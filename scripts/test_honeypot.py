#!/usr/bin/env python3
"""Positive and negative controls for the honeypot screen.

Across four real windows — about eleven hours of mainnet — the screen reports no proven honeypot. That is the right
answer and it is also indistinguishable, from the outside, from a detector that can no longer fire at all: three
successive tightenings removed every false positive it had, and the last of them (a failed sale must come from a
holder) removed all of them at once. A screen with no positives on real data has to be shown to work on data where
the answer is known.

So these are synthetic windows in the collector's own on-disk format, built to be the two cases that matter:

  * a **honeypot** — many buyers, no successful sellers, and holders whose sell transactions emit no logs;
  * a **normal launch** — the same lopsided buyer-to-seller ratio, because nobody has sold yet, but no failed sale.

The second is the one that matters. It is the shape that a naive ratio test calls a honeypot, and every token the
screen flags at `info` on real windows looks exactly like it.

    uv run --with pycryptodome python scripts/test_honeypot.py
"""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
V2_SWAP = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
ROUTER = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'
POOL = '0x' + 'p0'.encode().hex().ljust(40, '1')[:40]
TOKEN = '0x' + 'to'.encode().hex().ljust(40, '2')[:40]


def addr(i, tag='b'):
    """A well-formed 42-character address. The first draft built a 40-character one, and since a Transfer topic is
    read back through `topic_addr` — which always yields the full width — the buyer recorded from the log never
    matched the `from` of the transaction. The positive control failed on the harness, not on the detector, which is
    the sort of thing a control is for."""
    return '0x' + ('%s%038x' % (tag.encode().hex(), i))[:40]


def topic(a):
    return '0x' + '0' * 24 + a[2:]


def word32(v):
    return '%064x' % v


class Window:
    """The minimum a `Context` needs: raw/blocks, raw/logs, and an analysis with a window and a price basis."""

    def __init__(self, root):
        self.root = Path(root)
        (self.root / 'raw' / 'blocks').mkdir(parents=True, exist_ok=True)
        (self.root / 'raw' / 'logs').mkdir(parents=True, exist_ok=True)
        self.n = 1000
        (self.root / 'analysis.json').write_text(json.dumps({
            'window': {'first_utc': '2026-09-08T00:00:00+00:00', 'last_utc': '2026-09-08T01:00:00+00:00',
                       'first_block': 1000, 'last_block': 1100, 'hours': 1.0},
            'price_basis': {'ETH': 2500.0}}))

    def block(self, txs, logs):
        n = self.n
        self.n += 1
        b = {'number': hex(n), 'timestamp': hex(1788800000 + n * 12), 'gasUsed': hex(15_000_000),
             'baseFeePerGas': hex(50_000_000), 'transactions': txs}
        for i, l in enumerate(logs):
            l.setdefault('logIndex', hex(i))
            l.setdefault('address', TOKEN)
        with gzip.open(self.root / 'raw' / 'blocks' / ('%d.json.gz' % n), 'wt') as f:
            json.dump(b, f)
        with gzip.open(self.root / 'raw' / 'logs' / ('%d.json.gz' % n), 'wt') as f:
            json.dump(logs, f)
        return n

    def buy(self, i):
        """One buy: a swap on the pool, and the token leaving the pool to the buyer."""
        h = '0x%064x' % (0xbee0000 + i)
        buyer = addr(i, 'b')
        tx = {'hash': h, 'from': buyer, 'to': ROUTER, 'gas': hex(200_000), 'value': '0x0',
              'input': '0x38ed1739' + word32(0) + topic(TOKEN)[2:]}
        logs = [{'transactionHash': h, 'address': POOL, 'topics': [V2_SWAP, topic(ROUTER), topic(buyer)],
                 'data': '0x' + word32(0) * 4},
                {'transactionHash': h, 'address': TOKEN, 'topics': [TRANSFER, topic(POOL), topic(buyer)],
                 'data': '0x' + word32(10 ** 18)}]
        self.block([tx], logs)
        return buyer

    def failed_sell(self, buyer, i):
        """A holder calls the router naming the token, and the transaction emits nothing: it reverted."""
        h = '0x%064x' % (0xdead0000 + i)
        tx = {'hash': h, 'from': buyer, 'to': ROUTER, 'gas': hex(200_000), 'value': '0x0',
              'input': '0x18cbafe5' + word32(0) + topic(TOKEN)[2:]}
        self.block([tx], [])

    def good_sell(self, buyer, i):
        h = '0x%064x' % (0x5e110000 + i)
        tx = {'hash': h, 'from': buyer, 'to': ROUTER, 'gas': hex(200_000), 'value': '0x0',
              'input': '0x18cbafe5' + word32(0) + topic(TOKEN)[2:]}
        logs = [{'transactionHash': h, 'address': POOL, 'topics': [V2_SWAP, topic(ROUTER), topic(buyer)],
                 'data': '0x' + word32(0) * 4},
                {'transactionHash': h, 'address': TOKEN, 'topics': [TRANSFER, topic(buyer), topic(POOL)],
                 'data': '0x' + word32(10 ** 18)}]
        self.block([tx], logs)


def scan(root):
    from detectors import Context
    import detectors.honeypot_signature as H
    return H.scan(Context(root))


class HoneypotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_honeypot_is_reported_high(self):
        w = Window(Path(self.tmp.name) / 'trap')
        holders = [w.buy(i) for i in range(20)]
        for i, h in enumerate(holders[:12]):
            w.failed_sell(h, i)
        hits = scan(w.root)
        self.assertTrue(hits, 'the screen found nothing in a window built to contain a honeypot')
        top = hits[0]
        self.assertEqual(top.severity, 'high')
        self.assertEqual(top.evidence['distinct_sellers'], 0)
        self.assertEqual(top.evidence['fail_rate'], 1.0)

    def test_a_normal_launch_is_not_called_a_honeypot(self):
        """The control that matters: the same lopsided ratio, with no failed sale."""
        w = Window(Path(self.tmp.name) / 'launch')
        holders = [w.buy(i) for i in range(20)]
        for i, h in enumerate(holders[:6]):
            w.good_sell(h, i)
        hits = scan(w.root)
        self.assertTrue(all(h.severity != 'high' for h in hits),
                        'a launch where sales succeed must never be reported as a honeypot')

    def test_a_stranger_calling_a_router_is_not_a_failed_sale(self):
        """The attribution rule: only a holder can be failing to sell."""
        w = Window(Path(self.tmp.name) / 'stranger')
        [w.buy(i) for i in range(20)]
        for i in range(15):
            w.failed_sell(addr(900 + i, 'z'), i)     # never bought the token
        hits = scan(w.root)
        self.assertTrue(all(h.severity != 'high' for h in hits))
        if hits:
            self.assertEqual(hits[0].evidence['router_calls_naming_it'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
