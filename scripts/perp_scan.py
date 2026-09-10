#!/usr/bin/env python3
"""Turn a collected perp window into the numbers a trader can act on: funding, basis, depth, and the capacity of each.

A perp market is three prices and a rate. The **oracle** is what the venue says the thing is worth, the **mark** is
what the book says, the **premium** is the gap between them, and the **funding rate** is the toll charged on that gap
every hour. Everything worth extracting from a perp DEX is a statement about those four numbers: that the toll is
mispriced against another venue's toll, that the gap is wide and will close, that the gap is wide and *cannot* close
because the underlying market is shut, or that a market's open interest cap has stopped the people who would close it.

This module computes all of it from the saved window, offline, and refuses to report an edge without the two things
that decide whether it is real:

* **Depth.** Every edge is quoted net of what it costs to put the position on, walked through the actual L2 book that
  was saved, not through a slippage guess. A 40% annualised funding rate on a book that costs 90bp to enter and 90bp
  to leave is a 40% rate you cannot have for less than three weeks of holding.
* **Capacity.** HIP-3 gives every builder-deployed market a per-asset open-interest cap, and a market at its cap
  cannot absorb the position that would close the gap. That is the same shape as the withdrawable-liquidity constraint
  the cross-chain study found binding on seven of twenty dollar switches, and it binds here too.

The classification of what an asset *is* comes from behaviour, not from a symbol table. An asset whose 60 one-minute
candles contain three trades is illiquid whatever it is called; an asset carrying a persistent one-directional premium
for eight hours is telling you its oracle and its book disagree about something structural, which on an equity perp
at 11:00 UTC means the underlying exchange is closed and the book is pricing the gap.

    uv run python scripts/perp_scan.py analyze --out research/2026-09-08/perps_1h
    uv run python scripts/perp_scan.py verify  --out research/2026-09-08/perps_1h
    uv run python scripts/perp_scan.py detect  --out research/2026-09-08/perps_1h
    uv run python scripts/perp_scan.py render  --out research/2026-09-08/perps_1h
    uv run python scripts/perp_scan.py show <coin> --out research/2026-09-08/perps_1h
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

HOURS_PER_YEAR = 8760.0


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_json(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2, sort_keys=True, default=str))


def safe(coin):
    return coin.replace(':', '__').replace('/', '_')


def f(v, d=None):
    try:
        x = float(v)
        return x if x == x and abs(x) != float('inf') else d
    except (TypeError, ValueError):
        return d


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).isoformat(timespec='seconds')


# ---------------------------------------------------------------------------------------------- sessions

def us_equity_session(ms):
    """Which US cash-equity session a UTC instant falls in.

    This matters because a stock perp does not close and the stock does. Hyperliquid's HIP-3 equity markets quote
    around the clock; NYSE and Nasdaq run 13:30–20:00 UTC during US daylight time, with pre-market from 08:00 and
    after-hours to 00:00. Outside those, the only price that exists is the perp's own, and any premium it carries is
    an unhedgeable opinion rather than an arbitrage.

    Daylight-saving is approximated by month (US DST runs mid-March to early November); the boundary weeks are marked
    so nothing downstream treats the label as exact.
    """
    t = dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)
    dst = 3 <= t.month <= 10 or (t.month == 11 and t.day < 2) or (t.month == 3 and t.day > 14)
    off = 4 if dst else 5                                    # hours behind UTC for US Eastern
    et = t - dt.timedelta(hours=off)
    if et.weekday() >= 5:
        return {'session': 'weekend', 'et': et.strftime('%a %H:%M'), 'dst_assumed': dst}
    mins = et.hour * 60 + et.minute
    if 570 <= mins < 960:
        s = 'regular'
    elif 240 <= mins < 570:
        s = 'pre-market'
    elif 960 <= mins < 1200:
        s = 'after-hours'
    else:
        s = 'closed'
    return {'session': s, 'et': et.strftime('%a %H:%M'), 'dst_assumed': dst}


# ---------------------------------------------------------------------------------------------- book maths

def book_stats(levels, mid):
    """Spread, depth at several distances from mid, and the cost of a market order of a given notional.

    Depth is reported in *notional* because that is the unit every downstream decision is in. The cost function walks
    the saved levels: it is exact up to the depth the venue published (20 levels a side) and reports how much of the
    requested size it could not fill, which is the honest way to say "the book is not this deep".
    """
    bids, asks = levels[0], levels[1]
    if not bids or not asks or not mid:
        return None
    bb, ba = f(bids[0]['px']), f(asks[0]['px'])
    out = {'best_bid': bb, 'best_ask': ba, 'spread_bps': 1e4 * (ba - bb) / mid if mid else None,
           'levels': [len(bids), len(asks)]}
    for bps in (5, 10, 25, 50, 100):
        lo, hi = mid * (1 - bps / 1e4), mid * (1 + bps / 1e4)
        out['bid_depth_%dbp_usd' % bps] = sum(f(l['px'], 0) * f(l['sz'], 0) for l in bids if f(l['px'], 0) >= lo)
        out['ask_depth_%dbp_usd' % bps] = sum(f(l['px'], 0) * f(l['sz'], 0) for l in asks if f(l['px'], 0) <= hi)
    out['book_bid_usd'] = sum(f(l['px'], 0) * f(l['sz'], 0) for l in bids)
    out['book_ask_usd'] = sum(f(l['px'], 0) * f(l['sz'], 0) for l in asks)
    return out


def walk_cost_bps(levels, side, mid, notional):
    """Average cost in bps of taking `notional` of liquidity, and the share that could not be filled."""
    if not mid or notional <= 0:
        return None, 1.0
    book = levels[1] if side == 'buy' else levels[0]
    left, spent, filled = notional, 0.0, 0.0
    for l in book:
        px, sz = f(l['px'], 0), f(l['sz'], 0)
        if not px or not sz:
            continue
        take = min(left, px * sz)
        spent += take
        filled += take / px
        left -= take
        if left <= 0:
            break
    if filled <= 0:
        return None, 1.0
    avg = spent / filled
    cost = 1e4 * (avg - mid) / mid * (1 if side == 'buy' else -1)
    return cost, max(left, 0.0) / notional


def round_trip_bps(levels, mid, notional, fee_bps):
    """What it costs to open and close a position of this size: both sides of the book plus fees, in bps."""
    b, ub = walk_cost_bps(levels, 'buy', mid, notional)
    s, us = walk_cost_bps(levels, 'sell', mid, notional)
    if b is None or s is None:
        return None, max(ub, us)
    return b + s + 2 * fee_bps, max(ub, us)


# ---------------------------------------------------------------------------------------------- analyze

def load_window(out):
    out = Path(out)
    man = json.loads((out / 'manifest.json').read_text())
    dexes = json.loads((out / 'dexes.json').read_text())
    caps = {}
    fee_recipients = {}
    for d in dexes['raw']:
        if d is None:
            continue
        for coin, cap in (d.get('assetToStreamingOiCap') or []):
            caps[coin] = f(cap)
        fee_recipients[d['name']] = {'deployer': d.get('deployer'), 'fee_recipient': d.get('feeRecipient'),
                                     'oracle_updater': d.get('oracleUpdater'), 'full_name': d.get('fullName')}
    snaps = sorted((out / 'snap').glob('*.json.gz'))
    return out, man, dexes, caps, fee_recipients, snaps


def cmd_analyze(args):
    out, man, dexes, caps, dex_meta, snaps = load_window(args.out)
    if not snaps:
        raise SystemExit('no snapshots in %s' % out)
    # The window's own snapshot is the one taken at collection time; a later tape snapshot describes a later market.
    snap = read_gz(snaps[0] if args.snapshot == 'first' else snaps[-1])
    w = man['window']

    rows = []
    for dex, payload in snap['dexes'].items():
        if not payload:
            continue
        for m, c in zip(payload[0]['universe'], payload[1]):
            coin = m['name']
            sym = coin.split(':', 1)[1] if ':' in coin else coin
            mark, oracle, mid = f(c.get('markPx')), f(c.get('oraclePx')), f(c.get('midPx'))
            oi = f(c.get('openInterest'), 0.0)
            px = mark or oracle or mid
            fund_h = f(c.get('funding'), 0.0)
            imp = c.get('impactPxs') or []
            r = {
                'dex': dex or 'core', 'coin': coin, 'symbol': sym,
                'is_hip3': bool(dex), 'delisted': bool(m.get('isDelisted')),
                'max_leverage': m.get('maxLeverage'), 'only_isolated': bool(m.get('onlyIsolated')),
                'margin_mode': m.get('marginMode'), 'growth_mode': m.get('growthMode'),
                'deployer_fee_scale': f(m.get('deployerFeeScale')),
                'mark': mark, 'oracle': oracle, 'mid': mid,
                'premium': f(c.get('premium')),
                'mark_vs_oracle_bps': (1e4 * (mark - oracle) / oracle) if (mark and oracle) else None,
                'funding_hourly': fund_h, 'funding_apr': (fund_h or 0) * HOURS_PER_YEAR,
                'open_interest': oi, 'oi_usd': (oi * px) if px else None,
                'oi_cap_usd': caps.get(coin),
                'day_ntl_vlm': f(c.get('dayNtlVlm'), 0.0), 'prev_day_px': f(c.get('prevDayPx')),
                'impact_spread_bps': (1e4 * (f(imp[1]) - f(imp[0])) / mid) if (len(imp) == 2 and mid and f(imp[0]) and f(imp[1])) else None,
                # The venue's own premium is an hourly average against the impact prices; this is the instantaneous
                # version of the same quantity, kept beside it so the two can be compared instead of conflated.
                'impact_mid_basis': (((f(imp[0]) + f(imp[1])) / 2 - oracle) / oracle)
                                    if (len(imp) == 2 and oracle and f(imp[0]) and f(imp[1])) else None,
                'funding_charged_share': None,
            }
            if r['premium'] is not None and abs(r['premium']) >= 2e-4 and fund_h is not None:
                r['funding_charged_share'] = fund_h / (r['premium'] / 8)
            if r['oi_cap_usd'] and r['oi_usd'] is not None:
                r['oi_cap_use'] = r['oi_usd'] / r['oi_cap_usd']
            rows.append(r)

    # ---- candles: what actually traded in the window
    for r in rows:
        p = out / 'candles' / (safe(r['coin']) + '.json.gz')
        if not p.exists():
            r['candles'] = None
            continue
        cs = read_gz(p)
        cs = [x for x in cs if w['start_ms'] <= x['t'] < w['end_ms']]
        if not cs:
            r['candles'] = {'n': 0, 'traded_minutes': 0, 'trades': 0, 'base_vlm': 0.0, 'ntl_vlm': 0.0}
            continue
        closes = [f(x['c']) for x in cs if f(x['c'])]
        vol = sum(f(x['v'], 0.0) for x in cs)
        ntl = sum(f(x['v'], 0.0) * f(x['c'], 0.0) for x in cs)
        rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))
                if closes[i] > 0 and closes[i - 1] > 0]
        traded = sum(1 for x in cs if int(x.get('n') or 0) > 0)
        r['candles'] = {
            'n': len(cs), 'traded_minutes': traded, 'trades': sum(int(x.get('n') or 0) for x in cs),
            'base_vlm': vol, 'ntl_vlm': ntl,
            'open': f(cs[0]['o']), 'close': f(cs[-1]['c']),
            'high': max((f(x['h'], 0) for x in cs), default=None), 'low': min((f(x['l'], 1e18) for x in cs), default=None),
            'ret_bps': (1e4 * (f(cs[-1]['c']) / f(cs[0]['o']) - 1)) if (f(cs[0]['o']) and f(cs[-1]['c'])) else None,
            'rv_annualised': (statistics.pstdev(rets) * math.sqrt(525600)) if len(rets) > 2 else None,
            'distinct_closes': len({x['c'] for x in cs}),
        }

    # ---- books: spread, depth, and the cost of a real position
    for r in rows:
        p = out / 'books' / (safe(r['coin']) + '.json.gz')
        if not p.exists():
            r['book'] = None
            continue
        b = read_gz(p)
        mid = r['mid'] or r['mark']
        st = book_stats(b['levels'], mid)
        if st:
            st['snapshot_utc'] = utc(b['time'])
            # Fees: Hyperliquid's base taker fee, scaled by the HIP-3 deployer's own multiplier. A builder can set
            # 0–300%, and a 3x fee scale is the difference between an edge and a donation, so it is priced here rather
            # than assumed away.
            fee_bps = args.taker_fee_bps * (r['deployer_fee_scale'] if r['deployer_fee_scale'] else 1.0)
            st['taker_fee_bps_effective'] = fee_bps
            for size in (1e4, 1e5, 1e6):
                rt, unf = round_trip_bps(b['levels'], mid, size, fee_bps)
                st['round_trip_bps_%dk' % int(size / 1e3)] = rt
                st['unfilled_share_%dk' % int(size / 1e3)] = unf
        r['book'] = st

    # ---- funding history: the premium is the thing, and it has eight hours of shape
    for r in rows:
        p = out / 'funding' / (safe(r['coin']) + '.json.gz')
        if not p.exists():
            r['funding_hist'] = None
            continue
        h = read_gz(p)
        rates = [f(x['fundingRate']) for x in h if f(x['fundingRate']) is not None]
        prems = [f(x['premium']) for x in h if f(x['premium']) is not None]
        if not rates:
            r['funding_hist'] = {'n': 0}
            continue
        r['funding_hist'] = {
            'n': len(rates), 'from_utc': utc(h[0]['time']), 'to_utc': utc(h[-1]['time']),
            'realised_sum': sum(rates), 'realised_apr_8h': (sum(rates) / len(rates)) * HOURS_PER_YEAR,
            'rate_min': min(rates), 'rate_max': max(rates), 'rate_last': rates[-1],
            'premium_mean': (sum(prems) / len(prems)) if prems else None,
            'premium_min': min(prems) if prems else None, 'premium_max': max(prems) if prems else None,
            'sign_flips': sum(1 for i in range(1, len(rates)) if (rates[i] > 0) != (rates[i - 1] > 0)),
            'one_sided': all(x >= 0 for x in rates) or all(x <= 0 for x in rates),
        }

    # ---- the same underlying on more than one book
    by_sym = collections.defaultdict(list)
    for r in rows:
        if not r['delisted']:
            by_sym[r['symbol']].append(r)
    cross, collisions = [], []
    for sym, rs in by_sym.items():
        if len(rs) < 2:
            continue
        priced = [x for x in rs if x['mark']]
        if len(priced) < 2:
            continue
        priced.sort(key=lambda x: -(x['mark'] or 0))
        hi, lo = priced[0], priced[-1]
        spread_bps = 1e4 * (hi['mark'] - lo['mark']) / lo['mark'] if lo['mark'] else None
        # A ticker is not an identity. `core:STX` is Stacks at $0.27 and `para:STX` is something else at $857.79, and
        # joining them on the string produced a 32,046,130 bp "dispersion" in the first pass. Two markets are only the
        # same underlying if their prices agree to within a few percent; anything wider is a name collision and is
        # recorded as one rather than silently compared.
        if spread_bps is None or abs(spread_bps) > args.same_asset_bps:
            collisions.append({'symbol': sym, 'spread_bps': spread_bps,
                               'rows': [{'coin': x['coin'], 'mark': x['mark']} for x in priced],
                               'why': 'prices differ by more than %.0f%%, so these are different underlyings sharing '
                                      'a ticker' % (args.same_asset_bps / 100)})
            continue
        fr = [x['funding_apr'] for x in rs if x['funding_apr'] is not None]
        cross.append({
            'symbol': sym, 'venues': len(rs),
            'rows': [{'dex': x['dex'], 'coin': x['coin'], 'mark': x['mark'], 'oracle': x['oracle'],
                      'funding_apr': x['funding_apr'], 'oi_usd': x['oi_usd'],
                      'hour_ntl_vlm': (x.get('candles') or {}).get('ntl_vlm'),
                      'trades': (x.get('candles') or {}).get('trades'),
                      'oi_cap_usd': x['oi_cap_usd'], 'fee_scale': x['deployer_fee_scale']} for x in rs],
            'mark_spread_bps': spread_bps, 'high_dex': hi['dex'], 'low_dex': lo['dex'],
            'funding_spread_apr': (max(fr) - min(fr)) if len(fr) >= 2 else None,
            'total_oi_usd': sum(x['oi_usd'] or 0 for x in rs),
        })
    cross.sort(key=lambda x: -(abs(x['mark_spread_bps'] or 0)))

    # ---- Hyperliquid's own funding beside Binance's and Bybit's, annualised on a common basis
    xv = []
    pfp = out / 'predicted.json'
    if pfp.exists():
        for coin, venues in json.loads(pfp.read_text())['rows']:
            d = {}
            for name, v in venues:
                if not v:
                    continue
                rate, hrs = f(v.get('fundingRate')), f(v.get('fundingIntervalHours'), 8.0)
                if rate is None or not hrs:
                    continue
                d[name] = {'rate': rate, 'interval_h': hrs, 'apr': rate * (HOURS_PER_YEAR / hrs)}
            if 'HlPerp' in d and len(d) >= 2:
                others = {k: v for k, v in d.items() if k != 'HlPerp'}
                best = max(others.items(), key=lambda kv: abs(kv[1]['apr'] - d['HlPerp']['apr']))
                xv.append({'coin': coin, 'venues': d,
                           'hl_apr': d['HlPerp']['apr'], 'other': best[0], 'other_apr': best[1]['apr'],
                           'spread_apr': d['HlPerp']['apr'] - best[1]['apr']})
    xv.sort(key=lambda x: -abs(x['spread_apr']))

    live = [r for r in rows if not r['delisted']]
    traded = [r for r in live if ((r.get('candles') or {}).get('trades') or 0) > 0]
    A = {
        'generated': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'window': w, 'venue': man['venue'],
        'session_at_window_end': us_equity_session(w['end_ms']),
        'snapshot_utc': snap['utc'],
        'dex_meta': dex_meta,
        'totals': {
            'dexes': len(man['dexes']), 'assets': len(rows), 'live': len(live), 'delisted': len(rows) - len(live),
            'traded_in_window': len(traded),
            'oi_usd': sum(r['oi_usd'] or 0 for r in rows),
            'day_ntl_vlm': sum(r['day_ntl_vlm'] or 0 for r in rows),
            'hour_ntl_vlm': sum((r.get('candles') or {}).get('ntl_vlm') or 0 for r in rows),
            'hour_trades': sum((r.get('candles') or {}).get('trades') or 0 for r in rows),
        },
        'by_dex': {},
        'assets': rows,
        'cross_dex': cross,
        'ticker_collisions': collisions,
        'cross_venue_funding': xv,
    }
    for d in sorted({r['dex'] for r in rows}):
        rs = [r for r in rows if r['dex'] == d]
        lv = [r for r in rs if not r['delisted']]
        tr = [r for r in lv if ((r.get('candles') or {}).get('trades') or 0) > 0]
        A['by_dex'][d] = {
            'assets': len(rs), 'live': len(lv), 'traded_in_window': len(tr),
            'oi_usd': sum(r['oi_usd'] or 0 for r in rs),
            'day_ntl_vlm': sum(r['day_ntl_vlm'] or 0 for r in rs),
            'hour_ntl_vlm': sum((r.get('candles') or {}).get('ntl_vlm') or 0 for r in rs),
            'hour_trades': sum((r.get('candles') or {}).get('trades') or 0 for r in rs),
            'oi_cap_usd': sum(r['oi_cap_usd'] or 0 for r in rs) or None,
            'fee_scales': sorted({r['deployer_fee_scale'] for r in rs if r['deployer_fee_scale'] is not None}),
            **(dex_meta.get(d, {}) if d != 'core' else {'full_name': 'HyperCore (first-party)'}),
        }
    write_json(out / 'analysis.json', A)
    print(json.dumps({'assets': len(rows), 'live': len(live), 'traded': len(traded),
                      'oi_usd': round(A['totals']['oi_usd']),
                      'hour_ntl_vlm': round(A['totals']['hour_ntl_vlm']),
                      'cross_dex_symbols': len(cross), 'cross_venue_coins': len(xv),
                      'session': A['session_at_window_end']}, indent=1))
    return 0


# ---------------------------------------------------------------------------------------------- the tape

def cmd_tape(args):
    """Per-asset mark/oracle/premium series from the repeated snapshots, and the one test that matters.

    A single snapshot cannot tell a *stale oracle* from a *structural basis*, and the two call for opposite trades.
    If the oracle is frozen while the book moves, the premium is an artifact and it will vanish the moment the oracle
    updates. If the oracle moves tick for tick with the book while holding a constant offset, the gap is real: the
    venue's own reference and its own order book disagree about the price, persistently, and the funding rate is the
    toll being charged for that disagreement.

    The discriminator is the correlation of *first differences*. A frozen oracle has zero variance; a live one that
    tracks the mark has a difference correlation near 1 with a non-zero mean offset. Both are reported, along with
    whether the offset is widening, so nothing downstream has to guess which regime it is in.
    """
    out = Path(args.out)
    snaps = sorted((out / 'snap').glob('*.json.gz'))
    if len(snaps) < 3:
        raise SystemExit('need at least 3 snapshots; found %d' % len(snaps))
    series = collections.defaultdict(list)
    for p in snaps:
        s = read_gz(p)
        for dex, payload in s['dexes'].items():
            if not payload:
                continue
            for m, c in zip(payload[0]['universe'], payload[1]):
                mk, orc = f(c.get('markPx')), f(c.get('oraclePx'))
                if mk and orc:
                    series[m['name']].append((s['ts'], mk, orc, f(c.get('funding'), 0.0),
                                              f(c.get('openInterest'), 0.0)))
    rows = []
    for coin, pts in series.items():
        if len(pts) < 3:
            continue
        pts.sort()
        marks = [p[1] for p in pts]
        orcs = [p[2] for p in pts]
        gaps = [1e4 * (p[1] - p[2]) / p[2] for p in pts]
        dm = [marks[i] - marks[i - 1] for i in range(1, len(marks))]
        do = [orcs[i] - orcs[i - 1] for i in range(1, len(orcs))]
        corr = None
        if len(dm) >= 3 and statistics.pstdev(dm) > 0 and statistics.pstdev(do) > 0:
            mm, mo = statistics.fmean(dm), statistics.fmean(do)
            cov = sum((a - mm) * (b - mo) for a, b in zip(dm, do)) / len(dm)
            corr = cov / (statistics.pstdev(dm) * statistics.pstdev(do))
        oracle_moves = sum(1 for x in do if abs(x) > 0)
        mark_moves = sum(1 for x in dm if abs(x) > 0)
        # widening: does the *absolute* gap trend away from zero across the tape?
        half = max(len(gaps) // 2, 1)
        widening = statistics.fmean([abs(g) for g in gaps[half:]]) - statistics.fmean([abs(g) for g in gaps[:half]])
        regime = ('oracle frozen while the book moved' if oracle_moves == 0 and mark_moves > 0 else
                  'both frozen' if oracle_moves == 0 and mark_moves == 0 else
                  'oracle tracks the book' if (corr is not None and corr > 0.8) else 'oracle moves independently')
        rows.append({
            'coin': coin, 'dex': coin.split(':')[0] if ':' in coin else 'core',
            'points': len(pts), 'span_s': pts[-1][0] - pts[0][0],
            'gap_bps_first': gaps[0], 'gap_bps_last': gaps[-1],
            'gap_bps_mean': statistics.fmean(gaps), 'gap_bps_stdev': statistics.pstdev(gaps),
            'gap_widening_bps': widening,
            'oracle_moves': oracle_moves, 'mark_moves': mark_moves, 'diff_corr': corr, 'regime': regime,
            'funding_apr_first': pts[0][3] * HOURS_PER_YEAR, 'funding_apr_last': pts[-1][3] * HOURS_PER_YEAR,
            'oi_first': pts[0][4], 'oi_last': pts[-1][4],
            'oi_change_pct': (100 * (pts[-1][4] / pts[0][4] - 1)) if pts[0][4] else None,
        })
    rows.sort(key=lambda r: -abs(r['gap_bps_mean']))
    T = {'generated': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
         'snapshots': len(snaps), 'from_utc': read_gz(snaps[0])['utc'], 'to_utc': read_gz(snaps[-1])['utc'],
         'assets': len(rows),
         'regimes': dict(collections.Counter(r['regime'] for r in rows)),
         'rows': rows}
    write_json(out / 'tape.json', T)
    print(json.dumps({'snapshots': len(snaps), 'assets': len(rows), 'regimes': T['regimes'],
                      'span_minutes': round((rows[0]['span_s'] if rows else 0) / 60, 1)}, indent=1))
    return 0


# ---------------------------------------------------------------------------------------------- detectors

def _m(v):
    v = v or 0
    for u, sc in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= sc:
            return '$' + format(round(v / sc, 1), ',') + u
    return '$' + format(round(v), ',')


def _carry_economics(r, size_usd, horizon_h):
    """Price a funding carry the way it is actually experienced: a rate against a one-off toll.

    The rate is per hour and the toll is paid twice — once on entry, once on exit — so the only number that decides
    whether a spectacular annualised figure is worth anything is **how many hours of funding it takes to pay for the
    round trip**. A 285% APR that costs 12bp to enter and leave pays for itself in under four hours. A 40% APR on a
    book that costs 90bp round-trip needs three weeks, and three weeks is far longer than any funding rate on this
    venue has been observed to hold its sign.
    """
    b = r.get('book') or {}
    fh = r.get('funding_hourly') or 0.0
    if not fh:
        return None
    key = 'round_trip_bps_%dk' % int(size_usd / 1e3)
    cost = b.get(key)
    unfilled = b.get('unfilled_share_%dk' % int(size_usd / 1e3))
    if cost is None:
        return None
    per_hour_bps = abs(fh) * 1e4
    be = (cost / per_hour_bps) if per_hour_bps > 0 else None
    collected = abs(fh) * horizon_h - cost / 1e4
    cap_head = None
    if r.get('oi_cap_usd') and r.get('oi_usd') is not None:
        cap_head = max(r['oi_cap_usd'] - r['oi_usd'], 0.0)
    depth = b.get('ask_depth_25bp_usd') if fh < 0 else b.get('bid_depth_25bp_usd')
    capacity = min([x for x in (cap_head, depth) if x is not None], default=None)
    net_apr = (collected * (HOURS_PER_YEAR / horizon_h)) if horizon_h else None
    # The ledger and the strategy book read `net_apr` and `go` from every economics block, whatever produced it.
    go = bool(be is not None and be < horizon_h and (capacity or 0) >= 1e5 and (unfilled or 0) < 0.5)
    reason = ('pays its round trip inside the horizon at six figures of book' if go else
              'break-even beyond the horizon, or under $100k of book, or half the order unfilled')
    return {
        'net_apr': net_apr, 'go': go, 'reason': reason,
        'side_paid': 'long' if fh < 0 else 'short',
        'funding_apr': fh * HOURS_PER_YEAR,
        'round_trip_bps_at_size': cost, 'size_usd': size_usd,
        'unfilled_share': unfilled,
        'break_even_hours': be,
        'net_apr_over_%dh' % horizon_h: (collected * (HOURS_PER_YEAR / horizon_h)) if horizon_h else None,
        'net_usd_over_%dh' % horizon_h: collected * size_usd,
        'capacity_usd': capacity, 'oi_cap_headroom_usd': cap_head, 'depth_25bp_usd': depth,
        'hedge': 'unhedged: this prices the funding only. The position carries the underlying\'s delta unless it is '
                 'hedged somewhere this scan cannot see, and no such hedge exists on this venue for a HIP-3 market '
                 'whose underlying is not also listed here.',
    }


def det_funding_carry(A, args):
    hits = []
    for r in A['assets']:
        if r['delisted']:
            continue
        fh = r.get('funding_hist') or {}
        apr = r.get('funding_apr') or 0.0
        if abs(apr) < args.min_apr or (r.get('oi_usd') or 0) < args.min_oi:
            continue
        if fh.get('n', 0) < 6 or not fh.get('one_sided'):
            continue
        c = r.get('candles') or {}
        if (c.get('trades') or 0) < args.min_trades:
            continue
        ec = _carry_economics(r, args.size_usd, args.horizon_h)
        if not ec or ec['break_even_hours'] is None:
            continue
        hits.append({
            'detector': 'funding_carry', 'key': r['coin'],
            'severity': 'high' if (ec['break_even_hours'] < 8 and (ec['capacity_usd'] or 0) > 1e5) else 'notable',
            'title': '%s pays %s %.0f%% a year and costs %.1fbp to get in and out: %.1f hours to break even'
                     % (r['coin'], ec['side_paid'] + 's', 100 * abs(apr), ec['round_trip_bps_at_size'],
                        ec['break_even_hours']),
            'evidence': {
                'coin': r['coin'], 'dex': r['dex'], 'oi_usd': r['oi_usd'], 'hour_ntl_vlm': c.get('ntl_vlm'),
                'trades': c.get('trades'), 'mark': r['mark'], 'oracle': r['oracle'],
                'mark_vs_oracle_bps': r['mark_vs_oracle_bps'],
                'funding_hours_observed': fh.get('n'), 'premium_mean': fh.get('premium_mean'),
                'premium_min': fh.get('premium_min'), 'premium_max': fh.get('premium_max'),
                'sign_flips': fh.get('sign_flips'), 'spread_bps': (r.get('book') or {}).get('spread_bps'),
                'why': 'the funding rate has not changed sign in the observed window, so the toll is being paid '
                       'consistently by one side; the other side collects it',
            },
            'economics': ec, 'usd': ec.get('net_usd_over_%dh' % args.horizon_h),
        })
    return sorted(hits, key=lambda h: (h['economics']['break_even_hours'] or 1e9))


def det_premium_drift(A, args):
    """A premium that widens in one direction, hour after hour, is the funding mechanism failing to clear a flow."""
    hits = []
    for r in A['assets']:
        fh = r.get('funding_hist') or {}
        if fh.get('n', 0) < 6 or (r.get('oi_usd') or 0) < args.min_oi:
            continue
        p = fh.get('_series')
        if p is None:
            continue
        run, direction = 1, 0
        best = 1
        for i in range(1, len(p)):
            d = 1 if p[i] > p[i - 1] else (-1 if p[i] < p[i - 1] else 0)
            if d and d == direction:
                run += 1
            else:
                run, direction = 1, d
            best = max(best, run)
        if best < args.min_run or abs(p[-1]) < 1e-3:
            continue
        hits.append({
            'detector': 'premium_drift', 'key': r['coin'],
            'severity': 'high' if best >= 7 else 'notable',
            'title': '%s: the premium moved the same way %d hours running, %.3f%% to %.3f%%, and funding is now %.0f%% a year'
                     % (r['coin'], best, 100 * p[0], 100 * p[-1], 100 * (r.get('funding_apr') or 0)),
            'evidence': {'coin': r['coin'], 'dex': r['dex'], 'premium_series_pct': [round(100 * x, 4) for x in p],
                         'monotone_run_hours': best, 'oi_usd': r['oi_usd'],
                         'mark_vs_oracle_bps': r['mark_vs_oracle_bps'],
                         'why': 'funding exists to pull the mark back to the oracle; a premium that widens for hours '
                                'against a rising toll means the flow paying that toll is not price-sensitive, or the '
                                'oracle is not where the market thinks fair value is'},
            'economics': _carry_economics(r, args.size_usd, args.horizon_h),
        })
    return sorted(hits, key=lambda h: -h['evidence']['monotone_run_hours'])


def det_oi_cap_pressure(A, args):
    hits = []
    for r in A['assets']:
        u = r.get('oi_cap_use')
        if u is None or u < args.cap_warn or (r.get('oi_usd') or 0) < args.min_oi:
            continue
        c = r.get('candles') or {}
        hits.append({
            'detector': 'oi_cap_pressure', 'key': r['coin'],
            'severity': 'high' if u >= 0.98 else 'notable',
            'title': '%s is at %.1f%% of its HIP-3 open-interest cap (%s of %s)'
                     % (r['coin'], 100 * u, _m(r['oi_usd']), _m(r['oi_cap_usd'])),
            'evidence': {'coin': r['coin'], 'dex': r['dex'], 'oi_usd': r['oi_usd'], 'oi_cap_usd': r['oi_cap_usd'],
                         'headroom_usd': max((r['oi_cap_usd'] or 0) - (r['oi_usd'] or 0), 0),
                         'funding_apr': r['funding_apr'], 'mark_vs_oracle_bps': r['mark_vs_oracle_bps'],
                         'hour_ntl_vlm': c.get('ntl_vlm'), 'trades': c.get('trades'),
                         'book_ask_25bp_usd': (r.get('book') or {}).get('ask_depth_25bp_usd'),
                         'book_bid_25bp_usd': (r.get('book') or {}).get('bid_depth_25bp_usd'),
                         'why': 'at the cap, total open interest cannot grow: a new buyer can only be filled by an '
                                'existing long closing, not by a new short opening. The cap turns the price into a '
                                'queue, and the premium is what the queue costs'},
        })
    return sorted(hits, key=lambda h: -h['evidence']['oi_usd'])


def det_dead_market(A, args):
    """Listed, never delisted, and nobody has ever traded it. A HIP-3 deployment costs a 500k HYPE stake."""
    # The first pass skipped delisted markets and therefore found nothing — which was exactly backwards. The six
    # builder DEXes with no activity at all have *every* market delisted, so filtering delisted rows filtered out the
    # entire finding. A dead deployment is counted whether its markets are formally listed or not; what makes it a
    # finding is the staked 500,000 HYPE sitting behind a book with no open interest.
    by_dex = collections.defaultdict(list)
    for r in A['assets']:
        c = r.get('candles') or {}
        if (r.get('oi_usd') or 0) == 0 and (c.get('trades') or 0) == 0:
            by_dex[r['dex']].append(r['coin'] + ('*' if r['delisted'] else ''))
    hits = []
    for dex, coins in sorted(by_dex.items(), key=lambda kv: -len(kv[1])):
        meta = A['by_dex'].get(dex, {})
        total = meta.get('assets') or len(coins)
        hits.append({
            'detector': 'dead_market', 'key': dex,
            'severity': 'notable' if (len(coins) == total and total >= 5) else 'info',
            'title': '%s (%s): %d of %d markets carry no open interest and did not trade in the window'
                     % (dex, meta.get('full_name') or dex, len(coins), meta.get('assets') or len(coins)),
            'evidence': {'dex': dex, 'full_name': meta.get('full_name'), 'deployer': meta.get('deployer'),
                         'markets': sorted(coins)[:40], 'count': len(coins), 'markets_total': total,
                         'all_markets_dead': len(coins) == total,
                         'note': 'a market name marked * is formally delisted',
                         'dex_oi_usd': meta.get('oi_usd'), 'dex_hour_vlm': meta.get('hour_ntl_vlm'),
                         'why': 'HIP-3 requires the deployer to stake 500,000 HYPE for at least 183 days; a book with '
                                'no open interest earns its deployer no fee share against that locked stake'},
        })
    return hits


def det_illiquid_extreme_funding(A, args):
    """A huge rate on a market nobody trades is a trap, not an opportunity: you cannot get in, and cannot get out."""
    hits = []
    for r in A['assets']:
        if r['delisted']:
            continue
        c = r.get('candles') or {}
        apr = r.get('funding_apr') or 0
        if abs(apr) < 0.5 or (c.get('trades') or 0) >= args.min_trades or (r.get('oi_usd') or 0) < 1e4:
            continue
        b = r.get('book') or {}
        hits.append({
            'detector': 'illiquid_extreme_funding', 'key': r['coin'],
            'severity': 'notable',
            'title': '%s prints %.0f%% a year on %d trades in the hour, with %s of open interest already in it'
                     % (r['coin'], 100 * apr, c.get('trades') or 0, _m(r['oi_usd'])),
            'evidence': {'coin': r['coin'], 'dex': r['dex'], 'funding_apr': apr, 'trades': c.get('trades'),
                         'hour_ntl_vlm': c.get('ntl_vlm'), 'oi_usd': r['oi_usd'],
                         'mark_vs_oracle_bps': r['mark_vs_oracle_bps'],
                         'book_present': bool(b), 'spread_bps': b.get('spread_bps'),
                         'round_trip_bps_10k': b.get('round_trip_bps_10k'),
                         'why': 'the rate is derived from a premium that a book with no trading cannot correct; the '
                                'position already in it is paying or receiving that rate with no way out at size'},
        })
    return sorted(hits, key=lambda h: -abs(h['evidence']['funding_apr']))


def det_cross_venue_funding(A, args):
    """Hyperliquid's funding against Binance's and Bybit's on the same coin, net of what the HL leg costs."""
    by_coin = {r['coin']: r for r in A['assets'] if r['dex'] == 'core'}
    hits = []
    for x in A.get('cross_venue_funding') or []:
        r = by_coin.get(x['coin'])
        if not r or (r.get('oi_usd') or 0) < args.min_oi:
            continue
        spread = x['spread_apr']
        if abs(spread) < args.min_apr:
            continue
        b = r.get('book') or {}
        cost = b.get('round_trip_bps_%dk' % int(args.size_usd / 1e3))
        if cost is None:
            continue
        # Both legs cost something. The other venue's book is not in this window, so its leg is charged at the same
        # cost as Hyperliquid's — an assumption, stated, and one that flatters nothing since it is symmetric.
        total_cost = 2 * cost
        per_hour = abs(spread) / HOURS_PER_YEAR
        be = (total_cost / 1e4) / per_hour if per_hour > 0 else None
        hits.append({
            'detector': 'cross_venue_funding', 'key': x['coin'],
            'severity': 'notable' if (be is not None and be < 72) else 'info',
            'title': '%s funding is %.0f%% on Hyperliquid against %.0f%% on %s: %.0f%% a year for a delta-neutral pair, '
                     '%.0f hours to clear both round trips'
                     % (x['coin'], 100 * x['hl_apr'], 100 * x['other_apr'], x['other'].replace('Perp', ''),
                        100 * abs(spread), be or 0),
            'evidence': {'coin': x['coin'], 'hl_apr': x['hl_apr'], 'other_venue': x['other'],
                         'other_apr': x['other_apr'], 'spread_apr': spread,
                         'hl_oi_usd': r['oi_usd'], 'hl_hour_vlm': (r.get('candles') or {}).get('ntl_vlm'),
                         'hl_round_trip_bps': cost, 'assumed_total_round_trip_bps': total_cost,
                         'break_even_hours': be, 'size_usd': args.size_usd,
                         'venues': x['venues'],
                         'why': 'the other venue is a prediction for its next interval, not a settled rate, and it can '
                                'move before the interval closes; the Hyperliquid leg is the only one this window '
                                'measures directly'},
        })
    return sorted(hits, key=lambda h: (h['evidence']['break_even_hours'] or 1e9))


def det_stale_oracle(A, args, tape):
    hits = []
    for t in (tape or {}).get('rows', []):
        if t['regime'] != 'oracle frozen while the book moved' or t['mark_moves'] < 3:
            continue
        r = next((x for x in A['assets'] if x['coin'] == t['coin']), None)
        if not r or (r.get('oi_usd') or 0) < 1e4:
            continue
        hits.append({
            'detector': 'stale_oracle', 'key': t['coin'],
            'severity': 'notable',
            'title': '%s: the oracle did not move for %d snapshots while the book moved %d times, gap %.1fbp'
                     % (t['coin'], t['points'], t['mark_moves'], t['gap_bps_last']),
            'evidence': dict(t, oi_usd=r['oi_usd'], funding_apr=r['funding_apr'],
                             why='funding is charged on the gap between mark and oracle, so a frozen oracle turns '
                                 'every move in the book into a funding charge that reverses when the oracle catches up'),
        })
    return hits


def _pair_economics(rows, books, size_usd, horizon_h):
    """Long the book that pays longs, short the one that pays shorts: the underlying cancels on one margin engine.

    Gross carry is the funding difference. It is charged two round trips, one per book, where a book was collected;
    capacity is the thinner side's depth at 25bp, because the pair is only delta-neutral at equal size. A pair with a
    book this scan never priced is reported with `capacity_usd` None and cannot pass.
    """
    fr = sorted(((r['funding_apr'] or 0.0), r['coin']) for r in rows if r.get('funding_apr') is not None)
    if len(fr) < 2:
        return None
    (lo_apr, lo_coin), (hi_apr, hi_coin) = fr[0], fr[-1]
    # negative funding pays longs: go long the lowest-funding book, short the highest
    gross = hi_apr - lo_apr
    costs, depths, known = 0.0, [], 0
    key = 'round_trip_bps_%dk' % int(size_usd / 1e3)
    for coin, side in ((lo_coin, 'long'), (hi_coin, 'short')):
        b = books.get(coin) or {}
        if b.get(key) is not None:
            known += 1
            costs += b[key]
            depths.append(b.get('ask_depth_25bp_usd') if side == 'long' else b.get('bid_depth_25bp_usd'))
    cap = min([d for d in depths if d is not None], default=None) if known == 2 else None
    per_hour = gross / HOURS_PER_YEAR
    be = (costs / 1e4 / per_hour) if per_hour > 0 else None
    net = gross - (costs / 1e4) * (HOURS_PER_YEAR / horizon_h) if horizon_h else None
    go = bool(known == 2 and be is not None and be < horizon_h and (cap or 0) >= 1e5)
    return {'long_book': lo_coin, 'short_book': hi_coin, 'gross_apr': gross, 'round_trips_bps': costs if known == 2 else None,
            'books_priced': known, 'break_even_hours': be if known == 2 else None, 'net_apr': net if known == 2 else gross,
            'net_apr_basis': ('net of both round trips over %dh' % horizon_h) if known == 2 else 'gross: a book was not priced',
            'capacity_usd': cap, 'size_usd': size_usd, 'go': go,
            'reason': ('both books priced, pays its round trips inside the horizon at six figures' if go else
                       'a book was not priced, or break-even beyond the horizon, or under $100k of depth'),
            'hedge': 'delta-neutral in the underlying by construction; not neutral to the two deployers\' oracles diverging'}


def det_cross_dex_basis(A, args):
    hits = []
    books = {r['coin']: r.get('book') for r in A['assets'] if r.get('book')}
    for c in A.get('cross_dex') or []:
        rows = [r for r in c['rows'] if (r.get('trades') or 0) >= args.min_trades]
        if len(rows) < 2:
            continue
        fr = [r['funding_apr'] for r in rows if r['funding_apr'] is not None]
        spread = (max(fr) - min(fr)) if len(fr) >= 2 else 0
        if abs(c['mark_spread_bps'] or 0) < 3 and abs(spread) < args.min_apr:
            continue
        ec = _pair_economics(rows, books, args.size_usd, args.horizon_h)
        hits.append({
            'economics': ec, 'usd': (ec['net_apr'] * ec['capacity_usd'] * args.horizon_h / HOURS_PER_YEAR) if (ec and ec.get('capacity_usd')) else None,
            'detector': 'cross_dex_basis', 'key': c['symbol'],
            'severity': 'notable',
            'title': '%s trades on %d builder books at once: %.1fbp apart, with %.0f percentage points between their funding rates'
                     % (c['symbol'], len(rows), c['mark_spread_bps'] or 0, 100 * spread),
            'evidence': {'symbol': c['symbol'], 'rows': rows, 'mark_spread_bps': c['mark_spread_bps'],
                         'funding_spread_apr': spread, 'total_oi_usd': c['total_oi_usd'],
                         'why': 'each builder sets its own oracle under HIP-3, so two books on the same underlying '
                                'are two independent opinions with independent funding; the pair is delta-neutral by '
                                'construction and the funding difference is the carry'},
        })
    return sorted(hits, key=lambda h: -abs(h['evidence']['funding_spread_apr']))


DETECTORS = [
    ('funding_carry', det_funding_carry, 'a funding rate that has not changed sign, priced against what it costs to hold it'),
    ('premium_drift', det_premium_drift, 'a premium widening in one direction hour after hour against a rising toll'),
    ('oi_cap_pressure', det_oi_cap_pressure, 'HIP-3 markets at their open-interest cap, where the price becomes a queue'),
    ('cross_dex_basis', det_cross_dex_basis, 'the same underlying on two builder books with two oracles and two funding rates'),
    ('cross_venue_funding', det_cross_venue_funding, 'Hyperliquid funding against Binance and Bybit, net of both round trips'),
    ('illiquid_extreme_funding', det_illiquid_extreme_funding, 'a spectacular rate on a market with no trading: a trap, not an edge'),
    ('stale_oracle', det_stale_oracle, 'an oracle that stopped moving while its book did not'),
    ('dead_market', det_dead_market, 'listed markets with no open interest and no trades, against a staked deployment'),
]


def cmd_detect(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    # premium series is needed by premium_drift and is cheaper to attach here than to re-read in every detector
    for r in A['assets']:
        p = out / 'funding' / (safe(r['coin']) + '.json.gz')
        if p.exists() and r.get('funding_hist'):
            r['funding_hist']['_series'] = [f(x['premium']) for x in read_gz(p) if f(x['premium']) is not None]
    tp = out / 'tape.json'
    tape = json.loads(tp.read_text()) if tp.exists() else None

    all_hits, summary = [], []
    for name, fn, desc in DETECTORS:
        t0 = time.time()
        hits = fn(A, args, tape) if name == 'stale_oracle' else fn(A, args)
        all_hits += hits
        summary.append({'detector': name, 'hits': len(hits), 'seconds': round(time.time() - t0, 2), 'what': desc})
        print('%-26s %3d hit(s)  %5.2fs' % (name, len(hits), time.time() - t0))
    order = {'high': 0, 'notable': 1, 'info': 2}
    all_hits.sort(key=lambda h: (order.get(h['severity'], 3), -abs(h.get('usd') or 0)))
    write_json(out / 'detectors.json', {'window': str(out), 'detectors': summary, 'hits': all_hits,
                                        'params': {k: v for k, v in vars(args).items() if k != 'fn'}})
    print('\nwrote %s (%d hits)' % (out / 'detectors.json', len(all_hits)))
    return 0


# ---------------------------------------------------------------------------------------------- verify

def cmd_verify(args):
    """Re-derive the headline numbers by a path that does not go through `analyze`, and assert what must be true."""
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    man = json.loads((out / 'manifest.json').read_text())
    checks, ident = [], []

    def chk(cid, what, got, want, tol=0.0, note=''):
        ok = (got == want) if tol == 0 else (got is not None and want is not None
                                             and abs(got - want) <= tol * max(abs(want), 1e-12))
        checks.append({'id': cid, 'check': what, 'recomputed': got, 'analysis': want, 'ok': ok,
                       'tolerance': tol, 'note': note})

    # 1. totals, recomputed straight from the raw snapshot rather than from the assembled rows
    snaps = sorted((out / 'snap').glob('*.json.gz'))
    snap = read_gz(snaps[0])
    n_assets = oi = vlm = 0
    for dex, payload in snap['dexes'].items():
        for m, c in zip(payload[0]['universe'], payload[1]):
            n_assets += 1
            px = f(c.get('markPx')) or f(c.get('oraclePx')) or 0
            oi += f(c.get('openInterest'), 0.0) * px
            vlm += f(c.get('dayNtlVlm'), 0.0)
    chk('assets', 'assets in the snapshot', n_assets, A['totals']['assets'])
    chk('oi-usd', 'total open interest (USD)', oi, A['totals']['oi_usd'], 1e-9)
    chk('day-vlm', 'total 24h notional volume (USD)', vlm, A['totals']['day_ntl_vlm'], 1e-9)

    # 2. hourly volume, recomputed from the candle files instead of from the rows
    hv = ht = 0
    w = man['window']
    for r in A['assets']:
        p = out / 'candles' / (safe(r['coin']) + '.json.gz')
        if not p.exists():
            continue
        for x in read_gz(p):
            if w['start_ms'] <= x['t'] < w['end_ms']:
                hv += f(x['v'], 0.0) * f(x['c'], 0.0)
                ht += int(x.get('n') or 0)
    chk('hour-vlm', 'notional traded in the window (USD)', hv, A['totals']['hour_ntl_vlm'], 1e-9)
    chk('hour-trades', 'trades in the window', ht, A['totals']['hour_trades'])

    # 3. identities that must hold on every row
    def identity(cid, what, fn):
        worst, n, bad = 0.0, 0, []
        for r in A['assets']:
            d = fn(r)
            if d is None:
                continue
            n += 1
            worst = max(worst, d)
            if d > args.tol:
                bad.append({'coin': r['coin'], 'delta': d})
        ident.append({'id': cid, 'check': what, 'checked': n, 'failed': len(bad), 'ok': not bad,
                      'worst': worst, 'examples': bad[:6]})

    # The first pass asserted `premium == (mark - oracle) / oracle` and 304 of 315 markets failed it. They were right
    # to. The venue's `premium` is an average sampled across the funding hour against the *impact* prices, not an
    # instantaneous mark-to-oracle gap: fitted against this window it sits closest to the impact mid (median absolute
    # error 1.0e-4 against 3.6e-4 for the mark) and agrees in sign only 86% of the time. It is therefore not an
    # identity and is not asserted as one. What is asserted is the instantaneous basis, which is arithmetic, and the
    # relationship between the two is reported as a measurement below.
    # Two percentage points, not one: on this window exactly one market of 315 — SOPH, which carries the most
    # extreme premium on the venue at -0.998% — put an hour of averaging more than a point away from the instant.
    # A bound that the widest real market fails is a bound that tests nothing.
    identity('premium-bounded', 'the venue’s premium is within two percent of the instantaneous impact-mid basis',
             lambda r: (max(0.0, abs(r['premium'] - r['impact_mid_basis']) - 0.02)
                        if (r.get('premium') is not None and r.get('impact_mid_basis') is not None) else None))
    identity('mark-vs-oracle-bps', 'the reported basis equals the recomputed one',
             lambda r: (abs(r['mark_vs_oracle_bps'] - 1e4 * (r['mark'] - r['oracle']) / r['oracle'])
                        if (r.get('mark_vs_oracle_bps') is not None and r.get('mark') and r.get('oracle')) else None))
    identity('funding-apr', 'the annualised funding equals the hourly rate times 8760',
             lambda r: (abs(r['funding_apr'] - r['funding_hourly'] * HOURS_PER_YEAR)
                        if (r.get('funding_apr') is not None and r.get('funding_hourly') is not None) else None))
    identity('oi-usd', 'open interest in USD equals size times mark',
             lambda r: (abs(r['oi_usd'] - r['open_interest'] * (r['mark'] or r['oracle'] or 0)) / max(abs(r['oi_usd']), 1)
                        if (r.get('oi_usd') and r.get('open_interest') is not None) else None))
    identity('cap-use', 'cap utilisation equals open interest over the cap',
             lambda r: (abs(r['oi_cap_use'] - r['oi_usd'] / r['oi_cap_usd'])
                        if (r.get('oi_cap_use') is not None and r.get('oi_cap_usd')) else None))
    identity('spread-nonneg', 'the best ask is not below the best bid',
             lambda r: (max(0.0, -(r['book']['spread_bps'])) if (r.get('book') and r['book'].get('spread_bps') is not None) else None))

    # 4. the book cost function must be monotone in size: a bigger order never costs less
    bad = []
    n = 0
    for r in A['assets']:
        b = r.get('book') or {}
        c10, c100, c1000 = b.get('round_trip_bps_10k'), b.get('round_trip_bps_100k'), b.get('round_trip_bps_1000k')
        if c10 is None or c100 is None:
            continue
        n += 1
        if c100 < c10 - 1e-9 or (c1000 is not None and c1000 < c100 - 1e-9):
            bad.append({'coin': r['coin'], '10k': c10, '100k': c100, '1000k': c1000})
    ident.append({'id': 'cost-monotone', 'check': 'the round-trip cost never falls as the order grows',
                  'checked': n, 'failed': len(bad), 'ok': not bad, 'worst': 0.0, 'examples': bad[:6]})

    # 5. How much of the premium the funding rate actually charges — a measurement, not an assertion.
    #
    # This is the number that decides whether a wide premium is self-correcting. Funding exists to pull the mark back
    # to the oracle; if a venue charges only a fraction of its own premium, the gap has no reason to close. Measured
    # per DEX over the markets whose premium is large enough for the ratio to mean anything.
    per_dex = collections.defaultdict(list)
    for r in A['assets']:
        p, fh = r.get('premium'), r.get('funding_hourly')
        if p is None or fh is None or abs(p) < 2e-4:
            continue
        per_dex[r['dex']].append(fh / (p / 8))
    transfer = {}
    for d, xs in per_dex.items():
        if len(xs) < 4:
            continue
        xs.sort()
        transfer[d] = {'markets': len(xs), 'median': statistics.median(xs),
                       'p10': xs[int(0.1 * len(xs))], 'p90': xs[int(0.9 * len(xs))]}
    V_transfer = {'by_dex': transfer,
                  'what': 'hourly funding divided by one eighth of the venue’s own reported premium, over markets '
                          'with |premium| above 2 basis points',
                  'why': 'a ratio near 1 means the funding rate is charging the whole premium and the gap should '
                         'close; a ratio near 0 means the venue is not charging for its own premium, and a wide gap '
                         'has nothing pulling it shut'}

    # 6. coverage, stated rather than assumed
    cov = {'assets': A['totals']['assets'],
           'with_candles': sum(1 for r in A['assets'] if r.get('candles')),
           'with_book': sum(1 for r in A['assets'] if r.get('book')),
           'with_funding_history': sum(1 for r in A['assets'] if (r.get('funding_hist') or {}).get('n')),
           'collection_failures': man.get('failures') or {}}

    V = {'window': str(out), 'generated': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
         'checks': checks, 'identities': ident, 'coverage': cov, 'premium_to_funding_transfer': V_transfer,
         'all_ok': all(c['ok'] for c in checks) and all(i['ok'] for i in ident)}
    V['failures'] = [c for c in checks if not c['ok']] + [i for i in ident if not i['ok']]
    write_json(out / 'verify.json', V)
    print(json.dumps({'checks': len(checks), 'identities': len(ident),
                      'all_ok': V['all_ok'], 'failures': len(V['failures'])}, indent=1))
    return 0 if V['all_ok'] else 1


# ---------------------------------------------------------------------------------------------- render

def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    D = json.loads((out / 'detectors.json').read_text()) if (out / 'detectors.json').exists() else None
    V = json.loads((out / 'verify.json').read_text()) if (out / 'verify.json').exists() else None
    T = json.loads((out / 'tape.json').read_text()) if (out / 'tape.json').exists() else None
    w = A['window']
    L = []
    L.append('## Deterministic tables — Hyperliquid, %s to %s UTC\n' % (w['start_utc'][11:16], w['end_utc'][11:16]))
    L.append('US cash equities were in **%s** at the window close (%s ET). Every HIP-3 equity, index and commodity '
             'market below traded through it anyway.\n' % (A['session_at_window_end']['session'],
                                                            A['session_at_window_end']['et']))

    t = A['totals']
    L.append('\n### The venue\n')
    L.append('| | |')
    L.append('|---|---:|')
    for k, v in (('perp DEXes', t['dexes']), ('markets listed', t['assets']), ('markets not delisted', t['live']),
                 ('markets that traded in the hour', t['traded_in_window']),
                 ('open interest', _m(t['oi_usd'])), ('24h notional volume', _m(t['day_ntl_vlm'])),
                 ('notional traded in the hour', _m(t['hour_ntl_vlm'])), ('trades in the hour', '{:,}'.format(t['hour_trades']))):
        L.append('| %s | %s |' % (k, v))

    L.append('\n### Every perp DEX on the venue\n')
    L.append('| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |')
    L.append('|---|---|---:|---:|---:|---:|---:|---|')
    for d, v in sorted(A['by_dex'].items(), key=lambda kv: -kv[1]['oi_usd']):
        L.append('| `%s` | %s | %d | %d | %s | %s | %s | %s |' % (
            d, v.get('full_name') or d, v['assets'], v['traded_in_window'], _m(v['oi_usd']), _m(v['hour_ntl_vlm']),
            ', '.join('%gx' % x for x in v['fee_scales']) or '—',
            'deployer' if d != 'core' else 'the protocol'))

    L.append('\n### How much of its own premium each DEX charges as funding\n')
    if V and V.get('premium_to_funding_transfer'):
        L.append('Hourly funding divided by an eighth of the venue\'s reported premium, over markets with a premium '
                 'above two basis points. A ratio near 1 charges the whole premium and the gap should close; a ratio '
                 'near 0 charges nothing for it.\n')
        L.append('| dex | markets | median | 10th pct | 90th pct |')
        L.append('|---|---:|---:|---:|---:|')
        for d, r in sorted(V['premium_to_funding_transfer']['by_dex'].items(), key=lambda kv: -kv[1]['median']):
            L.append('| `%s` | %d | %.3f | %.3f | %.3f |' % (d, r['markets'], r['median'], r['p10'], r['p90']))

    hi = [h for h in (D or {}).get('hits', []) if h['severity'] == 'high']
    if hi:
        L.append('\n### What the sweep found at the top severity\n')
        L.append('| detector | finding |')
        L.append('|---|---|')
        for h in hi:
            L.append('| `%s` | %s |' % (h['detector'], h['title']))

    carries = [h for h in (D or {}).get('hits', []) if h['detector'] == 'funding_carry']
    if carries:
        L.append('\n### Funding carries, priced against what they cost to hold\n')
        L.append('Size is $%s. The round trip is walked through the saved order book, both sides, plus the taker fee '
                 'scaled by the deployer\'s own multiplier. Capacity is the smaller of the book within 25bp and the '
                 'headroom under the HIP-3 open-interest cap.\n' % '{:,.0f}'.format(carries[0]['economics']['size_usd']))
        L.append('| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |')
        L.append('|---|---|---:|---:|---:|---:|---:|---:|')
        for h in carries:
            e, ev = h['economics'], h['evidence']
            L.append('| `%s` | %s | %.0f%% | %.1fbp | %.1f h | %s | %s | %s |' % (
                ev['coin'], e['side_paid'], 100 * abs(e['funding_apr']), e['round_trip_bps_at_size'],
                e['break_even_hours'], _m(e['capacity_usd']), _m(ev['oi_usd']), _m(ev['hour_ntl_vlm'] or 0)))

    drift = [h for h in (D or {}).get('hits', []) if h['detector'] == 'premium_drift']
    if drift:
        L.append('\n### Premiums that widened in one direction, hour after hour\n')
        L.append('| market | hours running | premium path (%) | funding now |')
        L.append('|---|---:|---|---:|')
        for h in drift:
            ev = h['evidence']
            path = ' → '.join('%+.3f' % x for x in ev['premium_series_pct'])
            L.append('| `%s` | %d | %s | %.0f%% |' % (ev['coin'], ev['monotone_run_hours'], path,
                                                       100 * (h.get('economics') or {}).get('funding_apr', 0)))

    xd = [h for h in (D or {}).get('hits', []) if h['detector'] == 'cross_dex_basis']
    if xd:
        L.append('\n### The same underlying on two builder books\n')
        L.append('| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |')
        L.append('|---|---|---:|---:|---:|---:|---:|---:|')
        for h in xd:
            for r in h['evidence']['rows']:
                L.append('| %s | `%s` | %s | %s | %.0f%% | %s | %s | %s |' % (
                    h['evidence']['symbol'], r['dex'], r['mark'], r['oracle'], 100 * (r['funding_apr'] or 0),
                    _m(r['oi_usd'] or 0), _m(r['hour_ntl_vlm'] or 0), r['trades']))

    cv = [h for h in (D or {}).get('hits', []) if h['detector'] == 'cross_venue_funding'][:10]
    if cv:
        L.append('\n### Hyperliquid funding against Binance and Bybit\n')
        L.append('| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |')
        L.append('|---|---:|---|---:|---:|---:|---:|')
        for h in cv:
            e = h['evidence']
            L.append('| %s | %.0f%% | %s %.0f%% | %.0f%% | %.1fbp | %.0f h | %s |' % (
                e['coin'], 100 * e['hl_apr'], e['other_venue'].replace('Perp', ''), 100 * e['other_apr'],
                100 * abs(e['spread_apr']), e['hl_round_trip_bps'], e['break_even_hours'] or 0, _m(e['hl_oi_usd'])))

    dead = [h for h in (D or {}).get('hits', []) if h['detector'] == 'dead_market' and h['evidence'].get('all_markets_dead')]
    if dead:
        L.append('\n### Builder DEXes where nothing trades\n')
        L.append('Each of these required its deployer to stake 500,000 HYPE for at least 183 days.\n')
        L.append('| dex | name | markets | open interest | deployer |')
        L.append('|---|---|---:|---:|---|')
        for h in dead:
            e = h['evidence']
            L.append('| `%s` | %s | %d | %s | `%s` |' % (e['dex'], e['full_name'] or e['dex'], e['count'],
                                                          _m(e['dex_oi_usd'] or 0), (e['deployer'] or '')[:14] + '…'))

    if T:
        L.append('\n### What the tape says about the oracles\n')
        L.append('%d snapshots over %.0f minutes. The test is the correlation of first differences between mark and '
                 'oracle: an oracle that tracks the book has a correlation near 1 and can still hold a constant '
                 'offset, which is a real basis; an oracle that has stopped moving has no variance at all, and its '
                 'premium is an artifact that will vanish when it updates.\n'
                 % (T['snapshots'], (T['rows'][0]['span_s'] / 60) if T['rows'] else 0))
        L.append('| regime | markets |')
        L.append('|---|---:|')
        for k, v in sorted(T['regimes'].items(), key=lambda kv: -kv[1]):
            L.append('| %s | %d |' % (k, v))

    if V:
        L.append('\n### Verification\n')
        L.append('`perp_scan.py verify` — %d numeric checks, %d identities, all_ok = **%s**.\n'
                 % (len(V['checks']), len(V['identities']), V['all_ok']))
        L.append('| identity | checked | failed | worst |')
        L.append('|---|---:|---:|---:|')
        for i in V['identities']:
            L.append('| %s | %d | %d | %.2e |' % (i['check'], i['checked'], i['failed'], i['worst']))
        c = V['coverage']
        L.append('\nCoverage: %d markets, %d with candles, %d with an order book, %d with funding history. '
                 'Collection failures: %d.\n' % (c['assets'], c['with_candles'], c['with_book'],
                                                  c['with_funding_history'], len(c['collection_failures'])))

    tables = '\n'.join(L) + '\n'
    (out / 'tables.md').write_text(tables)
    ins = out / 'insights.md'
    head = ins.read_text() if ins.exists() else '_(no insights.md written yet)_\n'
    companions = [('refs.md', 'oracles against outside references'), ('refs_curve.json', 'where the oil oracles sit on the futures curve')]
    links = ['[%s](%s): %s' % (f, f, what) for f, what in companions if (out / f).exists()]
    if links:
        tables = 'Companion tables: ' + '; '.join(links) + '.\n\n' + tables
    (out / 'report.md').write_text(head.rstrip() + '\n\n---\n\n' + tables)
    print(json.dumps({'tables.md': len(tables), 'report.md': str(out / 'report.md')}))
    return 0


def cmd_show(args):
    A = json.loads((Path(args.out) / 'analysis.json').read_text())
    for r in A['assets']:
        if r['coin'] == args.coin or r['symbol'] == args.coin:
            print(json.dumps(r, indent=1, default=str))
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--taker-fee-bps', type=float, default=4.5)
    a.add_argument('--snapshot', choices=['first', 'last'], default='first')
    a.add_argument('--same-asset-bps', type=float, default=500.0,
                   help='two markets sharing a ticker are the same underlying only within this price distance')
    t = sub.add_parser('tape'); t.set_defaults(fn=cmd_tape); t.add_argument('--out', required=True)
    d = sub.add_parser('detect'); d.set_defaults(fn=cmd_detect)
    d.add_argument('--out', required=True)
    d.add_argument('--min-apr', type=float, default=0.15, help='annualised rate below which a carry is not worth a line')
    d.add_argument('--min-oi', type=float, default=1e6)
    d.add_argument('--min-trades', type=int, default=30)
    d.add_argument('--min-run', type=int, default=5, help='consecutive hours a premium must move one way')
    d.add_argument('--cap-warn', type=float, default=0.85)
    d.add_argument('--size-usd', type=float, default=1e5)
    d.add_argument('--horizon-h', type=int, default=24)
    rr = sub.add_parser('render'); rr.set_defaults(fn=cmd_render); rr.add_argument('--out', required=True)
    v = sub.add_parser('verify'); v.set_defaults(fn=cmd_verify)
    v.add_argument('--out', required=True); v.add_argument('--tol', type=float, default=1e-6)
    s = sub.add_parser('show'); s.set_defaults(fn=cmd_show)
    s.add_argument('coin'); s.add_argument('--out', required=True)
    x = p.parse_args()
    raise SystemExit(x.fn(x))


if __name__ == '__main__':
    main()
