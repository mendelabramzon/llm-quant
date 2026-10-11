#!/usr/bin/env python3
"""Accepted collateral on every venue, day by day, and the same-venue carry each collateral asset would pay.

Why. The 2026-10-10/11 synthesis (research/2026-10-10/rents_and_resources.md, lesson 3) found the largest persistent
rents in the funding formulas' interest leg: Hyperliquid funding sits exactly at the formula's interest rate (10.95% a
year) on 71.6% of open-interest-weighted hours, Binance's VELO on 90% of settlements. The rent stays uncollected because
arbitrage capital has to sit on two venues. It becomes collectable the day a venue accepts the spot asset (or its
staking token) as margin: the spot leg then *is* the short's collateral, so holding spot and shorting the same venue's
perp earns funding on almost no extra capital. The book's best carry (HYPE on Hyperliquid portfolio margin) exists only
because Hyperliquid accepts HYPE. Every addition to any venue's collateral list is a potential new same-venue carry at
the formula rate, so the lists are read daily and every accepted asset is priced as a carry.

How.
  snapshot  Per venue, the accepted collateral with its collateral ratio (1 - haircut), tiers where public, and borrow
            rates: Hyperliquid portfolio margin from the info API (`allBorrowLendReserveStates`: LTV, borrow and supply
            rates, utilisation), its docs page (caps, rate formula; one hash per section) and every HIP-3 dex's
            collateral token (`perpDexs`, `meta`); Binance portfolio margin (classic rates and the Pro tiers, public
            bapi endpoints), multi-assets mode (`/fapi/v1/assetIndex` bid buffers of the `marginAvailable` assets) and
            margin borrow rates; OKX discount-rate tiers and loan rates; Bybit UTA tiered collateral ratios and borrow
            rates; Deribit cross collateral (`get_currencies`), X:PM haircuts (`pme/get_params`) and the X:SM haircut
            table of its support article (hashed). Raw responses are kept gzip'd beside a normalised table
            (collateral.json) under research/collateral_watch/YYYY-MM-DD/.
  diff      The newest snapshot against the previous one, program by program: assets added or removed, collateral
            ratio or tiers changed, a HIP-3 dex's collateral token changed, a docs section's hash changed. One row per
            event appended to research/collateral_events.jsonl (never rewritten; a rerun does not duplicate rows).
  carry     Every collateral asset with a perp on the same venue (directly, by a 1000x ticker, as the venue's stock
            token, or as a wrapped or staking token of the perp's underlying): trailing 7- and 30-day funding APR from
            the venue's public history, the share of settlements exactly at the formula's interest leg (0.01% per 8 h
            scaled to the interval: 0.005% per 4 h on Binance/Bybit/OKX, 0.00125% an hour on Hyperliquid = 10.95% a
            year; Binance TradFi perps and Deribit have none, so their floor is 0), capital per $ of short, borrow cost,
            and the excess over the savings rate on that capital. Rows above 2pp get a depth check: $1M on both legs
            within 25bp of mid.

Capital. Long spot N and short perp N in one account; the spot counts as collateral at ratio c (Hyperliquid: its LTV),
read at a $1M holding where the ratio is tiered. The account must still carry the short's initial margin
im = max(1/10, 1/max leverage) after a rally of R = 50% without a top-up: c(1+R)N + C >= (im + R)N, so the capital per
$ of short is K = 1 + max(0, im + R - c(1+R)); the extra cash C earns nothing here. Hyperliquid borrows the short's
margin against the spot (docs: "only pays interest on the 1/10 initial margin"), so the borrow cost there is the USDC
borrow APR x im. The CEXs and Deribit charge only negative balances (realised losses; OKX and Deribit also unrealised
ones), which a carry does not have at entry, so 0; their rates are recorded. Excess = (funding APR - borrow cost +
known collateral yield) / K - SSR, gross of trading costs, with SSR the book's protocol benchmark term_carry.SSR
(3.80% a year, a constant).

    uv run python scripts/collateral_watch.py snapshot          # research/collateral_watch/<UTC date>/
    uv run python scripts/collateral_watch.py snapshot --from-raw --day 2026-10-11   # re-normalise saved raw only
    uv run python scripts/collateral_watch.py diff              # -> research/collateral_events.jsonl
    uv run python scripts/collateral_watch.py carry             # carry.json.gz, tables.md, manifest.json in the day's dir
    uv run python scripts/collateral_watch.py run               # all three and one summary line: the daily job
    uv run python scripts/collateral_watch.py run --out research/2026-10-11/collateral_watch   # plain carry.json there

Read-only: public, unauthenticated endpoints only; nothing is signed or sent. Hyperliquid through perp_rpc.Info at
0.5 s a call (the IP is shared with other jobs); Binance funding history at 0.65 s a call (500 per 5 minutes per IP).
"""
import argparse
import collections
import datetime as dt
import hashlib
import html
import html.parser
import json
import re
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import gold_carry as G   # noqa: E402  (paced GET, depth within a band, gzip/json writers)
import term_carry as TC  # noqa: E402  (SSR, the book's protocol benchmark)

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
WATCH = ROOT / 'research' / 'collateral_watch'
EVENTS = ROOT / 'research' / 'collateral_events.jsonl'
HL_STORE = ROOT / 'research' / '2026-09-10' / 'perps_history' / 'funding'      # perp_daily's accumulating store
TERM_CARRY = ROOT / 'research' / '2026-10-10' / 'term_carry' / 'analysis.json'

SSR = TC.SSR                  # 3.80% a year, constant: the benchmark of every row in the book
STRESS_RALLY = 0.5            # the rally the account must survive without a top-up or a rebalance
TARGET_LEV = 10.0             # the short's leverage: the docs' own carry example (and term_carry's HL_PM_MARGIN)
SIZE_USD = 1_000_000          # tiered ratios are read at this holding; the depth check asks for this much
DEPTH_BP = 25
FLAG_EXCESS = 0.02
DEPTH_CHECKS = 30             # rows above the flag whose books are read, per venue, by the perp's 24 h volume
WINDOWS = (7, 30)
FETCH_DAYS = 31               # one day more than the longest window, so the first settlement has a predecessor
INTEREST_8H = 0.0001          # the formulas' interest leg, 0.01% per 8 h (0.03% a day) on Binance, Bybit, OKX, Hyperliquid
HL_INTERVAL_S = 0.5
VENUES = ('hyperliquid', 'binance', 'okx', 'bybit', 'deribit')
UA = 'Mozilla/5.0'

BN_F, BN_S = G.BN_F, G.BN_S
BN_BAPI = 'https://www.binance.com/bapi/margin/v1'
OKX, BY = G.OKX, G.BY
DERIBIT = 'https://www.deribit.com/api/v2/'
HL_DOCS = 'https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin.md'
DERIBIT_ARTICLE = 'https://support.deribit.com/api/v2/help_center/en-us/articles/25944777203869.json'

# Collateral that is a 1:1 wrapper of a perp's underlying, or a staking token that accrues against it.
WRAPPED = {'UBTC': 'BTC', 'UETH': 'ETH', 'USOL': 'SOL', 'WBTC': 'BTC', 'CBBTC': 'BTC', 'BTCB': 'BTC', 'WETH': 'ETH'}
STAKING = {'WBETH': 'ETH', 'BETH': 'ETH', 'STETH': 'ETH', 'WSTETH': 'ETH', 'CBETH': 'ETH', 'RETH': 'ETH', 'METH': 'ETH',
           'CMETH': 'ETH', 'WEETH': 'ETH', 'EETH': 'ETH', 'BNSOL': 'SOL', 'BBSOL': 'SOL', 'JITOSOL': 'SOL', 'MSOL': 'SOL',
           'OKSOL': 'SOL', 'JUPSOL': 'SOL', 'KHYPE': 'HYPE', 'STHYPE': 'HYPE', 'LBTC': 'BTC'}
MULTIPLIERS = (('1000', 1e3), ('10000', 1e4), ('100000', 1e5), ('1000000', 1e6), ('1M', 1e6), ('k', 1e3))
DOCS_NAME = {'UBTC': 'BTC', 'USDT0': 'USDT'}                     # Hyperliquid docs' labels for HyperCore token names
# Taker fees in bp (spot, perp), VIP0: a round trip is 2 x (spot + perp). Deribit's spot is fee-free for rebalancing.
FEES_BP = {'hyperliquid': (7.0, 4.5), 'binance': (10.0, 5.0), 'okx': (10.0, 5.0), 'bybit': (10.0, 5.5),
           'deribit': (0.0, 5.0)}
WATCHLIST = ('HYPE', 'UBTC', 'BTC', 'ETH', 'SOL', 'XAUT', 'PAXG', 'KHYPE', 'WBETH', 'BNSOL', 'STETH', 'METH', 'BBSOL',
             'BETH', 'USDE', 'AERO', 'VELODROME', 'VELO', 'TAO', 'ENA')
TRACKED = ('ratio', 'tiers', 'collateral_token', 'hash')

fnum = G.fnum
write_gz, read_gz, write_json = G.write_gz, G.read_gz, G.write_json


# ---------------------------------------------------------------------------------------------- small helpers

def utc(ms=None):
    return G.utc(ms)


def today():
    return dt.datetime.now(UTC).strftime('%Y-%m-%d')


def now_ms():
    return int(time.time() * 1000)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def norm_text(s):
    return re.sub(r'\s+', ' ', html.unescape(s or '')).strip()


def slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'section'


def rnd(x, n=10):
    return None if x is None else round(float(x), n)


def sentinel(x):
    """The venues' 'no limit' bound: an all-nines integer of 11 digits or more (99999999999, 9999999999999, ...).
    Tier bounds of tiny-priced coins are genuinely that large (OKX PEPE 1.23e11, Bybit SATS 1.08e12), so size alone
    does not mark one."""
    return x is not None and x >= 9.9e10 and x == int(x) and set(str(int(x))) == {'9'}


def cap(v):
    """A tier's upper bound: None when open-ended (empty, or the all-nines sentinel)."""
    x = fnum(v)
    return None if x is None or sentinel(x) else x


def bad(r):
    """True for gold_carry.Get's error envelope or an empty answer."""
    return r is None or (isinstance(r, dict) and ('_http_error' in r or '_error' in r))


def get_text(url, retries=4, timeout=45):
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001 - retried, then reported by the caller
            last = repr(e)[:160]
            time.sleep(0.5 * 2 ** a)
    raise RuntimeError('%s: %s' % (url, last))


def hl_info():
    from perp_rpc import Info
    return Info(interval=HL_INTERVAL_S)


def row(venue, program, asset, ratio=None, tiers=None, tier_unit=None, borrow_apr=None, collateral_token=None,
        hash_=None, **extra):
    """One normalised collateral row. ratio is the collateral ratio of the first tier (1 - haircut); tiers are
    [[from, to (None: open), ratio]] in USD or in units of the asset."""
    r = {'venue': venue, 'program': program, 'asset': asset, 'ratio': rnd(ratio),
         'haircut': rnd(1.0 - ratio) if ratio is not None else None, 'tiers': tiers, 'tier_unit': tier_unit,
         'borrow_apr': rnd(borrow_apr)}
    if collateral_token is not None:
        r['collateral_token'] = collateral_token
    if hash_ is not None:
        r['hash'] = hash_
    r['extra'] = {k: v for k, v in extra.items() if v is not None}
    return r


# ---------------------------------------------------------------------------------------------- core arithmetic (tested)

def ratio_at(tiers, size):
    """Average collateral ratio of a holding of `size` (in the tiers' unit) over tiers [[from, to, ratio]]; nothing
    beyond the last capped tier counts."""
    if not tiers:
        return None
    if size <= 0:
        return tiers[0][2]
    t = sorted(tiers, key=lambda x: x[0] or 0.0)
    val = 0.0
    for i, (lo, hi, r) in enumerate(t):
        lo = lo or 0.0
        nxt = t[i + 1][0] if i + 1 < len(t) else None          # a tier never reaches past the next one's floor
        top = min(x for x in (size, hi, nxt) if x is not None)
        if top > lo:
            val += (top - lo) * (r or 0.0)
    return val / size


def capital_per_short(c, im, rally=STRESS_RALLY):
    """Capital per $ of short when the spot hedge is the collateral at ratio c: the spot itself plus the cash that keeps
    the short's initial margin covered after `rally` (K = 1 + max(0, im + R - c(1+R))). None if c is not collateral."""
    if c is None or c <= 0:
        return None
    return 1.0 + max(0.0, im + rally - c * (1.0 + rally))


def excess_on_capital(funding_apr, K, borrow_cost=0.0, collateral_yield=0.0, bench=SSR):
    if funding_apr is None or not K:
        return None
    return (funding_apr - borrow_cost + collateral_yield) / K - bench


def window_stats(events, end_ms, days, interest_8h, fixed_interval_h=None, max_gap_h=8.0, tol=1e-12):
    """Funding over (end - days, end] from settlements [(ms, rate per settlement)], positive when longs pay (a short
    receives +rate). Each settlement covers the hours since the previous one (capped at max_gap_h; the venue's
    hourly convention when fixed_interval_h is given), so APR = sum x 365 / covered days, the per-settlement
    convention whatever the interval. The formula's interest leg for a settlement is interest_8h x hours / 8;
    floor_share counts settlements exactly at it."""
    ev = sorted(events)
    start = end_ms - days * DAY_MS
    sel, gaps, prev = [], [], None
    for t, r in ev:
        g = (t - prev) / HOUR_MS if prev is not None else None
        prev = t
        if start < t <= end_ms:
            sel.append((t, r))
            gaps.append(g)
    n = len(sel)
    if not n:
        return {'n': 0, 'apr': None, 'coverage': 0.0, 'floor_share': None, 'covered_days': 0.0}
    known = [round(g) for g in gaps if g is not None and round(g) >= 1]
    nominal = fixed_interval_h or (statistics.median(known) if known else 8.0)
    hours = [fixed_interval_h or (min(round(g), max_gap_h) if g is not None and round(g) >= 1 else nominal)
             for g in gaps]
    covered = sum(hours) / 24.0               # not capped: a settlement stamped a few ms late is still one payment
    s = sum(r for _, r in sel)
    floors = [interest_8h * h / 8.0 for h in hours] if interest_8h is not None else None
    modal, modal_n = collections.Counter(round(r, 12) for _, r in sel).most_common(1)[0]
    out = {'n': n, 'sum': s, 'covered_days': covered, 'coverage': covered / days,
           'apr': s * 365.0 / covered if covered > 0 else None, 'interval_h': hours[-1],
           'neg_share': sum(1 for _, r in sel if r < 0) / n, 'modal_rate': modal, 'modal_share': modal_n / n,
           'modal_is_floor': any(abs(modal - f) <= tol for f in set(floors)) if floors else None,
           'floor_rate': floors[-1] if floors else None,
           'floor_share': (sum(1 for (_, r), f in zip(sel, floors) if abs(r - f) <= tol) / n) if floors else None,
           'first_ms': sel[0][0], 'last_ms': sel[-1][0]}
    return out


def match_perp(asset, by_base, perps, stock=False):
    """(symbol, how, multiplier, underlying) of the same-venue perp a collateral asset hedges, or None. by_base maps a
    perp's base ticker to its symbols in order of preference (USDT-margined first). Stock tokens (Binance's xxxB) map
    only to TradFi perps; everything else never does."""
    if stock:
        b = asset[:-1] if asset.endswith('B') else None
        for s in by_base.get(b, []) if b else []:
            if perps[s].get('kind') == 'tradfi':
                return s, 'stock token', 1.0, b
        return None
    for s in by_base.get(asset, []):
        if perps[s].get('kind') != 'tradfi':
            return s, 'direct', 1.0, asset
    for pre, mult in MULTIPLIERS:
        for s in by_base.get(pre + asset, []):
            if perps[s].get('kind') != 'tradfi':
                return s, 'multiplier', mult, asset
    for table, how in ((WRAPPED, 'wrapped'), (STAKING, 'staking token')):
        u = table.get(asset.upper())
        for s in by_base.get(u, []) if u else []:
            if perps[s].get('kind') != 'tradfi':
                return s, how, 1.0, u
    return None


def identity(spot_px, perp_mark, mult, how):
    """perp mark / (spot x multiplier) and whether it is plausible for the match (a staking token is worth at least
    its underlying, so the ratio sits at or below 1)."""
    if not spot_px or not perp_mark:
        return None, None
    q = perp_mark / (spot_px * mult)
    lo, hi = (0.6, 1.05) if how == 'staking token' else (0.9, 1.1)
    return q, lo <= q <= hi


def depth_usd(levels, mid, bp=DEPTH_BP):
    return G.depth_usd(levels, mid, bp) if levels and mid else 0.0


# ---------------------------------------------------------------------------------------------- docs parsers (tested)

def md_sections(md):
    """[(title, text)] of a markdown page split at its headings; GitBook's index banner is dropped."""
    lines = [ln for ln in md.replace('\r\n', '\n').split('\n')
             if not ln.startswith('> For the complete documentation index')]
    out, title, buf, fence = [], 'intro', [], False
    for ln in lines:
        if ln.strip().startswith('```'):
            fence = not fence
        m = None if fence else re.match(r'^#{1,6}\s+(.*)$', ln)
        if m:
            out.append((title, '\n'.join(buf)))
            title, buf = m.group(1).strip(), []
        else:
            buf.append(ln)
    out.append((title, '\n'.join(buf)))
    return [(t, x) for t, x in out if norm_text(x) or t != 'intro']


def parse_hl_docs(md):
    """Hyperliquid's portfolio-margin page: one hash per section, the LTVs, caps and borrow-rate formula it states."""
    secs = md_sections(md)
    body = '\n'.join(x for _, x in secs)
    ltv = {m.group(1): float(m.group(2)) for m in
           re.finditer(r'\b([A-Z][A-Z0-9]*) has an LTV of ([0-9]*\.?[0-9]+)', body)}
    caps = {}
    for m in re.finditer(r'^\*\s+([A-Z][A-Z0-9]*):\s*(.+)$', body, re.M):
        d = {}
        for q in re.finditer(r'([0-9][0-9.,]*)\s*([kKmMbB]?)\s+[A-Za-z0-9]+\s+(global|user)\s+(supply|borrow)\s+cap',
                             m.group(2)):
            mult = {'': 1.0, 'k': 1e3, 'm': 1e6, 'b': 1e9}[q.group(2).lower()]
            d['%s_%s' % (q.group(3), q.group(4))] = float(q.group(1).replace(',', '')) * mult
        if d:
            caps[m.group(1)] = d
    rate = re.search(r'interest rate for stablecoins is set at\s*`([^`]+)`', body)
    lt = re.search(r'liquidation_threshold\(token\)\s*=\s*([^\n]+)', body)
    req = [norm_text(m.group(1)) for m in re.finditer(r'^\*\s+((?:Master account|Account value)[^\n]*)$', body, re.M)]
    return {'sections': [{'slug': slug(t), 'title': t, 'hash': sha(norm_text(x))} for t, x in secs],
            'page_hash': sha(norm_text('\n'.join('%s\n%s' % (t, x) for t, x in secs))), 'ltv': ltv, 'caps': caps,
            'borrow_rate_formula': rate.group(1).strip() if rate else None,
            'liquidation_threshold': lt.group(1).strip() if lt else None, 'requirements': req}


class _Tables(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self._row, self._cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.tables.append([])
        elif tag == 'tr' and self.tables:
            self._row = []
        elif tag in ('td', 'th') and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self._cell is not None and self._row is not None:
            self._row.append(norm_text(''.join(self._cell)))
            self._cell = None
        elif tag == 'tr' and self._row is not None:
            self.tables[-1].append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def html_tables(body):
    p = _Tables()
    p.feed(body or '')
    return p.tables


def pct(s):
    s = (s or '').strip()
    if s in ('-', '–', '—', '', '0', '0%'):
        return 0.0
    m = re.match(r'^([0-9]*\.?[0-9]+)\s*%$', s)
    return float(m.group(1)) / 100.0 if m else None


def parse_deribit_article(art):
    """Deribit's 'Cross collateral specifications' article (Zendesk help-centre JSON): the haircut table by currency
    (X:PM and X:SM columns), the negative-equity collateral fee, and hashes of the table and of the whole text."""
    a = (art or {}).get('article') or {}
    body = a.get('body') or ''
    haircuts, table_text = {}, ''
    for t in html_tables(body):
        if not t or not any('haircut' in c.lower() for c in t[0]):
            continue
        hdr = [c.lower() for c in t[0]]
        i_pm = next((i for i, c in enumerate(hdr) if 'x:pm' in c), None)
        i_sm = next((i for i, c in enumerate(hdr) if 'x:sm' in c), None)
        i_cc = next((i for i, c in enumerate(hdr) if 'cross collateral' in c), None)
        i_off = next((i for i, c in enumerate(hdr) if 'offset' in c), None)
        if i_pm is None or i_sm is None:
            continue
        for r in t[1:]:
            if not r or not r[0] or len(r) <= max(i_pm, i_sm):
                continue
            haircuts[r[0].upper()] = {'cross': (r[i_cc] == '✓') if i_cc is not None else None,
                                      'offset': (r[i_off] == '✓') if i_off is not None else None,
                                      'x_pm': pct(r[i_pm]), 'x_sm': pct(r[i_sm])}
        table_text = json.dumps(t, ensure_ascii=False)
    text = norm_text(re.sub(r'<[^>]+>', ' ', body))
    fee = re.search(r'default\s*=\s*([0-9]*\.?[0-9]+)%\s*per day', text)
    return {'title': a.get('title'), 'updated_at': a.get('updated_at'), 'haircuts': haircuts,
            'collateral_fee_per_day': float(fee.group(1)) / 100.0 if fee else None,
            'table_hash': sha(table_text) if table_text else None, 'body_hash': sha(text) if text else None}


# ---------------------------------------------------------------------------------------------- normalisers (tested)

def norm_hl(reserves, spot_meta, dexes, metas, md):
    """Hyperliquid: portfolio-margin reserves (LTV = collateral ratio; the stablecoins are borrowable at LTV 0), every
    perp dex's collateral token, and the docs page's sections. Returns rows, programs fetched completely, checks."""
    rows, ok, checks = [], {}, {}
    toks = {t['index']: t for t in (spot_meta or {}).get('tokens', [])}
    docs = parse_hl_docs(md) if md else None
    res_idx = set()
    ok['portfolio_margin'] = reserves is not None and spot_meta is not None
    if ok['portfolio_margin']:
        for idx, st in reserves:
            res_idx.add(idx)
            name = toks.get(idx, {}).get('name', '#%s' % idx)
            ltv = fnum(st.get('ltv'))
            caps = (docs or {}).get('caps', {}).get(DOCS_NAME.get(name, name))
            rows.append(row('hyperliquid', 'portfolio_margin', name, ratio=ltv, borrow_apr=fnum(st.get('borrowYearlyRate')),
                            token=idx, role='collateral' if (ltv or 0) > 0 else 'borrowable',
                            supply_apr=fnum(st.get('supplyYearlyRate')), utilization=fnum(st.get('utilization')),
                            total_supplied=fnum(st.get('totalSupplied')), total_borrowed=fnum(st.get('totalBorrowed')),
                            oracle_px=fnum(st.get('oraclePx')), docs_caps=caps))
    ok['hip3_collateral'] = dexes is not None and metas is not None and spot_meta is not None and \
        all(('' if d is None else d.get('name', '')) in metas for d in dexes)
    if dexes is not None and metas is not None and spot_meta is not None:
        for d in dexes:
            name = '' if d is None else d.get('name', '')
            m = metas.get(name)
            if m is None:
                continue
            idx = m.get('collateralToken')
            uni = m.get('universe') or []
            rows.append(row('hyperliquid', 'hip3_collateral', name or 'main',
                            collateral_token=toks.get(idx, {}).get('name', '#%s' % idx), token=idx,
                            borrowable=(idx in res_idx) if ok['portfolio_margin'] else None,
                            full_name=None if d is None else d.get('fullName'), n_assets=len(uni),
                            n_live=sum(1 for u in uni if not u.get('isDelisted'))))
    ok['docs'] = docs is not None
    if docs:
        rows.append(row('hyperliquid', 'docs', 'docs:page', hash_=docs['page_hash'], url=HL_DOCS, ltv=docs['ltv'],
                        caps=docs['caps'], borrow_rate_formula=docs['borrow_rate_formula'],
                        liquidation_threshold=docs['liquidation_threshold'], requirements=docs['requirements']))
        for s in docs['sections']:
            rows.append(row('hyperliquid', 'docs', 'docs:' + s['slug'], hash_=s['hash'], title=s['title']))
        if ok['portfolio_margin']:
            api = {r['asset']: r['ratio'] for r in rows if r['program'] == 'portfolio_margin' and (r['ratio'] or 0) > 0}
            checks['docs_ltv_vs_api'] = {k: {'docs': docs['ltv'].get(DOCS_NAME.get(k, k)), 'api': v} for k, v in api.items()}
            checks['docs_ltv_mismatch'] = sorted(k for k, v in checks['docs_ltv_vs_api'].items() if v['docs'] != v['api'])
            checks['docs_assets_without_reserve'] = sorted(
                set(docs['ltv']) - {DOCS_NAME.get(k, k) for k in api})
    return rows, ok, checks


def norm_binance(pm, pro, vip, asset_index, fut_assets):
    """Binance: portfolio margin (classic collateral rate; stock tokens carry tiered liquidation ratios), portfolio
    margin Pro (tiered rates in USD), multi-assets mode (1 - bid buffer of the margin-available assets), and the
    VIP0 margin borrow rate of every asset."""
    rows, ok = [], {}
    borrow = {}
    for a in (vip or {}).get('data') or []:
        s0 = next((s for s in a.get('specs') or [] if str(s.get('vipLevel')) == '0'), None)
        if s0 and fnum(s0.get('dailyInterestRate')) is not None:
            borrow[a.get('assetName')] = fnum(s0['dailyInterestRate']) * 365.0
    ok['portfolio_margin'] = bool((pm or {}).get('data'))
    for a in (pm or {}).get('data') or []:
        r = fnum(a.get('collateralRate'))
        if a.get('virtual') or not r:
            continue
        tlr = a.get('tieredLiquidationRatio')
        rows.append(row('binance', 'portfolio_margin', a['asset'], ratio=r, borrow_apr=borrow.get(a['asset']),
                        discount_factor=a.get('discountFactor'),
                        tiered_liquidation_ratio=[[fnum(t.get('tierFloor')), cap(t.get('tierCap')),
                                                   fnum(t.get('liquidationRatio'))] for t in tlr] if tlr else None,
                        stock_token=True if tlr else None))
    ok['portfolio_margin_pro'] = bool((pro or {}).get('data'))
    for g in (pro or {}).get('data') or []:
        tiers = sorted([[fnum(c.get('tierFloor')), cap(c.get('tierCap')), fnum(c.get('collateralRate'))]
                        for c in g.get('collaterals') or []], key=lambda t: t[0])
        for name in g.get('assetNames') or []:
            rows.append(row('binance', 'portfolio_margin_pro', name, ratio=tiers[0][2] if tiers else None, tiers=tiers,
                            tier_unit='usd', borrow_apr=borrow.get(name), rank=g.get('rank')))
    ok['multi_assets'] = isinstance(asset_index, list) and isinstance(fut_assets, list)
    if ok['multi_assets']:
        idx = {a.get('symbol'): a for a in asset_index if isinstance(a, dict)}
        for a in fut_assets:
            if not a.get('marginAvailable'):
                continue
            x = idx.get(a['asset'] + 'USD')
            buf = fnum(x.get('bidBuffer')) if x else None
            rows.append(row('binance', 'multi_assets', a['asset'], ratio=(1.0 - buf) if buf is not None else None,
                            borrow_apr=borrow.get(a['asset']), index=fnum(x.get('index')) if x else None,
                            auto_exchange_bid_buffer=fnum(x.get('autoExchangeBidBuffer')) if x else None,
                            auto_asset_exchange=fnum(a.get('autoAssetExchange'))))
    return rows, ok


def norm_okx(disc, loan):
    """OKX multi-currency / portfolio margin: discount-rate tiers in units of the currency (restricted currencies
    and those without tiers are not collateral) and the basic daily loan rate."""
    borrow = {}
    for blk in (loan or {}).get('data') or []:
        for b in blk.get('basic') or []:
            if fnum(b.get('rate')) is not None:
                borrow[b.get('ccy')] = fnum(b['rate']) * 365.0
    rows = []
    for c in (disc or {}).get('data') or []:
        det = c.get('details') or []
        if not det or c.get('collateralRestrict'):
            continue
        tiers = sorted([[fnum(t.get('minAmt')), cap(t.get('maxAmt')), fnum(t.get('discountRate'))] for t in det],
                       key=lambda t: t[0] or 0.0)
        if not tiers[0][2]:
            continue
        rows.append(row('okx', 'multi_currency_margin', c['ccy'], ratio=tiers[0][2], tiers=tiers, tier_unit='qty',
                        borrow_apr=borrow.get(c['ccy']), interest_free_quota=fnum(c.get('amt')),
                        min_discount_rate=fnum(c.get('minDiscountRate')),
                        liq_penalty_tier1=fnum(det[0].get('liqPenaltyRate'))))
    return rows, {'multi_currency_margin': bool((disc or {}).get('data'))}


def norm_bybit(coll, vipdata):
    """Bybit unified trading account: tiered collateral ratios in units of the coin (the single collateralRatio of
    the VIP data is deprecated since the tiered logic), marginCollateral and the No-VIP hourly borrow rate."""
    nv = {}
    for g in ((vipdata or {}).get('result') or {}).get('vipCoinList') or []:
        if g.get('vipLevel') == 'No VIP':
            nv = {x.get('currency'): x for x in g.get('list') or []}
    rows = []
    lst = ((coll or {}).get('result') or {}).get('list') or []
    for c in lst:
        tiers = sorted([[fnum(t.get('minQty')), cap(t.get('maxQty')), fnum(t.get('collateralRatio'))]
                        for t in c.get('collateralRatioList') or []
                        if fnum(t.get('minQty')) is not None and not sentinel(fnum(t.get('minQty')))],
                       key=lambda t: t[0])
        if not tiers or not tiers[0][2]:
            continue
        v = nv.get(c.get('currency'), {})
        if v and v.get('marginCollateral') is False:
            continue
        hb = fnum(v.get('hourlyBorrowRate'))
        rows.append(row('bybit', 'uta', c['currency'], ratio=tiers[0][2], tiers=tiers, tier_unit='qty',
                        borrow_apr=hb * 8760.0 if hb is not None else None, borrowable=v.get('borrowable'),
                        liquidation_order=fnum(v.get('liquidationOrder')),
                        vip_collateral_ratio_deprecated=fnum(v.get('collateralRatio'))))
    return rows, {'uta': bool(lst)}


def norm_deribit(currencies, pme, article):
    """Deribit cross collateral: the pool from get_currencies, haircuts from the support article's X:SM column (the
    standard-margin account; X:PM from pme/get_params beside it), the yield Deribit states for a currency, and the
    article's hashes."""
    rows, checks = [], {}
    pmec = ((pme or {}).get('result') or {}).get('currency') or {}
    doc = parse_deribit_article(article) if article else None
    hc = (doc or {}).get('haircuts') or {}
    pool = []
    res = (currencies or {}).get('result') or []
    for c in res:
        if not c.get('in_cross_collateral_pool'):
            continue
        name = c['currency']
        h_pm = fnum((pmec.get(name.lower()) or {}).get('haircut')) if pmec else None
        h_sm = (hc.get(name.upper()) or {}).get('x_sm')
        h = h_sm if h_sm is not None else h_pm
        apr = fnum(c.get('apr'))
        rows.append(row('deribit', 'cross_collateral', name, ratio=(1.0 - h) if h is not None else None,
                        haircut_pm=h_pm, haircut_sm=h_sm,
                        haircut_source='article X:SM' if h_sm is not None else ('pme X:PM' if h_pm is not None else None),
                        yield_apr=apr / 100.0 if apr else None))
        pool.append(name.upper())
    if doc and doc.get('table_hash'):
        rows.append(row('deribit', 'docs', 'docs:cross-collateral-table', hash_=doc['table_hash'], url=DERIBIT_ARTICLE,
                        updated_at=doc['updated_at'], haircuts=hc, collateral_fee_per_day=doc['collateral_fee_per_day']))
        rows.append(row('deribit', 'docs', 'docs:cross-collateral-article', hash_=doc['body_hash'],
                        updated_at=doc['updated_at']))
        checks['article_not_in_pool'] = sorted(set(k for k, v in hc.items() if v.get('cross')) - set(pool))
        checks['pool_not_in_article'] = sorted(set(pool) - set(hc))
        checks['collateral_fee_per_day'] = doc['collateral_fee_per_day']
    return rows, {'cross_collateral': bool(res), 'docs': bool(doc and doc.get('table_hash'))}, checks


# ============================================================================================== snapshot

RAW_KEYS = {
    'hyperliquid': ('reserves', 'spot_meta', 'perp_dexs', 'metas', 'docs_md'),
    'binance': ('pm_collateral_rate', 'pm_pro_tiered_collateral_rate', 'margin_vip_spec', 'fapi_asset_index',
                'fapi_exchange_info_assets'),
    'okx': ('discount_rate_interest_free_quota', 'interest_rate_loan_quota'),
    'bybit': ('spot_margin_collateral', 'spot_margin_vip_data'),
    'deribit': ('get_currencies', 'pme_get_params', 'support_article_cross_collateral'),
}


def normalise(venue, p):
    """rows, programs fetched completely, checks: one venue's raw payloads (as saved under raw/) normalised; an error
    envelope or a missing file counts as no answer."""
    c = {k: (None if bad(p.get(k)) else p.get(k)) for k in RAW_KEYS[venue]}
    if venue == 'hyperliquid':
        return norm_hl(c['reserves'], c['spot_meta'], c['perp_dexs'], c['metas'], c['docs_md'])
    if venue == 'binance':
        rows, ok = norm_binance(c['pm_collateral_rate'], c['pm_pro_tiered_collateral_rate'], c['margin_vip_spec'],
                                c['fapi_asset_index'], c['fapi_exchange_info_assets'])
        return rows, ok, {}
    if venue == 'okx':
        rows, ok = norm_okx(c['discount_rate_interest_free_quota'], c['interest_rate_loan_quota'])
        return rows, ok, {}
    if venue == 'bybit':
        rows, ok = norm_bybit(c['spot_margin_collateral'], c['spot_margin_vip_data'])
        return rows, ok, {}
    return norm_deribit(c['get_currencies'], c['pme_get_params'], c['support_article_cross_collateral'])


def read_raw(raw, venue):
    p = {}
    for k in RAW_KEYS[venue]:
        f = Path(raw) / ('%s_%s.json.gz' % (venue, k))
        p[k] = read_gz(f) if f.exists() else None
    return p


def fetch_hl(raw, errors):
    api = hl_info()

    def call(name, body):
        try:
            return api.post(body)
        except Exception as e:  # noqa: BLE001 - recorded per venue; the other programs still run
            errors.append('%s: %s' % (name, str(e)[:200]))
            return None
    p = {'reserves': call('allBorrowLendReserveStates', {'type': 'allBorrowLendReserveStates'}),
         'spot_meta': call('spotMeta', {'type': 'spotMeta'}),
         'perp_dexs': call('perpDexs', {'type': 'perpDexs'})}
    metas = {}
    for d in p['perp_dexs'] or []:
        name = '' if d is None else d.get('name', '')
        m = call('meta %s' % (name or 'main'), {'type': 'meta', 'dex': name})
        if m is not None:
            metas[name] = m
    p['metas'] = metas if p['perp_dexs'] is not None else None
    try:
        p['docs_md'] = get_text(HL_DOCS)
    except Exception as e:  # noqa: BLE001
        errors.append('docs: %s' % str(e)[:200])
        p['docs_md'] = None
    for k, v in p.items():
        if v is not None:
            write_gz(raw / ('hyperliquid_%s.json.gz' % k), v)
    rows, ok, checks = normalise('hyperliquid', p)
    return rows, ok, checks, api.stats()


def fetch_binance(raw, errors):
    get = G.Get(interval=0.25, ua=UA)
    p = {'pm_collateral_rate': get(BN_BAPI + '/public/margin/portfolio/collateral-rate'),
         'pm_pro_tiered_collateral_rate': get(BN_BAPI + '/public/margin/portfolio/tiered-collateral-rate'),
         'margin_vip_spec': get(BN_BAPI + '/public/margin/vip/spec/list-all'),
         'fapi_asset_index': get(BN_F + '/fapi/v1/assetIndex')}
    ex = get(BN_F + '/fapi/v1/exchangeInfo')
    p['fapi_exchange_info_assets'] = ex.get('assets') if not bad(ex) else ex
    for k, v in p.items():
        if bad(v):
            errors.append('%s: %s' % (k, json.dumps(v)[:200]))
        write_gz(raw / ('binance_%s.json.gz' % k), v)
    rows, ok, checks = normalise('binance', p)
    return rows, ok, checks, get.stats()


def fetch_okx(raw, errors):
    get = G.Get(interval=1.2, ua=UA)        # discount-rate-interest-free-quota: 2 requests per 2 s
    p = {'discount_rate_interest_free_quota': get(OKX + '/api/v5/public/discount-rate-interest-free-quota'),
         'interest_rate_loan_quota': get(OKX + '/api/v5/public/interest-rate-loan-quota')}
    for k, v in p.items():
        if bad(v) or str((v or {}).get('code', '0')) != '0':
            errors.append('%s: %s' % (k, json.dumps(v)[:200]))
        write_gz(raw / ('okx_%s.json.gz' % k), v)
    rows, ok, checks = normalise('okx', p)
    return rows, ok, checks, get.stats()


def fetch_bybit(raw, errors):
    get = G.Get(interval=0.2, ua=UA)
    p = {'spot_margin_collateral': get(BY + '/v5/spot-margin-trade/collateral'),
         'spot_margin_vip_data': get(BY + '/v5/spot-margin-trade/data')}
    for k, v in p.items():
        if bad(v) or (v or {}).get('retCode') not in (0, None):
            errors.append('%s: %s' % (k, json.dumps(v)[:200]))
        write_gz(raw / ('bybit_%s.json.gz' % k), v)
    rows, ok, checks = normalise('bybit', p)
    return rows, ok, checks, get.stats()


def fetch_deribit(raw, errors):
    get = G.Get(interval=0.25, ua=UA)
    p = {'get_currencies': get(DERIBIT + 'public/get_currencies'),
         'pme_get_params': get(DERIBIT + 'public/pme/get_params'),
         'support_article_cross_collateral': get(DERIBIT_ARTICLE)}
    for k, v in p.items():
        if bad(v):
            errors.append('%s: %s' % (k, json.dumps(v)[:200]))
        write_gz(raw / ('deribit_%s.json.gz' % k), v)
    rows, ok, checks = normalise('deribit', p)
    return rows, ok, checks, get.stats()


FETCH = {'hyperliquid': fetch_hl, 'binance': fetch_binance, 'okx': fetch_okx, 'bybit': fetch_bybit,
         'deribit': fetch_deribit}


def counts_of(rows):
    c = collections.defaultdict(lambda: {'rows': 0, 'positive_ratio': 0})
    for r in rows:
        k = c[r['program']]
        k['rows'] += 1
        k['positive_ratio'] += 1 if (r.get('ratio') or 0) > 0 else 0
    return dict(c)


def cmd_snapshot(args):
    """Fetch every venue's collateral list (or, with --from-raw, rebuild the day's table from the raw responses
    already saved, e.g. after a normaliser fix; nothing is fetched then)."""
    day = args.day or today()
    d = Path(args.watch) / day
    raw = d / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    prior = load_snapshot(args.watch, day) if snapshot_file(d) else None
    venues, rows = {}, []
    for v in [x for x in args.venues.split(',') if x]:
        errors, t0 = [], time.time()
        if getattr(args, 'from_raw', False):
            p = read_raw(raw, v)
            if all(x is None for x in p.values()):
                continue
            vr, ok, checks = normalise(v, p)
            info = dict((prior or {}).get('venues', {}).get(v) or {})
            info.update({'ok': ok, 'counts': counts_of(vr), 'checks': checks, 'renormalised_at': utc()})
            rows += vr
            venues[v] = info
            print('snapshot %s (from raw): %s' % (v, ', '.join('%s %d' % (q, n['rows']) for q, n in
                                                                info['counts'].items())), flush=True)
            continue
        try:
            vr, ok, checks, http = FETCH[v](raw, errors)
        except Exception as e:  # noqa: BLE001 - one venue down must not stop the others
            vr, ok, checks, http = [], {}, {}, None
            errors.append('fatal: %s' % repr(e)[:300])
        rows += vr
        venues[v] = {'ok': ok, 'errors': errors, 'counts': counts_of(vr), 'checks': checks, 'http': http,
                     'seconds': round(time.time() - t0, 1)}
        print('snapshot %s: %s%s' % (v, ', '.join('%s %d' % (p, n['rows']) for p, n in venues[v]['counts'].items()),
                                     ('; errors: ' + '; '.join(errors)) if errors else ''), flush=True)
    fetched = (prior or {}).get('fetched_at') if getattr(args, 'from_raw', False) else utc()
    snap = {'date': day, 'fetched_at': fetched, 'script': 'scripts/collateral_watch.py', 'venues': venues, 'rows': rows}
    if prior:                                 # a partial rerun keeps the venues it did not touch
        for v, info in prior.get('venues', {}).items():
            if v not in venues:
                snap['venues'][v] = info
                snap['rows'] += [r for r in prior.get('rows', []) if r['venue'] == v]
    write_gz(d / SNAP_FILE, snap)
    return snap


# ============================================================================================== diff

SNAP_FILE = 'collateral.json.gz'           # the normalised table of one day (about 80 kB gzip'd)


def snapshot_file(d):
    for name in (SNAP_FILE, 'collateral.json'):
        if (Path(d) / name).exists():
            return Path(d) / name
    return None


def snapshot_days(watch):
    return sorted(p.name for p in Path(watch).glob('20??-??-??') if snapshot_file(p))


def load_snapshot(watch, day):
    f = snapshot_file(Path(watch) / day)
    return read_gz(f) if f.suffix == '.gz' else json.loads(f.read_text())


def _same(a, b):
    if a is None or b is None:
        return a is None and b is None
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return a == b


def _same_tiers(a, b):
    if not a or not b:
        return not a and not b
    if len(a) != len(b):
        return False
    return all(len(x) == len(y) and all(_same(p, q) for p, q in zip(x, y)) for x, y in zip(a, b))


def summary(r):
    s = {k: r.get(k) for k in TRACKED + ('haircut',) if r.get(k) is not None}
    for k in ('docs_caps', 'stock_token', 'haircut_source', 'title', 'borrowable'):
        if r.get('extra', {}).get(k) is not None:
            s[k] = r['extra'][k]
    return s


def diff_program(old_rows, new_rows, venue, program, old_date, new_date, at):
    """Events between two snapshots of one venue program: added, removed, ratio_changed, tiers_changed,
    collateral_token_changed, docs_hash_changed (docs sections appear and disappear as docs_section_added/removed)."""
    o = {r['asset']: r for r in old_rows}
    n = {r['asset']: r for r in new_rows}
    ev = []

    def mk(event, asset, old, new, detail=None):
        e = {'event': event, 'venue': venue, 'program': program, 'asset': asset, 'old': old, 'new': new,
             'old_date': old_date, 'new_date': new_date, 'detected_at': at}
        if detail:
            e['detail'] = detail
        return e
    docs = program == 'docs'
    for a in sorted(set(n) - set(o)):
        ev.append(mk('docs_section_added' if docs else 'added', a, None, summary(n[a])))
    for a in sorted(set(o) - set(n)):
        ev.append(mk('docs_section_removed' if docs else 'removed', a, summary(o[a]), None))
    for a in sorted(set(o) & set(n)):
        x, y = o[a], n[a]
        if not _same(x.get('ratio'), y.get('ratio')):
            ev.append(mk('ratio_changed', a, x.get('ratio'), y.get('ratio'),
                         {'haircut': [x.get('haircut'), y.get('haircut')]}))
        if not _same_tiers(x.get('tiers'), y.get('tiers')):
            ev.append(mk('tiers_changed', a, x.get('tiers'), y.get('tiers')))
        if x.get('collateral_token') != y.get('collateral_token'):
            ev.append(mk('collateral_token_changed', a, x.get('collateral_token'), y.get('collateral_token')))
        if x.get('hash') != y.get('hash'):
            ev.append(mk('docs_hash_changed', a, x.get('hash'), y.get('hash'),
                         {'old_extra': x.get('extra'), 'new_extra': y.get('extra')}))
    return ev


def event_key(e):
    return json.dumps([e.get('event'), e.get('venue'), e.get('program'), e.get('asset'), e.get('old_date'),
                       e.get('new_date'), e.get('old'), e.get('new')], sort_keys=True, default=str)


def diff_snapshots(watch, day=None, at=None):
    """Events of the newest snapshot (or `day`) against, per venue program, the latest earlier snapshot in which that
    program was fetched completely. A program never seen before gives one 'baseline' row."""
    days = snapshot_days(watch)
    if day:
        days = [x for x in days if x <= day]
    if not days:
        raise SystemExit('no snapshot under %s' % watch)
    new_day = days[-1]
    new = load_snapshot(watch, new_day)
    at = at or utc()
    cache = {}

    def earlier():                        # newest first, loaded only as far back as a search needs
        for d in reversed(days[:-1]):
            if d not in cache:
                cache[d] = load_snapshot(watch, d)
            yield d, cache[d]
    events, compared = [], []
    for venue, info in sorted(new['venues'].items()):
        for program, ok in sorted((info.get('ok') or {}).items()):
            if not ok:
                continue
            nrows = [r for r in new['rows'] if r['venue'] == venue and r['program'] == program]
            prev = next(((d, s) for d, s in earlier() if (s['venues'].get(venue, {}).get('ok') or {}).get(program)),
                        None)
            if prev is None:
                events.append({'event': 'baseline', 'venue': venue, 'program': program, 'asset': None, 'old': None,
                               'new': {'rows': len(nrows), 'positive_ratio': sum(1 for r in nrows if (r.get('ratio') or 0) > 0)},
                               'old_date': None, 'new_date': new_day, 'detected_at': at})
                continue
            orows = [r for r in prev[1]['rows'] if r['venue'] == venue and r['program'] == program]
            events += diff_program(orows, nrows, venue, program, prev[0], new_day, at)
            compared.append((venue, program, prev[0]))
    return new_day, events, compared


def append_events(path, events):
    path = Path(path)
    seen = set()
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                seen.add(event_key(json.loads(line)))
    fresh = [e for e in events if event_key(e) not in seen]
    if fresh:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as f:
            for e in fresh:
                f.write(json.dumps(e, sort_keys=True, default=str) + '\n')
    return fresh


def cmd_diff(args):
    new_day, events, compared = diff_snapshots(args.watch, args.day)
    fresh = append_events(args.events, events)
    changes = [e for e in events if e['event'] != 'baseline']
    if not compared:
        print('diff %s: baseline, no previous snapshot (%d programs recorded); %d rows appended to %s' % (
            new_day, sum(1 for e in events if e['event'] == 'baseline'), len(fresh), args.events))
    else:
        print('diff %s: %d events against %s; %d new rows appended to %s' % (
            new_day, len(changes), ', '.join(sorted({'%s/%s@%s' % c for c in compared})), len(fresh), args.events))
        for e in changes[:40]:
            print('  %s %s/%s %s: %s -> %s' % (e['event'], e['venue'], e['program'], e['asset'],
                                              json.dumps(e['old'])[:80], json.dumps(e['new'])[:80]))
    return {'day': new_day, 'events': events, 'appended': fresh, 'compared': compared}


# ============================================================================================== carry: markets

def by_base_of(perps, pref):
    out = collections.defaultdict(list)
    for s, p in perps.items():
        out[p['base']].append(s)
    for b in out:
        out[b].sort(key=lambda s: (pref(perps[s]), s))
    return dict(out)


def hl_markets(api, snap_rows):
    meta, ctxs = api.post({'type': 'metaAndAssetCtxs'})
    smeta, sctxs = api.post({'type': 'spotMetaAndAssetCtxs'})
    perps = {}
    for u, c in zip(meta['universe'], ctxs):
        if u.get('isDelisted'):
            continue
        mark = fnum(c.get('markPx'))
        perps[u['name']] = {'base': u['name'], 'kind': 'coin', 'max_lev': fnum(u.get('maxLeverage')), 'mark': mark,
                            'oi_usd': (fnum(c.get('openInterest'), 0.0) or 0.0) * (mark or 0.0),
                            'vol_usd': fnum(c.get('dayNtlVlm')), 'interest_8h': INTEREST_8H, 'fixed_interval_h': 1,
                            'settle': 'USDC'}
    sctx = {c.get('coin'): c for c in sctxs}
    spot = {}
    for u in smeta['universe']:
        t = u.get('tokens') or []
        if len(t) == 2 and t[1] == 0:                       # quoted in USDC
            c = sctx.get(u['name'], {})
            spot[t[0]] = {'symbol': u['name'], 'mid': fnum(c.get('midPx')) or fnum(c.get('markPx')),
                          'vol_usd': fnum(c.get('dayNtlVlm'))}
    toks = {t['name']: t['index'] for t in smeta['tokens']}
    return perps, spot, toks, {'perps': perps, 'spot': {str(k): v for k, v in spot.items()}}


def bn_markets(get):
    ex = get(BN_F + '/fapi/v1/exchangeInfo')
    prem = get(BN_F + '/fapi/v1/premiumIndex')
    finfo = get(BN_F + '/fapi/v1/fundingInfo')
    t24 = get(BN_F + '/fapi/v1/ticker/24hr')
    sbook = get(BN_S + '/api/v3/ticker/bookTicker')
    for name, x in (('exchangeInfo', ex), ('premiumIndex', prem), ('fundingInfo', finfo), ('ticker24hr', t24),
                    ('spot bookTicker', sbook)):
        if bad(x):
            raise RuntimeError('binance %s: %s' % (name, json.dumps(x)[:200]))
    pi = {x['symbol']: x for x in prem}
    iv = {x['symbol']: x.get('fundingIntervalHours') for x in finfo}
    vol = {x['symbol']: fnum(x.get('quoteVolume')) for x in t24}
    perps = {}
    for s in ex.get('symbols') or []:
        if s.get('status') != 'TRADING' or s.get('contractType') not in ('PERPETUAL', 'TRADIFI_PERPETUAL'):
            continue
        p = pi.get(s['symbol'], {})
        req = fnum(s.get('requiredMarginPercent'))
        perps[s['symbol']] = {'base': s['baseAsset'], 'quote': s['quoteAsset'],
                              'kind': 'tradfi' if s['contractType'] == 'TRADIFI_PERPETUAL' else 'coin',
                              'max_lev': 100.0 / req if req else None, 'mark': fnum(p.get('markPrice')),
                              'interest_8h': fnum(p.get('interestRate')), 'interval_h': iv.get(s['symbol'], 8),
                              'vol_usd': vol.get(s['symbol']), 'settle': s.get('marginAsset')}
    spot = {}
    for b in sbook:
        bid, ask = fnum(b.get('bidPrice')), fnum(b.get('askPrice'))
        if bid and ask:
            spot[b['symbol']] = (bid + ask) / 2.0
    return perps, spot, {'perps': perps}


def okx_markets(get):
    ins = get(OKX + '/api/v5/public/instruments', {'instType': 'SWAP'})
    marks = get(OKX + '/api/v5/public/mark-price', {'instType': 'SWAP'})
    oi = get(OKX + '/api/v5/public/open-interest', {'instType': 'SWAP'})
    st = get(OKX + '/api/v5/market/tickers', {'instType': 'SPOT'})
    sw = get(OKX + '/api/v5/market/tickers', {'instType': 'SWAP'})
    for name, x in (('instruments', ins), ('mark-price', marks), ('open-interest', oi), ('spot tickers', st),
                    ('swap tickers', sw)):
        if bad(x) or not (x or {}).get('data'):
            raise RuntimeError('okx %s: %s' % (name, json.dumps(x)[:200]))
    mk = {x['instId']: fnum(x.get('markPx')) for x in marks['data']}
    ois = {x['instId']: fnum(x.get('oiUsd')) for x in oi['data']}
    vol = {x['instId']: fnum(x.get('volCcy24h')) for x in sw['data']}
    perps = {}
    for x in ins['data']:
        if x.get('state') != 'live':
            continue
        if x.get('ctType') == 'linear':
            base, quote = x.get('ctValCcy'), x.get('settleCcy')
        else:
            base, quote = (x.get('uly') or '-').split('-')[0], 'USD'
        lever = fnum(x.get('lever'))
        perps[x['instId']] = {'base': base, 'quote': quote, 'kind': 'coin' if x.get('ctType') == 'linear' else 'inverse',
                              'max_lev': lever, 'mark': mk.get(x['instId']), 'oi_usd': ois.get(x['instId']),
                              'ct_val': fnum(x.get('ctVal')), 'ct_type': x.get('ctType'), 'settle': x.get('settleCcy'),
                              'vol_usd': (vol.get(x['instId']) or 0.0) * (mk.get(x['instId']) or 0.0) or None}
    spot = {}
    for t in st['data']:
        bid, ask = fnum(t.get('bidPx')), fnum(t.get('askPx'))
        if bid and ask:
            spot[t['instId']] = (bid + ask) / 2.0
    return perps, spot, {'perps': perps}


def by_markets(get):
    lst, cursor = [], ''
    for _ in range(10):
        q = {'category': 'linear', 'limit': 1000}
        if cursor:
            q['cursor'] = cursor
        r = get(BY + '/v5/market/instruments-info', q)
        if bad(r) or r.get('retCode') != 0:
            raise RuntimeError('bybit instruments: %s' % json.dumps(r)[:200])
        lst += r['result'].get('list') or []
        cursor = r['result'].get('nextPageCursor') or ''
        if not cursor:
            break
    tl = get(BY + '/v5/market/tickers', {'category': 'linear'})
    ts = get(BY + '/v5/market/tickers', {'category': 'spot'})
    for name, x in (('linear tickers', tl), ('spot tickers', ts)):
        if bad(x) or x.get('retCode') != 0:
            raise RuntimeError('bybit %s: %s' % (name, json.dumps(x)[:200]))
    tk = {x['symbol']: x for x in tl['result']['list']}
    perps = {}
    for x in lst:
        if x.get('status') != 'Trading' or x.get('contractType') != 'LinearPerpetual':
            continue
        t = tk.get(x['symbol'], {})
        fi = fnum(x.get('fundingInterval'))
        perps[x['symbol']] = {'base': x.get('baseCoin'), 'quote': x.get('quoteCoin'), 'kind': 'coin',
                              'max_lev': fnum((x.get('leverageFilter') or {}).get('maxLeverage')),
                              'mark': fnum(t.get('markPrice')), 'oi_usd': fnum(t.get('openInterestValue')),
                              'vol_usd': fnum(t.get('turnover24h')), 'interest_8h': INTEREST_8H,
                              'interval_h': fi / 60.0 if fi else None, 'settle': x.get('settleCoin')}
    spot = {}
    for t in ts['result']['list']:
        bid, ask = fnum(t.get('bid1Price')), fnum(t.get('ask1Price'))
        if bid and ask:
            spot[t['symbol']] = (bid + ask) / 2.0
    return perps, spot, {'perps': perps}


def deribit_markets(get):
    perps = {}
    for cur in ('BTC', 'ETH', 'USDC'):
        r = get(DERIBIT + 'public/get_instruments', {'currency': cur, 'kind': 'future', 'expired': 'false'})
        s = get(DERIBIT + 'public/get_book_summary_by_currency', {'currency': cur, 'kind': 'future'})
        if bad(r) or bad(s):
            raise RuntimeError('deribit %s instruments/summary: %s' % (cur, json.dumps(r if bad(r) else s)[:200]))
        summ = {x['instrument_name']: x for x in s.get('result') or []}
        for x in r.get('result') or []:
            if x.get('settlement_period') != 'perpetual' or not x.get('is_active', True):
                continue
            sm = summ.get(x['instrument_name'], {})
            inverse = x.get('instrument_type') == 'reversed' or x.get('future_type') == 'reversed'
            mark, oi = fnum(sm.get('mark_price')), fnum(sm.get('open_interest'))
            perps[x['instrument_name']] = {
                'base': x.get('base_currency'), 'quote': x.get('counter_currency'),
                'kind': 'inverse' if inverse else 'coin', 'max_lev': fnum(x.get('max_leverage')), 'mark': mark,
                'oi_usd': (oi if inverse else (oi or 0.0) * (mark or 0.0)) if oi is not None else None,
                'vol_usd': fnum(sm.get('volume_usd')), 'interest_8h': 0.0, 'fixed_interval_h': 1,
                'settle': x.get('settlement_currency')}
    sp = get(DERIBIT + 'public/get_instruments', {'currency': 'any', 'kind': 'spot'})
    spot = {x['instrument_name']: None for x in (sp.get('result') or [])} if not bad(sp) else {}
    return perps, spot, {'perps': perps, 'spot_instruments': sorted(spot)}


# ---------------------------------------------------------------------------------------------- carry: funding

def hl_funding(api, coins, start, end):
    from perp_history import page_funding
    return {c: sorted((int(r['time']), float(r['fundingRate'])) for r in page_funding(api, c, start, end))
            for c in coins}


def bn_funding_bulk(get, start, end, guard=600):
    """Every USDⓈ-M symbol's settlements from start, 1000 at a time in time order (no symbol parameter): about 115
    calls for 30 days instead of one per symbol. Paging restarts at the last stamp, inclusive, and drops duplicates;
    that is exact as long as fewer than 1000 settlements share one millisecond (under 800 symbols trade)."""
    rows, s = {}, start
    for _ in range(guard):
        r = get(BN_F + '/fapi/v1/fundingRate', {'startTime': s, 'endTime': end, 'limit': 1000})
        if bad(r) or not isinstance(r, list):
            raise RuntimeError('binance fundingRate: %s' % json.dumps(r)[:200])
        new = 0
        for x in r:
            k = (x['symbol'], int(x['fundingTime']))
            if k not in rows:
                rows[k] = float(x['fundingRate'])
                new += 1
        if len(r) < 1000:
            break
        last = int(r[-1]['fundingTime'])
        if new == 0 and last == s:
            raise RuntimeError('binance fundingRate: 1000 settlements share one millisecond; page by symbol')
        s = last
    out = collections.defaultdict(list)
    for (sym, t), rate in rows.items():
        out[sym].append((t, rate))
    return {k: sorted(v) for k, v in out.items()}


def bn_funding_symbol(get, sym, start, end):
    r = get(BN_F + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': start, 'endTime': end, 'limit': 1000})
    return sorted((int(x['fundingTime']), float(x['fundingRate'])) for x in r) if isinstance(r, list) else []


def okx_funding(get, inst, start):
    rows, after = [], None
    for _ in range(40):
        q = {'instId': inst, 'limit': 100}
        if after:
            q['after'] = after
        r = get(OKX + '/api/v5/public/funding-rate-history', q)
        lst = None if bad(r) else (r or {}).get('data')
        if not lst:
            break
        rows += lst
        oldest = min(int(x['fundingTime']) for x in lst)
        if oldest <= start or len(lst) < 100:
            break
        after = oldest
    ev = {}
    for x in rows:
        rate = fnum(x.get('realizedRate')) if x.get('realizedRate') not in (None, '') else fnum(x.get('fundingRate'))
        if rate is not None:
            ev[int(x['fundingTime'])] = rate
    formula = collections.Counter(x.get('formulaType') for x in rows).most_common(1)[0][0] if rows else None
    return sorted(ev.items()), formula


def by_funding(get, sym, start, end):
    rows, e = [], end
    for _ in range(40):
        r = get(BY + '/v5/market/funding/history', {'category': 'linear', 'symbol': sym, 'startTime': start,
                                                     'endTime': e, 'limit': 200})
        lst = [] if bad(r) else ((r or {}).get('result') or {}).get('list') or []
        if not lst:
            break
        rows += lst
        oldest = min(int(x['fundingRateTimestamp']) for x in lst)
        if oldest <= start or len(lst) < 200:
            break
        e = oldest - 1
    return sorted({int(x['fundingRateTimestamp']): float(x['fundingRate']) for x in rows}.items())


def deribit_funding(get, inst, start, end):
    out, s = {}, start
    for _ in range(10):
        r = get(DERIBIT + 'public/get_funding_rate_history', {'instrument_name': inst, 'start_timestamp': s,
                                                                'end_timestamp': end})
        res = [] if bad(r) else (r.get('result') or [])
        for x in res:
            if x.get('interest_1h') is not None:
                out[int(x['timestamp'])] = float(x['interest_1h'])
        if not res or max(int(x['timestamp']) for x in res) >= end - 2 * HOUR_MS:
            break
        s = max(int(x['timestamp']) for x in res) + 1
    return sorted(out.items())


# ---------------------------------------------------------------------------------------------- carry: books

def lv(levels, px=0, qty=1, mult=1.0):
    return [(float(x[px]), float(x[qty]) * mult) for x in levels or []]


def book_depth(bids, asks):
    """Mid, USD on the asks and on the bids within DEPTH_BP of mid (levels as (price, base quantity))."""
    if not bids or not asks:
        return None
    mid = (bids[0][0] + asks[0][0]) / 2.0
    return {'mid': mid, 'ask_usd': depth_usd(asks, mid), 'bid_usd': depth_usd(bids, mid)}


def depth_hl(api, coin):
    b = api.post({'type': 'l2Book', 'coin': coin})
    levels = (b or {}).get('levels') or [[], []]
    return book_depth([(float(x['px']), float(x['sz'])) for x in levels[0]],
                      [(float(x['px']), float(x['sz'])) for x in levels[1]])


def depth_bn(get, sym, spot=False):
    r = get((BN_S + '/api/v3/depth') if spot else (BN_F + '/fapi/v1/depth'), {'symbol': sym, 'limit': 1000})
    return None if bad(r) else book_depth(lv(r.get('bids')), lv(r.get('asks')))


def depth_okx(get, inst, ct_val=1.0, inverse=False):
    r = get(OKX + '/api/v5/market/books', {'instId': inst, 'sz': 400})
    d = None if bad(r) else ((r.get('data') or [None])[0])
    if not d:
        return None
    if inverse:                       # contracts of ct_val USD: base quantity = USD / price
        conv = lambda L: [(float(x[0]), float(x[1]) * ct_val / float(x[0])) for x in L]  # noqa: E731
        return book_depth(conv(d.get('bids')), conv(d.get('asks')))
    return book_depth(lv(d.get('bids'), mult=ct_val), lv(d.get('asks'), mult=ct_val))


def depth_by(get, sym, spot=False):
    r = get(BY + '/v5/market/orderbook', {'category': 'spot' if spot else 'linear', 'symbol': sym,
                                           'limit': 200 if spot else 500})
    d = None if bad(r) else (r.get('result') or {})
    return book_depth(lv(d.get('b')), lv(d.get('a'))) if d else None


def depth_deribit(get, inst, inverse=False):
    r = get(DERIBIT + 'public/get_order_book', {'instrument_name': inst, 'depth': 1000})
    d = None if bad(r) else (r.get('result') or {})
    if not d:
        return None
    if inverse:                       # amounts in USD
        conv = lambda L: [(float(p), float(a) / float(p)) for p, a in L]  # noqa: E731
        return book_depth(conv(d.get('bids')), conv(d.get('asks')))
    return book_depth(lv(d.get('bids')), lv(d.get('asks')))


# ---------------------------------------------------------------------------------------------- carry: rows

def carry_row(venue, asset, m, perp, c, c_detail, events, t_now, spot_symbol, spot_px, borrow_apr, borrow_on_im=False,
              collateral_yield=0.0, programs=None, notes=None, extra=None):
    """One collateral asset priced as a same-venue carry. borrow_on_im: the venue lends the short's initial margin
    against the spot and charges it (Hyperliquid portfolio margin); elsewhere nothing is borrowed at entry."""
    sym, how, mult, underlying = m
    im = max(1.0 / TARGET_LEV, 1.0 / perp['max_lev']) if perp.get('max_lev') else 1.0 / TARGET_LEV
    K = capital_per_short(c, im)
    borrowed_frac = im if borrow_on_im else 0.0
    w = {d: window_stats(events, t_now, d, perp.get('interest_8h'), fixed_interval_h=perp.get('fixed_interval_h'))
         for d in WINDOWS}
    borrow_cost = (borrow_apr or 0.0) * borrowed_frac
    q, ok = identity(spot_px, perp.get('mark'), mult, how)
    notes = list(notes or [])
    w30 = w[30]
    if w30.get('n') and w30.get('modal_is_floor') is False and w30['modal_share'] >= 0.3 and \
            abs(w30['modal_rate']) > 1e-12:
        notes.append('modal settlement %.8f (%.0f%%) is not the assumed interest leg (%.8f now)' % (
            w30['modal_rate'], 100 * w30['modal_share'], w30['floor_rate']))
    if ok is False:
        notes.append('identity check failed: perp mark / (spot x %g) = %.3f' % (mult, q))
    if how == 'staking token' and not collateral_yield:
        notes.append('staking yield of %s not counted' % asset)
    fs, fp = FEES_BP.get(venue, (10.0, 5.0))
    r = {'venue': venue, 'asset': asset, 'perp': sym, 'match': how, 'multiplier': mult, 'underlying': underlying,
         'programs': programs or [], 'ratio_1m': rnd(c, 6), 'haircut_1m': rnd(1.0 - c, 6) if c is not None else None,
         'ratio_detail': c_detail, 'im': rnd(im, 6), 'K': rnd(K, 6), 'stress_rally': STRESS_RALLY,
         'borrow_apr': rnd(borrow_apr, 6), 'borrowed_at_entry': borrowed_frac, 'borrow_cost': rnd(borrow_cost, 6),
         'collateral_yield': rnd(collateral_yield, 6), 'spot': spot_symbol, 'spot_px': spot_px,
         'perp_mark': perp.get('mark'), 'identity_ratio': rnd(q, 6), 'identity_ok': ok, 'perp_kind': perp.get('kind'),
         'settle': perp.get('settle'), 'max_lev': perp.get('max_lev'), 'interest_8h': perp.get('interest_8h'),
         'oi_usd': perp.get('oi_usd'), 'vol24_usd': perp.get('vol_usd'), 'rt_fee_bp': 2.0 * (fs + fp)}
    for d in WINDOWS:
        x = w[d]
        r['f%d' % d] = {k: (rnd(v, 10) if isinstance(v, float) else v) for k, v in x.items()}
        r['apr_%dd' % d] = rnd(x.get('apr'), 6)
        r['floor_share_%dd' % d] = rnd(x.get('floor_share'), 4)
        r['excess_%dd' % d] = rnd(excess_on_capital(x.get('apr'), K, borrow_cost, collateral_yield), 6)
    r['interval_h'] = w30.get('interval_h') or w[7].get('interval_h')
    r['floor_rate'] = w30.get('floor_rate')
    r['rankable'] = bool(r['excess_30d'] is not None and ok is not False and (w30.get('coverage') or 0) >= 0.8)
    r['notes'] = notes
    if extra:
        r.update(extra)
    return r


def programs_by_asset(rows, programs):
    out = collections.defaultdict(dict)
    for r in rows:
        if r['program'] in programs and (r.get('ratio') or 0) > 0:
            out[r['asset']][r['program']] = r
    return out


def carry_hl(rows, t_now, log, saved):
    api = hl_info()
    perps, spot, toks, mkt = hl_markets(api, rows)
    saved['markets']['hyperliquid'] = mkt
    pm = [r for r in rows if r['program'] == 'portfolio_margin']
    usdc = next((r for r in pm if r['asset'] == 'USDC'), {})
    by_base = by_base_of(perps, lambda p: 0)
    cands = []
    for r in pm:
        if not (r.get('ratio') or 0) > 0:
            continue
        m = match_perp(r['asset'], by_base, perps)
        if m:
            cands.append((r, m))
    # HIP-3 perps on the same underlying in a live dex whose collateral token is borrowable (portfolio margin spans
    # every HIP-3 dex): none on 2026-10-11, checked from the snapshot's universes so that a listing shows up.
    hip3 = [r for r in rows if r['program'] == 'hip3_collateral' and r['asset'] != 'main']
    events = hl_funding(api, sorted({m[0] for _, m in cands}), t_now - FETCH_DAYS * DAY_MS, t_now)
    saved['funding']['hyperliquid'] = events
    out = []
    for r, m in cands:
        sp = spot.get(r['extra'].get('token'), {})
        caps = r['extra'].get('docs_caps') or {}
        px = r['extra'].get('oracle_px')
        room = None
        if caps.get('global_supply') is not None and r['extra'].get('total_supplied') is not None and px:
            room = (caps['global_supply'] - r['extra']['total_supplied']) * px
        out.append(carry_row('hyperliquid', r['asset'], m, perps[m[0]], r['ratio'], {'portfolio_margin': r['ratio']},
                             events.get(m[0], []), t_now, sp.get('symbol'), sp.get('mid'), usdc.get('borrow_apr'),
                             borrow_on_im=True, programs=['portfolio_margin'],
                             extra={'user_supply_cap_usd': caps['user_supply'] * px if caps.get('user_supply') and px else None,
                                    'global_supply_room_usd': room, 'hip3_dexes_checked': len(hip3)}))
    saved['books_fns']['hyperliquid'] = lambda rr: {'perp': depth_hl(api, rr['perp']),
                                                    'spot': depth_hl(api, rr['spot']) if rr['spot'] else None}
    log['hyperliquid_http'] = api.stats()
    return out


def carry_binance(rows, t_now, log, saved):
    get = G.Get(interval=0.25, ua=UA)
    getf = G.Get(interval=0.65, ua=UA)
    perps, spot, mkt = bn_markets(get)
    saved['markets']['binance'] = mkt
    progs = programs_by_asset(rows, ('portfolio_margin', 'portfolio_margin_pro', 'multi_assets'))
    usdt = next((r for r in rows if r['program'] == 'portfolio_margin' and r['asset'] == 'USDT'), {})
    by_base = by_base_of(perps, lambda p: {'USDT': 0, 'USDC': 1}.get(p.get('quote'), 2))
    cands = []
    for asset, pr in progs.items():
        stock = bool(pr.get('portfolio_margin', {}).get('extra', {}).get('stock_token'))
        m = match_perp(asset, by_base, perps, stock=stock)
        if m:
            cands.append((asset, pr, m))
    need = sorted({m[0] for _, _, m in cands})
    try:
        bulk = bn_funding_bulk(getf, t_now - FETCH_DAYS * DAY_MS, t_now)
    except RuntimeError as e:
        log.setdefault('notes', []).append('binance bulk funding failed (%s); by symbol' % str(e)[:120])
        bulk = {}
    events = {s: bulk[s] for s in need if s in bulk}
    for s in need:
        if s not in events:
            events[s] = bn_funding_symbol(getf, s, t_now - FETCH_DAYS * DAY_MS, t_now)
    saved['funding']['binance'] = events
    out = []
    for asset, pr, m in cands:
        perp = perps[m[0]]
        sp_sym = next((asset + q for q in ('USDT', 'USDC', 'FDUSD') if (asset + q) in spot), None)
        detail, c = {}, None
        if 'portfolio_margin' in pr:
            detail['portfolio_margin'] = pr['portfolio_margin']['ratio']
        if 'portfolio_margin_pro' in pr:
            detail['portfolio_margin_pro_at_1m'] = rnd(ratio_at(pr['portfolio_margin_pro']['tiers'], SIZE_USD), 6)
        if 'multi_assets' in pr:
            detail['multi_assets'] = pr['multi_assets']['ratio']
        for k in ('portfolio_margin', 'portfolio_margin_pro_at_1m', 'multi_assets'):
            if detail.get(k):
                c = detail[k]
                detail['used'] = k
                break
        notes = []
        if perp['kind'] == 'tradfi':
            notes.append('TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public')
        out.append(carry_row('binance', asset, m, perp, c, detail, events.get(m[0], []), t_now, sp_sym,
                             spot.get(sp_sym), usdt.get('borrow_apr'), programs=sorted(pr), notes=notes))
    def books(rr):
        oi = get(BN_F + '/fapi/v1/openInterest', {'symbol': rr['perp']})
        if not bad(oi) and fnum(oi.get('openInterest')) is not None and rr.get('perp_mark'):
            rr['oi_usd'] = fnum(oi['openInterest']) * rr['perp_mark']
        return {'perp': depth_bn(get, rr['perp']), 'spot': depth_bn(get, rr['spot'], spot=True) if rr['spot'] else None}
    saved['books_fns']['binance'] = books
    log['binance_http'] = get.stats()
    log['binance_http_funding'] = getf.stats()
    return out


def carry_okx(rows, t_now, log, saved):
    get = G.Get(interval=0.25, ua=UA)
    perps, spot, mkt = okx_markets(get)
    progs = programs_by_asset(rows, ('multi_currency_margin',))
    usdt = progs.get('USDT', {}).get('multi_currency_margin', {})
    by_base = by_base_of(perps, lambda p: {'USDT': 0, 'USDC': 1}.get(p.get('quote'), 2))
    cands = []
    for asset, pr in progs.items():
        m = match_perp(asset, by_base, perps)
        if m:
            cands.append((asset, pr, m))
    events, formula = {}, {}
    for s in sorted({m[0] for _, _, m in cands}):
        events[s], formula[s] = okx_funding(get, s, t_now - FETCH_DAYS * DAY_MS)
        perps[s]['interest_8h'] = 0.0 if formula[s] == 'noRate' else INTEREST_8H
        perps[s]['formula_type'] = formula[s]
    saved['markets']['okx'] = mkt
    saved['funding']['okx'] = events
    out = []
    for asset, pr, m in cands:
        r = pr['multi_currency_margin']
        sp_sym = next((asset + '-' + q for q in ('USDT', 'USDC') if (asset + '-' + q) in spot), None)
        px = spot.get(sp_sym)
        c = ratio_at(r['tiers'], SIZE_USD / px) if px else r['ratio']
        out.append(carry_row('okx', asset, m, perps[m[0]], c, {'multi_currency_margin_at_1m': rnd(c, 6),
                                                                 'tier1': r['ratio'], 'priced': bool(px)},
                             events.get(m[0], []), t_now, sp_sym, px, usdt.get('borrow_apr'),
                             programs=['multi_currency_margin'],
                             extra={'formula_type': formula.get(m[0])}))
    saved['books_fns']['okx'] = lambda rr: {
        'perp': depth_okx(get, rr['perp'], perps[rr['perp']].get('ct_val') or 1.0, perps[rr['perp']]['kind'] == 'inverse'),
        'spot': depth_okx(get, rr['spot']) if rr['spot'] else None}
    log['okx_http'] = get.stats()
    return out


def carry_bybit(rows, t_now, log, saved):
    get = G.Get(interval=0.12, ua=UA)
    perps, spot, mkt = by_markets(get)
    saved['markets']['bybit'] = mkt
    progs = programs_by_asset(rows, ('uta',))
    usdt = progs.get('USDT', {}).get('uta', {})
    by_base = by_base_of(perps, lambda p: {'USDT': 0, 'USDC': 1}.get(p.get('quote'), 2))
    cands = []
    for asset, pr in progs.items():
        m = match_perp(asset, by_base, perps)
        if m:
            cands.append((asset, pr, m))
    events = {s: by_funding(get, s, t_now - FETCH_DAYS * DAY_MS, t_now) for s in sorted({m[0] for _, _, m in cands})}
    saved['funding']['bybit'] = events
    out = []
    for asset, pr, m in cands:
        r = pr['uta']
        sp_sym = next((asset + q for q in ('USDT', 'USDC') if (asset + q) in spot), None)
        px = spot.get(sp_sym)
        c = ratio_at(r['tiers'], SIZE_USD / px) if px else r['ratio']
        out.append(carry_row('bybit', asset, m, perps[m[0]], c, {'uta_at_1m': rnd(c, 6), 'tier1': r['ratio'],
                                                                   'priced': bool(px)},
                             events.get(m[0], []), t_now, sp_sym, px, usdt.get('borrow_apr'), programs=['uta']))
    saved['books_fns']['bybit'] = lambda rr: {'perp': depth_by(get, rr['perp']),
                                              'spot': depth_by(get, rr['spot'], spot=True) if rr['spot'] else None}
    log['bybit_http'] = get.stats()
    return out


def carry_deribit(rows, t_now, log, saved):
    get = G.Get(interval=0.25, ua=UA)
    perps, spot, mkt = deribit_markets(get)
    saved['markets']['deribit'] = mkt
    progs = programs_by_asset(rows, ('cross_collateral',))
    docs = next((r for r in rows if r['program'] == 'docs' and r['asset'] == 'docs:cross-collateral-table'), {})
    fee = (docs.get('extra') or {}).get('collateral_fee_per_day')
    # inverse (coin-settled) perps first: holding the coin against them leaves no negative-USD equity to pay a fee on
    by_base = by_base_of(perps, lambda p: 0 if p['kind'] == 'inverse' else 1)
    cands = []
    for asset, pr in progs.items():
        m = match_perp(asset.upper(), by_base, perps)
        if m:
            cands.append((asset, pr, m))
    events = {s: deribit_funding(get, s, t_now - FETCH_DAYS * DAY_MS, t_now) for s in sorted({m[0] for _, _, m in cands})}
    saved['funding']['deribit'] = events
    out = []
    for asset, pr, m in cands:
        r = pr['cross_collateral']
        perp = perps[m[0]]
        sp_sym = next((s for s in ('%s_USDC' % asset.upper(), '%s_USDT' % asset.upper()) if s in spot), None)
        y = r['extra'].get('yield_apr') if m[1] == 'staking token' else None
        notes = []
        if perp['kind'] != 'inverse' and fee:
            notes.append('USDC-settled: losses after a rally are negative USDC equity, charged %.2f%%/day (%.1f%%/yr)'
                         % (100 * fee, 100 * fee * 365))
        out.append(carry_row('deribit', asset, m, perp, r['ratio'],
                             {'cross_collateral_x_sm': r['ratio'], 'haircut_pm': r['extra'].get('haircut_pm'),
                              'source': r['extra'].get('haircut_source')},
                             events.get(m[0], []), t_now, sp_sym, None, fee * 365.0 if fee else None,
                             collateral_yield=y or 0.0, programs=['cross_collateral'], notes=notes))
    saved['books_fns']['deribit'] = lambda rr: {
        'perp': depth_deribit(get, rr['perp'], perps[rr['perp']]['kind'] == 'inverse'),
        'spot': depth_deribit(get, rr['spot']) if rr['spot'] else None}
    log['deribit_http'] = get.stats()
    return out


CARRY = {'hyperliquid': carry_hl, 'binance': carry_binance, 'okx': carry_okx, 'bybit': carry_bybit,
         'deribit': carry_deribit}


# ---------------------------------------------------------------------------------------------- carry: checks

def store_crosscheck(rows, saved):
    """Hyperliquid HYPE and BTC: the API's 30-day APR against the same window read from perp_daily's local store
    (same source, different read), and term_carry's 2026 year-to-date mean for context."""
    out = {}
    tc = {}
    try:
        tc = json.loads(TERM_CARRY.read_text()).get('funding_facts') or {}
    except (OSError, ValueError):
        pass
    ev = saved['funding'].get('hyperliquid') or {}
    for r in rows:
        if r['venue'] != 'hyperliquid':
            continue
        coin = r['perp']
        fp = HL_STORE / ('%s.json.gz' % coin)
        rec = {'asset': r['asset'], 'perp': coin, 'api_apr_30d': r['apr_30d'], 'api_floor_share_30d': r['floor_share_30d'],
               'term_carry_2026_ytd_ann': ((tc.get('hl:%s' % coin) or {}).get('2026') or {}).get('ann')}
        if fp.exists():
            st = sorted((int(x['time']), float(x['fundingRate'])) for x in read_gz(fp))
            end = st[-1][0] if st else None
            if end:
                a = window_stats(st, end, 30, INTEREST_8H, fixed_interval_h=1)
                b = window_stats(ev.get(coin, []), end, 30, INTEREST_8H, fixed_interval_h=1)
                rec.update({'store_end': utc(end), 'store_apr_30d': a['apr'], 'api_apr_same_window': b['apr'],
                            'store_floor_share_30d': a['floor_share'], 'api_floor_share_same_window': b['floor_share'],
                            'store_n': a['n'], 'api_n_same_window': b['n'],
                            'agree': (a['apr'] is not None and b['apr'] is not None and abs(a['apr'] - b['apr']) < 1e-9
                                      and a['n'] == b['n'])})
        out[coin] = rec
    return out


# ---------------------------------------------------------------------------------------------- carry: command

def floor_heavy(rows):
    """Collateral whose perp paid exactly the formula's interest leg on at least half of the last 30 days'
    settlements (venues with an interest leg only), most traded first."""
    return sorted([r for r in rows if (r['floor_share_30d'] or 0) >= 0.5 and (r['interest_8h'] or 0) > 0],
                  key=lambda r: -(r.get('vol24_usd') or 0))


def latest_day(watch, day=None):
    days = snapshot_days(watch)
    if day:
        days = [x for x in days if x <= day]
    if not days:
        raise SystemExit('no snapshot under %s; run snapshot first' % watch)
    return days[-1]


def cmd_carry(args):
    t0 = time.time()
    day = latest_day(args.watch, args.day)
    snap = load_snapshot(args.watch, day)
    out = Path(args.out) if args.out else Path(args.watch) / day
    out.mkdir(parents=True, exist_ok=True)
    t_now = now_ms()
    log = {'errors': {}, 'notes': []}
    saved = {'markets': {}, 'funding': {}, 'books_fns': {}}
    rows = []
    for v in [x for x in args.venues.split(',') if x]:
        vr = [r for r in snap['rows'] if r['venue'] == v]
        if not vr:
            log['errors'][v] = 'no snapshot rows'
            continue
        try:
            res = CARRY[v](vr, t_now, log, saved)
            rows += res
            print('carry %s: %d rows' % (v, len(res)), flush=True)
        except Exception as e:  # noqa: BLE001 - one venue down must not stop the others
            log['errors'][v] = repr(e)[:300]
            print('carry %s failed: %s' % (v, repr(e)[:300]), flush=True)
    rows.sort(key=lambda r: (not r['rankable'], -(r['excess_30d'] if r['excess_30d'] is not None else -9.0)))
    # depth: rows above the flag, the best few per venue, and the Hyperliquid cases the book trades
    books = {}
    for v in VENUES:
        fn = saved['books_fns'].get(v)
        if not fn:
            continue
        vr = [r for r in rows if r['venue'] == v and r['rankable']]
        above = sorted([r for r in vr if (r['excess_30d'] or -1) > FLAG_EXCESS], key=lambda r: -(r.get('vol24_usd') or 0))
        pick = above[:DEPTH_CHECKS] + vr[:5]           # the most traded rows above the flag (thin books fail anyway)
        pick += [r for r in rows if r['venue'] == v and v == 'hyperliquid']
        seen = set()
        for r in pick:
            k = (r['venue'], r['asset'], r['perp'])
            if k in seen:
                continue
            seen.add(k)
            try:
                d = fn(r)
            except Exception as e:  # noqa: BLE001 - a missing book is recorded, not fatal
                d = {'error': repr(e)[:200]}
            books['%s:%s:%s' % k] = d
            p, s = (d or {}).get('perp'), (d or {}).get('spot')
            r['depth'] = {'perp_bid_25bp_usd': rnd(p['bid_usd'], 0) if p else None,
                          'spot_ask_25bp_usd': rnd(s['ask_usd'], 0) if s else None,
                          'perp_mid': p['mid'] if p else None, 'spot_mid': s['mid'] if s else None}
            r['depth']['ok_1m'] = bool(p and s and p['bid_usd'] >= SIZE_USD and s['ask_usd'] >= SIZE_USD)
    for r in rows:
        r['flag_excess'] = bool(r['rankable'] and (r['excess_30d'] or 0) > FLAG_EXCESS)
        r['flag'] = bool(r['flag_excess'] and (r.get('depth') or {}).get('ok_1m'))
    res = {'generated': utc(), 'snapshot_day': day, 'computed_at_ms': t_now, 'ssr': SSR,
           'ssr_source': 'term_carry.SSR (constant 3.80%/yr, the book protocol benchmark)',
           'params': {'stress_rally': STRESS_RALLY, 'target_leverage': TARGET_LEV, 'size_usd': SIZE_USD,
                      'depth_bp': DEPTH_BP, 'flag_excess': FLAG_EXCESS, 'windows_days': list(WINDOWS),
                      'interest_8h': INTEREST_8H, 'fees_bp_spot_perp': FEES_BP,
                      'capital': 'K = 1 + max(0, im + R - c(1+R)), im = max(1/10, 1/max leverage), c at a $1M holding',
                      'excess': '(funding APR - borrow APR x borrowed at entry + known collateral yield) / K - SSR'},
           'rows': rows, 'errors': log['errors'], 'notes': log['notes'],
           'crosscheck_hl': store_crosscheck(rows, saved),
           'top_by_venue': {v: [r['venue'] + ':' + r['asset'] + '->' + r['perp'] for r in rows
                                if r['venue'] == v and r['rankable']][:10] for v in VENUES},
           'flagged': [r['venue'] + ':' + r['asset'] + '->' + r['perp'] for r in rows if r['flag']],
           'flag_excess_only': [r['venue'] + ':' + r['asset'] + '->' + r['perp'] for r in rows
                                if r['flag_excess'] and not r['flag']],
           'floor_heavy': [r['venue'] + ':' + r['asset'] + '->' + r['perp'] for r in floor_heavy(rows)],
           'seconds': round(time.time() - t0, 1),
           'http': {k: v for k, v in log.items() if k.endswith('_http') or k.endswith('_http_funding')}}
    if args.out:
        write_json(out / 'carry.json', res)
    else:                                     # the daily job: about 150 kB instead of 1.6 MB
        write_gz(out / 'carry.json.gz', res)
    write_gz(out / 'carry_inputs' / 'markets.json.gz', saved['markets'])
    for v, ev in saved['funding'].items():
        write_gz(out / 'carry_inputs' / ('funding_%s.json.gz' % v), {k: [[t, r] for t, r in x] for k, x in ev.items()})
    write_gz(out / 'carry_inputs' / 'books.json.gz', {'at': utc(), 'books': books})
    render(out, res, snap, args)
    return res


# ---------------------------------------------------------------------------------------------- render

def pc(x, d=2):
    return '' if x is None else ('%+.*f%%' % (d, 100 * x))


def pu(x, d=1):
    return '' if x is None else ('%.*f%%' % (d, 100 * x))


def usd(x):
    if x is None:
        return ''
    a = abs(x)
    return ('$%.1fB' % (x / 1e9)) if a >= 1e9 else ('$%.1fM' % (x / 1e6)) if a >= 1e6 else \
        ('$%.0fk' % (x / 1e3)) if a >= 1e3 else ('$%.0f' % x)


def rel(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def table(header, rows):
    L = ['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)]
    L += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(L)


def carry_table(rs):
    return table(['venue', 'asset -> perp', 'match', 'c at $1M', 'K', '7d APR', '30d APR', 'at floor 30d (7d)',
                  'borrow', 'excess 7d', 'excess 30d', 'OI', 'perp bid / spot ask <=25bp', 'notes'],
                 [[r['venue'], '%s -> %s' % (r['asset'], r['perp']), r['match'],
                   '%.3f' % r['ratio_1m'] if r['ratio_1m'] is not None else '',
                   '%.2f' % r['K'] if r['K'] else '', pc(r['apr_7d']), pc(r['apr_30d']),
                   '%s (%s)%s' % (pu(r['floor_share_30d'], 0), pu(r['floor_share_7d'], 0),
                                  ' at 0' if r.get('interest_8h') == 0 else ''), pc(r['borrow_cost']),
                   pc(r['excess_7d']), pc(r['excess_30d']), usd(r.get('oi_usd')),
                   ('%s / %s%s' % (usd(r['depth']['perp_bid_25bp_usd']), usd(r['depth']['spot_ask_25bp_usd']),
                                   ' ok' if r['depth']['ok_1m'] else '')) if r.get('depth') else '',
                   '; '.join(r['notes'])[:140]] for r in rs])


def render(out, res, snap, args):
    rows = res['rows']
    L = ['# Collateral watch: %s (carry computed %s)' % (res['snapshot_day'], res['generated']), '',
         'Benchmark: %s. Capital per $ of short: %s, R = %.0f%%. Excess: %s; gross of trading costs (round trip in '
         'the json as rt_fee_bp). "At floor" is the share of settlements exactly at the formula\'s interest leg '
         '(0.01%%/8h scaled to the interval; Hyperliquid 0.00125%%/h = 10.95%%/yr; 0 where a venue has no interest '
         'leg). Rows need 80%% funding coverage over 30 days and a plausible spot/perp price match to rank.' % (
             res['ssr_source'], res['params']['capital'], 100 * STRESS_RALLY, res['params']['excess']), '']
    # venues
    vrows = []
    for v, info in sorted(snap['venues'].items()):
        for p, n in sorted(info.get('counts', {}).items()):
            vr = [r for r in snap['rows'] if r['venue'] == v and r['program'] == p]
            note = ''
            if p in ('portfolio_margin', 'portfolio_margin_pro', 'multi_assets', 'multi_currency_margin', 'uta',
                     'cross_collateral'):
                pos = {r['asset']: r for r in vr}
                note = ', '.join(('%s %.2f' % (a, pos[a]['ratio'])) if pos[a].get('tier_unit') != 'usd' else
                                 ('%s %.2f (%.2f at $1M)' % (a, pos[a]['ratio'], ratio_at(pos[a]['tiers'], SIZE_USD)))
                                 for a in WATCHLIST if a in pos and pos[a]['ratio'])
                st = sum(1 for r in vr if r.get('extra', {}).get('stock_token'))
                if st:
                    note += '; %d stock tokens (TSLAB, NVDAB, ...)' % st
            elif p == 'hip3_collateral':
                note = ', '.join('%s: %s%s (%d/%d live)' % (r['asset'], r.get('collateral_token'),
                                                             '' if r['extra'].get('borrowable') else ' not borrowable',
                                                             r['extra'].get('n_live', 0), r['extra'].get('n_assets', 0))
                                 for r in vr)
            elif p == 'docs':
                note = ', '.join('%s %s' % (r['asset'][5:], r.get('hash')) for r in vr)
            ok = (info.get('ok') or {}).get(p)
            vrows.append([v, p, n['rows'], n['positive_ratio'], 'ok' if ok else 'INCOMPLETE', note])
    L += ['## Collateral lists (snapshot %s)' % snap['date'], '',
          table(['venue', 'program', 'rows', 'ratio > 0', 'fetch', 'notable (ratio = 1 - haircut, first tier)'], vrows), '']
    errs = {v: i['errors'] for v, i in snap['venues'].items() if i.get('errors')}
    if errs:
        L += ['Snapshot errors: ' + json.dumps(errs)[:1500], '']
    chk = {v: i['checks'] for v, i in snap['venues'].items() if i.get('checks')}
    if chk:
        L += ['Checks: ' + json.dumps(chk, sort_keys=True)[:2000], '']
    # carry by venue
    L += ['## Same-venue carry, ranked by 30-day excess on capital', '']
    for v in VENUES:
        vr = [r for r in rows if r['venue'] == v and r['rankable']]
        nr = [r for r in rows if r['venue'] == v and not r['rankable']]
        if not vr and not nr:
            continue
        L += ['### %s (%d rankable rows, %d not)' % (v, len(vr), len(nr)), '', carry_table(vr[:12]), '']
    dc = sorted([r for r in rows if r.get('depth')], key=lambda r: -min(r['depth']['perp_bid_25bp_usd'] or 0,
                                                                        r['depth']['spot_ask_25bp_usd'] or 0))
    L += ['## Books read (%d rows: per venue the %d most traded rows above %.0fpp, the top 5, and Hyperliquid), by '
          'the smaller leg within %dbp' % (len(dc), DEPTH_CHECKS, 100 * FLAG_EXCESS, DEPTH_BP), '',
          carry_table(dc[:40]), '']
    L += ['## Flagged: excess > %.0fpp and $1M within %dbp on both legs' % (100 * FLAG_EXCESS, DEPTH_BP), '']
    fl = [r for r in rows if r['flag']]
    L += [carry_table(fl) if fl else 'None.', '']
    fe = [r for r in rows if r['flag_excess'] and not r['flag']]
    L += ['Excess > %.0fpp but $1M does not fit within %dbp on both legs (or no book read): %d rows' % (
        100 * FLAG_EXCESS, DEPTH_BP, len(fe)), '', carry_table(fe[:30]) if fe else '', '']
    fh = floor_heavy(rows)
    L += ['## Collateral whose perp sits at the formula\'s interest leg on most settlements (>= 50%% of 30 days): %d'
          % len(fh), '', 'By venue: %s. The 40 most traded perps (24 h volume):' % ', '.join(
              '%s %d' % (v, sum(1 for r in fh if r['venue'] == v)) for v in VENUES), '',
          carry_table(fh[:40]) if fh else 'None.', '']
    # known cases
    cc = res.get('crosscheck_hl') or {}
    L += ['## Known cases: Hyperliquid portfolio margin', '',
          carry_table([r for r in rows if r['venue'] == 'hyperliquid']), '']
    for k, v in cc.items():
        L += ['- %s: API 30d %s, at floor %s; same window from perp_daily\'s store (to %s): %s vs API %s (n %s vs %s, '
              'agree %s); term_carry 2026 year-to-date mean %s.' % (
                  k, pc(v.get('api_apr_30d')), pu(v.get('api_floor_share_30d')), v.get('store_end'),
                  pc(v.get('store_apr_30d')), pc(v.get('api_apr_same_window')), v.get('store_n'),
                  v.get('api_n_same_window'), v.get('agree'), pc(v.get('term_carry_2026_ytd_ann')))]
    for r in rows:
        if r['venue'] == 'hyperliquid':
            L += ['- %s caps: user supply cap %s, global supply room %s.' % (
                r['asset'], usd(r.get('user_supply_cap_usd')), usd(r.get('global_supply_room_usd')))]
    L += ['', '## Errors and notes', '', json.dumps({'carry_errors': res['errors'], 'notes': res['notes']}), '',
          '## Endpoint gaps', ''] + ['- ' + g for g in API_GAPS]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    files = sorted(str(p.relative_to(out)) + ' %d' % p.stat().st_size for p in out.rglob('*') if p.is_file())
    man = {'generated': utc(), 'study': 'collateral_watch', 'script': 'scripts/collateral_watch.py',
           'snapshot': rel(Path(args.watch) / res['snapshot_day']), 'events': rel(args.events), 'commands': [
               'uv run python scripts/collateral_watch.py snapshot', 'uv run python scripts/collateral_watch.py diff',
               'uv run python scripts/collateral_watch.py carry --out %s' % args.out if args.out else
               'uv run python scripts/collateral_watch.py carry',
               'uv run python scripts/collateral_watch.py run  # the daily job'],
           'endpoints': ENDPOINTS, 'api_gaps': API_GAPS, 'params': res['params'], 'ssr': res['ssr_source'],
           'carry_seconds': res['seconds'], 'http': res['http'], 'files': files,
           'snapshot_venues': {v: {'ok': i.get('ok'), 'errors': i.get('errors'), 'http': i.get('http'),
                                   'seconds': i.get('seconds')} for v, i in snap['venues'].items()}}
    write_json(out / 'manifest.json', man)


ENDPOINTS = {
    'hyperliquid': 'https://api.hyperliquid.xyz/info (allBorrowLendReserveStates, spotMeta, perpDexs, meta per dex, '
                   'metaAndAssetCtxs, spotMetaAndAssetCtxs, fundingHistory, l2Book) at 0.5 s a call; docs ' + HL_DOCS,
    'binance': BN_BAPI + '/public/margin/portfolio/collateral-rate, .../portfolio/tiered-collateral-rate, '
               '.../margin/vip/spec/list-all; ' + BN_F + '/fapi/v1/{assetIndex, exchangeInfo, premiumIndex, fundingInfo, '
               'ticker/24hr, fundingRate (no symbol, paged by time), depth}; ' + BN_S + '/api/v3/{ticker/bookTicker, depth}',
    'okx': OKX + '/api/v5/public/{discount-rate-interest-free-quota, interest-rate-loan-quota, instruments, mark-price, '
           'open-interest, funding-rate-history}; /api/v5/market/{tickers, books}',
    'bybit': BY + '/v5/spot-margin-trade/{collateral, data}; /v5/market/{instruments-info, tickers, funding/history, '
             'orderbook}',
    'deribit': DERIBIT + 'public/{get_currencies, pme/get_params, get_instruments, get_book_summary_by_currency, '
               'get_funding_rate_history, get_order_book}; X:SM haircuts ' + DERIBIT_ARTICLE,
}

API_GAPS = [
    'Hyperliquid: the info API serves portfolio-margin eligibility, LTV and borrow/supply rates '
    '(allBorrowLendReserveStates) but not the supply/borrow caps or the account requirements; those are parsed from the '
    'docs page and hashed per section.',
    'Binance: the official portfolio-margin collateral endpoints (/sapi/v1/portfolio/collateralRate, '
    '/sapi/v2/portfolio/collateralRate) need an API key; the website bapi endpoints used here are public but '
    'undocumented. Leverage brackets (true max leverage, maintenance tiers) are keyed (/fapi/v1/leverageBracket); '
    'requiredMarginPercent from exchangeInfo is used. Whether TradFi perps can be margined by portfolio-margin '
    'collateral is not stated by any public endpoint.',
    'Binance multi-assets mode: /fapi/v1/assetIndex lists 29 index assets but exchangeInfo marks only the '
    'marginAvailable ones as collateral; the haircut is read as the bid buffer.',
    'OKX: discount tiers are in units of the currency (disCcyEq = maxAmt x rate) and need a spot price to read at $1M; '
    'loan rates are the basic daily rates (VIP discounts not applied).',
    'Bybit: the single collateralRatio in /v5/spot-margin-trade/data is deprecated by the tiered logic; tiers from '
    '/v5/spot-margin-trade/collateral are used. Account-level collateral switches (/v5/account/collateral-info) are keyed.',
    'Deribit: the API serves the cross-collateral pool (get_currencies.in_cross_collateral_pool) and X:PM haircuts '
    '(public/pme/get_params) but not the standard-margin (X:SM) haircuts; those come from the support article '
    '(Zendesk help-centre JSON), hashed. Deribit funding has no interest leg (a dead band around zero), so its floor '
    'share counts hours at exactly 0.',
    'No venue publishes the borrow cost of its portfolio-margin negative balances as an API field except Hyperliquid '
    '(borrowYearlyRate); Binance/OKX/Bybit margin borrow rates are used as the stand-in, Deribit\'s collateral fee '
    'comes from the article.',
]


# ============================================================================================== run

def cmd_run(args):
    t0 = time.time()
    snap = cmd_snapshot(args)
    d = cmd_diff(args)
    res = cmd_carry(args)
    counts = []
    for v in VENUES:
        info = snap['venues'].get(v)
        if not info:
            continue
        c = info.get('counts', {})
        main = {'hyperliquid': 'portfolio_margin', 'binance': 'portfolio_margin', 'okx': 'multi_currency_margin',
                'bybit': 'uta', 'deribit': 'cross_collateral'}[v]
        counts.append('%s %d%s' % (v, (c.get(main) or {}).get('positive_ratio', 0),
                                   '' if all((info.get('ok') or {}).values()) and info.get('ok') else ' (incomplete)'))
    changes = [e for e in d['events'] if e['event'] != 'baseline']
    rows = res['rows']
    flagged = [r for r in rows if r['flag']]
    hl = [r for r in rows if r['venue'] == 'hyperliquid']
    errs = sorted(set(list(res['errors']) + [v for v, i in snap['venues'].items() if i.get('errors')]))
    print('collateral_watch %s: collateral %s; %s; carry %d rows, %d above %.0fpp, flagged %d%s; Hyperliquid %s; '
          'errors: %s; %.0fs' % (
              snap['date'], ', '.join(counts),
              ('%d events (%s)' % (len(changes), ', '.join(sorted({'%s %s/%s' % (e['event'], e['venue'], e['asset'])
                                                                    for e in changes}))[:300])) if d['compared'] else
              'baseline (no previous snapshot)', len(rows), sum(1 for r in rows if r['flag_excess']),
              100 * FLAG_EXCESS, len(flagged),
              (' (' + ', '.join('%s:%s %s' % (r['venue'], r['asset'], pc(r['excess_30d'], 1)) for r in flagged[:5]) + ')')
              if flagged else '',
              ', '.join('%s 30d %s at floor %s excess %s' % (r['asset'], pc(r['apr_30d'], 1), pu(r['floor_share_30d'], 0),
                                                            pc(r['excess_30d'], 1)) for r in hl) or 'n/a',
              ', '.join(errs) or 'none', time.time() - t0))
    return 0


# ============================================================================================== entry point

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in (('snapshot', cmd_snapshot), ('diff', cmd_diff), ('carry', cmd_carry), ('run', cmd_run)):
        p = sub.add_parser(name)
        p.add_argument('--day', default=None, help='UTC date YYYY-MM-DD (default: today / the newest snapshot)')
        p.add_argument('--venues', default=','.join(VENUES))
        p.add_argument('--watch', default=str(WATCH), help='snapshot root')
        p.add_argument('--events', default=str(EVENTS), help='append-only event log')
        if name in ('carry', 'run'):
            p.add_argument('--out', default=None, help='carry output directory (default: the snapshot day directory)')
        if name == 'snapshot':
            p.add_argument('--from-raw', action='store_true', help="rebuild the day's table from its saved raw files")
        p.set_defaults(fn=fn)
    args = ap.parse_args(argv)
    r = args.fn(args)
    return r if isinstance(r, int) else 0


if __name__ == '__main__':
    sys.exit(main())
