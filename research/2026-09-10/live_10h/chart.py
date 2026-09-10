"""Rebuild the study's price/fee figure from the existing offline activity digest."""
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/llm-quant-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parent
a = json.loads((out / 'events.json').read_text())
s = a['series']
x = list(range(len(s)))
fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1.3, 1.3]})
fig.patch.set_facecolor('#f8fafc')
for ax in axes:
    ax.set_facecolor('#f8fafc')
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=.18)
    ax.set_axisbelow(True)
axes[0].fill_between(x, [r['eth_low'] for r in s], [r['eth_high'] for r in s], color='#2563eb', alpha=.15, label='Half-hour range')
axes[0].plot(x, [r['eth_close'] for r in s], color='#2563eb', linewidth=2, marker='.', label='Last swap in bucket')
axes[0].set_ylabel('ETH / USDC')
axes[0].legend(loc='lower left', frameon=False, ncol=2)
axes[0].set_title('ETH fell 1.04%; the largest fee spike was earlier in the afternoon', loc='left', fontsize=14, weight='bold', pad=18)
axes[1].bar(x, [r['v3_usdc_weth_usd'] / 1e6 for r in s], color='#64748b', width=.7)
axes[1].set_ylabel('Pool volume\nUSD millions')
axes[2].plot(x, [r['base_fee_gwei_median'] for r in s], color='#d97706', linewidth=2, marker='.')
axes[2].set_ylabel('Median base fee\ngwei')
axes[2].set_xticks(x[::2], [r['from_utc'] for r in s][::2])
axes[2].set_xlabel('2026-09-09 UTC · half-hour buckets (first and last buckets are partial)')
fig.text(.095, .025, 'Price and volume: Uniswap v3 USDC/WETH 0.05% pool only. Base fee: every collected block.\n'
         'Finalized blocks 25,939,239–25,942,222 · 10:32–20:32 UTC · Source: saved Ethereum blocks and logs.',
         fontsize=9, color='#475569')
fig.tight_layout(rect=(.03, .09, .99, .99))
fig.savefig(out / 'activity.png', dpi=160, facecolor=fig.get_facecolor())
fig.savefig(out / 'activity.svg', facecolor=fig.get_facecolor())
print('wrote activity.png and activity.svg')
