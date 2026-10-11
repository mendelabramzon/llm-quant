#!/usr/bin/env python3
"""The one-pool queue book, run live and read-only: today's bid ladder, unsigned CoW orders, and a daily forward test.

Why. research/2026-10-10/queue_book proposes `lst-queue-book-one-pool`: one WETH balance behind standing below-NAV
bids for stETH, wstETH, weETH and rsETH (LBTC against cbBTC later), posted as unescrowed CoW Protocol limit orders and
re-signed daily; a fill is redeemed through the protocol's own queue (Lido WithdrawalQueueERC721, ether.fi
WithdrawRequestNFT, Kelp LRTWithdrawalManager). The backtest says $409,889 a year out of sample at $15M, and
research/2026-10-10/cow_fill_check found resting CoW orders filling at their limits in the April 2026 episode. The next
step is to run it small, ETH only, and that needs what the studies do not give: the day's limit prices, order payloads
a human can check and sign, and the row's kill criteria recomputed every day on data that did not exist when the rule
was frozen. This script is that bridge. It never signs, never sends a transaction and never posts an order.

How.
- `quote`: NAV per token at the latest block (the `dislocation_history.STATE` call specs; stETH redeems 1:1), each
  queue's wait now (`wait_estimate`: the median, over requests created in the trailing 14 days, of the request points
  the study's wait models build, a pending request entering at its age so far), carry = staking APR x wait (as
  `queue_book.simulate_book` charges it; the APR is wstETH's NAV growth over 30 days), the redemption fee, and the
  hurdle frozen from the all4 book at $15M (1bp). Limit discount = hurdle + carry + fee; limit price = NAV x (1 -
  limit discount). Pool fees are not in the limit: a solver pays them sourcing the token, which is why a seller's
  print has to clear the limit by two of them (the simulation's `FEE_LEGS`). -> research/queue_live/quotes/DATE.json
- `orders`: one GPv2 order per token (sell WETH for the token, kind sell, partially fillable, valid 26 hours, the whole
  pool on every order: the orders are unescrowed and settlement cannot fill past the balance) and the EIP-712 digest
  it would be signed over. The digest code is pinned to a real filled order from CoW's API in the tests.
  -> research/queue_live/orders/DATE.json
- `monitor`: collects from where the studies' raw logs end (block 26,157,137, 2026-10-09T20:06Z; the ether.fi event
  streams end at 26,161,639) to the finalized head with the studies' own machinery (`collect_stream`,
  `surface_streams`, the STATE specs, `surface_swaps`, the wait models) into research/queue_live/swaps/, then turns the
  kill criteria into numbers: (1) the trailing-90-day `simulate_book` value of the one-pool book at $15M and the frozen
  hurdle; (2) the payout checks on the new claims (reported beside the verdict, which covers 1, 3 and 4); (3) the
  trailing-year correlation of LBTC's and the ETH tokens' daily locked capital; (4) read two ways: literally, hours in
  which the venue-median discount less one pool fee cleared the limit while no CoW order bought the token at or beyond
  it (until the book's orders rest that flags tokens nobody bids on CoW, so each flag carries the token's CoW flow), and
  on observed resting orders, CoW orders that sat through such an hour against their own limit and filled only later
  (the status rests on these). Then the paper ledger: register today's ladder and score it.
- A token whose queue reads paused (or Lido in bunker mode) at the quote gets no order and no paper bid that day.
- `implementations` (2026-10-11): how the book's value depends on how it is executed, on queue_book's window and split
  at $15M: the taker the backtest assumed, (a) a taker checked hourly, (b) one fixed resting limit, (c) a daily limit
  re-quoted from the market, (d) a two-level ladder, (e) an hourly re-quote. -> research/queue_live/implementation.json
  and tables.md. A resting order earns its limit, not the market; (c) keeps about half the backtest's value and is
  rule v2 (`FROZEN_RULE_V2`), registered from the first daily run dated 2026-10-12 (v1 rows stay as registered and
  each version is scored as its own paper pool). The persistence test that followed ((f) and (g): each qualifying
  sell bought back an hour or a day later at the later price) found the discounts persist for stETH and weETH, so a
  taker buying back at the next hour boundary keeps 72-86% of the backtest, and the daily re-quote falls below its
  interval: rule v3 (`FROZEN_RULE_V3`, an hourly keeper, scored by `score_taker` from data before each hour) registers
  beside v2 from the same day, and is the implementation the book row should carry.
- `score`: the paper ledger research/queue_live_paper.jsonl (append-only; a registered row is never edited) is filled
  only by sells that happened after a ladder's registration (block timestamps read exactly) whose capturable discount
  (`simulate_book`'s: the print less two pool fees, capped at the venue median less one) is at or beyond the
  registered limit, from one pool, capital locked for the measured wait. P&L two ways: at the registered limit (what a
  signed order guarantees; resting CoW orders filled at their limits in April 2026) and at the capturable discount
  (the backtest's convention). -> research/queue_live_paper.json with the verdict.

    uv run --with pycryptodome python scripts/queue_live.py quote   [--pool-eth 100]
    uv run --with pycryptodome python scripts/queue_live.py orders  [--owner 0x...]
    uv run --with pycryptodome python scripts/queue_live.py monitor
    uv run --with pycryptodome python scripts/queue_live.py score
    uv run --with pycryptodome python scripts/queue_live.py daily   [--owner 0x...]    # quote, orders, monitor
    uv run --with pycryptodome python scripts/queue_live.py implementations           # the implementation comparison

Read-only: eth_getLogs, eth_getBlockByNumber and eth_call through the local Infura keys (live_rpc; the public archive
endpoints in drpc when Infura refuses a state read), daily prices from DefiLlama, order details from CoW's public API.
Keys are never written.
"""
import argparse
import bisect
import collections
import datetime as dt
import gzip
import hashlib
import heapq
import json
import math
import re
import statistics
import sys
import time
import urllib.request
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B                      # noqa: E402
import cow_fill_check as C                # noqa: E402
import dislocation_history as D           # noqa: E402
import drpc                               # noqa: E402
import live_rpc                           # noqa: E402
import queue_book as Q                    # noqa: E402
from live_rpc import RPCError, hx, word   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'queue_live'
SWAPS = OUT / 'swaps'
LEDGER = ROOT / 'research' / 'queue_live_paper.jsonl'
LONG = ROOT / 'research' / '2026-10-09' / 'redemption_history' / 'raw' / 'long'      # stETH, rsETH raw logs and state
QBX = ROOT / 'research' / '2026-10-10' / 'queue_bids_ext'                              # ether.fi event streams
EF_LONG = QBX / 'raw' / 'etherfi_long'                                               # weETH priced swaps, Rebase steps
NEW_ASSETS = QBX / 'raw' / 'new_assets'                                              # LBTC priced swaps, lbtc_nav
QUEUE_BOOK = ROOT / 'research' / '2026-10-10' / 'queue_book' / 'analysis.json'

# The rule the forward test runs, frozen on 2026-10-11 from the book row `lst-queue-book-one-pool`. Nothing here is
# re-chosen on data that arrives later: NAVs, waits and the staking APR are measured each day by the methods named
# here, the rest is fixed.
FROZEN_RULE = {
    'id': 'lst-queue-book-one-pool', 'version': 1, 'frozen': '2026-10-11',
    'hurdle_bps': 1.0,
    'hurdle_source': 'research/2026-10-10/queue_book/analysis.json joint.all4.15000000.chosen_hurdle (h=1)',
    'tokens': ['stETH', 'wstETH', 'weETH', 'rsETH'],
    'limit': 'limit discount = hurdle + carry + redemption fee; limit price = NAV x (1 - limit discount / 1e4)',
    'carry': 'staking APR x wait / 365, the APR being wstETH stEthPerToken growth over the trailing 30 days',
    'wait': ('median, over requests created in the trailing 14 days (60 when fewer than 5), of the study wait model\'s '
             'request points as known now: the measured wait if finalized, the age so far if pending'),
    'nav': 'stETH 1; wstETH stEthPerToken(); weETH getRate(); rsETH LRTOracle.rsETHPrice(); read at the latest block',
    'order': {'sell_token': 'WETH', 'kind': 'sell', 'partially_fillable': True, 'valid_hours': 26,
              'size': 'the whole pool on every order (unescrowed)'},
    'path_check': ('a token whose queue reads paused (or Lido in bunker mode) at the quote gets no order and no paper bid '
                   'that day: Lido isBunkerModeActive()/isPaused(), ether.fi WithdrawRequestNFT and LiquidityPool paused(), '
                   'Kelp LRTWithdrawalManager paused()'),
    'simulation': {'fee_legs': D.FEE_LEGS, 'gas_per_fill_usd': D.GAS_PER_FILL_USD, 'min_fill_usd': D.MIN_FILL_USD,
                   'market_cap': 'venue median less one pool fee (market_discount_fn, 6h lookback)'},
    'criteria': {'c1': 'trailing 90-day simulate_book value of the all4 pool at $15M and the frozen hurdle >= $40,000 a year',
                 'c3': 'trailing 365-day correlation of LBTC and ETH-three daily locked capital (unbounded capital, frozen hurdle) <= 0.5',
                 'c4': 'no hour with the venue-median discount less one pool fee at or beyond the limit and no CoW buy of the token at or beyond it'},
}
# v2 (frozen 2026-10-11, registers from the first daily run dated 2026-10-12): the implementation comparison
# (research/queue_live/implementation.json) found that a resting limit at hurdle + carry earns about the hurdle, and that
# a limit re-quoted daily from the market keeps about half the backtest's value with t near 8, within noise of an hourly
# re-quote and without its 24 signatures a day. Everything else is v1's.
V2_FROM = '2026-10-12'
REQUOTE_INSIDE_BPS = 1.0
FROZEN_RULE_V2 = dict(FROZEN_RULE, version=2, frozen='2026-10-11', registers_from=V2_FROM,
                      implementation='daily re-quoted limit from the market (implementation c)',
                      limit=('limit discount = max(hurdle + carry + redemption fee, median of the 24 whole-hour venue medians '
                             '(market_discount_fn) before the hour of the data end, less the median venue fee of the last 30 '
                             'days, less 1bp); limit price = NAV x (1 - limit discount / 1e4)'),
                      evidence='research/queue_live/implementation.json')
# v3 (frozen 2026-10-11, registers from the first daily run dated 2026-10-12, beside v2): the persistence test found
# that liquid staking discounts are still there an hour later (98% of qualifying stETH/wstETH sells, 91% of weETH), so a
# taker that buys the previous hour's qualifying sells back at the next hour boundary keeps 72-86% of the backtest
# against the daily re-quote's 50%, and the daily re-quote falls below its 95% interval. It is not a pre-signed order: a
# keeper acts each hour. The paper test simulates its hourly decisions from data before each hour.
V3_FROM = '2026-10-12'
FROZEN_RULE_V3 = dict(FROZEN_RULE, version=3, frozen='2026-10-11', registers_from=V3_FROM,
                      implementation='hourly taker buying back the qualifying sells at the next hour boundary (implementation f)',
                      decision=('at each hour boundary H, from data before H: every sell of a bid token in [H-1h, H), after the '
                                'ladder\'s registration, whose own-hour edge (print less two pool fees, capped at its hour\'s '
                                'venue median less one fee, less the registered carry and redemption fee) exceeds the hurdle'),
                      execution=('bought at H for its volume less the capital locked, if the venue median over [H, H+1h) '
                                 '(trades in it only; skipped when none) still leaves an edge above the hurdle'),
                      pnl=('at the later venue median (the rule), at the first trade after H (the closer reading), and at '
                           'the hurdle (the worst price its order accepts: hurdle + carry below NAV)'),
                      live=('a keeper submits one CoW order per token at each hour boundary for the previous hour\'s '
                            'qualifying volume, limit at hurdle + carry below NAV; there is no pre-signed daily order'),
                      evidence='research/queue_live/implementation.json (f_taker_next_hour, persistence)')
HURDLE = FROZEN_RULE['hurdle_bps']
VALID_HOURS = FROZEN_RULE['order']['valid_hours']
C1_POOL_USD, C1_DAYS, C1_MIN_USD = 15_000_000, 90, 40_000.0
C3_DAYS, C3_MAX = 365, 0.5
WAIT_DAYS, WAIT_DAYS_FALLBACK, WAIT_MIN_POINTS = 14, 60, 5
APR_DAYS = 30
WINDOW_DAYS = 366                    # the simulation loads a trailing year (+1 day) so criterion 3 has its full window
HEADER_STEP = 300                    # an hourly header grid in the new window: timestamps to the minute
COW_STEP = 2_000
DEFAULT_POOL_ETH = 100.0             # "live and small": the default order size; the paper ledger runs at it

ETH3 = ['lido', 'etherfi_ev', 'kelp']
ALL4 = ETH3 + ['lbtc_cb']
SWAP_STREAM_KEYS = ['lido', 'etherfi', 'kelp', 'lbtc_cb']   # surface_streams keys (etherfi_ev borrows etherfi's pools)
EF_STREAMS = ['ef_wrnft', 'ef_admin', 'ef_lp', 'ef_upgrades']
TOKENS = {'stETH': {'address': D.STETH, 'asset': 'lido', 'nav': None},
          'wstETH': {'address': D.WSTETH, 'asset': 'lido', 'nav': 'wsteth_nav'},
          'weETH': {'address': D.WEETH, 'asset': 'etherfi_ev', 'nav': 'weeth_nav'},
          'rsETH': {'address': D.RSETH, 'asset': 'kelp', 'nav': 'rseth_nav'}}
TOKEN_BY_ADDR = {v['address']: k for k, v in TOKENS.items()}
NAV_KEY_PRICED = {'stETH': None, 'wstETH': 'wsteth_nav', 'weETH': 'weeth_nav_step', 'rsETH': 'rseth_nav'}
STATE_KEYS = ['wsteth_nav', 'weeth_nav', 'rseth_nav', 'kelp_next_locked', 'kelp_next_unused', 'lbtc_nav']
PATH_CHECKS = {'lido': [('bunker_mode', D.LIDO_WQ, 'isBunkerModeActive()'), ('paused', D.LIDO_WQ, 'isPaused()')],
               'etherfi_ev': [('withdraw_request_nft_paused', D.ETHERFI_WRNFT, 'paused()'),
                              ('liquidity_pool_paused', D.ETHERFI_LP, 'paused()')],
               'kelp': [('withdrawal_manager_paused', D.KELP_WM, 'paused()')]}

# CoW Protocol, GPv2 (GPv2Order.sol, GPv2Settlement domain).
SETTLEMENT_CHECKSUM = '0x9008D19f58AAbD9eD0D60971565AA8510560ab41'
VAULT_RELAYER = '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110'   # the address the WETH allowance must be granted to
ORDER_TYPE = ('Order(address sellToken,address buyToken,address receiver,uint256 sellAmount,uint256 buyAmount,'
              'uint32 validTo,bytes32 appData,uint256 feeAmount,string kind,bool partiallyFillable,'
              'string sellTokenBalance,string buyTokenBalance)')
ORDER_FIELDS = [('sellToken', 'address'), ('buyToken', 'address'), ('receiver', 'address'), ('sellAmount', 'uint256'),
                ('buyAmount', 'uint256'), ('validTo', 'uint32'), ('appData', 'bytes32'), ('feeAmount', 'uint256'),
                ('kind', 'string'), ('partiallyFillable', 'bool'), ('sellTokenBalance', 'string'),
                ('buyTokenBalance', 'string')]
DOMAIN = {'name': 'Gnosis Protocol', 'version': 'v2', 'chainId': 1, 'verifyingContract': SETTLEMENT_CHECKSUM}
# The app-data document every order carries. CoW hashes the exact UTF-8 bytes; whoever submits an order must upload
# this string with it (fullAppData) or PUT it to /api/v1/app_data/<hash> first.
APP_DATA_JSON = '{"appCode":"llm-quant queue book","metadata":{},"version":"1.3.0"}'
# Placeholder owner: the zero address, with receiver zero too, which GPv2 reads as "pay the owner", so a payload signed
# by mistake still pays whoever signed it. Its uid is not any real order's uid.
PLACEHOLDER_OWNER = '0x' + '0' * 40


def keccak_bytes(b):
    if D._keccak is not None:
        return D._keccak.new(digest_bits=256, data=bytes(b)).digest()
    return bytes.fromhex(D._keccak256_pure(bytes(b)))


APP_DATA = '0x' + keccak_bytes(APP_DATA_JSON.encode()).hex()


def utc(ts=None):
    return D.utc(int(ts) if ts is not None else None)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------- EIP-712, GPv2
def _abi_word(typ, v):
    if typ == 'address':
        return bytes.fromhex((v or PLACEHOLDER_OWNER)[2:].lower()).rjust(32, b'\0')
    if typ in ('uint256', 'uint32'):
        return int(v).to_bytes(32, 'big')
    if typ == 'bytes32':
        b = bytes.fromhex(v[2:])
        if len(b) != 32:
            raise ValueError('bytes32 field is %d bytes' % len(b))
        return b
    if typ == 'bool':
        return (1 if v else 0).to_bytes(32, 'big')
    if typ == 'string':
        return keccak_bytes(v.encode())
    raise ValueError(typ)


def domain_separator(name=DOMAIN['name'], version=DOMAIN['version'], chain_id=DOMAIN['chainId'],
                     verifying_contract=DOMAIN['verifyingContract']):
    return keccak_bytes(keccak_bytes(b'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)')
                        + keccak_bytes(name.encode()) + keccak_bytes(version.encode()) + int(chain_id).to_bytes(32, 'big')
                        + _abi_word('address', verifying_contract))


def order_struct_hash(o):
    """hashStruct(Order): GPv2Order.hash's struct part; `o` uses the API's field names (amounts as decimal strings)."""
    return keccak_bytes(keccak_bytes(ORDER_TYPE.encode()) + b''.join(_abi_word(t, o[n]) for n, t in ORDER_FIELDS))


def order_digest(o, domain=None):
    """The EIP-712 digest an owner signs: keccak256(0x1901 || domainSeparator || hashStruct(order))."""
    return keccak_bytes(b'\x19\x01' + (domain or domain_separator()) + order_struct_hash(o))


def order_uid(digest, owner, valid_to):
    """GPv2's 56-byte order uid: the digest, the owner, validTo as uint32."""
    return '0x' + digest.hex() + owner[2:].lower() + int(valid_to).to_bytes(4, 'big').hex()


def api_order_fields(api):
    """An order as CoW's API serves it -> the twelve signed fields (receiver null means the owner; old orders may carry
    the app-data document itself where newer ones carry its hash)."""
    app = api.get('appData') or ('0x' + '0' * 64)
    if not (isinstance(app, str) and re.fullmatch(r'0x[0-9a-fA-F]{64}', app)):
        app = '0x' + keccak_bytes(str(app).encode()).hex()
    o = {n: api.get(n) for n, _ in ORDER_FIELDS}
    o.update({'receiver': api.get('receiver') or PLACEHOLDER_OWNER, 'appData': app,
              'feeAmount': api.get('feeAmount') or '0', 'sellTokenBalance': api.get('sellTokenBalance') or 'erc20',
              'buyTokenBalance': api.get('buyTokenBalance') or 'erc20'})
    return o


def typed_data(o):
    """eth_signTypedData_v4 payload for one order (what a wallet shows and signs)."""
    return {'types': {'EIP712Domain': [{'name': 'name', 'type': 'string'}, {'name': 'version', 'type': 'string'},
                                       {'name': 'chainId', 'type': 'uint256'}, {'name': 'verifyingContract', 'type': 'address'}],
                      'Order': [{'name': n, 'type': t} for n, t in ORDER_FIELDS]},
            'primaryType': 'Order', 'domain': dict(DOMAIN), 'message': {n: o[n] for n, _ in ORDER_FIELDS}}


# --------------------------------------------------------------------------------------------- ladder arithmetic
def staking_apr(samples, as_of, days=APR_DAYS):
    """Annualised growth of wstETH's stEthPerToken over the `days` before `as_of`; samples [(ts, value)]."""
    xs = [(t, v) for t, v in samples if as_of - days * 86400 <= t <= as_of]
    return D.apr_from_nav(xs, days_min=days / 2.0)


def wait_estimate(points, as_of, days=WAIT_DAYS, fallback_days=WAIT_DAYS_FALLBACK, min_points=WAIT_MIN_POINTS):
    """The frozen wait rule. `points` are the wait model's request points [(created ts, wait days or None, lower
    bound)] (`lido_waits`, `pointer_waits`, ether.fi's request records). Each request created in the `days` before
    `as_of` enters as it was known at `as_of`: its measured wait if finalized by then, its age so far if not. The
    median of those is `simulate_book`'s day medians pooled over a fortnight; a stalling queue raises it as its pending
    requests age. Fewer than `min_points` requests widen the window to `fallback_days`. Returns (days, n, window)."""
    for window in (days, fallback_days):
        vals = []
        for ts, w, _ in points:
            if as_of - window * 86400 <= ts <= as_of:
                vals.append(w if (w is not None and ts + w * 86400 <= as_of) else (as_of - ts) / 86400.0)
        if len(vals) >= min_points or window == fallback_days:
            return (statistics.median(vals) if vals else None), len(vals), window
    return None, 0, fallback_days


def ladder_entry(nav_eth, wait_days, apr, hurdle_bps=HURDLE, redemption_fee_bps=0.0):
    """Every component of one rung: carry = APR x wait (bp), limit = hurdle + carry + redemption fee below NAV."""
    carry = apr * wait_days / 365.0 * 1e4
    limit = hurdle_bps + carry + redemption_fee_bps
    return {'nav_eth': nav_eth, 'wait_days': wait_days, 'staking_apr': apr, 'carry_bps': carry,
            'redemption_fee_bps': redemption_fee_bps, 'hurdle_bps': hurdle_bps, 'limit_discount_bps': limit,
            'limit_price_eth_per_token': nav_eth * (1.0 - limit / 1e4)}


def limit_price_wei(nav_wei, limit_bps):
    """Wei of ETH per 1e18 token units at the limit. The discount is rounded up to 1e-4 bp and the price down, so the
    order never pays above the exact limit (rounding the discount to nearest could, by up to 5e-9)."""
    units = math.ceil(limit_bps * 1e4 - 1e-6)
    return nav_wei * (10 ** 8 - units) // 10 ** 8


def buy_amount_for(sell_wei, limit_wei):
    """The smallest buyAmount whose price sell/buy is at or under the limit: ceil(sell x 1e18 / limit)."""
    return -(-sell_wei * 10 ** 18 // limit_wei)


# ---------------------------------------------------------------------------------------------- ledger primitives
def read_ledger(path=LEDGER):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def ledger_row(q, now_s, quote_path=None, version=None):
    """A registration: the ladder as quoted, valid from now for the orders' 26 hours. Never edited after it is written.
    A v3 (taker) row keeps v1's limit as its worst acceptable price."""
    version = version or q.get('rule_version', 1)
    lad = {}
    for sym, e in q['tokens'].items():
        x = {k: e[k] for k in ('asset', 'nav_eth', 'wait_days', 'carry_bps', 'hurdle_bps', 'redemption_fee_bps',
                               'limit_discount_bps', 'limit_price_eth_per_token')}
        x['path_open'] = e.get('path_open', True)
        if version == 3 and e.get('v1_limit_discount_bps') is not None:
            x['limit_discount_bps'] = e['v1_limit_discount_bps']
            x['limit_price_eth_per_token'] = e['nav_eth'] * (1.0 - e['v1_limit_discount_bps'] / 1e4)
        lad[sym] = x
    return {'date': q['date'], 'registered_at': dt.datetime.fromtimestamp(now_s, dt.timezone.utc).isoformat(),
            'registered_ts': now_s, 'valid_to_ts': now_s + VALID_HOURS * 3600, 'rule': FROZEN_RULE['id'],
            'rule_version': version, 'rule_kind': 'taker' if version == 3 else 'resting',
            'pool_eth': q['pool_eth'], 'staking_apr': q['staking_apr']['value'],
            'quote_generated': q['generated'], 'data_through_block': q['data_through']['block'],
            'data_through_utc': q['data_through']['utc'],
            'quote_file': str(Path(quote_path).relative_to(ROOT)) if quote_path else None,
            'quote_sha256': sha256_file(quote_path) if quote_path else None, 'ladder': lad}


def register(q, now_s, ledger_path=LEDGER, quote_path=None):
    """Append today's rows, one per rule version the quote registers (`register_versions`; v2 and v3 from 2026-10-12),
    skipping a version already registered that date; refuse a quote from another UTC day (a stale ladder registered
    late would be scored on sells its author had already seen). Returns (first row written or None, message)."""
    rows = read_ledger(ledger_path)
    today = utc(now_s)[:10]
    versions = q.get('register_versions') or [q.get('rule_version', 1)]
    have = {(r['date'], r.get('rule_version', 1)): r for r in rows}
    todo = [v for v in versions if (q['date'], v) not in have]
    if not todo:
        r = have[(q['date'], versions[0])]
        return None, 'already registered at %s' % r['registered_at']
    if q['date'] != today:
        return None, 'quote dated %s is not today (%s): not registered' % (q['date'], today)
    if dt.datetime.fromisoformat(q['generated'].replace('Z', '+00:00')).timestamp() > now_s + 60:
        return None, 'quote generated after the registration time: not registered'
    Path(ledger_path).parent.mkdir(parents=True, exist_ok=True)
    written = [ledger_row(q, now_s, quote_path, version=v) for v in todo]
    with Path(ledger_path).open('a') as f:
        for row in written:
            f.write(json.dumps(row, sort_keys=True) + '\n')
    return written[0], 'registered' + ('' if versions == [1] else ' v%s' % ', v'.join(str(v) for v in todo))


def periods(rows):
    """[(start, end, row)]: a ladder governs from its registration (exclusive) until it expires or the next one is
    registered, whichever is first."""
    rows = sorted(rows, key=lambda r: r['registered_ts'])
    out = []
    for i, r in enumerate(rows):
        end = r['valid_to_ts']
        if i + 1 < len(rows):
            end = min(end, rows[i + 1]['registered_ts'])
        out.append((r['registered_ts'], end, r))
    return out


def governing(per, ts):
    """The ladder in force at `ts` (registered strictly before it, not expired, not superseded), or None."""
    starts = [a for a, _, _ in per]
    i = bisect.bisect_left(starts, ts) - 1        # last registration strictly before ts
    if i >= 0 and per[i][0] < ts <= per[i][1]:
        return per[i][2]
    return None


# --------------------------------------------------------------------------------------------- paper scoring
def capturable_bps(s, market_bps):
    """simulate_book's discount a patient bid can take from one sell: the print less two pool fees, capped at the venue
    median less one."""
    disc = s['discount_bps'] - D.FEE_LEGS * s['fee_bps']
    if market_bps is not None:
        disc = min(disc, market_bps - s['fee_bps'])
    return disc


def score_paper(rows, sells, market, measured_wait, eth_usd, now_ts, exact_ts=None, gas_usd=D.GAS_PER_FILL_USD,
                min_fill_usd=D.MIN_FILL_USD):
    """Fill the registered ladders from the sells, one pool, with simulate_book's rule.

    `rows`: ledger rows. `sells`: [{ts, block, li, token, asset, eth (notional at NAV), usd, discount_bps, fee_bps,
    tx, pool}] in chain order. `market[asset](ts)`: venue median or None. `measured_wait(asset, ts)` -> (days,
    resolved). `eth_usd(ts)`. `exact_ts(block)` -> the block's own timestamp (None: keep the interpolated one).

    A sell fills only if it happened after the governing ladder's registration and its capturable discount is at or
    beyond the registered limit (edge over the registered carry and fee >= hurdle), it clears gas, and the fill clears
    the minimum. The signed limit is a price, so against a NAV that has accrued since registration it sits deeper:
    with the sell's `nav`, the limit used is max(registered, 1 - limit price / NAV at the sell). The fill locks its ETH for the measured wait (unresolved: the larger of the lower bound and the
    registered estimate, marked provisional). Value at the limit = fill x (limit - measured carry - fee) - gas; value
    at the market = fill x (capturable - measured carry - fee) - gas."""
    per = periods(rows)
    min_limit = collections.defaultdict(lambda: float('inf'))
    for r in rows:
        for sym, e in r['ladder'].items():
            min_limit[sym] = min(min_limit[sym], e['limit_discount_bps'])
    heap, locked, peak = [], 0.0, 0.0
    fills, st = [], collections.Counter()
    first_reg = min((r['registered_ts'] for r in rows), default=None)
    for s in sells:
        m = market[s['asset']](s['ts']) if s['asset'] in market else None
        disc = capturable_bps(s, m)
        if disc < min_limit[s['token']] - 1e-9:
            continue
        ts = s['ts']
        if exact_ts is not None:
            t = exact_ts(s['block'])
            if t is not None:
                ts = t
        while heap and heap[0][0] <= ts:
            locked -= heapq.heappop(heap)[1]
        r = governing(per, ts)
        if r is None:
            st['before_first_ladder' if first_reg is None or ts <= first_reg else 'outside_any_ladder'] += 1
            continue
        e = r['ladder'].get(s['token'])
        if e is None or not e.get('path_open', True):
            st['token_not_bid'] += 1
            continue
        if exact_ts is not None:
            m = market[s['asset']](ts)
            disc = capturable_bps(s, m)
        lim = e['limit_discount_bps']
        if s.get('nav') and e.get('limit_price_eth_per_token'):
            lim = max(lim, (1.0 - e['limit_price_eth_per_token'] / s['nav']) * 1e4)
        if disc < lim - 1e-9:
            continue
        edge = disc - e['carry_bps'] - e['redemption_fee_bps']
        st['qualifying_sells'] += 1
        if s['usd'] * edge / 1e4 <= gas_usd:
            st['below_gas'] += 1
            continue
        px = eth_usd(ts)
        avail = max(0.0, r['pool_eth'] - locked)
        fill = min(s['eth'], avail)
        if fill < s['eth']:
            st['missed_capital_eth'] += s['eth'] - fill
        if fill * px < min_fill_usd or fill * px * edge / 1e4 - gas_usd <= 0:
            st['below_min_fill'] += 1
            continue
        wait, resolved = measured_wait(s['asset'], ts)
        if not resolved:
            wait = max(wait, e['wait_days'])
        carry = r['staking_apr'] * wait / 365.0 * 1e4
        gas_eth = gas_usd / px
        v_lim = fill * (lim - carry - e['redemption_fee_bps']) / 1e4 - gas_eth
        v_mkt = fill * (disc - carry - e['redemption_fee_bps']) / 1e4 - gas_eth
        heapq.heappush(heap, (ts + wait * 86400.0, fill))
        locked += fill
        peak = max(peak, locked)
        fills.append({'ts': ts, 'utc': utc(ts), 'block': s['block'], 'tx': s.get('tx'), 'pool': s.get('pool'),
                      'token': s['token'], 'ladder_date': r['date'], 'eth': fill, 'usd': fill * px,
                      'print_discount_bps': s['discount_bps'], 'capturable_bps': disc,
                      'limit_discount_bps': lim, 'registered_limit_bps': e['limit_discount_bps'],
                      'registered_carry_bps': e['carry_bps'],
                      'wait_days': wait, 'wait_resolved': resolved, 'carry_bps': carry,
                      'value_eth_at_limit': v_lim, 'value_usd_at_limit': v_lim * px,
                      'value_eth_at_market': v_mkt, 'value_usd_at_market': v_mkt * px,
                      'release_utc': utc(ts + wait * 86400.0)})
    open_ = [f for f in fills if f['ts'] + f['wait_days'] * 86400.0 > now_ts]
    by_token = collections.defaultdict(lambda: {'fills': 0, 'eth': 0.0, 'value_eth_at_limit': 0.0, 'value_eth_at_market': 0.0})
    for f in fills:
        b = by_token[f['token']]
        b['fills'] += 1
        b['eth'] += f['eth']
        b['value_eth_at_limit'] += f['value_eth_at_limit']
        b['value_eth_at_market'] += f['value_eth_at_market']
    summary = {'fills': len(fills), 'eth_filled': sum(f['eth'] for f in fills), 'usd_filled': sum(f['usd'] for f in fills),
               'value_eth_at_limit': sum(f['value_eth_at_limit'] for f in fills),
               'value_usd_at_limit': sum(f['value_usd_at_limit'] for f in fills),
               'value_eth_at_market': sum(f['value_eth_at_market'] for f in fills),
               'value_usd_at_market': sum(f['value_usd_at_market'] for f in fills),
               'locked_eth_now': sum(f['eth'] for f in open_), 'open_positions': len(open_), 'peak_locked_eth': peak,
               'provisional_fills': sum(1 for f in fills if not f['wait_resolved']), 'by_token': dict(by_token),
               'counts': dict(st)}
    return fills, summary


def score_taker(rows, sells, market, idx, measured_wait, eth_usd, now_ts, exact_ts=None, gas_usd=D.GAS_PER_FILL_USD,
                min_fill_usd=D.MIN_FILL_USD):
    """Paper rule v3: the hourly taker's decisions, each from data before its hour.

    At each hour boundary H, a sell of a bid token in [H-1h, H) that happened after the governing (v3) row's
    registration qualifies when its own-hour edge (capturable discount at its own hour's venue median, less the
    registered carry and fee) exceeds the hurdle; it is bought at H for its volume (less locked capital) when the venue
    median over [H, H+1h) (`window_median`) still leaves an edge above the hurdle. Capital is locked from H for the
    measured wait. P&L at the later venue median (the rule), at the first trade after H, and at the hurdle (the worst
    price the order accepts). `idx[asset]` is `trade_index` of the asset's priced trades."""
    per = periods(rows)
    first_reg = min((r['registered_ts'] for r in rows), default=None)
    events, st, cache = [], collections.Counter(), {}
    for s in sells:
        H = (int(s['ts'] // 3600) + 1) * 3600
        r = governing(per, H)
        if r is None:
            st['before_first_ladder' if first_reg is None or H <= first_reg else 'outside_any_ladder'] += 1
            continue
        e = r['ladder'].get(s['token'])
        if e is None or not e.get('path_open', True):
            st['token_not_bid'] += 1
            continue
        own = capturable_bps(s, market[s['asset']](s['ts'])) - e['carry_bps'] - e['redemption_fee_bps']
        if own <= e['hurdle_bps'] or s['usd'] * own / 1e4 <= gas_usd:
            continue
        ts = s['ts']
        if exact_ts is not None:
            t = exact_ts(s['block'])
            ts = t if t is not None else ts
        if ts <= r['registered_ts']:
            st['sell_before_registration'] += 1
            continue
        st['qualifying'] += 1
        key = (s['asset'], H)
        if key not in cache:
            cache[key] = (window_median(idx[s['asset']], H, H + 3600), window_first(idx[s['asset']], H, H + 3600))
        med, first = cache[key]
        if med is None:
            st['later_missing'] += 1
            continue
        base = s['discount_bps'] - D.FEE_LEGS * s['fee_bps']
        if min(base, med - s['fee_bps']) - e['carry_bps'] - e['redemption_fee_bps'] <= e['hurdle_bps']:
            st['later_below_hurdle'] += 1
            continue
        events.append((H, ts, s, r, e, base, med, first))
    events.sort(key=lambda x: (x[0], x[1]))
    heap, locked, peak, fills = [], 0.0, 0.0, []
    for H, ts, s, r, e, base, med, first in events:
        while heap and heap[0][0] <= H:
            locked -= heapq.heappop(heap)[1]
        px = eth_usd(H)
        fill = min(s['eth'], max(0.0, r['pool_eth'] - locked))
        if fill < s['eth']:
            st['missed_capital_eth'] += s['eth'] - fill
        edge_reg = min(base, med - s['fee_bps']) - e['carry_bps'] - e['redemption_fee_bps']
        if fill * px < min_fill_usd or fill * px * edge_reg / 1e4 - gas_usd <= 0:
            st['below_min_fill'] += 1
            continue
        wait, resolved = measured_wait(s['asset'], H)
        if not resolved:
            wait = max(wait, e['wait_days'])
        carry = r['staking_apr'] * wait / 365.0 * 1e4
        gas_eth = gas_usd / px
        disc_m = min(base, med - s['fee_bps'])
        disc_f = min(base, first - s['fee_bps']) if first is not None else None
        v_mkt = fill * (disc_m - carry - e['redemption_fee_bps']) / 1e4 - gas_eth
        v_first = fill * (disc_f - carry - e['redemption_fee_bps']) / 1e4 - gas_eth if disc_f is not None else None
        v_lim = fill * (e['hurdle_bps'] + e['carry_bps'] - carry) / 1e4 - gas_eth
        heapq.heappush(heap, (H + wait * 86400.0, fill))
        locked += fill
        peak = max(peak, locked)
        fills.append({'ts': H, 'utc': utc(H), 'sell_ts': ts, 'block': s['block'], 'tx': s.get('tx'), 'pool': s.get('pool'),
                      'token': s['token'], 'ladder_date': r['date'], 'eth': fill, 'usd': fill * px,
                      'print_discount_bps': s['discount_bps'], 'later_median_bps': med, 'first_trade_bps': first,
                      'capturable_bps': disc_m, 'wait_days': wait, 'wait_resolved': resolved, 'carry_bps': carry,
                      'value_eth_at_market': v_mkt, 'value_usd_at_market': v_mkt * px,
                      'value_eth_at_first_trade': v_first, 'value_eth_at_limit': v_lim, 'value_usd_at_limit': v_lim * px,
                      'release_utc': utc(H + wait * 86400.0)})
    open_ = [f for f in fills if f['ts'] + f['wait_days'] * 86400.0 > now_ts]
    summary = {'fills': len(fills), 'eth_filled': sum(f['eth'] for f in fills), 'usd_filled': sum(f['usd'] for f in fills),
               'value_eth_at_market': sum(f['value_eth_at_market'] for f in fills),
               'value_usd_at_market': sum(f['value_usd_at_market'] for f in fills),
               'value_eth_at_first_trade': sum(f['value_eth_at_first_trade'] or 0.0 for f in fills),
               'value_eth_at_limit': sum(f['value_eth_at_limit'] for f in fills),
               'value_usd_at_limit': sum(f['value_usd_at_limit'] for f in fills),
               'locked_eth_now': sum(f['eth'] for f in open_), 'open_positions': len(open_), 'peak_locked_eth': peak,
               'provisional_fills': sum(1 for f in fills if not f['wait_resolved']), 'counts': dict(st)}
    return fills, summary


# ------------------------------------------------------------------------------------------------- data: bases
def base_ends():
    """The studies' last blocks: every surface directory ends at the same block; the ether.fi streams a little later."""
    ends = {p: D.read_json(p / 'manifest.json')['last_block'] for p in (LONG, EF_LONG, NEW_ASSETS)}
    if len(set(ends.values())) != 1:
        raise SystemExit('the study directories end at different blocks: %s' % ends)
    return ends[LONG], D.read_json(QBX / 'etherfi_manifest.json')['last_block']


def swap_metas():
    """Pool metadata for the book's assets, as the studies read it on chain (pools.json): coins, decimals, fees."""
    lp, npool = D.read_json(LONG / 'pools.json'), D.read_json(NEW_ASSETS / 'pools.json')
    flt = D.SURFACE['lbtc_cb']['pool_filter']
    return {'lido': lp['lido'], 'etherfi': lp['etherfi'], 'kelp': lp['kelp'],
            'lbtc_cb': [m for m in npool['lbtc'] if m['name'] in flt]}


def metas_for(k, metas):
    return metas.get(k) or metas.get(D.SURFACE[k].get('pools_of')) or []


# ---------------------------------------------------------------------------------------------- data: collection
class Log:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, obj):
        line = json.dumps(obj, default=str)
        print(line, flush=True)
        with self.path.open('a') as f:
            f.write(line + '\n')


def collect_headers(rpc, first, last):
    h = D.read_json(SWAPS / 'headers.json', {}) or {}
    grid = list(range(first, last, HEADER_STEP)) + [last]
    todo = [n for n in grid if str(n) not in h]
    for i in range(0, len(todo), 10):
        chunk = todo[i:i + 10]
        res = rpc.batch([('eth_getBlockByNumber', [hex(n), False]) for n in chunk])
        for n, b in zip(chunk, res):
            if not b or hx(b['number']) != n:
                raise RPCError('header %d missing' % n)
            h[str(n)] = {'ts': hx(b['timestamp']), 'hash': b['hash']}
    D.write_json(SWAPS / 'headers.json', h)
    return h, len(todo)


def _state_value(key, r):
    spec = D.STATE[key]
    v = int(r[:66], 16) / spec['scale']
    if spec.get('invert'):
        v = 1.0 / v if v else None
    return v


def collect_state(rpc, headers, log):
    """Every STATE key the book needs at every new header block: Infura first (it serves recent history), the public
    archive endpoints for any read it refuses."""
    st = D.read_json(SWAPS / 'state.json', None) or {'samples': {}, 'errors': []}
    for k in STATE_KEYS:
        st['samples'].setdefault(k, [])
    have = {k: {s['block'] for s in st['samples'][k]} for k in STATE_KEYS}
    tasks = [(int(n), k) for n in sorted(headers, key=int) for k in STATE_KEYS if int(n) not in have[k]]
    fallbacks = 0
    for i in range(0, len(tasks), 6):
        chunk = tasks[i:i + 6]
        res = rpc.batch([('eth_call', [{'to': D.STATE[k]['to'], 'data': D.STATE[k]['data']}, hex(n)]) for n, k in chunk],
                        allow_errors=True)
        for (n, k), r in zip(chunk, res):
            ep = 'infura'
            if isinstance(r, dict) or r in (None, '0x'):
                errs = []
                r, ep = D.archive_call(D.STATE[k]['to'], D.STATE[k]['data'], n, list(drpc.ENDPOINTS), errs)
                fallbacks += 1
                if not r:
                    st['errors'].extend([dict(e, key=k) for e in errs[-2:]])
                    continue
            st['samples'][k].append({'block': n, 'ts': headers[str(n)]['ts'], 'value': _state_value(k, r), 'endpoint': ep})
    for v in st['samples'].values():
        v.sort(key=lambda s: s['block'])
    st['method'] = 'eth_call of each STATE key at every header of the new window (hourly grid); Infura, drpc fallback'
    D.write_json(SWAPS / 'state.json', st)
    return {'reads': len(tasks), 'archive_fallbacks': fallbacks, 'errors': len(st['errors'])}


def collect_etherfi_finality(rpc):
    """lastFinalizedRequestId() at every new EtherFiAdmin execution block (finalization happens only inside them)."""
    blocks = sorted({hx(l['blockNumber']) for l in D.load_stream(SWAPS, 'ef_admin')})
    fin = D.read_json(SWAPS / 'etherfi_finality.json', None) or {'samples': {'last_finalized': []}, 'errors': []}
    have = {x['block'] for x in fin['samples']['last_finalized']}
    todo = [n for n in blocks if n not in have]
    data = D.sel('lastFinalizedRequestId()')
    for i in range(0, len(todo), 4):
        chunk = todo[i:i + 4]
        res = rpc.batch([('eth_call', [{'to': D.ETHERFI_WRNFT, 'data': data}, hex(n)]) for n in chunk], allow_errors=True)
        for n, r in zip(chunk, res):
            ep = 'infura'
            if isinstance(r, dict) or r in (None, '0x'):
                errs = []
                r, ep = D.archive_call(D.ETHERFI_WRNFT, data, n, list(drpc.ENDPOINTS), errs)
                if not r:
                    fin['errors'].extend(errs[-2:])
                    continue
            fin['samples']['last_finalized'].append({'block': n, 'value': int(r[:66], 16), 'endpoint': ep})
    fin['samples']['last_finalized'].sort(key=lambda x: x['block'])
    fin['method'] = 'lastFinalizedRequestId() on WithdrawRequestNFT at every EtherFiAdmin AdminOperationsExecuted block of the new window'
    D.write_json(SWAPS / 'etherfi_finality.json', fin)
    return {'admin_blocks': len(blocks), 'read': len(todo)}


def collect_cow(rpc, first, last, log):
    """GPv2Settlement Trade events, keeping the trades with a liquid staking token on either side (as cow_fill_check)."""
    d = SWAPS / 'cow'
    d.mkdir(parents=True, exist_ok=True)
    done = D.load_done(d)
    pending = collections.deque()
    for a, b in D.gaps(done, first, last):
        for s in range(a, b + 1, COW_STEP):
            pending.append((s, min(s + COW_STEP - 1, b)))
    n, trades, lst = 0, 0, 0
    while pending:
        a, b = pending.popleft()
        r = rpc.call('eth_getLogs', [{'address': C.SETTLEMENT, 'topics': [C.TRADE_TOPIC], 'fromBlock': hex(a), 'toBlock': hex(b)}],
                     allow_errors=True)
        if isinstance(r, dict) and 'error' in r:
            if a < b:
                mid = (a + b) // 2
                pending.appendleft((mid + 1, b))
                pending.appendleft((a, mid))
                continue
            raise RPCError('cow logs %d: %s' % (a, rpc.clean(json.dumps(r['error']))))
        keep = [t for t in (C.decode_trade(l) for l in (r or [])) if t['buy_token'] in C.LSTS or t['sell_token'] in C.LSTS]
        with gzip.open(d / ('%d_%d.json.gz' % (a, b)), 'wt') as f:
            json.dump({'trades_in_range': len(r or []), 'lst_trades': keep}, f)
        done.append([a, b])
        D.write_json(d / 'done.json', done)
        n, trades, lst = n + 1, trades + len(r or []), lst + len(keep)
    return {'ranges_fetched': n, 'trades_in_new_ranges': trades, 'lst_trades_in_new_ranges': lst}


def load_cow_trades():
    rows, total = [], 0
    d = SWAPS / 'cow'
    for p in sorted(d.glob('*_*.json.gz'), key=lambda p: int(p.name.split('_')[0])):
        with gzip.open(p, 'rt') as f:
            x = json.load(f)
        total += x['trades_in_range']
        rows += x['lst_trades']
    return rows, total


def collect_cow_orders(trades, log):
    """Order details (limit, creation time) for every new LST buy with ETH, from CoW's public API; errors are retried
    on the next run, not cached."""
    p = SWAPS / 'cow' / 'orders.json.gz'
    cache = json.load(gzip.open(p, 'rt')) if p.exists() else {}
    todo = sorted({t['uid'] for t in trades if t['buy_token'] in TOKEN_BY_ADDR and t['sell_token'] in (C.WETH, C.ETH)} - set(cache))
    errors = 0
    for uid in todo:
        req = urllib.request.Request(C.COW_API + uid, headers={'User-Agent': 'llm-quant research', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                cache[uid] = json.loads(r.read())
        except Exception as e:                      # a gap, retried next run
            errors += 1
            log({'cow_order_error': uid[:18], 'error': str(e)[:120]})
        time.sleep(0.25)
    with gzip.open(p, 'wt') as f:
        json.dump(cache, f)
    return cache, {'looked_up': len(todo), 'errors': errors, 'cached': len(cache)}


def collect_prices(first_ts, last_ts, log):
    out = {}
    for coin, fname in (('coingecko:ethereum', 'eth_usd.json'), ('coingecko:bitcoin', 'btc_usd.json')):
        try:
            prices, urls = D.llama_daily(coin, first_ts, last_ts)
            D.write_json(SWAPS / fname, {'source': urls, 'fetched': utc(), 'prices': prices})
            out[fname] = len(prices)
        except Exception as e:                      # keep the previous file; build_world says if it is stale
            log({'prices_error': fname, 'error': str(e)[:160]})
            out[fname] = 'error'
    return out


def collect(rpc, log, head_tag='finalized'):
    """Everything the quote and the monitor read, from the studies' last block to the finalized head. Incremental: the
    stream directories keep a done.json, so a run fetches only what is new."""
    SWAPS.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    base_last, ef_last = base_ends()
    head = rpc.call('eth_getBlockByNumber', [head_tag, False])
    last, last_ts = hx(head['number']), hx(head['timestamp'])
    man = D.read_json(SWAPS / 'manifest.json', {}) or {}
    if man.get('last_block') and last < man['last_block']:
        last = man['last_block']                    # never move backwards (a lagging endpoint)
    metas = swap_metas()
    D.write_json(SWAPS / 'pools.json', metas)
    streams = D.surface_streams(SWAP_STREAM_KEYS, metas)
    efs = [s for s in D.ETHERFI_STREAMS if s['name'] in EF_STREAMS]
    ranges = {s['name']: (base_last + 1, last) for s in streams}
    ranges.update({s['name']: (ef_last + 1, last) for s in efs})
    man.update({'chain': 'ethereum', 'chain_id': 1, 'first_block': base_last + 1, 'ef_first_block': ef_last + 1,
                'last_block': last, 'end_tag': head_tag, 'collect_started': utc()})
    man.setdefault('streams', {})
    for s in streams + efs:
        a, b = ranges[s['name']]
        res = D.collect_stream(rpc, SWAPS, s, a, b, 4, log)
        man['streams'][s['name']] = {'address': s['address'], 'topics': s['topics'], 'first_block': a, 'last_block': b, **res}
    headers, new_h = collect_headers(rpc, base_last + 1, last)
    man['last_block_utc'] = utc(headers[str(last)]['ts'])
    man['state'] = collect_state(rpc, headers, log)
    man['etherfi_finality'] = collect_etherfi_finality(rpc)
    man['cow'] = collect_cow(rpc, base_last + 1, last, log)
    trades, _ = load_cow_trades()
    _, man['cow_orders'] = collect_cow_orders(trades, log)
    first_ts = headers[str(base_last + 1)]['ts'] if str(base_last + 1) in headers else last_ts
    man['prices'] = collect_prices(first_ts - 2 * 86400, headers[str(last)]['ts'], log)
    man['complete'] = {s['name']: not D.gaps(D.load_done(SWAPS / 'raw' / s['name']), *ranges[s['name']]) for s in streams + efs}
    man['complete']['cow'] = not D.gaps(D.load_done(SWAPS / 'cow'), base_last + 1, last)
    man['raw_files'] = {s['name']: {p.name: D.sha256(p) for p in sorted((SWAPS / 'raw' / s['name']).glob('*.json.gz'))}
                        for s in streams + efs}
    man['headers'] = {'count': len(headers), 'step_blocks': HEADER_STEP, 'new_this_run': new_h}
    man['rpc'] = rpc.stats()
    man['collect_finished'] = utc()
    man['collect_seconds'] = round(time.monotonic() - t0, 1)
    D.write_json(SWAPS / 'manifest.json', man)
    log({'collected_to': last, 'utc': man['last_block_utc'], 'complete': man['complete'], 'seconds': man['collect_seconds'],
         **man['rpc']})
    return man


# ------------------------------------------------------------------------------------------- data: the world
def merged_prices(base_path, new_path):
    """The study's daily prices, then the new file's points after the study's last one (the base stays as it was)."""
    b = (D.read_json(base_path, {}) or {}).get('prices', [])
    top = max((p['timestamp'] for p in b), default=0)
    n = [p for p in (D.read_json(new_path, {}) or {}).get('prices', []) if p['timestamp'] > top]
    xs = sorted(b + n, key=lambda p: p['timestamp'])
    return [p['timestamp'] for p in xs], [p['price'] for p in xs]


def resolved_day_fn(points):
    """day -> whether the day whose median `daily_wait_fn` returns for it has every request finalized."""
    by = collections.defaultdict(list)
    for ts, w, _ in points:
        by[int(ts // 86400)].append(w is not None)
    days = sorted(by)
    ok = {d: all(by[d]) for d in days}

    def f(day):
        j = bisect.bisect_right(days, day) - 1
        return ok[days[j]] if j >= 0 else True
    return f


def build_world(window_days=WINDOW_DAYS, base_swaps=True, log=print):
    """Everything both bases and the new window imply, joined: block -> time, NAVs, prices, every queue's request points
    and wait function, and (with `base_swaps`) every priced swap of the four assets over the trailing `window_days`.

    The bases are the studies' own files, unchanged: stETH and rsETH swaps are priced from the long window's raw logs
    with the long window's state (this reproduces the swaps files queue_book read, checked on 2026-10-11), weETH and
    LBTC come from their studies' priced swaps files, and the new window is priced from research/queue_live/swaps the
    same way. Queue points are rebuilt from both windows' events, so requests pending at the studies' end resolve."""
    base_last, ef_last = base_ends()
    man = D.read_json(SWAPS / 'manifest.json')
    if not man:
        raise SystemExit('nothing collected yet: run quote or monitor first')
    last = man['last_block']
    hdr = {}
    for p in (LONG / 'headers.json', QBX / 'etherfi_headers.json', NEW_ASSETS / 'headers.json', SWAPS / 'headers.json'):
        for k, v in (D.read_json(p, {}) or {}).items():
            hdr.setdefault(int(k), v['ts'])
    hb = sorted(hdr)
    hts = [hdr[n] for n in hb]

    def ts_at(n):
        return int(round(D.interp(hb, hts, n)))

    def block_at(ts):
        return int(D.interp(hts, hb, ts))
    end_ts = hdr[last]
    samples = collections.defaultdict(dict)
    for p in (LONG / 'state.json', NEW_ASSETS / 'state.json', SWAPS / 'state.json'):
        for k, v in ((D.read_json(p, {}) or {}).get('samples') or {}).items():
            for s in v:
                if s.get('value') is not None:
                    samples[k].setdefault(s['block'], s)
    samples = {k: sorted(v.values(), key=lambda s: s['block']) for k, v in samples.items()}
    grids = {k: ([s['block'] for s in v], [s['value'] for s in v]) for k, v in samples.items() if v}
    steps = [tuple(x) for x in D.read_json(EF_LONG / 'etherfi_payouts.json')['nav_steps']]
    reb = sorted((hx(l['blockNumber']), hx(l['logIndex']), word(l['data'], 0) / word(l['data'], 1))
                 for l in D.load_stream(SWAPS, 'ef_lp') if word(l['data'], 1))
    steps += [(b, v) for b, _, v in reb if b > steps[-1][0]]
    sx, sy = [b for b, _ in steps], [v for _, v in steps]

    def nav_at(key, n):
        if key == 'weeth_nav_step':
            return D.step_at(sx, sy, n)
        g = grids.get(key)
        return D.interp(g[0], g[1], n) if g else None
    ex, ey = merged_prices(LONG / 'eth_usd.json', SWAPS / 'eth_usd.json')
    bx, by_ = merged_prices(NEW_ASSETS / 'btc_usd.json', SWAPS / 'btc_usd.json')

    def eth_usd(ts):
        return D.interp(ex, ey, ts)

    def btc_usd(ts):
        return D.interp(bx, by_, ts)
    stale = {'eth_usd_last_utc': utc(ex[-1]), 'btc_usd_last_utc': utc(bx[-1]),
             'eth_usd_stale': ex[-1] < end_ts - 2 * 86400, 'btc_usd_stale': bx[-1] < end_ts - 2 * 86400}

    # Queue points, as the study's wait_model builds them, over both windows.
    qlogs = list(D.load_stream(LONG, 'x_queues')) + list(D.load_stream(SWAPS, 'x_queues'))
    reqs, fins = {}, []
    for l in qlogs:
        if l['address'].lower() != D.LIDO_WQ:
            continue
        t0 = l['topics'][0]
        if t0 == D.XTOPICS['LidoRequested']:
            reqs[int(l['topics'][1], 16)] = ts_at(hx(l['blockNumber']))
        elif t0 == D.XTOPICS['LidoFinalized']:
            fins.append((int(l['topics'][1], 16), int(l['topics'][2], 16), ts_at(hx(l['blockNumber']))))
    pts = {'lido': list(D.lido_waits(reqs, fins, end_ts).values())}
    kr = D.SURFACE['kelp']['redemption']
    pts['kelp'] = D.pointer_waits([(s['ts'], s['value']) for s in samples.get(kr['created'], [])],
                                  [(s['ts'], s['value']) for s in samples.get(kr['finalized'], [])], kr['finalized_inclusive'])
    wr = list(D.load_stream(QBX, 'ef_wrnft')) + list(D.load_stream(SWAPS, 'ef_wrnft'))
    requests, claims, flags, _, _ = D.decode_etherfi_wrnft(wr)
    fin = (D.read_json(QBX / 'etherfi_finality.json') or {})['samples']['last_finalized'] + \
        ((D.read_json(SWAPS / 'etherfi_finality.json', {}) or {}).get('samples') or {}).get('last_finalized', [])
    fpts = [(x['block'], ts_at(x['block']), int(x['value'])) for x in fin]
    fin_at = D.finalization_times(fpts, {rid: r['block'] for rid, r in requests.items()})
    ef_recs = D.etherfi_payout_records(requests, claims, fin_at, lambda n: D.step_at(sx, sy, n), None, ts_at)
    pts['etherfi_ev'] = [(r['ts'], r.get('wait_days'), None if 'wait_days' in r else (end_ts - r['ts']) / 86400.0)
                         for r in ef_recs]
    D.write_json(SWAPS / 'etherfi_payouts.json', {
        'waits_recent': [x for x in pts['etherfi_ev'] if x[0] >= end_ts - 60 * 86400 or x[1] is None],
        'nav_steps_recent': [list(x) for x in steps if x[0] > base_last - 10 * D.BLOCKS_PER_DAY],
        'note': 'derived each run from the study streams (research/2026-10-10/queue_bids_ext/raw/ef_*) and the new ones '
                'here; requests of the last 60 days and every pending one, and the NAV steps since ten days before the '
                'study end'})
    wait_fn, wait_summary, resolved = {}, {}, {}
    for k in ETH3:
        f, by_day = D.daily_wait_fn(pts[k], 3.0)
        wait_fn[k], resolved[k] = f, resolved_day_fn(pts[k])
        done = [w for _, w, _ in pts[k] if w is not None]
        pend = [(end_ts - ts) / 86400.0 for ts, w, _ in pts[k] if w is None]
        wait_summary[k] = {'points': len(pts[k]), 'finalized': len(done), 'pending': len(pend),
                           'oldest_pending_days': max(pend) if pend else None,
                           'median_days_all': statistics.median(done) if done else None,
                           'model_at_end_days': f(end_ts), 'last_days': {utc(d * 86400)[:10]: by_day[d] for d in sorted(by_day)[-7:]}}
    lbtc_days = D.SURFACE['lbtc_cb']['redemption']['days']
    wait_fn['lbtc_cb'], resolved['lbtc_cb'] = (lambda ts, d=lbtc_days: d), (lambda day: True)
    wait_summary['lbtc_cb'] = {'kind': 'constant', 'median_days': lbtc_days}

    W = {'base_last': base_last, 'ef_base_last': ef_last, 'last': last, 'end_ts': end_ts, 'ts_at': ts_at, 'block_at': block_at,
         'nav_at': nav_at,
         'eth_usd': eth_usd, 'btc_usd': btc_usd, 'prices': stale, 'samples': samples, 'pts': pts, 'wait_fn': wait_fn,
         'wait_summary': wait_summary, 'resolved': resolved, 'qlogs': qlogs, 'ef': (requests, claims, flags, ef_recs),
         'manifest': man}
    # Priced swaps.
    metas = swap_metas()
    first_ts = end_ts - window_days * 86400
    first_block = hb[max(0, bisect.bisect_left(hts, first_ts) - 1)]
    unit_usd = {'ETH': eth_usd, 'BTC': btc_usd}
    kept, sells, market, info = {}, {}, {}, {}
    for k in ALL4:
        a = D.SURFACE[k]
        base = []
        if base_swaps:
            if k in ('lido', 'kelp'):
                sw, _ = D.surface_swaps(LONG, k, metas_for(k, metas), nav_at, ts_at, eth_usd, first_block, base_last)
                base = [s for s in sw if not s['excluded_print']]
            else:
                p = EF_LONG / 'swaps_etherfi_ev.jsonl.gz' if k == 'etherfi_ev' else NEW_ASSETS / 'swaps_lbtc_cb.jsonl.gz'
                with gzip.open(p, 'rt') as f:
                    base = [json.loads(l) for l in f]
            base = [s for s in base if s['ts'] >= first_ts and s['block'] <= base_last]
        new, skipped = D.surface_swaps(SWAPS, k, metas_for(k, metas), nav_at, ts_at, unit_usd[a['unit']], base_last + 1, last)
        new_kept = [s for s in new if not s['excluded_print']]
        with gzip.open(SWAPS / ('swaps_%s.jsonl.gz' % k), 'wt') as f:
            for s in new_kept:
                f.write(json.dumps({x: s.get(x) for x in ('ts', 'block', 'li', 'tx', 'pool', 'side', 'token', 'amount', 'usd',
                                                           'price', 'nav', 'discount_bps', 'fee_bps', 'unit_usd')}) + '\n')
        kept[k] = sorted(base + new_kept, key=lambda s: (s['ts'], s['block'], s.get('li') or 0))
        sells[k] = [s for s in kept[k] if s['side'] == 'sell']
        market[k] = D.market_discount_fn(kept[k])
        info[k] = {'base_swaps': len(base), 'new_swaps': len(new_kept), 'new_sells': sum(1 for s in new_kept if s['side'] == 'sell'),
                   'new_excluded_prints': len(new) - len(new_kept), 'new_skipped': dict(skipped),
                   'new_first_utc': utc(new_kept[0]['ts']) if new_kept else None,
                   'new_last_utc': utc(new_kept[-1]['ts']) if new_kept else None}
    W.update({'kept': kept, 'sells': sells, 'market': market, 'swaps_info': info, 'first_ts': first_ts})
    wst = [(s['ts'], s['value']) for s in samples.get('wsteth_nav', [])]
    W['staking_apr_window'] = D.apr_from_nav([x for x in wst if x[0] >= first_ts]) or D.ETH_STAKING_FALLBACK
    W['staking_apr_now'] = staking_apr(wst, end_ts) or D.ETH_STAKING_FALLBACK
    return W


def simulate_levels(envs, size_usd, levels, gas_usd=D.GAS_PER_FILL_USD, min_fill_usd=D.MIN_FILL_USD, delay_s=0):
    """Resting limit orders on one pool: simulate_book's mechanics, but a fill earns the order's price, not the market's.

    `levels`: [(share of the pool, net(asset, ts, carry_bps) -> the level's edge over carry and redemption fee in bp, or
    None for no order)], shallowest first. A sell whose capped net edge (simulate_book's: the print less two pool fees,
    capped at the venue median less one, less the wait's carry and the redemption fee) is at least a level's edge fills
    that level, up to the level's free share of the pool, shallower levels first (a solver fills the order that pays
    most first), and earns the level's edge. Capital is locked for the wait, as in simulate_book. Gas is charged once
    per sell filled (one settlement, one withdrawal request); fills under the minimum or not clearing gas are skipped,
    as in simulate_book (a resting order cannot refuse them, so this flatters small depths slightly). `delay_s`: a level
    is live for a sell only if the venue median showed that level's edge `delay_s` earlier (the late-entry test).
    Returns (fills, stats); fills carry `value_usd` and `ts` for `daily_values`."""
    ck = ('_lv_edges', delay_s)
    merged = []
    for k in sorted(envs):
        e = envs[k]
        if ck not in e:
            rows = []
            for s in e['sells']:
                wait = e['wait'](s['ts'])
                carry = 0.0 if e['accrues'] else wait * e['carry'](s['ts'])
                disc = capturable_bps(s, e['market'](s['ts']))
                seen = float('inf')
                if delay_s:
                    mp = e['market'](s['ts'] - delay_s)
                    seen = (mp - s['fee_bps'] - carry - e['redemption_fee_bps']) if mp is not None else float('-inf')
                rows.append((disc - carry - e['redemption_fee_bps'], wait, seen, carry))
            e[ck] = rows
        for i, s in enumerate(e['sells']):
            merged.append((s['ts'], k, i))
    merged.sort()
    caps = [share * size_usd for share, _ in levels]
    locked = [0.0] * len(levels)
    heap, fills = [], []
    st = {'crossing_sells': 0, 'filled_usd': 0.0, 'missed_capital_usd': 0.0, 'by_level_filled_usd': [0.0] * len(levels),
          'by_asset_filled_usd': collections.defaultdict(float), 'by_asset_value_usd': collections.defaultdict(float)}
    for ts, k, i in merged:
        while heap and heap[0][0] <= ts:
            _, j, amt = heapq.heappop(heap)
            locked[j] -= amt
        s = envs[k]['sells'][i]
        edge, wait, seen, carry = envs[k][ck][i]
        parts, left, earned, crossed = [], s['usd'], 0.0, False
        for j, (_, net) in enumerate(levels):
            n = net(k, ts, carry)
            if n is None or edge < n - 1e-9 or seen < n - 1e-9:
                continue
            crossed = True
            take = min(left, max(0.0, caps[j] - locked[j]))
            if take > 0:
                parts.append((j, take, n))
                left -= take
                earned += take * n / 1e4
        if not crossed:
            continue
        st['crossing_sells'] += 1
        fill = s['usd'] - left
        st['missed_capital_usd'] += left
        value = earned - gas_usd
        if fill < min_fill_usd or value <= 0:
            continue
        for j, take, _ in parts:
            locked[j] += take
            st['by_level_filled_usd'][j] += take
            if wait > 0:
                heapq.heappush(heap, (ts + wait * 86400.0, j, take))
        st['filled_usd'] += fill
        st['by_asset_filled_usd'][k] += fill
        st['by_asset_value_usd'][k] += value
        fills.append({'asset': k, 'ts': ts, 'usd': fill, 'value_usd': value, 'edge_bps': edge, 'earned_bps': earned / fill * 1e4,
                      'wait_days': wait, 'levels': [(j, take) for j, take, _ in parts]})
    st['by_asset_filled_usd'] = dict(st['by_asset_filled_usd'])
    st['by_asset_value_usd'] = dict(st['by_asset_value_usd'])
    return fills, st


def trade_index(kept):
    """An asset's priced trades (both sides, every venue) by time, for prices after a sell."""
    rows = sorted((s['ts'], s['pool'], s['discount_bps'], s['usd']) for s in kept)
    return {'ts': [r[0] for r in rows], 'rows': rows}


def window_median(idx, t0, t1):
    """The venue median over trades in [t0, t1) only: each venue's volume-weighted discount there, the median across the
    venues that traded; None when none did (no carry-over from earlier hours)."""
    lo, hi = bisect.bisect_left(idx['ts'], t0), bisect.bisect_left(idx['ts'], t1)
    if lo >= hi:
        return None
    acc = collections.defaultdict(lambda: [0.0, 0.0])
    for _, pool, d, u in idx['rows'][lo:hi]:
        acc[pool][0] += d * u
        acc[pool][1] += u
    vals = [a / b for a, b in acc.values() if b]
    return statistics.median(vals) if vals else None


def window_first(idx, t0, t1):
    """The discount of the first trade at or after t0 and before t1, or None."""
    lo = bisect.bisect_left(idx['ts'], t0)
    return idx['rows'][lo][2] if lo < len(idx['ts']) and idx['ts'][lo] < t1 else None


LATER_DELAYS = {'hour': 'bought at the next hour boundary H, priced over [H, H+1h)',
                'day': 'bought 24 hours after the sell, priced over [t+24h, t+25h)'}
LATER_READINGS = {'median': 'venue median over the later window, trades in it only; skipped when no venue traded',
                  'first': 'the first trade in the later window; skipped when none',
                  'lookback': 'market_discount_fn at the purchase (the study\'s 6h carry: a quiet venue counts as unchanged)'}


def later_rows(e, idx, reading, delay, cache=None):
    """Per sell of env e: (purchase ts, own-hour edge as simulate_book computes it, edge at the later price or None, wait
    at the purchase). The later edge = min(print less two fees, later discount less one fee) - carry - redemption fee,
    the carry and wait taken at the purchase (the withdrawal is requested then)."""
    out = []
    for s in e['sells']:
        t = s['ts']
        base = s['discount_bps'] - D.FEE_LEGS * s['fee_bps']
        m = e['market'](t)
        carry_t = 0.0 if e['accrues'] else e['wait'](t) * e['carry'](t)
        own = (min(base, m - s['fee_bps']) if m is not None else base) - carry_t - e['redemption_fee_bps']
        buy = (int(t // 3600) + 1) * 3600 if delay == 'hour' else t + 86400
        key = (reading, buy) if delay == 'hour' else None
        if cache is not None and key in cache:
            later = cache[key]
        else:
            if reading == 'median':
                later = window_median(idx, buy, buy + 3600)
            elif reading == 'first':
                later = window_first(idx, buy, buy + 3600)
            else:
                later = e['market'](buy)
            if cache is not None and key is not None:
                cache[key] = later
        wait_b = e['wait'](buy)
        carry_b = 0.0 if e['accrues'] else wait_b * e['carry'](buy)
        edge = None if later is None else min(base, later - s['fee_bps']) - carry_b - e['redemption_fee_bps']
        out.append((buy, own, edge, wait_b))
    return out


def simulate_later(envs, size_usd, hurdle_bps, reading, delay, idx, gas_usd=D.GAS_PER_FILL_USD, min_fill_usd=D.MIN_FILL_USD):
    """A taker that buys the qualifying sells back later instead of behind each seller (implementations f and g).

    A sell qualifies on what was known before the purchase: its own-hour edge (simulate_book's) above the hurdle. It is
    bought at the next hour boundary (`delay='hour'`) or a day later (`'day'`) for its own volume (less what the pool has
    locked), earning the edge at the later price (`later_rows`); it is skipped when that price is missing or leaves the
    edge at or under the hurdle (the pool has been bought back). One pool, capital locked from the purchase for the wait;
    gas, minimum fill and value filters as simulate_book. Returns (fills, stats); fills are dated at the purchase."""
    ck = ('_later', reading, delay)
    events = []
    for k in sorted(envs):
        e = envs[k]
        if ck not in e:
            e[ck] = later_rows(e, idx[k], reading, delay, cache={})
        for i, s in enumerate(e['sells']):
            events.append((e[ck][i][0], s['ts'], k, i))
    events.sort()
    heap, locked, fills = [], 0.0, []
    st = {'qualifying_own_hour': 0, 'later_missing': 0, 'later_below_hurdle': 0, 'filled_usd': 0.0, 'missed_capital_usd': 0.0}
    for buy, t, k, i in events:
        while heap and heap[0][0] <= buy:
            locked -= heapq.heappop(heap)[1]
        s = envs[k]['sells'][i]
        _, own, edge, wait = envs[k][ck][i]
        if own <= hurdle_bps or s['usd'] * own / 1e4 <= gas_usd:
            continue
        st['qualifying_own_hour'] += 1
        if edge is None:
            st['later_missing'] += 1
            continue
        if edge <= hurdle_bps or s['usd'] * edge / 1e4 <= gas_usd:
            st['later_below_hurdle'] += 1
            continue
        fill = min(s['usd'], max(0.0, size_usd - locked))
        st['missed_capital_usd'] += s['usd'] - fill
        value = fill * edge / 1e4 - gas_usd
        if fill < min_fill_usd or value <= 0:
            continue
        if wait > 0:
            heapq.heappush(heap, (buy + wait * 86400.0, fill))
            locked += fill
        st['filled_usd'] += fill
        fills.append({'asset': k, 'ts': buy, 'sell_ts': t, 'usd': fill, 'value_usd': value, 'edge_bps': edge,
                      'own_edge_bps': own, 'wait_days': wait})
    return fills, st


def persistence_stats(envs, idx, hurdle_bps=HURDLE, deep_bps=10.0):
    """Of the sells that qualified in their own hour (simulate_book's edge above the hurdle), the share whose edge still
    cleared the hurdle at the later price, an hour and a day later, under each reading; by count and by volume, for all
    of them and for the deep ones (own edge above `deep_bps`), by asset."""
    out = {}
    for k, e in envs.items():
        out[k] = {}
        for delay in LATER_DELAYS:
            for reading in LATER_READINGS:
                ck = ('_later', reading, delay)
                if ck not in e:
                    e[ck] = later_rows(e, idx[k], reading, delay, cache={})
                rows = [(s, r) for s, r in zip(e['sells'], e[ck]) if r[1] > hurdle_bps]
                res = {}
                for tag, sub in (('all', rows), ('deep', [(s, r) for s, r in rows if r[1] > deep_bps])):
                    n, vol = len(sub), sum(s['usd'] for s, _ in sub)
                    ok = [(s, r) for s, r in sub if r[2] is not None and r[2] > hurdle_bps]
                    miss = [(s, r) for s, r in sub if r[2] is None]
                    res[tag] = {'qualifying': n, 'qualifying_usd': vol,
                                'still_clear_share': len(ok) / n if n else None,
                                'still_clear_usd_share': sum(s['usd'] for s, _ in ok) / vol if vol else None,
                                'later_missing_share': len(miss) / n if n else None,
                                'median_edge_kept': (statistics.median([r[2] / r[1] for _, r in ok]) if ok else None)}
                out[k]['%s|%s' % (delay, reading)] = res
    return out


def requote_limits(env, first_day, last_day, fee_bps, hurdle_bps=HURDLE, offset_s=1800, inside_bps=1.0, period_s=86400,
                   lookback_s=86400):
    """A limit re-quoted from the market. Daily (implementation c, the defaults): at each day's registration (00:30 UTC)
    the limit discount is max(hurdle + carry, the median of the previous UTC day's 24 hourly venue medians less one
    pool fee, less `inside_bps`). Hourly (implementation e: period_s=lookback_s=3600, offset_s=0): the same from the
    last completed hour. Only whole hours before the period starts are read. Returns {period index: limit discount bp
    below NAV}, the period index being (ts - offset_s) // period_s."""
    out = {}
    for d in range(first_day * 86400 // period_s, (last_day + 1) * 86400 // period_s):
        start = d * period_s
        reg = start + offset_s
        carry = 0.0 if env['accrues'] else env['wait'](reg) * env['carry'](reg)
        floor_ = hurdle_bps + carry + env['redemption_fee_bps']
        ms = [env['market'](h) for h in range(start - lookback_s, start, 3600)]
        ms = [m - fee_bps for m in ms if m is not None]
        out[d] = max(floor_, statistics.median(ms) - inside_bps) if ms else floor_
    return out


def make_envs(W, keys=ALL4):
    """queue_book.load_env's env per asset, from the joined data: the carry is one APR over the loaded window, as there."""
    envs = {}
    for k in keys:
        a = D.SURFACE[k]
        c = (W['staking_apr_window'] if a['unit'] == 'ETH' else D.BTC_CARRY_APR) / 365.0 * 1e4
        envs[k] = {'key': k, 'unit': a['unit'], 'label': a['label'], 'sells': W['sells'][k], 'market': W['market'][k],
                   'wait': W['wait_fn'][k], 'carry': (lambda ts, c=c: c), 'accrues': a['redemption'].get('accrues', False),
                   'redemption_fee_bps': a['redemption'].get('fee_bps', 0.0)}
    return envs


def venue_fee_bps(W, k, since_ts=None):
    """The median of the asset's venues' fees (each venue once; a v4 pool's fee is its swaps' median)."""
    by = collections.defaultdict(list)
    for s in W['kept'][k]:
        if s.get('fee_bps') is not None and (since_ts is None or s['ts'] >= since_ts):
            by[s['pool']].append(s['fee_bps'])
    fees = [statistics.median(v) for v in by.values() if v]
    return statistics.median(fees) if fees else 1.0


def market_24h(W, k, as_of):
    """v2's market term: the median of the 24 whole-hour venue medians before the hour holding `as_of`, less the median
    venue fee of the 30 days before it. (None, 0) when no venue traded."""
    h_end = int(as_of // 3600) * 3600
    ms = [W['market'][k](h) for h in range(h_end - 86400, h_end, 3600)]
    ms = [m for m in ms if m is not None]
    if not ms:
        return None, 0
    return statistics.median(ms) - venue_fee_bps(W, k, since_ts=as_of - 30 * 86400), len(ms)


def v2_limit_bps(v1_limit_bps, market_term_bps, inside_bps=REQUOTE_INSIDE_BPS):
    return v1_limit_bps if market_term_bps is None else max(v1_limit_bps, market_term_bps - inside_bps)


def rule_limit_bps(W, k, as_of):
    """The limit the frozen rule would have quoted at `as_of`, from data known then."""
    if k == 'lbtc_cb':
        wait = D.SURFACE['lbtc_cb']['redemption']['days']
    else:
        wait, _, _ = wait_estimate(W['pts'][k], as_of)
    apr = staking_apr([(s['ts'], s['value']) for s in W['samples'].get('wsteth_nav', [])], as_of) or D.ETH_STAKING_FALLBACK
    v1 = ladder_entry(1.0, wait or 0.0, apr, HURDLE, D.SURFACE[k]['redemption'].get('fee_bps', 0.0))['limit_discount_bps']
    if utc(as_of)[:10] < V2_FROM:
        return v1
    reg = int(as_of // 86400) * 86400 + 1800                     # that day's registration
    return v2_limit_bps(v1, market_24h(W, k, reg)[0])


# ------------------------------------------------------------------------------------------------- criteria
def criterion_1(W, envs):
    """Trailing-90-day simulate_book value of the one-pool book at $15M and the frozen hurdle, annualised. The pool runs
    over the whole loaded year, so capital locked before the 90 days carries in, as in the studies' trailing figures."""
    cut = W['end_ts'] - C1_DAYS * 86400
    res = {}
    for name, keys in (('all4', ALL4), ('eth3', ETH3)):
        fills, st = Q.simulate_book({k: envs[k] for k in keys}, C1_POOL_USD, HURDLE)
        tail = [f for f in fills if f['ts'] > cut]
        by = collections.defaultdict(float)
        bym = collections.defaultdict(float)
        for f in tail:
            by[f['asset']] += f['value_usd']
            bym[utc(f['ts'])[:7]] += f['value_usd']
        res[name] = {'usd_per_year': sum(f['value_usd'] for f in tail) * 365.0 / C1_DAYS, 'fills': len(tail),
                     'filled_usd': sum(f['usd'] for f in tail), 'value_usd': sum(f['value_usd'] for f in tail),
                     'by_asset_usd_per_year': {k: v * 365.0 / C1_DAYS for k, v in sorted(by.items())},
                     'by_month_usd': dict(sorted(bym.items())),
                     'if_each_fill_earned_only_the_hurdle_usd_per_year':
                         sum(f['usd'] * HURDLE / 1e4 - D.GAS_PER_FILL_USD for f in tail) * 365.0 / C1_DAYS,
                     'median_edge_bps': statistics.median([f['edge_bps'] for f in tail]) if tail else None}
    fees = {}
    for k in ALL4:
        by = collections.defaultdict(list)
        for s in W['kept'][k]:
            if s.get('fee_bps') is not None:
                by[s['pool']].append(s['fee_bps'])
        fees[k] = statistics.median([statistics.median(x) for x in by.values()]) if by else 1.0
    lims = {k: requote_limits(envs[k], int(W['first_ts'] // 86400), int(W['end_ts'] // 86400), fees[k]) for k in ALL4}

    def net(k, ts, carry):
        lim = lims[k].get(int((ts - 1800) // 86400))
        return None if lim is None else lim - carry - envs[k]['redemption_fee_bps']
    res['v2_daily_requote'] = {'note': 'the v2 implementation on the same data (simulate_levels, daily re-quote at 00:30 UTC); '
                                       'reported beside the defined criterion, which the verdict still uses'}
    for name, keys in (('all4', ALL4), ('eth3', ETH3)):
        fl, _ = simulate_levels({k: envs[k] for k in keys}, C1_POOL_USD, [(1.0, net)])
        tail = [f for f in fl if f['ts'] > cut]
        res['v2_daily_requote'][name] = {'usd_per_year': sum(f['value_usd'] for f in tail) * 365.0 / C1_DAYS, 'fills': len(tail),
                                         'filled_usd': sum(f['usd'] for f in tail),
                                         'median_earned_bps': statistics.median([f['earned_bps'] for f in tail]) if tail else None}
    idx = {k: trade_index(W['kept'][k]) for k in ALL4}
    res['v3_hourly_taker'] = {'note': 'the v3 implementation on the same data (simulate_later: bought at the next hour, '
                                      'later venue median, frozen hurdle); reported beside the defined criterion'}
    for name, keys in (('all4', ALL4), ('eth3', ETH3)):
        fl, _ = simulate_later({k: envs[k] for k in keys}, C1_POOL_USD, HURDLE, 'median', 'hour', idx)
        tail = [f for f in fl if f['ts'] > cut]
        res['v3_hourly_taker'][name] = {'usd_per_year': sum(f['value_usd'] for f in tail) * 365.0 / C1_DAYS, 'fills': len(tail),
                                        'filled_usd': sum(f['usd'] for f in tail)}
    v = res['all4']['usd_per_year']
    res.update({'window': [utc(cut), utc(W['end_ts'])], 'pool_usd': C1_POOL_USD, 'hurdle_bps': HURDLE, 'threshold_usd_per_year': C1_MIN_USD,
                'staking_apr_window': W['staking_apr_window'],
                'status': 'pass' if v >= C1_MIN_USD else 'kill',
                'note': 'all4 is the row as defined (the verdict); eth3 is the ETH-only book being run first'})
    return res


def criterion_3(W, envs, hurdles=(HURDLE, 2.0)):
    """Trailing-year correlation of LBTC's and the ETH tokens' daily locked capital, each asset alone with unbounded
    capital (queue_book's overlap method). The verdict uses the frozen hurdle; 2bp is queue_book's overlap hurdle."""
    end_day = int(W['end_ts'] // 86400)
    first_day = end_day - C3_DAYS + 1
    out = {}
    for h in hurdles:
        demand = {}
        for k in ALL4:
            fills, _ = Q.simulate_book({k: envs[k]}, Q.UNBOUNDED, h)
            demand[k] = Q.locked_daily(fills, first_day, C3_DAYS)
        eth = [sum(demand[k][d] for k in ETH3) for d in range(C3_DAYS)]
        out['h=%g' % h] = {'corr_lbtc_vs_eth3_sum': Q.corr(demand['lbtc_cb'], eth),
                           'pairs': {'lbtc_cb|%s' % k: Q.corr(demand['lbtc_cb'], demand[k]) for k in ETH3},
                           'days_lbtc_locked': sum(1 for x in demand['lbtc_cb'] if x > 0),
                           'days_eth3_locked': sum(1 for x in eth if x > 0),
                           'peak_locked_usd': {k: max(v) for k, v in demand.items()}}
    c = out['h=%g' % HURDLE]['corr_lbtc_vs_eth3_sum']
    info = W['swaps_info']['lbtc_cb']
    refreshed = info['new_swaps'] > 0 and not W['prices']['btc_usd_stale']
    status = 'undefined (no locked capital on one side)' if c is None else ('pass' if c <= C3_MAX else 'kill')
    return {'window': [utc(first_day * 86400), utc((end_day + 1) * 86400 - 1)], 'threshold': C3_MAX, **out,
            'lbtc_refreshed': refreshed, 'lbtc_new_swaps': info['new_swaps'], 'status': status,
            'note': 'LBTC extended through the new window with the same pools (cbBTC side), lbtc_nav and BTC/USD' if refreshed
                    else 'LBTC NOT refreshed past the study window (no new priced swaps or stale BTC/USD)'}


def cow_buys(W, orders=None):
    """CoW trades in the new window that bought one of the bid tokens with WETH/ETH, priced against NAV at the block."""
    trades, total = load_cow_trades()
    out = []
    for t in trades:
        sym = TOKEN_BY_ADDR.get(t['buy_token'])
        if sym is None or t['sell_token'] not in (C.WETH, C.ETH):
            continue
        key = NAV_KEY_PRICED[sym]
        nav = 1.0 if key is None else W['nav_at'](key, t['block'])
        eth_paid = (t['sell_amount'] + t['fee_amount']) / 1e18
        got = t['buy_amount'] / 1e18
        if not got or not nav:
            continue
        ts = W['ts_at'](t['block'])
        o = (orders or {}).get(t['uid']) or {}
        age_h, limit_disc = None, None
        if o.get('creationDate'):
            age_h = (ts - dt.datetime.fromisoformat(o['creationDate'].replace('Z', '+00:00')).timestamp()) / 3600.0
        if o.get('kind') == 'sell' and o.get('sellAmount') and o.get('buyAmount'):
            limit_disc = (1 - int(o['sellAmount']) / int(o['buyAmount']) / nav) * 1e4
        out.append({'token': sym, 'asset': TOKENS[sym]['asset'], 'block': t['block'], 'ts': ts, 'eth': eth_paid,
                    'discount_bps': (1 - eth_paid / (got * nav)) * 1e4, 'owner': t['owner'], 'tx': t['tx'], 'uid': t['uid'],
                    'age_hours': age_h, 'limit_discount_bps': limit_disc})
    return sorted(out, key=lambda x: (x['block'], x['tx'])), total


CRITERION_4_LIVE = (
    'Once the book\'s own orders rest, the test is run on them alone, and it becomes a direct one: (1) every order the '
    'owner posted, from CoW\'s account endpoint (GET /api/v1/account/<owner>/orders), which also lists orders that never '
    'filled, invisible in Trade events; (2) for each whole hour an order was open (created, not expired or cancelled, '
    'not fully executed) and funded (the owner\'s WETH balance and GPv2VaultRelayer allowance covering its remaining '
    'sellAmount, read at that hour), whether the venue median less one fee was at or beyond its limit; (3) the owner\'s '
    'own Trade events (owner is indexed, so one cheap getLogs filter). A funded order sitting through such an hour '
    'without a fill is a failure of the implementation; a fill tells us the surplus over the limit we were paid.')


def resting_order_check(W, buys, orders, fees):
    """The kill criterion's own words on orders that can be observed before the book's rest: CoW orders (any owner) that
    bought a bid token with ETH in the new window, with their creation time and limit from CoW's API. For each, the whole
    clock hours between its creation (or the window's start) and the hour it first filled in which the venue median,
    less one pool fee, was at or beyond that order's own limit (re-expressed against NAV each hour). An order with such
    an hour rested through a cleared market without filling: evidence that resting orders do not fill."""
    first = {}
    for b in buys:
        first.setdefault(b['uid'], b)
    win = W['ts_at'](W['base_last'] + 1)
    rows, unknown = [], 0
    for uid, b in first.items():
        o = orders.get(uid) or {}
        if not (o.get('creationDate') and o.get('sellAmount') and o.get('buyAmount')):
            unknown += 1
            continue
        c = dt.datetime.fromisoformat(o['creationDate'].replace('Z', '+00:00')).timestamp()
        px = (int(o['sellAmount']) + int(o.get('feeAmount') or 0)) / int(o['buyAmount'])
        k, key = b['asset'], NAV_KEY_PRICED[b['token']]
        h0, h1 = int(-(-max(c, win) // 3600) * 3600), int(b['ts'] // 3600) * 3600
        cleared = []
        for h in range(h0, h1, 3600):
            m = W['market'][k](h)
            nav = 1.0 if key is None else W['nav_at'](key, W['block_at'](h))
            lim = (1 - px / nav) * 1e4
            if m is not None and m - fees[k] >= lim:
                cleared.append({'hour_utc': utc(h), 'market_bps': m, 'order_limit_bps': lim})
        rows.append({'uid': uid, 'token': b['token'], 'owner': b['owner'], 'created_utc': utc(c), 'first_fill_utc': utc(b['ts']),
                     'rested_hours': (b['ts'] - c) / 3600.0, 'kind': o.get('kind'), 'partially_fillable': o.get('partiallyFillable'),
                     'fill_discount_bps': b['discount_bps'], 'limit_discount_bps_at_fill': b['limit_discount_bps'],
                     'whole_hours_before_fill': max(0, (h1 - h0) // 3600), 'hours_market_cleared_its_limit': len(cleared),
                     'cleared_hours': cleared[:5]})
    ev = [r for r in rows if r['hours_market_cleared_its_limit'] >= 1]
    return {'orders_observed': len(rows), 'orders_without_details': unknown,
            'orders_resting_1h_plus': sum(1 for r in rows if r['rested_hours'] >= 1),
            'orders_through_a_cleared_hour': len(ev), 'evidence': ev[:20],
            'rested_1h_plus': [r for r in rows if r['rested_hours'] >= 1][:20]}


def criterion_4(W, rows, buys, orders=None):
    """Two readings of 'resting orders observed not to fill while the venue-median discount clears the limit for an hour'.

    Literal (as the forward test was specified): hours of the new window in which the venue-median discount, less one
    pool fee, cleared the frozen limit while no CoW trade bought the token with ETH at or beyond it. The limit is the
    ladder in force for the whole hour, or the one the frozen rule would have quoted then. Until the book's own orders
    rest this tests everyone's orders, and in a token nobody bids on CoW (rsETH; weETH most hours) it flags the absence
    of bidders, not a failure to fill: each flag carries the token's CoW buy flow so it can be read.
    Resting orders (`resting_order_check`): orders that did rest and sat through a cleared hour unfilled.
    Status: kill on resting-order evidence; review when a literal flag falls in an hour with CoW buys of that token;
    otherwise pass (vacuous when no hour cleared)."""
    per = periods(rows)
    first_h = -(-W['ts_at'](W['base_last'] + 1) // 3600) * 3600          # the first whole hour of the new window
    last_h = int(W['end_ts'] // 3600) * 3600 - 3600                       # the last whole hour before the data end
    hours = list(range(int(first_h), last_h + 1, 3600))
    by_hour = collections.defaultdict(list)
    for b in buys:
        by_hour[(b['asset'], int(b['ts'] // 3600) * 3600)].append(b)
    fees = {k: venue_fee_bps(W, k, since_ts=W['end_ts'] - 30 * 86400) for k in ETH3}
    res, flagged_all, cleared_all, informative = {}, 0, 0, 0
    for k in ETH3:
        fee = fees[k]
        cleared, flagged, lim_cache = [], [], {}
        for h in hours:
            m = W['market'][k](h)
            if m is None or m - fee < HURDLE:          # the limit is never below the hurdle: skip the arithmetic
                continue
            r = governing(per, h + 1e-6)
            if r is not None and r['registered_ts'] <= h:
                syms = [s for s, v in TOKENS.items() if v['asset'] == k and s in r['ladder']]
                lim, src = min(r['ladder'][s]['limit_discount_bps'] for s in syms), 'registered %s' % r['date']
            else:
                d = h // 86400
                if d not in lim_cache:
                    lim_cache[d] = rule_limit_bps(W, k, h)
                lim, src = lim_cache[d], 'rule-implied'
            if m - fee < lim:
                continue
            got = [b for b in by_hour.get((k, h), []) if b['discount_bps'] >= lim]
            row = {'hour_utc': utc(h), 'market_bps': m, 'fee_bps': fee, 'limit_bps': lim, 'limit_source': src,
                   'cow_buys_in_hour': len(by_hour.get((k, h), [])), 'cow_buys_at_or_beyond_limit': len(got),
                   'best_cow_discount_bps': max((b['discount_bps'] for b in by_hour.get((k, h), [])), default=None)}
            cleared.append(row)
            if not got:
                flagged.append(row)
        n_inf = sum(1 for r in flagged if r['cow_buys_in_hour'] > 0)
        res[k] = {'venue_fee_bps': fee, 'hours_cleared': len(cleared), 'hours_flagged': len(flagged),
                  'flagged_in_hours_with_cow_buys_of_the_token': n_inf,
                  'cow_buys_of_the_token_with_eth_in_window': sum(1 for b in buys if b['asset'] == k),
                  'flagged': flagged[:50], 'cleared_sample': cleared[:20]}
        flagged_all += len(flagged)
        cleared_all += len(cleared)
        informative += n_inf
    rest = resting_order_check(W, buys, orders or {}, fees)
    if rest['orders_through_a_cleared_hour']:
        status = 'kill'
    elif informative:
        status = 'review: %d literal flag(s) in hours with CoW buys of the token, no resting-order evidence' % informative
    elif cleared_all == 0:
        status = 'pass (vacuous: the venue-median discount never cleared the limit)'
    elif flagged_all == 0:
        status = 'pass'
    else:
        status = ('pass: the literal check flagged %d hour(s), all in hours without a CoW buy of the token (no bidder, not a '
                  'failed fill); no observed resting order sat through a cleared hour' % flagged_all)
    return {'hours_evaluated': len(hours), 'window': [utc(hours[0]) if hours else None, utc(hours[-1] + 3600) if hours else None],
            'cow_lst_buys_with_eth': len(buys),
            'literal': {'hours_cleared': cleared_all, 'hours_flagged': flagged_all,
                        'flagged_in_hours_with_cow_buys_of_the_token': informative, 'by_asset': res},
            'resting_orders': rest, 'hours_cleared': cleared_all, 'hours_flagged': flagged_all, 'status': status,
            'proxy': 'other owners\' CoW orders stand in for the book\'s own until they rest; once they do, filter by owner',
            'once_live': CRITERION_4_LIVE}


def criterion_2(W):
    """The payout checks on claims made in the new window (not part of the requested verdict; reported beside it)."""
    first, ef_first = W['base_last'] + 1, W['ef_base_last'] + 1
    out = {}
    req = {}
    for l in W['qlogs']:
        if l['address'].lower() == D.LIDO_WQ and l['topics'][0] == D.XTOPICS['LidoRequested']:
            req[int(l['topics'][1], 16)] = word(l['data'], 0)
    diffs = []
    for l in D.load_stream(SWAPS, 'x_redeem'):
        if l['address'].lower() == D.LIDO_WQ and l['topics'][0] == D.XTOPICS['LidoClaimed']:
            rid = int(l['topics'][1], 16)
            if req.get(rid) and req[rid] >= 10 ** 16:
                diffs.append(1e4 * (word(l['data'], 0) / req[rid] - 1.0))
    short = [x for x in diffs if x < -0.01]
    out['lido'] = {'claims': len(diffs), 'min_bps': min(diffs) if diffs else None, 'short_claims': len(short),
                   'status': 'fail' if short else ('pass' if diffs else 'no claims')}
    queued = collections.defaultdict(list)
    kd = []
    for l in list(D.load_stream(LONG, 'x_redeem')) + list(D.load_stream(SWAPS, 'x_redeem')):
        if l['address'].lower() != D.KELP_WM or len(l['topics']) < 3 or '0x' + l['topics'][2][-40:] != D.ETH_SENTINEL:
            continue
        n = hx(l['blockNumber'])
        if l['topics'][0] == D.XTOPICS['KelpQueued']:
            queued[('0x' + l['topics'][1][-40:], word(l['data'], 0))].append(n)
        elif l['topics'][0] == D.XTOPICS['KelpFinalized']:
            burned, received = word(l['data'], 0), word(l['data'], 1)
            key = ('0x' + l['topics'][1][-40:], burned)
            if not burned or not queued.get(key):
                continue
            qn = queued[key].pop(0)
            if n >= first:
                nq = W['nav_at']('rseth_nav', qn)
                kd.append(1e4 * (received / burned - nq) / nq)
    worst = [x for x in kd if x < -5.0]
    out['kelp'] = {'claims': len(kd), 'median_bps_vs_nav_at_request': statistics.median(kd) if kd else None,
                   'min_bps': min(kd) if kd else None, 'below_minus_5bp': len(worst),
                   'status': 'review' if worst else ('pass' if kd else 'no claims'),
                   'note': 'against the NAV interpolated at the request block (study p10/p90 -0.35/+0.42bp, min -20bp)'}
    requests, claims, _, ef_recs = W['ef']
    new_logs = list(D.load_stream(SWAPS, 'ef_wrnft'))
    _, _, flags_new, _, _ = D.decode_etherfi_wrnft(new_logs)
    pays = [r for r in ef_recs if r.get('claim_block', 0) >= ef_first and r['amount'] >= 0.01]
    shortp = [r for r in pays if r['payout_vs_request_bps'] < -0.01]
    fees = [r for r in ef_recs if r['block'] >= ef_first and r['fee'] > 0]
    out['etherfi'] = {'claims': len(pays), 'min_payout_vs_request_bps': min((r['payout_vs_request_bps'] for r in pays), default=None),
                      'short_claims': len(shortp), 'new_requests_with_fee': len(fees),
                      'invalidated_in_window': flags_new['invalidated'],
                      'status': 'fail' if (shortp or fees or flags_new['invalidated']) else ('pass' if pays else 'no claims')}
    st = [v['status'] for v in out.values()]
    out['status'] = 'fail' if 'fail' in st else ('review' if 'review' in st else 'pass')
    return out


# ------------------------------------------------------------------------------------------------- quote
def redemption_paths(rpc, block):
    """Is each queue taking requests at `block`? A flag that reads true closes the path; a read that fails is listed
    as unknown and does not close it."""
    out = {}
    for k, checks in PATH_CHECKS.items():
        res = rpc.batch([('eth_call', [{'to': to, 'data': D.sel(sig)}, hex(block)]) for _, to, sig in checks], allow_errors=True)
        st = {name: (None if (isinstance(r, dict) or r in (None, '0x')) else bool(int(r, 16)))
              for (name, _, _), r in zip(checks, res)}
        out[k] = {'flags': st, 'open': not any(v is True for v in st.values()),
                  'unknown': sorted(n for n, v in st.items() if v is None)}
    return out


def eth_price_now(W, log):
    try:
        req = urllib.request.Request('https://coins.llama.fi/prices/current/coingecko:ethereum', headers={'User-Agent': 'llm-quant research'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return float(json.loads(r.read())['coins']['coingecko:ethereum']['price']), 'coins.llama.fi current'
    except Exception as e:
        log({'eth_price_error': str(e)[:120]})
        return W['eth_usd'](W['end_ts']), 'DefiLlama daily, interpolated at the data end'


def quote_path(date):
    return OUT / 'quotes' / ('%s.json' % date)


def build_quote(rpc, W, pool_eth, log, now_s=None):
    now_s = now_s or time.time()
    head = rpc.call('eth_getBlockByNumber', ['latest', False])
    hn, hts = hx(head['number']), hx(head['timestamp'])
    navs = {}
    calls = [(sym, v['nav']) for sym, v in TOKENS.items() if v['nav']]
    res = rpc.batch([('eth_call', [{'to': D.STATE[k]['to'], 'data': D.STATE[k]['data']}, hex(hn)]) for _, k in calls])
    for (sym, k), r in zip(calls, res):
        navs[sym] = int(r[:66], 16)
    navs['stETH'] = 10 ** 18
    paths = redemption_paths(rpc, hn)
    end = W['end_ts']
    wst = [(s['ts'], s['value']) for s in W['samples'].get('wsteth_nav', [])]
    apr = staking_apr(wst, end)
    apr_src = 'wstETH stEthPerToken growth, %d days to %s' % (APR_DAYS, utc(end))
    if apr is None:
        apr, apr_src = D.ETH_STAKING_FALLBACK, 'fallback (too few wstETH samples)'
    px, px_src = eth_price_now(W, log)
    version = 2 if utc(now_s)[:10] >= V2_FROM else 1
    toks = {}
    for sym, v in TOKENS.items():
        k = v['asset']
        wait, n, window = wait_estimate(W['pts'][k], end)
        if wait is None:                            # no requests in 60 days: the queue's whole-history median
            wait, window = W['wait_summary'][k].get('median_days_all') or 3.0, 'all history'
        fee = D.SURFACE[k]['redemption'].get('fee_bps', 0.0)
        e = ladder_entry(navs[sym] / 1e18, wait, apr, HURDLE, fee)
        m24, n24 = market_24h(W, k, end)
        v1_lim, v2_lim = e['limit_discount_bps'], v2_limit_bps(e['limit_discount_bps'], m24)
        if version == 2:
            e['limit_discount_bps'] = v2_lim
            e['limit_price_eth_per_token'] = e['nav_eth'] * (1.0 - v2_lim / 1e4)
        e.update({'limit_rule_version': version, 'v1_limit_discount_bps': v1_lim, 'v2_limit_discount_bps': v2_lim,
                  'market_24h_less_fee_bps': m24, 'market_24h_hours': n24})
        vf = venue_fee_bps(W, k, since_ts=end - 30 * 86400)
        m = W['market'][k](end)
        drift = None
        if v['nav']:
            xs = [(s['ts'], s['value']) for s in W['samples'].get(v['nav'], []) if s['ts'] >= end - 30 * 86400]
            g = D.apr_from_nav(xs, days_min=15)
            drift = g / 365.0 * 1e4 if g is not None else None
        e.update({'asset': k, 'address': v['address'], 'nav_wei': navs[sym], 'nav_block': hn,
                  'nav_source': ('stETH redeems 1:1 in the Lido queue' if not v['nav'] else
                                 '%s %s' % (D.STATE[v['nav']]['to'], {'wsteth_nav': 'stEthPerToken()', 'weeth_nav': 'getRate()',
                                                                      'rseth_nav': 'rsETHPrice()'}[v['nav']])),
                  'wait_rule': {'requests_in_window': n, 'window_days': window, **W['wait_summary'][k]},
                  'cow_fee_bps_at_limit': 0.0, 'gas_usd_per_fill': D.GAS_PER_FILL_USD,
                  'gas_bps_at_min_fill': D.GAS_PER_FILL_USD / D.MIN_FILL_USD * 1e4,
                  'gas_bps_at_pool': D.GAS_PER_FILL_USD / (pool_eth * px) * 1e4,
                  'distance_below_nav_bps': e['limit_discount_bps'],
                  'limit_price_wei_per_token': limit_price_wei(navs[sym], e['limit_discount_bps']),
                  'venue_fee_bps_median': vf, 'seller_print_needed_bps': e['limit_discount_bps'] + D.FEE_LEGS * vf,
                  'market_median_bps_at_data_end': m, 'market_less_fee_bps': (m - vf) if m is not None else None,
                  'in_market_at_data_end': (m - vf >= e['limit_discount_bps']) if m is not None else None,
                  'nav_drift_bps_per_day': drift, 'path_open': paths[k]['open'], 'path_state': paths[k]})
        toks[sym] = e
    qb = D.read_json(QUEUE_BOOK) or {}
    chosen = ((qb.get('joint') or {}).get('all4') or {}).get(str(C1_POOL_USD), {}).get('chosen_hurdle')
    return {'generated': utc(now_s), 'date': utc(now_s)[:10], 'rule': FROZEN_RULE_V2 if version == 2 else FROZEN_RULE,
            'rule_version': version,
            'register_versions': ([2, 3] if utc(now_s)[:10] >= V3_FROM else [version]),
            'v3_rule': FROZEN_RULE_V3,
            'hurdle_check': {'frozen_bps': HURDLE, 'queue_book_analysis_now': chosen,
                             'match': chosen == 'h=%g' % HURDLE},
            'head': {'block': hn, 'utc': utc(hts)}, 'data_through': {'block': W['last'], 'utc': utc(W['end_ts'])},
            'staking_apr': {'value': apr, 'source': apr_src}, 'eth_usd': px, 'eth_usd_source': px_src,
            'pool_eth': pool_eth, 'pool_usd': pool_eth * px, 'tokens': toks, 'redemption_paths': paths,
            'notes': ['limit discount = hurdle + carry + redemption fee; pool fees and solver gas come out of the market\'s '
                      'discount, not the limit (a print must clear limit + 2 pool fees for the simulation to count it)',
                      'the limit is fixed in ETH per token for the order\'s 26 hours; wstETH, weETH and rsETH NAVs accrue '
                      '(nav_drift_bps_per_day), so a resting order drifts that much deeper below NAV per day',
                      'stETH pays 1:1 unless Lido is in bunker mode (discounted finalization)',
                      'gas ($10 per fill: buy, request, claim) is charged per fill in the paper P&L, not in the limit']}


def cmd_quote(args, rpc=None, log=None):
    log = log or Log(OUT / 'monitor.log')
    rpc = rpc or live_rpc.RPC(log_path=SWAPS / 'rpc_errors.jsonl', max_credits=args.max_credits)
    if not args.no_collect:
        collect(rpc, log)
    W = build_world()
    q = build_quote(rpc, W, args.pool_eth, log)
    p = quote_path(q['date'])
    if any(r['date'] == q['date'] for r in read_ledger(LEDGER)):
        p = OUT / 'quotes' / ('%s.unregistered-%s.json' % (q['date'], q['generated'][11:19].replace(':', '')))
        log({'quote': 'today is already registered; the registered ladder file is kept and this one written beside it', 'path': str(p)})
    p.parent.mkdir(parents=True, exist_ok=True)
    D.write_json(p, q)
    print('ladder %s, rule v%d (data to %s, staking APR %.3f%%, hurdle %gbp)' % (
        q['date'], q['rule_version'], q['data_through']['utc'], 100 * q['staking_apr']['value'], HURDLE))
    for sym, e in q['tokens'].items():
        print('  %-7s NAV %.8f  wait %5.2fd  carry %5.2fbp  hurdle %gbp  limit %.8f ETH (%5.2fbp below NAV)  market %s' % (
            sym, e['nav_eth'], e['wait_days'], e['carry_bps'], e['hurdle_bps'], e['limit_price_eth_per_token'],
            e['limit_discount_bps'], '—' if e['market_median_bps_at_data_end'] is None else '%.2fbp' % e['market_median_bps_at_data_end']) +
            '  [v1 %.2fbp, v2 %.2fbp]' % (e['v1_limit_discount_bps'], e['v2_limit_discount_bps']))
    print('wrote', p.relative_to(ROOT))
    return q, p


# ------------------------------------------------------------------------------------------------- orders
def build_orders(q, owner, pool_eth, valid_to):
    if not re.fullmatch(r'0x[0-9a-fA-F]{40}', owner):
        raise SystemExit('--owner must be a 0x-prefixed 20-byte address')
    owner = owner.lower()
    placeholder = owner == PLACEHOLDER_OWNER
    sell_wei = int(Decimal(str(pool_eth)) * 10 ** 18)
    dom = domain_separator()
    orders, skipped = [], {}
    for sym, e in q['tokens'].items():
        if not e.get('path_open', True):
            skipped[sym] = 'redemption path closed at the quote: %s' % e.get('path_state')
            continue
        lw = limit_price_wei(e['nav_wei'], e['limit_discount_bps'])
        buy = buy_amount_for(sell_wei, lw)
        o = {'sellToken': C.WETH, 'buyToken': e['address'], 'receiver': PLACEHOLDER_OWNER if placeholder else owner,
             'sellAmount': str(sell_wei), 'buyAmount': str(buy), 'validTo': int(valid_to), 'appData': APP_DATA,
             'feeAmount': '0', 'kind': 'sell', 'partiallyFillable': True, 'sellTokenBalance': 'erc20', 'buyTokenBalance': 'erc20'}
        dig = order_digest(o, dom)
        price = sell_wei / buy
        orders.append({'token': sym, 'order': o, 'owner': owner, 'digest': '0x' + dig.hex(), 'uid': order_uid(dig, owner, valid_to),
                       'signing_scheme': 'eip712', 'eip712': typed_data(o), 'nav_eth': e['nav_eth'],
                       'limit_discount_bps': e['limit_discount_bps'], 'limit_price_eth_per_token': e['limit_price_eth_per_token'],
                       'implied_price_eth_per_token': price, 'implied_discount_bps': (1 - price / e['nav_eth']) * 1e4,
                       'check_price_at_or_under_limit': sell_wei * 10 ** 18 <= buy * lw})
    return {'owner': owner, 'owner_is_placeholder': placeholder, 'pool_eth': pool_eth, 'sell_amount_wei': str(sell_wei),
            'valid_to': int(valid_to), 'valid_to_utc': utc(valid_to),
            'domain': dict(DOMAIN, separator='0x' + dom.hex()), 'order_type': ORDER_TYPE,
            'order_type_hash': '0x' + keccak_bytes(ORDER_TYPE.encode()).hex(),
            'app_data': {'json': APP_DATA_JSON, 'hash': APP_DATA}, 'orders': orders, 'skipped': skipped}


def cmd_orders(args):
    date = args.date or utc()[:10]
    p = quote_path(date)
    if not p.exists():
        raise SystemExit('no ladder for %s: run quote first' % date)
    q = D.read_json(p)
    pool = args.pool_eth if args.pool_eth is not None else q['pool_eth']
    now = int(time.time())
    out = build_orders(q, args.owner or PLACEHOLDER_OWNER, pool, now + VALID_HOURS * 3600)
    out.update({'generated': utc(now), 'date': date, 'quote_file': str(p.relative_to(ROOT)), 'quote_sha256': sha256_file(p),
                'never_signed_never_posted': True,
                'before_signing': ['WETH allowance for the GPv2VaultRelayer %s covering sellAmount' % VAULT_RELAYER,
                                   'a WETH balance: every order is sized to the whole pool and they share it; settlement fails a '
                                   'trade the balance cannot cover',
                                   'sign each eip712 payload (eth_signTypedData_v4); submit with signingScheme eip712, the owner, '
                                   'and fullAppData = app_data.json',
                                   'stETH transfers can arrive 1-2 wei short (share rounding)',
                                   'after a fill: request withdrawal (Lido requestWithdrawals / requestWithdrawalsWstETH, ether.fi '
                                   'LiquidityPool.requestWithdraw after unwrapping weETH, Kelp initiateWithdrawal) and claim when finalized']})
    if out['owner_is_placeholder']:
        out['warning'] = ('placeholder owner (zero address): the uids are not valid; pass --owner for the real uid and an '
                          'explicit receiver. The digest never includes the owner, and a zero receiver pays whoever signs, so '
                          'these digests are signable as they stand by any owner.')
    op = OUT / 'orders' / ('%s.json' % date)
    op.parent.mkdir(parents=True, exist_ok=True)
    D.write_json(op, out)
    for o in out['orders']:
        print('  %-7s sell %s WETH  buy >= %s  implied %.8f ETH/token (%.2fbp below NAV)  digest %s' % (
            o['token'], pool, o['order']['buyAmount'], o['implied_price_eth_per_token'], o['implied_discount_bps'], o['digest']))
    print('wrote', op.relative_to(ROOT), '(unsigned; nothing posted)')
    return out


# ------------------------------------------------------------------------------------------------- monitor, score
def exact_ts_fn(rpc):
    """block -> its own timestamp, cached; `prefetch` reads many in batches."""
    p = SWAPS / 'block_ts.json'
    cache = {int(k): v for k, v in (D.read_json(p, {}) or {}).items()}

    def prefetch(blocks):
        todo = sorted({b for b in blocks if b not in cache})
        for i in range(0, len(todo), 10):
            chunk = todo[i:i + 10]
            res = rpc.batch([('eth_getBlockByNumber', [hex(b), False]) for b in chunk])
            for b, r in zip(chunk, res):
                cache[b] = hx(r['timestamp'])
        D.write_json(p, {str(k): v for k, v in sorted(cache.items())})

    def f(b):
        if b not in cache:
            prefetch([b])
        return cache.get(b)
    f.prefetch = prefetch
    return f


def paper_sells(W):
    out = []
    for k in ETH3:
        for s in W['sells'][k]:
            if s['block'] <= W['base_last'] or s.get('token') not in TOKENS:
                continue
            out.append({'ts': s['ts'], 'block': s['block'], 'li': s.get('li') or 0, 'token': s['token'], 'asset': k,
                        'eth': s['amount'] * s['nav'], 'nav': s['nav'], 'usd': s['usd'], 'discount_bps': s['discount_bps'],
                        'fee_bps': s['fee_bps'], 'tx': s.get('tx'), 'pool': s.get('pool')})
    return sorted(out, key=lambda s: (s['block'], s['li']))


def run_score(W, rows, rpc=None):
    sells = paper_sells(W)

    def measured(asset, ts):
        return W['wait_fn'][asset](ts), W['resolved'][asset](int(ts // 86400))
    ex = None
    if rpc is not None and rows:
        ex = exact_ts_fn(rpc)
        lo = min(r['registered_ts'] for r in rows) - 1800
        min_lim = min(min(e['limit_discount_bps'], e['hurdle_bps'] + e['carry_bps']) for r in rows for e in r['ladder'].values())
        cand = [s['block'] for s in sells if s['ts'] >= lo and
                capturable_bps(s, W['market'][s['asset']](s['ts'])) >= min_lim - 1e-9]
        ex.prefetch(cand)
    out = {}
    idx = None
    for v in sorted({r.get('rule_version', 1) for r in rows}):
        rs = [r for r in rows if r.get('rule_version', 1) == v]
        if v == 3:
            idx = idx or {k: trade_index(W['kept'][k]) for k in ETH3}
            fills, summ = score_taker(rs, sells, W['market'], idx, measured, W['eth_usd'], W['end_ts'], ex)
        else:
            fills, summ = score_paper(rs, sells, W['market'], measured, W['eth_usd'], W['end_ts'], ex)
        summ.update({'ladders': len(rs), 'sells_in_new_window': len(sells),
                     'sells_after_first_registration': sum(1 for s in sells if s['ts'] > min(r['registered_ts'] for r in rs))})
        out['v%d' % v] = (fills, summ)
    return out


def verdict(c1, c3, c4):
    kills = [n for n, c in (('1', c1), ('3', c3), ('4', c4)) if c and str(c.get('status', '')).startswith('kill')]
    return ('kill: criterion %s' % ', '.join(kills)) if kills else 'continue: no kill criterion met'


def write_paper(W, rows, by_version, crit, now_s):
    nfill = sum(len(f) for f, _ in by_version.values())
    res = {'generated': utc(now_s), 'rules': {'v1': FROZEN_RULE, 'v2': FROZEN_RULE_V2, 'v3': FROZEN_RULE_V3},
           'ledger': str(LEDGER.relative_to(ROOT)),
           'registered': len(rows),
           'ladders': [{'date': r['date'], 'rule_version': r.get('rule_version', 1), 'registered_at': r['registered_at'],
                        'valid_to_utc': utc(r['valid_to_ts']), 'pool_eth': r['pool_eth'],
                        'limits_bps': {s: e['limit_discount_bps'] for s, e in r['ladder'].items()}}
                       for r in sorted(rows, key=lambda r: r['registered_ts'])],
           'scoring': 'each rule version is its own paper pool; a ladder governs until it expires or the next ladder of its version',
           'data_through': {'block': W['last'], 'utc': utc(W['end_ts'])},
           'paper_by_version': {v: summ for v, (_, summ) in by_version.items()},
           'fills_by_version': {v: f for v, (f, _) in by_version.items()},
           'criteria': crit, 'verdict': verdict(crit.get('c1'), crit.get('c3'), crit.get('c4')),
           'status': 'accumulating: %d ladder(s) registered (%s), %d paper fill(s)' % (
               len(rows), ', '.join('%s %d' % (v, s['ladders']) for v, (_, s) in by_version.items()) or 'none', nfill)}
    D.write_json(LEDGER.with_suffix('.json'), res)
    return res


def cmd_monitor(args, rpc=None, log=None):
    log = log or Log(OUT / 'monitor.log')
    rpc = rpc or live_rpc.RPC(log_path=SWAPS / 'rpc_errors.jsonl', max_credits=args.max_credits)
    t0 = time.monotonic()
    man = collect(rpc, log) if not args.no_collect else D.read_json(SWAPS / 'manifest.json')
    W = build_world()
    log({'world': {k: v for k, v in W['swaps_info'].items()}, 'seconds': round(time.monotonic() - t0, 1)})
    envs = make_envs(W)
    c1 = criterion_1(W, envs)
    c3 = criterion_3(W, envs)
    c2 = criterion_2(W)
    now_s = time.time()
    reg_msg = 'not attempted (--no-register)'
    if not args.no_register:
        p = quote_path(utc(now_s)[:10])
        if p.exists():
            _, reg_msg = register(D.read_json(p), now_s, LEDGER, p)
        else:
            reg_msg = 'no ladder for today: run quote first'
    rows = read_ledger(LEDGER)
    orders = json.load(gzip.open(SWAPS / 'cow' / 'orders.json.gz', 'rt')) if (SWAPS / 'cow' / 'orders.json.gz').exists() else {}
    buys, cow_total = cow_buys(W, orders)
    c4 = criterion_4(W, [r for r in rows if r.get('rule_version', 1) in (1, 2)], buys, orders)
    by_version = run_score(W, rows, rpc)
    crit = {'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4}
    paper = write_paper(W, rows, by_version, crit, now_s)
    mon = {'generated': utc(now_s), 'rule': FROZEN_RULE, 'data_through': {'block': W['last'], 'utc': utc(W['end_ts'])},
           'collection': {k: man.get(k) for k in ('first_block', 'ef_first_block', 'last_block', 'last_block_utc', 'complete',
                                                  'state', 'etherfi_finality', 'cow', 'cow_orders', 'prices', 'headers', 'rpc',
                                                  'collect_seconds')},
           'streams': {k: {x: v.get(x) for x in ('first_block', 'last_block', 'ranges', 'log_entries_this_run')}
                       for k, v in (man.get('streams') or {}).items()},
           'swaps': W['swaps_info'], 'cow_trades_in_window': cow_total, 'prices': W['prices'],
           'waits': W['wait_summary'], 'staking_apr': {'window': W['staking_apr_window'], 'now_30d': W['staking_apr_now']},
           'registration': reg_msg, 'criteria': crit, 'paper_by_version': paper['paper_by_version'], 'verdict': paper['verdict'],
           'seconds': round(time.monotonic() - t0, 1)}
    mp = OUT / 'monitor' / ('%s.json' % utc(now_s)[:10])
    mp.parent.mkdir(parents=True, exist_ok=True)
    D.write_json(mp, mon)
    print('data to %s (block %d); new swaps %s' % (utc(W['end_ts']), W['last'],
                                                   {k: v['new_swaps'] for k, v in W['swaps_info'].items()}))
    print('c1 trailing %dd at $%.0fM, h=%gbp: all4 $%s/yr, eth3 $%s/yr -> %s' % (
        C1_DAYS, C1_POOL_USD / 1e6, HURDLE, format(round(c1['all4']['usd_per_year']), ','),
        format(round(c1['eth3']['usd_per_year']), ','), c1['status']))
    print('c2 payout checks -> %s' % c2['status'])
    c3v = c3['h=%g' % HURDLE]['corr_lbtc_vs_eth3_sum']
    print('c3 corr(LBTC, ETH3) trailing %dd = %s -> %s (%s)' % (C3_DAYS, '—' if c3v is None else '%.3f' % c3v, c3['status'],
                                                              'LBTC refreshed' if c3['lbtc_refreshed'] else 'LBTC NOT refreshed'))
    ro = c4['resting_orders']
    print('c4 literal: %d hours, %d cleared, %d flagged (%d in hours with CoW buys of the token); resting orders: %d observed, '
          '%d rested 1h+, %d sat through a cleared hour -> %s' % (
              c4['hours_evaluated'], c4['hours_cleared'], c4['hours_flagged'], c4['literal']['flagged_in_hours_with_cow_buys_of_the_token'],
              ro['orders_observed'], ro['orders_resting_1h_plus'], ro['orders_through_a_cleared_hour'], c4['status']))
    print('registration: %s; paper: %s; verdict: %s' % (reg_msg, '; '.join(
        '%s %d fills, %.4f ETH at the limit, %.4f at the market' % (v, s['fills'], s['value_eth_at_limit'], s['value_eth_at_market'])
        for v, s in paper['paper_by_version'].items()) or 'no ladders', paper['verdict']))
    for tag, label in (('v2_daily_requote', 'v2 daily re-quote'), ('v3_hourly_taker', 'v3 hourly taker')):
        x = c1.get(tag) or {}
        if x:
            print('c1 for the %s, trailing %dd at $%.0fM: all4 $%s/yr, eth3 $%s/yr' % (
                label, C1_DAYS, C1_POOL_USD / 1e6, format(round(x['all4']['usd_per_year']), ','), format(round(x['eth3']['usd_per_year']), ',')))
    print('wrote', mp.relative_to(ROOT), 'and', LEDGER.with_suffix('.json').relative_to(ROOT), '(%.0fs)' % mon['seconds'])
    return mon


IMPL_LS = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0, 75.0]
IMPL_SIZE = 15_000_000


def study_window(W):
    """queue_book's common window and envs, rebuilt from the joined data: the studies' sells only, venue medians from
    the studies' swaps only, and queue_book's staking APR (one APR over its window, as load_env charged it)."""
    qb = D.read_json(QUEUE_BOOK)
    first_ts = max(D.read_json(p / 'headers.json')[str(D.read_json(p / 'manifest.json')['first_block'])]['ts']
                   for p in (LONG, EF_LONG, NEW_ASSETS))
    last_ts = D.read_json(LONG / 'headers.json')[str(W['base_last'])]['ts']
    W2 = dict(W)
    W2['sells'] = {k: [s for s in v if s['block'] <= W['base_last']] for k, v in W['sells'].items()}
    W2['kept'] = {k: [s for s in v if s['block'] <= W['base_last']] for k, v in W['kept'].items()}
    W2['market'] = {k: D.market_discount_fn(W2['kept'][k]) for k in ALL4}
    W2['staking_apr_window'] = qb['assets']['lido']['staking_apr']
    return W2, first_ts // 86400, int((last_ts - first_ts) // 86400) + 1, first_ts, last_ts


def oos_report(variants, first_day, n_days, fills_by=None):
    """backtest.choose_then_test on daily $ series (choose on the first half, test once on the second), with queue_book's
    bootstrap interval, the out-of-sample value of every variant, and the chosen variant's split by asset and month."""
    ct = B.choose_then_test(variants, frac=0.5, periods_per_year=365, key='ann_return')
    c, chosen = ct['cutoff_index'], ct['chosen']
    oos = variants[chosen][c:]
    boot = B.block_bootstrap(oos, block=7, n=2000)
    years = (n_days - c) / 365.0
    r = {'chosen': chosen, 'n_variants': ct['n_variants'], 'in_sample_usd_per_year': ct['in_sample'].get('ann_return'),
         'in_sample_positive': ct['in_sample_positive'], 'out_of_sample_usd_per_year': ct['out_of_sample'].get('ann_return'),
         'oos_t': ct['oos_t'], 'oos_rank_of_chosen': ct['oos_rank'],
         'oos_ci95_usd_per_year': [boot['lo'] * 365 if boot['lo'] is not None else None, boot['hi'] * 365 if boot['hi'] is not None else None],
         'by_variant_oos_usd_per_year': {v: sum(x[c:]) / years for v, x in variants.items()},
         'cutoff_utc': utc((first_day + c) * 86400)}
    if fills_by:
        cut = first_day + c
        f = [x for x in fills_by[chosen] if int(x['ts'] // 86400) >= cut]
        by, bym = collections.defaultdict(float), collections.defaultdict(float)
        for x in f:
            by[x['asset']] += x['value_usd']
            bym[utc(x['ts'])[:7]] += x['value_usd']
        top = sorted(bym.values(), reverse=True)
        tot = sum(bym.values())
        r.update({'oos_fills': len(f), 'oos_filled_usd': sum(x['usd'] for x in f),
                  'oos_median_earned_bps': statistics.median([x.get('earned_bps', x['edge_bps']) for x in f]) if f else None,
                  'oos_by_asset_usd_per_year': {k: v / years for k, v in sorted(by.items())},
                  'oos_top_month_share': top[0] / tot if tot > 0 else None})
    return r


def oos_value(series, first_day, n_days):
    c = B.cutoff_index(n_days, 0.5)
    return sum(series[c:]) * 365.0 / (n_days - c)


def implementation_comparison(W, sets=(('all4', ALL4), ('eth3', ETH3)), size=IMPL_SIZE, log=print):
    """How the book's value depends on how it is implemented, on queue_book's window and split, at `size`:
    (a) a taker checked hourly (simulate_book, delay_s=3600: takes a sell at the market only once the venue median had
        shown the edge an hour earlier), and the no-delay taker the backtest assumed;
    (b) one fixed resting limit L bp below NAV net of carry (fills when simulate_book's capped net edge >= L, earns L);
        L chosen on the first half from IMPL_LS;
    (c) a daily re-quoted limit, max(hurdle + carry, prior UTC day's median venue median less one fee, less 1bp), set at
        00:30 UTC from data before it and filling at its limit until the next re-quote;
    (d) two resting levels, half the pool at (b)'s chosen L and half at 2L, the shallow level filling first;
    (e) added: the taker made executable, a limit re-quoted every hour from the last completed hour's venue median (less
        one fee, less 1bp, floored at hurdle + carry), filling at its limit within the hour. (a) fills every sell at its
        own capped discount, which an hourly decision can only get by buying behind each seller as it trades.
    The 1-day late-entry kept share is reported for (a), (b) and (d); (c) and (e) are set from past prices already."""
    W2, first_day, n_days, first_ts, last_ts = study_window(W)
    envs = make_envs(W2)
    fees = {}
    for k in ALL4:
        by = collections.defaultdict(list)
        for s in W2['kept'][k]:
            if s.get('fee_bps') is not None:
                by[s['pool']].append(s['fee_bps'])
        fees[k] = statistics.median([statistics.median(v) for v in by.values()])
    last_day = first_day + n_days - 1
    idx = {k: trade_index(W2['kept'][k]) for k in ALL4}
    limits_c = {k: requote_limits(envs[k], first_day, last_day, fees[k]) for k in ALL4}
    limits_e = {k: requote_limits(envs[k], first_day, last_day, fees[k], offset_s=0, period_s=3600, lookback_s=3600)
                for k in ALL4}
    qb = D.read_json(QUEUE_BOOK)
    out = {'window': [utc(first_ts), utc(last_ts)], 'days': n_days, 'size_usd': size, 'hurdle_bps': HURDLE,
           'staking_apr': W2['staking_apr_window'], 'venue_fee_bps': fees, 'sets': {}, 'late_entry_check': {}}
    for name, keys in sets:
        sub = {k: envs[k] for k in keys}
        res = {}
        r0, _ = Q.run_choice(sub, size, first_day, n_days)
        res['a0_taker_no_delay'] = dict(r0, in_sample_positive=(r0['in_sample_usd_per_year'] or 0) > 0)
        r1, _ = Q.run_choice(sub, size, first_day, n_days, delay_s=3600)
        rd, _ = Q.run_choice(sub, size, first_day, n_days, delay_s=86400)
        base = r0['out_of_sample_usd_per_year'] or 0.0
        res['a_taker_hourly'] = dict(r1, in_sample_positive=(r1['in_sample_usd_per_year'] or 0) > 0,
                                     late_1d_out_of_sample_usd_per_year=rd['out_of_sample_usd_per_year'],
                                     late_1d_kept_share_vs_no_delay=(rd['out_of_sample_usd_per_year'] or 0) / base if base else None)
        ref = qb['late_entry'].get('%s|%d|1h' % (name, size)) or {}
        out['late_entry_check'][name] = {'queue_book_1h_usd_per_year': ref.get('out_of_sample_usd_per_year'),
                                         'queue_book_1h_hurdle': ref.get('chosen_hurdle'), 'queue_book_1h_t': ref.get('oos_t'),
                                         'mine_1h_usd_per_year': r1['out_of_sample_usd_per_year'], 'mine_1h_hurdle': r1['chosen_hurdle'],
                                         'mine_1h_t': r1['oos_t'],
                                         'queue_book_no_delay_usd_per_year': qb['joint'][name][str(size)]['out_of_sample_usd_per_year'],
                                         'mine_no_delay_usd_per_year': r0['out_of_sample_usd_per_year']}
        log({'set': name, 'a0': round(base), 'a_1h': round(r1['out_of_sample_usd_per_year'] or 0)})
        var_b, fills_b = {}, {}
        for L in IMPL_LS:
            f, _ = simulate_levels(sub, size, [(1.0, lambda k, ts, c, L=L: L)])
            var_b['L=%g' % L], fills_b['L=%g' % L] = D.daily_values(f, first_day, n_days), f
        rb = oos_report(var_b, first_day, n_days, fills_b)
        Lc = float(rb['chosen'].split('=')[1])
        fl, _ = simulate_levels(sub, size, [(1.0, lambda k, ts, c: Lc)], delay_s=86400)
        late_b = oos_value(D.daily_values(fl, first_day, n_days), first_day, n_days)
        rb['late_1d_out_of_sample_usd_per_year'] = late_b
        rb['late_1d_kept_share'] = late_b / rb['out_of_sample_usd_per_year'] if rb['out_of_sample_usd_per_year'] else None
        res['b_fixed_limit'] = rb
        log({'set': name, 'b': rb['chosen'], 'oos': round(rb['out_of_sample_usd_per_year'] or 0)})

        def net_c(k, ts, carry):
            lim = limits_c[k].get(int((ts - 1800) // 86400))
            return None if lim is None else lim - carry - envs[k]['redemption_fee_bps']
        fc, _ = simulate_levels(sub, size, [(1.0, net_c)])
        rc = oos_report({'requote': D.daily_values(fc, first_day, n_days)}, first_day, n_days, {'requote': fc})
        days_c = [d for d in range(first_day, last_day + 1)]
        rc['days_market_term_above_floor_share'] = {
            k: sum(1 for d in days_c if limits_c[k][d] > HURDLE + envs[k]['wait'](d * 86400 + 1800) * envs[k]['carry'](d * 86400 + 1800)
                   + envs[k]['redemption_fee_bps'] + 1e-9) / len(days_c) for k in keys}
        rc['late_1d_kept_share'] = 'n/a: the limit is set from the previous day\'s market'
        res['c_daily_requote'] = rc
        log({'set': name, 'c_oos': round(rc['out_of_sample_usd_per_year'] or 0)})
        fd, std = simulate_levels(sub, size, [(0.5, lambda k, ts, c: Lc), (0.5, lambda k, ts, c: 2 * Lc)])
        rdl = oos_report({'L=%g|2L' % Lc: D.daily_values(fd, first_day, n_days)}, first_day, n_days, {'L=%g|2L' % Lc: fd})
        fdl, _ = simulate_levels(sub, size, [(0.5, lambda k, ts, c: Lc), (0.5, lambda k, ts, c: 2 * Lc)], delay_s=86400)
        late_d = oos_value(D.daily_values(fdl, first_day, n_days), first_day, n_days)
        rdl.update({'late_1d_out_of_sample_usd_per_year': late_d,
                    'late_1d_kept_share': late_d / rdl['out_of_sample_usd_per_year'] if rdl['out_of_sample_usd_per_year'] else None,
                    'filled_usd_by_level_full_window': std['by_level_filled_usd']})
        res['d_two_level_ladder'] = rdl
        log({'set': name, 'd_oos': round(rdl['out_of_sample_usd_per_year'] or 0)})

        def net_e(k, ts, carry):
            lim = limits_e[k].get(int(ts // 3600))
            return None if lim is None else lim - carry - envs[k]['redemption_fee_bps']
        fe, _ = simulate_levels(sub, size, [(1.0, net_e)])
        re_ = oos_report({'hourly requote': D.daily_values(fe, first_day, n_days)}, first_day, n_days, {'hourly requote': fe})
        re_['late_1d_kept_share'] = 'n/a: the limit is set from the previous hour\'s market'
        res['e_hourly_requote'] = re_
        log({'set': name, 'e_oos': round(re_['out_of_sample_usd_per_year'] or 0)})
        for delay, tag in (('hour', 'f_taker_next_hour'), ('day', 'g_taker_next_day')):
            for reading in LATER_READINGS:
                var, fl_by = {}, {}
                for h in D.HURDLES_BPS:
                    f, _ = simulate_later(sub, size, h, reading, delay, idx)
                    var['h=%g' % h], fl_by['h=%g' % h] = D.daily_values(f, first_day, n_days), f
                r = oos_report(var, first_day, n_days, fl_by)
                _, st = simulate_later(sub, size, float(r['chosen'].split('=')[1]), reading, delay, idx)
                r.update({'reading': LATER_READINGS[reading], 'delay': LATER_DELAYS[delay], 'stats_full_window': st,
                          'kept_share_vs_no_delay_taker': (r['out_of_sample_usd_per_year'] or 0) / base if base else None})
                res['%s|%s' % (tag, reading)] = r
                log({'set': name, tag: reading, 'oos': round(r['out_of_sample_usd_per_year'] or 0), 'h': r['chosen'],
                     'kept': round(r['kept_share_vs_no_delay_taker'] or 0, 3)})
        out['sets'][name] = res
    out['persistence'] = persistence_stats(envs, idx)
    out['persistence_note'] = ('sells whose own-hour edge (simulate_book\'s) cleared %gbp; share whose edge at the later price '
                               'still cleared it, by count and volume, all and deep (own edge > 10bp); full window' % HURDLE)
    out['queue_book_late_entry_kept'] = {k: v.get('kept_share') for k, v in qb['late_entry'].items() if '|%d|' % size in k}
    return out


def impl_table(out):
    L = ['## Implementation comparison (queue_book window %s to %s, split %s, $%gM, out of sample)' % (
        out['window'][0][:10], out['window'][1][:10], out['sets']['all4']['b_fixed_limit']['cutoff_utc'][:10], out['size_usd'] / 1e6), '',
         '| implementation | set | chosen | out of sample $/yr | t | 95% interval | in-sample positive | 1-day late kept |',
         '|---|---|---|---:|---:|---|---|---:|']
    names = [('a0_taker_no_delay', 'taker, no delay (the backtest)'), ('a_taker_hourly', '(a) taker checked hourly'),
             ('b_fixed_limit', '(b) one fixed resting limit'), ('c_daily_requote', '(c) daily re-quoted limit'),
             ('d_two_level_ladder', '(d) two-level ladder L / 2L'), ('e_hourly_requote', '(e) hourly re-quoted limit (added)')] + \
        [('%s|%s' % (t, r), '(%s) taker buying back %s, %s' % (t[0], 'at the next hour' if t[0] == 'f' else 'a day later', lbl))
         for t in ('f_taker_next_hour', 'g_taker_next_day')
         for r, lbl in (('median', 'later venue median'), ('first', 'first later trade'), ('lookback', 'study median, 6h carry'))]
    for key, label in names:
        for s in ('all4', 'eth3'):
            r = out['sets'][s][key]
            ci = r.get('oos_ci95_usd_per_year') or [None, None]
            kept = r.get('late_1d_kept_share') if key != 'a_taker_hourly' else r.get('late_1d_kept_share_vs_no_delay')
            if key.startswith(('f_', 'g_')):
                kept = r.get('kept_share_vs_no_delay_taker')
            L.append('| %s | %s | %s | %s | %s | %s – %s | %s | %s |' % (
                label, s, r.get('chosen') or r.get('chosen_hurdle'), fmt_usd(r['out_of_sample_usd_per_year']),
                '%.2f' % r['oos_t'] if r.get('oos_t') is not None else '—', fmt_usd(ci[0]), fmt_usd(ci[1]),
                'yes' if r.get('in_sample_positive') else 'no',
                '%.0f%%' % (100 * kept) if isinstance(kept, float) else ('—' if kept is None else 'n/a')))
    L += ['', '(b) out of sample by depth, all4: ' + ', '.join('%s %s' % (v, fmt_usd(x)) for v, x in
                                                          out['sets']['all4']['b_fixed_limit']['by_variant_oos_usd_per_year'].items()),
          '', 'For (f) and (g) the last column is the share of the no-delay taker kept (queue_book\'s late-entry test kept ' +
          ', '.join('%s %.0f%%' % (k.replace('|15000000|', ' '), 100 * v) for k, v in sorted((out.get('queue_book_late_entry_kept') or {}).items())
                    if v is not None) + ' while still filling each sell at its own price).']
    P = out.get('persistence')
    if P:
        L += ['', '### Does the discount persist? Sells that qualified in their own hour, still clearing %gbp at the later price' % HURDLE, '',
              '| asset | qualifying sells | next hour: venue median | next hour: first trade | next hour: missing | a day later: venue median | a day later: first trade | deep (>10bp) next hour / day, median |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        pc = lambda x: '—' if x is None else '%.0f%%' % (100 * x)
        for k, v in P.items():
            a1, f1, a24, f24 = v['hour|median']['all'], v['hour|first']['all'], v['day|median']['all'], v['day|first']['all']
            L.append('| %s | %d | %s (%s of $) | %s | %s | %s (%s of $) | %s | %s / %s |' % (
                k, a1['qualifying'], pc(a1['still_clear_share']), pc(a1['still_clear_usd_share']), pc(f1['still_clear_share']),
                pc(a1['later_missing_share']), pc(a24['still_clear_share']), pc(a24['still_clear_usd_share']), pc(f24['still_clear_share']),
                pc(v['hour|median']['deep']['still_clear_share']), pc(v['day|median']['deep']['still_clear_share'])))
    v = out.get('verdict')
    if v:
        L += ['', '**Book row should carry:** %s. %s' % (v['book_row_should_carry'], v['reason'])]
    return '\n'.join(L) + '\n'


def fmt_usd(v):
    return '—' if v is None else '$%s' % format(int(round(v)), ',')


def cmd_implementations(args):
    t0 = time.monotonic()
    W = build_world(window_days=800)
    out = implementation_comparison(W, log=lambda o: print(json.dumps(o), flush=True))
    out['generated'] = utc()
    out['verdict'] = impl_verdict(out)
    out['seconds'] = round(time.monotonic() - t0, 1)
    D.write_json(OUT / 'implementation.json', out)
    tab = impl_table(out)
    tp = OUT / 'tables.md'
    old = tp.read_text() if tp.exists() else '# queue_live tables\n\n'
    head = old.split('## Implementation comparison')[0].rstrip() + '\n\n'
    tp.write_text(head + tab)
    print(tab)
    print('wrote', (OUT / 'implementation.json').relative_to(ROOT), 'and', tp.relative_to(ROOT), '(%.0fs)' % out['seconds'])


def impl_verdict(out):
    """Which implementation the book row should carry, among the executable ones. Excluded as executed: (a), whose fills
    take every sell at its own price with the cap read from the sell's own hour (only a bidder behind each seller gets
    that), and the readings of (f)/(g) that use the study's 6h carry (a venue that has not traded keeps the seller's own
    print). Executable: the resting orders (b, c, d, e) and the taker buying back later (f, g) priced at the later
    venue median or the first later trade. The choice is the best on the ETH-only book (run first) under the more
    conservative of the two later-price readings, if positive in sample on both sets with t above 2; a daily-signed
    implementation is preferred unless it falls below the hourly choice's 95% interval."""
    S = out['sets']

    def row(k):
        a, e = S['all4'][k], S['eth3'][k]
        return {'implementation': k, 'all4_usd_per_year': a['out_of_sample_usd_per_year'], 'all4_t': a['oos_t'],
                'all4_ci95': a.get('oos_ci95_usd_per_year'), 'eth3_usd_per_year': e['out_of_sample_usd_per_year'],
                'eth3_t': e['oos_t'], 'eth3_ci95': e.get('oos_ci95_usd_per_year'),
                'in_sample_positive_both': bool(a.get('in_sample_positive')) and bool(e.get('in_sample_positive'))}
    keys = [k for k in S['all4'] if k != 'a0_taker_no_delay']
    rows = {k: row(k) for k in keys}
    ok = lambda r: r['in_sample_positive_both'] and (r['all4_t'] or 0) > 2 and (r['eth3_t'] or 0) > 2
    daily = [rows[k] for k in ('b_fixed_limit', 'c_daily_requote', 'd_two_level_ladder') if ok(rows[k])]
    best_daily = max(daily, key=lambda r: r['eth3_usd_per_year'] or 0) if daily else None
    hourly = []
    for t in ('f_taker_next_hour', 'g_taker_next_day'):
        cons = min((rows['%s|%s' % (t, r)] for r in ('median', 'first')), key=lambda r: r['eth3_usd_per_year'] or 0)
        if ok(cons):
            hourly.append(cons)
    if ok(rows['e_hourly_requote']):
        hourly.append(rows['e_hourly_requote'])
    best_hourly = max(hourly, key=lambda r: r['eth3_usd_per_year'] or 0) if hourly else None
    pick, why = best_daily, 'daily-signed and not significantly below the best hourly implementation'
    if best_hourly and best_daily and all((best_daily['%s_usd_per_year' % n] or 0) < (best_hourly['%s_ci95' % n] or [0])[0]
                                          for n in ('all4', 'eth3')):
        pick, why = best_hourly, ('the best daily-signed implementation (%s) falls below its 95%% interval on both sets'
                                  % best_daily['implementation'])
    elif best_hourly and not best_daily:
        pick, why = best_hourly, 'no daily-signed implementation passes'
    impl = pick['implementation'].split('|')[0] if pick else None
    reason = None
    if pick:
        reason = '%s: %s a year out of sample on all four (t %.2f) and %s on the ETH-only book (t %.2f); %s.' % (
            pick['implementation'], fmt_usd(pick['all4_usd_per_year']), pick['all4_t'], fmt_usd(pick['eth3_usd_per_year']),
            pick['eth3_t'], why)
        if impl in ('f_taker_next_hour', 'g_taker_next_day'):
            up = rows['%s|first' % impl] if pick['implementation'].endswith('median') else rows['%s|median' % impl]
            reason += (' The other later-price reading gives %s / %s. Persistence makes it work: of the sells that qualified '
                       'in their own hour, %s of stETH/wstETH and %s of weETH still cleared the hurdle at the next hour\'s '
                       'venue median; rsETH and LBTC lose most sells to quiet venues (no later price), not to recovery.' % (
                           fmt_usd(up['all4_usd_per_year']), fmt_usd(up['eth3_usd_per_year']),
                           '%.0f%%' % (100 * out['persistence']['lido']['hour|median']['all']['still_clear_share']),
                           '%.0f%%' % (100 * out['persistence']['etherfi_ev']['hour|median']['all']['still_clear_share'])))
    return {'ranked': sorted(rows.values(), key=lambda r: -(r['eth3_usd_per_year'] or 0)),
            'excluded_as_executed': {'a_taker_hourly': 'fills each sell at its own price, cap read from the sell\'s own hour',
                                     '*|lookback': 'the 6h carry keeps a quiet venue at the seller\'s own print'},
            'best_daily_signed': best_daily and best_daily['implementation'],
            'best_hourly': best_hourly and best_hourly['implementation'],
            'book_row_should_carry': impl, 'headline_reading': pick and pick['implementation'], 'reason': reason}


def cmd_register(args):
    p = quote_path(args.date or utc()[:10])
    if not p.exists():
        raise SystemExit('no ladder at %s' % p)
    row, msg = register(D.read_json(p), time.time(), LEDGER, p)
    print(msg, '' if row is None else row['registered_at'])


def cmd_score(args):
    rpc = live_rpc.RPC(log_path=SWAPS / 'rpc_errors.jsonl', max_credits=args.max_credits)
    W = build_world()
    rows = read_ledger(LEDGER)
    by_version = run_score(W, rows, rpc)
    last = sorted((OUT / 'monitor').glob('*.json'))
    crit = (D.read_json(last[-1]) or {}).get('criteria', {}) if last else {}
    res = write_paper(W, rows, by_version, crit, time.time())
    print(json.dumps({'paper_by_version': res['paper_by_version'], 'verdict': res['verdict'], 'status': res['status']},
                     indent=1, default=str)[:3000])


def cmd_daily(args):
    """quote (which collects), orders, then monitor (which registers today's ladder and scores). On a second run the
    same day the registered ladder and its orders stand; only the monitor runs."""
    log = Log(OUT / 'monitor.log')
    rpc = live_rpc.RPC(log_path=SWAPS / 'rpc_errors.jsonl', max_credits=args.max_credits)
    today = utc()[:10]
    if any(r['date'] == today for r in read_ledger(LEDGER)):
        log({'daily': 'today already registered; quote and orders skipped'})
    else:
        cmd_quote(args, rpc, log)
        cmd_orders(argparse.Namespace(date=today, owner=args.owner, pool_eth=None))
        args.no_collect = True                  # the quote has just collected to the finalized head
    cmd_monitor(args, rpc, log)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('quote', 'orders', 'monitor', 'register', 'score', 'daily', 'implementations'):
        s = sub.add_parser(name)
        s.add_argument('--max-credits', type=int, default=3_000_000)
        if name in ('quote', 'daily'):
            s.add_argument('--pool-eth', type=float, default=DEFAULT_POOL_ETH, help='the pool every order is sized to (WETH)')
            s.add_argument('--no-collect', action='store_true', help='quote from what is already collected')
        if name in ('orders', 'daily'):
            s.add_argument('--owner', help='the signer (and receiver); default a zero-address placeholder')
        if name == 'orders':
            s.add_argument('--pool-eth', type=float, help='default: the ladder\'s pool')
        if name in ('orders', 'register'):
            s.add_argument('--date', help='UTC date of the ladder (default today)')
        if name in ('monitor', 'daily'):
            s.add_argument('--no-register', action='store_true', help='do not register today\'s ladder')
        if name == 'monitor':
            s.add_argument('--no-collect', action='store_true')
    args = p.parse_args()
    if args.cmd == 'daily':
        args.date = None
    {'quote': cmd_quote, 'orders': cmd_orders, 'monitor': cmd_monitor, 'register': cmd_register, 'score': cmd_score,
     'daily': cmd_daily, 'implementations': cmd_implementations}[args.cmd](args)


if __name__ == '__main__':
    main()
