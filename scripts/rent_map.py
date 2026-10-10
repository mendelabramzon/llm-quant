#!/usr/bin/env python3
"""Rent map: where the money paid by agents with a non-price motive flows, how large each pool is, who collects it
today, and which pools patient capital (no speed, no block position) could still take a share of.

Why. Twenty-five history-tested studies in this repo say the same thing: what survives is a rent paid by someone with a
non-price motive (leverage demand on one venue, impatience in a redemption queue, points speculation, marketing
budgets, entertainment), collected by whoever supplies the scarce resource that payer needs (patience or locked capital,
venue-specific capital, tail-risk tolerance, access, attention). Information signals were priced. This is the top-down
census of those rents, in USD a year at the current run-rate, so the loop knows where to look next and how wide each
family can ever be.

Pools (each sized in `analyze`, every number in `analysis.json`, `render` prints `tables.md`):

  1. perp funding paid by longs, and the part above a fair rate (the savings rate, 3.80%): Hyperliquid (main dex and
     HIP-3 builder dexes), Binance USDⓈ-M (top ~100 by open interest), Bybit and OKX (top 30 each);
  2. perp-venue LP vault income (fees and supply-side revenue of the perp venues, DefiLlama);
  3. incentive budgets: sum of tvlUsd x apyReward over DefiLlama's yield pools (and Merkl's own campaign budgets);
  4. DEX LP fees (supply side), with an LVR estimate on the main volatile pairs;
  5. lending: interest paid by borrowers, by asset class (Aave's and Morpho's own APIs), the share above a fair rate;
  6. queue impatience: LST/LRT discounts x secondary sell volume (this repo's measured histories);
  7. points speculation: Pendle YT implied-minus-realised yield x YT outstanding (on chain), and Pendle's fees;
  8. for scale only (inaccessible or racing): stablecoin issuers, chain fees and MEV, launchpads and other
     entertainment platforms, manager fees.

Conventions. Rates are decimals per year unless named `_bp` or `_h` (per hour). Funding is positive when longs pay
shorts. A run-rate is a window's flow scaled by 365/days. "Above fair" is the flow minus what the same notional would
earn at the fair rate (SSR for dollars; the staking yield for ETH; zero for BTC and other coins); `_clipped` sums only
the positive per-coin (or per-reserve) parts, which is what a collector who chooses where to stand can reach.

    python3 scripts/rent_map.py collect --out research/2026-10-10/rent_map            # all parts, cached
    python3 scripts/rent_map.py collect --out research/2026-10-10/rent_map --parts hl,llama
    python3 scripts/rent_map.py analyze --out research/2026-10-10/rent_map
    python3 scripts/rent_map.py render  --out research/2026-10-10/rent_map

Network etiquette (other workers share this IP): at most 2 requests a second to DefiLlama and Hyperliquid (0.6 s and
2.0 s spacing here), Binance's funding endpoint at 1.2 s (its 500 / 5 min budget is per IP), everything cached gzip
under `<out>/raw/` and never fetched twice unless `--refresh`.
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
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
SSR = 0.038                 # Sky savings rate on chain, 2026-10-09: the fair rate for dollars, and the book's benchmark
ETH_FAIR = 0.0237           # Lido staking APR over the 210-day redemption window (redemption_history benchmarks)
HOURS_PER_YEAR = 8760.0

LLAMA = 'https://api.llama.fi'
YIELDS = 'https://yields.llama.fi'
STABLES = 'https://stablecoins.llama.fi'
HL_INFO = 'https://api.hyperliquid.xyz/info'
HLP_VAULT = '0xdfc24b077bc1425ad1dea75bcb6f8158e10df303'
BN_FAPI = 'https://fapi.binance.com'
BN_SPOT = 'https://api.binance.com'
BYBIT = 'https://api.bybit.com'
OKX = 'https://www.okx.com'
AAVE_API = 'https://api.v3.aave.com/graphql'
MORPHO_API = 'https://blue-api.morpho.org/graphql'
MERKL = 'https://api.merkl.xyz/v4'

FUNDING_STORE = ROOT / 'research/2026-10-09/perps_history/funding'
SNAP_DIRS = [ROOT / 'research/2026-09-08/perps_1h/snap', ROOT / 'research/2026-09-10/perps_daily/snap',
             ROOT / 'research/2026-10-09/perps_daily/snap']
PENDLE_DIR = ROOT / 'research/2026-10-09/pendle_history'
REDEMPTION = ROOT / 'research/2026-10-09/redemption_history/analysis.json'
QUEUE_EXT = ROOT / 'research/2026-10-10/queue_bids_ext/analysis.json'
TERM_CARRY = ROOT / 'research/2026-10-10/term_carry/analysis.json'
REGISTRY = ROOT / 'scripts/chain_registry.json'

FEE_TYPES = ('dailyFees', 'dailyRevenue', 'dailySupplySideRevenue', 'dailyHoldersRevenue', 'dailyBribesRevenue')
SUMMARY_TYPES = ('dailyFees', 'dailyRevenue', 'dailySupplySideRevenue')


# ---------------------------------------------------------------------------------------------- small helpers

def utc(ms=None):
    t = dt.datetime.now(UTC) if ms is None else dt.datetime.fromtimestamp(ms / 1000, UTC)
    return t.strftime('%Y-%m-%dT%H:%M:%SZ')


def write_gz(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, 'wt') as f:
        json.dump(obj, f)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + '\n')


def fnum(v, d=None):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if math.isfinite(x) else d


def failed(v):
    return v is None or (isinstance(v, dict) and '_failed' in v)


# ---------------------------------------------------------------------------------------------- core arithmetic

def annualise(total, days):
    """A flow observed over `days` days, as a year at the same rate (simple, 365 days)."""
    if not days or days <= 0:
        raise ValueError('days must be positive')
    return total * 365.0 / days


def apy_to_apr(apy):
    """Per-second compounding (Aave, Morpho): APY = e^APR - 1, so the simple run-rate of interest is ln(1 + APY)."""
    return math.log1p(apy) if apy is not None and apy > -1 else None


def flow_split(notional, rate, fair):
    """Split a year's flow on `notional` at `rate` against a `fair` rate. Positive `rate` is paid by the payer side.
    gross: notional x rate; fair_part: what a fair rate explains (never more than the flow itself, never negative);
    above_fair: notional x (rate - fair), signed; above_fair_clipped: its positive part."""
    gross = notional * rate
    fair_part = notional * max(0.0, min(rate, fair)) if fair >= 0 else 0.0
    above = notional * (rate - fair)
    return {'gross': gross, 'fair_part': fair_part, 'above_fair': above, 'above_fair_clipped': max(0.0, above)}


def window_stats(series, t_end, days):
    """Settled rates in (t_end - days, t_end]: count, sum, sum of positive and negative parts, share positive.
    `series` is [(t_ms, rate)] sorted or not. Sums are per settlement, so `sum * 365 / days` is an annual rate whatever
    the settlement interval (1h on Hyperliquid, 1/4/8h on the exchanges)."""
    t0 = t_end - days * DAY_MS
    xs = [r for t, r in series if t0 < t <= t_end]
    pos = sum(r for r in xs if r > 0)
    neg = sum(r for r in xs if r < 0)
    return {'n': len(xs), 'sum': sum(xs), 'sum_pos': pos, 'sum_neg': neg,
            'share_pos': (sum(1 for r in xs if r > 0) / len(xs)) if xs else None,
            'ann': sum(xs) * 365.0 / days, 'ann_pos': pos * 365.0 / days, 'ann_neg': neg * 365.0 / days}


def coverage_ok(stats, days, per_day, min_frac=0.8):
    """Whether a window holds at least `min_frac` of the settlements it should (a coin listed mid-window does not)."""
    return stats['n'] >= min_frac * days * per_day


def interp(points, t):
    """Linear interpolation over [(t, v)] with flat extrapolation; None when empty."""
    if not points:
        return None
    pts = sorted(points)
    if t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 if t2 == t1 else v1 + (v2 - v1) * (t - t1) / (t2 - t1)
    return pts[-1][1]


def realised_flow(rates, oi_points, t0, t1):
    """Sum over settlements in (t0, t1] of OI(t) x rate(t): the dollars that actually changed hands, with OI
    interpolated between snapshots. Positive = longs paid."""
    tot = pos = neg = 0.0
    n = 0
    for t, r in rates:
        if t0 < t <= t1:
            oi = interp(oi_points, t) or 0.0
            tot += oi * r
            pos += oi * r if r > 0 else 0.0
            neg += oi * r if r < 0 else 0.0
            n += 1
    return {'n': n, 'net': tot, 'longs_paid': pos, 'shorts_paid': -neg}


def sigma_annual(closes):
    """Annualised volatility of daily log returns (365 trading days: crypto trades every day)."""
    rs = [math.log(b / a) for a, b in zip(closes, closes[1:]) if a and b and a > 0 and b > 0]
    if len(rs) < 10:
        return None
    return statistics.pstdev(rs) * math.sqrt(365.0)


def lvr_rate(sigma):
    """Loss-versus-rebalancing of a full-range constant-product pool, per year, as a fraction of pool value: sigma^2/8
    (Milionis, Moallemi, Roughgarden, Zhang 2022)."""
    return sigma * sigma / 8.0


def lvr_rate_concentrated(sigma, range_ratio):
    """The same for a Uniswap-v3 position centred (geometrically) in [pa, pb] with pb/pa = range_ratio: the full-range
    rate times 1 / (1 - range_ratio^(-1/4)). A 4x range (half to double) is 3.4x the full-range LVR."""
    if range_ratio <= 1:
        raise ValueError('range_ratio must exceed 1')
    return lvr_rate(sigma) / (1.0 - range_ratio ** -0.25)


def queue_rent(sell_usd, vw_discount_bp, fee_bp, wait_days, fair, days):
    """Impatience rent from DEX sales of a queued claim below its redemption value, per year.
    gross: what sellers gave up against NAV (sell volume x volume-weighted discount);
    above_fair: after the pool's swap fee (LP income, counted in DEX fees) and the time value of waiting in the queue at
    the fair rate (a buyer who redeems is owed that much) -- the part that is a rent, not a price of time."""
    fair_bp = fair * wait_days / 365.0 * 1e4
    gross = sell_usd * vw_discount_bp / 1e4
    above = sell_usd * max(0.0, vw_discount_bp - (fee_bp or 0.0) - fair_bp) / 1e4
    return {'gross': annualise(gross, days), 'above_fair': annualise(above, days), 'fair_bp': fair_bp}


def yt_premium(notional_usd, implied, realised):
    """What YT holders pay PT holders a year for the points and the option on the rate: notional x (implied - realised
    underlying yield). Negative when the floating yield runs above the implied rate (YT buyers then earn)."""
    return notional_usd * (implied - realised)


# ---------------------------------------------------------------------------------------------- classification

HIP3_ENERGY = {'CL', 'BRENTOIL', 'NATGAS', 'WTI', 'BRENT', 'OIL', 'GASOLINE', 'HEATOIL', 'USOIL', 'UKOIL'}
HIP3_METALS = {'GOLD', 'SILVER', 'COPPER', 'PLATINUM', 'PALLADIUM', 'ALUMINIUM', 'ALUMINUM', 'XAU', 'XAG', 'NICKEL',
               'URANIUM', 'ZINC', 'LITHIUM'}
HIP3_AGRI = {'CORN', 'WHEAT', 'SOYBEAN', 'SOYBEANS', 'COFFEE', 'SUGAR', 'COCOA', 'CATTLE', 'COTTON'}
HIP3_FX = {'EUR', 'GBP', 'JPY', 'KRW', 'CHF', 'AUD', 'CAD', 'CNH', 'DXY', 'MXN', 'INR', 'BRL', 'TRY'}
HIP3_RATES = {'10Y', '2Y', '30Y', '5Y', 'USBOND', 'TLT', 'BUND'}
HIP3_INDEX = {'US500', 'USTECH', 'SMALL2000', 'SPX', 'NDX', 'SP500', 'NASDAQ', 'DOW', 'US30', 'JP225', 'HK50', 'DAX',
              'SMH', 'IGV', 'EWY', 'XYZ100', 'MAG7', 'SEMIS', 'BVIV', 'BTCD', 'OTHERS', 'VIX'}


def classify_hip3(name, crypto_names=()):
    """Asset class of a HIP-3 market from its name ('xyz:CL' or 'CL'). Energy and agricultural futures-referenced
    markets fund the roll of their oracle (roll_carry.py: funding pays 0.89-0.97 of each GSCI step), so their funding
    is a calendar price, not a rent."""
    base = name.split(':', 1)[-1].upper()
    if base in HIP3_ENERGY:
        return 'energy'
    if base in HIP3_AGRI:
        return 'agri'
    if base in HIP3_METALS:
        return 'metal'
    if base in HIP3_FX:
        return 'fx'
    if base in HIP3_RATES:
        return 'rates'
    if base in HIP3_INDEX:
        return 'index'
    if base in {c.upper() for c in crypto_names}:
        return 'crypto'
    return 'equity'


ROLL_CLASSES = {'energy', 'agri'}

STABLE_SYMS = {'USDC', 'USDT', 'DAI', 'USDS', 'USDE', 'FRAX', 'LUSD', 'GHO', 'PYUSD', 'USDT0', 'USD0', 'FDUSD',
               'RLUSD', 'USDTB', 'USDG', 'USD1', 'CRVUSD', 'EURC', 'EURE', 'USDC.E', 'USDBC', 'BOLD', 'MIM', 'TUSD',
               'USDA', 'DEUSD', 'SUSDE', 'SUSDS', 'SDAI', 'USDX', 'AUSD', 'USDH', 'FRXUSD', 'SFRXUSD', 'USDHL', 'USR',
               'MUSD', 'USDF', 'SRUSD', 'EUSD', 'USDM', 'USDO', 'XUSD', 'DOLA', 'USDN', 'GUSD', 'USDP', 'BUSD', 'USDD',
               'USDAI', 'USN', 'AVUSD', 'SAVUSD', 'APXUSD', 'REUSD', 'SYRUPUSDC', 'SYRUPUSDT', 'USDT.E', 'USDC.B',
               'USDS.E', 'USD₮0', 'USD₮', 'USDE.E', 'WUSDM', 'SUSDA', 'USDQ', 'HYUSD', 'FEUSD', 'KUSD', 'YUSD', 'NUSD'}
ETH_SYMS = {'ETH', 'WETH', 'STETH', 'WSTETH', 'WEETH', 'EETH', 'RETH', 'CBETH', 'RSETH', 'EZETH', 'METH', 'OSETH',
            'ETHX', 'SFRXETH', 'FRXETH', 'OETH', 'WOETH', 'PUFETH', 'SWETH', 'RSWETH', 'ANKRETH', 'CMETH', 'TETH',
            'WRSETH', 'EBETH', 'WEETHS', 'LSETH', 'ETH+', 'SUPEROETHB', 'WSUPEROETHB', 'BETH', 'WBETH', 'HETH'}
BTC_SYMS = {'BTC', 'WBTC', 'CBBTC', 'TBTC', 'LBTC', 'BTCB', 'SOLVBTC', 'XSOLVBTC', 'FBTC', 'KBTC', 'UNIBTC',
            'EBTC', 'PUMPBTC', 'BTC.B', 'SBTC', 'UBTC', 'CLBTC', 'ENZOBTC', 'STBTC', 'XBTC', 'IBTC', 'BBTC', 'HBTC',
            'MBTC', 'WBTC.E', 'TACBTC', 'CIRBTC', 'LBTCV', 'BTCN', 'OBTC'}


def asset_class(symbol):
    """'stable', 'eth', 'btc' or 'other' for a token symbol (wrapped and staked variants included)."""
    s = (symbol or '').upper().replace('-', '').replace(' ', '')
    if s in STABLE_SYMS or (s.startswith('USD') and len(s) <= 6) or s.endswith('USD') and len(s) <= 7:
        return 'stable'
    if s in ETH_SYMS or (s.endswith('ETH') and len(s) <= 8):
        return 'eth'
    if s in BTC_SYMS or (s.endswith('BTC') and len(s) <= 8):
        return 'btc'
    return 'other'


def fair_rate(cls):
    """The defensible fair rate a lender of each class forgoes: the savings rate for dollars, the staking yield for ETH,
    nothing for BTC and other coins (they earn no native yield)."""
    return {'stable': SSR, 'eth': ETH_FAIR}.get(cls, 0.0)


# One pool per DefiLlama protocol: overrides by slug first, then by category. A protocol that lands in two pools would
# be counted twice in the census total; `assign_pools` refuses that.
SLUG_POOL = {
    'pendle': 'points', 'pendle-v2': 'points', 'boros': 'points',
    'ethena-usde': 'collector', 'ethena': 'collector', 'ethena-usdtb': 'scale_stable',
    'hyperliquid-hlp': 'perp_vaults',
    # USD1's reserve yield (Fidelity money funds) filed under Lending: issuer income, not borrower interest
    'world-liberty-financial': 'scale_stable',
    # memecoin trading apps filed under Interface
    'pump.fun-mobile-app': 'entertainment', 'bankr': 'entertainment',
}
CATEGORY_POOL = {
    'Derivatives': 'perp_vaults', 'Interface': 'perp_vaults', 'Options': 'perp_vaults', 'Options Vault': 'perp_vaults',
    'Synthetics': 'perp_vaults',
    'Dexs': 'dex_lp',
    'Lending': 'lending', 'CDP': 'lending', 'Uncollateralized Lending': 'lending', 'NFT Lending': 'lending',
    'Basis Trading': 'collector',
    'Stablecoin Issuer': 'scale_stable', 'RWA': 'scale_rwa',
    'Chain': 'scale_chain', 'MEV': 'scale_mev', 'Block Builders': 'scale_mev',
    'Liquid Staking': 'scale_staking', 'Liquid Restaking': 'scale_staking', 'Staking Pool': 'scale_staking',
    'Restaking': 'scale_staking',
    'Launchpad': 'entertainment', 'Trading App': 'entertainment', 'Telegram Bot': 'entertainment',
    'Prediction Market': 'entertainment', 'Luck Games': 'entertainment', 'Gamified Mining': 'entertainment',
    'Physical TCG': 'entertainment', 'NFT Marketplace': 'entertainment', 'Gaming': 'entertainment',
    'SoFi': 'entertainment', 'Memes': 'entertainment',
    'Onchain Capital Allocator': 'attention', 'Risk Curators': 'attention', 'Yield': 'attention',
    'Yield Aggregator': 'attention', 'Liquidity Manager': 'attention', 'Liquidity Automation': 'attention',
    'Indexes': 'attention', 'Leveraged Farming': 'attention', 'NFT Automated Strategies': 'attention',
    'Managed Vaults': 'attention',
}


def pool_of(protocol):
    slug = protocol.get('slug') or ''
    if slug in SLUG_POOL:
        return SLUG_POOL[slug]
    if protocol.get('category') == 'Interface':
        # front-ends that route perp orders (Hyperliquid builder codes, HIP-3 deployers) collect from the same leveraged
        # traders as the venue; other interfaces are trading apps
        perp = 'perp' in (protocol.get('name') or '').lower() or 'Hyperliquid L1' in (protocol.get('chains') or [])
        return 'perp_vaults' if perp else 'entertainment'
    return CATEGORY_POOL.get(protocol.get('category'))


def assign_pools(protocols):
    """{slug: pool} for every overview row; raises if a slug appears twice with different pools (a double count)."""
    out = {}
    for p in protocols:
        slug = p.get('slug') or p.get('name')
        pool = pool_of(p)
        if slug in out and out[slug] != pool:
            raise ValueError('protocol %s assigned to two pools: %s and %s' % (slug, out[slug], pool))
        out[slug] = pool
    return out


# Yield-pool categories whose reward APY is passed through from an underlying pool (a vault of a farm): counting
# them beside the underlying would count one budget twice.
PASS_THROUGH = {'Yield Aggregator', 'Yield', 'Liquidity Manager', 'Leveraged Farming', 'Liquidity Automation',
                'Onchain Capital Allocator', 'Risk Curators', 'Indexes', 'NFT Automated Strategies',
                'Managed Vaults', 'Farm'}


def incentive_budget(pools, categories, cap_apy=300.0, min_tvl=10_000.0):
    """Annual incentive budget = sum of tvlUsd x apyReward/100 over DefiLlama yield pools, with three guards: pools that
    DefiLlama flags as outliers, pools whose reward APY exceeds `cap_apy`% (a mispriced reward token or a dust pool),
    and pools in pass-through categories (counted separately, never in the headline)."""
    tot = {'headline': 0.0, 'pass_through': 0.0, 'outlier_flagged': 0.0, 'over_cap': 0.0, 'tiny': 0.0}
    rows = []
    for p in pools:
        apy_r = fnum(p.get('apyReward'), 0.0) or 0.0
        tvl = fnum(p.get('tvlUsd'), 0.0) or 0.0
        if apy_r <= 0 or tvl <= 0:
            continue
        b = tvl * apy_r / 100.0
        cat = categories.get(p.get('project'), 'unknown')
        if tvl < min_tvl:
            tot['tiny'] += b
            continue
        if p.get('outlier'):
            tot['outlier_flagged'] += b
            continue
        if apy_r > cap_apy:
            tot['over_cap'] += b
            continue
        if cat in PASS_THROUGH:
            tot['pass_through'] += b
            continue
        tot['headline'] += b
        rows.append({'project': p.get('project'), 'chain': p.get('chain'), 'symbol': p.get('symbol'), 'tvl': tvl,
                     'apy_reward': apy_r, 'apy_base': fnum(p.get('apyBase'), 0.0), 'budget': b,
                     'stable': bool(p.get('stablecoin')), 'exposure': p.get('exposure'), 'category': cat,
                     'pool': p.get('pool')})
    return tot, rows


# ---------------------------------------------------------------------------------------------- parsers

def parse_hl_ctxs(payload, dex=''):
    """metaAndAssetCtxs -> [{coin, dex, oi_coins, px, oi_usd, funding_h, vlm_usd, delisted}]. HIP-3 names come back
    prefixed ('xyz:CL'); main-dex names bare. Open interest is one side (longs = shorts)."""
    if failed(payload) or not isinstance(payload, list) or len(payload) < 2:
        return []
    meta, ctxs = payload[0], payload[1]
    out = []
    for m, c in zip(meta.get('universe') or [], ctxs or []):
        if not c:
            continue
        px = fnum(c.get('markPx')) or fnum(c.get('oraclePx')) or 0.0
        oi = fnum(c.get('openInterest'), 0.0)
        out.append({'coin': m.get('name'), 'dex': dex, 'oi_coins': oi, 'px': px, 'oi_usd': oi * px,
                    'funding_h': fnum(c.get('funding'), 0.0), 'vlm_usd': fnum(c.get('dayNtlVlm'), 0.0),
                    'delisted': bool(m.get('isDelisted'))})
    return out


def store_key(coin):
    """Hyperliquid name -> funding-store file stem ('xyz:CL' -> 'xyz__CL')."""
    return coin.replace(':', '__')


def parse_store(rows):
    return sorted((int(r['time']), float(r['fundingRate'])) for r in rows or [] if r.get('fundingRate') is not None)


def parse_bn_funding(rows):
    return sorted((int(r['fundingTime']), float(r['fundingRate'])) for r in rows or []
                  if isinstance(r, dict) and r.get('fundingRate') not in (None, ''))


def parse_bn_oi_hist(rows):
    """openInterestHist -> [(t_ms, oi_usd)] (sumOpenInterestValue is in the quote asset)."""
    return sorted((int(r['timestamp']), float(r['sumOpenInterestValue'])) for r in rows or []
                  if isinstance(r, dict) and r.get('sumOpenInterestValue') not in (None, ''))


def parse_bybit_funding(payload):
    lst = ((payload or {}).get('result') or {}).get('list') or []
    return sorted((int(r['fundingRateTimestamp']), float(r['fundingRate'])) for r in lst if r.get('fundingRate'))


def parse_okx_funding(payload):
    lst = (payload or {}).get('data') or []
    out = []
    for r in lst:
        rate = fnum(r.get('realizedRate'))
        if rate is None:
            rate = fnum(r.get('fundingRate'))
        if rate is not None:
            out.append((int(r['fundingTime']), rate))
    return sorted(out)


def overview_rows(payload):
    """DefiLlama /overview/* -> [{slug, name, category, chains, total24h, total7d, total30d, total1y, parent,
    breakdown30d}] (zero-total rows dropped)."""
    if failed(payload):
        return []
    out = []
    for p in payload.get('protocols') or []:
        t30 = fnum(p.get('total30d'), 0.0) or 0.0
        t24 = fnum(p.get('total24h'), 0.0) or 0.0
        if t30 <= 0 and t24 <= 0:
            continue
        out.append({'slug': p.get('slug') or p.get('module') or p.get('name'), 'name': p.get('name'),
                    'category': p.get('category'), 'chains': p.get('chains') or [], 'total24h': t24,
                    'total7d': fnum(p.get('total7d'), 0.0) or 0.0, 'total30d': t30,
                    'total1y': fnum(p.get('total1y'), 0.0) or 0.0, 'parent': p.get('parentProtocol'),
                    'type': p.get('protocolType'), 'breakdown30d': p.get('breakdown30d') or {}})
    return out


def chart_window(chart, t_end_s, days):
    """Sum of a DefiLlama daily chart [[ts, value], ...] over the `days` days ending at t_end_s, and the days seen."""
    t0 = t_end_s - days * 86400
    xs = [fnum(v, 0.0) for t, v in chart or [] if t0 < int(t) <= t_end_s]
    return sum(xs), len(xs)


def parse_aave_markets(payload):
    """Aave API markets -> [{market, chain_id, symbol, borrow_usd, borrow_apr, supply_usd, supply_apr,
    reserve_factor}]. APYs come as fractions (value) and are turned into simple APRs."""
    out = []
    for m in (((payload or {}).get('data') or {}).get('markets') or []):
        cid = ((m.get('chain') or {}).get('chainId'))
        for r in m.get('reserves') or []:
            bi = r.get('borrowInfo') or {}
            si = r.get('supplyInfo') or {}
            usd_rate = fnum(r.get('usdExchangeRate'), 0.0) or 0.0
            b_apy = fnum(((bi.get('apy') or {}).get('value')))
            s_apy = fnum(((si.get('apy') or {}).get('value')))
            b_usd = fnum(((bi.get('total') or {}).get('usd')))
            s_tot = fnum(((si.get('total') or {}).get('value')))
            out.append({'market': m.get('name'), 'chain_id': cid,
                        'symbol': ((r.get('underlyingToken') or {}).get('symbol')),
                        'borrow_usd': b_usd or 0.0, 'borrow_apr': apy_to_apr(b_apy) if b_apy is not None else None,
                        'supply_usd': (s_tot or 0.0) * usd_rate,
                        'supply_apr': apy_to_apr(s_apy) if s_apy is not None else None,
                        'reserve_factor': fnum(((bi.get('reserveFactor') or {}).get('value')))})
    return out


def parse_morpho(pages):
    out = []
    for pg in pages:
        items = ((((pg or {}).get('data') or {}).get('markets') or {}).get('items')) or []
        for m in items:
            st = m.get('state') or {}
            out.append({'id': m.get('marketId'), 'chain_id': ((m.get('morphoBlue') or {}).get('chain') or {}).get('id'),
                        'loan': ((m.get('loanAsset') or {}).get('symbol')),
                        'collateral': ((m.get('collateralAsset') or {}).get('symbol')),
                        'borrow_usd': fnum(st.get('borrowAssetsUsd'), 0.0) or 0.0,
                        'supply_usd': fnum(st.get('supplyAssetsUsd'), 0.0) or 0.0,
                        'borrow_apy': fnum(st.get('borrowApy')), 'borrow_apy_30d': fnum(st.get('monthlyBorrowApy')),
                        'fee': fnum(st.get('fee'), 0.0)})
    return out


# ---------------------------------------------------------------------------------------------- collect: plumbing

class Net:
    """Paced clients (one minimum spacing per host) and a request log for the manifest."""

    def __init__(self):
        from chain_adapters import Http
        self.http = Http(min_interval=0.25, timeout=120, retries=4)
        self.http.host_interval.update({
            'api.llama.fi': 0.6, 'yields.llama.fi': 0.6, 'stablecoins.llama.fi': 0.6,
            'api.hyperliquid.xyz': 2.0, 'fapi.binance.com': 0.4, 'api.binance.com': 0.3, 'api.bybit.com': 0.3,
            'www.okx.com': 0.35, 'api.v3.aave.com': 0.6, 'blue-api.morpho.org': 0.6, 'api.merkl.xyz': 0.6})
        # Binance's funding history has its own 500 / 5 min / IP budget shared with every worker on this IP
        self.fund = Http(min_interval=1.2, timeout=60, retries=5)
        self.failures = {}
        self.counts = collections.Counter()
        self.t0 = time.time()

    def get(self, name, url, params=None, client=None):
        self.counts[urllib.parse.urlsplit(url).netloc] += 1
        try:
            return (client or self.http).get(url, params)
        except Exception as e:  # noqa: BLE001 - recorded, the step carries on
            self.failures[name] = str(e)[:240]
            return {'_failed': str(e)[:240]}

    def post(self, name, url, body):
        self.counts[urllib.parse.urlsplit(url).netloc] += 1
        try:
            return self.http.post(url, body)
        except Exception as e:  # noqa: BLE001
            self.failures[name] = str(e)[:240]
            return {'_failed': str(e)[:240]}

    def stats(self):
        return {'requests_by_host': dict(self.counts), 'failures': dict(list(self.failures.items())[:60]),
                'n_failures': len(self.failures), 'seconds': round(time.time() - self.t0, 1),
                'transport_errors': len(self.http.errors) + len(self.fund.errors)}


def cached(path, fetch, refresh=False):
    """The gzip-cached JSON at `path`, fetched when absent (or failed before, or `refresh`)."""
    p = Path(path)
    if p.exists() and not refresh:
        v = read_gz(p)
        if not failed(v):
            return v
    v = fetch()
    write_gz(p, v)
    return v


def manifest_update(out, part, info):
    p = Path(out) / 'manifest.json'
    m = json.loads(p.read_text()) if p.exists() else {}
    m.setdefault('collect', {})[part] = dict(info, finished_utc=utc())
    write_json(p, m)


# ---------------------------------------------------------------------------------------------- collect: parts

def collect_llama(out, net, refresh):
    raw = Path(out) / 'raw' / 'llama'
    for dtype in FEE_TYPES:
        cached(raw / ('overview_fees_%s.json.gz' % dtype), lambda: net.get(
            'fees:' + dtype, LLAMA + '/overview/fees', {'excludeTotalDataChart': 'true',
                                                       'excludeTotalDataChartBreakdown': 'true', 'dataType': dtype}),
            refresh)
    for kind in ('dexs', 'derivatives', 'open-interest'):
        cached(raw / ('overview_%s.json.gz' % kind), lambda: net.get(
            'overview:' + kind, LLAMA + '/overview/' + kind,
            {'excludeTotalDataChart': 'true', 'excludeTotalDataChartBreakdown': 'true'}), refresh)
    prot = cached(raw / 'protocols.json.gz', lambda: _trim_protocols(net.get('protocols', LLAMA + '/protocols')), refresh)
    cached(raw / 'stablecoins.json.gz', lambda: _trim_stables(net.get('stablecoins', STABLES + '/stablecoins',
                                                                       {'includePrices': 'false'})), refresh)
    # history for the protocols that carry each pool: the top of each category by 30-day fees, plus named ones
    fees = overview_rows(read_gz(raw / 'overview_fees_dailyFees.json.gz'))
    pick = set(['aave-v3', 'pendle', 'ethena-usde', 'hyperliquid-perps', 'jupiter-perpetual-exchange', 'gmx-v2-perps',
                'gains-network', 'tether', 'circle', 'uniswap-v3', 'aerodrome-slipstream', 'morpho-blue', 'sky-lending'])
    by_cat = collections.defaultdict(list)
    for r in fees:
        by_cat[r['category']].append(r)
    for cat, k in (('Derivatives', 10), ('Dexs', 10), ('Lending', 8), ('CDP', 3), ('Interface', 3)):
        for r in sorted(by_cat.get(cat, []), key=lambda r: -r['total30d'])[:k]:
            pick.add(r['slug'])
    for slug in sorted(pick):
        for dtype in SUMMARY_TYPES:
            brk = 'false' if (slug == 'aave-v3' and dtype == 'dailyFees') else 'true'
            cached(raw / 'summary' / ('%s__%s.json.gz' % (slug, dtype)), lambda: _trim_summary(net.get(
                'summary:%s:%s' % (slug, dtype), LLAMA + '/summary/fees/' + urllib.parse.quote(slug),
                {'dataType': dtype, 'excludeTotalDataChartBreakdown': brk})), refresh)
    for dtype in ('dailyBribesRevenue',):
        for slug in ('aerodrome-slipstream', 'aerodrome-v1', 'velodrome-v2', 'velodrome-slipstream'):
            cached(raw / 'summary' / ('%s__%s.json.gz' % (slug, dtype)), lambda: _trim_summary(net.get(
                'summary:%s:%s' % (slug, dtype), LLAMA + '/summary/fees/' + slug,
                {'dataType': dtype, 'excludeTotalDataChartBreakdown': 'true'})), refresh)
    manifest_update(out, 'llama', {'summaries': len(pick), 'endpoints': {
        'overview': LLAMA + '/overview/fees?dataType={%s}' % '|'.join(FEE_TYPES),
        'volumes': LLAMA + '/overview/{dexs,derivatives,open-interest}', 'protocols': LLAMA + '/protocols',
        'summary': LLAMA + '/summary/fees/{slug}?dataType={dailyFees|dailyRevenue|dailySupplySideRevenue}',
        'stablecoins': STABLES + '/stablecoins'}, 'net': net.stats()})
    print('llama: %d summaries' % len(pick), flush=True)


def _trim_protocols(d):
    if failed(d) or not isinstance(d, list):
        return d
    keep = ('name', 'slug', 'category', 'parentProtocol', 'tvl', 'chains')
    return [{k: p.get(k) for k in keep} for p in d]


def _trim_stables(d):
    if failed(d):
        return d
    out = []
    for s in d.get('peggedAssets') or []:
        circ = (s.get('circulating') or {}).get('peggedUSD')
        out.append({'name': s.get('name'), 'symbol': s.get('symbol'), 'circulating_usd': circ,
                    'pegType': s.get('pegType'), 'pegMechanism': s.get('pegMechanism')})
    return {'peggedAssets': out}


def _trim_summary(d):
    if failed(d):
        return d
    keep = ('name', 'slug', 'category', 'total24h', 'total7d', 'total30d', 'total1y', 'totalDataChart',
            'totalDataChartBreakdown', 'chains', 'methodology')
    return {k: d.get(k) for k in keep if k in d}


def collect_yields(out, net, refresh):
    raw = Path(out) / 'raw' / 'yields'
    d = cached(raw / 'pools.json.gz', lambda: net.get('yields:pools', YIELDS + '/pools'), refresh)
    # poolsBorrow (borrow totals and rates per pool) answers 402 "upgrade to the paid API plan": recorded, not used
    gap = cached(raw / 'poolsBorrow_probe.json.gz', lambda: net.get('yields:poolsBorrow', YIELDS + '/poolsBorrow'), refresh)
    manifest_update(out, 'yields', {'pools': len((d or {}).get('data') or []), 'poolsBorrow': 'paid (402)' if failed(gap) else 'ok',
                                    'net': net.stats()})
    print('yields: %d pools' % len((d or {}).get('data') or []), flush=True)


def collect_hl(out, net, refresh):
    raw = Path(out) / 'raw' / 'hl'
    dexes = cached(raw / 'perpDexs.json.gz', lambda: net.post('hl:perpDexs', HL_INFO, {'type': 'perpDexs'}), refresh)
    names = [''] + [d['name'] for d in (dexes or []) if isinstance(d, dict) and d.get('name')]
    stamp = int(time.time())
    for name in names:
        body = {'type': 'metaAndAssetCtxs'}
        if name:
            body['dex'] = name
        cached(raw / ('ctxs_%s.json.gz' % (name or 'main')), lambda: dict(
            fetched_ms=int(time.time() * 1000), payload=net.post('hl:ctxs:' + name, HL_INFO, body)), refresh)
    cached(raw / 'hlp_vault.json.gz', lambda: net.post('hl:hlp', HL_INFO, {'type': 'vaultDetails', 'vaultAddress': HLP_VAULT}),
           refresh)
    manifest_update(out, 'hl', {'dexes': names, 'stamp': stamp, 'endpoint': HL_INFO + ' {metaAndAssetCtxs, perpDexs, vaultDetails}',
                                'net': net.stats()})
    print('hl: %d dexes' % len(names), flush=True)


def collect_binance(out, net, refresh, top_oi=100, candidates=170, days=92):
    raw = Path(out) / 'raw' / 'binance'
    ex = cached(raw / 'exchangeInfo.json.gz', lambda: _trim_exinfo(net.get('bn:exinfo', BN_FAPI + '/fapi/v1/exchangeInfo')), refresh)
    tick = cached(raw / 'ticker24h.json.gz', lambda: net.get('bn:ticker', BN_FAPI + '/fapi/v1/ticker/24hr'), refresh)
    cached(raw / 'premiumIndex.json.gz', lambda: net.get('bn:premium', BN_FAPI + '/fapi/v1/premiumIndex'), refresh)
    cached(raw / 'fundingInfo.json.gz', lambda: net.get('bn:fundingInfo', BN_FAPI + '/fapi/v1/fundingInfo', client=net.fund), refresh)
    live = {s['symbol']: s for s in (ex or {}).get('symbols') or []
            if s.get('status') == 'TRADING' and s.get('contractType') in ('PERPETUAL', 'TRADIFI_PERPETUAL')}
    vol = sorted(((fnum(t.get('quoteVolume'), 0.0), t['symbol']) for t in tick or [] if isinstance(t, dict)
                  and t.get('symbol') in live), reverse=True)
    cands = [s for _, s in vol[:candidates]]
    for i, sym in enumerate(cands):
        cached(raw / 'oi_hist' / ('%s.json.gz' % sym), lambda: net.get(
            'bn:oi:' + sym, BN_FAPI + '/futures/data/openInterestHist', {'symbol': sym, 'period': '1d', 'limit': 30}), refresh)
        if (i + 1) % 40 == 0:
            print('  binance oi %d/%d' % (i + 1, len(cands)), flush=True)
    last_oi = []
    for sym in cands:
        pts = parse_bn_oi_hist(read_gz(raw / 'oi_hist' / ('%s.json.gz' % sym)) if (raw / 'oi_hist' / ('%s.json.gz' % sym)).exists() else [])
        if pts:
            last_oi.append((pts[-1][1], sym))
    top = [s for _, s in sorted(last_oi, reverse=True)[:top_oi]]
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * DAY_MS
    for i, sym in enumerate(top):
        cached(raw / 'funding' / ('%s.json.gz' % sym), lambda: dict(start_ms=start_ms, end_ms=end_ms,
                                                                   rows=_bn_funding(net, sym, start_ms, end_ms)), refresh)
        if (i + 1) % 25 == 0:
            print('  binance funding %d/%d' % (i + 1, len(top)), flush=True)
    write_json(raw / 'top_by_oi.json', {'candidates_by_volume': cands, 'top_by_oi': top})
    manifest_update(out, 'binance', {'candidates': len(cands), 'top_by_oi': len(top), 'days': days, 'net': net.stats(),
                                     'endpoints': ['/fapi/v1/exchangeInfo', '/fapi/v1/ticker/24hr', '/fapi/v1/premiumIndex',
                                                   '/fapi/v1/fundingInfo', '/futures/data/openInterestHist?period=1d&limit=30',
                                                   '/fapi/v1/fundingRate?startTime&limit=1000']})
    print('binance: %d candidates, %d by OI' % (len(cands), len(top)), flush=True)


def _trim_exinfo(d):
    if failed(d):
        return d
    keep = ('symbol', 'contractType', 'status', 'baseAsset', 'quoteAsset', 'underlyingType', 'underlyingSubType')
    return {'symbols': [{k: s.get(k) for k in keep} for s in d.get('symbols') or []]}


def _bn_funding(net, sym, start_ms, end_ms):
    out, s = [], start_ms
    for _ in range(6):
        rows = net.get('bn:funding:' + sym, BN_FAPI + '/fapi/v1/fundingRate',
                       {'symbol': sym, 'startTime': s, 'endTime': end_ms, 'limit': 1000}, client=net.fund)
        if failed(rows) or not rows:
            break
        out += rows
        if len(rows) < 1000:
            break
        s = int(rows[-1]['fundingTime']) + 1
    return out


def collect_bybit(out, net, refresh, top_n=30, days=31):
    raw = Path(out) / 'raw' / 'bybit'
    t = cached(raw / 'tickers.json.gz', lambda: net.get('bybit:tickers', BYBIT + '/v5/market/tickers', {'category': 'linear'}), refresh)
    lst = ((t or {}).get('result') or {}).get('list') or []
    perps = [x for x in lst if fnum(x.get('openInterestValue'), 0.0) and x.get('fundingRate') not in (None, '')]
    top = [x['symbol'] for x in sorted(perps, key=lambda x: -fnum(x.get('openInterestValue'), 0.0))[:top_n]]
    end_ms = int(time.time() * 1000)
    for sym in top:
        def fetch(sym=sym):
            rows, e = [], end_ms
            for _ in range(4):
                p = net.get('bybit:funding:' + sym, BYBIT + '/v5/market/funding/history',
                            {'category': 'linear', 'symbol': sym, 'limit': 200, 'endTime': e})
                got = ((p or {}).get('result') or {}).get('list') or [] if not failed(p) else []
                rows += got
                if len(got) < 200:
                    break
                e = min(int(r['fundingRateTimestamp']) for r in got) - 1
                if e < end_ms - days * DAY_MS:
                    break
            return {'result': {'list': rows}}
        cached(raw / 'funding' / ('%s.json.gz' % sym), fetch, refresh)
    manifest_update(out, 'bybit', {'symbols': len(perps), 'top': top, 'net': net.stats(),
                                   'endpoints': ['/v5/market/tickers?category=linear', '/v5/market/funding/history']})
    print('bybit: %d perps, top %d' % (len(perps), len(top)), flush=True)


def collect_okx(out, net, refresh, top_n=30):
    raw = Path(out) / 'raw' / 'okx'
    oi = cached(raw / 'open_interest.json.gz', lambda: net.get('okx:oi', OKX + '/api/v5/public/open-interest', {'instType': 'SWAP'}), refresh)
    cached(raw / 'tickers.json.gz', lambda: net.get('okx:tickers', OKX + '/api/v5/market/tickers', {'instType': 'SWAP'}), refresh)
    rows = (oi or {}).get('data') or []
    top = [r['instId'] for r in sorted(rows, key=lambda r: -(fnum(r.get('oiUsd'), 0.0) or 0.0))[:top_n]]
    for inst in top:
        cached(raw / 'funding' / ('%s.json.gz' % inst), lambda: net.get(
            'okx:funding:' + inst, OKX + '/api/v5/public/funding-rate-history', {'instId': inst, 'limit': 100}), refresh)
    manifest_update(out, 'okx', {'swaps': len(rows), 'top': top, 'net': net.stats(),
                                 'endpoints': ['/api/v5/public/open-interest?instType=SWAP', '/api/v5/market/tickers?instType=SWAP',
                                               '/api/v5/public/funding-rate-history?limit=100']})
    print('okx: %d swaps, top %d' % (len(rows), len(top)), flush=True)


AAVE_QUERY = ('query M($ids: [ChainId!]!) { markets(request: {chainIds: $ids}) { name address chain { chainId name } '
              'reserves { underlyingToken { symbol address } usdExchangeRate '
              'borrowInfo { apy { value } total { usd amount { value } } reserveFactor { value } utilizationRate { value } } '
              'supplyInfo { apy { value } total { value } } } } }')
MORPHO_QUERY = ('query M($skip: Int!) { markets(first: 500, skip: $skip, orderBy: BorrowAssetsUsd, orderDirection: Desc) '
                '{ items { marketId loanAsset { symbol } collateralAsset { symbol } morphoBlue { chain { id } } '
                'state { borrowAssetsUsd supplyAssetsUsd borrowApy monthlyBorrowApy fee } } pageInfo { countTotal } } }')


def collect_lending(out, net, refresh):
    raw = Path(out) / 'raw' / 'lending'
    chains = cached(raw / 'aave_chains.json.gz', lambda: net.post('aave:chains', AAVE_API, {'query': '{ chains { name chainId } }'}), refresh)
    ids = [c['chainId'] for c in (((chains or {}).get('data') or {}).get('chains') or []) if c.get('chainId') not in (84532,)]
    cached(raw / 'aave_markets.json.gz', lambda: net.post('aave:markets', AAVE_API, {'query': AAVE_QUERY, 'variables': {'ids': ids}}), refresh)
    pages = 0
    for k in range(8):
        p = cached(raw / ('morpho_markets_%d.json.gz' % k), lambda: net.post(
            'morpho:%d' % k, MORPHO_API, {'query': MORPHO_QUERY, 'variables': {'skip': 500 * k}}), refresh)
        pages += 1
        items = ((((p or {}).get('data') or {}).get('markets') or {}).get('items')) or []
        if not items or min(fnum((i.get('state') or {}).get('borrowAssetsUsd'), 0.0) or 0.0 for i in items) < 50_000:
            break
    manifest_update(out, 'lending', {'aave_chain_ids': ids, 'morpho_pages': pages, 'net': net.stats(),
                                     'endpoints': [AAVE_API + ' markets(chainIds) reserves borrowInfo/supplyInfo',
                                                   MORPHO_API + ' markets orderBy BorrowAssetsUsd']})
    print('lending: aave %d chains, morpho %d pages' % (len(ids), pages), flush=True)


def collect_merkl(out, net, refresh, max_pages=15):
    raw = Path(out) / 'raw' / 'merkl'
    n = 0
    for k in range(max_pages):
        p = cached(raw / ('opportunities_%02d.json.gz' % k), lambda: _trim_merkl(net.get(
            'merkl:%d' % k, MERKL + '/opportunities', {'status': 'LIVE', 'items': 100, 'page': k})), refresh)
        n += 1
        if failed(p) or len(p) < 100:
            break
    manifest_update(out, 'merkl', {'pages': n, 'endpoint': MERKL + '/opportunities?status=LIVE&items=100&page=k', 'net': net.stats()})
    print('merkl: %d pages' % n, flush=True)


def _trim_merkl(d):
    if failed(d) or not isinstance(d, list):
        return d
    keep = ('chainId', 'type', 'name', 'action', 'tvl', 'apr', 'dailyRewards', 'liveCampaigns', 'identifier', 'id')
    return [dict({k: o.get(k) for k in keep}, protocol=(o.get('protocol') or {}).get('id'),
                 chain=(o.get('chain') or {}).get('name')) for o in d]


def collect_klines(out, net, refresh, symbols=('ETHUSDT', 'BTCUSDT', 'SOLUSDT', 'BNBUSDT', 'ETHBTC', 'HYPEUSDT', 'AVAXUSDT')):
    raw = Path(out) / 'raw' / 'klines'
    for sym in symbols:
        cached(raw / ('%s.json.gz' % sym), lambda: net.get('klines:' + sym, BN_SPOT + '/api/v3/klines',
                                                           {'symbol': sym, 'interval': '1d', 'limit': 120}), refresh)
    manifest_update(out, 'klines', {'symbols': list(symbols), 'endpoint': BN_SPOT + '/api/v3/klines?interval=1d&limit=120',
                                    'net': net.stats()})
    print('klines: %d' % len(symbols), flush=True)


def collect_pendle(out, net, refresh):
    """YT outstanding per active Pendle market: totalSupply() and decimals() of each YT, read on chain through the
    public endpoints in chain_registry.json (YT supply = PT supply = the notional on which YT holders pay the premium)."""
    from chain_adapters import JsonRpc
    raw = Path(out) / 'raw' / 'pendle'
    reg = json.loads(REGISTRY.read_text())
    rpcs = {c.get('evm_chain_id'): (c.get('probe') or {}).get('rpc') or [] for c in reg['chains'] if c.get('evm_chain_id')}
    lists = sorted((PENDLE_DIR / 'raw' / 'lists').glob('*_active.json'))
    done = {}
    for f in lists:
        cid = int(f.name.split('_')[0])
        mk = (json.loads(f.read_text()).get('markets') or [])
        if not mk:
            continue
        path = raw / ('yt_supply_%d.json.gz' % cid)
        if path.exists() and not refresh and not failed(read_gz(path)):
            done[cid] = len(mk)
            continue
        if not rpcs.get(cid):
            write_gz(path, {'_failed': 'no public RPC in chain_registry for chain %d' % cid})
            continue
        rpc = JsonRpc(rpcs[cid], label='pendle-%d' % cid)
        res = {}
        for m in mk:
            yt = m['yt'].split('-', 1)[1]
            try:
                ts = rpc.call('eth_call', [{'to': yt, 'data': '0x18160ddd'}, 'latest'])
                de = rpc.call('eth_call', [{'to': yt, 'data': '0x313ce567'}, 'latest'])
                res[m['address']] = {'yt': yt, 'name': m.get('name'), 'expiry': m.get('expiry'),
                                     'total_supply_raw': int(ts, 16) if ts and ts != '0x' else None,
                                     'decimals': int(de, 16) if de and de != '0x' else None}
            except Exception as e:  # noqa: BLE001
                res[m['address']] = {'yt': yt, 'error': str(e)[:200]}
            time.sleep(0.15)
        write_gz(path, {'chain_id': cid, 'read_utc': utc(), 'markets': res})
        done[cid] = len(mk)
    manifest_update(out, 'pendle', {'chains': done, 'source': 'eth_call totalSupply()/decimals() on each active YT; market list '
                                    'from research/2026-10-09/pendle_history/raw/lists (2026-10-10 00:02 UTC)'})
    print('pendle: %s' % done, flush=True)


PARTS = {'llama': collect_llama, 'yields': collect_yields, 'hl': collect_hl, 'binance': collect_binance,
         'bybit': collect_bybit, 'okx': collect_okx, 'lending': collect_lending, 'merkl': collect_merkl,
         'klines': collect_klines, 'pendle': collect_pendle}


def cmd_collect(args):
    net = Net()
    parts = args.parts.split(',') if args.parts else list(PARTS)
    for p in parts:
        t = time.time()
        try:
            PARTS[p](args.out, net, args.refresh)
        except Exception as e:  # noqa: BLE001 - one part failing must not stop the others
            print('part %s failed: %s' % (p, e), flush=True)
            manifest_update(args.out, p, {'error': str(e)[:300]})
        print('  %s took %.0fs' % (p, time.time() - t), flush=True)
    print(json.dumps(net.stats())[:2000])



# ---------------------------------------------------------------------------------------------- analyze: funding

def _store_series(key):
    p = FUNDING_STORE / ('%s.json.gz' % key)
    return parse_store(read_gz(p)) if p.exists() else []


def _snap_oi(dirs):
    """{coin: [(t_ms, oi_usd)]} from every stored metaAndAssetCtxs snapshot (main dex and HIP-3)."""
    pts = collections.defaultdict(list)
    for d in dirs:
        for f in sorted(Path(d).glob('*.json.gz')):
            s = read_gz(f)
            t = int(s.get('ts') or int(f.name.split('.')[0])) * (1000 if (s.get('ts') or 0) < 1e12 else 1)
            for dex, payload in (s.get('dexes') or {}).items():
                for r in parse_hl_ctxs(payload, dex):
                    pts[r['coin']].append((t, r['oi_usd']))
    return pts


def analyze_hl(out):
    raw = Path(out) / 'raw' / 'hl'
    files = sorted(raw.glob('ctxs_*.json.gz'))
    rows = []
    fetched = None
    for f in files:
        d = read_gz(f)
        dex = f.name[len('ctxs_'):-len('.json.gz')]
        dex = '' if dex == 'main' else dex
        fetched = d.get('fetched_ms') or fetched
        rows += parse_hl_ctxs(d.get('payload'), dex)
    main_names = {r['coin'] for r in rows if r['dex'] == ''}
    series = {r['coin']: _store_series(store_key(r['coin'])) for r in rows}
    store_end = max((s[-1][0] for s in series.values() if s), default=None)
    per = []
    for r in rows:
        if r['oi_usd'] <= 0:
            continue
        s = series.get(r['coin']) or []
        cls = ('metal' if is_metal(r['coin']) else 'crypto') if r['dex'] == '' else classify_hip3(r['coin'], main_names)
        w = {k: window_stats(s, store_end, k) for k in (7, 30, 90)} if s and store_end else {}
        src30 = 'store' if w and coverage_ok(w[30], 30, 24) else 'snapshot'
        src90 = 'store' if w and coverage_ok(w[90], 90, 24) else src30
        now_ann = r['funding_h'] * HOURS_PER_YEAR
        ann30 = w[30]['ann'] if src30 == 'store' else now_ann
        pos30 = w[30]['ann_pos'] if src30 == 'store' else max(now_ann, 0.0)
        neg30 = w[30]['ann_neg'] if src30 == 'store' else min(now_ann, 0.0)
        ann90 = w[90]['ann'] if src90 == 'store' else ann30
        per.append({'coin': r['coin'], 'dex': r['dex'] or 'main', 'cls': cls, 'rent': cls not in ROLL_CLASSES,
                    'oi_usd': r['oi_usd'], 'vlm_usd': r['vlm_usd'], 'rate_now': now_ann, 'rate_7d': w[7]['ann'] if w else None,
                    'rate_30d': ann30, 'rate_90d': ann90, 'src_30d': src30, 'src_90d': src90,
                    'share_pos_30d': w[30]['share_pos'] if w else None,
                    'share_at_interest_rate_30d': (sum(1 for t, x in s if t > store_end - 30 * DAY_MS and abs(x - 0.0000125) < 1e-10) /
                                                   w[30]['n']) if w and w[30]['n'] else None,
                    'longs_paid_30d': r['oi_usd'] * pos30, 'shorts_paid_30d': -r['oi_usd'] * neg30,
                    'net_30d': r['oi_usd'] * ann30, 'net_90d': r['oi_usd'] * ann90,
                    'above_fair_30d': flow_split(r['oi_usd'], ann30, SSR)['above_fair'],
                    'above_fair_90d': flow_split(r['oi_usd'], ann90, SSR)['above_fair']})
    agg = _agg_funding(per, keys=('dex', 'cls'))
    # path B: the dollars that actually changed hands since the first stored snapshot, OI interpolated between the
    # four snapshots (2026-09-08, 09-10, 10-09 and this collection), against path A on the same window
    snaps = _snap_oi(SNAP_DIRS)
    for r in rows:
        snaps[r['coin']].append((fetched, r['oi_usd']))
    t0 = min((p[0] for v in snaps.values() for p in v), default=None)
    pathb = {'net': 0.0, 'longs_paid': 0.0, 'shorts_paid': 0.0, 'coins': 0}
    patha = 0.0
    for r in per:
        if r['dex'] != 'main':
            continue
        s = series.get(r['coin']) or []
        f = realised_flow(s, snaps.get(r['coin']) or [], t0, store_end)
        if f['n']:
            pathb['coins'] += 1
            for k in ('net', 'longs_paid', 'shorts_paid'):
                pathb[k] += f[k]
            patha += r['oi_usd'] * window_stats(s, store_end, (store_end - t0) / DAY_MS)['sum']
    span = (store_end - t0) / DAY_MS if t0 and store_end else None
    checks = {'window_utc': [utc(t0), utc(store_end)], 'days': span,
              'path_b_realised_net_per_year': annualise(pathb['net'], span) if span else None,
              'path_b_longs_paid_per_year': annualise(pathb['longs_paid'], span) if span else None,
              'path_a_current_oi_x_same_window_rates_per_year': annualise(patha, span) if span else None,
              'coins': pathb['coins']}
    if checks['path_a_current_oi_x_same_window_rates_per_year']:
        checks['ratio_b_over_a'] = checks['path_b_realised_net_per_year'] / checks['path_a_current_oi_x_same_window_rates_per_year']
    # path C: open interest from DefiLlama's adapter against the venue's own contexts
    oi_ll = {r['slug']: r['total24h'] for r in overview_rows(_read(Path(out) / 'raw' / 'llama' / 'overview_open-interest.json.gz'))}
    hl_main_oi = sum(r['oi_usd'] for r in per if r['dex'] == 'main')
    xyz_oi = sum(r['oi_usd'] for r in per if r['dex'] == 'xyz')
    checks['oi_main_ctx_usd'] = hl_main_oi
    checks['oi_main_defillama_usd'] = oi_ll.get('hyperliquid-perps')
    checks['oi_xyz_ctx_usd'] = xyz_oi
    checks['oi_xyz_defillama_usd'] = oi_ll.get('tradexyz')
    for k, a, b in (('oi_ratio_main', 'oi_main_defillama_usd', 'oi_main_ctx_usd'), ('oi_ratio_xyz', 'oi_xyz_defillama_usd', 'oi_xyz_ctx_usd')):
        checks[k] = checks[a] / checks[b] if checks.get(a) and checks.get(b) else None
    # the store's last settled hour against the live predicted rate, coin by coin (same source family, different read)
    diffs = [abs((series[r['coin']][-1][1] * HOURS_PER_YEAR) - r['rate_now']) for r in per
             if r['dex'] == 'main' and series.get(r['coin']) and r['oi_usd'] > 1e8]
    checks['store_last_vs_live_abs_diff_ann_median'] = statistics.median(diffs) if diffs else None
    top = sorted(per, key=lambda r: -abs(r['above_fair_30d']))[:25]
    mains = [r for r in per if r['dex'] == 'main' and r['cls'] == 'crypto' and r.get('share_at_interest_rate_30d') is not None]
    oi_m = sum(r['oi_usd'] for r in mains)
    checks['main_dex_oi_weighted_share_of_hours_at_interest_rate_30d'] = (
        sum(r['oi_usd'] * r['share_at_interest_rate_30d'] for r in mains) / oi_m) if oi_m else None
    return {'fetched_utc': utc(fetched) if fetched else None, 'store_end_utc': utc(store_end) if store_end else None,
            'markets': len(per), 'aggregates': agg, 'top_by_above_fair': top,
            'roll_markets_oi_usd': sum(r['oi_usd'] for r in per if not r['rent']),
            'checks': checks, 'per_market': per}


def _read(p):
    return read_gz(p) if Path(p).exists() else None


def _agg_funding(per, keys=('cls',)):
    """Totals over funding rows (all, rent-only, and by each key): OI, longs paid, shorts paid, net, above fair (signed
    and per-market clipped), 30 and 90 days."""
    def tot(rs):
        return {'markets': len(rs), 'oi_usd': sum(r['oi_usd'] for r in rs),
                'longs_paid_30d': sum(r['longs_paid_30d'] for r in rs), 'shorts_paid_30d': sum(r['shorts_paid_30d'] for r in rs),
                'net_30d': sum(r['net_30d'] for r in rs), 'net_90d': sum(r['net_90d'] for r in rs),
                'above_fair_30d': sum(r['above_fair_30d'] for r in rs),
                'above_fair_30d_clipped': sum(max(0.0, r['above_fair_30d']) for r in rs),
                'above_fair_90d': sum(r['above_fair_90d'] for r in rs),
                'above_fair_90d_clipped': sum(max(0.0, r['above_fair_90d']) for r in rs),
                'oi_weighted_rate_30d': (sum(r['net_30d'] for r in rs) / sum(r['oi_usd'] for r in rs)) if rs and sum(r['oi_usd'] for r in rs) else None,
                'snapshot_rate_share_of_oi': (sum(r['oi_usd'] for r in rs if r.get('src_30d') == 'snapshot') /
                                              sum(r['oi_usd'] for r in rs)) if rs and sum(r['oi_usd'] for r in rs) else None}
    out = {'all': tot(per), 'rent_only': tot([r for r in per if r.get('rent', True)])}
    for k in keys:
        groups = collections.defaultdict(list)
        for r in per:
            groups[r.get(k)].append(r)
        out['by_' + k] = {str(g): tot(rs) for g, rs in sorted(groups.items(), key=lambda kv: -sum(r['oi_usd'] for r in kv[1]))}
    return out


def analyze_binance(out):
    raw = Path(out) / 'raw' / 'binance'
    top = json.loads((raw / 'top_by_oi.json').read_text())['top_by_oi'] if (raw / 'top_by_oi.json').exists() else []
    ex = {s['symbol']: s for s in (_read(raw / 'exchangeInfo.json.gz') or {}).get('symbols') or []}
    per = []
    t_end = None
    for sym in top:
        oi_pts = parse_bn_oi_hist(_read(raw / 'oi_hist' / ('%s.json.gz' % sym)) or [])
        f = _read(raw / 'funding' / ('%s.json.gz' % sym)) or {}
        rates = parse_bn_funding(f.get('rows') or [])
        if not oi_pts or not rates:
            continue
        t_end = f.get('end_ms') or rates[-1][0]
        info = ex.get(sym) or {}
        cls = 'tradfi_' + (info.get('underlyingType') or '').lower() if info.get('contractType') == 'TRADIFI_PERPETUAL' else 'crypto'
        if is_metal(sym):
            cls = 'metal'
        oi_now = oi_pts[-1][1]
        rf = realised_flow(rates, oi_pts, t_end - 30 * DAY_MS, t_end)
        w30, w90 = window_stats(rates, t_end, 30), window_stats(rates, t_end, 90)
        oi_avg30 = statistics.fmean(v for _, v in oi_pts)
        listed90 = rates[0][0] <= t_end - 85 * DAY_MS
        ann90 = w90['ann'] if listed90 else w30['ann']
        per.append({'coin': sym, 'cls': cls, 'oi_usd': oi_now, 'oi_avg30_usd': oi_avg30, 'rate_30d': w30['ann'], 'rate_90d': ann90,
                    'share_pos_30d': w30['share_pos'], 'settlements_30d': w30['n'],
                    'longs_paid_30d': annualise(rf['longs_paid'], 30), 'shorts_paid_30d': annualise(rf['shorts_paid'], 30),
                    'net_30d': annualise(rf['net'], 30), 'net_90d': oi_now * ann90,
                    'above_fair_30d': annualise(rf['net'], 30) - oi_avg30 * SSR,
                    'above_fair_90d': flow_split(oi_now, ann90, SSR)['above_fair'], 'rent': True})
    agg = _agg_funding(per, keys=('cls',))
    cand_oi = 0.0
    for p in (raw / 'oi_hist').glob('*.json.gz'):
        pts = parse_bn_oi_hist(_read(p) or [])
        if pts:
            cand_oi += pts[-1][1]
    zero = sum(1 for r in per if r['rate_30d'] == 0)
    return {'symbols': len(per), 'end_utc': utc(t_end) if t_end else None, 'aggregates': agg,
            'candidates_oi_usd': cand_oi, 'top_oi_share_of_candidates': agg['all']['oi_usd'] / cand_oi if cand_oi else None,
            'top_by_above_fair': sorted(per, key=lambda r: -abs(r['above_fair_30d']))[:20], 'zero_rate_symbols': zero,
            'per_market': per}


def analyze_bybit(out):
    raw = Path(out) / 'raw' / 'bybit'
    t = _read(raw / 'tickers.json.gz') or {}
    lst = ((t.get('result') or {}).get('list')) or []
    allp = [x for x in lst if fnum(x.get('openInterestValue'), 0.0)]
    per = []
    for f in sorted((raw / 'funding').glob('*.json.gz')):
        sym = f.name[:-len('.json.gz')]
        rates = parse_bybit_funding(_read(f))
        tick = next((x for x in allp if x['symbol'] == sym), None)
        if not rates or not tick:
            continue
        t_end = rates[-1][0]
        w = window_stats(rates, t_end, 30)
        oi = fnum(tick.get('openInterestValue'), 0.0)
        per.append(_cex_row(sym, oi, w))
    return _cex_summary(per, sum(fnum(x.get('openInterestValue'), 0.0) for x in allp), len(allp),
                        sum(fnum(x.get('openInterestValue'), 0.0) for x in allp if is_metal(x['symbol'])))


def analyze_okx(out):
    raw = Path(out) / 'raw' / 'okx'
    oi = (_read(raw / 'open_interest.json.gz') or {}).get('data') or []
    by = {r['instId']: fnum(r.get('oiUsd'), 0.0) or 0.0 for r in oi}
    per = []
    for f in sorted((raw / 'funding').glob('*.json.gz')):
        inst = f.name[:-len('.json.gz')]
        rates = parse_okx_funding(_read(f))
        if len(rates) < 10 or inst not in by:
            continue
        t_end = rates[-1][0]
        days = min(30.0, (t_end - rates[0][0]) / DAY_MS)
        w = window_stats(rates, t_end, days)
        w = dict(w, ann=w['sum'] * 365.0 / days, ann_pos=w['sum_pos'] * 365.0 / days, ann_neg=w['sum_neg'] * 365.0 / days)
        per.append(_cex_row(inst, by[inst], w, days))
    return _cex_summary(per, sum(by.values()), len(by), sum(v for k, v in by.items() if is_metal(k)))


def _cex_row(sym, oi, w, days=30):
    return {'coin': sym, 'cls': 'metal' if is_metal(sym) else 'crypto', 'oi_usd': oi, 'rate_30d': w['ann'], 'rate_90d': w['ann'], 'window_days': days,
            'share_pos_30d': w['share_pos'], 'longs_paid_30d': oi * w['ann_pos'], 'shorts_paid_30d': -oi * w['ann_neg'],
            'net_30d': oi * w['ann'], 'net_90d': oi * w['ann'], 'above_fair_30d': flow_split(oi, w['ann'], SSR)['above_fair'],
            'above_fair_90d': flow_split(oi, w['ann'], SSR)['above_fair'], 'rent': True, 'src_30d': 'history'}


def _cex_summary(per, total_oi, n_all, metal_oi_all=0.0):
    agg = _agg_funding(per)
    cov = agg['all']['oi_usd'] / total_oi if total_oi else None
    # the crypto tail is extrapolated at the covered crypto set's OI-weighted rates (upper end of the band); covered only
    # is the lower end; metals are counted market by market, never extrapolated
    cr = agg['by_cls'].get('crypto') or {'oi_usd': 0.0}
    scale = ((total_oi - metal_oi_all) / cr['oi_usd']) if cr['oi_usd'] else 1.0
    return {'symbols_all': n_all, 'symbols_history': len(per), 'oi_all_usd': total_oi, 'oi_covered_share': cov,
            'aggregates': agg, 'crypto_tail_scale': scale,
            'extrapolated': {k: cr.get(k, 0.0) * scale for k in ('longs_paid_30d', 'net_30d', 'above_fair_30d', 'above_fair_30d_clipped')},
            'per_market': per}



# ---------------------------------------------------------------------------------------------- analyze: DefiLlama pools

def llama_table(out):
    """One row per protocol with 30-day fees, revenue, supply-side and holders revenue (USD a year), its pool, and how
    the supply side was obtained when DefiLlama has none (fees - revenue, flagged)."""
    raw = Path(out) / 'raw' / 'llama'
    tabs = {dtype: {r['slug']: r for r in overview_rows(_read(raw / ('overview_fees_%s.json.gz' % dtype)))} for dtype in FEE_TYPES}
    fees = list(tabs['dailyFees'].values())
    pools = assign_pools(fees)
    rows = []
    for r in fees:
        slug = r['slug']
        get = lambda dtype, k='total30d': (tabs[dtype].get(slug) or {}).get(k)
        f30, rev30, sup30 = r['total30d'], get('dailyRevenue'), get('dailySupplySideRevenue')
        src = 'reported'
        if sup30 is None and rev30 is not None:
            sup30, src = max(0.0, f30 - rev30), 'fees_minus_revenue'
        elif sup30 is None:
            src = 'missing'
        rows.append({'slug': slug, 'name': r['name'], 'category': r['category'], 'pool': pools.get(slug),
                     'chains': r['chains'][:6], 'fees_yr': annualise(f30, 30), 'fees_1y': r['total1y'],
                     'fees_7d_yr': annualise(r['total7d'], 7), 'revenue_yr': annualise(rev30, 30) if rev30 is not None else None,
                     'supply_side_yr': annualise(sup30, 30) if sup30 is not None else None, 'supply_side_src': src,
                     'holders_yr': annualise(get('dailyHoldersRevenue'), 30) if get('dailyHoldersRevenue') is not None else None,
                     'bribes_yr': annualise(get('dailyBribesRevenue'), 30) if get('dailyBribesRevenue') is not None else None})
    return rows, tabs


def pool_totals(rows, pool, top=15):
    rs = [r for r in rows if r['pool'] == pool]
    def s(k):
        return sum(r[k] or 0.0 for r in rs)
    sup_rep = sum(r['supply_side_yr'] or 0.0 for r in rs if r['supply_side_src'] == 'reported')
    sup_1y = sum(r['fees_1y'] * (r['supply_side_yr'] / r['fees_yr']) for r in rs if r['fees_yr'] and r['supply_side_yr'] is not None)
    return {'protocols': len(rs), 'fees_yr': s('fees_yr'), 'fees_7d_yr': s('fees_7d_yr'), 'fees_1y': s('fees_1y'),
            'supply_side_1y': sup_1y,
            'revenue_yr': s('revenue_yr'), 'supply_side_yr': s('supply_side_yr'), 'supply_side_reported_yr': sup_rep,
            'supply_side_missing_fees_yr': sum(r['fees_yr'] for r in rs if r['supply_side_src'] == 'missing'),
            'holders_yr': s('holders_yr'),
            'by_category': {c: sum(r['fees_yr'] for r in rs if r['category'] == c) for c in sorted({r['category'] for r in rs})},
            'top': [{k: r[k] for k in ('name', 'slug', 'category', 'fees_yr', 'revenue_yr', 'supply_side_yr', 'supply_side_src', 'fees_1y')}
                    for r in sorted(rs, key=lambda r: -r['fees_yr'])[:top]]}


def summaries(out):
    """30/90/365-day run-rates from each protocol's daily history, and the per-chain split where it was kept."""
    res = {}
    for f in sorted((Path(out) / 'raw' / 'llama' / 'summary').glob('*.json.gz')):
        slug, dtype = f.name[:-len('.json.gz')].split('__')
        d = _read(f)
        if failed(d) or not d.get('totalDataChart'):
            res.setdefault(slug, {})[dtype] = None
            continue
        today = int(time.time()) // 86400 * 86400
        ch = [x for x in d['totalDataChart'] if int(x[0]) < today]  # today's point is a partial day
        if not ch:
            res.setdefault(slug, {})[dtype] = None
            continue
        t_end = int(ch[-1][0])
        e = {'last_day_utc': utc(t_end * 1000)}
        for days in (30, 90, 365):
            v, n = chart_window(ch, t_end, days)
            e['run_rate_%dd' % days] = annualise(v, days) if n >= 0.9 * days else None
        brk = d.get('totalDataChartBreakdown')
        if brk:
            by = collections.defaultdict(float)
            t0 = t_end - 30 * 86400
            for t, parts in brk:
                if int(t) > t0:
                    for chain, vs in (parts or {}).items():
                        by[chain] += sum(fnum(v, 0.0) for v in (vs.values() if isinstance(vs, dict) else [vs]))
            e['by_chain_30d_yr'] = {c: annualise(v, 30) for c, v in sorted(by.items(), key=lambda kv: -kv[1])}
        res.setdefault(slug, {})[dtype] = e
    return res


def analyze_hlp(out, llama_rows):
    """HLP's own account history (vaultDetails): last month's PnL over its account value, annualised. This is the
    vault's whole income (market making, liquidations), not fees; the PnL transfer is another worker's study."""
    v = _read(Path(out) / 'raw' / 'hl' / 'hlp_vault.json.gz')
    if failed(v) or not isinstance(v, dict):
        return {'error': 'vaultDetails unavailable'}
    res = {'apr_field': fnum(v.get('apr'))}
    for period, d in v.get('portfolio') or []:
        if period != 'month':
            continue
        av = [(int(t), fnum(x, 0.0)) for t, x in d.get('accountValueHistory') or []]
        pn = [(int(t), fnum(x, 0.0)) for t, x in d.get('pnlHistory') or []]
        if av and pn:
            days = (pn[-1][0] - pn[0][0]) / DAY_MS
            mean_av = statistics.fmean(x for _, x in av)
            res.update({'month_pnl_usd': pn[-1][1] - pn[0][1], 'days': days, 'account_value_usd': av[-1][1],
                        'mean_account_value_usd': mean_av,
                        'income_yr': annualise(pn[-1][1] - pn[0][1], days) if days > 0 else None})
            res['apr_month'] = res['income_yr'] / mean_av if mean_av and res.get('income_yr') is not None else None
    return res


def analyze_incentives(out):
    raw = Path(out) / 'raw'
    pools = ((_read(raw / 'yields' / 'pools.json.gz') or {}).get('data')) or []
    prot = _read(raw / 'llama' / 'protocols.json.gz') or []
    cats = {p.get('slug'): p.get('category') for p in prot if isinstance(p, dict)}
    tot, rows = incentive_budget(pools, cats)
    def group(key, top=None):
        g = collections.defaultdict(float)
        for r in rows:
            g[r[key]] += r['budget']
        items = sorted(g.items(), key=lambda kv: -kv[1])
        return dict(items[:top] if top else items)
    stable = sum(r['budget'] for r in rows if r['stable'])
    tvl_rewarded = sum(r['tvl'] for r in rows)
    sens = {}
    for cap in (100.0, 300.0, 1000.0):
        t2, _ = incentive_budget(pools, cats, cap_apy=cap)
        sens['cap_%d' % cap] = t2['headline']
    # Merkl's own budgets (live campaigns, dailyRewards in USD): an independent path for the part Merkl distributes
    mk = []
    for f in sorted((raw / 'merkl').glob('opportunities_*.json.gz')):
        d = _read(f)
        if isinstance(d, list):
            mk += d
    seen = set()
    mk_u = []
    for o in mk:
        k = o.get('id') or o.get('identifier')
        if k in seen:
            continue
        seen.add(k)
        mk_u.append(o)
    m_tot = sum(fnum(o.get('dailyRewards'), 0.0) or 0.0 for o in mk_u) * 365.0
    by_action = collections.defaultdict(float)
    by_proto = collections.defaultdict(float)
    by_chain = collections.defaultdict(float)
    for o in mk_u:
        b = (fnum(o.get('dailyRewards'), 0.0) or 0.0) * 365.0
        by_action[o.get('action') or '?'] += b
        by_proto[o.get('protocol') or '?'] += b
        by_chain[o.get('chain') or str(o.get('chainId'))] += b
    big = sorted(mk_u, key=lambda o: -(fnum(o.get('dailyRewards'), 0.0) or 0.0))[:12]
    # the same protocols' budgets as DefiLlama's yield pools see them
    ll_by_proj = group('project')
    ll_by_proj_all = ll_by_proj
    overlap = {}
    for proto, b in sorted(by_proto.items(), key=lambda kv: -kv[1])[:10]:
        cand = {k: v for k, v in ll_by_proj.items() if proto and (k == proto or k.startswith(proto + '-') or k.split('-')[0] == proto.split('-')[0])}
        overlap[proto] = {'merkl_yr': b, 'defillama_yr': sum(cand.values()), 'defillama_projects': sorted(cand)[:6]}
    # union of the two paths: DefiLlama's headline plus, protocol by protocol, whatever Merkl distributes beyond what
    # DefiLlama's pools of that protocol already show (Merkl campaigns DefiLlama does not see, e.g. Aave's loop programs)
    extra = 0.0
    for proto, b in by_proto.items():
        cand = sum(v for k, v in ll_by_proj_all.items() if proto and proto != '?' and (k == proto or k.split('-')[0] == proto.split('-')[0]))
        extra += max(0.0, b - cand)
    return {'union_with_merkl_yr': tot['headline'] + extra, 'merkl_beyond_defillama_yr': extra,
            'outlier_flagged_below_cap_yr': sum(fnum(p.get('tvlUsd'), 0.0) * (fnum(p.get('apyReward'), 0.0) or 0.0) / 100.0
                                                for p in pools if p.get('outlier') and 0 < (fnum(p.get('apyReward'), 0.0) or 0.0) <= 50.0
                                                and (fnum(p.get('tvlUsd'), 0.0) or 0.0) >= 10_000.0),
            'pools_total': len(pools), 'pools_rewarded_headline': len(rows), 'totals': tot,
            'headline_yr': tot['headline'], 'stable_yr': stable, 'volatile_yr': tot['headline'] - stable,
            'tvl_rewarded_usd': tvl_rewarded, 'mean_reward_apr_on_rewarded_tvl': tot['headline'] / tvl_rewarded if tvl_rewarded else None,
            'cap_sensitivity': sens, 'by_chain': group('chain', 15), 'by_project': group('project', 25),
            'by_category': group('category', 15), 'by_exposure': group('exposure'),
            'top_pools': [{k: r[k] for k in ('project', 'chain', 'symbol', 'tvl', 'apy_reward', 'apy_base', 'budget', 'stable')}
                          for r in sorted(rows, key=lambda r: -r['budget'])[:20]],
            'merkl': {'opportunities': len(mk_u), 'budget_yr': m_tot, 'by_action': dict(sorted(by_action.items(), key=lambda kv: -kv[1])),
                      'by_chain': dict(sorted(by_chain.items(), key=lambda kv: -kv[1])[:10]),
                      'by_protocol': dict(sorted(by_proto.items(), key=lambda kv: -kv[1])[:15]),
                      'largest': [{'name': o.get('name'), 'protocol': o.get('protocol'), 'chain': o.get('chain'), 'action': o.get('action'),
                                   'tvl': fnum(o.get('tvl')), 'apr': fnum(o.get('apr')), 'budget_yr': (fnum(o.get('dailyRewards'), 0.0) or 0.0) * 365}
                                  for o in big],
                      'vs_defillama_by_protocol': overlap}}


PAIR_TOKENS = {'eth': 'ETH', 'btc': 'BTC', 'stable': 'USD'}
EXTRA_TOKENS = {'SOL': 'SOL', 'WSOL': 'SOL', 'BNB': 'BNB', 'WBNB': 'BNB', 'HYPE': 'HYPE', 'WHYPE': 'HYPE', 'AVAX': 'AVAX', 'WAVAX': 'AVAX'}
PAIR_KLINES = {('ETH', 'USD'): 'ETHUSDT', ('BTC', 'USD'): 'BTCUSDT', ('SOL', 'USD'): 'SOLUSDT', ('BNB', 'USD'): 'BNBUSDT',
               ('BTC', 'ETH'): 'ETHBTC', ('HYPE', 'USD'): 'HYPEUSDT', ('AVAX', 'USD'): 'AVAXUSDT'}
CL_PROJECTS = ('uniswap-v3', 'uniswap-v4', 'aerodrome-slipstream', 'velodrome-slipstream', 'pancakeswap-amm-v3', 'orca-dex',
               'raydium-amm', 'meteora-dlmm', 'sushiswap-v3', 'camelot-v3', 'algebra', 'project-x', 'hyperswap-v3',
               'pancakeswap-amm-infinity', 'kittenswap-algebra', 'shadow-exchange-clmm', 'blackhole-clmm')


def pair_of(symbol):
    """'WETH-USDC' -> ('ETH', 'USD'); None unless both legs are main assets and the pair is volatile."""
    parts = [p for p in (symbol or '').upper().replace('/', '-').split('-') if p]
    if len(parts) != 2:
        return None
    legs = []
    for t in parts:
        if t in EXTRA_TOKENS:
            legs.append(EXTRA_TOKENS[t])
            continue
        c = asset_class(t)
        if c == 'other' or t not in ({'ETH', 'WETH'} | {'BTC', 'WBTC', 'CBBTC', 'BTCB'} | STABLE_SYMS):
            return None
        legs.append(PAIR_TOKENS[c])
    a, b = sorted(legs, key=lambda x: (x == 'USD', x == 'ETH' and 'BTC' in legs, x))
    if a == b:
        return None
    return (a, b) if (a, b) in PAIR_KLINES else ((b, a) if (b, a) in PAIR_KLINES else None)


def analyze_lvr(out, top=40):
    raw = Path(out) / 'raw'
    pools = ((_read(raw / 'yields' / 'pools.json.gz') or {}).get('data')) or []
    prot = _read(raw / 'llama' / 'protocols.json.gz') or []
    cats = {p.get('slug'): p.get('category') for p in prot if isinstance(p, dict)}
    sig = {}
    for (a, b), sym in PAIR_KLINES.items():
        k = _read(raw / 'klines' / ('%s.json.gz' % sym))
        if isinstance(k, list) and k:
            closes = [float(x[4]) for x in k[-91:]]
            sig[(a, b)] = sigma_annual(closes)
    cands = []
    for p in pools:
        if cats.get(p.get('project')) != 'Dexs' or p.get('exposure') != 'multi' or p.get('stablecoin'):
            continue
        pr = pair_of(p.get('symbol'))
        if not pr or sig.get(pr) is None:
            continue
        tvl = fnum(p.get('tvlUsd'), 0.0)
        fee_apr = (fnum(p.get('apyBase'), 0.0) or 0.0) / 100.0
        if fee_apr <= 0:
            continue  # no fee reading (Curve's crvUSD/BTC Yield Basis pools, idle gauges): nothing to compare
        cands.append({'project': p.get('project'), 'chain': p.get('chain'), 'symbol': p.get('symbol'), 'pair': '%s/%s' % pr,
                      'tvl': tvl, 'fee_apr': fee_apr, 'reward_apr': (fnum(p.get('apyReward'), 0.0) or 0.0) / 100.0,
                      'sigma': sig[pr], 'lvr_full_range_apr': lvr_rate(sig[pr]),
                      'concentrated': p.get('project') in CL_PROJECTS})
    cands.sort(key=lambda r: -r['tvl'])
    sel = cands[:top]
    fees = sum(r['tvl'] * r['fee_apr'] for r in sel)
    lvr_lo = sum(r['tvl'] * r['lvr_full_range_apr'] for r in sel)
    # concentrated pools: a position in a 4x range (half to double) loses 3.4x the full-range LVR per dollar; the TVL's
    # true concentration is unknown here, so this is the upper end of the band, not a measurement
    mult = 1.0 / (1.0 - 4 ** -0.25)
    lvr_hi = sum(r['tvl'] * r['lvr_full_range_apr'] * (mult if r['concentrated'] else 1.0) for r in sel)
    by_pair = collections.defaultdict(lambda: {'tvl': 0.0, 'fees_yr': 0.0, 'lvr_lo_yr': 0.0})
    for r in sel:
        b = by_pair[r['pair']]
        b['tvl'] += r['tvl']
        b['fees_yr'] += r['tvl'] * r['fee_apr']
        b['lvr_lo_yr'] += r['tvl'] * r['lvr_full_range_apr']
    return {'sigma_90d': {'%s/%s' % k: v for k, v in sig.items()}, 'pools': len(sel), 'tvl': sum(r['tvl'] for r in sel),
            'fees_yr': fees, 'lvr_full_range_yr': lvr_lo, 'lvr_concentrated_4x_yr': lvr_hi, 'range_multiplier_4x': mult,
            'kept_share_full_range': 1 - lvr_lo / fees if fees else None, 'kept_share_concentrated_4x': 1 - lvr_hi / fees if fees else None,
            'by_pair': dict(by_pair), 'top_pools': sel[:15]}


def analyze_lending(out, llama_rows, summ):
    raw = Path(out) / 'raw' / 'lending'
    aave = parse_aave_markets(_read(raw / 'aave_markets.json.gz'))
    pages = [(_read(f)) for f in sorted(raw.glob('morpho_markets_*.json.gz'))]
    morpho = parse_morpho(pages)
    def book(rows, apr_key):
        cls = collections.defaultdict(lambda: {'borrow_usd': 0.0, 'interest_yr': 0.0, 'above_fair_yr': 0.0, 'above_fair_clipped_yr': 0.0})
        for r in rows:
            apr = r.get(apr_key)
            if apr is None or r['borrow_usd'] <= 0:
                continue
            c = asset_class(r.get('symbol') or r.get('loan'))
            sp = flow_split(r['borrow_usd'], apr, fair_rate(c))
            e = cls[c]
            e['borrow_usd'] += r['borrow_usd']
            e['interest_yr'] += sp['gross']
            e['above_fair_yr'] += sp['above_fair']
            e['above_fair_clipped_yr'] += sp['above_fair_clipped']
        tot = {k: sum(v[k] for v in cls.values()) for k in ('borrow_usd', 'interest_yr', 'above_fair_yr', 'above_fair_clipped_yr')}
        return {'by_class': {k: dict(v, mean_apr=v['interest_yr'] / v['borrow_usd'] if v['borrow_usd'] else None) for k, v in cls.items()},
                'total': tot}
    # Morpho: drop markets whose borrow APY is not a rate (> 200%) or whose USD figures are not priced (borrow > supply)
    m_ok = []
    m_bad = 0
    for r in morpho:
        apy = r['borrow_apy']
        if apy is None or apy > 2.0 or r['borrow_usd'] > r['supply_usd'] * 1.001 + 1:
            m_bad += 1
            continue
        m_ok.append(dict(r, borrow_apr=apy_to_apr(apy)))
    a_book = book(aave, 'borrow_apr')
    m_book = book(m_ok, 'borrow_apr')
    # check: Aave's own reserves (borrowed x APR, now) against DefiLlama's aave-v3 fees (last 30 days), Ethereum and all
    a_eth = sum(r['borrow_usd'] * r['borrow_apr'] for r in aave if r['chain_id'] == 1 and r['borrow_apr'] is not None)
    a_all = a_book['total']['interest_yr']
    ll = (summ.get('aave-v3') or {}).get('dailyFees') or {}
    ll_sup = (summ.get('aave-v3') or {}).get('dailySupplySideRevenue') or {}
    ll_eth = (ll.get('by_chain_30d_yr') or {}).get('ethereum') or (ll.get('by_chain_30d_yr') or {}).get('Ethereum')
    check = {'aave_api_interest_ethereum_yr': a_eth, 'defillama_aave_v3_fees_ethereum_30d_yr': ll_eth,
             'ratio_ethereum': (ll_eth / a_eth) if ll_eth and a_eth else None,
             'aave_api_interest_all_chains_yr': a_all, 'defillama_aave_v3_fees_30d_yr': ll.get('run_rate_30d'),
             'ratio_all': (ll.get('run_rate_30d') / a_all) if ll.get('run_rate_30d') and a_all else None,
             'defillama_aave_v3_supply_side_30d_yr': ll_sup.get('run_rate_30d'),
             'aave_api_supply_interest_yr': sum((r['supply_usd'] or 0) * (r['supply_apr'] or 0) for r in aave)}
    lend = pool_totals(llama_rows, 'lending')
    # class shares measured on Aave + Morpho, applied to DefiLlama's lending total (a band: Aave alone vs both)
    comb = collections.defaultdict(float)
    for b in (a_book, m_book):
        for c, v in b['by_class'].items():
            comb[c] += v['interest_yr']
    ctot = sum(comb.values())
    shares = {c: v / ctot for c, v in comb.items()} if ctot else {}
    af_share = (a_book['total']['above_fair_clipped_yr'] + m_book['total']['above_fair_clipped_yr']) / ctot if ctot else None
    shares_by_src = {k: (b['total']['above_fair_clipped_yr'] / b['total']['interest_yr']) if b['total']['interest_yr'] else None
                     for k, b in (('aave', a_book), ('morpho', m_book))}
    return {'aave': a_book, 'morpho': dict(m_book, markets_used=len(m_ok), markets_dropped=m_bad),
            'class_share_of_interest': shares, 'above_fair_clipped_share_of_interest': af_share, 'above_fair_shares': shares_by_src,
            'defillama_lending': lend, 'check_aave': check,
            'aave_reserves_with_borrow': sum(1 for r in aave if r['borrow_usd'] > 0),
            'top_aave': sorted(({'market': r['market'], 'symbol': r['symbol'], 'borrow_usd': r['borrow_usd'], 'borrow_apr': r['borrow_apr']}
                                for r in aave if r['borrow_usd'] > 0), key=lambda r: -r['borrow_usd'])[:12],
            'top_morpho': sorted(({'loan': r['loan'], 'collateral': r['collateral'], 'chain_id': r['chain_id'], 'borrow_usd': r['borrow_usd'],
                                   'borrow_apr': r['borrow_apr']} for r in m_ok), key=lambda r: -r['borrow_usd'])[:12]}



# ---------------------------------------------------------------------------------------------- analyze: queues, points

UNIT_FAIR = {'ETH': ETH_FAIR, 'BTC': 0.0, 'USD': SSR}


def _queue_asset(name, a, days, src):
    wait = (a.get('wait') or {}).get('median_days') or 0.0
    fair = UNIT_FAIR.get(a.get('unit'), SSR)
    g = af = sell = 0.0
    for pool, b in (a.get('by_pool') or {}).items():
        if not b.get('sell_volume_usd') or b.get('vw_discount_bps') is None:
            continue
        q = queue_rent(b['sell_volume_usd'], b['vw_discount_bps'], b.get('fee_bps') or 1.0, wait, fair, days)
        g += q['gross']
        af += q['above_fair']
        sell += b['sell_volume_usd']
    row = {'asset': name, 'label': a.get('label'), 'unit': a.get('unit'), 'wait_days': wait, 'window_days': days, 'source': src,
           'sell_usd_per_year': annualise(sell, days), 'gross_yr': g, 'above_fair_yr': af,
           'book_capacity_usd': a.get('capacity_usd'), 'oos_usd_per_year_at_capacity': a.get('oos_usd_per_year_at_capacity')}
    wk = a.get('weekly_by_pool')
    if wk and a.get('volume_usd'):
        share = (a.get('sell_volume_usd') or 0.0) / a['volume_usd']
        weeks = sorted(wk)[-13:]
        gg = ff = 0.0
        fees = {k: (v.get('fee_bps') or 1.0) for k, v in (a.get('by_pool') or {}).items()}
        fair_bp = fair * wait / 365.0 * 1e4
        for w in weeks:
            for pool, (vw, vol, _n) in wk[w].items():
                if vw is None:
                    continue
                gg += vol * share * vw / 1e4
                ff += vol * share * max(0.0, vw - fees.get(pool, 1.0) - fair_bp) / 1e4
        row.update({'trailing_91d_gross_yr': annualise(gg, 7 * len(weeks)), 'trailing_91d_above_fair_yr': annualise(ff, 7 * len(weeks))})
    return row


def analyze_queues(out):
    red = _read_json(REDEMPTION)
    ext = _read_json(QUEUE_EXT)
    book = _read_json(ROOT / 'research/2026-10-10/queue_book/analysis.json')
    alt = _read_json(ROOT / 'research/2026-10-10/queue_bids_alt/screen.json')
    rows = []
    if red:
        for k, a in red['assets'].items():
            rows.append(_queue_asset(k, a, red['days'], 'redemption_history (2026-03-13 to 2026-10-09)'))
    if ext:
        w = ext.get('new_assets_window') or {}
        t0 = dt.datetime.fromisoformat(w['first_utc'].replace('Z', '+00:00'))
        t1 = dt.datetime.fromisoformat(w['last_utc'].replace('Z', '+00:00'))
        days = (t1 - t0).total_seconds() / 86400
        for k in ('lbtc', 'tbtc', 'oeth'):
            if k in ext['new_assets']:
                rows.append(_queue_asset(k, ext['new_assets'][k], days, 'queue_bids_ext (2024-09-26 to 2026-10-09)'))
    eth_like = [r for r in rows if r['wait_days'] > 0.05]
    res = {'assets': rows,
           'queued_total_gross_yr': sum(r['gross_yr'] for r in eth_like),
           'queued_total_above_fair_yr': sum(r['above_fair_yr'] for r in eth_like),
           'queued_trailing_91d_gross_yr': sum(r.get('trailing_91d_gross_yr') or 0.0 for r in eth_like if 'trailing_91d_gross_yr' in r),
           'instant_controls_gross_yr': sum(r['gross_yr'] for r in rows if r['wait_days'] <= 0.05)}
    if book:
        j = (book.get('joint') or {}).get('all4') or {}
        res['queue_book'] = {'window': book.get('window'), 'days': book.get('days'),
                             'joint_oos_usd_per_year': {k: (v or {}).get('out_of_sample_usd_per_year') for k, v in j.items()},
                             'peak_locked_unbounded_usd': (book.get('overlap') or {}).get('peak_of_sum_usd'),
                             'peak_day_utc': (book.get('overlap') or {}).get('peak_day_utc'),
                             'p90_locked_unbounded_usd': (book.get('overlap') or {}).get('p90_of_sum_usd'),
                             'late_entry_1h_15m': (book.get('late_entry') or {}).get('all4|15000000|1h')}
    if alt:
        tot = collections.defaultdict(float)
        for r in alt.get('rows') or []:
            tot[r.get('network')] += fnum(r.get('vol24_native_pairs_usd'), 0.0) or 0.0
        vol = sum(tot.values())
        # unmeasured discounts: band from the Ethereum queues' volume-weighted discounts net of fees (5 to 25 bp)
        res['off_ethereum'] = {'at': alt.get('at'), 'vol24_native_pairs_usd': vol, 'by_network': dict(sorted(tot.items(), key=lambda kv: -kv[1])),
                               'sell_usd_per_year_assumed_half': vol * 365 / 2,
                               'gross_yr_band': [vol * 365 / 2 * 5e-4, vol * 365 / 2 * 25e-4],
                               'source': 'research/2026-10-10/queue_bids_alt/screen.json (sibling worker, GeckoTerminal 24h volume)'}
    return res


def _read_json(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else None


def analyze_pendle(out):
    raw = Path(out) / 'raw' / 'pendle'
    pa = _read_json(PENDLE_DIR / 'analysis.json') or {}
    points = {x['key']: x.get('points') for x in pa.get('live') or []}
    cls_live = {x['key']: x.get('cls') for x in pa.get('live') or []}
    lists = {}
    for f in (PENDLE_DIR / 'raw' / 'lists').glob('*_active.json'):
        cid = int(f.name.split('_')[0])
        for m in json.loads(f.read_text()).get('markets') or []:
            lists['%d-%s' % (cid, m['address'])] = m
    per = []
    miss = collections.Counter()
    for f in sorted(raw.glob('yt_supply_*.json.gz')):
        d = _read(f)
        if failed(d):
            miss['chain_unread'] += 1
            continue
        cid = d['chain_id']
        for addr, m in (d.get('markets') or {}).items():
            key = '%d-%s' % (cid, addr)
            if m.get('total_supply_raw') is None or m.get('decimals') is None:
                miss['supply_unread'] += 1
                continue
            meta = _read_json(PENDLE_DIR / 'raw' / 'meta' / ('%s.json' % key))
            body = (meta or {}).get('body') or {}
            px = fnum(((body.get('accountingAsset') or {}).get('price') or {}).get('usd')) or \
                fnum(((body.get('basePricingAsset') or {}).get('price') or {}).get('usd'))
            hp = PENDLE_DIR / 'raw' / 'hist' / ('%s.json.gz' % key)
            hist = ((_read(hp) or {}).get('body') or {}).get('results') if hp.exists() else None
            if not px or not hist:
                miss['no_price_or_history'] += 1
                continue
            last = hist[-1]
            r30 = [fnum(x.get('underlyingApy')) for x in hist[-30:] if fnum(x.get('underlyingApy')) is not None]
            r7 = [fnum(x.get('underlyingApy')) for x in hist[-7:] if fnum(x.get('underlyingApy')) is not None]
            implied = fnum(last.get('impliedApy'))
            if implied is None or not r30:
                miss['no_rates'] += 1
                continue
            notional = m['total_supply_raw'] / 10 ** m['decimals'] * px
            cats = (lists.get(key) or {}).get('categoryIds') or []
            per.append({'key': key, 'name': m.get('name'), 'expiry': (m.get('expiry') or '')[:10], 'yt_notional_usd': notional,
                        'implied': implied, 'realised_30d': statistics.fmean(r30), 'realised_7d': statistics.fmean(r7) if r7 else None,
                        'premium_yr': yt_premium(notional, implied, statistics.fmean(r30)),
                        'points': points.get(key), 'cls': cls_live.get(key) or (cats[0] if cats else None),
                        'pool_tvl_usd': fnum(last.get('tvl'))})
    pos = sum(max(0.0, r['premium_yr']) for r in per)
    net = sum(r['premium_yr'] for r in per)
    net7 = sum(yt_premium(r['yt_notional_usd'], r['implied'], r['realised_7d']) for r in per if r['realised_7d'] is not None)
    notional = sum(r['yt_notional_usd'] for r in per)
    by_pts = collections.defaultdict(lambda: {'notional': 0.0, 'premium_yr': 0.0, 'markets': 0})
    for r in per:
        k = {True: 'points', False: 'no_points'}.get(r['points'], 'unknown')
        by_pts[k]['notional'] += r['yt_notional_usd']
        by_pts[k]['premium_yr'] += r['premium_yr']
        by_pts[k]['markets'] += 1
    return {'markets': len(per), 'missing': dict(miss), 'yt_notional_usd': notional, 'premium_net_yr': net, 'premium_net_7d_yr': net7,
            'premium_positive_yr': pos, 'premium_on_notional': net / notional if notional else None,
            'by_points': dict(by_pts), 'history_points_premium': pa.get('points_premium'),
            'top': sorted(per, key=lambda r: -abs(r['premium_yr']))[:15], 'per_market': per}



# ---------------------------------------------------------------------------------------------- the map

METAL_NAMES = ('GOLD', 'SILVER', 'XAU', 'XAG', 'XAUT', 'PAXG', 'COPPER', 'PLATINUM', 'PALLADIUM')


def is_metal(coin):
    base = coin.split(':', 1)[-1].upper().replace('-USDT-SWAP', '').replace('-USD-SWAP', '')
    for q in ('USDT', 'USDC', 'PERP'):
        if base.endswith(q) and len(base) > len(q):
            base = base[:-len(q)]
    return base in METAL_NAMES


def metals(sections):
    """Gold, silver and other metal perps on every venue: their oracles follow spot (roll_carry.py: xyz:GOLD and SILVER
    do not roll), so their funding is a leverage rent, and tokenized gold (PAXG, XAUT) is a 24/7 spot leg."""
    rows = []
    for venue in ('hl', 'binance', 'bybit', 'okx'):
        for r in sections[venue]['per_market']:
            if r['cls'] == 'metal':
                rows.append(dict({k: r[k] for k in ('coin', 'oi_usd', 'rate_30d', 'rate_90d', 'net_30d', 'longs_paid_30d',
                                                       'above_fair_30d')}, venue=venue))
    agg = {'markets': len(rows), 'oi_usd': sum(r['oi_usd'] for r in rows), 'net_30d': sum(r['net_30d'] for r in rows),
           'longs_paid_30d': sum(r['longs_paid_30d'] for r in rows), 'above_fair_30d': sum(r['above_fair_30d'] for r in rows),
           'above_fair_90d': sum(flow_split(r['oi_usd'], r['rate_90d'], SSR)['above_fair'] for r in rows)}
    agg['oi_weighted_rate_30d'] = agg['net_30d'] / agg['oi_usd'] if agg['oi_usd'] else None
    return {'aggregate': agg, 'markets': sorted(rows, key=lambda r: -r['oi_usd'])}


def band(*xs):
    v = [x for x in xs if x is not None]
    return [min(v), max(v)] if v else [None, None]


def mid(b):
    return None if b[0] is None else (b[0] + b[1]) / 2.0


# Who pays, why, who collects, what is scarce, how fast capital arrives, and what this repo already did -- the parts of
# each row that are judgement rather than arithmetic, kept apart from the numbers so either can be audited.
NOTES = {
    'funding_hl_crypto': dict(
        payer='leveraged longs on Hyperliquid (retail and on-chain natives; no KYC, high leverage, one wallet)',
        motive='leverage on a self-custodial venue; they pay ~9-10%/yr for BTC/ETH that cost ~4.4% on Binance',
        collector='HL shorts: market makers and basis desks hedging on CEX (two-venue capital), HYPE spot holders, HLP',
        scarce='HL-native spot inventory as portfolio-margin collateral (PM cap 200 BTC a user; UBTC depth ~$2M within 25bp), or cheap capital on two venues',
        contestability='medium: the HL-Binance spread has persisted for years because two-venue capital costs about as much (funding_arb)',
        repo='term_carry: HYPE spot-perp carry go (+4.30%/yr, $5M); BTC/ETH watch (t < 1 since 2025-11); funding_arb: HL vs Binance no-go at size',
        access=(0.0003, 0.0015), coverage=0.8),
    'funding_cex_crypto': dict(
        payer='leveraged longs on Binance, Bybit and OKX', motive='leverage demand; funding sits near the 0.01%/8h formula rate',
        collector="basis desks and Ethena's ~delta-neutral book (Ethena's fees ~$276M/yr include its funding), market makers",
        scarce='none beyond capital: BTC/ETH funding (4.1-5.0%) is within ~1pp of the savings rate',
        contestability='high: billions of basis capital arrive within days; altcoin excess lives in thin and new books',
        repo='term_carry: DIY Ethena on Binance no-go; funding_arb: altcoin spreads in sub-$5k books; listing_lifecycle: delisting spread earned weeks before notices',
        access=(0.0, 0.0005), coverage=0.9),
    'funding_metals': dict(
        payer='leveraged longs in gold and silver perps (HL xyz, Binance, OKX, Bybit)',
        motive='24/7 leveraged metal exposure from a crypto account (a broker barrier, like the equity carry)',
        collector='unknown: no basis desk is visible; Binance TradFi perps have no interest floor (46% of XAU settlements zero)',
        scarce='a tokenized spot leg (PAXG/XAUT, 24/7, KYC to mint/redeem) and its depth; venue access (Binance TradFi perps non-US)',
        contestability='low-medium: the spot leg is on chain and liquid in size; the oracles follow spot (xyz GOLD/SILVER do not roll)',
        repo='tradfi_perps: perp-perp metals pair (HL vs Binance) gold +2.9%, never traded; no test of perp vs tokenized spot',
        access=(0.004, 0.012), coverage=0.2),
    'funding_hip3_equity': dict(
        payer='leveraged longs in HIP-3 equity and index perps (trade.xyz and others)',
        motive='24/7 leveraged US-equity exposure without a broker; off-hours price discovery',
        collector='HIP-3 shorts: market makers hedging at brokers in US hours',
        scarce='a broker account (cash-equity hedge) and tolerance for off-hours gap risk',
        contestability='medium: needs a broker plus HL margin; books are thin outside the top names',
        repo='equity_offhours: thin go; tradfi_perps: Binance TradFi hedge no-go; book re-quoted $330k -> $54-73k/yr',
        access=(0.0004, 0.001), coverage=0.9),
    'funding_roll': dict(
        payer='holders of energy perps (oil, gas) whose oracles roll on the GSCI schedule',
        motive='none: the funding pays each roll step (0.89-0.97 of it), a calendar price', collector='the other side of the roll',
        scarce='-', contestability='priced', repo='roll_carry: retired ($2.84M/yr line)', access=(0.0, 0.0), coverage=1.0),
    'perp_venue_fees': dict(
        payer='perp traders: taker and maker fees, HIP-3 deployer fees, front-end builder codes',
        motive='leverage and venue convenience; front-ends charge for distribution (wallet perps: MetaMask, Phantom, Trust)',
        collector='venue token holders (HYPE buybacks take 99% of HL fees), front-ends, and LP vaults (supply side)',
        scarce='a venue or a distribution channel; for LP vaults: tolerance for trader PnL and directional exposure',
        contestability='LP vaults are open to any depositor (pro-rata), venue fees are not',
        repo='none on LP vaults (house_vaults, a sibling study, sizes trader-PnL transfers); usdg-captive-flow-lp is the DEX analogue',
        access=(0.01, 0.05), coverage=0.3),
    'incentives': dict(
        payer='issuers and protocols buying deposits (Ethena loop programs, Sky, Spark, Usual, PayPal PYUSD, Ripple RLUSD, Robinhood USDG)',
        motive='marketing: growth of a stablecoin float or a market, paid from a fixed budget',
        collector='depositors in rewarded vaults and markets, pro-rata; curators route flows',
        scarce='attention (campaigns change weekly), eligibility (KYC: "Robinhood users only"; looping required), tolerance for the issuer\'s credit',
        contestability='high in capital, low in attention: a fixed budget dilutes as deposits arrive, but each campaign must be found and read',
        repo='stacyvault-reward-harvest retired; usdg-captive-flow-lp fork-proven ($150k); brainstorm 5.4 incentive-adjusted dollar yields is next (incentive_yields sibling)',
        access=(0.005, 0.02), coverage=0.3),
    'dex_lp': dict(
        payer='memecoin and retail swappers (PumpSwap, Meteora, Raydium, Uniswap v4 on Base) and, on major pairs, informed flow',
        motive='entertainment and speed of access to new tokens; on majors the flow is mostly arbitrage, which takes LVR from LPs',
        collector='LPs; on memecoin pools much of the liquidity is protocol-seeded and locked',
        scarce='inventory in a decaying token (memecoins), or the ability to beat LVR (on majors: none without speed)',
        contestability='high and racing at launch (JIT, sniping); on majors fees are below LVR for concentrated positions',
        repo='jit-liquidity-mainnet retired; usdg-captive-flow-lp fork-proven (captive subsidized flow is the exception); listing_lifecycle: new tokens decay -25%/-33% at 30/60 days',
        access=(0.0, 0.002), coverage=0.5),
    'lending': dict(
        payer='borrowers: dollar loopers (sUSDe, PT and LST carry), market makers (Maple), CDP vaults (Sky)',
        motive='leverage on a carry; borrowing dollars against crypto without selling',
        collector='suppliers (after the reserve factor) and protocols',
        scarce='none beyond dollars: supply rates sit at or near the savings rate',
        contestability='high: dollars arrive within hours; above-fair rents are the price of credit risk',
        repo='multichain/strategy book: only 2 of 27 dollar reserves beat SSR (~$1M wide); cross-chain book $109k/yr; dollar PTs vs SSR died on defaults',
        access=(0.0003, 0.001), coverage=0.9),
    'queues': dict(
        payer='holders of queued claims (stETH, weETH, rsETH, LBTC, tBTC) who will not wait days for a redemption',
        motive='impatience: immediate liquidity, mostly in stress weeks', collector='DEX LPs, arbitrage bots, queue bidders',
        scarce='capital that can sit locked in a queue for days to weeks', contestability='medium: few bidders, capital lock is the barrier',
        repo='dislocation_history + queue_bids_ext + queue_book: combined $15M book $409,889/yr out of sample; off-Ethereum screen (queue_bids_alt) running',
        access=(0.02, 0.10), coverage=0.9),
    'points': dict(
        payer='YT buyers on Pendle (points and airdrop speculation, rate bets)', motive='points: a non-price payoff',
        collector='PT holders (fixed-rate buyers, Morpho/Aave PT loopers) and Pendle LPs',
        scarce='duration and patience to hold a PT to maturity', contestability='medium: PT capacity is the market depth',
        repo='pendle_history: PT-over-floating switch go ($216k/yr); points markets median implied - trailing 4.3% vs 1.8%; Boros no-go',
        access=(0.003, 0.01), coverage=0.9),
    'entertainment': dict(
        payer='memecoin launch and trading-app users, prediction-market bettors, gamers',
        motive='entertainment', collector='the platforms (pump.fun, trading bots, Polymarket, Kalshi)', scarce='the platform itself',
        contestability='not contestable by capital (owned); edges inside it are speed games',
        repo='polymarket_history, pm_crossvenue: no-go (favourites, neg-risk, lags automated)', access=(0.0, 0.0), coverage=0.6),
    'attention': dict(
        payer='passive depositors in curated vaults and yield aggregators', motive='convenience: not choosing markets',
        collector='curators and managers (performance fees)', scarce='reputation and distribution', contestability='slow (reputation)',
        repo='none (not a trade)', access=(0.0, 0.0), coverage=0.0),
}


def build_map(A):
    hl, bn, by, ok = A['funding']['hl'], A['funding']['binance'], A['funding']['bybit'], A['funding']['okx']
    ratio_b = (hl['checks'].get('ratio_b_over_a') or 1.0)
    hl_main = hl['aggregates']['by_dex'].get('main') or {}
    rows = []

    def add(key, name, size, net, above, above_band, size_band, method):
        n = NOTES[key]
        acc = [above_band[0] * n['access'][0] if above_band[0] is not None else None,
               above_band[1] * n['access'][1] if above_band[1] is not None else None]
        rows.append({'key': key, 'name': name, 'size_yr': size, 'size_band': size_band, 'net_yr': net, 'above_fair_yr': above,
                     'above_fair_band': above_band, 'accessible_share': list(n['access']), 'accessible_yr': acc,
                     'coverage': n['coverage'], 'method': method,
                     **{k: n[k] for k in ('payer', 'motive', 'collector', 'scarce', 'contestability', 'repo')}})

    # 1. funding
    mt = A['funding']['metals']['aggregate']
    hl_metal = sum(r['above_fair_30d'] for r in A['funding']['metals']['markets'] if r['venue'] == 'hl')
    hl_metal_long = sum(r['longs_paid_30d'] for r in A['funding']['metals']['markets'] if r['venue'] == 'hl')
    hc = [r for r in hl['per_market'] if r['dex'] == 'main' and r['cls'] == 'crypto']
    hl_main = {k: sum(r[k] for r in hc) for k in ('longs_paid_30d', 'net_30d', 'above_fair_30d', 'above_fair_90d', 'oi_usd')}
    a30, a90 = hl_main['above_fair_30d'], hl_main['above_fair_90d']
    add('funding_hl_crypto', 'Hyperliquid main-dex crypto perps', hl_main['longs_paid_30d'], hl_main['net_30d'], a30,
        band(min(a30, a90) * ratio_b, max(a30, a90)), band(hl_main['longs_paid_30d'] * ratio_b, hl_main['longs_paid_30d']),
        "venue OI now x trailing 30d (and 90d) hourly funding from the repo's store; low end x0.90, the realised/current-OI ratio of path B")
    cc = {v: A['funding'][v]['aggregates']['by_cls'].get('crypto') or {} for v in ('binance', 'bybit', 'okx')}
    cex_long = sum(c.get('longs_paid_30d', 0.0) for c in cc.values())
    cex_net = sum(c.get('net_30d', 0.0) for c in cc.values())
    cex_af = sum(c.get('above_fair_30d', 0.0) for c in cc.values())
    cex_af_hi = cc['binance'].get('above_fair_30d', 0.0) + by['extrapolated']['above_fair_30d'] + ok['extrapolated']['above_fair_30d']
    cex_af_90 = sum(c.get('above_fair_90d', 0.0) for c in cc.values())
    cex_long_hi = cc['binance'].get('longs_paid_30d', 0.0) + by['extrapolated']['longs_paid_30d'] + ok['extrapolated']['longs_paid_30d']
    add('funding_cex_crypto', 'Binance (top 100 by OI), Bybit and OKX (top 30 each) crypto perps', cex_long, cex_net, cex_af,
        band(cex_af, cex_af_hi, cex_af_90), band(cex_long, cex_long_hi),
        'Binance: daily OI history x every settlement of the last 30 days (realised); Bybit/OKX: OI now x last 30 days of settlements, tail extrapolated at the covered rate (high end)')
    add('funding_metals', 'Gold, silver and other metal perps (all four venues)', mt['longs_paid_30d'], mt['net_30d'], mt['above_fair_30d'],
        band(mt['above_fair_30d'], mt['above_fair_90d']), band(mt['longs_paid_30d'] * 0.8, mt['longs_paid_30d']),
        'per-market OI x 30d (and 90d) funding on each venue, spot-following oracles; above fair against SSR')
    eq = hl['aggregates']['by_cls']
    e_af = sum((eq.get(c) or {}).get('above_fair_30d', 0.0) for c in ('equity', 'index'))
    e_af90 = sum((eq.get(c) or {}).get('above_fair_90d', 0.0) for c in ('equity', 'index'))
    e_long = sum((eq.get(c) or {}).get('longs_paid_30d', 0.0) for c in ('equity', 'index'))
    e_net = sum((eq.get(c) or {}).get('net_30d', 0.0) for c in ('equity', 'index'))
    bn_eq = {k: v for k, v in bn['aggregates']['by_cls'].items() if 'equity' in k}
    add('funding_hip3_equity', 'HIP-3 equity and index perps (+ Binance TradFi equity perps)',
        e_long + sum(v['longs_paid_30d'] for v in bn_eq.values()), e_net + sum(v['net_30d'] for v in bn_eq.values()),
        e_af + sum(v['above_fair_30d'] for v in bn_eq.values()),
        band(e_af + sum(v['above_fair_30d'] for v in bn_eq.values()), e_af90 + sum(v['above_fair_90d'] for v in bn_eq.values()),
             sum((eq.get(c) or {}).get('above_fair_30d_clipped', 0.0) for c in ('equity', 'index')) + sum(v['above_fair_30d_clipped'] for v in bn_eq.values())),
        band(e_long, e_long + sum(v['longs_paid_30d'] for v in bn_eq.values())),
        'HL venue OI x store funding (30/90d) plus Binance TradFi equity perps (realised 30d); clipped per market at the high end')
    roll = [r for r in A['funding']['hl']['per_market'] if not r['rent']]
    bn_roll = [r for r in bn['per_market'] if r['cls'].startswith('tradfi_commodity') and not is_metal(r['coin'])]
    add('funding_roll', 'Energy perps (oil, gas): funding is the roll', sum(abs(r['net_30d']) for r in roll + bn_roll),
        sum(r['net_30d'] for r in roll + bn_roll), 0.0, [0.0, 0.0],
        band(sum(abs(r['net_30d']) for r in roll + bn_roll), sum(abs(r['net_90d']) for r in roll + bn_roll)),
        'excluded from rent: the oracle steps on the GSCI calendar and funding pays the step (roll_carry.py)')
    # 2. perp venue fees
    pv = A['llama']['pools']['perp_vaults']
    lpv = A['perp_vaults']
    add('perp_venue_fees', 'Perp venue fees (DefiLlama Derivatives + perp front-ends)', pv['fees_yr'], pv['supply_side_yr'],
        lpv['lp_vault_above_fair_yr'], band(lpv['lp_vault_above_fair_yr'] * 0.5, lpv['lp_vault_above_fair_yr']),
        band(min(pv['fees_yr'], pv['fees_1y']), max(pv['fees_yr'], pv['fees_1y'])),
        'DefiLlama 30d fees x 365/30 (band: trailing 365 days); "above fair" = LP-vault fee income above SSR on vault TVL (named vaults only)')
    # 3. incentives
    inc = A['incentives']
    add('incentives', 'Incentive budgets paid to depositors', inc['headline_yr'], inc['headline_yr'], inc['headline_yr'],
        band(inc['headline_yr'], inc['union_with_merkl_yr'] + inc['outlier_flagged_below_cap_yr']),
        band(inc['headline_yr'], inc['union_with_merkl_yr'] + inc['outlier_flagged_below_cap_yr']),
        'sum tvlUsd x apyReward over DefiLlama yield pools (outliers, >300% APR and pass-through vaults excluded); high end adds Merkl campaigns DefiLlama does not see and flagged pools under 50% APR')
    # 4. DEX LP
    dx = A['llama']['pools']['dex_lp']
    lvr = A['lvr']
    add('dex_lp', 'DEX LP fees (supply side)', dx['supply_side_yr'], dx['supply_side_yr'], 0.0,
        band(0.0, 0.0), band(dx['supply_side_1y'], dx['supply_side_yr']),
        'DefiLlama supply-side revenue of Dexs, 30d x 365/30 (band low end: the trailing 365 days at the same supply share); above fair is not defined: memecoin LPs hold decaying inventory and major-pair LPs pay LVR (%.0f%% to %.0f%% of fees on the main pairs)'
        % (100 * (1 - (lvr.get('kept_share_full_range') or 0)), 100 * (1 - (lvr.get('kept_share_concentrated_4x') or 0))))
    # 5. lending
    ln = A['lending']
    tot = ln['defillama_lending']['fees_yr']
    shares = ln['above_fair_shares']
    add('lending', 'Lending and CDP interest paid by borrowers', tot, ln['defillama_lending']['supply_side_yr'],
        tot * ln['above_fair_clipped_share_of_interest'], band(tot * shares['aave'], tot * shares['morpho']),
        band(ln['defillama_lending']['fees_1y'], tot),
        "DefiLlama Lending+CDP fees, 30d x 365/30; above fair = share of interest above each class's fair rate (SSR for dollars, staking for ETH), measured on Aave's and Morpho's own APIs (band: Aave-only to Morpho-only share)")
    # 6. queues
    q = A['queues']
    off = (q.get('off_ethereum') or {}).get('gross_yr_band') or [0.0, 0.0]
    add('queues', 'Queue impatience: LST/LRT and BTC-wrapper discounts x sell volume', q['queued_total_gross_yr'] + mid(off),
        q['queued_total_gross_yr'], q['queued_total_above_fair_yr'],
        band(q['queued_trailing_91d_gross_yr'] * 0.85, q['queued_total_above_fair_yr'] + off[1]),
        band(q['queued_trailing_91d_gross_yr'] + off[0], q['queued_total_gross_yr'] + off[1]),
        'repo histories: sell volume x volume-weighted discount per pool (210-day and 743-day windows), above fair after the pool fee and the time value of the queue; low end the last 13 weeks; off-Ethereum LSTs from a 24h volume screen at 5-25bp')
    # 7. points
    pe = A['pendle']
    add('points', 'Points speculation: Pendle YT premium (implied - realised) on YT outstanding', pe['premium_positive_yr'],
        pe['premium_net_yr'], pe['premium_net_yr'], band(pe['premium_net_yr'], pe.get('premium_net_7d_yr'), pe['premium_positive_yr']),
        band(pe['premium_net_yr'], pe['premium_positive_yr']),
        'YT totalSupply() on chain x accounting-asset price x (implied APY - trailing 30d underlying APY), 85 active markets')
    # 8. entertainment and attention (scale; not strategies)
    en = A['llama']['pools']['entertainment']
    add('entertainment', 'Entertainment platforms: launchpads, trading apps, prediction markets', en['fees_yr'], en['fees_yr'], 0.0,
        [0.0, 0.0], band(en['fees_1y'], en['fees_yr']), 'DefiLlama fees of the categories, 30d x 365/30')
    at = A['llama']['pools']['attention']
    add('attention', 'Manager and curator fees (the take, not the yield passed through)', at['revenue_yr'], at['revenue_yr'], 0.0,
        [0.0, 0.0], band(at['revenue_yr'] * 0.8, at['revenue_yr']), 'DefiLlama revenue of curator, aggregator and manager categories')
    rows.sort(key=lambda r: -(r['size_yr'] or 0))
    return rows


def rank(rows, A):
    """Under-contested pools: large rent above fair, a scarce resource patient capital can supply, little repo coverage.
    score = mid(above-fair band) x mid(accessible share) x (1 - coverage); the order is a guide, the reasons are in NOTES."""
    out = []
    for r in rows:
        af = mid(r['above_fair_band']) or 0.0
        acc = mid(r['accessible_share'])
        out.append({'key': r['key'], 'name': r['name'], 'above_fair_mid_yr': af, 'accessible_share_mid': acc,
                    'coverage': r['coverage'], 'score_yr': max(0.0, af) * acc * (1 - r['coverage']),
                    'accessible_mid_yr': max(0.0, af) * acc})
    out.sort(key=lambda x: -x['score_yr'])
    return out



def analyze_perp_vaults(out, rows, tabs, hlp):
    """LP-vault income at the perp venues whose DefiLlama methodology says the supply side goes to liquidity providers
    or a vault, against each vault's TVL (DefiLlama /protocols): fee APR and the part above SSR."""
    prot = {p.get('slug'): p for p in (_read(Path(out) / 'raw' / 'llama' / 'protocols.json.gz') or []) if isinstance(p, dict)}
    meth = {}
    for p in (_read(Path(out) / 'raw' / 'llama' / 'overview_fees_dailyFees.json.gz') or {}).get('protocols') or []:
        mt = p.get('methodology')
        meth[p.get('slug')] = (mt.get('SupplySideRevenue') or '') if isinstance(mt, dict) else str(mt or '')
    vaults = []
    for r in rows:
        if r['pool'] != 'perp_vaults' or not r['supply_side_yr'] or r['supply_side_src'] != 'reported':
            continue
        m = meth.get(r['slug'], '').lower()
        if not any(k in m for k in ('lp', 'liquidity provider', 'vault', 'pool')):
            continue
        if r['slug'] == 'hyperliquid-perps':
            continue  # its supply side is builder-code fees plus HLP's 1% (HLP is its own row)
        tvl = fnum((prot.get(r['slug']) or {}).get('tvl'))
        apr = r['supply_side_yr'] / tvl if tvl else None
        usable = bool(tvl and tvl >= 20e6 and apr is not None and apr <= 1.0)
        vaults.append({'name': r['name'], 'slug': r['slug'], 'supply_side_yr': r['supply_side_yr'], 'tvl_usd': tvl, 'fee_apr': apr,
                       'above_fair_yr': (r['supply_side_yr'] - tvl * SSR) if tvl else None, 'usable': usable,
                       'why_not': None if usable else ('no TVL' if not tvl else ('TVL under $20M' if tvl < 20e6 else 'fee APR over 100%: TVL or fees mis-measured')),
                       'methodology': m[:160]})
    vaults.sort(key=lambda v: -v['supply_side_yr'])
    af = sum(max(0.0, v['above_fair_yr']) for v in vaults if v['usable'])
    return {'lp_vaults': vaults, 'lp_vault_income_yr': sum(v['supply_side_yr'] for v in vaults), 'lp_vault_above_fair_yr': af,
            'lp_vault_income_usable_yr': sum(v['supply_side_yr'] for v in vaults if v['usable']),
            'lp_vault_tvl_usable_usd': sum(v['tvl_usd'] for v in vaults if v['usable']), 'hlp_vault_details': hlp,
            'note': 'fee income only; trader PnL transfers to these vaults are the house_vaults study'}


def hl_fee_check(A, llama_rows):
    """DefiLlama's Hyperliquid perp fees against the venue's own 24h notional volume: the implied fee per unit of volume
    should sit between a maker rebate and taker + maker + builder (about 2 to 12 bp)."""
    vol = sum(r['vlm_usd'] for r in A['funding']['hl']['per_market'])
    r = next((x for x in llama_rows if x['slug'] == 'hyperliquid-perps'), None)
    if not r or not vol:
        return None
    fee_day = r['fees_7d_yr'] / 365.0
    return {'hl_volume_24h_usd': vol, 'defillama_fees_per_day_7d_usd': fee_day, 'implied_fee_bp': fee_day / vol * 1e4,
            'expected_bp': [2.0, 12.0], 'ok': 2.0 <= fee_day / vol * 1e4 <= 12.0}


def double_count_guard(A, llama_rows):
    """Overlaps the census total must not contain, each checked rather than asserted in prose."""
    pools = collections.Counter(str(r['pool']) for r in llama_rows)
    slugs = collections.Counter(r['slug'] for r in llama_rows)
    dup = [s for s, n in slugs.items() if n > 1]
    return {
        'one_pool_per_protocol': not dup, 'duplicate_slugs': dup[:10], 'protocols_by_pool': dict(pools),
        'pendle_only_in_points': all(r['pool'] == 'points' for r in llama_rows if (r['slug'] or '').startswith('pendle')),
        'ethena_not_in_total': all(r['pool'] == 'collector' for r in llama_rows if (r['slug'] or '').startswith('ethena-usde')),
        'incentives_exclude_pass_through_yr': A['incentives']['totals']['pass_through'],
        'incentives_exclude_outliers_yr': A['incentives']['totals']['outlier_flagged'] + A['incentives']['totals']['over_cap'],
        'merkl_used_as_check_only': True,
        'queue_above_fair_net_of_pool_fee': True,
        'funding_not_in_defillama_fees': 'order-book funding is peer to peer and absent from venue fees; GMX/Jupiter borrow fees are in fees and not in funding',
        'dex_supply_side_excludes_voters_and_protocol': True,
        'roll_markets_excluded_from_rent_yr': sum(r['longs_paid_30d'] for r in A['funding']['hl']['per_market'] if not r['rent']),
    }


def census_total(rows):
    """Sum of the rent pools that can be added without overlap (scale-only rows excluded): gross size and above fair."""
    keep = [r for r in rows if r['key'] not in ('entertainment', 'attention', 'funding_roll')]
    return {'pools': [r['key'] for r in keep], 'size_yr': sum(r['size_yr'] or 0.0 for r in keep),
            'above_fair_yr': sum(max(0.0, r['above_fair_yr'] or 0.0) for r in keep),
            'above_fair_band': [sum(max(0.0, r['above_fair_band'][0] or 0.0) for r in keep), sum(max(0.0, r['above_fair_band'][1] or 0.0) for r in keep)],
            'accessible_band': [sum(r['accessible_yr'][0] or 0.0 for r in keep), sum(r['accessible_yr'][1] or 0.0 for r in keep)]}


API_GAPS = [
    'yields.llama.fi/poolsBorrow (borrow totals and rates per pool): HTTP 402, paid plan; borrow-side split taken from the Aave and Morpho APIs instead',
    'api.llama.fi/overview/derivatives (perp volume): HTTP 402, paid; the HL fee check uses the venue\'s own 24h volume',
    'dailyBribesRevenue: the free overview returns no protocols and the Aerodrome/Velodrome summaries carry no chart; ve(3,3) bribes unsized',
    "DefiLlama open interest for 'Hyperliquid Perps' reads 0.64 of the venue's own contexts on the main dex (1.00 on tradeXYZ); the venue's numbers are used",
    'liquidation penalties: no free per-protocol series; unsized (and a racing pool, excluded from the strategy space)',
    'Ethena hedge composition (which venues hold its shorts): not read; Ethena enters only as the collector of its DefiLlama fees',
    'Hyperliquid open-interest history: not served by the API; four stored snapshots (09-08, 09-10, 10-09, 10-10) interpolate path B',
    'Pendle YT supply: active markets of the 2026-10-10 00:02 list only; markets listed later are missing',
    'perp venues beyond HL, Binance, Bybit and OKX (Bitget, Gate, MEXC, Deribit, Aster, Lighter, edgeX): funding unsized',
    'tokenized gold supply (PAXG, XAUT): not in DefiLlama TVL or stablecoins; the spot leg depth is untested',
]


def cmd_analyze(args):
    out = args.out
    llama_rows, tabs = llama_table(out)
    summ = summaries(out)
    A = {'generated': utc(), 'ssr': SSR, 'eth_fair': ETH_FAIR}
    A['funding'] = {'hl': analyze_hl(out), 'binance': analyze_binance(out), 'bybit': analyze_bybit(out), 'okx': analyze_okx(out)}
    A['funding']['metals'] = metals(A['funding'])
    A['llama'] = {'pools': {p: pool_totals(llama_rows, p) for p in ('perp_vaults', 'dex_lp', 'lending', 'points', 'collector',
                                                                    'entertainment', 'attention', 'scale_stable', 'scale_chain',
                                                                    'scale_mev', 'scale_staking', 'scale_rwa', None)},
                  'run_rates': summ}
    A['llama']['pools']['unassigned'] = A['llama']['pools'].pop(None)
    hlp = analyze_hlp(out, llama_rows)
    A['perp_vaults'] = analyze_perp_vaults(out, llama_rows, tabs, hlp)
    A['incentives'] = analyze_incentives(out)
    A['lvr'] = analyze_lvr(out)
    A['lending'] = analyze_lending(out, llama_rows, summ)
    A['queues'] = analyze_queues(out)
    A['pendle'] = analyze_pendle(out)
    st = (_read(Path(out) / 'raw' / 'llama' / 'stablecoins.json.gz') or {}).get('peggedAssets') or []
    usde = next((x for x in st if (x.get('symbol') or '') == 'USDe'), {})
    eth = next((r for r in llama_rows if r['slug'] == 'ethena-usde'), {})
    longs = sum(A['funding'][v]['aggregates']['all']['longs_paid_30d'] for v in ('hl', 'binance')) + \
        A['funding']['bybit']['extrapolated']['longs_paid_30d'] + A['funding']['okx']['extrapolated']['longs_paid_30d']
    A['collectors'] = {'ethena': {'usde_supply_usd': usde.get('circulating_usd'), 'fees_yr': eth.get('fees_yr'),
                                  'fees_1y': eth.get('fees_1y'), 'share_of_longs_paid_4_venues': (eth.get('fees_yr') or 0) / longs if longs else None,
                                  'note': "Ethena's fees include LST staking and reserve yield as well as funding, so its funding share is lower"},
                       'longs_paid_4_venues_yr': longs, 'hlp': hlp}
    A['scale_only'] = {k: {kk: A['llama']['pools'][k][kk] for kk in ('fees_yr', 'fees_1y', 'revenue_yr', 'top')}
                       for k in ('scale_stable', 'scale_staking', 'scale_chain', 'scale_rwa', 'scale_mev')}
    A['scale_only']['stablecoin_supply_usd'] = sum((x.get('circulating_usd') or 0) for x in st)
    A['map'] = build_map(A)
    A['census_total'] = census_total(A['map'])
    A['ranking'] = rank(A['map'], A)
    A['checks'] = {'hl_funding_paths': A['funding']['hl']['checks'], 'aave_api_vs_defillama': A['lending']['check_aave'],
                   'incentives_merkl_vs_defillama': A['incentives']['merkl']['vs_defillama_by_protocol'],
                   'merkl_total_yr': A['incentives']['merkl']['budget_yr'], 'defillama_incentives_headline_yr': A['incentives']['headline_yr'],
                   'hl_fees_vs_volume': hl_fee_check(A, llama_rows)}
    A['double_count'] = double_count_guard(A, llama_rows)
    A['api_gaps'] = API_GAPS
    for v in ('hl', 'binance', 'bybit', 'okx'):
        A['funding'][v]['per_market'] = sorted(A['funding'][v]['per_market'], key=lambda r: -r['oi_usd'])
    write_json(Path(out) / 'analysis.json', A)
    m = Path(out) / 'manifest.json'
    man = json.loads(m.read_text()) if m.exists() else {}
    man['analyze'] = {'generated': A['generated'], 'map_rows': len(A['map']), 'script': 'scripts/rent_map.py'}
    write_json(m, man)
    print(json.dumps({'map': [(r['key'], round((r['size_yr'] or 0) / 1e6, 1), round((r['above_fair_yr'] or 0) / 1e6, 1)) for r in A['map']],
                      'total': {k: v for k, v in A['census_total'].items() if k != 'pools'}}, default=str)[:3000])



# ---------------------------------------------------------------------------------------------- render

def fm(v, unit='M'):
    if v is None:
        return '-'
    if unit == 'M':
        return '$%.1fM' % (v / 1e6) if abs(v) < 1e9 else '$%.2fB' % (v / 1e9)
    if unit == 'pct':
        return '%.2f%%' % (100 * v)
    return str(v)


def fb(b):
    return '%s to %s' % (fm(b[0]), fm(b[1])) if b and b[0] is not None else '-'


def cmd_render(args):
    A = json.loads((Path(args.out) / 'analysis.json').read_text())
    L = ['# Rent map — tables (generated %s; every number from analysis.json)\n' % A['generated'],
         'Fair rate: SSR %.2f%% for dollars, ETH staking %.2f%% for ETH, 0 for BTC and other coins. USD a year at the current '
         'run-rate (30 days unless stated).\n' % (100 * A['ssr'], 100 * A['eth_fair'])]
    L.append('## 1. The map (largest first)\n')
    L.append('| pool | size $/yr (band) | above fair $/yr (band) | accessible share | accessible $/yr | repo coverage |')
    L.append('|---|---:|---:|---:|---:|---:|')
    for r in A['map']:
        L.append('| %s | %s (%s) | %s (%s) | %s-%s | %s | %.0f%% |' % (
            r['name'], fm(r['size_yr']), fb(r['size_band']), fm(r['above_fair_yr']), fb(r['above_fair_band']),
            fm(r['accessible_share'][0], 'pct'), fm(r['accessible_share'][1], 'pct'), fb(r['accessible_yr']), 100 * r['coverage']))
    t = A['census_total']
    L.append('\nCensus total (rows that add without overlap; entertainment, manager fees and energy rolls excluded): size %s, '
             'above fair %s (band %s), accessible %s.\n' % (fm(t['size_yr']), fm(t['above_fair_yr']), fb(t['above_fair_band']), fb(t['accessible_band'])))
    L.append('| pool | payer and motive | collector today | scarce resource | contestability | repo evidence |')
    L.append('|---|---|---|---|---|---|')
    for r in A['map']:
        L.append('| %s | %s: %s | %s | %s | %s | %s |' % (r['key'], r['payer'], r['motive'], r['collector'], r['scarce'], r['contestability'], r['repo']))
    L.append('\n## 2. Ranking of under-contested pools (score = mid above fair x mid accessible share x (1 - coverage))\n')
    L.append('| rank | pool | above fair (mid) | accessible share (mid) | coverage | accessible $/yr (mid) | score $/yr |')
    L.append('|---:|---|---:|---:|---:|---:|---:|')
    for i, r in enumerate(A['ranking'], 1):
        L.append('| %d | %s | %s | %s | %.0f%% | %s | %s |' % (i, r['name'], fm(r['above_fair_mid_yr']), fm(r['accessible_share_mid'], 'pct'),
                                                            100 * r['coverage'], fm(r['accessible_mid_yr']), fm(r['score_yr'])))
    L.append('\n## 3. Perp funding by venue\n')
    L.append('| venue / slice | markets | OI | longs paid | shorts paid | net | above fair 30d (clipped) | above fair 90d | OI-weighted rate |')
    L.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
    for v in ('hl', 'binance', 'bybit', 'okx'):
        ag = A['funding'][v]['aggregates']
        for name, x in [('all', ag['all'])] + [('%s' % k, x) for k, x in ag.get('by_cls', {}).items()] + \
                [('dex ' + k, x) for k, x in ag.get('by_dex', {}).items()]:
            L.append('| %s %s | %d | %s | %s | %s | %s | %s (%s) | %s | %s |' % (
                v, name, x['markets'], fm(x['oi_usd']), fm(x['longs_paid_30d']), fm(x['shorts_paid_30d']), fm(x['net_30d']),
                fm(x['above_fair_30d']), fm(x['above_fair_30d_clipped']), fm(x['above_fair_90d']), fm(x['oi_weighted_rate_30d'], 'pct')))
    for v in ('bybit', 'okx'):
        x = A['funding'][v]
        L.append('\n%s: %d perps, OI %s, history for the top %d (%.0f%% of OI); crypto tail x%.2f gives longs paid %s, above fair %s.' % (
            v, x['symbols_all'], fm(x['oi_all_usd']), x['symbols_history'], 100 * (x['oi_covered_share'] or 0), x['crypto_tail_scale'],
            fm(x['extrapolated']['longs_paid_30d']), fm(x['extrapolated']['above_fair_30d'])))
    L.append('\nHyperliquid: top markets by |above fair| (30d)\n')
    L.append('| market | class | OI | rate now | 7d | 30d | 90d | hours at 0.00125%/h (30d) | above fair 30d |')
    L.append('|---|---|---:|---:|---:|---:|---:|---:|---:|')
    for r in A['funding']['hl']['top_by_above_fair'][:15]:
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (r['coin'], r['cls'], fm(r['oi_usd']), fm(r['rate_now'], 'pct'),
                                                               fm(r['rate_7d'], 'pct'), fm(r['rate_30d'], 'pct'), fm(r['rate_90d'], 'pct'),
                                                               fm(r.get('share_at_interest_rate_30d'), 'pct'), fm(r['above_fair_30d'])))
    L.append('\n## 4. Metal perps (oracles follow spot)\n')
    L.append('| venue | market | OI | 30d | 90d | net $/yr | above fair $/yr |')
    L.append('|---|---|---:|---:|---:|---:|---:|')
    for r in A['funding']['metals']['markets']:
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (r['venue'], r['coin'], fm(r['oi_usd']), fm(r['rate_30d'], 'pct'), fm(r['rate_90d'], 'pct'),
                                                    fm(r['net_30d']), fm(r['above_fair_30d'])))
    m = A['funding']['metals']['aggregate']
    L.append('| all | %d markets | %s | %s | | %s | %s |' % (m['markets'], fm(m['oi_usd']), fm(m['oi_weighted_rate_30d'], 'pct'), fm(m['net_30d']), fm(m['above_fair_30d'])))
    L.append('\n## 5. Perp-venue fees and LP vaults\n')
    pv = A['llama']['pools']['perp_vaults']
    L.append('Fees %s/yr (trailing 365 days %s), revenue %s, supply side %s.\n' % (fm(pv['fees_yr']), fm(pv['fees_1y']), fm(pv['revenue_yr']), fm(pv['supply_side_yr'])))
    L.append('| venue | fees | revenue | supply side | source |')
    L.append('|---|---:|---:|---:|---|')
    for r in pv['top'][:12]:
        L.append('| %s | %s | %s | %s | %s |' % (r['name'], fm(r['fees_yr']), fm(r['revenue_yr']), fm(r['supply_side_yr']), r['supply_side_src']))
    L.append('\n| LP vault | fee income | TVL | fee APR | above SSR | used |')
    L.append('|---|---:|---:|---:|---:|---|')
    for v in A['perp_vaults']['lp_vaults'][:14]:
        L.append('| %s | %s | %s | %s | %s | %s |' % (v['name'], fm(v['supply_side_yr']), fm(v['tvl_usd']), fm(v['fee_apr'], 'pct'), fm(v['above_fair_yr']),
                                                 'yes' if v['usable'] else v['why_not']))
    h = A['perp_vaults']['hlp_vault_details']
    L.append('\nHLP (vaultDetails): account value %s, last-month PnL %s, %s a year (%s APR).' % (
        fm(h.get('account_value_usd')), fm(h.get('month_pnl_usd')), fm(h.get('income_yr')), fm(h.get('apr_month'), 'pct')))
    L.append('\n## 6. Incentive budgets\n')
    inc = A['incentives']
    L.append('Headline %s/yr on %s of rewarded TVL (%s mean reward APR); stable %s, volatile %s. Excluded: pass-through %s, '
             'outlier-flagged %s, over 300%% APR %s. Merkl live campaigns: %s/yr (%d opportunities). Union with Merkl %s.\n' % (
                 fm(inc['headline_yr']), fm(inc['tvl_rewarded_usd']), fm(inc['mean_reward_apr_on_rewarded_tvl'], 'pct'), fm(inc['stable_yr']),
                 fm(inc['volatile_yr']), fm(inc['totals']['pass_through']), fm(inc['totals']['outlier_flagged']), fm(inc['totals']['over_cap']),
                 fm(inc['merkl']['budget_yr']), inc['merkl']['opportunities'], fm(inc['union_with_merkl_yr'])))
    L.append('| by chain | $/yr |\n|---|---:|')
    for k, v in sorted(inc['by_chain'].items(), key=lambda kv: -kv[1])[:10]:
        L.append('| %s | %s |' % (k, fm(v)))
    L.append('\n| by project | $/yr |\n|---|---:|')
    for k, v in sorted(inc['by_project'].items(), key=lambda kv: -kv[1])[:12]:
        L.append('| %s | %s |' % (k, fm(v)))
    L.append('\n| Merkl protocol | Merkl $/yr | DefiLlama $/yr |\n|---|---:|---:|')
    for k, v in sorted(inc['merkl']['vs_defillama_by_protocol'].items(), key=lambda kv: -kv[1]['merkl_yr']):
        L.append('| %s | %s | %s |' % (k, fm(v['merkl_yr']), fm(v['defillama_yr'])))
    L.append('\n| largest Merkl campaigns | action | TVL | APR | budget $/yr |\n|---|---|---:|---:|---:|')
    for o in inc['merkl']['largest'][:10]:
        L.append('| %s (%s, %s) | %s | %s | %.2f%% | %s |' % (o['name'][:70], o['protocol'], o['chain'], o['action'], fm(o['tvl']), o['apr'] or 0, fm(o['budget_yr'])))
    L.append('\n## 7. DEX LP fees and LVR\n')
    dx = A['llama']['pools']['dex_lp']
    L.append('Fees %s/yr, supply side %s (trailing 365 days at the same share %s), protocol revenue %s.\n' % (
        fm(dx['fees_yr']), fm(dx['supply_side_yr']), fm(dx['supply_side_1y']), fm(dx['revenue_yr'])))
    L.append('| DEX | fees | supply side | trailing 365d fees |\n|---|---:|---:|---:|')
    for r in dx['top'][:12]:
        L.append('| %s | %s | %s | %s |' % (r['name'], fm(r['fees_yr']), fm(r['supply_side_yr']), fm(r['fees_1y'])))
    lv = A['lvr']
    L.append('\nLVR on the %d largest volatile major-pair pools (TVL %s): fees %s/yr; LVR %s (full range) to %s (4x range); '
             'LPs keep %s to %s of fees. Volatility (90 days): %s.\n' % (
                 lv['pools'], fm(lv['tvl']), fm(lv['fees_yr']), fm(lv['lvr_full_range_yr']), fm(lv['lvr_concentrated_4x_yr']),
                 fm(lv['kept_share_full_range'], 'pct'), fm(lv['kept_share_concentrated_4x'], 'pct'),
                 ', '.join('%s %.0f%%' % (k, 100 * v) for k, v in lv['sigma_90d'].items() if v)))
    L.append('| pair | TVL | fees $/yr | LVR full range $/yr |\n|---|---:|---:|---:|')
    for k, v in sorted(lv['by_pair'].items(), key=lambda kv: -kv[1]['tvl']):
        L.append('| %s | %s | %s | %s |' % (k, fm(v['tvl']), fm(v['fees_yr']), fm(v['lvr_lo_yr'])))
    L.append('\n## 8. Lending\n')
    ln = A['lending']
    d = ln['defillama_lending']
    L.append('DefiLlama Lending + CDP: fees %s/yr (trailing 365 days %s), supply side %s, revenue %s.\n' % (fm(d['fees_yr']), fm(d['fees_1y']), fm(d['supply_side_yr']), fm(d['revenue_yr'])))
    L.append('| source | class | borrowed | interest $/yr | mean APR | above fair (clipped) |\n|---|---|---:|---:|---:|---:|')
    for src in ('aave', 'morpho'):
        for c, v in ln[src]['by_class'].items():
            L.append('| %s | %s | %s | %s | %s | %s |' % (src, c, fm(v['borrow_usd']), fm(v['interest_yr']), fm(v['mean_apr'], 'pct'), fm(v['above_fair_clipped_yr'])))
    L.append('\n## 9. Queues\n')
    q = A['queues']
    L.append('| asset | unit | wait (median days) | window | sell $/yr | gross rent $/yr | above fair $/yr | last 13 weeks gross |')
    L.append('|---|---|---:|---:|---:|---:|---:|---:|')
    for r in q['assets']:
        L.append('| %s | %s | %.2f | %dd | %s | %s | %s | %s |' % (r['asset'], r['unit'], r['wait_days'], r['window_days'], fm(r['sell_usd_per_year']),
                                                             fm(r['gross_yr']), fm(r['above_fair_yr']), fm(r.get('trailing_91d_gross_yr'))))
    qb = q.get('queue_book') or {}
    L.append('\nCombined queue book (queue_book): %s/yr out of sample at $15M; unbounded capital would have locked %s at the peak (%s); '
             '1h-late entry keeps %s. Off-Ethereum LSTs: %s a day of native-pair volume (gross band %s).\n' % (
                 fm((qb.get('joint_oos_usd_per_year') or {}).get('15000000')), fm(qb.get('peak_locked_unbounded_usd')), qb.get('peak_day_utc'),
                 fm((qb.get('late_entry_1h_15m') or {}).get('kept_share'), 'pct'), fm((q.get('off_ethereum') or {}).get('vol24_native_pairs_usd')),
                 fb((q.get('off_ethereum') or {}).get('gross_yr_band'))))
    L.append('## 10. Points: Pendle YT premium\n')
    pe = A['pendle']
    L.append('%d markets, YT outstanding %s, premium %s/yr net (%s on notional), %s positive-only; with trailing 7d realised %s.\n' % (
        pe['markets'], fm(pe['yt_notional_usd']), fm(pe['premium_net_yr']), fm(pe['premium_on_notional'], 'pct'), fm(pe['premium_positive_yr']), fm(pe['premium_net_7d_yr'])))
    L.append('| market | expiry | YT notional | implied | realised 30d | premium $/yr | points |\n|---|---|---:|---:|---:|---:|---|')
    for r in pe['top'][:12]:
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (r['name'], r['expiry'], fm(r['yt_notional_usd']), fm(r['implied'], 'pct'), fm(r['realised_30d'], 'pct'),
                                                       fm(r['premium_yr']), r['points']))
    L.append('\n## 11. For scale only\n')
    L.append('| pool | fees $/yr | trailing 365d |\n|---|---:|---:|')
    for k in ('scale_stable', 'scale_staking', 'scale_chain', 'scale_rwa', 'scale_mev'):
        x = A['scale_only'][k]
        L.append('| %s | %s | %s |' % (k, fm(x['fees_yr']), fm(x['fees_1y'])))
    en = A['llama']['pools']['entertainment']
    L.append('| entertainment | %s | %s |' % (fm(en['fees_yr']), fm(en['fees_1y'])))
    L.append('\nStablecoin supply %s; Ethena: USDe %s, fees %s/yr (%s of the longs-paid funding on the four venues, %s).\n' % (
        fm(A['scale_only']['stablecoin_supply_usd']), fm(A['collectors']['ethena']['usde_supply_usd']), fm(A['collectors']['ethena']['fees_yr']),
        fm(A['collectors']['ethena']['share_of_longs_paid_4_venues'], 'pct'), fm(A['collectors']['longs_paid_4_venues_yr'])))
    L.append('## 12. Checks\n')
    c = A['checks']
    hc = c['hl_funding_paths']
    L.append('- Hyperliquid funding, two paths over %s to %s (%.1f days, %d main-dex coins): realised (OI interpolated across four snapshots x every '
             'settled hour) %s/yr vs current OI x the same hours %s/yr, ratio %.3f.' % (
                 hc['window_utc'][0], hc['window_utc'][1], hc['days'], hc['coins'], fm(hc['path_b_realised_net_per_year']),
                 fm(hc['path_a_current_oi_x_same_window_rates_per_year']), hc['ratio_b_over_a']))
    L.append('- Hyperliquid OI: venue %s vs DefiLlama %s on the main dex (ratio %.2f); tradeXYZ %s vs %s (ratio %.3f).' % (
        fm(hc['oi_main_ctx_usd']), fm(hc['oi_main_defillama_usd']), hc['oi_ratio_main'] or 0, fm(hc['oi_xyz_ctx_usd']), fm(hc['oi_xyz_defillama_usd']), hc['oi_ratio_xyz'] or 0))
    a = c['aave_api_vs_defillama']
    L.append('- Aave: own API (borrowed x APR now) %s/yr vs DefiLlama aave-v3 fees (30 days) %s/yr, ratio %.3f; Ethereum %s vs %s, ratio %.3f.' % (
        fm(a['aave_api_interest_all_chains_yr']), fm(a['defillama_aave_v3_fees_30d_yr']), a['ratio_all'] or 0,
        fm(a['aave_api_interest_ethereum_yr']), fm(a['defillama_aave_v3_fees_ethereum_30d_yr']), a['ratio_ethereum'] or 0))
    L.append('- Incentives: Merkl own API %s/yr vs DefiLlama headline %s/yr (Morpho %s vs %s; Aave %s vs %s).' % (
        fm(c['merkl_total_yr']), fm(c['defillama_incentives_headline_yr']),
        fm(c['incentives_merkl_vs_defillama']['morpho']['merkl_yr']), fm(c['incentives_merkl_vs_defillama']['morpho']['defillama_yr']),
        fm(c['incentives_merkl_vs_defillama']['aave']['merkl_yr']), fm(c['incentives_merkl_vs_defillama']['aave']['defillama_yr'])))
    f = c['hl_fees_vs_volume']
    if f:
        L.append('- Hyperliquid fees: DefiLlama %s a day (7-day mean) on the venue\'s own %s of 24h volume = %.1f bp (expected 2-12 bp).' % (
            fm(f['defillama_fees_per_day_7d_usd']), fm(f['hl_volume_24h_usd']), f['implied_fee_bp']))
    L.append('\n## 13. Double-count guards\n')
    for k, v in A['double_count'].items():
        L.append('- %s: %s' % (k, json.dumps(v, default=str)[:300]))
    L.append('\n## 14. API gaps\n')
    for g in A['api_gaps']:
        L.append('- ' + g)
    (Path(args.out) / 'tables.md').write_text('\n'.join(L) + '\n')
    m = Path(args.out) / 'manifest.json'
    man = json.loads(m.read_text()) if m.exists() else {}
    man['render'] = {'generated': utc(), 'tables': 'tables.md'}
    man['outputs'] = ['analysis.json', 'tables.md', 'manifest.json']
    man['raw'] = sorted(str(p.relative_to(args.out)) for p in (Path(args.out) / 'raw').rglob('*.json*'))[:20] + ['...']
    man['raw_files'] = sum(1 for _ in (Path(args.out) / 'raw').rglob('*.json*'))
    write_json(m, man)
    print('tables.md: %d lines' % len(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--out', required=True)
    c.add_argument('--parts', default='')
    c.add_argument('--refresh', action='store_true')
    a = sub.add_parser('analyze')
    a.add_argument('--out', required=True)
    r = sub.add_parser('render')
    r.add_argument('--out', required=True)
    args = ap.parse_args()
    {'collect': cmd_collect, 'analyze': lambda a: cmd_analyze(a), 'render': lambda a: cmd_render(a)}[args.cmd](args)


if __name__ == '__main__':
    main()
