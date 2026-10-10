#!/usr/bin/env python3
"""Algorand: an exact transaction count from the block header's cumulative counter, and value from sampled blocks.

Counting. Every Algorand block header carries `tc` (TxnCounter): the number of transactions committed up to and
including that block, *inner transactions included* — checked live on 2026-10-09 by reading every block of one hour
(1,296 rounds): their top-level plus inner transactions summed to 64,786, exactly the counter's difference, and
tc(r) - tc(r-1) matched the block's own count in every round. So the count over a window is
tc(last) - tc(first - 1), exact for two header reads (`exact-counter`), and the counter itself is recorded so a daily
series can difference it between runs. Inner transactions are application-issued (a swap routed through a pool contract
emits them), which is why the sampled blocks also report the top-level count and the inner share. Algorand blocks hold
no failed transactions: a transaction that fails is never committed.

Value. For a stratified sample of rounds the full block is read (`format=json`, ~10 kB) and every transaction is
walked, inner ones recursively, as (from, to, amount) moves: `pay` moves `amt` microAlgos and a close-out its closing
amount (`ca`) to `close`; `axfer` moves `aamt` raw units of asset `xaid` (from `asnd` on a clawback) and an asset
close-out its `aca` to `aclose`. A zero-amount `axfer` is an opt-in and moves nothing. The headline is net per atomic
group (`grp`; an ungrouped transaction is its own group), the repo-wide convention: a swap is a group — the user pays
the pool, the pool's inner transaction pays the user — and each asset counts what its receivers gained net, so a
group that moves an asset out and back (an arbitrage round trip, a flash loan repaid in the same group) counts only
what stayed moved. `gross` keeps every move as stated for comparison.

Pricing. ALGO through the feed's coingecko id; ASAs through DefiLlama's `algorand:<asset id>` key, which also supplies
decimals. Circle's USDC (31566704) and Tether's USDt (312769) fall back to par only if the feed is silent and the
indexer confirms the asset's creator is the issuer's known account; the row then says so.
"""
import collections
import concurrent.futures as cf
import time
import urllib.parse

from chain_adapters import Http, asset_rows, net_positive, register, sample_points, stratified_total, window_dict

ALGOD = 'https://mainnet-api.algonode.cloud'
INDEXER = 'https://mainnet-idx.algonode.cloud'
MICROALGOS = 1_000_000
SECONDS_PER_ROUND_SEED = 2.8   # seeds the bracket only
MAX_SAMPLES = 300              # a block is ~10 kB
NAME_UNPRICED = 25
CANONICAL_PAR = {
    # asset id -> (symbol, creator). Checked 2026-10-09 against the indexer (and DefiLlama prices both at ~$1).
    '31566704': ('USDC', '2UEQTE5QDNXPI7M3TU44G6SYKLFWLPQO7EBZM7K7MHMQQMFI4QJPLHQFHM'),
    '312769': ('USDt', 'XIU7HGGAJ3QOTATPDSIIHPFVKMICXKHMOR2FJKHTVLII4FAOA3CYZQDLG4'),
}


def locate(target, lo_bound, head, head_ts, seconds_per_unit, ts_of):
    """First index in [lo_bound, head] whose time is >= target (head when none earlier), for a non-decreasing ts_of."""
    guess = int(head - (head_ts - target) / seconds_per_unit)
    lo = min(head, max(lo_bound, guess - 600))
    hi = max(lo_bound, min(head, guess + 600))
    step = 1200
    while lo > lo_bound and ts_of(lo) >= target:
        lo, step = max(lo_bound, lo - step), step * 2
    step = 1200
    while hi < head and ts_of(hi) < target:
        hi, step = min(head, hi + step), step * 2
    while lo < hi:
        mid = (lo + hi) // 2
        if ts_of(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def walk(stxn, acc, moves, depth=0):
    """Fold one SignedTxnInBlock (or inner SignedTxnWithAD) and its inner transactions into `acc`, appending its value
    moves as (asset, from, to, amount) to `moves`."""
    txn = stxn.get('txn') or {}
    ty = txn.get('type') or '?'
    acc['types'][ty] += 1
    acc['n'] += 1
    if depth:
        acc['inner'] += 1

    def add(asset, frm, to, amount):
        if amount and int(amount) > 0:
            moves.append((asset, frm, to, int(amount)))

    if ty == 'pay':
        add('native:ALGO', txn.get('snd'), txn.get('rcv'), txn.get('amt'))
        add('native:ALGO', txn.get('snd'), txn.get('close'), stxn.get('ca'))
    elif ty == 'axfer' and txn.get('xaid') is not None:
        a = str(int(txn['xaid']))
        src = txn.get('asnd') or txn.get('snd')
        add(a, src, txn.get('arcv'), txn.get('aamt'))
        add(a, src, txn.get('aclose'), stxn.get('aca'))
    for it in ((stxn.get('dt') or {}).get('itx') or []):
        walk(it, acc, moves, depth + 1)
    return acc


def net_by_asset(moves):
    """{asset: (sum of positive net changes, gross sum)} over one group's moves (asset, from, to, amount)."""
    by = {}
    for a, frm, to, v in moves:
        by.setdefault(a, []).append((frm, to, v))
    out = {}
    for a, mv in by.items():
        out[a] = (net_positive(mv), sum(v for _, _, v in mv))
    return out


def reduce_block(b):
    acc = {'types': collections.Counter(), 'n': 0, 'inner': 0, 'assets': {}}
    groups = {}
    for i, t in enumerate(b.get('txns') or []):
        key = (t.get('txn') or {}).get('grp') or ('solo', i)
        walk(t, acc, groups.setdefault(key, []))
    for moves in groups.values():
        for a, (net, gross) in net_by_asset(moves).items():
            e = acc['assets'].setdefault(a, [0, 0, 0])
            if net > 0:
                e[0] += 1
                e[1] += net
            e[2] += gross
    acc['top'] = acc['n'] - acc['inner']
    acc['ts'] = int(b.get('ts') or 0)
    acc['groups'] = len(groups)
    return acc


def window_count(tc_last, tc_before_first):
    """Transactions committed in rounds first..last, from the counters at last and at first - 1."""
    return int(tc_last) - int(tc_before_first)


@register('algorand')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    algod = (p.get('algod') or ALGOD).rstrip('/')
    indexer = (p.get('indexer') or INDEXER).rstrip('/')
    http = Http(min_interval=p.get('min_interval', 0.04), timeout=p.get('timeout', 45))
    errors = []
    headers = {}

    def header(r):
        if r not in headers:
            headers[r] = http.get('%s/v2/blocks/%d?format=json&header-only=true' % (algod, r))['block']
        return headers[r]

    head = int(http.get(algod + '/v2/status')['last-round'])
    head_ts = int(header(head)['ts'])
    end_ts = min(ctx.end_ts, head_ts)

    def ts_of(r):
        return int(header(r)['ts'])

    first = locate(ctx.start_ts, 1, head, head_ts, SECONDS_PER_ROUND_SEED, ts_of)
    last = head if end_ts >= head_ts else locate(end_ts, first, head, head_ts, SECONDS_PER_ROUND_SEED, ts_of) - 1
    N = last - first + 1
    tc_last, tc_prev = int(header(last)['tc']), int(header(first - 1)['tc'])
    count = window_count(tc_last, tc_prev)
    secs = max(1, end_ts - ctx.start_ts)

    n_samples = min(int(p.get('samples') or ctx.samples), MAX_SAMPLES)
    pts = sample_points(first, last, n_samples, seed=int(ctx.start_ts))

    def block(r):
        try:
            return r, reduce_block(http.get('%s/v2/blocks/%d?format=json' % (algod, r))['block'])
        except Exception as e:
            return r, {'error': str(e)[:160]}

    with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 6))) as ex:
        got = list(ex.map(block, pts))
    units = [u for _, u in got if 'error' not in u]
    errors += ['round %d: %s' % (r, u['error']) for r, u in got if 'error' in u]
    n = len(units)
    est_all, est_se = stratified_total([u['n'] for u in units], N)
    est_top, _ = stratified_total([u['top'] for u in units], N)
    types = collections.Counter()
    for u in units:
        types.update(u['types'])
    tot = sum(types.values())
    tx = {'count': count, 'se': 0.0, 'method': 'exact-counter', 'cumulative_total': tc_last, 'includes_inner': True,
          'top_level_est': est_top, 'from_blocks': est_all, 'from_blocks_se': est_se,
          'inner_share': (sum(u['inner'] for u in units) / tot) if tot else None,
          'type_share': {k: round(v / tot, 4) for k, v in types.most_common(10)} if tot else {},
          'unit': 'round', 'blocks': N, 'sampled': n, 'tps': count / secs,
          'note': 'TxnCounter difference across the window: every committed transaction, inner (application-issued) '
                  'ones included; Algorand commits no failed transactions'}

    # ------------------------------------------------------------------ price
    per_asset = {}
    for i, u in enumerate(units):
        for a, (c, raw, graw) in u['assets'].items():
            d = per_asset.setdefault(a, {'count': [0] * n, 'raw': [0] * n, 'graw': [0] * n})
            d['count'][i] += c
            d['raw'][i] += raw
            d['graw'][i] += graw
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'algorand')
    asas = [a for a in per_asset if a != 'native:ALGO']
    pr = ctx.prices.get([nat_key] + ['algorand:%s' % a for a in asas])
    meta, price_of, source, scale = {}, {}, {}, {}
    q = pr.get(nat_key)
    meta['native:ALGO'] = {'symbol': 'ALGO', 'decimals': 6}
    price_of['native:ALGO'], source['native:ALGO'] = (q.get('price'), 'defillama') if q else (None, None)
    scale['native:ALGO'] = MICROALGOS
    unpriced = []
    for a in asas:
        q = pr.get('algorand:%s' % a)
        if q and q.get('decimals') is not None:
            meta[a] = {'symbol': q.get('symbol'), 'decimals': int(q['decimals'])}
            price_of[a], source[a] = q.get('price'), 'defillama'
            scale[a] = 10 ** int(q['decimals'])
        else:
            unpriced.append(a)
    unpriced.sort(key=lambda a: -sum(per_asset[a]['count']))
    for a in unpriced[:NAME_UNPRICED] + [x for x in unpriced if x in CANONICAL_PAR]:
        if a in meta:
            continue
        try:
            prm = http.get('%s/v2/assets/%d' % (indexer, int(a)))['asset']['params']
            meta[a] = {'symbol': prm.get('unit-name'), 'decimals': int(prm.get('decimals') or 0)}
            scale[a] = 10 ** int(prm.get('decimals') or 0)
            if a in CANONICAL_PAR and prm.get('creator') == CANONICAL_PAR[a][1]:
                price_of[a], source[a] = 1.0, 'par-canonical-issuer'
        except Exception as e:
            errors.append('asset %s: %s' % (a, str(e)[:80]))
    pa = {}
    for a, d in per_asset.items():
        sc = scale.get(a)
        pa[a] = {'count': d['count'], 'amount': [(x / sc) if sc else 0.0 for x in d['raw']],
                 'gross': [(x / sc) if sc else 0.0 for x in d['graw']]}
        meta.setdefault(a, {'symbol': None, 'decimals': None})
        price_of.setdefault(a, None)
    tr = asset_rows(pa, n, N, meta, price_of, native_symbols=['ALGO'])
    for r in tr['assets'] + tr['unpriced_top']:
        r['price_source'] = source.get(r['asset'])
        if r['asset'] != 'native:ALGO' and scale.get(r['asset']) is None:
            r['note'] = 'decimals unknown: amount not scaled'
    tr['method'] = ('sampled-blocks (net per atomic group: pay, axfer and close-outs, inner transactions included; '
                    'opt-ins move nothing)')
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'head': head},
            'endpoint': urllib.parse.urlsplit(algod).netloc, 'calls': http.requests,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
