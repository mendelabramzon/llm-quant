#!/usr/bin/env python3
"""NEAR: transactions, receipts and transfer value from a stratified sample of blocks, read chunk by chunk.

Shape of the chain. A NEAR block is a header plus one chunk per shard (ten in October 2026); transactions live in the
chunks, and a transaction's work continues as *receipts* that may execute in later blocks and other shards. So a block
is read as its header and every chunk it actually included (`height_included` equal to the block height; a chunk
copied forward from an earlier block is skipped, or it would be counted twice). Heights are the sampling unit: a
height with no block (NEAR skips heights) is a real zero, so the stratified estimate over heights stays unbiased.

Counting. `tx.count` is signed transactions — the figure NEAR explorers publish — and `tx.receipts` the receipts
routed through the sampled chunks (gas refunds from `system` excluded). nearblocks' daily series (`/v1/charts`) is
attached as an independent reference; it counts UTC days, so it agrees with a trailing 24 hours only to within the
day-to-day change.

Value. Moves are read from the actions themselves: a `Transfer` deposit and the deposit attached to a function call
move NEAR; `ft_transfer` / `ft_transfer_call` on a token contract move that token from the caller to
`args.receiver_id`. Actions are taken from the signed transactions and from receipts that a *contract* created
(predecessor is not the signer), because a receipt whose predecessor is the signer is the transaction's own actions
routed to another shard and would count them twice. Receipts do not name their transaction and a cross-contract route
spans several blocks, so the repo's net-per-transaction convention is applied as net per block and token
(`net_positive` over the block's moves): a hop that passes a token on inside one block cancels, a route spread over
blocks is counted hop by hop. `gross_amount` keeps every move. NEAR Intents (`intents.near`) settles most of its
trading on an internal ledger; only deposits into it and withdrawals out of it appear here as token moves.

Limits. Meta-transactions (`Delegate` actions) are counted through the receipt they produce, so a delegate whose
inner receipt stays inside the signer's shard is missed. NEP-245 multi-token moves are not decoded.
"""
import base64
import concurrent.futures as cf
import json
import re
import threading
import time

from chain_adapters import (Http, HttpError, asset_rows, net_positive, register, sample_points, stratified_total,
                            window_dict)

FALLBACK_RPC = ['https://rpc.mainnet.fastnear.com', 'https://near.drpc.org', 'https://archival-rpc.mainnet.fastnear.com',
                'https://free.rpc.fastnear.com', 'https://rpc.mainnet.near.org']
# Verified 2026-10-09: the non-archival fastnear hosts answer UNKNOWN_BLOCK for blocks ~23 hours old, which a probe
# would read as skipped heights (real zeros) and so halve a 24-hour count. A "not found" is therefore believed only
# when an archival endpoint says it too.
ARCHIVAL = ('https://archival-rpc.mainnet.fastnear.com',)
NEARBLOCKS = 'https://api.nearblocks.io/v1'
DEFAULT_SAMPLES = 56          # ~11 calls a block: ~3.5 minutes for a day at the public endpoints' pace
FT_METHODS = ('ft_transfer', 'ft_transfer_call')
# wrap.near is NEAR's canonical wrapped native (1:1 through near_deposit / near_withdraw), priced as NEAR the way the
# Solana adapter prices the WSOL mint as SOL; the feed's own wNEAR price wanders below its confidence floor.
WRAPPED_NATIVE = 'wrap.near'
# Omni bridge tokens (the assets NEAR Intents trades) are named for what they bridge: '<chain>-<0x contract>.omft.near'
# is that ERC-20 and '<chain>.omft.near' that chain's native coin, so the name is the identity the price feed needs.
OMFT_EVM_PREFIX = {'eth': 'ethereum', 'arb': 'arbitrum', 'base': 'base', 'bsc': 'bsc', 'pol': 'polygon', 'avax': 'avax',
                   'op': 'optimism', 'gnosis': 'xdai', 'bera': 'berachain'}
OMFT_NATIVE = {'eth': ('ETH', 18, 'ethereum'), 'arb': ('ETH', 18, 'ethereum'), 'base': ('ETH', 18, 'ethereum'),
               'op': ('ETH', 18, 'ethereum'), 'btc': ('BTC', 8, 'bitcoin'), 'sol': ('SOL', 9, 'solana'),
               'zec': ('ZEC', 8, 'zcash'), 'doge': ('DOGE', 8, 'dogecoin'), 'xrp': ('XRP', 6, 'ripple'),
               'bsc': ('BNB', 18, 'binancecoin'), 'pol': ('POL', 18, 'polygon-ecosystem-token'),
               'avax': ('AVAX', 18, 'avalanche-2'), 'bera': ('BERA', 18, 'berachain-bera'), 'gnosis': ('XDAI', 18, 'xdai'),
               'tron': ('TRX', 6, 'tron'), 'ltc': ('LTC', 8, 'litecoin'), 'bch': ('BCH', 8, 'bitcoin-cash')}
_OMFT_ERC20 = re.compile(r'^([a-z]+)-(0x[0-9a-f]{40})\.omft\.near$')
_OMFT_NATIVE = re.compile(r'^([a-z]+)\.omft\.near$')


def omft_identity(account):
    """(price key, symbol or None, decimals or None) for an Omni bridge token account, else None."""
    m = _OMFT_ERC20.match(account or '')
    if m and m.group(1) in OMFT_EVM_PREFIX:
        return '%s:%s' % (OMFT_EVM_PREFIX[m.group(1)], m.group(2)), None, None
    m = _OMFT_NATIVE.match(account or '')
    if m and m.group(1) in OMFT_NATIVE:
        sym, dec, cg = OMFT_NATIVE[m.group(1)]
        return 'coingecko:%s' % cg, sym, dec
    return None
NOT_FOUND = ('UNKNOWN_BLOCK', 'UNKNOWN_CHUNK', 'DB Not Found', 'NOT_FOUND', 'GARBAGE_COLLECTED')
YOCTO = 1e24


class NotFound(Exception):
    pass


class NearRpc:
    """Round-robin over endpoints; a 429 parks one endpoint. A missing block or chunk is an answer only when an
    archival endpoint confirms it (or every endpoint agrees): pruned nodes say "unknown" about history they dropped."""

    def __init__(self, urls, http, archival=ARCHIVAL):
        self.urls = list(dict.fromkeys(u.rstrip('/') for u in urls if u))
        self.archival = [u for u in self.urls if u in {a.rstrip('/') for a in archival}]
        self.http = http
        self.parked = {}
        self.i = 0
        self.lock = threading.Lock()
        self.calls = 0
        self.used = {}

    def _next(self):
        with self.lock:
            now = time.monotonic()
            for _ in range(len(self.urls)):
                u = self.urls[self.i % len(self.urls)]
                self.i += 1
                if self.parked.get(u, 0) <= now:
                    return u
            return min(self.urls, key=lambda u: self.parked.get(u, 0))

    def _not_found(self, u, nf, why):
        """Record a 'not found' from u; raise NotFound once it is confirmed, else return the endpoint to ask next."""
        nf.add(u)
        if u in self.archival or len(nf) >= len(self.urls):
            raise NotFound(why[:120])
        nxt = [a for a in self.archival if a not in nf]
        return nxt[0] if nxt else None

    def call(self, method, params):
        last = None
        nf = set()
        forced = None
        for attempt in range(2 * len(self.urls) + 2):
            u = forced or self._next()
            forced = None
            if u in nf:
                continue
            wait = self.parked.get(u, 0) - time.monotonic()
            if wait > 0:
                time.sleep(min(wait, 10))
            try:
                d = self.http.post(u, {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params})
            except HttpError as e:
                body = str(e.body or '')
                if any(k in body for k in NOT_FOUND):
                    forced = self._not_found(u, nf, body)
                    continue
                last = e
                with self.lock:
                    self.parked[u] = time.monotonic() + (30 if e.code == 429 else 10)
                continue
            err = d.get('error') if isinstance(d, dict) else None
            if err:
                txt = json.dumps(err)
                if any(k in txt for k in NOT_FOUND):
                    forced = self._not_found(u, nf, txt)
                    continue
                last = RuntimeError(txt[:160])
                with self.lock:
                    self.parked[u] = time.monotonic() + 10
                continue
            with self.lock:
                self.calls += 1
                self.used[u] = self.used.get(u, 0) + 1
            return d['result']
        raise RuntimeError('%s failed on every endpoint: %s' % (method, str(last)[:160]))

    def block(self, h):
        return self.call('block', {'block_id': h} if h != 'final' else {'finality': 'final'})


def block_ts(b):
    return int(b['header']['timestamp']) / 1e9


def decode_args(args_b64):
    """FunctionCall args (base64 JSON) -> dict, or {} when the args are not JSON."""
    try:
        v = json.loads(base64.b64decode(args_b64 or ''))
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def action_moves(sender, receiver, actions):
    """Moves an action list makes: [('native'|token_contract, from, to, raw amount)]."""
    out = []
    for a in actions or []:
        if not isinstance(a, dict):
            continue
        if 'Transfer' in a:
            v = int((a['Transfer'] or {}).get('deposit') or 0)
            if v > 0:
                out.append(('native', sender, receiver, v))
        elif 'FunctionCall' in a:
            fc = a['FunctionCall'] or {}
            v = int(fc.get('deposit') or 0)
            if v > 1:            # one yoctoNEAR is the security deposit ft_transfer requires, not value
                out.append(('native', sender, receiver, v))
            if fc.get('method_name') in FT_METHODS:
                args = decode_args(fc.get('args'))
                try:
                    amt = int(args.get('amount'))
                except (TypeError, ValueError):
                    amt = None
                if amt and amt > 0 and args.get('receiver_id'):
                    out.append((receiver, sender, args['receiver_id'], amt))
    return out


def reduce_chunks(chunks):
    """Chunks of one block -> counts, and per asset [moves, net (per block), gross]."""
    txs = receipts = refunds = 0
    moves = {}
    for ch in chunks:
        for t in ch.get('transactions') or []:
            txs += 1
            for asset, f, to, v in action_moves(t.get('signer_id'), t.get('receiver_id'), t.get('actions')):
                moves.setdefault(asset, []).append((f, to, v))
        for r in ch.get('receipts') or []:
            pred = r.get('predecessor_id')
            if pred == 'system':
                refunds += 1
                continue
            receipts += 1
            act = (r.get('receipt') or {}).get('Action')
            if not act or pred == act.get('signer_id'):
                continue       # a data receipt, or the transaction's own actions routed to another shard
            for asset, f, to, v in action_moves(pred, r.get('receiver_id'), act.get('actions')):
                moves.setdefault(asset, []).append((f, to, v))
    per = {a: [len(mv), net_positive(mv), sum(v for _, _, v in mv)] for a, mv in moves.items()}
    return {'txs': txs, 'receipts': receipts, 'refunds': refunds, 'assets': per}


def nearblocks_reference(http, base=NEARBLOCKS):
    try:
        ch = http.get(base + '/charts', timeout=60).get('charts') or []
    except Exception as e:
        return {'source': 'nearblocks /v1/charts', 'error': str(e)[:100]}
    rows = [r for r in ch if r.get('txns') not in (None, '')]
    if not rows:
        return {'source': 'nearblocks /v1/charts', 'error': 'empty'}
    last = rows[-1]
    return {'source': 'nearblocks /v1/charts', 'date': (last.get('date') or '')[:10], 'txns': int(float(last['txns'])),
            'previous': [(r['date'][:10], int(float(r['txns']))) for r in rows[-8:-1]]}


@register('near')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    http = Http(min_interval=float(p.get('min_interval', 0.12)), timeout=p.get('timeout', 40), retries=1)
    c = NearRpc(list(p.get('rpc') or []) + FALLBACK_RPC, http)
    head = c.block('final')
    head_h, head_ts = int(head['header']['height']), block_ts(head)
    end_ts = min(ctx.end_ts, head_ts)

    def ts_at_or_after(h):
        for k in range(8):
            try:
                return h + k, block_ts(c.block(h + k))
            except NotFound:
                continue
        raise RuntimeError('no block at %d..%d' % (h, h + 7))

    def first_at(ts):
        """First existing height whose block time >= ts: bracket seeded by the recent block rate, then bisection.
        f(h) is the first existing block at or after h, so f is monotone even though NEAR skips heights."""
        back = 5000
        _, t_back = ts_at_or_after(head_h - back)
        spb = max((head_ts - t_back) / back, 0.05)
        guess = int(head_h - (head_ts - ts) / spb)
        lo, hi = guess - 4000, min(head_h, guess + 4000)
        step = 8000
        while ts_at_or_after(lo)[1] >= ts:
            lo, step = lo - step, step * 2
        step = 8000
        while ts_at_or_after(hi)[1] < ts:
            if hi >= head_h:
                return head_h + 1
            hi, step = min(head_h, hi + step), step * 2
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            h_, t_ = ts_at_or_after(mid)
            if t_ >= ts:
                hi = mid
            else:
                lo = max(mid, min(h_, hi - 1))
        return ts_at_or_after(hi)[0]

    first = first_at(ctx.start_ts)
    last = head_h if end_ts >= head_ts else first_at(end_ts) - 1
    H = last - first + 1
    n = min(int(p.get('samples') or min(ctx.samples, DEFAULT_SAMPLES)), H)
    heights = sample_points(first, last, n, seed=int(ctx.start_ts))
    workers = int(p.get('workers', 6))
    errors = []

    def get_block(h):
        try:
            return h, c.block(h), None
        except NotFound:
            return h, None, None                    # a skipped height: a real zero
        except Exception as e:
            return h, None, 'block %d: %s' % (h, str(e)[:100])

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        blocks = list(ex.map(get_block, heights))
    errors += [err for _, _, err in blocks if err]
    want = []
    for h, b, err in blocks:
        if b:
            want += [(h, ch['chunk_hash']) for ch in b.get('chunks') or [] if int(ch.get('height_included', -1)) == h]

    def get_chunk(item):
        h, ch = item
        try:
            return h, c.call('chunk', {'chunk_id': ch}), None
        except Exception as e:
            return h, None, 'chunk %s@%d: %s' % (ch[:8], h, str(e)[:80])

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        chunks = list(ex.map(get_chunk, want))
    by_h = {}
    bad_h = set()
    for h, chk, err in chunks:
        if err:
            errors.append(err)
            bad_h.add(h)            # a block with a missing chunk is dropped from the sample, not undercounted
            continue
        by_h.setdefault(h, []).append(chk)
    units = []
    for h, b, err in blocks:
        if err or h in bad_h:
            continue
        units.append(reduce_chunks(by_h.get(h, [])) if b else {'txs': 0, 'receipts': 0, 'refunds': 0, 'assets': {}})
    k = len(units)
    if not k:
        raise RuntimeError('no sampled block could be read: %s' % '; '.join(errors[:3]))
    txc, txse = stratified_total([u['txs'] for u in units], H)
    rc, rcse = stratified_total([u['receipts'] for u in units], H)
    secs = max(1, end_ts - ctx.start_ts)

    # ------------------------------------------------------------------ value
    assets = sorted({a for u in units for a in u['assets']})
    tokens = [a for a in assets if a != 'native']
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'near')
    omft = {t: omft_identity(t) for t in tokens if omft_identity(t)}
    pr = ctx.prices.get(['near:%s' % t for t in tokens] + [nat_key] + [v[0] for v in omft.values()])
    meta, price_of, per = {}, {}, {}
    unnamed = []
    for a in assets:
        cnt = [u['assets'].get(a, [0, 0, 0])[0] for u in units]
        net = [u['assets'].get(a, [0, 0, 0])[1] for u in units]
        gross = [u['assets'].get(a, [0, 0, 0])[2] for u in units]
        if a == 'native':
            aid, dec, q = 'native:NEAR', 24, pr.get(nat_key)
            meta[aid] = {'symbol': (cfg.get('native') or {}).get('symbol') or 'NEAR', 'decimals': 24}
        elif a == WRAPPED_NATIVE:
            aid, dec, q = a, 24, pr.get(nat_key)
            meta[aid] = {'symbol': 'wNEAR', 'decimals': 24}
        elif a in omft and not pr.get('near:%s' % a):
            key, sym, dec = omft[a]
            aid, q = a, pr.get(key)
            dec = dec if dec is not None else (int(q['decimals']) if q and q.get('decimals') is not None else None)
            meta[aid] = {'symbol': sym or (q or {}).get('symbol'), 'decimals': dec}
        else:
            aid, q = a, pr.get('near:%s' % a)
            dec = int(q['decimals']) if q and q.get('decimals') is not None else None
            meta[aid] = {'symbol': (q or {}).get('symbol'), 'decimals': dec}
            if q is None:
                unnamed.append((sum(cnt), a))
        price_of[aid] = q.get('price') if (q and dec is not None) else None
        per[aid] = {'count': cnt, 'amount': [x / 10 ** dec for x in net] if dec is not None else [0.0] * k,
                    'gross': [x / 10 ** dec for x in gross] if dec is not None else [0.0] * k}
    # name the busiest unpriced tokens from their own ft_metadata so the table can say what they are
    for _, a in sorted(unnamed, reverse=True)[:int(p.get('name_unpriced', 8))]:
        try:
            r = c.call('query', {'request_type': 'call_function', 'finality': 'final', 'account_id': a,
                                 'method_name': 'ft_metadata', 'args_base64': 'e30='})
            md = json.loads(bytes(r.get('result') or []).decode() or '{}')
            meta[a] = {'symbol': md.get('symbol'), 'decimals': md.get('decimals')}
        except Exception:
            pass
    tr = asset_rows(per, k, H, meta, price_of, native_symbols=['NEAR'])
    for r in tr['assets'] + tr['unpriced_top']:
        if r['asset'] == 'native:NEAR':
            r['note'] = 'Transfer and function-call deposits (one-yocto security deposits excluded); gas refunds excluded'
    tr['method'] = ('sampled-blocks (actions of signed transactions and of contract-created receipts; amount = net per '
                    'block and token, gross_amount = every move)')
    tx = {'count': txc, 'se': txse, 'method': 'sampled-blocks', 'receipts': rc, 'receipts_se': rcse,
          'blocks': H, 'sampled': k, 'missing_heights': sum(1 for _, b, err in blocks if b is None and not err),
          'tps': (txc / secs) if txc is not None else None,
          'reference': nearblocks_reference(http),
          'note': 'signed transactions (explorer convention); receipts reported apart, gas refunds excluded'}
    if tx['reference'].get('txns') and txc is not None:
        tx['reference']['probe_per_day'] = txc * 86400.0 / secs
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'head': head_h},
            'endpoint': ', '.join(u.replace('https://', '') for u, _ in sorted(c.used.items(), key=lambda kv: -kv[1])[:3]),
            'calls': c.calls, 'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
