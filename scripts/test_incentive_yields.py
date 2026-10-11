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


# ------------------------------------------------------------------------------------------------ forward test

DF = I.day_of('2026-10-12')       # a decision day of the frozen 28-day calendar


def test_forward_calendar_is_the_studys_four_week_phase():
    assert (DF - I.day_of(I.START)) % 28 == 0
    sat = I.day_of('2026-10-10') * I.DAY_S * 1000 + int(23.5 * 3600e3)
    assert I.mm_decision_after(sat) == DF
    assert I.mm_decision_after(DF * I.DAY_S * 1000) == DF + 28          # at 00:00 the decision has begun
    assert I.mm_decision_after(DF * I.DAY_S * 1000 - 1) == DF


def test_assign_slices_is_simulates_decision_block():
    """Two decisions through simulate (a scripted selector) and through assign_slices give the same holdings."""
    pids = list('abcdefgh')
    ctx = FakeCtx({p: chart([(5e6, 5.0, 0.0)] * 40) for p in pids})
    script = {D0 + 7: (['a', 'b', 'c', 'd', 'e', 'f'], set(pids)),
              D0 + 14: (['f', 'g', 'c', 'h', 'e', 'a', 'd', 'b'], set(pids) - {'b'})}

    def sel(D):
        return script[D]
    res = I.simulate(ctx, sel, 3, 1, 3e6, D0 + 7, D0 + 21, buffer=2, record=True)
    held = {}
    for e in res['events']:
        if e['type'] == 'enter':
            held.setdefault(e['day'], []).append(e['pool'])
    first = I.assign_slices([None] * 3, *script[D0 + 7], N=3, buffer=2)
    assert first == ['a', 'b', 'c'] and sorted(held[I.ymd(D0 + 7)]) == ['a', 'b', 'c']
    second = I.assign_slices(first, *script[D0 + 14], N=3, buffer=2)
    # a (rank 6 of the top 6) and c stay; b is no longer eligible: its slice takes f, the best pool not held
    assert second == ['a', 'f', 'c'] and held[I.ymd(D0 + 14)] == ['f']


def _fwd_inputs(D=DF):
    """Live-shaped inputs with one pool per failure mode."""
    def rows(n, base, rew, tvl=5e8, start=None):
        s0 = D - n if start is None else start
        return [{'timestamp': I.ymd(s0 + i) + 'T23:01:00.000Z', 'tvlUsd': tvl, 'apyBase': base, 'apyReward': rew}
                for i in range(D - s0)]
    usdc, dai, bad = '0x' + 'a' * 40, '0x' + 'd' * 40, '0x' + 'e' * 40
    pools = [('p1', 'aave-v3', usdc, 4.0, 1.0), ('p7', 'aave-v3', dai, 3.0, 0.5), ('p2', 'morpho-blue', usdc, 9.0, 3.0),
             ('p3', 'smalllend', usdc, 8.0, 0.0), ('p4', 'hackedlend', usdc, 7.0, 0.0), ('p5', 'aave-v3', bad, 6.0, 0.0),
             ('p6', 'aave-v3', usdc, 9.5, 0.0)]
    R = [{'pool': p, 'chain': 'Ethereum', 'project': pr, 'symbol': 'USDC', 'underlyingTokens': [u],
          'rewardTokens': ['0x' + 'b' * 40] if r else None, 'stablecoin': True, 'exposure': 'single', 'tvlUsd': 5e8}
         for p, pr, u, b, r in pools]
    charts = {p: rows(60, b, r) for p, _, _, b, r in pools}
    charts['p6'] = rows(5, 9.5, 0.0)                                   # five days old
    hist = lambda v: [[(D - 800 + i) * I.DAY_S, v] for i in range(800)]
    protocols = [{'slug': 'aave-v3', 'id': '1', 'name': 'Aave V3', 'category': 'Lending', 'tvl': 2e10},
                 {'slug': 'morpho-blue', 'id': '2', 'name': 'Morpho', 'category': 'Lending', 'tvl': 8e9},
                 {'slug': 'smalllend', 'id': '3', 'name': 'Small', 'category': 'Lending', 'tvl': 5e8},
                 {'slug': 'hackedlend', 'id': '4', 'name': 'Hacked', 'category': 'Lending', 'tvl': 3e9}]
    detail = {'aave-v3': {'category': 'Lending', 'tvl': hist(2e10), 'chainTvls': {}},
              'morpho-blue': {'category': 'Lending', 'tvl': hist(8e9), 'chainTvls': {}},
              'smalllend': {'category': 'Lending', 'tvl': hist(5e8), 'chainTvls': {}},
              'hackedlend': {'category': 'Lending', 'tvl': hist(3e9), 'chainTvls': {}}}
    hacks = [{'date': (D - 10) * I.DAY_S, 'defillamaId': '4', 'name': 'Hacked', 'amount': 1e6, 'returnedFunds': 0,
              'chain': ['Ethereum']}]
    prices = {I.coin_key('Ethereum', usdc): 1.0, I.coin_key('Ethereum', dai): 1.0, I.coin_key('Ethereum', bad): 0.97}
    marks = {'at': '2026-10-11T12:00:00+00:00', 'savings': {'apy': 0.038, 'susds_nav': 1.0},
             'pools': {'p1': {'share_px': 1.0, 'deposit_px': 1.0, 'reward_px': {}, 'onchain': None},
                       'p7': {'share_px': 1.0, 'deposit_px': 1.0, 'reward_px': {}, 'onchain': None}}}
    return {'rows': R, 'charts': charts, 'protocols': protocols, 'detail': detail, 'hacks': hacks, 'prices': prices,
            'marks': marks, 'pool_strings': {}, 'n_usd_stable': len(R), 'failed_charts': []}


def test_live_context_applies_the_studys_eligibility():
    ctx, ranked, elig = I.mm_rank(_fwd_inputs(), DF)
    # p2 curated, p3 protocol under $1B, p4 hacked 10 days ago, p5 deposit at $0.97, p6 five days old
    assert ranked == ['p1', 'p7'] and elig == {'p1', 'p7'}


def test_forward_registration_freezes_the_rule_and_is_append_only(tmp_path, monkeypatch):
    monkeypatch.setattr(I, 'MM_WATCH_RAW', tmp_path / 'raw')
    led = tmp_path / 'mm.jsonl'
    now = DF * I.DAY_S * 1000 - 20 * 3600 * 1000
    row = I.mm_forward_register(led, now, inputs_fn=lambda D, d: _fwd_inputs(D), log=lambda *a: None)
    assert row['rule_frozen'] == I.MM_FORWARD_RULE and row['params'] == I.MM_PARAMS
    assert row['decision_day'] == '2026-10-12' and row['hold_end'] == '2026-11-09'
    assert [x['pool'] for x in row['slices']] == ['p1', 'p7', None, None, None]
    assert row['top10'][0]['score_pct'] == pytest.approx(5.0) and row['slices'][0]['entered'] == '2026-10-12'
    before = led.read_text()
    assert I.mm_forward_register(led, now + 3600e3, inputs_fn=lambda D, d: _fwd_inputs(D), log=lambda *a: None) is None
    assert led.read_text() == before


def test_forward_registration_after_the_decision_or_too_early_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(I, 'MM_WATCH_RAW', tmp_path / 'raw')
    led = tmp_path / 'mm.jsonl'
    late = DF * I.DAY_S * 1000 + 60 * 1000
    assert I.mm_forward_register(led, late, inputs_fn=lambda D, d: _fwd_inputs(D), log=lambda *a: None,
                                 decision='2026-10-12') is None
    early = DF * I.DAY_S * 1000 - 40 * 3600 * 1000
    assert I.mm_forward_register(led, early, inputs_fn=lambda D, d: _fwd_inputs(D), log=lambda *a: None) is None
    assert not led.exists()


def _hold(slices, entry_marks, D=DF):
    infos = {p: {'pool': p, 'project': 'aave-v3', 'chain': 'Arbitrum', 'symbol': 'USDC', 'underlying': [],
                 'reward_keys': ['arbitrum:0xrew'], 'share_accruing': acc} for p, acc in slices if p}
    return {'kind': 'hold', 'decision_day': I.ymd(D), 'hold_end': I.ymd(D + 28), 'params': I.MM_PARAMS,
            'slices': [{'slice': i, 'pool': p, 'switch_cost_usd': 0.0 if p is None else 100.0,
                        'entered': I.ymd(D)} for i, (p, _) in enumerate(slices)],
            'infos': infos, 'entry_marks': entry_marks, 'protocol_tvl_at_decision': {'aave-v3': 1e10}}


def test_score_hold_arithmetic_on_synthetic_records():
    """One rebasing pool at 5% base + 2% rewards on $100M, four cash slices: the hold earns the diluted base, the
    rewards at sale price (flat) less 1% and claim gas, pays its switch cost, and is compared with sUSDS NAV growth."""
    X, D, E = 2e5, DF, DF + 28
    hold = _hold([('p', False), (None, None), (None, None), (None, None), (None, None)],
                 {'at': '2026-10-11T12:00:00+00:00', 'savings': {'apy': 0.038, 'susds_nav': 1.0},
                  'pools': {'p': {'share_px': 1.0, 'deposit_px': 1.0, 'reward_px': {'arbitrum:0xrew': 2.0}}}})
    charts = {'p': [{'timestamp': I.ymd(d) + 'T23:01:00.000Z', 'tvlUsd': 1e8, 'apyBase': 5.0, 'apyReward': 2.0}
                    for d in range(D - 10, E + 2)]}
    marks = {'p': {d: {'share_px': 1.0, 'deposit_px': 1.0, 'reward_px': {'arbitrum:0xrew': 2.0}}
                   for d in range(D - 1, E + 2)}}
    s28 = 0.038 * 28 / 365
    sav = [(D * I.DAY_S * 1000, 0.038, 1.0), (E * I.DAY_S * 1000, 0.038, 1.0 + s28)]
    out = I.score_hold(hold, charts, marks, sav, I.MM_PARAMS)
    f = 1e8 / (1e8 + X)
    base = X * 0.05 / 365 * 28 * f
    rew = X * 0.02 / 365 * 28 * f * 0.99
    gas = 2 * 0.5 / 7 * 28
    pnl = base + rew - gas - 100.0
    assert out['savings'] == pytest.approx(s28) and out['savings_source'] == 'sUSDS NAV'
    assert out['slices'][0]['pnl_usd'] == pytest.approx(pnl)
    assert out['return'] == pytest.approx((pnl + 4 * X * s28) / 1e6)
    assert out['excess'] == pytest.approx((pnl - X * s28) / 1e6)
    assert out['mean_reward_apr_pct'] == pytest.approx(2.0) and out['exit_marks_complete']
    # an accruing share that delivered 0.1% while claiming 5% books the shortfall (under 1%: no exit event)
    hold2 = _hold([('p', True), (None, None), (None, None), (None, None), (None, None)], hold['entry_marks'])
    marks2 = {'p': dict(marks['p'])}
    marks2['p'][E] = dict(marks2['p'][E], share_px=1.001)
    out2 = I.score_hold(hold2, charts, marks2, sav, I.MM_PARAMS)
    assert out2['slices'][0]['audit_loss_frac'] == pytest.approx(0.001 - 0.05 * 28 / 365)
    assert out2['events'] == []
    marks2['p'][E] = dict(marks2['p'][E], share_px=0.985)              # a 1.5% write-down: exit event
    out3 = I.score_hold(hold2, charts, marks2, sav, I.MM_PARAMS)
    assert out3['events'] and out3['events'][0]['type'] == 'share shortfall'
    assert out3['slices'][0]['pnl_usd'] == pytest.approx(pnl + X * (-0.015 - 0.05 * 28 / 365))


def test_forward_verdict_accumulates_then_follows_the_kill_and_promote_rules():
    def s(x, rew=2.0, ev=()):
        return {'excess': x, 'mean_reward_apr_pct': rew, 'events': list(ev), 'hold_end': '2026-11-09'}
    h = [{'decision_day': '2026-10-12', 'capacity_usd': 3e7}]
    assert I.mm_forward_summary([s(0.001), s(0.0012)], h)['verdict'] == 'accumulating (2 of 6 holds)'
    assert I.mm_forward_summary([s(0.001), s(-0.001), s(-0.0011)], h)['verdict'].startswith('kill: trailing 3-hold')
    assert 'reward APR' in I.mm_forward_summary([s(0.001, rew=0.5)], h)['verdict']
    assert 'capacity' in I.mm_forward_summary([s(0.001)], [{'decision_day': '2026-10-12', 'capacity_usd': 1e6}])['verdict']
    good = I.mm_forward_summary([s(0.0008 + 0.0001 * (i % 2)) for i in range(6)], h)
    assert good['verdict'].startswith('promote') and good['ann_excess'] == pytest.approx(0.00085 * 365 / 28)
    two = [{'type': 'share shortfall', 'day': '2026-11-09'}, {'type': 'hack', 'day': '2026-12-01'}]
    assert '2 shortfall/hack events' in I.mm_forward_summary([s(0.001, ev=two)], h)['verdict']
