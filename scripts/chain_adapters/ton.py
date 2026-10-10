#!/usr/bin/env python3
"""TON: transactions and transfer value from toncenter's v3 index, sampled in short sub-windows.

What a TON "transaction" is. TON is an actor model: every account processes each inbound message in its own
transaction, so one user action — a wallet sending a jetton, a swap through a DEX — is a *trace* of several transactions
across accounts (the wallet, the jetton wallets, the router, the pool, the notification). Explorers count those
per-account transactions, and so does the headline here (workchain 0 only; the masterchain's tick-tock and elector
transactions are reported apart as `masterchain`). The EVM-comparable figure — transactions started by a signed
external message — is estimated beside it as `user_initiated`.

Counting. `/blocks?start_utime=&end_utime=` lists every block (masterchain and each workchain-0 shard) generated in a
time range with its `tx_count`. The window is cut into 30-second units, one unit per stratum is read, and the total is
the stratified estimate over all units (successive-difference standard error). Value comes from the same sub-windows:

* jettons — `/jetton/transfers` with no master filter, so every jetton that moved is discovered rather than listed. A
  record is one owner-to-owner hop with its own transaction, so netting per transaction (the repo's convention) leaves
  it unchanged: `amount` is the record sum, aborted transfers excluded. A routed swap still shows each leg it sends.
* TON — the first 5 seconds of each sampled unit are read as full transactions (`/transactions`), and the internal
  messages' values are netted per trace (`net_positive` over every hop of one trace, so a forward that bounces back, or
  a router that passes value on, cancels); traces that straddle the slice edge are netted over the part inside it.
  Masterchain accounts (validator and config plumbing) are excluded.

Rate limit. Without a key toncenter serves about one request a second, so a 24-hour probe reads ~36 units (three calls
each) in about three minutes and reports a wide standard error rather than a narrow one it did not earn.
"""
import time

from chain_adapters import (Http, HttpError, asset_rows, net_positive, register, sample_points, stratified_total,
                            window_dict)

BASE = 'https://toncenter.com/api/v3'
UNIT_SECONDS = 30            # sub-window read for blocks and jetton transfers
SLICE_SECONDS = 5            # leading slice of each sampled unit read as full transactions
DEFAULT_SAMPLES = 36
PAGE = {'blocks': 256, 'jetton_transfers': 1000, 'transactions': 1000}
MAX_PAGES = 4
NANO = 1e9


def raw_upper(addr):
    """'0:b113..' or '0:B113..' -> '0:B113..' (toncenter writes raw addresses upper-case; the price feed accepts either)."""
    if not isinstance(addr, str) or ':' not in addr:
        return addr
    wc, h = addr.split(':', 1)
    return '%s:%s' % (wc, h.upper())


def workchain(addr):
    try:
        return int(str(addr).split(':', 1)[0])
    except (ValueError, IndexError):
        return None


def jetton_amount(rec):
    """Raw integer amount of a jetton transfer record; None if missing or malformed."""
    try:
        v = int(rec.get('amount'))
    except (TypeError, ValueError):
        return None
    return v if v >= 0 else None


def jetton_symbol(metadata, master):
    """Symbol and decimals of a jetton master from a toncenter `metadata` block, when the index attached them."""
    m = (metadata or {}).get(master) or (metadata or {}).get(raw_upper(master)) or {}
    for ti in m.get('token_info') or []:
        if ti.get('type') == 'jetton_masters':
            ex = ti.get('extra') or {}
            dec = ex.get('decimals')
            try:
                dec = int(dec) if dec is not None else None
            except (TypeError, ValueError):
                dec = None
            return ti.get('symbol'), dec
    return None, None


def reduce_jettons(records):
    """{master: [count, raw_sum]} over non-aborted records."""
    out = {}
    for r in records or []:
        if r.get('transaction_aborted'):
            continue
        amt = jetton_amount(r)
        if amt is None:
            continue
        m = raw_upper(r.get('jetton_master'))
        e = out.setdefault(m, [0, 0])
        e[0] += 1
        e[1] += amt
    return out


def reduce_transactions(txs):
    """One slice of transactions -> counts and native value (net per trace, gross), workchain 0 only."""
    wc0 = [t for t in txs or [] if workchain(t.get('account')) == 0]
    ext = sum(1 for t in wc0 if t.get('in_msg') and t['in_msg'].get('source') is None)
    aborted = sum(1 for t in wc0 if (t.get('description') or {}).get('aborted'))
    traces = {}
    gross = 0
    hops = 0
    for t in wc0:
        m = t.get('in_msg') or {}
        src, dst = m.get('source'), m.get('destination')
        if not src or not dst or workchain(src) != 0:
            continue
        try:
            v = int(m.get('value') or 0)
        except (TypeError, ValueError):
            continue
        if v <= 0:
            continue
        traces.setdefault(t.get('trace_id') or t.get('hash'), []).append((src, dst, v))
        gross += v
        hops += 1
    net = sum(net_positive(mv) for mv in traces.values())
    return {'txs': len(wc0), 'external': ext, 'aborted': aborted, 'net': net, 'gross': gross, 'hops': hops,
            'traces': len(traces)}


class Toncenter:
    def __init__(self, base, http):
        self.base = base.rstrip('/')
        self.http = http
        self.calls = 0

    def page(self, path, params, key):
        out, meta = [], {}
        for i in range(MAX_PAGES):
            q = dict(params, limit=PAGE[key], offset=i * PAGE[key])
            d = self.http.get(self.base + path, q)
            self.calls += 1
            rows = d.get(key) or []
            out += rows
            meta.update(d.get('metadata') or {})
            if len(rows) < PAGE[key]:
                return out, meta, False
        return out, meta, True        # truncated: more rows than MAX_PAGES pages


@register('ton')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    http = Http(min_interval=float(p.get('min_interval', 1.1)), timeout=p.get('timeout', 60), retries=4)
    tc = Toncenter(p.get('toncenter') or BASE, http)
    head = http.get(tc.base + '/masterchainInfo')
    tc.calls += 1
    head_ts = int((head.get('last') or {}).get('gen_utime') or time.time())
    end_ts = min(ctx.end_ts, head_ts - 30)        # the index trails the head by a few seconds
    S = max(UNIT_SECONDS, end_ts - ctx.start_ts)
    U = int(S // UNIT_SECONDS)
    n = min(int(p.get('samples') or min(ctx.samples, DEFAULT_SAMPLES)), U)
    units = sample_points(0, U - 1, n, seed=int(ctx.start_ts))
    rows, errors, truncated = [], [], 0
    jetton_meta = {}
    for u in units:
        a = int(ctx.start_ts) + u * UNIT_SECONDS
        b = a + UNIT_SECONDS - 1
        try:
            blocks, _, tb = tc.page('/blocks', {'start_utime': a, 'end_utime': b, 'sort': 'asc'}, 'blocks')
            jt, jmeta, tj = tc.page('/jetton/transfers', {'start_utime': a, 'end_utime': b, 'sort': 'asc'},
                                    'jetton_transfers')
            txs, _, tt = tc.page('/transactions', {'start_utime': a, 'end_utime': a + SLICE_SECONDS - 1, 'sort': 'asc'},
                                 'transactions')
        except HttpError as e:
            errors.append('unit %d: %s' % (a, str(e)[:120]))
            continue
        truncated += int(tb) + int(tj) + int(tt)
        jetton_meta.update(jmeta)
        rows.append({'wc0': sum(int(x.get('tx_count') or 0) for x in blocks if int(x.get('workchain', 0)) == 0),
                     'mc': sum(int(x.get('tx_count') or 0) for x in blocks if int(x.get('workchain', 0)) == -1),
                     'blocks': len(blocks), 'jettons': reduce_jettons(jt), 'slice': reduce_transactions(txs)})
    k = len(rows)
    if not k:
        raise RuntimeError('no sub-window could be read: %s' % '; '.join(errors[:3]))
    wc0, wc0_se = stratified_total([r['wc0'] for r in rows], U)
    mc, _ = stratified_total([r['mc'] for r in rows], U)
    N5 = S / SLICE_SECONDS
    ext, ext_se = stratified_total([r['slice']['external'] for r in rows], N5)
    slice_tx = sum(r['slice']['txs'] for r in rows)
    aborted = sum(r['slice']['aborted'] for r in rows)
    secs = max(1, end_ts - ctx.start_ts)

    # ------------------------------------------------------------------ value: jettons per 30 s unit, TON per 5 s slice
    masters = sorted({m for r in rows for m in r['jettons']})
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'the-open-network')
    pr = ctx.prices.get(['ton:%s' % m for m in masters] + [nat_key])
    per, meta, price_of = {}, {}, {}
    for m in masters:
        q = pr.get('ton:%s' % m)
        sym, dec = jetton_symbol(jetton_meta, m)
        if q and q.get('decimals') is not None:
            dec, sym = int(q['decimals']), q.get('symbol') or sym
        meta[m] = {'symbol': sym, 'decimals': dec}
        price_of[m] = q.get('price') if q else None
        cnt = [r['jettons'].get(m, [0, 0])[0] for r in rows]
        raw = [r['jettons'].get(m, [0, 0])[1] for r in rows]
        amt = [x / 10 ** dec for x in raw] if dec is not None else [0.0] * k
        per[m] = {'count': cnt, 'amount': amt, 'gross': amt}
    jt_table = asset_rows(per, k, U, meta, price_of, native_symbols=['TON'])
    nat_price = (pr.get(nat_key) or {}).get('price')
    nat = asset_rows({'native:TON': {'count': [r['slice']['hops'] for r in rows],
                                     'amount': [r['slice']['net'] / NANO for r in rows],
                                     'gross': [r['slice']['gross'] / NANO for r in rows]}},
                     k, N5, {'native:TON': {'symbol': (cfg.get('native') or {}).get('symbol') or 'TON', 'decimals': 9}},
                     {'native:TON': nat_price}, native_symbols=['TON', 'GRAM'])
    # one table: jettons (30 s units) and TON (5 s slices) were each scaled over their own unit count
    tr = jt_table
    for row in nat['assets'] + nat['unpriced_top']:
        row['note'] = ('internal-message value on workchain 0, netted per trace inside 5-second slices; transfers = '
                       'message hops')
        row['class'] = 'native'
        (tr['assets'] if row.get('price') is not None else tr['unpriced_top']).append(row)
    tr['assets'].sort(key=lambda r: -(r['usd'] or 0))
    tr['priced_usd'] = sum(r['usd'] or 0 for r in tr['assets'])
    tr['gross_priced_usd'] = sum((r.get('gross_usd') or 0) for r in tr['assets'])
    by_class = {}
    for r in tr['assets']:
        by_class[r['class']] = by_class.get(r['class'], 0.0) + (r['usd'] or 0.0)
    tr['usd_by_class'] = by_class
    tr['method'] = ('sampled sub-windows: jetton transfer records per 30 s unit (one owner-to-owner hop each, so net per '
                    'transaction equals the record; aborted excluded); TON from 5 s transaction slices netted per trace')
    if truncated:
        errors.append('%d page sets hit the page cap (MAX_PAGES); those units are undercounted' % truncated)
    tx = {'count': wc0, 'se': wc0_se, 'method': 'sampled-blocks',
          'masterchain': mc, 'user_initiated': ext, 'user_initiated_se': ext_se,
          'aborted_share': (aborted / slice_tx) if slice_tx else None,
          'units_read': k, 'units_total': U, 'unit_seconds': UNIT_SECONDS,
          'tps': (wc0 / secs) if wc0 is not None else None,
          'note': 'workchain-0 per-account transactions (explorer convention; one user action is several); '
                  'user_initiated = transactions started by an external signed message, the EVM-comparable count'}
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'mc_seqno_head': (head.get('last') or {}).get('seqno'),
                       'blocks_per_unit': (sum(r['blocks'] for r in rows) / k) if k else None},
            'endpoint': tc.base.replace('https://', ''), 'calls': tc.calls,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
