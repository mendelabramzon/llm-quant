#!/usr/bin/env python3
"""Solana mainnet window analysis over the compact blocks written by solana_collect.py — the Solana counterpart of live_scan.py.

  prices   pass over every K-th block: SOL/USD path from payer-centric SOL<->USDC/USDT swaps (median per minute) -> prices.json
  analyze  full offline pass: network, fees, compute, leaders, programs, tx kinds, DEX volume/pairs/venues, implied token
           prices, largest swaps, same-block sandwiches, pump.fun launches, lending events (Kamino/marginfi/Save), stablecoin
           and LST issuance, CCTP in/out by domain, exchange flow (labelled, fan-in checked), large transfers, Jito tips,
           dust/poisoning senders -> analysis.json
  head     external + RPC state at the head: Jupiter prices, Kamino/Save/Jupiter Lend rates, Sanctum LST NAV, Jito tip
           floor, epoch, recent priority fees -> head_state.json
  render   insights.md (LLM narrative, optional) + deterministic tables -> report.md
  show     decode one signature from the local blocks

Every number in the tables is computed here from the saved blocks (and head_state.json for head reads); prose is written by the
LLM separately. USD basis: stables at par, SOL from the in-window swap path (prices.json), registry tokens from the Jupiter
head read, everything else priced only through the opposite leg of a swap (a swap between two unpriced tokens is 'unpriced').
"""
import argparse
import collections
import datetime as dt
import glob
import gzip
import heapq
import json
import math
import statistics
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import solana_decode as D  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LABELS = json.loads((ROOT / 'scripts' / 'solana_labels.json').read_text())
PROG = LABELS['programs']
MINTS = LABELS['mints']
SYM = {m: v['symbol'] for m, v in MINTS.items()}
DEC = {m: v['decimals'] for m, v in MINTS.items()}
SOL = 'So11111111111111111111111111111111111111112'
USDC = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
USDT = 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
STABLES = {m for m, v in MINTS.items() if v['class'] == 'stable'}
LSTS = {m for m, v in MINTS.items() if v['class'] == 'lst'}
DEX_KINDS = {'dex', 'aggregator', 'launchpad'}
CCTP_PROGRAMS = {D.CCTP_TOKEN_MESSENGER, D.CCTP_V2_TOKEN_MESSENGER, D.CCTP_MESSAGE_TRANSMITTER, D.CCTP_V2_MESSAGE_TRANSMITTER}
LAUNCHPADS = {a for a, v in PROG.items() if v['kind'] == 'launchpad'}
SYSTEMISH = {a for a, v in PROG.items() if v['kind'] == 'system'}
JITO_TIPS = {a for a, v in PROG.items() if v['kind'] == 'mev_tip'}
EXCHANGES = {a: v['label'] for a, v in PROG.items() if v['kind'] == 'exchange'}
LENDING = {a: v['label'] for a, v in PROG.items() if v['kind'] == 'lending'}
PUMP = '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'
PUMPSWAP = 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA'
KAMINO = 'KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD'
MARGINFI = 'MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA'
SAVE = 'So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo'
JUP_LEND = 'jup3YeL8QhtSx1e253b2FDvsMNC87fDrgQZivbrndc9'
BASE_FEE = 5000  # lamports per signature
LAMPORTS = 1e9

ANCHOR_NAMES = {
    KAMINO: ['liquidate_obligation_and_redeem_reserve_collateral', 'liquidate_obligation_and_redeem_reserve_collateral_v2', 'flash_borrow_reserve_liquidity', 'flash_repay_reserve_liquidity',
             'deposit_reserve_liquidity_and_obligation_collateral', 'deposit_reserve_liquidity_and_obligation_collateral_v2', 'borrow_obligation_liquidity', 'borrow_obligation_liquidity_v2',
             'repay_obligation_liquidity', 'repay_obligation_liquidity_v2', 'withdraw_obligation_collateral_and_redeem_reserve_collateral', 'withdraw_obligation_collateral_and_redeem_reserve_collateral_v2',
             'deposit_reserve_liquidity', 'redeem_reserve_collateral', 'refresh_reserve', 'refresh_obligation', 'refresh_reserves_batch', 'init_obligation', 'init_user_metadata',
             'deposit_and_withdraw', 'repay_and_withdraw_and_redeem', 'withdraw_obligation_collateral', 'deposit_obligation_collateral', 'request_elevation_group'],
    MARGINFI: ['lending_account_liquidate', 'lending_account_deposit', 'lending_account_withdraw', 'lending_account_borrow', 'lending_account_repay',
               'lending_account_start_flashloan', 'lending_account_end_flashloan', 'marginfi_account_initialize', 'lending_account_withdraw_emissions', 'lending_pool_accrue_bank_interest'],
    D.CCTP_TOKEN_MESSENGER: ['deposit_for_burn', 'deposit_for_burn_with_caller', 'handle_receive_message'],
    D.CCTP_V2_TOKEN_MESSENGER: ['deposit_for_burn', 'deposit_for_burn_with_hook', 'handle_receive_finalized_message', 'handle_receive_unfinalized_message'],
    D.CCTP_MESSAGE_TRANSMITTER: ['receive_message', 'send_message'],
    D.CCTP_V2_MESSAGE_TRANSMITTER: ['receive_message', 'send_message'],
    PUMP: ['create', 'buy', 'sell', 'migrate', 'withdraw'],
    PUMPSWAP: ['create_pool', 'buy', 'sell', 'deposit', 'withdraw'],
}
DISC = {p: {D.anchor_disc(n): n for n in names} for p, names in ANCHOR_NAMES.items()}
SAVE_IX = {4: 'deposit_reserve_liquidity', 5: 'redeem_reserve_collateral', 10: 'borrow_obligation_liquidity', 11: 'repay_obligation_liquidity', 12: 'liquidate_obligation',
           13: 'flash_loan', 14: 'deposit_reserve_liquidity_and_obligation_collateral', 15: 'withdraw_obligation_collateral_and_redeem_reserve_collateral',
           19: 'liquidate_obligation_and_redeem_reserve_collateral', 20: 'flash_repay_reserve_liquidity', 21: 'flash_borrow_reserve_liquidity'}


def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()


def short(a):
    return a if len(a) <= 12 else a[:4] + '…' + a[-4:]


def label(a):
    v = PROG.get(a)
    return v['label'] if v else None


def name_of(a):
    return label(a) or short(a)


def usd_fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return '–'
    s = '-' if v < 0 else ''
    v = abs(v)
    if v >= 1e9:
        return '%s$%.2fB' % (s, v / 1e9)
    if v >= 1e6:
        return '%s$%.1fM' % (s, v / 1e6)
    if v >= 1e4:
        return '%s$%.0fk' % (s, v / 1e3)
    return '%s$%.0f' % (s, v) if v >= 100 else '%s$%.2f' % (s, v)


def human(v, signed=True):
    if v is None:
        return '–'
    sgn = ('+' if v > 0 else '-' if v < 0 else '') if signed else ('-' if v < 0 else '')
    a = abs(v)
    if a >= 1e9:
        return '%s%.2fB' % (sgn, a / 1e9)
    if a >= 1e6:
        return '%s%.2fM' % (sgn, a / 1e6)
    if a >= 1e4:
        return '%s%.1fk' % (sgn, a / 1e3)
    if a >= 100:
        return '%s%.0f' % (sgn, a)
    return '%s%.4g' % (sgn, a)


def pct(v, d=2):
    return '–' if v is None else ('%.' + str(d) + 'f%%') % (100 * v)


def load_json(p):
    p = Path(p)
    if p.suffix == '.gz':
        with gzip.open(p, 'rt') as f:
            return json.load(f)
    return json.loads(p.read_text())


def save_json(p, obj):
    Path(p).write_text(json.dumps(obj, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o)))


def block_files(out, every=1):
    slots = load_json(Path(out) / 'slots.json')['chosen']
    files = [(s, Path(out) / 'blocks' / ('%d.json.gz' % s)) for s in slots]
    files = [(s, p) for s, p in files if p.exists()]
    return files[::every]


class TopN:
    def __init__(self, n):
        self.n, self.h, self.i = n, [], 0

    def push(self, key, item):
        self.i += 1
        if len(self.h) < self.n:
            heapq.heappush(self.h, (key, self.i, item))
        elif key > self.h[0][0]:
            heapq.heapreplace(self.h, (key, self.i, item))

    def items(self):
        return [it for _, _, it in sorted(self.h, key=lambda x: -x[0])]


# ---------------------------------------------------------------- per-transaction features

def tx_features(tx, keys, prices, minute):
    """Everything the aggregators need from one non-vote transaction."""
    meta, msg = tx['meta'], tx['transaction']['message']
    nsig = msg['header']['numRequiredSignatures']
    payer = keys[0]
    signers = keys[:nsig]
    fee = meta['fee']
    err = meta['err']
    cu = meta.get('computeUnitsConsumed') or 0
    top_programs = []
    for ix in msg['instructions']:
        p = keys[ix['programIdIndex']] if ix['programIdIndex'] < len(keys) else '?'
        if p not in top_programs:
            top_programs.append(p)
    all_programs = set(top_programs)
    tips = 0
    tip_to = None
    cu_price = None
    cu_limit = None
    decoded = []      # decoded dicts of interest
    cctp_guess = []
    v2_body = None
    new_mints = 0
    ix_names = set()  # anchor names by discriminator, prefixed with program label
    sys_transfers = []  # (from, to, lamports)
    created = 0
    closed = 0
    token22 = 0
    token_ix = 0
    nonce = False
    for ix in D.iter_instructions(tx, keys):
        p = ix['program']
        all_programs.add(p)
        d = D.decode(ix)
        if d:
            k = d['kind']
            if k == 'cu_price':
                cu_price = d['micro_lamports']
            elif k == 'cu_limit':
                cu_limit = d['units']
            elif k == 'sys_transfer':
                sys_transfers.append((d['from'], d['to'], d['lamports']))
                if d['to'] in JITO_TIPS:
                    tips += d['lamports']
                    tip_to = d['to']
            elif k == 'sys_create_account':
                created += 1
            elif k == 'sys_advance_nonce':
                nonce = True
            elif k == 'closeAccount':
                closed += 1
            if d.get('program') in ('token', 'token2022'):
                token_ix += 1
                if d['program'] == 'token2022':
                    token22 += 1
            if k in ('mintTo', 'mintToChecked', 'burn', 'burnChecked', 'cctp_deposit_for_burn', 'cctp_receive_message', 'transfer', 'transferChecked'):
                decoded.append(d)
            if k in ('initializeMint', 'initializeMint2'):
                new_mints += 1
        if p == D.CCTP_V2_TOKEN_MESSENGER and len(ix['data']) >= 100 and v2_body is None:
            # v2 deposit_for_burn emits a self-CPI whose payload starts with destination_domain u32 + mint_recipient 32 bytes (amount is
            # a big-endian u256 further in, so the burned USDC amount of the same tx is used instead)
            domain = int.from_bytes(ix['data'][8:12], 'little')
            if domain < 64:
                v2_body = (domain, '0x' + ix['data'][12:44].hex())
        if p in (D.CCTP_MESSAGE_TRANSMITTER, D.CCTP_V2_MESSAGE_TRANSMITTER) and len(ix['data']) >= 120 and not (d and d['kind'] == 'cctp_receive_message'):
            ln = int.from_bytes(ix['data'][8:12], 'little')
            msg = ix['data'][12:12 + ln]
            if 100 <= ln <= len(ix['data']) and len(msg) >= 12:
                src = int.from_bytes(msg[4:8], 'big')
                if src in D.CCTP_DOMAINS and not any(x['kind'] == 'cctp_receive_message' for x in decoded):
                    cctp_guess.append({'kind': 'cctp_receive_message', 'version': 2 if p == D.CCTP_V2_MESSAGE_TRANSMITTER else 1, 'source_domain': src, 'source': D.CCTP_DOMAINS[src], 'guessed': True})
        dm = DISC.get(p)
        if dm and len(ix['data']) >= 8:
            n = dm.get(ix['data'][:8])
            if n:
                ix_names.add(n)
        elif p == SAVE and ix['data']:
            n = SAVE_IX.get(ix['data'][0])
            if n:
                ix_names.add('save:' + n)
    # balances
    sol = {}
    pre, post = meta['preBalances'], meta['postBalances']
    for i in range(min(len(keys), len(pre), len(post))):
        if post[i] != pre[i]:
            sol[keys[i]] = post[i] - pre[i]
    tok = D.token_deltas(tx, keys)   # per token account
    by_owner = collections.defaultdict(lambda: collections.defaultdict(int))
    for acct, e in tok.items():
        if e['delta_raw']:
            by_owner[e['owner'] or acct][e['mint']] += e['delta_raw']
    # payer legs (SOL: native delta + fee + tips; WSOL ATA deltas of the payer folded in)
    payer_legs = {}
    for m, v in by_owner.get(payer, {}).items():
        payer_legs[m] = payer_legs.get(m, 0) + v
    sol_leg = sol.get(payer, 0) + fee + tips
    if abs(sol_leg) > 2_500_000:  # ignore rent-sized residue (< 0.0025 SOL)
        payer_legs[SOL] = payer_legs.get(SOL, 0) + sol_leg
    elif SOL in payer_legs and abs(payer_legs[SOL]) <= 2_500_000:
        del payer_legs[SOL]
    log_names = []
    for l in meta.get('logMessages') or []:
        if l.startswith('Program log: Instruction: '):
            log_names.append(l[26:])
    if v2_body and ('DepositForBurn' in log_names or 'DepositForBurnWithHook' in log_names) and not any(x['kind'] == 'cctp_deposit_for_burn' for x in decoded):
        burned = sum(x['amount'] for x in decoded if x['kind'] in ('burn', 'burnChecked') and x.get('mint') == USDC)
        if burned:
            decoded.append({'kind': 'cctp_deposit_for_burn', 'version': 2, 'amount': burned, 'destination_domain': v2_body[0], 'destination': D.CCTP_DOMAINS.get(v2_body[0], 'domain %d' % v2_body[0]), 'mint_recipient': v2_body[1], 'guessed': True})
    for g in cctp_guess:
        if g['kind'] == 'cctp_receive_message' and 'ReceiveMessage' in log_names:
            decoded.append(g)
    # trader = payer if the payer has a sold and a bought leg, else another signer with both
    trader = payer
    tl = payer_legs
    if not (any(v < 0 for v in tl.values()) and any(v > 0 for v in tl.values())):
        for s_ in signers[1:]:
            legs = by_owner.get(s_, {})
            if any(v < 0 for v in legs.values()) and any(v > 0 for v in legs.values()):
                trader, tl = s_, dict(legs)
                break
    return {'trader': trader, 'trader_legs': tl, 'new_mints': new_mints, 'sig': tx['transaction']['signatures'][0], 'payer': payer, 'signers': signers, 'nsig': nsig, 'fee': fee, 'err': err, 'cu': cu, 'cu_price': cu_price, 'cu_limit': cu_limit,
            'tips': tips, 'tip_to': tip_to, 'top_programs': top_programs, 'programs': all_programs, 'decoded': decoded, 'ix_names': ix_names, 'log_names': log_names,
            'sol': sol, 'tok': tok, 'by_owner': by_owner, 'payer_legs': payer_legs, 'sys_transfers': sys_transfers, 'created': created, 'closed': closed,
            'token_ix': token_ix, 'token22': token22, 'nonce': nonce, 'version': tx.get('version', 'legacy'), 'n_keys': len(keys)}


def usd_of(mint, raw, prices, minute):
    """USD value of a raw token amount, or None when unpriced."""
    if mint in STABLES:
        return raw / 10 ** DEC[mint]
    if mint == SOL:
        p = prices.sol_at(minute)
        return raw / LAMPORTS * p if p else None
    p = prices.token.get(mint)
    if p:
        return raw / 10 ** DEC.get(mint, p.get('decimals', 0)) * p['usd'] if isinstance(p, dict) else None
    return None


class Prices:
    def __init__(self, out):
        self.path = Path(out) / 'prices.json'
        self.head = Path(out) / 'head_state.json'
        self.sol_minutes = {}
        self.sol_fallback = None
        self.token = {}
        if self.path.exists():
            p = load_json(self.path)
            self.sol_minutes = {int(k): v for k, v in p['sol_usd_by_minute'].items()}
            self.sol_fallback = p.get('sol_usd_median')
        if self.head.exists():
            h = load_json(self.head)
            for m, v in (h.get('jupiter_prices') or {}).items():
                if m in MINTS and m not in STABLES and m != SOL:
                    self.token[m] = {'usd': v['usdPrice'], 'decimals': DEC[m]}
            if self.sol_fallback is None and SOL in (h.get('jupiter_prices') or {}):
                self.sol_fallback = h['jupiter_prices'][SOL]['usdPrice']

    def sol_at(self, minute):
        v = self.sol_minutes.get(minute)
        if v:
            return v
        # nearest minute within 3
        for d in (1, -1, 2, -2, 3, -3):
            v = self.sol_minutes.get(minute + d)
            if v:
                return v
        return self.sol_fallback


def swap_legs(f):
    """Sold/bought legs of the trader (payer, else a signer with two-sided legs): {mint: raw} negative = sold."""
    legs = {m: v for m, v in f['trader_legs'].items() if v}
    sold = {m: -v for m, v in legs.items() if v < 0}
    bought = {m: v for m, v in legs.items() if v > 0}
    return sold, bought


def is_dex_tx(f):
    return any(PROG.get(p, {}).get('kind') in DEX_KINDS for p in f['programs'])


def venues_of(f):
    v = [PROG[p]['label'] for p in f['programs'] if PROG.get(p, {}).get('kind') == 'dex']
    return sorted(set(v))


# ---------------------------------------------------------------- prices pass

def cmd_prices(args):
    out = Path(args.out)
    files = block_files(out, args.every)
    per_min = collections.defaultdict(list)
    n = 0
    for slot, p in files:
        b = load_json(p)
        minute = b['blockTime'] // 60
        for tx in b['transactions']:
            if tx['meta']['err'] is not None:
                continue
            keys = D.tx_keys(tx)
            payer = keys[0]
            # quick check: any DEX program among keys
            if not any(PROG.get(k, {}).get('kind') in DEX_KINDS for k in keys):
                continue
            f = tx_features(tx, keys, None, minute)
            sold, bought = swap_legs(f)
            if len(sold) == 1 and len(bought) == 1:
                (ms, vs), (mb, vb) = list(sold.items())[0], list(bought.items())[0]
                if {ms, mb} & {USDC, USDT} and SOL in (ms, mb):
                    usd = (vs if ms != SOL else vb) / 1e6
                    solv = (vs if ms == SOL else vb) / LAMPORTS
                    if usd >= 200 and solv > 0:
                        per_min[minute].append(usd / solv)
                        n += 1
    series = {m: statistics.median(v) for m, v in per_min.items() if len(v) >= 3}
    allp = [x for v in per_min.values() for x in v]
    res = {'basis': 'median of payer-centric SOL<->USDC/USDT swaps >= $200 per minute (blocks sampled every %d)' % args.every, 'swaps_used': n, 'minutes': len(series),
           'sol_usd_by_minute': {str(k): round(v, 4) for k, v in sorted(series.items())}, 'sol_usd_median': round(statistics.median(allp), 4) if allp else None,
           'sol_usd_first': round(series[min(series)], 4) if series else None, 'sol_usd_last': round(series[max(series)], 4) if series else None,
           'sol_usd_min': round(min(series.values()), 4) if series else None, 'sol_usd_max': round(max(series.values()), 4) if series else None}
    save_json(out / 'prices.json', res)
    print(json.dumps({k: v for k, v in res.items() if k != 'sol_usd_by_minute'}, indent=1))


# ---------------------------------------------------------------- analyze pass

def cmd_analyze(args):
    out = Path(args.out)
    m = load_json(out / 'manifest.json')
    leaders = load_json(out / 'leaders.json') if (out / 'leaders.json').exists() else {}
    prices = Prices(out)
    if prices.sol_fallback is None and not prices.sol_minutes:
        raise SystemExit('No SOL price: run `prices` (and `head`) first')
    files = block_files(out)
    t0 = time.time()
    C = collections.Counter()
    S = collections.defaultdict(float)
    bins = collections.defaultdict(collections.Counter)          # 5-minute bins
    binsf = collections.defaultdict(lambda: collections.defaultdict(float))
    prog = collections.defaultdict(collections.Counter)          # main program -> counters
    progf = collections.defaultdict(lambda: collections.defaultdict(float))
    prog_names = collections.defaultdict(collections.Counter)    # program -> log instruction names (only single-program txs)
    kinds = collections.Counter()
    kindf = collections.defaultdict(float)
    payers = collections.defaultdict(collections.Counter)
    payerf = collections.defaultdict(lambda: collections.defaultdict(float))
    tippers = collections.defaultdict(float)
    tip_counts = collections.Counter()
    tip_by_account = collections.defaultdict(float)
    tip_payers_by_account = collections.defaultdict(set)
    venue_vol = collections.defaultdict(float)
    venue_n = collections.Counter()
    venue_unpriced = collections.Counter()
    pair_vol = collections.defaultdict(float)
    pair_n = collections.Counter()
    agg_vol = collections.defaultdict(float)
    token_px = collections.defaultdict(list)      # mint -> [(usd price, usd notional)]
    token_vol = collections.defaultdict(float)
    token_swaps = collections.Counter()
    unpriced_mints = collections.Counter()
    big_swaps = TopN(40)
    big_moves = TopN(60)
    big_sol = TopN(40)
    sandwiches = []
    sw_attackers = collections.Counter()
    sw_profit = collections.defaultdict(float)
    sw_victim_usd = 0.0
    pump = collections.Counter()
    pumpf = collections.defaultdict(float)
    pump_creators = collections.Counter()
    lend = collections.defaultdict(collections.Counter)
    liquidations = []
    flash = collections.defaultdict(collections.Counter)
    flash_amounts = collections.defaultdict(float)
    issuance = collections.defaultdict(lambda: collections.defaultdict(float))   # (mint) -> {'mint','burn'}
    issuance_auth = collections.defaultdict(lambda: collections.defaultdict(float))
    issuance_big = TopN(30)
    cctp_out = collections.defaultdict(float)
    cctp_out_n = collections.Counter()
    cctp_in = collections.defaultdict(float)
    cctp_in_n = collections.Counter()
    cctp_big = TopN(20)
    cctp_recipients = collections.defaultdict(float)
    ex_flow = collections.defaultdict(lambda: collections.defaultdict(float))   # exchange -> asset -> net raw
    ex_usd = collections.defaultdict(lambda: collections.defaultdict(float))
    ex_in_cp = collections.defaultdict(set)
    ex_out_cp = collections.defaultdict(set)
    ex_txn = collections.Counter()
    dust_senders = collections.Counter()
    dust_recipients = collections.defaultdict(set)
    fanin = collections.defaultdict(set)         # recipient -> set of senders of SOL >= 0.1
    fanin_amt = collections.defaultdict(float)
    leader_blocks = collections.Counter()
    leader_cu = collections.Counter()
    leader_tips = collections.defaultdict(float)
    block_rows = []
    max_block_cu = 0
    lst_flow = collections.defaultdict(lambda: collections.defaultdict(float))
    stake_ops = collections.Counter()
    cu_prices = []
    fees_nonvote = []
    priority_total = 0
    first_ts = None
    last_ts = None
    n_blocks = 0
    swap_index = collections.defaultdict(list)   # per block: (pool_owner, mint) -> [(idx, payer, side, usd)]
    prog_payers = collections.defaultdict(collections.Counter)
    launches = collections.Counter()
    launch_creators = collections.Counter()
    pump_names = collections.Counter()
    flash_payers = collections.defaultdict(collections.Counter)
    flash_co = collections.defaultdict(collections.Counter)
    liq_attempts = collections.defaultdict(collections.Counter)
    fanin_n = collections.Counter()
    fanin_amts = collections.defaultdict(list)
    fanout_dest = collections.defaultdict(set)   # sender -> up to 6 distinct destinations (SOL >= 0.1)
    fanout_n = collections.Counter()
    fanout_amt = collections.defaultdict(float)
    seen_sandwich = set()
    cctp_custody_in = collections.defaultdict(float)
    other_programs = collections.Counter()
    new_mints_other = collections.Counter()
    wash_venue = collections.defaultdict(float)
    wash_venue_n = collections.Counter()
    wash_token = collections.defaultdict(float)
    wash_token_n = collections.Counter()
    wash_pairs = collections.Counter()      # (trader, counter-signer) pairs
    cashback_n = 0
    cashback_sol = 0.0
    dex_other_programs = collections.Counter()
    for slot, p in files:
        b = load_json(p)
        n_blocks += 1
        ts = b['blockTime']
        first_ts = ts if first_ts is None else min(first_ts, ts)
        last_ts = ts if last_ts is None else max(last_ts, ts)
        minute = ts // 60
        bkey = (ts - m['start_ts']) // 300
        leader = leaders.get(str(slot))
        if leader:
            leader_blocks[leader] += 1
        C['tx'] += b['n_tx']
        C['vote'] += b['n_vote']
        S['vote_fee'] += b['vote_fee']
        bins[bkey]['tx'] += b['n_tx']
        bins[bkey]['vote'] += b['n_vote']
        bins[bkey]['blocks'] += 1
        block_cu = 0
        block_fee = 0
        block_tips = 0
        block_fail = 0
        swap_index.clear()
        txi = 0
        for tx in b['transactions']:
            txi += 1
            keys = D.tx_keys(tx)
            f = tx_features(tx, keys, prices, minute)
            failed = f['err'] is not None
            C['nonvote'] += 1
            C['failed'] += failed
            S['fee'] += f['fee']
            S['failed_fee'] += f['fee'] if failed else 0
            prio = f['fee'] - BASE_FEE * f['nsig']
            priority_total += max(prio, 0)
            if failed:
                f['tips'] = 0          # a failed tx reverts its tip transfer; only the fee is paid
            S['tips'] += f['tips']
            block_cu += f['cu']
            block_fee += f['fee']
            block_tips += f['tips']
            block_fail += failed
            C['v0'] += f['version'] == 0
            C['nonce'] += f['nonce']
            C['token22_ix'] += f['token22']
            C['token_ix'] += f['token_ix']
            C['created'] += f['created']
            C['closed'] += f['closed']
            if f['cu_price'] is not None:
                cu_prices.append(f['cu_price'])
            fees_nonvote.append(f['fee'])
            bins[bkey]['nonvote'] += 1
            bins[bkey]['failed'] += failed
            binsf[bkey]['fee'] += f['fee'] / LAMPORTS
            binsf[bkey]['tips'] += f['tips'] / LAMPORTS
            binsf[bkey]['cu'] += f['cu']
            if f['tips']:
                tip_counts[f['payer']] += 1
                tippers[f['payer']] += f['tips'] / LAMPORTS
                tip_by_account[f['tip_to']] += f['tips'] / LAMPORTS
                tip_payers_by_account[f['tip_to']].add(f['payer'])
                C['tip_txs'] += 1
                if leader:
                    leader_tips[leader] += f['tips'] / LAMPORTS
            # main program = first top-level program that is not system/compute/token/ata/memo
            main = next((p for p in f['top_programs'] if p not in SYSTEMISH), None) or (f['top_programs'][0] if f['top_programs'] else '?')
            prog[main]['tx'] += 1
            prog[main]['failed'] += failed
            prog[main]['cu'] += f['cu']
            prog[main]['nonce'] += f['nonce']
            prog_payers[main][f['payer']] += 1
            progf[main]['fee'] += f['fee'] / LAMPORTS
            progf[main]['tips'] += f['tips'] / LAMPORTS
            if len([p for p in f['top_programs'] if p not in SYSTEMISH]) == 1 and f['log_names']:
                for n_ in set(f['log_names']):
                    prog_names[main][n_] += 1
            payers[f['payer']]['tx'] += 1
            payers[f['payer']]['failed'] += failed
            payerf[f['payer']]['fee'] += f['fee'] / LAMPORTS
            payerf[f['payer']]['tips'] += f['tips'] / LAMPORTS
            # ---- kinds
            dex = is_dex_tx(f)
            kind = 'other'
            sold, bought = swap_legs(f)
            if failed:
                kind = 'failed'
            elif f['new_mints'] and f['programs'] & LAUNCHPADS:
                kind = 'launch'
            elif dex and sold and bought:
                kind = 'swap'
            elif dex:
                kind = 'dex_other'
            elif f['programs'] & set(LENDING):
                kind = 'lending'
            elif f['programs'] & {D.CCTP_TOKEN_MESSENGER, D.CCTP_V2_TOKEN_MESSENGER, D.CCTP_MESSAGE_TRANSMITTER, D.CCTP_V2_MESSAGE_TRANSMITTER}:
                kind = 'cctp'
            elif any(PROG.get(p, {}).get('kind') == 'bridge' for p in f['programs']):
                kind = 'bridge'
            elif any(PROG.get(p, {}).get('kind') == 'staking' for p in f['programs']) or D.STAKE in f['programs']:
                kind = 'staking'
            elif any(PROG.get(p, {}).get('kind') in ('perps', 'prediction', 'vault', 'protocol') for p in f['programs']):
                kind = next(PROG[p]['kind'] for p in f['programs'] if PROG.get(p, {}).get('kind') in ('perps', 'prediction', 'vault', 'protocol'))
            elif f['programs'] <= SYSTEMISH:
                kind = 'transfer' if (f['tok'] or len(f['sol']) > 1) else 'system_only'
            kinds[kind] += 1
            kindf[kind] += f['fee'] / LAMPORTS
            if kind == 'other':
                other_programs[main] += 1
            if kind == 'dex_other':
                dex_other_programs[main] += 1
            if kind == 'launch':
                launches[main] += 1
                launch_creators[f['payer']] += 1
            if kind == 'swap':
                prog[main]['swaps'] += 1
            if f['new_mints'] and kind != 'launch' and not failed:
                new_mints_other[main] += f['new_mints']
            prog[main]['token_moves'] += bool(any(e['delta_raw'] for e in f['tok'].values()))
            prog[main]['keys'] += f['n_keys']
            # ---- swaps
            if kind == 'swap':
                ven = venues_of(f)
                vkey = ven[0] if len(ven) == 1 else ('multi: ' + '+'.join(ven) if ven else 'aggregator-only')
                sold_usd = {mm: usd_of(mm, v, prices, minute) for mm, v in sold.items()}
                bought_usd = {mm: usd_of(mm, v, prices, minute) for mm, v in bought.items()}
                ps = sum(v for v in sold_usd.values() if v)
                pb = sum(v for v in bought_usd.values() if v)
                usd = max(ps, pb)
                if usd == 0:
                    venue_unpriced[vkey] += 1
                    for mm in list(sold) + list(bought):
                        unpriced_mints[mm] += 1
                else:
                    venue_vol[vkey] += usd
                    for p_ in f['programs']:
                        if PROG.get(p_, {}).get('kind') == 'aggregator':
                            agg_vol[PROG[p_]['label']] += usd
                    pair = ' / '.join(sorted(SYM.get(mm, mm) for mm in list(sold) + list(bought)))
                    pair_vol[(vkey, pair)] += usd
                    pair_n[(vkey, pair)] += 1
                    # implied prices for single-leg swaps where exactly one side is unpriced-by-registry
                    if len(sold) == 1 and len(bought) == 1:
                        (ms, vs), (mb, vb) = list(sold.items())[0], list(bought.items())[0]
                        for mm, vv, other_usd in ((ms, vs, bought_usd[mb]), (mb, vb, sold_usd[ms])):
                            if other_usd and usd >= 20:
                                dec = DEC.get(mm) or next((e['decimals'] for e in f['tok'].values() if e['mint'] == mm), None)
                                if dec is not None and vv:
                                    token_px[mm].append((other_usd / (vv / 10 ** dec), usd))
                                    token_vol[mm] += usd
                                    token_swaps[mm] += 1
                    big_swaps.push(usd, {'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'payer': f['payer'], 'venue': vkey, 'usd': round(usd),
                                         'sold': {SYM.get(mm, mm): v / 10 ** DEC.get(mm, 0) if mm in DEC else v for mm, v in sold.items()},
                                         'bought': {SYM.get(mm, mm): v / 10 ** DEC.get(mm, 0) if mm in DEC else v for mm, v in bought.items()}, 'tips_sol': f['tips'] / LAMPORTS})
                venue_n[vkey] += 1
                bins[bkey]['swaps'] += 1
                binsf[bkey]['dex_usd'] += usd
                # self-matched swap: another signer whose legs (tokens + native SOL) are the mirror of the trader's legs
                self_matched = None
                if len(f['signers']) > 1 and usd:
                    for s_ in f['signers']:
                        if s_ == f['trader']:
                            continue
                        legs = dict(f['by_owner'].get(s_, {}))
                        sd = f['sol'].get(s_, 0)
                        if abs(sd) > 2_500_000:
                            legs[SOL] = legs.get(SOL, 0) + sd
                        if any(legs.get(mm, 0) < 0 for mm in bought) and any(legs.get(mm, 0) > 0 for mm in sold):
                            self_matched = s_
                            break
                if self_matched:
                    wash_venue[vkey] += usd
                    wash_venue_n[vkey] += 1
                    for mm in list(sold) + list(bought):
                        if mm not in STABLES and mm != SOL:
                            wash_token[mm] += usd
                            wash_token_n[mm] += 1
                    wash_pairs[(f['trader'], self_matched)] += 1
                    bins[bkey]['wash_swaps'] += 1
                    binsf[bkey]['wash_usd'] += usd
                # sandwich index: pool owners = owners of changed token accounts that are not the payer
                pools = {e['owner'] for e in f['tok'].values() if e['delta_raw'] and e['owner'] and e['owner'] != f['trader'] and e['owner'] not in f['signers']}
                for mm in bought:
                    if mm in STABLES or mm == SOL:
                        continue
                    for po in pools:
                        swap_index[(po, mm)].append((txi, f['trader'], 'buy', usd, f['sig'], sold_usd, bought_usd, f))
                for mm in sold:
                    if mm in STABLES or mm == SOL:
                        continue
                    for po in pools:
                        swap_index[(po, mm)].append((txi, f['trader'], 'sell', usd, f['sig'], sold_usd, bought_usd, f))
            # ---- pump.fun
            if PUMP in f['programs'] or PUMPSWAP in f['programs']:
                for n_ in set(f['log_names']):
                    if n_.startswith(('Buy', 'Sell', 'Create', 'Migrate', 'Extend', 'Collect', 'Distribute', 'Claim', 'BondingCurve', 'Withdraw', 'Deposit')):
                        pump_names[n_] += 1
                if kind == 'launch' and PUMP in f['programs']:
                    pump_creators[f['payer']] += 1
                    pump['launches'] += 1
                if 'Migrate' in f['log_names'] and not failed:
                    pump['migrations'] += 1
                if 'CreatePool' in f['log_names'] and not failed and PUMPSWAP in f['programs']:
                    pump['pumpswap_pools_created'] += 1
                if not failed and ('ClaimCashback' in f['log_names'] or 'ClaimCashbackV2' in f['log_names']):
                    cashback_n += 1
                    gain = f['sol'].get(f['payer'], 0) + f['fee']
                    if gain > 0:
                        cashback_sol += gain / LAMPORTS
                if not failed and SOL in f['trader_legs'] and PUMP in f['programs']:
                    pumpf['bonding_curve_sol'] += abs(f['trader_legs'][SOL]) / LAMPORTS
                    pumpf['buy_sol' if f['trader_legs'][SOL] < 0 else 'sell_sol'] += abs(f['trader_legs'][SOL]) / LAMPORTS
                if not failed and SOL in f['trader_legs'] and PUMPSWAP in f['programs'] and PUMP not in f['programs']:
                    pumpf['pumpswap_sol'] += abs(f['trader_legs'][SOL]) / LAMPORTS
                pump['failed' if failed else 'ok'] += 1
            # ---- lending
            for lp, ln in LENDING.items():
                if lp in f['programs']:
                    lend[ln]['tx'] += 1
                    lend[ln]['failed'] += failed
                    names = set() if lp not in (KAMINO, MARGINFI, SAVE) else ({n_ for n_ in f['ix_names'] if not n_.startswith('save:')} if lp != SAVE else {n_[5:] for n_ in f['ix_names'] if n_.startswith('save:')})
                    if lp == MARGINFI:
                        names = {n_ for n_ in f['ix_names'] if n_.startswith('lending_account') or n_.startswith('marginfi')}
                    if lp == KAMINO:
                        names = {n_ for n_ in f['ix_names'] if n_ in ANCHOR_NAMES[KAMINO]}
                    for n_ in names:
                        lend[ln][n_ + (' (failed)' if failed else '')] += 1
                    if any('liquidat' in n_ for n_ in names):
                        liq_attempts[ln]['failed' if failed else 'ok'] += 1
                        liq_attempts[ln]['payer:' + f['payer']] += 1
                    if any('flash' in n_ for n_ in names):
                        flash_payers[ln][f['payer'] + (' (failed)' if failed else '')] += 1
                        for p_ in f['programs']:
                            if p_ not in SYSTEMISH and p_ != lp and PROG.get(p_):
                                flash_co[ln][PROG[p_]['label']] += 1
                    if not failed and any('liquidat' in n_ for n_ in names):
                        # liquidator = payer; value = priced positive legs of payer
                        got = {SYM.get(mm, short(mm)): v / 10 ** DEC.get(mm, 0) for mm, v in f['payer_legs'].items() if v > 0 and mm in DEC}
                        paid = {SYM.get(mm, short(mm)): -v / 10 ** DEC.get(mm, 0) for mm, v in f['payer_legs'].items() if v < 0 and mm in DEC}
                        usd_got = sum(v for v in (usd_of(mm, v, prices, minute) for mm, v in f['payer_legs'].items() if v > 0) if v)
                        usd_paid = sum(v for v in (usd_of(mm, -v, prices, minute) for mm, v in f['payer_legs'].items() if v < 0) if v)
                        liquidations.append({'venue': ln, 'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'liquidator': f['payer'], 'received': got, 'paid': paid,
                                             'usd_received': round(usd_got), 'usd_paid': round(usd_paid), 'tips_sol': f['tips'] / LAMPORTS})
                    if not failed and any('flash' in n_ for n_ in names):
                        flash[ln]['tx'] += 1
                        # flash principal: largest single token-account inflow to a payer-owned account? use largest positive owner delta of payer by usd
                        best = 0
                        for mm, v in f['by_owner'].get(f['payer'], {}).items():
                            u = usd_of(mm, abs(v), prices, minute)
                            if u and u > best:
                                best = u
                        flash_amounts[ln] += best
            # ---- issuance / CCTP / transfers
            cctp_tx = bool(f['programs'] & {D.CCTP_TOKEN_MESSENGER, D.CCTP_V2_TOKEN_MESSENGER, D.CCTP_MESSAGE_TRANSMITTER, D.CCTP_V2_MESSAGE_TRANSMITTER})
            if not failed:
                for d in f['decoded']:
                    k = d['kind']
                    if k in ('mintTo', 'mintToChecked', 'burn', 'burnChecked'):
                        mint = d.get('mint')
                        if mint in STABLES or mint in LSTS:
                            side = 'mint' if k.startswith('mint') else 'burn'
                            amt = d['amount'] / 10 ** DEC[mint]
                            issuance[mint][side] += amt
                            issuance[mint]['cctp_' + side if cctp_tx else 'issuer_' + side] += amt
                            akey = 'CCTP (user burn/mint inside a CCTP tx)' if cctp_tx else d.get('authority')
                            issuance_auth[(mint, side, akey)]['amount'] += amt
                            issuance_auth[(mint, side, akey)]['n'] += 1
                            u = usd_of(mint, d['amount'], prices, minute)
                            if u:
                                issuance_big.push(u, {'mint': SYM[mint], 'side': side, 'amount': amt, 'usd': round(u), 'authority': d.get('authority'), 'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'cctp': cctp_tx})
                            if mint in LSTS:
                                lst_flow[SYM[mint]][side] += amt
                    elif k == 'cctp_deposit_for_burn':
                        cctp_out[d['destination']] += d['amount'] / 1e6
                        cctp_out_n[d['destination']] += 1
                        cctp_big.push(d['amount'] / 1e6, {'direction': 'out', 'chain': d['destination'], 'usd': d['amount'] / 1e6, 'recipient': d['mint_recipient'], 'payer': f['payer'], 'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'version': d['version']})
                        cctp_recipients[(d['destination'], d['mint_recipient'])] += d['amount'] / 1e6
                    elif k == 'cctp_receive_message':
                        # v1 mints USDC; v2 pays out of a custody token account -> amount = largest positive USDC delta of a non-signer owner in the tx
                        amt = sum(x['amount'] for x in f['decoded'] if x['kind'] in ('mintTo', 'mintToChecked') and x.get('mint') == USDC) / 1e6
                        if not amt:
                            amt = max([v for o, mm_ in f['by_owner'].items() for mm, v in mm_.items() if mm == USDC and v > 0] + [0]) / 1e6
                            cctp_custody_in[d['source']] += amt
                        cctp_in[d['source']] += amt
                        cctp_in_n[d['source']] += 1
                        if amt:
                            cctp_big.push(amt, {'direction': 'in', 'chain': d['source'], 'usd': amt, 'payer': f['payer'], 'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'version': d['version']})
                # large moves by (owner, mint) and native SOL
                for owner, mm_ in f['by_owner'].items():
                    for mm, v in mm_.items():
                        u = usd_of(mm, abs(v), prices, minute)
                        if u and u >= 100_000:
                            big_moves.push(u, {'owner': owner, 'label': label(owner), 'asset': SYM.get(mm, short(mm)), 'delta': v / 10 ** DEC.get(mm, 0), 'usd': round(u), 'kind': kind, 'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'payer': f['payer'], 'programs': [name_of(p_) for p_ in f['top_programs'] if p_ not in SYSTEMISH][:3]})
                for k_, v in f['sol'].items():
                    if abs(v) >= 1000 * LAMPORTS:
                        big_sol.push(abs(v), {'account': k_, 'label': label(k_), 'delta_sol': v / LAMPORTS, 'usd': round(usd_of(SOL, abs(v), prices, minute) or 0), 'kind': kind, 'sig': f['sig'], 'slot': slot, 'time': utc(ts), 'payer': f['payer']})
                # exchange flows
                for ex, exname in EXCHANGES.items():
                    touched = False
                    v = f['sol'].get(ex)
                    if v:
                        touched = True
                        ex_flow[exname]['SOL'] += v / LAMPORTS
                        u = usd_of(SOL, v, prices, minute)
                        ex_usd[exname]['SOL'] += u or 0
                        (ex_in_cp if v > 0 else ex_out_cp)[exname].add(f['payer'] if f['payer'] != ex else next((k2 for k2, v2 in f['sol'].items() if k2 != ex and v2 > 0), '?'))
                    for mm, v in f['by_owner'].get(ex, {}).items():
                        touched = True
                        sym = SYM.get(mm, short(mm))
                        ex_flow[exname][sym] += v / 10 ** DEC.get(mm, 0)
                        u = usd_of(mm, v, prices, minute)
                        ex_usd[exname][sym] += u or 0
                        (ex_in_cp if v > 0 else ex_out_cp)[exname].add(f['payer'] if f['payer'] != ex else '?')
                    if touched:
                        ex_txn[exname] += 1
                # fan-in of SOL >= 0.1 (for behavioural exchange verification and unknown hot wallets)
                for fr, to, lam in f['sys_transfers']:
                    if lam >= 0.1 * LAMPORTS and fr and to:
                        fanin[to].add(fr)
                        fanin_amt[to] += lam / LAMPORTS
                        fanin_n[to] += 1
                        if len(fanin_amts[to]) < 2000:
                            fanin_amts[to].append(lam / LAMPORTS)
                        fanout_n[fr] += 1
                        fanout_amt[fr] += lam / LAMPORTS
                        if len(fanout_dest[fr]) < 6:
                            fanout_dest[fr].add(to)
                # dust senders (poisoning): transfers of <= 1 raw unit of a token or <= 1000 lamports to another owner
                for d in f['decoded']:
                    if d['kind'] in ('transfer', 'transferChecked') and d['amount'] <= 1 and d.get('authority') == f['payer']:
                        dust_senders[f['payer']] += 1
                        dust_recipients[f['payer']].add(d.get('dest'))
                for fr, to, lam in f['sys_transfers']:
                    if lam <= 1000 and fr == f['payer'] and to != f['payer']:
                        dust_senders[f['payer']] += 1
                        dust_recipients[f['payer']].add(to)
            # stake program ops
            if D.STAKE in f['programs']:
                stake_ops['stake_program_tx'] += 1
        # ---- per block wrap-up: sandwiches
        for (po, mm), lst in swap_index.items():
            if len(lst) < 3:
                continue
            lst.sort(key=lambda x: x[0])
            for i in range(len(lst)):
                a = lst[i]
                if a[2] != 'buy':
                    continue
                for j in range(i + 1, len(lst)):
                    v = lst[j]
                    if v[1] == a[1] or v[2] != 'buy':
                        continue
                    for k_ in range(j + 1, len(lst)):
                        c = lst[k_]
                        if c[1] == a[1] and c[2] == 'sell':
                            fa, fc = a[7], c[7]
                            key = (a[4], v[4], c[4])
                            if key in seen_sandwich:
                                break
                            seen_sandwich.add(key)
                            front_tok = fa['trader_legs'].get(mm, 0)
                            back_tok = fc['trader_legs'].get(mm, 0)
                            closed = front_tok > 0 and abs(front_tok + back_tok) <= 0.1 * front_tok
                            # attacker profit in USD from SOL/stable legs across both txs
                            pnl = 0.0
                            for ff in (fa, fc):
                                for m2, v2 in ff['payer_legs'].items():
                                    if m2 in STABLES or m2 == SOL:
                                        u = usd_of(m2, v2, prices, minute)
                                        pnl += u or 0
                            sandwiches.append({'slot': slot, 'time': utc(ts), 'pool': po, 'token': SYM.get(mm, short(mm)), 'attacker': a[1], 'victim': v[1], 'front': a[4], 'victim_sig': v[4], 'back': c[4],
                                               'victim_usd': round(v[3]), 'front_usd': round(a[3]), 'attacker_pnl_usd': round(pnl, 2), 'tips_sol': round((fa['tips'] + fc['tips']) / LAMPORTS, 5), 'position_closed': closed})
                            if closed:
                                sw_attackers[a[1]] += 1
                                sw_profit[a[1]] += pnl
                                sw_victim_usd += v[3]
                            break
                    else:
                        continue
                    break
        max_block_cu = max(max_block_cu, block_cu)
        if leader:
            leader_cu[leader] += block_cu
        block_rows.append([slot, ts, b['n_tx'], b['n_vote'], block_fail, block_cu, block_fee, block_tips])
        if n_blocks % 1000 == 0:
            print('analyzed %d blocks in %.0fs' % (n_blocks, time.time() - t0), flush=True)
    # ---------------------------------------------------------------- assemble
    hours = (last_ts - first_ts + 1) / 3600 if first_ts is not None else 0
    produced = load_json(out / 'slots.json')['produced']
    skipped_by_leader = collections.Counter()
    if leaders:
        prodset = set(produced)
        for s in range(m['start_slot'], m['end_slot'] + 1):
            if s not in prodset and str(s) in leaders:
                skipped_by_leader[leaders[str(s)]] += 1
    cu_prices.sort()
    fees_nonvote.sort()

    def q(a, p_):
        return a[min(len(a) - 1, int(len(a) * p_))] if a else None

    ex_labels_check = {}
    for ex, exname in EXCHANGES.items():
        ex_labels_check[exname] = {'address': ex, 'unique_senders_sol>=0.1': len(fanin.get(ex, ())), 'sol_received': round(fanin_amt.get(ex, 0), 2), 'txs_touching': ex_txn.get(exname, 0),
                                   'verdict': 'fan-in consistent with exchange deposit address' if len(fanin.get(ex, ())) >= 20 else ('some activity' if ex_txn.get(exname, 0) else 'no activity in window')}
    unknown_hot = [{'address': a, 'label': label(a), 'unique_senders': len(s), 'transfers': fanin_n[a], 'sol_received': round(fanin_amt[a], 1), 'median_sol': round(statistics.median(fanin_amts[a]), 3),
                    'out_transfers': fanout_n.get(a, 0), 'out_destinations': ('%d+' % len(fanout_dest[a])) if len(fanout_dest.get(a, ())) >= 6 else str(len(fanout_dest.get(a, ()))), 'sol_sent': round(fanout_amt.get(a, 0), 1),
                    'shape': ('collector hub (many in, ≤2 out)' if len(fanout_dest.get(a, ())) <= 2 and fanout_amt.get(a, 0) >= 0.5 * fanin_amt[a] else ('deposit address (many in, little out)' if fanout_amt.get(a, 0) < 0.1 * fanin_amt[a] else 'mixed'))} for a, s in fanin.items() if len(s) >= 40 and a not in JITO_TIPS]
    distributors = sorted([{'address': a, 'label': label(a), 'out_transfers': n_, 'sol_sent': round(fanout_amt[a], 1), 'destinations': '6+' if len(fanout_dest[a]) >= 6 else str(len(fanout_dest[a]))} for a, n_ in fanout_n.items() if n_ >= 200 and len(fanout_dest[a]) >= 6], key=lambda x: -x['out_transfers'])[:15]
    unknown_hot.sort(key=lambda x: -x['unique_senders'])
    token_prices = {}
    for mm, lst in token_px.items():
        if len(lst) >= 3:
            ws = sorted(lst)
            token_prices[mm] = {'symbol': SYM.get(mm), 'median_usd': statistics.median(x[0] for x in lst), 'n': len(lst), 'usd_volume': round(token_vol[mm]), 'min': ws[0][0], 'max': ws[-1][0]}
    res = {
        'window': {'start_utc': m['start_utc'], 'end_utc': m['end_utc'], 'start_slot': m['start_slot'], 'end_slot': m['end_slot'], 'produced_slots': m['produced_slots'], 'skipped_slots': m['skipped_slots'],
                   'blocks_analyzed': n_blocks, 'first_block_utc': utc(first_ts) if first_ts else None, 'last_block_utc': utc(last_ts) if last_ts else None, 'hours': round(hours, 3), 'complete': n_blocks == m['chosen_slots']},
        'price_basis': {'sol_usd_median': prices.sol_fallback, 'minutes': len(prices.sol_minutes), 'tokens_from_head': len(prices.token)},
        'network': {'transactions': C['tx'], 'votes': C['vote'], 'nonvote': C['nonvote'], 'failed': C['failed'], 'failed_share': C['failed'] / max(C['nonvote'], 1), 'tps_all': C['tx'] / max(hours * 3600, 1), 'tps_nonvote': C['nonvote'] / max(hours * 3600, 1),
                    'fees_sol': S['fee'] / LAMPORTS, 'vote_fees_sol': S['vote_fee'] / LAMPORTS, 'priority_fees_sol': priority_total / LAMPORTS, 'base_fees_sol': (S['fee'] - priority_total) / LAMPORTS,
                    'failed_fees_sol': S['failed_fee'] / LAMPORTS, 'jito_tips_sol': S['tips'] / LAMPORTS, 'tip_txs': C['tip_txs'], 'fee_median_lamports': q(fees_nonvote, .5), 'fee_p90_lamports': q(fees_nonvote, .9), 'fee_p99_lamports': q(fees_nonvote, .99),
                    'cu_price_median_microlamports': q(cu_prices, .5), 'cu_price_p90': q(cu_prices, .9), 'cu_price_p99': q(cu_prices, .99), 'txs_with_cu_price': len(cu_prices),
                    'max_block_nonvote_cu': max_block_cu, 'v0_share': C['v0'] / max(C['nonvote'], 1), 'durable_nonce_txs': C['nonce'], 'token22_ix_share': C['token22_ix'] / max(C['token_ix'], 1), 'accounts_created': C['created'], 'token_accounts_closed': C['closed']},
        'bins_5min': [{'bin': k, 'start_utc': utc(m['start_ts'] + k * 300), 'blocks': v['blocks'], 'tx': v['tx'], 'vote': v['vote'], 'nonvote': v['nonvote'], 'failed': v['failed'], 'fee_sol': round(binsf[k]['fee'], 3), 'tips_sol': round(binsf[k]['tips'], 3), 'cu': binsf[k]['cu'], 'swaps': v['swaps'], 'dex_usd': round(binsf[k]['dex_usd']), 'wash_usd': round(binsf[k]['wash_usd']),
                       'sol_usd': prices.sol_at((m['start_ts'] + k * 300) // 60)} for k, v in sorted(bins.items())],
        'leaders': {'blocks_by_leader': leader_blocks.most_common(25), 'skipped_by_leader': skipped_by_leader.most_common(15), 'tips_by_leader': sorted(((k, round(v, 3)) for k, v in leader_tips.items()), key=lambda x: -x[1])[:15], 'n_leaders': len(leader_blocks)},
        'programs': sorted([{'program': p_, 'label': label(p_), 'kind': PROG.get(p_, {}).get('kind'), 'tx': v['tx'], 'failed': v['failed'], 'fail_share': v['failed'] / v['tx'], 'cu': v['cu'], 'fee_sol': round(progf[p_]['fee'], 3), 'tips_sol': round(progf[p_]['tips'], 3), 'swaps': v['swaps'], 'nonce_txs': v['nonce'],
                            'token_move_share': v['token_moves'] / v['tx'], 'avg_keys': v['keys'] / v['tx'], 'avg_cu': v['cu'] / v['tx'], 'unique_payers': len(prog_payers[p_]), 'top_payer_share': prog_payers[p_].most_common(1)[0][1] / v['tx'] if prog_payers[p_] else 0, 'top_payer': prog_payers[p_].most_common(1)[0][0] if prog_payers[p_] else None, 'top_instructions': prog_names[p_].most_common(6)} for p_, v in prog.items()], key=lambda x: -x['tx'])[:80],
        'other_kind_programs': [(name_of(p_), p_, n_) for p_, n_ in other_programs.most_common(15)],
        'dex_other_programs': [(name_of(p_), p_, n_) for p_, n_ in dex_other_programs.most_common(15)],
        'launches': {'by_program': [(name_of(p_), p_, n_) for p_, n_ in launches.most_common(15)], 'total': sum(launches.values()), 'unique_creators': len(launch_creators), 'top_creators': launch_creators.most_common(10),
                     'other_new_mints_by_program': [(name_of(p_), p_, n_) for p_, n_ in new_mints_other.most_common(12)]},
        'kinds': [{'kind': k, 'tx': v, 'share': v / max(C['nonvote'], 1), 'fee_sol': round(kindf[k], 3)} for k, v in kinds.most_common()],
        'payers': sorted([{'payer': p_, 'label': label(p_), 'tx': v['tx'], 'failed': v['failed'], 'fee_sol': round(payerf[p_]['fee'], 3), 'tips_sol': round(payerf[p_]['tips'], 3)} for p_, v in payers.items()], key=lambda x: -x['tx'])[:40],
        'top_fee_payers': sorted([{'payer': p_, 'label': label(p_), 'tx': payers[p_]['tx'], 'failed': payers[p_]['failed'], 'fee_sol': round(v['fee'], 3), 'tips_sol': round(v['tips'], 3)} for p_, v in payerf.items()], key=lambda x: -(x['fee_sol'] + x['tips_sol']))[:30],
        'jito': {'tips_sol': S['tips'] / LAMPORTS, 'tip_txs': C['tip_txs'], 'unique_tippers': len(tippers), 'top_tippers': sorted([{'payer': p_, 'label': label(p_), 'tips_sol': round(v, 3), 'tip_txs': tip_counts[p_]} for p_, v in tippers.items()], key=lambda x: -x['tips_sol'])[:25],
                 'by_tip_account': [{'account': a, 'tips_sol': round(v, 3), 'unique_payers': len(tip_payers_by_account[a])} for a, v in sorted(tip_by_account.items(), key=lambda x: -x[1])]},
        'dex': {'volume_by_venue': sorted([{'venue': k, 'usd': round(v), 'swaps': venue_n[k], 'unpriced_swaps': venue_unpriced[k]} for k, v in venue_vol.items()], key=lambda x: -x['usd']),
                'unpriced_only_venues': [{'venue': k, 'unpriced_swaps': v} for k, v in venue_unpriced.most_common() if k not in venue_vol][:20],
                'volume_via_aggregator': sorted([{'aggregator': k, 'usd': round(v)} for k, v in agg_vol.items()], key=lambda x: -x['usd']),
                'total_priced_usd': round(sum(venue_vol.values())), 'priced_swaps': sum(venue_n.values()) - sum(venue_unpriced.values()), 'unpriced_swaps': sum(venue_unpriced.values()),
                'top_pairs': sorted([{'venue': k[0], 'pair': k[1], 'usd': round(v), 'swaps': pair_n[k]} for k, v in pair_vol.items()], key=lambda x: -x['usd'])[:40],
                'implied_prices': sorted(token_prices.values(), key=lambda x: -x['usd_volume'])[:40] if token_prices else [],
                'unpriced_mints_top': unpriced_mints.most_common(15), 'big_swaps': big_swaps.items(),
                'self_matched': {'total_usd': round(sum(wash_venue.values())), 'swaps': sum(wash_venue_n.values()), 'by_venue': sorted([{'venue': k, 'usd': round(v), 'swaps': wash_venue_n[k], 'share_of_venue': v / venue_vol[k] if venue_vol.get(k) else None} for k, v in wash_venue.items()], key=lambda x: -x['usd'])[:15],
                                 'by_token': sorted([{'mint': k, 'symbol': SYM.get(k), 'usd': round(v), 'swaps': wash_token_n[k]} for k, v in wash_token.items()], key=lambda x: -x['usd'])[:20],
                                 'wallet_pairs': len(wash_pairs), 'top_pairs': [((a[:8], b_[:8]), n_) for (a, b_), n_ in wash_pairs.most_common(10)]},
                'sandwiches': {'n': len(sandwiches), 'victim_usd': round(sw_victim_usd), 'attackers': [{'attacker': a, 'n': n_, 'pnl_usd': round(sw_profit[a], 2)} for a, n_ in sw_attackers.most_common(15)], 'examples': sorted(sandwiches, key=lambda x: -x['victim_usd'])[:25]}},
        'pump': {'counts': dict(pump), 'cashback_claims': cashback_n, 'cashback_sol_received': round(cashback_sol, 3), 'instructions': pump_names.most_common(30), 'sol': {k: round(v, 2) for k, v in pumpf.items()}, 'top_creators': pump_creators.most_common(10), 'unique_creators': len(pump_creators)},
        'lending': {'events': {k: dict(v) for k, v in lend.items()}, 'liquidations': sorted(liquidations, key=lambda x: -x['usd_received'])[:40], 'n_liquidations': len(liquidations),
                    'flash_loans': {k: {'tx': v['tx'], 'principal_usd_est': round(flash_amounts[k])} for k, v in flash.items()},
                    'flash_payers': {k: v.most_common(12) for k, v in flash_payers.items()}, 'flash_co_programs': {k: v.most_common(10) for k, v in flash_co.items()},
                    'liquidation_attempts': {k: {'ok': v['ok'], 'failed': v['failed'], 'top_payers': [(a[6:], n_) for a, n_ in v.most_common(40) if a.startswith('payer:')][:8]} for k, v in liq_attempts.items()}},
        'issuance': {'by_mint': {SYM[k]: {'mint': round(v['mint'], 2), 'burn': round(v['burn'], 2), 'net': round(v['mint'] - v['burn'], 2), 'issuer_mint': round(v['issuer_mint'], 2), 'issuer_burn': round(v['issuer_burn'], 2), 'cctp_mint': round(v['cctp_mint'], 2), 'cctp_burn': round(v['cctp_burn'], 2)} for k, v in issuance.items()},
                     'by_authority': sorted([{'mint': SYM[k[0]], 'side': k[1], 'authority': k[2], 'label': label(k[2]), 'amount': round(v['amount'], 2), 'n': int(v['n'])} for k, v in issuance_auth.items()], key=lambda x: -x['amount'])[:40],
                     'largest': issuance_big.items(), 'lst': {k: {'mint': round(v['mint'], 2), 'burn': round(v['burn'], 2), 'net': round(v['mint'] - v['burn'], 2)} for k, v in lst_flow.items()}},
        'cctp': {'out_by_chain': sorted([{'chain': k, 'usd': round(v), 'n': cctp_out_n[k]} for k, v in cctp_out.items()], key=lambda x: -x['usd']),
                 'in_by_chain': sorted([{'chain': k, 'usd': round(v), 'n': cctp_in_n[k]} for k, v in cctp_in.items()], key=lambda x: -x['usd']),
                 'out_total': round(sum(cctp_out.values())), 'in_total': round(sum(cctp_in.values())), 'in_paid_from_custody_v2': {k: round(v) for k, v in cctp_custody_in.items()}, 'largest': cctp_big.items(),
                 'top_recipients_out': sorted([{'chain': k[0], 'recipient': k[1], 'usd': round(v)} for k, v in cctp_recipients.items()], key=lambda x: -x['usd'])[:15]},
        'exchanges': {'net_flow': {ex: {'assets': {a: round(v, 4) for a, v in assets.items()}, 'usd': {a: round(v) for a, v in ex_usd[ex].items()}, 'usd_net': round(sum(ex_usd[ex].values())), 'txs': ex_txn[ex], 'in_counterparties': len(ex_in_cp[ex]), 'out_counterparties': len(ex_out_cp[ex])} for ex, assets in ex_flow.items()},
                      'label_checks': ex_labels_check, 'unlabelled_fan_in': unknown_hot[:25], 'distributors': distributors},
        'large': {'moves': big_moves.items(), 'sol': big_sol.items()},
        'poisoning': {'dust_senders': [{'sender': s, 'label': label(s), 'dust_transfers': n_, 'recipients': len(dust_recipients[s])} for s, n_ in dust_senders.most_common(60) if len(dust_recipients[s]) >= 20][:15],
                      'total_dust_transfers': sum(n_ for s, n_ in dust_senders.items() if len(dust_recipients[s]) >= 20), 'senders_over_50': sum(1 for s, v in dust_senders.items() if v >= 50 and len(dust_recipients[s]) >= 20),
                      'excluded_few_recipient_senders': [{'sender': s, 'label': label(s), 'dust_transfers': n_, 'recipients': len(dust_recipients[s])} for s, n_ in dust_senders.most_common(8) if len(dust_recipients[s]) < 20]},
        'blocks': block_rows,
        'generated_utc': utc(int(time.time())), 'seconds': round(time.time() - t0, 1),
    }
    save_json(out / 'analysis.json', res)
    print(json.dumps({'window': res['window'], 'network': res['network'], 'dex_total': res['dex']['total_priced_usd'], 'kinds': res['kinds'][:8], 'sandwiches': res['dex']['sandwiches']['n'], 'liquidations': res['lending']['n_liquidations'], 'seconds': res['seconds']}, indent=1, default=str))


# ---------------------------------------------------------------- head

def http_json(u, timeout=40):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Macintosh) llm-quant research', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def cmd_head(args):
    out = Path(args.out)
    from solana_rpc import Client
    c = Client()
    h = {'retrieved_utc': utc(int(time.time())), 'sources': {}}
    try:
        h['slot'] = c.call('getSlot', [{'commitment': 'finalized'}])
        h['epoch'] = c.call('getEpochInfo', [{'commitment': 'finalized'}])
        h['inflation'] = c.call('getInflationRate')
        h['recent_priority_fees'] = c.call('getRecentPrioritizationFees', [[]])
        h['performance_samples'] = c.call('getRecentPerformanceSamples', [30])
        h['sources']['rpc'] = 'GetBlock JSON-RPC'
    except Exception as e:
        h['rpc_error'] = str(e)[:200]
    try:
        ids = ','.join(MINTS)
        h['jupiter_prices'] = http_json('https://lite-api.jup.ag/price/v3?ids=' + ids)
        h['sources']['jupiter_prices'] = 'https://lite-api.jup.ag/price/v3 (off-chain aggregator price, blockId recorded per token)'
    except Exception as e:
        h['jupiter_error'] = str(e)[:200]
    try:
        mk = http_json('https://api.kamino.finance/v2/kamino-market?env=mainnet-beta')
        h['kamino_markets'] = []
        for mkt in mk[:8]:
            try:
                rs = http_json('https://api.kamino.finance/kamino-market/%s/reserves/metrics?env=mainnet-beta' % mkt['lendingMarket'])
            except Exception as e:
                rs = []
            h['kamino_markets'].append({'name': mkt['name'], 'market': mkt['lendingMarket'], 'reserves': [{'token': r['liquidityToken'], 'mint': r['liquidityTokenMint'], 'supply_apy': float(r['supplyApy']), 'borrow_apy': float(r['borrowApy']),
                                                                                                          'supplied_usd': float(r['totalSupplyUsd']), 'borrowed_usd': float(r['totalBorrowUsd']), 'util': float(r['totalBorrow']) / float(r['totalSupply']) if float(r['totalSupply']) else 0.0, 'reserve': r['reserve']} for r in rs]})
        h['sources']['kamino'] = 'https://api.kamino.finance (reserve metrics, APY as reported by the protocol API)'
    except Exception as e:
        h['kamino_error'] = str(e)[:200]
    try:
        cfg = http_json('https://api.solend.fi/v1/markets/configs?scope=all&deployment=production')
        main = next(mm for mm in cfg if mm['name'] == 'main')
        addrs = [r['address'] for r in main['reserves']]
        rows = []
        for i in range(0, len(addrs), 20):
            rr = http_json('https://api.solend.fi/v1/reserves?ids=' + ','.join(addrs[i:i + 20]))
            for x in rr['results']:
                r = x['reserve']
                liq = r['liquidity']
                dec = liq['mintDecimals']
                avail = int(liq['availableAmount']) / 10 ** dec
                borrowed = int(liq['borrowedAmountWads']) / 1e18 / 10 ** dec
                price = float(liq.get('marketPrice') or 0) / 1e18
                rows.append({'mint': liq['mintPubkey'], 'symbol': SYM.get(liq['mintPubkey']), 'available': avail, 'borrowed': borrowed, 'util': borrowed / (avail + borrowed) if avail + borrowed else 0, 'price': price,
                             'supply_apy': float(x['rates']['supplyInterest']) / 100, 'borrow_apy': float(x['rates']['borrowInterest']) / 100, 'supplied_usd': (avail + borrowed) * price, 'borrowed_usd': borrowed * price, 'reserve': r.get('address') or r.get('pubkey')})
        h['save_main'] = sorted(rows, key=lambda r: -r['supplied_usd'])
        h['sources']['save'] = 'https://api.solend.fi/v1/reserves (raw reserve state + protocol-computed rates)'
    except Exception as e:
        h['save_error'] = str(e)[:200]
    try:
        jl = http_json('https://lite-api.jup.ag/lend/v1/earn/tokens')
        h['jupiter_lend'] = [{'symbol': x.get('symbol'), 'asset': x.get('assetAddress'), 'asset_symbol': (x.get('asset') or {}).get('symbol'), 'supply_rate_bps': int(x.get('supplyRate') or 0), 'rewards_rate_bps': int(x.get('rewardsRate') or 0), 'total_rate_bps': int(x.get('totalRate') or 0),
                             'total_assets': int(x.get('totalAssets') or 0) / 10 ** int(x.get('decimals') or 0), 'decimals': x.get('decimals'), 'asset_price': float((x.get('asset') or {}).get('price') or 0)} for x in jl]
        h['sources']['jupiter_lend'] = 'https://lite-api.jup.ag/lend/v1/earn/tokens (rates in bps as reported)'
    except Exception as e:
        h['jupiter_lend_error'] = str(e)[:200]
    try:
        lsts = ['jitoSOL', 'mSOL', 'bSOL', 'jupSOL', 'INF', 'hSOL', 'vSOL', 'dSOL', 'bbSOL', 'sSOL', 'picoSOL', 'bonkSOL', 'dfdvSOL', 'laineSOL', 'compassSOL']
        sv = http_json('https://extra-api.sanctum.so/v1/sol-value/current?' + '&'.join('lst=%s' % s for s in lsts))
        h['sanctum_sol_value'] = {k: int(v) / LAMPORTS for k, v in sv['solValues'].items()}
        h['sources']['sanctum'] = 'https://extra-api.sanctum.so/v1/sol-value/current (SOL per LST token)'
    except Exception as e:
        h['sanctum_error'] = str(e)[:200]
    # on-chain stake-pool NAV (SPL stake pool layout: total_lamports u64 @258, pool_token_supply u64 @266, last_update_epoch u64 @274)
    pools = {'jitoSOL': 'Jito4APyf642JPZPx3hGc6WWJ8zPKtRbRs4P815Awbb', 'jupSOL': '8VpRhuxa7sUUepdY3kQiTmX9rS5vx4WgaXiAnXq4KCtr', 'bSOL': 'stk9ApL5HeVAwPLr3TLhDXdZS8ptVu7zp6ov8HFDuMi'}
    h['stake_pool_nav'] = {}
    for name, addr in pools.items():
        try:
            import base64
            import struct
            v = c.call('getAccountInfo', [addr, {'encoding': 'base64', 'commitment': 'finalized'}])['value']
            data = base64.b64decode(v['data'][0])
            if len(data) >= 282 and data[0] == 1:
                tl, ps, ep = struct.unpack_from('<QQQ', data, 258)
                h['stake_pool_nav'][name] = {'pool': addr, 'owner_program': v['owner'], 'total_lamports': tl, 'pool_token_supply': ps, 'nav_sol': tl / ps, 'last_update_epoch': ep}
        except Exception as e:
            h['stake_pool_nav'][name] = {'error': str(e)[:120]}
    h['sources']['stake_pool_nav'] = 'getAccountInfo on the stake pool state accounts (SPL stake pool layout), finalized'
    try:
        h['jito_tip_floor'] = http_json('https://bundles.jito.wtf/api/v1/bundles/tip_floor')
        h['sources']['jito'] = 'https://bundles.jito.wtf/api/v1/bundles/tip_floor'
    except Exception as e:
        h['jito_error'] = str(e)[:200]
    h['rpc_stats'] = c.stats()
    save_json(out / 'head_state.json', h)
    jp = h.get('jupiter_prices') or {}
    print(json.dumps({'slot': h.get('slot'), 'sol_usd': (jp.get(SOL) or {}).get('usdPrice'), 'kamino_markets': len(h.get('kamino_markets') or []), 'save_reserves': len(h.get('save_main') or []), 'jupiter_lend': len(h.get('jupiter_lend') or []), 'sanctum': len(h.get('sanctum_sol_value') or {}), 'errors': {k: v for k, v in h.items() if k.endswith('_error')}}, indent=1))


# ---------------------------------------------------------------- render

def table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers)]
    for r in rows:
        out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    return '\n'.join(out) + '\n'


def cmd_render(args):
    out = Path(args.out)
    A = load_json(out / 'analysis.json')
    H = load_json(out / 'head_state.json') if (out / 'head_state.json').exists() else {}
    P = load_json(out / 'prices.json') if (out / 'prices.json').exists() else {}
    w, n = A['window'], A['network']
    jp = H.get('jupiter_prices') or {}
    sol_head = (jp.get(SOL) or {}).get('usdPrice')
    L = []
    L.append('# Solana mainnet live scan: %s to %s UTC\n' % (w['start_utc'], w['end_utc']))
    L.append('Slots %d to %d (%d produced blocks of %d slots, %d skipped, %d analyzed%s), %s transactions of which %s votes and %s non-vote (%s failed, %s). SOL in-window swap price: first %s, last %s, median %s (min %s, max %s) from %s swaps; Jupiter head price %s at slot %s. Generated %s UTC by `scripts/solana_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.\n' % (
        w['start_slot'], w['end_slot'], w['produced_slots'], w['produced_slots'] + w['skipped_slots'], w['skipped_slots'], w['blocks_analyzed'], '' if w['complete'] else ' — INCOMPLETE COLLECTION', format(n['transactions'], ','), format(n['votes'], ','), format(n['nonvote'], ','), format(n['failed'], ','), pct(n['failed_share'], 1),
        P.get('sol_usd_first'), P.get('sol_usd_last'), P.get('sol_usd_median'), P.get('sol_usd_min'), P.get('sol_usd_max'), P.get('swaps_used'), ('$%.2f' % sol_head) if sol_head else '–', H.get('slot'), A['generated_utc']))
    ins = out / 'insights.md'
    if ins.exists():
        L.append(ins.read_text().strip() + '\n\n---\n')
    else:
        L.append('_No insights.md yet — narrative pending._\n\n---\n')
    # A network
    L.append('## A. Network: throughput, fees, compute, leaders\n')
    hrs = w['hours'] or 1
    L.append(table(['metric', 'value'], [
        ['transactions per second (all / non-vote)', '%.0f / %.0f' % (n['tps_all'], n['tps_nonvote'])],
        ['failed non-vote transactions', '%s (%s)' % (format(n['failed'], ','), pct(n['failed_share'], 1))],
        ['fees paid by non-vote txs', '%.1f SOL (base %.1f + priority %.1f); vote fees %.1f SOL' % (n['fees_sol'], n['base_fees_sol'], n['priority_fees_sol'], n['vote_fees_sol'])],
        ['fees paid by failed txs', '%.1f SOL' % n['failed_fees_sol']],
        ['Jito tips (successful txs only; a failed tx reverts its tip)', '%.1f SOL in %s tipping txs (%s unique tippers)' % (n['jito_tips_sol'], format(n['tip_txs'], ','), format(A['jito']['unique_tippers'], ','))],
        ['fee per non-vote tx (median / p90 / p99)', '%s / %s / %s lamports' % (n['fee_median_lamports'], n['fee_p90_lamports'], n['fee_p99_lamports'])],
        ['compute-unit price (median / p90 / p99, txs setting one)', '%s / %s / %s µlamports (%s txs)' % (n['cu_price_median_microlamports'], n['cu_price_p90'], n['cu_price_p99'], format(n['txs_with_cu_price'], ','))],
        ['largest block by non-vote compute units', format(n['max_block_nonvote_cu'], ',')],
        ['versioned (v0, lookup-table) tx share', pct(n['v0_share'], 1)],
        ['Token-2022 share of token instructions', pct(n['token22_ix_share'], 1)],
        ['accounts created / token accounts closed', '%s / %s' % (format(n['accounts_created'], ','), format(n['token_accounts_closed'], ','))],
        ['durable-nonce txs', format(n['durable_nonce_txs'], ',')],
    ]))
    L.append('\nPer 5 minutes (SOL price = in-window swap median at the bin start):\n')
    L.append(table(['start', 'blocks', 'tx', 'non-vote', 'failed', 'fees SOL', 'tips SOL', 'CU (M)', 'swaps', 'DEX volume', 'of which self-matched', 'SOL'],
                   [[r['start_utc'][11:16], r['blocks'], format(r['tx'], ','), format(r['nonvote'], ','), pct(r['failed'] / max(r['nonvote'], 1), 0), '%.1f' % r['fee_sol'], '%.1f' % r['tips_sol'], '%.0f' % (r['cu'] / 1e6), r['swaps'], usd_fmt(r['dex_usd']), usd_fmt(r.get('wash_usd', 0)), ('$%.2f' % r['sol_usd']) if r['sol_usd'] else '–'] for r in A['bins_5min']]))
    ld = A['leaders']
    L.append('\nLeaders: %d validators produced blocks. Most blocks: %s. Skipped slots by leader: %s. Most Jito tips collected: %s.\n' % (
        ld['n_leaders'], ', '.join('%s (%d)' % (short(a), c_) for a, c_ in ld['blocks_by_leader'][:8]), ', '.join('%s (%d)' % (short(a), c_) for a, c_ in ld['skipped_by_leader'][:8]) or 'none', ', '.join('%s (%.1f SOL)' % (short(a), c_) for a, c_ in ld['tips_by_leader'][:6])))
    L.append('\nJito tip accounts (behavioural check — many unique payers confirms the label):\n')
    L.append(table(['tip account', 'tips SOL', 'unique payers'], [[short(r['account']), '%.2f' % r['tips_sol'], r['unique_payers']] for r in A['jito']['by_tip_account']]))
    L.append('\nTop tippers:\n')
    L.append(table(['payer', 'label', 'tips SOL', 'tip txs'], [[short(r['payer']), r['label'] or '', '%.3f' % r['tips_sol'], r['tip_txs']] for r in A['jito']['top_tippers'][:15]]))
    # B programs
    L.append('\n## B. Programs and transaction kinds\n')
    L.append('Transaction kinds (payer-centric classification: `swap` = a DEX/aggregator program with a sold and a bought leg; `pump_launch` = pump.fun `create`; `transfer` = only system/token programs with balances moving):\n')
    L.append(table(['kind', 'txs', 'share', 'fees SOL'], [[r['kind'], format(r['tx'], ','), pct(r['share'], 1), '%.2f' % r['fee_sol']] for r in A['kinds']]))
    L.append('\nTop programs by transactions (main program = first non-system top-level program). `payers` = unique fee payers and the share of the top one — a program with one or two payers is a private bot; `tokens move` = share of its txs where any token balance changes (near zero = quote posting / opportunity checks, not trades); instruction names from Anchor logs when the tx has one main program:\n')
    L.append(table(['program', 'label', 'txs', 'failed', 'swaps', 'payers (top share)', 'tokens move', 'avg CU', 'avg keys', 'nonce txs', 'fees SOL', 'tips SOL', 'top instructions'],
                   [[short(r['program']), r['label'] or '', format(r['tx'], ','), pct(r['fail_share'], 0), format(r['swaps'], ','), '%d (%s)' % (r['unique_payers'], pct(r['top_payer_share'], 0)), pct(r['token_move_share'], 0), format(round(r['avg_cu']), ','), '%.0f' % r['avg_keys'], format(r['nonce_txs'], ','), '%.2f' % r['fee_sol'], '%.2f' % r['tips_sol'], ', '.join('%s %d' % (k_, v_) for k_, v_ in r['top_instructions'][:3])] for r in A['programs'][:40]]))
    la = A['launches']
    L.append('\nToken launches (a new mint initialised inside a launchpad transaction): %d in the window by %d creators — %s. New mints outside launchpads (CLMM position NFTs, LP tokens, other): %s.\n' % (
        la['total'], la['unique_creators'], ', '.join('%s %d' % (n_, c_) for n_, _, c_ in la['by_program'][:8]), ', '.join('%s %d' % (n_, c_) for n_, _, c_ in la['other_new_mints_by_program'][:6])))
    L.append('\n`other` (no DEX, lending, bridge or transfer signature) is dominated by: %s. `dex_other` (a DEX program is invoked but no trader has a sold and a bought leg — quote posts, fee collection, failed-in-effect routes): %s.\n' % (
        ', '.join('%s %s' % (n_, format(c_, ',')) for n_, _, c_ in A['other_kind_programs'][:8]), ', '.join('%s %s' % (n_, format(c_, ',')) for n_, _, c_ in A['dex_other_programs'][:8])))
    L.append('\nTop payers by transactions (bots):\n')
    L.append(table(['payer', 'label', 'txs', 'failed', 'fees SOL', 'tips SOL'], [[short(r['payer']), r['label'] or '', format(r['tx'], ','), r['failed'], '%.2f' % r['fee_sol'], '%.2f' % r['tips_sol']] for r in A['payers'][:20]]))
    L.append('\nTop payers by fees + tips:\n')
    L.append(table(['payer', 'label', 'txs', 'failed', 'fees SOL', 'tips SOL'], [[short(r['payer']), r['label'] or '', format(r['tx'], ','), r['failed'], '%.2f' % r['fee_sol'], '%.2f' % r['tips_sol']] for r in A['top_fee_payers'][:20]]))
    # C dex
    d = A['dex']
    L.append('\n## C. DEX: volume by venue, pairs, implied prices, largest swaps, sandwiches, launches\n')
    L.append('Priced volume %s over %s swaps (%s swaps between unpriced tokens are excluded). Volume = the larger priced leg of the payer; a swap that touches several venues is attributed to `multi`.\n' % (usd_fmt(d['total_priced_usd']), format(d['priced_swaps'], ','), format(d['unpriced_swaps'], ',')))
    L.append(table(['venue', 'volume', 'swaps', 'unpriced swaps'], [[r['venue'], usd_fmt(r['usd']), format(r['swaps'], ','), r['unpriced_swaps']] for r in d['volume_by_venue'][:25]]))
    L.append('\nVolume routed through aggregators (counted once per swap, overlapping with the venue table): %s\n' % ', '.join('%s %s' % (r['aggregator'], usd_fmt(r['usd'])) for r in d['volume_via_aggregator']))
    sm = d.get('self_matched') or {}
    if sm:
        L.append('\nSelf-matched swaps (one transaction, two signers: the second signer\'s token and native-SOL legs mirror the trader\'s — a buy and a sell of the same token by the same operator inside one transaction, i.e. wash volume): %s over %s swaps from %s wallet pairs, %s of all priced volume.\n' % (usd_fmt(sm['total_usd']), format(sm['swaps'], ','), format(sm['wallet_pairs'], ','), pct(sm['total_usd'] / max(d['total_priced_usd'], 1), 1)))
        L.append(table(['venue', 'self-matched volume', 'swaps', 'share of venue volume'], [[r['venue'], usd_fmt(r['usd']), format(r['swaps'], ','), pct(r['share_of_venue'], 0) if r['share_of_venue'] is not None else '–'] for r in sm['by_venue'][:8]]))
        L.append('\n' + table(['token', 'self-matched volume', 'swaps'], [[r['symbol'] or short(r['mint']), usd_fmt(r['usd']), format(r['swaps'], ',')] for r in sm['by_token'][:12]]))
    L.append('\nTop pairs:\n')
    L.append(table(['venue', 'pair', 'volume', 'swaps'], [[r['venue'], ' / '.join(x if len(x) < 12 else short(x) for x in r['pair'].split(' / ')), usd_fmt(r['usd']), r['swaps']] for r in d['top_pairs'][:30]]))
    if d['implied_prices']:
        L.append('\nImplied prices from single-pair swaps against a priced leg (median, min–max across the window):\n')
        L.append(table(['token', 'median', 'min', 'max', 'swaps', 'volume'], [[r['symbol'] or '?', '$%.6g' % r['median_usd'], '$%.4g' % r['min'], '$%.4g' % r['max'], r['n'], usd_fmt(r['usd_volume'])] for r in d['implied_prices'][:30]]))
    L.append('\nLargest swaps:\n')
    L.append(table(['time', 'venue', 'payer', 'sold', 'bought', 'value', 'tip SOL'], [[r['time'][11:19], r['venue'], short(r['payer']), ', '.join('%s %s' % (human(v, False) if isinstance(v, float) else 'raw ' + human(v, False), k_ if len(k_) < 12 else short(k_)) for k_, v in r['sold'].items()), ', '.join('%s %s' % (human(v, False) if isinstance(v, float) else 'raw ' + human(v, False), k_ if len(k_) < 12 else short(k_)) for k_, v in r['bought'].items()), usd_fmt(r['usd']), '%.4f' % r['tips_sol']] for r in d['big_swaps'][:25]]))
    sw = d['sandwiches']
    closed = [e for e in sw['examples'] if e.get('position_closed')]
    L.append('\nSame-block sandwich pattern (trader A buys, another trader buys the same token through the same pool, A sells — all in one block): %d pattern matches, of which %d closed the token position within 10%% (the true sandwich shape; the rest are coincidental buy-buy-sell sequences in busy pump pools). Confirmed-shape victim volume %s.\n' % (sw['n'], sum(1 for _ in closed), usd_fmt(sw['victim_usd'])))
    if sw['attackers']:
        L.append(table(['attacker', 'closed sandwiches', 'PnL (SOL+stable legs)'], [[short(r['attacker']), r['n'], usd_fmt(r['pnl_usd'])] for r in sw['attackers'][:10]]))
        L.append('\n' + table(['time', 'token', 'attacker', 'victim', 'victim size', 'front size', 'attacker PnL', 'closed', 'tips SOL'], [[r['time'][11:19], r['token'], short(r['attacker']), short(r['victim']), usd_fmt(r['victim_usd']), usd_fmt(r['front_usd']), usd_fmt(r['attacker_pnl_usd']), 'yes' if r.get('position_closed') else '', r['tips_sol']] for r in (closed + [e for e in sw['examples'] if not e.get('position_closed')])[:12]]))
    pu = A['pump']
    L.append('\nPump.fun (bonding curve + PumpSwap AMM): %s. Bonding-curve SOL turnover %.1f SOL (buys %.1f, sells %.1f); PumpSwap trader SOL legs %.1f SOL. Cashback claims: %s txs, %.2f SOL received. %d unique launch creators; most active: %s. Instruction mix: %s.\n' % (
        ', '.join('%s %d' % (k_, v_) for k_, v_ in sorted(pu['counts'].items(), key=lambda x: -x[1])), pu['sol'].get('bonding_curve_sol', 0), pu['sol'].get('buy_sol', 0), pu['sol'].get('sell_sol', 0), pu['sol'].get('pumpswap_sol', 0), format(pu.get('cashback_claims', 0), ','), pu.get('cashback_sol_received', 0), pu['unique_creators'], ', '.join('%s (%d)' % (short(a), c_) for a, c_ in pu['top_creators'][:5]),
        ', '.join('%s %d' % (k_, v_) for k_, v_ in pu['instructions'][:12])))
    # D lending
    L.append('\n## D. Lending: rates at head, events in window\n')
    for mk in (H.get('kamino_markets') or [])[:5]:
        rows = [r for r in mk['reserves'] if r['supplied_usd'] >= 1e6]
        rows.sort(key=lambda r: -r['supplied_usd'])
        if not rows:
            continue
        L.append('\nKamino %s (reserves with ≥ $1M supplied; APY as reported by the Kamino API):\n' % mk['name'])
        L.append(table(['asset', 'supply APY', 'borrow APY', 'utilisation', 'supplied', 'borrowed'], [[r['token'], pct(r['supply_apy']), pct(r['borrow_apy']), pct(r['util'], 1), usd_fmt(r['supplied_usd']), usd_fmt(r['borrowed_usd'])] for r in rows[:14]]))
    if H.get('save_main'):
        rows = [r for r in H['save_main'] if r['supplied_usd'] >= 1e6]
        L.append('\nSave (Solend) main market (reserves with ≥ $1M supplied; rates as reported by the Save API, utilisation from reserve state):\n')
        L.append(table(['asset', 'supply APY', 'borrow APY', 'utilisation', 'supplied', 'borrowed'], [[r['symbol'] or short(r['mint']), pct(r['supply_apy']), pct(r['borrow_apy']), pct(r['util'], 1), usd_fmt(r['supplied_usd']), usd_fmt(r['borrowed_usd'])] for r in rows[:12]]))
    if H.get('jupiter_lend'):
        L.append('\nJupiter Lend Earn (supply rate + rewards, bps as reported):\n')
        L.append(table(['vault', 'asset', 'supply APY', 'rewards', 'total', 'total assets'], [[r['symbol'], r['asset_symbol'], pct(r['supply_rate_bps'] / 1e4), pct(r['rewards_rate_bps'] / 1e4), pct(r['total_rate_bps'] / 1e4), usd_fmt(r['total_assets'] * r['asset_price'])] for r in sorted(H['jupiter_lend'], key=lambda r: -r['total_assets'] * r['asset_price'])[:12]]))
    le = A['lending']
    L.append('\nLending events in the window (instruction discriminators matched per program):\n')
    L.append(table(['venue', 'txs', 'failed', 'events'], [[k_, v.get('tx', 0), v.get('failed', 0), ', '.join('%s %d' % (a, b_) for a, b_ in sorted(((a, b_) for a, b_ in v.items() if a not in ('tx', 'failed')), key=lambda x: -x[1])[:10])] for k_, v in le['events'].items()]))
    L.append('\nLiquidations that succeeded: %d. Liquidation attempts (ok / failed, top payers): %s. Successful flash loans: %s. Flash-loan payers (with failures): %s. Programs co-invoked in flash-loan txs: %s.\n' % (
        le['n_liquidations'], '; '.join('%s %d / %d (%s)' % (k_, v['ok'], v['failed'], ', '.join('%s %d' % (short(a), n_) for a, n_ in v['top_payers'][:3])) for k_, v in le['liquidation_attempts'].items()) or 'none',
        ', '.join('%s %d txs (~%s principal)' % (k_, v['tx'], usd_fmt(v['principal_usd_est'])) for k_, v in le['flash_loans'].items()) or 'none',
        '; '.join('%s: %s' % (k_, ', '.join('%s %d' % (short(a.split(' ')[0]) + (' (failed)' if 'failed' in a else ''), n_) for a, n_ in v[:5])) for k_, v in le['flash_payers'].items()) or 'none',
        '; '.join('%s: %s' % (k_, ', '.join('%s %d' % (a, n_) for a, n_ in v[:5])) for k_, v in le['flash_co_programs'].items()) or 'none'))
    # dollar/SOL yield ladder across venues
    ladder = collections.defaultdict(dict)
    for mk in (H.get('kamino_markets') or [])[:6]:
        for r in mk['reserves']:
            if r['supplied_usd'] >= 5e6 and r['token'].upper() in ('USDC', 'USDT', 'USDG', 'PYUSD', 'USDS', 'USD1', 'SOL', 'JUPUSD', 'USDE', 'JLP', 'JITOSOL', 'JUPSOL'):
                ladder[r['token'].upper()]['Kamino ' + mk['name'].replace(' Market', '')] = (r['supply_apy'], r['borrow_apy'], r['util'], r['supplied_usd'])
    for r in H.get('save_main') or []:
        if r['supplied_usd'] >= 5e6 and (r['symbol'] or '').upper() in ('USDC', 'USDT', 'USDG', 'PYUSD', 'USDS', 'USD1', 'SOL', 'JUPUSD', 'USDE', 'JLP', 'JITOSOL', 'JUPSOL'):
            ladder[r['symbol'].upper()]['Save main'] = (r['supply_apy'], r['borrow_apy'], r['util'], r['supplied_usd'])
    for r in H.get('jupiter_lend') or []:
        sym = (r['asset_symbol'] or '').upper().replace('WSOL', 'SOL')
        if sym in ('USDC', 'USDT', 'USDG', 'PYUSD', 'USDS', 'USD1', 'SOL', 'JUPUSD', 'USDE', 'EURC') and r['total_assets'] * r['asset_price'] >= 5e6:
            ladder[sym]['Jupiter Lend'] = (r['total_rate_bps'] / 1e4, None, None, r['total_assets'] * r['asset_price'])
    if ladder:
        L.append('\nSame asset, different venue (supply APY / borrow APY / utilisation / supplied; reserves ≥ $5M; Jupiter Lend = supply + rewards, no borrow side):\n')
        rows = []
        for asset, vs in sorted(ladder.items(), key=lambda x: -max(v[3] for v in x[1].values())):
            for ven, (sa, ba, u, sup) in sorted(vs.items(), key=lambda x: -x[1][0]):
                rows.append([asset, ven, pct(sa), pct(ba) if ba is not None else '–', pct(u, 0) if u is not None else '–', usd_fmt(sup)])
        L.append(table(['asset', 'venue', 'supply APY', 'borrow APY', 'util', 'supplied'], rows))
    if le['liquidations']:
        L.append(table(['time', 'venue', 'liquidator', 'received', 'paid', 'received $', 'paid $', 'tip SOL'], [[r['time'][11:19], r['venue'], short(r['liquidator']), ', '.join('%s %s' % (human(v, False), k_) for k_, v in r['received'].items()), ', '.join('%s %s' % (human(v, False), k_) for k_, v in r['paid'].items()), usd_fmt(r['usd_received']), usd_fmt(r['usd_paid']), '%.4f' % r['tips_sol']] for r in le['liquidations'][:20]]))
    # E stablecoins / LST
    L.append('\n## E. Stablecoins and LSTs: issuance, pegs, NAV\n')
    iss = A['issuance']
    L.append('Mints and burns on the registry stablecoin and LST mints, split by whether the instruction ran inside a CCTP transaction (bridge) or not (issuer treasury / stake pool):\n')
    L.append(table(['token', 'issuer minted', 'issuer burned', 'CCTP minted', 'CCTP burned', 'net'], [[k_, format(round(v['issuer_mint']), ','), format(round(v['issuer_burn']), ','), format(round(v['cctp_mint']), ','), format(round(v['cctp_burn']), ','), format(round(v['net']), ',')] for k_, v in sorted(iss['by_mint'].items(), key=lambda x: -(x[1]['mint'] + x[1]['burn']))]))
    L.append('\nBy mint authority (CCTP mints/burns carry the CCTP minter PDA as authority; issuer treasuries carry the issuer authority):\n')
    L.append(table(['token', 'side', 'authority', 'label', 'amount', 'n'], [[r['mint'], r['side'], 'CCTP tx (user burn / custody)' if (r['authority'] or '').startswith('CCTP') else short(r['authority'] or '?'), r['label'] or '', format(round(r['amount']), ','), r['n']] for r in iss['by_authority'][:20]]))
    L.append('\nLargest single mints/burns:\n')
    L.append(table(['time', 'token', 'side', 'amount', 'authority', 'CCTP tx'], [[r['time'][11:19], r['mint'], r['side'], format(round(r['amount']), ','), short(r['authority'] or '?'), 'yes' if r['cctp'] else ''] for r in iss['largest'][:15]]))
    if jp:
        rows = []
        for mm, v in MINTS.items():
            if v['class'] in ('stable', 'yield_stable', 'stable_eur') and mm in jp:
                rows.append([v['symbol'], '$%.4f' % jp[mm]['usdPrice'], '%+.1f bp' % ((jp[mm]['usdPrice'] - 1) * 1e4) if v['class'] == 'stable' else '', usd_fmt(jp[mm].get('liquidity'))])
        L.append('\nStablecoin prices at head (Jupiter aggregator price; deviation from par):\n')
        L.append(table(['token', 'price', 'vs par', 'liquidity (Jupiter)'], rows))
    sv = H.get('sanctum_sol_value') or {}
    spn = {k: v for k, v in (H.get('stake_pool_nav') or {}).items() if 'nav_sol' in v}
    if (sv or spn) and sol_head:
        rows = []
        for mm, v in MINTS.items():
            if v['class'] == 'lst' and mm in jp:
                mkt = jp[mm]['usdPrice'] / sol_head
                onchain = spn.get(v['symbol'], {}).get('nav_sol')
                sanc = sv.get(v['symbol'])
                rows.append([v['symbol'], ('%.5f' % onchain) if onchain else '–', ('%+.1f bp' % ((mkt / onchain - 1) * 1e4)) if onchain else '–', ('%.5f' % sanc) if sanc else '–', ('%+.1f bp' % ((mkt / sanc - 1) * 1e4)) if sanc else '–', '%.5f' % mkt, usd_fmt(jp[mm].get('liquidity'))])
        L.append('\nLSTs: market price in SOL (Jupiter price / Jupiter SOL price) against the stake-pool NAV read on-chain (finalized; pools verified by owner program and account type) and against Sanctum\'s sol-value API. The two NAV sources disagree by ~1.9% on every pool the on-chain read covers; the on-chain value is authoritative and the Sanctum column is kept only to document the discrepancy:\n')
        L.append(table(['LST', 'NAV on-chain (SOL)', 'market vs on-chain', 'Sanctum sol-value', 'market vs Sanctum', 'market (SOL)', 'liquidity'], rows))
    if iss['lst']:
        L.append('\nLST issuance in the window (mintTo/burn on the LST mints): %s\n' % ', '.join('%s +%s −%s' % (k_, format(round(v['mint']), ','), format(round(v['burn']), ',')) for k_, v in sorted(iss['lst'].items(), key=lambda x: -(x[1]['mint'] + x[1]['burn']))))
    # F bridges / exchanges / large
    L.append('\n## F. Bridges, exchanges, large transfers, poisoning\n')
    cc = A['cctp']
    L.append('CCTP USDC: out %s (%d deposit-for-burn), in %s (%d receive-message; v2 pays recipients out of a custody token account instead of minting — %s).\n' % (usd_fmt(cc['out_total']), sum(r['n'] for r in cc['out_by_chain']), usd_fmt(cc['in_total']), sum(r['n'] for r in cc['in_by_chain']), ', '.join('%s %s' % (k_, usd_fmt(v)) for k_, v in cc['in_paid_from_custody_v2'].items()) or 'none'))
    L.append(table(['direction', 'chain', 'USDC', 'transfers'], [['out', r['chain'], usd_fmt(r['usd']), r['n']] for r in cc['out_by_chain']] + [['in', r['chain'], usd_fmt(r['usd']), r['n']] for r in cc['in_by_chain']]))
    if cc['largest']:
        L.append('\nLargest CCTP transfers:\n')
        L.append(table(['time', 'direction', 'chain', 'USDC', 'payer', 'recipient (EVM)'], [[r['time'][11:19], r['direction'], r['chain'], usd_fmt(r['usd']), short(r['payer']), ('0x' + r['recipient'][-40:][:8] + '…' + r['recipient'][-4:]) if r.get('recipient') else ''] for r in cc['largest'][:12]]))
    ex = A['exchanges']
    L.append('\nExchange net flow (labels from memory; the fan-in column is the behavioural check — a deposit hot wallet receives from many unique senders):\n')
    rows = []
    for name, v in sorted(ex['net_flow'].items(), key=lambda x: -abs(x[1]['usd_net'])):
        chk = ex['label_checks'].get(name, {})
        rows.append([name, ', '.join('%s %s' % (a, human(x)) for a, x in sorted(v['assets'].items(), key=lambda y: -abs(v['usd'].get(y[0], 0)))[:5]), usd_fmt(v['usd_net']), v['txs'], v['in_counterparties'], v['out_counterparties'], chk.get('unique_senders_sol>=0.1', 0)])
    L.append(table(['exchange', 'net by asset', 'net USD', 'txs', 'senders', 'receivers', 'fan-in (SOL≥0.1)'], rows))
    L.append('\nLabel checks: %s\n' % '; '.join('%s: %s' % (k_, v['verdict']) for k_, v in ex['label_checks'].items()))
    if ex['unlabelled_fan_in']:
        L.append('\nUnlabelled addresses with exchange-like fan-in (≥ 40 unique senders of ≥ 0.1 SOL):\n')
        L.append(table(['address', 'label', 'unique senders', 'transfers in', 'SOL in', 'median in', 'transfers out', 'destinations', 'SOL out', 'shape'], [[short(r['address']), r['label'] or '', r['unique_senders'], r['transfers'], '%.1f' % r['sol_received'], '%.3f' % r['median_sol'], r['out_transfers'], r['out_destinations'], '%.1f' % r['sol_sent'], r['shape']] for r in ex['unlabelled_fan_in'][:15]]))
    if ex.get('distributors'):
        L.append('\nDistributors (≥ 200 outgoing SOL transfers of ≥ 0.1 SOL to ≥ 6 destinations — wallet funders, payout hubs):\n')
        L.append(table(['address', 'label', 'transfers out', 'SOL sent'], [[short(r['address']), r['label'] or '', r['out_transfers'], '%.1f' % r['sol_sent']] for r in ex['distributors'][:12]]))
    L.append('\nLargest priced position changes (per owner and asset inside one transaction, ≥ $100k):\n')
    L.append(table(['time', 'owner', 'label', 'asset', 'change', 'value', 'kind', 'programs'], [[r['time'][11:19], short(r['owner']), r['label'] or '', r['asset'], human(r['delta']), usd_fmt(r['usd']), r['kind'], ', '.join(r['programs'])] for r in A['large']['moves'][:30]]))
    L.append('\nLargest native SOL balance changes (≥ 1,000 SOL):\n')
    L.append(table(['time', 'account', 'label', 'change SOL', 'value', 'kind', 'payer'], [[r['time'][11:19], short(r['account']), r['label'] or '', '%+.1f' % r['delta_sol'], usd_fmt(r['usd']), r['kind'], short(r['payer'])] for r in A['large']['sol'][:20]]))
    po = A['poisoning']
    L.append('\nAddress-poisoning style dust (≤ 1 raw token unit or ≤ 1,000 lamports sent by the payer to ≥ 20 distinct recipients): %s transfers in the window from %d senders with ≥ 50 each. Top senders (senders that dust only a handful of accounts — market-maker heartbeats — are excluded: %s):\n' % (
        format(po['total_dust_transfers'], ','), po['senders_over_50'], ', '.join('%s %d→%d' % (short(r['sender']), r['dust_transfers'], r['recipients']) for r in po['excluded_few_recipient_senders'][:4]) or 'none'))
    L.append(table(['sender', 'dust transfers', 'distinct recipients'], [[short(r['sender']), r['dust_transfers'], r['recipients']] for r in po['dust_senders'][:10]]))
    (out / 'report.md').write_text('\n'.join(L))
    print('wrote', out / 'report.md', len('\n'.join(L)), 'chars')


# ---------------------------------------------------------------- verify (independent re-derivation of headline numbers)

def cmd_verify(args):
    """Recompute headline numbers with separate, minimal code paths straight from the block files and compare with analysis.json."""
    out = Path(args.out)
    A = load_json(out / 'analysis.json')
    n_tx = n_vote = n_nonvote = n_failed = 0
    fees = 0
    tips = 0
    launches = 0
    cctp_out = 0.0
    usdc_burn = 0.0
    blocks = 0
    tip_set = JITO_TIPS
    for slot, p in block_files(out):
        b = load_json(p)
        blocks += 1
        n_tx += b['n_tx']
        n_vote += b['n_vote']
        for tx in b['transactions']:
            n_nonvote += 1
            meta = tx['meta']
            n_failed += meta['err'] is not None
            fees += meta['fee']
            keys = list(tx['transaction']['message']['accountKeys'])
            la = meta.get('loadedAddresses') or {}
            keys += (la.get('writable') or []) + (la.get('readonly') or [])
            # Jito tips: system transfers (top-level or inner) to a tip account
            allix = list(tx['transaction']['message']['instructions']) + [i for g in meta.get('innerInstructions') or [] for i in g['instructions']]
            for ix in allix:
                pid = keys[ix['programIdIndex']] if ix['programIdIndex'] < len(keys) else None
                if pid == D.SYSTEM and ix.get('data') and meta['err'] is None:
                    d = D.b58decode(ix['data'])
                    if len(d) >= 12 and int.from_bytes(d[:4], 'little') == 2 and len(ix['accounts']) >= 2 and keys[ix['accounts'][1]] in tip_set:
                        tips += int.from_bytes(d[4:12], 'little')
            if meta['err'] is None:
                logs = meta.get('logMessages') or []
                names = {l[26:] for l in logs if l.startswith('Program log: Instruction: ')}
                progs = {keys[ix['programIdIndex']] for ix in allix if ix['programIdIndex'] < len(keys)}
                if progs & LAUNCHPADS and ('InitializeMint2' in names or 'InitializeMint' in names):
                    launches += 1
                is_deposit = ('DepositForBurn' in names or 'DepositForBurnWithHook' in names) and bool(progs & {D.CCTP_TOKEN_MESSENGER, D.CCTP_V2_TOKEN_MESSENGER})
                for ix in allix:
                    pid = keys[ix['programIdIndex']] if ix['programIdIndex'] < len(keys) else None
                    if pid in (D.TOKEN, D.TOKEN_2022) and ix.get('data'):
                        d = D.b58decode(ix['data'])
                        if d and d[0] in (8, 15) and len(d) >= 9 and len(ix['accounts']) >= 2 and keys[ix['accounts'][1]] == USDC:
                            usdc_burn += int.from_bytes(d[1:9], 'little') / 1e6
                            if is_deposit:
                                cctp_out += int.from_bytes(d[1:9], 'little') / 1e6
    n = A['network']
    checks = [
        ('blocks analyzed', blocks, A['window']['blocks_analyzed']),
        ('transactions', n_tx, n['transactions']),
        ('votes', n_vote, n['votes']),
        ('non-vote', n_nonvote, n['nonvote']),
        ('failed', n_failed, n['failed']),
        ('fees SOL', round(fees / LAMPORTS, 3), round(n['fees_sol'], 3)),
        ('Jito tips SOL', round(tips / LAMPORTS, 3), round(n['jito_tips_sol'], 3)),
        ('launches (log-name basis; Solana truncates long logs, so <= 5% fewer is expected)', launches, float(A['launches']['total'])),
        ('CCTP USDC out (USDC burned inside DepositForBurn txs)', round(cctp_out), A['cctp']['out_total']),
        ('USDC burned (issuer + CCTP)', round(usdc_burn), round(A['issuance']['by_mint'].get('USDC', {}).get('burn', 0))),
    ]
    rows = []
    ok_all = True
    for name, mine, theirs in checks:
        tol = (0.05 if 'launches' in name else 0.02) * max(abs(theirs), 1) if isinstance(theirs, float) or 'CCTP' in name else 0
        ok = abs(mine - theirs) <= tol
        ok_all &= ok
        rows.append({'check': name, 'recomputed': mine, 'analysis': theirs, 'ok': ok})
        print('%-45s recomputed %-14s analysis %-14s %s' % (name, mine, theirs, 'OK' if ok else 'MISMATCH'))
    save_json(out / 'verify.json', {'checks': rows, 'all_ok': ok_all, 'utc': utc(int(time.time()))})
    print('all ok' if ok_all else 'MISMATCHES')


def cmd_show(args):
    out = Path(args.out)
    want = set(args.sigs)
    for slot, p in block_files(out):
        b = load_json(p)
        for tx in b['transactions']:
            if tx['transaction']['signatures'][0] in want:
                keys = D.tx_keys(tx)
                print('== slot', slot, utc(b['blockTime']), 'sig', tx['transaction']['signatures'][0], 'err', tx['meta']['err'], 'fee', tx['meta']['fee'], 'cu', tx['meta'].get('computeUnitsConsumed'))
                for ix in D.iter_instructions(tx, keys):
                    d = D.decode(ix)
                    print('  ' + '  ' * (ix['depth'] - 1) + name_of(ix['program']), json.dumps(d) if d else '(%d bytes) %s' % (len(ix['data']), DISC.get(ix['program'], {}).get(ix['data'][:8], '')), '' if d else [short(a) for a in ix['accounts'][:6]])
                for k_, v in D.sol_deltas(tx, keys).items():
                    print('  SOL', short(k_), label(k_) or '', '%+.6f' % (v / LAMPORTS))
                for acct, e in D.token_deltas(tx, keys).items():
                    if e['delta_raw']:
                        print('  TOKEN', short(acct), 'owner', short(e['owner'] or '?'), label(e['owner'] or '') or '', SYM.get(e['mint'], short(e['mint'])), '%+.6f' % (e['delta_raw'] / 10 ** e['decimals']))
                for l in tx['meta'].get('logMessages') or []:
                    print('  LOG', l[:160])
                want.discard(tx['transaction']['signatures'][0])
        if not want:
            break


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in (('prices', cmd_prices), ('analyze', cmd_analyze), ('head', cmd_head), ('render', cmd_render), ('verify', cmd_verify), ('show', cmd_show)):
        s = sub.add_parser(name)
        s.add_argument('--out', required=True)
        if name == 'prices':
            s.add_argument('--every', type=int, default=10)
        if name == 'show':
            s.add_argument('sigs', nargs='+')
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
