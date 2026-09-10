"""Window boundaries must survive retries and lag without changing the research population."""
import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import live_collect as c


class FakeRPC:
    keys = ['test']

    def call(self, method, params):
        if method == 'eth_chainId':
            return '0x1'
        tag = params[0]
        n = 1000 if tag == 'finalized' else int(tag, 16)
        return {'number': hex(n), 'timestamp': hex(n * 12), 'hash': 'hash-%d' % n}

    def stats(self):
        return {'credits': 0}

    def clean(self, message):
        return message


class CollectionTests(unittest.TestCase):
    def run_collect(self, out, **overrides):
        args = dict(out=str(out), hours=1, lag=2, end_tag='finalized', workers=1,
                    block_batch=4, log_range=6, max_credits=1000)
        args.update(overrides)
        def blocks(rpc, directory, nums):
            for n in nums:
                c.write_gz(c.block_path(directory, n), {'number': hex(n)})
        def logs(rpc, directory, first, last, splits):
            for n in range(first, last + 1):
                c.write_gz(c.logs_path(directory, n), [])
        with patch.object(c, 'RPC', return_value=FakeRPC()), \
             patch.object(c, 'first_block_at', return_value=996) as search, \
             patch.object(c, 'fetch_blocks', side_effect=blocks), \
             patch.object(c, 'fetch_logs', side_effect=logs), contextlib.redirect_stdout(io.StringIO()):
            c.collect(argparse.Namespace(**args))
        return json.loads((out / 'manifest.json').read_text()), search

    def test_finalized_lag_uses_actual_endpoint_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            m, search = self.run_collect(Path(d))
        self.assertEqual(m['last_block'], 998)
        self.assertEqual(m['end_timestamp'], 998 * 12 + 1)
        self.assertEqual(m['end_timestamp'] - m['start_timestamp'], 3600)
        self.assertEqual(search.call_args.args[1:], (998 * 12 + 1 - 3600, 998))
        self.assertEqual(m['finalized_at_start']['number'], 1000)
        self.assertTrue(m['complete'])

    def test_resume_never_reads_new_head_or_moves_boundaries(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            before, _ = self.run_collect(out)
            # An interrupted download must refill the same population even if flags/head change.
            c.logs_path(out, 997).unlink()
            with patch.object(c, 'head', side_effect=AssertionError('resume read the head')):
                after, search = self.run_collect(out, hours=10, lag=0, end_tag='latest')
            for field in ('first_block', 'last_block', 'start_timestamp', 'end_timestamp', 'endpoint'):
                self.assertEqual(before[field], after[field])
            search.assert_not_called()
            self.assertTrue(after['complete'])

    def test_incomplete_download_exits_unsuccessfully(self):
        with tempfile.TemporaryDirectory() as d:
            args = argparse.Namespace(out=d, hours=1, lag=0, end_tag='finalized', workers=1,
                                      block_batch=4, log_range=6, max_credits=1000)
            with patch.object(c, 'RPC', return_value=FakeRPC()), \
                 patch.object(c, 'first_block_at', return_value=1000), \
                 patch.object(c, 'fetch_blocks', side_effect=RuntimeError('failed download')), \
                 patch.object(c, 'fetch_logs', return_value=[]), contextlib.redirect_stdout(io.StringIO()), \
                 self.assertRaisesRegex(SystemExit, 'collection incomplete'):
                c.collect(args)
            self.assertFalse(json.loads((Path(d) / 'manifest.json').read_text())['complete'])


if __name__ == '__main__':
    unittest.main()
