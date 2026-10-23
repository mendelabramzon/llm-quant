#!/usr/bin/env python3
"""Crypto price markets on Polymarket and Kalshi against probabilities implied by Deribit options.

Why. Polymarket lists daily "above $K on <date>" strikes, daily range buckets and daily, weekly and monthly
touch markets ("What price will Bitcoin hit in October?") on BTC, ETH, SOL and XRP; Kalshi lists the same families
on CF Benchmarks indices. The hypothesis tested here is that retail prices touch and tail probabilities without a
vol surface (for driftless paths a touch is worth about twice the terminal digital), while Deribit's option books are
a deep reference for the same distribution. A deviation that persists for hours at a pre-registered decision time is
a model edge that needs no speed: the counterparty is a buyer without a model.

Pipeline (subcommands):
  universe   parse the stored resolved Polymarket universe (2026-10-09 polymarket_history) into strike / range /
             touch_day / touch_week / touch_month markets with their resolution clocks; choose the price-fetch set
  spot       Binance 1h klines (the resolution source's pair) for BTC, ETH, SOL, XRP / USDT
  deribit    history.deribit.com option trades in the hour (BTC: half hour) before every decision hour and the hour
             after it (late entry), for BTC and ETH inverse options and the USDC-margined SOL/XRP options
  prices     CLOB prices-history (hourly midpoints) for the fetch set, last 14.5 days before the close (two windows
             for monthly markets)
  live       one snapshot now: Polymarket crypto books, Kalshi crypto markets, Deribit book summaries
  analyze    implied probabilities, calibration, signals, choose_then_test, late entry, capacity -> analysis.json
  render     tables.md

Model. Per expiry, the smile is the Deribit mark implied vol of every instrument traded in the window (the mark,
not the trade, so bid/ask bounce does not enter); the forward of each expiry is backed out of near-the-money trades
(Deribit inverse options are priced Black76(F)/F in the coin: calls and puts give the same F that way, 2025-10-01
check, and not with the index in the denominator). Total variance is interpolated linearly in time between the two
expiries that bracket the resolution time, at fixed log-moneyness; the forward is interpolated likewise and moved
onto Binance's USDT pair by the Binance/Deribit-index ratio at the decision time. Digital = call spread on that smile
(skew included); touch = reflection formula at the barrier-strike vol, with the forward's drift.

PRE-REGISTERED before any return was computed (2026-10-14 ~08:30 UTC):
  decision times  strike, range, touch_week: resolution/window end minus 24h, 72h, 144h
                  touch_month: window end minus 24h, 72h, 7d, 14d, 21d (weekly checkpoints)
                  touch_day: window end minus 12h and 6h (the window is one ET day)
  split           choose on decisions before 2026-04-15, test once on decisions from 2026-04-15
  variants        type-horizon (16) x edge threshold {0.02, 0.05, 0.10} x side {both, yes, no} x {taker, maker}
                  = 288; the delta hedge is an overlay on the chosen variant only
  taker           pays midpoint + live half-spread (crypto books, by price band) + 0.07 p(1-p) per share
  maker           rests a bid at model - threshold for 6 hours; fills only if a later hourly midpoint prints at least
                  one tick through it; earns its limit, pays no fee
  late entry      the chosen rule's trades entered one hour later at the market price then
  go rule         in-sample positive, out-of-sample HAC t >= 2, chosen variant in bh_survivors_positive, and excess over
                  SSR at the stated capacity after all costs

    uv run python scripts/pm_crypto_options.py universe --out research/2026-10-14/pm_crypto_options
    uv run python scripts/pm_crypto_options.py spot     --out research/2026-10-14/pm_crypto_options
    uv run python scripts/pm_crypto_options.py deribit  --out research/2026-10-14/pm_crypto_options
    uv run python scripts/pm_crypto_options.py prices   --out research/2026-10-14/pm_crypto_options
    uv run python scripts/pm_crypto_options.py live     --out research/2026-10-14/pm_crypto_options
    uv run python scripts/pm_crypto_options.py analyze  --out research/2026-10-14/pm_crypto_options
    uv run python scripts/pm_crypto_options.py render   --out research/2026-10-14/pm_crypto_options
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import datetime as dt
import json
import math
import random
import re
import statistics
import sys
import time
import urllib.parse
import zoneinfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
from polymarket_history import (Http, categorize, fee_rate, parse_ts, write_gz, read_gz, update_manifest,  # noqa: E402,F401
                                price_path, fetch_prices, write_json, stable_u, as_of, binary_payout, daily_series,
                                summarize, cluster_bootstrap, utc, fnum, jload, compact_market, paginate_events,
                                parse_book, fetch_books)
from pm_crossvenue import http_json, kalshi_fee, KALSHI  # noqa: E402,F401

DAY = 86400.0
HOUR = 3600.0
YEAR = 365.0 * DAY
SSR = 0.038
ET = zoneinfo.ZoneInfo('America/New_York')
STORED = ROOT / 'research' / '2026-10-09' / 'polymarket_history'
DERIBIT = 'https://history.deribit.com/api/v2/public/'
DERIBIT_LIVE = 'https://www.deribit.com/api/v2/public/'
BINANCE = 'https://data-api.binance.vision/api/v3/'
CUTOFF = parse_ts('2026-04-15T00:00:00Z')
T_LO = parse_ts('2025-04-01T00:00:00Z')
PM_RATE = 0.07            # crypto taker coefficient (docs.polymarket.com/trading/fees; live feeSchedule rate 0.07)
DERIBIT_FEE = 0.0003      # option taker fee, fraction of underlying per contract (capped at 12.5% of the premium)
HEDGE_FEE = 0.0005        # perp taker fee per unit notional traded for the delta hedge
MAKER_LIFE = 6 * HOUR
TICK = 0.01

HORIZONS = {'strike': [24, 72, 144], 'range': [24, 72, 144], 'touch_week': [24, 72, 144],
            'touch_month': [24, 72, 168, 336, 504], 'touch_day': [12, 6]}
THRESHOLDS = [0.02, 0.05, 0.10]
SIDES = ['both', 'yes', 'no']
EXECS = ['taker', 'maker']
COINS = {'bitcoin': 'BTC', 'btc': 'BTC', 'ethereum': 'ETH', 'eth': 'ETH', 'solana': 'SOL', 'sol': 'SOL',
         'xrp': 'XRP'}
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
          'november', 'december']
PRICE_BANDS = [(0.0, 0.02), (0.02, 0.05), (0.05, 0.15), (0.15, 0.35), (0.35, 0.65), (0.65, 0.85), (0.85, 0.95),
               (0.95, 0.98), (0.98, 1.0001)]

_N = statistics.NormalDist()


# ------------------------------------------------------------------------------------------------ pure: parsing

COIN_RE = re.compile(r'\b(bitcoin|btc|ethereum|eth|solana|sol|xrp)\b', re.I)
NUM = r'\$?\s*([\d][\d,]*(?:\.\d+)?|\.\d+)\s*([kKmM])?'
INTRADAY = re.compile(r'\b\d{1,2}\s*(?::\d\d)?\s*(am|pm)\s*et\b', re.I)


def parse_num(s, suffix=None):
    v = float(s.replace(',', ''))
    if suffix and suffix.lower() == 'k':
        v *= 1e3
    elif suffix and suffix.lower() == 'm':
        v *= 1e6
    return v


def classify(question):
    """Question text -> dict(kind, coin, direction, K or (L, U), month) or None.

    kinds: strike (terminal digital), range (terminal bucket), touch_day / touch_week / touch_month (one-touch).
    direction: 'above' (YES if S_T > K), 'below' (YES if S_T < K), 'up' (touch from below), 'down' (touch from
    above). Intraday ("at 4PM ET") and hourly families are excluded: they are speed games."""
    q = (question or '').strip()
    ql = q.lower()
    mc = COIN_RE.search(q)
    if not mc:
        return None
    coin = COINS[mc.group(1).lower()]
    if INTRADAY.search(q) or 'up or down' in ql:
        return None
    months = '|'.join(MONTHS)
    m = re.search(r'between\s+' + NUM + r'\s+and\s+' + NUM + r'\s+on\s+(' + months + r')\s+(\d{1,2})', ql)
    if m:
        lo, hi = parse_num(m.group(1), m.group(2)), parse_num(m.group(3), m.group(4))
        return {'kind': 'range', 'coin': coin, 'direction': 'range', 'L': lo, 'U': hi,
                'month': MONTHS.index(m.group(5)) + 1, 'day': int(m.group(6))}
    m = re.search(r'\b(above|greater than|less than|below)\s+' + NUM + r'\s+on\s+(' + months + r')\s+(\d{1,2})', ql)
    if m:
        d = 'above' if m.group(1) in ('above', 'greater than') else 'below'
        return {'kind': 'strike', 'coin': coin, 'direction': d, 'K': parse_num(m.group(2), m.group(3)),
                'month': MONTHS.index(m.group(4)) + 1, 'day': int(m.group(5))}
    m = re.search(r'\b(reach|hit|dip to)\s+' + NUM + r'\s+(.*)$', ql)
    if m:
        d = 'down' if m.group(1) == 'dip to' else 'up'
        K = parse_num(m.group(2), m.group(3))
        rest = m.group(4)
        mm = re.match(r'in\s+(' + months + r')\s*\??$', rest)
        if mm:
            return {'kind': 'touch_month', 'coin': coin, 'direction': d, 'K': K, 'month': MONTHS.index(mm.group(1)) + 1}
        mm = re.match(r'on\s+(' + months + r')\s+(\d{1,2})\s*\??$', rest)
        if mm:
            return {'kind': 'touch_day', 'coin': coin, 'direction': d, 'K': K, 'month': MONTHS.index(mm.group(1)) + 1,
                    'day': int(mm.group(2))}
        mm = re.match(r'(' + months + r')\s+(\d{1,2})\s*[-–]\s*(?:(' + months + r')\s+)?(\d{1,2})\s*\??$', rest)
        if mm:
            m2 = mm.group(3) or mm.group(1)
            return {'kind': 'touch_week', 'coin': coin, 'direction': d, 'K': K, 'month': MONTHS.index(mm.group(1)) + 1,
                    'day': int(mm.group(2)), 'month2': MONTHS.index(m2) + 1, 'day2': int(mm.group(4))}
    return None


def et_ts(year, month, day, hour=0, minute=0):
    return dt.datetime(year, month, day, hour, minute, tzinfo=ET).timestamp()


def resolution_clock(info, end_ts):
    """(window_start, resolution_ts) in unix seconds from the parsed question and the market's endDate (which fixes
    the year). Strike and range resolve on the 12:00 ET one-minute candle; touch windows run from 00:00 ET on the
    first day to 23:59 ET on the last (resolution taken at 24:00 ET)."""
    y = dt.datetime.fromtimestamp(end_ts, ET).year
    k = info['kind']
    if k in ('strike', 'range'):
        # the year is that of the endDate, unless the date named is in January and the endDate in late December
        t = et_ts(y, info['month'], info['day'], 12)
        if abs(t - end_ts) > 40 * DAY:
            for yy in (y - 1, y + 1):
                tt = et_ts(yy, info['month'], info['day'], 12)
                if abs(tt - end_ts) < abs(t - end_ts):
                    t = tt
        return None, t
    if k == 'touch_day':
        s = et_ts(y, info['month'], info['day'])
        if abs(s - end_ts) > 40 * DAY:
            s = min((et_ts(yy, info['month'], info['day']) for yy in (y - 1, y + 1)), key=lambda v: abs(v - end_ts))
        return s, (dt.datetime.fromtimestamp(s, ET) + dt.timedelta(days=1)).timestamp()
    if k == 'touch_week':
        s = et_ts(y, info['month'], info['day'])
        yy2 = y + (1 if info['month2'] < info['month'] else 0)
        e = (dt.datetime(yy2, info['month2'], info['day2'], tzinfo=ET) + dt.timedelta(days=1)).timestamp()
        if abs(e - end_ts) > 40 * DAY:
            s = et_ts(y - 1, info['month'], info['day'])
            e = (dt.datetime(yy2 - 1, info['month2'], info['day2'], tzinfo=ET) + dt.timedelta(days=1)).timestamp()
        return s, e
    if k == 'touch_month':
        mo = info['month']
        ey = dt.datetime.fromtimestamp(end_ts - 2 * DAY, ET)
        yy = ey.year if ey.month >= mo else ey.year - 1 if mo - ey.month > 6 else ey.year
        s = et_ts(yy, mo, 1)
        e = et_ts(yy + (1 if mo == 12 else 0), 1 if mo == 12 else mo + 1, 1)
        return s, e
    return None, None


# ------------------------------------------------------------------------------------------------ pure: costs

def pm_fee(price, rate=PM_RATE):
    """Polymarket taker fee per share: rate x p x (1 - p); makers pay none."""
    return rate * price * (1.0 - price)


def taker_cost(mid, half_spread, rate=PM_RATE, cap=0.999):
    """All-in cost per share of buying at the ask (midpoint plus half-spread) as a taker."""
    px = min(cap, max(0.001, mid + half_spread))
    return px + pm_fee(px, rate)


def taker_edge(p_model, mid, half_spread, side, rate=PM_RATE):
    """Expected profit per share of a taker buy of YES (side 'yes') or NO (side 'no') under the model."""
    if side == 'yes':
        return p_model - taker_cost(mid, half_spread, rate)
    return (1.0 - p_model) - taker_cost(1.0 - mid, half_spread, rate)


def maker_fill(limit, path, tick=TICK):
    """A resting bid at `limit` fills only if a later midpoint prints at least one tick through it (conservative
    queue: touching the limit is not a fill). `path` is the list of later midpoints of the side being bought.
    Returns the index of the filling point or None."""
    for i, m in enumerate(path):
        if m is not None and m <= limit - tick + 1e-12:
            return i
    return None


def band_key(p):
    for lo, hi in PRICE_BANDS:
        if lo <= p < hi:
            return '%.2f-%.2f' % (lo, min(hi, 1.0))
    return '0.98-1.00'


# ------------------------------------------------------------------------------------------------ pure: options

def black76(F, K, sigma, T, cp):
    """Undiscounted Black-76 value in USD of a call ('C') or put ('P')."""
    if T <= 0 or sigma <= 0:
        return max(0.0, F - K) if cp == 'C' else max(0.0, K - F)
    v = sigma * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * v * v) / v
    d2 = d1 - v
    if cp == 'C':
        return F * _N.cdf(d1) - K * _N.cdf(d2)
    return K * _N.cdf(-d2) - F * _N.cdf(-d1)


def implied_vol(usd, F, K, T, cp, lo=0.01, hi=6.0):
    """Black-76 implied vol by bisection; None when the price is outside the no-arbitrage bounds."""
    intrinsic = max(0.0, F - K) if cp == 'C' else max(0.0, K - F)
    if T <= 0 or usd <= intrinsic + 1e-12 or usd >= (F if cp == 'C' else K):
        return None
    a, b = lo, hi
    if black76(F, K, b, T, cp) < usd:
        return None
    for _ in range(80):
        m = 0.5 * (a + b)
        if black76(F, K, m, T, cp) < usd:
            a = m
        else:
            b = m
    return 0.5 * (a + b)


def forward_from_inverse(price_coin, K, sigma, T, cp, S):
    """Forward implied by an inverse option's coin price and its implied vol: price_coin x F = Black76(F)."""
    def g(F):
        return black76(F, K, sigma, T, cp) / F - price_coin
    lo, hi = S * 0.85, S * 1.15
    glo, ghi = g(lo), g(hi)
    if glo * ghi > 0:
        return None
    for _ in range(70):
        m = 0.5 * (lo + hi)
        gm = g(m)
        if gm * glo <= 0:
            hi = m
        else:
            lo, glo = m, gm
    return 0.5 * (lo + hi)


class Smile:
    """Implied vol of one expiry as a function of log-moneyness k = ln(K/F): linear between observed points, flat
    beyond them."""

    def __init__(self, T, F, pts):
        self.T, self.F = T, F
        pts = sorted(pts)
        ks, vs = [], []
        for k, v in pts:
            if ks and abs(k - ks[-1]) < 1e-9:
                vs[-1] = 0.5 * (vs[-1] + v)
                continue
            ks.append(k)
            vs.append(v)
        self.ks, self.vs = ks, vs

    def vol(self, k):
        ks, vs = self.ks, self.vs
        if k <= ks[0]:
            return vs[0]
        if k >= ks[-1]:
            return vs[-1]
        i = bisect.bisect_right(ks, k)
        w = (k - ks[i - 1]) / (ks[i] - ks[i - 1])
        return vs[i - 1] + w * (vs[i] - vs[i - 1])


class Surface:
    """Smiles of several expiries at one decision time; total variance interpolated linearly in time at fixed
    log-moneyness; the forward's log-basis likewise. `spot` is the Deribit index at the decision time."""

    def __init__(self, t, spot, smiles):
        self.t, self.spot = t, spot
        self.smiles = sorted(smiles, key=lambda s: s.T)

    def forward(self, T):
        sm = self.smiles
        def lb(s):
            return math.log(s.F / self.spot)
        if T <= sm[0].T:
            return self.spot * math.exp(lb(sm[0]) * T / sm[0].T) if sm[0].T > 0 else self.spot
        if T >= sm[-1].T:
            return self.spot * math.exp(lb(sm[-1]) * T / sm[-1].T)
        i = bisect.bisect_right([s.T for s in sm], T)
        a, b = sm[i - 1], sm[i]
        w = (T - a.T) / (b.T - a.T)
        return self.spot * math.exp(lb(a) + w * (lb(b) - lb(a)))

    def vol(self, k, T):
        """Implied vol at log-moneyness k (relative to the T-forward) for maturity T (years)."""
        sm = self.smiles
        if T <= sm[0].T:
            return sm[0].vol(k)
        if T >= sm[-1].T:
            return sm[-1].vol(k)
        i = bisect.bisect_right([s.T for s in sm], T)
        a, b = sm[i - 1], sm[i]
        wa, wb = a.vol(k) ** 2 * a.T, b.vol(k) ** 2 * b.T
        w = wa + (wb - wa) * (T - a.T) / (b.T - a.T)
        return math.sqrt(max(w, 1e-12) / T)


def digital_above(F, K, T, volfn, h=0.002):
    """P(S_T > K) under the smile: minus the slope of the undiscounted call price, by a call spread of relative
    half-width h around K (this is the skew-corrected digital, not N(d2))."""
    if T <= 0:
        return 1.0 if F > K else 0.0
    k1, k2 = K * (1 - h), K * (1 + h)
    c1 = black76(F, k1, volfn(math.log(k1 / F)), T, 'C')
    c2 = black76(F, k2, volfn(math.log(k2 / F)), T, 'C')
    return min(1.0, max(0.0, (c1 - c2) / (k2 - k1)))


def touch_prob(S, B, T, sigma, mu=0.0):
    """P(the path touches B before T) for log-price with drift mu - sigma^2/2 and vol sigma (reflection principle,
    continuous monitoring). B above S is an up barrier, below S a down barrier."""
    if T <= 0 or sigma <= 0:
        return 1.0 if (B >= S and S >= B) else 0.0
    if (B >= S and S >= B):
        return 1.0
    b = math.log(B / S)
    nu = mu - 0.5 * sigma * sigma
    sT = sigma * math.sqrt(T)
    e = math.exp(min(700.0, 2.0 * nu * b / (sigma * sigma)))
    if b > 0:
        p = _N.cdf((-b + nu * T) / sT) + e * _N.cdf((-b - nu * T) / sT)
    else:
        p = _N.cdf((b - nu * T) / sT) + e * _N.cdf((b + nu * T) / sT)
    return min(1.0, max(0.0, p))


def model_prob(m, surf, t, S_bin, ratio, running=None):
    """Model probability of YES for market m at decision time t.

    S_bin: Binance price at t; ratio: Binance/Deribit-index at t (moves the Deribit forward onto the USDT pair);
    running: (high, low) of the Binance path since the window opened (touch markets), or None."""
    T = (m['T'] - t) / YEAR
    if T <= 0:
        return None
    F = surf.forward(T) * ratio
    def vf(k):
        return surf.vol(k, T)
    kind = m['kind']
    if kind == 'strike':
        p = digital_above(F, m['K'], T, vf)
        return p if m['direction'] == 'above' else 1.0 - p
    if kind == 'range':
        return max(0.0, digital_above(F, m['L'], T, vf) - digital_above(F, m['U'], T, vf))
    # touch: already touched -> 1
    if running is not None:
        hi, lo = running
        if m['direction'] == 'up' and hi is not None and hi >= m['K']:
            return 1.0
        if m['direction'] == 'down' and lo is not None and lo <= m['K']:
            return 1.0
    B = m['K']
    if (m['direction'] == 'up' and S_bin >= B) or (m['direction'] == 'down' and S_bin <= B):
        return 1.0
    sig = vf(math.log(B / F))
    mu = math.log(F / S_bin) / T
    return touch_prob(S_bin, B, T, sig, mu)


# ------------------------------------------------------------------------------------------------ universe

def study_markets():
    uni = read_gz(STORED / 'raw' / 'universe.json.gz')
    rows, skipped = [], collections.Counter()
    for m in uni:
        if m.get('cat') == 'crypto_updown':
            continue
        info = classify(m.get('question'))
        if not info:
            continue
        if len(m.get('outcomes') or []) != 2 or [str(x).lower() for x in m['outcomes']] != ['yes', 'no']:
            skipped['not_yes_no'] += 1
            continue
        pay = binary_payout(m)
        if pay is None:
            skipped['no_resolution'] += 1
            continue
        end = parse_ts(m.get('endDate'))
        close = parse_ts(m.get('closedTime'))
        if end is None or close is None:
            skipped['no_dates'] += 1
            continue
        ws, T = resolution_clock(info, end)
        if T is None:
            skipped['no_clock'] += 1
            continue
        r = dict(info)
        created = parse_ts(m.get('acceptingOrdersTimestamp') or m.get('startDate') or m.get('createdAt'))
        if ws is not None and created and created > ws:
            # strikes added mid-window: "from the creation of this market ... Price action before this market's
            # creation will not be considered" (rules of the October 2026 touch markets)
            ws = created
        r.update({'id': m['id'], 'question': m['question'], 'event': m.get('event_id'), 'T': T, 'ws': ws,
                  'end': end, 'close': close, 'start': parse_ts(m.get('acceptingOrdersTimestamp') or m.get('startDate')
                                                                   or m.get('createdAt')),
                  'pay': pay, 'vol': m.get('volumeNum') or 0.0, 'tokens': m.get('clobTokenIds'),
                  'feeType': m.get('feeType'), 'clock_gap_h': round((end - T) / HOUR, 2)})
        rows.append(r)
    return rows, skipped


def cmd_universe(args):
    out = Path(args.out)
    rows, skipped = study_markets()
    by = collections.Counter((r['kind'], r['coin']) for r in rows)
    # fetch set: every BTC/ETH touch market; a hashed 30% of BTC/ETH strike and range events (whole events)
    fetch = []
    for r in rows:
        if r['coin'] not in ('BTC', 'ETH') or r['T'] < T_LO:
            continue
        if r['kind'].startswith('touch') or stable_u('pmco:%s' % r['event']) < args.frac:
            fetch.append(r['id'])
    write_gz(out / 'raw' / 'markets.json.gz', rows)
    write_json(out / 'raw' / 'fetch_set.json', fetch)
    gaps = collections.Counter((r['kind'], r['clock_gap_h']) for r in rows if r['T'] >= T_LO)
    update_manifest(out, 'universe', {
        'at': utc(), 'source': str(STORED / 'raw' / 'universe.json.gz') + ' (gamma /markets/keyset, closed, volume >= $10k,'
                                                                          ' fetched 2026-10-09)',
        'markets': len(rows), 'by_kind_coin': {'%s|%s' % k: v for k, v in sorted(by.items())},
        'skipped': dict(skipped), 'fetch_set': len(fetch), 'strike_range_event_fraction': args.frac,
        'endDate_minus_clock_hours_top': {'%s|%s' % k: v for k, v in gaps.most_common(12)}})
    print(json.dumps({'markets': len(rows), 'fetch': len(fetch), 'by': {'%s|%s' % k: v for k, v in by.items()},
                      'skipped': dict(skipped), 'gaps': {'%s|%s' % k: v for k, v in gaps.most_common(12)}}))
    return 0


# ------------------------------------------------------------------------------------------------ spot

SYMBOLS = {'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT', 'XRP': 'XRPUSDT'}


def cmd_spot(args):
    out = Path(args.out)
    http = Http(interval=0.2)
    t0 = time.time()
    res = {}
    for coin, sym in SYMBOLS.items():
        rows = []
        start = int(parse_ts('2024-01-01T00:00:00Z') * 1000)
        end = int(time.time() * 1000)
        while start < end:
            d = http.request(BINANCE + 'klines?' + urllib.parse.urlencode({'symbol': sym, 'interval': '1h',
                                                                            'startTime': start, 'limit': 1000}))
            if not isinstance(d, list) or not d:
                break
            for k in d:
                rows.append([int(k[0]) // 1000, float(k[1]), float(k[2]), float(k[3]), float(k[4])])
            start = int(d[-1][0]) + 3600 * 1000
        write_gz(out / 'raw' / 'spot' / ('%s_1h.json.gz' % coin), rows)
        res[coin] = {'symbol': sym, 'hours': len(rows), 'first': utc(rows[0][0]) if rows else None,
                     'last': utc(rows[-1][0]) if rows else None}
    update_manifest(out, 'spot', {'at': utc(t0), 'source': BINANCE + 'klines interval=1h (open, high, low, close)',
                                  'series': res, 'http': http.stats()})
    print(json.dumps(res))
    return 0


def load_spot(out, coin):
    p = Path(out) / 'raw' / 'spot' / ('%s_1h.json.gz' % coin)
    return read_gz(p) if p.exists() else []


# ------------------------------------------------------------------------------------------------ decision times

def decision_times(m):
    """[(horizon_hours, t)] for a market, pre-registered per kind."""
    end = m['T']
    return [(h, end - h * HOUR) for h in HORIZONS[m['kind']]]


def needed_hours(markets):
    """Every hour at which a smile is needed: decision times and decision + 1h (late entry), floored to the hour."""
    hrs = set()
    for m in markets:
        for h, t in decision_times(m):
            if m.get('start') and t < m['start']:
                continue
            if t >= m['close']:
                continue
            for x in (t, t + HOUR):
                hrs.add(int(x // HOUR) * 3600)
    return sorted(hrs)


# ------------------------------------------------------------------------------------------------ deribit

def deribit_path(out, cur, hour_ts):
    d = dt.datetime.fromtimestamp(hour_ts, dt.timezone.utc)
    return Path(out) / 'raw' / 'deribit' / cur / d.strftime('%Y%m') / (d.strftime('%Y%m%d%H') + '.json.gz')


def compact_trade(x):
    return [x['timestamp'], x['instrument_name'], x['price'], x['mark_price'], x['iv'], x['index_price'],
            x.get('amount')]


def fetch_window(http, cur, a_ms, b_ms):
    rows, start, n = [], a_ms, 0
    while True:
        q = {'currency': cur, 'kind': 'option', 'start_timestamp': start, 'end_timestamp': b_ms, 'count': 1000,
             'include_old': 'true', 'sorting': 'asc'}
        d = http.request(DERIBIT + 'get_last_trades_by_currency_and_time?' + urllib.parse.urlencode(q))
        n += 1
        if not isinstance(d, dict) or '__error__' in d:
            return None, n
        r = d.get('result') or {}
        tr = r.get('trades') or []
        rows.extend(compact_trade(x) for x in tr)
        if not r.get('has_more') or not tr:
            break
        start = tr[-1]['timestamp'] + 1 if tr[-1]['timestamp'] + 1 > start else start + 1
        if n > 40:
            break
    return rows, n


def cmd_deribit(args):
    out = Path(args.out)
    markets = read_gz(out / 'raw' / 'markets.json.gz')
    fetch = set(json.loads((out / 'raw' / 'fetch_set.json').read_text()))
    ms = [m for m in markets if m['id'] in fetch]
    hours = needed_hours(ms)
    hours = [h for h in hours if h < time.time() - 2 * HOUR]
    if args.limit:
        hours = hours[:args.limit]
    http = Http(interval=args.interval)
    t0 = time.time()
    width = {'BTC': 30 * 60, 'ETH': 60 * 60, 'USDC': 3 * 3600}
    jobs = [(h, cur) for h in hours for cur in args.currencies.split(',') if not deribit_path(out, cur, h).exists()]

    def one(job):
        h, cur = job
        rows, n = fetch_window(http, cur, int((h - width[cur]) * 1000), int(h * 1000) - 1)
        if rows is None:
            return 0
        write_gz(deribit_path(out, cur, h), rows)
        return 1

    done = errs = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, ok in enumerate(ex.map(one, jobs)):
            done += ok
            errs += 1 - ok
            if i % 500 == 0:
                print(json.dumps({'i': i, 'of': len(jobs), 'written': done, 'errors': errs,
                                  'elapsed_s': round(time.time() - t0), **http.stats()}), flush=True)
    update_manifest(out, 'deribit', {
        'at': utc(t0), 'finished_at': utc(), 'source': DERIBIT + 'get_last_trades_by_currency_and_time (kind=option, '
                                                                  'include_old=true)',
        'window_before_hour_s': width, 'hours_needed': len(hours), 'files_written': done, 'errors': errs,
        'http': http.stats()})
    print(json.dumps({'hours': len(hours), 'written': done, 'errors': errs, **http.stats()}))
    return 0


MON3 = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV',
                                        'DEC'])}


def parse_instrument(name):
    """'BTC-10OCT25-118000-P' or 'SOL_USDC-10OCT25-150-C' -> (underlying, expiry_ts at 08:00 UTC, strike, 'C'/'P')."""
    parts = name.split('-')
    if len(parts) != 4:
        return None
    u, e, k, cp = parts
    try:
        day, mon, yr = int(e[:-5]), MON3[e[-5:-2]], 2000 + int(e[-2:])
        exp = dt.datetime(yr, mon, day, 8, tzinfo=dt.timezone.utc).timestamp()
        strike = float(k.replace('d', '.'))
    except (KeyError, ValueError):
        return None
    return u, exp, strike, cp


def build_surface(trades, t, underlying, inverse=True, min_expiry_h=2.0):
    """Surface at time t from compact trades [ts_ms, name, price, mark, iv, index, amount] with ts < t.

    The forward of each expiry comes from near-the-money trades (|ln K/S| < 5%): price x F = Black76(F) for inverse
    options, put-call parity on marks otherwise (USDC options: price is in USD, F from the median of call-put pairs
    or the index). Each instrument's latest mark price is inverted to a vol at that forward. Expiries with fewer
    than 3 strikes are dropped."""
    by_exp = collections.defaultdict(list)
    spot = None
    last_ts = -1
    for tr in trades:
        ts = tr[0] / 1000.0
        if ts >= t:
            continue
        pi = parse_instrument(tr[1])
        if not pi or pi[0] != underlying:
            continue
        if tr[0] > last_ts:
            last_ts, spot = tr[0], tr[5]
        by_exp[pi[1]].append((ts, pi[2], pi[3], tr[2], tr[3], tr[4], tr[5]))
    if spot is None:
        return None
    smiles = []
    for exp, rows in by_exp.items():
        T = (exp - t) / YEAR
        if T * YEAR < min_expiry_h * HOUR:
            continue
        fs = []
        for ts, K, cp, price, mark, iv, idx in rows:
            if abs(math.log(K / idx)) > 0.05 or not iv:
                continue
            Te = (exp - ts) / YEAR
            if inverse:
                f = forward_from_inverse(price, K, iv / 100.0, Te, cp, idx)
                if f:
                    fs.append(f / idx)
        if inverse and len(fs) < 2:
            continue
        F = spot * (statistics.median(fs) if fs else 1.0)
        latest = {}
        for ts, K, cp, price, mark, iv, idx in rows:
            key = (K, cp)
            if key not in latest or ts > latest[key][0]:
                latest[key] = (ts, mark, idx)
        pts = []
        for (K, cp), (ts, mark, idx) in latest.items():
            # use the OTM side only (the ITM mark is mostly intrinsic and inverts badly)
            if (cp == 'C' and K < F) or (cp == 'P' and K > F):
                continue
            usd = mark * F if inverse else mark
            v = implied_vol(usd, F, K, T, cp)
            if v and 0.05 < v < 4.0:
                pts.append((math.log(K / F), v))
        if len({round(k, 6) for k, _ in pts}) < 3:
            continue
        smiles.append(Smile(T, F, pts))
    if not smiles:
        return None
    return Surface(t, spot, smiles)


# ------------------------------------------------------------------------------------------------ polymarket prices

def own_price_path(out, mid, kind):
    return Path(out) / 'raw' / 'prices' / str(mid)[-2:] / ('%s_%s.json.gz' % (mid, kind))


def price_windows(m):
    """Hourly windows to fetch: up to 14.5 days before min(close, T) (+1h); a second earlier window for monthly
    touch markets (their weekly checkpoints reach 21 days before the window end)."""
    end = min(m['close'], m['T']) + HOUR
    w = [('h1', end - 14.5 * DAY, end)]
    if m['kind'] == 'touch_month' and end - 14.5 * DAY > m['T'] - 22 * DAY:
        e2 = end - 14.5 * DAY
        w.append(('h2', max(e2 - 14.5 * DAY, m['T'] - 23 * DAY), e2 + HOUR))
    return w


def cmd_prices(args):
    out = Path(args.out)
    markets = {m['id']: m for m in read_gz(out / 'raw' / 'markets.json.gz')}
    fetch = json.loads((out / 'raw' / 'fetch_set.json').read_text())
    order = {'touch_month': 0, 'touch_week': 1, 'touch_day': 2, 'strike': 3, 'range': 4}
    ids = sorted(fetch, key=lambda i: (order[markets[i]['kind']], stable_u('ord:%s' % i)))
    if args.limit:
        ids = ids[:args.limit]
    http = Http(interval=args.interval)
    t0 = time.time()
    errs, n = [], 0

    def one(mid):
        m = markets[mid]
        tok = m['tokens'][0]
        res = []
        for tag, a, b in price_windows(m):
            p = own_price_path(out, mid, tag)
            if p.exists():
                continue
            s, err = fetch_prices(http, tok, coarse=False, start=a, end=b, fidelity=60)
            res.append(err)
            if s is not None:
                write_gz(p, s)
        return mid, res

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for j, (mid, res) in enumerate(ex.map(one, ids)):
            n += len(res)
            errs.extend({'id': mid, 'err': e} for e in res if e)
            if j % 500 == 0:
                print(json.dumps({'i': j, 'of': len(ids), 'kind': markets[mid]['kind'], 'errors': len(errs),
                                  'elapsed_s': round(time.time() - t0), **http.stats()}), flush=True)
    update_manifest(out, 'prices', {'at': utc(t0), 'finished_at': utc(), 'markets': len(ids), 'requests': n,
                                    'errors': len(errs), 'error_examples': errs[:10], 'http': http.stats(),
                                    'source': 'https://clob.polymarket.com/prices-history (YES token, fidelity 60, '
                                              'windows of 14.5 days ending one hour after min(close, resolution))'})
    print(json.dumps({'markets': len(ids), 'requests': n, 'errors': len(errs), **http.stats()}))
    return 0


def load_pm_series(out, m):
    pts = []
    for tag in ('h2', 'h1'):
        p = own_price_path(out, m['id'], tag)
        if p.exists():
            pts.extend(read_gz(p))
    if not pts:
        p = price_path(STORED, m['id'], 'f')
        if p.exists():
            pts.extend(read_gz(p))
    pts = sorted({(int(a), float(b)) for a, b in pts})
    return [list(x) for x in pts]



# ------------------------------------------------------------------------------------------------ live snapshot

def deribit_live_surface(currency, underlying, now, inverse=True, coin=None):
    """Live surface from Deribit book summaries: each option's mark_iv at its own underlying (the expiry's
    forward). OTM side only, like the historical builder."""
    d = http_json(DERIBIT_LIVE + 'get_book_summary_by_currency?' + urllib.parse.urlencode(
        {'currency': currency, 'kind': 'option'}), 'deribit')
    idx = http_json(DERIBIT_LIVE + 'get_index_price?' + urllib.parse.urlencode(
        {'index_name': ('%s_usd' % underlying.lower()) if inverse else ('%s_usdc' % (coin or underlying).lower())}),
        'deribit')
    spot = ((idx or {}).get('result') or {}).get('index_price')
    by = collections.defaultdict(list)
    fwd = {}
    for r in (d or {}).get('result') or []:
        pi = parse_instrument(r.get('instrument_name') or '')
        if not pi or pi[0] != underlying:
            continue
        u, exp, K, cp = pi
        F = r.get('underlying_price')
        iv = r.get('mark_iv')
        if not F or not iv or exp - now < 2 * HOUR:
            continue
        fwd[exp] = F
        if (cp == 'C' and K < F) or (cp == 'P' and K > F):
            continue
        by[exp].append((math.log(K / F), iv / 100.0))
    smiles = [Smile((exp - now) / YEAR, fwd[exp], pts) for exp, pts in by.items() if len(pts) >= 3]
    if not smiles or not spot:
        return None, d
    return Surface(now, spot, smiles), d


def book_metrics(book):
    """Best bid/ask, midpoint, half-spread and USD depth at the touch and within 2c, for one YES book."""
    asks, bids = book.get('asks') or [], book.get('bids') or []
    if not asks or not bids:
        return None
    a, b = asks[0][0], bids[0][0]
    return {'ask': a, 'bid': b, 'mid': 0.5 * (a + b), 'hs': 0.5 * (a - b),
            'ask_usd_touch': a * asks[0][1], 'bid_usd_touch': (1 - b) * bids[0][1],
            'ask_usd_2c': sum(p * q for p, q in asks if p <= a + 0.02 + 1e-9),
            'bid_usd_2c': sum((1 - p) * q for p, q in bids if p >= b - 0.02 - 1e-9)}


def cmd_live(args):
    out = Path(args.out)
    now = time.time()
    http = Http(interval=max(0.22, args.interval))
    evs = paginate_events(http, {'closed': 'false', 'active': 'true', 'tag_slug': 'crypto-prices',
                                 'end_date_max': utc(now + 40 * DAY).replace('+00:00', 'Z')})
    rows = []
    for e in evs:
        for mk in e.get('markets') or []:
            info = classify(mk.get('question'))
            if not info or not mk.get('acceptingOrders') or mk.get('closed'):
                continue
            end = parse_ts(mk.get('endDate'))
            if not end:
                continue
            ws, T = resolution_clock(info, end)
            toks = jload(mk.get('clobTokenIds'), [])
            if len(toks) != 2 or T is None or T <= now:
                continue
            r = dict(info)
            created = parse_ts(mk.get('acceptingOrdersTimestamp') or mk.get('startDate') or mk.get('createdAt'))
            if ws is not None and created and created > ws:
                ws = created
            r.update({'id': mk.get('id'), 'question': mk.get('question'), 'event': e.get('id'), 'T': T, 'ws': ws,
                      'yes': toks[0], 'no': toks[1], 'vol': fnum(mk.get('volumeNum')) or fnum(mk.get('volume')),
                      'vol24': fnum(mk.get('volume24hr')), 'fee': mk.get('feeSchedule'), 'feeType': mk.get('feeType'),
                      'rules': (mk.get('description') or '')[:600], 'resolutionSource': mk.get('resolutionSource')})
            rows.append(r)
    books = fetch_books(http, sorted({r['yes'] for r in rows}))
    for r in rows:
        b = books.get(r['yes'])
        r['book'] = book_metrics(b) if b else None
    # Deribit live surfaces and Binance spot
    surf, raw_d = {}, {}
    for coin, cur, inv in (('BTC', 'BTC', True), ('ETH', 'ETH', True), ('SOL', 'USDC', False), ('XRP', 'USDC', False)):
        under = coin if inv else '%s_USDC' % coin
        sf, raw = deribit_live_surface(cur, under, now, inverse=inv, coin=coin)
        surf[coin] = sf
        raw_d[coin] = raw
    spot = {}
    for coin, sym in SYMBOLS.items():
        d = http.request(BINANCE + 'ticker/price?symbol=' + sym)
        spot[coin] = fnum((d or {}).get('price')) if isinstance(d, dict) else None
    kl = {coin: load_spot(out, coin) for coin in SYMBOLS}
    for r in rows:
        sf = surf.get(r['coin'])
        S = spot.get(r['coin'])
        r['model'] = None
        if not sf or not S or not r['book']:
            continue
        ratio = S / sf.spot
        running = None
        if r['kind'].startswith('touch') and r['ws']:
            hs = [k for k in kl[r['coin']] if r['ws'] <= k[0] < now]
            running = (max([k[2] for k in hs] + [S]), min([k[3] for k in hs] + [S])) if hs else (S, S)
        r['model'] = model_prob(r, sf, now, S, ratio, running)
        r['spot'] = S
        r['ratio'] = ratio
        r['sigma_atm'] = sf.vol(0.0, max(1e-6, (r['T'] - now) / YEAR))
    # Kalshi crypto markets
    kal = []
    for ser in ('KXBTCD', 'KXETHD', 'KXBTC', 'KXETH', 'KXBTCMAXMON', 'KXBTCMINMON', 'KXETHMAXMON', 'KXETHMINMON',
                'KXBTCMAXW', 'KXBTCMAXM'):
        cur = None
        for _ in range(20):
            q = {'series_ticker': ser, 'status': 'open', 'limit': 1000}
            if cur:
                q['cursor'] = cur
            d = http_json(KALSHI + 'markets?' + urllib.parse.urlencode(q), 'kalshi')
            if not d:
                break
            for mk in d.get('markets') or []:
                mk['_series'] = ser
                kal.append(mk)
            cur = d.get('cursor')
            if not cur:
                break
    snap = {'at': utc(now), 'polymarket': rows, 'kalshi': kal, 'binance_spot': spot,
            'deribit_spot': {c: (s.spot if s else None) for c, s in surf.items()},
            'deribit_expiries': {c: ([round(x.T * 365, 3) for x in s.smiles] if s else []) for c, s in surf.items()},
            'http': http.stats()}
    write_gz(out / 'raw' / 'live' / ('snap_%d.json.gz' % int(now)), snap)
    write_gz(out / 'raw' / 'live' / ('deribit_%d.json.gz' % int(now)), raw_d)
    update_manifest(out, 'live_%d' % int(now), {
        'at': utc(now), 'polymarket_markets': len(rows), 'with_book': sum(1 for r in rows if r['book']),
        'with_model': sum(1 for r in rows if r.get('model') is not None), 'kalshi_markets': len(kal),
        'sources': [GAMMA_EVENTS, 'https://clob.polymarket.com/books', DERIBIT_LIVE + 'get_book_summary_by_currency',
                    BINANCE + 'ticker/price', KALSHI + 'markets'], 'http': http.stats()})
    print(json.dumps({'pm': len(rows), 'books': sum(1 for r in rows if r['book']),
                      'model': sum(1 for r in rows if r.get('model') is not None), 'kalshi': len(kal),
                      'spot': spot, **http.stats()}))
    return 0


GAMMA_EVENTS = 'https://gamma-api.polymarket.com/events/keyset (tag_slug=crypto-prices)'


# ------------------------------------------------------------------------------------------------ analysis helpers

class SpotPath:
    """Binance 1h klines [t, open, high, low, close]."""

    def __init__(self, rows):
        self.rows = rows
        self.t = [r[0] for r in rows]
        self.by = {r[0]: r for r in rows}

    def open_at(self, t):
        r = self.by.get(int(t // HOUR) * 3600)
        return r[1] if r else None

    def running(self, a, b):
        """(max high, min low) over the hours [a, b); None when no hour is covered."""
        i, j = bisect.bisect_left(self.t, a), bisect.bisect_left(self.t, b)
        seg = self.rows[i:j]
        if not seg:
            return None
        return max(r[2] for r in seg), min(r[3] for r in seg)

    def closes(self, a, b):
        i, j = bisect.bisect_left(self.t, a), bisect.bisect_left(self.t, b)
        return [(r[0], r[4]) for r in self.rows[i:j]]


def mid_at(series, t, lag=120, max_stale=3 * DAY):
    """Polymarket hourly points land within a minute or two after the hour (pm_crossvenue alignment fix), so the
    point stamped up to `lag` seconds after t is the price at t."""
    return as_of(series, t + lag, max_stale=max_stale)


def moneyness_z(m, F, sigma, T):
    if not F or not sigma or T <= 0:
        return None
    K = m['K'] if 'K' in m else math.sqrt(m['L'] * m['U'])
    return math.log(K / F) / (sigma * math.sqrt(T))


def z_bucket(z):
    if z is None:
        return 'na'
    a = abs(z)
    return '<0.5sd' if a < 0.5 else '0.5-1sd' if a < 1 else '1-2sd' if a < 2 else '>2sd'


def logit(p):
    p = min(1 - 1e-4, max(1e-4, p))
    return math.log(p / (1 - p))


def floor_tick(x, tick=TICK):
    return math.floor(x / tick + 1e-9) * tick


def half_spread_table(out):
    """Median live half-spread of crypto strike/range/touch books by (group, price band), pooled over the live
    snapshots; each YES book counts for the band of its midpoint and, mirrored, for the band of 1 - mid (the NO
    side's price) - the two sides share one book."""
    snaps = sorted((Path(out) / 'raw' / 'live').glob('snap_*.json.gz'))
    acc = collections.defaultdict(list)
    for sp in snaps:
        sn = read_gz(sp)
        for r in sn['polymarket']:
            b = r.get('book')
            if not b or b['hs'] <= 0 or b['hs'] > 0.25:
                continue
            g = 'terminal' if r['kind'] in ('strike', 'range') else 'touch'
            for px in (b['mid'], 1 - b['mid']):
                acc[(g, band_key(px))].append(b['hs'])
                acc[('all', band_key(px))].append(b['hs'])
    return {'%s|%s' % k: {'n': len(v), 'median': statistics.median(v), 'p75': sorted(v)[int(0.75 * (len(v) - 1))]}
            for k, v in acc.items()}


def hs_lookup(table, kind, price, default=0.01):
    g = 'terminal' if kind in ('strike', 'range') else 'touch'
    for key in ('%s|%s' % (g, band_key(price)), 'all|%s' % band_key(price)):
        r = table.get(key)
        if r and r['n'] >= 5:
            return r['median']
    return default


# ------------------------------------------------------------------------------------------------ decisions

def build_decisions(out, now):
    markets = read_gz(Path(out) / 'raw' / 'markets.json.gz')
    fetch = set(json.loads((Path(out) / 'raw' / 'fetch_set.json').read_text()))
    spot = {c: SpotPath(load_spot(out, c)) for c in ('BTC', 'ETH')}
    cache = {}
    stats = collections.Counter()

    def surface(coin, t):
        h = int(t // HOUR) * 3600
        key = (coin, h)
        if key not in cache:
            p = deribit_path(out, coin, h)
            cache[key] = build_surface(read_gz(p), h, coin) if p.exists() else 'missing'
        return cache[key]

    decs = []
    for m in markets:
        if m['coin'] not in ('BTC', 'ETH'):
            continue
        if m['id'] not in fetch and not price_path(STORED, m['id'], 'f').exists():
            continue   # the hashed fetch set plus every market of the 2026-10-09 stratified sample
        series = load_pm_series(out, m)
        if not series:
            stats['no_series'] += 1
            continue
        sp = spot[m['coin']]
        for h, t in decision_times(m):
            if t < T_LO or t >= now - 2 * HOUR:
                continue
            if t >= m['close']:
                stats['closed_before_decision'] += 1
                continue
            mid = mid_at(series, t)
            if mid is None:
                stats['no_price_at_t'] += 1
                continue
            sf = surface(m['coin'], t)
            if sf == 'missing' or sf is None:
                stats['no_surface' if sf is None else 'no_deribit_file'] += 1
                continue
            S = sp.open_at(t)
            if not S:
                stats['no_spot'] += 1
                continue
            running = None
            if m['kind'].startswith('touch'):
                running = sp.running(m['ws'], t) if m['ws'] < t else None
                hi, lo = running if running else (S, S)
                if (m['direction'] == 'up' and max(hi, S) >= m['K']) or (m['direction'] == 'down' and min(lo, S) <= m['K']):
                    stats['already_touched'] += 1
                    continue
            ratio = S / sf.spot
            p = model_prob(m, sf, t, S, ratio, running)
            if p is None:
                stats['no_model'] += 1
                continue
            T = (m['T'] - t) / YEAR
            F = sf.forward(T) * ratio
            Kref = m['K'] if 'K' in m else math.sqrt(m['L'] * m['U'])
            sig = sf.vol(math.log(Kref / F), T)
            # late entry (+1h) and the maker path (hourly midpoints after t, up to 7h)
            t1 = t + HOUR
            mid1 = mid_at(series, t1) if t1 < m['close'] else None
            sf1 = surface(m['coin'], t1)
            p1 = None
            if mid1 is not None and sf1 not in ('missing', None):
                S1 = sp.open_at(t1)
                if S1:
                    run1 = sp.running(m['ws'], t1) if (m['kind'].startswith('touch') and m['ws'] < t1) else None
                    p1 = model_prob(m, sf1, t1, S1, S1 / sf1.spot, run1)
            path = []
            for k in range(1, 8):
                tk = t + k * HOUR
                path.append(mid_at(series, tk) if tk < min(m['close'], m['T']) else None)
            decs.append({'id': m['id'], 'event': m['event'], 'coin': m['coin'], 'kind': m['kind'], 'h': h, 't': t,
                         'T': m['T'], 'close': max(t + 60, min(m['close'], m['T'] + DAY)), 'pay': m['pay'],
                         'mid': mid, 'p': p, 'mid1': mid1, 'p1': p1, 'path': path, 'S': S, 'F': F, 'sigma': sig,
                         'z': moneyness_z(m, F, sig, T), 'vol': m['vol'], 'life_days': max(1.0, (m['close'] - (m['start'] or m['close'] - 7 * DAY)) / DAY),
                         'direction': m['direction'], 'K': m.get('K'), 'L': m.get('L'), 'U': m.get('U'), 'ws': m.get('ws')})
            stats['decisions'] += 1
    return decs, stats


# ------------------------------------------------------------------------------------------------ trades

def make_trade(d, side, exec_, thr, hs_table, late=False):
    """One variant's trade at decision d, or None: a dict with t (entry), close, w, event, pay (of the side bought),
    p (price paid per share, fee included), ret (per dollar), side, id.

    taker: buy the side whose model value exceeds its all-in cost (ask + fee) by at least thr at the decision time;
           late entry keeps that selection and pays the ask one hour later.
    maker: rest a bid at min(model - thr, ask - tick) on the chosen side(s) for six hours; it fills at its limit
           only when a later hourly midpoint prints a tick through it; with both sides resting, the first fill
           counts and the other order is cancelled (a both-sides fill would be a locked profit: not counted)."""
    mid = d['mid1'] if late else d['mid']
    if mid is None:
        return None
    p = d['p']
    t0 = d['t'] + (HOUR if late else 0)
    path = d['path'][1:7] if late else d['path'][:6]
    sides = ['yes', 'no'] if side == 'both' else [side]
    best = None
    for sd in sides:
        px_mid = mid if sd == 'yes' else 1.0 - mid
        q = p if sd == 'yes' else 1.0 - p
        pay = d['pay'] if sd == 'yes' else 1.0 - d['pay']
        hs = hs_lookup(hs_table, d['kind'], px_mid)
        if exec_ == 'taker':
            sig_mid = d['mid'] if sd == 'yes' else 1.0 - d['mid']
            sig_cost = taker_cost(sig_mid, hs_lookup(hs_table, d['kind'], sig_mid))
            if q - sig_cost < thr:      # the signal is always the decision-time one
                continue
            cost = taker_cost(px_mid, hs)
            return {'t': t0, 'close': max(t0 + 60, d['close']), 'w': 1.0, 'event': d['event'], 'pay': pay,
                    'p': cost, 'ret': pay / cost - 1.0, 'side': sd, 'id': d['id']}
        limit = min(floor_tick(q - thr), floor_tick(px_mid + hs - TICK))
        if limit < 0.01:
            continue
        side_path = [None if x is None else (x if sd == 'yes' else 1.0 - x) for x in path]
        i = maker_fill(limit, side_path)
        if i is None:
            continue
        tf = t0 + (i + 1) * HOUR
        tr = {'t': tf, 'close': max(tf + 60, d['close']), 'w': 1.0, 'event': d['event'], 'pay': pay, 'p': limit,
              'ret': pay / limit - 1.0, 'side': sd, 'id': d['id']}
        if best is None or tr['t'] < best['t']:
            best = tr
    return best


def variant_name(kind, h, thr, side, exec_):
    return '%s|%dh|thr%.2f|%s|%s' % (kind, h, thr, side, exec_)


def all_variants():
    out = []
    for kind, hs in HORIZONS.items():
        for h in hs:
            for thr in THRESHOLDS:
                for side in SIDES:
                    for ex in EXECS:
                        out.append((kind, h, thr, side, ex))
    return out


def protocol(trades_by_variant, t_lo, t_hi, cutoff):
    series, parts = {}, {}
    n_is = None
    for name, trades in trades_by_variant.items():
        ins = [t for t in trades if t['close'] < cutoff]
        oos = [t for t in trades if t['t'] >= cutoff]
        r_in, r_oos = [t['ret'] for t in ins], [t['ret'] for t in oos]
        s_in, _, _ = daily_series(ins, r_in, t_lo, cutoff - 1) if ins else ([], 0, 0)
        s_oos, _, _ = daily_series(oos, r_oos, cutoff, t_hi) if oos else ([], 0, 0)
        if not s_in:
            s_in = [0.0] * (int((cutoff - 1) // DAY) - int(t_lo // DAY) + 1)
        if not s_oos:
            s_oos = [0.0] * (int(t_hi // DAY) - int(cutoff // DAY) + 1)
        n_is = len(s_in)
        series[name] = s_in + s_oos
        parts[name] = {'in': summarize(ins, r_in) if ins else {'n': 0}, 'oos': summarize(oos, r_oos) if oos else {'n': 0}}
    frac = n_is / len(next(iter(series.values())))
    sel = B.choose_then_test(series, frac=frac, periods_per_year=365, key='sharpe')
    return sel, parts, series


# ------------------------------------------------------------------------------------------------ hedge overlay

def model_delta(d, S, tau, sigma, F_ratio=1.0):
    """dP(YES)/dS per share, with the vol held at the decision-time barrier/strike vol (sticky strike)."""
    eps = 0.002
    def P(s):
        if tau <= 0:
            return None
        if d['kind'] == 'strike':
            v = sigma * math.sqrt(tau)
            pa = _N.cdf((math.log(s / d['K']) - 0.5 * v * v) / v)
            return pa if d['direction'] == 'above' else 1 - pa
        if d['kind'] == 'range':
            v = sigma * math.sqrt(tau)
            return (_N.cdf((math.log(s / d['L']) - 0.5 * v * v) / v) - _N.cdf((math.log(s / d['U']) - 0.5 * v * v) / v))
        return touch_prob(s, d['K'], tau, sigma, 0.0)
    a, b = P(S * (1 + eps)), P(S * (1 - eps))
    if a is None or b is None:
        return 0.0
    return (a - b) / (2 * eps * S)


def hedged_return(tr, d, spot, fee=HEDGE_FEE):
    """Unhedged return plus the P&L of an hourly delta hedge in the perp (Binance hourly closes), per $1 staked."""
    shares = 1.0 / tr['p']
    sign = 1.0 if tr['side'] == 'yes' else -1.0
    pts = spot.closes(int(tr['t'] // HOUR) * 3600, d['T'])
    if len(pts) < 2:
        return tr['ret']
    pnl, prev = 0.0, 0.0
    for (ta, sa), (tb, sb) in zip(pts[:-1], pts[1:]):
        tau = (d['T'] - ta) / YEAR
        if d['kind'].startswith('touch'):
            if (d['direction'] == 'up' and sa >= d['K']) or (d['direction'] == 'down' and sa <= d['K']):
                break
        delta = sign * model_delta(d, sa, tau, d['sigma'])
        pnl += -delta * (sb - sa) - fee * abs(delta - prev) * sa
        prev = delta
    pnl -= fee * abs(prev) * pts[-1][1]
    return tr['ret'] + shares * pnl


# ------------------------------------------------------------------------------------------------ analysis

def calibration_tables(decs):
    """Model and market against outcomes, by kind and horizon: Brier, log loss, logistic slope of the outcome on
    logit(probability) (1 = calibrated, < 1 over-confident), and reliability by model decile."""
    from polymarket_history import logistic_fit
    groups = collections.defaultdict(list)
    for d in decs:
        groups[(d['kind'], d['h'])].append(d)
        groups[(d['kind'], 'all')].append(d)
        groups[('all', 'all')].append(d)
    res = {}
    for (k, h), ds in sorted(groups.items(), key=lambda x: str(x[0])):
        y = [d['pay'] for d in ds]
        pm = [d['p'] for d in ds]
        mk = [d['mid'] for d in ds]
        n = len(ds)
        def brier(ps):
            return sum((p - yy) ** 2 for p, yy in zip(ps, y)) / n
        def ll(ps):
            return -sum(yy * math.log(max(1e-4, p)) + (1 - yy) * math.log(max(1e-4, 1 - p)) for p, yy in zip(ps, y)) / n
        yb = [1.0 if v >= 0.5 else 0.0 for v in y]
        fm = logistic_fit([logit(p) for p in pm], yb, [1.0] * n)
        fk = logistic_fit([logit(p) for p in mk], yb, [1.0] * n)
        both = [dd for dd in ds if abs(dd['mid'] - dd['p']) >= 0.05]
        res['%s|%s' % (k, h)] = {
            'n': n, 'events': len({d['event'] for d in ds}), 'mean_outcome': sum(y) / n,
            'mean_model': sum(pm) / n, 'mean_market': sum(mk) / n,
            'brier_model': brier(pm), 'brier_market': brier(mk), 'logloss_model': ll(pm), 'logloss_market': ll(mk),
            'slope_model': fm[1] if fm else None, 'intercept_model': fm[0] if fm else None,
            'slope_market': fk[1] if fk else None, 'intercept_market': fk[0] if fk else None,
            'disagree_5c': {'n': len(both),
                            'mean_outcome_minus_market': (sum(dd['pay'] - dd['mid'] for dd in both) / len(both)) if both else None,
                            'mean_model_minus_market': (sum(dd['p'] - dd['mid'] for dd in both) / len(both)) if both else None,
                            'share_outcome_on_model_side': (sum(1 for dd in both if (dd['pay'] - dd['mid']) * (dd['p'] - dd['mid']) > 0) / len(both)) if both else None}}
        if k != 'all' and h == 'all':
            bins = collections.defaultdict(list)
            for d in ds:
                bins[min(9, int(d['p'] * 10))].append(d)
            res['%s|%s' % (k, h)]['reliability_model'] = {
                '%.1f' % (b / 10): {'n': len(v), 'model': sum(x['p'] for x in v) / len(v),
                                    'market': sum(x['mid'] for x in v) / len(v),
                                    'outcome': sum(x['pay'] for x in v) / len(v)} for b, v in sorted(bins.items())}
    return res


def mad_tables(decs, hs_table):
    g = collections.defaultdict(list)
    for d in decs:
        zb = z_bucket(d['z'])
        for key in ((d['kind'], d['h'], zb), (d['kind'], d['h'], 'all'), (d['kind'], 'all', zb), (d['kind'], 'all', 'all')):
            g[key].append(d)
    res = {}
    for (k, h, zb), ds in sorted(g.items(), key=lambda x: str(x[0])):
        dev = [d['mid'] - d['p'] for d in ds]
        cost = [hs_lookup(hs_table, d['kind'], d['mid']) + pm_fee(d['mid']) for d in ds]
        res['%s|%s|%s' % (k, h, zb)] = {
            'n': len(ds), 'mad': sum(abs(x) for x in dev) / len(ds), 'mean_signed_market_minus_model': sum(dev) / len(ds),
            'median_abs': statistics.median([abs(x) for x in dev]),
            'share_beyond_taker_cost': sum(1 for x, c in zip(dev, cost) if abs(x) > c) / len(ds)}
    return res


def kalshi_model(mk, sf, now, spot_path):
    """Model probability of YES for a Kalshi crypto market (CF Benchmarks index ~ the Deribit USD index, so no
    USDT ratio)."""
    st = mk.get('strike_type')
    T = (parse_ts(mk.get('close_time')) or 0) - now
    if T <= 0 or sf is None:
        return None
    Ty = T / YEAR
    F = sf.forward(Ty)
    def vf(k):
        return sf.vol(k, Ty)
    ser = mk['_series']
    lo, hi = fnum(mk.get('floor_strike')), fnum(mk.get('cap_strike'))
    if 'MAXMON' in ser or 'MINMON' in ser:
        B = lo if st == 'greater' else hi
        if not B:
            return None
        opened = parse_ts(mk.get('open_time')) or now
        run = spot_path.running(opened, now)
        S = sf.spot
        if run and ((st == 'greater' and run[0] >= B) or (st == 'less' and run[1] <= B)):
            return None   # touched on Binance already; the index may differ, so leave it out
        sig = vf(math.log(B / F))
        return touch_prob(S, B, Ty, sig, math.log(F / S) / Ty)
    if st == 'greater' and lo:
        return digital_above(F, lo, Ty, vf)
    if st == 'less' and hi:
        return 1.0 - digital_above(F, hi, Ty, vf)
    if st == 'between' and lo and hi:
        return max(0.0, digital_above(F, lo, Ty, vf) - digital_above(F, hi, Ty, vf))
    return None


def hours_bucket(hrs):
    return '<12h' if hrs < 12 else '12-36h' if hrs < 36 else '36-96h' if hrs < 96 else '96-200h' if hrs < 200 else '>200h'


def live_analysis(out):
    snaps = sorted((Path(out) / 'raw' / 'live').glob('snap_*.json.gz'))
    if not snaps:
        return None
    sn = read_gz(snaps[-1])
    now = parse_ts(sn['at'])
    rows, krows = [], []
    for r in sn['polymarket']:
        b, p = r.get('book'), r.get('model')
        if not b or p is None:
            continue
        hrs = (r['T'] - now) / HOUR
        ask, bid = b['ask'], b['bid']
        e_yes = p - (ask + pm_fee(ask))
        e_no = (1 - p) - ((1 - bid) + pm_fee(1 - bid))
        T = (r['T'] - now) / YEAR
        z = moneyness_z(r, r['spot'], r.get('sigma_atm'), T) if r.get('sigma_atm') else None
        rows.append({'venue': 'polymarket', 'kind': r['kind'], 'coin': r['coin'], 'question': r['question'],
                     'hours': hrs, 'hb': hours_bucket(hrs), 'zb': z_bucket(z), 'mid': b['mid'], 'model': p,
                     'dev': b['mid'] - p, 'edge_yes': e_yes, 'edge_no': e_no, 'ask': ask, 'bid': bid,
                     'depth_yes_touch': b['ask_usd_touch'], 'depth_no_touch': b['bid_usd_touch'],
                     'depth_yes_2c': b['ask_usd_2c'], 'depth_no_2c': b['bid_usd_2c'], 'vol24': r.get('vol24')})
    # Kalshi: rebuild the BTC/ETH live surfaces from the stored Deribit book summaries
    raw_d = read_gz(Path(out) / 'raw' / 'live' / snaps[-1].name.replace('snap_', 'deribit_'))
    surf = {}
    for coin in ('BTC', 'ETH'):
        d = raw_d.get(coin) or {}
        by, fwd = collections.defaultdict(list), {}
        for x in d.get('result') or []:
            pi = parse_instrument(x.get('instrument_name') or '')
            if not pi or pi[0] != coin or not x.get('underlying_price') or not x.get('mark_iv'):
                continue
            u, exp, K, cp = pi
            if exp - now < 2 * HOUR:
                continue
            F = x['underlying_price']
            fwd[exp] = F
            if (cp == 'C' and K < F) or (cp == 'P' and K > F):
                continue
            by[exp].append((math.log(K / F), x['mark_iv'] / 100.0))
        sm = [Smile((e - now) / YEAR, fwd[e], pts) for e, pts in by.items() if len(pts) >= 3]
        surf[coin] = Surface(now, sn['deribit_spot'][coin], sm) if sm else None
    sp = {c: SpotPath(load_spot(out, c)) for c in ('BTC', 'ETH')}
    for mk in sn['kalshi']:
        coin = 'ETH' if 'ETH' in mk['_series'] else 'BTC'
        if mk['_series'] in ('KXBTCD', 'KXETHD', 'KXBTC', 'KXETH') and not mk.get('event_ticker', '').endswith('17'):
            continue   # the 4am and other hourly events are the speed family
        if (parse_ts(mk.get('close_time')) or 0) - now < 6 * HOUR:
            continue
        p = kalshi_model(mk, surf.get(coin), now, sp[coin])
        ya, yb = fnum(mk.get('yes_ask_dollars')), fnum(mk.get('yes_bid_dollars'))
        if p is None or not ya or yb is None or ya <= 0 or ya >= 1:
            continue
        close = parse_ts(mk.get('close_time'))
        hrs = (close - now) / HOUR
        kind = 'touch_month' if ('MAXMON' in mk['_series'] or 'MINMON' in mk['_series']) else (
            'range' if mk.get('strike_type') == 'between' else 'strike')
        midk = 0.5 * (ya + yb) if yb > 0 else ya / 2
        e_yes = p - (ya + kalshi_fee(100, ya) / 100.0)
        na = 1 - yb if yb > 0 else None
        e_no = ((1 - p) - (na + kalshi_fee(100, na) / 100.0)) if na else None
        krows.append({'venue': 'kalshi', 'series': mk['_series'], 'ticker': mk['ticker'], 'kind': kind, 'coin': coin,
                      'hours': hrs, 'hb': hours_bucket(hrs), 'mid': midk, 'model': p, 'dev': midk - p,
                      'edge_yes': e_yes, 'edge_no': e_no, 'ask': ya, 'bid': yb,
                      'depth_yes_touch': ya * (fnum(mk.get('yes_ask_size_fp')) or 0.0),
                      'depth_no_touch': (1 - yb) * (fnum(mk.get('yes_bid_size_fp')) or 0.0), 'spread': ya - yb,
                      'vol24': fnum(mk.get('volume_24h_fp'))})
    def summarize_live(rs, keyf):
        g = collections.defaultdict(list)
        for r in rs:
            for k in keyf(r):
                g[k].append(r)
        out_ = {}
        for k, v in sorted(g.items()):
            ex = [max(r['edge_yes'], r['edge_no'] if r['edge_no'] is not None else -1) for r in v]
            out_[k] = {'n': len(v), 'mad': sum(abs(r['dev']) for r in v) / len(v),
                       'mean_signed_market_minus_model': sum(r['dev'] for r in v) / len(v),
                       'n_exec_edge_pos': sum(1 for e in ex if e > 0), 'n_exec_edge_2c': sum(1 for e in ex if e > 0.02),
                       'n_exec_edge_5c': sum(1 for e in ex if e > 0.05),
                       'usd_touch_where_edge_2c': sum((r['depth_yes_touch'] if r['edge_yes'] >= (r['edge_no'] or -1) else r['depth_no_touch'])
                                                      for r, e in zip(v, ex) if e > 0.02)}
        return out_
    allrows = rows + krows
    res = {'at': sn['at'], 'n_polymarket': len(rows), 'n_kalshi': len(krows),
           'by_venue_kind_hours': summarize_live(allrows, lambda r: ['%s|%s|%s' % (r['venue'], r['kind'], r['hb']),
                                                                    '%s|%s|all' % (r['venue'], r['kind'])]),
           'polymarket_by_kind_z': summarize_live(rows, lambda r: ['%s|%s' % (r['kind'], r['zb'])]),
           'top_edges': sorted([dict(r, best=max(r['edge_yes'], r['edge_no'] or -1)) for r in allrows],
                               key=lambda r: -r['best'])[:25],
           'half_spread_kalshi_median': statistics.median([r['spread'] / 2 for r in krows if r['bid'] > 0]) if krows else None}
    return res


def capacity_and_value(trades, decs_by_id, live_rows, years):
    """$ per year over SSR if each trade is sized at min(USD at the touch on that side for the market type and
    price band, 10% of the market's average daily volume); the touch depth is the live median for the band."""
    depth = collections.defaultdict(list)
    for r in live_rows or []:
        if r.get('venue') != 'polymarket':
            continue
        depth[(r['kind'], band_key(r['ask']))].append(r['depth_yes_touch'])
        depth[(r['kind'], band_key(1 - r['bid']))].append(r['depth_no_touch'])
    def touch_usd(kind, price):
        v = depth.get((kind, band_key(price)))
        return statistics.median(v) if v and len(v) >= 3 else None
    pnl = cap_days = 0.0
    sizes = []
    for tr in trades:
        d = decs_by_id.get((tr['id'], tr.get('h')))
        vol_day = (d['vol'] / d['life_days']) if d else 0.0
        tu = touch_usd(d['kind'], tr['p']) if d else None
        size = min(tu if tu is not None else 0.0, 0.10 * vol_day)
        sizes.append(size)
        pnl += size * tr['ret']
        cap_days += size * max(1.0 / 24, (tr['close'] - tr['t']) / DAY)
    usd_year = pnl / years - SSR * cap_days / 365.0 / years
    return {'trades': len(trades), 'median_size_usd': statistics.median(sizes) if sizes else None,
            'sum_size_usd': sum(sizes), 'pnl_usd': pnl, 'capital_days_usd': cap_days,
            'avg_capital_usd': cap_days / (years * 365.0), 'usd_per_year_over_ssr': usd_year}


def vrp_table(decs, out):
    """Implied vol used by the model (strike or barrier vol) against the realised vol of Binance hourly log returns
    over the decision's remaining window, by kind."""
    sp = {c: SpotPath(load_spot(out, c)) for c in ('BTC', 'ETH')}
    g = collections.defaultdict(list)
    for d in decs:
        pts = sp[d['coin']].closes(int(d['t'] // HOUR) * 3600, d['T'])
        if len(pts) < 12:
            continue
        r2 = sum(math.log(b[1] / a[1]) ** 2 for a, b in zip(pts[:-1], pts[1:]))
        yrs = (pts[-1][0] - pts[0][0]) / YEAR
        if yrs <= 0:
            continue
        g[d['kind']].append((d['sigma'], math.sqrt(r2 / yrs)))
    return {k: {'n': len(v), 'mean_implied': sum(a for a, _ in v) / len(v), 'mean_realised': sum(b for _, b in v) / len(v),
                'median_ratio_realised_to_implied': statistics.median([b / a for a, b in v if a > 0]),
                'share_realised_below_implied': sum(1 for a, b in v if b < a) / len(v)} for k, v in sorted(g.items())}


def cmd_analyze(args):
    out = Path(args.out)
    now = time.time()
    res = {'generated': utc(), 'ssr': SSR, 'cutoff': utc(CUTOFF), 't_lo': utc(T_LO),
           'pre_registration': {'horizons_h': HORIZONS, 'thresholds': THRESHOLDS, 'sides': SIDES, 'execs': EXECS,
                                'maker_life_h': MAKER_LIFE / HOUR, 'taker_fee_rate': PM_RATE,
                                'n_variants': len(all_variants())}}
    hs_table = half_spread_table(out)
    res['half_spread_live'] = hs_table
    decs, st = build_decisions(out, now)
    res['decision_stats'] = dict(st)
    res['decisions_by_kind_h'] = {'%s|%s' % k: v for k, v in sorted(collections.Counter((d['kind'], d['h']) for d in decs).items())}
    write_gz(out / 'raw' / 'decisions.json.gz', decs)
    res['calibration'] = calibration_tables(decs)
    res['mad_history'] = mad_tables(decs, hs_table)
    res['vrp'] = vrp_table(decs, out)
    # variants
    tv = {}
    for v in all_variants():
        kind, h, thr, side, ex = v
        trades = []
        for d in decs:
            if d['kind'] != kind or d['h'] != h:
                continue
            tr = make_trade(d, side, ex, thr, hs_table)
            if tr:
                tr['h'] = h
                trades.append(tr)
        tv[variant_name(*v)] = trades
    sel, parts, series = protocol(tv, T_LO, now, CUTOFF)
    res['protocol'] = {k: v for k, v in sel.items() if k != 'bh_adjusted_p'}
    res['protocol']['bh_adjusted_p_chosen'] = sel['bh_adjusted_p'].get(sel['chosen'])
    res['variants'] = {k: {'in': parts[k]['in'], 'oos': parts[k]['oos'], 'bh_p': sel['bh_adjusted_p'].get(k)}
                       for k in tv}
    chosen = sel['chosen']
    kind, h, thr, side, ex = [x for x in all_variants() if variant_name(*x) == chosen][0]
    ctr = tv[chosen]
    oos = [t for t in ctr if t['t'] >= CUTOFF]
    ins = [t for t in ctr if t['close'] < CUTOFF]
    res['chosen'] = {'name': chosen, 'in': summarize(ins, [t['ret'] for t in ins]) if ins else {'n': 0},
                     'oos': summarize(oos, [t['ret'] for t in oos]) if oos else {'n': 0},
                     'oos_cluster_ci': cluster_bootstrap(oos, [t['ret'] for t in oos]) if oos else None}
    # late entry: the same decisions, entered one hour later at the price then
    dmap = {(d['id'], d['h']): d for d in decs}
    late, base = [], []
    for t in ctr:
        d = dmap[(t['id'], h)]
        lt = make_trade(d, side, ex, thr, hs_table, late=True)
        if lt and t['t'] >= CUTOFF:
            late.append(lt['ret'])
            base.append(t['ret'])
    res['late_entry'] = {'n': len(late), 'mean_ret_original': (sum(base) / len(base)) if base else None,
                         'mean_ret_late': (sum(late) / len(late)) if late else None,
                         'share_kept': (sum(late) / sum(base)) if base and sum(base) != 0 else None}
    # the hedge overlay on the chosen variant
    sp = {c: SpotPath(load_spot(out, c)) for c in ('BTC', 'ETH')}
    hr = []
    for t in oos:
        d = dmap[(t['id'], h)]
        hr.append(hedged_return(t, d, sp[d['coin']]))
    res['hedge_overlay'] = {'n': len(hr), 'mean_unhedged': (sum(t['ret'] for t in oos) / len(oos)) if oos else None,
                            'mean_hedged': (sum(hr) / len(hr)) if hr else None,
                            'sd_unhedged': statistics.pstdev([t['ret'] for t in oos]) if len(oos) > 1 else None,
                            'sd_hedged': statistics.pstdev(hr) if len(hr) > 1 else None}
    # capacity and $/yr out of sample
    live = live_analysis(out)
    res['live'] = {k: v for k, v in (live or {}).items()}
    live_rows = (live or {}).get('top_edges') and None
    snaps = sorted((out / 'raw' / 'live').glob('snap_*.json.gz'))
    lrows = []
    if snaps:
        sn = read_gz(snaps[-1])
        for r in sn['polymarket']:
            if r.get('book'):
                b = r['book']
                lrows.append({'venue': 'polymarket', 'kind': r['kind'], 'ask': b['ask'], 'bid': b['bid'],
                              'depth_yes_touch': b['ask_usd_touch'], 'depth_no_touch': b['bid_usd_touch']})
    years = max(1e-6, (now - CUTOFF) / YEAR)
    res['capacity'] = capacity_and_value(oos, dmap, lrows, years)
    res['capacity']['depth_touch_by_kind_band'] = depth_table(lrows)
    # the best out-of-sample variants (descriptive only: not a selection)
    ranked = sorted(tv, key=lambda k: -((parts[k]['oos'] or {}).get('ann_excess') or -9))
    res['top_oos_descriptive'] = [{'name': k, 'oos': parts[k]['oos'], 'in': parts[k]['in']} for k in ranked[:10]]
    p = sel
    go = bool(p['in_sample_positive'] and (p['oos_t'] or 0) >= 2 and chosen in p['bh_survivors_positive']
              and res['capacity']['usd_per_year_over_ssr'] > 0)
    res['go'] = {'go': go, 'in_sample_positive': p['in_sample_positive'], 'oos_t': p['oos_t'],
                 'chosen_in_bh_survivors_positive': chosen in p['bh_survivors_positive'],
                 'usd_per_year_over_ssr': res['capacity']['usd_per_year_over_ssr'],
                 'variants_tried': len(all_variants()) + 2}
    res['touch_check'] = touch_check(out)
    # POST HOC (added after the calibration table was seen; counted as one more variant): sell the touch, i.e. buy
    # NO as a taker on weekly and monthly touch markets 0.5-2 sd from the barrier, regardless of the model
    ph = []
    for d in decs:
        if d['kind'] in ('touch_week', 'touch_month') and d['z'] is not None and 0.5 <= abs(d['z']) < 2:
            px = 1.0 - d['mid']
            cost = taker_cost(px, hs_lookup(hs_table, d['kind'], px))
            pay = 1.0 - d['pay']
            ph.append({'t': d['t'], 'close': d['close'], 'w': 1.0, 'event': d['event'], 'pay': pay, 'p': cost,
                       'ret': pay / cost - 1.0, 'h': d['h']})
    ph_in = [t for t in ph if t['close'] < CUTOFF]
    ph_oos = [t for t in ph if t['t'] >= CUTOFF]
    s_oos, _, _ = daily_series(ph_oos, [t['ret'] for t in ph_oos], CUTOFF, now) if ph_oos else ([], 0, 0)
    res['post_hoc_sell_touch'] = {
        'note': 'not pre-registered; added after the calibration table; a forward-test candidate at most',
        'in': summarize(ph_in, [t['ret'] for t in ph_in]) if ph_in else {'n': 0},
        'oos': summarize(ph_oos, [t['ret'] for t in ph_oos]) if ph_oos else {'n': 0},
        'oos_hac_t': B.newey_west_t(s_oos)[0] if s_oos else None,
        'oos_cluster_ci': cluster_bootstrap(ph_oos, [t['ret'] for t in ph_oos]) if ph_oos else None}
    res['go']['variants_tried'] = len(all_variants()) + 3
    write_json(out / 'analysis.json', res)
    print(json.dumps({'decisions': len(decs), 'chosen': chosen, 'go': res['go'], 'late': res['late_entry']},
                     default=str))
    return 0


def depth_table(lrows):
    g = collections.defaultdict(list)
    for r in lrows:
        g['%s|%s' % (r['kind'], band_key(r['ask']))].append(r['depth_yes_touch'])
        g['%s|%s' % (r['kind'], band_key(1 - r['bid']))].append(r['depth_no_touch'])
    return {k: {'n': len(v), 'median_usd': statistics.median(v), 'p75_usd': sorted(v)[int(0.75 * (len(v) - 1))]}
            for k, v in sorted(g.items())}


# ------------------------------------------------------------------------------------------------ touch check

def touch_check(out, n_cases=6, n_paths=4000, step_min=5, seed=9):
    """The reflection formula at the barrier-strike vol, checked on a few historical decisions: Monte Carlo of the
    same lognormal path at 5-minute steps (discretisation), the formula at the ATM vol (what ignoring the smile does)
    and twice the smile digital (the driftless rule of thumb)."""
    decs = read_gz(Path(out) / 'raw' / 'decisions.json.gz')
    cands = [d for d in decs if d['kind'] in ('touch_week', 'touch_month') and 0.08 < d['p'] < 0.6]
    cands.sort(key=lambda d: stable_u('tc:%s:%s' % (d['id'], d['h'])))
    rng = random.Random(seed)
    rows = []
    for d in cands[:n_cases]:
        T = (d['T'] - d['t']) / YEAR
        S, B, sig = d['S'], d['K'], d['sigma']
        mu = math.log(d['F'] / S) / T
        steps = max(10, int(T * YEAR / (step_min * 60)))
        dtt = T / steps
        b = math.log(B / S)
        hits = 0
        for _ in range(n_paths):
            x = 0.0
            for _ in range(steps):
                x += (mu - 0.5 * sig * sig) * dtt + sig * math.sqrt(dtt) * rng.gauss(0, 1)
                if (b > 0 and x >= b) or (b < 0 and x <= b):
                    hits += 1
                    break
        v = sig * math.sqrt(T)
        dig = _N.cdf((math.log(d['F'] / B) - 0.5 * v * v) / v)
        dig = dig if b > 0 else 1 - dig
        rows.append({'id': d['id'], 'kind': d['kind'], 'h': d['h'], 'direction': d['direction'], 'S': S, 'B': B,
                     'days': T * 365, 'sigma_barrier': sig, 'reflection': d['p'], 'mc_5min': hits / n_paths,
                     'mc_se': math.sqrt(max(1e-9, hits / n_paths * (1 - hits / n_paths)) / n_paths),
                     'twice_digital_flat': min(1.0, 2 * dig), 'market_mid': d['mid'], 'outcome': d['pay']})
    return rows


# ------------------------------------------------------------------------------------------------ render

def fmt(x, d=3):
    if x is None:
        return '-'
    if isinstance(x, float):
        return ('%.' + str(d) + 'f') % x
    return str(x)


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_crypto_options tables (%s)' % a['generated'], '']
    L += ['## Decisions', '', '| kind | horizon | decisions |', '|---|---:|---:|']
    for k, v in a['decisions_by_kind_h'].items():
        kk, hh = k.split('|')
        L.append('| %s | %sh | %d |' % (kk, hh, v))
    L += ['', 'Skipped: ' + ', '.join('%s %d' % (k, v) for k, v in a['decision_stats'].items()), '']
    L += ['## Calibration: model and market against outcomes', '',
          '| kind | horizon | n | events | outcome | model | market | Brier model | Brier market | slope model | slope market |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in a['calibration'].items():
        kk, hh = k.split('|')
        L.append('| %s | %s | %d | %d | %s | %s | %s | %s | %s | %s | %s |' % (
            kk, hh, v['n'], v['events'], fmt(v['mean_outcome']), fmt(v['mean_model']), fmt(v['mean_market']),
            fmt(v['brier_model'], 4), fmt(v['brier_market'], 4), fmt(v['slope_model'], 2), fmt(v['slope_market'], 2)))
    L += ['', '### Where model and market disagree by 5c or more', '',
          '| kind | horizon | n | mean (model - market) | mean (outcome - market) | outcome on model side |',
          '|---|---|---:|---:|---:|---:|']
    for k, v in a['calibration'].items():
        dd = v['disagree_5c']
        if dd['n']:
            kk, hh = k.split('|')
            L.append('| %s | %s | %d | %s | %s | %s |' % (kk, hh, dd['n'], fmt(dd['mean_model_minus_market']),
                                                         fmt(dd['mean_outcome_minus_market']),
                                                         fmt(dd['share_outcome_on_model_side'])))
    L += ['', '## Mean absolute deviation, market midpoint vs model (history)', '',
          '| kind | horizon | moneyness | n | MAD | mean market - model | share beyond taker cost |',
          '|---|---|---|---:|---:|---:|---:|']
    for k, v in a['mad_history'].items():
        kk, hh, zz = k.split('|')
        L.append('| %s | %s | %s | %d | %s | %s | %s |' % (kk, hh, zz, v['n'], fmt(v['mad']),
                                                           fmt(v['mean_signed_market_minus_model']),
                                                           fmt(v['share_beyond_taker_cost'], 2)))
    lv = a.get('live') or {}
    if lv:
        L += ['', '## Live snapshot %s: Polymarket and Kalshi against Deribit' % lv.get('at'), '',
              '| venue/kind/hours | n | MAD | mean market - model | exec edge > 0 | > 2c | > 5c | USD at touch where > 2c |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        for k, v in lv['by_venue_kind_hours'].items():
            L.append('| %s | %d | %s | %s | %d | %d | %d | %s |' % (k, v['n'], fmt(v['mad']),
                                                                  fmt(v['mean_signed_market_minus_model']),
                                                                  v['n_exec_edge_pos'], v['n_exec_edge_2c'],
                                                                  v['n_exec_edge_5c'], fmt(v['usd_touch_where_edge_2c'], 0)))
        L += ['', '| Polymarket kind/moneyness | n | MAD | mean market - model |', '|---|---:|---:|---:|']
        for k, v in lv['polymarket_by_kind_z'].items():
            L.append('| %s | %d | %s | %s |' % (k, v['n'], fmt(v['mad']), fmt(v['mean_signed_market_minus_model'])))
    L += ['', '## Live half-spread of crypto books (Polymarket, by group and price band)', '',
          '| group/band | n | median | p75 |', '|---|---:|---:|---:|']
    for k, v in sorted(a['half_spread_live'].items()):
        L.append('| %s | %d | %s | %s |' % (k, v['n'], fmt(v['median'], 4), fmt(v['p75'], 4)))
    pr = a['protocol']
    L += ['', '## Protocol (choose before %s, test after)' % a['cutoff'], '',
          '- variants: %d (+2 overlays: late entry, delta hedge)' % pr['n_variants'],
          '- chosen: `%s`; in-sample positive: %s; out-of-sample HAC t: %s; rank %s; BH positive survivors: %d' % (
              pr['chosen'], pr['in_sample_positive'], fmt(pr['oos_t'], 2), pr['oos_rank'],
              len(pr['bh_survivors_positive'])),
          '- chosen in sample: %s' % json.dumps({k: a['chosen']['in'].get(k) for k in ('n', 'mean_return', 'ann_excess', 'win_rate')}),
          '- chosen out of sample: %s' % json.dumps({k: a['chosen']['oos'].get(k) for k in ('n', 'mean_return', 'ann_excess', 'win_rate')}),
          '- late entry (+1h): %s' % json.dumps(a['late_entry']),
          '- delta-hedge overlay: %s' % json.dumps(a['hedge_overlay']),
          '- capacity: %s' % json.dumps({k: v for k, v in a['capacity'].items() if k != 'depth_touch_by_kind_band'}),
          '- go: %s' % json.dumps(a['go']), '']
    L += ['## Best out-of-sample variants (descriptive, not a selection)', '',
          '| variant | n in | ann. excess in | n oos | mean ret oos | ann. excess oos |', '|---|---:|---:|---:|---:|---:|']
    for r in a['top_oos_descriptive']:
        L.append('| %s | %s | %s | %s | %s | %s |' % (r['name'], r['in'].get('n'), fmt(r['in'].get('ann_excess')),
                                                    r['oos'].get('n'), fmt(r['oos'].get('mean_return'), 4),
                                                    fmt(r['oos'].get('ann_excess'))))
    if a.get('vrp'):
        L += ['', '## Implied (model) vol against realised vol over the remaining window', '',
              '| kind | n | mean implied | mean realised | median realised/implied | share realised < implied |',
              '|---|---:|---:|---:|---:|---:|']
        for k, v in a['vrp'].items():
            L.append('| %s | %d | %s | %s | %s | %s |' % (k, v['n'], fmt(v['mean_implied']), fmt(v['mean_realised']),
                                                        fmt(v['median_ratio_realised_to_implied']),
                                                        fmt(v['share_realised_below_implied'], 2)))
    if a.get('post_hoc_sell_touch'):
        ph = a['post_hoc_sell_touch']
        L += ['', '## Post hoc (not pre-registered): buy NO on weekly/monthly touch markets 0.5-2 sd out, taker', '',
              '- in sample: %s' % json.dumps({k: ph['in'].get(k) for k in ('n', 'events', 'mean_return', 'ann_excess', 'win_rate')}),
              '- out of sample: %s; HAC t %s; cluster CI %s' % (
                  json.dumps({k: ph['oos'].get(k) for k in ('n', 'events', 'mean_return', 'ann_excess', 'win_rate')}),
                  fmt(ph['oos_hac_t'], 2), json.dumps(ph['oos_cluster_ci']))]
    if a.get('touch_check'):
        L += ['', '## Touch approximation check', '',
              '| kind | h | dir | days | barrier vol | reflection | MC 5-min | 2x flat digital | market | outcome |',
              '|---|---:|---|---:|---:|---:|---:|---:|---:|---:|']
        for r in a['touch_check']:
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                r['kind'], r['h'], r['direction'], fmt(r['days'], 1), fmt(r['sigma_barrier'], 3), fmt(r['reflection']),
                fmt(r['mc_5min']), fmt(r['twice_digital_flat']), fmt(r['market_mid']), r['outcome']))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0

# ------------------------------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('universe', 'spot', 'deribit', 'prices', 'live', 'analyze', 'render'):
        p = sub.add_parser(name)
        p.add_argument('--out', default='research/2026-10-14/pm_crypto_options')
        p.add_argument('--interval', type=float, default=0.22)
        p.add_argument('--limit', type=int, default=0)
        p.add_argument('--frac', type=float, default=0.30)
        p.add_argument('--currencies', default='BTC,ETH')
        p.add_argument('--workers', type=int, default=3)
    a = ap.parse_args()
    return globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
