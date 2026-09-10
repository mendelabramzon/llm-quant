#!/usr/bin/env python3
"""The strategy book: what this system currently believes is tradable, priced, ranked, and re-checked until it dies.

The gap this closes. The loop's stated output is insight and proposed strategy, and this repo has produced good ones —
the sUSDe cooldown redemption arb, the captive-flow USDG LP, the Morpho/Pendle dollar-yield ladder. Every one of them
lives in a dated `findings.md` written in one session and never looked at again. So the system cannot answer the two
questions that decide whether a strategy is real: **is it still there**, and **was it ever worth doing at the size we
could actually deploy**. A strategy proposed on Sunday and silently dead by Tuesday reads exactly like one that held.

A `findings.jsonl` entry is an observation. A strategy is a *claim about the future* — that a mechanism will keep
producing an edge, and that the edge survives gas, impact, competition and decay at real size. So it carries three
things a finding does not:

  * **`legs` and economics inputs**, so `economics.py` prices it rather than prose asserting a number;
  * **`kill_criteria`**, falsifiable conditions that retire it. Without them "is it still alive" is a judgement call,
    and judgement calls about your own ideas go one way;
  * **a quote series**, so decay is visible. The book prints 3.48% -> 3.48% -> 1.9% rather than the best day.

Where a detector already produces the number, `refresh` re-quotes automatically from the findings ledger and the
strategy stays current for free. Where it does not, the quote is stamped with its source and its age, and a strategy
whose last quote is a week old is shown as stale rather than as live — which is itself the most useful thing this file
says about the loop, because most of the book is in that state.

    uv run --with pycryptodome python scripts/strategies.py book                    ranked, with staleness and decay
    uv run --with pycryptodome python scripts/strategies.py refresh --out <window>  re-quote from that window's ledger
    uv run --with pycryptodome python scripts/strategies.py propose --out <window>  candidates the book does not hold
    uv run --with pycryptodome python scripts/strategies.py show <id>
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BOOK = ROOT / 'research' / 'strategies.jsonl'

# A quote older than this is not a price, it is a memory. Chosen per kind: a lending rate moves hourly, a pool's fee
# yield daily, a redemption discount only when the queue changes.
STALE_HOURS = {'spread': 24, 'carry': 72, 'liquidity': 72, 'redemption': 168, 'harvest': 72}
STATUSES = ['proposed', 'fork-proven', 'monitored', 'retired']


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def parse_utc(s):
    try:
        return dt.datetime.fromisoformat((s or '').replace('Z', '+00:00'))
    except ValueError:
        return None


def load():
    if not BOOK.exists():
        return {}
    return {r['id']: r for r in (json.loads(l) for l in BOOK.read_text().splitlines() if l.strip())}


def save(d):
    BOOK.parent.mkdir(parents=True, exist_ok=True)
    BOOK.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in sorted(d.values(), key=lambda r: r['id'])))


def latest(s):
    return s['quotes'][-1] if s.get('quotes') else None


def last_priced(s):
    """The most recent quote that actually carries a rate.

    A strategy whose linked detector ran and found nothing gets a quote saying so, and that quote is current and
    informative — but it is not a price. The book shows both: the last rate seen, in brackets, and the fact that the
    newest look did not see it.
    """
    for q in reversed(s.get('quotes') or []):
        if q.get('net_apr') is not None:
            return q
    return None


def age_hours(s):
    q = latest(s)
    t = parse_utc(q.get('at')) if q else None
    return None if t is None else (now() - t).total_seconds() / 3600


def is_stale(s):
    a = age_hours(s)
    return True if a is None else a > STALE_HOURS.get(s.get('kind'), 48)


# ----------------------------------------------------------------------------------------------------------------------
def refresh(args):
    """Re-quote every strategy whose number a detector already produces, from one window's findings ledger.

    The link is `evidence.findings`: a strategy that names a finding id inherits that finding's latest observation as
    its quote. This is the whole reason the detector registry and the ledger were built — a strategy backed by a
    detector re-prices itself every window, and one backed only by a bespoke scanner does not and says so.
    """
    import findings as F
    L = F.load_ledger()
    book = load()
    win = json.loads((Path(args.out) / 'analysis.json').read_text()).get('window', {}) \
        if (Path(args.out) / 'analysis.json').exists() else {}
    at = win.get('last_utc') or win.get('end_utc') or now().isoformat()
    ran = set((F.load_windows().get(str(args.out)) or {}).get('detectors_run') or [])
    updated, unlinked, not_run = [], [], []
    for s in book.values():
        ids = [i for i in (s.get('evidence', {}).get('findings') or []) if i in L]
        if not ids:
            unlinked.append(s['id'])
            continue
        # A window only speaks about a strategy whose detectors ran in it. A perp window says nothing about a lending
        # spread, and stamping "not observed" on it would read as decay when it is silence.
        if ran and not any(L[i]['detector'] in ran for i in ids):
            not_run.append(s['id'])
            continue
        obs = []
        for i in ids:
            o = next((o for o in reversed(L[i]['observations']) if o['window'] == str(args.out)), None)
            if o:
                obs.append((i, o))
        if not obs:
            # The detector ran and did not see it. That is a data point about the strategy, not a missing quote.
            q = {'at': at, 'window': str(args.out), 'source': 'ledger', 'present': False,
                 'net_apr': None, 'usd': None, 'note': 'linked finding(s) not observed in this window'}
        else:
            best = max(obs, key=lambda x: (x[1].get('net_apr') or 0))
            q = {'at': at, 'window': str(args.out), 'source': 'ledger:' + best[0], 'present': True,
                 'net_apr': best[1].get('net_apr'), 'usd': best[1].get('usd'),
                 # The detector's own go/no-go travels with the rate. A quote can be arithmetically fine and still
                 # fail its detector's significance test — an edge inside its own price noise, an exit that may not
                 # be there — and a book that showed only the rate would present that as a clean number.
                 'go': best[1].get('go'), 'note': best[1].get('title')}
        # Upsert on the window, then order by time. Appending blindly made re-running a window read as six
        # observations of a rate that had been quoted once — the same double-count the findings ledger already fixed.
        s['quotes'] = sorted([x for x in s['quotes'] if x.get('window') != str(args.out)] + [q],
                             key=lambda x: (x.get('at') or '', x.get('window') or ''))
        updated.append((s['id'], q['net_apr']))
    save(book)
    print(json.dumps({'window': str(args.out), 're-quoted': [{'id': i, 'net_apr': v} for i, v in updated],
                      'detectors_did_not_run_in_this_window': not_run,
                      'not_linked_to_a_detector': unlinked}, indent=1))


def propose(args):
    """Recurring ledger findings that carry economics and no strategy in the book cites.

    Deliberately a *candidate list*, not a generated strategy. The machine can see that a rate gap recurred three times
    and nets 3.4% at $34M; it cannot say who is paying for that gap or what would end it, and a strategy without those
    two answers is a number with no mechanism behind it. That part is the qualitative half of the loop and stays with
    the analyst.
    """
    import findings as F
    L, W = F.load_ledger(), F.load_windows()
    elig, seen = F.coverage(L, W)
    cited = {i for s in load().values() for i in (s.get('evidence', {}).get('findings') or [])}
    rows = []
    for i, r in L.items():
        if i in cited or r.get('status') != 'open':
            continue
        aprs = [o['net_apr'] for o in r['observations'] if o.get('net_apr') is not None]
        usd = [o['usd'] for o in r['observations'] if o.get('usd')]
        if not aprs and not usd:
            continue
        rows.append({'finding': i, 'detector': r['detector'], 'key': r.get('key'),
                     'seen': '%d/%d' % (seen[i], elig[i]), 'persistence': round(seen[i] / max(elig[i], 1), 2),
                     'net_apr_series': aprs, 'latest_usd': usd[-1] if usd else None, 'title': r['title']})
    rows.sort(key=lambda x: (-x['persistence'], -((x['net_apr_series'] or [0])[-1] or 0), -(x['latest_usd'] or 0)))
    for x in rows[:args.top]:
        print('%-13s %-18s %6s p=%.2f  %-9s %14s  %s'
              % (x['finding'], x['detector'], x['seen'], x['persistence'],
                 ('%.2f%%' % (100 * x['net_apr_series'][-1])) if x['net_apr_series'] else '-',
                 format(round(x['latest_usd']), ',') if x['latest_usd'] else '-', x['title'][:72]))
    print('\n%d candidate(s) no strategy cites. A candidate becomes a strategy when someone can state the mechanism '
          'and a kill criterion.' % len(rows))


def book_cmd(args):
    book = load()
    if not book:
        raise SystemExit('empty book — seed research/strategies.jsonl')
    rows = [s for s in book.values() if args.all or s.get('status') != 'retired']
    def rank(s):
        q = latest(s)
        return (0 if is_stale(s) else 1, (q or {}).get('net_apr') or 0)
    rows.sort(key=rank, reverse=True)
    print('%-26s %-11s %-9s %10s %13s %7s  %s'
          % ('strategy', 'status', 'kind', 'net APR', 'capacity', 'quoted', 'evidence'))
    for s in rows:
        q = latest(s) or {}
        lp = last_priced(s)
        a = age_hours(s)
        src = q if q.get('net_apr') is not None else (lp or {})
        mark = '' if src.get('go') is not False else '*'
        shown = ('%.2f%%%s' % (100 * q['net_apr'], mark)) if q.get('net_apr') is not None else (
            ('(%.2f%%)%s' % (100 * lp['net_apr'], mark)) if (lp and q.get('present') is False) else '-')
        print('%-26s %-11s %-9s %10s %13s %7s  %s'
              % (s['id'][:26], s['status'], s.get('kind', '?'), shown,
                 ('$%s' % format(round(s.get('capacity_usd') or 0), ',')) if s.get('capacity_usd') else '-',
                 ('%.0fh%s' % (a, '!' if is_stale(s) else '')) if a is not None else 'never',
                 ('ledger' if (s.get('evidence', {}).get('findings')) else 'manual')
                 + (', fork' if s.get('evidence', {}).get('fork_proof') else '')))
    print()
    for s in rows:
        series = [q for q in s.get('quotes', []) if q.get('net_apr') is not None]
        if len(series) > 1:
            print('  %-26s %s' % (s['id'][:26], ' -> '.join('%.2f%%' % (100 * q['net_apr']) for q in series)))
    live = [s for s in rows if not is_stale(s)]
    absent = [s for s in rows if (latest(s) or {}).get('present') is False]
    print('\n%d strategy(ies), %d with a current quote, %d stale. A stale quote is a memory, not a price.'
          % (len(rows), len(live), len(rows) - len(live)))
    if absent:
        print('A rate in brackets is the last one seen: its detector ran on the newest window and did not find it — '
              '%s.' % ', '.join(s['id'] for s in absent))
    failed = [s for s in rows if ((latest(s) if (latest(s) or {}).get('net_apr') is not None else last_priced(s))
                                  or {}).get('go') is False]
    if failed:
        print('A starred rate is one its own detector declines: the arithmetic holds but a gate does not — %s. '
              'Read the finding before the number.' % ', '.join(s['id'] for s in failed))


def scorecard(args):
    """The loop's own metrics: what the book is worth at capacity on its detectors' verdicts, and how predictions fared.

    Time-to-verified-insight rewards being right; it says nothing about whether the output is worth anything. Two
    numbers do: dollars a year at deployable capacity across the strategies whose own detectors currently say go, and
    whether a rate quoted on one window was still there on the next. The benchmark row (the savings rate every dollar
    idea has to beat) is excluded from the totals by its `benchmark` flag.
    """
    import glob
    import findings as F
    book = load()
    rows = []
    for s in book.values():
        if s.get('status') == 'retired':
            continue
        q = latest(s) or {}
        lp = last_priced(s) or {}
        src = q if q.get('net_apr') is not None else lp
        apr, cap = src.get('net_apr'), (s.get('capacity_usd') or 0)
        rows.append({'id': s['id'], 'status': s['status'], 'kind': s.get('kind'), 'net_apr': apr, 'capacity_usd': cap,
                     'usd_per_year': (apr * cap) if apr is not None else None, 'go': src.get('go'),
                     'present': q.get('present'), 'stale': is_stale(s), 'benchmark': bool(s.get('benchmark')),
                     'source': src.get('source')})
    def total(pred):
        return sum(r['usd_per_year'] or 0.0 for r in rows if pred(r))
    edge = lambda r: not r['benchmark']
    current = lambda r: edge(r) and r['go'] is not False and not r['stale'] and r['present'] is not False
    T = {'strategies': len(rows), 'benchmark_rows': [r['id'] for r in rows if r['benchmark']],
         'usd_per_year_at_capacity_all_edges': total(edge),
         'usd_per_year_go_and_current': total(current),
         'usd_per_year_declined_stale_or_absent': total(edge) - total(current),
         'strategies_go_and_current': sum(1 for r in rows if current(r))}
    # Persistence: economics-bearing findings observed at least twice, whose latest rate kept at least half of the first.
    L = F.load_ledger()
    series = {}
    for r in L.values():
        xs = [o['net_apr'] for o in r['observations'] if o.get('net_apr') is not None]
        if len(xs) >= 2:
            series[r['id']] = xs
    kept = sum(1 for xs in series.values() if ((xs[-1] >= 0.5 * xs[0]) if xs[0] > 0 else (xs[-1] <= 0.5 * xs[0])))
    T['findings_with_a_rate_seen_twice'] = len(series)
    T['share_that_kept_half_their_first_rate'] = (kept / len(series)) if series else None
    # Out of sample, where a history has scored an earlier window's predictions.
    oos = []
    for p in sorted(glob.glob(str(ROOT / 'research' / '*' / '*' / 'history_summary.json'))):
        H = json.loads(Path(p).read_text())
        O = H.get('oos') or {}
        for r in O.get('rows') or []:
            if r.get('note') or r.get('detector') != 'funding_carry':
                continue
            oos.append({'window': O.get('window'), 'coin': r['coin'], 'predicted_apr': r.get('predicted_apr'),
                        'hours': r.get('hours_held'), 'hedged_net_bps': r.get('hedged_proxy_net_bps'),
                        'unhedged_net_bps': r.get('unhedged_net_bps')})
    if oos:
        T['oos_predictions'] = len(oos)
        T['oos_hedged_positive'] = sum(1 for r in oos if (r['hedged_net_bps'] or 0) > 0)
        T['oos_unhedged_positive'] = sum(1 for r in oos if (r['unhedged_net_bps'] or 0) > 0)
    print('%-28s %-11s %9s %14s %14s %5s  %s' % ('strategy', 'status', 'net APR', 'capacity', '$/yr at cap', 'go', 'state'))
    for r in sorted(rows, key=lambda r: -(r['usd_per_year'] or 0)):
        state = ('benchmark' if r['benchmark'] else 'stale' if r['stale'] else 'absent' if r['present'] is False else
                 'declined' if r['go'] is False else 'current')
        print('%-28s %-11s %9s %14s %14s %5s  %s' % (
            r['id'][:28], r['status'], ('%.2f%%' % (100 * r['net_apr'])) if r['net_apr'] is not None else '-',
            '$%s' % format(round(r['capacity_usd']), ','), ('$%s' % format(round(r['usd_per_year']), ',')) if r['usd_per_year'] is not None else '-',
            '-' if r['go'] is None else ('yes' if r['go'] else 'no'), state))
    print()
    print(json.dumps(T, indent=1))
    if oos:
        print('\nout of sample (funding_carry hits scored by a later history):')
        for r in oos:
            print('  %-14s predicted %+6.0f%%  held %3dh  hedged %+7.1fbp  unhedged %+7.1fbp' % (
                r['coin'], 100 * (r['predicted_apr'] or 0), r['hours'] or 0, r['hedged_net_bps'] or 0, r['unhedged_net_bps'] or 0))
    (ROOT / 'research' / 'scorecard.json').write_text(json.dumps({'generated': now().isoformat(), 'rows': rows, 'totals': T, 'oos': oos}, indent=1) + '\n')


def show(args):
    b = load()
    s = b.get(args.id) or next((x for x in b.values() if args.id in x['id']), None)
    if not s:
        raise SystemExit('no such strategy: %s' % args.id)
    print(json.dumps(s, indent=1, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('refresh'); a.add_argument('--out', required=True)
    b = sub.add_parser('propose'); b.add_argument('--out'); b.add_argument('--top', type=int, default=15)
    c = sub.add_parser('book'); c.add_argument('--all', action='store_true')
    d = sub.add_parser('show'); d.add_argument('id')
    e = sub.add_parser('scorecard')
    args = p.parse_args()
    {'refresh': refresh, 'propose': propose, 'book': book_cmd, 'show': show, 'scorecard': scorecard}[args.cmd](args)


if __name__ == '__main__':
    main()
