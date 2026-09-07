#!/usr/bin/env python3
"""A minimal, independent reader over a collected window's raw blocks and logs.

`live_scan.State` is a large one-pass machine: it prices swaps, infers pool tokens, tracks JIT episodes, follows
proceeds, and produces `analysis.json`. Nothing re-derives its numbers, so a bug in that machine is invisible.

This module is the second opinion. It decodes only what a headline number needs — ERC-20 `Transfer` legs, native value
legs, gas per target, Aave/Spark `ReserveDataUpdated` rate points — in a few dozen lines of straight-line code with no
shared state. `live_scan verify` recomputes the headline numbers through here and fails loudly on drift; `labels.py
coverage` uses the same transfer stream to measure how much window USD flows through unlabelled addresses.

Deliberately shared with `live_scan`: the token table (address -> symbol, decimals, price key) and the price basis read
from the window's own `analysis.json`. Verifying those would be verifying the price feed, not the aggregation. Everything
downstream of them is computed here from scratch.

    from window_raw import Window
    w = Window('research/2026-09-07/live_5h')
    for x in w.transfers(min_usd=1e4):
        ...
"""
import gzip
import json
from pathlib import Path

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
RESERVE_DATA_UPDATED = '0x804c9b842b2748a22bb64b345453a3de7ca54a6ca45ce00d415894979e22897a'
RAY = 10 ** 27
SECONDS_PER_YEAR = 31_536_000
ZERO = '0x' + '0' * 40


def hx(v):
    """Hex quantity -> int, tolerating already-decoded ints and None."""
    if isinstance(v, str):
        return int(v, 16)
    return int(v or 0)


def word(data, i):
    """The i-th 32-byte word of an ABI blob as an unsigned int."""
    off = 2 + i * 64
    return int(data[off:off + 64], 16) if len(data) >= off + 64 else 0


def topic_addr(t):
    return '0x' + t[-40:].lower()


class Window:
    """Raw blocks + logs of one collected window, with just enough decoding to re-derive headline numbers."""

    def __init__(self, out, first=None, last=None, tokens=None, prices=None):
        self.out = Path(out)
        analysis = self.out / 'analysis.json'
        self.analysis = json.loads(analysis.read_text()) if analysis.exists() else {}
        # The price basis is the one `analyze` actually used, so a verify mismatch means the aggregation drifted,
        # not that the feed moved between runs.
        self.prices = dict(prices if prices is not None else self.analysis.get('price_basis', {}))
        if tokens is None:
            import live_scan
            tokens = live_scan.TOKENS
        self.tokens = tokens
        nums = sorted(int(p.name.split('.')[0]) for p in (self.out / 'raw' / 'blocks').glob('*.json.gz'))
        self.nums = [n for n in nums if (first is None or n >= first) and (last is None or n <= last)
                     and (self.out / 'raw' / 'logs' / ('%d.json.gz' % n)).exists()]

    # -- io ------------------------------------------------------------------------------------------------------------
    def _read(self, kind, n):
        with gzip.open(self.out / 'raw' / kind / ('%d.json.gz' % n), 'rt') as f:
            return json.load(f)

    def blocks(self):
        """Yield (block, logs) for every block in range, in ascending block order."""
        for n in self.nums:
            yield self._read('blocks', n), self._read('logs', n)

    # -- pricing -------------------------------------------------------------------------------------------------------
    def usd(self, token, raw):
        """USD value of a raw token amount, or None when the token is not in the priced table."""
        t = self.tokens.get(token)
        if not t:
            return None
        px = self.prices.get(t[2])
        if px is None:
            return None
        return raw / 10 ** t[1] * px

    def symbol(self, token):
        t = self.tokens.get(token)
        return t[0] if t else None

    # -- streams -------------------------------------------------------------------------------------------------------
    def transfers(self, min_usd=1e4, include_native=True):
        """Every priced value leg at or above `min_usd`: ERC-20 Transfer logs plus native tx value.

        Straight-line decode: a Transfer is topic0 + 2 indexed topics + a 32-byte amount. No pool inference, no swap
        pricing, no dedup — deliberately the dumbest correct reading of the raw data.
        """
        for b, logs in self.blocks():
            n, ts = hx(b['number']), hx(b['timestamp'])
            if include_native:
                eth = self.prices.get('ETH')
                for t in b['transactions']:
                    v = hx(t.get('value', 0))
                    if v and eth and t.get('to'):
                        u = v / 1e18 * eth
                        if u >= min_usd:
                            yield {'block': n, 'ts': ts, 'tx': t['hash'], 'token': 'ETH', 'sym': 'ETH',
                                   'from': t['from'].lower(), 'to': t['to'].lower(), 'raw': v, 'usd': u, 'li': -1}
            for l in logs:
                tp = l['topics']
                if not tp or tp[0] != TRANSFER or len(tp) != 3 or len(l['data']) < 66:
                    continue
                tok = l['address'].lower()
                u = self.usd(tok, word(l['data'], 0))
                if u is None or u < min_usd:
                    continue
                yield {'block': n, 'ts': ts, 'tx': l['transactionHash'], 'token': tok, 'sym': self.symbol(tok),
                       'from': topic_addr(tp[1]), 'to': topic_addr(tp[2]), 'raw': word(l['data'], 0), 'usd': u,
                       'li': hx(l['logIndex'])}

    def gas_by_target(self):
        """tx.to -> total gas limit requested. The gas-spike attribution reduces to this counter."""
        import collections
        g = collections.Counter()
        for b, _ in self.blocks():
            for t in b['transactions']:
                if t.get('to'):
                    g[t['to'].lower()] += hx(t['gas'])
        return g

    def rate_points(self, pools):
        """(venue, reserve) -> [(block, ts, supply_apr, borrow_apr)] from Aave-style ReserveDataUpdated logs.

        `pools` maps a pool address to a venue name. The event packs liquidityRate at word 0 and variableBorrowRate at
        word 2, both in ray per second scaled to a year; the APR is the linear rate the protocol itself reports.
        """
        import collections
        out = collections.defaultdict(list)
        for b, logs in self.blocks():
            n, ts = hx(b['number']), hx(b['timestamp'])
            for l in logs:
                tp = l['topics']
                if not tp or tp[0] != RESERVE_DATA_UPDATED or len(tp) < 2:
                    continue
                venue = pools.get(l['address'].lower())
                if not venue:
                    continue
                d = l['data']
                out[(venue, topic_addr(tp[1]))].append((n, ts, word(d, 0) / RAY, word(d, 2) / RAY))
        return out

    def block_stats(self):
        """Per-block base fee and gas used, for de-spiking and window bookkeeping."""
        rows = []
        for b, _ in self.blocks():
            rows.append({'n': hx(b['number']), 'ts': hx(b['timestamp']), 'base_gwei': hx(b.get('baseFeePerGas', 0)) / 1e9,
                         'gas_used': hx(b['gasUsed']), 'txs': len(b['transactions'])})
        return rows


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


if __name__ == '__main__':
    import sys
    w = Window(sys.argv[1] if len(sys.argv) > 1 else 'research/2026-09-07/live_5h')
    n = sum(1 for _ in w.transfers(min_usd=1e6))
    print(json.dumps({'blocks': len(w.nums), 'transfers_1m': n, 'priced_keys': len(w.prices)}))
