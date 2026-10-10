#!/usr/bin/env python3
"""The book's door: `validate` and `add` on a temporary book, so a malformed study entry cannot enter it."""
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strategies as S  # noqa: E402


def entry(**kw):
    e = {'id': 'x-carry', 'name': 'X carry', 'kind': 'carry', 'status': 'proposed', 'thesis': 't', 'mechanism': 'm',
         'legs': ['buy', 'sell'], 'capacity_usd': 1e6, 'kill_criteria': ['k'], 'risks': ['r'],
         'evidence': {'findings': [], 'verify': [], 'notes': 'n'},
         'quotes': [{'at': '2026-10-09T20:00:00+00:00', 'net_apr': 0.1, 'usd': 1e5, 'present': True,
                     'source': 'history', 'window': 'research/2026-10-09/x', 'note': 'q'}]}
    e.update(kw)
    return e


class Door(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = S.BOOK
        S.BOOK = Path(self.tmp.name) / 'strategies.jsonl'

    def tearDown(self):
        S.BOOK = self.old
        self.tmp.cleanup()

    def write(self, entries):
        p = Path(self.tmp.name) / 'book_entries.json'
        p.write_text(json.dumps(entries))
        return p

    def test_valid_entry_passes(self):
        self.assertEqual(S.validate(entry()), [])

    def test_entry_without_kill_criteria_or_capacity_is_refused(self):
        errs = S.validate(entry(kill_criteria=[], capacity_usd=None))
        self.assertTrue(any('kill' in e for e in errs))
        self.assertTrue(any('capacity' in e for e in errs))

    def test_unknown_kind_and_status_are_refused(self):
        errs = S.validate(entry(kind='alpha', status='live'))
        self.assertEqual(len(errs), 2)

    def test_add_then_replace_keeps_the_quote_history(self):
        S.add(Namespace(file=self.write([entry()]), replace=False, dry_run=False))
        newer = entry(capacity_usd=2e6, quotes=[{'at': '2026-10-10T20:00:00+00:00', 'net_apr': 0.05, 'usd': 1e5,
                                                  'present': True, 'source': 'history', 'window': 'w2'}])
        S.add(Namespace(file=self.write([newer]), replace=False, dry_run=False))
        self.assertEqual(S.load()['x-carry']['capacity_usd'], 1e6)          # skipped without --replace
        S.add(Namespace(file=self.write([newer]), replace=True, dry_run=False))
        b = S.load()['x-carry']
        self.assertEqual(b['capacity_usd'], 2e6)
        self.assertEqual([q['net_apr'] for q in b['quotes']], [0.1, 0.05])

    def test_a_rejected_entry_exits_nonzero_and_writes_nothing_for_it(self):
        with self.assertRaises(SystemExit):
            S.add(Namespace(file=self.write([entry(id='bad', legs=[])]), replace=False, dry_run=False))
        self.assertNotIn('bad', S.load())


if __name__ == '__main__':
    unittest.main()
