#!/usr/bin/env python3
"""Tezos: exact operation counts over the window from the TzKT indexer, and every XTZ and FA-token transfer in it.

Counting. TzKT answers `/operations/<kind>/count?timestamp.ge=…&timestamp.lt=…` for each operation kind, so the count
is exact for the window, not sampled (`exact-indexer`). The headline is *signed* operations: external transactions
(`initiator.null=true` — TzKT also lists every contract-to-contract call as a transaction of its own, which is reported
as `internal` but not counted twice) plus every other manager operation (originations, delegations, reveals, staking,
smart-rollup and DAL operations). Consensus operations (attestations, ~1.9M a day) are reported for scale and excluded:
they are the validators talking to each other. On 2026-10-09 the smart-rollup inbox (`sr_add_messages`, ~15k a day —
Etherlink's sequencer posting to its L1) was a sixth of all signed operations; the breakdown keeps that visible.

Value. Every applied transaction with a non-zero amount is read (paged by id), so XTZ moved — external and internal — is
a full sum, not an estimate; likewise every FA1.2/FA2 transfer from `/tokens/transfers`. The headline `amount` is NET
per operation group (one signed operation and every internal call it caused, identified by its hash): within a group,
each account's positive net change is summed (`net_positive`), so a router that receives and forwards counts once and a
swap's internal legs cancel down to what the signer actually paid and received. Token transfers name the internal
transaction that caused them (`transactionId`); the window's transaction id -> group hash map turns that into a group.
`gross` keeps every leg. A token is priced through DefiLlama as `tezos:<contract>` (that key is how the feed prices
USDt, ctez and the other fungible FA tokens; FA2 token ids other than 0 have no key and stay unpriced). NFTs show up as
unpriced 0-decimal tokens.
"""
import concurrent.futures as cf
import datetime as dt
import time

from chain_adapters import Http, HttpError, asset_rows, net_positive, register, window_dict

TZKT = 'https://api.tzkt.io/v1'
PAGE = 10000
MAX_PAGES = 60                # 600k rows: far above a day of Tezos, a guard against a runaway window
# manager operations other than transactions; each is one signed operation. Unknown kinds answer 404 and are skipped.
MANAGER_OPS = ('originations', 'delegations', 'reveals', 'staking', 'set_delegate_parameters', 'increase_paid_storage',
               'register_constants', 'transfer_ticket', 'update_secondary_key', 'drain_delegate', 'sr_add_messages',
               'sr_cement', 'sr_execute', 'sr_originate', 'sr_publish', 'sr_recover_bond', 'sr_refute',
               'dal_publish_commitment')
CONSENSUS_OPS = ('attestations',)


def iso(ts):
    return dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def token_key(contract, token_id):
    """DefiLlama key for a fungible FA token, or None when the feed has no key shape for it (FA2 ids other than 0)."""
    return 'tezos:%s' % contract if str(token_id) in ('0', '', 'None') else None


def addr(x):
    """TzKT returns accounts as {'address', 'alias'} objects in select.values; None (mint/burn side) stays None."""
    return (x or {}).get('address') if isinstance(x, dict) else x


def xtz_by_group(rows):
    """rows: [id, hash, sender, target, amount(mutez)] -> (net mutez, gross mutez, transfers, groups)."""
    groups = {}
    for r in rows:
        _, h, snd, tgt, amount = (list(r) + [None] * 5)[:5]
        groups.setdefault(h, []).append((addr(snd), addr(tgt), int(amount or 0)))
    gross = sum(a for g in groups.values() for _, _, a in g)
    net = sum(net_positive(g) for g in groups.values())
    return net, gross, len(rows), len(groups)


def tokens_by_group(rows, id2hash):
    """rows: TzKT select.values [id, amount, contract, tokenId, standard, decimals, symbol, from, to, transactionId,
    originationId, migrationId] -> per-token {'count', 'gross', 'net', ...}, netted per operation group."""
    toks = {}
    for r in rows:
        tid_, amount, contract, tid, std, dec, sym, frm, to, txid, orig, mig = (list(r) + [None] * 12)[:12]
        if contract is None:
            continue
        a = '%s:%s' % (contract, tid if tid is not None else '0')
        e = toks.setdefault(a, {'contract': contract, 'token_id': str(tid if tid is not None else '0'), 'standard': std,
                                'decimals': int(dec) if dec not in (None, '') and str(dec).isdigit() else None,
                                'symbol': sym, 'count': 0, 'gross': 0, 'groups': {}})
        try:
            v = int(amount or 0)
        except (TypeError, ValueError):
            v = 0
        g = id2hash.get(txid) if txid is not None else None
        g = g or ('origination:%s' % orig if orig is not None else 'migration:%s' % mig if mig is not None else 'transfer:%s' % tid_)
        e['groups'].setdefault(g, []).append((addr(frm), addr(to), v))
        e['count'] += 1
        e['gross'] += v
    for e in toks.values():
        e['net'] = sum(net_positive(m) for m in e['groups'].values())
        e['n_groups'] = len(e['groups'])
        del e['groups']
    return toks


def paged(http, url, log=None):
    """All rows of a TzKT list endpoint whose first selected value is the row id, paged by `id.gt`."""
    out, last, pages = [], None, 0
    while pages < MAX_PAGES:
        u = url + '&sort.asc=id&limit=%d' % PAGE + ('&id.gt=%d' % last if last is not None else '')
        page = http.get(u) or []
        pages += 1
        out += page
        if len(page) < PAGE:
            break
        last = page[-1][0]
    return out, pages


@register('tezos')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    api = (p.get('tzkt') or TZKT).rstrip('/')
    http = Http(min_interval=float(p.get('min_interval', 0.12)))
    f = 'timestamp.ge=%s&timestamp.lt=%s' % (iso(ctx.start_ts), iso(ctx.end_ts))
    errors = []

    def count(kind, extra=''):
        try:
            return kind + extra, int(http.get('%s/operations/%s/count?%s%s' % (api, kind, f, extra)))
        except HttpError as e:
            if e.code != 404:
                errors.append('%s: %s' % (kind, str(e)[:100]))
            return kind + extra, None
        except (TypeError, ValueError) as e:
            errors.append('%s: %s' % (kind, str(e)[:100]))
            return kind + extra, None

    jobs = [('transactions', ''), ('transactions', '&initiator.null=true'), ('transactions', '&status.ne=applied')]
    jobs += [(k, '') for k in MANAGER_OPS + CONSENSUS_OPS]
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        res = dict(ex.map(lambda j: count(*j), jobs))
    all_tx = res.get('transactions')
    ext_tx = res.get('transactions&initiator.null=true')
    failed = res.get('transactions&status.ne=applied')
    manager = {k: res.get(k) for k in MANAGER_OPS if res.get(k)}
    signed = (ext_tx or 0) + sum(manager.values())
    try:
        token_transfers = int(http.get('%s/tokens/transfers/count?%s' % (api, f)))
    except (HttpError, TypeError, ValueError) as e:
        token_transfers = None
        errors.append('token count: %s' % str(e)[:100])
    try:
        head = http.get(api + '/head') or {}
    except HttpError:
        head = {}

    # ------------------------------------------------------------------ value: every XTZ amount, every FA transfer
    xtz_rows, xpages = paged(http, '%s/operations/transactions?%s&status=applied&amount.gt=0'
                                   '&select.values=id,hash,sender,target,amount' % (api, f))
    xtz_net, xtz_gross, xtz_n, xtz_groups = xtz_by_group(xtz_rows)
    tok_rows, tpages = paged(http, '%s/tokens/transfers?%s&select.values=id,amount,token.contract.address,token.tokenId,'
                                   'token.standard,token.metadata.decimals,token.metadata.symbol,from.address,to.address,'
                                   'transactionId,originationId,migrationId' % (api, f))
    id2hash = {}
    if tok_rows:
        # every applied transaction's group hash, so a token transfer can be netted within its operation group
        map_rows, mpages = paged(http, '%s/operations/transactions?%s&select.values=id,hash' % (api, f))
        id2hash = {r[0]: r[1] for r in map_rows}
    else:
        mpages = 0
    toks = tokens_by_group(tok_rows, id2hash)
    keys = {a: token_key(e['contract'], e['token_id']) for a, e in toks.items()}
    nat = cfg.get('native') or {}
    nat_key = 'coingecko:%s' % (nat.get('coingecko') or 'tezos')
    pr = ctx.prices.get([k for k in keys.values() if k] + [nat_key])
    per_asset, meta, price_of = {}, {}, {}
    for a, e in toks.items():
        q = pr.get(keys[a]) if keys[a] else None
        dec = (q or {}).get('decimals')
        dec = int(dec) if dec is not None else e['decimals']
        meta[a] = {'symbol': (q or {}).get('symbol') or e['symbol'], 'decimals': dec}
        price_of[a] = (q or {}).get('price') if q else None
        scale = 10 ** dec if dec is not None and dec <= 36 else None
        per_asset[a] = {'count': [e['count']], 'amount': [(e['net'] / scale) if scale else 0.0],
                        'gross': [(e['gross'] / scale) if scale else 0.0]}
    per_asset['native:XTZ'] = {'count': [xtz_n], 'amount': [xtz_net / 1e6], 'gross': [xtz_gross / 1e6]}
    meta['native:XTZ'] = {'symbol': 'XTZ', 'decimals': 6}
    price_of['native:XTZ'] = (pr.get(nat_key) or {}).get('price')
    tr = asset_rows(per_asset, 1, 1, meta, price_of, native_symbols=['XTZ'])
    for r in tr['assets'] + tr['unpriced_top']:
        r['top_block_share'] = None      # one unit = the whole window; the field means nothing here
        if r['asset'] == 'native:XTZ':
            r['note'] = 'every applied transaction with a non-zero amount; net per operation group (%d groups)' % xtz_groups
        else:
            e = toks.get(r['asset']) or {}
            r['contract'], r['token_id'], r['standard'] = e.get('contract'), e.get('token_id'), e.get('standard')
            r['groups'] = e.get('n_groups')
    tr['method'] = 'exact-indexer: every transfer in the window, NET per operation group (gross kept beside)'
    secs = max(1, ctx.end_ts - ctx.start_ts)
    tx = {'count': signed, 'se': 0.0, 'method': 'exact-indexer',
          'external_transactions': ext_tx, 'internal_transactions': (all_tx - ext_tx) if all_tx is not None and ext_tx is not None else None,
          'failed_transactions': failed, 'other_manager_ops': manager,
          'consensus_ops': {k: res.get(k) for k in CONSENSUS_OPS}, 'token_transfers': token_transfers,
          'tps': signed / secs,
          'note': 'signed operations: external transactions + other manager operations; internal calls and consensus excluded'}
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, ctx.end_ts),
            'blocks': {'head_level': head.get('level'), 'head_time': head.get('timestamp')},
            'endpoint': api, 'calls': http.requests,
            'notes': ['%d XTZ pages, %d token pages, %d id->group pages read' % (xpages, tpages, mpages)],
            'errors': errors[:20], 'error_count': len(errors), 'seconds': round(time.time() - t0, 1)}
