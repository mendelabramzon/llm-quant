#!/usr/bin/env python3
"""Event-window alignment (no look-ahead), abnormal-return and P&L signs, outcomes, placebo exclusion, the keyword
screen, label validation and the freeze guard in governance_events, on synthetic data."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import governance_events as G  # noqa: E402

H, D, BAR = G.HOUR_MS, G.DAY_MS, G.BAR_MS
T0 = 1_780_000_000_000 // D * D        # a UTC midnight


def kl(prices, start=T0):
    """4h klines [open_ms, o, h, l, c, qv] whose closes are `prices`; bar i closes at start + (i + 1) * 4h."""
    return [[start + i * BAR, p, p, p, p, 1.0] for i, p in enumerate(prices)]


def flat(n, p=100.0):
    return [p] * n


class SeriesLookups(unittest.TestCase):
    def setUp(self):
        self.s = G.Series(kl([1.0, 2.0, 3.0, 4.0]), funding=[[T0 + 8 * H, 0.001], [T0 + 16 * H, 0.002]])

    def test_before_is_the_last_close_at_or_before(self):
        self.assertEqual(self.s.before(T0 + 4 * H), (T0 + 4 * H, 1.0))      # exactly at a close: that close
        self.assertEqual(self.s.before(T0 + 7 * H), (T0 + 4 * H, 1.0))      # never the next one
        self.assertIsNone(self.s.before(T0 + 3 * H))                         # nothing closed yet

    def test_after_is_the_first_close_at_or_after(self):
        self.assertEqual(self.s.after(T0 + 5 * H), (T0 + 8 * H, 2.0))
        self.assertEqual(self.s.after(T0 + 8 * H), (T0 + 8 * H, 2.0))
        self.assertIsNone(self.s.after(T0 + 17 * H))                         # past the last bar

    def test_stale_prices_are_refused(self):
        s = G.Series(kl([1.0]))
        self.assertIsNone(s.before(T0 + 4 * H + 3 * BAR))                    # more than two bars old

    def test_zero_volume_bars_are_not_prices(self):
        k = kl([1.0, 2.0, 3.0, 3.0, 3.0])
        for r in k[3:]:
            r[5] = 0.0                                                       # delisted: settlement price, no trades
        s = G.Series(k)
        self.assertEqual(s.before(T0 + 12 * H), (T0 + 12 * H, 3.0))
        self.assertIsNone(s.before(T0 + 12 * H + 3 * BAR))                   # flat bars after the delisting don't count
        self.assertIsNone(s.after(T0 + 13 * H))
        self.assertEqual(G.traded_span(k), (T0 + 4 * H, T0 + 12 * H))

    def test_funding_window_is_open_closed(self):
        self.assertAlmostEqual(self.s.funding(T0 + 8 * H, T0 + 16 * H), 0.002)   # (t0, t1]: the t0 payment excluded
        self.assertAlmostEqual(self.s.funding(T0, T0 + 16 * H), 0.003)
        self.assertAlmostEqual(self.s.funding(T0 + 16 * H, T0 + 24 * H), 0.0)


def event(C, S=None, E=None, token='AAA', label='VALUE_UP', i='e1'):
    S = C if S is None else S
    E = S + 3 * D if E is None else E
    return {'id': i, 'token': token, 'label': label, 'C': C, 'S': S, 'E': E, 'title': 't', 'outcome': 'passed'}


class AbnormalReturns(unittest.TestCase):
    def test_pre_window_ignores_the_jump_after_publication(self):
        n = 60
        # the token jumps 50% in the bar that closes 4h after publication at C = T0 + 20d
        C = T0 + 20 * D
        k = (C - T0) // BAR
        tok = [100.0 if i < k else 150.0 for i in range(n * 6)]
        series = {'AAA': G.Series(kl(tok)), 'BTC': G.Series(kl(flat(n * 6)))}
        for j in range(6):
            series['O%d' % j] = G.Series(kl(flat(n * 6, 10.0)))
        e = event(C)
        pre = G.window_ar(e, G.AR_WINDOWS['pre7'], series, series['BTC'])
        self.assertAlmostEqual(pre['ar_btc'], 0.0)                           # the publication-day jump is not in it
        c1 = G.window_ar(e, G.AR_WINDOWS['created+1d'], series, series['BTC'])
        self.assertAlmostEqual(c1['ar_btc'], math.log(1.5))
        self.assertAlmostEqual(c1['ar_ew'], math.log(1.5))                   # the basket is flat
        self.assertEqual(c1['n_basket'], 6)

    def test_basket_excludes_the_event_token_and_btc(self):
        n = 40 * 6
        up = [100.0 * (1.001 ** i) for i in range(n)]
        series = {'AAA': G.Series(kl(up)), 'BTC': G.Series(kl(up))}
        for j in range(5):
            series['O%d' % j] = G.Series(kl(flat(n)))
        a = G.window_ar(event(T0 + 20 * D), G.AR_WINDOWS['vote'], series, series['BTC'])
        self.assertAlmostEqual(a['ar_btc'], 0.0, places=9)
        self.assertGreater(a['ar_ew'], 0)                                    # beat a flat basket

    def test_too_few_basket_members_gives_no_ew(self):
        n = 40 * 6
        series = {'AAA': G.Series(kl(flat(n))), 'BTC': G.Series(kl(flat(n)))}
        a = G.window_ar(event(T0 + 20 * D), G.AR_WINDOWS['vote'], series, series['BTC'])
        self.assertIsNone(a['ar_ew'])
        self.assertAlmostEqual(a['ar_btc'], 0.0)


class TradePnL(unittest.TestCase):
    def setUp(self):
        n = 40 * 6
        self.btc = G.Series(kl(flat(n, 50_000.0)), funding=[[T0 + i * 8 * H, 0.0001] for i in range(n // 2)])
        self.up = [100.0 * math.exp(0.002 * i) for i in range(n)]

    def test_long_value_up_gains_when_the_token_beats_btc_and_pays_its_funding(self):
        tok = G.Series(kl(self.up), funding=[[T0 + i * 8 * H, 0.0003] for i in range(120)])
        e = event(T0 + 10 * D)
        tr = G.trade_pnl(e, G.TRADE_WINDOWS['end+1h>end+3d'], 1, {'AAA': tok}, self.btc, 0.002)
        self.assertGreater(tr['gross'], 0)
        self.assertLess(tr['funding'], 0)                                    # long pays 3bp, short BTC receives 1bp
        n_f = sum(1 for i in range(120) if tr['entry_t'] < T0 + i * 8 * H <= tr['exit_t'])
        self.assertEqual(n_f, 9)                                             # 3 days less 4h: nine 8h payments
        self.assertAlmostEqual(tr['funding'], -0.0002 * n_f, places=9)
        self.assertAlmostEqual(tr['pnl'], tr['gross'] + tr['funding'] - 0.002)
        self.assertAlmostEqual(tr['excess_ssr'], tr['pnl'] - G.SSR * tr['days'] / 365)

    def test_short_value_down_gains_when_the_token_falls(self):
        down = [100.0 * math.exp(-0.002 * i) for i in range(40 * 6)]
        tok = G.Series(kl(down), funding=[[T0 + i * 8 * H, 0.0003] for i in range(120)])
        tr = G.trade_pnl(event(T0 + 10 * D, label='VALUE_DOWN'), G.TRADE_WINDOWS['end+1h>end+3d'], -1,
                         {'AAA': tok}, self.btc, 0.0)
        self.assertGreater(tr['gross'], 0)
        self.assertGreater(tr['funding'], 0)                                 # short receives 3bp, long BTC pays 1bp

    def test_entry_waits_for_the_first_close_after_the_decision(self):
        tok = G.Series(kl(self.up))
        e = event(T0 + 10 * D, E=T0 + 13 * D + 2 * H)                        # vote ends 02:00
        tr = G.trade_pnl(e, G.TRADE_WINDOWS['end+1h>end+1d'], 1, {'AAA': tok}, self.btc, 0.0)
        self.assertEqual(tr['entry_t'], T0 + 13 * D + 4 * H)                 # decision 03:00 -> the 04:00 close
        self.assertGreaterEqual(tr['entry_t'], e['E'] + H)
        i0 = (tr['entry_t'] - T0) // BAR - 1
        self.assertAlmostEqual(tr['r_tok'], self.up[i0 + 6] / self.up[i0] - 1)  # 24h later, six bars on

    def test_start_plus_one_day_after_the_end_is_skipped(self):
        tok = G.Series(kl(self.up))
        e = event(T0 + 10 * D, S=T0 + 10 * D, E=T0 + 10 * D + 12 * H)        # a 12-hour vote
        self.assertIsNone(G.trade_pnl(e, G.TRADE_WINDOWS['start+1d>end'], 1, {'AAA': tok}, self.btc, 0.0))
        self.assertIsNotNone(G.trade_pnl(e, G.TRADE_WINDOWS['start+1d>end+3d'], 1, {'AAA': tok}, self.btc, 0.0))


class Outcomes(unittest.TestCase):
    def test_for_against(self):
        o = G.outcome(['For', 'Against', 'Abstain'], [70, 30, 500])
        self.assertEqual(o['result'], 'passed')
        self.assertAlmostEqual(o['margin'], 0.4)                             # abstain excluded
        self.assertEqual(G.outcome(['Yes', 'No'], [10, 90])['result'], 'failed')
        self.assertEqual(G.outcome(['Yay', 'Nay'], [10, 90])['result'], 'failed')

    def test_status_quo_options_fail(self):
        self.assertEqual(G.outcome(['Burn 10%', 'Burn 20%', 'Do nothing'], [1, 2, 9])['result'], 'failed')
        self.assertEqual(G.outcome(['Burn 10%', 'Burn 20%', 'Do nothing'], [1, 9, 2])['result'], 'passed')
        self.assertEqual(G.outcome(['Keep current emissions', 'Cut emissions'], [9, 1])['result'], 'failed')

    def test_quorum_and_ties(self):
        self.assertEqual(G.outcome(['For', 'Against'], [90, 10], scores_total=100, quorum=1000)['result'], 'failed')
        self.assertEqual(G.outcome(['A', 'B'], [5, 5])['result'], 'unclear')
        self.assertEqual(G.outcome(None, None)['result'], 'unclear')
        self.assertEqual(G.outcome(['For', 'Against'], [0, 0])['result'], 'unclear')


class Placebo(unittest.TestCase):
    def test_shifts_are_deterministic_and_15_to_30_days_each_side(self):
        a, b = G.placebo_shifts('abc'), G.placebo_shifts('abc')
        self.assertEqual(a, b)
        self.assertLess(a[0], -15 + 1e-9)
        self.assertGreater(a[1], 15 - 1e-9)
        self.assertTrue(all(15 <= abs(x) <= 30 for x in a))
        self.assertNotEqual(G.placebo_shifts('abd'), a)

    def test_placebo_window_must_be_clear_of_other_events(self):
        e = event(T0 + 50 * D)
        p = G.shifted(e, 20)
        self.assertEqual(p['C'] - e['C'], 20 * D)
        times = sorted([e['C'], T0 + 75 * D])                                # another event inside [C'-7d, E'+7d]
        self.assertFalse(G.placebo_ok(p, times))
        self.assertTrue(G.placebo_ok(p, sorted([e['C'], T0 + 95 * D])))
        self.assertTrue(G.placebo_ok(p, [e['C']]))                           # the original is 20 days away


class Anchors(unittest.TestCase):
    def test_start_is_never_before_publication(self):
        cands = [{'id': 'a', 'token': 'X', 'space': 's', 'title': 't', 'created': 1_000_000, 'start': 1_000_000 - 40 * 3600,
                  'end': 1_000_000 + 5 * 86400, 'choices': ['For', 'Against'], 'scores': [1, 0]}]
        labels = [{'id': 'a', 'label': 'VALUE_UP', 'surprise': True, 'confidence': 1, 'binding': 'unknown'}]
        e = G.build_events(cands, labels)[0]
        self.assertEqual(e['S'], e['C'])
        self.assertEqual(e['E'], (1_000_000 + 5 * 86400) * 1000)


class Dedupe(unittest.TestCase):
    def test_same_token_label_day_is_one_event(self):
        evs = [event(T0 + 1 * H, i='a'), event(T0 + 5 * H, i='b'), event(T0 + 5 * H, label='VALUE_DOWN', i='c'),
               event(T0 + D + H, i='d'), event(T0 + 2 * H, token='BBB', i='e')]
        self.assertEqual(sorted(x['id'] for x in G.dedupe_events(evs)), ['a', 'c', 'd', 'e'])


class Screen(unittest.TestCase):
    def test_terms(self):
        self.assertIn(r'fee[ -]?switch', G.screen_terms('Activate the fee switch', ''))
        self.assertIn(r'buy[ -]?backs?\b', G.screen_terms('Proposal', 'a buyback of 1M'))
        self.assertEqual(G.screen_terms('Add DAI market', 'risk parameters'), [])
        self.assertEqual(G.screen_terms('Proposal', 'the treasury will pay'), [])      # treasury counts in titles only
        self.assertIn('title:treasury', G.screen_terms('Treasury report', ''))
        self.assertEqual(G.screen_terms('Unburnable', 'burnout'), [])

    def test_routine_titles(self):
        self.assertTrue(G.routine('[BIP-237] Enable USH - ETH 50/50 Gauge with 10% emission cap'.replace('emission', 'x')))
        self.assertTrue(G.routine('[ARFC] Onboard ezETH to Aave V3 Lido Instance'))
        self.assertTrue(G.routine('Proposal for a Telos Syrup Pool and Farm'))
        self.assertFalse(G.routine('[BIP-237] Enable Gauge with a 10% emission cap'))       # a value term keeps it
        self.assertFalse(G.routine('Reduce CAKE emissions on farms'))
        self.assertFalse(G.routine('Activate the fee switch'))
        self.assertFalse(G.routine('Increase supply caps'.replace('supply caps', 'supply')))

    def test_keyword_label(self):
        self.assertEqual(G.keyword_label('Buyback and burn', ''), 'VALUE_UP')
        self.assertEqual(G.keyword_label('Grant program for builders', ''), 'VALUE_DOWN')
        self.assertEqual(G.keyword_label('Buyback funded by a token sale', ''), 'NEUTRAL')
        self.assertEqual(G.keyword_label('Onboard wstETH', ''), 'NEUTRAL')

    def test_open_space_authors(self):
        props = ([{'space_id': 'cakevote.eth', 'author': 'team', 'votes': 900}] * 6 +
                 [{'space_id': 'cakevote.eth', 'author': 'spam', 'votes': 40}] * 60 +
                 [{'space_id': 'cakevote.eth', 'author': 'once', 'votes': 5000}])
        self.assertEqual(G.core_authors(props)['cakevote.eth'], {'team'})

    def test_packet_hides_everything_but_the_text(self):
        r = {'id': 'x', 'token': 'UNI', 'space': 's', 'created': 1_700_000_000, 'title': 'T', 'choices': ['For'],
             'body_head': 'b', 'keywords': ['k'], 'control': True, 'scores': [1], 'keyword_label': 'VALUE_UP'}
        self.assertEqual(sorted(G.label_packet(r)), ['choices', 'date', 'id', 'space', 'text', 'title', 'token'])


class Labels(unittest.TestCase):
    def test_validation(self):
        cands = [{'id': 'a'}, {'id': 'b'}]
        ok = {'label': 'VALUE_UP', 'surprise': True, 'confidence': 0.9}
        _, probs = G.validate_labels(cands, [dict(ok, id='a'), dict(ok, id='b')])
        self.assertEqual(probs, [])
        _, probs = G.validate_labels(cands, [dict(ok, id='a'), dict(ok, id='a'), dict(ok, id='z', label='UP')])
        self.assertTrue(any('duplicate' in p for p in probs))
        self.assertTrue(any('unknown id z' in p for p in probs))
        self.assertTrue(any('missing b' in p for p in probs))
        _, probs = G.validate_labels(cands[:1], [dict(ok, id='a', confidence=1.5, surprise='yes')])
        self.assertEqual(len(probs), 2)

    def test_kappa(self):
        self.assertAlmostEqual(G.cohen_kappa(['VALUE_UP', 'NEUTRAL'] * 5, ['VALUE_UP', 'NEUTRAL'] * 5), 1.0)
        self.assertLess(G.cohen_kappa(['VALUE_UP', 'NEUTRAL'] * 5, ['NEUTRAL', 'VALUE_UP'] * 5), 0)

    def test_analyze_refuses_unfrozen_or_changed_labels(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / 'labels.jsonl').write_text('{"id": "a"}\n')
            args = type('A', (), {'out': d, 'cutoff': None, 'size': 25_000, 'alt_size': 100_000, 'min_events': 15})()
            G.write_json(out / 'manifest.json', {})
            with self.assertRaises(SystemExit):
                G.cmd_analyze(args)
            G.write_json(out / 'manifest.json', {'labels_frozen': {'sha256': 'not-the-hash', 'at': 'x', 'cutoff': 'y'}})
            with self.assertRaises(SystemExit) as cm:
                G.cmd_analyze(args)
            self.assertIn('changed', str(cm.exception))


class Stats(unittest.TestCase):
    def test_cluster_by_week_averages_within_a_week(self):
        mon = T0 - ((T0 // D + 3) % 7) * D                                    # 1970-01-01 was a Thursday
        pairs = [(mon + H, 1.0), (mon + 2 * D, 3.0), (mon + 7 * D, 10.0)]
        self.assertEqual(G.cluster_means(pairs, 'week'), [2.0, 10.0])
        self.assertEqual(G.cluster_means(pairs, 'day'), [1.0, 3.0, 10.0])
        d = G.describe(pairs + [(mon + 14 * D, -1.0)])
        self.assertEqual(d['n'], 4)
        self.assertEqual(d['weeks'], 3)
        self.assertAlmostEqual(d['hit'], 0.75)


class Books(unittest.TestCase):
    def test_impact_and_depth(self):
        book = {'bids': [['99.9', '100'], ['99.0', '1000']], 'asks': [['100.1', '100'], ['101.0', '1000']]}
        s = G.book_summary(book, sizes=(5_000, 20_000, 1_000_000))
        self.assertAlmostEqual(s['mid'], 100.0)
        self.assertAlmostEqual(s['half_spread_bps'], 10.0)
        self.assertAlmostEqual(s['impact_bps_5k'], 10.0, places=6)           # fills at the touch on both sides
        self.assertGreater(s['impact_bps_20k'], 10.0)                        # walks past the $9,990 at the touch
        self.assertIsNone(s['impact_bps_1000k'])                             # too thin
        self.assertAlmostEqual(s['bid_depth_25bp'], 99.9 * 100)

    def test_symbol_resolution(self):
        xi = {'symbols': [{'symbol': 'FLOKIUSDT', 'contractType': 'PERPETUAL', 'quoteAsset': 'USDT', 'status': 'SETTLING'},
                          {'symbol': '1000FLOKIUSDT', 'contractType': 'PERPETUAL', 'quoteAsset': 'USDT', 'status': 'TRADING'},
                          {'symbol': 'BALUSDT', 'contractType': 'PERPETUAL', 'quoteAsset': 'USDT', 'status': 'SETTLING'}]}
        r = G.resolve_symbols(xi, ['FLOKI', 'BAL', 'NOPE'])
        self.assertEqual(r['FLOKI'], ['1000FLOKIUSDT', 1000, 'TRADING'])
        self.assertEqual(r['BAL'][0], 'BALUSDT')
        self.assertNotIn('NOPE', r)

    def test_pair_costs(self):
        books = {'AAA': {'impact_bps_100k': 10.0}, 'BBB': {'impact_bps_100k': 30.0}, 'CCC': {'impact_bps_100k': None}}
        c, fb = G.pair_costs(books, ['AAA', 'CCC', 'DDD'], 100_000)
        self.assertAlmostEqual(c['AAA'], (4 * G.TAKER_BPS + 20 + 2 * G.BTC_HALF_SPREAD_BPS) / 1e4)
        self.assertEqual(fb, 30.0)                                           # delisted / unfillable get the 75th pct
        self.assertAlmostEqual(c['DDD'], (4 * G.TAKER_BPS + 60 + 2 * G.BTC_HALF_SPREAD_BPS) / 1e4)


if __name__ == '__main__':
    unittest.main()


class EndToEnd(unittest.TestCase):
    """analyze + render on a fabricated study: VALUE_UP tokens rise 10% over the week after the vote ends, everything
    else is flat, so the up-long variants must show a positive mean and placebo near zero."""

    def test_pipeline(self):
        import random as _r
        rng = _r.Random(1)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            n_bars = 900 * 6
            toks = ['T%d' % i for i in range(8)]
            events, cands, labels = [], [], []
            start = T0
            for k in range(60):
                tok = toks[k % 8]
                C = start + (40 + k * 12) * D + 3 * H
                lab = 'VALUE_UP' if k % 3 else 'VALUE_DOWN'
                cands.append({'id': 'p%d' % k, 'token': tok, 'space': 's', 'title': 'title %d' % k, 'created': C // 1000,
                              'start': C // 1000, 'end': (C + 5 * D) // 1000, 'choices': ['For', 'Against'],
                              'scores': [9, 1], 'scores_total': 10, 'quorum': 0, 'control': False,
                              'keyword_label': lab, 'votes': 50})
                labels.append({'id': 'p%d' % k, 'token': tok, 'space': 's', 'label': lab, 'surprise': True,
                               'confidence': 0.9, 'binding': 'unknown', 'reason': 'r', 'control': False,
                               'keyword_label': lab, 'created_utc': G.utc_iso(C)})
                events.append((tok, C + 5 * D, 1 if lab == 'VALUE_UP' else -1))
            prices = {t: [100.0] * n_bars for t in toks}
            for tok, E, sgn in events:                                       # +-10% ramp over end..end+7d, kept
                i0 = (E - start) // BAR
                for i in range(i0, n_bars):
                    prices[tok][i] *= 1 + 0.10 * sgn * min(1.0, (i - i0) / 42.0)
            raw = out / 'raw' / 'binance'
            man = {'prices': {'tokens': {}}}
            for t in toks + ['BTC']:
                p = prices.get(t, [50_000.0] * n_bars)
                p = [x * (1 + 0.0005 * rng.uniform(-1, 1)) for x in p]
                G.write_gz(raw / 'klines_4h' / (t + 'USDT.json.gz'), [[start + i * BAR, x, x, x, x, 1.0]
                                                                        for i, x in enumerate(p)])
                G.write_gz(raw / 'funding' / (t + 'USDT.json.gz'), [[start + i * 8 * H, 0.0] for i in range(n_bars // 2)])
                man['prices']['tokens'][t] = {'symbol': t + 'USDT', 'status': 'TRADING'}
            G.write_jsonl(out / 'candidates.jsonl', cands)
            G.write_jsonl(out / 'labels.jsonl', labels)
            man['labels_frozen'] = {'at': 'x', 'sha256': G.sha256_file(out / 'labels.jsonl'),
                                    'cutoff': G.utc_iso(start + 400 * D)}
            G.write_json(out / 'manifest.json', man)
            G.write_json(out / 'raw' / 'books.json', {'books': {t: {'impact_bps_25k': 5.0, 'impact_bps_100k': 20.0}
                                                                for t in toks}})
            args = type('A', (), {'out': d, 'cutoff': None, 'size': 25_000, 'alt_size': 100_000, 'min_events': 5})()
            self.assertEqual(G.cmd_analyze(args), 0)
            A = json.loads((out / 'analysis.json').read_text())
            R = A['by_labeler']['llm']
            v = next(x for x in R['variants'] if (x['window'], x['side'], x['filter']) == ('end+1h>end+7d', 'up_long', 'all'))
            self.assertGreater(v['in']['mean'], 0.05)
            self.assertAlmostEqual(v['placebo_mean_in'], -(4 * G.TAKER_BPS + 10 + 1) / 1e4, places=2)
            self.assertLess(v['mean_out_alt_size'], v['out']['mean'])        # bigger size, bigger cost
            dn = next(x for x in R['variants'] if (x['window'], x['side'], x['filter']) == ('end+1h>end+7d', 'down_short', 'all'))
            self.assertGreater(dn['in']['mean'], 0.05)                       # shorting the falling token pays
            ar = R['ar']['VALUE_UP']['end+7d']['ar_ew']['all']
            self.assertGreater(ar['mean'], 0.05)
            pre = R['ar']['VALUE_UP']['pre7']['ar_ew']['all']
            self.assertLess(abs(pre['mean']), 0.05)                          # nothing before publication
            self.assertIsNotNone(R['chosen'])
            self.assertEqual(G.cmd_render(type('A', (), {'out': d})()), 0)
            self.assertIn('Trades', (out / 'tables.md').read_text())
