#!/usr/bin/env python3
"""An idle Aave reserve's stored rates against its drifted head utilisation: stale-but-consistent passes, a bad decode
still fails. Pinned with the 2026-10-09 Aave v3 FRAX reading that first tripped the identity checks."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

CURVE = {'base': 0.0, 'optimal': 0.9, 'reserve_factor': 0.2, 'slope1': 0.055, 'slope2': 0.4}


def head(supply_apr, borrow_apr, util):
    return {'lending': {'Aave v3': {'0xfrax': {'sym': 'FRAX', 'utilisation': util, 'supply_apr': supply_apr,
                                               'borrow_apr': borrow_apr, 'supplied_usd': 29621.29,
                                               'borrowed_usd': 29621.29 * util}}},
            'rate_curves': {'Aave v3 FRAX': CURVE}}


def run(hs):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / 'head_state.json').write_text(json.dumps(hs))
        return {r['id']: r for r in V.run_identities(d)}


class StaleReserve(unittest.TestCase):
    def test_inverse_irm(self):
        self.assertAlmostEqual(V._aave_util_from_borrow(CURVE, V._aave_borrow_at(CURVE, 0.9568)), 0.9568)
        self.assertAlmostEqual(V._aave_util_from_borrow(CURVE, V._aave_borrow_at(CURVE, 0.45)), 0.45)

    def test_the_frax_reading_is_stale_not_wrong(self):
        r = run(head(0.2158206447566147, 0.28200948602832, 0.964410565032305))
        self.assertTrue(r['head-supply-identity']['ok'])
        self.assertTrue(r['head-irm-identity']['ok'])
        self.assertEqual(r['head-stale-reserves']['examples'][0]['rates_utilisation'], 0.9568)

    def test_a_bad_decode_still_fails(self):
        # supply rate decoded as the borrow rate: no single utilisation makes the pair consistent
        r = run(head(0.28200948602832, 0.28200948602832, 0.964410565032305))
        self.assertFalse(r['head-supply-identity']['ok'])

    def test_rates_above_the_head_utilisation_are_not_excused(self):
        # stored rates imply a higher utilisation than the head: accrual cannot do that, so it stays a failure
        b = V._aave_borrow_at(CURVE, 0.99)
        r = run(head(b * 0.99 * 0.8, b, 0.95))
        self.assertFalse(r['head-irm-identity']['ok'])


if __name__ == '__main__':
    unittest.main()
