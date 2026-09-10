#!/usr/bin/env python3
"""External references for the HIP-3 perp surface: is the deployer's oracle where the outside world is?

Why. A HIP-3 deployer sets the oracle for its own markets, and the 2026-09-08 study found the XYZ oil markets sitting
half a percent below their own oracle with longs paid 285% a year to hold that gap. Whether that is an oracle that is
high or a book that is low is only checkable against a price neither side controls. This module snapshots public
delayed quotes for the futures, equities, indices and FX behind the builder markets, records Hyperliquid's oracle and
mark at the same moments, and compares them with the reference's own delay taken into account.

The reference is TradingView's public scanner (`scanner.tradingview.com/global/scan`). It serves futures by contract
month (`ICEEUR:BRNX2026`), which is what makes the oil question answerable: a perp oracle that tracks the front
month, the second month, or a rolling blend of the two behaves differently at the roll, and the roll is the risk a
funding carry on these markets actually carries. Quotes are delayed 10 minutes for futures and indices and 15 for US
equities; `compare` aligns each reference quote with the Hyperliquid snapshot taken that long before it.

    uv run python scripts/perp_refs.py snap    --out research/2026-09-10/perps_2 --minutes 15 --every 60
    uv run python scripts/perp_refs.py compare --out research/2026-09-10/perps_2
    uv run python scripts/perp_refs.py curve   --out research/2026-09-10/perps_2
"""
import argparse
import datetime as dt
import json
import re
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from perp_rpc import Info, APIError, perp_dexes, meta_and_ctxs  # noqa: E402
from perp_collect import read_gz, write_gz, write_json, dex_key, utc  # noqa: E402
from perp_scan import us_equity_session  # noqa: E402

SCAN_URL = 'https://scanner.tradingview.com/global/scan'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/128.0 Safari/537.36')
COLS = ['close', 'update_mode', 'description', 'type', 'currency', 'exchange']

# Reference candidates per builder symbol, first hit wins. A missing entry falls through to the US equity exchanges.
# Currency-quoted references (KRW, JPY) are converted with the FX rows in the same scan.
REFS = {
    'BRENTOIL': ['ICEEUR:BRN1!'], 'CL': ['NYMEX:CL1!'], 'NATGAS': ['NYMEX:NG1!'],
    'GOLD': ['TVC:GOLD', 'COMEX:GC1!'], 'SILVER': ['TVC:SILVER', 'COMEX:SI1!'],
    'COPPER': ['COMEX:HG1!'], 'PLATINUM': ['NYMEX:PL1!'], 'PALLADIUM': ['NYMEX:PA1!'],
    'SP500': ['SP:SPX'], 'XYZ100': ['NASDAQ:NDX'], 'JP225': ['TVC:NI225'], 'KR200': ['KRX:KOSPI200'],
    # Markets by Kinetiq quotes ETF prices, not index points: 758 is SPY, 708 is QQQ, 289 is IWM, 81 is TLT
    'US500': ['AMEX:SPY'], 'USTECH': ['NASDAQ:QQQ'], 'SMALL2000': ['AMEX:IWM'], 'USBOND': ['NASDAQ:TLT'],
    '10Y': ['TVC:US10Y'],
    'TOTAL2': ['CRYPTOCAP:TOTAL2'], 'OTHERS': ['CRYPTOCAP:OTHERS'], 'BTCD': ['CRYPTOCAP:BTC.D'],
    'EUR': ['FX_IDC:EURUSD'], 'GBP': ['FX_IDC:GBPUSD'], 'JPY': ['FX_IDC:USDJPY'],
    'SMSN': ['LSE:SMSN', 'KRX:005930'], 'HYUNDAI': ['KRX:005380'], 'SKHX': ['KRX:000660'],
    'SOFTBANK': ['TSE:9984'], 'KIOXIA': ['TSE:285A'],
    'TSM': ['NYSE:TSM'], 'BABA': ['NYSE:BABA'], 'ASML': ['NASDAQ:ASML'], 'NOK': ['NYSE:NOK'],
}
FX_ROWS = {'KRW': 'FX_IDC:USDKRW', 'JPY': 'FX_IDC:USDJPY', 'GBP': 'FX_IDC:GBPUSD', 'EUR': 'FX_IDC:EURUSD',
           'GBX': 'FX_IDC:GBPUSD'}
US_EXCHANGES = ['NASDAQ', 'NYSE', 'AMEX', 'BATS']
# Private companies and venue-specific indices: a ticker search would return an unrelated listing (io:ANTH resolved
# to a delisted pharmaceutical), so these are declared unreferenced rather than guessed.
NO_REF = {'ANTH', 'OAI', 'UNITREE', 'ZHIPU', 'MINIMAX', 'GIGADEV', 'SHEIN', 'CXMT', 'DRAM', 'LYTE', 'PURRDAT',
          'ANSEM', 'GPRO'}
# Exchanges whose cash session is not the US one; a quote outside it is a stale close, not a live reference.
LOCAL_SESSIONS_UTC = {'KRX': (0, 6.5), 'TSE': (0, 6), 'LSE': (8, 16.5)}
US_CASH_TYPES = {'stock', 'dr', 'fund'}
# Named contract months, front first. The scanner does not serve the 2!/3! continuous symbols, and a named month is
# unambiguous about what rolls when.
CURVES = {
    'BRENTOIL': ['ICEEUR:BRNX2026', 'ICEEUR:BRNZ2026', 'ICEEUR:BRNF2027'],
    'CL': ['NYMEX:CLV2026', 'NYMEX:CLX2026', 'NYMEX:CLZ2026'],
    'NATGAS': ['NYMEX:NGV2026', 'NYMEX:NGX2026', 'NYMEX:NGZ2026'],
    'GOLD': ['TVC:GOLD', 'COMEX:GC1!'],      # spot against the front future: the oracle follows spot
}
# Exchange expiry rules, stated for the roll test; these are the rules as published, not verified against a calendar.
FRONT_EXPIRY = {'BRENTOIL': ('ICEEUR:BRNX2026', '2026-09-30', 'ICE Brent: last business day of the second month before delivery'),
                'CL': ('NYMEX:CLV2026', '2026-09-22', 'NYMEX WTI: three business days before the 25th of the month before delivery'),
                'NATGAS': ('NYMEX:NGV2026', '2026-09-28', 'NYMEX Henry Hub: three business days before the first day of the delivery month')}
DELAY_S = {'streaming': 0, 'delayed_streaming_600': 600, 'delayed_streaming_900': 900, 'delayed_streaming_1200': 1200}


def scan(tickers, retries=3):
    body = {'symbols': {'tickers': tickers, 'query': {'types': []}}, 'columns': COLS}
    req = urllib.request.Request(SCAN_URL, data=json.dumps(body).encode(), headers={
        'User-Agent': UA, 'Accept': 'application/json', 'Content-Type': 'application/json',
        'Origin': 'https://www.tradingview.com', 'Referer': 'https://www.tradingview.com/'})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read())
            out = {}
            for row in d.get('data', []):
                out[row['s']] = dict(zip(COLS, row['d']))
            return out
        except Exception as e:
            last = e
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError('tradingview scan failed: %s' % last)


def universe(api):
    rows = []
    for d in perp_dexes(api):
        dk = dex_key(d)
        if not dk:
            continue   # the first-party dex is covered by cross_venue_funding against Binance and Bybit
        meta = meta_and_ctxs(api, dk)
        for m in meta[0]['universe']:
            if not m.get('isDelisted'):
                rows.append((dk, m['name']))
    return rows


def candidates(sym):
    if sym in NO_REF:
        return []
    c = list(REFS.get(sym, []))
    if not c:
        c = ['%s:%s' % (x, sym) for x in US_EXCHANGES]
    return c


def resolve_map(uni):
    """One scan over every candidate; the first candidate that answers becomes the market's reference."""
    want = set()
    for _, coin in uni:
        sym = coin.split(':', 1)[1]
        want.update(candidates(sym))
    want.update(FX_ROWS.values())
    for lst in CURVES.values():
        want.update(lst)
    want = sorted(want)
    found = {}
    for i in range(0, len(want), 60):
        found.update(scan(want[i:i + 60]))
        time.sleep(1.0)
    mp = {}
    for dk, coin in uni:
        sym = coin.split(':', 1)[1]
        pick = next((c for c in candidates(sym) if c in found and found[c].get('close') is not None), None)
        mp[coin] = {'ticker': pick, 'currency': (found[pick].get('currency') if pick else None),
                    'type': (found[pick].get('type') if pick else None),
                    'update_mode': (found[pick].get('update_mode') if pick else None),
                    'description': (found[pick].get('description') if pick else None)}
    return mp, found


def cmd_snap(args):
    out = Path(args.out)
    api = Info(interval=0.12)
    uni = universe(api)
    mp_path = out / 'refs' / 'map.json'
    if mp_path.exists() and not args.remap:
        mp = json.loads(mp_path.read_text())
    else:
        mp, _ = resolve_map(uni)
        write_json(mp_path, mp)
    tickers = sorted({v['ticker'] for v in mp.values() if v['ticker']} | set(FX_ROWS.values())
                     | {t for lst in CURVES.values() for t in lst})
    print(json.dumps({'markets': len(uni), 'referenced': sum(1 for v in mp.values() if v['ticker']),
                      'tickers': len(tickers)}), flush=True)
    dexes = sorted({dk for dk, _ in uni})
    t_end = time.time() + args.minutes * 60
    n = 0
    while True:
        t0 = time.time()
        tv = {}
        for i in range(0, len(tickers), 60):
            tv.update(scan(tickers[i:i + 60]))
            time.sleep(0.8)
        hl = {}
        for dk in dexes:
            try:
                hl[dk] = meta_and_ctxs(api, dk)
            except APIError as e:
                hl[dk] = {'error': str(e)[:120]}
        ts = time.time()
        write_gz(out / 'refs' / ('tv_%d.json.gz' % int(t0)), {'ts': t0, 'utc': utc(t0), 'rows': tv})
        write_gz(out / 'refs' / ('hl_%d.json.gz' % int(ts)), {'ts': ts, 'utc': utc(ts), 'dexes': hl})
        n += 1
        print(json.dumps({'snapshot': n, 'utc': utc(t0), 'tv_rows': len(tv)}), flush=True)
        if time.time() >= t_end:
            break
        time.sleep(max(0.0, args.every - (time.time() - t0)))
    print(json.dumps({'snap_complete': True, 'snapshots': n, **api.stats()}))
    return 0


def load_hl_series(out):
    """Every Hyperliquid snapshot available: the tape's `snap/` files and this module's `refs/hl_*`."""
    rows = []
    for p in sorted((out / 'snap').glob('*.json.gz')) if (out / 'snap').exists() else []:
        s = read_gz(p)
        rows.append((s['ts'], s['dexes']))
    for p in sorted((out / 'refs').glob('hl_*.json.gz')):
        s = read_gz(p)
        rows.append((s['ts'], s['dexes']))
    rows.sort(key=lambda x: x[0])
    return rows


def hl_prices(payload_by_dex):
    px = {}
    for dk, payload in payload_by_dex.items():
        if not payload or isinstance(payload, dict):
            continue
        for m, c in zip(payload[0]['universe'], payload[1]):
            try:
                px[m['name']] = {'oracle': float(c['oraclePx']), 'mark': float(c['markPx']),
                                 'mid': float(c['midPx']) if c.get('midPx') else None,
                                 'funding': float(c.get('funding') or 0), 'premium': float(c.get('premium') or 0)}
            except (TypeError, ValueError, KeyError):
                continue
    return px


def nearest(series, t, tol_s=90):
    best = min(series, key=lambda x: abs(x[0] - t), default=None)
    if best is None or abs(best[0] - t) > tol_s:
        return None
    return best


def scaled(oracle, ref):
    """The power of ten that puts a reference in the perp's units (crypto market caps quote in billions)."""
    if not oracle or not ref or oracle <= 0 or ref <= 0:
        return ref, 0
    import math
    k = round(math.log10(oracle / ref))
    return ref * 10 ** k, k


def session_state(ticker, rtype, ts):
    """Whether the reference quote can be live at `ts`: futures, FX, spot metals and crypto indices always; a cash
    equity or cash index only inside its exchange's session."""
    ex = ticker.split(':')[0]
    hour = (ts % 86400) / 3600.0
    if ex in LOCAL_SESSIONS_UTC:
        lo, hi = LOCAL_SESSIONS_UTC[ex]
        return 'live' if lo <= hour <= hi else 'closed:' + ex
    if rtype in US_CASH_TYPES or ex in ('SP', 'NASDAQ', 'AMEX', 'NYSE', 'BATS') or ticker in ('TVC:RUT',):
        return 'live' if us_equity_session(int(ts * 1000))['session'] == 'regular' else 'closed:US'
    if ticker in ('TVC:NI225',):
        return 'live' if 0 <= hour <= 6 else 'closed:TSE'
    return 'live'


def to_usd(price, currency, fx, rtype=None):
    # a pair, an index level or a yield is compared in its own units; only a share price is converted
    if rtype in ('forex', 'index', 'bond', 'commodity', 'futures'):
        return price
    if currency in (None, 'USD', ''):
        return price
    if currency == 'GBX':
        r = fx.get('FX_IDC:GBPUSD')
        return price / 100.0 * r if r else None
    if currency == 'KRW':
        r = fx.get('FX_IDC:USDKRW')
        return price / r if r else None
    if currency == 'JPY':
        r = fx.get('FX_IDC:USDJPY')
        return price / r if r else None
    if currency == 'EUR':
        r = fx.get('FX_IDC:EURUSD')
        return price * r if r else None
    if currency == 'GBP':
        r = fx.get('FX_IDC:GBPUSD')
        return price * r if r else None
    return None


def cmd_compare(args):
    out = Path(args.out)
    mp = json.loads((out / 'refs' / 'map.json').read_text())
    hl = load_hl_series(out)
    tvs = [read_gz(p) for p in sorted((out / 'refs').glob('tv_*.json.gz'))]
    if not tvs or not hl:
        raise SystemExit('need refs/tv_* and Hyperliquid snapshots; run `snap` (and the tape) first')
    per = {coin: [] for coin in mp}
    for tv in tvs:
        rows = tv['rows']
        fx = {k: (rows.get(k) or {}).get('close') for k in FX_ROWS.values()}
        for coin, m in mp.items():
            tk = m['ticker']
            if not tk or tk not in rows or rows[tk].get('close') is None:
                continue
            mode = rows[tk].get('update_mode') or ''
            lag = DELAY_S.get(mode, 600)
            h = nearest(hl, tv['ts'] - lag, tol_s=args.tol)
            if not h:
                continue
            px = hl_prices(h[1]).get(coin)
            if not px:
                continue
            ref = to_usd(rows[tk]['close'], rows[tk].get('currency'), fx, rows[tk].get('type'))
            if not ref:
                continue
            ref, k = scaled(px['oracle'], ref)
            state = session_state(tk, rows[tk].get('type'), tv['ts'])
            per[coin].append({'tv_utc': tv['utc'], 'hl_utc': utc(h[0]), 'lag_s': lag, 'ref': ref, 'scale_pow10': k,
                              'session': state,
                              'oracle': px['oracle'], 'mark': px['mark'],
                              'oracle_vs_ref_bps': 1e4 * (px['oracle'] / ref - 1),
                              'mark_vs_ref_bps': 1e4 * (px['mark'] / ref - 1),
                              'mark_vs_oracle_bps': 1e4 * (px['mark'] / px['oracle'] - 1),
                              'funding_apr': px['funding'] * 8760})
    table = []
    sess = us_equity_session(int(tvs[-1]['ts'] * 1000))
    for coin, obs in per.items():
        m = mp[coin]
        if not obs:
            table.append({'coin': coin, 'ticker': m['ticker'], 'n': 0, 'note': 'no reference' if not m['ticker'] else 'no aligned snapshot'})
            continue
        o = [x['oracle_vs_ref_bps'] for x in obs]
        k = [x['mark_vs_ref_bps'] for x in obs]
        med_o = statistics.median(o)
        state = obs[-1]['session']
        verdict = ('rejected: more than 25% apart after scaling' if abs(med_o) > 2500 else
                   'stale reference: exchange closed' if state != 'live' else 'live')
        table.append({'coin': coin, 'ticker': m['ticker'], 'type': m['type'], 'currency': m['currency'],
                      'update_mode': m['update_mode'], 'n': len(obs), 'scale_pow10': obs[-1]['scale_pow10'],
                      'session': state, 'verdict': verdict,
                      'oracle_vs_ref_bps_median': statistics.median(o), 'oracle_vs_ref_bps_sd': statistics.pstdev(o) if len(o) > 1 else 0.0,
                      'mark_vs_ref_bps_median': statistics.median(k),
                      'mark_vs_oracle_bps_median': statistics.median(x['mark_vs_oracle_bps'] for x in obs),
                      'funding_apr_last': obs[-1]['funding_apr'], 'ref_last': obs[-1]['ref'],
                      'oracle_last': obs[-1]['oracle'], 'mark_last': obs[-1]['mark'],
                      # which side of the oracle the outside world is on, and whether the book is between them
                      'book_between': (min(obs[-1]['oracle'], obs[-1]['ref']) <= obs[-1]['mark'] <= max(obs[-1]['oracle'], obs[-1]['ref']))})
    order = {'live': 0}
    table.sort(key=lambda r: (order.get(r.get('verdict'), 1), -abs(r.get('oracle_vs_ref_bps_median') or 0)))
    R = {'generated': utc(), 'window': str(out), 'tv_snapshots': len(tvs), 'hl_snapshots': len(hl),
         'us_equity_session_at_last_snapshot': sess, 'tolerance_s': args.tol, 'rows': table,
         'summary': {'referenced': sum(1 for r in table if r.get('n')),
                     'unreferenced': sum(1 for r in table if not r.get('n')),
                     'live_comparisons': sum(1 for r in table if r.get('verdict') == 'live'),
                     'stale_reference': sum(1 for r in table if r.get('verdict', '').startswith('stale')),
                     'rejected': sum(1 for r in table if r.get('verdict', '').startswith('rejected')),
                     'live_oracle_within_25bp': sum(1 for r in table if r.get('verdict') == 'live' and abs(r['oracle_vs_ref_bps_median']) <= 25),
                     'live_oracle_over_100bp': sum(1 for r in table if r.get('verdict') == 'live' and abs(r['oracle_vs_ref_bps_median']) > 100)}}
    write_json(out / 'refs_compare.json', R)
    L = ['# HIP-3 oracles against outside references', '',
         '%d TradingView snapshots, %d Hyperliquid snapshots, reference delay removed per quote (futures and indices '
         '10 min, US equities 15 min, FX and spot metals live). US equities were **%s** at the last snapshot.' % (
             len(tvs), len(hl), sess['session']), '',
         '| market | reference | verdict | n | oracle vs ref (median bp) | sd | mark vs ref | mark vs oracle | funding APR | book between |',
         '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
    for r in table:
        if not r.get('n'):
            L.append('| `%s` | %s | %s | 0 | | | | | | |' % (r['coin'], r.get('ticker') or '-', r['note']))
            continue
        L.append('| `%s` | %s%s | %s | %d | %.1f | %.1f | %.1f | %.1f | %.0f%% | %s |' % (
            r['coin'], r['ticker'], (' x1e%d' % r['scale_pow10']) if r['scale_pow10'] else '', r['verdict'], r['n'],
            r['oracle_vs_ref_bps_median'], r['oracle_vs_ref_bps_sd'],
            r['mark_vs_ref_bps_median'], r['mark_vs_oracle_bps_median'], 100 * r['funding_apr_last'],
            'yes' if r['book_between'] else 'no'))
    (out / 'refs.md').write_text('\n'.join(L) + '\n')
    print(json.dumps(R['summary'], indent=1))
    for r in [x for x in table if x.get('verdict') == 'live'][:20]:
        print('%-16s %-18s oracle %+7.1fbp  mark %+7.1fbp  funding %+6.0f%%' % (
            r['coin'], r['ticker'], r['oracle_vs_ref_bps_median'], r['mark_vs_ref_bps_median'], 100 * r['funding_apr_last']))
    return 0


def cmd_curve(args):
    """Where the oil and gas oracles sit on the futures curve, from the latest aligned snapshots."""
    out = Path(args.out)
    hl = load_hl_series(out)
    tvs = [read_gz(p) for p in sorted((out / 'refs').glob('tv_*.json.gz'))]
    if not tvs or not hl:
        raise SystemExit('run `snap` first')
    res = {}
    for sym, tickers in CURVES.items():
        coin = 'xyz:' + sym
        obs = []
        for tv in tvs:
            rows = tv['rows']
            got = {t: (rows.get(t) or {}).get('close') for t in tickers}
            mode = (rows.get(tickers[0]) or {}).get('update_mode') or 'delayed_streaming_600'
            h = nearest(hl, tv['ts'] - DELAY_S.get(mode, 600), tol_s=args.tol)
            if not h:
                continue
            px = hl_prices(h[1]).get(coin)
            if not px:
                continue
            m1, m2 = got.get(tickers[0]), got.get(tickers[1])
            w_or = w_mk = None
            if m1 and m2 and abs(m1 - m2) > 1e-9:
                w_or = (px['oracle'] - m2) / (m1 - m2)
                w_mk = (px['mark'] - m2) / (m1 - m2)
            obs.append({'tv_utc': tv['utc'], 'hl_utc': utc(h[0]), 'contracts': got, 'oracle': px['oracle'],
                        'mark': px['mark'], 'premium': px['premium'], 'funding_apr': px['funding'] * 8760,
                        'oracle_vs_front_bps': 1e4 * (px['oracle'] / m1 - 1) if m1 else None,
                        'oracle_vs_second_bps': 1e4 * (px['oracle'] / m2 - 1) if m2 else None,
                        'mark_vs_front_bps': 1e4 * (px['mark'] / m1 - 1) if m1 else None,
                        'front_over_second_pct': 100 * (m1 / m2 - 1) if (m1 and m2) else None,
                        'implied_front_weight_oracle': w_or, 'implied_front_weight_mark': w_mk})
        if obs:
            last = obs[-1]
            med = lambda k: statistics.median(x[k] for x in obs if x.get(k) is not None) if any(x.get(k) is not None for x in obs) else None
            res[coin] = {'n': len(obs), 'last': last,
                         'oracle_vs_front_bps_median': med('oracle_vs_front_bps'),
                         'oracle_vs_second_bps_median': med('oracle_vs_second_bps'),
                         'mark_vs_front_bps_median': med('mark_vs_front_bps'),
                         'implied_front_weight_oracle_median': med('implied_front_weight_oracle'),
                         'implied_front_weight_mark_median': med('implied_front_weight_mark'),
                         'front_over_second_pct_median': med('front_over_second_pct'),
                         'front_expiry': FRONT_EXPIRY.get(sym)}
    write_json(out / 'refs_curve.json', {'generated': utc(), 'rows': res})
    for coin, r in res.items():
        l = r['last']
        print('%-14s n=%d  oracle %s  mark %s  | %s | oracle vs front %+.0fbp, vs second %+.0fbp | front weight: oracle %.2f mark %.2f | front/second %+.2f%%' % (
            coin, r['n'], l['oracle'], l['mark'],
            ', '.join('%s=%s' % (k.split(':')[1], v) for k, v in l['contracts'].items() if v is not None),
            r['oracle_vs_front_bps_median'] or 0, r['oracle_vs_second_bps_median'] or 0,
            r['implied_front_weight_oracle_median'] if r['implied_front_weight_oracle_median'] is not None else float('nan'),
            r['implied_front_weight_mark_median'] if r['implied_front_weight_mark_median'] is not None else float('nan'),
            r['front_over_second_pct_median'] or 0))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('snap'); s.set_defaults(fn=cmd_snap)
    s.add_argument('--out', required=True); s.add_argument('--minutes', type=float, default=15)
    s.add_argument('--every', type=float, default=60); s.add_argument('--remap', action='store_true')
    c = sub.add_parser('compare'); c.set_defaults(fn=cmd_compare)
    c.add_argument('--out', required=True); c.add_argument('--tol', type=float, default=90)
    k = sub.add_parser('curve'); k.set_defaults(fn=cmd_curve)
    k.add_argument('--out', required=True); k.add_argument('--tol', type=float, default=90)
    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == '__main__':
    main()
