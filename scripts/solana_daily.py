#!/usr/bin/env python3
"""One unattended pass of the Solana loop: collect a trailing window, analyse it, run the detectors, diff it against the
previous Solana window, render, and fold the hits into the shared findings ledger.

Why. The first Solana window (2026-09-07) was a one-off: eight scripts run by hand in the right order, a narrative, and
nothing that ran again. The second window (2026-09-10) added `solana_detect.py` (detectors + diff) so a window is
compared with its predecessor and its hits accumulate in `research/findings.jsonl`. This runner is the sequence a
session would type, so the loop can run without one (launchd template in `scripts/launchd/`), and it appends one line
per pass to `research/solana_daily_log.md` for the next session to read first.

Cost. A full hour of chain is ~11.3k blocks, ~8.5 GB compact and ~100 minutes over the GetBlock tokens (bandwidth-bound
at ~1.8 blocks/s from this machine), plus ~12 minutes of analysis. `--every K` samples every K-th block (K=4 is ~25
minutes and ~2 GB). `solana_scan analyze` does not scale a sampled window up: its totals (transactions, fees, volume,
launches) are then ~1/K of the hour while shares, rates and per-program shapes hold, so a sampled window is for the
diff's ratios and the detectors' shapes, not for headline totals, and `diff` against a full window will show every total
down by ~K. `--prune-blocks` deletes the block files after the pass; the analysis, detector
and diff artifacts are all that the ledger and the next diff need, and 37 GB of free disk is four unpruned windows.

    uv run python scripts/solana_daily.py run                       # trailing hour under research/<UTC date>/solana_daily
    uv run python scripts/solana_daily.py run --every 4 --prune-blocks
    uv run python scripts/solana_daily.py run --out research/2026-09-10/solana_live --skip collect   # finish a window collected by hand
    uv run python scripts/solana_daily.py plan
"""
import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'research' / 'solana_daily_log.md'


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def latest_prior_window(today_out):
    """The most recent analysed Solana window other than this one: what `diff` compares against."""
    cands = []
    for p in ROOT.glob('research/*/solana_*'):
        if p.is_dir() and p.resolve() != Path(today_out).resolve() and (p / 'analysis.json').exists():
            cands.append(p)
    cands.sort(key=lambda p: (p / 'analysis.json').stat().st_mtime)
    # Relative to the repo root: the ledger and the diff name windows by their repo path.
    return cands[-1].relative_to(ROOT) if cands else None


def steps(out, hours, every, workers, prior):
    py = [sys.executable]
    S = [
        ('collect', py + ['scripts/solana_collect.py', 'collect', '--out', str(out), '--hours', str(hours), '--every', str(every), '--workers', str(workers)]),
        ('verify collection', py + ['scripts/solana_collect.py', 'verify', '--out', str(out)]),
        ('head state', py + ['scripts/solana_scan.py', 'head', '--out', str(out)]),
        ('prices', py + ['scripts/solana_scan.py', 'prices', '--out', str(out)]),
        ('analyze', py + ['scripts/solana_scan.py', 'analyze', '--out', str(out)]),
        ('detect', py + ['scripts/solana_detect.py', 'detect', '--out', str(out)]),
    ]
    if prior is not None:
        S.append(('diff', py + ['scripts/solana_detect.py', 'diff', '--out', str(out), '--prev', str(prior)]))
    S += [
        ('verify analysis', py + ['scripts/solana_scan.py', 'verify', '--out', str(out)]),
        ('render', py + ['scripts/solana_scan.py', 'render', '--out', str(out)]),
        ('ingest', py + ['scripts/findings.py', 'ingest', '--out', str(out), '--chain', 'solana']),
    ]
    return S


def summarise(out, prior):
    """One line for the log: the numbers a reader would compare first, and the notable hits."""
    row = {'utc': utc_now().isoformat(timespec='seconds'), 'window': str(Path(out).resolve().relative_to(ROOT)),
           'prior_window': str(prior) if prior else None}
    try:
        A = json.loads((out / 'analysis.json').read_text())
        n, d = A['network'], A['dex']
        row['nonvote_tps'] = round(n['tps_nonvote'])
        row['failed_share'] = round(n['failed_share'], 3)
        row['priced_dex_usd'] = round(d['total_priced_usd'])
        row['wash_share'] = round((d.get('self_matched') or {}).get('total_usd', 0) / d['total_priced_usd'], 3) if d.get('total_priced_usd') else None
        row['launches'] = (A.get('launches') or {}).get('total')
        row['liquidations'] = (A.get('lending') or {}).get('n_liquidations')
        row['sol_usd'] = A['price_basis']['sol_usd_median']
    except Exception as e:  # noqa: BLE001
        row['analysis_error'] = str(e)[:120]
    try:
        D = json.loads((out / 'detectors.json').read_text())
        row['hits'] = len(D['hits'])
        row['notable'] = [h['identity'] for h in D['hits'] if h['severity'] in ('high', 'notable')][:12]
        row['detector_errors'] = [m['detector'] for m in D['detectors'] if m.get('error')]
    except Exception as e:  # noqa: BLE001
        row['detectors_error'] = str(e)[:120]
    try:
        V = json.loads((out / 'verify.json').read_text())
        row['verify_ok'] = V.get('all_ok', V.get('ok'))
    except Exception as e:  # noqa: BLE001
        row['verify_error'] = str(e)[:120]
    return row


def cmd_run(args):
    out = Path(args.out) if args.out else ROOT / 'research' / utc_now().strftime('%Y-%m-%d') / 'solana_daily'
    if not args.out and (out / 'manifest.json').exists() and not args.force:
        raise SystemExit('%s already has a window today; pass --force to collect another or --out to finish it' % out)
    out.mkdir(parents=True, exist_ok=True)
    prior = latest_prior_window(out)
    S = [(n, c) for n, c in steps(out, args.hours, args.every, args.workers, prior) if n not in (args.skip or [])]
    results, t0 = [], time.time()
    for name, cmd in S:
        t = time.time()
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        results.append({'step': name, 'returncode': r.returncode, 'seconds': round(time.time() - t, 1),
                        'tail': (r.stdout or '').strip().splitlines()[-3:],
                        'stderr_tail': (r.stderr or '').strip().splitlines()[-3:] if r.returncode else []})
        print(json.dumps(results[-1]), flush=True)
        if r.returncode and name in ('collect', 'analyze', 'detect'):
            break   # nothing downstream means anything without these
    row = summarise(out, prior)
    row['steps'] = [{k: v for k, v in x.items() if k in ('step', 'returncode', 'seconds')} for x in results]
    row['seconds'] = round(time.time() - t0, 1)
    row['every'] = args.every
    if args.prune_blocks and (out / 'analysis.json').exists() and not any(x['returncode'] for x in results):
        n = sum(1 for _ in (out / 'blocks').glob('*'))
        shutil.rmtree(out / 'blocks', ignore_errors=True)
        row['pruned_blocks'] = n
    (out / 'daily_run.json').write_text(json.dumps(row, indent=1) + '\n')
    line = '- %s `%s` vs `%s`: nonvote_tps=%s failed=%s dex=$%s wash=%s launches=%s liq=%s hits=%s notable=%s verify=%s steps_failed=%s (%.0fs)' % (
        row['utc'], row['window'], row.get('prior_window'), row.get('nonvote_tps'), row.get('failed_share'),
        format(row.get('priced_dex_usd') or 0, ','), row.get('wash_share'), row.get('launches'), row.get('liquidations'),
        row.get('hits'), json.dumps(row.get('notable')), row.get('verify_ok'), [x['step'] for x in results if x['returncode']], row['seconds'])
    if not LOG.exists():
        LOG.write_text('# Solana daily log\n\nOne line per pass of `scripts/solana_daily.py`. Read this before a session; the '
                       'per-window `diff.md` and `detectors.md` carry the detail.\n\n')
    with LOG.open('a') as f:
        f.write(line + '\n')
    print(line)
    return 0 if not any(x['returncode'] for x in results) else 1


def cmd_plan(args):
    out = Path(args.out) if args.out else ROOT / 'research' / utc_now().strftime('%Y-%m-%d') / 'solana_daily'
    for name, cmd in steps(out, args.hours, args.every, args.workers, latest_prior_window(out)):
        print('%-20s %s' % (name, ' '.join(str(c) for c in cmd[1:])))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name, fn in (('run', cmd_run), ('plan', cmd_plan)):
        s = sub.add_parser(name); s.set_defaults(fn=fn)
        s.add_argument('--out', default=None, help='window directory (default research/<date>/solana_daily)')
        s.add_argument('--hours', type=float, default=1.0)
        s.add_argument('--every', type=int, default=1, help='collect every K-th block; 1 = every block (~100 min per hour)')
        s.add_argument('--workers', type=int, default=8)
        if name == 'run':
            s.add_argument('--skip', nargs='*', help='step names to skip, e.g. collect when the blocks are already on disk')
            s.add_argument('--prune-blocks', action='store_true', help='delete block files after a clean pass')
            s.add_argument('--force', action='store_true')
    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == '__main__':
    main()
