#!/usr/bin/env python3
"""The HIP-3 energy roll carry over every roll the data can see, hedged with the futures the oracle tracks.

Why. The book's largest line (`hip3-oil-funding-carry`, $2.84M a year at capacity) was priced from one window on
2026-09-10, when the regime was eleven days old and the out-of-sample test was 47 hours long. The mechanism found then
(`research/2026-09-10/perps_2/insights.md`): XYZ's energy oracles are a constant-maturity blend of the front and second
futures that steps a tenth of the calendar spread at 22:00 UTC each trading day; the book prices the blend a step or
two ahead, the premium is charged as funding, and the side behind the roll is paid. A month later, two questions
decide whether that line is real: did it keep paying, and what does it pay over a whole cycle — including the days
when no roll is on — once the hedge is priced from the actual futures rather than assumed to track the oracle?

Data.
  * Hyperliquid hourly funding (with the premium) and 1h candles for the xyz commodity perps, from perp_history's
    store (`perp_history.py collect`).
  * Futures hourly and daily bars from Yahoo's chart API: the continuous front (BZ=F, CL=F, NG=F; metals as controls)
    and every listed contract month still trading. Yahoo removes a contract when it expires, so the second month
    before the most recent expiry cannot be recovered from it; hours without both legs are reported, not filled.

Per market and hour this computes:
  * F1, F2 — front and second contract by the exchange's expiry rule (below);
  * the oracle implied from the venue, close / (1 + premium) — approximate: the premium is an hourly mean of
    impact-price samples and the close is a trade;
  * the oracle's front weight w = (oracle - F2) / (F1 - F2), only where the spread can resolve it;
  * hedged P&L for side s: s (r_perp - r_hedge) - s * funding, the hedge being the F1/F2 blend at the weight the oracle
    showed at the start of the UTC day (and, for comparison, the front contract alone);
  * the roll calendar: days on which the weight stepped.

Strategy and protocol. Hold the side the funding pays when the trailing-k-hour funding APR exceeds X; costs are the
perp round trip (taker fee x deployer fee scale + half-spread, each way) and 1bp each way on the future. (k, X) are
chosen on hours before 2026-09-10 13:00 UTC — the book's quote — with the front-only hedge (the only one the data
supports that early) and tested after it with both hedges. Sign conventions follow perp_history: Hyperliquid funding is
positive when longs pay; side +1 is long.

    uv run python scripts/roll_carry.py collect --out research/2026-10-09/roll_carry
    uv run python scripts/roll_carry.py analyze --out research/2026-10-09/roll_carry --hl research/2026-10-09/perps_hip3
    uv run python scripts/roll_carry.py render  --out research/2026-10-09/roll_carry
"""
import argparse
import datetime as dt
import gzip
import json
import math
import statistics
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

HOUR_MS = 3_600_000
HOURS_PER_YEAR = 8760.0
UTC = dt.timezone.utc
MONTH_CODES = 'FGHJKMNQUVXZ'
YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart/'
# A bare 'Mozilla/5.0' is served; a full desktop-Chrome string is answered 429 from this machine (2026-10-09).
UA = 'Mozilla/5.0'
BOOK_QUOTE_UTC = '2026-09-10T13:00:00+00:00'

# Venue market -> futures root, expiry rule, and whether the oracle is expected to roll. Metals are controls: the
# 2026-09-10 comparison found gold's oracle on spot, so a roll premium there would be a finding in itself.
MARKETS = {
    'xyz:BRENTOIL': {'root': 'BZ', 'rule': 'brent', 'rolls': True},
    'xyz:CL': {'root': 'CL', 'rule': 'wti', 'rolls': True},
    'xyz:NATGAS': {'root': 'NG', 'rule': 'ng', 'rolls': True},
    'xyz:GOLD': {'root': 'GC', 'rule': None, 'rolls': False},
    'xyz:SILVER': {'root': 'SI', 'rule': None, 'rolls': False},
    'xyz:COPPER': {'root': 'HG', 'rule': None, 'rolls': False},
    'xyz:PLATINUM': {'root': 'PL', 'rule': None, 'rolls': False},
    'xyz:PALLADIUM': {'root': 'PA', 'rule': None, 'rolls': False},
}

# Exchange holidays that can move an expiry by a day, 2025-2027. NYMEX follows US holidays; ICE Brent (and NYMEX's BZ
# look-alike, which settles on it) follows UK business days for its last trading day.
US_HOLIDAYS = {
    '2025-01-01', '2025-01-20', '2025-02-17', '2025-04-18', '2025-05-26', '2025-06-19', '2025-07-04', '2025-09-01',
    '2025-11-27', '2025-12-25', '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19',
    '2026-07-03', '2026-09-07', '2026-11-26', '2026-12-25', '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26',
    '2027-05-31', '2027-06-18', '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24'}
UK_HOLIDAYS = {
    '2025-01-01', '2025-04-18', '2025-04-21', '2025-05-05', '2025-05-26', '2025-08-25', '2025-12-25', '2025-12-26',
    '2026-01-01', '2026-04-03', '2026-04-06', '2026-05-04', '2026-05-25', '2026-08-31', '2026-12-25', '2026-12-28',
    '2027-01-01', '2027-03-26', '2027-03-29', '2027-05-03', '2027-05-31', '2027-08-30', '2027-12-27', '2027-12-28'}


# ------------------------------------------------------------------------------------------------ calendars

def is_business(d, holidays):
    return d.weekday() < 5 and d.isoformat() not in holidays


def add_business(d, n, holidays):
    """Move n business days (negative = back) from d, not counting d itself."""
    step = 1 if n > 0 else -1
    left = abs(n)
    while left:
        d += dt.timedelta(days=step)
        if is_business(d, holidays):
            left -= 1
    return d


def last_business_of_month(y, m, holidays):
    d = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
    while not is_business(d, holidays):
        d -= dt.timedelta(days=1)
    return d


def shift_month(y, m, k):
    i = y * 12 + (m - 1) + k
    return i // 12, i % 12 + 1


def expiry(rule, y, m):
    """Last trading day of the (y, m) contract, by the exchange's published rule.

    brent: last business day of the second month preceding the contract month (ICE Brent; Dec expires end-Oct).
    wti:   three business days before the 25th of the month preceding delivery, or before the last business day
           preceding the 25th when the 25th is not a business day (NYMEX CL).
    ng:    three business days before the first calendar day of the delivery month (NYMEX NG).
    """
    if rule == 'brent':
        yy, mm = shift_month(y, m, -2)
        return last_business_of_month(yy, mm, UK_HOLIDAYS)
    if rule == 'wti':
        yy, mm = shift_month(y, m, -1)
        d = dt.date(yy, mm, 25)
        while not is_business(d, US_HOLIDAYS):
            d -= dt.timedelta(days=1)
        return add_business(d, -3, US_HOLIDAYS)
    if rule == 'ng':
        return add_business(dt.date(y, m, 1), -3, US_HOLIDAYS)
    raise ValueError(rule)


def contract_symbol(root, y, m):
    return '%s%s%02d.NYM' % (root, MONTH_CODES[m - 1], y % 100)


def front_second(rule, when):
    """(front, second) contract months (y, m) at datetime `when` (UTC). A contract is front until 18:00 UTC on its last
    trading day; the oracle has normally left it well before then, so the boundary convention rarely matters."""
    y, m = when.year, when.month
    for k in range(0, 6):
        cy, cm = shift_month(y, m, k)
        e = expiry(rule, cy, cm)
        if dt.datetime(e.year, e.month, e.day, 18, tzinfo=UTC) > when:
            return (cy, cm), shift_month(cy, cm, 1)
    raise ValueError('no front contract found for %s' % when)


# ------------------------------------------------------------------------------------------------ io

def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))
    tmp.replace(p)


def utc_iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).isoformat()


def safe(coin):
    """perp_collect.safe: HIP-3 names are `dex:SYMBOL` and the store writes the colon as a double underscore."""
    return coin.replace(':', '__').replace('/', '_')


def fetch_yahoo(symbol, interval, period1, period2, retries=5, pause=2.5):
    q = urllib.parse.urlencode({'period1': int(period1), 'period2': int(period2), 'interval': interval,
                                'includePrePost': 'false'})
    url = YAHOO + urllib.parse.quote(symbol) + '?' + q
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            time.sleep(pause)
            return d
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code == 404:
                time.sleep(pause)
                return {'chart': {'result': None, 'error': {'code': 'Not Found'}}}
            time.sleep(min(60, pause * 2 ** (a + 1)))
        except Exception as e:  # noqa: BLE001 - network errors are retried and then reported
            last = repr(e)[:120]
            time.sleep(min(60, pause * 2 ** (a + 1)))
    raise RuntimeError('yahoo %s: %s' % (symbol, last))


def yahoo_bars(d):
    """Chart JSON -> sorted list of {t (ms, bar start), o, h, l, c, v}; bars without a close are dropped."""
    r = ((d or {}).get('chart') or {}).get('result') or []
    if not r:
        return []
    r = r[0]
    ts = r.get('timestamp') or []
    q = (r.get('indicators') or {}).get('quote') or [{}]
    q = q[0]
    out = []
    for i, t in enumerate(ts):
        c = (q.get('close') or [None] * len(ts))[i]
        if c is None:
            continue
        out.append({'t': int(t) * 1000, 'o': (q.get('open') or [None] * len(ts))[i],
                    'h': (q.get('high') or [None] * len(ts))[i], 'l': (q.get('low') or [None] * len(ts))[i],
                    'c': float(c), 'v': (q.get('volume') or [None] * len(ts))[i]})
    out.sort(key=lambda b: b['t'])
    return out


# ------------------------------------------------------------------------------------------------ collect

def symbols_to_fetch(today, months_ahead=8):
    syms = {}
    for coin, spec in MARKETS.items():
        syms[spec['root'] + '=F'] = coin
        if not spec['rolls']:
            continue
        for k in range(0, months_ahead):
            y, m = shift_month(today.year, today.month, k)
            if expiry(spec['rule'], y, m) >= today:
                syms[contract_symbol(spec['root'], y, m)] = coin
    return syms


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw' / 'yahoo'
    raw.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    p1 = dt.datetime.fromisoformat(args.since).replace(tzinfo=UTC).timestamp()
    p2 = time.time()
    syms = symbols_to_fetch(dt.datetime.now(UTC).date())
    rows = {}
    for sym, coin in sorted(syms.items()):
        rec = {'coin': coin}
        for interval in ('60m', '1d'):
            d = fetch_yahoo(sym, interval, p1, p2)
            bars = yahoo_bars(d)
            fn = raw / ('%s_%s.json.gz' % (sym.replace('=', '_'), interval))
            with gzip.open(fn, 'wt') as f:
                json.dump({'symbol': sym, 'interval': interval, 'bars': bars,
                           'meta': ((d.get('chart') or {}).get('result') or [{}])[0].get('meta') if bars else None,
                           'error': (d.get('chart') or {}).get('error')}, f)
            rec[interval] = {'bars': len(bars), 'first': utc_iso(bars[0]['t']) if bars else None,
                             'last': utc_iso(bars[-1]['t']) if bars else None}
        rows[sym] = rec
        print(json.dumps({sym: rec}), flush=True)
    write_json(out / 'manifest.json', {'collected_at': dt.datetime.now(UTC).isoformat(), 'source': YAHOO,
                                       'since': args.since, 'symbols': rows, 'seconds': round(time.time() - t0, 1),
                                       'note': 'Yahoo removes expired contract months; continuous =F series carry '
                                               'the front month at each date.'})
    return 0


def load_bars(out, sym, interval='60m'):
    fn = Path(out) / 'raw' / 'yahoo' / ('%s_%s.json.gz' % (sym.replace('=', '_'), interval))
    if not fn.exists():
        return {}
    return {b['t']: b['c'] for b in read_gz(fn)['bars']}


# ------------------------------------------------------------------------------------------------ pure analysis

def asof(series_sorted_keys, series, t, max_age_ms):
    """Last value at or before t within max_age_ms; series_sorted_keys is the sorted key list of series."""
    import bisect
    i = bisect.bisect_right(series_sorted_keys, t) - 1
    if i < 0:
        return None
    k = series_sorted_keys[i]
    return series[k] if t - k <= max_age_ms else None


def front_weight(oracle, f1, f2, min_spread=0.004):
    """The oracle's weight on the front contract, or None when the calendar spread is too narrow to resolve it."""
    if oracle is None or f1 is None or f2 is None:
        return None
    if abs(f1 / f2 - 1.0) < min_spread:
        return None
    return (oracle - f2) / (f1 - f2)


def hedged_return(side, r_perp, r_hedge, funding_rate):
    """One hour of a side-s perp position hedged with the futures blend: s (r_perp - r_hedge) - s * funding.
    funding_rate > 0 means longs pay, so a long (s=+1) earns -funding_rate."""
    return side * (r_perp - r_hedge) - side * funding_rate


def unhedged_return(side, r_perp, funding_rate):
    return side * r_perp - side * funding_rate


def build_panel(coin, funding_rows, candle_rows, fut, rule, start_ms=None):
    """Hourly rows for one market: perp close, funding, premium, implied oracle, F1/F2, weight, returns.

    `fut` maps a Yahoo symbol to {bar_start_ms: close}; the continuous '=F' series stands in for the front month on
    hours when that month has already expired on Yahoo. Perp and futures closes are aligned on bar *end* times; the
    funding row stamped at hour T pays for the hour that ended at T.
    """
    fund = {}
    for r in funding_rows:
        T = int((int(r['time']) + HOUR_MS // 2) // HOUR_MS * HOUR_MS)
        fund[T] = (float(r['fundingRate']), float(r.get('premium') or 0.0))
    closes = {int(c['t']) + HOUR_MS: float(c['c']) for c in candle_rows}
    root = MARKETS[coin]['root']
    cont = fut.get(root + '=F', {})
    cont_end = {t + HOUR_MS: c for t, c in cont.items()}
    by_sym_end = {s: {t + HOUR_MS: c for t, c in v.items()} for s, v in fut.items()}
    keys = {s: sorted(v) for s, v in by_sym_end.items()}
    ck = sorted(cont_end)
    rows = []
    prev = None
    for T in sorted(closes):
        if start_ms and T < start_ms:
            continue
        when = dt.datetime.fromtimestamp(T / 1000, UTC)
        rate, prem = fund.get(T, (None, None))
        c = closes[T]
        oracle = c / (1.0 + prem) if prem is not None else None
        f1 = f2 = None
        s1 = s2 = None
        if rule:
            (y1, m1), (y2, m2) = front_second(rule, when)
            s1, s2 = contract_symbol(root, y1, m1), contract_symbol(root, y2, m2)
            # 3h tolerance: futures pause daily and an hourly bar can be missing; the weekend is not bridged here.
            f1 = asof(keys[s1], by_sym_end[s1], T, 3 * HOUR_MS) if s1 in by_sym_end else None
            if f1 is None:
                f1 = asof(ck, cont_end, T, 3 * HOUR_MS)
            f2 = asof(keys[s2], by_sym_end[s2], T, 3 * HOUR_MS) if s2 in by_sym_end else None
        else:
            f1 = asof(ck, cont_end, T, 3 * HOUR_MS)
        row = {'t': T, 'close': c, 'rate': rate, 'premium': prem, 'oracle': oracle, 'f1': f1, 'f2': f2,
               'front': s1, 'second': s2, 'w': front_weight(oracle, f1, f2) if rule else None}
        rows.append(row)
        prev = row
    # Returns need consecutive hours with both legs; the futures leg is carried across its daily pause and weekends
    # by holding the last price, which assigns the reopening gap to the first hour after it (where it belongs).
    last_f1 = last_f2 = None
    last_front = None
    for i, r in enumerate(rows):
        r['r_perp'] = (r['close'] / rows[i - 1]['close'] - 1.0) if i and rows[i - 1]['t'] == r['t'] - HOUR_MS else None
        f1, f2 = r['f1'], r['f2']
        # a change of front contract is not a return: reset the carried prices at the roll of the calendar
        if r['front'] != last_front:
            last_f1 = last_f2 = None
            last_front = r['front']
        r['r_f1'] = (f1 / last_f1 - 1.0) if (f1 is not None and last_f1) else None
        r['r_f2'] = (f2 / last_f2 - 1.0) if (f2 is not None and last_f2) else None
        if f1 is not None:
            last_f1 = f1
        if f2 is not None:
            last_f2 = f2
    return rows


def day_weights(rows):
    """The oracle's front weight at the start of each UTC day (median of the first three resolvable hours)."""
    by_day = {}
    for r in rows:
        if r['w'] is None:
            continue
        d = dt.datetime.fromtimestamp(r['t'] / 1000, UTC).date().isoformat()
        by_day.setdefault(d, []).append(r['w'])
    return {d: statistics.median(v[:3]) for d, v in by_day.items()}


def roll_calendar(rows):
    """Per UTC day: the oracle's weight at the first and last resolvable hour, the step, the spread and the funding."""
    days = {}
    for r in rows:
        d = dt.datetime.fromtimestamp(r['t'] / 1000, UTC).date().isoformat()
        x = days.setdefault(d, {'w': [], 'rate': [], 'premium': [], 'spread': [], 'front': None})
        if r['w'] is not None:
            x['w'].append(r['w'])
        if r['rate'] is not None:
            x['rate'].append(r['rate'])
        if r['premium'] is not None:
            x['premium'].append(r['premium'])
        if r['f1'] and r['f2']:
            x['spread'].append(r['f1'] / r['f2'] - 1.0)
        x['front'] = r['front'] or x['front']
    out = []
    for d in sorted(days):
        x = days[d]
        out.append({'day': d, 'front': x['front'],
                    'w_first': x['w'][0] if x['w'] else None, 'w_last': x['w'][-1] if x['w'] else None,
                    'w_median': statistics.median(x['w']) if x['w'] else None,
                    'funding_apr_longs_paid': (-statistics.fmean(x['rate']) * HOURS_PER_YEAR) if x['rate'] else None,
                    'premium_mean': statistics.fmean(x['premium']) if x['premium'] else None,
                    'spread_mean': statistics.fmean(x['spread']) if x['spread'] else None,
                    'hours': len(x['rate'])})
    return out


def hedge_returns(rows, mode):
    """Per-hour hedge return. mode 'front': the front contract alone. mode 'blend': w0 * r_f1 + (1 - w0) * r_f2 with
    w0 the oracle's weight at the start of the UTC day, clipped to [0, 1]; falls back to the front when the weight or
    the second leg is missing (and counts how often)."""
    w_day = day_weights(rows) if mode == 'blend' else {}
    out, fallback = [], 0
    for r in rows:
        if mode == 'front':
            out.append(r['r_f1'])
            continue
        d = dt.datetime.fromtimestamp(r['t'] / 1000, UTC).date().isoformat()
        w0 = w_day.get(d)
        if w0 is None or r['r_f2'] is None or r['r_f1'] is None:
            out.append(r['r_f1'])
            fallback += 1
            continue
        w0 = min(1.0, max(0.0, w0))
        out.append(w0 * r['r_f1'] + (1.0 - w0) * r['r_f2'])
    return out, fallback


def strategy_returns(rows, hedge, lookback_h, entry_apr, exit_apr=None, round_trip_bps=12.0, fut_bps_each_way=1.0,
                     hedged=True):
    """Hourly returns of: hold the paid side when the trailing-lookback mean funding APR exceeds entry_apr in
    magnitude; leave when it falls below exit_apr (default half the entry) or flips sign.

    The decision for hour i uses funding up to hour i-1 only. A position change costs half the perp round trip per
    entry or exit plus the futures commission when hedged. Hours with no perp return (gaps) earn nothing.
    Returns (returns, positions).
    """
    exit_apr = entry_apr / 2.0 if exit_apr is None else exit_apr
    rets, pos_series = [], []
    pos = 0
    hist = []
    for i, r in enumerate(rows):
        # decide with information through the previous hour
        tr = statistics.fmean(hist[-lookback_h:]) * HOURS_PER_YEAR if len(hist) >= lookback_h else None
        want = pos
        if tr is not None:
            paid = -1 if tr > 0 else 1          # funding > 0: longs pay, shorts are paid
            mag = abs(tr)
            if pos == 0 and mag >= entry_apr:
                want = paid
            elif pos != 0 and (mag < exit_apr or paid != pos):
                want = paid if mag >= entry_apr else 0
        cost = 0.0
        if want != pos:
            legs = abs(want - pos)              # 1 for open/close, 2 for a flip
            cost = legs * (round_trip_bps / 2.0 + (fut_bps_each_way if hedged else 0.0)) / 1e4
            pos = want
        g = 0.0
        if pos != 0 and r['r_perp'] is not None and r['rate'] is not None:
            h = hedge[i]
            if hedged:
                g = hedged_return(pos, r['r_perp'], h if h is not None else 0.0, r['rate'])
            else:
                g = unhedged_return(pos, r['r_perp'], r['rate'])
        rets.append(g - cost)
        pos_series.append(pos)
        if r['rate'] is not None:
            hist.append(r['rate'])
    return rets, pos_series


def window_stats(rows, rets, pos, t_from, t_to):
    sel = [i for i, r in enumerate(rows) if t_from <= r['t'] < t_to]
    x = [rets[i] for i in sel]
    p = B.perf(x, HOURS_PER_YEAR)
    t, pv = B.newey_west_t(x, lags=48) if len(x) > 60 else (None, None)
    bs = B.block_bootstrap(x, block=24, n=1000) if len(x) > 60 else None
    held = sum(1 for i in sel if pos[i] != 0)
    return {'hours': len(sel), 'hours_held': held, 'total_return': sum(x) if x else 0.0, 'perf': p,
            'nw_t': t, 'nw_p': pv, 'bootstrap_mean_ci': bs,
            'from': utc_iso(t_from), 'to': utc_iso(t_to)}


# ------------------------------------------------------------------------------------------------ the roll schedule

def business_days_of_month(y, m, holidays=US_HOLIDAYS):
    d, out = dt.date(y, m, 1), []
    while d.month == m:
        if is_business(d, holidays):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def us_dst(d):
    """US daylight time: second Sunday of March to first Sunday of November."""
    mar = dt.date(d.year, 3, 8)
    start = mar + dt.timedelta(days=(6 - mar.weekday()) % 7)
    nov = dt.date(d.year, 11, 1)
    end = nov + dt.timedelta(days=(6 - nov.weekday()) % 7)
    return start <= d < end


def step_hour_utc(d):
    """The Globex reopen, 18:00 New York: 22:00 UTC in US daylight time, 23:00 UTC otherwise."""
    return 22 if us_dst(d) else 23


def roll_steps(y, m, days=(5, 9), step=0.2):
    """The oracle's roll in month (y, m): (step datetime UTC, front weight after the step) for each of the 5th..9th US
    business days, a fifth of the way each evening at the Globex reopen.

    Measured, not assumed: on 2026-09-08/09/10/11/14 and 10-07/08/09 the implied front weight of all three XYZ energy
    oracles fell 1.00 -> 0.80 -> 0.60 -> 0.40 -> 0.20 -> 0.00 at 22:00 UTC on exactly those days (the August roll shows
    in the funding on 08-07, 10, 11, 12, 13 and July's on 07-08..14). This is the S&P GSCI roll convention: 20% a day
    over the fifth to ninth business days.
    """
    b = business_days_of_month(y, m)
    out = []
    for k, d in enumerate(b[days[0] - 1:days[1]], 1):
        out.append((dt.datetime(d.year, d.month, d.day, step_hour_utc(d), tzinfo=UTC), max(0.0, 1.0 - step * k)))
    return out


def predicted_weight(when, rule):
    """The old front's weight the schedule predicts at `when`: 1 before the month's first step, falling a fifth per
    step to 0, and 1 again once the rolled-out contract expires and the calendar's front becomes the new contract."""
    steps = roll_steps(when.year, when.month)
    (fy, fm), _ = front_second(rule, when)
    # the roll in a month leaves the contract that expires in that month (Brent Dec expires end-October, etc.)
    e = expiry(rule, fy, fm)
    if (e.year, e.month) != (when.year, when.month):
        return 1.0
    w = 1.0
    for t, after in steps:
        if when >= t:
            w = after
    return w


def roll_windows(first, last):
    """Every monthly roll between two datetimes: (month, first step, last step)."""
    y, m = first.year, first.month
    out = []
    while (y, m) <= (last.year, last.month):
        s = roll_steps(y, m)
        if s:
            out.append(('%04d-%02d' % (y, m), s[0][0], s[-1][0]))
        y, m = shift_month(y, m, 1)
    return out


def window_pnl(rows, hedge, t_entry, t_exit, side, round_trip_bps, fut_bps_each_way=1.0):
    """A position on `side` from t_entry to t_exit (bar-end times), hour by hour: funding received, hedged basis, the
    part of the basis at the step hours, and the net after one round trip. Hours without a perp return are skipped and
    counted."""
    fund = basis = step_basis = 0.0
    n = missing = 0
    for i, r in enumerate(rows):
        if not (t_entry < r['t'] <= t_exit):
            continue
        if r['r_perp'] is None or r['rate'] is None:
            missing += 1
            continue
        h = hedge[i] if hedge[i] is not None else 0.0
        fund += -side * r['rate']
        b = side * (r['r_perp'] - h)
        basis += b
        hr = dt.datetime.fromtimestamp(r['t'] / 1000, UTC)
        if hr.hour in (22, 23, 0):
            step_basis += b
        n += 1
    cost = (round_trip_bps + 2 * fut_bps_each_way) / 1e4
    return {'hours': n, 'missing_hours': missing, 'funding': fund, 'hedged_basis': basis,
            'basis_at_step_hours': step_basis, 'gross': fund + basis, 'cost': cost, 'net': fund + basis - cost}


def evaluate_windows(rows, h_blend, h_front, rule, round_trip_bps, entries=None):
    """Hold the side the curve pays (long in backwardation, short in contango) through each month's roll.

    No parameter is fitted: the side is the sign of F1/F2 at entry, the window is the published schedule. Entry
    variants are reported side by side rather than chosen: 'eve' enters at 21:00 UTC before the first step and leaves
    an hour after the last; 'day' enters at 00:00 UTC on the first roll day (collecting the premium that builds into
    the first step) and leaves at 00:00 UTC the day after the last step.
    """
    if not rows:
        return []
    first = dt.datetime.fromtimestamp(rows[0]['t'] / 1000, UTC)
    last = dt.datetime.fromtimestamp(rows[-1]['t'] / 1000, UTC)
    by_t = {r['t']: r for r in rows}
    out = []
    for month, s1, s5 in roll_windows(first, last):
        d1 = s1.date()
        variants = {
            'eve': (s1 - dt.timedelta(hours=1), s5 + dt.timedelta(hours=1)),
            'day': (dt.datetime(d1.year, d1.month, d1.day, tzinfo=UTC),
                    dt.datetime(s5.year, s5.month, s5.day, tzinfo=UTC) + dt.timedelta(days=1)),
        }
        rec = {'month': month, 'first_step': s1.isoformat(), 'last_step': s5.isoformat(), 'complete': s5 < last}
        for name, (te, tx) in variants.items():
            te_ms, tx_ms = int(te.timestamp() * 1000), int(tx.timestamp() * 1000)
            r0 = by_t.get(te_ms) or next((r for r in rows if r['t'] >= te_ms), None)
            if r0 is None:
                continue
            f1, f2 = r0.get('f1'), r0.get('f2')
            spread = (f1 / f2 - 1.0) if (f1 and f2) else None
            side = (1 if spread > 0 else -1) if spread is not None else None
            if side is None:
                # no second month at entry: fall back on the sign of the funding the book was already charging
                prior = [r['rate'] for r in rows if te_ms - 24 * HOUR_MS < r['t'] <= te_ms and r['rate'] is not None]
                side = (1 if statistics.fmean(prior) < 0 else -1) if prior else 1
            rec[name] = {'entry': te.isoformat(), 'exit': tx.isoformat(), 'side': side, 'spread_at_entry': spread,
                         'blend': window_pnl(rows, h_blend, te_ms, tx_ms, side, round_trip_bps),
                         'front': window_pnl(rows, h_front, te_ms, tx_ms, side, round_trip_bps),
                         'unhedged': window_pnl(rows, [0.0] * len(rows), te_ms, tx_ms, side, round_trip_bps, 0.0)}
        out.append(rec)
    return out


def schedule_fit(rows, rule):
    """How well the published schedule predicts the measured front weight, over hours where the weight resolves:
    median absolute error and the share within 0.1, excluding the hour of a step (an hourly mean straddles it)."""
    errs = []
    for r in rows:
        if r['w'] is None:
            continue
        when = dt.datetime.fromtimestamp(r['t'] / 1000, UTC)
        if when.hour == step_hour_utc(when.date()):
            continue
        errs.append(abs(r['w'] - predicted_weight(when, rule)))
    if not errs:
        return None
    errs.sort()
    return {'hours': len(errs), 'median_abs_error': errs[len(errs) // 2],
            'share_within_0_1': sum(1 for e in errs if e <= 0.1) / len(errs)}


def load_hl(hl_dir, coin):
    hl = Path(hl_dir)
    fp, cp = hl / 'funding' / (safe(coin) + '.json.gz'), hl / 'candles_1h' / (safe(coin) + '.json.gz')
    if not fp.exists() or not cp.exists():
        return None, None
    return read_gz(fp), read_gz(cp)


def cmd_analyze(args):
    out = Path(args.out)
    cut = int(dt.datetime.fromisoformat(args.cutoff).timestamp() * 1000)
    start = int(dt.datetime.fromisoformat(args.since).replace(tzinfo=UTC).timestamp() * 1000)
    man = json.loads((out / 'manifest.json').read_text())
    syms_by_coin = {}
    for s, rec in man['symbols'].items():
        syms_by_coin.setdefault(rec['coin'], []).append(s)
    res = {'generated': dt.datetime.now(UTC).isoformat(), 'cutoff': args.cutoff, 'since': args.since,
           'hl_store': str(args.hl), 'markets': {}}
    lookbacks, entries = [int(x) for x in args.lookbacks.split(',')], [float(x) for x in args.entries.split(',')]
    for coin, spec in MARKETS.items():
        fr, cr = load_hl(args.hl, coin)
        if not fr:
            continue
        fut = {s: load_bars(out, s) for s in syms_by_coin.get(coin, [])}
        rows = build_panel(coin, fr, cr, fut, spec['rule'], start_ms=start)
        if not rows:
            continue
        end = rows[-1]['t'] + 1
        h_front, _ = hedge_returns(rows, 'front')
        h_blend, fb = hedge_returns(rows, 'blend') if spec['rule'] else (h_front, len(rows))
        cal = roll_calendar(rows)
        # always-on carry diagnostics: what the paid side collected and what the step cost, hour by hour
        rt = args.round_trip_bps
        variants, oos = {}, {}
        for k in lookbacks:
            for x in entries:
                name = 'k=%dh,X=%d%%' % (k, round(100 * x))
                r_in, _ = strategy_returns(rows, h_front, k, x, round_trip_bps=rt)
                variants[name] = r_in
        n = len(rows)
        cut_i = next((i for i, r in enumerate(rows) if r['t'] >= cut), n)
        sel = B.choose_then_test(variants, frac=cut_i / n if n else 0.5, periods_per_year=HOURS_PER_YEAR) \
            if 0 < cut_i < n else None
        chosen = sel['chosen'] if sel else None
        detail = {}
        if chosen:
            k = int(chosen.split(',')[0][2:-1])
            x = float(chosen.split('X=')[1][:-1]) / 100.0
            for label, hedge, hedged in (('front_hedge', h_front, True), ('blend_hedge', h_blend, True),
                                         ('unhedged', h_front, False)):
                rets, pos = strategy_returns(rows, hedge, k, x, round_trip_bps=rt, hedged=hedged)
                detail[label] = {'in_sample': window_stats(rows, rets, pos, start, cut),
                                 'out_of_sample': window_stats(rows, rets, pos, cut, end)}
        # the always-long/short-the-paid-side decomposition over the OOS period, by component
        comp = decompose(rows, h_blend, cut, end)
        windows = evaluate_windows(rows, h_blend, h_front, spec['rule'], rt) if spec['rule'] else []
        res['markets'][coin] = {
            'rolls': spec['rolls'], 'hours': n, 'first': utc_iso(rows[0]['t']), 'last': utc_iso(rows[-1]['t']),
            'hours_with_both_legs': sum(1 for r in rows if r['f1'] is not None and r['f2'] is not None),
            'hours_with_weight': sum(1 for r in rows if r['w'] is not None),
            'blend_fallback_hours': fb, 'calendar': cal, 'selection': sel, 'chosen_detail': detail,
            'oos_components_held_on_paid_side': comp,
            'schedule_fit': schedule_fit(rows, spec['rule']) if spec['rule'] else None,
            'roll_windows': windows,
            'funding_vs_step': funding_vs_step(rows, spec['rule']) if spec['rule'] else None,
        }
        print(coin, n, 'chosen', chosen, flush=True)
    write_json(out / 'analysis.json', res)
    return 0


def funding_vs_step(rows, rule):
    """Per roll day: the funding the paid side collected over the 24 hours ending at that day's step, against the step
    itself, a fifth of the calendar spread (F1/F2 - 1 read an hour before the step). If the market prices the roll,
    the ratio is near one."""
    out = []
    if not rows:
        return out
    first = dt.datetime.fromtimestamp(rows[0]['t'] / 1000, UTC)
    last = dt.datetime.fromtimestamp(rows[-1]['t'] / 1000, UTC)
    by_t = {r['t']: r for r in rows}
    for month, s1, s5 in roll_windows(first, last):
        for t, after in roll_steps(s1.year, s1.month):
            if t > last:
                continue
            ts = int(t.timestamp() * 1000)
            pre = by_t.get(ts - HOUR_MS)
            if not pre or not pre.get('f1') or not pre.get('f2'):
                continue
            spread = pre['f1'] / pre['f2'] - 1.0
            fund = [r['rate'] for r in rows if ts - 24 * HOUR_MS < r['t'] <= ts and r['rate'] is not None]
            if len(fund) < 20:
                continue
            side = 1 if spread > 0 else -1
            got = -side * sum(fund)
            step = abs(spread) * 0.2
            out.append({'step_utc': t.isoformat(), 'weight_after': after, 'spread': spread, 'funding_24h': got,
                        'step': step, 'ratio': got / step if step else None})
    return out


def decompose(rows, hedge, t_from, t_to):
    """Over [t_from, t_to), a position always on the side the *previous* hour's funding paid: total funding received,
    total hedged basis (s (r_perp - r_hedge)), split into hours at the 22:00 UTC step and the rest."""
    fund = basis = basis_step = 0.0
    n = 0
    for i, r in enumerate(rows):
        if not (t_from <= r['t'] < t_to) or i == 0:
            continue
        pr = rows[i - 1]['rate']
        if pr is None or r['rate'] is None or r['r_perp'] is None:
            continue
        s = -1 if pr > 0 else 1
        h = hedge[i] if hedge[i] is not None else 0.0
        fund += -s * r['rate']
        b = s * (r['r_perp'] - h)
        basis += b
        hr = dt.datetime.fromtimestamp(r['t'] / 1000, UTC).hour
        if hr in (22, 23):
            basis_step += b
        n += 1
    return {'hours': n, 'funding_received': fund, 'hedged_basis': basis, 'hedged_basis_22_23utc': basis_step,
            'net': fund + basis}


# ------------------------------------------------------------------------------------------------ render

def pct(x, d=1):
    return '—' if x is None else ('%.*f%%' % (d, 100 * x))


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# Roll carry — tables', '', 'Generated %s from `analysis.json`; cutoff %s (the book quote).' % (A['generated'], A['cutoff']), '']
    L.append('| market | hours | both legs | chosen rule | IS ann. | OOS ann. (blend hedge) | OOS ann. (front hedge) | OOS unhedged | OOS NW t | OOS hours held |')
    L.append('|---|---|---|---|---|---|---|---|---|---|')
    for coin, m in A['markets'].items():
        d = m.get('chosen_detail') or {}
        g = lambda lab, part, key: (((d.get(lab) or {}).get(part) or {}).get('perf') or {}).get(key)
        o = (d.get('blend_hedge') or {}).get('out_of_sample') or {}
        L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s |' % (
            coin, m['hours'], m['hours_with_both_legs'], (m.get('selection') or {}).get('chosen') or '—',
            pct(g('front_hedge', 'in_sample', 'ann_return'), 0), pct(g('blend_hedge', 'out_of_sample', 'ann_return'), 0),
            pct(g('front_hedge', 'out_of_sample', 'ann_return'), 0), pct(g('unhedged', 'out_of_sample', 'ann_return'), 0),
            ('%.2f' % o['nw_t']) if o.get('nw_t') is not None else '—', o.get('hours_held', '—')))
    L.append('')
    for coin, m in A['markets'].items():
        if not m['rolls']:
            continue
        L.append('## %s — daily roll calendar' % coin)
        L.append('')
        L.append('| day | front | w first | w last | longs paid (APR) | premium | F1/F2 − 1 |')
        L.append('|---|---|---|---|---|---|---|')
        for c in m['calendar'][-45:]:
            f = lambda v: '—' if v is None else '%.2f' % v
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (c['day'], c['front'] or '—', f(c['w_first']), f(c['w_last']),
                                                         pct(c['funding_apr_longs_paid'], 0), pct(c['premium_mean'], 2),
                                                         pct(c['spread_mean'], 2)))
        L.append('')
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:20]))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--since', default='2025-09-01')
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--hl', default='research/2026-10-09/perps_hip3')
    a.add_argument('--since', default='2026-07-01')
    a.add_argument('--cutoff', default=BOOK_QUOTE_UTC)
    a.add_argument('--lookbacks', default='6,24,72')
    a.add_argument('--entries', default='0.5,1.0,1.5,2.0')
    a.add_argument('--round-trip-bps', type=float, default=12.6, help='perp round trip at $100k on 2026-09-10 (Brent)')
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
