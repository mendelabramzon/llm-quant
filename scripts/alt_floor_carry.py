#!/usr/bin/env python3
"""Altcoin floor carry: a diversified basket of spot-long / same-venue perp-short positions in the coins whose funding
sits at the formula's interest floor. Does it beat the savings rate out of sample, after negative spikes, basis moves,
costs and capacity, and how much capital can it hold?

Why. The repo's surviving edges are rents paid by agents with a non-price motive. The largest persistent one is the
funding formula's interest leg: when longs dominate, many perps settle exactly at the floor (0.01% per 8 h, 10.95% a
year, pro rata for 4 h and 1 h intervals). Collecting it needs the spot leg as collateral on the same venue. On BTC and
ETH the carry is too small (term_carry: 1.6-6.9% funding, a no-go); HYPE on Hyperliquid portfolio margin is the book's
best carry. The rent map guessed that the altcoin excess "lives in thin books" but never tested it on history, and the
collateral watcher (2026-10-11) found 298 Binance collateral/perp pairs at the floor on at least half of the last 30
days' settlements, yet also that floor share is not carry: MAGIC, KAIA, ERA and OGN sat at the floor 73-89% of the time
and paid -20% to -94% a year through negative spikes. So the question is a history test of a rule family fixed in
advance: pick coins by trailing floor persistence, screen spikes and liquidity, hold an equal-weight basket, and see
whether it survives choose-then-test, multiple testing and size.

How.
  collect   Binance USD-M, read-only public endpoints. Survivorship: the perp universe is every USDT-margined perp in
            fapi exchangeInfo (TRADING, PENDING_TRADING and the SETTLING rows Binance keeps for delisted contracts) plus
            every symbol that appears in the bulk funding history (/fapi/v1/fundingRate without a symbol, paged forward
            from FETCH_START), which also returns contracts that have left exchangeInfo altogether. For each: daily perp
            klines and, where the same coin has a Binance spot market (USDT, else USDC; `1000x` tickers mapped through
            their multiplier; BREAK pairs included, their klines are still served), daily spot klines. Book and 24 h
            tickers calibrate the half-spread model. Raw responses are kept gzip'd under <out>/raw/ with a manifest.
            `--venue bybit`: linear perps listed as Trading and Closed (delisted), per-symbol funding paged backward,
            daily perp and spot klines (delisted spot pairs are not listable but their klines are served by name),
            tickers. OKX is not covered: its public funding history reaches back about three months.
  grid      Writes the rule family into analysis.json before anything is computed; `analyze` refuses to run if the
            grid there differs from GRID.
  analyze   Normalises (drops untraded bars; drops funding stamped on days the perp did not trade or after its delivery
            date, because Binance keeps printing phantom settlements at exactly the floor with a frozen mark for months
            after a delisting), fixes the rule grid in analysis.json before any return is computed, runs every variant
            day by day, then `backtest.choose_then_test` on the first/second half, the top-N-by-floor-share baseline,
            the all-spot robustness universe, the tail numbers and capacity at $1M-$10M.
  render    tables.md and manifest.json from analysis.json; book_entries.json (status 'proposed') only if the chosen
            variant passes (in-sample positive, OOS HAC t > 2, a BH survivor on one-sided p, OOS excess positive at
            $3M). BH is one-sided here because backtest.choose_then_test's two-sided p lets a significant loser
            'survive'; its two-sided list is kept beside.
  probe     One coin's decision-day features recomputed from the raw files (re-derivation, cross-checks).

Conventions. A funding rate is per settlement, positive when longs pay, so a short receives +rate. Day d holds the
settlements in (d 00:00, d+1 00:00] UTC and the kline that opens at d 00:00 (its close is d+1 00:00). A decision at the
start of day d sees days <= d-1 only, enters at day d-1's closes and earns day d's settlements. A position is a fixed
quantity between rebalances (funding paid on quantity x the settlement's mark price); its basis P&L is the change in
(spot x multiplier - perp) per unit; one side of a trade costs the taker fee (Binance VIP0: spot 10bp, USD-M 5bp) plus
the half-spread model, and, in the capacity runs, square-root impact. Capital per $ of short is the collateral
watcher's K = 1 + max(0, im + R - c(1+R)) with c today's portfolio-margin collateral ratio, im = max(1/10, 1/max
leverage), R = 50%; a rally beyond R inside a holding forces a rebalance of the drift. Each name gets 1/N of capital;
unused capital earns the savings rate (zero excess). Excess is over the savings rate actually paid each day (DSR, then
the SSR, from term_carry.load_navs; the constant 3.80% is reported beside it).

    uv run python scripts/alt_floor_carry.py collect --end-day 2026-10-11               # Binance, ~45 min paced, resumable
    uv run python scripts/alt_floor_carry.py collect --venue bybit --end-day 2026-10-11 # Bybit, 8 threads, ~25 min
    uv run python scripts/alt_floor_carry.py grid                    # the rule family, before any result
    uv run python scripts/alt_floor_carry.py analyze                 # both venues -> analysis.json, series.json.gz
    uv run python scripts/alt_floor_carry.py render                  # tables.md, manifest.json (+ book_entries.json)
    uv run python scripts/alt_floor_carry.py probe --symbols MAGICUSDT,KAIAUSDT --day 2026-10-11

Read-only: public, unauthenticated endpoints only; nothing is signed or sent. Binance funding history at 0.7 s a call
(the endpoint has its own 500 calls / 5 min / IP budget), other fapi calls at 0.25 s under the 1-minute weight header,
spot at 0.15 s; a 429/418 stops all calls to that host for Retry-After.
"""
import argparse
import collections
import datetime as dt
import gzip
import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B          # noqa: E402

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
OUT = ROOT / 'research' / '2026-10-11' / 'alt_floor_carry'
COLLATERAL_SNAPSHOT = ROOT / 'research' / 'collateral_watch' / '2026-10-11' / 'collateral.json.gz'
TERM_CARRY_OUT = ROOT / 'research' / '2026-10-10' / 'term_carry'

FETCH_START = '2024-09-01'      # one month before the P&L window, so the first decision has a full 30-day lookback
PNL_START = '2024-10-01'
BN_F = 'https://fapi.binance.com'
BN_S = 'https://api.binance.com'
UA = 'Mozilla/5.0'

SSR_CONST = 0.038               # term_carry.SSR, the book's protocol benchmark (reported beside the paid path)
INTEREST_8H = 0.0001            # the formula's interest leg on Binance USD-M coin perps: 0.01% per 8 h
SPIKE_8H = -0.0005              # the spike screen: any settlement below -0.05% per 8 h-equivalent
FLOOR_TOL = 1e-10               # rates are quoted to 8 decimals; 1e-10 is far below one tick
MAX_GAP_H = 8                   # a settlement never covers more than 8 h (longer gaps are halts, not intervals)
FEE_BP = {'spot': 10.0, 'perp': 5.0}       # Binance VIP0 taker, no BNB discount
STRESS_RALLY = 0.5              # collateral_watch.STRESS_RALLY: the rally the account survives without a top-up
TARGET_LEV = 10.0               # collateral_watch.TARGET_LEV: im = max(1/10, 1/max leverage)
LOOKBACK = 30                   # trailing days for floor share, spikes, volume and volatility
MIN_COVERAGE = 0.8              # trailing funding coverage (hours settled / hours in the window) to be eligible
MIN_SPOT_DAYS = 20              # traded spot days in the lookback for the volume median
IDENTITY_BAND = 0.10            # |perp / (spot x multiplier) - 1| at decision time
EXCLUDE_BASES = {'BTC', 'ETH', 'USDC', 'FDUSD', 'TUSD', 'USDP', 'DAI', 'BUSD', 'USDE', 'USD1', 'PAXG', 'XAUT',
                 'BTCDOM', 'DEFI', 'FOOTBALL', 'BLUEBIRD', 'WBTC', 'WBETH', 'BNSOL', 'STETH'}
MULTIPLIERS = (('1000000', 1e6), ('100000', 1e5), ('10000', 1e4), ('1000', 1e3), ('1M', 1e6))
ALIASES = {'LUNA2': 'LUNA', 'DODOX': 'DODO', 'RAYSOL': 'RAY', 'RONIN': 'RON'}

# The rule family, fixed before any return is computed (written to analysis.json first; see `grid`).
GRID = {'rebalance_days': [7, 28], 'floor_share_min': [0.50, 0.75], 'spike_8h': [None, SPIKE_8H],
        'spot_vol_min_usd': [2e6, 1e7], 'n_names': [10, 30]}
RANK = 'trailing-30d floor share (desc), then trailing-30d funding APR (desc), then spot 30d median quote volume (desc)'
BASELINE = {'floor_share_min': 0.0, 'spike_8h': None, 'spot_vol_min_usd': 2e6}   # top-N by floor share, no screens
SIZES = [1_000_000, 3_000_000, 5_000_000, 10_000_000]
PARTICIPATION = 0.02            # a position <= 2% of the coin's 30-day median daily spot (and perp) quote volume
ENTRY_DAYS = 3                  # a position is built (and unwound) over this many days: daily slice = trade / 3
IMPACT_Y = 0.5                  # square-root impact: cost = Y x sigma_daily x sqrt(daily slice / daily volume)
IMPACT_Y_STRESS = 1.0
SPLIT_FRAC = 0.5


# ---------------------------------------------------------------------------------------------- small utilities

def utc(ms=None):
    t = time.time() if ms is None else ms / 1000.0
    return dt.datetime.fromtimestamp(t, UTC).isoformat(timespec='seconds')


def day_ms(s):
    return int(dt.datetime.strptime(s[:10], '%Y-%m-%d').replace(tzinfo=UTC).timestamp() * 1000)


def ymd(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, UTC).strftime('%Y-%m-%d')


def dname(d):
    return ymd(d * DAY_MS)


def write_gz(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(obj, f)
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


def bad(r):
    return not isinstance(r, (list, dict)) or (isinstance(r, dict) and ('_http_error' in r or '_error' in r or
                                                                      (r.get('code') not in (None, 200, 0))))


# ---------------------------------------------------------------------------------------------- collect: Binance

def bn_http(interval):
    import funding_arb as FA
    return FA.Http(interval=interval, weight_header='X-MBX-USED-WEIGHT-1M', weight_soft=1100)


def collect_funding_bulk(http, raw, start_ms, end_ms, log, chunk_pages=50):
    """Every USD-M settlement in [start, end], 1000 rows a call in time order (no symbol parameter), kept as raw
    pages in chunk files. Paging restarts at the last stamp, inclusive, and duplicates are dropped when normalising;
    exact while fewer than 1000 settlements share one millisecond (about 600 symbols settle at 00:00). Resumable:
    the state file holds the next start."""
    d = Path(raw) / 'funding_bulk'
    d.mkdir(parents=True, exist_ok=True)
    state_fn = d / 'state.json'
    st = json.loads(state_fn.read_text()) if state_fn.exists() else {'next': start_ms, 'chunks': 0, 'pages': 0,
                                                                     'done': False}
    if st.get('done'):
        log['funding_bulk'] = st
        return st
    s, pages, t0 = st['next'], [], time.time()
    while True:
        r = http.get(BN_F + '/fapi/v1/fundingRate', {'startTime': s, 'endTime': end_ms, 'limit': 1000})
        if bad(r):
            raise RuntimeError('fundingRate bulk at %s: %s' % (s, json.dumps(r)[:200]))
        pages.append({'start': s, 'rows': r})
        last = int(r[-1]['fundingTime']) if r else s
        finished = len(r) < 1000
        if not finished and last == s:
            raise RuntimeError('fundingRate bulk: 1000 settlements share one millisecond at %s' % s)
        s = last
        if len(pages) >= chunk_pages or finished:
            write_gz(d / ('chunk_%04d.json.gz' % st['chunks']), pages)
            st['chunks'] += 1
            st['pages'] += len(pages)
            st['next'] = s
            st['done'] = finished
            st['last_stamp'] = utc(last)
            state_fn.write_text(json.dumps(st))
            print('funding bulk: chunk %d, %d pages, at %s, %.0fs' % (st['chunks'], st['pages'], utc(last),
                                                                    time.time() - t0), flush=True)
            pages = []
        if finished:
            break
    log['funding_bulk'] = st
    return st


def load_funding_bulk(raw):
    """{symbol: [(ms, rate, mark)]} from the raw pages, duplicates (same symbol and stamp) removed."""
    out = collections.defaultdict(dict)
    d = Path(raw) / 'funding_bulk'
    for fn in sorted(d.glob('chunk_*.json.gz')):
        for p in read_gz(fn):
            for x in p['rows']:
                out[x['symbol']][int(x['fundingTime'])] = (fnum(x['fundingRate']), fnum(x.get('markPrice')))
    return {s: sorted((t, r, m) for t, (r, m) in v.items()) for s, v in out.items()}


def perp_universe(fex, funding_symbols):
    """USDT-margined coin perps that existed in the window: exchangeInfo rows of any status (SETTLING = delisted) plus
    symbols seen only in the funding history (left exchangeInfo). TradFi perps are excluded (no interest leg)."""
    info = {}
    for s in fex.get('symbols') or []:
        if s.get('contractType') == 'PERPETUAL' and s.get('quoteAsset') == 'USDT':
            req = fnum(s.get('requiredMarginPercent'))
            info[s['symbol']] = {'base': s['baseAsset'], 'status': s['status'], 'source': 'exchangeInfo',
                                 'onboard_ms': s.get('onboardDate'), 'delivery_ms': s.get('deliveryDate'),
                                 'max_lev': (100.0 / req) if req else None}
    known = {s['symbol'] for s in fex.get('symbols') or []}
    for sym in funding_symbols:
        if sym not in known and sym.endswith('USDT'):
            info[sym] = {'base': sym[:-4], 'status': 'absent_from_exchangeInfo', 'source': 'funding_history',
                         'onboard_ms': None, 'delivery_ms': None, 'max_lev': None}
    return info


def spot_bases(base):
    """(spot base, multiplier) a perp with this base asset may hedge with, best first: itself, the base without a
    1000x-style prefix, and a known alias."""
    bases = [(base, 1.0)]
    for pre, mult in MULTIPLIERS:
        if base.startswith(pre) and len(base) > len(pre):
            bases.append((base[len(pre):], mult))
    if base in ALIASES:
        bases.append((ALIASES[base], 1.0))
    return bases


def spot_candidates(base, spot_symbols=None, quotes=('USDT', 'USDC')):
    """Spot pairs that may be the same coin as a perp with this base asset, best first: (spot symbol, spot base,
    multiplier); only listed ones when `spot_symbols` is given. The data identity check (perp / (spot x multiplier)
    near 1) decides among them."""
    out = []
    for b, mult in spot_bases(base):
        for q in quotes:
            if spot_symbols is None or b + q in spot_symbols:
                out.append((b + q, b, mult))
    return out


BN_ARCHIVE = 'https://data.binance.vision/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{m}.zip'


def months_between(start_ms, end_ms):
    d = dt.datetime.fromtimestamp(start_ms / 1000.0, UTC).replace(day=1)
    e = dt.datetime.fromtimestamp(end_ms / 1000.0, UTC)
    out = []
    while d < e:
        out.append(d.strftime('%Y-%m'))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return out


def parse_archive_csv(text):
    """Binance archive kline CSV -> API-shaped rows [open ms, o, h, l, c, v, close ms, quote v, trades, ...]; header
    lines are skipped and microsecond stamps (newer archives) are converted to milliseconds."""
    rows = []
    for line in text.splitlines():
        p = line.strip().split(',')
        if len(p) < 9 or not p[0].strip().isdigit():
            continue
        t, tc = int(p[0]), int(p[6])
        if t > 10 ** 14:
            t, tc = t // 1000, tc // 1000
        rows.append([t, p[1], p[2], p[3], p[4], p[5], tc, p[7], int(p[8])] + p[9:12])
    return rows


def archive_klines(sym, raw, start_ms, end_ms, log):
    """Daily klines of a perp the API no longer serves ('Invalid symbol') from Binance's public archive
    (data.binance.vision monthly files). The zips are kept, unextracted, under raw/archive_klines/<symbol>/."""
    import io
    import urllib.error
    import urllib.request
    import zipfile
    d = Path(raw) / 'archive_klines' / sym
    rows, got = [], []
    for m in months_between(start_ms, end_ms):
        fn = d / ('%s-1d-%s.zip' % (sym, m))
        if not fn.exists():
            url = BN_ARCHIVE.format(s=sym, m=m)
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                    b = r.read()
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                raise
            finally:
                time.sleep(0.2)
            d.mkdir(parents=True, exist_ok=True)
            fn.write_bytes(b)
        with zipfile.ZipFile(io.BytesIO(fn.read_bytes())) as z:
            for name in z.namelist():
                rows += parse_archive_csv(z.read(name).decode('utf-8', 'replace'))
        got.append(m)
    seen = {}
    for x in rows:
        if start_ms <= x[0] < end_ms:
            seen[x[0]] = x
    log.setdefault('archive_klines', {})[sym] = {'months': got, 'rows': len(seen)}
    return [seen[k] for k in sorted(seen)]


def collect_binance(out, end_day=None):
    out = Path(out)
    raw = out / 'raw' / 'binance'
    raw.mkdir(parents=True, exist_ok=True)
    log = {'started': utc(), 'venue': 'binance'}
    end_ms = day_ms(end_day) if end_day else (int(time.time() * 1000) // DAY_MS) * DAY_MS
    start_ms = day_ms(FETCH_START)
    log['window'] = {'fetch_start': FETCH_START, 'end_exclusive': ymd(end_ms)}
    hf = bn_http(0.25)        # fapi market data (weight header watched)
    hfund = bn_http(0.7)      # fundingRate: its own 500 / 5 min / IP budget
    hs = bn_http(0.15)        # spot API, its own weight pool
    snap = {}
    for name, h, url in (('fapi_exchangeInfo', hf, BN_F + '/fapi/v1/exchangeInfo'),
                         ('fapi_fundingInfo', hf, BN_F + '/fapi/v1/fundingInfo'),
                         ('fapi_bookTicker', hf, BN_F + '/fapi/v1/ticker/bookTicker'),
                         ('fapi_ticker24hr', hf, BN_F + '/fapi/v1/ticker/24hr'),
                         ('spot_exchangeInfo', hs, BN_S + '/api/v3/exchangeInfo'),
                         ('spot_bookTicker', hs, BN_S + '/api/v3/ticker/bookTicker'),
                         ('spot_ticker24hr', hs, BN_S + '/api/v3/ticker/24hr')):
        fn = raw / (name + '.json.gz')
        if not fn.exists():
            r = h.get(url)
            if bad(r):
                raise RuntimeError('%s: %s' % (name, json.dumps(r)[:200]))
            write_gz(fn, {'fetched_at': utc(), 'url': url, 'data': r})
        snap[name] = read_gz(fn)['data']
    collect_funding_bulk(hfund, raw, start_ms, end_ms + 60_000, log)
    fund = load_funding_bulk(raw)
    uni = perp_universe(snap['fapi_exchangeInfo'], fund.keys())
    log['universe'] = {'perps': len(uni), 'by_status': dict(collections.Counter(v['status'] for v in uni.values())),
                       'funding_symbols': len(fund)}
    # perp daily klines, every symbol of the universe (one call each covers 1000 days)
    kd = raw / 'perp_klines'
    n_new = 0
    for i, sym in enumerate(sorted(uni)):
        fn = kd / ('%s.json.gz' % sym)
        if fn.exists():
            continue
        r = hf.get(BN_F + '/fapi/v1/klines', {'symbol': sym, 'interval': '1d', 'startTime': start_ms,
                                              'endTime': end_ms - 1, 'limit': 1000})
        write_gz(fn, r if isinstance(r, list) else {'error': r})
        n_new += 1
        if n_new % 100 == 0:
            print('perp klines: %d/%d' % (i + 1, len(uni)), flush=True)
    # perps the API refuses ('Invalid symbol': removed from exchangeInfo) come from the public archive
    for sym in sorted(uni):
        fn = kd / ('%s.json.gz' % sym)
        r = read_gz(fn)
        if isinstance(r, dict) and 'error' in r:
            rows = archive_klines(sym, raw, start_ms, end_ms, log)
            if rows:
                write_gz(fn, rows)
    # spot daily klines for every candidate pair of every perp base
    spot_syms = {s['symbol']: s for s in snap['spot_exchangeInfo'].get('symbols') or []}
    want = set()
    for sym, v in uni.items():
        for sp, _, _ in spot_candidates(v['base'], spot_syms):
            want.add(sp)
    sd = raw / 'spot_klines'
    n_new = 0
    for i, sp in enumerate(sorted(want)):
        fn = sd / ('%s.json.gz' % sp)
        if fn.exists():
            continue
        r = hs.get(BN_S + '/api/v3/klines', {'symbol': sp, 'interval': '1d', 'startTime': start_ms,
                                             'endTime': end_ms - 1, 'limit': 1000})
        write_gz(fn, r if isinstance(r, list) else {'error': r})
        n_new += 1
        if n_new % 100 == 0:
            print('spot klines: %d/%d' % (i + 1, len(want)), flush=True)
    log['spot_pairs_fetched'] = len(want)
    log['http'] = {'fapi': hf.stats(), 'funding': hfund.stats(), 'spot': hs.stats()}
    log['finished'] = utc()
    write_json(out / 'raw' / 'manifest_binance.json', collect_manifest(out, log))
    return log


BY = 'https://api.bybit.com'


def by_http():
    import funding_arb as FA
    return FA.Http(interval=0.06, backoff_429=10.0)


def by_list(r):
    return ((r or {}).get('result') or {}).get('list') or [] if isinstance(r, dict) and r.get('retCode') == 0 else None


def collect_bybit(out, end_day=None):
    """Bybit linear perps (Trading and Closed, i.e. delisted, paged), per-symbol funding history paged backward 200 at a
    time, daily perp and spot klines, and tickers for the spread model. Resumable per file."""
    out = Path(out)
    raw = out / 'raw' / 'bybit'
    raw.mkdir(parents=True, exist_ok=True)
    log = {'started': utc(), 'venue': 'bybit'}
    end_ms = day_ms(end_day) if end_day else (int(time.time() * 1000) // DAY_MS) * DAY_MS
    start_ms = day_ms(FETCH_START)
    log['window'] = {'fetch_start': FETCH_START, 'end_exclusive': ymd(end_ms)}
    h = by_http()
    inst = {}
    for cat, status in (('linear', None), ('linear', 'Closed'), ('spot', None), ('spot', 'Closed')):
        fn = raw / ('instruments_%s_%s.json.gz' % (cat, status or 'Trading'))
        if not fn.exists():
            pages, cursor = [], None
            for _ in range(30):
                q = {'category': cat, 'limit': 1000}
                if status:
                    q['status'] = status
                if cursor:
                    q['cursor'] = cursor
                r = h.get(BY + '/v5/market/instruments-info', q)
                pages.append(r)
                cursor = ((r or {}).get('result') or {}).get('nextPageCursor') if isinstance(r, dict) else None
                if not cursor:
                    break
            write_gz(fn, {'fetched_at': utc(), 'pages': pages})
        inst[(cat, status or 'Trading')] = [x for p in read_gz(fn)['pages'] for x in (by_list(p) or [])]
    for cat in ('linear', 'spot'):
        fn = raw / ('tickers_%s.json.gz' % cat)
        if not fn.exists():
            write_gz(fn, {'fetched_at': utc(), 'data': h.get(BY + '/v5/market/tickers', {'category': cat})})
    perps = {}
    for key in (('linear', 'Trading'), ('linear', 'Closed')):
        for x in inst[key]:
            if x.get('contractType') != 'LinearPerpetual' or x.get('quoteCoin') != 'USDT' or \
                    x.get('settleCoin') != 'USDT':
                continue
            launch, dlv = fnum(x.get('launchTime'), 0), fnum(x.get('deliveryTime'), 0)
            if launch and launch >= end_ms:
                continue
            if key[1] == 'Closed' and dlv and dlv < start_ms:
                continue
            perps[x['symbol']] = x
    spot_syms = {x['symbol']: x for k in (('spot', 'Trading'), ('spot', 'Closed')) for x in inst[k]}
    log['universe'] = {'perps': len(perps), 'by_status': dict(collections.Counter(x.get('status') for x in perps.values())),
                       'spot_pairs_listed': len(spot_syms)}
    fd = raw / 'funding'
    import concurrent.futures as cf

    def funding_job(sym):       # threads share one paced limiter (latency, not the 600 / 5 s limit, is the bound)
        fn = fd / ('%s.json.gz' % sym)
        pages, e = [], end_ms + 60_000
        for _ in range(400):
            r = h.get(BY + '/v5/market/funding/history', {'category': 'linear', 'symbol': sym, 'endTime': e,
                                                          'limit': 200})
            L = by_list(r)
            pages.append(r)
            if not L:
                break
            oldest = min(int(x['fundingRateTimestamp']) for x in L)
            if oldest <= start_ms or len(L) < 200:
                break
            e = oldest - 1
        write_gz(fn, pages)

    todo = [s_ for s_ in sorted(perps) if not (fd / ('%s.json.gz' % s_)).exists()]
    with cf.ThreadPoolExecutor(max_workers=8) as ex_:
        for i, _ in enumerate(ex_.map(funding_job, todo)):
            if (i + 1) % 100 == 0:
                print('bybit funding: %d/%d' % (i + 1, len(todo)), flush=True)
    kd = raw / 'perp_klines'

    def kline_job(args_):
        cat, sym, fn = args_
        write_gz(fn, h.get(BY + '/v5/market/kline', {'category': cat, 'symbol': sym, 'interval': 'D',
                                                     'start': start_ms, 'end': end_ms - 1, 'limit': 1000}))

    jobs = [('linear', s_, kd / ('%s.json.gz' % s_)) for s_ in sorted(perps)]
    with cf.ThreadPoolExecutor(max_workers=8) as ex_:
        list(ex_.map(kline_job, [j for j in jobs if not j[2].exists()]))
    want = set()        # delisted spot pairs are not listable on Bybit but their klines are served by symbol
    for sym, x in perps.items():
        base = x.get('baseCoin') or sym[:-4]
        want.update(sp for sp, _, _ in spot_candidates(base, None, ('USDT',)))
        want.update(sp for sp, _, _ in spot_candidates(base, spot_syms, ('USDC',)))
    sd = raw / 'spot_klines'
    jobs = [('spot', sp, sd / ('%s.json.gz' % sp)) for sp in sorted(want)]
    with cf.ThreadPoolExecutor(max_workers=8) as ex_:
        list(ex_.map(kline_job, [j for j in jobs if not j[2].exists()]))
    log['spot_pairs_fetched'] = len(want)
    log['http'] = {'bybit': h.stats()}
    log['finished'] = utc()
    man = collect_manifest(out, log)
    man['endpoints'] = {'instruments': BY + '/v5/market/instruments-info?category=linear|spot[&status=Closed]',
                        'funding': BY + '/v5/market/funding/history?category=linear&symbol&endTime&limit=200 (backward)',
                        'klines': BY + '/v5/market/kline?category=linear|spot&symbol&interval=D&start&end&limit=1000',
                        'tickers': BY + '/v5/market/tickers?category=linear|spot'}
    write_json(out / 'raw' / 'manifest_bybit.json', man)
    return log


def collect_manifest(out, log):
    raw = Path(out) / 'raw'
    files = []
    for fn in sorted(raw.rglob('*.json.gz')):
        files.append({'path': str(fn.relative_to(out)), 'bytes': fn.stat().st_size})
    by_dir = collections.Counter(str(Path(f['path']).parent) for f in files)
    return {'log': log, 'n_files': len(files), 'bytes': sum(f['bytes'] for f in files), 'files_by_dir': dict(by_dir),
            'endpoints': {
                'funding': BN_F + '/fapi/v1/fundingRate?startTime&endTime&limit=1000 (no symbol: all symbols, time order)',
                'perp_klines': BN_F + '/fapi/v1/klines?symbol&interval=1d&startTime&endTime&limit=1000',
                'spot_klines': BN_S + '/api/v3/klines?symbol&interval=1d&startTime&endTime&limit=1000',
                'perp_klines_archive': BN_ARCHIVE + ' (only for perps the API answers Invalid symbol; zips kept in '
                                       'raw/binance/archive_klines/)',
                'snapshots': 'fapi exchangeInfo, fundingInfo, ticker/bookTicker, ticker/24hr; spot exchangeInfo, '
                             'ticker/bookTicker, ticker/24hr'}}


# ---------------------------------------------------------------------------------------------- funding arithmetic (tested)

STD_HOURS = (1, 2, 4, 8)        # Binance USD-M settlement intervals (2 h exists: its modal print is 0.0025%, the floor)


def day_of(ms):
    """Funding day d whose window (d 00:00, d+1 00:00] holds a settlement stamped at ms (stamps are rounded to the
    hour first: Binance stamps a few milliseconds after the hour). Same convention as term_carry.day_of."""
    h = int(round(ms / HOUR_MS)) * HOUR_MS
    return (h - 1) // DAY_MS


def settlement_hours(stamps, std=STD_HOURS):
    """Hours each settlement covers, from the gaps between consecutive stamps (ms, ascending). A gap equal to a
    standard interval is the interval (so 8 h -> 4 h -> 1 h switches are followed settlement by settlement); a gap
    that is not (a halt, a missing print, the first settlement) takes the next gap if that one is standard, else the
    gap clamped to [1, 8]."""
    n = len(stamps)
    gaps = [None] + [int(round((stamps[i] - stamps[i - 1]) / HOUR_MS)) for i in range(1, n)]
    out = []
    for i in range(n):
        g = gaps[i]
        if g in std:
            out.append(g)
            continue
        nxt = gaps[i + 1] if i + 1 < n else None
        if nxt in std:
            out.append(nxt)
        elif g is not None and g >= 1:
            out.append(min(g, MAX_GAP_H))
        else:
            out.append(MAX_GAP_H)
    return out


def floor_rate(hours):
    """The interest leg for a settlement covering `hours`: 0.01% per 8 h pro rata (4 h: 0.005%, 1 h: 0.00125%)."""
    return INTEREST_8H * hours / 8.0


def is_floor(rate, hours, tol=FLOOR_TOL):
    return rate is not None and abs(rate - floor_rate(hours)) <= tol


def rate_8h(rate, hours):
    """A settlement restated per 8 h, the unit of the spike screen."""
    return rate * 8.0 / hours


def kline_days(rows):
    """{day: (close, quote volume)} of the traded bars only: quote volume > 0 and at least one trade. Binance serves a
    delisted perp as flat zero-volume bars for months, and those are not prices anyone could trade at."""
    out = {}
    if not isinstance(rows, list):
        return out
    for x in rows:
        qv = fnum(x[7], 0.0) or 0.0
        n = int(x[8]) if len(x) > 8 and x[8] is not None else 1
        c = fnum(x[4])
        if qv > 0 and n > 0 and c and c > 0:
            out[int(x[0]) // DAY_MS] = (c, qv)
    return out


def clean_funding(events, traded_days, delivery_ms=None):
    """Real settlements of one perp as [(ms, rate, mark, hours, day)], and how many were dropped. A settlement is kept
    only if the perp traded on its funding day and it is not after the contract's delivery (delisting) time: Binance
    keeps stamping phantom settlements at exactly the floor, with a frozen mark, for months after a delisting (FTMUSDT,
    delisted 2025-01-06, still 'paid' 0.01% every 8 h in February), which would read as a perfect floor coin."""
    kept, dropped = [], 0
    for t, r, m in events:
        d = day_of(t)
        if r is None or d not in traded_days or (delivery_ms and t > delivery_ms + 60_000):
            dropped += 1
            continue
        kept.append((t, r, m, d))
    hrs = settlement_hours([k[0] for k in kept])
    return [(t, r, m, h, d) for (t, r, m, d), h in zip(kept, hrs)], dropped


def capital_per_short(c, im, rally=STRESS_RALLY):
    """The collateral watcher's K (collateral_watch.capital_per_short): the spot plus the cash that keeps the short's
    initial margin covered after `rally` without a top-up, K = 1 + max(0, im + R - c(1+R)); c None or 0 -> 1 + im + R
    (the spot is not collateral and the short is margined in cash for the same stress)."""
    c = c or 0.0
    return 1.0 + max(0.0, im + rally - c * (1.0 + rally))


# ---------------------------------------------------------------------------------------------- costs (tested)

def spread_table(book, t24, quote='USDT', status=None, buckets=(0, 5e5, 2e6, 5e6, 1e7, 3e7, 1e8)):
    """Half-spread in bp by 24 h quote-volume bucket from today's book tickers: the 75th percentile of each bucket
    (spreads are mostly tick-bound, so volume explains little of them; a high percentile keeps the model honest for
    names whose tick is coarse), made non-increasing in volume. Returns [(volume floor, half-spread bp, n)]."""
    vol = {x['symbol']: fnum(x.get('quoteVolume'), 0.0) for x in t24}
    rows = []
    for x in book:
        s = x['symbol']
        if not s.endswith(quote) or (status is not None and s not in status):
            continue
        b, a = fnum(x.get('bidPrice')), fnum(x.get('askPrice'))
        v = vol.get(s) or 0.0
        if b and a and a >= b and v > 0:
            rows.append((v, (a - b) / (a + b) * 1e4))
    out = []
    for i, lo in enumerate(buckets):
        hi = buckets[i + 1] if i + 1 < len(buckets) else float('inf')
        hs = sorted(h for v, h in rows if lo <= v < hi)
        if hs:
            out.append([lo, hs[min(len(hs) - 1, int(0.75 * len(hs)))], len(hs)])
    for i in range(len(out) - 2, -1, -1):          # a thinner bucket never quotes tighter than a deeper one
        out[i][1] = max(out[i][1], out[i + 1][1])
    return out


def half_spread_bp(table, vol, tick_bp=0.0):
    hs = table[0][1] if table else 5.0
    for lo, h, _ in table:
        if vol >= lo:
            hs = h
    return max(hs, tick_bp)


def impact_frac(trade_usd, vol_usd, sigma, Y, days=ENTRY_DAYS):
    """Square-root impact of building (or unwinding) `trade_usd` over `days` equal daily slices: Y x sigma_daily x
    sqrt(slice / daily volume), as a fraction of the traded notional."""
    if not trade_usd or not Y or not vol_usd or vol_usd <= 0 or not sigma:
        return 0.0
    return Y * sigma * math.sqrt(trade_usd / days / vol_usd)


# ---------------------------------------------------------------------------------------------- normalise

VENUE_FEES_BP = {'binance': {'spot': 10.0, 'perp': 5.0}, 'bybit': {'spot': 10.0, 'perp': 5.5}}   # VIP0 taker
DELISTED_STATUS = {'binance': 'SETTLING', 'bybit': 'Closed'}


def collateral_ratios(venue='binance', path=COLLATERAL_SNAPSHOT, prices=None):
    """Today's collateral ratios {asset: c} from the watcher's snapshot (no history of the lists exists): Binance's
    classic portfolio-margin rate (the program the watcher prices first), Bybit's UTA tiers read at a $1M holding
    (tiers are in units of the coin; today's spot price converts), as the watcher does."""
    snap = read_gz(path)
    out = {}
    for r in snap['rows']:
        if r['venue'] != venue or not (r.get('ratio') or 0) > 0:
            continue
        if venue == 'binance' and r['program'] == 'portfolio_margin':
            out[r['asset']] = r['ratio']
        elif venue == 'bybit' and r['program'] == 'uta':
            px = (prices or {}).get(r['asset'])
            if r.get('tiers') and px:
                import collateral_watch as CW
                out[r['asset']] = CW.ratio_at(r['tiers'], 1e6 / px)
            else:
                out[r['asset']] = r['ratio']
    return out, snap.get('date')


def tick_of(sym_info):
    for f in sym_info.get('filters') or []:
        if f.get('filterType') == 'PRICE_FILTER':
            return fnum(f.get('tickSize'))
    return None


def read_or(fn, default):
    fn = Path(fn)
    return read_gz(fn) if fn.exists() else default


def kline_days_bybit(resp):
    """Bybit kline response -> {day: (close, quote turnover)} of traded bars (rows come newest first)."""
    rows = by_list(resp) if isinstance(resp, dict) else None
    out = {}
    for x in rows or []:
        c, qv = fnum(x[4]), fnum(x[6], 0.0) if len(x) > 6 else 0.0
        if c and c > 0 and qv and qv > 0:
            out[int(x[0]) // DAY_MS] = (c, qv)
    return out


def venue_inputs(out, venue):
    """Everything build_coins needs from one venue's raw files, in one shape."""
    out = Path(out)
    raw = out / 'raw' / venue
    man = json.loads((out / 'raw' / ('manifest_%s.json' % venue)).read_text())
    end_ms = day_ms(man['log']['window']['end_exclusive'])
    if venue == 'binance':
        fex = read_gz(raw / 'fapi_exchangeInfo.json.gz')['data']
        sex = read_gz(raw / 'spot_exchangeInfo.json.gz')['data']
        fund = load_funding_bulk(raw)
        uni = perp_universe(fex, fund.keys())
        ptick = {s['symbol']: tick_of(s) for s in fex.get('symbols') or []}
        for sym in uni:
            uni[sym]['tick'] = ptick.get(sym)
        spot_meta = {s['symbol']: {'base': s.get('baseAsset'), 'status': s.get('status'), 'tick': tick_of(s)}
                     for s in sex.get('symbols') or []}
        s_trading = {k for k, v in spot_meta.items() if v['status'] == 'TRADING'}
        f_trading = {s['symbol'] for s in fex['symbols'] if s.get('status') == 'TRADING' and
                     s.get('contractType') == 'PERPETUAL'}
        st = spread_table(read_gz(raw / 'spot_bookTicker.json.gz')['data'],
                          read_gz(raw / 'spot_ticker24hr.json.gz')['data'], status=s_trading)
        pt = spread_table(read_gz(raw / 'fapi_bookTicker.json.gz')['data'],
                          read_gz(raw / 'fapi_ticker24hr.json.gz')['data'], status=f_trading)
        coll, cday = collateral_ratios('binance')
        return {'venue': venue, 'end_ms': end_ms, 'uni': uni, 'funding': fund, 'spot_meta': spot_meta,
                'perp_bars': lambda sym: kline_days(read_or(raw / 'perp_klines' / ('%s.json.gz' % sym), [])),
                'spot_bars': lambda sp: kline_days(read_or(raw / 'spot_klines' / ('%s.json.gz' % sp), [])),
                'cands': lambda base: spot_candidates(base, spot_meta), 'collateral': coll, 'collateral_day': cday,
                'spread': (st, pt), 'fees': VENUE_FEES_BP[venue], 'manifest': man}
    if venue == 'bybit':
        inst = {}
        for cat, status in (('linear', 'Trading'), ('linear', 'Closed'), ('spot', 'Trading')):
            pages = read_gz(raw / ('instruments_%s_%s.json.gz' % (cat, status)))['pages']
            inst[(cat, status)] = [x for p in pages for x in (by_list(p) or [])]
        uni = {}
        for key in (('linear', 'Trading'), ('linear', 'Closed')):
            for x in inst[key]:
                fn = raw / 'funding' / ('%s.json.gz' % x['symbol'])
                if x.get('contractType') != 'LinearPerpetual' or x.get('quoteCoin') != 'USDT' or not fn.exists():
                    continue
                ml = fnum((x.get('leverageFilter') or {}).get('maxLeverage'))
                uni[x['symbol']] = {'base': x.get('baseCoin'), 'status': x.get('status'), 'source': 'instruments',
                                    'onboard_ms': fnum(x.get('launchTime')),
                                    'delivery_ms': fnum(x.get('deliveryTime')) or None, 'max_lev': ml,
                                    'tick': fnum((x.get('priceFilter') or {}).get('tickSize'))}
        fund = {}
        for sym in uni:
            ev = {}
            for p in read_gz(raw / 'funding' / ('%s.json.gz' % sym)):
                for x in by_list(p) or []:
                    ev[int(x['fundingRateTimestamp'])] = fnum(x.get('fundingRate'))
            fund[sym] = sorted((t, r, None) for t, r in ev.items())
        listed = {x['symbol']: {'base': x.get('baseCoin'), 'status': x.get('status'),
                                'tick': fnum((x.get('priceFilter') or {}).get('tickSize'))}
                  for x in inst[('spot', 'Trading')]}

        def cands(base):
            out_ = spot_candidates(base, None, ('USDT',)) + spot_candidates(base, listed, ('USDC',))
            return [c for c in out_ if (raw / 'spot_klines' / ('%s.json.gz' % c[0])).exists()]
        spot_meta = collections.defaultdict(lambda: {'base': None, 'status': 'unlisted (delisted or never)',
                                                     'tick': None})
        spot_meta.update(listed)
        tk = {c: (by_list(read_gz(raw / ('tickers_%s.json.gz' % c))['data']) or []) for c in ('spot', 'linear')}
        conv = lambda L: ([{'symbol': x['symbol'], 'bidPrice': x.get('bid1Price'), 'askPrice': x.get('ask1Price')}  # noqa: E731
                           for x in L], [{'symbol': x['symbol'], 'quoteVolume': x.get('turnover24h')} for x in L])
        st = spread_table(*conv(tk['spot']))
        pt = spread_table(*conv([x for x in tk['linear'] if x['symbol'] in uni and uni[x['symbol']]['status'] ==
                                 'Trading']))
        prices = {x['symbol'][:-4]: fnum(x.get('lastPrice')) for x in tk['spot'] if x['symbol'].endswith('USDT')}
        coll, cday = collateral_ratios('bybit', prices=prices)
        return {'venue': venue, 'end_ms': end_ms, 'uni': uni, 'funding': fund, 'spot_meta': spot_meta,
                'perp_bars': lambda sym: kline_days_bybit(read_or(raw / 'perp_klines' / ('%s.json.gz' % sym), {})),
                'spot_bars': lambda sp: kline_days_bybit(read_or(raw / 'spot_klines' / ('%s.json.gz' % sp), {})),
                'cands': cands, 'collateral': coll, 'collateral_day': cday, 'spread': (st, pt),
                'fees': VENUE_FEES_BP[venue], 'manifest': man}
    raise ValueError(venue)


def build_coins(vi):
    """Per perp: traded daily bars of both legs (spot in perp units: close x multiplier), real settlements by funding
    day, delisting days, today's collateral ratio and im. Returns (coins, report, last day)."""
    end_ms = vi['end_ms']
    last_day = end_ms // DAY_MS - 1
    uni, fund, spot_meta, coll = vi['uni'], vi['funding'], vi['spot_meta'], vi['collateral']
    rep = collections.Counter()
    rep_lists = collections.defaultdict(list)
    coins = {}
    for sym, info in sorted(uni.items()):
        pdays = {d: v for d, v in vi['perp_bars'](sym).items() if d <= last_day}
        if not pdays:
            rep['no_traded_perp_bar_in_window'] += 1
            ghost = [t for t, _, _ in fund.get(sym, []) if day_ms(FETCH_START) // DAY_MS <= day_of(t) <= last_day]
            if ghost:
                rep['perps_never_traded_but_settling'] += 1
                rep['settlements_of_never_traded_perps'] += len(ghost)
            continue
        rep['perps_traded_in_window'] += 1
        rep['perps_traded_in_window_' + str(info['status'])] += 1
        if info['base'] in EXCLUDE_BASES:
            rep['excluded_base'] += 1
            continue
        dlv = info['delivery_ms'] if (info['status'] == DELISTED_STATUS[vi['venue']] and info['delivery_ms']
                                      and info['delivery_ms'] < end_ms) else None
        ev, dropped = clean_funding(fund.get(sym, []), pdays, dlv)
        rep['settlements_raw'] += len(fund.get(sym, []))
        rep['settlements_kept'] += len(ev)
        rep['settlements_dropped'] += dropped
        rep['settlements_after_last_trade'] += sum(1 for t, _, _ in fund.get(sym, [])
                                                   if t > (max(pdays) + 1) * DAY_MS + 60_000)
        rep['settlements_before_first_trade'] += sum(1 for t, _, _ in fund.get(sym, []) if day_of(t) < min(pdays))
        spot, tried = None, []
        for sp, sb, mult in vi['cands'](info['base']):
            sdays = {d: v for d, v in vi['spot_bars'](sp).items() if d <= last_day}
            ov = [d for d in pdays if d in sdays]
            tried.append(sp)
            if len(ov) < 30:
                continue
            ratios = sorted(pdays[d][0] / (sdays[d][0] * mult) for d in ov)
            med = ratios[len(ratios) // 2]
            if abs(med - 1.0) <= IDENTITY_BAND:
                spot = (sp, spot_meta[sp].get('base') or sb, mult, sdays, med)
                break
        if spot is None:
            rep['no_spot_match'] += 1
            cause = 'no_spot_data'
            for sp, sb, mult in vi['cands'](info['base']):
                sdays = vi['spot_bars'](sp)
                ov = [d for d in pdays if d in sdays]
                if sdays and len(ov) < 30 and cause == 'no_spot_data':
                    cause = 'overlap_under_30d'
                elif len(ov) >= 30:
                    cause = 'identity_mismatch'
                    rep_lists['identity_mismatch'].append('%s~%s' % (sym, sp))
            rep['no_spot_match_' + cause] += 1
            continue
        sp, sb, mult, sdays, med = spot
        if sb in EXCLUDE_BASES:
            rep['excluded_base'] += 1
            continue
        max_lev = info.get('max_lev')
        im = max(1.0 / TARGET_LEV, 1.0 / max_lev) if max_lev else 1.0 / TARGET_LEV
        fd = collections.defaultdict(list)
        for t, r, m, h, d in ev:
            fd[d].append((t, r, m, h))
        lp, ls = max(pdays), max(sdays)
        coins[sym] = {
            'sym': sym, 'base': info['base'], 'status': info['status'], 'source': info['source'],
            'spot': sp, 'spot_base': sb, 'spot_status': spot_meta[sp].get('status'), 'mult': mult,
            'identity_median': med,
            'pc': {d: v[0] for d, v in pdays.items()}, 'pv': {d: v[1] for d, v in pdays.items()},
            'sc': {d: v[0] * mult for d, v in sdays.items()}, 'sv': {d: v[1] for d, v in sdays.items()},
            'fd': dict(fd), 'first_p': min(pdays), 'last_p': lp, 'first_s': min(sdays), 'last_s': ls,
            'delist_p': lp if lp < last_day - 1 else None, 'delist_s': ls if ls < last_day - 1 else None,
            'c': coll.get(sb), 'im': im, 'max_lev': max_lev, 'tick_p': info.get('tick'),
            'tick_s': spot_meta[sp].get('tick'), 'dropped_settlements': dropped}
        rep['coins_with_spot'] += 1
        if coins[sym]['c']:
            rep['coins_collateral_today'] += 1
        if coins[sym]['delist_p'] or coins[sym]['delist_s']:
            rep['coins_delisted_in_window'] += 1
            if coins[sym]['delist_p']:
                rep['coins_perp_delisted'] += 1
            if coins[sym]['delist_s']:
                rep['coins_spot_delisted'] += 1
    rep = dict(rep)
    rep['last_day'] = dname(last_day)
    rep['collateral_snapshot_day'] = vi['collateral_day']
    rep['collateral_assets_today'] = len(coll)
    rep['funding_symbols'] = len(fund)
    rep['universe_by_status'] = dict(collections.Counter(str(v['status']) for v in uni.values()))
    rep['universe_perps'] = len(uni)
    rep['identity_mismatch'] = sorted(rep_lists['identity_mismatch'])
    return coins, rep, last_day


# ---------------------------------------------------------------------------------------------- the rule (tested)

def features(coin, d, lookback=LOOKBACK):
    """What the rule may know at the start of day d: funding days and bars d-lookback .. d-1, nothing later."""
    d0, d1 = d - lookback, d - 1
    sets = [s for x in range(d0, d1 + 1) for s in coin['fd'].get(x, ())]
    n = len(sets)
    hours = sum(s[3] for s in sets)
    nf = sum(1 for s in sets if is_floor(s[1], s[3]))
    tot = sum(s[1] for s in sets)
    sv = [coin['sv'].get(x, 0.0) for x in range(d0, d1 + 1)]
    pv = [coin['pv'].get(x, 0.0) for x in range(d0, d1 + 1)]
    rets = []
    for x in range(d0 + 1, d1 + 1):
        a, b = coin['sc'].get(x - 1), coin['sc'].get(x)
        if a and b:
            rets.append(math.log(b / a))
    sigma = statistics.pstdev(rets) if len(rets) >= 10 else None
    F, S = coin['pc'].get(d1), coin['sc'].get(d1)
    ident = (F / S - 1.0) if (F and S) else None
    cov = hours / (24.0 * lookback)
    ok = bool(n and cov >= MIN_COVERAGE and coin['first_p'] <= d0 and sum(1 for v in sv if v > 0) >= MIN_SPOT_DAYS
              and ident is not None and abs(ident) <= IDENTITY_BAND and sigma is not None)
    return {'n': n, 'floor_share': nf / n if n else 0.0, 'apr': tot * 365.0 / (hours / 24.0) if hours else 0.0,
            'min_rate_8h': min((rate_8h(s[1], s[3]) for s in sets), default=0.0), 'coverage': cov,
            'spot_vol': statistics.median(sv), 'perp_vol': statistics.median(pv), 'sigma': sigma,
            'F': F, 'S': S, 'identity': ident, 'eligible': ok}


def forward_stats(coin, d, horizon=28):
    """Realised funding over funding days d .. d+horizon-1 (what a position entered at the start of day d earns):
    floor share, APR, and whether any settlement fell below the spike threshold."""
    sets = [s for x in range(d, d + horizon) for s in coin['fd'].get(x, ())]
    hours = sum(s[3] for s in sets)
    if not sets or hours < 0.8 * 24 * horizon:
        return None
    return {'floor_share': sum(1 for s in sets if is_floor(s[1], s[3])) / len(sets),
            'apr': sum(s[1] for s in sets) * 365.0 / (hours / 24.0),
            'spike': any(rate_8h(s[1], s[3]) < SPIKE_8H for s in sets)}


def persistence_table(coins, feats, members, edges=(0.0, 0.25, 0.5, 0.75, 0.9, 1.0001), horizon=28):
    """Does floor persistence persist? Eligible members bucketed by trailing floor share at each rebalance day, with
    the next `horizon` days' realised floor share, funding APR and spike frequency (all rebalance days pooled)."""
    acc = collections.defaultdict(list)
    for d, f in feats.items():
        for s, x in f.items():
            if s not in members or not x['eligible']:
                continue
            fw = forward_stats(coins[s], d, horizon)
            if fw is None:
                continue
            for i in range(len(edges) - 1):
                if edges[i] <= x['floor_share'] < edges[i + 1]:
                    acc[i].append((x, fw))
    out = []
    for i in range(len(edges) - 1):
        rows = acc.get(i, [])
        if not rows:
            continue
        out.append({'trailing_floor_share': '[%.2f, %.2f)' % (edges[i], min(edges[i + 1], 1.0)), 'n': len(rows),
                    'trailing_apr_mean': statistics.fmean(x['apr'] for x, _ in rows),
                    'next_floor_share_mean': statistics.fmean(fw['floor_share'] for _, fw in rows),
                    'next_apr_mean': statistics.fmean(fw['apr'] for _, fw in rows),
                    'next_apr_median': statistics.median(fw['apr'] for _, fw in rows),
                    'next_apr_p10': sorted(fw['apr'] for _, fw in rows)[len(rows) // 10],
                    'next_spike_share': sum(1 for _, fw in rows if fw['spike']) / len(rows)})
    return out


def select(feats, variant, members):
    """Names to hold from the start of a day: eligible members that pass the screens, ranked by floor share, then the
    trailing funding APR, then spot volume; at most one perp per spot coin; the first N. `members` maps a perp symbol
    to its spot coin. Returns (selected, number that qualified before the cut)."""
    th, spike, vmin = variant['floor_share_min'], variant['spike_8h'], variant['spot_vol_min_usd']
    cand = []
    for s, f in feats.items():
        if s not in members or not f['eligible'] or f['floor_share'] < th or f['spot_vol'] < vmin:
            continue
        if spike is not None and f['min_rate_8h'] < spike:
            continue
        cand.append(s)
    cand.sort(key=lambda s: (-feats[s]['floor_share'], -feats[s]['apr'], -feats[s]['spot_vol'], s))
    seen, out = set(), []
    for s in cand:
        if members[s] in seen:
            continue
        seen.add(members[s])
        if len(out) < variant['n_names']:
            out.append(s)
    return out, len(seen)


def variant_name(v):
    return 'R%d_F%d_S%s_V%dM_N%d' % (v['rebalance_days'], round(100 * v['floor_share_min']),
                                     'none' if v['spike_8h'] is None else 'm5bp',
                                     round(v['spot_vol_min_usd'] / 1e6), v['n_names'])


def grid_variants(grid=GRID):
    out = []
    for r in grid['rebalance_days']:
        for f in grid['floor_share_min']:
            for s in grid['spike_8h']:
                for v in grid['spot_vol_min_usd']:
                    for n in grid['n_names']:
                        x = {'rebalance_days': r, 'floor_share_min': f, 'spike_8h': s, 'spot_vol_min_usd': v,
                             'n_names': n}
                        x['name'] = variant_name(x)
                        out.append(x)
    return out


# ---------------------------------------------------------------------------------------------- the engine (tested)

class Costs:
    """One side of each leg as a fraction of the traded notional: taker fee + the half-spread model (+ square-root
    impact when the run has a size). `mult` scales fees and spreads (the cost-sensitivity rows)."""

    def __init__(self, spot_table, perp_table, aum=None, Y=0.0, mult=1.0, entry_days=ENTRY_DAYS, cap=True,
                 fees=None):
        self.st, self.pt, self.aum, self.Y, self.mult, self.days = spot_table, perp_table, aum, Y, mult, entry_days
        self.cap, self.fees = cap, fees or FEE_BP

    def legs(self, coin, f, trade):
        """(spot side, perp side, impact part of both) for trading `trade` (capital units) of this coin."""
        S, F = f.get('S') or 0.0, f.get('F') or 0.0
        tb_s = 0.5 * coin['tick_s'] * coin['mult'] / S * 1e4 if coin.get('tick_s') and S else 0.0
        tb_p = 0.5 * coin['tick_p'] / F * 1e4 if coin.get('tick_p') and F else 0.0
        cs = (self.fees['spot'] + half_spread_bp(self.st, f['spot_vol'], tb_s)) / 1e4 * self.mult
        cp = (self.fees['perp'] + half_spread_bp(self.pt, f['perp_vol'], tb_p)) / 1e4 * self.mult
        imp = 0.0
        if self.aum and self.Y:
            usd = trade * self.aum
            imp = impact_frac(usd, f['spot_vol'], f['sigma'], self.Y, self.days) + \
                impact_frac(usd, f['perp_vol'], f['sigma'], self.Y, self.days)
        return cs, cp, imp


def simulate(coins, feats_by_day, days, variant, members, K_of, bench, costs, record=False):
    """Day-by-day P&L of one variant on a constant capital of 1. Returns (daily excess over the benchmark, book).

    At a rebalance day d (every R days from days[0]) the selection sees features computed from days <= d-1, each
    selected name's target short notional is (1/N)/K (capped at PARTICIPATION x the smaller of its spot and perp
    30-day median volumes when the run has a size), and every position is traded from its current notional (fixed
    quantity x day d-1's perp close) to the target at day d-1's closes, paying one side of both legs on the change.
    A held position earns day d's settlements (rate x quantity x the settlement's mark) and the change in
    (spot x multiplier - perp) x quantity. It is closed at day d-1's closes with double costs when either leg has no
    traded bar on day d or day d is that leg's last traded day before a delisting; a rally beyond the stress rally
    since the last trade forces a rebalance of the drift. Capital a position uses is its target notional x K; the rest
    earns the benchmark (zero excess). Open positions are closed at the last day's closes with normal costs."""
    R = variant['rebalance_days']
    rebal = set(days[::R])
    last = days[-1]
    pos = {}
    ex = []
    bk = collections.Counter()
    held_days = []
    qual = []
    invested_path = []
    by_coin = collections.defaultdict(float) if record else None
    exits, books = [], []
    comp = {'funding': [], 'neg_funding': [], 'basis': [], 'costs': [], 'bench': []}
    for d in days:
        cost = imp_cost = 0.0
        if d in rebal:
            f = feats_by_day[d]
            sel, nq = select(f, variant, members)
            sel = [s for s in sel if (d - 1) in coins[s]['pc'] and (d - 1) in coins[s]['sc']]
            qual.append(nq)
            tgt = {}
            for s in sel:
                K = K_of(coins[s])
                n = (1.0 / variant['n_names']) / K
                if costs.aum and costs.cap:
                    capn = PARTICIPATION * min(f[s]['spot_vol'], f[s]['perp_vol']) / costs.aum
                    if capn < n:
                        bk['capped_name_rebalances'] += 1
                        n = capn
                bk['name_rebalances'] += 1
                tgt[s] = (n, K)
            for s in sorted(set(pos) | set(tgt)):
                c = coins[s]
                F = c['pc'][d - 1]
                cur = pos[s]['q'] * F if s in pos else 0.0
                new = tgt[s][0] if s in tgt else 0.0
                tr = abs(new - cur)
                if tr > 1e-12:
                    fs = f.get(s)
                    if not fs or fs.get('sigma') is None or not fs.get('S'):
                        fs = pos[s]['f']
                    cs, cp, imp = costs.legs(c, fs, tr)
                    cost += tr * (cs + cp + imp)
                    imp_cost += tr * imp
                    bk['turnover'] += tr
                    if record:
                        by_coin[s] -= tr * (cs + cp + imp)
                if s in tgt:
                    pos[s] = {'q': new / F, 'F_ref': F, 'n': new, 'cap': new * tgt[s][1], 'f': f.get(s) or pos[s]['f']}
                else:
                    pos.pop(s, None)
            if record:
                books.append((d, {s: (p['n'], p['f']) for s, p in pos.items()}))
        pnl = 0.0
        day_fund = day_neg = day_basis = 0.0
        for s in sorted(pos):
            c, p = coins[s], pos[s]
            gone = any(x is not None and d >= x for x in (c['delist_p'], c['delist_s']))
            if gone or d not in c['pc'] or d not in c['sc']:
                F = c['pc'][d - 1]
                tr = p['q'] * F
                cs, cp, imp = costs.legs(c, p['f'], tr)
                cost += 2.0 * tr * (cs + cp + imp)
                imp_cost += 2.0 * tr * imp
                bk['turnover'] += tr
                bk['forced_exits'] += 1
                bk['forced_exits_delisting' if gone else 'forced_exits_gap'] += 1
                if record:
                    by_coin[s] -= 2.0 * tr * (cs + cp + imp)
                    exits.append({'sym': s, 'day': dname(d), 'why': 'delisting' if gone else 'gap',
                                  'notional': tr})
                del pos[s]
                continue
            F0, F1, S0, S1 = c['pc'][d - 1], c['pc'][d], c['sc'][d - 1], c['sc'][d]
            fund = 0.0
            for t, r, m, h in c['fd'].get(d, ()):
                v = r * p['q'] * (m if m else F1)
                fund += v
                if r < 0:
                    bk['neg_funding'] += v
                else:
                    bk['pos_funding'] += v
                if is_floor(r, h):
                    bk['floor_funding'] += v
            basis = p['q'] * ((S1 - F1) - (S0 - F0))
            pnl += fund + basis
            day_fund += fund
            day_basis += basis
            day_neg += sum(r * p['q'] * (m if m else F1) for t, r, m, h in c['fd'].get(d, ()) if r < 0)
            bk['funding'] += fund
            bk['basis'] += basis
            if record:
                by_coin[s] += fund + basis
            if F1 / p['F_ref'] - 1.0 > STRESS_RALLY:
                tr = p['q'] * F1 - p['n']
                cs, cp, imp = costs.legs(c, p['f'], tr)
                cost += tr * (cs + cp + imp)
                imp_cost += tr * imp
                bk['turnover'] += tr
                bk['rally_rebalances'] += 1
                p['q'], p['F_ref'] = p['n'] / F1, F1
        if d == last:
            for s, p in pos.items():
                tr = p['q'] * coins[s]['pc'][d]
                cs, cp, imp = costs.legs(coins[s], p['f'], tr)
                cost += tr * (cs + cp + imp)
                imp_cost += tr * imp
                bk['turnover'] += tr
        inv = sum(p['cap'] for p in pos.values())
        b = bench(d)
        ex.append(pnl - cost - inv * b / 365.0)
        bk['costs'] += cost
        bk['impact'] += imp_cost
        bk['bench_on_invested'] += inv * b / 365.0
        held_days.append(len(pos))
        invested_path.append(inv)
        if record:
            comp['funding'].append(day_fund)
            comp['neg_funding'].append(day_neg)
            comp['basis'].append(day_basis)
            comp['costs'].append(cost)
            comp['bench'].append(inv * b / 365.0)
    out = dict(bk)
    for k in ('forced_exits', 'forced_exits_delisting', 'forced_exits_gap', 'rally_rebalances', 'name_rebalances',
              'capped_name_rebalances', 'turnover', 'funding', 'pos_funding', 'neg_funding', 'floor_funding', 'basis',
              'costs', 'impact', 'bench_on_invested'):
        out.setdefault(k, 0)
    out['mean_names_held'] = statistics.fmean(held_days) if held_days else 0.0
    out['mean_invested'] = statistics.fmean(invested_path) if invested_path else 0.0
    out['mean_qualified_at_rebalance'] = statistics.fmean(qual) if qual else 0.0
    out['min_qualified_at_rebalance'] = min(qual) if qual else 0
    out['rebalances'] = len(qual)
    if record:
        out['by_coin'] = dict(by_coin)
        out['exits'] = exits
        out['_books'] = books
        out['_comp'] = comp
        out['_held'] = held_days
        out['_invested'] = invested_path
    return ex, out


# ---------------------------------------------------------------------------------------------- analysis

def savings_path():
    """The savings rate actually paid each day (Maker's DSR, then the SSR from sUSDS's NAV; annual, continuously
    compounded), from term_carry.load_navs over the chain samples that study read."""
    import term_carry as TC
    return TC.load_navs(str(TERM_CARRY_OUT))['savings_path']


def preregistration():
    return {'written_at': utc(), 'grid': GRID, 'n_variants': len(grid_variants()),
            'variants': [v['name'] for v in grid_variants()], 'rank': RANK, 'baseline': BASELINE,
            'universe_main': 'Binance USD-M coin perps whose spot coin is on the 2026-10-11 classic portfolio-margin '
                             'list (c > 0), K from that ratio',
            'universe_robustness': 'every Binance USD-M coin perp with a same-venue spot market (delisted included), '
                                   'K at an assumed ratio (median c of the main universe)',
            'protocol': 'backtest.choose_then_test on daily excess, choose on the first half (Sharpe), test once on '
                        'the second; BH q=0.10 on full-sample Newey-West p; deflated Sharpe with 32 trials',
            'pass_rule': 'in_sample_positive and OOS HAC t > 2 and chosen in BH survivors and OOS excess > 0 at $3M',
            'costs': {'fee_bp': FEE_BP, 'half_spread': 'bucket p75 of 2026-10-11 book tickers by 24 h quote volume, '
                                                       'floored at half a tick', 'impact_Y': IMPACT_Y,
                      'impact_Y_stress': IMPACT_Y_STRESS, 'entry_days': ENTRY_DAYS, 'participation': PARTICIPATION},
            'benchmark': 'savings rate paid each day (term_carry.load_navs savings_path); constant 3.80% beside it',
            'window': {'pnl_start': PNL_START, 'fetch_start': FETCH_START}}


def cmd_grid(args):
    """Write the rule family into analysis.json before any return is computed (refuses to overwrite results)."""
    fn = Path(args.out) / 'analysis.json'
    if fn.exists():
        cur = json.loads(fn.read_text())
        if cur.get('results_written_at'):
            raise SystemExit('analysis.json already holds results; the grid is fixed')
    write_json(fn, {'preregistered': preregistration()})
    print('grid written:', fn, len(grid_variants()), 'variants')


def ann(xs):
    return (sum(xs) / len(xs) * 365.0) if xs else None


def perf_split(ex, c):
    full, ins, oos = B.perf(ex, 365), B.perf(ex[:c], 365), B.perf(ex[c:], 365)
    return {'full': full.get('ann_return'), 'in_sample': ins.get('ann_return'), 'out_of_sample': oos.get('ann_return'),
            'sharpe_full': full.get('sharpe'), 'sharpe_in': ins.get('sharpe'), 'sharpe_oos': oos.get('sharpe'),
            't_full': B.newey_west_t(ex)[0], 't_oos': B.newey_west_t(ex[c:])[0],
            't_oos_lag30': B.newey_west_t(ex[c:], lags=30)[0], 'mdd_full': full.get('max_drawdown')}


def tails(ex, days, bk, inv_bench):
    """Worst week, drawdown, concentration, the cost of negative settlements, turnover."""
    n = len(ex)
    years = n / 365.0
    roll7 = [sum(ex[i:i + 7]) for i in range(n - 6)]
    wi = min(range(len(roll7)), key=lambda i: roll7[i]) if roll7 else None
    cal = collections.defaultdict(float)
    for d, x in zip(days, ex):
        iso = dt.datetime.fromtimestamp(d * 86400, UTC).isocalendar()
        cal['%d-W%02d' % (iso[0], iso[1])] += x
    wc = min(cal, key=cal.get) if cal else None
    gross = [x + b for x, b in zip(ex, inv_bench)]           # return on capital before the benchmark
    k = max(1, int(math.ceil(0.01 * n)))
    tot, totg = sum(ex), sum(gross)
    top = sum(sorted(ex, reverse=True)[:k])
    topg = sum(sorted(gross, reverse=True)[:k])
    worst_days = sorted(range(n), key=lambda i: ex[i])[:5]
    return {
        'worst_rolling_week': roll7[wi] if roll7 else None,
        'worst_rolling_week_start': dname(days[wi]) if roll7 else None,
        'worst_calendar_week': cal[wc] if wc else None, 'worst_calendar_week_id': wc,
        'max_drawdown': B.max_drawdown(ex),
        'worst_days': [{'day': dname(days[i]), 'excess': ex[i]} for i in worst_days],
        'best_1pct_days_share_of_excess': (top / tot) if tot > 0 else None,
        'best_1pct_days_share_of_gross': (topg / totg) if totg > 0 else None,
        'best_1pct_days_n': k,
        'neg_funding_paid_per_year': -bk.get('neg_funding', 0.0) / years,
        'neg_funding_share_of_positive': (-bk.get('neg_funding', 0.0) / bk['pos_funding'])
        if bk.get('pos_funding') else None,
        'turnover_per_year': bk.get('turnover', 0.0) / years,
        'funding_per_year': bk.get('funding', 0.0) / years, 'basis_per_year': bk.get('basis', 0.0) / years,
        'costs_per_year': bk.get('costs', 0.0) / years, 'impact_per_year': bk.get('impact', 0.0) / years,
        'bench_on_invested_per_year': bk.get('bench_on_invested', 0.0) / years,
        'floor_funding_share': (bk.get('floor_funding', 0.0) / bk['pos_funding']) if bk.get('pos_funding') else None,
        'forced_exits': bk.get('forced_exits', 0), 'forced_exits_delisting': bk.get('forced_exits_delisting', 0),
        'forced_exits_gap': bk.get('forced_exits_gap', 0), 'rally_rebalances': bk.get('rally_rebalances', 0),
        'mean_names_held': bk.get('mean_names_held'), 'mean_invested': bk.get('mean_invested'),
        'mean_qualified_at_rebalance': bk.get('mean_qualified_at_rebalance'),
        'min_qualified_at_rebalance': bk.get('min_qualified_at_rebalance')}


def by_year(ex, days):
    out = collections.defaultdict(list)
    for d, x in zip(days, ex):
        y = dname(d)[:4]
        out[y].append(x)
    return {y: {'ann_excess': ann(v), 'days': len(v)} for y, v in sorted(out.items())}


def by_half_year(ex, days):
    out = collections.defaultdict(list)
    for d, x in zip(days, ex):
        s = dname(d)
        out['%sH%d' % (s[:4], 1 if int(s[5:7]) <= 6 else 2)].append(x)
    return {k: {'ann_excess': ann(v), 'days': len(v)} for k, v in sorted(out.items())}


def crash_exit_costs(books, coins, costs_obj, aum, Y=IMPACT_Y_STRESS, vol_mult=3.0):
    """One-day unwind of each rebalanced book (all positions, both legs, in one day) at the trailing volatility
    times `vol_mult` (a crash day) and Y: fraction of capital. Median and worst over rebalance days."""
    vals = []
    for d, book in books:
        tot = 0.0
        for s, (n, f) in book.items():
            c = coins[s]
            cs, cp, _ = costs_obj.legs(c, f, n)
            usd = n * aum
            sig = (f['sigma'] or 0.0) * vol_mult
            imp = impact_frac(usd, f['spot_vol'], sig, Y, 1) + impact_frac(usd, f['perp_vol'], sig, Y, 1)
            tot += n * (cs + cp + imp)
        vals.append((tot, d))
    if not vals:
        return {}
    xs = sorted(v for v, _ in vals)
    worst = max(vals)
    return {'median': statistics.median(xs), 'worst': worst[0], 'worst_day': dname(worst[1]), 'Y': Y,
            'vol_mult': vol_mult}


def run_family(coins, feats, days, members, K_of, bench, costs, variants):
    series, books = {}, {}
    for v in variants:
        ex, bk = simulate(coins, feats, days, v, members, K_of, bench, costs)
        series[v['name']], books[v['name']] = ex, bk
    ctt = B.choose_then_test(series, frac=SPLIT_FRAC, periods_per_year=365)
    return series, books, ctt


def bh_one_sided(series, q=0.10):
    """BH on one-sided p-values for 'mean daily excess > 0' (full-sample Newey-West). backtest.choose_then_test's BH
    uses two-sided p, under which a variant that loses significantly also 'survives'; the pass rule uses this one."""
    names = list(series)
    pv = []
    for k in names:
        t, p = B.newey_west_t(series[k])
        pv.append(None if t is None else (p / 2.0 if t > 0 else 1.0 - p / 2.0))
    rej, adj = B.bh(pv, q=q)
    return [k for k, r in zip(names, rej) if r], dict(zip(names, adj))


def family_table(series, books, ctt, c):
    rows = {}
    surv1, adj1 = bh_one_sided(series)
    for k, ex in series.items():
        r = perf_split(ex, c)
        bk = books[k]
        yrs = len(ex) / 365.0
        r.update({'bh_adj_p': adj1.get(k), 'bh_survivor': k in surv1,
                  'bh_adj_p_two_sided': ctt['bh_adjusted_p'].get(k),
                  'mean_names_held': bk.get('mean_names_held'), 'mean_invested': bk.get('mean_invested'),
                  'turnover_per_year': bk.get('turnover', 0.0) / yrs, 'forced_exits': bk.get('forced_exits', 0),
                  'neg_funding_per_year': -bk.get('neg_funding', 0.0) / yrs,
                  'mean_qualified': bk.get('mean_qualified_at_rebalance')})
        rows[k] = r
    return rows


def protocol_summary(ctt, n_variants, series=None):
    keep = ('chosen', 'n_variants', 'cutoff_index', 'in_sample_positive', 'oos_rank', 'oos_t', 'oos_p',
            'deflated_sharpe_in_sample', 'bh_survivors_full_sample')
    out = {k: ctt[k] for k in keep}
    out['bh_survivors_full_sample_two_sided'] = out.pop('bh_survivors_full_sample')
    out['bh_survivors_full_sample'] = bh_one_sided(series)[0] if series else None
    out['in_sample'] = {k: ctt['in_sample'].get(k) for k in ('ann_return', 'sharpe', 'max_drawdown', 'n')}
    out['out_of_sample'] = {k: ctt['out_of_sample'].get(k) for k in ('ann_return', 'sharpe', 'max_drawdown', 'n')}
    return out


def coin_attribution(bk, coins, top=12):
    items = sorted(bk.get('by_coin', {}).items(), key=lambda kv: kv[1])
    fmt = lambda kv: {'sym': kv[0], 'pnl': kv[1], 'status': coins[kv[0]]['status'], 'c': coins[kv[0]]['c']}
    return {'worst': [fmt(kv) for kv in items[:top]], 'best': [fmt(kv) for kv in items[::-1][:top]],
            'n_coins_traded': len(items)}


def analyze_venue(out, venue, sav):
    """Every result for one venue: the grid on the main (collateral) universe, the chosen variant in detail, the
    baseline, the all-spot robustness universe, sensitivities and capacity. Returns (result, daily series)."""
    t0 = time.time()
    vi = venue_inputs(out, venue)
    coins, rep, last_day = build_coins(vi)
    st, pt = vi['spread']
    fees = vi['fees']
    bench = lambda d: sav.get(d, SSR_CONST)                       # noqa: E731
    bench_const = lambda d: SSR_CONST                             # noqa: E731
    d0 = day_ms(PNL_START) // DAY_MS
    days = list(range(d0, last_day + 1))
    c_cut = B.cutoff_index(len(days), SPLIT_FRAC)
    # features at every 7-day rebalance day (the 28-day schedule is a subset), and one day stale for late entry
    reb = days[::min(GRID['rebalance_days'])]
    alive = lambda c, d: c['first_p'] <= d - LOOKBACK and c['last_p'] >= d - 1     # noqa: E731
    feats = {d: {s: features(c, d) for s, c in coins.items() if alive(c, d)} for d in reb}
    feats_late = {d: {s: features(c, d - 1) for s, c in coins.items() if alive(c, d - 1)} for d in reb}
    t_feat = time.time() - t0
    coll_members = {s: c['spot_base'] for s, c in coins.items() if c['c']}
    all_members = {s: c['spot_base'] for s, c in coins.items()}
    cs_main = sorted(coins[s]['c'] for s in coll_members)
    c_assumed = statistics.median(cs_main) if cs_main else 0.3
    K_main = lambda c: capital_per_short(c['c'], c['im'])          # noqa: E731
    K_assumed = lambda c: capital_per_short(c_assumed, c['im'])    # noqa: E731
    small = Costs(st, pt, fees=fees)
    variants = grid_variants()
    # ---- main family
    ser, bks, ctt = run_family(coins, feats, days, coll_members, K_main, bench, small, variants)
    chosen = ctt['chosen']
    vch = next(v for v in variants if v['name'] == chosen)
    ex_ch, bk_ch = simulate(coins, feats, days, vch, coll_members, K_main, bench, small, record=True)
    inv_b = [i * bench(d) / 365.0 for i, d in zip(bk_ch['_invested'], days)]
    # ---- baseline: always the top N by floor share (no floor threshold, no spike screen), chosen R
    base = {}
    for n in GRID['n_names']:
        vb = dict(BASELINE, rebalance_days=vch['rebalance_days'], n_names=n)
        vb['name'] = 'baseline_' + variant_name(vb)
        exb, bkb = simulate(coins, feats, days, vb, coll_members, K_main, bench, small, record=True)
        invb = [i * bench(d) / 365.0 for i, d in zip(bkb['_invested'], days)]
        base[vb['name']] = {'variant': vb, 'perf': perf_split(exb, c_cut), 'by_year': by_year(exb, days),
                            'tails': tails(exb, days, bkb, invb), 'attribution': coin_attribution(bkb, coins, 8),
                            'excess_per_invested_full': (sum(exb) / sum(bkb['_invested']) * 365.0)
                            if sum(bkb['_invested']) else None}
    # ---- robustness universe: every coin with a spot market, K at the assumed ratio
    ser_a, bks_a, ctt_a = run_family(coins, feats, days, all_members, K_assumed, bench, small, variants)
    ex_a_ch, bk_a_ch = simulate(coins, feats, days, vch, all_members, K_assumed, bench, small, record=True)
    ex_bridge, _ = simulate(coins, feats, days, vch, coll_members, K_assumed, bench, small)
    # ---- sensitivities of the chosen variant
    ex_c2, _ = simulate(coins, feats, days, vch, coll_members, K_main, bench, Costs(st, pt, mult=2.0, fees=fees))
    ex_const, _ = simulate(coins, feats, days, vch, coll_members, K_main, bench_const, small)
    ex_late, _ = simulate(coins, feats_late, days, vch, coll_members, K_main, bench, small)
    # ---- capacity
    cap = {}
    for A in SIZES:
        row = {}
        for label, Y, capon in (('base', IMPACT_Y, True), ('stress_Y1', IMPACT_Y_STRESS, True),
                                ('cap_only', 0.0, True), ('impact_only', IMPACT_Y, False)):
            co = Costs(st, pt, aum=A, Y=Y, cap=capon, fees=fees)
            exA, bkA = simulate(coins, feats, days, vch, coll_members, K_main, bench, co, record=(label == 'base'))
            r = perf_split(exA, c_cut)
            yrs = len(exA) / 365.0
            r.update({'usd_per_year_full': (r['full'] or 0.0) * A, 'usd_per_year_oos': (r['out_of_sample'] or 0.0) * A,
                      'mean_invested': bkA.get('mean_invested'), 'mean_names_held': bkA.get('mean_names_held'),
                      'capped_share': (bkA.get('capped_name_rebalances', 0) / bkA['name_rebalances'])
                      if bkA.get('name_rebalances') else None,
                      'impact_per_year': bkA.get('impact', 0.0) / yrs, 'costs_per_year': bkA.get('costs', 0.0) / yrs,
                      'turnover_per_year': bkA.get('turnover', 0.0) / yrs})
            if label == 'base':
                r['crash_exit'] = crash_exit_costs(bkA['_books'], coins, co, A)
                r['invested_oos'] = statistics.fmean(bkA['_invested'][c_cut:])
            row[label] = r
        exb3, _ = simulate(coins, feats, days, dict(BASELINE, rebalance_days=vch['rebalance_days'],
                                                    n_names=vch['n_names']), coll_members, K_main, bench,
                           Costs(st, pt, aum=A, Y=IMPACT_Y, fees=fees))
        row['baseline_base'] = perf_split(exb3, c_cut)
        cap[str(A)] = row
    # ---- plain facts about the universe on each rebalance day
    floor_counts = []
    for d in reb:
        f = feats[d]
        el = [s for s in f if f[s]['eligible'] and s in coll_members]
        floor_counts.append({'day': dname(d), 'eligible': len(el),
                             'floor50': sum(1 for s in el if f[s]['floor_share'] >= 0.5),
                             'floor50_v2m': sum(1 for s in el if f[s]['floor_share'] >= 0.5 and
                                                f[s]['spot_vol'] >= 2e6),
                             'floor50_v10m': sum(1 for s in el if f[s]['floor_share'] >= 0.5 and
                                                 f[s]['spot_vol'] >= 1e7)})
    fam = family_table(ser, bks, ctt, c_cut)
    fam_a = family_table(ser_a, bks_a, ctt_a, c_cut)
    liquid = {d: {s: x for s, x in f.items() if x['min_rate_8h'] >= SPIKE_8H and x['spot_vol'] >= 1e7}
              for d, f in feats.items()}
    persist = {'main_v10m_spike_screened': persistence_table(coins, liquid, coll_members),
               'main': persistence_table(coins, feats, coll_members),
               'all_spot': persistence_table(coins, feats, all_members),
               'main_spike_screened': persistence_table(
                   coins, {d: {s: x for s, x in f.items() if x['min_rate_8h'] >= SPIKE_8H} for d, f in feats.items()},
                   coll_members)}
    oos_ex = ex_ch[c_cut:]
    # ---- post hoc (not part of the protocol, nothing here selects anything): where does the loss come from?
    def per_invested(ex, inv, lo=0, hi=None):
        e, i = ex[lo:hi], inv[lo:hi]
        return (sum(e) / sum(i) * 365.0) if sum(i) > 0 else None

    def decomp(bk_, ex_, inv_, lo, hi):
        return {'excess': ann(ex_[lo:hi]), 'excess_per_invested': per_invested(ex_, inv_, lo, hi),
                'mean_invested': statistics.fmean(inv_[lo:hi])}
    def halves(bk_):
        """Each P&L component per year of capital and per year of capital deployed, in and out of sample."""
        cp_, inv_ = bk_['_comp'], bk_['_invested']
        out_ = {}
        for lab, lo, hi in (('in_sample', 0, c_cut), ('out_of_sample', c_cut, len(days))):
            si = sum(inv_[lo:hi])
            row_ = {'mean_invested': statistics.fmean(inv_[lo:hi])}
            for k_, xs in cp_.items():
                tot = sum(xs[lo:hi])
                row_[k_ + '_per_year'] = tot / (hi - lo) * 365.0
                row_[k_ + '_per_deployed'] = (tot / si * 365.0) if si > 0 else None
            out_[lab] = row_
        return out_
    broad = next(v for v in variants if v['name'] == 'R28_F50_Sm5bp_V2M_N30')
    ex_b, bk_b = simulate(coins, feats, days, broad, coll_members, K_main, bench, small, record=True)
    ex_b0, _ = simulate(coins, feats, days, broad, coll_members, K_main, bench, Costs(st, pt, mult=0.0, fees=fees))
    ex_ch0, bk_ch0 = simulate(coins, feats, days, vch, coll_members, K_main, bench,
                              Costs(st, pt, mult=0.0, fees=fees), record=True)
    yrs_b = len(days) / 365.0

    def retention(bk_):
        """Mean share of the names held after one rebalance that are still held after the next."""
        bs = [set(b) for _, b in bk_['_books']]
        r_ = [len(a & b) / len(a) for a, b in zip(bs, bs[1:]) if a]
        return statistics.fmean(r_) if r_ else None
    post_hoc = {
        'note': 'diagnostics computed after the protocol; they select nothing',
        'chosen_excess_per_invested': {'full': per_invested(ex_ch, bk_ch['_invested']),
                                       'in_sample': per_invested(ex_ch, bk_ch['_invested'], 0, c_cut),
                                       'out_of_sample': per_invested(ex_ch, bk_ch['_invested'], c_cut)},
        'chosen_decomposition': halves(bk_ch),
        'chosen_retention_between_rebalances': retention(bk_ch),
        'broad_retention_between_rebalances': retention(bk_b),
        'chosen_zero_cost': perf_split(ex_ch0, c_cut),
        'chosen_zero_cost_per_invested': {'in_sample': per_invested(ex_ch0, bk_ch0['_invested'], 0, c_cut),
                                          'out_of_sample': per_invested(ex_ch0, bk_ch0['_invested'], c_cut)},
        'broad_variant': {'name': broad['name'], 'perf': perf_split(ex_b, c_cut),
                          'zero_cost': perf_split(ex_b0, c_cut),
                          'in_sample': decomp(bk_b, ex_b, bk_b['_invested'], 0, c_cut),
                          'out_of_sample': decomp(bk_b, ex_b, bk_b['_invested'], c_cut, len(days)),
                          'funding_per_year': bk_b['funding'] / yrs_b, 'neg_funding_per_year': -bk_b['neg_funding'] / yrs_b,
                          'basis_per_year': bk_b['basis'] / yrs_b, 'costs_per_year': bk_b['costs'] / yrs_b,
                          'bench_on_invested_per_year': bk_b['bench_on_invested'] / yrs_b,
                          'decomposition': halves(bk_b),
                          'turnover_per_year': bk_b['turnover'] / yrs_b, 'tails': tails(
                              ex_b, days, bk_b, [i * bench(d) / 365.0 for i, d in zip(bk_b['_invested'], days)])},
    }
    passes = {'in_sample_positive': bool(ctt['in_sample_positive']),
              'oos_t_gt_2': (ctt['oos_t'] or 0.0) > 2.0,
              'bh_survivor': chosen in bh_one_sided(ser)[0],
              'oos_positive_at_3m': (cap[str(3_000_000)]['base']['out_of_sample'] or 0.0) > 0.0}
    passes['pass'] = all(passes.values())
    R = {
        'venue': venue,
        'seconds': round(time.time() - t0, 1), 'seconds_features': round(t_feat, 1),
        'data': rep,
        'window': {'pnl_first_day': dname(days[0]), 'pnl_last_day': dname(days[-1]), 'days': len(days),
                   'split_day': dname(days[c_cut]), 'in_sample_days': c_cut, 'oos_days': len(days) - c_cut},
        'benchmark': {'kind': 'savings rate paid (term_carry.load_navs savings_path: DSR, then SSR from sUSDS NAV)',
                      'mean_in_sample': statistics.fmean(bench(d) for d in days[:c_cut]),
                      'mean_oos': statistics.fmean(bench(d) for d in days[c_cut:]),
                      'constant_reported_beside': SSR_CONST},
        'costs': {'fee_bp': fees, 'spot_half_spread_table': st, 'perp_half_spread_table': pt,
                  'impact_Y': IMPACT_Y, 'impact_Y_stress': IMPACT_Y_STRESS, 'entry_days': ENTRY_DAYS,
                  'participation': PARTICIPATION},
        'capital': {'formula': 'K = 1 + max(0, im + 0.5 - 1.5 c), im = max(0.1, 1/max leverage)',
                    'c_assumed_robustness': c_assumed,
                    'collateral_members': len(coll_members), 'all_spot_members': len(all_members),
                    'K_main_median': statistics.median(K_main(coins[s]) for s in coll_members) if coll_members else None,
                    'c_main_quartiles': [cs_main[len(cs_main) // 4], cs_main[len(cs_main) // 2],
                                         cs_main[3 * len(cs_main) // 4]] if cs_main else None},
        'universe_by_rebalance': floor_counts,
        'persistence': persist,
        'protocol': protocol_summary(ctt, len(variants), ser),
        'family': fam,
        'chosen': {'name': chosen, 'variant': vch, 'perf': perf_split(ex_ch, c_cut), 'by_year': by_year(ex_ch, days),
                   'by_half_year': by_half_year(ex_ch, days),
                   'deflated_sharpe_full': B.deflated_sharpe(ex_ch, len(variants)),
                   'deflated_sharpe_oos': B.deflated_sharpe(oos_ex, len(variants)),
                   'oos_block_bootstrap_mean': B.block_bootstrap(oos_ex, block=28),
                   'tails': tails(ex_ch, days, bk_ch, inv_b),
                   'tails_oos': tails(ex_ch[c_cut:], days[c_cut:], {}, inv_b[c_cut:]),
                   'attribution': coin_attribution(bk_ch, coins), 'forced_exits': bk_ch.get('exits', []),
                   'last_book': {s: {'n': n, 'floor_share': f['floor_share'], 'apr': f['apr'],
                                     'spot_vol': f['spot_vol'], 'c': coins[s]['c']}
                                 for s, (n, f) in (bk_ch['_books'][-1][1].items() if bk_ch['_books'] else [])},
                   'last_book_day': dname(bk_ch['_books'][-1][0]) if bk_ch['_books'] else None},
        'baseline': base,
        'robustness': {
            'all_spot_universe': {'protocol': protocol_summary(ctt_a, len(variants), ser_a), 'family': fam_a,
                                  'chosen_main_variant_here': perf_split(ex_a_ch, c_cut),
                                  'chosen_main_variant_tails': tails(ex_a_ch, days, bk_a_ch,
                                                                     [i * bench(d) / 365.0 for i, d in
                                                                      zip(bk_a_ch['_invested'], days)]),
                                  'chosen_main_variant_exits': bk_a_ch.get('exits', [])},
            'collateral_universe_at_assumed_ratio': perf_split(ex_bridge, c_cut),
            'costs_x2': perf_split(ex_c2, c_cut),
            'constant_ssr_benchmark': perf_split(ex_const, c_cut),
            'late_entry_signal_one_day_stale': perf_split(ex_late, c_cut)},
        'capacity': cap,
        'post_hoc': post_hoc,
        'passes': passes,
    }
    series = {'days': [dname(d) for d in days], 'chosen': chosen, 'chosen_excess': ex_ch,
              'chosen_invested': bk_ch['_invested'], 'chosen_names_held': bk_ch['_held'],
              'bench': [bench(d) for d in days], 'cutoff_index': c_cut, 'variants': ser, 'variants_all_spot': ser_a}
    return R, series


def analyze(out, venues=('binance', 'bybit')):
    out = Path(out)
    fn = out / 'analysis.json'
    prior = json.loads(fn.read_text()) if fn.exists() else {}
    pre = prior.get('preregistered')
    if not pre or pre.get('grid') != json.loads(json.dumps(GRID)):
        raise SystemExit('the grid in analysis.json is missing or differs from GRID: run `grid` first, never edit it')
    sav = savings_path()
    A = {'preregistered': pre, 'venues': {}, 'primary': 'binance',
         'protocol_amendments': [
             {'at': '2026-10-11T04:05:00+00:00', 'before_any_result': True,
              'what': 'BH survivors use one-sided p-values (mean daily excess > 0, full-sample Newey-West); '
                      'backtest.choose_then_test\'s two-sided list is kept beside it as '
                      'bh_survivors_full_sample_two_sided (under two-sided p a significant loser also survives)'},
             {'at': '2026-10-11T04:05:00+00:00', 'before_any_result': True,
              'what': 'Bybit added as a second venue with the same grid and protocol (its own choose-then-test)'}]}
    series = {}
    for v in venues:
        if not (out / 'raw' / ('manifest_%s.json' % v)).exists():
            A['venues'][v] = {'skipped': 'no manifest_%s.json (collection not finished)' % v}
            continue
        A['venues'][v], series[v] = analyze_venue(out, v, sav)
    d0 = day_ms(PNL_START) // DAY_MS
    A['benchmark_daily'] = {dname(d): round(x, 6) for d, x in sorted(sav.items()) if d >= d0}
    A['results_written_at'] = utc()
    A['passes'] = (A['venues'].get('binance') or {}).get('passes')
    write_gz(out / 'series.json.gz', series)
    write_json(fn, A)
    return A


def cmd_analyze(args):
    A = analyze(args.out, tuple(args.venues.split(',')))
    for v, R in A['venues'].items():
        if 'protocol' not in R:
            print(v, R)
            continue
        p = R['protocol']
        print(v, json.dumps({'chosen': p['chosen'], 'in_sample': p['in_sample'], 'out_of_sample': p['out_of_sample'],
                             'oos_t': p['oos_t'], 'bh': len(p['bh_survivors_full_sample']), 'passes': R['passes'],
                             'seconds': R['seconds']}, indent=1, default=str))


# ---------------------------------------------------------------------------------------------- render

def pc(x, d=2):
    return '-' if x is None else ('%+.*f%%' % (d, 100.0 * x))


def pu(x, d=1):
    return '-' if x is None else ('%.*f%%' % (d, 100.0 * x))


def num(x, d=2):
    return '-' if x is None else ('%.*f' % (d, x))


def usd(x):
    if x is None:
        return '-'
    a = abs(x)
    s = '-' if x < 0 else ''
    if a >= 1e6:
        return '%s$%.2fM' % (s, a / 1e6)
    if a >= 1e3:
        return '%s$%.0fk' % (s, a / 1e3)
    return '%s$%.0f' % (s, a)


def render_venue(R, L, pre):
    P, ch, D, W = R['protocol'], R['chosen'], R['data'], R['window']
    venue = R['venue']
    fees = R['costs']['fee_bp']
    verdict = 'PASSES' if R['passes']['pass'] else 'FAILS'
    L.append('## %s\n' % venue.capitalize())
    L.append('**Verdict: the chosen variant %s the go rule** (in-sample positive, out-of-sample HAC t > 2, a BH '
             'survivor, out-of-sample excess positive at $3M): %s.\n' % (verdict, ', '.join(
                 '%s=%s' % (k, v) for k, v in R['passes'].items() if k != 'pass')))
    L.append('Excess is over the savings rate paid each day (DSR, then the SSR; mean %s in sample, %s out of sample; '
             'term_carry.load_navs), on the capital the trade ties up (K = 1 + max(0, im + 0.5 - 1.5c), c = today\'s '
             'collateral ratio; median K %s, c quartiles %s). Costs: taker fees spot %gbp / perp %gbp per side, '
             'half-spread from today\'s book tickers (75th percentile by volume bucket, floored at half a tick), '
             'double costs on forced exits. P&L window %s..%s, split at %s (%d / %d days).\n' % (
                 pu(R['benchmark']['mean_in_sample'], 2), pu(R['benchmark']['mean_oos'], 2),
                 num(R['capital']['K_main_median']), R['capital']['c_main_quartiles'], fees['spot'], fees['perp'],
                 W['pnl_first_day'], W['pnl_last_day'], W['split_day'], W['in_sample_days'], W['oos_days']))
    L.append('### Data coverage\n')
    L.append('| item | value |\n|---|---|')
    for k, lab in (('universe_perps', 'USDT-margined coin perps found (listed any status + funding history)'),
                   ('universe_by_status', 'by status today'),
                   ('funding_symbols', 'symbols with funding history since %s' % FETCH_START),
                   ('perps_traded_in_window', 'perps with a traded daily bar in the window'),
                   ('excluded_base', 'excluded (BTC, ETH, stables, gold, indices)'),
                   ('no_spot_match', 'no same-coin spot pair on the venue'),
                   ('no_spot_match_no_spot_data', '  no spot market (no data under any candidate name)'),
                   ('no_spot_match_overlap_under_30d', '  spot overlap under 30 days'),
                   ('no_spot_match_identity_mismatch', '  a spot pair of the same name is another coin (rejected)'),
                   ('coins_with_spot', 'coins with both legs (the all-spot universe)'),
                   ('coins_collateral_today', 'of which collateral today (main universe)'),
                   ('coins_delisted_in_window', 'coins with a leg delisted in the window'),
                   ('coins_perp_delisted', '  perp delisted'), ('coins_spot_delisted', '  spot delisted'),
                   ('perps_never_traded_but_settling', 'perps with no traded bar in the window that still print '
                                                       'settlements in it (dropped entirely)'),
                   ('settlements_of_never_traded_perps', '  their settlements in the window'),
                   ('settlements_raw', 'settlements fetched (the perps above with a traded bar)'),
                   ('settlements_kept', 'settlements kept'),
                   ('settlements_dropped', 'dropped: funding day without a traded perp bar, or after delivery'),
                   ('settlements_after_last_trade', '  stamped after the last traded perp bar (phantom prints)'),
                   ('settlements_before_first_trade', '  before the first traded bar (paging overshoot before the '
                                                      'window, pre-market funding)'),
                   ('collateral_assets_today', 'collateral assets on %s' % D.get('collateral_snapshot_day'))):
        v = D.get(k)
        L.append('| %s | %s |' % (lab, json.dumps(v) if isinstance(v, dict) else v))
    L.append('')
    ub = R['universe_by_rebalance']
    if ub:
        L.append('Main universe at the 7-day rebalances: eligible names median %d (min %d, max %d); at the floor on '
                 '>= 50%% of trailing settlements median %d; with spot volume >= $2M median %d, >= $10M median %d.\n'
                 % (statistics.median(r['eligible'] for r in ub), min(r['eligible'] for r in ub),
                    max(r['eligible'] for r in ub), statistics.median(r['floor50'] for r in ub),
                    statistics.median(r['floor50_v2m'] for r in ub), statistics.median(r['floor50_v10m'] for r in ub)))
    if R.get('persistence'):
        L.append('### Does floor persistence persist? (eligible coins at every 7-day rebalance, next 28 days)\n')
        L.append('| universe | trailing floor share | coin-dates | trailing APR | next floor share | next APR mean | '
                 'next APR median | next APR p10 | next 28d has a spike < -0.05%/8h |')
        L.append('|---|---|---|---|---|---|---|---|---|')
        for u in ('main', 'main_spike_screened', 'main_v10m_spike_screened', 'all_spot'):
            for r in R['persistence'].get(u, []):
                L.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s |' % (
                    u, r['trailing_floor_share'], r['n'], pc(r['trailing_apr_mean']), pu(r['next_floor_share_mean'], 0),
                    pc(r['next_apr_mean']), pc(r['next_apr_median']), pc(r['next_apr_p10']),
                    pu(r['next_spike_share'], 0)))
        L.append('')
    L.append('### Protocol: choose on the first half, test once on the second\n')
    L.append('| chosen | in-sample excess | IS Sharpe | in_sample_positive | OOS excess | OOS Sharpe | OOS HAC t | '
             'OOS t (30 lags) | OOS rank | deflated Sharpe (IS, 32 trials) | BH survivors (q=0.10, full sample, '
             'one-sided: mean > 0) |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    bh = P['bh_survivors_full_sample']
    L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %d/%d | %s | %d%s |' % (
        P['chosen'], pc(P['in_sample']['ann_return']), num(P['in_sample']['sharpe']), P['in_sample_positive'],
        pc(P['out_of_sample']['ann_return']), num(P['out_of_sample']['sharpe']), num(P['oos_t']),
        num(ch['perf']['t_oos_lag30']), P['oos_rank'], P['n_variants'], num(P['deflated_sharpe_in_sample'], 3),
        len(bh), (': ' + ', '.join(bh[:6]) + (' ...' if len(bh) > 6 else '')) if bh else ''))
    L.append('')
    two = P.get('bh_survivors_full_sample_two_sided') or []
    if two:
        L.append('backtest.choose_then_test\'s own BH (two-sided p) would list %d "survivors" here; %d of them have a '
                 'negative full-sample mean, i.e. they are significant losers.\n' % (
                     len(two), sum(1 for k in two if (R['family'][k]['full'] or 0) < 0)))
    bb = ch['oos_block_bootstrap_mean']
    L.append('Chosen variant: full sample %s (t %s); deflated Sharpe full %s, OOS %s; OOS mean daily excess, 28-day '
             'block bootstrap 95%% interval %s..%s a year.\n' % (
                 pc(ch['perf']['full']), num(ch['perf']['t_full']), num(ch['deflated_sharpe_full'], 3),
                 num(ch['deflated_sharpe_oos'], 3), pc((bb.get('lo') or 0) * 365), pc((bb.get('hi') or 0) * 365)))
    L.append('### All variants (main universe, small size), by in-sample excess\n')
    L.append('| variant | full | in sample | OOS | OOS t | BH adj p | names held | invested | turnover/yr | '
             'forced exits | neg. funding/yr |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for k, r in sorted(R['family'].items(), key=lambda kv: -(kv[1]['in_sample'] if kv[1]['in_sample'] is not None
                                                              else -9)):
        L.append('| %s%s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %s |' % (
            k, ' (chosen)' if k == P['chosen'] else '', pc(r['full']), pc(r['in_sample']), pc(r['out_of_sample']),
            num(r['t_oos']), num(r['bh_adj_p'], 3), num(r['mean_names_held'], 1), pu(r['mean_invested'], 0),
            pu(r['turnover_per_year'], 0), r['forced_exits'], pu(r['neg_funding_per_year'], 2)))
    L.append('')
    t = ch['tails']
    L.append('### Chosen variant: where the P&L came from, and its tail\n')
    L.append('| funding/yr | of which at the floor | basis/yr | costs/yr | savings rate on invested/yr | excess/yr | '
             'turnover/yr | names held | invested |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
        pc(t['funding_per_year']), pu(t['floor_funding_share'], 0), pc(t['basis_per_year']), pc(-t['costs_per_year']),
        pc(-t['bench_on_invested_per_year']), pc(ch['perf']['full']), pu(t['turnover_per_year'], 0),
        num(t['mean_names_held'], 1), pu(t['mean_invested'], 0)))
    L.append('')
    L.append('| worst rolling week | worst calendar week | max drawdown | best 1% of days: share of excess (of gross) | '
             'negative settlements paid/yr (share of positive funding) | forced exits (delisting/gap) | rally '
             'rebalances |')
    L.append('|---|---|---|---|---|---|---|')
    L.append('| %s from %s | %s (%s) | %s | %s (%s) | %s (%s) | %d (%d/%d) | %d |' % (
        pc(t['worst_rolling_week']), t['worst_rolling_week_start'], pc(t['worst_calendar_week']),
        t['worst_calendar_week_id'], pu(t['max_drawdown']), pu(t['best_1pct_days_share_of_excess'], 0),
        pu(t['best_1pct_days_share_of_gross'], 0), pu(t['neg_funding_paid_per_year']),
        pu(t['neg_funding_share_of_positive'], 0), t['forced_exits'], t['forced_exits_delisting'],
        t['forced_exits_gap'], t['rally_rebalances']))
    L.append('')
    L.append('By year: %s. By half-year: %s.\n' % (
        ', '.join('%s %s (%dd)' % (y, pc(v['ann_excess']), v['days']) for y, v in ch['by_year'].items()),
        ', '.join('%s %s' % (y, pc(v['ann_excess'])) for y, v in ch['by_half_year'].items())))
    at = ch['attribution']
    L.append('Best coins (P&L in capital units over the window, before the benchmark): %s. Worst: %s.\n' % (
        ', '.join('%s %s' % (x['sym'], pc(x['pnl'])) for x in at['best'][:8]),
        ', '.join('%s %s' % (x['sym'], pc(x['pnl'])) for x in at['worst'][:8])))
    if ch.get('last_book'):
        L.append('Last book (%s): %s.\n' % (ch['last_book_day'], ', '.join(
            '%s (floor %s, spot vol %s, c %s)' % (k, pu(v['floor_share'], 0), usd(v['spot_vol']), num(v['c']))
            for k, v in sorted(ch['last_book'].items(), key=lambda kv: -kv[1]['spot_vol']))))
    L.append('### Baseline: always the top N by floor share\n')
    L.append('| baseline | full | in sample | OOS | OOS t | excess per $ deployed | worst week | max drawdown | '
             'neg. funding/yr | turnover/yr | names held |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for k, b in R['baseline'].items():
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            k, pc(b['perf']['full']), pc(b['perf']['in_sample']), pc(b['perf']['out_of_sample']),
            num(b['perf']['t_oos']), pc(b.get('excess_per_invested_full')), pc(b['tails']['worst_rolling_week']),
            pu(b['tails']['max_drawdown']), pu(b['tails']['neg_funding_paid_per_year']),
            pu(b['tails']['turnover_per_year'], 0), num(b['tails']['mean_names_held'], 1)))
    L.append('')
    RB = R['robustness']
    ra = RB['all_spot_universe']
    L.append('### Robustness\n')
    L.append('| run | full | in sample | OOS | OOS t |')
    L.append('|---|---|---|---|---|')
    L.append('| all-spot universe (delisted included, c = %.2f for every coin): its own chosen %s | - | %s | %s | %s |'
             % (R['capital']['c_assumed_robustness'], ra['protocol']['chosen'],
                pc(ra['protocol']['in_sample']['ann_return']), pc(ra['protocol']['out_of_sample']['ann_return']),
                num(ra['protocol']['oos_t'])))
    for lab, r in (('all-spot universe, the main chosen variant', ra['chosen_main_variant_here']),
                   ('main universe at the assumed ratio (bridge)', RB['collateral_universe_at_assumed_ratio']),
                   ('fees and spreads x2', RB['costs_x2']),
                   ('constant 3.80% benchmark', RB['constant_ssr_benchmark']),
                   ('late entry: signal one day stale', RB['late_entry_signal_one_day_stale'])):
        L.append('| %s | %s | %s | %s | %s |' % (lab, pc(r['full']), pc(r['in_sample']), pc(r['out_of_sample']),
                                                num(r['t_oos'])))
    L.append('')
    L.append('All-spot universe: BH survivors %d; in_sample_positive %s; forced exits of the main chosen variant '
             'there %d (%s).\n' % (len(ra['protocol']['bh_survivors_full_sample']),
                                   ra['protocol']['in_sample_positive'],
                                   ra['chosen_main_variant_tails']['forced_exits'],
                                   ', '.join('%s %s' % (x['sym'], x['day'])
                                             for x in ra['chosen_main_variant_exits'][:10]) or 'none'))
    ph = R.get('post_hoc')
    if ph:
        cz, bv = ph['chosen_zero_cost'], ph['broad_variant']
        L.append('### Post hoc (computed after the protocol; selects nothing)\n')
        L.append('| run | full | in sample | OOS | OOS t |')
        L.append('|---|---|---|---|---|')
        L.append('| chosen, excess per $ actually deployed | %s | %s | %s | - |' % (
            pc(ph['chosen_excess_per_invested']['full']), pc(ph['chosen_excess_per_invested']['in_sample']),
            pc(ph['chosen_excess_per_invested']['out_of_sample'])))
        L.append('| chosen at zero fees and spreads | %s | %s | %s | %s |' % (
            pc(cz['full']), pc(cz['in_sample']), pc(cz['out_of_sample']), num(cz['t_oos'])))
        L.append('| chosen at zero cost, per $ deployed | - | %s | %s | - |' % (
            pc(ph['chosen_zero_cost_per_invested']['in_sample']),
            pc(ph['chosen_zero_cost_per_invested']['out_of_sample'])))
        L.append('| broad %s (costed) | %s | %s | %s | %s |' % (
            bv['name'], pc(bv['perf']['full']), pc(bv['perf']['in_sample']), pc(bv['perf']['out_of_sample']),
            num(bv['perf']['t_oos'])))
        L.append('| broad, per $ deployed | - | %s | %s | - |' % (pc(bv['in_sample']['excess_per_invested']),
                                                                  pc(bv['out_of_sample']['excess_per_invested'])))
        L.append('| broad at zero fees and spreads | %s | %s | %s | %s |' % (
            pc(bv['zero_cost']['full']), pc(bv['zero_cost']['in_sample']), pc(bv['zero_cost']['out_of_sample']),
            num(bv['zero_cost']['t_oos'])))
        L.append('')
        L.append('| P&L per year of capital deployed | funding | of which negative settlements | basis | costs | '
                 'savings rate | invested |')
        L.append('|---|---|---|---|---|---|---|')
        for lab, dd in (('chosen', ph['chosen_decomposition']), ('broad', bv['decomposition'])):
            for half in ('in_sample', 'out_of_sample'):
                x = dd[half]
                L.append('| %s, %s | %s | %s | %s | %s | %s | %s |' % (
                    lab, half.replace('_', ' '), pc(x['funding_per_deployed']), pc(x['neg_funding_per_deployed']),
                    pc(x['basis_per_deployed']), pc(-x['costs_per_deployed'] if x['costs_per_deployed'] is not None
                                                     else None),
                    pc(-x['bench_per_deployed'] if x['bench_per_deployed'] is not None else None),
                    pu(x['mean_invested'], 0)))
        L.append('')
        L.append('Names kept from one rebalance to the next: chosen %s, broad %s.\n' % (
            pu(ph.get('chosen_retention_between_rebalances'), 0), pu(ph.get('broad_retention_between_rebalances'), 0)))
        L.append('Broad variant, whole window per year of capital: funding %s (negative settlements %s), basis %s, '
                 'costs %s, savings rate on invested %s; turnover %s; invested %s in sample, %s out of sample; '
                 'worst week %s, max drawdown %s.\n' % (
                     pc(bv['funding_per_year']), pc(-bv['neg_funding_per_year']), pc(bv['basis_per_year']),
                     pc(-bv['costs_per_year']), pc(-bv['bench_on_invested_per_year']),
                     pu(bv['turnover_per_year'], 0), pu(bv['in_sample']['mean_invested'], 0),
                     pu(bv['out_of_sample']['mean_invested'], 0), pc(bv['tails']['worst_rolling_week']),
                     pu(bv['tails']['max_drawdown'])))
    L.append('### Capacity (chosen variant; each name <= %g%% of its 30-day median daily spot and perp volume, built '
             'and unwound over %d days, square-root impact Y = %g, stress Y = %g)\n' % (
                 100 * PARTICIPATION, ENTRY_DAYS, IMPACT_Y, IMPACT_Y_STRESS))
    L.append('| capital | excess full | excess OOS | OOS t | $/yr OOS | invested (OOS) | names capped | impact/yr | '
             'stress Y=1 OOS | cap only OOS | impact only OOS | baseline OOS | one-day crash unwind (median / worst) |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for a, row in sorted(R['capacity'].items(), key=lambda kv: float(kv[0])):
        b = row['base']
        ce = b.get('crash_exit') or {}
        L.append('| %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s | %s | %s / %s |' % (
            usd(float(a)), pc(b['full']), pc(b['out_of_sample']), num(b['t_oos']), usd(b['usd_per_year_oos']),
            pu(b['mean_invested'], 0), pu(b.get('invested_oos'), 0), pu(b['capped_share'], 0),
            pc(-b['impact_per_year']), pc(row['stress_Y1']['out_of_sample']), pc(row['cap_only']['out_of_sample']),
            pc(row['impact_only']['out_of_sample']), pc(row['baseline_base']['out_of_sample']),
            pu(ce.get('median')), pu(ce.get('worst'))))
    L.append('')
    L.append('"cap only" keeps fees and spreads but no impact (what the participation cap alone costs: idle capital '
             'earns zero excess); "impact only" lifts the cap (what impact alone costs). The crash unwind is the cost '
             'of closing the whole book in one day at three times the trailing volatility and Y = 1, as a fraction '
             'of capital.\n')


def render(out):
    out = Path(out)
    A = json.loads((out / 'analysis.json').read_text())
    pre = A['preregistered']
    L = ['# Altcoin floor carry: a basket of spot-long / same-venue perp-short positions chosen by trailing floor '
         'persistence (computed %s)\n' % A['results_written_at']]
    L.append('Question: does a diversified, collateral-efficient basket of altcoin spot-long / same-venue perp-short '
             'positions, chosen by trailing floor persistence, beat the savings rate out of sample after negative '
             'funding spikes, basis moves, costs and realistic capacity, and how much capital can it hold?\n')
    L.append('The rule family was written to analysis.json at %s, before any return was computed: `%s`; rank: %s; '
             '%d variants. Baseline: top-N by floor share with no floor threshold and no spike screen (spot volume '
             '>= $2M).\n' % (pre['written_at'], json.dumps(pre['grid']), pre['rank'], pre['n_variants']))
    for v, R in A['venues'].items():
        if 'protocol' not in R:
            L.append('## %s\n\n%s\n' % (v.capitalize(), R.get('skipped')))
            continue
        render_venue(R, L, pre)
    L.append('## Caveats\n')
    L.append('- Collateral survivorship: collateral lists exist only as of the watcher\'s 2026-10-11 snapshot. The '
             'main universe is today\'s list, so every coin delisted before today is absent from it and never forces '
             'an exit there; the all-spot universe includes delisted coins and shows what they cost.')
    L.append('- Ratios are today\'s for the whole history (Binance: the classic program; Bybit: UTA tiers at a $1M '
             'holding).')
    L.append('- Daily closes are last trades, not mids, so the basis at entry and exit carries last-trade noise; '
             'funding is paid on the settlement\'s mark price where the venue reports it (Binance) and on the day\'s '
             'perp close otherwise (Bybit).')
    L.append('- Half-spreads come from one Sunday snapshot of book tickers applied by volume bucket to the whole '
             'history; impact is a square-root model, not measured fills.')
    L.append('- OKX is not covered: its public funding history serves about three months, not the window.')
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    return A


def build_manifest(out, A):
    out = Path(out)
    files = {}
    for fn in sorted(out.glob('*')):
        if fn.is_file():
            files[fn.name] = fn.stat().st_size
    raw = {}
    for v in A['venues']:
        mf = out / 'raw' / ('manifest_%s.json' % v)
        if mf.exists():
            m = json.loads(mf.read_text())
            raw[v] = {k: m.get(k) for k in ('n_files', 'bytes', 'files_by_dir', 'endpoints', 'log')}
    return {'generated': utc(), 'analysis_generated': A['results_written_at'], 'script': 'scripts/alt_floor_carry.py',
            'tests': 'uv run --with pytest --with pycryptodome python -m pytest scripts/test_alt_floor_carry.py -q',
            'commands': ['uv run python scripts/alt_floor_carry.py collect --end-day 2026-10-11',
                         'uv run python scripts/alt_floor_carry.py collect --venue bybit --end-day 2026-10-11',
                         'uv run python scripts/alt_floor_carry.py grid      # wrote the rule family first',
                         'uv run python scripts/alt_floor_carry.py analyze',
                         'uv run python scripts/alt_floor_carry.py render'],
            'inputs': {'raw': 'research/2026-10-11/alt_floor_carry/raw/<venue>/ (manifest_<venue>.json)',
                       'collateral_snapshot': str(COLLATERAL_SNAPSHOT.relative_to(ROOT)),
                       'savings_path': 'term_carry.load_navs(%s): raw/chain/samples.json and '
                                       'research/2026-10-09/redemption_history/raw/long/state.json'
                                       % TERM_CARRY_OUT.relative_to(ROOT)},
            'raw': raw, 'outputs': files, 'preregistered_at': A['preregistered']['written_at'],
            'venues': {v: ({'data': R.get('data'), 'window': R.get('window'), 'passes': R.get('passes')}
                           if 'protocol' in R else R) for v, R in A['venues'].items()},
            'series': 'series.json.gz: per venue, the daily excess of every variant (main and all-spot universes), '
                      'the chosen variant, its invested capital and names held, the benchmark, the cutoff index'}


def book_entry(R, generated):
    """A draft book row (status 'proposed') for a venue whose chosen variant passed; for the coordinator, not the
    book. Quoted at the largest tested size whose out-of-sample excess (base impact) is positive with t > 2."""
    ch, P, cap = R['chosen'], R['protocol'], R['capacity']
    v = ch['variant']
    ok = [(float(a), row['base']) for a, row in cap.items()
          if (row['base']['out_of_sample'] or 0) > 0 and (row['base']['t_oos'] or 0) > 2]
    size, b = max(ok, key=lambda x: x[1]['usd_per_year_oos']) if ok else (SIZES[0], cap[str(SIZES[0])]['base'])
    t = ch['tails']
    venue = R['venue']
    return {
        'id': '%s-alt-floor-carry-basket' % venue,
        'name': 'Altcoin floor-carry basket on %s: hold collateral-eligible alt spot and short the same-venue perp, '
                'names chosen by trailing floor persistence' % venue.capitalize(),
        'kind': 'carry', 'status': 'proposed',
        'thesis': ('Perp longs on %s pay the funding formula\'s interest leg (0.01%%/8h, 10.95%% a year pro rata) '
                   'whenever the premium is small. Holding the coin as portfolio collateral and shorting its perp '
                   'collects it on capital K = 1 + max(0, im + 0.5 - 1.5c). Rule %s (rebalance every %d days, trailing '
                   '30-day floor share >= %d%%, spike screen %s, spot volume >= $%dM, %d names equal weight) chosen '
                   'on %s..%s among 32 pre-registered variants, tested once on %s..%s: %s a year over the savings '
                   'rate paid (HAC t %.2f; in sample %s; deflated Sharpe %.2f). Max drawdown %s, worst week %s, '
                   'negative settlements cost %s a year.' % (
                       venue.capitalize(), ch['name'], v['rebalance_days'], round(100 * v['floor_share_min']),
                       'on' if v['spike_8h'] is not None else 'off', round(v['spot_vol_min_usd'] / 1e6),
                       v['n_names'], R['window']['pnl_first_day'], R['window']['split_day'], R['window']['split_day'],
                       R['window']['pnl_last_day'], pc(P['out_of_sample']['ann_return']), P['oos_t'] or 0.0,
                       pc(P['in_sample']['ann_return']), P['deflated_sharpe_in_sample'] or 0.0,
                       pu(t['max_drawdown']), pc(t['worst_rolling_week']), pu(t['neg_funding_paid_per_year']))),
        'mechanism': 'Funding = premium + clamp(interest - premium, +/-0.05%): with the premium near zero, longs pay '
                     'the interest leg. The arbitrage that would push it down needs spot inventory on the same venue; '
                     'portfolio margin makes that inventory the short\'s collateral, so the trade ties up roughly the '
                     'notional instead of notional plus margin elsewhere.',
        'legs': ['every %d days at 00:00 UTC rank the venue\'s collateral-eligible coins with a same-venue spot market '
                 'by trailing-30-day floor share, then trailing funding APR, then spot volume; keep the first %d '
                 'that pass the screens' % (v['rebalance_days'], v['n_names']),
                 'buy the spot and short the same quantity of the USDT perp in one portfolio-margin account; each name '
                 '1/%d of capital, short notional = capital share / K; build and unwind over ~%d days' % (
                     v['n_names'], ENTRY_DAYS),
                 'exit a name on a delisting announcement or a trading halt; rebalance the drift after a rally above '
                 '50% since the last trade'],
        'capacity_usd': int(size), 'capital_days': 365,
        'kill_criteria': ['trailing-90-day realised excess over the savings rate negative (alt_floor_carry.py analyze)',
                          'the basket\'s trailing-30-day floor share below 50% for two consecutive rebalances',
                          'a portfolio-margin collateral-ratio cut that lifts the median K above 1.3',
                          'two delisting exits in one quarter, or any auto-deleveraging of a short leg'],
        'risks': ['collateral survivorship: the backtest used today\'s collateral list for the whole history; coins '
                  'delisted before today are absent from the main universe',
                  'negative funding spikes on altcoins (squeezes) are the main loss; floor share is not carry',
                  'thin spot books: capacity is set by spot volume, and a crash exit costs %s of capital at $%dM '
                  '(one day, 3x volatility, Y = 1)' % (pu((b.get('crash_exit') or {}).get('worst')), size / 1e6),
                  'venue concentration: both legs and the collateral sit on one exchange',
                  'collateral ratios and portfolio-margin terms change without notice'],
        'evidence': {'notes': 'research/2026-10-11/alt_floor_carry/analysis.json venues.%s (protocol, chosen, '
                              'capacity, robustness); tables.md; scripts/alt_floor_carry.py' % venue,
                     'findings': [], 'verify': []},
        'quotes': [{'at': generated, 'window': 'research/2026-10-11/alt_floor_carry', 'source': 'history',
                    'present': True, 'go': True, 'net_apr': round(b['out_of_sample'] or 0.0, 4),
                    'usd': round(b['usd_per_year_oos'] or 0.0),
                    'note': 'out-of-sample excess over the savings rate at $%dM with square-root impact (Y=%g) and '
                            'the 2%% participation cap; invested %s of capital' % (
                                size / 1e6, IMPACT_Y, pu(b.get('invested_oos'), 0))}],
        'recheck_hours': 168}


def cmd_render(args):
    A = render(args.out)
    entries = [book_entry(R, A['results_written_at']) for v, R in A['venues'].items()
               if 'passes' in R and R['passes']['pass']]
    bfn = Path(args.out) / 'book_entries.json'
    if entries:
        write_json(bfn, entries)
    elif bfn.exists():
        bfn.unlink()                     # a draft from an earlier run must not survive a failing one
    write_json(Path(args.out) / 'manifest.json', build_manifest(args.out, A))
    print('tables.md and manifest.json written; passing venues:', [e['id'] for e in entries])


def cmd_probe(args):
    """Recompute one coin's decision-day features from the raw files (for re-derivation and cross-checks)."""
    vi = venue_inputs(args.out, args.venue)
    vi['uni'] = {k: v for k, v in vi['uni'].items() if k in args.symbols.split(',')}
    coins, rep, last_day = build_coins(vi)
    d = day_ms(args.day) // DAY_MS if args.day else last_day + 1
    for sym, c in coins.items():
        f = features(c, d)
        sets = [x for dd in range(d - LOOKBACK, d) for x in c['fd'].get(dd, ())]
        print(json.dumps({'symbol': sym, 'decision_day': dname(d), 'spot': c['spot'], 'mult': c['mult'], 'c': c['c'],
                          'K': capital_per_short(c['c'], c['im']), 'status': c['status'],
                          'dropped_phantom_or_untraded': c['dropped_settlements'],
                          'intervals_h': dict(collections.Counter(x[3] for x in sets)),
                          **{k: f[k] for k in ('n', 'floor_share', 'apr', 'min_rate_8h', 'coverage', 'spot_vol',
                                               'perp_vol', 'sigma', 'identity', 'eligible')}}, default=str))


def cmd_collect(args):
    if args.venue not in ('binance', 'bybit'):
        raise SystemExit('venues: binance, bybit')
    log = (collect_binance if args.venue == 'binance' else collect_bybit)(args.out, args.end_day)
    print(json.dumps({k: log[k] for k in ('universe', 'spot_pairs_fetched', 'http', 'finished')}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--out', default=str(OUT))
    c.add_argument('--venue', default='binance')
    c.add_argument('--end-day', default=None, help='exclusive end day (default: today 00:00 UTC)')
    c.set_defaults(fn=cmd_collect)
    pr = sub.add_parser('probe')
    pr.add_argument('--out', default=str(OUT))
    pr.add_argument('--venue', default='binance')
    pr.add_argument('--symbols', required=True, help='comma-separated perp symbols, e.g. MAGICUSDT,KAIAUSDT')
    pr.add_argument('--day', default=None, help='decision day (default: the day after the last complete day)')
    pr.set_defaults(fn=cmd_probe)
    for name, fn in (('grid', cmd_grid), ('analyze', cmd_analyze), ('render', cmd_render)):
        p = sub.add_parser(name)
        p.add_argument('--out', default=str(OUT))
        if name == 'analyze':
            p.add_argument('--venues', default='binance,bybit')
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
