#!/usr/bin/env python3
"""Cardano: exact transaction counts from every block in the window, ADA value from a block sample, and native-token
value from a smaller transaction-level sample — all through the public Koios API.

Counting. `/blocks?block_time=gte.S&block_time=lt.E` lists every block in the window with its `tx_count` (~4,300 blocks
a day, paged 1,000 at a time), so the count is exact (`exact-blocks`). Cardano has no system transactions: every
transaction in a block was signed by a user or a script batcher, so all of them count.

Value, and why it is netted. An eUTXO transaction spends whole outputs and returns the change to the sender, so summing
outputs ("gross") counts the change as if it had moved. The headline `amount` is therefore NET per transaction: for each
transaction, every wallet's outputs minus its inputs, per asset, positive part summed (the same quantity as the package's
`net_positive`). A wallet is its stake key where the address has one — change usually goes to a fresh address under the
same stake key, and keying on the address alone would miss it — and the payment address otherwise. That needs every
input, which only `/tx_info` gives (~5 s per 50 transactions on the public tier), so:

* native tokens (USDM, DJED, iUSD, SNEK, NIGHT, …) come from `/tx_info` on every transaction of a few sampled blocks
  (`token_blocks`, default 12), net and gross both, priced through DefiLlama as `cardano:<policy id><asset name hex>`;
* ADA comes from `/block_info`'s `total_output` (gross, change included) on a stratified sample of ~200 blocks, scaled
  by the net/gross ratio measured on the transaction-level blocks (a ratio estimator: the level from the large sample,
  the netting from the small one; the reported standard error does not include the ratio's own uncertainty).

The token sample is small and its standard errors say so; `units_seen` is how many sampled blocks an asset was in.
Koios returns no rows for the very newest transactions' inputs; a transaction that came back without inputs is left out
of the netting rather than counted as all-output.
"""
import concurrent.futures as cf
import json
import time

from chain_adapters import Http, HttpError, asset_rows, register, sample_points, stratified_total, window_dict

KOIOS = 'https://api.koios.rest/api/v1'
PAGE = 1000
INFO_BATCH = 50              # block hashes per /block_info call
TX_BATCH = 50                # tx hashes per /tx_info call (~5 s each with inputs on the public tier)
TOKEN_BLOCKS = 12           # ~1,100 transactions a day-window; the ADA net/gross ratio swings 0.03-0.5 block to block
MIN_ADA_SAMPLE = 200
LOVELACE = 'lovelace'


def _assets(o):
    al = o.get('asset_list') or []
    if isinstance(al, str):              # some Koios fields arrive JSON-encoded
        try:
            al = json.loads(al)
        except ValueError:
            al = []
    return al


def wallet(o):
    return o.get('stake_addr') or (o.get('payment_addr') or {}).get('bech32')


def fold_txs(tx_infos):
    """Per block: gross outputs and net-per-transaction value, for ADA and for every native asset.

    Returns {'txs', 'netted', 'lovelace_gross', 'lovelace_net', 'assets': {id: {'gross', 'net', 'outputs', 'decimals'}}}.
    A transaction without inputs (Koios answered none) contributes to gross but not to net or to `netted`.
    """
    out = {'txs': 0, 'netted': 0, 'lovelace_gross': 0, 'lovelace_net': 0, 'lovelace_gross_netted': 0, 'assets': {}}
    for t in tx_infos or []:
        out['txs'] += 1
        has_inputs = bool(t.get('inputs'))
        delta = {}
        gross_l = 0
        for side, sign in (('inputs', -1), ('outputs', 1)):
            for o in t.get(side) or []:
                w = wallet(o)
                try:
                    v = int(o.get('value') or 0)
                except (TypeError, ValueError):
                    v = 0
                delta[(w, LOVELACE)] = delta.get((w, LOVELACE), 0) + sign * v
                if sign > 0:
                    gross_l += v
                for a in _assets(o):
                    aid = (a.get('policy_id') or '') + (a.get('asset_name') or '')
                    try:
                        q = int(a.get('quantity') or 0)
                    except (TypeError, ValueError):
                        q = 0
                    delta[(w, aid)] = delta.get((w, aid), 0) + sign * q
                    if sign > 0:
                        e = out['assets'].setdefault(aid, {'gross': 0, 'net': 0, 'outputs': 0, 'decimals': a.get('decimals')})
                        e['gross'] += q
                        e['outputs'] += 1
                        if e['decimals'] is None:
                            e['decimals'] = a.get('decimals')
        out['lovelace_gross'] += gross_l
        if not has_inputs:
            continue
        out['netted'] += 1
        out['lovelace_gross_netted'] += gross_l
        for (w, aid), d in delta.items():
            if d <= 0:
                continue
            if aid == LOVELACE:
                out['lovelace_net'] += d
            else:
                out['assets'].setdefault(aid, {'gross': 0, 'net': 0, 'outputs': 0, 'decimals': None})['net'] += d
    return out


def merge_rows(a, b):
    """Merge two asset_rows() results computed over different samples of the same window."""
    out = {'assets': sorted(a['assets'] + b['assets'], key=lambda r: -(r['usd'] or 0)),
           'unpriced_top': sorted(a['unpriced_top'] + b['unpriced_top'], key=lambda r: -(r['transfers'] or 0))[:25],
           'unpriced_assets': a['unpriced_assets'] + b['unpriced_assets'],
           'unpriced_transfers': a['unpriced_transfers'] + b['unpriced_transfers'],
           'priced_usd': a['priced_usd'] + b['priced_usd'], 'usd_by_class': dict(a['usd_by_class'])}
    for k, v in b['usd_by_class'].items():
        out['usd_by_class'][k] = out['usd_by_class'].get(k, 0.0) + v
    if 'gross_priced_usd' in a or 'gross_priced_usd' in b:
        out['gross_priced_usd'] = a.get('gross_priced_usd', 0.0) + b.get('gross_priced_usd', 0.0)
    return out


def all_blocks(http, api, start_ts, end_ts):
    rows, off = [], 0
    while True:
        page = http.get('%s/blocks?block_time=gte.%d&block_time=lt.%d&select=block_height,tx_count,block_time,hash'
                        '&order=block_height.asc&limit=%d&offset=%d' % (api, start_ts, end_ts, PAGE, off)) or []
        rows += page
        if len(page) < PAGE:
            return rows
        off += PAGE


def ascii_name(hexname):
    try:
        s = bytes.fromhex(hexname).decode('utf-8')
        return s if s.isprintable() and s else None
    except (ValueError, UnicodeDecodeError):
        return None


@register('cardano')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    api = (p.get('koios') or KOIOS).rstrip('/')
    http = Http(min_interval=float(p.get('min_interval', 0.25)), timeout=120)
    errors, notes = [], []
    blocks = all_blocks(http, api, ctx.start_ts, ctx.end_ts)
    N = len(blocks)
    tx_count = sum(b.get('tx_count') or 0 for b in blocks)

    # ------------------------------------------------------------------ ADA level: block_info over a stratified sample
    n_ada = min(N, max(int(p.get('samples') or ctx.samples), MIN_ADA_SAMPLE))
    idx = sample_points(0, N - 1, n_ada, seed=int(ctx.start_ts)) if N else []
    sample = [blocks[i] for i in idx]
    info = {}
    for i in range(0, len(sample), INFO_BATCH):
        part = [b['hash'] for b in sample[i:i + INFO_BATCH]]
        try:
            for r in http.post(api + '/block_info', {'_block_hashes': part}) or []:
                info[r['hash']] = r
        except HttpError as e:
            errors.append('block_info: %s' % str(e)[:100])
    ada_units = [b for b in sample if b['hash'] in info]
    gross_ada = [int(info[b['hash']].get('total_output') or 0) / 1e6 for b in ada_units]
    fees = [int(info[b['hash']].get('total_fees') or 0) / 1e6 for b in ada_units]
    nat = cfg.get('native') or {}
    nat_key = 'coingecko:%s' % (nat.get('coingecko') or 'cardano')

    # ------------------------------------------------------------------ netting: every transaction of a few blocks
    k = min(len(ada_units), int(p.get('token_blocks', TOKEN_BLOCKS)))
    tok_units = [ada_units[int(j * len(ada_units) / k)] for j in range(k)] if k else []
    per_block = []
    if tok_units:
        by_block = {}
        try:
            for x in http.post(api + '/block_txs', {'_block_hashes': [b['hash'] for b in tok_units]}) or []:
                by_block.setdefault(x['block_hash'], []).append(x['tx_hash'])
        except HttpError as e:
            errors.append('block_txs: %s' % str(e)[:100])
        hashes = [h for b in tok_units for h in by_block.get(b['hash'], [])]
        parts = [hashes[i:i + TX_BATCH] for i in range(0, len(hashes), TX_BATCH)]

        def info_part(part):
            try:
                return http.post(api + '/tx_info', {'_tx_hashes': part, '_inputs': True, '_metadata': False,
                                                    '_assets': True, '_withdrawals': False, '_certs': False,
                                                    '_scripts': False, '_bytecode': False}) or []
            except HttpError as e:
                errors.append('tx_info: %s' % str(e)[:100])
                return []

        # each call is ~5 s of server time on the public tier, so three run at once (still paced by min_interval)
        with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 3))) as ex:
            txs = [t for part in ex.map(info_part, parts) for t in part]
        tx_by_block = {}
        for t in txs:
            tx_by_block.setdefault(t.get('block_hash'), []).append(t)
        for b in tok_units:
            got, want = tx_by_block.get(b['hash'], []), len(by_block.get(b['hash'], []))
            if len(got) < want:
                errors.append('tx_info %s: %d of %d transactions returned' % (b['hash'][:12], len(got), want))
            f = fold_txs(got)
            f['requested'] = want
            per_block.append(f)
    g_net = sum(f['lovelace_gross_netted'] for f in per_block)
    ratio = (sum(f['lovelace_net'] for f in per_block) / g_net) if g_net else None
    if ratio is None:
        notes.append('no transaction-level block came back with inputs: ADA reported gross')
    aids = sorted({a for f in per_block for a in f['assets']})
    pr = ctx.prices.get(['cardano:%s' % a for a in aids] + [nat_key])
    meta, price_of, per_asset = {}, {}, {}
    nt = len(per_block)
    for a in aids:
        q = pr.get('cardano:%s' % a)
        kdec = next((f['assets'][a]['decimals'] for f in per_block if a in f['assets'] and f['assets'][a]['decimals'] is not None), None)
        dec = int(q['decimals']) if q and q.get('decimals') is not None else (int(kdec) if kdec is not None else 0)
        meta[a] = {'symbol': (q or {}).get('symbol') or ascii_name(a[56:]), 'decimals': dec}
        price_of[a] = (q or {}).get('price') if q else None
        per_asset[a] = {'count': [f['assets'][a]['outputs'] if a in f['assets'] else 0 for f in per_block],
                        'amount': [f['assets'][a]['net'] / 10 ** dec if a in f['assets'] else 0.0 for f in per_block],
                        'gross': [f['assets'][a]['gross'] / 10 ** dec if a in f['assets'] else 0.0 for f in per_block]}
    tok_tr = asset_rows(per_asset, nt, N, meta, price_of)
    ada_amount = [g * ratio for g in gross_ada] if ratio is not None else list(gross_ada)
    ada_tr = asset_rows({'native:ADA': {'count': [info[b['hash']].get('tx_count') or 0 for b in ada_units],
                                        'amount': ada_amount, 'gross': gross_ada}},
                        len(ada_units), N, {'native:ADA': {'symbol': 'ADA', 'decimals': 6}},
                        {'native:ADA': (pr.get(nat_key) or {}).get('price')}, native_symbols=['ADA'])
    for r in ada_tr['assets'] + ada_tr['unpriced_top']:
        r['net_over_gross'] = ratio
        r['note'] = ('net = block total_output (%d blocks) x net/gross ratio %.3f measured on every transaction of %d '
                     'blocks; gross = total_output, change included' % (len(ada_units), ratio, nt)) if ratio is not None \
            else 'gross block total_output (change included): no netted sample'
    for r in tok_tr['assets'] + tok_tr['unpriced_top']:
        r['note'] = 'net per transaction per wallet, from every transaction of %d sampled blocks; "transfers" = outputs carrying it' % nt
    tr = merge_rows(ada_tr, tok_tr)
    tr['method'] = ('NET per transaction per wallet (stake key, else address): tokens from tx_info on %d blocks; ADA = '
                    'block_info total_output on %d blocks x the net/gross ratio of those transactions' % (nt, len(ada_units)))
    block_ratios = sorted(f['lovelace_net'] / f['lovelace_gross_netted'] for f in per_block if f['lovelace_gross_netted'])
    tr['netting'] = {'blocks': nt, 'transactions': sum(f['txs'] for f in per_block),
                     'netted_transactions': sum(f['netted'] for f in per_block), 'ada_net_over_gross': ratio,
                     'block_ratio_min': block_ratios[0] if block_ratios else None,
                     'block_ratio_median': block_ratios[len(block_ratios) // 2] if block_ratios else None,
                     'block_ratio_max': block_ratios[-1] if block_ratios else None}
    fee_total, fee_se = stratified_total(fees, N)
    secs = max(1, ctx.end_ts - ctx.start_ts)
    tx = {'count': tx_count, 'se': 0.0, 'method': 'exact-blocks', 'blocks': N, 'sampled': N, 'tps': tx_count / secs,
          'note': 'every block in the window; Cardano has no system transactions'}
    cross = cross_check(cfg, tx_count, ctx)
    if cross:
        tx['cross_check'] = cross
    return {'tx': tx, 'transfers': tr,
            'fees': {'native': fee_total, 'native_se': fee_se},
            'window': window_dict(ctx.start_ts, ctx.end_ts),
            'blocks': {'first': blocks[0]['block_height'] if blocks else None,
                       'last': blocks[-1]['block_height'] if blocks else None},
            'endpoint': api, 'calls': http.requests, 'notes': notes, 'errors': errors[:20], 'error_count': len(errors),
            'seconds': round(time.time() - t0, 1)}


def cross_check(cfg, tx_count, ctx):
    key = (cfg.get('ids') or {}).get('blockchair')
    if not key:
        return None
    from chain_adapters.utxo import blockchair_stats
    d = blockchair_stats(None, key)
    if not d:
        return None
    hours = (ctx.end_ts - ctx.start_ts) / 3600.0
    out = {'source': 'blockchair', 'transactions_24h': d.get('transactions_24h'), 'window_hours': round(hours, 3)}
    if d.get('transactions_24h') and 22 <= hours <= 26:
        out['count_over_blockchair'] = tx_count * (24.0 / hours) / d['transactions_24h']
    return out
