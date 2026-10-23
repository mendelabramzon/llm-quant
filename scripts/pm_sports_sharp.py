#!/usr/bin/env python3
"""Pre-game soccer prices on Polymarket against the sharp bookmaker consensus (pm_sports_sharp, 2026-10-14).

Why. The repo's frame is that alpha is a rent paid by a counterparty with a non-price motive. Polymarket's sports flow
is widely described as fan money; bookmakers' consensus prices (Pinnacle above all) are the sharpest public estimate of
a match's probabilities. If Polymarket's pre-game price strays from the de-vigged consensus by more than the fee plus
the spread, buying the cheap side 1-24 hours before kick-off earns the gap without racing anyone. This module counts
whether it did, on every Polymarket main-league soccer match it can match to football-data.co.uk.

Data.
  * Polymarket: the stored resolved universe (research/2026-10-09/polymarket_history/raw/universe.json.gz); a match is
    a neg-risk event of up to three "Will X win / end in a draw" markets (only members with >= $10k volume are in the
    universe). Hourly midpoints over [kick-off - 30h, kick-off + 1h] from CLOB prices-history (points are forward-filled
    and stamped seconds after each hour).
  * football-data.co.uk main divisions, seasons 2025/26 and 2026/27: pre-closing odds (Pinnacle PSH/PSD/PSA where
    present - 2026/27 dropped them - otherwise the market average AvgH/AvgD/AvgA) and closing odds (PSC*/AvgC*).
    "Betting odds for weekend games are collected Friday afternoons, and on Tuesday afternoons for midweek games"
    (notes.txt). The pre-closing odds are therefore usable only after that collection; the availability rule here
    assumes 18:00 London on the collection day (the latest plausible afternoon) and drops a decision taken earlier.
  * Extra leagues (/new/*.csv) and tennis-data.co.uk carry closing odds only ("the most recent before play starts");
    they are used for description and look-ahead accounting, never for a decision.
  * A live CLOB snapshot of open soccer/tennis moneyline books (half-spread and depth by price band and hours to
    start), and data-api taker trades around sampled entries (what takers actually paid, and the volume there).

Costs. A taker buys at the midpoint plus the live half-spread for the price band plus the taker fee
shares x 0.05 x p x (1 - p) (sports rate; polymarket_history.fee_rate). A resting buy joins the bid (mid - half-spread),
pays no fee, and fills only if a later hourly midpoint trades a full tick through it before kick-off.

Protocol. Variants are fixed in VARIANTS before any return is computed; choose on the first half of matched events by
kick-off date, test once on the rest (backtest.choose_then_test on daily P&L per $1 stake); late entry one hour later at
that hour's price; capacity from the touch depth and the traded volume around entries.

    uv run python scripts/pm_sports_sharp.py odds    --out research/2026-10-14/pm_sports_sharp
    uv run python scripts/pm_sports_sharp.py live    --out research/2026-10-14/pm_sports_sharp
    uv run python scripts/pm_sports_sharp.py match   --out research/2026-10-14/pm_sports_sharp
    uv run python scripts/pm_sports_sharp.py prices  --out research/2026-10-14/pm_sports_sharp
    uv run python scripts/pm_sports_sharp.py analyze --out research/2026-10-14/pm_sports_sharp
    uv run python scripts/pm_sports_sharp.py trades  --out research/2026-10-14/pm_sports_sharp
    uv run python scripts/pm_sports_sharp.py render  --out research/2026-10-14/pm_sports_sharp
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import io
import json
import math
import random
import re
import statistics
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
import polymarket_history as PH  # noqa: E402

HIST = ROOT / 'research' / '2026-10-09' / 'polymarket_history'
LONDON = ZoneInfo('Europe/London')
UTC = dt.timezone.utc
DAY, HOUR = 86400.0, 3600.0
SSR = 0.038
FD = 'https://www.football-data.co.uk/'
TD = 'http://www.tennis-data.co.uk/hrjk-85HytOjkhth76j_ygh4jf7/'   # the plain /2026/ path is a parked page
SPORTS_RATE = PH.fee_rate('sports')                                # 0.05 (docs.polymarket.com, re-read 2026-10-14)

MAIN_DIVS = ['E0', 'E1', 'E2', 'E3', 'EC', 'SC0', 'SC1', 'SC2', 'SC3', 'D1', 'D2', 'I1', 'I2', 'SP1', 'SP2', 'F1',
             'F2', 'N1', 'B1', 'P1', 'T1', 'G1']
SEASONS = ['2526', '2627']
EXTRA = ['ARG', 'AUT', 'BRA', 'CHN', 'DNK', 'FIN', 'IRL', 'JPN', 'MEX', 'NOR', 'POL', 'ROU', 'RUS', 'SWE', 'SWZ', 'USA']
# Polymarket event-slug prefix -> football-data division. 'spl' is the Saudi league, not Scotland ('scop').
SLUG_DIV = {'epl': 'E0', 'elc': 'E1', 'el1': 'E2', 'el2': 'E3', 'scop': 'SC0', 'bun': 'D1', 'bl2': 'D2', 'sea': 'I1',
            'itsb': 'I2', 'lal': 'SP1', 'es2': 'SP2', 'fl1': 'F1', 'fr2': 'F2', 'ere': 'N1', 'bel1': 'B1', 'por': 'P1',
            'tur': 'T1', 'gre': 'G1', 'gre1': 'G1'}
SLUG_EXTRA = {'mls': 'USA', 'arg': 'ARG', 'bra': 'BRA', 'mex': 'MEX', 'chi': 'CHN', 'nor': 'NOR', 'den': 'DNK',
              'swe': 'SWE', 'j1100': 'JPN', 'jap': 'JPN', 'rus': 'RUS', 'sui': 'SWZ', 'aut': 'AUT', 'pol': 'POL',
              'rou1': 'ROU', 'fin1': 'FIN', 'irl': 'IRL', 'irl1': 'IRL'}
TOP5 = {'E0', 'SP1', 'D1', 'I1', 'F1'}

# ------------------------------------------------------------------------------------------------- pre-registration
# Fixed 2026-10-14 before any return was computed (see analysis.json['preregistration']).
HORIZONS_H = [24, 6, 2]
THRESHOLDS = [0.0, 0.03, 0.06]          # minimum expected return per $ after spread and fee, at the fair value
OTYPES = ['all', 'fav', 'draw', 'dog']   # which member: favourite team, draw, underdog team (by fair probability)
TIERS = ['all', 'top5', 'rest']
EXECS = ['taker', 'maker']
DEVIG = 'shin'                           # primary; multiplicative is a reported sensitivity, never selected on
MID_MIN, MID_MAX = 0.02, 0.98            # a member priced outside this is not traded
MAKER_THROUGH = 0.01                     # a resting buy fills when a later mid is a full tick below the limit
SETTLE_AFTER_H = 2.5                     # soccer: capital returns ~2.5h after kick-off (Polymarket closes ~3-6h)
KO_TOL_H = 0.25                          # drop a match whose Polymarket and football-data kick-offs disagree by more
                                         # (20 of 3,244: rescheduled games; a "pre-game" price could be in play)


def variant_names():
    return ['%s|h%d|thr%.2f|%s|%s' % (e, h, t, o, r) for e in EXECS for h in HORIZONS_H for t in THRESHOLDS
            for o in OTYPES for r in TIERS]


# ------------------------------------------------------------------------------------------------- pure: odds

def implied(odds):
    """Decimal odds -> raw implied probabilities; None if any price is missing or not above 1."""
    if not odds or any(o is None or not (o > 1.0) for o in odds):
        return None
    return [1.0 / o for o in odds]


def devig_mult(odds):
    pi = implied(odds)
    if pi is None:
        return None
    s = sum(pi)
    return [x / s for x in pi]


def devig_shin(odds, iters=200):
    """Shin (1993) probabilities: p_i = (sqrt(z^2 + 4(1-z) pi_i^2 / S) - z) / (2(1-z)), with z solved so they sum to
    one. Shin takes more margin off longshots than the multiplicative rule does. Books with no overround are only
    normalised."""
    pi = implied(odds)
    if pi is None:
        return None
    s = sum(pi)
    if s <= 1.0:
        return [x / s for x in pi]

    def probs(z):
        return [(math.sqrt(z * z + 4.0 * (1.0 - z) * x * x / s) - z) / (2.0 * (1.0 - z)) for x in pi]

    lo, hi = 0.0, 0.99
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if sum(probs(mid)) > 1.0:
            lo = mid
        else:
            hi = mid
    p = probs((lo + hi) / 2.0)
    t = sum(p)
    return [x / t for x in p]


def devig(odds, method):
    return devig_shin(odds) if method == 'shin' else devig_mult(odds)


def fnum(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def fd_odds(row, kind):
    """(source, [home, draw, away] decimal odds) from a football-data row: Pinnacle if all three present, else the
    market average. kind 'pre' or 'close'."""
    c = 'C' if kind == 'close' else ''
    ps = [fnum(row.get('PS%s%s' % (c, x))) for x in 'HDA']
    if implied(ps):
        return 'pinnacle', ps
    av = [fnum(row.get('Avg%s%s' % (c, x))) for x in 'HDA']
    if implied(av):
        return 'average', av
    return None, None


def fd_kickoff(date_s, time_s):
    """football-data Date (dd/mm/yyyy or dd/mm/yy) and Time (UK local) -> UTC timestamp; noon when no time."""
    try:
        d, m, y = [int(x) for x in date_s.strip().split('/')]
    except (ValueError, AttributeError):
        return None
    if y < 100:
        y += 2000
    hh, mm = 12, 0
    if time_s and ':' in time_s:
        try:
            hh, mm = [int(x) for x in time_s.strip().split(':')[:2]]
        except ValueError:
            pass
    return dt.datetime(y, m, d, hh, mm, tzinfo=LONDON).timestamp()


def fd_available(kickoff_ts, hour_local=18):
    """When football-data's pre-closing odds for a match can be assumed known: 18:00 London on the collection day
    (Friday for weekend games, Tuesday for midweek), the latest Tuesday or Friday whose 18:00 precedes kick-off. A
    match kicking off on a Tuesday or Friday before 18:00 gets kick-off itself (no pre-game decision allowed): its
    odds were taken that afternoon, at an unknown time."""
    ko = dt.datetime.fromtimestamp(kickoff_ts, LONDON)
    if ko.weekday() in (1, 4):
        c = dt.datetime(ko.year, ko.month, ko.day, hour_local, 0, tzinfo=LONDON).timestamp()
        if c >= kickoff_ts:
            return kickoff_ts
        return c
    d = ko.date()
    for back in range(1, 8):
        day = d - dt.timedelta(days=back)
        if day.weekday() in (1, 4):
            return dt.datetime(day.year, day.month, day.day, hour_local, 0, tzinfo=LONDON).timestamp()
    return kickoff_ts


# ------------------------------------------------------------------------------------------------- pure: names

NAME_STOP = {'fc', 'cf', 'afc', 'sc', 'ac', 'as', 'ss', 'us', 'sv', 'vfb', 'vfl', 'tsg', 'fsv', 'sk', 'jk', 'fk',
             'cd', 'ud', 'rcd', 'rc', 'sd', 'ca', 'club', 'de', 'del', 'la', 'le', 'el', 'calcio', 'balompie',
             'futbol', 'football', 'sad', 'bk', 'if', 'ik', 'kv', 'krc', 'rsc', 'cfc', 'ssc', 'acf', 'hsc', 'sco',
             'spor', 'kulubu', 'ksk', 'ksv', 'kaa', 'kas', 'rsca', 'rwd', 'oh', 'sl', 'fsc', 'ogc', 'sm', 'aj', 'rb',
             'bc', 'ec', 'aa', 'tc', 'and', 'the', 'of', 'da', 'do', 'di', 'en', 'cp', 'sp', 'futebol', 'clube'}
NAME_SYN = {'utd': 'united', 'man': 'manchester', 'nottm': 'nottingham', 'weds': 'wednesday', 'ein': 'eintracht',
            'mgladbach': 'monchengladbach', 'gladbach': 'monchengladbach', 'koln': 'koln', 'cologne': 'koln',
            'munich': 'munchen', 'bayern': 'bayern', 'st': 'saint', 'sint': 'saint', 'internazionale': 'inter',
            'psg': 'paris', 'atletico': 'atletico', 'atl': 'atletico', 'ath': 'athletic', 'espanol': 'espanyol',
            'qpr': 'queens', 'wolves': 'wolverhampton', 'spurs': 'tottenham', 'brighton': 'brighton',
            'hellas': 'verona', 'buyuksehyr': 'basaksehir', 'goztep': 'goztepe', 'pacos': 'pacos',
            'guimaraes': 'guimaraes', 'vitoria': 'vitoria', 'standard': 'standard', 'gilloise': 'gilloise',
            'forest': 'forest', 'mainz': 'mainz', 'zwolle': 'zwolle', 'nijmegen': 'nec', 'sittard': 'sittard',
            'jrs': 'juniors', 'hamkam': 'hamarkameratene'}
# Whole-name aliases for football-data short names whose tokens do not overlap the Polymarket names.
FD_ALIAS = {
    "nott'm forest": 'nottingham forest', 'man united': 'manchester united', 'man city': 'manchester city',
    'sheffield weds': 'sheffield wednesday', 'qpr': 'queens park rangers', 'west brom': 'west bromwich albion',
    'wolves': 'wolverhampton wanderers', 'ath madrid': 'atletico madrid', 'ath bilbao': 'athletic club bilbao',
    'betis': 'real betis', 'sociedad': 'real sociedad', 'celta': 'celta vigo', 'vallecano': 'rayo vallecano',
    'sp gijon': 'sporting gijon', 'la coruna': 'deportivo la coruna', 'santander': 'racing santander',
    'ferrol': 'racing ferrol', 'ein frankfurt': 'eintracht frankfurt', "m'gladbach": 'borussia monchengladbach',
    'fc koln': 'koln', 'bayern munich': 'bayern munchen', 'hertha': 'hertha berlin',
    'fortuna dusseldorf': 'fortuna dusseldorf', 'greuther furth': 'greuther furth', 'inter': 'inter milano',
    'milan': 'ac milan', 'paris sg': 'paris saint germain', 'st etienne': 'saint etienne', 'sp lisbon': 'sporting lisbon',
    'sp braga': 'braga', 'guimaraes': 'vitoria guimaraes', 'for sittard': 'fortuna sittard', 'nijmegen': 'nec nijmegen',
    'waalwijk': 'rkc waalwijk', 'zwolle': 'pec zwolle', 'buyuksehyr': 'istanbul basaksehir', 'ad. demirspor': 'adana demirspor',
    'karagumruk': 'fatih karagumruk', 'st truiden': 'sint truiden', 'standard': 'standard liege',
    'st. gilloise': 'union saint gilloise', 'oud-heverlee leuven': 'oh leuven', 'cercle brugge': 'cercle brugge',
    'club brugge': 'club brugge', 'dundee united': 'dundee united', 'st mirren': 'saint mirren',
    'st johnstone': 'saint johnstone', 'hearts': 'heart of midlothian', 'verona': 'hellas verona',
    'leverkusen': 'bayer leverkusen', 'dortmund': 'borussia dortmund', 'psv eindhoven': 'psv', 'az alkmaar': 'az',
    'nac breda': 'nac breda', 'go ahead eagles': 'go ahead eagles', 'man utd': 'manchester united',
    'wycombe': 'wycombe wanderers', 'mk dons': 'milton keynes dons', 'peterboro': 'peterborough',
    'bristol rvs': 'bristol rovers', 'cambridge': 'cambridge united', 'oxford': 'oxford united',
    'stockport': 'stockport county', 'leyton orient': 'leyton orient', 'sp. gijon': 'sporting gijon',
    'pacos ferreira': 'pacos ferreira', 'estrela': 'estrela amadora', 'casa pia': 'casa pia', 'famalicao': 'famalicao',
    'arouca': 'arouca', 'tondela': 'tondela', 'gil vicente': 'gil vicente', 'nacional': 'nacional madeira',
    'santa clara': 'santa clara', 'avs': 'afs avs', 'alverca': 'alverca', 'moreirense': 'moreirense',
    'heidenheim': 'heidenheim', 'st pauli': 'saint pauli', 'union berlin': 'union berlin', 'werder bremen': 'werder bremen',
    'hamburg': 'hamburger', 'schalke 04': 'schalke', 'fc heidenheim': 'heidenheim', 'rb leipzig': 'leipzig',
    'mainz': 'mainz', 'augsburg': 'augsburg', 'wolfsburg': 'wolfsburg', 'freiburg': 'freiburg', 'hoffenheim': 'hoffenheim',
    'stuttgart': 'stuttgart', 'parma': 'parma', 'como': 'como', 'cremonese': 'cremonese', 'pisa': 'pisa',
    'atalanta': 'atalanta', 'genoa': 'genoa', 'torino': 'torino', 'lecce': 'lecce', 'cagliari': 'cagliari',
    'sassuolo': 'sassuolo', 'udinese': 'udinese', 'fiorentina': 'fiorentina', 'bologna': 'bologna', 'napoli': 'napoli',
    'juventus': 'juventus', 'lazio': 'lazio', 'roma': 'roma', 'athletico-pr': 'athletico paranaense',
    'atletico-mg': 'atletico mineiro', 'rennes': 'stade rennais'}


TRANSLIT = str.maketrans({'æ': 'ae', 'Æ': 'AE', 'ø': 'o', 'Ø': 'O', 'å': 'a', 'Å': 'A', 'ß': 'ss', 'ł': 'l', 'Ł': 'L',
                          'đ': 'd', 'Đ': 'D', 'ı': 'i', 'İ': 'I', 'ð': 'd', 'þ': 'th', 'œ': 'oe', '·': ' '})


def name_tokens(s):
    s = (s or '').translate(TRANSLIT)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().strip()
    s = FD_ALIAS.get(s, s)
    s = s.replace("'", '')
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    toks = []
    for t in s.split():
        t = NAME_SYN.get(t, t)
        if t in NAME_STOP or t.isdigit() or len(t) < 2:
            continue
        toks.append(t)
    return toks


def edit_distance(a, b, cap=3):
    """Levenshtein distance, stopped early once every entry of a row exceeds `cap`."""
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, y in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y))
        if min(cur) > cap:
            return cap + 1
        prev = cur
    return prev[-1]


def _tok_match(a, b):
    if a == b:
        return True
    if len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a)):
        return True
    n = min(len(a), len(b))
    if n >= 6:
        # transliteration variants: Levadiakos/Levadeiakos, Panaitolikos/Panetolikos, Goztepe/Göztepe
        return edit_distance(a, b) <= (2 if n >= 9 else 1)
    return False


# Club words shared by many teams count for little on their own ('Real' Madrid is not 'Real' Sociedad).
GENERIC = {'real', 'united', 'city', 'athletic', 'atletico', 'saint', 'inter', 'racing', 'stade', 'deportivo', 'union',
           'borussia', 'eintracht', 'fortuna', 'young', 'town', 'county', 'rovers', 'wanderers', 'albion', 'sporting',
           'olympique', 'dynamo', 'nacional', 'universidad', 'independiente', 'hotspur', 'rangers', 'athletico',
           'america', 'central', 'olympic', 'atletica', 'esporte', 'sports'}
GENERIC_W = 0.3


def team_sim(a, b):
    """Share of the shorter name's tokens found in the other (exact, a 4+ letter prefix, or one edit for 6+ letters);
    1.0 when the names are equal once normalised."""
    ta, tb = name_tokens(a), name_tokens(b)
    if not ta or not tb:
        return 0.0
    if ''.join(ta) == ''.join(tb):
        return 1.0
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    w = [GENERIC_W if x in GENERIC else 1.0 for x in short]
    hit = sum(wi for x, wi in zip(short, w) if any(_tok_match(x, y) for y in long_))
    return hit / sum(w)


def pair_score(pm_a, pm_b, fd_home, fd_away):
    """Best orientation of a Polymarket pair (A vs B) against a football-data fixture: (score, swapped, simA, simB)."""
    s1 = (team_sim(pm_a, fd_home), team_sim(pm_b, fd_away))
    s2 = (team_sim(pm_a, fd_away), team_sim(pm_b, fd_home))
    if sum(s2) > sum(s1):
        return sum(s2), True, s2[0], s2[1]
    return sum(s1), False, s1[0], s1[1]


def accept_match(cands, min_each=0.5, min_total=1.2, margin=0.3):
    """cands: [(score, swapped, simA, simB, key)], best first after sorting. Accept the best when both teams match and it
    beats the runner-up by `margin`."""
    if not cands:
        return None
    cands = sorted(cands, key=lambda x: -x[0])
    best = cands[0]
    if best[2] < min_each or best[3] < min_each or best[0] < min_total:
        return None
    if len(cands) > 1 and best[0] - cands[1][0] < margin:
        return None
    return best


# ------------------------------------------------------------------------------------------------- pure: trading

def taker_cost(p_mid, half_spread, rate=SPORTS_RATE, cap=0.99):
    """Cost of one share bought at the ask (mid + half-spread) with the taker fee rate x p x (1 - p)."""
    px = min(cap, p_mid + half_spread)
    return px + PH.fee_per_share(rate, px), px


def maker_limit(p_mid, half_spread):
    """A resting buy joins the bid."""
    return max(0.001, p_mid - half_spread)


def maker_filled(limit, later_mids, through=MAKER_THROUGH):
    """Conservative queue: the order fills only if the market later trades a full tick through the limit."""
    return any(m is not None and m <= limit - through + 1e-12 for m in later_mids)


def expected_return(fair, cost):
    return fair / cost - 1.0 if cost > 0 else None


def side_view(mid_yes, fair_yes, payout_yes, side):
    """Price, fair probability and payout of buying YES (side 0) or NO (side 1) of a member market."""
    if side == 0:
        return mid_yes, fair_yes, payout_yes
    return 1.0 - mid_yes, 1.0 - fair_yes, (None if payout_yes is None else 1.0 - payout_yes)


def otype_of(member, fair):
    """'draw', or 'fav' / 'dog' for a team member by fair win probability (home vs away)."""
    if member == 'draw':
        return 'draw'
    other = 'away' if member == 'home' else 'home'
    return 'fav' if fair[member] >= fair[other] else 'dog'


def pick_signal(cands, thr, otype):
    """One trade per match: the candidate with the largest expected return among those of the outcome type (or any)
    clearing the threshold. cands: dicts with 'ev' and 'otype'."""
    ok = [c for c in cands if c['ev'] is not None and c['ev'] >= thr and (otype == 'all' or c['otype'] == otype)]
    if not ok:
        return None
    return max(ok, key=lambda c: c['ev'])


def band10(p):
    return min(9, max(0, int(p * 10.0)))


# ------------------------------------------------------------------------------------------------- io helpers

def get_text(url, path, pace=0.6):
    path = Path(path)
    if path.exists() and path.stat().st_size > 0:
        return path.read_bytes(), 'cached'
    time.sleep(pace)
    last = None
    for a in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (llm-quant research)'})
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            return raw, 'fetched'
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:120]
            if '404' in last:
                return None, last
            time.sleep(min(20.0, 2.0 * 2 ** a))
    return None, last


def read_csv_rows(path):
    raw = Path(path).read_bytes()
    txt = raw.decode('utf-8-sig', errors='replace')
    rows = list(csv.DictReader(io.StringIO(txt)))
    return [r for r in rows if any((v or '').strip() for v in r.values())]


XNS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def read_xlsx(path):
    """First sheet of an .xlsx as a list of rows (pure Python: zip + XML; the repo runs without third-party libs)."""
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.iter(XNS + 'si'):
            ss.append(''.join(t.text or '' for t in si.iter(XNS + 't')))
    sheet = sorted(n for n in z.namelist() if n.startswith('xl/worksheets/sheet'))[0]
    root = ET.fromstring(z.read(sheet))
    rows = []
    for r in root.iter(XNS + 'row'):
        vals = {}
        for c in r.findall(XNS + 'c'):
            ref = re.match(r'([A-Z]+)', c.get('r')).group(1)
            ci = 0
            for ch in ref:
                ci = ci * 26 + (ord(ch) - 64)
            t, v = c.get('t'), c.find(XNS + 'v')
            if t == 's' and v is not None:
                val = ss[int(v.text)]
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter(XNS + 't'))
            else:
                val = v.text if v is not None else None
            vals[ci - 1] = val
        if vals:
            rows.append([vals.get(i) for i in range(max(vals) + 1)])
    return rows


# ------------------------------------------------------------------------------------------------- odds

def cmd_odds(args):
    out = Path(args.out)
    t0 = time.time()
    log = []
    for s in SEASONS:
        for d in MAIN_DIVS:
            raw, st = get_text(FD + 'mmz4281/%s/%s.csv' % (s, d), out / 'raw' / 'fd' / ('%s_%s.csv' % (s, d)))
            log.append({'file': '%s/%s' % (s, d), 'status': st, 'bytes': len(raw or b'')})
    for x in EXTRA:
        raw, st = get_text(FD + 'new/%s.csv' % x, out / 'raw' / 'fd' / ('new_%s.csv' % x))
        log.append({'file': 'new/%s' % x, 'status': st, 'bytes': len(raw or b'')})
    for p in ['2025/2025.xlsx', '2025w/2025.xlsx', '2026/2026.xlsx', '2026w/2026.xlsx']:
        raw, st = get_text(TD + p, out / 'raw' / 'tennis' / p.replace('/', '_'))
        log.append({'file': 'tennis/' + p, 'status': st, 'bytes': len(raw or b'')})
    cols = {}
    for s in SEASONS:
        p = out / 'raw' / 'fd' / ('%s_E0.csv' % s)
        if p.exists():
            rows = read_csv_rows(p)
            cols[s] = {'n': len(rows), 'has_PS': bool(rows and 'PSH' in rows[0]),
                       'has_PSC': bool(rows and 'PSCH' in rows[0]), 'has_BFE': bool(rows and 'BFEH' in rows[0])}
    PH.update_manifest(out, 'odds', {'fetched_at': PH.utc(t0), 'sources': [FD + 'mmz4281/<season>/<div>.csv',
                                                                           FD + 'new/<country>.csv',
                                                                           TD + '<year>[w]/<year>.xlsx'],
                                     'files': log, 'errors': sum(1 for x in log if x['status'] not in
                                                                 ('cached', 'fetched')), 'columns_E0': cols,
                                     'notes': 'football-data: pre-closing odds collected Friday afternoons (weekend) '
                                              'and Tuesday afternoons (midweek); closing odds at kick-off. '
                                              'tennis-data: "the most recent before play starts" (closing).'})
    print(json.dumps({'files': len(log), 'columns_E0': cols}))
    return 0


def load_fd(out):
    """Every football-data fixture with odds: main divisions (pre + close) and extra leagues (close only)."""
    rows = []
    for s in SEASONS:
        for d in MAIN_DIVS:
            p = Path(out) / 'raw' / 'fd' / ('%s_%s.csv' % (s, d))
            if not p.exists() or p.stat().st_size < 100:
                continue
            for r in read_csv_rows(p):
                ko = fd_kickoff(r.get('Date'), r.get('Time'))
                if ko is None or not r.get('HomeTeam'):
                    continue
                src_pre, pre = fd_odds(r, 'pre')
                src_cl, cl = fd_odds(r, 'close')
                bfe = [fnum(r.get('BFE%s' % x)) for x in 'HDA']
                rows.append({'div': d, 'season': s, 'ko': ko, 'date': r.get('Date'), 'time': r.get('Time'),
                             'home': r['HomeTeam'].strip(), 'away': r['AwayTeam'].strip(), 'ftr': r.get('FTR'),
                             'fthg': r.get('FTHG'), 'ftag': r.get('FTAG'), 'pre_src': src_pre, 'pre': pre,
                             'close_src': src_cl, 'close': cl, 'bfe': bfe if implied(bfe) else None,
                             'avg_pre': [fnum(r.get('Avg%s' % x)) for x in 'HDA'],
                             'avg_close': [fnum(r.get('AvgC%s' % x)) for x in 'HDA'], 'extra': False})
    for x in EXTRA:
        p = Path(out) / 'raw' / 'fd' / ('new_%s.csv' % x)
        if not p.exists():
            continue
        for r in read_csv_rows(p):
            if (r.get('Season') or '') < '2025':
                continue
            ko = fd_kickoff(r.get('Date'), r.get('Time'))
            if ko is None or ko < dt.datetime(2025, 6, 1, tzinfo=UTC).timestamp():
                continue
            ps = [fnum(r.get('PSC%s' % c)) for c in 'HDA']
            av = [fnum(r.get('AvgC%s' % c)) for c in 'HDA']
            src, cl = ('pinnacle', ps) if implied(ps) else (('average', av) if implied(av) else (None, None))
            rows.append({'div': x, 'season': r.get('Season'), 'ko': ko, 'date': r.get('Date'), 'time': r.get('Time'),
                         'home': (r.get('Home') or '').strip(), 'away': (r.get('Away') or '').strip(),
                         'ftr': r.get('Res'), 'fthg': r.get('HG'), 'ftag': r.get('AG'), 'pre_src': None, 'pre': None,
                         'close_src': src, 'close': cl, 'bfe': None, 'avg_pre': None, 'avg_close': av,
                         'extra': True})
    return rows


# ------------------------------------------------------------------------------------------------- match

def pm_soccer_events(uni):
    """Polymarket soccer match events from the resolved universe: members keyed home/draw/away by name."""
    ev = collections.defaultdict(list)
    for m in uni:
        if m.get('cat') != 'sports' or m.get('sportsMarketType') != 'moneyline' or not m.get('gameStartTime'):
            continue
        if 'Soccer' not in (m.get('tags') or []):
            continue
        ev[m['event_id']].append(m)
    out = []
    for eid, ms in ev.items():
        title = ms[0].get('event_title') or ''
        if ' vs. ' not in title:
            continue
        a, b = [x.strip() for x in title.split(' vs. ', 1)]
        prefix = (ms[0].get('event_slug') or '').split('-')[0]
        mem = {}
        for m in ms:
            g = (m.get('groupItemTitle') or '').strip()
            if g.lower().startswith('draw') or 'end in a draw' in (m.get('question') or '').lower():
                role = 'draw'
            elif g == a:
                role = 'A'
            elif g == b:
                role = 'B'
            else:
                q = m.get('question') or ''
                role = 'A' if (a and a in q) else ('B' if (b and b in q) else None)
            if role is None or role in mem:
                continue
            pay = PH.binary_payout(m)
            mem[role] = {'id': m['id'], 'token': (m.get('clobTokenIds') or [None])[0], 'payout': pay,
                         'volume': m.get('volumeNum'), 'closed': m.get('closedTime'), 'question': m.get('question'),
                         'conditionId': m.get('conditionId'), 'fee_type': m.get('feeType')}
        if not mem:
            continue
        out.append({'event_id': eid, 'slug': ms[0].get('event_slug'), 'prefix': prefix, 'title': title, 'A': a, 'B': b,
                    'ko': PH.parse_ts(ms[0]['gameStartTime']), 'members': mem,
                    'tags': [t for t in ms[0].get('tags') or [] if t not in ('Sports', 'Games', 'Soccer')]})
    return out


def cmd_match(args):
    out = Path(args.out)
    t0 = time.time()
    uni = PH.read_gz(HIST / 'raw' / 'universe.json.gz')
    events = pm_soccer_events(uni)
    del uni
    fd = load_fd(out)
    by_div = collections.defaultdict(list)
    for i, r in enumerate(fd):
        by_div[r['div']].append(i)
    for d in by_div:
        by_div[d].sort(key=lambda i: fd[i]['ko'])
    matches, unmatched, stats = [], [], collections.Counter()
    for e in events:
        div = SLUG_DIV.get(e['prefix']) or SLUG_EXTRA.get(e['prefix'])
        if not div:
            stats['no_division'] += 1
            continue
        stats['in_scope'] += 1
        idx = by_div.get(div, [])
        kos = [fd[i]['ko'] for i in idx]
        lo = bisect.bisect_left(kos, e['ko'] - 36 * HOUR)
        hi = bisect.bisect_right(kos, e['ko'] + 36 * HOUR)
        cands = []
        for i in idx[lo:hi]:
            r = fd[i]
            sc, sw, sa, sb = pair_score(e['A'], e['B'], r['home'], r['away'])
            cands.append((sc, sw, sa, sb, i))
        best = accept_match(cands)
        if best is None:
            unmatched.append({'event_id': e['event_id'], 'slug': e['slug'], 'title': e['title'], 'div': div,
                              'ko': PH.utc(e['ko']), 'best': (sorted(cands, key=lambda x: -x[0])[:2] and
                                                              [(round(c[0], 2), fd[c[4]]['home'], fd[c[4]]['away'])
                                                               for c in sorted(cands, key=lambda x: -x[0])[:2]])})
            stats['unmatched'] += 1
            continue
        sc, sw, sa, sb, i = best
        r = fd[i]
        roles = {'draw': 'draw', 'A': 'away' if sw else 'home', 'B': 'home' if sw else 'away'}
        mem = {roles[k]: v for k, v in e['members'].items()}
        # Polymarket's resolution against the result: each present member's payout must agree with FTR
        exp = {'H': {'home': 1.0, 'draw': 0.0, 'away': 0.0}, 'D': {'home': 0.0, 'draw': 1.0, 'away': 0.0},
               'A': {'home': 0.0, 'draw': 0.0, 'away': 1.0}}.get((r.get('ftr') or '').strip())
        agree = None
        if exp:
            agree = all(v['payout'] is None or abs(v['payout'] - exp[k]) < 1e-9 for k, v in mem.items())
        matches.append({'event_id': e['event_id'], 'slug': e['slug'], 'title': e['title'], 'div': div,
                        'extra': r['extra'], 'ko': e['ko'], 'fd_ko': r['ko'], 'ko_diff_h': (r['ko'] - e['ko']) / HOUR,
                        'swapped': sw, 'sim': [round(sa, 3), round(sb, 3)], 'score': round(sc, 3),
                        'fd': {k: r[k] for k in ('home', 'away', 'date', 'time', 'ftr', 'fthg', 'ftag', 'pre_src',
                                                 'pre', 'close_src', 'close', 'bfe', 'avg_pre', 'avg_close',
                                                 'season')},
                        'members': mem, 'result_agrees': agree})
        stats['matched'] += 1
        stats['matched_extra' if r['extra'] else 'matched_main'] += 1
    # one Polymarket event per fixture: a duplicate claim on the same fixture is ambiguous, drop both
    claim = collections.Counter((m['div'], m['fd']['home'], m['fd']['away'], m['fd']['date']) for m in matches)
    dup = {k for k, v in claim.items() if v > 1}
    if dup:
        stats['dropped_duplicate_fixture'] = sum(claim[k] for k in dup)
        matches = [m for m in matches if (m['div'], m['fd']['home'], m['fd']['away'], m['fd']['date']) not in dup]
    PH.write_gz(out / 'raw' / 'matches.json.gz', matches)
    PH.write_gz(out / 'raw' / 'unmatched.json.gz', unmatched)
    rng = random.Random(14)
    hand = rng.sample(matches, min(40, len(matches)))
    summary = {'generated': PH.utc(), 'pm_soccer_events': len(events), 'stats': dict(stats),
               'fd_fixtures': len(fd), 'result_agrees': collections.Counter(str(m['result_agrees']) for m in matches),
               'hand_check_sample': [{'pm': m['title'], 'fd': '%s v %s' % (m['fd']['home'], m['fd']['away']),
                                      'div': m['div'], 'pm_ko': PH.utc(m['ko']), 'fd_ko_diff_h': round(m['ko_diff_h'], 2),
                                      'swapped': m['swapped'], 'sim': m['sim'], 'ftr': m['fd']['ftr'],
                                      'agrees': m['result_agrees']} for m in hand]}
    PH.write_json(out / 'raw' / 'match_summary.json', summary)
    PH.update_manifest(out, 'match', {'generated': summary['generated'], 'seconds': round(time.time() - t0, 1),
                                      'stats': dict(stats)})
    print(json.dumps({k: v for k, v in summary.items() if k != 'hand_check_sample'}, default=str))
    return 0


# ------------------------------------------------------------------------------------------------- complete events

def member_roles(title, markets):
    """Polymarket moneyline members of one match event -> {'A'|'B'|'draw': market}, by groupItemTitle against the
    'A vs. B' title (question text as a fallback)."""
    if ' vs. ' not in (title or ''):
        return {}
    a, b = [x.strip() for x in title.split(' vs. ', 1)]
    out = {}
    for m in markets:
        g = (m.get('groupItemTitle') or '').strip()
        q = m.get('question') or ''
        if g.lower().startswith('draw') or 'end in a draw' in q.lower():
            role = 'draw'
        elif g == a:
            role = 'A'
        elif g == b:
            role = 'B'
        else:
            role = 'A' if (a and a in q) else ('B' if (b and b in q) else None)
        if role and role not in out:
            out[role] = m
    return out


def cmd_complete(args):
    """The stored universe keeps only markets with >= $10k lifetime volume, so a match event can be missing the members
    that traded little - and in-play volume depends on the result, so which members survive the filter is correlated
    with the outcome. Rebuild every matched event from gamma with all of home, draw and away."""
    out = Path(args.out)
    matches = PH.read_gz(out / 'raw' / 'matches.json.gz')
    http = PH.Http(interval=args.interval)
    t0 = time.time()
    ids = [m['event_id'] for m in matches]
    got = {}
    for i in range(0, len(ids), 25):
        chunk = ids[i:i + 25]
        q = urllib.parse.urlencode([('id', x) for x in chunk] + [('limit', 50)])
        d = http.request(PH.GAMMA + '/events?' + q)
        if not isinstance(d, list):
            continue
        for e in d:
            got[str(e.get('id'))] = e
    stats = collections.Counter()
    for m in matches:
        e = got.get(str(m['event_id']))
        m['members_in_universe'] = sorted(m['members'])
        if not e:
            stats['event_not_returned'] += 1
            continue
        ml = [PH.compact_market(x) for x in e.get('markets') or [] if x.get('sportsMarketType') == 'moneyline']
        roles = member_roles(e.get('title') or m['title'], ml)
        conv = {'draw': 'draw', 'A': 'away' if m['swapped'] else 'home', 'B': 'home' if m['swapped'] else 'away'}
        full = {}
        for r, x in roles.items():
            full[conv[r]] = {'id': x['id'], 'token': (x.get('clobTokenIds') or [None])[0], 'payout': PH.binary_payout(x),
                             'volume': x.get('volumeNum'), 'closed': x.get('closedTime'), 'question': x.get('question'),
                             'conditionId': x.get('conditionId'), 'fee_type': x.get('feeType')}
        for r, v in m['members'].items():           # keep what the universe had if gamma lost a member
            full.setdefault(r, v)
        stats['members_before_%d' % len(m['members'])] += 1
        stats['members_after_%d' % len(full)] += 1
        m['members'] = full
        exp = {'H': {'home': 1.0, 'draw': 0.0, 'away': 0.0}, 'D': {'home': 0.0, 'draw': 1.0, 'away': 0.0},
               'A': {'home': 0.0, 'draw': 0.0, 'away': 1.0}}.get((m['fd'].get('ftr') or '').strip())
        if exp:
            m['result_agrees'] = all(v['payout'] is None or abs(v['payout'] - exp[k]) < 1e-9 for k, v in full.items())
        stats['result_agrees_%s' % m['result_agrees']] += 1
    PH.write_gz(out / 'raw' / 'matches_full.json.gz', matches)
    PH.update_manifest(out, 'complete', {'generated': PH.utc(), 'source': PH.GAMMA + '/events?id=... (25 per request)',
                                         'events': len(ids), 'returned': len(got), 'stats': dict(stats),
                                         'http': http.stats(), 'seconds': round(time.time() - t0, 1)})
    print(json.dumps({'events': len(ids), 'returned': len(got), **stats, **http.stats()}))
    return 0


# ------------------------------------------------------------------------------------------------- prices

def series_path(out, mid):
    return Path(out) / 'raw' / 'prices' / str(mid)[-2:] / ('%s_w.json.gz' % mid)


def load_window(out, mid):
    """Hourly YES midpoints around kick-off: this study's fetch, else the stored sample's fine series."""
    p = series_path(out, mid)
    if p.exists():
        s = PH.read_gz(p)
        return sorted(s) if s else []
    p = PH.price_path(HIST, mid, 'f')
    if p.exists():
        return sorted(PH.read_gz(p))
    return None


def load_matches(out):
    p = Path(out) / 'raw' / 'matches_full.json.gz'
    return PH.read_gz(p if p.exists() else Path(out) / 'raw' / 'matches.json.gz')


def cmd_prices(args):
    out = Path(args.out)
    matches = load_matches(out)
    todo = []
    for m in matches:
        if m['extra'] and not args.extra:
            continue
        for role, v in m['members'].items():
            if not v.get('token'):
                continue
            if series_path(out, v['id']).exists() or PH.price_path(HIST, v['id'], 'f').exists():
                continue
            todo.append((v['id'], v['token'], m['ko']))
    http = PH.Http(interval=args.interval)
    t0 = time.time()
    done = [0]
    errs = []

    def one(x):
        mid, tok, ko = x
        s, err = PH.fetch_prices(http, tok, coarse=False, start=ko - 30 * HOUR, end=ko + HOUR, fidelity=60)
        if s is None:
            errs.append({'id': mid, 'error': err})
            return
        PH.write_gz(series_path(out, mid), s)
        done[0] += 1
        if done[0] % 500 == 0:
            print(json.dumps({'done': done[0], 'todo': len(todo), 'elapsed_s': round(time.time() - t0),
                              **http.stats()}), flush=True)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(one, todo))
    PH.update_manifest(out, 'prices_%s%s' % (int(t0), '_extra' if args.extra else ''), {
        'fetched_at': PH.utc(t0), 'finished_at': PH.utc(), 'source': PH.CLOB + '/prices-history (startTs/endTs, '
        'fidelity 60, [kick-off - 30h, kick-off + 1h])', 'markets': len(todo), 'written': done[0],
        'errors': len(errs), 'error_sample': errs[:5], 'http': http.stats(),
        'reused_from': str(HIST / 'raw' / 'prices') + ' (fine series of the 2026-10-09 sample)'})
    print(json.dumps({'todo': len(todo), 'written': done[0], 'errors': len(errs), **http.stats()}))
    return 0


# ------------------------------------------------------------------------------------------------- live books

def cmd_live(args):
    """Open soccer and tennis moneyline books starting within the next `hours`: half-spread and touch depth by price
    band and hours to start. These are the executable costs the backtest charges."""
    out = Path(args.out)
    http = PH.Http(interval=args.interval)
    t0 = time.time()
    now = time.time()
    rows = []
    for tag, horizon_end in (('soccer', now + args.hours * HOUR), ('tennis', now + (args.hours + 8 * 24) * HOUR)):
        evs = PH.paginate_events(http, {'closed': 'false', 'active': 'true', 'tag_slug': tag,
                                        'end_date_min': PH.utc(now), 'end_date_max': PH.utc(horizon_end)})
        for e in evs:
            prefix = (e.get('slug') or '').split('-')[0]
            for m in e.get('markets') or []:
                if m.get('sportsMarketType') != 'moneyline' or m.get('closed') or not m.get('acceptingOrders'):
                    continue
                gs = PH.parse_ts(m.get('gameStartTime'))
                if not gs or not (now + 0.25 * HOUR <= gs <= now + args.hours * HOUR):
                    continue
                toks = PH.jload(m.get('clobTokenIds'), [])
                if not toks:
                    continue
                rows.append({'sport': tag, 'event': e.get('id'), 'slug': e.get('slug'), 'prefix': prefix,
                             'market': m.get('id'), 'q': m.get('question'), 'group': m.get('groupItemTitle'),
                             'token': toks[0], 'start': gs, 'tts_h': (gs - now) / HOUR,
                             'volume': PH.fnum(m.get('volumeNum')), 'fee_type': m.get('feeType'),
                             'fees_enabled': m.get('feesEnabled'), 'fee_schedule': m.get('feeSchedule')})
    books = PH.fetch_books(http, [r['token'] for r in rows])
    for r in rows:
        b = books.get(r['token'])
        r['book'] = b
    snap = {'at': PH.utc(now), 'hours': args.hours, 'rows': rows, 'http': http.stats(),
            'seconds': round(time.time() - t0, 1)}
    PH.write_gz(out / 'raw' / 'live' / ('snap_%d.json.gz' % int(now)), snap)
    PH.update_manifest(out, 'live_%d' % int(now), {'at': snap['at'], 'markets': len(rows),
                                                   'books': sum(1 for r in rows if r['book']),
                                                   'source': PH.GAMMA + '/events/keyset + ' + PH.CLOB + '/books',
                                                   'http': http.stats()})
    print(json.dumps({'at': snap['at'], 'markets': len(rows), 'books': sum(1 for r in rows if r['book']),
                      'by_sport': collections.Counter(r['sport'] for r in rows), **http.stats()}, default=str))
    return 0


def book_stats(book):
    asks, bids = book.get('asks') or [], book.get('bids') or []
    if not asks or not bids:
        return None
    ba, bb = asks[0][0], bids[0][0]
    if ba <= bb:
        return None
    mid = (ba + bb) / 2.0
    return {'mid': mid, 'hs': (ba - bb) / 2.0, 'ask': ba, 'bid': bb,
            'ask_usd_best': ba * asks[0][1], 'bid_usd_best': (1.0 - bb) * bids[0][1],   # buying NO at 1 - bid
            'ask_usd_2c': sum(p * s for p, s in asks if p <= ba + 0.02 + 1e-9),
            'bid_usd_2c': sum((1.0 - p) * s for p, s in bids if p >= bb - 0.02 - 1e-9)}


def live_tables(out):
    snaps = sorted((Path(out) / 'raw' / 'live').glob('snap_*.json.gz'))
    recs = []
    for sp in snaps:
        s = PH.read_gz(sp)
        for r in s['rows']:
            st = book_stats(r['book']) if r.get('book') else None
            if not st:
                continue
            tier = 'top5' if SLUG_DIV.get(r['prefix']) in TOP5 else ('main' if r['prefix'] in SLUG_DIV else 'other')
            recs.append({'sport': r['sport'], 'band': band10(st['mid']), 'tts': r['tts_h'], 'tier': tier,
                         'snap': s['at'], **st})
    res = {'snapshots': [sp.name for sp in snaps], 'n_books': len(recs), 'hs': {}, 'depth': {}}

    def summ(sel):
        hs = sorted(x['hs'] for x in sel)
        dep = sorted(min(x['ask_usd_best'], 1e9) for x in sel)
        d2 = sorted(x['ask_usd_2c'] for x in sel)
        return {'n': len(sel), 'hs_median': statistics.median(hs), 'hs_p75': hs[int(0.75 * (len(hs) - 1))],
                'ask_usd_best_median': statistics.median(dep), 'ask_usd_best_p25': dep[int(0.25 * (len(dep) - 1))],
                'ask_usd_2c_median': statistics.median(d2)}

    for sport in ('soccer', 'tennis'):
        for band in range(10):
            for tb, (lo, hi) in {'0-3h': (0, 3), '3-12h': (3, 12), '12-30h': (12, 30), '0-30h': (0, 30),
                                 '0-96h': (0, 96)}.items():
                sel = [x for x in recs if x['sport'] == sport and x['band'] == band and lo <= x['tts'] < hi]
                if sel:
                    res['hs']['%s|b%d|%s' % (sport, band, tb)] = summ(sel)
                for tier in ('top5', 'main', 'other'):
                    sel2 = [x for x in sel if x['tier'] == tier]
                    if sel2 and tb == '0-96h':
                        res['hs']['%s|b%d|%s|%s' % (sport, band, tb, tier)] = summ(sel2)
    return res


def hs_model(live, sport='soccer', min_n=8):
    """Half-spread by YES-mid band and league tier (the NO side's spread is the same book's). Tier 'top5' uses the
    top-five leagues' books, tier 'rest' the other main divisions' books; 0-96h medians (spreads narrow towards
    kick-off, so this is conservative for decisions inside 24h); a band with fewer than `min_n` books takes the tier's
    pooled median; floor half a cent."""
    model = {}
    for tier, key in (('top5', 'top5'), ('rest', 'main')):
        vals = [(b, live['hs'].get('%s|b%d|0-96h|%s' % (sport, b, key))) for b in range(10)]
        pooled_src = [v['hs_median'] for b, v in vals if v and v['n'] >= min_n]
        pooled = statistics.median(pooled_src) if pooled_src else 0.01
        model[tier] = {b: max(0.005, v['hs_median']) if (v and v['n'] >= min_n) else max(0.005, pooled)
                       for b, v in vals}
    return model


def depth_model(live, sport='soccer', min_n=8):
    """Median USD at the best ask by band and tier (0-96h books), the same fallbacks as hs_model."""
    model = {}
    for tier, key in (('top5', 'top5'), ('rest', 'main')):
        vals = [(b, live['hs'].get('%s|b%d|0-96h|%s' % (sport, b, key))) for b in range(10)]
        pooled_src = [v['ask_usd_best_median'] for b, v in vals if v and v['n'] >= min_n]
        pooled = statistics.median(pooled_src) if pooled_src else 0.0
        model[tier] = {b: v['ask_usd_best_median'] if (v and v['n'] >= min_n) else pooled for b, v in vals}
    return model


def tier_of(div):
    return 'top5' if div in TOP5 else 'rest'


# ------------------------------------------------------------------------------------------------- analysis

def mid_at(series, t):
    """The hourly midpoint known at t: the last point at or before t + 2 minutes (points land seconds after the hour),
    only if the series had started by t (the market existed)."""
    if not series or series[0][0] > t + 120:
        return None
    return PH.as_of(series, t + 120, max_stale=36 * HOUR)


def build_candidates(m, series, h, fair, hs, delay_h=0.0, prints=None):
    """Every member-side of one match at decision time ko - h (+ delay): taker and maker economics. `hs` is the
    tier -> band -> half-spread model."""
    ko = m['ko']
    hs = hs[tier_of(m['div'])]
    t = ko - h * HOUR + delay_h * HOUR
    out = []
    for role, v in m['members'].items():
        s = series.get(v['id'])
        if not s:
            continue
        mid = mid_at(s, t)
        if mid is None or not (MID_MIN <= mid <= MID_MAX):
            continue
        later = [p for (ts, p) in s if t + 120 < ts <= ko + 60]
        hs_m = hs[band10(mid)]
        for side in (0, 1):
            p, f, pay = side_view(mid, fair[role], v['payout'], side)
            if pay is None:
                continue
            cost, ask = taker_cost(p, hs_m)
            lim = maker_limit(p, hs_m)
            usd_through = None
            if prints is not None:
                filled, usd_through = print_fill(prints[v['id']], side, lim, t + 60, ko)
            else:
                later_side = [(x if side == 0 else 1.0 - x) for x in later]
                filled = maker_filled(lim, later_side)
            out.append({'role': role, 'side': side, 'otype': otype_of(role, fair), 'mid': p, 'fair': f, 'pay': pay,
                        'ask': ask, 'cost': cost, 'ev': expected_return(f, cost), 'ret': pay / cost - 1.0,
                        'limit': lim, 'ev_m': expected_return(f, lim), 'filled': filled,
                        'ret_m': (pay / lim - 1.0) if filled else None, 'member_id': v['id'],
                        'usd_through': usd_through})
    return out


def analyze_core(out, matches, series, hs, devig_method='shin', odds_kind='pre', delay_h=0.0, horizons=HORIZONS_H,
                 prints=None, complete=True):
    """Trades of every pre-registered variant. Returns {variant: [trade dicts]} and the eligibility counts."""
    trades = collections.defaultdict(list)
    elig = collections.Counter()
    for m in matches:
        if m['extra']:
            continue
        if abs(m['ko_diff_h']) > KO_TOL_H:
            elig['kickoff_disagrees'] += 1
            continue
        if complete and (len(m['members']) < 3 or any(v['id'] not in series for v in m['members'].values())):
            elig['incomplete_event_or_series'] += 1     # all of home, draw and away, or the match is not traded
            continue
        if prints is not None and any(v['id'] not in prints for v in m['members'].values()):
            elig['no_prints'] += 1
            continue
        odds = {'pre': m['fd']['pre'], 'close': m['fd']['close'], 'bfe': m['fd']['bfe']}[odds_kind]
        fair_l = devig(odds, devig_method) if odds else None
        if not fair_l:
            elig['no_odds'] += 1
            continue
        fair = {'home': fair_l[0], 'draw': fair_l[1], 'away': fair_l[2]}
        avail = fd_available(m['fd_ko']) if odds_kind in ('pre', 'bfe') else m['ko']
        tier = tier_of(m['div'])
        for h in horizons:
            t = m['ko'] - h * HOUR
            if odds_kind in ('pre', 'bfe') and t < avail:
                elig['h%d_odds_not_yet_collected' % h] += 1
                continue
            cands = build_candidates(m, series, h, fair, hs, delay_h=delay_h, prints=prints)
            if not cands:
                elig['h%d_no_price' % h] += 1
                continue
            elig['h%d_priced' % h] += 1
            for thr in THRESHOLDS:
                for ot in OTYPES:
                    tk = pick_signal(cands, thr, ot)
                    mk = pick_signal([dict(c, ev=c['ev_m']) for c in cands], thr, ot)
                    for tr_name in ('all', tier):
                        if tk:
                            trades['taker|h%d|thr%.2f|%s|%s' % (h, thr, ot, tr_name)].append(
                                dict(tk, event_id=m['event_id'], ko=m['ko'], div=m['div'], tier=tier, h=h,
                                     r=tk['ret'], price=tk['ask'], stake_cost=tk['cost']))
                        if mk:
                            trades['maker|h%d|thr%.2f|%s|%s' % (h, thr, ot, tr_name)].append(
                                dict(mk, event_id=m['event_id'], ko=m['ko'], div=m['div'], tier=tier, h=h,
                                     r=(mk['ret_m'] if mk['filled'] else 0.0), price=mk['limit'],
                                     stake_cost=mk['limit']))
    return trades, elig


def daily_axis(matches):
    ds = sorted({dt.datetime.fromtimestamp(m['ko'], UTC).date() for m in matches if not m['extra']})
    if not ds:
        return []
    d0, d1 = ds[0], ds[-1]
    return [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]


def daily_series(trades, axis):
    idx = {d: i for i, d in enumerate(axis)}
    s = [0.0] * len(axis)
    for t in trades:
        d = dt.datetime.fromtimestamp(t['ko'], UTC).date()
        if d in idx and t['r'] is not None:
            s[idx[d]] += t['r']
    return s


def trade_stats(trades, filled_only=False):
    rs = [t['r'] for t in trades if t['r'] is not None and (not filled_only or t.get('filled', True))]
    if not rs:
        return {'n': 0}
    ev = [t['ev'] for t in trades if t.get('ev') is not None]
    ci = PH.wilson(sum(1 for x in rs if x > 0), len(rs))
    sd = statistics.pstdev(rs) if len(rs) > 1 else 0.0
    return {'n': len(rs), 'mean_ret': sum(rs) / len(rs), 'se': sd / math.sqrt(len(rs)) if len(rs) > 1 else None,
            'hit': sum(1 for x in rs if x > 0) / len(rs), 'hit_ci': ci, 'mean_ev': (sum(ev) / len(ev)) if ev else None,
            'mean_price': statistics.mean(t['price'] for t in trades)}


def cluster_ci(values_by_cluster, n=1000, seed=3):
    """Mean of per-item values with a cluster (event) bootstrap interval. values_by_cluster: list of lists."""
    flat = [x for c in values_by_cluster for x in c]
    if not flat:
        return None
    rng = random.Random(seed)
    k = len(values_by_cluster)
    boots = []
    for _ in range(n):
        tot = cnt = 0
        for _ in range(k):
            c = values_by_cluster[rng.randrange(k)]
            tot += sum(c)
            cnt += len(c)
        if cnt:
            boots.append(tot / cnt)
    boots.sort()
    return {'mean': sum(flat) / len(flat), 'lo': boots[int(0.025 * (len(boots) - 1))],
            'hi': boots[int(0.975 * (len(boots) - 1))], 'n': len(flat), 'clusters': k}


def logit(p):
    p = min(1 - 1e-6, max(1e-6, p))
    return math.log(p / (1 - p))


def brier(pairs):
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs) if pairs else None


def logloss(pairs):
    return -sum(y * math.log(min(1 - 1e-6, max(1e-6, p))) + (1 - y) * math.log(min(1 - 1e-6, max(1e-6, 1 - p)))
                for p, y in pairs) / len(pairs) if pairs else None


def biases(matches, series, h=2, odds_kind='pre', extra=False):
    """Polymarket midpoint minus the de-vigged consensus, per member, at ko - h, by outcome role, favourite status and
    fair-probability band, with event-clustered intervals; plus Brier/log-loss of both against results."""
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    acc_pm, acc_fair = [], []
    pop = collections.Counter()
    for m in matches:
        for v in m['members'].values():
            pop[m['fd']['home']] += 0
    for m in matches:
        if m['extra'] != extra or abs(m['ko_diff_h']) > KO_TOL_H:
            continue
        if len(m['members']) < 3 or any(v['id'] not in series for v in m['members'].values()):
            continue
        odds = m['fd']['pre'] if odds_kind == 'pre' else m['fd']['close']
        fl = devig_shin(odds) if odds else None
        if not fl:
            continue
        fair = {'home': fl[0], 'draw': fl[1], 'away': fl[2]}
        t = m['ko'] - h * HOUR
        if odds_kind == 'pre' and t < fd_available(m['fd_ko']):
            continue
        for role, v in m['members'].items():
            s = series.get(v['id'])
            mid = mid_at(s, t) if s else None
            if mid is None or v['payout'] not in (0.0, 1.0):
                continue
            d = mid - fair[role]
            ot = otype_of(role, fair)
            fb = '%.1f' % (min(0.9, int(fair[role] * 10) / 10.0))
            for key in ('role:' + role, 'otype:' + ot, 'fairband:' + fb, 'all:all',
                        'tier:' + ('top5' if m['div'] in TOP5 else ('extra' if m['extra'] else 'rest'))):
                by[key][m['event_id']].append(d)
            acc_pm.append((mid, v['payout']))
            acc_fair.append((fair[role], v['payout']))
    res = {}
    for key, cl in by.items():
        res[key] = cluster_ci(list(cl.values()))
    res['accuracy'] = {'n': len(acc_pm), 'brier_pm': brier(acc_pm), 'brier_fair': brier(acc_fair),
                       'logloss_pm': logloss(acc_pm), 'logloss_fair': logloss(acc_fair)}
    return res


def popular_bias(matches, series, h=2, top_n=20):
    """'Popular' teams = the top_n by total Polymarket volume of their own win market in matched main-league games.
    Bias = midpoint minus fair for those teams' win markets against everyone else's."""
    vol = collections.Counter()
    for m in matches:
        if m['extra']:
            continue
        for role in ('home', 'away'):
            v = m['members'].get(role)
            if v:
                vol[m['fd'][role]] += v.get('volume') or 0.0
    popular = {k for k, _ in vol.most_common(top_n)}
    grp = {'popular': collections.defaultdict(list), 'other': collections.defaultdict(list)}
    for m in matches:
        if m['extra'] or abs(m['ko_diff_h']) > KO_TOL_H:
            continue
        if len(m['members']) < 3 or any(v['id'] not in series for v in m['members'].values()):
            continue
        fl = devig_shin(m['fd']['pre']) if m['fd']['pre'] else None
        if not fl:
            continue
        t = m['ko'] - h * HOUR
        if t < fd_available(m['fd_ko']):
            continue
        fair = {'home': fl[0], 'draw': fl[1], 'away': fl[2]}
        for role in ('home', 'away'):
            v = m['members'].get(role)
            s = series.get(v['id']) if v else None
            mid = mid_at(s, t) if s else None
            if mid is None:
                continue
            g = 'popular' if m['fd'][role] in popular else 'other'
            grp[g][m['event_id']].append(mid - fair[role])
    return {'popular_teams': sorted(popular), 'popular': cluster_ci(list(grp['popular'].values())),
            'other': cluster_ci(list(grp['other'].values()))}


def peak_capital(trades, stake):
    ev = []
    for t in trades:
        if t['r'] is None or (t.get('filled') is False):
            continue
        st = t['ko'] - t['h'] * HOUR
        ev.append((st, stake))
        ev.append((t['ko'] + SETTLE_AFTER_H * HOUR, -stake))
    ev.sort()
    cur = peak = 0.0
    for _, x in ev:
        cur += x
        peak = max(peak, cur)
    return peak


def late_entry(trades, matches_by_id, series, hs, split_epoch, execution, prints=None):
    """Same signal (member and side fixed at the decision), entered one hour later at that hour's price."""
    rows = []
    for t in trades:
        m = matches_by_id[t['event_id']]
        fl = devig(m['fd']['pre'], 'shin')
        fair = {'home': fl[0], 'draw': fl[1], 'away': fl[2]}
        later = [c for c in build_candidates(m, series, t['h'], fair, hs, delay_h=1.0, prints=prints)
                 if c['role'] == t['role'] and c['side'] == t['side']]
        if not later:
            continue
        c = later[0]
        r_late = c['ret'] if execution == 'taker' else (c['ret_m'] if c['filled'] else 0.0)
        rows.append((t['r'], r_late, t['ko']))

    def share(rr):
        a = sum(x[0] for x in rr)
        b = sum(x[1] for x in rr)
        return {'n': len(rr), 'orig_mean': a / len(rr) if rr else None, 'late_mean': b / len(rr) if rr else None,
                'share_kept': (b / a) if a else None}
    return {'all': share(rows), 'oos': share([x for x in rows if x[2] >= split_epoch]),
            'dropped_no_price_later': len(trades) - len(rows)}


def selection_report(matches, series, fd_rows, h=2):
    """How the stored universe's $10k-volume filter biases outcome rates. Member level: YES rate against the
    Polymarket midpoint at ko - h and against the closing consensus, for members that were in the universe (of
    complete and of incomplete events), for members added from gamma, and for all members after the fix. Event level:
    the consensus calibration (result minus Shin closing probability) on the matched events against every
    football-data fixture of the same divisions and dates (which no Polymarket filter touches)."""
    grp = collections.defaultdict(lambda: collections.defaultdict(list))
    agg = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    for m in matches:
        if m['extra'] or abs(m['ko_diff_h']) > KO_TOL_H or not m['fd']['close']:
            continue
        fl = devig_shin(m['fd']['close'])
        fair = {'home': fl[0], 'draw': fl[1], 'away': fl[2]}
        inu = set(m.get('members_in_universe') or m['members'])
        complete_before = len(inu) == 3
        for role, v in m['members'].items():
            s = series.get(v['id'])
            mid = mid_at(s, m['ko'] - h * HOUR) if s else None
            if mid is None or v['payout'] not in (0.0, 1.0):
                continue
            keys = ['after_fix_all']
            if role in inu:
                keys.append('universe_member_' + ('complete_event' if complete_before else 'incomplete_event'))
                keys.append('universe_members_all')
            else:
                keys.append('added_from_gamma')
            for k in keys:
                grp[k][m['event_id']].append(v['payout'] - mid)
                a = agg[k]
                a[0] += 1
                a[1] += v['payout']
                a[2] += mid
                a[3] += fair[role]
    res = {}
    for k, cl in grp.items():
        n, y, pm, f = agg[k]
        res[k] = {'members': n, 'yes_rate': y / n, 'mean_mid': pm / n, 'mean_fair_close': f / n,
                  'rate_minus_mid': cluster_ci(list(cl.values()))}
    # event level: the consensus' calibration on matched events vs all fixtures in the same divisions and window
    mk = {(m['div'], m['fd']['home'], m['fd']['away'], m['fd']['date']) for m in matches if not m['extra']}
    divs = {m['div'] for m in matches if not m['extra']}
    kos = [m['ko'] for m in matches if not m['extra']]
    lo, hi = min(kos), max(kos)
    cal = {'matched': collections.defaultdict(list), 'all_fd': collections.defaultdict(list)}
    for r in fd_rows:
        if r['extra'] or r['div'] not in divs or not (lo <= r['ko'] <= hi) or not r['close']:
            continue
        res_ = {'H': 'home', 'D': 'draw', 'A': 'away'}.get((r.get('ftr') or '').strip())
        if not res_:
            continue
        fl = devig_shin(r['close'])
        key = (r['div'], r['home'], r['away'], r['date'])
        for i, role in enumerate(('home', 'draw', 'away')):
            y = 1.0 if role == res_ else 0.0
            band = 'fav' if role != 'draw' and fl[i] >= max(fl[0], fl[2]) else ('draw' if role == 'draw' else 'dog')
            cal['all_fd'][band].append(y - fl[i])
            if key in mk:
                cal['matched'][band].append(y - fl[i])
    res['event_level_calibration'] = {
        g: {b: {'n': len(v), 'result_minus_fair': sum(v) / len(v)} for b, v in d.items()} for g, d in cal.items()}
    return res


def load_prints(out, main):
    """Stored YES-normalised taker prints per member, when the prints step has covered every main-league member."""
    d = {}
    for m in main:
        for v in m['members'].values():
            p = prints_path(out, v['id'])
            if p.exists():
                d[v['id']] = PH.read_gz(p)
    return d


def cmd_analyze(args):
    out = Path(args.out)
    t0 = time.time()
    matches = load_matches(out)
    msum = json.loads((out / 'raw' / 'match_summary.json').read_text())
    live = live_tables(out)
    hs = hs_model(live, 'soccer')
    depth = depth_model(live, 'soccer')
    series = {}
    for m in matches:
        for v in m['members'].values():
            s = load_window(out, v['id'])
            if s is not None:
                series[v['id']] = s
    main = [m for m in matches if not m['extra']]
    by_id = {m['event_id']: m for m in main}
    res = {'generated': PH.utc(), 'ssr': SSR, 'fee_rate_sports': SPORTS_RATE,
           'preregistration': {
               'fixed_at': '2026-10-14T07:30:00+00:00 (script written before any return was computed). Changed '
                           'before any return was looked at: 07:38 kick-off tolerance (data hygiene after a '
                           'price-vs-fair check, no outcomes used); 07:41 half-spread and depth made tier-specific '
                           'after reading the live books',
               'fair_value': 'Shin de-vig of football-data pre-closing odds: Pinnacle (PSH/PSD/PSA) when all three '
                             'present, else the market average (AvgH/AvgD/AvgA)',
               'decision_times_h': HORIZONS_H, 'thresholds_ev': THRESHOLDS, 'outcome_types': OTYPES,
               'tiers': TIERS, 'executions': EXECS, 'n_variants': len(variant_names()),
               'one_trade_per_match': 'the member-side with the largest expected return clearing the threshold',
               'mid_filter': [MID_MIN, MID_MAX],
               'maker_fill': 'limit at the bid (mid - half-spread); fills only if a later hourly mid before kick-off '
                             'is <= limit - %.2f; unfilled orders earn 0' % MAKER_THROUGH,
               'taker_cost': 'mid + half-spread(tier, band) + 0.05 x p x (1 - p)',
               'odds_availability': '18:00 London on the latest Tuesday/Friday before kick-off (same-day Tue/Fri '
                                    'kick-offs before 18:00: no decision)',
               'split': 'choose on matches kicking off before the median matched kick-off date; test once after',
               'return_series': 'daily sum of per-$1 returns of trades by kick-off date (backtest.choose_then_test, '
                                'periods_per_year 365)',
               'sensitivities_not_selected_on': ['multiplicative de-vig', 'closing odds (look-ahead)',
                                                 'Betfair Exchange pre-closing as fair value', 'late entry +1h',
                                                 'p75 half-spread']},
           'match': msum, 'live': live, 'half_spread_model': hs, 'depth_model_usd_best_ask': depth}
    cov = collections.Counter()
    for m in main:
        cov['events'] += 1
        cov['members'] += len(m['members'])
        cov['members_with_series'] += sum(1 for v in m['members'].values() if v['id'] in series)
        cov['pre_src_' + str(m['fd']['pre_src'])] += 1
        cov['result_agrees_' + str(m['result_agrees'])] += 1
        cov['tier_' + tier_of(m['div'])] += 1
        cov['members_in_universe_%d' % len(m.get('members_in_universe') or m['members'])] += 1
        cov['complete_with_series'] += int(len(m['members']) == 3 and all(v['id'] in series
                                                                          for v in m['members'].values()))
    res['coverage_main'] = dict(cov)
    kos = sorted(m['ko'] for m in main)
    split_ts = kos[len(kos) // 2]
    axis = daily_axis(matches)
    split_date = dt.datetime.fromtimestamp(split_ts, UTC).date()
    frac = axis.index(split_date) / len(axis)
    split_epoch = dt.datetime.combine(split_date, dt.time(0), UTC).timestamp()
    res['split'] = {'date': str(split_date), 'frac_of_days': frac, 'days': len(axis), 'first': str(axis[0]),
                    'last': str(axis[-1])}

    trades, elig = analyze_core(out, matches, series, hs, 'shin', 'pre')
    res['eligibility'] = dict(elig)
    names = variant_names()
    variants = {n: daily_series(trades.get(n, []), axis) for n in names}
    sel = B.choose_then_test(variants, frac=frac, periods_per_year=365)
    res['selection'] = {k: v for k, v in sel.items() if k != 'bh_adjusted_p'}
    res['selection']['bh_adjusted_p_chosen'] = sel['bh_adjusted_p'].get(sel['chosen'])
    per = {}
    for n in names:
        tr = trades.get(n, [])
        ins = [t for t in tr if t['ko'] < split_epoch]
        oos = [t for t in tr if t['ko'] >= split_epoch]
        t_full, p_full = B.newey_west_t(variants[n])
        per[n] = {'all': trade_stats(tr), 'in': trade_stats(ins), 'oos': trade_stats(oos), 'hac_t_full': t_full,
                  'maker_fill_rate': (sum(1 for t in tr if t.get('filled')) / len(tr)) if (tr and n.startswith('maker'))
                  else None}
    res['variants'] = per
    ch = sel['chosen']
    fam = {}
    for e in EXECS:
        sub = {n: variants[n] for n in names if n.startswith(e + '|')}
        s2 = B.choose_then_test(sub, frac=frac, periods_per_year=365)
        fam[e] = {k: v for k, v in s2.items() if k not in ('bh_adjusted_p',)}
    res['selection_by_execution'] = fam
    go = {'in_sample_positive': sel['in_sample_positive'], 'oos_t': sel['oos_t'],
          'oos_t_ge_2': (sel['oos_t'] or 0) >= 2.0, 'in_bh_survivors_positive': ch in sel['bh_survivors_positive']}
    # late entry for the chosen variant and for each execution's choice
    res['late_entry'] = {}
    for n in dict.fromkeys([ch, fam['taker']['chosen'], fam['maker']['chosen']]):
        res['late_entry'][n] = late_entry(trades.get(n, []), by_id, series, hs, split_epoch, n.split('|')[0])
    # sensitivities on the chosen variant (and the grid mean for the look-ahead)
    tr_close, _ = analyze_core(out, matches, series, hs, 'shin', 'close')
    tr_mult, _ = analyze_core(out, matches, series, hs, 'mult', 'pre')
    tr_bfe, _ = analyze_core(out, matches, series, hs, 'shin', 'bfe')
    hs75 = {}
    for tier, key in (('top5', 'top5'), ('rest', 'main')):
        hs75[tier] = {b: max(hs[tier][b], (live['hs'].get('soccer|b%d|0-96h|%s' % (b, key)) or {}).get('hs_p75', 0.0))
                      for b in range(10)}
    tr75, _ = analyze_core(out, matches, series, hs75, 'shin', 'pre')

    def grid_mean(tr):
        v = [trade_stats(tr[n])['mean_ret'] for n in names if len(tr.get(n, [])) >= 30]
        return statistics.mean(v) if v else None
    res['sensitivity'] = {
        'chosen': ch,
        'pre_shin': per[ch]['all'], 'pre_shin_oos': per[ch]['oos'],
        'close_shin_lookahead': trade_stats(tr_close.get(ch, [])),
        'close_shin_lookahead_oos': trade_stats([t for t in tr_close.get(ch, []) if t['ko'] >= split_epoch]),
        'pre_mult': trade_stats(tr_mult.get(ch, [])), 'bfe_shin': trade_stats(tr_bfe.get(ch, [])),
        'hs_p75': trade_stats(tr75.get(ch, [])),
        'grid_mean_ret': {'pre': grid_mean(trades), 'close_lookahead': grid_mean(tr_close), 'bfe': grid_mean(tr_bfe)}}
    # the best variant under each fair value, for the look-ahead accounting (descriptive)
    def best_of(tr):
        cand = [(trade_stats(tr[n])['mean_ret'], n, len(tr[n])) for n in names if len(tr.get(n, [])) >= 100]
        return max(cand) if cand else None
    res['sensitivity']['best_mean_ret_n100'] = {'pre': best_of(trades), 'close_lookahead': best_of(tr_close),
                                                'bfe': best_of(tr_bfe)}
    clv = []
    for t in trades.get(ch, []):
        if t.get('filled') is False and ch.startswith('maker'):
            continue                      # an unfilled resting order bought nothing
        m = by_id[t['event_id']]
        fl = devig_shin(m['fd']['close']) if m['fd']['close'] else None
        if not fl:
            continue
        f_close = {'home': fl[0], 'draw': fl[1], 'away': fl[2]}[t['role']]
        f_side = f_close if t['side'] == 0 else 1.0 - f_close
        clv.append(f_side / t['stake_cost'] - 1.0)
    res['clv_chosen'] = {'n': len(clv), 'mean': (sum(clv) / len(clv)) if clv else None,
                         'share_positive': (sum(1 for x in clv if x > 0) / len(clv)) if clv else None}
    # capacity: the touch depth for the traded band and tier; annual dollars net of the savings rate on peak capital
    ch_tr = trades.get(ch, [])
    oos_tr = [t for t in ch_tr if t['ko'] >= split_epoch]
    years = len(axis) / 365.0
    oos_years = (len(axis) - axis.index(split_date)) / 365.0
    if ch_tr:
        stake = lambda t: depth[t['tier']][band10(t['mid'])]  # noqa: E731
        stakes = [stake(t) for t in ch_tr]
        pnl_all = sum(t['r'] * stake(t) for t in ch_tr)
        pnl_oos = sum(t['r'] * stake(t) for t in oos_tr)
        cap = peak_capital(ch_tr, statistics.median(stakes))
        res['capacity'] = {'median_stake_usd': statistics.median(stakes), 'mean_stake_usd': statistics.mean(stakes),
                           'trades_per_year_all': len(ch_tr) / years, 'trades_per_year_oos': len(oos_tr) / oos_years,
                           'pnl_usd_per_year_all': pnl_all / years, 'pnl_usd_per_year_oos': pnl_oos / oos_years,
                           'peak_capital_usd': cap, 'ssr_cost_usd_per_year': SSR * cap,
                           'excess_usd_per_year_oos': pnl_oos / oos_years - SSR * cap,
                           'note': 'stake = median USD at the best ask in the live books for the band and tier '
                                   '(one fill per signal at the touch); years of the daily axis'}
        go['excess_over_ssr_positive'] = res['capacity']['excess_usd_per_year_oos'] > 0
    else:
        go['excess_over_ssr_positive'] = False
    go['go'] = all(v for k, v in go.items() if k != 'oos_t')
    res['go_rule'] = go
    # B. The protocol's resting-limit rule on real prints (the hourly-mid proxy above missed most fills: trades_check
    # found real prints through the limit in 104 of 300 sampled signals against 9 proxy fills). Same 216 variants;
    # the taker variants are unchanged, the maker variants are re-priced. Reported beside the pre-registered run.
    prints = load_prints(out, main)
    if prints:
        trp, elp = analyze_core(out, matches, series, hs, 'shin', 'pre', prints=prints)
        vp = {n: daily_series(trp.get(n, []), axis) for n in names}
        selp = B.choose_then_test(vp, frac=frac, periods_per_year=365)
        chp = selp['chosen']
        perp = {}
        for n in names:
            tr = trp.get(n, [])
            perp[n] = {'all': trade_stats(tr), 'in': trade_stats([t for t in tr if t['ko'] < split_epoch]),
                       'oos': trade_stats([t for t in tr if t['ko'] >= split_epoch]),
                       'hac_t_full': B.newey_west_t(vp[n])[0],
                       'fill_rate': (sum(1 for t in tr if t.get('filled')) / len(tr)) if (tr and n.startswith('maker'))
                       else None}
        famp = {}
        for e in EXECS:
            sub = {n: vp[n] for n in names if n.startswith(e + '|')}
            s2 = B.choose_then_test(sub, frac=frac, periods_per_year=365)
            famp[e] = {k: v for k, v in s2.items() if k not in ('bh_adjusted_p',)}
        gop = {'in_sample_positive': selp['in_sample_positive'], 'oos_t': selp['oos_t'],
               'oos_t_ge_2': (selp['oos_t'] or 0) >= 2.0, 'in_bh_survivors_positive': chp in selp['bh_survivors_positive']}
        ch_trp = trp.get(chp, [])
        oos_trp = [t for t in ch_trp if t['ko'] >= split_epoch]

        def stake_p(t):
            d = depth[t['tier']][band10(t['mid'])]
            if chp.startswith('maker'):
                return min(d, t.get('usd_through') or 0.0) if t.get('filled') else 0.0
            return d
        pnl_oos = sum(t['r'] * stake_p(t) for t in oos_trp)
        stakes = [stake_p(t) for t in ch_trp if stake_p(t) > 0]
        capp = peak_capital([t for t in ch_trp if stake_p(t) > 0], statistics.median(stakes)) if stakes else 0.0
        mk_fill = [t for t in trp.get(famp['maker']['chosen'], []) if t.get('filled')]
        clvp = []
        for t in mk_fill:
            fl = devig_shin(by_id[t['event_id']]['fd']['close']) if by_id[t['event_id']]['fd']['close'] else None
            if fl:
                fc = {'home': fl[0], 'draw': fl[1], 'away': fl[2]}[t['role']]
                clvp.append((fc if t['side'] == 0 else 1.0 - fc) / t['limit'] - 1.0)
        res['protocol_fills'] = {
            'note': 'maker fills on real taker prints strictly through the limit between the order and kick-off',
            'eligibility': dict(elp), 'selection': {k: v for k, v in selp.items() if k != 'bh_adjusted_p'},
            'selection_by_execution': famp, 'variants': perp, 'go_rule': gop,
            'late_entry': {n: late_entry(trp.get(n, []), by_id, series, hs, split_epoch, n.split('|')[0], prints=prints)
                           for n in dict.fromkeys([chp, famp['maker']['chosen']])},
            'clv_maker_choice_filled': {'variant': famp['maker']['chosen'], 'n': len(clvp),
                                        'mean': (sum(clvp) / len(clvp)) if clvp else None,
                                        'share_positive': (sum(1 for x in clvp if x > 0) / len(clvp)) if clvp else None},
            'capacity': {'chosen': chp, 'pnl_usd_per_year_oos': pnl_oos / oos_years, 'peak_capital_usd': capp,
                         'excess_usd_per_year_oos': pnl_oos / oos_years - SSR * capp,
                         'median_stake_usd': statistics.median(stakes) if stakes else None,
                         'note': 'maker stake = min(touch depth, USD traded through the limit) on filled orders'}}
        gop['excess_over_ssr_positive'] = res['protocol_fills']['capacity']['excess_usd_per_year_oos'] > 0
        gop['go'] = all(v for k, v in gop.items() if k != 'oos_t')
    res['bias'] = {}
    for h in HORIZONS_H:
        res['bias']['main_pre_h%d' % h] = biases(matches, series, h=h, odds_kind='pre')
    res['bias']['main_close_h2'] = biases(matches, series, h=2, odds_kind='close')
    res['bias']['main_close_h0'] = biases(matches, series, h=0, odds_kind='close')   # same time: PM at kick-off
    # Exploratory, post-hoc (added after the pre-registered grid was seen; never eligible for a go): what a trader
    # with a live sharp feed would see at kick-off - Polymarket's last pre-game midpoint against the closing consensus
    # taken at the same moment, as a taker, held to resolution.
    tr0, el0 = analyze_core(out, matches, series, hs, 'shin', 'close', horizons=[0])
    res['exploratory_same_time'] = {n: trade_stats(tr0.get(n, [])) for n in
                                    ['taker|h0|thr%.2f|%s|all' % (t, o) for t in THRESHOLDS for o in OTYPES]}
    res['exploratory_same_time_eligibility'] = dict(el0)
    res['bias']['extra_close_h2'] = biases(matches, series, h=2, odds_kind='close', extra=True)
    res['bias']['popular_h2'] = popular_bias(matches, series, h=2)
    res['bias']['tennis_close_h1'] = tennis_bias(out, h=1)
    res['universe_selection'] = selection_report(matches, series, load_fd(out), h=2)
    # Disclosure: the same pre-registered grid on the uncorrected universe (members as stored, incomplete events
    # allowed), to size what the $10k-volume filter would have done to the backtest.
    raw_matches = PH.read_gz(out / 'raw' / 'matches.json.gz')
    tr_raw, el_raw = analyze_core(out, raw_matches, series, hs, 'shin', 'pre', complete=False)
    v_raw = {n: daily_series(tr_raw.get(n, []), axis) for n in names}
    sel_raw = B.choose_then_test(v_raw, frac=frac, periods_per_year=365)

    def gm(tr, pre):
        v = [trade_stats(tr[n])['mean_ret'] for n in names if n.startswith(pre) and len(tr.get(n, [])) >= 30]
        return statistics.mean(v) if v else None
    res['uncorrected_universe_backtest'] = {
        'note': 'disclosure only: members as the $10k universe stored them; never a decision input',
        'eligibility': dict(el_raw), 'chosen': sel_raw['chosen'], 'oos_t': sel_raw['oos_t'],
        'in_sample_positive': sel_raw['in_sample_positive'], 'bh_survivors_positive': sel_raw['bh_survivors_positive'][:10],
        'chosen_stats': trade_stats(tr_raw.get(sel_raw['chosen'], [])),
        'grid_mean_ret_taker': {'uncorrected': gm(tr_raw, 'taker'), 'corrected': gm(trades, 'taker')},
        'grid_mean_ret_maker_proxy': {'uncorrected': gm(tr_raw, 'maker'), 'corrected': gm(trades, 'maker')},
        'taker_h2_thr0_all_all': {'uncorrected': trade_stats(tr_raw.get('taker|h2|thr0.00|all|all', [])),
                                  'corrected': trade_stats(trades.get('taker|h2|thr0.00|all|all', []))}}
    res['n_variants_tried'] = {'preregistered_grid': len(names), 'per_execution_reselection': 2,
                               'uncorrected_universe_disclosure_rerun': len(names),
                               'sensitivities_on_chosen': 5, 'exploratory_same_time_post_hoc': 12,
                               'maker_variants_repriced_on_prints': 108 if prints else 0,
                               'total_with_disclosure_reruns': 2 * len(names) + 2 + 5 + 12 + (108 if prints else 0)}
    res['seconds'] = round(time.time() - t0, 1)
    PH.write_json(out / 'analysis.json', res)
    PH.write_gz(out / 'raw' / 'trades_chosen.json.gz', {'chosen': ch, 'trades': ch_tr, 'split_epoch': split_epoch,
                                                       'taker_chosen': 'taker|h2|thr0.00|all|all',
                                                       'taker_trades': trades.get('taker|h2|thr0.00|all|all', [])})
    print(json.dumps({'chosen': ch, 'go_rule': go, 'oos': per[ch]['oos'], 'in': per[ch]['in'],
                      'bh_survivors_positive': sel['bh_survivors_positive'][:10], 'eligibility': dict(elig)},
                     default=str, indent=1))
    return 0


# ------------------------------------------------------------------------------------------------- trades check

# ------------------------------------------------------------------------------------------------- tennis (description)

def td_date(v):
    """tennis-data Date: an Excel serial (days since 1899-12-30) or dd/mm/yyyy."""
    x = fnum(v)
    if x is not None:
        return (dt.datetime(1899, 12, 30, tzinfo=UTC) + dt.timedelta(days=x)).date()
    try:
        return dt.datetime.strptime(str(v).strip()[:10], '%d/%m/%Y').date()
    except ValueError:
        return None


def td_player(name):
    """'Auger-Aliassime F.' -> ({'auger', 'aliassime'}, 'f'); the last token is the first-name initial(s)."""
    s = unicodedata.normalize('NFKD', (name or '').translate(TRANSLIT)).encode('ascii', 'ignore').decode().lower()
    toks = [t for t in re.split(r'[^a-z]+', s) if t]
    if len(toks) < 2:
        return set(toks), ''
    return set(toks[:-1]), toks[-1][0]


def pm_player_match(pm_name, td_name):
    """Every surname token of the tennis-data name appears in the Polymarket full name, and the first initial agrees."""
    sur, ini = td_player(td_name)
    s = unicodedata.normalize('NFKD', (pm_name or '').translate(TRANSLIT)).encode('ascii', 'ignore').decode().lower()
    toks = [t for t in re.split(r'[^a-z]+', s) if t]
    if not sur or not toks:
        return False
    return sur <= set(toks) and (not ini or toks[0][0] == ini)


def load_tennis(out):
    rows = []
    for p in sorted((Path(out) / 'raw' / 'tennis').glob('*.xlsx')):
        x = read_xlsx(p)
        hdr = x[0]
        for r in x[1:]:
            d = dict(zip(hdr, r))
            day = td_date(d.get('Date'))
            if day is None or not d.get('Winner'):
                continue
            ps = [fnum(d.get('PSW')), fnum(d.get('PSL'))]
            av = [fnum(d.get('AvgW')), fnum(d.get('AvgL'))]
            src, odds = ('pinnacle', ps) if implied(ps) else (('average', av) if implied(av) else (None, None))
            rows.append({'tour': 'wta' if 'w_' in p.name else 'atp', 'date': day, 'winner': d['Winner'],
                         'loser': d['Loser'], 'odds_src': src, 'odds_wl': odds, 'comment': d.get('Comment'),
                         'tournament': d.get('Tournament')})
    return rows


def cmd_tennis(args):
    """Match Polymarket tennis moneylines to tennis-data (closing odds only) and fetch hourly windows; the analysis
    is descriptive (venue bias against the closing consensus), never a trading test."""
    out = Path(args.out)
    td = load_tennis(out)
    by_day = collections.defaultdict(list)
    for i, r in enumerate(td):
        by_day[r['date']].append(i)
    uni = PH.read_gz(HIST / 'raw' / 'universe.json.gz')
    pm = [m for m in uni if m.get('cat') == 'sports' and m.get('sportsMarketType') == 'moneyline'
          and 'Tennis' in (m.get('tags') or []) and m.get('gameStartTime') and len(m.get('outcomes') or []) == 2]
    del uni
    matches, stats = [], collections.Counter()
    for m in pm:
        ko = PH.parse_ts(m['gameStartTime'])
        day = dt.datetime.fromtimestamp(ko, UTC).date()
        a, b = m['outcomes']
        cands = []
        for dd in (-1, 0, 1):
            for i in by_day.get(day + dt.timedelta(days=dd), []):
                r = td[i]
                if pm_player_match(a, r['winner']) and pm_player_match(b, r['loser']):
                    cands.append((i, 0))      # outcome 0 is the winner
                elif pm_player_match(a, r['loser']) and pm_player_match(b, r['winner']):
                    cands.append((i, 1))      # outcome 1 is the winner
        stats['pm_markets'] += 1
        if len(cands) != 1:
            stats['unmatched' if not cands else 'ambiguous'] += 1
            continue
        i, w = cands[0]
        r = td[i]
        pay0 = PH.binary_payout(m)
        agrees = None if pay0 is None else (pay0 == (1.0 if w == 0 else 0.0))
        matches.append({'id': m['id'], 'token': m['clobTokenIds'][0], 'ko': ko, 'q': m.get('question'), 'tour': r['tour'],
                        'winner_outcome': w, 'odds_src': r['odds_src'], 'odds_wl': r['odds_wl'],
                        'comment': r['comment'], 'payout0': pay0, 'agrees': agrees, 'volume': m.get('volumeNum')})
        stats['matched'] += 1
        stats['agrees_%s' % agrees] += 1
    PH.write_gz(out / 'raw' / 'tennis_matches.json.gz', matches)
    todo = [x for x in matches if not series_path(out, x['id']).exists() and not PH.price_path(HIST, x['id'], 'f').exists()]
    http = PH.Http(interval=args.interval)

    def one(x):
        s, err = PH.fetch_prices(http, x['token'], coarse=False, start=x['ko'] - 30 * HOUR, end=x['ko'] + HOUR,
                                 fidelity=60)
        if s is not None:
            PH.write_gz(series_path(out, x['id']), s)
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(one, todo))
    PH.update_manifest(out, 'tennis', {'generated': PH.utc(), 'tennis_data_rows': len(td), 'stats': dict(stats),
                                       'fetched_series': len(todo), 'http': http.stats(),
                                       'source': TD + ' (closing odds) + ' + PH.CLOB + '/prices-history'})
    print(json.dumps({'tennis_data_rows': len(td), **stats, 'fetched': len(todo), **http.stats()}))
    return 0


def tennis_bias(out, h=1):
    """Polymarket midpoint at ko - h against the Shin-de-vigged closing consensus (look-ahead: description only)."""
    p = Path(out) / 'raw' / 'tennis_matches.json.gz'
    if not p.exists():
        return None
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    acc_pm, acc_fair = [], []
    for x in PH.read_gz(p):
        if x['agrees'] is not True or not x['odds_wl'] or (x['comment'] or '').lower().startswith('w'):
            continue
        s = load_window(out, x['id'])
        mid = mid_at(s, x['ko'] - h * HOUR) if s else None
        if mid is None or not (MID_MIN <= mid <= MID_MAX):
            continue
        fw, fl = devig_shin(x['odds_wl'])
        f0 = fw if x['winner_outcome'] == 0 else fl
        y0 = 1.0 if x['winner_outcome'] == 0 else 0.0
        for p_, f_, y_ in ((mid, f0, y0), (1.0 - mid, 1.0 - f0, 1.0 - y0)):
            if f_ < 0.5:
                continue   # describe from the favourite's side only (each match once)
            fb = '%.1f' % min(0.9, int(f_ * 10) / 10.0)
            for key in ('all:fav_side', 'fairband:' + fb, 'tour:' + x['tour'], 'src:' + str(x['odds_src'])):
                by[key][x['id']].append(p_ - f_)
            acc_pm.append((p_, y_))
            acc_fair.append((f_, y_))
    res = {k: cluster_ci(list(v.values())) for k, v in by.items()}
    res['accuracy'] = {'n': len(acc_pm), 'brier_pm': brier(acc_pm), 'brier_fair': brier(acc_fair),
                       'logloss_pm': logloss(acc_pm), 'logloss_fair': logloss(acc_fair)}
    # selection check: the favourite's result minus its closing probability, matched markets vs every tennis-data
    # match since the first matched day (the $10k-volume filter could favour upsets, which draw in-play volume)
    ms = PH.read_gz(p)
    first = min(dt.datetime.fromtimestamp(x['ko'], UTC).date() for x in ms)

    def fav_dev(odds):
        fw, fl = devig_shin(odds)
        return (1.0 - fw) if fw >= 0.5 else (0.0 - fl)   # favourite won -> 1 - p_fav; lost -> 0 - p_fav
    allv = [fav_dev(r['odds_wl']) for r in load_tennis(out)
            if r['date'] >= first and r['odds_wl'] and not (r['comment'] or '').lower().startswith('w')]
    mv = [fav_dev(x['odds_wl']) for x in ms
          if x['agrees'] is True and x['odds_wl'] and not (x['comment'] or '').lower().startswith('w')]
    res['selection_check_fav_result_minus_fair'] = {
        'all_tennis_data': {'n': len(allv), 'mean': sum(allv) / len(allv) if allv else None},
        'matched_polymarket': {'n': len(mv), 'mean': sum(mv) / len(mv) if mv else None}}
    return res


def side_prints(rows, yes_token, side):
    """data-api taker trades -> [(ts, price of our side, usd, our side bought?)]. A trade in the other token is the
    mirror: selling the complement is buying ours at 1 - price."""
    out = []
    for x in rows:
        ts = int(x.get('timestamp') or 0)
        px = float(x.get('price') or 0)
        sz = float(x.get('size') or 0)
        ours = (x.get('asset') == yes_token) == (side == 0)
        p_ours = px if ours else 1.0 - px
        bought = (x.get('side') == 'BUY') == ours
        out.append((ts, p_ours, p_ours * sz, bought))
    return out


def cmd_trades(args):
    """What takers actually paid around sampled entries of the taker choice, the volume there, and (for a maker
    choice) whether real prints went through the resting limit when the midpoint proxy says it filled."""
    out = Path(args.out)
    tc = PH.read_gz(out / 'raw' / 'trades_chosen.json.gz')
    matches = {m['event_id']: m for m in load_matches(out)}
    rng = random.Random(7)
    taker_pool = list(tc['taker_trades'])
    rng.shuffle(taker_pool)
    taker_pool = [('taker', t) for t in taker_pool[:args.n]]
    maker_pool = []
    if tc['chosen'].startswith('maker'):
        mp = list(tc['trades'])
        rng.shuffle(mp)
        maker_pool = [('maker', t) for t in mp[:args.n]]
    http = PH.Http(interval=args.interval)

    def one(x):
        kind, t = x
        m = matches[t['event_id']]
        v = m['members'][t['role']]
        t_dec = m['ko'] - t['h'] * HOUR
        end = (t_dec + 3600) if kind == 'taker' else m['ko']
        q = {'market': v['conditionId'], 'limit': 1000, 'takerOnly': 'true', 'start': int(t_dec - 3600),
             'end': int(end)}
        d = http.request(PH.DATA + '/trades?' + urllib.parse.urlencode(q))
        if not isinstance(d, list):
            return {'kind': kind, 'event_id': t['event_id'], 'error': str(d)[:120]}
        pr = side_prints(d, v['token'], t['side'])
        buys30 = [p for ts, p, usd, bought in pr if bought and abs(ts - t_dec) <= 1800]
        rec = {'kind': kind, 'event_id': t['event_id'], 'role': t['role'], 'side': t['side'], 'mid': t['mid'],
               'n_raw': len(d), 'capped': len(d) >= 1000,
               'taker_buy_usd_2h': sum(usd for ts, p, usd, bought in pr if bought and abs(ts - t_dec) <= 3600),
               'n_buys_30m': len(buys30), 'buy_median': statistics.median(buys30) if buys30 else None}
        if kind == 'taker':
            rec['ask_model'] = t['ask']
        else:
            lim = t['limit']
            after = [(p, usd) for ts, p, usd, bought in pr if t_dec < ts <= m['ko'] and not bought]
            rec.update({'limit': lim, 'proxy_filled': t.get('filled'),
                        'print_through': any(p < lim - 1e-9 for p, _ in after),
                        'usd_sold_through': sum(usd for p, usd in after if p < lim - 1e-9)})
        return rec

    rows = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(one, taker_pool + maker_pool):
            if r:
                rows.append(r)
    ok = [r for r in rows if 'error' not in r and r['kind'] == 'taker']
    dif = [r['buy_median'] - r['mid'] for r in ok if r.get('buy_median') is not None]
    vs_model = [r['buy_median'] - r['ask_model'] for r in ok if r.get('buy_median') is not None]
    usd = sorted(r['taker_buy_usd_2h'] for r in ok)
    q = lambda a, p: a[int(p * (len(a) - 1))] if a else None  # noqa: E731
    summ = {'taker_variant': tc['taker_chosen'], 'chosen': tc['chosen'], 'sampled_taker': len(taker_pool),
            'ok': len(ok), 'errors': sum(1 for r in rows if 'error' in r), 'capped_at_1000': sum(1 for r in ok if r['capped']),
            'with_buys_30m': len(dif), 'no_taker_buy_30m': sum(1 for r in ok if r.get('buy_median') is None),
            'buy_minus_mid_median': statistics.median(dif) if dif else None,
            'buy_minus_mid_p75': q(sorted(dif), 0.75),
            'buy_minus_model_ask_median': statistics.median(vs_model) if vs_model else None,
            'taker_buy_usd_2h_median': statistics.median(usd) if usd else None,
            'taker_buy_usd_2h_p25': q(usd, 0.25), 'taker_buy_usd_2h_p75': q(usd, 0.75)}
    mk = [r for r in rows if 'error' not in r and r['kind'] == 'maker']
    if mk:
        summ['maker'] = {'sampled': len(mk), 'proxy_filled': sum(1 for r in mk if r['proxy_filled']),
                         'print_through': sum(1 for r in mk if r['print_through']),
                         'proxy_filled_and_print_through': sum(1 for r in mk if r['proxy_filled'] and r['print_through']),
                         'proxy_filled_no_print': sum(1 for r in mk if r['proxy_filled'] and not r['print_through']),
                         'usd_sold_through_median_when_filled': statistics.median(
                             [r['usd_sold_through'] for r in mk if r['proxy_filled']] or [0.0])}
    PH.write_json(out / 'raw' / 'trades_check.json', {'summary': summ, 'rows': rows, 'http': http.stats()})
    res = json.loads((out / 'analysis.json').read_text())
    res['trades_check'] = summ
    PH.write_json(out / 'analysis.json', res)
    PH.update_manifest(out, 'trades_check', {'generated': PH.utc(), 'source': PH.DATA + '/trades (takerOnly; taker: '
                                             'entry +-1h; maker: entry-1h to kick-off)',
                                             'sampled': len(taker_pool) + len(maker_pool), 'http': http.stats()})
    print(json.dumps(summ, indent=1))
    return 0


def prints_path(out, mid):
    return Path(out) / 'raw' / 'prints' / str(mid)[-2:] / ('%s.json.gz' % mid)


def yes_prints(rows, yes_token):
    """data-api taker trades of one member -> [(ts, YES price, size, +1 taker bought YES | -1 taker sold YES)].
    A trade in the NO token is the mirror: buying NO at q sells YES at 1 - q (it matches YES bids by minting)."""
    out = []
    for x in rows:
        try:
            ts, px, sz = int(x.get('timestamp') or 0), float(x.get('price') or 0), float(x.get('size') or 0)
        except (TypeError, ValueError):
            continue
        buy = x.get('side') == 'BUY'
        if x.get('asset') == yes_token:
            out.append((ts, px, sz, 1 if buy else -1))
        else:
            out.append((ts, 1.0 - px, sz, -1 if buy else 1))
    out.sort()
    return out


def print_fill(prints, side, limit, t0, t1):
    """The protocol's resting-limit rule: a buy of YES (side 0) at `limit` fills if a taker later sold YES strictly
    below it; a buy of NO (side 1) at `limit` fills if a taker later bought YES strictly above 1 - limit (sold NO
    below the limit). Returns (filled, USD traded through the limit)."""
    usd, hit = 0.0, False
    for ts, p, sz, d in prints:
        if not (t0 < ts <= t1):
            continue
        if side == 0 and d < 0 and p < limit - 1e-9:
            hit = True
            usd += limit * sz
        elif side == 1 and d > 0 and (1.0 - p) < limit - 1e-9:
            hit = True
            usd += limit * sz
    return hit, usd


def cmd_prints(args):
    """Taker trades of every main-league member from 25 hours before kick-off to kick-off (pages of 1,000)."""
    out = Path(args.out)
    todo = []
    for m in load_matches(out):
        if m['extra'] or abs(m['ko_diff_h']) > KO_TOL_H or len(m['members']) < 3:
            continue
        for v in m['members'].values():
            if not prints_path(out, v['id']).exists():
                todo.append((v['id'], v['conditionId'], v['token'], m['ko']))
    http = PH.Http(interval=args.interval)
    t0 = time.time()
    st = collections.Counter()

    def one(x):
        mid, cond, tok, ko = x
        rows = []
        for page in range(5):
            q = {'market': cond, 'limit': 1000, 'offset': page * 1000, 'takerOnly': 'true',
                 'start': int(ko - 25 * HOUR), 'end': int(ko)}
            d = http.request(PH.DATA + '/trades?' + urllib.parse.urlencode(q))
            if not isinstance(d, list):
                st['errors'] += 1
                return
            rows.extend(d)
            if len(d) < 1000:
                break
        else:
            st['capped_5000'] += 1
        PH.write_gz(prints_path(out, mid), yes_prints(rows, tok))
        st['written'] += 1
        if st['written'] % 1000 == 0:
            print(json.dumps({'written': st['written'], 'todo': len(todo), 'elapsed_s': round(time.time() - t0),
                              **http.stats()}), flush=True)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(one, todo))
    PH.update_manifest(out, 'prints_%d' % int(t0), {
        'fetched_at': PH.utc(t0), 'finished_at': PH.utc(), 'source': PH.DATA + '/trades (takerOnly, conditionId, '
        '[kick-off - 25h, kick-off], pages of 1,000 up to 5)', 'members': len(todo), **dict(st), 'http': http.stats()})
    print(json.dumps({'todo': len(todo), **dict(st), **http.stats()}))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('odds', 'match', 'complete', 'prices', 'live', 'analyze', 'trades', 'render', 'tennis', 'prints'):
        p = sub.add_parser(name)
        p.add_argument('--out', default=str(ROOT / 'research' / '2026-10-14' / 'pm_sports_sharp'))
        p.add_argument('--interval', type=float, default=0.25)
        p.add_argument('--workers', type=int, default=4)
        p.add_argument('--hours', type=float, default=96.0)
        p.add_argument('--extra', action='store_true')
        p.add_argument('--n', type=int, default=300)
    a = ap.parse_args()
    fn = {'odds': cmd_odds, 'match': cmd_match, 'prices': cmd_prices, 'live': cmd_live, 'analyze': cmd_analyze,
          'trades': cmd_trades, 'render': cmd_render, 'tennis': cmd_tennis, 'complete': cmd_complete,
          'prints': cmd_prints}[a.cmd]
    return fn(a)


def _pct(x, d=1):
    return '-' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def _f(x, d=3):
    return '-' if x is None else ('%.' + str(d) + 'f') % x


def _usd(x):
    return '-' if x is None else '${:,.0f}'.format(x)


def _sel_rows(sel, variants):
    ch = sel['chosen']
    return ['| variants | %d |' % sel['n_variants'],
            '| chosen in sample | `%s` |' % ch,
            '| in sample: trades, mean per trade, Sharpe (daily) | %s, %s, %s |' % (
                variants[ch]['in'].get('n'), _pct(variants[ch]['in'].get('mean_ret'), 2), _f(sel['in_sample'].get('sharpe'), 2)),
            '| out of sample: trades, mean per trade, Sharpe (daily) | %s, %s, %s |' % (
                variants[ch]['oos'].get('n'), _pct(variants[ch]['oos'].get('mean_ret'), 2),
                _f(sel['out_of_sample'].get('sharpe'), 2)),
            '| out of sample: HAC t, rank | %s, %s of %d |' % (_f(sel['oos_t'], 2), sel['oos_rank'], sel['n_variants']),
            '| deflated Sharpe of the in-sample choice | %s |' % _f(sel.get('deflated_sharpe_in_sample'), 3),
            '| BH survivors, positive one-sided (full sample) | %d %s |' % (
                len(sel['bh_survivors_positive']), ', '.join('`%s`' % x for x in sel['bh_survivors_positive'][:5])),
            '| BH survivors, two-sided (full sample) | %s |' % ', '.join('`%s`' % x for x in sel['bh_survivors_full_sample'][:6])]


def _bias_table(L, title, bset):
    if not bset:
        return
    L += ['### %s' % title, '', '| group | members | mean (PM - consensus) | 95% interval |', '|---|---:|---:|---:|']
    for g in sorted(k for k in bset if k not in ('accuracy', 'selection_check_fav_result_minus_fair')):
        v = bset[g]
        if v:
            L.append('| %s | %d | %+.4f | %+.4f to %+.4f |' % (g, v['n'], v['mean'], v['lo'], v['hi']))
    acc = bset.get('accuracy') or {}
    L += ['', 'Against results: Brier Polymarket %s vs consensus %s; log-loss %s vs %s (n %s)' % (
        _f(acc.get('brier_pm'), 4), _f(acc.get('brier_fair'), 4), _f(acc.get('logloss_pm'), 4),
        _f(acc.get('logloss_fair'), 4), acc.get('n')), '']


def cmd_render(args):
    out = Path(args.out)
    r = json.loads((out / 'analysis.json').read_text())
    man = json.loads((out / 'manifest.json').read_text())
    L = ['# pm_sports_sharp: Polymarket pre-game soccer against the de-vigged bookmaker consensus (2026-10-14)', '',
         'Every number is a key of `analysis.json` (paths in backticks). Returns are per $1 staked: a taker pays the '
         'live half-spread and the 0.05 x p x (1 - p) fee; a resting buy earns its limit and pays nothing.', '']
    m = r['match']
    st = m['stats']
    comp = man.get('complete', {}).get('stats', {})
    L += ['## Matching and event completion (`match`, `coverage_main`, manifest `complete`)', '',
          '| item | value |', '|---|---:|',
          '| Polymarket soccer match events in the stored universe | %d |' % m['pm_soccer_events'],
          '| in a division football-data covers | %d |' % st['in_scope'],
          '| matched: main divisions (pre-closing + closing odds) / extra leagues (closing only) | %d / %d |' % (
              st['matched_main'], st['matched_extra']),
          '| match rate in scope | %s |' % _pct(st['matched'] / st['in_scope']),
          '| Polymarket resolution vs the football-data result: agree / disagree / no result | %s / %s / %s |' % (
              m['result_agrees'].get('True', 0), m['result_agrees'].get('False', 0), m['result_agrees'].get('None', 0)),
          '| events with 3 / 2 / 1 members in the $10k universe (all leagues) | %s / %s / %s |' % (
              comp.get('members_before_3'), comp.get('members_before_2'), comp.get('members_before_1')),
          '| events with all 3 members after rebuilding from gamma | %s |' % comp.get('members_after_3'),
          '| main-league events / members with hourly series | %d / %d |' % (r['coverage_main']['events'],
                                                                        r['coverage_main']['members_with_series']),
          '| pre-closing source: Pinnacle / market average | %d / %d |' % (
              r['coverage_main'].get('pre_src_pinnacle', 0), r['coverage_main'].get('pre_src_average', 0)),
          '| split (median matched kick-off) | %s (%d days, %s to %s) |' % (r['split']['date'], r['split']['days'],
                                                                         r['split']['first'], r['split']['last']), '']
    us = r.get('universe_selection') or {}
    if us:
        L += ['### What the $10k-volume universe does to outcome rates (`universe_selection`), 2h before kick-off', '',
              '| members | n | YES rate | mean midpoint | YES rate - midpoint (95% interval) |', '|---|---:|---:|---:|---:|']
        for k in ('universe_member_complete_event', 'universe_member_incomplete_event', 'universe_members_all',
                  'added_from_gamma', 'after_fix_all'):
            v = us.get(k)
            if v:
                c = v['rate_minus_mid']
                L.append('| %s | %d | %s | %s | %+.4f (%+.4f to %+.4f) |' % (k, v['members'], _pct(v['yes_rate']),
                                                                           _pct(v['mean_mid']), c['mean'], c['lo'], c['hi']))
        ev = us.get('event_level_calibration') or {}
        if ev:
            L += ['', 'Event level, result minus Shin closing probability: matched events %s; every football-data '
                  'fixture of the same divisions and dates %s' % (
                      ', '.join('%s %+.4f (n %d)' % (k, v['result_minus_fair'], v['n']) for k, v in ev['matched'].items()),
                      ', '.join('%s %+.4f (n %d)' % (k, v['result_minus_fair'], v['n']) for k, v in ev['all_fd'].items())), '']
    ub = r.get('uncorrected_universe_backtest')
    if ub:
        L += ['Backtest on the uncorrected universe (`uncorrected_universe_backtest`, disclosure only): taker grid mean '
              '%s per trade (corrected %s); maker-proxy grid mean %s (corrected %s); `taker|h2|thr0.00|all|all` %s on %s '
              'trades (corrected %s on %s); chosen `%s`, oos t %s, BH positive survivors %d' % (
                  _pct(ub['grid_mean_ret_taker']['uncorrected'], 2), _pct(ub['grid_mean_ret_taker']['corrected'], 2),
                  _pct(ub['grid_mean_ret_maker_proxy']['uncorrected'], 2), _pct(ub['grid_mean_ret_maker_proxy']['corrected'], 2),
                  _pct(ub['taker_h2_thr0_all_all']['uncorrected'].get('mean_ret'), 2),
                  ub['taker_h2_thr0_all_all']['uncorrected'].get('n'),
                  _pct(ub['taker_h2_thr0_all_all']['corrected'].get('mean_ret'), 2),
                  ub['taker_h2_thr0_all_all']['corrected'].get('n'), ub['chosen'], _f(ub['oos_t'], 2),
                  len(ub['bh_survivors_positive'])), '']
    L += ['## Costs from the live books (`half_spread_model`, `depth_model_usd_best_ask`)', '',
          '| YES-mid band | top-5 half-spread | other main half-spread | top-5 $ at best ask | other main $ at best ask |',
          '|---|---:|---:|---:|---:|']
    for b in range(10):
        b_ = str(b)
        L.append('| %.1f-%.1f | %s | %s | %s | %s |' % (b / 10, (b + 1) / 10, _f(r['half_spread_model']['top5'][b_]),
                                                        _f(r['half_spread_model']['rest'][b_]),
                                                        _usd(r['depth_model_usd_best_ask']['top5'][b_]),
                                                        _usd(r['depth_model_usd_best_ask']['rest'][b_])))
    L += ['', 'Eligibility (`eligibility`): ' + ', '.join('%s %s' % (k, v) for k, v in sorted(r['eligibility'].items())), '']
    L += ['## A. Pre-registered run (`selection`, `go_rule`; maker fills on the hourly-midpoint proxy)', '',
          '| item | value |', '|---|---:|'] + _sel_rows(r['selection'], r['variants'])
    L += ['', 'Go rule: ' + ', '.join('%s=%s' % (k, (_f(v, 2) if isinstance(v, float) else v)) for k, v in r['go_rule'].items()), '']
    pf = r.get('protocol_fills')
    if pf:
        L += ['## B. Maker fills on real prints (`protocol_fills`)', '',
              'The proxy filled 9 of 300 sampled maker signals; real taker prints went through the limit in 104 '
              '(`trades_check.maker`). Run B re-prices the 108 maker variants on every print and re-selects.', '',
              '| item | value |', '|---|---:|'] + _sel_rows(pf['selection'], pf['variants'])
        L += ['', 'Go rule: ' + ', '.join('%s=%s' % (k, (_f(v, 2) if isinstance(v, float) else v)) for k, v in pf['go_rule'].items()),
              '', 'Per execution: ' + '; '.join('%s chose `%s` (in-sample positive %s, oos t %s, rank %s)' % (
                  e, v['chosen'], v['in_sample_positive'], _f(v['oos_t'], 2), v['oos_rank']) for e, v in pf['selection_by_execution'].items()),
              '', 'Closing-line value of the maker choice\'s filled orders: %s (positive %s of %s)' % (
                  _pct(pf['clv_maker_choice_filled']['mean'], 2), _pct(pf['clv_maker_choice_filled']['share_positive']),
                  pf['clv_maker_choice_filled']['n']), '']
        for n, v in pf['late_entry'].items():
            L.append('- late entry +1h `%s`: %s -> %s per signal (share kept %s); out of sample %s -> %s (share %s)' % (
                n, _pct(v['all']['orig_mean'], 2), _pct(v['all']['late_mean'], 2), _f(v['all']['share_kept'], 2),
                _pct(v['oos']['orig_mean'], 2), _pct(v['oos']['late_mean'], 2), _f(v['oos']['share_kept'], 2)))
        c = pf['capacity']
        L += ['- capacity `%s`: P&L %s a year out of sample, peak capital %s, excess over SSR %s' % (
            c['chosen'], _usd(c['pnl_usd_per_year_oos']), _usd(c['peak_capital_usd']), _usd(c['excess_usd_per_year_oos'])), '']
    L += ['## Every-outcome variants, all tiers (A taker; A and B maker)', '',
          '| variant | trades | mean EV at entry | mean realised | hit | oos mean | maker fill A | B: mean realised | B: fill |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for ex in EXECS:
        for h in HORIZONS_H:
            for t in THRESHOLDS:
                n = '%s|h%d|thr%.2f|all|all' % (ex, h, t)
                v = r['variants'][n]
                vb = (pf or {}).get('variants', {}).get(n, {}) if ex == 'maker' else {}
                L.append('| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    n, v['all'].get('n', 0), _pct(v['all'].get('mean_ev'), 2), _pct(v['all'].get('mean_ret'), 2),
                    _pct(v['all'].get('hit')), _pct(v['oos'].get('mean_ret'), 2), _pct(v.get('maker_fill_rate')),
                    _pct((vb.get('all') or {}).get('mean_ret'), 2), _pct(vb.get('fill_rate'))))
    se = r['sensitivity']
    L += ['', '## Sensitivities and look-ahead (`sensitivity`, `late_entry`, `clv_chosen`)', '']
    for k in ('pre_shin', 'pre_shin_oos', 'close_shin_lookahead', 'close_shin_lookahead_oos', 'pre_mult', 'bfe_shin', 'hs_p75'):
        v = se[k]
        L.append('- A-chosen `%s` under `%s`: %s trades, mean %s, hit %s' % (se['chosen'], k, v.get('n', 0),
                                                                          _pct(v.get('mean_ret'), 2), _pct(v.get('hit'))))
    L.append('- mean over variants with >= 30 trades: pre-closing %s, closing odds (look-ahead) %s, Betfair Exchange '
             'pre-closing %s' % (_pct(se['grid_mean_ret']['pre'], 2), _pct(se['grid_mean_ret']['close_lookahead'], 2),
                                 _pct(se['grid_mean_ret']['bfe'], 2)))
    L.append('- best variant with >= 100 trades: pre-closing %s; closing (look-ahead) %s' % (
        se['best_mean_ret_n100']['pre'], se['best_mean_ret_n100']['close_lookahead']))
    for n, v in r['late_entry'].items():
        L.append('- late entry +1h (A) `%s`: %s -> %s (share kept %s); oos share %s' % (
            n, _pct(v['all']['orig_mean'], 2), _pct(v['all']['late_mean'], 2), _f(v['all']['share_kept'], 2),
            _f(v['oos']['share_kept'], 2)))
    L.append('- closing-line value of the A-chosen filled trades: %s (positive %s of %s)' % (
        _pct(r['clv_chosen']['mean'], 2), _pct(r['clv_chosen']['share_positive']), r['clv_chosen']['n']))
    if r.get('capacity'):
        c = r['capacity']
        L.append('- capacity (A-chosen, touch depth): P&L %s a year out of sample; excess over SSR %s' % (
            _usd(c['pnl_usd_per_year_oos']), _usd(c['excess_usd_per_year_oos'])))
    L += ['', '## Exploratory, post-hoc: the same moment (`exploratory_same_time`)', '',
          'Polymarket\'s kick-off midpoint against the closing consensus taken at the same moment, taker, held to '
          'the result. Added after run A was seen; never eligible for a go.', '',
          '| variant | trades | mean EV | mean realised | s.e. | hit |', '|---|---:|---:|---:|---:|---:|']
    for n, v in r['exploratory_same_time'].items():
        L.append('| `%s` | %s | %s | %s | %s | %s |' % (n, v.get('n', 0), _pct(v.get('mean_ev'), 2), _pct(v.get('mean_ret'), 2),
                                                       _pct(v.get('se'), 2), _pct(v.get('hit'))))
    if r.get('trades_check'):
        t = r['trades_check']
        L += ['', '## Fills around entries (`trades_check`)', '',
              '- taker `%s`: %s sampled; %s with a taker buy of the side within 30 min; median buy - mid %s (modelled '
              'half-spread at the median: buy - modelled ask %s); taker-buy USD within 1h: median %s, p25 %s, p75 %s' % (
                  t['taker_variant'], t['sampled_taker'], t['with_buys_30m'], _f(t['buy_minus_mid_median'], 4),
                  _f(t['buy_minus_model_ask_median'], 4), _usd(t['taker_buy_usd_2h_median']), _usd(t['taker_buy_usd_2h_p25']),
                  _usd(t['taker_buy_usd_2h_p75']))]
        if t.get('maker'):
            mk = t['maker']
            L.append('- maker `%s`: %s sampled; hourly-mid proxy filled %s; real prints through the limit %s; proxy '
                     'fills without a print %s' % (t['chosen'], mk['sampled'], mk['proxy_filled'], mk['print_through'],
                                                   mk['proxy_filled_no_print']))
    L += ['', '## Polymarket minus the de-vigged consensus (`bias`), event-clustered 95% intervals', '']
    for key, title in (('main_close_h0', 'Same moment: Polymarket at kick-off vs closing consensus (main divisions)'),
                       ('main_pre_h2', '2h before kick-off vs pre-closing consensus'),
                       ('main_pre_h6', '6h before vs pre-closing'), ('main_pre_h24', '24h before vs pre-closing'),
                       ('main_close_h2', '2h before vs closing (look-ahead of 2h)'),
                       ('extra_close_h2', 'Extra leagues: 2h before vs closing (look-ahead of 2h)'),
                       ('tennis_close_h1', 'Tennis (ATP/WTA tour): 1h before the listed start vs closing, favourite side')):
        _bias_table(L, title, r['bias'].get(key))
    tb = r['bias'].get('tennis_close_h1') or {}
    if tb.get('selection_check_fav_result_minus_fair'):
        sc = tb['selection_check_fav_result_minus_fair']
        L += ['Tennis selection check (favourite result minus closing probability): matched %s (n %s) vs every '
              'tennis-data match %s (n %s)' % (_f(sc['matched_polymarket']['mean'], 4), sc['matched_polymarket']['n'],
                                               _f(sc['all_tennis_data']['mean'], 4), sc['all_tennis_data']['n']), '']
    pb = r['bias']['popular_h2']
    L += ['### Popular teams (top 20 by Polymarket win-market volume), 2h before kick-off, team win members', '',
          '- popular %s; other teams %s' % (
              ('%+.4f (%+.4f to %+.4f, n %d)' % (pb['popular']['mean'], pb['popular']['lo'], pb['popular']['hi'],
                                                  pb['popular']['n'])) if pb['popular'] else '-',
              ('%+.4f (%+.4f to %+.4f, n %d)' % (pb['other']['mean'], pb['other']['lo'], pb['other']['hi'],
                                                  pb['other']['n'])) if pb['other'] else '-'),
          '- teams: ' + ', '.join(pb['popular_teams']), '']
    L += ['Variants tried (`n_variants_tried`): %s' % r['n_variants_tried'], '']
    # a pipe inside a code span still splits a Markdown table cell: escape it on table rows
    L = [re.sub(r'`[^`]*`', lambda mm: mm.group(0).replace('|', '\\|'), x) if x.startswith('|') else x for x in L]
    (out / 'tables.md').write_text('\n'.join(L))
    go_a = bool(r['go_rule'].get('go'))
    go_b = bool((pf or {}).get('go_rule', {}).get('go'))
    entries = []
    if go_a or go_b:
        entries.append({'id': 'pm-sports-sharp', 'status': 'proposed', 'go': True, 'note': 'see analysis.json'})
    (out / 'book_entries.json').write_text(json.dumps(entries, indent=1))
    print('tables.md and book_entries.json written (%d entries); go A %s, go B %s' % (len(entries), go_a, go_b))
    return 0


if __name__ == '__main__':
    sys.exit(main())
