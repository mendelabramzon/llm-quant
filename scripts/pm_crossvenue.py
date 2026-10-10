#!/usr/bin/env python3
"""One proposition, two prediction-market venues: Kalshi against Polymarket (and Limitless), priced as an arbitrage.

Why. A binary contract that pays $1 on the same event can trade at different prices on two venues that do not share a
book. Buying YES on the cheaper venue and NO on the other locks $1 at resolution for less than $1 when the two asks
sum below one after fees. Kalshi is a CFTC-regulated US exchange; Polymarket's international venue settles in USDC on
Polygon and blocks US persons. The segmentation of who can hold both is the usual explanation of why such gaps would
persist, and whether they do — at a size worth deploying, net of fees and of the capital both legs lock until the
later resolution — is what this module measures. Resolution-rule mismatch is the risk that turns an "arbitrage" into
two directional bets, so every pair carries a classification (identical / near-identical / different) and only the
first two enter the strategy.

Pipeline:
  snapshot    fetch Kalshi open events + markets (selected series), Polymarket active events (by end-date windows,
              gamma caps offset at 2,000), Limitless active markets, Kalshi series fee parameters  -> raw/
  candidates  deterministic candidate generation: sports by league + date + team codes; everything else by blocked
              token similarity with date proximity                                                 -> candidates.json
  (review)    the qualitative layer: matches.json is written by the analyst (pair ids, both rules excerpts, the
              classification and a one-line reason); the code never promotes a candidate on its own
  books       both order books for every confirmed pair; the executable gap at the touch and walked -> books.json
  history     Kalshi hourly candlesticks (yes bid/ask) and Polymarket prices-history for matched pairs -> history.json
  analyze     every number the note quotes                                                           -> analysis.json
  render      tables                                                                                     -> tables.md

Arithmetic (unit-tested in test_pm_crossvenue.py):
  * Kalshi taker fee  = ceil_to_cent(0.07 x multiplier x C x P x (1 - P)) per order (series `fee_multiplier`;
    docs.kalshi.com fee rounding: trade fee ceil to $0.000001, balance aligned to $0.01 for non-direct members).
  * Polymarket taker fee = C x rate x p x (1 - p) (docs.polymarket.com/trading/fees; rate from the market's
    `feeSchedule`, zero when `feesEnabled` is false; makers never pay).
  * A pair buys YES on one venue and NO on the other; each matched contract pays exactly $1 if the rules agree.
    Profit = C - (C x (a_yes + a_no) + fees). Return on capital = profit / cost; annualised simply over the days to the
    later resolution (floored at one day) and stated net of the Sky savings rate.
  * Kalshi's book lists bids on both sides: a YES ask at 1 - q exists for every NO bid at q, and vice versa.
    Polymarket's /book for each token is already the unified book (the NO token's asks mirror the YES bids).

    uv run python scripts/pm_crossvenue.py snapshot   --out research/2026-10-09/pm_crossvenue
    uv run python scripts/pm_crossvenue.py candidates --out research/2026-10-09/pm_crossvenue
    uv run python scripts/pm_crossvenue.py books      --out research/2026-10-09/pm_crossvenue
    uv run python scripts/pm_crossvenue.py history    --out research/2026-10-09/pm_crossvenue
    uv run python scripts/pm_crossvenue.py analyze    --out research/2026-10-09/pm_crossvenue
    uv run python scripts/pm_crossvenue.py render     --out research/2026-10-09/pm_crossvenue
"""
import argparse
import datetime as dt
import json
import math
import re
import statistics
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
KALSHI = 'https://api.elections.kalshi.com/trade-api/v2/'
GAMMA = 'https://gamma-api.polymarket.com/'
CLOB = 'https://clob.polymarket.com/'
LIMITLESS = 'https://api.limitless.exchange/'
UA = 'Mozilla/5.0'
SSR = 0.038                     # Sky savings rate read on chain 2026-10-09 ~20:45 UTC (sUSDS.ssr())
KALSHI_TAKER_RATE = 0.07
PACE = {'kalshi': 0.3, 'gamma': 0.4, 'clob': 0.5, 'limitless': 0.4}

# Polymarket's published taker rates by category (docs.polymarket.com/trading/fees, fetched 2026-10-09); a market's own
# feeSchedule overrides this table, which is used only when a history row lacks the schedule.
PM_RATE_BY_CATEGORY = {'crypto': 0.07, 'sports': 0.05, 'finance': 0.04, 'politics': 0.04, 'economics': 0.05,
                       'culture': 0.05, 'weather': 0.05, 'other': 0.05, 'mentions': 0.04, 'tech': 0.04,
                       'geopolitics': 0.0}


# ------------------------------------------------------------------------------------------------ fees and arithmetic

def kalshi_fee(contracts, price, multiplier=1.0, rate=KALSHI_TAKER_RATE):
    """Kalshi taker fee in dollars for one order: rate x multiplier x C x P x (1 - P), rounded up to the cent."""
    if contracts <= 0:
        return 0.0
    raw = rate * multiplier * contracts * price * (1.0 - price)
    return math.ceil(round(raw * 100.0, 9)) / 100.0


def polymarket_fee(shares, price, rate):
    """Polymarket taker fee in USDC: C x rate x p x (1 - p); zero when the market charges no fee."""
    if shares <= 0 or not rate:
        return 0.0
    return shares * rate * price * (1.0 - price)


def pm_fee_rate(market):
    """The taker rate a Polymarket market charges, from its own fields."""
    if not market.get('feesEnabled'):
        return 0.0
    fs = market.get('feeSchedule') or {}
    try:
        rate = float(fs.get('rate'))
    except (TypeError, ValueError):
        rate = None
    if rate is None:
        return PM_RATE_BY_CATEGORY.get((market.get('feeType') or 'other').split('_')[0], 0.05)
    if fs.get('exponent') not in (None, 1, 1.0):
        # the documented formula is the exponent-1 case; a different exponent would change the curve, so say so
        raise ValueError('unsupported fee exponent %r' % fs.get('exponent'))
    return rate


def kalshi_asks(orderbook):
    """Kalshi orderbook JSON -> (yes_asks, no_asks), each a list of (price, size) best first.

    The book carries bids only: a NO bid at q is a YES ask at 1 - q for the same size, and a YES bid at q a NO ask at
    1 - q. Handles both the `orderbook_fp` dollar form and the legacy integer-cents form."""
    ob = orderbook.get('orderbook_fp') or orderbook.get('orderbook') or {}
    def levels(key_dollars, key_cents):
        if ob.get(key_dollars) is not None:
            return [(float(p), float(s)) for p, s in ob[key_dollars]]
        if ob.get(key_cents) is not None:
            return [(int(p) / 100.0, float(s)) for p, s in ob[key_cents]]
        return []
    yes_bids = levels('yes_dollars', 'yes')
    no_bids = levels('no_dollars', 'no')
    yes_asks = sorted(((round(1.0 - q, 4), s) for q, s in no_bids if s > 0), key=lambda x: x[0])
    no_asks = sorted(((round(1.0 - q, 4), s) for q, s in yes_bids if s > 0), key=lambda x: x[0])
    return yes_asks, no_asks


def pm_asks(book):
    """Polymarket /book JSON -> asks (price, size) best first."""
    return sorted(((float(a['price']), float(a['size'])) for a in (book.get('asks') or []) if float(a['size']) > 0),
                  key=lambda x: x[0])


def touch(leg1, leg2, fee1, fee2):
    """The pair at the best ask on both legs: per-contract cost and profit, and the size both books show there.

    leg1/leg2: ask ladders [(price, size)]; fee1/fee2: callables (contracts, price) -> fee dollars.
    """
    if not leg1 or not leg2:
        return None
    (p1, s1), (p2, s2) = leg1[0], leg2[0]
    c = min(s1, s2)
    if c <= 0:
        return None
    f = fee1(c, p1) + fee2(c, p2)
    cost = c * (p1 + p2) + f
    return {'p1': p1, 'p2': p2, 'contracts': c, 'fees': f, 'cost': cost, 'profit': c - cost,
            'gross_gap': 1.0 - p1 - p2, 'net_per_contract': (c - cost) / c}


def walk(leg1, leg2, fee1_unit, fee2_unit, fee1, fee2, max_contracts=None):
    """Walk both ask ladders together while the marginal contract still pays after fees.

    fee*_unit(price) is the per-contract fee used for the marginal decision (no rounding); fee1/fee2 price the
    filled totals per leg (with the venue's rounding). Returns totals or None when nothing pays.
    """
    i = j = 0
    r1 = leg1[0][1] if leg1 else 0.0
    r2 = leg2[0][1] if leg2 else 0.0
    fills1, fills2 = [], []
    n = 0.0
    while i < len(leg1) and j < len(leg2):
        p1, p2 = leg1[i][0], leg2[j][0]
        if 1.0 - p1 - p2 - fee1_unit(p1) - fee2_unit(p2) <= 0:
            break
        q = min(r1, r2)
        if max_contracts is not None:
            q = min(q, max_contracts - n)
        if q <= 0:
            break
        fills1.append((p1, q))
        fills2.append((p2, q))
        n += q
        r1 -= q
        r2 -= q
        if r1 <= 1e-12:
            i += 1
            r1 = leg1[i][1] if i < len(leg1) else 0.0
        if r2 <= 1e-12:
            j += 1
            r2 = leg2[j][1] if j < len(leg2) else 0.0
        if max_contracts is not None and n >= max_contracts:
            break
    if n <= 0:
        return None
    cost1 = sum(p * q for p, q in fills1)
    cost2 = sum(p * q for p, q in fills2)
    # fees on the whole fill, priced at each leg's volume-weighted price (one order per leg)
    f = fee1(n, cost1 / n) + fee2(n, cost2 / n)
    cost = cost1 + cost2 + f
    return {'contracts': n, 'avg_p1': cost1 / n, 'avg_p2': cost2 / n, 'fees': f, 'cost': cost, 'profit': n - cost,
            'net_per_contract': (n - cost) / n}


def annualise(profit, cost, days, floor_days=1.0):
    """Simple annualised return on the capital both legs lock until the later resolution, and the same net of SSR."""
    if cost <= 0:
        return None, None
    d = max(days, floor_days)
    r = profit / cost * 365.0 / d
    return r, r - SSR


# ------------------------------------------------------------------------------------------------ text normalisation

STOP = set('the a an of in on at to for by will be is are and or vs v versus who what which win wins winner game '
           'match election 2025 2026 2027 than more less above below over under between before after yes no does '
           'do did any with from this that market markets party next most'.split())


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z0-9%.$ ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def tokens(s):
    return {t for t in norm(s).split() if t not in STOP and len(t) > 1}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def parse_time(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except ValueError:
        return None


def jl(v):
    """Gamma returns some list fields as JSON strings."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return []
    return v or []


# ------------------------------------------------------------------------------------------------ http with cache

_last = {}


def http_json(url, venue, cache=None, retries=6, timeout=60):
    if cache is not None and Path(cache).exists():
        return json.loads(Path(cache).read_text())
    wait = PACE.get(venue, 0.5) - (time.monotonic() - _last.get(venue, 0.0))
    if wait > 0:
        time.sleep(wait)
    last = None
    for a in range(retries):
        _last[venue] = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode())
            if cache is not None:
                Path(cache).parent.mkdir(parents=True, exist_ok=True)
                Path(cache).write_text(json.dumps(d))
            return d
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code in (400, 404, 422):
                return None
            ra = e.headers.get('Retry-After') if e.headers else None
            time.sleep(float(ra) if ra and ra.replace('.', '', 1).isdigit() else min(30.0, 1.5 * 2 ** a))
        except Exception as e:  # noqa: BLE001 - network errors are retried, then reported
            last = repr(e)[:100]
            time.sleep(min(30.0, 1.5 * 2 ** a))
    print('give up %s: %s' % (url[:140], last), flush=True)
    return None


# ------------------------------------------------------------------------------------------------ snapshot (fetch)

GAME_SERIES = re.compile(r'(GAME|MATCH|FIGHT)$')
ELECTION_SERIES = re.compile(r'HOUSE|SENATE|GOV|CONTROL|PRES|MAYOR')
MACRO_SERIES = ['KXFEDDECISION', 'KXFED', 'KXCPI', 'KXCPIYOY', 'KXCPICORE', 'KXCPICOREYOY', 'KXPAYROLLS', 'KXGDP',
                'KXU3', 'KXECONSTATCPI', 'KXECONSTATCPIYOY', 'KXBTCD', 'KXETHD', 'KXBTC', 'KXETH', 'KXBTCMAXY',
                'KXBTCMINY', 'KXFEDCHGCOUNT', 'KXRATECUTCOUNT', 'KXSHUTDOWN', 'KXGOVSHUT']


def fetch_kalshi_events(raw):
    evs, cur = [], None
    for page in range(2000):
        p = {'status': 'open', 'limit': 200}
        if cur:
            p['cursor'] = cur
        d = http_json(KALSHI + 'events?' + urllib.parse.urlencode(p), 'kalshi')
        if not d:
            break
        evs.extend(d.get('events') or [])
        cur = d.get('cursor')
        if not cur:
            break
    (raw / 'kalshi').mkdir(parents=True, exist_ok=True)
    (raw / 'kalshi' / 'events_open.json').write_text(json.dumps(evs))
    return evs


def select_kalshi_series(evs):
    cat = {e['series_ticker']: e.get('category') for e in evs}
    sel = set()
    for s, c in cat.items():
        if GAME_SERIES.search(s):
            sel.add(s)
        if c in ('Elections', 'Politics') and ELECTION_SERIES.search(s):
            sel.add(s)
    sel.update(s for s in MACRO_SERIES if s in cat)
    return sorted(sel)


def fetch_kalshi_markets(raw, series):
    out = raw / 'kalshi' / 'markets'
    out.mkdir(parents=True, exist_ok=True)
    for s in series:
        ms, cur = [], None
        for page in range(50):
            p = {'series_ticker': s, 'status': 'open', 'limit': 1000}
            if cur:
                p['cursor'] = cur
            d = http_json(KALSHI + 'markets?' + urllib.parse.urlencode(p), 'kalshi')
            if not d:
                break
            ms.extend(d.get('markets') or [])
            cur = d.get('cursor')
            if not cur:
                break
        (out / (s + '.json')).write_text(json.dumps(ms))


def fetch_polymarket_events(raw, now):
    """Every active Polymarket event. Gamma refuses offsets past 2,000 (HTTP 422), so the universe is read in end-date
    windows, each split in half until it fits."""
    seen = {}

    def window(a, b, depth=0):
        got, capped = [], False
        for page in range(21):
            q = {'active': 'true', 'closed': 'false', 'archived': 'false', 'limit': 100, 'offset': page * 100,
                 'end_date_min': a.isoformat().replace('+00:00', 'Z'), 'end_date_max': b.isoformat().replace('+00:00', 'Z')}
            d = http_json(GAMMA + 'events?' + urllib.parse.urlencode(q), 'gamma')
            if d is None:
                capped = True
                break
            got.extend(d)
            if len(d) < 100:
                break
        else:
            capped = True
        if capped and (b - a) > dt.timedelta(hours=2) and depth < 8:
            mid = a + (b - a) / 2
            return window(a, mid, depth + 1) + window(mid, b, depth + 1)
        return got

    day0 = dt.datetime(now.year, now.month, now.day, tzinfo=UTC)
    edges = [dt.datetime(2020, 1, 1, tzinfo=UTC), day0]
    edges += [day0 + dt.timedelta(days=d) for d in range(1, 8)]
    edges += [day0 + dt.timedelta(days=7 * w) for w in range(2, 10)]
    edges += [day0 + dt.timedelta(days=30 * m) for m in range(3, 15)]
    edges.append(dt.datetime(2100, 1, 1, tzinfo=UTC))
    for a, b in zip(edges[:-1], edges[1:]):
        for e in window(a, b):
            seen.setdefault(e['id'], e)
    write_pm_compact(raw, list(seen.values()))
    return list(seen.values())


PM_MARKET_FIELDS = ['conditionId', 'slug', 'question', 'groupItemTitle', 'outcomes', 'clobTokenIds', 'bestBid',
                    'bestAsk', 'lastTradePrice', 'feesEnabled', 'feeSchedule', 'feeType', 'volumeNum', 'volume24hr',
                    'liquidityNum', 'endDate', 'description', 'resolutionSource', 'sportsMarketType',
                    'acceptingOrders', 'negRisk', 'active', 'closed', 'gameStartTime']


def write_pm_compact(raw, events):
    """The active universe is ~23k events and ~377k markets (1.7 GB as served); keep the fields the matcher and the
    fee arithmetic use, with rules text cut at 2,000 characters."""
    import gzip
    out = []
    for e in events:
        ms = []
        for m in e.get('markets') or []:
            r = {k: m.get(k) for k in PM_MARKET_FIELDS}
            if r.get('description'):
                r['description'] = r['description'][:2000]
            ms.append(r)
        out.append({'id': e.get('id'), 'slug': e.get('slug'), 'title': e.get('title'),
                    'tags': [{'slug': t.get('slug'), 'label': t.get('label')} for t in e.get('tags') or []],
                    'endDate': e.get('endDate'), 'eventDate': e.get('eventDate'), 'gameId': e.get('gameId'),
                    'startTime': e.get('startTime'), 'seriesSlug': e.get('seriesSlug'), 'markets': ms})
    (raw / 'pm_events').mkdir(parents=True, exist_ok=True)
    with gzip.open(raw / 'pm_events' / 'events_all.json.gz', 'wt') as f:
        json.dump(out, f)


def fetch_limitless(raw):
    allm = []
    for page in range(1, 100):
        d = http_json(LIMITLESS + 'markets/active?page=%d&limit=25' % page, 'limitless')
        data = (d or {}).get('data') or []
        allm.extend(data)
        if len(data) < 25:
            break
    (raw / 'limitless').mkdir(parents=True, exist_ok=True)
    (raw / 'limitless' / 'markets_active.json').write_text(json.dumps(allm))
    return allm


def cmd_snapshot(args):
    out = Path(args.out)
    raw = out / 'raw'
    now = dt.datetime.now(UTC)
    t0 = time.time()
    log = {}
    if not args.skip_kalshi:
        evs = fetch_kalshi_events(raw)
        series = select_kalshi_series(evs)
        fetch_kalshi_markets(raw, series)
        s = http_json(KALSHI + 'series?limit=100000', 'kalshi')
        if s:
            (raw / 'kalshi' / 'series_all.json').write_text(json.dumps(s))
        log['kalshi'] = {'events_open': len(evs), 'series_selected': len(series)}
    if not args.skip_polymarket:
        log['polymarket'] = {'events_active': len(fetch_polymarket_events(raw, now))}
    if not args.skip_limitless:
        log['limitless'] = {'markets_active': len(fetch_limitless(raw))}
    write_manifest(out, 'snapshot', {'started_at': now.isoformat(), 'seconds': round(time.time() - t0, 1), **log})
    print(json.dumps(log))
    return 0


def write_manifest(out, step, rec):
    p = Path(out) / 'manifest.json'
    m = json.loads(p.read_text()) if p.exists() else {'steps': {}}
    m['steps'][step] = rec
    m['sources'] = {'kalshi': KALSHI, 'polymarket_gamma': GAMMA, 'polymarket_clob': CLOB, 'limitless': LIMITLESS,
                    'kalshi_fee_doc': 'https://docs.kalshi.com/getting_started/fee_rounding.md',
                    'polymarket_fee_doc': 'https://docs.polymarket.com/trading/fees.md'}
    p.write_text(json.dumps(m, indent=1, sort_keys=True))


# ------------------------------------------------------------------------------------------------ normalised events

MONTHS = {m: i for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV',
                                      'DEC'], 1)}


def kalshi_event_date(event_ticker):
    """Game tickers carry the local game date: KXNFLGAME-26OCT19WASSF -> 2026-10-19."""
    m = re.search(r'-(\d{2})([A-Z]{3})(\d{2})', event_ticker)
    if not m or m.group(2) not in MONTHS:
        return None
    try:
        return dt.date(2000 + int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))
    except ValueError:
        return None


def fnum(v, d=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def kalshi_events(raw):
    evs = {e['event_ticker']: e for e in json.loads((raw / 'kalshi' / 'events_open.json').read_text())}
    series_meta = {}
    sp = raw / 'kalshi' / 'series_all.json'
    if sp.exists():
        for s in json.loads(sp.read_text()).get('series') or []:
            series_meta[s['ticker']] = {'fee_type': s.get('fee_type'), 'fee_multiplier': s.get('fee_multiplier'),
                                        'category': s.get('category')}
    out = {}
    for f in sorted((raw / 'kalshi' / 'markets').glob('*.json')):
        for m in json.loads(f.read_text()):
            et = m['event_ticker']
            e = evs.get(et) or {}
            rec = out.setdefault(et, {
                'venue': 'kalshi', 'event': et, 'series': f.stem, 'title': e.get('title') or m.get('title'),
                'sub_title': e.get('sub_title'), 'category': e.get('category'),
                'mutually_exclusive': e.get('mutually_exclusive'), 'date': kalshi_event_date(et),
                'fee_multiplier': (series_meta.get(f.stem) or {}).get('fee_multiplier', 1),
                'fee_type': (series_meta.get(f.stem) or {}).get('fee_type'), 'markets': []})
            rec['markets'].append({
                'id': m['ticker'], 'label': m.get('yes_sub_title') or m.get('title'), 'title': m.get('title'),
                'yes_bid': fnum(m.get('yes_bid_dollars')), 'yes_ask': fnum(m.get('yes_ask_dollars')),
                'no_bid': fnum(m.get('no_bid_dollars')), 'no_ask': fnum(m.get('no_ask_dollars')),
                'yes_ask_size': fnum(m.get('yes_ask_size_fp')), 'yes_bid_size': fnum(m.get('yes_bid_size_fp')),
                'volume': fnum(m.get('volume_fp')), 'volume_24h': fnum(m.get('volume_24h_fp')),
                'open_interest': fnum(m.get('open_interest_fp')),
                'close': m.get('close_time'), 'expected_expiration': m.get('expected_expiration_time'),
                'rules': ((m.get('rules_primary') or '') + ' || ' + (m.get('rules_secondary') or '')).strip(),
                'status': m.get('status')})
    for rec in out.values():
        closes = [parse_time(x['close']) for x in rec['markets'] if parse_time(x['close'])]
        rec['close'] = max(closes).isoformat() if closes else None
    return out


def pm_events(raw):
    import gzip
    out = {}
    with gzip.open(raw / 'pm_events' / 'events_all.json.gz', 'rt') as f:
        events = json.load(f)
    for e in events:
        ms = []
        for m in e.get('markets') or []:
            if m.get('closed') or not m.get('active', True):
                continue
            try:
                rate = pm_fee_rate(m)
            except ValueError:
                rate = None
            ms.append({'id': m.get('conditionId'), 'slug': m.get('slug'), 'question': m.get('question'),
                       'label': m.get('groupItemTitle') or m.get('question'), 'outcomes': jl(m.get('outcomes')),
                       'tokens': jl(m.get('clobTokenIds')), 'best_bid': fnum(m.get('bestBid')),
                       'best_ask': fnum(m.get('bestAsk')), 'last': fnum(m.get('lastTradePrice')),
                       'fee_rate': rate, 'fee_type': m.get('feeType'), 'volume': fnum(m.get('volumeNum')),
                       'volume_24h': fnum(m.get('volume24hr')), 'liquidity': fnum(m.get('liquidityNum')),
                       'close': m.get('endDate'), 'rules': m.get('description') or '',
                       'resolution_source': m.get('resolutionSource'), 'sports_type': m.get('sportsMarketType'),
                       'accepting_orders': m.get('acceptingOrders'), 'neg_risk': m.get('negRisk')})
        if not ms:
            continue
        out[e['slug']] = {'venue': 'polymarket', 'event': e['slug'], 'id': e.get('id'), 'title': e.get('title'),
                          'tags': [t.get('slug') for t in e.get('tags') or []], 'close': e.get('endDate'),
                          'date': (dt.date.fromisoformat(e['eventDate']) if e.get('eventDate') else None),
                          'game': bool(e.get('gameId')), 'markets': ms}
    return out


def limitless_events(raw):
    p = raw / 'limitless' / 'markets_active.json'
    if not p.exists():
        return {}
    out = {}
    for m in json.loads(p.read_text()):
        prices = m.get('prices') or []
        out[m['slug']] = {'venue': 'limitless', 'event': m['slug'], 'title': m.get('title'),
                          'tags': (m.get('categories') or []) + (m.get('tags') or []),
                          'close': (dt.datetime.fromtimestamp(m['expirationTimestamp'] / 1000, UTC).isoformat()
                                    if m.get('expirationTimestamp') else None), 'date': None, 'game': False,
                          'markets': [{'id': m['slug'], 'label': m.get('title'), 'question': m.get('title'),
                                       'yes_price': prices[0] if prices else None, 'volume': fnum(m.get('volumeFormatted')),
                                       'rules': m.get('description') or '', 'close': None}]}
    return out


# ------------------------------------------------------------------------------------------------ candidates

def event_tokens(ev):
    t = tokens(ev['title'] or '') | tokens(ev.get('sub_title') or '')
    if len(ev['markets']) <= 6:
        for m in ev['markets']:
            t |= tokens(m.get('label') or '')
    return t


SYNONYMS = {'republicans': 'republican', 'gop': 'republican', 'democrats': 'democratic', 'democrat': 'democratic',
            'dem': 'democratic', 'rep': 'republican', 'tie': 'draw'}


def team_tokens(label):
    t = {SYNONYMS.get(x, x) for x in tokens(label)}
    return t - {'fc', 'cf', 'sc', 'ac', 'club', 'united', 'city', 'de', 'team', 'party'}


# Kalshi game series -> the Polymarket tag its counterpart must carry. Unlisted game series need 'sports' or 'esports'.
LEAGUE_TAGS = {'KXNFLGAME': 'nfl', 'KXNCAAFGAME': 'cfb', 'KXNBAGAME': 'nba', 'KXWNBAGAME': 'wnba', 'KXNHLGAME': 'nhl',
               'KXMLBGAME': 'mlb', 'KXAHLGAME': 'ahl', 'KXUFCFIGHT': 'ufc', 'KXCS2GAME': 'counter-strike-2',
               'KXLOLGAME': 'league-of-legends', 'KXDOTA2GAME': 'dota-2', 'KXVALORANTGAME': 'valorant'}
SIDE_EVENT = re.compile(r'more markets|player props|exact score|exact margin|halftime|1st half|first half|corners|'
                        r'cards|both teams|total goals|spread|o/u|over/under|props|winning margin|method of victory|'
                        r'round betting|set betting|correct score|first to score|anytime', re.I)


def is_main_game_event(pe):
    if SIDE_EVENT.search(pe.get('title') or '') or SIDE_EVENT.search(pe.get('event') or ''):
        return False
    return any((m.get('sports_type') == 'moneyline') for m in pe['markets']) or len(pe['markets']) <= 3


def years_in(s):
    return set(re.findall(r'\b(20\d\d)\b', s or ''))


def kalshi_year(event_ticker):
    m = re.search(r'-(\d{2})$', event_ticker)
    return {'20' + m.group(1)} if m else set()


def candidates(kev, pev, sports_days=1, other_days=400, min_score=0.25, top=3):
    """Event-level candidates. Sports: same game date within a day and team-name overlap. Others: close dates within
    `other_days` and title-token Jaccard. Returns [(score, kalshi_event, pm_event, kind)]."""
    by_date = {}
    for e in pev.values():
        if e.get('date'):
            by_date.setdefault(e['date'], []).append(e)
    idx = {}
    for e in pev.values():
        for t in event_tokens(e):
            idx.setdefault(t, []).append(e['event'])
    ptok = {k: event_tokens(e) for k, e in pev.items()}
    out = []
    for k, ke in kev.items():
        kt = event_tokens(ke)
        cands = []
        if GAME_SERIES.search(ke['series']) and ke.get('date'):
            pool = []
            for d in range(-sports_days, sports_days + 1):
                pool += by_date.get(ke['date'] + dt.timedelta(days=d), [])
            need = LEAGUE_TAGS.get(ke['series'])
            for pe in pool:
                tags = set(pe.get('tags') or [])
                if need and need not in tags:
                    continue
                if not need and not (tags & {'sports', 'esports'}):
                    continue
                if not is_main_game_event(pe):
                    continue
                s = jaccard(kt, ptok[pe['event']])
                if s >= 0.15:
                    cands.append((s, pe['event'], 'sports'))
        else:
            kc = parse_time(ke.get('close'))
            seen = {}
            for t in kt:
                lst = idx.get(t) or []
                if len(lst) > 400:          # a token that common blocks nothing
                    continue
                for pk in lst:
                    seen[pk] = seen.get(pk, 0) + 1
            for pk, n in seen.items():
                if n < 2:
                    continue
                pe = pev[pk]
                if pe.get('game') or set(pe.get('tags') or []) & {'sports', 'esports', 'games'}:
                    continue
                pc = parse_time(pe.get('close'))
                if kc and pc and abs((kc - pc).days) > other_days:
                    continue
                # an explicit year on both sides must agree (2026 midterms vs 2028); Kalshi closes election events a
                # year after the vote, so the year, not the close date, is the test
                ky = years_in(ke['title']) | kalshi_year(ke['event'])
                py = years_in(pe['title']) | ({pc.strftime('%Y')} if pc else set())
                if ky and py and not (ky & py):
                    continue
                s = jaccard(kt, ptok[pk])
                if s >= min_score:
                    cands.append((s, pk, 'other'))
        cands.sort(reverse=True)
        for s, pk, kind in cands[:top]:
            out.append((round(s, 3), k, pk, kind))
    out.sort(key=lambda x: -x[0])
    return out


SUB_MARKET = re.compile(r'\bmap \d|\bgame \d|\bset \d|handicap|\btotal|spread|o/u|over/under|both teams|exact|'
                        r'\bfirst\b|\b1st\b|half|quarter|period|inning|corners|\bcards', re.I)


def kalshi_market_tokens(ke, km):
    """A Kalshi team market's identifying tokens: its label (often a city), the team code that ends its ticker, and
    the half of the event title that carries either ('WAS Commanders vs SF 49ers' gives 'commanders' to the WAS
    market), so a city label can meet a nickname outcome."""
    t = team_tokens(km['label'] or '')
    code = km['id'].rsplit('-', 1)[-1].lower()
    title = ke['title'] or ''
    if ':' in title:
        title = title.split(':', 1)[1]
    for h in re.split(r'\s+(?:vs\.?|at|@)\s+', title, flags=re.I):
        ht = team_tokens(h)
        if (t & ht) or code in norm(h).split():
            t |= ht
    if len(code) <= 5:
        t.add(code)
    return t


def map_markets(ke, pe):
    """Market-level mapping inside a candidate event pair: each Kalshi market to the Polymarket market (and the token
    that pays when the Kalshi YES pays) whose label shares the most tokens. Two-outcome Polymarket markets whose
    outcomes are names (a moneyline 'Team A' / 'Team B') map the Kalshi team market to that outcome's token, with the
    other outcome as the complement."""
    rows = []
    for km in ke['markets']:
        kt = kalshi_market_tokens(ke, km)
        best = None
        if norm(km['label'] or '') in ('tie', 'draw'):
            for pm in pe['markets']:
                if norm(pm.get('label') or '').startswith('draw') and len(pm.get('tokens') or []) == 2:
                    best = (1.0, pm, 0, 1, 'yes_no')
        pool = pe['markets']
        if any(m.get('sports_type') == 'moneyline' for m in pool):
            # a game event also lists map/set/half/total markets; only the full-game moneyline is the same proposition
            pool = [m for m in pool if m.get('sports_type') == 'moneyline' and not SUB_MARKET.search(
                (m.get('question') or '') + ' ' + (m.get('label') or ''))]
        for pm in ([] if best else pool):
            outs = [str(o) for o in pm.get('outcomes') or []]
            if len(outs) == 2 and outs[0].lower() not in ('yes', 'no'):
                for i, o in enumerate(outs):
                    s = jaccard(kt, team_tokens(o))
                    if s > 0 and (best is None or s > best[0]):
                        best = (s, pm, i, 1 - i, 'outcome')
            else:
                s = jaccard(kt, team_tokens(pm.get('label') or ''))
                if s > 0 and (best is None or s > best[0]):
                    best = (s, pm, 0, 1, 'yes_no')
        if best:
            s, pm, yi, ni, form = best
            rows.append({'kalshi': km['id'], 'kalshi_label': km['label'], 'pm_market': pm['id'], 'pm_label': pm['label'],
                         'pm_question': pm.get('question'), 'pm_yes_token': (pm['tokens'] or [None, None])[yi],
                         'pm_no_token': (pm['tokens'] or [None, None])[ni], 'pm_yes_outcome': (pm.get('outcomes') or ['?', '?'])[yi],
                         'form': form, 'label_score': round(s, 3), 'pm_fee_rate': pm.get('fee_rate'),
                         'kalshi_rules': km.get('rules', '')[:600], 'pm_rules': (pm.get('rules') or '')[:600],
                         'kalshi_close': km.get('close'), 'pm_close': pm.get('close'),
                         'kalshi_yes_ask': km.get('yes_ask'), 'kalshi_no_ask': km.get('no_ask'),
                         'pm_best_bid': pm.get('best_bid'), 'pm_best_ask': pm.get('best_ask'),
                         'kalshi_volume': km.get('volume'), 'pm_volume': pm.get('volume')})
    return rows


def screen_gap(r):
    """A screening gap from listed top-of-book prices (not executable until the books are read): the better of
    YES-Kalshi + NO-Polymarket and NO-Kalshi + YES-Polymarket, before fees. For a 'yes_no' Polymarket market the NO
    ask is 1 - best bid; for an 'outcome' form the listed prices belong to the first outcome and are not used."""
    ky, kn = r.get('kalshi_yes_ask'), r.get('kalshi_no_ask')
    if r['form'] != 'yes_no' or r.get('pm_best_ask') is None or r.get('pm_best_bid') is None:
        return None
    py, pn = r['pm_best_ask'], 1.0 - r['pm_best_bid']
    gaps = []
    if ky is not None and ky > 0:
        gaps.append(1.0 - ky - pn)
    if kn is not None and kn > 0:
        gaps.append(1.0 - kn - py)
    return max(gaps) if gaps else None


def cmd_candidates(args):
    out = Path(args.out)
    raw = out / 'raw'
    kev, pev = kalshi_events(raw), pm_events(raw)
    cands = candidates(kev, pev)
    rows = []
    for s, k, p, kind in cands:
        ke, pe = kev[k], pev[p]
        mm = map_markets(ke, pe)
        for r in mm:
            r['screen_gap'] = screen_gap(r)
        rows.append({'score': s, 'kind': kind, 'kalshi_event': k, 'kalshi_series': ke['series'],
                     'kalshi_title': ke['title'], 'kalshi_category': ke.get('category'), 'kalshi_close': ke.get('close'),
                     'kalshi_date': ke['date'].isoformat() if ke.get('date') else None,
                     'pm_event': p, 'pm_title': pe['title'], 'pm_tags': pe.get('tags'), 'pm_close': pe.get('close'),
                     'pm_date': pe['date'].isoformat() if pe.get('date') else None,
                     'kalshi_markets': len(ke['markets']), 'pm_markets': len(pe['markets']), 'market_map': mm})
    (out / 'candidates.json').write_text(json.dumps({'generated': dt.datetime.now(UTC).isoformat(),
                                                     'kalshi_events': len(kev), 'pm_events': len(pev),
                                                     'pairs': rows}, indent=1, default=str))
    print(json.dumps({'kalshi_events': len(kev), 'pm_events': len(pev), 'candidate_pairs': len(rows),
                      'sports': sum(1 for r in rows if r['kind'] == 'sports'),
                      'other': sum(1 for r in rows if r['kind'] == 'other')}))
    return 0



# ------------------------------------------------------------------------------------------------ match (accept)

# The qualitative layer, written down. Each class records how the two venues' rules compare, read from both rules
# texts on 2026-10-09 (examples quoted in findings.md). 'near-identical' means the normal outcome resolves the same way
# on both venues and the venues differ only on a stated edge case; a pair in a 'different' class never enters the book.
RULE_CLASSES = {
    'football': ('near-identical', 'win and tie handled alike (a tie pays 50/50 on both); differs on postponement '
                 'past 48h, where Kalshi resolves to a fair price and Polymarket stays open until the game is played'),
    'baseball': ('near-identical', 'winner of the game on both; Kalshi resolves a game cancelled or moved more than two '
                 'days to a fair price, Polymarket waits for the make-up game and pays 50-50 on a cancellation'),
    'basketball_hockey': ('near-identical', 'winner including overtime on both; postponement and cancellation are '
                          'resolved differently (Kalshi fair price, Polymarket 50-50 or open)'),
    'soccer': ('near-identical', 'result after 90 minutes plus stoppage time on both, three outcomes (home, draw, away); '
               'a cancelled match resolves to a fair price on Kalshi but to No on the team markets and Yes on the draw '
               'on Polymarket'),
    'tennis': ('near-identical', 'the player who wins or advances once a ball has been played; a walkover before the '
               'first ball resolves to a fair price on Kalshi and to the advancing player (or 50-50) on Polymarket'),
    'esports': ('near-identical', 'full-match winner on both (map markets excluded); forfeits and postponements past '
                '48h are resolved differently'),
    'combat': ('near-identical', 'official winner; draw or no contest pays 50/50 on both; a cancelled or long-postponed '
               'bout resolves to a fair price on Kalshi and 50-50 on Polymarket'),
    'other_sport': ('near-identical', 'winner of the listed match on both; cancellation and postponement rules differ'),
    'election_party': ('near-identical', 'both resolve on the winning nominee’s party; Kalshi on the party of the '
                       'person sworn in or inaugurated (determined early on a media consensus), Polymarket on the '
                       'declared winner; they differ only if the winner never takes office or changes party'),
    'chamber_control': ('near-identical', 'majority of voting seats, with the Speaker’s party as the fallback on '
                        'both; Kalshi reads the Speaker on 2027-02-01 if no media consensus'),
}
SPORT_CLASS = [(re.compile(r'NFL|NCAAF|CFL|UFL'), 'football'), (re.compile(r'MLB|KBO|NPB|BBSERIEA|MLBB'), 'baseball'),
               (re.compile(r'NBA|WNBA|NHL|AHL|NCAAH|NCAAB|EUROLEAGUE|ACB|ABA|BSL|KHL|SHL|BASKET'), 'basketball_hockey'),
               (re.compile(r'ATP|WTA|ITF|TENNIS|CHALLENGER'), 'tennis'), (re.compile(r'CS2|LOL|DOTA|VALORANT|OW|ESPORT|COD'),
               'esports'), (re.compile(r'UFC|MMA|BOX|FIGHT'), 'combat')]
SOCCER_HINT = re.compile(r'GAME$')


TAG_CLASS = [({'esports', 'counter-strike-2', 'league-of-legends', 'dota-2', 'valorant', 'mobile-legends'}, 'esports'),
             ({'soccer'}, 'soccer'), ({'tennis'}, 'tennis'), ({'nfl', 'cfb', 'football', 'cfl'}, 'football'),
             ({'mlb', 'baseball', 'kbo', 'npb'}, 'baseball'),
             ({'nba', 'wnba', 'basketball', 'nhl', 'hockey', 'ahl', 'khl'}, 'basketball_hockey'),
             ({'ufc', 'mma', 'boxing'}, 'combat')]


def sport_class(series, pe_tags):
    """The Polymarket event's own tags decide (a Kalshi series name can mislead: 'ARGNACBGAME' is Argentine football,
    'MLBB' is an esport); the series name is the fallback."""
    tags = set(pe_tags or [])
    for want, c in TAG_CLASS:
        if tags & want:
            return c
    for rx, c in SPORT_CLASS:
        if rx.search(series):
            return c
    return 'other_sport'


OFFICE_WORDS = ['lieutenant', 'state', 'attorney', 'secretary', 'house', 'senate', 'governor', 'mayor', 'assembly',
                'special', 'runoff', 'primary']


def office_words(title):
    t = (title or '').lower()
    return frozenset(w for w in OFFICE_WORDS if re.search(r'\b' + w + r'\b', t))


KALSHI_SPORT = [(re.compile(r'NFL|NCAAF|CFL|UFL'), 'american_football'),
                (re.compile(r'NBA|WNBA|NCAAB|NCAAWB|EUROLEAGUE|EUROCUP|ACBGAME|ABAGAME|BSLGAME|BBSERIEA|BASKETBALL|'
                            r'NBLGAME|CBAGAME|LNBGAME|BBLGAME'), 'basketball'),
                (re.compile(r'NHL|AHL|NCAAH|KHL|SHL|LIIGA|HOCKEY'), 'hockey'),
                (re.compile(r'MLB(?!B)|KBO|NPB|BASEBALL'), 'baseball'),
                (re.compile(r'ATP|WTA|ITF|TENNIS|CHALLENGER'), 'tennis'),
                (re.compile(r'CS2|LOL|OWGAME|DOTA|VALORANT|MLBB|ESOCCER|EBASKETBALL|CODGAME|R6'), 'esports'),
                (re.compile(r'UFC|MMA|BOX'), 'combat'), (re.compile(r'DARTS'), 'darts'),
                (re.compile(r'T20|CRICKET|RANJI|ODIMATCH'), 'cricket'), (re.compile(r'NCAAWV|VOLLEY'), 'volleyball'),
                (re.compile(r'RUGBY|NRLGAME|TOP14'), 'rugby'), (re.compile(r'TABLETENNIS|TTGAME|TTMATCH'), 'table_tennis')]
PM_SPORT_TAGS = {'american_football': {'nfl', 'cfb', 'ncaaf'}, 'basketball': {'basketball', 'nba', 'wnba', 'ncaab',
                 'euroleague', 'cbb'}, 'hockey': {'hockey', 'nhl', 'ahl', 'khl'}, 'baseball': {'baseball', 'mlb', 'kbo',
                 'npb'}, 'soccer': {'soccer'}, 'tennis': {'tennis'}, 'esports': {'esports'},
                 'combat': {'ufc', 'mma', 'boxing'}, 'darts': {'darts'}, 'cricket': {'cricket'},
                 'volleyball': {'volleyball'}, 'rugby': {'rugby'}, 'table_tennis': {'table-tennis'}}


def kalshi_sport(series):
    for rx, sp in KALSHI_SPORT:
        if rx.search(series):
            return sp
    return 'soccer' if GAME_SERIES.search(series) else None


def sport_consistent(series, pm_tags):
    """The Polymarket event must be the same sport as the Kalshi series: a women's volleyball match and a football game
    between the same two universities on the same weekend are different propositions with identical team names."""
    ks = kalshi_sport(series)
    tags = set(pm_tags or [])
    known = {sp for sp, ts in PM_SPORT_TAGS.items() if tags & ts}
    if ks is None or not known:
        return ks is None
    return ks in known


PLACE_STOP = set(OFFICE_WORDS) | {'winner', 'election', 'party', 'which', 'will', 'win', 'race', 'seat', 'the', 'in',
                                   'of', 'us', 'u', 's', 'midterm', 'midterms', 'person', 'representatives',
                                   'congressional', 'district', 'general', 'gubernatorial', 'control'}


def place_tokens(title):
    """What an election title is about once the office and the filler are removed: 'CA-22 House winner?' -> {ca, 22}.
    Two titles about the same race carry the same place; a county inside a state, or a state against the whole chamber,
    does not."""
    t = {x for x in norm(title).split() if x not in PLACE_STOP and not re.fullmatch(r'20\d\d', x)}
    return {x.lstrip('0') or '0' for x in t}


def accept_pairs(cands, kev, pev):
    """Deterministic acceptance of candidate pairs; returns (accepted, rejected_reasons Counter).

    Sports: the best Polymarket event per Kalshi event with an exact date when one exists; every Kalshi market mapped
    to a distinct Polymarket outcome with label overlap; a two-outcome Polymarket market only against a two-market
    Kalshi event (no draw). Elections: identical office and place tokens, every candidate mapped one to one."""
    import collections
    why = collections.Counter()
    by_k = {}
    for r in cands:
        by_k.setdefault(r['kalshi_event'], []).append(r)
    out = []
    for k, rs in by_k.items():
        ke = kev.get(k)
        if not ke:
            continue
        if rs[0]['kind'] == 'sports':
            rs = [r for r in rs if sport_consistent(ke['series'], r['pm_tags'])]
            if not rs:
                why['no candidate of the same sport'] += 1
                continue
            exact = [r for r in rs if r['pm_date'] and ke.get('date') and r['pm_date'] == ke['date'].isoformat()]
            r = max(exact or rs, key=lambda x: x['score'])
            cls = sport_class(ke['series'], r['pm_tags'])
        else:
            cls = None
            title = norm(ke['title'])
            if ke['series'] in ('CONTROLH', 'CONTROLS'):
                ok = [r for r in rs if r['score'] >= 0.6 and office_words(ke['title']) == office_words(r['pm_title'])]
                cls = 'chamber_control' if ok else None
            elif re.search(r'\b(house|senate|governor)\b', title) and 'winner' in (ke['title'] or '').lower():
                ok = [r for r in rs if office_words(ke['title']) == office_words(r['pm_title'])
                      and place_tokens(ke['title']) == place_tokens(r['pm_title'])]
                if not ok:
                    why['no candidate for the same office and place'] += 1
                    continue
                cls = 'election_party'
            else:
                ok = []
            if cls is None:
                why['non-sports pair left to manual review'] += 1
                continue
            r = max(ok, key=lambda x: x['score'])
        mm = r['market_map']
        if len(mm) != len(ke['markets']):
            why['not every Kalshi market mapped'] += 1
            continue
        keys = [(m['pm_market'], m['pm_yes_token']) for m in mm]
        if len(set(keys)) != len(keys):
            why['mapping not one-to-one'] += 1
            continue
        if any(m['label_score'] < (0.3 if r['kind'] == 'sports' else 0.5) for m in mm):
            why['weak label overlap'] += 1
            continue
        if any(m['form'] == 'outcome' for m in mm) and len(ke['markets']) != 2:
            why['two-way Polymarket market against a three-way Kalshi event'] += 1
            continue
        if any(not m['pm_yes_token'] or not m['pm_no_token'] for m in mm):
            why['missing Polymarket token ids'] += 1
            continue
        pe = pev.get(r['pm_event']) or {}
        status, reason = RULE_CLASSES[cls]
        for m in mm:
            out.append({'class': cls, 'rules_match': status, 'reason': reason, 'kalshi_event': k,
                         'kalshi_series': ke['series'], 'kalshi_title': ke['title'], 'kalshi_ticker': m['kalshi'],
                         'kalshi_label': m['kalshi_label'], 'kalshi_fee_multiplier': ke.get('fee_multiplier') or 1,
                         'pm_event': r['pm_event'], 'pm_title': r['pm_title'], 'pm_market': m['pm_market'],
                         'pm_label': m['pm_label'], 'pm_yes_token': m['pm_yes_token'], 'pm_no_token': m['pm_no_token'],
                         'pm_yes_outcome': m['pm_yes_outcome'], 'pm_fee_rate': m['pm_fee_rate'], 'form': m['form'],
                         'kalshi_close': m['kalshi_close'], 'pm_close': m['pm_close'],
                         'kalshi_rules': m['kalshi_rules'][:400], 'pm_rules': m['pm_rules'][:400],
                         'match_score': r['score'], 'label_score': m['label_score'], 'source': 'auto',
                         'note': '%s on Kalshi (%s) = %s on Polymarket (%s): %s; event-title overlap %.2f, outcome-label '
                                 'overlap %.2f; %s.' % (m['kalshi_label'], m['kalshi'], m['pm_yes_outcome'] if m['form'] == 'outcome'
                                                         else 'YES on "%s"' % m['pm_label'], r['pm_event'],
                                                         ('same game date %s' % r['kalshi_date']) if r['kind'] == 'sports'
                                                         else 'same office and place', r['score'], m['label_score'],
                                                         status)})
        why['accepted events'] += 1
    return out, why


def manual_pairs(kev, pev, path):
    """Pairs a person mapped by hand (manual_matches.json): macro releases and anything whose outcome labels differ in
    wording. Each row names the Kalshi ticker, the Polymarket market (slug) and which Polymarket outcome pays when the
    Kalshi YES pays."""
    if not Path(path).exists():
        return []
    km = {m['id']: (e, m) for e in kev.values() for m in e['markets']}
    pm = {}
    for e in pev.values():
        for m in e['markets']:
            pm[m.get('slug')] = (e, m)
    out = []
    for row in json.loads(Path(path).read_text()):
        if row['kalshi_ticker'] not in km or row['pm_slug'] not in pm:
            print('manual pair not found: %s / %s' % (row['kalshi_ticker'], row['pm_slug']))
            continue
        ke, k = km[row['kalshi_ticker']]
        pe, m = pm[row['pm_slug']]
        outs = [str(o).lower() for o in m.get('outcomes') or []]
        yi = outs.index(row.get('pm_yes_outcome', 'yes').lower())
        out.append({'class': row['class'], 'rules_match': row['rules_match'], 'reason': row['reason'],
                    'kalshi_event': ke['event'], 'kalshi_series': ke['series'], 'kalshi_title': ke['title'],
                    'kalshi_ticker': k['id'], 'kalshi_label': k['label'], 'kalshi_fee_multiplier': ke.get('fee_multiplier') or 1,
                    'pm_event': pe['event'], 'pm_title': pe['title'], 'pm_market': m['id'], 'pm_label': m['label'],
                    'pm_yes_token': m['tokens'][yi], 'pm_no_token': m['tokens'][1 - yi],
                    'pm_yes_outcome': m['outcomes'][yi], 'pm_fee_rate': m.get('fee_rate'), 'form': 'manual',
                    'kalshi_close': k.get('close'), 'pm_close': m.get('close'), 'kalshi_rules': k.get('rules', '')[:400],
                    'pm_rules': (m.get('rules') or '')[:400], 'match_score': None, 'label_score': None,
                    'source': 'manual', 'note': 'mapped by hand: %s; %s.' % (row['reason'], row['rules_match'])})
    return out


def cmd_match(args):
    out = Path(args.out)
    raw = out / 'raw'
    kev, pev = kalshi_events(raw), pm_events(raw)
    C = json.loads((out / 'candidates.json').read_text())
    acc, why = accept_pairs(C['pairs'], kev, pev)
    man = manual_pairs(kev, pev, out / 'manual_matches.json')
    rows = acc + man
    import collections
    by = collections.Counter(r['class'] for r in rows)
    (out / 'matches.json').write_text(json.dumps({'generated': dt.datetime.now(UTC).isoformat(),
                                                  'rule_classes': {k: {'rules_match': v[0], 'reason': v[1]} for k, v in RULE_CLASSES.items()},
                                                  'acceptance': dict(why), 'pairs_by_class': dict(by),
                                                  'pairs': rows}, indent=1, default=str))
    print(json.dumps({'pairs': len(rows), 'by_class': dict(by), 'acceptance': dict(why)}, indent=1))
    return 0



# ------------------------------------------------------------------------------------------------ N-leg structures

def touch_n(legs, fees, payout=1.0):
    """Every leg at its best ask: the size all books show there, and the profit per set after each leg's fee.
    legs: ask ladders [(price, size)] best first; fees: callables (contracts, price) -> dollars."""
    if not legs or any(not l for l in legs):
        return None
    c = min(l[0][1] for l in legs)
    if c <= 0:
        return None
    prices = [l[0][0] for l in legs]
    f = sum(fee(c, p) for fee, p in zip(fees, prices))
    cost = c * sum(prices) + f
    return {'prices': prices, 'contracts': c, 'fees': f, 'cost': cost, 'profit': payout * c - cost,
            'gross_gap': payout - sum(prices), 'net_per_set': (payout * c - cost) / c}


def walk_n(legs, unit_fees, fees, payout=1.0, max_sets=None):
    """Walk every ladder together while the marginal set still pays after fees; fees on the filled totals per leg."""
    n = len(legs)
    if n == 0 or any(not l for l in legs):
        return None
    idx = [0] * n
    rem = [l[0][1] for l in legs]
    fills = [[] for _ in range(n)]
    total = 0.0
    while all(idx[i] < len(legs[i]) for i in range(n)):
        prices = [legs[i][idx[i]][0] for i in range(n)]
        if payout - sum(prices) - sum(uf(p) for uf, p in zip(unit_fees, prices)) <= 0:
            break
        q = min(rem)
        if max_sets is not None:
            q = min(q, max_sets - total)
        if q <= 0:
            break
        for i in range(n):
            fills[i].append((prices[i], q))
            rem[i] -= q
            if rem[i] <= 1e-9:
                idx[i] += 1
                rem[i] = legs[i][idx[i]][1] if idx[i] < len(legs[i]) else 0.0
        total += q
        if max_sets is not None and total >= max_sets:
            break
    if total <= 0:
        return None
    costs = [sum(p * q for p, q in f) for f in fills]
    f = sum(fee(total, c / total) for fee, c in zip(fees, costs))
    cost = sum(costs) + f
    return {'contracts': total, 'avg_prices': [c / total for c in costs], 'fees': f, 'cost': cost,
            'profit': payout * total - cost, 'net_per_set': (payout * total - cost) / total}


# ------------------------------------------------------------------------------------------------ books

def structures(matches, buckets):
    """Every arbitrage structure the matched pairs allow. A two-venue pair gives two (Kalshi YES + Polymarket's
    complement token, Kalshi NO + Polymarket's matching token), each paying $1; a three-leg bucket gives the $1 set
    (bucket YES, Above-low NO, Above-high YES) and its complement, which pays $2 in every state."""
    out = []
    for r in matches:
        base = {k: r[k] for k in ('class', 'rules_match', 'reason', 'kalshi_event', 'kalshi_title', 'pm_event',
                                  'pm_title', 'kalshi_close', 'pm_close', 'kalshi_label', 'pm_label')}
        rate = r.get('pm_fee_rate') or 0.0
        mult = r.get('kalshi_fee_multiplier') or 1
        out.append({**base, 'id': r['kalshi_ticker'] + ':yes', 'payout': 1.0,
                    'legs': [{'venue': 'kalshi', 'ticker': r['kalshi_ticker'], 'side': 'yes', 'mult': mult},
                             {'venue': 'polymarket', 'token': r['pm_no_token'], 'rate': rate}]})
        out.append({**base, 'id': r['kalshi_ticker'] + ':no', 'payout': 1.0,
                    'legs': [{'venue': 'kalshi', 'ticker': r['kalshi_ticker'], 'side': 'no', 'mult': mult},
                             {'venue': 'polymarket', 'token': r['pm_yes_token'], 'rate': rate}]})
    for b in buckets:
        base = {k: b.get(k) for k in ('class', 'rules_match', 'reason', 'kalshi_event', 'kalshi_title', 'pm_event',
                                      'pm_title', 'kalshi_close', 'pm_close', 'kalshi_label', 'pm_label')}
        rate, mult = b.get('pm_fee_rate') or 0.0, b.get('kalshi_fee_multiplier') or 1
        out.append({**base, 'id': b['pm_slug'] + ':set', 'payout': 1.0,
                    'legs': [{'venue': 'polymarket', 'token': b['pm_yes_token'], 'rate': rate},
                             {'venue': 'kalshi', 'ticker': b['kalshi_low'], 'side': 'no', 'mult': mult},
                             {'venue': 'kalshi', 'ticker': b['kalshi_high'], 'side': 'yes', 'mult': mult}]})
        out.append({**base, 'id': b['pm_slug'] + ':complement', 'payout': 2.0,
                    'legs': [{'venue': 'polymarket', 'token': b['pm_no_token'], 'rate': rate},
                             {'venue': 'kalshi', 'ticker': b['kalshi_low'], 'side': 'yes', 'mult': mult},
                             {'venue': 'kalshi', 'ticker': b['kalshi_high'], 'side': 'no', 'mult': mult}]})
    return out


def resolve_buckets(kev, pev, path):
    if not Path(path).exists():
        return []
    km = {m['id']: (e, m) for e in kev.values() for m in e['markets']}
    pm = {m.get('slug'): (e, m) for e in pev.values() for m in e['markets']}
    out = []
    for b in json.loads(Path(path).read_text()):
        if b['pm_slug'] not in pm or b['kalshi_low'] not in km or b['kalshi_high'] not in km:
            print('bucket not found: %s' % b['pm_slug'])
            continue
        pe, m = pm[b['pm_slug']]
        ke, kl = km[b['kalshi_low']]
        out.append({**b, 'pm_yes_token': m['tokens'][0], 'pm_no_token': m['tokens'][1], 'pm_fee_rate': m.get('fee_rate'),
                    'kalshi_fee_multiplier': ke.get('fee_multiplier') or 1, 'kalshi_event': ke['event'],
                    'kalshi_title': ke['title'], 'pm_event': pe['event'], 'pm_title': pe['title'],
                    'kalshi_close': kl.get('close'), 'pm_close': m.get('close'),
                    'kalshi_label': '%s / %s' % (b['kalshi_low'], b['kalshi_high']), 'pm_label': m['label']})
    return out


def kalshi_tops(tickers, raw_dir):
    """Fresh top of book for many Kalshi markets at once: YES ask and NO ask (1 - YES bid) with their sizes."""
    out = {}
    tickers = sorted(set(tickers))
    for i in range(0, len(tickers), 100):
        chunk = tickers[i:i + 100]
        d = http_json(KALSHI + 'markets?' + urllib.parse.urlencode({'tickers': ','.join(chunk), 'limit': 1000}), 'kalshi')
        for m in (d or {}).get('markets') or []:
            ya, yas = fnum(m.get('yes_ask_dollars')), fnum(m.get('yes_ask_size_fp'), 0.0)
            yb, ybs = fnum(m.get('yes_bid_dollars')), fnum(m.get('yes_bid_size_fp'), 0.0)
            out[m['ticker']] = {'yes': [(ya, yas)] if (ya and 0 < ya < 1 and yas) else [],
                                'no': [(round(1.0 - yb, 4), ybs)] if (yb and 0 < yb < 1 and ybs) else [],
                                'status': m.get('status'), 'close': m.get('close_time'),
                                'expected_expiration': m.get('expected_expiration_time')}
    return out


def pm_books(tokens):
    """Full Polymarket books for many tokens at once (POST /books)."""
    out = {}
    tokens = sorted(set(t for t in tokens if t))
    for i in range(0, len(tokens), 100):
        chunk = tokens[i:i + 100]
        body = json.dumps([{'token_id': t} for t in chunk]).encode()
        wait = PACE['clob'] - (time.monotonic() - _last.get('clob', 0.0))
        if wait > 0:
            time.sleep(wait)
        for a in range(6):
            _last['clob'] = time.monotonic()
            try:
                req = urllib.request.Request(CLOB + 'books', data=body, headers={'Content-Type': 'application/json',
                                                                                   'User-Agent': UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    for b in json.loads(r.read().decode()):
                        out[b['asset_id']] = {'asks': pm_asks(b), 'tick': fnum(b.get('tick_size')),
                                              'min_size': fnum(b.get('min_order_size')), 'ts': b.get('timestamp')}
                break
            except Exception as e:  # noqa: BLE001
                time.sleep(min(20.0, 1.5 * 2 ** a))
    return out


def leg_fees(leg):
    if leg['venue'] == 'kalshi':
        m = leg.get('mult') or 1
        return (lambda c, p: kalshi_fee(c, p, m)), (lambda p: KALSHI_TAKER_RATE * m * p * (1 - p))
    r = leg.get('rate') or 0.0
    return (lambda c, p: polymarket_fee(c, p, r)), (lambda p: r * p * (1 - p))


def ladders(st, ktops, pbooks, kbooks=None):
    out = []
    for leg in st['legs']:
        if leg['venue'] == 'kalshi':
            if kbooks is not None and leg['ticker'] in kbooks:
                ya, na = kbooks[leg['ticker']]
                out.append(ya if leg['side'] == 'yes' else na)
            else:
                out.append((ktops.get(leg['ticker']) or {}).get(leg['side']) or [])
        else:
            out.append((pbooks.get(leg['token']) or {}).get('asks') or [])
    return out


def evaluate(st, lads, now):
    fees = [leg_fees(l)[0] for l in st['legs']]
    units = [leg_fees(l)[1] for l in st['legs']]
    t = touch_n(lads, fees, st['payout'])
    w = walk_n(lads, units, fees, st['payout'])
    closes = [parse_time(st.get('pm_close')), parse_time(st.get('kalshi_close'))]
    pm_c = parse_time(st.get('pm_close'))
    days_pm = max(0.0, (pm_c - now).total_seconds() / 86400) if pm_c else None
    k_c = parse_time(st.get('kalshi_close'))
    days_k = max(0.0, (k_c - now).total_seconds() / 86400) if k_c else None
    # Expected resolution: the later venue's close, except elections, where Kalshi resolves early on a media consensus
    # (its listed close is a year out) - there the Polymarket close plus a week is used, and the listed close is kept.
    if st['class'] in ('election_party', 'chamber_control') and days_pm is not None:
        days = days_pm + 7.0
    else:
        days = max([d for d in (days_pm, days_k) if d is not None] or [1.0])
    res = {'id': st['id'], 'class': st['class'], 'rules_match': st['rules_match'], 'payout': st['payout'],
           'days_to_resolution': days, 'days_to_pm_close': days_pm, 'days_to_kalshi_close': days_k,
           'touch': t, 'walk': w, 'legs': [l.get('ticker') or (l.get('token') or '')[:12] + '..' for l in st['legs']],
           'kalshi_title': st.get('kalshi_title'), 'pm_title': st.get('pm_title'), 'kalshi_label': st.get('kalshi_label'),
           'pm_label': st.get('pm_label')}
    for key, x in (('touch', t), ('walk', w)):
        if x and x['profit'] > 0:
            a, an = annualise(x['profit'], x['cost'], days)
            res[key + '_apr'], res[key + '_apr_net_ssr'] = a, an
    return res


def cmd_books(args):
    out = Path(args.out)
    raw = out / 'raw'
    kev, pev = kalshi_events(raw), pm_events(raw)
    M = json.loads((out / 'matches.json').read_text())
    buckets = resolve_buckets(kev, pev, out / 'manual_buckets.json')
    sts = structures(M['pairs'], buckets)
    t0 = dt.datetime.now(UTC)
    ktops = kalshi_tops([l['ticker'] for s_ in sts for l in s_['legs'] if l['venue'] == 'kalshi'], raw)
    t1 = dt.datetime.now(UTC)
    pbooks = pm_books([l['token'] for s_ in sts for l in s_['legs'] if l['venue'] == 'polymarket'])
    t2 = dt.datetime.now(UTC)
    screen = [evaluate(s_, ladders(s_, ktops, pbooks), t2) for s_ in sts]
    hot = [x for x in screen if x['touch'] and x['touch']['gross_gap'] > args.screen_gap]
    # confirm: both venues' full books read back to back, then evaluated together
    by_id = {s_['id']: s_ for s_ in sts}
    confirmed = []
    for x in hot:
        st = by_id[x['id']]
        kb = {}
        for leg in st['legs']:
            if leg['venue'] == 'kalshi':
                ob = http_json(KALSHI + 'markets/%s/orderbook' % leg['ticker'], 'kalshi')
                if ob:
                    kb[leg['ticker']] = kalshi_asks(ob)
        pb = pm_books([leg['token'] for leg in st['legs'] if leg['venue'] == 'polymarket'])
        now = dt.datetime.now(UTC)
        c = evaluate(st, ladders(st, {}, pb, kb), now)
        c['confirmed_at'] = now.isoformat()
        c['screen_touch'] = x['touch']
        confirmed.append(c)
    res = {'generated': t2.isoformat(), 'kalshi_read': [t0.isoformat(), t1.isoformat()],
           'polymarket_read': [t1.isoformat(), t2.isoformat()], 'structures': len(sts),
           'screen_gap_threshold': args.screen_gap, 'screen': screen, 'confirmed': confirmed}
    (out / ('books_%s.json' % t2.strftime('%Y%m%dT%H%M'))).write_text(json.dumps(res, default=str))
    (out / 'books.json').write_text(json.dumps(res, default=str))
    pos = [c for c in confirmed if c['touch'] and c['touch']['profit'] > 0]
    print(json.dumps({'structures': len(sts), 'kalshi_tops': len(ktops), 'pm_books': len(pbooks),
                      'screen_positive_gross': len(hot), 'confirmed_positive_after_fees': len(pos),
                      'seconds': round((dt.datetime.now(UTC) - t0).total_seconds(), 1)}))
    return 0



# ------------------------------------------------------------------------------------------------ history

def kalshi_candles(series, ticker, start_ts, end_ts, raw):
    cache = raw / 'history' / 'kalshi' / ('%s.json' % ticker)
    d = http_json(KALSHI + 'series/%s/markets/%s/candlesticks?%s' % (series, ticker, urllib.parse.urlencode(
        {'start_ts': int(start_ts), 'end_ts': int(end_ts), 'period_interval': 60})), 'kalshi', cache=cache)
    out = {}
    for c in (d or {}).get('candlesticks') or []:
        yb = fnum(((c.get('yes_bid') or {}).get('close_dollars')))
        ya = fnum(((c.get('yes_ask') or {}).get('close_dollars')))
        out[int(c['end_period_ts'])] = {'yes_bid': yb, 'yes_ask': ya, 'volume': fnum(c.get('volume_fp'), 0.0)}
    return out


def pm_history(token, start_ts, end_ts, raw, window_days=14):
    """Hourly Polymarket prices for a token, fetched in 14-day windows (a 30-day window is refused with HTTP 400)."""
    cache = raw / 'history' / 'polymarket' / ('%s.json' % token[:40])
    if cache.exists():
        rows = json.loads(cache.read_text())
    else:
        rows = []
        t, end_ts = int(start_ts), int(end_ts)      # an integer end, or the last window never closes
        while t < end_ts:
            e = min(end_ts, t + window_days * 86400)
            d = http_json(CLOB + 'prices-history?' + urllib.parse.urlencode({'market': token, 'startTs': t, 'endTs': e,
                                                                             'fidelity': 60}), 'clob')
            rows.extend((d or {}).get('history') or [])
            t = e
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(rows))
    out = {}
    for r in rows:
        # Polymarket's hourly points land within a minute after the hour (99.5% in the first minute on 2026-10-09);
        # Kalshi's candle for the hour that just ended closes at that same boundary, so both stamp to the boundary.
        # (Stamping to the next boundary compared prices an hour apart and manufactured gaps in fast markets.)
        out[int(r['t']) // 3600 * 3600] = float(r['p'])
    return out


def gap_series(kc, pmh, pm_half_spread, rate, mult):
    """Per hour where both venues printed: the better direction's net gap per $1 set after fees.

    Kalshi side uses its hourly closing YES bid and ask (executable top of book at the close of the hour); the
    Polymarket side is the hourly price (a trade or midpoint, not executable) plus an assumed half spread, so the series
    is an upper bound when the half spread is set to zero and an estimate otherwise."""
    rows = []
    for t in sorted(set(kc) & set(pmh)):
        k, p = kc[t], pmh[t]
        best = None
        if k['yes_ask'] and 0 < k['yes_ask'] < 1:
            a1, a2 = k['yes_ask'], min(1.0, 1.0 - p + pm_half_spread)        # Kalshi YES + Polymarket NO
            net = 1.0 - a1 - a2 - KALSHI_TAKER_RATE * mult * a1 * (1 - a1) - rate * a2 * (1 - a2)
            best = (net, 'kalshi_yes', a1, a2)
        if k['yes_bid'] and 0 < k['yes_bid'] < 1:
            a1, a2 = 1.0 - k['yes_bid'], min(1.0, p + pm_half_spread)        # Kalshi NO + Polymarket YES
            net = 1.0 - a1 - a2 - KALSHI_TAKER_RATE * mult * a1 * (1 - a1) - rate * a2 * (1 - a2)
            if best is None or net > best[0]:
                best = (net, 'kalshi_no', a1, a2)
        if best:
            spread = (k['yes_ask'] - k['yes_bid']) if (k['yes_ask'] and k['yes_bid']) else None
            rows.append({'t': t, 'net': best[0], 'dir': best[1], 'k_ask': best[2], 'p_ask': best[3],
                         'k_volume': k['volume'], 'k_spread': spread})
    return rows


MAX_KALSHI_SPREAD = 0.05     # an hour whose Kalshi book was wider than this is a stale or empty book, not a price
MAX_PM_HALF_SPREAD = 0.025   # a Polymarket market this wide today has no reliable displayed price


def liquid(row, pair):
    return (row.get('k_spread') is not None and row['k_spread'] <= MAX_KALSHI_SPREAD
            and (pair.get('pm_half_spread_used') or 0.0) <= MAX_PM_HALF_SPREAD)


def episodes(rows, threshold=0.0):
    """Runs of consecutive hours with a net gap above the threshold: start, hours, peak, and the gap an hour after."""
    out, cur = [], None
    for i, r in enumerate(rows):
        if r['net'] > threshold:
            if cur and r['t'] - cur['last'] <= 3600:
                cur['hours'] += 1
                cur['peak'] = max(cur['peak'], r['net'])
                cur['last'] = r['t']
            else:
                if cur:
                    out.append(cur)
                cur = {'start': r['t'], 'last': r['t'], 'hours': 1, 'peak': r['net']}
        elif cur and r['t'] - cur['last'] > 0:
            out.append(cur)
            cur = None
    if cur:
        out.append(cur)
    return out


def pm_half_spreads(books_path):
    """Half the Polymarket YES spread per matched Kalshi ticker, from a books snapshot: the ':no' structure's second
    leg is the YES ask and the ':yes' structure's second leg is the NO ask, i.e. one minus the YES bid."""
    if not Path(books_path).exists():
        return {}
    B = json.loads(Path(books_path).read_text())
    ya, nb = {}, {}
    for x in B.get('screen') or []:
        if not x.get('touch') or len(x['touch']['prices']) != 2:
            continue
        tk, d = x['id'].rsplit(':', 1)
        if d == 'no':
            ya[tk] = x['touch']['prices'][1]
        elif d == 'yes':
            nb[tk] = x['touch']['prices'][1]
    return {tk: max(0.0, (ya[tk] - (1.0 - nb[tk])) / 2.0) for tk in ya if tk in nb}


def cmd_history(args):
    out = Path(args.out)
    raw = out / 'raw'
    kev = kalshi_events(raw)
    M = json.loads((out / 'matches.json').read_text())
    kvol = {m['id']: (m.get('volume') or 0) for e in kev.values() for m in e['markets']}
    kser = {m['id']: e['series'] for e in kev.values() for m in e['markets']}
    pairs = [r for r in M['pairs'] if r['class'] in ('chamber_control', 'fomc', 'cpi_release')]
    el = sorted([r for r in M['pairs'] if r['class'] == 'election_party'], key=lambda r: -kvol.get(r['kalshi_ticker'], 0))
    pairs += el[:args.top_elections]
    if args.sports:
        sp = sorted([r for r in M['pairs'] if r['class'] not in ('chamber_control', 'fomc', 'cpi_release', 'election_party')],
                    key=lambda r: -kvol.get(r['kalshi_ticker'], 0))
        pairs += sp[:args.sports]
    end = time.time()
    start = end - args.days * 86400
    hs_now = pm_half_spreads(out / 'books.json')
    res = []
    for i, r in enumerate(pairs):
        kc = kalshi_candles(kser.get(r['kalshi_ticker']) or r['kalshi_series'], r['kalshi_ticker'], start, end, raw)
        pmh = pm_history(r['pm_yes_token'], start, end, raw)
        rate = r.get('pm_fee_rate') or 0.0
        mult = r.get('kalshi_fee_multiplier') or 1
        # the Polymarket side is a displayed price (midpoint, or last trade when the spread exceeds 10c): add the
        # market's own half spread read from the latest books snapshot, never less than the floor
        hs = max(args.pm_half_spread, hs_now.get(r['kalshi_ticker']) or 0.0)
        rows = gap_series(kc, pmh, hs, rate, mult)
        rows0 = gap_series(kc, pmh, 0.0, rate, mult)
        ep = episodes(rows)
        res.append({'kalshi_ticker': r['kalshi_ticker'], 'class': r['class'], 'kalshi_title': r['kalshi_title'],
                    'pm_half_spread_used': hs, 'pm_close': r.get('pm_close'), 'kalshi_close': r.get('kalshi_close'),
                    'kalshi_label': r['kalshi_label'], 'pm_title': r['pm_title'], 'pm_label': r['pm_label'],
                    'hours_both': len(rows), 'kalshi_hours': len(kc), 'pm_hours': len(pmh),
                    'hours_positive': sum(1 for x in rows if x['net'] > 0),
                    'hours_positive_upper_bound': sum(1 for x in rows0 if x['net'] > 0),
                    'hours_over_1c': sum(1 for x in rows if x['net'] > 0.01),
                    'median_net': statistics.median([x['net'] for x in rows]) if rows else None,
                    'max_net': max([x['net'] for x in rows]) if rows else None,
                    'episodes': ep, 'series': rows})
        if i % 10 == 0:
            print('%d/%d %s hours %d positive %d' % (i + 1, len(pairs), r['kalshi_ticker'], len(rows),
                                                      res[-1]['hours_positive']), flush=True)
    (out / 'history.json').write_text(json.dumps({'generated': dt.datetime.now(UTC).isoformat(), 'days': args.days,
                                                  'pm_half_spread': args.pm_half_spread, 'pairs': res}, default=str))
    print(json.dumps({'pairs': len(res), 'hours_both': sum(x['hours_both'] for x in res),
                      'hours_positive': sum(x['hours_positive'] for x in res),
                      'hours_positive_upper_bound': sum(x['hours_positive_upper_bound'] for x in res)}))
    return 0



# ------------------------------------------------------------------------------------------------ analyze / render

def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    return xs[min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))]


def snapshot_summary(B):
    sc = [x for x in B['screen'] if x.get('touch')]
    gross = [x['touch']['gross_gap'] for x in sc]
    conf = B.get('confirmed') or []
    pos = [c for c in conf if c.get('touch') and c['touch']['profit'] > 0]
    walked = [c for c in pos if c.get('walk')]
    by_class = {}
    for x in sc:
        d = by_class.setdefault(x['class'], {'structures': 0, 'gross_positive': 0, 'gross': []})
        d['structures'] += 1
        d['gross'].append(x['touch']['gross_gap'])
        d['gross_positive'] += x['touch']['gross_gap'] > 0
    for c in pos:
        d = by_class.setdefault(c['class'], {'structures': 0, 'gross_positive': 0, 'gross': []})
        d['confirmed_positive'] = d.get('confirmed_positive', 0) + 1
        d['touch_profit'] = d.get('touch_profit', 0.0) + c['touch']['profit']
        d['walk_profit'] = d.get('walk_profit', 0.0) + ((c.get('walk') or {}).get('profit') or 0.0)
        d['walk_capital'] = d.get('walk_capital', 0.0) + ((c.get('walk') or {}).get('cost') or 0.0)
    for d in by_class.values():
        g = d.pop('gross')
        d['median_gross_gap'] = statistics.median(g) if g else None
        d['p95_gross_gap'] = pct(g, 0.95)
    aprs = [c['walk_apr_net_ssr'] for c in walked if c.get('walk_apr_net_ssr') is not None]
    best = max(walked, key=lambda c: c['walk']['profit']) if walked else None
    return {
        'generated': B['generated'], 'structures': B['structures'], 'with_touch_on_all_legs': len(sc),
        'median_gross_gap': statistics.median(gross) if gross else None, 'p95_gross_gap': pct(gross, 0.95),
        'gross_positive_share': (sum(1 for g in gross if g > 0) / len(gross)) if gross else None,
        'screened_for_confirmation': len(conf), 'confirmed_positive_after_fees': len(pos),
        'confirmed_net_per_set_median': statistics.median([c['touch']['net_per_set'] for c in pos]) if pos else None,
        'touch_contracts_total': sum(c['touch']['contracts'] for c in pos),
        'touch_profit_total': sum(c['touch']['profit'] for c in pos),
        'walk_profit_total': sum(c['walk']['profit'] for c in walked),
        'walk_capital_total': sum(c['walk']['cost'] for c in walked),
        'walk_apr_net_ssr_median': statistics.median(aprs) if aprs else None,
        'walk_apr_net_ssr_positive': sum(1 for a in aprs if a > 0),
        'best': ({'id': best['id'], 'class': best['class'], 'kalshi_title': best['kalshi_title'],
                  'kalshi_label': best['kalshi_label'], 'pm_title': best['pm_title'],
                  'profit': best['walk']['profit'], 'cost': best['walk']['cost'], 'sets': best['walk']['contracts'],
                  'days': best['days_to_resolution'], 'apr_net_ssr': best.get('walk_apr_net_ssr')} if best else None),
        'by_class': by_class,
    }


def history_summary(H):
    pairs = [dict(r, series=[x for x in r['series'] if liquid(x, r)]) for r in H['pairs']]
    dropped = sum(len(r['series']) for r in H['pairs']) - sum(len(r['series']) for r in pairs)
    for r in pairs:
        r['hours_both'] = len(r['series'])
        r['hours_positive'] = sum(1 for x in r['series'] if x['net'] > 0)
        r['hours_over_1c'] = sum(1 for x in r['series'] if x['net'] > 0.01)
        r['episodes'] = episodes(r['series'])
    by_class = {}
    eps_all = []
    for r in pairs:
        d = by_class.setdefault(r['class'], {'pairs': 0, 'hours': 0, 'hours_positive': 0, 'hours_positive_ub': 0,
                                              'hours_over_1c': 0, 'episodes': 0})
        d['pairs'] += 1
        d['hours'] += r['hours_both']
        d['hours_positive'] += r['hours_positive']
        d['hours_positive_ub'] += r['hours_positive_upper_bound']
        d['hours_over_1c'] += r['hours_over_1c']
        d['episodes'] += len(r['episodes'])
        eps_all += [dict(e, ticker=r['kalshi_ticker'], cls=r['class']) for e in r['episodes']]
    for d in by_class.values():
        d['share_positive'] = d['hours_positive'] / d['hours'] if d['hours'] else None
        d['share_positive_ub'] = d['hours_positive_ub'] / d['hours'] if d['hours'] else None
    # stability: first against second half of the window
    ts = [x['t'] for r in pairs for x in r['series']]
    split = {}
    if ts:
        mid = (min(ts) + max(ts)) / 2
        for half, sel in (('first_half', lambda t: t < mid), ('second_half', lambda t: t >= mid)):
            xs = [x for r in pairs for x in r['series'] if sel(x['t'])]
            split[half] = {'hours': len(xs), 'positive': sum(1 for x in xs if x['net'] > 0),
                           'over_1c': sum(1 for x in xs if x['net'] > 0.01),
                           'mean_positive_net': statistics.fmean([x['net'] for x in xs if x['net'] > 0])
                           if any(x['net'] > 0 for x in xs) else None}
        split['midpoint'] = dt.datetime.fromtimestamp(mid, UTC).isoformat()
    durations = [e['hours'] for e in eps_all]
    top = sorted(eps_all, key=lambda e: -e['peak'])[:15]
    return {'pairs': len(pairs), 'days': H['days'], 'pm_half_spread': H['pm_half_spread'], 'by_class': by_class,
            'illiquid_hours_dropped': dropped, 'max_kalshi_spread': MAX_KALSHI_SPREAD,
            'max_pm_half_spread': MAX_PM_HALF_SPREAD,
            'episodes': len(eps_all), 'episode_hours_median': statistics.median(durations) if durations else None,
            'episode_hours_p90': pct(durations, 0.9), 'episodes_over_24h': sum(1 for d in durations if d >= 24),
            'top_episodes': [{'ticker': e['ticker'], 'class': e['cls'], 'hours': e['hours'], 'peak': e['peak'],
                              'start': dt.datetime.fromtimestamp(e['start'], UTC).isoformat()} for e in top],
            'split': split}


def resolution_ts(cls, pm_close, kalshi_close):
    """Expected resolution: elections resolve on the media call (Kalshi's listed close is a year out), taken as the
    Polymarket close plus a week; everything else at the later of the two venues' closes."""
    pc, kc = parse_time(pm_close), parse_time(kalshi_close)
    if cls in ('election_party', 'chamber_control') and pc:
        return (pc + dt.timedelta(days=7)).timestamp()
    xs = [d.timestamp() for d in (pc, kc) if d]
    return max(xs) if xs else None


def history_strategy(H, books, hurdles=(0.0, 0.05, 0.10, 0.20), clip_usd=25_000.0,
                     classes=('election_party', 'chamber_control', 'fomc', 'cpi_release')):
    """What a monitor that locks a pair whenever its annualised gap clears a hurdle would have booked over the window.

    Each episode (consecutive hours above the hurdle) is entered once, at its first hour, for a clip equal to the size
    both books show at the touch in the latest snapshot for that direction (capped at clip_usd) - the only depth this
    study observed, so the dollar figures are an order of magnitude, not a fill record. The gain is locked at entry
    (the pair pays $1 at resolution) and the capital stays out until the expected resolution. The Polymarket leg is
    the displayed price plus the market's half spread, so the series is an estimate, not an execution log."""
    touch = {x['id']: x['touch'] for x in (books.get('screen') or []) if x.get('touch')}
    out = {}
    for h in hurdles:
        daily_gain, eps, opens = {}, [], []
        for r in H['pairs']:
            if r['class'] not in classes:
                continue
            R = resolution_ts(r['class'], r.get('pm_close'), r.get('kalshi_close'))
            if R is None:
                continue
            prev_t, in_ep = None, False
            for x in (y for y in r['series'] if liquid(y, r)):
                cost = 1.0 - x['net']
                days = max(1.0, (R - x['t']) / 86400.0)
                apr = (x['net'] / cost * 365.0 / days - SSR) if x['net'] > 0 else -1.0
                hot = apr > h
                cont = prev_t is not None and x['t'] - prev_t <= 3600
                if hot and not (in_ep and cont):
                    tk = r['kalshi_ticker'] + (':yes' if x['dir'] == 'kalshi_yes' else ':no')
                    t = touch.get(tk)
                    if t:
                        sets = min(t['contracts'], clip_usd / cost)
                        gain, cap = x['net'] * sets, cost * sets
                        d = dt.datetime.fromtimestamp(x['t'], UTC).date().isoformat()
                        daily_gain[d] = daily_gain.get(d, 0.0) + gain
                        eps.append({'ticker': r['kalshi_ticker'], 't': x['t'], 'net': x['net'], 'apr_net_ssr': apr,
                                    'sets': sets, 'gain': gain, 'capital': cap})
                        opens.append((x['t'], R, cap))
                in_ep = hot
                prev_t = x['t']
        if not eps:
            out['%.2f' % h] = {'episodes': 0}
            continue
        t0 = min(H_t for H_t, _, _ in opens)
        t1 = max(x['t'] for r in H['pairs'] for x in r['series'])
        days = sorted({dt.datetime.fromtimestamp(t, UTC).date().isoformat()
                       for t in range(int(t0) // 86400 * 86400, int(t1) + 1, 86400)})
        # capital outstanding each day
        cap_day = {d: sum(c for (a, b, c) in opens if a <= dt.datetime.fromisoformat(d + 'T23:59:59+00:00').timestamp() < b)
                   for d in days}
        peak = max(cap_day.values()) if cap_day else 0.0
        total = sum(e['gain'] for e in eps)
        span = max(1.0, (t1 - t0) / 86400.0)
        avg_cap = statistics.fmean(cap_day.values()) if cap_day else 0.0
        mid = t0 + (t1 - t0) / 2.0
        g1 = sum(e['gain'] for e in eps if e['t'] < mid)
        g2 = total - g1
        out['%.2f' % h] = {'episodes': len(eps), 'gain_total': total, 'peak_capital': peak,
                           'average_capital': avg_cap,
                           'annualised_on_average_capital': (total / avg_cap * 365.0 / span) if avg_cap else None,
                           'gain_first_half': g1, 'gain_second_half': g2,
                           'episodes_first_half': sum(1 for e in eps if e['t'] < mid),
                           'episodes_second_half': sum(1 for e in eps if e['t'] >= mid),
                           'annualised_on_peak_capital': (total / peak * 365.0 / span) if peak else None,
                           'gain_per_year': total * 365.0 / span, 'span_days': span,
                           'median_episode_gain': statistics.median([e['gain'] for e in eps]),
                           'weekly_gain': {wk: sum(e['gain'] for e in eps
                                                   if dt.datetime.fromtimestamp(e['t'], UTC).strftime('%G-W%V') == wk)
                                           for wk in sorted({dt.datetime.fromtimestamp(e['t'], UTC).strftime('%G-W%V')
                                                             for e in eps})},
                           'top': sorted(eps, key=lambda e: -e['gain'])[:8],
                           'daily': [daily_gain.get(d, 0.0) / peak if peak else 0.0 for d in days]}
    # protocol: choose the hurdle on the first half of days, report it on the second (backtest.choose_then_test)
    series = {k: v['daily'] for k, v in out.items() if v.get('episodes')}
    sel = B.choose_then_test(series, frac=0.5, periods_per_year=365.0) if len(series) > 1 else None
    for v in out.values():
        v.pop('daily', None)
    return {'by_hurdle': out, 'selection': sel, 'clip_usd': clip_usd, 'classes': list(classes)}


def venue_tilt(out, matches, H):
    """Kalshi's midpoint minus Polymarket's displayed price, hour by hour, from the cached history: by month for the
    chamber-control pairs, and averaged per race for the party-coded election markets (tickers ending -R / -D)."""
    raw = Path(out) / 'raw'
    mm = {r['kalshi_ticker']: r for r in matches['pairs']}
    kser = {r['kalshi_ticker']: r.get('kalshi_series') for r in matches['pairs']}

    def mids(tk):
        kc = raw / 'history' / 'kalshi' / ('%s.json' % tk)
        r = mm.get(tk)
        if not kc.exists() or not r:
            return []
        pmh = pm_history(r['pm_yes_token'], 0, 0, raw)
        rows = []
        for c in (json.loads(kc.read_text()) or {}).get('candlesticks') or []:
            yb = fnum((c.get('yes_bid') or {}).get('close_dollars'))
            ya = fnum((c.get('yes_ask') or {}).get('close_dollars'))
            t = int(c['end_period_ts'])
            if yb and ya and 0 < yb < 1 and 0 < ya < 1 and t in pmh:
                rows.append((t, (yb + ya) / 2.0 - pmh[t]))
        return rows

    monthly = {}
    for tk in ('CONTROLH-2026-R', 'CONTROLS-2026-R'):
        by = {}
        for t, d in mids(tk):
            by.setdefault(dt.datetime.fromtimestamp(t, UTC).strftime('%Y-%m'), []).append(d)
        monthly[tk] = {m: statistics.fmean(v) for m, v in sorted(by.items())}
    party = {'R': [], 'D': []}
    for x in H['pairs']:
        tk = x['kalshi_ticker']
        if x['class'] == 'election_party' and tk[-2:] in ('-R', '-D'):
            rows = mids(tk)
            if rows:
                party[tk[-1]].append(statistics.fmean(d for _, d in rows))
    return {'chamber_control_monthly_kalshi_minus_polymarket': monthly,
            'party_coded_races': {k: {'races': len(v), 'mean_kalshi_minus_polymarket': statistics.fmean(v) if v else None,
                                      'share_kalshi_higher': (sum(1 for d in v if d > 0) / len(v)) if v else None}
                                  for k, v in party.items()}}


def proxy_check(H, books):
    """The history's last hour against the books read within three hours of it: the hourly proxy's net gap minus the
    executable net gap at the touch, same pair and direction. Tells how far the history can be trusted."""
    gen = parse_time(books.get('generated'))
    scr = {x['id']: x for x in books.get('screen') or [] if x.get('touch')}
    diffs, proxy_pos, live_pos, both = [], 0, 0, 0
    for p_ in H['pairs']:
        if not p_['series'] or gen is None:
            continue
        last = p_['series'][-1]
        if gen.timestamp() - last['t'] > 3 * 3600:
            continue
        s_ = scr.get(p_['kalshi_ticker'] + (':yes' if last['dir'] == 'kalshi_yes' else ':no'))
        if not s_:
            continue
        live = s_['touch']['net_per_set']
        diffs.append(last['net'] - live)
        proxy_pos += last['net'] > 0
        live_pos += live > 0
        both += last['net'] > 0 and live > 0
    if not diffs:
        return None
    return {'books_generated': books.get('generated'), 'pairs': len(diffs), 'proxy_positive': proxy_pos,
            'live_positive': live_pos, 'both_positive': both, 'median_proxy_minus_live': statistics.median(diffs),
            'mean_proxy_minus_live': statistics.fmean(diffs), 'p10': pct(diffs, 0.1), 'p90': pct(diffs, 0.9)}


def cmd_analyze(args):
    out = Path(args.out)
    M = json.loads((out / 'matches.json').read_text())
    C = json.loads((out / 'candidates.json').read_text())
    snaps = []
    for f in sorted(out.glob('books_*.json')):
        snaps.append(snapshot_summary(json.loads(f.read_text())))
    H = json.loads((out / 'history.json').read_text()) if (out / 'history.json').exists() else None
    import collections
    rm = collections.Counter(r['rules_match'] for r in M['pairs'])
    res = {'generated': dt.datetime.now(UTC).isoformat(), 'ssr': SSR,
           'universe': {'kalshi_events_with_markets': C['kalshi_events'], 'pm_events_active': C['pm_events'],
                        'candidate_pairs': len(C['pairs'])},
           'matches': {'pairs': len(M['pairs']), 'by_class': M['pairs_by_class'], 'acceptance': M['acceptance'],
                       'rules_match': dict(rm),
                       'events': len({r['kalshi_event'] for r in M['pairs']})},
           'snapshots': snaps, 'history': history_summary(H) if H else None,
           'history_strategy': history_strategy(H, json.loads((out / 'books.json').read_text())) if H else None,
           'venue_tilt': venue_tilt(out, M, H) if H else None,
           'proxy_check': proxy_check(H, json.loads((out / 'books.json').read_text())) if H else None}
    (out / 'analysis.json').write_text(json.dumps(res, indent=1, default=str))
    raw = out / 'raw'
    stamp = lambda f: dt.datetime.fromtimestamp(f.stat().st_mtime, UTC).isoformat() if f.exists() else None
    write_manifest(out, 'analyze', {
        'raw': {'kalshi_events_open': stamp(raw / 'kalshi' / 'events_open.json'),
                'kalshi_markets_dir_files': len(list((raw / 'kalshi' / 'markets').glob('*.json'))),
                'kalshi_series_all': stamp(raw / 'kalshi' / 'series_all.json'),
                'polymarket_events_all': stamp(raw / 'pm_events' / 'events_all.json.gz'),
                'limitless_markets_active': stamp(raw / 'limitless' / 'markets_active.json'),
                'history_files': len(list((raw / 'history').rglob('*.json'))) if (raw / 'history').exists() else 0},
        'books_snapshots': [s_['generated'] for s_ in snaps],
        'matches': res['matches']['pairs'], 'history_pairs': (res['history'] or {}).get('pairs'),
        'note': 'The raw universe (2026-10-09 ~20:13-20:30 UTC) was fetched by scratch copies of fetch_kalshi_events, '
                'fetch_kalshi_markets, fetch_polymarket_events and fetch_limitless; `snapshot` is the packaged form '
                'and was not re-run against the venues.'})
    print(json.dumps({'snapshots': [{k: s_[k] for k in ('generated', 'structures', 'confirmed_positive_after_fees',
                                                          'walk_profit_total', 'walk_capital_total')} for s_ in snaps],
                      'history_pairs': (res['history'] or {}).get('pairs')}, indent=1, default=str))
    return 0


def money(x):
    return '—' if x is None else '$%s' % format(round(x, 2), ',')


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# Kalshi against Polymarket — tables', '', 'Generated %s from `analysis.json`.' % A['generated'], '',
         '## Matching', '',
         'Kalshi events with markets read: %d; Polymarket active events: %d; candidate event pairs: %d; accepted market '
         'pairs: %d across %d Kalshi events.' % (A['universe']['kalshi_events_with_markets'], A['universe']['pm_events_active'],
                                                 A['universe']['candidate_pairs'], A['matches']['pairs'], A['matches']['events']), '',
         '| class | market pairs |', '|---|---:|']
    for k, v in sorted(A['matches']['by_class'].items(), key=lambda x: -x[1]):
        L.append('| %s | %d |' % (k, v))
    L += ['', 'Rejected at acceptance: ' + '; '.join('%s %d' % (k, v) for k, v in A['matches']['acceptance'].items()
                                                    if k != 'accepted events'), '']
    for s_ in A['snapshots']:
        L += ['## Snapshot %s' % s_['generated'], '',
              '| | |', '|---|---:|',
              '| structures priced (two directions per pair, two per bucket) | %d |' % s_['structures'],
              '| with an ask on every leg | %d |' % s_['with_touch_on_all_legs'],
              '| median gross gap at the touch (1 − cost per $1 set) | %.2f¢ |' % (100 * s_['median_gross_gap']),
              '| 95th percentile gross gap | %.2f¢ |' % (100 * s_['p95_gross_gap']),
              '| share with a positive gross gap | %.1f%% |' % (100 * s_['gross_positive_share']),
              '| positive after fees on a back-to-back read of both books | %d |' % s_['confirmed_positive_after_fees'],
              '| contracts at the touch, all of them | %s |' % format(round(s_['touch_contracts_total']), ','),
              '| profit at the touch, all of them | %s |' % money(s_['touch_profit_total']),
              '| profit walking both books, all of them | %s on %s of capital |' % (money(s_['walk_profit_total']), money(s_['walk_capital_total'])),
              '| median annualised return net of SSR, walked | %s |' % (('%.1f%%' % (100 * s_['walk_apr_net_ssr_median'])) if s_['walk_apr_net_ssr_median'] is not None else '—'),
              '', '| class | structures | gross > 0 | median gross | confirmed > 0 | walked profit | capital |',
              '|---|---:|---:|---:|---:|---:|---:|']
        for k, d in sorted(s_['by_class'].items(), key=lambda x: -x[1]['structures']):
            L.append('| %s | %d | %d | %s | %d | %s | %s |' % (
                k, d['structures'], d['gross_positive'],
                ('%.2f¢' % (100 * d['median_gross_gap'])) if d.get('median_gross_gap') is not None else '—',
                d.get('confirmed_positive', 0), money(d.get('walk_profit')), money(d.get('walk_capital'))))
        L.append('')
    H = A.get('history')
    if H:
        L += ['## History (%d pairs, %d days, Polymarket half spread assumed %.1f¢)' % (H['pairs'], H['days'], 100 * H['pm_half_spread']), '',
              '| class | pairs | hours with both venues | hours net > 0 | share | upper bound (no half spread) | hours > 1¢ | episodes |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        for k, d in sorted(H['by_class'].items(), key=lambda x: -x[1]['hours']):
            L.append('| %s | %d | %d | %d | %s | %s | %d | %d |' % (
                k, d['pairs'], d['hours'], d['hours_positive'],
                ('%.2f%%' % (100 * d['share_positive'])) if d['share_positive'] is not None else '—',
                ('%.2f%%' % (100 * d['share_positive_ub'])) if d['share_positive_ub'] is not None else '—',
                d['hours_over_1c'], d['episodes']))
        L += ['', 'Episodes: %d; median %s h, p90 %s h, %d lasting a day or more.' % (
            H['episodes'], H['episode_hours_median'], H['episode_hours_p90'], H['episodes_over_24h']), '']
        if H.get('split'):
            sp = H['split']
            L.append('Stability (split at %s): first half %d hours, %d positive, %d over 1¢; second half %d hours, %d positive, %d over 1¢.' % (
                sp['midpoint'], sp['first_half']['hours'], sp['first_half']['positive'], sp['first_half']['over_1c'],
                sp['second_half']['hours'], sp['second_half']['positive'], sp['second_half']['over_1c']))
        L += ['', '| ticker | class | start | hours | peak net |', '|---|---|---|---:|---:|']
        for e in H['top_episodes']:
            L.append('| %s | %s | %s | %d | %.2f¢ |' % (e['ticker'], e['class'], e['start'][:16], e['hours'], 100 * e['peak']))
    HS = A.get('history_strategy')
    if HS:
        L += ['', '## A monitor on the history (one fill per episode at the latest touch size, clip %s)' % money(HS['clip_usd']), '',
              '| hurdle (APR net of SSR) | episodes | booked gain | first half | second half | peak capital | average capital | on peak | on average |',
              '|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for h, v in HS['by_hurdle'].items():
            if not v.get('episodes'):
                continue
            L.append('| %s | %d | %s | %s | %s | %s | %s | %.1f%% | %.1f%% |' % (
                '%d%%' % round(100 * float(h)), v['episodes'], money(v['gain_total']), money(v['gain_first_half']),
                money(v['gain_second_half']), money(v['peak_capital']), money(v['average_capital']),
                100 * (v['annualised_on_peak_capital'] or 0), 100 * (v['annualised_on_average_capital'] or 0)))
        sel = HS.get('selection')
        if sel:
            L += ['', 'Hurdle chosen on the first half of days: %s (of %d); annualised on peak capital %.1f%% in sample, %.1f%% '
                  'out of sample (rank %d of %d out of sample).' % (sel['chosen'], sel['n_variants'],
                                                                   100 * (sel['in_sample'].get('ann_return') or 0),
                                                                   100 * (sel['out_of_sample'].get('ann_return') or 0),
                                                                   sel['oos_rank'], sel['n_variants'])]
    PC = A.get('proxy_check')
    if PC:
        L += ['', 'Proxy check against the books read at %s: %d pairs, hourly proxy minus executable net gap median %+.2f¢, '
              'mean %+.2f¢, p10 %+.2f¢, p90 %+.2f¢; positive on the proxy %d, in the books %d, both %d.' % (
                  PC['books_generated'][:16], PC['pairs'], 100 * PC['median_proxy_minus_live'], 100 * PC['mean_proxy_minus_live'],
                  100 * PC['p10'], 100 * PC['p90'], PC['proxy_positive'], PC['live_positive'], PC['both_positive'])]
    VT = A.get('venue_tilt')
    if VT:
        L += ['', '## Venue tilt: Kalshi midpoint minus Polymarket price', '', '| market | ' +
              ' | '.join(sorted({m for v in VT['chamber_control_monthly_kalshi_minus_polymarket'].values() for m in v})) + ' |']
        months = sorted({m for v in VT['chamber_control_monthly_kalshi_minus_polymarket'].values() for m in v})
        L.append('|---|' + '---:|' * len(months))
        for tk, v in VT['chamber_control_monthly_kalshi_minus_polymarket'].items():
            L.append('| %s | %s |' % (tk, ' | '.join(('%+.2f¢' % (100 * v[m])) if m in v else '—' for m in months)))
        for k, v in VT['party_coded_races'].items():
            if v['races']:
                L.append('')
                L.append('%s-coded race markets: %d, mean %+.2f¢, Kalshi higher in %.0f%%.' % (
                    k, v['races'], 100 * v['mean_kalshi_minus_polymarket'], 100 * v['share_kalshi_higher']))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))
    return 0


# ------------------------------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('snapshot'); s.set_defaults(fn=cmd_snapshot)
    s.add_argument('--out', required=True)
    s.add_argument('--skip-kalshi', action='store_true')
    s.add_argument('--skip-polymarket', action='store_true')
    s.add_argument('--skip-limitless', action='store_true')
    c = sub.add_parser('candidates'); c.set_defaults(fn=cmd_candidates)
    c.add_argument('--out', required=True)
    m = sub.add_parser('match'); m.set_defaults(fn=cmd_match)
    m.add_argument('--out', required=True)
    h = sub.add_parser('history'); h.set_defaults(fn=cmd_history)
    h.add_argument('--out', required=True)
    h.add_argument('--days', type=float, default=90.0)
    h.add_argument('--top-elections', type=int, default=60)
    h.add_argument('--sports', type=int, default=0, help='also the N highest-volume sports pairs (their history is short)')
    h.add_argument('--pm-half-spread', type=float, default=0.005, help='assumed Polymarket half spread over its hourly price')
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    b = sub.add_parser('books'); b.set_defaults(fn=cmd_books)
    b.add_argument('--out', required=True)
    b.add_argument('--screen-gap', type=float, default=0.0, help='gross gap at the touch that triggers a confirmation read')
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
