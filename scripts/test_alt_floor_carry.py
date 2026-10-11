"""Tests for alt_floor_carry: floor detection per settlement across interval changes, the phantom-settlement cut, the
P&L arithmetic on a synthetic coin, the spike screen, delisting exits, and that a rebalance sees only the past."""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import alt_floor_carry as A   # noqa: E402
import collateral_watch as CW  # noqa: E402

H, D = A.HOUR_MS, A.DAY_MS
TABLE = [[0, 2.0, 1]]          # a flat 2bp half-spread for both legs


def stamps(start_ms, hours, n):
    return [start_ms + (k + 1) * hours * H for k in range(n)]


def make_coin(sym='AAA', first=0, last=120, price=100.0, rate=None, hours=8, c=0.5, im=0.1, spot_vol=5e7,
              perp_vol=1e8, spot_last=None):
    """A coin that trades every day in [first, last] at a flat price, paying `rate` per settlement (default: the floor
    for its interval) on an `hours` schedule; its spot may stop trading after `spot_last`."""
    rate = A.floor_rate(hours) if rate is None else rate
    spot_last = last if spot_last is None else spot_last
    days = range(first, last + 1)
    fd = {d: [(t, rate, price, hours) for t in stamps(d * D, hours, 24 // hours)] for d in days}
    return {'sym': sym, 'base': sym, 'status': 'TRADING', 'source': 'test', 'spot': sym + 'USDT', 'spot_base': sym,
            'spot_status': 'TRADING', 'mult': 1.0, 'identity_median': 1.0,
            'pc': {d: price for d in days}, 'pv': {d: perp_vol for d in days},
            'sc': {d: price for d in days if d <= spot_last}, 'sv': {d: spot_vol for d in days if d <= spot_last},
            'fd': fd, 'first_p': first, 'last_p': last, 'first_s': first, 'last_s': spot_last,
            'delist_p': None, 'delist_s': spot_last if spot_last < last - 1 else None,
            'c': c, 'im': im, 'max_lev': 20.0, 'tick_p': None, 'tick_s': None}


def variant(**kw):
    v = {'rebalance_days': 7, 'floor_share_min': 0.5, 'spike_8h': None, 'spot_vol_min_usd': 2e6, 'n_names': 1}
    v.update(kw)
    v['name'] = A.variant_name(v)
    return v


def run(coins, days, v, bench=0.0, costs=None, record=True):
    feats = {d: {s: A.features(c, d) for s, c in coins.items()} for d in days[::v['rebalance_days']]}
    members = {s: c['spot_base'] for s, c in coins.items()}
    K_of = lambda c: A.capital_per_short(c['c'], c['im'])   # noqa: E731
    return A.simulate(coins, feats, days, v, members, K_of, lambda d: bench, costs or A.Costs(TABLE, TABLE),
                      record=record)


# ------------------------------------------------------------------------------------------- floor detection

def test_settlement_hours_follow_interval_changes():
    t8 = stamps(0, 8, 3)                       # 08:00, 16:00, 24:00 of day 0
    t4 = stamps(t8[-1], 4, 6)                  # then every 4 h for a day
    t1 = stamps(t4[-1], 1, 24)                 # then hourly
    halt = [t1[-1] + 30 * H]                   # a 30 h halt, then back to 8 h
    t8b = stamps(halt[0], 8, 3)
    hrs = A.settlement_hours(t8 + t4 + t1 + halt + t8b)
    assert hrs[:3] == [8, 8, 8]
    assert hrs[3:9] == [4] * 6
    assert hrs[9:33] == [1] * 24
    assert hrs[33] == 8                        # the halt is not an interval: the next gap decides
    assert hrs[34:] == [8, 8, 8]


def test_two_hour_interval_is_an_interval_and_odd_gaps_are_not():
    assert A.settlement_hours(stamps(0, 2, 4)) == [2, 2, 2, 2]     # Binance runs some symbols on 2 h
    assert A.is_floor(0.000025, 2)
    ts = stamps(0, 1, 6)
    ts = ts[:2] + ts[4:]                       # two hourly prints missing -> a 3 h gap, not an interval
    assert A.settlement_hours(ts) == [1, 1, 1, 1]


def test_floor_detection_per_settlement_with_interval_changes():
    t = stamps(0, 8, 3) + stamps(3 * 8 * H, 4, 6) + stamps(3 * 8 * H + 6 * 4 * H, 1, 24)
    hrs = A.settlement_hours(t)
    rates = [0.0001] * 3 + [0.00005] * 6 + [0.0000125] * 24
    assert all(A.is_floor(r, h) for r, h in zip(rates, hrs))
    assert not A.is_floor(0.0001, 4)           # an 8 h floor printed on a 4 h interval is twice the floor
    assert not A.is_floor(0.00005, 8)
    assert not A.is_floor(0.00010001, 8)       # one tick off
    assert A.rate_8h(-0.0001, 1) == pytest.approx(-0.0008)


def test_phantom_settlements_after_delisting_are_dropped():
    traded = {0, 1, 2}
    ev = [(t, 0.0001, 1.0) for t in stamps(0, 8, 3 * 6)]          # six days of 8 h prints, three traded
    kept, dropped = A.clean_funding(ev, traded)
    assert len(kept) == 9 and dropped == 9
    assert {k[4] for k in kept} == traded
    kept2, dropped2 = A.clean_funding(ev, traded, delivery_ms=1 * D + 9 * H)   # delisted at day 1 09:00
    assert [A.day_of(k[0]) for k in kept2] == [0, 0, 0, 1]          # day 1's 08:00 print survives, 16:00 does not
    assert dropped2 == 14


def test_kline_days_drop_untraded_bars():
    rows = [[0, '1', '1', '1', '1.0', '10', D - 1, '10.0', 5], [D, '1', '1', '1', '1.0', '0', 2 * D - 1, '0', 0]]
    assert A.kline_days(rows) == {0: (1.0, 10.0)}


def test_capital_matches_the_watcher():
    for c in (0.0, 0.1, 0.3, 0.5, 0.95):
        for im in (0.1, 0.2):
            assert A.capital_per_short(c, im) == pytest.approx(CW.capital_per_short(c, im) if c else 1 + im + 0.5)


# ------------------------------------------------------------------------------------------- P&L arithmetic

def test_constant_floor_flat_basis_earns_floor_minus_costs():
    coin = make_coin(first=0, last=120)
    days = list(range(40, 121))
    ex, bk = run({'AAA': coin}, days, variant())
    side = (A.FEE_BP['spot'] + 2.0 + A.FEE_BP['perp'] + 2.0) / 1e4   # one side of both legs
    n = 1.0 / A.capital_per_short(0.5, 0.1)                            # K = 1.0
    assert sum(ex) == pytest.approx(n * (3 * 0.0001 * len(days) - 2 * side), abs=1e-12)
    assert bk['basis'] == pytest.approx(0.0, abs=1e-15)
    assert bk['forced_exits'] == 0
    assert bk['turnover'] == pytest.approx(2 * n)       # one entry, one exit: re-selection at flat prices trades nothing


def test_capital_scales_the_return_and_the_benchmark_is_charged_on_invested_capital():
    coin = make_coin(c=0.1)                                            # K = 1 + 0.1 + 0.5 - 0.15 = 1.45
    days = list(range(40, 121))
    ex, _ = run({'AAA': coin}, days, variant(), bench=0.05)
    K = A.capital_per_short(0.1, 0.1)
    assert K == pytest.approx(1.45)
    side = (A.FEE_BP['spot'] + 2.0 + A.FEE_BP['perp'] + 2.0) / 1e4
    expect = (1.0 / K) * (3 * 0.0001 * len(days) - 2 * side) - 0.05 / 365.0 * len(days)
    assert sum(ex) == pytest.approx(expect, abs=1e-12)


def test_basis_change_is_marked_to_the_short():
    coin = make_coin()
    for d in range(60, 121):
        coin['pc'][d] = 101.0                  # the perp's premium rises 1% on day 60 and stays
    days = list(range(40, 121))
    ex, bk = run({'AAA': coin}, days, variant(spike_8h=None))
    assert bk['basis'] == pytest.approx(-(1.0 / 100.0) * 1.0, rel=1e-9)   # q = 1/100 per unit capital, -$1 a unit


def test_negative_spike_screen():
    coin = make_coin()
    d_spike = 50
    coin['fd'][d_spike][0] = (coin['fd'][d_spike][0][0], -0.0006, 100.0, 8)       # -0.06% per 8 h
    feats = {'AAA': A.features(coin, 60)}
    members = {'AAA': 'AAA'}
    assert A.select(feats, variant(spike_8h=None), members)[0] == ['AAA']
    assert A.select(feats, variant(spike_8h=A.SPIKE_8H), members)[0] == []
    coin['fd'][d_spike][0] = (coin['fd'][d_spike][0][0], -0.0004, 100.0, 8)       # above the threshold
    assert A.select({'AAA': A.features(coin, 60)}, variant(spike_8h=A.SPIKE_8H), members)[0] == ['AAA']
    hourly = make_coin(hours=1)
    hourly['fd'][d_spike][0] = (hourly['fd'][d_spike][0][0], -0.0001, 100.0, 1)   # -0.01% an hour = -0.08% / 8 h
    assert A.select({'AAA': A.features(hourly, 60)}, variant(spike_8h=A.SPIKE_8H), members)[0] == []
    assert A.features(coin, 50 + A.LOOKBACK + 1)['min_rate_8h'] > 0             # the spike has left the window


def test_floor_share_threshold_and_ranking():
    a = make_coin('AAA')                                  # always at the floor
    b = make_coin('BBB', rate=0.0003)                     # above the floor: floor share 0, high APR
    c = make_coin('CCC', spot_vol=3e6)                    # at the floor, thinner
    feats = {s: A.features(x, 60) for s, x in (('AAA', a), ('BBB', b), ('CCC', c))}
    members = {'AAA': 'AAA', 'BBB': 'BBB', 'CCC': 'CCC'}
    sel, nq = A.select(feats, variant(n_names=10), members)
    assert sel == ['AAA', 'CCC'] and nq == 2              # BBB fails the floor share; AAA outranks CCC on volume
    sel, _ = A.select(feats, variant(n_names=10, spot_vol_min_usd=1e7), members)
    assert sel == ['AAA']
    base = dict(A.BASELINE, rebalance_days=7, n_names=10)
    assert A.select(feats, base, members)[0] == ['AAA', 'CCC', 'BBB']


def test_delisting_exit_pays_double_costs_at_the_last_traded_prices():
    coin = make_coin(first=0, last=120, spot_last=70)     # spot delisted: last (partial) traded day 70
    days = list(range(40, 121))
    ex, bk = run({'AAA': coin}, days, variant())
    side = (A.FEE_BP['spot'] + 2.0 + A.FEE_BP['perp'] + 2.0) / 1e4
    held = 70 - 40                                        # days 40..69 earn; the exit is at day 69's close
    assert bk['forced_exits'] == 1 and bk['forced_exits_delisting'] == 1
    assert sum(ex) == pytest.approx(3 * 0.0001 * held - side - 2 * side, abs=1e-12)
    assert bk['exits'][0]['day'] == A.dname(70)
    assert all(x == 0.0 for x in ex[held + 1:])           # nothing held afterwards (the coin is never eligible again)


def test_gap_in_a_leg_forces_an_exit():
    coin = make_coin()
    del coin['sc'][55], coin['sv'][55]
    days = list(range(40, 121))
    ex, bk = run({'AAA': coin}, days, variant())
    assert bk['forced_exits_gap'] == 1


def test_rally_beyond_the_stress_forces_a_drift_rebalance():
    coin = make_coin()
    for d in range(45, 121):
        coin['pc'][d] = coin['sc'][d] = 160.0             # +60% on day 45, flat basis
    days = list(range(40, 121))
    _, bk = run({'AAA': coin}, days, variant(rebalance_days=28))
    assert bk['rally_rebalances'] == 1


# ------------------------------------------------------------------------------------------- no look-ahead

def test_features_at_a_rebalance_use_only_earlier_days():
    coin = make_coin()
    d = 60
    before = A.features(coin, d)
    later = copy.deepcopy(coin)
    for x in range(d, 121):
        later['fd'][x] = [(t, -0.01, 1.0, h) for t, _, _, h in later['fd'][x]]
        later['pc'][x] = later['sc'][x] = 1.0
        later['sv'][x] = later['pv'][x] = 0.0
    assert A.features(later, d) == before
    later['fd'][d - 1] = [(t, -0.01, 1.0, h) for t, _, _, h in later['fd'][d - 1]]
    assert A.features(later, d) != before                 # ... and day d-1 is seen


def test_selection_at_a_rebalance_ignores_the_future():
    good, trap = make_coin('AAA'), make_coin('BBB', spot_vol=3e6)
    days = list(range(40, 121))
    _, bk1 = run({'AAA': good, 'BBB': trap}, days, variant(rebalance_days=28, n_names=1))
    fut = copy.deepcopy(good)
    for x in range(40, 121):                              # AAA turns terrible from the first decision day on
        fut['fd'][x] = [(t, -0.002, 100.0, h) for t, _, _, h in fut['fd'][x]]
    _, bk2 = run({'AAA': fut, 'BBB': trap}, days, variant(rebalance_days=28, n_names=1))
    first1, first2 = bk1['_books'][0][1], bk2['_books'][0][1]
    assert list(first1) == list(first2) == ['AAA']        # the first decision cannot see it
    assert list(bk2['_books'][1][1]) == ['BBB']           # the next one, 28 days later, does


# ------------------------------------------------------------------------------------------- costs

def test_spread_table_is_monotone_and_uses_the_75th_percentile():
    book = [{'symbol': 'A%dUSDT' % i, 'bidPrice': '100', 'askPrice': str(100 + s)} for i, s in
            enumerate((0.02, 0.04, 0.06, 0.08, 0.01, 0.01, 0.01, 0.01))]
    t24 = [{'symbol': 'A%dUSDT' % i, 'quoteVolume': str(v)} for i, v in
           enumerate((1e6, 1e6, 1e6, 1e6, 5e7, 5e7, 5e7, 5e7))]
    tab = A.spread_table(book, t24, buckets=(0, 1e7))
    assert tab[0][0] == 0 and tab[0][1] == pytest.approx(0.08 / 200.08 * 1e4, rel=1e-6)
    assert tab[1][1] <= tab[0][1]
    assert A.half_spread_bp(tab, 5e8) == tab[1][1]
    assert A.half_spread_bp(tab, 5e8, tick_bp=9.0) == 9.0


def test_square_root_impact():
    assert A.impact_frac(0, 1e7, 0.05, 0.5) == 0.0
    assert A.impact_frac(3e5, 1e7, 0.05, 0.5, days=3) == pytest.approx(0.5 * 0.05 * (1e5 / 1e7) ** 0.5)


def test_participation_cap_and_impact_in_a_sized_run():
    coin = make_coin(spot_vol=5e6, perp_vol=5e7)
    days = list(range(40, 121))
    co = A.Costs(TABLE, TABLE, aum=1e7, Y=0.5)
    _, bk = run({'AAA': coin}, days, variant(), costs=co)
    assert bk['capped_name_rebalances'] == bk['name_rebalances'] > 0
    assert bk['mean_invested'] == pytest.approx(A.PARTICIPATION * 5e6 / 1e7)   # $100k of $10M deployed
    assert bk['impact'] == 0.0                            # sigma is zero on a flat price, so no impact


def test_grid_is_small_and_named_uniquely():
    v = A.grid_variants()
    assert 24 <= len(v) <= 48
    assert len({x['name'] for x in v}) == len(v)


def test_one_sided_bh_rejects_significant_losers():
    import random
    rng = random.Random(1)
    win = [0.001 + rng.gauss(0, 0.002) for _ in range(400)]
    lose = [-0.001 + rng.gauss(0, 0.002) for _ in range(400)]
    noise = [rng.gauss(0, 0.002) for _ in range(400)]
    surv, adj = A.bh_one_sided({'win': win, 'lose': lose, 'noise': noise})
    assert surv == ['win']
    assert adj['lose'] > 0.5


def test_archive_csv_parsing_handles_headers_and_microseconds():
    text = ('open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,'
            'taker_buy_quote_volume,ignore\n'
            '1735689600000,1,2,0.5,1.5,10,1735775999999,15.0,7,5,7.5,0\n'
            '1735776000000000,1.5,2,1,1.2,10,1735862399999999,12.0,3,5,6,0\n')
    rows = A.parse_archive_csv(text)
    assert [r[0] for r in rows] == [1735689600000, 1735776000000]
    assert A.kline_days(rows) == {1735689600000 // A.DAY_MS: (1.5, 15.0), 1735776000000 // A.DAY_MS: (1.2, 12.0)}
    assert A.months_between(A.day_ms('2024-09-01'), A.day_ms('2024-12-15')) == ['2024-09', '2024-10', '2024-11',
                                                                               '2024-12']
