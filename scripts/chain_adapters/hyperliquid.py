#!/usr/bin/env python3
"""Hyperliquid's HyperCore: traded (not transferred) volume per market from the info API, and the chain's action count
from a stratified sample of explorer blocks. HyperEVM is a separate registry entry read by the EVM adapter.

Value. HyperCore is a venue, so the asset table is *traded notional*, not transfers: every perp market of the first-party
dex and of every HIP-3 dex (`perpDexs` lists them; `metaAndAssetCtxs` takes the dex name), every spot pair
(`spotMetaAndAssetCtxs`), and the outcome (prediction) markets — spot coins named `#<id>` priced in [0, 1] — folded
into one row because there are hundreds of them and together they traded under $1M on 2026-10-09. `usd` is the
venue's own `dayNtlVlm`: a rolling 24 hours at query time, whatever the probe window is (`window_note` says so). Spot
volume is in quote units; a stable quote counts at par and any other quote is converted through its own USDC pair.
Open interest (`openInterest * markPx`) and the hourly funding rate ride along on each perp row, because the
interesting things on this venue so far (research/2026-09-10/perps_*) were funding, not volume.

Counting. The explorer (`rpc.hyperliquid.xyz/explorer`, `{'type': 'blockDetails', 'height': h}`) returns a block's
`numTxs`, its time and every action in it. There is no head call, so the window's first and last heights are found by
interpolation search on `blockTime` (blocks come at a near-constant ~14 a second, so it converges in a handful of
reads; a height past the head answers "invalid block height"), and ~50 blocks are read across the window. The count is
of HyperCore *actions* — orders, cancels, modifies, EVM raw transactions, transfers — and the action-type mix of the
sample is reported, because on an exchange chain "transactions" are mostly order-book messages.
"""
import collections
import concurrent.futures as cf
import time

from chain_adapters import (Http, HttpError, USD_STABLES, asset_class, asset_rows, register, sample_points,
                            stratified_total, window_dict)

INFO = 'https://api.hyperliquid.xyz/info'
EXPLORER = 'https://rpc.hyperliquid.xyz/explorer'
ANCHOR_HEIGHT = 1_000_000_000      # a height that exists (2026-05-17); only where the height search starts
DEFAULT_RATE = 14.3                # blocks/s measured 2026-05..08; seeds the search, then measured rate replaces it
TIME_TOLERANCE_MS = 1500           # ~20 blocks: plenty for a window of a million blocks
MAX_SAMPLES = 80                   # blocks are heavy-tailed (0 to 8k actions); 80 x ~1 MB is ~1 min


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def perp_rows(dex, meta, ctxs):
    """One row per perp market: (asset id, symbol, notional, base volume, mark, OI usd, funding, premium)."""
    out = []
    for u, c in zip(meta.get('universe') or [], ctxs or []):
        coin = u.get('name')
        vol = fnum(c.get('dayNtlVlm'))
        if u.get('isDelisted') and not vol:
            continue
        mark = fnum(c.get('markPx'))
        out.append({'asset': 'perp:%s' % coin, 'symbol': coin, 'dex': dex or 'main', 'kind': 'perp', 'usd': vol,
                    'base': fnum(c.get('dayBaseVlm')), 'mark': mark, 'oi_usd': fnum(c.get('openInterest')) * mark,
                    'funding': fnum(c.get('funding')), 'premium': c.get('premium'), 'oracle': fnum(c.get('oraclePx'))})
    return out


def spot_rows(spot_meta, ctxs):
    """Spot pairs priced in USD, plus one aggregate row for the outcome markets."""
    tokens = {t['index']: t for t in spot_meta.get('tokens') or []}
    pairs_by_name = {u['name']: u for u in spot_meta.get('universe') or []}
    pairs_by_index = {u['index']: u for u in spot_meta.get('universe') or []}

    def pair_of(coin):
        if coin in pairs_by_name:
            return pairs_by_name[coin]
        if coin.startswith('@') and coin[1:].isdigit():
            return pairs_by_index.get(int(coin[1:]))
        return None

    def names(u):
        b, q = (u.get('tokens') or [None, None])[:2]
        return (tokens.get(b) or {}).get('name'), (tokens.get(q) or {}).get('name')

    # quote conversion: a non-stable quote is priced through its own <quote>/USDC pair
    quote_usd = {}
    for c in ctxs or []:
        u = pair_of(c.get('coin') or '')
        if u:
            b, q = names(u)
            if q == 'USDC' and b:
                quote_usd[b] = fnum(c.get('markPx'))
    rows, outcome = [], {'usd': 0.0, 'markets': 0, 'traded': 0, 'top': []}
    for c in ctxs or []:
        coin = c.get('coin') or ''
        vol = fnum(c.get('dayNtlVlm'))
        if coin.startswith('#'):
            outcome['markets'] += 1
            outcome['usd'] += vol
            if vol:
                outcome['traded'] += 1
                outcome['top'].append((vol, coin))
            continue
        u = pair_of(coin)
        if not u:
            continue
        b, q = names(u)
        if q is None:
            continue
        if q.upper() in USD_STABLES:
            px = 1.0
        else:
            px = quote_usd.get(q)
        if not vol:
            continue
        rows.append({'asset': 'spot:%s/%s' % (b, q), 'symbol': b, 'kind': 'spot', 'quote': q, 'coin': coin,
                     'usd': vol * px if px else None, 'quote_volume': vol, 'base': fnum(c.get('dayBaseVlm')),
                     'mark': fnum(c.get('markPx'))})
    outcome['top'] = [coin for _, coin in sorted(outcome['top'], reverse=True)[:5]]
    return rows, outcome


def height_at(get_time, ts_ms, anchor=ANCHOR_HEIGHT, rate=DEFAULT_RATE, tol_ms=TIME_TOLERANCE_MS, max_steps=48):
    """A height whose blockTime is within tol_ms of ts_ms (the head, if ts_ms is past it), by interpolation search.

    get_time(h) -> blockTime in ms, or None for a height past the head. Returns (height, time_ms, reads).
    """
    reads = 0
    t = get_time(anchor)
    reads += 1
    while t is None or t > ts_ms:                 # the anchor is in the future of ts (or past the head): step back
        anchor = max(1, anchor // 2)
        t = get_time(anchor)
        reads += 1
        if anchor == 1:
            break
    lo, hi, inv = (anchor, t), None, None          # lo.time <= ts < hi.time; inv: smallest height known past the head
    for _ in range(max_steps):
        if abs(lo[1] - ts_ms) <= tol_ms:
            return lo[0], lo[1], reads
        if hi is not None:
            if hi[0] - lo[0] <= 1:
                return hi[0], hi[1], reads
            g = lo[0] + int((ts_ms - lo[1]) * (hi[0] - lo[0]) / max(1, hi[1] - lo[1]))
            g = min(max(g, lo[0] + 1), hi[0] - 1)
        else:
            g = lo[0] + max(1, int((ts_ms - lo[1]) / 1000.0 * rate))
            if inv is not None:
                if inv - lo[0] <= 1:
                    return lo[0], lo[1], reads   # ts is past the head: the head is the answer
                if g >= inv:
                    g = (lo[0] + inv) // 2
        tg = get_time(g)
        reads += 1
        if tg is None:
            inv = g if inv is None else min(inv, g)
            continue
        if tg <= ts_ms:
            if lo[1] < tg:
                rate = max(rate * 0.2, min(rate * 5, (g - lo[0]) / max(1e-3, (tg - lo[1]) / 1000.0)))
            lo = (g, tg)
        else:
            hi = (g, tg)
            if abs(tg - ts_ms) <= tol_ms:
                return g, tg, reads
    return (hi or lo)[0], (hi or lo)[1], reads


@register('hyperliquid')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    info = p.get('info') or INFO
    explorer = p.get('explorer') or EXPLORER
    http = Http(min_interval=float(p.get('min_interval', 0.12)), timeout=60)
    errors, notes = [], []

    # ------------------------------------------------------------------ venue: every perp dex and the spot book
    rows = []
    try:
        dexes = [(d or {}).get('name') or '' for d in http.post(info, {'type': 'perpDexs'}) or [None]]
    except HttpError as e:
        dexes = ['']
        errors.append('perpDexs: %s' % str(e)[:100])
    for dex in dexes:
        try:
            m = http.post(info, {'type': 'metaAndAssetCtxs', 'dex': dex})
            rows += perp_rows(dex, m[0], m[1])
        except (HttpError, IndexError, KeyError, TypeError) as e:
            errors.append('metaAndAssetCtxs %s: %s' % (dex or 'main', str(e)[:100]))
    outcome = None
    try:
        s = http.post(info, {'type': 'spotMetaAndAssetCtxs'})
        srows, outcome = spot_rows(s[0], s[1])
        rows += srows
    except (HttpError, IndexError, KeyError, TypeError) as e:
        errors.append('spotMetaAndAssetCtxs: %s' % str(e)[:100])
    if outcome and outcome['markets']:
        rows.append({'asset': 'outcome:all', 'symbol': 'OUTCOMES', 'kind': 'outcome', 'usd': outcome['usd'],
                     'markets': outcome['markets'], 'traded_markets': outcome['traded'], 'top': outcome['top']})
    native = (cfg.get('native') or {}).get('symbol') or 'HYPE'
    per_asset, meta, price_of, extra = {}, {}, {}, {}
    for r in rows:
        if r['usd'] is None:
            continue
        a = r['asset']
        base_sym = r['symbol'].split(':')[-1]
        per_asset[a] = {'count': [0], 'amount': [r['usd']]}
        meta[a] = {'symbol': r['symbol'], 'decimals': None}
        price_of[a] = 1.0                      # amount is already USD notional; the real mark is restored below
        extra[a] = r
        extra[a]['base_sym'] = base_sym
    tr = asset_rows(per_asset, 1, 1, meta, price_of, native_symbols=[native])
    for r in tr['assets']:
        e = extra[r['asset']]
        r['class'] = asset_class(e['base_sym'], [native])
        r.update({'kind': e['kind'], 'transfers': None, 'transfers_se': None, 'top_block_share': None,
                  'price': e.get('mark'), 'amount': e.get('base')})
        for k in ('dex', 'oi_usd', 'funding', 'premium', 'oracle', 'quote', 'quote_volume', 'markets',
                  'traded_markets', 'top'):
            if k in e:
                r[k] = e[k]
    by_class = collections.Counter()
    for r in tr['assets']:
        by_class[r['class']] += r['usd'] or 0.0
    tr['usd_by_class'] = dict(by_class)
    tr['usd_by_kind'] = dict(collections.Counter({k: sum(r['usd'] or 0 for r in tr['assets'] if r['kind'] == k)
                                                  for k in ('perp', 'spot', 'outcome')}))
    tr['usd_by_dex'] = dict(collections.Counter({d or 'main': sum(r['usd'] or 0 for r in tr['assets']
                                                                 if r.get('dex') == (d or 'main')) for d in dexes}))
    tr['open_interest_usd'] = sum(r.get('oi_usd') or 0 for r in tr['assets'])
    tr['unpriced_spot_pairs'] = sum(1 for r in rows if r['usd'] is None)
    tr['method'] = 'venue-24h-notional (info API dayNtlVlm)'
    tr['window_note'] = 'traded notional over the venue\'s rolling 24 h at query time, not the probe window'

    # ------------------------------------------------------------------ actions: explorer block sample
    tx = {'count': None, 'se': None, 'method': 'unavailable'}
    try:
        def block(h):
            d = http.post(explorer, {'type': 'blockDetails', 'height': int(h)})
            if not isinstance(d, dict) or d.get('type') == 'error':
                return None
            return d.get('blockDetails')

        cache = {}

        def bt(h):
            if h not in cache:
                b = block(h)
                cache[h] = b['blockTime'] if b else None
            return cache[h]

        end_ms = ctx.end_ts * 1000
        h_end, t_end, r1 = height_at(bt, end_ms)
        h_start, t_start, r2 = height_at(bt, ctx.start_ts * 1000, anchor=max(1, h_end - int((ctx.end_ts - ctx.start_ts) * DEFAULT_RATE)))
        N = h_end - h_start + 1
        n = min(int(p.get('samples') or ctx.samples), MAX_SAMPLES)
        hs = sample_points(h_start, h_end, n, seed=int(ctx.start_ts))
        with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 3))) as ex:
            blocks = list(ex.map(lambda h: (h, block(h)), hs))
        got = [b for _, b in blocks if b]
        counts = [b.get('numTxs') or len(b.get('txs') or []) for b in got]
        total, se = stratified_total(counts, N)
        mix, failed, listed, users = collections.Counter(), 0, 0, set()
        for b in got:
            for t in b.get('txs') or []:
                mix[(t.get('action') or {}).get('type') or '?'] += 1
                failed += 1 if t.get('error') else 0
                listed += 1
                if t.get('user'):
                    users.add(t['user'])
        secs = max(1e-3, (t_end - t_start) / 1000.0)
        tx = {'count': total, 'se': se, 'method': 'sampled-blocks', 'blocks': N, 'sampled': len(got),
              'tps': (total / secs) if total is not None else None, 'blocks_per_second': N / secs,
              'action_mix': {k: round(v / listed, 4) for k, v in mix.most_common(12)} if listed else {},
              'failed_share': (failed / listed) if listed else None, 'distinct_users_in_sample': len(users),
              'search_reads': r1 + r2, 'first_height': h_start, 'last_height': h_end,
              'note': 'HyperCore actions (orders, cancels, modifies, EVM raw txs, transfers) per explorer block'}
        if len(got) < len(hs):
            errors.append('%d of %d sampled blocks did not come back' % (len(hs) - len(got), len(hs)))
    except HttpError as e:
        errors.append('explorer: %s' % str(e)[:120])
        notes.append('transaction count unavailable: the explorer did not answer')
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, ctx.end_ts),
            'endpoint': '%s + %s' % (info, explorer), 'calls': http.requests, 'dexes': [d or 'main' for d in dexes],
            'notes': notes, 'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
