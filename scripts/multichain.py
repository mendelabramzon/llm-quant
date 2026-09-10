#!/usr/bin/env python3
"""One trailing hour, read on every EVM at once: the dollar rate surface, the bridge that connects it, and the gas
market underneath it.

Everything this repo has measured so far has been one chain at a time, and the strategy book that came out of it is
Ethereum-only. That is a real blind spot for a dollar: USDC on Base and USDC on Ethereum are the *same claim on the
same issuer*, redeemable into each other in minutes over CCTP for a fee that is usually zero, so their lending rates
are two prices for one asset. A gap between them is not a spread between two risks; it is a spread inside one risk,
and the only things that can hold it open are latency, gas, and attention.

Design rule, learned from this repo's four mislabels: **discover, do not assert**. Nothing here is keyed off a
remembered contract address.

* Lending markets are found by scanning the whole chain for one topic — `ReserveDataUpdated` — so every Aave-v3-family
  deployment on every chain (Aave itself, and its forks) announces itself by emitting, and the same query that finds
  the market hands back its full intra-hour rate path for free. That path is what lets a rate be de-spiked instead of
  believed, which is the failure mode the roadmap calls out as still open ("head reads are still spot").
* The bridge is found the same way, by `DepositForBurn` / `MintAndWithdraw` topics, and each emitter is then asked
  on-chain for its own Circle domain id (`localMessageTransmitter()` → `localDomain()`), so the chain↔domain map is
  verified rather than recalled. USDC's address on each chain falls out of the same logs as the indexed `burnToken`.
* Token identity is checked at the head (`symbol()`, `decimals()`) and a mismatch is reported, never silently used.

    uv run --with pycryptodome python scripts/multichain.py collect --out research/2026-09-08/multi_1h --hours 1
    uv run --with pycryptodome python scripts/multichain.py head    --out research/2026-09-08/multi_1h
    uv run --with pycryptodome python scripts/multichain.py analyze --out research/2026-09-08/multi_1h   # offline
    uv run --with pycryptodome python scripts/multichain.py render  --out research/2026-09-08/multi_1h   # offline
"""
import argparse
import collections
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from Crypto.Hash import keccak as _keccak
from live_rpc import RPC, RPCError, hx, word, enc_addr

RAY = 1e27


def keccak(s):
    k = _keccak.new(digest_bits=256)
    k.update(s.encode())
    return '0x' + k.hexdigest()


def sel(s):
    return keccak(s)[:10]


def utc(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec='seconds')


# chain -> (chain id, Infura network host, native symbol, seconds per block (nominal, only used to seed the search))
CHAINS = {
    'ethereum':  (1,      'mainnet',           'ETH',   12.0),
    'base':      (8453,   'base-mainnet',      'ETH',    2.0),
    'arbitrum':  (42161,  'arbitrum-mainnet',  'ETH',    0.25),
    'optimism':  (10,     'optimism-mainnet',  'ETH',    2.0),
    'polygon':   (137,    'polygon-mainnet',   'POL',    2.0),
    'avalanche': (43114,  'avalanche-mainnet', 'AVAX',   2.0),
    'bsc':       (56,     'bsc-mainnet',       'BNB',    0.75),
    'unichain':  (130,    'unichain-mainnet',  'ETH',    1.0),
    'linea':     (59144,  'linea-mainnet',     'ETH',    3.0),
    'scroll':    (534352, 'scroll-mainnet',    'ETH',    3.0),
}
DEFAULT_CHAINS = 'ethereum,base,arbitrum,optimism,polygon,avalanche,bsc,unichain,linea,scroll'

# Event topics. Signatures are written out in full so the constant is the derivation, not a remembered hash.
T_RESERVE_DATA = keccak('ReserveDataUpdated(address,uint256,uint256,uint256,uint256,uint256)')
T_BURN_V1 = keccak('DepositForBurn(uint64,address,uint256,address,bytes32,uint32,bytes32,bytes32)')
T_BURN_V2 = keccak('DepositForBurn(address,uint256,address,bytes32,uint32,bytes32,bytes32,uint256,uint32,bytes)')
T_MINT_V1 = keccak('MintAndWithdraw(address,uint256,address)')
T_MINT_V2 = keccak('MintAndWithdraw(address,uint256,address,uint256)')
T_TRANSFER = keccak('Transfer(address,address,uint256)')
ZERO32 = '0x' + '0' * 64

TOPIC_SETS = {
    'reserve_data': [T_RESERVE_DATA],
    'cctp_burn': [T_BURN_V1, T_BURN_V2],
    'cctp_mint': [T_MINT_V1, T_MINT_V2],
}

# Circle domain ids that no chain in this scan can be asked for directly. Verified domains come from the chain itself
# (see `head`); these are model memory and are labelled as such wherever they are printed.
DOMAIN_MEMORY = {4: 'noble', 5: 'solana', 8: 'sui', 9: 'aptos', 12: 'codex', 13: 'sonic', 14: 'worldchain'}

# Chainlink native/USD feeds, used only through the repo's description() check: a feed whose description() does not
# match the expected pair contributes no price and is reported as a miss.
NATIVE_FEEDS = {
    'polygon':   ('0xab594600376ec9fd91f8e885dadf0ce036862de0', ('POL / USD', 'MATIC / USD')),
    'avalanche': ('0x0a77230d17318075983913bc2145db16c7366156', ('AVAX / USD',)),
    'bsc':       ('0x0567f2323251f0aab15c8dfb1967e4e8a7d42aee', ('BNB / USD',)),
    'ethereum':  ('0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419', ('ETH / USD',)),
}

SEL = {k: sel(k) for k in (
    'symbol()', 'decimals()', 'description()', 'latestRoundData()', 'totalSupply()',
    'getReservesList()', 'localMessageTransmitter()', 'localDomain()', 'version()',
)}
SEL_RESERVE_DATA = sel('getReserveData(address)')
SEL_IRD_BPS = sel('getInterestRateDataBps(address)')
SEL_VIRTUAL = sel('getVirtualUnderlyingBalance(address)')
SEL_OPTIMAL = sel('OPTIMAL_USAGE_RATIO()')
SEL_BASE = sel('getBaseVariableBorrowRate()')
SEL_S1 = sel('getVariableRateSlope1()')
SEL_S2 = sel('getVariableRateSlope2()')


def write_gz(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(value, f, separators=(',', ':'))
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True))


def rpc_for(chain, out=None, max_credits=3_000_000):
    _, host, _, _ = CHAINS[chain]
    return RPC(log_path=(Path(out) / 'rpc_errors.jsonl') if out else None, max_credits=max_credits,
               url='https://%s.infura.io/v3/' % host)


def dec_str(data):
    """ABI-decode a string return, tolerating the bytes32 form some old tokens use."""
    if not data or data == '0x':
        return None
    b = bytes.fromhex(data[2:])
    if len(b) >= 64:
        try:
            n = int.from_bytes(b[32:64], 'big')
            if 0 < n <= len(b) - 64:
                return b[64:64 + n].decode('utf-8', 'replace')
        except Exception:
            pass
    return b.rstrip(b'\x00').decode('utf-8', 'replace') or None


# ---------------------------------------------------------------------------------------------- collect

def header(rpc, n):
    b = rpc.call('eth_getBlockByNumber', [hex(n), False])
    if not b:
        raise RPCError('no block %d' % n)
    return b


def first_block_at(rpc, ts, head_n, spb):
    """First block whose timestamp is >= ts. Walks back in strides, then bisects; no assumption of constant spacing."""
    stride = max(64, int(3600 / max(spb, 0.05)))
    lo = max(1, head_n - stride)
    while lo > 1:
        b = header(rpc, lo)
        if hx(b['timestamp']) < ts:
            break
        lo = max(1, lo - stride)
        stride *= 2
    hi = head_n
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if hx(header(rpc, mid)['timestamp']) >= ts:
            hi = mid
        else:
            lo = mid
    return hi


def get_logs_range(rpc, first, last, topics, max_span=9000, depth=0):
    """eth_getLogs over [first,last] for one topic0, split on both the block-range cap and the result cap."""
    if last < first:
        return []
    if last - first + 1 > max_span:
        mid = (first + last) // 2
        return get_logs_range(rpc, first, mid, topics, max_span, depth) + \
               get_logs_range(rpc, mid + 1, last, topics, max_span, depth)
    try:
        return rpc.call('eth_getLogs', [{'fromBlock': hex(first), 'toBlock': hex(last), 'topics': topics}])
    except RPCError as exc:
        msg = str(exc).lower()
        splittable = 'more than' in msg or '10000' in msg or 'query timeout' in msg or 'response size' in msg or 'limit' in msg
        if first == last or depth > 14 or not splittable:
            raise
        mid = (first + last) // 2
        return get_logs_range(rpc, first, mid, topics, max_span, depth + 1) + \
               get_logs_range(rpc, mid + 1, last, topics, max_span, depth + 1)


def sample_headers(rpc, first, last, n=60):
    span = last - first
    nums = sorted({first + round(span * i / max(n - 1, 1)) for i in range(n)} | {first, last})
    rows = []
    for i in range(0, len(nums), 20):
        part = nums[i:i + 20]
        res = rpc.batch([('eth_getBlockByNumber', [hex(x), False]) for x in part], allow_errors=True)
        for x, b in zip(part, res):
            if isinstance(b, dict) and b.get('number'):
                rows.append({'n': hx(b['number']), 'ts': hx(b['timestamp']), 'gas_used': hx(b['gasUsed']),
                             'gas_limit': hx(b['gasLimit']), 'base_fee': hx(b.get('baseFeePerGas') or '0x0'),
                             'txs': len(b.get('transactions') or [])})
    return sorted(rows, key=lambda r: r['n'])


def collect_chain(chain, out, hours, samples):
    cdir = Path(out) / chain
    cdir.mkdir(parents=True, exist_ok=True)
    rpc = rpc_for(chain, out=cdir)
    t0 = time.time()
    hb = header(rpc, hx(rpc.call('eth_getBlockByNumber', ['latest', False])['number']))
    head_n, head_ts = hx(hb['number']), hx(hb['timestamp'])
    _, _, native, spb = CHAINS[chain]
    first = first_block_at(rpc, head_ts - int(hours * 3600), head_n, spb)
    meta = {'chain': chain, 'chain_id': CHAINS[chain][0], 'native': native,
            'first_block': first, 'last_block': head_n, 'blocks': head_n - first + 1,
            'first_ts': hx(header(rpc, first)['timestamp']), 'last_ts': head_ts,
            'collected_at': utc(time.time()), 'hours_requested': hours, 'logs': {}}
    meta['first_utc'], meta['last_utc'] = utc(meta['first_ts']), utc(meta['last_ts'])
    meta['seconds'] = meta['last_ts'] - meta['first_ts']
    meta['headers'] = sample_headers(rpc, first, head_n, samples)
    for name, tops in TOPIC_SETS.items():
        rows = []
        for t in tops:
            rows += get_logs_range(rpc, first, head_n, [t])
        rows.sort(key=lambda l: (hx(l['blockNumber']), hx(l['logIndex'])))
        write_gz(cdir / ('logs_%s.json.gz' % name), rows)
        meta['logs'][name] = len(rows)
    meta['rpc'] = rpc.stats()
    meta['collect_seconds'] = round(time.time() - t0, 1)
    write_json(cdir / 'chain.json', meta)
    return meta


def cmd_collect(args):
    out = Path(args.out)
    chains = [c.strip() for c in args.chains.split(',') if c.strip()]
    results, errors = {}, {}
    with cf.ThreadPoolExecutor(max_workers=min(len(chains), args.workers)) as ex:
        futs = {ex.submit(collect_chain, c, out, args.hours, args.samples): c for c in chains}
        for f in cf.as_completed(futs):
            c = futs[f]
            try:
                results[c] = f.result()
                print(json.dumps({'chain': c, 'blocks': results[c]['blocks'], 'logs': results[c]['logs'],
                                  'seconds': results[c]['collect_seconds'], 'credits': results[c]['rpc']['credits']}))
            except Exception as exc:
                errors[c] = type(exc).__name__ + ': ' + str(exc)[:300]
                print(json.dumps({'chain': c, 'error': errors[c]}))
    # A partial re-run must not erase the chains that already succeeded, so the manifest is rebuilt from whatever
    # per-chain `chain.json` files exist on disk rather than from this invocation's results alone.
    window, credits = {}, 0
    for d in sorted(out.iterdir()):
        f = d / 'chain.json'
        if d.is_dir() and f.exists():
            m = json.loads(f.read_text())
            window[m['chain']] = {'first_block': m['first_block'], 'last_block': m['last_block'], 'blocks': m['blocks'],
                                  'first_utc': m['first_utc'], 'last_utc': m['last_utc'], 'seconds': m['seconds'],
                                  'logs': m['logs']}
            credits += m['rpc']['credits']
    write_json(out / 'manifest.json', {
        'collected_at': utc(time.time()), 'hours': args.hours, 'chains': sorted(window),
        'errors': {c: e for c, e in errors.items() if c not in window},
        'window': window, 'credits': credits,
    })
    return 0


# ---------------------------------------------------------------------------------------------- head

def decode_burn(log):
    """DepositForBurn, v1 and v2, told apart by shape rather than by trusting one signature."""
    t, d = log['topics'], log['data']
    words = (len(d) - 2) // 64
    if t[0] == T_BURN_V1 and len(t) == 4 and words >= 5:
        return {'v': 1, 'token': '0x' + t[2][-40:], 'depositor': '0x' + t[3][-40:],
                'amount': word(d, 0), 'dest_domain': word(d, 2), 'nonce': int(t[1], 16)}
    if t[0] == T_BURN_V2 and len(t) == 4 and words >= 8:
        return {'v': 2, 'token': '0x' + t[1][-40:], 'depositor': '0x' + t[2][-40:],
                'amount': word(d, 0), 'dest_domain': word(d, 2), 'max_fee': word(d, 5)}
    return None


def decode_mint(log):
    t, d = log['topics'], log['data']
    words = (len(d) - 2) // 64
    if t[0] in (T_MINT_V1, T_MINT_V2) and len(t) == 3 and words >= 1:
        return {'v': 1 if t[0] == T_MINT_V1 else 2, 'recipient': '0x' + t[1][-40:], 'token': '0x' + t[2][-40:],
                'amount': word(d, 0), 'fee': word(d, 1) if words >= 2 else 0}
    return None


def head_chain(chain, out):
    cdir = Path(out) / chain
    meta = json.loads((cdir / 'chain.json').read_text())
    rpc = rpc_for(chain, out=cdir)
    hs = {'chain': chain, 'read_at': utc(time.time()), 'block': hx(rpc.call('eth_getBlockByNumber', ['latest', False])['number'])}
    blk = hex(hs['block'])

    # --- native price, through the description() check
    hs['native_usd'] = None
    if chain in NATIVE_FEEDS:
        feed, want = NATIVE_FEEDS[chain]
        d, r, dec = rpc.eth_calls([(feed, SEL['description()']), (feed, SEL['latestRoundData()']), (feed, SEL['decimals()'])], blk)
        got = dec_str(d)
        if r and got and got.strip() in want:
            hs['native_usd'] = word(r, 1) / 10 ** (word(dec, 0) if dec else 8)
            hs['native_feed'] = {'feed': feed, 'description': got}
        else:
            hs['native_feed'] = {'feed': feed, 'description': got, 'error': 'description mismatch or call failed'}

    # --- CCTP: which contracts emitted, what domain this chain is, which token is USDC here
    burns = [decode_burn(l) for l in read_gz(cdir / 'logs_cctp_burn.json.gz')]
    mints = [decode_mint(l) for l in read_gz(cdir / 'logs_cctp_mint.json.gz')]
    emitters = sorted({l['address'].lower() for l in read_gz(cdir / 'logs_cctp_burn.json.gz')} |
                      {l['address'].lower() for l in read_gz(cdir / 'logs_cctp_mint.json.gz')})
    cctp = {'emitters': {}, 'local_domain': None}
    if emitters:
        tm = rpc.eth_calls([(a, SEL['localMessageTransmitter()']) for a in emitters], blk)
        transmitters = ['0x' + (x[-40:]) if x else None for x in tm]
        dm = rpc.eth_calls([(t, SEL['localDomain()']) for t in transmitters if t], blk)
        di = iter(dm)
        for a, t in zip(emitters, transmitters):
            dom = None
            if t:
                v = next(di)
                dom = word(v, 0) if v else None
            cctp['emitters'][a] = {'transmitter': t, 'local_domain': dom}
            if dom is not None:
                cctp['local_domain'] = dom
    cctp['unresolved_domain'] = cctp['local_domain'] is None and bool(emitters)
    hs['cctp'] = cctp

    # --- the USDC contract on this chain, as the bridge itself named it, then checked
    tokens = {}
    for x in burns + mints:
        if x:
            tokens[x['token'].lower()] = tokens.get(x['token'].lower(), 0) + 1
    hs['bridge_tokens'] = {}
    if tokens:
        addrs = sorted(tokens, key=lambda a: -tokens[a])[:5]
        res = rpc.eth_calls([(a, s) for a in addrs for s in (SEL['symbol()'], SEL['decimals()'], SEL['totalSupply()'])], blk)
        for i, a in enumerate(addrs):
            s, d, ts = res[3 * i], res[3 * i + 1], res[3 * i + 2]
            dec = word(d, 0) if d else None
            hs['bridge_tokens'][a] = {'symbol': dec_str(s), 'decimals': dec, 'legs': tokens[a],
                                      'total_supply': (word(ts, 0) / 10 ** dec) if (ts and dec is not None) else None}

    # --- lending: every pool that emitted a rate update, asked for its own reserve list and state
    rlogs = read_gz(cdir / 'logs_reserve_data.json.gz')
    pools = {}
    for l in rlogs:
        pools[l['address'].lower()] = pools.get(l['address'].lower(), 0) + 1
    pools = dict(sorted(pools.items(), key=lambda kv: -kv[1])[:args_max_pools])
    hs['pools'] = {}
    for pool, updates in pools.items():
        listed = rpc.eth_calls([(pool, SEL['getReservesList()'])], blk)[0]
        assets = []
        if listed and len(listed) >= 2 + 128:
            n = word(listed, 1)
            for i in range(min(n, 250)):
                assets.append('0x' + listed[2 + 64 * (2 + i):2 + 64 * (3 + i)][-40:])
        if not assets:
            hs['pools'][pool] = {'updates': updates, 'error': 'getReservesList() empty or not an Aave-v3 pool'}
            continue
        res = rpc.eth_calls([(pool, SEL_RESERVE_DATA + enc_addr(a)) for a in assets], blk)
        rows, meta_items, meta_keys = {}, [], []
        for a, r in zip(assets, res):
            if not r or len(r) < 2 + 64 * 12:
                continue
            atoken = '0x' + r[2 + 64 * 8:2 + 64 * 9][-40:]
            vdebt = '0x' + r[2 + 64 * 10:2 + 64 * 11][-40:]
            strategy = '0x' + r[2 + 64 * 11:2 + 64 * 12][-40:]
            rows[a] = {'supply_apr': word(r, 2) / RAY, 'borrow_apr': word(r, 4) / RAY, 'aToken': atoken,
                       'variableDebt': vdebt, 'strategy': strategy, 'config': word(r, 0)}
            meta_items += [(a, SEL['symbol()']), (a, SEL['decimals()']), (atoken, SEL['totalSupply()']),
                           (vdebt, SEL['totalSupply()']), (pool, SEL_VIRTUAL + enc_addr(a))]
            meta_keys.append(a)
        res2 = rpc.eth_calls(meta_items, blk)
        for i, a in enumerate(meta_keys):
            s, d, sup, dbt, virt = res2[5 * i:5 * i + 5]
            dec = word(d, 0) if d else None
            rows[a].update({'sym': dec_str(s), 'decimals': dec,
                            'supplied': (word(sup, 0) / 10 ** dec) if (sup and dec is not None) else None,
                            'borrowed': (word(dbt, 0) / 10 ** dec) if (dbt and dec is not None) else None,
                            'virtual': (word(virt, 0) / 10 ** dec) if (virt and dec is not None) else None})
            rows[a]['reserve_factor'] = ((rows[a]['config'] >> 64) & 0xFFFF) / 1e4
            sp, bo = rows[a]['supplied'], rows[a]['borrowed']
            rows[a]['utilisation'] = (bo / sp) if (sp and bo is not None and sp > 0) else None
        # rate curve: v3.2 packs the four parameters in one bps call; v3.0/v3.1 forks expose four ray getters
        strategies = sorted({r['strategy'] for r in rows.values() if r.get('strategy') and int(r['strategy'], 16)})
        curve_items, curve_keys = [], []
        for a, r in rows.items():
            if r.get('strategy') and int(r['strategy'], 16):
                curve_items.append((r['strategy'], SEL_IRD_BPS + enc_addr(a)))
                curve_keys.append(a)
        cres = rpc.eth_calls(curve_items, blk) if curve_items else []
        need_legacy = []
        for a, r in zip(curve_keys, cres):
            if r and len(r) >= 2 + 64 * 4:
                rows[a]['curve'] = {'optimal': word(r, 0) / 1e4, 'base': word(r, 1) / 1e4,
                                    'slope1': word(r, 2) / 1e4, 'slope2': word(r, 3) / 1e4, 'src': 'bps'}
            else:
                need_legacy.append(a)
        if need_legacy:
            items = []
            for a in need_legacy:
                st = rows[a]['strategy']
                items += [(st, SEL_OPTIMAL), (st, SEL_BASE), (st, SEL_S1), (st, SEL_S2)]
            lres = rpc.eth_calls(items, blk)
            for i, a in enumerate(need_legacy):
                o, b, s1, s2 = lres[4 * i:4 * i + 4]
                if o and s1:
                    rows[a]['curve'] = {'optimal': word(o, 0) / RAY, 'base': (word(b, 0) / RAY) if b else 0.0,
                                        'slope1': word(s1, 0) / RAY, 'slope2': (word(s2, 0) / RAY) if s2 else 0.0,
                                        'src': 'ray'}
        for a, r in rows.items():
            if r.get('curve'):
                r['curve']['reserve_factor'] = r['reserve_factor']
        hs['pools'][pool] = {'updates': updates, 'reserves': rows, 'strategies': strategies}
    hs['rpc'] = rpc.stats()
    # `head` rebuilds the state from scratch, so anything a later step appended has to be carried across or a re-read
    # silently deletes it. `issuance` is written by its own command after this one and is expensive to redo.
    prev = cdir / 'head_state.json'
    if prev.exists():
        old = json.loads(prev.read_text())
        for k in ('issuance', 'issuance_rpc'):
            if k in old:
                hs[k] = old[k]
    write_json(prev, hs)
    return hs


args_max_pools = 8


def cmd_head(args):
    global args_max_pools
    args_max_pools = args.max_pools
    out = Path(args.out)
    chains = [c for c in json.loads((out / 'manifest.json').read_text())['chains']]
    if args.chains:
        want = {c.strip() for c in args.chains.split(',')}
        chains = [c for c in chains if c in want]
    errors = {}
    with cf.ThreadPoolExecutor(max_workers=min(len(chains), args.workers)) as ex:
        futs = {ex.submit(head_chain, c, out): c for c in chains}
        for f in cf.as_completed(futs):
            c = futs[f]
            try:
                hs = f.result()
                print(json.dumps({'chain': c, 'pools': len(hs['pools']),
                                  'reserves': sum(len(p.get('reserves') or {}) for p in hs['pools'].values()),
                                  'domain': hs['cctp']['local_domain'], 'credits': hs['rpc']['credits']}))
            except Exception as exc:
                errors[c] = type(exc).__name__ + ': ' + str(exc)[:300]
                print(json.dumps({'chain': c, 'error': errors[c]}))
    if errors:
        write_json(out / 'head_errors.json', errors)
    return 0


# ---------------------------------------------------------------------------------------------- issuance

def issuance_chain(chain, out):
    """Native mint and burn of the bridge's own dollar on this chain, from Transfer legs against the zero address.

    Runs after `head` because the token address is not asserted: it is whatever CCTP burned and minted in this window,
    checked by `symbol()`. Two queries per token."""
    cdir = Path(out) / chain
    hs = json.loads((cdir / 'head_state.json').read_text())
    meta = json.loads((cdir / 'chain.json').read_text())
    rpc = rpc_for(chain, out=cdir)
    rows = {}
    for addr, t in (hs.get('bridge_tokens') or {}).items():
        if not t.get('symbol') or t.get('decimals') is None:
            continue
        dec = t['decimals']
        mints = get_logs_range(rpc, meta['first_block'], meta['last_block'], [T_TRANSFER, ZERO32])
        burns = get_logs_range(rpc, meta['first_block'], meta['last_block'], [T_TRANSFER, None, ZERO32])
        mints = [l for l in mints if l['address'].lower() == addr]
        burns = [l for l in burns if l['address'].lower() == addr]
        rows[addr] = {
            'symbol': t['symbol'], 'decimals': dec,
            'minted': sum(word(l['data'], 0) for l in mints) / 10 ** dec, 'mint_legs': len(mints),
            'burned': sum(word(l['data'], 0) for l in burns) / 10 ** dec, 'burn_legs': len(burns),
            'mint_to': _top(collections.Counter({'0x' + l['topics'][2][-40:]: word(l['data'], 0) / 10 ** dec for l in mints}) if mints else None, mints, 2, dec),
            'burn_from': _top(None, burns, 1, dec),
        }
        rows[addr]['net_issued'] = rows[addr]['minted'] - rows[addr]['burned']
    hs['issuance'] = rows
    hs['issuance_rpc'] = rpc.stats()
    write_json(cdir / 'head_state.json', hs)
    return rows


def _top(_unused, logs, topic_i, dec, n=6):
    agg = collections.Counter()
    for l in logs:
        agg['0x' + l['topics'][topic_i][-40:]] += word(l['data'], 0)
    return [{'address': a, 'amount': v / 10 ** dec} for a, v in agg.most_common(n)]


def cmd_issuance(args):
    out = Path(args.out)
    chains = json.loads((out / 'manifest.json').read_text())['chains']
    if args.chains:
        want = {c.strip() for c in args.chains.split(',')}
        chains = [c for c in chains if c in want]
    with cf.ThreadPoolExecutor(max_workers=min(len(chains), args.workers)) as ex:
        futs = {ex.submit(issuance_chain, c, out): c for c in chains}
        for f in cf.as_completed(futs):
            c = futs[f]
            try:
                r = f.result()
                print(json.dumps({'chain': c, 'tokens': {v['symbol']: round(v['net_issued']) for v in r.values()}}))
            except Exception as exc:
                print(json.dumps({'chain': c, 'error': type(exc).__name__ + ': ' + str(exc)[:200]}))
    return 0


# ---------------------------------------------------------------------------------------------- analyze

DOLLARS = {'USDC', 'USDT', 'DAI', 'USDS', 'USDe', 'GHO', 'PYUSD', 'RLUSD', 'USDG', 'USDtb', 'FRAX', 'LUSD', 'crvUSD',
           'sUSDe', 'sUSDS', 'USD1', 'AUSD', 'FDUSD', 'EURC', 'USDC.e', 'USDT0', 'USDbC', 'USDT.e', 'DAI.e',
           'BUSD', 'USDD', 'lisUSD', 'FRAX', 'M', 'USDX', 'deUSD', 'USDL'}
NON_DOLLARS = {'EURC', 'EURe', 'EURS', 'agEUR'}   # priced in a currency that is not the dollar; excluded from the surface


def borrow_apr(curve, util):
    o = curve.get('optimal') or 0.9
    base, s1, s2 = curve.get('base', 0.0), curve.get('slope1', 0.05), curve.get('slope2', 0.5)
    if util <= o:
        return base + s1 * (util / o if o else 0)
    return base + s1 + s2 * (util - o) / max(1 - o, 1e-9)



def implied_utilisation(curve, borrow_rate):
    """The utilisation that reproduces the pool's own published borrow rate, by inverting its IRM.

    Why this exists, and why it replaces `variableDebt.totalSupply() / aToken.totalSupply()`.

    That ratio looks like the definition of utilisation and is not the number Aave prices with, and which way it is
    wrong is a function of the deployment's version. Measured on this window: Ethereum and Base reproduce their
    published borrow rate from the aToken total, while Avalanche reproduces it from `getVirtualUnderlyingBalance()`
    plus debt — the two differ by the unbacked aTokens the Portal has minted. Usually the gap is noise. On Avalanche's
    GHO reserve it was 5,592 GHO on a 1.09M reserve, 0.5%, and it straddled the kink: the aToken ratio says 89.91%
    utilisation and a 4.50% borrow rate, the pool says 90.38% and **6.00%**. A tenth of a percent of measurement error
    became 151 basis points of rate, because above the kink the curve is eighty times steeper than below it.

    Inverting the published rate is version-independent by construction: whatever denominator the deployment uses,
    the utilisation recovered here is the one its own curve was evaluated at. The aToken ratio is kept beside it, and
    the gap between the two is reported rather than reconciled — it is a real quantity (unbacked supply, or a virtual
    balance that has drifted from the token balance), not a rounding error to be hidden.
    """
    if not curve or borrow_rate is None:
        return None
    # A flat curve carries no information about utilisation, so it cannot be inverted. Aave's GHO strategy is exactly
    # this: base 3.00%, both slopes zero — a borrow rate set by governance rather than by the market. Inverting it
    # would return whichever point the bisection happened to land on and would then be used as if it were a
    # measurement. The caller falls back to the aToken ratio, which for a flat curve is the right denominator anyway
    # because nothing about the borrow rate depends on it.
    if abs(curve.get('slope1', 0)) < 1e-12 and abs(curve.get('slope2', 0)) < 1e-12:
        return None
    lo, hi = 0.0, 1.0
    if borrow_apr(curve, 1.0) < borrow_rate - 1e-12:
        return None                      # the curve cannot reach this rate: it is the wrong curve for this reserve
    for _ in range(200):
        mid = (lo + hi) / 2
        if borrow_apr(curve, mid) < borrow_rate:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def supply_apr(curve, borrowed, supplied):
    if supplied <= 0:
        return 0.0
    u = min(borrowed / supplied, 1.0)
    return borrow_apr(curve, u) * u * (1 - curve.get('reserve_factor', 0.1))


def width_to(curve, borrowed, supplied, target):
    """How much new supply the reserve absorbs before its supply rate falls to `target`."""
    if supply_apr(curve, borrowed, supplied) <= target:
        return 0.0
    lo, hi = 0.0, max(supplied, 1.0)
    for _ in range(80):
        if supply_apr(curve, borrowed, supplied + hi) > target:
            hi *= 2
            if hi > 1e13:
                return hi
        else:
            break
    for _ in range(120):
        mid = (lo + hi) / 2
        if supply_apr(curve, borrowed, supplied + mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def best_size(curve, borrowed, supplied, bench):
    """The position that maximises dollars earned over the benchmark. Unimodal in size, so ternary search."""
    w = width_to(curve, borrowed, supplied, bench)
    if w <= 0:
        return 0.0, supply_apr(curve, borrowed, supplied), 0.0
    lo, hi = 0.0, w
    f = lambda x: (supply_apr(curve, borrowed, supplied + x) - bench) * x
    for _ in range(200):
        a, b = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if f(a) < f(b):
            lo = a
        else:
            hi = b
    x = (lo + hi) / 2
    return x, supply_apr(curve, borrowed, supplied + x), f(x)


def ts_of(headers, n):
    """Block -> timestamp, piecewise-linear through the sampled headers. Block spacing is not assumed constant."""
    if not headers:
        return None
    if n <= headers[0]['n']:
        return headers[0]['ts']
    if n >= headers[-1]['n']:
        return headers[-1]['ts']
    lo, hi = 0, len(headers) - 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if headers[mid]['n'] <= n:
            lo = mid
        else:
            hi = mid
    a, b = headers[lo], headers[hi]
    if b['n'] == a['n']:
        return a['ts']
    return a['ts'] + (b['ts'] - a['ts']) * (n - a['n']) / (b['n'] - a['n'])


def rate_paths(meta, logs):
    """(pool, reserve) -> the intra-window supply/borrow rate path, time-weighted."""
    series = collections.defaultdict(list)
    for l in logs:
        if len(l['topics']) < 2:
            continue
        pool, reserve = l['address'].lower(), '0x' + l['topics'][1][-40:]
        d = l['data']
        if (len(d) - 2) // 64 < 5:
            continue
        series[(pool, reserve)].append((hx(l['blockNumber']), word(d, 0) / RAY, word(d, 2) / RAY))
    hdr, t0, t1 = meta['headers'], meta['first_ts'], meta['last_ts']
    out = {}
    for k, pts in series.items():
        pts.sort()
        stamped = [(ts_of(hdr, n), s, b) for n, s, b in pts]
        # A rate holds until the next update; before the first observation the pre-window value is unknown, so the
        # first observed rate is carried backwards and the fact is recorded rather than hidden.
        tw_s = tw_b = 0.0
        span = max(t1 - t0, 1)
        prev_t, prev_s, prev_b = t0, stamped[0][1], stamped[0][2]
        for t, s, b in stamped:
            dt_ = max(t - prev_t, 0)
            tw_s += prev_s * dt_
            tw_b += prev_b * dt_
            prev_t, prev_s, prev_b = t, s, b
        tw_s += prev_s * max(t1 - prev_t, 0)
        tw_b += prev_b * max(t1 - prev_t, 0)
        sup = sorted(s for _, s, _ in stamped)
        out[k] = {'updates': len(stamped), 'supply_twa': tw_s / span, 'borrow_twa': tw_b / span,
                  'supply_first': stamped[0][1], 'supply_last': stamped[-1][1],
                  'supply_min': sup[0], 'supply_max': sup[-1], 'supply_median': sup[len(sup) // 2],
                  'carried_back_from_first': True}
    return out


def cmd_analyze(args):
    out = Path(args.out)
    man = json.loads((out / 'manifest.json').read_text())
    bench, bench_name = args.benchmark, args.benchmark_name
    if args.benchmark_head and Path(args.benchmark_head).exists():
        bh = json.loads(Path(args.benchmark_head).read_text())
        if (bh.get('sky') or {}).get('ssr_apy'):
            bench, bench_name = bh['sky']['ssr_apy'], 'Sky savings rate (SSR), read on Ethereum at block %d' % bh['block']
    eth_usd = None
    if args.benchmark_head and Path(args.benchmark_head).exists():
        eth_usd = ((json.loads(Path(args.benchmark_head).read_text()).get('feeds') or {}).get('ETH') or {}).get('usd')

    A = {'generated': utc(time.time()), 'benchmark': {'apy': bench, 'name': bench_name},
         'eth_usd': eth_usd, 'chains': {}, 'domains': {}, 'errors': man.get('errors') or {},
         'window': window_bounds(man)}
    chains, metas, heads = man['chains'], {}, {}
    for c in chains:
        metas[c] = json.loads((out / c / 'chain.json').read_text())
        hp = out / c / 'head_state.json'
        heads[c] = json.loads(hp.read_text()) if hp.exists() else {}

    # verified chain <-> Circle domain map, from each chain's own transmitter
    for c in chains:
        d = ((heads[c].get('cctp') or {}).get('local_domain'))
        if d is not None:
            A['domains'][str(d)] = {'chain': c, 'source': 'localDomain() on this chain'}
    for d, name in DOMAIN_MEMORY.items():
        A['domains'].setdefault(str(d), {'chain': name, 'source': 'model memory (not verified in this window)'})

    surface, excluded = [], []   # every dollar reserve on every chain, and the ones that are not supply markets
    for c in chains:
        meta, hs = metas[c], heads[c]
        hdr = meta['headers']
        paths = rate_paths(meta, read_gz(out / c / 'logs_reserve_data.json.gz'))
        native_usd = hs.get('native_usd') or (eth_usd if CHAINS[c][2] == 'ETH' else None)

        # gas market, from the sampled headers scaled to the window
        gas = {}
        if hdr:
            n = len(hdr)
            used = sum(h['gas_used'] for h in hdr) / n
            lim = sum(h['gas_limit'] for h in hdr) / n
            bf = sum(h['base_fee'] for h in hdr) / n
            txs = sum(h['txs'] for h in hdr) / n
            burn_native = sum(h['gas_used'] * h['base_fee'] for h in hdr) / n * meta['blocks'] / 1e18
            gas = {'blocks': meta['blocks'], 'block_time_s': round(meta['seconds'] / max(meta['blocks'] - 1, 1), 3),
                   'mean_gas_used': round(used), 'mean_gas_limit': round(lim),
                   'fullness': round(used / lim, 4) if lim else None,
                   'mean_base_fee_gwei': round(bf / 1e9, 6), 'mean_txs_per_block': round(txs, 1),
                   'txs_in_window_est': round(txs * meta['blocks']),
                   'base_fee_native_est': round(burn_native, 4),
                   'base_fee_usd_est': round(burn_native * native_usd, 1) if native_usd else None,
                   'sampled_blocks': n, 'method': 'mean over %d evenly spaced headers, scaled by block count' % n}

        # CCTP flow
        burns = [decode_burn(l) for l in read_gz(out / c / 'logs_cctp_burn.json.gz')]
        mints = [decode_mint(l) for l in read_gz(out / c / 'logs_cctp_mint.json.gz')]
        tok = hs.get('bridge_tokens') or {}
        def dec_of(a):
            return (tok.get(a.lower()) or {}).get('decimals', 6)
        outbound = collections.defaultdict(lambda: {'amount': 0.0, 'legs': 0})
        for x in burns:
            if not x:
                continue
            k = str(x['dest_domain'])
            outbound[k]['amount'] += x['amount'] / 10 ** dec_of(x['token'])
            outbound[k]['legs'] += 1
        inbound = {'amount': sum(x['amount'] / 10 ** dec_of(x['token']) for x in mints if x), 'legs': len([x for x in mints if x])}
        depositors = collections.Counter()
        for x in burns:
            if x:
                depositors[x['depositor']] += x['amount'] / 10 ** dec_of(x['token'])
        recipients = collections.Counter()
        for x in mints:
            if x:
                recipients[x['recipient']] += x['amount'] / 10 ** dec_of(x['token'])
        cctp = {'out_by_domain': {k: dict(v) for k, v in sorted(outbound.items(), key=lambda kv: -kv[1]['amount'])},
                'out_total': sum(v['amount'] for v in outbound.values()), 'out_legs': sum(v['legs'] for v in outbound.values()),
                'in_total': inbound['amount'], 'in_legs': inbound['legs'],
                'net': inbound['amount'] - sum(v['amount'] for v in outbound.values()),
                'top_depositors': [{'address': a, 'amount': v} for a, v in depositors.most_common(6)],
                'top_recipients': [{'address': a, 'amount': v} for a, v in recipients.most_common(6)],
                'versions': collections.Counter(x['v'] for x in burns if x)}

        # lending surface
        pools = []
        for pool, p in (hs.get('pools') or {}).items():
            reserves = p.get('reserves') or {}
            prow = {'pool': pool, 'updates': p.get('updates'), 'reserves': len(reserves), 'error': p.get('error'),
                    'supplied_usd': 0.0}
            for a, r in reserves.items():
                sym = (r.get('sym') or '').strip()
                sup, bor = r.get('supplied'), r.get('borrowed')
                is_dollar = sym in DOLLARS and sym not in NON_DOLLARS
                px = 1.0 if is_dollar else (eth_usd if sym in ('WETH', 'ETH') else None)
                sup_usd = sup * px if (sup is not None and px) else None
                if sup_usd:
                    prow['supplied_usd'] += sup_usd
                if not is_dollar or not sup_usd:
                    continue
                path = paths.get((pool, a.lower())) or {}
                curve = r.get('curve')
                bor_usd_raw = (bor or 0) * px
                u_impl = implied_utilisation(curve, r.get('borrow_apr'))
                u_flat = u_impl is None and curve is not None and r.get('utilisation') is not None \
                    and abs(curve.get('slope1', 0)) < 1e-12 and abs(curve.get('slope2', 0)) < 1e-12
                if u_flat:
                    u_impl = r['utilisation']
                # Everything downstream sizes positions off the curve, so the liquidity base has to be the one the
                # curve was evaluated at, not the one the aToken reports.
                liq_eff = (bor_usd_raw / u_impl) if (u_impl and u_impl > 1e-9 and bor_usd_raw) else None
                # A reserve that pays its whole borrow rate to the treasury is not a supply market, and comparing its
                # 0.00% against another chain manufactures a spread out of an accounting fact. Aave's GHO reserve on
                # Ethereum is exactly this: reserve factor 1.0, $135.2M of "supplied" GHO that is the facilitator's own
                # minted balance rather than anybody's deposit. Left in, it produced the largest cross-chain switch on
                # the board ($12.8k/yr from a 5.40% Base rate against a 0.00% Ethereum one) and every dollar of it was
                # imaginary. The exclusion is recorded rather than silent.
                if (r.get('reserve_factor') or 0) >= 0.999:
                    excluded.append({'chain': c, 'pool': pool, 'asset': sym, 'supplied_usd': sup_usd,
                                     'reserve_factor': r.get('reserve_factor'),
                                     'why': 'reserve factor 1.0: the whole borrow rate goes to the treasury, so this '
                                            'is a mint facility, not a supply market'})
                    continue
                bor_usd = bor_usd_raw
                virt_usd = (r.get('virtual') * px) if (r.get('virtual') is not None and px) else None
                spot = r.get('supply_apr') or 0.0
                twa = path.get('supply_twa')
                # A head read that the window's own log path contradicts is a spike, not a rate: price the path.
                effective = twa if (twa is not None and path.get('updates', 0) >= args.min_updates) else spot
                # Effective supplied: what the pool prices on. Withdrawable: the smaller of what the curve implies is
                # free and what the pool says it physically holds — you cannot withdraw an unbacked aToken's worth.
                sup_eff = liq_eff if liq_eff else sup_usd
                avail = min(x for x in (sup_eff - bor_usd, virt_usd) if x is not None)
                row = {'chain': c, 'pool': pool, 'asset': sym, 'address': a,
                       'supplied_usd': sup_usd, 'supplied_effective_usd': sup_eff, 'borrowed_usd': bor_usd,
                       'virtual_usd': virt_usd,
                       'available_usd': max(avail, 0.0), 'utilisation': r.get('utilisation'),
                       'utilisation_implied': u_impl,
                       'utilisation_source': 'aToken ratio (flat IRM: the borrow rate is fixed, so the rate cannot be '
                                             'inverted for it)' if u_flat else 'inverted from the published borrow rate',
                       'utilisation_gap': (u_impl - r['utilisation']) if (u_impl is not None and r.get('utilisation') is not None) else None,
                       'supply_apr_spot': spot, 'supply_apr_twa': twa, 'supply_apr_used': effective,
                       'borrow_apr_spot': r.get('borrow_apr'), 'updates': path.get('updates', 0),
                       'rate_min': path.get('supply_min'), 'rate_max': path.get('supply_max'),
                       'reserve_factor': r.get('reserve_factor'), 'curve': curve,
                       'rate_source': 'window time-weighted' if effective is twa else 'head spot (unchecked: %d updates)' % path.get('updates', 0)}
                if curve and bench and liq_eff:
                    w = width_to(curve, bor_usd, sup_eff, bench)
                    x, apr, gain = best_size(curve, bor_usd, sup_eff, bench)
                    row.update({'width_to_benchmark_usd': w, 'best_size_usd': x, 'apr_at_best': apr,
                                'annual_gain_usd': gain,
                                'curve_reproduces_spot': abs(supply_apr(curve, bor_usd, sup_eff) - spot) < 0.0005})
                elif curve is None:
                    row['sizing'] = 'no rate curve read from the strategy contract; cannot be sized'
                elif not liq_eff:
                    row['sizing'] = 'the curve cannot reproduce the published borrow rate; treated as unverified'
                surface.append(row)
            pools.append(prow)

        A['chains'][c] = {'window': {'first_block': meta['first_block'], 'last_block': meta['last_block'],
                                     'blocks': meta['blocks'], 'first_utc': meta['first_utc'],
                                     'last_utc': meta['last_utc'], 'seconds': meta['seconds']},
                          'native': CHAINS[c][2], 'native_usd': native_usd, 'native_feed': hs.get('native_feed'),
                          'gas': gas, 'cctp': cctp, 'pools': pools,
                          'local_domain': (hs.get('cctp') or {}).get('local_domain'),
                          'bridge_tokens': tok, 'issuance': hs.get('issuance') or {},
                          'rate_paths': len(paths)}

    A['surface'] = sorted(surface, key=lambda r: -(r['supply_apr_used'] or 0))
    A['excluded_reserves'] = excluded
    # the same asset across chains
    by_asset = collections.defaultdict(list)
    for r in surface:
        by_asset[r['asset']].append(r)
    spreads = []
    for sym, rows in by_asset.items():
        big = {}
        for r in rows:                      # one row per chain: the deepest reserve of that asset there
            if r['chain'] not in big or r['supplied_usd'] > big[r['chain']]['supplied_usd']:
                big[r['chain']] = r
        if len(big) < 2:
            continue
        rs = sorted(big.values(), key=lambda r: -(r['supply_apr_used'] or 0))
        spreads.append({'asset': sym, 'chains': len(rs),
                        'high': {'chain': rs[0]['chain'], 'apr': rs[0]['supply_apr_used'], 'supplied_usd': rs[0]['supplied_usd'],
                                 'width_usd': rs[0].get('width_to_benchmark_usd'), 'best_size_usd': rs[0].get('best_size_usd'),
                                 'annual_gain_usd': rs[0].get('annual_gain_usd')},
                        'low': {'chain': rs[-1]['chain'], 'apr': rs[-1]['supply_apr_used'], 'supplied_usd': rs[-1]['supplied_usd']},
                        'spread': (rs[0]['supply_apr_used'] or 0) - (rs[-1]['supply_apr_used'] or 0),
                        'total_supplied_usd': sum(r['supplied_usd'] for r in rs),
                        'rows': [{'chain': r['chain'], 'apr': r['supply_apr_used'], 'supplied_usd': r['supplied_usd'],
                                  'utilisation': r['utilisation'], 'source': r['rate_source']} for r in rs]})
    A['spreads'] = sorted(spreads, key=lambda s: -s['spread'])


    # --- the cross-chain switch, priced the way a mover actually experiences it.
    #
    # The naive spread (high chain's rate minus low chain's rate, times any size you like) is wrong twice over, and
    # both corrections cut the same way.
    #
    # 1. The high side dilutes. A rate is a point on a kinked curve; supplying into it moves it down. The size that
    #    maximises dollars earned is where marginal APR still beats the rate being left behind, not the whole reserve.
    # 2. The low side may not let you leave. Utilisation is the share of supply that is lent out, and what a supplier
    #    can actually withdraw is `supplied - borrowed`. Optimism's USDC reserve pays 2.53% on $11.3M, of which $2.3M
    #    is withdrawable: the "move $18M to Base" that the curve says is optimal cannot be executed at a twentieth of
    #    that size, whatever the spread looks like.
    #
    # So capacity is min(high-side optimum, low-side withdrawable), and the binding one is recorded, because which
    # constraint binds is the finding. What is deliberately *not* charged here: bridge latency (CCTP standard waits
    # for source finality), the destination gas, and the fact that the two venues are different credit. Those make
    # the number smaller, never larger, so the figure below is an upper bound on a trade that is already small.
    best_of = {}
    for r in surface:
        k = (r['asset'], r['chain'])
        if k not in best_of or r['supplied_usd'] > best_of[k]['supplied_usd']:
            best_of[k] = r
    switches = []
    for sym in sorted({a for a, _ in best_of}):
        rs = sorted([v for (a, ch), v in best_of.items() if a == sym], key=lambda r: -(r['supply_apr_used'] or 0))
        if len(rs) < 2:
            continue
        hi = rs[0]
        if not hi.get('curve'):
            continue
        for lo in rs[1:]:
            target = lo['supply_apr_used'] or 0.0
            if not hi.get('supplied_effective_usd') or hi.get('curve_reproduces_spot') is not True:
                continue
            opt, _, _ = best_size(hi['curve'], hi['borrowed_usd'], hi['supplied_effective_usd'], target)
            movable = switch_capacity(opt, lo['available_usd'])
            if movable <= 0:
                continue
            apr = supply_apr(hi['curve'], hi['borrowed_usd'], hi['supplied_effective_usd'] + movable)
            gain = (apr - target) * movable
            if gain <= 0:
                continue
            switches.append({
                'asset': sym, 'to': hi['chain'], 'from': lo['chain'],
                'to_apr': hi['supply_apr_used'], 'from_apr': target,
                'spread_pp': 100 * ((hi['supply_apr_used'] or 0) - target),
                'unconstrained_size_usd': opt, 'from_available_usd': lo['available_usd'],
                'movable_usd': movable, 'apr_at_size': apr, 'annual_usd': gain,
                'binding': 'low-side withdrawable liquidity' if lo['available_usd'] < opt else 'high-side rate dilution',
                'from_supplied_usd': lo['supplied_usd'], 'from_utilisation': lo['utilisation_implied'],
                'to_supplied_usd': hi['supplied_usd'], 'to_pool': hi['pool'], 'from_pool': lo['pool'],
                'to_address': hi['address'], 'from_address': lo['address'],
                'rate_source': {'to': hi['rate_source'], 'from': lo['rate_source']}})
    A['switches'] = sorted(switches, key=lambda s: -s['annual_usd'])

    # Those lines are not additive: they compete for the same destination reserve, and filling it once uses up the
    # dilution room the next line assumed was free. The honest total fills each destination greedily from the
    # cheapest sources it can actually drain, and it is a good deal smaller than the sum of the rows.
    joint, used_dest, drained = [], {}, {}
    for sw in A['switches']:
        dk, sk = (sw['asset'], sw['to']), (sw['asset'], sw['from'])
        hi, lo = best_of[dk], best_of[sk]
        already = used_dest.get(dk, 0.0)
        opt, _, _ = best_size(hi['curve'], hi['borrowed_usd'], hi['supplied_effective_usd'] + already, sw['from_apr'])
        left = max(lo['available_usd'] - drained.get(sk, 0.0), 0.0)
        x = max(min(opt, left), 0.0)
        if x <= 0:
            continue
        apr = supply_apr(hi['curve'], hi['borrowed_usd'], hi['supplied_effective_usd'] + already + x)
        g = (apr - sw['from_apr']) * x
        if g <= 0:
            continue
        used_dest[dk] = already + x
        drained[sk] = drained.get(sk, 0.0) + x
        joint.append({'asset': sw['asset'], 'to': sw['to'], 'from': sw['from'], 'size_usd': x,
                      'apr_at_size': apr, 'from_apr': sw['from_apr'], 'annual_usd': g})
    A['switch_book'] = {'legs': joint, 'total_annual_usd': sum(l['annual_usd'] for l in joint),
                        'total_size_usd': sum(l['size_usd'] for l in joint),
                        'sum_of_rows_annual_usd': sum(s['annual_usd'] for s in A['switches']),
                        'note': 'each destination reserve is filled once, cheapest source first; the sum of the '
                                'individual rows double-counts that room'}

    # does the bridge move dollars toward the yield?
    flow = []
    for c in chains:
        ch = A['chains'][c]
        usdc_rows = [r for r in surface if r['chain'] == c and r['asset'] in ('USDC', 'USDC.e')]
        best = max(usdc_rows, key=lambda r: r['supplied_usd']) if usdc_rows else None
        flow.append({'chain': c, 'net_cctp_usdc': ch['cctp']['net'], 'in': ch['cctp']['in_total'],
                     'out': ch['cctp']['out_total'],
                     'usdc_supply_apr': best['supply_apr_used'] if best else None,
                     'usdc_supplied_usd': best['supplied_usd'] if best else None,
                     'usdc_utilisation': best['utilisation'] if best else None,
                     'net_issued': sum(v.get('net_issued', 0) for v in (ch.get('issuance') or {}).values())})
    A['flow_vs_yield'] = sorted(flow, key=lambda f: -(f['net_cctp_usdc'] or 0))
    # One hour and ten chains is not a law, but the sign is worth stating precisely rather than by eye.
    pairs = [(f['usdc_supply_apr'], f['net_cctp_usdc']) for f in flow if f['usdc_supply_apr']]
    if len(pairs) >= 4:
        def ranks(vals):
            order = sorted(range(len(vals)), key=lambda i: vals[i])
            rk = [0.0] * len(vals)
            i = 0
            while i < len(order):
                j = i
                while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                    j += 1
                avg = (i + j) / 2 + 1
                for k in range(i, j + 1):
                    rk[order[k]] = avg
                i = j + 1
            return rk
        ra, rb = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
        n = len(pairs)
        ma, mb = sum(ra) / n, sum(rb) / n
        num = sum((a - ma) * (b - mb) for a, b in zip(ra, rb))
        den = (sum((a - ma) ** 2 for a in ra) * sum((b - mb) ** 2 for b in rb)) ** .5
        A['flow_vs_yield_spearman'] = {'rho': (num / den) if den else None, 'n': n,
                                       'note': 'rank correlation between a chain\'s USDC supply APR and its net CCTP '
                                               'USDC flow over this one hour; a negative value means dollars moved '
                                               'toward the lower rate'}
    write_json(out / 'analysis.json', A)
    print(json.dumps({'chains': len(chains), 'dollar_reserves': len(surface), 'assets_multi_chain': len(A['spreads']),
                      'benchmark': bench, 'cctp_legs': sum(A['chains'][c]['cctp']['out_legs'] + A['chains'][c]['cctp']['in_legs'] for c in chains)}, indent=1))
    return 0


# ---------------------------------------------------------------------------------------------- detect

DETECTOR = 'cross_chain_rate'
GO_MIN_CAPACITY_USD = 250_000.0
GO_MIN_NET_APR = 0.005


def switch_capacity(opt_usd, available_usd):
    """The study's definition of a switch's size: min(high-side optimum before it dilutes, low-side withdrawable)."""
    return max(min(opt_usd or 0.0, available_usd or 0.0), 0.0)


def go_rule(capacity_usd, net_apr):
    """A switch is worth a row in the book at $250k of capacity and 50bp net; below either it is a curiosity."""
    return bool((capacity_usd or 0.0) >= GO_MIN_CAPACITY_USD and (net_apr or 0.0) >= GO_MIN_NET_APR)


def window_bounds(man):
    """One window for the ledger from the per-chain windows: earliest first, latest last. Blocks are per chain."""
    ws = man.get('window') or {}
    firsts = [w['first_utc'] for w in ws.values() if w.get('first_utc')]
    lasts = [w['last_utc'] for w in ws.values() if w.get('last_utc')]
    return {'first_utc': min(firsts) if firsts else None, 'last_utc': max(lasts) if lasts else None,
            'hours': man.get('hours'), 'chains': sorted(ws), 'first_block': None, 'last_block': None,
            'note': 'per-chain block ranges are in manifest.json; block numbers are not comparable across chains'}


def detect_hits(A, bridge_bps=0.0):
    """Every priced switch as a ledger finding, plus the book filled once as a window-level one.

    `net_apr` is the APR the moved dollars earn at the moved size minus the rate they leave, less a bridge round trip.
    The study charged that round trip at zero (a standard CCTP transfer has no fee) and said what it did not charge:
    source-finality latency, destination gas, and the two venues being different credit. `bridge_bps` lets a reader
    charge it anyway; the default reproduces the study.
    """
    hits = []
    for sw in A.get('switches') or []:
        cap = switch_capacity(sw.get('unconstrained_size_usd'), sw.get('from_available_usd'))
        net = (sw.get('apr_at_size') or 0.0) - (sw.get('from_apr') or 0.0) - bridge_bps / 1e4
        go = go_rule(cap, net)
        key = '%s:%s->%s' % (sw['asset'], sw['from'], sw['to'])
        hits.append({
            'detector': DETECTOR, 'key': key, 'identity': DETECTOR + ':' + key,
            'severity': 'notable' if go else 'info',
            'title': '%s pays %.2fpp more on %s than %s; %s of it can move (%s), earning %.2f%% at size for $%s a year'
                     % (sw['asset'], sw.get('spread_pp') or 0.0, sw['to'], sw['from'], _m(cap),
                        'bound by ' + sw['binding'], 100 * (sw.get('apr_at_size') or 0.0), format(round(sw.get('annual_usd') or 0), ',')),
            'evidence': {'asset': sw['asset'], 'from': sw['from'], 'to': sw['to'],
                         'from_pool': sw.get('from_pool'), 'to_pool': sw.get('to_pool'),
                         'from_address': sw.get('from_address'), 'to_address': sw.get('to_address'),
                         'from_apr': sw.get('from_apr'), 'to_apr': sw.get('to_apr'), 'apr_at_size': sw.get('apr_at_size'),
                         'spread_pp': sw.get('spread_pp'), 'unconstrained_size_usd': sw.get('unconstrained_size_usd'),
                         'from_available_usd': sw.get('from_available_usd'), 'movable_usd': sw.get('movable_usd'),
                         'binding': sw.get('binding'), 'from_supplied_usd': sw.get('from_supplied_usd'),
                         'to_supplied_usd': sw.get('to_supplied_usd'), 'from_utilisation': sw.get('from_utilisation'),
                         'rate_source': sw.get('rate_source'),
                         'capacity_matches_row': abs(cap - (sw.get('movable_usd') or 0.0)) < 1e-6,
                         'why': 'the same dollar on two chains is one claim on one issuer; the spread is what the '
                                'lending markets fail to equalise, and it is only worth what can be moved'},
            'economics': {'net_apr': net, 'go': go, 'capacity_usd': cap, 'net_per_year_usd': sw.get('annual_usd'),
                          'bridge_round_trip_bps': bridge_bps, 'binding': sw.get('binding'),
                          'reason': ('clears $250k and 50bp net at the movable size' if go else
                                     'under $250k movable or under 50bp net at that size')},
            'usd': sw.get('annual_usd')})
    sb = A.get('switch_book') or {}
    size = sb.get('total_size_usd') or 0.0
    ann = sb.get('total_annual_usd') or 0.0
    blended = (ann / size) if size else None
    bind = collections.Counter(sw.get('binding') for sw in (A.get('switches') or []))
    go = go_rule(size, blended)
    hits.append({
        'detector': DETECTOR, 'key': 'book', 'identity': DETECTOR + ':book',
        'severity': 'notable' if go else 'info',
        'title': 'the cross-chain dollar book absorbs %s at %.0fbp, each destination filled once, cheapest source first '
                 '(%d legs; the rows summed would claim $%s a year)'
                 % (_m(size), 1e4 * (blended or 0.0), len(sb.get('legs') or []), format(round(sb.get('sum_of_rows_annual_usd') or 0), ',')),
        'evidence': {'legs': sb.get('legs'), 'total_size_usd': size, 'total_annual_usd': ann,
                     'sum_of_rows_annual_usd': sb.get('sum_of_rows_annual_usd'),
                     'switches_priced': len(A.get('switches') or []), 'bindings': dict(bind),
                     'dollar_reserves': len(A.get('surface') or []), 'chains': sorted((A.get('chains') or {}).keys()),
                     'benchmark': A.get('benchmark'), 'flow_vs_yield_spearman': A.get('flow_vs_yield_spearman'),
                     'why': 'the rows compete for the same destination reserve; filled once, the book is what the whole '
                            'surface is worth, and the CCTP rank correlation says whether the bridge is closing it'},
        'economics': {'net_apr': blended, 'go': go, 'capacity_usd': size, 'net_per_year_usd': ann,
                      'bridge_round_trip_bps': bridge_bps,
                      'reason': ('the book clears $250k and 50bp blended' if go else 'the book is under $250k or under 50bp blended')},
        'usd': ann})
    return hits


def cmd_detect(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    if not A.get('window'):
        # an analysis written before the window key existed: derive it from the manifest so the ledger can date it
        A['window'] = window_bounds(json.loads((out / 'manifest.json').read_text()))
        write_json(out / 'analysis.json', A)
        print(json.dumps({'note': 'analysis.json had no window; added from manifest', 'window': A['window']}))
    t0 = time.time()
    hits = detect_hits(A, bridge_bps=args.bridge_bps)
    order = {'high': 0, 'notable': 1, 'info': 2}
    hits.sort(key=lambda h: (order.get(h['severity'], 3), -(h.get('usd') or 0)))
    meta = [{'detector': DETECTOR, 'hits': len(hits), 'seconds': round(time.time() - t0, 3), 'error': None,
             'description': 'every priced cross-chain dollar switch, sized by min(high-side optimum, low-side withdrawable), '
                            'plus the book filled once'}]
    write_json(out / 'detectors.json', {'window': str(out), 'analysis_window': A['window'], 'detectors': meta, 'hits': hits,
                                        'params': {'bridge_round_trip_bps': args.bridge_bps,
                                                   'go_min_capacity_usd': GO_MIN_CAPACITY_USD, 'go_min_net_apr': GO_MIN_NET_APR}})
    L = ['# Detector sweep — %s' % out, '', 'Ran 1 detector; %d hit(s).' % len(hits), '',
         '| detector | hits | seconds | what it looks for |', '|---|---:|---:|---|']
    for m in meta:
        L.append('| `%s` | %d | %.3f | %s |' % (m['detector'], m['hits'], m['seconds'], m['description']))
    L.append('')
    for h in hits:
        L += ['### [%s] %s' % (h['severity'], h['title']), '', '```json',
              json.dumps({k: v for k, v in h['evidence'].items() if k != 'legs'}, indent=1, default=str)[:2400], '```']
        e = h['economics']
        L += ['', 'Economics: net APR %.2f%%, capacity %s, %s — %s' % (100 * (e['net_apr'] or 0), _m(e['capacity_usd']),
                                                                   'GO' if e['go'] else 'no', e['reason']), '']
    (out / 'detectors.md').write_text('\n'.join(L) + '\n')
    for h in hits:
        print('[%-7s] %s' % (h['severity'], h['title']))
    print('wrote %s (%d hits)' % (out / 'detectors.json', len(hits)))
    return 0


# ---------------------------------------------------------------------------------------------- verify

def cmd_verify(args):
    """Re-derive the headline numbers by a path that does not go through `analyze`, and assert the identities.

    The point is not to re-run the same arithmetic. Each check either recomputes a figure straight from the saved
    logs, or tests a relationship that must hold on-chain whatever this repo believes.
    """
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    man = json.loads((out / 'manifest.json').read_text())
    checks, ident = [], []

    def chk(cid, what, recomputed, claimed, tol=0.0, note=''):
        if recomputed is None or claimed is None:
            ok = False
        elif tol == 0:
            ok = recomputed == claimed
        else:
            ok = abs(recomputed - claimed) <= tol * max(abs(claimed), 1e-9)
        checks.append({'id': cid, 'check': what, 'recomputed': recomputed, 'analysis': claimed, 'ok': ok,
                       'tolerance': tol, 'note': note})

    # 1. CCTP conservation across the whole scan: what one chain burned for domain D, the chain that *is* domain D
    #    should have minted. It will not balance exactly — the attestation takes minutes, so sends near the end of the
    #    window land after it, and sends from chains outside the scan land inside it — but the residual is itself the
    #    measurement: dollars in flight.
    dom_chain = {int(d): v['chain'] for d, v in A['domains'].items() if v['chain'] in A['chains']}
    burned_to, minted_on = collections.Counter(), {}
    for c, ch in A['chains'].items():
        for d, v in ch['cctp']['out_by_domain'].items():
            burned_to[int(d)] += v['amount']
        minted_on[c] = ch['cctp']['in_total']
    conservation = []
    for d, c in sorted(dom_chain.items()):
        conservation.append({'domain': d, 'chain': c, 'burned_for_it_in_window': burned_to.get(d, 0.0),
                             'minted_on_it_in_window': minted_on.get(c, 0.0),
                             'residual': minted_on.get(c, 0.0) - burned_to.get(d, 0.0)})
    inside = sum(burned_to.get(d, 0.0) for d in dom_chain)
    outside = sum(v for d, v in burned_to.items() if d not in dom_chain)
    # Coverage, not correctness: dollars leave for domains this scan has no chain for. Naming how many is honest;
    # asserting there are none would just be wrong.
    unknown_domains = sorted(d for d in burned_to if str(d) not in A['domains'])
    chk('cctp-scanned-domains-verified', 'every scanned chain that used CCTP resolved its own domain on-chain',
        len([c for c, ch in A['chains'].items() if ch['local_domain'] is not None]),
        len([c for c, ch in A['chains'].items() if ch['cctp']['out_legs'] or ch['cctp']['in_legs']]))

    # 2. Every CCTP burn is also a USDC burn, so the bridge leg can never exceed the token's own burn total. This
    #    catches a decimals error or a double count, and it uses a completely separate log set (Transfer to zero).
    for c, ch in A['chains'].items():
        iss = list((ch.get('issuance') or {}).values())
        if not iss:
            continue
        tot_burn = sum(i['burned'] for i in iss)
        tot_mint = sum(i['minted'] for i in iss)
        chk('cctp-le-burn-%s' % c, '%s: CCTP out <= USDC burned' % c,
            1 if ch['cctp']['out_total'] <= tot_burn * 1.0001 + 1 else 0, 1)
        chk('cctp-le-mint-%s' % c, '%s: CCTP in <= USDC minted' % c,
            1 if ch['cctp']['in_total'] <= tot_mint * 1.0001 + 1 else 0, 1)

    # 3. The three on-chain identities, on every reserve in the surface, on every chain.
    for cid, what, fn in (
            ('utilisation', 'utilisation equals borrowed / supplied',
             lambda r: (abs(r['utilisation'] - r['borrowed_usd'] / r['supplied_usd'])
                        if r['supplied_usd'] and r.get('utilisation') is not None else None)),
            # The identity holds at the utilisation the pool prices with, not at the aToken ratio. Running it on the
            # aToken ratio is what surfaced the whole liquidity-base problem; the divergence itself is reported under
            # `liquidity_base_gap` rather than being asserted away.
            ('supply-identity', 'supply APR equals borrow APR x priced utilisation x (1 - reserve factor)',
             lambda r: (abs(r['supply_apr_spot'] - r['borrow_apr_spot'] * r['utilisation_implied'] * (1 - r['reserve_factor']))
                        if None not in (r.get('borrow_apr_spot'), r.get('utilisation_implied'), r.get('reserve_factor')) else None)),
            # The IRM check is now on the inverted utilisation, which is the number every size in this file is
            # computed from. If the curve cannot reproduce the pool's own published rate at any utilisation, the
            # curve is not this reserve's curve and nothing may be sized from it.
            ('irm-invertible', 'the reserve IRM reproduces the pool\'s published borrow rate at the inverted utilisation',
             lambda r: (abs(r['borrow_apr_spot'] - borrow_apr(r['curve'], r['utilisation_implied']))
                        if r.get('curve') and r.get('utilisation_implied') is not None and r.get('borrow_apr_spot') is not None else None)),
            ('supply-on-effective-liquidity', 'supply APR replays from the curve at the effective liquidity base',
             lambda r: (abs(r['supply_apr_spot'] - supply_apr(r['curve'], r['borrowed_usd'], r['supplied_effective_usd']))
                        if r.get('curve') and r.get('supplied_effective_usd') else None))):
        worst, n, bad = 0.0, 0, []
        for r in A['surface']:
            d = fn(r)
            if d is None:
                continue
            n += 1
            worst = max(worst, d)
            if d > args.tol:
                bad.append({'chain': r['chain'], 'pool': r['pool'], 'asset': r['asset'], 'delta': d,
                            'utilisation': r.get('utilisation'), 'curve': r.get('curve')})
        ident.append({'id': cid, 'check': what, 'checked': n, 'failed': len(bad), 'ok': not bad,
                      'worst': worst, 'examples': bad[:6]})

    # 4. The rate path must bracket the head read, or one of the two is not describing the same reserve.
    bad = []
    for r in A['surface']:
        if r.get('updates', 0) >= args.min_updates and r.get('rate_min') is not None:
            lo, hi = r['rate_min'], r['rate_max']
            if not (lo - 1e-9 <= (r['supply_apr_twa'] or 0) <= hi + 1e-9):
                bad.append({'chain': r['chain'], 'asset': r['asset'], 'twa': r['supply_apr_twa'], 'min': lo, 'max': hi})
    ident.append({'id': 'twa-in-range', 'check': 'the time-weighted rate lies between the window min and max',
                  'checked': len([r for r in A['surface'] if r.get('updates', 0) >= args.min_updates]),
                  'failed': len(bad), 'ok': not bad, 'worst': 0, 'examples': bad[:6]})

    # 5. Every switch must be executable: its size cannot exceed what the source reserve lets out, and the rate it
    #    claims at that size must be the curve's answer, recomputed here rather than copied.
    bad = []
    for sw in A['switches']:
        src = [r for r in A['surface'] if r['chain'] == sw['from'] and r['asset'] == sw['asset'] and r['pool'] == sw['from_pool']]
        dst = [r for r in A['surface'] if r['chain'] == sw['to'] and r['asset'] == sw['asset'] and r['pool'] == sw['to_pool']]
        if not src or not dst:
            bad.append({'switch': sw['asset'] + ' ' + sw['from'] + '->' + sw['to'], 'why': 'reserve not found'})
            continue
        src = [r for r in src if r['address'] == sw['from_address']] or src
        dst = [r for r in dst if r['address'] == sw['to_address']] or dst
        s0, d0 = src[0], dst[0]
        if sw['movable_usd'] > s0['available_usd'] + 1:
            bad.append({'switch': sw['asset'] + ' ' + sw['from'] + '->' + sw['to'], 'why': 'size exceeds withdrawable',
                        'size': sw['movable_usd'], 'available': s0['available_usd']})
        re_apr = supply_apr(d0['curve'], d0['borrowed_usd'], d0['supplied_effective_usd'] + sw['movable_usd'])
        if abs(re_apr - sw['apr_at_size']) > 1e-6:
            bad.append({'switch': sw['asset'] + ' ' + sw['from'] + '->' + sw['to'], 'why': 'apr at size not reproducible',
                        'claimed': sw['apr_at_size'], 'recomputed': re_apr})
    ident.append({'id': 'switch-executable', 'check': 'every switch fits the source liquidity and its APR replays on the curve',
                  'checked': len(A['switches']), 'failed': len(bad), 'ok': not bad, 'worst': 0, 'examples': bad[:6]})

    # 6. Gas: the sampled estimate is a scaling, so state its sampling error rather than the point value alone.
    gas_note = []
    for c, ch in A['chains'].items():
        g = ch.get('gas') or {}
        if g.get('sampled_blocks'):
            gas_note.append({'chain': c, 'sampled_blocks': g['sampled_blocks'], 'blocks': g['blocks'],
                             'sample_share': round(g['sampled_blocks'] / g['blocks'], 5)})

    V = {'window': str(out), 'generated': utc(time.time()), 'checks': checks, 'identities': ident,
         'cctp_conservation': conservation,
         'cctp_in_flight': {'burned_for_scanned_chains': inside, 'burned_for_unscanned_chains': outside,
                            'minted_on_scanned_chains': sum(minted_on.values()),
                            'note': 'a residual is expected and is the float: attestation takes minutes, so legs '
                                    'near the window edges settle outside it, and chains outside the scan send into it'},
         'gas_sampling': gas_note,
         'cctp_unknown_destination_domains': [
             {'domain': d, 'usd': burned_to[d],
              'note': 'a Circle domain no chain in this scan resolved on-chain; dollars left for it and this scan '
                      'cannot see them arrive'} for d in unknown_domains],
         'liquidity_base_gap': sorted(
             [{'chain': r['chain'], 'asset': r['asset'], 'pool': r['pool'],
               'utilisation_atoken': r['utilisation'], 'utilisation_priced': r['utilisation_implied'],
               'gap_pp': 100 * r['utilisation_gap'], 'supplied_usd': r['supplied_usd'],
               'rate_error_if_atoken_used_pp': 100 * abs(borrow_apr(r['curve'], r['utilisation']) - r['borrow_apr_spot'])}
              for r in A['surface']
              if r.get('utilisation_gap') is not None and r.get('curve') and abs(r['utilisation_gap']) > 1e-6],
             key=lambda x: -x['rate_error_if_atoken_used_pp'])[:12],
         'chains_failed_to_collect': man.get('errors') or {},
         'all_ok': all(c['ok'] for c in checks) and all(i['ok'] for i in ident)}
    V['failures'] = [c for c in checks if not c['ok']] + [i for i in ident if not i['ok']]
    write_json(out / 'verify.json', V)
    print(json.dumps({'checks': len(checks), 'identities': len(ident), 'all_ok': V['all_ok'],
                      'failures': len(V['failures'])}, indent=1))
    return 0 if V['all_ok'] else 1


# ---------------------------------------------------------------------------------------------- render

def _m(v):
    if v is None:
        return '-'
    a = abs(v)
    if a >= 1e9:
        return '$%.2fB' % (v / 1e9)
    if a >= 1e6:
        return '$%.1fM' % (v / 1e6)
    if a >= 1e3:
        return '$%.0fk' % (v / 1e3)
    return '$%.0f' % v


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    V = json.loads((out / 'verify.json').read_text()) if (out / 'verify.json').exists() else None
    L = []
    w = A['chains'][sorted(A['chains'])[0]]['window']
    L.append('## Deterministic tables — %d chains, %s to %s UTC\n' % (len(A['chains']), w['first_utc'][11:16], w['last_utc'][11:16]))
    L.append('Benchmark: **%s = %.2f%%**. Every rate below is a supply APR; "priced utilisation" is inverted from the '
             'pool\'s own published borrow rate rather than taken from the aToken ratio (see `multichain.py`, '
             '`implied_utilisation`).\n' % (A['benchmark']['name'], 100 * A['benchmark']['apy']))

    L.append('\n### The same dollar, across chains\n')
    L.append('| asset | chains | high | low | spread | supplied |')
    L.append('|---|---:|---|---|---:|---:|')
    for sp in A['spreads']:
        L.append('| %s | %d | %s %.2f%% | %s %.2f%% | %.2fpp | %s |' % (
            sp['asset'], sp['chains'], sp['high']['chain'], 100 * (sp['high']['apr'] or 0),
            sp['low']['chain'], 100 * (sp['low']['apr'] or 0), 100 * sp['spread'], _m(sp['total_supplied_usd'])))

    L.append('\n### USDC reserve by reserve\n')
    L.append('| chain | supply APR | priced util | supplied | withdrawable | rate source |')
    L.append('|---|---:|---:|---:|---:|---|')
    # One row per chain, and it has to be the *deepest* reserve there, not the highest-paying one: a $39k fork
    # reserve paying 3.31% is not what "USDC on Optimism" means to anyone deciding where to put dollars.
    deepest = {}
    for r in A['surface']:
        if r['asset'] != 'USDC':
            continue
        if r['chain'] not in deepest or r['supplied_usd'] > deepest[r['chain']]['supplied_usd']:
            deepest[r['chain']] = r
    for r in sorted(deepest.values(), key=lambda r: -(r['supply_apr_used'] or 0)):
        L.append('| %s | %.2f%% | %.4f | %s | %s | %s |' % (
            r['chain'], 100 * (r['supply_apr_used'] or 0), r['utilisation_implied'] or 0,
            _m(r['supplied_usd']), _m(r['available_usd']), r['rate_source']))

    b = A['switch_book']
    L.append('\n### Every cross-chain dollar switch that pays, filled once\n')
    L.append('Size is `min(the high side\'s optimum before it dilutes, the low side\'s withdrawable liquidity)`. '
             'Destinations are filled cheapest-source-first, because the rows compete for the same reserve.\n')
    L.append('| asset | earn on | move from | size | APR at size | leaving | $/year |')
    L.append('|---|---|---|---:|---:|---:|---:|')
    for l in b['legs']:
        L.append('| %s | %s | %s | %s | %.2f%% | %.2f%% | %s |' % (
            l['asset'], l['to'], l['from'], _m(l['size_usd']), 100 * l['apr_at_size'], 100 * l['from_apr'], _m(l['annual_usd'])))
    L.append('| **total** | | | **%s** | | | **%s** |' % (_m(b['total_size_usd']), _m(b['total_annual_usd'])))
    L.append('\nSum of the rows taken independently would say %s — %.0f%% higher, because each row assumes the '
             'destination reserve is empty.\n' % (_m(b['sum_of_rows_annual_usd']),
                                                   100 * (b['sum_of_rows_annual_usd'] / max(b['total_annual_usd'], 1) - 1)))

    L.append('\n### CCTP: where the dollars actually went, against where the yield is\n')
    L.append('| chain | net CCTP USDC | in | out | USDC APR | net USDC issued |')
    L.append('|---|---:|---:|---:|---:|---:|')
    for f in A['flow_vs_yield']:
        L.append('| %s | %s | %s | %s | %s | %s |' % (
            f['chain'], _m(f['net_cctp_usdc']), _m(f['in']), _m(f['out']),
            ('%.2f%%' % (100 * f['usdc_supply_apr'])) if f['usdc_supply_apr'] else '-', _m(f['net_issued'])))
    sp = A.get('flow_vs_yield_spearman')
    if sp and sp.get('rho') is not None:
        L.append('\nRank correlation between a chain\'s USDC supply rate and its net CCTP flow this hour: '
                 '**%.2f** (n=%d). Negative means the dollars moved toward the lower rate.\n' % (sp['rho'], sp['n']))

    L.append('\n### The gas market, ten chains, one hour\n')
    L.append('| chain | blocks | block time | txs/hour | fullness | base fee (gwei) | native $ | base fee $/hour |')
    L.append('|---|---:|---:|---:|---:|---:|---:|---:|')
    tot = 0
    for c, ch in sorted(A['chains'].items(), key=lambda kv: -(kv[1]['gas'].get('base_fee_usd_est') or 0)):
        g = ch['gas']
        tot += g.get('base_fee_usd_est') or 0
        L.append('| %s | %d | %.2fs | %s | %s | %.6f | %s | %s |' % (
            c, g['blocks'], g['block_time_s'], '{:,}'.format(g['txs_in_window_est']),
            ('%.1f%%' % (100 * g['fullness'])) if (g['fullness'] is not None and g['fullness'] < 1) else 'n/a',
            g['mean_base_fee_gwei'], ('%.2f' % ch['native_usd']) if ch['native_usd'] else '-',
            ('$%.0f' % g['base_fee_usd_est']) if g['base_fee_usd_est'] is not None else '-'))
    L.append('| **total** | | | | | | | **$%.0f** |' % tot)
    L.append('\nFullness is `gas used / gas limit` over evenly sampled headers; Arbitrum posts a sentinel gas limit '
             'so its share is not meaningful and is shown as n/a.\n')

    if A.get('excluded_reserves'):
        L.append('\n### Reserves excluded from the surface\n')
        L.append('| chain | asset | supplied | why |')
        L.append('|---|---|---:|---|')
        for e in A['excluded_reserves']:
            L.append('| %s | %s | %s | %s |' % (e['chain'], e['asset'], _m(e['supplied_usd']), e['why']))

    if V:
        L.append('\n### Verification\n')
        L.append('`multichain.py verify` — %d numeric checks, %d identities, all_ok = **%s**.\n'
                 % (len(V['checks']), len(V['identities']), V['all_ok']))
        L.append('| identity | checked | failed | worst deviation |')
        L.append('|---|---:|---:|---:|')
        for i in V['identities']:
            L.append('| %s | %d | %d | %.2e |' % (i['check'], i['checked'], i['failed'], i['worst']))
        if V.get('liquidity_base_gap'):
            L.append('\n**The liquidity base the pool actually prices at, versus the aToken ratio.** Reading '
                     '`variableDebt.totalSupply() / aToken.totalSupply()` is close to right and occasionally very '
                     'wrong; near a kink the error is multiplied by the slope.\n')
            L.append('| chain | asset | u (aToken) | u (priced) | gap | borrow-rate error if the aToken ratio is used |')
            L.append('|---|---|---:|---:|---:|---:|')
            for g in V['liquidity_base_gap'][:8]:
                L.append('| %s | %s | %.6f | %.6f | %+.4fpp | %.3fpp |' % (
                    g['chain'], g['asset'], g['utilisation_atoken'], g['utilisation_priced'], g['gap_pp'],
                    g['rate_error_if_atoken_used_pp']))
        if V.get('cctp_unknown_destination_domains'):
            L.append('\n**Dollars leaving for domains outside this scan.** %s burned for Circle domains no scanned '
                     'chain resolved, against %s for chains inside it.\n'
                     % (_m(V['cctp_in_flight']['burned_for_unscanned_chains']),
                        _m(V['cctp_in_flight']['burned_for_scanned_chains'])))
            L.append('| domain | USDC burned for it |')
            L.append('|---:|---:|')
            for d in V['cctp_unknown_destination_domains']:
                L.append('| %d | %s |' % (d['domain'], _m(d['usd'])))

    tables = '\n'.join(L) + '\n'
    (out / 'tables.md').write_text(tables)
    ins = out / 'insights.md'
    head = ins.read_text() if ins.exists() else '_(no insights.md written yet)_\n'
    (out / 'report.md').write_text(head.rstrip() + '\n\n---\n\n' + tables)
    print(json.dumps({'tables.md': len(tables), 'report.md': str(out / 'report.md')}))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True); c.add_argument('--hours', type=float, default=1.0)
    c.add_argument('--chains', default=DEFAULT_CHAINS); c.add_argument('--workers', type=int, default=10)
    c.add_argument('--samples', type=int, default=60)
    h = sub.add_parser('head'); h.set_defaults(fn=cmd_head)
    h.add_argument('--out', required=True); h.add_argument('--chains', default=None)
    h.add_argument('--workers', type=int, default=10); h.add_argument('--max-pools', type=int, default=8)
    i = sub.add_parser('issuance'); i.set_defaults(fn=cmd_issuance)
    i.add_argument('--out', required=True); i.add_argument('--chains', default=None); i.add_argument('--workers', type=int, default=10)
    z = sub.add_parser('analyze'); z.set_defaults(fn=cmd_analyze)
    z.add_argument('--out', required=True)
    z.add_argument('--benchmark', type=float, default=0.036)
    z.add_argument('--benchmark-name', default='Sky savings rate (assumed)')
    z.add_argument('--benchmark-head', default=None, help='an Ethereum head_state.json to read the SSR and ETH price from')
    z.add_argument('--min-updates', type=int, default=8)
    v = sub.add_parser('verify'); v.set_defaults(fn=cmd_verify)
    v.add_argument('--out', required=True); v.add_argument('--tol', type=float, default=0.002)
    v.add_argument('--min-updates', type=int, default=8)
    d = sub.add_parser('render'); d.set_defaults(fn=cmd_render); d.add_argument('--out', required=True)
    t = sub.add_parser('detect'); t.set_defaults(fn=cmd_detect); t.add_argument('--out', required=True)
    t.add_argument('--bridge-bps', type=float, default=0.0, help='charge a bridge round trip; the study charged zero')
    a = ap.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == '__main__':
    main()
