#!/usr/bin/env python3
"""Hedera: an exact transaction count from the mirror node's record-file blocks, and HBAR / HTS value from a sample.

Counting. The mirror node groups consensus into ~2 s record files ("blocks"), and each block record carries `count`,
the number of transaction records it holds. Paging `/blocks` 100 at a time over the window reads every block, so the
count is exact (`exact-blocks`; a day is ~400 requests, run in parallel). A record is a transaction *or* a child
record a transaction spawned (a contract's precompile call, an auto-created account, a scheduled execution), so the
sampled blocks also report how many records were top-level, which succeeded, and the mix by type — on 2026-10-09
consensus-service messages (CONSENSUSSUBMITMESSAGE) were 31% of records, and the type mix is the first thing to read
before calling a Hedera count "activity".

Value. For a stratified sample of the window's blocks, `/transactions` over each block's consensus range returns every
record with its HBAR `transfers` and HTS `token_transfers`, which Hedera already states net per account (each list
sums to zero). A transaction's work can be split across a parent record and child records (a contract call's HBAR
legs on the parent, its token transfers on precompile children), so successful records are first merged by
`transaction_id` and the value of a transaction in an asset is the sum of the accounts' positive net changes — the
repo-wide convention, under which a router that receives and forwards in two child records counts nothing. HBAR
received by accounts numbered below SYSTEM_ACCOUNT_MAX is excluded: the treasury 0.0.2, the node accounts 0.0.3+ and
the fee and reward accounts 0.0.98 / 0.0.800-0.0.802 only ever receive fees and rewards. `gross` keeps the per-record
sums (no merging across a transaction's records) for comparison. HTS amounts are raw and scaled by the token's decimals
(from the price feed, or the mirror node's /tokens/{id}). Each sampled block's fetched records are compared with its
`count`, so a mirror-node gap shows up as `count_match_share` below one rather than as a quiet undercount.

Pricing. HBAR through the feed's coingecko id; tokens through DefiLlama's `hedera:0.0.<id>` key. When the feed is
silent, Circle's USDC (0.0.456858) falls back to par and SaucerSwap's WHBAR (0.0.1456986, whose treasury is the
wrapping contract) to the HBAR price — each only after the mirror node confirms the token's symbol (and the wrapper's
treasury) — and the row says which.
"""
import collections
import concurrent.futures as cf
import time
import urllib.parse

from chain_adapters import Http, asset_rows, register, sample_points, stratified_total, window_dict

MIRROR = 'https://mainnet-public.mirrornode.hedera.com/api/v1'
TINYBARS_PER_HBAR = 100_000_000
SYSTEM_ACCOUNT_MAX = 1000      # receipts by 0.0.0-0.0.999 are fees, node payments and staking rewards
BLOCK_PAGE = 100
MAX_COUNT_PAGES = 600          # exact count when the window needs at most this many /blocks pages (~33 hours)
MAX_VALUE_SAMPLES = 150
MAX_TX_PAGES = 8               # per sampled block (800 records)
NAME_UNPRICED = 20
CANONICAL_PAR = {
    # token id -> symbol. Checked 2026-10-09: DefiLlama prices hedera:0.0.456858 as USDC (6 decimals) at $0.9996.
    '0.0.456858': 'USDC',
}
NATIVE_WRAPPERS = {
    # token id -> (symbol, treasury). Checked 2026-10-09 on the mirror node: "Wrapped Hbar", 8 decimals, treasury
    # 0.0.1456985 (SaucerSwap's wrapping contract). The feed does not price it; it is HBAR one for one.
    '0.0.1456986': ('WHBAR', '0.0.1456985'),
}


def account_num(acct):
    """The entity number of '0.0.N' (shard.realm.num); -1 when it does not parse."""
    try:
        return int(str(acct).rsplit('.', 1)[1])
    except (IndexError, ValueError):
        return -1


def record_changes(t):
    """{asset id: {account: raw change}} of one successful record (HBAR in tinybars, HTS tokens in raw units)."""
    if t.get('result') != 'SUCCESS':
        return {}
    ch = {}
    for tr in t.get('transfers') or []:
        amt = int(tr.get('amount') or 0)
        if amt:
            d = ch.setdefault('native:HBAR', {})
            d[tr.get('account')] = d.get(tr.get('account'), 0) + amt
    for tt in t.get('token_transfers') or []:
        amt = int(tt.get('amount') or 0)
        if amt and tt.get('token_id'):
            d = ch.setdefault(tt['token_id'], {})
            d[tt.get('account')] = d.get(tt.get('account'), 0) + amt
    return ch


def merge_changes(into, ch):
    for a, accts in ch.items():
        d = into.setdefault(a, {})
        for acct, v in accts.items():
            d[acct] = d.get(acct, 0) + v
    return into


def positive_value(ch):
    """{asset: sum of positive net changes}, HBAR received by system accounts (fees, node and staking rewards) excluded."""
    out = {}
    for a, accts in ch.items():
        v = sum(x for acct, x in accts.items()
                if x > 0 and (a != 'native:HBAR' or account_num(acct) >= SYSTEM_ACCOUNT_MAX))
        if v > 0:
            out[a] = v
    return out


def is_child(t):
    return bool(t.get('parent_consensus_timestamp')) and int(t.get('nonce') or 0) > 0


def page_ranges(first, last, size=BLOCK_PAGE):
    """[(lo, hi)] block-number ranges of at most `size` covering [first, last]."""
    return [(s, min(s + size - 1, last)) for s in range(first, last + 1, size)]


@register('hedera')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    base = (p.get('mirror') or MIRROR).rstrip('/')
    root = '%s://%s' % urllib.parse.urlsplit(base)[:2]
    http = Http(min_interval=p.get('min_interval', 0.06), timeout=p.get('timeout', 60))
    workers = int(p.get('workers', 6))
    errors = []
    head_b = http.get(base + '/blocks?order=desc&limit=1')['blocks'][0]
    head_ts = int(float(head_b['timestamp']['to']))
    end_ts = min(ctx.end_ts, head_ts)
    fb = http.get(base + '/blocks?timestamp=gte:%d&limit=1&order=asc' % ctx.start_ts)['blocks']
    lb = http.get(base + '/blocks?timestamp=lt:%d&limit=1&order=desc' % end_ts)['blocks']
    if not fb or not lb:
        raise RuntimeError('no blocks in window')
    first, last = int(fb[0]['number']), int(lb[0]['number'])
    N = last - first + 1
    secs = max(1, end_ts - ctx.start_ts)

    # ------------------------------------------------------------------ count: every block record
    ranges = page_ranges(first, last)
    blocks = {}
    if len(ranges) <= int(p.get('max_count_pages', MAX_COUNT_PAGES)):
        def page(r):
            lo, hi = r
            try:
                return http.get('%s/blocks?block.number=gte:%d&block.number=lte:%d&limit=%d&order=asc'
                                % (base, lo, hi, BLOCK_PAGE))['blocks']
            except Exception as e:
                errors.append('blocks %d-%d: %s' % (lo, hi, str(e)[:120]))
                return []

        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for part in ex.map(page, ranges):
                for b in part:
                    blocks[int(b['number'])] = b
        got = [b for n_, b in blocks.items() if first <= n_ <= last]
        total = sum(int(b.get('count') or 0) for b in got)
        missing = N - len(got)
        count = total * N / max(1, len(got)) if missing else total
        if missing:
            errors.append('%d of %d blocks missing; count scaled to the window' % (missing, N))
        tx = {'count': count, 'se': 0.0 if not missing else None, 'method': 'exact-blocks' if not missing else 'blocks-scaled',
              'blocks_read': len(got)}
        sample_numbers = sample_points(first, last, min(int(p.get('samples') or ctx.samples),
                                                        int(p.get('max_value_samples', MAX_VALUE_SAMPLES))),
                                       seed=int(ctx.start_ts))
    else:
        sample_numbers = sample_points(first, last, min(int(p.get('samples') or ctx.samples), 300), seed=int(ctx.start_ts))
        tx = {'method': 'sampled-blocks'}

    # ------------------------------------------------------------------ sampled blocks: type mix and value
    def sampled(nb):
        try:
            b = blocks.get(nb) or http.get('%s/blocks/%d' % (base, nb))
            fr, to = b['timestamp']['from'], b['timestamp']['to']
            url = '%s/transactions?timestamp=gte:%s&timestamp=lte:%s&limit=100&order=asc' % (base, fr, to)
            recs = []
            for _ in range(MAX_TX_PAGES):
                d = http.get(url)
                recs += d.get('transactions') or []
                nxt = (d.get('links') or {}).get('next')
                if not nxt:
                    break
                url = root + nxt if nxt.startswith('/') else nxt
            types, results = collections.Counter(), collections.Counter()
            assets, children, by_tx = {}, 0, {}
            for t in recs:
                types[t.get('name') or '?'] += 1
                results[t.get('result') or '?'] += 1
                children += is_child(t)
                ch = record_changes(t)
                if ch:
                    merge_changes(by_tx.setdefault(t.get('transaction_id') or t.get('consensus_timestamp'), {}), ch)
                    for a, amt in positive_value(ch).items():
                        assets.setdefault(a, [0, 0, 0])[2] += amt
            for ch in by_tx.values():
                for a, amt in positive_value(ch).items():
                    e = assets.setdefault(a, [0, 0, 0])
                    e[0] += 1
                    e[1] += amt
            return nb, {'count': int(b.get('count') or 0), 'fetched': len(recs), 'types': dict(types),
                        'results': dict(results), 'children': children, 'assets': assets}
        except Exception as e:
            return nb, {'error': str(e)[:160]}

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        got_s = list(ex.map(sampled, sample_numbers))
    units = [u for _, u in got_s if 'error' not in u]
    errors += ['block %d: %s' % (nb, u['error']) for nb, u in got_s if 'error' in u]
    n = len(units)
    if tx['method'] == 'sampled-blocks':
        tx['count'], tx['se'] = stratified_total([u['count'] for u in units], N)
    fetched = sum(u['fetched'] for u in units)
    types, results = collections.Counter(), collections.Counter()
    for u in units:
        types.update(u['types'])
        results.update(u['results'])
    tx.update({'unit': 'record file', 'blocks': N, 'sampled': n, 'tps': tx['count'] / secs if tx.get('count') is not None else None,
               'type_share': {k: round(v / fetched, 4) for k, v in types.most_common(10)} if fetched else {},
               'success_share': (results.get('SUCCESS', 0) / fetched) if fetched else None,
               'child_share': (sum(u['children'] for u in units) / fetched) if fetched else None,
               'count_match_share': (sum(1 for u in units if u['fetched'] == u['count']) / n) if n else None,
               'note': 'transaction records per mirror-node block, including child records; type_share, child_share and '
                       'success_share come from the sampled blocks'})

    # ------------------------------------------------------------------ price
    per_asset = {}
    for i, u in enumerate(units):
        for a, (c, raw, graw) in u['assets'].items():
            d = per_asset.setdefault(a, {'count': [0] * n, 'raw': [0] * n, 'graw': [0] * n})
            d['count'][i] += c
            d['raw'][i] += raw
            d['graw'][i] += graw
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'hedera-hashgraph')
    tokens = [a for a in per_asset if a != 'native:HBAR']
    pr = ctx.prices.get([nat_key] + ['hedera:%s' % a for a in tokens])
    meta, price_of, source, scale = {}, {}, {}, {}
    q = pr.get(nat_key)
    meta['native:HBAR'] = {'symbol': 'HBAR', 'decimals': 8}
    price_of['native:HBAR'], source['native:HBAR'] = (q.get('price'), 'defillama') if q else (None, None)
    scale['native:HBAR'] = TINYBARS_PER_HBAR
    unpriced = []
    for a in tokens:
        q = pr.get('hedera:%s' % a)
        if q and q.get('decimals') is not None:
            meta[a] = {'symbol': q.get('symbol'), 'decimals': int(q['decimals'])}
            price_of[a], source[a] = q.get('price'), 'defillama'
            scale[a] = 10 ** int(q['decimals'])
        else:
            unpriced.append(a)
    unpriced.sort(key=lambda a: -sum(per_asset[a]['count']))
    for a in unpriced[:NAME_UNPRICED] + [x for x in unpriced if x in CANONICAL_PAR or x in NATIVE_WRAPPERS]:
        if a in meta:
            continue
        try:
            t = http.get('%s/tokens/%s' % (base, a))
            meta[a] = {'symbol': t.get('symbol'), 'decimals': int(t.get('decimals') or 0)}
            scale[a] = 10 ** int(t.get('decimals') or 0)
            if a in CANONICAL_PAR and (t.get('symbol') or '').upper() == CANONICAL_PAR[a]:
                price_of[a], source[a] = 1.0, 'par-canonical-issuer'
            elif (a in NATIVE_WRAPPERS and price_of.get('native:HBAR') is not None
                  and (t.get('symbol'), t.get('treasury_account_id')) == NATIVE_WRAPPERS[a]):
                price_of[a], source[a] = price_of['native:HBAR'], 'native-wrapper'
        except Exception as e:
            errors.append('token %s: %s' % (a, str(e)[:80]))
    pa = {}
    for a, d in per_asset.items():
        sc = scale.get(a)
        pa[a] = {'count': d['count'], 'amount': [(x / sc) if sc else 0.0 for x in d['raw']],
                 'gross': [(x / sc) if sc else 0.0 for x in d['graw']]}
        meta.setdefault(a, {'symbol': None, 'decimals': None})
        price_of.setdefault(a, None)
    tr = asset_rows(pa, n, N, meta, price_of, native_symbols=['HBAR'])
    for r in tr['assets'] + tr['unpriced_top']:
        r['price_source'] = source.get(r['asset'])
        if r['asset'] != 'native:HBAR' and scale.get(r['asset']) is None:
            r['note'] = 'decimals unknown: amount not scaled'
    tr['method'] = ('sampled-blocks (successful records merged per transaction_id; positive net HBAR to accounts '
                    '>= 0.0.%d and positive net HTS changes)' % SYSTEM_ACCOUNT_MAX)
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'head': int(head_b['number'])},
            'endpoint': urllib.parse.urlsplit(base).netloc, 'calls': http.requests,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
