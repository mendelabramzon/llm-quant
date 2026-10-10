#!/usr/bin/env python3
"""Direct measurement of every chain in `scripts/chain_registry.json`: transactions and per-asset transfer value over a
window, read from the chain itself rather than from an aggregator.

Why both this and `chain_census.py`. The census reads DefiLlama, growthepie, L2Beat, Blockchair and Tronscan for several
hundred chains with daily history, which is what makes a baseline possible on day one. But an aggregator is a day late,
counts only what its adapters were written for, and does not say which *assets* moved. This probe reads the chain: a
cumulative counter where the chain keeps one, a stratified block sample where it does not, and every token transfer in
the sampled blocks priced by contract address — so a token that starts carrying value on a chain shows up the day it
does, whether or not anyone has written an adapter for it. `chain_activity.py verify` compares the two readings.

    uv run --with pycryptodome python scripts/chain_probe.py one ethereum --hours 1 --samples 20     # print one chain
    uv run --with pycryptodome python scripts/chain_probe.py run --out research/2026-10-09/chains --hours 24
    uv run --with pycryptodome python scripts/chain_probe.py run --out ... --chains base,solana,tron --samples 300
    uv run --with pycryptodome python scripts/chain_probe.py history --days 14 --probe research/2026-10-09/chains/probe.json
    uv run --with pycryptodome python scripts/chain_probe.py list                                   # the registry

Output: `<out>/probe/<slug>.json` per chain and `<out>/probe.json` (all chains, plus failures). Nothing is signed or
sent; every call is a public read. Keys (Infura, GetBlock) are read from the gitignored files and never written out.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import chain_adapters as CA  # noqa: E402

REGISTRY = ROOT / 'scripts' / 'chain_registry.json'


def load_registry():
    return json.loads(REGISTRY.read_text())


def chains_by_slug():
    return {c['slug']: c for c in load_registry()['chains']}


class Ctx:
    """What every adapter gets: the window, the sample size, one price cache, and a few switches."""

    def __init__(self, start_ts, end_ts, samples=200, out=None, no_infura=False, verbose=False):
        self.start_ts, self.end_ts = int(start_ts), int(end_ts)
        self.samples = samples
        self.out = Path(out) if out else None
        cache = (self.out / 'cache' / 'prices.json') if self.out else None
        self.prices = CA.Prices(cache=cache)
        self.no_infura = no_infura
        self.verbose = verbose

    def log(self, *a):
        if self.verbose:
            print(*a, file=sys.stderr, flush=True)


def window(args):
    if args.day:
        if args.day == 'yesterday':
            args.day = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime('%Y-%m-%d')
        d = dt.datetime.strptime(args.day, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc)
        return int(d.timestamp()), int((d + dt.timedelta(days=1)).timestamp())
    end = int(time.time()) // 60 * 60 - 60 * int(args.lag_minutes)
    if args.end:
        end = int(dt.datetime.fromisoformat(args.end.replace('Z', '+00:00')).timestamp())
    return end - int(args.hours * 3600), end


def probe_one(cfg, ctx):
    fams = CA.load_all()
    adapter = (cfg.get('probe') or {}).get('adapter') or cfg.get('family')
    fn = fams.get(adapter)
    if fn is None:
        return {'chain': cfg['slug'], 'ok': False, 'error': 'no adapter for %r' % adapter}
    t0 = time.time()
    try:
        r = fn(cfg, ctx)
        r.update({'chain': cfg['slug'], 'name': cfg.get('name'), 'family': cfg.get('family'), 'adapter': adapter,
                  'ok': True, 'probed_at': CA.utc(time.time())})
        return r
    except Exception as e:
        return {'chain': cfg['slug'], 'name': cfg.get('name'), 'family': cfg.get('family'), 'adapter': adapter,
                'ok': False, 'error': '%s: %s' % (type(e).__name__, str(e)[:300]),
                'trace': traceback.format_exc()[-1500:], 'seconds': round(time.time() - t0, 1),
                'probed_at': CA.utc(time.time())}


def summary_line(r):
    if not r.get('ok'):
        return '%-14s FAILED  %s' % (r['chain'], r.get('error', '')[:110])
    tx = r.get('tx') or {}
    tr = r.get('transfers') or {}
    top = ', '.join('%s %s' % (a.get('symbol') or a['asset'][:10], fmt_usd(a.get('usd'))) for a in (tr.get('assets') or [])[:4])
    se = tx.get('se')
    return '%-14s tx %s%s (%s)  transfers %s  [%s]  %ss' % (
        r['chain'], fmt_n(tx.get('count')), (' ±%s' % fmt_n(se)) if se else '', tx.get('method'),
        fmt_usd(tr.get('priced_usd')), top, r.get('seconds'))


def fmt_n(v):
    if v is None:
        return '-'
    v = float(v)
    for unit, d in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= d:
            return '%.2f%s' % (v / d, unit)
    return '%.0f' % v


def fmt_usd(v):
    return '-' if v is None else '$' + fmt_n(v)


def cmd_one(args):
    cfg = chains_by_slug()[args.chain]
    s, e = window(args)
    ctx = Ctx(s, e, samples=args.samples, out=args.out, no_infura=args.no_infura, verbose=True)
    r = probe_one(cfg, ctx)
    print(json.dumps(r, indent=1, default=str)[:args.max_chars])
    print(summary_line(r), file=sys.stderr)


def cmd_run(args):
    out = Path(args.out)
    reg = chains_by_slug()
    want = [c.strip() for c in args.chains.split(',')] if args.chains else list(reg)
    skip = set(x.strip() for x in (args.skip or '').split(',') if x.strip())
    want = [c for c in want if c in reg and c not in skip]
    s, e = window(args)
    ctx = Ctx(s, e, samples=args.samples, out=out, no_infura=args.no_infura, verbose=args.verbose)
    pdir = out / 'probe'
    pdir.mkdir(parents=True, exist_ok=True)
    results = {}
    t0 = time.time()
    # Solana and the paced explorers are slow; run them first so they overlap the EVM sweep
    order = sorted(want, key=lambda c: (0 if reg[c].get('family') in ('solana', 'ton', 'tron', 'stellar', 'xrpl') else 1, c))
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(probe_one, reg[c], ctx): c for c in order}
        for f in cf.as_completed(futs):
            c = futs[f]
            r = f.result()
            results[c] = r
            (pdir / ('%s.json' % c)).write_text(json.dumps(r, indent=1, default=str))
            print(summary_line(r), flush=True)
    meta = {'window': CA.window_dict(s, e), 'samples': args.samples, 'chains': len(want),
            'ok': sorted(c for c, r in results.items() if r.get('ok')),
            'failed': {c: r.get('error') for c, r in results.items() if not r.get('ok')},
            'seconds': round(time.time() - t0, 1), 'generated_utc': CA.utc(time.time()),
            'registry_sha': CA.sha(REGISTRY.read_text())}
    merged = {'meta': meta, 'chains': {c: results[c] for c in sorted(results)}}
    if args.merge and (out / 'probe.json').exists():
        old = json.loads((out / 'probe.json').read_text())
        old_chains = old.get('chains') or {}
        old_chains.update(merged['chains'])
        merged['chains'] = dict(sorted(old_chains.items()))
        meta['merged_into_existing'] = True
        meta['ok'] = sorted(c for c, r in merged['chains'].items() if r.get('ok'))
        meta['failed'] = {c: r.get('error') for c, r in merged['chains'].items() if not r.get('ok')}
    (out / 'probe.json').write_text(json.dumps(merged, indent=1, default=str))
    print(json.dumps({'ok': len(meta['ok']), 'failed': len(meta['failed']), 'seconds': meta['seconds']}))


HISTORY = ROOT / 'research' / 'chains' / 'tx_history.jsonl'


def load_history():
    rows = {}
    if HISTORY.exists():
        for line in HISTORY.read_text().splitlines():
            if line.strip():
                x = json.loads(line)
                rows[(x['chain'], x['day'])] = x
    return rows


def cmd_history(args):
    """Daily transaction counts for the last N complete UTC days: the baseline a probe-measured chain needs before
    a detector can call its activity new. Writes research/chains/tx_history.jsonl (one row per chain-day; existing
    rows are kept unless --refresh). Adapters that support `ctx.tx_only` skip the transfer read; the rest run as usual."""
    reg = chains_by_slug()
    want = [c.strip() for c in args.chains.split(',')] if args.chains else list(reg)
    want = [c for c in want if c in reg]
    latest = {}
    if args.probe and Path(args.probe).exists():
        latest = (json.loads(Path(args.probe).read_text()).get('chains') or {})
    today = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    days = [today - dt.timedelta(days=i) for i in range(1, args.days + 1)]
    have = load_history()
    lock = __import__('threading').Lock()

    def save():
        with lock:
            HISTORY.parent.mkdir(parents=True, exist_ok=True)
            rows = sorted(have.values(), key=lambda x: (x['chain'], x['day']))
            HISTORY.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in rows))

    CA.load_all()          # adapters register their history functions on import
    fams_h = CA.HISTORY

    def one_chain(slug):
        cfg = dict(reg[slug])
        ltx = (latest.get(slug) or {}).get('tx') or {}
        spb = ltx.get('system_per_block')
        if spb is None and ltx.get('system_count') is not None and ltx.get('blocks'):
            spb = ltx['system_count'] / ltx['blocks']
        if spb is not None:
            cfg['_system_per_block'] = round(spb)   # a block format constant: 0 or 1 system transaction per block
        out_rows = []
        todo = [d for d in days if args.refresh or not (have.get((slug, d.strftime('%Y-%m-%d'))) or {}).get('ok')]
        if not todo:
            return out_rows
        adapter = (cfg.get('probe') or {}).get('adapter') or cfg.get('family')
        if adapter in fams_h:
            ctx = Ctx(min(todo).timestamp(), (max(todo) + dt.timedelta(days=1)).timestamp(), samples=args.samples,
                      out=None, no_infura=args.no_infura)
            try:
                got = fams_h[adapter](cfg, ctx, [d.timestamp() for d in todo], args.samples)
                err = None
            except Exception as e:
                got, err = [], '%s: %s' % (type(e).__name__, str(e)[:200])
            for g in got:
                day = dt.datetime.fromtimestamp(g['day_start'], dt.timezone.utc).strftime('%Y-%m-%d')
                row = {'chain': slug, 'day': day, 'ok': bool(g.get('count')) and g['count'] > 0, 'count': g.get('count'),
                       'se': g.get('se'), 'method': g.get('method'), 'samples': g.get('sampled'), 'error': None,
                       'probed_at': CA.utc(time.time()), 'source': 'backfill'}
                with lock:
                    have[(slug, day)] = row
                out_rows.append(row)
            print('%-13s %d day(s) %s' % (slug, len(got), ('FAILED ' + err) if err else 'ok'), flush=True)
            save()
            return out_rows
        for d in todo:
            day = d.strftime('%Y-%m-%d')
            ctx = Ctx(d.timestamp(), (d + dt.timedelta(days=1)).timestamp(), samples=args.samples, out=None,
                      no_infura=args.no_infura)
            ctx.tx_only = True
            r = probe_one(cfg, ctx)
            tx = r.get('tx') or {}
            row = {'chain': slug, 'day': day, 'ok': bool(r.get('ok') and tx.get('count')) and tx['count'] > 0,
                   'count': tx.get('count'), 'se': tx.get('se'), 'method': tx.get('method'),
                   'samples': tx.get('sampled'), 'error': r.get('error'), 'probed_at': r.get('probed_at'),
                   'source': 'backfill'}
            out_rows.append(row)
            with lock:
                have[(slug, day)] = row
            print('%-13s %s %s %s' % (slug, day, fmt_n(row['count']) if row['ok'] else 'FAILED ' + str(row['error'])[:80], row['method'] or ''), flush=True)
        save()
        return out_rows

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(one_chain, want))
    save()
    print(json.dumps({'rows': len(have), 'chains': len({x[0] for x in have})}))


def cmd_assemble(args):
    """Rebuild <out>/probe.json from the per-chain files in <out>/probe/ — after an interrupted or partial run."""
    out = Path(args.out)
    chains = {}
    for f in sorted((out / 'probe').glob('*.json')):
        r = json.loads(f.read_text())
        chains[r.get('chain') or f.stem] = r
    ok = {c: r for c, r in chains.items() if r.get('ok')}
    wins = {json.dumps((r.get('window') or {}).get('start_ts')) + json.dumps((r.get('window') or {}).get('end_ts')) for r in ok.values()}
    first = next(iter(ok.values()), {}) if ok else {}
    meta = {'window': first.get('window'), 'chains': len(chains), 'ok': sorted(ok),
            'failed': {c: r.get('error') for c, r in chains.items() if not r.get('ok')},
            'windows_differ': len(wins) > 1, 'generated_utc': CA.utc(time.time()),
            'registry_sha': CA.sha(REGISTRY.read_text()), 'assembled': True}
    (out / 'probe.json').write_text(json.dumps({'meta': meta, 'chains': chains}, indent=1, default=str))
    print(json.dumps({'chains': len(chains), 'ok': len(ok), 'failed': len(meta['failed']), 'windows_differ': meta['windows_differ']}))


def cmd_list(args):
    reg = load_registry()
    for c in reg['chains']:
        print('%-14s %-12s %-9s %s' % (c['slug'], c['family'], c.get('layer', ''), c.get('why', '')[:90]))
    print('\ncensus only (no adapter yet): ' + ', '.join(x['name'] for x in reg.get('census_only', [])))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('one', 'run'):
        a = sub.add_parser(name)
        if name == 'one':
            a.add_argument('chain')
            a.add_argument('--max-chars', type=int, default=6000)
        a.add_argument('--out', default=None if name == 'one' else None, required=(name == 'run'))
        a.add_argument('--hours', type=float, default=24.0)
        a.add_argument('--day', help="a complete UTC day YYYY-MM-DD (or 'yesterday') instead of a trailing window; "
                                     'aligns the probe with the aggregators\' daily figures so verify compares like with like')
        a.add_argument('--end', help='window end (ISO, UTC); default now minus --lag-minutes')
        a.add_argument('--lag-minutes', type=int, default=2, help='end the trailing window this far back so heads are final')
        a.add_argument('--samples', type=int, default=200, help='sampled blocks per chain (adapters may override)')
        a.add_argument('--no-infura', action='store_true')
        if name == 'run':
            a.add_argument('--chains', help='comma list of slugs (default: whole registry)')
            a.add_argument('--skip', help='comma list of slugs to leave out')
            a.add_argument('--workers', type=int, default=6)
            a.add_argument('--merge', action='store_true', help='merge into an existing probe.json instead of replacing it')
            a.add_argument('-v', '--verbose', action='store_true')
    h = sub.add_parser('history', help='daily transaction counts for the last N UTC days (the probe baseline)')
    h.add_argument('--days', type=int, default=14)
    h.add_argument('--samples', type=int, default=40)
    h.add_argument('--chains')
    h.add_argument('--workers', type=int, default=8)
    h.add_argument('--probe', help='a probe.json whose per-block system-transaction rates the EVM backfill should use')
    h.add_argument('--refresh', action='store_true')
    h.add_argument('--no-infura', action='store_true')
    sa = sub.add_parser('assemble', help='rebuild probe.json from the per-chain files after an interrupted run')
    sa.add_argument('--out', required=True)
    sub.add_parser('list')
    args = p.parse_args()
    {'one': cmd_one, 'run': cmd_run, 'list': cmd_list, 'history': cmd_history, 'assemble': cmd_assemble}[args.cmd](args)


if __name__ == '__main__':
    main()
