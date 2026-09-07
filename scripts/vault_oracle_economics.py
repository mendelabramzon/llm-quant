#!/usr/bin/env python3
"""Offline economics of already-recorded Yearn-style profit unlocking.

Outputs token-denominated scenarios, not dollar valuations or trading signals.
No future keeper reports or transactions are assumed. The model requires the
vault to burn its remaining self-held shares without changing totalAssets.
Actual entry and exit behavior must be checked separately on a fork.
"""
import argparse
import json
from decimal import Decimal, getcontext
from pathlib import Path

from non_mev_screen import ROOT

getcontext().prec = 64
D = Decimal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'research/2026-09-07/vault_oracles')
    args = parser.parse_args()
    h = json.loads((args.out/'snapshot.json').read_text())
    vaults = json.loads((args.out/'vaults.json').read_text())['vaults']
    rows = []
    for v in vaults:
        if not (v['profitMaxUnlockTime'] and v['self_held_shares'] and v['totalSupply']):
            continue
        decimals = v['asset_metadata']['decimals']
        if decimals is None:
            continue
        assets = D(v['totalAssets']) / 10**decimals
        locked_fraction = D(v['self_held_shares']) / v['totalSupply']
        duration = max(0, (v['fullProfitUnlockDate'] or 0) + 1 - h['timestamp'])
        if not duration or not 0 < locked_fraction < 1:
            continue
        locked_value = assets * locked_fraction
        active_value = assets - locked_value
        cap = D(v['maxDeposit_probe'] or 0) / 10**decimals

        def gain(capital):
            return capital*locked_value/(active_value+capital)

        scenarios = []
        for annual_cost in ['0.03', '0.05', '0.08']:
            time_cost = D(annual_cost)*duration/D(31536000)
            optimum = max(D(0), (locked_value*active_value/time_cost).sqrt()-active_value)
            optimum = min(optimum, cap)
            scenarios.append({'annual_capital_cost': annual_cost,
                'model_optimum_principal_units': str(optimum),
                'gain_before_capital_gas_and_swaps_units': str(gain(optimum)),
                'surplus_before_gas_and_swaps_units': str(gain(optimum)-time_cost*optimum)})
        rows.append({'address':v['address'], 'symbol':v['metadata']['symbol'],
            'asset':v['asset'], 'asset_symbol':v['asset_metadata']['symbol'],
            'total_assets_units':str(assets), 'locked_value_units':str(locked_value),
            'hold_seconds':duration, 'deposit_cap_probe_units':str(cap),
            'gain_at_100k_units':str(gain(D(100000))), 'scenarios':scenarios,
            'status':'model_only; getter cap is not proof of public entry or exit liquidity'})
    (args.out/'economics.json').write_text(json.dumps({'snapshot':h,
        'formula':'G(C)=C*D/(A-D+C); D=A*remaining_self_shares/totalSupply',
        'assumptions':['No additional reports, losses, deposits, withdrawals or slashes',
            'Self-held shares fully unlock and assets remain constant',
            'No fees, swaps, gas, reserve for risk or integer rounding in this model',
            'Every result is in its named underlying token; no parity assumption'],
        'candidates':rows},indent=2)+'\n')
    print(f'Wrote {len(rows)} token-denominated scenarios to {args.out / "economics.json"}')


if __name__ == '__main__':
    main()
