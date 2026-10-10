#!/usr/bin/env python3
"""XRP Ledger: transactions and net transfer value over a window, from a stratified sample of validated ledgers.

Counting. rippled exposes no cumulative transaction counter, so the count is estimated: the window's validated ledgers
(one every ~3.9 s, ~22k a day) are located by close time, a stratified sample of them is read in full (`ledger` with
expanded transactions and metadata), and the total is the sample mean times the ledger count with its standard error.
Every transaction in a validated ledger counts, whatever its result: a `tec`-class failure was applied, paid its fee and
consumed a sequence number. The success share and the mix by type are reported beside the total, because most XRPL
traffic is not payments — OfferCreate/OfferCancel on the native order book, TrustSet, AMM and NFToken operations.

Value. Net per transaction, from the metadata rather than from what a transaction asked for: every successful
transaction's AffectedNodes give each account's balance change per asset — XRP from AccountRoot balances (drops), an
issued currency from RippleState trust lines, an MPT from MPToken amounts — and the transfer value of that transaction
in that asset is the sum of the positive changes (`chain_adapters.net_positive`'s convention). A payment from A to B
counts once, a cross-currency payment that routes back to its sender counts the conversion and not the loop, an
order-book fill counts both assets as a swap does on every other chain here, and the burned fee counts nothing. A
trust-line balance is held from the low account's side, so the holder and the issuer are told apart by the sign of the
balance (a positive balance means the high account owes the low one); the issuer's position moves by the opposite
amount, which is what makes issuance, redemption and holder-to-holder transfers all net correctly. What Payments
*delivered* is kept beside it (`payments_delivered`), read from `meta.delivered_amount` and never from `Amount`: a
partial payment (tfPartialPayment) can name an Amount of 10^15 while delivering a few drops, which is the classic way of
faking an XRPL deposit. MPT amounts are raw units and stay unpriced.

Pricing. XRP through the feed's coingecko id; an issued currency only by (currency, issuer) through DefiLlama's
`ripple:<40-hex currency>.<issuer>` key. The same code from another issuer is a different asset and stays unpriced:
pricing by code alone is how an aggregator reports a $139B "largest transaction" on an ordinary day (Blockchair,
2026-10-09). RLUSD at its canonical issuer falls back to par only if the feed is silent, and the row says so.
"""
import collections
import concurrent.futures as cf
import threading
import time
import urllib.parse

from chain_adapters import Http, HttpError, asset_rows, register, sample_points, stratified_total, window_dict

RIPPLE_EPOCH = 946684800          # XRPL close_time counts seconds from 2000-01-01T00:00:00Z
DROPS_PER_XRP = 1_000_000
DEFAULT_RPC = ['https://xrplcluster.com/', 'https://s1.ripple.com:51234/', 'https://s2.ripple.com:51234/']
SECONDS_PER_LEDGER_SEED = 3.9     # seeds the bracket only; the bisection reads close times
FIRST_LEDGER = 32570              # the oldest ledger any server holds (the history before it was lost in 2013)
MAX_SAMPLES = 200                 # an expanded ledger is ~0.5 MB (~120 kB gzipped)
RETRYABLE = {'slowDown', 'tooBusy', 'noNetwork', 'noCurrent', 'noClosed', 'internal', 'failedToForward'}
CANONICAL_PAR = {
    # (currency as 40 hex, issuer) -> symbol. Checked 2026-10-09: DefiLlama prices this exact key as RLUSD at $0.9998.
    ('524C555344000000000000000000000000000000', 'rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De'): 'RLUSD',
}


class XrplError(Exception):
    def __init__(self, result):
        super().__init__(str(result.get('error_message') or result.get('error') or result)[:200])
        self.code = result.get('error')


class Xrpl:
    """rippled JSON-RPC: {"method", "params": [{...}]}; an error is result.status == 'error', not a JSON-RPC error."""

    def __init__(self, urls, http):
        self.urls = list(urls)
        self.http = http
        self.calls = 0
        self.next = 0
        self.lock = threading.Lock()

    def call(self, method, **params):
        # round robin across the public servers: the per-host spacing in Http then spreads the load instead of queueing
        with self.lock:
            start = self.next
            self.next += 1
        last = None
        for attempt in range(2 * len(self.urls)):
            u = self.urls[(start + attempt) % len(self.urls)]
            try:
                d = self.http.post(u, {'method': method, 'params': [params]})
            except HttpError as e:
                last = e
                continue
            self.calls += 1
            r = (d or {}).get('result') or {}
            if r.get('status') == 'error' or r.get('error'):
                if r.get('error') in RETRYABLE:
                    last = XrplError(r)
                    time.sleep(1 + attempt)
                    continue
                raise XrplError(r)
            return r
        raise last or XrplError({'error': 'all endpoints failed'})


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


def currency_hex(code):
    """A currency code in its 160-bit form: a 3-character standard code sits in bytes 12-14 of 20."""
    if len(code) == 40:
        return code.upper()
    if len(code) == 3:
        return ('00' * 12 + code.encode('ascii').hex() + '00' * 5).upper()
    raise ValueError('bad currency code %r' % code)


def iou_id(code, issuer):
    """'iou:<40-hex currency>.<issuer>' — the asset is the (currency, issuer) pair, never the code alone."""
    try:
        return 'iou:%s.%s' % (currency_hex(code), issuer)
    except (ValueError, UnicodeEncodeError, TypeError):
        return 'iou:%s.%s' % (code, issuer)


def currency_symbol(code):
    """Readable symbol: standard codes as-is, non-standard 40-hex codes as their ASCII (RLUSD), AMM LP tokens as such."""
    if len(code) == 3:
        return code
    try:
        b = bytes.fromhex(code)
    except ValueError:
        return code[:12]
    if len(b) != 20:
        return code[:12]
    if b[0] == 0x00:
        std = b[12:15]
        return std.decode('ascii') if all(32 < c < 127 for c in std) else code[:8]
    if b[0] == 0x03:
        return 'AMM-LP'
    s = b.rstrip(b'\x00')
    return s.decode('ascii') if s and all(32 <= c < 127 for c in s) else code[:8]


def tx_parts(t):
    """(transaction fields, metadata) for an expanded ledger transaction in either API version's shape."""
    if isinstance(t, dict) and 'tx_json' in t:
        return t['tx_json'], t.get('meta') or {}
    if isinstance(t, dict):
        return t, t.get('metaData') or t.get('meta') or {}
    return {}, {}


def delivered(meta):
    """(asset id, amount in units) a successful Payment delivered, or None. Never reads the transaction's Amount."""
    d = meta.get('delivered_amount', meta.get('DeliveredAmount'))
    if d is None or d == 'unavailable':
        return None
    if isinstance(d, str):
        return 'native:XRP', int(d) / DROPS_PER_XRP
    if isinstance(d, dict):
        if d.get('mpt_issuance_id'):
            return 'mpt:%s' % d['mpt_issuance_id'], float(d.get('value') or 0)
        cur, iss = d.get('currency'), d.get('issuer')
        if cur and iss:
            return iou_id(cur, iss), float(d.get('value') or 0)
    return None


def balance_changes(meta):
    """{asset id: {account: change in units}} for one transaction, from its AffectedNodes."""
    ch = {}

    def add(asset, acct, v):
        if v:
            d = ch.setdefault(asset, {})
            d[acct] = d.get(acct, 0) + v

    for node in meta.get('AffectedNodes') or []:
        for kind, n in node.items():
            et = n.get('LedgerEntryType')
            new = n.get('NewFields') or {}
            fin = n.get('FinalFields') or new
            prev = n.get('PreviousFields') or {}
            if et == 'AccountRoot':
                if kind == 'CreatedNode':
                    d = int(new.get('Balance') or 0)
                elif 'Balance' in prev:
                    d = int(fin.get('Balance') or 0) - int(prev['Balance'])
                else:
                    continue
                add('native:XRP', fin.get('Account'), d / DROPS_PER_XRP)
            elif et == 'RippleState':
                if kind == 'CreatedNode':
                    b0 = 0.0
                elif 'Balance' in prev:
                    b0 = float(prev['Balance']['value'])
                else:
                    continue
                bal = fin.get('Balance') or {}
                b1 = float(bal.get('value') or 0)
                d = b1 - b0
                if not d:
                    continue
                low, high = (fin.get('LowLimit') or {}).get('issuer'), (fin.get('HighLimit') or {}).get('issuer')
                ref = b1 if b1 else b0
                # positive: the high account owes the low one, so low holds high's currency; negative: the reverse
                holder, issuer, h = (low, high, d) if ref > 0 else (high, low, -d)
                cur = bal.get('currency') or (fin.get('LowLimit') or {}).get('currency')
                asset = iou_id(cur, issuer)
                add(asset, holder, h)
                add(asset, issuer, -h)
            elif et == 'MPToken':
                if kind == 'CreatedNode':
                    a0 = 0
                elif 'MPTAmount' in prev:
                    a0 = int(prev['MPTAmount'])
                else:
                    continue
                d = int(fin.get('MPTAmount') or 0) - a0
                if d:
                    asset = 'mpt:%s' % fin.get('MPTokenIssuanceID')
                    add(asset, fin.get('Account'), d)
                    add(asset, 'issuer:' + str(fin.get('MPTokenIssuanceID')), -d)
    return ch


def net_moved(changes):
    """Transfer value per asset of one transaction: the sum of every account's positive change."""
    return {a: sum(v for v in accts.values() if v > 0) for a, accts in changes.items()}


def reduce_ledger(L):
    """Per-ledger sums: transaction count, successes, type mix, net value per asset, and what Payments delivered."""
    txs = L.get('transactions') or []
    types = collections.Counter()
    assets, delivered_by = {}, {}
    ok = 0
    for t in txs:
        tx, meta = tx_parts(t)
        ty = tx.get('TransactionType') or '?'
        types[ty] += 1
        if meta.get('TransactionResult') != 'tesSUCCESS':
            continue
        ok += 1
        for a, v in net_moved(balance_changes(meta)).items():
            if v > 0:
                e = assets.setdefault(a, [0, 0.0, 0.0])
                e[0] += 1
                e[1] += v
                if ty == 'Payment':
                    e[2] += v
        if ty == 'Payment':
            d = delivered(meta)
            if d and d[1] > 0:
                e = delivered_by.setdefault(d[0], [0, 0.0])
                e[0] += 1
                e[1] += d[1]
    return {'n': len(txs), 'ok': ok, 'types': dict(types), 'assets': assets, 'delivered': delivered_by,
            'ts': int(L.get('close_time') or 0) + RIPPLE_EPOCH, 'index': int(L.get('ledger_index') or 0)}


def iou_parts(asset):
    hexcode, issuer = asset[4:].split('.', 1)
    return hexcode, issuer


@register('xrpl')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    http = Http(min_interval=p.get('min_interval', 0.15), timeout=p.get('timeout', 60))
    x = Xrpl(p.get('rpc') or DEFAULT_RPC, http)
    head_l = x.call('ledger', ledger_index='validated', transactions=False, expand=False)['ledger']
    head, head_ts = int(head_l['ledger_index']), int(head_l['close_time']) + RIPPLE_EPOCH
    end_ts = min(ctx.end_ts, head_ts)
    cache = {head: head_ts}

    def ts_of(i):
        if i not in cache:
            L = x.call('ledger', ledger_index=int(i), transactions=False, expand=False)['ledger']
            cache[i] = int(L['close_time']) + RIPPLE_EPOCH
        return cache[i]

    first = locate(ctx.start_ts, FIRST_LEDGER, head, head_ts, SECONDS_PER_LEDGER_SEED, ts_of)
    last = head if end_ts >= head_ts else locate(end_ts, first, head, head_ts, SECONDS_PER_LEDGER_SEED, ts_of) - 1
    N = last - first + 1
    n_samples = min(int(p.get('samples') or ctx.samples), MAX_SAMPLES)
    pts = sample_points(first, last, n_samples, seed=int(ctx.start_ts))

    def fetch(i):
        try:
            L = x.call('ledger', ledger_index=int(i), transactions=True, expand=True, api_version=2)['ledger']
            return i, reduce_ledger(L)
        except Exception as e:
            return i, {'error': str(e)[:160]}

    with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 8))) as ex:
        got = list(ex.map(fetch, pts))
    units = [r for _, r in got if 'error' not in r]
    errors = ['ledger %d: %s' % (i, r['error']) for i, r in got if 'error' in r]
    n = len(units)
    count, se = stratified_total([u['n'] for u in units], N)
    ok_total = sum(u['ok'] for u in units)
    all_total = sum(u['n'] for u in units)
    type_tot = collections.Counter()
    for u in units:
        type_tot.update(u['types'])
    by_type = {}
    for ty, _ in type_tot.most_common(14):
        est, _se = stratified_total([u['types'].get(ty, 0) for u in units], N)
        by_type[ty] = round(est or 0)
    offers = type_tot.get('OfferCreate', 0) + type_tot.get('OfferCancel', 0)
    secs = max(1, end_ts - ctx.start_ts)
    tx = {'count': count, 'se': se, 'method': 'sampled-blocks', 'unit': 'ledger', 'blocks': N, 'sampled': n,
          'success_share': (ok_total / all_total) if all_total else None,
          'order_book_share': (offers / all_total) if all_total else None,
          'by_type': by_type, 'tps': (count / secs) if count is not None else None,
          'note': 'every transaction in a validated ledger, any result (tec-class failures are applied and pay a fee); '
                  'no cumulative counter exists, so this is a stratified sample of ledgers'}

    # ------------------------------------------------------------------ price what moved
    per_asset, pay_share, delivered_tot = {}, {}, {}
    for i, u in enumerate(units):
        for a, (c, amt, amt_pay) in u['assets'].items():
            d = per_asset.setdefault(a, {'count': [0] * n, 'amount': [0.0] * n})
            d['count'][i] += c
            d['amount'][i] += amt
            pay_share[a] = pay_share.get(a, 0.0) + amt_pay
        for a, (c, amt) in u['delivered'].items():
            d = delivered_tot.setdefault(a, {'count': [0] * n, 'amount': [0.0] * n})
            d['count'][i] += c
            d['amount'][i] += amt
    nat_key = 'coingecko:%s' % ((cfg.get('native') or {}).get('coingecko') or 'ripple')
    everything = set(per_asset) | set(delivered_tot)
    ious = [a for a in everything if a.startswith('iou:')]
    keys = {}
    for a in ious:
        hexcode, issuer = iou_parts(a)
        cands = ['ripple:%s.%s' % (hexcode, issuer)]
        sym = currency_symbol(hexcode)
        if hexcode.startswith('00') and len(sym) == 3:
            cands.append('ripple:%s.%s' % (sym, issuer))
        keys[a] = cands
    pr = ctx.prices.get([nat_key] + [k for ks in keys.values() for k in ks])
    meta, price_of, source = {}, {}, {}
    for a in everything:
        if a == 'native:XRP':
            meta[a] = {'symbol': 'XRP', 'decimals': 6}
            q = pr.get(nat_key)
            price_of[a] = q.get('price') if q else None
            source[a] = 'defillama' if q else None
        elif a.startswith('iou:'):
            hexcode, issuer = iou_parts(a)
            meta[a] = {'symbol': currency_symbol(hexcode), 'decimals': None}
            q = next((pr.get(k) for k in keys[a] if pr.get(k)), None)
            if q:
                price_of[a], source[a] = q.get('price'), 'defillama'
                meta[a]['symbol'] = q.get('symbol') or meta[a]['symbol']
            elif (hexcode, issuer) in CANONICAL_PAR:
                price_of[a], source[a] = 1.0, 'par-canonical-issuer'
                meta[a]['symbol'] = CANONICAL_PAR[(hexcode, issuer)]
            else:
                price_of[a], source[a] = None, None
        else:
            meta[a] = {'symbol': 'MPT:' + a[4:12], 'decimals': None}
            price_of[a], source[a] = None, None
    tr = asset_rows(per_asset, n, N, meta, price_of, native_symbols=['XRP'])
    for r in tr['assets'] + tr['unpriced_top']:
        r['price_source'] = source.get(r['asset'])
        tot = sum(per_asset[r['asset']]['amount'])
        r['payment_share'] = (pay_share.get(r['asset'], 0.0) / tot) if tot else None
        if r['asset'].startswith('iou:'):
            r['currency'], r['issuer'] = iou_parts(r['asset'])
        elif r['asset'].startswith('mpt:'):
            r['note'] = 'raw MPT units (AssetScale not applied)'
    dl = asset_rows(delivered_tot, n, N, meta, price_of, native_symbols=['XRP']) if delivered_tot else None
    tr['payments_delivered'] = ({'priced_usd': dl['priced_usd'],
                                 'assets': [{k: r[k] for k in ('asset', 'symbol', 'transfers', 'amount', 'usd', 'usd_se')}
                                            for r in dl['assets'][:10]]} if dl else None)
    priced_pay = sum((r['usd'] or 0) * (r['payment_share'] or 0) for r in tr['assets'])
    tr['payment_tx_share_of_usd'] = (priced_pay / tr['priced_usd']) if tr['priced_usd'] else None
    tr['method'] = ('sampled-blocks (net per transaction from metadata balance changes, every successful transaction; '
                    'payments_delivered = Payment delivered_amount)')
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'head': head},
            'endpoint': ','.join(urllib.parse.urlsplit(u).netloc for u in x.urls), 'calls': x.calls,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
