#!/usr/bin/env python3
"""Venue liquidity rents: do Polymarket's and Kalshi's maker incentives pay a slow quoter more than adverse selection
costs it?

Why. The repo's frame is that alpha is a rent paid by a counterparty with a non-price motive. A venue's marketing
budget is the cleanest such payer: Polymarket pays resting quotes a daily pool per market ("liquidity rewards"),
redistributes 15-25% of taker fees to the makers who were filled ("maker rebates") and pays 3.25% a year on positions
in 18 long-dated events ("holding rewards"); Kalshi runs a Liquidity Incentive Program (LIP) per market and pays 3.50%
on cash and positions. None of these payers cares about price. The question is whether a quoter that re-centres only
once an hour (never racing) collects more of them than the informed flow it is filled by takes back.

Mechanics, pinned in pure functions below (tests: scripts/test_pm_rewards_mm.py):
  * Polymarket liquidity rewards (docs.polymarket.com/programs/liquidity-rewards, read 2026-10-14): an order at
    distance s (cents) from the size-cutoff-adjusted midpoint, inside the market's max spread v, scores
    S = ((v - s) / v)^2 * b (b = in-game multiplier, 1 outside live sports) times its size in shares, if its size is
    at least the market's min size. Q_one sums the YES bids and NO asks, Q_two the YES asks and NO bids. A maker's
    sample score is min(Q_one, Q_two), or max(min, max/c) with c = 3 when the midpoint is in [0.10, 0.90]. Each
    minute (random offset) the scores are normalised across makers; the day's pool is split by the sum of normalised
    scores, so a maker present in every sample earns rate x mean(own / (own + others)). Payout >= $1, daily.
    The adjusted midpoint ignores levels below the min size (a third-party reading; the docs do not define it).
  * Polymarket's YES and NO books are one book: the NO token's bids are the YES asks at 1 - p (checked live,
    2026-10-14), so reading the YES book scores both sides.
  * Maker rebates (docs .../programs/maker-rebates): makers are paid rebate_rate x their fee-equivalent
    C x feeRate x p x (1 - p) on filled shares, per market per day (rebate_rate 0.20 crypto, 0.15 sports, 0.25 else,
    none on fee-free geopolitics). Makers pay no fee.
  * Holding rewards (help.polymarket.com/en/articles/13364459, updated 2026-06-01): 3.25% a year on the mid-valued
    YES + NO position in 18 listed events, sampled hourly, paid daily; a complete set is worth $1 and earns it.
  * Kalshi LIP (help.kalshi.com/en/articles/13823851): one snapshot a second; per side, orders that help reach the
    Target Size score size x discount^(ticks beyond the reference price), the reference price being the first level
    where cumulative size reaches Target/5; a snapshot counts only if both sides reach Target; each side is
    normalised and a snapshot is worth at most 2. US members only. Kalshi APY: 3.50% on cash and positions, US only,
    balances >= $250 (help.kalshi.com/en/articles/13823847).

Subcommands (in order):
    uv run python scripts/pm_rewards_mm.py collect rewards        # reward configs (CLOB current, sponsored, multi)
    uv run python scripts/pm_rewards_mm.py collect gamma          # active markets: tags, fees, holding flag (capped)
    uv run python scripts/pm_rewards_mm.py collect gamma-fill     # rewarded markets the capped scan missed
    uv run python scripts/pm_rewards_mm.py collect books          # a book snapshot of every rewarded market (repeat)
    uv run python scripts/pm_rewards_mm.py collect trades         # trades + hourly prices, stratified sample
    uv run python scripts/pm_rewards_mm.py collect chain          # daily reward payouts on Polygon (60 days)
    uv run python scripts/pm_rewards_mm.py collect kalshi         # LIP programs + books for a sample
    uv run python scripts/pm_rewards_mm.py collect kalshi-books   # re-read the slow LIP books (repeat)
    uv run python scripts/pm_rewards_mm.py collect kalshi-trades  # trades + hourly candles of the slow LIP sample
    uv run python scripts/pm_rewards_mm.py analyze                # analysis.json, book_entries.json
    uv run python scripts/pm_rewards_mm.py render                 # tables.md

Design decisions fixed before returns were seen are in the constants (S_GRID_FRAC, SIZE_MULT, VOL_SCREEN, INV_CAP,
K_SIZES, K_VOL_CENTS, FAV_*). One was added after a first simulation pass and is disclosed in analysis.json
(first_pass_disclosed): JOIN_MIN, quoting only where others already quote both sides inside the band, with a floor at
today's touch, because a lone quote inside a 20c spread prices a midpoint that is not a price.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B  # noqa: E402
from polymarket_history import (Http, categorize, fee_rate, parse_ts, write_gz, read_gz, update_manifest,  # noqa: E402
                                stable_u, write_json)
from pm_crossvenue import http_json, kalshi_fee  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / '2026-10-14' / 'pm_rewards_mm'
GAMMA = 'https://gamma-api.polymarket.com'
CLOB = 'https://clob.polymarket.com'
DATA = 'https://data-api.polymarket.com'
KALSHI = 'https://api.elections.kalshi.com/trade-api/v2/'
SSR = 0.038
C_SCALE = 3.0                 # "currently 3.0 on all markets"
HOLDING_RATE = 0.0325         # Polymarket holding rewards, annualised, help article updated 2026-06-01
KALSHI_APY = 0.035            # Kalshi APY on cash and positions (help article read 2026-10-14)
PUSD = '0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB'
USDCE = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
REBATE_RATE_BY_CAT = {'crypto': 0.20, 'sports': 0.15}   # every other fee-enabled category 0.25; geopolitics none
HOUR = 3600.0
DAY = 86400.0


# ------------------------------------------------------------------------------------------------- pure: scoring

def order_score(v, s, b=1.0):
    """Polymarket's quadratic order score S(v, s) = ((v - s) / v)^2 * b, with v the max spread and s the distance
    from the adjusted midpoint, both in cents. Zero at or beyond v; a distance within rounding of zero counts as 0."""
    if v is None or s is None or v <= 0:
        return 0.0
    if s < 0:
        if s < -1e-9:
            return 0.0
        s = 0.0
    if s >= v:
        return 0.0
    return ((v - s) / v) ** 2 * b


def adjusted_mid(bids, asks, min_size):
    """Midpoint of the best bid and best ask among levels holding at least `min_size` shares (bids, asks are
    [(price, size)] in any order). Falls back to the raw midpoint when a side has no level that large; None if a
    side is empty."""
    if not bids or not asks:
        return None
    qb = [p for p, sz in bids if sz >= min_size]
    qa = [p for p, sz in asks if sz >= min_size]
    bb = max(qb) if qb else max(p for p, _ in bids)
    ba = min(qa) if qa else min(p for p, _ in asks)
    if bb >= ba:   # filtered levels crossed (cannot happen on a live book); use the raw touch
        bb, ba = max(p for p, _ in bids), min(p for p, _ in asks)
    return (bb + ba) / 2.0


def side_scores(bids, asks, mid, v, min_size, b=1.0):
    """(Q_one, Q_two) of a set of YES-book levels: Q_one from bids (YES bids and NO asks, which the YES book shows
    as bids), Q_two from asks. Distances in cents. Levels below `min_size` do not score."""
    q1 = sum(order_score(v, (mid - p) * 100.0, b) * sz for p, sz in bids if sz >= min_size)
    q2 = sum(order_score(v, (p - mid) * 100.0, b) * sz for p, sz in asks if sz >= min_size)
    return q1, q2


def q_min(q1, q2, mid, c=C_SCALE):
    """A maker's sample score: two-sided min, with single-sided liquidity scoring 1/c while the midpoint is in
    [0.10, 0.90]; outside that range only two-sided liquidity scores."""
    if mid is not None and 0.10 <= mid <= 0.90:
        return max(min(q1, q2), max(q1, q2) / c)
    return min(q1, q2)


def competitor_bounds(q1, q2, mid, c=C_SCALE):
    """Bounds on the sum of makers' Q_min when only the side totals are known (books are aggregated by level).
    Upper: every maker balanced, the excess of the larger side held one-sided at 1/c. Lower: each maker scores at
    least max(own sides)/c in range (so the sum is at least max(q1, q2)/c); out of range it can be zero."""
    lo, hi = min(q1, q2), max(q1, q2)
    if mid is not None and 0.10 <= mid <= 0.90:
        return {'upper': lo + (hi - lo) / c, 'lower': hi / c}
    return {'upper': lo, 'lower': 0.0}


def reward_share(q_ours, q_others):
    if q_ours <= 0:
        return 0.0
    return q_ours / (q_ours + max(0.0, q_others))


def quote_prices(mid, s_cents, tick, best_bid=None, best_ask=None):
    """Bid and ask on the tick grid at least `s_cents` from `mid`, never crossing the book: the bid is rounded down,
    the ask up, and each is pulled back to at most the best bid / at least the best ask (a post-only quote)."""
    t = tick or 0.01
    eps = 1e-9
    bid = math.floor((mid - s_cents / 100.0) / t + eps) * t
    ask = math.ceil((mid + s_cents / 100.0) / t - eps) * t
    if best_ask is not None and bid >= best_ask - eps:
        bid = best_ask - t
    if best_bid is not None and ask <= best_bid + eps:
        ask = best_bid + t
    bid = round(max(t, bid), 6)
    ask = round(min(1.0 - t, ask), 6)
    return bid, ask


def quote_capital(q, bid, ask):
    """Collateral locked by a two-sided quote of q shares: the YES bid locks q x bid; the ask is a NO bid at 1 - ask
    (or YES shares from a split set), q x (1 - ask). Together q x (1 - (ask - bid)); a complete set (q dollars) backs
    both sides as well."""
    return q * (bid + (1.0 - ask))


# ------------------------------------------------------------------------------------------------- pure: money

def maker_rebate(shares, price, fee_rate_, rebate_rate):
    """Polymarket maker rebate on a filled maker order: rebate_rate x C x feeRate x p x (1 - p)."""
    if shares <= 0 or not fee_rate_ or not rebate_rate:
        return 0.0
    return rebate_rate * shares * fee_rate_ * price * (1.0 - price)


def rebate_rate_for(cat_fee, fee_rate_):
    """Rebate share by fee category ('crypto', 'sports', else 0.25); zero where the taker fee is zero."""
    if not fee_rate_:
        return 0.0
    return REBATE_RATE_BY_CAT.get(cat_fee, 0.25)


def holding_reward(yes_shares, no_shares, mid_yes, hours, rate=HOLDING_RATE):
    """Polymarket holding reward for `hours` on a position valued at the midpoints (YES at mid, NO at 1 - mid)."""
    value = max(0.0, yes_shares) * mid_yes + max(0.0, no_shares) * (1.0 - mid_yes)
    return value * rate * hours / 8760.0


def to_yes_terms(price, side, outcome_index):
    """A trade on the NO token (outcome index 1) at q with taker side X is a YES trade at 1 - q with the opposite
    taker side."""
    if int(outcome_index or 0) == 0:
        return float(price), side
    return 1.0 - float(price), ('SELL' if side == 'BUY' else 'BUY')


def through_fill(quote_px, quote_side, trade_px, trade_side, trade_size, remaining):
    """Conservative queue: a resting YES bid fills only from a taker SELL printing strictly below it, an ask only
    from a taker BUY printing strictly above it, up to the print's size and the order's remaining size."""
    if remaining <= 0 or trade_size <= 0:
        return 0.0
    if quote_side == 'bid' and trade_side == 'SELL' and trade_px < quote_px - 1e-9:
        return min(remaining, trade_size)
    if quote_side == 'ask' and trade_side == 'BUY' and trade_px > quote_px + 1e-9:
        return min(remaining, trade_size)
    return 0.0


# ------------------------------------------------------------------------------------------------- pure: Kalshi LIP

def lip_side_scores(levels, target, discount, tick=0.01):
    """Kalshi LIP raw scores for one side. `levels` is [(price, size)] best first (highest bid first). Walking from
    the best, levels count until cumulative size reaches `target` (the level that crosses it counts in full); the
    reference price is the first level where cumulative size reaches target/5; levels at or better than it score
    size x 1, worse levels size x discount^(ticks beyond the reference). Returns (scores per level, reached)."""
    out, cum, ref = [], 0.0, None
    for p, sz in levels:
        if cum >= target:
            out.append(0.0)
            continue
        cum += sz
        if ref is None and cum >= target / 5.0:
            ref = p
        out.append(None)
    reached = cum >= target
    if ref is None:
        ref = levels[-1][0] if levels else None
    res = []
    for (p, sz), o in zip(levels, out):
        if o is not None:
            res.append(0.0)
            continue
        ticks = max(0, int(round((ref - p) / tick))) if ref is not None else 0
        res.append(sz * (discount ** ticks))
    return res, reached


def lip_marginal_share(own_size, others_score_side, discount=1.0, ticks_beyond_ref=0):
    """Share of one side's normalised score from adding `own_size` at `ticks_beyond_ref` ticks beyond the
    reference price (0 = at or better than it)."""
    own = own_size * discount ** max(0, ticks_beyond_ref)
    return own / (own + others_score_side) if own > 0 else 0.0


# ------------------------------------------------------------------------------------------------- utilities

def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def jl(v, default=None):
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


def fee_category(tags, question=''):
    """The fee schedule's own category names (for the rebate share): crypto, sports, geopolitics or other."""
    labels = {str(t).strip().lower() for t in (tags or [])}
    if 'geopolitics' in labels:
        return 'geopolitics'
    cat = categorize(tags, question)
    if cat in ('crypto_updown', 'crypto_price'):
        return 'crypto'
    if cat == 'sports':
        return 'sports'
    return cat


def study_cat(tags, question=''):
    """Coarse study category for the variant grid."""
    labels = {str(t).strip().lower() for t in (tags or [])}
    cat = categorize(tags, question)
    if 'geopolitics' in labels:
        return 'politics'
    if cat in ('crypto_updown', 'crypto_price'):
        return 'crypto'
    if cat in ('elections', 'politics'):
        return 'politics'
    if cat == 'sports':
        return 'sports'
    if cat == 'economics':
        return 'economics'
    return 'other'


def paged_clob(http, path, params=None, max_pages=200):
    rows, cursor, pages = [], None, 0
    for _ in range(max_pages):
        q = dict(params or {})
        if cursor:
            q['next_cursor'] = cursor
        d = http.request(CLOB + path + ('?' + urllib.parse.urlencode(q) if q else ''))
        pages += 1
        if not isinstance(d, dict) or '__error__' in d:
            break
        rows.extend(d.get('data') or [])
        cursor = d.get('next_cursor')
        if not cursor or cursor == 'LTE=' or not d.get('data'):
            break
    return rows, pages


# ------------------------------------------------------------------------------------------------- collect: rewards

def collect_rewards(args):
    out = Path(args.out)
    raw = out / 'raw'
    http = Http(interval=args.interval)
    t0 = time.time()
    cur, p1 = paged_clob(http, '/rewards/markets/current')
    spons, p2 = paged_clob(http, '/rewards/markets/current', {'sponsored': 'true'})
    multi, p3 = paged_clob(http, '/rewards/markets/multi', {'page_size': 500})
    print('current %d (%d pages), sponsored %d, multi %d' % (len(cur), p1, len(spons), len(multi)), flush=True)
    stamp = int(t0)
    write_gz(raw / ('rewards_%d.json.gz' % stamp), {'at': now_iso(), 'current': cur, 'sponsored': spons,
                                                     'multi': multi})
    update_manifest(out, 'rewards_%d' % stamp, {'at': now_iso(), 'sources': [
        CLOB + '/rewards/markets/current', CLOB + '/rewards/markets/current?sponsored=true',
        CLOB + '/rewards/markets/multi'],
        'counts': {'current': len(cur), 'sponsored': len(spons), 'multi': len(multi)},
        'http': http.stats(), 'seconds': round(time.time() - t0, 1)})
    print('rewards saved: %s' % http.stats(), flush=True)


GKEEP = ['id', 'conditionId', 'question', 'slug', 'endDate', 'startDate', 'createdAt', 'negRisk', 'feesEnabled',
         'feeType', 'feeSchedule', 'holdingRewardsEnabled', 'rewardsMinSize', 'rewardsMaxSpread', 'clobRewards',
         'orderPriceMinTickSize', 'orderMinSize', 'volume24hr', 'volumeNum', 'liquidityNum', 'bestBid', 'bestAsk',
         'spread', 'competitive', 'gameStartTime', 'sportsMarketType', 'active', 'closed', 'acceptingOrders',
         'lastTradePrice', 'umaResolutionStatuses', 'outcomePrices', 'closedTime', 'groupItemTitle']


def compact_gamma(m):
    out = {k: m.get(k) for k in GKEEP}
    out['clobTokenIds'] = jl(m.get('clobTokenIds'), [])
    out['outcomes'] = jl(m.get('outcomes'), [])
    out['tags'] = [t.get('label') for t in (m.get('tags') or []) if isinstance(t, dict)]
    ev = (m.get('events') or [{}])[0] or {}
    out['event_id'], out['event_slug'], out['event_title'] = ev.get('id'), ev.get('slug'), ev.get('title')
    return out


def collect_gamma_fill(args):
    """Second pass: rewarded markets the active scan did not reach (it is capped by --max-pages), by condition id."""
    out = Path(args.out)
    gp = out / 'raw' / 'gamma_active.json.gz'
    g = read_gz(gp)
    have = {m.get('conditionId') for m in g['markets']}
    r = read_gz(latest(out, 'rewards_*.json.gz'))
    miss = sorted({x['condition_id'] for x in r['current']} - have)
    http = Http(interval=args.interval)
    t0, added = time.time(), 0
    for i in range(0, len(miss), 40):
        q = [('condition_ids', c) for c in miss[i:i + 40]] + [('include_tag', 'true'), ('limit', 100)]
        d = http.request(GAMMA + '/markets?' + urllib.parse.urlencode(q))
        if isinstance(d, list):
            for m in d:
                g['markets'].append(compact_gamma(m))
                added += 1
    g['filled'] = {'at': now_iso(), 'missing': len(miss), 'added': added}
    write_gz(gp, g)
    update_manifest(out, 'gamma_fill', {'at': now_iso(), 'source': GAMMA + '/markets?condition_ids=',
                                        'missing': len(miss), 'added': added, 'http': http.stats(),
                                        'seconds': round(time.time() - t0, 1)})
    print('gamma fill: %d missing, %d added %s' % (len(miss), added, http.stats()), flush=True)


def collect_gamma(args):
    """Every active market from gamma's keyset endpoint (offset paging stops near 2,000 rows), compacted: tags,
    fee schedule, the holdingRewardsEnabled flag and the reward fields. One pass serves the budget table's
    categories, the fee/rebate rates of the simulated markets and the holding-reward set."""
    out = Path(args.out)
    http = Http(interval=args.interval)
    t0 = time.time()
    rows, cursor, n, pages = [], None, 0, 0
    for _ in range(args.max_pages):
        q = {'limit': 100, 'closed': 'false', 'active': 'true', 'include_tag': 'true'}
        if cursor:
            q['after_cursor'] = cursor
        d = http.request(GAMMA + '/markets/keyset?' + urllib.parse.urlencode(q))
        pages += 1
        if not isinstance(d, dict) or '__error__' in d:
            print('  stop:', str(d)[:200], flush=True)
            break
        ms = d.get('markets') or []
        n += len(ms)
        rows.extend(compact_gamma(m) for m in ms)
        cursor = d.get('next_cursor')
        if pages % 100 == 0:
            print('  pages %d markets %d' % (pages, n), flush=True)
        if not cursor or not ms:
            break
    nh = sum(1 for r in rows if r.get('holdingRewardsEnabled'))
    write_gz(Path(out) / 'raw' / 'gamma_active.json.gz', {'at': now_iso(), 'active_scanned': n, 'pages': pages,
                                                        'complete': not cursor, 'markets': rows})
    update_manifest(out, 'gamma_scan', {'at': now_iso(), 'source': GAMMA + '/markets/keyset (active, all pages)',
                                        'active_scanned': n, 'pages': pages, 'holding_markets': nh,
                                        'complete': not cursor, 'http': http.stats(),
                                        'seconds': round(time.time() - t0, 1)})
    print('gamma: %d active markets, %d with holding rewards, %s' % (n, nh, http.stats()), flush=True)


def latest(out, pattern):
    ps = sorted((Path(out) / 'raw').glob(pattern))
    return ps[-1] if ps else None


def rewarded_markets(out):
    """Merge the latest reward pull into one row per condition id: config, tokens, prices, gamma metadata."""
    p = latest(out, 'rewards_*.json.gz')
    r = read_gz(p)
    gp = Path(out) / 'raw' / 'gamma_active.json.gz'
    gam = {m.get('conditionId'): m for m in read_gz(gp)['markets']} if gp.exists() else {}
    spons = {x['condition_id']: x for x in r['sponsored']}
    multi = {x['condition_id']: x for x in r['multi']}
    rows = {}
    for x in r['current']:
        cid = x['condition_id']
        g = gam.get(cid) or {}
        mu = multi.get(cid) or {}
        sp = spons.get(cid) or {}
        native = fnum(x.get('native_daily_rate'), None)
        if native is None:
            native = sum(fnum(c.get('rate_per_day'), 0.0) for c in x.get('rewards_config') or [])
        total = native + (fnum(sp.get('sponsored_daily_rate'), 0.0) or 0.0)
        toks = g.get('clobTokenIds') or [t.get('token_id') for t in mu.get('tokens') or []]
        rows[cid] = {'cid': cid, 'native_rate': native, 'sponsored_rate': fnum(sp.get('sponsored_daily_rate'), 0.0),
                     'rate': total, 'v': fnum(x.get('rewards_max_spread'), 0.0),
                     'min_size': fnum(x.get('rewards_min_size'), 0.0),
                     'start': min((c.get('start_date') or '9999') for c in x.get('rewards_config') or [{}]),
                     'tokens': toks, 'question': g.get('question') or mu.get('question'),
                     'tags': g.get('tags') or [], 'cat': study_cat(g.get('tags'), g.get('question') or ''),
                     'fee_cat': fee_category(g.get('tags'), g.get('question') or ''),
                     'fee_rate': fee_rate_from_gamma(g), 'neg_risk': g.get('negRisk'),
                     'holding': bool(g.get('holdingRewardsEnabled')), 'end': g.get('endDate') or mu.get('end_date'),
                     'tick': fnum(g.get('orderPriceMinTickSize'), 0.01), 'volume24hr': fnum(mu.get('volume_24hr'),
                                                                                               fnum(g.get('volume24hr'))),
                     'competitiveness': fnum(mu.get('market_competitiveness')), 'event_id': g.get('event_id'),
                     'event_title': g.get('event_title'), 'game_start': g.get('gameStartTime'),
                     'market_id': g.get('id') or mu.get('market_id'), 'in_gamma': bool(g),
                     'accepting': g.get('acceptingOrders'), 'created': g.get('createdAt')}
    return rows, r['at']


def fee_rate_from_gamma(g):
    fs = g.get('feeSchedule') or {}
    if g.get('feesEnabled') is False:
        return 0.0
    r = fnum(fs.get('rate'))
    if r is not None:
        return r
    return fee_rate(categorize(g.get('tags'), g.get('question') or ''), g.get('tags'))


# ------------------------------------------------------------------------------------------------- collect: books

def collect_books(args):
    out = Path(args.out)
    rows, _ = rewarded_markets(out)
    http = Http(interval=args.interval)
    toks = [(cid, r['tokens'][0]) for cid, r in rows.items() if r['tokens'] and r['rate'] > 0]
    t0 = time.time()
    books = {}
    for i in range(0, len(toks), args.batch):
        chunk = toks[i:i + args.batch]
        d = http.request(CLOB + '/books', body=[{'token_id': t} for _, t in chunk])
        if isinstance(d, dict) and '__error__' in d:
            continue
        got = time.time()
        for b in d or []:
            bids = sorted(((float(x['price']), float(x['size'])) for x in b.get('bids') or []), reverse=True)
            asks = sorted((float(x['price']), float(x['size'])) for x in b.get('asks') or [])
            if bids and asks:
                lo, hi = bids[0][0] - 0.20, asks[0][0] + 0.20
                bids = [x for x in bids if x[0] >= lo]
                asks = [x for x in asks if x[0] <= hi]
            books[b.get('asset_id')] = {'t': got, 'bids': bids, 'asks': asks, 'tick': fnum(b.get('tick_size')),
                                        'min_order': fnum(b.get('min_order_size')), 'ts': b.get('timestamp')}
    stamp = int(t0)
    write_gz(out / 'raw' / 'books' / ('snap_%d.json.gz' % stamp), {'at': now_iso(), 't0': t0, 't1': time.time(),
                                                                  'books': books})
    update_manifest(out, 'books_%d' % stamp, {'at': now_iso(), 'source': CLOB + '/books (POST, YES tokens)',
                                              'tokens': len(toks), 'books': len(books), 'http': http.stats(),
                                              'seconds': round(time.time() - t0, 1)})
    print('books %d/%d in %.0fs %s' % (len(books), len(toks), time.time() - t0, http.stats()), flush=True)


# ------------------------------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('what', choices=['rewards', 'gamma', 'gamma-fill', 'books', 'trades', 'chain', 'kalshi',
                                    'kalshi-books', 'kalshi-trades'])
    c.add_argument('--out', default=str(OUT))
    c.add_argument('--interval', type=float, default=0.25)
    c.add_argument('--batch', type=int, default=500)
    c.add_argument('--max-pages', type=int, default=2000)
    c.add_argument('--n', type=int, default=200)
    c.add_argument('--days', type=float, default=14.0)
    a = sub.add_parser('analyze')
    a.add_argument('--out', default=str(OUT))
    a.add_argument('--skip-fav', action='store_true')
    r = sub.add_parser('render')
    r.add_argument('--out', default=str(OUT))
    args = ap.parse_args()
    Path(args.out).mkdir(parents=True, exist_ok=True)
    if args.cmd == 'collect':
        {'rewards': collect_rewards, 'gamma': collect_gamma, 'gamma-fill': collect_gamma_fill, 'books': collect_books,
         'trades': collect_trades, 'chain': collect_chain, 'kalshi': collect_kalshi,
         'kalshi-books': collect_kalshi_books, 'kalshi-trades': collect_kalshi_trades}[args.what](args)
    elif args.cmd == 'analyze':
        cmd_analyze(args)
    else:
        cmd_render(args)


RATE_BUCKETS = [(1e-9, 5, '$0-5'), (5, 50, '$5-50'), (50, 500, '$50-500'), (500, 1e12, '$500+')]
CATS = ['sports', 'politics', 'crypto', 'economics', 'other']


def rate_bucket(rate):
    for lo, hi, name in RATE_BUCKETS:
        if lo <= rate < hi:
            return name
    return None


def trade_sample(rows, now, per_stratum=12, min_age_days=3.0):
    """The simulated set, fixed before any return is computed: rewarded, binary, accepting orders, listed at least
    `min_age_days` ago and not ending within a day; up to `per_stratum` per (category, $/day bucket), drawn by a
    hash of the condition id."""
    strata = collections.defaultdict(list)
    for cid, r in rows.items():
        if r['rate'] <= 0 or len(r['tokens']) != 2 or not r['in_gamma'] or r.get('accepting') is False:
            continue
        created = parse_ts(r.get('created'))
        end = parse_ts(r.get('end'))
        if created is None or now - created < min_age_days * DAY or (end is not None and end < now + DAY):
            continue
        strata[(r['cat'], rate_bucket(r['rate']))].append(cid)
    pick = {}
    for key, cids in strata.items():
        for cid in sorted(cids, key=stable_u)[:per_stratum]:
            pick[cid] = '%s|%s' % key
    return pick, {('%s|%s' % k): len(v) for k, v in strata.items()}


def collect_trades(args):
    out = Path(args.out)
    rows, at = rewarded_markets(out)
    now = time.time()
    pick, strata_n = trade_sample(rows, now, per_stratum=args.n)
    http = Http(interval=args.interval)
    t0 = time.time()
    since = now - args.days * DAY
    done = 0
    for cid, stratum in sorted(pick.items(), key=lambda kv: stable_u(kv[0])):
        path = out / 'raw' / 'trades' / ('%s.json.gz' % cid[:18])
        if path.exists():
            continue
        r = rows[cid]
        trades, cursor, pages, complete = [], None, 0, False
        while pages < args.max_pages:
            q = {'condition': cid, 'limit': 1000}
            if cursor:
                q['cursor'] = cursor
            d = http.request(DATA + '/v2/trades?' + urllib.parse.urlencode(q))
            pages += 1
            if not isinstance(d, dict) or '__error__' in d:
                break
            for x in d.get('data') or []:
                trades.append([int(x['timestamp']), int(x.get('outcome_index') or 0), x.get('side'),
                               float(x['price']), float(x['size']), (x.get('transaction_hash') or '')[:12]])
            cursor = (d.get('pagination') or {}).get('next_cursor')
            if not d.get('data') or not cursor or not (d.get('pagination') or {}).get('has_more'):
                complete = True
                break
            if trades and trades[-1][0] < since:
                complete = True
                break
        ph = http.request(CLOB + '/prices-history?' + urllib.parse.urlencode(
            {'market': r['tokens'][0], 'startTs': int(since), 'endTs': int(now), 'fidelity': 60}))
        prices = [[int(x['t']), float(x['p'])] for x in (ph.get('history') or [])] if isinstance(ph, dict) else []
        write_gz(path, {'cid': cid, 'stratum': stratum, 'at': now_iso(), 'since': since, 'until': now,
                        'pages': pages, 'complete': complete, 'trades': trades, 'prices': prices})
        done += 1
        if done % 20 == 0:
            print('  trades %d/%d %s %.0fs' % (done, len(pick), http.stats(), time.time() - t0), flush=True)
    update_manifest(out, 'trades', {'at': now_iso(), 'source': DATA + '/v2/trades?condition= (taker rows), ' + CLOB +
                                    '/prices-history (hourly)', 'rewards_snapshot': at, 'markets': len(pick),
                                    'strata_population': strata_n, 'days': args.days, 'max_pages': args.max_pages,
                                    'http': http.stats(), 'seconds': round(time.time() - t0, 1)})
    print('trades done: %d markets %s' % (len(pick), http.stats()), flush=True)


LIQ_PAYER = '0x2c2795ea295d5eb51f9121b728ed2ea4e936a709'     # sender of the 00:00-00:05 UTC pUSD batches (found from
#                                                            REWARD activity tx 0x8e5b8337..., 2026-10-14)
OTHER_PAYER = '0xdd8db71ce3be8d71ff148b2163d64da181a29e8b'   # smart account paying small pUSD amounts through the day


def transfer_logs(rpc, token, sender, b0, b1, step=9999):
    from onchain_probe import hx
    topic = '0x' + '0' * 24 + sender[2:].lower()
    rows, s = [], b0
    while s <= b1:
        e = min(b1, s + step)
        r = rpc_retry(rpc, 'eth_getLogs', [{'address': token, 'fromBlock': hex(s), 'toBlock': hex(e),
                                            'topics': [TRANSFER_TOPIC, topic]}])
        for lg in r or []:
            rows.append([hx(lg['blockNumber']), '0x' + lg['topics'][2][-40:], int(lg['data'], 16) / 1e6])
        s = e + 1
    return rows


def rpc_retry(rpc, method, params, tries=6):
    """One call retried through Infura's transient -32603 "precondition failure"."""
    last = None
    for k in range(tries):
        try:
            return rpc.call('polygon', method, params)
        except Exception as e:  # noqa: BLE001 - logged by RPC; retried here
            last = e
            time.sleep(1.0 + k)
    raise last


def safe_batch(rpc, calls, chunk=15, tries=6):
    """rpc.batch in small chunks, retried with backoff through Infura's "Too Many Requests" and transient -32603
    errors (the key is shared with other workers); failed members come back as None."""
    out = []
    for i in range(0, len(calls), chunk):
        part = calls[i:i + chunk]
        res = None
        for k in range(tries):
            try:
                res = rpc.batch('polygon', part, allow_errors=True)
                break
            except Exception:  # noqa: BLE001 - logged by RPC; retried here
                time.sleep(3.0 * (k + 1))
        if res is None:
            res = [None] * len(part)
        out.extend(None if (isinstance(x, dict) and 'error' in x and 'timestamp' not in x) else x for x in res)
        time.sleep(0.5)
    return out


def blocks_at(rpc, targets, anchor_block, anchor_ts, rounds=4):
    """Approximate first blocks at several timestamps at once: secant steps from an anchor, each round a few small
    batched eth_getBlockByNumber calls. Accurate to seconds; the padded windows absorb the rest."""
    from onchain_probe import hx
    est = {t: int(anchor_block + (t - anchor_ts) / 1.5) for t in targets}
    for _ in range(rounds):
        items = list(est.items())
        res = safe_batch(rpc, [('eth_getBlockByNumber', [hex(b), False]) for _, b in items])
        done = True
        for (t, b), blk in zip(items, res):
            if not isinstance(blk, dict) or 'timestamp' not in blk:
                done = False
                continue
            d = t - hx(blk['timestamp'])
            if abs(d) > 6:
                done = False
                est[t] = int(b + d / 1.5)
        if done:
            break
    return est


def collect_chain(args):
    """Daily liquidity-reward payouts: the payer's pUSD and USDC.e transfers in a padded window around 00:00 UTC
    (23:30-01:30), for the last `--days` days; a day with nothing in the window is rescanned over the whole day."""
    from onchain_probe import RPC, hx
    out = Path(args.out)
    rpc = RPC(out / 'raw' / 'rpc', max_credits=600000)
    t0 = time.time()
    head = rpc_retry(rpc, 'eth_getBlockByNumber', ['latest', False])
    hb, hts = hx(head['number']), hx(head['timestamp'])
    today = int(hts // DAY) * DAY
    d0s = [today - k * DAY for k in range(int(args.days), -1, -1)]
    targets = sorted({t for d0 in d0s for t in (d0 - 1800, d0 + 5400, d0 + DAY - 1800) if t < hts})
    est = blocks_at(rpc, targets, hb, hts)
    print('block estimates done (%d targets) %.0fs' % (len(targets), time.time() - t0), flush=True)
    days = []
    for d0 in d0s:
        b_lo = est[d0 - 1800]
        b_hi = est.get(d0 + 5400, hb)
        rec = {'day': dt.datetime.fromtimestamp(d0, dt.timezone.utc).date().isoformat(), 'b_lo': b_lo, 'b_hi': b_hi,
               'window': '23:30-01:30 UTC'}
        if b_hi - b_lo > 30000:   # an unconverged estimate; fall back to a 1.5 s/block window
            b_lo, b_hi = b_hi - 4800, b_hi
            rec['b_lo'], rec['window'] = b_lo, '~2h before the 01:30 estimate'
        for name, tok in (('pusd', PUSD), ('usdce', USDCE)):
            rec[name] = transfer_logs(rpc, tok, LIQ_PAYER, b_lo, b_hi)
        if not rec['pusd'] and not rec['usdce'] and d0 + 5400 < hts:
            b_day = est.get(d0 + DAY - 1800, hb)
            rec['window'] = 'full day'
            for name, tok in (('pusd', PUSD), ('usdce', USDCE)):
                rec[name] = transfer_logs(rpc, tok, LIQ_PAYER, b_lo, b_day)
        tot = sum(x[2] for x in rec['pusd']) + sum(x[2] for x in rec['usdce'])
        print('%s %s transfers %d+%d total %.0f' % (rec['day'], rec['window'], len(rec['pusd']), len(rec['usdce']),
                                                    tot), flush=True)
        days.append(rec)
    write_gz(out / 'raw' / 'chain_payouts.json.gz', {'at': now_iso(), 'payer': LIQ_PAYER, 'days': days,
                                                    'other_payer': OTHER_PAYER, 'other_days': []})
    rows_other = []
    try:
        for d0 in d0s[-4:-1]:
            b_lo, b_hi = est[d0 - 1800], est.get(d0 + DAY - 1800, hb)
            rows_other.append({'day': dt.datetime.fromtimestamp(d0, dt.timezone.utc).date().isoformat(),
                               'pusd': transfer_logs(rpc, PUSD, OTHER_PAYER, b_lo, b_hi)})
    except Exception as e:  # noqa: BLE001 - context only; the daily payouts are already saved
        print('other payer skipped: %r' % e, flush=True)
    write_gz(out / 'raw' / 'chain_payouts.json.gz', {'at': now_iso(), 'payer': LIQ_PAYER, 'days': days,
                                                    'other_payer': OTHER_PAYER, 'other_days': rows_other})
    update_manifest(out, 'chain', {'at': now_iso(), 'source': 'Polygon via Infura (onchain_probe.RPC): eth_getLogs '
                                   'Transfer(from=payer) on pUSD and USDC.e', 'payer': LIQ_PAYER,
                                   'days': len(days), 'credits_estimated': rpc.credits,
                                   'seconds': round(time.time() - t0, 1)})
    print('chain done: %d days, credits %d, %.0fs' % (len(days), rpc.credits, time.time() - t0), flush=True)


def kalshi_programs(status, kind='liquidity', max_pages=20):
    rows, cursor = [], None
    for _ in range(max_pages):
        q = {'status': status, 'type': kind, 'limit': 10000}
        if cursor:
            q['cursor'] = cursor
        d = http_json(KALSHI + 'incentive_programs?' + urllib.parse.urlencode(q), 'kalshi')
        if not d:
            break
        rows.extend(d.get('incentive_programs') or [])
        cursor = d.get('next_cursor')
        if not cursor:
            break
    return rows


def kalshi_book_levels(ob):
    """Kalshi orderbook JSON -> (yes_bids, no_bids), each [(price, size)] best (highest) first."""
    book = ob.get('orderbook_fp') or ob.get('orderbook') or {}

    def levels(kd, kc):
        if book.get(kd) is not None:
            v = [(float(p), float(sz)) for p, sz in book[kd]]
        elif book.get(kc) is not None:
            v = [(int(p) / 100.0, float(sz)) for p, sz in book[kc]]
        else:
            v = []
        return sorted((x for x in v if x[1] > 0), key=lambda x: -x[0])
    return levels('yes_dollars', 'yes'), levels('no_dollars', 'no')


def collect_kalshi_books(args):
    """Re-read the books of the sampled LIP markets whose program period is at least ~a day (the slow ones), so
    competition is a sample of several reads rather than one."""
    out = Path(args.out)
    d = read_gz(out / 'raw' / 'kalshi_lip.json.gz')
    act = {p['id']: p for p in d['active']}
    tick = []
    for pid in d['sample']:
        p = act.get(pid)
        if not p:
            continue
        L = (parse_ts(p['end_date']) - parse_ts(p['start_date'])) / DAY
        if L >= 0.9 and parse_ts(p['end_date']) > time.time() + 600:
            tick.append(p['market_ticker'])
    t0 = time.time()
    books = {}
    for t in tick:
        ob = http_json(KALSHI + 'markets/%s/orderbook' % t, 'kalshi')
        if ob is None:
            continue
        yb, nb = kalshi_book_levels(ob)
        books[t] = {'t': time.time(), 'yes_bids': yb, 'no_bids': nb}
    stamp = int(t0)
    write_gz(out / 'raw' / ('kalshi_books_%d.json.gz' % stamp), {'at': now_iso(), 'books': books})
    update_manifest(out, 'kalshi_books_%d' % stamp, {'at': now_iso(), 'source': KALSHI + 'markets/{t}/orderbook',
                                                    'tickers': len(tick), 'books': len(books),
                                                    'seconds': round(time.time() - t0, 1)})
    print('kalshi books %d/%d in %.0fs' % (len(books), len(tick), time.time() - t0), flush=True)


def collect_kalshi_trades(args):
    """Trades and hourly candles (best bid/ask) for the sampled slow LIP markets over the last --days days."""
    out = Path(args.out)
    d = read_gz(out / 'raw' / 'kalshi_lip.json.gz')
    act = {p['id']: p for p in d['active']}
    now = time.time()
    since = int(now - args.days * DAY)
    t0 = time.time()
    res = {}
    for pid in d['sample']:
        p = act.get(pid)
        if not p:
            continue
        L = (parse_ts(p['end_date']) - parse_ts(p['start_date'])) / DAY
        t = p['market_ticker']
        b = d['books'].get(t) or {}
        if L < 0.9 or not b.get('event_ticker'):
            continue
        trades, cursor = [], None
        for _ in range(args.max_pages if args.max_pages < 2000 else 20):
            q = {'ticker': t, 'min_ts': since, 'limit': 1000}
            if cursor:
                q['cursor'] = cursor
            r = http_json(KALSHI + 'markets/trades?' + urllib.parse.urlencode(q), 'kalshi')
            if not r:
                break
            for x in r.get('trades') or []:
                trades.append([parse_ts(x['created_time']), fnum(x.get('yes_price_dollars')), x.get('taker_side'),
                               fnum(x.get('count_fp'), 0.0)])
            cursor = r.get('cursor')
            if not cursor or not r.get('trades'):
                break
        series = b['event_ticker'].split('-')[0]
        c = http_json(KALSHI + 'series/%s/markets/%s/candlesticks?%s' % (series, t, urllib.parse.urlencode(
            {'start_ts': since, 'end_ts': int(now), 'period_interval': 60})), 'kalshi')
        candles = []
        for x in (c or {}).get('candlesticks') or []:
            candles.append([x['end_period_ts'], fnum((x.get('yes_bid') or {}).get('close_dollars')),
                            fnum((x.get('yes_ask') or {}).get('close_dollars'))])
        res[t] = {'program': pid, 'trades': trades, 'candles': candles}
    write_gz(out / 'raw' / 'kalshi_trades.json.gz', {'at': now_iso(), 'since': since, 'until': now, 'markets': res})
    update_manifest(out, 'kalshi_trades', {'at': now_iso(), 'source': KALSHI + 'markets/trades, series/{s}/markets/'
                                           '{t}/candlesticks (60m)', 'markets': len(res), 'days': args.days,
                                           'seconds': round(time.time() - t0, 1)})
    print('kalshi trades: %d markets in %.0fs' % (len(res), time.time() - t0), flush=True)


def collect_kalshi(args):
    out = Path(args.out)
    t0 = time.time()
    active = kalshi_programs('active')
    upcoming = kalshi_programs('upcoming', max_pages=5)
    paid = kalshi_programs('paid_out', max_pages=args.max_pages if args.max_pages < 2000 else 30)
    print('kalshi programs: active %d upcoming %d paid_out %d' % (len(active), len(upcoming), len(paid)), flush=True)
    now = time.time()
    rows = []
    for p in active:
        st, en = parse_ts(p.get('start_date')), parse_ts(p.get('end_date'))
        if not st or not en or en <= now:
            continue
        days = max(1.0 / 96, (en - st) / DAY)
        rows.append((p['period_reward'] / 1e4 / days, p))
    rows.sort(key=lambda x: -x[0])
    # stratified sample: every program above $200/day, then hash-sampled programs per $/day bucket
    buckets = collections.defaultdict(list)
    for usd_day, p in rows:
        b = 'a>=200' if usd_day >= 200 else 'b50-200' if usd_day >= 50 else 'c10-50' if usd_day >= 10 else 'd<10'
        buckets[b].append(p)
    pick = []
    for b, ps in sorted(buckets.items()):
        ps = sorted(ps, key=lambda p: stable_u(p['id']))
        pick.extend(ps[:max(1, args.n // 4)])
    books = {}
    for p in pick:
        t = p['market_ticker']
        ob = http_json(KALSHI + 'markets/%s/orderbook' % t, 'kalshi')
        mk = http_json(KALSHI + 'markets/%s' % t, 'kalshi')
        if ob is None:
            continue
        yb, nb = kalshi_book_levels(ob)
        m = (mk or {}).get('market') or {}
        books[t] = {'t': time.time(), 'yes_bids': yb, 'no_bids': nb, 'event_ticker': m.get('event_ticker'),
                    'status': m.get('status'), 'volume_24h': fnum(m.get('volume_24h_fp') or m.get('volume_24h')),
                    'tick': fnum(m.get('tick_size'), 1) / 100.0 if m.get('tick_size') else 0.01,
                    'close_time': m.get('close_time'), 'title': m.get('title'),
                    'price_ranges': m.get('price_ranges')}
    series = {}
    for t in sorted({(b.get('event_ticker') or '').split('-')[0] for b in books.values() if b.get('event_ticker')}):
        d = http_json(KALSHI + 'series/%s' % t, 'kalshi')
        if d and d.get('series'):
            sr = d['series']
            series[t] = {k: sr.get(k) for k in ('ticker', 'title', 'category', 'fee_type', 'fee_multiplier',
                                                 'frequency')}
    write_gz(out / 'raw' / 'kalshi_lip.json.gz', {'at': now_iso(), 'active': active, 'upcoming': upcoming,
                                                 'paid_out': paid, 'sample': [p['id'] for p in pick],
                                                 'books': books, 'series': series})
    update_manifest(out, 'kalshi', {'at': now_iso(), 'source': KALSHI + 'incentive_programs, markets/{t}/orderbook, '
                                    'markets/{t}, series/{s}', 'active': len(active), 'paid_out': len(paid),
                                    'sampled_books': len(books), 'series': len(series),
                                    'seconds': round(time.time() - t0, 1)})
    print('kalshi done: %d books, %d series, %.0fs' % (len(books), len(series), time.time() - t0), flush=True)


# ------------------------------------------------------------------------------------------------- analysis: budgets

def pctl(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    f = int(math.floor(k))
    c = min(len(xs) - 1, f + 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def analyze_budgets(rows):
    by_cat = collections.defaultdict(lambda: {'markets': 0, 'usd_day': 0.0, 'sponsored_usd_day': 0.0})
    by_bucket = collections.defaultdict(lambda: {'markets': 0, 'usd_day': 0.0})
    rates = []
    for r in rows.values():
        c = by_cat[r['cat'] if r['in_gamma'] else 'unmatched']
        c['markets'] += 1
        c['usd_day'] += r['rate']
        c['sponsored_usd_day'] += r['sponsored_rate'] or 0.0
        b = by_bucket[rate_bucket(r['rate']) or 'zero']
        b['markets'] += 1
        b['usd_day'] += r['rate']
        rates.append(r['rate'])
    tot = sum(rates)
    top = sorted(rows.values(), key=lambda r: -r['rate'])[:25]
    srt = sorted(rates, reverse=True)
    cum, n50, n90 = 0.0, None, None
    for i, x in enumerate(srt):
        cum += x
        if n50 is None and cum >= 0.5 * tot:
            n50 = i + 1
        if n90 is None and cum >= 0.9 * tot:
            n90 = i + 1
    return {'markets': len(rows), 'usd_day_total': tot, 'usd_year_total': tot * 365,
            'sponsored_usd_day': sum(r['sponsored_rate'] or 0.0 for r in rows.values()),
            'by_category': dict(by_cat), 'by_rate_bucket': dict(by_bucket),
            'per_market': {'p10': pctl(rates, 0.1), 'median': pctl(rates, 0.5), 'p90': pctl(rates, 0.9),
                           'p99': pctl(rates, 0.99), 'max': max(rates) if rates else None,
                           'markets_for_half_of_budget': n50, 'markets_for_90pct_of_budget': n90},
            'max_spread_cents': {'median': pctl([r['v'] for r in rows.values()], 0.5),
                                 'p10': pctl([r['v'] for r in rows.values()], 0.1),
                                 'p90': pctl([r['v'] for r in rows.values()], 0.9)},
            'min_size_shares': {'median': pctl([r['min_size'] for r in rows.values()], 0.5),
                                'p90': pctl([r['min_size'] for r in rows.values()], 0.9)},
            'holding_enabled_markets_rewarded': sum(1 for r in rows.values() if r['holding']),
            'top': [{'q': r['question'], 'rate': r['rate'], 'v': r['v'], 'min_size': r['min_size'], 'cat': r['cat'],
                     'volume24hr': r['volume24hr'], 'end': r['end']} for r in top]}


# ------------------------------------------------------------------------------------------------- analysis: books

S_GRID_FRAC = [0.0, 1.0 / 3.0, 2.0 / 3.0]     # quote distance as a fraction of the max spread v (0 = at the touch)


def market_competition(r, book):
    """Score the liquidity already resting in one rewarded market's YES book (both sides), at its adjusted
    midpoint, and the bounds on the competitors' summed Q_min."""
    bids, asks = book.get('bids') or [], book.get('asks') or []
    if not bids or not asks or not r['v'] or r['v'] <= 0:
        return None
    mid = adjusted_mid(bids, asks, r['min_size'])
    if mid is None:
        return None
    q1, q2 = side_scores(bids, asks, mid, r['v'], r['min_size'])
    cb = competitor_bounds(q1, q2, mid)
    return {'mid': mid, 'raw_mid': (bids[0][0] + asks[0][0]) / 2.0, 'best_bid': bids[0][0], 'best_ask': asks[0][0],
            'q1': q1, 'q2': q2, 'comp_upper': cb['upper'], 'comp_lower': cb['lower'],
            'two_sided': q1 > 0 and q2 > 0, 'hs_cents': (asks[0][0] - bids[0][0]) * 50.0,
            'tick': book.get('tick') or r['tick'] or 0.01}


def our_quote(r, comp, frac, q_shares):
    """Our two-sided quote of q_shares at distance frac x v from the adjusted midpoint (post-only, on the tick
    grid): its reward per day against the conservative (upper) and optimistic (lower) competitor bounds, and the
    capital it locks."""
    v = r['v']
    tick = comp['tick']
    s_target = frac * v
    bid, ask = quote_prices(comp['mid'], s_target, tick, comp['best_bid'], comp['best_ask'])
    if frac == 0.0:   # at the touch: join the best bid/ask (never improve, never cross)
        bid, ask = comp['best_bid'], comp['best_ask']
    sb, sa = (comp['mid'] - bid) * 100.0, (ask - comp['mid']) * 100.0
    q1, q2 = order_score(v, sb) * q_shares, order_score(v, sa) * q_shares
    ours = q_min(q1, q2, comp['mid'])
    cap = quote_capital(q_shares, bid, ask)
    return {'bid': bid, 'ask': ask, 's_bid': sb, 's_ask': sa, 'ours': ours, 'capital': cap,
            'usd_day_cons': r['rate'] * reward_share(ours, comp['comp_upper']),
            'usd_day_opt': r['rate'] * reward_share(ours, comp['comp_lower'])}


def load_snaps(out):
    return [read_gz(p) for p in sorted((Path(out) / 'raw' / 'books').glob('snap_*.json.gz'))]


def analyze_books(rows, snaps, ref_capital=1000.0):
    """Per market and snapshot: competition and our reward yield at $ref_capital two-sided, three distances.
    Then a greedy allocation of capital across markets by marginal reward per dollar (conservative bound),
    averaged over snapshots, which is the rent curve before adverse selection."""
    per = collections.defaultdict(list)
    for sn in snaps:
        for cid, r in rows.items():
            if not r['tokens']:
                continue
            b = sn['books'].get(r['tokens'][0])
            if not b:
                continue
            comp = market_competition(r, b)
            if comp is None:
                continue
            q_sh = max(r['min_size'], ref_capital)   # ~$1 of capital per two-sided share
            quotes = {}
            for f in S_GRID_FRAC:
                qq = our_quote(r, comp, f, q_sh)
                quotes['%.2f' % f] = qq
            per[cid].append({'at': sn['at'], 'comp': comp, 'quotes': quotes})
    # per-market averages
    mk = {}
    for cid, obs in per.items():
        r = rows[cid]
        best = {}
        for f in S_GRID_FRAC:
            k = '%.2f' % f
            cons = statistics.mean(o['quotes'][k]['usd_day_cons'] for o in obs)
            opt = statistics.mean(o['quotes'][k]['usd_day_opt'] for o in obs)
            cap = statistics.mean(o['quotes'][k]['capital'] for o in obs)
            best[k] = {'usd_day_cons': cons, 'usd_day_opt': opt, 'capital': cap,
                       'apr_cons': cons * 365 / cap if cap > 0 else None,
                       'apr_opt': opt * 365 / cap if cap > 0 else None}
        mk[cid] = {'cat': r['cat'], 'rate': r['rate'], 'v': r['v'], 'min_size': r['min_size'], 'n_snap': len(obs),
                   'mid': statistics.mean(o['comp']['mid'] for o in obs),
                   'comp_upper': statistics.mean(o['comp']['comp_upper'] for o in obs),
                   'comp_lower': statistics.mean(o['comp']['comp_lower'] for o in obs),
                   # central: midpoint of the bounds where single-sided liquidity can score (mid in [0.10, 0.90]),
                   # the balanced (upper) bound outside it, where only two-sided liquidity scores
                   'comp_central': statistics.mean(
                       (o['comp']['comp_upper'] + o['comp']['comp_lower']) / 2.0 if 0.10 <= o['comp']['mid'] <= 0.90
                       else o['comp']['comp_upper'] for o in obs),
                   'comp_cv': (statistics.pstdev([o['comp']['comp_upper'] for o in obs]) /
                               max(1e-9, statistics.mean(o['comp']['comp_upper'] for o in obs))) if len(obs) > 1 else None,
                   'empty_share': sum(1 for o in obs if o['comp']['comp_upper'] <= 0) / len(obs),
                   'joinable_share': sum(1 for o in obs if o['comp']['two_sided']) / len(obs),
                   'hs_cents': statistics.median(o['comp']['hs_cents'] for o in obs),
                   'quotes': best, 'holding': r['holding'], 'volume24hr': r['volume24hr']}
    return mk


JOIN_MIN = 0.5    # a market is joinable when others quote both sides inside the reward band in >= half the snapshots


def greedy_allocation(mk, rows, frac_key, budgets=(1e4, 1e5, 1e6, 1e7), step=500.0, bound='comp_upper',
                      joinable_only=True):
    """Allocate capital in `step` dollars to the market with the highest marginal reward per dollar at distance
    frac x v (reward_i(Q) = rate x S Q / (S Q + C)), the first allocation in a market at least its min size.
    Returns, per budget, $/day of rewards (before adverse selection), APR and markets used."""
    import heapq
    f = float(frac_key)
    state = {}
    heap = []
    for cid, m in mk.items():
        r = rows[cid]
        if joinable_only and m['joinable_share'] < JOIN_MIN:
            continue
        C = m[bound]
        sv = order_score(r['v'], max(f * r['v'], m['hs_cents']))
        if sv <= 0 or r['rate'] <= 0:
            continue
        q0 = max(r['min_size'], step)

        def rew(q, C=C, sv=sv, rate=r['rate']):
            return rate * sv * q / (sv * q + C) if q > 0 else 0.0
        state[cid] = {'q': 0.0, 'rew': rew, 'q0': q0}
        gain = rew(q0) / q0
        heapq.heappush(heap, (-gain, cid))
    out, spent, total, used = {}, 0.0, 0.0, set()
    targets = sorted(budgets)
    ti = 0
    while heap and ti < len(targets):
        g, cid = heapq.heappop(heap)
        st = state[cid]
        inc = st['q0'] if st['q'] == 0 else step
        if spent + inc > targets[ti]:
            out[targets[ti]] = {'usd_day': total, 'apr': total * 365 / spent if spent else None,
                                'markets': len(used), 'capital': spent}
            ti += 1
            heapq.heappush(heap, (g, cid))
            continue
        before = st['rew'](st['q'])
        st['q'] += inc
        total += st['rew'](st['q']) - before
        spent += inc
        used.add(cid)
        nxt = (st['rew'](st['q'] + step) - st['rew'](st['q'])) / step
        heapq.heappush(heap, (-nxt, cid))
    while ti < len(targets):
        out[targets[ti]] = {'usd_day': total, 'apr': total * 365 / spent if spent else None, 'markets': len(used),
                            'capital': spent, 'exhausted': True}
        ti += 1
    return {str(int(k)): v for k, v in out.items()}


# ------------------------------------------------------------------------------------------------- analysis: simulation

SIZE_MULT = [1, 5]            # quote size per side, in multiples of the market's min size
VOL_SCREEN = [False, True]    # skip an hour when the trailing-24h hourly mid move (rms, cents) exceeds v/2
INV_CAP = 4                   # stop quoting the side that grows |inventory| beyond 4 quote sizes


def hourly_mids(prices, h0, h1):
    """Last midpoint at or before each hour boundary in [h0, h1] (None before the first point)."""
    ts = [p[0] for p in prices]
    out = {}
    for h in range(int(h0), int(h1) + 1, 3600):
        i = bisect.bisect_right(ts, h) - 1
        out[h] = prices[i][1] if i >= 0 else None
    return out


def simulate_market(r, data, comp_upper, frac, size_mult, vol_screen, stale=0, record_fills=False, hs_floor=0.0,
                    full_fill=False):
    """Hourly re-centred two-sided quote in one market over its trade history.

    Each hour h: quote q = size_mult x min_size shares per side at distance max(frac x v, half a tick) from the
    midpoint at h - stale hours (the late-entry test uses stale = 1), on the tick grid. Fills only from taker prints
    strictly through the quote (conservative queue), up to the print's size. Rewards accrue while each side rests,
    at today's rate and today's competition (conservative bound), integrated between fills. Inventory is held and
    marked at each hour's midpoint; a maker rebate is paid on fills; holding-reward markets also earn 3.25% on the
    capital. Capital each hour = q (complete sets backing both sides) + the value of the inventory.
    Returns {hour: (pnl, capital, parts)} for the hours quoted or holding inventory."""
    trades, mids = data['trades_by_hour'], data['mids']
    hours = data['hours']
    v, tick = r['v'], r['tick'] or 0.01
    q = max(1.0, size_mult * max(r['min_size'], 1.0))
    s_c = max(frac * v, 50.0 * tick, hs_floor)  # cents; at least half a tick, never inside today's touch
    reb = rebate_rate_for(r['fee_cat'], r['fee_rate'])
    inv, cash = 0.0, 0.0
    res = {}
    fills = []
    for k, h in enumerate(hours):
        mid_now = mids.get(h)
        mid_q = mids.get(h - 3600 * stale) if stale else mid_now
        if mid_now is None:
            continue
        val_start = cash + inv * mid_now
        parts = {'reward': 0.0, 'rebate': 0.0, 'holding': 0.0, 'spread': 0.0}
        quoting = mid_q is not None and 0.0 < mid_q < 1.0
        if quoting and vol_screen:
            back = [mids.get(h - 3600 * j) for j in range(0, 25)]
            dif = [(back[j] - back[j + 1]) * 100.0 for j in range(24) if back[j] is not None and back[j + 1] is not None]
            if dif and math.sqrt(sum(x * x for x in dif) / len(dif)) > v / 2.0:
                quoting = False
        bid = ask = None
        rb = ra = 0.0
        if quoting:
            bid, ask = quote_prices(mid_q, s_c, tick)
            if bid <= 0 or ask >= 1 or bid >= ask:
                quoting = False
        if quoting:
            rb = q if inv < INV_CAP * q else 0.0
            ra = q if inv > -INV_CAP * q else 0.0
            sb, sa = (mid_now - bid) * 100.0, (ask - mid_now) * 100.0
            t_prev = h
            seg = []
            for (ts, px, side, sz) in trades.get(h, ()):
                fb = through_fill(bid, 'bid', px, side, sz if not full_fill else rb, rb) if rb > 0 else 0.0
                fa = through_fill(ask, 'ask', px, side, sz if not full_fill else ra, ra) if ra > 0 else 0.0
                if fb or fa:
                    seg.append((t_prev, ts, rb, ra))
                    t_prev = ts
                    if fb:
                        rb -= fb
                        inv += fb
                        cash -= fb * bid
                        parts['rebate'] += maker_rebate(fb, bid, r['fee_rate'], reb)
                        parts['spread'] += fb * (mid_now - bid)
                        if record_fills:
                            fills.append((h, 'bid', bid, fb))
                    if fa:
                        ra -= fa
                        inv -= fa
                        cash += fa * ask
                        parts['rebate'] += maker_rebate(fa, ask, r['fee_rate'], reb)
                        parts['spread'] += fa * (ask - mid_now)
                        if record_fills:
                            fills.append((h, 'ask', ask, fa))
            seg.append((t_prev, h + 3600, rb, ra))
            for t_a, t_b, sb_rem, sa_rem in seg:
                q1 = order_score(v, sb) * sb_rem if sb_rem >= r['min_size'] else 0.0
                q2 = order_score(v, sa) * sa_rem if sa_rem >= r['min_size'] else 0.0
                ours = q_min(q1, q2, mid_now)
                parts['reward'] += r['rate'] / 24.0 * reward_share(ours, comp_upper) * (t_b - t_a) / 3600.0
        # mark at the next hour's midpoint
        nxt = hours[k + 1] if k + 1 < len(hours) else None
        mid_end = mids.get(nxt) if nxt is not None else mid_now
        if mid_end is None:
            mid_end = mid_now
        inv_val = inv * mid_end if inv >= 0 else -inv * (1.0 - mid_end)
        capital = (q if quoting else 0.0) + abs(inv_val)
        if r['holding']:
            parts['holding'] = capital * HOLDING_RATE / 8760.0
        val_end = cash + inv * mid_end
        pnl = (val_end - val_start) + parts['reward'] + parts['rebate'] + parts['holding']
        if quoting or abs(inv) > 1e-9:
            res[h] = (pnl, capital, parts)
    if record_fills:
        return res, fills
    return res


def prepare_market(raw, h_lo=None, h_hi=None):
    """Trades to YES terms bucketed by hour; hourly mids; the covered hour range (a truncated fetch starts at its
    oldest trade)."""
    trades = sorted(raw['trades'], key=lambda x: x[0])
    t_start = raw['since']
    if not raw.get('complete') and trades:
        t_start = max(t_start, trades[0][0])
    h0 = int(math.ceil(t_start / 3600.0)) * 3600
    h1 = int(math.floor(raw['until'] / 3600.0)) * 3600 - 3600
    if h_lo:
        h0 = max(h0, h_lo)
    if h_hi:
        h1 = min(h1, h_hi)
    by_h = collections.defaultdict(list)
    for ts, oi, side, px, sz, _tx in trades:
        if ts < h0 or ts >= h1 + 3600:
            continue
        ypx, yside = to_yes_terms(px, side, oi)
        by_h[int(ts // 3600) * 3600].append((ts, ypx, yside, sz))
    mids = hourly_mids(raw['prices'], h0 - 25 * 3600, h1 + 3600) if raw['prices'] else {}
    hours = list(range(h0, h1 + 1, 3600))
    return {'trades_by_hour': by_h, 'mids': mids, 'hours': hours, 'h0': h0, 'h1': h1}


CONFIGS = [(f, m, vs) for f in S_GRID_FRAC for m in SIZE_MULT for vs in VOL_SCREEN]
VARIANT_CATS = ['all'] + CATS


def config_name(f, m, vs):
    return 'd%.2fv_x%d_%s' % (f, m, 'vol' if vs else 'novol')


def load_sim_inputs(out, rows, mk):
    sims = []
    for p in sorted((Path(out) / 'raw' / 'trades').glob('*.json.gz')):
        raw = read_gz(p)
        cid = raw['cid']
        if cid not in rows or cid not in mk or not raw['prices']:
            continue
        sims.append((cid, raw))
    return sims


def run_simulation(rows, mk, sims, stale=0, rate_scale=1.0, configs=None, record_fills=False, full_fill=False,
                   joinable_only=True, bound='comp_upper'):
    """{config: {cid: {hour: (pnl, capital, parts)}}} over the trade sample (joinable markets only by default:
    where nobody else quotes inside the band, the midpoint is not a price and the trade history cannot show the
    informed flow a lone tight quote would attract)."""
    res = collections.defaultdict(dict)
    fills = collections.defaultdict(dict)
    for cid, raw in sims:
        if joinable_only and mk[cid]['joinable_share'] < JOIN_MIN:
            continue
        r = dict(rows[cid])
        r['rate'] = r['rate'] * rate_scale
        data = prepare_market(raw)
        comp = mk[cid][bound]
        for (f, m, vs) in (configs or CONFIGS):
            out_ = simulate_market(r, data, comp, f, m, vs, stale=stale, record_fills=record_fills,
                                   hs_floor=mk[cid]['hs_cents'], full_fill=full_fill)
            if record_fills:
                res[config_name(f, m, vs)][cid], fills[config_name(f, m, vs)][cid] = out_
            else:
                res[config_name(f, m, vs)][cid] = out_
    return (res, fills) if record_fills else res


def portfolio_series(per_market, rows, cat, hours):
    """Hourly excess return of the markets in `cat`: sum P&L / sum capital - SSR/8760 (0 when nothing is
    deployed), and the totals that make it up."""
    ser, tot = [], collections.Counter()
    for h in hours:
        pnl = cap = 0.0
        for cid, hh in per_market.items():
            if cat != 'all' and rows[cid]['cat'] != cat:
                continue
            x = hh.get(h)
            if x is None:
                continue
            pnl += x[0]
            cap += x[1]
            for k, v in x[2].items():
                tot[k] += v
        tot['pnl'] += pnl
        tot['capital_hours'] += cap
        ser.append(pnl / cap - SSR / 8760.0 if cap > 0 else 0.0)
    return ser, dict(tot)


def markouts(fills, sims, horizons=(1, 6, 24)):
    """Mean signed markout of the simulated fills per share (positive = good for the maker): bid fills gain when
    the midpoint later rises above the fill price, ask fills when it falls below."""
    mids = {}
    for cid, raw in sims:
        d = prepare_market(raw)
        mids[cid] = d['mids']
    acc = {h: [0.0, 0.0] for h in horizons}
    for cid, fl in fills.items():
        m = mids.get(cid, {})
        for (h, side, px, sz) in fl:
            for H in horizons:
                mm = m.get(h + 3600 * H)
                if mm is None:
                    continue
                gain = (mm - px) if side == 'bid' else (px - mm)
                acc[H][0] += gain * sz
                acc[H][1] += sz
    return {str(H): {'per_share': (a / n if n else None), 'shares': n} for H, (a, n) in acc.items()}


# ------------------------------------------------------------------------------------------------- analysis: chain

def concentration(amounts):
    """Distinct recipients, top-k shares and the Herfindahl index of a {recipient: amount} map."""
    v = sorted(amounts.values(), reverse=True)
    tot = sum(v)
    if not tot:
        return {'recipients': 0}
    share = lambda k: sum(v[:k]) / tot  # noqa: E731
    n50 = next(i + 1 for i in range(len(v)) if sum(v[:i + 1]) >= 0.5 * tot)
    n90 = next(i + 1 for i in range(len(v)) if sum(v[:i + 1]) >= 0.9 * tot)
    return {'recipients': len(v), 'total': tot, 'top1': share(1), 'top10': share(10), 'top100': share(100),
            'recipients_for_half': n50, 'recipients_for_90pct': n90,
            'hhi': sum((x / tot) ** 2 for x in v), 'median_recipient_usd': v[len(v) // 2]}


def analyze_chain(out):
    p = Path(out) / 'raw' / 'chain_payouts.json.gz'
    if not p.exists():
        return None
    d = read_gz(p)
    per_day, tot_by = [], collections.Counter()
    last30 = collections.Counter()
    days = d['days']
    for i, rec in enumerate(days):
        rows = rec['pusd'] + rec['usdce']
        amt = sum(x[2] for x in rows)
        rc = collections.Counter()
        for _b, to, a in rows:
            rc[to] += a
        per_day.append({'day': rec['day'], 'usd': amt, 'transfers': len(rows), 'recipients': len(rc),
                        'pusd': sum(x[2] for x in rec['pusd']), 'usdce': sum(x[2] for x in rec['usdce']),
                        'window': rec['window'], 'top10_share': (sum(sorted(rc.values(), reverse=True)[:10]) / amt)
                        if amt else None})
        tot_by.update(rc)
        if i >= len(days) - 30:
            last30.update(rc)
    paid = [x['usd'] for x in per_day if x['usd'] > 0]
    other = [{'day': o['day'], 'usd': sum(x[2] for x in o['pusd']), 'transfers': len(o['pusd'])}
             for o in d.get('other_days') or []]
    return {'payer': d['payer'], 'days': per_day, 'days_with_payout': len(paid),
            'mean_usd_day': statistics.mean(paid) if paid else None,
            'median_usd_day': statistics.median(paid) if paid else None,
            'last7_mean_usd_day': statistics.mean([x['usd'] for x in per_day[-7:] if x['usd'] > 0] or [0]),
            'first7_mean_usd_day': statistics.mean([x['usd'] for x in per_day[:7] if x['usd'] > 0] or [0]),
            'total_usd': sum(paid), 'concentration_all': concentration(tot_by),
            'concentration_last30': concentration(last30), 'other_payer': d.get('other_payer'),
            'other_payer_days': other,
            'top_recipients_last30': [[a, v] for a, v in last30.most_common(15)]}


# ------------------------------------------------------------------------------------------------- analysis: Kalshi

def period_class(days):
    return '<1h' if days <= 1.0 / 24 + 1e-6 else '<1d' if days < 0.9 else '>=1d'


def lip_quote(book, prog, qn):
    """Our marginal LIP reward ($/day) and capital for qn contracts at the best YES bid and the best NO bid, on one
    book read (zero if the book still misses the target on a side after our order)."""
    tick = book.get('tick') or 0.01
    yb, nb = book['yes_bids'], book['no_bids']
    if not yb or not nb:
        return None
    ys, _ = lip_side_scores(yb, prog['target'], prog['discount'], tick)
    ns, _ = lip_side_scores(nb, prog['target'], prog['discount'], tick)
    both = (sum(x[1] for x in yb) + qn >= prog['target']) and (sum(x[1] for x in nb) + qn >= prog['target'])
    sh = (lip_marginal_share(qn, sum(ys)) + lip_marginal_share(qn, sum(ns))) / 2.0
    return {'usd_day': prog['usd_day'] * sh if both else 0.0, 'capital': qn * (yb[0][0] + nb[0][0]),
            'others_yes': sum(ys), 'others_no': sum(ns), 'spread': round(1.0 - yb[0][0] - nb[0][0], 4)}


def analyze_kalshi(out):
    p = Path(out) / 'raw' / 'kalshi_lip.json.gz'
    if not p.exists():
        return None
    d = read_gz(p)
    now = parse_ts(d['at'])
    act, by_id = [], {}
    for pr in d['active']:
        st, en = parse_ts(pr.get('start_date')), parse_ts(pr.get('end_date'))
        if not st or not en or en <= now:
            continue
        days = max(1.0 / 96, (en - st) / DAY)
        row = {'id': pr['id'], 'ticker': pr['market_ticker'], 'series': pr['market_ticker'].split('-')[0],
               'usd_period': pr['period_reward'] / 1e4, 'days': days, 'cls': period_class(days),
               'usd_day': pr['period_reward'] / 1e4 / days, 'target': fnum(pr.get('target_size_fp')),
               'discount': (pr.get('discount_factor_bps') or 10000) / 1e4,
               'cap': (pr.get('max_reward_per_account') or 0) / 1e4 or None}
        act.append(row)
        by_id[pr['id']] = row
    by_cls = collections.defaultdict(lambda: {'programs': 0, 'usd_day': 0.0})
    for a_ in act:
        by_cls[a_['cls']]['programs'] += 1
        by_cls[a_['cls']]['usd_day'] += a_['usd_day']
    by_series = collections.defaultdict(lambda: {'programs': 0, 'usd_day': 0.0, 'cls': None})
    for a_ in act:
        b_ = by_series[a_['series']]
        b_['programs'] += 1
        b_['usd_day'] += a_['usd_day']
        b_['cls'] = a_['cls']
    paid30, n30 = 0.0, 0
    for pr in d['paid_out']:
        en = parse_ts(pr.get('end_date'))
        if en and now - 30 * DAY <= en <= now:
            paid30 += pr['period_reward'] / 1e4
            n30 += 1
    ends = sorted(pr['end_date'] for pr in d['paid_out'])
    # every read of each sampled market's book
    reads = collections.defaultdict(list)
    for t, b_ in d['books'].items():
        reads[t].append(b_)
    for bp in sorted(Path(out, 'raw').glob('kalshi_books_*.json.gz')):
        for t, b_ in read_gz(bp)['books'].items():
            tick = (d['books'].get(t) or {}).get('tick') or 0.01
            reads[t].append(dict(b_, tick=tick))
    # stratum weights (the sample is hash-drawn per $/day bucket)
    bucket = lambda u: 'a>=200' if u >= 200 else 'b50-200' if u >= 50 else 'c10-50' if u >= 10 else 'd<10'  # noqa
    pop = collections.Counter(bucket(a_['usd_day']) for a_ in act)
    samp_ids = [pid for pid in d['sample'] if pid in by_id]
    smp = collections.Counter(bucket(by_id[pid]['usd_day']) for pid in samp_ids)
    samp = []
    for pid in samp_ids:
        pr = by_id[pid]
        rs = reads.get(pr['ticker']) or []
        qs = {}
        for qn in (100, 1000):
            vals = [lip_quote(b_, pr, qn) for b_ in rs]
            vals = [v for v in vals if v]
            if not vals:
                continue
            ud = statistics.mean(v['usd_day'] for v in vals)
            cap = statistics.mean(v['capital'] for v in vals)
            qs[str(qn)] = {'usd_day': ud, 'capital': cap, 'apr': ud * 365 / cap if cap else None,
                           'others_yes': statistics.mean(v['others_yes'] for v in vals),
                           'others_no': statistics.mean(v['others_no'] for v in vals),
                           'spread': statistics.median(v['spread'] for v in vals), 'reads': len(vals)}
        if '100' not in qs:
            continue
        sr = d['series'].get(pr['series']) or {}
        samp.append({'ticker': pr['ticker'], 'series': pr['series'], 'cls': pr['cls'], 'usd_day': pr['usd_day'],
                     'target': pr['target'], 'discount': pr['discount'], 'q': qs,
                     'weight': pop[bucket(pr['usd_day'])] / max(1, smp[bucket(pr['usd_day'])]),
                     'fee_type': sr.get('fee_type'), 'category': sr.get('category')})
    cls_stats = {}
    for cl in ('<1h', '<1d', '>=1d'):
        xs = [x for x in samp if x['cls'] == cl]
        a1 = [x['q']['100']['apr'] for x in xs if x['q']['100']['apr'] is not None]
        a2 = [x['q']['1000']['apr'] for x in xs if '1000' in x['q'] and x['q']['1000']['apr'] is not None]
        cls_stats[cl] = {'sampled': len(xs), 'apr_q100': {'p25': pctl(a1, 0.25), 'median': pctl(a1, 0.5),
                                                         'p75': pctl(a1, 0.75)},
                         'apr_q1000': {'p25': pctl(a2, 0.25), 'median': pctl(a2, 0.5), 'p75': pctl(a2, 0.75)},
                         'zero_share_q100': (sum(1 for x in xs if x['q']['100']['usd_day'] <= 0) / len(xs))
                         if xs else None}
    # capacity on the slow programs: greedy over sampled programs replicated by their stratum weight
    slow = [x for x in samp if x['cls'] == '>=1d']
    cap_curve = {}
    for K in (1e4, 1e5, 1e6):
        items = []
        for x in slow:
            for qn in ('100', '1000'):
                if qn in x['q'] and x['q'][qn]['capital'] > 0:
                    items.append((x['q'][qn]['usd_day'] / x['q'][qn]['capital'], x['q'][qn]['capital'],
                                  x['q'][qn]['usd_day'], x['weight'], x['ticker'], qn))
        items.sort(key=lambda z: -z[0])
        spent = usd = 0.0
        used = set()
        for yld, cap, ud, w, t, qn in items:
            if t in used:
                continue
            reps = max(1, int(round(w)))
            for _ in range(reps):
                if spent + cap > K:
                    break
                spent += cap
                usd += ud
            used.add(t)
            if spent >= K * 0.999:
                break
        cap_curve[str(int(K))] = {'capital': spent, 'usd_day': usd, 'apr': usd * 365 / spent if spent else None}
    return {'active_programs': len(act), 'active_usd_day': sum(a_['usd_day'] for a_ in act),
            'by_period_class': dict(by_cls),
            'paid_out_last30_usd': paid30, 'paid_out_last30_programs': n30, 'paid_out_rows_read': len(d['paid_out']),
            'paid_out_end_range': [ends[0], ends[-1]] if ends else None,
            'per_program_usd_day': {'median': pctl([a_['usd_day'] for a_ in act], 0.5),
                                    'p90': pctl([a_['usd_day'] for a_ in act], 0.9),
                                    'max': max([a_['usd_day'] for a_ in act] or [0])},
            'top_series': sorted(([k, v['programs'], v['usd_day'], v['cls']] for k, v in by_series.items()),
                                 key=lambda x: -x[2])[:20],
            'sample_n': len(samp), 'reads_per_market_median': pctl([x['q']['100']['reads'] for x in samp], 0.5),
            'by_class_sample': cls_stats, 'slow_capacity_pre_adverse_selection': cap_curve,
            'sample': samp,
            'maker_fee_series': sorted({x['series'] for x in samp if x['fee_type'] and 'maker' in str(x['fee_type'])}),
            'access': 'LIP: most regular US members; international (non-US) users, FCM/IB customers excluded '
                      '(help.kalshi.com/en/articles/13823851). APY 3.50% on cash and positions, US only, balance '
                      '>= $250 (articles/13823847). Polymarket international excludes US persons, so no one '
                      'account holds both rents.'}


# ------------------------------------------------------------------------------------------------- analysis: Kalshi simulation

K_SIZES = [100, 1000]
K_VOL_CENTS = 2.5          # skip an hour when the trailing-24h rms hourly mid move exceeds 2.5c


def simulate_kalshi(km, usd_day, R_y, R_n, eligible, q, vol_screen, stale=0, maker_fee=0.0):
    """Hourly join-the-touch quote on one Kalshi LIP market: q contracts on the best YES bid and q on the best NO
    bid (a YES ask), from the hourly candle's closing book; fills only from taker prints strictly through
    (taker_side 'no' at a YES price below our bid, 'yes' above our ask); LIP reward = $/day x mean of the two
    side shares against today's measured competitor scores, accrued between fills, zero if a side still misses
    the target; inventory marked at the next hour's mid. Returns {hour: (pnl, capital, parts)}."""
    cand = {int(c[0]): (c[1], c[2]) for c in km['candles'] if c[1] is not None and c[2] is not None}
    if not cand:
        return {}
    by_h = collections.defaultdict(list)
    for ts, ypx, side, cnt in sorted(km['trades'], key=lambda x: x[0]):
        if ypx is None or not cnt:
            continue
        by_h[int(math.ceil(ts / 3600.0)) * 3600 - 3600].append((ts, ypx, 'BUY' if side == 'yes' else 'SELL', cnt))
    hours = sorted(cand)
    inv = cash = 0.0
    res = {}
    for k, h in enumerate(hours):
        bb, ba = cand[h]
        mid_now = (bb + ba) / 2.0
        qb = cand.get(h - 3600 * stale) if stale else (bb, ba)
        parts = {'reward': 0.0, 'fee': 0.0, 'spread': 0.0}
        val_start = cash + inv * mid_now
        quoting = qb is not None and 0 < qb[0] < qb[1] < 1
        if quoting and vol_screen:
            back = [cand.get(h - 3600 * j) for j in range(25)]
            mids = [(x[0] + x[1]) / 2.0 if x else None for x in back]
            dif = [(mids[j] - mids[j + 1]) * 100 for j in range(24) if mids[j] is not None and mids[j + 1] is not None]
            if dif and math.sqrt(sum(x * x for x in dif) / len(dif)) > K_VOL_CENTS:
                quoting = False
        rb = ra = 0.0
        if quoting:
            bid, ask = qb
            if bid >= ba:      # a stale bid at or through the current ask would take; post-only rejects it
                bid = None
            if ask <= bb:
                ask = None
            rb = q if (bid is not None and inv < INV_CAP * q) else 0.0
            ra = q if (ask is not None and inv > -INV_CAP * q) else 0.0
            both = eligible          # today's reads: both sides reach the target once our size is added
            t_prev, seg = h, []
            for ts, px, side, cnt in by_h.get(h, ()):
                fb = through_fill(bid, 'bid', px, side, cnt, rb) if rb > 0 else 0.0
                fa = through_fill(ask, 'ask', px, side, cnt, ra) if ra > 0 else 0.0
                if fb or fa:
                    seg.append((t_prev, ts, rb, ra))
                    t_prev = ts
                if fb:
                    rb -= fb
                    inv += fb
                    cash -= fb * bid
                    parts['spread'] += fb * (mid_now - bid)
                    parts['fee'] += kalshi_fee(fb, bid, rate=maker_fee) if maker_fee else 0.0
                if fa:
                    ra -= fa
                    inv -= fa
                    cash += fa * ask
                    parts['spread'] += fa * (ask - mid_now)
                    parts['fee'] += kalshi_fee(fa, 1.0 - ask, rate=maker_fee) if maker_fee else 0.0
            seg.append((t_prev, h + 3600, rb, ra))
            if both:
                for t_a, t_b, yb_rem, na_rem in seg:
                    sh = (lip_marginal_share(yb_rem, R_y) + lip_marginal_share(na_rem, R_n)) / 2.0
                    parts['reward'] += usd_day / 24.0 * sh * (t_b - t_a) / 3600.0
        nxt = hours[k + 1] if k + 1 < len(hours) else None
        mid_end = (sum(cand[nxt]) / 2.0) if nxt is not None and nxt - h <= 3600 * 3 else mid_now
        inv_val = inv * mid_end if inv >= 0 else -inv * (1.0 - mid_end)
        capital = (q * (bb + 1 - ba) if quoting else 0.0) + abs(inv_val)
        val_end = cash + inv * mid_end
        pnl = val_end - val_start + parts['reward'] - parts['fee']
        if quoting or abs(inv) > 1e-9:
            res[h] = (pnl, capital, parts)
    return res


def kalshi_sim(out):
    """Choose-then-test over (size x volatility screen) for the slow LIP markets; returns the protocol result and
    the reward / market-making decomposition per variant (rewards at today's pools and competition)."""
    tp = Path(out) / 'raw' / 'kalshi_trades.json.gz'
    if not tp.exists():
        return None
    kt = read_gz(tp)
    ka = analyze_kalshi(out)
    samp = {x['ticker']: x for x in ka['sample']}
    per_var = collections.defaultdict(dict)
    for t, km in kt['markets'].items():
        x = samp.get(t)
        if not x:
            continue
        maker_fee = 0.0175 if (x.get('fee_type') and 'maker' in str(x['fee_type'])) else 0.0
        for qn in K_SIZES:
            qq = x['q'].get(str(qn)) or x['q'].get('100')
            for vs in (False, True):
                per_var['q%d_%s' % (qn, 'vol' if vs else 'novol')][t] = simulate_kalshi(
                    km, x['usd_day'], qq['others_yes'], qq['others_no'], qq['usd_day'] > 0, qn, vs,
                    maker_fee=maker_fee)
    hs = sorted({h for v in per_var.values() for hh in v.values() for h in hh})
    if not hs:
        return None
    hours = list(range(hs[0], hs[-1] + 1, 3600))
    series, tab = {}, {}
    for name, per in per_var.items():
        ser, tot = [], collections.Counter()
        for h in hours:
            pnl = cap = 0.0
            for t, hh in per.items():
                z = hh.get(h)
                if z:
                    pnl += z[0]
                    cap += z[1]
                    for kk, vv in z[2].items():
                        tot[kk] += vv
            tot['pnl'] += pnl
            tot['cap'] += cap
            ser.append(pnl / cap - SSR / 8760.0 if cap > 0 else 0.0)
        series[name] = ser
        ch = tot['cap'] or 1.0
        tab[name] = {'ann_excess_full': B.perf(ser, 8760).get('ann_return'), 'reward_apr': tot['reward'] / ch * 8760,
                     'mm_apr': (tot['pnl'] - tot['reward']) / ch * 8760, 'spread_apr': tot['spread'] / ch * 8760,
                     'mean_capital': tot['cap'] / len(hours), 'apy_addon_us_only': KALSHI_APY}
    sel = B.choose_then_test(series, frac=0.5, periods_per_year=8760)
    name = sel['chosen']
    qn = int(name[1:].split('_')[0])
    vs = name.endswith('_vol')
    late = {}
    for t, km in kt['markets'].items():
        x = samp.get(t)
        if not x:
            continue
        qq = x['q'].get(str(qn)) or x['q'].get('100')
        late[t] = simulate_kalshi(km, x['usd_day'], qq['others_yes'], qq['others_no'], qq['usd_day'] > 0, qn, vs,
                                  stale=1)
    ser_l = []
    for h in hours:
        pnl = sum(hh[h][0] for hh in late.values() if h in hh)
        cap = sum(hh[h][1] for hh in late.values() if h in hh)
        ser_l.append(pnl / cap - SSR / 8760.0 if cap > 0 else 0.0)
    c = B.cutoff_index(len(hours), 0.5)
    base = B.perf(series[name][c:], 8760)['ann_return']
    lt = B.perf(ser_l[c:], 8760)['ann_return']
    daily = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for t, hh in per_var[name].items():
        for h, (pnl, cap, parts) in hh.items():
            dd = daily[dt.datetime.fromtimestamp(h, dt.timezone.utc).date().isoformat()]
            dd[0] += pnl
            dd[1] += parts['reward']
            dd[2] += cap / 24.0
    return {'markets': len(kt['markets']), 'hours': len(hours), 'variants': len(series), 'protocol': sel,
            'chosen_daily': {k: {'pnl': v[0], 'reward': v[1], 'mean_capital': v[2]} for k, v in sorted(daily.items())},
            'cutoff_hour': dt.datetime.fromtimestamp(hours[c], dt.timezone.utc).isoformat(),
            'variant_table': tab, 'late_entry': {'oos_ann_excess': lt, 'chosen_oos_ann_excess': base,
                                                 'share_kept': (lt + SSR) / (base + SSR) if base + SSR else None}}


# ------------------------------------------------------------------------------------------------- analysis: favourite carry

PH = ROOT / 'research' / '2026-10-09' / 'polymarket_history'
FAV_BANDS = [(0.85, 0.95), (0.95, 0.995)]
FAV_HORIZONS = ['30d', '7d']
FAV_WAIT = 7 * DAY          # a resting bid lives a week, then is cancelled


def maker_fill_time(series, t, t_end, bid, hs):
    """First time after t (and before t_end) the favourite's midpoint is at or below bid - hs, i.e. the ask has come
    down to the bid and sellers trade through it (a conservative queue on a midpoint series); None if never."""
    for ts, p in series:
        if ts <= t:
            continue
        if ts >= t_end:
            break
        if p <= bid - hs + 1e-9:
            return ts
    return None


def fav_carry(live_hs):
    """Long-dated favourite carry as a maker, on standalone binaries only (negRisk false and no group title: the
    universe's $10k volume floor over-samples winning members of multi-outcome events, coordinator note
    2026-10-14). Entry: at the horizon before the scheduled end, rest a bid one live half-spread under the
    favourite's midpoint for a week; it fills only if the midpoint later falls a further half-spread (the ask
    reaches the bid). Filled: hold to resolution, no fee, plus the maker rebate. Capital is locked from posting.
    The taker version (ask + fee at the horizon) is computed on the same entries for comparison."""
    import polymarket_history as P
    uni = P.load_universe(PH)
    by_id = {m['id']: m for m in uni}
    sample = json.loads((PH / 'sample.json').read_text())['markets']
    A, _, meta = P.build_trades(PH, by_id, sample)
    live = {'half_spread': live_hs}
    cutoff = parse_ts(P.CUTOFF)
    rows = collections.defaultdict(list)
    n_std = collections.Counter()
    for tr in A:
        if tr['h'] not in FAV_HORIZONS or tr['pay'] is None:
            continue
        m = by_id[tr['id']]
        standalone = not m.get('negRisk') and not (m.get('groupItemTitle') or '').strip() \
            and not m.get('event_augmented')
        n_std['standalone' if standalone else 'member'] += 1
        if not standalone:
            continue
        band = next((b for b in FAV_BANDS if b[0] <= tr['p'] < b[1]), None)
        if band is None:
            continue
        hs = P.half_spread_for(live, tr['cat'], tr['p'])
        tick = 0.001 if tr['p'] >= 0.96 else 0.01
        bid = math.floor((tr['p'] - hs) / tick + 1e-9) * tick
        coarse, fine = P.load_series(PH, tr['id'], 'c'), P.load_series(PH, tr['id'], 'f')
        ser = sorted((fine or []) + [x for x in (coarse or []) if not fine or x[0] < fine[0][0]])
        if tr['side'] == 1:
            ser = [[ts, 1.0 - p] for ts, p in ser]
        t_end = min(tr['t'] + FAV_WAIT, tr['close'])
        tf = maker_fill_time(ser, tr['t'], t_end, bid, hs)
        rate = tr['rate']
        reb = 0.25 if tr['cat'] not in ('sports', 'crypto_price', 'crypto_updown') else \
            (0.15 if tr['cat'] == 'sports' else 0.20)
        if tf is not None:
            r_m = tr['pay'] / bid - 1.0 + maker_rebate(1.0, bid, rate, reb) / bid
            mk_row = dict(tr, close=tr['close'], t=tr['t'], filled=True, r=r_m, fill_t=tf, bid=bid)
        else:
            mk_row = dict(tr, close=t_end, t=tr['t'], filled=False, r=0.0, fill_t=None, bid=bid)
        px = min(0.999, tr['p'] + hs)
        r_t = tr['pay'] / (px + fee_rate(tr['cat']) * px * (1 - px)) - 1.0
        name = '%s|%.2f-%.3f' % (tr['h'], band[0], band[1])
        rows[name].append((mk_row, dict(tr, r=r_t)))
    # protocol: choose on markets closed before the cutoff, test on entries after it (daily series, SSR excess)
    t_lo = min(x[0]['t'] for v in rows.values() for x in v)
    t_hi = max(x[0]['close'] for v in rows.values() for x in v)
    series, parts, n_is = {}, {}, None
    for name, v in rows.items():
        ins = [mk for mk, _ in v if mk['close'] < cutoff]
        oos = [mk for mk, _ in v if mk['t'] >= cutoff]
        s_in, _, _ = P.daily_series(ins, [x['r'] for x in ins], t_lo, cutoff - 1)
        s_oos, k_oos, _ = P.daily_series(oos, [x['r'] for x in oos], cutoff, t_hi)
        if not s_in:
            s_in = [0.0] * (int((cutoff - 1) // DAY) - int(t_lo // DAY) + 1)
        if not s_oos:
            s_oos = [0.0] * (int(t_hi // DAY) - int(cutoff // DAY) + 1)
        n_is = len(s_in)
        series[name] = s_in + s_oos
        tk_oos = [tk for mk, tk in v if mk['t'] >= cutoff]

        def ann(xs):
            cd = sum(x['w'] * max(1.0, (x['close'] - x['t']) / DAY) for x in xs)
            return (sum(x['w'] * x['r'] for x in xs) / cd * 365.0) if cd else None
        parts[name] = {'entries_in': len(ins), 'entries_oos': len(oos),
                       'fill_rate_oos': (sum(1 for x in oos if x['filled']) / len(oos)) if oos else None,
                       'win_rate_filled_oos': (sum(1 for x in oos if x['filled'] and x['pay'] >= 1) /
                                               max(1, sum(1 for x in oos if x['filled']))),
                       'maker_ann_oos_on_locked_capital': ann(oos),
                       'maker_ann_oos_filled_only': ann([x for x in oos if x['filled']]),
                       'taker_ann_oos': ann(tk_oos), 'mean_capital_oos': k_oos,
                       'filled_oos_mean_bid': (statistics.mean(x['bid'] for x in oos if x['filled'])
                                               if any(x['filled'] for x in oos) else None),
                       'filled_oos_mean_return': (statistics.mean(x['r'] for x in oos if x['filled'])
                                                  if any(x['filled'] for x in oos) else None),
                       'taker_oos_mean_price': statistics.mean(x['p'] for x in tk_oos) if tk_oos else None,
                       'taker_oos_win_rate': (sum(1 for x in tk_oos if x['pay'] >= 1) / len(tk_oos)) if tk_oos else None,
                       'taker_oos_mean_return': statistics.mean(x['r'] for x in tk_oos) if tk_oos else None}
    sel = B.choose_then_test(series, frac=n_is / len(next(iter(series.values()))), periods_per_year=365)
    return {'meta': dict(meta), 'standalone_counts': dict(n_std), 'variants': parts, 'protocol': sel,
            'holding_addon_apr': HOLDING_RATE,
            'note': 'returns are per dollar of capital locked from posting; the protocol series are daily excess '
                    'over SSR; a holding reward would add 3.25%/yr of position value only in the ~18-60 eligible '
                    'events, none of which has resolved'}


def cmd_analyze(args):
    out = Path(args.out)
    t0 = time.time()
    rows, at = rewarded_markets(out)
    res = {'generated': now_iso(), 'rewards_snapshot': at, 'ssr': SSR, 'holding_rate': HOLDING_RATE,
           'c_scale': C_SCALE}
    res['budgets'] = analyze_budgets(rows)
    snaps = load_snaps(out)
    res['snapshots'] = [s_['at'] for s_ in snaps]
    mk = analyze_books(rows, snaps)
    print('books analysed: %d markets x %d snapshots (%.0fs)' % (len(mk), len(snaps), time.time() - t0), flush=True)
    # competition summaries
    comp = {}
    for cat in VARIANT_CATS:
        ms = [m for m in mk.values() if cat == 'all' or m['cat'] == cat]
        if not ms:
            continue
        js = [m for m in ms if m['joinable_share'] >= JOIN_MIN]
        row = {'markets': len(ms), 'usd_day': sum(m['rate'] for m in ms),
               'empty_book_share': sum(m['empty_share'] for m in ms) / len(ms),
               'joinable_markets': len(js), 'joinable_usd_day': sum(m['rate'] for m in js),
               'comp_upper_median_joinable': pctl([m['comp_upper'] for m in js], 0.5),
               'half_spread_cents_median_joinable': pctl([m['hs_cents'] for m in js], 0.5),
               'half_spread_cents_median_not_joinable': pctl([m['hs_cents'] for m in ms
                                                              if m['joinable_share'] < JOIN_MIN], 0.5)}
        for k in ('0.00', '0.33', '0.67'):
            ap = [m['quotes'][k]['apr_cons'] for m in js if m['quotes'][k]['apr_cons'] is not None]
            apo = [m['quotes'][k]['apr_opt'] for m in js if m['quotes'][k]['apr_opt'] is not None]
            row['apr_cons_' + k] = {'p25': pctl(ap, 0.25), 'median': pctl(ap, 0.5), 'p75': pctl(ap, 0.75),
                                    'p90': pctl(ap, 0.9)}
            row['apr_opt_' + k] = {'median': pctl(apo, 0.5), 'p90': pctl(apo, 0.9)}
        comp[cat] = row
    res['competition'] = comp
    # how much of the pool is already competed for: per market, today's competitor score vs our $1k quote
    res['rent_curve'] = {k: greedy_allocation(mk, rows, k) for k in ('0.00', '0.33', '0.67')}
    res['rent_curve_optimistic'] = {k: greedy_allocation(mk, rows, k, bound='comp_lower') for k in ('0.33',)}
    res['rent_curve_naive_incl_unjoinable'] = {k: greedy_allocation(mk, rows, k, joinable_only=False)
                                               for k in ('0.33',)}
    print('rent curves done (%.0fs)' % (time.time() - t0), flush=True)
    # does the venue pay what it configures? (chain)
    res['chain'] = analyze_chain(out)
    res['kalshi'] = analyze_kalshi(out)
    # holding rewards
    gp = out / 'raw' / 'gamma_active.json.gz'
    g = read_gz(gp)
    hold = [m for m in g['markets'] if m.get('holdingRewardsEnabled')]
    hold_rewarded = [rows[m['conditionId']] for m in hold if m['conditionId'] in rows]
    hold_mk = [mk[m['conditionId']] for m in hold if m['conditionId'] in mk]
    res['holding'] = {'markets': len(hold), 'events': len({m.get('event_id') for m in hold}),
                      'scan_complete': g.get('complete'), 'active_scanned': g.get('active_scanned'),
                      'also_liquidity_rewarded': len(hold_rewarded),
                      'liquidity_usd_day_in_holding_markets': sum(r['rate'] for r in hold_rewarded),
                      'complete_set_apr': HOLDING_RATE, 'complete_set_excess_over_ssr': HOLDING_RATE - SSR,
                      'liquidity_apr_cons_0.33_median': pctl([m['quotes']['0.33']['apr_cons'] for m in hold_mk
                                                              if m['quotes']['0.33']['apr_cons'] is not None], 0.5),
                      'events_list': sorted({m.get('event_title') or '' for m in hold})}
    # ---------------------------------------------------------------- simulation
    sims = load_sim_inputs(out, rows, mk)
    res['sim_markets'] = len(sims)
    res['sim_markets_joinable'] = sum(1 for cid, _ in sims if mk[cid]['joinable_share'] >= JOIN_MIN)
    res['sim_strata'] = dict(collections.Counter(rows[cid]['cat'] for cid, _ in sims
                                                 if mk[cid]['joinable_share'] >= JOIN_MIN))
    sim = run_simulation(rows, mk, sims)
    h_all = sorted({h for cfg in sim.values() for hh in cfg.values() for h in hh})
    hours = list(range(h_all[0], h_all[-1] + 1, 3600)) if h_all else []
    variants, totals = {}, {}
    for cfg, per in sim.items():
        for cat in VARIANT_CATS:
            ser, tot = portfolio_series(per, rows, cat, hours)
            if tot.get('capital_hours', 0) <= 0:
                continue
            name = '%s|%s' % (cat, cfg)
            variants[name] = ser
            totals[name] = tot
    res['sim_hours'] = len(hours)
    res['sim_first_hour'] = dt.datetime.fromtimestamp(hours[0], dt.timezone.utc).isoformat() if hours else None
    res['variants_tried'] = len(variants)
    ctt = B.choose_then_test(variants, frac=0.5, periods_per_year=8760)
    res['protocol'] = ctt
    chosen = ctt['chosen']
    cat_c, cfg_c = chosen.split('|')
    res['chosen_totals'] = totals[chosen]
    # all variants' annualised excess on the full sample and the decomposition per capital-hour
    table = {}
    for name, tot in totals.items():
        ch = tot['capital_hours']
        table[name] = {'ann_excess_full': B.perf(variants[name], 8760).get('ann_return'),
                       'reward_apr': tot.get('reward', 0) / ch * 8760, 'rebate_apr': tot.get('rebate', 0) / ch * 8760,
                       'holding_apr': tot.get('holding', 0) / ch * 8760,
                       'mm_apr': (tot['pnl'] - tot.get('reward', 0) - tot.get('rebate', 0) - tot.get('holding', 0))
                       / ch * 8760, 'spread_apr': tot.get('spread', 0) / ch * 8760, 'capital_hours': ch,
                       'mean_capital': ch / max(1, len(hours))}
    res['variant_table'] = table
    daily = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for cid, hh in sim[cfg_c].items():
        if cat_c != 'all' and rows[cid]['cat'] != cat_c:
            continue
        for h, (pnl, cap, parts) in hh.items():
            dd = daily[dt.datetime.fromtimestamp(h, dt.timezone.utc).date().isoformat()]
            dd[0] += pnl
            dd[1] += parts['reward']
            dd[2] += cap / 24.0
    res['chosen_daily'] = {k: {'pnl': v[0], 'reward': v[1], 'mean_capital': v[2]} for k, v in sorted(daily.items())}
    res['cutoff_hour'] = dt.datetime.fromtimestamp(hours[B.cutoff_index(len(hours), 0.5)], dt.timezone.utc).isoformat()
    # late entry: quotes centred on the midpoint an hour stale
    f_c, m_c, vs_c = next(c_ for c_ in CONFIGS if config_name(*c_) == cfg_c)
    late = run_simulation(rows, mk, sims, stale=1, configs=[(f_c, m_c, vs_c)])
    ser_late, tot_late = portfolio_series(late[cfg_c], rows, cat_c, hours)
    c = B.cutoff_index(len(hours), 0.5)
    base_oos = B.perf(variants[chosen][c:], 8760)['ann_return']
    late_oos = B.perf(ser_late[c:], 8760)['ann_return']
    res['late_entry'] = {'chosen_oos_ann_excess': base_oos, 'stale_oos_ann_excess': late_oos,
                         'share_kept': (late_oos + SSR) / (base_oos + SSR) if (base_oos + SSR) else None,
                         'note': 'quotes centred on the midpoint one hour stale; share of gross (pre-SSR) return'}
    # no-reward baseline and markouts for the chosen config
    base0 = run_simulation(rows, mk, sims, rate_scale=0.0, configs=[(f_c, m_c, vs_c)])
    ser0, tot0 = portfolio_series(base0[cfg_c], rows, cat_c, hours)
    res['no_reward_baseline'] = {'ann_excess_full': B.perf(ser0, 8760).get('ann_return'),
                                 'mm_apr': (tot0['pnl'] - tot0.get('rebate', 0) - tot0.get('holding', 0)) /
                                 tot0['capital_hours'] * 8760 if tot0.get('capital_hours') else None}
    _, fl = run_simulation(rows, mk, sims, configs=[(f_c, m_c, vs_c)], record_fills=True)
    res['markouts_chosen'] = markouts({cid: x for cid, x in fl[cfg_c].items()
                                       if cat_c == 'all' or rows[cid]['cat'] == cat_c}, sims)
    # stress: a through-print fills the whole remaining quote, not just the print's size
    ff = run_simulation(rows, mk, sims, configs=[(f_c, m_c, vs_c)], full_fill=True)
    ser_ff, tot_ff = portfolio_series(ff[cfg_c], rows, cat_c, hours)
    res['full_fill_stress'] = {'ann_excess_full': B.perf(ser_ff, 8760).get('ann_return'),
                               'oos_ann_excess': B.perf(ser_ff[c:], 8760).get('ann_return'),
                               'oos_t': B.newey_west_t(ser_ff[c:])[0]}
    # the naive family (markets nobody else quotes included), recorded and counted, never chosen from
    naive = run_simulation(rows, mk, sims, joinable_only=False)
    nv = {}
    for cfg, per in naive.items():
        for cat in VARIANT_CATS:
            ser, tot = portfolio_series(per, rows, cat, hours)
            if tot.get('capital_hours', 0) > 0:
                nv['%s|%s' % (cat, cfg)] = B.perf(ser, 8760).get('ann_return')
    res['naive_family'] = {'variants': len(nv), 'ann_excess_full_median': pctl(list(nv.values()), 0.5),
                           'ann_excess_full_max': max(nv.values()) if nv else None}
    fp = out / 'raw' / 'first_pass_analysis.json'
    if fp.exists():
        f1 = json.loads(fp.read_text())
        res['first_pass_disclosed'] = {'note': 'first run (2026-10-14 ~07:57 UTC) quoted every rewarded market in '
                                       'the sample including ones nobody else quotes, with no touch floor; its '
                                       'protocol result is kept for the variant count, not used',
                                       'variants': f1.get('variants_tried'), 'chosen': f1['protocol']['chosen'],
                                       'oos_ann_excess': f1['protocol']['out_of_sample']['ann_return'],
                                       'oos_t': f1['protocol']['oos_t']}
    n_first = (res.get('first_pass_disclosed') or {}).get('variants') or 0
    res['variants_total_including_dropped'] = len(variants) + len(nv) + n_first
    # sensitivity: rewards against the optimistic competitor bound (never used for the choice)
    opt = run_simulation(rows, mk, sims, bound='comp_lower')
    res['optimistic_rewards_sensitivity'] = {}
    for cfg, per in opt.items():
        ser, tot = portfolio_series(per, rows, 'all', hours)
        if tot.get('capital_hours', 0) > 0:
            res['optimistic_rewards_sensitivity']['all|' + cfg] = {
                'ann_excess_full': B.perf(ser, 8760).get('ann_return'),
                'oos_ann_excess': B.perf(ser[c:], 8760).get('ann_return'), 'oos_t': B.newey_west_t(ser[c:])[0],
                'reward_apr': tot.get('reward', 0) / tot['capital_hours'] * 8760}
    cen = run_simulation(rows, mk, sims, bound='comp_central')
    res['central_rewards_sensitivity'] = {}
    for cfg, per in cen.items():
        ser, tot = portfolio_series(per, rows, 'all', hours)
        if tot.get('capital_hours', 0) > 0:
            res['central_rewards_sensitivity']['all|' + cfg] = {
                'ann_excess_full': B.perf(ser, 8760).get('ann_return'),
                'oos_ann_excess': B.perf(ser[c:], 8760).get('ann_return'), 'oos_t': B.newey_west_t(ser[c:])[0],
                'reward_apr': tot.get('reward', 0) / tot['capital_hours'] * 8760}
    ser_o, _ = portfolio_series(opt[cfg_c], rows, cat_c, hours)
    res['optimistic_rewards_sensitivity']['chosen'] = {'oos_ann_excess': B.perf(ser_o[c:], 8760).get('ann_return'),
                                                       'oos_t': B.newey_west_t(ser_o[c:])[0]}
    # capacity: the simulated portfolio's own capital (min-size quotes in the sampled markets) and its out-of-sample
    # excess; the rent curve above is rewards before adverse selection and is not netted against the simulation's
    # average market-making loss (the greedy's first picks are same-day weather and intraday markets, where that
    # loss is largest)
    mean_cap = table[chosen]['mean_capital']
    oos_ex = ctt['out_of_sample']['ann_return']
    res['capacity'] = {'chosen_mean_capital': mean_cap, 'chosen_oos_ann_excess': oos_ex,
                       'chosen_usd_year_excess_at_sim_capital': oos_ex * mean_cap,
                       'rent_curve_pre_adverse_selection': res['rent_curve']['%.2f' % f_c]}
    go = {'in_sample_positive': ctt['in_sample_positive'], 'oos_t_ge_2': (ctt['oos_t'] or 0) >= 2.0,
          'chosen_in_bh_positive': chosen in ctt['bh_survivors_positive'],
          'oos_excess_positive_at_sim_capital': oos_ex > 0}
    go['go'] = all(go.values())
    res['go_rule'] = go
    print('simulation done (%.0fs)' % (time.time() - t0), flush=True)
    res['market_table'] = market_table(mk, rows)
    res['kalshi_sim'] = kalshi_sim(out)
    print('kalshi simulation done (%.0fs)' % (time.time() - t0), flush=True)
    if not getattr(args, 'skip_fav', False):
        ph = json.loads((PH / 'analysis.json').read_text())
        res['fav_carry'] = fav_carry(ph['live']['half_spread'])
        print('favourite carry done (%.0fs)' % (time.time() - t0), flush=True)
    n_sens = (len(res.get('optimistic_rewards_sensitivity') or {}) + len(res.get('central_rewards_sensitivity') or {})
              + 3)   # + full-fill stress, no-reward baseline, late entry
    res['variants_grand_total'] = {
        'total': res['variants_total_including_dropped'] + n_sens + ((res.get('kalshi_sim') or {}).get('variants', 0) + 1)
        + len((res.get('fav_carry') or {}).get('variants') or {}),
        'polymarket_tested': res['variants_tried'], 'polymarket_first_pass_and_naive': res['variants_total_including_dropped']
        - res['variants_tried'], 'polymarket_sensitivity_runs': n_sens,
        'kalshi': (res.get('kalshi_sim') or {}).get('variants', 0) + 1,
        'favourite_carry': len((res.get('fav_carry') or {}).get('variants') or {})}
    ks = res.get('kalshi_sim') or {}
    if ks:
        kp = ks['protocol']
        ks['go_rule'] = {'in_sample_positive': kp['in_sample_positive'], 'oos_t_ge_2': (kp['oos_t'] or 0) >= 2.0,
                         'chosen_in_bh_positive': kp['chosen'] in kp['bh_survivors_positive']}
        ks['go_rule']['go'] = all(ks['go_rule'].values())
    write_json(out / 'analysis.json', res)
    if not (out / 'book_entries.json').exists() or not go['go']:
        write_json(out / 'book_entries.json', [])
    print('analysis.json written (%.0fs); go=%s' % (time.time() - t0, go['go']), flush=True)


def market_table(mk, rows, n=40):
    top = sorted(mk.items(), key=lambda kv: -(kv[1]['quotes']['0.33']['usd_day_cons'] or 0))[:n]
    return [{'cid': cid, 'q': rows[cid]['question'], 'cat': m['cat'], 'rate': m['rate'], 'v': m['v'],
             'min_size': m['min_size'], 'mid': m['mid'], 'comp_upper': m['comp_upper'],
             'usd_day_1k_0.33': m['quotes']['0.33']['usd_day_cons'], 'apr_1k_0.33': m['quotes']['0.33']['apr_cons'],
             'volume24hr': m['volume24hr'], 'n_snap': m['n_snap']} for cid, m in top]


def fmt_usd(x):
    if x is None:
        return '-'
    return '${:,.0f}'.format(x)


def fmt_pct(x, d=1):
    if x is None:
        return '-'
    return ('{:.%df}%%' % d).format(100.0 * x)


def esc(name):
    """A variant name inside a markdown table cell: its '|' separator escaped."""
    return name.replace('|', '\\|')


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_rewards_mm tables (%s)' % a['generated'], '',
         'Every number is in `analysis.json`; keys are given in brackets.', '']
    b = a['budgets']
    ch0 = a.get('chain') or {}
    k0 = a.get('kalshi') or {}
    ks0 = a.get('kalshi_sim') or {}
    p0 = a['protocol']
    cc0 = (ch0.get('concentration_last30') or {})
    L += ['## Rent table', '',
          '| rent | payer | $/day | collected by | competition | yield at stated capital |', '|---|---|---:|---|---|---|',
          '| Polymarket liquidity rewards | Polymarket (payer %s, pUSD at 00:00 UTC) | %s configured; %s paid (7-day mean) '
          '[budgets, chain] | %d addresses in 30 days; %d take half, top 10 take %s [chain.concentration_last30] | '
          '%d of %d markets joinable (others quote both sides inside the band); unjoinable books have a median %0.fc '
          'half-spread [competition.all] | before adverse selection %s/day on $100k (conservative bound) '
          '[rent_curve]; simulated net out of sample %s a year on %s, t %.2f [protocol, capacity] |' % (
              ch0.get('payer', '-')[:10] + '...', fmt_usd(b['usd_day_total']), fmt_usd(ch0.get('last7_mean_usd_day')),
              cc0.get('recipients', 0), cc0.get('recipients_for_half', 0), fmt_pct(cc0.get('top10')),
              a['competition']['all']['joinable_markets'], a['competition']['all']['markets'],
              a['competition']['all']['half_spread_cents_median_not_joinable'] or 0,
              fmt_usd(a['rent_curve']['0.33']['100000']['usd_day']), fmt_pct(p0['out_of_sample']['ann_return'], 0),
              fmt_usd(a['capacity']['chosen_mean_capital']), p0['oos_t'] or 0),
          '| Polymarket maker rebates | taker fees (15-25%% rebated) | not measured (payer not identified) | makers '
          'filled | per filled share rebate x feeRate x p(1-p) | %s of capital a year in the chosen simulation '
          '[variant_table] |' % fmt_pct(a['variant_table'][p0['chosen']]['rebate_apr'], 0),
          '| Polymarket holding rewards | Polymarket treasury | 3.25%% a year of position value | holders of %d+ '
          'markets in %d+ events | none (pro rata) | complete set %s against the savings rate [holding] |' % (
              a['holding']['markets'], a['holding']['events'], fmt_pct(a['holding']['complete_set_excess_over_ssr'], 2)),
          '| Kalshi LIP | Kalshi | %s paid (30-day mean); %s configured in programs of a day or more [kalshi] | US '
          'members only | marginal APR median %s for 100 contracts at the touch, programs of a day or more '
          '[kalshi.by_class_sample] | simulated net out of sample %s a year, t %.2f [kalshi_sim] |' % (
              fmt_usd(k0.get('paid_out_last30_usd', 0) / 30.0), fmt_usd((k0.get('by_period_class') or {}).get('>=1d', {})
                                                                       .get('usd_day')),
              fmt_pct((k0.get('by_class_sample') or {}).get('>=1d', {}).get('apr_q100', {}).get('median'), 0),
              fmt_pct(ks0.get('protocol', {}).get('out_of_sample', {}).get('ann_return'), 0),
              ks0.get('protocol', {}).get('oos_t') or 0),
          '| Kalshi APY | Kalshi | 3.50% a year on cash and positions | US members, balance >= $250 | none | '
          '-0.30% against the savings rate |', '']
    L += ['## Polymarket liquidity-reward budgets today [budgets]', '',
          'Configured %s/day across %d markets (%s/yr); sponsored %s/day. Half the budget sits in %d markets, 90%% in '
          '%d. Per market: median %s, p90 %s, max %s a day. Max spread median %.1fc, min size median %.0f shares.'
          % (fmt_usd(b['usd_day_total']), b['markets'], fmt_usd(b['usd_year_total']), fmt_usd(b['sponsored_usd_day']),
             b['per_market']['markets_for_half_of_budget'], b['per_market']['markets_for_90pct_of_budget'],
             fmt_usd(b['per_market']['median']), fmt_usd(b['per_market']['p90']), fmt_usd(b['per_market']['max']),
             b['max_spread_cents']['median'], b['min_size_shares']['median']), '',
          '| category | markets | $/day | joinable markets | joinable $/day | median marginal APR at 1/3 v, $1k (cons.) |',
          '|---|---:|---:|---:|---:|---:|']
    comp = a['competition']
    for cat, v in sorted(b['by_category'].items(), key=lambda kv: -kv[1]['usd_day']):
        c = comp.get(cat) or {}
        L.append('| %s | %d | %s | %s | %s | %s |' % (cat, v['markets'], fmt_usd(v['usd_day']),
                                                      c.get('joinable_markets', '-'), fmt_usd(c.get('joinable_usd_day')),
                                                      fmt_pct((c.get('apr_cons_0.33') or {}).get('median'), 0)))
    L += ['', '| $/day bucket | markets | $/day |', '|---|---:|---:|']
    for k, v in b['by_rate_bucket'].items():
        L.append('| %s | %d | %s |' % (k, v['markets'], fmt_usd(v['usd_day'])))
    ch = a.get('chain') or {}
    if ch:
        cc = ch['concentration_last30']
        L += ['', '## What was paid on chain [chain]', '',
              'Payer %s (pUSD/USDC.e transfers 23:30-01:30 UTC). Days with a payout: %d; mean %s/day, last 7 days %s/day, '
              'first 7 days %s/day; total %s.' % (ch['payer'], ch['days_with_payout'], fmt_usd(ch['mean_usd_day']),
                                                  fmt_usd(ch['last7_mean_usd_day']), fmt_usd(ch['first7_mean_usd_day']),
                                                  fmt_usd(ch['total_usd'])),
              '', 'Last 30 days: %d recipients; top 1 %s, top 10 %s, top 100 %s; %d addresses take half, %d take 90%%; '
              'HHI %.3f.' % (cc['recipients'], fmt_pct(cc['top1']), fmt_pct(cc['top10']), fmt_pct(cc['top100']),
                            cc['recipients_for_half'], cc['recipients_for_90pct'], cc['hhi']), '',
              '| day | paid | transfers | recipients | top-10 share |', '|---|---:|---:|---:|---:|']
        for x in ch['days'][-14:]:
            L.append('| %s | %s | %d | %d | %s |' % (x['day'], fmt_usd(x['usd']), x['transfers'], x['recipients'],
                                                    fmt_pct(x['top10_share'])))
    L += ['', '## Rent curve before adverse selection (greedy by marginal $/day per $, joinable markets, '
          'conservative competitor bound) [rent_curve]', '',
          '| distance | $10k | $100k | $1M | $10M |', '|---|---:|---:|---:|---:|']
    for k, v in a['rent_curve'].items():
        L.append('| %s v | %s | %s | %s | %s |' % (k, *['%s/day (%s)' % (fmt_usd(v[K]['usd_day']), fmt_pct(v[K]['apr'], 0))
                                                        for K in ('10000', '100000', '1000000', '10000000')]))
    v = a['rent_curve_optimistic']['0.33']
    L.append('| 0.33 v, optimistic bound | %s | %s | %s | %s |' % tuple(
        '%s/day (%s)' % (fmt_usd(v[K]['usd_day']), fmt_pct(v[K]['apr'], 0)) for K in ('10000', '100000', '1000000', '10000000')))
    p = a['protocol']
    L += ['', '## Simulated slow quoter [protocol, variant_table]', '',
          '%d sampled markets with trades, %d joinable (simulated), %d hours from %s; %d variants in the tested family, '
          '%d tried including dropped ones.' % (a['sim_markets'], a['sim_markets_joinable'], a['sim_hours'],
                                               a['sim_first_hour'], a['variants_tried'],
                                               a['variants_total_including_dropped']), '',
          'Chosen in sample: `%s` (in-sample ann. excess %s, Sharpe %.1f). Out of sample: %s, HAC t %.2f, rank %d of %d; '
          'in BH positive survivors: %s.' % (p['chosen'], fmt_pct(p['in_sample']['ann_return'], 0),
                                            p['in_sample']['sharpe'] or 0, fmt_pct(p['out_of_sample']['ann_return'], 0),
                                            p['oos_t'] or 0, p['oos_rank'], p['n_variants'],
                                            p['chosen'] in p['bh_survivors_positive']), '',
          '| variant (all categories) | ann. excess | reward | rebate | spread | inventory + spread (MM) | mean capital |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for name, v in sorted(a['variant_table'].items()):
        if name.startswith('all|') or name == p['chosen']:
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (esc(name), fmt_pct(v['ann_excess_full'], 0),
                                                                fmt_pct(v['reward_apr'], 0), fmt_pct(v['rebate_apr'], 0),
                                                                fmt_pct(v['spread_apr'], 0), fmt_pct(v['mm_apr'], 0),
                                                                fmt_usd(v['mean_capital'])))
    le = a['late_entry']
    L += ['', 'Late entry (quotes centred on an hour-stale midpoint): out-of-sample %s vs %s, share kept %s '
          '[late_entry]. No-reward baseline: %s a year [no_reward_baseline]. Full-fill stress: out of sample %s, t %.2f '
          '[full_fill_stress]. Markouts per share at 1/6/24 h: %s [markouts_chosen].'
          % (fmt_pct(le['stale_oos_ann_excess'], 0), fmt_pct(le['chosen_oos_ann_excess'], 0), fmt_pct(le['share_kept'], 0),
             fmt_pct(a['no_reward_baseline']['ann_excess_full'], 0), fmt_pct(a['full_fill_stress']['oos_ann_excess'], 0),
             a['full_fill_stress']['oos_t'] or 0,
             ', '.join('%s' % (('%.2fc' % (100 * v['per_share'])) if v['per_share'] is not None else '-')
                       for v in a['markouts_chosen'].values()))]
    os_ = a.get('optimistic_rewards_sensitivity') or {}
    if os_:
        L += ['', 'Rewards against the optimistic competitor bound instead (sensitivity, never used for the choice) '
              '[optimistic_rewards_sensitivity]:', '', '| variant | ann. excess full | out of sample | OOS t |',
              '|---|---:|---:|---:|']
        for name, v in sorted(os_.items()):
            if name == 'chosen':
                continue
            L.append('| %s | %s | %s | %.1f |' % (esc(name), fmt_pct(v['ann_excess_full'], 0), fmt_pct(v['oos_ann_excess'], 0),
                                                  v['oos_t'] or 0))
    cs_ = a.get('central_rewards_sensitivity') or {}
    if cs_:
        L += ['', 'Rewards against a central competitor estimate (midpoint of the bounds in [0.10, 0.90], balanced bound '
              'outside) [central_rewards_sensitivity]:', '', '| variant | ann. excess full | out of sample | OOS t |',
              '|---|---:|---:|---:|']
        for name, v in sorted(cs_.items()):
            L.append('| %s | %s | %s | %.1f |' % (esc(name), fmt_pct(v['ann_excess_full'], 0), fmt_pct(v['oos_ann_excess'], 0),
                                                  v['oos_t'] or 0))
    cd = a.get('chosen_daily') or {}
    if cd:
        L += ['', 'Chosen variant by day (P&L / rewards / mean capital) [chosen_daily]: ' + '; '.join(
            '%s %+.0f/%.0f/%s' % (d[5:], v['pnl'], v['reward'], fmt_usd(v['mean_capital'])) for d, v in cd.items())]
    ks = a.get('kalshi_sim') or {}
    if ks:
        kp = ks['protocol']
        L += ['', '## Kalshi slow-LIP quoter simulation [kalshi_sim]', '',
              '%d markets (programs of a day or longer), %d hours; %d variants (size x volatility screen); cutoff %s. '
              'Chosen `%s`: in sample %s, out of sample %s, HAC t %.2f, rank %d; BH positive survivors (full sample): %s. '
              'Late entry share kept %s. Go: %s.' % (ks['markets'], ks['hours'], ks['variants'], ks['cutoff_hour'],
                                                    kp['chosen'], fmt_pct(kp['in_sample']['ann_return'], 0),
                                                    fmt_pct(kp['out_of_sample']['ann_return'], 0), kp['oos_t'] or 0,
                                                    kp['oos_rank'], ', '.join(kp['bh_survivors_positive']) or 'none',
                                                    fmt_pct(ks['late_entry']['share_kept'], 0), ks['go_rule']['go']),
              '', '| variant | ann. excess full | reward | MM (spread + inventory) | spread | mean capital |',
              '|---|---:|---:|---:|---:|---:|']
        for name, v in sorted(ks['variant_table'].items()):
            L.append('| %s | %s | %s | %s | %s | %s |' % (name, fmt_pct(v['ann_excess_full'], 0), fmt_pct(v['reward_apr'], 0),
                                                          fmt_pct(v['mm_apr'], 0), fmt_pct(v['spread_apr'], 0),
                                                          fmt_usd(v['mean_capital'])))
        L += ['', 'Chosen by day (P&L / LIP reward / mean capital): ' + '; '.join(
            '%s %+.0f/%.0f/%s' % (d[5:], v['pnl'], v['reward'], fmt_usd(v['mean_capital']))
            for d, v in ks['chosen_daily'].items())]
    k = a.get('kalshi') or {}
    if k:
        L += ['', '## Kalshi LIP [kalshi]', '',
              'Active programs %d, %s/day configured (by period: %s). Paid out, programs ending in the last 30 days: %s '
              '(%s/day). %s' % (k['active_programs'], fmt_usd(k['active_usd_day']),
                                ', '.join('%s %s' % (c, fmt_usd(v['usd_day'])) for c, v in k['by_period_class'].items()),
                                fmt_usd(k['paid_out_last30_usd']), fmt_usd(k['paid_out_last30_usd'] / 30), k['access']),
              '', '| period class | sampled | marginal APR, 100 contracts (p25/median/p75) | 1,000 contracts |',
              '|---|---:|---:|---:|']
        for cl, v in k['by_class_sample'].items():
            if v['sampled']:
                L.append('| %s | %d | %s / %s / %s | %s / %s / %s |' % (
                    cl, v['sampled'], *[fmt_pct(v['apr_q100'][q], 0) for q in ('p25', 'median', 'p75')],
                    *[fmt_pct(v['apr_q1000'][q], 0) for q in ('p25', 'median', 'p75')]))
        L += ['', 'Slow programs, greedy capacity before adverse selection: ' + '; '.join(
            '%s -> %s/day (%s)' % (fmt_usd(v['capital']), fmt_usd(v['usd_day']), fmt_pct(v['apr'], 0))
            for v in k['slow_capacity_pre_adverse_selection'].values())]
    h = a['holding']
    L += ['', '## Holding rewards [holding]', '',
          '%d markets in %d events flagged holdingRewardsEnabled (scan of %d active markets, complete: %s); %d of them '
          'also carry liquidity rewards (%s/day). A complete set earns %s a year, %s against the savings rate.'
          % (h['markets'], h['events'], h['active_scanned'] or 0, h['scan_complete'], h['also_liquidity_rewarded'],
             fmt_usd(h['liquidity_usd_day_in_holding_markets']), fmt_pct(h['complete_set_apr'], 2),
             fmt_pct(h['complete_set_excess_over_ssr'], 2))]
    fc = a.get('fav_carry')
    if fc:
        pp = fc['protocol']
        L += ['', '## Maker favourite carry on standalone binaries [fav_carry]', '',
              'Chosen `%s`; out of sample %s, HAC t %.2f, rank %d of %d.' % (pp['chosen'],
                                                                         fmt_pct(pp['out_of_sample'].get('ann_return'), 0),
                                                                         pp['oos_t'] or 0, pp['oos_rank'],
                                                                         pp['n_variants']), '',
              '| variant | entries in/oos | fill rate oos | filled win rate | taker oos win rate vs mean price |',
              '|---|---:|---:|---:|---:|']
        for name, v in sorted(fc['variants'].items()):
            L.append('| %s | %d / %d | %s | %s | %s vs %s |' % (esc(name), v['entries_in'], v['entries_oos'],
                                                                 fmt_pct(v['fill_rate_oos'], 0),
                                                                 fmt_pct(v['win_rate_filled_oos'], 0),
                                                                 fmt_pct(v['taker_oos_win_rate'], 0),
                                                                 fmt_pct(v['taker_oos_mean_price'], 1)))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('tables.md written (%d lines)' % len(L))


if __name__ == '__main__':
    main()
