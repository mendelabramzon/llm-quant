#!/usr/bin/env python3
"""The house edge on parlays: can an outside quoter sell Kalshi combos (and Polymarket Combos) for a rent?

Why. Sportsbooks charge 20-30% on parlays; the buyer is paying for entertainment, not a price. Kalshi's multivariate
event (MVE) "combos" and Polymarket's Combos replace the book with a request-for-quote auction: the buyer names the
legs, market makers quote, the best quote fills. If buyers still overpay, the quoting side is a rent open to anyone
with a fair-value model and capital, and it does not race on latency or block position (an RFQ is an auction on
price; Kalshi gives a combo maker 3 s to confirm, Polymarket a 400 ms quote deadline and a 1 s last look).

What is measured (Kalshi, public API, live tier = trades after the 2026-08-15 historical cutoff):
  * a stratified time sample of the global trade tape (fixed windows per UTC day, hashed start times), keeping every
    combo trade (tickers KXMVE*) and the window's totals for scale-up;
  * a hashed subsample of the combos traded in those windows: legs, settlement value, series (fee schedule);
  * every leg's book (1-minute candlestick yes bid/ask close, event-driven) at or before the combo trade;
  * Kalshi sports milestones: each game's start time and every event ticker that belongs to it, which classifies a
    combo as pre-game or in-play and its legs as same-game or cross-game exactly.

Arithmetic (unit-tested in test_pm_parlays.py):
  * leg probability: mid of the leg's YES bid/ask (1 - mid for a NO leg); fair (independent legs) = product of mids;
    the product of bids and of asks bound it;
  * implied margin = combo YES price / fair - 1;
  * the quoter is the maker: it sells YES when the requester buys YES (pays 1 - p per contract, receives 1 - v);
    P&L = p - v - maker fee, capital = 1 - p + fee; a requester selling YES (cash-out) is the mirror;
  * maker fee: 0.035 x C x p x (1 - p) (half the 0.07 taker rate) on series KXMVECROSSCATEGORY from 2026-08-20 09:02
    UTC, zero on KXMVECROSSCATEGORY0 (uncorrelated NFL parlays, series fee_type 'quadratic'); the taker pays
    0.07 x C x p x (1 - p) everywhere. Both are rounded up to the cent per trade (kalshi_fee).

    uv run python scripts/pm_parlays.py kalshi-milestones --out research/2026-10-14/pm_parlays
    uv run python scripts/pm_parlays.py kalshi-collect    --out research/2026-10-14/pm_parlays
    uv run python scripts/pm_parlays.py pm-collect        --out research/2026-10-14/pm_parlays
    uv run python scripts/pm_parlays.py analyze           --out research/2026-10-14/pm_parlays
    uv run python scripts/pm_parlays.py render            --out research/2026-10-14/pm_parlays
"""
import argparse
import bisect
import collections
import datetime as dt
import json
import math
import statistics
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
from pm_crossvenue import http_json, kalshi_fee  # noqa: E402
from polymarket_history import Http, write_gz, read_gz, update_manifest, parse_ts, stable_u, write_json  # noqa: E402

KALSHI = 'https://api.elections.kalshi.com/trade-api/v2/'
SSR = 0.038                      # Sky savings rate (repo convention): idle USDC's opportunity cost
DAY = 86400.0
TAKER_RATE = 0.07
COMBO_MAKER_RATE = 0.035         # "combos, excluding uncorrelated NFL parlays: maker fee 50% of the taker fee"
COMBO_MAKER_FEE_START = parse_ts('2026-08-20T09:02:00Z')   # series fee change on KXMVECROSSCATEGORY (API)
MAKER_FEE_SERIES = ('KXMVECROSSCATEGORY', 'KXMVESPORTSMULTIGAMEEXTENDED')   # fee_type quadratic_with_combo_maker_fees
LIVE_FROM = '2026-08-16'         # first whole UTC day after the historical cutoff (2026-08-15T00:00Z)

STATS = collections.Counter()


# ------------------------------------------------------------------------------------------------ pure arithmetic

def leg_prob(bid, ask, side, max_spread=0.10):
    """(mid, lo, hi) probability of a leg paying, from its YES bid/ask and the side selected. None when unpriced.

    A NO leg pays when YES fails: its bid is 1 - YES ask and its ask is 1 - YES bid. An empty side of the book shows
    in Kalshi candles as bid 0 or ask 0.999/1, so a book wider than `max_spread` is unpriced, not a price."""
    if bid is None or ask is None:
        return None
    if not (0.0 < bid < 1.0 and 0.0 < ask < 1.0) or ask < bid or ask - bid > max_spread:
        return None
    if side == 'yes':
        lo, hi = bid, ask
    elif side == 'no':
        lo, hi = 1.0 - ask, 1.0 - bid
    else:
        return None
    return (lo + hi) / 2.0, lo, hi


def combo_fair(probs):
    """Fair price of an all-legs-pay combo under independence: product of the leg mids, bounded by the products of
    the leg bids (lo) and asks (hi). `probs` is a list of (mid, lo, hi); None if any leg is unpriced."""
    if not probs or any(p is None for p in probs):
        return None
    mid = lo = hi = 1.0
    for m, a, b in probs:
        mid *= m
        lo *= a
        hi *= b
    return mid, lo, hi


def implied_margin(price, fair):
    """Combo price over its fair value, minus one: the buyer's overpayment as a share of fair."""
    if fair is None or fair <= 0:
        return None
    return price / fair - 1.0


def maker_fee_applies(combo_ticker, ts, schedule='actual'):
    """Whether the combo maker fee is charged on this trade. 'actual' follows the series' fee history; 'current'
    charges today's schedule to every trade (the repo's forward-looking convention)."""
    series = combo_ticker.split('-', 1)[0]
    if series not in MAKER_FEE_SERIES:
        return False
    if schedule == 'current':
        return True
    return ts >= COMBO_MAKER_FEE_START


def combo_maker_fee(contracts, price, applies):
    return kalshi_fee(contracts, price, rate=COMBO_MAKER_RATE) if applies else 0.0


def combo_taker_fee(contracts, price):
    return kalshi_fee(contracts, price, rate=TAKER_RATE)


def maker_pnl(price, contracts, taker_side, settle, fee):
    """The quoting side's P&L and capital for one combo trade at YES price `price`.

    taker_side 'yes' (a parlay buyer): the maker sold YES, i.e. paid 1 - p per contract for NO, which pays 1 - settle.
    taker_side 'no' (a holder selling / a NO buyer): the maker bought YES at p, which pays settle.
    Returns (pnl, capital) in dollars; capital includes the fee."""
    if taker_side == 'yes':
        pnl = (price - settle) * contracts - fee
        cap = (1.0 - price) * contracts + fee
    elif taker_side == 'no':
        pnl = (settle - price) * contracts - fee
        cap = price * contracts + fee
    else:
        raise ValueError(taker_side)
    return pnl, cap


def own_quote_fill(price, fair, m, tick=0.001):
    """The executable version of 'sell when price >= fair x (1 + m)': quote ask q = fair x (1 + m) rounded up to the
    tick. The RFQ is won only if q is below the incumbent's winning price (the trade print); the fill is at q, not at
    the print. Returns q when won, else None. Ties go to the incumbent (it was there first)."""
    if fair is None:
        return None
    q = math.ceil(round(fair * (1.0 + m) / tick, 9)) * tick
    if q >= 1.0 or q <= 0.0:
        return None
    return q if q < price - 1e-12 else None


def structure_of(keys):
    """'single' (one game key), 'cross' (every leg a different game), or 'mixed' (some legs share a game)."""
    keys = list(keys)
    if not keys:
        return None
    n, k = len(keys), len(set(keys))
    if k == 1:
        return 'same'
    if k == n:
        return 'cross'
    return 'mixed'


def legs_bucket(n):
    if n <= 4:
        return str(n)
    if n <= 6:
        return '5-6'
    if n <= 10:
        return '7-10'
    return '11+'


SPORT_PREFIXES = [
    ('NFL', ('KXNFL',)), ('NCAAF', ('KXNCAAF',)), ('NBA', ('KXNBA',)), ('WNBA', ('KXWNBA',)), ('NCAAB', ('KXNCAAB', 'KXNCAAMB', 'KXNCAAWB')),
    ('MLB', ('KXMLB',)), ('NHL', ('KXNHL',)),
    ('soccer', ('KXUCL', 'KXEPL', 'KXLALIGA', 'KXSERIEA', 'KXBUNDESLIGA', 'KXLIGUE1', 'KXMLS', 'KXLIGAMX', 'KXUEL',
                'KXUECL', 'KXLIGAPORTUGAL', 'KXBRASILEIRO', 'KXARGNAC', 'KXURY', 'KXEREDIVISIE', 'KXEFL', 'KXSOCCER',
                'KXFIFA', 'KXWC', 'KXCONCACAF', 'KXCOPA', 'KXSAUDI', 'KXSUPERLIG', 'KXSCOTPREM', 'KXJLEAGUE',
                'KXKLEAGUE', 'KXALEAGUE', 'KXCHAMPIONSHIP', 'KXFACUP', 'KXCOLOMBIA', 'KXCHILE', 'KXBELGIAN',
                'KXDENMARK', 'KXNORWAY', 'KXSWEDEN', 'KXINTLFRIENDLY', 'KXUNL', 'KXEURO', 'KXAFCON')),
    ('tennis', ('KXATP', 'KXWTA', 'KXTENNIS', 'KXUSOPEN', 'KXDAVIS')),
    ('golf', ('KXPGA', 'KXLIV', 'KXGOLF', 'KXRYDER')),
    ('mma_boxing', ('KXUFC', 'KXBOXING', 'KXMMA')),
    ('esports', ('KXCS2', 'KXLOL', 'KXVALORANT', 'KXDOTA', 'KXCSGO', 'KXESPORT')),
    ('crypto_15m', ('KXBTC15M', 'KXETH15M', 'KXSOL15M', 'KXXRP15M', 'KXDOGE15M', 'KXBNB15M', 'KXHYPE15M',
                    'KXNEAR15M', 'KXZEC15M')),
    ('commodity_15m', ('KXGOLD15M', 'KXSILVER15M', 'KXWTI15M', 'KXNATGAS15M', 'KXCOPPER15M')),
]


def sport_of(series):
    s = series.upper()
    if s.endswith('15M'):
        for name, pre in SPORT_PREFIXES[-2:]:
            if s.startswith(pre):
                return name
        return 'crypto_15m'
    for name, pre in SPORT_PREFIXES:
        if s.startswith(pre):
            return name
    return 'other'


def combo_sport(leg_series):
    sports = sorted({sport_of(s) for s in leg_series})
    return sports[0] if len(sports) == 1 else 'multi:' + '+'.join(sports)


def game_code(event_ticker):
    """The game part of a Kalshi sports event ticker: 'KXNFLTD-26OCT11CHIGB' -> '26OCT11CHIGB'. Team-scoped events
    ('KXNFLTEAMFIRSTTD-26OCT15SEADEN-DEN') drop the team suffix."""
    parts = (event_ticker or '').split('-')
    return parts[1] if len(parts) >= 2 else None


def milestone_index(milestones):
    """(by_event, by_code): event ticker -> (milestone id, start ts) and game code -> the same, the second built from
    every event a milestone lists. A code claimed by two milestones (a doubleheader) is dropped from by_code."""
    by_event, by_code, clash = {}, {}, set()
    for m in milestones:
        st = parse_ts(m.get('start'))
        if st is None:
            continue
        for e in m.get('events') or []:
            by_event[e] = (m['id'], st)
            code = game_code(e)
            if code:
                if code in by_code and by_code[code][0] != m['id']:
                    clash.add(code)
                by_code[code] = (m['id'], st)
    for c in clash:
        by_code.pop(c, None)
    return by_event, by_code


def game_of(event_ticker, by_event, by_code):
    """(milestone id, game start ts) for a leg's event, or None when the leg is not a scheduled game."""
    hit = by_event.get(event_ticker)
    if hit:
        return hit
    code = game_code(event_ticker)
    return by_code.get(code) if code else None


def leg_book_at(rows_1m, rows_1h, t):
    """The leg's YES (bid, ask, age_s) at time t: the close of the last 1-minute candle that ended at or before t,
    else the last hourly candle that did. Candles are event-driven (emitted when the book or a trade changes), so a
    missing minute means an unchanged book. Rows are [end_ts, bid, ask, ...] in time order."""
    for rows in (rows_1m, rows_1h):
        if not rows:
            continue
        i = bisect.bisect_right([r[0] for r in rows], t) - 1
        while i >= 0:
            r = rows[i]
            if r[1] is not None and r[2] is not None:
                return r[1], r[2], t - r[0]
            i -= 1
    return None


# ------------------------------------------------------------------------------------------------ http

def kget(path, params=None):
    url = KALSHI + path + ('?' + urllib.parse.urlencode(params) if params else '')
    STATS['kalshi_requests'] += 1
    d = http_json(url, 'kalshi')
    if d is None:
        STATS['kalshi_failures'] += 1
    return d


def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec='seconds')


def day_epoch(day):
    return dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp()


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


# ------------------------------------------------------------------------------------------------ Kalshi: milestones

def cmd_k_milestones(args):
    out = Path(args.out)
    rows, seen = [], set()
    t_start = time.time()
    for cat in ('Sports', 'Esports'):
        cur, pages = None, 0
        while True:
            params = {'limit': 200, 'category': cat, 'minimum_start_date': args.since}
            if cur:
                params['cursor'] = cur
            d = kget('milestones', params)
            if not d:
                break
            ms = d.get('milestones') or []
            for m in ms:
                if m['id'] in seen:
                    continue
                seen.add(m['id'])
                det = m.get('details') or {}
                rows.append({'id': m['id'], 'start': m.get('start_date'), 'end': m.get('end_date'),
                             'type': m.get('type'), 'title': m.get('title'), 'league': det.get('league'),
                             'category': cat,
                             'events': sorted(set((m.get('related_event_tickers') or [])
                                                  + (m.get('primary_event_tickers') or [])))})
            pages += 1
            cur = d.get('cursor')
            if not cur or not ms:
                break
        print('milestones %s: %d pages, %d total' % (cat, pages, len(rows)), flush=True)
    write_gz(out / 'raw' / 'kalshi' / 'milestones.json.gz', rows)
    update_manifest(out, 'kalshi_milestones', {'fetched_at': utc(time.time()), 'since': args.since,
                                               'milestones': len(rows), 'seconds': round(time.time() - t_start),
                                               'requests': STATS['kalshi_requests'],
                                               'failures': STATS['kalshi_failures']})
    return 0


# ------------------------------------------------------------------------------------------------ Kalshi: windows

def sample_windows(day_from, day_to, per_day, width, seed='pm_parlays-v1'):
    """Stratified, reproducible window starts: window k of a day lies in the k-th 1/per_day slice of that UTC day,
    at a hashed offset within the slice."""
    out = []
    d0 = dt.date.fromisoformat(day_from)
    d1 = dt.date.fromisoformat(day_to)
    slot = DAY / per_day
    d = d0
    while d <= d1:
        base = day_epoch(d.isoformat())
        for k in range(per_day):
            u = stable_u('%s|%s|%d' % (seed, d.isoformat(), k))
            t0 = int(base + k * slot + u * (slot - width))
            out.append((d.isoformat(), k, t0, t0 + width))
        d += dt.timedelta(days=1)
    return out


def fetch_tape(t0, t1):
    """Every trade in [t0, t1) from the global tape; keeps combo trades, counts the rest."""
    keep, n_all, c_all, n_combo, c_combo, pages, cur = [], 0, 0.0, 0, 0.0, 0, None
    while True:
        params = {'limit': 1000, 'min_ts': t0, 'max_ts': t1}
        if cur:
            params['cursor'] = cur
        d = kget('markets/trades', params)
        if d is None:
            return None
        ts = d.get('trades') or []
        pages += 1
        for x in ts:
            c = fnum(x.get('count_fp'), 0.0)
            n_all += 1
            c_all += c
            if x['ticker'].startswith('KXMVE'):
                n_combo += 1
                c_combo += c
                keep.append([x['trade_id'], x['ticker'], parse_ts(x['created_time']), c,
                             fnum(x.get('yes_price_dollars')), x.get('taker_outcome_side') or x.get('taker_side'),
                             bool(x.get('is_block_trade'))])
        cur = d.get('cursor')
        if not cur or not ts:
            break
    return {'pages': pages, 'n_all': n_all, 'contracts_all': c_all, 'n_combo': n_combo, 'contracts_combo': c_combo,
            'combo_trades': keep}


def compact_combo(m):
    return {'ticker': m['ticker'], 'collection': m.get('mve_collection_ticker'),
            'legs': [[l.get('market_ticker'), l.get('event_ticker'), l.get('side')] for l in (m.get('mve_selected_legs') or [])],
            'status': m.get('status'), 'result': m.get('result'),
            'settle': fnum(m.get('settlement_value_dollars')), 'settled_at': m.get('settlement_ts'),
            'created': m.get('created_time'), 'close': m.get('close_time'), 'volume': fnum(m.get('volume_fp')),
            'last': fnum(m.get('last_price_dollars'))}


def fetch_markets(tickers):
    out = {}
    for i in range(0, len(tickers), 100):
        chunk = tickers[i:i + 100]
        d = kget('markets', {'limit': 1000, 'tickers': ','.join(chunk)})
        for m in (d or {}).get('markets') or []:
            out[m['ticker']] = compact_combo(m)
    return out


def fetch_candles(tickers, start, end, period=1, per_call=100):
    """Batch candlesticks: {ticker: [[end_ts, bid, ask, last_price, volume], ...]} (bid/ask = yes close)."""
    out = {}
    span = max(1, int((end - start) / (60 * period)) + 2)
    per_call = max(1, min(per_call, 10000 // span))
    for i in range(0, len(tickers), per_call):
        chunk = tickers[i:i + per_call]
        d = kget('markets/candlesticks', {'market_tickers': ','.join(chunk), 'start_ts': int(start),
                                          'end_ts': int(end), 'period_interval': period})
        for m in (d or {}).get('markets') or []:
            rows = []
            for c in m.get('candlesticks') or []:
                yb = (c.get('yes_bid') or {}).get('close_dollars')
                ya = (c.get('yes_ask') or {}).get('close_dollars')
                pr = (c.get('price') or {}).get('close_dollars')
                rows.append([c['end_period_ts'], fnum(yb), fnum(ya), fnum(pr), fnum(c.get('volume_fp'), 0.0)])
            out[m.get('market_ticker')] = rows
    return out


def cmd_k_collect(args):
    out = Path(args.out)
    wdir = out / 'raw' / 'kalshi' / 'windows'
    wdir.mkdir(parents=True, exist_ok=True)
    wins = sample_windows(args.day_from, args.day_to, args.per_day, args.width)
    by_event, by_code = milestone_index(read_gz(out / 'raw' / 'kalshi' / 'milestones.json.gz'))
    combos_cache = {}
    for p in sorted(wdir.glob('*.json.gz')):
        try:
            for k, v in read_gz(p).get('combos', {}).items():
                combos_cache[k] = v
        except Exception:  # noqa: BLE001 - a torn file is re-fetched below
            p.unlink()
    t_start = time.time()
    done = 0
    for day, k, t0, t1 in wins:
        path = wdir / ('%d.json.gz' % t0)
        if path.exists():
            continue
        tape = fetch_tape(t0, t1)
        if tape is None:
            STATS['windows_failed'] += 1
            continue
        tickers = sorted({x[1] for x in tape['combo_trades']})
        kept = [t for t in tickers if stable_u('combo|' + t) < args.combo_frac]
        need = [t for t in kept if t not in combos_cache]
        combos = fetch_markets(need)
        combos_cache.update(combos)
        # leg books are fetched only for combos traded before every leg's game started (the non-latency population);
        # in-play and non-game combos keep their trades and settlement (the maker's realized P&L needs no leg price)
        first_by = {}
        for x in tape['combo_trades']:
            first_by[x[1]] = min(first_by.get(x[1], x[2]), x[2])
        pregame = []
        for t in kept:
            c = combos_cache.get(t)
            if not c or not c['legs']:
                continue
            g = [game_of(l[1], by_event, by_code) for l in c['legs']]
            if all(g) and first_by.get(t, t1) < min(x[1] for x in g):
                pregame.append(t)
        legs = sorted({l[0] for t in pregame for l in combos_cache[t]['legs'] if l[0]})
        first_trade = min([first_by[t] for t in pregame] or [t0])
        candles = fetch_candles(legs, t0 - args.lookback, t1, period=1)
        missing = [l for l in legs if not any(r[0] <= first_trade for r in candles.get(l, []))]
        hourly = fetch_candles(missing, t0 - 86400, t0, period=60) if missing else {}
        write_gz(path, {'day': day, 'slot': k, 't0': t0, 't1': t1,
                        'tape': {kk: v for kk, v in tape.items() if kk != 'combo_trades'},
                        'combo_trades': tape['combo_trades'], 'kept_tickers': kept, 'pregame_priced': pregame,
                        'combos': {t: combos_cache[t] for t in kept if t in combos_cache},
                        'candles_1m': candles, 'candles_1h': hourly})
        done += 1
        if done % 10 == 0:
            el = time.time() - t_start
            print('%s windows done=%d (%.0fs, %.1fs/window) requests=%d failures=%d' % (
                day, done, el, el / done, STATS['kalshi_requests'], STATS['kalshi_failures']), flush=True)
    update_manifest(out, 'kalshi_collect_%s_%s' % (args.day_from, args.day_to), {
        'finished_at': utc(time.time()), 'windows': len(wins), 'windows_fetched_this_run': done,
        'per_day': args.per_day, 'width_s': args.width, 'combo_frac': args.combo_frac, 'lookback_s': args.lookback,
        'requests': STATS['kalshi_requests'], 'failures': STATS['kalshi_failures'],
        'windows_failed': STATS['windows_failed'], 'seconds': round(time.time() - t_start)})
    return 0


# ------------------------------------------------------------------------------------------------ Polymarket Combos

PM_EXCHANGE_V3 = '0xe3333700ca9d93003f00f0f71f8515005f6c00aa'     # docs.polymarket.com/trading/combos/market-makers
TOPIC_ORDER_FILLED = '0xd543adfd945773f1a62f74f0ee55a5e3b9b1a28262980ba90b1a89f2ea84d8ee'
TOPIC_ORDERS_MATCHED = '0x174b3811690657c217184f89418266767c87e4805d09680c39fc9c031c0cab7c'
TOPIC_FEE_CHARGED = '0x55bb3cade9d43b798a4fe5ffdd05024b2d7870df53920673bfc7e68047cd0ab1'
PM_SPORTS_RATE = 0.05
DATA_API = 'https://data-api.polymarket.com'


def _word(data, i):
    return int(data[2 + 64 * i: 2 + 64 * (i + 1)], 16)


def _addr(topic):
    return '0x' + topic[-40:].lower()


def decode_matches(logs, exchange=PM_EXCHANGE_V3):
    """Group Exchange v3 logs into Combo matches.

    Layout read off the chain (2026-10-14): each match emits the makers' OrderFilled (topic2 maker, topic3 = the
    requester; data side, asset, makerAmountFilled, takerAmountFilled, fee, ...), a FeeCharged, the requester's
    aggregate OrderFilled (maker = requester, taker = the exchange, data word 4 = the requester's fee) and an
    OrdersMatched. Amounts have 6 decimals. Side 0 = BUY (pays pUSD, receives shares), 1 = SELL.
    A requester BUY of p per share pays `makerAmount` pUSD for `takerAmount` shares plus the fee on top."""
    ex = exchange.lower()
    out, pending = [], collections.defaultdict(list)
    for l in sorted(logs, key=lambda x: (int(x['blockNumber'], 16), int(x['logIndex'], 16))):
        t0 = l['topics'][0]
        tx = l['transactionHash']
        if t0 == TOPIC_ORDER_FILLED and len(l['topics']) >= 4:
            maker, taker = _addr(l['topics'][2]), _addr(l['topics'][3])
            d = l['data']
            row = {'maker': maker, 'taker': taker, 'side': _word(d, 0), 'asset': str(_word(d, 1)),
                   'maker_amt': _word(d, 2) / 1e6, 'taker_amt': _word(d, 3) / 1e6, 'fee': _word(d, 4) / 1e6}
            if taker == ex:
                fills = pending.pop((tx, maker), [])
                side = row['side']
                if side == 0:
                    usd, shares = row['maker_amt'], row['taker_amt']
                else:
                    usd, shares = row['taker_amt'], row['maker_amt']
                out.append({'block': int(l['blockNumber'], 16), 'tx': tx, 'log': int(l['logIndex'], 16),
                            'requester': maker, 'side': 'BUY' if side == 0 else 'SELL', 'asset': row['asset'],
                            'usd': usd, 'shares': shares, 'price': (usd / shares) if shares else None,
                            'fee': row['fee'], 'makers': fills})
            else:
                pending[(tx, taker)].append(row)
    return out


def pm_fee(shares, price, rate=PM_SPORTS_RATE):
    """Polymarket taker fee on a Combo fill: shares x rate x p x (1 - p) (the CLOB schedule; makers pay none)."""
    return shares * rate * price * (1.0 - price)


def _rpc_retry(rpc, method, params, tries=4):
    for a in range(tries):
        try:
            return rpc.call('polygon', method, params)
        except Exception:  # noqa: BLE001 - Infura's transient 'precondition failure' and timeouts are retried
            STATS['rpc_retries'] += 1
            if a == tries - 1:
                raise
            time.sleep(2.0 * (a + 1))


def block_at(rpc, t, known):
    """First block at or after unix time t, by secant steps between known (block, ts) pairs; `known` is updated."""
    def ts_of(b):
        # some blocks fail on Infura with a persistent 'precondition failure'; a neighbour is as good for a search
        for nb in (b, b + 1, b - 1, b + 3, b - 3, b + 7):
            if nb in known:
                return nb, known[nb]
            try:
                known[nb] = int(_rpc_retry(rpc, 'eth_getBlockByNumber', [hex(nb), False], tries=2)['timestamp'], 16)
                return nb, known[nb]
            except Exception:  # noqa: BLE001
                STATS['rpc_block_skips'] += 1
        raise RuntimeError('no readable block near %d' % b)
    pts = sorted(known.items())
    lo = max([p for p in pts if p[1] <= t], default=pts[0], key=lambda p: p[1])
    hi = min([p for p in pts if p[1] >= t], default=pts[-1], key=lambda p: p[1])
    for _ in range(12):
        if hi[0] - lo[0] <= 1 or hi[1] == lo[1]:
            break
        guess = lo[0] + int((t - lo[1]) * (hi[0] - lo[0]) / float(hi[1] - lo[1]))
        guess = min(hi[0] - 1, max(lo[0] + 1, guess))
        g = ts_of(guess)
        if abs(g[1] - t) <= 2:
            return g
        if g[1] < t:
            lo = g
        else:
            hi = g
    return hi


def cmd_pm_collect(args):
    out = Path(args.out)
    from onchain_probe import RPC   # imported here: it reads its own key file, which this script never touches
    rpc = RPC(out / 'raw' / 'polygon', max_credits=args.max_credits)
    wdir = out / 'raw' / 'polygon' / 'windows'
    wdir.mkdir(parents=True, exist_ok=True)
    head = int(_rpc_retry(rpc, 'eth_blockNumber', []), 16)
    head_ts = int(_rpc_retry(rpc, 'eth_getBlockByNumber', [hex(head), False])['timestamp'], 16)
    known = {head: head_ts}
    early = head - 6_000_000
    known[early] = int(_rpc_retry(rpc, 'eth_getBlockByNumber', [hex(early), False])['timestamp'], 16)
    t_start = time.time()
    wins = sample_windows(args.day_from, args.day_to, args.per_day, 1, seed='pm_parlays-polygon-v1')
    n_logs = 0
    for day, k, t0, _ in wins:
        path = wdir / ('%d.json.gz' % t0)
        if path.exists() or t0 > head_ts - 600:
            continue
        b, bt = block_at(rpc, t0, known)
        logs, step, lo = [], args.blocks, b
        while lo < b + args.blocks:
            hi = min(b + args.blocks, lo + step) - 1
            try:
                got = _rpc_retry(rpc, 'eth_getLogs', [{'address': PM_EXCHANGE_V3, 'fromBlock': hex(lo), 'toBlock': hex(hi)}], tries=2)
            except Exception:  # noqa: BLE001 - a result-count cap halves the range
                if step > 25:
                    step //= 2
                    continue
                raise
            logs.extend(got)
            lo = hi + 1
        try:
            et = int(_rpc_retry(rpc, 'eth_getBlockByNumber', [hex(b + args.blocks - 1), False], tries=2)['timestamp'], 16)
        except Exception:  # noqa: BLE001 - the window's end time is then estimated from its start at 1.5 s/block
            et = bt + int(1.5 * (args.blocks - 1))
            STATS['rpc_end_estimated'] += 1
        n_logs += len(logs)
        write_gz(path, {'day': day, 'slot': k, 'from_block': b, 'to_block': b + args.blocks - 1, 'from_ts': bt,
                        'to_ts': et, 'n_logs': len(logs), 'matches': decode_matches(logs)})
    update_manifest(out, 'polymarket_onchain', {'finished_at': utc(time.time()), 'windows': len(wins),
                                                'blocks_per_window': args.blocks, 'logs_this_run': n_logs,
                                                'rpc_credits_estimated': rpc.credits, 'head_block': head,
                                                'rpc_retries': STATS['rpc_retries'], 'rpc_block_skips': STATS['rpc_block_skips'],
                                                'window_end_estimated': STATS['rpc_end_estimated'],
                                                'windows_on_disk': len(list(wdir.glob('*.json.gz'))),
                                                'seconds': round(time.time() - t_start)})
    return 0


def cmd_pm_makers(args):
    """Every resolved Combo position of the largest makers seen on chain: the incumbents' realized rent."""
    out = Path(args.out)
    vol = collections.Counter()
    req_vol = collections.Counter()
    for p in sorted((out / 'raw' / 'polygon' / 'windows').glob('*.json.gz')):
        for m in read_gz(p)['matches']:
            req_vol[m['requester']] += m['usd']
            for f in m['makers']:
                vol[f['maker']] += f['maker_amt'] if f['side'] == 0 else f['taker_amt']
    makers = [a for a, _ in vol.most_common(args.top)][args.start_rank - 1:]
    http = Http(interval=0.5)
    pdir = out / 'raw' / 'polymarket' / 'positions'
    pdir.mkdir(parents=True, exist_ok=True)
    for a in makers:
        path = pdir / ('%s.json.gz' % a)
        if path.exists():
            continue
        rows, cur = [], None
        for _ in range(args.max_pages):
            q = {'user': a, 'limit': 500, 'status': 'RESOLVED_WIN,RESOLVED_PARTIAL,RESOLVED_LOSS'}
            if cur:
                q['cursor'] = cur
            d = http.request(DATA_API + '/v2/positions/combos?' + urllib.parse.urlencode(q))
            if not isinstance(d, dict) or '__error__' in d:
                break
            for r in d.get('data') or []:
                legs = [{'market_id': (l.get('market') or {}).get('market_id'),
                         'slug': (l.get('market') or {}).get('slug'),
                         'type': (l.get('market') or {}).get('sports_market_type'),
                         'event_id': ((l.get('market') or {}).get('event') or {}).get('event_id'),
                         'outcome_index': l.get('leg_outcome_index'), 'status': l.get('leg_status'),
                         'condition_id': l.get('leg_condition_id'), 'position_id': l.get('leg_position_id'),
                         'resolved_at': l.get('leg_resolved_at')} for l in r.get('legs') or []]
                rows.append({k: r.get(k) for k in ('combo_condition_id', 'outcome_index', 'entry_avg_price_usdc',
                                                   'gross_entry_cost_usdc', 'entry_fees_usdc', 'realized_payout_usdc',
                                                   'status', 'first_entry_at', 'resolved_at', 'legs_total')}
                            | {'legs': legs})
            pg = d.get('pagination') or {}
            cur = pg.get('next_cursor')
            if not pg.get('has_more') or not cur:
                break
        write_gz(path, {'maker': a, 'onchain_maker_usd_in_sample': vol[a], 'positions': rows})
        print('maker %s: %d resolved positions' % (a, len(rows)), flush=True)
    update_manifest(out, 'polymarket_makers', {'finished_at': utc(time.time()), 'makers': makers,
                                               'maker_usd_in_sample': {a: vol[a] for a in makers},
                                               'requesters_in_sample': len(req_vol), 'http': http.stats()})
    return 0


# ------------------------------------------------------------------------------------------------ analysis: Polymarket

def pm_section(out):
    """Polymarket Combos: flow and fees from sampled onchain windows; the incumbents' realized rent from their own
    resolved positions (data-api)."""
    wdir = out / 'raw' / 'polygon' / 'windows'
    wins = [read_gz(p) for p in sorted(wdir.glob('*.json.gz'))] if wdir.exists() else []
    S = {}
    if wins:
        ms = [m for w in wins for m in w['matches']]
        secs = sum(w['to_ts'] - w['from_ts'] for w in wins)
        ndays = len({w['day'] for w in wins})
        scale = DAY / (secs / ndays)
        buys = [m for m in ms if m['side'] == 'BUY']
        fee_err = [abs(m['fee'] - pm_fee(m['shares'], m['price'])) for m in ms if m['price']]
        implied_rate = [m['fee'] / (m['shares'] * m['price'] * (1 - m['price'])) for m in ms
                        if m['price'] and 0 < m['price'] < 1 and m['shares']]
        maker_usd = collections.Counter()
        for m in ms:
            for f in m['makers']:
                maker_usd[f['maker']] += f['maker_amt'] if f['side'] == 0 else f['taker_amt']
        tot = sum(maker_usd.values())
        by_day = collections.defaultdict(lambda: [0.0, 0.0, 0])
        for w in wins:
            for m in w['matches']:
                by_day[w['day']][0] += m['usd']
                by_day[w['day']][1] += m['fee']
                by_day[w['day']][2] += 1
        sec_by_day = collections.Counter()
        for w in wins:
            sec_by_day[w['day']] += w['to_ts'] - w['from_ts']
        S['onchain'] = {
            'windows': len(wins), 'days': ndays, 'seconds_sampled': secs, 'matches': len(ms),
            'requester_buy_share': len(buys) / max(1, len(ms)),
            'requester_usd_per_day': sum(m['usd'] for m in ms) * scale / ndays,
            'requester_buy_usd_per_day': sum(m['usd'] for m in buys) * scale / ndays,
            'fees_usd_per_day': sum(m['fee'] for m in ms) * scale / ndays,
            'matches_per_day': len(ms) * scale / ndays,
            'fee_formula_max_abs_error_usd': max(fee_err) if fee_err else None,
            'fee_formula_checked_matches': len(fee_err),
            'fee_rate_0p05_share': sum(1 for r in implied_rate if abs(r - 0.05) <= 0.002) / max(1, len(implied_rate)),
            'fee_rate_other_quantiles': [sorted(r for r in implied_rate if abs(r - 0.05) > 0.002)[int(q * (sum(1 for r in implied_rate if abs(r - 0.05) > 0.002) - 1))]
                                         for q in (0.0, 0.25, 0.5, 0.75, 1.0)] if any(abs(r - 0.05) > 0.002 for r in implied_rate) else [],
            'buy_price_median': statistics.median([m['price'] for m in buys]) if buys else None,
            'buy_usd_weighted_price': (sum(m['usd'] for m in buys) / sum(m['shares'] for m in buys)) if buys else None,
            'makers_distinct': len(maker_usd), 'requesters_distinct': len({m['requester'] for m in ms}),
            'maker_top5_share': sum(v for _, v in maker_usd.most_common(5)) / tot if tot else None,
            'maker_top10': [[a, v / tot] for a, v in maker_usd.most_common(10)] if tot else [],
            'makers_per_match_mean': statistics.mean([len(m['makers']) for m in ms]) if ms else None,
            'by_day': {d: {'requester_usd_per_day': v[0] * DAY / sec_by_day[d], 'fees_usd_per_day': v[1] * DAY / sec_by_day[d],
                           'matches_per_day': v[2] * DAY / sec_by_day[d]} for d, v in sorted(by_day.items())}}
    pdir = out / 'raw' / 'polymarket' / 'positions'
    if pdir.exists():
        per, allpos = {}, []
        for p in sorted(pdir.glob('*.json.gz')):
            d = read_gz(p)
            pos = [r for r in d['positions'] if r.get('gross_entry_cost_usdc') is not None and r.get('realized_payout_usdc') is not None]
            cost = sum(r['gross_entry_cost_usdc'] for r in pos)
            pay = sum(r['realized_payout_usdc'] for r in pos)
            per[d['maker']] = {'positions': len(pos), 'cost_usd': cost, 'payout_usd': pay, 'pnl_usd': pay - cost,
                               'return_on_cost': (pay - cost) / cost if cost else None,
                               'no_side_share': sum(1 for r in pos if r.get('outcome_index') == 1) / max(1, len(pos)),
                               'first': min((r['first_entry_at'] for r in pos if r.get('first_entry_at')), default=None),
                               'last': max((r['resolved_at'] for r in pos if r.get('resolved_at')), default=None)}
            for r in pos:
                allpos.append(dict(r, maker=d['maker']))
        S['makers'] = per
        if S.get('onchain') and wins:
            mu = collections.Counter()
            for w in wins:
                for m in w['matches']:
                    for f in m['makers']:
                        mu[f['maker']] += f['maker_amt'] if f['side'] == 0 else f['taker_amt']
            S['onchain']['maker_usd_share_with_positions_fetched'] = sum(v for a, v in mu.items() if a in per) / max(1e-9, sum(mu.values()))
        if allpos:
            def agg(v):
                c = sum(r['gross_entry_cost_usdc'] for r in v)
                p = sum(r['realized_payout_usdc'] for r in v)
                return {'positions': len(v), 'cost_usd': c, 'pnl_usd': p - c, 'return_on_cost': (p - c) / c if c else None}
            def same_event(r):
                ev = [l.get('event_id') for l in r.get('legs') or []]
                return structure_of(ev) if all(ev) else 'unknown'
            def mtypes(r):
                t = {l.get('type') or 'other' for l in r.get('legs') or []}
                return 'moneyline_only' if t == {'moneyline'} else ('has_props' if t - {'moneyline', 'spreads', 'totals'} else 'lines')
            no_pos = [r for r in allpos if r.get('outcome_index') == 1 and (r.get('entry_avg_price_usdc') or 0) > 0]
            yes_prem = sum(r['gross_entry_cost_usdc'] / r['entry_avg_price_usdc'] * (1.0 - r['entry_avg_price_usdc']) for r in no_pos)
            no_pnl = sum(r['realized_payout_usdc'] - r['gross_entry_cost_usdc'] for r in no_pos)
            rocs = sorted(v['return_on_cost'] for v in per.values() if v['return_on_cost'] is not None)
            S['maker_positions'] = {
                'no_side_pnl_over_yes_premium_sold': no_pnl / yes_prem if yes_prem else None,
                'yes_premium_sold_usd': yes_prem,
                'maker_return_on_cost_range': [rocs[0], rocs[-1]] if rocs else None,
                'makers_above_2pct': sum(1 for r in rocs if r > 0.02), 'makers_at_or_below_0p5pct': sum(1 for r in rocs if r <= 0.005),
                'pooled': agg(allpos),
                'by_side': {('NO' if k == 1 else 'YES'): agg(v) for k, v in group_by(allpos, lambda r: r.get('outcome_index')).items()},
                'by_legs': {legs_bucket(k or 0): agg(v) for k, v in sorted(group_by(allpos, lambda r: r.get('legs_total') or 0).items())},
                'by_structure': {k: agg(v) for k, v in group_by(allpos, same_event).items()},
                'by_market_types': {k: agg(v) for k, v in group_by(allpos, mtypes).items()},
                'by_month': {k: agg(v) for k, v in sorted(group_by(allpos, lambda r: (r.get('resolved_at') or '')[:7]).items())}}
            # daily series of the pooled makers' return on cost (by resolution day) and its HAC t
            dd = group_by(allpos, lambda r: (r.get('resolved_at') or '')[:10])
            ds = sorted(k for k in dd if k)
            ser = [(sum(r['realized_payout_usdc'] for r in dd[d]) - sum(r['gross_entry_cost_usdc'] for r in dd[d]))
                   / max(1e-9, sum(r['gross_entry_cost_usdc'] for r in dd[d])) for d in ds]
            t, p = B.newey_west_t(ser)
            S['maker_positions']['daily'] = {'days': len(ds), 'first': ds[0] if ds else None, 'last': ds[-1] if ds else None,
                                             'mean_daily_return_on_cost': statistics.mean(ser) if ser else None,
                                             'hac_t': t, 'p': p,
                                             'cost_usd_per_day': sum(r['gross_entry_cost_usdc'] for r in allpos) / max(1, len(ds)),
                                             'pnl_usd_per_day': sum(r['realized_payout_usdc'] - r['gross_entry_cost_usdc'] for r in allpos) / max(1, len(ds))}
    return S


# ------------------------------------------------------------------------------------------------ analysis: Kalshi

MARGINS = [0.0, 0.05, 0.10, 0.20, 0.40]       # the quoting rule's hurdle over leg-implied fair (pre-registered)
SPLIT_FRAC = 0.5                               # choose on the first half of days, test once on the second
MAX_LEG_AGE = 3 * 3600                         # a leg book older than this at the trade is stale -> unpriced
SETTLED = ('settled', 'finalized')


def kalshi_rows(out, max_spread=0.10):
    """One row per sampled combo trade: classification, price, fair value, settlement, the maker's P&L and capital."""
    ms = read_gz(out / 'raw' / 'kalshi' / 'milestones.json.gz')
    by_event, by_code = milestone_index(ms)
    rows, wins = [], []
    for p in sorted((out / 'raw' / 'kalshi' / 'windows').glob('*.json.gz')):
        w = read_gz(p)
        kept = set(w['kept_tickers'])
        c1 = {k: sorted(v, key=lambda r: r[0]) for k, v in (w.get('candles_1m') or {}).items()}
        c1h = {k: sorted(v, key=lambda r: r[0]) for k, v in (w.get('candles_1h') or {}).items()}
        prem_all = sum(x[3] * (x[4] or 0.0) for x in w['combo_trades'])
        kept_contracts = sum(x[3] for x in w['combo_trades'] if x[1] in kept)
        wins.append({'day': w['day'], 't0': w['t0'], 'width': w['t1'] - w['t0'], 'n_all': w['tape']['n_all'],
                     'contracts_all': w['tape']['contracts_all'], 'n_combo': w['tape']['n_combo'],
                     'contracts_combo': w['tape']['contracts_combo'], 'premium_combo': prem_all,
                     'kept_contracts': kept_contracts, 'n_kept_combos': len(kept)})
        for x in w['combo_trades']:
            tid, tk, ts, cnt, price, tside, block = x
            if tk not in kept or price is None:
                continue
            c = w['combos'].get(tk)
            if not c or not c['legs']:
                continue
            legs = c['legs']
            series = [l[1].split('-')[0] for l in legs]
            games = [game_of(l[1], by_event, by_code) for l in legs]
            if all(games):
                start = min(g[1] for g in games)
                cls = 'pregame' if ts < start else 'inplay'
                struct = structure_of([g[0] for g in games])
                lead_h = (start - ts) / 3600.0
            else:
                cls, start, lead_h = 'nongame', None, None
                struct = structure_of([game_code(l[1]) or l[1] for l in legs])
            fair = None
            ages = []
            if cls == 'pregame' and tk in set(w.get('pregame_priced') or []):
                probs = []
                for l in legs:
                    bk = leg_book_at(c1.get(l[0]), c1h.get(l[0]), ts)
                    if bk is None or bk[2] > MAX_LEG_AGE:
                        probs.append(None)
                        continue
                    ages.append(bk[2])
                    probs.append(leg_prob(bk[0], bk[1], l[2], max_spread=max_spread))
                fair = combo_fair(probs)
            settled = c['status'] in SETTLED and c['settle'] is not None
            settle = c['settle'] if settled else None
            fee_cur = combo_maker_fee(cnt, price, maker_fee_applies(tk, ts, 'current'))
            fee_act = combo_maker_fee(cnt, price, maker_fee_applies(tk, ts, 'actual'))
            pnl = cap = pnl_act = None
            if settled and tside in ('yes', 'no'):
                pnl, cap = maker_pnl(price, cnt, tside, settle, fee_cur)
                pnl_act, _ = maker_pnl(price, cnt, tside, settle, fee_act)
            st = parse_ts(c.get('settled_at')) if c.get('settled_at') else None
            rows.append({
                'tid': tid, 'ticker': tk, 'ts': ts, 'day': utc(ts)[:10], 'window': w['t0'], 'contracts': cnt,
                'price': price, 'taker_side': tside, 'block': block, 'n_legs': len(legs), 'cls': cls,
                'struct': struct, 'sport': combo_sport(series), 'lead_h': lead_h,
                'fee_series': tk.split('-', 1)[0], 'game_key': '|'.join(sorted({g[0] for g in games if g})) if all(games) else None,
                'fair': fair[0] if fair else None, 'fair_lo': fair[1] if fair else None,
                'fair_hi': fair[2] if fair else None, 'leg_age_max': max(ages) if ages and fair else None,
                'settled': settled, 'settle': settle, 'hold_d': ((st - ts) / DAY) if (st and settled) else None,
                'maker_fee': fee_cur, 'maker_fee_actual': fee_act, 'taker_fee': combo_taker_fee(cnt, price),
                'pnl': pnl, 'pnl_actual_fees': pnl_act, 'cap': cap})
    return rows, wins


def wmean(xs, ws):
    s = sum(ws)
    return sum(x * w for x, w in zip(xs, ws)) / s if s else None


def margin_stats(rows):
    """Implied margin of YES-buyer trades with a priced fair: contract- and premium-weighted, median, and how often the
    print is above the product of leg asks / below the product of leg bids."""
    r = [x for x in rows if x['fair'] and x['taker_side'] == 'yes']
    if not r:
        return {'n': 0}
    m = [implied_margin(x['price'], x['fair']) for x in r]
    prem = [x['price'] * x['contracts'] for x in r]
    fairv = [x['fair'] * x['contracts'] for x in r]
    return {'n': len(r), 'contracts': sum(x['contracts'] for x in r), 'premium_usd': sum(prem),
            'margin_median': statistics.median(m),
            'margin_premium_weighted': sum(prem) / sum(fairv) - 1.0 if sum(fairv) else None,
            'share_above_ask_product': sum(1 for x in r if x['price'] > x['fair_hi']) / len(r),
            'share_below_bid_product': sum(1 for x in r if x['price'] < x['fair_lo']) / len(r),
            'mean_price': wmean([x['price'] for x in r], [x['contracts'] for x in r]),
            'mean_fair': wmean([x['fair'] for x in r], [x['contracts'] for x in r])}


def pnl_stats(rows):
    """The maker side's realized P&L on settled trades: per $ risked, per $ of buyer premium, fees, hit rate."""
    r = [x for x in rows if x['pnl'] is not None]
    if not r:
        return {'n': 0}
    pnl = sum(x['pnl'] for x in r)
    cap = sum(x['cap'] for x in r)
    yes = [x for x in r if x['taker_side'] == 'yes']
    prem = sum(x['price'] * x['contracts'] for x in yes)
    paid = sum((x['settle'] or 0.0) * x['contracts'] for x in yes)
    out = {'n': len(r), 'contracts': sum(x['contracts'] for x in r), 'pnl_usd': pnl, 'capital_usd': cap,
           'pnl_per_risked': pnl / cap if cap else None,
           'pnl_actual_fees_usd': sum(x['pnl_actual_fees'] for x in r),
           'maker_fees_usd': sum(x['maker_fee'] for x in r), 'taker_fees_usd': sum(x['taker_fee'] for x in r),
           'yes_buyer_premium_usd': prem,
           'buyer_loss_per_premium_before_fees': (prem - paid) / prem if prem else None,
           'hold_days_median': statistics.median([x['hold_d'] for x in r if x['hold_d'] is not None] or [0.0]),
           'n_unsettled_excluded': None}
    fr = [x for x in yes if x['fair']]
    if fr:
        c = sum(x['contracts'] for x in fr)
        out['priced_yes'] = {'n': len(fr), 'hit_rate': sum((x['settle'] or 0.0) * x['contracts'] for x in fr) / c,
                             'mean_fair': sum(x['fair'] * x['contracts'] for x in fr) / c,
                             'mean_price': sum(x['price'] * x['contracts'] for x in fr) / c}
    return out


def group_by(rows, key):
    g = collections.defaultdict(list)
    for x in rows:
        g[key(x)].append(x)
    return dict(g)


def daily_series(rows, days, select, price_fn=None):
    """Per-day return per $ risked of the maker trades `select` keeps; days without a trade return 0.

    `price_fn(row)` replaces the print with the quoter's own fill price (None = not won). The fee is recharged at the
    fill price. Returns (series, per-day pnl, per-day capital)."""
    pnl_d, cap_d = collections.Counter(), collections.Counter()
    for x in rows:
        if x['pnl'] is None or not select(x):
            continue
        p = x['price']
        if price_fn is not None:
            p = price_fn(x)
            if p is None:
                continue
        fee = combo_maker_fee(x['contracts'], p, maker_fee_applies(x['ticker'], x['ts'], 'current'))
        pnl, cap = maker_pnl(p, x['contracts'], x['taker_side'], x['settle'], fee)
        pnl_d[x['day']] += pnl
        cap_d[x['day']] += cap
    ser = [(pnl_d[d] / cap_d[d]) if cap_d[d] else 0.0 for d in days]
    return ser, pnl_d, cap_d


def payout_z(fills):
    """Realized maker P&L over its payout standard deviation, and how many payouts the sample should contain.

    `fills` are (ticker, signed_contracts, pnl, prob): signed_contracts < 0 when the maker is short YES. Trades on the
    same combo are one bet, so exposure is netted per ticker; var = sum_t prob_t (1 - prob_t) x exposure_t^2.
    A daily-return t-statistic says nothing about a book of 1-in-500 shots that has not yet paid one out; this does:
    with expected_payouts well below one the sample cannot distinguish an edge from a lottery short.
    (Legs shared across combos make outcomes positively correlated, so this variance is a lower bound.)"""
    expo, prob, pnl = collections.Counter(), {}, 0.0
    for tk, sc, p, pr in fills:
        expo[tk] += sc
        prob[tk] = pr
        pnl += p
    var = sum(prob[t] * (1.0 - prob[t]) * expo[t] ** 2 for t in expo)
    return {'pnl_usd': pnl, 'payout_sd_usd': math.sqrt(var), 'z': (pnl / math.sqrt(var)) if var > 0 else None,
            'expected_payouts': sum(prob.values()), 'combos': len(expo)}


def cluster_t(rows, key, value, weight):
    """t-statistic of a weighted mean with clustered standard errors (clusters = key(row))."""
    g = group_by(rows, key)
    W = sum(weight(x) for x in rows)
    if W <= 0 or len(g) < 3:
        return None, len(g)
    mu = sum(value(x) * weight(x) for x in rows) / W
    s = 0.0
    for v in g.values():
        e = sum(weight(x) * (value(x) - mu) for x in v)
        s += e * e
    se = math.sqrt(s) / W * math.sqrt(len(g) / (len(g) - 1.0))
    return (mu / se if se > 0 else None), len(g)


def cmd_analyze(args):
    out = Path(args.out)
    A = {'generated_at': utc(time.time()), 'ssr': SSR}
    rows, wins = kalshi_rows(out)
    days = sorted({w['day'] for w in wins})
    A['kalshi_sample'] = {
        'windows': len(wins), 'days': len(days), 'first_day': days[0], 'last_day': days[-1],
        'seconds_sampled': sum(w['width'] for w in wins),
        'tape_trades': sum(w['n_all'] for w in wins), 'tape_combo_trades': sum(w['n_combo'] for w in wins),
        'tape_contracts': sum(w['contracts_all'] for w in wins),
        'tape_combo_contracts': sum(w['contracts_combo'] for w in wins),
        'combo_share_of_contracts': sum(w['contracts_combo'] for w in wins) / max(1.0, sum(w['contracts_all'] for w in wins)),
        'combo_share_of_trades': sum(w['n_combo'] for w in wins) / max(1, sum(w['n_all'] for w in wins)),
        'kept_trades': len(rows), 'kept_contracts': sum(x['contracts'] for x in rows),
        'kept_share_of_combo_contracts': sum(w['kept_contracts'] for w in wins) / max(1.0, sum(w['contracts_combo'] for w in wins)),
        'settled_trades': sum(1 for x in rows if x['settled']),
        'unsettled_trades': sum(1 for x in rows if not x['settled'])}
    # scale-up: sampled seconds -> a day; kept combos -> all combos by contracts
    sec_per_day = sum(w['width'] for w in wins) / len(days)
    kept_frac = A['kalshi_sample']['kept_share_of_combo_contracts']
    scale = (DAY / sec_per_day) / kept_frac
    A['kalshi_scale'] = {'seconds_per_day_sampled': sec_per_day, 'kept_fraction': kept_frac,
                         'row_to_daily_flow': scale,
                         'combo_contracts_per_day': sum(w['contracts_combo'] for w in wins) / len(days) * DAY / sec_per_day,
                         'combo_premium_usd_per_day': sum(w['premium_combo'] for w in wins) / len(days) * DAY / sec_per_day,
                         'all_contracts_per_day': sum(w['contracts_all'] for w in wins) / len(days) * DAY / sec_per_day}
    # composition (kept rows, scaled to daily $ premium)
    comp = {}
    for name, key in (('cls', lambda x: x['cls']), ('taker_side', lambda x: x['taker_side']),
                      ('sport', lambda x: x['sport'] if not x['sport'].startswith('multi') else 'multi-sport'),
                      ('legs', lambda x: legs_bucket(x['n_legs'])), ('struct', lambda x: x['struct']),
                      ('fee_series', lambda x: x['fee_series'])):
        g = group_by(rows, key)
        comp[name] = {k: {'trades': len(v), 'contracts': sum(x['contracts'] for x in v),
                          'premium_usd_per_day': sum(x['contracts'] * x['price'] for x in v) * scale / len(days)}
                      for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))}
    A['kalshi_composition'] = comp
    pre = [x for x in rows if x['cls'] == 'pregame']
    pre_priced = [x for x in pre if x['fair']]
    A['kalshi_pricing_coverage'] = {'pregame_trades': len(pre), 'pregame_priced': len(pre_priced),
                                    'priced_share': len(pre_priced) / max(1, len(pre)),
                                    'leg_age_median_s': statistics.median([x['leg_age_max'] for x in pre_priced] or [0])}
    # margins
    M = {'all_pregame_priced': margin_stats(pre_priced)}
    for name, key in (('struct', lambda x: x['struct']), ('legs', lambda x: legs_bucket(x['n_legs'])),
                      ('sport', lambda x: x['sport'] if not x['sport'].startswith('multi') else 'multi-sport'),
                      ('fee_series', lambda x: x['fee_series']),
                      ('week', lambda x: dt.date.fromisoformat(x['day']).isocalendar()[1]),
                      ('price_band', lambda x: '%.2f-%.2f' % (min(0.8, math.floor(x['price'] / 0.1) * 0.1),
                                                              min(0.9, math.floor(x['price'] / 0.1) * 0.1 + 0.1)))):
        M[name] = {str(k): margin_stats(v) for k, v in sorted(group_by(pre_priced, key).items(), key=lambda kv: str(kv[0]))}
    cross = [x for x in pre_priced if x['struct'] == 'cross']
    M['cross_by_legs'] = {k: margin_stats(v) for k, v in sorted(group_by(cross, lambda x: legs_bucket(x['n_legs'])).items())}
    M['cross_by_sport'] = {k: margin_stats(v) for k, v in sorted(group_by(
        cross, lambda x: x['sport'] if not x['sport'].startswith('multi') else 'multi-sport').items())}
    M['cross_by_fee_series'] = {k: margin_stats(v) for k, v in sorted(group_by(cross, lambda x: x['fee_series']).items())}
    M['cross_by_week'] = {str(k): margin_stats(v) for k, v in sorted(group_by(cross, lambda x: dt.date.fromisoformat(x['day']).isocalendar()[1]).items())}
    A['kalshi_margin'] = M
    # realized maker P&L by class (all kept trades, settled)
    P = {'all': pnl_stats(rows)}
    for name, key in (('cls', lambda x: x['cls']), ('cls_struct', lambda x: '%s/%s' % (x['cls'], x['struct'])),
                      ('sport', lambda x: x['sport'] if not x['sport'].startswith('multi') else 'multi-sport'),
                      ('legs', lambda x: legs_bucket(x['n_legs'])), ('fee_series', lambda x: x['fee_series']),
                      ('taker_side', lambda x: x['taker_side'])):
        P[name] = {str(k): pnl_stats(v) for k, v in sorted(group_by(rows, key).items(), key=lambda kv: str(kv[0]))}
    for name, sel in (('pregame_yes', lambda x: x['cls'] == 'pregame' and x['taker_side'] == 'yes'),
                      ('pregame_cross_yes', lambda x: x['cls'] == 'pregame' and x['struct'] == 'cross' and x['taker_side'] == 'yes'),
                      ('inplay_yes', lambda x: x['cls'] == 'inplay' and x['taker_side'] == 'yes'),
                      ('nongame_yes', lambda x: x['cls'] == 'nongame' and x['taker_side'] == 'yes')):
        sub = [x for x in rows if sel(x) and x['pnl'] is not None]
        t_game, n_game = cluster_t(sub, lambda x: x['game_key'] or x['ticker'], lambda x: x['pnl'] / x['cap'], lambda x: x['cap'])
        t_day, n_day = cluster_t(sub, lambda x: x['day'], lambda x: x['pnl'] / x['cap'], lambda x: x['cap'])
        P.setdefault('clustered_t', {})[name] = {'t_by_game_cluster': t_game, 'game_clusters': n_game,
                                                 't_by_day_cluster': t_day, 'day_clusters': n_day}
    A['kalshi_maker_pnl'] = P
    # who earns the rent: per day (scaled), YES buyers' premium and realized loss, the exchange's two fees, makers' net
    R = {}
    for name, sub in (('all', rows), ('pregame', [x for x in rows if x['cls'] == 'pregame']),
                      ('pregame_cross', [x for x in rows if x['cls'] == 'pregame' and x['struct'] == 'cross']),
                      ('pregame_same_or_mixed', [x for x in rows if x['cls'] == 'pregame' and x['struct'] in ('same', 'mixed')]),
                      ('inplay', [x for x in rows if x['cls'] == 'inplay']), ('nongame', [x for x in rows if x['cls'] == 'nongame'])):
        s = [x for x in sub if x['pnl'] is not None]
        y = [x for x in s if x['taker_side'] == 'yes']
        pf = [x for x in y if x['fair']]
        k = scale / len(days)
        R[name] = {'yes_premium_usd_per_day': sum(x['price'] * x['contracts'] for x in y) * k,
                   'yes_buyer_loss_pre_fee_usd_per_day': sum((x['price'] - x['settle']) * x['contracts'] for x in y) * k,
                   'model_margin_usd_per_day_priced_only': sum((x['price'] - x['fair']) * x['contracts'] for x in pf) * k,
                   'taker_fees_usd_per_day': sum(x['taker_fee'] for x in s) * k,
                   'maker_fees_usd_per_day': sum(x['maker_fee'] for x in s) * k,
                   'maker_net_usd_per_day': sum(x['pnl'] for x in s) * k,
                   'maker_capital_usd_per_day': sum(x['cap'] for x in s) * k}
    A['kalshi_rent_per_day'] = R
    # calibration of the leg-implied fair against outcomes (pregame, priced, YES buyers, settled)
    cal = []
    cr = [x for x in pre_priced if x['settled'] and x['taker_side'] == 'yes']
    for lo, hi in ((0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.35), (0.35, 0.5), (0.5, 0.75), (0.75, 1.01)):
        b = [x for x in cr if lo <= x['fair'] < hi]
        if not b:
            continue
        c = sum(x['contracts'] for x in b)
        cal.append({'fair_band': '%.2f-%.2f' % (lo, hi), 'trades': len(b),
                    'mean_fair': sum(x['fair'] * x['contracts'] for x in b) / c,
                    'mean_price': sum(x['price'] * x['contracts'] for x in b) / c,
                    'hit_rate': sum(x['settle'] * x['contracts'] for x in b) / c,
                    'hit_rate_unweighted': sum(x['settle'] for x in b) / len(b),
                    'mean_fair_unweighted': sum(x['fair'] for x in b) / len(b),
                    'mean_price_unweighted': sum(x['price'] for x in b) / len(b)})
    A['kalshi_calibration'] = cal
    # ---- the protocol: choose_then_test on the quoting rule (pre-registered family, see VARIANTS in analysis.json)
    pops = {'cross': lambda x: x['cls'] == 'pregame' and x['struct'] == 'cross' and x['taker_side'] == 'yes' and x['fair'],
            'samegame': lambda x: x['cls'] == 'pregame' and x['struct'] in ('same', 'mixed') and x['taker_side'] == 'yes' and x['fair']}
    variants, meta = {}, {}
    for pn, sel in pops.items():
        variants['%s/all' % pn] = daily_series(rows, days, sel)[0]
        meta['%s/all' % pn] = {'population': pn, 'm': None}
        for m in MARGINS:
            name = '%s/m=%.2f' % (pn, m)
            variants[name] = daily_series(rows, days, lambda x, s=sel, m=m: s(x) and x['price'] >= x['fair'] * (1 + m))[0]
            meta[name] = {'population': pn, 'm': m}
    ct = B.choose_then_test(variants, frac=SPLIT_FRAC, periods_per_year=365)
    cut_day = days[ct['cutoff_index']]

    def fills_of(select, price_fn=None, day_from=None):
        """(ticker, signed contracts, pnl, prob) for the payout z, at the print or at the quoter's own fill."""
        out_ = []
        for x in rows:
            if x['pnl'] is None or not select(x) or (day_from and x['day'] < day_from):
                continue
            p = x['price'] if price_fn is None else price_fn(x)
            if p is None:
                continue
            fee = combo_maker_fee(x['contracts'], p, maker_fee_applies(x['ticker'], x['ts'], 'current'))
            pnl_, _ = maker_pnl(p, x['contracts'], x['taker_side'], x['settle'], fee)
            sc = -x['contracts'] if x['taker_side'] == 'yes' else x['contracts']
            out_.append((x['ticker'], sc, pnl_, x['fair'] if x['fair'] else p))
        return out_
    vstats = {}
    for name in variants:
        pn_, m_ = meta[name]['population'], meta[name]['m']
        sel_ = (lambda x, s=pops[pn_], m=m_: s(x) and (m is None or x['price'] >= x['fair'] * (1 + m)))
        vstats[name] = {'full_sample': payout_z(fills_of(sel_)), 'out_of_sample': payout_z(fills_of(sel_, day_from=cut_day))}
    A['variant_payout_z'] = vstats
    c_ = ct['cutoff_index']
    vdesc = {}
    for name, ser in variants.items():
        pn_, m_ = meta[name]['population'], meta[name]['m']
        t_in, _ = B.newey_west_t(ser[:c_])
        t_out, _ = B.newey_west_t(ser[c_:])
        d_ = {'in_sample_sharpe': B.perf(ser[:c_], 365).get('sharpe'), 'in_sample_hac_t': t_in,
              'oos_ann_return': B.perf(ser[c_:], 365).get('ann_return'), 'oos_sharpe': B.perf(ser[c_:], 365).get('sharpe'),
              'oos_hac_t': t_out}
        if m_ is not None:
            sel_ = pops[pn_]
            fn_ = (lambda x, m=m_: own_quote_fill(x['price'], x['fair'], m))
            s_q, _, _ = daily_series(rows, days, sel_, price_fn=fn_)
            d_['own_quote_oos_ann_return'] = B.perf(s_q[c_:], 365).get('ann_return')
            d_['own_quote_oos_hac_t'] = B.newey_west_t(s_q[c_:])[0]
            d_['own_quote_oos_payout_z'] = payout_z(fills_of(sel_, price_fn=fn_, day_from=cut_day))
        vdesc[name] = d_
    A['variant_descriptive'] = vdesc
    A['protocol'] = {'variants_in_family': len(variants), 'variant_names': list(variants), 'cutoff_day': cut_day,
                     'choose_then_test': ct, 'periods_per_year': 365,
                     'note': 'daily return per $ risked of trades entered that day (capital turned once a day); '
                             'fills at the traded print (an upper bound: the quoter would have had to be the winner)'}
    ch = ct['chosen']
    pn, m = meta[ch]['population'], meta[ch]['m']
    sel = pops[pn]
    # executable implementation of the chosen variant: own quote at fair x (1 + m), won only below the print
    if m is not None:
        imp = lambda x, m=m: own_quote_fill(x['price'], x['fair'], m)  # noqa: E731
        s_imp, pnl_imp, cap_imp = daily_series(rows, days, sel, price_fn=imp)
    else:
        s_imp, pnl_imp, cap_imp = daily_series(rows, days, sel)
    c = B.cutoff_index(len(days), SPLIT_FRAC)
    oos_days = days[c:]
    t_imp, p_imp = B.newey_west_t(s_imp[c:])
    imp_fn = (lambda x, m=m: own_quote_fill(x['price'], x['fair'], m)) if m is not None else None
    imp_z = payout_z(fills_of(sel, price_fn=imp_fn, day_from=cut_day))
    won_oos = [x for x in rows if x['pnl'] is not None and sel(x) and x['day'] >= cut_day
               and (imp_fn is None or imp_fn(x) is not None)]
    t_game_imp, n_game_imp = cluster_t(won_oos, lambda x: x['game_key'] or x['ticker'],
                                       lambda x: x['pnl'] / x['cap'], lambda x: x['cap'])
    A['implementation'] = {'chosen': ch, 'rule': 'quote ask = fair x (1+m) rounded up to 0.001; won only when below '
                                                   'the incumbent print; filled at the quote; maker fee recharged',
                           'oos_perf': B.perf(s_imp[c:], 365), 'oos_hac_t': t_imp, 'oos_p': p_imp,
                           'oos_payout_z': imp_z,
                           'oos_game_cluster_t_at_print': t_game_imp, 'oos_game_clusters': n_game_imp,
                           'oos_pnl_sample_usd': sum(pnl_imp[d] for d in oos_days),
                           'oos_capital_sample_usd': sum(cap_imp[d] for d in oos_days),
                           'in_sample_perf': B.perf(s_imp[:c], 365)}
    # winner's curse: on the trades the own quote wins, model edge vs realized edge (per contract)
    wc = {}
    for pn2, sel2 in pops.items():
        for m2 in MARGINS:
            won = []
            for x in rows:
                if x['pnl'] is None or not sel2(x):
                    continue
                q = own_quote_fill(x['price'], x['fair'], m2)
                if q is not None:
                    won.append((x, q))
            if not won:
                continue
            C = sum(x['contracts'] for x, _ in won)
            wc['%s/m=%.2f' % (pn2, m2)] = {
                'won_trades': len(won), 'won_share_of_population': len(won) / max(1, sum(1 for x in rows if x['pnl'] is not None and sel2(x))),
                'model_edge_per_contract': sum((q - x['fair']) * x['contracts'] for x, q in won) / C,
                'realized_edge_per_contract': sum((q - x['settle']) * x['contracts'] for x, q in won) / C,
                'incumbent_print_edge_per_contract': sum((x['price'] - x['settle']) * x['contracts'] for x, _ in won) / C,
                'mean_quote': sum(q * x['contracts'] for x, q in won) / C,
                'mean_fair': sum(x['fair'] * x['contracts'] for x, _ in won) / C,
                'hit_rate': sum(x['settle'] * x['contracts'] for x, _ in won) / C}
    A['winners_curse'] = wc
    # capacity and $/yr of the chosen variant (traded-price version and implementation), scaled to the whole flow
    n_oos = len(oos_days)
    def dollars(pnl_d, cap_d):
        pnl = sum(pnl_d[d] for d in oos_days) * scale / n_oos
        cap = sum(cap_d[d] for d in oos_days) * scale / n_oos
        return {'pnl_usd_per_day': pnl, 'capital_usd_per_day': cap, 'pnl_usd_per_year': pnl * 365,
                'ssr_cost_usd_per_year': cap * SSR, 'excess_usd_per_year': pnl * 365 - cap * SSR}
    _, pnl_c, cap_c = daily_series(rows, days, lambda x: sel(x) and (m is None or x['price'] >= x['fair'] * (1 + m)))
    imp_d = dollars(pnl_imp, cap_imp)
    sd_yr = (imp_z.get('payout_sd_usd') or 0.0) * scale / n_oos * 365
    imp_d['excess_usd_per_year_ci95'] = [imp_d['excess_usd_per_year'] - 1.96 * sd_yr, imp_d['excess_usd_per_year'] + 1.96 * sd_yr]
    imp_d['payout_sd_usd_per_year_scaled'] = sd_yr
    A['capacity'] = {'chosen_at_print_whole_flow': dollars(pnl_c, cap_c),
                     'implementation_whole_flow': imp_d,
                     'note': 'whole flow = every sampled trade the rule selects, scaled by row_to_daily_flow; '
                             'capital = one day of risk (combos traded pre-game settle within a day, see hold_days)'}
    # the go rule (repo protocol) plus the payout gate this study adds for longshot books
    imp_cap = A['capacity']['implementation_whole_flow']
    go = {'in_sample_positive': bool(ct['in_sample_positive']),
          'oos_hac_t_ge_2': (ct['oos_t'] or 0) >= 2.0,
          'chosen_in_bh_survivors_positive': ch in ct['bh_survivors_positive'],
          'implementation_excess_positive': imp_cap['excess_usd_per_year'] > 0,
          'implementation_oos_hac_t': t_imp,
          'payout_gate_expected_payouts_ge_20': (imp_z.get('expected_payouts') or 0) >= 20,
          'payout_gate_z_ge_2': (imp_z.get('z') or 0) >= 2.0}
    go['go'] = all(go[k] for k in ('in_sample_positive', 'oos_hac_t_ge_2', 'chosen_in_bh_survivors_positive',
                                   'implementation_excess_positive', 'payout_gate_expected_payouts_ge_20',
                                   'payout_gate_z_ge_2'))
    A['go_rule'] = go
    A['polymarket'] = pm_section(out)
    A['polymarket']['fair_at_entry'] = pm_fair_section(out)
    # provenance: planned vs collected windows, and every collector's last request/failure count from its log
    planned_k = sample_windows(LIVE_FROM, '2026-10-12', 6, 60)
    have_k = {int(p.name.split('.')[0]) for p in (out / 'raw' / 'kalshi' / 'windows').glob('*.json.gz')}
    logs = {}
    for lg in sorted(out.glob('*.log')):
        last = [l for l in lg.read_text().splitlines() if 'requests=' in l or 'resolved positions' in l or 'give up' in l]
        logs[lg.name] = {'last_progress': last[-1] if last else None,
                         'give_ups': sum(1 for l in lg.read_text().splitlines() if 'give up' in l),
                         'tracebacks': lg.read_text().count('Traceback')}
    A['collection'] = {'kalshi_windows_planned': len(planned_k),
                       'kalshi_windows_collected': len(have_k & {w[2] for w in planned_k}),
                       'kalshi_windows_missing': sorted({w[2] for w in planned_k} - have_k),
                       'polygon_windows_collected': len(list((out / 'raw' / 'polygon' / 'windows').glob('*.json.gz'))),
                       'polymarket_makers_fetched': len(list((out / 'raw' / 'polymarket' / 'positions').glob('*.json.gz'))),
                       'logs': logs}
    update_manifest(out, 'collection_summary', dict(A['collection'], summarized_at=A['generated_at']))
    write_json(out / 'analysis.json', A)
    entries = []
    if go['go']:
        entries.append({
            'id': 'kalshi-combo-quoter', 'name': 'Quote Kalshi pre-game combo RFQs at leg-implied fair plus a margin',
            'kind': 'rfq-quoting', 'status': 'proposed',
            'thesis': 'chosen %s; out-of-sample HAC t %.2f' % (ch, ct['oos_t']),
            'capacity_usd': imp_cap['capital_usd_per_day'],
            'quotes': [{'at': A['generated_at'], 'source': 'history', 'window': 'research/2026-10-14/pm_parlays',
                        'usd': imp_cap['excess_usd_per_year'], 'go': True, 'present': True}],
            'risks': ['winner\'s curse: the quoter wins the requests where its fair is lowest',
                      'longshot payout variance (see variant_payout_z)'],
            'evidence': ['research/2026-10-14/pm_parlays/analysis.json']})
    write_json(out / 'book_entries.json', entries)
    write_gz(out / 'raw' / 'kalshi_rows.json.gz', rows)
    print(json.dumps({'protocol': {k: ct[k] for k in ('chosen', 'in_sample_positive', 'oos_t', 'oos_rank',
                                                      'bh_survivors_positive')},
                      'oos': ct['out_of_sample'].get('ann_return'), 'impl_oos_t': t_imp}, default=str))
    return 0


# ------------------------------------------------------------------------------------------------ render

def _pct(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def _usd(x):
    if x is None:
        return '—'
    a = abs(x)
    s = '$%.2fM' % (x / 1e6) if a >= 1e6 else ('$%.1fk' % (x / 1e3) if a >= 1e4 else '$%.0f' % x)
    return s


def _f(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_parlays tables (%s)' % A['generated_at'], '',
         'Every number is in `analysis.json` (key in brackets). Kalshi = public trade tape, live tier; Polymarket = '
         'Exchange v3 logs on Polygon plus the data-api positions of the largest makers.', '']
    S, K = A['kalshi_sample'], A['kalshi_scale']
    L += ['## 1. Kalshi sample and flow [kalshi_sample, kalshi_scale]', '',
          '| item | value |', '|---|---:|',
          '| windows (60 s, stratified 6 per UTC day) | %d over %d days (%s to %s) |' % (S['windows'], S['days'], S['first_day'], S['last_day']),
          '| tape trades read / combo trades | %d / %d |' % (S['tape_trades'], S['tape_combo_trades']),
          '| combo share of contracts / of trades | %s / %s |' % (_pct(S['combo_share_of_contracts']), _pct(S['combo_share_of_trades'])),
          '| combos kept (hash subsample) share of combo contracts | %s |' % _pct(S['kept_share_of_combo_contracts']),
          '| kept combo trades analysed (settled / unsettled) | %d (%d / %d) |' % (S['kept_trades'], S['settled_trades'], S['unsettled_trades']),
          '| combo contracts per day (scaled) | %.0fM |' % (K['combo_contracts_per_day'] / 1e6),
          '| combo YES-price premium per day (scaled) | %s |' % _usd(K['combo_premium_usd_per_day']), '']
    C = A['kalshi_composition']
    L += ['## 2. What the combo flow is [kalshi_composition]', '', '| group | value | trades | premium $/day |', '|---|---|---:|---:|']
    for g in ('cls', 'struct', 'taker_side', 'fee_series', 'legs', 'sport'):
        for k, v in list(C[g].items())[:14]:
            L.append('| %s | %s | %d | %s |' % (g, k, v['trades'], _usd(v['premium_usd_per_day'])))
    L.append('')
    cov = A['kalshi_pricing_coverage']
    L += ['Pre-game trades with every leg priced: %d of %d (%s); median age of the oldest leg book at the trade %.0f s '
          '[kalshi_pricing_coverage].' % (cov['pregame_priced'], cov['pregame_trades'], _pct(cov['priced_share']), cov['leg_age_median_s']), '']
    M = A['kalshi_margin']
    L += ['## 3. Implied margin of pre-game combos, YES buyers [kalshi_margin]', '',
          'margin = print / product of leg mids − 1. "above asks" = share of prints above the product of the leg asks.', '',
          '| cut | bucket | trades | premium | median margin | premium-weighted margin | above asks | below bids |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    def mrow(cut, k, v):
        if not v.get('n'):
            return
        L.append('| %s | %s | %d | %s | %s | %s | %s | %s |' % (cut, k, v['n'], _usd(v['premium_usd']), _pct(v['margin_median']),
                                                                _pct(v['margin_premium_weighted']), _pct(v['share_above_ask_product'], 0),
                                                                _pct(v['share_below_bid_product'], 0)))
    mrow('all', 'pre-game priced', M['all_pregame_priced'])
    for cut in ('struct', 'cross_by_legs', 'legs', 'cross_by_sport', 'cross_by_fee_series', 'fee_series', 'price_band', 'week', 'cross_by_week'):
        for k, v in M[cut].items():
            mrow(cut, k, v)
    L.append('')
    L += ['## 4. Is the leg product calibrated? Pre-game priced YES buys, settled [kalshi_calibration]', '',
          '| fair band | trades | mean fair | mean price | hit rate (contract-weighted) | hit rate (per trade) | mean fair (per trade) |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for x in A['kalshi_calibration']:
        L.append('| %s | %d | %s | %s | %s | %s | %s |' % (x['fair_band'], x['trades'], _f(x['mean_fair'], 4), _f(x['mean_price'], 4),
                                                         _f(x['hit_rate'], 4), _f(x['hit_rate_unweighted'], 4), _f(x['mean_fair_unweighted'], 4)))
    L.append('')
    P = A['kalshi_maker_pnl']
    L += ['## 5. The quoting side\'s realized P&L at the prints (current fee schedule) [kalshi_maker_pnl]', '',
          '| cut | bucket | trades | maker P&L | capital | per $ risked | buyer loss / premium (pre-fee) | maker fees | median hold (d) |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    def prow(cut, k, v):
        if not v.get('n'):
            return
        L.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s |' % (cut, k, v['n'], _usd(v['pnl_usd']), _usd(v['capital_usd']),
                                                                   _pct(v['pnl_per_risked'], 2), _pct(v['buyer_loss_per_premium_before_fees']),
                                                                   _usd(v['maker_fees_usd']), _f(v['hold_days_median'])))
    prow('all', 'all', P['all'])
    for cut in ('cls', 'cls_struct', 'taker_side', 'fee_series', 'legs', 'sport'):
        for k, v in P[cut].items():
            prow(cut, k, v)
    L += ['', '| population | t (game clusters) | games | t (day clusters) | days |', '|---|---:|---:|---:|---:|']
    for k, v in P['clustered_t'].items():
        L.append('| %s | %s | %d | %s | %d |' % (k, _f(v['t_by_game_cluster']), v['game_clusters'], _f(v['t_by_day_cluster']), v['day_clusters']))
    L.append('')
    L += ['## 5b. Who earns the rent, per day (scaled to the whole flow) [kalshi_rent_per_day]', '',
          '| class | YES premium | buyer loss pre-fee | model margin (priced) | taker fees | maker fees | maker net | maker capital |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['kalshi_rent_per_day'].items():
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (k, _usd(v['yes_premium_usd_per_day']), _usd(v['yes_buyer_loss_pre_fee_usd_per_day']),
                                                             _usd(v['model_margin_usd_per_day_priced_only']), _usd(v['taker_fees_usd_per_day']),
                                                             _usd(v['maker_fees_usd_per_day']), _usd(v['maker_net_usd_per_day']),
                                                             _usd(v['maker_capital_usd_per_day'])))
    L.append('')
    pr, ct = A['protocol'], A['protocol']['choose_then_test']
    L += ['## 6. Protocol: choose_then_test on "sell when print >= fair x (1 + m)" [protocol, variant_payout_z]', '',
          '%d pre-registered variants, chosen on days before %s, tested once after. Fills at the print (an upper bound).' % (
              pr['variants_in_family'], pr['cutoff_day']), '',
          '| variant | full-sample P&L | payout sd | payout z | expected payouts | combos | OOS P&L | OOS payout z | OOS expected payouts |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['variant_payout_z'].items():
        f_, o_ = v['full_sample'], v['out_of_sample']
        L.append('| %s | %s | %s | %s | %s | %d | %s | %s | %s |' % (k, _usd(f_['pnl_usd']), _usd(f_['payout_sd_usd']), _f(f_['z']),
                                                                   _f(f_['expected_payouts'], 1), f_['combos'], _usd(o_['pnl_usd']),
                                                                   _f(o_['z']), _f(o_['expected_payouts'], 1)))
    L += ['', '| item | value |', '|---|---|',
          '| chosen | %s |' % ct['chosen'],
          '| in-sample positive / ann. return / Sharpe | %s / %s / %s |' % (ct['in_sample_positive'], _pct(ct['in_sample'].get('ann_return')), _f(ct['in_sample'].get('sharpe'))),
          '| out-of-sample ann. return / Sharpe / HAC t / rank | %s / %s / %s / %d of %d |' % (
              _pct(ct['out_of_sample'].get('ann_return')), _f(ct['out_of_sample'].get('sharpe')), _f(ct['oos_t']), ct['oos_rank'], ct['n_variants']),
          '| BH survivors (positive, full sample) | %s |' % (', '.join(ct['bh_survivors_positive']) or 'none'),
          '| deflated Sharpe of the in-sample choice | %s |' % _f(ct['deflated_sharpe_in_sample']), '']
    L += ['', 'Per-variant detail (descriptive; only the chosen row is the protocol result) [variant_descriptive]:', '',
          '| variant | in-sample Sharpe | in-sample HAC t | OOS ann. return (print) | OOS HAC t (print) | own-quote OOS ann. return | own-quote OOS HAC t | own-quote OOS payout z |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['variant_descriptive'].items():
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (k, _f(v['in_sample_sharpe']), _f(v['in_sample_hac_t']), _pct(v['oos_ann_return']),
                                                             _f(v['oos_hac_t']), _pct(v.get('own_quote_oos_ann_return')), _f(v.get('own_quote_oos_hac_t')),
                                                             _f((v.get('own_quote_oos_payout_z') or {}).get('z'))))
    L.append('')
    I = A['implementation']
    L += ['## 7. Executable implementation and the winner\'s curse [implementation, winners_curse]', '',
          'Rule: %s.' % I['rule'], '',
          '| item | value |', '|---|---|',
          '| OOS ann. return / HAC t (daily) | %s / %s |' % (_pct(I['oos_perf'].get('ann_return')), _f(I['oos_hac_t'])),
          '| OOS payout z / expected payouts / combos | %s / %s / %d |' % (_f(I['oos_payout_z']['z']), _f(I['oos_payout_z']['expected_payouts'], 2), I['oos_payout_z']['combos']),
          '| OOS P&L / capital in the sample | %s / %s |' % (_usd(I['oos_pnl_sample_usd']), _usd(I['oos_capital_sample_usd'])), '',
          '| variant | won trades | share of population | mean quote | mean fair | model edge / contract | realized edge / contract | incumbent print edge / contract | hit rate |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['winners_curse'].items():
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (k, v['won_trades'], _pct(v['won_share_of_population']), _f(v['mean_quote'], 4),
                                                                   _f(v['mean_fair'], 4), _f(v['model_edge_per_contract'], 4),
                                                                   _f(v['realized_edge_per_contract'], 4), _f(v['incumbent_print_edge_per_contract'], 4),
                                                                   _f(v['hit_rate'], 4)))
    cp = A['capacity']
    L += ['', '## 8. Capacity and dollars [capacity, go_rule]', '', '| version | P&L $/day | capital $/day | P&L $/yr | SSR cost $/yr | excess $/yr |',
          '|---|---:|---:|---:|---:|---:|']
    for k in ('chosen_at_print_whole_flow', 'implementation_whole_flow'):
        v = cp[k]
        L.append('| %s | %s | %s | %s | %s | %s |' % (k, _usd(v['pnl_usd_per_day']), _usd(v['capital_usd_per_day']), _usd(v['pnl_usd_per_year']),
                                                    _usd(v['ssr_cost_usd_per_year']), _usd(v['excess_usd_per_year'])))
    ci = cp['implementation_whole_flow'].get('excess_usd_per_year_ci95')
    if ci:
        L += ['', 'Implementation excess 95%% interval from its payout sd: %s to %s a year. "Whole flow" assumes the quoter sees '
              'every RFQ and wins every one its quote undercuts, with no incumbent response: an upper bound on share.' % (_usd(ci[0]), _usd(ci[1]))]
    L += ['', 'Go rule: ' + ', '.join('%s=%s' % (k, v) for k, v in A['go_rule'].items()), '']
    PM = A.get('polymarket') or {}
    if PM.get('onchain'):
        o = PM['onchain']
        L += ['## 9. Polymarket Combos on chain [polymarket.onchain]', '', '| item | value |', '|---|---|',
              '| windows (600 blocks, 4 per day) / days / matches | %d / %d / %d |' % (o['windows'], o['days'], o['matches']),
              '| requester $ per day (all / buys) | %s / %s |' % (_usd(o['requester_usd_per_day']), _usd(o['requester_buy_usd_per_day'])),
              '| fees $ per day (requester pays 0.05 x p(1-p); makers none) | %s |' % _usd(o['fees_usd_per_day']),
              '| fee = 0.05 x shares x p(1-p) exactly (+-0.002 in rate) | %s of %d matches; the rest pay rates %s (leg-category blends) |' % (
                  _pct(o['fee_rate_0p05_share']), o['fee_formula_checked_matches'], ', '.join('%.3f' % r for r in o['fee_rate_other_quantiles'])),
              '| buy price median / $-weighted | %s / %s |' % (_f(o['buy_price_median'], 3), _f(o['buy_usd_weighted_price'], 3)),
              '| distinct makers / requesters / makers per match | %d / %d / %s |' % (o['makers_distinct'], o['requesters_distinct'], _f(o['makers_per_match_mean'])),
              '| top-5 makers\' share of maker $ | %s |' % _pct(o['maker_top5_share']),
              '| share of onchain maker $ by the wallets whose positions were fetched (section 10) | %s |' % _pct(o.get('maker_usd_share_with_positions_fetched')), '']
    if PM.get('maker_positions'):
        mp = PM['maker_positions']
        L += ['## 10. Polymarket makers\' realized rent from their resolved positions [polymarket.maker_positions, polymarket.makers]', '',
              '| cut | bucket | positions | cost | P&L | return on cost |', '|---|---|---:|---:|---:|---:|']
        L.append('| pooled | all | %d | %s | %s | %s |' % (mp['pooled']['positions'], _usd(mp['pooled']['cost_usd']), _usd(mp['pooled']['pnl_usd']), _pct(mp['pooled']['return_on_cost'], 2)))
        for cut in ('by_side', 'by_structure', 'by_legs', 'by_market_types', 'by_month'):
            for k, v in mp[cut].items():
                L.append('| %s | %s | %d | %s | %s | %s |' % (cut, k, v['positions'], _usd(v['cost_usd']), _usd(v['pnl_usd']), _pct(v['return_on_cost'], 2)))
        d = mp['daily']
        L += ['', 'Daily pooled return on cost by resolution day: %d days (%s to %s), mean %s, HAC t %s; cost %s/day, P&L %s/day.' % (
            d['days'], d['first'], d['last'], _pct(d['mean_daily_return_on_cost'], 2), _f(d['hac_t']), _usd(d['cost_usd_per_day']), _usd(d['pnl_usd_per_day'])), '',
              '| maker | positions | cost | P&L | return on cost | NO-side share | first entry | last resolution |', '|---|---:|---:|---:|---:|---:|---|---|']
        for a, v in sorted(PM['makers'].items(), key=lambda kv: -kv[1]['cost_usd']):
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (a[:10], v['positions'], _usd(v['cost_usd']), _usd(v['pnl_usd']), _pct(v['return_on_cost'], 2),
                                                                 _pct(v['no_side_share'], 0), (v['first'] or '')[:10], (v['last'] or '')[:10]))
        L.append('')
    fa = (PM or {}).get('fair_at_entry') or {}
    if fa.get('all', {}).get('n'):
        L += ['## 11. Polymarket implied margin at entry, pre-game sample [polymarket.fair_at_entry]', '',
              '%d sampled maker NO positions, %d pre-game, %d with every leg priced. %s' % (fa['positions'], fa['pregame'], fa['priced_pregame'], fa['note']), '',
              '| cut | bucket | n | median margin | premium-weighted margin | maker return (cost-weighted) | maker return (equal weight +- se) | mean YES | mean fair |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
        def frow(cut, k, v):
            if v.get('n'):
                L.append('| %s | %s | %d | %s | %s | %s | %s +- %s | %s | %s |' % (cut, k, v['n'], _pct(v['margin_median']), _pct(v['margin_premium_weighted']),
                                                                     _pct(v['maker_return_on_cost'], 2), _pct(v.get('maker_return_equal_weight'), 1),
                                                                     _pct(v.get('maker_return_equal_weight_se'), 1), _f(v['mean_yes'], 3), _f(v['mean_fair'], 3)))
        frow('all', 'pre-game priced', fa['all'])
        for cut in ('by_structure', 'by_legs'):
            for k, v in fa[cut].items():
                frow(cut, k, v)
        L.append('')
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0


# ------------------------------------------------------------------------------------------------ Polymarket: fair value at entry

GAMMA = 'https://gamma-api.polymarket.com'
CLOB = 'https://clob.polymarket.com'


def cmd_pm_fair(args):
    """For a hashed sample of the makers' resolved NO positions: each leg's CLOB price (prices-history, a midpoint)
    at the position's first entry, the game start (gamma), and so the leg-product fair and the implied margin."""
    out = Path(args.out)
    pos = []
    for p in sorted((out / 'raw' / 'polymarket' / 'positions').glob('*.json.gz')):
        d = read_gz(p)
        for r in d['positions']:
            if r.get('outcome_index') != 1 or not r.get('first_entry_at') or not r.get('legs'):
                continue
            if not (2 <= len(r['legs']) <= 6) or any(not l.get('market_id') for l in r['legs']):
                continue
            if (r.get('first_entry_at') or '') < args.since:
                continue
            u = stable_u('pmfair|%s|%s' % (d['maker'], r['combo_condition_id']))
            if u < args.frac:
                pos.append(dict(r, maker=d['maker'], _u=u))
    pos = sorted(pos, key=lambda r: r['_u'])[:args.max_positions]     # uniform across makers, reproducible
    http = Http(interval=0.5)
    mids = sorted({l['market_id'] for r in pos for l in r['legs']})
    gamma = {}
    for i in range(0, len(mids), 20):
        q = '&'.join('id=%s' % m for m in mids[i:i + 20])
        d = http.request(GAMMA + '/markets?' + q + '&closed=true&limit=50')
        if isinstance(d, list):
            for m in d:
                gamma[str(m['id'])] = {'tokens': json.loads(m.get('clobTokenIds') or '[]'), 'start': m.get('gameStartTime'),
                                       'closed': m.get('closedTime'), 'slug': m.get('slug')}
    rows = []
    for r in pos:
        t = parse_ts(r['first_entry_at'])
        starts = [parse_ts((gamma.get(str(l['market_id'])) or {}).get('start')) for l in r['legs']]
        pre = all(starts) and t < min(starts)
        legs = []
        if pre:
            for l in r['legs']:
                g = gamma.get(str(l['market_id'])) or {}
                toks = g.get('tokens') or []
                oi = l.get('outcome_index')
                if oi is None or oi >= len(toks):
                    legs.append(None)
                    continue
                q = urllib.parse.urlencode({'market': toks[oi], 'startTs': int(t - 3 * 3600), 'endTs': int(t), 'fidelity': 1})
                h = http.request(CLOB + '/prices-history?' + q)
                pts = [x for x in (h.get('history') or [])] if isinstance(h, dict) else []
                pts = [x for x in pts if x.get('t') is not None and x['t'] <= t]
                legs.append(pts[-1]['p'] if pts else None)
        rows.append({'maker': r['maker'], 'combo': r['combo_condition_id'], 'entry': r['first_entry_at'], 'pregame': pre,
                     'no_price': r.get('entry_avg_price_usdc'), 'cost': r.get('gross_entry_cost_usdc'),
                     'payout': r.get('realized_payout_usdc'), 'legs_total': len(r['legs']),
                     'events': [l.get('event_id') for l in r['legs']], 'types': [l.get('type') for l in r['legs']],
                     'leg_prices': legs})
    write_gz(out / 'raw' / 'polymarket' / 'fair_sample.json.gz', rows)
    update_manifest(out, 'polymarket_fair', {'finished_at': utc(time.time()), 'positions_sampled': len(pos),
                                             'pregame': sum(1 for x in rows if x['pregame']), 'frac': args.frac,
                                             'since': args.since, 'http': http.stats()})
    print('fair sample: %d positions, %d pre-game' % (len(rows), sum(1 for x in rows if x['pregame'])))
    return 0


def pm_fair_section(out):
    p = out / 'raw' / 'polymarket' / 'fair_sample.json.gz'
    if not p.exists():
        return {}
    rows = read_gz(p)
    ok = []
    for x in rows:
        if not x['pregame'] or not x['leg_prices'] or any(v is None or not (0 < v < 1) for v in x['leg_prices']):
            continue
        fair = 1.0
        for v in x['leg_prices']:
            fair *= v
        yes = 1.0 - (x['no_price'] or 0.0)
        if not (0 < yes < 1):
            continue
        ok.append(dict(x, fair=fair, yes=yes, margin=implied_margin(yes, fair), struct=structure_of(x['events']) if all(x['events']) else 'unknown'))

    def st(v):
        if not v:
            return {'n': 0}
        w = [x['cost'] / max(1e-9, 1.0 - x['yes']) * x['yes'] for x in v]          # YES premium the requester paid
        r_ = [x['payout'] / x['cost'] - 1.0 for x in v if x['cost']]
        return {'n': len(v), 'margin_median': statistics.median([x['margin'] for x in v]),
                'maker_return_equal_weight': statistics.mean(r_) if r_ else None,
                'maker_return_equal_weight_se': (statistics.pstdev(r_) / math.sqrt(len(r_))) if len(r_) > 1 else None,
                'margin_premium_weighted': sum(w) / sum(wi / x['yes'] * x['fair'] for wi, x in zip(w, v)) - 1.0,
                'maker_return_on_cost': (sum(x['payout'] for x in v) - sum(x['cost'] for x in v)) / sum(x['cost'] for x in v),
                'mean_yes': statistics.mean([x['yes'] for x in v]), 'mean_fair': statistics.mean([x['fair'] for x in v])}
    return {'positions': len(rows), 'pregame': sum(1 for x in rows if x['pregame']), 'priced_pregame': len(ok),
            'all': st(ok), 'by_structure': {k: st(v) for k, v in group_by(ok, lambda x: x['struct']).items()},
            'by_legs': {k: st(v) for k, v in sorted(group_by(ok, lambda x: legs_bucket(x['legs_total'])).items())},
            'note': 'leg price = CLOB prices-history point at or before the first entry (a midpoint); YES price = 1 - '
                    'the maker\'s average NO entry; margin = YES / product of legs - 1'}


# ------------------------------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('kalshi-milestones'); s.set_defaults(fn=cmd_k_milestones)
    s.add_argument('--out', required=True)
    s.add_argument('--since', default='2026-08-01T00:00:00Z')
    c = sub.add_parser('kalshi-collect'); c.set_defaults(fn=cmd_k_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--day-from', default=LIVE_FROM)
    c.add_argument('--day-to', default='2026-10-12')
    c.add_argument('--per-day', type=int, default=6)
    c.add_argument('--width', type=int, default=60)
    c.add_argument('--combo-frac', type=float, default=0.15)
    c.add_argument('--lookback', type=int, default=3600)
    o = sub.add_parser('pm-collect'); o.set_defaults(fn=cmd_pm_collect)
    o.add_argument('--out', required=True)
    o.add_argument('--day-from', default='2026-09-01')
    o.add_argument('--day-to', default='2026-10-13')
    o.add_argument('--per-day', type=int, default=4)
    o.add_argument('--blocks', type=int, default=600)
    o.add_argument('--max-credits', type=int, default=300000)
    mk = sub.add_parser('pm-makers'); mk.set_defaults(fn=cmd_pm_makers)
    mk.add_argument('--out', required=True)
    mk.add_argument('--top', type=int, default=25)
    mk.add_argument('--max-pages', type=int, default=200)
    mk.add_argument('--start-rank', type=int, default=1, help='skip the makers ranked above this (parallel runs)')
    pf = sub.add_parser('pm-fair'); pf.set_defaults(fn=cmd_pm_fair)
    pf.add_argument('--out', required=True)
    pf.add_argument('--frac', type=float, default=0.02)
    pf.add_argument('--since', default='2026-08-01')
    pf.add_argument('--max-positions', type=int, default=700)
    an = sub.add_parser('analyze'); an.set_defaults(fn=cmd_analyze)
    an.add_argument('--out', required=True)
    rn = sub.add_parser('render'); rn.set_defaults(fn=cmd_render)
    rn.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
