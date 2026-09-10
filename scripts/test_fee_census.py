import json
import tempfile
import unittest
from pathlib import Path

from fee_census import validate_receipts, weighted_quantile, census_blocks
from detectors import Context


class FeeTests(unittest.TestCase):
    def test_weighting_uses_gas_instead_of_transaction_count(self):
        self.assertEqual(weighted_quantile([(0.1, 100), (2.0, 900)], .5), 2.0)

    def test_empty_quantile_is_not_a_zero_cost_quote(self):
        with self.assertRaises(ValueError):
            weighted_quantile([], .5)

    def test_zero_stride_is_rejected(self):
        with self.assertRaises(ValueError):
            census_blocks('.', 0)

    def test_receipts_must_cover_the_exact_block(self):
        b = {'number': '0x1', 'gasUsed': '0x64', 'baseFeePerGas': '0xa',
             'transactions': [{'hash': 'a'}, {'hash': 'b'}]}
        good = [{'h': 'a', 'gu': 40, 'egp': 10, 'st': 0}, {'h': 'b', 'gu': 60, 'egp': 30, 'st': 1}]
        validate_receipts(b, good)
        for bad in (good[:1], [good[0], good[0]],
                    [good[0], dict(good[1], gu=59)], [good[0], dict(good[1], egp=9)]):
            with self.assertRaises(ValueError):
                validate_receipts(b, bad)

    def test_cost_includes_priority_and_rejects_stale_census(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = object.__new__(Context)
            ctx.out = Path(directory)
            ctx.analysis = {'window': {'first_block': 1, 'last_block': 10}}
            data = {'sample_complete': True, 'first_block': 1, 'last_block': 10, 'blocks': 3,
                    'gas_weighted_effective_gwei': {'p50': .06, 'p75': .6, 'p90': 2.1}}
            p = ctx.out / 'fee_census.json'
            p.write_text(json.dumps(data))
            self.assertEqual(ctx.gas_quote()['gwei'], .6)
            self.assertEqual(ctx.gas_quote(race=True)['gwei'], 2.1)
            data['last_block'] = 11
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                ctx.gas_quote()

    def test_fallback_still_includes_observed_tip(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = object.__new__(Context)
            ctx.out = Path(directory)
            ctx._blocks = [{'base_gwei': .05}]
            ctx.analysis = {'gas': {'tip_median_gwei': .2}}
            self.assertAlmostEqual(ctx.gas_quote()['gwei'], .25)


if __name__ == '__main__':
    unittest.main()
