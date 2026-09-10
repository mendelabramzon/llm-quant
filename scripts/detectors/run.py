#!/usr/bin/env python3
"""Run every detector over a collected window and write `detectors.json` plus a markdown digest.

    uv run --with pycryptodome python scripts/detectors/run.py --out research/2026-09-07/live_midday
    uv run --with pycryptodome python scripts/detectors/run.py --out ... --only rate_dispersion
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from detectors import Context, run_all, registry


def digest(hits, meta, out):
    L = ['# Detector sweep — %s' % out, '',
         'Ran %d detector(s); %d hit(s).' % (len(meta), len(hits)), '']
    L.append('| detector | hits | seconds | what it looks for |')
    L.append('|---|---:|---:|---|')
    for m in meta:
        L.append('| `%s` | %d | %.2f | %s |' % (m['detector'], m['hits'], m['seconds'],
                                                m['error'] or m['description']))
    L.append('')
    for h in hits:
        L.append('### [%s] %s' % (h.severity, h.title))
        L.append('')
        L.append('```json')
        L.append(json.dumps(h.evidence, indent=1, default=str)[:2400])
        L.append('```')
        if h.economics:
            L.append('')
            apr = h.economics.get('net_apr')
            L.append('Economics: net APR %s, %s per year, %s — %s' % (
                ('%.2f%%' % (100 * apr)) if apr is not None else 'unquoted', '$%s' % format(h.economics['net_per_year_usd'], ','),
                'GO' if h.economics['go'] else 'no', h.economics['reason']))
        L.append('')
    return '\n'.join(L)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', required=True)
    p.add_argument('--only', nargs='*')
    p.add_argument('--min-usd', type=float, default=1e4)
    p.add_argument('--list', action='store_true', help='list registered detectors and exit')
    a = p.parse_args()
    if a.list:
        for m in registry():
            print('%-22s %s' % (getattr(m, 'NAME', m.__name__), getattr(m, 'DESCRIPTION', '')))
        return
    ctx = Context(a.out, min_usd=a.min_usd)
    hits, meta = run_all(ctx, only=a.only)
    outdir = Path(a.out)
    (outdir / 'detectors.json').write_text(json.dumps(
        {'window': str(a.out), 'detectors': meta, 'hits': [h.as_dict() for h in hits],
         'gas_scenarios': {'standard': ctx.gas_quote(), 'competing': ctx.gas_quote(race=True)}},
        indent=1, default=str) + '\n')
    (outdir / 'detectors.md').write_text(digest(hits, meta, a.out) + '\n')
    for m in meta:
        print('%-22s %2d hit(s)  %5.2fs  %s' % (m['detector'], m['hits'], m['seconds'], m['error'] or ''))
    print()
    for h in hits:
        print('[%-7s] %s' % (h.severity, h.title))
    print('\nwrote %s and %s' % (outdir / 'detectors.json', outdir / 'detectors.md'))
    if any(m['error'] for m in meta):
        raise SystemExit('detector errors; refusing to report a complete sweep')


if __name__ == '__main__':
    main()
