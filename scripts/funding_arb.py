#!/usr/bin/env python3
"""Funding spreads between Hyperliquid and the centralised perp venues, and what a delta-neutral pair actually keeps.

The question. The same coin is a perpetual on Hyperliquid, Binance and Bybit, and each venue charges its own funding
from its own premium. A trader who is short where funding is high and long where it is low holds no coin delta and
collects the difference. That is the most widely known carry in crypto, so the interesting numbers are not whether it
exists but: how large the spread is net of four fee legs and the basis the two books drift through, whether a rule
chosen on the first half of a year still earns on the second, how much notional each coin takes before the depth on
the thinner venue binds, and — where a spread persists for months in a liquid coin — who it is that cannot arbitrage it.

Variants, each tested with the same machinery (scripts/backtest.py: parameters chosen on 2025-10-01 → 2026-04-01 only,
tested once on 2026-04-01 → now, plus a monthly walk-forward; every variant tried is counted for the deflated Sharpe):

  (i)   Hyperliquid vs Binance, per coin;
  (ii)  Hyperliquid vs Bybit, per coin;
  (iii) Binance vs Bybit on the same coins, as a CEX–CEX control;
  (iv)  same-venue Hyperliquid spot–perp carry (long spot, short perp) where a spot market exists;
  (v)   the cross-sectional carry *factor* on Hyperliquid core (short the highest-funding decile, long the lowest).
        It carries market risk by construction and is labelled as a factor, not an arbitrage.

Conventions used everywhere.
  * A funding rate is a fraction of notional per settlement, positive when longs pay shorts (true on all three venues).
    A short receives `+rate`, a long receives `-rate`.
  * Settlements: Hyperliquid every hour; Binance and Bybit every 8, 4 or 1 hours depending on the symbol, and the
    interval of a symbol changes over time, so the series is read from the settlement timestamps, never assumed.
  * A position opened at decision time t does not take the settlement at t (it has already been observed) and does take
    the settlement at its exit time; payments are summed over (t_entry, t_exit].
  * Pair notation: the pair (A, B) is short A and long B, a fixed quantity of each from entry. Funding P&L = rate_A −
    rate_B over the settlements held, scaled by the quantity's value. Basis P&L = B's price change minus A's, both
    relative to entry, on price levels: each leg's own hourly close where it exists; Hyperliquid serves only its last
    5,000 hourly candles, so before mid-March 2026 its leg uses 4-hour closes (5,000 bars reach back ~830 days) and,
    between them, a level synthesised from the other leg through the two premium indices, in the leg's own units.
    The proxy is checked against real closes on the test period, and a second split runs both halves on real closes.
  * Capital: each leg is margined on its own venue at 2x, so a pair of notional N ties up N of capital. Return is per
    unit of that capital. The opportunity cost is the Sky savings rate, 3.80% a year, quoted beside every result.

    uv run python scripts/funding_arb.py collect  --out research/2026-10-09/funding_arb                 # Binance, Bybit: funding, premium, klines
    uv run python scripts/funding_arb.py collect  --out research/2026-10-09/funding_arb --venues okx    # OKX: last quarter only
    uv run python scripts/funding_arb.py hl-extra --out research/2026-10-09/funding_arb                 # HL delisted, 4h candles, spot (paced)
    uv run python scripts/funding_arb.py collect  --out research/2026-10-09/funding_arb                 # again: CEX legs of HL-delisted coins
    uv run python scripts/funding_arb.py snapshot --out research/2026-10-09/funding_arb --venues binance,bybit,okx,hl
    uv run python scripts/funding_arb.py analyze  --out research/2026-10-09/funding_arb --hl research/2026-10-09/perps_history
    uv run python scripts/funding_arb.py analyze  --out research/2026-10-09/funding_arb --train-start 2026-03-15 \
        --test-start 2026-06-01 --tag split0601 --kinds hl_binance,hl_bybit,binance_bybit       # both halves on real closes
    uv run python scripts/funding_arb.py render   --out research/2026-10-09/funding_arb                 # tables.md, manifest.json
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import gzip
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
HOURS_PER_YEAR = 8760.0
SSR = 0.038                       # Sky savings rate read on chain 2026-10-09 (3.80% APY), the benchmark every dollar strategy is compared with

SINCE = '2025-09-25'              # CEX data starts a few days before the HL store so the first signals have a lookback
TRAIN_START = '2025-10-01'
TEST_START = '2026-04-01'

# Fees in bp of notional per fill, base tier (no volume discounts, no referral, no token staking).
FEES_TAKER = {'hl': 4.5, 'binance': 5.0, 'bybit': 5.5, 'okx': 5.0, 'hl_spot': 7.0}
FEES_MAKER = {'hl': 1.5, 'binance': 2.0, 'bybit': 2.0, 'okx': 2.0, 'hl_spot': 4.0}
DEFAULT_HALF_SPREAD_BP = 2.0       # used only where no live book was read for the coin


def utc(ms=None):
    t = time.time() if ms is None else ms / 1000.0
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec='seconds')


def ms_of(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


def write_gz(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(value, f, separators=(',', ':'))
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=1, sort_keys=False, default=str))
    tmp.replace(path)


def safe(name):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', name)


# ---------------------------------------------------------------------------------------------- HTTP

class Http:
    """Paced GET/POST with retries. Binance bans an IP that keeps calling after a 429 (418 follows), so a 429/418 here
    sleeps for the Retry-After the venue sends (or a minute) before anything else is sent to that host."""

    def __init__(self, interval=0.25, timeout=40, retries=6, weight_header=None, weight_soft=None, backoff_429=60.0):
        self.interval, self.timeout, self.retries = interval, timeout, retries
        self.backoff_429 = backoff_429      # Binance means a minute; OKX's windows are two seconds long
        self.weight_header, self.weight_soft = weight_header, weight_soft
        self.next_at = 0.0
        self.n = self.errors = self.throttled = 0
        self.lock = threading.Lock()

    def _wait(self):
        # Several threads may share one limiter: each reserves the next slot under the lock, then sleeps outside it.
        with self.lock:
            now = time.monotonic()
            slot = max(now, self.next_at)
            self.next_at = slot + self.interval
        if slot > now:
            time.sleep(slot - now)

    def get(self, url, params=None, body=None):
        if params:
            url = url + '?' + urllib.parse.urlencode(params)
        last = None
        for attempt in range(self.retries):
            self._wait()
            self.n += 1
            try:
                data = json.dumps(body).encode() if body is not None else None
                req = urllib.request.Request(url, data=data, headers={
                    'User-Agent': 'llm-quant-research/1.0', 'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    payload = json.loads(r.read().decode())
                    if self.weight_header and self.weight_soft:
                        w = fnum(r.headers.get(self.weight_header), 0)
                        if w and w > self.weight_soft:
                            # Over the soft budget: let the one-minute window roll before the next call.
                            self.next_at = time.monotonic() + 20.0
                    return payload
            except urllib.error.HTTPError as e:
                last = 'HTTP %s %s' % (e.code, url[:120])
                if e.code in (429, 418):
                    self.throttled += 1
                    ra = fnum(e.headers.get('Retry-After'), self.backoff_429) if e.headers else self.backoff_429
                    with self.lock:
                        self.next_at = time.monotonic() + max(1.0, min(ra, 300.0))
                    continue
                if e.code in (500, 502, 503, 504):
                    self.errors += 1
                    time.sleep(min(10.0, 0.5 * 2 ** attempt))
                    continue
                self.errors += 1
                try:
                    return {'_http_error': e.code, '_body': e.read().decode()[:300]}
                except Exception:  # noqa: BLE001
                    return {'_http_error': e.code}
            except Exception as e:  # noqa: BLE001 - network errors of any kind are retried
                last = repr(e)[:160]
                self.errors += 1
                time.sleep(min(10.0, 0.5 * 2 ** attempt))
        raise RuntimeError('retry limit: %s' % last)

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


BN = 'https://fapi.binance.com'
BY = 'https://api.bybit.com'
OKX = 'https://www.okx.com'
HL = 'https://api.hyperliquid.xyz/info'


# ---------------------------------------------------------------------------------------------- symbol mapping

MULT_PREFIX = re.compile(r'^(1000000|100000|10000|1000|1M)(?=[A-Z])')
MULT_SUFFIX = re.compile(r'(?<=[A-Z])(1000)$')


def cex_core(base):
    """'1000PEPE' -> (1000, 'PEPE'); 'SHIB1000' (Bybit) -> (1000, 'SHIB'); '1MBABYDOGE' -> (1e6, 'BABYDOGE')."""
    m = MULT_PREFIX.match(base)
    if m:
        p = m.group(1)
        return (1_000_000 if p == '1M' else int(p)), base[len(p):]
    m = MULT_SUFFIX.search(base)
    if m and len(base) > 4:
        return 1000, base[:-4]
    return 1, base


def hl_core(coin):
    """Hyperliquid lists small-unit coins as k<NAME> (1,000 units): 'kPEPE' -> (1000, 'PEPE')."""
    if len(coin) > 1 and coin[0] == 'k' and coin[1:2].isupper():
        return 1000, coin[1:]
    return 1, coin


def map_symbols(hl_coins, bn_symbols, by_symbols, okx_symbols=None):
    """Map each HL coin to at most one Binance and one Bybit USDT perpetual on the same underlying.

    `bn_symbols` / `by_symbols`: lists of {symbol, base, status, listed_ms, delisted_ms}. A core name that matches more
    than one perpetual on a venue (a relaunch, a migration) keeps the one whose life overlaps the study most and records
    the others, so a price-ratio check can overrule the choice later.
    """
    def index(rows):
        d = {}
        for r in rows:
            mult, core = cex_core(r['base'])
            d.setdefault(core.upper(), []).append(dict(r, mult=mult))
        return d

    bi, yi = index(bn_symbols), index(by_symbols)
    oi = index(okx_symbols or [])
    out = {}
    for coin in hl_coins:
        hm, core = hl_core(coin)
        rec = {'hl_mult': hm, 'core': core}
        for venue, idx in (('binance', bi), ('bybit', yi), ('okx', oi)):
            cands = idx.get(core.upper(), [])
            if not cands:
                continue
            cands = sorted(cands, key=lambda r: (-(r.get('delisted_ms') or 9e15), r['symbol']))
            rec[venue] = cands[0]['symbol']
            rec[venue + '_mult'] = cands[0]['mult']
            if len(cands) > 1:
                rec[venue + '_alternatives'] = [c['symbol'] for c in cands[1:]]
        out[coin] = rec
    return out


# ---------------------------------------------------------------------------------------------- collection

def bn_symbols(raw):
    ei = json.loads((raw / 'bn_exchangeInfo.json').read_text())
    rows = []
    for s in ei['symbols']:
        if s.get('contractType') != 'PERPETUAL' or s.get('quoteAsset') != 'USDT':
            continue
        delisted = s.get('deliveryDate') if s.get('status') != 'TRADING' else None
        rows.append({'symbol': s['symbol'], 'base': s['baseAsset'], 'status': s['status'],
                     'listed_ms': s.get('onboardDate'), 'delisted_ms': delisted})
    return rows


def by_symbols(raw):
    rows = []
    for fn in sorted(raw.glob('by_instruments_*.json')):
        d = json.loads(fn.read_text())
        for x in d['result']['list']:
            if x.get('contractType') != 'LinearPerpetual' or x.get('quoteCoin') != 'USDT':
                continue
            dl = int(x['deliveryTime']) if x.get('deliveryTime') not in (None, '', '0') else None
            rows.append({'symbol': x['symbol'], 'base': x['baseCoin'], 'status': x['status'],
                         'listed_ms': int(x.get('launchTime') or 0) or None, 'delisted_ms': dl,
                         'funding_interval_min': x.get('fundingInterval')})
    seen, out = set(), []
    for r in rows:
        if r['symbol'] not in seen:
            seen.add(r['symbol'])
            out.append(r)
    return out


def okx_symbols(raw):
    """OKX USDT-margined swaps. OKX quotes every coin per unit (PEPE at its own price, contract size in ctVal), so the
    core name is ctValCcy and the multiplier is 1. Delisted swaps are not served by the instruments endpoint, and the
    funding endpoint keeps only about three months, so OKX is an out-of-sample check on the last quarter, not a
    backtest venue."""
    p = raw / 'okx_instruments.json'
    if not p.exists():
        return []
    rows = []
    for x in json.loads(p.read_text()).get('data', []):
        if x.get('settleCcy') != 'USDT' or x.get('instType') != 'SWAP':
            continue
        rows.append({'symbol': x['instId'], 'base': x['ctValCcy'], 'status': x.get('state'),
                     'listed_ms': int(x.get('listTime') or 0) or None, 'delisted_ms': None})
    return rows


def okx_funding(http, inst, start):
    rows, after = [], None
    for _ in range(20):
        p = {'instId': inst, 'limit': 400}
        if after:
            p['after'] = after
        d = http.get(OKX + '/api/v5/public/funding-rate-history', p)
        L = (d or {}).get('data') or []
        if not L:
            break
        rows += [{'t': int(x['fundingTime']), 'rate': float(x.get('realizedRate') or x['fundingRate'])} for x in L]
        oldest = min(int(x['fundingTime']) for x in L)
        if oldest <= start or len(L) < 400:
            break
        after = oldest
    return sorted({r['t']: r for r in rows if r['t'] >= start}.values(), key=lambda r: r['t'])


def okx_klines(http, inst, start):
    rows, after = [], None
    for _ in range(80):
        p = {'instId': inst, 'bar': '1H', 'limit': 100}
        if after:
            p['after'] = after
        d = http.get(OKX + '/api/v5/market/history-candles', p)
        L = (d or {}).get('data') or []
        if not L:
            break
        rows += [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7] or 0)] for x in L]
        oldest = min(int(x[0]) for x in L)
        if oldest <= start:
            break
        after = oldest
    return sorted({r[0]: r for r in rows if r[0] >= start}.values(), key=lambda r: r[0])


def fetch_meta(raw, http_bn, http_by):
    """Exchange metadata, including delisted perpetuals: Binance keeps them as SETTLING with their delivery date, Bybit
    serves them under status=Closed (paged)."""
    write_json(raw / 'bn_exchangeInfo.json', http_bn.get(BN + '/fapi/v1/exchangeInfo'))
    write_json(raw / 'bn_fundingInfo.json', http_bn.get(BN + '/fapi/v1/fundingInfo'))
    write_json(raw / 'by_instruments_trading.json',
               http_by.get(BY + '/v5/market/instruments-info', {'category': 'linear', 'limit': 1000}))
    cursor, k = None, 0
    while True:
        p = {'category': 'linear', 'limit': 1000, 'status': 'Closed'}
        if cursor:
            p['cursor'] = cursor
        d = http_by.get(BY + '/v5/market/instruments-info', p)
        write_json(raw / ('by_instruments_closed_%d.json' % k), d)
        cursor = (d.get('result') or {}).get('nextPageCursor')
        k += 1
        if not cursor or k > 20:
            break


def bn_funding(http, sym, start, end):
    rows, s = [], start
    for _ in range(60):
        r = http.get(BN + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': end, 'limit': 1000})
        if not isinstance(r, list):
            break
        rows += [{'t': int(x['fundingTime']), 'rate': float(x['fundingRate'])} for x in r]
        if len(r) < 1000:
            break
        s = int(r[-1]['fundingTime']) + 1
    return rows


def bn_klines(http, path, sym, start, end):
    rows, s = [], start
    for _ in range(60):
        r = http.get(BN + path, {'symbol': sym, 'interval': '1h', 'startTime': s, 'endTime': end, 'limit': 1500})
        if not isinstance(r, list) or not r:
            break
        rows += [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7] or 0)] for x in r]
        if len(r) < 1500:
            break
        s = int(r[-1][0]) + HOUR_MS
    return rows


def by_funding(http, sym, start, end):
    rows, e = [], end
    for _ in range(200):
        d = http.get(BY + '/v5/market/funding/history', {'category': 'linear', 'symbol': sym, 'endTime': e,
                                                          'limit': 200})
        L = ((d or {}).get('result') or {}).get('list') or []
        if not L:
            break
        rows += [{'t': int(x['fundingRateTimestamp']), 'rate': float(x['fundingRate'])} for x in L]
        oldest = min(int(x['fundingRateTimestamp']) for x in L)
        if oldest <= start or len(L) < 200:
            break
        e = oldest - 1
    rows = sorted({r['t']: r for r in rows if r['t'] >= start}.values(), key=lambda r: r['t'])
    return rows


def by_klines(http, path, sym, start, end):
    rows, e = [], end
    for _ in range(60):
        d = http.get(BY + path, {'category': 'linear', 'symbol': sym, 'interval': '60', 'start': start, 'end': e,
                                 'limit': 1000})
        L = ((d or {}).get('result') or {}).get('list') or []
        if not L:
            break
        for x in L:
            t = int(x[0])
            turnover = float(x[6]) if len(x) > 6 else 0.0
            rows.append([t, float(x[1]), float(x[2]), float(x[3]), float(x[4]), turnover])
        oldest = min(int(x[0]) for x in L)
        if oldest <= start or len(L) < 1000:
            break
        e = oldest - 1
    return sorted({r[0]: r for r in rows if r[0] >= start}.values(), key=lambda r: r[0])


def hl_universe(hl_store):
    u = json.loads((Path(hl_store) / 'universe.json').read_text())
    return [m['coin'] for m in u['markets'] if m['dex'] == 'core']


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    http_bn = Http(interval=0.4, weight_header='x-mbx-used-weight-1m', weight_soft=1500)
    http_bnf = Http(interval=0.75)            # fundingRate shares a separate 500 / 5 min budget
    http_by = Http(interval=0.12)
    if args.refresh_meta or not (raw / 'bn_exchangeInfo.json').exists():
        fetch_meta(raw, http_bn, http_by)
    hl_coins = hl_universe(args.hl)
    extra = raw / 'hl_extra' / 'delisted.json'
    if extra.exists():
        hl_coins += [c for c in json.loads(extra.read_text())['coins'] if c not in hl_coins]
    bnl, byl = bn_symbols(raw), by_symbols(raw)
    if 'okx' in args.venues.split(',') and not (raw / 'okx_instruments.json').exists():
        write_json(raw / 'okx_instruments.json', Http().get(OKX + '/api/v5/public/instruments', {'instType': 'SWAP'}))
    okl = okx_symbols(raw)
    mapping = map_symbols(hl_coins, bnl, byl, okl)
    write_json(out / 'mapping.json', mapping)
    start = ms_of(args.since)
    end = int(time.time() * 1000) // HOUR_MS * HOUR_MS
    life = {('binance', r['symbol']): r for r in bnl}
    life.update({('bybit', r['symbol']): r for r in byl})
    life.update({('okx', r['symbol']): r for r in okl})
    venues = args.venues.split(',')
    jobs = []
    for coin, m in mapping.items():
        for v in venues:
            sym = m.get(v)
            if not sym:
                continue
            L = life.get((v, sym), {})
            s = max(start, int(L.get('listed_ms') or 0))
            e = min(end, int(L.get('delisted_ms') or end))
            if e > s:
                jobs.append((v, sym, s, e))
    print(json.dumps({'hl_coins': len(hl_coins), 'jobs': len(jobs), 'since': utc(start), 'until': utc(end)}),
          flush=True)

    def bn_job(sym, s, e):
        rec = {}
        fp = raw / 'binance' / 'funding' / (safe(sym) + '.json.gz')
        if not fp.exists() or args.force:
            write_gz(fp, bn_funding(http_bnf, sym, s, e))
        rec['funding'] = len(read_gz(fp))
        for kind, path in (('premium', '/fapi/v1/premiumIndexKlines'), ('klines', '/fapi/v1/klines')):
            kp = raw / 'binance' / kind / (safe(sym) + '.json.gz')
            if not kp.exists() or args.force:
                write_gz(kp, bn_klines(http_bn, path, sym, s, e))
            rec[kind] = len(read_gz(kp))
        return rec

    def by_job(sym, s, e):
        rec = {}
        fp = raw / 'bybit' / 'funding' / (safe(sym) + '.json.gz')
        if not fp.exists() or args.force:
            write_gz(fp, by_funding(http_by, sym, s, e))
        rec['funding'] = len(read_gz(fp))
        for kind, path in (('premium', '/v5/market/premium-index-price-kline'), ('klines', '/v5/market/kline')):
            kp = raw / 'bybit' / kind / (safe(sym) + '.json.gz')
            if not kp.exists() or args.force:
                write_gz(kp, by_klines(http_by, path, sym, s, e))
            rec[kind] = len(read_gz(kp))
        return rec

    http_okx = Http(interval=0.25, backoff_429=4.0)   # history-candles 20 / 2 s, funding history 10 / 2 s

    def okx_job(sym, s, e):
        rec = {}
        s = max(s, ms_of(args.okx_since))
        fp = raw / 'okx' / 'funding' / (safe(sym) + '.json.gz')
        if not fp.exists() or args.force:
            write_gz(fp, okx_funding(http_okx, sym, s))
        rec['funding'] = len(read_gz(fp))
        kp = raw / 'okx' / 'klines' / (safe(sym) + '.json.gz')
        if not kp.exists() or args.force:
            write_gz(kp, okx_klines(http_okx, sym, s))
        rec['klines'] = len(read_gz(kp))
        return rec

    results, failures = {}, {}

    def run(job):
        v, sym, s, e = job
        try:
            fn = {'binance': bn_job, 'bybit': by_job, 'okx': okx_job}[v]
            return job, fn(sym, s, e), None
        except Exception as ex:  # noqa: BLE001 - one symbol failing must not stop the collection
            return job, None, repr(ex)[:200]

    # A pool per venue: each venue's limiter is its own, so the venues run side by side without sharing a budget, and
    # a few threads per venue overlap network latency while the shared limiter keeps the request rate where it was.
    threads = {'binance': args.bn_threads, 'bybit': args.by_threads, 'okx': args.okx_threads}
    pools = {v: cf.ThreadPoolExecutor(max_workers=threads.get(v, 1)) for v in venues}
    futs = [pools[j[0]].submit(run, j) for j in jobs]
    for k, f in enumerate(cf.as_completed(futs), 1):
        job, rec, err = f.result()
        key = '%s:%s' % (job[0], job[1])
        if err:
            failures[key] = err
        else:
            results[key] = rec
        if k % 25 == 0:
            print(json.dumps({'done': k, 'of': len(jobs), 'elapsed_s': round(time.time() - t0),
                              'binance': http_bn.stats(), 'bybit': http_by.stats(),
                              'okx': http_okx.stats()}), flush=True)
    for pool in pools.values():
        pool.shutdown()
    man = {'collected_at': utc(t0 * 1000), 'finished_at': utc(), 'since_utc': utc(start), 'until_utc': utc(end),
           'venues': venues, 'jobs': len(jobs), 'ok': len(results), 'failures': failures,
           'binance_api': {**http_bn.stats(), 'funding_endpoint': http_bnf.stats()}, 'bybit_api': http_by.stats(),
           'okx_api': http_okx.stats(),
           'sources': {'binance': [BN + '/fapi/v1/fundingRate', BN + '/fapi/v1/premiumIndexKlines',
                                   BN + '/fapi/v1/klines', BN + '/fapi/v1/exchangeInfo', BN + '/fapi/v1/fundingInfo'],
                       'bybit': [BY + '/v5/market/funding/history', BY + '/v5/market/premium-index-price-kline',
                                 BY + '/v5/market/kline', BY + '/v5/market/instruments-info']},
           'seconds': round(time.time() - t0, 1)}
    write_json(out / ('collect_manifest_%s.json' % '_'.join(venues)), man)
    print(json.dumps({k: v for k, v in man.items() if k != 'failures'}, indent=1))
    print(json.dumps({'failures': len(failures)}))
    return 0


# ---------------------------------------------------------------------------------------------- Hyperliquid extras

def hl_post(http, body):
    return http.get(HL, body=body)


def spot_perp_map(spot_meta, perp_coins):
    """Spot pairs on Hyperliquid whose base token is the same asset as a core perp.

    The base token is matched by name (HYPE -> HYPE) or as a Unit bridge token (UBTC -> BTC, USOL -> SOL, UFART ->
    FARTCOIN is not guessable and is listed explicitly). Only USDC-quoted pairs are kept, since the perp is margined in
    USDC and the carry should not pick up a second currency. Returns {perp_coin: {'pair': candle coin, 'token': name}}.
    """
    explicit = {'UFART': 'FARTCOIN', 'UPUMP': 'PUMP', 'UBONK': 'kBONK', 'UPEPE': 'kPEPE'}
    tokens = {t['index']: t['name'] for t in spot_meta.get('tokens', [])}
    perps = set(perp_coins)
    out = {}
    for u in spot_meta.get('universe', []):
        base_i, quote_i = u['tokens']
        base, quote = tokens.get(base_i, ''), tokens.get(quote_i, '')
        if quote != 'USDC':
            continue
        coin = None
        if base in perps:
            coin = base
        elif base in explicit and explicit[base] in perps:
            coin = explicit[base]
        elif base.startswith('U') and base[1:] in perps:
            coin = base[1:]
        if coin is None:
            continue
        pair = u['name'] if u.get('index') == 0 or '/' in u['name'] else '@%d' % u['index']
        # Spot tickers collide (an early HIP-1 'PUMP' is not pump.fun's PUMP, which trades as the Unit token UPUMP),
        # so every candidate is kept and the price check in the analysis picks the one that is the same asset.
        out.setdefault(coin, {'pair': pair, 'token': base, 'index': u.get('index'), 'candidates': []})
        out[coin]['candidates'].append({'pair': pair, 'token': base, 'index': u.get('index')})
    return out


def hl_row_live(r):
    """A Hyperliquid funding row from a trading market. Delisted markets keep emitting rows with rate and premium both
    exactly zero; a live market never prints that (its floor is the 1.25bp interest rate, and its premium is a 5-second
    average that is not exactly zero)."""
    return not (fnum(r.get('fundingRate'), 0.0) == 0.0 and fnum(r.get('premium'), 0.0) == 0.0)


def cmd_hl_extra(args):
    """Hyperliquid data the shared perps store does not hold: coins delisted inside the study (survivorship) and spot
    markets (the same-venue carry). Paced far under the venue's weight limit; run after the store's collector is done."""
    out = Path(args.out)
    raw = out / 'raw' / 'hl_extra'
    raw.mkdir(parents=True, exist_ok=True)
    # Hyperliquid's limiter is weight per minute shared with every other client on this IP: pace by interval, and on a
    # 429 wait a short while rather than Binance's minute.
    http = Http(interval=args.interval, backoff_429=10.0)
    meta = hl_post(http, {'type': 'meta'})
    write_json(raw / 'meta.json', meta)
    live = set(hl_universe(args.hl))
    delisted = [u['name'] for u in meta['universe'] if u.get('isDelisted')]
    start = ms_of(TRAIN_START)
    end = int(time.time() * 1000) // HOUR_MS * HOUR_MS
    # Core coins the shared store does not hold (its collector gave up on them under the venue's rate limit): fetched
    # here into hl_extra, which the loader reads when the store has no file.
    store = Path(args.hl)
    missing = sorted(c for c in live if not (store / 'funding' / (safe_hl(c) + '.json.gz')).exists())
    # Only delisted coins that also had a CEX perpetual can enter a pair; the rest are not fetched.
    m = map_symbols(delisted, bn_symbols(out / 'raw'), by_symbols(out / 'raw'))
    pairable = [c for c in delisted if m[c].get('binance') or m[c].get('bybit')]
    kept = []
    for coin in pairable + missing:
        fp = raw / 'funding' / (safe(coin) + '.json.gz')
        if fp.exists():
            if any(hl_row_live(x) for x in read_gz(fp)):
                kept.append(coin)
            continue
        rows, s = [], start
        for _ in range(40):
            r = hl_post(http, {'type': 'fundingHistory', 'coin': coin, 'startTime': s, 'endTime': end})
            if not isinstance(r, list) or not r:
                break
            rows += r
            # A delisted market keeps printing hourly rows with rate and premium exactly zero: a full page of those
            # means it is dead, and the rest of the year is not fetched.
            if len(r) < 500 or not any(hl_row_live(x) for x in r):
                break
            s = int(r[-1]['time']) + 1
        write_gz(fp, rows)
        if any(hl_row_live(x) for x in rows):
            kept.append(coin)
    write_json(raw / 'delisted.json', {'checked': delisted, 'pairable': pairable,
                                      'coins': [c for c in kept if c in set(delisted)],
                                      'store_missing_fetched_here': [c for c in kept if c in set(missing)],
                                      'note': 'delisted on Hyperliquid with at least one funding row since %s'
                                              % TRAIN_START})
    spot = hl_post(http, {'type': 'spotMetaAndAssetCtxs'})
    write_json(raw / 'spot_meta_ctxs.json', spot)
    smap = spot_perp_map(spot[0], sorted(live | set(kept)))
    write_json(raw / 'spot_map.json', smap)
    # Hourly spot candles exist only for the last 5,000 hours; daily ones go back to listing, which is what dates the
    # spot leg's liveness for the earlier part of the year.
    for coin, m in [(c, cand) for c, mm in smap.items() for cand in mm.get('candidates', [mm])]:
        for sub_dir, interval in (('spot_candles', '1h'), ('spot_candles_1d', '1d')):
            fp = raw / sub_dir / (safe(m['pair']) + '.json.gz')
            if fp.exists():
                continue
            r = hl_post(http, {'type': 'candleSnapshot', 'req': {'coin': m['pair'], 'interval': interval,
                                                                  'startTime': start - 30 * DAY_MS, 'endTime': end}})
            write_gz(fp, r if isinstance(r, list) else [])
    # 4-hour candles for every core coin (and the delisted ones): ~2,200 bars a call, weight ~57, so paced by the
    # interval (default 3 s, ~1,140 weight a minute at worst).
    for coin in sorted(live | set(kept)):
        fp = raw / 'candles_4h' / (safe(coin) + '.json.gz')
        if fp.exists():
            continue
        r = hl_post(http, {'type': 'candleSnapshot', 'req': {'coin': coin, 'interval': '4h',
                                                              'startTime': start - 8 * DAY_MS, 'endTime': end}})
        write_gz(fp, r if isinstance(r, list) else [])
    # Delisted perps, store-missing coins and store coins whose candles failed: their last 5,000 hourly candles (the
    # price-ratio check and the hybrid basis need them).
    no_candles = sorted(c for c in live if not (store / 'candles_1h' / (safe_hl(c) + '.json.gz')).exists())
    for coin in sorted(set(kept) | set(no_candles)):
        fp = raw / 'candles_1h' / (safe(coin) + '.json.gz')
        if fp.exists():
            continue
        r = hl_post(http, {'type': 'candleSnapshot', 'req': {'coin': coin, 'interval': '1h',
                                                              'startTime': start, 'endTime': end}})
        write_gz(fp, r if isinstance(r, list) else [])
    try:
        write_json(raw / 'validator_summaries.json', hl_post(http, {'type': 'validatorSummaries'}))
    except Exception as e:  # noqa: BLE001 - the staking add-on is optional
        print('validatorSummaries failed: %r' % e)
    print(json.dumps({'delisted_checked': len(delisted), 'delisted_with_data': len(kept), 'spot_pairs': len(smap),
                      'api': http.stats()}))
    return 0


# ---------------------------------------------------------------------------------------------- live snapshot (capacity)

def walk(levels, notional):
    """Market order of `notional` USD through `levels` [(px, size)] best first: (VWAP, filled USD)."""
    cum_usd = cum_qty = 0.0
    for px, sz in levels:
        take = min(sz * px, notional - cum_usd)
        if take <= 0:
            break
        cum_usd += take
        cum_qty += take / px
        if cum_usd >= notional - 1e-9:
            break
    return (cum_usd / cum_qty if cum_qty else None), cum_usd


def slippage_bp(levels, mid, notional):
    """VWAP distance from mid, in bp, for a market order of `notional` USD; None if the book shown is too thin."""
    if not levels or not mid or notional <= 0:
        return None
    vwap, filled = walk(levels, notional)
    if vwap is None or filled < notional * (1 - 1e-6):
        return None
    return abs(vwap / mid - 1.0) * 1e4


def depth_within(levels, mid, bp):
    """USD resting within `bp` of mid on one side."""
    tot = 0.0
    for px, sz in levels:
        if abs(px / mid - 1.0) * 1e4 > bp + 1e-9:
            break
        tot += px * sz
    return tot


def max_size(levels, mid, max_slip_bp):
    """Largest notional whose market-order VWAP stays within `max_slip_bp` of mid (bisection on the shown book)."""
    if not levels or not mid:
        return 0.0
    total = sum(px * sz for px, sz in levels)
    lo, hi = 0.0, total
    if (slippage_bp(levels, mid, hi) or 1e9) <= max_slip_bp:
        return hi
    for _ in range(50):
        m = (lo + hi) / 2
        s = slippage_bp(levels, mid, m)
        if s is not None and s <= max_slip_bp:
            lo = m
        else:
            hi = m
    return lo


def trim(levels, mid, bp=100):
    out = []
    for px, sz in levels:
        if abs(px / mid - 1.0) * 1e4 > bp:
            break
        out.append([px, sz])
    return out


def cmd_snapshot(args):
    out = Path(args.out)
    snap_p = out / 'snapshot.json'
    snap = json.loads(snap_p.read_text()) if snap_p.exists() else {}
    mapping = json.loads((out / 'mapping.json').read_text())
    venues = args.venues.split(',')
    t0 = time.time()
    if 'binance' in venues:
        http = Http(interval=0.35, weight_header='x-mbx-used-weight-1m', weight_soft=1500)
        tick = {x['symbol']: x for x in http.get(BN + '/fapi/v1/ticker/24hr')}
        prem = {x['symbol']: x for x in http.get(BN + '/fapi/v1/premiumIndex')}
        bn = {}
        for coin, m in mapping.items():
            sym = m.get('binance')
            if not sym or sym not in tick:
                continue
            d = http.get(BN + '/fapi/v1/depth', {'symbol': sym, 'limit': 500})
            oi = http.get(BN + '/fapi/v1/openInterest', {'symbol': sym})
            if not isinstance(d, dict) or 'bids' not in d:
                continue
            bids = [[float(p), float(q)] for p, q in d['bids']]
            asks = [[float(p), float(q)] for p, q in d['asks']]
            if not bids or not asks:
                continue
            mid = (bids[0][0] + asks[0][0]) / 2
            mark = fnum(prem.get(sym, {}).get('markPrice'), mid)
            bn[sym] = {'mid': mid, 'bid': bids[0][0], 'ask': asks[0][0],
                       'half_spread_bp': (asks[0][0] - bids[0][0]) / 2 / mid * 1e4,
                       'bids': trim(bids, mid), 'asks': trim(asks, mid),
                       'oi_usd': fnum(oi.get('openInterest'), 0) * mark if isinstance(oi, dict) else None,
                       'vol24_usd': fnum(tick[sym].get('quoteVolume')),
                       'funding_rate': fnum(prem.get(sym, {}).get('lastFundingRate'))}
        snap['binance'] = {'at': utc(), 'books': bn}
    if 'bybit' in venues:
        http = Http(interval=0.12)
        tk = http.get(BY + '/v5/market/tickers', {'category': 'linear'})
        tick = {x['symbol']: x for x in tk['result']['list']}
        by = {}
        for coin, m in mapping.items():
            sym = m.get('bybit')
            if not sym or sym not in tick:
                continue
            d = http.get(BY + '/v5/market/orderbook', {'category': 'linear', 'symbol': sym, 'limit': 500})
            r = (d or {}).get('result') or {}
            bids = [[float(p), float(q)] for p, q in r.get('b', [])]
            asks = [[float(p), float(q)] for p, q in r.get('a', [])]
            if not bids or not asks:
                continue
            mid = (bids[0][0] + asks[0][0]) / 2
            by[sym] = {'mid': mid, 'bid': bids[0][0], 'ask': asks[0][0],
                       'half_spread_bp': (asks[0][0] - bids[0][0]) / 2 / mid * 1e4,
                       'bids': trim(bids, mid), 'asks': trim(asks, mid),
                       'oi_usd': fnum(tick[sym].get('openInterestValue')),
                       'vol24_usd': fnum(tick[sym].get('turnover24h')),
                       'funding_rate': fnum(tick[sym].get('fundingRate'))}
        snap['bybit'] = {'at': utc(), 'books': by}
    if 'okx' in venues:
        http = Http(interval=0.25)
        inst = {x['instId']: x for x in json.loads((out / 'raw' / 'okx_instruments.json').read_text())['data']}
        oi = {x['instId']: x for x in (http.get(OKX + '/api/v5/public/open-interest', {'instType': 'SWAP'}) or {}).get('data', [])}
        tk = {x['instId']: x for x in (http.get(OKX + '/api/v5/market/tickers', {'instType': 'SWAP'}) or {}).get('data', [])}
        ok = {}
        for coin, m in mapping.items():
            sym = m.get('okx')
            if not sym or sym not in inst:
                continue
            ctv = fnum(inst[sym].get('ctVal'), 1.0)
            d = http.get(OKX + '/api/v5/market/books', {'instId': sym, 'sz': 400})
            L = (d or {}).get('data') or []
            if not L:
                continue
            bids = [[float(x[0]), float(x[1]) * ctv] for x in L[0].get('bids', [])]
            asks = [[float(x[0]), float(x[1]) * ctv] for x in L[0].get('asks', [])]
            if not bids or not asks:
                continue
            mid = (bids[0][0] + asks[0][0]) / 2
            ok[sym] = {'mid': mid, 'bid': bids[0][0], 'ask': asks[0][0],
                       'half_spread_bp': (asks[0][0] - bids[0][0]) / 2 / mid * 1e4,
                       'bids': trim(bids, mid), 'asks': trim(asks, mid),
                       'oi_usd': fnum((oi.get(sym) or {}).get('oiUsd')),
                       'vol24_usd': (fnum((tk.get(sym) or {}).get('volCcy24h'), 0) or 0) * mid}
        snap['okx'] = {'at': utc(), 'books': ok}
    if 'hl' in venues:
        http = Http(interval=args.hl_interval, backoff_429=10.0)
        mc = hl_post(http, {'type': 'metaAndAssetCtxs'})
        ctx = {u['name']: c for u, c in zip(mc[0]['universe'], mc[1])}
        hl = {}
        for coin in mapping:
            if coin not in ctx:
                continue
            d = hl_post(http, {'type': 'l2Book', 'coin': coin})
            if not isinstance(d, dict) or not d.get('levels'):
                continue
            bids = [[float(x['px']), float(x['sz'])] for x in d['levels'][0]]
            asks = [[float(x['px']), float(x['sz'])] for x in d['levels'][1]]
            if not bids or not asks:
                continue
            mid = (bids[0][0] + asks[0][0]) / 2
            # The venue shows 20 levels a side; on a liquid coin that is a few bp. The same book aggregated to four
            # significant figures reaches much further, at bucket prices no better than the orders in them.
            dc = hl_post(http, {'type': 'l2Book', 'coin': coin, 'nSigFigs': 4})
            cb = [[float(x['px']), float(x['sz'])] for x in dc['levels'][0]] if isinstance(dc, dict) and dc.get('levels') else []
            ca = [[float(x['px']), float(x['sz'])] for x in dc['levels'][1]] if isinstance(dc, dict) and dc.get('levels') else []
            c = ctx[coin]
            mark = fnum(c.get('markPx'), mid)
            hl[coin] = {'mid': mid, 'bid': bids[0][0], 'ask': asks[0][0],
                        'half_spread_bp': (asks[0][0] - bids[0][0]) / 2 / mid * 1e4,
                        'bids': trim(bids, mid), 'asks': trim(asks, mid),
                        'bids_coarse': trim(cb, mid), 'asks_coarse': trim(ca, mid),
                        'levels_shown': [len(bids), len(asks)],
                        'oi_usd': fnum(c.get('openInterest'), 0) * mark, 'vol24_usd': fnum(c.get('dayNtlVlm')),
                        'funding_rate': fnum(c.get('funding')), 'premium': fnum(c.get('premium'))}
        snap['hl'] = {'at': utc(), 'books': hl, 'note': 'l2Book shows at most 20 levels a side, so depth beyond '
                                                       'them is a lower bound'}
        smap_p = out / 'raw' / 'hl_extra' / 'spot_map.json'
        if smap_p.exists():
            spot = {}
            for coin, m in [(c, cand) for c, mm in json.loads(smap_p.read_text()).items()
                            for cand in mm.get('candidates', [mm])]:
                d = hl_post(http, {'type': 'l2Book', 'coin': m['pair']})
                if not isinstance(d, dict) or not d.get('levels'):
                    continue
                bids = [[float(x['px']), float(x['sz'])] for x in d['levels'][0]]
                asks = [[float(x['px']), float(x['sz'])] for x in d['levels'][1]]
                if not bids or not asks:
                    continue
                mid = (bids[0][0] + asks[0][0]) / 2
                spot[m['pair']] = {'coin': coin, 'token': m['token'], 'mid': mid,
                                   'half_spread_bp': (asks[0][0] - bids[0][0]) / 2 / mid * 1e4,
                                   'bids': trim(bids, mid), 'asks': trim(asks, mid)}
            snap['hl_spot'] = {'at': utc(), 'books': spot}
    snap['seconds_last_run'] = round(time.time() - t0, 1)
    write_json(snap_p, snap)
    print(json.dumps({v: len(snap.get(v, {}).get('books', {})) for v in ('binance', 'bybit', 'okx', 'hl', 'hl_spot')}))
    return 0


# ---------------------------------------------------------------------------------------------- series on one grid

def hour_of(ms):
    """The hour a settlement belongs to: payments land a few milliseconds after the boundary."""
    return int((int(ms) + HOUR_MS // 2) // HOUR_MS * HOUR_MS)


class Venue:
    """One venue's view of one coin on the study grid: settlements, premium, trade close, liveness.

    `pay[j]` is the funding settled at hour j (0 between settlements), `prem[j]` the premium index at hour j
    forward-filled inside the live range, `px[j]` the trade close of the hour ending at j (None where missing), and
    `live[j]` whether the market existed (first to last settlement, inclusive)."""

    def __init__(self, n):
        self.pay = [0.0] * n
        self.prem = [None] * n
        self.px = [None] * n
        self.live = [False] * n
        self.settlements = 0
        self.interval_hours = {}

    def fill(self, t0, n, settlements, premium, closes):
        """settlements: [(ms, rate)]; premium: {hour_ms: value at that hour}; closes: {hour_ms: close at that hour}."""
        hours = sorted(hour_of(t) for t, _ in settlements)
        for t, r in settlements:
            j = (hour_of(t) - t0) // HOUR_MS
            if 0 <= j < n:
                self.pay[j] += r
                self.settlements += 1
        for a, b in zip(hours, hours[1:]):
            h = (b - a) // HOUR_MS
            self.interval_hours[h] = self.interval_hours.get(h, 0) + 1
        if not hours:
            return self
        # Live from the first settlement until one usual interval after the last: an 8-hour market is open between
        # its settlements, and ending it at the last one would close every 8-hour pair for the final seven hours.
        tail = max(self.interval_hours, key=self.interval_hours.get) - 1 if self.interval_hours else 0
        j0 = max(0, (hours[0] - t0) // HOUR_MS)
        j1 = min(n - 1, (hours[-1] - t0) // HOUR_MS + tail)
        last = None
        for j in range(j0, j1 + 1):
            self.live[j] = True
            h = t0 + j * HOUR_MS
            v = premium.get(h)
            if v is not None:
                last = v
            self.prem[j] = last
            self.px[j] = closes.get(h)
        return self


def load_hl_venue(store, coin, t0, n, extra=None):
    fp = Path(store) / 'funding' / (safe_hl(coin) + '.json.gz')
    if not fp.exists() and extra is not None:
        fp = Path(extra) / 'funding' / (safe(coin) + '.json.gz')
    if not fp.exists():
        return None
    rows = [r for r in read_gz(fp) if hl_row_live(r)]
    sett = [(int(r['time']), float(r['fundingRate'])) for r in rows]
    prem = {hour_of(r['time']): float(r['premium']) for r in rows if r.get('premium') is not None}
    closes, src = {}, {'1h': 0, '4h': 0}
    if extra is not None:
        # 4-hour candles reach back ~830 days (the venue serves 5,000 bars of any interval), so before mid-March 2026
        # the HL leg has a real close every fourth hour, at exactly the decision hours of the fast family.
        cp4 = Path(extra) / 'candles_4h' / (safe(coin) + '.json.gz')
        if cp4.exists():
            for c in read_gz(cp4):
                closes[int(c['t']) + 4 * HOUR_MS] = float(c['c'])
            src['4h'] = len(closes)
    cp = Path(store) / 'candles_1h' / (safe_hl(coin) + '.json.gz')
    if not cp.exists() and extra is not None:
        cp = Path(extra) / 'candles_1h' / (safe(coin) + '.json.gz')
    if cp.exists():
        for c in read_gz(cp):
            closes[int(c['t']) + HOUR_MS] = float(c['c'])
            src['1h'] += 1
    v = Venue(n).fill(t0, n, sett, prem, closes)
    v.price_sources = src
    return v


def safe_hl(coin):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from perp_collect import safe as s  # the store's own file naming
    return s(coin)


def load_cex_venue(raw, venue, sym, t0, n):
    fp = Path(raw) / venue / 'funding' / (safe(sym) + '.json.gz')
    if not fp.exists():
        return None
    sett = [(int(r['t']), float(r['rate'])) for r in read_gz(fp)]
    prem, closes = {}, {}
    pp = Path(raw) / venue / 'premium' / (safe(sym) + '.json.gz')
    if pp.exists():
        for k in read_gz(pp):
            prem[int(k[0]) + HOUR_MS] = float(k[4])
    kp = Path(raw) / venue / 'klines' / (safe(sym) + '.json.gz')
    if kp.exists():
        for k in read_gz(kp):
            closes[int(k[0]) + HOUR_MS] = float(k[4])
    if not pp.exists():
        # No premium history (OKX): both legs carry real closes over its whole window, so the premium only stands in
        # for an hour that lacks one; zero is that stand-in.
        prem = {h: 0.0 for h in closes}
    return Venue(n).fill(t0, n, sett, prem, closes)


def prefix(xs):
    p = [0.0]
    for x in xs:
        p.append(p[-1] + x)
    return p


class Pair:
    """Short leg A, long leg B, on one coin, priced exactly as a fixed-quantity position.

    Entering at hour i with notional 1 on each leg (short 1/pa[i] of A, long 1/pb[i] of B), the position is worth, at
    hour t,  (pb[t]/pb[i] - 1) - (pa[t]/pa[i] - 1)  in basis, plus the funding each leg's quantity received:
    sum over settlements of (rateA - rateB) * pb[t]/pb[i]. Both are computed from price *levels* rather than summed
    returns, so a coin that halves while held is not mispriced (summing log returns overstated SAGA's basis 3.6x).

    Price levels: each leg's own hourly trade close where it exists; where it does not (Hyperliquid serves only its last
    5,000 hourly candles, so before mid-March 2026), the level is synthesised from the other leg through the two premium
    indices, pa = pb * (1 + premA) / (1 + premB) — the two venues quoting the same spot index, each at its own premium.
    `basis='premium'` synthesises A from B everywhere, which is the proxy the early months rely on; comparing the two
    on the late months says how good that proxy is. For the spot–perp carry, B is the spot leg: no funding, premium 0.
    """

    def __init__(self, coin, A, B, n, long_only=False, a_name='A', b_name='B', basis='hybrid', unit_ratio=1.0):
        # unit_ratio: coins per quoted unit on A over the same on B (HL TURBO is 1 TURBO, Bybit 1000TURBOUSDT is 1,000:
        # 1/1000), so a level synthesised from the other leg is in this leg's own units.
        self.coin, self.n, self.long_only, self.a_name, self.b_name = coin, n, long_only, a_name, b_name
        self.unit_ratio = unit_ratio
        s, av = [0.0] * n, [0] * n
        pa, pb = [None] * n, [None] * n
        la = lb = None
        self.price_hours = 0
        for j in range(n):
            xa = A.px[j] if basis != 'premium' else None
            xb = B.px[j]
            qa, qb = A.prem[j], B.prem[j]
            if xb is None and xa is not None and qa is not None and qb is not None:
                xb = xa / unit_ratio * (1 + qb) / (1 + qa)
            if xa is None and xb is not None and qa is not None and qb is not None:
                xa = xb * unit_ratio * (1 + qa) / (1 + qb)
            if xa is not None and A.px[j] is not None and B.px[j] is not None and basis != 'premium':
                self.price_hours += 1
            la = xa if xa is not None else la
            lb = xb if xb is not None else lb
            pa[j], pb[j] = la, lb
            if A.live[j] and B.live[j] and qa is not None and qb is not None and la and lb:
                av[j] = 1
                s[j] = A.pay[j] - B.pay[j]
        self.s, self.av, self.pa, self.pb = s, av, pa, pb
        self.S, self.AV = prefix(s), prefix(av)
        self.SP = prefix([x * (y or 0.0) for x, y in zip(s, pb)])
        self.A, self.B = A, B

    def window(self, i, k, min_cover=0.95):
        """Annualised mean spread over the observable hours among i-k+1..i, or None when fewer than 95% of them are
        observable (one missing hour must not close a position whose signal is three months long)."""
        if i - k + 1 < 0:
            return None
        m = self.AV[i + 1] - self.AV[i - k + 1]
        if m < math.ceil(min_cover * k):
            return None
        return (self.S[i + 1] - self.S[i - k + 1]) * HOURS_PER_YEAR / m

    def value(self, i, t):
        """Basis value at hour t of (short A, long B) entered at hour i, per unit notional."""
        return (self.pb[t] / self.pb[i] - 1.0) - (self.pa[t] / self.pa[i] - 1.0)

    def funding(self, i, lo, hi):
        """Funding received over settlements lo..hi by (short A, long B) entered at hour i, quantity held fixed."""
        return (self.SP[hi + 1] - self.SP[lo]) / self.pb[i]

    def hold(self, i, e):
        """(funding, basis) per unit notional for (short A, long B) held over hours (i, e]."""
        return self.funding(i, i + 1, e), self.value(i, e)


def simulate(pair, k, X, Y, H, step, cost_entry, cost_exit, start=0, end=None):
    """The entry/exit state machine. Decisions at hours i = start, start+step, ... (the grid starts at 00:00 UTC, so a
    4-hour step decides at the funding hours of every venue).

    flat:       enter d = sign(S) when |S| >= X (only d = +1 when the pair is long-only)
    holding d:  exit when d*S < Y, when the hold reaches H hours, or when the pair stops being observable;
                after an exit, enter the other way at the same decision if -d*S >= X.
    Costs are fractions of notional, charged per entry and per exit. Returns the list of trades
    [{'d', 'i', 'e', 'funding', 'basis', 'cost', 'net', 'forced'}], funding and basis already signed by d.
    """
    end = pair.n - 1 if end is None else end
    trades, d, ei = [], 0, None

    def close(e, forced=False):
        f, b = pair.hold(ei, e)
        f, b = d * f, d * b
        c = cost_entry + cost_exit
        trades.append({'d': d, 'i': ei, 'e': e, 'funding': f, 'basis': b, 'cost': c, 'net': f + b - c,
                       'forced': forced})

    i = start
    while i <= end:
        S = pair.window(i, k)
        if d != 0:
            if S is None or not pair.av[i]:
                close(i, forced=True)
                d = 0
            elif d * S < Y or (H is not None and i - ei >= H):
                close(i)
                prev, d = d, 0
                if -prev * S >= X and not (pair.long_only and -prev < 0):
                    d, ei = -prev, i
        elif S is not None and abs(S) >= X:
            dd = 1 if S > 0 else -1
            if not (pair.long_only and dd < 0):
                d, ei = dd, i
        i += step
    if d != 0:
        close(min(end, pair.n - 1), forced=True)
    return trades


def daily_pnl(pair, trades, n_days):
    """Per-day P&L and deployed capital (in position-days) of a coin's trades; costs land on entry and exit days."""
    pnl = [0.0] * n_days
    cap = [0.0] * n_days
    for t in trades:
        i, e, d = t['i'], t['e'], t['d']
        half = t['cost'] / 2
        if i // 24 < n_days:
            pnl[i // 24] -= half
        if e // 24 < n_days:
            pnl[e // 24] -= half
        j = i + 1
        while j <= e:
            day = j // 24
            hi = min(e, day * 24 + 23)
            f = pair.funding(i, j, hi)
            b = pair.value(i, hi) - pair.value(i, j - 1)
            if day < n_days:
                pnl[day] += d * (f + b)
                cap[day] += (hi - j + 1) / 24.0
            j = hi + 1
    return pnl, cap


def leg_cost(fee_bp, half_spread_bp):
    return (fee_bp + half_spread_bp) / 1e4


# ---------------------------------------------------------------------------------------------- analysis

GRID_K = (24, 72, 168)                      # trailing hours the signal averages
GRID_X = (0.10, 0.20, 0.30, 0.50, 1.00)     # annualised spread to enter
GRID_Y = ('zero', 'half')                   # exit when the held spread falls below 0, or below X/2
GRID_H = (168, 720, None)                   # maximum hold in hours
STEP = 4                                    # hours between decisions (the grid starts at 00:00 UTC)
SPOT_X = (0.05, 0.10, 0.20, 0.30, 0.50)
PAIR_TYPES = {'hl_binance': ('hl', 'binance'), 'hl_bybit': ('hl', 'bybit'), 'binance_bybit': ('binance', 'bybit'),
              'hl_okx': ('hl', 'okx')}
CAP_SLIP_BP = 10.0                          # capacity: the size whose market-order VWAP stays within this of mid
CAP_OI_SHARE = 0.05                         # ... and no more than this share of the smaller venue's open interest
SIZE_LIMITS = (10_000, 25_000, 50_000)      # the same book with every coin capped at a fixed size (or its capacity)
MISSING_HALF_SPREAD_BP = 5.0                # half-spread charged where the snapshot has no book (delisted markets)


SLOW_K = (720, 2160)                        # 30 and 90 days: the structural-spread family
SLOW_X = (0.02, 0.04, 0.06, 0.08)
SLOW_STEP = 168                             # decided weekly


def variants_grid():
    """Two families on one state machine. Fast: trailing 1–7 days, entry 10–100% a year, decided every 4 hours —
    episodes. Slow: trailing 30 or 90 days, entry 2–8% a year, decided weekly — a coin's structural spread."""
    out = []
    for k in GRID_K:
        for X in GRID_X:
            for yk in GRID_Y:
                for H in GRID_H:
                    out.append({'name': 'k%d_X%d_Y%s_H%s' % (k, round(X * 100), yk, H or 'inf'), 'k': k, 'X': X,
                                'Y': 0.0 if yk == 'zero' else X / 2, 'H': H, 'step': STEP, 'family': 'fast'})
    for k in SLOW_K:
        for X in SLOW_X:
            for yk in GRID_Y:
                out.append({'name': 'slow_k%dd_X%d_Y%s' % (k // 24, round(X * 100), yk), 'k': k, 'X': X,
                            'Y': 0.0 if yk == 'zero' else X / 2, 'H': None, 'step': SLOW_STEP, 'family': 'slow'})
    return out


def spot_variants():
    out = [{'name': 'always_on', 'k': 24, 'X': -1e9, 'Y': -1e9, 'H': None, 'step': STEP, 'family': 'always'}]
    for k in GRID_K:
        for X in SPOT_X:
            for yk in GRID_Y:
                out.append({'name': 'k%d_X%d_Y%s' % (k, round(X * 100), yk), 'k': k, 'X': X,
                            'Y': 0.0 if yk == 'zero' else X / 2, 'H': None, 'step': STEP, 'family': 'fast'})
    return out


def price_ratio(A, B, mult_a, mult_b, last=1000):
    """Median of (A/mult_a)/(B/mult_b) over the latest hours where both trade closes exist: ~1 when two listings
    are the same asset in the same units. None with under a day of overlap."""
    r = []
    for j in range(len(A.px) - 1, -1, -1):
        a, b = A.px[j], B.px[j]
        if a and b:
            r.append((a / mult_a) / (b / mult_b))
            if len(r) >= last:
                break
    return statistics.median(r) if len(r) >= 24 else None


def corr(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None


def load_study(out, hl_store, start=TRAIN_START):
    out, hl_store = Path(out), Path(hl_store)
    raw = out / 'raw'
    extra = raw / 'hl_extra'
    uni = json.loads((hl_store / 'universe.json').read_text())
    t0 = ms_of(start)
    t_end = int(dt.datetime.fromisoformat(uni['until_utc']).timestamp() * 1000)
    n = (t_end - t0) // HOUR_MS + 1
    mapping = json.loads((out / 'mapping.json').read_text())
    V = {}
    for coin, m in mapping.items():
        hv = load_hl_venue(hl_store, coin, t0, n, extra)
        if hv is not None and hv.settlements:
            V[('hl', coin)] = hv
        for v in ('binance', 'bybit', 'okx'):
            if m.get(v):
                cv = load_cex_venue(raw, v, m[v], t0, n)
                if cv is not None and cv.settlements:
                    V[(v, coin)] = cv
    return t0, n, mapping, V


def hl_price_sources(V, t0, n):
    """Share of live HL hours with a real trade close, before and after the 1-hour candles begin."""
    tot = real = 0
    first_1h = []
    for (venue, coin), v in V.items():
        if venue != 'hl':
            continue
        for j in range(n):
            if v.live[j]:
                tot += 1
                real += 1 if v.px[j] else 0
        first = next((j for j in range(n) if v.px[j] and j % 4), None)
        if first is not None:
            first_1h.append(first)
    return {'live_hours': tot, 'hours_with_real_close': real, 'share': (real / tot) if tot else None,
            'first_hourly_close_utc_median': utc(t0 + statistics.median(first_1h) * HOUR_MS) if first_1h else None}


def check_mapping(mapping, V):
    """Drop any CEX listing whose price, in units, is not the HL coin's (a name collision, a redenomination)."""
    report, dropped = {}, []
    for coin, m in mapping.items():
        hv = V.get(('hl', coin))
        for v in ('binance', 'bybit'):
            cv = V.get((v, coin))
            if cv is None:
                continue
            if hv is None:
                # No Hyperliquid leg loaded: check the two CEX listings against each other instead, which is what the
                # CEX–CEX control trades.
                other = 'bybit' if v == 'binance' else 'binance'
                ov = V.get((other, coin))
                r = price_ratio(cv, ov, m.get(v + '_mult', 1), m.get(other + '_mult', 1)) if ov is not None else None
                ok = r is None or 0.97 <= r <= 1.03
                report['%s:%s' % (v, coin)] = {'ratio_vs_' + other: r, 'ok': ok, 'hl_leg': 'missing'}
                if not ok:
                    dropped.append('%s:%s' % (v, coin))
                    del V[(v, coin)]
                continue
            r = price_ratio(hv, cv, m['hl_mult'], m.get(v + '_mult', 1))
            if r is None:
                # No overlapping trade closes (a delisted leg): fall back to the premium series agreeing in sign
                # more often than not, which a different asset would not do systematically.
                xs, ys = [], []
                if hv is not None:
                    for j in range(len(cv.prem)):
                        if hv.live[j] and cv.live[j] and hv.prem[j] is not None and cv.prem[j] is not None:
                            xs.append(hv.prem[j])
                            ys.append(cv.prem[j])
                c = corr(xs, ys)
                ok = c is not None and c > 0.2
                report['%s:%s' % (v, coin)] = {'ratio': None, 'premium_corr': c, 'ok': ok}
            else:
                ok = 0.97 <= r <= 1.03
                report['%s:%s' % (v, coin)] = {'ratio': r, 'ok': ok}
            if not ok:
                dropped.append('%s:%s' % (v, coin))
                del V[(v, coin)]
    return report, dropped


def half_spread(snap, venue, key):
    b = ((snap.get(venue) or {}).get('books') or {}).get(key)
    if not b:
        return MISSING_HALF_SPREAD_BP
    return max(0.25, b['half_spread_bp'])


def venue_key(venue, coin, mapping):
    return coin if venue == 'hl' else mapping[coin].get(venue)


def unit_mult(m, venue):
    """Coins per quoted unit of this coin on this venue (kPEPE and 1000PEPEUSDT are 1,000; OKX quotes per coin)."""
    return m.get('hl_mult', 1) if venue == 'hl' else m.get(venue + '_mult', 1)


def build_pairs(kind, mapping, V, n, snap, fees):
    va, vb = PAIR_TYPES[kind]
    pairs, costs = {}, {}
    for coin in mapping:
        A, Bv = V.get((va, coin)), V.get((vb, coin))
        if A is None or Bv is None:
            continue
        pr = Pair(coin, A, Bv, n, a_name=va, b_name=vb, unit_ratio=unit_mult(mapping[coin], va) / unit_mult(mapping[coin], vb))
        if pr.AV[-1] < 24 * 7:
            continue
        pairs[coin] = pr
        c = (leg_cost(fees[va], half_spread(snap, va, venue_key(va, coin, mapping)))
             + leg_cost(fees[vb], half_spread(snap, vb, venue_key(vb, coin, mapping))))
        costs[coin] = (c, c)
    return pairs, costs


def live_counts(pairs, n_days):
    cnt = [0] * n_days
    for pr in pairs.values():
        for d in range(n_days):
            a, b = d * 24, min(pr.n, d * 24 + 24)
            if a < pr.n and pr.AV[b] - pr.AV[a] >= 12:
                cnt[d] += 1
    return cnt


def run_grid(pairs, costs, variants, n_days, step=STEP):
    """Daily P&L and deployed capital of every variant, summed over coins. Trades are not kept (re-simulated for the
    chosen variant), so a 90-variant grid over 170 coins fits in memory."""
    res = {}
    for v in variants:
        P, C = [0.0] * n_days, [0.0] * n_days
        ntr = 0
        for coin, pr in pairs.items():
            ce, cx = costs[coin]
            tr = simulate(pr, v['k'], v['X'], v['Y'], v['H'], v.get('step', step), ce, cx)
            ntr += len(tr)
            if not tr:
                continue
            pnl, cap = daily_pnl(pr, tr, n_days)
            P = [a + b for a, b in zip(P, pnl)]
            C = [a + b for a, b in zip(C, cap)]
        res[v['name']] = {'P': P, 'C': C, 'trades': ntr, 'variant': v}
    return res


def month_starts(t0, n_days):
    out, d = [], 0
    while d < n_days:
        t = dt.datetime.fromtimestamp((t0 + d * DAY_MS) / 1000, dt.timezone.utc)
        if t.day == 1:
            out.append(d)
        d += 1
    return out


def walk_forward(series, t0, n_days, min_train=90):
    names = list(series)
    ms = month_starts(t0, n_days) + [n_days]
    oos, picks = [], []
    for a, b in zip(ms, ms[1:]):
        if a < min_train or b <= a:
            continue

        def sh(k):
            p = B.perf(series[k][:a], 365).get('sharpe')
            return -1e18 if p is None else p
        best = max(names, key=sh)
        oos.extend(series[best][a:b])
        picks.append({'month': utc(t0 + a * DAY_MS)[:7], 'chosen': best,
                      'month_return': sum(series[best][a:b])})
    return oos, picks


def excursions(pr, trs, levels=(0.25, 0.40)):
    """Worst move against each leg while a trade was held (hourly price levels). The legs are margined on different
    venues, so a hedge that is flat in total can still need collateral moved before one side is liquidated: at 2x a
    leg is wiped out by a 50% move against it, and margin has to be moved well before that."""
    worst = []
    for t in trs:
        i, e, d = t['i'], t['e'], t['d']
        a0, b0 = pr.pa[i], pr.pb[i]
        w = 0.0
        for j in range(i + 1, e + 1):
            ra, rb = pr.pa[j] / a0 - 1.0, pr.pb[j] / b0 - 1.0
            # d = +1: short A (hurt by A rising), long B (hurt by B falling); d = -1 the other way round
            adv = max(ra, -rb) if d > 0 else max(-ra, rb)
            w = max(w, adv)
        worst.append(w)
    out = {'trades': len(worst)}
    for lv in levels:
        out['share_over_%d%%' % round(100 * lv)] = (sum(1 for x in worst if x > lv) / len(worst)) if worst else None
    out['median_worst'] = statistics.median(worst) if worst else None
    return out


def trade_stats(trs, hours_per_year=HOURS_PER_YEAR):
    if not trs:
        return {'n': 0}
    held = [t['e'] - t['i'] for t in trs]
    net = [t['net'] for t in trs]
    return {'n': len(trs), 'mean_hours': sum(held) / len(held), 'median_hours': statistics.median(held),
            'mean_funding_bp': 1e4 * sum(t['funding'] for t in trs) / len(trs),
            'mean_basis_bp': 1e4 * sum(t['basis'] for t in trs) / len(trs),
            'mean_cost_bp': 1e4 * sum(t['cost'] for t in trs) / len(trs),
            'mean_net_bp': 1e4 * sum(net) / len(net), 'median_net_bp': 1e4 * statistics.median(net),
            'hit_rate': sum(1 for x in net if x > 0) / len(net),
            'forced_exits': sum(1 for t in trs if t['forced']),
            'net_per_position_year': (sum(net) / sum(held) * hours_per_year) if sum(held) else None}


def nearest_px(V, j, tol=1):
    for dj in range(0, tol + 1):
        for jj in (j - dj, j + dj):
            if 0 <= jj < len(V.px) and V.px[jj]:
                return V.px[jj]
    return None


def proxy_check(pr_hybrid, pr_premium, trs):
    """The same trades priced twice: on real trade closes (hybrid, which is real prices wherever both legs have them)
    and on the premium-index proxy the early months depend on. Only trades whose whole life has real closes on both
    legs are compared, so the gap is the proxy's error and nothing else."""
    a, b = [], []
    for t in trs:
        i, e = t['i'], t['e']
        if not all(pr_hybrid.A.px[j] and pr_hybrid.B.px[j] for j in (i, e)):
            continue
        a.append(t['d'] * pr_hybrid.value(i, e))
        b.append(t['d'] * pr_premium.value(i, e))
    return a, b


def capacity(snap, legs, oi_share=CAP_OI_SHARE, max_slip=CAP_SLIP_BP, size_limit=None):
    """legs: [(venue, key)]. Largest notional tradable in both directions on every leg within `max_slip` of mid, capped
    at `oi_share` of the smaller open interest; and the per-fill slippage at that size, averaged over the two sides."""
    sizes, ois, books = [], [], []
    for venue, key in legs:
        bk = ((snap.get(venue) or {}).get('books') or {}).get(key)
        if not bk:
            return None
        books.append(bk)
        for side in ('bids', 'asks'):
            # Two lower bounds of the same depth (the levels shown, and the aggregated book): the larger one holds.
            q_side = max(max_size(bk[side], bk['mid'], max_slip),
                         max_size(bk.get(side + '_coarse') or [], bk['mid'], max_slip))
            sizes.append(q_side)
        if bk.get('oi_usd'):
            ois.append(bk['oi_usd'])
    q = min(sizes) if sizes else 0.0
    if ois:
        q = min(q, oi_share * min(ois))
    if size_limit is not None:
        q = min(q, size_limit)
    slips = []
    for bk in books:
        per_side = []
        for side in ('bids', 'asks'):
            cands = [x for x in (slippage_bp(bk[side], bk['mid'], q),
                                 slippage_bp(bk.get(side + '_coarse') or [], bk['mid'], q)) if x is not None]
            per_side.append(min(cands) if cands and q > 0 else (0.0 if q <= 0 else max_slip))
        slips.append(sum(per_side) / 2)
    return {'size_usd': q, 'slip_bp_per_fill': slips, 'oi_usd': ois}


def peak_concurrent(trades_by_coin, size_by_coin, start, end):
    ev = []
    for coin, trs in trades_by_coin.items():
        q = size_by_coin.get(coin, 0.0)
        for t in trs:
            if t['e'] <= start or t['i'] >= end or q <= 0:
                continue
            ev.append((max(t['i'], start), q))
            ev.append((min(t['e'], end), -q))
    ev.sort(key=lambda x: (x[0], x[1]))
    cur = peak = 0.0
    for _, q in ev:
        cur += q
        peak = max(peak, cur)
    return peak


def spread_profile(pairs, test_hour):
    """Per coin: mean annualised spread (A − B), its sign persistence, and how often a trailing day exceeded 20%."""
    out = {}
    for coin, pr in pairs.items():
        n_av = pr.AV[-1]
        if n_av < 24 * 14:
            continue
        mean_all = pr.S[-1] / n_av * HOURS_PER_YEAR
        tr_av = pr.AV[test_hour + 1] if test_hour + 1 < len(pr.AV) else pr.AV[-1]
        te_av = n_av - tr_av
        mean_tr = (pr.S[test_hour + 1] / tr_av * HOURS_PER_YEAR) if tr_av > 24 * 7 else None
        mean_te = ((pr.S[-1] - pr.S[test_hour + 1]) / te_av * HOURS_PER_YEAR) if te_av > 24 * 7 else None
        days = []
        for d in range(pr.n // 24):
            a, b = d * 24, d * 24 + 24
            if pr.AV[b] - pr.AV[a] == 24:
                days.append((pr.S[b] - pr.S[a]) * 365)
        wide = sum(1 for x in days if abs(x) > 0.20) / len(days) if days else None
        ac1 = corr(days[:-1], days[1:]) if len(days) > 10 else None
        out[coin] = {'hours': n_av, 'mean_ann': mean_all, 'mean_ann_train': mean_tr, 'mean_ann_test': mean_te,
                     'share_days_abs_over_20pct': wide, 'daily_autocorr': ac1,
                     'same_sign_halves': (mean_tr is not None and mean_te is not None and mean_tr * mean_te > 0)}
    return out


def effective_trials(series, upto):
    """Variants on one grid are highly correlated, so N of them are worth fewer independent trials. The usual
    approximation N_eff = 1 + (N - 1)(1 - mean pairwise correlation) on the choose period; returned with the mean."""
    names = list(series)
    xs = [series[k][:upto] for k in names]
    cs = []
    for a in range(len(xs)):
        for b in range(a + 1, len(xs)):
            c = corr(xs[a], xs[b])
            if c is not None:
                cs.append(c)
    rho = sum(cs) / len(cs) if cs else 0.0
    return 1 + (len(names) - 1) * (1 - rho), rho


def family_tests(series, variants, test_day, n_days):
    """The choose-then-test protocol inside each family separately: does the slow (structural) family hold out of
    sample on its own, whatever the overall winner is."""
    out = {}
    fams = sorted({v.get('family', 'fast') for v in variants})
    for fam in fams:
        sub = {v['name']: series[v['name']] for v in variants if v.get('family', 'fast') == fam}
        if not sub:
            continue
        ct = B.choose_then_test(sub, frac=test_day / n_days, periods_per_year=365)
        out[fam] = {'chosen': ct['chosen'], 'n_variants': ct['n_variants'], 'in_sample': ct['in_sample'],
                    'out_of_sample': ct['out_of_sample'], 'oos_t': ct['oos_t'], 'oos_p': ct['oos_p'],
                    'oos_rank': ct['oos_rank']}
    return out


def variant_detail(kind, v, r, pairs, costs, snap, mapping, fees, maker_fees, t0, n, test_day):
    """Everything economic about one variant on the test period: trades, costs, basis, the proxy check, margin stress,
    month by month, and capacity at the live books with the savings rate charged on the capital it ties up."""
    n_days = n // 24
    test_hour = test_day * 24
    trades = {}
    for coin, pr in pairs.items():
        ce, cx = costs[coin]
        trades[coin] = simulate(pr, v['k'], v['X'], v['Y'], v['H'], v['step'], ce, cx)
    te_trades = {c: [t for t in trs if t['i'] >= test_hour] for c, trs in trades.items()}
    tr_trades = {c: [t for t in trs if t['i'] < test_hour] for c, trs in trades.items()}
    allte = [t for trs in te_trades.values() for t in trs]
    alltr = [t for trs in tr_trades.values() for t in trs]
    P, C = r['P'], r['C']
    dep_te = (sum(P[test_day:]) / sum(C[test_day:]) * 365) if sum(C[test_day:]) else None
    dep_tr = (sum(P[:test_day]) / sum(C[:test_day]) * 365) if sum(C[:test_day]) else None
    # Maker variant: same rule, maker fee and no half-spread (a resting order is filled at its own price; the cost
    # of that is fill uncertainty, which this does not model, so the maker line is an upper bound).
    va, vb = PAIR_TYPES[kind] if kind in PAIR_TYPES else (None, None)
    maker = None
    if va:
        mc = leg_cost(maker_fees[va], 0) + leg_cost(maker_fees[vb], 0)
        mt = [t for coin, pr in pairs.items() for t in simulate(pr, v['k'], v['X'], v['Y'], v['H'], v['step'], mc, mc)
              if t['i'] >= test_hour]
        maker = trade_stats(mt)
    # How good is the premium proxy the early months rely on: the test trades priced on real closes and on the proxy.
    pa, pb = [], []
    for coin, trs in te_trades.items():
        if trs:
            pr = pairs[coin]
            a, b = proxy_check(pr, Pair(coin, pr.A, pr.B, pr.n, pr.long_only, basis='premium',
                                        unit_ratio=pr.unit_ratio), trs)
            pa += a
            pb += b
    pcheck = {'trades': len(pa), 'price_basis_bp_mean': (1e4 * sum(pa) / len(pa)) if pa else None,
              'proxy_basis_bp_mean': (1e4 * sum(pb) / len(pb)) if pb else None, 'corr': corr(pa, pb),
              'mean_abs_diff_bp': (1e4 * sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)) if pa else None}
    monthly = []
    ms_ = month_starts(t0, n_days) + [n_days]
    for a_, b_ in zip(ms_, ms_[1:]):
        Pm, Cm = sum(P[a_:b_]), sum(C[a_:b_])
        monthly.append({'month': utc(t0 + a_ * DAY_MS)[:7], 'pnl_units': Pm, 'position_days': Cm,
                        'deployed_apr': (Pm / Cm * 365) if Cm else None,
                        'avg_positions': Cm / max(1, b_ - a_), 'test': a_ >= test_day})
    exc_rows = [excursions(pairs[c], trs) for c, trs in te_trades.items() if trs]
    nt = sum(x['trades'] for x in exc_rows)
    exc = {'trades': nt}
    for key in ('share_over_25%', 'share_over_40%'):
        exc[key] = (sum((x[key] or 0) * x['trades'] for x in exc_rows) / nt) if nt else None
    # Capacity at the live books, per coin; then the book: dollars a year, the capital it ties up (peak and average
    # concurrent notional), and what is left after paying the savings rate on that capital.
    test_years = (n - test_hour) / HOURS_PER_YEAR
    per_coin, sizes, sizes20 = [], {}, {}
    for coin, trs in te_trades.items():
        if not trs:
            continue
        legs = [(va, venue_key(va, coin, mapping)), (vb, venue_key(vb, coin, mapping))] if va else []
        cap = capacity(snap, legs) if legs else None
        gross = sum(t['funding'] + t['basis'] for t in trs)
        hours = sum(t['e'] - t['i'] for t in trs)
        row = {'coin': coin, 'trades': len(trs), 'hours': hours,
               'funding_bp': 1e4 * sum(t['funding'] for t in trs), 'basis_bp': 1e4 * sum(t['basis'] for t in trs),
               'net_bp_small': 1e4 * sum(t['net'] for t in trs)}
        if cap and cap['size_usd'] > 0:
            per_fill = sum(leg_cost(fees[x], sl) for x, sl in zip((va, vb), cap['slip_bp_per_fill']))
            net_q = gross - len(trs) * 2 * per_fill
            row.update({'cap_usd': cap['size_usd'], 'slip_bp': cap['slip_bp_per_fill'], 'net_bp_at_cap': 1e4 * net_q,
                        'usd_per_year_at_cap': cap['size_usd'] * net_q / test_years,
                        'avg_notional_usd': cap['size_usd'] * hours / (n - test_hour)})
            sizes[coin] = cap['size_usd']
        for lim in SIZE_LIMITS:
            cl = capacity(snap, legs, size_limit=lim) if legs else None
            if cl and cl['size_usd'] > 0:
                per_fill = sum(leg_cost(fees[x], sl) for x, sl in zip((va, vb), cl['slip_bp_per_fill']))
                net_q = gross - len(trs) * 2 * per_fill
                row['at_%dk' % (lim // 1000)] = {'size_usd': cl['size_usd'],
                                                 'usd_per_year': cl['size_usd'] * net_q / test_years,
                                                 'avg_notional_usd': cl['size_usd'] * hours / (n - test_hour)}
        cap20 = capacity(snap, legs, max_slip=20.0) if legs else None
        if cap20 and cap20['size_usd'] > 0:
            per_fill = sum(leg_cost(fees[x], sl) for x, sl in zip((va, vb), cap20['slip_bp_per_fill']))
            net_q = gross - len(trs) * 2 * per_fill
            row.update({'cap20_usd': cap20['size_usd'], 'usd_per_year_at_cap20': cap20['size_usd'] * net_q / test_years})
            sizes20[coin] = cap20['size_usd']
        per_coin.append(row)
    per_coin.sort(key=lambda x: -(x.get('usd_per_year_at_cap') or 0))
    usd_year = sum(x.get('usd_per_year_at_cap') or 0 for x in per_coin)
    usd_year20 = sum(x.get('usd_per_year_at_cap20') or 0 for x in per_coin)
    avg_notional = sum(x.get('avg_notional_usd') or 0 for x in per_coin)
    peak = peak_concurrent(te_trades, sizes, test_hour, n)
    peak20 = peak_concurrent(te_trades, sizes20, test_hour, n)
    capd = [x for x in per_coin if x.get('usd_per_year_at_cap') is not None]
    largest = max(capd, key=lambda x: x['cap_usd']) if capd else None
    # Where the per-unit edge lives: test trades grouped by the coin's capacity at the live books.
    buckets = []
    for lo, hi in ((0, 5e3), (5e3, 25e3), (25e3, 1e5), (1e5, 1e12)):
        rows_b = [x for x in per_coin if x.get('cap_usd') is not None and lo <= x['cap_usd'] < hi]
        trs_b = [t for x in rows_b for t in te_trades[x['coin']]]
        hb = sum(t['e'] - t['i'] for t in trs_b)
        buckets.append({'cap_from_usd': lo, 'cap_to_usd': hi if hi < 1e12 else None, 'coins': len(rows_b),
                        'trades': len(trs_b), 'mean_net_bp': (1e4 * sum(t['net'] for t in trs_b) / len(trs_b)) if trs_b else None,
                        'net_per_position_year': (sum(t['net'] for t in trs_b) / hb * HOURS_PER_YEAR) if hb else None})
    limits = {}
    for lim in SIZE_LIMITS:
        key = 'at_%dk' % (lim // 1000)
        u = sum(x[key]['usd_per_year'] for x in per_coin if key in x)
        an = sum(x[key]['avg_notional_usd'] for x in per_coin if key in x)
        limits[key] = {'size_limit_usd': lim, 'usd_per_year': u, 'avg_concurrent_usd': an,
                       'return_on_avg_capital': (u / an) if an else None,
                       'usd_per_year_over_ssr_on_avg_capital': u - SSR * an,
                       'coins': sum(1 for x in per_coin if key in x)}
    capacity_block = {
        'size_limits': limits, 'edge_by_capacity_bucket': buckets,
        'usd_per_year_test_at_cap': usd_year, 'peak_concurrent_usd': peak, 'avg_concurrent_usd': avg_notional,
        'return_on_peak_capital': (usd_year / peak) if peak else None,
        'return_on_avg_capital': (usd_year / avg_notional) if avg_notional else None,
        'usd_per_year_over_ssr_on_avg_capital': usd_year - SSR * avg_notional,
        'usd_per_year_over_ssr_on_peak_capital': usd_year - SSR * peak,
        'largest_capacity_coin': largest['coin'] if largest else None,
        'largest_capacity_coin_share_of_avg_capital': (largest['avg_notional_usd'] / avg_notional)
        if largest and avg_notional else None,
        'usd_per_year_excluding_largest_capacity_coin': (usd_year - largest['usd_per_year_at_cap']) if largest else None,
        'usd_per_year_test_at_cap20': usd_year20, 'peak_concurrent_usd_cap20': peak20,
        'coins_traded_test': len(per_coin), 'coins_with_book': len(capd),
        'median_cap_usd': statistics.median([x['cap_usd'] for x in capd]) if capd else None,
        'top': per_coin[:15], 'bottom': per_coin[-5:] if len(per_coin) > 15 else []}
    return {
        'variant': v['name'], 'variant_spec': v,
        'deployed_apr_train': dep_tr, 'deployed_apr_test': dep_te,
        'deployed_apr_test_over_ssr': (dep_te - SSR) if dep_te is not None else None,
        'trades_train': trade_stats(alltr), 'trades_test': trade_stats(allte), 'maker_test': maker,
        'trades_test_by_direction': {'short_%s_long_%s' % (va, vb): trade_stats([t for t in allte if t['d'] > 0]),
                                     'short_%s_long_%s' % (vb, va): trade_stats([t for t in allte if t['d'] < 0])}
        if va else None,
        'price_check_test': pcheck, 'monthly': monthly, 'margin_stress_test': exc,
        'capacity': capacity_block, 'per_coin_test': per_coin,
    }


def evaluate_kind(kind, pairs, costs, variants, t0, n, snap, mapping, fees, maker_fees, test_day, step=STEP):
    n_days = n // 24
    cnt = live_counts(pairs, n_days)
    res = run_grid(pairs, costs, variants, n_days, step)
    series = {k: [r['P'][d] / cnt[d] if cnt[d] else 0.0 for d in range(n_days)] for k, r in res.items()}
    ctt = B.choose_then_test(series, frac=test_day / n_days, periods_per_year=365)
    chosen = ctt['chosen']
    v = res[chosen]['variant']
    wf, picks = walk_forward(series, t0, n_days)
    n_eff, rho = effective_trials(series, test_day)
    fam = family_tests(series, variants, test_day, n_days)
    detail = variant_detail(kind, v, res[chosen], pairs, costs, snap, mapping, fees, maker_fees, t0, n, test_day)
    fam_details = {f: variant_detail(kind, res[x['chosen']]['variant'], res[x['chosen']], pairs, costs, snap, mapping,
                                     fees, maker_fees, t0, n, test_day)
                   for f, x in fam.items() if x['chosen'] != chosen}
    # Serial dependence: positions last weeks, so the default HAC lag is short; the same statistics at 30 days.
    nw30 = B.newey_west_t(series[chosen][test_day:], lags=30)
    bb30 = B.block_bootstrap(series[chosen][test_day:], block=30)

    # The plateau, not the peak: the ten best variants on the choose period and how each did on the test period. A
    # rule whose neighbours also hold is a mechanism; one that stands alone is a draw from the grid.
    def dep(r, a_, b_):
        cc = sum(r['C'][a_:b_])
        return (sum(r['P'][a_:b_]) / cc * 365) if cc else None
    ranked_is = sorted(res, key=lambda k_: -(B.perf(series[k_][:test_day], 365).get('sharpe') or -1e9))
    top = [{'variant': k_, 'choose_sharpe': B.perf(series[k_][:test_day], 365).get('sharpe'),
            'test_sharpe': B.perf(series[k_][test_day:], 365).get('sharpe'),
            'test_deployed_apr': dep(res[k_], test_day, n_days)} for k_ in ranked_is[:10]]
    deps = [x['test_deployed_apr'] for x in top if x['test_deployed_apr'] is not None]
    all_dep = [x for x in (dep(r, test_day, n_days) for r in res.values()) if x is not None]
    plateau = {'top10': top, 'top10_median_test_deployed_apr': statistics.median(deps) if deps else None,
               'top10_min_test_deployed_apr': min(deps) if deps else None,
               'share_of_all_variants_test_deployed_over_ssr': (sum(1 for x in all_dep if x > SSR) / len(all_dep))
               if all_dep else None}
    out = {
        'kind': kind, 'coins': len(pairs), 'variants': len(variants), 'chosen': chosen, 'chosen_variant': v,
        'plateau': plateau,
        'choose_then_test': {k: ctt[k] for k in ('in_sample', 'out_of_sample', 'oos_rank', 'oos_t', 'oos_p',
                                                 'deflated_sharpe_in_sample', 'bh_survivors_full_sample',
                                                 'cutoff_index')},
        'oos_bootstrap_mean_daily': B.block_bootstrap(series[chosen][test_day:]),
        'oos_nw_30d': {'t': nw30[0], 'p': nw30[1]}, 'oos_bootstrap_block30': bb30,
        'effective_trials': {'n_eff': n_eff, 'mean_pairwise_corr': rho,
                             'deflated_sharpe_in_sample_n_eff': B.deflated_sharpe(series[chosen][:test_day], n_eff)},
        'families': fam, 'family_details': fam_details,
        'walk_forward': {'perf': B.perf(wf, 365), 'nw': B.newey_west_t(wf), 'bootstrap': B.block_bootstrap(wf),
                         'picks': picks},
        'oos_reserved_capital_perf': ctt['out_of_sample'],
        'live_coins_median': statistics.median([c for c in cnt if c]) if any(cnt) else 0,
        'all_variants': {k: {'trades': r['trades'],
                             'train': {kk: B.perf(series[k][:test_day], 365).get(kk) for kk in ('ann_return', 'sharpe')},
                             'test': {kk: B.perf(series[k][test_day:], 365).get(kk) for kk in ('ann_return', 'sharpe')},
                             'deployed_apr_test': dep(r, test_day, n_days)}
                         for k, r in res.items()},
    }
    out.update(detail)
    return out, series


def transfer_test(src_kind, src_eval, mapping, V, n, t0, snap):
    """The rules chosen on Hyperliquid vs Binance (overall and in each family), run unchanged on Hyperliquid vs OKX
    over OKX's last quarter, and on Hyperliquid vs Binance over the same dates: a third venue the selection never saw.
    A rule whose signal is longer than the window is reported as untestable rather than run on a few days."""
    okx_pairs, okx_costs = build_pairs('hl_okx', mapping, V, n, snap, FEES_TAKER)
    src_pairs, src_costs = build_pairs(src_kind, mapping, V, n, snap, FEES_TAKER)
    firsts = [next((j for j in range(n) if pr.av[j]), None) for pr in okx_pairs.values()]
    firsts = [f for f in firsts if f is not None]
    if not firsts:
        return None
    first = int(statistics.median(firsts))
    rules = {'overall': src_eval['chosen_variant']}
    for fam, d in (src_eval.get('family_details') or {}).items():
        rules[fam] = d['variant_spec']
    out = {'okx_first_utc': utc(t0 + first * HOUR_MS), 'end_utc': utc(t0 + (n - 1) * HOUR_MS), 'rules': {}}
    for lab_rule, v in rules.items():
        start = first + v['k']
        start = (start + v['step'] - 1) // v['step'] * v['step']
        rec = {'variant': v['name'], 'start_utc': utc(t0 + start * HOUR_MS)}
        if n - start < 30 * 24:
            rec['untestable'] = 'signal of %d days leaves %d days of OKX history' % (v['k'] // 24, (n - start) // 24)
            out['rules'][lab_rule] = rec
            continue
        for lab, pairs, costs in (('hl_okx', okx_pairs, okx_costs), (src_kind + '_same_dates', src_pairs, src_costs)):
            trs = []
            for coin, pr in pairs.items():
                ce, cx = costs[coin]
                trs += simulate(pr, v['k'], v['X'], v['Y'], v['H'], v['step'], ce, cx, start=start)
            rec[lab] = {'coins': len(pairs), 'trades': trade_stats(trs), 'net_bp_total': 1e4 * sum(t['net'] for t in trs)}
        out['rules'][lab_rule] = rec
    return out


def build_spot_pairs(mapping, V, n, t0, raw, snap):
    """Short the HL perp, hold the HL spot token. The spot leg pays no funding and its premium is taken as 0 (the
    oracle is built from spot prices, Hyperliquid's own spot book among them); trade closes check that."""
    extra = raw / 'hl_extra'
    smap_p = extra / 'spot_map.json'
    if not smap_p.exists():
        return {}, {}
    smap = json.loads(smap_p.read_text())
    pairs, costs, checks = {}, {}, {}
    for coin, mm in smap.items():
        A = V.get(('hl', coin))
        if A is None:
            continue
        # The candidate whose hourly closes sit within 3% of the perp's (in the perp's units: kBONK is 1,000 BONK) is
        # the same asset; the others are namesakes.
        unit = (mapping.get(coin) or {}).get('hl_mult', 1)
        best = None
        for cand in mm.get('candidates', [mm]):
            h1c = extra / 'spot_candles' / (safe(cand['pair']) + '.json.gz')
            if not h1c.exists():
                continue
            rs = []
            for c in read_gz(h1c):
                j = (int(c['t']) + HOUR_MS - t0) // HOUR_MS
                if 0 <= j < n and A.px[j]:
                    rs.append(float(c['c']) / (A.px[j] / unit))
            r = statistics.median(rs) if len(rs) >= 24 else None
            checks['%s:%s' % (coin, cand['pair'])] = {'token': cand['token'], 'ratio': r, 'hours': len(rs)}
            if r is not None and 0.97 <= r <= 1.03 and (best is None or abs(r - 1) < abs(best[1] - 1)):
                best = (cand, r)
        if best is None:
            continue
        m = best[0]
        sp = Venue(n)
        d1 = extra / 'spot_candles_1d' / (safe(m['pair']) + '.json.gz')
        h1 = extra / 'spot_candles' / (safe(m['pair']) + '.json.gz')
        first = None
        if d1.exists():
            rows = read_gz(d1)
            if rows:
                first = int(rows[0]['t'])
        closes = {}
        if h1.exists():
            for c in read_gz(h1):
                closes[int(c['t']) + HOUR_MS] = float(c['c']) * unit   # in the perp's units
        if first is None and closes:
            first = min(closes) - HOUR_MS
        if first is None:
            continue
        j0 = max(0, (first - t0) // HOUR_MS + 24)
        for j in range(j0, n):
            sp.live[j] = True
            sp.prem[j] = 0.0
            sp.px[j] = closes.get(t0 + j * HOUR_MS)
        sp.settlements = 1
        pr = Pair(coin, A, sp, n, long_only=True, a_name='hl', b_name='hl_spot')
        if pr.AV[-1] < 24 * 7:
            continue
        pairs[coin] = pr
        hs_spot = ((snap.get('hl_spot') or {}).get('books') or {}).get(m['pair'], {}).get('half_spread_bp',
                                                                                         MISSING_HALF_SPREAD_BP)
        c = leg_cost(FEES_TAKER['hl'], half_spread(snap, 'hl', coin)) + leg_cost(FEES_TAKER['hl_spot'], hs_spot)
        costs[coin] = (c, c)
        pr.spot_pair, pr.spot_token = m['pair'], m['token']
    return pairs, costs, checks


def evaluate_spot(pairs, costs, t0, n, snap, test_day, staking_apr=None):
    variants = spot_variants()
    n_days = n // 24
    cnt = live_counts(pairs, n_days)
    res = run_grid(pairs, costs, variants, n_days)
    series = {k: [r['P'][d] / cnt[d] if cnt[d] else 0.0 for d in range(n_days)] for k, r in res.items()}
    ctt = B.choose_then_test(series, frac=test_day / n_days, periods_per_year=365)
    chosen = ctt['chosen']
    v = res[chosen]['variant']
    test_hour = test_day * 24
    test_years = (n - test_hour) / HOURS_PER_YEAR
    per_coin = []
    for coin, pr in pairs.items():
        ce, cx = costs[coin]
        out_coin = {'coin': coin, 'spot_pair': getattr(pr, 'spot_pair', None), 'spot_token': getattr(pr, 'spot_token', None)}
        # Capacity: the spot book is usually the thin leg; the perp is margined on the same venue.
        sp_book = ((snap.get('hl_spot') or {}).get('books') or {}).get(getattr(pr, 'spot_pair', None))
        pp_book = ((snap.get('hl') or {}).get('books') or {}).get(coin)
        q, per_fill = None, None
        if sp_book and pp_book:
            q = min(max_size(sp_book['bids'], sp_book['mid'], CAP_SLIP_BP),
                    max_size(sp_book['asks'], sp_book['mid'], CAP_SLIP_BP),
                    max(max_size(pp_book['bids'], pp_book['mid'], CAP_SLIP_BP),
                        max_size(pp_book.get('bids_coarse') or [], pp_book['mid'], CAP_SLIP_BP)),
                    max(max_size(pp_book['asks'], pp_book['mid'], CAP_SLIP_BP),
                        max_size(pp_book.get('asks_coarse') or [], pp_book['mid'], CAP_SLIP_BP)))
            if pp_book.get('oi_usd'):
                q = min(q, CAP_OI_SHARE * pp_book['oi_usd'])
            out_coin['cap_usd'] = q
            if q and q > 0:
                ss = [(slippage_bp(sp_book[sd], sp_book['mid'], q) or CAP_SLIP_BP) for sd in ('bids', 'asks')]
                ps = [min([x for x in (slippage_bp(pp_book[sd], pp_book['mid'], q),
                                       slippage_bp(pp_book.get(sd + '_coarse') or [], pp_book['mid'], q))
                           if x is not None] or [CAP_SLIP_BP]) for sd in ('bids', 'asks')]
                per_fill = leg_cost(FEES_TAKER['hl_spot'], sum(ss) / 2) + leg_cost(FEES_TAKER['hl'], sum(ps) / 2)
        for name in (chosen, 'always_on'):
            vv = res[name]['variant']
            all_trs = simulate(pr, vv['k'], vv['X'], vv['Y'], vv['H'], vv['step'], ce, cx)
            dp, dc = daily_pnl(pr, all_trs, n // 24)
            test_pnl, test_cap = sum(dp[test_day:]), sum(dc[test_day:])
            trs = [t for t in all_trs if t['i'] >= test_hour]
            st = trade_stats(trs)
            a, b = proxy_check(pr, Pair(coin, pr.A, pr.B, pr.n, pr.long_only, basis='premium',
                                        unit_ratio=pr.unit_ratio), trs)
            row = {'stats': st, 'net_bp': 1e4 * sum(t['net'] for t in trs),
                   'test_pnl_bp': 1e4 * test_pnl, 'test_position_days': test_cap,
                   'test_return_on_capital': (test_pnl / test_cap * 365 / 1.5) if test_cap else None,
                   'proxy_check': {'trades': len(a), 'price_basis_bp': 1e4 * sum(a), 'proxy_basis_bp': 1e4 * sum(b)}}
            if per_fill is not None and test_cap:
                # At capacity: the test-period P&L with every fill that landed in it (entries and exits, each charged
                # `ce` by daily_pnl at small size) re-priced at the size, on that size, per year.
                fills = (sum(1 for t in all_trs if t['i'] >= test_hour)
                         + sum(1 for t in all_trs if t['e'] >= test_hour))
                row['test_usd_per_year_at_cap'] = q * (test_pnl - fills * (per_fill - ce)) / test_years
            if per_fill is not None and trs:
                gross = sum(t['funding'] + t['basis'] for t in trs)
                net_q = gross - len(trs) * 2 * per_fill
                row['net_bp_at_cap'] = 1e4 * net_q
                # per unit of capital (spot paid in full + perp at 2x = 1.5 of notional)
                row['usd_per_year_at_cap'] = q * net_q / test_years
                row['return_on_capital_at_cap'] = net_q / test_years / 1.5
            out_coin[name] = row
        per_coin.append(out_coin)
    # Capital: spot fully paid plus the perp margined at 2x, so 1.5 of capital per unit notional.
    dep = {}
    for name in (chosen, 'always_on'):
        P, C = res[name]['P'], res[name]['C']
        dep[name] = (sum(P[test_day:]) / sum(C[test_day:]) * 365 / 1.5) if sum(C[test_day:]) else None
    return {'coins': sorted(pairs), 'variants': len(variants), 'chosen': chosen, 'chosen_variant': v,
            'choose_then_test': {k: ctt[k] for k in ('in_sample', 'out_of_sample', 'oos_rank', 'oos_t', 'oos_p',
                                                     'deflated_sharpe_in_sample', 'bh_survivors_full_sample')},
            'return_on_capital_test': dep, 'capital_per_notional': 1.5, 'staking_apr_hype': staking_apr,
            'per_coin': per_coin,
            'all_variants': {k: {'test_ann': B.perf(series[k][test_day:], 365).get('ann_return'),
                                 'train_ann': B.perf(series[k][:test_day], 365).get('ann_return'),
                                 'trades': r['trades']} for k, r in res.items()}}, series


def factor(V, mapping, t0, n, test_day, raw):
    """Cross-sectional carry on Hyperliquid core: each day at 00:00 UTC rank coins by trailing HL funding, short the
    top fraction, long the bottom, equal weight, gross 1. Prices are Binance (else Bybit) hourly closes plus the change
    in the HL-minus-CEX premium, which is the HL perp's own return to within the two indices' difference."""
    n_days = n // 24
    coins = []
    for coin in mapping:
        hv = V.get(('hl', coin))
        cv = V.get(('binance', coin)) or V.get(('bybit', coin))
        if hv is None or cv is None:
            continue
        coins.append((coin, hv, cv))
    # daily close and quote volume per coin
    px, vol = {}, {}
    for coin, hv, cv in coins:
        m = mapping[coin]
        venue = 'binance' if V.get(('binance', coin)) is cv else 'bybit'
        kp = raw / venue / 'klines' / (safe(m[venue]) + '.json.gz')
        qv = {}
        if kp.exists():
            for k in read_gz(kp):
                d = (int(k[0]) - t0) // DAY_MS
                if 0 <= d < n_days:
                    qv[d] = qv.get(d, 0.0) + float(k[5])
        vol[coin] = qv
        closes = []
        for d in range(n_days + 1):
            j = min(d * 24, n - 1)
            c = nearest_px(cv, j, tol=2)
            ph, pc = hv.prem[j], cv.prem[j]
            if c is None or ph is None or pc is None:
                closes.append(None)
            else:
                closes.append(c * (1 + ph - pc))
        px[coin] = closes
    btc = px.get('BTC')
    variants = []
    for k in (24, 72, 168):
        for q in (0.1, 0.2):
            for neutral in ('dollar', 'beta'):
                variants.append({'name': 'k%d_q%d_%s' % (k, round(q * 100), neutral), 'k': k, 'q': q, 'neutral': neutral})
    series, turnover = {}, {}
    for v in variants:
        rets, prev_w, turn = [0.0] * n_days, {}, []
        for d in range(8, n_days):
            j = d * 24
            elig = []
            for coin, hv, cv in coins:
                if px[coin][d] is None or px[coin][d + 1] is None if d + 1 <= n_days else True:
                    continue
                if not all(hv.live[jj] for jj in range(max(0, j - v['k']), j)):
                    continue
                v7 = sum(vol[coin].get(dd, 0.0) for dd in range(d - 7, d)) / 7
                if v7 < 5e6:
                    continue
                sig = sum(hv.pay[jj] for jj in range(j - v['k'], j))
                elig.append((sig, coin))
            if len(elig) < 20:
                continue
            elig.sort()
            m = max(3, int(len(elig) * v['q']))
            longs, shorts = [c for _, c in elig[:m]], [c for _, c in elig[-m:]]
            w = {c: 0.5 / m for c in longs}
            w.update({c: -0.5 / m for c in shorts})
            if v['neutral'] == 'beta' and btc is not None:
                betas = {}
                for c in longs + shorts:
                    xs, ys = [], []
                    for dd in range(max(1, d - 60), d):
                        a0, a1, b0, b1 = px[c][dd - 1], px[c][dd], btc[dd - 1], btc[dd]
                        if None not in (a0, a1, b0, b1):
                            ys.append(a1 / a0 - 1)
                            xs.append(b1 / b0 - 1)
                    if len(xs) > 20:
                        mx = sum(xs) / len(xs)
                        vx = sum((x - mx) ** 2 for x in xs)
                        betas[c] = (sum((x - mx) * (y - sum(ys) / len(ys)) for x, y in zip(xs, ys)) / vx) if vx else 1.0
                    else:
                        betas[c] = 1.0
                bl = sum(betas[c] for c in longs) / m
                bs = sum(betas[c] for c in shorts) / m
                if bl > 0 and bs > 0:
                    # scale the legs so that 0.5*L*bl = 0.5*S*bs with gross 1: L = 2 bs/(bl+bs), S = 2 bl/(bl+bs)
                    L, S_ = 2 * bs / (bl + bs), 2 * bl / (bl + bs)
                    w = {c: 0.5 * L / m for c in longs}
                    w.update({c: -0.5 * S_ / m for c in shorts})
            r = 0.0
            for c, wc in w.items():
                hv = V[('hl', c)]
                f = sum(hv.pay[jj] for jj in range(j + 1, min(n, j + 25)))
                r += wc * (px[c][d + 1] / px[c][d] - 1.0) - wc * f
            tv = sum(abs(w.get(c, 0.0) - prev_w.get(c, 0.0)) for c in set(w) | set(prev_w))
            r -= tv * FEES_TAKER['hl'] / 1e4
            turn.append(tv)
            rets[d] = r
            prev_w = w
        series[v['name']] = rets
        turnover[v['name']] = sum(turn) / len(turn) if turn else None
    ctt = B.choose_then_test(series, frac=test_day / n_days, periods_per_year=365)
    btc_r = [0.0] * n_days
    if btc:
        for d in range(1, n_days):
            if btc[d] and btc[d + 1] if d + 1 <= n_days else False:
                btc_r[d] = btc[d + 1] / btc[d] - 1
    ch = ctt['chosen']
    return {'variants': len(variants), 'chosen': ch,
            'choose_then_test': {k: ctt[k] for k in ('in_sample', 'out_of_sample', 'oos_rank', 'oos_t', 'oos_p',
                                                     'deflated_sharpe_in_sample', 'bh_survivors_full_sample')},
            'corr_with_btc_test': corr(series[ch][test_day:], btc_r[test_day:]),
            'mean_daily_turnover': turnover[ch],
            'all_variants': {k: {'train': B.perf(s[:test_day], 365).get('sharpe'),
                                 'test': B.perf(s[test_day:], 365).get('sharpe'),
                                 'test_ann': B.perf(s[test_day:], 365).get('ann_return')} for k, s in series.items()}}


def staking_apr(raw):
    p = raw / 'hl_extra' / 'validator_summaries.json'
    if not p.exists():
        return None
    try:
        vs = json.loads(p.read_text())
        aprs, stakes = [], []
        for v in vs:
            st = dict(v.get('stats') or [])
            day = st.get('day') or st.get('week') or {}
            apr = fnum(day.get('predictedApr'))
            if apr is not None:
                aprs.append(apr)
                stakes.append(fnum(v.get('stake'), 0))
        if not aprs:
            return None
        tot = sum(stakes)
        return sum(a * s for a, s in zip(aprs, stakes)) / tot if tot else statistics.median(aprs)
    except Exception:  # noqa: BLE001
        return None


def venue_facts(V, mapping, t0, n, since='2026-07-01'):
    """Plain facts about each venue's funding, quoted in the note: how often Hyperliquid sits at its interest floor,
    whether its 4%-an-hour cap ever bound, the modal CEX rates, how many CEX symbols changed settlement interval, and
    BTC's mean funding on every venue since `since`."""
    from collections import Counter
    out = {}
    hl_floor, cap_hits, hl_hours = [], 0, 0
    for (venue, coin), v in V.items():
        if venue != 'hl':
            continue
        pays = [v.pay[j] for j in range(n) if v.live[j]]
        if len(pays) < 24 * 30:
            continue
        hl_floor.append(sum(1 for x in pays if abs(x - 0.0000125) < 1e-12) / len(pays))
        cap_hits += sum(1 for x in pays if abs(x) >= 0.04 - 1e-12)
        hl_hours += len(pays)
    out['hl_median_coin_share_of_hours_at_1.25bp_floor'] = statistics.median(hl_floor) if hl_floor else None
    out['hl_hours_at_4pct_cap'] = cap_hits
    out['hl_hours_checked'] = hl_hours
    for venue in ('binance', 'bybit', 'okx'):
        modal, changed, nsym = Counter(), 0, 0
        for (vv, coin), v in V.items():
            if vv != venue or not v.interval_hours:
                continue
            nsym += 1
            main = max(v.interval_hours, key=v.interval_hours.get)
            modal[main] += 1
            if sum(1 for c in v.interval_hours.values() if c > 20) > 1:
                changed += 1
        out[venue + '_symbols_by_modal_interval_hours'] = dict(modal)
        out[venue + '_symbols_whose_interval_changed'] = changed
    s0 = (ms_of(since) - t0) // HOUR_MS
    btc = {}
    for venue in ('hl', 'binance', 'bybit', 'okx'):
        v = V.get((venue, 'BTC'))
        if v is None:
            continue
        hrs = [j for j in range(max(0, s0), n) if v.live[j]]
        if hrs:
            btc[venue] = sum(v.pay[j] for j in hrs) / len(hrs) * HOURS_PER_YEAR
    out['btc_mean_funding_annualised_since_' + since] = btc
    return out


def cmd_analyze(args):
    out = Path(args.out)
    raw = out / 'raw'
    t_start = time.time()
    t0, n, mapping, V = load_study(out, args.hl, args.train_start)
    snap = json.loads((out / 'snapshot.json').read_text()) if (out / 'snapshot.json').exists() else {}
    mreport, dropped = check_mapping(mapping, V)
    test_day = (ms_of(args.test_start) - t0) // DAY_MS
    test_hour = test_day * 24
    n_days = n // 24
    variants = variants_grid()
    kinds = args.kinds.split(',')
    result = {'generated': utc(), 'grid': {'t0': utc(t0), 'hours': n, 'days': n_days, 'test_start': args.test_start,
                                           'step_hours': STEP, 'variants_per_pair_type': len(variants)},
              'fees_taker_bp': FEES_TAKER, 'fees_maker_bp': FEES_MAKER, 'ssr': SSR,
              'capital_assumption': 'each leg margined at 2x on its own venue: capital = notional of one leg',
              'mapping': {'checked': len(mreport), 'dropped': dropped,
                          'hl_delisted_included': [c for c in mapping if ('hl', c) in V and not mapping[c].get('_live', True)]},
              'kinds': {}, 'profiles': {}}
    extra = raw / 'hl_extra' / 'delisted.json'
    if extra.exists():
        dl = set(json.loads(extra.read_text())['coins'])
        result['mapping']['hl_delisted_included'] = sorted(c for c in dl if ('hl', c) in V)
    result['mapping']['cex_delisted_included'] = sorted(
        '%s:%s' % (v, mapping[c][v]) for (v, c), ven in V.items() if v != 'hl' and ven.live and not ven.live[-1])
    trials = 0
    all_series = {}
    for kind in kinds:
        if kind not in PAIR_TYPES:
            continue
        pairs, costs = build_pairs(kind, mapping, V, n, snap, FEES_TAKER)
        print(json.dumps({'kind': kind, 'pairs': len(pairs), 'elapsed_s': round(time.time() - t_start)}), flush=True)
        ev, series = evaluate_kind(kind, pairs, costs, variants, t0, n, snap, mapping, FEES_TAKER, FEES_MAKER,
                                   test_day)
        trials += len(variants)
        result['kinds'][kind] = ev
        prof = spread_profile(pairs, test_hour)
        result['profiles'][kind] = prof
        tt_ = [(r['mean_ann_train'], r['mean_ann_test']) for r in prof.values()
               if r['mean_ann_train'] is not None and r['mean_ann_test'] is not None]
        means = [r['mean_ann'] for r in prof.values()]
        result['structure'] = result.get('structure', {})
        result['structure'][kind] = {
            'coins': len(prof), 'median_mean_spread': statistics.median(means) if means else None,
            'share_positive': (sum(1 for x in means if x > 0) / len(means)) if means else None,
            'train_test_corr_of_coin_means': corr([a for a, _ in tt_], [b for _, b in tt_]),
            'share_same_sign_halves': (sum(1 for a, b in tt_ if a * b > 0) / len(tt_)) if tt_ else None,
            'median_abs_mean_spread': statistics.median([abs(x) for x in means]) if means else None}
        all_series.update({kind + ':' + k: s for k, s in series.items()})
    if 'okx' in kinds and 'hl_binance' in result['kinds']:
        tt = transfer_test('hl_binance', result['kinds']['hl_binance'], mapping, V, n, t0, snap)
        if tt:
            result['kinds']['hl_okx_transfer'] = tt
    if 'spot' in kinds:
        sp_pairs, sp_costs, sp_checks = build_spot_pairs(mapping, V, n, t0, raw, snap)
        if sp_pairs:
            ev, series = evaluate_spot(sp_pairs, sp_costs, t0, n, snap, test_day, staking_apr(raw))
            ev['spot_price_checks'] = sp_checks
            ev['spot_legs'] = {c: {'pair': pr.spot_pair, 'token': pr.spot_token} for c, pr in sp_pairs.items()}
            trials += ev['variants']
            result['kinds']['hl_spot_perp'] = ev
            all_series.update({'spot:' + k: s for k, s in series.items()})
    if 'factor' in kinds:
        ev = factor(V, mapping, t0, n, test_day, raw)
        trials += ev['variants']
        result['kinds']['hl_carry_factor'] = ev
    # Deflated Sharpe of each chosen variant against every variant tried in the whole study.
    result['trials_total'] = trials
    for kind, ev in result['kinds'].items():
        key = {'hl_spot_perp': 'spot:'}.get(kind, kind + ':') + ev.get('chosen', '')
        s = all_series.get(key)
        if s is not None:
            ev['deflated_sharpe_in_sample_all_trials'] = B.deflated_sharpe(s[:test_day], trials)
            ev['deflated_sharpe_test_all_trials'] = B.deflated_sharpe(s[test_day:], trials)
    result['mapping_report'] = mreport
    result['seconds'] = round(time.time() - t_start, 1)
    result['hl_price_sources'] = hl_price_sources(V, t0, n)
    result['venue_facts'] = venue_facts(V, mapping, t0, n)
    result['hl_store'] = str(args.hl)
    write_json(out / ('analysis%s.json' % (('_' + args.tag) if args.tag else '')), result)
    print(json.dumps({k: {'chosen': v.get('chosen'), 'deployed_apr_test': v.get('deployed_apr_test'),
                          'oos_ann': (v.get('choose_then_test') or {}).get('out_of_sample', {}).get('ann_return'),
                          'usd_year': (v.get('capacity') or {}).get('usd_per_year_test_at_cap')}
                      for k, v in result['kinds'].items()}, indent=1, default=str))
    return 0


# ---------------------------------------------------------------------------------------------- render

def pct(x, d=1):
    return '-' if x is None else ('%.' + str(d) + 'f%%') % (100 * x)


def num(x, d=2):
    return '-' if x is None else ('%.' + str(d) + 'f') % x


def usd(x):
    if x is None:
        return '-'
    a = abs(x)
    if a >= 1e6:
        return '$%.2fM' % (x / 1e6)
    if a >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def capacity_sentence(cap):
    return ('Capacity at the live books (%s bp VWAP on every leg in both directions, at most %d%% of the smaller open '
            'interest): **%s a year** on the test period across %d coins (%d with books; median size %s), on an average '
            'concurrent notional of %s (peak %s): %s on the average capital, %s a year after paying the %s savings rate '
            'on it (%s on the peak). The largest-capacity coin, %s, is %s of that average capital; without it the book '
            'makes %s a year. At 20 bp VWAP: %s a year on a peak of %s.'
            % (num(CAP_SLIP_BP, 0), round(100 * CAP_OI_SHARE), usd(cap.get('usd_per_year_test_at_cap')),
               cap.get('coins_traded_test', 0), cap.get('coins_with_book', 0), usd(cap.get('median_cap_usd')),
               usd(cap.get('avg_concurrent_usd')), usd(cap.get('peak_concurrent_usd')),
               pct(cap.get('return_on_avg_capital')), usd(cap.get('usd_per_year_over_ssr_on_avg_capital')),
               pct(SSR, 2), usd(cap.get('usd_per_year_over_ssr_on_peak_capital')), cap.get('largest_capacity_coin'),
               pct(cap.get('largest_capacity_coin_share_of_avg_capital'), 0),
               usd(cap.get('usd_per_year_excluding_largest_capacity_coin')),
               usd(cap.get('usd_per_year_test_at_cap20')), usd(cap.get('peak_concurrent_usd_cap20'))))


def size_limit_table(cap):
    lim = cap.get('size_limits') or {}
    if not lim:
        return []
    out = ['| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | '
           '$/yr after the savings rate |', '|---|---:|---:|---:|---:|---:|']
    for key, x in lim.items():
        out.append('| %s | %d | %s | %s | %s | %s |' % (usd(x['size_limit_usd']), x['coins'], usd(x['avg_concurrent_usd']),
                                                       usd(x['usd_per_year']), pct(x['return_on_avg_capital']),
                                                       usd(x['usd_per_year_over_ssr_on_avg_capital'])))
    out.append('')
    bk = cap.get('edge_by_capacity_bucket') or []
    if bk:
        out += ['| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |',
                '|---|---:|---:|---:|---:|']
        for b in bk:
            lab = '%s to %s' % (usd(b['cap_from_usd']), usd(b['cap_to_usd'])) if b['cap_to_usd'] else 'over %s' % usd(b['cap_from_usd'])
            out.append('| %s | %d | %d | %s | %s |' % (lab, b['coins'], b['trades'], num(b['mean_net_bp'], 1),
                                                      pct(b['net_per_position_year'])))
        out.append('')
    return out


def render_family_details(L, k):
    fd = k.get('family_details') or {}
    for fam, d in fd.items():
        t = d.get('trades_test') or {}
        ms = d.get('margin_stress_test') or {}
        L.append('**The %s family on its own** (`%s`, chosen inside the family on the choose period): deployed return '
                 'choose %s, test %s; %d test trades, %s bp net mean (%s median), %s hit, %s a position-year; maker upper '
                 'bound %s a position-year; %s of test trades saw a 40%% move against one leg.'
                 % (fam, d['variant'], pct(d.get('deployed_apr_train')), pct(d.get('deployed_apr_test')),
                    t.get('n', 0), num(t.get('mean_net_bp'), 1), num(t.get('median_net_bp'), 1),
                    pct(t.get('hit_rate'), 0), pct(t.get('net_per_position_year')),
                    pct((d.get('maker_test') or {}).get('net_per_position_year')), pct(ms.get('share_over_40%'), 0)))
        L.append('')
        cap = d.get('capacity') or {}
        if cap.get('coins_traded_test'):
            L.append(capacity_sentence(cap))
            L.append('')
            L.extend(size_limit_table(cap))
            L.append('| coin | trades | hours | funding bp | basis bp | net bp (small) | size | net bp at size | $/yr at size |')
            L.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
            for r in (cap.get('top') or [])[:10] + (cap.get('bottom') or []):
                L.append('| %s | %d | %d | %.1f | %.1f | %.1f | %s | %s | %s |'
                         % (r['coin'], r['trades'], r['hours'], r['funding_bp'], r['basis_bp'], r['net_bp_small'],
                            usd(r.get('cap_usd')), num(r.get('net_bp_at_cap'), 1), usd(r.get('usd_per_year_at_cap'))))
            L.append('')


def render_kind(L, name, k):
    ct = k['choose_then_test']
    ins, oos = ct['in_sample'], ct['out_of_sample']
    L.append('### %s — %d coins, %d variants' % (name, k['coins'], k['variants']))
    L.append('')
    L.append('Chosen on the choose period: `%s`. Reserved-capital series (each coin with a live pair holds one unit '
             'of capital, idle or not), daily:' % k['chosen'])
    L.append('')
    L.append('| | ann. return | Sharpe | max DD | hit rate | days |')
    L.append('|---|---:|---:|---:|---:|---:|')
    L.append('| choose period | %s | %s | %s | %s | %d |' % (pct(ins.get('ann_return'), 2), num(ins.get('sharpe')),
                                                         pct(ins.get('max_drawdown'), 2), pct(ins.get('hit_rate'), 0),
                                                         ins.get('n', 0)))
    L.append('| test period | %s | %s | %s | %s | %d |' % (pct(oos.get('ann_return'), 2), num(oos.get('sharpe')),
                                                       pct(oos.get('max_drawdown'), 2), pct(oos.get('hit_rate'), 0),
                                                       oos.get('n', 0)))
    wf = k['walk_forward']['perf']
    L.append('| monthly walk-forward | %s | %s | %s | %s | %d |' % (pct(wf.get('ann_return'), 2), num(wf.get('sharpe')),
                                                                pct(wf.get('max_drawdown'), 2),
                                                                pct(wf.get('hit_rate'), 0), wf.get('n', 0)))
    L.append('')
    et = k.get('effective_trials', {})
    bs = k.get('oos_bootstrap_mean_daily', {})
    L.append('Test-period Newey–West t %s (p %s); block-bootstrap 95%% interval of the daily mean %s to %s (share at or '
             'below zero %s); test rank of the chosen variant %d of %d; deflated Sharpe of the choice %s against %d '
             'trials in this pair type (%s against N_eff %.0f, mean pairwise correlation %.2f) and %s against all %s '
             'trials in the study; %d of %d variants survive Benjamini–Hochberg at 10%% on the full year.'
             % (num(ct.get('oos_t')), num(ct.get('oos_p'), 4), num(1e4 * (bs.get('lo') or 0), 3) + 'bp',
                num(1e4 * (bs.get('hi') or 0), 3) + 'bp', num(bs.get('p_le_0'), 3), ct.get('oos_rank', 0),
                k['variants'], num(ct.get('deflated_sharpe_in_sample'), 3), k['variants'],
                num(et.get('deflated_sharpe_in_sample_n_eff'), 3), et.get('n_eff') or 0,
                et.get('mean_pairwise_corr') or 0, num(k.get('deflated_sharpe_in_sample_all_trials'), 3),
                k.get('trials_total', '-'), len(ct.get('bh_survivors_full_sample') or []), k['variants']))
    L.append('')
    L.append('Per unit of deployed capital (capital = notional of one leg): choose period %s, test period %s, '
             'test minus the savings rate %s.' % (pct(k.get('deployed_apr_train')), pct(k.get('deployed_apr_test')),
                                                  pct(k.get('deployed_apr_test_over_ssr'))))
    L.append('')
    L.append('| trades | n | mean hours | funding bp | basis bp | cost bp | net bp (mean) | net bp (median) | hit | '
             'net / position-year |')
    L.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for lab, t in (('choose, taker', k['trades_train']), ('test, taker', k['trades_test']),
                   ('test, maker (upper bound)', k.get('maker_test') or {})):
        if not t or not t.get('n'):
            continue
        L.append('| %s | %d | %.0f | %.1f | %.1f | %.1f | %.1f | %.1f | %s | %s |'
                 % (lab, t['n'], t['mean_hours'], t['mean_funding_bp'], t['mean_basis_bp'], t['mean_cost_bp'],
                    t['mean_net_bp'], t['median_net_bp'], pct(t['hit_rate'], 0), pct(t.get('net_per_position_year'))))
    L.append('')
    pl = k.get('plateau') or {}
    if pl.get('top10'):
        L.append('The ten best variants on the choose period, on the test period (deployed return): median %s, worst %s; '
                 '%s of all %d variants beat the savings rate on the test period.'
                 % (pct(pl.get('top10_median_test_deployed_apr')), pct(pl.get('top10_min_test_deployed_apr')),
                    pct(pl.get('share_of_all_variants_test_deployed_over_ssr'), 0), k['variants']))
        L.append('')
        L.append('| variant | choose Sharpe | test Sharpe | test deployed return |')
        L.append('|---|---:|---:|---:|')
        for x in pl['top10']:
            L.append('| `%s` | %s | %s | %s |' % (x['variant'], num(x['choose_sharpe']), num(x['test_sharpe']),
                                                 pct(x['test_deployed_apr'])))
        L.append('')
    bd = k.get('trades_test_by_direction') or {}
    if bd:
        L.append('By direction, test trades: ' + '; '.join(
            '%s %d trades, %s bp net mean, %s a position-year' % (lab.replace('_', ' '), t.get('n', 0),
                                                                 num(t.get('mean_net_bp'), 1),
                                                                 pct(t.get('net_per_position_year')))
            for lab, t in bd.items()) + '.')
        L.append('')
    mo = k.get('monthly') or []
    if mo:
        L.append('| month | ' + ' | '.join(m['month'][2:] for m in mo) + ' |')
        L.append('|---|' + '---:|' * len(mo))
        L.append('| deployed return, annualised | ' + ' | '.join(pct(m['deployed_apr'], 0) for m in mo) + ' |')
        L.append('| average open positions | ' + ' | '.join('%.1f' % m['avg_positions'] for m in mo) + ' |')
        L.append('')
    ms = k.get('margin_stress_test') or {}
    nw30 = k.get('oos_nw_30d') or {}
    bb30 = k.get('oos_bootstrap_block30') or {}
    L.append('With a 30-day HAC lag the test-period t is %s (p %s); a 30-day block bootstrap puts the daily mean between '
             '%s and %s bp. Margin stress: %s of test trades saw a 25%% move against one leg while held, %s a 40%% move.'
             % (num(nw30.get('t')), num(nw30.get('p'), 4), num(1e4 * (bb30.get('lo') or 0), 3),
                num(1e4 * (bb30.get('hi') or 0), 3), pct(ms.get('share_over_25%'), 0), pct(ms.get('share_over_40%'), 0)))
    L.append('')
    pc = k.get('price_check_test') or {}
    if pc.get('trades'):
        L.append('Premium-proxy check on the %d test trades with real closes on both legs at entry and exit: basis %s bp '
                 'a trade on real prices against %s bp on the proxy (correlation %s, mean absolute gap %s bp).'
                 % (pc['trades'], num(pc.get('price_basis_bp_mean'), 1), num(pc.get('proxy_basis_bp_mean'), 1),
                    num(pc.get('corr')), num(pc.get('mean_abs_diff_bp'), 1)))
        L.append('')
    fam = k.get('families') or {}
    if fam:
        L.append('| family | chosen | choose ann. | choose Sharpe | test ann. | test Sharpe | test t |')
        L.append('|---|---|---:|---:|---:|---:|---:|')
        for fn, f in fam.items():
            L.append('| %s | `%s` | %s | %s | %s | %s | %s |' % (fn, f['chosen'], pct(f['in_sample'].get('ann_return'), 2),
                                                            num(f['in_sample'].get('sharpe')),
                                                            pct(f['out_of_sample'].get('ann_return'), 2),
                                                            num(f['out_of_sample'].get('sharpe')), num(f.get('oos_t'))))
        L.append('')
    cap = k.get('capacity') or {}
    if cap.get('coins_traded_test'):
        L.append(capacity_sentence(cap))
        L.append('')
        L.extend(size_limit_table(cap))
        L.append('| coin | trades | hours | funding bp | basis bp | net bp (small) | size | slip bp/fill | net bp at size | '
                 '$/yr at size |')
        L.append('|---|---:|---:|---:|---:|---:|---:|---|---:|---:|')
        for r in (cap.get('top') or []) + (cap.get('bottom') or []):
            L.append('| %s | %d | %d | %.1f | %.1f | %.1f | %s | %s | %s | %s |'
                     % (r['coin'], r['trades'], r['hours'], r['funding_bp'], r['basis_bp'], r['net_bp_small'],
                        usd(r.get('cap_usd')), '/'.join('%.1f' % x for x in r.get('slip_bp') or []) or '-',
                        num(r.get('net_bp_at_cap'), 1), usd(r.get('usd_per_year_at_cap'))))
        L.append('')
    render_family_details(L, k)


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    L = ['# Funding spreads: tables', '',
         'Generated from `analysis.json` (%s) by `scripts/funding_arb.py render`. Grid %s, %d hours; choose period '
         'to %s, test period from it; decisions every %d hours (slow family weekly); fees taker %s, maker %s (bp); '
         'savings rate %s.' % (a['generated'], a['grid']['t0'], a['grid']['hours'], a['grid']['test_start'],
                               a['grid']['step_hours'], a['fees_taker_bp'], a['fees_maker_bp'], pct(a['ssr'], 2)), '']
    m = a['mapping']
    L.append('Mapping: %d listings checked by price ratio (or premium sign where no overlapping closes), %d dropped (%s); '
             'Hyperliquid coins delisted inside the study and included: %d; CEX perpetuals delisted inside it and '
             'included: %d. HL price sources: %s of live HL hours have a real close (1-hour candles from about %s, '
             '4-hour candles before).' % (m['checked'], len(m['dropped']), ', '.join(m['dropped']) or 'none',
                                          len(m.get('hl_delisted_included') or []),
                                          len(m.get('cex_delisted_included') or []),
                                          pct((a.get('hl_price_sources') or {}).get('share')),
                                          ((a.get('hl_price_sources') or {}).get('first_hourly_close_utc_median') or '-')[:10]))
    L.append('')
    names = {'hl_binance': 'Hyperliquid vs Binance', 'hl_bybit': 'Hyperliquid vs Bybit',
             'binance_bybit': 'Binance vs Bybit (control)'}
    st = a.get('structure') or {}
    if st:
        L.append('### The structure under the spreads (A minus B funding, each coin over the year)')
        L.append('')
        L.append('| pair (A − B) | coins | median coin mean | share of coins A > B | median absolute | same sign both halves | '
                 'correlation of coin means, choose half vs test half |')
        L.append('|---|---:|---:|---:|---:|---:|---:|')
        for kind, x in st.items():
            L.append('| %s | %d | %s | %s | %s | %s | %s |' % (names.get(kind, kind), x['coins'], pct(x['median_mean_spread'], 2),
                                                          pct(x['share_positive'], 0), pct(x['median_abs_mean_spread'], 2),
                                                          pct(x['share_same_sign_halves'], 0),
                                                          num(x['train_test_corr_of_coin_means'])))
        L.append('')
    for kind in ('hl_binance', 'hl_bybit', 'binance_bybit'):
        if kind in a['kinds']:
            k = dict(a['kinds'][kind], trials_total=a.get('trials_total'))
            render_kind(L, names[kind], k)
    tt = a['kinds'].get('hl_okx_transfer')
    if tt:
        L.append('### The chosen rules on a third venue: Hyperliquid vs OKX (OKX funding history from %s)'
                 % tt['okx_first_utc'][:10])
        L.append('')
        L.append('Rules chosen on Hyperliquid vs Binance before %s, run unchanged from the first decision with a full '
                 'signal window:' % a['grid']['test_start'])
        L.append('')
        L.append('| rule | pair | from | coins | trades | mean hours | funding bp | basis bp | cost bp | net bp | hit | '
                 'net / position-year |')
        L.append('|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
        for lab_rule, rec in tt['rules'].items():
            if rec.get('untestable'):
                L.append('| %s `%s` | - | - | - | - | - | - | - | - | - | - | untestable: %s |'
                         % (lab_rule, rec['variant'], rec['untestable']))
                continue
            for lab in [x for x in rec if x.startswith('hl_')]:
                t = rec[lab]['trades']
                if not t.get('n'):
                    continue
                L.append('| %s `%s` | %s | %s | %d | %d | %.0f | %.1f | %.1f | %.1f | %.1f | %s | %s |'
                         % (lab_rule, rec['variant'], lab, rec['start_utc'][:10], rec[lab]['coins'], t['n'],
                            t['mean_hours'], t['mean_funding_bp'], t['mean_basis_bp'], t['mean_cost_bp'],
                            t['mean_net_bp'], pct(t['hit_rate'], 0), pct(t.get('net_per_position_year'))))
        L.append('')
    sp = a['kinds'].get('hl_spot_perp')
    if sp:
        ct = sp['choose_then_test']
        L.append('### Hyperliquid spot–perp carry — %d coins (%s), %d variants' % (len(sp['coins']), ', '.join(sp['coins']),
                                                                                sp['variants']))
        L.append('')
        L.append('Chosen `%s`: choose period %s a year (Sharpe %s), test period %s (Sharpe %s, t %s). Return on capital '
                 '(spot fully paid + perp at 2x = %.1f of notional), test period: chosen %s, always-on %s. HYPE staking '
                 'yield read from the validators: %s.'
                 % (sp['chosen'], pct(ct['in_sample'].get('ann_return'), 2), num(ct['in_sample'].get('sharpe')),
                    pct(ct['out_of_sample'].get('ann_return'), 2), num(ct['out_of_sample'].get('sharpe')),
                    num(ct.get('oos_t')), sp['capital_per_notional'],
                    pct((sp['return_on_capital_test'] or {}).get(sp['chosen'])),
                    pct((sp['return_on_capital_test'] or {}).get('always_on')), pct(sp.get('staking_apr_hype'), 2)))
        L.append('')
        L.append('Test-period P&L per coin is marked daily, so a position opened before the test period and still '
                 'held counts for its test-period part; return on capital charges 1.5 of notional.')
        L.append('')
        L.append('| perp | spot token | chosen: test P&L bp | return on capital | always-on: test P&L bp | return on capital | '
                 'size at 10bp | chosen $/yr at size | always-on $/yr at size |')
        L.append('|---|---|---:|---:|---:|---:|---:|---:|---:|')
        tot_c = tot_a = 0.0
        for r in sp['per_coin']:
            c, ao = r.get(sp['chosen'], {}), r.get('always_on', {})
            tot_c += c.get('test_usd_per_year_at_cap') or 0
            tot_a += ao.get('test_usd_per_year_at_cap') or 0
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |'
                     % (r['coin'], r.get('spot_token') or '-', num(c.get('test_pnl_bp'), 1),
                        pct(c.get('test_return_on_capital')), num(ao.get('test_pnl_bp'), 1),
                        pct(ao.get('test_return_on_capital')), usd(r.get('cap_usd')),
                        usd(c.get('test_usd_per_year_at_cap')), usd(ao.get('test_usd_per_year_at_cap'))))
        L.append('')
        L.append('Sum at size: chosen rule %s a year, always-on %s a year.' % (usd(tot_c), usd(tot_a)))
        L.append('')
    fa = a['kinds'].get('hl_carry_factor')
    if fa:
        ct = fa['choose_then_test']
        L.append('### Cross-sectional carry factor on Hyperliquid core (a factor, not an arbitrage) — %d variants'
                 % fa['variants'])
        L.append('')
        L.append('Chosen `%s`: choose period %s a year at %s volatility (Sharpe %s); test period %s at %s (Sharpe %s, '
                 't %s, p %s, test rank %d); deflated Sharpe of the choice %s; correlation with BTC in the test period '
                 '%s; mean daily turnover %s of gross.'
                 % (fa['chosen'], pct(ct['in_sample'].get('ann_return')), pct(ct['in_sample'].get('ann_vol')),
                    num(ct['in_sample'].get('sharpe')), pct(ct['out_of_sample'].get('ann_return')),
                    pct(ct['out_of_sample'].get('ann_vol')), num(ct['out_of_sample'].get('sharpe')),
                    num(ct.get('oos_t')), num(ct.get('oos_p'), 3), ct.get('oos_rank', 0),
                    num(ct.get('deflated_sharpe_in_sample'), 3), num(fa.get('corr_with_btc_test')),
                    pct(fa.get('mean_daily_turnover'))))
        L.append('')
        L.append('| variant | choose Sharpe | test Sharpe | test ann. |')
        L.append('|---|---:|---:|---:|')
        for n_, v in fa['all_variants'].items():
            L.append('| `%s` | %s | %s | %s |' % (n_, num(v['train']), num(v['test']), pct(v['test_ann'])))
        L.append('')
    prof = a.get('profiles', {}).get('hl_binance') or {}
    if prof:
        rows = [(c, r) for c, r in prof.items() if r.get('same_sign_halves') and abs(r['mean_ann']) >= 0.05]
        rows.sort(key=lambda cr: -abs(cr[1]['mean_ann']))
        L.append('### Structural spreads, Hyperliquid minus Binance: same sign in both halves, |mean| at least 5%')
        L.append('')
        L.append('| coin | mean (year) | choose half | test half | days beyond ±20% | daily autocorrelation |')
        L.append('|---|---:|---:|---:|---:|---:|')
        for c, r in rows[:30]:
            L.append('| %s | %s | %s | %s | %s | %s |' % (c, pct(r['mean_ann']), pct(r['mean_ann_train']),
                                                     pct(r['mean_ann_test']), pct(r['share_days_abs_over_20pct'], 0),
                                                     num(r['daily_autocorr'])))
        L.append('')
        L.append('%d of %d coins have the same sign in both halves; %d of those at |mean| >= 5%%.'
                 % (sum(1 for r in prof.values() if r.get('same_sign_halves')), len(prof), len(rows)))
        L.append('')
    alt = out / 'analysis_split0601.json'
    if alt.exists():
        b = json.loads(alt.read_text())
        L.append('### Robustness: both halves on real hourly prices (grid from %s, test from %s)'
                 % (b['grid']['t0'][:10], b['grid']['test_start']))
        L.append('')
        L.append('| pair | chosen | test deployed return | test reserved Sharpe | test t | top-10 median test deployed | '
                 'variants over the savings rate |')
        L.append('|---|---|---:|---:|---:|---:|---:|')
        for kind in ('hl_binance', 'hl_bybit', 'binance_bybit'):
            k = b['kinds'].get(kind)
            if not k:
                continue
            ct = k['choose_then_test']
            L.append('| %s | `%s` | %s | %s | %s | %s | %s |'
                     % (kind, k['chosen'], pct(k.get('deployed_apr_test')), num(ct['out_of_sample'].get('sharpe')),
                        num(ct.get('oos_t')), pct((k.get('plateau') or {}).get('top10_median_test_deployed_apr')),
                        pct((k.get('plateau') or {}).get('share_of_all_variants_test_deployed_over_ssr'), 0)))
        L.append('')
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    write_json(out / 'manifest.json', build_manifest(out, a))
    print('wrote', out / 'tables.md', out / 'manifest.json')
    return 0


def build_manifest(out, a):
    """Where every input came from and which code produced the numbers."""
    import hashlib
    raw = out / 'raw'

    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16] if Path(path).exists() else None

    def load(path):
        return json.loads(Path(path).read_text()) if Path(path).exists() else None
    hl_store = Path(a.get('hl_store') or 'research/2026-10-09/perps_history')
    hlm = load(hl_store / 'manifest.json') or {}
    ex = load(raw / 'hl_extra' / 'delisted.json') or {}
    snap = load(out / 'snapshot.json') or {}
    man = {
        'generated': utc(),
        'code': {'scripts/funding_arb.py': sha(ROOT / 'scripts' / 'funding_arb.py'),
                 'scripts/backtest.py': sha(ROOT / 'scripts' / 'backtest.py')},
        'study': {'grid_start': a['grid']['t0'], 'hours': a['grid']['hours'], 'test_start': a['grid']['test_start'],
                  'decision_step_hours': a['grid']['step_hours'], 'variants_per_pair_type': a['grid']['variants_per_pair_type'],
                  'trials_total': a.get('trials_total')},
        'hyperliquid_store': {'path': str(hl_store), 'collected_at': hlm.get('collected_at'),
                              'since_utc': hlm.get('since_utc'), 'until_utc': hlm.get('until_utc'),
                              'markets': hlm.get('markets'), 'failures': len(hlm.get('failures') or {}),
                              'note': 'read-only here; funding with premium hourly from 2025-10-01, 1-hour candles '
                                      'for the last 5,000 hours only'},
        'hyperliquid_extra': {'delisted_checked': len(ex.get('checked') or []),
                              'delisted_pairable': len(ex.get('pairable') or []),
                              'delisted_with_data': ex.get('coins'),
                              'store_missing_fetched_here': ex.get('store_missing_fetched_here'),
                              'candles_4h': len(list((raw / 'hl_extra' / 'candles_4h').glob('*.json.gz')))
                              if (raw / 'hl_extra' / 'candles_4h').exists() else 0,
                              'spot_pairs': load(raw / 'hl_extra' / 'spot_map.json')},
        'cex_collections': {fn.name: {k: v for k, v in (load(fn) or {}).items() if k != 'failures'}
                            for fn in sorted(out.glob('collect_manifest_*.json'))},
        'snapshot': {v: (snap.get(v) or {}).get('at') for v in ('binance', 'bybit', 'okx', 'hl', 'hl_spot')},
        'mapping': {'listings_checked': a['mapping']['checked'], 'dropped': a['mapping']['dropped']},
    }
    return man


# ---------------------------------------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--hl', default='research/2026-10-09/perps_history')
    c.add_argument('--since', default=SINCE)
    c.add_argument('--venues', default='binance,bybit')
    c.add_argument('--force', action='store_true')
    c.add_argument('--refresh-meta', action='store_true')
    c.add_argument('--okx-since', default='2026-06-20')
    c.add_argument('--okx-threads', type=int, default=5)
    c.add_argument('--bn-threads', type=int, default=3)
    c.add_argument('--by-threads', type=int, default=4)
    x = sub.add_parser('hl-extra'); x.set_defaults(fn=cmd_hl_extra)
    x.add_argument('--out', required=True)
    x.add_argument('--hl', default='research/2026-10-09/perps_history')
    x.add_argument('--interval', type=float, default=3.0)
    n = sub.add_parser('snapshot'); n.set_defaults(fn=cmd_snapshot)
    n.add_argument('--out', required=True)
    n.add_argument('--venues', default='binance,bybit')
    n.add_argument('--hl-interval', type=float, default=1.0)
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--hl', default='research/2026-10-09/perps_history')
    a.add_argument('--kinds', default='hl_binance,hl_bybit,binance_bybit,okx,spot,factor')
    a.add_argument('--train-start', default=TRAIN_START)
    a.add_argument('--test-start', default=TEST_START)
    a.add_argument('--tag', default='', help='suffix for the output file, e.g. split0601')
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
