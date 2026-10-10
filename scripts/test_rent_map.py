"""Tests for scripts/rent_map.py: the arithmetic every number in the rent map rests on (annualisation, the above-fair
split, windows and realised flows, LVR, queue and YT rents), the double-count guards, and the parsers.

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_rent_map.py -q
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rent_map as R  # noqa: E402

DAY = R.DAY_MS
HOUR = R.HOUR_MS


# ---------------------------------------------------------------------------------------------- annualisation

def test_annualise_scales_by_365_over_days():
    assert R.annualise(30.0, 30) == pytest.approx(365.0)
    assert R.annualise(1.0, 365) == pytest.approx(1.0)
    assert R.annualise(7.0, 7) == pytest.approx(365.0)


@pytest.mark.parametrize('days', [0, -1])
def test_annualise_refuses_empty_windows(days):
    with pytest.raises(ValueError):
        R.annualise(1.0, days)


def test_apy_to_apr_is_the_continuous_rate():
    assert R.apy_to_apr(math.e - 1) == pytest.approx(1.0)
    assert R.apy_to_apr(0.05) == pytest.approx(math.log(1.05))
    assert R.apy_to_apr(0.0) == 0.0
    assert R.apy_to_apr(None) is None


# ---------------------------------------------------------------------------------------------- above-fair split

def test_flow_split_above_fair_positive():
    s = R.flow_split(1_000_000, 0.10, 0.038)
    assert s['gross'] == pytest.approx(100_000)
    assert s['fair_part'] == pytest.approx(38_000)
    assert s['above_fair'] == pytest.approx(62_000)
    assert s['above_fair_clipped'] == pytest.approx(62_000)
    assert s['fair_part'] + s['above_fair'] == pytest.approx(s['gross'])


def test_flow_split_below_fair_is_negative_and_clipped_to_zero():
    s = R.flow_split(1_000_000, 0.02, 0.038)
    assert s['above_fair'] == pytest.approx(-18_000)
    assert s['above_fair_clipped'] == 0.0
    assert s['fair_part'] == pytest.approx(20_000)   # a fair rate explains no more than the flow itself


def test_flow_split_negative_rate_pays_the_other_way():
    s = R.flow_split(1_000_000, -0.05, 0.038)
    assert s['gross'] == pytest.approx(-50_000)
    assert s['fair_part'] == 0.0
    assert s['above_fair'] == pytest.approx(-88_000)


def test_fair_rate_by_class():
    assert R.fair_rate('stable') == R.SSR
    assert R.fair_rate('eth') == R.ETH_FAIR
    assert R.fair_rate('btc') == 0.0
    assert R.fair_rate('other') == 0.0


# ---------------------------------------------------------------------------------------------- windows and flows

def hourly(n, rate, t_end):
    return [(t_end - i * HOUR, rate) for i in range(n)]


def test_window_stats_annual_rate_is_interval_free():
    t_end = 1_000 * DAY
    h = hourly(30 * 24, 0.0000125, t_end)                       # 0.00125%/h = 10.95%/yr
    s = R.window_stats(h, t_end, 30)
    assert s['n'] == 720
    assert s['ann'] == pytest.approx(0.0000125 * 8760, rel=1e-9)
    e = [(t_end - i * 8 * HOUR, 0.0001) for i in range(90)]    # 0.01% per 8h, 90 settlements in 30 days
    assert R.window_stats(e, t_end, 30)['ann'] == pytest.approx(0.0001 * 3 * 365, rel=1e-9)


def test_window_stats_boundaries_and_signs():
    t_end = 100 * DAY
    series = [(t_end - 30 * DAY, 1.0),          # exactly at t0: excluded
              (t_end - 10 * DAY, 0.002), (t_end - 5 * DAY, -0.001), (t_end, 0.003),
              (t_end + HOUR, 9.0)]              # after the window: excluded
    s = R.window_stats(series, t_end, 30)
    assert s['n'] == 3
    assert s['sum'] == pytest.approx(0.004)
    assert s['sum_pos'] == pytest.approx(0.005)
    assert s['sum_neg'] == pytest.approx(-0.001)
    assert s['share_pos'] == pytest.approx(2 / 3)
    assert s['ann_pos'] + s['ann_neg'] == pytest.approx(s['ann'])


def test_coverage_ok_rejects_a_coin_listed_mid_window():
    t_end = 100 * DAY
    full = R.window_stats(hourly(720, 1e-5, t_end), t_end, 30)
    half = R.window_stats(hourly(300, 1e-5, t_end), t_end, 30)
    assert R.coverage_ok(full, 30, 24)
    assert not R.coverage_ok(half, 30, 24)


def test_interp_linear_and_flat_outside():
    pts = [(10, 100.0), (20, 200.0)]
    assert R.interp(pts, 15) == pytest.approx(150.0)
    assert R.interp(pts, 0) == 100.0
    assert R.interp(pts, 99) == 200.0
    assert R.interp([], 5) is None


def test_realised_flow_uses_interpolated_oi_and_splits_sides():
    oi = [(0, 1_000.0), (10 * HOUR, 2_000.0)]
    rates = [(5 * HOUR, 0.01), (10 * HOUR, -0.02), (11 * HOUR, 0.5)]
    f = R.realised_flow(rates, oi, 0, 10 * HOUR)
    assert f['n'] == 2
    assert f['longs_paid'] == pytest.approx(1_500.0 * 0.01)
    assert f['shorts_paid'] == pytest.approx(2_000.0 * 0.02)
    assert f['net'] == pytest.approx(15.0 - 40.0)


# ---------------------------------------------------------------------------------------------- LVR, queue, YT

def test_sigma_annual():
    assert R.sigma_annual([100.0 * 1.01 ** i for i in range(30)]) == pytest.approx(0.0, abs=1e-12)
    closes = [100.0 * (1.02 if i % 2 else 1.0) for i in range(41)]   # 40 log returns, +-ln(1.02), mean 0
    assert R.sigma_annual(closes) == pytest.approx(math.log(1.02) * math.sqrt(365), rel=1e-9)
    assert R.sigma_annual([1.0, 2.0]) is None


def test_lvr_full_range_and_concentrated():
    assert R.lvr_rate(0.5) == pytest.approx(0.25 / 8)
    m = R.lvr_rate_concentrated(0.5, 4.0) / R.lvr_rate(0.5)
    assert m == pytest.approx(1 / (1 - 4 ** -0.25))
    assert m == pytest.approx(3.4142, rel=1e-4)
    with pytest.raises(ValueError):
        R.lvr_rate_concentrated(0.5, 1.0)


def test_queue_rent_net_of_fee_and_time_value():
    # $3.65M sold over 365 days at 20bp; 1bp fee; 10-day queue at 3.65% -> 10bp time value; above fair 9bp
    q = R.queue_rent(3_650_000, 20.0, 1.0, 10.0, 0.0365, 365)
    assert q['fair_bp'] == pytest.approx(10.0)
    assert q['gross'] == pytest.approx(7_300.0)
    assert q['above_fair'] == pytest.approx(3_650_000 * 9e-4)
    # a discount below fee + time value leaves no rent
    assert R.queue_rent(1e6, 5.0, 1.0, 30.0, 0.0365, 30)['above_fair'] == 0.0


def test_yt_premium_sign():
    assert R.yt_premium(1e6, 0.10, 0.06) == pytest.approx(40_000)
    assert R.yt_premium(1e6, 0.05, 0.08) == pytest.approx(-30_000)


# ---------------------------------------------------------------------------------------------- classification

@pytest.mark.parametrize('name,cls', [('xyz:CL', 'energy'), ('xyz:BRENTOIL', 'energy'), ('xyz:GOLD', 'metal'),
                                      ('xyz:SP500', 'index'), ('xyz:NVDA', 'equity'), ('xyz:EUR', 'fx'),
                                      ('para:10Y', 'rates'), ('hyna:BTC', 'crypto'), ('xyz:CORN', 'agri')])
def test_classify_hip3(name, cls):
    assert R.classify_hip3(name, crypto_names=('BTC', 'ETH')) == cls


def test_roll_classes_are_not_rent():
    assert R.ROLL_CLASSES == {'energy', 'agri'}


@pytest.mark.parametrize('sym,cls', [('USDC', 'stable'), ('USDT0', 'stable'), ('crvUSD', 'stable'), ('WETH', 'eth'),
                                     ('wstETH', 'eth'), ('cbBTC', 'btc'), ('LBTC', 'btc'), ('SOL', 'other'), ('AAVE', 'other')])
def test_asset_class(sym, cls):
    assert R.asset_class(sym) == cls


@pytest.mark.parametrize('coin,metal', [('XAUUSDT', True), ('xyz:GOLD', True), ('XAU-USDT-SWAP', True), ('PAXG', True),
                                        ('XAUTUSDT', True), ('xyz:SILVER', True), ('BTCUSDT', False), ('xyz:CL', False),
                                        ('ETH-USDT-SWAP', False)])
def test_is_metal(coin, metal):
    assert R.is_metal(coin) is metal


@pytest.mark.parametrize('sym,pair', [('WETH-USDC', ('ETH', 'USD')), ('USDC-WETH', ('ETH', 'USD')),
                                      ('WBTC-WETH', ('BTC', 'ETH')), ('CBBTC-WETH', ('BTC', 'ETH')), ('SOL-USDC', ('SOL', 'USD')),
                                      ('USDC-USDT', None), ('PEPE-WETH', None), ('WSTETH-WETH', None), ('A-B-C', None)])
def test_pair_of(sym, pair):
    assert R.pair_of(sym) == pair


# ---------------------------------------------------------------------------------------------- double-count guards

def test_pool_of_overrides_and_interfaces():
    assert R.pool_of({'slug': 'pendle-v2', 'category': 'Yield'}) == 'points'
    assert R.pool_of({'slug': 'ethena-usde', 'category': 'Basis Trading'}) == 'collector'
    assert R.pool_of({'slug': 'world-liberty-financial', 'category': 'Lending'}) == 'scale_stable'
    assert R.pool_of({'slug': 'tradexyz', 'name': 'tradeXYZ', 'category': 'Interface', 'chains': ['Hyperliquid L1']}) == 'perp_vaults'
    assert R.pool_of({'slug': 'metamask-perps', 'name': 'MetaMask Perps', 'category': 'Interface', 'chains': ['Hyperliquid L1']}) == 'perp_vaults'
    assert R.pool_of({'slug': 'some-wallet', 'name': 'Some Wallet', 'category': 'Interface', 'chains': ['Solana']}) == 'entertainment'
    assert R.pool_of({'slug': 'pump.fun-mobile-app', 'name': 'pump.fun Mobile App', 'category': 'Interface'}) == 'entertainment'
    assert R.pool_of({'slug': 'uniswap-v3', 'category': 'Dexs'}) == 'dex_lp'
    assert R.pool_of({'slug': 'x', 'category': 'Wallets'}) is None


def test_assign_pools_refuses_a_protocol_in_two_pools():
    ok = R.assign_pools([{'slug': 'a', 'category': 'Dexs'}, {'slug': 'a', 'category': 'Dexs'}])
    assert ok == {'a': 'dex_lp'}
    with pytest.raises(ValueError):
        R.assign_pools([{'slug': 'a', 'category': 'Dexs'}, {'slug': 'a', 'category': 'Lending'}])


def test_incentive_budget_guards():
    pools = [
        {'project': 'p1', 'chain': 'Ethereum', 'symbol': 'USDC', 'tvlUsd': 1e8, 'apyReward': 5.0, 'stablecoin': True},
        {'project': 'p1', 'chain': 'Ethereum', 'symbol': 'X', 'tvlUsd': 1e6, 'apyReward': 120000.0, 'outlier': True},
        {'project': 'p1', 'chain': 'Base', 'symbol': 'Y', 'tvlUsd': 1e6, 'apyReward': 400.0},
        {'project': 'vault', 'chain': 'Base', 'symbol': 'USDC', 'tvlUsd': 1e7, 'apyReward': 10.0},
        {'project': 'p1', 'chain': 'Base', 'symbol': 'dust', 'tvlUsd': 5e3, 'apyReward': 50.0},
        {'project': 'p1', 'chain': 'Base', 'symbol': 'none', 'tvlUsd': 1e9, 'apyReward': None},
    ]
    tot, rows = R.incentive_budget(pools, {'p1': 'Lending', 'vault': 'Yield Aggregator'})
    assert tot['headline'] == pytest.approx(5e6)
    assert tot['outlier_flagged'] == pytest.approx(1.2e9)
    assert tot['over_cap'] == pytest.approx(4e6)
    assert tot['pass_through'] == pytest.approx(1e6)
    assert tot['tiny'] == pytest.approx(2.5e3)
    assert len(rows) == 1 and rows[0]['stable']


def test_census_total_excludes_scale_rows_and_clips():
    rows = [{'key': 'a', 'size_yr': 10.0, 'above_fair_yr': 4.0, 'above_fair_band': [3.0, 5.0], 'accessible_yr': [0.1, 0.2]},
            {'key': 'b', 'size_yr': 5.0, 'above_fair_yr': -2.0, 'above_fair_band': [-3.0, 1.0], 'accessible_yr': [0.0, 0.0]},
            {'key': 'entertainment', 'size_yr': 100.0, 'above_fair_yr': 0.0, 'above_fair_band': [0, 0], 'accessible_yr': [0, 0]},
            {'key': 'funding_roll', 'size_yr': 50.0, 'above_fair_yr': 0.0, 'above_fair_band': [0, 0], 'accessible_yr': [0, 0]}]
    t = R.census_total(rows)
    assert t['size_yr'] == 15.0
    assert t['above_fair_yr'] == 4.0
    assert t['above_fair_band'] == [3.0, 6.0]
    assert t['accessible_band'] == [0.1, 0.2]


def test_agg_funding_signed_vs_clipped():
    per = [{'oi_usd': 100.0, 'longs_paid_30d': 10.0, 'shorts_paid_30d': 0.0, 'net_30d': 10.0, 'net_90d': 9.0,
            'above_fair_30d': 6.2, 'above_fair_90d': 5.2, 'cls': 'crypto'},
           {'oi_usd': 100.0, 'longs_paid_30d': 0.0, 'shorts_paid_30d': 5.0, 'net_30d': -5.0, 'net_90d': -5.0,
            'above_fair_30d': -8.8, 'above_fair_90d': -8.8, 'cls': 'energy', 'rent': False}]
    a = R._agg_funding(per)
    assert a['all']['above_fair_30d'] == pytest.approx(-2.6)
    assert a['all']['above_fair_30d_clipped'] == pytest.approx(6.2)
    assert a['rent_only']['markets'] == 1
    assert a['all']['oi_weighted_rate_30d'] == pytest.approx(5.0 / 200.0)


def test_band_and_mid():
    assert R.band(3.0, None, 1.0, 2.0) == [1.0, 3.0]
    assert R.band(None) == [None, None]
    assert R.mid([1.0, 3.0]) == 2.0
    assert R.mid([None, None]) is None


# ---------------------------------------------------------------------------------------------- parsers

def test_parse_hl_ctxs_one_side_notional():
    payload = [{'universe': [{'name': 'BTC'}, {'name': 'xyz:GOLD', 'isDelisted': True}]},
               [{'openInterest': '2.0', 'markPx': '80000', 'oraclePx': '80010', 'funding': '0.0000125', 'dayNtlVlm': '1e6'},
                {'openInterest': '0', 'markPx': '4000', 'funding': '0'}]]
    rows = R.parse_hl_ctxs(payload, 'main')
    assert rows[0]['oi_usd'] == pytest.approx(160_000.0)
    assert rows[0]['funding_h'] == pytest.approx(0.0000125)
    assert rows[1]['delisted'] is True
    assert R.parse_hl_ctxs({'_failed': 'x'}) == []
    assert R.store_key('xyz:GOLD') == 'xyz__GOLD'


def test_parse_exchange_rows():
    bn = R.parse_bn_funding([{'fundingTime': 2, 'fundingRate': '0.0001'}, {'fundingTime': 1, 'fundingRate': '-0.0002'},
                             {'fundingTime': 3, 'fundingRate': ''}])
    assert bn == [(1, -0.0002), (2, 0.0001)]
    oi = R.parse_bn_oi_hist([{'timestamp': 5, 'sumOpenInterestValue': '123.5'}])
    assert oi == [(5, 123.5)]
    by = R.parse_bybit_funding({'result': {'list': [{'fundingRateTimestamp': '9', 'fundingRate': '0.0001'}]}})
    assert by == [(9, 0.0001)]
    ok = R.parse_okx_funding({'data': [{'fundingTime': '7', 'fundingRate': '0.0003', 'realizedRate': '0.0002'},
                                       {'fundingTime': '8', 'fundingRate': '0.0004', 'realizedRate': ''}]})
    assert ok == [(7, 0.0002), (8, 0.0004)]      # the settled rate when present, else the posted one


def test_overview_rows_and_chart_window():
    d = {'protocols': [{'slug': 'a', 'name': 'A', 'category': 'Dexs', 'total30d': 30.0, 'total24h': 1.0, 'total1y': 400.0},
                       {'slug': 'z', 'name': 'Z', 'category': 'Dexs', 'total30d': 0, 'total24h': 0}]}
    rows = R.overview_rows(d)
    assert [r['slug'] for r in rows] == ['a']
    assert R.overview_rows({'_failed': 'x'}) == []
    chart = [[86400 * i, 1.0] for i in range(1, 101)]
    assert R.chart_window(chart, 86400 * 100, 30) == (30.0, 30)


def test_parse_aave_markets_turns_apy_into_apr():
    payload = {'data': {'markets': [{'name': 'AaveV3Ethereum', 'chain': {'chainId': 1}, 'reserves': [
        {'underlyingToken': {'symbol': 'USDC'}, 'usdExchangeRate': '1.0',
         'borrowInfo': {'apy': {'value': '0.05'}, 'total': {'usd': '1000000'}, 'reserveFactor': {'value': '0.1'}},
         'supplyInfo': {'apy': {'value': '0.04'}, 'total': {'value': '2000000'}}},
        {'underlyingToken': {'symbol': 'GHO'}, 'usdExchangeRate': '1.0', 'borrowInfo': None, 'supplyInfo': {}}]}]}}
    rows = R.parse_aave_markets(payload)
    assert rows[0]['borrow_apr'] == pytest.approx(math.log(1.05))
    assert rows[0]['supply_usd'] == pytest.approx(2e6)
    assert rows[1]['borrow_usd'] == 0.0 and rows[1]['borrow_apr'] is None


def test_parse_morpho():
    pages = [{'data': {'markets': {'items': [{'marketId': 'm', 'loanAsset': {'symbol': 'USDC'}, 'collateralAsset': {'symbol': 'cbBTC'},
                                              'morphoBlue': {'chain': {'id': 8453}},
                                              'state': {'borrowAssetsUsd': 5e8, 'supplyAssetsUsd': 6e8, 'borrowApy': 0.05}}]}}}]
    m = R.parse_morpho(pages)
    assert m[0]['loan'] == 'USDC' and m[0]['chain_id'] == 8453 and m[0]['borrow_usd'] == 5e8
