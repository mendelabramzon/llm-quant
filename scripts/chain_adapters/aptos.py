#!/usr/bin/env python3
"""Aptos: an exact transaction count from ledger versions, the system share and the transfer value from a stratified
sample of blocks, over the public REST API.

Counting. Every Aptos transaction has a version, versions are dense, and a block names its first and last, so the
number of transactions between two blocks is one subtraction — exact, including the protocol's own. Those are not
activity: each block opens with a `block_metadata_transaction` and closes with a `block_epilogue_transaction` (state
checkpoints and validator transactions are rarer), and at ~40 blocks a second most blocks hold nothing else, so system
transactions are about half of all versions. The headline is therefore user transactions: the exact version count
minus the system transactions per block measured in the sampled blocks and scaled to the window's block count. Because
the system count per block barely varies, the subtraction is nearly exact, and its standard error says how nearly.
Aptos Labs' own explorer analytics (`daily_user_transactions`, a separate pipeline) is the independent check for a
complete UTC day (`--day`).

Value. For each successful user transaction in a sampled block, every `0x1::fungible_asset::Deposit` and `Withdraw`
is netted per store within the transaction, and the positive nets are summed per asset (the `net_positive`
convention: a router or a flash loan repaid in full nets to zero; a transfer counts once; a swap counts both legs). A
store is attributed to its asset through the transaction's write set, which carries the store's `FungibleStore`
resource with its `metadata` (concurrent stores, whose balance lives in a separate resource, are looked up once and
cached). Legacy `0x1::coin::CoinDeposit`/`CoinWithdraw` events name their coin type and account directly, and the
older guid-based `DepositEvent`/`WithdrawEvent` are mapped through the CoinStore handles in the write set. Every
deposit is also summed un-netted as `gross`. Assets are priced through DefiLlama as
`aptos:<FA metadata address or coin type>`.

Limits. Fullnodes prune: the public API keeps ~10 days of versions (`oldest_ledger_version`), so a window older than
that fails with a clear error rather than a partial count.
"""
import concurrent.futures as cf
import time

from chain_adapters import ROOT, Http, HttpError, asset_rows, register, sample_points, stratified_total, window_dict
from chain_adapters._search import seeded_bracket

REST = 'https://api.mainnet.aptoslabs.com/v1'
SYSTEM_TYPES = {'block_metadata_transaction', 'block_epilogue_transaction', 'state_checkpoint_transaction',
                'validator_transaction', 'genesis_transaction'}
FA_DEPOSIT = '0x1::fungible_asset::Deposit'
FA_WITHDRAW = '0x1::fungible_asset::Withdraw'
COIN_DEPOSIT = '0x1::coin::CoinDeposit'
COIN_WITHDRAW = '0x1::coin::CoinWithdraw'
COIN_DEPOSIT_LEGACY = '0x1::coin::DepositEvent'
COIN_WITHDRAW_LEGACY = '0x1::coin::WithdrawEvent'
FA_STORE = '0x1::fungible_asset::FungibleStore'
COIN_STORE_PREFIX = '0x1::coin::CoinStore<'
MAX_STORE_LOOKUPS = 40      # FungibleStore resources read to resolve deposits whose store the write set did not carry
DEFAULT_SAMPLES = 80        # blocks read in full: ~600 compute units each against an anonymous 40,000 per 300 s
PATIENCE_S = 300            # how long one request may wait out a 429 before the probe gives up on it
KEY_FILE = 'aptos_api_key.txt'   # optional Aptos Build key (gitignored), sent as a Bearer token


def norm_addr(a):
    """Canonical Aptos address (AIP-40): special addresses 0x0..0xf short, everything else 64 hex digits."""
    h = (a or '').lower()
    h = h[2:] if h.startswith('0x') else h
    h = h.lstrip('0') or '0'
    return '0x' + h if len(h) == 1 else '0x' + h.rjust(64, '0')


class Rest:
    """The fullnode REST API with patience: Aptos Labs meters anonymous callers at 40,000 compute units per rolling
    300 s per IP (the indexer GraphQL shares the budget), a block with its transactions costs a few hundred units, and
    the answer to overspending is a 429 with no Retry-After. So a 429 is waited out in 15 s steps for up to
    PATIENCE_S, and an Aptos Build key in `aptos_api_key.txt` (gitignored, never written out) lifts the limit."""

    def __init__(self, base, http, key=None):
        self.base, self.http = base.rstrip('/'), http
        self.headers = {'Authorization': 'Bearer ' + key} if key else None
        self.requests = 0
        self.waited = 0.0

    def get(self, path, params=None):
        deadline = time.monotonic() + PATIENCE_S
        while True:
            self.requests += 1
            try:
                return self.http.get(self.base + path, params, headers=self.headers)
            except HttpError as e:
                if e.code != 429 or time.monotonic() > deadline:
                    raise
                time.sleep(15)
                self.waited += 15

    def block(self, h, txs=False):
        return self.get('/blocks/by_height/%d' % h, {'with_transactions': 'true'} if txs else None)


def api_key():
    f = ROOT / KEY_FILE
    try:
        k = f.read_text().strip() if f.exists() else ''
    except OSError:
        k = ''
    return k or None


def block_at(rest, ts_us, head_h, head_ts_us, rate, floor):
    """First block height whose block_timestamp (µs) is >= ts_us: a rate-seeded bracket, then plain bisection.

    Bisection, not a parallel k-ary search, because every read is metered: ~20 header reads per boundary is the
    cheapest way to the answer, and the time it costs (a few seconds) is not the binding constraint here.
    """
    cache = {}

    def ts_of(h):
        if h not in cache:
            b = _safe(rest.block, h) if floor <= h <= head_h else None
            cache[h] = int(b['block_timestamp']) if b else None
        return cache[h]
    lo, hi = seeded_bracket(ts_of, ts_us, head_h, head_ts_us, rate / 1e6, floor=floor)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        v = ts_of(mid)
        if v is None:            # unreadable (pruned on the node that answered): step past it
            v = ts_of(mid + 1)
            if v is None:
                break
        if v >= ts_us:
            hi = mid
        else:
            lo = mid
    return hi


def _safe(fn, *a):
    try:
        return fn(*a)
    except HttpError:
        return None


def block_transactions(rest, b):
    """A block's transactions, completed through /transactions if the block listing was truncated."""
    txs = list(b.get('transactions') or [])
    first, last = int(b['first_version']), int(b['last_version'])
    want = last - first + 1
    while len(txs) < want:
        start = first + len(txs)
        more = rest.get('/transactions', {'start': start, 'limit': min(100, want - len(txs))})
        if not more:
            break
        txs += more
    return txs[:want]


def coin_store_guids(changes):
    """{(account, creation_num): (coin type, 'deposit' | 'withdraw')} for the legacy CoinStore event handles a write set carries."""
    out = {}
    for c in changes or []:
        if c.get('type') != 'write_resource':
            continue
        d = c.get('data') or {}
        rtype = d.get('type') or ''
        if not rtype.startswith(COIN_STORE_PREFIX):
            continue
        ct = rtype[len(COIN_STORE_PREFIX):-1]
        for field, side in (('deposit_events', 'deposit'), ('withdraw_events', 'withdraw')):
            gid = ((((d.get('data') or {}).get(field)) or {}).get('guid') or {}).get('id') or {}
            if gid:
                out[(norm_addr(gid.get('addr') or c.get('address')), str(gid.get('creation_num')))] = (ct, side)
    return out


def tx_moves(t):
    """One successful user transaction -> ({holder: net raw change}, {holder: asset or None}, deposit events, gross).

    A holder is a fungible store (FA) or an (account, coin type) pair (legacy coins). Deposits add and withdrawals
    subtract, so a store that receives and forwards the same amount in one transaction (a router, a flash loan repaid
    in full) nets to zero. `asset` is known for every coin holder and for every store whose `FungibleStore` resource is
    in the write set; the rest are resolved later by a resource read.
    """
    stores = {}
    for c in t.get('changes') or []:
        if c.get('type') != 'write_resource':
            continue
        d = c.get('data') or {}
        if (d.get('type') or '') == FA_STORE:
            meta = (((d.get('data') or {}).get('metadata')) or {}).get('inner')
            if meta:
                stores[norm_addr(c.get('address'))] = norm_addr(meta)
    guids = None
    net, asset_of, deposits, gross = {}, {}, {}, {}
    for e in t.get('events') or []:
        et, data = e.get('type'), e.get('data') or {}
        amt = int(data.get('amount') or 0)
        if amt <= 0:
            continue
        if et in (FA_DEPOSIT, FA_WITHDRAW):
            holder = ('fa', norm_addr(data.get('store')))
            asset_of.setdefault(holder, stores.get(holder[1]))
            sign = 1 if et == FA_DEPOSIT else -1
        elif et in (COIN_DEPOSIT, COIN_WITHDRAW):
            holder = ('coin', norm_addr(data.get('account')), data.get('coin_type'))
            asset_of[holder] = data.get('coin_type')
            sign = 1 if et == COIN_DEPOSIT else -1
        elif et in (COIN_DEPOSIT_LEGACY, COIN_WITHDRAW_LEGACY):
            if guids is None:
                guids = coin_store_guids(t.get('changes'))
            g = e.get('guid') or {}
            hit = guids.get((norm_addr(g.get('account_address')), str(g.get('creation_number'))))
            if not hit:
                continue
            holder = ('coin', norm_addr(g.get('account_address')), hit[0])
            asset_of[holder] = hit[0]
            sign = 1 if et == COIN_DEPOSIT_LEGACY else -1
        else:
            continue
        net[holder] = net.get(holder, 0) + sign * amt
        if sign > 0:
            deposits[holder] = deposits.get(holder, 0) + 1
            gross[holder] = gross.get(holder, 0) + amt
    return net, asset_of, deposits, gross


def reduce_block(txs):
    """Counts by type and, over successful user transactions, the *net* value each asset moved.

    Returns {'n_all', 'n_user', 'n_system', 'n_fail', 'assets': {asset: [deposits, net raw, gross raw]},
    'unresolved': {store: [deposits, net raw, gross raw]}} where an asset is a normalised FA metadata address or a
    coin type. Net is the sum of every holder's positive net change within each transaction (the convention of
    `chain_adapters.net_positive`); gross is every deposit. `unresolved` holds stores the write set did not describe.
    """
    out = {'n_all': len(txs), 'n_user': 0, 'n_system': 0, 'n_fail': 0, 'assets': {}, 'unresolved': {}}
    for t in txs:
        ty = t.get('type')
        if ty != 'user_transaction':
            out['n_system'] += 1          # SYSTEM_TYPES, and anything newer the API adds
            continue
        out['n_user'] += 1
        if not t.get('success'):
            out['n_fail'] += 1
            continue
        net, asset_of, deposits, gross = tx_moves(t)
        for holder in set(net) | set(gross):
            asset = asset_of.get(holder)
            bucket, key = (out['assets'], asset) if asset else (out['unresolved'], holder[1])
            v = bucket.setdefault(key, [0, 0, 0])
            v[0] += deposits.get(holder, 0)
            v[1] += max(0, net.get(holder, 0))
            v[2] += gross.get(holder, 0)
    return out


def resolve_stores(rest, stores, cache):
    """{store: metadata} for FungibleStore objects, read once each (bounded) and cached across blocks."""
    todo = [s for s in stores if s not in cache][:MAX_STORE_LOOKUPS]

    def one(s):
        try:
            r = rest.get('/accounts/%s/resource/%s' % (s, FA_STORE))
            return s, norm_addr((((r or {}).get('data') or {}).get('metadata') or {}).get('inner'))
        except HttpError:
            return s, None
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for s, m in ex.map(one, todo):
            cache[s] = m if m and m != '0x0' else None
    return cache


def explorer_daily(http, day):
    """Aptos Labs' explorer analytics: user transactions for one complete UTC day, or None."""
    try:
        d = http.get('https://storage.googleapis.com/aptos-mainnet/explorer/chain_stats_v2.json')
    except HttpError:
        return None
    for row in d.get('daily_user_transactions') or []:
        if row.get('date') == day:
            return int(row.get('num_user_transactions'))
    return None


@register('aptos')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    http = Http(min_interval=p.get('min_interval', 0.1), timeout=p.get('timeout', 60))
    key = api_key()
    rest = Rest(p.get('rest') or REST, http, key=key)
    notes, errors = [], []
    info = rest.get('')
    head_h, head_ts = int(info['block_height']), int(info['ledger_timestamp'])
    oldest_h = int(info.get('oldest_block_height') or 0)
    back = rest.block(head_h - 20000)
    rate = 20000 / max(1e-6, (head_ts - int(back['block_timestamp'])) / 1e6)      # blocks per second
    end_us = min(int(ctx.end_ts * 1e6), head_ts)
    start_us = int(ctx.start_ts * 1e6)
    # the gateway balances across nodes that prune at different heights, so the advertised oldest block may already be
    # gone; require the window to start comfortably (an hour) inside the advertised range rather than at its edge
    oldest_ts_est = head_ts - (head_h - oldest_h) / rate * 1e6
    if start_us < oldest_ts_est + 3600e6:
        raise RuntimeError('window starts within an hour of (or before) the oldest unpruned block %d (~%s); '
                           'the public fullnode keeps ~%.1f days' % (oldest_h, window_dict(oldest_ts_est / 1e6, oldest_ts_est / 1e6)['start_utc'],
                                                                     (head_ts - oldest_ts_est) / 86400e6))
    first = block_at(rest, start_us, head_h, head_ts, rate, oldest_h + 1)
    last = head_h if end_us >= head_ts else block_at(rest, end_us, head_h, head_ts, rate, oldest_h + 1) - 1
    bf, bl = rest.block(first), rest.block(last)
    versions = int(bl['last_version']) - int(bf['first_version']) + 1
    N = last - first + 1

    # a full block costs ~600 of the anonymous 40,000 compute units per 300 s, so without a key the sample is capped
    n_samples = int(p.get('samples') or (ctx.samples if key else min(ctx.samples, DEFAULT_SAMPLES)))
    hs = sample_points(first, last, n_samples, seed=int(ctx.start_ts))

    def fetch(h):
        for attempt in range(3):
            try:
                b = rest.block(h, txs=True)
                return h, reduce_block(block_transactions(rest, b)), None
            except HttpError as e:
                err = str(e)[:120]
                time.sleep(1.0 + attempt)
        return h, None, err

    units, unit_h = [], []
    with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 4 if key else 3))) as ex:
        for h, u, err in ex.map(fetch, hs):
            if u is None:
                errors.append('block %d: %s' % (h, err))
                continue
            units.append(u)
            unit_h.append(h)
    n = len(units)
    system_est, system_se = stratified_total([u['n_system'] for u in units], N)
    user_blocks, user_blocks_se = stratified_total([u['n_user'] for u in units], N)
    users = versions - system_est if system_est is not None else None
    n_user_s = sum(u['n_user'] for u in units)
    day = None
    if ctx.end_ts - ctx.start_ts == 86400 and ctx.start_ts % 86400 == 0:
        import datetime as dt
        day = dt.datetime.fromtimestamp(ctx.start_ts, dt.timezone.utc).strftime('%Y-%m-%d')
    explorer = explorer_daily(http, day) if day else None
    tx = {'count': users, 'se': system_se, 'method': 'exact-versions minus sampled system share',
          'all_versions': versions, 'all_versions_method': 'exact-counter', 'cumulative_total': int(bl['last_version']) + 1,
          'system_est': system_est, 'system_per_block': (system_est / N) if system_est is not None and N else None,
          'user_from_blocks': user_blocks, 'user_from_blocks_se': user_blocks_se,
          'failed_share': (sum(u['n_fail'] for u in units) / n_user_s) if n_user_s else None,
          'blocks': N, 'sampled': n,
          'crosscheck': ({'source': 'aptos explorer analytics (daily_user_transactions)', 'day': day,
                          'user_transactions': explorer,
                          'ratio': (users / explorer) if (users and explorer) else None} if day else None),
          'note': 'user transactions; block metadata, epilogue, state-checkpoint and validator transactions excluded'}

    # ------------------------------------------------------------------ resolve stores, price, scale
    weight = {}
    for u in units:
        for st, v in u['unresolved'].items():
            weight[st] = weight.get(st, 0) + v[0]
    cache = resolve_stores(rest, sorted(weight, key=lambda st: -weight[st]), {})
    raw = {}
    lost = 0
    for i, u in enumerate(units):
        merged = dict((k, list(v)) for k, v in u['assets'].items())
        for st, (cnt, net, gross) in u['unresolved'].items():
            meta = cache.get(st)
            if not meta:
                lost += cnt
                continue
            e = merged.setdefault(meta, [0, 0, 0])
            e[0] += cnt
            e[1] += net
            e[2] += gross
        for a, (cnt, net, gross) in merged.items():
            d = raw.setdefault(a, {'count': [0] * n, 'net': [0] * n, 'gross': [0] * n})
            d['count'][i] += cnt
            d['net'][i] += net
            d['gross'][i] += gross
    if lost:
        notes.append('%d sampled deposits into stores that could not be resolved to an asset' % lost)
    key = ((cfg.get('ids') or {}).get('llama_key')) or 'aptos'
    pr = ctx.prices.get(['%s:%s' % (key, a) for a in raw])
    meta, price_of, per_asset = {}, {}, {}
    for a, d in raw.items():
        q = pr.get('%s:%s' % (key, a))
        dec = (q or {}).get('decimals')
        meta[a] = {'symbol': (q or {}).get('symbol') or (a.split('::')[-1] if '::' in a else None), 'decimals': dec}
        if q and dec is not None:
            price_of[a] = q.get('price')
        scale = 10 ** int(dec) if dec is not None else None
        per_asset[a] = {'count': d['count'], 'amount': [(x / scale) if scale else 0.0 for x in d['net']],
                        'gross': [(x / scale) if scale else 0.0 for x in d['gross']]}
    tr = asset_rows(per_asset, n, N, meta, price_of, native_symbols=[(cfg.get('native') or {}).get('symbol') or 'APT'])
    tr['method'] = ('sampled-blocks (fungible-asset and coin deposit/withdraw events of successful user transactions, '
                    'netted per store or account within each transaction)')
    tr['unresolved_deposits_sampled'] = lost
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_us / 1e6),
            'blocks': {'first': first, 'last': last, 'head': head_h, 'oldest_available': oldest_h,
                       'blocks_per_second': rate},
            'endpoint': (p.get('rest') or REST).split('/')[2], 'calls': rest.requests,
            'rate_limit_wait_s': rest.waited, 'api_key': bool(key), 'notes': notes,
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
