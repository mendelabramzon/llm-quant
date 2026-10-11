#!/usr/bin/env python3
"""Tests for scripts/jlp_forward.py on synthetic snapshots: the net-delta identity and its signs, the P&L conventions (a
pool that moves only with its delta hedges to its fee return), no look-ahead, agreement with house_vaults'
simulator, the verdict thresholds, and the append-only ledger. Run:

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_jlp_forward.py -q
"""
import json
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import house_vaults as H  # noqa: E402
import jlp_forward as F  # noqa: E402

DAY = F.DAY_MS
T0 = H.day_ts('2026-10-11') * 1000 + 3600 * 1000          # 01:00 UTC
SAVED = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research', '2026-10-10', 'house_vaults', 'raw',
                     'jlp', 'jlp_info_2026-10-10.json')
DEC = {'SOL': 9, 'ETH': 8, 'WBTC': 8}
CUST = {'SOL': 'SOL', 'ETH': 'ETH', 'BTC': 'WBTC'}


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# ---------------------------------------------------------------------------------------------------------------------
# synthetic jlp-info
# ---------------------------------------------------------------------------------------------------------------------
def custody(symbol, owned, locked, g, G, avg, p, target=10.0):
    """A jlp-info custody as the API writes it (integer strings), valued at oracle price p."""
    d = DEC[symbol]
    aum = F.custody_aum(owned, locked, g, G, avg, p)
    side = G * (p - avg) / avg if G else 0.0                      # the pool's side of the shorts' P&L
    return {'symbol': symbol, 'owned': str(round(owned * 10 ** d)), 'locked': str(round(locked * 10 ** d)),
            'aumTokenAmount': str(round(owned * 10 ** d)), 'aumTokenAmountFormatted': '%.2f' % owned,
            'guaranteedUsd': str(round(g * 1e6)), 'globalShortSizes': str(round(G * 1e6)),
            'globalShortAveragePrice': str(round(avg * 1e6)), 'shortPnlDelta': str(round(abs(side) * 1e6)),
            'shortTradersHasProfit': side < 0, 'aumUsd': str(round(aum * 1e6)), 'currentWeightagePct': '10.00',
            'targetWeightagePct': '%.2f' % target, 'utilizationPct': '0.00', 'totalStakedAmountLamports': '0'}


def info(prices, state, usdc=3e8, supply=1e8):
    """A pool: state[asset] = (owned, locked, guaranteedUsd, shortSizes, shortAvg), plus USDC; NAV = AUM / supply."""
    cs = [custody(CUST[a], *state[a], prices[a], target={'SOL': 47, 'ETH': 8, 'BTC': 13}[a]) for a in F.ASSETS]
    cs.append({'symbol': 'USDC', 'aumUsd': str(round(usdc * 1e6)), 'currentWeightagePct': '30.00',
               'targetWeightagePct': '30.00'})
    aum = sum(int(c['aumUsd']) for c in cs) / 1e6
    return {'aumUsd': str(round(aum * 1e6)), 'jlpTotalSupply': str(round(supply * 1e6)),
            'jlpPriceUsd': str(round(aum / supply * 1e6)), 'aumLimitUsd': str(3 * 10 ** 15), 'jlpAprPct': '8.00',
            'jlpApyPct': '8.33', 'custodies': cs}


STATE = {  # roughly the 2026-10-10 pool, rounded
    'SOL': (3_939_042.0, 508_347.0, 43_587_081.0, 9_694_216.0, 110.4),
    'ETH': (27_880.0, 1_774.0, 3_614_635.0, 959_331.0, 2_462.9),
    'BTC': (1_482.0, 226.6, 15_366_787.0, 5_245_688.0, 80_820.0),
}
PX0 = {'SOL': 110.0, 'ETH': 2500.0, 'BTC': 83_000.0}


def venue(prices, t, rate=0.0):
    return {a: {'symbol': F.ASSETS[a]['binance'], 'mark': prices[a], 'index': prices[a], 'funding_rate': rate,
                'interval_h': 8, 'funding_ann': rate * 3 * 365, 'next_funding_ms': t + 8 * 3600 * 1000, 'time_ms': t}
            for a in F.ASSETS}


def hl_venue(prices, rate=0.0):
    return {a: {'mark': prices[a], 'oracle': prices[a], 'funding_hourly': rate, 'funding_ann': rate * 8760,
                'premium': 0.0, 'open_interest': 1.0} for a in F.ASSETS}


def make_rows(paths, states=None, usdc=None, rate_bn=0.0, rate_hl=0.0, step=DAY):
    """Daily rows from price paths (a list of {asset: price}), pool states and USDC balances, with Binance funding
    settled every 8 hours at `rate_bn` (each at the period-start mark) and Hyperliquid hourly at `rate_hl`."""
    n = len(paths)
    states = states or [STATE] * n
    usdc = usdc or [3e8] * n
    rows = []
    for i in range(n):
        t = T0 + i * step
        fund = None
        if i:
            t0 = rows[-1]['t_ms']
            fund = {'from_ms': t0, 'to_ms': t,
                    'binance': {a: [[t0 + k * 8 * 3600 * 1000, rate_bn, paths[i - 1][a]] for k in (1, 2, 3)
                                    if t0 + k * 8 * 3600 * 1000 <= t] for a in F.ASSETS},
                    'hyperliquid': {a: [[t0 + k * 3600 * 1000, rate_hl] for k in range(1, 25)
                                        if t0 + k * 3600 * 1000 <= t] for a in F.ASSETS}}
        rows.append(F.build_row(info(paths[i], states[i], usdc[i]), t, venue(paths[i], t), hl_venue(paths[i]), fund,
                                ssr={'apy': 0.038}))
    return rows


# ---------------------------------------------------------------------------------------------------------------------
# the net delta
# ---------------------------------------------------------------------------------------------------------------------
def test_delta_signs_long_and_short():
    # LPs alone: 1,000 tokens, all unclaimed
    lp = (1000.0, 0.0, 0.0, 0.0, 0.0)
    assert F.custody_state(custody('SOL', *lp, 100.0), 9)['delta_tokens'] == pytest.approx(1000.0)
    # a $1M 5x long at $100: owned +2,000 (collateral), locked +10,000, guaranteed +$0.8M -> 8,000 shorter
    lg = (3000.0, 10000.0, 800_000.0, 0.0, 0.0)
    s = F.custody_state(custody('SOL', *lg, 100.0), 9)
    assert s['delta_tokens'] == pytest.approx(1000.0 - 8000.0)
    # the long's claim is collateral + P&L: at $110, 200k + 1M x 10% = 300k = locked x p - guaranteed
    assert F.custody_aum(*lg, 110.0) == pytest.approx(3000 * 110 - 300_000.0)
    # a $1M short at $100 on top: 10,000 longer
    sh = (3000.0, 10000.0, 800_000.0, 1_000_000.0, 100.0)
    assert F.custody_state(custody('SOL', *sh, 100.0), 9)['delta_tokens'] == pytest.approx(-7000.0 + 10000.0)
    # the custody AUM is linear in p with slope delta, on both sides of the shorts' entry
    for p in (80.0, 100.0, 130.0):
        assert F.custody_aum(*sh, p + 1.0) - F.custody_aum(*sh, p) == pytest.approx(3000.0, rel=1e-12)


def test_custody_state_recovers_price_both_ways():
    for p in (95.0, 110.4, 140.0):          # shorts losing, at entry, winning
        c = custody('SOL', *STATE['SOL'], p)
        s = F.custody_state(c, 9)
        assert s['oracle_px'] == pytest.approx(p, rel=1e-8)
        if p != 110.4:
            assert s['oracle_px_short'] == pytest.approx(p, rel=1e-6)
            assert abs(s['identity_resid_usd']) < 50.0
        owned, locked, g, G, avg = STATE['SOL']
        assert s['delta_tokens'] == pytest.approx(owned - locked + G / avg, rel=1e-9)
    with pytest.raises(ValueError):          # a decimals change is caught, not silently mis-scaled
        F.custody_state(custody('SOL', *STATE['SOL'], 110.0), 8)


@pytest.mark.skipif(not os.path.exists(SAVED), reason='house_vaults raw jlp-info not present')
def test_saved_sample_identity():
    J = F.parse_info(H.load_json(SAVED))
    assert J['checks']['oracle_px_two_ways_max_rel'] < 1e-6
    assert J['checks']['identity_resid_max_usd'] < 100.0
    assert abs(J['checks']['price_field_minus_nav']) < 1e-6
    sol = J['custodies']['SOL']
    assert sol['delta_tokens'] == pytest.approx(3_939_042.3125 - 508_347.0797 + 9_694_216.796264 / 110.409766, abs=0.01)
    assert sol['delta_tokens'] * sol['oracle_px'] / J['aum_usd'] == pytest.approx(0.432, abs=0.001)


# ---------------------------------------------------------------------------------------------------------------------
# P&L conventions
# ---------------------------------------------------------------------------------------------------------------------
def test_pool_moving_with_its_delta_hedges_to_the_fee_return(monkeypatch):
    monkeypatch.setattr(F, 'TAKER', {'binance': 0.0, 'hyperliquid': 0.0})
    rng = random.Random(3)
    paths, usdc = [dict(PX0)], [3e8]
    for _ in range(10):
        paths.append({a: p * (1 + rng.uniform(-0.06, 0.06)) for a, p in paths[-1].items()})
        usdc.append(usdc[-1] + 200_000.0)               # fees of $200k a day credited to the pool
    rows = make_rows(paths, usdc=usdc)
    N = F.FORWARD_RULE['jlp_usd'] / rows[0]['jlp']['price']
    tok = [{a: r['delta_per_jlp'][a] * N for a in F.ASSETS} for r in rows]
    sim = F.simulate(rows, tok, N)
    for p in sim:
        assert p['pnl'] == pytest.approx(N * 200_000.0 / 1e8, rel=1e-6)    # the fee share of the JLP held, exactly
    # unhedged, the same pool carries the market
    un = F.simulate(rows, [{}] * len(rows), N)
    assert max(abs(p['pnl'] - N * 200_000.0 / 1e8) for p in un) > 1000.0


def test_short_leg_and_funding_signs():
    up, down = dict(PX0), {a: p * 0.9 for a, p in PX0.items()}
    rows = make_rows([up, down], rate_bn=0.0001, rate_hl=0.00002)
    tok = [{'SOL': 100.0}, {'SOL': 100.0}]
    sim = F.simulate(rows, tok, 1000.0)
    assert sim[0]['price_pnl'] == pytest.approx(100.0 * 11.0)               # a short gains when the price falls
    assert sim[0]['funding_pnl'] == pytest.approx(100.0 * 0.0001 * 110.0 * 3)  # positive rates pay the short
    hl = F.simulate(rows, tok, 1000.0, venue='hyperliquid')
    # 24 hourly settlements priced at the oracle interpolated from 110 to 99
    exp = sum(100.0 * 0.00002 * (110.0 - 11.0 * k / 24.0) for k in range(1, 25))
    assert hl[0]['funding_pnl'] == pytest.approx(exp)
    neg = make_rows([up, down], rate_bn=-0.0001)
    assert F.simulate(neg, tok, 1000.0)[0]['funding_pnl'] < 0                # negative rates charge the short


def test_no_look_ahead(monkeypatch):
    monkeypatch.setattr(F, 'TAKER', {'binance': 0.0, 'hyperliquid': 0.0})
    p1 = {'SOL': 121.0, 'ETH': 2500.0, 'BTC': 83_000.0}
    # at row 1 a $50M 5x SOL long is opened at the new price: NAV unchanged by it, the delta much shorter
    owned, locked, g, G, avg = STATE['SOL']
    st1 = dict(STATE)
    st1['SOL'] = (owned + 10e6 / 121.0, locked + 50e6 / 121.0, g + 40e6, G, avg)
    rows = make_rows([PX0, p1, p1], states=[STATE, st1, st1])
    assert rows[1]['delta_per_jlp']['SOL'] < rows[0]['delta_per_jlp']['SOL'] - 0.003
    N = 1e6
    tok = [{a: r['delta_per_jlp'][a] * N for a in F.ASSETS} for r in rows]
    sim = F.simulate(rows, tok, N)
    assert sim[0]['held']['SOL'] == pytest.approx(rows[0]['delta_per_jlp']['SOL'] * N)
    assert abs(sim[0]['pnl']) < 1e-6 * N * rows[0]['jlp']['price']        # row 0's delta hedges period 0 exactly
    peek = [tok[1], tok[1], tok[2]]                                          # the delta known only at row 1
    assert abs(F.simulate(rows, peek, N)[0]['pnl']) > 100.0


def test_matches_house_vaults_simulator():
    rng = random.Random(5)
    paths = [dict(PX0)]
    for _ in range(12):
        paths.append({a: p * (1 + rng.uniform(-0.05, 0.05)) for a, p in paths[-1].items()})
    rows = make_rows(paths, usdc=[3e8 + 1e5 * i for i in range(13)], rate_bn=0.00005)
    N = 2e6
    ratios = [{a: 0.4 + 0.02 * rng.random() if a == 'SOL' else 0.1 for a in F.ASSETS} for _ in rows]
    tok = [{a: q[a] * N * r['jlp']['price'] / r['binance'][a]['mark'] for a in F.ASSETS} for q, r in zip(ratios, rows)]
    mine = F.simulate(rows, tok, N)
    P = [{'r_v': p['r_v'], 'r': p['r'], 'f': {a: 0.00005 * 3 for a in F.ASSETS}} for p in mine]
    theirs = H.simulate_hedge(P, ratios[:len(P)], fee=F.TAKER['binance'], margin=H.MARGIN, band=0.0)
    for a, b in zip(mine, theirs):
        assert a['ret'] == pytest.approx(b['ret'], rel=1e-9, abs=1e-12)


def test_one_off_amortised_over_the_hold_and_the_test():
    rows = make_rows([PX0] * 11, usdc=[3e8 + 1e5 * i for i in range(11)])
    N = F.FORWARD_RULE['jlp_usd'] / rows[0]['jlp']['price']
    sim = F.simulate(rows, [{} for _ in rows], N)
    a = F.series_stats(sim, 0.0)
    b = F.series_stats(sim, 20_000.0)
    # the verdict spreads a $20k one-off over the 365-day hold: 10 days carry 10/365 of it, 0.2% a year on $10M
    drag = sum(20_000.0 * p['days'] / 365.0 / p['capital'] for p in sim) / 10.0 * 365.0
    assert a['ann_excess'] - b['ann_excess'] == pytest.approx(drag)
    assert drag == pytest.approx(20_000.0 / 10e6, rel=1e-3)
    # the reported 60-day column carries 10/60 of it, 1.2% a year; before one-offs it is untouched
    drag60 = sum(20_000.0 * p['days'] / 60.0 / p['capital'] for p in sim) / 10.0 * 365.0
    assert a['ann_excess_one_off_60d'] - b['ann_excess_one_off_60d'] == pytest.approx(drag60)
    assert b['ann_excess_before_one_off'] == pytest.approx(a['ann_excess_before_one_off'])


# ---------------------------------------------------------------------------------------------------------------------
# kill / promote
# ---------------------------------------------------------------------------------------------------------------------
def test_verdict_thresholds():
    V = F.verdict
    assert V(0, None, None) == 'accumulating (0 of 60 days)'
    assert V(10.2, 0.08, 3.0).startswith('accumulating (10 of 60')
    assert V(59.4, 0.08, 3.0).startswith('accumulating (59 of 60')
    assert V(59.6, 0.005, 1.0).startswith('kill: realised excess +0.50%')
    assert V(60, 0.0099, 5.0).startswith('kill')
    assert V(60, 0.030, 2.5).startswith('promote')
    assert V(60, 0.030, 1.9).startswith('hold')
    assert V(60, 0.024, 4.0).startswith('hold')
    assert V(60, 0.030, None).startswith('hold')
    assert V(20, 0.08, 3.0, sigma_breach='2026-11-01').startswith('kill: 14-day hedged sigma above 0.5% on 15')
    assert V(20, 0.08, 3.0, fee_breach='2026-11-02').startswith('kill: 30-day fee yield')
    assert V(20, 0.08, 3.0, events=['x: AUM limit']).endswith('review: x: AUM limit')


def test_sigma_check_window_and_runs():
    sim = [{'day': 'd%02d' % i, 'days': 1.0, 'ret': 0.0003 * (1 if i % 2 else -1)} for i in range(20)]
    sim += [{'day': 'd%02d' % (20 + i), 'days': 1.0, 'ret': 0.012 * (1 if i % 2 else -1)} for i in range(10)]
    sg = F.sigma_check(sim, 14, 0.005, 14)
    assert sg['n_windows'] == 30 - 13
    # two loud days give a 14-day sd of sqrt(2 x 1.2%^2 / 13) = 0.47%; the third lifts it to 0.58%: a warning
    assert sg['first_breach'] == 'd22'
    assert sg['current_run_above'] == 8 and sg['longest_run_above'] == 8
    assert sg['kill_day'] is None                       # 8 consecutive windows: not yet a kill
    longer = sim + [{'day': 'd%02d' % (30 + i), 'days': 1.0, 'ret': 0.012 * (1 if i % 2 else -1)} for i in range(6)]
    assert F.sigma_check(longer, 14, 0.005, 14)['kill_day'] == 'd35'    # the 14th consecutive window
    # One tail day sits in exactly 14 consecutive 14-day windows, so a single -2.1% day among +-0.05% days reaches a
    # 14-day run on its own; the rule's run of 15 (longer than the window) keeps it a warning
    tail = [{'day': 'q%02d' % i, 'days': 1.0, 'ret': 0.0005 * (1 if i % 2 else -1)} for i in range(40)]
    tail[20] = dict(tail[20], ret=-0.021)
    t = F.sigma_check(tail, 14, 0.005, 14)
    assert t['first_breach'] == 'q20' and t['longest_run_above'] == 14 and t['kill_day'] == 'q33'
    assert F.sigma_check(tail, 14, 0.005, 15)['kill_day'] is None
    assert F.FORWARD_RULE['sigma_kill_run'] > F.FORWARD_RULE['sigma_window']
    assert F.sigma_check(tail, F.FORWARD_RULE['sigma_window'], F.FORWARD_RULE['sigma_max'],
                         F.FORWARD_RULE['sigma_kill_run'])['kill_day'] is None
    quiet = F.sigma_check(sim[:20], 14, 0.005, 14)
    assert quiet['first_breach'] is None and quiet['latest'] < 0.001 and quiet['kill_day'] is None


def test_fee_and_event_flags():
    rows = make_rows([PX0] * 3)
    for r, v in zip(rows, (0.085, 0.064, 0.07)):
        r['fee_yield_30d'] = {'value': v}
    assert F.fee_check(rows, 0.065)['first_breach'] == rows[1]['day']
    assert F.event_flags(rows, 0.01) == []
    rows[2]['jlp']['aum_limit_usd'] = 4e9
    rows[1]['jlp']['dex_vs_nav'] = -0.02
    ev = F.event_flags(rows, 0.01)
    assert any('AUM limit' in e for e in ev) and any('DEX' in e for e in ev)
    # a row carrying a hash other than the one in force when it was written is flagged
    rows[0]['rule_sha256_16'] = 'edited-before'
    assert any('FORWARD_RULE' in e for e in F.event_flags(rows, 0.01))


def test_documented_revision_hashes():
    rev = F.FORWARD_RULE['revisions'][0]
    assert F.expected_hash(rev['last_row_ms']) == rev['replaces_hash'] == '6dfd4a88dece6013'
    assert F.expected_hash(rev['last_row_ms'] + 1) == F.RULE_HASH != rev['replaces_hash']
    # the first real row (written under the replaced rule) passes; the same row claiming the new hash would not
    rows = make_rows([PX0, PX0])
    rows[0] = dict(rows[0], t_ms=rev['last_row_ms'], rule_sha256_16=rev['replaces_hash'])
    assert F.event_flags(rows, 0.01) == []
    rows[0] = dict(rows[0], rule_sha256_16=F.RULE_HASH)
    assert any('FORWARD_RULE' in e for e in F.event_flags(rows, 0.01))
    # a chain of revisions: each row is held to the hash in force at its time
    rule = {'revisions': [{'replaces_hash': 'h0', 'last_row_ms': 10}, {'replaces_hash': 'h1', 'last_row_ms': 20}]}
    assert [F.expected_hash(t, rule, 'h2') for t in (5, 10, 15, 20, 25)] == ['h0', 'h0', 'h1', 'h1', 'h2']


@pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(SAVED), '..', 'llama',
                                                    'fees_jupiter-perpetual-exchange_dailySupplySideRevenue.json')),
                    reason='house_vaults raw fees not present')
def test_fee_yield_is_house_vaults_number():
    f = os.path.join(os.path.dirname(SAVED), '..', 'llama', 'fees_jupiter-perpetual-exchange_dailySupplySideRevenue.json')
    chart = H.load_json(f)['totalDataChart']
    fy = F.fee_yield_30d(chart, 899740189.01)
    assert fy['days'] == 30 and fy['supply_side_usd'] == 6296888
    assert fy['value'] == pytest.approx(0.08514918, abs=1e-8)       # house_vaults analysis.json, JLP checks


def test_ssr_apy():
    assert F.ssr_apy('1000000001182641500000000000') == pytest.approx(0.038, abs=1e-6)   # sUSDS.ssr() 2026-10-10


def test_regression_betas_on_synthetic_history(tmp_path):
    """house_vaults-shaped raw files where JLP moves exactly 0.4 SOL + 0.1 ETH + 0.2 BTC: the trailing 60-day OLS
    recovers the betas, the bridge joins the history to the first row, and every row gets the last refit's betas."""
    import gzip
    rng = random.Random(2)
    H_MS = 3600 * 1000
    start = H.day_ts('2026-06-01') * 1000
    hours = 130 * 24
    closes = {a: [] for a in F.ASSETS}
    px = dict(PX0)
    for k in range(hours):
        for a in F.ASSETS:
            px[a] *= 1 + rng.gauss(0, 0.006)
            closes[a].append(px[a])
    (tmp_path / 'binance').mkdir()
    (tmp_path / 'jlp').mkdir()
    for a, sym in (('SOL', 'SOLUSDT'), ('ETH', 'ETHUSDT'), ('BTC', 'BTCUSDT')):
        rows = [[start + k * H_MS, c, c, c, c, 1.0] for k, c in enumerate(closes[a])]
        with gzip.open(tmp_path / 'binance' / ('klines1h_%s.json.gz' % sym), 'wt') as f:
            json.dump(rows, f)
        with gzip.open(tmp_path / 'binance' / ('funding_%s.json.gz' % sym), 'wt') as f:
            json.dump([{'t': start + k * 8 * H_MS, 'rate': 1e-4} for k in range(hours // 8)], f)

    def at(a, t):                                  # the close of the last bar that closed at or before t
        return closes[a][(t - start) // H_MS - 1]
    beta = {'SOL': 0.4, 'ETH': 0.1, 'BTC': 0.2}
    stamps = [start + (d + 1) * 86400 * 1000 - 2 * H_MS for d in range(120)]      # 22:00 UTC each day
    jl, pts = 4.0, []
    for i, t in enumerate(stamps):
        if i:
            jl *= 1 + sum(b * (at(a, t) / at(a, stamps[i - 1]) - 1) for a, b in beta.items())
        pts.append({'timestamp': t // 1000, 'price': jl})
    (tmp_path / 'jlp' / 'llama_chart_1.json').write_text(json.dumps({'coins': {'solana:x': {'prices': pts}}}))
    t_first = stamps[-1] + 26 * H_MS                                 # the forward test starts a day later
    marks = {a: at(a, t_first) for a in F.ASSETS}
    rows = make_rows([marks, marks])
    for i, r in enumerate(rows):
        r['t_ms'] = t_first + i * DAY
    rows[0]['jlp']['price'] = jl * 1.01
    reg = F.regression_betas(rows, tmp_path)
    for a, b in beta.items():
        assert reg['last_historical'][a] == pytest.approx(b, abs=1e-6)
        assert reg['betas'][-1][a] == pytest.approx(b, abs=1e-6)
    assert len(reg['betas']) == len(rows) and reg['n_history'] == 119
    br = reg['bridge']
    assert br['t0'] == stamps[-1] and br['t1'] == t_first
    assert br['r_v'] == pytest.approx(0.01)
    assert br['r']['SOL'] == pytest.approx(marks['SOL'] / at('SOL', stamps[-1]) - 1)


def _binance_raw(tmp_path, start, hours, rate=1e-4):
    import gzip
    (tmp_path / 'binance').mkdir(exist_ok=True)
    for sym, p in (('SOLUSDT', 100.0), ('ETHUSDT', 2500.0), ('BTCUSDT', 80000.0)):
        rows = [[start + k * 3600 * 1000, p, p, p, p * (1 + 0.001 * k), 1.0] for k in range(hours)]
        with gzip.open(tmp_path / 'binance' / ('klines1h_%s.json.gz' % sym), 'wt') as f:
            json.dump(rows, f)
        with gzip.open(tmp_path / 'binance' / ('funding_%s.json.gz' % sym), 'wt') as f:
            json.dump([{'t': start + k * 8 * 3600 * 1000 + 1, 'rate': rate} for k in range(hours // 8)], f)


def test_hl_book_swaps_only_the_funding(tmp_path):
    H_MS = 3600 * 1000
    start = H.day_ts('2025-01-01') * 1000
    _binance_raw(tmp_path, start, 24 * 5)
    hl = {a: [[start + k * H_MS + 50, 1.25e-5 if k % 3 else -2e-5, 0.0] for k in range(24, 24 * 5)] for a in F.ASSETS}
    bn, hb = H.PriceBook(tmp_path), F.HLBook(tmp_path, hl)
    t0, t1 = start + 2 * DAY, start + 3 * DAY
    assert hb.price('SOL', t1) == bn.price('SOL', t1) and hb.ret('ETH', t0, t1) == bn.ret('ETH', t0, t1)
    exp = sum(r[1] for r in hl['SOL'] if t0 < r[0] <= t1)
    assert hb.funding('SOL', t0, t1) == pytest.approx(exp) and len([r for r in hl['SOL'] if t0 < r[0] <= t1]) == 24
    assert bn.funding('SOL', t0, t1) == pytest.approx(3e-4)                 # three 8-hourly settlements of 1bp
    assert hb.funding('SOL', start, start + DAY) is None                     # before the Hyperliquid series starts


def test_asset_funding_matches_house_vaults_simulator():
    rng = random.Random(9)
    P, betas = [], []
    for i in range(60):
        P.append({'r_v': rng.gauss(0.0003, 0.01), 'r': {a: rng.gauss(0, 0.03) for a in F.ASSETS},
                  'f': {a: rng.gauss(1e-4, 3e-4) for a in F.ASSETS}})
        betas.append({'SOL': 0.42 + 0.05 * rng.random(), 'ETH': 0.07, 'BTC': 0.2 * (i % 7 != 3)})
    sim = H.simulate_hedge(P, betas)
    split = F.asset_funding(P, betas)
    for s, q in zip(sim, split):
        assert sum(q.values()) == pytest.approx(s['fund_pnl'], rel=1e-12, abs=1e-15)


def test_rate_profile_and_gaps():
    H_MS = 3600 * 1000
    rows = [[k * H_MS, F.HL_FLOOR, 0.0] for k in range(6)] + [[6 * H_MS, 3e-5, 0.0], [7 * H_MS, -1e-5, 0.0],
                                                             [11 * H_MS, F.HL_FLOOR, 0.0]]
    rp = F.rate_profile(rows, 0, 12 * H_MS, F.HL_FLOOR)
    assert rp['n'] == 9 and rp['share_at_formula'] == pytest.approx(7 / 9)
    assert rp['share_above'] == pytest.approx(1 / 9) and rp['share_below'] == rp['share_negative'] == pytest.approx(1 / 9)
    # the rates cover 00:00..11:00 (the three missing hours count zero): summed and scaled by 8760 / 11
    assert rp['mean_ann'] == pytest.approx((7 * F.HL_FLOOR + 3e-5 - 1e-5) * 8760.0 / 11.0)
    # an 8-hourly series of 0.01% annualises to the same 10.95% as an hourly series of 0.00125%
    eight = [[k * 8 * H_MS, F.BN_FLOOR] for k in range(1, 31)]
    hourly = [[k * H_MS, F.HL_FLOOR] for k in range(1, 241)]
    assert F.rate_profile(eight, 0, 241 * H_MS, F.BN_FLOOR)['mean_ann'] == pytest.approx(0.1095)
    assert F.rate_profile(hourly, 0, 241 * H_MS, F.HL_FLOOR)['mean_ann'] == pytest.approx(0.1095)
    assert F.hourly_gaps(rows) == {'missing_hours': 3, 'gaps': 1, 'largest_hours': 3.0}


def test_late_settlement_is_kept_once():
    A, Bt = T0, T0 + DAY                          # the previous row's window (A, B]
    T = A + 16 * 3600 * 1000                       # settled inside it, but published after the previous snapshot
    prev = {'t_ms': Bt, 'funding_since_prev': {'from_ms': A, 'binance': {'SOL': [[A + 8 * 3600 * 1000, 1e-4, 100.0]]}}}
    recs = [[A - 1, 9e-4, 100.0], [A + 8 * 3600 * 1000, 1e-4, 100.0], [T, 2e-4, 101.0], [Bt + 3600 * 1000, 3e-4, 102.0]]
    got, late = F.window_records(recs, prev, 'binance', 'SOL')
    assert [x[0] for x in got] == [T, Bt + 3600 * 1000] and late == [T]
    # after the first row there is no earlier window: nothing at or before it may enter the test
    got, late = F.window_records(recs, {'t_ms': Bt, 'funding_since_prev': None}, 'binance', 'SOL')
    assert [x[0] for x in got] == [Bt + 3600 * 1000] and late == []


# ---------------------------------------------------------------------------------------------------------------------
# the ledger
# ---------------------------------------------------------------------------------------------------------------------
def test_append_only_and_same_day_skip(tmp_path):
    led = tmp_path / 'fwd.jsonl'
    rows = make_rows([PX0, PX0])
    r0 = rows[0]
    assert F.append_row(led, r0) == 'daily'
    before = led.read_bytes()
    later = dict(r0, t_ms=r0['t_ms'] + 3600 * 1000)                       # same UTC day, an hour later
    assert F.append_row(led, later) is None
    assert led.read_bytes() == before                                      # skipped, untouched
    assert F.append_row(led, later, intraday=True) == 'intraday'
    after = led.read_bytes()
    assert after.startswith(before) and after.count(b'\n') == 2            # appended; nothing earlier edited
    assert F.read_ledger(led)[1]['kind'] == 'intraday'
    with pytest.raises(ValueError):                                        # never out of order
        F.append_row(led, dict(r0, t_ms=r0['t_ms'] - 1, day='2026-10-10'))
    nxt = dict(rows[1])
    assert F.append_row(led, nxt, intraday=True) == 'daily'                # a new day's first row is the daily one
    assert [r['kind'] for r in F.read_ledger(led)] == ['daily', 'intraday', 'daily']


def test_score_end_to_end(tmp_path, monkeypatch):
    nowhere = tmp_path / 'none'
    one = F.score_rows(make_rows([PX0]), nowhere, nowhere)
    assert one['summary']['verdict'] == 'accumulating (0 of 60 days)'
    rng = random.Random(11)
    paths, usdc = [dict(PX0)], [3e8]
    for _ in range(64):
        paths.append({a: p * (1 + rng.gauss(0, 0.03)) for a, p in paths[-1].items()})
        usdc.append(usdc[-1] + 9e8 * rng.gauss(0.10, 0.05) / 365.0)        # ~10% a year of AUM in fees, noisy
    rows = make_rows(paths, usdc=usdc, rate_bn=0.00005, rate_hl=0.00001)
    rows.insert(3, dict(rows[2], kind='intraday', t_ms=rows[2]['t_ms'] + 3600 * 1000))   # never scored
    res = F.score_rows(rows, nowhere, nowhere)
    S = res['summary']
    assert res['rows'] == {'daily': 65, 'intraday': 1, 'first': rows[0]['day'], 'last': rows[-1]['day']}
    assert S['n'] == 64 and S['days'] == pytest.approx(64.0)
    assert S['verdict'].startswith('promote'), S['verdict']
    assert res['models']['net_delta_binance']['residual_betas']['betas']['SOL'] == pytest.approx(0.0, abs=0.02)
    assert abs(res['models']['unhedged']['residual_betas']['betas']['SOL']) > 0.2
    assert res['models']['net_delta_hyperliquid']['n'] == 64
    assert not res['flags']['warnings']
    # one row without Hyperliquid marks leaves its two periods out of that column only; a lost funding window counts
    # zero and is flagged
    rows[10] = dict(rows[10], hyperliquid=None)
    rows[20] = dict(rows[20], funding_since_prev=dict(rows[20]['funding_since_prev'], hyperliquid=None))
    res2 = F.score_rows(rows, nowhere, nowhere)
    assert res2['models']['net_delta_hyperliquid']['n'] == 62
    assert res2['models']['net_delta_hyperliquid']['periods_left_out'] == 2
    assert res2['models']['net_delta_hyperliquid']['periods_funding_missing'] == 1
    assert res2['models']['net_delta_binance']['n'] == 64
