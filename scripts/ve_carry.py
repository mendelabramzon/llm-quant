#!/usr/bin/env python3
"""Hedged vote-escrow carry on Aerodrome (Base) and Velodrome (Optimism): lock the token, vote, short the perp.

Why. Every surviving row in the book has a counterparty with a non-price motive. On Aerodrome and Velodrome two such
counterparties pay vote-escrowed holders each week, in real tokens: protocols that bribe to steer emissions to their
pools, and traders whose swap fees go to the voters of the pool they traded in. The scarce resource is the lock
(up to four years, or permanent), because few holders want years of AERO price risk. If the price risk can be shorted
away on a perp, what is left is a carry: voter rewards plus funding, minus the hedge's costs and the cost of ever getting
out of the lock. Two questions: (1) does the hedged position beat the savings rate, net of everything, out of sample;
(2) does an attentive voter who re-allocates every epoch earn materially more than the average vote, and does that
need last-hour votes (a timing game) or not.

Data, all read-only:
  * chain — every gauge's fee and bribe reward contracts, read from current state through Multicall3: the per-epoch
    reward amounts (`tokenRewardsPerEpoch(token, epochStart)`), the pool's votes at the end of the epoch and at the
    decision times (`getPriorSupplyIndex` / `supplyCheckpoints`), the veNFT voting supply (`totalSupplyAt`) and the
    rebase (`RewardsDistributor.tokensPerWeek`). Killed gauges are included (RewardsSugar skips them: survivorship).
  * logs — `NotifyReward` events in the last 24 hours of each epoch (what was not yet known at the decision time),
    full weeks for a sample of epochs (the independent check of the storage reads), and veNFT transfers (sales).
  * perps — Binance, Bybit, OKX and Hyperliquid funding, daily klines, open interest and depth for AERO (and Binance's
    VELODROMEUSDT).
  * prices — DefiLlama (coins.llama.fi) at claim time plus a sale lag.

Conventions. Epochs are Aerodrome's weeks, Thursday 00:00 UTC to Thursday 00:00 UTC (`ts // WEEK * WEEK`). Rewards
of epoch e are notified during e and claimable at its end (the flip); the fees voters of epoch e receive are the swap
fees of epoch e-1, deposited at the start of e. A vote is one unit of veNFT voting power; a permanent lock has one vote
per locked token. Returns are per epoch as a fraction of the capital the position ties up; annualised with
365/7 epochs a year.

Protocol. 22 variants are fixed in `precommitted_variants()` before any return is computed: the voter rule (average
vote; `prev` = last epoch's rewards; `t24` / `t1` = what is posted a day / an hour before the vote closes, using the
NotifyReward logs to remove what arrived later) x lock size ($1M/$5M/$20M, own dilution by water-filling over at most
30 pools), always on or switched on a trailing signal (exits sell the lock at the observed discount), and the hedge
venue (Binance once listed, Bybit before; or the venue with the best trailing four epochs of funding). One is chosen
on the first half of the hedged epochs and tested once on the second (backtest.choose_then_test); Newey-West t with
4 lags, a 4-epoch block bootstrap, drawdown, halves of the test window and sensitivities are reported beside it.

    python3 scripts/ve_carry.py collect --parts registry,epochs,logs,verify,prices,sales --chains base
    python3 scripts/ve_carry.py collect --parts registry,epochs,logs,verify,prices --chains optimism
    python3 scripts/ve_carry.py collect --parts perps --chains none
    python3 scripts/ve_carry.py analyze --chains base,optimism
    python3 scripts/ve_carry.py render

Network etiquette: Infura through scripts/live_rpc.py (key rotation, redaction) with Multicall3 batches of 350 reads
and 6 workers; DefiLlama batchHistorical at 1.2 s a call; Hyperliquid at 4 s a call. Every stage writes gzipped raw
files under research/2026-10-10/ve_carry/raw/ and is skipped when its file exists (delete a file to refetch it).
"""
import argparse
import bisect
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import math
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
WEEK = 604800
DAY = 86400
HOUR = 3600
EPOCHS_PER_YEAR = 365.0 / 7.0
SSR = 0.038                       # Sky savings rate today: the benchmark of every row
SAVINGS_PAID = {2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}
UA = 'Mozilla/5.0'
MERGER_TS = 1792627200            # 2026-10-22 00:00 UTC: legacy emissions and voting end, veNFTs migrate to sAERO
MULTICALL3 = '0xcA11bde05977b3631167028862bE2a173976CA11'

# Addresses checked against github.com/aerodrome-finance/contracts README, velodrome-finance/sugar deployments/*.env,
# and Voter.ve() on chain (2026-10-10).
CHAINS = {
    'base': {
        'rpc': 'https://base-mainnet.infura.io/v3/',
        'voter': '0x16613524e02ad97eDfeF371bC883F2F5d6C480A5',
        've': '0xeBf418Fe2512e7E6bd9b87a8F0f294aCDC67e6B4',
        'dist': '0x227f65131A261548b057215bB1D5Ab2997964C7d',
        'token': '0x940181a94A35A4569E4529A3CDfB74e38FD98631',
        'symbol': 'AERO',
        'rewards_sugar': '0x1b121EfDaF4ABb8785a315C51D29BCE0552A7678',
        'llama': 'base',
        'genesis_ts': 1686789347,     # block 0; Base blocks are exactly 2 s apart
        'genesis_block': 0,
        'first_epoch': 1692835200,    # 2023-08-24: the epoch in which Aerodrome's first votes were cast
    },
    'optimism': {
        'rpc': 'https://optimism-mainnet.infura.io/v3/',
        'voter': '0x41C914ee0c7E1A5edCD0295623e6dC557B5aBf3C',
        've': '0xFAf8FD17D9840595845582fCB047DF13f006787d',
        'dist': '0x9D4736EC60715e71aFe72973f7885DCBC21EA99b',
        'token': '0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db',
        'symbol': 'VELO',
        'rewards_sugar': '0x62CCFB2496f49A80B0184AD720379B529E9152fB',
        'llama': 'optimism',
        'genesis_ts': 1686068903,     # Bedrock activation, block 105235063; 2 s blocks after it
        'genesis_block': 105235063,
        'first_epoch': 1686787200,    # 2023-06-15: Velodrome v2 launch week
    },
}

# Selectors (keccak-256 of the signature, first four bytes; test_ve_carry.py recomputes them).
SEL = {
    'length()': '0x1f7b6d32',
    'pools(uint256)': '0xac4afa38',
    'gauges(address)': '0xb9a09fd5',
    'gaugeToFees(address)': '0xc4f08165',
    'gaugeToBribe(address)': '0x929c8dcd',
    'isAlive(address)': '0x1703e5f9',
    'weights(address)': '0xa7cac846',
    'totalWeight()': '0x96c82e57',
    'token0()': '0x0dfe1681',
    'token1()': '0xd21220a7',
    'rewardsListLength()': '0xe6886396',
    'rewards(uint256)': '0xf301af42',
    'supplyNumCheckpoints()': '0xe8111a12',
    'supplyCheckpoints(uint256)': '0xf7412baf',
    'getPriorSupplyIndex(uint256)': '0x76f4be36',
    'tokenRewardsPerEpoch(address,uint256)': '0x92777b29',
    'totalSupply()': '0x18160ddd',
    'rewardRateByEpoch(uint256)': '0x94af5b63',
    'totalSupplyAt(uint256)': '0x981b24d0',
    'supply()': '0x047fc9aa',
    'permanentLockBalance()': '0x4d01cb66',
    'tokensPerWeek(uint256)': '0x899519be',
    'aggregate3((address,bool,bytes)[])': '0x82ad56cb',
    'decimals()': '0x313ce567',
    'symbol()': '0x95d89b41',
    'epochsByAddress(uint256,uint256,address)': '0x8878d06c',
    'locked(uint256)': '0xb45a3c0e',
    'ownerOf(uint256)': '0x6352211e',
}
TOPIC = {
    'NotifyReward': '0x52977ea98a2220a03ee9ba5cb003ada08d394ea10155483c95dc2dc77a7eb24b',
    'Transfer': '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
    'OrderFulfilled': '0x9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31',
}


# ---------------------------------------------------------------------------------------------- small helpers
def utc(ts):
    return dt.datetime.fromtimestamp(ts, UTC).strftime('%Y-%m-%d %H:%M')


def ymd(ts):
    return dt.datetime.fromtimestamp(ts, UTC).strftime('%Y-%m-%d')


def write_gz(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(obj, f)
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


def epoch_start(ts):
    return ts - ts % WEEK


def epochs_between(first, last_start):
    """Epoch starts from `first` (rounded down) to `last_start` inclusive."""
    e = epoch_start(first)
    out = []
    while e <= last_start:
        out.append(e)
        e += WEEK
    return out


def block_at(chain, ts):
    c = CHAINS[chain]
    return c['genesis_block'] + max(0, (ts - c['genesis_ts']) // 2)


def get_json(url, params=None, headers=None, retries=5, pause=0.3, timeout=60, data=None):
    if params:
        url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    last = None
    for a in range(retries):
        try:
            h = dict({'User-Agent': UA, 'Accept': 'application/json', 'Accept-Encoding': 'gzip'}, **(headers or {}))
            body_out = None
            if data is not None:
                body_out = json.dumps(data).encode()
                h['Content-Type'] = 'application/json'
            req = urllib.request.Request(url, data=body_out, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
                d = json.loads(body.decode())
            time.sleep(pause)
            return d
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code in (400, 404):
                return {'_http_error': e.code}
            wait = 60.0 if e.code in (418, 429) else pause * 2 ** (a + 1)
            time.sleep(min(wait, 90.0))
        except Exception as e:  # noqa: BLE001 - transport errors are retried, then raised with context
            last = repr(e)[:160]
            time.sleep(pause * 2 ** (a + 1))
    raise RuntimeError('%s: %s' % (url[:160], last))


# ---------------------------------------------------------------------------------------------- ABI
def enc_uint(v):
    return '%064x' % int(v)


def enc_addr(a):
    return a.lower().replace('0x', '').rjust(64, '0')


def cdata(sig, *args):
    """Call data for a function whose arguments are all static words (uint or address)."""
    out = SEL[sig]
    for a in args:
        out += enc_addr(a) if isinstance(a, str) else enc_uint(a)
    return out


def words(h):
    h = h[2:] if h.startswith('0x') else h
    return [int(h[i:i + 64], 16) for i in range(0, len(h) - len(h) % 64, 64)]


def dec_uint(h):
    if not h or h == '0x':
        return None
    return int(h[2:66], 16)


def dec_addr(h):
    if not h or h == '0x' or len(h) < 66:
        return None
    return '0x' + h[26:66].lower()


def dec_string(h):
    """ABI string, tolerating bytes32-returning tokens."""
    if not h or h == '0x':
        return None
    b = bytes.fromhex(h[2:])
    try:
        if len(b) >= 64:
            off = int.from_bytes(b[0:32], 'big')
            if off + 32 <= len(b):
                n = int.from_bytes(b[off:off + 32], 'big')
                if n <= 256 and off + 32 + n <= len(b):
                    return b[off + 32:off + 32 + n].decode('utf-8', 'replace')
        return b[:32].rstrip(b'\0').decode('utf-8', 'replace')
    except Exception:  # noqa: BLE001
        return None


def enc_aggregate3(calls):
    """aggregate3 with allowFailure=true for every (target, calldata) pair."""
    elems = []
    for target, data in calls:
        b = bytes.fromhex(data[2:] if data.startswith('0x') else data)
        pad = (32 - len(b) % 32) % 32
        elems.append(enc_addr(target) + enc_uint(1) + enc_uint(0x60) + enc_uint(len(b)) + (b + b'\0' * pad).hex())
    offs, pos = [], 32 * len(elems)
    for e in elems:
        offs.append(enc_uint(pos))
        pos += len(e) // 2
    return SEL['aggregate3((address,bool,bytes)[])'] + enc_uint(0x20) + enc_uint(len(elems)) + ''.join(offs) + ''.join(elems)


def dec_aggregate3(h):
    """Result[] -> list of '0x..' return data, or None where the inner call failed."""
    b = bytes.fromhex(h[2:] if h.startswith('0x') else h)

    def w(i):
        return int.from_bytes(b[i:i + 32], 'big')
    arr = w(0)
    n = w(arr)
    base = arr + 32
    out = []
    for k in range(n):
        eo = base + w(base + 32 * k)
        ok = w(eo)
        bo = eo + w(eo + 32)
        ln = w(bo)
        out.append(('0x' + b[bo + 32:bo + 32 + ln].hex()) if ok else None)
    return out


# ---------------------------------------------------------------------------------------------- RPC
class Chain:
    """Multicall3 reads over the repo's Infura client (key rotation, redaction), pinned to one block."""

    def __init__(self, chain, log_path=None, block=None, workers=6, chunk=350):
        from live_rpc import RPC
        self.name = chain
        self.c = CHAINS[chain]
        self.rpc = RPC(url=self.c['rpc'], log_path=log_path, max_credits=40_000_000, interval=.05)
        self.block = block
        self.workers, self.chunk = workers, chunk
        self.calls = 0
        self.failed = 0

    def head(self):
        b = self.rpc.call('eth_getBlockByNumber', ['latest', False])
        return int(b['number'], 16), int(b['timestamp'], 16)

    def call_retry(self, method, params, tries=8):
        """live_rpc retries quota errors itself; node faults such as -32603 'service temporarily unavailable'
        are raised at once, so they are retried here with backoff before anything is split or dropped."""
        last = None
        for a in range(tries):
            try:
                return self.rpc.call(method, params)
            except Exception as e:  # noqa: BLE001
                last = e
                msg = str(e).lower()
                if 'revert' in msg or 'out of gas' in msg or 'exceeds' in msg or 'too large' in msg or 'more than' in msg:
                    raise
                time.sleep(min(30.0, 1.5 * 2 ** a))
        raise last

    def _agg(self, part, block):
        data = enc_aggregate3(part)
        try:
            res = self.call_retry('eth_call', [{'to': MULTICALL3, 'data': data}, hex(block) if isinstance(block, int) else block])
            out = dec_aggregate3(res)
            if len(out) != len(part):
                raise ValueError('multicall length mismatch')
            return out
        except Exception:  # noqa: BLE001 - too large: split and retry; a single call that still fails is None
            if len(part) == 1:
                self.failed += 1
                return [None]
            h = len(part) // 2
            return self._agg(part[:h], block) + self._agg(part[h:], block)

    def multicall(self, calls, block=None, progress=None):
        block = block if block is not None else (self.block or 'latest')
        parts = [calls[i:i + self.chunk] for i in range(0, len(calls), self.chunk)]
        out = [None] * len(parts)
        done = [0]
        lock = threading.Lock()

        def run(i):
            out[i] = self._agg(parts[i], block)
            with lock:
                done[0] += 1
                if progress and done[0] % 50 == 0:
                    progress('  multicall %d/%d chunks' % (done[0], len(parts)))
        with cf.ThreadPoolExecutor(max_workers=self.workers) as ex:
            list(ex.map(run, range(len(parts))))
        self.calls += len(calls)
        return [x for p in out for x in p]

    def logs(self, address, topics, b0, b1, step=10_000):
        out = []
        b = b0
        while b <= b1:
            e = min(b1, b + step - 1)
            flt = {'topics': topics, 'fromBlock': hex(b), 'toBlock': hex(e)}
            if address:
                flt['address'] = address
            out.extend(self.rpc.call('eth_getLogs', [flt]))
            b = e + 1
        return out


# ---------------------------------------------------------------------------------------------- collect: registry
def collect_registry(out, chain, log):
    path = out / 'raw' / chain / 'registry.json.gz'
    if path.exists():
        log('registry: on disk')
        return read_gz(path)
    ch = Chain(chain, log_path=out / 'raw' / chain / 'rpc_errors.jsonl')
    head_block, head_ts = ch.head()
    ch.block = head_block
    c = ch.c
    n = dec_uint(ch.multicall([(c['voter'], cdata('length()'))])[0])
    log('registry: %d pools with gauges at block %d' % (n, head_block))
    pools = [dec_addr(x) for x in ch.multicall([(c['voter'], cdata('pools(uint256)', i)) for i in range(n)])]
    gauges = [dec_addr(x) for x in ch.multicall([(c['voter'], cdata('gauges(address)', p)) for p in pools])]
    calls = []
    for p, g in zip(pools, gauges):
        calls += [(c['voter'], cdata('gaugeToFees(address)', g)), (c['voter'], cdata('gaugeToBribe(address)', g)),
                  (c['voter'], cdata('isAlive(address)', g)), (p, cdata('token0()')), (p, cdata('token1()')),
                  (c['voter'], cdata('weights(address)', p))]
    res = ch.multicall(calls, progress=log)
    rows = []
    for i, (p, g) in enumerate(zip(pools, gauges)):
        r = res[6 * i:6 * i + 6]
        rows.append({'i': i, 'pool': p, 'gauge': g, 'fees': dec_addr(r[0]), 'bribe': dec_addr(r[1]),
                     'alive': bool(dec_uint(r[2])), 'token0': dec_addr(r[3]), 'token1': dec_addr(r[4]),
                     'weight_now': dec_uint(r[5]) or 0})
    # Reward contracts: token lists and checkpoint counts.
    rcs = [x for row in rows for x in (row['fees'], row['bribe']) if x]
    res = ch.multicall([(a, cdata(s)) for a in rcs for s in ('rewardsListLength()', 'supplyNumCheckpoints()')])
    meta = {}
    for k, a in enumerate(rcs):
        meta[a] = {'n_rewards': dec_uint(res[2 * k]) or 0, 'n_ckpt': dec_uint(res[2 * k + 1]) or 0}
    calls, keys = [], []
    for a, m in meta.items():
        for j in range(min(m['n_rewards'], 200)):
            calls.append((a, cdata('rewards(uint256)', j)))
            keys.append(a)
        if m['n_ckpt']:
            calls.append((a, cdata('supplyCheckpoints(uint256)', 0)))
            keys.append(('cp0', a))
    res = ch.multicall(calls, progress=log)
    for key, r in zip(keys, res):
        if isinstance(key, tuple):
            w = words(r) if r else [0, 0]
            meta[key[1]]['first_ckpt_ts'] = w[0]
        else:
            meta[key].setdefault('tokens', []).append(dec_addr(r))
    for row in rows:
        row['fees_meta'] = meta.get(row['fees'], {})
        row['bribe_meta'] = meta.get(row['bribe'], {})
    glob = ch.multicall([(c['ve'], cdata('supply()')), (c['ve'], cdata('totalSupply()')),
                         (c['ve'], cdata('permanentLockBalance()')), (c['voter'], cdata('totalWeight()'))])
    reg = {'chain': chain, 'block': head_block, 'ts': head_ts, 'n_pools': n, 'pools': rows,
           'now': {'ve_locked': dec_uint(glob[0]), 've_power': dec_uint(glob[1]),
                   've_permanent': dec_uint(glob[2]), 'total_weight': dec_uint(glob[3])},
           'rpc': ch.rpc.stats()}
    write_gz(path, reg)
    log('registry: %d reward contracts, %d with votes, %d token slots' % (
        len(meta), sum(1 for m in meta.values() if m['n_ckpt']), sum(m['n_rewards'] for m in meta.values())))
    return reg


# ---------------------------------------------------------------------------------------------- collect: epochs
def reward_contracts(reg):
    """(pool index, kind, contract, tokens, first epoch) for every reward contract that ever had a vote."""
    out = []
    for row in reg['pools']:
        for kind in ('fees', 'bribe'):
            a, m = row[kind], row[kind + '_meta']
            if not a or not m.get('n_ckpt'):
                continue
            out.append((row['i'], kind, a, [t for t in m.get('tokens', []) if t], epoch_start(m.get('first_ckpt_ts') or 0)))
    return out


def collect_epochs(out, chain, log):
    """Per-epoch reward amounts, votes at end / T-24h / T-1h, ve supply and rebase, read from current state."""
    reg = collect_registry(out, chain, log)
    c = CHAINS[chain]
    base = out / 'raw' / chain
    cur = epoch_start(reg['ts'])
    eps = epochs_between(c['first_epoch'], cur)       # the last one is in progress at collection time
    ch = Chain(chain, log_path=base / 'rpc_errors.jsonl', block=reg['block'])

    # 1. global per epoch: ve voting supply at the end of the epoch, rebase tokensPerWeek, ve supply at the start.
    p = base / 'global.json.gz'
    if not p.exists():
        calls = []
        for e in eps:
            calls += [(c['ve'], cdata('totalSupplyAt(uint256)', min(e + WEEK - 1, reg['ts']))),
                      (c['dist'], cdata('tokensPerWeek(uint256)', e))]
        res = ch.multicall(calls)
        g = [{'epoch': e, 've_power_end': dec_uint(res[2 * k]), 'rebase_tokens': dec_uint(res[2 * k + 1])} for k, e in enumerate(eps)]
        write_gz(p, g)
        log('global: %d epochs' % len(g))

    # 2. votes per pool per epoch (bribe contract supply; fee contract supply is identical by construction).
    p = base / 'votes.json.gz'
    if not p.exists():
        rcs = [x for x in reward_contracts(reg) if x[1] == 'bribe']
        offsets = (('end', WEEK - 1), ('t24', WEEK - DAY), ('t1', WEEK - HOUR - 60), ('start', 3600))
        jobs = []
        for (i, kind, a, toks, e0) in rcs:
            for e in eps:
                if e < e0:
                    continue
                for name, off in offsets:
                    t = e + off
                    if t > reg['ts']:
                        continue
                    jobs.append((i, e, name, a, t))
        log('votes: %d index reads' % len(jobs))
        idx = ch.multicall([(a, cdata('getPriorSupplyIndex(uint256)', t)) for (_, _, _, a, t) in jobs], progress=log)
        res = ch.multicall([(a, cdata('supplyCheckpoints(uint256)', dec_uint(x) or 0)) for (_, _, _, a, _), x in zip(jobs, idx)], progress=log)
        votes = {}
        bad = 0
        for (i, e, name, a, t), x, r in zip(jobs, idx, res):
            if x is None or r is None:
                v = None
                bad += 1
            else:
                w = words(r)
                v = w[1] if (len(w) >= 2 and w[0] <= t) else 0
            votes.setdefault(str(i), {}).setdefault(str(e), {})[name] = v
        write_gz(p, votes)
        log('votes: %d pools, %d failed reads (kept as null)' % (len(votes), bad))

    # 3. reward amounts per contract, token and epoch.
    p = base / 'rewards.json.gz'
    if not p.exists():
        jobs = []
        for (i, kind, a, toks, e0) in reward_contracts(reg):
            for t in toks:
                for e in eps:
                    if e >= e0:
                        jobs.append((i, kind, a, t, e))
        log('rewards: %d reads' % len(jobs))
        res = ch.multicall([(a, cdata('tokenRewardsPerEpoch(address,uint256)', t, e)) for (_, _, a, t, e) in jobs], progress=log)
        rw = []
        failed = 0
        for (i, kind, a, t, e), r in zip(jobs, res):
            v = dec_uint(r)
            if v is None:
                failed += 1
            elif v:
                rw.append([i, kind, t, e, str(v)])
        write_gz(p, {'rows': rw, 'failed': failed, 'reads': len(jobs)})
        log('rewards: %d nonzero, %d failed reads' % (len(rw), failed))

    # 4. token metadata for every token that paid something.
    p = base / 'tokens.json.gz'
    if not p.exists():
        rw = read_gz(base / 'rewards.json.gz')['rows']
        toks = sorted({r[2] for r in rw} | {c['token'].lower()})
        res = ch.multicall([(t, cdata(s)) for t in toks for s in ('decimals()', 'symbol()')])
        meta = {t: {'decimals': dec_uint(res[2 * k]), 'symbol': dec_string(res[2 * k + 1])} for k, t in enumerate(toks)}
        write_gz(p, meta)
        log('tokens: %d' % len(meta))
    return True




def verify_votes(out, chain, log, n=20000, seed=11):
    """Re-read a random sample of the stored vote reads at the registry block and count disagreements."""
    import random
    reg = read_gz(out / 'raw' / chain / 'registry.json.gz')
    votes = read_gz(out / 'raw' / chain / 'votes.json.gz')
    bribe = {str(r['i']): r['bribe'] for r in reg['pools']}
    offs = {'end': WEEK - 1, 't24': WEEK - DAY, 't1': WEEK - HOUR - 60, 'start': 3600}
    keys = [(i, e, k) for i, per in votes.items() for e, d in per.items() for k in d]
    rng = random.Random(seed)
    sample = rng.sample(keys, min(n, len(keys)))
    ch = Chain(chain, log_path=out / 'raw' / chain / 'rpc_errors.jsonl', block=reg['block'])
    jobs = [(i, e, k, bribe[i], int(e) + offs[k]) for i, e, k in sample]
    idx = ch.multicall([(a, cdata('getPriorSupplyIndex(uint256)', t)) for (_, _, _, a, t) in jobs])
    res = ch.multicall([(a, cdata('supplyCheckpoints(uint256)', dec_uint(x) or 0)) for (_, _, _, a, _), x in zip(jobs, idx)])
    bad, failed, nulls = [], 0, 0
    for (i, e, k, a, t), x, r in zip(jobs, idx, res):
        if x is None or r is None:
            failed += 1
            continue
        w = words(r)
        v = w[1] if (len(w) >= 2 and w[0] <= t) else 0
        stored = votes[i][e][k]
        if stored is None:
            nulls += 1
        elif stored != v:
            bad.append([i, e, k, stored, v])
    nulls_all = sum(1 for i, per in votes.items() for e, d in per.items() for kk, vv in d.items() if vv is None)
    resd = {'sampled': len(jobs), 'mismatches': len(bad), 'failed_rereads': failed, 'stored_nulls_in_sample': nulls,
            'stored_nulls_total': nulls_all, 'examples': bad[:10]}
    write_gz(out / 'raw' / chain / 'votes_verify.json.gz', resd)
    log('verify votes: %s' % {k: v for k, v in resd.items() if k != 'examples'})
    return resd


# ---------------------------------------------------------------------------------------------- collect: perps
BN = 'https://fapi.binance.com'
BY = 'https://api.bybit.com'
OKX = 'https://www.okx.com'
HL = 'https://api.hyperliquid.xyz/info'


def _paged_forward(fetch, start_ms, end_ms, key, limit, step_floor=1):
    """Generic forward pagination on a millisecond time key."""
    rows, t = [], start_ms
    while t < end_ms:
        page = fetch(t)
        if not page:
            break
        rows.extend(page)
        last = max(int(r[key] if isinstance(r, dict) else r[key]) for r in page)
        if last + step_floor <= t or len(page) < limit:
            break
        t = last + step_floor
    return rows


def collect_perps(out, log):
    d = out / 'raw' / 'perps'
    d.mkdir(parents=True, exist_ok=True)
    now_ms = int(time.time() * 1000)

    def save(name, obj):
        write_gz(d / (name + '.json.gz'), obj)

    def have(name):
        return (d / (name + '.json.gz')).exists()

    # Binance USD-M: AEROUSDT and VELODROMEUSDT (Binance's ticker for Velodrome's VELO).
    info = get_json(BN + '/fapi/v1/exchangeInfo')
    finfo = get_json(BN + '/fapi/v1/fundingInfo')
    save('binance_fundingInfo', [x for x in finfo if x.get('symbol') in ('AEROUSDT', 'VELODROMEUSDT')])
    for sym in ('AEROUSDT', 'VELODROMEUSDT'):
        meta = next((s for s in info['symbols'] if s['symbol'] == sym), None)
        if not meta:
            log('binance: %s not listed' % sym)
            continue
        onboard = int(meta['onboardDate'])
        if not have('binance_%s_funding' % sym):
            rows = _paged_forward(lambda t: get_json(BN + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': t, 'limit': 1000}),
                                  onboard - DAY * 1000, now_ms, 'fundingTime', 1000)
            save('binance_%s_funding' % sym, rows)
            log('binance %s funding: %d' % (sym, len(rows)))
        for kind, path, extra in (('klines', '/fapi/v1/klines', {'symbol': sym}),
                                  ('index', '/fapi/v1/indexPriceKlines', {'pair': sym}),
                                  ('mark', '/fapi/v1/markPriceKlines', {'symbol': sym})):
            if have('binance_%s_%s_1d' % (sym, kind)):
                continue
            rows = _paged_forward(lambda t: get_json(BN + path, dict(extra, interval='1d', startTime=t, limit=1500)),
                                  onboard - DAY * 1000, now_ms, 0, 1500, DAY * 1000)
            save('binance_%s_%s_1d' % (sym, kind), rows)
        save('binance_%s_oi_hist' % sym, get_json(BN + '/futures/data/openInterestHist', {'symbol': sym, 'period': '1d', 'limit': 30}))
        save('binance_%s_depth' % sym, get_json(BN + '/fapi/v1/depth', {'symbol': sym, 'limit': 1000}))
        save('binance_%s_ticker' % sym, get_json(BN + '/fapi/v1/ticker/24hr', {'symbol': sym}))
        save('binance_%s_premium' % sym, get_json(BN + '/fapi/v1/premiumIndex', {'symbol': sym}))
        save('binance_%s_oi' % sym, get_json(BN + '/fapi/v1/openInterest', {'symbol': sym}))
        log('binance %s: klines, depth, oi' % sym)

    # Bybit linear: AEROUSDT (4-hour funding) and VELOUSDT (checked for identity: Bybit's VELO is Velo, not Velodrome).
    for sym in ('AEROUSDT', 'VELOUSDT'):
        inst = get_json(BY + '/v5/market/instruments-info', {'category': 'linear', 'symbol': sym})
        lst = (inst.get('result') or {}).get('list') or []
        if not lst:
            continue
        launch = int(lst[0]['launchTime'])
        save('bybit_%s_instrument' % sym, lst[0])
        save('bybit_%s_ticker' % sym, get_json(BY + '/v5/market/tickers', {'category': 'linear', 'symbol': sym}))
        if sym != 'AEROUSDT':
            continue
        if not have('bybit_AEROUSDT_funding'):
            rows, end = [], now_ms
            while True:
                r = get_json(BY + '/v5/market/funding/history', {'category': 'linear', 'symbol': sym, 'endTime': end, 'limit': 200})
                page = (r.get('result') or {}).get('list') or []
                if not page:
                    break
                rows.extend(page)
                first = min(int(x['fundingRateTimestamp']) for x in page)
                if first <= launch or len(page) < 200:
                    break
                end = first - 1
            save('bybit_AEROUSDT_funding', rows)
            log('bybit AEROUSDT funding: %d' % len(rows))
        for kind, path in (('klines', '/v5/market/kline'), ('index', '/v5/market/index-price-kline'), ('mark', '/v5/market/mark-price-kline')):
            if have('bybit_AEROUSDT_%s_1d' % kind):
                continue
            rows, end = [], now_ms
            while True:
                r = get_json(BY + path, {'category': 'linear', 'symbol': sym, 'interval': 'D', 'end': end, 'limit': 1000})
                page = (r.get('result') or {}).get('list') or []
                if not page:
                    break
                rows.extend(page)
                first = min(int(x[0]) for x in page)
                if first <= launch or len(page) < 1000:
                    break
                end = first - 1
            save('bybit_AEROUSDT_%s_1d' % kind, rows)
        if not have('bybit_AEROUSDT_oi_1d'):
            rows, cursor = [], None
            for _ in range(40):
                params = {'category': 'linear', 'symbol': sym, 'intervalTime': '1d', 'limit': 200, 'startTime': launch, 'endTime': now_ms}
                if cursor:
                    params['cursor'] = cursor
                r = get_json(BY + '/v5/market/open-interest', params)
                res = r.get('result') or {}
                rows.extend(res.get('list') or [])
                cursor = res.get('nextPageCursor')
                if not cursor:
                    break
            save('bybit_AEROUSDT_oi_1d', rows)
        save('bybit_AEROUSDT_book', get_json(BY + '/v5/market/orderbook', {'category': 'linear', 'symbol': sym, 'limit': 500}))
        save('bybit_AEROUSDT_spot_book', get_json(BY + '/v5/market/orderbook', {'category': 'spot', 'symbol': sym, 'limit': 200}))
        save('bybit_AEROUSDT_spot_ticker', get_json(BY + '/v5/market/tickers', {'category': 'spot', 'symbol': sym}))
        log('bybit AEROUSDT: klines, oi, books')

    # OKX AERO-USDT-SWAP (contract value 10 AERO).
    inst = 'AERO-USDT-SWAP'
    save('okx_instrument', get_json(OKX + '/api/v5/public/instruments', {'instType': 'SWAP', 'instId': inst}))
    if not have('okx_funding'):
        rows, after = [], None
        for _ in range(60):
            params = {'instId': inst, 'limit': 400}
            if after:
                params['after'] = after
            r = get_json(OKX + '/api/v5/public/funding-rate-history', params, pause=0.4)
            page = r.get('data') or []
            if not page:
                break
            rows.extend(page)
            after = min(int(x['fundingTime']) for x in page)
        save('okx_funding', rows)
        log('okx funding: %d' % len(rows))
    if not have('okx_klines_1d'):
        rows, after = [], None
        for _ in range(30):
            params = {'instId': inst, 'bar': '1Dutc', 'limit': 100}
            if after:
                params['after'] = after
            r = get_json(OKX + '/api/v5/market/history-candles', params, pause=0.4)
            page = r.get('data') or []
            if not page:
                break
            rows.extend(page)
            after = min(int(x[0]) for x in page)
        save('okx_klines_1d', rows)
    save('okx_oi', get_json(OKX + '/api/v5/public/open-interest', {'instType': 'SWAP', 'instId': inst}))
    save('okx_oi_hist', get_json(OKX + '/api/v5/rubik/stat/contracts/open-interest-history', {'instId': inst, 'period': '1D'}))
    save('okx_book', get_json(OKX + '/api/v5/market/books', {'instId': inst, 'sz': 400}))
    save('okx_ticker', get_json(OKX + '/api/v5/market/ticker', {'instId': inst}))
    log('okx: klines, oi, book')

    # Hyperliquid AERO perp, paced at >= 4 s a call (other workers share the IP).
    def hl(body):
        r = get_json(HL, data=body, pause=4.0)
        return r
    if not have('hl_funding'):
        rows, t = [], 1672531200000
        for _ in range(80):
            page = hl({'type': 'fundingHistory', 'coin': 'AERO', 'startTime': t})
            if not isinstance(page, list) or not page:
                break
            rows.extend(page)
            last = max(int(x['time']) for x in page)
            if len(page) < 500:
                break
            t = last + 1
        save('hl_funding', rows)
        log('hl funding: %d' % len(rows))
    if not have('hl_candles_1d'):
        save('hl_candles_1d', hl({'type': 'candleSnapshot', 'req': {'coin': 'AERO', 'interval': '1d', 'startTime': 1672531200000, 'endTime': now_ms}}))
    ctx = hl({'type': 'metaAndAssetCtxs'})
    try:
        names = [u['name'] for u in ctx[0]['universe']]
        k = names.index('AERO')
        save('hl_ctx', {'meta': ctx[0]['universe'][k], 'ctx': ctx[1][k]})
    except Exception as e:  # noqa: BLE001
        log('hl ctx: %r' % e)
    for sf in (5, 4, 3):
        save('hl_book_sf%d' % sf, hl({'type': 'l2Book', 'coin': 'AERO', 'nSigFigs': sf}))
    log('hl: candles, ctx, books')

    # Coinbase spot AERO-USD (the deepest spot venue for AERO): daily candles and the book.
    if not have('coinbase_candles_1d'):
        rows, end = [], int(time.time())
        for _ in range(12):
            start = end - 300 * DAY
            r = get_json('https://api.exchange.coinbase.com/products/AERO-USD/candles',
                         {'granularity': 86400, 'start': dt.datetime.fromtimestamp(start, UTC).isoformat(),
                          'end': dt.datetime.fromtimestamp(end, UTC).isoformat()}, pause=0.5)
            if not isinstance(r, list) or not r:
                break
            rows.extend(r)
            end = start
        save('coinbase_candles_1d', rows)
    save('coinbase_book', get_json('https://api.exchange.coinbase.com/products/AERO-USD/book', {'level': 2}))
    log('coinbase: candles, book')
    # exit markets: iAERO pools (GeckoTerminal public API)
    save('gt_iaero_pools', get_json('https://api.geckoterminal.com/api/v2/networks/base/tokens/%s/pools' % IAERO, pause=2.0))
    log('geckoterminal: iAERO pools')



# ---------------------------------------------------------------------------------------------- collect: logs
CHECK_EPOCHS = (1716422400, 1747872000, 1784160000)   # 2024-05-23, 2025-05-22, 2026-07-16: full-week event checks


def _log_chunks(chain, b0, b1, step=10_000):
    out, b = [], b0
    while b <= b1:
        out.append((b, min(b1, b + step - 1)))
        b += step
    return out


def fetch_logs_parallel(ch, address, topics, chunks, workers=6, progress=None):
    res = [None] * len(chunks)
    done = [0]
    lock = threading.Lock()

    def get(b0, b1):
        flt = {'topics': topics, 'fromBlock': hex(b0), 'toBlock': hex(b1)}
        if address:
            flt['address'] = address
        try:
            return ch.call_retry('eth_getLogs', [flt])
        except Exception as e:  # noqa: BLE001 - more than 10,000 results: halve the range
            if 'more than' in str(e) and b1 > b0:
                mid = (b0 + b1) // 2
                return get(b0, mid) + get(mid + 1, b1)
            raise

    def run(k):
        b0, b1 = chunks[k]
        res[k] = get(b0, b1)
        with lock:
            done[0] += 1
            if progress and done[0] % 200 == 0:
                progress('  logs %d/%d chunks' % (done[0], len(chunks)))
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(run, range(len(chunks))))
    return [x for r in res for x in r]


def slim_notify(lg):
    return [lg['address'].lower(), '0x' + lg['topics'][2][26:], int(lg['topics'][3], 16), str(int(lg['data'][:66], 16)),
            int(lg['blockNumber'], 16), lg['transactionHash']]


def collect_logs(out, chain, log):
    """NotifyReward in the last 24 h of each epoch, and over three full sample weeks."""
    reg = collect_registry(out, chain, log)
    base = out / 'raw' / chain
    ch = Chain(chain, log_path=base / 'rpc_errors.jsonl')
    ours = {x for row in reg['pools'] for x in (row['fees'], row['bribe']) if x}
    cur = epoch_start(reg['ts'])
    p = base / 'notify_last24h.json.gz'
    if not p.exists():
        eps = [e for e in epochs_between(CHAINS[chain]['first_epoch'], cur) if e + WEEK <= reg['ts']]
        chunks = []
        for e in eps:
            f = e + WEEK
            chunks += _log_chunks(chain, block_at(chain, f - DAY), block_at(chain, f) - 1)
        logs = fetch_logs_parallel(ch, None, [TOPIC['NotifyReward']], chunks, progress=log)
        rows = [slim_notify(lg) for lg in logs if lg['address'].lower() in ours]
        write_gz(p, {'epochs': eps, 'rows': rows, 'n_all': len(logs)})
        log('notify last 24h: %d of ours (of %d)' % (len(rows), len(logs)))
    p = base / 'notify_checkweeks.json.gz'
    if not p.exists():
        chunks = []
        for e in CHECK_EPOCHS:
            chunks += _log_chunks(chain, block_at(chain, e), block_at(chain, e + WEEK) - 1)
        logs = fetch_logs_parallel(ch, None, [TOPIC['NotifyReward']], chunks, progress=log)
        rows = [slim_notify(lg) for lg in logs if lg['address'].lower() in ours]
        write_gz(p, {'epochs': list(CHECK_EPOCHS), 'rows': rows, 'n_all': len(logs)})
        log('notify check weeks: %d of ours' % len(rows))
    p = base / 'sugar_check.json.gz'
    if not p.exists():
        top = sorted([r for r in reg['pools'] if r['alive']], key=lambda r: -r['weight_now'])[:6]
        ch.block = reg['block']
        res = ch.multicall([(CHAINS[chain]['rewards_sugar'], SEL['epochsByAddress(uint256,uint256,address)'] + enc_uint(10) + enc_uint(1) + enc_addr(r['pool'])) for r in top])
        write_gz(p, {r['pool']: h for r, h in zip(top, res)})
        log('sugar check: %d pools' % sum(1 for h in res if h))


# ---------------------------------------------------------------------------------------------- collect: veNFT sales
SEAPORT = {'0x00000000000000adc04c56bf30ac9d3c0aaf14dc', '0x0000000000000068f116a894984e2db1123eb395',
           '0x00000000006c3852cbef3e08e8df289169ede581'}
ZERO_T = '0x' + '0' * 64


def collect_sales(out, chain, log):
    """veNFT transfers between two non-zero addresses, their receipts, and the lock at the block before."""
    reg = collect_registry(out, chain, log)
    c = CHAINS[chain]
    base = out / 'raw' / chain
    ch = Chain(chain, log_path=base / 'rpc_errors.jsonl')
    p = base / 've_transfers.json.gz'
    if not p.exists():
        b0 = block_at(chain, c['first_epoch'])
        chunks = _log_chunks(chain, b0, reg['block'])
        logs = fetch_logs_parallel(ch, c['ve'], [TOPIC['Transfer']], chunks, workers=8, progress=log)
        rows = [['0x' + lg['topics'][1][26:], '0x' + lg['topics'][2][26:], int(lg['topics'][3], 16), int(lg['blockNumber'], 16),
                 lg['transactionHash']] for lg in logs]
        write_gz(p, rows)
        log('ve transfers: %d' % len(rows))
    rows = read_gz(p)
    zero = '0x' + '0' * 40
    cand = [r for r in rows if r[0] != zero and r[1] != zero]
    txs = sorted({r[4] for r in cand})
    log('ve transfers between non-zero addresses: %d in %d txs' % (len(cand), len(txs)))
    p = base / 've_receipts.json.gz'
    have = read_gz(p) if p.exists() else {}
    todo = [t for t in txs if t not in have]
    if todo:
        def fetch(part):
            return ch.rpc.batch([('eth_getTransactionReceipt', [t]) for t in part], allow_errors=True)
        parts = [todo[i:i + 20] for i in range(0, len(todo), 20)]
        for k in range(0, len(parts), 60):
            with cf.ThreadPoolExecutor(max_workers=6) as ex:
                res = list(ex.map(fetch, parts[k:k + 60]))
            for part, rr in zip(parts[k:k + 60], res):
                for t, rc in zip(part, rr):
                    if isinstance(rc, dict) and 'logs' in rc:
                        have[t] = {'from': rc.get('from'), 'to': rc.get('to'), 'block': int(rc['blockNumber'], 16),
                                   'logs': [[lg['address'].lower(), lg['topics'], lg['data']] for lg in rc['logs']
                                            if lg['topics'] and (lg['address'].lower() in SEAPORT or lg['topics'][0] == TOPIC['Transfer'])]}
            write_gz(p, have)
            log('  receipts %d/%d' % (len(have), len(txs)))
    # Lock state at the block before each material sale (archive eth_call): every payment >= $10k, Seaport >= $1k,
    # and a fixed random sample of 500 of the $1k-10k ERC20 payments (the rest are priced but not valued).
    import random
    p2 = base / 've_locks_at_transfer.json.gz'
    locks = read_gz(p2) if p2.exists() else {}
    pr = Prices(read_gz(base / 'prices.json.gz'), c['llama'])

    def tpx(day):
        return pr.get(c['token'].lower(), day)[0]
    big, mid = [], []
    for r in cand:
        rc = have.get(r[4])
        if not rc:
            continue
        ts = c['genesis_ts'] + 2 * (r[3] - c['genesis_block'])
        sp = sale_payment(rc, r[0], r[1], r[2], c['ve'].lower(), chain, ts - ts % DAY, tpx, pr)
        if not sp:
            continue
        if sp[1] >= 1e4 or (sp[0].startswith('seaport') and sp[1] >= 1e3):
            big.append(r)
        elif sp[1] >= 1e3:
            mid.append(r)
    rng = random.Random(5)
    sale_like = big + rng.sample(mid, min(500, len(mid)))
    log('material sales: %d (>= $10k or Seaport >= $1k) + %d sampled of %d in $1k-10k' % (len(big), min(500, len(mid)), len(mid)))
    write_gz(base / 've_sales_selection.json.gz', {'big': len(big), 'mid': len(mid), 'sampled': min(500, len(mid))})
    todo = [r for r in sale_like if '%d:%d' % (r[2], r[3]) not in locks]

    def lock_at(r):
        # read at the block before the transfer: the lock the buyer paid for
        return '%d:%d' % (r[2], r[3]), ch.call_retry('eth_call', [{'to': c['ve'], 'data': cdata('locked(uint256)', r[2])}, hex(r[3] - 1)])
    for k in range(0, len(todo), 300):
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            for key, res in ex.map(lock_at, todo[k:k + 300]):
                locks[key] = res
        write_gz(p2, locks)
        log('  lock states %d/%d' % (min(k + 300, len(todo)), len(todo)))
    log('sale-like transfers: %d; lock states: %d' % (len(sale_like), len(locks)))



# ---------------------------------------------------------------------------------------------- collect: prices
LLAMA = 'https://coins.llama.fi'
IAERO = '0x81034fb34009115f215f5d5f564aac9ffa46a1dc'   # docs.iaero.finance contract-addresses.md, read 2026-10-10
SALE_LAG = DAY                    # rewards are priced one day after the flip that makes them claimable
DECISION_LAG = -DAY               # what a voter could see when deciding: the price a day before the flip


def price_lookups(rew_rows, c):
    """{coin: sorted timestamps} for claim-time and decision-time prices of every token-epoch that paid."""
    want = {}
    for i, kind, t, e, amt in rew_rows:
        f = e + WEEK
        want.setdefault(t, set()).update((f + SALE_LAG, f + DECISION_LAG))
    return {('%s:%s' % (c['llama'], t)): sorted(v) for t, v in want.items()}


def collect_prices(out, chain, log, max_lookups=380):
    c = CHAINS[chain]
    base = out / 'raw' / chain
    p = base / 'prices.json.gz'
    have = read_gz(p) if p.exists() else {}
    rew = read_gz(base / 'rewards.json.gz')['rows']
    want = price_lookups(rew, c)
    now = int(time.time())
    # the token itself: daily from the first epoch, for the hedge and the capital
    tok = '%s:%s' % (c['llama'], c['token'].lower())
    want.setdefault(tok, [])
    want[tok] = sorted(set(want[tok]) | set(range(epoch_start(c['first_epoch']), now - DAY, DAY)))
    weth = '%s:0x4200000000000000000000000000000000000006' % c['llama']
    want[weth] = sorted(set(want.get(weth, [])) | set(range(epoch_start(c['first_epoch']), now - DAY, DAY)))
    if chain == 'base':                  # iAERO: a liquid receipt for permanently locked veAERO (5% mint fee)
        want['base:' + IAERO] = sorted(set(range(1748736000, now - DAY, DAY)))
    todo = []
    for coin, tss in want.items():
        got = have.get(coin, {})
        for ts in tss:
            if ts <= now - 600 and str(ts) not in got:
                todo.append((coin, ts))
    log('prices: %d lookups to do (%d coins)' % (len(todo), len(want)))
    calls = 0
    while todo:
        batch, rest, size = {}, [], 0
        for coin, ts in todo:
            if size < max_lookups and (len(batch) < 60 or coin in batch):
                batch.setdefault(coin, []).append(ts)
                size += 1
            else:
                rest.append((coin, ts))
        q = urllib.parse.quote(json.dumps(batch, separators=(',', ':')))
        r = get_json(LLAMA + '/batchHistorical?coins=' + q + '&searchWidth=6h', pause=1.2)
        coins = r.get('coins') or {}
        for coin, tss in batch.items():
            pts = (coins.get(coin) or {}).get('prices') or []
            got = have.setdefault(coin, {})
            # match each requested timestamp to the nearest returned point within the search width
            for ts in tss:
                best = None
                for pt in pts:
                    dtt = abs(int(pt['timestamp']) - ts)
                    if dtt <= 6 * HOUR and (best is None or dtt < best[0]):
                        best = (dtt, pt)
                got[str(ts)] = [best[1]['price'], best[1].get('confidence')] if best else None
        todo = rest
        calls += 1
        if calls % 25 == 0:
            write_gz(p, have)
            log('  prices: %d calls, %d left' % (calls, len(todo)))
    write_gz(p, have)
    log('prices: done, %d coins' % len(have))



# ---------------------------------------------------------------------------------------------- core math (tested)
MAX_VOTE_POOLS = 30               # Voter.maxVotingNum on Aerodrome


def water_fill(pools, M, k_max=MAX_VOTE_POOLS, vfloor=1.0, iters=80):
    """Split M votes over pools {key: (R_hat, V_hat)} to maximise sum R_hat * v / (V_hat + v).

    The objective is concave in each v; at the optimum every funded pool has the same marginal reward
    R V / (V + v)^2 = lam, so v = sqrt(R V / lam) - V. lam is found by bisection so that the votes add up to M;
    if more than k_max pools are funded, the k_max largest allocations are kept and the split is solved again.
    V_hat is floored at `vfloor` votes so an unvoted pool with a reward gets a finite allocation.
    """
    items = [(k, r, max(v, vfloor)) for k, (r, v) in pools.items() if r > 0]
    if not items or M <= 0:
        return {}

    def solve(its):
        def tot(lam):
            return sum(max(0.0, math.sqrt(r * v / lam) - v) for _, r, v in its)
        hi = max(r / v for _, r, v in its)            # at lam >= max R/V nothing is funded
        lo = hi
        while tot(lo) < M:
            lo /= 4.0
            if lo < 1e-300:
                break
        for _ in range(iters):
            mid = math.sqrt(lo * hi)
            if tot(mid) > M:
                lo = mid
            else:
                hi = mid
        lam = math.sqrt(lo * hi)
        al = {k: max(0.0, math.sqrt(r * v / lam) - v) for k, r, v in its}
        s = sum(al.values())
        return {k: x * M / s for k, x in al.items() if x > 0} if s > 0 else {}
    al = solve(items)
    if len(al) > k_max:
        keep = set(sorted(al, key=lambda k: -al[k])[:k_max])
        al = solve([it for it in items if it[0] in keep])
    return al


def realized_reward(alloc, R, V_end):
    """What the allocation earns: each pool's reward shared pro rata with the votes there at the end, mine added."""
    tot = 0.0
    for k, v in alloc.items():
        if v <= 0:
            continue
        tot += R.get(k, 0.0) * v / (V_end.get(k, 0.0) + v)
    return tot


def avg_vote_reward(R_tot, V_tot, M):
    """Voting like the average voter (pro rata to existing votes) with own dilution: R M / (V + M)."""
    return R_tot * M / (V_tot + M) if V_tot + M > 0 else 0.0


def bucket_by_epoch(ts_values, first_epoch, n_epochs):
    """Sum (ts, value) pairs into epochs (s, s + WEEK]: a settlement at the flip belongs to the epoch it ends."""
    out = [0.0] * n_epochs
    cnt = [0] * n_epochs
    for ts, v in ts_values:
        k = int(math.ceil((ts - first_epoch) / WEEK)) - 1
        if 0 <= k < n_epochs:
            out[k] += v
            cnt[k] += 1
    return out, cnt


def epoch_carry(rpv_usd, rebase_tok, p_start, p_end, funding_usd, basis_start, basis_end, m,
                taker=0.0005, reward_sale_cost=0.0):
    """One epoch of the hedged lock, per locked token: (carry in USD, capital in USD, return on capital).

    carry = rewards per vote (sold) + rebase tokens at the end price - taker fee to add the rebase to the short
          + funding received by the short - the change in the perp's basis over the index (the short loses when the
            perp richens against the spot the lock is worth).
    capital = (1 + m) x the token price at the start: the token bought and locked, and the short's margin m.
    """
    carry = (rpv_usd * (1.0 - reward_sale_cost) + rebase_tok * p_end * (1.0 - taker) + funding_usd
             - (basis_end - basis_start))
    cap = (1.0 + m) * p_start
    return carry, cap, (carry / cap if cap > 0 else None)


def breakeven_discount(excess_on_capital, m):
    """Exit discount (on the lock's underlying value) that N epochs of excess carry pay for, price unchanged."""
    return sum(excess_on_capital) * (1.0 + m)


def annuity_value(net_yield, rate):
    """Value per unit of notional of a perpetual net carry `net_yield` a year discounted at `rate`."""
    return net_yield / rate if rate > 0 else float('inf')


def sale_discount(price_usd, locked_tokens, token_price):
    value = locked_tokens * token_price
    return (1.0 - price_usd / value) if value > 0 else None


def dec_order_fulfilled(topics, data):
    """Seaport OrderFulfilled -> (offerer, recipient, offer[(type, token, id, amount)], consideration[(type, token, id, amount, recipient)])."""
    b = bytes.fromhex(data[2:] if data.startswith('0x') else data)

    def w(i):
        return int.from_bytes(b[i:i + 32], 'big')
    offerer = '0x' + topics[1][26:]
    recipient = '0x' + b[32 + 12:64].hex()
    oo, co = w(64), w(96)
    offer = []
    n = w(oo)
    for k in range(n):
        q = oo + 32 + 128 * k
        offer.append((w(q), '0x' + b[q + 32 + 12:q + 64].hex(), w(q + 64), w(q + 96)))
    cons = []
    n = w(co)
    for k in range(n):
        q = co + 32 + 160 * k
        cons.append((w(q), '0x' + b[q + 32 + 12:q + 64].hex(), w(q + 64), w(q + 96), '0x' + b[q + 128 + 12:q + 160].hex()))
    return offerer, recipient, offer, cons


def dec_locked(h):
    """VotingEscrow.locked(id) -> (amount tokens as int, end, isPermanent)."""
    if not h or h == '0x' or len(h) < 2 + 64 * 3:
        return None
    w = words(h)
    amt = w[0] - (1 << 256) if w[0] >= (1 << 255) else w[0]
    return amt, w[1], bool(w[2])



# ---------------------------------------------------------------------------------------------- analysis: valuation
MAJORS = {
    'base': {
        '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913': 'USDC', '0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca': 'USDbC',
        '0x50c5725949a6f0c72e6c4a641f24049a917db0cb': 'DAI', '0xfde4c96c8593536e31f229ea8f37b2ada2699bb2': 'USDT',
        '0x60a3e35cc302bfa44cb288bc5a4f316fdb1adb42': 'EURC', '0x4200000000000000000000000000000000000006': 'WETH',
        '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf': 'cbBTC', '0x2ae3f1ec7f1f5012cfeab0185bfc7aa3cf0dec22': 'cbETH',
        '0xc1cba3fcea344f92d9239c08c0568f6f2f0ee452': 'wstETH', '0x04c0599ae5a44757c0af6f9ec3b93da8976c150a': 'weETH',
        '0x2416092f143378750bb29b79ed961ab195cceea5': 'ezETH', '0x940181a94a35a4569e4529a3cdfb74e38fd98631': 'AERO',
        '0x820c137fa70c8691f0e44dc420a5e53c168921dc': 'USDS', '0x5875eee11cf8398102fdad704c9e96607675467a': 'sUSDS',
        '0x236aa50979d5f3de3bd1eeb40e81137f22ab794b': 'tBTC', '0xecac9c5f704e954931349da37f60e39f515c11c1': 'LBTC',
        '0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b': 'VIRTUAL',
    },
    'optimism': {
        '0x0b2c639c533813f4aa9d7837caf62653d097ff85': 'USDC', '0x7f5c764cbc14f9669b88837ca1490cca17c31607': 'USDC.e',
        '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': 'DAI', '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58': 'USDT',
        '0x01bff41798a0bcf287b996046ca68b395dbc1071': 'USDT0', '0x4200000000000000000000000000000000000006': 'WETH',
        '0x68f180fcce6836688e9084f035309e29bf0a2095': 'WBTC', '0x1f32b1c2345538c0c6f582fcb022739c4a194ebb': 'wstETH',
        '0x9560e827af36c94d2ac33a39bce1fe78631088db': 'VELO', '0x4200000000000000000000000000000000000042': 'OP',
        '0x9bcef72be871e61ed4fbbc7630889bee758eb81d': 'rETH', '0x8700daec35af8ff88c16bdf0418774cb3d7599b4': 'SNX',
    },
}
HAIRCUT = {'major': 0.001, 'priced': 0.20, 'lowconf': 0.50, 'unpriced': 1.0}


class Prices:
    def __init__(self, raw, llama_prefix):
        self.raw, self.pre = raw, llama_prefix

    def get(self, token, ts):
        v = (self.raw.get('%s:%s' % (self.pre, token)) or {}).get(str(ts))
        return (v[0], v[1]) if v else (None, None)

    def tier(self, token, ts, majors):
        p, conf = self.get(token, ts)
        if p is None or p <= 0:
            return 'unpriced', 0.0
        if token in majors:
            return 'major', p
        if conf is not None and conf < 0.9:
            return 'lowconf', p
        return 'priced', p


def value_rows(rew_rows, toks, prices, majors, ts_of, haircut=HAIRCUT):
    """{(pool, epoch): {'fees': usd, 'bribe': usd, 'fees_major': usd, 'bribe_major': usd, 'raw': usd w/o haircut}}."""
    out = {}
    tier_tot = {}
    for i, kind, t, e, amt in rew_rows:
        dec = (toks.get(t) or {}).get('decimals')
        if dec is None or dec > 36:
            tier, p = 'unpriced', 0.0
        else:
            tier, p = prices.tier(t, ts_of(e), majors)
        q = int(amt) / 10 ** (dec or 18)
        usd = q * p
        if usd > 5e8:            # a single token-epoch worth $500M is a bad price, not a reward
            tier, usd = 'unpriced', 0.0
        d = out.setdefault((i, e), {'fees': 0.0, 'bribe': 0.0, 'fees_major': 0.0, 'bribe_major': 0.0, 'raw': 0.0})
        d[kind] += usd * (1.0 - haircut[tier])
        d['raw'] += usd
        if tier == 'major':
            d[kind + '_major'] += usd * (1.0 - haircut[tier])
        tier_tot[tier] = tier_tot.get(tier, 0.0) + usd
    return out, tier_tot


# ---------------------------------------------------------------------------------------------- analysis: perps
def load_funding(out, chain='base'):
    d = out / 'raw' / 'perps'
    bsym = 'AEROUSDT' if chain == 'base' else 'VELODROMEUSDT'
    only_binance = chain != 'base'

    def rd(n):
        if only_binance and not n.startswith('binance'):
            return []
        n = n.replace('AEROUSDT', bsym) if n.startswith('binance') else n
        f = d / (n + '.json.gz')
        return read_gz(f) if f.exists() else []
    daily = {}
    for k in rd('binance_AEROUSDT_klines_1d'):
        daily.setdefault('binance', {})[int(k[0]) // 1000] = float(k[4])
    for k in rd('binance_AEROUSDT_index_1d'):
        daily.setdefault('binance_index', {})[int(k[0]) // 1000] = float(k[4])
    for k in rd('bybit_AEROUSDT_klines_1d'):
        daily.setdefault('bybit', {})[int(k[0]) // 1000] = float(k[4])
    for k in rd('bybit_AEROUSDT_index_1d'):
        daily.setdefault('bybit_index', {})[int(k[0]) // 1000] = float(k[4])
    for k in rd('okx_klines_1d'):
        daily.setdefault('okx', {})[int(k[0]) // 1000] = float(k[4])
    for k in (rd('hl_candles_1d') or []):
        daily.setdefault('hl', {})[int(k['t']) // 1000] = float(k['c'])

    def px(venue, ts):
        day = ts - ts % DAY
        dd = daily.get(venue) or {}
        return dd.get(day) or dd.get(day - DAY)
    fund = {}
    for x in rd('binance_AEROUSDT_funding'):
        t = int(x['fundingTime']) // 1000
        mk = fnum(x.get('markPrice')) or px('binance', t)
        fund.setdefault('binance', []).append((t, float(x['fundingRate']), mk))
    for x in rd('bybit_AEROUSDT_funding'):
        t = int(x['fundingRateTimestamp']) // 1000
        fund.setdefault('bybit', []).append((t, float(x['fundingRate']), px('bybit', t)))
    for x in rd('okx_funding'):
        t = int(x['fundingTime']) // 1000
        fund.setdefault('okx', []).append((t, float(x.get('realizedRate') or x['fundingRate']), px('okx', t)))
    for x in rd('hl_funding'):
        t = int(x['time']) // 1000
        fund.setdefault('hl', []).append((t, float(x['fundingRate']), px('hl', t)))
    for v in fund.values():
        v.sort()
    return fund, daily


def funding_epochs(fund_rows, eps):
    """Per epoch: USD funding received by a 1-token short (rate x price summed over settlements), the count, and
    the annualised rate (sum of rates x 365/7)."""
    usd, cnt = bucket_by_epoch([(t, r * (p or 0.0)) for t, r, p in fund_rows], eps[0], len(eps))
    rate, _ = bucket_by_epoch([(t, r) for t, r, p in fund_rows], eps[0], len(eps))
    return usd, cnt, [x * EPOCHS_PER_YEAR for x in rate]


def book_depth(levels_bid, levels_ask, mid, bands=(0.005, 0.01, 0.02)):
    out = {}
    for b in bands:
        out['bid_%gpct' % (b * 100)] = sum(p * q for p, q in levels_bid if p >= mid * (1 - b))
        out['ask_%gpct' % (b * 100)] = sum(p * q for p, q in levels_ask if p <= mid * (1 + b))
    return out


def perp_capacity(out):
    d = out / 'raw' / 'perps'

    def rd(n):
        f = d / (n + '.json.gz')
        return read_gz(f) if f.exists() else None
    cap = {}
    prem = rd('binance_AEROUSDT_premium') or {}
    mark = fnum(prem.get('markPrice'))
    oi = rd('binance_AEROUSDT_oi') or {}
    dep = rd('binance_AEROUSDT_depth') or {}
    if dep and mark:
        bids = [(float(p), float(q)) for p, q in dep.get('bids', [])]
        asks = [(float(p), float(q)) for p, q in dep.get('asks', [])]
        mid = (bids[0][0] + asks[0][0]) / 2
        cap['binance'] = dict(book_depth(bids, asks, mid), oi_usd=fnum(oi.get('openInterest'), 0) * mark, mark=mark,
                              vol24h_usd=fnum((rd('binance_AEROUSDT_ticker') or {}).get('quoteVolume')),
                              funding_now=fnum(prem.get('lastFundingRate')))
    bk = ((rd('bybit_AEROUSDT_book') or {}).get('result') or {})
    tk = (((rd('bybit_AEROUSDT_ticker') or {}).get('result') or {}).get('list') or [{}])[0]
    if bk.get('b'):
        bids = [(float(p), float(q)) for p, q in bk['b']]
        asks = [(float(p), float(q)) for p, q in bk['a']]
        mid = (bids[0][0] + asks[0][0]) / 2
        cap['bybit'] = dict(book_depth(bids, asks, mid), oi_usd=fnum(tk.get('openInterestValue')), mark=fnum(tk.get('markPrice')),
                            vol24h_usd=fnum(tk.get('turnover24h')), funding_now=fnum(tk.get('fundingRate')))
    ob = ((rd('okx_book') or {}).get('data') or [{}])[0]
    if ob.get('bids'):
        ct = 10.0
        bids = [(float(x[0]), float(x[1]) * ct) for x in ob['bids']]
        asks = [(float(x[0]), float(x[1]) * ct) for x in ob['asks']]
        mid = (bids[0][0] + asks[0][0]) / 2
        oid = ((rd('okx_oi') or {}).get('data') or [{}])[0]
        cap['okx'] = dict(book_depth(bids, asks, mid), oi_usd=fnum(oid.get('oiUsd')), mark=mid)
    ctx = (rd('hl_ctx') or {}).get('ctx') or {}
    hb = rd('hl_book_sf3') or {}         # 20 levels at 3 significant figures span ~2%; the 4-figure book only ~0.2%
    if hb.get('levels'):
        bids = [(float(x['px']), float(x['sz'])) for x in hb['levels'][0]]
        asks = [(float(x['px']), float(x['sz'])) for x in hb['levels'][1]]
        mid = (bids[0][0] + asks[0][0]) / 2
        cap['hl'] = dict(book_depth(bids, asks, mid), oi_usd=fnum(ctx.get('openInterest'), 0) * fnum(ctx.get('markPx'), 0),
                         max_leverage=((rd('hl_ctx') or {}).get('meta') or {}).get('maxLeverage'),
                         mark=fnum(ctx.get('markPx')), vol24h_usd=fnum(ctx.get('dayNtlVlm')), funding_now=fnum(ctx.get('funding')))
    sb = ((rd('bybit_AEROUSDT_spot_book') or {}).get('result') or {})
    if sb.get('b'):
        bids = [(float(p), float(q)) for p, q in sb['b']]
        asks = [(float(p), float(q)) for p, q in sb['a']]
        mid = (bids[0][0] + asks[0][0]) / 2
        cap['bybit_spot'] = book_depth(bids, asks, mid)
    cb = rd('coinbase_book') or {}
    if cb.get('bids'):
        bids = [(float(x[0]), float(x[1])) for x in cb['bids']]
        asks = [(float(x[0]), float(x[1])) for x in cb['asks']]
        mid = (bids[0][0] + asks[0][0]) / 2
        cap['coinbase_spot'] = book_depth(bids, asks, mid)
    vel = rd('binance_VELODROMEUSDT_premium') or {}
    voi = rd('binance_VELODROMEUSDT_oi') or {}
    vdep = rd('binance_VELODROMEUSDT_depth') or {}
    if vel:
        vd = {}
        if vdep.get('bids'):
            bids = [(float(p), float(q)) for p, q in vdep['bids']]
            asks = [(float(p), float(q)) for p, q in vdep['asks']]
            vd = book_depth(bids, asks, (bids[0][0] + asks[0][0]) / 2)
        cap['binance_velodrome'] = dict(vd, **{'oi_usd': fnum(voi.get('openInterest'), 0) * fnum(vel.get('markPrice'), 0),
                                    'vol24h_usd': fnum((rd('binance_VELODROMEUSDT_ticker') or {}).get('quoteVolume')),
                                    'funding_now': fnum(vel.get('lastFundingRate'))})
    cap['perp_oi_total_usd'] = sum((v.get('oi_usd') or 0) for k, v in cap.items() if k in ('binance', 'bybit', 'okx', 'hl'))
    return cap



# ---------------------------------------------------------------------------------------------- analysis: chain
SIZES = (1e6, 5e6, 20e6)
RULES = ('avg', 'prev', 't24', 't1')
MARGIN = 1.0 / 3.0                # the short margined at 3x in cash: capital per unit of notional 1 + 1/3
TAKER = 0.0005
ENTRY_COST = 0.003                # buying the token on the DEX/CEX and opening the short (measured below)
MIN_POOL_USD = 25.0               # pools whose decision-time reward is below this are not considered by the voter


def savings_paid(ts):
    return SAVINGS_PAID.get(int(ymd(ts)[:4]), SSR)


def load_chain_data(out, chain):
    base = out / 'raw' / chain
    D = {'reg': read_gz(base / 'registry.json.gz'), 'rew': read_gz(base / 'rewards.json.gz'),
         'votes': read_gz(base / 'votes.json.gz'), 'glob': read_gz(base / 'global.json.gz'),
         'toks': read_gz(base / 'tokens.json.gz'), 'prices': read_gz(base / 'prices.json.gz') if (base / 'prices.json.gz').exists() else {}}
    for name in ('notify_last24h', 'notify_checkweeks', 've_transfers', 've_receipts', 've_locks_at_transfer', 'sugar_check',
                 'votes_verify'):
        f = base / (name + '.json.gz')
        D[name] = read_gz(f) if f.exists() else None
    D['_perps_dir'] = out / 'raw' / 'perps'
    return D


def late_amounts(D, chain, prices, majors):
    """Decision-time USD of rewards notified after T-24h and after T-1h, per (pool, epoch) and kind."""
    rows = (D.get('notify_last24h') or {}).get('rows') or []
    owner = {}
    for row in D['reg']['pools']:
        if row['fees']:
            owner[row['fees']] = (row['i'], 'fees')
        if row['bribe']:
            owner[row['bribe']] = (row['i'], 'bribe')
    c = CHAINS[chain]
    late24, late1 = {}, {}
    for addr, tok, ep, amt, blk, tx in rows:
        if addr not in owner:
            continue
        i, kind = owner[addr]
        ts = c['genesis_ts'] + 2 * (blk - c['genesis_block'])
        e = epoch_start(ts)
        dec = (D['toks'].get(tok) or {}).get('decimals') or 18
        tier, p = prices.tier(tok, e + WEEK + DECISION_LAG, majors)
        usd = int(amt) / 10 ** dec * p * (1 - HAIRCUT[tier])
        d = late24.setdefault((i, e), {'fees': 0.0, 'bribe': 0.0})
        d[kind] += usd
        if ts >= e + WEEK - HOUR - 60:
            d1 = late1.setdefault((i, e), {'fees': 0.0, 'bribe': 0.0})
            d1[kind] += usd
    return late24, late1


def analyze_chain(out, chain, log):
    c = CHAINS[chain]
    D = load_chain_data(out, chain)
    reg = D['reg']
    majors = MAJORS.get(chain, {})
    prices = Prices(D['prices'], c['llama'])
    tok = c['token'].lower()
    cur = epoch_start(reg['ts'])
    eps_all = epochs_between(c['first_epoch'], cur)
    E = [e for e in eps_all if e + WEEK <= reg['ts']]           # complete epochs

    def tok_px(ts):
        p, _ = prices.get(tok, ts - ts % DAY)
        if p is None:
            p, _ = prices.get(tok, ts - ts % DAY - DAY)
        return p
    rew_rows = D['rew']['rows']
    claim, tiers_claim = value_rows(rew_rows, D['toks'], prices, majors, lambda e: e + WEEK + SALE_LAG)
    decis, _ = value_rows(rew_rows, D['toks'], prices, majors, lambda e: e + WEEK + DECISION_LAG)
    late24, late1 = late_amounts(D, chain, prices, majors)
    have_logs = bool(D.get('notify_last24h'))
    # outlier screen: the largest non-major token-epoch values (a wrong DefiLlama price on an illiquid token is the
    # one way a few rows could carry the headline)
    big = {}
    for i, kind, t, e, amt in rew_rows:
        if t in majors:
            continue
        dec = (D['toks'].get(t) or {}).get('decimals')
        tier, p = prices.tier(t, e + WEEK + SALE_LAG, majors)
        if dec is None or tier == 'unpriced':
            continue
        usd = int(amt) / 10 ** dec * p
        k = (t, e)
        big[k] = big.get(k, 0.0) + usd
    top_nonmajor = sorted(big.items(), key=lambda kv: -kv[1])[:25]
    top_nonmajor = [{'token': t, 'symbol': (D['toks'].get(t) or {}).get('symbol'), 'epoch': ymd(e), 'usd_before_haircut': v}
                    for (t, e), v in top_nonmajor]
    nonmajor_by_token = {}
    for (t, e), v in big.items():
        nonmajor_by_token[t] = nonmajor_by_token.get(t, 0.0) + v
    top_tokens = [{'token': t, 'symbol': (D['toks'].get(t) or {}).get('symbol'), 'usd_before_haircut': v}
                  for t, v in sorted(nonmajor_by_token.items(), key=lambda kv: -kv[1])[:20]]
    votes = D['votes']
    glob = {g['epoch']: g for g in D['glob']}

    def V(i, e, name):
        v = ((votes.get(str(i)) or {}).get(str(e)) or {}).get(name)
        return (v or 0) / 1e18

    pools_by_epoch = {}
    for (i, e) in claim:
        pools_by_epoch.setdefault(e, set()).add(i)
    for si, per in votes.items():
        for se in per:
            pools_by_epoch.setdefault(int(se), set()).add(int(si))

    # ---- per-epoch table (average vote)
    table = []
    for e in E:
        P0, P1 = tok_px(e), tok_px(e + WEEK)
        ids = pools_by_epoch.get(e, set())
        R = fees = bribes = stranded = maj = raw = 0.0
        Vtot = 0.0
        per_pool = []
        for i in ids:
            v = V(i, e, 'end')
            d = claim.get((i, e))
            r = (d['fees'] + d['bribe']) if d else 0.0
            Vtot += v
            if v > 0:
                R += r
                fees += d['fees'] if d else 0.0
                bribes += d['bribe'] if d else 0.0
                maj += (d['fees_major'] + d['bribe_major']) if d else 0.0
                raw += d['raw'] if d else 0.0
                per_pool.append((r, i, v))
            else:
                stranded += r
        g = glob.get(e) or {}
        vepow = (g.get('ve_power_end') or 0) / 1e18
        rebase = (g.get('rebase_tokens') or 0) / 1e18
        rpv = R / Vtot if Vtot > 0 else None
        per_pool.sort(reverse=True)
        top10 = sum(r for r, _, _ in per_pool[:10]) / R if R > 0 else None
        # staleness: vote-weighted mean absolute deviation of each pool's reward per vote from the average, over the
        # average (0 if votes equalised rewards), and the share of votes in pools paying under half the average
        disp = below = None
        if rpv:
            disp = sum(v * abs(r / v - rpv) for r, _, v in per_pool) / (Vtot * rpv)
            below = sum(v for r, _, v in per_pool if r / v < 0.5 * rpv) / Vtot
        row = {'epoch': e, 'date': ymd(e), 'p_start': P0, 'p_end': P1, 'rewards_usd': R, 'raw_usd': raw, 'fees_usd': fees,
               'bribes_usd': bribes, 'majors_usd': maj, 'stranded_usd': stranded, 'votes': Vtot, 've_power': vepow,
               'vote_share_of_power': (Vtot / vepow) if vepow else None, 'rebase_tokens': rebase,
               'rebase_per_vote': (rebase / vepow) if vepow else None, 'rpv_usd': rpv, 'top10_share': top10,
               'n_pools_paid': len(per_pool), 'rpv_dispersion': disp, 'votes_below_half_avg': below}
        if rpv is not None and P0:
            row['voter_apr'] = rpv * EPOCHS_PER_YEAR / P0
            row['rebase_apr'] = (row['rebase_per_vote'] or 0) * EPOCHS_PER_YEAR * (P1 or P0) / P0
        table.append(row)
    log('%s: %d complete epochs, rewards $%.0fM' % (chain, len(table), sum(r['rewards_usd'] for r in table) / 1e6))

    # ---- attentive voter
    by_e = {r['epoch']: r for r in table}
    att = {}
    timing = []
    for k, e in enumerate(E):
        row = by_e[e]
        P0 = row['p_start']
        if not P0 or not row['votes'] or k == 0:
            continue
        ids = pools_by_epoch.get(e, set())
        Rc = {i: (claim[(i, e)]['fees'] + claim[(i, e)]['bribe']) for i in ids if (i, e) in claim}
        Vend = {i: V(i, e, 'end') for i in ids}
        dec = {i: (decis[(i, e)]['fees'] + decis[(i, e)]['bribe']) for i in ids if (i, e) in decis}
        prev_ids = pools_by_epoch.get(E[k - 1], set())
        hat = {
            'prev': {i: ((claim.get((i, E[k - 1])) or {}).get('fees', 0.0) + (claim.get((i, E[k - 1])) or {}).get('bribe', 0.0),
                         V(i, e, 'start')) for i in (prev_ids | ids)},
            'early': {i: ((decis.get((i, e)) or {}).get('fees', 0.0) + (claim.get((i, E[k - 1])) or {}).get('bribe', 0.0),
                          V(i, e, 'start')) for i in (prev_ids | ids)},
            't24': {i: (dec.get(i, 0.0) - sum((late24.get((i, e)) or {}).values()), V(i, e, 't24')) for i in ids},
            't1': {i: (dec.get(i, 0.0) - sum((late1.get((i, e)) or {}).values()), V(i, e, 't1')) for i in ids},
            'oracle': {i: (Rc.get(i, 0.0), Vend.get(i, 0.0)) for i in ids},
        }
        Rtot, Vtot = row['rewards_usd'], row['votes']
        late24_tot = sum(sum((late24.get((i, e)) or {}).values()) for i in ids)
        late1_tot = sum(sum((late1.get((i, e)) or {}).values()) for i in ids)
        vt24 = sum(V(i, e, 't24') for i in ids)
        vt1 = sum(V(i, e, 't1') for i in ids)
        moved24 = sum(abs(Vend.get(i, 0.0) - V(i, e, 't24')) for i in ids) / 2
        moved1 = sum(abs(Vend.get(i, 0.0) - V(i, e, 't1')) for i in ids) / 2
        dec_tot = sum(dec.values())
        timing.append({'epoch': e, 'late24_share_of_rewards': late24_tot / dec_tot if dec_tot else None,
                       'late1_share_of_rewards': late1_tot / dec_tot if dec_tot else None,
                       'votes_moved_last24h_share': moved24 / Vtot if Vtot else None,
                       'votes_moved_last1h_share': moved1 / Vtot if Vtot else None,
                       'votes_t24_over_end': vt24 / Vtot if Vtot else None, 'votes_t1_over_end': vt1 / Vtot if Vtot else None})
        for size in SIZES:
            M = size / P0
            res = {'avg': avg_vote_reward(Rtot, Vtot, M) / M}
            for rule in ('prev', 'early', 't24', 't1', 'oracle'):
                if rule in ('t24', 't1') and not have_logs:
                    res[rule] = None          # without the late-notification logs these rules would see the future
                    continue
                cand = {i: rv for i, rv in hat[rule].items() if rv[0] >= MIN_POOL_USD}
                al = water_fill(cand, M)
                res[rule] = realized_reward(al, Rc, Vend) / M
                res[rule + '_npools'] = len(al)
            att.setdefault(int(size), {})[e] = res
    log('%s: attentive voter on %d epochs' % (chain, len(att.get(int(SIZES[0]), {}))))
    return {'D': D, 'E': E, 'table': table, 'att': att, 'timing': timing, 'tiers_claim': tiers_claim, 'tok_px': tok_px,
            'claim': claim, 'cur': cur, 'prices': prices, 'late24': late24,
            'outliers': {'top_token_epochs': top_nonmajor, 'top_tokens': top_tokens}}



# ---------------------------------------------------------------------------------------------- analysis: hedge, protocol
def hedge_inputs(out, E, chain='base'):
    """Per epoch: the venue used (Binance once listed, Bybit before; pre-committed), USD funding to a 1-token short,
    its annualised rate, and the perp-minus-index basis at both ends; plus every venue's annualised funding."""
    fund, daily = load_funding(out, chain)
    per = {}
    for v, rows in fund.items():
        usd, cnt, ann = funding_epochs(rows, E)
        per[v] = {'usd': usd, 'cnt': cnt, 'ann': ann, 'first': rows[0][0] if rows else None}

    def basis(venue, ts):
        f = (daily.get(venue) or {}).get(ts - DAY)          # daily bar opened a day before closes at ts
        ix = (daily.get(venue + '_index') or {}).get(ts - DAY)
        return (f - ix) if (f and ix) else 0.0
    out_rows = []
    best_prev = None
    for k, e in enumerate(E):
        # best venue by trailing four epochs of funding to the short (needs four epochs of history; past data only)
        cands = []
        for v, d in per.items():
            hist = [d['ann'][j] for j in range(max(0, k - 4), k) if d['cnt'][j] > 0]
            if len(hist) == 4 and d['cnt'][k] > 0:
                cands.append((sum(hist) / 4, v))
        best = max(cands)[1] if cands else None
        best_row = {}
        if best:
            best_row = {'best_venue': best, 'best_funding_usd': per[best]['usd'][k], 'best_funding_ann': per[best]['ann'][k],
                        'best_switch': bool(best_prev and best_prev != best)}
            best_prev = best
        venue = None
        for v in ('binance', 'bybit'):
            first = (per.get(v) or {}).get('first')
            if first and first <= e and per[v]['cnt'][k] > 0:
                venue = v
                break
        row = dict({'epoch': e, 'venue': venue}, **best_row)
        if venue:
            row.update(funding_usd=per[venue]['usd'][k], funding_ann=per[venue]['ann'][k],
                       basis0=basis(venue, e), basis1=basis(venue, e + WEEK))
        for v in per:
            if per[v]['cnt'][k] > 0:
                row['ann_' + v] = per[v]['ann'][k]
        out_rows.append(row)
    return out_rows


def carry_series(chain_res, hedge, rule, size, m=MARGIN, bench='ssr', venue_rule='main', rpv_map=None):
    """Weekly excess return over the benchmark on capital, for epochs with a hedge venue. Returns (epochs, excess,
    detail rows). venue_rule 'main' = Binance once listed, Bybit before; 'best' = best trailing-4-epoch funding venue,
    paying a round trip of taker fees when it changes (basis not modelled for the switch)."""
    table = {r['epoch']: r for r in chain_res['table']}
    att = chain_res['att'].get(int(size), {})
    eps, xs, det = [], [], []
    for h in hedge:
        e = h['epoch']
        r = table.get(e)
        a = att.get(e)
        if not h.get('venue') or not r or not a or not r.get('p_start') or not r.get('p_end'):
            continue
        rpv = a[rule] if rpv_map is None else rpv_map.get(e, 0.0)
        if venue_rule == 'best' and h.get('best_venue'):
            f_usd = h['best_funding_usd'] - (2 * TAKER * r['p_start'] if h.get('best_switch') else 0.0)
            b0 = b1 = 0.0
        else:
            f_usd, b0, b1 = h['funding_usd'], h['basis0'], h['basis1']
        carry, cap, ret = epoch_carry(rpv, r['rebase_per_vote'] or 0.0, r['p_start'], r['p_end'], f_usd, b0, b1, m, TAKER)
        b = SSR if bench == 'ssr' else savings_paid(e)
        ex = ret - b * 7.0 / 365.0
        eps.append(e)
        xs.append(ex)
        det.append({'epoch': e, 'ret': ret, 'excess': ex, 'rewards': rpv / ((1 + m) * r['p_start']),
                    'rebase': (r['rebase_per_vote'] or 0.0) * r['p_end'] / ((1 + m) * r['p_start']),
                    'funding': f_usd / ((1 + m) * r['p_start']),
                    'basis': -(b1 - b0) / ((1 + m) * r['p_start'])})
    return eps, xs, det


def switch_series(eps, xs, det, signal_ok, entry_cost, exit_disc, m=MARGIN):
    """On/off version of a carry: when the signal (known before the epoch) is off the capital earns the benchmark
    (excess 0); each switch on pays the entry cost, each switch off sells the lock at `exit_disc` below its value."""
    out, on = [], False
    for e, x, ok in zip(eps, xs, signal_ok):
        cost = 0.0
        if ok and not on:
            cost = entry_cost / (1 + m)
            on = True
        elif not ok and on:
            cost = (exit_disc + TAKER) / (1 + m)
            on = False
        out.append((x if on else 0.0) - cost)
    return out


def ann_stats(xs, ppy=EPOCHS_PER_YEAR):
    if not xs:
        return {'n': 0}
    pf = B.perf(xs, ppy)
    t, pv = B.newey_west_t(xs, lags=4)
    bs = B.block_bootstrap(xs, block=4)
    return {'n': len(xs), 'ann_excess': pf['ann_return'], 'ann_vol': pf['ann_vol'], 'sharpe': pf['sharpe'],
            'max_dd': pf['max_drawdown'], 'hit': pf['hit_rate'], 'nw_t': t, 'nw_p': pv,
            'boot_lo': bs['lo'] * ppy if bs['lo'] is not None else None, 'boot_hi': bs['hi'] * ppy if bs['hi'] is not None else None,
            'boot_p_le_0': bs['p_le_0'], 'worst_week': pf['worst']}


def precommitted_variants():
    v = []
    for rule in RULES:
        for size in SIZES:
            v.append({'name': '%s/$%dM/always' % (rule, size / 1e6), 'rule': rule, 'size': size, 'switch': None})
    for rule in RULES:
        for x in (0.0, 0.05):
            v.append({'name': '%s/$5M/on>SSR+%dpp' % (rule, x * 100), 'rule': rule, 'size': 5e6, 'switch': x})
    for rule in ('avg', 't24'):
        v.append({'name': '%s/$5M/best-venue' % rule, 'rule': rule, 'size': 5e6, 'switch': None, 'venue': 'best'})
    return v


# ---------------------------------------------------------------------------------------------- analysis: sales
def sale_payment(rc, frm, to, tid, ve, chain, day, tok_px, prices):
    """(venue, usd, {token: amount}) paid to the seller of veNFT `tid` in one receipt, or None. Seaport: the order that
    offers (listing) or asks for (offer acceptance) the NFT; otherwise ERC20 transfers to the seller from the buyer or
    from the transaction's sender."""
    c = CHAINS[chain]
    weth = '0x4200000000000000000000000000000000000006'
    stables = {a for a, s_ in MAJORS.get(chain, {}).items() if s_ in ('USDC', 'USDbC', 'DAI', 'USDT', 'USDS', 'USDC.e', 'USDT0')}
    pay, venue = {}, None
    for addr, topics, data in rc['logs']:
        if addr in SEAPORT and topics and topics[0] == TOPIC['OrderFulfilled']:
            try:
                offerer, recip, offer, cons = dec_order_fulfilled(topics, data)
            except Exception:  # noqa: BLE001
                continue
            if any(it[1] == ve and it[2] == tid for it in offer):
                venue = 'seaport'
                for it in cons:
                    if it[0] in (0, 1):
                        k = it[1] if it[0] == 1 else 'eth'
                        pay[k] = pay.get(k, 0) + it[3]
            elif any(it[1] == ve and it[2] == tid for it in cons):
                venue = 'seaport_offer'
                for it in offer:
                    if it[0] in (0, 1):
                        k = it[1] if it[0] == 1 else 'eth'
                        pay[k] = pay.get(k, 0) + it[3]
    if not venue:
        for addr, topics, data in rc['logs']:
            if topics[0] == TOPIC['Transfer'] and len(topics) == 3 and addr != ve:
                f2, t2 = '0x' + topics[1][26:], '0x' + topics[2][26:]
                if t2 == frm and f2 in (to, (rc.get('from') or '').lower()):
                    pay[addr] = pay.get(addr, 0) + int(data[:66], 16)
                    venue = 'erc20_same_tx'
    if not pay:
        return None
    usd = 0.0
    for t, amt in pay.items():
        if t in ('eth', weth):
            p_, _ = prices.get(weth, day)
            if p_ is None:
                return None
            usd += amt / 1e18 * p_
        elif t in stables:
            usd += amt / (1e18 if t == '0x50c5725949a6f0c72e6c4a641f24049a917db0cb' else 1e6)
        elif t == c['token'].lower():
            usd += amt / 1e18 * (tok_px(day) or 0.0)
        else:
            return None
    return venue, usd, pay


def parse_sales(D, chain, tok_px, prices):
    c = CHAINS[chain]
    rows = D.get('ve_transfers') or []
    rec = D.get('ve_receipts') or {}
    locks = D.get('ve_locks_at_transfer') or {}
    zero = '0x' + '0' * 40
    ve = c['ve'].lower()
    out = []
    for frm, to, tid, blk, tx in rows:
        if frm == zero or to == zero:
            continue
        lkh = locks.get('%d:%d' % (tid, blk))
        rc = rec.get(tx)
        if not rc or not lkh:
            continue
        ts = c['genesis_ts'] + 2 * (blk - c['genesis_block'])
        day = ts - ts % DAY
        sp = sale_payment(rc, frm, to, tid, ve, chain, day, tok_px, prices)
        if not sp or sp[1] <= 0:
            continue
        venue, usd, pay = sp
        lk = dec_locked(lkh)
        P = tok_px(day)
        if not lk or not P or lk[0] <= 0:
            continue
        amount = lk[0] / 1e18
        value = amount * P
        if value < 50:
            continue
        years_left = None if lk[2] else max(0.0, (lk[1] - ts) / (365.0 * DAY))
        paid_in_token = (len(pay) == 1 and c['token'].lower() in pay)
        out.append({'ts': ts, 'date': ymd(ts), 'token_id': tid, 'venue': venue, 'via': rc.get('to'), 'usd': usd,
                    'locked': amount, 'value_usd': value, 'discount': sale_discount(usd, amount, P), 'permanent': lk[2],
                    'years_left': years_left, 'paid_in_token': paid_in_token, 'tx': tx})
    return out


def sales_summary(sales):
    def summ(xs):
        if not xs:
            return {'n': 0}
        ds = sorted(x['discount'] for x in xs)
        w = sum(x['value_usd'] for x in xs)
        return {'n': len(xs), 'value_usd': w, 'paid_usd': sum(x['usd'] for x in xs),
                'median_discount': ds[len(ds) // 2], 'p25': ds[len(ds) // 4], 'p75': ds[(3 * len(ds)) // 4],
                'value_weighted_discount': 1 - sum(x['usd'] for x in xs) / w if w else None}
    ok = [x for x in sales if -0.5 < x['discount'] < 0.99]
    res = {'all': summ(ok), 'excluded_outliers': len(sales) - len(ok)}
    for y in sorted({x['date'][:4] for x in ok}):
        res['year_' + y] = summ([x for x in ok if x['date'][:4] == y])
    res['permanent_or_4y'] = summ([x for x in ok if x['permanent'] or (x['years_left'] or 0) > 3.5])
    res['size_lt_10k'] = summ([x for x in ok if x['value_usd'] < 1e4])
    res['size_10k_100k'] = summ([x for x in ok if 1e4 <= x['value_usd'] < 1e5])
    res['size_ge_100k'] = summ([x for x in ok if x['value_usd'] >= 1e5])
    res['last_365d'] = summ([x for x in ok if x['ts'] >= time.time() - 365 * DAY])
    res['largest'] = sorted(ok, key=lambda x: -x['value_usd'])[:10]
    return res


# ---------------------------------------------------------------------------------------------- analysis: checks
def check_events_vs_storage(D):
    """Sum of NotifyReward events per (contract, token, epoch) over full sample weeks against tokenRewardsPerEpoch."""
    cw = D.get('notify_checkweeks')
    if not cw:
        return None
    owner = {}
    for row in D['reg']['pools']:
        for kind in ('fees', 'bribe'):
            if row[kind]:
                owner[(row['i'], kind)] = row[kind]
    ev = {}
    for addr, tok, ep, amt, blk, tx in cw['rows']:
        ev[(addr, tok, ep)] = ev.get((addr, tok, ep), 0) + int(amt)
    st = {}
    weeks = set(cw['epochs'])
    for i, kind, t, e, amt in D['rew']['rows']:
        if e in weeks:
            st[(owner.get((i, kind)), t, e)] = int(amt)
    keys = set(ev) | set(st)
    exact = sum(1 for k in keys if ev.get(k, 0) == st.get(k, 0))
    only_ev = [k for k in keys if k not in st]
    only_st = [k for k in keys if k not in ev]
    return {'epochs': sorted(weeks), 'keys': len(keys), 'exact_matches': exact, 'only_in_events': len(only_ev),
            'only_in_storage': len(only_st), 'examples_mismatch': [list(k) + [ev.get(k, 0), st.get(k, 0)] for k in keys if ev.get(k, 0) != st.get(k, 0)][:5]}


def dec_lp_epochs(h):
    """RewardsSugar.epochsByAddress -> [{'ts','lp','votes','emissions','bribes':[(token, amount)],'fees':[...]}]."""
    b = bytes.fromhex(h[2:] if h.startswith('0x') else h)

    def w(i):
        return int.from_bytes(b[i:i + 32], 'big')
    arr = w(0)
    n = w(arr)
    base = arr + 32
    out = []
    for k in range(n):
        so = base + w(base + 32 * k)

        def arr2(off):
            q = so + off
            mm = w(q)
            return [('0x' + b[q + 32 + 64 * j + 12:q + 32 + 64 * j + 32].hex(), w(q + 32 + 64 * j + 32)) for j in range(mm)]
        out.append({'ts': w(so), 'lp': '0x' + b[so + 44:so + 64].hex(), 'votes': w(so + 64), 'emissions': w(so + 96),
                    'bribes': arr2(w(so + 128)), 'fees': arr2(w(so + 160))})
    return out


def check_sugar(D):
    sc = D.get('sugar_check')
    if not sc:
        return None
    by_pool = {row['pool']: row['i'] for row in D['reg']['pools']}
    st = {}
    for i, kind, t, e, amt in D['rew']['rows']:
        st[(i, kind, t, e)] = int(amt)
    n = match = vmatch = vn = 0
    for pool, h in sc.items():
        if not h:
            continue
        i = by_pool.get(pool)
        for ep in dec_lp_epochs(h):
            for kind, lst in (('bribe', ep['bribes']), ('fees', ep['fees'])):
                for t, amt in lst:
                    n += 1
                    match += int(st.get((i, kind, t, ep['ts']), 0) == amt)
            vv = ((D['votes'].get(str(i)) or {}).get(str(ep['ts'])) or {}).get('end')
            if vv is not None:
                vn += 1
                vmatch += int(vv == ep['votes'])
    return {'pools': len(sc), 'reward_items': n, 'reward_exact': match, 'vote_epochs': vn, 'vote_exact': vmatch}


AERO_XYZ_REVENUE = {'2023Q3': 12.9e6, '2023Q4': 6.4e6, '2024Q1': 30.7e6, '2024Q2': 78.5e6, '2024Q3': 57.7e6,
                    '2024Q4': 111.2e6, '2025Q1': 71.8e6, '2025Q2': 40.6e6, '2025Q3': 63.6e6, '2025Q4': 38.6e6,
                    '2026Q1': 20.5e6, '2026Q2': 16.4e6, '2026Q3': 25.8e6}   # aero.xyz/economics, read 2026-10-10


def quarter(ts):
    d = dt.datetime.fromtimestamp(ts, UTC)
    return '%dQ%d' % (d.year, (d.month - 1) // 3 + 1)



# ---------------------------------------------------------------------------------------------- analysis: assemble
MERGER = {
    'what': 'Aerodrome and Velodrome merge into Aero (Dromos Labs MetaDEX); one token, AERO',
    'start_utc': '2026-10-22 00:00 (MERGER_TS); legacy emissions and weekly voting end',
    'conversion': 'AERO 1:1; VELO about 0.044 AERO (94.5% / 5.5% split); veNFT -> sAERO stake via the upgrade portal '
                  '(not automatic); remaining lock rounded up to whole weeks, capped at 4 years; permanent locks stay '
                  'permanent (Migration._resolveStake, github.com/Dromos-Labs/metadex-public); expired locks settle liquid',
    'new_system': 'continuous allocation instead of epochs; stakers receive 100% of exchange revenue of the pools they '
                  'support plus incentives (IncentiveClaim in IVoter); an allocation cooldown (47 h at launch, per press); '
                  'sAERO is a transferable NFT; MAXTIME 4 years with linear decay or permanent mode',
    'contracts': 'MetaDEX 1.0.0 deployed on Arc (2026-09-15); 1.0.1 (2026-10-02) lists no deployment; Base addresses not published at 2026-10-10',
    'sources': ['https://aero.xyz/economics/', 'https://github.com/Dromos-Labs/metadex-public',
                'https://www.tokenpost.com/news/business/29296'],
}


def rnd(x, k=6):
    if isinstance(x, float):
        return round(x, k) if math.isfinite(x) else None
    if isinstance(x, dict):
        return {kk: rnd(v, k) for kk, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rnd(v, k) for v in x]
    return x


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None



def input_checks(out):
    """(a) AERO funding against the copy another worker pulled on 2026-10-09 (research/2026-10-09/funding_arb/raw);
    (b) DefiLlama's daily AERO against the exchange closes of the bar ending at the same midnight."""
    res = {}
    other = ROOT / 'research' / '2026-10-09' / 'funding_arb' / 'raw'
    for venue, mine_f, key_t, other_f in (('binance', 'binance_AEROUSDT_funding', 'fundingTime', other / 'binance' / 'funding' / 'AEROUSDT.json.gz'),
                                           ('bybit', 'bybit_AEROUSDT_funding', 'fundingRateTimestamp', other / 'bybit' / 'funding' / 'AEROUSDT.json.gz')):
        f = out / 'raw' / 'perps' / (mine_f + '.json.gz')
        if not (f.exists() and other_f.exists()):
            continue
        m = {int(x[key_t]) // 1000: float(x['fundingRate']) for x in read_gz(f)}
        o = {int(x['t']) // 1000: float(x['rate']) for x in read_gz(other_f)}
        com = sorted(set(m) & set(o))
        if not com:
            continue
        days = (com[-1] - com[0]) / DAY
        res['funding_' + venue] = {'common': len(com), 'diffs': sum(1 for k in com if abs(m[k] - o[k]) > 1e-12),
                                   'window': [ymd(com[0]), ymd(com[-1])], 'ann_mine': sum(m[k] for k in com) / days * 365,
                                   'ann_other': sum(o[k] for k in com) / days * 365}
    pf = out / 'raw' / 'base' / 'prices.json.gz'
    if pf.exists():
        aero = read_gz(pf).get('base:' + CHAINS['base']['token'].lower()) or {}
        _, daily = load_funding(out, 'base')
        idx = daily.get('binance_index') or {}
        cb = {}
        cf_ = out / 'raw' / 'perps' / 'coinbase_candles_1d.json.gz'
        if cf_.exists():
            cb = {int(r[0]): float(r[4]) for r in read_gz(cf_)}
        rel = []
        for k, v in aero.items():
            d = int(k)
            ref = idx.get(d - DAY) or cb.get(d - DAY)
            if v and ref:
                rel.append(abs(v[0] / ref - 1))
        rel.sort()
        if rel:
            res['aero_price_vs_exchange'] = {'n_days': len(rel), 'median_abs_rel_diff': rel[len(rel) // 2],
                                             'p95': rel[int(0.95 * (len(rel) - 1))], 'max': rel[-1]}
    return res


def analyze(out, chains, log):
    A = {'generated_at': dt.datetime.now(UTC).isoformat(timespec='seconds'), 'merger': MERGER,
         'benchmark': {'ssr': SSR, 'savings_paid_by_year': SAVINGS_PAID},
         'conventions': {'epoch': 'Thursday 00:00 UTC to Thursday 00:00 UTC', 'sale_lag_s': SALE_LAG,
                         'decision_price_lag_s': DECISION_LAG, 'haircuts': HAIRCUT, 'margin_per_notional': MARGIN,
                         'taker': TAKER, 'entry_cost': ENTRY_COST, 'epochs_per_year': EPOCHS_PER_YEAR,
                         'min_pool_usd_considered': MIN_POOL_USD, 'max_vote_pools': MAX_VOTE_POOLS},
         'variants_precommitted': [v['name'] for v in precommitted_variants()]}
    A['perp_capacity'] = perp_capacity(out)
    for chain in chains:
        res = analyze_chain(out, chain, log)
        A[chain] = assemble_chain(out, chain, res, A, log)
    # independent paths for the hedge-cost and price inputs
    A['input_checks'] = input_checks(out)
    # external check: gross voter rewards (no haircut) on both chains against aero.xyz's quarterly exchange revenue
    if A.get('base'):
        cmp_ = {}
        for qq, ref in AERO_XYZ_REVENUE.items():
            ours = sum(((A.get(ch) or {}).get('quarterly') or {}).get(qq, {}).get('raw_usd', 0.0) for ch in ('base', 'optimism'))
            cmp_[qq] = {'ours_gross_both_chains': ours, 'aero_xyz': ref, 'ratio': ours / ref if ref else None}
        A['external_check_aero_xyz'] = cmp_
    write_json(out / 'analysis.json', rnd(A))
    write_manifest(out, A)
    log('analysis.json and manifest.json written')
    return A


def assemble_chain(out, chain, res, A, log):
    c = CHAINS[chain]
    D, E, table = res['D'], res['E'], res['table']
    R = {'n_epochs': len(table), 'first_epoch': ymd(E[0]), 'last_complete_epoch': ymd(E[-1]),
         'registry': {'pools': D['reg']['n_pools'], 'block': D['reg']['block'], 'now': D['reg']['now']},
         'value_by_tier_usd': res['tiers_claim'], 'nonmajor_outlier_screen': res['outliers']}
    R['epochs'] = [{k: v for k, v in r.items()} for r in table]
    # by year
    by = {}
    for r in table:
        y = r['date'][:4]
        by.setdefault(y, []).append(r)
    R['by_year'] = {}
    for y, rows in by.items():
        R['by_year'][y] = {'epochs': len(rows), 'rewards_usd': sum(r['rewards_usd'] for r in rows),
                           'fees_usd': sum(r['fees_usd'] for r in rows), 'bribes_usd': sum(r['bribes_usd'] for r in rows),
                           'majors_share': sum(r['majors_usd'] for r in rows) / max(1e-9, sum(r['rewards_usd'] for r in rows)),
                           'voter_apr_mean': mean([r.get('voter_apr') for r in rows]),
                           'voter_apr_median': med([r.get('voter_apr') for r in rows]),
                           'rebase_apr_mean': mean([r.get('rebase_apr') for r in rows]),
                           'p_mean': mean([r['p_start'] for r in rows]),
                           'votes_mean': mean([r['votes'] for r in rows]),
                           'top10_share_mean': mean([r.get('top10_share') for r in rows]),
                           'rpv_dispersion_mean': mean([r.get('rpv_dispersion') for r in rows]),
                           'votes_below_half_avg_mean': mean([r.get('votes_below_half_avg') for r in rows]),
                           'vote_share_of_power_mean': mean([r.get('vote_share_of_power') for r in rows])}
    # quarterly check against aero.xyz
    q = {}
    for r in table:
        qq = quarter(r['epoch'])
        q.setdefault(qq, {'fees_usd': 0.0, 'bribes_usd': 0.0, 'raw_usd': 0.0})
        q[qq]['fees_usd'] += r['fees_usd']
        q[qq]['bribes_usd'] += r['bribes_usd']
        q[qq]['raw_usd'] += r.get('raw_usd') or 0.0
    if chain == 'base':
        for qq, v in q.items():
            v['aero_xyz_all_chains'] = AERO_XYZ_REVENUE.get(qq)
    R['quarterly'] = q
    # attentive voter
    att = res['att']
    R['attentive'] = {}
    for size, per in att.items():
        eps = sorted(per)
        d = {}
        tmap = {r['epoch']: r for r in table}
        for rule in ('prev', 'early', 't24', 't1', 'oracle'):
            if any(per[e].get(rule) is None for e in eps):
                continue
            prem = [per[e][rule] / per[e]['avg'] - 1 for e in eps if per[e]['avg'] > 0]
            apr_gain = []
            for e in eps:
                row = tmap.get(e)
                if row and row.get('p_start'):
                    apr_gain.append((per[e][rule] - per[e]['avg']) * EPOCHS_PER_YEAR / row['p_start'])
            half = len(prem) // 2
            d[rule] = {'mean_premium': mean(prem), 'median_premium': med(prem),
                       'mean_apr_gain': mean(apr_gain), 'first_half_apr_gain': mean(apr_gain[:half]),
                       'second_half_apr_gain': mean(apr_gain[half:]), 'last_52_apr_gain': mean(apr_gain[-52:]),
                       'share_epochs_positive': (sum(1 for x in prem if x > 0) / len(prem)) if prem else None,
                       'mean_npools': mean([per[e].get(rule + '_npools') for e in eps])}
            yr = {}
            for e, g in zip(eps, apr_gain):
                yr.setdefault(ymd(e)[:4], []).append(g)
            d[rule]['apr_gain_by_year'] = {y: mean(v) for y, v in yr.items()}
        d['split_epoch'] = ymd(eps[len(eps) // 2]) if eps else None
        d['first_epoch'] = ymd(eps[0]) if eps else None
        t1_vs_t24 = [(per[e]['t1'] - per[e]['t24']) / per[e]['avg'] for e in eps
                     if per[e]['avg'] > 0 and per[e].get('t1') is not None and per[e].get('t24') is not None]
        d['t1_minus_t24_over_avg'] = mean(t1_vs_t24)
        R['attentive'][str(size)] = d
    R['timing'] = {k: mean([t[k] for t in res['timing']]) for k in ('late24_share_of_rewards', 'late1_share_of_rewards',
                                                                      'votes_moved_last24h_share', 'votes_moved_last1h_share',
                                                                      'votes_t24_over_end', 'votes_t1_over_end')}
    R['timing']['last_52'] = {k: mean([t[k] for t in res['timing'][-52:]]) for k in ('late24_share_of_rewards', 'votes_moved_last24h_share')}
    # hedge and carry (Aerodrome only: the AERO perps)
    hedge = hedge_inputs(out, E, chain)
    if any(h.get('venue') for h in hedge):
        R['hedge'] = summarize_hedge(hedge)
        R['hedge']['funding_detail'] = funding_detail(out, chain)
        # the on/off rule sells the lock at the observed median sale discount (15% if no sales are measured)
        sales = parse_sales(D, chain, res['tok_px'], res['prices']) if chain == 'base' else []
        ss = sales_summary(sales) if sales else {}
        disc = ((ss.get('all') or {}).get('median_discount'))
        res['sales'], res['sales_summary'] = sales, ss
        R['carry'] = carry_protocol(res, hedge, log, disc if disc is not None and disc > 0 else 0.15)
        R['exit'] = exit_block(res, R['carry'], D, chain)
    if chain == 'base':
        R['live'] = live_block(out, res, D, chain)
    R['counts'] = {'notify_last24h_rows': len((D.get('notify_last24h') or {}).get('rows') or []),
                   'notify_checkweek_rows': len((D.get('notify_checkweeks') or {}).get('rows') or []),
                   've_transfers': len(D.get('ve_transfers') or []), 've_receipts': len(D.get('ve_receipts') or {}),
                   'reward_contracts_with_votes': len(reward_contracts(D['reg']))}
    R['checks'] = {'events_vs_storage': check_events_vs_storage(D), 'sugar_vs_storage': check_sugar(D),
                   'votes_reread_sample': {k: v for k, v in (D.get('votes_verify') or {}).items() if k != 'examples'} or None,
                   'reward_reads_failed': D['rew'].get('failed'), 'reward_reads': D['rew'].get('reads')}
    return R



def funding_detail(out, chain):
    """Per venue: monthly annualised funding to a short, the modal settlement rate and its share (the interest-only
    rate when the premium is inside the clamp), and the worst month."""
    fund, _ = load_funding(out, chain)
    res = {}
    for v, rows in fund.items():
        months = {}
        for t, r, _p in rows:
            m = dt.datetime.fromtimestamp(t, UTC).strftime('%Y-%m')
            months.setdefault(m, 0.0)
            months[m] += r
        monthly = {m: x / 30.4 * 365 for m, x in months.items()}
        rates = {}
        for _t, r, _p in rows:
            rates[round(r, 8)] = rates.get(round(r, 8), 0) + 1
        modal = max(rates.items(), key=lambda kv: kv[1]) if rates else (None, 0)
        res[v] = {'first': ymd(rows[0][0]) if rows else None, 'settlements': len(rows), 'monthly_ann': monthly,
                  'modal_rate': modal[0], 'modal_share': modal[1] / len(rows) if rows else None,
                  'worst_month': min(monthly.items(), key=lambda kv: kv[1]) if monthly else None}
    return res


def summarize_hedge(hedge):
    out = {'by_year': {}, 'venue_epochs': {}}
    for h in hedge:
        y = ymd(h['epoch'])[:4]
        for k, v in h.items():
            if k.startswith('ann_'):
                out['by_year'].setdefault(y, {}).setdefault(k[4:], []).append(v)
        if h.get('venue'):
            out['venue_epochs'][h['venue']] = out['venue_epochs'].get(h['venue'], 0) + 1
    out['by_year'] = {y: {v: mean(xs) for v, xs in d.items()} for y, d in out['by_year'].items()}
    hv = [h for h in hedge if h.get('venue')]
    out['first_hedged_epoch'] = ymd(hv[0]['epoch']) if hv else None
    if hv:
        cut = B.cutoff_index(len(hv), 0.5)
        for part, sl in (('in_sample', hv[:cut]), ('out_of_sample', hv[cut:])):
            cnt = {}
            for h in sl:
                cnt[h.get('best_venue') or 'none'] = cnt.get(h.get('best_venue') or 'none', 0) + 1
            out['best_venue_epochs_' + part] = cnt
    out['mean_funding_ann_used'] = mean([h['funding_ann'] for h in hv])
    out['last_26_funding_ann_used'] = mean([h['funding_ann'] for h in hv[-26:]])
    out['share_epochs_shorts_pay'] = (sum(1 for h in hv if h['funding_ann'] < 0) / len(hv)) if hv else None
    for v in ('binance', 'bybit', 'okx', 'hl'):
        xs = [h['ann_' + v] for h in hedge if ('ann_' + v) in h]
        out['venue_mean_ann_' + v] = mean(xs)
        out['venue_last_26_ann_' + v] = mean(xs[-26:])
    return out


def carry_protocol(res, hedge, log, exit_disc=0.15):
    att5 = res['att'].get(int(5e6), {})
    ok_rules = {r for r in RULES if att5 and all(a.get(r) is not None for a in att5.values())}
    variants = [v for v in precommitted_variants() if v['rule'] in ok_rules]
    series, det = {}, {}
    eps_ref = None
    for v in variants:
        if v['switch'] is not None:
            continue
        eps, xs, dd = carry_series(res, hedge, v['rule'], v['size'], venue_rule=v.get('venue', 'main'))
        series[v['name']] = xs
        det[v['name']] = (eps, dd)
        eps_ref = eps_ref or eps
    # each half starts fresh: an always-on position pays the entry cost in its first epoch of each half
    cut0 = B.cutoff_index(len(eps_ref), 0.5)
    for name in list(series):
        xs = list(series[name])
        xs[0] -= ENTRY_COST / (1 + MARGIN)
        xs[cut0] -= ENTRY_COST / (1 + MARGIN)
        series[name] = xs
    # on/off: trailing four epochs of (avg voter APR + rebase APR + funding APR) minus SSR, known before the epoch
    table = {r['epoch']: r for r in res['table']}
    hmap = {h['epoch']: h for h in hedge}
    sig = []
    for k, e in enumerate(eps_ref):
        prev = [eps_ref[j] for j in range(max(0, k - 4), k)]
        vals = []
        for pe in prev:
            r, h = table[pe], hmap[pe]
            if r.get('voter_apr') is not None:
                # per unit of notional: voter APR + rebase APR + funding to the short; per unit of capital below
                vals.append(r['voter_apr'] + (r.get('rebase_apr') or 0) + h['funding_ann'])
        sig.append(mean(vals))
    disc = exit_disc
    for v in variants:
        if v['switch'] is None:
            continue
        base = '%s/$5M/always' % v['rule']
        eps, dd = det[base]
        ok = [(s_ is not None and s_ / (1 + MARGIN) - SSR > v['switch']) for s_ in sig]
        raw = [x for x in det[base][1]]
        xs_raw = [r_['excess'] for r_ in raw]
        series[v['name']] = (switch_series(eps[:cut0], xs_raw[:cut0], None, ok[:cut0], ENTRY_COST, disc)
                             + switch_series(eps[cut0:], xs_raw[cut0:], None, ok[cut0:], ENTRY_COST, disc))
    ct = B.choose_then_test(series, frac=0.5, periods_per_year=EPOCHS_PER_YEAR)
    n = len(eps_ref)
    cut = ct['cutoff_index']
    out = {'epochs': [ymd(e) for e in eps_ref], 'cutoff_epoch': ymd(eps_ref[cut]), 'switch_exit_discount_assumed': disc,
           'choose_then_test': {k: v for k, v in ct.items() if k not in ('bh_adjusted_p',)}, 'variants': {}}
    for name, xs in series.items():
        out['variants'][name] = {'full': ann_stats(xs), 'in_sample': ann_stats(xs[:cut]), 'out_of_sample': ann_stats(xs[cut:]),
                                 'last_26': ann_stats(xs[-26:]), 'last_52': ann_stats(xs[-52:])}
    # decomposition of the main rows, annualised, per half
    for name in ('avg/$5M/always', 'prev/$5M/always', 't24/$5M/always', ct['chosen']):
        if name not in det:
            continue
        eps, dd = det[name]
        comp = {}
        for part, sl in (('in_sample', slice(0, cut)), ('out_of_sample', slice(cut, n)), ('full', slice(0, n))):
            rows = dd[sl]
            comp[part] = {k: mean([r[k] for r in rows]) * EPOCHS_PER_YEAR for k in ('rewards', 'rebase', 'funding', 'basis', 'ret')}
            comp[part]['excess'] = comp[part]['ret'] - SSR
        out.setdefault('decomposition', {})[name] = comp
        yr = {}
        for r in dd:
            yr.setdefault(ymd(r['epoch'])[:4], []).append(r)
        out.setdefault('by_year', {})[name] = {y: {k: mean([r[k] for r in rows]) * EPOCHS_PER_YEAR for k in ('rewards', 'rebase', 'funding', 'basis', 'excess')}
                                               for y, rows in yr.items()}
    # against the savings rate actually paid
    for name in {'avg/$5M/always', ct['chosen']}:
        if not name.endswith('always'):
            continue
        rule, size = name.split('/')[0], float(name.split('/')[1].strip('$M')) * 1e6
        _, xs, _ = carry_series(res, hedge, rule, size, bench='paid')
        out.setdefault('vs_savings_paid', {})[name] = {'out_of_sample': ann_stats(xs[cut:]), 'full': ann_stats(xs)}
    # stability inside the test window: its two halves, and how much of the total the best four weeks carry
    stab = {}
    for name in {'avg/$5M/always', 'avg/$5M/best-venue', ct['chosen']}:
        xs = series.get(name)
        if not xs:
            continue
        o = xs[cut:]
        h = len(o) // 2
        tot = sum(o)
        top4 = sum(sorted(o, reverse=True)[:4])
        stab[name] = {'test_first_half': ann_stats(o[:h]), 'test_second_half': ann_stats(o[h:]),
                      'test_halves_split_epoch': ymd(eps_ref[cut + h]), 'best4_share_of_total': (top4 / tot) if tot > 0 else None,
                      'weeks_positive_share': sum(1 for x in o if x > 0) / len(o) if o else None}
    out['test_stability'] = stab
    # sensitivities outside the protocol (not candidates for the choice): capital, valuation, venue
    sens = {}
    _, xs5, _ = carry_series(res, hedge, 'avg', 5e6, m=0.2)
    sens['avg/5x margin (m=0.2)'] = xs5
    tb = {r['epoch']: r for r in res['table']}
    maj = {e: (r['majors_usd'] / r['votes']) if r['votes'] else 0.0 for e, r in tb.items()}
    h50 = {e: ((r['majors_usd'] + (r['rewards_usd'] - r['majors_usd']) * 0.5 / 0.8) / r['votes']) if r['votes'] else 0.0 for e, r in tb.items()}
    for label, mp in (('avg/majors-only rewards', maj), ('avg/non-majors at 50% haircut', h50)):
        _, xs_, _ = carry_series(res, hedge, 'avg', 5e6, rpv_map=mp)
        sens[label] = xs_
        _, xs_, _ = carry_series(res, hedge, 'avg', 5e6, rpv_map=mp, venue_rule='best')
        sens[label + ', best venue'] = xs_
    _, xs_, _ = carry_series(res, hedge, 'avg', 5e6, bench='paid', venue_rule='best')
    sens['avg/best venue vs savings paid'] = xs_
    out['sensitivity'] = {k: {'in_sample': ann_stats(v[:cut]), 'out_of_sample': ann_stats(v[cut:]), 'last_52': ann_stats(v[-52:])}
                          for k, v in sens.items()}
    # unhedged context: voter + rebase APR minus SSR on the token alone, every complete epoch
    log('carry: chosen %s, OOS ann excess %.4f' % (ct['chosen'], ct['out_of_sample'].get('ann_return') or float('nan')))
    return out


def exit_block(res, carry, D, chain):
    out = {}
    cut_name = carry['choose_then_test']['chosen']
    for name in ('avg/$5M/always', 'prev/$5M/always', cut_name):
        v = carry['variants'].get(name)
        if not v:
            continue
        oos = v['out_of_sample'].get('ann_excess')
        last = v['last_52'].get('ann_excess')
        # net of the entry (token purchase + short) and the exit's taker fee; the discount itself is what is solved for
        out[name] = {'breakeven_discount_after_months': {str(mo): (breakeven_discount([oos / EPOCHS_PER_YEAR] * int(mo * 52 / 12), MARGIN) - ENTRY_COST - TAKER
                                                                   if oos is not None else None) for mo in (3, 6, 12, 24)},
                     'oos_ann_excess': oos, 'last_52_ann_excess': last}
    prices = res['prices']
    if chain == 'base':
        # iAERO: liquid receipt of permanently locked veAERO, minted at 0.95 per AERO; exit = 0.95 x iAERO/AERO
        ratio = []
        for day in sorted(int(k) for k in (D['prices'].get('base:' + IAERO) or {})):
            pi, _ = prices.get(IAERO, day)
            pa = res['tok_px'](day)
            if pi and pa:
                ratio.append((day, pi / pa))
        if ratio:
            last90 = [r for d_, r in ratio if d_ >= ratio[-1][0] - 90 * DAY]
            out['iaero'] = {'first_day': ymd(ratio[0][0]), 'last_day': ymd(ratio[-1][0]), 'ratio_last': ratio[-1][1],
                            'ratio_mean_90d': mean(last90), 'ratio_min': min(r for _, r in ratio), 'ratio_max': max(r for _, r in ratio),
                            'exit_cost_via_mint_last': 1 - 0.95 * ratio[-1][1], 'n_days': len(ratio)}
        gt = None
        f = out_dir_perps(D) / 'gt_iaero_pools.json.gz' if out_dir_perps(D) else None
        if f and f.exists():
            gt = read_gz(f)
            out.setdefault('iaero', {})['pools'] = [{'name': p_['attributes']['name'], 'reserve_usd': fnum(p_['attributes'].get('reserve_in_usd')),
                                                    'volume_24h_usd': fnum((p_['attributes'].get('volume_usd') or {}).get('h24'))}
                                                   for p_ in (gt.get('data') or [])]
    sales = res.get('sales')
    if sales is None:
        sales = parse_sales(D, chain, res['tok_px'], prices)
    out['sales'] = sales_summary(sales) if sales else {}
    out['sales_n_raw'] = len(sales)
    sel = (D.get('_perps_dir').parent / chain / 've_sales_selection.json.gz') if D.get('_perps_dir') else None
    if sel and sel.exists():
        out['sales_selection'] = read_gz(sel)
    # by venue (contract the transaction called); names from Basescan verified sources, read 2026-10-10
    names = {'0x6b478209974bd27e6cf661fef86c68072b0d6738': 'VexyMarketplace (listings)',
             '0x2903ee1a9dc4c8230651004d11f733787a0f69c4': 'VexyOffers (bids)',
             '0xbddcf6ab290e7ad076ca103183730d1bf0661112': 'unverified contract',
             '0x0000000000000068f116a894984e2db1123eb395': 'Seaport 1.6',
             '0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789': 'ERC-4337 EntryPoint'}
    okk = [x for x in sales if -0.5 < x['discount'] < 0.99]
    byv = {}
    for x in okk:
        byv.setdefault((x.get('via') or '').lower(), []).append(x)
    recent_cut = time.time() - 365 * DAY
    out['sales_by_venue'] = []
    for via, xs in sorted(byv.items(), key=lambda kv: -sum(x['value_usd'] for x in kv[1]))[:8]:
        rec_ = [x['discount'] for x in xs if x['ts'] >= recent_cut]
        out['sales_by_venue'].append({'via': via, 'name': names.get(via), 'n': len(xs), 'value_usd': sum(x['value_usd'] for x in xs),
                                      'median_discount': med([x['discount'] for x in xs]), 'n_last_365d': len(rec_),
                                      'median_discount_last_365d': med(rec_), 'paid_in_token': sum(1 for x in xs if x['paid_in_token'])})
    # entry variant: buy a lock at discount d (capital 1 - d + m per unit of underlying), hedge the full underlying,
    # sell later at the same discount: the exit costs nothing extra, the risk is the discount moving
    ent = {}
    for label, dd in (('vexy_listings_last_365d', next((v['median_discount_last_365d'] for v in out['sales_by_venue'] if v['name'] and 'listings' in v['name']), None)),
                      ('vexy_offers_last_365d', next((v['median_discount_last_365d'] for v in out['sales_by_venue'] if v['name'] and 'bids' in v['name']), None)),
                      ('all_sales_last_365d', (out['sales'].get('last_365d') or {}).get('median_discount'))):
        if dd is None:
            continue
        row = {'discount': dd}
        for name in ('avg/$5M/always', 'avg/$5M/best-venue'):
            dec_ = (carry.get('decomposition') or {}).get(name, {}).get('out_of_sample')
            if not dec_:
                v_ = (carry.get('variants') or {}).get(name)
                if not v_:
                    continue
                r_on_cap = (v_['out_of_sample'].get('ann_excess') or 0) + SSR
            else:
                r_on_cap = dec_['ret']
            scaled = r_on_cap * (1 + MARGIN) / (1 - dd + MARGIN)
            row[name] = {'ret_on_capital': scaled, 'excess': scaled - SSR}
        ent[label] = row
    out['entry_at_discount'] = ent
    # annuity: what a perpetual hedged lock is worth per unit of notional at the savings rate (+ spreads)
    dec = carry.get('decomposition', {}).get('avg/$5M/always', {})
    y = None
    if dec.get('out_of_sample'):
        y = dec['out_of_sample']['ret'] * (1 + MARGIN)          # net carry per unit of notional
        out['annuity'] = {'net_carry_per_notional_oos': y,
                          'value_per_notional_at': {str(r): annuity_value(y, r) for r in (SSR, SSR + 0.05, SSR + 0.10)} if y and y > 0 else None}
    return out


def out_dir_perps(D):
    return D.get('_perps_dir')


def live_block(out, res, D, chain):
    """The epoch in progress at collection time: fees deposited at its start, bribes posted so far, votes now."""
    c = CHAINS[chain]
    reg = D['reg']
    cur = res['cur']
    prices = res['prices']
    majors = MAJORS.get(chain, {})
    fees = bribes = 0.0
    for i, kind, t, e, amt in D['rew']['rows']:
        if e != cur:
            continue
        dec = (D['toks'].get(t) or {}).get('decimals') or 18
        p = None
        day = reg['ts'] - reg['ts'] % DAY - DAY
        tier, p = prices.tier(t, day, majors)
        if tier == 'unpriced':
            pp, _ = prices.get(t, cur - DAY)     # decision-time lookup of the last complete epoch
            tier, p = ('priced', pp) if pp else ('unpriced', 0.0)
        usd = int(amt) / 10 ** dec * (p or 0.0) * (1 - HAIRCUT[tier])
        if kind == 'fees':
            fees += usd
        else:
            bribes += usd
    votes = (reg['now']['total_weight'] or 0) / 1e18
    P = res['tok_px'](reg['ts'] - reg['ts'] % DAY - DAY)
    cap = perp_capacity(out)
    live = {'epoch': ymd(cur), 'collected_at': utc(reg['ts']), 'fees_usd_known': fees, 'bribes_usd_so_far': bribes,
            'votes_now': votes, 'price': P, 've_locked': (reg['now']['ve_locked'] or 0) / 1e18,
            've_permanent_share': (reg['now']['ve_permanent'] or 0) / max(1, reg['now']['ve_locked'] or 1)}
    if votes and P:
        live['indicative_voter_apr_so_far'] = (fees + bribes) / votes * EPOCHS_PER_YEAR / P
    fn = {}
    for v, per_day in (('binance', 6), ('bybit', 6), ('hl', 24)):
        f = (cap.get(v) or {}).get('funding_now')
        if f is not None:
            fn[v] = f * per_day * 365
    live['funding_now_ann'] = fn
    live['epochs_left_before_merger'] = (MERGER_TS - cur) // WEEK
    return live



# ---------------------------------------------------------------------------------------------- render
def pct(x, k=2):
    return '—' if x is None else ('%+.*f%%' % (k, 100 * x))


def pc(x, k=1):
    return '—' if x is None else ('%.*f%%' % (k, 100 * x))


def usd(x):
    if x is None:
        return '—'
    a = abs(x)
    return ('$%.1fB' % (x / 1e9)) if a >= 1e9 else ('$%.1fM' % (x / 1e6)) if a >= 1e6 else ('$%.0fk' % (x / 1e3)) if a >= 1e3 else '$%.0f' % x


def num(x, k=2):
    return '—' if x is None else '%.*f' % (k, x)


def render_carry(L, b, label):
    cp = b.get('carry') or {}
    ct = cp.get('choose_then_test') or {}
    L += ['', '## Hedged carry (%s): excess over SSR on capital (1 + 1/3 per unit of notional), weekly, annualised' % label, '',
          'Test split at %s; chosen on the first half: **%s**; out-of-sample rank %s of %s; OOS Newey-West t %s.' % (
              cp.get('cutoff_epoch'), ct.get('chosen'), ct.get('oos_rank'), ct.get('n_variants'), num(ct.get('oos_t'))), '',
          '| variant | in sample | out of sample | OOS t | OOS boot 95% | OOS max DD | last 52 | last 26 |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name, v in (cp.get('variants') or {}).items():
        o = v['out_of_sample']
        L.append('| %s | %s | %s | %s | %s..%s | %s | %s | %s |' % (
            name, pct(v['in_sample'].get('ann_excess')), pct(o.get('ann_excess')), num(o.get('nw_t')),
            pct(o.get('boot_lo'), 1), pct(o.get('boot_hi'), 1), pc(o.get('max_dd')), pct(v['last_52'].get('ann_excess')),
            pct(v['last_26'].get('ann_excess'))))
    if cp.get('test_stability'):
        L += ['', '### Inside the test window', '', '| row | first half | t | second half | t | split | best 4 weeks / total | weeks > 0 |', '|---|---:|---:|---:|---:|---|---:|---:|']
        for name, v in cp['test_stability'].items():
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (name, pct(v['test_first_half'].get('ann_excess')), num(v['test_first_half'].get('nw_t')),
                                                                pct(v['test_second_half'].get('ann_excess')), num(v['test_second_half'].get('nw_t')),
                                                                v['test_halves_split_epoch'], pc(v['best4_share_of_total']), pc(v['weeks_positive_share'], 0)))
    if cp.get('sensitivity'):
        L += ['', '### Sensitivities (not candidates in the choice)', '', '| row | in sample | out of sample | OOS t | last 52 |', '|---|---:|---:|---:|---:|']
        for name, v in cp['sensitivity'].items():
            L.append('| %s | %s | %s | %s | %s |' % (name, pct(v['in_sample'].get('ann_excess')), pct(v['out_of_sample'].get('ann_excess')),
                                                  num(v['out_of_sample'].get('nw_t')), pct(v['last_52'].get('ann_excess'))))
    L += ['', '### Decomposition (annualised, on capital)', '', '| variant | part | rewards | rebase | funding | basis | return | excess over SSR |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    for name, d in (cp.get('decomposition') or {}).items():
        for part in ('in_sample', 'out_of_sample', 'full'):
            r = d.get(part) or {}
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (name, part, pct(r.get('rewards')), pct(r.get('rebase')),
                                                                    pct(r.get('funding')), pct(r.get('basis')), pct(r.get('ret')), pct(r.get('excess'))))
    L += ['', '### By year (avg vote, $5M, always on)', '', '| year | rewards | rebase | funding | basis | excess |', '|---|---:|---:|---:|---:|---:|']
    if not cp:
        return
    for y, r in sorted(((cp.get('by_year') or {}).get('avg/$5M/always') or {}).items()):
        L.append('| %s | %s | %s | %s | %s | %s |' % (y, pct(r['rewards']), pct(r['rebase']), pct(r['funding']), pct(r['basis']), pct(r['excess'])))


def render(out, log):
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# ve_carry tables (generated from analysis.json; %s)' % A['generated_at'], '']
    b = A.get('base') or {}
    L += ['## Voter economics, Aerodrome (average vote, permanent lock, rewards priced at claim + 1 day, haircut)', '',
          '| year | epochs | rewards | fees | bribes | majors share | voter APR mean | median | rebase APR | AERO mean | votes mean | top-10 pools share | reward/vote dispersion | votes in pools < half avg |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for y, r in sorted((b.get('by_year') or {}).items()):
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | $%s | %sM | %s | %s | %s |' % (
            y, r['epochs'], usd(r['rewards_usd']), usd(r['fees_usd']), usd(r['bribes_usd']), pc(r['majors_share']),
            pc(r['voter_apr_mean']), pc(r['voter_apr_median']), pc(r['rebase_apr_mean']), num(r['p_mean'], 3),
            num((r['votes_mean'] or 0) / 1e6, 0), pc(r['top10_share_mean']), pc(r.get('rpv_dispersion_mean')), pc(r.get('votes_below_half_avg_mean'))))
    h = b.get('hedge') or {}
    L += ['', '## AERO perp funding received by a short, annualised (mean of epochs)', '',
          '| year | Binance | Bybit | OKX | Hyperliquid |', '|---|---:|---:|---:|---:|']
    for y, r in sorted((h.get('by_year') or {}).items()):
        L.append('| %s | %s | %s | %s | %s |' % (y, pct(r.get('binance')), pct(r.get('bybit')), pct(r.get('okx')), pct(r.get('hl'))))
    L.append('\nVenue used (pre-committed: Binance once listed, Bybit before): %s; epochs where shorts paid: %s; mean used %s, last 26 epochs %s.' % (
        h.get('venue_epochs'), pc(h.get('share_epochs_shorts_pay')), pct(h.get('mean_funding_ann_used')), pct(h.get('last_26_funding_ann_used'))))
    render_carry(L, b, 'Aerodrome, AERO perps')
    att = b.get('attentive') or {}
    L += ['', '## Attentive voter: reward per vote over the average vote (own dilution included)', '',
          '| lock | rule | mean premium | median | APR gain | 1st half | 2nd half | last 52 | epochs > avg | pools |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for size, d in sorted(att.items(), key=lambda kv: float(kv[0])):
        for rule in ('prev', 'early', 't24', 't1', 'oracle'):
            r = d.get(rule) or {}
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                usd(float(size)), rule, pct(r.get('mean_premium'), 1), pct(r.get('median_premium'), 1), pct(r.get('mean_apr_gain')),
                pct(r.get('first_half_apr_gain')), pct(r.get('second_half_apr_gain')), pct(r.get('last_52_apr_gain')),
                pc(r.get('share_epochs_positive'), 0), num(r.get('mean_npools'), 1)))
        L.append('| %s | t1 − t24 | %s of the average | | | | | | | |' % (usd(float(size)), pct(d.get('t1_minus_t24_over_avg'), 2)))
    tm = b.get('timing') or {}
    L += ['', 'Timing: rewards notified in the last 24 h %s of the epoch total (last hour %s); votes that moved in the last 24 h %s of all votes (last hour %s).' % (
        pc(tm.get('late24_share_of_rewards')), pc(tm.get('late1_share_of_rewards')), pc(tm.get('votes_moved_last24h_share')), pc(tm.get('votes_moved_last1h_share')))]
    ex = b.get('exit') or {}
    L += ['', '## Exit', '', '| variant | OOS excess | break-even discount after 3 / 6 / 12 / 24 months |', '|---|---:|---|']
    for name, v in ex.items():
        if isinstance(v, dict) and 'breakeven_discount_after_months' in v:
            bd = v['breakeven_discount_after_months']
            L.append('| %s | %s | %s |' % (name, pct(v['oos_ann_excess']), ' / '.join(pc(bd.get(k)) for k in ('3', '6', '12', '24'))))
    sa = ex.get('sales') or {}
    L += ['', 'veNFT sales (transfer + payment in the same transaction), discount to the locked AERO at the day\'s price:', '',
          '| slice | n | value | paid | median | p25 | p75 | value-weighted |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in sa.items():
        if isinstance(v, dict) and 'n' in v and v['n']:
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (k, v['n'], usd(v['value_usd']), usd(v['paid_usd']), pc(v['median_discount']),
                                                                   pc(v['p25']), pc(v['p75']), pc(v['value_weighted_discount'])))
    if ex.get('sales_by_venue'):
        L += ['', '| venue | n | locked value | median discount | n last 365 days | median last 365 days | paid in AERO |', '|---|---:|---:|---:|---:|---:|---:|']
        for v in ex['sales_by_venue']:
            L.append('| %s %s | %d | %s | %s | %d | %s | %d |' % (v['name'] or '', v['via'][:10], v['n'], usd(v['value_usd']), pc(v['median_discount']),
                                                              v['n_last_365d'], pc(v['median_discount_last_365d']), v['paid_in_token']))
    if ex.get('entry_at_discount'):
        L += ['', 'Entry at a discount (buy a lock at d, hedge the full underlying, exit at the same d), test-window excess over SSR:', '']
        for k, v in ex['entry_at_discount'].items():
            L.append('- %s, d = %s: average vote, main venue %s; best venue %s' % (k, pc(v['discount']), pct((v.get('avg/$5M/always') or {}).get('excess')),
                                                                                  pct((v.get('avg/$5M/best-venue') or {}).get('excess'))))
    ia = ex.get('iaero') or {}
    if ia:
        L.append('\niAERO (liquid permanently locked veAERO; minted at 0.95 per AERO): price/AERO last %s (%s), 90-day mean %s, range %s..%s since %s; exit cost by minting and selling now %s; pools %s.' % (
            num(ia.get('ratio_last'), 3), ia.get('last_day'), num(ia.get('ratio_mean_90d'), 3), num(ia.get('ratio_min'), 3), num(ia.get('ratio_max'), 3),
            ia.get('first_day'), pc(ia.get('exit_cost_via_mint_last')), ia.get('pools')))
    cap = A.get('perp_capacity') or {}
    L += ['', '## Capacity (books read %s)' % (b.get('live') or {}).get('collected_at', ''), '',
          '| venue | OI | 24h volume | bids within 0.5% / 1% / 2% | asks within 1% | funding now (ann.) |', '|---|---:|---:|---|---:|---:|']
    lv = (b.get('live') or {}).get('funding_now_ann') or {}
    for v in ('binance', 'bybit', 'okx', 'hl', 'bybit_spot', 'coinbase_spot'):
        r = cap.get(v)
        if not r:
            continue
        L.append('| %s | %s | %s | %s / %s / %s | %s | %s |' % (v, usd(r.get('oi_usd')), usd(r.get('vol24h_usd')), usd(r.get('bid_0.5pct')),
                                                               usd(r.get('bid_1pct')), usd(r.get('bid_2pct')), usd(r.get('ask_1pct')), pct(lv.get(v))))
    L.append('\nTotal AERO perp OI: %s. Binance VELODROMEUSDT: %s.' % (usd(cap.get('perp_oi_total_usd')), cap.get('binance_velodrome')))
    live = b.get('live') or {}
    L += ['', '## Live (epoch %s, %s)' % (live.get('epoch'), live.get('collected_at')), '',
          '- fees known %s, bribes so far %s, votes %sM, AERO $%s: indicative voter APR so far %s (bribes still arriving)' % (
              usd(live.get('fees_usd_known')), usd(live.get('bribes_usd_so_far')), num((live.get('votes_now') or 0) / 1e6, 0),
              num(live.get('price'), 3), pc(live.get('indicative_voter_apr_so_far'))),
          '- locked %sM AERO, %s of it permanent; epochs left before the merger: %s' % (
              num((live.get('ve_locked') or 0) / 1e6, 0), pc(live.get('ve_permanent_share')), live.get('epochs_left_before_merger'))]
    ck = b.get('checks') or {}
    L += ['', '## Checks', '', '- events vs storage: %s' % ck.get('events_vs_storage'), '- Sugar vs storage: %s' % ck.get('sugar_vs_storage')]
    q = b.get('quarterly') or {}
    xc = A.get('external_check_aero_xyz') or {}
    L += ['', '| quarter | fees (ours, Base, haircut) | bribes (ours, haircut) | gross, Base + Optimism | aero.xyz revenue (all chains) | ratio |', '|---|---:|---:|---:|---:|---:|']
    for k in sorted(q):
        x = xc.get(k) or {}
        L.append('| %s | %s | %s | %s | %s | %s |' % (k, usd(q[k]['fees_usd']), usd(q[k]['bribes_usd']), usd(x.get('ours_gross_both_chains')),
                                                    usd(q[k].get('aero_xyz_all_chains')), num(x.get('ratio'), 2)))
    o = A.get('optimism')
    if o:
        L += ['', '## Velodrome (Optimism), average vote', '', '| year | rewards | fees | bribes | voter APR mean | median | rebase APR | VELO mean |', '|---|---:|---:|---:|---:|---:|---:|---:|']
        for y, r in sorted((o.get('by_year') or {}).items()):
            L.append('| %s | %s | %s | %s | %s | %s | %s | $%s |' % (y, usd(r['rewards_usd']), usd(r['fees_usd']), usd(r['bribes_usd']), pc(r['voter_apr_mean']),
                                                         pc(r['voter_apr_median']), pc(r['rebase_apr_mean']), num(r['p_mean'], 4)))
        oh = o.get('hedge') or {}
        L.append('\nVELODROMEUSDT (Binance) funding to a short by year: %s; mean %s, last 26 epochs %s.' % (
            {y: pct(v.get('binance')) for y, v in sorted((oh.get('by_year') or {}).items())}, pct(oh.get('mean_funding_ann_used')), pct(oh.get('last_26_funding_ann_used'))))
        render_carry(L, o, 'Velodrome, Binance VELODROMEUSDT')
        oa = o.get('attentive') or {}
        if oa:
            L += ['', '| Velodrome lock | rule | mean premium | APR gain | 2nd half |', '|---|---|---:|---:|---:|']
            for size, d in sorted(oa.items(), key=lambda kv: float(kv[0])):
                for rule in ('prev', 'early', 't24', 't1'):
                    r = d.get(rule) or {}
                    L.append('| %s | %s | %s | %s | %s |' % (usd(float(size)), rule, pct(r.get('mean_premium'), 1), pct(r.get('mean_apr_gain')), pct(r.get('second_half_apr_gain'))))
        L += ['', '- Velodrome checks: %s' % o.get('checks')]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    log('tables.md written')



# ---------------------------------------------------------------------------------------------- manifest
API_GAPS = [
    'OKX public funding history reaches back only to 2026-06-29 (621 settlements); the OKX hedge is descriptive only',
    'Hyperliquid lists AERO from 2025-11-11; Binance from 2024-12-04; Bybit from 2024-07-15: no hedge exists before 2024-07-15',
    'Binance open-interest history is served for 30 days only; capacity uses the live OI and books',
    "Bybit's VELOUSDT is Velo (price ~$0.005), not Velodrome; Velodrome's perp is Binance VELODROMEUSDT only",
    'RewardsSugar.epochsByAddress returns nothing for killed gauges (survivorship); history is read from the reward contracts directly',
    'live_rpc raises -32603 "service temporarily unavailable" without retry or log; ve_carry retries it (Chain.call_retry)',
    'the Base MetaDEX (sAERO) contracts are not published as of 2026-10-10: post-merger economics are not measurable',
    'iAERO (liquid veAERO) docs were not reachable this session: the liquid-locker discount is not measured',
]


def write_manifest(out, A=None):
    files = []
    for f in sorted((out / 'raw').rglob('*')):
        if f.is_file() and not f.name.endswith('.tmp'):
            files.append({'path': str(f.relative_to(out)), 'bytes': f.stat().st_size})
    m = {'generated_at': dt.datetime.now(UTC).isoformat(timespec='seconds'), 'script': 'scripts/ve_carry.py',
         'tests': 'scripts/test_ve_carry.py',
         'contracts': {k: {kk: vv for kk, vv in v.items() if kk not in ('rpc',)} for k, v in CHAINS.items()},
         'contract_sources': ['https://github.com/aerodrome-finance/contracts (README deployment table)',
                              'https://github.com/velodrome-finance/sugar/tree/main/deployments (base.env, optimism.env)',
                              'Voter.ve() on chain matches both VotingEscrow addresses'],
         'endpoints': ['Infura base-mainnet / optimism-mainnet via scripts/live_rpc.py (eth_call through Multicall3 '
                       '0xcA11bde05977b3631167028862bE2a173976CA11, eth_getLogs in 10k-block chunks, archive reads)',
                       'coins.llama.fi/batchHistorical (1.2 s between calls)', 'fapi.binance.com', 'api.bybit.com',
                       'www.okx.com', 'api.hyperliquid.xyz/info (4 s between calls)', 'api.exchange.coinbase.com'],
         'api_gaps': API_GAPS, 'files': files}
    if A:
        m['analysis_keys'] = sorted(A.keys())
    log_f = out / 'raw' / 'collect.log'
    if log_f.exists():
        m['collect_log_tail'] = log_f.read_text().splitlines()[-40:]
    write_json(out / 'manifest.json', m)


# ---------------------------------------------------------------------------------------------- main (collect stub)
def _log_to(path):
    def log(msg):
        line = '%s %s' % (dt.datetime.now(UTC).strftime('%H:%M:%S'), msg)
        print(line, flush=True)
        with open(path, 'a') as f:
            f.write(line + '\n')
    return log


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['collect', 'analyze', 'render'])
    ap.add_argument('--out', default='research/2026-10-10/ve_carry')
    ap.add_argument('--parts', default='registry,epochs')
    ap.add_argument('--chains', default='base')
    a = ap.parse_args()
    out = (ROOT / a.out) if not Path(a.out).is_absolute() else Path(a.out)
    (out / 'raw').mkdir(parents=True, exist_ok=True)
    log = _log_to(out / 'raw' / 'collect.log')
    if a.cmd == 'collect':
        parts = a.parts.split(',')
        for chain in a.chains.split(','):
            if 'registry' in parts:
                collect_registry(out, chain, log)
            if 'epochs' in parts:
                collect_epochs(out, chain, log)
            if 'logs' in parts:
                collect_logs(out, chain, log)
            if 'verify' in parts:
                verify_votes(out, chain, log)
            if 'prices' in parts:
                collect_prices(out, chain, log)
            if 'sales' in parts:
                collect_sales(out, chain, log)
        if 'perps' in parts:
            collect_perps(out, log)
    elif a.cmd == 'analyze':
        analyze(out, a.chains.split(','), log)
    elif a.cmd == 'render':
        render(out, log)


if __name__ == '__main__':
    main()
