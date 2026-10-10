#!/usr/bin/env python3
"""The unlock forward test inside the daily perp pass: register daily, refresh the schedule only when it is a week old."""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perp_daily as P  # noqa: E402


def schedule(root, rel, collected_at):
    d = root / rel
    d.mkdir(parents=True)
    (d / 'manifest.json').write_text(json.dumps({'collected_at': collected_at.isoformat()}))
    return d


class UnlockSteps(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.saved = P.ROOT, P.UNLOCK_STUDY
        P.ROOT, P.UNLOCK_STUDY = self.root, self.root / 'research' / '2026-10-09' / 'unlocks'

    def tearDown(self):
        P.ROOT, P.UNLOCK_STUDY = self.saved
        self.tmp.cleanup()

    def names(self, S):
        return [name for name, _ in S]

    def test_a_fresh_schedule_is_reused(self):
        now = P.utc_now()
        study = schedule(self.root, 'research/2026-10-09/unlocks', now - dt.timedelta(days=8))
        newer = schedule(self.root, 'research/2026-10-12/unlock_schedule', now - dt.timedelta(days=2))
        self.assertEqual(P.latest_unlock_schedule()[0], newer)
        S = P.unlock_steps(['py'], '2026-10-14', Path('hist'))
        self.assertEqual(self.names(S), ['unlock forward register', 'unlock forward score'])
        self.assertIn(str(newer), S[0][1])
        self.assertNotIn(str(study), S[0][1])

    def test_a_week_old_schedule_is_refreshed_into_today(self):
        schedule(self.root, 'research/2026-10-09/unlocks', P.utc_now() - dt.timedelta(days=8))
        S = P.unlock_steps(['py'], '2026-10-17', Path('hist'))
        self.assertEqual(self.names(S), ['unlock schedule', 'unlock forward register', 'unlock forward score'])
        today = str(self.root / 'research' / '2026-10-17' / 'unlock_schedule')
        self.assertIn(today, S[0][1])
        self.assertIn(today, S[1][1])


if __name__ == '__main__':
    unittest.main()
