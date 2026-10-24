"""Tests for stability_pool: the counterfactual redemption queue and the loop's daily accounting."""
import stability_pool as S


def _trv(ops, red):
    return {'ops': ops, 'red': red}


def test_hits_sit_in_front_of_higher_rates_only():
    ops = [{'tx': 'a', 'op': 6, 'rate': 0.005, 'debt_chg': -100.0, 'ts': 10},
           {'tx': 'a', 'op': 6, 'rate': 0.02, 'debt_chg': -300.0, 'ts': 10},
           {'tx': 'b', 'op': 6, 'rate': 0.005, 'debt_chg': -50.0, 'ts': 20},
           {'tx': 'c', 'op': 2, 'rate': 0.03, 'debt_chg': -999.0, 'ts': 30}]       # not a redemption
    red = [{'tx': 'a', 'coll_sent': 0.99, 'coll_fee': 0.01, 'price': 2000.0, 'redemption_price': 2000.0}]
    h = S._redemption_hits(_trv(ops, red), 0.01)
    assert len(h) == 1 and h[0]['amount'] == 300.0          # only the 2% trove would have been behind us
    assert abs(h[0]['fee'] - 0.01) < 1e-12
    # at exactly 0.5%, ties go behind the troves already there by default ...
    assert [x['amount'] for x in S._redemption_hits(_trv(ops, red), 0.005)] == [300.0]
    # ... and in front of them only when asked
    assert [x['amount'] for x in S._redemption_hits(_trv(ops, red), 0.005, ties_first=True)] == [400.0, 50.0]


def test_loop_accounting_without_redemptions():
    daily = [{'day': '2026-01-0%d' % i, 'deposits': 9e6, 'yield': 1000.0, 'gain': 0.0, 'burn': 0.0,
              'r_yield': 1.0, 'r_liq': 0.0} for i in range(1, 4)]
    rows = S.simulate_loop('WETH', daily, _trv([], []), {}, 0.01, 1e6)
    flow = 1000.0 + 0.75 * 0.01 * 1e6 / 365
    assert abs(rows[0]['sp'] - 1e6 * flow / 10e6) < 1e-9
    assert abs(rows[0]['interest'] - 1e6 * 0.01 / 365) < 1e-9
    assert all(r['red'] == 0 for r in rows)


def test_redemption_cycle_pays_fee_minus_discount_and_costs():
    ts = 1767225600 + 3600                                  # 2026-01-01 01:00 UTC
    daily = [{'day': '2026-01-01', 'deposits': 9e6, 'yield': 0.0, 'gain': 0.0, 'burn': 0.0, 'r_yield': 0.0,
              'r_liq': 0.0},
             {'day': '2026-01-02', 'deposits': 9e6, 'yield': 0.0, 'gain': 0.0, 'burn': 0.0, 'r_yield': 0.0,
              'r_liq': 0.0}]
    ops = [{'tx': 'a', 'op': 6, 'rate': 0.05, 'debt_chg': -1e5, 'ts': ts}]
    red = [{'tx': 'a', 'coll_sent': 0.99, 'coll_fee': 0.01, 'price': 2000.0, 'redemption_price': 2000.0}]
    chain = {'2026-01-02': {'sell1m': 0.996}}
    rows = S.simulate_loop('WETH', daily, _trv(ops, red), chain, 0.005, 1e6)
    want = 1e5 * (0.996 - 0.99 - S.SPOT_COST - S.AVG_RATE_CAP * S.UPFRONT_DAYS / 365)
    assert rows[0]['absorbed'] == 1e5
    assert abs(rows[0]['red'] - want) < 1e-6
    assert rows[0]['D'] == 1e6                              # rebuilt to size at the day's close
