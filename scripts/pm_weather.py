#!/usr/bin/env python3
"""Daily temperature markets against a calibrated numerical forecast, on Kalshi and Polymarket.

Why. Kalshi lists a daily high-temperature ladder for a dozen US cities (six 2-degree buckets per city-day, one of
which pays) and Polymarket lists the same kind of ladder for ~40 cities. The hypothesis the owner asked to test: retail
prices these ladders without a forecast model, a calibrated forecast distribution prices the buckets better, and the
gap pays after fees when entered hours before the outcome. That is not a latency trade: the forecast that matters (the
National Blend of Models, NBM) updates every few hours and the decision times are fixed clock times.

The forecast. IEM archives the NBM's station text bulletin (NBS): for each station a max/min temperature (TXN) and
its spread (XND) for each 12-hour period, from runs at 01/07/13/19 UTC (00/06/12/18 UTC from 2026). The predictive
distribution for a day's high is a normal around TXN plus a station-and-season bias, with a variance fitted to the
training-period errors (a + b x XND^2), discretised to whole degrees because the climate report prints integers. Every
parameter is fitted on a training year that ends before the first market day, and calibration (PIT) is checked on
the trading period before any return is computed.

What is traded. At a pre-registered clock time (16:00 local the day before, 08:00 local on the day), for every bucket
of every city-day ladder: buy YES (or NO) when the model probability exceeds the executable price by an edge
threshold. A taker pays the ask (Kalshi: the hourly candle's closing yes_ask, or 1 - yes_bid for NO; Polymarket: the
midpoint plus the measured half-spread) plus the fee, and holds to settlement. A resting maker bid earns only its limit
and fills only if a later candle's ask trades through it (a conservative queue).

    uv run python scripts/pm_weather.py kalshi   --out research/2026-10-14/pm_weather   (markets + hourly candles)
    uv run python scripts/pm_weather.py wx       --out research/2026-10-14/pm_weather   (IEM climate reports + NBM)
    uv run python scripts/pm_weather.py pm       --out research/2026-10-14/pm_weather   (Polymarket events + prices)
    uv run python scripts/pm_weather.py books    --out research/2026-10-14/pm_weather   (live depth, both venues)
    uv run python scripts/pm_weather.py analyze  --out research/2026-10-14/pm_weather
    uv run python scripts/pm_weather.py render   --out research/2026-10-14/pm_weather
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import io
import json
import math
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
from polymarket_history import Http, parse_ts, read_gz, write_gz, update_manifest, fee_rate, categorize  # noqa: E402
from pm_crossvenue import kalshi_fee  # noqa: E402

KALSHI = 'https://api.elections.kalshi.com/trade-api/v2'
GAMMA = 'https://gamma-api.polymarket.com'
CLOB = 'https://clob.polymarket.com'
IEM = 'https://mesonet.agron.iastate.edu'
UTC = dt.timezone.utc
DAY = 86400.0
HOUR = 3600.0
SSR = 0.038

# ------------------------------------------------------------------------------------------------ pre-registration
# Fixed on 2026-10-14 before any market price was joined to a forecast (see analysis.json['preregistration']).
MARKET_START = '2025-09-01'          # first market day collected
MARKET_END = '2026-10-12'            # last settled market day
TRAIN_START = '2024-09-01'           # forecast error model: fitted on NBM vs climate report over this year only
TRAIN_END = '2025-08-31'
CUTOFF = '2026-04-01'                # choose the trading variant on market days before, test once on days from it
DECISIONS = {'d1_16': (-1, 16), 'd0_08': (0, 8)}   # (day offset from the market day, local hour)
EDGES = [0.03, 0.06, 0.10, 0.15]     # model probability minus all-in cost per $1, before the variant chooses
NBM_LAG_H = 2.5                      # an NBM run is usable this many hours after its nominal cycle time

# Kalshi daily-high series and the climate-report station each settles on (rules_primary is checked in `analyze`).
KALSHI_SERIES = {
    'KXHIGHNY': {'station': 'KNYC', 'tz': 'America/New_York', 'city': 'NYC (Central Park)'},
    'KXHIGHCHI': {'station': 'KMDW', 'tz': 'America/Chicago', 'city': 'Chicago (Midway)'},
    'KXHIGHMIA': {'station': 'KMIA', 'tz': 'America/New_York', 'city': 'Miami'},
    'KXHIGHAUS': {'station': 'KAUS', 'tz': 'America/Chicago', 'city': 'Austin (Bergstrom)'},
    'KXHIGHDEN': {'station': 'KDEN', 'tz': 'America/Denver', 'city': 'Denver'},
    'KXHIGHPHIL': {'station': 'KPHL', 'tz': 'America/New_York', 'city': 'Philadelphia'},
}


def utc_iso(ts=None):
    ts = time.time() if ts is None else ts
    return dt.datetime.fromtimestamp(ts, UTC).isoformat(timespec='seconds')


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


MONTHS = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT',
                                           'NOV', 'DEC'])}


def kalshi_event_date(event_ticker):
    """'KXHIGHNY-26AUG13' -> '2026-08-13'."""
    m = re.search(r'-(\d{2})([A-Z]{3})(\d{2})$', event_ticker or '')
    if not m or m.group(2) not in MONTHS:
        return None
    return '20%s-%02d-%s' % (m.group(1), MONTHS[m.group(2)], m.group(3))


def local_ts(date_str, offset_days, hour, tz):
    """Unix time of `hour`:00 local on date + offset_days in zone tz (DST-aware)."""
    d = dt.date.fromisoformat(date_str) + dt.timedelta(days=offset_days)
    return dt.datetime(d.year, d.month, d.day, hour, tzinfo=ZoneInfo(tz)).timestamp()


# ------------------------------------------------------------------------------------------------ pure money rules

def bucket_bounds(strike_type, floor_strike, cap_strike):
    """Kalshi strike fields -> the inclusive integer range [lo, hi] of reported highs that pay YES.

    'greater' with floor f pays on T > f, i.e. T >= f + 1; 'less' with cap c pays on T < c, i.e. T <= c - 1;
    'between' pays on floor <= T <= cap (both whole degrees, '91-92' is floor 91 cap 92). The climate report prints
    integers, so these are exact."""
    if strike_type == 'greater':
        return int(round(floor_strike)) + 1, None
    if strike_type == 'less':
        return None, int(round(cap_strike)) - 1
    if strike_type == 'between':
        return int(round(floor_strike)), int(round(cap_strike))
    raise ValueError('unknown strike type %r' % strike_type)


def pays_yes(lo, hi, value):
    return (lo is None or value >= lo) and (hi is None or value <= hi)


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bucket_prob(lo, hi, mu, sd, cdf=None):
    """P(lo <= round(T) <= hi) for T = mu + sd * Z, Z with standardised CDF `cdf` (normal by default): the reported
    integer is the rounded continuous temperature, so the integer k occupies [k - 0.5, k + 0.5)."""
    cdf = cdf or norm_cdf
    a = 0.0 if lo is None else cdf((lo - 0.5 - mu) / sd)
    b = 1.0 if hi is None else cdf((hi + 0.5 - mu) / sd)
    return max(0.0, b - a)


def kernel_cdf(zs, h):
    """The CDF of a Gaussian-kernel-smoothed sample of standardised errors."""
    n = float(len(zs))
    return lambda x: sum(norm_cdf((x - z) / h) for z in zs) / n


def kalshi_taker_cost(price, contracts=100.0):
    """All-in cost per contract of a Kalshi taker buy at `price` (fee rounded up to the cent on the order)."""
    return price + kalshi_fee(contracts, price) / contracts


def pm_taker_cost(price, rate):
    """All-in cost per share of a Polymarket taker buy at `price` (no rounding; makers pay nothing)."""
    return price + rate * price * (1.0 - price)


def trade_pnl(cost, payout):
    """Profit per $1 staked of buying at all-in `cost` a share that pays `payout` (1 or 0)."""
    return payout / cost - 1.0


def maker_filled(limit, later_asks):
    """A resting bid at `limit` fills only if a later ask prints strictly below it (a trade through the level, so the
    queue ahead of us at `limit` is assumed to absorb everything that prints exactly at it)."""
    return any(a is not None and a < limit - 1e-9 for a in later_asks)


# ------------------------------------------------------------------------------------------------ http

class TextHttp:
    """Paced text GET for IEM (CSV and JSON), backing off on 429/503 and on IEM's 'Too many requests' page."""

    def __init__(self, interval=2.0, timeout=120, retries=6):
        self.interval, self.timeout, self.retries = interval, timeout, retries
        self.next_at = 0.0
        self.lock = threading.Lock()
        self.n = self.errors = self.throttled = 0

    def get(self, url):
        last = None
        for attempt in range(self.retries):
            with self.lock:
                now = time.monotonic()
                wait = self.next_at - now
                self.next_at = max(now, self.next_at) + self.interval
            if wait > 0:
                time.sleep(wait)
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (llm-quant research; pm_weather)'})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    txt = r.read().decode('utf-8', 'replace')
                if 'Too many requests' in txt[:200]:
                    raise urllib.error.HTTPError(url, 429, 'throttled', None, None)
                self.n += 1
                return txt
            except urllib.error.HTTPError as e:
                self.errors += 1
                last = 'HTTP %s' % e.code
                if e.code in (429, 503):
                    self.throttled += 1
                    time.sleep(min(60.0, 5.0 * 2 ** attempt))
                    continue
                if e.code >= 500:
                    time.sleep(min(30.0, 2.0 * 2 ** attempt))
                    continue
                return None
            except Exception as e:  # noqa: BLE001 - network errors are retried, then reported
                self.errors += 1
                last = repr(e)[:120]
                time.sleep(min(30.0, 2.0 * 2 ** attempt))
        print(json.dumps({'give_up': url[:160], 'last': last}), flush=True)
        return None

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


# ------------------------------------------------------------------------------------------------ kalshi collect

class GentleHttp(Http):
    """polymarket_history.Http with a flatter 429 policy: the shared Kalshi budget throttles ~20% of requests when
    several workers run, and Http's doubling global backoff (2, 4, 8, 16, 30 s, blocking every thread) cut throughput
    to ~1 request/s. Here a 429 pauses all threads 1.5 s x attempt (at most 6 s); pacing stays at >= 0.25 s."""

    def request(self, url, body=None):
        last = None
        for attempt in range(self.retries + 4):
            self._pace()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (llm-quant research; pm_weather)',
                                                       'Accept': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                with self.lock:
                    self.n += 1
                return json.loads(raw)
            except urllib.error.HTTPError as e:
                with self.lock:
                    self.errors += 1
                last = 'HTTP %s' % e.code
                if e.code == 429:
                    with self.lock:
                        self.throttled += 1
                        self.next_at = time.monotonic() + min(6.0, 1.5 * (attempt + 1))
                    continue
                if e.code in (500, 502, 503, 504):
                    time.sleep(min(10.0, 0.5 * 2 ** attempt))
                    continue
                return {'__error__': last, '__code__': e.code}
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, ValueError) as e:
                with self.lock:
                    self.errors += 1
                last = repr(e)[:200]
                time.sleep(min(10.0, 0.5 * 2 ** attempt))
        return {'__error__': 'retry limit: %s' % last}


def kalshi_list(http, path, params, max_pages=200):
    rows, cur = [], None
    for _ in range(max_pages):
        q = dict(params)
        if cur:
            q['cursor'] = cur
        d = http.request(KALSHI + path + '?' + urllib.parse.urlencode(q))
        if '__error__' in d:
            print(json.dumps({'error': d['__error__'], 'path': path, 'params': params}), flush=True)
            break
        rows.extend(d.get('markets') or [])
        cur = d.get('cursor')
        if not cur or not d.get('markets'):
            break
    return rows


KM_KEEP = ['ticker', 'event_ticker', 'status', 'result', 'expiration_value', 'open_time', 'close_time',
           'settlement_ts', 'floor_strike', 'cap_strike', 'strike_type', 'volume_fp', 'volume', 'open_interest_fp',
           'rules_primary', 'title', 'yes_sub_title', 'settlement_value_dollars']


def parse_candle(c):
    """One Kalshi hourly candle in either the live (`close_dollars`, `volume_fp`) or the historical (`close`,
    `volume`) shape -> {t, bid, ask, last, vol}. A 0 bid or a 1 ask means that side of the book was empty."""
    def side(obj, k):
        obj = obj or {}
        return fnum(obj.get(k + '_dollars'), fnum(obj.get(k)))
    yb, ya = side(c.get('yes_bid'), 'close'), side(c.get('yes_ask'), 'close')
    pr = c.get('price') or {}
    return {'t': int(c['end_period_ts']), 'bid': yb, 'ask': ya,
            'ask_low': side(c.get('yes_ask'), 'low'), 'bid_high': side(c.get('yes_bid'), 'high'),
            'last': side(pr, 'close'), 'vol': fnum(c.get('volume_fp'), fnum(c.get('volume'), 0.0)) or 0.0}


def cmd_kalshi(args):
    out = Path(args.out)
    raw = out / 'raw' / 'kalshi'
    raw.mkdir(parents=True, exist_ok=True)
    http = GentleHttp(interval=args.interval)
    t0 = time.time()
    series = args.series.split(',') if args.series else list(KALSHI_SERIES)
    lo, hi = args.start or MARKET_START, args.end or MARKET_END
    plan = []
    for s in series:
        mp = raw / ('markets_%s.json.gz' % s)
        if mp.exists() and not args.refresh:
            ms = read_gz(mp)
        else:
            hist = kalshi_list(http, '/historical/markets', {'series_ticker': s, 'limit': 1000})
            live = kalshi_list(http, '/markets', {'series_ticker': s, 'status': 'settled', 'limit': 1000})
            seen, ms = set(), []
            for src, rows in (('historical', hist), ('live', live)):
                for m in rows:
                    if m['ticker'] in seen:
                        continue
                    seen.add(m['ticker'])
                    r = {k: m.get(k) for k in KM_KEEP}
                    r['src'] = src
                    r['date'] = kalshi_event_date(m.get('event_ticker'))
                    ms.append(r)
            write_gz(mp, ms)
        sel = [m for m in ms if m['date'] and lo <= m['date'] <= hi]
        print(json.dumps({'series': s, 'markets': len(ms), 'in_window': len(sel),
                          'first': min((m['date'] for m in ms if m['date']), default=None),
                          'last': max((m['date'] for m in ms if m['date']), default=None)}), flush=True)
        plan.extend((s, m) for m in sel)
    if args.list_only:
        return 0
    cdir = raw / 'candles'
    # The batch endpoint (/markets/candlesticks) also serves markets archived past the historical cutoff (checked
    # 2026-10-14 on KXHIGHNY-26AUG13), so every event is one request; the per-market historical endpoint is kept for
    # a ticker the batch call does not return.
    live_events = collections.defaultdict(list)
    todo_hist = []
    if args.single_only:
        # The batch call returns nothing for most markets archived before ~April 2026 and the per-market endpoint is
        # throttled to ~1.6/s by the shared IP, so the remaining markets are fetched in an order that fills the
        # window evenly (every 4th day first, then the days between): a run stopped early still spans both sides
        # of the cutoff with whole days (all six cities)
        d0 = dt.date.fromisoformat(lo)
        def order(item):
            k = (dt.date.fromisoformat(item[1]['date']) - d0).days
            return ([0, 2, 1, 3].index(k % 4), k, item[0])
        todo_hist = sorted(((s, m) for s, m in plan if not (cdir / s / ('%s.json.gz' % m['ticker'])).exists()),
                           key=order)
    else:
        for s, m in plan:
            if not (cdir / s / ('%s.json.gz' % m['ticker'])).exists():
                live_events[(s, m['event_ticker'])].append(m)
    print(json.dumps({'todo_events': len(live_events), 'todo_single': len(todo_hist)}), flush=True)
    done = [0]
    lock = threading.Lock()

    def window(m):
        a = parse_ts(m.get('open_time')) or 0
        b = parse_ts(m.get('close_time')) or a + 3 * DAY
        return int(a) - 3600, int(b) + 3600

    def one_hist(item):
        s, m = item
        a, b = window(m)
        d = http.request(KALSHI + '/historical/markets/%s/candlesticks?%s' % (
            m['ticker'], urllib.parse.urlencode({'start_ts': a, 'end_ts': b, 'period_interval': 60})))
        if '__error__' in d:
            return 'error'
        write_gz(cdir / s / ('%s.json.gz' % m['ticker']),
                 [parse_candle(c) for c in d.get('candlesticks') or []])
        with lock:
            done[0] += 1
            if done[0] % 500 == 0:
                print(json.dumps({'done': done[0], 'elapsed_s': round(time.time() - t0), **http.stats()}),
                      flush=True)
        return 'ok'

    def one_event(item):
        (s, ev), ms = item
        a = min(window(m)[0] for m in ms)
        b = max(window(m)[1] for m in ms)
        d = http.request(KALSHI + '/markets/candlesticks?%s' % urllib.parse.urlencode(
            {'market_tickers': ','.join(m['ticker'] for m in ms), 'start_ts': a, 'end_ts': b,
             'period_interval': 60}))
        if '__error__' in d:
            return 'error'
        got = {x.get('market_ticker') or x.get('ticker'): x.get('candlesticks') or [] for x in d.get('markets') or []}
        missing = 0
        for m in ms:
            if m['ticker'] not in got:
                missing += 1
                todo_hist.append((s, m))
                continue
            write_gz(cdir / s / ('%s.json.gz' % m['ticker']), [parse_candle(c) for c in got[m['ticker']]])
        with lock:
            done[0] += 1
            if done[0] % 200 == 0:
                print(json.dumps({'events_done': done[0], 'elapsed_s': round(time.time() - t0), **http.stats()}),
                      flush=True)
        return 'ok' if not missing else 'partial'

    res = collections.Counter()
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(one_event, list(live_events.items())):
            res['batch_' + r] += 1
        for r in ex.map(one_hist, list(todo_hist)):
            res['single_' + r] += 1
    update_manifest(out, 'kalshi', {'fetched_at': utc_iso(t0), 'finished_at': utc_iso(), 'series': series,
                                    'window': [lo, hi], 'markets_in_window': len(plan), 'results': dict(res),
                                    'http': http.stats(), 'sources': [KALSHI + '/historical/markets',
                                                                      KALSHI + '/markets?status=settled',
                                                                      KALSHI + '/historical/markets/{t}/candlesticks',
                                                                      KALSHI + '/markets/candlesticks']})
    print(json.dumps({'results': dict(res), **http.stats(), 'seconds': round(time.time() - t0)}), flush=True)
    return 0


# ------------------------------------------------------------------------------------------------ weather collect

# Polymarket's US daily-high ladders and the station each resolves on (descriptions read 2026-10-14: Weather
# Underground's daily history through early 2026, then "the highest reading under the Temp column" of NOAA's
# timeseries page, hourly data, whole degrees F, Weather Underground as the fallback). Both read METAR reports, so the
# settlement value is rebuilt from IEM's METAR archive, not from the climate report.
PM_CITIES = {
    'NYC': {'station': 'KLGA', 'asos': 'LGA', 'tz': 'America/New_York'},
    'Miami': {'station': 'KMIA', 'asos': 'MIA', 'tz': 'America/New_York'},
    'Dallas': {'station': 'KDAL', 'asos': 'DAL', 'tz': 'America/Chicago'},
    'Atlanta': {'station': 'KATL', 'asos': 'ATL', 'tz': 'America/New_York'},
    'Chicago': {'station': 'KORD', 'asos': 'ORD', 'tz': 'America/Chicago'},
    'Seattle': {'station': 'KSEA', 'asos': 'SEA', 'tz': 'America/Los_Angeles'},
}


def parse_nbs_csv(txt):
    """IEM mos.py CSV for model NBS -> [[runtime_ts, ftime_ts, txn, xnd, tmp]] for rows that carry a TXN (the 12-hour
    max at 00 UTC and the 12-hour min at 12 UTC) or an hourly temperature."""
    rows = []
    rd = csv.DictReader(io.StringIO(txt))
    for r in rd:
        rt = parse_ts((r.get('runtime') or '').replace(' ', 'T') + 'Z') if r.get('runtime') else None
        ft = parse_ts((r.get('ftime') or '').replace(' ', 'T') + 'Z') if r.get('ftime') else None
        if rt is None or ft is None:
            continue
        txn, xnd, tmp = fnum(r.get('txn')), fnum(r.get('xnd')), fnum(r.get('tmp'))
        if txn is None and tmp is None:
            continue
        rows.append([int(rt), int(ft), txn, xnd, tmp])
    return rows


def month_chunks(start, end, months=3):
    a = dt.date.fromisoformat(start)
    e = dt.date.fromisoformat(end)
    while a < e:
        y, m = a.year + (a.month - 1 + months) // 12, (a.month - 1 + months) % 12 + 1
        b = min(e, dt.date(y, m, 1))
        yield a.isoformat(), b.isoformat()
        a = b


def cmd_wx(args):
    out = Path(args.out)
    raw = out / 'raw' / 'wx'
    raw.mkdir(parents=True, exist_ok=True)
    http = TextHttp(interval=args.interval)
    t0 = time.time()
    k_stations = sorted({v['station'] for v in KALSHI_SERIES.values()})
    p_stations = sorted({v['station'] for v in PM_CITIES.values()})
    res = collections.Counter()
    # 1. NWS daily climate reports (CLI), parsed by IEM: Kalshi's settlement source through 2026-09
    for st in k_stations + p_stations:
        for yr in (2024, 2025, 2026):
            p = raw / 'cli' / ('%s_%d.json' % (st, yr))
            if p.exists():
                continue
            txt = http.get(IEM + '/json/cli.py?' + urllib.parse.urlencode({'station': st, 'year': yr}))
            if txt is None:
                res['cli_error'] += 1
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt)
            res['cli'] += 1
    # 2. NBM station text (NBS) archive: TXN/XND per run
    for st in k_stations + p_stations:
        for a, b in month_chunks(args.nbs_start, args.nbs_end, 3):
            p = raw / 'nbs' / st / ('%s_%s.json.gz' % (a, b))
            if p.exists():
                continue
            txt = http.get(IEM + '/cgi-bin/request/mos.py?' + urllib.parse.urlencode(
                {'station': st, 'model': 'NBS', 'sts': a + 'T00:00Z', 'ets': b + 'T00:00Z', 'format': 'csv'}))
            if txt is None:
                res['nbs_error'] += 1
                continue
            rows = parse_nbs_csv(txt)
            write_gz(p, rows)
            res['nbs'] += 1
            print(json.dumps({'nbs': st, 'chunk': a, 'rows': len(rows), **http.stats()}), flush=True)
    # 3. METAR temperatures (routine + specials) for Polymarket's stations
    for city, v in PM_CITIES.items():
        p = raw / 'asos' / ('%s.json.gz' % v['asos'])
        if p.exists():
            continue
        a = dt.date.fromisoformat(args.asos_start)
        b = dt.date.fromisoformat(args.nbs_end)
        q = [('station', v['asos']), ('data', 'tmpf'), ('year1', a.year), ('month1', a.month), ('day1', a.day),
             ('year2', b.year), ('month2', b.month), ('day2', b.day), ('tz', 'Etc/UTC'), ('format', 'onlycomma'),
             ('latlon', 'no'), ('missing', 'M'), ('trace', 'T'), ('direct', 'no'), ('report_type', '3'),
             ('report_type', '4')]
        txt = http.get(IEM + '/cgi-bin/request/asos.py?' + urllib.parse.urlencode(q))
        if txt is None:
            res['asos_error'] += 1
            continue
        rows = []
        for r in csv.DictReader(io.StringIO(txt)):
            tf = fnum(r.get('tmpf'))
            ts = parse_ts((r.get('valid') or '').replace(' ', 'T') + 'Z')
            if tf is not None and ts is not None:
                rows.append([int(ts), tf])
        write_gz(p, rows)
        res['asos'] += 1
        print(json.dumps({'asos': v['asos'], 'rows': len(rows), **http.stats()}), flush=True)
    update_manifest(out, 'wx', {'fetched_at': utc_iso(t0), 'finished_at': utc_iso(), 'results': dict(res),
                                'http': http.stats(), 'stations_kalshi': k_stations, 'stations_polymarket': p_stations,
                                'nbs_window': [args.nbs_start, args.nbs_end], 'asos_start': args.asos_start,
                                'sources': [IEM + '/json/cli.py', IEM + '/cgi-bin/request/mos.py (model=NBS)',
                                            IEM + '/cgi-bin/request/asos.py']})
    print(json.dumps({'results': dict(res), **http.stats(), 'seconds': round(time.time() - t0)}), flush=True)
    return 0


# ------------------------------------------------------------------------------------------------ polymarket collect

PM_UNIVERSE = ROOT / 'research' / '2026-10-09' / 'polymarket_history' / 'raw' / 'universe.json.gz'
MONTH_NAMES = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
               'november', 'december']


def pm_bucket(label):
    """Polymarket bucket label -> inclusive whole-degree range (lo, hi); None for an unparseable label.
    '76-77°F' -> (76, 77); '75°F or below' -> (None, 75); '86°F or higher' -> (86, None); '18°C' -> (18, 18)."""
    s = (label or '').replace('º', '°').strip()
    m = re.match(r'^(-?\d+)\s*-\s*(-?\d+)\s*°?\s*[FC]?$', s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r'^(-?\d+)\s*°?\s*[FC]?\s+or\s+(below|lower|less)$', s, re.I)
    if m:
        return None, int(m.group(1))
    m = re.match(r'^(-?\d+)\s*°?\s*[FC]?\s+or\s+(higher|above|more)$', s, re.I)
    if m:
        return int(m.group(1)), None
    m = re.match(r'^(-?\d+)\s*°?\s*[FC]?$', s)
    if m:
        return int(m.group(1)), int(m.group(1))
    return None


def pm_city_events(cities, lo, hi):
    """Event slugs per (city, date) from the stored resolved universe, plus constructed slugs for later days."""
    uni = read_gz(PM_UNIVERSE)
    found = {}
    for m in uni:
        t = m.get('event_title') or ''
        if not t.startswith('Highest temperature in '):
            continue
        city = t[len('Highest temperature in '):].split(' on ')[0]
        if city not in cities:
            continue
        d = (m.get('endDate') or '')[:10]
        if lo <= d <= hi:
            found[(city, d)] = m.get('event_slug')
    del uni
    d = dt.date.fromisoformat(lo)
    while d.isoformat() <= hi:
        for city in cities:
            if (city, d.isoformat()) not in found:
                found[(city, d.isoformat())] = 'highest-temperature-in-%s-on-%s-%d-%d' % (
                    city.lower().replace(' ', '-'), MONTH_NAMES[d.month - 1], d.day, d.year)
        d += dt.timedelta(days=1)
    return found


PM_KEEP = ['id', 'conditionId', 'question', 'groupItemTitle', 'endDate', 'closedTime', 'umaResolutionStatus',
           'volumeNum', 'feesEnabled', 'feeType', 'feeSchedule', 'outcomes', 'outcomePrices', 'clobTokenIds',
           'orderPriceMinTickSize', 'acceptingOrdersTimestamp', 'createdAt', 'negRisk']


def cmd_pm(args):
    out = Path(args.out)
    raw = out / 'raw' / 'pm'
    http = Http(interval=args.interval)
    t0 = time.time()
    cities = args.cities.split(',')
    lo, hi = args.start or MARKET_START, args.end or MARKET_END
    slugs = pm_city_events(cities, lo, hi)
    res = collections.Counter()
    events = {}
    for (city, d), slug in sorted(slugs.items(), key=lambda kv: (cities.index(kv[0][0]), kv[0][1])):
        p = raw / 'events' / city / ('%s.json.gz' % d)
        if p.exists():
            events[(city, d)] = read_gz(p)
            continue
        js = http.request(GAMMA + '/events?' + urllib.parse.urlencode({'slug': slug}))
        if isinstance(js, dict) and '__error__' in js:
            res['event_error'] += 1
            continue
        if not js:
            res['event_missing'] += 1
            write_gz(p, {'slug': slug, 'missing': True})
            continue
        e = js[0]
        rec = {'id': e.get('id'), 'slug': e.get('slug'), 'title': e.get('title'), 'endDate': e.get('endDate'),
               'negRisk': e.get('negRisk'), 'tags': [t.get('label') for t in e.get('tags') or [] if isinstance(t, dict)],
               'markets': [{k: mm.get(k) for k in PM_KEEP} for mm in e.get('markets') or []]}
        write_gz(p, rec)
        events[(city, d)] = rec
        res['event'] += 1
    print(json.dumps({'events': len(events), **res, **http.stats()}), flush=True)
    # prices: the YES token's hourly midpoint from 13:00 local the day before to 01:00 local the day after
    jobs = []
    for (city, d), e in events.items():
        if e.get('missing'):
            continue
        tz = PM_CITIES[city]['tz']
        a, b = local_ts(d, -1, 13, tz), local_ts(d, 1, 1, tz)
        for mm in e['markets']:
            toks = mm.get('clobTokenIds')
            toks = json.loads(toks) if isinstance(toks, str) else toks
            if not toks:
                continue
            p = raw / 'prices' / city / ('%s.json.gz' % mm['id'])
            if not p.exists():
                jobs.append((p, toks[0], int(a), int(b)))
    print(json.dumps({'price_jobs': len(jobs)}), flush=True)
    done = [0]
    lock = threading.Lock()

    def one(job):
        p, tok, a, b = job
        d = http.request(CLOB + '/prices-history?' + urllib.parse.urlencode(
            {'market': tok, 'startTs': a, 'endTs': b, 'fidelity': 60}))
        if '__error__' in d:
            return 'error'
        write_gz(p, [[int(x['t']), float(x['p'])] for x in d.get('history') or []])
        with lock:
            done[0] += 1
            if done[0] % 500 == 0:
                print(json.dumps({'prices_done': done[0], 'elapsed_s': round(time.time() - t0), **http.stats()}),
                      flush=True)
        return 'ok'

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(one, jobs):
            res['prices_' + r] += 1
    man = json.loads((out / 'manifest.json').read_text()).get('pm', {}) if (out / 'manifest.json').exists() else {}
    man[','.join(cities)] = {'fetched_at': utc_iso(t0), 'finished_at': utc_iso(), 'window': [lo, hi],
                             'results': dict(res), 'http': http.stats(),
                             'sources': [GAMMA + '/events?slug=', CLOB + '/prices-history (fidelity 60)']}
    update_manifest(out, 'pm', man)
    print(json.dumps({'results': dict(res), **http.stats(), 'seconds': round(time.time() - t0)}), flush=True)
    return 0


# ------------------------------------------------------------------------------------------------ live books

PBANDS = [0.0, 0.05, 0.15, 0.35, 0.65, 0.85, 0.95, 1.0001]


def pband(p):
    for a, b in zip(PBANDS[:-1], PBANDS[1:]):
        if a <= p < b:
            return '%.2f-%.2f' % (a, min(b, 1.0))
    return None


def cmd_books(args):
    """One read of today's and tomorrow's ladders on both venues: the half-spread by price band (the cost a taker pays
    over the midpoint) and the size at the touch (the capacity a taker can take at that cost)."""
    out = Path(args.out)
    raw = out / 'raw' / 'books'
    raw.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    kh, ph = Http(interval=0.3), Http(interval=0.3)
    snap = {'at': utc_iso(t0), 'kalshi': [], 'polymarket': []}
    for s in KALSHI_SERIES:
        d = kh.request(KALSHI + '/markets?' + urllib.parse.urlencode({'series_ticker': s, 'status': 'open',
                                                                     'limit': 100}))
        for m in (d.get('markets') or []) if '__error__' not in d else []:
            ob = kh.request(KALSHI + '/markets/%s/orderbook' % m['ticker'])
            if '__error__' in ob:
                continue
            o = ob.get('orderbook_fp') or ob.get('orderbook') or {}
            yes = [(float(p), float(q)) for p, q in (o.get('yes_dollars') or [])]
            no = [(float(p), float(q)) for p, q in (o.get('no_dollars') or [])]
            snap['kalshi'].append({'series': s, 'ticker': m['ticker'], 'event': m.get('event_ticker'),
                                   'close_time': m.get('close_time'), 'yes_bids': yes, 'no_bids': no,
                                   'volume': fnum(m.get('volume_fp')), 'strike_type': m.get('strike_type')})
    today = dt.datetime.now(UTC).date()
    tokens = []
    for city in args.pm_cities.split(','):
        for k in (0, 1):
            d = today + dt.timedelta(days=k)
            slug = 'highest-temperature-in-%s-on-%s-%d-%d' % (city.lower().replace(' ', '-'),
                                                              MONTH_NAMES[d.month - 1], d.day, d.year)
            js = ph.request(GAMMA + '/events?' + urllib.parse.urlencode({'slug': slug}))
            if not js or (isinstance(js, dict) and '__error__' in js):
                continue
            for mm in js[0].get('markets') or []:
                toks = mm.get('clobTokenIds')
                toks = json.loads(toks) if isinstance(toks, str) else toks
                if toks and not mm.get('closed'):
                    tokens.append({'city': city, 'date': d.isoformat(), 'label': mm.get('groupItemTitle'),
                                   'token': toks[0], 'volume': fnum(mm.get('volumeNum')),
                                   'tick': fnum(mm.get('orderPriceMinTickSize'))})
    for i in range(0, len(tokens), 100):
        chunk = tokens[i:i + 100]
        books = ph.request(CLOB + '/books', body=[{'token_id': t['token']} for t in chunk])
        if isinstance(books, dict) and '__error__' in books:
            continue
        by = {b.get('asset_id'): b for b in books or []}
        for t in chunk:
            b = by.get(t['token']) or {}
            t['bids'] = sorted([(float(x['price']), float(x['size'])) for x in b.get('bids') or []], reverse=True)
            t['asks'] = sorted([(float(x['price']), float(x['size'])) for x in b.get('asks') or []])
            snap['polymarket'].append(t)
    p = raw / ('books_%s.json.gz' % dt.datetime.fromtimestamp(t0, UTC).strftime('%Y%m%dT%H%M'))
    write_gz(p, snap)
    man = json.loads((out / 'manifest.json').read_text()).get('books', []) if (out / 'manifest.json').exists() else []
    man.append({'at': snap['at'], 'file': str(p.relative_to(out)), 'kalshi_books': len(snap['kalshi']),
                'polymarket_books': len(snap['polymarket']), 'http_kalshi': kh.stats(), 'http_polymarket': ph.stats()})
    update_manifest(out, 'books', man)
    print(json.dumps(man[-1]))
    return 0


# ------------------------------------------------------------------------------------------------ analysis: truth

def load_cli(out, station):
    res = {}
    for p in sorted((Path(out) / 'raw' / 'wx' / 'cli').glob('%s_*.json' % station)):
        for r in json.loads(p.read_text()).get('results') or []:
            h = r.get('high')
            res[r['valid']] = h if isinstance(h, (int, float)) else None
    return res


def routine_minute(rows):
    """The minute past the hour at which a station files its routine METAR (the modal minute)."""
    c = collections.Counter(dt.datetime.fromtimestamp(ts, UTC).minute for ts, _ in rows)
    return c.most_common(1)[0][0] if c else None


def f_to_wholec_f(tf):
    """A METAR's body temperature is whole degrees C; its tenths-of-C remark is what IEM's tmpf carries. This is the
    Fahrenheit value a reader of the body group alone would see."""
    c = (tf - 32.0) * 5.0 / 9.0
    return math.floor(c + 0.5) * 9.0 / 5.0 + 32.0


def round_half_up(x):
    return int(math.floor(x + 0.5 + 1e-9))


def metar_daily_max(rows, tz, minute=None, wholec=False):
    """Local-calendar-day max of METAR temperatures, rounded to whole F; `minute` keeps only routine reports."""
    z = ZoneInfo(tz)
    best = {}
    for ts, tf in rows:
        d = dt.datetime.fromtimestamp(ts, z)
        if minute is not None and dt.datetime.fromtimestamp(ts, UTC).minute != minute:
            continue
        v = f_to_wholec_f(tf) if wholec else tf
        k = d.date().isoformat()
        if k not in best or v > best[k]:
            best[k] = v
    return {k: round_half_up(v) for k, v in best.items()}


# ------------------------------------------------------------------------------------------------ analysis: forecast

def load_nbs_max(out, station):
    """Target local date -> sorted [(runtime, txn, xnd)]: the NBM's 12-hour max ending 00 UTC the next day."""
    seen = {}
    for p in sorted((Path(out) / 'raw' / 'wx' / 'nbs' / station).glob('*.json.gz')):
        for rt, ft, txn, xnd, tmp in read_gz(p):
            if txn is None:
                continue
            f = dt.datetime.fromtimestamp(ft, UTC)
            if f.hour != 0:
                continue
            seen[(rt, ft)] = (txn, xnd)
    by_day = collections.defaultdict(list)
    for (rt, ft), (txn, xnd) in seen.items():
        d = (dt.datetime.fromtimestamp(ft, UTC) - dt.timedelta(days=1)).date().isoformat()
        by_day[d].append((rt, txn, xnd))
    for d in by_day:
        by_day[d].sort()
    return by_day


def forecast_at(runs, T, lag_h=NBM_LAG_H, max_age_h=30.0):
    """The latest run usable at decision time T (cycle time + lag <= T), if it is not older than max_age_h."""
    best = None
    for rt, txn, xnd in runs or []:
        if rt + lag_h * HOUR <= T and rt >= T - max_age_h * HOUR:
            best = (rt, txn, xnd)
    return best


def doy(date_str):
    return dt.date.fromisoformat(date_str).timetuple().tm_yday


def circ_dist(a, b, n=366):
    d = abs(a - b) % n
    return min(d, n - d)


def fit_error_model(pairs, window=45, seasonal_var=True):
    """pairs: [(doy, resid, xnd)] from the training year. Seasonal bias = mean residual within +-window days of the
    day of year; variance = a + c * xnd^2 by least squares on the de-biased squared residuals (a >= 0.25, c >= 0),
    times (seasonal_var) a day-of-year scale: the window's mean squared error over the window's mean model variance."""
    if len(pairs) < 60:
        return None
    overall = statistics.fmean(r for _, r, _ in pairs)
    bias = {}
    for d in range(1, 367):
        near = [r for dd, r, _ in pairs if circ_dist(d, dd) <= window]
        bias[d] = statistics.fmean(near) if len(near) >= 20 else overall
    xs, ys = [], []
    med_x = statistics.median(x for _, _, x in pairs if x is not None) if any(x is not None for _, _, x in pairs) \
        else 2.0
    for dd, r, x in pairs:
        x = med_x if x is None else x
        xs.append(x * x)
        ys.append((r - bias[dd]) ** 2)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    c = (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx) if sxx > 0 else 0.0
    c = max(0.0, c)
    a = max(0.25, my - c * mx)
    scale = {d: 1.0 for d in range(1, 367)}
    if seasonal_var:
        for d in range(1, 367):
            num, den, k = 0.0, 0.0, 0
            for dd, r, x in pairs:
                if circ_dist(d, dd) <= window:
                    x = med_x if x is None else x
                    num += (r - bias[dd]) ** 2
                    den += a + c * x * x
                    k += 1
            if k >= 20 and den > 0:
                scale[d] = num / den
    # The error shape: forecast errors are fat-tailed and skewed (a front that leaves the day's high at midnight), so
    # the standardised training residuals are kept and smoothed; the form (normal or empirical) is chosen by the
    # training year's leave-one-out log score of the observed integer, never by the market window.
    zs = []
    for dd, r, x in pairs:
        x = med_x if x is None else x
        zs.append((r - bias[dd]) / math.sqrt(scale[dd] * (a + c * x * x)))
    h = 1.06 * statistics.pstdev(zs) * len(zs) ** -0.2
    ll_norm = ll_emp = 0.0
    for i, (dd, r, x) in enumerate(pairs):
        x = med_x if x is None else x
        sd = math.sqrt(scale[dd] * (a + c * x * x))
        lo_, hi_ = (r - 0.5 - bias[dd]) / sd, (r + 0.5 - bias[dd]) / sd
        ll_norm += math.log(max(1e-6, norm_cdf(hi_) - norm_cdf(lo_)))
        rest = zs[:i] + zs[i + 1:]
        pe = sum(norm_cdf((hi_ - z) / h) - norm_cdf((lo_ - z) / h) for z in rest) / len(rest)
        ll_emp += math.log(max(1e-6, pe))
    form = 'empirical' if ll_emp > ll_norm else 'normal'
    return {'bias': bias, 'a': a, 'c': c, 'scale': scale, 'seasonal_var': seasonal_var, 'med_xnd': med_x,
            'n': len(pairs), 'overall_bias': overall, 'scale_range': [min(scale.values()), max(scale.values())],
            'resid_sd': statistics.pstdev([r for _, r, _ in pairs]), 'zs': sorted(zs), 'h': h, 'form': form,
            'loo_log_normal': ll_norm / len(pairs), 'loo_log_empirical': ll_emp / len(pairs),
            'z_skew': B.moments(zs)[0], 'z_kurtosis': B.moments(zs)[1]}


def model_cdf(model):
    if model.get('form') == 'empirical':
        if '_cdf' not in model:
            model['_cdf'] = kernel_cdf(model['zs'], model['h'])
        return model['_cdf']
    return norm_cdf


def predictive(model, date_str, txn, xnd):
    x = model['med_xnd'] if xnd is None else xnd
    d = doy(date_str)
    return txn + model['bias'][d], math.sqrt(model.get('scale', {}).get(d, 1.0) * (model['a'] + model['c'] * x * x))


def pit_value(obs, mu, sd, u, cdf=None):
    """Randomised PIT for an integer observation: uniform within the probability mass of the observed integer."""
    cdf = cdf or norm_cdf
    lo = cdf((obs - 0.5 - mu) / sd)
    hi = cdf((obs + 0.5 - mu) / sd)
    return lo + u * (hi - lo)


# ------------------------------------------------------------------------------------------------ analysis: events

def candle_at(candles, T, max_stale=2 * HOUR):
    """The candle closing at or before T (Kalshi stamps a candle with the end of its hour)."""
    ts = [c['t'] for c in candles]
    i = bisect.bisect_right(ts, T) - 1
    if i < 0 or T - ts[i] > max_stale:
        return None
    return candles[i]


def price_at(series, T, grace=120, max_stale=3 * HOUR):
    """Polymarket hourly midpoint at T: its points land within a minute after the hour, so the point stamped up to
    `grace` seconds after T is the price at T."""
    ts = [x[0] for x in series]
    i = bisect.bisect_right(ts, T + grace) - 1
    if i < 0 or T + grace - ts[i] > max_stale:
        return None
    return series[i][1]


def load_kalshi_events(out):
    evs = []
    for s, meta in KALSHI_SERIES.items():
        mp = Path(out) / 'raw' / 'kalshi' / ('markets_%s.json.gz' % s)
        if not mp.exists():
            continue
        by = collections.defaultdict(list)
        for m in read_gz(mp):
            if m['date'] and MARKET_START <= m['date'] <= MARKET_END:
                by[m['event_ticker']].append(m)
        for ev, ms in by.items():
            buckets = []
            for m in ms:
                cp = Path(out) / 'raw' / 'kalshi' / 'candles' / s / ('%s.json.gz' % m['ticker'])
                if not cp.exists():
                    buckets = None
                    break
                lo, hi = bucket_bounds(m['strike_type'], m['floor_strike'], m['cap_strike'])
                cs = sorted(read_gz(cp), key=lambda c: c['t'])
                buckets.append({'id': m['ticker'], 'lo': lo, 'hi': hi,
                                'type': 'interior' if m['strike_type'] == 'between' else 'tail',
                                'result': 1 if m['result'] == 'yes' else 0 if m['result'] == 'no' else None,
                                'candles': cs, 'settle_ts': parse_ts(m.get('settlement_ts')),
                                'exp_value': fnum(m.get('expiration_value')), 'rules': m.get('rules_primary')})
            if not buckets:
                continue
            evs.append({'venue': 'kalshi', 'key': s, 'station': meta['station'], 'tz': meta['tz'],
                        'date': ms[0]['date'], 'event': ev, 'buckets': buckets})
    return evs


def load_pm_events(out, cities):
    evs = []
    for city in cities:
        meta = PM_CITIES[city]
        for p in sorted((Path(out) / 'raw' / 'pm' / 'events' / city).glob('*.json.gz')):
            e = read_gz(p)
            if e.get('missing'):
                continue
            d = p.name[:10]
            buckets = []
            for mm in e['markets']:
                pp = Path(out) / 'raw' / 'pm' / 'prices' / city / ('%s.json.gz' % mm['id'])
                b = pm_bucket(mm.get('groupItemTitle'))
                if b is None or not pp.exists():
                    buckets = None
                    break
                op = mm.get('outcomePrices')
                op = json.loads(op) if isinstance(op, str) else op
                res = None
                if op and len(op) == 2:
                    y = fnum(op[0])
                    res = 1 if y is not None and y > 0.99 else 0 if y is not None and y < 0.01 else None
                fs = mm.get('feeSchedule') or {}
                # the market's own schedule (weather: rate 0.05, taker only, read 2026-10-14); the category schedule
                # (polymarket_history.fee_rate) when a market carries none
                tags = e.get('tags') or ['Weather']
                default_rate = fee_rate(categorize(tags, e.get('title')), tags)
                buckets.append({'id': mm['id'], 'lo': b[0], 'hi': b[1],
                                'type': 'interior' if (b[0] is not None and b[1] is not None) else 'tail',
                                'result': res, 'prices': sorted(read_gz(pp)),
                                'settle_ts': parse_ts(mm.get('closedTime')), 'volume': fnum(mm.get('volumeNum'), 0.0),
                                # the current schedule is charged to every trade, including 2025 markets that
                                # charged none (the question is what the rule earns from here)
                                'fee_rate': fnum(fs.get('rate'), default_rate) or default_rate,
                                'label': mm.get('groupItemTitle')})
            if not buckets:
                continue
            evs.append({'venue': 'polymarket', 'key': city, 'station': meta['station'], 'tz': meta['tz'],
                        'date': d, 'event': e.get('slug'), 'buckets': buckets})
    return evs


def load_pm_winners(out, cities):
    """Every listed Polymarket event's settled bucket (from the outcome prices), without needing price files."""
    rows = []
    for city in cities:
        meta = PM_CITIES[city]
        for p in sorted((Path(out) / 'raw' / 'pm' / 'events' / city).glob('*.json.gz')):
            e = read_gz(p)
            if e.get('missing'):
                continue
            wins = []
            for mm in e['markets']:
                op = mm.get('outcomePrices')
                op = json.loads(op) if isinstance(op, str) else op
                if op and fnum(op[0], 0.0) > 0.99:
                    wins.append(pm_bucket(mm.get('groupItemTitle')))
            w = wins[0] if len(wins) == 1 and wins[0] is not None else None
            rows.append({'key': city, 'station': meta['station'], 'date': p.name[:10],
                         'winner': None if w is None else {'lo': w[0], 'hi': w[1]}})
    return rows


def winner(ev):
    w = [b for b in ev['buckets'] if b['result'] == 1]
    return w[0] if len(w) == 1 else None


# ------------------------------------------------------------------------------------------------ analysis: costs

def half_spread_table(out):
    """Polymarket weather half-spread by price band from the live snapshots: median (ask - bid) / 2 over books with
    both sides, plus the median size at the touch in dollars; Kalshi touch size by band likewise."""
    pm_hs, pm_depth, k_depth, k_hs = (collections.defaultdict(list) for _ in range(4))
    files = sorted((Path(out) / 'raw' / 'books').glob('books_*.json.gz'))
    for f in files:
        s = read_gz(f)
        for t in s['polymarket']:
            if not t.get('bids') or not t.get('asks'):
                continue
            bb, ba = t['bids'][0][0], t['asks'][0][0]
            if ba <= bb:
                continue
            mid = (bb + ba) / 2.0
            band = pband(mid)
            pm_hs[band].append((ba - bb) / 2.0)
            pm_depth[band].append(ba * t['asks'][0][1])
        for b in s['kalshi']:
            yb = b['yes_bids'][-1] if b['yes_bids'] else None
            nb = b['no_bids'][-1] if b['no_bids'] else None
            if yb and nb:
                ask = round(1.0 - nb[0], 4)
                if ask > yb[0]:
                    mid = (ask + yb[0]) / 2.0
                    k_hs[pband(mid)].append((ask - yb[0]) / 2.0)
                    k_depth[pband(ask)].append(nb[1])          # contracts at the YES ask
                    k_depth[pband(1.0 - yb[0])].append(yb[1])  # contracts at the NO ask
    def summ(d, f=statistics.median):
        return {k: {'n': len(v), 'median': f(v), 'p25': sorted(v)[int(0.25 * (len(v) - 1))]} for k, v in d.items()
                if v}
    return {'files': [f.name for f in files], 'pm_half_spread': summ(pm_hs), 'pm_touch_usd': summ(pm_depth),
            'kalshi_half_spread': summ(k_hs), 'kalshi_touch_contracts': summ(k_depth)}


def pm_hs_for(table, p, default=0.01):
    r = table['pm_half_spread'].get(pband(p))
    return r['median'] if r and r['n'] >= 5 else default


# ------------------------------------------------------------------------------------------------ analysis: rows

def decision_rows(evs, models, nbs, truth):
    """For each event, decision time and bucket: the model probability, the executable prices then and an hour later,
    and what the bucket paid. Rows without a usable forecast or price are dropped (counted)."""
    rows, drops = [], collections.Counter()
    for ev in evs:
        w = winner(ev)
        if w is None:
            drops['no_single_winner'] += 1
            continue
        for dec, (off, hour) in DECISIONS.items():
            T = local_ts(ev['date'], off, hour, ev['tz'])
            model = models.get((ev['station'], dec))
            fc = forecast_at(nbs.get(ev['station'], {}).get(ev['date']), T)
            if model is None or fc is None:
                drops['no_forecast_' + dec] += 1
                continue
            mu, sd = predictive(model, ev['date'], fc[1], fc[2])
            obs = truth.get(ev['station'], {}).get(ev['date'])
            for b in ev['buckets']:
                p = bucket_prob(b['lo'], b['hi'], mu, sd, model_cdf(model))
                r = {'venue': ev['venue'], 'key': ev['key'], 'date': ev['date'], 'dec': dec, 'T': T, 'id': b['id'],
                     'type': b['type'], 'lo': b['lo'], 'hi': b['hi'], 'p': p, 'mu': mu, 'sd': sd, 'txn': fc[1],
                     'run': fc[0], 'result': b['result'], 'obs': obs, 'hold_days': None}
                if b.get('settle_ts'):
                    r['hold_days'] = max(0.25, (b['settle_ts'] - T) / DAY)
                if ev['venue'] == 'kalshi':
                    c, c1 = candle_at(b['candles'], T), candle_at(b['candles'], T + HOUR)
                    if c is None:
                        drops['no_candle'] += 1
                        continue
                    r['ask'] = c['ask'] if c['ask'] is not None and 0 < c['ask'] < 1 else None
                    r['bid'] = c['bid'] if c['bid'] is not None and 0 < c['bid'] < 1 else None
                    r['ask1'] = (c1['ask'] if c1 and c1['ask'] is not None and 0 < c1['ask'] < 1 else None)
                    r['bid1'] = (c1['bid'] if c1 and c1['bid'] is not None and 0 < c1['bid'] < 1 else None)
                    later = [x for x in b['candles'] if T < x['t'] <= T + 6 * HOUR]
                    r['later_ask_low'] = [x['ask_low'] for x in later]
                    r['later_bid_high'] = [x['bid_high'] for x in later]
                    later1 = [x for x in b['candles'] if T + HOUR < x['t'] <= T + 7 * HOUR]
                    r['later_ask_low1'] = [x['ask_low'] for x in later1]
                    r['later_bid_high1'] = [x['bid_high'] for x in later1]
                    r['vol2h'] = sum(x['vol'] for x in b['candles'] if T - HOUR < x['t'] <= T + HOUR)
                    r['mid'] = (r['ask'] + r['bid']) / 2.0 if r['ask'] is not None and r['bid'] is not None else None
                else:
                    m0, m1 = price_at(b['prices'], T), price_at(b['prices'], T + HOUR)
                    if m0 is None:
                        drops['no_price'] += 1
                        continue
                    r['mid'], r['mid1'] = m0, m1
                    r['fee_rate'] = b['fee_rate']
                    r['volume'] = b['volume']
                    r['later_mids'] = [x[1] for x in b['prices'] if T + 120 < x[0] <= T + 6 * HOUR + 120]
                    r['later_mids1'] = [x[1] for x in b['prices'] if T + HOUR + 120 < x[0] <= T + 7 * HOUR + 120]
                rows.append(r)
    return rows, dict(drops)


# ------------------------------------------------------------------------------------------------ analysis: trading

def floor_cent(x):
    return math.floor(x * 100.0 + 1e-9) / 100.0


def trades_for(rows, variant, hs_table=None, late=False):
    """The trades a variant takes. variant = (venue, dec, thr, exec, btype). Each trade is one contract/share:
    {'date', 'cost', 'payout', 'side', 'id', 'p', 'hold_days', 'price'}. `late` prices the same decision an hour
    later (the trade happens only if the later price still clears the threshold)."""
    venue, dec, thr, execu, btype = variant
    out = []
    for r in rows:
        if r['venue'] != venue or r['dec'] != dec or r['result'] is None:
            continue
        if btype != 'all' and r['type'] != btype:
            continue
        p = r['p']
        cands = []
        if venue == 'kalshi':
            ask, bid = (r['ask1'], r['bid1']) if late else (r['ask'], r['bid'])
            if execu == 'taker':
                if ask is not None:
                    cands.append(('yes', ask, kalshi_taker_cost(ask), p))
                if bid is not None:
                    cands.append(('no', 1.0 - bid, kalshi_taker_cost(1.0 - bid), 1.0 - p))
            else:
                # resting bids priced to clear the threshold, never crossing the touch, filled only on a trade-through
                # within six hours of posting (Kalshi weather series charge makers nothing: fee_type 'quadratic')
                lows = r['later_ask_low1'] if late else r['later_ask_low']
                highs = r['later_bid_high1'] if late else r['later_bid_high']
                if ask is not None or bid is not None:
                    lim = floor_cent(p - thr)
                    if ask is not None:
                        lim = min(lim, round(ask - 0.01, 2))
                    if lim >= 0.01 and maker_filled(lim, lows):
                        cands.append(('yes', lim, lim, p))
                    lim_no = floor_cent((1.0 - p) - thr)
                    if bid is not None:
                        lim_no = min(lim_no, round(1.0 - bid - 0.01, 2))
                    no_asks = [None if x is None else 1.0 - x for x in highs]
                    if lim_no >= 0.01 and maker_filled(lim_no, no_asks):
                        cands.append(('no', lim_no, lim_no, 1.0 - p))
        else:
            mid = r['mid1'] if late else r['mid']
            if mid is None:
                continue
            hs = pm_hs_for(hs_table, mid)
            ya = min(0.999, mid + hs)
            na = min(0.999, (1.0 - mid) + hs)
            if execu == 'taker':
                if 0.0 < ya < 1.0:
                    cands.append(('yes', ya, pm_taker_cost(ya, r['fee_rate']), p))
                if 0.0 < na < 1.0:
                    cands.append(('no', na, pm_taker_cost(na, r['fee_rate']), 1.0 - p))
            else:
                # resting bids (makers pay no fee) a cent below the ask proxy; filled only if a later hourly ask proxy
                # (midpoint + the band's half-spread) prints below the limit within six hours. Hourly midpoints miss
                # intra-hour dips, so this undercounts fills.
                mids = r['later_mids1'] if late else r['later_mids']
                lim = min(floor_cent(p - thr), round(ya - 0.01, 3))
                if lim >= 0.01 and maker_filled(lim, [m + pm_hs_for(hs_table, m) for m in mids]):
                    cands.append(('yes', lim, lim, p))
                lim_no = min(floor_cent((1.0 - p) - thr), round(na - 0.01, 3))
                if lim_no >= 0.01 and maker_filled(lim_no, [(1.0 - m) + pm_hs_for(hs_table, m) for m in mids]):
                    cands.append(('no', lim_no, lim_no, 1.0 - p))
        for side, price, cost, q in cands:
            if execu == 'taker' and q - cost < thr:
                continue
            payout = r['result'] if side == 'yes' else 1 - r['result']
            out.append({'date': r['date'], 'key': r['key'], 'id': r['id'], 'side': side, 'price': price, 'cost': cost,
                        'payout': payout, 'p': q, 'edge': q - cost, 'hold_days': r['hold_days'] or 1.5,
                        'type': r['type'], 'vol2h': r.get('vol2h'), 'volume': r.get('volume'), 'T': r['T']})
    return out


def daily_series(trades, days):
    """Per market day: profit over capital staked that day (0 on days without a trade)."""
    pnl, cap = collections.defaultdict(float), collections.defaultdict(float)
    for t in trades:
        pnl[t['date']] += t['payout'] - t['cost']
        cap[t['date']] += t['cost']
    return [(pnl[d] / cap[d]) if cap[d] > 0 else 0.0 for d in days]


def daily_pnl_series(trades, days, cutoff=CUTOFF):
    """Per market day: profit over a constant capital base, the variant's mean daily stake on the in-sample days
    (one contract per trade). Unlike `daily_series` it weights each dollar, not each day, so its mean has the sign
    of the pooled profit; Sharpe and t are unchanged by the choice of the constant."""
    pnl, cap = collections.defaultdict(float), collections.defaultdict(float)
    for t in trades:
        pnl[t['date']] += t['payout'] - t['cost']
        cap[t['date']] += t['cost']
    is_days = [d for d in days if d < cutoff] or days
    base = sum(cap[d] for d in is_days) / len(is_days)
    if base <= 0:
        base = (sum(cap.values()) / len(days)) if days and sum(cap.values()) > 0 else 1.0
    return [pnl[d] / base for d in days]


def summarize_trades(trades):
    if not trades:
        return {'n': 0}
    cost = sum(t['cost'] for t in trades)
    pnl = sum(t['payout'] - t['cost'] for t in trades)
    capdays = sum(t['cost'] * t['hold_days'] for t in trades)
    return {'n': len(trades), 'win_rate': sum(t['payout'] for t in trades) / len(trades),
            'mean_price': statistics.fmean(t['price'] for t in trades), 'mean_model_p': statistics.fmean(
                t['p'] for t in trades), 'return_per_dollar': pnl / cost, 'pnl_per_contract': pnl / len(trades),
            'ann_return_on_capital': pnl / capdays * 365.0 if capdays > 0 else None,
            'ann_excess_over_ssr': (pnl / capdays * 365.0 - SSR) if capdays > 0 else None,
            'yes_share': sum(1 for t in trades if t['side'] == 'yes') / len(trades)}


def market_days(lo=MARKET_START, hi=MARKET_END):
    d, e, out = dt.date.fromisoformat(lo), dt.date.fromisoformat(hi), []
    while d <= e:
        out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


# ------------------------------------------------------------------------------------------------ analysis: command

PROB_BINS = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 1.0001]


def reliability(pairs):
    """pairs: [(prob, outcome)] -> per bin: n, mean prob, observed frequency."""
    out = []
    for a, b in zip(PROB_BINS[:-1], PROB_BINS[1:]):
        v = [(p, y) for p, y in pairs if a <= p < b]
        if v:
            out.append({'bin': '%.2f-%.2f' % (a, min(b, 1.0)), 'n': len(v), 'mean_p': statistics.fmean(p for p, _ in v),
                        'freq': statistics.fmean(y for _, y in v)})
    return out


def scores(pairs):
    if not pairs:
        return {'n': 0}
    brier = statistics.fmean((p - y) ** 2 for p, y in pairs)
    logs = statistics.fmean(-math.log(max(1e-4, p) if y else max(1e-4, 1.0 - p)) for p, y in pairs)
    return {'n': len(pairs), 'brier': brier, 'log': logs}


def implied_mean_diag(rows):
    """Per ladder and decision: the market's implied expected high (normalised mids over bucket centres; a tail
    counts as one degree beyond its edge) against the model mean and the settled value. If the crowd prices the
    calendar-day high that forecasts and apps quote while Polymarket settles on METAR readings (which run 0-2F
    lower), the market's implied mean sits above the settled value."""
    groups = collections.defaultdict(list)
    for r in rows:
        if r.get('mid') is not None and r.get('obs') is not None:
            groups[(r['venue'], r['key'], r['date'], r['dec'])].append(r)
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for (venue, key, date, dec), rr in groups.items():
        tot = sum(r['mid'] for r in rr)
        if tot <= 0:
            continue
        imp = 0.0
        for r in rr:
            t = ((r['lo'] + r['hi']) / 2.0 if r['lo'] is not None and r['hi'] is not None
                 else (r['hi'] - 1.0) if r['lo'] is None else (r['lo'] + 1.0))
            imp += r['mid'] / tot * t
        obs, mu = rr[0]['obs'], rr[0]['mu']
        for k in ('%s|%s' % (venue, dec), '%s|%s|%s' % (venue, dec, key)):
            acc[k]['mkt_err'].append(imp - obs)
            acc[k]['model_err'].append(mu - obs)
            acc[k]['mkt_minus_model'].append(imp - mu)
    out = {}
    for k, v in acc.items():
        out[k] = {'n': len(v['mkt_err']), 'market_bias': statistics.fmean(v['mkt_err']),
                  'market_mae': statistics.fmean(abs(x) for x in v['mkt_err']),
                  'model_bias': statistics.fmean(v['model_err']),
                  'model_mae': statistics.fmean(abs(x) for x in v['model_err']),
                  'market_minus_model_mean': statistics.fmean(v['mkt_minus_model'])}
    return out


def pit_summary(vals):
    if not vals:
        return {'n': 0}
    dec = [0] * 10
    for u in vals:
        dec[min(9, int(u * 10))] += 1
    n = len(vals)
    cov = {}
    for c in (0.5, 0.8, 0.9, 0.98):
        lo, hi = (1 - c) / 2, 1 - (1 - c) / 2
        cov['%d%%' % int(c * 100)] = sum(1 for u in vals if lo <= u <= hi) / n
    return {'n': n, 'mean': statistics.fmean(vals), 'deciles': [x / n for x in dec], 'central_coverage': cov}


def cmd_analyze(args):
    out = Path(args.out)
    t0 = time.time()
    A = {'generated': utc_iso(), 'ssr': SSR,
         'preregistration': {'market_window': [MARKET_START, MARKET_END], 'train_window': [TRAIN_START, TRAIN_END],
                             'cutoff': CUTOFF, 'decisions': DECISIONS, 'edges': EDGES, 'nbm_lag_h': NBM_LAG_H,
                             'maker_rest_hours': 6, 'exec': ['taker', 'maker'],
                             'bucket_types': ['all', 'interior', 'tail'],
                             'note': 'fixed in the script header before any price was joined to a forecast'}}
    # ---- truth
    k_st = sorted({v['station'] for v in KALSHI_SERIES.values()})
    truth = {st: load_cli(out, st) for st in k_st}
    pm_truths = {}
    for city, meta in PM_CITIES.items():
        ap_ = out / 'raw' / 'wx' / 'asos' / ('%s.json.gz' % meta['asos'])
        if not ap_.exists():
            continue
        rows = read_gz(ap_)
        mnt = routine_minute(rows)
        pm_truths[meta['station']] = {
            'minute': mnt, 'all_tenths': metar_daily_max(rows, meta['tz']),
            'routine_tenths': metar_daily_max(rows, meta['tz'], minute=mnt),
            'all_wholec': metar_daily_max(rows, meta['tz'], wholec=True),
            'routine_wholec': metar_daily_max(rows, meta['tz'], minute=mnt, wholec=True),
            'cli': load_cli(out, meta['station'])}
    # ---- events
    kev = load_kalshi_events(out)
    cities = [c for c in PM_CITIES if (out / 'raw' / 'pm' / 'events' / c).exists()]
    pev_all = load_pm_events(out, cities)
    pm_cov = collections.Counter(e['key'] for e in pev_all)
    # a city enters when (nearly) every listed event has its prices; Polymarket listed the non-NYC US ladders from
    # December 2025 / January 2026, so their in-sample stretch is short
    listed = {c: sum(1 for f in (out / 'raw' / 'pm' / 'events' / c).glob('*.json.gz') if not read_gz(f).get('missing'))
              for c in cities}
    pm_cities = [c for c in cities if listed[c] and pm_cov[c] >= 0.9 * listed[c]]
    pev = [e for e in pev_all if e['key'] in pm_cities]
    A['universe'] = {'kalshi_events': len(kev), 'kalshi_markets': sum(len(e['buckets']) for e in kev),
                     'kalshi_by_series': dict(collections.Counter(e['key'] for e in kev)),
                     'polymarket_events_loaded': dict(pm_cov), 'polymarket_events_listed': listed,
                     'polymarket_cities_used': pm_cities,
                     'polymarket_events': len(pev), 'polymarket_markets': sum(len(e['buckets']) for e in pev)}
    # ---- resolution: does the station record reproduce the settled bucket?
    res_k = collections.defaultdict(lambda: collections.Counter())
    mism = []
    for e in kev:
        w = winner(e)
        v = truth[e['station']].get(e['date'])
        c = res_k[e['key']]
        if w is None:
            c['no_single_winner'] += 1
            continue
        if v is None:
            c['no_cli'] += 1
            continue
        ok = pays_yes(w['lo'], w['hi'], v)
        c['match' if ok else 'mismatch'] += 1
        if not ok:
            mism.append({'series': e['key'], 'date': e['date'], 'cli_high': v, 'winner': [w['lo'], w['hi']],
                         'expiration_value': w.get('exp_value'),
                         'source': 'twc' if 'Weather Company' in (w.get('rules') or '') else 'nws_cli'})
    tot = sum((c for c in res_k.values()), collections.Counter())
    A['resolution_kalshi'] = {'by_series': {k: dict(v) for k, v in res_k.items()}, 'total': dict(tot),
                              'match_rate': tot['match'] / max(1, tot['match'] + tot['mismatch']),
                              'mismatches': mism[:60]}
    res_p = collections.defaultdict(lambda: collections.Counter())
    for e in load_pm_winners(out, cities):          # every listed event, whether or not its prices were fetched
        w = e['winner']
        if w is None:
            res_p['_no_single_winner']['n'] += 1
            continue
        tv = pm_truths.get(e['station'], {})
        era = e['date'][:7]
        for name in ('all_tenths', 'routine_tenths', 'all_wholec', 'routine_wholec', 'cli'):
            v = (tv.get(name) or {}).get(e['date'])
            if v is None:
                res_p[name]['missing'] += 1
                continue
            ok = pays_yes(w['lo'], w['hi'], v)
            res_p[name]['match' if ok else 'mismatch'] += 1
            res_p[name + '|' + era]['match' if ok else 'mismatch'] += 1
            res_p[name + '|' + e['key']]['match' if ok else 'mismatch'] += 1
    A['resolution_polymarket'] = {k: dict(v, rate=v['match'] / max(1, v['match'] + v['mismatch']))
                                  for k, v in res_p.items()}
    best_pm = max(('all_tenths', 'routine_tenths', 'all_wholec', 'routine_wholec', 'cli'),
                  key=lambda n: A['resolution_polymarket'].get(n, {}).get('rate', 0.0))
    A['polymarket_truth_used'] = best_pm
    truth_p = {st: tv[best_pm] for st, tv in pm_truths.items()}
    def model_block(seasonal_var):
        R = {}
        # ---- forecasts and error models (training year only); Kalshi settles on the climate report, Polymarket on
        # METAR readings, so the same station (KMIA) carries two models
        nbs = {st: load_nbs_max(out, st) for st in set(k_st) | set(pm_truths)}
        tzs = {v['station']: v['tz'] for v in list(KALSHI_SERIES.values()) + list(PM_CITIES.values())}
        venues = {'kalshi': (k_st, truth), 'polymarket': (sorted(pm_truths), truth_p)}
        models = {'kalshi': {}, 'polymarket': {}}
        fits = {}
        for venue, (stations, tr) in venues.items():
            for st in stations:
                for dec, (off, hour) in DECISIONS.items():
                    pairs = []
                    for d in market_days(TRAIN_START, TRAIN_END):
                        o = tr.get(st, {}).get(d)
                        fc = forecast_at(nbs[st].get(d), local_ts(d, off, hour, tzs[st]))
                        if o is None or fc is None:
                            continue
                        pairs.append((doy(d), o - fc[1], fc[2]))
                    m = fit_error_model(pairs, seasonal_var=seasonal_var)
                    if m:
                        models[venue][(st, dec)] = m
                        fits['%s|%s|%s' % (venue, st, dec)] = {k: m[k] for k in (
                            'n', 'a', 'c', 'med_xnd', 'overall_bias', 'resid_sd', 'form', 'h', 'loo_log_normal',
                            'loo_log_empirical', 'z_skew', 'z_kurtosis', 'scale_range')}
        R['error_models'] = fits
        # ---- calibration on the market window (before any price is used)
        import random
        rng = random.Random(17)
        pit = collections.defaultdict(list)
        for venue, (stations, tr) in venues.items():
            for st in stations:
                for dec, (off, hour) in DECISIONS.items():
                    if (st, dec) not in models[venue]:
                        continue
                    for d in market_days():
                        o = tr.get(st, {}).get(d)
                        fc = forecast_at(nbs[st].get(d), local_ts(d, off, hour, tzs[st]))
                        if o is None or fc is None:
                            continue
                        mu, sd = predictive(models[venue][(st, dec)], d, fc[1], fc[2])
                        u = pit_value(o, mu, sd, rng.random(), model_cdf(models[venue][(st, dec)]))
                        pit['%s|%s|%s' % (venue, st, dec)].append(u)
                        pit['%s|all|%s' % (venue, dec)].append(u)
                        pit['%s|all|%s|%s' % (venue, dec, 'is' if d < CUTOFF else 'oos')].append(u)
        R['pit'] = {k: pit_summary(v) for k, v in sorted(pit.items())}
        # ---- decision rows
        rows_k, drops_k = decision_rows(kev, models['kalshi'], nbs, truth)
        rows_p, drops_p = decision_rows(pev, models['polymarket'], nbs, truth_p)
        R['rows'] = {'kalshi': len(rows_k), 'kalshi_drops': drops_k, 'polymarket': len(rows_p), 'polymarket_drops': drops_p}
        hs_table = half_spread_table(out)
        R['live_costs'] = hs_table
        # ---- diagnostics: market vs model, same buckets
        diag = {}
        for venue, rows in (('kalshi', rows_k), ('polymarket', rows_p)):
            for dec in DECISIONS:
                for per in ('is', 'oos', 'all'):
                    rr = [r for r in rows if r['dec'] == dec and r['result'] is not None and r.get('mid') is not None
                          and (per == 'all' or (per == 'is') == (r['date'] < CUTOFF))]
                    mk = [(min(0.999, max(0.001, r['mid'])), r['result']) for r in rr]
                    md = [(r['p'], r['result']) for r in rr]
                    # the mean of the two: does the model add information to the price?
                    bl = [((min(0.999, max(0.001, r['mid'])) + r['p']) / 2.0, r['result']) for r in rr]
                    diag['%s|%s|%s' % (venue, dec, per)] = {'market': scores(mk), 'model': scores(md), 'blend': scores(bl)}
                    if per == 'all':
                        diag['%s|%s|reliability' % (venue, dec)] = {'market': reliability(mk), 'model': reliability(md)}
        R['diagnostics'] = diag
        R['implied_mean'] = implied_mean_diag(rows_k + rows_p)
        # when the model and the price disagree, who is right? bins of (model p - price), same buckets
        dis = {}
        for venue, rows in (('kalshi', rows_k), ('polymarket', rows_p)):
            for dec in DECISIONS:
                rr = [r for r in rows if r['dec'] == dec and r['result'] is not None and r.get('mid') is not None]
                for a, b in ((-1.0, -0.15), (-0.15, -0.05), (-0.05, 0.05), (0.05, 0.15), (0.15, 1.0)):
                    v = [r for r in rr if a <= r['p'] - r['mid'] < b]
                    if v:
                        dis['%s|%s|%+.2f..%+.2f' % (venue, dec, a, b)] = {
                            'n': len(v), 'mean_model_p': statistics.fmean(r['p'] for r in v),
                            'mean_price': statistics.fmean(r['mid'] for r in v),
                            'yes_rate': statistics.fmean(r['result'] for r in v)}
        R['disagreement'] = dis
        # month by month and city by city: is the price ever worse than the model (a newly listed city, a season)?
        bym = collections.defaultdict(lambda: {'n': 0, 'mkt': 0.0, 'mdl': 0.0})
        for venue, rows in (('kalshi', rows_k), ('polymarket', rows_p)):
            for r in rows:
                if r['result'] is None or r.get('mid') is None:
                    continue
                m = min(0.999, max(0.001, r['mid']))
                for k in ('%s|%s|%s' % (venue, r['dec'], r['date'][:7]), '%s|%s|%s' % (venue, r['dec'], r['key'])):
                    bym[k]['n'] += 1
                    bym[k]['mkt'] += (m - r['result']) ** 2
                    bym[k]['mdl'] += (r['p'] - r['result']) ** 2
        # is the price's lead significant? daily mean of (model Brier - market Brier), circular block bootstrap
        bsig = {}
        for venue, rows in (('kalshi', rows_k), ('polymarket', rows_p)):
            for dec in DECISIONS:
                byd = collections.defaultdict(list)
                for r in rows:
                    if r['dec'] == dec and r['result'] is not None and r.get('mid') is not None:
                        m = min(0.999, max(0.001, r['mid']))
                        byd[r['date']].append((r['p'] - r['result']) ** 2 - (m - r['result']) ** 2)
                daily = [statistics.fmean(byd[d]) for d in sorted(byd)]
                if len(daily) > 10:
                    bb = B.block_bootstrap(daily, n=2000, seed=7)
                    t, pv = B.newey_west_t(daily)
                    bsig['%s|%s' % (venue, dec)] = {'days': len(daily), 'mean_daily_model_minus_market': bb['point'],
                                                    'ci95': [bb['lo'], bb['hi']], 'share_le_0': bb['p_le_0'],
                                                    'hac_t': t}
        R['brier_gap_significance'] = bsig
        R['brier_by_month_and_city'] = {k: {'n': v['n'], 'market': v['mkt'] / v['n'], 'model': v['mdl'] / v['n'],
                                            'model_minus_market': (v['mdl'] - v['mkt']) / v['n']}
                                        for k, v in sorted(bym.items())}
        # how much of the market's lead is the forecast's age? the model's point error with a 1-hour publication lag
        # (which admits the 18 UTC run at 16:00 Eastern) against the pre-registered 2.5 hours (weather only, no prices)
        lagsens = {}
        for venue, (stations, tr) in venues.items():
            for lag in (1.0, NBM_LAG_H):
                for dec, (off, hour) in DECISIONS.items():
                    errs = []
                    for st in stations:
                        if (st, dec) not in models[venue]:
                            continue
                        for d in market_days():
                            o = tr.get(st, {}).get(d)
                            fc = forecast_at(nbs[st].get(d), local_ts(d, off, hour, tzs[st]), lag_h=lag)
                            if o is None or fc is None:
                                continue
                            mu, _ = predictive(models[venue][(st, dec)], d, fc[1], fc[2])
                            errs.append(abs(mu - o))
                    if errs:
                        lagsens['%s|%s|lag%.1fh' % (venue, dec, lag)] = {'n': len(errs), 'mae': statistics.fmean(errs)}
        R['nbm_lag_sensitivity'] = lagsens
        # ---- variants and the protocol: the time axis is the market days the venue's data covers (a day missing from the
        # collection is not a day without trades), split at the pre-registered cutoff
        axes = {'kalshi': sorted({e['date'] for e in kev}), 'polymarket': sorted({e['date'] for e in pev})}
        fam = {'kalshi': [], 'polymarket': []}
        for dec in DECISIONS:
            for thr in EDGES:
                for bt in ('all', 'interior', 'tail'):
                    for ex in ('taker', 'maker'):
                        fam['kalshi'].append(('kalshi', dec, thr, ex, bt))
                        fam['polymarket'].append(('polymarket', dec, thr, ex, bt))
        R['variants_count'] = {k: len(v) for k, v in fam.items()}
        proto, chosen_detail = {}, {}
        for venue, vs in fam.items():
            rows = rows_k if venue == 'kalshi' else rows_p
            if not rows:
                continue
            days = axes[venue]
            ci = bisect.bisect_left(days, CUTOFF)
            frac = ci / len(days)
            series, series_ratio, per_v = {}, {}, {}
            for v in vs:
                name = '%s|%s|e%.2f|%s|%s' % v
                tr = trades_for(rows, v, hs_table)
                series[name] = daily_pnl_series(tr, days)
                series_ratio[name] = daily_series(tr, days)
                per_v[name] = {'is': summarize_trades([t for t in tr if t['date'] < CUTOFF]),
                               'oos': summarize_trades([t for t in tr if t['date'] >= CUTOFF])}
            res = B.choose_then_test(series, frac=frac, periods_per_year=365)
            res.pop('bh_adjusted_p', None)
            # the first run's series (profit over that day's stake) equal-weights days: a tail variant with rare large
            # wins on tiny stakes showed a positive in-sample mean while its pooled in-sample return per dollar was
            # negative. Kept for disclosure; the go rule uses the constant-capital series above.
            rr = B.choose_then_test(series_ratio, frac=frac, periods_per_year=365)
            R.setdefault('protocol_per_day_stake_series', {})[venue] = {
                kk: rr[kk] for kk in ('chosen', 'in_sample_positive', 'oos_t', 'oos_rank', 'bh_survivors_positive')}
            R['protocol_per_day_stake_series'][venue]['chosen_pooled_is_return_per_dollar'] = per_v[rr['chosen']][
                'is'].get('return_per_dollar')
            res['frac'] = frac
            res['cutoff_date'] = CUTOFF
            res['days_in_sample'], res['days_out_of_sample'] = ci, len(days) - ci
            res['first_day'], res['last_day'] = days[0], days[-1]
            proto[venue] = res
            R['variants_%s' % venue] = per_v
            name = res['chosen']
            v = next(x for x in vs if '%s|%s|e%.2f|%s|%s' % x == name)
            tr = trades_for(rows, v, hs_table)
            oos = [t for t in tr if t['date'] >= CUTOFF]
            late = trades_for(rows, v, hs_table, late=True)
            late_oos = [t for t in late if t['date'] >= CUTOFF]
            # the same trades priced an hour later (fill at the later ask, whatever its edge then); a maker variant
            # has no 'same trade' an hour later, so its late test is the rule re-run (the limit posted an hour later)
            same_late = []
            idx = {(r['id'], r['dec']): r for r in rows}
            for t in (oos if v[3] == 'taker' else []):
                r = idx.get((t['id'], v[1]))
                if venue == 'kalshi':
                    px = (r['ask1'] if t['side'] == 'yes' else (None if r['bid1'] is None else 1.0 - r['bid1']))
                    cost = None if px is None else kalshi_taker_cost(px)
                else:
                    m1 = r.get('mid1')
                    if m1 is None:
                        px = None
                    else:
                        px = min(0.999, (m1 if t['side'] == 'yes' else 1.0 - m1) + pm_hs_for(hs_table, m1))
                    cost = None if px is None else pm_taker_cost(px, r['fee_rate'])
                if cost is not None:
                    same_late.append(dict(t, cost=cost, price=px))
            s0, s1, s2 = summarize_trades(oos), summarize_trades(late_oos), summarize_trades(same_late)
            if v[3] != 'taker':
                s2 = s1
            oos_days = len(days) - ci
            # capacity: size at the touch (live median by price band) and half the volume traded in the two hours around
            cap_rows, part_rows = [], []
            for t in oos:
                if venue == 'kalshi':
                    td = hs_table['kalshi_touch_contracts'].get(pband(t['price']), {}).get('median', 0.0)
                    size = min(td, 0.5 * (t.get('vol2h') or 0.0))
                    # upper bound: a tenth of the contracts traded in the two hours around the decision, as if the
                    # book refilled between takes
                    part_rows.append((0.10 * (t.get('vol2h') or 0.0), t))
                else:
                    tu = hs_table['pm_touch_usd'].get(pband(t['price']), {}).get('median', 0.0)
                    size = min(tu, 0.02 * (t.get('volume') or 0.0)) / max(t['price'], 1e-3)
                cap_rows.append((size, t))
            if part_rows:
                pp = sum(sz * (t['payout'] - t['cost']) for sz, t in part_rows) * 365.0 / (len(days) - ci)
                pc = sum(sz * t['cost'] * t['hold_days'] for sz, t in part_rows) / (len(days) - ci)
                participation = {'annual_pnl_usd': pp, 'avg_capital_usd': pc, 'annual_excess_over_ssr_usd': pp - SSR * pc,
                                 'rule': '10% of contracts traded in the two hours around the decision'}
            else:
                participation = None
            pnl_usd = sum(sz * (t['payout'] - t['cost']) for sz, t in cap_rows)
            capd = sum(sz * t['cost'] * t['hold_days'] for sz, t in cap_rows)
            by_day = collections.defaultdict(float)
            for sz, t in cap_rows:
                by_day[t['date']] += sz * t['cost']
            avg_cap = capd / oos_days
            ann = pnl_usd * 365.0 / oos_days
            chosen_detail[venue] = {
                'variant': name, 'oos_trades': s0, 'late_same_trades': s2, 'late_rule_rerun': s1,
            'oos_by_key': {k: summarize_trades([t for t in oos if t['key'] == k])
                           for k in sorted({t['key'] for t in oos})},
            'oos_by_side': {k: summarize_trades([t for t in oos if t['side'] == k]) for k in ('yes', 'no')},
            'oos_by_month': {k: summarize_trades([t for t in oos if t['date'][:7] == k])
                             for k in sorted({t['date'][:7] for t in oos})},
                'late_share_kept_same_trades': (s2.get('pnl_per_contract', 0) / s0['pnl_per_contract'])
                if s0.get('n') and s0.get('pnl_per_contract') else None,
                'late_share_kept_rule_rerun': (sum(t['payout'] - t['cost'] for t in late_oos) /
                                               sum(t['payout'] - t['cost'] for t in oos))
                if oos and sum(t['payout'] - t['cost'] for t in oos) != 0 else None,
                'capacity_participation': participation,
                'capacity': {'oos_days': oos_days, 'pnl_usd_oos': pnl_usd, 'annual_pnl_usd': ann,
                             'avg_capital_usd': avg_cap, 'peak_day_capital_usd': max(by_day.values()) if by_day else 0.0,
                             'annual_excess_over_ssr_usd': ann - SSR * avg_cap,
                             'median_size_contracts': statistics.median(sz for sz, _ in cap_rows) if cap_rows else None},
            }
        R['protocol'] = proto
        R['chosen'] = chosen_detail
        go = {}
        for venue, res in proto.items():
            cd = chosen_detail.get(venue, {})
            go[venue] = {'in_sample_positive': res['in_sample_positive'],
                         'oos_t_ge_2': (res['oos_t'] or 0) >= 2.0,
                         'chosen_in_bh_positive': res['chosen'] in res['bh_survivors_positive'],
                         'excess_over_ssr_positive': (cd.get('capacity', {}).get('annual_excess_over_ssr_usd') or 0) > 0}
            go[venue]['go'] = all(go[venue].values())
        R['go'] = go
        R['_rows'] = (rows_k, rows_p)
        return R

    R1 = model_block(True)
    rows_k, rows_p = R1.pop('_rows')
    A.update(R1)
    # ---- the stored universe's $10k filter (coordinator note, 2026-10-14): members that cross $10k of lifetime volume
    # are disproportionately the winners. Every event here is fetched whole from gamma by slug, so the backtest uses
    # every member; this block measures how large the bias would have been on the filtered subset.
    sb = {}
    for dec in DECISIONS:
        for name, keep in (('all_members', lambda r: True),
                           ('members_with_10k_volume', lambda r: (r.get('volume') or 0) >= 10000),
                           ('members_under_10k_volume', lambda r: (r.get('volume') or 0) < 10000)):
            rr = [r for r in rows_p if r['dec'] == dec and r['result'] is not None and r.get('mid') is not None
                  and keep(r)]
            sb['%s|%s' % (dec, name)] = {'n': len(rr), 'yes_rate': statistics.fmean(r['result'] for r in rr)
                                         if rr else None, 'mean_mid': statistics.fmean(r['mid'] for r in rr)
                                         if rr else None, 'mean_model_p': statistics.fmean(r['p'] for r in rr)
                                         if rr else None}
    ev_members = collections.Counter()
    for e in pev:
        ev_members[len(e['buckets'])] += 1
    sb['event_member_counts'] = dict(ev_members)
    sb['members_total'] = sum(len(e['buckets']) for e in pev)
    sb['members_under_10k'] = sum(1 for e in pev for b in e['buckets'] if (b.get('volume') or 0) < 10000)
    A['selection_bias_check'] = sb
    R0 = model_block(False)
    R0.pop('_rows')
    A['robustness_flat_variance'] = {
        'note': 'the same 96 variants with a season-aware bias but a flat variance model (the first version, '
                'replaced after its PIT showed summer over-dispersion; one debug run on partial data printed its '
                'Kalshi protocol line)', 'pit': {k: v for k, v in R0['pit'].items() if '|all|' in k},
        'protocol': {k: {kk: v[kk] for kk in ('chosen', 'in_sample_positive', 'oos_t', 'oos_rank',
                                             'bh_survivors_positive')} for k, v in R0['protocol'].items()},
        'go': R0['go'], 'chosen': {k: {'variant': v['variant'], 'oos_trades': v['oos_trades'],
                                      'capacity': v['capacity']} for k, v in R0['chosen'].items()},
        'diagnostics': {k: v for k, v in R0['diagnostics'].items() if not k.endswith('reliability')}}
    if args.fills and 'polymarket' in A.get('chosen', {}):
        name = A['chosen']['polymarket']['variant']
        venue, dec, thr, execu, bt = name.split('|')
        fc = fills_check(out, rows_p, (venue, dec, float(thr[1:]), execu, bt), A['live_costs'], n=args.fills)
        A['fills_check_polymarket'] = fc
        update_manifest(out, 'fills_check', {'generated': utc_iso(), 'entries': len(fc['rows']), 'variant': name,
                                             'http': fc['http'], 'source': fc['source']})
    A['variants_frozen_at'] = {'kalshi': '2026-10-14T07:45:00+00:00', 'polymarket_taker': '2026-10-14T07:45:00+00:00',
                               'polymarket_maker': '2026-10-14T07:58:00+00:00 (added before any Polymarket return was '
                                                   'computed)'}
    # The Kalshi per-market endpoint ran at ~1-1.6 requests/s behind other workers' traffic, so the collection stop was
    # fixed in advance (07:55 UTC) at 09:00 UTC, whatever the data then showed; Kalshi days were fetched in a
    # stratified order (every 4th day first) so that a stopped run still spans both sides of the cutoff.
    A['collection_stop_committed'] = {'committed_at': '2026-10-14T07:55:00+00:00', 'stop_at': '2026-10-14T09:00:00+00:00',
                                      'outcome': 'every Kalshi market (14,652) and every listed Polymarket event in the '
                                                 'six cities was collected before the stop'}
    A['audit'] = {
        'variants_tried': {'primary': sum(A['variants_count'].values()),
                           'flat_variance_robustness': sum(A['variants_count'].values()),
                           'total': 2 * sum(A['variants_count'].values())},
        'protocol_series_versions': ['profit over that day\'s stake (first run, equal-weights days; kept as '
                                     'protocol_per_day_stake_series)', 'profit over a constant capital (final)'],
        'non_return_choices': ['error shape normal vs kernel-smoothed empirical, by training-year leave-one-out log '
                               'score, per station and decision', 'Polymarket settlement record among 5 candidates, by '
                               'match rate with settled buckets', 'variance model flat vs seasonal: seasonal adopted '
                               'after the flat model\'s PIT showed warm-season over-dispersion'],
        'interim_runs': 'four debug runs on partial data before the 09:00 stop; two printed protocol lines (Kalshi, then '
                        'Kalshi and NYC-only Polymarket); no variant or model was changed after the 07:58 freeze '
                        'except the series correction above, which made no venue pass; the Polymarket fee change '
                        '(charging the current 5% to markets that charged nothing before 2026-03-30) and the maker '
                        'late-entry rule were made before any Polymarket return was computed',
    }
    A['seconds'] = round(time.time() - t0, 1)
    write_json_list(out / 'book_entries.json', book_entries(A))
    # keep the rows' compact form for render and the book
    write_gz(out / 'raw' / 'rows.json.gz', {'kalshi': [{k: r[k] for k in ('key', 'date', 'dec', 'id', 'type', 'p',
                                                                          'mid', 'result', 'lo', 'hi', 'mu', 'sd')}
                                                       for r in rows_k],
                                            'polymarket': [{k: r[k] for k in ('key', 'date', 'dec', 'id', 'type', 'p',
                                                                              'mid', 'result', 'lo', 'hi', 'mu', 'sd')}
                                                           for r in rows_p]})
    p = out / 'analysis.json'
    p.write_text(json.dumps(A, indent=1, default=str))
    update_manifest(out, 'analysis', {'generated': A['generated'], 'script': 'scripts/pm_weather.py analyze',
                                      'kalshi_events': A['universe']['kalshi_events'],
                                      'polymarket_events': A['universe']['polymarket_events'],
                                      'polymarket_cities': A['universe']['polymarket_cities_used'],
                                      'book_snapshots': A['live_costs']['files'], 'seconds': A['seconds']})
    print(json.dumps({'universe': A['universe'], 'rows': A['rows'], 'seconds': A['seconds']}, default=str))
    return 0


# ------------------------------------------------------------------------------------------------ fills check

DATA_API = 'https://data-api.polymarket.com'


def fills_check(out, rows, variant, hs_table, n=200, interval=0.25):
    """Where did Polymarket taker fills sit against the price the backtest charged, and how much flow was there?
    For a sample of a variant's out-of-sample trades: every taker trade on that bucket within an hour either side of
    the decision, on our side (a sale of the other token is a purchase of ours at 1 - price)."""
    import random
    trades = [t for t in trades_for(rows, variant, hs_table) if t['date'] >= CUTOFF]
    meta = {}
    for city in PM_CITIES:
        for f in (Path(out) / 'raw' / 'pm' / 'events' / city).glob('*.json.gz'):
            e = read_gz(f)
            for mm in e.get('markets') or []:
                toks = mm.get('clobTokenIds')
                toks = json.loads(toks) if isinstance(toks, str) else toks
                meta[mm['id']] = (mm.get('conditionId'), toks)
    rng = random.Random(11)
    rng.shuffle(trades)
    sample = trades[:n]
    http = Http(interval=interval)
    res = []

    def one(t):
        cid, toks = meta.get(t['id'], (None, None))
        if not cid or not toks:
            return None
        q = {'market': cid, 'limit': 1000, 'takerOnly': 'true', 'start': int(t['T'] - HOUR), 'end': int(t['T'] + HOUR)}
        d = http.request(DATA_API + '/trades?' + urllib.parse.urlencode(q))
        if not isinstance(d, list):
            return None
        yes, no = toks[0], toks[1]
        mine = yes if t['side'] == 'yes' else no
        other = no if t['side'] == 'yes' else yes
        buys = [(float(x['price']), float(x['size'])) for x in d if x.get('asset') == mine and x.get('side') == 'BUY'
                and t['T'] - HOUR <= int(x.get('timestamp', 0)) <= t['T'] + HOUR]
        buys += [(1.0 - float(x['price']), float(x['size'])) for x in d
                 if x.get('asset') == other and x.get('side') == 'SELL'
                 and t['T'] - HOUR <= int(x.get('timestamp', 0)) <= t['T'] + HOUR]
        near = [p for p, _ in buys]
        return {'id': t['id'], 'side': t['side'], 'charged_price': t['price'], 'n_taker_buys': len(buys),
                'buy_median': statistics.median(near) if near else None, 'buy_usd_2h': sum(p * s for p, s in buys),
                'raw_trades': len(d)}

    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for r in ex.map(one, sample):
            if r:
                res.append(r)
    dif = [r['buy_median'] - r['charged_price'] for r in res if r['buy_median'] is not None]
    usd = sorted(r['buy_usd_2h'] for r in res)
    summ = {'variant': '%s|%s|e%.2f|%s|%s' % variant, 'oos_trades': len(trades), 'sampled': len(res),
            'with_taker_buys': len(dif),
            'buy_median_minus_charged_median': statistics.median(dif) if dif else None,
            'buy_median_minus_charged_p75': sorted(dif)[int(0.75 * (len(dif) - 1))] if dif else None,
            'taker_buy_usd_2h_median': statistics.median(usd) if usd else None,
            'taker_buy_usd_2h_p75': usd[int(0.75 * (len(usd) - 1))] if usd else None,
            'taker_buy_usd_2h_mean': statistics.fmean(usd) if usd else None}
    return {'summary': summ, 'rows': res[:400], 'http': http.stats(),
            'source': DATA_API + '/trades (takerOnly, +-1h of the decision)'}


# ------------------------------------------------------------------------------------------------ book entries

def write_json_list(p, rows):
    Path(p).write_text(json.dumps(rows, indent=1, default=str) + '\n')


def book_entries(A):
    """A proposed strategy row per venue whose chosen variant passed the go rule; [] when none did."""
    rows = []
    for venue, g in (A.get('go') or {}).items():
        if not g.get('go'):
            continue
        cd, res = A['chosen'][venue], A['protocol'][venue]
        c, o = cd['capacity'], cd['oos_trades']
        rows.append({
            'id': 'pm-weather-%s' % venue,
            'name': 'Daily high-temperature ladders on %s priced by the NBM with a station error model' % venue,
            'kind': 'prediction-market',
            'status': 'proposed',
            'thesis': 'Variant %s chosen before %s; out of sample %d trades, %.1f%% a dollar, HAC t %.2f.' % (
                cd['variant'], res['cutoff_date'], o['n'], 100 * o['return_per_dollar'], res['oos_t']),
            'mechanism': 'Retail prices the ladder without a calibrated forecast; the NBM station bulletin plus a '
                         'training-year error model prices the buckets, entered at fixed clock times.',
            'legs': ['at the decision time, buy every bucket side whose model probability exceeds the all-in cost '
                     'by the chosen edge; hold to settlement'],
            'capacity_usd': round(c['avg_capital_usd']),
            'capital_days': round(statistics.fmean([1.1, 1.75]), 2),
            'kill_criteria': ['trailing 60-day return per dollar below zero',
                              'the station record stops reproducing the settled bucket (match rate below 97%)',
                              'PIT 80% coverage outside 75-90% over a trailing quarter'],
            'quotes': [{'at': A['generated'], 'source': 'history', 'window': 'research/2026-10-14/pm_weather',
                        'net_apr': o.get('ann_excess_over_ssr'), 'usd': round(c['annual_excess_over_ssr_usd']),
                        'go': True, 'present': True,
                        'note': 'late entry keeps %s of the edge' % cd.get('late_share_kept_same_trades')}],
            'risks': ['resolution source changes (Kalshi moved to The Weather Company in October 2026; Polymarket '
                      'from Weather Underground to NOAA hourly data)', 'thin books: capacity is the touch size',
                      'forecast model drift (NBM upgrades)'],
            'evidence': ['research/2026-10-14/pm_weather/analysis.json', 'research/2026-10-14/pm_weather/tables.md'],
        })
    return rows


# ------------------------------------------------------------------------------------------------ render

def _pct(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def _f(x, d=3):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_weather tables (%s)' % A['generated'], '',
         'Every number is in `analysis.json`; the keys are given in each heading.', '']
    u = A['universe']
    L += ['## Universe (`universe`)', '', '| venue | events | markets | detail |', '|---|---:|---:|---|',
          '| Kalshi | %d | %d | %s |' % (u['kalshi_events'], u['kalshi_markets'], ', '.join(
              '%s %d' % kv for kv in sorted(u['kalshi_by_series'].items()))),
          '| Polymarket | %d | %d | cities used: %s (loaded %s) |' % (
              u['polymarket_events'], u['polymarket_markets'], ', '.join(u['polymarket_cities_used']),
              ', '.join('%s %d' % kv for kv in sorted(u['polymarket_events_loaded'].items()))), '']
    rk = A['resolution_kalshi']
    L += ['## Resolution check (`resolution_kalshi`, `resolution_polymarket`)', '',
          'Kalshi: the NWS climate-report high (IEM) inside the settled bucket: %s of %d events (%d mismatches).' % (
              _pct(rk['match_rate'], 2), rk['total'].get('match', 0) + rk['total'].get('mismatch', 0),
              rk['total'].get('mismatch', 0)), '',
          '| series | match | mismatch | no CLI | no single winner |', '|---|---:|---:|---:|---:|']
    for k, v in sorted(rk['by_series'].items()):
        L.append('| %s | %d | %d | %d | %d |' % (k, v.get('match', 0), v.get('mismatch', 0), v.get('no_cli', 0),
                                                 v.get('no_single_winner', 0)))
    L += ['', 'Polymarket: which station record reproduces the settled bucket (used: `%s`).' %
          A['polymarket_truth_used'], '', '| record | match | mismatch | rate |', '|---|---:|---:|---:|']
    for k, v in sorted(A['resolution_polymarket'].items()):
        if '|' not in k and not k.startswith('_'):
            L.append('| %s | %d | %d | %s |' % (k, v.get('match', 0), v.get('mismatch', 0), _pct(v.get('rate'), 2)))
    L += ['', '## Forecast error models, training year (`error_models`)', '',
          '| venue / station / decision | n | bias (mean resid, F) | resid sd | a | c | median XND |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted(A['error_models'].items()):
        L.append('| %s | %d | %s | %s | %s | %s | %s |' % (k, v['n'], _f(v['overall_bias'], 2), _f(v['resid_sd'], 2),
                                                           _f(v['a'], 2), _f(v['c'], 2), _f(v['med_xnd'], 1)))
    L += ['', '## Calibration on the market window (`pit`)', '',
          '| key | n | mean PIT | 50% cov | 80% cov | 90% cov | 98% cov |', '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted(A['pit'].items()):
        if '|all|' in k:
            c = v['central_coverage']
            L.append('| %s | %d | %s | %s | %s | %s | %s |' % (k, v['n'], _f(v['mean']), _pct(c['50%']),
                                                               _pct(c['80%']), _pct(c['90%']), _pct(c['98%'])))
    L += ['', '## Market vs model scores on the same buckets (`diagnostics`)', '',
          '| venue / decision / period | n | Brier market | Brier model | Brier blend | log market | log model |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted(A['diagnostics'].items()):
        if k.endswith('reliability'):
            continue
        L.append('| %s | %d | %s | %s | %s | %s | %s |' % (
            k, v['market'].get('n', 0), _f(v['market'].get('brier'), 4), _f(v['model'].get('brier'), 4),
            _f(v['blend'].get('brier'), 4), _f(v['market'].get('log'), 4), _f(v['model'].get('log'), 4)))
    for k, v in sorted(A['diagnostics'].items()):
        if not k.endswith('reliability'):
            continue
        L += ['', '### Reliability %s' % k, '', '| bin | n market | price | freq | n model | model p | freq |',
              '|---|---:|---:|---:|---:|---:|---:|']
        mk = {r['bin']: r for r in v['market']}
        md = {r['bin']: r for r in v['model']}
        for b in sorted(set(mk) | set(md)):
            a, m = mk.get(b, {}), md.get(b, {})
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (b, a.get('n', 0), _f(a.get('mean_p')), _f(a.get('freq')),
                                                               m.get('n', 0), _f(m.get('mean_p')), _f(m.get('freq'))))
    L += ['', '## Protocol (`protocol`, `go`)', '']
    for venue, res in A['protocol'].items():
        ins, oos = res['in_sample'], res['out_of_sample']
        L += ['**%s** — %d variants, chose `%s` on market days before %s.' % (
            venue, res['n_variants'], res['chosen'], res['cutoff_date']), '',
              '| | days | mean daily return on capital | Sharpe | hit rate (active days) |', '|---|---:|---:|---:|---:|',
              '| in sample | %d | %s | %s | %s |' % (ins['n'], _pct(ins.get('mean'), 3), _f(ins.get('sharpe'), 2),
                                                     _pct(ins.get('hit_rate'))),
              '| out of sample | %d | %s | %s | %s |' % (oos['n'], _pct(oos.get('mean'), 3), _f(oos.get('sharpe'), 2),
                                                         _pct(oos.get('hit_rate'))), '',
              'Out-of-sample HAC t %s (rank %d of %d); BH one-sided survivors: %s; go: %s.' % (
                  _f(res['oos_t'], 2), res['oos_rank'], res['n_variants'],
                  ', '.join(res['bh_survivors_positive']) or 'none', A['go'][venue]), '']
        cd = A['chosen'].get(venue, {})
        if cd:
            o, l2, l1, c = cd['oos_trades'], cd['late_same_trades'], cd['late_rule_rerun'], cd['capacity']
            L += ['| chosen variant, out of sample | trades | win rate | mean price | model p | return per $ | '
                  'annualised excess over SSR |', '|---|---:|---:|---:|---:|---:|---:|',
                  '| at the decision | %s | %s | %s | %s | %s | %s |' % (
                      o.get('n'), _pct(o.get('win_rate')), _f(o.get('mean_price')), _f(o.get('mean_model_p')),
                      _pct(o.get('return_per_dollar'), 2), _pct(o.get('ann_excess_over_ssr'))),
                  '| same trades an hour later | %s | %s | %s | %s | %s | %s |' % (
                      l2.get('n'), _pct(l2.get('win_rate')), _f(l2.get('mean_price')), _f(l2.get('mean_model_p')),
                      _pct(l2.get('return_per_dollar'), 2), _pct(l2.get('ann_excess_over_ssr'))),
                  '| rule re-run an hour later | %s | %s | %s | %s | %s | %s |' % (
                      l1.get('n'), _pct(l1.get('win_rate')), _f(l1.get('mean_price')), _f(l1.get('mean_model_p')),
                      _pct(l1.get('return_per_dollar'), 2), _pct(l1.get('ann_excess_over_ssr'))), '',
                  'Late entry keeps %s (same trades) / %s (rule re-run) of the edge. Capacity at the touch: average '
                  'capital $%s, peak day $%s, P&L $%s a year, $%s a year over SSR.' % (
                      _pct(cd.get('late_share_kept_same_trades')), _pct(cd.get('late_share_kept_rule_rerun')),
                      _f(c['avg_capital_usd'], 0), _f(c['peak_day_capital_usd'], 0), _f(c['annual_pnl_usd'], 0),
                      _f(c['annual_excess_over_ssr_usd'], 0)), '']
    for venue in ('kalshi', 'polymarket'):
        pv = A.get('variants_%s' % venue) or {}
        if not pv:
            continue
        L += ['### Every %s variant (`variants_%s`)' % (venue, venue), '',
              '| variant | IS trades | IS return/$ | IS win | OOS trades | OOS return/$ | OOS win | OOS mean price |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        for k, v in pv.items():
            i, o = v['is'], v['oos']
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                k, i.get('n'), _pct(i.get('return_per_dollar'), 2), _pct(i.get('win_rate')), o.get('n'),
                _pct(o.get('return_per_dollar'), 2), _pct(o.get('win_rate')), _f(o.get('mean_price'))))
        L.append('')
    im = A.get('implied_mean') or {}
    if im:
        L += ['## Implied mean high vs the settled value (`implied_mean`)', '',
              '| venue / decision (/ city) | ladders | market bias F | market MAE | model bias F | model MAE | '
              'market minus model F |', '|---|---:|---:|---:|---:|---:|---:|']
        for k, v in sorted(im.items()):
            L.append('| %s | %d | %s | %s | %s | %s | %s |' % (k, v['n'], _f(v['market_bias'], 2), _f(v['market_mae'], 2),
                                                               _f(v['model_bias'], 2), _f(v['model_mae'], 2),
                                                               _f(v['market_minus_model_mean'], 2)))
        L.append('')
    bs = A.get('brier_gap_significance') or {}
    if bs:
        L += ['## Is the price better than the model? (`brier_gap_significance`)', '',
              'Daily mean of (model Brier - market Brier) on the same buckets; positive means the price is better.', '',
              '| venue / decision | days | mean | 95% interval (block bootstrap) | HAC t |', '|---|---:|---:|---|---:|']
        for k, v in sorted(bs.items()):
            L.append('| %s | %d | %s | %s to %s | %s |' % (k, v['days'], _f(v['mean_daily_model_minus_market'], 4),
                                                         _f(v['ci95'][0], 4), _f(v['ci95'][1], 4), _f(v['hac_t'], 2)))
        L.append('')
    ls = A.get('nbm_lag_sensitivity') or {}
    if ls:
        L += ['## Forecast age (`nbm_lag_sensitivity`)', '', '| venue / decision / publication lag | days | model MAE F |',
              '|---|---:|---:|']
        for k, v in sorted(ls.items()):
            L.append('| %s | %d | %s |' % (k, v['n'], _f(v['mae'], 2)))
        L.append('')
    bm = A.get('brier_by_month_and_city') or {}
    if bm:
        L += ['## Model minus market Brier by month and city (`brier_by_month_and_city`)', '',
              '| key | n | market | model | model - market |', '|---|---:|---:|---:|---:|']
        for k, v in sorted(bm.items()):
            L.append('| %s | %d | %s | %s | %s |' % (k, v['n'], _f(v['market'], 4), _f(v['model'], 4),
                                                     _f(v['model_minus_market'], 4)))
        L.append('')
    dis = A.get('disagreement') or {}
    if dis:
        L += ['## When the model and the price disagree (`disagreement`)', '',
              '| venue / decision / model p minus price | n | model p | price | YES rate |', '|---|---:|---:|---:|---:|']
        for k, v in sorted(dis.items()):
            L.append('| %s | %d | %s | %s | %s |' % (k, v['n'], _pct(v['mean_model_p']), _pct(v['mean_price']),
                                                     _pct(v['yes_rate'])))
        L.append('')
    sb = A.get('selection_bias_check') or {}
    if sb:
        L += ['## The $10k-volume selection effect (`selection_bias_check`)', '',
              'Members %d, of which %d under $10k of lifetime volume; event sizes %s.' % (
                  sb.get('members_total', 0), sb.get('members_under_10k', 0), sb.get('event_member_counts')), '',
              '| decision / members | n | YES rate | mean price | mean model p |', '|---|---:|---:|---:|---:|']
        for k, v in sorted(sb.items()):
            if isinstance(v, dict) and 'yes_rate' in v:
                L.append('| %s | %d | %s | %s | %s |' % (k, v['n'], _pct(v['yes_rate'], 2), _pct(v['mean_mid'], 2),
                                                         _pct(v['mean_model_p'], 2)))
        L.append('')
    fc = (A.get('fills_check_polymarket') or {}).get('summary')
    if fc:
        L += ['## Polymarket fills around the decision (`fills_check_polymarket`)', '',
              '```', json.dumps(fc, indent=1), '```', '']
    ps = A.get('protocol_per_day_stake_series')
    if ps:
        L += ['## First protocol run, per-day-stake series (`protocol_per_day_stake_series`)', '',
              'Profit over that day\'s stake equal-weights days; replaced by the constant-capital series above.', '',
              '```', json.dumps(ps, indent=1, default=str), '```', '']
    rb = A.get('robustness_flat_variance')
    if rb:
        L += ['## Robustness: flat variance model (`robustness_flat_variance`)', '', '```',
              json.dumps({'protocol': rb['protocol'], 'go': rb['go']}, indent=1, default=str), '```', '']
    lc = A['live_costs']
    L += ['## Live costs (`live_costs`, %d snapshots)' % len(lc['files']), '',
          '| price band | PM half-spread (median, n) | PM touch $ (median) | Kalshi half-spread | Kalshi touch contracts |',
          '|---|---:|---:|---:|---:|']
    for b in sorted(set(lc['pm_half_spread']) | set(lc['kalshi_touch_contracts'])):
        a, d = lc['pm_half_spread'].get(b, {}), lc['pm_touch_usd'].get(b, {})
        kh, kd = lc['kalshi_half_spread'].get(b, {}), lc['kalshi_touch_contracts'].get(b, {})
        L.append('| %s | %s (%s) | %s | %s | %s |' % (b, _f(a.get('median'), 4), a.get('n', 0), _f(d.get('median'), 0),
                                                     _f(kh.get('median'), 4), _f(kd.get('median'), 0)))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    k = sub.add_parser('kalshi')
    k.add_argument('--out', required=True)
    k.add_argument('--series', default='')
    k.add_argument('--start', default='')
    k.add_argument('--end', default='')
    k.add_argument('--interval', type=float, default=0.25)
    k.add_argument('--workers', type=int, default=2)
    k.add_argument('--refresh', action='store_true')
    k.add_argument('--list-only', action='store_true')
    k.add_argument('--single-only', action='store_true')
    w = sub.add_parser('wx')
    w.add_argument('--out', required=True)
    w.add_argument('--interval', type=float, default=2.0)
    w.add_argument('--nbs-start', default='2024-08-25')
    w.add_argument('--nbs-end', default='2026-10-14')
    w.add_argument('--asos-start', default='2025-08-25')
    pm = sub.add_parser('pm')
    pm.add_argument('--out', required=True)
    pm.add_argument('--cities', default='NYC')
    pm.add_argument('--start', default='')
    pm.add_argument('--end', default='')
    pm.add_argument('--interval', type=float, default=0.25)
    pm.add_argument('--workers', type=int, default=2)
    bk = sub.add_parser('books')
    bk.add_argument('--out', required=True)
    bk.add_argument('--pm-cities', default='NYC,Miami,Dallas,Atlanta,Chicago,Seattle,London,Seoul,Toronto,Paris')
    an = sub.add_parser('analyze')
    an.add_argument('--out', required=True)
    an.add_argument('--fills', type=int, default=0, help='sample this many Polymarket OOS trades for a fills check')
    rn = sub.add_parser('render')
    rn.add_argument('--out', required=True)
    a = ap.parse_args()
    return {'kalshi': cmd_kalshi, 'wx': cmd_wx, 'pm': cmd_pm, 'books': cmd_books, 'analyze': cmd_analyze,
            'render': cmd_render}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
