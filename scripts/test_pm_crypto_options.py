"""Tests for the money-deciding pure functions of pm_crypto_options: fees, costs, fill rules, probabilities, parsing."""
import math
import random
import statistics

import pm_crypto_options as P

N = statistics.NormalDist()


def test_pm_fee_and_taker_cost():
    assert abs(P.pm_fee(0.5) - 0.07 * 0.25) < 1e-12
    assert abs(P.pm_fee(0.02) - 0.07 * 0.02 * 0.98) < 1e-12
    # ask = mid + half-spread, then the fee at the ask
    c = P.taker_cost(0.40, 0.01)
    assert abs(c - (0.41 + 0.07 * 0.41 * 0.59)) < 1e-12
    # capped at 0.999 and floored at 0.001
    assert P.taker_cost(0.9995, 0.01) <= 0.999 + 0.07 * 0.999 * 0.001 + 1e-12
    assert P.taker_cost(-0.01, 0.0) >= 0.001


def test_taker_edge_sides_sum_negative():
    # buying both sides can never be profitable: the two edges sum to minus the costs
    for p in (0.05, 0.3, 0.5, 0.8):
        for mid in (0.1, 0.5, 0.9):
            e = P.taker_edge(p, mid, 0.01, 'yes') + P.taker_edge(p, mid, 0.01, 'no')
            assert e < 0


def test_maker_fill_needs_a_tick_through():
    assert P.maker_fill(0.40, [0.45, 0.40, 0.42]) is None          # touching the limit is not a fill
    assert P.maker_fill(0.40, [0.45, 0.395, 0.39]) == 2            # 0.395 is not a full tick through 0.40
    assert P.maker_fill(0.40, [None, 0.39]) == 1
    assert P.maker_fill(0.05, [0.06, 0.04]) == 1


def test_kalshi_fee_import_rounds_up():
    assert P.kalshi_fee(100, 0.5) == 1.75
    assert P.kalshi_fee(1, 0.5) == 0.02


def test_black76_parity_and_implied_vol():
    F, K, s, T = 100.0, 110.0, 0.6, 30 / 365
    c, p = P.black76(F, K, s, T, 'C'), P.black76(F, K, s, T, 'P')
    assert abs((c - p) - (F - K)) < 1e-9
    assert abs(P.implied_vol(c, F, K, T, 'C') - s) < 1e-6
    assert P.implied_vol(0.0, F, K, T, 'C') is None


def test_forward_from_inverse_round_trip():
    S, F, K, s, T = 100000.0, 100550.0, 101000.0, 0.45, 30 / 365
    price_coin = P.black76(F, K, s, T, 'C') / F
    assert abs(P.forward_from_inverse(price_coin, K, s, T, 'C', S) - F) < 0.5
    price_coin = P.black76(F, 98000.0, s, T, 'P') / F
    assert abs(P.forward_from_inverse(price_coin, 98000.0, s, T, 'P', S) - F) < 0.5


def test_digital_flat_smile_is_n_d2_and_skew_moves_it():
    F, K, s, T = 100.0, 105.0, 0.5, 7 / 365
    v = s * math.sqrt(T)
    d2 = (math.log(F / K) - 0.5 * v * v) / v
    assert abs(P.digital_above(F, K, T, lambda k: s) - N.cdf(d2)) < 2e-4
    # a put skew (vol falling with strike) makes the up-digital richer than N(d2): -dsigma/dK > 0 adds probability
    skewed = P.digital_above(F, K, T, lambda k: s - 0.5 * k)
    assert skewed > N.cdf(d2)


def test_touch_prob_limits_and_reflection():
    S, s, T = 100.0, 0.5, 30 / 365
    assert P.touch_prob(S, 100.0, T, s) == 1.0
    assert P.touch_prob(S, 1e6, T, s) < 1e-9
    # driftless in the price (mu = 0): touch of an up barrier is about twice the terminal digital
    B = 110.0
    v = s * math.sqrt(T)
    dig = N.cdf((math.log(S / B) - 0.5 * v * v) / v)
    t = P.touch_prob(S, B, T, s, 0.0)
    assert 1.8 * dig < t < 2.2 * dig
    # down barrier symmetric case
    assert 0 < P.touch_prob(S, 90.0, T, s) < 1


def test_touch_prob_matches_monte_carlo():
    random.seed(5)
    S, B, s, T = 100.0, 108.0, 0.6, 7 / 365
    n_steps, n_paths = 2000, 3000
    dt = T / n_steps
    hits = 0
    for _ in range(n_paths):
        x = 0.0
        b = math.log(B / S)
        for _ in range(n_steps):
            x += -0.5 * s * s * dt + s * math.sqrt(dt) * random.gauss(0, 1)
            if x >= b:
                hits += 1
                break
    mc = hits / n_paths
    # discrete monitoring misses a little; allow 3 points
    assert abs(mc - P.touch_prob(S, B, T, s, 0.0)) < 0.03


def test_classify_questions():
    c = P.classify('Will the price of Bitcoin be above $74,000 on October 14?')
    assert c['kind'] == 'strike' and c['direction'] == 'above' and c['K'] == 74000 and c['coin'] == 'BTC'
    c = P.classify('Will the price of Ethereum be less than $2,100 on October 14?')
    assert c['kind'] == 'strike' and c['direction'] == 'below'
    c = P.classify('Will the price of Bitcoin be between $103K and $105K on June 10?')
    assert c['kind'] == 'range' and c['L'] == 103000 and c['U'] == 105000
    c = P.classify('Will Bitcoin reach $150,000 in October?')
    assert c['kind'] == 'touch_month' and c['direction'] == 'up' and c['month'] == 10
    c = P.classify('Will Bitcoin dip to 116.5k on August 16?')
    assert c['kind'] == 'touch_day' and c['direction'] == 'down' and c['K'] == 116500
    c = P.classify('Will Bitcoin reach $135K July 14–20?')
    assert c['kind'] == 'touch_week' and c['day'] == 14 and c['day2'] == 20
    assert P.classify('Will the price of Bitcoin be above $90,000 on October 14 at 4PM ET?') is None
    assert P.classify('Bitcoin Up or Down - October 14, 4PM ET') is None


def test_resolution_clock():
    end = P.parse_ts('2026-10-14T16:00:00Z')
    ws, T = P.resolution_clock(P.classify('Will the price of Bitcoin be above $74,000 on October 14?'), end)
    assert T == end and ws is None
    end = P.parse_ts('2026-11-01T04:00:00Z')
    ws, T = P.resolution_clock(P.classify('Will Bitcoin reach $150,000 in October?'), end)
    assert T == end and ws == P.parse_ts('2026-10-01T04:00:00Z')
    # winter time: the window ends at 05:00 UTC
    end = P.parse_ts('2026-01-01T05:00:00Z')
    ws, T = P.resolution_clock(P.classify('Will Bitcoin reach $150,000 in December?'), end)
    assert T == end and ws == P.parse_ts('2025-12-01T05:00:00Z')


def test_make_trade_taker_and_maker():
    hs = {'terminal|0.35-0.65': {'n': 10, 'median': 0.01}, 'all|0.35-0.65': {'n': 10, 'median': 0.01}}
    d = {'mid': 0.40, 'mid1': 0.42, 'p': 0.50, 't': 0.0, 'close': 86400.0, 'pay': 1.0, 'event': 'e', 'id': 'm',
         'kind': 'strike', 'path': [0.40, 0.38, 0.40, 0.41, 0.41, 0.41, 0.41]}
    tr = P.make_trade(d, 'both', 'taker', 0.05, hs)
    cost = 0.41 + 0.07 * 0.41 * 0.59
    assert tr['side'] == 'yes' and abs(tr['ret'] - (1 / cost - 1)) < 1e-12
    assert P.make_trade(d, 'no', 'taker', 0.02, hs) is None
    late = P.make_trade(d, 'both', 'taker', 0.05, hs, late=True)
    assert abs(late['p'] - (0.43 + 0.07 * 0.43 * 0.57)) < 1e-12
    # maker: limit = min(0.50 - 0.05, ask - tick) = 0.40; fills at the hourly mid 0.38 (two ticks through)
    mk = P.make_trade(d, 'yes', 'maker', 0.05, hs)
    assert mk is not None and abs(mk['p'] - 0.40) < 1e-12 and mk['t'] == 2 * 3600
    d2 = dict(d, path=[0.40, 0.395, 0.40, 0.41, 0.41, 0.41, 0.41])
    assert P.make_trade(d2, 'yes', 'maker', 0.05, hs) is None
