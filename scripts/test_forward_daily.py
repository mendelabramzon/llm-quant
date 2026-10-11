#!/usr/bin/env python3
"""The forward-test runner: the JLP snapshot runs first, every test's verdict is read back, missing files are tolerated."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forward_daily as F  # noqa: E402


class Steps(unittest.TestCase):
    def test_the_jlp_snapshot_is_first_and_every_test_has_a_step(self):
        names = [n for n, _ in F.steps()]
        self.assertEqual(names[0], 'jlp snapshot')
        self.assertLess(names.index('jlp snapshot'), names.index('jlp score'))
        self.assertLess(names.index('gold snapshot'), names.index('gold score'))
        self.assertLess(names.index('money-market snapshot'), names.index('money-market score'))
        scripts = {cmd[1] for _, cmd in F.steps()}
        for s in scripts:
            self.assertTrue((F.ROOT / s).exists(), s)

    def test_no_step_aborts_the_pass(self):
        self.assertEqual(F.CRITICAL, ())


class Verdicts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = F.ROOT
        F.ROOT = Path(self.tmp.name)
        (F.ROOT / 'research').mkdir()

    def tearDown(self):
        F.ROOT = self.saved
        self.tmp.cleanup()

    def put(self, name, obj):
        (F.ROOT / 'research' / name).write_text(json.dumps(obj))

    def test_nothing_scored_yet(self):
        self.assertEqual(F.verdicts(), {})

    def test_each_file_is_read_where_its_score_step_writes_it(self):
        self.put('jlp_forward.json', {'summary': {'verdict': 'accumulating (3 of 60 days)', 'days': 3.0, 'ann_excess': 0.02},
                                      'flags': {'warnings': ['w'], 'events': []}})
        self.put('queue_live_paper.json', {'verdict': 'continue: no kill criterion met', 'data_through': 'x',
                                           'paper': {'fills': 2}})
        self.put('gold_carry_forward.json', {'summary': {'verdict': 'accumulating (1 of 90 days)'}})
        self.put('mm_rotation_forward.json', {'summary': {'verdict': 'accumulating (0 of 6 holds)', 'kill': []}})
        self.put('dat_events_forward.json', {'summary': {'verdict': 'accumulating (0 of 4 candidate horizons scored)'}})
        V = F.verdicts()
        self.assertEqual(V['jlp']['verdict'], 'accumulating (3 of 60 days)')
        self.assertEqual(V['jlp']['warnings'], ['w'])
        self.assertEqual(V['queue_book']['fills'], 2)
        self.assertEqual(V['gold']['verdict'], 'accumulating (1 of 90 days)')
        self.assertEqual(V['money_markets']['verdict'], 'accumulating (0 of 6 holds)')
        self.assertTrue(V['dat_events']['verdict'].startswith('accumulating'))

    def test_collateral_events_skip_baselines_and_count_today(self):
        today = F.utc_now().strftime('%Y-%m-%d')
        rows = [{'event': 'baseline', 'new_date': today, 'venue': 'binance', 'program': 'portfolio_margin', 'asset': None},
                {'event': 'added', 'new_date': today, 'venue': 'hyperliquid', 'program': 'portfolio_margin', 'asset': 'KHYPE'},
                {'event': 'haircut_changed', 'new_date': '2026-01-01', 'venue': 'okx', 'program': 'multi_currency_margin',
                 'asset': 'DOGE'}]
        (F.ROOT / 'research' / 'collateral_events.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
        C = F.verdicts()['collateral']
        self.assertEqual(C['events_total'], 2)
        self.assertEqual(C['events_today'], 1)
        self.assertEqual(C['today'], ['added hyperliquid/portfolio_margin KHYPE'])

    def test_a_corrupt_file_is_skipped(self):
        (F.ROOT / 'research' / 'jlp_forward.json').write_text('{not json')
        self.assertNotIn('jlp', F.verdicts())


if __name__ == '__main__':
    unittest.main()
