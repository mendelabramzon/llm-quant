#!/usr/bin/env python3
"""JLP hedged with the pool's own net delta, forward: does the hedge a trader would actually run keep the fee share?

Why. research/2026-10-10/house_vaults found JLP (Jupiter perps LP, Solana) hedged with SOL/ETH/BTC shorts beat the
savings rate by +8.3% a year out of sample (Newey-West t 3.80; re-measured +2.6..+6.6%), with a hedge it could only
estimate: a 60-day trailing regression, because there is no history of the pool's composition. Live, the hedge is the
pool's own net delta, which jlp-info publishes. The book quotes +2.5% on $10M, and its first kill gate is this test:
"first 60 days live: realised hedged excess below +1% a year with the jlp-info net-delta hedge".

Net delta. Per custody (SOL, ETH, WBTC; the stables carry no price exposure) the pool's AUM is linear in the oracle
price p of the custody's token:
    aum(p) = (owned - locked) * p + guaranteedUsd + shortSizes * (p - shortAvg) / shortAvg
`owned` includes the long traders' collateral (a long posts the token itself); `locked` is the longs' size in tokens;
`guaranteedUsd` is their size less collateral, fixed in dollars, so the longs' claim is locked * p - guaranteedUsd; the
last term is the pool's side of the shorts' P&L (shorts post stables; their size sits on the traded token's custody).
The pool's delta, in tokens, is therefore
    delta = owned - locked + shortSizes / shortAvg
long the tokens no trader has a claim on, short each long's exposure beyond its collateral, long the shorts' open
interest. Signs: a $1M 5x SOL long opened at $100 adds 2,000 SOL of collateral to owned and locks 10,000, so the pool
gets 8,000 SOL shorter (short the $0.8M the trader borrowed); a $1M short at $100 makes it 10,000 SOL longer. Worked
example, SOL in the 2026-10-10 jlp-info: 3,939,042 owned - 508,347 locked + $9.69M / $110.41 of shorts = 3,518,497 SOL,
$388.7M or 43% of the $899.7M AUM. house_vaults' book entry says the same ("owned minus locked plus short open interest
per custody"). The identity is checked on every snapshot: the price it implies from the custody's aumUsd and the price
shortPnlDelta implies agree to 1e-9 and re-price aumUsd within a few dollars, and that price is compared with the
Binance index.

How. `snapshot` (once a UTC day) appends one row to research/jlp_forward.jsonl: jlp-info (kept raw under
research/2026-10-11/jlp_forward/raw/<day>/), the net delta per JLP, Binance USDT-M and Hyperliquid marks and funding
rates, the funding settled on both venues since the previous row, the 30-day fee yield exactly as house_vaults computes
it, sUSDS.ssr(), the JLP supply on chain and the JLP DEX price. `score` replays FORWARD_RULE over consecutive daily rows
(the hedge set at row t earns from t to t+1) beside the backtest's 60-day regression hedge on the same days, and writes
the summary and the verdict to research/jlp_forward.json. A row is never edited. `check` runs the arithmetic on a saved
jlp-info file (the pre-registration sanity check) and, given a second file, attributes the JLP move between the two.

    uv run python scripts/jlp_forward.py snapshot              # daily; a second call the same UTC day is skipped
    uv run python scripts/jlp_forward.py snapshot --intraday   # an extra row marked intraday (never scored)
    uv run python scripts/jlp_forward.py score
    uv run python scripts/jlp_forward.py check --info research/2026-10-10/house_vaults/raw/jlp/jlp_info_2026-10-10.json
    uv run python scripts/jlp_forward.py hl-hedge [--no-collect]   # house_vaults' JLP / GM SOL hedges on Hyperliquid

Read-only everywhere: public GETs, the Hyperliquid info API through perp_rpc (>= 0.4 s a call), and one eth_call and
one getTokenSupply through the repo's key-holding helpers (live_rpc, solana_rpc), whose keys are never written.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import statistics
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import backtest as B  # noqa: E402
import house_vaults as H  # noqa: E402  (imported only: constants, HTTP pacing, history loaders, rolling betas)

LEDGER = ROOT / 'research' / 'jlp_forward.jsonl'
STUDY = ROOT / 'research' / '2026-10-11' / 'jlp_forward'
HV_RAW = H.OUT / 'raw'
HV_ANALYSIS = H.OUT / 'analysis.json'
JLP_INFO = 'https://perps-api.jup.ag/v1/jlp-info'
JUP_PRICE = 'https://lite-api.jup.ag/price/v3?ids=' + H.JLP_MINT
LLAMA_FEES = 'https://api.llama.fi/summary/fees/jupiter-perpetual-exchange?dataType=dailySupplySideRevenue'
KRAKEN_USDT = 'https://api.kraken.com/0/public/Ticker?pair=USDTZUSD'
SUSDS = '0xa3931d71877c0e7a3148cb7eb4463524fec27fbd'
SEL_SSR, SEL_CONVERT = '0x03607ceb', '0x07a2d13a'       # ssr(), convertToAssets(uint256)
RAY = 10 ** 27
USD_DEC = 6               # jlp-info's dollar amounts, prices and the JLP supply all carry 6 decimals
DAY_MS = H.DAY_MS
ASSETS = {                # hedged asset -> jlp-info custody, token decimals, the two perp venues' tickers
    'SOL': {'custody': 'SOL', 'decimals': 9, 'binance': 'SOLUSDT', 'hl': 'SOL'},
    'ETH': {'custody': 'ETH', 'decimals': 8, 'binance': 'ETHUSDT', 'hl': 'ETH'},
    'BTC': {'custody': 'WBTC', 'decimals': 8, 'binance': 'BTCUSDT', 'hl': 'BTC'},
}
STABLES = {'USDC', 'USDT', 'JUPUSD'}
RAW_FIELDS = ('owned', 'locked', 'guaranteedUsd', 'globalShortSizes', 'globalShortAveragePrice', 'shortPnlDelta',
              'shortTradersHasProfit', 'aumUsd', 'aumTokenAmount')
# Taker fees, one way, fraction of notional: Binance USDT-M VIP0 0.0500% (binance.com/en/fee/futureFee, no BNB
# discount; the same 5bp as house_vaults.HEDGE_FEE), Hyperliquid tier-0 perps 0.045%. Half-spreads on these three
# books are under 0.5bp and are not added.
TAKER = {'binance': 0.0005, 'hyperliquid': 0.00045}

# The rule, frozen before the first row (2026-10-11). The kill and promote thresholds are the book entry's
# (house_vaults.book_entry, 'jlp-hedged-house-lp'); the cost model is the backtest's except that the hedge is set to
# the target at every row (no 10% band: the forward rule trades the pool's delta as published).
FORWARD_RULE = {
    'id': 'jlp-net-delta-forward', 'book_entry': 'jlp-hedged-house-lp', 'registered': '2026-10-11',
    'start': 'the first daily row of research/jlp_forward.jsonl; earlier jlp-info files are a sanity check, not rows',
    'jlp_usd': 10_000_000,
    'hold': 'JLP tokens = jlp_usd / JLP price (aumUsd / supply) at the first row, held unchanged to the end',
    'hedge': 'at each daily row t: short, per asset, the net delta per JLP (owned - locked + shortSizes / shortAvg, '
             'over the JLP supply) x JLP held, traded at the row\'s mark; it earns from t to t+1 (no look-ahead)',
    'assets': list(ASSETS),
    'venue': 'Binance USDT-M perps: premiumIndex marks; fundingRate settlements x the mark each one carries',
    'second_venue': 'Hyperliquid: markPx; hourly fundingHistory x oracle price interpolated between rows',
    'margin_per_short': H.MARGIN,
    'capital': 'JLP value + margin x gross short notional, at each row (margin held idle)',
    'taker': TAKER,
    'jlp_round_trip': H.ENTRY_EXIT['JLP'],
    'one_off_costs': 'JLP round trip x jlp_usd, plus taker x gross short at the last row (closing the hedge); '
                     'charged once and amortised evenly over max(days elapsed, one_off_days) for the verdict; the same '
                     'over max(days elapsed, min_days), and the excess before one-offs, are reported beside it',
    'one_off_days': 365,
    'savings': 'sUSDS.ssr() read at each row (an APY), accrued simple over the period as house_vaults does',
    'nw_lags': 'backtest.newey_west_t default, floor(4 (n/100)^(2/9))',
    'min_days': 60,
    'kill_below': 0.01, 'promote_above': 0.025, 'promote_t': 2.0,
    'sigma_window': 14, 'sigma_max': 0.005, 'sigma_kill_run': 15, 'fee_yield_min': 0.065, 'depeg_max': 0.01,
    'kill': 'at 60 days, annualised excess over the savings rate on capital below +1% a year',
    'kill_now': ['the rolling 14-day standard deviation of the daily hedged return on capital above 0.5% on 15 '
                 'consecutive days (a persistently ineffective hedge: one tail day sits in at most 14 windows, so it '
                 'cannot reach the kill alone); a single window above 0.5% is a warning',
                 'the trailing 30-day fee yield (DefiLlama supply-side revenue / JLP AUM) below 6.5%'],
    'review': 'flagged for a reader, as the book\'s exploit / fee-split / AUM-limit / depeg gate: the AUM limit or the '
              'custody set differs from the first row, a non-stable custody is left unhedged, or the JLP DEX price is '
              'more than 1% from NAV',
    'promote': 'at 60 days, excess above +2.5% a year with Newey-West t above 2',
    'comparison': 'the backtest\'s chosen hedge (house_vaults roll60: 60-day trailing OLS of daily JLP returns on '
                  'SOL/ETH/BTC, refit every 7 days, >= 20 observations) on the same rows and costs, its window fed by '
                  'house_vaults\' DefiLlama/Binance history, a bridge to the first row, then the ledger\'s own periods',
    # Each revision names the hash it replaces and the last row written under it; rows up to that time are checked
    # against the replaced hash, later rows against the current one.
    'revisions': [{
        'date': '2026-10-11', 'replaces_hash': '6dfd4a88dece6013', 'last_row_ms': 1791676954075,
        'rows_under_replaced': 1, 'periods_scored_before': 0, 'decided_by': 'coordinator',
        'changes': [
            {'what': 'the verdict\'s excess amortises the one-off costs (JLP round trip + hedge close) over 365 days, '
                     'was the 60-day test; the 60-day amortisation and the before-one-offs excess stay as reported '
                     'columns',
             'why': '365 days is the intended minimum hold; amortised over 60 days the one-offs put ~1.2pp a year of '
                    'drag on a +1% kill line'},
            {'what': 'the sigma kill fires only when the rolling 14-day sigma has been above 0.5% on 15 consecutive '
                     'days, was the first window above 0.5%; a single window above 0.5% is a warning',
             'why': 'the gate is for a persistently ineffective hedge, and one tail day (the backtest\'s worst was '
                    '-2.06%) lifts a 14-day sigma above 0.5% on its own',
             'caveat': 'found in testing: one tail day sits in exactly 14 consecutive 14-day windows, so a 14-day run '
                       'could still be reached by that day alone; the coordinator set the run to 15 (longer than the '
                       'window) on 2026-10-11, before any scored period'}],
        'reason': 'both decided by the coordinator on 2026-10-11, before any outcome (one row, no scored period)'}],
}
# Every row carries this hash; `score` flags a row whose rule differs from the first row's (an edit after the start).
RULE_HASH = hashlib.sha256(json.dumps(FORWARD_RULE, sort_keys=True, default=str).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------------------------------
# jlp-info arithmetic (pure; tested)
# ----------------------------------------------------------------------------------------------------------------------
def units(x, d):
    """A jlp-info integer string -> float in natural units."""
    return int(x) / 10 ** d


def custody_aum(owned, locked, guaranteed_usd, short_usd, short_avg, p):
    """The custody's AUM at oracle price p: unclaimed tokens, plus what the longs borrowed, plus the pool's side of the
    shorts' P&L."""
    short = short_usd * (p - short_avg) / short_avg if (short_usd > 0 and short_avg > 0) else 0.0
    return (owned - locked) * p + guaranteed_usd + short


def custody_state(c, decimals):
    """One non-stable jlp-info custody -> natural units, the net delta, and the oracle price it was valued at.

    aum(p) = delta * p + guaranteedUsd - shortSizes, so the price is (aumUsd - guaranteedUsd + shortSizes) / delta;
    shortPnlDelta implies the same price independently, shortAvg * (1 + pool's short P&L / shortSizes)."""
    if abs(units(c['aumTokenAmount'], decimals) - float(c['aumTokenAmountFormatted'])) > 0.006:
        raise ValueError('%s: token decimals are not %d (aumTokenAmount %s vs %s)' % (
            c['symbol'], decimals, c['aumTokenAmount'], c['aumTokenAmountFormatted']))
    owned, locked = units(c['owned'], decimals), units(c['locked'], decimals)
    g = units(c['guaranteedUsd'], USD_DEC)
    G, avg = units(c['globalShortSizes'], USD_DEC), units(c['globalShortAveragePrice'], USD_DEC)
    spnl = units(c['shortPnlDelta'], USD_DEC)
    pool_spnl = -spnl if c.get('shortTradersHasProfit') else spnl     # + when the shorts are losing
    open_shorts = G > 0 and avg > 0
    short_tok = G / avg if open_shorts else 0.0
    delta = owned - locked + short_tok
    aum = units(c['aumUsd'], USD_DEC)
    p_aum = (aum - g + (G if open_shorts else 0.0)) / delta if delta > 0 else None
    p_short = avg * (1.0 + pool_spnl / G) if open_shorts else None
    resid = aum - custody_aum(owned, locked, g, G, avg, p_short) if p_short else None
    return {'owned': owned, 'locked': locked, 'guaranteed_usd': g, 'short_usd': G, 'short_avg': avg,
            'short_tokens': short_tok, 'pool_short_pnl': pool_spnl, 'delta_tokens': delta, 'aum_usd': aum,
            'oracle_px': p_aum, 'oracle_px_short': p_short, 'identity_resid_usd': resid,
            'long_claim_usd': (locked * p_aum - g) if p_aum else None,     # longs' collateral + open P&L
            'weight_pct': float(c['currentWeightagePct']), 'target_pct': float(c['targetWeightagePct']),
            'utilization_pct': float(c['utilizationPct']),
            'staked_tokens': units(c.get('totalStakedAmountLamports') or 0, decimals)}


def parse_info(info):
    """A jlp-info reply -> the pool (NAV = aumUsd / supply), the hedged custodies, the rest, and consistency checks."""
    aum, supply = units(info['aumUsd'], USD_DEC), units(info['jlpTotalSupply'], USD_DEC)
    by = {c['symbol']: c for c in info['custodies']}
    cust = {a: custody_state(by[m['custody']], m['decimals']) for a, m in ASSETS.items()}
    hedged = {m['custody'] for m in ASSETS.values()}
    others = {s: {'aum_usd': units(c['aumUsd'], USD_DEC), 'weight_pct': float(c['currentWeightagePct']),
                  'target_pct': float(c['targetWeightagePct']), 'stable': s in STABLES}
              for s, c in by.items() if s not in hedged}
    price = aum / supply
    pxs = [(c['oracle_px'], c['oracle_px_short']) for c in cust.values() if c['oracle_px'] and c['oracle_px_short']]
    res = [abs(c['identity_resid_usd']) for c in cust.values() if c['identity_resid_usd'] is not None]
    return {
        'aum_usd': aum, 'supply': supply, 'price': price, 'price_field': units(info['jlpPriceUsd'], USD_DEC),
        'aum_limit_usd': units(info['aumLimitUsd'], USD_DEC), 'apr_pct': float(info.get('jlpAprPct') or 0),
        'apy_pct': float(info.get('jlpApyPct') or 0), 'apr_updated': int(info.get('jlpAprLastUpdatedTimestamp') or 0),
        'realized_fee_usd': units(info.get('jlpRealizedFeeUsd') or 0, USD_DEC),
        'custodies': cust, 'others': others, 'custody_set': sorted(by),
        'unhedged': sorted(s for s, o in others.items() if not o['stable'] and o['aum_usd'] > 1e3),
        'delta_per_jlp': {a: cust[a]['delta_tokens'] / supply for a in ASSETS},
        'checks': {'sum_custody_aum_minus_pool_usd': sum(units(c['aumUsd'], USD_DEC) for c in by.values()) - aum,
                   'price_field_minus_nav': units(info['jlpPriceUsd'], USD_DEC) - price,
                   'oracle_px_two_ways_max_rel': max((abs(a / b - 1) for a, b in pxs), default=None),
                   'identity_resid_max_usd': max(res, default=None)},
    }


def fee_yield_30d(chart, aum):
    """house_vaults.analyze_jlp's 'fee_yield_30d_vs_venue_apr', verbatim: the mean of DefiLlama's daily supply-side
    revenue over the 30 days ending at its last point, x 365, over the AUM now."""
    if not chart or not aum:
        return None
    last = int(chart[-1][0])
    last30 = [v for t, v in chart if int(t) * 1000 >= (last - 29 * 86400) * 1000]
    return {'value': sum(last30) / len(last30) * 365 / aum, 'supply_side_usd': sum(last30), 'days': len(last30),
            'last_day': H.day_of(last), 'aum_usd': aum}


def ssr_apy(ray):
    """sUSDS.ssr() (a per-second rate in RAY) -> the annual yield it compounds to."""
    return (int(ray) / RAY) ** 31536000 - 1.0


def build_row(info, t_ms, binance, hl=None, funding=None, fees=None, ssr=None, supply_onchain=None, dex=None,
              kind='daily', raw_dir=None, errors=None, usdt_usd=None):
    """Everything one snapshot records, from already-fetched inputs (no network here). Jupiter's oracle quotes in USD
    and both perp venues in USDT, so the oracle-vs-index check is also given with the index converted at USDT/USD."""
    J = parse_info(info)
    by = {c['symbol']: c for c in info['custodies']}
    cust = {}
    for a, m in ASSETS.items():
        c = dict(J['custodies'][a])
        mk = binance[a]['mark']
        c['delta_usd'] = c['delta_tokens'] * mk                         # at the Binance mark
        c['delta_pct_aum'] = c['delta_usd'] / J['aum_usd']
        c['hedge_ratio'] = J['delta_per_jlp'][a] * mk / J['price']     # short dollars per dollar of JLP
        cust[a] = c
    chk = dict(J['checks'])
    chk['oracle_vs_binance_index_bp'] = {a: 1e4 * (J['custodies'][a]['oracle_px'] / binance[a]['index'] - 1)
                                         for a in ASSETS}
    if usdt_usd:
        chk['oracle_vs_binance_index_in_usd_bp'] = {
            a: 1e4 * (J['custodies'][a]['oracle_px'] / (binance[a]['index'] * usdt_usd) - 1) for a in ASSETS}
    if hl:
        chk['oracle_vs_hl_oracle_bp'] = {a: 1e4 * (J['custodies'][a]['oracle_px'] / hl[a]['oracle'] - 1) for a in ASSETS}
    if supply_onchain is not None:
        chk['supply_onchain_minus_api'] = supply_onchain - J['supply']
    fy = fee_yield_30d((fees or {}).get('chart'), J['aum_usd']) if fees else None
    if fy is not None:
        fy['defillama_total30d'] = fees.get('total30d')
    return {
        'rule': FORWARD_RULE['id'], 'rule_sha256_16': RULE_HASH, 'kind': kind, 'day': H.day_of(t_ms), 't_ms': int(t_ms),
        'ts': H.utc(t_ms).isoformat(),
        'jlp': {'price': J['price'], 'price_field': J['price_field'], 'aum_usd': J['aum_usd'], 'supply': J['supply'],
                'supply_onchain': supply_onchain, 'aum_limit_usd': J['aum_limit_usd'], 'apr_pct': J['apr_pct'],
                'apy_pct': J['apy_pct'], 'apr_updated': J['apr_updated'], 'realized_fee_usd': J['realized_fee_usd'],
                'dex_price': (dex or {}).get('price'), 'dex_liquidity_usd': (dex or {}).get('liquidity_usd'),
                'dex_vs_nav': ((dex['price'] / J['price'] - 1) if dex and dex.get('price') else None)},
        'delta_per_jlp': J['delta_per_jlp'],
        'custodies': cust, 'others': J['others'], 'custody_set': J['custody_set'], 'unhedged': J['unhedged'],
        'binance': binance, 'hyperliquid': hl, 'funding_since_prev': funding, 'fee_yield_30d': fy, 'ssr': ssr,
        'usdt_usd': usdt_usd, 'checks': chk,
        'raw': {a: {k: by[m['custody']][k] for k in RAW_FIELDS} for a, m in ASSETS.items()},
        'raw_dir': raw_dir, 'errors': errors or [],
    }


# ----------------------------------------------------------------------------------------------------------------------
# the ledger (append-only)
# ----------------------------------------------------------------------------------------------------------------------
def read_ledger(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def last_daily(rows):
    d = [r for r in rows if r.get('kind') == 'daily']
    return max(d, key=lambda r: r['t_ms']) if d else None


def append_row(path, row, intraday=False):
    """Append one row unless its UTC day already has a daily row; then an intraday row if asked, else nothing.
    Returns the kind written (or None). The check and the write happen under one exclusive lock; nothing earlier in
    the file is touched, and a row older than the last one is refused."""
    import fcntl
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        rows = [json.loads(line) for line in f.read().splitlines() if line.strip()]
        if rows and row['t_ms'] <= max(r['t_ms'] for r in rows):
            raise ValueError('row at %s is not after the last ledger row' % row['ts'])
        has_daily = any(r.get('day') == row['day'] and r.get('kind') == 'daily' for r in rows)
        if has_daily and not intraday:
            return None
        row = dict(row, kind='intraday' if has_daily else 'daily')
        f.seek(0, os.SEEK_END)
        f.write(json.dumps(row, sort_keys=True) + '\n')
        f.flush()
        os.fsync(f.fileno())
        return row['kind']


# ----------------------------------------------------------------------------------------------------------------------
# replay (pure; tested)
# ----------------------------------------------------------------------------------------------------------------------
def interp(p0, p1, t0, t1, t):
    if t1 <= t0:
        return p1
    w = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return p0 + (p1 - p0) * w


def marks_of(row, venue):
    if venue == 'hyperliquid':
        h = row.get('hyperliquid') or {}
        return {a: (h.get(a) or {}).get('mark') for a in ASSETS}
    if venue == 'oracle':
        return {a: row['custodies'][a]['oracle_px'] for a in ASSETS}
    return {a: row['binance'][a]['mark'] for a in ASSETS}


def funding_usd(r0, r1, held, venue):
    """Funding the short legs received over (r0, r1]: the sum over settlements of rate x tokens x price, positive
    rates being paid by longs to shorts. A Binance settlement carries its own mark; Hyperliquid's hourly rates are
    priced at the oracle interpolated between the rows (it charges funding on oracle notional). None if missing."""
    src = 'hyperliquid' if venue == 'hyperliquid' else 'binance'
    book = (r1.get('funding_since_prev') or {}).get(src)
    if not held:
        return 0.0
    if book is None:
        return None
    t0, t1 = r0['t_ms'], r1['t_ms']
    if venue == 'hyperliquid':
        p0 = {a: r0['hyperliquid'][a]['oracle'] for a in ASSETS}
        p1 = {a: r1['hyperliquid'][a]['oracle'] for a in ASSETS}
    else:
        p0, p1 = marks_of(r0, venue), marks_of(r1, venue)
    tot = 0.0
    for a, h in held.items():
        for rec in book.get(a) or []:
            px = rec[2] if (len(rec) > 2 and rec[2]) else interp(p0[a], p1[a], t0, t1, rec[0])
            tot += h * rec[1] * px
    return tot


def simulate(D, tokens, N, venue='binance'):
    """The frozen rule's accounting over consecutive daily rows D. tokens[i] = {asset: tokens short} set at row i and
    held to row i+1; N = JLP tokens held. Per period, in dollars: JLP N (P1 - P0), the shorts' -h (m1 - m0), funding,
    and the taker fee on the notional traded at row i. Capital = JLP value + margin x gross short, at row i. A period
    whose venue marks are missing at either end is left out of that venue's column (Binance marks are required by the
    snapshot, so the primary column never skips); missing funding counts zero and is flagged (the next snapshot back-
    fills the window, so the total is kept and only its timing shifts by a period)."""
    taker = TAKER['hyperliquid' if venue == 'hyperliquid' else 'binance']
    out, held = [], {}
    for i in range(len(D) - 1):
        r0, r1 = D[i], D[i + 1]
        m0, m1 = marks_of(r0, venue), marks_of(r1, venue)
        if any(m0[a] is None or m1[a] is None for a in ASSETS):
            continue
        tgt = {a: v for a, v in (tokens[i] or {}).items() if v}
        traded = sum(abs(tgt.get(a, 0.0) - held.get(a, 0.0)) * m0[a] for a in ASSETS)
        held = tgt
        fund = funding_usd(r0, r1, held, venue)
        missing = fund is None
        fund = 0.0 if missing else fund
        v0, v1 = N * r0['jlp']['price'], N * r1['jlp']['price']
        price = -sum(h * (m1[a] - m0[a]) for a, h in held.items())
        cost = taker * traded
        gross = sum(abs(h) * m0[a] for a, h in held.items())
        cap = v0 + H.MARGIN * gross
        days = (r1['t_ms'] - r0['t_ms']) / DAY_MS
        ssr = (r0.get('ssr') or {}).get('apy')
        ssr = H.SSR_NOW if ssr is None else ssr
        pnl = (v1 - v0) + price + fund - cost
        out.append({'t0': r0['t_ms'], 't1': r1['t_ms'], 'day': r1['day'], 'days': days, 'jlp_pnl': v1 - v0,
                    'price_pnl': price, 'funding_pnl': fund, 'cost': cost, 'traded': traded, 'gross': gross,
                    'capital': cap, 'jlp_value': v0, 'pnl': pnl, 'ret': pnl / cap, 's': ssr * days / 365.0,
                    'held': held, 'r_v': r1['jlp']['price'] / r0['jlp']['price'] - 1.0,
                    'r': {a: m1[a] / m0[a] - 1.0 for a in ASSETS}, 'm_end': m1, 'funding_missing': missing})
    return out


def close_cost(sim, venue='binance'):
    """Taker fee on closing the hedge held over the last period, at the last row's marks."""
    if not sim:
        return 0.0
    last = sim[-1]
    return TAKER['hyperliquid' if venue == 'hyperliquid' else 'binance'] * sum(
        abs(h) * last['m_end'][a] for a, h in last['held'].items())


def series_stats(sim, one_off_usd, rule=FORWARD_RULE):
    """Excess over the savings rate on capital, per period: ret - savings - the amortised one-off costs (spread over
    max(days, one_off_days) for the verdict; over max(days, min_days) as a reported column). Annualised by time as
    house_vaults.seg_stats does; Newey-West t at backtest's default lags; daily sigma per sqrt(day)."""
    if not sim:
        return {'n': 0, 'days': 0.0}
    days = sum(p['days'] for p in sim)

    def amortised(span_days):
        span = max(days, span_days)
        return [one_off_usd * p['days'] / span / p['capital'] for p in sim]
    amort, amort60 = amortised(rule['one_off_days']), amortised(rule['min_days'])
    xs = [p['ret'] - p['s'] - a for p, a in zip(sim, amort)]
    t, pv = B.newey_west_t(xs)
    daily = [p['ret'] / math.sqrt(p['days']) for p in sim]

    def ann(vals):
        return sum(vals) / days * 365.0

    comp = {'jlp': ann([p['jlp_pnl'] / p['capital'] for p in sim]),
            'hedge_price': ann([p['price_pnl'] / p['capital'] for p in sim]),
            'funding': ann([p['funding_pnl'] / p['capital'] for p in sim]),
            'rebalance_cost': -ann([p['cost'] / p['capital'] for p in sim]),
            'one_off_amortised': -ann(amort), 'savings': -ann([p['s'] for p in sim])}
    return {'n': len(sim), 'days': days, 'start': H.day_of(sim[0]['t0']), 'end': H.day_of(sim[-1]['t1']),
            'ann_excess': ann(xs), 'ann_hedged_return': ann([p['ret'] for p in sim]),
            'ann_excess_before_one_off': ann([p['ret'] - p['s'] for p in sim]),
            'ann_excess_one_off_60d': ann([p['ret'] - p['s'] - a for p, a in zip(sim, amort60)]),
            'nw_t': t, 'nw_p': pv, 'daily_sigma': statistics.stdev(daily) if len(daily) > 1 else None,
            'worst_day': min(xs), 'best_day': max(xs), 'cum_pnl_usd': sum(p['pnl'] for p in sim),
            'one_off_usd': one_off_usd, 'mean_capital_usd': statistics.fmean(p['capital'] for p in sim),
            'mean_gross_short_usd': statistics.fmean(p['gross'] for p in sim), 'components_ann': comp,
            'excess_series': xs}


def sigma_check(sim, window=14, cap=0.005, kill_run=14):
    """The rolling standard deviation of the daily hedged return over `window` periods. The first window above `cap`
    is a warning; the kill day is the one on which `kill_run` consecutive windows have been above it."""
    daily = [(p['day'], p['ret'] / math.sqrt(p['days'])) for p in sim or []]
    roll = [(daily[k][0], statistics.stdev([x for _, x in daily[k - window + 1:k + 1]]))
            for k in range(window - 1, len(daily))]
    run = best = 0
    kill_day = None
    for d, s in roll:
        run = run + 1 if s > cap else 0
        best = max(best, run)
        if kill_day is None and run >= kill_run:
            kill_day = d
    return {'window': window, 'cap': cap, 'kill_run': kill_run, 'n_windows': len(roll),
            'latest': roll[-1][1] if roll else None, 'max': max((s for _, s in roll), default=None),
            'first_breach': next((d for d, s in roll if s > cap), None), 'kill_day': kill_day,
            'longest_run_above': best, 'current_run_above': run, 'series': roll}


def expected_hash(t_ms, rule=FORWARD_RULE, current=None):
    """The rule hash a row written at t_ms must carry: the current one, or the one a documented revision replaced if
    the row predates that revision."""
    h = current or RULE_HASH
    for rev in sorted(rule.get('revisions') or [], key=lambda r: r['last_row_ms'], reverse=True):
        if t_ms <= rev['last_row_ms']:
            h = rev['replaces_hash']
    return h


def fee_check(rows, floor):
    vals = [(r['day'], r['fee_yield_30d']['value']) for r in rows
            if r.get('fee_yield_30d') and r['fee_yield_30d'].get('value') is not None]
    if not vals:
        return {'latest': None, 'first_breach': None}
    return {'latest': vals[-1][1], 'latest_day': vals[-1][0], 'min': min(v for _, v in vals),
            'first_breach': next((d for d, v in vals if v < floor), None), 'floor': floor}


def event_flags(rows, depeg_max):
    """The book's event gates that a snapshot can see; each is reported once, at its first occurrence."""
    if not rows:
        return []
    ev, seen = [], set()
    lim0, set0 = rows[0]['jlp']['aum_limit_usd'], rows[0]['custody_set']

    def add(key, msg):
        if key not in seen:
            seen.add(key)
            ev.append(msg)
    for r in rows:
        want = expected_hash(r['t_ms'])
        if r.get('rule_sha256_16') != want:
            add('rule', '%s: row carries FORWARD_RULE hash %s, expected %s (an undocumented rule edit)' % (
                r['day'], r.get('rule_sha256_16'), want))
        if r['jlp']['aum_limit_usd'] != lim0:
            add('limit', '%s: AUM limit %.0f -> %.0f' % (r['day'], lim0, r['jlp']['aum_limit_usd']))
        if r['custody_set'] != set0:
            add('set', '%s: custodies %s -> %s' % (r['day'], ','.join(set0), ','.join(r['custody_set'])))
        if r.get('unhedged'):
            add('unhedged', '%s: non-stable custody not hedged: %s' % (r['day'], ','.join(r['unhedged'])))
        dv = r['jlp'].get('dex_vs_nav')
        if dv is not None and abs(dv) > depeg_max:
            add('depeg', '%s: JLP DEX price %+.2f%% from NAV' % (r['day'], 100 * dv))
        fy = r.get('fee_yield_30d') or {}
        if fy.get('last_day') and H.day_ts(r['day']) - H.day_ts(fy['last_day']) > 3 * 86400:
            add('stale', '%s: DefiLlama fees end %s, the fee gate is reading stale data' % (r['day'], fy['last_day']))
    return ev


def verdict(days, ann_excess, t, sigma_breach=None, fee_breach=None, events=(), rule=FORWARD_RULE):
    """The frozen rule's verdict: immediate kills first, then 'accumulating (n of N days)' until the minimum sample,
    then kill / promote / hold at the book's thresholds; event flags are appended for a reader."""
    n = int(days + 0.5)
    if sigma_breach:
        v = 'kill: %d-day hedged sigma above %.1f%% on %d consecutive days (on %s)' % (
            rule['sigma_window'], 100 * rule['sigma_max'], rule['sigma_kill_run'], sigma_breach)
    elif fee_breach:
        v = 'kill: 30-day fee yield below %.1f%% (first %s)' % (100 * rule['fee_yield_min'], fee_breach)
    elif n < rule['min_days']:
        v = 'accumulating (%d of %d days)' % (n, rule['min_days'])
    elif ann_excess is None or ann_excess < rule['kill_below']:
        v = 'kill: realised excess %s a year after %d days, below +%.1f%%' % (
            '—' if ann_excess is None else '%+.2f%%' % (100 * ann_excess), n, 100 * rule['kill_below'])
    elif ann_excess > rule['promote_above'] and t is not None and t > rule['promote_t']:
        v = 'promote: excess %+.2f%% a year, t %.2f after %d days' % (100 * ann_excess, t, n)
    else:
        v = 'hold: excess %+.2f%% a year (t %s) after %d days, between the kill and promote bars' % (
            100 * ann_excess, '—' if t is None else '%.2f' % t, n)
    if events:
        v += '; review: ' + '; '.join(events)
    return v


def residual_betas(sim, min_obs=20):
    """OLS of the hedged return on the hedge assets' returns: near zero when the hedge tracks the pool's delta."""
    if not sim or len(sim) < min_obs:
        return None
    fit = H.ols([p['ret'] for p in sim], [[p['r'][a] for a in ASSETS] for p in sim])
    if not fit:
        return None
    return {'n': fit['n'], 'betas': dict(zip(ASSETS, fit['betas'])),
            't': dict(zip(ASSETS, fit['t'][1:])), 'r2': fit['r2'], 'alpha_ann': fit['alpha'] * 365}


def regression_betas(D, hv_raw=HV_RAW, window=60, every=7, min_obs=20):
    """The betas the backtest's chosen hedge would set at each daily row: house_vaults.rolling_betas (60-day trailing
    OLS, refit every 7 days on the schedule anchored at the start of its history) over house_vaults' DefiLlama/Binance
    periods, a bridge from their last point to the first row, the ledger's periods, and a probe period starting at the
    last row (its betas are the ones set there). Also returns the betas at the last historical period, which must equal
    analysis.json's last_rolling_betas."""
    assets = list(ASSETS)
    if not D or not (hv_raw / 'jlp').exists() or not (hv_raw / 'binance').exists():
        return None
    j = H.load_jlp(hv_raw)
    book = H.PriceBook(hv_raw)
    P = [p for p in H.attach_legs(H.price_returns(j['points']), book, assets) if p['t1'] <= D[0]['t_ms']]
    if not P:
        return None
    bridge = None
    th = P[-1]['t1']
    then = {a: book.price(a, th) for a in assets}
    if all(then.values()):
        bridge = {'t0': th, 't1': D[0]['t_ms'], 'days': (D[0]['t_ms'] - th) / DAY_MS,
                  'r_v': D[0]['jlp']['price'] / P[-1]['p1'] - 1.0,
                  'r': {a: D[0]['binance'][a]['mark'] / then[a] - 1.0 for a in assets}}
    fwd = [{'t0': r0['t_ms'], 't1': r1['t_ms'], 'days': (r1['t_ms'] - r0['t_ms']) / DAY_MS,
            'r_v': r1['jlp']['price'] / r0['jlp']['price'] - 1.0,
            'r': {a: r1['binance'][a]['mark'] / r0['binance'][a]['mark'] - 1.0 for a in assets}}
           for r0, r1 in zip(D, D[1:])]
    probe = {'t0': D[-1]['t_ms'], 't1': D[-1]['t_ms'] + DAY_MS, 'days': 1.0, 'r_v': 0.0, 'r': {a: 0.0 for a in assets}}
    allp = P + ([bridge] if bridge else []) + fwd + [probe]
    betas = H.rolling_betas(allp, assets, window, every, min_obs)
    k = len(P) + (1 if bridge else 0)
    return {'betas': betas[k:], 'last_historical': betas[len(P) - 1], 'history_end': H.utc(th).isoformat(),
            'bridge': bridge, 'n_history': len(P)}


def hv_simulator(D, betas):
    """house_vaults.simulate_hedge (10% band, funding as the sum of rates) on the ledger's periods: the backtest's own
    accounting of the regression hedge, a cross-check on `simulate`."""
    P = []
    for r0, r1 in zip(D, D[1:]):
        fs = (r1.get('funding_since_prev') or {}).get('binance') or {}
        P.append({'t0': r0['t_ms'], 't1': r1['t_ms'], 'days': (r1['t_ms'] - r0['t_ms']) / DAY_MS,
                  'r_v': r1['jlp']['price'] / r0['jlp']['price'] - 1.0,
                  'r': {a: r1['binance'][a]['mark'] / r0['binance'][a]['mark'] - 1.0 for a in ASSETS},
                  'f': {a: sum(x[1] for x in fs.get(a) or []) for a in ASSETS},
                  's': (((r0.get('ssr') or {}).get('apy')) or H.SSR_NOW) * (r1['t_ms'] - r0['t_ms']) / DAY_MS / 365.0})
    if not P:
        return {'n': 0}
    sim = H.simulate_hedge(P, betas[:len(P)])
    xs = [s['ret'] - p['s'] for s, p in zip(sim, P)]
    days = sum(p['days'] for p in P)
    return {'n': len(P), 'days': days, 'ann_excess_before_one_off': sum(xs) / days * 365.0,
            'note': 'house_vaults.simulate_hedge with its 10% band; no JLP round trip, no closing trade'}


def score_rows(rows, hv_raw=HV_RAW, analysis_path=HV_ANALYSIS, rule=FORWARD_RULE):
    """The forward test so far: every model on the same daily rows, the kill flags and the verdict."""
    D = sorted((r for r in rows if r.get('kind') == 'daily'), key=lambda r: r['t_ms'])
    res = {'rule': rule, 'rows': {'daily': len(D), 'intraday': sum(1 for r in rows if r.get('kind') == 'intraday')}}
    if not D:
        res['summary'] = {'verdict': verdict(0, None, None, rule=rule)}
        return res
    res['rows'].update({'first': D[0]['day'], 'last': D[-1]['day']})
    N = rule['jlp_usd'] / D[0]['jlp']['price']
    warn = []
    for r0, r1 in zip(D, D[1:]):
        fs = r1.get('funding_since_prev') or {}
        if fs.get('from_ms') != r0['t_ms']:
            warn.append('%s: funding window starts %s, previous row %s' % (r1['day'], fs.get('from_ms'), r0['t_ms']))
    tok_nd = [{a: r['delta_per_jlp'][a] * N for a in ASSETS} for r in D]

    def by_ratio(ratios):
        return [{a: (q or {}).get(a, 0.0) * N * r['jlp']['price'] / r['binance'][a]['mark'] for a in ASSETS}
                for q, r in zip(ratios, D)]
    reg = regression_betas(D, hv_raw)
    models = {'net_delta_binance': (tok_nd, 'binance'), 'net_delta_hyperliquid': (tok_nd, 'hyperliquid'),
              'net_delta_oracle_marked': (tok_nd, 'oracle')}
    if reg:
        models['regression60_binance'] = (by_ratio(reg['betas']), 'binance')
    models['target_weights_binance'] = (by_ratio([{a: r['custodies'][a]['target_pct'] / 100.0 for a in ASSETS}
                                                  for r in D]), 'binance')
    models['unhedged'] = ([{}] * len(D), 'binance')
    sims, stats = {}, {}
    for name, (tok, venue) in models.items():
        sim = simulate(D, tok, N, venue)
        sims[name] = sim
        one_off = rule['jlp_round_trip'] * rule['jlp_usd'] + close_cost(sim, venue)
        st = series_stats(sim, one_off, rule)
        st.pop('excess_series', None)
        st.update({'residual_betas': residual_betas(sim), 'venue': venue,
                   'periods_left_out': len(D) - 1 - len(sim),
                   'periods_funding_missing': sum(1 for p in sim if p['funding_missing'])})
        stats[name] = st
    if reg:
        stats['regression60_backtest_simulator'] = hv_simulator(D, reg['betas'])
    prim = sims['net_delta_binance'] or []
    P0 = series_stats(prim, rule['jlp_round_trip'] * rule['jlp_usd'] + close_cost(prim), rule) if prim else \
        {'n': 0, 'days': 0.0, 'ann_excess': None, 'nw_t': None, 'excess_series': []}
    xs = P0.pop('excess_series')
    sg = sigma_check(prim, rule['sigma_window'], rule['sigma_max'], rule['sigma_kill_run'])
    if sg['first_breach']:
        warn.append('%s: %d-day hedged sigma first above %.1f%% (a warning; the kill needs %d consecutive days)' % (
            sg['first_breach'], rule['sigma_window'], 100 * rule['sigma_max'], rule['sigma_kill_run']))
    fc = fee_check(D, rule['fee_yield_min'])
    ev = event_flags(sorted(rows, key=lambda r: r['t_ms']), rule['depeg_max'])
    v = verdict(P0['days'], P0.get('ann_excess'), P0.get('nw_t'), sg['kill_day'], fc['first_breach'], ev, rule)
    res['summary'] = {k: P0.get(k) for k in ('n', 'days', 'start', 'end', 'ann_excess', 'ann_excess_before_one_off',
                                             'ann_excess_one_off_60d', 'ann_hedged_return', 'nw_t', 'nw_p',
                                             'daily_sigma', 'worst_day', 'best_day', 'cum_pnl_usd', 'one_off_usd',
                                             'mean_capital_usd', 'components_ann')}
    res['summary']['verdict'] = v
    res['flags'] = {'sigma': {k: x for k, x in sg.items() if k != 'series'}, 'fee_yield': fc, 'events': ev,
                    'warnings': warn,
                    'rule': {'hash': RULE_HASH, 'revisions': [{k: r[k] for k in ('date', 'replaces_hash', 'changes')}
                                                              for r in rule.get('revisions') or []]}}
    res['models'] = stats
    last = D[-1]
    an = json.loads(Path(analysis_path).read_text()) if Path(analysis_path).exists() else None
    an_b = (an or {}).get('vaults', {}).get('JLP', {}).get('last_rolling_betas') if an else None
    res['start'] = {'day': D[0]['day'], 'ts': D[0]['ts'], 'jlp_price': D[0]['jlp']['price'], 'jlp_tokens': N}
    res['latest'] = snapshot_summary(last, N, reg['betas'][-1] if reg else None, an_b)
    if reg:
        res['regression'] = {'history_end': reg['history_end'], 'n_history': reg['n_history'], 'bridge': reg['bridge'],
                             'betas_at_last_historical_period': reg['last_historical'],
                             'analysis_json_last_rolling_betas': an_b,
                             'replication_max_abs_diff': (max(abs(reg['last_historical'][a] - an_b[a]) for a in ASSETS)
                                                          if an_b and reg['last_historical'] else None)}
    res['ratios'] = [{'day': r['day'], 'net_delta': {a: r['custodies'][a]['hedge_ratio'] for a in ASSETS},
                      'regression60': (reg['betas'][i] if reg else None)} for i, r in enumerate(D)]
    rsim = sims.get('regression60_binance') or [None] * len(prim)
    res['periods'] = [{'day': p['day'], 'days': round(p['days'], 4), 'jlp_ret': p['r_v'], 'hedged_ret': p['ret'],
                       'excess': x, 'jlp_pnl': p['jlp_pnl'], 'hedge_price_pnl': p['price_pnl'],
                       'funding_pnl': p['funding_pnl'], 'cost': p['cost'], 'capital': p['capital'],
                       'regression60_ret': q['ret'] if q else None, 'assets': p['r']}
                      for p, x, q in zip(prim, xs, rsim)]
    return res


def snapshot_summary(r, N, reg_now=None, an_betas=None):
    """One row as the report reads it: the pool, the delta, the hedge at the rule's size, funding on both venues."""
    out = {'day': r['day'], 'ts': r['ts'], 'jlp_price': r['jlp']['price'], 'aum_usd': r['jlp']['aum_usd'],
           'supply': r['jlp']['supply'], 'supply_onchain': r['jlp'].get('supply_onchain'),
           'dex_vs_nav': r['jlp'].get('dex_vs_nav'), 'apr_pct_venue': r['jlp'].get('apr_pct'),
           'fee_yield_30d': (r.get('fee_yield_30d') or {}).get('value'), 'ssr_apy': (r.get('ssr') or {}).get('apy'),
           'jlp_tokens_held': N, 'jlp_value_usd': N * r['jlp']['price'], 'assets': {}}
    gross = 0.0
    for a in ASSETS:
        c, b, h = r['custodies'][a], r['binance'][a], (r.get('hyperliquid') or {}).get(a) or {}
        tok = r['delta_per_jlp'][a] * N
        gross += tok * b['mark']
        out['assets'][a] = {
            'delta_tokens': c['delta_tokens'], 'delta_usd': c['delta_usd'], 'delta_pct_aum': c['delta_pct_aum'],
            'owned': c['owned'], 'locked': c['locked'], 'short_tokens': c['short_tokens'],
            'delta_per_jlp': r['delta_per_jlp'][a], 'hedge_tokens': tok, 'hedge_usd': tok * b['mark'],
            'hedge_ratio': c['hedge_ratio'], 'regression60_now': (reg_now or {}).get(a),
            'regression60_analysis_json': (an_betas or {}).get(a), 'target_weight': c['target_pct'] / 100.0,
            'binance_mark': b['mark'], 'binance_funding_ann': b['funding_ann'],
            'hl_mark': h.get('mark'), 'hl_funding_ann': h.get('funding_ann'),
            'oracle_px': c['oracle_px'], 'oracle_vs_binance_index_bp': r['checks']['oracle_vs_binance_index_bp'][a]}
    out['gross_short_usd'] = gross
    out['capital_usd'] = N * r['jlp']['price'] + H.MARGIN * gross
    return out


# ----------------------------------------------------------------------------------------------------------------------
# fetch (network; read-only)
# ----------------------------------------------------------------------------------------------------------------------
def fetch_binance(fund_info):
    raw, out = {}, {}
    for a, m in ASSETS.items():
        x = H.http_json('%s/fapi/v1/premiumIndex?symbol=%s' % (H.BINANCE, m['binance']))
        raw[m['binance']] = x
        iv = int((fund_info.get(m['binance']) or {}).get('fundingIntervalHours') or 8)
        rate = float(x['lastFundingRate'])
        out[a] = {'symbol': m['binance'], 'mark': float(x['markPrice']), 'index': float(x['indexPrice']),
                  'funding_rate': rate, 'interval_h': iv, 'funding_ann': rate * 24.0 / iv * 365.0,
                  'next_funding_ms': int(x['nextFundingTime']), 'time_ms': int(x['time'])}
    return out, raw


def binance_funding(sym, from_ms, to_ms):
    """Settlements in (from_ms, to_ms] as [time, rate, mark]."""
    rows, cur = [], from_ms + 1
    while cur <= to_ms:
        q = urllib.parse.urlencode({'symbol': sym, 'startTime': cur, 'endTime': to_ms, 'limit': 1000})
        page = H.http_json('%s/fapi/v1/fundingRate?%s' % (H.BINANCE, q))
        if not page:
            break
        rows += [[int(x['fundingTime']), float(x['fundingRate']), float(x['markPrice']) if x.get('markPrice') else None]
                 for x in page]
        if len(page) < 1000:
            break
        cur = int(page[-1]['fundingTime']) + 1
    return sorted(r for r in {r[0]: r for r in rows}.values() if from_ms < r[0] <= to_ms)


def fetch_hl(api):
    import perp_rpc as R
    meta, ctxs = R.meta_and_ctxs(api)
    names = [u['name'] for u in meta['universe']]
    raw, out = {}, {}
    for a, m in ASSETS.items():
        c = ctxs[names.index(m['hl'])]
        raw[m['hl']] = c
        f = float(c['funding'])
        out[a] = {'mark': float(c['markPx']), 'oracle': float(c['oraclePx']), 'funding_hourly': f,
                  'funding_ann': f * 24.0 * 365.0, 'premium': float(c.get('premium') or 0.0),
                  'open_interest': float(c['openInterest'])}
    return out, raw


def hl_funding(api, coin, from_ms, to_ms):
    """Hourly settlements in (from_ms, to_ms] as [time, rate]."""
    import perp_rpc as R
    rows, cur = [], from_ms + 1
    while True:
        page = R.funding_history(api, coin, cur, to_ms) or []
        rows += [[int(x['time']), float(x['fundingRate'])] for x in page]
        if len(page) < 500:
            break
        cur = int(page[-1]['time']) + 1
    return sorted(r for r in {r[0]: r for r in rows}.values() if from_ms < r[0] <= to_ms)


LATE_MS = 2 * 3600 * 1000      # how far before the previous row to look for settlements it missed


def window_records(recs, prev, src, asset):
    """This row's settlements: those after the previous row, plus any inside the previous row's own window that it
    did not record (published by the venue after that snapshot was taken). Nothing before the test is ever added,
    and nothing is counted twice. Returns (records, late times)."""
    pf = prev.get('funding_since_prev') or {}
    start = pf.get('from_ms')
    have = {x[0] for x in ((pf.get(src) or {}).get(asset) or [])}
    late = [x for x in recs if start is not None and start < x[0] <= prev['t_ms'] and x[0] not in have]
    return sorted(late + [x for x in recs if x[0] > prev['t_ms']]), [x[0] for x in late]


def fetch_funding(prev, t_ms, api, soft):
    """Settlements on both venues for the period (previous daily row, now]; Binance is required, Hyperliquid soft.
    The look-back reaches LATE_MS before the previous row, or its whole window when that venue failed there."""
    pf = prev.get('funding_since_prev') or {}
    out = {'from_ms': prev['t_ms'], 'to_ms': t_ms, 'binance': {}, 'late': {}}

    def lo(src):
        return pf['from_ms'] if (pf.get('from_ms') and pf.get(src) is None) else prev['t_ms'] - LATE_MS
    for a, m in ASSETS.items():
        recs = binance_funding(m['binance'], lo('binance'), t_ms)
        out['binance'][a], late = window_records(recs, prev, 'binance', a)
        if late:
            out['late']['binance_' + a] = late

    def hl_all():
        got = {}
        for a, m in ASSETS.items():
            recs = hl_funding(api, m['hl'], lo('hyperliquid'), t_ms)
            got[a], late = window_records(recs, prev, 'hyperliquid', a)
            if late:
                out['late']['hyperliquid_' + a] = late
        return got
    out['hyperliquid'] = soft('hyperliquid fundingHistory', hl_all)
    return out


def fetch_fees():
    d = H.http_json(LLAMA_FEES)
    ch = [[int(t), float(v)] for t, v in d['totalDataChart']]
    return {'chart': ch[-90:], 'total30d': d.get('total30d'), 'total24h': d.get('total24h'), 'n_points': len(ch)}


def fetch_ssr():
    import live_rpc as L
    rpc = L.RPC(max_credits=5000)
    blk = int(rpc.call('eth_blockNumber', []), 16)
    ray = int(rpc.eth_call(SUSDS, SEL_SSR, hex(blk)), 16)
    nav = int(rpc.eth_call(SUSDS, SEL_CONVERT + L.enc_uint(10 ** 18), hex(blk)), 16) / 1e18
    return {'apy': ssr_apy(ray), 'ray': str(ray), 'susds_nav': nav, 'block': blk,
            'source': 'sUSDS.ssr() on Ethereum (live_rpc)'}


def fetch_supply():
    import solana_rpc as S
    v = S.Client().call('getTokenSupply', [H.JLP_MINT])
    return int(v['value']['amount']) / 10 ** int(v['value']['decimals']), v['context']['slot']


def fetch_dex():
    x = (H.http_json(JUP_PRICE) or {}).get(H.JLP_MINT) or {}
    return {'price': float(x['usdPrice']), 'liquidity_usd': float(x.get('liquidity') or 0.0), 'block': x.get('blockId')}


def fetch_usdt_usd():
    """USDT in dollars, the mid of Kraken's USDT/USD book (public)."""
    t = H.http_json(KRAKEN_USDT)['result']['USDTZUSD']
    return (float(t['a'][0]) + float(t['b'][0])) / 2.0


# ----------------------------------------------------------------------------------------------------------------------
# study: house_vaults' hedged backtests with the shorts on Hyperliquid instead of Binance
# ----------------------------------------------------------------------------------------------------------------------
HL_HISTORY = STUDY / 'raw' / 'hl_history'
HL_STORE = ROOT / 'research' / '2026-10-09' / 'perps_history'      # perp_history's store (since 2025-10-01), read only
HL_FLOOR = 0.0000125        # Hyperliquid's hourly rate whenever the premium sits inside the clamp: 0.01% per 8h / 8
BN_FLOOR = 0.0001           # Binance's per-settlement equivalent, 0.01% per 8h
STUDY_VAULTS = ('JLP', 'GM_SOL-USDC')


def collect_hl_funding(coins=('SOL', 'ETH', 'BTC'), since='2023-05-01', out=HL_HISTORY, interval=3.0):
    """Hyperliquid's hourly funding for the hedge coins from `since` to now, paged from the public fundingHistory into
    out/funding_<coin>.json.gz as [time_ms, rate, premium]; resumable from the last cached row. Paced at `interval`
    seconds a call because another job shares the info API; perp_rpc backs off on 429."""
    import perp_rpc as R
    api = R.Info(interval=max(0.4, interval))
    end = int(time.time() * 1000)
    got = {}
    for coin in coins:
        f = Path(out) / ('funding_%s.json.gz' % coin)
        rows = H.load_json(f) if f.exists() else []
        cur = (rows[-1][0] + 1) if rows else H.day_ts(since) * 1000
        pages = 0
        while cur < end:
            page = R.funding_history(api, coin, cur, end) or []
            rows += [[int(x['time']), float(x['fundingRate']), float(x.get('premium') or 0.0)] for x in page]
            pages += 1
            if len(page) < 500:
                break
            cur = int(page[-1]['time']) + 1
            if pages % 10 == 0:
                H.save_json(f, rows)
        rows = sorted({r[0]: r for r in rows}.values())
        H.save_json(f, rows)
        got[coin] = {'rows': len(rows), 'first': H.utc(rows[0][0]).isoformat(), 'last': H.utc(rows[-1][0]).isoformat(),
                     'pages_this_run': pages}
        print('hl funding %s: %d rows %s .. %s' % (coin, len(rows), got[coin]['first'][:16], got[coin]['last'][:16]),
              flush=True)
    got['api'] = api.stats()
    return got


class HLBook(H.PriceBook):
    """house_vaults' PriceBook with Hyperliquid's hourly funding in place of Binance's 8-hourly settlements. The price
    leg stays on Binance's hourly closes (both perps track one index; `hl_price_check` measures the difference where
    the repo holds Hyperliquid closes). funding(a, t0, t1) sums the hourly rates paid in (t0, t1], positive when longs
    pay shorts, exactly as for Binance; None for a period that starts before the series."""

    def __init__(self, raw, hl):
        super().__init__(raw)
        for a, rows in hl.items():
            rows = sorted(rows)
            self.ft[a] = [int(r[0]) for r in rows]
            c, acc = [0.0], 0.0
            for r in rows:
                acc += float(r[1])
                c.append(acc)
            self.fcum[a] = c

    def funding(self, a, t0, t1):
        ts = self.ft.get(a)
        if not ts or t0 < ts[0] - H.H_MS:
            return None
        return super().funding(a, t0, t1)


def rate_profile(rows, t0, t1, formula):
    """Settlements in [t0, t1): the share exactly at the formula rate (the premium inside the clamp), above it and
    below it (and below zero), and the funding a short collected a year: the rates summed over the time they cover
    (each settlement pays for the interval since the previous one), so 8-hourly and hourly series annualise alike
    and missing hours count as zero."""
    sel = [r for r in rows if t0 <= r[0] < t1]
    if not sel:
        return None
    xs = [r[1] for r in sel]
    gaps = [b[0] - a[0] for a, b in zip(sel, sel[1:])]
    step = statistics.median(gaps) if gaps else H.H_MS
    span = min(t1, sel[-1][0]) - max(t0, sel[0][0] - step)
    n = float(len(xs))
    return {'n': len(xs), 'share_at_formula': sum(1 for x in xs if abs(x - formula) < 1e-12) / n,
            'share_above': sum(1 for x in xs if x > formula + 1e-12) / n,
            'share_below': sum(1 for x in xs if x < formula - 1e-12) / n,
            'share_negative': sum(1 for x in xs if x < 0) / n,
            'mean_ann': sum(xs) / (span / (365.0 * DAY_MS)) if span > 0 else None}


def hourly_gaps(rows):
    """Missing funding hours in an hourly series (consecutive stamps more than 1.5 h apart), and the largest gap."""
    gaps = [(b[0] - a[0]) / H.H_MS - 1 for a, b in zip(rows, rows[1:]) if b[0] - a[0] > 1.5 * H.H_MS]
    return {'missing_hours': int(round(sum(gaps))), 'gaps': len(gaps), 'largest_hours': max(gaps, default=0)}


def asset_funding(periods, betas, band=None):
    """house_vaults.simulate_hedge's holdings (the same band and drift rules), with the funding split by asset: per
    period {asset: h * f}. Summed over assets it equals simulate_hedge's fund_pnl (tested)."""
    band = H.REBAL_BAND if band is None else band
    held, out = {}, []
    for p, tgt in zip(periods, betas):
        tgt = tgt or {}
        for k in set(held) | set(tgt):
            h, b = held.get(k, 0.0), tgt.get(k, 0.0)
            if b == 0.0 or h == 0.0 or (h > 0) != (b > 0) or abs(h - b) > band * abs(b):
                held[k] = b
        held = {k: v for k, v in held.items() if v != 0.0}
        out.append({k: h * p['f'].get(k, 0.0) for k, h in held.items()})
        g = 1.0 + p['r_v']
        held = {k: h * (1.0 + p['r'].get(k, 0.0)) / g for k, h in held.items()} if g > 0 else {}
    return out


def hl_price_check(book, coins, store=HL_STORE):
    """Daily (00:00 UTC) returns of Hyperliquid's perp against Binance's over the window the store holds Hyperliquid
    closes for: the price-leg difference the study leaves out by pricing both venues' shorts at Binance closes."""
    import gzip
    out = {}
    for a in coins:
        f = store / 'candles_1h' / ('%s.json.gz' % a)
        if not f.exists():
            continue
        with gzip.open(f, 'rt') as fh:
            hl = {int(r['t']) + H.H_MS: float(r['c']) for r in json.load(fh)}        # keyed by bar close
        days = sorted(t for t in hl if t % DAY_MS == 0)
        diffs = []
        for t0, t1 in zip(days, days[1:]):
            b0, b1 = book.price(a, t0), book.price(a, t1)
            if b0 and b1 and t1 - t0 == DAY_MS:
                diffs.append((hl[t1] / hl[t0] - 1) - (b1 / b0 - 1))
        if len(diffs) > 2:
            out[a] = {'days': len(diffs), 'first': H.day_of(days[0]), 'last': H.day_of(days[-1]),
                      'mean_daily_diff_ann': statistics.fmean(diffs) * 365, 'sd_daily_diff': statistics.stdev(diffs)}
    return out


def strip_res(res):
    """The parts of a run_protocol result the study reports."""
    keep = ('chosen', 'in_sample', 'test', 'n_periods', 'plan_sha256_16', 'oos_rank', 'n_variants',
            'deflated_sharpe_in_sample', 'bh_survivors_full_sample', 'static_betas_in_sample', 'last_rolling_betas',
            'decomposition_out')
    out = {k: res.get(k) for k in keep}
    for k in ('chosen_in', 'chosen_out'):
        out[k] = {x: res[k].get(x) for x in ('n', 'days', 'ann_excess', 'nw_t', 'nw_p', 'boot_lo', 'boot_hi', 'sharpe',
                                             'ann_vol', 'max_drawdown', 'worst_week')}
    return out


def venue_study(name, points, assets, comp, entry_exit, books, hl_rows, bn_rows):
    """One vault: the house_vaults protocol on identical periods once per venue, the Binance-chosen variant on both,
    every variant's test half, the funding each venue paid that variant's always-on hedge, and the rate profiles."""
    P = {v: H.attach_legs(H.price_returns(points), b, assets) for v, b in books.items()}
    spans = {v: [(p['t0'], p['t1']) for p in Pv] for v, Pv in P.items()}
    if spans['binance'] != spans['hyperliquid']:
        raise RuntimeError('%s: the venues priced different periods' % name)
    runs = {v: H.run_protocol(name, Pv, assets, comp=comp, entry_exit=entry_exit) for v, Pv in P.items()}
    bn = runs['binance']
    ch = bn['chosen']
    hn = ch.split('|')[0]
    S0 = bn['_series']
    c = S0['c']
    t0, t1 = S0['P'][c]['t0'], S0['P'][-1]['t1']
    out = {'periods': len(S0['P']), 'in_sample': bn['in_sample'], 'test': bn['test'], 'assets': assets,
           'entry_exit': entry_exit, 'venues': {}, 'variants_test': {}}
    for v, res in runs.items():
        S = res['_series']
        nav = H.nav_points(S['P_all'])
        r = strip_res(res)
        r['robustness'] = {'weekly_grid': H.weekly_check(nav, books[v], assets, S['P'][c]['t0']),
                           'daily_roll120': H.weekly_check(nav, books[v], assets, S['P'][c]['t0'], step=1,
                                                           roll_days=120, min_obs=40)}
        for k in ('weekly_grid', 'daily_roll120'):
            if r['robustness'][k]:
                r['robustness'][k] = {x: r['robustness'][k].get(x) for x in ('n', 'days', 'ann_excess', 'nw_t')}
        sh = S['shadows'][hn][c:]
        Pt = S['P'][c:]
        days = sum(p['days'] for p in Pt)
        per_asset = asset_funding(Pt, _betas_of(res, hn)[c:])      # the test half starts flat, as the shadow does
        r['funding_of_bn_chosen_hedge'] = {
            'hedge': hn, 'per_vault_ann': sum(s['fund_pnl'] for s in sh) / days * 365.0,
            'on_capital_ann': sum(s['fund_pnl'] / s['capital'] for s in sh) / days * 365.0,
            'per_asset_per_vault_ann': {a: sum(q.get(a, 0.0) for q in per_asset) / days * 365.0 for a in assets},
            'check_sum_vs_shadow': sum(sum(q.values()) for q in per_asset) - sum(s['fund_pnl'] for s in sh)}
        out['venues'][v] = r
        for k, st in res['variants'].items():
            out['variants_test'].setdefault(k, {})[v] = {'ann_excess': st['out']['ann_excess'], 'nw_t': st['out']['nw_t']}
    vb, vh = out['variants_test'][ch]['binance'], out['variants_test'][ch]['hyperliquid']
    fb, fh = out['venues']['binance']['funding_of_bn_chosen_hedge'], out['venues']['hyperliquid']['funding_of_bn_chosen_hedge']
    out['same_variant'] = {'variant': ch, 'binance': vb, 'hyperliquid': vh,
                           'excess_difference_hl_minus_bn': vh['ann_excess'] - vb['ann_excess'],
                           'funding_difference_on_capital': fh['on_capital_ann'] - fb['on_capital_ann'],
                           'funding_difference_per_vault': fh['per_vault_ann'] - fb['per_vault_ann']}
    out['rate_profile_test'] = {a: {'hyperliquid': rate_profile(hl_rows[a], t0, t1, HL_FLOOR),
                                    'binance': rate_profile(bn_rows[a], t0, t1, BN_FLOOR)} for a in assets}
    yrs = range(H.utc(S0['P_all'][0]['t0']).year, H.utc(t1).year + 1)
    out['rate_profile_by_year'] = {a: {str(y): {'hyperliquid': rate_profile(hl_rows[a], H.day_ts('%d-01-01' % y) * 1000,
                                                                            H.day_ts('%d-01-01' % (y + 1)) * 1000,
                                                                            HL_FLOOR),
                                                'binance': rate_profile(bn_rows[a], H.day_ts('%d-01-01' % y) * 1000,
                                                                        H.day_ts('%d-01-01' % (y + 1)) * 1000,
                                                                        BN_FLOOR)} for y in yrs}
                                   for a in assets}
    return out


def _betas_of(res, hn):
    """The hedge path run_protocol simulated for hedge `hn`, rebuilt over the full period list it returned."""
    S = res['_series']
    P = S['P']
    if hn == 'none':
        return [{}] * len(P)
    if hn == 'static':
        return [res['static_betas_in_sample']] * len(P)
    if hn == 'comp':
        return [res['plan']['comp']] * len(P)
    idx = {id(p): i for i, p in enumerate(S['P_all'])}
    full = H.rolling_betas(S['P_all'], res['plan']['assets'], res['plan']['roll_days'], 7, 20)
    return [full[idx[id(p)]] for p in P]


# ----------------------------------------------------------------------------------------------------------------------
# commands
# ----------------------------------------------------------------------------------------------------------------------
def pct(x, d=2):
    return '—' if x is None else '%+.*f%%' % (d, 100 * x)


def cmd_snapshot(args):
    ledger = Path(args.ledger)
    rows = read_ledger(ledger)
    now = time.time()
    day = H.day_of(now)
    has_daily = any(r.get('day') == day and r.get('kind') == 'daily' for r in rows)
    if has_daily and not args.intraday:
        print('skip: %s already has a daily row in %s (--intraday writes an extra row marked intraday)' % (day, ledger))
        return 0
    kind = 'intraday' if has_daily else 'daily'
    prev = last_daily(rows)
    import perp_rpc as R
    api = R.Info(interval=max(0.4, args.hl_interval))
    errors, ctx = [], {}
    stamp = time.strftime('%H%M%SZ', time.gmtime(now))
    raw_dir = Path(args.raw) / day

    def soft(label, fn):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — recorded in the row; the required parts raise
            errors.append('%s: %s' % (label, str(e)[:200]))
            return None
    fund_info = soft('binance fundingInfo', lambda: {x['symbol']: x for x in H.http_json(H.BINANCE + '/fapi/v1/fundingInfo')
                                                     if x['symbol'] in {m['binance'] for m in ASSETS.values()}}) or {}
    ctx['binance_funding_info'] = fund_info
    # the pool and the hedge marks back to back (both required)
    info = H.http_json(JLP_INFO)
    t_ms = int(time.time() * 1000)
    bn, ctx['binance_premium_index'] = fetch_binance(fund_info)
    hl_pair = soft('hyperliquid metaAndAssetCtxs', lambda: fetch_hl(api))
    hl = hl_pair[0] if hl_pair else None
    ctx['hl_ctxs'] = hl_pair[1] if hl_pair else None
    funding = fetch_funding(prev, t_ms, api, soft) if (kind == 'daily' and prev) else None
    fees = soft('defillama fees', fetch_fees)
    ssr = soft('sUSDS ssr', fetch_ssr)
    if ssr is None:
        ssr = {'apy': H.SSR_NOW, 'source': 'fallback: house_vaults.SSR_NOW (the on-chain read failed)'}
    sup = soft('solana getTokenSupply', fetch_supply)
    dex = soft('jupiter price', fetch_dex)
    usdt = soft('kraken USDT/USD', fetch_usdt_usd)
    ctx.update({'funding': funding, 'fees': fees, 'ssr': ssr, 'supply_onchain': sup, 'dex': dex, 'usdt_usd': usdt,
                'hl_stats': api.stats(), 'http_stats': dict(H.STATS)})
    H.save_json(raw_dir / ('jlp_info_%s.json' % stamp), info)
    H.save_json(raw_dir / ('context_%s.json' % stamp), ctx)
    rel = str(raw_dir.relative_to(ROOT)) if raw_dir.is_relative_to(ROOT) else str(raw_dir)
    row = build_row(info, t_ms, bn, hl, funding, fees, ssr, sup[0] if sup else None, dex, kind, rel, errors, usdt)
    wrote = append_row(ledger, row, intraday=args.intraday)
    print_row(row, rows)
    print('%s row %s for %s (%s)%s' % ('wrote' if wrote else 'skipped', wrote or '', day, ledger,
                                       ('; soft errors: ' + '; '.join(errors)) if errors else ''))
    return 0


def print_row(row, rows):
    first = next((r for r in sorted(rows, key=lambda r: r['t_ms']) if r.get('kind') == 'daily'), row)
    N = FORWARD_RULE['jlp_usd'] / first['jlp']['price']
    an = json.loads(HV_ANALYSIS.read_text()) if HV_ANALYSIS.exists() else {}
    betas = an.get('vaults', {}).get('JLP', {}).get('last_rolling_betas') or {}
    s = snapshot_summary(row, N, None, betas)
    print('%s  JLP %.6f  AUM $%.1fM  supply %.0f (on chain %s)  DEX vs NAV %s  fee yield 30d %s  SSR %s' % (
        row['ts'][:19], s['jlp_price'], s['aum_usd'] / 1e6, s['supply'],
        '—' if s['supply_onchain'] is None else '%.0f' % s['supply_onchain'], pct(s['dex_vs_nav']),
        pct(s['fee_yield_30d']), pct(s['ssr_apy'])))
    for a, x in s['assets'].items():
        print('  %-3s delta %14.4f (%5.2f%% AUM, $%6.1fM)  hedge %12.4f = $%.3fM  ratio %.3f  regression %.3f  '
              'funding Binance %s HL %s  oracle-index %+.1fbp' % (
                  a, x['delta_tokens'], 100 * x['delta_pct_aum'], x['delta_usd'] / 1e6, x['hedge_tokens'],
                  x['hedge_usd'] / 1e6, x['hedge_ratio'], x['regression60_analysis_json'] or float('nan'),
                  pct(x['binance_funding_ann']), pct(x['hl_funding_ann']), x['oracle_vs_binance_index_bp']))
    print('  JLP $%.2fM (%.1f tokens), gross short $%.3fM, capital $%.3fM; checks %s' % (
        s['jlp_value_usd'] / 1e6, N, s['gross_short_usd'] / 1e6, s['capital_usd'] / 1e6,
        json.dumps({k: v for k, v in row['checks'].items() if not isinstance(v, dict)})))


def cmd_score(args):
    ledger = Path(args.ledger)
    rows = read_ledger(ledger)
    res = score_rows(rows, Path(args.hv_raw), Path(args.analysis))
    res = {'generated': dt.datetime.now(dt.timezone.utc).isoformat(), 'ledger': str(ledger.relative_to(ROOT))
           if ledger.is_relative_to(ROOT) else str(ledger), **res}
    out = Path(args.out) if args.out else ledger.with_suffix('.json')
    H.save_json(out, res)
    S = res['summary']
    print('rows: %d daily, %d intraday (%s .. %s)' % (res['rows']['daily'], res['rows']['intraday'],
                                                     res['rows'].get('first'), res['rows'].get('last')))
    L = res.get('latest')
    if L:
        print('latest %s: JLP %.6f, hedge ratios %s (regression %s), gross short $%.3fM on $%.3fM capital' % (
            L['ts'][:16], L['jlp_price'], ' '.join('%s %.3f' % (a, x['hedge_ratio']) for a, x in L['assets'].items()),
            ' '.join('%s %.3f' % (a, x['regression60_now']) for a, x in L['assets'].items()
                     if x['regression60_now'] is not None) or '—',
            L['gross_short_usd'] / 1e6, L['capital_usd'] / 1e6))
    for name, st in (res.get('models') or {}).items():
        if st.get('ann_excess') is not None:
            print('  %-32s excess %s (60-day one-offs %s, before one-offs %s)  t %s  sigma/day %s  n %d' % (
                name, pct(st['ann_excess']), pct(st.get('ann_excess_one_off_60d')), pct(st.get('ann_excess_before_one_off')),
                '—' if st.get('nw_t') is None else '%.2f' % st['nw_t'],
                '—' if st.get('daily_sigma') is None else '%.3f%%' % (100 * st['daily_sigma']), st['n']))
        elif st.get('ann_excess_before_one_off') is not None:
            print('  %-32s excess before one-offs %s  n %d' % (name, pct(st['ann_excess_before_one_off']), st['n']))
    F = res.get('flags') or {}
    print('flags: sigma14 latest %s, fee yield %s, events %s' % (
        pct((F.get('sigma') or {}).get('latest'), 3), pct((F.get('fee_yield') or {}).get('latest')),
        F.get('events') or 'none'))
    print('verdict: %s  -> %s' % (S['verdict'], out))
    return 0


def attribute(J0, J1):
    """How much of the JLP NAV change between two jlp-info states the net delta explains: delta per JLP x the oracle
    move, with the first state's delta (what a hedge set then earns against) and with the mean of the two."""
    act = J1['price'] - J0['price']
    p0 = {a: J0['custodies'][a]['oracle_px'] for a in ASSETS}
    p1 = {a: J1['custodies'][a]['oracle_px'] for a in ASSETS}
    pred0 = sum(J0['delta_per_jlp'][a] * (p1[a] - p0[a]) for a in ASSETS)
    predm = sum(0.5 * (J0['delta_per_jlp'][a] + J1['delta_per_jlp'][a]) * (p1[a] - p0[a]) for a in ASSETS)
    return {'nav_change_rel': act / J0['price'], 'explained_by_delta0_rel': pred0 / J0['price'],
            'explained_by_mean_delta_rel': predm / J0['price'], 'residual_delta0_rel': (act - pred0) / J0['price'],
            'residual_mean_delta_rel': (act - predm) / J0['price'],
            'oracle_moves': {a: p1[a] / p0[a] - 1 for a in ASSETS}}


def cmd_check(args):
    path = Path(args.info)
    info = H.load_json(path)
    at_ms = int(dt.datetime.fromisoformat(args.at).timestamp() * 1000) if args.at else int(path.stat().st_mtime * 1000)
    J = parse_info(info)
    book = H.PriceBook(HV_RAW) if (HV_RAW / 'binance').exists() else None
    an = json.loads(HV_ANALYSIS.read_text()) if HV_ANALYSIS.exists() else {}
    betas = an.get('vaults', {}).get('JLP', {}).get('last_rolling_betas') or {}
    N = FORWARD_RULE['jlp_usd'] / J['price']
    res = {'file': str(path), 'at': H.utc(at_ms).isoformat(), 'nav': J['price'], 'price_field': J['price_field'],
           'aum_usd': J['aum_usd'], 'supply': J['supply'], 'checks': J['checks'], 'jlp_tokens_at_10m': N, 'assets': {}}
    gross = 0.0
    for a in ASSETS:
        c = J['custodies'][a]
        bpx = book.price(a, at_ms) if book else None
        px = c['oracle_px']
        hedge_usd = J['delta_per_jlp'][a] * N * px
        gross += hedge_usd
        res['assets'][a] = {
            'owned': c['owned'], 'locked': c['locked'], 'guaranteed_usd': c['guaranteed_usd'], 'short_usd': c['short_usd'],
            'short_avg': c['short_avg'], 'short_tokens': c['short_tokens'], 'delta_tokens': c['delta_tokens'],
            'oracle_px_from_aum': px, 'oracle_px_from_short_pnl': c['oracle_px_short'],
            'identity_resid_usd': c['identity_resid_usd'], 'binance_close_before': bpx,
            'oracle_vs_binance_close_bp': (1e4 * (px / bpx - 1)) if bpx else None,
            'delta_usd': c['delta_tokens'] * px, 'delta_pct_aum': c['delta_tokens'] * px / J['aum_usd'],
            'long_claim_usd': c['long_claim_usd'], 'hedge_tokens_at_10m': J['delta_per_jlp'][a] * N,
            'hedge_usd_at_10m': hedge_usd, 'hedge_ratio': J['delta_per_jlp'][a] * px / J['price'],
            'regression60_last': betas.get(a), 'target_weight': c['target_pct'] / 100.0,
            'naive_owned_ratio': c['owned'] * px / J['aum_usd']}
    res['gross_hedge_ratio'] = gross / FORWARD_RULE['jlp_usd']
    res['regression60_gross'] = sum(betas.values()) if betas else None
    if args.next:
        J1 = parse_info(H.load_json(args.next))
        res['next'] = {'file': args.next, 'attribution': attribute(J, J1)}
    out = Path(args.out) if args.out else STUDY / ('precheck_%s.json' % path.stem)
    H.save_json(out, res)
    print('%s at %s: NAV %.7f (field %.6f), AUM $%.2fM, supply %.2f; checks %s' % (
        path.name, res['at'][:19], J['price'], J['price_field'], J['aum_usd'] / 1e6, J['supply'], json.dumps(J['checks'])))
    for a, x in res['assets'].items():
        print('  %-3s owned %.4f - locked %.4f + shorts %.4f = delta %.4f ($%.1fM, %.2f%% AUM; owned alone %.2f%%)'
              '  px %.5f / %.5f (resid $%.2f)  vs Binance close %s  ratio %.4f  regression %.4f  target %.2f' % (
                  a, x['owned'], x['locked'], x['short_tokens'], x['delta_tokens'], x['delta_usd'] / 1e6,
                  100 * x['delta_pct_aum'], 100 * x['naive_owned_ratio'], x['oracle_px_from_aum'],
                  x['oracle_px_from_short_pnl'] or float('nan'), x['identity_resid_usd'] or 0.0,
                  '—' if x['oracle_vs_binance_close_bp'] is None else '%+.1fbp' % x['oracle_vs_binance_close_bp'],
                  x['hedge_ratio'], x['regression60_last'] or float('nan'), x['target_weight']))
    print('  gross hedge ratio %.4f (regression %.4f); at $10M: %s' % (
        res['gross_hedge_ratio'], res['regression60_gross'] or float('nan'),
        ', '.join('%s %.4f = $%.3fM' % (a, x['hedge_tokens_at_10m'], x['hedge_usd_at_10m'] / 1e6)
                  for a, x in res['assets'].items())))
    if args.next:
        at = res['next']['attribution']
        print('  attribution to %s: NAV %s, delta then %s, mean delta %s, residual %s / %s; oracle moves %s' % (
            Path(args.next).name, pct(at['nav_change_rel'], 4), pct(at['explained_by_delta0_rel'], 4),
            pct(at['explained_by_mean_delta_rel'], 4), pct(at['residual_delta0_rel'], 4),
            pct(at['residual_mean_delta_rel'], 4), {a: round(100 * v, 3) for a, v in at['oracle_moves'].items()}))
    print('wrote', out)
    return 0


def cmd_hl_hedge(args):
    """The JLP and GM SOL-USDC backtests with the shorts on Hyperliquid, beside Binance, written to hl_hedge.json."""
    got = collect_hl_funding(interval=args.interval) if not args.no_collect else None
    if args.collect_only:
        return 0
    raw = HV_RAW
    hl_rows = {a: H.load_json(HL_HISTORY / ('funding_%s.json.gz' % a)) for a in ASSETS}
    bn_rows = {a: [[int(r['t']), float(r['rate'])] for r in H.load_json(raw / 'binance' / ('funding_%sUSDT.json.gz' % a))]
               for a in ASSETS}
    data = {}
    for a, rows in hl_rows.items():
        # Hyperliquid settled every 8 hours at first (those rows carry 8-hour rates); hourly from the first 1h step
        k = next(i for i, (x, y) in enumerate(zip(rows, rows[1:])) if y[0] - x[0] < 1.5 * H.H_MS)
        d = {'rows': len(rows), 'first': H.utc(rows[0][0]).isoformat(), 'last': H.utc(rows[-1][0]).isoformat(),
             'hourly_from': H.utc(rows[k][0]).isoformat(), 'eight_hourly_rows_before': k,
             'gaps_after_hourly_start': hourly_gaps(rows[k:])}
        sf = HL_STORE / 'funding' / ('%s.json.gz' % a)
        if sf.exists():   # an independent copy: perp_history's store over its own window
            mine = {int((r[0] + H.H_MS // 2) // H.H_MS): r[1] for r in rows}
            theirs = {int((int(x['time']) + H.H_MS // 2) // H.H_MS): float(x['fundingRate']) for x in H.load_json(sf)}
            both = sorted(set(mine) & set(theirs))
            d['store_check'] = {'store': str(sf.relative_to(ROOT)), 'overlap_hours': len(both),
                                'store_hours_missing_here': len(set(theirs) - set(mine)),
                                'max_abs_rate_diff': max((abs(mine[h] - theirs[h]) for h in both), default=None)}
        data[a] = d
    books = {'binance': H.PriceBook(raw), 'hyperliquid': HLBook(raw, hl_rows)}
    j = H.load_jlp(raw)
    comp = {}
    for cst in (j['info'] or {}).get('custodies', []):
        sym = {'SOL': 'SOL', 'ETH': 'ETH', 'WBTC': 'BTC'}.get(cst['symbol'])
        if sym:
            comp[sym] = float(cst['targetWeightagePct']) / 100.0
    g = H.load_gmx(raw, 'GM_SOL-USDC')
    an = json.loads(HV_ANALYSIS.read_text())['vaults']
    vaults = {}
    for name, points, assets, cp, ee in (('JLP', j['points'], ['SOL', 'ETH', 'BTC'], comp, H.ENTRY_EXIT['JLP']),
                                         ('GM_SOL-USDC', g['points'], ['SOL'], None, H.ENTRY_EXIT['GM'])):
        t = time.time()
        v = venue_study(name, points, assets, cp, ee, books, hl_rows, bn_rows)
        a0 = an[name]
        v['replicates_house_vaults'] = {
            'chosen_here': v['venues']['binance']['chosen'], 'chosen_analysis_json': a0['chosen'],
            'test_excess_here': v['venues']['binance']['chosen_out']['ann_excess'],
            'test_excess_analysis_json': a0['chosen_out']['ann_excess'],
            'plan_hash_here': v['venues']['binance']['plan_sha256_16'], 'plan_hash_analysis_json': a0['plan_sha256_16']}
        v['seconds'] = round(time.time() - t, 1)
        vaults[name] = v
        sv = v['same_variant']
        print('%-12s %s: Binance %s (t %.2f) | Hyperliquid %s (t %.2f) | funding on capital %+.2f%% a year; HL chose %s '
              'at %s (t %.2f)' % (name, sv['variant'], pct(sv['binance']['ann_excess']), sv['binance']['nw_t'],
                                  pct(sv['hyperliquid']['ann_excess']), sv['hyperliquid']['nw_t'],
                                  100 * sv['funding_difference_on_capital'], v['venues']['hyperliquid']['chosen'],
                                  pct(v['venues']['hyperliquid']['chosen_out']['ann_excess']),
                                  v['venues']['hyperliquid']['chosen_out']['nw_t']), flush=True)
    res = {'generated': dt.datetime.now(dt.timezone.utc).isoformat(),
           'question': 'house_vaults\' hedged JLP and GM SOL-USDC backtests with the shorts on Hyperliquid instead of '
                       'Binance: excess by venue, the funding difference, and how often funding sat at the formula rate',
           'method': ['house_vaults.run_protocol unchanged (pre-committed variants, chosen by first-half Sharpe, tested '
                      'once on the second half), on identical periods for both venues',
                      'the only input that changes is funding: Hyperliquid\'s hourly fundingHistory summed over each '
                      'period in place of Binance\'s 8-hourly settlements (same sign: positive pays the short)',
                      'both venues\' shorts are priced at Binance\'s hourly closes; price_leg_check measures the HL-vs-'
                      'Binance daily return difference over the window the repo holds Hyperliquid closes for',
                      'costs unchanged (5bp a hedge trade, 10% band, one-third margin, vault round trips); '
                      'Hyperliquid\'s tier-0 taker is 4.5bp, so this slightly understates the Hyperliquid side',
                      'margin: Binance USDT-M posts USDT, Hyperliquid posts USDC; the difference is noted, not modelled',
                      'formula rate: Hyperliquid pays 0.00125%/h (0.01% per 8h) whenever the premium sits inside the '
                      'clamp; rates go above it and below it (down to negative) when the premium leaves the clamp'],
           'hl_funding_data': data, 'collect': got, 'price_leg_check': hl_price_check(books['binance'], list(ASSETS)),
           'vaults': vaults,
           'notes': ['Hyperliquid funding: public fundingHistory, collected into %s; identical to perp_history\'s store '
                     'over every hour they share (store_check)' % HL_HISTORY.relative_to(ROOT),
                     'Hyperliquid settled every 8 hours until hourly settlement began (hourly_from, 2023-06-08); both '
                     'vault histories start later (GM SOL-USDC 2023-07-05, JLP 2023-11-22), and the by-year profiles '
                     'annualise by covered time, so the 8-hour rows count correctly there',
                     'for the same always-on variant, the venues differ only in funding: the excess difference equals '
                     'the funding difference on capital (same_variant)',
                     'rate profiles: share_at_formula is the share of settlements exactly at 0.00125%/h (Hyperliquid) '
                     'or 0.01%/8h (Binance), the rate paid while the premium sits inside the clamp; it is not a floor '
                     '(rates fall below it, to negative, when the perp trades at a discount beyond the clamp)']}
    out = Path(args.out) if args.out else STUDY / 'hl_hedge.json'
    H.save_json(out, res)
    print('wrote', out)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    hh = sub.add_parser('hl-hedge', help='house_vaults\' JLP and GM SOL hedges re-run with the shorts on Hyperliquid')
    hh.add_argument('--interval', type=float, default=3.0, help='seconds between Hyperliquid info calls (>= 0.4)')
    hh.add_argument('--no-collect', action='store_true', help='use the cached funding history as it is')
    hh.add_argument('--collect-only', action='store_true')
    hh.add_argument('--out', default=None)
    s = sub.add_parser('snapshot', help='append today\'s row (skipped if the UTC day has one, unless --intraday)')
    s.add_argument('--ledger', default=str(LEDGER))
    s.add_argument('--raw', default=str(STUDY / 'raw'))
    s.add_argument('--intraday', action='store_true', help='write an extra row marked intraday (never scored)')
    s.add_argument('--hl-interval', type=float, default=0.4)
    c = sub.add_parser('score', help='replay the frozen rule over the ledger and write its .json sibling')
    c.add_argument('--ledger', default=str(LEDGER))
    c.add_argument('--out', default=None)
    c.add_argument('--hv-raw', default=str(HV_RAW))
    c.add_argument('--analysis', default=str(HV_ANALYSIS))
    k = sub.add_parser('check', help='the arithmetic on a saved jlp-info file (no ledger write)')
    k.add_argument('--info', required=True)
    k.add_argument('--next', default=None, help='a later jlp-info file: attribute the NAV move to the net delta')
    k.add_argument('--at', default=None, help='ISO time the file was fetched (default: its mtime)')
    k.add_argument('--out', default=None)
    args = ap.parse_args(argv)
    return {'snapshot': cmd_snapshot, 'score': cmd_score, 'check': cmd_check, 'hl-hedge': cmd_hl_hedge}[args.cmd](args)


if __name__ == '__main__':
    raise SystemExit(main())
