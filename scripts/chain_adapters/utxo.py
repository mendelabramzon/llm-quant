#!/usr/bin/env python3
"""UTXO chains: Bitcoin and Litecoin read block by block from a mempool.space-style explorer, and Dogecoin, Bitcoin
Cash and Zcash from Blockchair's trailing-24h statistics.

Counting (`utxo`). A day of Bitcoin is ~144 blocks and of Litecoin ~576, and `/v1/blocks/{height}` returns fifteen
block summaries per call with `tx_count` and `extras.totalOutputAmt`, so every block in the window is read and the count
is exact (`exact-blocks`). Blocks are selected by their own header timestamp, which miners may set up to two hours off;
the walk therefore continues two hours past the window start before it stops. The coinbase is one transaction per
block and is not activity, so it is excluded from the headline (`raw_count` keeps it, which is what Blockchair counts).

Litecoin's MWEB extension adds a second system transaction to every block: the HogEx ("integrating") transaction, the
last one in the block, which spends the previous HogEx output and re-creates the whole MWEB peg balance (~465k LTC) as
one witness-v8 output every 2.5 minutes. Left in, it is ~95% of Litecoin's "gross output" and moves by nothing a user
did. It is detected on the newest block (one call) and, when present, read from each block's last transaction page and
subtracted from both the count and the value.

Value. `totalOutputAmt` less the coinbase reward (and the HogEx output) is the gross output value: it includes change
returned to the sender, so it overstates economic transfer by a factor that is not knowable from block summaries. The
package convention is a net per-transaction headline wherever the data allows; here it does not (netting change needs
every transaction's inputs, ~650k a day on Bitcoin), so `amount` and `gross` carry the same gross figure and the method
string says GROSS. Fees are reported beside it.

Aggregator fallback (`blockchair`). For chains without a mempool-style explorer, `api.blockchair.com/stats` gives every
chain's `transactions_24h` and `volume_24h` (smallest units, gross outputs) in one call. Its window is Blockchair's
trailing 24 hours ending at its own best block, not the probe's window; the result records both, and flags an index whose
block count disagrees with its best height (Dogecoin's did on 2026-10-09).
"""
import concurrent.futures as cf
import threading
import time

from chain_adapters import Http, HttpError, asset_rows, register, window_dict

PAGE = 15                    # block summaries per /v1/blocks/{height} call
TIMESTAMP_SLACK = 7200       # header timestamps may be this far off; walk this far past the window start
TX_PAGE = 25                 # transactions per /block/{hash}/txs/{start} page
BLOCKCHAIR_STATS = 'https://api.blockchair.com/stats'
INDEX_LAG_TOLERANCE = 100    # blocks: a Blockchair index whose count and best height differ by more is flagged

_bc_lock = threading.Lock()
_bc_cache = {}


def blockchair_stats(http=None, key=None):
    """Blockchair's all-chain stats, fetched once per process (one call answers every chain)."""
    with _bc_lock:
        if 'all' not in _bc_cache:
            h = http or Http(min_interval=1.0)
            try:
                _bc_cache['all'] = (h.get(BLOCKCHAIR_STATS) or {}).get('data') or {}
            except HttpError:
                _bc_cache['all'] = {}
        allstats = _bc_cache['all']
    if key is None:
        return allstats
    d = (allstats.get(key) or {}).get('data')
    if d is None and http is not None:
        try:
            d = (http.get('https://api.blockchair.com/%s/stats' % key) or {}).get('data')
        except HttpError:
            d = None
    return d


def is_v8(o):
    spk = (o.get('scriptpubkey') or '').lower()
    return spk.startswith('5820') or (o.get('scriptpubkey_address') or '').startswith('ltc1g')


def is_hogex(tx):
    """MWEB integrating transaction: its first output is a witness-v8 program (OP_8 PUSH32, '5820…', 'ltc1g…').

    Peg-outs from MWEB appear as further, ordinary outputs of the same transaction (2026-10-09: 6 of 22 blocks had one
    or two), so the test is on the first output only and `hogex_value` subtracts only the v8 output.
    """
    vout = tx.get('vout') or []
    return bool(vout) and is_v8(vout[0])


def hogex_value(tx):
    """The MWEB peg balance carried forward: the v8 output(s) only; peg-out outputs are user flows and stay in."""
    return sum(o.get('value') or 0 for o in tx.get('vout') or [] if is_v8(o))


def reduce_blocks(blocks, start_ts, end_ts, hogex_out=None):
    """Select blocks by header time in [start_ts, end_ts) and reduce each to the fields the probe reports.

    hogex_out: {block hash: HogEx output in base units}, present only for chains with MWEB.
    Returns rows sorted by height with user_tx, raw_tx, gross_out (base units, coinbase and HogEx removed), fees.
    """
    rows = {}
    for b in blocks:
        ts = b.get('timestamp')
        if ts is None or not (start_ts <= ts < end_ts):
            continue
        ex = b.get('extras') or {}
        h = (hogex_out or {}).get(b.get('id'))
        system = 1 + (1 if h is not None else 0)
        out_amt = ex.get('totalOutputAmt')
        reward = ex.get('reward') or 0
        gross = None if out_amt is None else max(0, out_amt - reward - (h or 0))
        rows[b['height']] = {'height': b['height'], 'ts': ts, 'hash': b.get('id'), 'raw_tx': b.get('tx_count') or 0,
                             'user_tx': max(0, (b.get('tx_count') or 0) - system), 'gross_out': gross,
                             'fees': ex.get('totalFees'), 'hogex_out': h}
    return [rows[k] for k in sorted(rows)]


def walk_blocks(http, base, start_ts, max_pages=400):
    """Every block summary from the tip back to TIMESTAMP_SLACK before start_ts."""
    tip = int(http.get(base + '/blocks/tip/height'))
    h, out, pages = tip, [], 0
    while h >= 0 and pages < max_pages:
        page = http.get(base + '/v1/blocks/%d' % h) or []
        pages += 1
        if not page:
            break
        out += page
        if max(b['timestamp'] for b in page) < start_ts - TIMESTAMP_SLACK:
            break
        h = min(b['height'] for b in page) - 1
    return tip, out, pages


def last_tx(http, base, b):
    """The final transaction of a block, from the last 25-transaction page."""
    start = ((max(1, b.get('tx_count') or 1) - 1) // TX_PAGE) * TX_PAGE
    page = http.get(base + '/block/%s/txs/%d' % (b['id'], start)) or []
    return page[-1] if page else None


def native_price(cfg, ctx):
    cg = (cfg.get('native') or {}).get('coingecko')
    if not cg:
        return None, None
    p = ctx.prices.one('coingecko:%s' % cg)
    return ((p or {}).get('price'), 'defillama:coingecko:%s' % cg) if p else (None, None)


@register('utxo')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    base = p['mempool'].rstrip('/')
    http = Http(min_interval=float(p.get('min_interval', 0.15)))
    nat = cfg.get('native') or {}
    sym, dec = nat.get('symbol') or '?', int(nat.get('decimals', 8))
    errors, notes = [], []
    tip, blocks, pages = walk_blocks(http, base, ctx.start_ts)
    newest = max(blocks, key=lambda b: b['height']) if blocks else None
    end_ts = ctx.end_ts

    # MWEB: detect on the newest block, then read the HogEx of every block in the window
    mweb = False
    if newest is not None and p.get('mweb', True):
        try:
            lt = last_tx(http, base, newest)
            mweb = bool(lt and is_hogex(lt))
        except HttpError as e:
            errors.append('mweb probe: %s' % str(e)[:100])
    hogex = {}
    if mweb:
        inwin = [b for b in blocks if b.get('timestamp') is not None and ctx.start_ts <= b['timestamp'] < end_ts]

        def one(b):
            try:
                t = last_tx(http, base, b)
                if t and is_hogex(t):
                    return b['id'], hogex_value(t)
                return b['id'], None
            except HttpError as e:
                return b['id'], 'error: %s' % str(e)[:80]

        with cf.ThreadPoolExecutor(max_workers=int(p.get('workers', 4))) as ex:
            for bid, v in ex.map(one, inwin):
                if isinstance(v, str):
                    errors.append('hogex %s: %s' % (bid[:16], v))
                elif v is not None:
                    hogex[bid] = v
        missing = len(inwin) - len(hogex)
        notes.append('MWEB HogEx found and removed in %d of %d blocks' % (len(hogex), len(inwin)))
        if missing:
            notes.append('%d block(s) without a readable HogEx kept their full output (value overstated there)' % missing)

    rows = reduce_blocks(blocks, ctx.start_ts, end_ts, hogex)
    N = len(rows)
    user_tx = sum(r['user_tx'] for r in rows)
    raw_tx = sum(r['raw_tx'] for r in rows)
    price, psrc = native_price(cfg, ctx)
    nat_id = 'native:%s' % sym
    gross = [(r['gross_out'] or 0) / 10 ** dec for r in rows]
    # Block summaries carry no per-transaction inputs, so there is no net figure to give: the headline is the gross
    # output value and says so (the package convention is net per transaction wherever the data allows it).
    per_asset = {nat_id: {'count': [r['user_tx'] for r in rows], 'amount': gross, 'gross': gross}}
    tr = asset_rows(per_asset, N, N, {nat_id: {'symbol': sym, 'decimals': dec}}, {nat_id: price}, native_symbols=[sym])
    for r in tr['assets'] + tr['unpriced_top']:
        r['note'] = ('gross output value: change returned to senders is included; coinbase%s removed'
                     % (' and MWEB HogEx' if mweb else ''))
        r['price_source'] = psrc
    tr['method'] = 'exact-blocks; GROSS outputs (change included; block summaries give no net figure)'
    fees = sum(r['fees'] or 0 for r in rows) / 10 ** dec
    secs = max(1, end_ts - ctx.start_ts)
    tx = {'count': user_tx, 'se': 0.0, 'raw_count': raw_tx, 'system_count': raw_tx - user_tx, 'method': 'exact-blocks',
          'blocks': N, 'sampled': N, 'tps': user_tx / secs,
          'note': 'every block whose header time falls in the window; coinbase%s excluded from the count'
                  % (' and MWEB HogEx' if mweb else '')}
    cross = cross_check(cfg, http, user_tx, raw_tx, sum(r['gross_out'] or 0 for r in rows) / 10 ** dec, ctx, dec)
    if cross:
        tx['cross_check'] = cross
    return {'tx': tx, 'transfers': tr,
            'fees': {'native': fees, 'usd': fees * price if price else None,
                     'per_tx_native': fees / user_tx if user_tx else None},
            'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': rows[0]['height'] if rows else None, 'last': rows[-1]['height'] if rows else None,
                       'tip': tip, 'pages': pages,
                       'mean_interval_s': ((rows[-1]['ts'] - rows[0]['ts']) / (N - 1)) if N > 1 else None},
            'endpoint': base, 'calls': http.requests, 'notes': notes, 'errors': errors[:20], 'error_count': len(errors),
            'seconds': round(time.time() - t0, 1)}


def cross_check(cfg, http, user_tx, raw_tx, gross_native, ctx, dec):
    """Blockchair's trailing-24h figures beside ours, meaningful only when the probe window is about a day."""
    key = (cfg.get('ids') or {}).get('blockchair')
    if not key:
        return None
    d = blockchair_stats(http, key)
    if not d:
        return {'source': 'blockchair', 'error': 'no stats for %s' % key}
    hours = (ctx.end_ts - ctx.start_ts) / 3600.0
    bc_tx = d.get('transactions_24h')
    bc_vol = d.get('volume_24h')
    out = {'source': 'blockchair', 'transactions_24h': bc_tx, 'volume_24h_native': (bc_vol / 10 ** dec) if bc_vol else None,
           'best_block_time': d.get('best_block_time'), 'window_hours': round(hours, 3)}
    if bc_tx and 22 <= hours <= 26:
        out['raw_count_over_blockchair'] = raw_tx * (24.0 / hours) / bc_tx
        if bc_vol and gross_native:
            out['gross_over_blockchair_volume'] = gross_native * (24.0 / hours) / (bc_vol / 10 ** dec)
    else:
        out['note'] = 'window is not ~24 h; ratios not computed'
    return out


@register('blockchair')
def probe_blockchair(cfg, ctx):
    """Blockchair's trailing-24h statistics for chains without a block-level explorer adapter."""
    t0 = time.time()
    p = cfg.get('probe') or {}
    key = p.get('blockchair') or (cfg.get('ids') or {}).get('blockchair')
    http = Http(min_interval=1.0)
    # the per-chain endpoint first: on 2026-10-09 the all-chain one served a Dogecoin index whose block count was
    # 142k ahead of its own best height, while the per-chain one was consistent
    try:
        d = (http.get('https://api.blockchair.com/%s/stats' % key) or {}).get('data')
    except HttpError:
        d = None
    d = d or blockchair_stats(http, key)
    if not d:
        raise RuntimeError('blockchair has no stats for %r' % key)
    nat = cfg.get('native') or {}
    sym, dec = nat.get('symbol') or '?', int(nat.get('decimals', 8))
    parsed = parse_blockchair(d, dec)
    price, psrc = native_price(cfg, ctx)
    if price is None and d.get('market_price_usd'):
        price, psrc = float(d['market_price_usd']), 'blockchair:market_price_usd'
    nat_id = 'native:%s' % sym
    vol = [parsed['volume_24h_native'] or 0.0]
    per_asset = {nat_id: {'count': [parsed['transactions_24h'] or 0], 'amount': vol, 'gross': vol}}
    tr = asset_rows(per_asset, 1, 1, {nat_id: {'symbol': sym, 'decimals': dec}}, {nat_id: price}, native_symbols=[sym])
    for r in tr['assets'] + tr['unpriced_top']:
        r['note'] = 'Blockchair volume_24h: gross outputs over its trailing 24 h (change included)'
        r['price_source'] = psrc
        r['top_block_share'] = None
    tr['method'] = 'aggregator-24h (blockchair); GROSS outputs, change included'
    end = parsed['best_block_ts'] or ctx.end_ts
    notes = ['window is Blockchair\'s trailing 24 h ending at its best block (%s UTC), not the probe window'
             % d.get('best_block_time')]
    if parsed['index_inconsistent']:
        # Seen on Dogecoin 2026-10-09: `blocks` ran 142k ahead of `best_block_height`, while the best height matched
        # BlockCypher's and transactions_24h matched an independent block sample (13.6 tx/block x ~1,400 blocks).
        # So the flag names the field that disagrees rather than voiding the count.
        notes.append('Blockchair `blocks` field (%s) disagrees with its best_block_height (%s); the 24 h figures do not '
                     'depend on it' % (d.get('blocks'), d.get('best_block_height')))
    tx = {'count': parsed['transactions_24h'], 'se': None, 'method': 'aggregator-24h', 'blocks': d.get('blocks_24h'),
          'mempool_transactions': d.get('mempool_transactions'),
          'avg_fee_native': (d['average_transaction_fee_24h'] / 10 ** dec) if d.get('average_transaction_fee_24h') else None,
          'note': 'Blockchair transactions_24h (its count; coinbase included)'}
    return {'tx': tx, 'transfers': tr, 'window': window_dict(end - 86400, end),
            'probe_window': window_dict(ctx.start_ts, ctx.end_ts),
            'endpoint': BLOCKCHAIR_STATS, 'calls': http.requests, 'notes': notes, 'errors': [], 'error_count': 0,
            'seconds': round(time.time() - t0, 1)}


def parse_blockchair(d, dec):
    """The fields the fallback reports, from one chain's Blockchair `data` object."""
    import datetime as dt
    best = d.get('best_block_time')
    best_ts = None
    if best:
        try:
            best_ts = int(dt.datetime.strptime(best, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())
        except ValueError:
            best_ts = None
    blocks, height = d.get('blocks'), d.get('best_block_height')
    vol = d.get('volume_24h')
    return {'transactions_24h': d.get('transactions_24h'),
            'volume_24h_native': (float(vol) / 10 ** dec) if vol is not None else None,
            'best_block_ts': best_ts,
            'index_inconsistent': (blocks is not None and height is not None
                                   and abs((blocks - 1) - height) > INDEX_LAG_TOLERANCE)}
