#!/usr/bin/env python3
"""Starknet: transactions and ERC-20 transfer value over a window, from a stratified sample of blocks, over the
Starknet JSON-RPC (spec 0.9 on Infura; any public endpoint that answers `starknet_chainId` with SN_MAIN as fallback).

Counting. Starknet has no cumulative transaction counter, so the count is estimated: one
`starknet_getBlockWithTxHashes` per sampled block (hashes only, a few hundred bytes) gives its transaction count, and
the stratified total over the window's blocks carries a standard error. Every transaction type counts (INVOKE,
DEPLOY_ACCOUNT, DECLARE and the L1_HANDLER messages that carry bridge deposits), which is what growthepie and L2Beat
count too.

Value. `starknet_getEvents` on each sampled block, filtered on the `Transfer` key (sn_keccak("Transfer")), returns every
token transfer; two layouts are in use and both are decoded — Cairo-1 tokens index the parties
(keys = [sel, from, to], data = [amount.low, amount.high]) and Cairo-0 tokens do not (keys = [sel],
data = [from, to, amount.low, amount.high]). An ERC-721 transfer either indexes the token id (five keys, skipped) or
uses the Cairo-0 layout with the id in place of the amount; the latter is indistinguishable by shape and is left to
pricing, which only values contracts DefiLlama prices as fungible tokens. The headline amount is net per transaction
and token (`chain_adapters.net_positive`): events are grouped by transaction hash and only each account's positive net
change counts, so a router hop or a flash loan repaid in full adds nothing; the raw event sum is kept as `gross`. Fees
are themselves STRK transfers to the sequencer, so STRK's transfer count includes one per transaction. Tokens are priced as `starknet:<address>`; Starknet
has no native value field, so STRK and ETH appear as the ERC-20s they are.
"""
import concurrent.futures as cf
import re
import sys
import time

from chain_adapters import (Http, JsonRpc, ROOT, asset_rows, is_err, net_positive, register, sample_points,
                            stratified_total, window_dict)
from chain_adapters._search import kary_first_at, seeded_bracket

try:
    from Crypto.Hash import keccak as _keccak

    def sn_keccak(name):
        """Starknet selector: keccak256 of the ASCII name, masked to 250 bits."""
        k = _keccak.new(digest_bits=256)
        k.update(name.encode())
        return hex(int(k.hexdigest(), 16) & ((1 << 250) - 1))
except ImportError:  # pragma: no cover - pycryptodome is part of every run command in this repo
    sn_keccak = None

TRANSFER_SEL = sn_keccak('Transfer') if sn_keccak else '0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9'
SYMBOL_SEL = sn_keccak('symbol') if sn_keccak else None
DECIMALS_SEL = sn_keccak('decimals') if sn_keccak else None
SN_MAIN = '0x534e5f4d41494e'          # 'SN_MAIN' as a short string
EVENTS_CHUNK = 1000
SEARCH_FANOUT = 20


def felt(x):
    return int(x, 16) if isinstance(x, str) else int(x)


def norm_addr(a):
    """Starknet addresses as 0x + 64 lowercase hex digits (DefiLlama accepts padded and unpadded; padded is canonical)."""
    return '0x' + format(felt(a), 'x').rjust(64, '0')


def decode_transfer(ev):
    """(token, from, to, amount) for a fungible Transfer event in either layout, or None.

    Cairo-1 / OpenZeppelin >= 0.8: keys = [sel, from, to], data = [low, high]
    Cairo-0:                       keys = [sel],             data = [from, to, low, high]
    A single-felt Cairo-0 amount (data = [from, to, amount]) is accepted too. Anything else (ERC-721 with an indexed
    token id, malformed events) is not a fungible transfer.
    """
    keys, data = ev.get('keys') or [], ev.get('data') or []
    if not keys or felt(keys[0]) != felt(TRANSFER_SEL):
        return None
    if len(keys) == 3 and len(data) == 2:
        frm, to, amt = keys[1], keys[2], felt(data[0]) + (felt(data[1]) << 128)
    elif len(keys) == 1 and len(data) == 4:
        frm, to, amt = data[0], data[1], felt(data[2]) + (felt(data[3]) << 128)
    elif len(keys) == 1 and len(data) == 3:
        frm, to, amt = data[0], data[1], felt(data[2])
    else:
        return None
    return norm_addr(ev.get('from_address')), norm_addr(frm), norm_addr(to), amt


def block_token_sums(events):
    """{token: [transfer events, net raw, gross raw]} for one block's Transfer events.

    Net is per transaction and token (`chain_adapters.net_positive`: every account's positive net change, so a router
    hop or a flash loan repaid in full counts nothing); gross is every event's amount.
    """
    by_tx = {}
    for e in events:
        d = decode_transfer(e)
        if not d:
            continue
        tok, frm, to, amt = d
        by_tx.setdefault((e.get('transaction_hash'), tok), []).append((frm, to, amt))
    out = {}
    for (_, tok), moves in by_tx.items():
        v = out.setdefault(tok, [0, 0, 0])
        v[0] += len(moves)
        v[1] += net_positive(moves)
        v[2] += sum(m[2] for m in moves)
    return out


def decode_short_string(felts):
    """A Cairo short string (one felt) or ByteArray ([n_words, *words, pending_word, pending_len]) to text."""
    vals = [felt(x) for x in felts or []]
    if not vals:
        return None
    if len(vals) == 1:
        b = vals[0].to_bytes(32, 'big').lstrip(b'\x00')
        return b.decode('utf-8', 'replace') or None
    n = vals[0]
    if len(vals) == n + 3:
        out = b''.join(w.to_bytes(31, 'big') for w in vals[1:1 + n])
        plen = vals[-1]
        if plen:
            out += vals[-2].to_bytes(plen, 'big')
        return out.decode('utf-8', 'replace') or None
    return None


class InfuraStarknet:
    """live_rpc.RPC (key rotation, credit ceiling) on the Starknet network, behind the JsonRpc interface."""

    def __init__(self, network='starknet-mainnet', max_credits=1_000_000):
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


def make_client(cfg, ctx):
    p = cfg.get('probe') or {}
    notes = []
    if p.get('infura') and not getattr(ctx, 'no_infura', False) and (ROOT / 'infura_keys.txt').exists():
        try:
            c = InfuraStarknet(p['infura'])
            if c.call('starknet_chainId', []) == SN_MAIN:
                return c, notes
            notes.append('infura answered another chain id')
        except Exception as e:
            notes.append('infura unavailable: %s' % str(e)[:100])
    http = Http(min_interval=p.get('min_interval', 0.05), timeout=p.get('timeout', 45))
    for u in p.get('rpc') or []:
        c = JsonRpc([u], http=http, batch_size=10)
        try:
            if c.call('starknet_chainId', []) == SN_MAIN:
                return c, notes
            notes.append('%s: wrong chain id' % u.split('/')[2])
        except Exception as e:
            notes.append('%s: %s' % (u.split('/')[2], str(e)[:80]))
    raise RuntimeError('no working Starknet endpoint: ' + '; '.join(notes[-4:]))


def header(c, n):
    b = c.call('starknet_getBlockWithTxHashes', [{'block_number': n} if isinstance(n, int) else n])
    if not b or 'timestamp' not in b:
        raise RuntimeError('no block %s' % n)
    return b


def block_at(c, ts, head_n, head_ts, rate):
    """First block whose timestamp is >= ts: a rate-seeded bracket, then a k-ary search over batched headers."""
    cache = {}

    def read(xs):
        todo = [x for x in xs if x not in cache and 0 <= x <= head_n]
        res = c.batch([('starknet_getBlockWithTxHashes', [{'block_number': x}]) for x in todo])
        for x, b in zip(todo, res):
            cache[x] = b.get('timestamp') if isinstance(b, dict) and not is_err(b) else None
        return {x: cache.get(x) for x in xs}
    lo, hi = seeded_bracket(lambda x: read([x]).get(x), ts, head_n, head_ts, rate)
    return kary_first_at(read, lo, hi, ts, fanout=SEARCH_FANOUT)


def block_events(c, n):
    """Every Transfer event of block n, following continuation tokens."""
    out, token = [], None
    for _ in range(200):
        f = {'from_block': {'block_number': n}, 'to_block': {'block_number': n}, 'keys': [[TRANSFER_SEL]],
             'chunk_size': EVENTS_CHUNK}
        if token:
            f['continuation_token'] = token
        r = c.call('starknet_getEvents', [f])
        out += r.get('events') or []
        token = r.get('continuation_token')
        if not token:
            break
    return out


def token_names(c, tokens):
    """{token: (symbol, decimals)} through starknet_call, tolerating contracts that answer neither."""
    if not tokens or SYMBOL_SEL is None:
        return {}
    calls = []
    for t in tokens:
        calls.append(('starknet_call', [{'contract_address': t, 'entry_point_selector': SYMBOL_SEL, 'calldata': []}, 'latest']))
        calls.append(('starknet_call', [{'contract_address': t, 'entry_point_selector': DECIMALS_SEL, 'calldata': []}, 'latest']))
    res = c.batch(calls)
    out = {}
    for i, t in enumerate(tokens):
        sym, dec = res[2 * i], res[2 * i + 1]
        s = decode_short_string(sym) if isinstance(sym, list) else None
        d = felt(dec[0]) if isinstance(dec, list) and dec else None
        out[t] = (re.sub(r'[^\x20-\x7e]', '', s)[:32] if s else None, d if d is not None and d <= 36 else None)
    return out


@register('starknet')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    c, notes = make_client(cfg, ctx)
    head = header(c, 'latest')
    head_n, head_ts = int(head['block_number']), int(head['timestamp'])
    back = header(c, max(0, head_n - 2000))
    rate = 2000 / max(1.0, head_ts - int(back['timestamp']))        # blocks per second
    end_ts = min(ctx.end_ts, head_ts)
    first = block_at(c, ctx.start_ts, head_n, head_ts, rate)
    last = head_n if end_ts >= head_ts else block_at(c, end_ts, head_n, head_ts, rate) - 1
    N = last - first + 1
    n_samples = int(p.get('samples') or ctx.samples)
    pts = sample_points(first, last, n_samples, seed=int(ctx.start_ts))

    heads = c.batch([('starknet_getBlockWithTxHashes', [{'block_number': x}]) for x in pts])
    errors = []

    def ev(n):
        try:
            return n, block_events(c, n), None
        except Exception as e:
            return n, None, str(e)[:120]

    with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 4))) as ex:
        evs = {n: (e, err) for n, e, err in ex.map(ev, pts)}
    units = []
    tok_count, tok_raw, tok_gross = {}, {}, {}
    for n, b in zip(pts, heads):
        if not isinstance(b, dict) or is_err(b) or 'transactions' not in b:
            errors.append('block %d: %s' % (n, str(b)[:80]))
            continue
        events, err = evs.get(n, (None, 'missing'))
        if events is None:
            errors.append('events %d: %s' % (n, err))
            continue
        i = len(units)
        sums = block_token_sums(events)
        units.append({'n': n, 'txs': len(b['transactions']), 'transfers': sum(v[0] for v in sums.values())})
        for tok, (cnt, net, gross) in sums.items():
            cl = tok_count.setdefault(tok, [])
            rl = tok_raw.setdefault(tok, [])
            gl = tok_gross.setdefault(tok, [])
            while len(cl) <= i:
                cl.append(0)
                rl.append(0)
                gl.append(0)
            cl[i] += cnt
            rl[i] += net
            gl[i] += gross
    n = len(units)
    txc, txse = stratified_total([u['txs'] for u in units], N)
    secs = max(1, end_ts - ctx.start_ts)

    key = ((cfg.get('ids') or {}).get('llama_key')) or 'starknet'
    tokens = sorted(tok_count, key=lambda a: -sum(tok_count[a]))
    pr = ctx.prices.get(['%s:%s' % (key, a) for a in tokens])
    meta, price_of, per_asset = {}, {}, {}
    unpriced = []
    for a in tokens:
        q = pr.get('%s:%s' % (key, a))
        if q and q.get('decimals') is not None:
            meta[a] = {'symbol': q.get('symbol'), 'decimals': int(q['decimals'])}
            price_of[a] = q.get('price')
        else:
            unpriced.append(a)
    # the feed prices some tokens without naming them (it answers symbol "-" for Endur's xSTRK), so those are named on
    # chain too; the price and decimals stay the feed's
    nameless = [a for a in tokens if a in price_of and (meta[a].get('symbol') or '-') in ('-', '')][:10]
    names = token_names(c, unpriced[:int(p.get('name_unpriced', 20))] + nameless) if not p.get('skip_names') else {}
    for a in unpriced:
        sym, dec = names.get(a, (None, None))
        meta[a] = {'symbol': sym, 'decimals': dec}
    for a in nameless:
        if names.get(a, (None, None))[0]:
            meta[a]['symbol'] = names[a][0]
    for a in tokens:
        dec = meta[a].get('decimals')
        scale = 10 ** int(dec) if isinstance(dec, int) else None
        per_asset[a] = {'count': tok_count[a], 'amount': [(x / scale) if scale else 0.0 for x in tok_raw[a]],
                        'gross': [(x / scale) if scale else 0.0 for x in tok_gross[a]]}
    tr = asset_rows(per_asset, n, N, meta, price_of, native_symbols=[(cfg.get('native') or {}).get('symbol') or 'STRK'])
    tr['method'] = 'sampled-blocks (Transfer events, both Cairo layouts, netted per transaction and token)'
    tr['transfer_events_per_block'] = (sum(u['transfers'] for u in units) / n) if n else None
    return {'tx': {'count': txc, 'se': txse, 'method': 'sampled-blocks', 'blocks': N, 'sampled': n,
                   'per_block': (txc / N) if txc is not None and N else None,
                   'tps': (txc / secs) if txc is not None else None,
                   'note': 'all transaction types (INVOKE, DEPLOY_ACCOUNT, DECLARE, L1_HANDLER), reverted included'},
            'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'head': head_n, 'blocks_per_second': rate},
            'endpoint': c.public_name(), 'calls': getattr(c, 'calls', None), 'notes': notes,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
