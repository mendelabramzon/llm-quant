#!/usr/bin/env python3
"""Solana detectors and the window-to-window diff: what turns a Solana scan into a loop iteration.

The gap this closes. The first Solana window (2026-09-07) produced a report with eleven findings and a five-item
request list, and then nothing remembered them: the wash-volume share, the quote-posting swarm, the sniper failure spam,
the Relay depository, the sybil dump clusters all lived in one `report.md`. The Ethereum side of this repo stopped
working that way on 2026-09-08 — every mechanism became a *detector* that runs on every window and reports one `Hit`
shape into `research/findings.jsonl`, so recurrence and decay are measured rather than remembered. Solana windows did
not feed that ledger because the Ethereum `Context` is built on EVM blocks and logs.

The Solana detectors below read the deterministic `analysis.json` and `head_state.json` that `solana_scan.py` already
produces, so they cost seconds rather than another twelve-minute pass over the blocks, and they emit the same `Hit`
(`detector`, `key`, `severity`, `usd`, `evidence`, `economics`) so `findings.py ingest --chain solana` folds them into
the shared ledger unchanged. A `key` names the thing itself (program, venue, mint, hub address, asset pair) so the
same wash pair or failure bot seen on Monday and Thursday is one finding observed twice.

`diff` is the second half of the loop: the qualitative step for window N should start from what *changed* since
window N-1, not from a fresh reading of the same tables. It writes `diff.json` / `diff.md` with the standing metrics
side by side, the programs that entered or left the top tier, and which of the previous window's named actors (wash
tokens, hubs, failure bots, launch factories) are still there.

  uv run python scripts/solana_detect.py detect --out research/2026-09-10/solana_live
  uv run python scripts/solana_detect.py diff   --out research/2026-09-10/solana_live --prev research/2026-09-07/solana_live
  uv run python scripts/findings.py ingest --chain solana --out research/2026-09-10/solana_live

Thresholds are module constants so a reader can see what "spam" or "wash" means numerically; they are deliberately
conservative (a hit should be worth a human minute) and every hit carries the numbers it was judged on.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detectors import Hit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LABELS = json.loads((ROOT / 'scripts' / 'solana_labels.json').read_text())
PROG, MINTS = LABELS['programs'], LABELS['mints']
SYM = {m: v['symbol'] for m, v in MINTS.items()}
SOL = 'So11111111111111111111111111111111111111112'

# --- thresholds -------------------------------------------------------------------------------------------------------
WASH_MIN_USD = 1e6            # a venue or token is reported when at least this much of its volume is self-matched
WASH_MIN_SHARE = 0.20         # ...and self-matching is at least this share of the venue's priced volume
QUOTE_MIN_TX = 50_000         # a program is a quote poster when it sends this many txs...
QUOTE_MAX_TOKEN_MOVE = 0.05   # ...of which fewer than this share move any token...
QUOTE_MAX_PAYERS = 200        # ...from at most this many payers
SPAM_MIN_TX = 20_000          # a failure bot sends this many txs...
SPAM_MIN_FAIL = 0.90          # ...and this share of them fail
HUB_MIN_SENDERS = 500         # unlabelled fan-in hub: unique senders in the hour
DISTRIBUTOR_MIN_OUT = 1_000   # unlabelled fan-out: outgoing SOL transfers in the hour
FACTORY_MIN_LAUNCHES = 20     # a creator launching this many tokens in an hour is a factory
FLASH_MIN_FAILED = 100        # a flash-loan payer with this many failed and zero successful loans
NAV_MIN_BASIS_BP = 25         # LST market price vs on-chain stake-pool NAV
RATE_MIN_GAP_PP = 1.5         # same stable, two venues, supply-rate gap in percentage points
RATE_MIN_SUPPLIED_USD = 1e6   # both venues must hold at least this much of the asset
EXCHANGE_MIN_NET_USD = 5e6    # net exchange flow worth a ledger row
DUST_MIN_TRANSFERS = 1_000    # address-poisoning dust sender
LARGE_MIN_USD = 5e6           # a single owner's net position change in one transaction


def _m(v):
    return format(round(v or 0), ',')


def short(a):
    return a if len(a) <= 12 else a[:4] + '…' + a[-4:]


def plabel(p):
    v = PROG.get(p)
    return v['label'] if v else None


class Context:
    """Everything a Solana detector needs: the window's analysis, the head state, the label registry."""

    def __init__(self, out):
        self.out = Path(out)
        self.analysis = json.loads((self.out / 'analysis.json').read_text())
        hs = self.out / 'head_state.json'
        self.head = json.loads(hs.read_text()) if hs.exists() else {}
        self.window = self.analysis.get('window', {})
        self.network = self.analysis.get('network', {})
        self.sol_usd = (self.analysis.get('price_basis') or {}).get('sol_usd_median') or 0.0


# --- detectors ---------------------------------------------------------------------------------------------------------

def wash_volume(ctx):
    """Self-matched swap volume: one transaction, two signers, the second's legs mirror the first's."""
    d = ctx.analysis.get('dex') or {}
    sm = d.get('self_matched') or {}
    total = d.get('total_priced_usd') or 0
    hits = []
    if sm.get('total_usd'):
        share = sm['total_usd'] / total if total else 0
        hits.append(Hit(detector='sol_wash_volume', key='all', severity='notable', usd=sm['total_usd'],
                        title='$%s of $%s priced DEX volume (%.0f%%) is self-matched in %s swaps by %s wallet pairs'
                              % (_m(sm['total_usd']), _m(total), 100 * share, _m(sm.get('swaps')), _m(sm.get('wallet_pairs'))),
                        evidence={'self_matched_usd': sm['total_usd'], 'priced_usd': total, 'share': round(share, 4),
                                  'swaps': sm.get('swaps'), 'wallet_pairs': sm.get('wallet_pairs'),
                                  'method': 'second signer whose token and native-SOL legs mirror the trader inside one tx'}))
    # The washed tokens themselves are evidence, not findings: a pump token lives a day, so a per-mint key would add ten
    # never-recurring ledger rows per window. The venue is the thing that persists.
    tokens = [t for t in (sm.get('by_token') or [])[:10] if t.get('usd', 0) >= WASH_MIN_USD]
    for v in sm.get('by_venue') or []:
        if v.get('usd', 0) >= WASH_MIN_USD and v.get('share_of_venue', 0) >= WASH_MIN_SHARE:
            hits.append(Hit(detector='sol_wash_volume', key='venue:' + v['venue'], severity='notable', usd=v['usd'],
                            title='%s: $%s (%.0f%% of its priced volume) self-matched in %s swaps; top washed tokens %s'
                                  % (v['venue'], _m(v['usd']), 100 * v['share_of_venue'], _m(v['swaps']),
                                     ', '.join('%s $%.1fM' % (t.get('symbol') or short(t['mint']), t['usd'] / 1e6) for t in tokens[:3]) or 'none'),
                            evidence=dict(v, top_tokens=tokens)))
    return hits


def quote_posters(ctx):
    """Programs whose transactions are single-instruction parameter posts from a handful of payers that move no token."""
    hits, agg_tx = [], 0
    for p in ctx.analysis.get('programs') or []:
        if (p.get('tx', 0) >= QUOTE_MIN_TX and p.get('token_move_share', 1) <= QUOTE_MAX_TOKEN_MOVE
                and p.get('unique_payers', 10**9) <= QUOTE_MAX_PAYERS):
            agg_tx += p['tx']
            hits.append(Hit(detector='sol_quote_poster', key=p['program'], severity='info',
                            title='%s: %s txs from %d payer(s), %.1f%% move a token, %.0f%% failed, %.1f SOL fees'
                                  % (p.get('label') or short(p['program']), _m(p['tx']), p['unique_payers'],
                                     100 * p['token_move_share'], 100 * p.get('fail_share', 0), p.get('fee_sol', 0)),
                            evidence={k: p.get(k) for k in ('program', 'label', 'kind', 'tx', 'failed', 'fail_share', 'fee_sol',
                                                             'unique_payers', 'top_payer', 'top_payer_share', 'token_move_share', 'avg_cu')}))
    nonvote = ctx.network.get('nonvote') or 0
    if hits:
        hits.insert(0, Hit(detector='sol_quote_poster', key='all', severity='info',
                           title='%d quote-posting programs sent %s txs = %.1f%% of non-vote transactions'
                                 % (len(hits), _m(agg_tx), 100 * agg_tx / nonvote if nonvote else 0),
                           evidence={'programs': len(hits), 'tx': agg_tx, 'nonvote': nonvote,
                                     'thresholds': {'min_tx': QUOTE_MIN_TX, 'max_token_move_share': QUOTE_MAX_TOKEN_MOVE,
                                                    'max_payers': QUOTE_MAX_PAYERS}}))
    return hits


def failure_spam(ctx):
    """Programs that fail almost every transaction at scale: snipers and arb bots paying base fees to lose races."""
    hits, agg_tx, agg_failed, agg_fee = [], 0, 0, 0.0
    for p in ctx.analysis.get('programs') or []:
        if p.get('tx', 0) >= SPAM_MIN_TX and p.get('fail_share', 0) >= SPAM_MIN_FAIL:
            agg_tx += p['tx']; agg_failed += p.get('failed', 0); agg_fee += p.get('fee_sol', 0)
            hits.append(Hit(detector='sol_failure_spam', key=p['program'], severity='info',
                            title='%s: %s txs, %.0f%% failed, %d payer(s), %.1f SOL fees'
                                  % (p.get('label') or short(p['program']), _m(p['tx']), 100 * p['fail_share'],
                                     p.get('unique_payers') or 0, p.get('fee_sol', 0)),
                            evidence={k: p.get(k) for k in ('program', 'label', 'kind', 'tx', 'failed', 'fail_share', 'fee_sol',
                                                             'unique_payers', 'top_payer', 'top_payer_share')}))
    failed = ctx.network.get('failed') or 0
    if hits:
        hits.insert(0, Hit(detector='sol_failure_spam', key='all', severity='info',
                           title='%d failure bots: %s failed txs = %.1f%% of all failures, %.1f SOL of fees'
                                 % (len(hits), _m(agg_failed), 100 * agg_failed / failed if failed else 0, agg_fee),
                           evidence={'programs': len(hits), 'tx': agg_tx, 'failed': agg_failed, 'window_failed': failed,
                                     'fee_sol': round(agg_fee, 3), 'fee_usd': round(agg_fee * ctx.sol_usd)}))
    return hits


def collector_hubs(ctx):
    """Unlabelled fan-in hubs (many senders, one or two destinations) and fan-out distributors."""
    ex = ctx.analysis.get('exchanges') or {}
    hits = []
    for h in ex.get('unlabelled_fan_in') or []:
        if h.get('unique_senders', 0) >= HUB_MIN_SENDERS:
            usd = (h.get('sol_received') or 0) * ctx.sol_usd
            hits.append(Hit(detector='sol_collector_hub', key='in:' + h['address'], severity='notable', usd=usd,
                            title='%s: %s senders, %.0f SOL in (median %.3f), %d transfer(s) out to %s destination(s)%s'
                                  % (short(h['address']), _m(h['unique_senders']), h.get('sol_received') or 0,
                                     h.get('median_sol') or 0, h.get('out_transfers') or 0, h.get('out_destinations'),
                                     (' — ' + h['label']) if h.get('label') else ''),
                            evidence=dict(h)))
    for d in ex.get('distributors') or []:
        if d.get('out_transfers', 0) >= DISTRIBUTOR_MIN_OUT:
            usd = (d.get('sol_sent') or 0) * ctx.sol_usd
            hits.append(Hit(detector='sol_collector_hub', key='out:' + d['address'], severity='info', usd=usd,
                            title='%s: %s SOL transfers out (%.0f SOL) to %s destinations%s'
                                  % (short(d['address']), _m(d['out_transfers']), d.get('sol_sent') or 0, d.get('destinations'),
                                     (' — ' + d['label']) if d.get('label') else ''),
                            evidence=dict(d)))
    # Sybil clusters reuse the playbook with fresh hub addresses, so the per-hub rows will not recur; the count and the
    # SOL they collect per hour is the finding that can.
    ins = [h for h in hits if h.key.startswith('in:')]
    if ins:
        sol_in = sum(h.evidence.get('sol_received') or 0 for h in ins)
        hits.insert(0, Hit(detector='sol_collector_hub', key='all', severity='notable', usd=sol_in * ctx.sol_usd,
                           title='%d unlabelled fan-in hubs with >=%d senders collected %.0f SOL; %d fan-out distributors with >=%s transfers'
                                 % (len(ins), HUB_MIN_SENDERS, sol_in, len(hits) - len(ins), _m(DISTRIBUTOR_MIN_OUT)),
                           evidence={'hubs': [h.evidence['address'] for h in ins], 'sol_received': round(sol_in, 1),
                                     'distributors': [h.evidence['address'] for h in hits if h.key.startswith('out:')]}))
    return hits


def launch_factories(ctx):
    la = ctx.analysis.get('launches') or {}
    hits = []
    for creator, n in la.get('top_creators') or []:
        if n >= FACTORY_MIN_LAUNCHES:
            hits.append(Hit(detector='sol_launch_factory', key=creator, severity='info',
                            title='%s launched %d tokens in the hour' % (short(creator), n),
                            evidence={'creator': creator, 'launches': n, 'window_launches': la.get('total'),
                                      'unique_creators': la.get('unique_creators')}))
    if la.get('total'):
        hits.insert(0, Hit(detector='sol_launch_factory', key='all', severity='info',
                           title='%s token launches by %s creators; top 3 creators %s'
                                 % (_m(la['total']), _m(la.get('unique_creators')), [n for _, n in (la.get('top_creators') or [])[:3]]),
                           evidence={'total': la['total'], 'unique_creators': la.get('unique_creators'),
                                     'by_program': la.get('by_program')}))
    return hits


def flash_loan_spam(ctx):
    le = ctx.analysis.get('lending') or {}
    hits = []
    for venue, rows in (le.get('flash_payers') or {}).items():
        for payer, n in rows:
            if payer.endswith('(failed)') and n >= FLASH_MIN_FAILED:
                addr = payer.split()[0]
                hits.append(Hit(detector='sol_flash_loan_spam', key='%s:%s' % (venue, addr), severity='info',
                                title='%s: %s failed flash loans on %s, no successes' % (short(addr), _m(n), venue),
                                evidence={'venue': venue, 'payer': addr, 'failed': n,
                                          'co_programs': (le.get('flash_co_programs') or {}).get(addr)}))
    return hits


def liquidation_drought(ctx):
    le = ctx.analysis.get('lending') or {}
    att = le.get('liquidation_attempts') or {}
    failed = sum(v.get('failed', 0) for v in att.values())
    ok = sum(v.get('ok', 0) for v in att.values())
    n = le.get('n_liquidations') or 0
    if n == 0 and (failed or ok == 0):
        return [Hit(detector='sol_liquidation_drought', key='all', severity='info',
                    title='0 liquidations on any lending venue; %s failed attempts (%s)'
                          % (_m(failed), ', '.join('%s %d' % (k, v.get('failed', 0)) for k, v in att.items()) or 'none'),
                    evidence={'attempts': att, 'events': {k: {'tx': v.get('tx'), 'failed': v.get('failed')}
                                                          for k, v in (le.get('events') or {}).items()}})]
    return []


def exchange_flow(ctx):
    hits = []
    for name, f in ((ctx.analysis.get('exchanges') or {}).get('net_flow') or {}).items():
        net = f.get('usd_net') or 0
        if abs(net) >= EXCHANGE_MIN_NET_USD:
            top = sorted((f.get('usd') or {}).items(), key=lambda kv: -abs(kv[1]))[:4]
            hits.append(Hit(detector='sol_exchange_flow', key=name, severity='info', usd=abs(net),
                            title='%s net %s$%s over %s txs (%s)' % (name, '+' if net > 0 else '-', _m(abs(net)), _m(f.get('txs')),
                                                                   ', '.join('%s %+.1fM' % (a, v / 1e6) for a, v in top)),
                            evidence={'exchange': name, 'usd_net': net, 'txs': f.get('txs'), 'usd_by_asset': dict(top),
                                      'sign': 'deposits exceed withdrawals' if net > 0 else 'withdrawals exceed deposits'}))
    return hits


def cctp_unknown_domain(ctx):
    c = ctx.analysis.get('cctp') or {}
    hits = []
    for direction in ('out', 'in'):
        for row in c.get('%s_by_chain' % direction) or []:
            if str(row.get('chain', '')).startswith('domain '):
                hits.append(Hit(detector='sol_cctp_unknown_domain', key='%s:%s' % (direction, row['chain']), severity='info',
                                usd=row.get('usd'),
                                title='CCTP %s to unmapped %s: $%s in %d transfers' % (direction, row['chain'], _m(row.get('usd')), row.get('n', 0)),
                                evidence=dict(row, direction=direction)))
    return hits


def dust_poisoning(ctx):
    hits = []
    for s in (ctx.analysis.get('poisoning') or {}).get('dust_senders') or []:
        if s.get('dust_transfers', 0) >= DUST_MIN_TRANSFERS:
            hits.append(Hit(detector='sol_dust_poisoning', key=s['sender'], severity='info',
                            title='%s: %s dust transfers to %s recipients' % (short(s['sender']), _m(s['dust_transfers']), _m(s.get('recipients'))),
                            evidence=dict(s)))
    return hits


def large_moves(ctx):
    hits, seen = [], set()
    for mv in (ctx.analysis.get('large') or {}).get('moves') or []:
        if (mv.get('usd') or 0) >= LARGE_MIN_USD and mv['owner'] not in seen:
            seen.add(mv['owner'])
            hits.append(Hit(detector='sol_large_move', key=mv['owner'], severity='info', usd=mv['usd'],
                            title='%s %s %s %s in one tx%s' % (short(mv['owner']), 'sent' if (mv.get('delta') or 0) < 0 else 'received',
                                                              '$' + _m(mv['usd']), mv.get('asset'),
                                                              (' — ' + mv['label']) if mv.get('label') else ''),
                            evidence={k: mv.get(k) for k in ('owner', 'label', 'asset', 'delta', 'usd', 'kind', 'sig', 'slot', 'time', 'payer', 'programs')}))
    return hits


def lst_nav_basis(ctx):
    """LST market price (Jupiter head, in SOL) against the on-chain stake-pool NAV. Sanctum's API is not used: it reads 1.9% low."""
    nav = ctx.head.get('stake_pool_nav') or {}
    jp = ctx.head.get('jupiter_prices') or {}
    sol = (jp.get(SOL) or {}).get('usdPrice')
    if not sol or not nav:
        return []
    by_sym = {v['symbol']: m for m, v in MINTS.items() if v.get('class') == 'lst'}
    hits = []
    for sym, n in nav.items():
        mint = by_sym.get(sym)
        px = (jp.get(mint) or {}).get('usdPrice') if mint else None
        if not px or not n.get('nav_sol'):
            continue
        basis_bp = 1e4 * (px / sol / n['nav_sol'] - 1)
        if abs(basis_bp) >= NAV_MIN_BASIS_BP:
            hits.append(Hit(detector='sol_lst_nav_basis', key=sym, severity='notable',
                            title='%s trades %+.0f bp vs on-chain NAV %.5f SOL (epoch %s)' % (sym, basis_bp, n['nav_sol'], n.get('last_update_epoch')),
                            evidence={'lst': sym, 'mint': mint, 'price_sol': px / sol, 'nav_sol': n['nav_sol'], 'basis_bp': round(basis_bp, 1),
                                      'nav_epoch': n.get('last_update_epoch'), 'head_epoch': (ctx.head.get('epoch') or {}).get('epoch'),
                                      'note': 'NAV updates at the epoch boundary; a small positive basis mid-epoch is accrued reward'},
                            economics={'go': None, 'net_apr': None, 'edge_bps': round(abs(basis_bp), 1),
                                       'reason': 'a discount is claimable only through the stake-pool withdraw (unstake at epoch end); '
                                                 'a premium is a mint-and-sell if the pool mints at NAV'}))
    return hits


def stable_rates(ctx):
    """Every stable lending market at the head, joined across Kamino, Save and Jupiter Lend; the widest gap per asset."""
    rows = []
    stable = {v['symbol'] for v in MINTS.values() if v.get('class') in ('stable', 'yield_stable')}
    for mkt in ctx.head.get('kamino_markets') or []:
        for r in mkt.get('reserves') or []:
            if r.get('token') in stable:
                rows.append(('Kamino %s' % mkt['name'].replace(' Market', ''), r['token'], r.get('supply_apy') or 0, r.get('supplied_usd') or 0))
    for r in ctx.head.get('save_main') or []:
        if r.get('symbol') in stable:
            rows.append(('Save main', r['symbol'], r.get('supply_apy') or 0, r.get('supplied_usd') or 0))
    for r in ctx.head.get('jupiter_lend') or []:
        if r.get('asset_symbol') in stable:
            rows.append(('Jupiter Lend', r['asset_symbol'], (r.get('supply_rate_bps') or 0) / 1e4,
                         (r.get('total_assets') or 0) * (r.get('asset_price') or 1)))
    return rows


def stable_rate_gap(ctx):
    rows = [r for r in stable_rates(ctx) if r[3] >= RATE_MIN_SUPPLIED_USD]
    by_asset = {}
    for venue, sym, apy, supplied in rows:
        by_asset.setdefault(sym, []).append((venue, apy, supplied))
    hits = []
    for sym, vs in sorted(by_asset.items()):
        if len(vs) < 2:
            continue
        hi, lo = max(vs, key=lambda x: x[1]), min(vs, key=lambda x: x[1])
        gap = 100 * (hi[1] - lo[1])
        if gap >= RATE_MIN_GAP_PP:
            cap = min(hi[2], lo[2])
            hits.append(Hit(detector='sol_stable_rate_gap', key='%s:%s/%s' % (sym, hi[0], lo[0]), severity='notable',
                            usd=cap * (hi[1] - lo[1]),
                            title='%s pays %.2fpp more on %s (%.2f%%, $%s) than %s (%.2f%%, $%s)'
                                  % (sym, gap, hi[0], 100 * hi[1], _m(hi[2]), lo[0], 100 * lo[1], _m(lo[2])),
                            evidence={'asset': sym, 'high_venue': hi[0], 'low_venue': lo[0], 'gap_pp': round(gap, 3),
                                      'markets': [{'venue': v, 'supply_apy_pct': round(100 * a, 3), 'supplied_usd': round(s)} for v, a, s in vs],
                                      'note': 'head read only (one block); no in-window rate series exists on Solana yet, so this is not de-spiked'},
                            economics={'go': None, 'net_apr': round(hi[1] - lo[1], 5), 'capacity_usd': round(cap),
                                       'reason': 'smaller of the two markets caps the switch; dilution of the high side not modelled'}))
    return hits


def tip_providers(ctx):
    """Tips actually paid (successful txs only) per tip-account provider: Jito, Helius Sender, Astralane, unidentified families."""
    j = ctx.analysis.get('jito') or {}
    by = {}
    for r in j.get('by_tip_account') or []:
        lab = plabel(r['account']) or 'unlabelled'
        prov = lab.split(' tip account')[0].split(' (')[0] if 'tip' in lab else lab
        d = by.setdefault(prov, {'tips_sol': 0.0, 'accounts': 0, 'unique_payers_max': 0})
        d['tips_sol'] += r.get('tips_sol') or 0
        d['accounts'] += 1
        d['unique_payers_max'] = max(d['unique_payers_max'], r.get('unique_payers') or 0)
    total = sum(d['tips_sol'] for d in by.values())
    hits = []
    for prov, d in sorted(by.items(), key=lambda kv: -kv[1]['tips_sol']):
        if d['tips_sol'] <= 0:
            continue
        hits.append(Hit(detector='sol_tip_providers', key=prov, severity='info', usd=d['tips_sol'] * ctx.sol_usd,
                        title='%s: %.1f SOL of tips paid (%.0f%% of all tips) via %d account(s)'
                              % (prov, d['tips_sol'], 100 * d['tips_sol'] / total if total else 0, d['accounts']),
                        evidence=dict(d, share=round(d['tips_sol'] / total, 4) if total else None, total_tips_sol=round(total, 3),
                                      note='tips inside failed transactions revert and are not counted')))
    return hits


DETECTORS = [
    ('sol_wash_volume', 'self-matched swap volume by venue and token', wash_volume),
    ('sol_quote_poster', 'programs that post quotes/parameters without moving tokens', quote_posters),
    ('sol_failure_spam', 'programs failing >=90% of >=20k transactions', failure_spam),
    ('sol_collector_hub', 'unlabelled fan-in hubs and fan-out distributors', collector_hubs),
    ('sol_launch_factory', 'creators launching >=20 tokens per hour', launch_factories),
    ('sol_flash_loan_spam', 'flash-loan payers with hundreds of failures and no success', flash_loan_spam),
    ('sol_liquidation_drought', 'zero liquidations across venues while bots keep trying', liquidation_drought),
    ('sol_exchange_flow', 'net exchange flow above $5M', exchange_flow),
    ('sol_cctp_unknown_domain', 'CCTP domains not in the chain map', cctp_unknown_domain),
    ('sol_dust_poisoning', 'address-poisoning dust senders', dust_poisoning),
    ('sol_large_move', 'single-tx position changes above $5M', large_moves),
    ('sol_lst_nav_basis', 'LST market price vs on-chain stake-pool NAV', lst_nav_basis),
    ('sol_stable_rate_gap', 'same stable lending at different supply rates across venues', stable_rate_gap),
    ('sol_tip_providers', 'tips paid per tip-account provider (Jito, Helius Sender, Astralane, ...)', tip_providers),
]


def run_all(ctx, only=None):
    hits, meta = [], []
    for name, desc, fn in DETECTORS:
        if only and name not in only:
            continue
        t0 = time.monotonic()
        try:
            found = list(fn(ctx) or [])
            err = None
        except Exception as e:  # a broken detector must not silently vanish from the sweep
            found, err = [], '%s: %s' % (type(e).__name__, str(e)[:160])
        meta.append({'detector': name, 'description': desc, 'hits': len(found), 'seconds': round(time.monotonic() - t0, 3), 'error': err})
        hits.extend(found)
    order = {'high': 0, 'notable': 1, 'info': 2}
    hits.sort(key=lambda h: (order.get(h.severity, 3), -(h.usd or 0)))
    return hits, meta


def digest(hits, meta, out):
    L = ['# Solana detectors: %s\n' % out]
    L.append('| detector | hits | error |', )
    L.append('|---|---:|---|')
    for m in meta:
        L.append('| %s | %d | %s |' % (m['detector'], m['hits'], m['error'] or ''))
    L.append('')
    for sev in ('high', 'notable', 'info'):
        rows = [h for h in hits if h.severity == sev]
        if not rows:
            continue
        L.append('## %s (%d)\n' % (sev, len(rows)))
        for h in rows:
            L.append('- `%s` %s' % (h.identity(), h.title))
        L.append('')
    return '\n'.join(L)


# --- diff --------------------------------------------------------------------------------------------------------------

def _get(d, path):
    for p in path.split('.'):
        if not isinstance(d, dict):
            return None
        d = d.get(p)
    return d


def _venue_usd(A, venue):
    for v in _get(A, 'dex.volume_by_venue') or []:
        if v['venue'] == venue:
            return v['usd']
    return 0


def _wash_share(A):
    t = _get(A, 'dex.total_priced_usd') or 0
    s = _get(A, 'dex.self_matched.total_usd') or 0
    return s / t if t else None


def _kind_share(A, kind):
    for k in A.get('kinds') or []:
        if k['kind'] == kind:
            return k['share']
    return None


def _flash_failed(A):
    ev = _get(A, 'lending.events') or {}
    return sum(v.get('flash_borrow_reserve_liquidity (failed)', 0) for v in ev.values())


def _exchange_net(A, name):
    return (_get(A, 'exchanges.net_flow') or {}).get(name, {}).get('usd_net')


METRICS = [
    # (name, unit, extractor)
    ('non-vote TPS', 'tps', lambda A: _get(A, 'network.tps_nonvote')),
    ('failed share of non-vote txs', 'share', lambda A: _get(A, 'network.failed_share')),
    ('non-vote fees', 'SOL', lambda A: _get(A, 'network.fees_sol')),
    ('priority fees', 'SOL', lambda A: _get(A, 'network.priority_fees_sol')),
    ('fees paid by failed txs', 'SOL', lambda A: _get(A, 'network.failed_fees_sol')),
    ('tips paid to tip accounts, all providers (successful txs)', 'SOL', lambda A: _get(A, 'jito.tips_sol')),
    ('swap share of non-vote txs', 'share', lambda A: _kind_share(A, 'swap')),
    ('transfer share of non-vote txs', 'share', lambda A: _kind_share(A, 'transfer')),
    ('priced DEX volume', 'USD', lambda A: _get(A, 'dex.total_priced_usd')),
    ('PumpSwap volume', 'USD', lambda A: _venue_usd(A, 'Pump.fun Amm')),
    ('self-matched (wash) volume', 'USD', lambda A: _get(A, 'dex.self_matched.total_usd')),
    ('wash share of priced volume', 'share', _wash_share),
    ('sandwich patterns in pump pools', 'n', lambda A: _get(A, 'dex.sandwiches.n')),
    ('token launches', 'n', lambda A: _get(A, 'launches.total')),
    ('unique launch creators', 'n', lambda A: _get(A, 'launches.unique_creators')),
    ('pump.fun bonding-curve turnover', 'SOL', lambda A: _get(A, 'pump.sol.bonding_curve_sol')),
    ('pump.fun cashback paid', 'SOL', lambda A: _get(A, 'pump.cashback_sol_received')),
    ('PumpSwap pools created', 'n', lambda A: _get(A, 'pump.counts.pumpswap_pools_created')),
    ('liquidations (all venues)', 'n', lambda A: _get(A, 'lending.n_liquidations')),
    ('failed Kamino flash loans', 'n', _flash_failed),
    ('USDC net issuance', 'USD', lambda A: _get(A, 'issuance.by_mint.USDC.net')),
    ('CCTP out', 'USD', lambda A: _get(A, 'cctp.out_total')),
    ('CCTP in', 'USD', lambda A: _get(A, 'cctp.in_total')),
    ('Binance net flow', 'USD', lambda A: _exchange_net(A, 'Binance')),
    ('SOL price (in-window median)', 'USD', lambda A: _get(A, 'price_basis.sol_usd_median')),
    ('block producers', 'n', lambda A: _get(A, 'leaders.n_leaders')),
    ('skipped slots', 'n', lambda A: _get(A, 'window.skipped_slots')),
]


def fmt(v, unit):
    if v is None:
        return '–'
    if unit == 'share':
        return '%.1f%%' % (100 * v)
    if unit == 'USD':
        return '$' + _m(v)
    if unit == 'SOL':
        return '%.1f' % v
    if unit == 'tps':
        return '%.0f' % v
    return _m(v)


def delta(a, b):
    if a is None or b is None:
        return None
    if a == 0:
        return None
    return (b - a) / abs(a)


def top_set(A, field, key, n, min_tx=0):
    rows = [r for r in (A.get(field) or []) if r.get('tx', 0) >= min_tx][:n]
    return {r[key]: r for r in rows}


def compute_diff(prev, cur):
    """Everything that changed between two Solana windows, in one JSON a reader or a narrative can consume."""
    metrics = []
    for name, unit, fn in METRICS:
        a, b = fn(prev), fn(cur)
        metrics.append({'metric': name, 'unit': unit, 'prev': a, 'cur': b, 'delta': delta(a, b)})
    P, C = top_set(prev, 'programs', 'program', 40), top_set(cur, 'programs', 'program', 40)
    programs = {
        'entered': [{'program': k, 'label': v.get('label'), 'tx': v['tx'], 'kind': v.get('kind')} for k, v in C.items() if k not in P],
        'left': [{'program': k, 'label': v.get('label'), 'tx': v['tx'], 'kind': v.get('kind')} for k, v in P.items() if k not in C],
        'moved': sorted([{'program': k, 'label': v.get('label'), 'prev_tx': P[k]['tx'], 'cur_tx': v['tx'], 'delta': delta(P[k]['tx'], v['tx'])}
                         for k, v in C.items() if k in P and P[k]['tx'] and abs(v['tx'] / P[k]['tx'] - 1) >= 0.5],
                        key=lambda r: -abs(r['delta'])),
    }

    def names(A, path, key, n=10):
        rows = _get(A, path) or []
        out = []
        for r in rows[:n]:
            out.append(r[key] if isinstance(r, dict) else r[0])
        return out

    actors = {}
    for label, path, key in (('wash_tokens', 'dex.self_matched.by_token', 'mint'),
                             ('fan_in_hubs', 'exchanges.unlabelled_fan_in', 'address'),
                             ('distributors', 'exchanges.distributors', 'address'),
                             ('top_payers', 'payers', 'payer'),
                             ('top_fee_payers', 'top_fee_payers', 'payer'),
                             ('launch_creators', 'launches.top_creators', 0),
                             ('dust_senders', 'poisoning.dust_senders', 'sender'),
                             ('top_pairs', 'dex.top_pairs', 'pair')):
        p, c = names(prev, path, key), names(cur, path, key)
        actors[label] = {'prev': p, 'cur': c, 'persisting': [x for x in c if x in p]}
    return {'prev': prev.get('window'), 'cur': cur.get('window'), 'coverage': {'prev': coverage(prev), 'cur': coverage(cur)},
            'metrics': metrics, 'programs': programs, 'actors': actors}


def coverage(A):
    """Share of the window's produced slots that were analysed. Totals of a partial window are not comparable; shares are."""
    w = A.get('window') or {}
    prod = w.get('produced_slots') or 0
    return (w.get('blocks_analyzed') or 0) / prod if prod else None


def render_diff(D, prev_out, cur_out):
    L = ['## Change since the previous Solana window\n',
         'Previous: `%s` (%s to %s). Current: `%s` (%s to %s). Deterministic, from the two `analysis.json` files; '
         'deltas are relative to the previous window.\n' % (prev_out, D['prev']['start_utc'], D['prev']['end_utc'],
                                                             cur_out, D['cur']['start_utc'], D['cur']['end_utc'])]
    cov = D.get('coverage') or {}
    partial = [k for k in ('prev', 'cur') if cov.get(k) is not None and cov[k] < 0.99]
    if partial:
        L.append('**Partial window(s):** %s. Totals (fees, volume, launches, flows) of a partial window are not comparable '
                 'and are marked ~; shares, rates and TPS are.\n'
                 % ', '.join('%s analysed %.1f%% of its produced slots' % (k, 100 * cov[k]) for k in partial))
    L.append('| metric | previous | current | change |')
    L.append('|---|---:|---:|---:|')
    for m in D['metrics']:
        d = m['delta']
        total = m['unit'] in ('USD', 'SOL', 'n') and m['metric'] not in ('block producers', 'skipped slots', 'SOL price (in-window median)')
        mark = '~' if partial and total else ''
        L.append('| %s | %s | %s | %s |' % (m['metric'], mark + fmt(m['prev'], m['unit']), mark + fmt(m['cur'], m['unit']),
                                            (mark + '%+.0f%%' % (100 * d)) if d is not None else '–'))
    L.append('')
    pr = D['programs']
    if pr['entered']:
        L.append('**Programs entering the top 40 by transactions:** ' + '; '.join(
            '%s (%s, %s txs)' % (r['label'] or short(r['program']), r.get('kind') or '?', _m(r['tx'])) for r in pr['entered']) + '.\n')
    if pr['left']:
        L.append('**Programs leaving the top 40:** ' + '; '.join(
            '%s (%s txs last time)' % (r['label'] or short(r['program']), _m(r['tx'])) for r in pr['left']) + '.\n')
    if pr['moved']:
        L.append('**Programs whose transaction count moved by 50% or more:** ' + '; '.join(
            '%s %s → %s (%+.0f%%)' % (r['label'] or short(r['program']), _m(r['prev_tx']), _m(r['cur_tx']), 100 * r['delta']) for r in pr['moved'][:12]) + '.\n')
    L.append('| named actors (top 10) | previous | current | still present |')
    L.append('|---|---:|---:|---|')
    for k, v in D['actors'].items():
        L.append('| %s | %d | %d | %s |' % (k.replace('_', ' '), len(v['prev']), len(v['cur']),
                                            ', '.join(short(x) for x in v['persisting']) or 'none'))
    L.append('')
    return '\n'.join(L)


# --- CLI ---------------------------------------------------------------------------------------------------------------

def cmd_detect(a):
    ctx = Context(a.out)
    hits, meta = run_all(ctx, only=a.only)
    out = Path(a.out)
    (out / 'detectors.json').write_text(json.dumps(
        {'window': str(a.out), 'chain': 'solana', 'detectors': meta, 'hits': [h.as_dict() for h in hits],
         'sol_usd': ctx.sol_usd, 'thresholds': {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float)) and k not in ('SOL',)}},
        indent=1, default=str) + '\n')
    (out / 'detectors.md').write_text(digest(hits, meta, a.out) + '\n')
    for m in meta:
        print('%-26s %3d hit(s)  %5.2fs  %s' % (m['detector'], m['hits'], m['seconds'], m['error'] or ''))
    print()
    for h in hits:
        print('[%-7s] %s' % (h.severity, h.title))
    print('\nwrote %s and %s' % (out / 'detectors.json', out / 'detectors.md'))
    if any(m['error'] for m in meta):
        raise SystemExit('detector errors; refusing to report a complete sweep')


def cmd_diff(a):
    prev = json.loads((Path(a.prev) / 'analysis.json').read_text())
    cur = json.loads((Path(a.out) / 'analysis.json').read_text())
    D = compute_diff(prev, cur)
    D['prev_out'], D['cur_out'] = str(a.prev), str(a.out)
    out = Path(a.out)
    (out / 'diff.json').write_text(json.dumps(D, indent=1, default=str) + '\n')
    md = render_diff(D, a.prev, a.out)
    (out / 'diff.md').write_text(md + '\n')
    print(md)
    print('wrote %s and %s' % (out / 'diff.json', out / 'diff.md'))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('detect'); d.add_argument('--out', required=True); d.add_argument('--only', nargs='*')
    f = sub.add_parser('diff'); f.add_argument('--out', required=True); f.add_argument('--prev', required=True)
    a = p.parse_args()
    {'detect': cmd_detect, 'diff': cmd_diff}[a.cmd](a)


if __name__ == '__main__':
    main()
