"""Offline five-hour activity figure using saved events and the settled fan-in detector."""
import json,os
from pathlib import Path
from datetime import datetime,timezone
os.environ.setdefault('MPLCONFIGDIR','/tmp/llm-quant-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path(__file__).resolve().parent
s=json.loads((out/'events.json').read_text())['series']
h=next(h for h in json.loads((out/'detectors.json').read_text())['hits'] if h['detector']=='token_fan_in')
buckets={datetime.fromtimestamp(int(t),timezone.utc).strftime('%H:%M'):n for t,n in h['evidence']['buckets'].items()}
x=list(range(len(s)))
lpt=[buckets.get(r['from_utc'],0) for r in s]
fig,axes=plt.subplots(3,1,figsize=(11,8),sharex=True,gridspec_kw={'height_ratios':[1.5,1.6,1.2]})
fig.patch.set_facecolor('#f8fafc')
for ax in axes:
 ax.set_facecolor('#f8fafc'); ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
 ax.axvline(11.5,color='#94a3b8',ls='--',lw=1)
axes[0].fill_between(x,[r['eth_low'] for r in s],[r['eth_high'] for r in s],color='#2563eb',alpha=.15)
axes[0].plot(x,[r['eth_close'] for r in s],color='#2563eb',lw=2,marker='.')
axes[0].set_ylabel('ETH / USDC')
axes[0].set_title('LPT transfers explain a large part of the activity increase after 08:30 UTC',loc='left',fontsize=13,weight='bold',pad=17)
axes[1].bar(x,[(r['txs']-n)/1000 for r,n in zip(s,lpt)],label='Other transactions',color='#94a3b8',width=.78)
axes[1].bar(x,[n/1000 for n in lpt],bottom=[(r['txs']-n)/1000 for r,n in zip(s,lpt)],label='LPT transfers to one recipient',color='#0f766e',width=.78)
axes[1].set_ylabel('Transactions\nthousands');axes[1].legend(loc='upper left',frameon=False,fontsize=9)
axes[2].plot(x,[r['base_fee_gwei_median'] for r in s],color='#d97706',lw=2,marker='.')
axes[2].set_ylabel('Median base fee\ngwei')
axes[2].set_xticks(x[::2],[r['from_utc'] for r in s][::2])
axes[2].set_xlabel('2026-09-10 UTC · 15-minute buckets; first and last buckets are partial')
fig.text(.095,.027,'Price: Uniswap v3 USDC/WETH 0.05% pool. Transfers: settled LPT logs, matched to distinct transactions.\n'
 'The final bucket contains only 47 seconds. Window pinned at original request: 05:30:48–10:30:48 UTC.',fontsize=9,color='#475569')
fig.tight_layout(rect=(.03,.09,.99,.99))
fig.savefig(out/'activity.png',dpi=160,facecolor=fig.get_facecolor())
fig.savefig(out/'activity.svg',facecolor=fig.get_facecolor())
print('wrote activity.png and activity.svg')
