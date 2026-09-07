#!/usr/bin/env python3
"""Follow-up checks for a Robinhood Chain window that need sources other than the collected chunk files.

Writes `followups.json` and `followups.md` into the window directory:
  - L1 cost of the window: the batch poster's blob and execution fees on Ethereum (from `l1_poster_window.json`,
    assembled from local mainnet blocks + Infura; blob base fee recomputed from excessBlobGas with the update
    fraction calibrated against sampled receipts)
  - fee regime: daily balance of the network / infra fee accounts (Blockscout) and a base-fee history sample
  - weekly fee distributions (RewardDistributor RecipientRecieved logs, Blockscout)
  - stock-token access-control registry: blocked / unblocked / pause events (Blockscout logs)
  - identities of the stock-token minters found in the window (Blockscout)

    uv run python scripts/orbit_followups.py --dir research/2026-09-07/robinhood_10h
"""
import argparse
import collections
import datetime as dt
import json
import time
import urllib.request
from pathlib import Path

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
BS = 'https://robinhoodchain.blockscout.com/api/v2/'
NETWORK_FEE = '0xbC5C3a7Adecf54D34169fd90dbD1B7d3142DF067'
INFRA_FEE = '0x5a2B80a9b7effc06129bD5462D77BC20A8A59BE7'
AEP_ROUTER = '0x92433c650785397386A0Cc347EC2489718E45307'
RH_RECIPIENT = '0x8b3511B4c4b68FCAfdCE7e6f91B925458bB64Ea6'
REGISTRY = '0xe10b6f6b275de231345c20d14ab812db62151b00'
BLOB_GAS_PER_BLOB = 131072
CANDIDATE_FRACTIONS = {'cancun 3338477': 3338477, 'pectra 5007716': 5007716, 'bpo1 8346193': 8346193, 'bpo2 11684671': 11684671}


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e
            time.sleep(1.0 + i)
    return {'_error': str(last)[:120]}


def fake_exponential(factor, numerator, denominator):
    i = 1
    output = 0
    acc = factor * denominator
    while acc > 0:
        output += acc
        acc = acc * numerator // (denominator * i)
        i += 1
    return output // denominator


def l1_cost(rows):
    """rows: hash -> {ts, blobs, excessBlobGas, baseFee, gas, [gasUsed, blobGasPrice]}"""
    sampled = [r for r in rows.values() if r.get('blobGasPrice')]
    best = None
    for name, frac in CANDIDATE_FRACTIONS.items():
        err = sum(abs(fake_exponential(1, r['excessBlobGas'], frac) - r['blobGasPrice']) / max(1, r['blobGasPrice']) for r in sampled) / max(1, len(sampled))
        if best is None or err < best[1]:
            best = (name, err, frac)
    frac = best[2]
    exec_gas = int(sum(r['gasUsed'] for r in sampled) / max(1, len(sampled))) if sampled else 145000
    per_hour = collections.defaultdict(lambda: {'batches': 0, 'blobs': 0, 'blob_fee_eth': 0.0, 'exec_fee_eth': 0.0})
    tot = {'batches': 0, 'blobs': 0, 'blob_fee_eth': 0.0, 'exec_fee_eth': 0.0, 'bytes_blob_capacity_MB': 0.0}
    prices = []
    for r in rows.values():
        price = fake_exponential(1, r['excessBlobGas'], frac)
        prices.append(price)
        bf = r['blobs'] * BLOB_GAS_PER_BLOB * price / 1e18
        ef = exec_gas * r['baseFee'] / 1e18
        h = dt.datetime.fromtimestamp(r['ts'], dt.timezone.utc).strftime('%H:00')
        per_hour[h]['batches'] += 1
        per_hour[h]['blobs'] += r['blobs']
        per_hour[h]['blob_fee_eth'] += bf
        per_hour[h]['exec_fee_eth'] += ef
        tot['batches'] += 1
        tot['blobs'] += r['blobs']
        tot['blob_fee_eth'] += bf
        tot['exec_fee_eth'] += ef
    tot['bytes_blob_capacity_MB'] = tot['blobs'] * BLOB_GAS_PER_BLOB / 1e6
    tot['total_eth'] = tot['blob_fee_eth'] + tot['exec_fee_eth']
    return {'blob_fee_update_fraction': best[0], 'calibration_rel_error': round(best[1], 4), 'exec_gas_per_batch': exec_gas, 'blob_price_gwei_min': min(prices) / 1e9 if prices else None, 'blob_price_gwei_max': max(prices) / 1e9 if prices else None,
            'totals': {k: (round(v, 6) if isinstance(v, float) else v) for k, v in tot.items()}, 'per_hour': [{'hour_utc': h, **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()}} for h, c in sorted(per_hour.items())]}


def balance_history(addr):
    d = get(BS + 'addresses/%s/coin-balance-history-by-day' % addr)
    items = d.get('items') if isinstance(d, dict) else d
    if not isinstance(items, list):
        return []
    rows = [{'date': x.get('date'), 'eth': int(x.get('value') or 0) / 1e18} for x in items]
    for i, r in enumerate(rows):
        r['delta_eth'] = round(r['eth'] - rows[i - 1]['eth'], 1) if i else None
        r['eth'] = round(r['eth'], 1)
    return rows


def distributions(addr):
    out = []
    d = get(BS + 'addresses/%s/logs' % addr)
    for it in (d.get('items') or []):
        dec = it.get('decoded') or {}
        if not (dec.get('method_call') or '').startswith('RecipientRecieved'):
            continue
        params = {p.get('name'): p.get('value') for p in dec.get('parameters', [])}
        out.append({'block': it.get('block_number'), 'tx': it.get('transaction_hash'), 'recipient': params.get('recipient'), 'eth': round(int(params.get('value') or 0) / 1e18, 3)})
    by_tx = collections.OrderedDict()
    for r in out:
        by_tx.setdefault(r['tx'], {'block': r['block'], 'tx': r['tx'], 'recipients': []})['recipients'].append((r['recipient'], r['eth']))
    return list(by_tx.values())


def registry_events():
    d = get(BS + 'addresses/%s/logs' % REGISTRY)
    items = d.get('items') or []
    rows = []
    for it in items:
        dec = it.get('decoded') or {}
        rows.append({'block': it.get('block_number'), 'event': (dec.get('method_call') or (it.get('topics') or [''])[0])[:60], 'params': [(p.get('name'), p.get('value')) for p in dec.get('parameters', [])][:2], 'tx': it.get('transaction_hash')})
    counts = collections.Counter(r['event'].split('(')[0] for r in rows)
    ct = get(BS + 'addresses/%s/counters' % REGISTRY)
    return {'recent': rows[:30], 'recent_counts': dict(counts), 'counters': ct if isinstance(ct, dict) else None, 'has_more_pages': bool(d.get('next_page_params'))}


def identities(addrs):
    out = {}
    for a in addrs:
        if not a:
            continue
        d = get(BS + 'addresses/%s' % a)
        tok = d.get('token') or {}
        out[a] = {'name': d.get('name'), 'is_contract': d.get('is_contract'), 'verified': d.get('is_verified'), 'token': tok.get('symbol'), 'impl': [(i.get('name')) for i in d.get('implementations') or []], 'creator': d.get('creator_address_hash'), 'coin_balance_eth': round(int(d.get('coin_balance') or 0) / 1e18, 3), 'tags': [t.get('display_name') for t in (d.get('public_tags') or [])]}
        time.sleep(0.15)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dir', required=True)
    p.add_argument('--l1-poster', default=None, help='path to l1_poster_window.json (default <dir>/l1_poster_window.json)')
    p.add_argument('--basefee-history', default=None)
    a = p.parse_args()
    d = Path(a.dir)
    out = {}
    lp = Path(a.l1_poster) if a.l1_poster else d / 'l1_poster_window.json'
    if lp.exists():
        out['l1_cost'] = l1_cost(json.loads(lp.read_text()))
    bh = Path(a.basefee_history) if a.basefee_history else d / 'basefee_history.json'
    if bh.exists():
        out['basefee_history'] = json.loads(bh.read_text())
    out['fee_accounts'] = {'network_fee_distributor': balance_history(NETWORK_FEE), 'infra_fee_distributor': balance_history(INFRA_FEE), 'robinhood_recipient': balance_history(RH_RECIPIENT)}
    out['distributions'] = {'network': distributions(NETWORK_FEE), 'infra': distributions(INFRA_FEE)}
    out['registry'] = registry_events()
    analysis = json.loads((d / 'analysis.json').read_text()) if (d / 'analysis.json').exists() else {}
    minters = [m for m, _ in (analysis.get('stocks', {}).get('totals', {}).get('mint_tx_senders') or [])]
    ids = identities(minters + [RH_RECIPIENT, '0xF1e45A0B1B4290eb95D04cec2b4b26D72b99568b', '0x395E8B30E069aD49b851a519be444CEB6aA38e7E', AEP_ROUTER])
    out['identities'] = ids
    (d / 'followups.json').write_text(json.dumps(out, indent=1, default=str))
    L = ['# Follow-ups\n']
    if 'l1_cost' in out:
        c = out['l1_cost']
        t = c['totals']
        L.append('## L1 cost of the window (Ethereum batch poster 0xdaa52608 -> SequencerInbox 0xbd0d173e)\n')
        L.append('Batches %d, blobs %d (%.1f MB of blob capacity), blob price %.4f-%.4f gwei (fraction %s, calibration error %.1f%%), execution gas %d per batch. Blob fees %.4f ETH + execution fees %.4f ETH = **%.4f ETH**.\n' % (
            t['batches'], t['blobs'], t['bytes_blob_capacity_MB'], c['blob_price_gwei_min'], c['blob_price_gwei_max'], c['blob_fee_update_fraction'], 100 * c['calibration_rel_error'], c['exec_gas_per_batch'], t['blob_fee_eth'], t['exec_fee_eth'], t['total_eth']))
        L.append('| hour | batches | blobs | blob fee ETH | exec fee ETH |\n|---|---|---|---|---|\n' + ''.join('| %s | %d | %d | %.5f | %.5f |\n' % (r['hour_utc'], r['batches'], r['blobs'], r['blob_fee_eth'], r['exec_fee_eth']) for r in c['per_hour']))
    fa = out['fee_accounts']
    L.append('\n## Fee accounts, daily balance (ETH) and daily accrual\n')
    L.append('| date | network fee account | accrual | infra fee account | accrual |\n|---|---|---|---|---|\n')
    inf = {r['date']: r for r in fa['infra_fee_distributor']}
    for r in fa['network_fee_distributor'][-16:]:
        i = inf.get(r['date'], {})
        L.append('| %s | %s | %s | %s | %s |\n' % (r['date'], format(r['eth'], ','), r['delta_eth'] if r['delta_eth'] is not None else '', format(i.get('eth', 0), ','), i.get('delta_eth', '')))
    L.append('\n## Weekly distributions (RecipientRecieved)\n')
    for k in ('network', 'infra'):
        L.append('\n%s fee distributor:\n' % k)
        for x in out['distributions'][k]:
            L.append('- block %s: %s (tx %s)\n' % (x['block'], ', '.join('%s %.2f ETH' % (r[0][:10], r[1]) for r in x['recipients']), x['tx'][:14]))
    if 'basefee_history' in out:
        L.append('\n## Base fee history (six-hour samples)\n')
        L.append('| utc | block | base fee gwei | txs in block | gas used |\n|---|---|---|---|---|\n' + ''.join('| %s | %d | %.4f | %d | %s |\n' % (r['utc'], r['block'], r['basefee_gwei'], r['txs'], format(r['gasUsed'], ',')) for r in out['basefee_history']))
    rg = out['registry']
    L.append('\n## Stock-token access-control registry %s\n' % REGISTRY)
    L.append('Recent event counts (first page of logs): %s; counters: %s\n' % (rg['recent_counts'], rg['counters']))
    L.append('| block | event | params | tx |\n|---|---|---|---|\n' + ''.join('| %s | %s | %s | %s |\n' % (r['block'], r['event'], r['params'], (r['tx'] or '')[:14]) for r in rg['recent'][:20]))
    L.append('\n## Identities\n')
    L.append('| address | name | contract | impl | balance ETH | tags |\n|---|---|---|---|---|---|\n' + ''.join('| %s | %s | %s | %s | %s | %s |\n' % (k, v.get('name'), v.get('is_contract'), v.get('impl'), v.get('coin_balance_eth'), v.get('tags')) for k, v in ids.items()))
    (d / 'followups.md').write_text(''.join(L))
    print(json.dumps({k: (v if k in ('l1_cost',) else '...') for k, v in out.items()}, indent=1, default=str)[:3000])
    print('wrote', d / 'followups.md')


if __name__ == '__main__':
    main()
