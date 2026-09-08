#!/usr/bin/env python3
"""What an artifact was built from, so a stale one announces itself instead of sitting in a report.

The problem, observed twice in one session. A parallel study reclassified an address this repo called an "exchange hot
wallet" as a Relay solver. Every `analysis.json` written before that edit still carried the old exchange flow, and
nothing said so: `verify` eventually caught it, but only as a *numeric* mismatch whose stated cause ("the aggregation
drifted") was wrong. The real cause was a label edit, and the fix was not to re-check the arithmetic but to re-run
`analyze`. Both windows were corrected by hand.

So every artifact now records the inputs that decide its numbers, and `verify` compares them before it compares a
single value. Three of those inputs are hard gates, because a change to any of them means the artifact is describing a
world the current code no longer believes in:

    labels      sha over the *effective* address book -- registry file, model-memory table and the behavioural rule
                together, because all three feed `load_address_book` and any of them can move exchange flow
    tokens      sha over the token table, which `analyze` and `window_raw` share; if it changed since the analysis,
                a verify mismatch is a pricing difference and not the aggregation drift verify exists to find
    blocks      first/last/count of the raw files, so blocks arriving after an analysis can't silently widen it
    head        the block `head_state.json` was read at. `analyze` prices the whole window from that file, so a later
                `head` run re-prices every dollar figure in an analysis that is not re-run -- and nothing said so
                until this gate existed. It caught its own motivating case: a window collected to 23:27 UTC ended up
                carrying a head read from 05:21 the next morning, six hours of price drift with the labels and the
                token table both unchanged, so no other gate could see it.

`code` and `git` are recorded but never gate: `live_scan.py` changes for a dozen unrelated reasons a session and a
hard gate on it would cry stale constantly, which is the fastest way to teach a reader to ignore the check.

    from provenance import stamp, check
    res['provenance'] = stamp('analysis', blocks=len(nums), first=nums[0], last=nums[-1])
    drift = check(analysis.get('provenance'))       # -> rows, each {field, artifact, current, gate, ok}
"""
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Fields whose mismatch invalidates the artifact rather than merely dating it.
GATES = ('labels', 'tokens', 'blocks', 'head')
# Modules whose source is recorded with an analysis. Recorded, not gated -- see the module docstring.
CODE = ('live_scan.py', 'window_raw.py', 'verify.py', 'labels.py', 'economics.py')


def _sha(s):
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()[:16]


def label_fingerprint():
    """sha over the effective address book as `addr kind source`, sorted.

    Deliberately the *resolved* book rather than the registry file: `load_address_book` merges three sources and the
    merge rule itself has changed twice. Hashing the output means an edit to any input, or to the rule, shows up.
    """
    import live_scan
    book = live_scan.load_address_book()
    body = '\n'.join('%s %s %s' % (a, v.get('kind'), v.get('source')) for a, v in sorted(book.items()))
    return _sha(body), len(book)


def token_fingerprint():
    import live_scan
    return _sha('\n'.join('%s %s' % (a, t) for a, t in sorted(live_scan.TOKENS.items()))), len(live_scan.TOKENS)


def block_fingerprint(out):
    """(sha, count, first, last) over the raw block files actually present."""
    d = Path(out) / 'raw' / 'blocks'
    nums = sorted(int(p.name.split('.')[0]) for p in d.glob('*.json.gz')) if d.exists() else []
    return _sha(','.join(map(str, nums))), len(nums), (nums[0] if nums else None), (nums[-1] if nums else None)


def head_fingerprint(out):
    """The block `head_state.json` was read at, or None when the window has no head state."""
    if out is None:
        return None
    p = Path(out) / 'head_state.json'
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get('block')
    except Exception:
        return None


def code_fingerprint():
    out = {}
    for name in CODE:
        p = ROOT / 'scripts' / name
        if p.exists():
            out[name] = _sha(p.read_bytes())
    return out


def git_state():
    try:
        h = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=5).stdout.strip()
        d = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'],
                           capture_output=True, text=True, timeout=5).stdout.strip()
        return {'commit': h or None, 'dirty': bool(d)}
    except Exception:
        return {'commit': None, 'dirty': None}


def stamp(artifact, out=None, **extra):
    """The provenance block an artifact embeds. `out` enables the block-range gate."""
    lab, n_lab = label_fingerprint()
    tok, n_tok = token_fingerprint()
    s = {'artifact': artifact,
         'generated_at': dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
         'labels': lab, 'label_count': n_lab,
         'tokens': tok, 'token_count': n_tok,
         'code': code_fingerprint(), 'git': git_state()}
    if out is not None:
        blk, n, first, last = block_fingerprint(out)
        s.update({'blocks': blk, 'block_count': n, 'first_block': first, 'last_block': last,
                  'head': head_fingerprint(out)})
    # A caller passing `blocks=1492` would otherwise replace the block *fingerprint* with a count, and the gate would
    # then compare a number against a sha and call every artifact stale. Gate fields are not caller-writable.
    s.update({k: v for k, v in extra.items() if k not in GATES})
    return s


def check(recorded, out=None):
    """Compare an artifact's recorded provenance against the current state.

    Returns `(rows, stale)`. `stale` is true only when a *gate* moved, so a code edit dates an artifact without
    invalidating it. An artifact with no provenance block predates this module: reported, not failed, because failing
    it would make every old window unreadable rather than making the next one honest.
    """
    if not recorded:
        return [{'field': 'provenance', 'artifact': 'absent', 'current': 'present', 'gate': False, 'ok': True,
                 'note': 'artifact predates provenance stamping; re-run analyze to gate it'}], False
    cur = stamp(recorded.get('artifact', '?'), out=out)
    rows, stale = [], False
    for f in GATES:
        if f not in recorded:
            continue
        a, c = recorded.get(f), cur.get(f)
        ok = (a == c)
        note = ''
        if not ok:
            note = {'labels': 'the address book changed since this analysis -- re-run `live_scan analyze`',
                    'tokens': 'the token table changed since this analysis -- re-run `live_scan analyze`',
                    'blocks': 'the raw block set changed since this analysis -- re-run `live_scan analyze`',
                    'head': 'head_state.json was re-read at a different block, so the price basis this analysis used '
                            'is not the one on disk -- re-run `live_scan analyze`'}[f]
            stale = True
        rows.append({'field': f, 'artifact': a, 'current': c, 'gate': True, 'ok': ok, 'note': note})
    for name, sha in (cur.get('code') or {}).items():
        was = (recorded.get('code') or {}).get(name)
        if was and was != sha:
            rows.append({'field': 'code:' + name, 'artifact': was, 'current': sha, 'gate': False, 'ok': True,
                         'note': 'source changed since this analysis (recorded, not a gate)'})
    return rows, stale


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['show', 'check'])
    p.add_argument('--out', help='window directory holding analysis.json')
    a = p.parse_args()
    if a.command == 'show':
        print(json.dumps(stamp('adhoc', out=a.out), indent=1))
        return
    ap = Path(a.out) / 'analysis.json'
    rec = json.loads(ap.read_text()).get('provenance') if ap.exists() else None
    rows, stale = check(rec, out=a.out)
    for r in rows:
        print('%-24s %-18s %-18s %s' % (r['field'], str(r['artifact'])[:18], str(r['current'])[:18],
                                        ('STALE -- ' + r['note']) if not r['ok'] else (r.get('note') or 'ok')))
    print('\n%s' % ('STALE' if stale else 'current'))
    sys.exit(1 if stale else 0)


if __name__ == '__main__':
    main()
