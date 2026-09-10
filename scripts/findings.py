#!/usr/bin/env python3
"""The findings ledger: what the detectors found, how often it comes back, and whether it decayed.

The gap this closes. Every window so far produced a fresh set of findings and then forgot them. A rate gap seen on
Monday and again on Tuesday looked like two discoveries rather than one edge that persisted, and an edge that vanished
by Tuesday looked exactly the same as one nobody re-checked. Neither the *recurrence* of a mechanism nor the *decay* of
an opportunity was visible anywhere, and those two facts are most of what separates a tradable edge from a one-off.

So a detector hit is no longer only a line in one window's digest. It is an observation of a `finding`, identified
across windows by `detector:key`, and this ledger accumulates them:

    research/findings.jsonl   one line per finding: identity, severity, every observation, recheck cadence
    research/windows.json     which windows have been ingested, and which detectors ran in each

The window index is what makes *absence* mean something. Without it, a finding that stops appearing is indistinguishable
from one whose detector was never run again, so "seen 3 times" would be uninterpretable. With it, every finding carries
`seen / eligible`: how many of the windows that ran its detector actually contained it. A rate gap at 3/3 is a standing
dislocation; at 1/4 it was a spot artifact that the de-spiker happened to miss.

Predicted versus realized is the same bookkeeping applied to `economics`. A hit carrying a net APR is a prediction that
the edge is worth that much; the next observation of the same finding records what it was worth then. The ledger keeps
the series, so `report` can show 3.48% -> 3.37% -> 1.63% rather than asserting an edge from its best day.

    uv run --with pycryptodome python scripts/findings.py ingest --out research/2026-09-07/live_midday
    uv run python scripts/findings.py report                       recurrence, decay, and what each finding is worth now
    uv run python scripts/findings.py due                          findings past their recheck cadence
    uv run python scripts/findings.py show <id>                    every observation of one finding
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

LEDGER = ROOT / 'research' / 'findings.jsonl'
WINDOWS = ROOT / 'research' / 'windows.json'

# How soon a finding is worth looking at again. A severity is a claim about how much a wrong answer costs, so it is
# also a claim about how stale an answer may be: a mislabelled sink corrupts the next headline, a dust-scale curiosity
# does not.
RECHECK_HOURS = {'high': 6, 'notable': 24, 'info': 72}


def fid(identity):
    return hashlib.sha256(identity.encode()).hexdigest()[:12]


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def parse_utc(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        return None


def load_ledger():
    if not LEDGER.exists():
        return {}
    out = {}
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            out[r['id']] = r
    return out


def save_ledger(d):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(d.values(), key=lambda r: (r['detector'], r.get('key') or ''))
    LEDGER.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))


def load_windows():
    return json.loads(WINDOWS.read_text()) if WINDOWS.exists() else {}


def save_windows(d):
    WINDOWS.parent.mkdir(parents=True, exist_ok=True)
    WINDOWS.write_text(json.dumps(d, indent=1, sort_keys=True) + '\n')


# ----------------------------------------------------------------------------------------------------------------------
def ingest(out, chain='ethereum'):
    """Fold one window's `detectors.json` into the ledger.

    Re-ingesting the same window replaces that window's observations rather than appending them, so a re-run after a
    detector fix corrects the history instead of double-counting it.
    """
    out = Path(out)
    dj = out / 'detectors.json'
    if not dj.exists():
        raise SystemExit('no detectors.json in %s — run `live_scan detect` first' % out)
    det = json.loads(dj.read_text())
    aj = out / 'analysis.json'
    A = json.loads(aj.read_text()) if aj.exists() else {}
    win = A.get('window', {})
    # A block-chain window names its bounds first/last; the perp windows name them start/end. Either is a window.
    first_utc = win.get('first_utc') or win.get('start_utc')
    last_utc = win.get('last_utc') or win.get('end_utc')
    key = str(out)
    ran = [m['detector'] for m in det.get('detectors', []) if not m.get('error')]

    W = load_windows()
    W[key] = {'chain': chain, 'first_utc': first_utc, 'last_utc': last_utc,
              'first_block': win.get('first_block'), 'last_block': win.get('last_block'),
              'hours': win.get('hours'), 'detectors_run': sorted(ran),
              'ingested_at': now().isoformat(),
              'label_fingerprint': (A.get('provenance') or {}).get('labels')}
    save_windows(W)

    L = load_ledger()
    seen_now = set()
    for h in det.get('hits', []):
        ident = h.get('identity') or ('%s:%s' % (h['detector'], h.get('key')) if h.get('key') else h['detector'])
        i = fid(ident)
        seen_now.add(i)
        obs = {'window': key, 'utc': last_utc, 'first_block': win.get('first_block'),
               'last_block': win.get('last_block'), 'severity': h.get('severity'), 'usd': h.get('usd'),
               'title': h.get('title'),
               'net_apr': (h.get('economics') or {}).get('net_apr'),
               'go': (h.get('economics') or {}).get('go')}
        r = L.get(i)
        if r is None:
            r = {'id': i, 'identity': ident, 'detector': h['detector'], 'key': h.get('key'),
                 'title': h.get('title'), 'severity': h.get('severity'),
                 'recheck_hours': RECHECK_HOURS.get(h.get('severity'), 24),
                 'status': 'open', 'observations': []}
            L[i] = r
        r['observations'] = [o for o in r['observations'] if o['window'] != key] + [obs]
        r['observations'].sort(key=lambda o: (o.get('utc') or '', o['window']))
        # The most recent reading is the current one: a finding's severity and headline are properties of now, while
        # the series behind them is the history.
        r['title'] = h.get('title')
        r['severity'] = h.get('severity')
        r['recheck_hours'] = RECHECK_HOURS.get(h.get('severity'), 24)
    save_ledger(L)

    elig, seen = coverage(L, W)
    print(json.dumps({'window': key, 'detectors_run': len(ran), 'hits': len(det.get('hits', [])),
                      'findings_total': len(L), 'new_findings': sum(1 for i in seen_now if len(L[i]['observations']) == 1),
                      'recurring': sum(1 for r in L.values() if len(r['observations']) > 1)}, indent=1))


def coverage(L, W):
    """(eligible, seen) per finding: windows that ran its detector, and windows that contained it."""
    elig, seen = {}, {}
    for i, r in L.items():
        e = sum(1 for w in W.values() if r['detector'] in (w.get('detectors_run') or []))
        elig[i] = e
        seen[i] = len(r['observations'])
    return elig, seen


# ----------------------------------------------------------------------------------------------------------------------
def report(args):
    L, W = load_ledger(), load_windows()
    if not L:
        raise SystemExit('empty ledger — run `findings.py ingest --out <window>` first')
    elig, seen = coverage(L, W)
    shown = [r for r in L.values() if args.all or r.get('status') == 'open']
    n_closed = sum(1 for r in L.values() if r.get('status') != 'open')
    rows = sorted(shown, key=lambda r: (-seen[r['id']], -(r['observations'][-1].get('usd') or 0)))
    print('%d open finding(s)%s across %d ingested window(s)\n'
          % (len(L) - n_closed, (' and %d resolved' % n_closed) if n_closed else '', len(W)))
    print('%-13s %-19s %5s %10s %14s  %s' % ('id', 'detector', 'seen', 'severity', 'latest USD', 'what'))
    for r in rows:
        o = r['observations'][-1]
        usd = o.get('usd')
        mark = '' if r.get('status') == 'open' else '[resolved] '
        print('%-13s %-19s %5s %10s %14s  %s%s'
              % (r['id'], r['detector'], '%d/%d' % (seen[r['id']], elig[r['id']]), r['severity'],
                 format(round(usd), ',') if usd else '-', mark, (r['title'] or '')[:78 - len(mark)]))
    econ = [r for r in L.values() if any(o.get('net_apr') is not None for o in r['observations'])]
    if econ:
        print('\npredicted net APR, oldest reading first (this is the decay column):')
        for r in sorted(econ, key=lambda r: -(r['observations'][-1].get('net_apr') or 0)):
            series = ['%.2f%%' % (100 * o['net_apr']) for o in r['observations'] if o.get('net_apr') is not None]
            print('  %-13s %-42s %s' % (r['id'], (r['key'] or r['detector'])[:42], ' -> '.join(series)))
    rec = [r for r in shown if seen[r['id']] > 1]
    once = [r for r in shown if seen[r['id']] == 1 and elig[r['id']] > 1]
    print('\n%d recurring (seen in more than one window), %d seen once despite a later sweep that could have seen it.'
          % (len(rec), len(once)))
    if once and args.verbose:
        for r in once:
            print('  once-only: %-13s %s' % (r['id'], (r['title'] or '')[:88]))


def due(args):
    L = load_ledger()
    t = now()
    rows = []
    for r in L.values():
        if r.get('status') != 'open':
            continue   # a closed finding has been answered; `close` records why
        last = parse_utc(r['observations'][-1].get('utc')) if r['observations'] else None
        if last is None:
            continue
        age = (t - last).total_seconds() / 3600
        if age >= r['recheck_hours']:
            rows.append((age, r))
    rows.sort(key=lambda x: -x[0])
    if not rows:
        print('nothing due')
        return
    print('%-13s %-19s %8s %8s  %s' % ('id', 'detector', 'age h', 'cadence', 'what'))
    for age, r in rows:
        print('%-13s %-19s %8.1f %8d  %s' % (r['id'], r['detector'], age, r['recheck_hours'], (r['title'] or '')[:70]))
    print('\n%d finding(s) past their recheck cadence. Collect a fresh window and run `live_scan detect` + '
          '`findings.py ingest`.' % len(rows))


def close(args):
    """Mark a finding resolved, with the reason. A closed finding stops appearing in `due`.

    The case this exists for: `solver_fingerprint` reports an *unlabelled* address of a given shape, and adopting that
    shape into the registry answers it. Leaving it open would keep asking a question that has been answered, and
    deleting it would lose the fact that it was ever asked. Closing keeps the history and stops the nagging.
    """
    L = load_ledger()
    ids = [args.id] if args.id else [r['id'] for r in L.values()
                                     if r['detector'] == args.detector and (not args.key or r.get('key') == args.key)]
    n = 0
    for i in ids:
        r = L.get(i)
        if not r:
            continue
        r['status'] = 'resolved'
        r['resolution'] = {'note': args.note, 'at': now().isoformat()}
        n += 1
    save_ledger(L)
    print(json.dumps({'closed': n, 'note': args.note}))


def show(args):
    L = load_ledger()
    r = L.get(args.id) or next((x for x in L.values() if args.id in x['identity']), None)
    if not r:
        raise SystemExit('no such finding: %s' % args.id)
    print(json.dumps(r, indent=1, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('ingest'); a.add_argument('--out', required=True); a.add_argument('--chain', default='ethereum')
    b = sub.add_parser('report'); b.add_argument('-v', '--verbose', action='store_true')
    b.add_argument('--all', action='store_true', help='include findings already resolved')
    sub.add_parser('due')
    c = sub.add_parser('show'); c.add_argument('id')
    d = sub.add_parser('close')
    d.add_argument('id', nargs='?', help='one finding id; omit to close every finding of a detector')
    d.add_argument('--detector'); d.add_argument('--key')
    d.add_argument('--note', required=True, help='why it is closed — this is the record')
    args = p.parse_args()
    if args.cmd == 'ingest':
        ingest(args.out, args.chain)
    elif args.cmd == 'report':
        report(args)
    elif args.cmd == 'due':
        due(args)
    elif args.cmd == 'close':
        close(args)
    else:
        show(args)


if __name__ == '__main__':
    main()
