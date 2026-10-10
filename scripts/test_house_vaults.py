#!/usr/bin/env python3
"""Tests for scripts/house_vaults.py: the core math on synthetic inputs (flow-adjusted returns, hedge accounting, cost
model, rules, capacity) and the parsers. Run:

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_house_vaults.py -q
"""
import gzip
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import house_vaults as H  # noqa: E402

DAY = H.DAY_MS
T0 = H.day_ts('2025-01-01') * 1000


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# ---------------------------------------------------------------------------------------------------------------------
# flow-adjusted returns
# ---------------------------------------------------------------------------------------------------------------------
def test_dietz_excludes_flows():
    # AV 100 -> 160: +10 P&L and a +50 deposit. Modified Dietz: 10 / (100 + 50/2) = 0.08; simple: 10/100.
    pts = [(T0, 100.0, 0.0), (T0 + 14 * DAY, 160.0, 10.0)]
    r = H.dietz_returns(pts)
    assert len(r) == 1
    assert approx(r[0]['r_v'], 0.08)
    assert approx(r[0]['r_simple'], 0.10)
    assert approx(r[0]['flow'], 50.0)
    assert approx(r[0]['days'], 14.0)


def test_dietz_withdrawal_and_zero_start():
    # the first point has no capital (vault launch): skipped; a withdrawal of 40 with a loss of 5
    pts = [(T0, 0.0, 0.0), (T0 + DAY, 100.0, 0.0), (T0 + 2 * DAY, 55.0, -5.0)]
    r = H.dietz_returns(pts)
    assert len(r) == 1
    assert approx(r[0]['flow'], -40.0)
    assert approx(r[0]['r_v'], -5.0 / (100.0 - 20.0))


def test_price_returns_drop_stale():
    pts = [(T0, 1.0), (T0 + DAY, 1.01), (T0 + 2 * DAY, 1.01), (T0 + 3 * DAY, 1.0201)]
    r = H.price_returns(pts)
    assert len(r) == 2
    assert approx(r[1]['days'], 2.0) and approx(r[1]['r_v'], 0.01)
    r2 = H.price_returns(pts, drop_stale=False)
    assert len(r2) == 3 and r2[1]['r_v'] == 0.0


def test_nav_points_compound():
    P = [{'t0': T0, 't1': T0 + DAY, 'r_v': 0.1}, {'t0': T0 + DAY, 't1': T0 + 2 * DAY, 'r_v': -0.1}]
    nav = H.nav_points(P)
    assert nav[0] == (T0, 1.0) and approx(nav[-1][1], 0.99)


# ---------------------------------------------------------------------------------------------------------------------
# benchmark
# ---------------------------------------------------------------------------------------------------------------------
def test_savings_between_year_and_boundary():
    a = H.day_ts('2024-01-01') * 1000
    b = H.day_ts('2025-01-01') * 1000
    assert approx(H.savings_between(a, b), 0.078 * 366 / 365)
    # ten days either side of 1 Jan 2025: 10 days at 7.8% and 10 at 5.5%
    m = H.day_ts('2025-01-01') * 1000
    assert approx(H.savings_between(m - 10 * DAY, m + 10 * DAY), (0.078 + 0.055) * 10 / 365)


# ---------------------------------------------------------------------------------------------------------------------
# regression and betas
# ---------------------------------------------------------------------------------------------------------------------
def test_ols_recovers_coefficients():
    xs = [[math.sin(i), math.cos(3 * i)] for i in range(50)]
    y = [0.01 + 0.5 * a - 0.2 * b for a, b in xs]
    f = H.ols(y, xs)
    assert approx(f['alpha'], 0.01, 1e-8) and approx(f['betas'][0], 0.5, 1e-8) and approx(f['betas'][1], -0.2, 1e-8)
    assert H.ols([1.0, 2.0], [[1.0], [2.0]]) is None          # too few observations
    assert H.ols([1.0, 2.0, 3.0, 4.0], [[1.0, 2.0]] * 4) is None  # singular


def _periods(n, beta_fn, start=T0, asset='BTC'):
    out = []
    for i in range(n):
        ra = 0.02 * math.sin(1.7 * i) + 0.01 * math.cos(0.3 * i)
        out.append({'t0': start + i * DAY, 't1': start + (i + 1) * DAY, 'days': 1.0, 'r_v': beta_fn(i) * ra + 0.0002,
                    'r': {asset: ra}, 'f': {asset: 0.0001}, 's': 0.0})
    return out


def test_static_betas_in_sample_only():
    P = _periods(100, lambda i: 0.5 if i < 50 else 0.9)
    b = H.static_betas(P, ['BTC'], 50)
    assert approx(b['BTC'], 0.5, 1e-6)


def test_rolling_betas_no_lookahead():
    P = _periods(120, lambda i: 0.5 if i < 60 else 0.9)
    bb = H.rolling_betas(P, ['BTC'], window_days=30, every_days=1, min_obs=10)
    assert bb[5] == {}                                   # not enough history yet
    assert approx(bb[60]['BTC'], 0.5, 1e-6)              # the regime change at 60 is not yet visible
    assert approx(bb[119]['BTC'], 0.9, 1e-6)             # the trailing window now holds only the new regime


# ---------------------------------------------------------------------------------------------------------------------
# hedge accounting and costs
# ---------------------------------------------------------------------------------------------------------------------
def test_simulate_hedge_perfect_hedge_and_costs():
    P = _periods(10, lambda i: 0.6)
    sim = H.simulate_hedge(P, [{'BTC': 0.6}] * 10, fee=0.0005, margin=1 / 3, band=10.0)  # huge band: no rebalancing
    # first period: open 0.6 notional at 5bp
    assert approx(sim[0]['cost'], 0.0005 * 0.6)
    assert approx(sim[0]['capital'], 1 + 0.6 / 3)
    # the price leg cancels the vault's market move exactly in period 0; funding pays the short 0.6 * 1bp
    assert approx(sim[0]['price_pnl'], -0.6 * P[0]['r']['BTC'])
    assert approx(sim[0]['fund_pnl'], 0.6 * 0.0001)
    assert approx(sim[0]['pnl'], 0.0002 + 0.6 * 0.0001 - 0.0005 * 0.6)
    assert all(s['cost'] == 0.0 for s in sim[1:])         # never rebalanced inside the band


def test_simulate_hedge_rebalances_beyond_band_and_sign_flip():
    P = _periods(3, lambda i: 0.5)
    sim = H.simulate_hedge(P, [{'BTC': 0.5}, {'BTC': 0.8}, {'BTC': -0.2}], fee=0.001, band=0.10)
    assert approx(sim[1]['traded'], abs(0.8 - 0.5 * (1 + P[0]['r']['BTC']) / (1 + P[0]['r_v'])), 1e-9)
    assert sim[2]['traded'] > 1.0 - 1e-9 and sim[2]['gross'] == 0.2   # flipped from short 0.8-ish to long 0.2


def test_funding_sign_long_hedge_pays():
    P = _periods(1, lambda i: -0.3)
    sim = H.simulate_hedge(P, [{'BTC': -0.3}], fee=0.0)
    assert approx(sim[0]['fund_pnl'], -0.3 * 0.0001)     # a long hedge pays positive funding


def test_apply_rule_segments_costs():
    P = _periods(6, lambda i: 0.0)
    sh = [{'ret': 0.001, 's': 0.0002, 'capital': 1.0, 'gross': 0.0} for _ in P]
    out = H.apply_rule_segments(P, sh, None, entry_exit=0.002, starts=(0, 3))
    # always on: entry half at each segment start, exit half at each segment end
    assert approx(out[0]['x'], 0.0008 - 0.001)
    assert approx(out[2]['x'], 0.0008 - 0.001)
    assert approx(out[3]['x'], 0.0008 - 0.001)
    assert approx(out[1]['x'], 0.0008)
    # a rule that needs 30 days of history is never on in a 6-day sample: every period earns the savings rate (0 excess)
    off = H.apply_rule_segments(P, sh, 0.0, entry_exit=0.002, starts=(0,))
    assert all(x['x'] == 0.0 and not x['on'] for x in off)


# ---------------------------------------------------------------------------------------------------------------------
# statistics helpers
# ---------------------------------------------------------------------------------------------------------------------
def test_best_share_and_worst_window():
    xs = [0.01] * 99 + [1.0]
    assert approx(H.best_share(xs), 1.0 / 1.99)
    P = [{'days': 1.0}] * 10
    assert approx(H.worst_window(P, [0.0, -1.0, -1.0, 0.5, -3.0, 0, 0, 0, 0, 0], 2.0), -3.0)
    assert approx(H.worst_window(P, [-1.0] * 10, 7.0), -7.0)


# ---------------------------------------------------------------------------------------------------------------------
# capacity
# ---------------------------------------------------------------------------------------------------------------------
def test_income_vs_tvl_fixed_income():
    rows = [(tvl, 1000.0 + 0.0 * tvl + (5 if i % 2 else -5)) for i, tvl in enumerate(range(10_000_000, 30_000_000, 1_000_000))]
    f = H.income_vs_tvl(rows)
    assert abs(f['b_per_day']) < 1e-6 and abs(f['a_usd_day'] - 1000.0) < 10


def test_dilution_and_deposit_inverse():
    a, b, tvl, s = 10_000.0, 0.0, 50e6, 0.038      # $3.65M a year on $50M = 7.3%
    assert approx(H.diluted_excess(a, b, tvl, 0.0, s), 3.65e6 / 50e6 - s)
    X = H.deposit_for_excess(a, b, tvl, s, 0.02)
    assert approx(H.diluted_excess(a, b, tvl, X, s), 0.02, 1e-9)
    assert H.deposit_for_excess(a, 0.10 / 365, tvl, s, 0.02) == float('inf')   # proportional income never dilutes


# ---------------------------------------------------------------------------------------------------------------------
# parsers
# ---------------------------------------------------------------------------------------------------------------------
def test_parse_hl_portfolio():
    det = {'portfolio': [['allTime', {'accountValueHistory': [[2, '10.0'], [1, '5.0']],
                                      'pnlHistory': [[1, '0.0'], [2, '1.5'], [3, '9']]}]]}
    assert H.parse_hl_portfolio(det, 'allTime') == [(1, 5.0, 0.0), (2, 10.0, 1.5)]


def test_parse_squid_prices_scale_and_mid():
    rows = [{'snapshotTimestamp': 1791590400, 'minPrice': str(19 * 10 ** 29), 'maxPrice': str(21 * 10 ** 29)}]
    assert H.parse_squid_prices(rows) == {'2026-10-10': 2.0}


def test_parse_dydx_pnl_and_hex():
    rows = [{'equity': '10', 'totalPnl': '1', 'netTransfers': '0', 'blockTime': '2026-07-14T00:13:41.819Z'}]
    t, e, p, f = H.parse_dydx_pnl(rows)[0]
    assert H.day_of(t) == '2026-07-14' and e == 10.0 and p == 1.0 and f == 0.0
    assert H.hex_int256('0x' + 'f' * 64) == -1
    assert H.hex_uint('0x0de0b6b3a7640000') == 10 ** 18 and H.hex_uint('0x') is None


def test_parse_llama_chart_last_of_day():
    objs = [{'coins': {'x': {'prices': [{'timestamp': 1700000000, 'price': 1.0}, {'timestamp': 1700003600, 'price': 1.1}]}}}]
    assert H.parse_llama_chart(objs) == {H.day_of(1700000000): 1.1}


def test_interp_block():
    anchors = [(1000, 100), (2000, 200), (6000, 300)]
    assert H.interp_block(anchors, 150) == 1500 and H.interp_block(anchors, 250) == 4000
    assert H.interp_block(anchors, 50) == 1000 and H.interp_block(anchors, 400) == 6000


def test_pricebook_price_and_funding(tmp_path):
    raw = tmp_path / 'raw' / 'binance'
    raw.mkdir(parents=True)
    h = H.H_MS
    rows = [[T0 + i * h, 0, 0, 0, 100.0 + i, 1e6] for i in range(48)]
    with gzip.open(raw / 'klines1h_BTCUSDT.json.gz', 'wt') as f:
        json.dump(rows, f)
    with gzip.open(raw / 'funding_BTCUSDT.json.gz', 'wt') as f:
        json.dump([{'t': T0 + 8 * h * k + 1, 'rate': 0.0001 * (k + 1)} for k in range(6)], f)
    book = H.PriceBook(tmp_path / 'raw')
    # the bar opened at T0 closes at T0+1h with close 100: the price "at" T0+1h is 100, at T0+1h+59min still 100
    assert book.price('BTC', T0 + h) == 100.0 and book.price('BTC', T0 + 2 * h - 1) == 100.0
    assert approx(book.ret('BTC', T0 + h, T0 + 3 * h), 102.0 / 100.0 - 1)
    # settlements at T0+1ms, T0+8h+1ms, ...: (T0, T0+16h] holds the first two
    assert approx(book.funding('BTC', T0, T0 + 16 * h), 0.0001 + 0.0002)
    assert book.funding('ETH', T0, T0 + h) is None
