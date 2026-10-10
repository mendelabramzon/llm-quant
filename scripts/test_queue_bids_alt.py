"""Core math of queue_bids_alt: discount against the exchange rate, swap reconstruction from transfers, the kHYPE
payout check, bid fill/redeem accounting, and the carry with a staked token as collateral.

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_queue_bids_alt.py -q
"""
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import queue_bids_alt as Q  # noqa: E402
import queue_book as QB  # noqa: E402

DAY = 86400
HOUR = 3600


# ---------------------------------------------------------------------------------------------- discount alignment
def test_rate_fn_linear_and_step_and_bounds():
    s = [(0, 1.0), (DAY, 1.001)]
    lin = Q.rate_fn(s)
    step = Q.rate_fn(s, mode='step')
    assert abs(lin(DAY // 2) - 1.0005) < 1e-12
    assert step(DAY // 2) == 1.0
    assert lin(-1) is None                       # no extrapolation before the first sample
    assert lin(DAY + 3 * DAY) is None            # nor long after the last one
    assert lin(DAY + HOUR) == 1.001              # held a little past the last sample


def test_bar_records_discount_units_and_zero_volume():
    rate = Q.rate_fn([(0, 1.02), (10 * DAY, 1.02)])
    usd = lambda ts: 50.0  # noqa: E731
    bars = [[HOUR, 1.0190, 1.0195, 1.0185, 1.0190, 100.0],     # typical price (1.0195+1.0185+1.0190)/3 = 1.0190
            [2 * HOUR, 1.02, 1.02, 1.02, 1.02, 0.0]]           # untraded: dropped
    r = Q.bar_records(bars, rate, 1.0, usd, 'p')
    assert len(r) == 1
    x = r[0]
    assert x['ts'] == HOUR + HOUR // 2                          # priced at mid-bar
    assert abs(x['discount_bps'] - 1e4 * (1.02 - 1.0190) / 1.02) < 1e-9
    assert x['discount_bps'] > 0                                # below the rate is a positive discount
    assert abs(x['usd'] - 100.0 * 50.0) < 1e-9                  # volume is in native units (the other token)
    assert abs(x['low_discount_bps'] - 1e4 * (1.02 - 1.0185) / 1.02) < 1e-9


def test_hourly_market_volume_weighted():
    recs = [{'hour': 0, 'discount_bps': 10.0, 'usd': 300.0}, {'hour': 0, 'discount_bps': 20.0, 'usd': 100.0}]
    m = Q.hourly_market(recs)
    assert abs(m[0][0] - 12.5) < 1e-12 and m[0][1] == 400.0


def test_episodes_threshold_and_gap():
    m = {0: (5.0, 1.0), HOUR: (12.0, 10.0), 2 * HOUR: (15.0, 10.0), 6 * HOUR: (30.0, 5.0)}
    eps = Q.episodes(m, 10.0, max_gap_hours=2)
    assert len(eps) == 2                                         # 3 silent hours split the run
    assert eps[0]['qualifying_hours'] == 2 and abs(eps[0]['vw_discount_bps'] - 13.5) < 1e-12
    assert abs(eps[0]['net_of_round_trip_bps'] - 3.5) < 1e-12


# ---------------------------------------------------------------------------------------------- swaps from transfers
def _tr(tx, li, token, frm, to, amount, block=100):
    pad = lambda a: '0x' + '0' * 24 + a[2:]  # noqa: E731
    return {'transactionHash': tx, 'logIndex': hex(li), 'address': token, 'blockNumber': hex(block),
            'topics': ['0xddf2', pad(frm), pad(to)], 'data': hex(int(amount * 1e18))}


def test_swaps_from_transfers_sell_buy_and_liquidity():
    K, W, P, U = '0x' + 'aa' * 20, '0x' + 'bb' * 20, '0x' + 'cc' * 20, '0x' + 'dd' * 20
    logs = [_tr('0x1', 1, K, U, P, 10.0), _tr('0x1', 2, W, P, U, 10.24),        # sell 10 kHYPE for 10.24 WHYPE
            _tr('0x2', 1, W, U, P, 5.13), _tr('0x2', 2, K, P, U, 5.0),          # buy 5 kHYPE for 5.13 WHYPE
            _tr('0x3', 1, K, U, P, 1.0), _tr('0x3', 2, W, U, P, 1.0)]           # liquidity add: both in, dropped
    logs.append(dict(logs[0]))                                                   # the same log returned twice
    sw = Q.swaps_from_transfers(logs, [P], K, W)
    assert len(sw) == 2
    s = {x[1]: x for x in sw}
    assert s['0x1'][3] == 's' and abs(s['0x1'][4] - 10.0) < 1e-9 and abs(s['0x1'][5] - 10.24) < 1e-9
    assert s['0x2'][3] == 'b' and abs(s['0x2'][4] - 5.0) < 1e-9 and abs(s['0x2'][5] - 5.13) < 1e-9


def test_swaps_from_transfers_multihop_counts_each_pool():
    K, W, P1, P2, U = '0x' + 'aa' * 20, '0x' + 'bb' * 20, '0x' + '11' * 20, '0x' + '22' * 20, '0x' + 'dd' * 20
    # sell into P1 for WHYPE, which goes straight into P2 to buy kHYPE back (an arbitrage through both pools)
    logs = [_tr('0x9', 1, K, U, P1, 10.0), _tr('0x9', 2, W, P1, P2, 10.2), _tr('0x9', 3, K, P2, U, 10.05)]
    sw = Q.swaps_from_transfers(logs, [P1, P2], K, W)
    by = {x[2]: x for x in sw}
    assert by[P1][3] == 's' and by[P2][3] == 'b'
    assert abs(by[P1][5] - 10.2) < 1e-9 and abs(by[P2][5] - 10.2) < 1e-9


# ---------------------------------------------------------------------------------------------- kHYPE payout check
def _word(v):
    return '%064x' % v


def test_decode_kinetiq_and_check_payouts():
    T = Q.kq_topics()
    user = '0x' + '12' * 20
    pad = lambda a: '0x' + '0' * 24 + a[2:]  # noqa: E731
    e18 = 10 ** 18
    logs = [
        {'block': 10, 'li': 0, 'tx': '0xa', 'topics': [T['queued'], pad('0x' + '99' * 20), pad(user), '0x' + _word(1)],
         'data': '0x' + _word(999 * e18 // 1000) + _word(1025 * e18 // 1000 * 999 // 1000) + _word(e18 // 1000)},
        {'block': 20, 'li': 0, 'tx': '0xb', 'topics': [T['confirmed'], pad(user), '0x' + _word(1)],
         'data': '0x' + _word(1025 * e18 // 1000 * 999 // 1000)},
    ]
    ts = {10: 0, 20: 7 * DAY + 600}
    req, conf, canc, params = Q.decode_kinetiq(logs, lambda b: ts[b])
    assert (user, 1) in req and (user, 1) in conf
    rate = Q.rate_fn([(0, 1.025), (10 * DAY, 1.025)])
    summ, rows = Q.kinetiq_check(req, conf, canc, rate)
    assert summ['confirmed'] == 1 and summ['paid_exact_share'] == 1.0
    r = rows[0]
    assert abs(r['wait_days'] - (7 + 600 / DAY)) < 1e-9
    assert abs(r['fee_bps'] - 10.0) < 1e-6                       # 0.001 of 1.0 kHYPE gross
    assert abs(r['rate_gap_bps']) < 1e-6                         # hype / net kHYPE = the rate


def test_wait_from_events_floor_and_neighbours():
    rows = [{'ts': 5 * DAY + 100, 'wait_days': 7.2, 'khype': 1.0}, {'ts': 5 * DAY + 200, 'wait_days': 30.0, 'khype': 1.0},
            {'ts': 9 * DAY, 'wait_days': 6.5, 'khype': 1.0}]
    f, best = Q.wait_from_events(rows, 7.0, pad_days=0.0)
    assert abs(f(5 * DAY + 5) - 7.2) < 1e-12                    # the fastest claim that day
    assert abs(f(6 * DAY) - 7.2) < 1e-12                        # a day either side
    assert f(9 * DAY) == 7.0                                     # never under the contract's delay
    assert f(20 * DAY) == 7.0                                    # no data: the delay itself


# ---------------------------------------------------------------------------------------------- bid accounting
def _env(sells, wait=7.0, carry=0.5, accrues=False, fee=0.0, market=None):
    return {'sells': sells, 'wait': lambda ts: wait, 'carry': lambda ts: carry, 'accrues': accrues,
            'market': market or (lambda ts: None), 'redemption_fee_bps': fee}


def test_bid_fill_edge_and_capital_lock():
    s = [{'ts': 0, 'usd': 1_000_000.0, 'discount_bps': 20.0, 'fee_bps': 1.0, 'pool': 'p', 'tx': 'a'},
         {'ts': DAY, 'usd': 500_000.0, 'discount_bps': 20.0, 'fee_bps': 1.0, 'pool': 'p', 'tx': 'b'},
         {'ts': 8 * DAY, 'usd': 500_000.0, 'discount_bps': 20.0, 'fee_bps': 1.0, 'pool': 'p', 'tx': 'c'}]
    fills, st = QB.simulate_book({'a': _env(s)}, 1_000_000.0, 0.0, gas_usd=1.0, min_fill_usd=1000.0)
    # edge = 20 - 2 x 1 (two pool fees) - 7 x 0.5 (the queue's carry) = 14.5bp
    assert abs(fills[0]['edge_bps'] - 14.5) < 1e-12
    assert abs(fills[0]['value_usd'] - (1_000_000 * 14.5 / 1e4 - 1.0)) < 1e-9
    assert len(fills) == 2                                       # day 1: all capital locked until day 7
    assert fills[1]['ts'] == 8 * DAY
    assert st['missed_capital_usd'] == 500_000.0


def test_bid_market_cap_redemption_fee_and_accrual():
    s = [{'ts': 0, 'usd': 100_000.0, 'discount_bps': 40.0, 'fee_bps': 1.0, 'pool': 'p', 'tx': 'a'}]
    f1, _ = QB.simulate_book({'a': _env(s, market=lambda ts: 12.0)}, 1e6, 0.0, gas_usd=0.0, min_fill_usd=0.0)
    assert abs(f1[0]['edge_bps'] - (min(40 - 2, 12 - 1) - 3.5)) < 1e-12    # capped at the venue median less one fee
    f2, _ = QB.simulate_book({'a': _env(s, fee=10.0)}, 1e6, 0.0, gas_usd=0.0, min_fill_usd=0.0)
    assert abs(f2[0]['edge_bps'] - (38 - 3.5 - 10)) < 1e-12
    f3, _ = QB.simulate_book({'a': _env(s, accrues=True)}, 1e6, 0.0, gas_usd=0.0, min_fill_usd=0.0)
    assert abs(f3[0]['edge_bps'] - 38.0) < 1e-12                           # a queue that keeps earning costs no carry


def test_make_env_sell_share_and_positive_only():
    recs = [{'ts': 0, 'hour': 0, 'pool': 'p', 'discount_bps': 10.0, 'usd': 1000.0, 'fee_bps': 1.0},
            {'ts': HOUR, 'hour': HOUR, 'pool': 'p', 'discount_bps': -3.0, 'usd': 1000.0, 'fee_bps': 1.0}]
    e = Q.make_env(recs, lambda ts: 1.0, lambda ts: 0.0, sell_share=0.25)
    assert len(e['sells']) == 1 and e['sells'][0]['usd'] == 250.0


def test_late_entry_needs_the_edge_seen_earlier():
    recs = [{'ts': 10 * HOUR, 'hour': 10 * HOUR, 'pool': 'p', 'discount_bps': 30.0, 'usd': 1e6, 'fee_bps': 1.0}]
    env = Q.make_env(recs, lambda ts: 1.0, lambda ts: 0.0)
    f0, _ = QB.simulate_book({'a': env}, 1e7, 0.0, gas_usd=0.0, min_fill_usd=0.0)
    f1, _ = QB.simulate_book({'a': env}, 1e7, 0.0, gas_usd=0.0, min_fill_usd=0.0, delay_s=DAY)
    assert len(f0) == 1 and len(f1) == 0                          # nothing traded a day earlier: a late bidder misses it


# ---------------------------------------------------------------------------------------------- carry, part (b)
def test_carry_with_staked_collateral_adds_the_yield():
    import term_carry as TC
    days = list(range(1000, 1100))
    f = {d: 0.10 / 365 for d in days}
    p = {d: 0.0 for d in days}
    stake = {d: 0.02 / 365 for d in days}
    ex0, _, st0 = TC.simulate_carry(days, {'hl': f}, {'hl': p}, {'kind': 'always'}, 0.0, {'hl': 0.0}, 1.0, lambda d: 0.038)
    ex1, _, st1 = TC.simulate_carry(days, {'hl': f}, {'hl': p}, {'kind': 'always'}, 0.0, {'hl': 0.0}, 1.0, lambda d: 0.038,
                                    extra=stake)
    assert abs(sum(ex1) - sum(ex0) - 0.02 / 365 * len(days)) < 1e-12
    assert abs(sum(ex0) / len(days) * 365 - (0.10 - 0.038)) < 1e-9
    # cash margin: capital 4/3 per unit of notional dilutes both
    ex2, _, _ = TC.simulate_carry(days, {'hl': f}, {'hl': p}, {'kind': 'always'}, 0.0, {'hl': 0.0}, 4 / 3, lambda d: 0.038,
                                  extra=stake)
    assert abs(sum(ex2) / len(days) * 365 - ((0.12) * 0.75 - 0.038)) < 1e-9


def test_basis_accrual_and_daily_rate_accrual():
    b = Q.basis_accrual({1: 10.0, 2: 25.0, 4: 5.0}, [1, 2, 3, 4])
    assert abs(b[2] - (-15e-4)) < 1e-15                          # the discount widened: the LST leg lost 15bp
    assert abs(b[3]) < 1e-15                                     # an unmarked day carries the last mark
    assert abs(b[4] - 20e-4) < 1e-15
    acc = Q.daily_rate_accrual([(0, 1.0), (10 * DAY, 1.0 * math.exp(0.001))], 0, 10)
    assert abs(sum(acc.values()) - 0.001) < 1e-12


def test_daily_apy_accrual_staleness():
    rows = [{'ts': 0, 'apyBase': 5.0}, {'ts': 20 * DAY, 'apyBase': 7.0}]
    a = Q.daily_apy_accrual(rows, 0, 25)
    assert abs(a[0] - math.log(1.05) / 365) < 1e-15
    assert 8 not in a                                            # more than a week after the last reading: unknown
    assert abs(a[21] - math.log(1.07) / 365) < 1e-15


# ---------------------------------------------------------------------------------------------- Solana stake pool
def test_parse_spl_stake_pool_fees():
    buf = bytearray()
    buf += bytes([1]) + bytes(32 * 3) + bytes([255]) + bytes(32 * 5)
    buf += struct.pack('<QQQ', 1_305_717_000, 1_000_000_000, 1054)
    buf += bytes(48)                                            # lockup
    buf += struct.pack('<QQ', 100, 4)                           # epoch fee 4%
    buf += bytes([0])                                           # next epoch fee: none
    buf += bytes([0]) + bytes([0])                              # preferred validators: none
    buf += struct.pack('<QQ', 1, 0)                             # stake deposit fee 0
    buf += struct.pack('<QQ', 1000, 1)                          # stake withdrawal fee 0.1%
    buf += bytes([0]) + bytes([0])                              # next stake withdrawal fee none; referral
    buf += bytes([0])                                           # sol deposit authority none
    buf += struct.pack('<QQ', 1, 0) + bytes([0])                # sol deposit fee, referral
    buf += bytes([0])                                           # sol withdraw authority none
    buf += struct.pack('<QQ', 1000, 1)                          # sol withdrawal fee 0.1%
    p = Q.parse_spl_stake_pool(bytes(buf))
    assert abs(p['rate'] - 1.305717) < 1e-12 and p['epoch'] == 1054
    assert abs(p['stake_withdrawal_fee_bps'] - 10.0) < 1e-9 and abs(p['sol_withdrawal_fee_bps'] - 10.0) < 1e-9
    assert abs(p['epoch_fee'] - 0.04) < 1e-12


def test_other_side_and_fee_from_name():
    pool = {'relationships': {'base_token': {'data': {'id': 'hyperevm_0xAA'}}, 'quote_token': {'data': {'id': 'hyperevm_0xbb'}}}}
    assert Q.other_side(pool, 'hyperevm', '0xaa') == ('base', '0xbb')
    assert Q.other_side(pool, 'hyperevm', '0xbb') == ('quote', '0xAA')
    assert Q.fee_from_name('kHYPE / WHYPE 0.008%') == 0.008 and Q.fee_from_name('sAVAX / WAVAX') is None


# ---------------------------------------------------------------------------------------------- verdict helpers
def test_trailing_apr_fn_and_window_days():
    s = [(0, 1.0), (30 * DAY, 1.0 * (1.02 ** (30 / 365)))]
    f = Q.trailing_apr_fn(s, window_days=30.0)
    assert abs(f(30 * DAY) - 0.02) < 1e-9
    assert f(-DAY) == 0.02 or f(-DAY) is not None              # before history: the fallback
    recs = [{'ts': 10 * DAY + 5}, {'ts': 20 * DAY + 5}]
    d0, n = Q.window_days(recs)
    assert d0 == 11 and n == 9                                   # partial first and last days dropped


def test_depth_below_round_trip_reads_the_priced_edges():
    sells = [{'ts': 0, 'usd': 10_000.0, 'discount_bps': 20.0, 'fee_bps': 1.0, 'pool': 'p', 'tx': 'a'},
             {'ts': DAY, 'usd': 5_000.0, 'discount_bps': 3.0, 'fee_bps': 1.0, 'pool': 'p', 'tx': 'b'}]
    env = {'sells': sells, 'wait': lambda ts: 1.0, 'carry': lambda ts: 1.0, 'accrues': False, 'market': lambda ts: None,
           'redemption_fee_bps': 0.0}
    QB.simulate_book({'a': env}, 1e9, 0.0, gas_usd=0.0, min_fill_usd=0.0)
    d = Q.depth_below_round_trip(env, 0, 2)
    assert d['days_with_any'] == 1 and d['usd_total'] == 10_000.0     # 3bp - 2 fees - 1bp carry is not an edge
    assert abs(d['edge_usd_total'] - 10_000.0 * 17.0 / 1e4) < 1e-9


def test_verdict_and_carry_pass_rules():
    good = {'at_quoted_size': {'out_of_sample_usd_per_year': 60_000.0, 'oos_ci95_usd_per_year': [5_000.0, 90_000.0],
                               'trailing_90d_usd_per_year': 20_000.0}, 'late_entry': {'1h': {'kept_share': 0.9}}}
    assert Q.verdict_for(good) == 'proposed'
    late = dict(good, late_entry={'1h': {'kept_share': 0.3}})
    assert Q.verdict_for(late).startswith('watch')               # an edge an hour late cannot keep is a race
    bars = dict(good, sell_share_0_25={'out_of_sample_usd_per_year': 20_000.0})
    assert Q.verdict_for(bars).startswith('watch (bar-only')     # unmeasured sale side must survive the sensitivity
    small = {'at_quoted_size': {'out_of_sample_usd_per_year': 2_000.0, 'oos_ci95_usd_per_year': [500.0, 4_000.0]}}
    assert Q.verdict_for(small) == 'no-go'
    assert Q.verdict_for({'at_quoted_size': {'out_of_sample_usd_per_year': 0.0, 'oos_ci95_usd_per_year': [0.0, 0.0]}}) == 'no-go'
    v = {'oos_ann_excess': 0.045, 'oos_t': 4.5, 'oos_bootstrap_mean_ci': [0.02, 0.06], 'last_90d': {'chosen': 0.05}}
    assert Q.carry_passes(v, {'oos_ann_excess': 0.03})
    assert not Q.carry_passes(v, {'oos_ann_excess': 0.05})       # must beat the plain-spot version of the same trade
    assert not Q.carry_passes(dict(v, oos_bootstrap_mean_ci=[-0.004, 0.05]))
