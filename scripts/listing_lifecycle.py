#!/usr/bin/env python3
"""The life cycle of a perp: does a new Hyperliquid listing decay against seasoned alts, and what happens on the way out?

Why. Two loose ends from the funding study (research/2026-10-09/funding_arb): its HL-vs-Binance profit leaned on coins
that were later delisted ("funding blows out on a market heading for delisting"), and the unlock study found that
shorting almost any alt against BTC made money this year. Both point at the ends of a market's life. At the start, a
new perp lists into airdrop and unlock supply with a thin book; the folklore is that it bleeds for weeks and that the
funding a short pays does not charge for it. At the end, an exchange announces a delisting days ahead, its book empties
and its funding and premium can run wild while the coin still trades elsewhere. Both are slow edges (days to weeks, no
latency or block-position race), so both fit the book if they survive a fair test.

Part (a), new listings. The listing calendar is every Hyperliquid core perp's first trading hour: the first live
funding row (from the shared store, the funding study's delisted extras, or fetched here) and, for the coins that
predate them, the first daily candle (candleSnapshot serves the last 5,000 bars of a coin's own history, which for daily
bars is all of it). Migrations of seasoned coins (RNDR->RENDER, MATIC->POL, FTM->S, MKR->SKY) are not new listings.
Each listing is tagged: a coin whose first CEX perp (Binance or Bybit) came more than 60 days before Hyperliquid is an
*established* coin new to Hyperliquid; a coin Hyperliquid listed at least two days before any CEX perp is *pre-launch*
(Hyperliquid's pre-launch "hyperps" price off their own mark until the token trades, so they are reported apart). The
trade: short the new perp d days after its listing and hold H days, hedged long with the same notional of (i) BTC or
(ii) an equal-weight basket of seasoned Hyperliquid alts (listed more than 180 days before entry, delisted ones
included while they traded); P&L = -coin return + hedge return + the hourly funding the short receives - the funding
the hedge pays - both round trips, all on daily closes, funding weighted by each leg's price path. The placebo is the
same coin's same window starting 90 days later. (d, H, hedge) is chosen on the first half of listings by date and
tested once on the second half; listings cluster in time, so every t is computed on listing-week means.

Part (b), delistings. Binance announces USD-M perp delistings in its CMS (catalog 161) a few days ahead, with the
settlement time in the body; Hyperliquid's delistings are visible only as the hour its funding rows turn to exactly
zero. Around each event the module lines up both venues' funding, premium, price against BTC and the seasoned basket,
volume and (Binance) open interest, and prices two slow trades: (1) convergence, short the perp whose funding or premium
has blown out and long the coin on the other venue, from the announcement plus a delay of hours to the settlement; (2)
drift, short the announced coin against the seasoned basket over the same window, against a placebo a month earlier.

Conventions. Funding rates are fractions of notional per settlement, positive when longs pay (a short receives +rate).
P&L is a fraction of one leg's notional, which is also the capital charged (each leg margined at 2x); the benchmark is
the Sky savings rate, 3.80% a year, on that capital for the days it is tied up. Costs: Hyperliquid taker 4.5bp,
Binance 5bp a fill, plus half-spread and impact from the live books of 2026-10-10 (the funding study's snapshot, and
fresh books for the newest listings and any pending delisting).

    python3 scripts/listing_lifecycle.py collect --stage hl-meta     --out research/2026-10-10/listing_lifecycle
    python3 scripts/listing_lifecycle.py collect --stage hl-candles  --out research/2026-10-10/listing_lifecycle  # 1d bars, every coin
    python3 scripts/listing_lifecycle.py collect --stage hl-funding  --out research/2026-10-10/listing_lifecycle  # pre-store months
    python3 scripts/listing_lifecycle.py collect --stage binance     --out research/2026-10-10/listing_lifecycle  # CMS + delisted perps
    python3 scripts/listing_lifecycle.py collect --stage books       --out research/2026-10-10/listing_lifecycle  # newest listings
    python3 scripts/listing_lifecycle.py analyze --out research/2026-10-10/listing_lifecycle
    python3 scripts/listing_lifecycle.py render  --out research/2026-10-10/listing_lifecycle
"""
import argparse
import bisect
import datetime as dt
import gzip
import io
import json
import math
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
SSR = 0.038                     # Sky savings rate, 3.80% a year: the benchmark on the capital a trade ties up
FEE_BP = {'hl': 4.5, 'binance': 5.0, 'bybit': 5.5, 'binance_spot': 10.0}
STORE = ROOT / 'research' / '2026-10-09' / 'perps_history'
FUNDING_STUDY = ROOT / 'research' / '2026-10-09' / 'funding_arb'
HL_EXTRA = FUNDING_STUDY / 'raw' / 'hl_extra'
UNLOCKS = ROOT / 'research' / '2026-10-09' / 'unlocks'
STORE_START = '2025-10-01'      # the shared store's funding begins here
STUDY_START = '2024-01-01'      # listings from here on enter part (a)
CANDLES_FROM = '2023-01-01'
# Coins that are the same asset as an earlier Hyperliquid market under a new ticker: not new listings.
MIGRATIONS = {'RENDER': 'RNDR', 'POL': 'MATIC', 'S': 'FTM', 'SKY': 'MKR'}
NOT_ALTS = {'BTC', 'ETH', 'PAXG'}          # left out of the seasoned-alt basket (BTC is the other hedge; gold is not an alt)
BASKET_MIN_AGE_DAYS = 180
CMS_LIST = 'https://www.binance.com/bapi/composite/v1/public/cms/article/list/query'
CMS_DETAIL = 'https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query'
BN = 'https://fapi.binance.com'
BN_SPOT = 'https://api.binance.com'
VISION = 'https://data.binance.vision/data'
UA = 'Mozilla/5.0'


# ------------------------------------------------------------------------------------------------ small helpers

def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_gz(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(obj, f, separators=(',', ':'))
    tmp.replace(p)


def write_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))
    tmp.replace(p)


def load_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else default


def safe(coin):
    return coin.replace(':', '__').replace('/', '_')


def ms_of(day):
    d = dt.datetime.fromisoformat(day)
    if d.tzinfo is None:
        d = d.replace(tzinfo=UTC)
    return int(d.timestamp() * 1000)


def iso(ms):
    return None if ms is None else dt.datetime.fromtimestamp(ms / 1000, UTC).isoformat(timespec='minutes')


def hour_of(ms):
    """The hour a settlement belongs to: payments land a few milliseconds after the boundary."""
    return int((int(ms) + HOUR_MS // 2) // HOUR_MS * HOUR_MS)


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


def hl_row_live(r):
    """A Hyperliquid funding row from a trading market. A delisted market keeps printing hourly rows with rate and
    premium both exactly zero; a live one never does (its floor is the interest rate, 1.25e-5 an hour)."""
    return not (fnum(r.get('fundingRate'), 0.0) == 0.0 and fnum(r.get('premium'), 0.0) == 0.0)


class Http:
    """Paced GET with retries for the Binance hosts. A 429/418 waits for Retry-After (or a minute) before anything else
    goes to that host, because Binance bans an IP that keeps calling after a 429."""

    def __init__(self, interval=0.3, timeout=40, retries=5):
        self.interval, self.timeout, self.retries = interval, timeout, retries
        self.next_at = 0.0
        self.n = self.errors = self.throttled = 0

    def get(self, url, params=None, raw=False):
        if params:
            url = url + '?' + urllib.parse.urlencode(params)
        last = None
        for attempt in range(self.retries):
            wait = self.next_at - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self.next_at = time.monotonic() + self.interval
            self.n += 1
            try:
                req = urllib.request.Request(url, headers={'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    body = r.read()
                return body if raw else json.loads(body.decode())
            except urllib.error.HTTPError as e:
                last = 'HTTP %s' % e.code
                if e.code in (429, 418):
                    self.throttled += 1
                    ra = fnum(e.headers.get('Retry-After'), 60.0) if e.headers else 60.0
                    self.next_at = time.monotonic() + max(1.0, min(ra, 300.0))
                    continue
                if e.code in (500, 502, 503, 504):
                    self.errors += 1
                    time.sleep(min(10.0, 0.5 * 2 ** attempt))
                    continue
                self.errors += 1
                if raw:
                    return None
                try:
                    return {'_http_error': e.code, '_body': e.read().decode()[:300]}
                except Exception:  # noqa: BLE001
                    return {'_http_error': e.code}
            except Exception as e:  # noqa: BLE001 - network errors are retried
                last = repr(e)[:160]
                self.errors += 1
                time.sleep(min(10.0, 0.5 * 2 ** attempt))
        raise RuntimeError('retry limit: %s %s' % (last, url[:140]))

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


# ------------------------------------------------------------------------------------------------ Hyperliquid inputs

def store_funding_path(coin):
    """Where an hourly funding file for `coin` already exists on disk: the shared store, then the funding study's
    delisted extras. None if neither has it."""
    for p in (STORE / 'funding' / (safe(coin) + '.json.gz'), HL_EXTRA / 'funding' / (safe(coin) + '.json.gz')):
        if p.exists():
            return p
    return None


def load_funding_rows(out, coin):
    """Every hourly funding row on disk for `coin` (store, extras, and this study's own fetches), one per hour, live
    rows only, sorted: [(hour_ms, rate, premium)]."""
    rows = {}
    for p in (store_funding_path(coin), Path(out) / 'raw' / 'hl' / 'funding' / (safe(coin) + '.json.gz')):
        if p and Path(p).exists():
            for r in read_gz(p):
                if hl_row_live(r):
                    rows[hour_of(r['time'])] = (fnum(r['fundingRate'], 0.0), fnum(r.get('premium'), 0.0))
    return [(h, v[0], v[1]) for h, v in sorted(rows.items())]


def cmd_collect_hl_meta(args, out):
    import perp_rpc as R
    api = R.Info(interval=max(0.3, args.interval))
    raw = out / 'raw' / 'hl'
    write_json(raw / 'meta.json', api.post({'type': 'meta'}))
    write_json(raw / 'meta_ctxs.json', R.meta_and_ctxs(api))
    print(json.dumps({'meta': len(load_json(raw / 'meta.json')['universe']), 'api': api.stats()}))
    return api.stats()


def cmd_collect_hl_candles(args, out):
    """Daily candles for every core perp Hyperliquid has ever listed (live and delisted): one call each, all history."""
    import perp_rpc as R
    api = R.Info(interval=max(0.3, args.interval))
    raw = out / 'raw' / 'hl'
    meta = load_json(raw / 'meta.json')
    coins = [u['name'] for u in meta['universe']]
    s, e = ms_of(CANDLES_FROM), int(time.time() * 1000)
    failed = {}
    for k, c in enumerate(coins):
        fp = raw / 'candles_1d' / (safe(c) + '.json.gz')
        if fp.exists():
            continue
        try:
            rows = R.candles(api, c, '1d', s, e) or []
        except R.APIError as ex:
            failed[c] = str(ex)[:120]
            continue
        write_gz(fp, rows)
        if k % 25 == 0:
            print(json.dumps({'done': k, 'of': len(coins), 'api': api.stats()}), flush=True)
    print(json.dumps({'coins': len(coins), 'failed': failed, 'api': api.stats()}))
    return {'coins': len(coins), 'failed': failed, 'api': api.stats()}


def first_candle_ms(out, coin):
    """Open time of the first daily bar with a trade (earlier bars are zero-volume fills from before the listing)."""
    p = Path(out) / 'raw' / 'hl' / 'candles_1d' / (safe(coin) + '.json.gz')
    if not p.exists():
        return None
    rows = [r for r in read_gz(p) if traded(r)]
    return int(rows[0]['t']) if rows else None


def last_candle_ms(out, coin):
    """Close time of the last daily bar with a trade."""
    p = Path(out) / 'raw' / 'hl' / 'candles_1d' / (safe(coin) + '.json.gz')
    if not p.exists():
        return None
    rows = [r for r in read_gz(p) if traded(r)]
    return int(rows[-1]['T']) if rows else None


def fetch_funding(api, coin, start, end):
    """Hourly funding rows in [start, end], paged 500 at a time. A full page of dead rows (rate and premium exactly
    zero) ends the walk: the market was delisted."""
    import perp_rpc as R
    rows, s = [], start
    for _ in range(80):
        r = R.funding_history(api, coin, s, end) or []
        if not isinstance(r, list) or not r:
            break
        rows += r
        if len(r) < 500 or not any(hl_row_live(x) for x in r):
            break
        s = int(r[-1]['time']) + 1
    return rows


def funding_needs(out, meta, horizon_days=160):
    """(coin, start_ms, end_ms) ranges of hourly funding this study needs and nothing on disk holds.

    Part (a) needs each listing's first `horizon_days` (the event windows and the placebo 90 days on) for listings
    since STUDY_START; the store begins at STORE_START, so only the months before it are fetched. BTC and a fixed set
    of seasoned alts are fetched over the same pre-store months for the hedge legs. Part (b) needs the 45 days before
    each Hyperliquid delisting since 2025-01-01 that the store and the funding study's extras do not cover."""
    s0, store0 = ms_of(STUDY_START), ms_of(STORE_START)
    needs = []
    for u in meta['universe']:
        c = u['name']
        L = first_candle_ms(out, c)
        if L is None:
            continue
        if s0 - 2 * DAY_MS <= L < store0:
            needs.append((c, max(L - DAY_MS, s0 - 2 * DAY_MS), min(L + horizon_days * DAY_MS, store0 + DAY_MS)))
        if u.get('isDelisted'):
            last = last_candle_ms(out, c)
            if last and ms_of('2025-01-01') <= last < store0 and store_funding_path(c) is None:
                needs.append((c, last - 45 * DAY_MS, last + 2 * DAY_MS))
    for c in ['BTC'] + list(HEDGE_FUNDING_SUBSET):
        needs.append((c, s0 - 2 * DAY_MS, store0 + DAY_MS))
    # merge overlapping ranges per coin
    by = {}
    for c, a, b in needs:
        by.setdefault(c, []).append([a, b])
    merged = []
    for c, rs in by.items():
        rs.sort()
        cur = rs[0]
        for a, b in rs[1:]:
            if a <= cur[1]:
                cur[1] = max(cur[1], b)
            else:
                merged.append((c, cur[0], cur[1]))
                cur = [a, b]
        merged.append((c, cur[0], cur[1]))
    return merged


# Seasoned alts whose funding is fetched for the months before the store, to stand for the basket's funding there.
# Chosen before looking at any result: the largest-volume core alts that traded continuously from 2023 to now.
HEDGE_FUNDING_SUBSET = ('SOL', 'DOGE', 'XRP', 'AVAX', 'LINK')
# (Ten were chosen at first; the venue's shared rate limit made the fetch take an hour, so the first five were kept.)


def cmd_collect_hl_funding(args, out):
    import perp_rpc as R
    api = R.Info(interval=max(0.3, args.interval))
    raw = out / 'raw' / 'hl'
    meta = load_json(raw / 'meta.json')
    needs = funding_needs(out, meta)
    # Hedge legs first, then listings newest first: the test half is the recent listings, and the venue's shared rate
    # limit means a fetch can be cut short.
    hedge = {'BTC', *HEDGE_FUNDING_SUBSET}
    needs.sort(key=lambda x: (0 if x[0] in hedge else 1, -x[1]))
    print(json.dumps({'ranges': len(needs), 'coins': len({c for c, _, _ in needs})}), flush=True)
    failed, pages = {}, 0
    for k, (c, a, b) in enumerate(needs):
        fp = raw / 'funding' / (safe(c) + '.json.gz')
        have = read_gz(fp) if fp.exists() else []
        hours = {hour_of(r['time']) for r in have}
        # already fetched: the range's first and last hours (or a dead tail) are on disk
        if have and (hour_of(a + HOUR_MS) in hours or min(hours) <= a + DAY_MS) and max(hours) >= min(b, int(time.time() * 1000)) - 2 * DAY_MS:
            continue
        try:
            rows = fetch_funding(api, c, a, b)
        except R.APIError as ex:
            failed['%s:%s' % (c, iso(a))] = str(ex)[:120]
            continue
        pages += max(1, math.ceil(len(rows) / 500))
        merged = {hour_of(r['time']): r for r in have}
        merged.update({hour_of(r['time']): r for r in rows})
        write_gz(fp, [merged[h] for h in sorted(merged)])
        if k % 10 == 0:
            print(json.dumps({'done': k, 'of': len(needs), 'coin': c, 'api': api.stats()}), flush=True)
    print(json.dumps({'ranges': len(needs), 'failed': failed, 'api': api.stats()}))
    return {'ranges': len(needs), 'pages_fetched_est': pages, 'failed': failed, 'api': api.stats()}


def cmd_collect_books(args, out):
    """Fresh Hyperliquid books for the newest listings (the only live view of a book in its first weeks) and for any
    coin with a pending delisting; 20 levels a side plus the 4-significant-figure aggregation that reaches further."""
    import perp_rpc as R
    api = R.Info(interval=max(0.3, args.interval))
    raw = out / 'raw' / 'hl'
    meta = load_json(raw / 'meta.json')
    now = int(time.time() * 1000)
    recent = []
    for u in meta['universe']:
        if u.get('isDelisted'):
            continue
        L = first_candle_ms(out, u['name'])
        if L and now - L <= args.recent_days * DAY_MS:
            recent.append(u['name'])
    extra = [c for c in (args.coins.split(',') if args.coins else []) if c]
    books = {}
    for c in recent + extra:
        try:
            fine = R.l2_book(api, c)
            coarse = api.post({'type': 'l2Book', 'coin': c, 'nSigFigs': 4})
        except R.APIError as ex:
            books[c] = {'error': str(ex)[:120]}
            continue
        books[c] = {'at': iso(now), 'fine': fine, 'coarse': coarse}
    write_json(raw / 'books_recent.json', {'at': iso(now), 'recent_days': args.recent_days, 'books': books})
    print(json.dumps({'books': len(books), 'recent': recent, 'api': api.stats()}))
    return {'books': len(books), 'recent': recent, 'api': api.stats()}


# ------------------------------------------------------------------------------------------------ Binance inputs

def cms_text(body):
    """Plain text of a Binance CMS article body (a JSON tree of nodes, or HTML in older articles)."""
    try:
        tree = json.loads(body)
    except (TypeError, ValueError):
        return re.sub(r'<[^>]+>', ' ', body or '')
    out = []

    def walk(n):
        if isinstance(n, dict):
            if n.get('node') == 'text':
                out.append(n.get('text', ''))
            for c in n.get('child') or []:
                walk(c)
        elif isinstance(n, list):
            for c in n:
                walk(c)
    walk(tree)
    return ' '.join(out)


SETTLE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s*\(UTC\)\s*:\s*(?:USDⓈ-M|USDS-M|USD.-M|USDⓈ-Margined)?\s*'
                       r'((?:[0-9A-Z]{2,30}(?:USDT|USDC)\b[ ,]*(?:and\s+)?)+)')
DT_RE = re.compile(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s*\(UTC\)')
SYM_RE = re.compile(r'\b([0-9A-Z]{2,30}(?:USDT|USDC))\b')
TITLE_TOKENS_RE = re.compile(r'Will Delist (.+?) on \d{4}-\d{2}-\d{2}')


def parse_delisting(text, title=''):
    """Settlement and reduce-only times of the USD-M perpetuals a Binance delisting notice names.

    Returns (rows, title_tokens): rows [{'symbol', 'settle_ms', 'reduce_only_ms'}], where `symbol` is None for a time
    that applies to "the contracts of the aforementioned token(s)" (a spot notice that also delists the perps; the
    tokens are the title's, resolved to perp symbols by `resolve_tokens`). Three wordings occur:
      "settlement on USDⓈ-M XUSDT and YUSDT Perpetual Contracts at 2025-11-14 09:00 (UTC)"            (one sentence)
      "settlement the following perpetual contract(s) as below: 2026-10-05 09:00 (UTC) : USDⓈ-M XUSDT, YUSDT ..."
      "settlement on the contracts of the aforementioned token(s) at 2026-08-26 09:00 (UTC)"           (spot notices)
    and the end of new positions is stated the same way with "not allowed to open new".
    """
    text = (text or '').replace('\u00a0', ' ').replace('&nbsp;', ' ')
    chunks = re.split(r'\s+\.\s+|(?<=[.;])\s+(?=[A-Z])', text)
    m = TITLE_TOKENS_RE.search(title or '')
    tokens = [t.strip() for t in re.split(r',|\band\b', m.group(1)) if t.strip()] if m else []
    tokens = [re.sub(r'\s*\(.*?\)', '', t).strip() for t in tokens]
    out = {}
    last_syms = SYM_RE.findall(title or '')
    for ch in chunks:
        low = ch.lower()
        if 'not allowed' in low or 'open new' in low or 'non-reduce' in low:
            kind = 'reduce_only_ms'
        elif 'settlement' in low or 'close all positions' in low:
            kind = 'settle_ms'
        else:
            continue
        groups = list(SETTLE_RE.finditer(ch))
        if groups:
            pairs = [(ms_of('%sT%s:00+00:00' % (g.group(1), g.group(2))), SYM_RE.findall(g.group(3))) for g in groups]
        else:
            dts = DT_RE.findall(ch)
            if not dts:
                continue
            syms = SYM_RE.findall(ch)
            if not syms and 'aforementioned' not in low and not last_syms:
                continue
            pairs = [(ms_of('%sT%s:00+00:00' % dts[0]), syms or last_syms or [None])]
        for when, syms in pairs:
            if kind == 'settle_ms' and syms and syms != [None]:
                last_syms = syms
            for sy in syms:
                r = out.setdefault(sy, {'symbol': sy, 'settle_ms': None, 'reduce_only_ms': None})
                if r[kind] is None or when < r[kind]:
                    r[kind] = when
    rows = sorted(out.values(), key=lambda r: (r['settle_ms'] or 0, r['symbol'] or ''))
    return rows, tokens


def resolve_tokens(tokens, exchange_symbols):
    """Perp symbols (USDT or USDC quoted) whose base asset is one of `tokens`, allowing Binance's 1000/1000000 unit
    prefixes. `exchange_symbols` is exchangeInfo's symbol list."""
    want = {t.upper() for t in tokens}
    out = []
    for s in exchange_symbols:
        if s.get('contractType') != 'PERPETUAL':
            continue
        base = s.get('baseAsset', '')
        core = re.sub(r'^(1000000|10000|1000|1M)(?=[A-Z])', '', base)
        if base.upper() in want or core.upper() in want:
            out.append(s['symbol'])
    return sorted(out)


def is_delisting_notice(title):
    """A notice that can delist a USD-M perpetual: a futures delisting, or a spot delisting (which closes the perps of
    the same tokens in a 'Futures' section). Margin, loan, Alpha and spot-pair removals cannot."""
    t = (title or '').lower()
    if 'delist' not in t:
        return False
    # phrases, not words: "ALPHAUSDT" and "USDⓈ-Margined" are futures delistings
    return not any(k in t for k in ('binance alpha', 'margin and loan', 'margin trading', 'loan will', 'vip loan',
                                    'notice of removal', 'monitoring tag', 'fiat'))


def is_futures_delisting(title):
    t = title.lower()
    return ('futures' in t and 'delist' in t) or ('perpetual' in t and 'delist' in t)


def vision_zip_rows(http, url):
    """Rows of the single CSV inside a data.binance.vision zip (None when the file is not there)."""
    body = http.get(url, raw=True)
    if not body:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
        name = z.namelist()[0]
        lines = z.read(name).decode().splitlines()
    except (zipfile.BadZipFile, IndexError):
        return None
    rows = [ln.split(',') for ln in lines if ln and ln[0].isdigit() or (ln and ln.split(',')[0][:2] == '20')]
    return rows


def months_between(a_ms, b_ms):
    d = dt.datetime.fromtimestamp(a_ms / 1000, UTC).replace(day=1)
    end = dt.datetime.fromtimestamp(b_ms / 1000, UTC)
    out = []
    while d <= end:
        out.append(d.strftime('%Y-%m'))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return out


def bn_paged_klines(http, path, sym, start, end, interval='1h', host=BN):
    rows, s = [], start
    for _ in range(40):
        r = http.get(host + path, {'symbol': sym, 'interval': interval, 'startTime': s, 'endTime': end, 'limit': 1500
                                   if host == BN else 1000})
        if not isinstance(r, list) or not r:
            break
        rows += [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7] or 0)] for x in r]
        if len(r) < (1500 if host == BN else 1000):
            break
        s = int(r[-1][0]) + HOUR_MS
    return rows


def bn_funding_rows(http, sym, start, end):
    rows, s = [], start
    for _ in range(30):
        r = http.get(BN + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': end, 'limit': 1000})
        if not isinstance(r, list):
            break
        rows += [{'t': int(x['fundingTime']), 'rate': float(x['fundingRate']), 'mark': fnum(x.get('markPrice'))}
                 for x in r]
        if len(r) < 1000:
            break
        s = int(r[-1]['fundingTime']) + 1
    return rows


def cmd_collect_binance(args, out):
    """Binance's delisting notices for a year, then each delisted USD-M perp's funding, premium index and trade candles
    around its settlement, its spot candles where a spot pair existed, and its daily open-interest metrics."""
    raw = out / 'raw' / 'binance'
    raw.mkdir(parents=True, exist_ok=True)
    web = Http(interval=1.0)
    since = ms_of(args.since)
    # 1. the notice list, newest first, paged until older than `since`
    articles = []
    for page in range(1, 40):
        fp = raw / 'cms' / ('list_%02d.json' % page)
        if fp.exists() and not args.refresh:
            d = load_json(fp)
        else:
            d = web.get(CMS_LIST, {'type': 1, 'catalogId': 161, 'pageNo': page, 'pageSize': 50})
            write_json(fp, d)
        arts = ((((d or {}).get('data') or {}).get('catalogs') or [{}])[0]).get('articles') or []
        articles += arts
        if not arts or min(a['releaseDate'] for a in arts) < since:
            break
    fut = [a for a in articles if a['releaseDate'] >= since and is_delisting_notice(a['title'])]
    events = []
    for a in fut:
        fp = raw / 'cms' / 'articles' / (a['code'] + '.json')
        if fp.exists():
            d = load_json(fp)
        else:
            d = web.get(CMS_DETAIL, {'articleCode': a['code']})
            write_json(fp, d)
        body = ((d or {}).get('data') or {}).get('body') or ''
        text = cms_text(body)
        rows, tokens = parse_delisting(text, a['title'])
        for r in rows:
            events.append(dict(r, article=a['code'], title=a['title'], announced_ms=a['releaseDate'], tokens=tokens))
    write_json(raw / 'delisting_notices.json', {'articles_listed': len(articles), 'futures_notices': len(fut),
                                                'events': events})
    print(json.dumps({'articles': len(articles), 'futures_notices': len(fut), 'events': len(events),
                      'web': web.stats()}), flush=True)
    # 2. exchange info (delisted perps stay as SETTLING with their delivery date)
    api = Http(interval=0.35)
    ei_p = raw / 'exchangeInfo.json'
    if not ei_p.exists() or args.refresh:
        write_json(ei_p, api.get(BN + '/fapi/v1/exchangeInfo'))
    ei = load_json(ei_p)
    delivery = {s['symbol']: s.get('deliveryDate') for s in ei.get('symbols', []) if s.get('status') != 'TRADING'}
    syms = sorted({e['symbol'] for e in events if e['symbol']} | {s for s, d in delivery.items()
                                                                if d and since <= d <= int(time.time() * 1000)})
    vis = Http(interval=0.15)
    done, failed = 0, {}
    for sym in syms:
        settle = next((e['settle_ms'] for e in events if e['symbol'] == sym and e['settle_ms']), None) or delivery.get(sym)
        if not settle:
            failed[sym] = 'no settlement time'
            continue
        a, b = settle - args.days_before * DAY_MS, settle + HOUR_MS
        try:
            for kind, path in (('premium', '/fapi/v1/premiumIndexKlines'), ('klines', '/fapi/v1/klines')):
                fp = raw / kind / (sym + '.json.gz')
                if not fp.exists():
                    write_gz(fp, bn_paged_klines(api, path, sym, a, b))
            fp = raw / 'funding' / (sym + '.json.gz')
            if not fp.exists():
                write_gz(fp, bn_funding_rows(api, sym, a, b))
            # spot: the same base against USDT, from the archive (delisted spot pairs are gone from the API)
            fp = raw / 'spot_klines' / (sym + '.json.gz')
            if not fp.exists():
                rows = []
                spot_sym = sym if sym.endswith('USDT') else None
                if spot_sym:
                    for mth in months_between(a, settle + 10 * DAY_MS):
                        rr = vision_zip_rows(vis, '%s/spot/monthly/klines/%s/1h/%s-1h-%s.zip' % (
                            VISION, spot_sym, spot_sym, mth))
                        if rr is None:
                            # the current month is only in daily files
                            continue
                        rows += [[int(x[0]) // (1000 if int(x[0]) > 1e14 else 1), float(x[1]), float(x[2]),
                                  float(x[3]), float(x[4]), float(x[7] or 0)] for x in rr]
                    if not rows:
                        rows = bn_paged_klines(api, '/api/v3/klines', spot_sym, a, settle + 10 * DAY_MS, host=BN_SPOT)
                write_gz(fp, rows)
            # open interest: daily metrics files (5-minute rows) for the days before the settlement
            fp = raw / 'metrics' / (sym + '.json.gz')
            if not fp.exists():
                rows = []
                for k in range(args.metrics_days, -1, -1):
                    day = dt.datetime.fromtimestamp((settle - k * DAY_MS) / 1000, UTC).strftime('%Y-%m-%d')
                    rr = vision_zip_rows(vis, '%s/futures/um/daily/metrics/%s/%s-metrics-%s.zip' % (VISION, sym, sym, day))
                    for x in rr or []:
                        # create_time, symbol, sum_open_interest, sum_open_interest_value, ...
                        try:
                            t = int(dt.datetime.fromisoformat(x[0]).replace(tzinfo=UTC).timestamp() * 1000)
                            rows.append([t, float(x[2]), float(x[3])])
                        except (ValueError, IndexError):
                            continue
                write_gz(fp, rows)
            done += 1
        except RuntimeError as ex:
            failed[sym] = str(ex)[:160]
    print(json.dumps({'symbols': len(syms), 'done': done, 'failed': failed, 'api': api.stats(), 'vision': vis.stats()}))
    return {'notices': len(fut), 'events': len(events), 'symbols': len(syms), 'done': done, 'failed': failed,
            'api': api.stats(), 'vision': vis.stats(), 'web': web.stats()}


def cmd_collect(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    fn = {'hl-meta': cmd_collect_hl_meta, 'hl-candles': cmd_collect_hl_candles, 'hl-funding': cmd_collect_hl_funding,
          'books': cmd_collect_books, 'binance': cmd_collect_binance}[args.stage]
    res = fn(args, out)
    man = load_json(out / 'manifest.json', {}) or {}
    man.setdefault('stages', {})[args.stage] = {'at': iso(int(t0 * 1000)), 'seconds': round(time.time() - t0, 1),
                                                'result': res}
    man['sources'] = {
        'hyperliquid_info': 'https://api.hyperliquid.xyz/info (meta, metaAndAssetCtxs, candleSnapshot 1d, '
                            'fundingHistory, l2Book) via scripts/perp_rpc.Info',
        'shared_store': str(STORE.relative_to(ROOT)), 'funding_study_raw': str((FUNDING_STUDY / 'raw').relative_to(ROOT)),
        'binance_cms': CMS_LIST + ' (catalogId 161) and ' + CMS_DETAIL,
        'binance_fapi': BN + ' (/fapi/v1/exchangeInfo, fundingRate, premiumIndexKlines, klines)',
        'binance_archive': VISION + ' (spot monthly 1h klines, futures daily metrics)'}
    write_json(out / 'manifest.json', man)
    return 0


# ================================================================================================ shared series

def traded(c):
    """A candle with at least one trade in it."""
    return int(c.get('n') or 0) > 0 or fnum(c.get('v'), 0.0) > 0


class Daily:
    """A coin's daily closes on Hyperliquid, keyed by bar end (00:00 UTC of the next day), with its daily volume."""

    def __init__(self, candles):
        """Bars before the first one with a trade are dropped: candleSnapshot fills the days (for some coins, years)
        before a market opened with zero-volume bars at a price nobody traded, so the first bar is not the listing."""
        self.close, self.vol, self.high, self.low = {}, {}, {}, {}
        candles = list(candles or [])
        self.first_bar_open = int(candles[0]['t']) if candles else None
        k = next((i for i, c in enumerate(candles) if traded(c)), None)
        candles = candles[k:] if k is not None else []
        self.first_traded_open = int(candles[0]['t']) if candles else None
        last_traded = next((c for c in reversed(candles) if traded(c)), None)
        self.last_traded_close = int(last_traded['t']) + DAY_MS if last_traded else None
        for c in candles:
            t = int(c['t']) + DAY_MS
            px = float(c['c'])
            self.close[t] = px
            self.vol[t] = float(c.get('v') or 0.0) * px
            self.high[t] = float(c.get('h') or px)
            self.low[t] = float(c.get('l') or px)
        self.keys = sorted(self.close)

    def first(self):
        return self.keys[0] if self.keys else None

    def last(self):
        return self.keys[-1] if self.keys else None

    def at(self, t, max_age=DAY_MS + HOUR_MS):
        """The latest close at or before t, if it is no older than `max_age`."""
        i = bisect.bisect_right(self.keys, t) - 1
        if i < 0 or t - self.keys[i] > max_age:
            return None
        return self.close[self.keys[i]]

    def max_high(self, t0, t1):
        """Highest daily high among bars ending in (t0, t1]: the worst point for a short opened at t0."""
        i = bisect.bisect_right(self.keys, t0)
        j = bisect.bisect_right(self.keys, t1)
        return max((self.high[k] for k in self.keys[i:j]), default=None)

    def path(self, t0, t1):
        """[(bar end, close)] for bar ends in [t0, t1]."""
        i = bisect.bisect_left(self.keys, t0)
        j = bisect.bisect_right(self.keys, t1)
        return [(k, self.close[k]) for k in self.keys[i:j]]


def ceil_day(t):
    return -(-int(t) // DAY_MS) * DAY_MS


def day_funding(rows):
    """{day start ms: sum of hourly rates paid in (day, day + 1d]} from [(hour_ms, rate, premium)] rows, and the set of
    days with a full 24 rows (anything less is a partial day: a listing, a delisting or a gap)."""
    d, cnt = {}, {}
    for h, r, _ in rows:
        k = (h - 1) // DAY_MS * DAY_MS
        d[k] = d.get(k, 0.0) + r
        cnt[k] = cnt.get(k, 0) + 1
    return d, cnt


def weighted_funding(fday, daily, t0, t1):
    """Funding a fixed-quantity short opened at t0 receives through t1 (both day boundaries), as a fraction of its
    entry notional: each day's summed hourly rate times the coin's price at the start of that day over the entry price.
    Returns (funding, days with data, days in window)."""
    p0 = daily.at(t0)
    if not p0:
        return None, 0, 0
    tot, have, n = 0.0, 0, 0
    for D in range(int(t0), int(t1), DAY_MS):
        n += 1
        if D in fday:
            px = daily.at(D) or p0
            tot += fday[D] * px / p0
            have += 1
    return tot, have, n


FLOOR_RATE_DAY = 24 * 1.25e-5       # Hyperliquid's interest-only funding, 10.95% a year: the stand-in for a missing day


# ================================================================================================ part (a): new listings

def cex_first_listing(funding_raw=FUNDING_STUDY / 'raw'):
    """{core name: {'binance': first onboard ms, 'bybit': first launch ms}} over every USDT/USDC perpetual either venue
    has listed, delisted ones included (Binance keeps them as SETTLING, Bybit under status=Closed)."""
    out = {}
    ei = load_json(Path(funding_raw) / 'bn_exchangeInfo.json', {}) or {}
    for s_ in ei.get('symbols', []):
        if s_.get('contractType') != 'PERPETUAL' or s_.get('quoteAsset') not in ('USDT', 'USDC'):
            continue
        core = re.sub(r'^(1000000|10000|1000|1M)(?=[A-Z])', '', s_.get('baseAsset', '')).upper()
        t = s_.get('onboardDate')
        if t:
            r = out.setdefault(core, {})
            r['binance'] = min(r.get('binance') or t, t)
    seen = set()
    for fn in sorted(Path(funding_raw).glob('by_instruments_*.json')):
        for x in ((load_json(fn, {}) or {}).get('result') or {}).get('list') or []:
            if x.get('contractType') != 'LinearPerpetual' or x.get('quoteCoin') not in ('USDT', 'USDC'):
                continue
            if x['symbol'] in seen:
                continue
            seen.add(x['symbol'])
            core = re.sub(r'^(1000000|10000|1000|1M)(?=[A-Z])', '', x.get('baseCoin', ''))
            core = re.sub(r'(?<=[A-Z])1000$', '', core).upper()
            t = int(x.get('launchTime') or 0) or None
            if t:
                r = out.setdefault(core, {})
                r['bybit'] = min(r.get('bybit') or t, t)
    return out


def hl_core_name(coin):
    return coin[1:] if (len(coin) > 1 and coin[0] == 'k' and coin[1:2].isupper()) else coin


def tag_listing(coin, L, cex, prelaunch_days=2, established_days=60):
    """Cohort tags for one Hyperliquid listing at L (ms): migration, established coin new to Hyperliquid, pre-launch
    (Hyperliquid first by at least `prelaunch_days`), no CEX perp at all, or a new token listed alongside the CEXs."""
    if coin in MIGRATIONS:
        return 'migration'
    c = cex.get(hl_core_name(coin).upper()) or {}
    firsts = [v for v in (c.get('binance'), c.get('bybit')) if v]
    if not firsts:
        return 'hl_only'
    f = min(firsts)
    if f <= L - established_days * DAY_MS:
        return 'established'
    if f >= L + prelaunch_days * DAY_MS:
        return 'prelaunch'
    return 'new_token'


def emissions_match(index_rows):
    """{SYMBOL: row} from DefiLlama's emissions index (symbol upper-cased). Several protocols can share a symbol; the
    one with the larger market cap is kept (collisions are reported by the caller through the price check)."""
    out = {}
    for r in index_rows or []:
        tp = (r.get('tokenPrice') or [{}])[0]
        sym = (tp.get('symbol') or '').upper()
        if not sym:
            continue
        if sym not in out or (r.get('mcap') or 0) > (out[sym].get('mcap') or 0):
            out[sym] = r
    return out


class World:
    """Everything part (a) and (b) read, loaded once: the listing calendar, daily prices, daily funding sums, the
    seasoned-alt basket, and the cost model."""

    def __init__(self, out):
        self.out = Path(out)
        raw = self.out / 'raw' / 'hl'
        self.meta = load_json(raw / 'meta.json')
        self.delisted = {u['name'] for u in self.meta['universe'] if u.get('isDelisted')}
        self.order = {u['name']: i for i, u in enumerate(self.meta['universe'])}
        self.daily, self.fday, self.fcnt, self.frows = {}, {}, {}, {}
        for u in self.meta['universe']:
            c = u['name']
            p = raw / 'candles_1d' / (safe(c) + '.json.gz')
            self.daily[c] = Daily(read_gz(p) if p.exists() else [])
            rows = load_funding_rows(self.out, c)
            self.frows[c] = rows
            self.fday[c], self.fcnt[c] = day_funding(rows)
        self.cex = cex_first_listing()
        self.calendar = self.build_calendar()
        self.data_end = max((d.last() or 0) for d in self.daily.values())
        self._basket_fday = None

    def build_calendar(self):
        """Per coin: the listing (start of the first UTC day with a trade; the hour, where the store's funding shows the
        first non-zero premium that day), the last trading day of a delisted market (its last hour from the last live
        funding row), and the cohort."""
        cal = {}
        for c, d in self.daily.items():
            if not d.keys:
                continue
            L_day = d.first_traded_open
            rows = self.frows.get(c) or []
            first_prem = next((h for h, r, pm in rows if pm != 0.0 and h >= L_day), None)
            L_hour = first_prem - HOUR_MS if (first_prem is not None and first_prem < L_day + DAY_MS) else None
            last_live = None
            if c in self.delisted:
                last_live = d.last_traded_close
                tail = [h for h, r, pm in rows if h <= (last_live or 0) + DAY_MS]
                if tail and tail[-1] >= (last_live or 0) - 2 * DAY_MS:
                    last_live = tail[-1]
            cal[c] = {'coin': c, 'listing_ms': L_day, 'listing_utc': iso(L_day), 'listing_hour_ms': L_hour,
                      'listing_hour_utc': iso(L_hour), 'first_bar_utc': iso(d.first_bar_open),
                      'zero_volume_lead_days': (L_day - d.first_bar_open) // DAY_MS,
                      'delisted': c in self.delisted, 'last_live_ms': last_live, 'last_live_utc': iso(last_live),
                      'cohort': tag_listing(c, L_day, self.cex), 'asset_index': self.order.get(c)}
        return cal

    # ------------------------------------------------------------------ the seasoned basket
    def basket_members(self, t, min_age_days=BASKET_MIN_AGE_DAYS):
        out = []
        for c, r in self.calendar.items():
            if c in NOT_ALTS or r['cohort'] == 'migration':
                continue
            if r['listing_ms'] > t - min_age_days * DAY_MS:
                continue
            if r['last_live_ms'] is not None and r['last_live_ms'] <= t:
                continue
            if self.daily[c].at(t) is None:
                continue
            out.append(c)
        return out

    def basket_return(self, t0, t1, exclude=()):
        """Equal-weight buy-and-hold return of the seasoned alts live at t0, each closed at its last close if it was
        delisted before t1 (its settlement): (return, members)."""
        mem = [c for c in self.basket_members(t0) if c not in exclude]
        rets = []
        for c in mem:
            d = self.daily[c]
            p0 = d.at(t0)
            end = t1
            last = self.calendar[c]['last_live_ms']
            if last is not None and last < t1:
                end = last
            p1 = d.at(end, max_age=3 * DAY_MS)
            if p0 and p1:
                rets.append(p1 / p0 - 1.0)
        return (statistics.fmean(rets) if rets else None), len(rets)

    def basket_fday(self):
        """{day: mean summed daily funding over the basket members (as of that day) whose funding is on disk}: before
        the store (2025-10-01) only HEDGE_FUNDING_SUBSET is on disk, so it stands for the basket there."""
        if self._basket_fday is not None:
            return self._basket_fday
        days = sorted({D for c in self.fday for D in self.fday[c]})
        out, n_used = {}, {}
        mem_cache = {}
        for D in days:
            wk = D // (7 * DAY_MS)
            if wk not in mem_cache:
                mem_cache[wk] = self.basket_members(wk * 7 * DAY_MS)
            vals = [self.fday[c][D] for c in mem_cache[wk] if D in self.fday[c] and self.fcnt[c].get(D, 0) >= 20]
            if vals:
                out[D] = statistics.fmean(vals)
                n_used[D] = len(vals)
        self._basket_fday, self._basket_n = out, n_used
        return out


# ------------------------------------------------------------------------------------------------ the event trade

def listing_trade(W, coin, te, H, hedge, costs):
    """Short `coin` at te (a day boundary) for H days, long the same notional of the hedge. Returns the components and
    the P&L as a fraction of one leg's notional, or None if a price is missing.

    The coin leg: -(P1/P0 - 1) + funding received (weighted by the coin's price path; a missing day is charged at the
    interest-only floor and counted). Delisted inside the window: closed at its last close. The hedge leg: +return
    - funding paid (BTC from its own rows; the basket from `basket_fday`)."""
    d = W.daily[coin]
    p0 = d.at(te)
    if not p0:
        return None
    tx = te + H * DAY_MS
    last = W.calendar[coin]['last_live_ms']
    end = tx
    if last is not None and last < tx:
        end = ceil_day(last) if ceil_day(last) <= tx else tx
    if end > W.data_end:
        return None
    p1 = d.at(end, max_age=3 * DAY_MS)
    if not p1:
        return None
    f_coin, have, n = weighted_funding(W.fday[coin], d, te, end)
    missing = n - have
    f_coin = (f_coin or 0.0) + missing * FLOOR_RATE_DAY
    if hedge == 'btc':
        b = W.daily['BTC']
        b0, b1 = b.at(te), b.at(end)
        if not (b0 and b1):
            return None
        r_h = b1 / b0 - 1.0
        f_h, hh, hn = weighted_funding(W.fday['BTC'], b, te, end)
        f_h = (f_h or 0.0) + (hn - hh) * FLOOR_RATE_DAY
        n_mem = 1
        cost_h = costs['btc_rt']
    else:
        r_h, n_mem = W.basket_return(te, end, exclude=(coin,))
        if r_h is None or n_mem < 10:
            return None
        bf = W.basket_fday()
        f_h = sum(bf.get(D, FLOOR_RATE_DAY) for D in range(int(te), int(end), DAY_MS))
        cost_h = costs['basket_rt']
    r_c = p1 / p0 - 1.0
    hi = d.max_high(te, end)
    mae = (hi / p0 - 1.0) if hi else None
    cost_c = costs['coin_rt'](coin)
    pnl = -r_c + f_coin + r_h - f_h - cost_c - cost_h
    return {'coin': coin, 'te': te, 'tx': end, 'days': (end - te) / DAY_MS, 'coin_return': r_c, 'hedge_return': r_h,
            'funding_short_received': f_coin, 'funding_hedge_paid': f_h, 'funding_days_missing': missing,
            'cost': cost_c + cost_h, 'excess_vs_hedge': -(r_c - r_h), 'pnl': pnl, 'basket_members': n_mem,
            'closed_early': end < tx, 'max_adverse': mae}


def week_of(t):
    return int(t // (7 * DAY_MS))


def by_group_means(pairs, key=week_of):
    """Mean of the values sharing a group (default: the listing's week since epoch), one per group, in group order."""
    g = {}
    for t, v in pairs:
        g.setdefault(key(t), []).append(v)
    return [statistics.fmean(v) for _, v in sorted(g.items())]


def tstat(x):
    if len(x) < 3:
        return None
    sd = statistics.stdev(x)
    return (statistics.fmean(x) / (sd / math.sqrt(len(x)))) if sd > 0 else None


def pvalue(t):
    if t is None:
        return None
    return 2.0 * (1.0 - statistics.NormalDist().cdf(abs(t)))


def summarize(rows, key='pnl'):
    """n, mean, median, hit rate, plain t and listing-week t of `key` over trade rows carrying their listing time 'L'."""
    x = [r[key] for r in rows if r.get(key) is not None]
    if not x:
        return {'n': 0}
    wk = by_group_means([(r['L'], r[key]) for r in rows if r.get(key) is not None])
    return {'n': len(x), 'mean': statistics.fmean(x), 'median': statistics.median(x),
            'hit': sum(1 for v in x if v > 0) / len(x), 't': tstat(x), 'weeks': len(wk), 't_week': tstat(wk)}


# ------------------------------------------------------------------------------------------------ books and costs

def walk_book(levels, usd):
    """Market order of `usd` through [(px, size)] best first: (VWAP, filled usd)."""
    cum_usd = cum_qty = 0.0
    for px, sz in levels:
        take = min(px * sz, usd - cum_usd)
        if take <= 0:
            break
        cum_usd += take
        cum_qty += take / px
        if cum_usd >= usd - 1e-9:
            break
    return (cum_usd / cum_qty if cum_qty else None), cum_usd


def slip_bp(levels, mid, usd):
    """Distance of a market order's VWAP from mid in bp (half-spread included); None if the shown book is too thin."""
    if not levels or not mid or usd <= 0:
        return None
    vwap, filled = walk_book(levels, usd)
    if vwap is None or filled < usd * (1 - 1e-6):
        return None
    return abs(vwap / mid - 1.0) * 1e4


def book_from_l2(reply):
    """(mid, bids, asks) from a Hyperliquid l2Book reply; None for an empty side."""
    if not isinstance(reply, dict) or not reply.get('levels'):
        return None
    bids = [(float(x['px']), float(x['sz'])) for x in reply['levels'][0]]
    asks = [(float(x['px']), float(x['sz'])) for x in reply['levels'][1]]
    if not bids or not asks:
        return None
    return (bids[0][0] + asks[0][0]) / 2, bids, asks


def side_slip(fine, coarse, side, usd):
    """Slippage of one side at `usd` from the true (20-level) mid: the 20-level book where it reaches, else the
    4-significant-figure aggregation (bucket prices are no better than the orders in them, so that is an upper
    bound); None if neither reaches."""
    mid = fine[0] if fine else (coarse[0] if coarse else None)
    for b in (fine, coarse):
        if b:
            v = slip_bp(b[1] if side == 'bid' else b[2], mid, usd)
            if v is not None:
                return v
    return None


def round_trip_bp(fine, coarse, usd, fee_bp=FEE_BP['hl'], extrapolate=True):
    """Sell `usd` into the bids and buy it back from the asks (or the reverse): two fees plus both sides' slippage.
    Beyond what the shown book holds, the slippage at the largest fillable size is scaled up linearly with size (a
    linear-impact extrapolation, flagged by the caller as such); None only for an empty book."""
    out = 2 * fee_bp
    for side in ('bid', 'ask'):
        v = side_slip(fine, coarse, side, usd)
        if v is None:
            if not extrapolate:
                return None
            lo, hi = 0.0, usd
            for _ in range(30):
                m = (lo + hi) / 2
                if side_slip(fine, coarse, side, m) is not None:
                    lo = m
                else:
                    hi = m
            if lo < 100:
                return None
            v = side_slip(fine, coarse, side, lo) * usd / lo
        out += v
    return out


def fillable(fine, coarse, usd):
    return side_slip(fine, coarse, 'bid', usd) is not None and side_slip(fine, coarse, 'ask', usd) is not None


def depth_usd(levels, mid, bp):
    return sum(px * sz for px, sz in levels if abs(px / mid - 1) * 1e4 <= bp + 1e-9)


def load_books(out):
    """{coin: (fine, coarse, source)} from the fresh books this study read (newest listings) and, for every other live
    coin, the funding study's snapshot of the same morning (research/2026-10-09/funding_arb/snapshot.json)."""
    books = {}
    snap = load_json(FUNDING_STUDY / 'snapshot.json', {}) or {}
    for c, b in ((snap.get('hl') or {}).get('books') or {}).items():
        fine = (b['mid'], [tuple(x) for x in b['bids']], [tuple(x) for x in b['asks']])
        coarse = (b['mid'], [tuple(x) for x in b.get('bids_coarse') or []], [tuple(x) for x in b.get('asks_coarse') or []])
        books[c] = (fine, coarse if coarse[1] and coarse[2] else None, 'funding_arb snapshot ' + snap['hl']['at'],
                    b.get('oi_usd'), b.get('vol24_usd'))
    fresh = load_json(Path(out) / 'raw' / 'hl' / 'books_recent.json', {}) or {}
    for c, b in (fresh.get('books') or {}).items():
        if 'error' in b:
            continue
        fine, coarse = book_from_l2(b.get('fine')), book_from_l2(b.get('coarse'))
        if fine:
            prev = books.get(c)
            books[c] = (fine, coarse, 'fresh ' + b['at'], prev[3] if prev else None, prev[4] if prev else None)
    return books


def build_costs(W, books, usd):
    """The cost model of part (a) at `usd` a leg: each coin's own live round trip where it has a book, else the median
    of the live coins in its listing year (delisted coins have no book: said so in the output); BTC's own; the basket
    as two fees plus the members' median round-trip spread (each member is a ~1% sliver, so impact is nil)."""
    rt = {}
    for c, b in books.items():
        v = round_trip_bp(b[0], b[1], usd)
        if v is not None:
            rt[c] = v
    by_year = {}
    for c, v in rt.items():
        r = W.calendar.get(c)
        if r:
            by_year.setdefault(iso(r['listing_ms'])[:4], []).append(v)
    med_year = {y: statistics.median(v) for y, v in by_year.items()}
    med_all = statistics.median(rt.values()) if rt else 30.0
    spreads = [(b[0][2][0][0] - b[0][1][0][0]) / b[0][0] * 1e4 for c, b in books.items()
               if c not in NOT_ALTS and ':' not in c and b[0][1] and b[0][2]]
    basket_rt = 2 * FEE_BP['hl'] + (statistics.median(spreads) if spreads else 4.0)
    imputed = set()

    def coin_rt(c):
        if c in rt:
            return rt[c] / 1e4
        imputed.add(c)
        y = iso(W.calendar[c]['listing_ms'])[:4] if c in W.calendar else None
        return med_year.get(y, med_all) / 1e4

    return {'coin_rt': coin_rt, 'btc_rt': (rt.get('BTC') or 9.1) / 1e4, 'basket_rt': basket_rt / 1e4,
            'usd': usd, 'per_coin_bp': rt, 'median_by_listing_year_bp': med_year, 'median_bp': med_all,
            'imputed': imputed}


# ------------------------------------------------------------------------------------------------ part (a) analysis

D_GRID = (1, 3, 7)
H_GRID = (7, 14, 30, 60)
HEDGES = ('btc', 'basket')
PLACEBO_DAYS = 90


def listing_events(W):
    """The listings part (a) studies: every core listing since STUDY_START except migrations, oldest first."""
    s0 = ms_of(STUDY_START)
    ev = [r for r in W.calendar.values() if r['listing_ms'] >= s0 and r['cohort'] != 'migration'
          and r['coin'] not in NOT_ALTS]
    return sorted(ev, key=lambda r: r['listing_ms'])


def entry_time(listing_day_ms, d, offset_days=0):
    """Entry for "listing + d days": the daily close that ends UTC day d+1, counting the listing day as day 1. The
    listing hour is known only where the store's funding shows it (29 listings), so every listing is treated alike and
    entry falls between d and d+1 days after the first trade."""
    return listing_day_ms + (offset_days + d + 1) * DAY_MS


def run_variant(W, events, d, H, hedge, costs, offset_days=0):
    rows = []
    for e in events:
        te = entry_time(e['listing_ms'], d, offset_days)
        tr = listing_trade(W, e['coin'], te, H, hedge, costs)
        if tr:
            tr['L'] = e['listing_ms']
            tr['cohort'] = e['cohort']
            rows.append(tr)
    return rows


def squeeze_stats(rows):
    """How far against a short the coin went while held (daily highs over entry): the margin a short must post to
    stay in the trade, which is what sizes it, not the round trip."""
    m = [r['max_adverse'] for r in rows if r.get('max_adverse') is not None]
    if not m:
        return None
    m.sort()
    return {'n': len(m), 'share_over_25pct': sum(1 for v in m if v > 0.25) / len(m),
            'share_over_50pct': sum(1 for v in m if v > 0.5) / len(m),
            'share_over_100pct': sum(1 for v in m if v > 1.0) / len(m), 'p90': m[int(0.9 * (len(m) - 1))],
            'max': m[-1], 'share_pnl_below_minus_50pct': sum(1 for r in rows if r['pnl'] < -0.5) / len(rows)}


def paired(trades, placebo):
    """Per coin: the trade's P&L minus its own placebo's, keyed by listing time."""
    pm = {r['coin']: r['pnl'] for r in placebo}
    return [{'coin': r['coin'], 'L': r['L'], 'diff': r['pnl'] - pm[r['coin']]} for r in trades if r['coin'] in pm]


def components(rows):
    if not rows:
        return None
    keys = ('coin_return', 'hedge_return', 'excess_vs_hedge', 'funding_short_received', 'funding_hedge_paid', 'cost',
            'pnl')
    return {k: statistics.fmean(r[k] for r in rows) for k in keys}


def cohort_flags(W, e, te, em):
    """Extra cohort labels for one listing: Binance perp live at entry, airdrop allocation in DefiLlama's schedule,
    and the fully diluted value at listing where DefiLlama has a max supply."""
    c = W.cex.get(hl_core_name(e['coin']).upper()) or {}
    bn = c.get('binance')
    row = em.get(hl_core_name(e['coin']).upper())
    airdrop = None
    fdv = None
    if row:
        px_now = ((row.get('tokenPrice') or [{}])[0]).get('price')
        hl_now = W.daily[e['coin']].at(W.daily[e['coin']].last() or 0) if W.daily[e['coin']].keys else None
        scale = 1000.0 if e['coin'].startswith('k') and e['coin'][1:2].isupper() else 1.0
        ok = (px_now and hl_now and abs((hl_now / scale) / px_now - 1) < 0.5) or e['delisted']
        if ok:
            airdrop = any((ev.get('category') == 'airdrop') for ev in (row.get('events') or []))
            p0 = W.daily[e['coin']].at(e['listing_ms'] + DAY_MS)
            if p0 and row.get('maxSupply'):
                fdv = p0 / scale * float(row['maxSupply'])
    return {'binance_at_entry': bool(bn and bn <= te), 'airdrop': airdrop, 'fdv_at_listing': fdv}


def decay_curve(W, events, days=90):
    """Mean cumulative return of the new coin over the seasoned basket (and BTC), and the cumulative funding a short
    received, by day since listing (entry at the first day boundary after listing)."""
    curve = {k: {'excess_basket': [], 'excess_btc': [], 'funding': []} for k in (1, 3, 7, 14, 30, 45, 60, 90)}
    b = W.daily['BTC']
    for e in events:
        t0 = e['listing_ms'] + DAY_MS            # the first daily close
        d = W.daily[e['coin']]
        p0, b0 = d.at(t0), b.at(t0)
        if not (p0 and b0):
            continue
        for k in curve:
            t1 = t0 + k * DAY_MS
            if t1 > W.data_end:
                continue
            last = W.calendar[e['coin']]['last_live_ms']
            if last is not None and last < t1:
                continue
            p1, b1 = d.at(t1), b.at(t1)
            if not (p1 and b1):
                continue
            rb, n = W.basket_return(t0, t1, exclude=(e['coin'],))
            f, have, nd = weighted_funding(W.fday[e['coin']], d, t0, t1)
            curve[k]['excess_btc'].append((p1 / p0) - (b1 / b0))
            if rb is not None:
                curve[k]['excess_basket'].append((p1 / p0 - 1) - rb)
            if f is not None and have >= 0.8 * nd:
                curve[k]['funding'].append(f)
    out = {}
    for k, v in curve.items():
        out[k] = {key: ({'n': len(x), 'mean': statistics.fmean(x), 'median': statistics.median(x)} if x else {'n': 0})
                  for key, x in v.items()}
    return out


def analyze_listings(W, books, usd=25_000, min_in=15):
    costs = build_costs(W, books, usd)
    events = listing_events(W)
    usable = [e for e in events if entry_time(e['listing_ms'], 1) + 7 * DAY_MS <= W.data_end]
    cutoff = statistics.median([e['listing_ms'] for e in usable])
    em = emissions_match((load_json(UNLOCKS / 'raw' / 'emissions_index.json', {}) or {}).get('data'))
    flags = {e['coin']: cohort_flags(W, e, entry_time(e['listing_ms'], 1), em) for e in events}
    variants = []
    store = {}
    for d in D_GRID:
        for H in H_GRID:
            for hedge in HEDGES:
                tr = run_variant(W, events, d, H, hedge, costs)
                pl = run_variant(W, events, d, H, hedge, costs, offset_days=PLACEBO_DAYS)
                ins = [r for r in tr if r['L'] < cutoff]
                oos = [r for r in tr if r['L'] >= cutoff]
                pins = [r for r in pl if r['L'] < cutoff]
                poos = [r for r in pl if r['L'] >= cutoff]
                pr = paired(tr, pl)
                v = {'d': d, 'H': H, 'hedge': hedge, 'name': 'd%d_H%d_%s' % (d, H, hedge),
                     'in': summarize(ins), 'out': summarize(oos),
                     'placebo_in': summarize(pins), 'placebo_out': summarize(poos),
                     'paired_in': summarize([r for r in pr if r['L'] < cutoff], 'diff'),
                     'paired_out': summarize([r for r in pr if r['L'] >= cutoff], 'diff'),
                     'components_in': components(ins), 'components_out': components(oos),
                     'placebo_components_out': components(poos), 'squeeze_out': squeeze_stats(oos),
                     'per_year_out': (v_mean * 365.0 / H) if (v_mean := (summarize(oos).get('mean'))) is not None else None}
                variants.append(v)
                store[v['name']] = (tr, pl)
    elig = [v for v in variants if v['in'].get('n', 0) >= min_in and v['in'].get('t_week') is not None]
    chosen = max(elig, key=lambda v: v['in']['t_week']) if elig else None
    pv = [pvalue(v['in'].get('t_week')) for v in variants]
    rej, adj = B.bh(pv, q=0.10)
    for v, r, a in zip(variants, rej, adj):
        v['bh_in_reject'], v['bh_in_adj_p'] = r, a
    res = {'usd_per_leg': usd, 'events': len(events), 'usable': len(usable), 'cutoff_ms': cutoff,
           'cutoff_utc': iso(cutoff), 'variants': variants, 'n_variants': len(variants),
           'chosen': chosen and chosen['name'], 'cost_model': {
               'coin_rt_median_bp': costs['median_bp'], 'by_listing_year_bp': costs['median_by_listing_year_bp'],
               'btc_rt_bp': costs['btc_rt'] * 1e4, 'basket_rt_bp': costs['basket_rt'] * 1e4,
               'coins_priced_from_own_book': sum(1 for e in events if e['coin'] in costs['per_coin_bp']),
               'coins_imputed': sum(1 for e in events if e['coin'] not in costs['per_coin_bp'])}}
    if chosen:
        tr, pl = store[chosen['name']]
        ins = [r for r in tr if r['L'] < cutoff]
        wk_in = by_group_means([(r['L'], r['pnl']) for r in ins])
        in_srs = []
        for v in variants:
            t_, _ = store[v['name']]
            w = by_group_means([(r['L'], r['pnl']) for r in t_ if r['L'] < cutoff])
            if len(w) > 2 and statistics.pstdev(w) > 0:
                in_srs.append(statistics.fmean(w) / statistics.pstdev(w))
        res['deflated_sharpe_in_sample'] = B.deflated_sharpe(wk_in, len(variants),
                                                             statistics.pstdev(in_srs) if len(in_srs) > 1 else None)
        oos = [r for r in tr if r['L'] >= cutoff]
        res['chosen_oos_rank'] = 1 + sum(1 for v in variants if (v['out'].get('t_week') or -9) > (chosen['out'].get('t_week') or -9))
        res['chosen_cohorts'] = cohort_table(tr, flags, cutoff)
        res['chosen_trades_oos'] = [{k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()
                                     if k in ('coin', 'L', 'te', 'tx', 'cohort', 'coin_return', 'hedge_return',
                                              'funding_short_received', 'funding_hedge_paid', 'cost', 'pnl',
                                              'closed_early', 'max_adverse', 'funding_days_missing')} for r in oos]
        res['chosen_by_quarter'] = quarter_table(tr, pl)
    # the same table with BTC and basket side by side for the decision-relevant variants
    res['decay_curve'] = decay_curve(W, events)
    res['decay_curve_by_cohort'] = {c: decay_curve(W, [e for e in events if e['cohort'] == c])
                                    for c in ('new_token', 'prelaunch', 'established', 'hl_only')}
    res['calendar_counts'] = calendar_counts(W, events)
    res['flags'] = flags
    res['_store'] = store
    res['_costs'] = costs
    return res


def cohort_table(trades, flags, cutoff):
    out = {}
    groups = {
        'cohort': lambda r: r['cohort'],
        'binance_at_entry': lambda r: flags[r['coin']]['binance_at_entry'],
        'airdrop': lambda r: flags[r['coin']]['airdrop'],
        'fdv_at_listing': lambda r: (None if flags[r['coin']]['fdv_at_listing'] is None else
                                     ('<$500M' if flags[r['coin']]['fdv_at_listing'] < 5e8 else
                                      ('$500M-3B' if flags[r['coin']]['fdv_at_listing'] < 3e9 else '>$3B'))),
    }
    for gname, fn in groups.items():
        g = {}
        for r in trades:
            g.setdefault(str(fn(r)), []).append(r)
        out[gname] = {k: {'all': summarize(v), 'out': summarize([r for r in v if r['L'] >= cutoff]),
                          'components': components(v)} for k, v in sorted(g.items())}
    return out


def quarter_table(trades, placebo):
    q = {}
    for r in trades:
        d = dt.datetime.fromtimestamp(r['L'] / 1000, UTC)
        q.setdefault('%dQ%d' % (d.year, (d.month - 1) // 3 + 1), {'t': [], 'p': []})['t'].append(r['pnl'])
    for r in placebo:
        d = dt.datetime.fromtimestamp(r['L'] / 1000, UTC)
        q.setdefault('%dQ%d' % (d.year, (d.month - 1) // 3 + 1), {'t': [], 'p': []})['p'].append(r['pnl'])
    return {k: {'n': len(v['t']), 'mean': statistics.fmean(v['t']) if v['t'] else None,
                'placebo_n': len(v['p']), 'placebo_mean': statistics.fmean(v['p']) if v['p'] else None}
            for k, v in sorted(q.items())}


def calendar_counts(W, events):
    by_q, by_c = {}, {}
    for e in events:
        d = dt.datetime.fromtimestamp(e['listing_ms'] / 1000, UTC)
        k = '%dQ%d' % (d.year, (d.month - 1) // 3 + 1)
        by_q[k] = by_q.get(k, 0) + 1
        by_c[e['cohort']] = by_c.get(e['cohort'], 0) + 1
    return {'by_quarter': dict(sorted(by_q.items())), 'by_cohort': by_c,
            'delisted_since_study_start': sum(1 for e in events if e['delisted']),
            'with_listing_hour': sum(1 for e in events if e['listing_hour_ms'] is not None),
            'zero_volume_lead_days_over_1': sum(1 for e in events if (e['zero_volume_lead_days'] or 0) > 1)}


# ================================================================================================ part (b): delistings

class Hourly:
    """An hourly series keyed by bar end (ms): close and quote volume, from [[open_ms, o, h, l, c, quote_vol]] rows."""

    def __init__(self, rows):
        self.close, self.vol = {}, {}
        for r in rows or []:
            t = int(r[0]) + HOUR_MS
            self.close[t] = float(r[4])
            self.vol[t] = float(r[5] or 0.0)
        self.keys = sorted(self.close)

    def at(self, t, max_age=3 * HOUR_MS):
        i = bisect.bisect_right(self.keys, t) - 1
        if i < 0 or t - self.keys[i] > max_age:
            return None
        return self.close[self.keys[i]]

    def vol_between(self, t0, t1):
        i, j = bisect.bisect_right(self.keys, t0), bisect.bisect_right(self.keys, t1)
        return sum(self.vol[k] for k in self.keys[i:j])

    def last(self):
        return self.keys[-1] if self.keys else None


def hl_hourly(coin):
    """Hyperliquid hourly closes for `coin` (the store's, else the funding study's delisted extras), with 4h bars
    filling the months before the 1h ones; volume in USD."""
    rows = []
    for p in (HL_EXTRA / 'candles_4h' / (safe(coin) + '.json.gz'),):
        if p.exists():
            rows += [[int(c['t']) + 3 * HOUR_MS, 0, 0, 0, float(c['c']), float(c['v']) * float(c['c'])]
                     for c in read_gz(p) if traded(c)]
    for p in (STORE / 'candles_1h' / (safe(coin) + '.json.gz'), HL_EXTRA / 'candles_1h' / (safe(coin) + '.json.gz')):
        if p.exists():
            rows += [[int(c['t']), 0, 0, 0, float(c['c']), float(c['v']) * float(c['c'])] for c in read_gz(p)
                     if traded(c)]
            break
    return Hourly(rows)


def settlements_between(rows, t0, t1):
    """Sum of settlement rates with t0 < t <= t1 from [(t_ms, rate)] (any venue, any interval)."""
    return sum(r for t, r in rows if t0 < t <= t1)


def bn_series(raw, sym):
    """Binance perp klines, premium-index klines, funding settlements, spot klines and 5-minute open interest for one
    delisted symbol (empty where the archive has nothing)."""
    def g(kind):
        p = Path(raw) / kind / (sym + '.json.gz')
        return read_gz(p) if p.exists() else []
    fund = [(int(r['t']), float(r['rate'])) for r in g('funding')]
    return {'perp': Hourly(g('klines')), 'premium': Hourly(g('premium')), 'funding': sorted(fund),
            'spot': Hourly(g('spot_klines')), 'oi': sorted((int(r[0]), float(r[2])) for r in g('metrics'))}


def binance_events(out):
    """One row per delisted USD-M perpetual: announcement (the notice's release time), settlement (exchangeInfo's
    deliveryDate, cross-checked with the notice), reduce-only time, notice hours, and the notice it came from. Symbols
    that settled without a notice found in the CMS list are kept with announce_ms None."""
    raw = Path(out) / 'raw' / 'binance'
    notes = (load_json(raw / 'delisting_notices.json', {}) or {}).get('events') or []
    ei = load_json(raw / 'exchangeInfo.json', {}) or {}
    syms = ei.get('symbols') or []
    delivery = {s_['symbol']: s_.get('deliveryDate') for s_ in syms if s_.get('status') != 'TRADING'}
    base = {s_['symbol']: s_.get('baseAsset') for s_ in syms}
    ev = {}
    for n in notes:
        targets = [n['symbol']] if n.get('symbol') else resolve_tokens(n.get('tokens') or [], syms)
        for sy in targets:
            settle = delivery.get(sy) or n.get('settle_ms')
            if not settle or not (n['announced_ms'] < settle <= n['announced_ms'] + 30 * DAY_MS):
                continue
            cur = ev.get(sy)
            if cur is None or n['announced_ms'] < cur['announce_ms']:
                ev[sy] = {'symbol': sy, 'base': base.get(sy), 'announce_ms': n['announced_ms'], 'settle_ms': settle,
                          'settle_from_notice_ms': n.get('settle_ms'), 'reduce_only_ms': n.get('reduce_only_ms'),
                          'article': n['article'], 'title': n['title']}
    # The first notice is the information event; a later notice can move the settlement (FLM and PERP: first notice
    # 2025-10-29 said 11-04, they settled 11-21). Trades exit before the earlier of the first stated settlement and the
    # actual one, which is what a trader holding from the first notice would have planned.
    for e in ev.values():
        stated = e.get('settle_from_notice_ms')
        e['settle_moved'] = bool(stated and abs(stated - e['settle_ms']) > HOUR_MS)
        e['exit_ms'] = min(stated, e['settle_ms']) if stated else e['settle_ms']
    since = min((e['announce_ms'] for e in ev.values()), default=0)
    for sy, d in delivery.items():
        if d and since <= d <= int(time.time() * 1000) and sy not in ev:
            ev[sy] = {'symbol': sy, 'base': base.get(sy), 'announce_ms': None, 'settle_ms': d, 'article': None,
                      'title': None, 'settle_from_notice_ms': None, 'reduce_only_ms': None, 'settle_moved': False,
                      'exit_ms': d}
    for e in ev.values():
        e['notice_hours'] = (e['settle_ms'] - e['announce_ms']) / HOUR_MS if e['announce_ms'] else None
        e['core'] = re.sub(r'^(1000000|10000|1000|1M)(?=[A-Z])', '', e['base'] or '').upper()
        e['unit'] = (1_000_000 if (e['base'] or '').startswith('1000000') else 1000 if (e['base'] or '').startswith('1000') else 1)
    return sorted(ev.values(), key=lambda e: e['settle_ms'])


def hl_coin_for(W, core):
    """The Hyperliquid core perp of the same underlying, or None (k-prefixed thousand-unit tickers included)."""
    for c in (core, 'k' + core):
        if c in W.calendar:
            return c
    return None


class BnBasket:
    """Hourly equal-weight basket of seasoned alts from the Binance 1h klines the funding study holds (every HL-mapped
    USDT perpetual since 2025-09-25): members are perps listed on Binance more than 180 days before the window starts,
    BTC and ETH excluded. Used to hedge part (b), whose events sit between 2025-09 and 2026-10."""

    def __init__(self):
        raw = FUNDING_STUDY / 'raw'
        ei = load_json(raw / 'bn_exchangeInfo.json', {}) or {}
        onboard = {s_['symbol']: s_.get('onboardDate') for s_ in ei.get('symbols', [])}
        self.series, self.onboard = {}, {}
        for p in sorted((raw / 'binance' / 'klines').glob('*.json.gz')):
            sym = p.name[:-8]
            if sym in ('BTCUSDT', 'ETHUSDT') or not sym.endswith('USDT'):
                continue
            self.series[sym] = Hourly(read_gz(p))
            self.onboard[sym] = onboard.get(sym)
        btc = raw / 'binance' / 'klines' / 'BTCUSDT.json.gz'
        self.btc = Hourly(read_gz(btc)) if btc.exists() else None

    def ret(self, t0, t1, exclude=()):
        rs = []
        for sym, h in self.series.items():
            if sym in exclude or not self.onboard.get(sym) or self.onboard[sym] > t0 - 180 * DAY_MS:
                continue
            a, b = h.at(t0), h.at(t1)
            if a and b:
                rs.append(b / a - 1.0)
        return (statistics.fmean(rs) if rs else None), len(rs)


def infer_hl_announcement(vol_series, last_ms, lookback_days=7, base_days=14, mult=8.0):
    """The first hour in the `lookback_days` before a Hyperliquid delisting whose trailing-4h volume exceeds `mult`
    times the median 4h volume of the `base_days` before that: Hyperliquid's notice is not in its API, and a notice
    shows up as a burst of closing trades. None if no such burst (then the notice is assumed to be 24h)."""
    h = vol_series
    base = []
    for t in range(last_ms - (lookback_days + base_days) * DAY_MS, last_ms - lookback_days * DAY_MS, 4 * HOUR_MS):
        base.append(h.vol_between(t - 4 * HOUR_MS, t))
    med = statistics.median(base) if base else 0.0
    if med <= 0:
        med = max(1.0, statistics.fmean(base) if base else 1.0)
    for t in range(last_ms - lookback_days * DAY_MS, last_ms + HOUR_MS, HOUR_MS):
        if h.vol_between(t - 4 * HOUR_MS, t) > mult * med:
            return t
    return None


def bn_cost_bp(usd, vol24_usd, fee_bp, half_spread_bp, depth_per_vol):
    """Round trip (two fills) at `usd` in a book whose depth within 1% is `depth_per_vol` times its 24h volume
    (calibrated on the live books): two fees, the half-spread twice, and linear impact to the 1% band."""
    depth = max(1.0, depth_per_vol * max(vol24_usd, 1.0))
    impact = 100.0 * min(1.0, usd / depth) / 2 + (100.0 * max(0.0, usd / depth - 1.0))
    return 2 * fee_bp + 2 * half_spread_bp + 2 * impact


def calibrate_depth(snapshot_books, band_bp=100):
    """Median ratio of (bid+ask)/2 depth within `band_bp` of mid to 24h volume across a venue's live books, and the
    median half-spread, for coins with under $20M of daily volume (the delisting candidates' size)."""
    ratios, hs = [], []
    for b in snapshot_books.values():
        v = b.get('vol24_usd') or 0
        if not v or v > 20e6 or not b.get('bids') or not b.get('asks'):
            continue
        mid = b['mid']
        d = (depth_usd([tuple(x) for x in b['bids']], mid, band_bp) +
             depth_usd([tuple(x) for x in b['asks']], mid, band_bp)) / 2
        ratios.append(d / v)
        hs.append(b['half_spread_bp'])
    return {'depth_per_vol': statistics.median(ratios) if ratios else 0.02, 'half_spread_bp': statistics.median(hs) if hs else 10.0,
            'n': len(ratios)}


DELAYS_H = (2, 8, 24)
SIZES = (10_000, 50_000, 100_000)
FLOOR_RATE_H = 1.25e-5                 # interest-only funding an hour on both venues (0.01% per 8h on Binance)


def trailing_rate(rows, t, hours=8):
    """Mean funding per hour over the `hours` before t from settlement rows [(t_ms, rate)] (any interval)."""
    return settlements_between(rows, t - hours * HOUR_MS, t) / hours


def bn_event_path(e, S, basket):
    """Event-time readings of one Binance delisting: funding (annualised, per hour of settlements), premium index,
    price against BTC and the seasoned basket, volume and open interest, around announcement A and settlement T."""
    A, T = e['announce_ms'], e['settle_ms']
    perp, prem = S['perp'], S['premium']
    out = {}
    if A:
        ann = 8760.0
        out['funding_ann_7d_before_A'] = settlements_between(S['funding'], A - 7 * DAY_MS, A) / (7 * 24) * ann
        out['funding_ann_A_to_T'] = (settlements_between(S['funding'], A, T) / max(1.0, (T - A) / HOUR_MS)) * ann
        out['funding_ann_last_24h'] = settlements_between(S['funding'], T - DAY_MS, T) / 24 * ann
        out['funding_max_settlement'] = max((r for t, r in S['funding'] if A < t <= T), default=None)
        out['funding_min_settlement'] = min((r for t, r in S['funding'] if A < t <= T), default=None)
        for k, t in (('premium_A_minus_24h', A - DAY_MS), ('premium_A_plus_2h', A + 2 * HOUR_MS),
                     ('premium_T_minus_24h', T - DAY_MS), ('premium_T_minus_2h', T - 2 * HOUR_MS),
                     ('premium_T', T)):
            out[k] = prem.at(t)
        for k, (t0, t1) in (('ret_A-7d_A', (A - 7 * DAY_MS, A)), ('ret_A-24h_A', (A - DAY_MS, A)),
                            ('ret_A_A+2h', (A, A + 2 * HOUR_MS)), ('ret_A+2h_T', (A + 2 * HOUR_MS, T - HOUR_MS)),
                            ('ret_A+24h_T', (A + DAY_MS, T - HOUR_MS))):
            p0, p1 = perp.at(t0), perp.at(t1)
            b, n = basket.ret(t0, t1, exclude=(e['symbol'],))
            out[k] = None if not (p0 and p1) else p1 / p0 - 1.0
            out[k + '_vs_basket'] = None if (out[k] is None or b is None) else out[k] - b
        out['vol24_before_A'] = perp.vol_between(A - DAY_MS, A)
        out['vol24_after_A'] = perp.vol_between(A, A + DAY_MS)
        out['vol_last_24h'] = perp.vol_between(T - DAY_MS, T)
        oi = S['oi']
        def oi_at(t):
            i = bisect.bisect_right([x[0] for x in oi], t) - 1
            return oi[i][1] if i >= 0 and t - oi[i][0] < 2 * HOUR_MS else None
        out['oi_usd_A'], out['oi_usd_A+24h'], out['oi_usd_T-2h'] = oi_at(A), oi_at(A + DAY_MS), oi_at(T - 2 * HOUR_MS)
        sp = S['spot']
        out['spot_trades_through_T'] = bool(sp.at(T + HOUR_MS, max_age=2 * HOUR_MS))
        if sp.at(T) and perp.at(T):
            out['perp_vs_spot_at_T'] = perp.at(T) / sp.at(T) - 1.0
        if sp.at(T + 7 * DAY_MS, max_age=DAY_MS) and sp.at(T):
            out['spot_ret_T_T+7d'] = sp.at(T + 7 * DAY_MS, max_age=DAY_MS) / sp.at(T) - 1.0
    return out


def drift_trade(price, funding_rows, basket_ret, te, tx, cost_coin, cost_basket, unit=1.0):
    """Short the coin from te to tx, long the same notional of the seasoned basket. Funding: the short receives the
    coin's settlements in (te, tx]; the basket pays the interest-only floor. None if a price is missing."""
    p0, p1 = price.at(te), price.at(tx)
    if not (p0 and p1) or basket_ret is None:
        return None
    hours = (tx - te) / HOUR_MS
    f = settlements_between(funding_rows, te, tx)
    pnl = -(p1 / p0 - 1.0) + basket_ret + f - FLOOR_RATE_H * hours - cost_coin - cost_basket
    return {'coin_return': p1 / p0 - 1.0, 'basket_return': basket_ret, 'funding_short_received': f,
            'hours': hours, 'cost': cost_coin + cost_basket, 'pnl': pnl}


def pair_trade(short_px, short_fund, long_px, long_fund, te, tx, cost):
    """Short one venue's perp, long the other venue's (or spot, with no funding rows): funding received on the short
    minus funding paid on the long, plus the relative price move, minus `cost`."""
    a0, a1, b0, b1 = short_px.at(te), short_px.at(tx), long_px.at(te), long_px.at(tx)
    if None in (a0, a1, b0, b1):
        return None
    f = settlements_between(short_fund, te, tx) - settlements_between(long_fund, te, tx)
    basis = (b1 / b0 - 1.0) - (a1 / a0 - 1.0)
    return {'funding': f, 'basis': basis, 'hours': (tx - te) / HOUR_MS, 'cost': cost, 'pnl': f + basis - cost,
            'gross': f + basis}


def hl_rows_ms(W, coin):
    return [(h, r) for h, r, _ in W.frows.get(coin) or []]


def analyze_delistings(W, out):
    out = Path(out)
    raw = out / 'raw' / 'binance'
    snap = load_json(FUNDING_STUDY / 'snapshot.json', {}) or {}
    cal_bn = calibrate_depth((snap.get('binance') or {}).get('books') or {})
    cal_hl = calibrate_depth((snap.get('hl') or {}).get('books') or {})
    basket = BnBasket()
    events = binance_events(out)
    res = {'calibration': {'binance': cal_bn, 'hyperliquid': cal_hl}, 'binance_events': [], 'hl_events': []}
    variants = {}
    for e in events:
        S = bn_series(raw, e['symbol'])
        hl = hl_coin_for(W, e['core'])
        hl_live = None
        if hl:
            r = W.calendar[hl]
            hl_live = (r['listing_ms'] <= (e['announce_ms'] or e['settle_ms']) - DAY_MS and
                       (r['last_live_ms'] is None or r['last_live_ms'] >= e['settle_ms']))
        row = dict(e, hl_coin=hl, hl_live_through_settlement=hl_live, has_klines=bool(S['perp'].keys),
                   has_spot=bool(S['spot'].keys), has_oi=bool(S['oi']))
        if e['announce_ms'] and S['perp'].keys:
            row['path'] = bn_event_path(e, S, basket)
            A, T = e['announce_ms'], e['exit_ms']
            for delay in DELAYS_H:
                te = (A + delay * HOUR_MS + HOUR_MS - 1) // HOUR_MS * HOUR_MS
                tx = T - HOUR_MS
                if tx - te < 4 * HOUR_MS:
                    continue
                v24 = S['perp'].vol_between(te - DAY_MS, te)
                b, n = basket.ret(te, tx, exclude=(e['symbol'],))
                for usd in (25_000,) + SIZES:
                    c_coin = bn_cost_bp(usd, v24, FEE_BP['binance'], cal_bn['half_spread_bp'], cal_bn['depth_per_vol']) / 1e4
                    c_bask = (2 * FEE_BP['binance'] + 2 * 2.0) / 1e4
                    tr = drift_trade(S['perp'], S['funding'], b, te, tx, c_coin, c_bask)
                    if tr:
                        pl_b, _ = basket.ret(te - 30 * DAY_MS, tx - 30 * DAY_MS, exclude=(e['symbol'],))
                        pl = drift_trade(S['perp'], S['funding'], pl_b, te - 30 * DAY_MS, tx - 30 * DAY_MS, c_coin, c_bask)
                        tr.update({'A': A, 'symbol': e['symbol'], 'usd': usd, 'vol24_usd': v24,
                                   'placebo_pnl': pl and pl['pnl']})
                        variants.setdefault(('bn_drift', delay, usd), []).append(tr)
                    # convergence: Binance perp against Hyperliquid's (both live), or against Binance spot
                    if hl and hl_live:
                        hp = hl_hourly(hl)
                        hf = hl_rows_ms(W, hl)
                        r_bn, r_hl = trailing_rate(S['funding'], te), trailing_rate(hf, te)
                        hv = hp.vol_between(te - DAY_MS, te)
                        cc = (bn_cost_bp(usd, v24, FEE_BP['binance'], cal_bn['half_spread_bp'], cal_bn['depth_per_vol']) +
                              bn_cost_bp(usd, hv, FEE_BP['hl'], cal_hl['half_spread_bp'], cal_hl['depth_per_vol'])) / 1e4
                        if r_bn >= r_hl:
                            ptr = pair_trade(S['perp'], S['funding'], hp, hf, te, tx, cc)
                            short = 'binance'
                        else:
                            ptr = pair_trade(hp, hf, S['perp'], S['funding'], te, tx, cc)
                            short = 'hyperliquid'
                        if ptr:
                            ptr.update({'A': A, 'symbol': e['symbol'], 'usd': usd, 'short': short,
                                        'spread_ann_at_entry': (r_bn - r_hl) * 8760})
                            variants.setdefault(('bn_vs_hl', delay, usd), []).append(ptr)
                    if S['spot'].keys and trailing_rate(S['funding'], te) > 0:
                        sv = S['spot'].vol_between(te - DAY_MS, te)
                        cc = (bn_cost_bp(usd, v24, FEE_BP['binance'], cal_bn['half_spread_bp'], cal_bn['depth_per_vol']) +
                              bn_cost_bp(usd, sv, FEE_BP['binance_spot'], cal_bn['half_spread_bp'], cal_bn['depth_per_vol'])) / 1e4
                        ptr = pair_trade(S['perp'], S['funding'], S['spot'], [], te, tx, cc)
                        if ptr:
                            ptr.update({'A': A, 'symbol': e['symbol'], 'usd': usd, 'short': 'binance_perp'})
                            variants.setdefault(('bn_vs_spot', delay, usd), []).append(ptr)
        res['binance_events'].append(row)
    # Hyperliquid's own delistings in the store's year
    store0 = ms_of(STORE_START)
    m = load_json(FUNDING_STUDY / 'mapping.json', {}) or {}
    for c, r in sorted(W.calendar.items(), key=lambda x: x[1]['last_live_ms'] or 0):
        if not r['delisted'] or not r['last_live_ms'] or r['last_live_ms'] < store0 + 14 * DAY_MS:
            continue
        last = r['last_live_ms']
        hp = hl_hourly(c)
        hf = hl_rows_ms(W, c)
        A = infer_hl_announcement(hp, last)
        row = {'coin': c, 'last_live_ms': last, 'last_live_utc': iso(last), 'announce_inferred_ms': A,
               'announce_inferred_utc': iso(A), 'notice_hours_inferred': (last - A) / HOUR_MS if A else None}
        mp = m.get(c) or {}
        cex = None
        for venue in ('binance', 'bybit'):
            sym = mp.get(venue)
            p = FUNDING_STUDY / 'raw' / venue / 'klines' / ('%s.json.gz' % sym) if sym else None
            if p and p.exists():
                fr = [(int(x['t']), float(x['rate'])) for x in read_gz(FUNDING_STUDY / 'raw' / venue / 'funding' / ('%s.json.gz' % sym))]
                cex = (venue, sym, Hourly(read_gz(p)), sorted(fr), mp.get(venue + '_mult') or 1)
                if cex[2].at(last):
                    break
        row['cex'] = cex and cex[:2]
        ann = 8760.0
        row['hl_funding_ann'] = {k: settlements_between(hf, last - d * DAY_MS, last) / (d * 24) * ann
                                 for k, d in (('last_30d', 30), ('last_7d', 7), ('last_24h', 1))}
        if cex:
            row['cex_funding_ann'] = {k: settlements_between(cex[3], last - d * DAY_MS, last) / (d * 24) * ann
                                      for k, d in (('last_30d', 30), ('last_7d', 7), ('last_24h', 1))}
            px_hl, px_cx = hp.at(last), cex[2].at(last)
            hl_mult = 1000.0 if c.startswith('k') and c[1:2].isupper() else 1.0
            if px_hl and px_cx:
                row['hl_last_vs_cex'] = (px_hl / hl_mult) / (px_cx / cex[4]) - 1.0
        b0, n0 = basket.ret(last - 7 * DAY_MS, last)
        p0, p1 = hp.at(last - 7 * DAY_MS), hp.at(last)
        row['ret_last_7d_vs_basket'] = (p1 / p0 - 1 - b0) if (p0 and p1 and b0 is not None) else None
        if cex and cex[2].at(last + 7 * DAY_MS) and cex[2].at(last):
            b1, _ = basket.ret(last, last + 7 * DAY_MS)
            row['cex_ret_after_7d_vs_basket'] = (cex[2].at(last + 7 * DAY_MS) / cex[2].at(last) - 1 - (b1 or 0))
        res['hl_events'].append(row)
        anchor = A or (last - DAY_MS)
        for delay in DELAYS_H:
            te = (anchor + delay * HOUR_MS) // HOUR_MS * HOUR_MS
            tx = last - HOUR_MS
            if tx - te < 4 * HOUR_MS:
                continue
            hv = hp.vol_between(te - DAY_MS, te)
            for usd in (25_000,) + SIZES:
                c_hl = bn_cost_bp(usd, hv, FEE_BP['hl'], cal_hl['half_spread_bp'], cal_hl['depth_per_vol']) / 1e4
                b, _ = basket.ret(te, tx)
                tr = drift_trade(hp, hf, b, te, tx, c_hl, (2 * FEE_BP['hl'] + 4.0) / 1e4)
                if tr:
                    tr.update({'A': anchor, 'symbol': c, 'usd': usd, 'announce_inferred': A is not None})
                    variants.setdefault(('hl_drift', delay, usd), []).append(tr)
                if cex and cex[2].at(tx):
                    cv = cex[2].vol_between(te - DAY_MS, te)
                    cc = c_hl + bn_cost_bp(usd, cv, FEE_BP[cex[0]], cal_bn['half_spread_bp'], cal_bn['depth_per_vol']) / 1e4
                    r_hl, r_cx = trailing_rate(hf, te), trailing_rate(cex[3], te)
                    if r_hl >= r_cx:
                        ptr = pair_trade(hp, hf, cex[2], cex[3], te, tx, cc)
                        short = 'hyperliquid'
                    else:
                        ptr = pair_trade(cex[2], cex[3], hp, hf, te, tx, cc)
                        short = cex[0]
                    if ptr:
                        ptr.update({'A': anchor, 'symbol': c, 'usd': usd, 'short': short,
                                    'spread_ann_at_entry': (r_hl - r_cx) * 8760, 'announce_inferred': A is not None})
                        variants.setdefault(('hl_vs_cex', delay, usd), []).append(ptr)
    res['variants'] = summarize_delist_variants(variants)
    res['funding_arb_attribution'] = funding_arb_attribution(W)
    keys = ('funding_ann_7d_before_A', 'funding_ann_A_to_T', 'funding_ann_last_24h', 'premium_A_minus_24h',
            'premium_A_plus_2h', 'premium_T_minus_24h', 'premium_T_minus_2h', 'premium_T', 'ret_A-24h_A_vs_basket',
            'ret_A_A+2h', 'ret_A_A+2h_vs_basket', 'ret_A+2h_T_vs_basket', 'ret_A+24h_T_vs_basket', 'spot_ret_T_T+7d')
    summ = {}
    paths = [e['path'] for e in res['binance_events'] if e.get('path')]
    for k in keys:
        xs = [p_[k] for p_ in paths if p_.get(k) is not None]
        summ[k] = {'n': len(xs), 'median': statistics.median(xs) if xs else None, 'mean': statistics.fmean(xs) if xs else None,
                   'share_positive': (sum(1 for v in xs if v > 0) / len(xs)) if xs else None}
    vr = [p_['vol24_after_A'] / p_['vol24_before_A'] for p_ in paths if p_.get('vol24_before_A')]
    oi = [p_['oi_usd_T-2h'] / p_['oi_usd_A'] for p_ in paths if p_.get('oi_usd_A') and p_.get('oi_usd_T-2h')]
    summ['volume_multiple_24h_after_A'] = {'n': len(vr), 'median': statistics.median(vr) if vr else None}
    summ['oi_T-2h_over_A'] = {'n': len(oi), 'median': statistics.median(oi) if oi else None}
    nh = [e['notice_hours'] for e in res['binance_events'] if e.get('notice_hours')]
    summ['notice_hours'] = {'n': len(nh), 'median': statistics.median(nh) if nh else None, 'min': min(nh, default=None),
                            'max': max(nh, default=None)}
    res['binance_path_summary'] = summ
    hn = [e['notice_hours_inferred'] for e in res['hl_events'] if e.get('notice_hours_inferred')]
    res['hl_path_summary'] = {
        'inferred_notice_hours': {'n': len(hn), 'median': statistics.median(hn) if hn else None},
        'hl_last_vs_cex': {k: (statistics.median(v) if v else None) for k, v in
                           (('median', [e['hl_last_vs_cex'] for e in res['hl_events'] if e.get('hl_last_vs_cex') is not None]),)},
        'ret_last_7d_vs_basket_median': statistics.median([e['ret_last_7d_vs_basket'] for e in res['hl_events']
                                                           if e.get('ret_last_7d_vs_basket') is not None] or [0.0])}
    res['events_per_year'] = {
        'binance_with_notice': sum(1 for e in res['binance_events'] if e.get('announce_ms')),
        'binance_notice_dates': len({int(e['announce_ms'] // DAY_MS) for e in res['binance_events'] if e.get('announce_ms')}),
        'binance_span_days': ((max(e['settle_ms'] for e in res['binance_events']) -
                               min(e['settle_ms'] for e in res['binance_events'])) / DAY_MS) if res['binance_events'] else None,
        'hl_delistings': len(res['hl_events']),
        'hl_delisting_dates': len({int(e['last_live_ms'] // DAY_MS) for e in res['hl_events']})}
    res['_variants'] = variants
    return res


FUNDING_ARB_DELISTED = ('MAVIA', 'ZEREBRO', 'TST', 'IP', 'PROMPT', 'DOOD', 'ARK', 'TON', 'MEW', 'CHILLGUY', 'HMSTR',
                        'NOT', 'XAI')


def funding_arb_attribution(W, test_start='2026-04-01'):
    """For the thirteen coins the funding study credited with 43% of its HL-vs-Binance test profit ("later delisted"):
    whether Hyperliquid has in fact delisted each, and how its HL-minus-Binance funding spread (summed hourly, in bp)
    splits between the weeks before the last 30 days, the last 30 days, the last 7 days and the inferred notice."""
    m = load_json(FUNDING_STUDY / 'mapping.json', {}) or {}
    t0 = ms_of(test_start)
    out = []
    for c in FUNDING_ARB_DELISTED:
        r = W.calendar.get(c) or {}
        sym = (m.get(c) or {}).get('binance')
        fp = FUNDING_STUDY / 'raw' / 'binance' / 'funding' / ('%s.json.gz' % sym) if sym else None
        bn = sorted((int(x['t']), float(x['rate'])) for x in read_gz(fp)) if fp and fp.exists() else []
        hl = hl_rows_ms(W, c)
        end = r.get('last_live_ms') or W.data_end
        row = {'coin': c, 'hl_delisted': bool(r.get('delisted')), 'last_live_utc': r.get('last_live_utc'),
               'binance_symbol': sym}
        for k, a in (('test_period', t0), ('last_30d', end - 30 * DAY_MS), ('last_7d', end - 7 * DAY_MS),
                     ('last_24h', end - DAY_MS)):
            a = max(a, t0)
            row[k + '_spread_bp'] = 1e4 * (settlements_between(hl, a, end) - settlements_between(bn, a, end))
            row[k + '_hours'] = (end - a) / HOUR_MS
        out.append(row)
    return out


def summarize_delist_variants(variants):
    out = []
    for (kind, delay, usd), rows in sorted(variants.items()):
        rows = sorted(rows, key=lambda r: r['A'])
        x = [r['pnl'] for r in rows]
        if not x:
            continue
        by_day = by_group_means([(r['A'], r['pnl']) for r in rows], key=lambda t: int(t // DAY_MS))
        hours = sum(r['hours'] for r in rows)
        rec = {'kind': kind, 'delay_h': delay, 'usd': usd, 'n': len(x), 'mean': statistics.fmean(x),
               'median': statistics.median(x), 'hit': sum(1 for v in x if v > 0) / len(x), 't': tstat(x),
               'announce_days': len(by_day), 't_by_day': tstat(by_day), 'mean_hours': hours / len(x),
               'per_position_year': sum(x) / hours * 8760 if hours else None,
               'gross_per_position_year': (sum(r.get('gross', r['pnl'] + r['cost']) for r in rows) / hours * 8760) if hours else None,
               'mean_cost': statistics.fmean(r['cost'] for r in rows)}
        if 'placebo_pnl' in rows[0]:
            pl = [r['placebo_pnl'] for r in rows if r.get('placebo_pnl') is not None]
            rec['placebo_mean'] = statistics.fmean(pl) if pl else None
            rec['placebo_n'] = len(pl)
        half = len(rows) // 2
        rec['first_half_mean'] = statistics.fmean(x[:half]) if half else None
        rec['second_half_mean'] = statistics.fmean(x[half:]) if len(x) > half else None
        rec['second_half_t_by_day'] = tstat(by_group_means([(r['A'], r['pnl']) for r in rows[half:]],
                                                           key=lambda t: int(t // DAY_MS)))
        rec['split_at'] = iso(rows[half]['A']) if half < len(rows) else None
        out.append(rec)
    return out


# ================================================================================================ capacity, commands

def capacity_listings(W, books, edge=None, sizes=(10_000, 25_000, 50_000, 100_000, 250_000)):
    """Round trips and depth on the live books by listing age (only today's books exist, so the "first weeks" are the
    coins listed in the last 120 days), and the size at which a round trip eats half of `edge` (a fraction a trade)."""
    now = W.data_end
    rows = []
    for c, b in books.items():
        r = W.calendar.get(c)
        if not r or c in NOT_ALTS:
            continue
        age = (now - r['listing_ms']) / DAY_MS
        rec = {'coin': c, 'age_days': age, 'source': b[2], 'oi_usd': b[3], 'vol24_usd': b[4]}
        fine = b[0]
        for bp in (25, 50, 100):
            rec['depth_%dbp' % bp] = (depth_usd(fine[1], fine[0], bp) + depth_usd(fine[2], fine[0], bp)) / 2
            if b[1]:
                rec['depth_%dbp' % bp] = max(rec['depth_%dbp' % bp],
                                             (depth_usd(b[1][1], b[1][0], bp) + depth_usd(b[1][2], b[1][0], bp)) / 2)
        for usd in sizes:
            rec['rt_bp_%d' % usd] = round_trip_bp(b[0], b[1], usd)
            rec['fill_%d' % usd] = fillable(b[0], b[1], usd)
        if edge:
            lo, hi = 1_000.0, 5_000_000.0
            if (round_trip_bp(b[0], b[1], lo) or 1e9) / 1e4 > edge / 2:
                rec['half_edge_usd'] = 0.0
            else:
                for _ in range(40):
                    mid = (lo + hi) / 2
                    v = round_trip_bp(b[0], b[1], mid)
                    if v is not None and v / 1e4 <= edge / 2:
                        lo = mid
                    else:
                        hi = mid
                rec['half_edge_usd'] = lo
        rows.append(rec)
    buckets = {}
    for rec in rows:
        k = '<=120d' if rec['age_days'] <= 120 else ('120-365d' if rec['age_days'] <= 365 else '>365d')
        buckets.setdefault(k, []).append(rec)
    summ = {}
    for k, v in buckets.items():
        d = {'n': len(v)}
        for key in ['depth_25bp', 'depth_50bp', 'depth_100bp'] + ['rt_bp_%d' % u for u in sizes] + (['half_edge_usd'] if edge else []):
            xs = [r[key] for r in v if r.get(key) is not None]
            d[key + '_median'] = statistics.median(xs) if xs else None
            d[key + '_priced'] = len(xs)
        for u in sizes:
            d['fillable_share_%d' % u] = sum(1 for r in v if r.get('fill_%d' % u)) / len(v)
        summ[k] = d
    return {'by_age': summ, 'recent': sorted([r for r in rows if r['age_days'] <= 120], key=lambda r: r['age_days']),
            'edge_used': edge}


def strip_private(d):
    if isinstance(d, dict):
        return {k: strip_private(v) for k, v in d.items() if not str(k).startswith('_')}
    if isinstance(d, list):
        return [strip_private(v) for v in d]
    if isinstance(d, set):
        return sorted(d)
    return d


def funding_proxy_check(W):
    """How well the fixed seasoned subset's funding stands for the whole basket's, measured where both exist (from the
    store's start): mean daily difference and its spread, annualised."""
    bf = W.basket_fday()
    s0 = ms_of(STORE_START)
    diffs = []
    for D, v in bf.items():
        if D < s0:
            continue
        sub = [W.fday[c][D] for c in HEDGE_FUNDING_SUBSET if D in W.fday.get(c, {})]
        if len(sub) >= 5:
            diffs.append(v - statistics.fmean(sub))
    if not diffs:
        return None
    return {'days': len(diffs), 'basket_minus_subset_ann': statistics.fmean(diffs) * 365,
            'sd_daily_ann': statistics.pstdev(diffs) * 365,
            'basket_ann_mean': statistics.fmean(v for D, v in bf.items() if D >= s0) * 365,
            'basket_ann_mean_pre_store_subset': (statistics.fmean(v for D, v in bf.items() if D < s0) * 365
                                                 if any(D < s0 for D in bf) else None)}


def cmd_analyze(args):
    out = Path(args.out)
    t0 = time.time()
    W = World(out)
    books = load_books(out)
    res = {'generated': iso(int(time.time() * 1000)), 'data_end': iso(W.data_end), 'ssr': SSR,
           'calendar': sorted(W.calendar.values(), key=lambda r: r['listing_ms'])}
    A = analyze_listings(W, books, usd=args.usd)
    chosen = next((v for v in A['variants'] if v['name'] == A['chosen']), None)
    edge = chosen['out'].get('mean') if chosen and chosen['out'].get('n') else None
    A['capacity'] = capacity_listings(W, books, edge=edge if (edge and edge > 0) else None)
    A['funding_proxy_check'] = funding_proxy_check(W)
    # the size ladder for the chosen variant: the same trades re-costed at each size
    if chosen:
        ladder = {}
        for usd in (10_000, 25_000, 50_000, 100_000):
            costs = build_costs(W, books, usd)
            tr = run_variant(W, listing_events(W), chosen['d'], chosen['H'], chosen['hedge'], costs)
            oos = [r for r in tr if r['L'] >= A['cutoff_ms']]
            ladder[usd] = {'out': summarize(oos), 'mean_cost': statistics.fmean(r['cost'] for r in oos) if oos else None,
                           'coins_imputed': len(costs['imputed'])}
        A['chosen_size_ladder'] = ladder
    res['part_a'] = A
    res['part_b'] = analyze_delistings(W, out)
    res['seconds'] = round(time.time() - t0, 1)
    write_json(out / 'analysis.json', strip_private(res))
    # the manifest also records what is on disk and each collector's last log line (a stage re-run overwrites its
    # entry in `stages`, so the first, downloading run of each is kept here)
    man = load_json(out / 'manifest.json', {}) or {}
    raw = out / 'raw'
    man['raw_counts'] = {str(p_.relative_to(raw)): len(list(p_.glob('*'))) for p_ in sorted(raw.glob('*/*')) if p_.is_dir()}
    man['logs'] = {}
    for lg in sorted(out.glob('collect_*.log')):
        lines = [x for x in lg.read_text().splitlines() if x.strip()]
        man['logs'][lg.name] = lines[-1][:600] if lines else None
    man['analysis'] = {'generated': res['generated'], 'seconds': res['seconds'], 'listings': A['events'],
                       'binance_events': len(res['part_b']['binance_events']), 'hl_delistings': len(res['part_b']['hl_events']),
                       'funding_days_imputed_at_floor_chosen_oos': sum(r.get('funding_days_missing') or 0
                                                                       for r in A.get('chosen_trades_oos') or [])}
    write_json(out / 'manifest.json', man)
    print(json.dumps({'events_a': A['events'], 'chosen': A['chosen'], 'cutoff': A['cutoff_utc'],
                      'binance_events': len(res['part_b']['binance_events']), 'hl_events': len(res['part_b']['hl_events']),
                      'seconds': res['seconds']}))
    return 0


def pct(x, d=1):
    return '—' if x is None else '%+.*f%%' % (d, 100 * x)


def num(x, d=2):
    return '—' if x is None else '%.*f' % (d, x)


def usd_s(x):
    if x is None:
        return '—'
    return '$%.1fM' % (x / 1e6) if abs(x) >= 1e6 else '$%.0fk' % (x / 1e3)


def cmd_render(args):
    out = Path(args.out)
    R = load_json(out / 'analysis.json')
    A, Bd = R['part_a'], R['part_b']
    L = ['# Listing life cycle — tables', '', 'Generated %s; data to %s.' % (R['generated'], R['data_end']), '',
         '## (a) New listings', '',
         'Listings since %s (migrations and PAXG excluded): %d; split at %s (median listing date) into a choosing half '
         'and a test half. P&L per trade is a fraction of one leg\'s notional at %s a leg, after both round trips '
         '(coin: own live book, else the median of its listing year; BTC %.1fbp; basket %.1fbp).' % (
             STUDY_START, A['events'], A['cutoff_utc'][:10], usd_s(A['usd_per_leg']),
             A['cost_model']['btc_rt_bp'], A['cost_model']['basket_rt_bp']), '',
         'Listings by quarter: ' + ', '.join('%s %d' % kv for kv in A['calendar_counts']['by_quarter'].items()) + '.',
         'Cohorts: ' + ', '.join('%s %d' % kv for kv in A['calendar_counts']['by_cohort'].items()) + '.', '',
         '| variant | n in | mean in | week t in | BH | n out | mean out | median out | hit out | week t out | placebo out | paired excess out (t) | coin ret out | hedge ret out | short funding out | hedge funding out |',
         '|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for v in A['variants']:
        ci, co, po, pe, cc = v['in'], v['out'], v['placebo_out'], v['paired_out'], v['components_out'] or {}
        L.append('| %s%s | %d | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s |' % (
            v['name'], ' **chosen**' if v['name'] == A['chosen'] else '', ci.get('n', 0), pct(ci.get('mean')),
            num(ci.get('t_week')), 'yes' if v.get('bh_in_reject') else 'no', co.get('n', 0), pct(co.get('mean')),
            pct(co.get('median')), '—' if co.get('hit') is None else '%.0f%%' % (100 * co['hit']), num(co.get('t_week')),
            pct(po.get('mean')), pct(pe.get('mean')), num(pe.get('t_week')), pct(cc.get('coin_return')),
            pct(cc.get('hedge_return')), pct(cc.get('funding_short_received')), pct(cc.get('funding_hedge_paid'))))
    L += ['', 'Deflated Sharpe of the in-sample choice (week means, %d variants): %s; its out-of-sample rank by week t: %s of %d.' % (
        A['n_variants'], num(A.get('deflated_sharpe_in_sample'), 3), A.get('chosen_oos_rank'), A['n_variants']), '']
    if A.get('chosen_size_ladder'):
        L += ['### Chosen variant re-costed by size (test half)', '', '| size a leg | n | mean | week t | mean cost |', '|---|---:|---:|---:|---:|']
        for usd, x in sorted(A['chosen_size_ladder'].items(), key=lambda kv: int(kv[0])):
            L.append('| %s | %d | %s | %s | %s |' % (usd_s(int(usd)), x['out'].get('n', 0), pct(x['out'].get('mean')),
                                                     num(x['out'].get('t_week')), pct(x.get('mean_cost'), 2)))
        L.append('')
    if A.get('chosen_by_quarter'):
        L += ['### Chosen variant by listing quarter', '', '| quarter | n | mean | placebo n | placebo mean |', '|---|---:|---:|---:|---:|']
        for q, x in A['chosen_by_quarter'].items():
            L.append('| %s | %d | %s | %d | %s |' % (q, x['n'], pct(x['mean']), x['placebo_n'], pct(x['placebo_mean'])))
        L.append('')
    if A.get('chosen_cohorts'):
        L += ['### Chosen variant by cohort (all listings; test half in brackets)', '', '| split | group | n | mean | week t | n test | mean test | coin ret | short funding |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
        for g, rows in A['chosen_cohorts'].items():
            for k, x in rows.items():
                c = x.get('components') or {}
                L.append('| %s | %s | %d | %s | %s | %d | %s | %s | %s |' % (g, k, x['all'].get('n', 0), pct(x['all'].get('mean')),
                         num(x['all'].get('t_week')), x['out'].get('n', 0), pct(x['out'].get('mean')),
                         pct(c.get('coin_return')), pct(c.get('funding_short_received'))))
        L.append('')
    L += ['### Decay curve: mean cumulative return of a new listing over the seasoned basket and over BTC, and the funding a short received', '',
          '| day | n | excess vs basket mean (median) | excess vs BTC mean | short funding mean |', '|---:|---:|---:|---:|---:|']
    for k, x in sorted(A['decay_curve'].items(), key=lambda kv: int(kv[0])):
        eb, ex, f = x['excess_basket'], x['excess_btc'], x['funding']
        L.append('| %s | %d | %s (%s) | %s | %s |' % (k, eb.get('n', 0), pct(eb.get('mean')), pct(eb.get('median')),
                                                    pct(ex.get('mean')), pct(f.get('mean'), 2)))
    cap = A.get('capacity') or {}
    if cap:
        L += ['', '### Capacity on the live books (2026-10-10), by listing age', '',
              '| age | coins | depth ±50bp | depth ±100bp | RT $10k | RT $25k | RT $50k | RT $100k | RT $250k | half-edge size |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for k in ('<=120d', '120-365d', '>365d'):
            x = cap['by_age'].get(k)
            if not x:
                continue
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                k, x['n'], usd_s(x.get('depth_50bp_median')), usd_s(x.get('depth_100bp_median')),
                num(x.get('rt_bp_10000_median'), 1), num(x.get('rt_bp_25000_median'), 1), num(x.get('rt_bp_50000_median'), 1),
                num(x.get('rt_bp_100000_median'), 1), num(x.get('rt_bp_250000_median'), 1), usd_s(x.get('half_edge_usd_median'))))
        L += ['', 'Recent listings: ' + '; '.join('%s %.0fd depth±50bp %s RT$50k %s' % (r['coin'], r['age_days'], usd_s(r['depth_50bp']), num(r.get('rt_bp_50000'), 1)) for r in cap['recent']), '']
    L += ['## (b) Delistings', '', '| trade | delay | size | n | mean | median | hit | t | t by day | per position-year | gross per pos-yr | placebo | first half | second half (t by day) |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for v in Bd['variants']:
        L.append('| %s | %dh | %s | %d | %s | %s | %.0f%% | %s | %s | %s | %s | %s | %s | %s (%s) |' % (
            v['kind'], v['delay_h'], usd_s(v['usd']), v['n'], pct(v['mean'], 2), pct(v['median'], 2), 100 * v['hit'],
            num(v['t']), num(v['t_by_day']), pct(v['per_position_year'], 0), pct(v.get('gross_per_position_year'), 0),
            pct(v.get('placebo_mean'), 2), pct(v.get('first_half_mean'), 2), pct(v.get('second_half_mean'), 2),
            num(v.get('second_half_t_by_day'))))
    L += ['', '### Binance events', '', '| symbol | announced | settled | notice h | HL | funding ann before A | A→T | last 24h | premium T−2h | ret A−24h→A vs basket | A→A+2h | A+2h→T vs basket | vol24 before→after A | OI at A → T−2h | perp vs spot at T |',
          '|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|']
    for e in Bd['binance_events']:
        pth = e.get('path') or {}
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s→%s | %s→%s | %s |' % (
            e['symbol'], (iso(e['announce_ms']) or '—')[:16], iso(e['settle_ms'])[:16], num(e.get('notice_hours'), 0),
            (e.get('hl_coin') or '—') + ('' if not e.get('hl_coin') else (' live' if e.get('hl_live_through_settlement') else ' gone')),
            pct(pth.get('funding_ann_7d_before_A'), 0), pct(pth.get('funding_ann_A_to_T'), 0), pct(pth.get('funding_ann_last_24h'), 0),
            pct(pth.get('premium_T_minus_2h'), 2), pct(pth.get('ret_A-24h_A_vs_basket')), pct(pth.get('ret_A_A+2h')),
            pct(pth.get('ret_A+2h_T_vs_basket')), usd_s(pth.get('vol24_before_A')), usd_s(pth.get('vol24_after_A')),
            usd_s(pth.get('oi_usd_A')), usd_s(pth.get('oi_usd_T-2h')), pct(pth.get('perp_vs_spot_at_T'), 2)))
    L += ['', '### Hyperliquid delistings (announcement inferred from a closing-volume burst)', '',
          '| coin | last live hour | inferred notice h | CEX leg | HL funding ann 30d / 7d / 24h | CEX funding ann 30d / 7d / 24h | HL last vs CEX | ret last 7d vs basket | CEX ret 7d after vs basket |',
          '|---|---|---:|---|---|---|---:|---:|---:|']
    for e in Bd['hl_events']:
        h, c = e.get('hl_funding_ann') or {}, e.get('cex_funding_ann') or {}
        L.append('| %s | %s | %s | %s | %s / %s / %s | %s / %s / %s | %s | %s | %s |' % (
            e['coin'], e['last_live_utc'][:16], num(e.get('notice_hours_inferred'), 0), (e.get('cex') or ['—'])[0] if e.get('cex') else '—',
            pct(h.get('last_30d'), 0), pct(h.get('last_7d'), 0), pct(h.get('last_24h'), 0),
            pct(c.get('last_30d'), 0), pct(c.get('last_7d'), 0), pct(c.get('last_24h'), 0),
            pct(e.get('hl_last_vs_cex'), 2), pct(e.get('ret_last_7d_vs_basket')), pct(e.get('cex_ret_after_7d_vs_basket'))))
    ep = Bd.get('events_per_year') or {}
    L += ['', 'Events: %s Binance USD-M delistings with a notice (on %s notice dates over %s days of settlements); %s '
          'Hyperliquid delistings on %s dates in the store year.' % (ep.get('binance_with_notice'), ep.get('binance_notice_dates'),
                                                                   num(ep.get('binance_span_days'), 0), ep.get('hl_delistings'),
                                                                   ep.get('hl_delisting_dates')), '',
          '### The funding study\'s thirteen "later delisted" coins: HL minus Binance funding, summed (bp)', '',
          '| coin | HL delisted | last live | test period | last 30d | last 7d | last 24h |', '|---|---|---|---:|---:|---:|---:|']
    for r in Bd.get('funding_arb_attribution') or []:
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (r['coin'], 'yes' if r['hl_delisted'] else '**no**',
                 (r['last_live_utc'] or '—')[:10], num(r['test_period_spread_bp'], 0), num(r['last_30d_spread_bp'], 0),
                 num(r['last_7d_spread_bp'], 0), num(r['last_24h_spread_bp'], 0)))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:40]))
    return 0


# ================================================================================================ main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect', help='download one stage of inputs (cached; re-runs skip what is on disk)')
    c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--stage', required=True, choices=['hl-meta', 'hl-candles', 'hl-funding', 'books', 'binance'])
    c.add_argument('--interval', type=float, default=1.5, help='seconds between Hyperliquid calls (>= 0.3)')
    c.add_argument('--since', default='2025-09-01', help='Binance notices from this date')
    c.add_argument('--days-before', type=int, default=45, help='Binance series start this many days before settlement')
    c.add_argument('--metrics-days', type=int, default=12, help='daily open-interest files before each settlement')
    c.add_argument('--recent-days', type=int, default=75, help='books: coins listed within this many days')
    c.add_argument('--coins', default='', help='books: extra coins to read')
    c.add_argument('--refresh', action='store_true')
    a = sub.add_parser('analyze', help='part (a) and (b): analysis.json')
    a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--usd', type=float, default=25_000, help='size a leg for the part (a) cost model')
    r = sub.add_parser('render', help='tables.md from analysis.json')
    r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
