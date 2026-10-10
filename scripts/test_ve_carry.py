"""Tests for ve_carry.py: ABI decoding, epoch bucketing, vote allocation with own dilution, hedge accounting, exit math.

    cd /Users/iv/dev/llm-quant && uv run --with pytest --with pycryptodome python -m pytest scripts/test_ve_carry.py -q
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ve_carry as V  # noqa: E402


def keccak_hex(s):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256)
    k.update(s.encode())
    return k.hexdigest()


# ------------------------------------------------------------------------------------------------ ABI
def test_selectors_and_topics_are_keccak():
    for sig, sel in V.SEL.items():
        assert sel == '0x' + keccak_hex(sig)[:8], sig
    assert V.TOPIC['NotifyReward'] == '0x' + keccak_hex('NotifyReward(address,address,uint256,uint256)')
    assert V.TOPIC['Transfer'] == '0x' + keccak_hex('Transfer(address,address,uint256)')
    assert V.TOPIC['OrderFulfilled'] == '0x' + keccak_hex(
        'OrderFulfilled(bytes32,address,address,address,(uint8,address,uint256,uint256)[],(uint8,address,uint256,uint256,address)[])')


def test_cdata_static_args():
    d = V.cdata('tokenRewardsPerEpoch(address,uint256)', '0x940181a94A35A4569E4529A3CDfB74e38FD98631', 1693440000)
    assert d.startswith('0x92777b29')
    assert d[10:74] == '000000000000000000000000940181a94a35a4569e4529a3cdfb74e38fd98631'
    assert int(d[74:], 16) == 1693440000


def _enc_result(items):
    """Encode Result[] (bool success, bytes returnData) the way Multicall3 returns it."""
    elems = []
    for ok, data in items:
        b = bytes.fromhex(data[2:]) if data else b''
        pad = (32 - len(b) % 32) % 32
        elems.append(V.enc_uint(1 if ok else 0) + V.enc_uint(0x40) + V.enc_uint(len(b)) + (b + b'\0' * pad).hex())
    offs, pos = [], 32 * len(elems)
    for e in elems:
        offs.append(V.enc_uint(pos))
        pos += len(e) // 2
    return '0x' + V.enc_uint(0x20) + V.enc_uint(len(elems)) + ''.join(offs) + ''.join(elems)


def test_aggregate3_roundtrip():
    calls = [('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5', V.cdata('length()')),
             ('0xeBf418Fe2512e7E6bd9b87a8F0f294aCDC67e6B4', V.cdata('totalSupplyAt(uint256)', 1791417599))]
    enc = V.enc_aggregate3(calls)
    w = V.words(enc[10:])
    assert enc.startswith('0x82ad56cb') and w[0] == 0x20 and w[1] == 2
    # first element: offset 0x40 from the start of the array content (two offset words)
    assert w[2] == 0x40
    # element 0: target, allowFailure, bytes offset 0x60, length 4 (selector only)
    assert w[4] == int('16613524e02ad97eDfeF371bC883F2F5d6C480A5', 16) and w[5] == 1 and w[6] == 0x60 and w[7] == 4
    resp = _enc_result([(True, '0x' + V.enc_uint(1990)), (False, '0x'), (True, '0x' + V.enc_uint(7) + V.enc_uint(9))])
    out = V.dec_aggregate3(resp)
    assert V.dec_uint(out[0]) == 1990 and out[1] is None and V.words(out[2]) == [7, 9]


def test_decoders():
    assert V.dec_addr('0x' + V.enc_addr('0xABCDEF0000000000000000000000000000000001')) == '0xabcdef0000000000000000000000000000000001'
    s = '0x' + V.enc_uint(0x20) + V.enc_uint(4) + b'AERO'.hex().ljust(64, '0')
    assert V.dec_string(s) == 'AERO'
    assert V.dec_string('0x' + b'MKR'.hex().ljust(64, '0')) == 'MKR'          # bytes32 symbol
    neg = (1 << 256) - 5
    assert V.dec_locked('0x' + V.enc_uint(neg) + V.enc_uint(0) + V.enc_uint(1)) == (-5, 0, True)
    assert V.dec_locked('0x' + V.enc_uint(10 ** 18) + V.enc_uint(1900000000) + V.enc_uint(0)) == (10 ** 18, 1900000000, False)


def test_dec_order_fulfilled_listing():
    ve = '0xebf418fe2512e7e6bd9b87a8f0f294acdc67e6b4'
    seller = '0x' + '11' * 20
    buyer = '0x' + '22' * 20
    fee = '0x' + '33' * 20
    # offer: one ERC721 (type 2) = ve #42; consideration: 0.9 ETH to seller, 0.1 ETH to fee recipient
    offer = [(2, ve, 42, 1)]
    cons = [(0, '0x' + '00' * 20, 0, 9 * 10 ** 17, seller), (0, '0x' + '00' * 20, 0, 10 ** 17, fee)]
    head = V.enc_uint(0xAA) + V.enc_addr(buyer) + V.enc_uint(0x80) + V.enc_uint(0x80 + 32 + 128 * len(offer))
    o = V.enc_uint(len(offer)) + ''.join(V.enc_uint(t) + V.enc_addr(a) + V.enc_uint(i) + V.enc_uint(m) for t, a, i, m in offer)
    c = V.enc_uint(len(cons)) + ''.join(V.enc_uint(t) + V.enc_addr(a) + V.enc_uint(i) + V.enc_uint(m) + V.enc_addr(r) for t, a, i, m, r in cons)
    topics = [V.TOPIC['OrderFulfilled'], '0x' + V.enc_addr(seller), '0x' + V.enc_addr('0x' + '00' * 20)]
    off, rec, of, co = V.dec_order_fulfilled(topics, '0x' + head + o + c)
    assert off == seller and rec == buyer
    assert of == [(2, ve, 42, 1)]
    assert co[0] == (0, '0x' + '00' * 20, 0, 9 * 10 ** 17, seller) and co[1][4] == fee


def test_dec_lp_epochs_roundtrip():
    lp = '0x' + 'ab' * 20
    t1, t2 = '0x' + '01' * 20, '0x' + '02' * 20
    epochs = [(1791417600 - 604800, lp, 5 * 10 ** 24, 3, [(t1, 7)], [(t1, 11), (t2, 13)])]

    def enc_struct(ts, l, v, em, br, fe):
        static = V.enc_uint(ts) + V.enc_addr(l) + V.enc_uint(v) + V.enc_uint(em)
        a1 = V.enc_uint(len(br)) + ''.join(V.enc_addr(a) + V.enc_uint(m) for a, m in br)
        a2 = V.enc_uint(len(fe)) + ''.join(V.enc_addr(a) + V.enc_uint(m) for a, m in fe)
        o1 = 6 * 32
        o2 = o1 + len(a1) // 2
        return static + V.enc_uint(o1) + V.enc_uint(o2) + a1 + a2
    body = [enc_struct(*e) for e in epochs]
    offs, pos = [], 32 * len(body)
    for b in body:
        offs.append(V.enc_uint(pos))
        pos += len(b) // 2
    h = '0x' + V.enc_uint(0x20) + V.enc_uint(len(body)) + ''.join(offs) + ''.join(body)
    d = V.dec_lp_epochs(h)
    assert d[0]['ts'] == epochs[0][0] and d[0]['lp'] == lp and d[0]['votes'] == 5 * 10 ** 24
    assert d[0]['bribes'] == [(t1, 7)] and d[0]['fees'] == [(t1, 11), (t2, 13)]


# ------------------------------------------------------------------------------------------------ epochs
def test_epoch_bucketing():
    thu = 1791417600                       # 2026-10-08 00:00 UTC, a Thursday
    assert V.epoch_start(thu) == thu and V.epoch_start(thu + 604799) == thu and V.epoch_start(thu - 1) == thu - 604800
    assert V.ymd(thu) == '2026-10-08'
    eps = V.epochs_between(thu - 3 * 604800 + 5, thu)
    assert eps == [thu - 3 * 604800, thu - 2 * 604800, thu - 604800, thu]
    # a settlement exactly at the flip belongs to the epoch it ends; one second later to the next
    vals, cnt = V.bucket_by_epoch([(thu, 1.0), (thu + 1, 2.0), (thu - 604800 + 1, 4.0)], thu - 604800, 2)
    assert vals == [5.0, 2.0] and cnt == [2, 1]
    assert V.block_at('base', 1686789347 + 200) == 100
    assert V.MERGER_TS == 1792627200 and V.ymd(V.MERGER_TS) == '2026-10-22'


def test_funding_epochs_annualises():
    e0 = 1791417600 - 2 * 604800
    rows = [(e0 + 4 * 3600 * k, -0.0001, 0.9) for k in range(1, 43)]   # 42 four-hour settlements in epoch 0
    usd, cnt, ann = V.funding_epochs(rows, [e0, e0 + 604800])
    assert cnt[0] == 42 and cnt[1] == 0
    assert usd[0] == pytest.approx(-0.0001 * 0.9 * 42)
    assert ann[0] == pytest.approx(-0.0001 * 42 * 365 / 7)


# ------------------------------------------------------------------------------------------------ voting
def test_avg_vote_with_own_dilution_equals_pro_rata_allocation():
    R = {1: 100.0, 2: 300.0}
    Vv = {1: 1000.0, 2: 2000.0}
    M = 600.0
    pro = {k: M * Vv[k] / 3000.0 for k in Vv}
    assert V.realized_reward(pro, R, Vv) == pytest.approx(V.avg_vote_reward(400.0, 3000.0, M))
    assert V.avg_vote_reward(400.0, 3000.0, M) == pytest.approx(400.0 * 600 / 3600)


def test_water_fill_kkt_and_budget():
    pools = {'a': (1000.0, 1e5), 'b': (500.0, 1e5), 'c': (10.0, 1e6), 'd': (0.0, 10.0)}
    M = 5e4
    al = V.water_fill(pools, M)
    assert sum(al.values()) == pytest.approx(M, rel=1e-9)
    assert 'd' not in al and 'c' not in al          # c's marginal at zero (1e-5) is below the funded pools'
    marg = {k: pools[k][0] * pools[k][1] / (pools[k][1] + v) ** 2 for k, v in al.items()}
    vals = list(marg.values())
    assert max(vals) == pytest.approx(min(vals), rel=1e-6)
    # it beats an even split and the pro-rata split
    R = {k: r for k, (r, _) in pools.items()}
    Vv = {k: v for k, (_, v) in pools.items()}
    best = V.realized_reward(al, R, Vv)
    assert best >= V.realized_reward({'a': M / 2, 'b': M / 2}, R, Vv) - 1e-9
    assert best >= V.avg_vote_reward(sum(R.values()), sum(Vv.values()), M)


def test_water_fill_symmetric_and_cap():
    pools = {k: (100.0, 1000.0) for k in range(40)}
    al = V.water_fill(pools, 4000.0, k_max=30)
    assert len(al) == 30
    assert sum(al.values()) == pytest.approx(4000.0)
    assert max(al.values()) == pytest.approx(min(al.values()))


def test_water_fill_unvoted_pool_gets_finite_votes():
    al = V.water_fill({'x': (100.0, 0.0), 'y': (100.0, 1e6)}, 1e4, vfloor=1.0)
    assert al['x'] > 0 and sum(al.values()) == pytest.approx(1e4)
    # once votes are added the unvoted pool pays its whole reward to us
    assert V.realized_reward({'x': 5.0}, {'x': 100.0}, {'x': 0.0}) == pytest.approx(100.0)


def test_own_dilution_shrinks_premium_with_size():
    pools = {'rich': (1000.0, 1e5), 'poor': (1000.0, 1e7)}
    R = {k: r for k, (r, _) in pools.items()}
    Vv = {k: v for k, (_, v) in pools.items()}
    per_vote = []
    for M in (1e3, 1e5, 1e7):
        al = V.water_fill(pools, M)
        per_vote.append(V.realized_reward(al, R, Vv) / M)
    assert per_vote[0] > per_vote[1] > per_vote[2]


# ------------------------------------------------------------------------------------------------ hedge and exit
def test_epoch_carry_accounting():
    carry, cap, ret = V.epoch_carry(rpv_usd=0.004, rebase_tok=0.0005, p_start=1.0, p_end=1.0, funding_usd=-0.001,
                                    basis_start=0.0, basis_end=0.0, m=1 / 3, taker=0.0)
    assert carry == pytest.approx(0.004 + 0.0005 - 0.001)
    assert cap == pytest.approx(4 / 3)
    assert ret == pytest.approx(0.0035 / (4 / 3))
    # a price move with no basis change does not enter the carry (the short offsets the lock) ...
    c2, _, _ = V.epoch_carry(0.004, 0.0, 1.0, 2.0, 0.0, 0.0, 0.0, 1 / 3, 0.0)
    assert c2 == pytest.approx(0.004)
    # ... but the perp richening against the index costs the short
    c3, _, _ = V.epoch_carry(0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.01, 1 / 3, 0.0)
    assert c3 == pytest.approx(-0.01)
    # positive funding is received by the short
    c4, _, _ = V.epoch_carry(0.0, 0.0, 1.0, 1.0, 0.002, 0.0, 0.0, 0.0, 0.0)
    assert c4 == pytest.approx(0.002)


def test_switch_series_charges_switches():
    xs = [0.01, 0.01, 0.01, 0.01]
    ok = [True, True, False, True]
    out = V.switch_series([1, 2, 3, 4], xs, None, ok, entry_cost=0.003, exit_disc=0.1, m=0.0)
    assert out[0] == pytest.approx(0.01 - 0.003)
    assert out[1] == pytest.approx(0.01)
    assert out[2] == pytest.approx(0.0 - (0.1 + V.TAKER))
    assert out[3] == pytest.approx(0.01 - 0.003)


def test_exit_math():
    weekly = [0.001] * 52                       # 5.2% excess a year on capital
    assert V.breakeven_discount(weekly, 1 / 3) == pytest.approx(0.052 * 4 / 3)
    assert V.annuity_value(0.10, 0.05) == pytest.approx(2.0)
    assert V.sale_discount(800.0, 1000.0, 1.0) == pytest.approx(0.2)
    assert V.sale_discount(1.0, 0.0, 1.0) is None


def test_value_rows_haircuts():
    class P:
        def tier(self, token, ts, majors):
            return {'maj': ('major', 2.0), 'mid': ('priced', 1.0), 'low': ('lowconf', 1.0)}.get(token, ('unpriced', 0.0))
    rows = [[0, 'fees', 'maj', 100, str(10 ** 18)], [0, 'bribe', 'mid', 100, str(10 ** 18)],
            [0, 'bribe', 'low', 100, str(10 ** 18)], [0, 'bribe', 'zzz', 100, str(10 ** 18)]]
    toks = {t: {'decimals': 18} for t in ('maj', 'mid', 'low', 'zzz')}
    out, tiers = V.value_rows(rows, toks, P(), {'maj': 'X'}, lambda e: e)
    d = out[(0, 100)]
    assert d['fees'] == pytest.approx(2.0 * (1 - V.HAIRCUT['major']))
    assert d['bribe'] == pytest.approx(1.0 * 0.8 + 1.0 * 0.5)
    assert d['fees_major'] == pytest.approx(d['fees']) and d['bribe_major'] == 0.0
    assert tiers['unpriced'] == 0.0


def test_book_depth_bands():
    d = V.book_depth([(0.99, 100.0), (0.98, 100.0), (0.95, 1000.0)], [(1.01, 50.0), (1.03, 50.0)], 1.0)
    assert d['bid_1pct'] == pytest.approx(99.0)
    assert d['bid_2pct'] == pytest.approx(99.0 + 98.0)
    assert d['ask_1pct'] == pytest.approx(50.5)


def test_carry_series_venue_switch_and_benchmark():
    e0 = 1791417600 - 2 * 604800
    e1 = e0 + 604800
    table = [{'epoch': e, 'p_start': 1.0, 'p_end': 1.0, 'rebase_per_vote': 0.0} for e in (e0, e1)]
    att = {5000000: {e0: {'avg': 0.002}, e1: {'avg': 0.002}}}
    res = {'table': table, 'att': att}
    hedge = [{'epoch': e0, 'venue': 'binance', 'funding_usd': -0.001, 'basis0': 0.0, 'basis1': 0.0,
              'best_venue': 'bybit', 'best_funding_usd': 0.0005, 'best_switch': False},
             {'epoch': e1, 'venue': 'binance', 'funding_usd': -0.001, 'basis0': 0.0, 'basis1': 0.0,
              'best_venue': 'hl', 'best_funding_usd': 0.0005, 'best_switch': True}]
    eps, xs, det = V.carry_series(res, hedge, 'avg', 5e6, m=0.0)
    wk = V.SSR * 7 / 365
    assert eps == [e0, e1]
    assert xs[0] == pytest.approx(0.002 - 0.001 - wk)
    eps, xs, det = V.carry_series(res, hedge, 'avg', 5e6, m=0.0, venue_rule='best')
    assert xs[0] == pytest.approx(0.002 + 0.0005 - wk)
    assert xs[1] == pytest.approx(0.002 + 0.0005 - 2 * V.TAKER - wk)       # switching venue costs a round trip
    eps, xs, det = V.carry_series(res, hedge, 'avg', 5e6, m=0.0, rpv_map={e0: 0.0, e1: 0.0})
    assert xs[0] == pytest.approx(-0.001 - wk)
    eps, xs, det = V.carry_series(res, hedge, 'avg', 5e6, m=0.0, bench='paid')
    assert xs[0] == pytest.approx(0.002 - 0.001 - V.SAVINGS_PAID[2026] * 7 / 365)


def test_sales_summary_quantiles_and_weights():
    rows = [{'discount': d, 'value_usd': v, 'usd': v * (1 - d), 'date': '2025-01-0%d' % (k + 1), 'ts': 0,
             'permanent': True, 'years_left': None} for k, (d, v) in enumerate([(0.1, 1000.0), (0.3, 3000.0), (0.2, 1000.0), (2.0, 10.0)])]
    s = V.sales_summary(rows)
    assert s['excluded_outliers'] == 1
    assert s['all']['n'] == 3 and s['all']['median_discount'] == pytest.approx(0.2)
    assert s['all']['value_weighted_discount'] == pytest.approx(1 - (900 + 2100 + 800) / 5000)
