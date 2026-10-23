#!/usr/bin/env python3
"""Structural mispricing in Polymarket's resolved history, priced as executable and corrected for multiple testing.

Why. The 2026-10-09 studies closed four Polymarket ideas (favourites by category, neg-risk sums, the resolution lag,
cross-venue arbitrage). What they did not look at is *structure*: the question template a market is written in
("Will X happen by <date>?", "Will Trump say 'Y'?", "Exact score: A 2-1 B?"), the sibling markets it shares an
event with (date and strike ladders, which must be monotone), and the path its price took. Each is a place where a
counterparty with a non-price motive (a fan of the drama, a buyer of lottery tickets, an impatient seller) could be
paying a rent. This script looks in all three places with one cost model and one protocol:

  * **templates** (hypotheses a and b): a regex classifier on the question, the event title and the group item title,
    checked against a hand-labelled sample; calibration and executable returns by template x horizon x price band x
    side, chosen before 2026-01-01 and tested once after it, one-sided Benjamini-Hochberg across everything tried;
  * **ladders** (c): sibling markets ordered by a date or a strike, where P(by d1) <= P(by d2) and P(above k1) >=
    P(above k2) must hold; historical violations at midpoints (an upper bound), then live executable violations from
    one atomic POST /books per ladder, fee-aware;
  * **dynamics** (d): moves over the past k hours on the hourly series, entered at the next hour's price, exited at
    +h hours or at resolution.

Costs. A prices-history point is a midpoint. A taker pays the live half-spread for its template (or category) and
price band, measured here across all bands from a fresh snapshot (the 2026-10-09 table covers only favourites), plus
the taker fee shares x feeRate x p x (1 - p) (`polymarket_history.fee_rate`). Exits before resolution pay the
half-spread and the fee again.

    uv run python scripts/pm_structure_scan.py inventory --out research/2026-10-14/pm_structure_scan
    uv run python scripts/pm_structure_scan.py collect   --out ... --what extra|ladders
    uv run python scripts/pm_structure_scan.py live      --out ...            (repeat for persistence)
    uv run python scripts/pm_structure_scan.py analyze   --out ...
    uv run python scripts/pm_structure_scan.py render    --out ...
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import datetime as dt
import json
import math
import re
import statistics
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
import polymarket_history as P  # noqa: E402
from polymarket_history import (Http, categorize, fee_rate, parse_ts, write_gz, read_gz, update_manifest,  # noqa: E402
                                price_path, fetch_prices, as_of)

HIST = ROOT / 'research' / '2026-10-09' / 'polymarket_history'
DAY, HOUR = P.DAY, P.HOUR
SSR = 0.038
CUTOFF = '2026-01-01T00:00:00+00:00'
START = '2024-01-01T00:00:00+00:00'

# ------------------------------------------------------------------------------------------------- templates

MONTHS = (r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|'
          r'oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?')
DATE_AFTER = (r'(?:the\s+)?(?:end\s+of\b|eo[ymq]\b|' + MONTHS + r'\b|20\d\d\b|q[1-4]\b|'
              r'(?:mon|tues|wednes|thurs|fri|satur|sun)day\b|tomorrow|tonight|midnight|'
              r'(?:the\s+)?(?:election|midterms|inauguration|deadline|summit|primary|debate|convention)\b|'
              r'\.\.\.|_{2,}|\?|\d{1,2}/\d{1,2})')
RE_BY_DATE = re.compile(r'\b(?:by|before|until)\s+' + DATE_AFTER, re.I)
RE_IN_PERIOD = re.compile(r'\b(?:in|during)\s+(?:' + MONTHS + r'\b|20\d\d\b|q[1-4]\b|(?:the\s+)?(?:first|next)\s+\d+\s+days)'
                          r'[^?]*\?\s*$', re.I)
RE_ON_DATE = re.compile(r'\bon\s+(?:' + MONTHS + r'\s*\d{1,2}|\d{4}-\d\d-\d\d|(?:mon|tues|wednes|thurs|fri|satur|sun)day)',
                        re.I)
RE_NUM = r'\$?\d[\d,]*(?:\.\d+)?\s*(?:[kmb]\b|million|billion|trillion|%)?'

SPORTS_PROP = re.compile(
    r'both teams to score|to score first|score first|leading at halftime|halftime|\b\d\+\s*goals|most sixes|'
    r'top batter|run scored|first inning|\bnrfi\b|\b1h\b|1st half|first half|2nd half|second half|corners|'
    r'\bcards\b|total kills|first blood|points o/u|rebounds|assists|touchdowns?|yards|strikeouts|home runs?|'
    r'anytime|completed match|method of victory|go the distance|by ko|by decision|\bround\s+\d|first set|'
    r'set winner|\bto advance\b|player of the match|man of the match|first goal|clean sheet|penalt|'
    r'double fault|tie ?break|sacks|receptions|passing yards|rushing yards|3-pointers|odd/even|'
    r'race to \d|longest|fastest lap|podium|pole position|safety car|top \d+ finish|winning margin',
    re.I)
FUTURES = re.compile(
    r'\bwin\b[^?]*\b(?:the\s+)?(?:\d{4}(?:[-–]\d{2,4})?\s+)?(?:[\w\'’\.\- ]+\s)?(?:championship|champions?\b|'
    r'tournament|cup\b|open\b|league\b|title|finals?\b|series\b|mvp|trophy|medal|award|oscar|grammy|emmy|'
    r'golden globe|eurovision|ballon|prize|nobel|person of the year|best (?:picture|actor|actress|director|'
    r'album|song|new artist|record|supporting)|grand prix|gp\b|masters|derby|bowl\b|stanley|world series|'
    r'conference|division|east\b|west\b|pennant|nomination\b|rookie|cy young|heisman|slam)|'
    r'\bmake the playoffs|\brelegated|\bqualify for|\badvance to the|\breach the (?:final|semi)|'
    r'\bwin (?:best|album of|song of|record of)|\bnominated for',
    re.I)
ELECTION_WORDS = re.compile(
    r'\b(?:election|elections|primary|primaries|presidency|presidential|senate|house|governor|gubernatorial|'
    r'mayor|mayoral|seat|nomination|nominee|caucus|runoff|run-off|district|parliament|chancellor|prime minister|'
    r'referendum|electoral|ballot|congress|congressional|assembly|majority|party|democrat|republican|tory|'
    r'labour|leader of|president of|next president|pm\b|vice president|vp\b|speaker)\b', re.I)
ECON = re.compile(
    r'\b(?:fed (?:rate|rates|interest|decision|decreases|increases|cuts?|hikes?|holds?|pauses?|funds|meeting)|fomc|'
    r'interest rates?|bps|basis points|cpi|inflation|gdp|unemployment|jobs report|nonfarm|'
    r'non-farm|payrolls|pce|rate cuts?|rate hikes?|recession|treasury yields?|10-year|ecb|boe|bank of (?:england|'
    r'japan|canada)|boj|rba|snb|jobless claims|retail sales|ism\b|pmi\b|consumer sentiment|core cpi|deficit|'
    r'debt ceiling|tariff rate)\b', re.I)
RANKING = re.compile(
    r'best [\w\- ]{0,20}ai model|top [\w\- ]{0,20}ai model|best [\w\- ]{0,12}model|#1|number one|no\. ?1\b|largest company|most (?:streamed|downloaded|popular|'
    r'viewed|watched|liked|followed)|billboard|top (?:free )?app|app store|highest[- ]grossing|\branks?\b|'
    r'\branked\b|biggest opening|top spot|top of the|chart|leaderboard|lmarena|arena\b|elo\b|benchmark|'
    r'top grossing|spotify|netflix top|imdb|rotten tomatoes|metacritic|score of at least|time person|'
    r'most (?:goals|assists|points)', re.I)
COUNT_BUCKET = re.compile(
    r'\bexactly\s+\d|\bbetween\s+' + RE_NUM + r'\s*(?:and|-|–|to)\s*' + RE_NUM + r'|how many|\bnumber of\b|'
    r'\b\d+\s*[-–]\s*\d+\s+(?:times|people|cases|launches|seats|votes|deaths|earthquakes|days|games|goals|points|'
    r'medals|wins|bills|executive orders|signed)|\bviews\b|box office|opening weekend|\bstreams?\b|'
    r'\bless than \d+\b|\bfewer than \d+|\bmore than \d+|\b\d+\s*or (?:more|fewer|less)\b|\b\d+\+\s|\b\d+\+\??$|'
    r'#\s*of\b', re.I)
RELEASE = re.compile(
    r'\b(?:release|released|releases|launch|launches|launched|debut|debuts|unveil|unveils|unveiled|'
    r'ship|ships|shipped|available|go live|goes live|listed|list on|listing|ipo|airdrop|token generation|tge|'
    r'open source|open-source|premiere|premieres|come out|comes out|start(?:s)? selling|roll out|rolls out|'
    r'rollout)\b', re.I)
NOT_RELEASE = re.compile(r'missile|nuclear|rocket|strike|invasion|offensive|ballistic|ceasefire|blockade|war\b|'
                         r'troops|sanction|hostage|attack|military|epstein|files|documents|tax returns|prisoner|'
                         r'detainee|report\b', re.I)
DEPARTURE = re.compile(r'\bout as\b|\bout by\b|\bout\?|\bresigns?\b|\bfired\b|\bremoved\b|\bimpeach|\bindicted\b|'
                       r'\barrested\b|\bjail\b|\bstep(?:s)? down\b|\bleave(?:s)? office\b|\bousted\b|\bdies\b|'
                       r'\bcharged\b|\bconvicted\b|\bsentenced\b|\bdeported\b|\bpardon', re.I)
ELECTION_STRONG = re.compile(
    r'\b(?:election|elections|by-election|primary|primaries|presidential|presidency|nominee|nomination|caucus|'
    r'runoff|run-off|mayoral|gubernatorial|parliament|parliamentary|seats?|prime minister|chancellor|governor|'
    r'senate|house of|congress|congressional|party|electoral|referendum|ballot|mayor|vice president|'
    r'next president|next pope|pope|speaker)\b', re.I)
PRICE_ASSET = re.compile(
    r'\b(?:bitcoin|btc|ethereum|eth|solana|sol|xrp|doge|dogecoin|bnb|hype|cardano|ada|avax|link|ltc|sui|pepe|'
    r'shib|ton|trx|pump|price|s&p|spx|spy|nasdaq|ndx|qqq|dow|gold|silver|oil|wti|brent|crude|natural gas|'
    r'tesla|tsla|nvidia|nvda|apple|aapl|amazon|amzn|google|googl|meta|microsoft|msft|coinbase|coin|mstr|'
    r'microstrategy|stock|shares|market cap|fdv|token|yield|vix|dxy|euro|eur|usd|yen|jpy|gbp|index|close|'
    r'closes|trading)\b|\(\s*[A-Z]{1,6}\s*\)', re.I)


def classify(q, et='', g='', cat=''):
    """Template of one market from its question, event title and group item title; the first rule that matches
    wins. The order puts the machine-made and sports families first because their wording is the most regular."""
    q = q or ''
    et = et or ''
    g = g or ''
    ql = q.lower()
    qe = (q + ' || ' + et).lower()
    if 'up or down' in ql:
        return 'updown'
    if 'exact score' in qe:
        return 'exact_score'
    sportsish = cat == 'sports' or re.search(r'\bvs\.?\s', q + ' ' + et) is not None
    if sportsish and re.search(r'end in a (?:draw|tie)|\bdraw\?|\bresult: draw', ql):
        return 'sports_draw'
    if sportsish and re.search(r'\bmap\s*\d+\b|\bgame\s*\d+\s*(?:winner|handicap)|\bset\s*\d+\s*winner|'
                               r'map handicap|game handicap', ql):
        return 'esports_map'
    if sportsish and re.search(r'\bo/u\b|over/under|\btotals?\b[^?]*\d+\.5|\b(?:over|under)\s+\d+\.5\b', ql):
        return 'sports_total'
    if sportsish and re.search(r'^spread|\bspread\b|handicap|\(\s*[-+]\d+(?:\.\d+)?\s*\)|[-+]\d+\.5\b|'
                               r'\bby\s+(?:\d+(?:\.\d+)?\s+or more|more than \d+(?:\.\d+)?)\s+(?:points|goals|runs)', ql):
        return 'sports_spread'
    if sportsish and SPORTS_PROP.search(ql):
        return 'sports_prop'
    if cat == 'sports':
        if FUTURES.search(ql) or RANKING.search(ql):
            return 'futures_winner'
        if re.search(r'\bvs\.?\b|\bv\.?\s|\bwin on\b|\bbeat\b|\bwin\??$|\bwins?\b', ql + ' ' + et.lower()):
            return 'sports_match'
    if re.search(r'(?:highest|lowest|high|low|max(?:imum)?|min(?:imum)?) temperature|temperature in|°\s*[cf]\b', ql):
        return 'weather_temp'
    if re.search(r'\b(?:post|tweet|truth)s?\b[^?]*\b(?:\d[\d,]*\s*(?:[-–]\s*\d[\d,]*|\+)|\d[\d,]*\s*or\s*(?:more|fewer|less)|'
                 r'(?:less|fewer|more) than \d)[^?]*\b(?:tweets?|posts?|times|truth)', ql) or \
            re.search(r'#\s*of\s*(?:tweets|posts|truth)|how many (?:tweets|posts|times will .* (?:tweet|post))', qe):
        return 'tweet_count'
    if re.search(r'\b(?:say|says|said|mention|mentions|mentioned|utter|utters)\b', qe) and \
            not re.search(r'polls? say|survey', ql):
        return 'mention'
    if re.search(r'approval rating|approval\s+(?:be|on|at|of)|disapproval|net approval|approve of', ql):
        return 'approval'
    if re.search(r'\bfdv\b|fully diluted|market cap[^?]*after launch|one day after launch|after (?:its )?launch|'
                 r'public sale|committed to|\btge\b', qe) and re.search(r'\d', q):
        return 'fdv_launch'
    has_num = re.search(r'\$\s?\d|\d[\d,]*(?:\.\d+)?\s*[kmb]\b|\d{2,}', q) is not None
    priced = PRICE_ASSET.search(q) is not None or re.search(r'\$\s?\d', q) is not None
    if has_num and priced and re.search(
            r'\bbetween\s+\$?\d|\bclose at\s+\$?\d[\d,\.]*\s*[-–]|\bat\s+\$\d[\d,\.]*\s*[-–]\s*\$?\d|'
            r'\bin the range\b', ql) and (PRICE_ASSET.search(q) or re.search(r'between\s+\$', ql)):
        return 'price_range'
    if has_num and PRICE_ASSET.search(q) and re.search(
            r'\b(?:reach|reaches|hit|hits|dip|dips|fall|falls|drop|drops|crash|crashes|touch|touches|sink|sinks|'
            r'surge|surges|rise|rises|climb|climbs)\b[^?]*\d|[↑↓]', ql + ' ' + g):
        return 'price_hit'
    if has_num and PRICE_ASSET.search(q) and re.search(
            r'\b(?:above|below|greater than|less than|over|under|higher than|lower than|at or above|at least|'
            r'close above|closes above|close below|closes below|finish above|finish below)\b|[<>≥≤]', ql):
        return 'price_above'
    dated = RE_BY_DATE.search(ql) or RE_BY_DATE.search(et.lower()) or RE_IN_PERIOD.search(ql)
    if dated and DEPARTURE.search(ql):
        return 'drama_by_date'
    if ECON.search(qe):
        return 'econ_release'
    if re.search(r'\bearnings\b|\brevenue\b|\beps\b|\bguidance\b|quarterly results', ql):
        return 'earnings'
    electoral = ELECTION_STRONG.search(qe) is not None or cat == 'elections'
    if re.search(r'margin of victory|popular vote|vote share|\bby\s+\d+(?:\.\d+)?\+?\s*(?:points|pts|%|percent)|'
                 r'\bturnout\b|percentage of (?:the )?vote|electoral votes|\bwin\b[^?]*\bby\s+[\d\.]+%|'
                 r'%\s*of the vote|\bvotes?\b[^?]*\b(?:more|less|between)', qe) and electoral:
        return 'election_margin'
    if electoral and re.search(r'\bwin\b|\bwins\b|\bwinner\b|next (?:prime minister|president|chancellor|pope|leader|'
                               r'speaker|mayor|governor)|which party|control (?:the )?(?:house|senate)|\bbe elected\b|'
                               r'\belected\b|\bnominee\b|\bnominated\b|\bnomination\b|\bmajority\b|\bseats?\b', ql):
        return 'election_winner'
    if dated and RELEASE.search(ql) and not NOT_RELEASE.search(ql):
        return 'release_by'
    if RE_ON_DATE.search(ql) and RELEASE.search(ql) and not NOT_RELEASE.search(ql):
        return 'release_by'
    if RANKING.search(qe):
        return 'ranking'
    if COUNT_BUCKET.search(ql) or re.search(r'how many|# of|number of', et.lower()):
        return 'count_bucket'
    if dated:
        return 'drama_by_date'
    if FUTURES.search(ql):
        return 'futures_winner'
    if RE_ON_DATE.search(ql):
        return 'drama_on_date'
    if sportsish:
        return 'sports_match'
    return 'other'


TEMPLATES = ['updown', 'exact_score', 'sports_draw', 'esports_map', 'sports_spread', 'sports_prop', 'sports_total',
             'weather_temp', 'tweet_count', 'mention', 'approval', 'fdv_launch', 'price_range', 'price_hit',
             'price_above', 'econ_release', 'earnings', 'election_margin', 'election_winner', 'release_by',
             'ranking', 'count_bucket', 'drama_by_date', 'futures_winner', 'drama_on_date', 'sports_match', 'other']

# The hypotheses are pre-registered on these template groups. (a) is drama_by_date; (b) is every other template the
# brief names (mentions, tweet counts, exact scores, approval buckets, release/launch-by) and the rest of the list
# as "other templates". updown is classified but not traded (a coin flip with a 7% fee coefficient).
HYPOTHESIS = {'drama_by_date': 'a'}
for _t in TEMPLATES:
    HYPOTHESIS.setdefault(_t, 'b')
TRADED_TEMPLATES = [t for t in TEMPLATES if t not in ('updown',)]

# ------------------------------------------------------------------------------------------------- ladders

MONTH_NUM = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct',
                                          'nov', 'dec'], 1)}
RE_DATE_TOKEN = re.compile(r'\b(' + MONTHS + r')\s*(\d{1,2})(?:st|nd|rd|th)?(?:,?\s*(20\d\d))?\b', re.I)
RE_MONTH_ONLY = re.compile(r'\b(?:end of\s+)?(' + MONTHS + r')(?:\s+(20\d\d))?\b', re.I)


def nearest_year(mon, day, ref):
    """Year for a year-less 'Month Day' label: the one that puts the date nearest the market's scheduled end.
    `ref` is that end as a timestamp, or a bare year (then used as is). End dates are stored in UTC, so a 'December
    31' deadline at 23:59 New York time ends on 1 January of the next year; taking the end's year would misorder
    it after the following year's rungs (found on the 2026-10-14 pilot snapshot)."""
    if ref is None:
        return None
    if ref < 10000:
        return int(ref)
    y0 = dt.datetime.fromtimestamp(ref, dt.timezone.utc).year
    best = None
    for y in (y0 - 1, y0, y0 + 1):
        try:
            d = dt.datetime(y, mon, min(day, 28 if mon == 2 else 30 if mon in (4, 6, 9, 11) else 31),
                            tzinfo=dt.timezone.utc).timestamp()
        except ValueError:
            continue
        if best is None or abs(d - ref) < best[0]:
            best = (abs(d - ref), y)
    return best[1] if best else None


def first_year_after(mon, day, start):
    """Year for a year-less deadline: the first one that puts it on or after the market's opening (a deadline
    cannot precede its market). Gamma's endDate is unreliable for this: 'Iran x Israel/US conflict ends by December
    31?' carries endDate 2026-06-30, and the nearest-year rule placed it in 2025, before its March siblings."""
    y0 = dt.datetime.fromtimestamp(start, dt.timezone.utc).year
    for y in (y0, y0 + 1, y0 + 2):
        dd = min(day, 28 if mon == 2 else 30 if mon in (4, 6, 9, 11) else 31)
        if dt.datetime(y, mon, dd, 23, 59, tzinfo=dt.timezone.utc).timestamp() >= start - 7 * DAY:
            return y
    return None


def parse_rung_date(text, ref, start=None):
    """A deadline date in a rung label or question ('June 30', 'March 31, 2026', 'end of June'): a sortable number
    (year*10000 + month*100 + day); month-only labels take day 31. A missing year is the first that puts the date
    after the market's opening `start`; without a start, the one nearest `ref` (the scheduled end, or a year)."""
    if not text:
        return None
    m = RE_DATE_TOKEN.search(text)
    if m:
        mon = MONTH_NUM.get(m.group(1).lower()[:3])
        day = int(m.group(2))
        if mon and 1 <= day <= 31:
            year = int(m.group(3)) if m.group(3) else (first_year_after(mon, day, start) if start
                                                         else nearest_year(mon, day, ref))
            return year * 10000 + mon * 100 + day if year else None
    m = RE_MONTH_ONLY.search(text)
    if m:
        mon = MONTH_NUM.get(m.group(1).lower()[:3])
        year = int(m.group(2)) if m.group(2) else (first_year_after(mon, 28, start) if start
                                                     else nearest_year(mon, 28, ref))
        if mon and year:
            return year * 10000 + mon * 100 + 31
    m = re.search(r'\b(20\d\d)\b', text)
    if m and re.search(r'\b(?:by|before|in|end of)\s+(?:the end of\s+)?20\d\d\b', text, re.I):
        return int(m.group(1)) * 10000 + 1231
    return None


def parse_number(s):
    """'$72,000' -> 72000, '1.5B' -> 1.5e9, '25+' -> 25, '−1.5' -> -1.5. None if no number."""
    if s is None:
        return None
    s = str(s).replace('−', '-').replace('–', '-')
    m = re.search(r'(-?)\$?\s*(\d[\d,]*(?:\.\d+)?)\s*([kKmMbBtT](?:illion|n)?\b)?', s)
    if not m:
        return None
    v = float(m.group(2).replace(',', ''))
    suf = (m.group(3) or '').lower()[:1]
    v *= {'k': 1e3, 'm': 1e6, 'b': 1e9, 't': 1e12}.get(suf, 1.0)
    return -v if m.group(1) else v


UP_WORDS = re.compile(r'\b(?:above|over|greater than|more than|higher than|at least|or more|or higher|reach|reaches|'
                      r'hit \(high\)|high\b|surge|rise|climb|exceed|exceeds)\b|↑|\d\+|≥|>', re.I)
# 'top N' rankings rise with N (top 5 is inside top 50), so 'top' sits with the rising words
DOWN_WORDS = re.compile(r'\b(?:below|under|less than|fewer than|lower than|or less|or fewer|or lower|dip|dips|fall|'
                        r'falls|drop|drops|crash|sink|hit \(low\)|low\b|top(?=\s*\d))\b|↓|≤|<', re.I)


def spread_side(label, outcomes):
    """Index of the outcome a spread label names ('Spread: Kansas (-3.5)', '1H Spread: Kansas State (-0.5)'): an exact
    match on the name after any 'xxx:' prefix, else the only outcome contained in it. 'Kansas' inside 'Kansas State'
    once put both teams' spreads on one side (2026-10-14 pilot)."""
    name = re.sub(r'^.*:\s*', '', label).strip().lower()
    outs = [str(o).strip().lower() for o in outcomes]
    exact = [i for i, o in enumerate(outs) if o == name]
    if len(exact) == 1:
        return exact[0]
    if exact:
        return None
    cont = [i for i, o in enumerate(outs) if o and (o in name or name in o)]
    if len(cont) == 1:
        return cont[0]
    if len(cont) == 2:
        longest = max(cont, key=lambda i: len(outs[i]))
        if outs[longest] in name:          # 'kansas state' named: the longer outcome is the one meant
            return longest
    return None


def comparison_sign(text, num_span):
    """+1/-1 from the comparison word nearest the rung number and closer to it than to any other number: 'above
    $70,000' or '70+' says falling (-1), 'dip to $60,000' rising (+1). None when the nearest comparison belongs to
    another number ('0 earthquakes of 6.5 or above' is a count bucket, not a ladder in the count)."""
    nums = [mm.span() for mm in re.finditer(r'\d[\d,]*(?:\.\d+)?', text)]
    best = None
    for rx, sg in ((UP_WORDS, -1), (DOWN_WORDS, +1)):
        for mm in rx.finditer(text):
            a, b = mm.span()
            d = num_span[0] - b if b <= num_span[0] else (a - num_span[1] if a >= num_span[1] else 0)
            if d > 30:
                continue
            closest_other = min([(a - y if y <= a else x - b) for x, y in nums if (x, y) != num_span] or [99])
            if closest_other < d:
                continue
            if best is None or d < best[0]:
                best = (d, sg)
    return best[1] if best else None


def ladder_rung(m):
    """(family, key, rung, sign) for a market that sits on an ordered ladder with its siblings, or None.

    sign = +1 when P(YES) must rise with the rung (deadlines: P(by d) grows with d; 'below k' grows with k; a dip to
    k grows with k), -1 when it must fall (above k, reach k, over a total, k+ mentions, a team covering -k).
    key groups siblings: the event id plus the question with its rung replaced, so 'Bitcoin above X on Apr 25' and
    'Ethereum above X on Apr 25' in one event never mix, nor do a game's total and its first-half total."""
    q = (m.get('question') or '').strip()
    g = (m.get('groupItemTitle') or '').strip()
    et = m.get('event_title') or ''
    ev = m.get('event_id') or m.get('id')
    outs = m.get('outcomes') or []
    ql = q.lower()
    if 'up or down' in ql or re.search(r'\bbetween\b|\bexactly\b|\d\s*[-–]\s*\d', ql + ' ' + g.lower()):
        return None
    ref_year = parse_ts(m.get('endDate')) or 2026
    # sports totals: Over is outcome 0
    mt = re.search(r'\bo/u\s*(\d+(?:\.\d+)?)', ql)
    if mt and outs and str(outs[0]).lower().startswith('over'):
        stem = re.sub(r'\bo/u\s*\d+(?:\.\d+)?', 'O/U #', ql)
        return 'total', '%s|%s' % (ev, stem), float(mt.group(1)), -1, 0
    # sports spreads: 'Spread: Pacers (-2.5)'; the named team must be one of the two outcomes
    ms = re.search(r'^(?:spread:\s*)?(.+?)\s*\(\s*([-+−]\d+(?:\.\d+)?)\s*\)\s*\??$', q, re.I)
    if ms and len(outs) == 2 and 'vs' not in ms.group(1).lower():
        team = ms.group(1).strip().lower()
        side = spread_side(team, outs)
        line = parse_number(ms.group(2))
        if side is not None and line is not None and line < 0:
            return 'spread', '%s|%s' % (ev, team), -line, -1, side
    if len(outs) != 2 or str(outs[0]).lower() != 'yes':
        return None
    # deadlines: the event title says 'by...?' / 'by ___' / 'before ...', or the question says 'by <date>'
    if RE_BY_DATE.search(ql) or re.search(r'\bby\s*(?:\.\.\.|_{2,}|\?)|before\s*(?:\.\.\.|_{2,})', et.lower()):
        # a bare count ('0 earthquakes ... by Feb 15') makes the question a bucket, not monotone in the deadline
        qd = RE_DATE_TOKEN.sub(' ', ql)
        qd = re.sub(r'\b20\d\d\b', ' ', qd)
        for mm in re.finditer(r'(?<![\w.\-])\d[\d,]*(?:\.\d+)?(?![\w.%\-])', qd):
            after = qd[mm.end():mm.end() + 12]
            before = qd[max(0, mm.start() - 12):mm.start()]
            if not (re.match(r'\s*(?:\+|or more|or higher|or above|or greater)', after) or
                    re.search(r'(?:at least|more than|over|above|exceed|exceeds)\s*\$?$', before)):
                return None
        st0 = P.start_ts(m)
        cl0 = parse_ts(m.get('closedTime'))
        if st0 and cl0 and st0 > cl0:
            st0 = None                    # 2021-23 markets carry a 2023 re-listing date after their own close
        tail = q[q.lower().rfind(' by ') if ' by ' in ql else 0:]
        mq = RE_DATE_TOKEN.search(tail)
        if mq and mq.group(3):            # an explicit year in the question wins over a year-less label
            d = parse_rung_date(tail, ref_year, st0)
        else:
            d = parse_rung_date(g, ref_year, st0) or parse_rung_date(tail, ref_year, st0)
        if d:
            stem = RE_DATE_TOKEN.sub('<D>', ql)
            stem = RE_MONTH_ONLY.sub('<D>', stem)
            stem = re.sub(r'\b20\d\d\b', '', stem)
            stem = re.sub(r'\s+', ' ', stem).strip()
            return 'date', '%s|%s' % (ev, stem), d, +1, 0
    # strikes / thresholds: the rung is the one number in the group item title (or the question)
    src = g if (g and re.search(r'\d', g)) else q
    if re.search(r'[A-Za-z]\d', src.split(':')[-1]) and not re.search(r'\d\s*[kKmMbB]\b', src):
        return None                       # 'Q1', 'GPT5': a label, not a strike
    k = parse_number(re.sub(r'\b(?:on|by|in)\s+' + MONTHS + r'\s*\d{1,2}(?:,?\s*20\d\d)?', ' ', src, flags=re.I)
                     .replace('20' + '24', ' ').replace('20' + '25', ' ').replace('20' + '26', ' ')
                     if src is q else src)
    if k is None:
        return None
    if src is g and k < 1000:
        # '>126' beside 'Bitcoin above $126K': the label dropped the suffix the question carries
        mk = re.search(r'\$?' + re.escape(('%g' % k)) + r'\s*([kmb])\b', ql)
        if mk:
            k *= {'k': 1e3, 'm': 1e6, 'b': 1e9}[mk.group(1)]
    ctx = (g + ' ' + ql)
    sign = None
    if g and re.search(r'\d', g):
        mg = re.search(r'\d[\d,]*(?:\.\d+)?', g)
        sign = comparison_sign(g, mg.span())
    if sign is None:
        qd = re.sub(r'\b(?:on|by|in|before)\s+' + MONTHS + r'\s*\d{1,2}(?:st|nd|rd|th)?(?:,?\s*20\d\d)?', lambda x: ' ' * len(x.group(0)),
                    ql, flags=re.I)
        qd = re.sub(r'\b20\d\d\b', '    ', qd)
        target = None
        for mm in re.finditer(r'\d[\d,]*(?:\.\d+)?', qd):
            if parse_number(mm.group(0)) == k or parse_number(mm.group(0) + 'k') == k:
                target = mm.span()
                break
        if target is None:
            return None
        sign = comparison_sign(qd, target)
    if sign is None:
        return None
    up = sign < 0
    stem = re.sub(r'\$?\d[\d,]*(?:\.\d+)?\s*[kmbt]?\b\+?', '#', ql)
    stem = re.sub(r'\s+', ' ', stem).strip()
    if re.search(r'(?:say|said|mention)', ql + et.lower()):
        fam = 'count'
    elif re.search(r'\b(?:reach|hit|dip|fall|drop|crash|touch|sink)\b|↑|↓', ctx, re.I):
        fam = 'touch'
        # older 'What price will X hit' events say 'reach' for strikes below the spot too, and a touch below the
        # spot is a dip: without an arrow or a directional verb the rung's side of the spot is unknown
        if not re.search(r'[↑↓]|\((?:high|low)\)|\b(?:dip|dips|fall|falls|drop|drops|crash|sink|surge|rise|climb)\b',
                         ctx, re.I):
            return None
    else:
        fam = 'strike'
    return fam, '%s|%s' % (ev, stem), k, sign, 0


# ------------------------------------------------------------------------------------------------- inventory

def eligible(m):
    return P.eligible_binary(m)


def cmd_inventory(args):
    """Classify every market in the 2026-10-09 universe, count templates and ladders, and pick what to fetch."""
    out = Path(args.out)
    uni = P.load_universe(HIST)
    smp = json.loads((HIST / 'sample.json').read_text())
    in_sample = {r['id'] for r in smp['markets']}
    rows = []
    for m in uni:
        if not eligible(m):
            continue
        t = classify(m.get('question'), m.get('event_title'), m.get('groupItemTitle'), m.get('cat'))
        lr = ladder_rung(m)
        rows.append({'id': m['id'], 'tpl': t, 'cat': m['cat'], 'vb': P.vol_bucket(m.get('volumeNum')),
                     'vol': m.get('volumeNum') or 0.0, 'close': (m.get('closedTime') or '')[:10],
                     'in_sample': m['id'] in in_sample,
                     'ladder': list(lr) if lr else None})
    write_gz(out / 'raw' / 'inventory.json.gz', rows)
    cnt = collections.Counter(r['tpl'] for r in rows)
    smp_cnt = collections.Counter(r['tpl'] for r in rows if r['in_sample'])
    vol = collections.Counter()
    for r in rows:
        vol[r['tpl']] += r['vol']
    lad = collections.defaultdict(set)
    lad_m = collections.Counter()
    for r in rows:
        if r['ladder']:
            lad[r['ladder'][0]].add(r['ladder'][1])
            lad_m[r['ladder'][0]] += 1
    summary = {'eligible': len(rows),
               'templates': {t: {'markets': cnt[t], 'in_sample': smp_cnt[t], 'volume_musd': vol[t] / 1e6}
                             for t in TEMPLATES},
               'ladder_markets': dict(lad_m), 'ladder_groups': {k: len(v) for k, v in lad.items()}}
    print(json.dumps(summary, indent=1))
    P.write_json(out / 'raw' / 'inventory_summary.json', summary)
    return 0


# ------------------------------------------------------------------------------------------------- collect

# Templates the 2026-10-09 sample under-covers (it was stratified by category and volume, not template): extra
# markets are drawn by an independent hash so the union stays a probability sample. Targets are totals of extra
# markets per template, fixed before any return was computed.
SUPPLEMENT = {'exact_score': 450, 'sports_draw': 450, 'sports_prop': 400, 'approval': 300, 'earnings': 400,
              'fdv_launch': 350, 'mention': 300, 'drama_on_date': 200, 'esports_map': 150, 'sports_spread': 200,
              'release_by': 200, 'econ_release': 150, 'election_margin': 100}
LADDER_TARGET = {'date': 260, 'strike': 140, 'touch': 140, 'count': 75, 'total': 160, 'spread': 110, 'date_x': 220}
NEST_TOL = DAY   # a cross-event pair counts only if the later deadline's market opened no later than this after


def stem_of(key):
    return key.split('|', 1)[1] if '|' in key else key


def cross_event_groups(inv, uni):
    """Date rungs grouped by question stem across events ('series of events'), keeping stems that span at least two
    events and two deadlines: {stem: [inventory rows]}."""
    g = collections.defaultdict(list)
    for r in inv:
        if r['ladder'] and r['ladder'][0] == 'date':
            g[stem_of(r['ladder'][1])].append(r)
    return {k: v for k, v in g.items() if len({uni[r['id']].get('event_id') for r in v}) >= 2 and
            len({r['ladder'][2] for r in v}) >= 2}


def nested(start_hi, start_lo):
    """A later deadline must count everything the earlier one counts: its market must have opened no later than
    the earlier market (plus a day of listing slack). Windows of re-listed monthly markets often start at their own
    listing, and those pairs are not ordered."""
    return start_hi is not None and start_lo is not None and start_hi <= start_lo + NEST_TOL


def series_path(out, mid, kind):
    """Our own fetch if we made one, else the 2026-10-09 sample's file (same layout, same token 0)."""
    p = price_path(out, mid, kind)
    if p.exists():
        return p
    q = price_path(HIST, mid, kind)
    return q if q.exists() else None


def load_series(out, mid, kind):
    p = series_path(out, mid, kind)
    if p is None:
        return None
    s = read_gz(p)
    s.sort()
    return s


def supplement_plan(inv):
    """{template: q_T}: the inclusion probability of the supplementary draw among markets not in the main sample."""
    plan = {}
    for t, n_extra in SUPPLEMENT.items():
        pool = [r for r in inv if r['tpl'] == t and not r['in_sample']]
        plan[t] = min(1.0, n_extra / len(pool)) if pool else 0.0
    return plan


def in_supplement(mid, tpl, plan):
    q = plan.get(tpl, 0.0)
    return q > 0 and P.stable_u('pm-structure-sup:' + str(mid)) < q


def fetch_market_series(http, out, m, kinds):
    tok = m['clobTokenIds'][0]
    err = None
    for kind in kinds:
        if series_path(out, m['id'], kind) is not None:
            continue
        if kind == 'c':
            s, e = fetch_prices(http, tok, coarse=True)
        else:
            a, b, fid = P.fine_window(m)
            s, e = fetch_prices(http, tok, coarse=False, start=a, end=b, fidelity=fid)
        if s is not None:
            write_gz(price_path(out, m['id'], kind), s)
        err = err or e
    return err


def ladder_selection(inv):
    """Ladder groups with at least two members, drawn per family by a hash of the key (volume-ordered within the
    hash draw so the selection is reproducible): {family: [key, ...]}."""
    g = collections.defaultdict(list)
    for r in inv:
        if r['ladder']:
            g[(r['ladder'][0], r['ladder'][1])].append(r)
    sel = {}
    for fam, n in LADDER_TARGET.items():
        if fam == 'date_x':
            continue
        keys = [k for k in g if k[0] == fam and len({x['ladder'][2] for x in g[k]}) >= 2]
        keys.sort(key=lambda k: P.stable_u('pm-structure-ladder:' + k[1]))
        sel[fam] = [k[1] for k in keys[:n]]
    return sel, g


def compact_event(e):
    """An event with every member market (gamma embeds all of them, including those under $10k of volume, which the
    stored universe drops). Members carry the event's tags when they have none of their own."""
    stub = {k: e.get(k) for k in ('id', 'slug', 'title', 'negRisk', 'negRiskAugmented')}
    etags = [t for t in (e.get('tags') or []) if isinstance(t, dict)]
    ms = []
    for m in e.get('markets') or []:
        mm = dict(m, events=[stub])
        if not mm.get('tags'):
            mm['tags'] = etags
        ms.append(P.compact_market(mm))
    return {'id': str(e.get('id')), 'title': e.get('title'), 'negRisk': e.get('negRisk'),
            'augmented': e.get('negRiskAugmented'), 'closed': e.get('closed'), 'markets': ms}


def fetch_events(http, ids, batch=40):
    """Full events by id, many per request (gamma accepts repeated id parameters)."""
    got, errs = {}, 0
    ids = list(ids)
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        q = urllib.parse.urlencode([('id', x) for x in chunk] + [('limit', batch)])
        d = http.request(P.GAMMA + '/events?' + q)
        if not isinstance(d, list):
            errs += 1
            continue
        for e in d:
            got[str(e.get('id'))] = compact_event(e)
    return got, errs


TRADABLE_USD = 1000.0      # members under this lifetime volume never had a book worth trading; outside the population
FIX_EVENTS = 500           # incomplete events completed with every tradable member (event-level draw)


def event_members(e):
    """Tradable binary members of a full event: two outcomes, a clean resolution, at least TRADABLE_USD traded."""
    return [x for x in e['markets'] if P.eligible_binary(x) and (x.get('volumeNum') or 0) >= TRADABLE_USD]


def event_design(out, uni, inv_by_id, events):
    """The corrected sampling design. The stored universe keeps markets with at least $10k of lifetime volume, and
    inside a multi-market event the members that cross it are disproportionately the winners. So:
      (A) union-sample markets whose event is complete (every tradable member is in the universe) or standalone
          keep their market weight 1/pi_m;
      (B) a hash draw of FIX_EVENTS incomplete events enters with every tradable member (fetched from gamma when
          under $10k), each weighted 1/(pi_event x q_fix), pi_event = 1 - prod(1 - pi_m) over the event's universe
          members;
      (C) other union-sample markets in incomplete events are dropped.
    Returns {market id: (row, weight, part)} and a summary."""
    w = sample_weights(out, inv_by_id)
    smp = json.loads((HIST / 'sample.json').read_text())
    pmain = {k: v['prob'] for k, v in smp['plan'].items()}
    plan = json.loads((Path(out) / 'raw' / 'supplement.json').read_text())['plan']

    def pi_m(mid):
        r = inv_by_id.get(mid)
        if r is None:
            return 0.0
        return 1.0 - (1.0 - pmain.get('%s|%s' % (r['cat'], r['vb']), 0.0)) * (1.0 - plan.get(r['tpl'], 0.0))

    complete, incomplete = {}, {}
    for mid in w:
        m = uni.get(mid)
        e = events.get(str(m.get('event_id'))) if m else None
        if e is None:
            complete[mid] = True          # no event record: treated as standalone
            continue
        missing = [x for x in event_members(e) if x['id'] not in uni]
        if missing:
            incomplete.setdefault(e['id'], []).append(mid)
        else:
            complete[mid] = True
    inc_ids = sorted(incomplete)
    q_fix = min(1.0, FIX_EVENTS / float(len(inc_ids))) if inc_ids else 0.0
    fix = [e for e in inc_ids if P.stable_u('pm-structure-fix:' + e) < q_fix]
    design = {}
    for mid in complete:
        design[mid] = (uni[mid], w[mid], 'A')
    for eid in fix:
        e = events[eid]
        univ_members = [x for x in e['markets'] if x['id'] in uni and P.eligible_binary(uni[x['id']])]
        prod = 1.0
        for x in univ_members:
            prod *= (1.0 - pi_m(x['id']))
        pe = (1.0 - prod) * q_fix
        if pe <= 0:
            continue
        for x in event_members(e):
            row = uni.get(x['id']) or x
            design[x['id']] = (row, 1.0 / pe, 'B')
    summ = {'union_markets': len(w), 'complete_or_standalone': len(complete),
            'incomplete_events': len(inc_ids), 'union_markets_in_incomplete_events': sum(len(v) for v in incomplete.values()),
            'q_fix': q_fix, 'fix_events': len(fix), 'design_markets': len(design),
            'design_A': sum(1 for v in design.values() if v[2] == 'A'),
            'design_B': sum(1 for v in design.values() if v[2] == 'B'),
            'design_B_not_in_universe': sum(1 for k, v in design.items() if v[2] == 'B' and k not in uni),
            'tradable_usd_floor': TRADABLE_USD}
    return design, summ, fix


def leg_fill_prices(trades, token, other):
    """From one market's taker trades: prices at which this token could be bought (taker buys of it, and taker
    sells of the complement at 1 - p) and sold (taker sells of it, taker buys of the complement at 1 - p)."""
    buy, sell = [], []
    for x in trades or []:
        a, sd, px = x.get('asset'), x.get('side'), P.fnum(x.get('price'))
        if px is None:
            continue
        if a == token:
            (buy if sd == 'BUY' else sell).append(px)
        elif a == other:
            (sell if sd == 'BUY' else buy).append(1.0 - px)
    return buy, sell


def cmd_ladder_fills(args):
    """Were historical ladder violations executable? For a sample of out-of-sample entries of the chosen ladder
    variant, read the taker trades of both legs within +-30 minutes (data-api) and ask whether someone bought the
    must-be-higher YES and sold the must-be-lower YES at prices that lock a profit after fees."""
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    tr = read_gz(out / 'raw' / 'trades.json.gz')['ladders']
    uni = {m['id']: m for m in P.load_universe(HIST)}
    cutoff_ts = parse_ts(CUTOFF)
    ch = a['ladders']['protocol'].get('chosen')
    fam = ch.split('|')[1] if ch else 'strike'
    pool = [t for t in tr if t['fam'] == fam and t['th'] == 0.0 and t['t'] >= cutoff_ts and
            t['pair'][0] in uni and t['pair'][1] in uni]
    pool.sort(key=lambda t: P.stable_u('pm-structure-fills:%s:%s' % (t['pair'], t['t'])))
    pool = pool[:args.n]
    http = Http(interval=args.interval)
    rows = []
    for t in pool:
        legs = []
        for mid in t['pair']:
            m = uni[mid]
            q = {'market': m['conditionId'], 'limit': 500, 'takerOnly': 'true',
                 'start': int(t['t'] - 1800), 'end': int(t['t'] + 1800)}
            d = http.request(P.DATA + '/trades?' + urllib.parse.urlencode(q))
            legs.append((m, d if isinstance(d, list) else None))
        (mh, dh), (ml, dl) = legs
        if dh is None or dl is None:
            continue
        # a spread rung can name outcome 1, so each leg's 'YES' is the token on the rung's side
        sh, sl_ = t.get('sides') or [0, 0]
        bh, _ = leg_fill_prices(dh, mh['clobTokenIds'][sh], mh['clobTokenIds'][1 - sh])
        _, sl = leg_fill_prices(dl, ml['clobTokenIds'][sl_], ml['clobTokenIds'][1 - sl_])
        rate_h, rate_l = fee_rate(mh['cat'], mh.get('tags')), fee_rate(ml['cat'], ml.get('tags'))
        best = None
        if bh and sl:
            ph, pl = min(bh), max(sl)
            cost = ph + P.fee_per_share(rate_h, ph) + (1.0 - pl) + P.fee_per_share(rate_l, 1.0 - pl)
            best = 1.0 - cost
        rows.append({'pair': t['pair'], 't': t['t'], 'v_mid': t['v_mid'], 'edge_at_mid': t['edge'],
                     'buys_hi': len(bh), 'sells_lo': len(sl), 'best_fill_edge': best,
                     'q_hi': mh['question'][:80], 'q_lo': ml['question'][:80]})
    both = [r for r in rows if r['best_fill_edge'] is not None]
    summ = {'family': fam, 'sampled': len(pool), 'read': len(rows), 'with_trades_on_both_legs': len(both),
            'fill_edge_positive': sum(1 for r in both if r['best_fill_edge'] > 0),
            'median_fill_edge': statistics.median([r['best_fill_edge'] for r in both]) if both else None,
            'median_mid_edge': statistics.median([r['edge_at_mid'] for r in rows]) if rows else None,
            'no_trade_on_a_leg': len(rows) - len(both),
            'note': 'best prices on each leg within +-30 min are not simultaneous: an upper bound on executability'}
    P.write_json(out / 'ladder_fills.json', {'generated': P.utc(), 'summary': summ, 'rows': rows,
                                             'http': http.stats(),
                                             'source': P.DATA + '/trades (takerOnly, +-30 min of entry)'})
    # the ladder go needs the history to have been executable, not just violated at midpoints: at least half of the
    # sampled entries must show trades on both legs that lock a profit after fees
    exe = (summ['fill_edge_positive'] / float(summ['read'])) if summ['read'] else 0.0
    for gg in a['go']:
        if gg['family'] == 'ladders':
            gg['checks']['historical_fills_executable'] = exe >= 0.5
            gg['historical_fill_share'] = exe
            gg['go'] = all(gg['checks'].values())
    a['ladder_fills'] = summ
    P.write_json(out / 'analysis.json', a)
    update_manifest(out, 'ladder_fills', {'generated': P.utc(), 'entries': len(rows), 'http': http.stats()})
    print(json.dumps(summ), flush=True)
    return 0


def cmd_collect(args):
    out = Path(args.out)
    inv = read_gz(out / 'raw' / 'inventory.json.gz')
    uni = {m['id']: m for m in P.load_universe(HIST)}
    http = Http(interval=args.interval)
    t0 = time.time()
    jobs = []
    if args.what == 'extra':
        plan = supplement_plan(inv)
        chosen = [r for r in inv if not r['in_sample'] and in_supplement(r['id'], r['tpl'], plan)]
        P.write_json(out / 'raw' / 'supplement.json', {'plan': plan, 'targets': SUPPLEMENT,
                                                       'markets': [r['id'] for r in chosen]})
        for r in chosen:
            m = uni[r['id']]
            life = (parse_ts(m['closedTime']) - (P.start_ts(m) or parse_ts(m['closedTime']))) / DAY
            jobs.append((m, ['f'] if life <= 14.0 else ['f', 'c']))
    elif args.what == 'events':
        # every event that holds a market of the union sample: its full member list decides whether the event is
        # complete in the $10k universe (the volume floor keeps winners more often than losers)
        w = sample_weights(out, {r['id']: r for r in inv})
        evs = sorted({str(uni[mid].get('event_id')) for mid in w if mid in uni and uni[mid].get('event_id')})
        print(json.dumps({'events': len(evs)}), flush=True)
        got, errs = fetch_events(http, evs)
        write_gz(out / 'raw' / 'events_full.json.gz', got)
        update_manifest(out, 'collect_events', {'fetched_at': P.utc(t0), 'finished_at': P.utc(), 'events': len(evs),
                                                'returned': len(got), 'batch_errors': errs, 'http': http.stats(),
                                                'source': P.GAMMA + '/events?id=..&id=.. (40 per request)'})
        print(json.dumps({'returned': len(got), 'batch_errors': errs, **http.stats()}), flush=True)
        return 0
    elif args.what == 'complete':
        events = read_gz(out / 'raw' / 'events_full.json.gz')
        design, summ, fix = event_design(out, uni, {r['id']: r for r in inv}, events)
        P.write_json(out / 'raw' / 'complete_selection.json', {'summary': summ, 'fix_events': fix})
        for mid, (row, wt, part) in design.items():
            if part == 'B' and series_path(out, mid, 'f') is None and series_path(out, mid, 'c') is None:
                st_ = P.start_ts(row)
                cl = parse_ts(row.get('closedTime'))
                if not (cl and row.get('clobTokenIds')):
                    continue
                life = (cl - (st_ or cl)) / DAY
                jobs.append((row, ['f'] if life <= 14.0 else ['f', 'c']))
        print(json.dumps(dict(summ, to_fetch=len(jobs))), flush=True)
    elif args.what == 'confirm':
        # fresh events for the pre-registered confirmation test (confirm_preregistration.json)
        w = sample_weights(out, {r['id']: r for r in inv})
        used = {str(uni[mid].get('event_id')) for mid in w if mid in uni}
        cut = parse_ts(CUTOFF)
        cand = sorted({str(uni[r['id']].get('event_id')) for r in inv
                       if r['tpl'] in ('price_above', 'price_range') and uni[r['id']].get('event_id') and
                       (parse_ts(uni[r['id']].get('closedTime')) or 0) >= cut} - used)
        cand.sort(key=lambda e: P.stable_u('pm-structure-confirm:' + e))
        chosen = cand[:args.max_events]
        evs, errs = fetch_events(http, chosen)
        write_gz(out / 'raw' / 'confirm_events.json.gz', evs)
        P.write_json(out / 'raw' / 'confirm_selection.json', {'candidates': len(cand), 'events': chosen,
                                                              'returned': len(evs), 'batch_errors': errs})
        for e in evs.values():
            for x in event_members(e):
                if series_path(out, x['id'], 'f') is None and x.get('clobTokenIds'):
                    jobs.append((x, ['f']))
        print(json.dumps({'candidate_events': len(cand), 'chosen': len(chosen), 'returned': len(evs)}), flush=True)
    elif args.what == 'ladders':
        sel, g = ladder_selection(inv)
        P.write_json(out / 'raw' / 'ladder_selection.json', {'targets': LADDER_TARGET, 'keys': sel})
        for fam, keys in sel.items():
            for k in keys:
                for r in g[(fam, k)]:
                    jobs.append((uni[r['id']], ['c'] if fam == 'date' else ['f']))
    else:
        gx = cross_event_groups(inv, uni)
        keys = sorted(gx, key=lambda k: P.stable_u('pm-structure-ladder-x:' + k))[:LADDER_TARGET['date_x']]
        P.write_json(out / 'raw' / 'ladder_selection_x.json', {'target': LADDER_TARGET['date_x'],
                                                               'stems_in_universe': len(gx), 'keys': keys})
        for k in keys:
            for r in gx[k]:
                jobs.append((uni[r['id']], ['c']))
    if args.shards > 1:
        jobs = [j for i, j in enumerate(jobs) if i % args.shards == args.shard]
    print(json.dumps({'what': args.what, 'markets': len(jobs), 'shard': args.shard}), flush=True)
    errs = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for e in ex.map(lambda j: fetch_market_series(http, out, j[0], j[1]), jobs):
            done += 1
            if e:
                errs.append(e)
            if done % 250 == 0:
                print(json.dumps({'done': done, 'of': len(jobs), 'errors': len(errs),
                                  'elapsed_s': round(time.time() - t0), **http.stats()}), flush=True)
    update_manifest(out, 'collect_' + args.what + ('_%d' % args.shard if args.shards > 1 else ''), {
        'fetched_at': P.utc(t0), 'finished_at': P.utc(), 'markets': len(jobs), 'errors': len(errs),
        'error_examples': errs[:5], 'http': http.stats(), 'seconds': round(time.time() - t0, 1),
        'source': P.CLOB + '/prices-history (token 0; coarse interval=max fidelity=720; fine last 14.5 days)'})
    print(json.dumps({'done': done, 'errors': len(errs), **http.stats()}), flush=True)
    return 0


# ------------------------------------------------------------------------------------------------- live

# Half-spreads are symmetric in the two outcomes (one book), so they are keyed on the distance band of the YES
# midpoint from the nearer edge: a YES at 0.07 and a NO at 0.93 cross the same spread.
EDGE_BANDS = [(0.0, 0.02), (0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 0.35), (0.35, 0.5001)]


def edge_band(p):
    e = min(p, 1.0 - p)
    for lo, hi in EDGE_BANDS:
        if lo <= e < hi:
            return '%.2f-%.2f' % (lo, min(hi, 0.5))
    return None


def mirror(book):
    """The NO token's book from the YES token's: NO asks are 1 - YES bids, NO bids are 1 - YES asks."""
    return {'asks': sorted((round(1.0 - p, 6), s) for p, s in book.get('bids') or []),
            'bids': sorted(((round(1.0 - p, 6), s) for p, s in book.get('asks') or []), reverse=True)}


def ladder_pairs(rungs):
    """Every ordered pair (hi, lo) of a ladder's members where P(hi) must be >= P(lo). `rungs` is a list of
    (rung, sign, member) with one sign; sign -1 means P falls with the rung (so the lower rung must be priced
    higher), +1 that it rises. Equal rungs are skipped (duplicated listings are not a ladder)."""
    out = []
    for i in range(len(rungs)):
        for j in range(len(rungs)):
            ri, si, mi = rungs[i]
            rj, sj, mj = rungs[j]
            if ri == rj or si != sj:
                continue
            # P(i) >= P(j) must hold when (sign -1 and ri < rj) or (sign +1 and ri > rj)
            if (si < 0 and ri < rj) or (si > 0 and ri > rj):
                out.append((mi, mj))
    return out


def violation_fill(book_hi, book_lo, rate_hi, rate_lo, max_sets=1e9):
    """Walk the two books for the monotonicity trade: buy YES of the member that must be priced higher (at its
    asks) and NO of the member that must be priced lower (at 1 - its bids). Every state pays at least 1 per set
    (both pay 1 in the states between the rungs), so the trade locks a profit while a set costs under 1 after fees.
    Returns sets, cost, profit, the first set's edge, and the min payout (1)."""
    a = [list(x) for x in sorted(book_hi.get('asks') or [])]
    b = [[round(1.0 - p, 6), s] for p, s in sorted(book_lo.get('bids') or [], reverse=True)]
    sets = cost = 0.0
    i = j = 0
    first = None
    while i < len(a) and j < len(b) and sets < max_sets:
        pa, pb = a[i][0], b[j][0]
        unit = pa + P.fee_per_share(rate_hi, pa) + pb + P.fee_per_share(rate_lo, pb)
        if first is None:
            first = 1.0 - unit
        if unit >= 1.0:
            break
        q = min(a[i][1], b[j][1], max_sets - sets)
        sets += q
        cost += q * unit
        a[i][1] -= q
        b[j][1] -= q
        if a[i][1] <= 1e-9:
            i += 1
        if b[j][1] <= 1e-9:
            j += 1
    return {'sets': sets, 'cost': cost, 'profit': sets - cost, 'first_edge': first}


def gamma_market_row(m):
    cm = P.compact_market(m)
    cm['tpl'] = classify(cm.get('question'), cm.get('event_title'), cm.get('groupItemTitle'), cm.get('cat'))
    lr = ladder_rung(cm)
    cm['ladder'] = list(lr) if lr else None
    cm['bestBid'] = P.fnum(m.get('bestBid'))
    cm['bestAsk'] = P.fnum(m.get('bestAsk'))
    return cm


def cmd_live(args):
    """One snapshot of every open market (gamma keyset): half-spreads by template and band from the displayed best
    bid/ask, a CLOB book sample per template for depth and to check gamma's quotes, and every ladder whose
    displayed quotes cross, re-read with all of its members in one POST /books."""
    out = Path(args.out)
    http = Http(interval=args.interval)
    t0 = time.time()
    rows = []
    cursor = None
    pages = 0
    while pages < args.max_pages:
        q = {'limit': 100, 'closed': 'false', 'include_tag': 'true', 'volume_num_min': args.min_volume}
        if cursor:
            q['after_cursor'] = cursor
        d = http.request(P.GAMMA + '/markets/keyset?' + urllib.parse.urlencode(q))
        if not isinstance(d, dict) or '__error__' in d:
            print(json.dumps({'error': str(d)[:200], 'page': pages}), flush=True)
            break
        ms = d.get('markets') or []
        pages += 1
        for m in ms:
            if m.get('acceptingOrders') and m.get('enableOrderBook') is not False:
                rows.append(gamma_market_row(m))
        cursor = d.get('next_cursor')
        if not cursor or not ms:
            break
    t_census = time.time()
    now = t_census
    print(json.dumps({'open_accepting': len(rows), 'pages': pages, **http.stats()}), flush=True)
    # book sample per template (stratified by a hash so a rerun draws the same markets where they still exist)
    by_t = collections.defaultdict(list)
    for m in rows:
        if len(m.get('clobTokenIds') or []) == 2 and (m.get('volumeNum') or 0) >= 1000:
            by_t[m['tpl']].append(m)
    sample_tokens = []
    for t, ms in by_t.items():
        ms.sort(key=lambda m: P.stable_u('pm-structure-live:' + str(m['id'])))
        sample_tokens += [m['clobTokenIds'][0] for m in ms[:args.per_template]]
    books = P.fetch_books(http, sample_tokens, batch=40)
    t_books = time.time()
    # ladders: candidates from the displayed quotes, then one atomic read per candidate ladder
    groups = collections.defaultdict(list)
    for m in rows:
        if m['ladder'] and m.get('bestBid') is not None and m.get('bestAsk') is not None:
            groups[(m['ladder'][0], m['ladder'][1])].append(m)
    cands = {}
    n_ladders = 0
    for key, ms in groups.items():
        if len({m['ladder'][2] for m in ms}) < 2:
            continue
        n_ladders += 1
        rungs = []
        for m in ms:
            side = m['ladder'][4]
            bid, ask = m['bestBid'], m['bestAsk']
            if side == 1:
                bid, ask = 1.0 - ask, 1.0 - bid
            rungs.append((m['ladder'][2], m['ladder'][3], {'id': m['id'], 'bid': bid, 'ask': ask}))
        for hi, lo in ladder_pairs(rungs):
            if lo['bid'] > hi['ask']:          # the must-be-lower member bids above the must-be-higher one's ask
                cands[key] = ms
                break
    # series of events: date rungs sharing a question stem across events, ordered only when windows nest
    gx = collections.defaultdict(list)
    for m in rows:
        if m['ladder'] and m['ladder'][0] == 'date' and m.get('bestBid') is not None and m.get('bestAsk') is not None:
            gx[stem_of(m['ladder'][1])].append(m)
    for stem, ms in gx.items():
        if len({m.get('event_id') for m in ms}) < 2 or len({m['ladder'][2] for m in ms}) < 2 or len(ms) > 40:
            continue
        n_ladders += 1
        rungs = [(m['ladder'][2], m['ladder'][3], m) for m in ms]
        for hi, lo in ladder_pairs(rungs):
            if hi.get('event_id') == lo.get('event_id') or not nested(P.start_ts(hi), P.start_ts(lo)):
                continue
            if lo['bestBid'] > hi['bestAsk']:
                cands[('date_x', stem)] = ms
                break
    confirm = {}
    for key, ms in cands.items():
        toks = [m['clobTokenIds'][0] for m in ms]
        t_req = time.time()
        d = http.request(P.CLOB + '/books', body=[{'token_id': tk} for tk in toks])
        if not isinstance(d, list):
            continue
        bk = {b.get('asset_id'): P.parse_book(b) for b in d}
        confirm['%s||%s' % key] = {'at': P.utc(t_req), 'books': bk,
                                   'members': [{k: m.get(k) for k in ('id', 'question', 'groupItemTitle', 'ladder',
                                                                      'clobTokenIds', 'endDate', 'cat', 'tags',
                                                                      'bestBid', 'bestAsk', 'volumeNum', 'tpl',
                                                                      'event_id', 'negRisk', 'startDate',
                                                                      'acceptingOrdersTimestamp', 'createdAt')}
                                               for m in ms]}
    snap = {'at': P.utc(now), 'census_seconds': round(t_census - t0, 1), 'books_seconds': round(t_books - t_census, 1),
            'markets': rows, 'books': books, 'ladders_scanned': n_ladders, 'ladder_candidates': len(cands),
            'confirm': confirm, 'http': http.stats(), 'seconds': round(time.time() - t0, 1)}
    p = out / 'raw' / 'live' / ('snap_%d.json.gz' % int(now))
    write_gz(p, snap)
    man_key = 'live_%d' % int(now)
    update_manifest(out, man_key, {'at': snap['at'], 'file': str(p.relative_to(out)), 'markets': len(rows),
                                   'pages': pages, 'page_cap_hit': pages >= args.max_pages,
                                   'volume_num_min': args.min_volume, 'book_sample': len(books), 'ladders_scanned': n_ladders,
                                   'ladder_candidates_reread': len(confirm), 'http': http.stats(),
                                   'seconds': snap['seconds'],
                                   'sources': [P.GAMMA + '/markets/keyset (closed=false)', P.CLOB + '/books (POST)']})
    print(json.dumps({'at': snap['at'], 'markets': len(rows), 'books': len(books), 'ladders': n_ladders,
                      'candidates': len(cands), 'reread': len(confirm), **http.stats(),
                      'seconds': snap['seconds']}), flush=True)
    return 0


# ------------------------------------------------------------------------------------------------- cost model

THIN_USD = 10000.0          # markets under this lifetime volume pay the thin-market spread table


def half_spread_table(snaps, min_volume=1000.0, max_volume=float('inf')):
    """Median and 75th-percentile half-spread by (template, edge band), (category, edge band) and (all, edge band)
    from the displayed best bid and ask of every open market in the live snapshots."""
    acc = collections.defaultdict(list)
    for sn in snaps:
        now = parse_ts(sn['at'])
        for m in sn['markets']:
            bb, ba = m.get('bestBid'), m.get('bestAsk')
            if bb is None or ba is None or ba <= bb or ba > 1 or bb < 0 or (m.get('volumeNum') or 0) < min_volume:
                continue
            if (m.get('volumeNum') or 0) >= max_volume:
                continue
            if (parse_ts(m.get('endDate')) or 0) < now:     # past its scheduled end: in play or awaiting resolution
                continue
            if len(m.get('outcomes') or []) != 2:
                continue
            mid = (bb + ba) / 2.0
            band = edge_band(mid)
            if band is None:
                continue
            h = (ba - bb) / 2.0
            for key in ((m['tpl'], band), (m['cat'], band), ('all', band)):
                acc['%s|%s' % key].append(h)
    out = {}
    for k, v in acc.items():
        v.sort()
        out[k] = {'n': len(v), 'median': statistics.median(v), 'p75': v[int(0.75 * (len(v) - 1))],
                  'mean': sum(v) / len(v)}
    return out


def half_spread(table, tpl, cat, p, which='median', min_n=30):
    band = edge_band(p)
    for key in ('%s|%s' % (tpl, band), '%s|%s' % (cat, band), 'all|%s' % band):
        r = table.get(key)
        if r and r['n'] >= min_n:
            return r[which]
    return 0.01


# ------------------------------------------------------------------------------------------------- sample

def sample_weights(out, inv_by_id):
    """Weights of the union of the 2026-10-09 stratified sample and this study's template supplement: the two draws
    use independent hashes, so a market's inclusion probability is 1 - (1 - p_main)(1 - q_template)."""
    smp = json.loads((HIST / 'sample.json').read_text())
    pmain = {k: v['prob'] for k, v in smp['plan'].items()}
    sup = json.loads((Path(out) / 'raw' / 'supplement.json').read_text())
    plan = sup['plan']
    ids = {r['id'] for r in smp['markets']} | set(sup['markets'])
    w = {}
    for mid in ids:
        r = inv_by_id.get(mid)
        if r is None:
            continue
        pm = pmain.get('%s|%s' % (r['cat'], r['vb']), 0.0)
        q = plan.get(r['tpl'], 0.0)
        pi = 1.0 - (1.0 - pm) * (1.0 - q)
        if pi > 0:
            w[mid] = 1.0 / pi
    return w


# ------------------------------------------------------------------------------------------------- trades

T_HORIZONS = {'7d': 7 * DAY, '3d': 3 * DAY, '1d': DAY, '6h': 6 * HOUR}
YES_BANDS = [(0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98)]
DYN_K = (1, 6, 24)
DYN_THETA = (0.05, 0.10, 0.20)
DYN_DIR = ('mom', 'rev')
DYN_HOLD = (6, 24, 72, 'res')
DYN_PRICE = (0.05, 0.95)


def yes_band(p):
    for lo, hi in YES_BANDS:
        if lo <= p < hi:
            return '%.2f-%.2f' % (lo, hi)
    return None


def exit_value(p_side_mid, hs, rate):
    """Proceeds per share of selling at the bid (midpoint less the half-spread) as a taker, after the fee."""
    px = max(0.001, p_side_mid - hs)
    return px - P.fee_per_share(rate, px)


def entry_cost(p_side_mid, hs, rate, cap=0.999):
    px = min(cap, p_side_mid + hs)
    return px + P.fee_per_share(rate, px)


def template_trades(m, tpl, w, coarse, fine, hs_table):
    """Entries at each horizon before the scheduled end, both sides, banded on the YES midpoint at entry; plus the
    late-entry twin one hour later at the then-midpoint."""
    out = []
    pay0 = P.binary_payout(m)
    close, end, st = parse_ts(m['closedTime']), parse_ts(m['endDate']), P.start_ts(m)
    rate = fee_rate(m['cat'], m.get('tags'))
    disputed = any('disput' in str(x).lower() for x in (m.get('umaResolutionStatuses') or []))
    for h, secs in T_HORIZONS.items():
        t = end - secs
        if st is None or t < st or t > close - 600:
            continue
        p0, src = P.price_at(coarse, fine, t)
        if p0 is None or p0 <= 0 or p0 >= 1:
            continue
        band = yes_band(p0)
        if band is None:
            continue
        p0l = None
        if t + HOUR <= close - 600:
            p0l, _ = P.price_at(coarse, fine, t + HOUR)
        for side in (0, 1):
            ps = p0 if side == 0 else 1.0 - p0
            pay = pay0 if side == 0 else 1.0 - pay0
            hs = half_spread(hs_table, tpl, m['cat'], p0)
            ret = pay / entry_cost(ps, hs, rate) - 1.0
            ret_late = None
            if p0l is not None and 0 < p0l < 1:
                psl = p0l if side == 0 else 1.0 - p0l
                ret_late = pay / entry_cost(psl, half_spread(hs_table, tpl, m['cat'], p0l), rate) - 1.0
            out.append({'id': m['id'], 'event': m.get('event_id') or m['id'], 'cat': m['cat'], 'tpl': tpl, 'w': w,
                        't': t, 'close': close, 'end': end, 'h': h, 'band': band, 'side': side, 'p': ps, 'p0': p0,
                        'pay': pay, 'ret': ret, 'ret_late': ret_late, 'rate': rate, 'hs': hs, 'src': src,
                        'vol': m.get('volumeNum') or 0.0, 'disputed': disputed,
                        'life_days': (close - st) / DAY})
    return out


def hourly_grid(fine, t0, t1, max_stale=3 * DAY):
    """{hour timestamp: YES midpoint} on whole hours in [t0, t1], last point at or before each hour."""
    out = {}
    if not fine:
        return out
    ts = [x[0] for x in fine]
    h = int(math.ceil(t0 / HOUR) * HOUR)
    while h <= t1:
        i = bisect.bisect_right(ts, h) - 1
        if i >= 0 and h - ts[i] <= max_stale:
            out[h] = fine[i][1]
        h += int(HOUR)
    return out


def dynamics_signals(grid, k, theta):
    """(t, move) for every whole hour whose move over the past k hours is at least theta in absolute value."""
    out = []
    for t in sorted(grid):
        a = grid.get(t - k * int(HOUR))
        if a is None:
            continue
        mv = grid[t] - a
        if abs(mv) >= theta:
            out.append((t, mv))
    return out


def dynamics_trades(m, tpl, w, fine, hs_table):
    """Signals on the hourly series before the scheduled end; enter at the next hour's midpoint plus the half-spread
    and the fee; exit at +h hours at the midpoint less the half-spread and the fee, or hold to resolution when the
    exit would fall at or after the scheduled end or the close. One open trade per market per variant."""
    pay0 = P.binary_payout(m)
    close, end, st = parse_ts(m['closedTime']), parse_ts(m['endDate']), P.start_ts(m)
    if not fine or st is None or close - st <= 2 * DAY:      # fine series is 5-minute for short-lived markets
        return []
    rate = fee_rate(m['cat'], m.get('tags'))
    stop = min(end, close)
    grid = hourly_grid(fine, max(fine[0][0], st), stop - 600)
    if len(grid) < 30:
        return []
    out = []
    for k in DYN_K:
        for theta in DYN_THETA:
            sig = dynamics_signals(grid, k, theta)
            if not sig:
                continue
            for d in DYN_DIR:
                for hold in DYN_HOLD:
                    busy = -1.0
                    for t, mv in sig:
                        if t < busy:
                            continue
                        rec = dyn_one(grid, t, mv, d, hold, pay0, close, stop, tpl, m['cat'], rate, hs_table, 1)
                        if rec is None:
                            continue
                        late = dyn_one(grid, t, mv, d, hold, pay0, close, stop, tpl, m['cat'], rate, hs_table, 2)
                        busy = rec['exit_t']
                        out.append({'id': m['id'], 'event': m.get('event_id') or m['id'], 'cat': m['cat'],
                                    'tpl': tpl, 'w': w, 'v': 'D|k%d|%.2f|%s|%s' % (k, theta, d, hold),
                                    't': rec['entry_t'], 'close': rec['exit_t'], 'ret': rec['ret'],
                                    'ret_late': late['ret'] if late else None, 'p': rec['ps'],
                                    'pay': 1.0 if rec['ret'] > 0 else 0.0, 'held_to_res': rec['res'],
                                    'vol': m.get('volumeNum') or 0.0, 'life_days': (close - st) / DAY})
    return out


def dyn_one(grid, t, mv, d, hold, pay0, close, stop, tpl, cat, rate, hs_table, lag_h):
    te = t + lag_h * int(HOUR)
    if te >= stop - 600 or te not in grid:
        return None
    up = mv > 0
    side = (0 if up else 1) if d == 'mom' else (1 if up else 0)
    pe = grid[te]
    ps = pe if side == 0 else 1.0 - pe
    if not (DYN_PRICE[0] <= ps <= DYN_PRICE[1]):
        return None
    cost = entry_cost(ps, half_spread(hs_table, tpl, cat, pe), rate)
    pay = pay0 if side == 0 else 1.0 - pay0
    if hold == 'res':
        return {'entry_t': te, 'exit_t': close, 'ret': pay / cost - 1.0, 'ps': ps, 'res': True}
    tx = te + int(hold) * int(HOUR)
    if tx >= stop - 600 or tx not in grid:
        if tx >= stop - 600:
            return {'entry_t': te, 'exit_t': close, 'ret': pay / cost - 1.0, 'ps': ps, 'res': True}
        return None
    px = grid[tx]
    pxs = px if side == 0 else 1.0 - px
    val = exit_value(pxs, half_spread(hs_table, tpl, cat, px), rate)
    return {'entry_t': te, 'exit_t': tx, 'ret': val / cost - 1.0, 'ps': ps, 'res': False}


def build_one(args):
    """Worker: one market's template and dynamics trades (runs in a process pool)."""
    mid, m, tpl, w, out, hs_pair = args
    # each market pays the live spread of its own volume class: thin members (under $10k of lifetime volume, which
    # the event-level design brings in) quote 2-8x wider than the $10k universe (2026-10-14 snapshots)
    hs_table = hs_pair[1] if (m.get('volumeNum') or 0) < THIN_USD else hs_pair[0]
    coarse = load_series(out, mid, 'c')
    fine = load_series(out, mid, 'f')
    if not coarse and not fine:
        return mid, None, None
    tt = template_trades(m, tpl, w, coarse, fine, hs_table)
    dt_ = dynamics_trades(m, tpl, w, fine, hs_table) if tpl != 'updown' else []
    return mid, tt, dt_


# ------------------------------------------------------------------------------------------------- protocol

MIN_TRADES = 30


def protocol(variants, cutoff_ts, t_lo, t_hi, ret_key='ret'):
    """choose_then_test over daily series. In sample = trades that closed before the cutoff; out of sample = trades
    entered after it; straddlers belong to neither. A variant needs MIN_TRADES in each part to be eligible for the
    choice (all variants count as tried). Returns (selection, per-variant parts, series, n_is, eligible names)."""
    n_is = int((cutoff_ts - 1) // DAY) - int(t_lo // DAY) + 1
    n_oos = int(t_hi // DAY) - int(cutoff_ts // DAY) + 1
    series, parts, elig = {}, {}, []
    for name, trades in variants.items():
        ins = [t for t in trades if t['close'] < cutoff_ts and t.get(ret_key) is not None]
        oos = [t for t in trades if t['t'] >= cutoff_ts and t.get(ret_key) is not None]
        r_in = [t[ret_key] for t in ins]
        r_oos = [t[ret_key] for t in oos]
        s_in = P.daily_series(ins, r_in, t_lo, cutoff_ts - 1)[0] if ins else []
        s_oos = P.daily_series(oos, r_oos, cutoff_ts, t_hi)[0] if oos else []
        s_in = s_in or [0.0] * n_is
        s_oos = s_oos or [0.0] * n_oos
        series[name] = s_in + s_oos
        parts[name] = {'in': P.summarize(ins, r_in) if ins else {'n': 0},
                       'oos': P.summarize(oos, r_oos) if oos else {'n': 0}}
        if len(ins) >= MIN_TRADES and len(oos) >= MIN_TRADES:
            elig.append(name)
    sel = None
    if elig:
        sel = B.choose_then_test({k: series[k] for k in elig}, frac=n_is / float(n_is + n_oos),
                                 periods_per_year=365, key='sharpe')
        ch = sel['chosen']
        ins = [t for t in variants[ch] if t['t'] >= cutoff_ts]
        sel['oos_cluster_ci'] = P.cluster_bootstrap(ins, [t[ret_key] for t in ins], n=500)
    return sel, parts, series, n_is, elig


def one_sided_p(series):
    t, p = B.newey_west_t(series)
    if p is None:
        return None, None
    return t, (p / 2.0 if t > 0 else 1.0 - p / 2.0)


def calibration_rows(trades):
    """YES calibration by template x horizon x band (side-0 rows only), weighted, with Kish effective n."""
    acc = collections.defaultdict(list)
    for t in trades:
        if t['side'] == 0 and t['pay'] in (0.0, 1.0):
            acc[(t['tpl'], t['h'], t['band'])].append(t)
    rows = []
    for (tpl, h, band), b in sorted(acc.items()):
        sw = sum(t['w'] for t in b)
        k = sum(t['w'] for t in b if t['pay'] == 1.0)
        neff = sw * sw / sum(t['w'] ** 2 for t in b)
        lo, hi = P.wilson(k / sw * neff, neff)
        mp = sum(t['w'] * t['p0'] for t in b) / sw
        rows.append({'tpl': tpl, 'h': h, 'band': band, 'n': len(b), 'n_eff': neff, 'mean_yes_price': mp,
                     'yes_rate': k / sw, 'ci_lo': lo, 'ci_hi': hi, 'edge_pp': 100 * (k / sw - mp),
                     'events': len({t['event'] for t in b})})
    return rows


# ------------------------------------------------------------------------------------------------- ladders: history

LADDER_THETA = (0.0, 0.01, 0.02, 0.05)


def ladder_groups(inv):
    g = collections.defaultdict(list)
    for r in inv:
        if r['ladder']:
            g[(r['ladder'][0], r['ladder'][1])].append(r)
    return g


def side_adjust(series, side):
    if series is None:
        return None
    return series if side == 0 else [[t, 1.0 - p] for t, p in series]


def ladder_history(out, inv, uni, hs_table):
    """Midpoint violations pair by pair, each pair on the grid of its common open window before either scheduled
    end, plus the executable-at-midpoint trade (YES of the member that must be higher, NO of the one that must be
    lower, each paying the median live half-spread and the taker fee), held to both resolutions. A trade is entered
    once per pair and threshold, at the first grid point where the after-cost edge clears the threshold."""
    selj = json.loads((Path(out) / 'raw' / 'ladder_selection.json').read_text())
    px = Path(out) / 'raw' / 'ladder_selection_x.json'
    selx = json.loads(px.read_text()) if px.exists() else {'keys': []}
    g = ladder_groups(inv)
    gx = cross_event_groups(inv, uni)
    n_groups = collections.Counter()
    for (fam, key), rs in g.items():
        if len({x['ladder'][2] for x in rs}) >= 2:
            n_groups[fam] += 1
    n_groups['date_x'] = len(gx)
    fams = list(selj['keys'].items()) + [('date_x', selx['keys'])]
    stats, trades, examples = {}, [], []
    for fam, keys in fams:
        w = n_groups[fam] / float(len(keys)) if keys else 0.0
        coarse = fam in ('date', 'date_x')
        step = 12 * HOUR if coarse else HOUR
        # a point older than this is not a price: prices-history emits a point only when the displayed price moves,
        # and on a thin rung that price can be a stale last trade (first run: +2,927%/yr on strike ladders at 1 day)
        stale = 3 * DAY if coarse else 2 * HOUR
        st = collections.Counter()
        for key in keys:
            rs = gx.get(key, []) if fam == 'date_x' else g[(fam, key)]
            mem = []
            for r in rs:
                m = uni[r['id']]
                ser = load_series(out, r['id'], 'c' if coarse else 'f')
                if not ser:
                    continue
                side = r['ladder'][4]
                pay0 = P.binary_payout(m)
                mem.append({'id': r['id'], 'rung': r['ladder'][2], 'sign': r['ladder'][3], 'side': side,
                            's': side_adjust(ser, side), 'pay': pay0 if side == 0 else 1.0 - pay0,
                            'close': parse_ts(m['closedTime']), 'end': parse_ts(m['endDate']),
                            'start': P.start_ts(m) or ser[0][0], 'cat': m['cat'], 'tpl': r['tpl'],
                            'rate': fee_rate(m['cat'], m.get('tags')), 'event': m.get('event_id'),
                            'q': m.get('question')})
            if len({x['rung'] for x in mem}) < 2:
                st['ladders_without_two_series'] += 1
                continue
            st['ladders'] += 1
            pairs = ladder_pairs([(x['rung'], x['sign'], i) for i, x in enumerate(mem)])
            if fam == 'date_x':
                pairs = [(h, l) for h, l in pairs if mem[h]['event'] != mem[l]['event'] and
                         nested(mem[h]['start'], mem[l]['start'])]
            for hi, lo in pairs:
                A, Bm = mem[hi], mem[lo]
                t0 = max(A['s'][0][0], Bm['s'][0][0], A['start'], Bm['start'])
                t1 = min(A['close'], A['end'], Bm['close'], Bm['end']) - step
                if t1 <= t0:
                    continue
                st['pairs'] += 1
                t = math.ceil(t0 / step) * step
                entered = set()
                while t <= t1:
                    ph, pl = as_of(A['s'], t, max_stale=stale), as_of(Bm['s'], t, max_stale=stale)
                    if ph is not None and pl is not None:
                        st['points'] += 1
                        v = pl - ph
                        for th, lab in ((0.0, 'points_violated'), (0.01, 'points_violated_1c'),
                                        (0.02, 'points_violated_2c'), (0.05, 'points_violated_5c')):
                            if v > th:
                                st[lab] += 1
                        if v > 0:
                            cost = entry_cost(ph, half_spread(hs_table, A['tpl'], A['cat'], ph), A['rate']) + \
                                entry_cost(1.0 - pl, half_spread(hs_table, Bm['tpl'], Bm['cat'], pl), Bm['rate'])
                            edge = 1.0 - cost
                            if edge > 0:
                                st['points_exec_positive'] += 1
                            for th in LADDER_THETA:
                                if edge > th and th not in entered:
                                    entered.add(th)
                                    late = late_edge = None
                                    tl = t + (HOUR if not coarse else step)
                                    if tl <= t1:
                                        a2 = as_of(A['s'], tl, max_stale=stale)
                                        b2 = as_of(Bm['s'], tl, max_stale=stale)
                                        if a2 is not None and b2 is not None:
                                            costl = entry_cost(a2, half_spread(hs_table, A['tpl'], A['cat'], a2),
                                                               A['rate']) + \
                                                entry_cost(1.0 - b2, half_spread(hs_table, Bm['tpl'], Bm['cat'], b2),
                                                           Bm['rate'])
                                            late = min(1.0, A['pay'] + 1.0 - Bm['pay']) / costl - 1.0
                                            late_edge = 1.0 - costl
                                    payout = A['pay'] + 1.0 - Bm['pay']
                                    if payout < 1.0:
                                        st['inconsistent_resolutions'] += 1
                                    trades.append({'v': 'L|%s|%.2f' % (fam, th), 'fam': fam, 'th': th, 'id': A['id'],
                                                   'event': A['event'], 'w': w, 't': t,
                                                   'close': max(A['close'], Bm['close']), 'cost': cost, 'edge': edge,
                                                   'payout': payout, 'ret': min(1.0, payout) / cost - 1.0,
                                               'ret_realized': payout / cost - 1.0, 'ret_late': late,
                                                   'late_edge': late_edge, 'pay': 1.0 if payout >= 1.0 else 0.0,
                                                   'p': ph, 'v_mid': v, 'cat': A['cat'], 'tpl': A['tpl'],
                                                   'pair': [A['id'], Bm['id']], 'sides': [A['side'], Bm['side']]})
                                    if len(examples) < 60 and th == 0.0 and edge > 0.02:
                                        examples.append({'fam': fam, 'at': P.utc(t), 'hi': A['q'][:90],
                                                         'lo': Bm['q'][:90], 'p_hi': ph, 'p_lo': pl,
                                                         'edge_after_costs': edge, 'payout': payout,
                                                         'late_edge': late_edge})
                    t += step
        stats[fam] = dict(st, groups_in_universe=n_groups[fam], selected=len(keys), weight=w,
                          grid_hours=step / HOUR)
    return stats, trades, examples


# ------------------------------------------------------------------------------------------------- ladders: live

def ladder_live(snaps):
    """Executable violations in each snapshot's atomically re-read ladders: the best pair per ladder, walked
    through both books with taker fees."""
    rows = []
    for sn in snaps:
        now = parse_ts(sn['at'])
        full = {m['id']: m for m in sn['markets']}
        for ck, c in (sn.get('confirm') or {}).items():
            mem = []
            for m0 in c['members']:
                # rungs are re-parsed with the current parser from the snapshot's full market row, so a snapshot
                # taken before a parser fix is read with the fix (the 2026-10-14 snapshot at 07:45 was)
                m = dict(full.get(m0['id'], m0))
                lr = ladder_rung(m)
                if not lr or lr[0] != m0['ladder'][0] or (not ck.startswith('date_x||') and lr[1] != m0['ladder'][1]):
                    continue
                m['ladder'] = list(lr)
                tok = m['clobTokenIds'][0]
                b = c['books'].get(tok)
                if not b:
                    continue
                side = m['ladder'][4]
                mem.append({'m': m, 'book': b if side == 0 else mirror(b), 'rung': m['ladder'][2],
                            'sign': m['ladder'][3], 'rate': fee_rate(m['cat'], m.get('tags')),
                            'end': parse_ts(m.get('endDate'))})
            if len({x['rung'] for x in mem}) < 2:
                continue
            best = None
            pairs = ladder_pairs([(x['rung'], x['sign'], i) for i, x in enumerate(mem)])
            if ck.startswith('date_x||'):
                pairs = [(h, l) for h, l in pairs if mem[h]['m'].get('event_id') != mem[l]['m'].get('event_id') and
                         nested(P.start_ts(mem[h]['m']), P.start_ts(mem[l]['m']))]
            for hi, lo in pairs:
                f = violation_fill(mem[hi]['book'], mem[lo]['book'], mem[hi]['rate'], mem[lo]['rate'])
                if f['profit'] > 0 and (best is None or f['profit'] > best[0]['profit']):
                    best = (f, hi, lo)
            fam_name = ck.split('||')[0]
            if not best:
                rows.append({'at': sn['at'], 'key': ck, 'fam': fam_name, 'profit': 0.0})
                continue
            f, hi, lo = best
            a, b = mem[hi], mem[lo]
            ends = [x for x in (a['end'], b['end']) if x]
            days = max(1.0 / 24, (max(ends) - now) / DAY + (0.125 if a['m']['ladder'][0] in ('total', 'spread')
                                                             else 0.0)) if ends else None
            ret = f['profit'] / f['cost'] if f['cost'] > 0 else None
            rows.append({'at': sn['at'], 'key': ck, 'fam': fam_name, 'profit': f['profit'],
                         'cost': f['cost'], 'sets': f['sets'], 'first_edge': f['first_edge'], 'ret': ret,
                         'days': days, 'ann_excess': (ret * 365.0 / days - SSR) if (ret is not None and days) else None,
                         'hi': a['m']['question'], 'lo': b['m']['question'], 'cat': a['m']['cat'],
                         'pair': [a['m']['id'], b['m']['id']]})
    return rows


# ------------------------------------------------------------------------------------------------- analyze

def classifier_report(out):
    rows = json.loads((Path(out) / 'hand_labels.json').read_text())
    for r in rows:
        r['regex_now'] = classify(r['question'], r['event_title'], r['group'], r['cat'])
    prec, rec = {}, {}
    for t in TEMPLATES:
        pr = [r for r in rows if r['regex_now'] == t]
        rc = [r for r in rows if r['hand'] == t]
        if pr:
            prec[t] = {'n': len(pr), 'correct': sum(r['hand'] == t for r in pr),
                       'precision': sum(r['hand'] == t for r in pr) / len(pr)}
        if rc:
            rec[t] = {'n': len(rc), 'found': sum(r['regex_now'] == t for r in rc),
                      'recall': sum(r['regex_now'] == t for r in rc) / len(rc)}
    rnd = [r for r in rows if r['draw'] == 'random']
    return {'labelled': len(rows), 'stratified': len(rows) - len(rnd), 'random': len(rnd),
            'accuracy_all': sum(r['hand'] == r['regex_now'] for r in rows) / len(rows),
            'accuracy_random_draw': (sum(r['hand'] == r['regex_now'] for r in rnd) / len(rnd)) if rnd else None,
            'macro_precision': statistics.mean(v['precision'] for v in prec.values()),
            'precision_by_template': prec, 'recall_by_template': rec,
            'confusions': [{'n': r['n'], 'hand': r['hand'], 'regex': r['regex_now'], 'q': r['question'][:100]}
                           for r in rows if r['hand'] != r['regex_now']],
            'note': 'labels written blind to the regex output; classifier frozen before the comparison'}


def depth_table(snaps):
    """USD at the best ask for buying each side, from the sampled CLOB books, keyed by (template, band of the
    side's price) and (all, band)."""
    acc = collections.defaultdict(list)
    chk = []
    for sn in snaps:
        tok_m = {}
        for m in sn['markets']:
            if m.get('clobTokenIds'):
                tok_m[m['clobTokenIds'][0]] = m
        for tok, b in (sn.get('books') or {}).items():
            m = tok_m.get(tok)
            if not m:
                continue
            asks, bids = b.get('asks') or [], b.get('bids') or []
            if asks and bids:
                chk.append((m.get('bestBid'), m.get('bestAsk'), bids[0][0], asks[0][0]))
            if asks:
                band = yes_band(asks[0][0])
                if band:
                    for key in ((m['tpl'], band), ('all', band)):
                        acc['%s|%s' % key].append(asks[0][0] * asks[0][1])
            if bids:
                px = 1.0 - bids[0][0]
                band = yes_band(px)
                if band:
                    for key in ((m['tpl'], band), ('all', band)):
                        acc['%s|%s' % key].append(px * bids[0][1])
    out = {k: {'n': len(v), 'median_usd': statistics.median(v), 'p25_usd': sorted(v)[int(0.25 * (len(v) - 1))]}
           for k, v in acc.items()}
    same = [1 for gb, ga, bb, ba in chk if gb is not None and ga is not None and abs(gb - bb) < 1e-9 and
            abs(ga - ba) < 1e-9]
    dif = [abs(((gb + ga) / 2) - ((bb + ba) / 2)) for gb, ga, bb, ba in chk if gb is not None and ga is not None]
    hs_g = [(ga - gb) / 2 for gb, ga, bb, ba in chk if gb is not None and ga is not None]
    hs_b = [(ba - bb) / 2 for gb, ga, bb, ba in chk]
    check = {'books': len(chk), 'gamma_equals_book_share': (len(same) / len(chk)) if chk else None,
             'mid_abs_diff_median': statistics.median(dif) if dif else None,
             'mid_abs_diff_p90': sorted(dif)[int(0.9 * (len(dif) - 1))] if dif else None,
             'half_spread_median_gamma': statistics.median(hs_g) if hs_g else None,
             'half_spread_median_books': statistics.median(hs_b) if hs_b else None}
    return out, check


def depth_for(dtab, tpl, p_side):
    band = yes_band(min(0.979, max(0.02, p_side)))
    for key in ('%s|%s' % (tpl, band), 'all|%s' % band):
        r = dtab.get(key)
        if r and r['n'] >= 10:
            return r['median_usd']
    return 0.0


def capacity_for(trades_oos, dtab, cutoff_ts, t_hi, ann_excess, adv_share=0.10):
    """$/yr at capacity: universe-scaled entries per day out of sample, each sized at the lesser of the median live
    depth at the best ask for its template and side-price band and 10% of the market's average daily volume, held
    for the realised days, earning the out-of-sample annualised excess over SSR."""
    if not trades_oos:
        return None
    days_span = max(1.0, (t_hi - cutoff_ts) / DAY)
    per_day = sum(t['w'] for t in trades_oos) / days_span
    sizes, holds = [], []
    for t in trades_oos:
        adv = (t.get('vol') or 0.0) / max(1.0, t.get('life_days') or 1.0)
        sizes.append(min(depth_for(dtab, t['tpl'], t['p']), adv_share * adv) if adv > 0 else
                     depth_for(dtab, t['tpl'], t['p']))
        holds.append(max(1.0 / 24, (t['close'] - t['t']) / DAY))
    sw = sum(t['w'] for t in trades_oos)
    size = sum(t['w'] * z for t, z in zip(trades_oos, sizes)) / sw
    hold = sum(t['w'] * h for t, h in zip(trades_oos, holds)) / sw
    capital = per_day * size * hold
    return {'entries_per_day_universe': per_day, 'mean_size_usd': size, 'mean_hold_days': hold,
            'capital_usd': capital, 'oos_ann_excess': ann_excess,
            'usd_per_year': capital * (ann_excess or 0.0)}


def late_entry(trades, cutoff_ts):
    """Same OOS trades re-priced one hour later: mean return per trade and annualised excess for both."""
    oos = [t for t in trades if t['t'] >= cutoff_ts and t.get('ret_late') is not None]
    if not oos:
        return None
    a = P.summarize(oos, [t['ret'] for t in oos])
    b = P.summarize(oos, [t['ret_late'] for t in oos])
    share = (b['mean_return'] / a['mean_return']) if a.get('mean_return') else None
    return {'trades': len(oos), 'mean_return_orig': a['mean_return'], 'mean_return_late': b['mean_return'],
            'ann_excess_orig': a.get('ann_excess'), 'ann_excess_late': b.get('ann_excess'),
            'share_of_edge_kept': share}


def summarize_family(name, sel, parts, series, n_is, elig, variants, cutoff_ts, t_hi, dtab):
    fam = {'variants': len(variants), 'eligible': len(elig), 'selection': sel,
           'variant_summary': {k: {'in_n': v['in'].get('n'), 'in_mean_ret': v['in'].get('mean_return'),
                                   'in_ann_excess': v['in'].get('ann_excess'), 'oos_n': v['oos'].get('n'),
                                   'oos_mean_ret': v['oos'].get('mean_return'),
                                   'oos_ann_excess': v['oos'].get('ann_excess'),
                                   'oos_win_rate': v['oos'].get('win_rate'),
                                   'oos_mean_price': v['oos'].get('mean_price'),
                                   'oos_events': v['oos'].get('events')} for k, v in parts.items()}}
    if sel:
        ch = sel['chosen']
        fam['chosen'] = ch
        fam['chosen_parts'] = parts[ch]
        fam['late_entry'] = late_entry(variants[ch], cutoff_ts)
        oos = [t for t in variants[ch] if t['t'] >= cutoff_ts]
        fam['capacity'] = capacity_for(oos, dtab, cutoff_ts, t_hi, parts[ch]['oos'].get('ann_excess'))
        fam['go_checks'] = {'in_sample_positive': sel['in_sample_positive'],
                            'oos_t_ge_2': (sel['oos_t'] or 0) >= 2.0,
                            'in_family_bh_positive': ch in sel['bh_survivors_positive'],
                            'excess_over_ssr_positive': (parts[ch]['oos'].get('ann_excess') or -1) > 0}
    return fam


def _rate(rows, wkey):
    sw = sum(r[wkey] for r in rows)
    if sw <= 0:
        return None
    k = sum(r[wkey] * r['pay'] for r in rows)
    pr = sum(r[wkey] * r['p0'] for r in rows)
    neff = sw * sw / sum(r[wkey] ** 2 for r in rows)
    lo, hi = P.wilson(k / sw * neff, neff)
    return {'n': len(rows), 'yes_rate': k / sw, 'mean_price': pr / sw, 'gap_pp': 100 * (k - pr) / sw,
            'ci_lo': lo, 'ci_hi': hi}


def selection_bias_table(T_all):
    """YES resolution rate against the mean YES midpoint, one day before the scheduled end, by template:
    before = the union sample of the $10k universe at market weights; after = the corrected design; and, inside the
    completed events alone, their universe members against all of their tradable members (the same events, so the
    difference is the volume floor and nothing else)."""
    rows = [t for t in T_all if t['side'] == 0 and t['h'] == '1d' and t['pay'] in (0.0, 1.0)]
    out = {}
    for tpl in TEMPLATES + ['ALL_MULTI']:
        sel = rows if tpl == 'ALL_MULTI' else [t for t in rows if t['tpl'] == tpl]
        before = [t for t in sel if t['w_union']]
        after = [dict(t, wd=t['w_design']) for t in sel if t['part']]
        b_all = [dict(t, wd=t['w_design']) for t in sel if t['part'] == 'B']
        b_uni = [t for t in b_all if t['in_universe']]
        out[tpl] = {'before_union_sample': _rate(before, 'w_union') if before else None,
                    'after_corrected_design': _rate(after, 'wd') if after else None,
                    'completed_events_universe_members_only': _rate(b_uni, 'wd') if b_uni else None,
                    'completed_events_all_tradable_members': _rate(b_all, 'wd') if b_all else None}
    return out


def cmd_analyze(args):
    out = Path(args.out)
    t_run = time.time()
    uni = {m['id']: m for m in P.load_universe(HIST)}
    inv = read_gz(out / 'raw' / 'inventory.json.gz')
    inv_by_id = {r['id']: r for r in inv}
    snaps = [read_gz(p) for p in sorted((out / 'raw' / 'live').glob('snap_*.json.gz'))]
    # the history universe is markets with at least $10k of volume at close; the live table matches that floor
    hs_table = half_spread_table(snaps, min_volume=THIN_USD)
    hs_thin = half_spread_table(snaps, min_volume=1000.0, max_volume=THIN_USD)
    hs_table_1k = half_spread_table(snaps, min_volume=1000.0)
    dtab, book_check = depth_table(snaps)
    cutoff_ts, start_ts_ = parse_ts(CUTOFF), parse_ts(START)
    res = {'generated': P.utc(), 'cutoff': CUTOFF, 'start': START, 'ssr': SSR,
           'fee_schedule': 'fee = shares x feeRate x p x (1 - p), taker only; polymarket_history.fee_rate',
           'classifier': classifier_report(out),
           'live': {'snapshots': [{'at': sn['at'], 'markets': len(sn['markets']), 'books': len(sn['books']),
                                   'ladders_scanned': sn['ladders_scanned'],
                                   'ladder_candidates_reread': len(sn.get('confirm') or {})} for sn in snaps],
                    'half_spread': hs_table, 'half_spread_thin_1k_10k': hs_thin,
                    'half_spread_min_volume_1k': {k: v for k, v in hs_table_1k.items() if k.startswith('all|')},
                    'depth_best_ask': dtab, 'gamma_vs_books': book_check}}
    # inventory and the corrected (event-level) design
    cnt = collections.Counter(r['tpl'] for r in inv)
    w = sample_weights(out, inv_by_id)
    in_union = collections.Counter(inv_by_id[m]['tpl'] for m in w)
    sup = json.loads((out / 'raw' / 'supplement.json').read_text())
    events = read_gz(out / 'raw' / 'events_full.json.gz')
    design, dsum, fix = event_design(out, uni, inv_by_id, events)
    tpl_of = {}
    for mid, (row, wt, part) in design.items():
        tpl_of[mid] = inv_by_id[mid]['tpl'] if mid in inv_by_id else \
            classify(row.get('question'), row.get('event_title'), row.get('groupItemTitle'), row.get('cat'))
    in_design = collections.Counter(tpl_of[m] for m in design)
    res['inventory'] = {'eligible_binary': len(inv), 'union_sample': len(w), 'supplement_markets': len(sup['markets']),
                        'supplement_plan': sup['plan'], 'design': dsum,
                        'by_template': {t: {'universe': cnt[t], 'union_sample': in_union[t],
                                            'corrected_design': in_design[t]} for t in TEMPLATES}}
    # trades for the union sample (the biased estimate, kept for the before/after table) and the design
    ids = set(w) | set(design)
    jobs = []
    for mid in ids:
        if mid in design:
            row, tpl = design[mid][0], tpl_of[mid]
        else:
            row, tpl = uni.get(mid), inv_by_id.get(mid, {}).get('tpl')
        if row is None or tpl is None:
            continue
        jobs.append((mid, row, tpl, 1.0, str(out), (hs_table, hs_thin)))
    T_all, D = [], []
    meta = collections.Counter()
    with cf.ProcessPoolExecutor(max_workers=args.workers) as ex:
        for mid, tt, dd in ex.map(build_one, jobs, chunksize=100):
            if tt is None:
                meta['no_series'] += 1
                continue
            meta['with_series'] += 1
            part = design[mid][2] if mid in design else None
            wd = design[mid][1] if mid in design else None
            for x in tt:
                x.update(w_union=w.get(mid), w_design=wd, part=part, in_universe=mid in uni)
            T_all.extend(x for x in tt if x['t'] >= start_ts_)
            if part:
                for x in dd:
                    x['w'] = wd
                    x['part'] = part
                D.extend(x for x in dd if x['t'] >= start_ts_)
    T = []
    for x in T_all:
        if x['part']:
            y = dict(x)
            y['w'] = x['w_design']
            T.append(y)
    res['meta'] = dict(meta, template_trades_all=len(T_all), template_trades_design=len(T), dynamics_trades=len(D),
                       seconds_trades=round(time.time() - t_run, 1))
    res['selection_bias'] = selection_bias_table(T_all)
    print(json.dumps(res['meta']), flush=True)
    t_hi = max([t['close'] for t in T + D] or [time.time()])
    t_lo = start_ts_
    # ---- (a)/(b): templates
    tv = collections.defaultdict(list)
    for t in T:
        if t['tpl'] in TRADED_TEMPLATES and not (t['cat'] == 'crypto_updown' and t['tpl'] == 'updown'):
            tv['T|%s|%s|%s|%s' % (t['tpl'], t['h'], t['band'], 'YES' if t['side'] == 0 else 'NO')].append(t)
    defined = ['T|%s|%s|%s|%s' % (tpl, h, '%.2f-%.2f' % b, sd) for tpl in TRADED_TEMPLATES for h in T_HORIZONS
               for b in YES_BANDS for sd in ('YES', 'NO')]
    for k in defined:
        tv.setdefault(k, [])
    all_series = {}
    fams = {}
    for tpl in TRADED_TEMPLATES:
        vs = {k: v for k, v in tv.items() if k.split('|')[1] == tpl}
        sel, parts, series, n_is, elig = protocol(vs, cutoff_ts, t_lo, t_hi)
        all_series.update(series)
        fams[tpl] = summarize_family(tpl, sel, parts, series, n_is, elig, vs, cutoff_ts, t_hi, dtab)
        fams[tpl]['hypothesis'] = HYPOTHESIS[tpl]
    res['templates'] = {'variants_defined': len(defined), 'families': fams,
                        'calibration': calibration_rows(T),
                        'robust_spread_p75': {}}
    # ---- (d): dynamics
    dv = collections.defaultdict(list)
    for t in D:
        dv[t['v']].append(t)
    ddef = ['D|k%d|%.2f|%s|%s' % (k, th, d, h) for k in DYN_K for th in DYN_THETA for d in DYN_DIR for h in DYN_HOLD]
    for k in ddef:
        dv.setdefault(k, [])
    sel, parts, series, n_is_d, elig = protocol(dv, cutoff_ts, t_lo, t_hi)
    all_series.update(series)
    res['dynamics'] = summarize_family('dynamics', sel, parts, series, n_is_d, elig, dv, cutoff_ts, t_hi, dtab)
    res['dynamics']['variants_defined'] = len(ddef)
    # ---- (c): ladders, history
    lstats, LT, lex = ladder_history(out, inv, uni, hs_table)
    lv = collections.defaultdict(list)
    for t in LT:
        lv[t['v']].append(t)
    ldef = ['L|%s|%.2f' % (f, th) for f in LADDER_TARGET for th in LADDER_THETA]
    for k in ldef:
        lv.setdefault(k, [])
    sel, parts, series, n_is_l, elig = protocol(lv, cutoff_ts, t_lo, t_hi)
    all_series.update(series)
    res['ladders'] = {'history_stats': lstats, 'history_examples': lex,
                      'protocol': summarize_family('ladders', sel, parts, series, n_is_l, elig, lv, cutoff_ts,
                                                   t_hi, dtab)}
    res['ladders']['protocol']['variants_defined'] = len(ldef)
    edges = [t['edge'] for t in LT if t['th'] == 0.0]
    late_edges = [t['late_edge'] for t in LT if t['th'] == 0.0 and t['late_edge'] is not None]
    res['ladders']['history_entries_theta0'] = {
        'entries': len(edges), 'median_edge_after_costs': statistics.median(edges) if edges else None,
        'late_entries_measured': len(late_edges),
        'late_still_positive_share': (sum(1 for e in late_edges if e > 0) / len(late_edges)) if late_edges else None}
    # ---- (c): ladders, live
    lrows = ladder_live(snaps)
    res['ladders']['live'] = summarize_live_ladders(lrows, snaps)
    # ---- multiple testing across everything tried
    n_is = n_is_d
    names = sorted(all_series)
    p_full, p_oos = [], []
    for k in names:
        p_full.append(one_sided_p(all_series[k])[1])
        p_oos.append(one_sided_p(all_series[k][n_is:])[1])
    conservative = [1.0 if p is None else p for p in p_full]
    rej_full, adj_full = B.bh(conservative, q=0.10)
    conservative_o = [1.0 if p is None else p for p in p_oos]
    rej_oos, adj_oos = B.bh(conservative_o, q=0.10)
    res['multiple_testing'] = {
        'variants_tried_total': len(names), 'templates': len(defined), 'dynamics': len(ddef), 'ladders': len(ldef),
        'q': 0.10, 'one_sided': True, 'untestable_counted_as_p1': sum(1 for p in p_full if p is None),
        'bh_survivors_full_sample': [k for k, r in zip(names, rej_full) if r],
        'bh_survivors_oos_only': [k for k, r in zip(names, rej_oos) if r],
        'smallest_p_full': sorted(((p, k) for p, k in zip(p_full, names) if p is not None))[:15],
        'smallest_p_oos': sorted(((p, k) for p, k in zip(p_oos, names) if p is not None))[:15]}
    surv = set(res['multiple_testing']['bh_survivors_full_sample'])
    # near misses: positive in both halves; how much more out-of-sample data would make t reach 2, and reach the
    # first BH rank across everything tried (one-sided z for q/m), if the effect held at its measured size
    z_bh = statistics.NormalDist().inv_cdf(1.0 - 0.10 / len(names))
    parts_all = {}
    for fam in fams.values():
        parts_all.update({k: v for k, v in fam['variant_summary'].items()})
    parts_all.update(res['dynamics']['variant_summary'])
    parts_all.update(res['ladders']['protocol']['variant_summary'])
    nm = []
    for k in names:
        v = parts_all.get(k)
        if not v or (v.get('oos_n') or 0) < MIN_TRADES or (v.get('in_n') or 0) < MIN_TRADES:
            continue
        if (v.get('in_ann_excess') or -1) <= 0 or (v.get('oos_ann_excess') or -1) <= 0:
            continue
        t_o, _ = B.newey_west_t(all_series[k][n_is:])
        if not t_o or t_o <= 0:
            continue
        nm.append({'variant': k, 'oos_t': t_o, 'oos_n': v['oos_n'], 'oos_ann_excess': v['oos_ann_excess'],
                   'in_ann_excess': v['in_ann_excess'], 'data_multiple_for_t2': (2.0 / t_o) ** 2,
                   'data_multiple_for_bh': (z_bh / t_o) ** 2, 'in_global_bh': k in surv})
    nm.sort(key=lambda r: r['data_multiple_for_t2'])
    res['near_misses'] = {'z_needed_for_bh_rank1': z_bh, 'oos_days': len(all_series[names[0]]) - n_is,
                          'rows': nm[:25]}
    # ---- go decisions
    gos = []
    for label, fam in [('template:' + k, v) for k, v in fams.items()] + [('dynamics', res['dynamics']),
                                                                         ('ladders', res['ladders']['protocol'])]:
        if not fam.get('selection'):
            continue
        ch = fam['chosen']
        sel = fam['selection']
        checks = dict(fam['go_checks'], global_bh_positive=ch in surv,
                      usd_per_year_positive=((fam.get('capacity') or {}).get('usd_per_year') or 0) > 0)
        gos.append({'family': label, 'chosen': ch, 'checks': checks, 'go': all(checks.values()),
                    'oos_t': sel['oos_t'], 'oos_ann_excess': fam['chosen_parts']['oos'].get('ann_excess'),
                    'in_ann_excess': fam['chosen_parts']['in'].get('ann_excess'),
                    'oos_n': fam['chosen_parts']['oos'].get('n'),
                    'late_share': (fam.get('late_entry') or {}).get('share_of_edge_kept'),
                    'usd_per_year': (fam.get('capacity') or {}).get('usd_per_year')})
    # ladders: a midpoint violation valued at its locked payout wins by construction, so the history is an upper
    # bound and only the live atomic reads can show the trade exists; the ladder go needs live value over SSR
    lvd = (res['ladders']['live'] or {}).get('value_per_day_usd_estimate') or 0.0
    for gg in gos:
        if gg['family'] == 'ladders':
            gg['checks']['live_executable_value_positive'] = lvd > 0
            gg['usd_per_year_history_upper_bound'] = gg['usd_per_year']
            gg['usd_per_year'] = lvd * 365.0
            gg['checks']['usd_per_year_positive'] = lvd > 0
            gg['go'] = all(gg['checks'].values())
    res['go'] = gos
    res['seconds'] = round(time.time() - t_run, 1)
    P.write_json(out / 'analysis.json', res)
    keep_d = {res['dynamics'].get('chosen')}
    write_gz(out / 'raw' / 'trades.json.gz', {'templates': T, 'ladders': LT,
                                              'dynamics_chosen': [t for t in D if t['v'] in keep_d]})
    update_manifest(out, 'analysis', {'generated': res['generated'], 'variants_tried_total': len(names),
                                      'template_trades': len(T), 'dynamics_trades': len(D),
                                      'ladder_trades': len(LT), 'seconds': res['seconds']})
    print(json.dumps({'variants': len(names), 'bh_full': res['multiple_testing']['bh_survivors_full_sample'][:20],
                      'go': [g for g in gos if g['go']]}, default=str), flush=True)
    return 0


def cmd_confirm(args):
    """The pre-registered confirmation test (confirm_preregistration.json): the three hypotheses, evaluated once on
    fresh, complete 2026 events that share no event with the union sample."""
    out = Path(args.out)
    reg = json.loads((out / 'confirm_preregistration.json').read_text())
    a = json.loads((out / 'analysis.json').read_text())
    evs = read_gz(out / 'raw' / 'confirm_events.json.gz')
    sel = json.loads((out / 'raw' / 'confirm_selection.json').read_text())
    snaps = [read_gz(p) for p in sorted((out / 'raw' / 'live').glob('snap_*.json.gz'))]
    hs_table = half_spread_table(snaps, min_volume=THIN_USD)
    hs_thin = half_spread_table(snaps, min_volume=1000.0, max_volume=THIN_USD)
    dtab, _ = depth_table(snaps)
    cutoff_ts = parse_ts(CUTOFF)
    w_event = sel['candidates'] / float(max(1, len(sel['events'])))
    hyp = {h: [] for h in reg['hypotheses']}
    n_members = n_series = 0
    for e in evs.values():
        for x in event_members(e):
            n_members += 1
            fine = load_series(out, x['id'], 'f')
            if not fine:
                continue
            n_series += 1
            tpl = classify(x.get('question'), x.get('event_title'), x.get('groupItemTitle'), x.get('cat'))
            tbl = hs_thin if (x.get('volumeNum') or 0) < THIN_USD else hs_table
            for t in template_trades(x, tpl, w_event, None, fine, tbl):
                key = 'T|%s|%s|%s|%s' % (t['tpl'], t['h'], t['band'], 'YES' if t['side'] == 0 else 'NO')
                if key in hyp and t['t'] >= cutoff_ts:
                    hyp[key].append(t)
    t_hi = max([t['close'] for v in hyp.values() for t in v] or [time.time()])
    res = {'registered': reg, 'events': len(evs), 'members_tradable': n_members, 'members_with_series': n_series,
           'event_weight': w_event, 'results': {}}
    pv = []
    for h, trades in hyp.items():
        if not trades:
            res['results'][h] = {'n': 0}
            pv.append(None)
            continue
        rets = [t['ret'] for t in trades]
        series = P.daily_series(trades, rets, cutoff_ts, t_hi)[0]
        tt, p1 = one_sided_p(series)
        pv.append(p1)
        summ = P.summarize(trades, rets)
        thick = [t for t in trades if t['vol'] >= THIN_USD]
        thin = [t for t in trades if t['vol'] < THIN_USD]
        summ['by_volume_class'] = {
            'over_10k': P.summarize(thick, [t['ret'] for t in thick]) if thick else {'n': 0},
            'under_10k': P.summarize(thin, [t['ret'] for t in thin]) if thin else {'n': 0}}
        res['results'][h] = dict(summ, hac_t=tt, p_one_sided=p1, cluster_ci=P.cluster_bootstrap(trades, rets, n=500),
                                 late_entry=late_entry(trades, cutoff_ts),
                                 capacity=capacity_for(trades, dtab, cutoff_ts, t_hi, summ.get('ann_excess')))
    rej, adj = B.bh([1.0 if p is None else p for p in pv], q=0.10)
    for (h, r), rj, ad in zip(res['results'].items(), rej, adj):
        r['bh_adjusted_p'] = ad
        r['confirmed'] = bool(rj and (r.get('hac_t') or 0) >= 2.0 and (r.get('mean_return') or 0) > 0)
    a['confirmation'] = res
    # registered as the deciding test: a chosen variant it re-tests must also confirm on the fresh events
    for gg in a['go']:
        if gg['family'].startswith('template:') and gg['chosen'] in res['results']:
            rr = res['results'][gg['chosen']]
            gg['checks']['fresh_event_confirmation'] = bool(rr.get('confirmed'))
            gg['fresh_event_t'] = rr.get('hac_t')
            gg['fresh_event_usd_per_year'] = (rr.get('capacity') or {}).get('usd_per_year')
            gg['go'] = all(gg['checks'].values())
    a['multiple_testing']['variants_tried_total_with_confirmation'] = a['multiple_testing']['variants_tried_total'] + \
        len(reg['hypotheses'])
    P.write_json(out / 'analysis.json', a)
    update_manifest(out, 'confirmation', {'generated': P.utc(), 'events': len(evs), 'members_with_series': n_series,
                                          'hypotheses': reg['hypotheses']})
    print(json.dumps({h: {k: r.get(k) for k in ('n', 'events', 'mean_return', 'ann_excess', 'hac_t', 'p_one_sided',
                                                'confirmed', 'win_rate', 'mean_price')}
                      for h, r in res['results'].items()}, indent=1, default=str))
    return 0


def summarize_live_ladders(rows, snaps):
    pos = [r for r in rows if r['profit'] > 0]
    by_snap = collections.defaultdict(list)
    for r in pos:
        by_snap[r['at']].append(r)
    ats = sorted({sn['at'] for sn in snaps})
    persist = None
    if len(ats) > 1:
        keyed = {(r['at'], r['key']) for r in pos}
        nxt = dict(zip(ats, ats[1:]))
        cand = [r for r in pos if r['at'] in nxt]
        if cand:
            persist = sum(1 for r in cand if (nxt[r['at']], r['key']) in keyed) / len(cand)
    per = []
    for a in ats:
        rs = by_snap.get(a, [])
        per.append({'at': a, 'violations': len(rs), 'profit_usd': sum(r['profit'] for r in rs),
                    'capital_usd': sum(r['cost'] for r in rs),
                    'beating_ssr': sum(1 for r in rs if (r.get('ann_excess') or -1) > 0),
                    'profit_beating_ssr_usd': sum(r['profit'] for r in rs if (r.get('ann_excess') or -1) > 0),
                    'by_family': dict(collections.Counter(r['fam'] for r in rs))})
    span_h = ((parse_ts(ats[-1]) - parse_ts(ats[0])) / HOUR) if len(ats) > 1 else None
    first = per[0]['profit_beating_ssr_usd'] if per else 0.0
    new = 0.0
    if len(ats) > 1:
        seen = {r['key'] for r in by_snap.get(ats[0], [])}
        for a in ats[1:]:
            for r in by_snap.get(a, []):
                if r['key'] not in seen and (r.get('ann_excess') or -1) > 0:
                    new += r['profit']
                seen.add(r['key'])
    per_day = None
    if span_h:
        per_day = first + new / span_h * 24.0
    return {'reread_ladders': len(rows), 'positive_rows': len(pos), 'per_snapshot': per,
            'persistence_next_snapshot': persist, 'span_hours': span_h,
            'value_per_day_usd_estimate': per_day,
            'value_per_day_note': 'profit beating SSR at the first snapshot plus new violations per hour x 24',
            'examples': sorted(pos, key=lambda r: -r['profit'])[:15]}


# ------------------------------------------------------------------------------------------------- render

def _pct(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def _num(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


def _usd(x):
    return '—' if x is None else '${:,.0f}'.format(x)


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_structure_scan tables (%s)' % a['generated'], '',
         'Every number is in `analysis.json`; keys are given in each heading.', '']
    c = a['classifier']
    L += ['## Template classifier (`classifier`)', '',
          '%d hand labels (%d stratified by regex template, %d uniform random). Accuracy %s overall, %s on the random '
          'draw; macro precision %s.' % (c['labelled'], c['stratified'], c['random'], _pct(c['accuracy_all']),
                                          _pct(c['accuracy_random_draw']), _pct(c['macro_precision'])), '',
          '| template | regex-labelled | precision | hand-labelled | recall | universe | union sample |',
          '|---|---:|---:|---:|---:|---:|---:|']
    inv = a['inventory']['by_template']
    for t in TEMPLATES:
        pr = c['precision_by_template'].get(t, {})
        rc = c['recall_by_template'].get(t, {})
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (t, pr.get('n', 0), _pct(pr.get('precision')),
                                                         rc.get('n', 0), _pct(rc.get('recall')),
                                                         '{:,}'.format(inv[t]['universe']),
                                                         '{:,}'.format(inv[t]['union_sample'])))
    L += ['', '## Live half-spread by edge band (`live.half_spread`)', '',
          '| band (distance of YES mid from 0 or 1) | all: n | median | p75 |', '|---|---:|---:|---:|']
    for lo, hi in EDGE_BANDS:
        k = 'all|%.2f-%.2f' % (lo, min(hi, 0.5))
        r = a['live']['half_spread'].get(k, {})
        L.append('| %s | %s | %s | %s |' % (k[4:], r.get('n'), _num(r.get('median'), 4), _num(r.get('p75'), 4)))
    g = a['live']['gamma_vs_books']
    L += ['', 'Gamma quotes against CLOB books (`live.gamma_vs_books`): %s books, identical best bid and ask in %s, '
          'median half-spread %s (gamma) vs %s (books).' % (g['books'], _pct(g['gamma_equals_book_share']),
                                                           _num(g['half_spread_median_gamma'], 4),
                                                           _num(g['half_spread_median_books'], 4)), '']
    L += ['## Templates: chosen variant per family (`templates.families.<tpl>`)', '',
          '| family | hyp | eligible/variants | chosen | IS excess | OOS excess | OOS n | OOS t | OOS rank | '
          'in-family BH | late share | $/yr |', '|---|---|---:|---|---:|---:|---:|---:|---:|---|---:|---:|']
    for t, f in a['templates']['families'].items():
        sel = f.get('selection')
        if not sel:
            L.append('| %s | %s | %d/%d | (none eligible) | | | | | | | | |' % (t, f['hypothesis'], f['eligible'],
                                                                              f['variants']))
            continue
        cp = f['chosen_parts']
        L.append('| %s | %s | %d/%d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            t, f['hypothesis'], f['eligible'], f['variants'], f['chosen'][2 + len(t) + 1:],
            _pct(cp['in'].get('ann_excess')), _pct(cp['oos'].get('ann_excess')), cp['oos'].get('n'),
            _num(sel['oos_t']), '%d/%d' % (sel['oos_rank'], sel['n_variants']),
            'yes' if f['chosen'] in sel['bh_survivors_positive'] else 'no',
            _pct((f.get('late_entry') or {}).get('share_of_edge_kept'), 0),
            _usd((f.get('capacity') or {}).get('usd_per_year'))))
    mt = a['multiple_testing']
    L += ['', '## Multiple testing (`multiple_testing`)', '',
          '%d variants tried (templates %d, dynamics %d, ladders %d). One-sided BH at q=0.10 with untestable variants '
          'counted at p=1.' % (mt['variants_tried_total'], mt['templates'], mt['dynamics'], mt['ladders']), '',
          '- full-sample survivors (%d): %s' % (len(mt['bh_survivors_full_sample']),
                                                ', '.join(mt['bh_survivors_full_sample'][:40]) or 'none'),
          '- out-of-sample-only survivors (%d): %s' % (len(mt['bh_survivors_oos_only']),
                                                       ', '.join(mt['bh_survivors_oos_only'][:40]) or 'none'), '',
          '| smallest one-sided p (OOS only) | variant |', '|---:|---|']
    for p_, k in mt['smallest_p_oos'][:12]:
        L.append('| %.2g | %s |' % (p_, k))
    sb = a.get('selection_bias') or {}
    L += ['', '## Volume-floor selection bias, YES rate against price one day out (`selection_bias`)', '',
          'Before: union sample of the $10k universe. After: corrected design (complete events at market weights, '
          'plus a hash draw of incomplete events with every tradable member at event weights). Last two columns: '
          'the completed events alone, universe members only against all tradable members.', '',
          '| template | before n | before gap (pp) | after n | after gap (pp) | completed: universe only (pp) | '
          'completed: all members (pp) |', '|---|---:|---:|---:|---:|---:|---:|']
    for t in TEMPLATES + ['ALL_MULTI']:
        r = sb.get(t) or {}
        b, af = r.get('before_union_sample') or {}, r.get('after_corrected_design') or {}
        cu, ca = r.get('completed_events_universe_members_only') or {}, r.get('completed_events_all_tradable_members') or {}
        if not b and not af:
            continue
        L.append('| %s | %s | %s | %s | %s | %s (n %s) | %s (n %s) |' % (
            t, b.get('n'), _num(b.get('gap_pp'), 1), af.get('n'), _num(af.get('gap_pp'), 1), _num(cu.get('gap_pp'), 1),
            cu.get('n'), _num(ca.get('gap_pp'), 1), ca.get('n')))
    nmr = (a.get('near_misses') or {}).get('rows') or []
    L += ['', '## Near misses (`near_misses`)', '',
          'Positive in sample and out of sample; the data multiple is how many times the current out-of-sample '
          'span would be needed for t = 2, and for the first BH rank (z %s), if the effect held.' % (
              _num((a.get('near_misses') or {}).get('z_needed_for_bh_rank1'), 2)), '',
          '| variant | OOS n | OOS t | OOS excess | IS excess | x data for t=2 | x data for BH |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for r in nmr[:15]:
        L.append('| %s | %d | %s | %s | %s | %s | %s |' % (r['variant'], r['oos_n'], _num(r['oos_t']),
                                                        _pct(r['oos_ann_excess']), _pct(r['in_ann_excess']),
                                                        _num(r['data_multiple_for_t2'], 1),
                                                        _num(r['data_multiple_for_bh'], 1)))
    lf = out / 'ladder_fills.json'
    if lf.exists():
        f = json.loads(lf.read_text())['summary']
        L += ['', '## Historical ladder violations against actual fills (`ladder_fills.json`)', '',
              '%s entries of the %s family sampled; %s had taker trades on both legs within 30 minutes; of those, %s '
              'locked a profit after fees at the best observed prices (median edge %s, against %s at midpoints).' % (
                  f['read'], f['family'], f['with_trades_on_both_legs'], f['fill_edge_positive'],
                  _num(f['median_fill_edge'], 4), _num(f['median_mid_edge'], 4))]
    cf_ = a.get('confirmation')
    if cf_:
        L += ['', '## Pre-registered confirmation on fresh events (`confirmation`, `confirm_preregistration.json`)', '',
              '%d fresh complete events (%d tradable members) sharing no event with the union sample, 2026 only.' % (
                  cf_['events'], cf_['members_with_series']), '',
              '| hypothesis | trades | events | win rate | mean price | mean return | days | HAC t | BH adj p | late keeps | '
              '$/yr | confirmed |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
        for h, r in cf_['results'].items():
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                h, r.get('n'), r.get('events'), _pct(r.get('win_rate')), _num(r.get('mean_price'), 3),
                _pct(r.get('mean_return'), 2), _num(r.get('mean_days'), 2), _num(r.get('hac_t')),
                _num(r.get('bh_adjusted_p'), 3), _pct((r.get('late_entry') or {}).get('share_of_edge_kept'), 0),
                _usd((r.get('capacity') or {}).get('usd_per_year')), r.get('confirmed')))
    L += ['', '## Go checks (`go`)', '', '| family | chosen | IS+ | OOS t>=2 | family BH | global BH | excess>0 | '
          '$/yr>0 | go |', '|---|---|---|---|---|---|---|---|---|']
    for gg in a['go']:
        ck = gg['checks']
        extra = ', '.join('%s=%s' % (k, v) for k, v in ck.items() if k in ('fresh_event_confirmation',
                                                                         'live_executable_value_positive',
                                                                         'historical_fills_executable'))
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | **%s**%s |' % (
            gg['family'], gg['chosen'], ck['in_sample_positive'], ck['oos_t_ge_2'], ck['in_family_bh_positive'],
            ck['global_bh_positive'], ck['excess_over_ssr_positive'], ck['usd_per_year_positive'], gg['go'],
            (' (' + extra + ')') if extra else ''))
    ds = a['inventory'].get('design') or {}
    L += ['', 'Design (`inventory.design`): %s union-sample markets; %s in complete events or standalone (part A); '
          '%s incomplete events, %s completed by a hash draw (q = %s) with %s tradable members, %s of them under $10k '
          '(part B).' % (ds.get('union_markets'), ds.get('complete_or_standalone'), ds.get('incomplete_events'),
                         ds.get('fix_events'), _num(ds.get('q_fix'), 4), ds.get('design_B'),
                         ds.get('design_B_not_in_universe'))]
    L += ['', '## Calibration of YES by template, horizon and band (`templates.calibration`)', '',
          'Weighted YES resolution rate against the mean YES midpoint; rows with at least 40 markets.', '',
          '| template | horizon | YES band | n | mean YES mid | YES rate | 95% CI | edge (pp) |',
          '|---|---|---|---:|---:|---:|---|---:|']
    for r in a['templates']['calibration']:
        if r['n'] >= 40 and r['tpl'] in ('drama_by_date', 'mention', 'tweet_count', 'exact_score', 'approval',
                                          'release_by', 'drama_on_date', 'count_bucket', 'weather_temp'):
            L.append('| %s | %s | %s | %d | %s | %s | %s–%s | %+.1f |' % (
                r['tpl'], r['h'], r['band'], r['n'], _num(r['mean_yes_price'], 3), _num(r['yes_rate'], 3),
                _num(r['ci_lo'], 3), _num(r['ci_hi'], 3), r['edge_pp']))
    lad = a['ladders']
    L += ['', '## Ladders: history at midpoints (`ladders.history_stats`)', '',
          '| family | ladders in universe | read | grid points | violated | >1c | >2c | >5c |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for fam, st in lad['history_stats'].items():
        n = st.get('points', 0) or 1
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            fam, st['groups_in_universe'], st.get('ladders', 0), st.get('points', 0),
            _pct(st.get('points_violated', 0) / n), _pct(st.get('points_violated_1c', 0) / n),
            _pct(st.get('points_violated_2c', 0) / n), _pct(st.get('points_violated_5c', 0) / n)))
    lp = lad['protocol']
    if lp.get('selection'):
        L += ['', 'Violation trade protocol (`ladders.protocol`): chosen %s, in-sample excess %s, out-of-sample excess %s '
              'on %s trades, t %s; late entry keeps %s.' % (
                  lp['chosen'], _pct(lp['chosen_parts']['in'].get('ann_excess')),
                  _pct(lp['chosen_parts']['oos'].get('ann_excess')), lp['chosen_parts']['oos'].get('n'),
                  _num(lp['selection']['oos_t']), _pct((lp.get('late_entry') or {}).get('share_of_edge_kept'), 0))]
    lv = lad['live']
    L += ['', '## Ladders: live executable violations (`ladders.live`)', '',
          '| snapshot | violations | profit | capital | beating SSR | profit beating SSR | families |',
          '|---|---:|---:|---:|---:|---:|---|']
    for r in lv['per_snapshot']:
        L.append('| %s | %d | %s | %s | %d | %s | %s |' % (r['at'], r['violations'], _usd(r['profit_usd']),
                                                          _usd(r['capital_usd']), r['beating_ssr'],
                                                          _usd(r['profit_beating_ssr_usd']),
                                                          json.dumps(r['by_family'])))
    L += ['', 'Persistence to the next snapshot: %s. Value per day (estimate): %s.' % (
        _pct(lv['persistence_next_snapshot']), _usd(lv['value_per_day_usd_estimate'])), '']
    d = a['dynamics']
    if d.get('selection'):
        L += ['## Dynamics (`dynamics`)', '',
              'Chosen %s: in-sample excess %s, out-of-sample excess %s on %s trades, t %s, rank %d/%d; late entry '
              'keeps %s.' % (d['chosen'], _pct(d['chosen_parts']['in'].get('ann_excess')),
                             _pct(d['chosen_parts']['oos'].get('ann_excess')), d['chosen_parts']['oos'].get('n'),
                             _num(d['selection']['oos_t']), d['selection']['oos_rank'], d['selection']['n_variants'],
                             _pct((d.get('late_entry') or {}).get('share_of_edge_kept'), 0)), '',
              '| variant | IS n | IS mean ret | OOS n | OOS mean ret | OOS excess |', '|---|---:|---:|---:|---:|---:|']
        rows = sorted(d['variant_summary'].items(), key=lambda kv: -(kv[1]['oos_mean_ret'] or -9))
        for k, v in rows[:12]:
            L.append('| %s | %s | %s | %s | %s | %s |' % (k, v['in_n'], _pct(v['in_mean_ret'], 2), v['oos_n'],
                                                         _pct(v['oos_mean_ret'], 2), _pct(v['oos_ann_excess'])))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    entries = []
    for gg in a['go']:
        if not gg['go']:
            continue
        fam = gg['family']
        entries.append({
            'id': 'pm-structure-' + fam.replace(':', '-').replace('_', '-'),
            'name': 'Polymarket structural rule %s (%s)' % (gg['chosen'], fam),
            'kind': 'prediction-market', 'status': 'proposed',
            'thesis': 'Chosen before 2026-01-01 and tested once after it by backtest.choose_then_test; out-of-sample '
                      'excess over SSR %.1f%% a year on %s trades (HAC t %.2f), surviving one-sided BH across %d '
                      'variants; late entry keeps %s of the edge.' % (
                          100 * (gg['oos_ann_excess'] or 0), gg['oos_n'], gg['oos_t'] or 0,
                          a['multiple_testing']['variants_tried_total'],
                          _pct(gg.get('late_share'), 0)),
            'mechanism': 'see research/2026-10-14/pm_structure_scan/analysis.json go and templates.families',
            'legs': ['taker entry at the ask (midpoint plus the live half-spread) plus the category fee; hold as the '
                     'rule states'],
            'capacity_usd': None, 'capital_days': None,
            'kill_criteria': ['out-of-sample excess over SSR below zero over a trailing quarter',
                              'live half-spread in the traded band above the backtest charge for a month'],
            'quotes': [{'at': a['generated'], 'source': 'history', 'window': 'research/2026-10-14/pm_structure_scan',
                        'net_apr': gg['oos_ann_excess'], 'usd': gg['usd_per_year'], 'go': True, 'present': False,
                        'note': 'capacity from median live depth at the best ask and 10% of average daily volume'}],
            'risks': ['multiple testing: %d variants tried' % a['multiple_testing']['variants_tried_total'],
                      'the $10k volume floor of the stored universe selects winners inside events; corrected by '
                      'event-level design, residual selection on standalone markets remains',
                      'midpoints are not fills; the charged half-spread is today\'s median, not the historical one'],
            'evidence': ['research/2026-10-14/pm_structure_scan/analysis.json', 'research/2026-10-14/pm_structure_scan/tables.md']})
    P.write_json(out / 'book_entries.json', entries)
    print('book entries', len(entries))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('inventory')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    s = sub.add_parser('collect')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    s.add_argument('--what', choices=['extra', 'ladders', 'ladders_x', 'events', 'complete', 'confirm'],
                   required=True)
    s.add_argument('--max-events', type=int, default=360)
    s.add_argument('--interval', type=float, default=0.25)
    s.add_argument('--workers', type=int, default=4)
    s.add_argument('--shards', type=int, default=1)
    s.add_argument('--shard', type=int, default=0)
    s = sub.add_parser('live')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    s.add_argument('--interval', type=float, default=0.25)
    s.add_argument('--max-pages', type=int, default=2500)
    s.add_argument('--per-template', type=int, default=80)
    s.add_argument('--min-volume', type=float, default=1000.0)
    s = sub.add_parser('analyze')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    s.add_argument('--workers', type=int, default=8)
    s = sub.add_parser('ladder_fills')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    s.add_argument('--n', type=int, default=120)
    s.add_argument('--interval', type=float, default=0.25)
    s = sub.add_parser('confirm')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    s = sub.add_parser('render')
    s.add_argument('--out', default='research/2026-10-14/pm_structure_scan')
    args = ap.parse_args()
    return {'inventory': cmd_inventory, 'collect': cmd_collect, 'live': cmd_live, 'analyze': cmd_analyze,
            'ladder_fills': cmd_ladder_fills, 'confirm': cmd_confirm, 'render': cmd_render}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
