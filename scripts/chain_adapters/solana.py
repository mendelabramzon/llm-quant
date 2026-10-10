#!/usr/bin/env python3
"""Solana: transactions from the validator's own performance samples, transfer value from a stratified sample of blocks.

Counting. `getRecentPerformanceSamples` returns, for each of the last ~720 minutes, how many transactions (and how many
non-vote transactions) the cluster processed, so the count over a window inside the last twelve hours is a sum of
published per-minute counts rather than an estimate. A longer window is covered from the samples it overlaps and
scaled to its length (`coverage` says how much was read). `getTransactionCount` — the cumulative total — is recorded too,
so the daily series can take exact differences between runs. Vote transactions (~half of everything) are reported but
excluded from the headline, because they are consensus overhead rather than activity.

Value. Each sampled block is read in full and reduced on arrival: for every successful non-vote transaction, the sum of
the positive token-balance changes per mint (from `pre/postTokenBalances`) is what that mint moved, and the positive
lamport changes are what SOL moved. A swap therefore counts both of its legs and a routed swap counts each hop, which is
gross transfer value by construction (see the package docstring). Blocks are ~1,300 transactions and several MB, so the
sample is small (120 by default) and the per-asset standard error is reported beside every figure.
"""
import concurrent.futures as cf
import sys
import time

from chain_adapters import (JsonRpc, Http, asset_rows, register, sample_points, stratified_total, window_dict, ROOT)

VOTE = 'Vote111111111111111111111111111111111111111'
WSOL = 'So11111111111111111111111111111111111111112'
PUBLIC = 'https://api.mainnet-beta.solana.com'
BLOCK_PARAMS = {'encoding': 'json', 'transactionDetails': 'full', 'rewards': False,
                'maxSupportedTransactionVersion': 1, 'commitment': 'finalized'}


PRUNED_CODES = (-32001, -32004, -32009, -32011)


class Fallback:
    """GetBlock first, the public endpoint for what GetBlock's nodes no longer hold.

    GetBlock's nodes prune blocks within hours ("Block N cleaned up, does not exist on node"), while the public
    mainnet-beta endpoint answers from long-term storage, slowly. A calendar-day window read the next morning lives
    almost entirely in the second regime, so every call that comes back pruned is retried there, and counted.
    """

    def __init__(self, primary, public):
        self.primary, self.public = primary, public
        self.public_calls = 0

    def call(self, method, params=None, **kw):
        try:
            return self.primary.call(method, params, **kw) if kw else self.primary.call(method, params)
        except Exception as e:
            msg = str(e).lower()
            if getattr(e, 'code', None) in PRUNED_CODES or 'cleaned up' in msg or 'not available' in msg or 'first available' in msg:
                self.public_calls += 1
                return self.public.call(method, params)
            raise


def client():
    sys.path.insert(0, str(ROOT / 'scripts'))
    # the public endpoint caps data per IP (~100 MB per 30 s) and a full block is several MB: pace it, don't race it
    public = JsonRpc([PUBLIC], http=Http(min_interval=1.6, timeout=180), batch_size=1)
    try:
        import solana_rpc
        return Fallback(solana_rpc.Client(), public), 'getblock+public'
    except Exception:
        return public, 'public'


def slot_at(c, ts, hi_slot, hi_ts):
    """First produced slot with blockTime >= ts: bracket (slots are ~0.27-0.4 s, so the guess is checked, not
    trusted) and bisect over produced slots."""

    def produced_at_or_after(s):
        r = c.call('getBlocksWithLimit', [s, 1, {'commitment': 'finalized'}])
        return r[0] if r else None

    hi = hi_slot
    back = int((hi_ts - ts) * 4.0) + 5000
    lo = max(0, hi_slot - back)
    while lo > 0:
        s0 = produced_at_or_after(lo)
        if s0 is not None and c.call('getBlockTime', [s0]) < ts:
            break
        back *= 2
        lo = max(0, hi_slot - back)
    while lo < hi:
        mid = (lo + hi) // 2
        s = produced_at_or_after(mid)
        if s is None or c.call('getBlockTime', [s]) < ts:
            lo = (s if s is not None else mid) + 1
        else:
            hi = mid
    return produced_at_or_after(lo)


def reduce_block(b):
    """Per-block sums: tx counts, and per-mint (count, raw positive delta, decimals) over successful non-vote txs."""
    n_all = len(b.get('transactions') or [])
    n_vote = n_fail = 0
    mints = {}
    lamports = 0
    sol_receipts = 0
    for t in b.get('transactions') or []:
        msg = t['transaction']['message']
        keys = list(msg['accountKeys'])
        if VOTE in keys:
            n_vote += 1
            continue
        meta = t.get('meta') or {}
        if meta.get('err') is not None:
            n_fail += 1
            continue
        la = meta.get('loadedAddresses') or {}
        keys += (la.get('writable') or []) + (la.get('readonly') or [])
        pre = {}
        for a in meta.get('preTokenBalances') or []:
            pre[a['accountIndex']] = (a['mint'], int(a['uiTokenAmount']['amount']), a['uiTokenAmount']['decimals'])
        seen = set()
        for a in meta.get('postTokenBalances') or []:
            i = a['accountIndex']
            seen.add(i)
            post = int(a['uiTokenAmount']['amount'])
            p0 = pre.get(i, (a['mint'], 0, a['uiTokenAmount']['decimals']))[1]
            d = post - p0
            if d > 0:
                e = mints.setdefault(a['mint'], [0, 0, a['uiTokenAmount']['decimals']])
                e[0] += 1
                e[1] += d
        pb, qb = meta.get('preBalances') or [], meta.get('postBalances') or []
        for i in range(min(len(pb), len(qb))):
            d = qb[i] - pb[i]
            if d > 0:
                lamports += d
                sol_receipts += 1
    return {'n_all': n_all, 'n_vote': n_vote, 'n_fail': n_fail, 'mints': mints, 'lamports': lamports,
            'sol_receipts': sol_receipts, 'ts': b.get('blockTime')}


@register('solana')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    c, src = client()
    head = c.call('getSlot', [{'commitment': 'finalized'}])
    head_ts = c.call('getBlockTime', [head])
    if isinstance(c, Fallback):
        # GetBlock answers getBlocksWithLimit below its retention with its first available block — no error, just the
        # wrong slot — so a window that starts before that block is read from the public endpoint end to end.
        try:
            first_avail = c.primary.call('getFirstAvailableBlock', [])
        except Exception:
            first_avail = None
        if first_avail is None or head - int((head_ts - ctx.start_ts) * 4.0) - 5000 < first_avail:
            c, src = c.public, 'public (window older than GetBlock retention)'
    end_ts = min(ctx.end_ts, head_ts)
    end_slot = head if end_ts >= head_ts else slot_at(c, end_ts, head, head_ts) - 1
    start_slot = slot_at(c, ctx.start_ts, head, head_ts)
    tx_total = c.call('getTransactionCount', [{'commitment': 'finalized'}])

    # ------------------------------------------------------------------ counts from the per-minute samples
    # The samples are node-local: a node keeps ~4.5 hours of them (not the documented 12), a node that was catching up
    # records one "60 s" sample spanning 600+ slots, and the provider load-balances calls across nodes. So coverage is
    # measured in slots (each sample covers `numSlots` slots ending at `slot`), the best of three answers is kept, and
    # the count is called exact only when the window's slots are covered end to end.
    win_slots = end_slot - start_slot + 1
    best = None
    for _ in range(3):
        perf = c.call('getRecentPerformanceSamples', [720]) or []
        inwin = [s for s in perf if start_slot <= s['slot'] - s['numSlots'] + 1 and s['slot'] <= end_slot]
        cov = sum(s['numSlots'] for s in inwin) / max(1, win_slots)
        if best is None or cov > best[0]:
            best = (cov, inwin)
        if cov >= 0.97:
            break
    cov, inwin = best
    nonvote = sum(s.get('numNonVoteTransactions') or 0 for s in inwin)
    allt = sum(s['numTransactions'] for s in inwin)
    exact = cov >= 0.97
    usable = cov >= 0.5
    tx = {'count': (nonvote / cov) if usable else None, 'se': 0.0 if exact else None,
          'all_including_votes': (allt / cov) if usable else None,
          'method': 'exact-counter' if exact else 'counter-extrapolated',
          'coverage': min(1.0, cov), 'perf_samples': len(inwin), 'cumulative_total': tx_total,
          'note': 'non-vote transactions, successful and failed; getRecentPerformanceSamples, scaled by slot coverage '
                  'when the node did not cover the whole window (nodes keep ~4.5 h)'}

    # ------------------------------------------------------------------ value from sampled blocks
    produced = []
    s = start_slot
    while s <= end_slot:
        e = min(end_slot, s + 499_999)
        produced += c.call('getBlocks', [s, e, {'commitment': 'finalized'}]) or []
        s = e + 1
    N = len(produced)
    n_samples = int(p.get('samples') or min(ctx.samples, 200))
    idx = sample_points(0, N - 1, n_samples, seed=int(ctx.start_ts))
    slots = [produced[i] for i in idx]

    def fetch(slot):
        err = None
        for attempt in range(3):
            try:
                b = c.call('getBlock', [slot, BLOCK_PARAMS], timeout=180) if src.startswith('getblock') else c.call('getBlock', [slot, BLOCK_PARAMS])
                return slot, reduce_block(b) if b else None
            except Exception as ex:
                err = str(ex)[:120]
                time.sleep(1 + attempt)
        return slot, {'error': err}

    with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 8))) as ex:
        reduced = list(ex.map(fetch, slots))
    units = [r for _, r in reduced if r and 'error' not in r]
    errors = ['slot %d: %s' % (s_, r.get('error') if r else 'null') for s_, r in reduced if not r or 'error' in r]
    n = len(units)
    block_nonvote, block_se = stratified_total([u['n_all'] - u['n_vote'] for u in units], N)
    fails = sum(u['n_fail'] for u in units)
    nv = sum(u['n_all'] - u['n_vote'] for u in units)
    tx.update({'from_blocks': block_nonvote, 'from_blocks_se': block_se, 'failed_share': (fails / nv) if nv else None,
               'blocks': N, 'sampled': n, 'skipped_slots': (end_slot - start_slot + 1) - N})
    if tx['count'] is None:
        tx['count'], tx['se'], tx['method'] = block_nonvote, block_se, 'sampled-blocks'

    per_asset, meta, dec_of = {}, {}, {}
    for i, u in enumerate(units):
        for mint, (cnt, raw, dec) in u['mints'].items():
            d = per_asset.setdefault(mint, {'count': [0] * n, 'raw': [0] * n})
            d['count'][i] += cnt
            d['raw'][i] += raw
            dec_of[mint] = dec
    keys = ['solana:%s' % m for m in per_asset]
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'solana')
    pr = ctx.prices.get(keys + [nat_key])
    price_of = {}
    pa = {}
    for mint, d in per_asset.items():
        q = pr.get('solana:%s' % mint)
        dec = dec_of[mint]
        meta[mint] = {'symbol': (q or {}).get('symbol') or ('SOL' if mint == WSOL else None), 'decimals': dec}
        price_of[mint] = (q or {}).get('price') if q else ((pr.get(nat_key) or {}).get('price') if mint == WSOL else None)
        pa[mint] = {'count': d['count'], 'amount': [x / 10 ** dec for x in d['raw']]}
    pa['native:SOL'] = {'count': [u['sol_receipts'] for u in units], 'amount': [u['lamports'] / 1e9 for u in units]}
    meta['native:SOL'] = {'symbol': 'SOL', 'decimals': 9}
    price_of['native:SOL'] = (pr.get(nat_key) or {}).get('price')
    tr = asset_rows(pa, n, N, meta, price_of, native_symbols=['SOL'])
    for r in tr['assets'] + tr['unpriced_top']:
        if r['asset'] == 'native:SOL':
            r['note'] = 'positive lamport changes: transfers, rent deposits, tips and wrapping all count'
    tr['method'] = 'sampled-blocks (token-balance deltas)'
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first_slot': start_slot, 'last_slot': end_slot, 'head_slot': head},
            'endpoint': src, 'public_fallback_calls': getattr(c, 'public_calls', None),
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
