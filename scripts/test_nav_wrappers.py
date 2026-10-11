"""Core math of nav_wrappers: look-through NAV with debt / preferred / convertibles, the three mNAV ratios, hedge
accounting of a discount trade, split bases of restated XBRL comparatives, fee interpolation, the XBRL capital rule,
event windows and the trust rule's entry/exit logic. Synthetic data only; no network."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nav_wrappers as N  # noqa: E402


# ---------------------------------------------------------------- look-through NAV and the three ratios

def test_lookthrough_nav_subtracts_debt_and_preferred():
    nav, ds, eq = N.lookthrough_nav(coins=100.0, price=50_000.0, cash=1e6, debt=2e6, pref=1e6, shares=1e6)
    assert eq == pytest.approx(5e6 + 1e6 - 2e6 - 1e6)
    assert ds == 1e6
    assert nav == pytest.approx(3.0)


def test_convertible_is_debt_out_of_the_money_and_shares_in_the_money():
    # $10M face converting at $20/share
    nav_otm, ds_otm, _ = N.lookthrough_nav(1000.0, 10_000.0, shares=1e6, converts=[(10e6, 20.0)], stock_price=15.0)
    assert ds_otm == 1e6
    assert nav_otm == pytest.approx((10e6 - 10e6) / 1e6)
    nav_itm, ds_itm, _ = N.lookthrough_nav(1000.0, 10_000.0, shares=1e6, converts=[(10e6, 20.0)], stock_price=25.0)
    assert ds_itm == pytest.approx(1e6 + 10e6 / 20.0)
    assert nav_itm == pytest.approx(10e6 / 1.5e6)
    # never both: debt removed when converted
    assert nav_itm > nav_otm


def test_mnav_variants_mstr_like_gap():
    # coins worth 70, market cap 65, debt 6.7, preferred 13.9, cash 5.7 (in $B, per share basis 1 share)
    v = N.mnav_variants(price=65.0, shares=1.0, coins=1.0, coin_price=70.0, cash=5.7, debt=6.7, pref=13.9)
    assert v['naive'] == pytest.approx(65 / 70)
    assert v['ev'] == pytest.approx((65 + 6.7 + 13.9 - 5.7) / 70)
    assert v['true'] == pytest.approx(65 / (70 + 5.7 - 6.7 - 13.9))
    assert v['naive'] < 1 < v['true']                 # a dashboard "discount" that is a premium


def test_mnav_negative_equity_flagged():
    v = N.mnav_variants(price=1.0, shares=1.0, coins=1.0, coin_price=10.0, debt=12.0)
    assert v['negative_equity'] and v['true'] is None


# ---------------------------------------------------------------- hedge accounting

def _flat_funding(n):
    return [0.0] * n


def test_nav_hedge_captures_discount_at_convergence_with_flat_coin():
    prices = [70.0, 100.0]              # trust closes from a 30% discount to NAV
    coin = [100.0, 100.0]
    cps = [1.0, 1.0]
    r = N.hedged_path(prices, coin, cps, _flat_funding(2), 0, 1, margin=1 / 3, perp_fee=0.0)
    n0 = (1 / 70.0) * 1.0 * 100.0      # coin notional short per $ of trust
    assert r['capital'] == pytest.approx(1 + n0 / 3)
    assert r['total'] == pytest.approx((100 / 70 - 1) / r['capital'])


def test_nav_hedge_is_net_short_the_discount_while_it_persists():
    # constant 30% discount, coin +50%: NAV hedge P&L = d1 * coin return / (1 + d0) per $ of trust
    prices = [70.0, 105.0]
    coin = [100.0, 150.0]
    r = N.hedged_path(prices, coin, [1.0, 1.0], _flat_funding(2), 0, 1, margin=0.0, perp_fee=0.0)
    assert r['total'] == pytest.approx((-0.30 * 0.5) / 0.70)
    # dollar hedge (hedge units = price / coin price) is flat when the discount is constant
    hu = [p / c for p, c in zip(prices, coin)]
    r2 = N.hedged_path(prices, coin, hu, _flat_funding(2), 0, 1, margin=0.0, perp_fee=0.0)
    assert r2['total'] == pytest.approx(0.0, abs=1e-12)


def test_short_receives_positive_funding_and_pays_costs():
    prices, coin, cps = [100.0, 100.0], [100.0, 100.0], [1.0, 1.0]
    r = N.hedged_path(prices, coin, cps, [0.0, 0.001], 0, 1, margin=0.0, cost_in=0.01, cost_out=0.01, perp_fee=0.0005)
    # +0.1% funding on $1 short, minus 1% + 1% wrapper costs, minus 2 x 5bp perp
    assert r['total'] == pytest.approx(0.001 - 0.01 - 0.01 - 0.0005 - 0.0005)


def test_distribution_is_credited_to_the_holder():
    # a 10% coin distribution: price and coin per share drop 10%, holder receives the coin value
    prices, coin, cps = [100.0, 90.0], [100.0, 100.0], [1.0, 0.9]
    r = N.hedged_path(prices, coin, cps, [0.0, 0.0], 0, 1, margin=0.0, perp_fee=0.0, dist=[0.0, 10.0])
    assert r['total'] == pytest.approx(0.0, abs=1e-12)


def test_excess_over_savings_rate_uses_calendar_gap():
    prices, coin = [100.0, 100.0, 100.0], [1.0, 1.0, 1.0]
    dates = ['2024-01-05', '2024-01-08', '2024-01-09']        # Friday -> Monday is 3 days
    r = N.hedged_path(prices, coin, [0.0] * 3, [0.0] * 3, 0, 2, margin=0.0, perp_fee=0.0,
                      ssr=lambda d: 0.0365, dates=dates)
    assert r['excess_total'] == pytest.approx(-0.0365 * 4 / 365.0)


# ---------------------------------------------------------------- split bases, fees, interpolation

def test_split_factor_after():
    splits = [('2018-01-29', 91.0), ('2026-02-06', 0.05)]
    assert N.split_factor_after('2017-12-31', splits) == pytest.approx(91 * 0.05)
    assert N.split_factor_after('2020-01-01', splits) == pytest.approx(0.05)
    assert N.split_factor_after('2026-03-01', splits) == 1.0


def test_fix_split_basis_handles_restated_comparatives():
    # latest filing after the split: values already post-split; an old period restated (post-split) and one
    # original pre-split value both resolve to the same continuous path
    fee = 0.02
    true_cps = lambda days_back: 0.001 * math.exp(fee * days_back / 365.25)
    raw = [('2017-09-30', true_cps(1000) * 91, '2017-11-01'),      # original pre-split filing
           ('2017-12-31', true_cps(900), '2021-03-05'),            # restated in a later filing
           ('2020-06-30', true_cps(0), '2020-08-07')]
    fixed = N.fix_split_basis([(a, v, f) for a, v, f in raw], [('2018-01-29', 91.0)], fee)
    assert fixed[0][1] == pytest.approx(true_cps(1000))
    assert fixed[1][1] == pytest.approx(true_cps(900))
    assert fixed[2][1] == pytest.approx(true_cps(0))


def test_interp_log_between_and_beyond_anchors():
    anchors = [('2024-01-01', 1.0), ('2025-01-01', 0.98)]
    mid = N.interp_log(anchors, '2024-07-01', 0.02)
    assert 0.98 < mid < 1.0
    assert N.interp_log(anchors, '2026-01-01', 0.02) == pytest.approx(0.98 * math.exp(-0.02 * 365 / 365.25))
    assert N.interp_log(anchors, '2023-01-01', 0.02) == pytest.approx(1.0 * math.exp(0.02 * 365 / 365.25))


# ---------------------------------------------------------------- XBRL rules

def test_capital_rule_takes_largest_total_debt_not_the_sum():
    end = '2026-06-30'
    tv = {'LongTermDebt': {end: {'val': 100.0}},
          'LongTermDebtNoncurrent': {end: {'val': 60.0}}, 'LongTermDebtCurrent': {end: {'val': 40.0}},
          'ConvertibleLongTermNotesPayable': {end: {'val': 90.0}},
          'ShortTermBorrowings': {end: {'val': 5.0}},
          'CashAndCashEquivalentsAtCarryingValue': {end: {'val': 7.0}},
          'TemporaryEquityCarryingAmountAttributableToParent': {end: {'val': 2e6}},
          'PreferredStockValue': {end: {'val': 10.0}}}
    c = N.capital_from_xbrl(None, end, tv)
    assert c['debt'] == pytest.approx(100.0 + 5.0)
    assert c['cash'] == 7.0
    assert c['pref'] == 2e6
    tv2 = {'PreferredStockValue': {end: {'val': 524.0}}}
    assert N.capital_from_xbrl(None, end, tv2)['pref'] == 0.0      # par-value noise ignored


def test_xbrl_original_keeps_the_first_filing_of_each_period():
    facts = {'facts': {'us-gaap': {'X': {'units': {'shares': [
        {'end': '2025-06-30', 'val': 10, 'filed': '2026-02-01', 'form': '10-K'},
        {'end': '2025-06-30', 'val': 200, 'filed': '2025-08-10', 'form': '10-Q'},
        {'end': '2025-06-30', 'start': '2025-04-01', 'val': 1, 'filed': '2025-08-09', 'form': '10-Q'}]}}}}}
    out = N.xbrl_original(facts, 'X')
    assert out['2025-06-30']['val'] == 200


# ---------------------------------------------------------------- event windows and rules

def _series(discs, nav=100.0, coin=100.0):
    rows = []
    for i, d in enumerate(discs):
        date = '2024-01-%02d' % (i + 1)
        rows.append({'date': date, 'close': nav * (1 + d), 'high': nav * (1 + d), 'low': nav * (1 + d),
                     'dollar_volume': 5e7, 'coin_px': coin, 'cps': nav / coin, 'nav': nav, 'disc': d, 'funding': 0.0,
                     'dist_cash': 0.0})
    return {'ticker': 'TST', 'coin': 'BTC', 'rows': rows}


def test_event_trade_windows_and_late_entry():
    ts = _series([-0.30, -0.30, -0.20, -0.10, 0.0])
    base = N.event_trade(ts, '2024-01-01', '2024-01-05', margin=0.0, perp_fee=0.0)
    late = N.event_trade(ts, '2024-01-01', '2024-01-05', margin=0.0, perp_fee=0.0, skip=2)
    assert base['entry'] == '2024-01-01' and base['exit'] == '2024-01-05'
    assert late['entry'] == '2024-01-03'
    # 5bp floor per side on liquid names; the exit cost is charged on the exit notional (1/70 x 100)
    gross = 100 / 70 - 1 - 0.0005 - 0.0005 * 100 / 70
    assert base['return_on_capital'] == pytest.approx(gross, rel=1e-6)
    assert late['return_on_capital'] < base['return_on_capital']


def test_rule_backtest_enters_below_trigger_and_exits_above_half():
    ts = _series([-0.02, -0.12, -0.12, -0.04, -0.04])
    events = [{'ticker': 'TST', 'filing_public': '2024-01-01', 'listed': None}]
    out, log = N.rule_backtest({'TST': ts}, events, 0.10, True, margin=0.0, perp_fee=0.0)
    assert log[0]['entry'] == '2024-01-02' and log[0]['exit'] == '2024-01-04'
    # held over 01-03 (flat) and 01-04 (discount -12% -> -4%): excess on those days, zero elsewhere
    assert out['2024-01-01'] == 0.0 and out['2024-01-05'] == 0.0
    assert out['2024-01-04'] > 0


def test_dat_forward_beta_hedge_is_neutral_at_constant_true_mnav():
    # levered DAT: coins 2 per share, debt 100 per share; true mNAV held at 0.8 while the coin rises 10%
    rows = []
    for k, c in enumerate([100.0, 110.0]):
        nav = 2 * c - 100.0
        rows.append({'date': '2025-12-0%d' % (k + 1), 'price': 0.8 * nav, 'coin_px': c, 'cps': 2.0, 'nav': nav,
                     'funding': 0.0, 'adv_usd': 1e9})
    dd = {'rows': rows}
    r = N.dat_forward(dd, 0, 1, hedge='beta', margin=0.0)
    cost = 2 * (0.0005 + 0.0005 * (200 / 100.0))
    assert r == pytest.approx(-cost - N.ssr_for('2025-12-02') / 365.0, abs=1e-9)
    # the asset hedge is net short (1 - m) of the coin value: it loses when the coin rises
    ra = N.dat_forward(dd, 0, 1, hedge='asset', margin=0.0)
    assert ra < r


def test_abdi_ranaldo_zero_for_constant_prices():
    assert N.abdi_ranaldo_spread([10.0] * 5, [10.0] * 5, [10.0] * 5) == 0.0


# ---------------------------------------------------------------- forward test (DATs): registration and scoring

H_MS = 3600000


def _fwd_inputs():
    # 1,000 coins, $20k cash, $40k debt, 1,000 shares: NAV/share = coin - 20; beta = C / (C - 20)
    return {'coins': 1000.0, 'cash_usd': 20_000.0, 'debt_usd': 40_000.0, 'pref_usd': 0.0, 'shares': 1000.0,
            'committed_to_illiquid_usd': 0.0}


def _fwd_rows(prices, coins, perps=None, funding=None, adv=5e6, start='2026-10-12'):
    d0 = N.dt.date.fromisoformat(start)
    out = []
    for i, (p, c) in enumerate(zip(prices, coins)):
        date = (d0 + N.dt.timedelta(days=i)).isoformat()
        out.append({'date': date, 'close_ms': N.session_close_ms(date), 'price': p, 'coin_px': c,
                    'perp_px': (perps or coins)[i], 'funding': (funding or [0.0] * len(prices))[i], 'adv_usd': adv})
    return out


def test_calendar_entry_is_the_first_close_after_registration_and_horizons_count_sessions():
    sat = N.iso_to_ms('2026-10-10T23:24:00+00:00')
    assert N.next_close_after(sat) == ('2026-10-12', N.iso_to_ms('2026-10-12T20:00:00+00:00'))
    s = N.sessions_after('2026-10-12', 60)
    assert (s[19], s[59]) == ('2026-11-09', '2027-01-07')            # Thanksgiving, Christmas, New Year skipped
    assert '2026-11-26' not in s and '2026-11-27' in s
    assert N.utc_iso_ms(N.session_close_ms('2026-11-27')) == '2026-11-27T18:00:00+00:00'   # early close, EST
    assert N.utc_iso_ms(N.session_close_ms('2026-11-09')) == '2026-11-09T21:00:00+00:00'   # after the DST change


def test_frozen_rule_arithmetic_on_synthetic_prices():
    P = N.DAT_FORWARD_PARAMS
    inp = _fwd_inputs()
    # coin flat at 100 (beta 100/80 = 1.25), stock 40 -> 44 over two sessions, funding 0.01% on day 2
    rows = _fwd_rows([40.0, 42.0, 44.0], [100.0, 100.0, 100.0], funding=[0.0, 0.0, 0.0001], adv=5e6)
    tr = N.dat_forward_trade(rows, 0, 2, inp, P)
    h, cap = 1.25, 1.0 + 1.25 / 3
    stock = (42 / 40 - 1) + (44 / 42 - 1)
    sav = 2 * 0.037 / 365.0
    costs = 2 * (0.003 + 0.0005 * h)                                   # $1-10M ADV tier
    assert tr['h0'] == pytest.approx(h) and tr['capital'] == pytest.approx(cap)
    assert tr['excess'] == pytest.approx((stock + h * 0.0001) / cap - sav - costs / cap)
    assert tr['parts']['funding'] == pytest.approx(h * 0.0001 / cap)
    # at constant true mNAV the beta hedge cancels the coin move to first order
    coins = [100.0, 104.0, 99.0]
    flat = N.dat_forward_trade(_fwd_rows([0.5 * (c - 20) for c in coins], coins, adv=5e6), 0, 2, inp, P)
    assert abs(flat['parts']['stock'] + flat['parts']['hedge']) < 2e-3
    # the perp-leg variant marks the hedge on the perp close
    pv = N.dat_forward_trade(_fwd_rows([40.0, 40.0], [100.0, 100.0], perps=[100.0, 101.0]), 0, 1, inp, P, leg='perp_px')
    assert pv['parts']['hedge'] == pytest.approx(-1.25 * 0.01 / cap)
    assert N.dat_forward_trade(rows, 0, 3, inp, P) is None             # runs past the data


def test_session_rows_take_the_hour_ending_at_the_close_and_funding_in_between():
    d1, d2 = '2026-10-12', '2026-10-13'
    T1, T2 = N.session_close_ms(d1), N.session_close_ms(d2)
    coin = {T1 - H_MS: 100.0, T1: 999.0, T2 - H_MS: 110.0}            # keyed by bar open: the 19:00 bar closes at 20:00
    funding = [(T1, 0.5), (T1 + 1, 0.001), (T2, 0.002), (T2 + 1, 9.0)]
    rows = N.dat_session_rows({'dates': [d1, d2], 'close': [10.0, 11.0], 'volume': [100, 300]}, coin, coin, funding)
    assert [r['coin_px'] for r in rows] == [100.0, 110.0]
    assert rows[1]['funding'] == pytest.approx(0.003)                   # (T1, T2]
    assert rows[1]['adv_usd'] == pytest.approx((1000 + 3300) / 2)


class _FakeFetch:
    def __init__(self, raw):
        self.raw = raw

    def yahoo_daily(self, sym, t0, t1):
        return {'dates': ['2026-10-08', '2026-10-09'], 'close': [10.0, 10.0], 'volume': [1e6, 1e6], 'splits': []}

    def hourly(self, coin, a, b, kind='study'):
        T = N.session_close_ms('2026-10-09')
        return {T - H_MS: 100.0}, ('spot:X' if kind == 'study' else 'perp:X')

    def funding(self, coin, a, b):
        return []

    def perp_state(self, symbol):
        return {'symbol': symbol}


def _fwd_analysis():
    live = []
    for tk in N.DAT_FORWARD_NAMES:
        live.append(dict(_fwd_inputs(), ticker=tk, coin='BTC', date='2026-10-09', price_usd=10.0, coin_px=100.0,
                         capital_source='test', holdings_source='test'))
    return {'generated': 'test', 'dats': {'live': live}}


def test_registration_freezes_the_rule_and_the_ledger_is_append_only(tmp_path, monkeypatch):
    led = tmp_path / 'fwd.jsonl'
    sat = N.iso_to_ms('2026-10-10T23:24:00+00:00')
    rows, late = N.dat_forward_register(led, sat, _FakeFetch(tmp_path), _fwd_analysis(), {}, log=lambda *a: None)
    assert len(rows) == len(N.DAT_FORWARD_NAMES) and not late
    r = rows[0]
    assert r['rule_frozen'] == N.DAT_FORWARD_RULE and r['params'] == N.DAT_FORWARD_PARAMS
    assert r['entry_date'] == '2026-10-12' and r['score_dates_expected'] == {'20': '2026-11-09', '60': '2027-01-07'}
    assert r['reference']['date'] == '2026-10-09' and r['at_reference']['hedge_beta'] == pytest.approx(1.25)
    before = led.read_text()
    again, _ = N.dat_forward_register(led, sat + 3600000, _FakeFetch(tmp_path), _fwd_analysis(), {},
                                      log=lambda *a: None)
    assert again == [] and led.read_text() == before                    # never re-registered, never rewritten
    # the registered row carries its own parameters: changing the module's later does not re-score it
    srows = _fwd_rows([10.0] * 25, [100.0] * 25, start='2026-10-12')
    for i, x in enumerate(srows):                                        # sessions only, as Yahoo serves them
        x['date'] = (['2026-10-12'] + N.sessions_after('2026-10-12', 24))[i]
        x['close_ms'] = N.session_close_ms(x['date'])
    now = N.session_close_ms(srows[-1]['date']) + 3600000
    s1 = N.dat_forward_score_row(N.read_jsonl(led)[0], srows, now)
    monkeypatch.setitem(N.DAT_FORWARD_PARAMS, 'margin', 1.0)
    s2 = N.dat_forward_score_row(N.read_jsonl(led)[0], srows, now)
    assert s1['horizons']['20']['excess'] == s2['horizons']['20']['excess']
    assert any(p.startswith('+60: 24 of 60') for p in s1['pending'])


def test_a_row_registered_after_its_entry_is_refused(tmp_path):
    led = tmp_path / 'fwd.jsonl'
    mon_late = N.iso_to_ms('2026-10-12T20:30:00+00:00')
    c = [{'rule': 'r', 'ticker': 'A', 'entry_date': '2026-10-12', 'entry_utc': '2026-10-12T20:00:00+00:00'},
         {'rule': 'r', 'ticker': 'B', 'entry_date': '2026-10-13', 'entry_utc': '2026-10-13T20:00:00+00:00'},
         {'rule': 'r', 'ticker': 'C', 'entry_date': '2026-10-13', 'entry_utc': '2026-10-13T20:00:00+00:00'}]
    new, late = N.dat_forward_registrable(c, [{'rule': 'r', 'ticker': 'C'}], mon_late)
    assert [x['ticker'] for x in new] == ['B'] and [x['ticker'] for x in late] == ['A']
    rows, late = N.dat_forward_register(led, mon_late, _FakeFetch(tmp_path), _fwd_analysis(), {},
                                        entry_date='2026-10-12', log=lambda *a: None)
    assert rows == [] and len(late) == len(N.DAT_FORWARD_NAMES) and not led.exists()


def test_forward_verdict_waits_for_four_candidate_horizons_then_follows_the_criteria():
    def s(tk, role, ex20=None, ex60=None, ch=0.05):
        hz = {}
        if ex20 is not None:
            hz['20'] = {'excess': ex20, 'true_change': ch}
        if ex60 is not None:
            hz['60'] = {'excess': ex60, 'true_change': ch}
        return {'ticker': tk, 'role': role, 'horizons': hz}
    pl = [s('P%d' % i, 'placebo', 0.0, 0.0) for i in range(5)]
    early = N.dat_forward_summary([s('A', 'candidate', 0.05), s('B', 'candidate', 0.02)] + pl)
    assert early['verdict'].startswith('accumulating (2 of 4')
    kill = N.dat_forward_summary([s('A', 'candidate', 0.05, -0.04), s('B', 'candidate', 0.02, 0.01)] + pl)
    assert kill['verdict'].startswith('kill')
    good = N.dat_forward_summary([s('A', 'candidate', 0.05, 0.06), s('B', 'candidate', 0.02, 0.03)] + pl)
    assert good['verdict'].startswith('promote')
    assert good['horizons']['60']['candidates']['A']['over_placebo'] == pytest.approx(0.06)
    mixed = N.dat_forward_summary([s('A', 'candidate', 0.05, 0.08), s('B', 'candidate', 0.02, -0.01)] + pl)
    assert mixed['verdict'].startswith('hold')
