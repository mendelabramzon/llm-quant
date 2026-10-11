#!/usr/bin/env python3
"""One unattended pass of the forward tests: every frozen rule that only advances when somebody runs it.

Why. On 2026-10-11 the book's open questions moved from history to the future. Five forward tests and a watcher were
frozen in one session, and each of them needs something every day that cannot be done later:

  * the JLP net-delta hedge (`jlp_forward.py`), the first kill gate of `jlp-hedged-house-lp`: one jlp-info snapshot a
    day, because the venue serves no composition history;
  * the one-pool queue book (`queue_live.py daily`): today's ladder must be registered before the sells it may fill,
    and the row's kill criteria are recomputed on blocks that did not exist when the rule was frozen;
  * the gold-carry watch lines (`gold_carry.py forward`): funding, premium and depth, which the venues do not keep;
  * the pooled money-market rotation (`incentive_yields.py forward`): the next hold registers inside a 30-hour window
    before its decision day, and the share prices behind the audit are only readable on the day;
  * EMPD and BNC (`nav_wrappers.py forward score`): scored when their +20 and +60 session closes settle;
  * the collateral watcher (`collateral_watch.py run`): a new collateral asset on a venue is a new same-venue carry,
    and the diff needs yesterday's snapshot.

The perp pass (`perp_daily.py`) already carries the unlock test and the Boros snapshots. This runner carries the rest,
one step at a time; the steps are independent, so one failure does not stop the others. It appends one line a day to
research/forward_daily_log.md with every test's verdict, which the next session reads first.

    uv run --with pycryptodome python scripts/forward_daily.py run
    uv run --with pycryptodome python scripts/forward_daily.py plan      # print the steps without running them

Schedule it once a day at a fixed time away from the 00/08/16 UTC funding settlements (the JLP hedge earns funding
between snapshots). The template `scripts/launchd/com.llm-quant.forward-daily.plist` runs at 07:30 UTC: DefiLlama has
published the previous day, the chains pass (07:00 UTC) has finished with the shared Infura keys, and the money-market
rotation's registration window (30 hours before a decision day's 00:00 UTC) contains exactly one run. It is not
installed; copy it to ~/Library/LaunchAgents/ to install.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'research' / 'forward_daily_log.md'
CRITICAL = ()     # no step feeds another test, so nothing aborts the pass


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def steps():
    py = [sys.executable]
    return [
        # first, so the snapshot's time of day (and the funding window it closes) does not drift with the other steps
        ('jlp snapshot', py + ['scripts/jlp_forward.py', 'snapshot']),
        ('jlp score', py + ['scripts/jlp_forward.py', 'score']),
        ('collateral watch', py + ['scripts/collateral_watch.py', 'run']),
        ('queue book', py + ['scripts/queue_live.py', 'daily']),
        ('gold snapshot', py + ['scripts/gold_carry.py', 'forward', 'snapshot']),
        ('gold score', py + ['scripts/gold_carry.py', 'forward', 'score']),
        ('money-market snapshot', py + ['scripts/incentive_yields.py', 'forward', 'snapshot']),
        ('money-market score', py + ['scripts/incentive_yields.py', 'forward', 'score']),
        ('dat events score', py + ['scripts/nav_wrappers.py', 'forward', 'score']),
    ]


def read(path):
    try:
        return json.loads((ROOT / path).read_text())
    except (OSError, ValueError):
        return None


def verdicts():
    """Each test's current verdict from the .json its score step writes; None where a test has not scored yet."""
    out = {}
    d = read('research/jlp_forward.json')
    if d:
        s = d.get('summary') or {}
        f = d.get('flags') or {}
        out['jlp'] = {'verdict': s.get('verdict'), 'days': s.get('days'), 'ann_excess': s.get('ann_excess'),
                      'warnings': f.get('warnings') or [], 'events': f.get('events') or []}
    d = read('research/queue_live_paper.json')
    if d:
        out['queue_book'] = {'verdict': d.get('verdict'), 'data_through': d.get('data_through'),
                             'fills': (d.get('paper') or {}).get('fills')}
    d = read('research/gold_carry_forward.json')
    if d:
        out['gold'] = {'verdict': (d.get('summary') or {}).get('verdict')}
    d = read('research/mm_rotation_forward.json')
    if d:
        s = d.get('summary') or {}
        out['money_markets'] = {'verdict': s.get('verdict'), 'kill': s.get('kill') or []}
    d = read('research/dat_events_forward.json')
    if d:
        out['dat_events'] = {'verdict': (d.get('summary') or {}).get('verdict')}
    p = ROOT / 'research' / 'collateral_events.jsonl'
    if p.exists():
        # a baseline row records a venue program's first snapshot; every other event is a change worth reading
        today = utc_now().strftime('%Y-%m-%d')
        rows = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        new = [r for r in rows if r.get('new_date') == today and r.get('event') != 'baseline']
        out['collateral'] = {'events_total': sum(1 for r in rows if r.get('event') != 'baseline'),
                             'events_today': len(new),
                             'today': ['%s %s/%s %s' % (r.get('event'), r.get('venue'), r.get('program'), r.get('asset'))
                                       for r in new]}
    return out


def cmd_run(args):
    day = utc_now().strftime('%Y-%m-%d')
    out = ROOT / 'research' / day / 'forward_daily'
    if (out / 'daily_run.json').exists() and not args.force:
        raise SystemExit('%s already ran today; pass --force to run again (every step is idempotent within a UTC day)' % out)
    out.mkdir(parents=True, exist_ok=True)
    results, t0 = [], time.time()
    skip = [x.strip() for x in (args.skip or '').split(',') if x.strip()]
    for name, cmd in steps():
        if any(name.startswith(x) for x in skip):
            results.append({'step': name, 'returncode': 0, 'seconds': 0.0, 'tail': ['skipped (--skip)'], 'stderr_tail': []})
            print(json.dumps(results[-1]), flush=True)
            continue
        t = time.time()
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        results.append({'step': name, 'returncode': r.returncode, 'seconds': round(time.time() - t, 1),
                        'tail': (r.stdout or '').strip().splitlines()[-3:],
                        'stderr_tail': (r.stderr or '').strip().splitlines()[-3:] if r.returncode else []})
        print(json.dumps(results[-1]), flush=True)
        if r.returncode and name in CRITICAL:
            break
    row = {'utc': utc_now().isoformat(timespec='seconds'), 'verdicts': verdicts(),
           'steps': [{k: v for k, v in x.items() if k in ('step', 'returncode', 'seconds')} for x in results],
           'seconds': round(time.time() - t0, 1)}
    (out / 'daily_run.json').write_text(json.dumps(dict(row, results=results), indent=1) + '\n')
    V = row['verdicts']
    line = '- %s jlp=%s queue=%s gold=%s mm=%s dat=%s collateral_events_today=%s steps_failed=%s (%.0fs)' % (
        row['utc'], json.dumps((V.get('jlp') or {}).get('verdict')), json.dumps((V.get('queue_book') or {}).get('verdict')),
        json.dumps((V.get('gold') or {}).get('verdict')), json.dumps((V.get('money_markets') or {}).get('verdict')),
        json.dumps((V.get('dat_events') or {}).get('verdict')), (V.get('collateral') or {}).get('events_today'),
        [x['step'] for x in results if x['returncode']], row['seconds'])
    if not LOG.exists():
        LOG.write_text('# Forward-test daily log\n\nOne line per pass of `scripts/forward_daily.py run`. Read this before a '
                       'session.\n\n')
    with LOG.open('a') as f:
        f.write(line + '\n')
    print(line)
    return 0 if not any(x['returncode'] for x in results) else 1


def cmd_plan(args):
    for name, cmd in steps():
        print('%-24s %s' % (name, ' '.join(str(c) for c in cmd[1:])))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.set_defaults(fn=cmd_run)
    r.add_argument('--force', action='store_true')
    r.add_argument('--skip', help="comma-separated step-name prefixes to skip, e.g. 'collateral watch' on a second run "
                                  "the same UTC day (it would re-snapshot the day)")
    q = sub.add_parser('plan')
    q.set_defaults(fn=cmd_plan)
    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == '__main__':
    main()
