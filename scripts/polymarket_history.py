#!/usr/bin/env python3
"""Polymarket from its history: what resolved markets paid the favourite, the neg-risk sum, and the resolution lag.

Why. Every strategy this repo had priced before 2026-10-09 read a ledger or a perp book, and every prediction-market
claim anyone makes ("favourites are underpriced", "neg-risk baskets sum to less than a dollar", "buy the decided
market at 99c and wait") is a statement about thousands of resolved markets that nobody had counted here. Polymarket
publishes the resolved universe (gamma API: outcome, close time, the UMA resolution history, neg-risk grouping, fee
flags, tags) and a price history for every outcome token (CLOB `prices-history`), so the claims can be counted
retroactively instead of argued.

Three strategies, each tested with the repo's backtest protocol (`backtest.py`: choose on markets that closed before
a cutoff, report once on markets entered after it):

  A. **Favourite–longshot / high-probability bonds.** At a fixed horizon before the *scheduled* end (`endDate`, known
     in advance; anchoring on the actual close would be look-ahead), buy the outcome trading in a band [lo, hi) and
     hold to the actual close. Return is per dollar staked, annualised over the days actually held (`closedTime`).
  B. **Neg-risk sums.** A neg-risk event is a set of mutually exclusive YES markets of which exactly one pays. If the
     YES asks sum to less than one dollar, buying all of them is an arbitrage; if the YES bids sum to more than one,
     the NO side is. History gives a non-executable upper bound (the series is a midpoint); live book snapshots give
     the executable sums and their size.
  C. **Resolution lag.** Markets that trade at >= a threshold on one side after their scheduled end, before the
     oracle settles. The trade is the last cent or two over the lag, annualised against the savings rate.

What `prices-history` is. Points are the CLOB's displayed price: the bid/ask midpoint (half-tick values such as 0.405
on a 0.01 tick and 0.0005 on a 0.001 tick occur throughout), so a "price" here is a midpoint, not a fill. Every
return below charges a half-spread on top of it — measured in the live books per category and price band — and the
`trades` subcommand measures, on a sample of the backtest's own entries, where actual taker fills sat against the
midpoint at the same minutes. Range rules learnt the hard way: `interval=max` works on resolved tokens only at coarse
fidelity (720 minutes returns points, 60 returns nothing); `startTs/endTs` windows longer than ~15 days are rejected
at any fidelity; points are only emitted when the price moved, so a price at time t is the last point at or before t.

Fees. Since 2026 taker fees apply per category, `fee = shares x feeRate x p x (1 - p)` (docs.polymarket.com/trading/
fees, read 2026-10-09; makers pay none). The backtest charges the *current* schedule to every trade, including
historical ones that paid nothing, because the question is what the strategy earns from here.

    uv run python scripts/polymarket_history.py universe --out research/2026-10-09/polymarket_history
    uv run python scripts/polymarket_history.py collect  --out research/2026-10-09/polymarket_history
    uv run python scripts/polymarket_history.py negrisk  --out research/2026-10-09/polymarket_history
    uv run python scripts/polymarket_history.py live     --out research/2026-10-09/polymarket_history   (repeat)
    uv run python scripts/polymarket_history.py analyze  --out research/2026-10-09/polymarket_history
    uv run python scripts/polymarket_history.py trades   --out research/2026-10-09/polymarket_history
    uv run python scripts/polymarket_history.py render   --out research/2026-10-09/polymarket_history
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import json
import math
import random
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

GAMMA = 'https://gamma-api.polymarket.com'
CLOB = 'https://clob.polymarket.com'
DATA = 'https://data-api.polymarket.com'
UA = 'Mozilla/5.0 (llm-quant research; polymarket_history)'
DAY = 86400.0
HOUR = 3600.0
SSR = 0.038            # Sky savings rate read on chain (sUSDS.ssr(), 2026-10-09 ~20:45 UTC): idle USDC's opportunity cost
CUTOFF = '2026-01-01T00:00:00+00:00'   # fixed before any return was computed: choose before it, test after it
START = '2024-01-01T00:00:00+00:00'    # the CLOB era with volume; 2020-2023 markets ($10k+) number ~2,300 in all

HORIZONS = {'30d': 30 * DAY, '7d': 7 * DAY, '3d': 3 * DAY, '1d': DAY, '6h': 6 * HOUR}
BANDS = [(0.85, 0.90), (0.90, 0.95), (0.95, 0.98), (0.98, 0.995), (0.85, 0.995)]
C_THRESHOLDS = [0.95, 0.97, 0.98, 0.99]
PRICE_BINS = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.98, 0.995, 1.0001]

# Current taker fee coefficients per category (docs.polymarket.com/trading/fees, read 2026-10-09). Geopolitics is
# fee-free; mentions/tech/finance/politics 0.04; crypto 0.07; the rest 0.05.
FEE_RATE_BY_CAT = {'crypto_updown': 0.07, 'crypto_price': 0.07, 'sports': 0.05, 'elections': 0.04,
                   'politics': 0.04, 'economics': 0.05, 'culture': 0.05, 'science_tech': 0.05, 'other': 0.05}
# feeType values seen on resolved markets (2026): crypto_fees_v2, crypto_15_min, crypto_fees, sports_fees_v2/_v3,
# sports_fees_nfl_cfb_oct26, politics_fees, finance_prices_fees, tech_fees, economics_fees, culture_fees, weather_fees,
# mentions_fees, general_fees, zero_fees. The forward-looking cost uses the category schedule above, not these flags.


# ------------------------------------------------------------------------------------------------- utilities

def utc(ts=None):
    ts = time.time() if ts is None else ts
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec='seconds')


def parse_ts(s):
    """Gamma timestamps come as '2026-04-05 06:15:11+00', '2026-03-31T00:00:00Z' or '...123456Z'."""
    if not s:
        return None
    s = str(s).strip().replace(' ', 'T')
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    if len(s) >= 3 and (s.endswith('+00') or s.endswith('-00')):
        s = s + ':00'
    try:
        d = dt.datetime.fromisoformat(s)
    except ValueError:
        try:
            d = dt.datetime.fromisoformat(s[:10])
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.timestamp()


def jload(v, default=None):
    if v is None:
        return default
    if isinstance(v, (list, dict)):
        return v
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return default


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


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
    tmp.write_text(json.dumps(obj, indent=1, default=str))
    tmp.replace(p)


def update_manifest(out, key, value):
    p = Path(out) / 'manifest.json'
    man = json.loads(p.read_text()) if p.exists() else {}
    man[key] = value
    write_json(p, man)


def stable_u(key):
    """A uniform number in [0, 1) from a hash of the key: sampling that is reproducible and order-free."""
    return int(hashlib.sha1(str(key).encode()).hexdigest()[:13], 16) / float(16 ** 13)


class Http:
    """Paced GET/POST with retries. 429 and 5xx back off; the pacing is global across worker threads."""

    def __init__(self, interval=0.12, timeout=40, retries=6):
        self.interval, self.timeout, self.retries = interval, timeout, retries
        self.lock = threading.Lock()
        self.next_at = 0.0
        self.n = self.errors = self.throttled = 0

    def _pace(self):
        with self.lock:
            now = time.monotonic()
            wait = self.next_at - now
            self.next_at = max(now, self.next_at) + self.interval
        if wait > 0:
            time.sleep(wait)

    def request(self, url, body=None):
        last = None
        for attempt in range(self.retries):
            self._pace()
            data = None if body is None else json.dumps(body).encode()
            headers = {'User-Agent': UA, 'Accept': 'application/json', 'Accept-Encoding': 'gzip'}
            if body is not None:
                headers['Content-Type'] = 'application/json'
            req = urllib.request.Request(url, data=data, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        raw = gzip.decompress(raw)
                with self.lock:
                    self.n += 1
                return json.loads(raw)
            except urllib.error.HTTPError as e:
                with self.lock:
                    self.errors += 1
                last = 'HTTP %s %s' % (e.code, e.read()[:200])
                if e.code == 429:
                    with self.lock:
                        self.throttled += 1
                        self.next_at = time.monotonic() + min(30.0, 2.0 * 2 ** attempt)
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

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


# ------------------------------------------------------------------------------------------------- categories

# Tag labels (lower-cased) to a coarse category, first match wins in this order. Polymarket tags are many and
# overlapping ("Crypto", "Crypto Prices", "Up or Down", "Bitcoin"); the order puts the short-dated machine-made
# families first because they behave differently from everything else.
CATEGORY_RULES = [
    ('crypto_updown', {'up or down', '15m', '5m', '1h', '4h', 'hourly', 'daily up or down'}),
    ('crypto_price', {'crypto prices', 'bitcoin', 'ethereum', 'solana', 'xrp', 'crypto', 'pre-market', 'airdrops',
                      'memecoins', 'stablecoins', 'fdv', 'token launch'}),
    ('sports', {'sports', 'nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'tennis', 'golf', 'ufc', 'mma', 'boxing',
                'esports', 'cricket', 'f1', 'formula 1', 'ncaa', 'cfb', 'cbb', 'epl', 'la liga', 'champions league',
                'basketball', 'baseball', 'hockey', 'games', 'counter strike', 'league of legends', 'dota 2',
                'olympics', 'world cup', 'wnba', 'mls', 'serie a', 'bundesliga', 'ligue 1', 'atp', 'wta', 'chess',
                'poker'}),
    ('elections', {'elections', 'us election', 'global elections', 'primaries', 'us presidential election',
                   'midterms', 'world elections', 'election'}),
    ('politics', {'politics', 'us politics', 'trump', 'congress', 'geopolitics', 'world', 'ukraine', 'israel',
                  'iran', 'china', 'middle east', 'courts', 'scotus', 'trump presidency', 'cabinet', 'tariffs'}),
    ('economics', {'economy', 'economics', 'fed', 'fed rates', 'inflation', 'business', 'finance', 'stocks',
                   'earnings', 'equities', 'commodities', 'ipos', 'macro', 'gdp', 'jobs report', 'cpi'}),
    ('culture', {'pop culture', 'culture', 'movies', 'music', 'awards', 'oscars', 'grammys', 'tv', 'celebrities',
                 'tweet markets', 'elon musk', 'mentions', 'twitter', 'youtube', 'box office', 'entertainment'}),
    ('science_tech', {'science', 'tech', 'ai', 'space', 'weather', 'climate', 'openai', 'technology', 'health'}),
]


def categorize(tag_labels, question='', legacy_category=None):
    labels = {str(t).strip().lower() for t in (tag_labels or []) if t}
    q = (question or '').lower()
    if 'up or down' in q:
        return 'crypto_updown'
    for cat, keys in CATEGORY_RULES:
        if labels & keys:
            return cat
    lc = (legacy_category or '').strip().lower()
    if lc:
        for cat, keys in CATEGORY_RULES:
            if lc in keys:
                return cat
    if lc in ('sports',):
        return 'sports'
    if lc in ('crypto',):
        return 'crypto_price'
    if lc in ('us-current-affairs', 'politics', 'global politics'):
        return 'politics'
    return 'other'


def fee_rate(cat, tags=None):
    """Current taker coefficient for a market: geopolitics markets are fee-free; the mixed categories take the
    schedule's own split from their tags (weather 0.05 inside science_tech, finance 0.04 inside economics, mentions
    0.04 inside culture); otherwise by category."""
    labels = {str(t).strip().lower() for t in (tags or [])}
    if 'geopolitics' in labels:
        return 0.0
    if cat in ('science_tech', 'economics', 'culture', 'other'):
        if 'weather' in labels:
            return 0.05
        if labels & {'mentions', 'tweet markets'}:
            return 0.04
        if labels & {'finance', 'equities', 'stocks', 'commodities'}:
            return 0.04
        if labels & {'tech', 'ai'}:
            return 0.04
    return FEE_RATE_BY_CAT.get(cat, 0.05)


# ------------------------------------------------------------------------------------------------- pure economics

def fee_per_share(rate, price):
    return rate * price * (1.0 - price)


def trade_return(p_mid, payout, half_spread=0.0, rate=0.0, cap=0.999):
    """Return per dollar of buying one outcome at the midpoint plus a half-spread, paying the taker fee, and holding
    to resolution, where the share pays `payout` (1, 0, or 0.5 on a 50-50 resolution)."""
    px = min(cap, p_mid + half_spread)
    cost = px + fee_per_share(rate, px)
    return payout / cost - 1.0


def annualised(sum_return, sum_days):
    """Return per capital-day, annualised: the rate a strategy earns if every dollar is recycled the day it frees."""
    return (sum_return / sum_days * 365.0) if sum_days > 0 else None


def wilson(k, n, z=1.96):
    """Wilson score interval for a proportion; k may be fractional (weighted counts, 50-50 halves)."""
    if n <= 0:
        return None, None
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n))) / d
    return max(0.0, c - h), min(1.0, c + h)


def as_of(series, t, max_stale=None):
    """Last (t_i, p_i) with t_i <= t, as p; None if there is none or it is older than max_stale seconds."""
    if not series:
        return None
    i = bisect.bisect_right([x[0] for x in series], t) - 1
    if i < 0:
        return None
    if max_stale is not None and t - series[i][0] > max_stale:
        return None
    return series[i][1]


def binary_payout(m):
    """Payout of outcome 0 at resolution: 1.0, 0.0, 0.5 (a 50-50 resolution), or None (closed without one)."""
    op = m.get('outcomePrices') or []
    if len(op) != 2 or any(x is None for x in op):
        return None
    a, b = op
    if a >= 0.99 and b <= 0.01:
        return 1.0
    if b >= 0.99 and a <= 0.01:
        return 0.0
    if abs(a - 0.5) < 0.01 and abs(b - 0.5) < 0.01:
        return 0.5
    return None


def favourite(p0, payout0):
    """Side, price and payout of the favourite (the outcome priced at or above one half)."""
    if p0 >= 0.5:
        return 0, p0, payout0
    return 1, 1.0 - p0, (1.0 - payout0) if payout0 is not None else None


def neg_risk_sums(books):
    """Executable sums over the YES books of one neg-risk event.

    `books` is a list of {'asks': [(price, size)...], 'bids': [...]} for every member that can win. Returns the sum of
    best asks (None if any member has no ask: the basket cannot be bought), the sum of best bids (None if any member
    has no bid), and the number of complete baskets available at the best levels (the thinnest member's size).
    Buying one YES of every member costs sum(asks) and pays exactly 1; buying one NO of every member costs
    sum(1 - bid) = n - sum(bids) and pays n - 1, so it profits when sum(bids) > 1.
    """
    asks, bids, ask_sz, bid_sz = [], [], [], []
    for b in books:
        a = sorted(b.get('asks') or [])
        d = sorted(b.get('bids') or [], reverse=True)
        if a:
            asks.append(a[0][0])
            ask_sz.append(a[0][1])
        else:
            asks.append(None)
        if d:
            bids.append(d[0][0])
            bid_sz.append(d[0][1])
        else:
            bids.append(None)
    sa = None if (not asks or any(x is None for x in asks)) else sum(asks)
    sb = None if (not bids or any(x is None for x in bids)) else sum(bids)
    return {'n': len(books), 'sum_ask': sa, 'sum_bid': sb,
            'ask_baskets': min(ask_sz) if (sa is not None and ask_sz) else 0.0,
            'bid_baskets': min(bid_sz) if (sb is not None and bid_sz) else 0.0}


def basket_fill(books, side='ask', rates=None, max_sets=1e9):
    """Walk every member's book together, buying one share of each per set, while a set is still profitable.

    side='ask': buy YES of every member (pays 1 per set). side='bid': buy NO of every member at 1 - bid (pays n - 1).
    Fees are charged per share at the fill price (`rates` per member, default zero). Returns sets bought, cost, payout
    and profit — the executable size of the arbitrage, not just its top-of-book sign.
    """
    n = len(books)
    rates = rates or [0.0] * n
    levels = []
    for b in books:
        if side == 'ask':
            lv = sorted([(p, s) for p, s in (b.get('asks') or [])])
        else:
            lv = sorted([(1.0 - p, s) for p, s in (b.get('bids') or [])])
        if not lv:
            return {'sets': 0.0, 'cost': 0.0, 'payout': 0.0, 'profit': 0.0}
        levels.append([list(x) for x in lv])
    pay_per_set = 1.0 if side == 'ask' else float(n - 1)
    idx = [0] * n
    sets = cost = 0.0
    while sets < max_sets:
        if any(idx[i] >= len(levels[i]) for i in range(n)):
            break
        prices = [levels[i][idx[i]][0] for i in range(n)]
        unit = sum(p + fee_per_share(rates[i], p) for i, p in enumerate(prices))
        if unit >= pay_per_set:
            break
        q = min(levels[i][idx[i]][1] for i in range(n))
        q = min(q, max_sets - sets)
        sets += q
        cost += q * unit
        for i in range(n):
            levels[i][idx[i]][1] -= q
            if levels[i][idx[i]][1] <= 1e-9:
                idx[i] += 1
    return {'sets': sets, 'cost': cost, 'payout': sets * pay_per_set, 'profit': sets * pay_per_set - cost}


# ------------------------------------------------------------------------------------------------- universe

KEEP = ['id', 'conditionId', 'question', 'slug', 'startDate', 'endDate', 'closedTime', 'umaEndDate',
        'umaResolutionStatus', 'negRisk', 'negRiskRequestID', 'negRiskOther', 'volumeNum', 'liquidityNum',
        'feesEnabled', 'feeType', 'category', 'automaticallyResolved', 'orderPriceMinTickSize', 'groupItemTitle',
        'createdAt', 'acceptingOrdersTimestamp', 'gameStartTime', 'sportsMarketType', 'umaBond', 'restricted',
        'archived', 'cyom', 'closed', 'active', 'lastTradePrice', 'bestAsk', 'bestBid', 'spread', 'enableOrderBook',
        'acceptingOrders']


def compact_market(m):
    ev = (m.get('events') or [{}])[0] or {}
    out = {k: m.get(k) for k in KEEP}
    out['outcomes'] = jload(m.get('outcomes'), [])
    out['outcomePrices'] = [fnum(x) for x in jload(m.get('outcomePrices'), [])]
    out['clobTokenIds'] = jload(m.get('clobTokenIds'), [])
    out['umaResolutionStatuses'] = jload(m.get('umaResolutionStatuses'), [])
    out['event_id'] = ev.get('id')
    out['event_slug'] = ev.get('slug')
    out['event_title'] = ev.get('title')
    out['event_neg_risk'] = ev.get('negRisk')
    out['event_augmented'] = ev.get('negRiskAugmented')
    out['tags'] = [t.get('label') for t in (m.get('tags') or []) if isinstance(t, dict)]
    out['cat'] = categorize(out['tags'], m.get('question'), m.get('category'))
    return out


def cmd_universe(args):
    """Keyset-paginate every closed market with volume >= floor; raw pages are cached, so a rerun resumes."""
    out = Path(args.out)
    raw = out / 'raw' / 'markets'
    raw.mkdir(parents=True, exist_ok=True)
    http = Http(interval=args.interval)
    t0 = time.time()
    cursor, page = None, 0
    state = out / 'raw' / 'markets_cursor.json'
    if state.exists():
        st = json.loads(state.read_text())
        cursor, page = st.get('cursor'), st.get('page', 0)
    while True:
        q = {'limit': 100, 'closed': 'true', 'volume_num_min': args.min_volume, 'include_tag': 'true'}
        if cursor:
            q['after_cursor'] = cursor
        d = http.request(GAMMA + '/markets/keyset?' + urllib.parse.urlencode(q))
        if '__error__' in d:
            print(json.dumps({'error': d['__error__'], 'page': page}), flush=True)
            time.sleep(5)
            continue
        ms = d.get('markets') or []
        if ms:
            write_gz(raw / ('page_%05d.json.gz' % page), [compact_market(m) for m in ms])
            page += 1
        cursor = d.get('next_cursor')
        state.write_text(json.dumps({'cursor': cursor, 'page': page}))
        if page % 50 == 0:
            print(json.dumps({'page': page, 'last_closed': ms[-1].get('closedTime') if ms else None,
                              'elapsed_s': round(time.time() - t0), **http.stats()}), flush=True)
        if not cursor or not ms:
            break
    rows, seen = [], set()
    for p in sorted(raw.glob('page_*.json.gz')):
        for m in read_gz(p):
            if m['id'] in seen:
                continue
            seen.add(m['id'])
            rows.append(m)
    write_gz(out / 'raw' / 'universe.json.gz', rows)   # 106 MB: under raw/, which git ignores
    update_manifest(out, 'universe', {
        'fetched_at': utc(t0), 'finished_at': utc(), 'source': GAMMA + '/markets/keyset',
        'filters': {'closed': True, 'volume_num_min': args.min_volume, 'include_tag': True},
        'pages': page, 'markets': len(rows), 'http': http.stats(), 'seconds': round(time.time() - t0, 1)})
    print(json.dumps({'markets': len(rows), 'pages': page}))
    return 0


def load_universe(out):
    return read_gz(Path(out) / 'raw' / 'universe.json.gz')


# ------------------------------------------------------------------------------------------------- sampling

def vol_bucket(v):
    v = v or 0.0
    if v >= 1e6:
        return '1m+'
    if v >= 1e5:
        return '100k-1m'
    return '10k-100k'


def eligible_binary(m):
    """A two-outcome CLOB market with a definite resolution and the timestamps the backtest needs."""
    if len(m.get('outcomes') or []) != 2 or len(m.get('clobTokenIds') or []) != 2:
        return False
    if m.get('enableOrderBook') is False:
        return False
    if binary_payout(m) is None:
        return False
    if parse_ts(m.get('closedTime')) is None or parse_ts(m.get('endDate')) is None:
        return False
    return True


def start_ts(m):
    for k in ('acceptingOrdersTimestamp', 'startDate', 'createdAt'):
        t = parse_ts(m.get(k))
        if t:
            return t
    return None


def sample_plan(universe, targets):
    """Inclusion probability per (category, volume bucket): everything when the stratum is under its target,
    otherwise target / count. Returns {(cat, bucket): (count, prob)}."""
    counts = collections.Counter((m['cat'], vol_bucket(m.get('volumeNum'))) for m in universe if eligible_binary(m))
    plan = {}
    for (cat, b), n in counts.items():
        tgt = targets.get(b, 1000)
        plan[(cat, b)] = (n, min(1.0, tgt / n))
    return plan


def draw_sample(universe, plan):
    rows = []
    for m in universe:
        if not eligible_binary(m):
            continue
        key = (m['cat'], vol_bucket(m.get('volumeNum')))
        n, prob = plan[key]
        if stable_u('pm-sample:' + str(m['id'])) < prob:
            rows.append({'id': m['id'], 'weight': 1.0 / prob, 'stratum': '%s|%s' % key})
    return rows


# ------------------------------------------------------------------------------------------------- collect

def price_path(out, mid, kind):
    return Path(out) / 'raw' / 'prices' / str(mid)[-2:] / ('%s_%s.json.gz' % (mid, kind))


def fetch_prices(http, token, coarse=True, start=None, end=None, fidelity=60):
    if coarse:
        q = {'market': token, 'interval': 'max', 'fidelity': 720}
    else:
        q = {'market': token, 'startTs': int(start), 'endTs': int(end), 'fidelity': fidelity}
    d = http.request(CLOB + '/prices-history?' + urllib.parse.urlencode(q))
    if '__error__' in d:
        return None, d['__error__']
    return [[int(x['t']), float(x['p'])] for x in d.get('history') or []], None


def fine_window(m):
    """Up to the last 14.5 days before the close (the endpoint rejects longer windows), hourly; 5-minute resolution
    for markets that lived under two days (the short-dated families)."""
    close = parse_ts(m['closedTime'])
    st = start_ts(m)
    if st is None or st >= close:
        st = close - 14.5 * DAY   # 2021-23 markets carry a 2023 re-listing date after their own close
    end = close + HOUR
    s = max(st - HOUR, end - 14.5 * DAY)
    fid = 60 if (end - s) > 2 * DAY else 5
    return s, end, fid


def cmd_collect(args):
    out = Path(args.out)
    uni = load_universe(out)
    by_id = {m['id']: m for m in uni}
    targets = {'1m+': args.target_1m, '100k-1m': args.target_100k, '10k-100k': args.target_10k}
    plan = sample_plan(uni, targets)
    sample = draw_sample(uni, plan)
    write_json(out / 'sample.json', {'targets': targets,
                                     'plan': {'%s|%s' % k: {'count': v[0], 'prob': v[1]} for k, v in plan.items()},
                                     'markets': sample})
    print(json.dumps({'universe': len(uni), 'eligible': sum(v[0] for v in plan.values()), 'sample': len(sample)}),
          flush=True)
    http = Http(interval=args.interval)
    t0 = time.time()

    def one(row):
        m = by_id[row['id']]
        tok = m['clobTokenIds'][0]
        rec = {'id': m['id'], 'coarse': None, 'fine': None, 'err': None}
        pc = price_path(out, m['id'], 'c')
        if not pc.exists():
            s, err = fetch_prices(http, tok, coarse=True)
            if s is not None:
                write_gz(pc, s)
            rec['err'] = err
        pf = price_path(out, m['id'], 'f')
        if not pf.exists():
            a, b, fid = fine_window(m)
            s, err = fetch_prices(http, tok, coarse=False, start=a, end=b, fidelity=fid)
            if s is not None:
                write_gz(pf, s)
            rec['err'] = rec['err'] or err
        return rec

    errs = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for rec in ex.map(one, sample):
            done += 1
            if rec['err']:
                errs.append(rec)
            if done % 500 == 0:
                print(json.dumps({'done': done, 'of': len(sample), 'errors': len(errs),
                                  'elapsed_s': round(time.time() - t0), **http.stats()}), flush=True)
    update_manifest(out, 'collect', {
        'finished_at': utc(), 'sample': len(sample), 'targets': targets, 'errors': len(errs),
        'error_examples': errs[:10], 'http': http.stats(), 'seconds': round(time.time() - t0, 1),
        'source': CLOB + '/prices-history (coarse: interval=max fidelity=720; fine: last 14.5 days, fidelity 60 or 5)'})
    print(json.dumps({'done': done, 'errors': len(errs), **http.stats()}))
    return 0


# ------------------------------------------------------------------------------------------------- neg-risk history

def neg_risk_events(universe, min_volume):
    ev = collections.defaultdict(list)
    for m in universe:
        if (m.get('negRisk') or m.get('event_neg_risk')) and m.get('event_id'):
            ev[m['event_id']].append(m)
    keep = {}
    for eid, ms in ev.items():
        vol = sum(m.get('volumeNum') or 0 for m in ms)
        if vol >= min_volume:
            keep[eid] = {'volume_in_universe': vol, 'members_in_universe': len(ms),
                         'augmented': any(m.get('event_augmented') for m in ms),
                         'title': ms[0].get('event_title')}
    return keep


def cmd_negrisk(args):
    """Every member of each sampled neg-risk event (the universe floor drops thin members, so the event is
    re-read in full), then each member's coarse YES series."""
    out = Path(args.out)
    uni = load_universe(out)
    evs = neg_risk_events(uni, args.min_event_volume)
    ids = sorted(evs, key=lambda e: -evs[e]['volume_in_universe'])
    if args.max_events:
        ids = [e for e in ids if stable_u('pm-nr:' + str(e)) < 1.0][:args.max_events]
    http = Http(interval=args.interval)
    t0 = time.time()
    raw = out / 'raw' / 'negrisk'
    raw.mkdir(parents=True, exist_ok=True)

    def one_event(eid):
        p = raw / ('event_%s.json.gz' % eid)
        if p.exists():
            return read_gz(p)
        d = http.request(GAMMA + '/events/%s' % eid)
        if '__error__' in d:
            return None
        ms = [compact_market(dict(m, events=[{k: d.get(k) for k in ('id', 'slug', 'title', 'negRisk',
                                                                       'negRiskAugmented')}]))
              for m in d.get('markets') or []]
        rec = {'id': eid, 'title': d.get('title'), 'negRisk': d.get('negRisk'),
               'augmented': d.get('negRiskAugmented'), 'closedTime': d.get('closedTime'), 'markets': ms}
        write_gz(p, rec)
        return rec

    events = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for rec in ex.map(one_event, ids):
            if rec:
                events.append(rec)
    toks = []
    for e in events:
        for m in e['markets']:
            if m.get('clobTokenIds'):
                toks.append((m['id'], m['clobTokenIds'][0]))

    def one_tok(x):
        mid, tok = x
        pc = price_path(out, mid, 'c')
        if pc.exists():
            return None
        s, err = fetch_prices(http, tok, coarse=True)
        if s is not None:
            write_gz(pc, s)
        return err

    errs = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, err in enumerate(ex.map(one_tok, toks), 1):
            errs += 1 if err else 0
            if i % 1000 == 0:
                print(json.dumps({'tokens': i, 'of': len(toks), 'errors': errs, **http.stats()}), flush=True)
    update_manifest(out, 'negrisk', {'finished_at': utc(), 'events': len(events), 'member_tokens': len(toks),
                                     'min_event_volume': args.min_event_volume, 'errors': errs,
                                     'http': http.stats(), 'seconds': round(time.time() - t0, 1)})
    print(json.dumps({'events': len(events), 'tokens': len(toks), 'errors': errs}))
    return 0


# ------------------------------------------------------------------------------------------------- live books

def parse_book(b):
    asks = [(float(x['price']), float(x['size'])) for x in b.get('asks') or []]
    bids = [(float(x['price']), float(x['size'])) for x in b.get('bids') or []]
    return {'asks': sorted(asks), 'bids': sorted(bids, reverse=True), 'tick': fnum(b.get('tick_size')),
            'ts': b.get('timestamp')}


def fetch_books(http, tokens, batch=40):
    books = {}
    for i in range(0, len(tokens), batch):
        chunk = tokens[i:i + batch]
        d = http.request(CLOB + '/books', body=[{'token_id': t} for t in chunk])
        if isinstance(d, dict) and '__error__' in d:
            continue
        for b in d or []:
            books[b.get('asset_id')] = parse_book(b)
    return books


def paginate_events(http, params, max_pages=400):
    """Every event matching `params` through the keyset endpoint (offset pagination stops at ~2,100 rows).

    Note: gamma ignores a `negRisk` filter on events (both endpoints return a mix), so neg-risk membership is decided
    from each event's own `negRisk` field after the fetch."""
    rows, cursor = [], None
    for _ in range(max_pages):
        q = dict(params, limit=100)
        if cursor:
            q['after_cursor'] = cursor
        d = http.request(GAMMA + '/events/keyset?' + urllib.parse.urlencode(q))
        if not isinstance(d, dict) or '__error__' in d:
            break
        ev = d.get('events') or []
        rows.extend(ev)
        cursor = d.get('next_cursor')
        if not cursor or not ev:
            break
    return rows


def paginate_markets_keyset(http, params, max_pages=200):
    rows, cursor = [], None
    for _ in range(max_pages):
        q = dict(params, limit=100)
        if cursor:
            q['after_cursor'] = cursor
        d = http.request(GAMMA + '/markets/keyset?' + urllib.parse.urlencode(q))
        if not isinstance(d, dict) or '__error__' in d:
            break
        ms = d.get('markets') or []
        rows.extend(ms)
        cursor = d.get('next_cursor')
        if not cursor or not ms:
            break
    return rows


def cmd_live(args):
    """One snapshot: every active neg-risk event's YES books, and the books of every binary favourite in the bands
    the backtest trades (ending within the next week, or past its scheduled end and not yet resolved)."""
    out = Path(args.out)
    http = Http(interval=args.interval)
    t0 = time.time()
    now = time.time()
    events = paginate_events(http, {'closed': 'false', 'active': 'true'})
    nr = []
    for e in events:
        if e.get('negRisk') is not True:
            continue
        ms = []
        for m in e.get('markets') or []:
            if m.get('negRisk') is not True:
                continue
            toks = jload(m.get('clobTokenIds'), [])
            outs = jload(m.get('outcomes'), [])
            if not toks:
                continue
            ms.append({'id': m.get('id'), 'question': m.get('question'), 'yes': toks[0], 'no': toks[1] if len(toks) > 1 else None,
                       'outcome0': outs[0] if outs else None, 'active': m.get('active'), 'closed': m.get('closed'),
                       'accepting': m.get('acceptingOrders'), 'negRiskOther': m.get('negRiskOther'),
                       'groupItemTitle': m.get('groupItemTitle'), 'feesEnabled': m.get('feesEnabled'),
                       'feeType': m.get('feeType'), 'bestBid': fnum(m.get('bestBid')),
                       'bestAsk': fnum(m.get('bestAsk')), 'volume': fnum(m.get('volumeNum')),
                       'endDate': m.get('endDate')})
        nr.append({'id': e.get('id'), 'title': e.get('title'), 'augmented': e.get('negRiskAugmented'),
                   'negRisk': e.get('negRisk'), 'events_scanned': len(events),
                   'enableNegRisk': e.get('enableNegRisk'), 'volume': fnum(e.get('volume')),
                   'liquidity': fnum(e.get('liquidity')), 'endDate': e.get('endDate'),
                   'tags': [t.get('label') for t in e.get('tags') or [] if isinstance(t, dict)], 'markets': ms})
    yes_tokens = sorted({m['yes'] for e in nr for m in e['markets']
                         if m['active'] and not m['closed'] and m['accepting']})
    books = fetch_books(http, yes_tokens)
    # The sweep reads books in batches over minutes, so an event whose members sit in different batches is not
    # priced at one instant; on a live game that alone manufactures "arbitrage". Every candidate (asks summing under
    # one or bids over one) is re-read with all of its members in a single request, seconds later.
    confirm = {}
    for e in nr:
        live = [m for m in e['markets'] if m['active'] and not m['closed'] and m['accepting']]
        if len(live) < 2 or any(m['yes'] not in books for m in live):
            continue
        sm = neg_risk_sums([books[m['yes']] for m in live])
        if (sm['sum_ask'] is not None and sm['sum_ask'] < 1) or (sm['sum_bid'] is not None and sm['sum_bid'] > 1):
            t_req = time.time()
            cb = fetch_books(http, [m['yes'] for m in live], batch=len(live))
            confirm[e['id']] = {'at': utc(t_req), 'books': cb}
    # binary favourites
    lo = utc(now - 3 * DAY).replace('+00:00', 'Z')
    hi = utc(now + 7 * DAY).replace('+00:00', 'Z')
    act = paginate_markets_keyset(http, {'closed': 'false', 'active': 'true', 'end_date_min': lo,
                                         'end_date_max': hi, 'include_tag': 'true'})
    fav = []
    for m in act:
        cm = compact_market(m)
        if len(cm['outcomes']) != 2 or len(cm['clobTokenIds']) != 2 or not m.get('acceptingOrders'):
            continue
        bb, ba = fnum(m.get('bestBid')), fnum(m.get('bestAsk'))
        if bb is None or ba is None or ba <= 0:
            continue
        mid = (bb + ba) / 2.0
        side = 0 if mid >= 0.5 else 1
        pf = mid if side == 0 else 1.0 - mid
        if pf < 0.85:
            continue
        cm['fav_side'] = side
        cm['fav_mid_gamma'] = pf
        fav.append(cm)
    fav_tokens = sorted({m['clobTokenIds'][m['fav_side']] for m in fav})
    fbooks = fetch_books(http, fav_tokens)
    snap = {'at': utc(now), 'events_scanned': len(events), 'neg_risk_events': nr, 'books': books, 'confirm': confirm, 'favourites': fav, 'fav_books': fbooks,
            'http': http.stats(), 'seconds': round(time.time() - t0, 1)}
    p = out / 'raw' / 'live' / ('snap_%d.json.gz' % int(now))
    write_gz(p, snap)
    print(json.dumps({'at': snap['at'], 'neg_risk_events': len(nr), 'yes_books': len(books), 'confirmed': len(confirm),
                      'favourites': len(fav), 'fav_books': len(fbooks), **http.stats(),
                      'seconds': snap['seconds']}))
    return 0


# ------------------------------------------------------------------------------------------------- analysis: live

def book_side_stats(book, side_price_cap=0.999, within=0.01):
    """Best ask/bid, mid, half-spread and the ask depth (USD) within `within` of the best ask."""
    asks, bids = book.get('asks') or [], book.get('bids') or []
    if not asks or not bids:
        return None
    ba, bb = asks[0][0], bids[0][0]
    mid = (ba + bb) / 2.0
    depth = sum(p * s for p, s in asks if p <= min(side_price_cap, ba + within + 1e-12))
    shares = sum(s for p, s in asks if p <= min(side_price_cap, ba + within + 1e-12))
    return {'ask': ba, 'bid': bb, 'mid': mid, 'half_spread': ba - mid, 'ask_depth_usd_1c': depth,
            'ask_shares_1c': shares, 'ask_size_best': asks[0][1], 'ask_depth_usd_best': ba * asks[0][1],
            'tick': book.get('tick')}


def band_of(p, bands=None):
    for lo, hi in (bands or BANDS[:4]):
        if lo <= p < hi:
            return '%.2f-%.3f' % (lo, hi)
    return None


def analyze_live(out):
    snaps = sorted((Path(out) / 'raw' / 'live').glob('snap_*.json.gz'))
    res = {'snapshots': [], 'half_spread': {}, 'fav_depth': {}, 'neg_risk': []}
    hs = collections.defaultdict(list)
    depth = collections.defaultdict(list)
    depth_best = collections.defaultdict(list)
    nr_rows = []
    for sp in snaps:
        s = read_gz(sp)
        at = s['at']
        # favourites
        nfav = 0
        for m in s['favourites']:
            tok = m['clobTokenIds'][m['fav_side']]
            b = s['fav_books'].get(tok)
            if not b:
                continue
            st = book_side_stats(b)
            if not st:
                continue
            band = band_of(st['mid'])
            if not band:
                continue
            nfav += 1
            past_end = (parse_ts(m.get('endDate')) or 0) < parse_ts(at)
            keys = [(m['cat'], band), ('all', band)] + ([('past_end', band)] if past_end else [])
            for key in keys:
                hs[key].append(st['half_spread'])
                depth[key].append(st['ask_depth_usd_1c'])
                depth_best[key].append(st['ask_depth_usd_best'])
        # neg-risk events (the first snapshot predates the negRisk filter: its "events" include date ladders)
        nev = 0
        for e in (s['neg_risk_events'] if 'events_scanned' in s else []):
            live = [m for m in e['markets'] if m['active'] and not m['closed'] and m['accepting']]
            if len(live) < 2:
                continue
            # a member that is neither closed nor tradable (a suspended market, a placeholder) can still win, so a
            # basket of the tradable members is not exhaustive
            incomplete = any(not m['closed'] and not (m['active'] and m['accepting']) for m in e['markets'])
            bk = [s['books'].get(m['yes']) for m in live]
            if any(b is None for b in bk):
                continue
            nev += 1
            sweep = neg_risk_sums(bk)
            conf = (s.get('confirm') or {}).get(e['id'])
            confirmed = False
            if conf and all(m['yes'] in conf['books'] for m in live):
                bk = [conf['books'][m['yes']] for m in live]
                confirmed = True
            sums = neg_risk_sums(bk)
            cat = categorize(e.get('tags'), e.get('title'))
            rates = [fee_rate(cat, e.get('tags'))] * len(live)
            fa = basket_fill(bk, 'ask', rates) if (sums['sum_ask'] is not None and sums['sum_ask'] < 1) else None
            fb = basket_fill(bk, 'bid', rates) if (sums['sum_bid'] is not None and sums['sum_bid'] > 1) else None
            ends = [parse_ts(m.get('endDate')) for m in live if parse_ts(m.get('endDate'))]
            end = max(ends) if ends else parse_ts(e.get('endDate'))
            days = max(1.0, (end - parse_ts(at)) / DAY) if end else None
            for f in (fa, fb):
                if f and f['cost'] > 0:
                    f['ret'] = f['profit'] / f['cost']
                    f['days_to_end'] = days
                    f['ann_excess'] = (f['ret'] * 365.0 / days - SSR) if days else None
            nr_rows.append({'at': at, 'event': e['id'], 'title': e['title'], 'augmented': bool(e.get('augmented')),
                            'members_live': len(live), 'members_total': len(e['markets']), 'incomplete': incomplete,
                            'cat': cat, 'has_other': any(m.get('negRiskOther') for m in live),
                            'volume': e.get('volume'), 'days_to_end': days,
                            'sum_ask': sums['sum_ask'], 'sum_bid': sums['sum_bid'],
                            'sweep_sum_ask': sweep['sum_ask'], 'sweep_sum_bid': sweep['sum_bid'],
                            'confirmed_read': confirmed, 'has_confirm_field': 'confirm' in s,
                            'ask_baskets_top': sums['ask_baskets'], 'bid_baskets_top': sums['bid_baskets'],
                            'buy_all_yes': fa, 'buy_all_no': fb})
        res['snapshots'].append({'at': at, 'favourites_priced': nfav, 'neg_risk_events_priced': nev})
    for key, v in hs.items():
        res['half_spread']['%s|%s' % key] = {'n': len(v), 'median': statistics.median(v),
                                             'p75': sorted(v)[int(0.75 * (len(v) - 1))], 'mean': sum(v) / len(v)}
    for key, v in depth.items():
        vb = depth_best[key]
        res['fav_depth']['%s|%s' % key] = {'n': len(v), 'median_usd': statistics.median(v),
                                           'p25_usd': sorted(v)[int(0.25 * (len(v) - 1))],
                                           'p75_usd': sorted(v)[int(0.75 * (len(v) - 1))], 'sum_usd': sum(v),
                                           'median_usd_best': statistics.median(vb), 'sum_usd_best': sum(vb)}
    res['neg_risk'] = nr_rows
    return res


def half_spread_for(live, cat, p, which='median'):
    band = band_of(p)
    if band is None:
        band = band_of(min(0.994, max(0.85, p)))
    for key in ('%s|%s' % (cat, band), 'all|%s' % band):
        r = live['half_spread'].get(key)
        if r and r['n'] >= 5:
            return r[which]
    return 0.005


# ------------------------------------------------------------------------------------------------- analysis: history

def load_series(out, mid, kind):
    p = price_path(out, mid, kind)
    if not p.exists():
        return None
    s = read_gz(p)
    s.sort()
    return s


def price_at(coarse, fine, t):
    """Fine (hourly or 5-minute) where it covers t, coarse (12-hourly) otherwise. Points appear only when the price
    moves, so staleness is bounded generously; a point older than 3 days is not a price."""
    if fine and fine[0][0] <= t:
        p = as_of(fine, t, max_stale=3 * DAY)
        if p is not None:
            return p, 'fine'
    if coarse:
        p = as_of(coarse, t, max_stale=3 * DAY)
        if p is not None:
            return p, 'coarse'
    return None, None


def build_trades(out, uni_by_id, sample):
    """Strategy A entries at each horizon and strategy C entries at each threshold, one row per (market, variant)."""
    A, Cr, meta = [], [], collections.Counter()
    for row in sample:
        m = uni_by_id[row['id']]
        pay0 = binary_payout(m)
        close, end, st = parse_ts(m['closedTime']), parse_ts(m['endDate']), start_ts(m)
        coarse, fine = load_series(out, m['id'], 'c'), load_series(out, m['id'], 'f')
        if not coarse and not fine:
            meta['no_series'] += 1
            continue
        meta['with_series'] += 1
        disputed = any('disput' in str(x).lower() for x in (m.get('umaResolutionStatuses') or []))
        base = {'id': m['id'], 'event': m.get('event_id') or m['id'], 'cat': m['cat'], 'w': row['weight'],
                'vb': vol_bucket(m.get('volumeNum')), 'close': close, 'end': end, 'neg_risk': bool(m.get('negRisk')),
                'disputed': disputed, 'fifty': pay0 == 0.5, 'rate': fee_rate(m['cat'], m.get('tags')),
                'volume': m.get('volumeNum')}
        for h, secs in HORIZONS.items():
            t = end - secs
            if st is None or t < st or t > close - 600:
                continue
            p0, src = price_at(coarse, fine, t)
            if p0 is None or p0 <= 0 or p0 >= 1:
                continue
            side, p, pay = favourite(p0, pay0)
            A.append(dict(base, h=h, t=t, p=p, pay=pay, side=side, src=src))
        if fine:
            for th in C_THRESHOLDS:
                for t, p0 in fine:
                    if t < end or t > close - 60:
                        continue
                    side, p, pay = favourite(p0, pay0)
                    if p >= th:
                        if p >= 0.9995:
                            break  # a midpoint at the cap: nothing left to buy
                        Cr.append(dict(base, th=th, t=t, p=p, pay=pay, side=side, src='fine'))
                        break
    return A, Cr, meta


def daily_series(trades, rets, t_lo, t_hi, ssr=SSR):
    """Daily return series on average deployed capital: P&L lands on the close day, capital is the weighted stake
    open each day. Returns (series, avg_capital, sum_w_days)."""
    d0 = int(t_lo // DAY)
    n = int(t_hi // DAY) - d0 + 1
    pnl = [0.0] * n
    cap = [0.0] * n
    for tr, r in zip(trades, rets):
        a = int(tr['t'] // DAY) - d0
        b = int(tr['close'] // DAY) - d0
        a, b = max(0, a), min(n - 1, b)
        if b >= 0 and b < n:
            pnl[b] += tr['w'] * r
        for d in range(max(0, a), b + 1):
            cap[d] += tr['w']
    k = sum(cap) / n if n else 0.0
    if k <= 0:
        return [], 0.0, 0.0
    return [x / k - ssr / 365.0 for x in pnl], k, sum(cap)


def summarize(trades, rets, label=''):
    """Weighted trade-level summary: hit rate, mean return, annualised return per capital-day and excess over SSR."""
    if not trades:
        return {'n': 0}
    w = [t['w'] for t in trades]
    days = [max(1.0 / 24, (t['close'] - t['t']) / DAY) for t in trades]
    sw = sum(w)
    sr = sum(wi * r for wi, r in zip(w, rets))
    sd = sum(wi * d for wi, d in zip(w, days))
    wins = sum(wi for wi, t in zip(w, trades) if t['pay'] == 1.0)
    losses = sum(wi for wi, t in zip(w, trades) if t['pay'] == 0.0)
    ann = annualised(sr, sd)
    events = len({t['event'] for t in trades})
    return {'n': len(trades), 'events': events, 'weighted_n': sw, 'win_rate': wins / sw, 'loss_rate': losses / sw,
            'fifty_rate': 1 - (wins + losses) / sw, 'mean_price': sum(wi * t['p'] for wi, t in zip(w, trades)) / sw,
            'mean_return': sr / sw, 'mean_days': sd / sw, 'ann_return': ann,
            'ann_excess': (ann - SSR) if ann is not None else None,
            'worst_return': min(rets), 'median_days': statistics.median(days)}


def cluster_bootstrap(trades, rets, n=1000, seed=11):
    """Resample events (all of an event's trades together) and recompute the annualised excess return: neg-risk
    members and same-day entries are not independent bets."""
    by = collections.defaultdict(list)
    for tr, r in zip(trades, rets):
        by[tr['event']].append((tr['w'], r, max(1.0 / 24, (tr['close'] - tr['t']) / DAY)))
    keys = list(by)
    if len(keys) < 5:
        return {'lo': None, 'hi': None, 'p_le_0': None}
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sr = sd = 0.0
        for _ in range(len(keys)):
            for w, r, d in by[keys[rng.randrange(len(keys))]]:
                sr += w * r
                sd += w * d
        vals.append(sr / sd * 365.0 - SSR if sd > 0 else 0.0)
    vals.sort()
    return {'lo': vals[int(0.025 * (n - 1))], 'hi': vals[int(math.ceil(0.975 * (n - 1)))],
            'p_le_0': sum(1 for v in vals if v <= 0) / n}


def calibration(trades, horizon):
    rows = []
    sel = [t for t in trades if t['h'] == horizon and not t['fifty']]
    for lo, hi in zip(PRICE_BINS[:-1], PRICE_BINS[1:]):
        b = [t for t in sel if lo <= t['p'] < hi]
        if not b:
            continue
        sw = sum(t['w'] for t in b)
        k = sum(t['w'] for t in b if t['pay'] == 1.0)
        neff = sw * sw / sum(t['w'] ** 2 for t in b)      # Kish: unequal sampling weights shrink the sample
        lo_ci, hi_ci = wilson(k / sw * neff, neff)
        rows.append({'bin': '%.3f-%.3f' % (lo, hi), 'n': len(b), 'n_eff': neff,
                     'mean_price': sum(t['w'] * t['p'] for t in b) / sw,
                     'win_rate': k / sw, 'ci_lo': lo_ci, 'ci_hi': hi_ci,
                     'edge_pp': 100 * (k / sw - sum(t['w'] * t['p'] for t in b) / sw)})
    return rows


def logistic_fit(x, y, w, iters=50):
    """Weighted logistic regression of y on [1, x] by Newton-Raphson; returns (a, b) or None if it fails."""
    a = b = 0.0
    for _ in range(iters):
        ga = gb = haa = hab = hbb = 0.0
        for xi, yi, wi in zip(x, y, w):
            z = a + b * xi
            pz = 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z))))
            r = yi - pz
            v = pz * (1 - pz)
            ga += wi * r
            gb += wi * r * xi
            haa += wi * v
            hab += wi * v * xi
            hbb += wi * v * xi * xi
        det = haa * hbb - hab * hab
        if det <= 1e-12:
            return None
        da = (hbb * ga - hab * gb) / det
        db = (haa * gb - hab * ga) / det
        a += da
        b += db
        if abs(da) + abs(db) < 1e-9:
            break
    return a, b


def calibration_slope(trades, horizon, n_boot=200, seed=3):
    """logit(P(win)) = a + b logit(price) over favourites at one horizon. b > 1: the market is under-confident
    (favourites underpriced, the favourite-longshot bias); b < 1: over-confident. Event-clustered bootstrap CI."""
    sel = [t for t in trades if t['h'] == horizon and not t['fifty'] and 0.5 <= t['p'] < 0.9995]
    if len(sel) < 50:
        return None
    lg = lambda q: math.log(q / (1 - q))
    fit = logistic_fit([lg(t['p']) for t in sel], [t['pay'] for t in sel], [t['w'] for t in sel])
    if fit is None:
        return None
    by = collections.defaultdict(list)
    for t in sel:
        by[t['event']].append(t)
    keys = list(by)
    rng = random.Random(seed)
    bs = []
    for _ in range(n_boot):
        smp = [t for _ in keys for t in by[keys[rng.randrange(len(keys))]]]
        f = logistic_fit([lg(t['p']) for t in smp], [t['pay'] for t in smp], [t['w'] for t in smp], iters=25)
        if f:
            bs.append(f[1])
    bs.sort()
    return {'n': len(sel), 'a': fit[0], 'b': fit[1],
            'b_lo': bs[int(0.025 * (len(bs) - 1))] if bs else None,
            'b_hi': bs[int(math.ceil(0.975 * (len(bs) - 1)))] if bs else None}


def returns_for(trades, live, spread='median', fees='current'):
    out = []
    for t in trades:
        hs = 0.0 if spread == 'zero' else half_spread_for(live, t['cat'], t['p'], spread)
        rate = t['rate'] if fees == 'current' else 0.0
        out.append(trade_return(t['p'], t['pay'], hs, rate))
    return out


def run_protocol(variants, live, cutoff_ts, t_lo, t_hi):
    """Choose on trades whose market closed before the cutoff, test on trades entered after it; trades that
    straddle the cutoff belong to neither part. Each variant's series is normalised by its own part's capital."""
    series, parts = {}, {}
    n_is = None
    for name, trades in variants.items():
        ins = [t for t in trades if t['close'] < cutoff_ts]
        oos = [t for t in trades if t['t'] >= cutoff_ts]
        r_in, r_oos = returns_for(ins, live), returns_for(oos, live)
        s_in, _, _ = daily_series(ins, r_in, t_lo, cutoff_ts - 1)
        s_oos, _, _ = daily_series(oos, r_oos, cutoff_ts, t_hi)
        if not s_in:
            s_in = [0.0] * (int((cutoff_ts - 1) // DAY) - int(t_lo // DAY) + 1)
        if not s_oos:
            s_oos = [0.0] * (int(t_hi // DAY) - int(cutoff_ts // DAY) + 1)
        n_is = len(s_in)
        series[name] = s_in + s_oos
        parts[name] = {'in': summarize(ins, r_in), 'oos': summarize(oos, r_oos),
                       'oos_cluster_ci': cluster_bootstrap(oos, r_oos) if oos else None,
                       'in_cluster_ci': cluster_bootstrap(ins, r_in) if ins else None}
    frac = n_is / len(next(iter(series.values())))
    sel = B.choose_then_test(series, frac=frac, periods_per_year=365, key='sharpe')
    return sel, parts, series, n_is


def analyze_negrisk_history(out, uni):
    raw = Path(out) / 'raw' / 'negrisk'
    rows = []
    for p in sorted(raw.glob('event_*.json.gz')):
        e = read_gz(p)
        ms = [m for m in e['markets'] if m.get('clobTokenIds')]
        if len(ms) < 2:
            continue
        pays = [binary_payout(m) for m in ms]
        resolved = all(x is not None for x in pays)
        series = {}
        for m in ms:
            s = load_series(out, m['id'], 'c')
            if s:
                series[m['id']] = s
        if len(series) < len(ms):
            rows.append({'event': e['id'], 'title': e['title'], 'members': len(ms), 'skipped': 'missing series'})
            continue
        # common 12-hour grid where every member has a price and none has closed
        t0 = max(s[0][0] for s in series.values())
        t1 = min(parse_ts(m.get('closedTime')) or 1e18 for m in ms)
        grid = []
        t = t0
        while t < t1 - 12 * HOUR and len(grid) < 2000:
            ps = [as_of(series[m['id']], t, max_stale=3 * DAY) for m in ms]
            if all(x is not None for x in ps):
                grid.append((t, sum(ps)))
            t += 12 * HOUR
        sums = [x[1] for x in grid]
        rows.append({'event': e['id'], 'title': e['title'], 'members': len(ms), 'augmented': bool(e.get('augmented')),
                     'resolved': resolved, 'payout_sum': sum(pays) if resolved else None, 'points': len(sums),
                     'sum_median': statistics.median(sums) if sums else None,
                     'sum_min': min(sums) if sums else None, 'sum_max': max(sums) if sums else None,
                     'share_below_098': (sum(1 for x in sums if x < 0.98) / len(sums)) if sums else None,
                     'share_above_102': (sum(1 for x in sums if x > 1.02) / len(sums)) if sums else None})
    return rows


def describe_universe(uni, elig):
    """Facts about the universe the note relies on, each computed here rather than by hand: what the scheduled end
    means per category, how fees rolled out, how many markets close a day, and how fast crypto price markets now
    resolve."""
    out = {'timing': {}, 'fee_rollout': {}, 'closing_per_day_2026_08_09': {}, 'crypto_price_2026_09_10': {}}
    by = collections.defaultdict(list)
    for m in elig:
        e, c, g = parse_ts(m['endDate']), parse_ts(m['closedTime']), parse_ts(m.get('gameStartTime'))
        by[m['cat']].append(((c - e) / HOUR, (e - g) / HOUR if g else None))
    for cat, rows in sorted(by.items()):
        lag = sorted(r[0] for r in rows)
        eg = sorted(r[1] for r in rows if r[1] is not None)
        out['timing'][cat] = {'n': len(rows), 'close_minus_end_h_p10': lag[int(0.1 * (len(lag) - 1))],
                              'close_minus_end_h_p50': lag[int(0.5 * (len(lag) - 1))],
                              'close_minus_end_h_p90': lag[int(0.9 * (len(lag) - 1))],
                              'closed_over_1h_before_end_share': sum(1 for x in lag if x < -1) / len(lag),
                              'with_game_start': len(eg),
                              'end_minus_game_start_h_p50': eg[int(0.5 * (len(eg) - 1))] if eg else None}
    fr = collections.defaultdict(collections.Counter)
    for m in uni:
        mo = (m.get('closedTime') or '')[:7]
        if mo < '2025-10':
            continue
        fr[mo]['all'] += 1
        fr[mo][m['cat']] += 1
        if m.get('feesEnabled'):
            fr[mo]['fees'] += 1
            fr[mo][m['cat'] + '|fees'] += 1
    for mo, c in sorted(fr.items()):
        out['fee_rollout'][mo] = dict({'all': c['fees'] / c['all']},
                                      **{cat: c[cat + '|fees'] / c[cat] for cat in FEE_RATE_BY_CAT if c[cat]})
    cnt = collections.Counter(m['cat'] for m in elig if (m.get('closedTime') or '')[:7] in ('2026-08', '2026-09'))
    out['closing_per_day_2026_08_09'] = {k: v / 61.0 for k, v in cnt.most_common()}
    cp = [m for m in elig if m['cat'] == 'crypto_price' and (m.get('closedTime') or '')[:7] in ('2026-09', '2026-10')]
    if cp:
        lag = sorted((parse_ts(m['closedTime']) - parse_ts(m['endDate'])) / HOUR for m in cp)
        out['crypto_price_2026_09_10'] = {
            'markets': len(cp), 'end_hour_utc': dict(sorted(collections.Counter(
                int((parse_ts(m['endDate']) % DAY) // HOUR) for m in cp).items())),
            'close_minus_end_h_p10': lag[int(0.1 * (len(lag) - 1))], 'close_minus_end_h_p50': lag[int(0.5 * (len(lag) - 1))],
            'close_minus_end_h_p90': lag[int(0.9 * (len(lag) - 1))],
            'automatically_resolved_share': sum(1 for m in cp if m.get('automaticallyResolved')) / len(cp)}
    return out


def midpoint_evidence(out, sample, n=400):
    """Is a prices-history point a midpoint? In a 1-cent-tick book a midpoint lands on a half cent whenever the
    spread is one tick; a last-trade price never does. Count both over a deterministic sample of hourly series."""
    ids = sorted((r['id'] for r in sample), key=lambda i: stable_u('pm-mid:' + str(i)))
    whole = half = finer = pts = series = 0
    for mid in ids:
        if series >= n:
            break
        s = load_series(out, mid, 'f')
        if not s:
            continue
        series += 1
        for _, p in s:
            pts += 1
            k = p * 1000.0
            c = round(k)
            if abs(k - c) > 1e-6:
                finer += 1
            elif c % 10 == 0:
                whole += 1
            elif c % 10 == 5:
                half += 1
            else:
                finer += 1
    return {'series': series, 'points': pts, 'whole_cent': whole, 'half_cent': half, 'other_ticks': finer}


def cmd_analyze(args):
    out = Path(args.out)
    uni = load_universe(out)
    by_id = {m['id']: m for m in uni}
    smp = json.loads((out / 'sample.json').read_text())
    sample = smp['markets']
    live = analyze_live(out)
    A, Cr, meta = build_trades(out, by_id, sample)
    start = parse_ts(args.start)
    meta['dropped_before_start_A'] = sum(1 for t in A if t['t'] < start)
    meta['dropped_before_start_C'] = sum(1 for t in Cr if t['t'] < start)
    A = [t for t in A if t['t'] >= start]
    Cr = [t for t in Cr if t['t'] >= start]
    cutoff_ts = parse_ts(args.cutoff)
    t_lo = start
    t_hi = max(t['close'] for t in A + Cr)
    res = {'generated': utc(), 'cutoff': args.cutoff, 'start': args.start, 'ssr': SSR, 'meta': dict(meta),
           'sample_size': len(sample), 'trades_A': len(A), 'trades_C': len(Cr)}

    # universe census
    elig = [m for m in uni if eligible_binary(m)]
    res['universe'] = {
        'markets': len(uni), 'eligible_binary': len(elig),
        'by_cat': dict(collections.Counter(m['cat'] for m in elig)),
        'by_year': dict(collections.Counter((m.get('closedTime') or '')[:4] for m in elig)),
        'fifty_fifty': sum(1 for m in elig if binary_payout(m) == 0.5),
        'disputed': sum(1 for m in elig if any('disput' in str(x).lower() for x in m.get('umaResolutionStatuses') or [])),
        'not_cleanly_resolved': sum(1 for m in uni if len(m.get('outcomes') or []) == 2 and binary_payout(m) is None),
        'fees_enabled': dict(collections.Counter(str(m.get('feeType')) for m in uni if m.get('feesEnabled'))),
    }

    res['descriptive'] = describe_universe(uni, elig)
    res['midpoint_evidence'] = midpoint_evidence(out, sample)

    # strategy A: calibration on the whole sample (descriptive), then the protocol, excluding the short-dated
    # up/down family which is reported on its own
    res['calibration'] = {h: calibration([t for t in A if t['cat'] != 'crypto_updown'], h) for h in HORIZONS}
    res['calibration_updown'] = {h: calibration([t for t in A if t['cat'] == 'crypto_updown'], h) for h in HORIZONS}
    res['calibration_slope'] = {}
    for part, sel in (('in_sample', [t for t in A if t['close'] < cutoff_ts]), ('out_of_sample', [t for t in A if t['t'] >= cutoff_ts])):
        core_p = [t for t in sel if t['cat'] != 'crypto_updown']
        res['calibration_slope'][part] = {h: calibration_slope(core_p, h) for h in HORIZONS}
        res['calibration_slope'][part + '_by_cat_1d'] = {
            cat: calibration_slope([t for t in sel if t['cat'] == cat], '1d', n_boot=100)
            for cat in sorted({t['cat'] for t in sel})}
    core = [t for t in A if t['cat'] != 'crypto_updown']
    variants = {}
    for h in HORIZONS:
        for lo, hi in BANDS:
            variants['A|%s|%.2f-%.3f' % (h, lo, hi)] = [t for t in core if t['h'] == h and lo <= t['p'] < hi]
    for th in C_THRESHOLDS:
        variants['C|%.2f' % th] = [t for t in Cr if t['cat'] != 'crypto_updown' and t['th'] == th]
    sel_A, parts_A, series_A, n_is = run_protocol({k: v for k, v in variants.items() if k.startswith('A|')},
                                                  live, cutoff_ts, t_lo, t_hi)
    sel_C, parts_C, series_C, _ = run_protocol({k: v for k, v in variants.items() if k.startswith('C|')},
                                               live, cutoff_ts, t_lo, t_hi)
    # C split by category. Added after the pooled C result was seen (disclosed in the note): the category decides
    # whether the scheduled end is the moment the outcome becomes known (a crypto price print) or merely a date
    # after which the result is still being counted (elections) or the game is still being played (sports). Its
    # variants are chosen on the in-sample part like every other family and count towards the trials.
    ccat = {}
    for th in C_THRESHOLDS:
        for cat in sorted({t['cat'] for t in Cr if t['cat'] != 'crypto_updown'}):
            v = [t for t in Cr if t['th'] == th and t['cat'] == cat]
            if len(v) >= 30:
                ccat['Ccat|%.2f|%s' % (th, cat)] = v
    sel_Cc, parts_Cc, series_Cc, _ = run_protocol(ccat, live, cutoff_ts, t_lo, t_hi)
    # the up/down family on its own, same protocol; its variants count towards the trials
    ud = {}
    for h in ('1d', '6h'):
        for lo, hi in BANDS:
            ud['UD|%s|%.2f-%.3f' % (h, lo, hi)] = [t for t in A if t['cat'] == 'crypto_updown' and t['h'] == h
                                                   and lo <= t['p'] < hi]
    ud = {k: v for k, v in ud.items() if len(v) >= 30}
    series_ud = {}
    if ud:
        sel_ud, parts_ud, series_ud, _ = run_protocol(ud, live, cutoff_ts, t_lo, t_hi)
        res['updown'] = {'selection': sel_ud, 'variants': parts_ud}
    all_series = dict(series_A, **series_C, **series_ud, **series_Cc)
    n_trials = len(all_series)
    # every variant's OOS mean daily excess, tested once each, BH across all of them
    pv, names = [], []
    for k, s in all_series.items():
        t_, p_ = B.newey_west_t(s[n_is:])
        names.append(k)
        pv.append(p_)
    rej, adj = B.bh(pv, q=0.10)
    res['protocol'] = {'n_variants_tried': n_trials, 'cutoff_index': n_is,
                       'A': {'selection': sel_A, 'variants': parts_A},
                       'C': {'selection': sel_C, 'variants': parts_C},
                       'Ccat': {'selection': sel_Cc, 'variants': parts_Cc},
                       'bh_oos': {k: {'p': p, 'adj': a, 'reject': r} for k, p, a, r in zip(names, pv, adj, rej)}}
    for key, sel in (('A', sel_A), ('C', sel_C), ('Ccat', sel_Cc)):
        ch = sel['chosen']
        s = all_series[ch]
        res['protocol'][key]['chosen_oos_block_bootstrap'] = B.block_bootstrap(s[n_is:], n=1000)
        res['protocol'][key]['chosen_deflated_sharpe_oos'] = B.deflated_sharpe(s[n_is:], n_trials)
        res['protocol'][key]['chosen_oos_perf'] = B.perf(s[n_is:], 365)

    # robustness of the chosen A variant: spread and fee assumptions, categories, volume buckets, neg-risk members
    chA = sel_A['chosen']
    trA = [t for t in variants[chA] if t['t'] >= cutoff_ts]
    rob = {}
    for spread in ('zero', 'median', 'p75'):
        for fees in ('none', 'current'):
            r = returns_for(trA, live, spread, fees)
            rob['%s_spread|%s_fees' % (spread, fees)] = summarize(trA, r)
    res['robust_A'] = rob
    res['by_cat_A'] = {}
    for cat in sorted({t['cat'] for t in trA}):
        sub = [t for t in trA if t['cat'] == cat]
        r = returns_for(sub, live)
        res['by_cat_A'][cat] = dict(summarize(sub, r), ci=cluster_bootstrap(sub, r, n=500))
    res['by_vb_A'] = {}
    for vb in ('10k-100k', '100k-1m', '1m+'):
        sub = [t for t in trA if t['vb'] == vb]
        if sub:
            r = returns_for(sub, live)
            res['by_vb_A'][vb] = summarize(sub, r)
    # where the short-horizon losses come from: the widest band at 1d and 3d, by category, both parts
    res['by_cat_short'] = {}
    for h in ('1d', '3d'):
        for part in ('in_sample', 'out_of_sample'):
            sel = [t for t in core if t['h'] == h and 0.85 <= t['p'] < 0.995 and
                   ((t['close'] < cutoff_ts) if part == 'in_sample' else (t['t'] >= cutoff_ts))]
            for cat in sorted({t['cat'] for t in sel}):
                sub = [t for t in sel if t['cat'] == cat]
                if len(sub) < 20:
                    continue
                net = summarize(sub, returns_for(sub, live))
                gross = summarize(sub, returns_for(sub, live, 'zero', 'none'))
                res['by_cat_short']['%s|%s|%s' % (h, part, cat)] = {
                    'n': net['n'], 'events': net['events'], 'win_rate': net['win_rate'], 'mean_price': net['mean_price'],
                    'gross_mean_return_at_mid': gross['mean_return'], 'net_mean_return': net['mean_return']}
    res['tails_A'] = sorted(({'id': t['id'], 'cat': t['cat'], 'p': t['p'], 'pay': t['pay'], 'w': t['w'],
                              'q': by_id[t['id']]['question'][:90]} for t in trA if t['pay'] == 0.0),
                            key=lambda x: -x['p'])[:15]

    # strategy C detail: lag distribution and losses for the chosen threshold, OOS
    chC = sel_C['chosen']
    trC = [t for t in variants[chC] if t['t'] >= cutoff_ts]
    lags = sorted((t['close'] - t['t']) / HOUR for t in trC)
    res['C_detail'] = {'chosen': chC, 'n_oos': len(trC),
                       'lag_hours_median': statistics.median(lags) if lags else None,
                       'lag_hours_p90': lags[int(0.9 * (len(lags) - 1))] if lags else None,
                       'losses': [{'id': t['id'], 'p': t['p'], 'cat': t['cat'], 'q': by_id[t['id']]['question'][:90],
                                   'disputed': t['disputed']} for t in trC if t['pay'] == 0.0][:20],
                       'disputed_share': (sum(1 for t in trC if t['disputed']) / len(trC)) if trC else None}
    chCc = sel_Cc['chosen']
    trCc = [t for t in ccat[chCc] if t['t'] >= cutoff_ts]
    lagc = sorted((t['close'] - t['t']) / HOUR for t in trCc)
    res['Ccat_detail'] = {'chosen': chCc, 'n_oos': len(trCc),
                          'lag_hours_median': statistics.median(lagc) if lagc else None,
                          'lag_hours_p90': lagc[int(0.9 * (len(lagc) - 1))] if lagc else None,
                          'robust': {'%s_spread|%s_fees' % (sp, fe): summarize(trCc, returns_for(trCc, live, sp, fe))
                                     for sp in ('zero', 'median', 'p75') for fe in ('none', 'current')},
                          'losses': [{'id': t['id'], 'p': t['p'], 'q': by_id[t['id']]['question'][:90]}
                                     for t in trCc if t['pay'] != 1.0][:20]}
    res['C_by_cat'] = {}
    for cat in sorted({t['cat'] for t in trC}):
        sub = [t for t in trC if t['cat'] == cat]
        res['C_by_cat'][cat] = summarize(sub, returns_for(sub, live))
    res['live'] = {'snapshots': live['snapshots'], 'half_spread': live['half_spread'], 'fav_depth': live['fav_depth']}
    confirmed_rows = [r for r in live['neg_risk'] if r.get('has_confirm_field')]
    res['negrisk_live'] = summarize_negrisk_live(confirmed_rows)
    res['negrisk_live_sweep_only'] = {
        'note': 'snapshots taken before candidates were re-read atomically; kept to show the artifact',
        'summary': {k: v for k, v in summarize_negrisk_live([r for r in live['neg_risk'] if not r.get('has_confirm_field')]).items()
                    if k in ('rows', 'snapshots', 'clean')}}
    res['negrisk_confirmation'] = {
        'candidates_reread': sum(1 for r in confirmed_rows if r.get('confirmed_read')),
        'sweep_arb_signs': sum(1 for r in confirmed_rows if r.get('confirmed_read') and (
            (r.get('sweep_sum_ask') is not None and r['sweep_sum_ask'] < 1) or (r.get('sweep_sum_bid') is not None and r['sweep_sum_bid'] > 1))),
        'still_arb_sign_after_reread': sum(1 for r in confirmed_rows if r.get('confirmed_read') and (
            (r.get('sum_ask') is not None and r['sum_ask'] < 1) or (r.get('sum_bid') is not None and r['sum_bid'] > 1))),
        'clean_reread': sum(1 for r in confirmed_rows if r.get('confirmed_read') and not r['augmented'] and not r['incomplete']),
        'clean_still_arb_sign': sum(1 for r in confirmed_rows if r.get('confirmed_read') and not r['augmented'] and not r['incomplete'] and (
            (r.get('sum_ask') is not None and r['sum_ask'] < 1) or (r.get('sum_bid') is not None and r['sum_bid'] > 1)))}
    res['negrisk_history'] = summarize_negrisk_history(analyze_negrisk_history(out, uni))
    res['capacity'] = capacity({'A': (chA, trA), 'C': (chC, trC), 'Ccat': (chCc, trCc)}, live, res, cutoff_ts, t_hi)
    res['current_A'] = current_quotes(out, chA, trA)
    lf = out / 'lagflow_crypto_price.json'
    if lf.exists():
        res['lagflow_crypto_price'] = json.loads(lf.read_text())['summary']
    tc = out / 'trades_check.json'
    if tc.exists():
        res['trades_check'] = json.loads(tc.read_text())['summary']
    write_json(out / 'analysis.json', res)
    write_gz(out / 'raw' / 'trades.json.gz', {'A': A, 'C': Cr})
    snaps = []
    for sp in sorted((out / 'raw' / 'live').glob('snap_*.json.gz')):
        sn = read_gz(sp)
        snaps.append({'file': str(sp.relative_to(out)), 'at': sn['at'], 'events_scanned': sn.get('events_scanned'),
                      'neg_risk_events': len(sn['neg_risk_events']), 'yes_books': len(sn['books']),
                      'confirmed_rereads': len(sn.get('confirm') or {}), 'favourites': len(sn['favourites']),
                      'neg_risk_filter': 'events_scanned' in sn, 'seconds': sn.get('seconds')})
    update_manifest(out, 'live_snapshots', snaps)
    update_manifest(out, 'analysis', {'generated': res['generated'], 'cutoff': args.cutoff, 'start': args.start,
                                      'ssr': SSR, 'trades_A': len(A), 'trades_C': len(Cr),
                                      'variants_tried': res['protocol']['n_variants_tried'],
                                      'fee_schedule': 'docs.polymarket.com/trading/fees read 2026-10-09: '
                                                      'fee = shares x feeRate x p x (1 - p), taker only'})
    print(json.dumps({'trades_A': len(A), 'trades_C': len(Cr), 'chosen_A': chA, 'chosen_C': chC,
                      'A_oos': parts_A[chA]['oos'].get('ann_excess'), 'C_oos': parts_C[chC]['oos'].get('ann_excess')}))
    return 0


def summarize_negrisk_live(rows):
    """Executable neg-risk sums across snapshots. 'clean' = not augmented and every untraded member closed, so a
    basket of the tradable members is exhaustive; 'augmented' events carry an "Other" whose meaning changes as
    outcomes are named, so a basket there is a bet, not an arbitrage. An arbitrage counts when the walked fill is
    profitable after fees; it is *worth doing* when that profit, annualised to the event's end, beats the SSR."""
    if not rows:
        return {'rows': 0}
    snaps = sorted({r['at'] for r in rows})
    out = {'rows': len(rows), 'snapshots': len(snaps),
           'events_per_snapshot': statistics.median([sum(1 for r in rows if r['at'] == a) for a in snaps])}
    groups = (('clean', [r for r in rows if not r['augmented'] and not r['incomplete']]),
              ('incomplete', [r for r in rows if not r['augmented'] and r['incomplete']]),
              ('augmented', [r for r in rows if r['augmented']]))
    for label, sel in groups:
        sa = [r['sum_ask'] for r in sel if r['sum_ask'] is not None]
        sb = [r['sum_bid'] for r in sel if r['sum_bid'] is not None]
        arbs = []
        for r in sel:
            for kind in ('buy_all_yes', 'buy_all_no'):
                f = r.get(kind)
                if f and f['profit'] > 0:
                    arbs.append(dict(f, kind=kind, at=r['at'], event=r['event'], title=r['title'][:70],
                                     members=r['members_live'], sum_ask=r['sum_ask'], sum_bid=r['sum_bid']))
        worth = [x for x in arbs if (x.get('ann_excess') or -1) > 0]
        persist = None
        if len(snaps) > 1:
            keyed = {(x['at'], x['event'], x['kind']) for x in arbs}
            nxt = {a: b for a, b in zip(snaps, snaps[1:])}
            cand = [x for x in arbs if x['at'] in nxt]
            if cand:
                persist = sum(1 for x in cand if (nxt[x['at']], x['event'], x['kind']) in keyed) / len(cand)
        out[label] = {
            'rows': len(sel), 'events': len({r['event'] for r in sel}), 'with_full_ask': len(sa), 'with_full_bid': len(sb),
            'sum_ask_median': statistics.median(sa) if sa else None,
            'sum_bid_median': statistics.median(sb) if sb else None,
            'sum_ask_below_1': sum(1 for x in sa if x < 1), 'sum_bid_above_1': sum(1 for x in sb if x > 1),
            'arbs_after_fees': len(arbs), 'arbs_beating_ssr': len(worth),
            'arb_profit_usd_per_snapshot': sum(x['profit'] for x in arbs) / len(snaps),
            'arb_capital_usd_per_snapshot': sum(x['cost'] for x in arbs) / len(snaps),
            'worth_profit_usd_per_snapshot': sum(x['profit'] for x in worth) / len(snaps),
            'worth_capital_usd_per_snapshot': sum(x['cost'] for x in worth) / len(snaps),
            'persistence_next_snapshot': persist,
            'examples': sorted(arbs, key=lambda x: -(x.get('ann_excess') or -9))[:15]}
    return out


def summarize_negrisk_history(rows):
    ok = [r for r in rows if r.get('points')]
    out = {'events': len(rows), 'with_grid': len(ok),
           'skipped': sum(1 for r in rows if r.get('skipped'))}
    for label, sel in (('clean', [r for r in ok if not r['augmented']]), ('augmented', [r for r in ok if r['augmented']])):
        med = [r['sum_median'] for r in sel]
        out[label] = {'events': len(sel), 'sum_median_of_medians': statistics.median(med) if med else None,
                      'events_ever_below_098': sum(1 for r in sel if r['sum_min'] < 0.98),
                      'events_ever_above_102': sum(1 for r in sel if r['sum_max'] > 1.02),
                      'mean_share_below_098': (sum(r['share_below_098'] for r in sel) / len(sel)) if sel else None,
                      'payout_sum_not_1': sum(1 for r in sel if r['resolved'] and abs(r['payout_sum'] - 1) > 1e-6),
                      'resolved': sum(1 for r in sel if r['resolved'])}
    out['rows'] = rows[:400]
    return out


def current_quotes(out, variant, oos_trades):
    """What the chosen A variant would buy from the latest live snapshot, priced at the executable best ask with the
    taker fee, and valued at the variant's own out-of-sample win rate (not the in-sample one): the strategy's quote
    today, if the past nine months' calibration holds."""
    snaps = sorted((Path(out) / 'raw' / 'live').glob('snap_*.json.gz'))
    if not snaps or not oos_trades:
        return None
    _, h, band = variant.split('|')
    lo, hi = [float(x) for x in band.split('-')]
    sw = sum(t['w'] for t in oos_trades)
    win = sum(t['w'] for t in oos_trades if t['pay'] == 1.0) / sw
    half = sum(t['w'] for t in oos_trades if t['pay'] == 0.5) / sw
    s = read_gz(snaps[-1])
    now = parse_ts(s['at'])
    target = HORIZONS[h]
    tol = max(3 * HOUR, 0.5 * target)
    rows = []
    for m in s['favourites']:
        if m['cat'] == 'crypto_updown':
            continue
        end = parse_ts(m.get('endDate'))
        if end is None or abs((end - now) - target) > tol:
            continue
        b = s['fav_books'].get(m['clobTokenIds'][m['fav_side']])
        st = book_side_stats(b) if b else None
        if not st or not (lo <= st['mid'] < hi):
            continue
        ask = st['ask']
        cost = ask + fee_per_share(fee_rate(m['cat'], m.get('tags')), ask)
        e = (win + 0.5 * half) / cost - 1.0
        rows.append({'id': m['id'], 'q': (m.get('question') or '')[:80], 'cat': m['cat'], 'mid': st['mid'],
                     'ask': ask, 'best_ask_usd': st['ask_depth_usd_best'], 'exp_return': e,
                     'exp_usd': e * st['ask_depth_usd_best'], 'hours_to_end': (end - now) / HOUR})
    return {'snapshot': s['at'], 'variant': variant, 'oos_win_rate': win, 'oos_fifty_rate': half,
            'markets': len(rows), 'best_ask_usd': sum(r['best_ask_usd'] for r in rows),
            'positive_ev_markets': sum(1 for r in rows if r['exp_return'] > 0),
            'exp_usd_positive': sum(r['exp_usd'] for r in rows if r['exp_return'] > 0),
            'median_exp_return': statistics.median([r['exp_return'] for r in rows]) if rows else None,
            'top': sorted(rows, key=lambda r: -r['exp_usd'])[:10]}


def capacity(families, live, res, cutoff_ts, t_hi):
    """$/yr at capacity: entries per day in the test period, scaled to the universe by the sampling weights, times
    the live depth at the best ask (the price the backtest charges), held for the realised days, earning the OOS
    excess. `families` maps a protocol key to (chosen variant, its OOS trades)."""
    out = {}
    for key, (ch, trades) in families.items():
        if not trades:
            continue
        days_span = max(1.0, (t_hi - cutoff_ts) / DAY)
        per_day = sum(t['w'] for t in trades) / days_span
        hold = sum(t['w'] * max(1.0 / 24, (t['close'] - t['t']) / DAY) for t in trades) / sum(t['w'] for t in trades)
        dep = []
        for t in trades:
            band = band_of(t['p']) or band_of(min(0.994, max(0.85, t['p'])))
            r = live['fav_depth'].get('%s|%s' % (t['cat'], band)) or live['fav_depth'].get('all|%s' % band)
            dep.append(r['median_usd_best'] if r else 0.0)
        depth = statistics.median(dep) if dep else 0.0
        part = res['protocol'][key]['variants'][ch]['oos']
        exc = part.get('ann_excess') or 0.0
        capital = per_day * depth * hold
        out[key] = {'variant': ch, 'entries_per_day_universe': per_day, 'median_depth_usd_best_ask': depth,
                    'mean_hold_days': hold, 'capital_at_capacity_usd': capital, 'oos_ann_excess': exc,
                    'usd_per_year': capital * exc}
    return out


# ------------------------------------------------------------------------------------------------- trades check

def cmd_trades(args):
    """Where did taker fills sit against the midpoint the backtest uses? For a sample of OOS entries of the chosen
    variants, fetch taker trades of the favourite within +-30 minutes of the entry."""
    out = Path(args.out)
    res = json.loads((out / 'analysis.json').read_text())
    tr = read_gz(out / 'raw' / 'trades.json.gz')
    uni = {m['id']: m for m in load_universe(out)}
    cutoff_ts = parse_ts(res['cutoff'])
    chA = res['protocol']['A']['selection']['chosen']
    chC = res['protocol']['C']['selection']['chosen']
    _, h, band = chA.split('|')
    lo, hi = [float(x) for x in band.split('-')]
    th = float(chC.split('|')[1])
    pool = [('A', t) for t in tr['A'] if t['h'] == h and lo <= t['p'] < hi and t['t'] >= cutoff_ts
            and t['cat'] != 'crypto_updown']
    pool += [('C', t) for t in tr['C'] if t['th'] == th and t['t'] >= cutoff_ts and t['cat'] != 'crypto_updown']
    chCc = res['protocol']['Ccat']['selection']['chosen']
    _, thc, catc = chCc.split('|')
    poolc = [('Ccat', t) for t in tr['C'] if t['th'] == float(thc) and t['cat'] == catc and t['t'] >= cutoff_ts]
    rng = random.Random(5)
    rng.shuffle(pool)
    pool = pool[:args.n] + poolc
    http = Http(interval=args.interval)
    rows = []

    def one(x):
        kind, t = x
        m = uni[t['id']]
        q = {'market': m['conditionId'], 'limit': 500, 'takerOnly': 'true',
             'start': int(t['t'] - 1800), 'end': int(t['t'] + 1800)}
        d = http.request(DATA + '/trades?' + urllib.parse.urlencode(q))
        if not isinstance(d, list):
            return None
        fav_tok = m['clobTokenIds'][t['side']]
        buys = [float(x['price']) for x in d if x.get('asset') == fav_tok and x.get('side') == 'BUY']
        sells = [float(x['price']) for x in d if x.get('asset') == fav_tok and x.get('side') == 'SELL']
        # the complement token's sells are buys of the favourite at 1 - price, and vice versa
        other = m['clobTokenIds'][1 - t['side']]
        buys += [1.0 - float(x['price']) for x in d if x.get('asset') == other and x.get('side') == 'SELL']
        sells += [1.0 - float(x['price']) for x in d if x.get('asset') == other and x.get('side') == 'BUY']
        return {'kind': kind, 'id': t['id'], 'cat': t['cat'], 'mid': t['p'], 'n_buys': len(buys),
                'n_sells': len(sells), 'buy_median': statistics.median(buys) if buys else None,
                'sell_median': statistics.median(sells) if sells else None}

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(one, pool):
            if r:
                rows.append(r)
    summ = {}
    for kind in ('A', 'C', 'Ccat'):
        sel = [r for r in rows if r['kind'] == kind]
        dif_b = [r['buy_median'] - r['mid'] for r in sel if r['buy_median'] is not None]
        dif_s = [r['mid'] - r['sell_median'] for r in sel if r['sell_median'] is not None]
        summ[kind] = {'sampled': len(sel), 'with_buys': len(dif_b), 'with_sells': len(dif_s),
                      'buy_minus_mid_median': statistics.median(dif_b) if dif_b else None,
                      'buy_minus_mid_p75': sorted(dif_b)[int(0.75 * (len(dif_b) - 1))] if dif_b else None,
                      'mid_minus_sell_median': statistics.median(dif_s) if dif_s else None,
                      'no_taker_buy_within_30min': sum(1 for r in sel if r['buy_median'] is None)}
    out_obj = {'generated': utc(), 'variants': {'A': chA, 'C': chC, 'Ccat': chCc}, 'summary': summ, 'rows': rows,
               'http': http.stats(), 'source': DATA + '/trades (takerOnly, +-30 min of entry)'}
    write_json(out / 'trades_check.json', out_obj)
    update_manifest(out, 'trades_check', {'generated': out_obj['generated'], 'source': out_obj['source'],
                                          'entries': len(rows), 'variants': out_obj['variants'], 'http': http.stats()})
    print(json.dumps(summ, indent=1))
    return 0


# ------------------------------------------------------------------------------------------------- lag flow

def lag_flow_market(trades, winner, loser, min_price=0.90, rate=0.0):
    """From one market's taker trades after its scheduled end: every time the token that won changed hands at a
    price in [min_price, 1). The buyer of each such trade collected 1 - p at resolution. Two routes: a taker buying
    the winner (what a taker strategy competes for; the taker fee is netted) and a taker selling the winner into a
    resting bid (what a maker strategy competes for; makers pay no fee). Trades in the losing token are left out:
    whoever is on either side of those is not buying the resolved claim."""
    rows = []
    for x in trades:
        a, side, px, sz = x.get('asset'), x.get('side'), fnum(x.get('price')), fnum(x.get('size'))
        if px is None or sz is None or a != winner or px < min_price or px >= 1.0:
            continue
        rows.append((int(x.get('timestamp') or 0), side, px, sz, x.get('proxyWallet')))
    tb = [r for r in rows if r[1] == 'BUY']
    ts = [r for r in rows if r[1] == 'SELL']
    pool_t = sum(sz * (1.0 - px - fee_per_share(rate, px)) for _, _, px, sz, _ in tb)
    pool_m = sum(sz * (1.0 - px) for _, _, px, sz, _ in ts)
    by_w = collections.Counter()
    for _, _, px, sz, w in tb:
        by_w[w] += sz * (1.0 - px - fee_per_share(rate, px))
    vol_t = sum(sz * px for _, _, px, sz, _ in tb)
    return {'taker_buys': len(tb), 'pool_usd': pool_t, 'volume_usd': vol_t,
            'maker_fills': len(ts), 'maker_pool_usd': pool_m, 'maker_volume_usd': sum(sz * px for _, _, px, sz, _ in ts),
            'wallets': len(by_w), 'vwap': (vol_t / sum(sz for _, _, _, sz, _ in tb)) if tb else None,
            'top_wallet_share': (max(by_w.values()) / pool_t) if pool_t > 0 else None, 'by_wallet': dict(by_w)}


def cmd_lagflow(args):
    """Capacity of the resolution-lag trade in one category, measured from what was actually bought: every taker
    purchase of the eventual winner between the scheduled end and the close."""
    out = Path(args.out)
    tr = read_gz(out / 'raw' / 'trades.json.gz')
    uni = {m['id']: m for m in load_universe(out)}
    start, cutoff_ts = parse_ts(START), parse_ts(CUTOFF)
    rows = [t for t in tr['C'] if t['th'] == C_THRESHOLDS[0] and t['cat'] == args.cat and t['t'] >= start
            and t['pay'] in (0.0, 1.0)]
    http = Http(interval=args.interval)
    raw = out / 'raw' / 'lagflow'
    raw.mkdir(parents=True, exist_ok=True)

    def one(t):
        m = uni[t['id']]
        p = raw / ('%s.json.gz' % m['id'])
        if p.exists():
            got = read_gz(p)
        else:
            got, trunc = [], False
            for off in range(0, 3000, 500):
                q = {'market': m['conditionId'], 'limit': 500, 'offset': off, 'takerOnly': 'true',
                     'start': int(t['end']), 'end': int(t['close']) + 60}
                d = http.request(DATA + '/trades?' + urllib.parse.urlencode(q))
                if not isinstance(d, list):
                    break
                got.extend(d)
                if len(d) < 500:
                    break
                trunc = off + 500 >= 3000
            got = {'trades': got, 'truncated': trunc}
            write_gz(p, got)
        win_i = 0 if binary_payout(m) == 1.0 else 1
        f = lag_flow_market(got['trades'], m['clobTokenIds'][win_i], m['clobTokenIds'][1 - win_i],
                            rate=fee_rate(m['cat'], m.get('tags')))
        f.update({'id': m['id'], 'w': t['w'], 'oos': t['t'] >= cutoff_ts, 'is': t['close'] < cutoff_ts,
                  'end': t['end'], 'close': t['close'], 'truncated': got.get('truncated'), 'vb': t['vb'],
                  'q': (m.get('question') or '')[:80]})
        return f

    res_rows = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for f in ex.map(one, rows):
            res_rows.append(f)
    summ = {}
    for part in ('is', 'oos'):
        sel = [r for r in res_rows if r[part]]
        if not sel:
            continue
        lo = min(r['end'] for r in sel)
        hi = max(r['close'] for r in sel)
        days = max(1.0, (hi - lo) / DAY) if part == 'oos' else max(1.0, (cutoff_ts - parse_ts(START)) / DAY)
        sw = sum(r['w'] for r in sel)
        wallets = collections.Counter()
        for r in sel:
            for w, v in r['by_wallet'].items():
                wallets[w] += r['w'] * v
        tot = sum(wallets.values())
        summ[part] = {'markets': len(sel), 'markets_weighted': sw, 'days': days,
                      'markets_per_day_universe': sw / days,
                      'with_any_flow': sum(1 for r in sel if r['taker_buys'] or r['maker_fills']),
                      'maker_pool_usd_per_day_universe': sum(r['w'] * r['maker_pool_usd'] for r in sel) / days,
                      'pool_usd_per_market_mean': sum(r['w'] * r['pool_usd'] for r in sel) / sw,
                      'pool_usd_per_market_median': statistics.median([r['pool_usd'] for r in sel]),
                      'volume_usd_per_market_mean': sum(r['w'] * r['volume_usd'] for r in sel) / sw,
                      'pool_usd_per_day_universe': sum(r['w'] * r['pool_usd'] for r in sel) / days,
                      'volume_usd_per_day_universe': sum(r['w'] * r['volume_usd'] for r in sel) / days,
                      'pool_usd_per_year_universe': 365.0 * sum(r['w'] * r['pool_usd'] for r in sel) / days,
                      'top5_wallet_share': (sum(v for _, v in wallets.most_common(5)) / tot) if tot > 0 else None,
                      'wallets': len(wallets), 'truncated_markets': sum(1 for r in sel if r['truncated'])}
    # the decay series: the same pool month by month (calendar days, universe-weighted)
    by_month = collections.defaultdict(lambda: {'markets': 0, 'w': 0.0, 'pool': 0.0, 'maker_pool': 0.0, 'lag_w': 0.0})
    for r in res_rows:
        b = by_month[utc(r['end'])[:7]]
        b['markets'] += 1
        b['w'] += r['w']
        b['pool'] += r['w'] * r['pool_usd']
        b['maker_pool'] += r['w'] * r['maker_pool_usd']
        b['lag_w'] += r['w'] * (r['close'] - r['end']) / HOUR
    months = {}
    for mo, b in sorted(by_month.items()):
        y, mth = int(mo[:4]), int(mo[5:7])
        nd = (dt.date(y + (mth == 12), mth % 12 + 1, 1) - dt.date(y, mth, 1)).days
        months[mo] = {'markets_sampled': b['markets'], 'markets_universe': b['w'],
                      'taker_pool_usd_per_day': b['pool'] / nd, 'maker_pool_usd_per_day': b['maker_pool'] / nd,
                      'mean_lag_hours': b['lag_w'] / b['w'] if b['w'] else None}
    summ['by_month'] = months
    for r in res_rows:
        r.pop('by_wallet', None)
    obj = {'generated': utc(), 'category': args.cat, 'threshold_rows': C_THRESHOLDS[0], 'min_price': 0.90,
           'source': DATA + '/trades (takerOnly, scheduled end to close)', 'summary': summ, 'rows': res_rows,
           'http': http.stats()}
    write_json(out / ('lagflow_%s.json' % args.cat), obj)
    update_manifest(out, 'lagflow_%s' % args.cat, {'generated': obj['generated'], 'source': obj['source'],
                                                   'markets': len(res_rows), 'http': http.stats(),
                                                   'raw': 'raw/lagflow/<market id>.json.gz'})
    print(json.dumps(summ, indent=1))
    return 0


# ------------------------------------------------------------------------------------------------- render

def pct(x, d=1):
    return '-' if x is None else ('%.*f%%' % (d, 100 * x))


def usd(x):
    return '-' if x is None else '$' + format(int(round(x)), ',')


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    U = a['universe']
    L = ['# Polymarket history: tables', '',
         'Generated %s from `analysis.json`. Cutoff %s: variants are chosen on markets that closed before it and '
         'reported on entries after it. Returns are per dollar staked at the midpoint plus the live median '
         'half-spread for the category and price band, net of the current taker fee, and annualised per capital-day '
         'in excess of the %.2f%% savings rate.' % (a['generated'], a['cutoff'], 100 * a['ssr']), '']
    L += ['## Universe and sample', '', '| | |', '|---|---|']
    for k in ('markets', 'eligible_binary', 'fifty_fifty', 'disputed', 'not_cleanly_resolved'):
        L.append('| %s | %s |' % (k, format(U[k], ',')))
    L.append('| sampled markets | %s |' % format(a['sample_size'], ','))
    L.append('| with a price series | %s |' % format(a['meta'].get('with_series', 0), ','))
    L.append('| strategy A entries / C entries | %s / %s |' % (format(a['trades_A'], ','), format(a['trades_C'], ',')))
    L.append('')
    cs = a.get('calibration_slope') or {}
    if cs:
        L += ['## Calibration slope: logit(P(win)) = a + b logit(price), favourites, weighted to the universe', '',
              'b > 1 means favourites win more often than their price says (the favourite-longshot bias); b < 1 the '
              'reverse. 95% intervals from an event-clustered bootstrap.', '',
              '| horizon | in-sample b (n) | 95% CI | out-of-sample b (n) | 95% CI |', '|---|---|---|---|---|']
        for h in HORIZONS:
            i, o = (cs.get('in_sample') or {}).get(h), (cs.get('out_of_sample') or {}).get(h)
            f = lambda c: ('%.2f (%d)' % (c['b'], c['n'])) if c else '-'
            g = lambda c: ('%.2f-%.2f' % (c['b_lo'], c['b_hi'])) if c and c.get('b_lo') is not None else '-'
            L.append('| %s | %s | %s | %s | %s |' % (h, f(i), g(i), f(o), g(o)))
        L += ['', '| category (1d horizon) | in-sample b (n) | 95% CI | out-of-sample b (n) | 95% CI |', '|---|---|---|---|---|']
        cats = sorted(set((cs.get('in_sample_by_cat_1d') or {})) | set((cs.get('out_of_sample_by_cat_1d') or {})))
        for c_ in cats:
            i, o = (cs.get('in_sample_by_cat_1d') or {}).get(c_), (cs.get('out_of_sample_by_cat_1d') or {}).get(c_)
            f = lambda c: ('%.2f (%d)' % (c['b'], c['n'])) if c else '-'
            g = lambda c: ('%.2f-%.2f' % (c['b_lo'], c['b_hi'])) if c and c.get('b_lo') is not None else '-'
            L.append('| %s | %s | %s | %s | %s |' % (c_, f(i), g(i), f(o), g(o)))
        L.append('')
    L += ['## Calibration of the favourite (every category except up/down, weighted to the universe)', '']
    for h, rows in a['calibration'].items():
        L += ['### %s before the scheduled end' % h, '', '| price bin | n | mean price | win rate | 95% CI | edge pp |',
              '|---|---|---|---|---|---|']
        for r in rows:
            L.append('| %s | %d | %.3f | %.3f | %.3f-%.3f | %+.2f |' % (r['bin'], r['n'], r['mean_price'], r['win_rate'],
                                                                     r['ci_lo'], r['ci_hi'], r['edge_pp']))
        L.append('')
    for key in ('A', 'C'):
        P_ = a['protocol'][key]
        sel = P_['selection']
        L += ['## Strategy %s: choose then test' % key, '',
              'Chosen in sample by Sharpe: **%s** (of %d variants in this family; %d tried in all). Out-of-sample '
              'rank %d of %d; HAC t %.2f (p %.3f); deflated Sharpe of the out-of-sample series given %d trials: %s.'
              % (sel['chosen'], sel['n_variants'], a['protocol']['n_variants_tried'], sel['oos_rank'],
                 sel['n_variants'], sel['oos_t'] or float('nan'), sel['oos_p'] or float('nan'),
                 a['protocol']['n_variants_tried'],
                 ('%.3f' % P_['chosen_deflated_sharpe_oos']) if P_.get('chosen_deflated_sharpe_oos') is not None else '-'),
              '', '| variant | IS n | IS win | IS ann. excess | OOS n | OOS win | OOS mean ret | OOS days | OOS ann. excess | 95% event CI | BH q=0.1 |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
        for name, v in P_['variants'].items():
            i, o, ci = v['in'], v['oos'], v.get('oos_cluster_ci') or {}
            bh = a['protocol']['bh_oos'].get(name, {})
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                name, i.get('n', 0), pct(i.get('win_rate')), pct(i.get('ann_excess')), o.get('n', 0),
                pct(o.get('win_rate')), pct(o.get('mean_return'), 2),
                ('%.2f' % o['mean_days']) if o.get('mean_days') else '-', pct(o.get('ann_excess')),
                ('%s to %s' % (pct(ci.get('lo')), pct(ci.get('hi')))) if ci.get('lo') is not None else '-',
                'yes' if bh.get('reject') else 'no'))
        L.append('')
    L += ['## Chosen A variant, out of sample: cost assumptions', '', '| assumption | n | win | mean ret | ann. excess |',
          '|---|---|---|---|---|']
    for k, v in a['robust_A'].items():
        L.append('| %s | %s | %s | %s | %s |' % (k, v.get('n'), pct(v.get('win_rate')), pct(v.get('mean_return'), 2),
                                                 pct(v.get('ann_excess'))))
    L += ['', '## Chosen A variant, out of sample: by category', '', '| category | n | events | win | mean ret | days | ann. excess | 95% event CI |',
          '|---|---|---|---|---|---|---|---|']
    for k, v in a['by_cat_A'].items():
        ci = v.get('ci') or {}
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            k, v.get('n'), v.get('events'), pct(v.get('win_rate')), pct(v.get('mean_return'), 2),
            ('%.2f' % v['mean_days']) if v.get('mean_days') else '-', pct(v.get('ann_excess')),
            ('%s to %s' % (pct(ci.get('lo')), pct(ci.get('hi')))) if ci.get('lo') is not None else '-'))
    L += ['', '## Chosen A variant, out of sample: by total volume (ex post)', '', '| bucket | n | win | mean ret | ann. excess |', '|---|---|---|---|---|']
    for k, v in a['by_vb_A'].items():
        L.append('| %s | %s | %s | %s | %s |' % (k, v.get('n'), pct(v.get('win_rate')), pct(v.get('mean_return'), 2),
                                                 pct(v.get('ann_excess'))))
    if a.get('updown'):
        sel = a['updown']['selection']
        L += ['', '## Up/down family on its own', '', 'Chosen: **%s**; OOS rank %d of %d.' % (sel['chosen'], sel['oos_rank'], sel['n_variants']),
              '', '| variant | IS n | IS ann. excess | OOS n | OOS win | OOS ann. excess |', '|---|---|---|---|---|---|']
        for name, v in a['updown']['variants'].items():
            L.append('| %s | %s | %s | %s | %s | %s |' % (name, v['in'].get('n', 0), pct(v['in'].get('ann_excess')),
                                                         v['oos'].get('n', 0), pct(v['oos'].get('win_rate')),
                                                         pct(v['oos'].get('ann_excess'))))
    cd = a['C_detail']
    L += ['', '## Strategy C detail (%s, out of sample)' % cd['chosen'], '',
          'Entries %d; lag to close median %.1f h, p90 %.1f h; disputed share %s.' % (
              cd['n_oos'], cd['lag_hours_median'] or 0, cd['lag_hours_p90'] or 0, pct(cd.get('disputed_share'))), '']
    if a.get('C_by_cat'):
        L += ['| category | n | win | loss | mean ret | hours | ann. excess |', '|---|---|---|---|---|---|---|']
        for k, v in a['C_by_cat'].items():
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (k, v.get('n'), pct(v.get('win_rate')), pct(v.get('loss_rate'), 2),
                                                               pct(v.get('mean_return'), 2),
                                                               ('%.1f' % (24 * v['mean_days'])) if v.get('mean_days') else '-',
                                                               pct(v.get('ann_excess'))))
        L.append('')
    L += ['## Capacity', '', '| strategy | variant | entries/day (universe) | depth at best ask | hold days | capital | OOS ann. excess | $/yr |',
          '|---|---|---|---|---|---|---|---|']
    for k, v in a['capacity'].items():
        L.append('| %s | %s | %.1f | %s | %.2f | %s | %s | %s |' % (k, v['variant'], v['entries_per_day_universe'],
                                                                 usd(v['median_depth_usd_best_ask']), v['mean_hold_days'],
                                                                 usd(v['capital_at_capacity_usd']), pct(v['oos_ann_excess']),
                                                                 usd(v['usd_per_year'])))
    nl = a['negrisk_live']
    L += ['', '## Strategy B: live neg-risk books (%s snapshots, %s events per snapshot)' % (nl.get('snapshots'), nl.get('events_per_snapshot')), '',
          '| class | event-snapshots | median sum of asks | median sum of bids | asks < 1 | bids > 1 | arbitrages after fees | beating SSR | profit per snapshot | capital per snapshot | persists to next snapshot |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for k in ('clean', 'incomplete', 'augmented'):
        v = nl.get(k) or {}
        if not v:
            continue
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            k, v['rows'], ('%.3f' % v['sum_ask_median']) if v.get('sum_ask_median') is not None else '-',
            ('%.3f' % v['sum_bid_median']) if v.get('sum_bid_median') is not None else '-', v['sum_ask_below_1'],
            v['sum_bid_above_1'], v['arbs_after_fees'], v['arbs_beating_ssr'], usd(v['arb_profit_usd_per_snapshot']),
            usd(v['arb_capital_usd_per_snapshot']), pct(v.get('persistence_next_snapshot'))))
    nh = a['negrisk_history']
    L += ['', '## Strategy B: history (midpoints, an upper bound)', '', '| class | events | median of event median sums | ever below 0.98 | ever above 1.02 | mean share of time below 0.98 | resolved | payouts not summing to 1 |',
          '|---|---|---|---|---|---|---|---|']
    for k in ('clean', 'augmented'):
        v = nh.get(k) or {}
        if not v:
            continue
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            k, v['events'], ('%.3f' % v['sum_median_of_medians']) if v.get('sum_median_of_medians') is not None else '-',
            v['events_ever_below_098'], v['events_ever_above_102'], pct(v.get('mean_share_below_098')), v['resolved'],
            v['payout_sum_not_1']))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0


# ------------------------------------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    u = sub.add_parser('universe'); u.set_defaults(fn=cmd_universe)
    u.add_argument('--out', required=True)
    u.add_argument('--min-volume', type=float, default=10000)
    u.add_argument('--interval', type=float, default=0.25)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--target-1m', type=int, default=3000)
    c.add_argument('--target-100k', type=int, default=1500)
    c.add_argument('--target-10k', type=int, default=800)
    c.add_argument('--workers', type=int, default=6)
    c.add_argument('--interval', type=float, default=0.06)
    n = sub.add_parser('negrisk'); n.set_defaults(fn=cmd_negrisk)
    n.add_argument('--out', required=True)
    n.add_argument('--min-event-volume', type=float, default=1e6)
    n.add_argument('--max-events', type=int, default=400)
    n.add_argument('--workers', type=int, default=6)
    n.add_argument('--interval', type=float, default=0.06)
    lv = sub.add_parser('live'); lv.set_defaults(fn=cmd_live)
    lv.add_argument('--out', required=True)
    lv.add_argument('--interval', type=float, default=0.1)
    an = sub.add_parser('analyze'); an.set_defaults(fn=cmd_analyze)
    an.add_argument('--out', required=True)
    an.add_argument('--cutoff', default=CUTOFF)
    an.add_argument('--start', default=START)
    tr = sub.add_parser('trades'); tr.set_defaults(fn=cmd_trades)
    tr.add_argument('--out', required=True)
    tr.add_argument('--n', type=int, default=400)
    tr.add_argument('--workers', type=int, default=4)
    tr.add_argument('--interval', type=float, default=0.12)
    lf = sub.add_parser('lagflow'); lf.set_defaults(fn=cmd_lagflow)
    lf.add_argument('--out', required=True)
    lf.add_argument('--cat', default='crypto_price')
    lf.add_argument('--workers', type=int, default=4)
    lf.add_argument('--interval', type=float, default=0.06)
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
