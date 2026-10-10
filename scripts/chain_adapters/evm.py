#!/usr/bin/env python3
"""EVM chains (and Tron, whose JSON-RPC speaks the same block and log dialect): transactions and ERC-20 transfer value
over a window, from a stratified sample of blocks.

Per sampled block, one `eth_getBlockByNumber(full)` gives the transaction count, the native value moved at the top level
and the gas used, and one `eth_getLogs` on that block gives every ERC-20 `Transfer` (three topics, one data word; ERC-721
transfers carry the token id as a fourth topic and are skipped). Transfers are grouped by transaction and netted per
account (`chain_adapters.net_positive`), so a routed swap or a flash-loan loop counts what actually changed hands; the
raw log sum is kept as `gross`. Nothing is keyed off a remembered token list: every
token seen in the sample is priced by contract address through DefiLlama, so the asset table is discovered, and a new
token that starts carrying value on a chain appears in it the day it does.

System transactions are separated from user ones, because on some rollups they are a large share of the count: the
OP-stack L1-attributes deposit (type 0x7e from 0xdead...0001, one per block) and Arbitrum's internal start-block
transaction (type 0x6a, one per block, a fifth of Arbitrum's raw count at 0.25 s blocks). Everything else counts.

Endpoint choice is discovery too: the registry's endpoints first, then chainlist's public endpoints for the chain id,
each accepted only after it answers `eth_chainId` with the right id and serves `eth_getLogs` for one block.
"""
import concurrent.futures as cf
import json
import re
import sys
import time

from chain_adapters import (Http, JsonRpc, RpcError, asset_rows, b58check, is_err, net_positive, register,
                            register_history, sample_points, stratified_total, window_dict, ROOT)

try:
    from Crypto.Hash import keccak as _keccak

    def keccak(s):
        k = _keccak.new(digest_bits=256)
        k.update(s.encode())
        return '0x' + k.hexdigest()
    TRANSFER = keccak('Transfer(address,address,uint256)')
except ImportError:  # the derivation above is the source of truth; this is its value, checked in the tests
    TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

OP_DEPOSITOR = '0xdeaddeaddeaddeaddeaddeaddeaddeaddead0001'
SEL_SYMBOL, SEL_DECIMALS = '0x95d89b41', '0x313ce567'
CHAINLIST = 'https://chainlist.org/rpcs.json'
_chainlist = None


def hx(v):
    if v is None:
        return 0
    if isinstance(v, int):
        return v
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


class InfuraClient:
    """live_rpc.RPC (key rotation, credit ceiling) behind the JsonRpc interface used here."""

    def __init__(self, network, max_credits=1_500_000):
        sys.path.insert(0, str(ROOT / 'scripts'))
        from live_rpc import RPC
        self.rpc = RPC(url='https://%s.infura.io/v3/' % network, max_credits=max_credits, interval=0.03)
        self.network = network
        self.calls = 0

    def public_name(self, u=None):
        return 'infura:%s' % self.network

    def call(self, method, params=None):
        self.calls += 1
        return self.rpc.call(method, params if params is not None else [])

    def batch(self, calls, allow_errors=True):
        out = []
        for i in range(0, len(calls), 10):
            part = calls[i:i + 10]
            self.calls += len(part)
            try:
                res = self.rpc.batch(part, allow_errors=True)
            except Exception as e:
                if not allow_errors:
                    raise
                res = [{'error': str(e)[:200]}] * len(part)
            for r in res:
                if isinstance(r, dict) and 'error' in r and ('jsonrpc' in r or 'id' in r):
                    r = {'error': r['error']}
                out.append(r)
        return out


def chainlist_urls(chain_id, http):
    global _chainlist
    if _chainlist is None:
        cache = ROOT / 'research' / 'chains' / 'cache' / 'chainlist_rpcs.json'
        try:
            if cache.exists() and time.time() - cache.stat().st_mtime < 7 * 86400:
                _chainlist = json.loads(cache.read_text())
            else:
                _chainlist = http.get(CHAINLIST, timeout=60)
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(_chainlist))
        except Exception:
            _chainlist = []
    for c in _chainlist:
        if c.get('chainId') == chain_id:
            urls = []
            for r in c.get('rpc') or []:
                u = r.get('url') if isinstance(r, dict) else r
                if not isinstance(u, str) or not u.startswith('https://') or '${' in u or 'API_KEY' in u.upper():
                    continue
                # tracking-free endpoints first; the probe reads public chain data only, but the order is still a choice
                track = r.get('tracking') if isinstance(r, dict) else None
                urls.append((0 if track == 'none' else 1 if track in (None, 'limited') else 2, u.strip()))
            return [u for _, u in sorted(urls)]
    return []


def endpoint_ok(url, chain_id, http):
    """(serves the chain, serves eth_getLogs, why): the right chain id, and logs for one recent block."""
    c = JsonRpc([url], http=http, batch_size=10)
    try:
        cid = hx(c.call('eth_chainId', []))
        if cid != chain_id:
            return False, False, 'chain id %s' % cid
        n = hx(c.call('eth_blockNumber', []))
    except Exception as e:
        return False, False, str(e)[:120]
    try:
        logs = c.call('eth_getLogs', [{'fromBlock': hex(n - 5), 'toBlock': hex(n - 5), 'topics': [TRANSFER]}])
        if not isinstance(logs, list):
            return True, False, 'getLogs malformed'
        return True, True, 'ok'
    except Exception as e:
        return True, False, 'no getLogs: ' + str(e)[:100]


def make_client(cfg, ctx):
    p = cfg.get('probe') or {}
    chain_id = cfg.get('evm_chain_id')
    notes = []
    if p.get('infura') and not ctx.no_infura:
        try:
            c = InfuraClient(p['infura'])
            cid = hx(c.call('eth_chainId', []))
            if cid == chain_id:
                return c, notes
            notes.append('infura answered chain id %s' % cid)
        except Exception as e:
            notes.append('infura unavailable: %s' % str(e)[:100])
    http = Http(min_interval=p.get('min_interval', 0.05), timeout=p.get('timeout', 45))
    cands = list(p.get('rpc') or [])
    if not p.get('rpc_only'):
        cands += [u for u in chainlist_urls(chain_id, http) if u not in cands]
    good, nologs = [], []
    for u in cands[:14]:
        ok, logs_ok, why = endpoint_ok(u, chain_id, http)
        if ok and logs_ok:
            good.append(u)
            if len(good) >= 3:
                break
        else:
            if ok:
                nologs.append(u)
            notes.append('%s rejected: %s' % (u.split('/')[2], why))
    if not good and nologs:
        # every endpoint serves blocks but none serves logs: count transactions and native value, and say so
        c = JsonRpc(nologs[:3], http=http, batch_size=p.get('batch', 10))
        c.no_logs = True
        notes.append('no endpoint serves eth_getLogs: token transfers not measured')
        return c, notes
    if not good:
        raise RuntimeError('no working endpoint (%d tried): %s' % (min(len(cands), 14), '; '.join(notes[-4:])))
    return JsonRpc(good, http=http, batch_size=p.get('batch', 10)), notes


def header(c, n):
    b = c.call('eth_getBlockByNumber', [hex(n) if isinstance(n, int) else n, False])
    if not b:
        raise RpcError({'message': 'no block %s' % n})
    return b


def block_at(c, ts, head_n, head_ts):
    """First block with timestamp >= ts, by a rate-seeded bracket and bisection; no constant-spacing assumption."""
    probe_back = min(head_n - 1, 2000)
    t_back = hx(header(c, head_n - probe_back)['timestamp'])
    spb = max((head_ts - t_back) / max(probe_back, 1), 1e-3)
    guess = int(head_n - (head_ts - ts) / spb)
    lo, hi = max(1, guess - 2000), min(head_n, guess + 2000)
    # widen until the bracket holds ts
    step = 4000
    while lo > 1 and hx(header(c, lo)['timestamp']) >= ts:
        lo, step = max(1, lo - step), step * 2
    step = 4000
    while hi < head_n and hx(header(c, hi)['timestamp']) < ts:
        hi, step = min(head_n, hi + step), step * 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if hx(header(c, mid)['timestamp']) >= ts:
            hi = mid
        else:
            lo = mid
    return hi


def tron_addr(hex20):
    return b58check(bytes.fromhex('41' + hex20[-40:]))


def fetch_samples(c, pts, workers, full=True, logs_too=True):
    chunks = [pts[i:i + 10] for i in range(0, len(pts), 10)]

    def blocks(part):
        return c.batch([('eth_getBlockByNumber', [hex(n), full]) for n in part])

    def logs(part):
        return c.batch([('eth_getLogs', [{'fromBlock': hex(n), 'toBlock': hex(n), 'topics': [TRANSFER]}]) for n in part])

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        B = [x for part in ex.map(blocks, chunks) for x in part]
        L = [x for part in ex.map(logs, chunks) for x in part] if logs_too else [[] for _ in pts]
    return B, L


@register('evm')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    tron = cfg.get('family') == 'tron'
    c, notes = make_client(cfg, ctx)
    head = header(c, 'latest')
    head_n, head_ts = hx(head['number']), hx(head['timestamp'])
    end_ts = min(ctx.end_ts, head_ts)
    first = block_at(c, ctx.start_ts, head_n, head_ts)
    last = head_n if end_ts >= head_ts else block_at(c, end_ts, head_n, head_ts) - 1
    N = last - first + 1
    n_samples = int(p.get('samples') or ctx.samples)
    pts = sample_points(first, last, n_samples, seed=int(ctx.start_ts))
    no_logs = getattr(c, 'no_logs', False)
    if getattr(ctx, 'tx_only', False):
        return tx_only(c, cfg, ctx, first, last, pts, end_ts, notes, t0)
    B, L = fetch_samples(c, pts, workers=int(p.get('workers', 4)), full=not p.get('headers_only'), logs_too=not no_logs)

    units = []                     # one row per sampled block that came back
    tok_count, tok_amt, tok_gross = {}, {}, {}   # token -> per-unit lists (raw ints): transfers, net value, gross value
    to_txs = {}                    # transaction target -> sampled transactions sent to it
    to_val = {}                    # (target, token) -> sampled net raw value of transactions sent to it
    # chain bookkeeping that is a real transaction but not activity: oracle pushes, validator signatures, builder
    # flashblock markers. Listed per chain in the registry (found by `top_targets_by_txs`), counted, reported beside.
    keeping = {a.lower() for a in (p.get('bookkeeping_targets') or [])}
    errors = []
    for n, b, lg in zip(pts, B, L):
        if not b or is_err(b):
            errors.append('block %d: %s' % (n, str(b)[:80] if b else 'null'))
            continue
        if is_err(lg) or lg is None:
            errors.append('logs %d: %s' % (n, str(lg)[:80]))
            lg = None
        txs = b.get('transactions') or []
        system = native = 0
        target = {}
        for tx in txs:
            if not isinstance(tx, dict):
                continue
            ty = hx(tx.get('type') or '0x0')
            frm = (tx.get('from') or '').lower()
            if (ty == 0x7e and frm == OP_DEPOSITOR) or ty == 0x6a:
                system += 1
                continue
            native += hx(tx.get('value') or '0x0')
            t = (tx.get('to') or 'create').lower()
            target[tx.get('hash')] = t
            to_txs[t] = to_txs.get(t, 0) + 1
        i = len(units)
        units.append({'n': n, 'ts': hx(b['timestamp']), 'txs': len(txs), 'system': system, 'native_raw': native,
                      'gas_used': hx(b.get('gasUsed')), 'base_fee': hx(b.get('baseFeePerGas') or '0x0'),
                      'logs_ok': lg is not None, 'transfer_logs': 0,
                      'bookkeeping': sum(1 for t in target.values() if t in keeping) if keeping else 0})
        moves = {}                 # (tx hash, token) -> [(from, to, amount)]
        for log in lg or []:
            tp = log.get('topics') or []
            data = log.get('data') or ''
            if len(tp) != 3 or len(data) != 66 or (tp[0] or '').lower() != TRANSFER:
                continue
            a = (log.get('address') or '').lower()
            v = int(data, 16)
            units[i]['transfer_logs'] += 1
            moves.setdefault((log.get('transactionHash'), a), []).append((tp[1][-40:].lower(), tp[2][-40:].lower(), v))
        for (h, a), mv in moves.items():
            k = (target.get(h, '?'), a)
            to_val[k] = to_val.get(k, 0) + net_positive(mv)
            cl = tok_count.setdefault(a, [])
            al = tok_amt.setdefault(a, [])
            gl = tok_gross.setdefault(a, [])
            while len(cl) <= i:
                cl.append(0)
                al.append(0)
                gl.append(0)
            cl[i] += len(mv)
            al[i] += net_positive(mv)
            gl[i] += sum(x for _, _, x in mv)
    n = len(units)
    # a block that failed to come back is dropped from the sample, not counted as empty
    N_eff = N
    user_tx, se = stratified_total([u['txs'] - u['system'] for u in units], N_eff)
    keep_tx, _ = stratified_total([u['bookkeeping'] for u in units], N_eff) if keeping else (None, None)
    raw_tx, _ = stratified_total([u['txs'] for u in units], N_eff)
    sys_tx, _ = stratified_total([u['system'] for u in units], N_eff)
    gas_total, _ = stratified_total([u['gas_used'] for u in units], N_eff)
    secs = max(1, end_ts - ctx.start_ts)

    # ------------------------------------------------------------------ price every token the sample saw
    key = p.get('llama_key') or (cfg.get('ids') or {}).get('llama_key')
    native_sym = (cfg.get('native') or {}).get('symbol')
    nat_key = 'coingecko:%s' % (cfg.get('native') or {}).get('coingecko') if (cfg.get('native') or {}).get('coingecko') else None
    tokens = sorted(tok_count, key=lambda a: -sum(tok_count[a]))[:int(p.get('max_tokens', 4000))]
    ids = {a: ('%s:%s' % (key, tron_addr(a) if tron else a)) for a in tokens} if key else {}
    priced = ctx.prices.get(list(ids.values()) + ([nat_key] if nat_key else []))
    meta, price_of, per_asset = {}, {}, {}
    for a in tokens:
        pr = priced.get(ids.get(a))
        dec = (pr or {}).get('decimals')
        if pr and dec is not None:
            meta[a] = {'symbol': pr.get('symbol'), 'decimals': dec}
            price_of[a] = pr.get('price')
            scale = 10 ** int(dec)
            per_asset[a] = {'count': tok_count[a], 'amount': [x / scale for x in tok_amt[a]],
                            'gross': [x / scale for x in tok_gross[a]]}
    # unpriced: name the busiest ones on chain so the table can still say what they are
    unp = [a for a in tokens if a not in price_of][:int(p.get('name_unpriced', 25))]
    if unp and not p.get('skip_names'):
        res = c.batch([('eth_call', [{'to': a, 'data': SEL_SYMBOL}, 'latest']) for a in unp] +
                      [('eth_call', [{'to': a, 'data': SEL_DECIMALS}, 'latest']) for a in unp])
        for j, a in enumerate(unp):
            sym, dec = res[j], res[len(unp) + j]
            meta[a] = {'symbol': dec_str(sym) if isinstance(sym, str) else None,
                       'decimals': hx(dec) if isinstance(dec, str) and dec not in ('0x', '') and len(dec) <= 66 else None}
    for a in unp:
        m = meta.get(a) or {}
        d = m.get('decimals')
        scale = 10 ** d if isinstance(d, int) and 0 <= d <= 36 else None
        per_asset[a] = {'count': tok_count[a], 'amount': [(x / scale) if scale else 0.0 for x in tok_amt[a]],
                        'gross': [(x / scale) if scale else 0.0 for x in tok_gross[a]]}
    nat_dec = int((cfg.get('native') or {}).get('decimals', 6 if tron else 18))
    nat_id = 'native:%s' % (native_sym or '?')
    per_asset[nat_id] = {'count': [1 if u['native_raw'] else 0 for u in units],
                         'amount': [u['native_raw'] / 10 ** nat_dec for u in units]}
    meta[nat_id] = {'symbol': native_sym, 'decimals': nat_dec}
    price_of[nat_id] = (priced.get(nat_key) or {}).get('price') if nat_key else None
    tr = asset_rows(per_asset, n, N_eff, meta, price_of, native_symbols=[native_sym] if native_sym else [])
    for r in tr['assets'] + tr['unpriced_top']:
        if r['asset'] == nat_id:
            r['note'] = 'top-level transaction value only; internal transfers need traces'
            r['transfers'] = None
            r['transfers_se'] = None
        elif tron:
            r['address_base58'] = tron_addr(r['asset'])
    tr['method'] = ('sampled-blocks; native value only — no public endpoint serves eth_getLogs' if no_logs else
                    'sampled-blocks; value = net per transaction (each account\'s positive net change), gross beside it')
    # who the activity is: the contracts transactions are sent to, by share of transactions and of priced value
    scale_n = (N_eff / n) if n else 0
    usd_to = {}
    for (t, a), raw in to_val.items():
        pr_ = price_of.get(a)
        dec = (meta.get(a) or {}).get('decimals')
        if pr_ is not None and isinstance(dec, int):
            usd_to[t] = usd_to.get(t, 0.0) + raw / 10 ** dec * pr_ * scale_n
    tot_usd = sum(usd_to.values()) or None
    tot_tx = sum(to_txs.values()) or None
    tr['top_targets_by_value'] = [{'to': t, 'usd': v, 'share': v / tot_usd} for t, v in
                                  sorted(usd_to.items(), key=lambda kv: -kv[1])[:10]] if tot_usd else []
    tr['top_targets_by_txs'] = [{'to': t, 'txs': c_ * scale_n, 'share': c_ / tot_tx} for t, c_ in
                                sorted(to_txs.items(), key=lambda kv: -kv[1])[:10]] if tot_tx else []
    if tron:
        for x in tr['top_targets_by_value'] + tr['top_targets_by_txs']:
            if x['to'].startswith('0x') and len(x['to']) == 42:
                x['to_base58'] = tron_addr(x['to'])
    tr['transfer_logs_per_block'] = (sum(u['transfer_logs'] for u in units) / n) if n else None
    tr['logs_missing_blocks'] = sum(1 for u in units if not u['logs_ok'])
    base_fees = sorted(u['base_fee'] for u in units if u['base_fee'])
    return {
        'tx': {'count': user_tx, 'se': se, 'raw_count': raw_tx, 'system_count': sys_tx, 'method': 'sampled-blocks',
               'system_per_block': (sys_tx / N) if N and sys_tx is not None else None,
               'bookkeeping': keep_tx, 'count_ex_bookkeeping': (user_tx - keep_tx) if keep_tx is not None and user_tx is not None else None,
               'bookkeeping_targets': sorted(keeping) or None,
               'blocks': N, 'sampled': n, 'per_block': (user_tx / N) if N and user_tx is not None else None,
               'tps': (user_tx / secs) if user_tx is not None else None,
               'note': 'user transactions: OP-stack L1-attributes deposits and Arbitrum internal txs excluded'},
        'gas': {'gas_per_second': (gas_total / secs) if gas_total is not None else None,
                'base_fee_median_gwei': (base_fees[len(base_fees) // 2] / 1e9) if base_fees else None},
        'transfers': tr,
        'window': window_dict(ctx.start_ts, end_ts),
        'blocks': {'first': first, 'last': last, 'head': head_n},
        'endpoint': c.public_name(), 'calls': getattr(c, 'calls', None), 'notes': notes,
        'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}


def tx_only(c, cfg, ctx, first, last, pts, end_ts, notes, t0):
    """Transactions only, for the daily backfill: headers without bodies or logs, so a day costs a few hundred kB.

    A header lists transaction hashes but not types, so system transactions cannot be told apart here; they are
    subtracted at the per-block rate the full probe measured (`cfg['_system_per_block']`: exactly 1.0 on OP-stack and
    Arbitrum-family chains, 0 elsewhere), which is a property of the chain's block format rather than of its traffic.
    """
    B, _ = fetch_samples(c, pts, workers=int((cfg.get('probe') or {}).get('workers', 4)), full=False, logs_too=False)
    counts = [len(b.get('transactions') or []) for b in B if isinstance(b, dict) and 'transactions' in b]
    N = last - first + 1
    raw, se = stratified_total(counts, N)
    spb = float(cfg.get('_system_per_block') or 0.0)
    user = (raw - spb * N) if raw is not None else None
    return {'tx': {'count': user, 'se': se, 'raw_count': raw, 'system_count': spb * N, 'method': 'sampled-headers',
                   'blocks': N, 'sampled': len(counts), 'system_per_block': spb,
                   'note': 'transactions-only backfill: system transactions subtracted at the full probe\'s per-block rate'},
            'transfers': None, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last}, 'endpoint': c.public_name(), 'notes': notes,
            'errors': [], 'error_count': len(pts) - len(counts), 'seconds': round(time.time() - t0, 1)}


def block_after(c, ts, lo, head_n, step):
    """First block with timestamp >= ts, given a block `lo` known to be earlier and a step of about a day's blocks."""
    hi = min(head_n, lo + step)
    while hi < head_n and hx(header(c, hi)['timestamp']) < ts:
        lo, hi = hi, min(head_n, hi + step)
    if hx(header(c, hi)['timestamp']) < ts:
        return head_n + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if hx(header(c, mid)['timestamp']) >= ts:
            hi = mid
        else:
            lo = mid
    return hi


@register_history('evm')
@register_history('tron')
def history(cfg, ctx, day_starts, samples):
    """Daily user-transaction counts for consecutive UTC days in one pass: one endpoint choice, each day boundary
    found once (the end of a day is the start of the next) by bisecting forward from the previous one, and a header
    sample per day. System transactions are subtracted at the per-block rate the full probe measured."""
    c, notes = make_client(cfg, ctx)
    head = header(c, 'latest')
    head_n, head_ts = hx(head['number']), hx(head['timestamp'])
    days = sorted(int(d) for d in day_starts)
    b0 = block_at(c, days[0], head_n, head_ts)
    bounds = [b0]
    step = None
    for ts in days[1:] + [days[-1] + 86400]:
        if ts > head_ts:
            bounds.append(head_n + 1)
            continue
        if step is None:
            # a day's worth of blocks, from the chain's recent rate; bisection corrects any error in it
            back = min(head_n - 1, 5000)
            spb = max((head_ts - hx(header(c, head_n - back)['timestamp'])) / back, 1e-3)
            step = max(1000, int(86400 / spb))
        bounds.append(block_after(c, ts, bounds[-1], head_n, step))
    spb_sys = float(cfg.get('_system_per_block') or 0.0)
    rows = []
    for k, ts in enumerate(days):
        first, last = bounds[k], bounds[k + 1] - 1
        N = last - first + 1
        if N <= 0:
            continue
        pts = sample_points(first, last, samples, seed=ts)
        B, _ = fetch_samples(c, pts, workers=int((cfg.get('probe') or {}).get('workers', 4)), full=False, logs_too=False)
        counts = [len(b.get('transactions') or []) for b in B if isinstance(b, dict) and 'transactions' in b]
        raw, se = stratified_total(counts, N)
        rows.append({'day_start': ts, 'count': (raw - spb_sys * N) if raw is not None else None, 'se': se,
                     'raw_count': raw, 'blocks': N, 'sampled': len(counts), 'method': 'sampled-headers',
                     'system_per_block': spb_sys, 'endpoint': c.public_name()})
    return rows


def dec_str(data):
    """ABI-decode a string return, tolerating the bytes32 form some old tokens use."""
    if not data or data == '0x' or not re.match(r'^0x[0-9a-fA-F]*$', data):
        return None
    b = bytes.fromhex(data[2:])
    if len(b) >= 64:
        try:
            n = int.from_bytes(b[32:64], 'big')
            if 0 < n <= len(b) - 64:
                return b[64:64 + n].decode('utf-8', 'replace')[:32]
        except Exception:
            pass
    return b.rstrip(b'\x00').decode('utf-8', 'replace')[:32] or None


@register('tron')
def probe_tron(cfg, ctx):
    """Tron through its Ethereum-compatible JSON-RPC: the same blocks and TRC-20 Transfer logs, priced by base58 address."""
    return probe(cfg, ctx)
