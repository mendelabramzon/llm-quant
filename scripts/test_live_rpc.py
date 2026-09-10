import threading
import unittest

from live_rpc import RPC


class ReadBatchTests(unittest.TestCase):
    def test_parallel_chunks_preserve_pinned_block_and_result_order(self):
        rpc = object.__new__(RPC)
        barrier = threading.Barrier(2)
        def batch(calls, allow_errors):
            self.assertTrue(allow_errors)
            self.assertTrue(all(method == 'eth_call' and params[1] == '0x123' for method, params in calls))
            barrier.wait(timeout=3)
            return [params[0]['data'] for _, params in calls]
        rpc.batch = batch
        values = [('0xabc', hex(i + 1)) for i in range(40)]
        self.assertEqual(rpc.eth_calls(values, '0x123'), [v for _, v in values])

    def test_empty_and_failed_reads_keep_their_position(self):
        rpc = object.__new__(RPC)
        rpc.batch = lambda calls, allow_errors: ['0x1', {'error': {'code': -1}}, None, '0x']
        self.assertEqual(rpc.eth_calls([('a', 'b')] * 4), ['0x1', None, None, None])
        self.assertEqual(rpc.eth_calls([]), [])


if __name__ == '__main__':
    unittest.main()
