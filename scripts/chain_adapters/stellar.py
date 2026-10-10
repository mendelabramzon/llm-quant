#!/usr/bin/env python3
"""Stellar: an exact transaction count from Horizon's ledger headers, and net payment value from a sample of ledgers.

Counting. Every ledger header Horizon serves carries `successful_transaction_count`, `failed_transaction_count` and
`operation_count`, and `/ledgers` pages them 200 at a time in sequence order. A day is ~17,300 ledgers, so reading every
header in the window is ~90 requests and the count is exact rather than estimated (`exact-blocks`); a window too long to
page within MAX_COUNT_PAGES falls back to a stratified sample of headers. Failed transactions count — they were
included in a ledger and paid a fee — and are reported separately (about a fifth of Stellar's transactions fail).
The window's first ledger is found by bisection on `closed_at`, and the page cursor for "after ledger s" is `s << 32`,
Horizon's paging token for a ledger.

Value. For a stratified sample of the window's ledgers, `/ledgers/{seq}/payments` (successful operations only) gives
every payment-like operation with its amount already in units, and the headline counts what each operation's receiver
gained, net (the repo-wide convention): a `payment` its amount, a `create_account` its starting balance, a path payment
its received leg only, Soroban `invoke_host_function` the `transfer` entries of its `asset_balance_changes`. A payment
to oneself moves nothing and counts nothing; a path payment that routes an asset back to its own sender (the shape of
an arbitrage loop: XLM in, XLM out, through the order books) counts only the sender's gain — the received amount less
the amount sent — because the rest of the loop is a round trip. `gross` keeps the operation amounts as the
records state them (both legs of a cross-asset path payment, whole loops) for comparison. `account_merge` carries no
amount and is counted as an operation only. A ledger holds hundreds of payments, so each sampled ledger is several pages
and the value sample is kept small (MAX_VALUE_SAMPLES).

Pricing. XLM through the feed's coingecko id; a credit asset only by code *and* issuer, through DefiLlama's
`stellar:<CODE>-<ISSUER>` key, so a lookalike USDC from another issuer stays unpriced. Circle's USDC at its canonical
issuer falls back to par only if the feed is silent, and the row says so.
"""
import collections
import concurrent.futures as cf
import datetime as dt
import time
import urllib.parse

from chain_adapters import Http, asset_rows, register, sample_points, stratified_total, window_dict

HORIZON = 'https://horizon.stellar.org'
PAGE = 200
MAX_COUNT_PAGES = 150          # exact count when the window needs at most this many /ledgers pages (~30 hours)
MAX_VALUE_SAMPLES = 60         # sampled ledgers whose payments are read
MAX_PAYMENT_PAGES = 10         # per sampled ledger (2,000 payment operations)
SECONDS_PER_LEDGER_SEED = 5.0  # seeds the bracket only
CANONICAL_PAR = {
    # code-issuer -> symbol. Checked 2026-10-09: DefiLlama prices this exact key as USDC at $0.9996.
    'USDC-GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN': 'USDC',
}


def ts_iso(s):
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())


def cursor_after(seq):
    """Horizon's paging token for ledger `seq`; a page with this cursor (order=asc) starts at seq + 1."""
    return seq << 32


def locate(target, lo_bound, head, head_ts, seconds_per_unit, ts_of):
    """First index in [lo_bound, head] whose time is >= target (head when none earlier), for a non-decreasing ts_of."""
    guess = int(head - (head_ts - target) / seconds_per_unit)
    lo = min(head, max(lo_bound, guess - 400))
    hi = max(lo_bound, min(head, guess + 400))
    step = 800
    while lo > lo_bound and ts_of(lo) >= target:
        lo, step = max(lo_bound, lo - step), step * 2
    step = 800
    while hi < head and ts_of(hi) < target:
        hi, step = min(head, hi + step), step * 2
    while lo < hi:
        mid = (lo + hi) // 2
        if ts_of(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def asset_id(rec, prefix=''):
    """'native:XLM' or 'CODE-ISSUER' for the asset named by `<prefix>asset_*` fields of a Horizon record."""
    ty = rec.get(prefix + 'asset_type')
    if ty == 'native':
        return 'native:XLM'
    code, issuer = rec.get(prefix + 'asset_code'), rec.get(prefix + 'asset_issuer')
    return '%s-%s' % (code, issuer) if code and issuer else None


def legs(rec):
    """(net, gross): lists of (asset id, amount) one record of the payments endpoint moved.

    net counts what the receiver gained: nothing for a payment to oneself, the received leg of a path payment, and for a
    path payment back to its own sender in the same asset only the gain (received - sent). gross is the records' own
    amounts: both legs of a cross-asset path payment, a loop's full size.
    """
    ty = rec.get('type')
    try:
        if ty == 'payment':
            g = [(asset_id(rec), float(rec['amount']))]
            return ([] if rec.get('from') == rec.get('to') else g), g
        if ty in ('path_payment_strict_send', 'path_payment_strict_receive'):
            dst = (asset_id(rec), float(rec['amount']))
            src = (asset_id(rec, 'source_'), float(rec.get('source_amount') or 0))
            gross = [dst] + ([src] if src[0] != dst[0] else [])
            if rec.get('from') == rec.get('to'):
                net = [(dst[0], max(0.0, dst[1] - src[1]))] if src[0] == dst[0] else [dst]
            else:
                net = [dst]
            return net, gross
        if ty == 'create_account':
            g = [('native:XLM', float(rec.get('starting_balance') or 0))]
            return g, g
        if ty == 'invoke_host_function':
            g = [(asset_id(ch), float(ch.get('amount') or 0)) for ch in (rec.get('asset_balance_changes') or [])
                 if ch.get('type') == 'transfer' and asset_id(ch)]
            n = [(asset_id(ch), float(ch.get('amount') or 0)) for ch in (rec.get('asset_balance_changes') or [])
                 if ch.get('type') == 'transfer' and asset_id(ch) and ch.get('from') != ch.get('to')]
            return n, g
    except (KeyError, TypeError, ValueError):
        return [], []
    return [], []


def sum_headers(records, first, last):
    """Totals over ledger headers inside [first, last], each ledger counted once."""
    seen = {}
    for r in records:
        s = int(r['sequence'])
        if first <= s <= last:
            seen[s] = r
    tot = collections.Counter()
    for r in seen.values():
        tot['successful'] += int(r.get('successful_transaction_count') or 0)
        tot['failed'] += int(r.get('failed_transaction_count') or 0)
        tot['operations'] += int(r.get('operation_count') or 0)
        tot['tx_set_operations'] += int(r.get('tx_set_operation_count') or 0)
    return dict(tot), sorted(seen)


@register('stellar')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    base = (p.get('horizon') or HORIZON).rstrip('/')
    http = Http(min_interval=p.get('min_interval', 0.12), timeout=p.get('timeout', 60))
    workers = int(p.get('workers', 6))
    head_rec = http.get(base + '/ledgers?order=desc&limit=1')['_embedded']['records'][0]
    head, head_ts = int(head_rec['sequence']), ts_iso(head_rec['closed_at'])
    end_ts = min(ctx.end_ts, head_ts)
    cache = {head: head_ts}

    def ts_of(s):
        if s not in cache:
            cache[s] = ts_iso(http.get('%s/ledgers/%d' % (base, s))['closed_at'])
        return cache[s]

    first = locate(ctx.start_ts, 2, head, head_ts, SECONDS_PER_LEDGER_SEED, ts_of)
    last = head if end_ts >= head_ts else locate(end_ts, first, head, head_ts, SECONDS_PER_LEDGER_SEED, ts_of) - 1
    N = last - first + 1
    errors = []
    secs = max(1, end_ts - ctx.start_ts)

    # ------------------------------------------------------------------ count: every header, or a sample of them
    pages = (N + PAGE - 1) // PAGE
    if pages <= int(p.get('max_count_pages', MAX_COUNT_PAGES)):
        starts = list(range(first, last + 1, PAGE))

        def page(s):
            try:
                return http.get('%s/ledgers?order=asc&limit=%d&cursor=%d' % (base, PAGE, cursor_after(s - 1)))['_embedded']['records']
            except Exception as e:
                errors.append('ledgers page at %d: %s' % (s, str(e)[:120]))
                return []

        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            recs = [r for part in ex.map(page, starts) for r in part]
        tot, seqs = sum_headers(recs, first, last)
        missing = N - len(seqs)
        count = tot.get('successful', 0) + tot.get('failed', 0)
        if missing:
            count = count * N / max(1, len(seqs))
            errors.append('%d of %d ledger headers missing; count scaled to the window' % (missing, N))
        tx = {'count': count, 'se': 0.0 if not missing else None, 'method': 'exact-blocks' if not missing else 'blocks-scaled',
              'successful': tot.get('successful', 0), 'failed': tot.get('failed', 0),
              'operations': tot.get('operations', 0), 'tx_set_operations': tot.get('tx_set_operations', 0),
              'headers_read': len(seqs)}
    else:
        pts = sample_points(first, last, min(int(p.get('samples') or ctx.samples), 300), seed=int(ctx.start_ts) + 1)

        def header(s):
            try:
                return http.get('%s/ledgers/%d' % (base, s))
            except Exception as e:
                errors.append('ledger %d: %s' % (s, str(e)[:120]))
                return None

        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            hs = [h for h in ex.map(header, pts) if h]
        succ, _ = stratified_total([int(h['successful_transaction_count']) for h in hs], N)
        fail, _ = stratified_total([int(h['failed_transaction_count']) for h in hs], N)
        count, se = stratified_total([int(h['successful_transaction_count']) + int(h['failed_transaction_count']) for h in hs], N)
        ops, _ = stratified_total([int(h['operation_count']) for h in hs], N)
        tx = {'count': count, 'se': se, 'method': 'sampled-blocks', 'successful': succ, 'failed': fail, 'operations': ops,
              'headers_read': len(hs)}
    tx.update({'unit': 'ledger', 'blocks': N, 'tps': tx['count'] / secs if tx['count'] is not None else None,
               'failed_share': (tx['failed'] / tx['count']) if tx.get('count') else None,
               'note': 'successful + failed transactions per ledger header (failed ones are included and pay a fee); '
                       'operations are successful operations only'})

    # ------------------------------------------------------------------ value: payments in a sample of ledgers
    n_val = min(int(p.get('value_samples') or ctx.samples), int(p.get('max_value_samples', MAX_VALUE_SAMPLES)))
    vpts = sample_points(first, last, n_val, seed=int(ctx.start_ts))

    def payments(s):
        url = '%s/ledgers/%d/payments?limit=%d&include_failed=false&order=asc' % (base, s, PAGE)
        assets, ops, kinds, truncated = {}, 0, collections.Counter(), False
        try:
            for k in range(MAX_PAYMENT_PAGES):
                d = http.get(url)
                recs = (d.get('_embedded') or {}).get('records') or []
                for r in recs:
                    ops += 1
                    kinds[r.get('type')] += 1
                    net, gross = legs(r)
                    for a, amt in net:
                        if a and amt > 0:
                            e = assets.setdefault(a, [0, 0.0, 0.0])
                            e[0] += 1
                            e[1] += amt
                    for a, amt in gross:
                        if a and amt > 0:
                            assets.setdefault(a, [0, 0.0, 0.0])[2] += amt
                if len(recs) < PAGE:
                    break
                url = ((d.get('_links') or {}).get('next') or {}).get('href')
                if not url:
                    break
            else:
                truncated = True
        except Exception as e:
            return s, {'error': str(e)[:160]}
        return s, {'assets': assets, 'ops': ops, 'kinds': dict(kinds), 'truncated': truncated}

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        got = list(ex.map(payments, vpts))
    units = [u for _, u in got if 'error' not in u]
    errors += ['payments %d: %s' % (s, u['error']) for s, u in got if 'error' in u]
    n = len(units)
    per_asset = {}
    for i, u in enumerate(units):
        for a, (c, amt, gross) in u['assets'].items():
            d = per_asset.setdefault(a, {'count': [0] * n, 'amount': [0.0] * n, 'gross': [0.0] * n})
            d['count'][i] += c
            d['amount'][i] += amt
            d['gross'][i] += gross
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'stellar')
    key_of = {a: 'stellar:%s' % a for a in per_asset if a != 'native:XLM'}
    pr = ctx.prices.get([nat_key] + list(key_of.values()))
    meta, price_of, source = {}, {}, {}
    for a in per_asset:
        if a == 'native:XLM':
            q = pr.get(nat_key)
            meta[a] = {'symbol': 'XLM', 'decimals': 7}
        else:
            q = pr.get(key_of[a])
            meta[a] = {'symbol': a.split('-', 1)[0], 'decimals': 7}
        if q:
            price_of[a], source[a] = q.get('price'), 'defillama'
        elif a in CANONICAL_PAR:
            price_of[a], source[a] = 1.0, 'par-canonical-issuer'
        else:
            price_of[a], source[a] = None, None
    tr = asset_rows(per_asset, n, N, meta, price_of, native_symbols=['XLM'])
    for r in tr['assets'] + tr['unpriced_top']:
        r['price_source'] = source.get(r['asset'])
        if r['asset'] != 'native:XLM':
            r['issuer'] = r['asset'].split('-', 1)[1]
    kinds = collections.Counter()
    for u in units:
        kinds.update(u['kinds'])
    pay_ops, pay_se = stratified_total([u['ops'] for u in units], N)
    tr.update({'method': 'sampled-blocks (Horizon payments, net: received legs, self-payments nothing, self-loops their '
                         'gain; create_account, Soroban transfers; account_merge amounts not counted)',
               'payment_operations': pay_ops, 'payment_operations_se': pay_se,
               'payment_kinds_sampled': dict(kinds.most_common(8)),
               'truncated_ledgers': sum(1 for u in units if u['truncated'])})
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'head': head},
            'endpoint': urllib.parse.urlsplit(base).netloc, 'calls': http.requests,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
