#!/usr/bin/env python3
"""Unit tests for the findings ledger and the provenance stamp.

Both modules are bookkeeping, which is exactly the kind of code that is wrong quietly. A ledger that appends instead of
upserting inflates "seen 4 times" for a finding observed once and re-ingested three times; an eligibility count that
ignores which detectors actually ran turns "seen 1 of 4" — a spot artifact — into "seen 1 of 1", a standing edge. A
provenance gate that a caller can overwrite through `extra` marks every artifact stale and teaches the reader to pass
`--ignore-stale` by reflex, which is worse than having no gate. Each of those is a real bug this file pins down; the
`extra`-clobbering one was live for about ten minutes.

    uv run --with pycryptodome python scripts/test_findings.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import findings as F
import provenance as P


def window(out, hits, detectors, first_utc='2026-09-07T02:39:11+00:00', last_utc='2026-09-07T07:39:11+00:00'):
    """Write the minimal `analysis.json` + `detectors.json` pair that `ingest` reads."""
    out.mkdir(parents=True, exist_ok=True)
    (out / 'analysis.json').write_text(json.dumps({
        'window': {'first_utc': first_utc, 'last_utc': last_utc, 'first_block': 1, 'last_block': 2, 'hours': 5.0},
        'provenance': {'labels': 'abc'}}))
    (out / 'detectors.json').write_text(json.dumps({
        'detectors': [{'detector': d, 'error': None} for d in detectors], 'hits': hits}))
    return out


def hit(detector, key, usd=None, severity='notable', net_apr=None):
    h = {'detector': detector, 'key': key, 'identity': '%s:%s' % (detector, key), 'title': '%s on %s' % (detector, key),
         'severity': severity, 'usd': usd, 'evidence': {}}
    if net_apr is not None:
        h['economics'] = {'net_apr': net_apr, 'go': True}
    return h


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        F.LEDGER = self.root / 'findings.jsonl'
        F.WINDOWS = self.root / 'windows.json'

    def tearDown(self):
        self.tmp.cleanup()

    def test_identity_is_stable_and_distinct(self):
        self.assertEqual(F.fid('rate_dispersion:USDS'), F.fid('rate_dispersion:USDS'))
        self.assertNotEqual(F.fid('rate_dispersion:USDS'), F.fid('rate_dispersion:USDC'))

    def test_reingesting_a_window_replaces_rather_than_appends(self):
        """The bug this prevents: re-running a window after a detector fix would otherwise read as recurrence."""
        w = window(self.root / 'w1', [hit('rate_dispersion', 'USDS', 100.0)], ['rate_dispersion'])
        F.ingest(w)
        F.ingest(w)
        L = F.load_ledger()
        self.assertEqual(len(L), 1)
        self.assertEqual(len(list(L.values())[0]['observations']), 1)

    def test_two_windows_make_one_finding_seen_twice(self):
        F.ingest(window(self.root / 'w1', [hit('rate_dispersion', 'USDS', 100.0)], ['rate_dispersion']))
        F.ingest(window(self.root / 'w2', [hit('rate_dispersion', 'USDS', 90.0)], ['rate_dispersion'],
                        last_utc='2026-09-07T12:39:11+00:00'))
        L = F.load_ledger()
        self.assertEqual(len(L), 1)
        r = list(L.values())[0]
        self.assertEqual(len(r['observations']), 2)
        self.assertEqual([o['usd'] for o in r['observations']], [100.0, 90.0])

    def test_eligibility_counts_only_windows_that_ran_the_detector(self):
        """A finding absent from a window that never ran its detector is not evidence of decay."""
        F.ingest(window(self.root / 'w1', [hit('rate_dispersion', 'USDS')], ['rate_dispersion']))
        F.ingest(window(self.root / 'w2', [hit('gas_concentration', 'x')], ['gas_concentration'],
                        last_utc='2026-09-07T12:39:11+00:00'))
        L, W = F.load_ledger(), F.load_windows()
        elig, seen = F.coverage(L, W)
        for i, r in L.items():
            self.assertEqual((seen[i], elig[i]), (1, 1), r['identity'])

    def test_absence_from_an_eligible_window_shows_as_one_of_two(self):
        F.ingest(window(self.root / 'w1', [hit('rate_dispersion', 'USDS')], ['rate_dispersion']))
        F.ingest(window(self.root / 'w2', [], ['rate_dispersion'], last_utc='2026-09-07T12:39:11+00:00'))
        L, W = F.load_ledger(), F.load_windows()
        elig, seen = F.coverage(L, W)
        i = list(L)[0]
        self.assertEqual((seen[i], elig[i]), (1, 2))

    def test_latest_observation_drives_severity_and_cadence(self):
        F.ingest(window(self.root / 'w1', [hit('mislabelled_flow', 'a', severity='info')], ['mislabelled_flow']))
        F.ingest(window(self.root / 'w2', [hit('mislabelled_flow', 'a', severity='high')], ['mislabelled_flow'],
                        last_utc='2026-09-07T12:39:11+00:00'))
        r = list(F.load_ledger().values())[0]
        self.assertEqual(r['severity'], 'high')
        self.assertEqual(r['recheck_hours'], F.RECHECK_HOURS['high'])

    def test_economics_series_is_kept_in_order(self):
        F.ingest(window(self.root / 'w1', [hit('rate_dispersion', 'USDS', net_apr=0.035)], ['rate_dispersion']))
        F.ingest(window(self.root / 'w2', [hit('rate_dispersion', 'USDS', net_apr=0.012)], ['rate_dispersion'],
                        last_utc='2026-09-07T12:39:11+00:00'))
        r = list(F.load_ledger().values())[0]
        self.assertEqual([o['net_apr'] for o in r['observations']], [0.035, 0.012])

    def test_close_marks_resolved_with_a_reason(self):
        F.ingest(window(self.root / 'w1', [hit('solver_fingerprint', '0xabc')], ['solver_fingerprint']))
        i = list(F.load_ledger())[0]
        F.close(type('A', (), {'id': i, 'detector': None, 'key': None, 'note': 'labelled'})())
        r = F.load_ledger()[i]
        self.assertEqual(r['status'], 'resolved')
        self.assertEqual(r['resolution']['note'], 'labelled')


class ProvenanceTest(unittest.TestCase):
    def test_extra_cannot_overwrite_a_gate_field(self):
        """`stamp('analysis', blocks=1492)` once replaced the block fingerprint with a count, so every artifact was
        stale against a sha it could never match."""
        s = P.stamp('t', blocks='not-a-sha', labels='not-a-sha')
        self.assertNotEqual(s.get('labels'), 'not-a-sha')
        self.assertNotIn('blocks', {k: v for k, v in s.items() if v == 'not-a-sha'})

    def test_missing_provenance_is_reported_but_not_stale(self):
        rows, stale = P.check(None)
        self.assertFalse(stale)
        self.assertEqual(len(rows), 1)
        self.assertIn('predates', rows[0]['note'])

    def test_matching_stamp_is_current(self):
        s = P.stamp('t')
        rows, stale = P.check(s)
        self.assertFalse(stale)
        self.assertTrue(all(r['ok'] for r in rows))

    def test_changed_labels_are_stale(self):
        s = dict(P.stamp('t'), labels='0000000000000000')
        rows, stale = P.check(s)
        self.assertTrue(stale)
        self.assertTrue(any(r['field'] == 'labels' and not r['ok'] for r in rows))

    def test_changed_code_is_recorded_but_not_stale(self):
        s = P.stamp('t')
        s['code'] = dict(s['code'])
        s['code']['live_scan.py'] = '0000000000000000'
        rows, stale = P.check(s)
        self.assertFalse(stale)
        self.assertTrue(any(r['field'] == 'code:live_scan.py' for r in rows))


if __name__ == '__main__':
    unittest.main(verbosity=2)
