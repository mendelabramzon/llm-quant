"""Tests for incentive_yields.py core math: no-look-ahead ranking, dilution, reward valuation at sale, loss marking,
cost model, and the allocator engine on a synthetic context.

    cd /Users/iv/dev/llm-quant && uv run --with pytest --with pycryptodome python -m pytest scripts/test_incentive_yields.py -q
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import incentive_yields as I  # noqa: E402

D0 = I.day_of('2024-01-01')   # a Monday


def chart(days_vals, start=D0):
    """[(tvl, base, reward), ...] from `start` -> chart rows as DefiLlama returns them (~23:01 UTC each day)."""
    return [{'timestamp': I.ymd(start + i) + 'T23:01:00.000Z', 'tvlUsd': t, 'apyBase': b, 'apyReward': r}
            for i, (t, b, r) in enumerate(days_vals)]


# ------------------------------------------------------------------------------------------------ dates

def test_day_roundtrip_and_chart_stamp():
    assert I.ymd(I.day_of('2024-07-01')) == '2024-07-01'
    assert I.day_of('2024-07-01T23:01:24.670Z') == I.day_of('2024-07-01')
    assert I.day_of(1719792000) == I.day_of('2024-07-01')


# ------------------------------------------------------------------------------------------------ dilution / capacity

def test_dilution():
    assert I.dilution(1e6, 0) == 1.0
    assert I.dilution(1e6, 1e6) == pytest.approx(0.5)
    assert I.dilution(3e6, 1e6) == pytest.approx(0.75)
    assert I.dilution(0, 1e5) == 0.0


def test_capacity_deposit_marginal_yield():
    T, y, m = 10e6, 0.12, 0.048
    X = I.capacity_deposit(y, T, m)
    assert X == pytest.approx(T * (math.sqrt(y / m) - 1))
    # the marginal yield at X* equals the hurdle: d/dX [X y T/(T+X)] = y T^2/(T+X)^2
    assert y * T * T / (T + X) ** 2 == pytest.approx(m)
    assert I.capacity_deposit(0.04, T, m) == 0.0
    assert I.capacity_deposit(None, T, m) == 0.0


# ------------------------------------------------------------------------------------------------ rewards

def test_claim_sale_day_weekly_from_entry():
    e = D0
    assert I.claim_sale_day(e, e, 10 ** 9) == e + 7 + 1
    assert I.claim_sale_day(e + 6, e, 10 ** 9) == e + 7 + 1
    assert I.claim_sale_day(e + 7, e, 10 ** 9) == e + 14 + 1
    # exit before the claim week ends: claimed at exit
    assert I.claim_sale_day(e + 2, e, e + 4) == e + 4 + 1


def test_price_at_never_looks_forward():
    days, px = [D0, D0 + 2, D0 + 9], [1.0, 2.0, 3.0]
    assert I.price_at(days, px, D0 + 1) == 1.0
    assert I.price_at(days, px, D0 + 2) == 2.0
    assert I.price_at(days, px, D0 + 8) is None          # stale beyond 5 days, and D0+9 is in the future
    assert I.price_at(days, px, D0 - 1) is None


def test_sale_ratio_values_reward_at_sale_price():
    tok_a = ([D0 + i for i in range(20)], [10.0 - 0.5 * i for i in range(20)])   # falling token
    tok_b = ([D0 + i for i in range(20)], [1.0] * 20)                             # stable reward
    # 3-day backward medians: P(D0) = 10 (only day), P(D0+8) = median(6.0, 6.5, 7.0) = 6.5
    r, n = I.sale_ratio([tok_a], D0, D0 + 8)
    assert n == 1 and r == pytest.approx(6.5 / 10.0)
    r, n = I.sale_ratio([tok_a, tok_b], D0, D0 + 8)
    assert n == 2 and r == pytest.approx((0.65 + 1.0) / 2)
    assert I.sale_ratio([], D0, D0 + 8) == (None, 0)


def test_sale_ratio_survives_a_bad_print_and_is_capped():
    days = [D0 + i for i in range(20)]
    px = [1.0] * 20
    px[5] = 8e-7                                   # one bad print on the accrual day
    r, _ = I.sale_ratio([(days, px)], D0 + 5, D0 + 13)
    assert r == pytest.approx(1.0)
    px2 = [1.0] * 10 + [50.0] * 10                 # a genuine (or bad) 50x move is capped
    r, _ = I.sale_ratio([(days, px2)], D0 + 3, D0 + 15)
    assert r == I.SALE_RATIO_CAP


# ------------------------------------------------------------------------------------------------ losses

def test_depeg_loss_band():
    assert I.depeg_loss(1.0, 0.995) == 0.0                 # noise inside the band
    assert I.depeg_loss(1.0, 0.95) == pytest.approx(-0.05)
    assert I.depeg_loss(1.0, 1.03) == 0.0
    assert I.depeg_loss(None, 0.5) == 0.0


def test_hack_severity():
    assert I.hack_severity(10e6, 100e6) == pytest.approx(0.1)
    assert I.hack_severity(200e6, 100e6) == 1.0
    assert I.hack_severity(5e6, None) == 1.0
    assert I.hack_severity(0, 100e6) == 0.0


# ------------------------------------------------------------------------------------------------ costs

def test_switch_cost_components():
    d = I.day_of('2025-06-01')
    # same chain, same token: gas only (1 withdraw + 2 deposit txs)
    assert I.switch_cost(1e6, 'Arbitrum', 'Arbitrum', 'USDC', 'USDC', d) == pytest.approx(3 * I.GAS_OTHER)
    # chain change adds a bridge ($10 + 5bp at $1M)
    c = I.switch_cost(1e6, 'Arbitrum', 'Base', 'USDC', 'USDC', d)
    assert c == pytest.approx(3 * I.GAS_OTHER + 10 + 500)
    # exotic stable swap at $10M costs 50bp, bridges 8bp
    c = I.switch_cost(1e7, 'Ethereum', 'Base', 'USDC', 'AUSD', d)
    assert c == pytest.approx(I.gas_per_tx('Ethereum', d) + 2 * I.GAS_OTHER + 10 + 8000 + 50000)
    # Ethereum gas is era-dependent
    assert I.gas_per_tx('Ethereum', I.day_of('2023-05-01')) == 20.0
    assert I.gas_per_tx('Ethereum', I.day_of('2026-05-01')) == 3.0


def test_swap_bp_tiers():
    assert I.swap_bp('USDC', 'USDC', 1e5) == 0.0
    assert I.swap_bp('USDC', 'USDT', 1e5) == 2.0
    assert I.swap_bp('USDC', 'USDT', 1e7) == 5.0
    assert I.swap_bp('USDC', 'CRVUSD', 1e6) == 20.0


# ------------------------------------------------------------------------------------------------ Pool / ranking

def test_pool_trailing_uses_only_days_before_decision():
    vals = [(2e6, 5.0, 0.0)] * 10 + [(2e6, 50.0, 0.0)] * 10
    P = I.Pool('p', {}, chart(vals))
    D = D0 + 10                                   # day 10 is the first 50% day: not visible at D
    b, r = P.trailing(D, 7)
    assert b == pytest.approx(5.0) and r == 0.0
    b2, _ = P.trailing(D + 1, 7)                  # one day later the first 50% day enters
    assert b2 == pytest.approx((6 * 5.0 + 50.0) / 7)
    # changing anything on or after D cannot change the score at D
    vals2 = [(2e6, 5.0, 0.0)] * 10 + [(9e9, 99.0, 99.0)] * 10
    P2 = I.Pool('p', {}, chart(vals2))
    assert P2.trailing(D, 7) == P.trailing(D, 7)
    assert P2.tvl_before(D) == P.tvl_before(D)


def test_pool_staleness_and_bad_records():
    vals = [(2e6, 5.0, 0.0)] * 5
    P = I.Pool('p', {}, chart(vals))
    assert P.trailing(D0 + 5 + I.FRESH_DAYS + 1, 30) is None    # last record too old
    rows = chart([(2e6, 5.0, 0.0), (2e6, 500.0, 0.0), (2e6, 5.0, 0.0)])
    P = I.Pool('p', {}, rows)
    assert P.bad == 1 and P.at(D0 + 1) == (2e6, 5.0, 0.0)          # the 500% day is dropped and forward filled


def test_rank_pools_deterministic():
    c = [(5.0, 1e6, 'b'), (7.0, 1e6, 'a'), (5.0, 2e6, 'c'), (5.0, 1e6, 'a2')]
    assert I.rank_pools(c, 3) == ['a', 'c', 'a2']


# ------------------------------------------------------------------------------------------------ engine

class FakeCtx:
    """Minimal context: pools with charts, a flat savings rate, optional hacks/prices."""

    def __init__(self, charts, sav=0.04, hacks=None, dep=None, reward_px=None, meta=None):
        self.pools = {pid: I.Pool(pid, {}, rows) for pid, rows in charts.items()}
        self.meta = meta or {pid: {'chain': 'Arbitrum', 'project': 'proj-' + pid, 'symbol': 'USDC'} for pid in charts}
        self._sav = sav
        self.hacks = hacks or {}
        self.dep = dep or {}
        self.reward_px = reward_px or {}
        self.impute_ratio = 0.9

    def sav(self, d):
        return self._sav

    def hack_on(self, project, chain, d):
        return self.hacks.get((project, d))

    def dep_price(self, pid, d):
        ser = self.dep.get(pid)
        return None if ser is None else I.price_at(ser[0], ser[1], d)

    def eligible(self, D, k, uni, alive=None):
        out = []
        for pid, P in self.pools.items():
            tr = P.trailing(D, k)
            T = P.tvl_before(D)
            if tr and T and T >= 1e6:
                out.append((tr[0], tr[1], T, pid))
        return out


def run(ctx, days=28, N=1, H=1, cap=1e6, **kw):
    sel = I.score_selector(ctx, 7, 1.0, 'all')
    return I.simulate(ctx, sel, N, H, cap, D0 + 7, D0 + 7 + days, **kw)


def test_engine_base_yield_with_dilution_and_costs():
    T = 9e6
    ctx = FakeCtx({'a': chart([(T, 10.0, 0.0)] * 60)})
    res = run(ctx, cap=1e6)
    f = T / (T + 1e6)
    weekly = 10.0 / 100 / 365 * f * 7
    w = res['weeks']
    # first week pays the switch cost (from cash on Ethereum to Arbitrum: bridge + gas)
    d = D0 + 7
    cost = I.switch_cost(1e6, None, 'Arbitrum', None, 'USDC', d) / 1e6
    assert w[0][1] == pytest.approx(weekly - cost)
    assert w[1][1] == pytest.approx(weekly)
    assert w[1][3] == pytest.approx(weekly - 0.04 * 7 / 365)


def test_engine_rewards_valued_at_sale_price():
    ctx = FakeCtx({'a': chart([(1e12, 0.0, 20.0)] * 60)},
                  reward_px={'a': [([D0 + i for i in range(60)], [10.0 * 0.99 ** i for i in range(60)])]})
    res = run(ctx, days=7, cap=1e3)
    # every day of the first week is sold on entry+8: ratio = p(entry+8)/p(d)
    e = D0 + 7
    exp = sum(20.0 / 100 / 365 * (0.99 ** (e + 8 - D0)) / (0.99 ** (d - D0)) * (1 - I.REWARD_SALE_COST)
              for d in range(e, e + 7)) * 1e3
    gas = 7 * 2 * I.GAS_OTHER / 7
    cost = I.switch_cost(1e3, None, 'Arbitrum', None, 'USDC', e)
    got = res['weeks'][0][1] * 1e3
    assert got == pytest.approx(exp - gas - cost, rel=1e-6)


def test_engine_hack_marks_to_zero_then_recovers():
    pid = 'a'
    hack_day = D0 + 10
    ctx = FakeCtx({pid: chart([(5e6, 10.0, 0.0)] * 120)},
                  hacks={('proj-a', hack_day): {'severity': 0.3, 'name': 'x'}})
    res = run(ctx, days=63, cap=1e6)
    ev = [e for e in res['events'] if e['type'] == 'hack']
    assert len(ev) == 1 and ev[0]['loss'] == pytest.approx(-0.3e6)
    by_week = {I.ymd(w[0]): w[1] for w in res['weeks']}
    wk_hack = I.ymd(D0 + 7)
    assert by_week[wk_hack] < -0.99       # marked to zero in the hack week
    total = sum(w[1] for w in res['weeks']) * 1e6
    # net: -30% severity, plus ~30 days of 10% a year outside the freeze, minus two entries' bridge costs
    assert -0.30e6 < total < -0.28e6


def test_engine_depeg_realised_at_exit():
    # pool 'a' ranks first for two weeks, then 'b' overtakes; the token of 'a' fell 5% by the exit
    a = chart([(5e6, 10.0, 0.0)] * 14 + [(5e6, 0.1, 0.0)] * 30)
    b = chart([(5e6, 5.0, 0.0)] * 44)
    px = ([D0 + i for i in range(44)], [1.0] * 15 + [0.95] * 29)
    ctx = FakeCtx({'a': a, 'b': b}, dep={'a': px})
    res = run(ctx, days=28, cap=1e6, buffer=1)
    ev = [e for e in res['events'] if e['type'] == 'depeg']
    assert len(ev) == 1 and ev[0]['loss'] == pytest.approx(-0.05e6)


def test_engine_delay_executes_late_not_never():
    ctx = FakeCtx({'a': chart([(5e6, 10.0, 0.0)] * 80)})
    r0 = run(ctx, days=35)
    r7 = run(ctx, days=35, delay=7)
    # with a week's delay the first week is in cash (excess 0) and the rest earns the pool
    assert r7['weeks'][0][3] == pytest.approx(0.0, abs=1e-12)
    assert r7['weeks'][2][1] == pytest.approx(r0['weeks'][2][1])


def test_engine_decision_ignores_future_data():
    # identical histories before the decision, wildly different after: the first week's pick must match
    good = chart([(5e6, 8.0, 0.0)] * 7 + [(5e6, 8.0, 0.0)] * 30)
    good_future = chart([(5e6, 8.0, 0.0)] * 7 + [(5e6, 0.0, 0.0)] * 30)
    other = chart([(5e6, 6.0, 0.0)] * 7 + [(5e6, 90.0, 0.0)] * 30)
    r1 = run(FakeCtx({'a': good, 'b': other}), days=7, record=True)
    r2 = run(FakeCtx({'a': good_future, 'b': other}), days=7, record=True)
    e1 = [e['pool'] for e in r1['events'] if e['type'] == 'enter']
    e2 = [e['pool'] for e in r2['events'] if e['type'] == 'enter']
    assert e1 == e2 == ['a']


# ------------------------------------------------------------------------------------------------ chain reads

def test_selectors_match_keccak():
    from Crypto.Hash import keccak

    def sel(sig):
        k = keccak.new(digest_bits=256)
        k.update(sig.encode())
        return '0x' + k.hexdigest()[:8]
    assert sel('getReserveData(address)') == I.SEL_GET_RESERVE_DATA
    assert sel('getUtilization()') == I.SEL_GET_UTILIZATION
    assert sel('getSupplyRate(uint256)') == I.SEL_GET_SUPPLY_RATE


def test_rate_conversions():
    # 5% APR in ray compounds to ~5.127% APY
    assert I.aave_apy_from_ray(0.05e27) == pytest.approx(math.exp(0.05) - 1, rel=1e-6)
    per_sec = 0.05 / I.SECONDS_PER_YEAR * 1e18
    assert I.comet_apy_from_rate(per_sec) == pytest.approx(math.exp(0.05) - 1, rel=1e-6)


def test_wayback_pick_and_usd_filter():
    rows = [['20240101120000', '200', '1'], ['20240103120000', '200', '1'], ['20240116120000', '200', '1'],
            ['20240301120000', '200', '1']]
    picks = I.wayback_pick(rows, (1, 15))
    assert picks == ['20240101120000', '20240116120000', '20240301120000']
    assert I.is_usd_stable_row({'stablecoin': True, 'exposure': 'single', 'symbol': 'USDC'})
    assert not I.is_usd_stable_row({'stablecoin': True, 'exposure': 'single', 'symbol': 'EURC'})
    assert not I.is_usd_stable_row({'stablecoin': True, 'exposure': 'multi', 'symbol': 'USDC-USDT'})


def test_incentive_spend_filters():
    fields = ['pool', 'chain', 'project', 'symbol', 'tvlUsd', 'apyBase', 'apyReward', 'stablecoin', 'exposure', 'ilRisk']
    rows = [['a', 'Base', 'x', 'USDC', 1e6, 1.0, 10.0, True, 'single', 'no'],
            ['b', 'Base', 'y', 'WETH-USDC', 2e6, 1.0, 5.0, False, 'multi', 'yes'],
            ['c', 'Base', 'z', 'MEME', 5e3, 0.0, 9000.0, False, 'single', 'no']]
    s = I.incentive_spend(rows, fields)
    assert s['total_clean_usd'] == pytest.approx(1e5 + 1e5)
    assert s['total_raw_usd'] == pytest.approx(1e5 + 1e5 + 5e3 * 90)
    assert s['usd_stable_single']['usd'] == pytest.approx(1e5)


# ------------------------------------------------------------------------------------------------ share-price marks

def test_share_key_parsing():
    a = '0x0F359FD18BDa75e9c49bC027E7da59a4b01BF32a'
    assert I.share_key('morpho-blue-%s-ethereum' % a, 'Ethereum') == 'ethereum:' + a.lower()
    assert I.share_key('euler-earn-%s-avax' % a, 'Avalanche') == 'avax:' + a.lower()
    assert I.share_key('%s-optimism' % a, 'OP Mainnet') == 'optimism:' + a.lower()
    assert I.share_key(a, 'Ethereum') == 'ethereum:' + a.lower()
    assert I.share_key(a, 'Avalanche') == 'avax:' + a.lower()
    assert I.share_key('USDT-Sui', 'Sui') is None
    assert I.share_key(None, 'Ethereum') is None


def share_ctx(days, px, accruing):
    c = I.Ctx.__new__(I.Ctx)
    c.share_px = {'v': (days, px)}
    c.share_accruing = {'v': accruing}
    c.dep_px = {}
    return c


def test_principal_mark_vault_writedown_and_shortfall():
    days = [D0 + i for i in range(80)]
    px = [1.0 + 0.0003 * i for i in range(40)] + [0.02] * 40          # accrues, then a 98% write-down on day 40
    c = share_ctx(days, px, True)
    # a hold that ends before the write-down, share growth equal to the claimed accrual: no loss
    f, kind = c.principal_mark('v', D0 + 5, D0 + 25, None, c.share_price('v', D0 + 5), 0.0003 * 20, False)
    assert kind == 'share' and f == pytest.approx(0.0, abs=1e-4)
    # a share that grew more than claimed is not credited (the surplus may be rewards counted elsewhere)
    f, _ = c.principal_mark('v', D0 + 5, D0 + 25, None, c.share_price('v', D0 + 5), 0.0, False)
    assert f == 0.0
    # the same hold, but the pool claimed 3x the accrual the share price delivered: the shortfall is booked
    f, _ = c.principal_mark('v', D0 + 5, D0 + 25, None, c.share_price('v', D0 + 5), 0.0003 * 20 + 0.02, False)
    assert f == pytest.approx(-0.02, abs=1e-3)
    # a hold across the write-down loses ~98%
    f, kind = c.principal_mark('v', D0 + 30, D0 + 45, None, c.share_price('v', D0 + 30), 0.0003 * 15, False)
    assert kind == 'share' and f < -0.95


def test_principal_mark_stuck_exit_after_collapse():
    days = [D0 + i for i in range(80)]
    px = [1.0] * 30 + [0.5] * 50                                        # the run resolves at half value
    c = share_ctx(days, px, False)
    spx0 = c.share_price('v', D0 + 5)
    # exit decided on day 28 (before the write-down) after a liquidity collapse: marked four weeks later
    f, kind = c.principal_mark('v', D0 + 5, D0 + 28, None, spx0, 0.0, True)
    assert kind == 'share_stuck' and f == pytest.approx(-0.5)
    # without the collapse flag the exit is at the day-28 price
    f, kind = c.principal_mark('v', D0 + 5, D0 + 28, None, spx0, 0.0, False)
    assert kind == 'share' and f == 0.0


def test_share_price_backward_median_ignores_one_day_glitch():
    days = [D0 + i for i in range(10)]
    px = [1.0, 1.0, 1.0, 1.0, 0.01, 1.0, 1.0, 1.0, 1.0, 1.0]
    c = share_ctx(days, px, False)
    assert c.share_price('v', D0 + 4) == 1.0          # median of days 2..4
    assert c.share_price('v', D0 + 3) == 1.0


def test_engine_small_hack_booked_without_freeze():
    hack_day = D0 + 10
    ctx = FakeCtx({'a': chart([(5e6, 10.0, 0.0)] * 60)},
                  hacks={('proj-a', hack_day): {'severity': 0.01, 'name': 'x'}})
    res = run(ctx, days=14, cap=1e6)
    ev = [e for e in res['events'] if e['type'] == 'hack']
    assert len(ev) == 1 and ev[0]['frozen'] is False
    wk = res['weeks'][0][1]
    assert -0.0105 < wk < -0.008            # -1% loss plus a week's yield, no mark to zero


def test_densify_captures_no_lookahead():
    caps = [(D0, 2e6, 5.0, 1.0), (D0 + 7, 3e6, 9.0, 0.0), (D0 + 30, 1e6, 2.0, 0.0)]
    rows = I.densify_captures(caps)
    days = [r['timestamp'] for r in rows]
    assert days[0] == D0 and D0 + 6 in days and D0 + 7 in days
    # a capture's values never appear before its day
    assert all(r['apyBase'] == 5.0 for r in rows if r['timestamp'] < D0 + 7)
    # carried at most 10 days: the 23-day gap leaves days D0+17..D0+29 empty
    assert D0 + 16 in days and D0 + 17 not in days and D0 + 29 not in days
    P = I.Pool('p', {}, rows)
    assert P.trailing(D0 + 7, 7) == (5.0, 1.0)
