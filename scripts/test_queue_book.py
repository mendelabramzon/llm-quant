"""queue_book: the shared-pool simulator must equal the per-asset one when there is one asset, add up when the
assets never overlap, and ration when they do."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dislocation_history as D   # noqa: E402
import queue_book as Q            # noqa: E402


def _env(sells, wait=2.0, carry_bps_day=0.7, market=None, accrues=False, fee=0.0):
    return {'sells': sorted(sells, key=lambda s: s['ts']), 'wait': (lambda ts: wait), 'carry': (lambda ts: carry_bps_day),
            'market': market or (lambda ts: None), 'accrues': accrues, 'redemption_fee_bps': fee}


def _sells(n, seed, t0=1_700_000_000, span_days=60):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        out.append({'ts': t0 + rng.randrange(span_days * 86400), 'usd': rng.choice([2e4, 1e5, 5e5, 3e6]),
                    'discount_bps': rng.uniform(-5, 60), 'fee_bps': rng.choice([0.0, 1.0, 4.0]), 'pool': 'p', 'tx': '0x%x' % i})
    return sorted(out, key=lambda s: s['ts'])


def test_one_asset_reproduces_simulate_bid():
    sells = _sells(400, 1)
    market = (lambda ts: 25.0)
    for size in (1e5, 1e6, 5e6):
        for h in (0.0, 3.0, 10.0):
            ref, st_ref = D.simulate_bid(sells, size, h, lambda ts: 2.0, lambda ts: 0.7, market_bps_at=market)
            got, st = Q.simulate_book({'a': _env(sells, market=market)}, size, h)
            assert [(f['ts'], round(f['usd'], 6), round(f['value_usd'], 6)) for f in ref] == \
                   [(f['ts'], round(f['usd'], 6), round(f['value_usd'], 6)) for f in got]
            assert abs(st_ref['filled_usd'] - st['filled_usd']) < 1e-6


def test_disjoint_assets_add_up():
    a = _sells(150, 2, t0=1_700_000_000, span_days=30)
    b = _sells(150, 3, t0=1_700_000_000 + 60 * 86400, span_days=30)    # starts after every a-fill has been released
    size = 2e6
    fa, _ = Q.simulate_book({'a': _env(a)}, size, 0.0)
    fb, _ = Q.simulate_book({'b': _env(b)}, size, 0.0)
    fab, st = Q.simulate_book({'a': _env(a), 'b': _env(b)}, size, 0.0)
    assert abs(sum(f['value_usd'] for f in fa) + sum(f['value_usd'] for f in fb) - sum(f['value_usd'] for f in fab)) < 1e-6
    assert set(st['by_asset_value_usd']) == {'a', 'b'}


def test_overlapping_assets_share_the_pool():
    t = 1_700_000_000
    a = [{'ts': t, 'usd': 1e6, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    b = [{'ts': t + 3600, 'usd': 1e6, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    fills, st = Q.simulate_book({'a': _env(a, wait=5.0), 'b': _env(b, wait=5.0)}, 1e6, 0.0)
    assert [f['asset'] for f in fills] == ['a']                     # b arrives while a's capital is still queued
    assert st['missed_capital_usd'] == 1e6
    fills, _ = Q.simulate_book({'a': _env(a, wait=5.0), 'b': _env(b, wait=5.0)}, 2e6, 0.0)
    assert [f['asset'] for f in fills] == ['a', 'b']


def test_locked_daily_counts_the_wait():
    fills = [{'ts': 10 * 86400 + 100, 'usd': 5.0, 'wait_days': 2.0}, {'ts': 11 * 86400, 'usd': 1.0, 'wait_days': 0.5}]
    v = Q.locked_daily(fills, 9, 6)
    assert v == [0.0, 5.0, 6.0, 5.0, 0.0, 0.0]
