"""queue_live: the order digest is GPv2's (pinned to real CoW orders), the ladder arithmetic is the rule's, and the paper
ledger fills only from sells after a ladder's registration, with simulate_book's rule and one pool."""
import random
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import queue_book as Q   # noqa: E402
import queue_live as L   # noqa: E402

# Fetched from https://api.cow.fi/mainnet/api/v1/orders/<uid> on 2026-10-11 (raw response saved as
# research/queue_live/orders/cow_api_order_0x01a4bae6.json): a partially fillable sell of 150 WETH for at least
# 150.195 stETH, the same shape as the book's orders, executed in full in May 2026.
COW_SELL = {
    'uid': '0x01a4bae69ec8a25165a2e5a24d5e216f4843c29a94584202af8b5b510fd6d8567613bcb077bfe7781ff11cc8eb0c9271a056de4469f8847a',
    'owner': '0x7613bcb077bfe7781ff11cc8eb0c9271a056de44',
    'sellToken': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', 'buyToken': '0xae7ab96520de3a18e5e111b5eaab095312d7fe84',
    'receiver': '0x7613bcb077bfe7781ff11cc8eb0c9271a056de44', 'sellAmount': '150000000000000000000',
    'buyAmount': '150195000000000000000', 'validTo': 1777894522,
    'appData': '0x8d78cddb1ea9a618a8c94fea73e950b04e2643050155325b80a78bd8fcd9f8cf', 'feeAmount': '0', 'kind': 'sell',
    'partiallyFillable': True, 'sellTokenBalance': 'erc20', 'buyTokenBalance': 'erc20',
    'fullAppData': '{"appCode":"CoW Swap","environment":"production","metadata":{"orderClass":{"orderClass":"limit"},'
                   '"quote":{"slippageBips":0}},"version":"1.14.0"}'}
# From cow_fill_check's saved API data (research/2026-10-10/cow_fill_check/orders.json.gz): a buy-kind order.
COW_BUY = {
    'uid': '0x00fcecd389d03c0f96a400f58e180c297d13a08bf0b4110a07f48f837b53e05cf2ff84d45783bd64913903516fa44b419f26699869e977a2',
    'owner': '0xf2ff84d45783bd64913903516fa44b419f266998',
    'sellToken': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', 'buyToken': '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0',
    'receiver': '0xf2ff84d45783bd64913903516fa44b419f266998', 'sellAmount': '28506337869302968000',
    'buyAmount': '23211575844584715000', 'validTo': 1776908194,
    'appData': '0xf3ef4e1477de213e3c0a9dcc25112f3c62d65283db00bab8de61147b78f9a07b', 'feeAmount': '0', 'kind': 'buy',
    'partiallyFillable': True, 'sellTokenBalance': 'erc20', 'buyTokenBalance': 'erc20'}


# ------------------------------------------------------------------------------------------------- digest
def test_domain_separator_and_type_hash_are_gpv2_mainnet():
    assert L.domain_separator().hex() == 'c078f884a2676e1345748b1feace7b0abee5d00ecadb6e574dcdd109a63e8943'
    assert L.keccak_bytes(L.ORDER_TYPE.encode()).hex() == 'd5a25ba2e97094ad7d83dc28a6572da797d6b3e7fc6663bd93efb789fc17e489'


def test_digest_matches_real_filled_cow_orders():
    for api in (COW_SELL, COW_BUY):
        d = L.order_digest(L.api_order_fields(api))
        assert '0x' + d.hex() == api['uid'][:66]                      # the uid's first 32 bytes are the digest
        assert L.order_uid(d, api['owner'], api['validTo']) == api['uid']


def test_app_data_is_the_keccak_of_the_document():
    assert '0x' + L.keccak_bytes(COW_SELL['fullAppData'].encode()).hex() == COW_SELL['appData']
    assert L.APP_DATA == '0x' + L.keccak_bytes(L.APP_DATA_JSON.encode()).hex()


def test_every_signed_field_moves_the_digest():
    base = L.api_order_fields(COW_SELL)
    d0 = L.order_digest(base)
    for k, v in (('partiallyFillable', False), ('kind', 'buy'), ('validTo', 1777894523), ('buyAmount', '150195000000000000001'),
                 ('receiver', '0x' + '0' * 40), ('sellTokenBalance', 'external')):
        assert L.order_digest(dict(base, **{k: v})) != d0, k


# ------------------------------------------------------------------------------------------------- ladder
def test_ladder_arithmetic():
    e = L.ladder_entry(1.2, 2.0, 0.0365, hurdle_bps=1.0, redemption_fee_bps=0.5)
    assert abs(e['carry_bps'] - 2.0) < 1e-12                          # 3.65% a year for 2 days = 2bp
    assert abs(e['limit_discount_bps'] - 3.5) < 1e-12                 # hurdle + carry + redemption fee
    assert abs(e['limit_price_eth_per_token'] - 1.2 * (1 - 3.5e-4)) < 1e-15


def test_limit_wei_and_buy_amount_never_pay_above_the_limit():
    rng = random.Random(7)
    for _ in range(200):
        nav = rng.randrange(10 ** 18, 13 * 10 ** 17)
        lim_bps = rng.uniform(0.5, 40)
        lw = L.limit_price_wei(nav, lim_bps)
        assert Fraction(lw) <= Fraction(nav) * (1 - Fraction(lim_bps) / 10 ** 4)          # exact, not float
        assert Fraction(lw) >= Fraction(nav) * (1 - (Fraction(lim_bps) + Fraction(1, 10 ** 4)) / 10 ** 4) - 1
        sell = rng.randrange(10 ** 16, 10 ** 22)
        buy = L.buy_amount_for(sell, lw)
        assert sell * 10 ** 18 <= buy * lw                            # price = sell/buy at or under the limit
        assert sell * 10 ** 18 > (buy - 1) * lw                       # and the smallest such buyAmount


def _quote():
    toks = {}
    for sym, nav in (('stETH', 10 ** 18), ('wstETH', 1_246_013_674_805_236_000), ('weETH', 1_105_484_160_000_000_000),
                     ('rsETH', 1_081_738_520_000_000_000)):
        e = L.ladder_entry(nav / 1e18, 1.0, 0.025)
        e.update({'asset': L.TOKENS[sym]['asset'], 'address': L.TOKENS[sym]['address'], 'nav_wei': nav})
        toks[sym] = e
    return {'date': '2026-10-11', 'generated': '2026-10-11T00:01:00Z', 'pool_eth': 100.0, 'tokens': toks,
            'staking_apr': {'value': 0.025}, 'data_through': {'block': 1, 'utc': '2026-10-11T00:00:00Z'}}


def test_orders_are_unescrowed_full_pool_partial_sells_with_checkable_digests():
    q = _quote()
    out = L.build_orders(q, L.PLACEHOLDER_OWNER, 100.0, 1_800_000_000)
    assert out['owner_is_placeholder'] and len(out['orders']) == 4
    for o in out['orders']:
        x = o['order']
        assert x['sellToken'] == L.C.WETH and x['kind'] == 'sell' and x['partiallyFillable'] is True
        assert x['sellAmount'] == str(100 * 10 ** 18) and x['feeAmount'] == '0' and x['appData'] == L.APP_DATA
        assert x['receiver'] == L.PLACEHOLDER_OWNER                   # zero receiver = pay the signer
        assert o['check_price_at_or_under_limit'] and o['implied_discount_bps'] >= o['limit_discount_bps'] - 1e-6
        assert o['digest'] == '0x' + L.order_digest(x).hex()
        assert o['eip712']['message'] == x and o['eip712']['domain']['verifyingContract'] == L.SETTLEMENT_CHECKSUM
    owner = '0x' + 'ab' * 20
    out2 = L.build_orders(q, owner, 100.0, 1_800_000_000)
    assert all(o['uid'][66:106] == 'ab' * 20 and o['order']['receiver'] == owner for o in out2['orders'])


def test_wait_estimate_sees_requests_as_they_were_known():
    day = 86400
    now = 100 * day
    pts = [(now - 10 * day, 1.0, None),    # finalized at now - 9d
           (now - 7 * day, 3.0, None),     # finalized at now - 4d
           (now - 6 * day, 4.0, None),     # finalized at now - 2d
           (now - 5 * day, 6.0, None),     # finalized at now + 1d: pending at now, age 5
           (now - 1 * day, None, 1.0),     # pending, age 1
           (now - 30 * day, 2.0, None)]    # outside the 14 days
    assert L.wait_estimate(pts, now) == (3.0, 5, 14)                  # [1, 3, 4, 5, 1]
    # three days earlier: the 4- and 6-day requests were still pending (ages 3 and 2), the last one did not exist; four
    # requests are too few, so the window widens to 60 days and takes in the old 2-day request: [1, 3, 3, 2, 2]
    assert L.wait_estimate(pts, now - 3 * day) == (2.0, 5, 60)


def test_wait_estimate_widens_when_requests_are_few():
    now = 100 * 86400
    pts = [(now - 30 * 86400, 7.0, None), (now - 40 * 86400, 9.0, None)]
    w, n, window = L.wait_estimate(pts, now)
    assert window == 60 and n == 2 and w == 8.0


def test_staking_apr_from_nav_growth():
    t0 = 1_700_000_000
    xs = [(t0 + d * 86400, 1.2 * 1.03 ** (d / 365.0)) for d in range(0, 41)]
    assert abs(L.staking_apr(xs, t0 + 40 * 86400) - 0.03) < 1e-9


def test_register_is_append_only_and_refuses_stale_or_repeated_ladders(tmp_path):
    led = tmp_path / 'paper.jsonl'
    q = _quote()
    now = 1_791_677_000.0                                             # 2026-10-11T00:03:20Z
    row, msg = L.register(q, now, led)
    assert row and msg == 'registered' and row['registered_ts'] == now and row['valid_to_ts'] == now + 26 * 3600
    again, msg2 = L.register(q, now + 60, led)
    assert again is None and msg2.startswith('already registered')
    stale, msg3 = L.register(dict(q, date='2026-10-10'), now, led)
    assert stale is None and 'not today' in msg3
    assert len(L.read_ledger(led)) == 1


# ------------------------------------------------------------------------------------------------- paper ledger
T = 1_791_677_000          # a registration time


def _row(limit_bps=3.0, carry_bps=1.0, wait=2.0, reg=T, date='2026-10-11', pool=100.0, apr=0.025, tokens=('stETH',)):
    lad = {s: {'asset': L.TOKENS[s]['asset'], 'nav_eth': 1.0, 'wait_days': wait, 'carry_bps': carry_bps, 'hurdle_bps': limit_bps - carry_bps,
               'redemption_fee_bps': 0.0, 'limit_discount_bps': limit_bps, 'limit_price_eth_per_token': 1 - limit_bps / 1e4}
           for s in tokens}
    return {'date': date, 'registered_at': 'x', 'registered_ts': reg, 'valid_to_ts': reg + 26 * 3600, 'pool_eth': pool,
            'staking_apr': apr, 'ladder': lad}


def _sell(ts, disc, eth=50.0, fee=0.0, block=None, token='stETH'):
    return {'ts': ts, 'block': block or ts, 'li': 0, 'token': token, 'asset': L.TOKENS[token]['asset'], 'eth': eth,
            'usd': eth * 4000.0, 'discount_bps': disc, 'fee_bps': fee, 'tx': '0x%x' % ts, 'pool': 'p'}


def _score(rows, sells, market=None, wait=(2.0, True), exact=None):
    mk = {'lido': market or (lambda ts: None), 'etherfi_ev': lambda ts: None, 'kelp': lambda ts: None}
    return L.score_paper(rows, sells, mk, lambda a, ts: wait, lambda ts: 4000.0, T + 30 * 86400, exact)


def test_paper_fills_only_after_registration_and_at_or_beyond_the_limit():
    rows = [_row(limit_bps=3.0)]
    sells = [_sell(T - 600, 40.0),        # deep, but before the ladder existed
             _sell(T + 600, 2.9),         # after, but shallower than the limit
             _sell(T + 1200, 3.0),        # exactly at the limit: fills ("at or beyond")
             _sell(T + 1800, 25.0)]
    fills, s = _score(rows, sells)
    assert [f['ts'] for f in fills] == [T + 1200, T + 1800]
    assert s['counts']['before_first_ladder'] == 1


def test_a_sell_before_registration_cannot_fill_even_if_interpolation_puts_it_after():
    rows = [_row(limit_bps=3.0)]
    sells = [_sell(T + 30, 40.0, block=26_200_000)]                   # interpolated ts 30s after registration
    fills, s = _score(rows, sells, exact=lambda b: T - 5)            # the block's own timestamp is 5s before it
    assert fills == [] and s['counts']['before_first_ladder'] == 1
    fills, _ = _score(rows, sells, exact=lambda b: T + 12)           # and fills when the block really came after
    assert len(fills) == 1


def test_paper_capital_is_locked_for_the_measured_wait_and_released():
    rows = [_row(limit_bps=3.0, pool=100.0)]
    sells = [_sell(T + 100, 20.0, eth=80.0), _sell(T + 3700, 20.0, eth=50.0),      # only 20 ETH left an hour later
             _sell(T + 3 * 86400, 20.0, eth=50.0)]                                  # after the 2-day wait: all 100 back
    fills, s = _score(rows + [_row(limit_bps=3.0, reg=T + 86400, date='2026-10-12'),
                              _row(limit_bps=3.0, reg=T + 2 * 86400, date='2026-10-13')], sells)
    assert [round(f['eth'], 9) for f in fills] == [80.0, 20.0, 50.0]
    assert abs(s['peak_locked_eth'] - 100.0) < 1e-9 and abs(s['counts']['missed_capital_eth'] - 30.0) < 1e-9


def test_paper_values_at_the_limit_and_at_the_market():
    rows = [_row(limit_bps=3.0, carry_bps=1.0, wait=2.0, apr=0.025)]
    fills, s = _score(rows, [_sell(T + 100, 20.0, eth=50.0, fee=1.0)], market=lambda ts: 15.0)
    f = fills[0]
    carry = 0.025 * 2.0 / 365 * 1e4                                   # the measured wait's carry
    assert abs(f['capturable_bps'] - min(20.0 - 2 * 1.0, 15.0 - 1.0)) < 1e-12
    assert abs(f['value_eth_at_limit'] - (50.0 * (3.0 - carry) / 1e4 - 10.0 / 4000.0)) < 1e-12
    assert abs(f['value_eth_at_market'] - (50.0 * (14.0 - carry) / 1e4 - 10.0 / 4000.0)) < 1e-12


def test_unresolved_waits_are_provisional_and_never_shorter_than_registered():
    rows = [_row(limit_bps=3.0, wait=4.0)]
    fills, s = _score(rows, [_sell(T + 100, 20.0)], wait=(0.5, False))
    assert fills[0]['wait_days'] == 4.0 and not fills[0]['wait_resolved'] and s['provisional_fills'] == 1


def test_a_newer_ladder_supersedes_and_an_expired_one_stops():
    rows = [_row(limit_bps=3.0), _row(limit_bps=10.0, reg=T + 3600, date='2026-10-12')]
    fills, _ = _score(rows, [_sell(T + 1800, 5.0), _sell(T + 7200, 5.0), _sell(T + 7300, 12.0)])
    assert [(f['ts'], f['ladder_date']) for f in fills] == [(T + 1800, '2026-10-11'), (T + 7300, '2026-10-12')]
    fills, s = _score([_row(limit_bps=3.0)], [_sell(T + 27 * 3600, 30.0)])
    assert fills == [] and s['counts']['outside_any_ladder'] == 1


def test_with_the_same_parameters_the_paper_rule_is_simulate_books_rule():
    rng = random.Random(3)
    carry_day, wait, h = 0.7, 2.0, 1.0
    sells = []
    for i in range(400):
        ts = T + 60 + rng.randrange(60 * 86400)
        sells.append({'ts': ts, 'usd': rng.choice([2e4, 1e5, 5e5, 3e6]), 'discount_bps': rng.uniform(-5, 40),
                      'fee_bps': rng.choice([0.0, 1.0, 4.0]), 'pool': 'p', 'tx': '0x%x' % i})
    sells.sort(key=lambda s: s['ts'])
    market = (lambda ts: 20.0)
    env = {'sells': sells, 'wait': lambda ts: wait, 'carry': lambda ts: carry_day, 'market': market, 'accrues': False,
           'redemption_fee_bps': 0.0}
    ref, _ = Q.simulate_book({'lido': env}, 5e6, h)
    apr = carry_day * 365 / 1e4
    carry = carry_day * wait
    row = _row(limit_bps=h + carry, carry_bps=carry, wait=wait, pool=5e6, apr=apr)
    row['valid_to_ts'] = T + 90 * 86400
    ps = [{'ts': s['ts'], 'block': s['ts'], 'li': 0, 'token': 'stETH', 'asset': 'lido', 'eth': s['usd'], 'usd': s['usd'],
           'discount_bps': s['discount_bps'], 'fee_bps': s['fee_bps'], 'tx': s['tx'], 'pool': 'p'} for s in sells]
    got, _ = L.score_paper([row], ps, {'lido': market}, lambda a, ts: (wait, True), lambda ts: 1.0, T + 90 * 86400)
    assert [(f['ts'], round(f['usd'], 6)) for f in ref] == [(f['ts'], round(f['eth'], 6)) for f in got]
    assert all(abs(a['value_usd'] - b['value_eth_at_market']) < 1e-6 for a, b in zip(ref, got))


# ------------------------------------------------------------------------------------------------- criterion 4
def _world(market_by_asset, end_ts, buys_kept=None):
    flat = lambda ts: None
    W = {'base_last': 100, 'end_ts': end_ts, 'ts_at': lambda n: end_ts - 10 * 3600 if n == 101 else end_ts,
         'block_at': lambda ts: 1, 'nav_at': lambda k, n: 1.0, 'market': {k: market_by_asset.get(k, flat) for k in L.ETH3},
         'kept': {k: [{'pool': 'p', 'fee_bps': 1.0, 'ts': end_ts - 3600}] for k in L.ETH3},
         'pts': {k: [] for k in L.ETH3}, 'samples': {'wsteth_nav': []}}
    return W


def test_c4_passes_vacuously_without_a_dislocation():
    end = 1_791_700_000 // 3600 * 3600
    W = _world({'lido': lambda ts: 0.5}, end)
    c = L.criterion_4(W, [_row(limit_bps=3.0, reg=end - 20 * 3600, tokens=('stETH', 'wstETH', 'weETH', 'rsETH'))], [])
    assert c['hours_cleared'] == 0 and c['status'].startswith('pass (vacuous')


def test_c4_literal_flags_and_resting_order_evidence():
    end = 1_791_700_000 // 3600 * 3600
    rows = [_row(limit_bps=3.0, reg=end - 20 * 3600, tokens=('stETH', 'wstETH', 'weETH', 'rsETH'))]
    W = _world({'lido': lambda ts: 10.0}, end)                        # the market clears 3bp + 1bp fee all window
    c = L.criterion_4(W, rows, [])
    assert c['hours_flagged'] == c['hours_cleared'] > 0 and c['status'].startswith('pass: the literal check flagged')
    # a CoW buy at or beyond the limit in an hour clears that hour's flag
    h = end - 5 * 3600
    buy = {'token': 'stETH', 'asset': 'lido', 'block': 1, 'ts': h + 60, 'eth': 1.0, 'discount_bps': 3.5, 'owner': '0x1',
           'tx': '0x2', 'uid': '0xu', 'age_hours': None, 'limit_discount_bps': None}
    c2 = L.criterion_4(W, rows, [buy])
    assert c2['hours_flagged'] == c['hours_flagged'] - 1
    # an order created four hours before its fill, with a 5bp limit, sat through hours in which the market (10bp, less
    # a 1bp fee) cleared it: that is the kill criterion observed
    orders = {'0xu': {'creationDate': L.utc(h - 4 * 3600).replace('Z', '+00:00'), 'sellAmount': str(9995 * 10 ** 14),
                      'buyAmount': str(10 ** 18), 'kind': 'sell'}}
    c3 = L.criterion_4(W, rows, [buy], orders)
    assert c3['resting_orders']['orders_through_a_cleared_hour'] == 1 and c3['status'] == 'kill'


def test_resolved_day_fn():
    pts = [(10 * 86400 + 5, 1.0, None), (10 * 86400 + 9, None, 0.5), (12 * 86400, 2.0, None)]
    f = L.resolved_day_fn(pts)
    assert f(10) is False and f(11) is False and f(12) is True and f(13) is True and f(9) is True


def test_a_closed_redemption_path_gets_no_order_and_no_paper_bid():
    q = _quote()
    q['tokens']['rsETH']['path_open'] = False
    out = L.build_orders(q, L.PLACEHOLDER_OWNER, 100.0, 1_800_000_000)
    assert [o['token'] for o in out['orders']] == ['stETH', 'wstETH', 'weETH'] and 'rsETH' in out['skipped']
    row = _row(limit_bps=3.0, tokens=('stETH', 'rsETH'))
    row['ladder']['rsETH']['path_open'] = False
    fills, s = _score([row], [_sell(T + 100, 30.0, token='rsETH'), _sell(T + 200, 30.0)])
    assert [f['token'] for f in fills] == ['stETH'] and s['counts']['token_not_bid'] == 1


def test_the_limit_is_a_price_so_an_accruing_nav_deepens_it():
    row = _row(limit_bps=3.0, tokens=('wstETH',))
    row['ladder']['wstETH'].update({'nav_eth': 1.2, 'limit_price_eth_per_token': 1.2 * (1 - 3.0 / 1e4)})
    s = dict(_sell(T + 100, 3.5, token='wstETH'), nav=1.2 * (1 + 1.0 / 1e4))     # NAV up 1bp since registration
    fills, _ = _score([row], [s])
    assert fills == []                                                 # the order now sits ~4bp under NAV, not 3
    fills, _ = _score([row], [dict(s, discount_bps=4.5)])
    assert len(fills) == 1 and abs(fills[0]['limit_discount_bps'] - (1 - (1 - 3e-4) / (1 + 1e-4)) * 1e4) < 1e-9


# ------------------------------------------------------------------------------------------------- implementations
def _lenv(sells, wait=2.0, carry_day=0.5, market=None):
    return {'sells': sorted(sells, key=lambda s: s['ts']), 'wait': lambda ts: wait, 'carry': lambda ts: carry_day,
            'market': market or (lambda ts: None), 'accrues': False, 'redemption_fee_bps': 0.0}


def _ls(ts, disc, usd=1e6, fee=0.0):
    return {'ts': ts, 'usd': usd, 'discount_bps': disc, 'fee_bps': fee, 'pool': 'p', 'tx': '0x%x' % ts}


def test_one_resting_level_earns_its_depth_not_the_market():
    t = 1_700_000_000
    env = _lenv([_ls(t, 30.0), _ls(t + 10, 6.0)], wait=2.0, carry_day=0.5)          # edges 29 and 5 net of 1bp carry
    fills, st = L.simulate_levels({'a': env}, 1e7, [(1.0, lambda k, ts, c: 10.0)])
    assert [f['ts'] for f in fills] == [t] and abs(fills[0]['value_usd'] - (1e6 * 10.0 / 1e4 - 10.0)) < 1e-9
    assert abs(fills[0]['earned_bps'] - 10.0) < 1e-12 and st['crossing_sells'] == 1


def test_two_levels_shallow_first_and_the_deep_half_is_reserved():
    t = 1_700_000_000
    env = _lenv([_ls(t, 40.0, usd=8e6), _ls(t + 10, 15.0, usd=3e6), _ls(t + 20, 40.0, usd=3e6)], wait=5.0, carry_day=0.0)
    lv = [(0.5, lambda k, ts, c: 10.0), (0.5, lambda k, ts, c: 20.0)]
    fills, st = L.simulate_levels({'a': env}, 10e6, lv)
    # 8M crossing both: 5M at 10bp (the shallow half), 3M at 20bp; the 15bp sell finds the shallow half full; the last
    # 40bp sell takes the deep half's remaining 2M
    assert [(f['ts'], round(f['usd'])) for f in fills] == [(t, 8_000_000), (t + 20, 2_000_000)]
    assert abs(fills[0]['value_usd'] - (5e6 * 10 / 1e4 + 3e6 * 20 / 1e4 - 10)) < 1e-6
    assert [round(x) for x in st['by_level_filled_usd']] == [5_000_000, 5_000_000]


def test_levels_release_capital_after_the_wait_and_respect_late_entry():
    t = 1_700_000_000
    env = _lenv([_ls(t, 30.0, usd=1e7), _ls(t + 86400, 30.0, usd=1e7), _ls(t + 3 * 86400, 30.0, usd=1e7)], wait=2.0, carry_day=0.0)
    fills, _ = L.simulate_levels({'a': env}, 1e7, [(1.0, lambda k, ts, c: 5.0)])
    assert [f['ts'] for f in fills] == [t, t + 3 * 86400]
    env2 = _lenv([_ls(t, 30.0)], wait=2.0, carry_day=0.0, market=lambda ts: 30.0 if ts >= t - 3600 else 0.0)
    assert L.simulate_levels({'a': env2}, 1e7, [(1.0, lambda k, ts, c: 5.0)], delay_s=86400)[0] == []
    assert len(L.simulate_levels({'a': env2}, 1e7, [(1.0, lambda k, ts, c: 5.0)], delay_s=1800)[0]) == 1


def test_a_level_selects_the_sells_simulate_book_takes():
    rng = random.Random(11)
    t = 1_700_000_000
    sells = [_ls(t + rng.randrange(40 * 86400), rng.uniform(-5, 40), usd=rng.choice([1e6, 3e6]), fee=rng.choice([0.0, 1.0]))
             for _ in range(300)]
    env = _lenv(sells, wait=2.0, carry_day=0.7, market=lambda ts: 22.0)
    ref, _ = Q.simulate_book({'a': dict(env)}, 1e7, 3.0)
    got, _ = L.simulate_levels({'a': dict(env)}, 1e7, [(1.0, lambda k, ts, c: 3.0)])
    assert [(f['ts'], round(f['usd'], 6)) for f in ref] == [(f['ts'], round(f['usd'], 6)) for f in got]
    assert all(abs(g['value_usd'] - (g['usd'] * 3.0 / 1e4 - 10.0)) < 1e-6 for g in got)


def test_requote_limit_is_the_previous_days_market_inside_by_a_bp_floored_at_hurdle_plus_carry():
    day = 20_000
    env = _lenv([], wait=2.0, carry_day=0.5, market=lambda ts: 12.0 if ts < day * 86400 else 0.0)
    lim = L.requote_limits(env, day, day + 1, fee_bps=1.0)
    assert abs(lim[day] - (12.0 - 1.0 - 1.0)) < 1e-12                 # market less fee less 1bp
    assert abs(lim[day + 1] - (L.HURDLE + 1.0)) < 1e-12               # quiet day: the hurdle plus 2 days x 0.5bp


def test_hourly_requote_reads_only_the_last_completed_hour():
    h0 = 20_000 * 86400
    env = _lenv([], wait=1.0, carry_day=0.5, market=lambda ts: 9.0 if ts < h0 + 3600 else 30.0)
    lim = L.requote_limits(env, 20_000, 20_000, fee_bps=1.0, offset_s=0, period_s=3600, lookback_s=3600)
    assert abs(lim[h0 // 3600 + 1] - 7.0) < 1e-12                   # hour 1 sees hour 0's 9bp: 9 - 1 fee - 1 inside
    assert abs(lim[h0 // 3600 + 2] - 28.0) < 1e-12                  # hour 2 sees hour 1's 30bp, not its own


# ------------------------------------------------------------------------------------------------- v2 rule
def test_v2_limit_is_the_market_inside_a_bp_never_shallower_than_v1():
    assert L.v2_limit_bps(1.6, None) == 1.6                           # no venue traded: v1's limit
    assert L.v2_limit_bps(1.6, 0.4) == 1.6                            # quiet market: v1's floor
    assert abs(L.v2_limit_bps(5.0, 26.6) - 25.6) < 1e-12              # dislocated: 1bp inside the market


def test_market_24h_reads_the_whole_hours_before_the_data_end():
    end = 1_791_700_000
    h_end = end // 3600 * 3600
    W = {'market': {'kelp': lambda ts: 30.0 if ts >= h_end else (20.0 if ts >= h_end - 86400 else None)},
         'kept': {'kelp': [{'pool': 'a', 'fee_bps': 1.0, 'ts': end - 3600}, {'pool': 'b', 'fee_bps': 5.0, 'ts': end - 3600}]}}
    m, n = L.market_24h(W, 'kelp', end)
    assert n == 24 and abs(m - (20.0 - 3.0)) < 1e-12                  # the current hour's 30bp is not read; fee = median(1, 5)


def test_each_rule_version_is_its_own_paper_pool():
    v1 = dict(_row(limit_bps=3.0, pool=100.0), rule_version=1)
    v2 = dict(_row(limit_bps=20.0, reg=T + 3600, date='2026-10-12', pool=100.0), rule_version=2)
    sells = [_sell(T + 600, 25.0, eth=100.0), _sell(T + 7200, 25.0, eth=100.0)]
    f1, s1 = _score([v1], sells)
    f2, s2 = _score([v2], sells)
    assert [f['ts'] for f in f1] == [T + 600]                         # v1's pool is locked by its first fill
    assert [f['ts'] for f in f2] == [T + 7200] and abs(f2[0]['value_eth_at_limit'] - f1[0]['value_eth_at_limit']) > 0
    assert abs(f2[0]['value_eth_at_limit'] - (100.0 * (20.0 - 0.025 * 2 / 365 * 1e4) / 1e4 - 10 / 4000)) < 1e-9


# ------------------------------------------------------------------------------------------------- later purchases
def test_window_median_and_first_read_only_the_window():
    kept = [{'ts': 100, 'pool': 'a', 'discount_bps': 50.0, 'usd': 1.0},       # before the window: ignored
            {'ts': 3600, 'pool': 'a', 'discount_bps': 10.0, 'usd': 1.0}, {'ts': 3700, 'pool': 'a', 'discount_bps': 20.0, 'usd': 3.0},
            {'ts': 3800, 'pool': 'b', 'discount_bps': 4.0, 'usd': 1.0}, {'ts': 7200, 'pool': 'b', 'discount_bps': 99.0, 'usd': 1.0}]
    idx = L.trade_index(kept)
    assert abs(L.window_median(idx, 3600, 7200) - statistics_median([17.5, 4.0])) < 1e-12   # a: (10 + 60) / 4 = 17.5
    assert L.window_first(idx, 3600, 7200) == 10.0 and L.window_median(idx, 7300, 9000) is None
    assert L.window_first(idx, 7201, 9000) is None


def statistics_median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def _later_env(sells, kept, wait=2.0, carry_day=0.5, market=None):
    e = _lenv(sells, wait=wait, carry_day=carry_day, market=market or (lambda ts: 30.0))
    return e, {'a': L.trade_index(kept)}


def test_the_hourly_taker_buys_at_the_next_hour_at_the_later_price():
    H = 1_700_002_800 // 3600 * 3600 + 3600
    sell = _ls(H - 1800, 30.0, usd=1e6, fee=1.0)                     # print 30bp, 1bp pool fee
    later = [{'ts': H + 60, 'pool': 'p', 'discount_bps': 12.0, 'usd': 1e5}]
    e, idx = _later_env([sell], later, wait=2.0, carry_day=0.5)
    fills, st = L.simulate_later({'a': e}, 1e7, 1.0, 'median', 'hour', idx)
    f = fills[0]
    assert f['ts'] == H and abs(f['edge_bps'] - (min(30 - 2, 12 - 1) - 1.0)) < 1e-12     # capped at the later 12bp less a fee
    assert abs(f['own_edge_bps'] - (min(30 - 2, 30 - 1) - 1.0)) < 1e-12
    e2, idx2 = _later_env([sell], [{'ts': H + 60, 'pool': 'p', 'discount_bps': 2.0, 'usd': 1e5}])   # bought back by then
    fills2, st2 = L.simulate_later({'a': e2}, 1e7, 1.0, 'median', 'hour', idx2)
    assert fills2 == [] and st2['later_below_hurdle'] == 1
    e3, idx3 = _later_env([sell], [])                                     # nobody traded in the next hour
    assert L.simulate_later({'a': e3}, 1e7, 1.0, 'median', 'hour', idx3)[1]['later_missing'] == 1
    f4, _ = L.simulate_later({'a': e3}, 1e7, 1.0, 'lookback', 'hour', idx3)          # the 6h carry treats it as unchanged
    assert len(f4) == 1 and abs(f4[0]['edge_bps'] - (min(30 - 2, 30 - 1) - 1.0)) < 1e-12        # less the 1bp carry


def test_a_day_later_and_only_sells_that_qualified_in_their_own_hour():
    t = 1_700_000_000
    e, idx = _later_env([_ls(t, 30.0)], [{'ts': t + 86400 + 10, 'pool': 'p', 'discount_bps': 25.0, 'usd': 1e5}])
    fills, _ = L.simulate_later({'a': e}, 1e7, 1.0, 'first', 'day', idx)
    assert [f['ts'] for f in fills] == [t + 86400] and abs(fills[0]['edge_bps'] - 24.0) < 1e-12
    # the market showed nothing in the sell's own hour, so the taker never decides to buy it, however deep it gets later
    e2, idx2 = _later_env([_ls(t, 30.0)], [{'ts': t + 3700, 'pool': 'p', 'discount_bps': 40.0, 'usd': 1e5}],
                          market=lambda ts: 0.5 if ts < t + 3600 else 40.0)
    assert L.simulate_later({'a': e2}, 1e7, 1.0, 'median', 'hour', idx2)[0] == []


# ------------------------------------------------------------------------------------------------- v3 taker
def _taker_row(reg=T, carry=1.0, wait=2.0, pool=100.0):
    r = _row(limit_bps=1.0 + carry, carry_bps=carry, wait=wait, reg=reg, pool=pool, tokens=('stETH', 'rsETH'))
    return dict(r, rule_version=3)


def _taker(rows, sells, later, market=None):
    idx = {'lido': L.trade_index(later), 'etherfi_ev': L.trade_index([]), 'kelp': L.trade_index([])}
    mk = {'lido': market or (lambda ts: 30.0), 'etherfi_ev': lambda ts: None, 'kelp': lambda ts: None}
    return L.score_taker(rows, sells, mk, idx, lambda a, ts: (2.0, True), lambda ts: 4000.0, T + 30 * 86400)


def test_the_paper_taker_buys_at_the_next_hour_from_data_before_it():
    H = (T // 3600 + 2) * 3600
    sells = [_sell(H - 1800, 30.0, eth=50.0, fee=1.0), _sell(T - 100, 30.0)]      # the second is before registration
    later = [{'ts': H + 120, 'pool': 'p', 'discount_bps': 14.0, 'usd': 1e5}, {'ts': H + 1800, 'pool': 'p', 'discount_bps': 10.0, 'usd': 1e5}]
    fills, s = _taker([_taker_row()], sells, later)
    assert len(fills) == 1 and fills[0]['ts'] == H and s['counts']['sell_before_registration'] == 1
    f = fills[0]
    carry = 0.025 * 2 / 365 * 1e4
    assert abs(f['later_median_bps'] - 12.0) < 1e-12 and f['first_trade_bps'] == 14.0
    assert abs(f['value_eth_at_market'] - (50 * (min(28, 12 - 1) - carry) / 1e4 - 10 / 4000)) < 1e-12
    assert abs(f['value_eth_at_first_trade'] - (50 * (min(28, 14 - 1) - carry) / 1e4 - 10 / 4000)) < 1e-12
    assert abs(f['value_eth_at_limit'] - (50 * (1.0 + 1.0 - carry) / 1e4 - 10 / 4000)) < 1e-12


def test_the_paper_taker_skips_a_bought_back_pool_and_a_silent_hour():
    H = (T // 3600 + 2) * 3600
    sells = [_sell(H - 1800, 30.0)]
    assert _taker([_taker_row()], sells, [{'ts': H + 60, 'pool': 'p', 'discount_bps': 1.5, 'usd': 1e5}])[1]['counts']['later_below_hurdle'] == 1
    assert _taker([_taker_row()], sells, [])[1]['counts']['later_missing'] == 1


def test_register_writes_one_row_per_version_and_never_twice(tmp_path):
    led = tmp_path / 'paper.jsonl'
    q = dict(_quote(), register_versions=[2, 3], rule_version=2)
    for e in q['tokens'].values():
        e['v1_limit_discount_bps'] = e['limit_discount_bps']
    now = 1_791_677_000.0
    row, msg = L.register(q, now, led)
    rows = L.read_ledger(led)
    assert msg == 'registered v2, v3' and [r['rule_version'] for r in rows] == [2, 3] and rows[1]['rule_kind'] == 'taker'
    assert L.register(q, now + 60, led)[1].startswith('already registered') and len(L.read_ledger(led)) == 2
