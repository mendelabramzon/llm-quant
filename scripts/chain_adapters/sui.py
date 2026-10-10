#!/usr/bin/env python3
"""Sui: an exact transaction count from the checkpoint counter, the user share and the transfer value from a stratified
sample of checkpoints, all over GraphQL (the public JSON-RPC on Mysten's fullnodes is deprecated and answers
"Method not found").

Counting. Every checkpoint carries `networkTotalTransactions`, the chain's cumulative count, so the number of
transactions in a window is one subtraction between the first checkpoint at or after its start and the last one before
its end — exact, and including the protocol's own transactions. Those are not activity: consensus-commit prologues,
randomness updates and `ProgrammableSystemTransaction`s (accumulator settlements) were ~39% of all transactions on
2026-10-09 and carry no positive balance change. So the headline count is user (`ProgrammableTransaction`) transactions,
estimated as the exact total times the user share measured in the sampled checkpoints (a ratio estimator with its own
standard error), and the exact all-kinds total is kept beside it. The same counter is read a second time from an
independent provider's JSON-RPC (`crosscheck`), and the sample's own transaction listing gives a third, so a decode or
window error shows up as a disagreement rather than as a number.

Value. In each sampled checkpoint, every successful user transaction's `balanceChanges` are read and the positive
amounts summed per coin type. Sui reports a balance change already netted per owner and coin within the transaction,
so this *is* the `chain_adapters.net_positive` convention without further work: a transfer counts once, a swap counts
both legs, a pool used as a hop counts the input it kept, and coins that pass through an owner and leave in the same
transaction count nothing. No gross figure exists at this level, so none is reported. Coin types are priced through
DefiLlama as `sui:<type>`.

GraphQL limits that shape the code (`serviceConfig`, 2026-10-09): pages of at most 50, multi-gets of at most 200 keys,
and at most 21 connection reads that need the backing store per request — so checkpoints are fetched 20 at a time.
"""
import concurrent.futures as cf
import datetime as dt
import time

from chain_adapters import (Http, HttpError, RpcError, asset_rows, register, sample_points, stratified_total,
                            window_dict)
from chain_adapters._search import kary_first_at, ratio_estimate, seeded_bracket

GRAPHQL = 'https://graphql.mainnet.sui.io/graphql'
CROSSCHECK_RPC = ['https://rpc-mainnet.suiscan.xyz', 'https://sui-mainnet.nodeinfra.com', 'https://sui-rpc.publicnode.com']
USER_KINDS = {'ProgrammableTransaction'}
PAGE = 50                 # serviceConfig.maxPageSize
MULTIGET = 200            # serviceConfig.maxMultiGetSize
STORE_READS = 20          # one below the per-request cap of 21 backing-store connection reads
SEARCH_FANOUT = 100       # checkpoints read per round of the k-ary timestamp search

TX_FIELDS = ('pageInfo { hasNextPage endCursor } nodes { digest kind { __typename } effects { status '
             'balanceChanges(first: %d) { pageInfo { hasNextPage endCursor } nodes { coinType { repr } amount } } } }' % PAGE)
Q_HEADERS = 'query($k: [UInt53!]!) { multiGetCheckpoints(keys: $k) { sequenceNumber timestamp networkTotalTransactions } }'
Q_CHECKPOINTS = ('query($k: [UInt53!]!) { multiGetCheckpoints(keys: $k) { sequenceNumber timestamp networkTotalTransactions '
                 'transactions(first: %d) { %s } } }' % (PAGE, TX_FIELDS))


def parse_ts(iso):
    """'2026-10-09T14:41:37.337Z' -> unix seconds (float)."""
    return dt.datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp()


class Gql:
    def __init__(self, url, http):
        self.url, self.http = url, http
        self.requests = 0

    def q(self, query, variables=None):
        last = None
        for attempt in range(4):
            d = self.http.post(self.url, {'query': query, 'variables': variables or {}})
            self.requests += 1
            if d.get('errors'):
                msg = str(d['errors'])[:400]
                last = RpcError({'message': msg})
                if 'RESOURCE_EXHAUSTED' in msg or 'timeout' in msg.lower() or 'rate' in msg.lower():
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise last
            return d['data']
        raise last


def headers(g, seqs):
    """{seq: (unix ts, networkTotalTransactions)} for the given checkpoint sequence numbers."""
    out = {}
    seqs = sorted(set(int(s) for s in seqs))
    for i in range(0, len(seqs), MULTIGET):
        for c in g.q(Q_HEADERS, {'k': seqs[i:i + MULTIGET]})['multiGetCheckpoints'] or []:
            if c:
                out[int(c['sequenceNumber'])] = (parse_ts(c['timestamp']), int(c['networkTotalTransactions']))
    return out


def checkpoint_at(g, ts, head_seq, head_ts, rate):
    """First checkpoint whose timestamp is >= ts: a rate-seeded bracket, then a k-ary search over multi-gets."""
    def read(xs):
        return {x: v[0] for x, v in headers(g, xs).items()}
    lo, hi = seeded_bracket(lambda x: read([x]).get(x), ts, head_seq, head_ts, rate)
    return kary_first_at(read, lo, hi, ts, fanout=SEARCH_FANOUT)


def fetch_checkpoints(g, seqs):
    """{seq: [transaction nodes]} with every transaction page and every balance-change page followed to the end."""
    out = {}
    pending = []          # (seq, cursor) of checkpoints with more transaction pages
    for i in range(0, len(seqs), STORE_READS):
        part = seqs[i:i + STORE_READS]
        for c in g.q(Q_CHECKPOINTS, {'k': part})['multiGetCheckpoints'] or []:
            if not c:
                continue
            s = int(c['sequenceNumber'])
            conn = c['transactions'] or {}
            out[s] = list(conn.get('nodes') or [])
            pi = conn.get('pageInfo') or {}
            if pi.get('hasNextPage'):
                pending.append((s, pi.get('endCursor')))
    while pending:
        part, pending = pending[:STORE_READS], pending[STORE_READS:]
        q = 'query { %s }' % ' '.join(
            'a%d: checkpoint(sequenceNumber: %d) { transactions(first: %d, after: "%s") { %s } }' % (j, s, PAGE, cur, TX_FIELDS)
            for j, (s, cur) in enumerate(part))
        d = g.q(q)
        for j, (s, _) in enumerate(part):
            conn = ((d.get('a%d' % j) or {}).get('transactions')) or {}
            out[s] += list(conn.get('nodes') or [])
            pi = conn.get('pageInfo') or {}
            if pi.get('hasNextPage'):
                pending.append((s, pi.get('endCursor')))
    # balance changes beyond the first page (large multi-recipient transactions)
    more = [(t['digest'], t['effects']['balanceChanges']['pageInfo'].get('endCursor'))
            for txs in out.values() for t in txs
            if (((t.get('effects') or {}).get('balanceChanges') or {}).get('pageInfo') or {}).get('hasNextPage')]
    by_digest = {t['digest']: t for txs in out.values() for t in txs}
    while more:
        part, more = more[:STORE_READS], more[STORE_READS:]
        q = 'query { %s }' % ' '.join(
            'a%d: transaction(digest: "%s") { effects { balanceChanges(first: %d, after: "%s") { pageInfo { hasNextPage endCursor } '
            'nodes { coinType { repr } amount } } } }' % (j, dg, PAGE, cur) for j, (dg, cur) in enumerate(part))
        d = g.q(q)
        for j, (dg, _) in enumerate(part):
            conn = ((((d.get('a%d' % j) or {}).get('effects')) or {}).get('balanceChanges')) or {}
            by_digest[dg]['effects']['balanceChanges']['nodes'] += list(conn.get('nodes') or [])
            pi = conn.get('pageInfo') or {}
            if pi.get('hasNextPage'):
                more.append((dg, pi.get('endCursor')))
    return out


def reduce_checkpoint(txs):
    """Counts by kind and, over successful user transactions, the positive balance change per coin type."""
    n_user = n_fail = 0
    coins = {}
    for t in txs:
        kind = ((t.get('kind') or {}).get('__typename')) or '?'
        if kind not in USER_KINDS:
            continue
        n_user += 1
        eff = t.get('effects') or {}
        if eff.get('status') != 'SUCCESS':
            n_fail += 1
            continue
        for b in ((eff.get('balanceChanges') or {}).get('nodes') or []):
            amt = int(b.get('amount') or 0)
            if amt > 0:
                ct = ((b.get('coinType') or {}).get('repr')) or '?'
                e = coins.setdefault(ct, [0, 0])
                e[0] += 1
                e[1] += amt
    return {'n_all': len(txs), 'n_user': n_user, 'n_fail': n_fail, 'coins': coins}


def rpc_total(http, url, seq):
    d = http.post(url, {'jsonrpc': '2.0', 'id': 1, 'method': 'sui_getCheckpoint', 'params': [str(seq)]})
    res = (d or {}).get('result') or {}
    v = res.get('networkTotalTransactions')
    return int(v) if v is not None else None


def coin_metadata(g, types):
    """{coin type: (symbol, decimals)} for unpriced coins, so the table can still say what they are."""
    out = {}
    for i in range(0, len(types), STORE_READS):
        part = types[i:i + STORE_READS]
        q = 'query { %s }' % ' '.join('a%d: coinMetadata(coinType: "%s") { symbol decimals }' % (j, t) for j, t in enumerate(part))
        try:
            d = g.q(q)
        except Exception:
            continue
        for j, t in enumerate(part):
            m = d.get('a%d' % j) or {}
            if m:
                out[t] = (m.get('symbol'), m.get('decimals'))
    return out


@register('sui')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    http = Http(min_interval=p.get('min_interval', 0.05), timeout=p.get('timeout', 60))
    g = Gql(p.get('graphql') or GRAPHQL, http)
    notes, errors = [], []

    head = g.q('{ checkpoint { sequenceNumber timestamp networkTotalTransactions } }')['checkpoint']
    head_seq, head_ts = int(head['sequenceNumber']), parse_ts(head['timestamp'])
    back = headers(g, [head_seq - 20000])
    rate = 20000 / max(1.0, head_ts - back[head_seq - 20000][0]) if back else 4.0
    end_ts = min(ctx.end_ts, head_ts)
    first = checkpoint_at(g, ctx.start_ts, head_seq, head_ts, rate)
    last = head_seq if end_ts >= head_ts else checkpoint_at(g, end_ts, head_seq, head_ts, rate) - 1
    bounds = headers(g, [first - 1, first, last])
    total_all = bounds[last][1] - bounds[first - 1][1]
    N = last - first + 1

    # ------------------------------------------------------------------ the same counter, from another provider
    cross = {}
    for url in p.get('crosscheck_rpc') or CROSSCHECK_RPC:
        try:
            a, b = rpc_total(http, url, first - 1), rpc_total(http, url, last)
            if a is not None and b is not None:
                cross = {'endpoint': url.split('/')[2], 'all_kinds': b - a, 'matches': (b - a) == total_all}
                break
        except (HttpError, RpcError, ValueError) as e:
            notes.append('crosscheck %s: %s' % (url.split('/')[2], str(e)[:80]))

    # ------------------------------------------------------------------ the sample
    n_samples = int(p.get('samples') or ctx.samples)
    seqs = sample_points(first, last, n_samples, seed=int(ctx.start_ts))
    chunks = [seqs[i:i + STORE_READS] for i in range(0, len(seqs), STORE_READS)]

    def get(part):
        try:
            return fetch_checkpoints(g, part), None
        except Exception as e:
            return {}, '%s..%s: %s' % (part[0], part[-1], str(e)[:120])

    fetched = {}
    with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 4))) as ex:
        for got, err in ex.map(get, chunks):
            fetched.update(got)
            if err:
                errors.append(err)
    units = [reduce_checkpoint(fetched[s]) for s in seqs if s in fetched]
    n = len(units)
    user, user_se = ratio_estimate([u['n_user'] for u in units], [u['n_all'] for u in units], total_all, N)
    listed_all, listed_se = stratified_total([u['n_all'] for u in units], N)
    n_user_s = sum(u['n_user'] for u in units)
    tx = {'count': user, 'se': user_se, 'method': 'exact-counter x sampled user share',
          'all_kinds': total_all, 'all_kinds_method': 'exact-counter', 'cumulative_total': bounds[last][1],
          'user_share': (n_user_s / sum(u['n_all'] for u in units)) if units else None,
          'failed_share': (sum(u['n_fail'] for u in units) / n_user_s) if n_user_s else None,
          'listed_all_kinds': listed_all, 'listed_all_kinds_se': listed_se,
          'checkpoints': N, 'sampled': n, 'crosscheck': cross or None,
          'note': 'user = ProgrammableTransaction; consensus prologues, randomness updates and system transactions '
                  'are in all_kinds only'}

    # ------------------------------------------------------------------ price and scale
    per_asset, raw = {}, {}
    for i, u in enumerate(units):
        for ct, (cnt, amt) in u['coins'].items():
            d = raw.setdefault(ct, {'count': [0] * n, 'raw': [0] * n})
            d['count'][i] += cnt
            d['raw'][i] += amt
    nat_cg = (cfg.get('native') or {}).get('coingecko')
    key = ((cfg.get('ids') or {}).get('llama_key')) or 'sui'
    pr = ctx.prices.get(['%s:%s' % (key, ct) for ct in raw] + (['coingecko:%s' % nat_cg] if nat_cg else []))
    meta, price_of = {}, {}
    unnamed = []
    for ct, d in raw.items():
        q = pr.get('%s:%s' % (key, ct))
        if q and q.get('decimals') is not None:
            meta[ct] = {'symbol': q.get('symbol'), 'decimals': int(q['decimals'])}
            price_of[ct] = q.get('price')
        else:
            unnamed.append(ct)
    unnamed.sort(key=lambda ct: -sum(raw[ct]['count']))
    names = coin_metadata(g, unnamed[:int(p.get('name_unpriced', 25))]) if unnamed else {}
    for ct in unnamed:
        sym, dec = names.get(ct, (ct.split('::')[-1] if '::' in ct else None, None))
        meta[ct] = {'symbol': sym, 'decimals': dec}
    for ct, d in raw.items():
        dec = meta[ct].get('decimals')
        scale = 10 ** int(dec) if isinstance(dec, int) and 0 <= dec <= 36 else None
        per_asset[ct] = {'count': d['count'], 'amount': [(x / scale) if scale else 0.0 for x in d['raw']]}
    tr = asset_rows(per_asset, n, N, meta, price_of, native_symbols=[(cfg.get('native') or {}).get('symbol') or 'SUI'])
    tr['method'] = 'sampled-checkpoints (positive balance changes of successful user transactions)'
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first_checkpoint': first, 'last_checkpoint': last, 'head_checkpoint': head_seq,
                       'checkpoints_per_second': rate},
            'endpoint': (p.get('graphql') or GRAPHQL).split('/')[2], 'calls': g.requests, 'notes': notes,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
