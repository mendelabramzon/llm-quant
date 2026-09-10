#!/usr/bin/env python3
"""One unattended pass of the perp loop: a window, its references, the detectors, the ledger, the book, the history.

Why. The 2026-09-10 state review found that the loop only ran while a session was open: forty findings were past
their recheck cadence and the highest-EV thread had one window. The perp side of the loop reads public, unauthenticated
endpoints, so a daily pass costs nothing but a few minutes of machine time. This runner does the sequence a session
would do, one step at a time (the venue's per-IP limiter throttles concurrent collectors), and appends one line per
day to a log the next session can read before anything else.

    uv run python scripts/perp_daily.py run                 # today's pass, under research/<UTC date>/perps_daily
    uv run python scripts/perp_daily.py run --minutes 4     # shorter reference sampling
    uv run python scripts/perp_daily.py plan                # print the steps without running them

Install as a daily job with launchd (macOS): copy `scripts/launchd/com.llm-quant.perp-daily.plist` to
`~/Library/LaunchAgents/`, edit the two absolute paths, then `launchctl load ~/Library/LaunchAgents/com.llm-quant.perp-daily.plist`.
The template runs at 19:00 local time (15:00 UTC in Asia/Tbilisi), when both US cash equities and the futures are open,
so the equity references are live rather than stale closes.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'research' / '2026-09-10' / 'perps_history'   # the accumulating store; started 2026-09-10 from 1 July
LOG = ROOT / 'research' / 'perps_daily_log.md'


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def steps(out, history, minutes, prior_window):
    py = [sys.executable]
    S = []
    S.append(('history append', py + ['scripts/perp_history.py', 'collect', '--out', str(history), '--since', '2026-07-01',
                                      '--workers', '2', '--interval', '0.15']))
    S.append(('window', py + ['scripts/perp_collect.py', 'window', '--out', str(out), '--hours', '1', '--workers', '3',
                              '--interval', '0.12']))
    S.append(('references', py + ['scripts/perp_refs.py', 'snap', '--out', str(out), '--minutes', str(minutes), '--every', '60']))
    S.append(('analyze', py + ['scripts/perp_scan.py', 'analyze', '--out', str(out)]))
    S.append(('tape from reference snapshots', py + ['scripts/perp_scan.py', 'tape', '--out', str(out)]))
    S.append(('compare', py + ['scripts/perp_refs.py', 'compare', '--out', str(out)]))
    S.append(('curve', py + ['scripts/perp_refs.py', 'curve', '--out', str(out)]))
    S.append(('detect', py + ['scripts/perp_scan.py', 'detect', '--out', str(out)]))
    S.append(('verify', py + ['scripts/perp_scan.py', 'verify', '--out', str(out)]))
    S.append(('render', py + ['scripts/perp_scan.py', 'render', '--out', str(out)]))
    S.append(('ingest', py + ['scripts/findings.py', 'ingest', '--out', str(out), '--chain', 'hyperliquid']))
    S.append(('refresh book', py + ['scripts/strategies.py', 'refresh', '--out', str(out)]))
    S.append(('history analyze', py + ['scripts/perp_history.py', 'analyze', '--out', str(history), '--window', str(prior_window)]))
    S.append(('history render', py + ['scripts/perp_history.py', 'render', '--out', str(history)]))
    return S


def latest_prior_window(today_out):
    """The most recent perp window other than today's, whose hits the history scores out of sample."""
    cands = []
    for p in (ROOT / 'research').glob('*/perps*'):
        if p.is_dir() and p != today_out and (p / 'detectors.json').exists() and (p / 'manifest.json').exists():
            cands.append(p)
    cands.sort(key=lambda p: (p / 'manifest.json').stat().st_mtime)
    return cands[-1] if cands else ROOT / 'research' / '2026-09-08' / 'perps_1h'


def summarise(out, history):
    """One line for the daily log: the energy premium, the curve lead, the funding, and the book's top row."""
    row = {'utc': utc_now().isoformat(timespec='seconds'), 'window': str(out.relative_to(ROOT))}
    try:
        D = json.loads((out / 'detectors.json').read_text())
        rp = [h for h in D['hits'] if h['detector'] == 'roll_premium']
        row['roll_premium'] = [{'coin': h['key'], 'lead': round(h['evidence']['lead'], 3),
                                'spread_pct': round(h['evidence']['calendar_spread_pct'], 2),
                                'observed_premium': round(h['evidence']['observed_premium'], 5),
                                'funding_apr': round(h['economics']['funding_apr'], 3),
                                'net_apr': round(h['economics']['net_apr'], 3), 'go': h['economics']['go'],
                                'capacity_usd': h['economics']['capacity_usd']} for h in rp]
        fc = [h for h in D['hits'] if h['detector'] == 'funding_carry' and h['severity'] == 'high']
        row['funding_carry_high'] = [h['key'] for h in fc]
    except Exception as e:  # noqa: BLE001
        row['detectors_error'] = str(e)[:120]
    try:
        R = json.loads((out / 'refs_compare.json').read_text())
        row['refs'] = R['summary']
    except Exception as e:  # noqa: BLE001
        row['refs_error'] = str(e)[:120]
    try:
        V = json.loads((out / 'verify.json').read_text())
        row['verify_ok'] = V['all_ok']
    except Exception as e:  # noqa: BLE001
        row['verify_error'] = str(e)[:120]
    return row


def cmd_run(args):
    day = utc_now().strftime('%Y-%m-%d')
    out = ROOT / 'research' / day / 'perps_daily'
    if out.exists() and (out / 'manifest.json').exists() and not args.force:
        raise SystemExit('%s already has a window today; pass --force to collect another' % out)
    out.mkdir(parents=True, exist_ok=True)
    history = Path(args.history) if args.history else HISTORY
    prior = latest_prior_window(out)
    S = steps(out, history, args.minutes, prior)
    results = []
    t0 = time.time()
    for name, cmd in S:
        t = time.time()
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        tail = (r.stdout or '').strip().splitlines()[-3:]
        results.append({'step': name, 'returncode': r.returncode, 'seconds': round(time.time() - t, 1),
                        'tail': tail, 'stderr_tail': (r.stderr or '').strip().splitlines()[-3:] if r.returncode else []})
        print(json.dumps(results[-1]), flush=True)
        if r.returncode and name in ('window', 'analyze', 'detect'):
            break   # nothing downstream is meaningful without these
    row = summarise(out, history)
    row['steps'] = [{k: v for k, v in x.items() if k in ('step', 'returncode', 'seconds')} for x in results]
    row['seconds'] = round(time.time() - t0, 1)
    row['prior_window'] = str(prior.relative_to(ROOT))
    (out / 'daily_run.json').write_text(json.dumps(row, indent=1) + '\n')
    line = '- %s `%s` verify=%s refs=%s roll_premium=%s steps_failed=%s (%.0fs)' % (
        row['utc'], row['window'], row.get('verify_ok'), json.dumps(row.get('refs')),
        json.dumps(row.get('roll_premium')), [x['step'] for x in results if x['returncode']], row['seconds'])
    if not LOG.exists():
        LOG.write_text('# Perp daily log\n\nOne line per unattended pass of `scripts/perp_daily.py`. Read this before a session.\n\n')
    with LOG.open('a') as f:
        f.write(line + '\n')
    print(line)
    return 0 if not any(x['returncode'] for x in results) else 1


def cmd_plan(args):
    out = ROOT / 'research' / utc_now().strftime('%Y-%m-%d') / 'perps_daily'
    for name, cmd in steps(out, HISTORY, args.minutes, latest_prior_window(out)):
        print('%-30s %s' % (name, ' '.join(str(c) for c in cmd[1:])))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run'); r.set_defaults(fn=cmd_run)
    r.add_argument('--minutes', type=float, default=6)
    r.add_argument('--history', default=None)
    r.add_argument('--force', action='store_true')
    q = sub.add_parser('plan'); q.set_defaults(fn=cmd_plan)
    q.add_argument('--minutes', type=float, default=6)
    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == '__main__':
    main()
