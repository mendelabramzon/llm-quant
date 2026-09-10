#!/usr/bin/env python3
"""Funding history for every live perpetual on Hyperliquid and its HIP-3 builder DEXes, and what each rate did next.

Why. The 2026-09-08 perp study found a 285% funding rate on a HIP-3 oil market and priced it on a single hour: the
rate, the round trip, the break-even. A rate's value is its size times how long it holds, and one hour cannot say how
long. The venue's `fundingHistory` endpoint pages back for months at hourly resolution and carries the premium beside
the rate, so the decay ledger the study asked for can be built retroactively rather than waited for.

What this produces, offline from the collected series:

  * per market: how often the rate was extreme, the longest one-sided run, sign flips, how much of its own premium
    the venue charged;
  * episodes: every run of hours where |APR| stayed above a threshold on one side, with the funding the paid side
    collected, the mark move over the same hours, and what the rate was 24 and 72 hours after the run ended;
  * premium snaps: hours where the premium jumped by more than a threshold while the mark did not, which is what an
    oracle roll or an oracle correction looks like from the funding series alone;
  * an out-of-sample test of an earlier window's `funding_carry` hits: what a position taken at that window's close
    on the paid side actually earned, hour by hour, against the round trip the hit quoted.

Sign conventions, used everywhere: Hyperliquid funding is positive when longs pay shorts. A position's funding
*received* per hour is `-side * rate` with side = +1 for long and -1 for short. Mark PnL is `side * (exit/entry - 1)`.
The hedged proxy replaces the mark move with the change in the venue's premium, which is what a position hedged in the
oracle's underlying would experience if the hedge tracked the oracle exactly; it is a proxy because the premium is an
hourly average against impact prices and the hedge instrument is not the oracle.

    uv run python scripts/perp_history.py collect --out research/2026-09-10/perps_history --since 2026-07-01
    uv run python scripts/perp_history.py analyze --out research/2026-09-10/perps_history --window research/2026-09-08/perps_1h
    uv run python scripts/perp_history.py render  --out research/2026-09-10/perps_history
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from perp_rpc import Info, APIError, perp_dexes, meta_and_ctxs, candles, funding_history  # noqa: E402
from perp_collect import safe, read_gz, write_gz, write_json, dex_key, utc  # noqa: E402

HOUR_MS = 3_600_000
HOURS_PER_YEAR = 8760.0
PAGE = 500          # fundingHistory returns at most this many rows per call


def fnum(v, d=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def hour_of(ms):
    """The funding hour a timestamp belongs to: payments land a few milliseconds after the boundary."""
    return int((ms + HOUR_MS // 2) // HOUR_MS * HOUR_MS)


# ---------------------------------------------------------------------------------------------- collect

def live_universe(api, dexes=None):
    rows = []
    for d in perp_dexes(api):
        dk = dex_key(d)
        if dexes is not None and (dk or 'core') not in dexes:
            continue
        mult = dict(d.get('assetToFundingMultiplier') or []) if d else {}
        caps = dict(d.get('assetToStreamingOiCap') or []) if d else {}
        meta = meta_and_ctxs(api, dk)
        for m, c in zip(meta[0]['universe'], meta[1]):
            if m.get('isDelisted'):
                continue
            rows.append({'dex': dk or 'core', 'coin': m['name'], 'max_leverage': m.get('maxLeverage'),
                         'funding_multiplier': fnum(mult.get(m['name'])), 'oi_cap': fnum(caps.get(m['name'])),
                         'oi': fnum(c.get('openInterest')), 'mark': fnum(c.get('markPx')),
                         'day_ntl_vlm': fnum(c.get('dayNtlVlm'))})
    return rows


def page_funding(api, coin, start_ms, end_ms):
    rows, s = [], start_ms
    for _ in range(400):
        r = funding_history(api, coin, s, end_ms) or []
        rows.extend(r)
        if len(r) < PAGE:
            break
        last = int(r[-1]['time'])
        if last >= end_ms or last + 1 <= s:
            break
        s = last + 1
    return rows


def page_candles(api, coin, start_ms, end_ms, interval='1h'):
    rows = list(candles(api, coin, interval, start_ms, end_ms) or [])
    batch = rows
    for _ in range(40):
        if not rows or rows[0]['t'] <= start_ms + HOUR_MS or len(batch) < PAGE:
            break
        batch = list(candles(api, coin, interval, start_ms, rows[0]['t'] - 1) or [])
        if not batch or batch[0]['t'] >= rows[0]['t']:
            break
        rows = batch + rows
    return rows


def merge_rows(old, new, key):
    d = {int(r[key]): r for r in old}
    d.update({int(r[key]): r for r in new})
    return [d[k] for k in sorted(d)]


def cmd_collect(args):
    out = Path(args.out)
    api = Info(interval=args.interval)
    t0 = time.time()
    end_ms = int(t0 * 1000) // HOUR_MS * HOUR_MS
    since_ms = int(dt.datetime.fromisoformat(args.since).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    dexes = set(args.dexes.split(',')) if args.dexes else None
    uni = live_universe(api, dexes)
    prior = json.loads((out / 'universe.json').read_text())['markets'] if (out / 'universe.json').exists() else []
    if args.coins:
        # A subset run (a retry of the markets that failed) updates those entries and keeps the rest of the universe,
        # so the analysis that follows still sees every market collected so far.
        want = set(args.coins)
        uni = [u for u in uni if u['coin'] in want]
        merged = {u['coin']: u for u in prior}
        merged.update({u['coin']: u for u in uni})
        full = [merged[k] for k in sorted(merged)]
    else:
        full = uni
    write_json(out / 'universe.json', {'collected_at': utc(t0), 'since_utc': utc(since_ms / 1000),
                                       'until_utc': utc(end_ms / 1000), 'markets': full})
    print(json.dumps({'markets': len(uni), 'since': utc(since_ms / 1000), 'until': utc(end_ms / 1000)}), flush=True)

    def one(u):
        coin = u['coin']
        rec = {'coin': coin, 'funding_rows': 0, 'candle_rows': 0, 'error': None}
        try:
            fp = out / 'funding' / (safe(coin) + '.json.gz')
            old = read_gz(fp) if fp.exists() else []
            s = (int(old[-1]['time']) + 1) if old else since_ms
            new = page_funding(api, coin, s, end_ms) if s < end_ms else []
            rows = merge_rows(old, new, 'time')
            write_gz(fp, rows)
            rec['funding_rows'] = len(rows)
            cp = out / 'candles_1h' / (safe(coin) + '.json.gz')
            oldc = read_gz(cp) if cp.exists() else []
            sc = (int(oldc[-1]['t']) + HOUR_MS) if oldc else since_ms
            newc = page_candles(api, coin, sc, end_ms) if sc < end_ms else []
            crows = merge_rows(oldc, newc, 't')
            write_gz(cp, crows)
            rec['candle_rows'] = len(crows)
        except APIError as e:
            rec['error'] = str(e)[:160]
        return rec

    recs = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, rec in enumerate(ex.map(one, uni), 1):
            recs.append(rec)
            if i % 25 == 0:
                print(json.dumps({'done': i, 'of': len(uni), 'elapsed_s': round(time.time() - t0), **api.stats()}),
                      flush=True)
    # Totals are counted from disk so a subset run reports the whole collection, not the retry.
    n_f = n_c = 0
    for u in full:
        fp = out / 'funding' / (safe(u['coin']) + '.json.gz')
        cp = out / 'candles_1h' / (safe(u['coin']) + '.json.gz')
        n_f += len(read_gz(fp)) if fp.exists() else 0
        n_c += len(read_gz(cp)) if cp.exists() else 0
    prior_fail = json.loads((out / 'manifest.json').read_text()).get('failures', {}) if (out / 'manifest.json').exists() else {}
    fails = {k: v for k, v in prior_fail.items() if k not in {u['coin'] for u in uni}}
    fails.update({r['coin']: r['error'] for r in recs if r['error']})
    man = {'collected_at': utc(t0), 'finished_at': utc(), 'venue': 'hyperliquid',
           'info_url': 'https://api.hyperliquid.xyz/info', 'since_ms': since_ms, 'until_ms': end_ms,
           'since_utc': utc(since_ms / 1000), 'until_utc': utc(end_ms / 1000), 'candle_interval': '1h',
           'markets': len(full), 'markets_this_run': len(uni), 'funding_rows': n_f, 'candle_rows': n_c,
           'failures': fails, 'api': api.stats(), 'seconds': round(time.time() - t0, 1)}
    write_json(out / 'manifest.json', man)
    print(json.dumps({k: v for k, v in man.items() if k != 'failures'}, indent=1))
    print(json.dumps({'failures': len(man['failures'])}))
    return 0


# ---------------------------------------------------------------------------------------------- pure analysis

def hourly_series(funding_rows, candle_rows):
    """One record per funding hour. The candle that ends at hour h is the one with t == h - 1h."""
    by_hour = {}
    for r in funding_rows:
        h = hour_of(int(r['time']))
        by_hour[h] = {'t': h, 'rate': fnum(r.get('fundingRate')), 'premium': fnum(r.get('premium'))}
    cl = {}
    for c in candle_rows or []:
        cl[int(c['t']) + HOUR_MS] = c
    for h, rec in by_hour.items():
        c = cl.get(h)
        if c:
            rec['close'] = fnum(c.get('c'))
            rec['open'] = fnum(c.get('o'))
            rec['high'] = fnum(c.get('h'))
            rec['low'] = fnum(c.get('l'))
            rec['volume_usd'] = (fnum(c.get('v'), 0.0) or 0.0) * (fnum(c.get('c'), 0.0) or 0.0)
            rec['trades'] = int(c.get('n') or 0)
        else:
            rec.update({'close': None, 'open': None, 'high': None, 'low': None, 'volume_usd': None, 'trades': None})
    return [by_hour[h] for h in sorted(by_hour)]


def side_sign(side):
    return 1 if side == 'long' else -1


def paid_side(rate):
    """Who collects: negative funding means shorts pay longs."""
    return 'long' if rate < 0 else 'short'


def received(rate, side):
    """Funding received per hour, as a fraction of notional, by a position on `side`."""
    return -side_sign(side) * rate


def hold(series, i0, side, hours=None):
    """A position opened at the close of `series[i0]` and held for `hours` payments (or to the end).

    Returns the cumulative path so a caller can read the realised break-even hour and the drawdown, not just the end.
    """
    s = side_sign(side)
    entry = series[i0].get('close')
    p0 = series[i0].get('premium')
    n = len(series) - 1 - i0 if hours is None else min(hours, len(series) - 1 - i0)
    path, fund, best, worst_dd = [], 0.0, 0.0, 0.0
    for k in range(1, n + 1):
        r = series[i0 + k]
        if r.get('rate') is None:
            continue
        fund += received(r['rate'], side)
        mark = (s * (r['close'] / entry - 1)) if (entry and r.get('close')) else None
        hedged = (s * (r['premium'] - p0)) if (p0 is not None and r.get('premium') is not None) else None
        total = (fund + mark) if mark is not None else None
        if total is not None:
            best = max(best, total)
            worst_dd = min(worst_dd, total - best)
        path.append({'t': r['t'], 'funding': fund, 'mark': mark, 'hedged_proxy': hedged, 'total': total})
    return {'entry_t': series[i0]['t'], 'entry': entry, 'premium_entry': p0, 'hours': len(path), 'path': path,
            'funding': fund, 'mark': path[-1]['mark'] if path else None,
            'hedged_proxy': (fund + path[-1]['hedged_proxy']) if (path and path[-1]['hedged_proxy'] is not None) else None,
            'total': path[-1]['total'] if path else None, 'max_drawdown': worst_dd}


def episodes(series, min_apr=1.0, min_hours=1):
    """Runs of consecutive hours where |APR| >= min_apr on the same paid side."""
    out, i, n = [], 0, len(series)
    by_t = {r['t']: r for r in series}
    while i < n:
        r = series[i]
        if r.get('rate') is None or abs(r['rate']) * HOURS_PER_YEAR < min_apr:
            i += 1
            continue
        side = paid_side(r['rate'])
        j = i
        while j + 1 < n and series[j + 1].get('rate') is not None and paid_side(series[j + 1]['rate']) == side \
                and abs(series[j + 1]['rate']) * HOURS_PER_YEAR >= min_apr \
                and series[j + 1]['t'] - series[j]['t'] == HOUR_MS:
            j += 1
        hours = j - i + 1
        if hours >= min_hours:
            rates = [abs(series[k]['rate']) for k in range(i, j + 1)]
            # Enter at the close before the first extreme payment; exit at the close of the first hour whose rate is
            # back under the threshold. Exiting on the last extreme hour would compare the premium at its most extreme
            # with the premium before the run began, and score every episode against the paid side by construction.
            i_entry = max(i - 1, 0)
            i_exit = min(j + 1, n - 1)
            h = hold(series, i_entry, side, hours=i_exit - i_entry)
            after24 = by_t.get(series[j]['t'] + 24 * HOUR_MS)
            after72 = by_t.get(series[j]['t'] + 72 * HOUR_MS)
            flip = None
            look = [x for x in series[j + 1:j + 73] if x.get('rate') is not None]
            if look:
                flip = any(paid_side(x['rate']) != side and abs(x['rate']) > 0 for x in look)
            out.append({'start_t': series[i]['t'], 'end_t': series[j]['t'], 'hours': hours, 'side': side,
                        'mean_apr': statistics.fmean(rates) * HOURS_PER_YEAR,
                        'max_apr': max(rates) * HOURS_PER_YEAR,
                        'funding_received': h['funding'], 'mark_pnl': h['mark'],
                        'total_unhedged': h['total'], 'hedged_proxy': h['hedged_proxy'],
                        'max_drawdown': h['max_drawdown'],
                        'premium_start': series[i_entry].get('premium'), 'premium_end': series[i_exit].get('premium'),
                        'entry': h['entry'], 'exit': series[i_exit].get('close'), 'exit_t': series[i_exit]['t'],
                        'apr_after_24h': (after24['rate'] * HOURS_PER_YEAR) if (after24 and after24.get('rate') is not None) else None,
                        'apr_after_72h': (after72['rate'] * HOURS_PER_YEAR) if (after72 and after72.get('rate') is not None) else None,
                        'sign_flipped_within_72h': flip})
        i = j + 1
    return out


def premium_snaps(series, min_jump=0.004):
    """Hours where the premium moved by more than `min_jump` in one step, with what the mark did in the same hour."""
    out = []
    for a, b in zip(series, series[1:]):
        if a.get('premium') is None or b.get('premium') is None or b['t'] - a['t'] != HOUR_MS:
            continue
        d = b['premium'] - a['premium']
        if abs(d) < min_jump:
            continue
        mark_move = math.log(b['close'] / a['close']) if (a.get('close') and b.get('close')) else None
        oracle_move = None
        if mark_move is not None:
            oracle_move = math.log((b['close'] / (1 + b['premium'])) / (a['close'] / (1 + a['premium'])))
        out.append({'t': b['t'], 'premium_before': a['premium'], 'premium_after': b['premium'], 'jump': d,
                    'mark_move': mark_move, 'implied_oracle_move': oracle_move,
                    'rate_before': a.get('rate'), 'rate_after': b.get('rate')})
    return out


def longest_run(series, min_apr):
    best = cur = 0
    prev_side, prev_t = None, None
    for r in series:
        rate = r.get('rate')
        ok = rate is not None and abs(rate) * HOURS_PER_YEAR >= min_apr
        side = paid_side(rate) if ok else None
        if ok and side == prev_side and prev_t is not None and r['t'] - prev_t == HOUR_MS:
            cur += 1
        else:
            cur = 1 if ok else 0
        best = max(best, cur)
        prev_side, prev_t = side, r['t']
    return best


def market_stats(series):
    rates = [r['rate'] for r in series if r.get('rate') is not None]
    if not rates:
        return None
    aprs = sorted(abs(x) * HOURS_PER_YEAR for x in rates)
    prem = [r['premium'] for r in series if r.get('premium') is not None]
    flips = sum(1 for a, b in zip(rates, rates[1:]) if (a < 0) != (b < 0) and a != 0 and b != 0)
    ratio = [r['rate'] / (r['premium'] / 8) for r in series
             if r.get('rate') is not None and r.get('premium') is not None and abs(r['premium']) >= 2e-4]
    q = lambda p: aprs[min(len(aprs) - 1, int(p * len(aprs)))]
    return {'hours': len(rates), 'first_t': series[0]['t'], 'last_t': series[-1]['t'],
            'mean_apr': statistics.fmean(rates) * HOURS_PER_YEAR,
            'abs_apr_p50': q(0.5), 'abs_apr_p90': q(0.9), 'abs_apr_max': aprs[-1],
            'share_hours_over_50pct': sum(1 for x in aprs if x >= 0.5) / len(aprs),
            'share_hours_over_100pct': sum(1 for x in aprs if x >= 1.0) / len(aprs),
            'longest_run_over_50pct_h': longest_run(series, 0.5),
            'longest_run_over_100pct_h': longest_run(series, 1.0),
            'sign_flips': flips,
            'premium_mean': statistics.fmean(prem) if prem else None,
            'premium_min': min(prem) if prem else None, 'premium_max': max(prem) if prem else None,
            'transfer_ratio_median': statistics.median(ratio) if ratio else None,
            'funding_sum': sum(rates), 'volume_usd': sum(r.get('volume_usd') or 0.0 for r in series)}


# ---------------------------------------------------------------------------------------------- analyze

def pct(x, d=1):
    return '-' if x is None else ('%.*f%%' % (d, 100 * x))


def bps(x, d=1):
    return '-' if x is None else ('%.*fbp' % (d, x))


def load_history(out):
    out = Path(out)
    uni = json.loads((out / 'universe.json').read_text())['markets']
    H = {}
    for u in uni:
        fp = out / 'funding' / (safe(u['coin']) + '.json.gz')
        if not fp.exists():
            continue
        cp = out / 'candles_1h' / (safe(u['coin']) + '.json.gz')
        H[u['coin']] = {'meta': u, 'series': hourly_series(read_gz(fp), read_gz(cp) if cp.exists() else [])}
    return H


def oos_from_window(window, H):
    """What the earlier window's funding_carry hits earned from that window's close to the end of the history."""
    w = Path(window)
    dj = w / 'detectors.json'
    if not dj.exists():
        return None
    man = json.loads((w / 'manifest.json').read_text())
    t_close = hour_of(int(man['window']['end_ms'])) if 'window' in man else None
    rows = []
    for h in json.loads(dj.read_text()).get('hits', []):
        if h['detector'] not in ('funding_carry', 'premium_drift'):
            continue
        coin = h.get('key') or h['evidence'].get('coin')
        ec = h.get('economics') or {}
        side = ec.get('side_paid') or paid_side(h['evidence'].get('funding_apr') or -1)
        rt = ec.get('round_trip_bps_at_size')
        S = (H.get(coin) or {}).get('series')
        if not S or t_close is None:
            rows.append({'coin': coin, 'detector': h['detector'], 'note': 'no history for this market'})
            continue
        i0 = next((i for i, r in enumerate(S) if r['t'] >= t_close), None)
        if i0 is None or i0 >= len(S) - 1:
            rows.append({'coin': coin, 'detector': h['detector'], 'note': 'history ends before the window closed'})
            continue
        r = hold(S, i0, side)
        be_hour = None
        if rt is not None:
            be_hour = next((k + 1 for k, p in enumerate(r['path']) if p['funding'] * 1e4 >= rt), None)
        r24 = hold(S, i0, side, hours=24) if len(S) - 1 - i0 >= 24 else None
        rows.append({
            'coin': coin, 'detector': h['detector'], 'side': side, 'entered_utc': utc(S[i0]['t'] / 1000),
            'hours_held': r['hours'], 'predicted_apr': ec.get('funding_apr'),
            'predicted_net_apr_24h': ec.get('net_apr_over_24h'), 'round_trip_bps': rt,
            'funding_received_bps': 1e4 * r['funding'], 'mark_pnl_bps': (1e4 * r['mark']) if r['mark'] is not None else None,
            'unhedged_net_bps': (1e4 * r['total'] - (rt or 0)) if r['total'] is not None else None,
            'hedged_proxy_net_bps': (1e4 * r['hedged_proxy'] - (rt or 0)) if r['hedged_proxy'] is not None else None,
            'max_drawdown_bps': 1e4 * r['max_drawdown'],
            'realised_break_even_hour': be_hour,
            'realised_net_apr_24h': ((r24['total'] - (rt or 0) / 1e4) * HOURS_PER_YEAR / 24) if (r24 and r24['total'] is not None) else None,
            'realised_hedged_proxy_apr_24h': ((r24['hedged_proxy'] - (rt or 0) / 1e4) * HOURS_PER_YEAR / 24) if (r24 and r24['hedged_proxy'] is not None) else None,
            'funding_apr_realised_mean': (r['funding'] / r['hours'] * HOURS_PER_YEAR) if r['hours'] else None,
            'premium_entry': r['premium_entry'], 'premium_last': S[-1].get('premium'),
            'rate_last_apr': (S[-1]['rate'] * HOURS_PER_YEAR) if S[-1].get('rate') is not None else None,
            'path_daily': [p for k, p in enumerate(r['path']) if (k + 1) % 24 == 0 or k == len(r['path']) - 1],
        })
    return {'window': str(window), 'window_close_utc': utc(t_close / 1000) if t_close else None, 'rows': rows}


def cmd_analyze(args):
    out = Path(args.out)
    H = load_history(out)
    books = {}
    if args.window:
        aj = Path(args.window) / 'analysis.json'
        if aj.exists():
            for r in json.loads(aj.read_text())['assets']:
                if r.get('book'):
                    books[r['coin']] = r['book'].get('round_trip_bps_100k')
    markets, eps, snaps = [], [], []
    for coin, h in H.items():
        S = h['series']
        st = market_stats(S)
        if not st:
            continue
        st.update({'coin': coin, 'dex': h['meta']['dex'], 'oi_usd': (h['meta'].get('oi') or 0) * (h['meta'].get('mark') or 0),
                   'day_ntl_vlm': h['meta'].get('day_ntl_vlm'), 'funding_multiplier': h['meta'].get('funding_multiplier'),
                   'round_trip_bps_100k': books.get(coin)})
        markets.append(st)
        for e in episodes(S, min_apr=args.min_apr, min_hours=args.min_hours):
            e.update({'coin': coin, 'dex': h['meta']['dex'], 'round_trip_bps_100k': books.get(coin)})
            rt = books.get(coin)
            e['net_unhedged_bps'] = (1e4 * e['total_unhedged'] - rt) if (rt is not None and e['total_unhedged'] is not None) else None
            e['net_hedged_proxy_bps'] = (1e4 * e['hedged_proxy'] - rt) if (rt is not None and e['hedged_proxy'] is not None) else None
            eps.append(e)
        for s in premium_snaps(S, min_jump=args.min_jump):
            s.update({'coin': coin, 'dex': h['meta']['dex']})
            snaps.append(s)
    markets.sort(key=lambda m: -abs(m['mean_apr']))
    eps.sort(key=lambda e: -(e['funding_received'] or 0))
    snaps.sort(key=lambda s: -abs(s['jump']))
    if (out / 'manifest.json').exists():
        man = json.loads((out / 'manifest.json').read_text())
    else:
        # the manifest lands when the collection ends; a partial analysis is labelled from the universe file instead
        u = json.loads((out / 'universe.json').read_text())
        man = {'since_utc': u['since_utc'], 'until_utc': u['until_utc'], 'markets': len(H),
               'funding_rows': sum(len(h['series']) for h in H.values()),
               'candle_rows': sum(1 for h in H.values() for r in h['series'] if r.get('close') is not None),
               'partial': True}
    A = {'generated': utc(), 'history': {k: man.get(k) for k in ('since_utc', 'until_utc', 'markets', 'funding_rows', 'candle_rows', 'partial')},
         'params': {'min_apr': args.min_apr, 'min_hours': args.min_hours, 'min_jump': args.min_jump, 'window': args.window},
         'markets': markets, 'episodes': eps, 'premium_snaps': snaps,
         'oos': oos_from_window(args.window, H) if args.window else None}
    # summary numbers the note will cite
    ext = [m for m in markets if m['share_hours_over_100pct'] > 0]
    A['summary'] = {
        'markets_with_history': len(markets),
        'markets_ever_over_100pct_apr': len(ext),
        'markets_over_100pct_for_24h_plus': sum(1 for m in markets if m['longest_run_over_100pct_h'] >= 24),
        'episodes': len(eps),
        'episodes_24h_plus': sum(1 for e in eps if e['hours'] >= 24),
        'episodes_flipped_within_72h': sum(1 for e in eps if e['sign_flipped_within_72h']),
        'episodes_with_flip_data': sum(1 for e in eps if e['sign_flipped_within_72h'] is not None),
        'episode_hours_median': statistics.median([e['hours'] for e in eps]) if eps else None,
        'episode_unhedged_positive_share': (sum(1 for e in eps if (e['total_unhedged'] or 0) > 0)
                                            / max(1, sum(1 for e in eps if e['total_unhedged'] is not None))),
        'episode_hedged_proxy_positive_share': (sum(1 for e in eps if (e['hedged_proxy'] or 0) > 0)
                                                / max(1, sum(1 for e in eps if e['hedged_proxy'] is not None))),
        'premium_snaps': len(snaps),
    }
    # The same summary per DEX: the first-party book's alt-coins dominate the counts, and the HIP-3 markets, which
    # carry a 0.5 funding multiplier and deployer oracles, are the ones the question is about.
    by_dex = {}
    for d in sorted({m['dex'] for m in markets}):
        ms = [m for m in markets if m['dex'] == d]
        es = [e for e in eps if e['dex'] == d]
        hp = [e for e in es if e['hedged_proxy'] is not None]
        un = [e for e in es if e['total_unhedged'] is not None]
        hours = sum(m['hours'] for m in ms)
        by_dex[d] = {
            'markets': len(ms), 'hours': hours,
            'share_hours_over_100pct': (sum(m['share_hours_over_100pct'] * m['hours'] for m in ms) / hours) if hours else None,
            'markets_over_100pct_for_24h_plus': sum(1 for m in ms if m['longest_run_over_100pct_h'] >= 24),
            'episodes': len(es), 'episodes_24h_plus': sum(1 for e in es if e['hours'] >= 24),
            'episode_hours_median': statistics.median([e['hours'] for e in es]) if es else None,
            'episodes_flipped_within_72h_share': (sum(1 for e in es if e['sign_flipped_within_72h']) / len(es)) if es else None,
            'episode_unhedged_positive_share': (sum(1 for e in un if e['total_unhedged'] > 0) / len(un)) if un else None,
            'episode_hedged_proxy_positive_share': (sum(1 for e in hp if e['hedged_proxy'] > 0) / len(hp)) if hp else None,
            'episode_funding_received_bps_median': statistics.median([1e4 * e['funding_received'] for e in es]) if es else None,
            'episode_hedged_proxy_bps_median': statistics.median([1e4 * e['hedged_proxy'] for e in hp]) if hp else None,
            'transfer_ratio_median': statistics.median([m['transfer_ratio_median'] for m in ms if m['transfer_ratio_median'] is not None])
                                     if any(m['transfer_ratio_median'] is not None for m in ms) else None,
        }
    A['by_dex'] = by_dex
    write_json(out / 'history_analysis.json', A)
    print(json.dumps(A['summary'], indent=1))
    for d, v in by_dex.items():
        print('%-6s markets=%3d  hours>100%%=%s  eps=%4d  eps24h+=%3d  flipped<72h=%s  unhedged+=%s  hedged+=%s  median funding %s / hedged %s' % (
            d, v['markets'], pct(v['share_hours_over_100pct']), v['episodes'], v['episodes_24h_plus'],
            pct(v['episodes_flipped_within_72h_share']), pct(v['episode_unhedged_positive_share']),
            pct(v['episode_hedged_proxy_positive_share']), bps(v['episode_funding_received_bps_median']),
            bps(v['episode_hedged_proxy_bps_median'])))
    return 0


# ---------------------------------------------------------------------------------------------- render

def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'history_analysis.json').read_text())
    L = ['# Funding history, %s to %s UTC' % (A['history']['since_utc'][:16], A['history']['until_utc'][:16]), '',
         '%d markets, %s funding hours, %s hourly candles. Episode threshold |APR| >= %s for at least %d hour(s).' % (
             A['history']['markets'], format(A['history']['funding_rows'], ','), format(A['history']['candle_rows'], ','),
             pct(A['params']['min_apr'], 0), A['params']['min_hours']), '']
    S = A['summary']
    L += ['| | |', '|---|---:|']
    for k, v in S.items():
        L.append('| %s | %s |' % (k.replace('_', ' '), (pct(v) if 'share' in k else v)))
    if A.get('by_dex'):
        L += ['', '## The same, per DEX', '',
              '| dex | markets | hours >100% APR | markets >100% for 24h+ | episodes | 24h+ | median hours | flipped <72h | unhedged positive | hedged proxy positive | median funding / episode | median hedged proxy | transfer ratio |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for d, v in A['by_dex'].items():
            L.append('| `%s` | %d | %s | %d | %d | %d | %s | %s | %s | %s | %s | %s | %s |' % (
                d, v['markets'], pct(v['share_hours_over_100pct']), v['markets_over_100pct_for_24h_plus'], v['episodes'],
                v['episodes_24h_plus'], v['episode_hours_median'], pct(v['episodes_flipped_within_72h_share']),
                pct(v['episode_unhedged_positive_share']), pct(v['episode_hedged_proxy_positive_share']),
                bps(v['episode_funding_received_bps_median']), bps(v['episode_hedged_proxy_bps_median']),
                '-' if v['transfer_ratio_median'] is None else '%.2f' % v['transfer_ratio_median']))
    L += ['', '## Markets by mean funding, most one-sided first', '',
          '| market | hours | mean APR | p90 abs APR | max abs APR | hours >100% | longest run >100% | flips | premium mean | transfer ratio | OI |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for m in A['markets'][:40]:
        L.append('| `%s` | %d | %s | %s | %s | %s | %dh | %d | %s | %s | $%s |' % (
            m['coin'], m['hours'], pct(m['mean_apr'], 0), pct(m['abs_apr_p90'], 0), pct(m['abs_apr_max'], 0),
            pct(m['share_hours_over_100pct']), m['longest_run_over_100pct_h'], m['sign_flips'],
            pct(m['premium_mean'], 3), '-' if m['transfer_ratio_median'] is None else '%.3f' % m['transfer_ratio_median'],
            format(round(m['oi_usd'] or 0), ',')))
    L += ['', '## Episodes: the paid side collected the most', '',
          '| market | side paid | start (UTC) | hours | mean APR | funding collected | mark PnL | total unhedged | hedged proxy | max DD | APR +24h | APR +72h | flipped <72h |',
          '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for e in A['episodes'][:60]:
        L.append('| `%s` | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            e['coin'], e['side'], utc(e['start_t'] / 1000)[:16], e['hours'], pct(e['mean_apr'], 0),
            bps(1e4 * e['funding_received']), bps(1e4 * e['mark_pnl']) if e['mark_pnl'] is not None else '-',
            bps(1e4 * e['total_unhedged']) if e['total_unhedged'] is not None else '-',
            bps(1e4 * e['hedged_proxy']) if e['hedged_proxy'] is not None else '-',
            bps(1e4 * e['max_drawdown']), pct(e['apr_after_24h'], 0), pct(e['apr_after_72h'], 0),
            '-' if e['sign_flipped_within_72h'] is None else ('yes' if e['sign_flipped_within_72h'] else 'no')))
    L += ['', '## Premium snaps: the premium jumped by more than %s in one hour' % pct(A['params']['min_jump'], 1), '',
          '| market | hour (UTC) | premium before | after | mark move | implied oracle move | rate before | rate after |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    for s in A['premium_snaps'][:60]:
        L.append('| `%s` | %s | %s | %s | %s | %s | %s | %s |' % (
            s['coin'], utc(s['t'] / 1000)[:16], pct(s['premium_before'], 3), pct(s['premium_after'], 3),
            pct(s['mark_move'], 2) if s['mark_move'] is not None else '-',
            pct(s['implied_oracle_move'], 2) if s['implied_oracle_move'] is not None else '-',
            pct((s['rate_before'] or 0) * HOURS_PER_YEAR, 0), pct((s['rate_after'] or 0) * HOURS_PER_YEAR, 0)))
    if A.get('oos'):
        O = A['oos']
        L += ['', '## Out of sample: the %s hits, held from %s' % (O['window'], O['window_close_utc']), '',
              '| market | side | hours held | predicted APR | round trip | funding collected | mark PnL | unhedged net | hedged proxy net | max DD | realised break-even hour | realised 24h net APR | last rate APR |',
              '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in O['rows']:
            if r.get('note'):
                L.append('| `%s` | %s | | | | | | | | | | | |' % (r['coin'], r['note']))
                continue
            L.append('| `%s` | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                r['coin'], r['side'], r['hours_held'], pct(r['predicted_apr'], 0), bps(r['round_trip_bps']),
                bps(r['funding_received_bps']), bps(r['mark_pnl_bps']), bps(r['unhedged_net_bps']),
                bps(r['hedged_proxy_net_bps']), bps(r['max_drawdown_bps']),
                '-' if r['realised_break_even_hour'] is None else r['realised_break_even_hour'],
                pct(r['realised_net_apr_24h'], 0), pct(r['rate_last_apr'], 0)))
    (out / 'history.md').write_text('\n'.join(L) + '\n')
    # The full analysis carries every episode and snap for 300+ markets and runs to tens of megabytes; the summary
    # keeps what a reader or a later window needs and is the file that is committed.
    compact = {k: A[k] for k in ('generated', 'history', 'params', 'summary') if k in A}
    compact['by_dex'] = A.get('by_dex')
    compact['markets'] = A['markets']
    compact['episodes_top'] = A['episodes'][:200]
    compact['episodes_24h_plus'] = [e for e in A['episodes'] if e['hours'] >= 24]
    compact['premium_snaps_top'] = A['premium_snaps'][:200]
    compact['oos'] = A.get('oos')
    write_json(out / 'history_summary.json', compact)
    print('wrote %s and %s' % (out / 'history.md', out / 'history_summary.json'))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--since', default='2026-07-01')
    c.add_argument('--dexes', default=None, help='comma list, e.g. core,xyz,para,mkts,io; default all')
    c.add_argument('--coins', nargs='*')
    c.add_argument('--workers', type=int, default=2)
    c.add_argument('--interval', type=float, default=0.15)
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--window', default=None, help='an earlier perps window whose funding_carry hits are tested out of sample')
    a.add_argument('--min-apr', type=float, default=1.0)
    a.add_argument('--min-hours', type=int, default=1)
    a.add_argument('--min-jump', type=float, default=0.004)
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
