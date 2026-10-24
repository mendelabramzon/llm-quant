"""Tests for levered_trove: carry accounting at a flat price, and the liquidation paths."""
import levered_trove as L


def _data(prices, funding_h=0.0, lido=0.0):
    px = [(i * 3600, p, hi, lo, p) for i, (p, hi, lo) in enumerate(prices)]
    hl = {t: funding_h for t, *_ in px}
    days = {L.S.day(t) for t, *_ in px}
    return hl, {d: lido for d in days}, {}, px, {'wstETH': {'ops': [], 'red': []}}


def test_flat_price_earns_levered_carry():
    n = 24 * 30
    data = _data([(2000.0, 2000.0, 2000.0)] * n, funding_h=0.08 / 8760, lido=0.02)
    c, k, E = 1.5, 5, 1e6
    x = L.simulate('wstETH', data, c, k, 0.1, E)
    lev = 1 / (1 - 1 / c + 1 / k)                        # collateral per $ of equity
    hours = n - 1
    want = E * hours / 8760 * (lev * (0.08 + 0.02) - lev / c * L.RATE)
    got = x['E_end'] - E + x['costs']
    assert abs(got - want) / want < 0.01
    assert x['liqs'] == [] and x['n_reb'] == 1


def test_rally_through_margin_liquidates_perp_and_rebuilds():
    data = _data([(2000.0, 2000.0, 2000.0), (2000.0, 2500.0, 2000.0), (2000.0, 2000.0, 2000.0)])
    x = L.simulate('wstETH', data, 1.5, 5, 0.1, 1e6)
    assert [l[1] for l in x['liqs']] == ['perp']
    # the margin (20% of collateral, less entry cost) is lost; the trove survives at the close
    assert 0.6e6 < x['E_end'] < 0.65e6


def test_wick_below_mcr_liquidates_trove():
    data = _data([(2000.0, 2000.0, 2000.0), (2000.0, 2000.0, 1500.0), (2000.0, 2000.0, 2000.0)])
    x = L.simulate('wstETH', data, 1.5, 5, 0.1, 1e6)
    assert [l[1] for l in x['liqs']] == ['trove']
    assert x['E_end'] < 1e6 * 0.8                          # the collateral went at the wick, the hedge at the close


def test_fixed_cost_charged_per_rebalance():
    data = _data([(2000.0, 2000.0, 2000.0)] * 48)
    a = L.simulate('wstETH', data, 1.5, 5, 0.1, 1e4)
    b = L.simulate('wstETH', data, 1.5, 5, 0.1, 1e4, fixed=3.0)
    assert abs((a['E_end'] - b['E_end']) - 3.0 * b['n_reb']) < 1e-6
