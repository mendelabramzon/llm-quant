#!/usr/bin/env python3
"""Offline check motivated by the amount-outlier notes: do the per-block concentrated-liquidity cyclers on
Optimism and Base hold their positions while swaps execute, or only across block boundaries?

Uses the pilot's saved 30-minute pool log histories (followup/*_pool_context.json.gz). A "cycler position"
is a liquidity delta whose exact value appears at least three times as a mint and three times as a burn in
the history: the same size re-minted again and again. The check walks events in (block, log index) order,
tracks how much cycler liquidity is in the pool, and asks for every swap whether any cycler liquidity was
present and what share of the swap's reported in-range liquidity it was. It also records where in the block
cycler burns and mints land. No RPC. Writes amount_outliers/cycling_check.json.
"""
import collections
import gzip
import json
import statistics

from onchain_probe import ROOT, hx, save, utc
from analyze_onchain import decode

BASE = ROOT / 'research/2026-09-05'
POOLS = {'optimism': ['0x478946bcd4a5a22b316470f5486fafb928c0ba25'],
         'base': ['0xb2cc224c1c9fee385f8ad6a55b4d94e92359dc59', '0x4e962bb3889bf030368f56810a9c96b83cb3e778', '0xb5f0b4ae66c14f7efaa9aa1468e8fc536a3e288c']}
MIN_REPEATS = 3


def analyse(chain, pool, logs):
    events = []
    for l in logs:
        if l['address'].lower() != pool:
            continue
        d = decode(l)
        if d['family'] in ('V3Swap', 'V3Mint', 'V3Burn'):
            events.append((hx(l['blockNumber']), hx(l['logIndex']), hx(l['transactionIndex']), d))
    events.sort(key=lambda e: (e[0], e[1]))
    mints = collections.Counter(int(e[3]['liquidity_delta']) for e in events if e[3]['family'] == 'V3Mint' and int(e[3]['liquidity_delta']) > 0)
    burns = collections.Counter(-int(e[3]['liquidity_delta']) for e in events if e[3]['family'] == 'V3Burn' and int(e[3]['liquidity_delta']) < 0)
    cycler_sizes = {L for L in mints if mints[L] >= MIN_REPEATS and burns.get(L, 0) >= MIN_REPEATS}
    present, swaps = 0, []
    cycler_mint_idx, cycler_burn_idx, cycle_blocks = [], [], set()
    for block, _, tx_index, d in events:
        if d['family'] == 'V3Mint' and int(d['liquidity_delta']) in cycler_sizes:
            present += int(d['liquidity_delta'])
            cycler_mint_idx.append(tx_index)
            cycle_blocks.add(block)
        elif d['family'] == 'V3Burn' and -int(d['liquidity_delta']) in cycler_sizes:
            present = max(0, present - (-int(d['liquidity_delta'])))
            cycler_burn_idx.append(tx_index)
            cycle_blocks.add(block)
        elif d['family'] == 'V3Swap' and 'liquidity' in d:
            liq = int(d['liquidity'])
            swaps.append({'block': block, 'tx_index': tx_index, 'cycler_present': present > 0, 'cycler_share': (present / liq) if liq else None,
                          'liquidity': liq, 'amount0_abs': abs(int(d['amount0_raw'])), 'amount1_abs': abs(int(d['amount1_raw']))})
    with_c = [s for s in swaps if s['cycler_present']]
    vol0 = sum(s['amount0_abs'] for s in swaps)
    out = {'pool': pool, 'chain': chain, 'events': len(events), 'swaps': len(swaps), 'mints': sum(mints.values()), 'burns_nonzero': sum(burns.values()),
           'cycler_position_sizes': len(cycler_sizes), 'cycler_mints': len(cycler_mint_idx), 'cycler_burns': len(cycler_burn_idx),
           'blocks_with_cycler_activity': len(cycle_blocks),
           'cycler_mint_tx_index_median': statistics.median(cycler_mint_idx) if cycler_mint_idx else None,
           'cycler_burn_tx_index_median': statistics.median(cycler_burn_idx) if cycler_burn_idx else None,
           'swaps_with_cycler_liquidity_present': len(with_c), 'swaps_with_cycler_present_pct': round(100 * len(with_c) / len(swaps), 2) if swaps else None,
           'token0_volume_share_with_cycler_present_pct': round(100 * sum(s['amount0_abs'] for s in with_c) / vol0, 2) if vol0 else None,
           'median_cycler_share_of_in_range_liquidity_when_present': round(statistics.median(s['cycler_share'] for s in with_c if s['cycler_share'] is not None), 4) if with_c else None,
           'median_swap_liquidity_with_cycler': int(statistics.median(s['liquidity'] for s in with_c)) if with_c else None,
           'median_swap_liquidity_without_cycler': int(statistics.median(s['liquidity'] for s in swaps if not s['cycler_present'])) if any(not s['cycler_present'] for s in swaps) else None,
           'method': 'cycler sizes = liquidity deltas repeated >= %d times as both mint and burn; presence tracked in (block, log index) order; '
                     'swap liquidity field is the pool in-range liquidity after the swap' % MIN_REPEATS}
    return out


def main():
    result = {'generated_at': utc(), 'pools': []}
    for chain, pools in POOLS.items():
        path = BASE / 'followup' / (chain + '_pool_context.json.gz')
        if not path.exists():
            continue
        with gzip.open(path, 'rt') as f:
            ctx = json.load(f)
        for pool in pools:
            r = analyse(chain, pool, ctx['logs'])
            r.update(history_start_block=ctx['start_block'], history_end_block=ctx['end_block'], history_start_utc=utc(ctx['start_timestamp']))
            result['pools'].append(r)
            print(json.dumps({k: v for k, v in r.items() if k != 'method'}), flush=True)
    save(BASE / 'amount_outliers' / 'cycling_check.json', result)


if __name__ == '__main__':
    main()
