"""Tests for collateral_watch.py: each venue's collateral payload normalised from small fixtures, the snapshot diff on
synthetic snapshots (added, removed, haircut, tiers, collateral token, docs hash; baseline; no duplicate rows), and the
funding arithmetic (interest-leg share per interval, APR convention, capital per $ of short).

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_collateral_watch.py -q
"""
import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collateral_watch as C  # noqa: E402

HOUR = C.HOUR_MS
DAY = C.DAY_MS

# ---------------------------------------------------------------------------------------------- fixtures

HL_DOCS_MD = """> For the complete documentation index, see [llms.txt](https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt).

# Portfolio margin

Under portfolio margin, a user's spot and perps trading are unified for greater capital efficiency.

IMPORTANT: Portfolio margin is a complex technical upgrade. The following requirements apply:&#x20;

* Master account >$5M in weighted volume or account value >$10k
* Account value <$25M
* USDT: 50M USDT global supply cap, 10M USDT global borrow cap, 5M USDT user supply cap, 1M USDT user borrow cap
* USDC: 1B USDC global supply cap, 500M USDC global borrow cap, 250M USDC user supply cap, 50M USDC user borrow cap
* HYPE: 25M HYPE global supply cap, 1M HYPE user supply cap
* BTC: 5k BTC global supply cap, 200 BTC user supply cap

### LTV and borrowing

Under portfolio margin, eligible collateral assets have an LTV (loan-to-value) ratio between 0 and 1. HYPE has an LTV of 0.65 and BTC has an LTV of 0.5. The borrow interest rate for stablecoins is set at `0.05 + 4.75 * max(0, utilization - 0.8)` APY, compounded continuously.

### Liquidations

```latex
# not a heading inside a code block
liquidation_threshold(token) = 0.5 + 0.5 * LTV(token)
```
"""

HL_RESERVES = [[0, {'borrowYearlyRate': '0.05', 'supplyYearlyRate': '0.0338829537', 'balance': '1', 'utilization':
                    '0.7529545263', 'oraclePx': '1.0', 'ltv': '0.0', 'totalSupplied': '546273134.59',
                    'totalBorrowed': '411318829.27'}],
               [150, {'borrowYearlyRate': '0.05', 'supplyYearlyRate': '0.0', 'balance': '1', 'utilization': '0.0',
                      'oraclePx': '85.361', 'ltv': '0.65', 'totalSupplied': '13839757.64', 'totalBorrowed': '0.0'}],
               [197, {'borrowYearlyRate': '0.05', 'supplyYearlyRate': '0.0', 'balance': '1', 'utilization': '0.0',
                      'oraclePx': '82998.0', 'ltv': '0.5', 'totalSupplied': '2225.15', 'totalBorrowed': '0.0'}]]
HL_SPOT_META = {'tokens': [{'index': 0, 'name': 'USDC'}, {'index': 150, 'name': 'HYPE'}, {'index': 197, 'name': 'UBTC'},
                           {'index': 235, 'name': 'USDE'}, {'index': 360, 'name': 'USDH'}],
                'universe': [{'tokens': [150, 0], 'name': '@107', 'index': 107}]}
HL_DEXES = [None, {'name': 'xyz', 'fullName': 'XYZ'}, {'name': 'hyna', 'fullName': 'HyENA'}]
HL_METAS = {'': {'collateralToken': 0, 'universe': [{'name': 'BTC'}, {'name': 'HYPE'}, {'name': 'OLD', 'isDelisted': True}]},
            'xyz': {'collateralToken': 0, 'universe': [{'name': 'xyz:GOLD'}]},
            'hyna': {'collateralToken': 235, 'universe': [{'name': 'hyna:BTC', 'isDelisted': True}]}}

BN_PM = {'code': '000000', 'data': [
    {'asset': 'BTCDOM', 'collateralRate': '0.0000', 'virtual': True, 'discountFactor': 0.0, 'tieredLiquidationRatio': None},
    {'asset': 'USDT', 'collateralRate': '0.9999', 'virtual': False, 'discountFactor': 0.0001, 'tieredLiquidationRatio': None},
    {'asset': 'BTC', 'collateralRate': '0.9500', 'virtual': False, 'discountFactor': 0.05, 'tieredLiquidationRatio': None},
    {'asset': 'XMR', 'collateralRate': '0.0000', 'virtual': False, 'discountFactor': 0.0, 'tieredLiquidationRatio': None},
    {'asset': 'TSLAB', 'collateralRate': '0.5000', 'virtual': False, 'discountFactor': 0.2, 'tieredLiquidationRatio': [
        {'tierFloor': '0.0000', 'tierCap': '5000.0000', 'liquidationRatio': '0.0500', 'cum': '0.0000'},
        {'tierFloor': '5000.0000', 'tierCap': '99999999999.0000', 'liquidationRatio': '0.1000', 'cum': '250.0000'}]}]}
BN_PRO = {'code': '000000', 'data': [
    {'rank': 2, 'assetNames': ['BTC'], 'collaterals': [
        {'tierFloor': '30000000.0000', 'tierCap': '50000000.0000', 'collateralRate': '0.9750', 'cum': '750000.0000'},
        {'tierFloor': '0.0000', 'tierCap': '30000000.0000', 'collateralRate': '1.0000', 'cum': '0.0000'},
        {'tierFloor': '50000000.0000', 'tierCap': '99999999999.0000', 'collateralRate': '0.9500', 'cum': '0'}]},
    {'rank': 10, 'assetNames': ['VELODROME'], 'collaterals': [
        {'tierFloor': '0.0000', 'tierCap': '50000.0000', 'collateralRate': '1.0000', 'cum': '0.0000'},
        {'tierFloor': '50000.0000', 'tierCap': '100000.0000', 'collateralRate': '0.8000', 'cum': '0'},
        {'tierFloor': '100000.0000', 'tierCap': '200000.0000', 'collateralRate': '0.5000', 'cum': '0'},
        {'tierFloor': '200000.0000', 'tierCap': '400000.0000', 'collateralRate': '0.2000', 'cum': '0'},
        {'tierFloor': '400000.0000', 'tierCap': '99999999999.0000', 'collateralRate': '0.1000', 'cum': '0'}]}]}
BN_VIP = {'code': '000000', 'data': [
    {'assetName': 'USDT', 'specs': [{'vipLevel': '0', 'dailyInterestRate': '0.00013102', 'borrowLimit': '500000'},
                                    {'vipLevel': '1', 'dailyInterestRate': '0.00012', 'borrowLimit': '1'}]},
    {'assetName': 'BTC', 'specs': [{'vipLevel': '0', 'dailyInterestRate': '0.00001184', 'borrowLimit': '100'}]}]}
BN_ASSET_INDEX = [{'symbol': 'BTCUSD', 'index': '82984.15', 'bidBuffer': '0.05000000', 'autoExchangeBidBuffer': '0.025'},
                  {'symbol': 'USDTUSD', 'index': '0.9990', 'bidBuffer': '0.00010000', 'autoExchangeBidBuffer': '0.0001'},
                  {'symbol': 'SOLUSD', 'index': '110.19', 'bidBuffer': '0.00000000', 'autoExchangeBidBuffer': '0'}]
BN_FUT_ASSETS = [{'asset': 'USDT', 'marginAvailable': True, 'autoAssetExchange': '-10000'},
                 {'asset': 'BTC', 'marginAvailable': True, 'autoAssetExchange': '-0.1'},
                 {'asset': 'SOL', 'marginAvailable': False, 'autoAssetExchange': '0'}]

OKX_DISC = {'code': '0', 'data': [
    {'amt': '0.23', 'ccy': 'BTC', 'collateralRestrict': False, 'minDiscountRate': '0', 'details': [
        {'discountRate': '0.9775', 'liqPenaltyRate': '0.0225', 'maxAmt': '25', 'minAmt': '20', 'tier': '2'},
        {'discountRate': '0.98', 'liqPenaltyRate': '0.02', 'maxAmt': '20', 'minAmt': '0', 'tier': '1'},
        {'discountRate': '0.5', 'liqPenaltyRate': '0.1', 'maxAmt': '', 'minAmt': '25', 'tier': '3'}]},
    {'amt': '0', 'ccy': 'AERO', 'collateralRestrict': False, 'details': []},
    {'amt': '0', 'ccy': 'LOCKED', 'collateralRestrict': True, 'details': [
        {'discountRate': '0.5', 'maxAmt': '10', 'minAmt': '0', 'tier': '1'}]}]}
OKX_LOAN = {'code': '0', 'data': [{'basic': [{'ccy': 'USDT', 'quota': '5000000', 'rate': '0.000096'},
                                             {'ccy': 'BTC', 'quota': '175', 'rate': '0.00001392'}]}]}

BY_COLL = {'retCode': 0, 'result': {'list': [
    {'currency': 'HYPE', 'collateralRatioList': [
        {'minQty': '0', 'maxQty': '7700', 'collateralRatio': '0.8'},
        {'minQty': '7700', 'maxQty': '99999999999', 'collateralRatio': '0.3'},
        {'minQty': '99999999999', 'maxQty': '', 'collateralRatio': '0'}]},
    {'currency': 'BTC', 'collateralRatioList': [{'minQty': '0', 'maxQty': '', 'collateralRatio': '0.98'}]},
    {'currency': 'NOPE', 'collateralRatioList': [{'minQty': '0', 'maxQty': '', 'collateralRatio': '0.5'}]}]}}
BY_VIP = {'retCode': 0, 'result': {'vipCoinList': [
    {'vipLevel': 'VIP-1', 'list': []},
    {'vipLevel': 'No VIP', 'list': [
        {'currency': 'HYPE', 'borrowable': True, 'collateralRatio': '0.6', 'hourlyBorrowRate': '0.0000073602610000',
         'liquidationOrder': '246', 'marginCollateral': True},
        {'currency': 'BTC', 'borrowable': True, 'collateralRatio': '0.98', 'hourlyBorrowRate': '0.000000493216',
         'liquidationOrder': '3', 'marginCollateral': True},
        {'currency': 'NOPE', 'borrowable': False, 'collateralRatio': '0.5', 'hourlyBorrowRate': '',
         'liquidationOrder': '9', 'marginCollateral': False}]}]}}

DERIBIT_CURRENCIES = {'result': [
    {'currency': 'BTC', 'in_cross_collateral_pool': True, 'apr': 0.0},
    {'currency': 'STETH', 'in_cross_collateral_pool': True, 'apr': 2.2455714285714286},
    {'currency': 'HYPE', 'in_cross_collateral_pool': True, 'apr': 0.0},
    {'currency': 'XLM', 'in_cross_collateral_pool': False, 'apr': 0.0}]}
DERIBIT_PME = {'result': {'currency': {'btc': {'haircut': 0.0}, 'steth': {'haircut': 0.075}, 'hype': {'haircut': 0.0}}}}


def article(rows, fee='0.05'):
    tr = ''.join('<tr><td><p><span class="bold"><strong>%s</strong></span></p></td><td><p>&#10003;</p></td>'
                 '<td><p>-</p></td><td><p>%s</p></td><td><p>%s</p></td></tr>' % r for r in rows)
    body = ('<p>With cross collateral models ...</p><table frame="border"><thead><tr><th></th><th><p>Cross Collateral '
            'Currency</p></th><th><p>Offset Currency</p></th><th><p>Haircut (X:PM)</p></th><th><p>Haircut (X:SM)</p>'
            '</th></tr></thead><tbody>%s</tbody></table><p>This fee is charged daily in the same currency as the '
            'negative balance (default = %s%% per day).</p>' % (tr, fee))
    return {'article': {'title': 'Cross collateral specifications', 'updated_at': '2026-09-28T14:59:39Z', 'body': body}}


DERIBIT_ARTICLE = article([('BTC', '-', '-'), ('stETH', '7.5%', '7.5%'), ('HYPE', '-', '15%')])


# ---------------------------------------------------------------------------------------------- normalisation

def by_key(rows):
    return {(r['program'], r['asset']): r for r in rows}


def test_norm_hl_reserves_dexes_and_docs():
    rows, ok, checks = C.norm_hl(HL_RESERVES, HL_SPOT_META, HL_DEXES, HL_METAS, HL_DOCS_MD)
    assert ok == {'portfolio_margin': True, 'hip3_collateral': True, 'docs': True}
    k = by_key(rows)
    hype = k[('portfolio_margin', 'HYPE')]
    assert hype['ratio'] == 0.65 and hype['haircut'] == 0.35 and hype['borrow_apr'] == 0.05
    assert hype['extra']['role'] == 'collateral' and hype['extra']['docs_caps'] == {'global_supply': 25e6,
                                                                                    'user_supply': 1e6}
    ubtc = k[('portfolio_margin', 'UBTC')]
    assert ubtc['ratio'] == 0.5 and ubtc['extra']['docs_caps'] == {'global_supply': 5000.0, 'user_supply': 200.0}
    assert k[('portfolio_margin', 'USDC')]['extra']['role'] == 'borrowable'
    assert k[('portfolio_margin', 'USDC')]['extra']['docs_caps']['user_borrow'] == 50e6
    assert k[('hip3_collateral', 'main')]['collateral_token'] == 'USDC'
    hy = k[('hip3_collateral', 'hyna')]
    assert hy['collateral_token'] == 'USDE' and hy['extra']['borrowable'] is False and hy['extra']['n_live'] == 0
    assert k[('hip3_collateral', 'main')]['extra']['n_live'] == 2
    page = k[('docs', 'docs:page')]
    assert page['extra']['ltv'] == {'HYPE': 0.65, 'BTC': 0.5}
    assert page['extra']['borrow_rate_formula'] == '0.05 + 4.75 * max(0, utilization - 0.8)'
    assert page['extra']['liquidation_threshold'] == '0.5 + 0.5 * LTV(token)'
    assert len(page['extra']['requirements']) == 2
    # the '#' line inside the code block is not a section
    assert {a for p, a in k if p == 'docs'} == {'docs:page', 'docs:portfolio-margin', 'docs:ltv-and-borrowing',
                                                'docs:liquidations'}
    assert checks['docs_ltv_mismatch'] == [] and checks['docs_assets_without_reserve'] == []


def test_norm_hl_marks_incomplete_programs():
    metas = {'': HL_METAS['']}                       # two dexes' meta calls failed
    rows, ok, _ = C.norm_hl(None, HL_SPOT_META, HL_DEXES, metas, None)
    assert ok == {'portfolio_margin': False, 'hip3_collateral': False, 'docs': False}
    assert [r['asset'] for r in rows] == ['main']


def test_docs_section_hashes_move_only_where_the_text_moved():
    a = C.parse_hl_docs(HL_DOCS_MD)
    b = C.parse_hl_docs(HL_DOCS_MD.replace('HYPE has an LTV of 0.65', 'HYPE has an LTV of 0.7'))
    ha = {s['slug']: s['hash'] for s in a['sections']}
    hb = {s['slug']: s['hash'] for s in b['sections']}
    assert ha['ltv-and-borrowing'] != hb['ltv-and-borrowing'] and b['ltv']['HYPE'] == 0.7
    assert ha['portfolio-margin'] == hb['portfolio-margin'] and ha['liquidations'] == hb['liquidations']
    assert a['page_hash'] != b['page_hash']
    c = C.parse_hl_docs(HL_DOCS_MD.replace('Under portfolio margin, a', 'Under  portfolio\nmargin, a'))
    assert c['page_hash'] == a['page_hash']                    # whitespace is not a change


def test_norm_binance_programs():
    rows, ok = C.norm_binance(BN_PM, BN_PRO, BN_VIP, BN_ASSET_INDEX, BN_FUT_ASSETS)
    assert ok == {'portfolio_margin': True, 'portfolio_margin_pro': True, 'multi_assets': True}
    k = by_key(rows)
    assert ('portfolio_margin', 'BTCDOM') not in k and ('portfolio_margin', 'XMR') not in k   # virtual, zero
    assert k[('portfolio_margin', 'BTC')]['ratio'] == 0.95
    assert k[('portfolio_margin', 'BTC')]['borrow_apr'] == pytest.approx(0.00001184 * 365)
    ts = k[('portfolio_margin', 'TSLAB')]
    assert ts['extra']['stock_token'] is True and ts['extra']['tiered_liquidation_ratio'][-1] == [5000.0, None, 0.1]
    pro = k[('portfolio_margin_pro', 'BTC')]
    assert pro['tiers'] == [[0.0, 30e6, 1.0], [30e6, 50e6, 0.975], [50e6, None, 0.95]] and pro['ratio'] == 1.0
    assert pro['tier_unit'] == 'usd'
    assert k[('multi_assets', 'BTC')]['ratio'] == pytest.approx(0.95)
    assert k[('multi_assets', 'USDT')]['ratio'] == pytest.approx(0.9999)
    assert ('multi_assets', 'SOL') not in k                      # indexed, but not margin-available
    assert k[('portfolio_margin', 'USDT')]['borrow_apr'] == pytest.approx(0.00013102 * 365)


def test_norm_okx_tiers_in_units_and_exclusions():
    rows, ok = C.norm_okx(OKX_DISC, OKX_LOAN)
    assert ok == {'multi_currency_margin': True}
    assert [r['asset'] for r in rows] == ['BTC']               # AERO has no tiers, LOCKED is restricted
    r = rows[0]
    assert r['tiers'] == [[0.0, 20.0, 0.98], [20.0, 25.0, 0.9775], [25.0, None, 0.5]] and r['ratio'] == 0.98
    assert r['tier_unit'] == 'qty' and r['borrow_apr'] == pytest.approx(0.00001392 * 365)
    assert r['extra']['interest_free_quota'] == 0.23


def test_large_tier_bounds_of_tiny_coins_are_not_the_sentinel():
    """OKX and Bybit state memecoin tiers in coin units above 1e11 (PEPE 1.23e11, SATS 3.2e11); only all-nines bounds
    mean 'no limit'. Reading them as open-ended double-counted tiers (a collateral ratio of 3.86 for SATS)."""
    disc = {'code': '0', 'data': [{'ccy': 'SATS', 'amt': '0', 'collateralRestrict': False, 'details': [
        {'discountRate': '0.8', 'maxAmt': '320000000000', 'minAmt': '0', 'tier': '1'},
        {'discountRate': '0.7', 'maxAmt': '520000000000', 'minAmt': '320000000000', 'tier': '2'},
        {'discountRate': '0.6', 'maxAmt': '850000000000', 'minAmt': '520000000000', 'tier': '3'}]}]}
    rows, _ = C.norm_okx(disc, None)
    assert rows[0]['tiers'] == [[0.0, 3.2e11, 0.8], [3.2e11, 5.2e11, 0.7], [5.2e11, 8.5e11, 0.6]]
    size = 1e6 / 1.2032e-08                                      # $1M of SATS: 8.3e13 coins, beyond the last tier
    assert C.ratio_at(rows[0]['tiers'], size) == pytest.approx((3.2e11 * 0.8 + 2e11 * 0.7 + 3.3e11 * 0.6) / size)
    assert C.ratio_at(rows[0]['tiers'], 1e11) == pytest.approx(0.8)
    coll = {'retCode': 0, 'result': {'list': [{'currency': 'SATS', 'collateralRatioList': [
        {'minQty': '0', 'maxQty': '1080000000000', 'collateralRatio': '0.7'},
        {'minQty': '1080000000000', 'maxQty': '9999999999999', 'collateralRatio': '0.5'},
        {'minQty': '9999999999999', 'maxQty': '', 'collateralRatio': '0'}]}]}}
    rows, _ = C.norm_bybit(coll, None)
    assert rows[0]['tiers'] == [[0.0, 1.08e12, 0.7], [1.08e12, None, 0.5]]
    assert C.sentinel(99999999999.0) and C.sentinel(999999999999999.0) and not C.sentinel(123000000000.0)
    # overlapping tiers (two open-ended) can never push the ratio above the best tier
    assert C.ratio_at([[0, None, 0.8], [100, None, 0.7]], 1000) == pytest.approx((100 * 0.8 + 900 * 0.7) / 1000)


def test_norm_bybit_tiers_and_flags():
    rows, ok = C.norm_bybit(BY_COLL, BY_VIP)
    assert ok == {'uta': True}
    k = by_key(rows)
    assert set(a for _, a in k) == {'HYPE', 'BTC'}             # NOPE is not margin collateral
    h = k[('uta', 'HYPE')]
    assert h['tiers'] == [[0.0, 7700.0, 0.8], [7700.0, None, 0.3]] and h['ratio'] == 0.8   # sentinel tier dropped
    assert h['borrow_apr'] == pytest.approx(0.000007360261 * 8760)
    assert h['extra']['vip_collateral_ratio_deprecated'] == 0.6
    assert k[('uta', 'BTC')]['tiers'] == [[0.0, None, 0.98]]


def test_norm_deribit_pool_haircuts_and_article():
    rows, ok, checks = C.norm_deribit(DERIBIT_CURRENCIES, DERIBIT_PME, DERIBIT_ARTICLE)
    assert ok == {'cross_collateral': True, 'docs': True}
    k = by_key(rows)
    assert ('cross_collateral', 'XLM') not in k
    assert k[('cross_collateral', 'HYPE')]['ratio'] == pytest.approx(0.85)          # X:SM 15%, X:PM 0
    assert k[('cross_collateral', 'HYPE')]['extra']['haircut_pm'] == 0.0
    st = k[('cross_collateral', 'STETH')]
    assert st['ratio'] == pytest.approx(0.925) and st['extra']['yield_apr'] == pytest.approx(0.022455714285714286)
    assert k[('cross_collateral', 'BTC')]['ratio'] == 1.0
    tab = k[('docs', 'docs:cross-collateral-table')]
    assert tab['extra']['collateral_fee_per_day'] == pytest.approx(0.0005)
    assert tab['extra']['haircuts']['STETH'] == {'cross': True, 'offset': False, 'x_pm': 0.075, 'x_sm': 0.075}
    assert checks['pool_not_in_article'] == [] and checks['article_not_in_pool'] == []
    changed = C.parse_deribit_article(article([('BTC', '-', '-'), ('stETH', '7.5%', '10%'), ('HYPE', '-', '15%')]))
    assert changed['table_hash'] != C.parse_deribit_article(DERIBIT_ARTICLE)['table_hash']


def test_pct_parsing():
    assert C.pct('-') == 0.0 and C.pct('7.5%') == pytest.approx(0.075) and C.pct('15 %') == pytest.approx(0.15)
    assert C.pct('n/a') is None


# ---------------------------------------------------------------------------------------------- diff

def snap(day, rows, ok):
    venues = collections_venues(rows, ok)
    return {'date': day, 'fetched_at': day + 'T00:00:00+00:00', 'venues': venues, 'rows': rows}


def collections_venues(rows, ok):
    v = {}
    for (venue, program), good in ok.items():
        v.setdefault(venue, {'ok': {}, 'errors': [], 'counts': {}, 'checks': {}})['ok'][program] = good
    return v


def base_rows():
    return [C.row('binance', 'portfolio_margin', 'BTC', ratio=0.95),
            C.row('binance', 'portfolio_margin', 'DOGE', ratio=0.8),
            C.row('binance', 'portfolio_margin_pro', 'HYPE', ratio=1.0, tiers=[[0, 8e5, 1.0], [8e5, None, 0.95]],
                  tier_unit='usd'),
            C.row('hyperliquid', 'hip3_collateral', 'flx', collateral_token='USDH'),
            C.row('hyperliquid', 'docs', 'docs:ltv-and-borrowing', hash_='aaaa', title='LTV and borrowing')]


OK_ALL = {('binance', 'portfolio_margin'): True, ('binance', 'portfolio_margin_pro'): True,
          ('hyperliquid', 'hip3_collateral'): True, ('hyperliquid', 'docs'): True}


def write_snap(root, s, plain=False):
    d = Path(root) / s['date']
    d.mkdir(parents=True, exist_ok=True)
    if plain:                                                   # the reader takes either form
        (d / 'collateral.json').write_text(json.dumps(s))
    else:
        C.write_gz(d / C.SNAP_FILE, s)


def test_diff_program_every_event_type():
    old = base_rows()
    new = copy.deepcopy(old)
    new[0]['ratio'], new[0]['haircut'] = 0.9, 0.1                                     # BTC haircut 5% -> 10%
    del new[1]                                                                        # DOGE removed
    new.append(C.row('binance', 'portfolio_margin', 'HYPE', ratio=0.7))               # HYPE added
    new[1]['tiers'] = [[0, 1e6, 1.0], [1e6, None, 0.9]]                               # Pro tiers moved
    new[2]['collateral_token'] = 'USDC'                                               # dex switched collateral
    new[3]['hash'] = 'bbbb'                                                           # docs section edited
    ev = []
    for venue, program in OK_ALL:
        o = [r for r in old if r['venue'] == venue and r['program'] == program]
        n = [r for r in new if r['venue'] == venue and r['program'] == program]
        ev += C.diff_program(o, n, venue, program, '2026-10-11', '2026-10-12', 'now')
    got = {(e['event'], e['asset']): e for e in ev}
    assert set(got) == {('ratio_changed', 'BTC'), ('removed', 'DOGE'), ('added', 'HYPE'), ('tiers_changed', 'HYPE'),
                        ('collateral_token_changed', 'flx'), ('docs_hash_changed', 'docs:ltv-and-borrowing')}
    e = got[('ratio_changed', 'BTC')]
    assert (e['old'], e['new'], e['detail']['haircut']) == (0.95, 0.9, [0.05, 0.1])
    assert (e['old_date'], e['new_date'], e['venue'], e['program']) == ('2026-10-11', '2026-10-12', 'binance',
                                                                        'portfolio_margin')
    assert got[('added', 'HYPE')]['new'] == {'ratio': 0.7, 'haircut': 0.3} and got[('added', 'HYPE')]['old'] is None
    assert got[('removed', 'DOGE')]['old']['ratio'] == 0.8 and got[('removed', 'DOGE')]['new'] is None
    assert (got[('collateral_token_changed', 'flx')]['old'], got[('collateral_token_changed', 'flx')]['new']) == \
        ('USDH', 'USDC')
    assert got[('docs_hash_changed', 'docs:ltv-and-borrowing')]['new'] == 'bbbb'


def test_diff_unchanged_is_silent_and_float_noise_ignored():
    old = base_rows()
    new = copy.deepcopy(old)
    new[0]['ratio'] = 0.95 + 1e-12
    for venue, program in OK_ALL:
        o = [r for r in old if r['venue'] == venue and r['program'] == program]
        n = [r for r in new if r['venue'] == venue and r['program'] == program]
        assert C.diff_program(o, n, venue, program, 'a', 'b', 'now') == []


def test_diff_snapshots_baseline_then_changes_then_no_duplicates(tmp_path):
    watch, events = tmp_path / 'watch', tmp_path / 'events.jsonl'
    write_snap(watch, snap('2026-10-11', base_rows(), OK_ALL), plain=True)
    day, ev, compared = C.diff_snapshots(watch, at='t1')
    assert day == '2026-10-11' and compared == []
    assert sorted((e['venue'], e['program']) for e in ev) == sorted(OK_ALL)
    assert all(e['event'] == 'baseline' and e['old_date'] is None for e in ev)
    assert len(C.append_events(events, ev)) == 4
    new = base_rows()
    new[0]['ratio'], new[0]['haircut'] = 0.9, 0.1
    write_snap(watch, snap('2026-10-12', new, OK_ALL))
    day, ev, compared = C.diff_snapshots(watch, at='t2')
    assert [(e['event'], e['asset'], e['old_date'], e['new_date']) for e in ev] == \
        [('ratio_changed', 'BTC', '2026-10-11', '2026-10-12')]
    assert len(C.append_events(events, ev)) == 1
    _, ev2, _ = C.diff_snapshots(watch, at='t3')                       # a rerun appends nothing
    assert C.append_events(events, ev2) == []
    lines = [json.loads(x) for x in events.read_text().splitlines()]
    assert len(lines) == 5 and lines[-1]['event'] == 'ratio_changed'


def test_snapshot_from_raw_rebuilds_the_table_without_fetching(tmp_path):
    raw = tmp_path / 'watch' / '2026-10-11' / 'raw'
    raw.mkdir(parents=True)
    C.write_gz(raw / 'okx_discount_rate_interest_free_quota.json.gz', OKX_DISC)
    C.write_gz(raw / 'okx_interest_rate_loan_quota.json.gz', OKX_LOAN)
    C.write_gz(raw / 'bybit_spot_margin_collateral.json.gz', {'_http_error': 503})     # a failed fetch, as saved
    args = type('A', (), {'day': '2026-10-11', 'watch': str(tmp_path / 'watch'), 'venues': 'okx,bybit,deribit',
                          'from_raw': True})()
    snap = C.cmd_snapshot(args)
    assert [r['asset'] for r in snap['rows']] == ['BTC']
    assert snap['venues']['okx']['ok'] == {'multi_currency_margin': True}
    assert snap['venues']['bybit']['ok'] == {'uta': False}                           # no rows, marked incomplete
    assert 'deribit' not in snap['venues']                                           # nothing saved for it
    assert C.load_snapshot(args.watch, '2026-10-11')['rows'][0]['tiers'][0] == [0.0, 20.0, 0.98]


def test_diff_skips_a_failed_program_and_compares_with_the_last_good_one(tmp_path):
    watch = tmp_path / 'watch'
    write_snap(watch, snap('2026-10-11', base_rows(), OK_ALL))
    bad_ok = dict(OK_ALL)
    bad_ok[('binance', 'portfolio_margin')] = False                    # the endpoint failed on the 12th
    rows12 = [r for r in base_rows() if r['program'] != 'portfolio_margin']
    write_snap(watch, snap('2026-10-12', rows12, bad_ok))
    _, ev, _ = C.diff_snapshots(watch, at='t')
    assert ev == []                                                    # no false 'removed' for every asset
    rows13 = base_rows()
    rows13.append(C.row('binance', 'portfolio_margin', 'ENA', ratio=0.6))
    write_snap(watch, snap('2026-10-13', rows13, OK_ALL))
    _, ev, compared = C.diff_snapshots(watch, at='t')
    assert [(e['event'], e['asset'], e['old_date']) for e in ev] == [('added', 'ENA', '2026-10-11')]
    assert ('binance', 'portfolio_margin', '2026-10-11') in compared


# ---------------------------------------------------------------------------------------------- funding arithmetic

def test_floor_share_hourly_hyperliquid():
    end = 1_791_676_800_000
    ev = [(end - k * HOUR, 0.0000125 if k % 3 else 0.0001) for k in range(0, 31 * 24)]
    w = C.window_stats(ev, end, 30, C.INTEREST_8H, fixed_interval_h=1)
    assert w['n'] == 720 and w['floor_rate'] == pytest.approx(0.0000125)
    assert w['floor_share'] == pytest.approx(480 / 720)
    assert w['apr'] == pytest.approx((480 * 0.0000125 + 240 * 0.0001) * 365 / 30)
    flat = C.window_stats([(t, 0.0000125) for t, _ in ev], end, 30, C.INTEREST_8H, fixed_interval_h=1)
    assert flat['apr'] == pytest.approx(0.1095) and flat['floor_share'] == 1.0         # 10.95% a year at the floor


@pytest.mark.parametrize('hours,floor', [(8, 0.0001), (4, 0.00005), (1, 0.0000125)])
def test_floor_scales_with_the_settlement_interval(hours, floor):
    end = 1_791_676_800_000 + 1                                   # venues stamp a millisecond after the hour
    ev = [(end - k * hours * HOUR, floor if k % 4 else -0.0002) for k in range(0, 31 * 24 // hours + 1)]
    w = C.window_stats(ev, end, 30, C.INTEREST_8H)
    n = 30 * 24 // hours
    assert w['n'] == n and w['interval_h'] == hours and w['floor_rate'] == pytest.approx(floor)
    at = sum(1 for k in range(n) if k % 4)
    assert w['floor_share'] == pytest.approx(at / n)
    assert w['neg_share'] == pytest.approx((n - at) / n)
    assert w['apr'] == pytest.approx(sum(r for t, r in ev if end - 30 * DAY < t <= end) * 365 / 30)


def test_floor_follows_an_interval_switch_inside_the_window():
    end = 1_791_676_800_000
    t8 = [end - 30 * DAY + k * 8 * HOUR for k in range(0, 45)]                 # 15 days at 8 h
    t4 = [t8[-1] + k * 4 * HOUR for k in range(1, 91)]                        # then 15 days at 4 h
    ev = [(t, 0.0001) for t in t8] + [(t, 0.00005) for t in t4]
    w = C.window_stats(ev, end, 30, C.INTEREST_8H)
    assert w['floor_share'] == pytest.approx(1.0) and w['interval_h'] == 4
    assert w['apr'] == pytest.approx(0.1095, rel=1e-3)


def test_zero_interest_venues_and_young_markets():
    end = 1_791_676_800_000
    ev = [(end - k * HOUR, 0.0 if k % 2 else 3e-6) for k in range(0, 10 * 24)]   # 10 days of a 30-day window
    w = C.window_stats(ev, end, 30, 0.0, fixed_interval_h=1)
    assert w['floor_rate'] == 0.0 and w['floor_share'] == pytest.approx(0.5)
    assert w['coverage'] == pytest.approx(10 / 30)
    assert w['apr'] == pytest.approx(120 * 3e-6 * 365 / 10)                   # annualised over the days it covers
    assert C.window_stats([], end, 30, 0.0)['n'] == 0


def test_millisecond_jitter_does_not_inflate_the_apr():
    """Hourly stamps a few ms after the hour can put 721 settlements in a 30-day window; each is one hour's payment,
    so the APR stays the per-settlement mean x 8760."""
    end = 1_791_676_800_018
    ev = [(end - k * HOUR + (45 if k == 720 else 0), 0.0000125) for k in range(0, 722)]
    w = C.window_stats(ev, end, 30, C.INTEREST_8H, fixed_interval_h=1)
    assert w['n'] == 721 and w['apr'] == pytest.approx(0.1095) and w['floor_share'] == 1.0


def test_modal_rate_is_checked_against_each_settlements_own_leg():
    end = 1_791_676_800_000
    t4 = [end - 30 * DAY + k * 4 * HOUR for k in range(1, 151)]              # 25 days at 4 h, mostly at 0.005%
    t8 = [t4[-1] + k * 8 * HOUR for k in range(1, 16)]                       # then 5 days at 8 h
    ev = [(t, 0.00005) for t in t4] + [(t, 0.0002) for t in t8]
    w = C.window_stats(ev, end, 30, C.INTEREST_8H)
    assert w['interval_h'] == 8 and w['floor_rate'] == pytest.approx(0.0001)
    assert w['modal_rate'] == pytest.approx(0.00005) and w['modal_is_floor'] is True
    assert w['floor_share'] == pytest.approx(150 / 165)


def test_capital_excess_and_tiers():
    assert C.capital_per_short(0.95, 0.1) == 1.0
    assert C.capital_per_short(0.5, 0.1) == 1.0                    # 0.5 x 1.5 = 0.75 >= 0.6
    assert C.capital_per_short(0.1, 0.1) == pytest.approx(1.45)    # 0.6 - 0.15 extra cash
    assert C.capital_per_short(0.0, 0.1) is None and C.capital_per_short(None, 0.1) is None
    assert C.capital_per_short(0.5, 0.1, rally=1.0) == pytest.approx(1.1)
    assert C.excess_on_capital(0.1095, 1.0, bench=0.038) == pytest.approx(0.0715)
    assert C.excess_on_capital(0.1095, 1.45, bench=0.038) == pytest.approx(0.1095 / 1.45 - 0.038)
    assert C.excess_on_capital(0.1095, 1.0, borrow_cost=0.005, collateral_yield=0.02, bench=0.038) == \
        pytest.approx(0.1095 - 0.005 + 0.02 - 0.038)
    velo = [[0, 5e4, 1.0], [5e4, 1e5, 0.8], [1e5, 2e5, 0.5], [2e5, 4e5, 0.2], [4e5, None, 0.1]]
    assert C.ratio_at(velo, 1e6) == pytest.approx((5e4 + 4e4 + 5e4 + 4e4 + 6e4) / 1e6)
    assert C.ratio_at([[0, 20, 0.98], [20, 25, 0.9775]], 30) == pytest.approx((20 * 0.98 + 5 * 0.9775) / 30)
    assert C.ratio_at(velo, 0) == 1.0 and C.ratio_at(None, 5) is None


def test_match_perp_kinds():
    perps = {'BTCUSDT': {'base': 'BTC', 'kind': 'coin'}, 'BTCUSDC': {'base': 'BTC', 'kind': 'coin'},
             '1000PEPEUSDT': {'base': '1000PEPE', 'kind': 'coin'}, 'TSLAUSDT': {'base': 'TSLA', 'kind': 'tradfi'},
             'QNTUSDT': {'base': 'QNT', 'kind': 'coin'}, 'ETHUSDT': {'base': 'ETH', 'kind': 'coin'},
             'kBONK': {'base': 'kBONK', 'kind': 'coin'}}
    bb = C.by_base_of(perps, lambda p: 0)
    bb['BTC'] = ['BTCUSDT', 'BTCUSDC']
    assert C.match_perp('BTC', bb, perps) == ('BTCUSDT', 'direct', 1.0, 'BTC')
    assert C.match_perp('PEPE', bb, perps) == ('1000PEPEUSDT', 'multiplier', 1e3, 'PEPE')
    assert C.match_perp('BONK', bb, perps) == ('kBONK', 'multiplier', 1e3, 'BONK')
    assert C.match_perp('TSLAB', bb, perps, stock=True) == ('TSLAUSDT', 'stock token', 1.0, 'TSLA')
    assert C.match_perp('QNTB', bb, perps, stock=True) is None       # a stock token never maps to a crypto perp
    assert C.match_perp('TSLA', bb, perps) is None                   # and a crypto asset never to a TradFi perp
    assert C.match_perp('UBTC', bb, perps) == ('BTCUSDT', 'wrapped', 1.0, 'BTC')
    assert C.match_perp('WBETH', bb, perps) == ('ETHUSDT', 'staking token', 1.0, 'ETH')
    assert C.match_perp('USDC', bb, perps) is None


def test_identity_bounds():
    assert C.identity(0.0000052, 0.0052, 1e3, 'multiplier')[1] is True
    assert C.identity(100.0, 150.0, 1.0, 'direct')[1] is False
    assert C.identity(2700.0, 2500.0, 1.0, 'staking token')[1] is True      # WBETH worth more than ETH
    assert C.identity(None, 2500.0, 1.0, 'direct') == (None, None)


def test_depth_within_band_on_the_taking_side():
    d = C.book_depth([(99.9, 10.0), (99.0, 100.0)], [(100.1, 5.0), (100.5, 50.0)])
    assert d['mid'] == pytest.approx(100.0)
    assert d['ask_usd'] == pytest.approx(100.1 * 5.0 + 100.5 * 50.0 * 0)          # 100.5 is 50bp away
    assert d['bid_usd'] == pytest.approx(99.9 * 10.0)
