#!/usr/bin/env python3
"""The cheapest place to borrow each dollar, and how much of it you could actually borrow there.

The last hand-measured strategy in this repo's book was "borrow USDT on Morpho rather than Aave", quoted at 91bp on
$24M from a single afternoon in September and never re-measured. It was also the largest number in the book by annual
value, which is a poor combination: the biggest claim resting on the oldest reading.

Borrowing inverts two habits from the supply side. The venue you want is the *cheapest*, not the dearest. And the
constraint is **available liquidity**, not the size of the market: a lending market at 99% utilisation quoting a cheap
rate is quoting a rate on nothing, and Morpho's isolated markets make that visible in a way a single pooled reserve
does not. So every rate here is paired with what is actually withdrawable behind it, and the saving is capped by that
rather than by the market's headline size.

Three frictions are priced or stated rather than assumed away:

  * **Refinancing costs gas twice** and is a one-off against a saving that accrues, so a small debt never justifies it;
    the break-even notional is reported.
  * **A Morpho market is isolated**, so its rate is available only against the collateral that market accepts. Moving
    a position from Aave to a Morpho market means moving the collateral too, and the accepted collateral is named in
    the evidence because it is usually the binding constraint rather than the rate.
  * **The cheap rate is often somebody's allocation**, not a standing condition. Spark's liquidity layer moves USDT
    between its own products on a schedule, and each allocation into the Morpho vault drops that market's rate until
    borrowers arrive. The saving is real and it is not permanent, which is what the ledger's decay column is for.
"""
from . import Hit
from economics import Opportunity, Leg, score

NAME = 'borrow_cost'
DESCRIPTION = 'cheapest venue to borrow each asset, capped by the liquidity actually withdrawable there'
SEVERITY = 'notable'

MIN_GAP = 0.0025        # 25bps: below this two refinancing legs and the spread eat the saving
MIN_LIQUIDITY = 1e6     # a venue with less than this withdrawable cannot take a position worth moving
REFINANCE_GAS = 900_000  # repay + withdraw collateral + supply + borrow, across two venues
DOLLARS = {'USDC', 'USDT', 'DAI', 'USDS', 'USDe', 'GHO', 'PYUSD', 'RLUSD', 'USDG', 'USDtb', 'crvUSD', 'FRAX'}


def scan(ctx):
    head = _head(ctx)
    if not head:
        return []
    venues = _venues(head, ctx)
    gas_gwei = _gas(ctx)
    eth = ctx.prices.get('ETH') or 2500.0

    hits = []
    for sym, rows in venues.items():
        live = [r for r in rows if r['liquidity_usd'] >= MIN_LIQUIDITY and r['borrow_apy'] is not None]
        if len(live) < 2:
            continue
        lo = min(live, key=lambda r: r['borrow_apy'])
        hi = max(live, key=lambda r: r['borrow_apy'])
        gap = hi['borrow_apy'] - lo['borrow_apy']
        if gap < MIN_GAP:
            continue
        cap = lo['liquidity_usd']
        v = score(Opportunity(
            name='borrow %s on %s rather than %s' % (sym, lo['venue'], hi['venue']),
            edge_bps=1e4 * gap,
            legs=[Leg('borrow %s from %s' % (sym, lo['venue']), capacity_usd=cap)],
            gas_units=REFINANCE_GAS, capital_locked_usd=None, capital_days=365, runs_per_day=1 / 365,
            competitors=0,
            notes='the saving accrues on the debt while the refinance is a one-off gas cost, so the break-even '
                  'notional below is the number that decides whether to move a given position. The cheap rate is '
                  'capped by what is withdrawable there, not by the market’s size.'),
            gas_gwei=gas_gwei, eth_usd=eth, min_net_usd=0.0)
        hits.append(Hit(
            detector=NAME, key='%s:%s/%s' % (sym, lo['venue'], hi['venue']),
            severity='notable' if v.go else 'info', usd=v.annual_net_usd,
            # At a 0.05 gwei base fee the refinance costs about eleven cents, so a break-even of "$8 of debt" is
            # arithmetically right and tells the reader nothing. Quote it only when gas is actually a constraint;
            # otherwise say what the real one is.
            title='%s borrows %.2fpp cheaper on %s than %s; $%s withdrawable there, %s'
                  % (sym, 100 * gap, lo['venue'], hi['venue'], _m(cap),
                     ('break-even at $%s of debt' % _m(v.break_even_size_usd))
                     if (v.break_even_size_usd or 0) >= 1000 else
                     'gas is negligible at this base fee — the constraint is the collateral and the liquidity'),
            evidence={'asset': sym,
                      'cheapest': {'venue': lo['venue'], 'borrow_apy_pct': round(100 * lo['borrow_apy'], 3),
                                   'liquidity_usd': round(lo['liquidity_usd']),
                                   'utilisation': lo.get('utilisation'),
                                   'collateral_required': lo.get('collateral'), 'market': lo.get('market')},
                      'dearest': {'venue': hi['venue'], 'borrow_apy_pct': round(100 * hi['borrow_apy'], 3),
                                  'liquidity_usd': round(hi['liquidity_usd'])},
                      'all_venues': sorted(({'venue': r['venue'], 'borrow_apy_pct': round(100 * r['borrow_apy'], 3),
                                             'liquidity_usd': round(r['liquidity_usd']),
                                             'collateral': r.get('collateral')} for r in live),
                                           key=lambda r: r['borrow_apy_pct']),
                      'gap_pp': round(100 * gap, 3),
                      'refinance_gas_usd': round(REFINANCE_GAS * _gas(ctx) * 1e-9 * (ctx.prices.get('ETH') or 2500), 3),
                      'caveat': 'moving a position between venues also pays the spread on any collateral that has to '
                                'be converted, which this does not price: it compares rates and liquidity only',
                      'why': 'the saving is capped by what is withdrawable at the cheap venue, and on an isolated '
                             'market it is only available against the collateral that market accepts — which is '
                             'usually the binding constraint rather than the rate'},
            economics={'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                       'go': v.go, 'reason': v.reason, 'capacity_usd': round(cap),
                       'break_even_size_usd': round(v.break_even_size_usd) if v.break_even_size_usd else None}))
    hits.sort(key=lambda h: -(h.usd or 0))
    return hits


def _sym(ctx, addr):
    """A collateral address as a symbol where the token table knows it. The accepted collateral is the binding
    constraint on an isolated market, so it has to be readable, not a hex string."""
    return ctx.window.symbol((addr or '').lower()) or (addr or '')[:12]


def _venues(head, ctx):
    """symbol -> [{venue, borrow_apy, liquidity_usd, ...}] across Aave, SparkLend, Compound and Morpho Blue."""
    import collections
    out = collections.defaultdict(list)
    for venue, reserves in (head.get('lending') or {}).items():
        for _, d in reserves.items():
            sym, sup, bor = d.get('sym'), d.get('supplied_usd'), d.get('borrowed_usd')
            if sym not in DOLLARS or not sup or d.get('borrow_apr') is None:
                continue
            out[sym].append({'venue': venue, 'borrow_apy': d['borrow_apr'], 'liquidity_usd': sup - (bor or 0),
                             'utilisation': d.get('utilisation'), 'collateral': 'any listed on the pool'})
    for venue, d in (head.get('compound') or {}).items():
        sym = venue.replace('Compound v3 ', '')
        if sym not in DOLLARS or d.get('borrow_apr') is None or not d.get('supplied'):
            continue
        out[sym].append({'venue': venue, 'borrow_apy': d['borrow_apr'],
                         'liquidity_usd': (d['supplied'] - (d.get('borrowed') or 0)),
                         'utilisation': d.get('utilisation'), 'collateral': 'the Comet’s listed collaterals'})
    # Morpho: each isolated market is its own venue, so the cheapest *market* with real liquidity is what competes.
    best = {}
    for mid, m in (head.get('morpho') or {}).items():
        sym = m.get('sym')
        if sym not in DOLLARS or m.get('borrow_apy') is None:
            continue
        liq = m['liquidity']          # loan units; dollar markets price at ~1
        cur = best.get(sym)
        if liq >= MIN_LIQUIDITY and (cur is None or m['borrow_apy'] < cur['borrow_apy']):
            best[sym] = {'venue': 'Morpho Blue', 'borrow_apy': m['borrow_apy'], 'liquidity_usd': liq,
                         'utilisation': m.get('utilisation'), 'market': mid[:18],
                         'collateral': '%s (%s, LLTV %.1f%%)' % (_sym(ctx, m.get('collateral')),
                                                                 (m.get('collateral') or '')[:10],
                                                                 100 * (m.get('lltv') or 0))}
    for sym, r in best.items():
        out[sym].append(r)
    return out


def _head(ctx):
    import json
    p = ctx.out / 'head_state.json'
    return json.loads(p.read_text()) if p.exists() else None


def _gas(ctx):
    return ctx.gas_quote()['gwei']


def _m(v):
    v = v or 0
    for unit, scale in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= scale:
            return format(round(v / scale, 1), ',') + unit
    return format(round(v), ',')
