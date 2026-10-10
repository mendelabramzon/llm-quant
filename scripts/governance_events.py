#!/usr/bin/env python3
"""Governance events read by an LLM: do token-holder-value proposals move the token over days, tradably?

Why. Every other study in this repo reads a ledger or a market. This one reads text. A DAO proposal to switch on a fee,
buy back or burn the token, share revenue or cut emissions is, on paper, a change to the cash flow or the supply of the
token, and a proposal to sell treasury tokens, raise emissions or pay a large program in the token is the opposite.
Whether such proposals move the price over the days a patient trader can act in (the vote runs for days, the tally is
public while it runs, the outcome is known at the end) is an old question with a new tool: the qualitative step —
deciding which proposals are about holder value at all — can be done by an LLM reading each one, systematically and
auditably, and the quantitative step by deterministic code that never sees the labels change. This is the loop's first
qual->quant study built that way, so the labeling is part of the result: how often a blind re-read agrees, and how much
of it a keyword screen alone would have gotten.

What.
  * Events: Snapshot proposals (hub.snapshot.org/graphql, no key) from ~70 spaces whose token has a Binance USDⓈ-M
    perpetual (SPACES below; each id verified by its voting strategy's token and its proposals' content). Snapshot
    dates are public: created (published), start, end. Many binding votes later happen on chain (Governor/Tally); the
    Snapshot dates are still dates a trader could watch.
  * Labels: a keyword screen (KEYWORDS_ANY anywhere in the title or first 4,000 characters of the body; KEYWORDS_TITLE
    only in the title) picks candidates, plus a random control sample of proposals the screen missed. Every candidate
    is labeled VALUE_UP / VALUE_DOWN / NEUTRAL with a surprise flag and a confidence by an LLM reading the title and
    the first 1,500 characters, against criteria.md, written before any label and frozen before any price
    (`label-freeze` stamps the time and a sha256 into manifest.json; `analyze` refuses to run on a changed file).
  * Prices: Binance USDⓈ-M 4h klines and funding history per token (cached gzip), BTC as the hedge and an equal-weight
    basket of the universe's other tokens as the second benchmark.
  * Trade: long VALUE_UP / short VALUE_DOWN against the opposite BTC leg, entered at realistic non-latency times (vote
    start + 1 day, or vote end + 1 hour), at the first 4h close at or after the decision time; P&L with funding (positive
    rate: longs pay), taker fees and the half-spread at size from live books; benchmark = the Sky savings rate on the
    notional for the days held.
  * Protocol: variants (window x side x outcome filter) chosen on events before the cutoff by the excess over a placebo
    (the same token, the same window shape, 15-30 days away from any other labeled event), tested once after it;
    Benjamini-Hochberg across variants; t by event week (governance votes cluster on calendar weeks).

How (the order is the protocol: labels are frozen before a single price path is computed):
    python3 scripts/governance_events.py collect      --out research/2026-10-10/governance_events
    python3 scripts/governance_events.py screen       --out research/2026-10-10/governance_events
    python3 scripts/governance_events.py label-export --out research/2026-10-10/governance_events
      ... the LLM labels label_batches/batch_*.jsonl against criteria.md into label_batches/out_*.jsonl ...
    python3 scripts/governance_events.py label-freeze --out research/2026-10-10/governance_events
      ... a blind re-label of label_batches/spot_check.jsonl into label_batches/spot_out.jsonl ...
    python3 scripts/governance_events.py label-agree  --out research/2026-10-10/governance_events
    python3 scripts/governance_events.py prices       --out research/2026-10-10/governance_events
    python3 scripts/governance_events.py books        --out research/2026-10-10/governance_events
    python3 scripts/governance_events.py analyze      --out research/2026-10-10/governance_events
    python3 scripts/governance_events.py render       --out research/2026-10-10/governance_events
"""
import argparse
import bisect
import datetime as dt
import gzip
import hashlib
import json
import math
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
BAR_MS = 4 * HOUR_MS
SNAPSHOT_URL = 'https://hub.snapshot.org/graphql'
BN_FAPI = 'https://fapi.binance.com'
UA = 'llm-quant-research/1.0'
SSR = 0.038                    # Sky savings rate, the benchmark on the capital a trade ties up
TAKER_BPS = 5.0                # Binance USDⓈ-M taker fee per side (VIP0 with BNB off is 5bp)
BTC_HALF_SPREAD_BPS = 0.5      # BTCUSDT perp at $100k: the touch is a cent wide; impact well under a basis point
BODY_KEEP = 4000               # characters of each proposal body stored (the screen reads these)
BODY_LABEL = 1500              # characters the labeler reads
LABELS = ('VALUE_UP', 'VALUE_DOWN', 'NEUTRAL')
SEED = 20261010
MIN_VOTES = 3                  # fewer votes than this: a test or spam (council spaces such as Synthetix vote with ~8)
# Spaces where anyone can post: PancakeSwap's carries thousands of phishing and chat proposals beside the team's.
# There a proposal counts only if its author posted at least 5 proposals in the space with a median of at least 300
# votes (five addresses: the team's "Proposal to/for ..." series). Fixed from vote counts before any label or price.
OPEN_SPACES = {'cakevote.eth': {'min_proposals': 5, 'min_median_votes': 300}}

# Snapshot space -> token. Every id was checked on 2026-10-10: the space's voting strategy names the token (or its
# staked/vote-escrowed wrapper), the space is Snapshot-verified unless noted, and its proposals are about that token's
# protocol. Spaces whose symbol collides with an unrelated Binance listing were dropped: timelessfi.eth (veLIT vs
# Litentry LIT), banklessvault.eth (BANK vs Lorenzo BANK), hyperlockfi.eth (HYPER vs Hyperlane), ffdao.eth (Forefront
# FF vs Falcon FF), zora.eth (Zorb NFT DAO), gasdao.eth, mocana.eth (NFT-weighted Moca DAO), governance.qredo.eth,
# monetadao.eth, zechubdao.eth, thestandardio.eth, xdaistake.eth, blockzerolabs.eth. Two were dropped after reading
# their proposals: snapshot.movedao.eth (2022-24 "MoveDAO", before Movement's MOVE token existed) and
# celernetwork.eth (unverified, community questions only). Tokens without a Binance USDⓈ-M perp were left out (GNO,
# OHM, AURA, SWISE, HOP, POOL, INDEX, MNT; Pendle has no Snapshot governance).
SPACES = {
    'uniswapgovernance.eth': 'UNI', 'aavedao.eth': 'AAVE', 'arbitrumfoundation.eth': 'ARB', 'opcollective.eth': 'OP',
    'citizenshouse.eth': 'OP', 'lido-snapshot.eth': 'LDO', 'ens.eth': 'ENS', 'cvx.eth': 'CVX', 'gmx.eth': 'GMX',
    'balancer.eth': 'BAL', 'sushigov.eth': 'SUSHI', '1inch.eth': '1INCH', 'safe.eth': 'SAFE', 'starknet.eth': 'STRK',
    'apecoin.eth': 'APE', 'gitcoindao.eth': 'GTC', 'frax.eth': 'FXS', 'curve.eth': 'CRV', 'venus-xvs.eth': 'XVS',
    'stgdao.eth': 'STG', 'origingov.eth': 'OGN', 'morpho.eth': 'MORPHO', 'mainnet.ssvnetwork.eth': 'SSV',
    'badgerdao.eth': 'BADGER', 'threshold.eth': 'T', 'diadao.eth': 'DIA', 'sparkfi.eth': 'SPK',
    'abracadabrabymerlinthemagician.eth': 'SPELL', 'cow.eth': 'COW', 'acrossprotocol.eth': 'ACX', 'veyfi.eth': 'YFI',
    'ybaby.eth': 'YFI', 'quickvote.eth': 'QUICK', 'truefigov.eth': 'TRU', 'dydxgov.eth': 'DYDX', 'eulerdao.eth': 'EUL',
    'radiantcapital.eth': 'RDNT', 'synapseprotocol.eth': 'SYN', 'people-dao.eth': 'PEOPLE',
    'alpacafinance.eth': 'ALPACA', 'vote-perp.eth': 'PERP', 'comp-vote.eth': 'COMP', 'rbn.eth': 'AEVO',
    'metislayer2.eth': 'METIS', 'aavegotchi.eth': 'GHST', 'bancornetwork.eth': 'BNT', 'chaingptai.eth': 'CGPT',
    'superraredao.eth': 'RARE', 'promdao.eth': 'PROM', 'bioxyz.eth': 'BIO', 'barnbridge.eth': 'BOND',
    'gov.radworks.eth': 'RAD', 'hashflowdao.eth': 'HFT', 'joegovernance.eth': 'JOE', '0xgov.eth': 'ZRX',
    'listavote.eth': 'LISTA', 'floki-inu.eth': 'FLOKI', 'dao.spaceid.eth': 'ID', 'uma.eth': 'UMA',
    'harmony-mainnet.eth': 'ONE', 'trustwallet': 'TWT', 'ilv.eth': 'ILV', 'opencampusdao.eth': 'EDU', 'stp.eth': 'AWE',
    'cartesi.eth': 'CTSI', 'masknetwork.eth': 'MASK', 'treehousefi.eth': 'TREE', 'loopringdao.eth': 'LRC',
    'worldlibertyfinancial.com': 'WLFI', 'ethenagovernance.eth': 'ENA', 'vote.turbocouncil.eth': 'TURBO',
    'agld-dao.eth': 'AGLD', 'mavxyz.eth': 'MAV', 'dexe.network': 'DEXE', 'immutablex.eth': 'IMX', 'skale.eth': 'SKL',
    'walletconnect.eth': 'WCT', 'graphprotocol.eth': 'GRT', 'wormholegovernance.eth': 'W', 'yieldguild.eth': 'YGG',
    'cakevote.eth': 'CAKE', 'snapshot.dcl.eth': 'MANA', 'snxgov.eth': 'SNX', 'treasuregaming.eth': 'MAGIC',
    'sandboxdao.eth': 'SAND', 'rocketpool-dao.eth': 'RPL', 'etherfi-dao.eth': 'ETHFI', 'renzogovernance.eth': 'REZ',
    'iotex.eth': 'IOTX', 'g-dao.eth': 'G', 'mantra-dao.eth': 'OM', 'chaingov.eth': 'XCN', 'ampleforthorg.eth': 'FORTH', 'officialoceandao.eth': 'OCEAN',
    'airdaofoundation.eth': 'AMB', 'moonbeam-foundation.eth': 'GLMR', 'biswap-org.eth': 'BSW',
}

# The keyword screen, fixed before any proposal was read. KEYWORDS_ANY match the title or the first BODY_KEEP
# characters of the body; KEYWORDS_TITLE are too common in bodies (every proposal mentions the treasury) and match the
# title only. Patterns are case-insensitive regular expressions.
KEYWORDS_ANY = [
    r'fee[ -]?switch', r'fee[ -]shar', r'revenue[ -]shar', r'profit[ -]shar', r'buy[ -]?backs?\b', r'repurchas',
    r'\bburn(s|ed|ing)?\b', r'dividend', r'staking rewards?', r'\bemissions?\b', r'\binflation', r'tokenomics',
    r'protocol fees?', r'fee tier', r'\brebates?\b', r'token sale', r'sell(ing)? .{0,40}tokens', r'\botc\b',
    r'grant program', r'value accrual', r'real yield', r'max(imum)? supply', r'\bmint(ing)? (new )?tokens',
    r'treasury diversification', r'diversif\w* .{0,40}treasury', r'treasury .{0,40}diversif',
]
# Screen v2 (2026-10-10, before any label): v1 also matched 'supply cap', 'diversif', 'vesting' and 'unlock' anywhere in
# the body. Their single-term hits were Aave per-asset supply caps (risk parameters), generic "diversify", and 290
# Decentraland grant requests whose boilerplate mentions a vesting contract; 'vesting' and 'unlock' now count in titles.
KEYWORDS_TITLE = [r'treasury', r'\bgrants?\b', r'incentive', r'revenue', r'distribution', r'\brewards?\b',
                  r'\bfees?\b', r'\bstaking\b', r'\bsupply\b', r'allocation', r'liquidity mining', r'\bvesting\b',
                  r'\bunlock']

# Routine operational votes that criteria.md already calls NEUTRAL (gauge, farm, pool, market and collateral additions,
# listings, risk parameters, caps). A keyword hit with such a title is not a candidate unless its title also carries a
# value term; these proposals stay in the pool the random controls are drawn from, so the controls measure the cost.
ROUTINE_TITLE = re.compile(
    r'\bgauges?\b|syrup pool|\bfarms?\b|\bonboard|\bwhitelist|risk param|parameter|\b(supply|borrow) caps?\b|'
    r'\b(add|enable|create|deploy|launch|kill|remove|disable|deprecate|list|offboard)\b.{0,60}\b(pools?|markets?|vaults?|'
    r'pairs?|collateral|strateg(y|ies)|assets?|reserves?|chains?|networks?)\b', re.I)
VALUE_TITLE = re.compile(r'emission|inflation|\bburn|buy ?back|fee switch|revenue|tokenomics|treasury|token sale|\bsell|'
                         r'unlock|vesting|staking reward|dividend|distribut|supply\b(?! cap)|\bmint', re.I)


def routine(title):
    """True for a routine operational title without a value term (criteria.md: NEUTRAL by definition)."""
    t = title or ''
    return bool(ROUTINE_TITLE.search(t)) and not VALUE_TITLE.search(t)


# The keyword-only classifier the LLM is compared against: what a screen would call each proposal with no reading.
# Fixed with the screen. UP terms are the cash-flow and supply-cut vocabulary; DOWN the dilution vocabulary.
KW_UP = [r'fee[ -]?switch', r'fee[ -]shar', r'revenue[ -]shar', r'profit[ -]shar', r'buy[ -]?backs?\b', r'repurchas',
         r'\bburn(s|ed|ing)?\b', r'dividend', r'value accrual', r'real yield', r'\bsupply cap', r'reduce .{0,20}emissions?',
         r'emissions? (cut|reduction)', r'cut .{0,20}emissions?']
KW_DOWN = [r'token sale', r'sell(ing)? .{0,40}tokens', r'\botc\b', r'grant program', r'incentive program',
           r'liquidity mining', r'\bmint(ing)? (new )?tokens', r'increase .{0,20}emissions?', r'treasury diversification',
           r'\bgrants?\b']


def now_iso():
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat()


def utc_iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).isoformat()


def write_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def read_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else default


def write_gz(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, 'wt') as f:
        json.dump(obj, f)


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def read_jsonl(p):
    p = Path(p)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def write_jsonl(p, rows):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def update_manifest(out, **kw):
    man = read_json(Path(out) / 'manifest.json', {}) or {}
    man.update(kw)
    write_json(Path(out) / 'manifest.json', man)
    return man


# ------------------------------------------------------------------------------------------------ HTTP

class Http:
    """Paced JSON client: one request per `interval` seconds, backs off on 429/418/5xx."""

    def __init__(self, interval=1.1, timeout=90, retries=6):
        self.interval, self.timeout, self.retries = interval, timeout, retries
        self.next_at = 0.0
        self.n = self.errors = self.throttled = 0

    def _wait(self):
        d = self.next_at - time.monotonic()
        if d > 0:
            time.sleep(d)
        self.next_at = time.monotonic() + self.interval

    def request(self, url, params=None, body=None):
        if params:
            url = url + '?' + urllib.parse.urlencode(params)
        last = None
        for attempt in range(self.retries):
            self._wait()
            self.n += 1
            try:
                data = json.dumps(body).encode() if body is not None else None
                req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, 'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                last = 'HTTP %s' % e.code
                self.errors += 1
                if e.code in (429, 418):
                    self.throttled += 1
                    self.next_at = time.monotonic() + min(120.0, 15.0 * (attempt + 1))
                    continue
                if e.code in (500, 502, 503, 504):
                    time.sleep(min(20.0, 1.0 * 2 ** attempt))
                    continue
                try:
                    return {'_http_error': e.code, '_body': e.read().decode()[:300]}
                except Exception:  # noqa: BLE001
                    return {'_http_error': e.code}
            except Exception as e:  # noqa: BLE001 - network errors of any kind are retried
                last = repr(e)[:160]
                self.errors += 1
                time.sleep(min(20.0, 1.0 * 2 ** attempt))
        raise RuntimeError('retry limit %s: %s' % (url[:100], last))

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


# ------------------------------------------------------------------------------------------------ Snapshot

PROPOSAL_FIELDS = ('id title body choices start end snapshot state author created type scores scores_total '
                   'scores_state votes quorum discussion link flagged space { id }')


def gql(http, query, variables=None):
    d = http.request(SNAPSHOT_URL, body={'query': query, 'variables': variables or {}})
    if not isinstance(d, dict) or 'errors' in d or 'data' not in d:
        raise RuntimeError('graphql: %s' % str(d)[:300])
    return d['data']


def fetch_space_proposals(http, space, page=100):
    """Every proposal of `space`, newest first, paged on `created` (ties at a page boundary are re-read and deduped)."""
    q = ('query($space: String!, $lte: Int!, $first: Int!) { proposals(first: $first, '
         'where: {space: $space, created_lte: $lte}, orderBy: "created", orderDirection: desc) { %s } }' % PROPOSAL_FIELDS)
    seen, rows, lte = set(), [], 2 ** 31 - 1
    while True:
        batch = gql(http, q, {'space': space, 'lte': lte, 'first': page})['proposals'] or []
        new = [p for p in batch if p['id'] not in seen]
        for p in new:
            seen.add(p['id'])
            body = p.get('body') or ''
            p['body_len'] = len(body)
            p['body'] = body[:BODY_KEEP]
            rows.append(p)
        if len(batch) < page or not new:
            break
        lte = min(p['created'] for p in batch)
    return rows


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw' / 'snapshot'
    raw.mkdir(parents=True, exist_ok=True)
    http = Http(interval=args.interval)
    t0 = time.time()
    spaces = sorted(SPACES)
    meta = gql(http, '{ spaces(first: 200, where: {id_in: %s}) { id name symbol network proposalsCount followersCount '
                     'verified strategies { name network params } } }' % json.dumps(spaces))['spaces']
    write_json(out / 'raw' / 'snapshot_spaces.json', meta)
    counts, failures = {}, {}
    for s in spaces:
        fn = raw / (s.replace('/', '_') + '.json.gz')
        if fn.exists() and not args.force:
            counts[s] = len(read_gz(fn))
            continue
        try:
            rows = fetch_space_proposals(http, s)
        except RuntimeError as e:
            failures[s] = str(e)[:200]
            print('FAIL', s, e, flush=True)
            continue
        write_gz(fn, rows)
        counts[s] = len(rows)
        print('%-40s %5d proposals' % (s, len(rows)), flush=True)
    update_manifest(out, snapshot={'collected_at': now_iso(), 'endpoint': SNAPSHOT_URL, 'spaces': len(spaces),
                                   'proposals': sum(counts.values()), 'per_space': counts, 'failures': failures,
                                   'body_chars_kept': BODY_KEEP, 'seconds': round(time.time() - t0, 1),
                                   'http': http.stats()})
    print(json.dumps({'spaces': len(spaces), 'proposals': sum(counts.values()), 'failures': failures}))
    return 0


def load_proposals(out):
    rows = []
    for fn in sorted((Path(out) / 'raw' / 'snapshot').glob('*.json.gz')):
        for p in read_gz(fn):
            sp = (p.get('space') or {}).get('id')
            if sp in SPACES:
                p['space_id'] = sp
                p['token'] = SPACES[sp]
                rows.append(p)
    return rows


# ------------------------------------------------------------------------------------------------ screen

_ANY = [re.compile(k, re.I) for k in KEYWORDS_ANY]
_TITLE = [re.compile(k, re.I) for k in KEYWORDS_TITLE]
_KW_UP = [re.compile(k, re.I) for k in KW_UP]
_KW_DOWN = [re.compile(k, re.I) for k in KW_DOWN]


def screen_terms(title, body):
    """The keyword-screen terms a proposal matches (patterns, in list order); empty = not a candidate."""
    text = (title or '') + '\n' + (body or '')[:BODY_KEEP]
    hits = [k for k, rx in zip(KEYWORDS_ANY, _ANY) if rx.search(text)]
    hits += ['title:' + k for k, rx in zip(KEYWORDS_TITLE, _TITLE) if rx.search(title or '')]
    return hits


def keyword_label(title, body):
    """What the keyword screen alone would call a proposal: VALUE_UP if it matches only the cash-flow/supply-cut
    vocabulary, VALUE_DOWN if only the dilution vocabulary, NEUTRAL if neither or both."""
    text = (title or '') + '\n' + (body or '')[:BODY_LABEL]
    up = any(rx.search(text) for rx in _KW_UP)
    down = any(rx.search(text) for rx in _KW_DOWN)
    if up and not down:
        return 'VALUE_UP'
    if down and not up:
        return 'VALUE_DOWN'
    return 'NEUTRAL'


SIGNAL_RX = re.compile(r'temp(erature)?[ -]?check|\[?arfc\]?|\brfc\b|signal(ing|ling)?\b|\bpoll\b|sentiment|snapshot vote '
                       r'to gauge|\bidea\b|discussion', re.I)


def stage_hint(title):
    """'signal' when the title marks a temperature check, request for comment or poll; '' otherwise (unknown)."""
    return 'signal' if SIGNAL_RX.search(title or '') else ''


def traded_span(klines):
    """(first, last) close time of the bars that traded (quote volume > 0), or None."""
    t = [int(r[0]) + BAR_MS for r in klines if len(r) < 6 or r[5] > 0]
    return (min(t), max(t)) if t else None


def priced_span(out):
    """{token: (first traded bar close ms, last traded bar close ms)} from the cached klines — only bar times and
    volumes are read, never a return — or None before `prices` has run."""
    man = read_json(Path(out) / 'manifest.json', {}) or {}
    toks = (man.get('prices') or {}).get('tokens')
    if not toks:
        return None
    res = {}
    for t, m in toks.items():
        kp = Path(out) / 'raw' / 'binance' / 'klines_4h' / (m['symbol'] + '.json.gz')
        sp = traded_span(read_gz(kp)) if kp.exists() else None
        if sp:
            res[t] = sp
    return res


def core_authors(props):
    """{open space: authors who pass OPEN_SPACES' rule}."""
    res = {}
    for sp, rule in OPEN_SPACES.items():
        by = {}
        for p in props:
            if p['space_id'] == sp:
                by.setdefault(p.get('author'), []).append(p.get('votes') or 0)
        res[sp] = {a for a, v in by.items() if len(v) >= rule['min_proposals'] and statistics.median(v) >= rule['min_median_votes']}
    return res


def cmd_screen(args):
    out = Path(args.out)
    props = load_proposals(out)
    lo = int(dt.datetime.fromisoformat(args.since).replace(tzinfo=UTC).timestamp())
    hi = int(dt.datetime.fromisoformat(args.until).replace(tzinfo=UTC).timestamp())
    kept, dropped = [], {'flagged': 0, 'outside_dates': 0, 'not_closed': 0, 'few_votes': 0, 'open_space_author': 0}
    core = core_authors(props)
    for p in props:
        if p.get('flagged'):
            dropped['flagged'] += 1
            continue
        if (p.get('votes') or 0) < MIN_VOTES:
            dropped['few_votes'] += 1
            continue
        if p['space_id'] in OPEN_SPACES and p.get('author') not in core.get(p['space_id'], set()):
            dropped['open_space_author'] += 1
            continue
        if not (lo <= int(p['created']) < hi):
            dropped['outside_dates'] += 1
            continue
        if p.get('state') != 'closed':
            dropped['not_closed'] += 1
            continue
        kept.append(p)
    # Only proposals a price can be put on need a label: the token's Binance perp must have closes from 8 days before
    # publication to 8 days after the vote ends. Only the first and last bar times are read here, never a return.
    span = priced_span(out)
    if span:
        pk = []
        for p in kept:
            sp = span.get(p['token'])
            if sp and sp[0] + 8 * DAY_MS <= int(p['created']) * 1000 and int(p['end']) * 1000 + 8 * DAY_MS <= sp[1]:
                pk.append(p)
            else:
                dropped['unpriceable'] = dropped.get('unpriceable', 0) + 1
        kept = pk
    hits, misses, n_routine = [], [], 0
    for p in kept:
        terms = screen_terms(p.get('title'), p.get('body'))
        if terms and routine(p.get('title')):
            n_routine += 1
            terms = []
        (hits if terms else misses).append((p, terms))
    rng = random.Random(SEED)
    n_ctrl = min(args.controls, len(misses))
    ctrl = rng.sample(misses, n_ctrl)
    rows = []
    for (p, terms), is_ctrl in [(x, False) for x in hits] + [(x, True) for x in ctrl]:
        rows.append({'id': p['id'], 'space': p['space_id'], 'token': p['token'], 'created': int(p['created']),
                     'start': int(p['start']), 'end': int(p['end']), 'state': p.get('state'), 'title': p.get('title'),
                     'body_head': (p.get('body') or '')[:BODY_LABEL], 'body_len': p.get('body_len'),
                     'keywords': terms, 'control': is_ctrl, 'choices': p.get('choices'), 'scores': p.get('scores'),
                     'scores_total': p.get('scores_total'), 'votes': p.get('votes'), 'quorum': p.get('quorum'),
                     'type': p.get('type'), 'author': p.get('author'), 'discussion': p.get('discussion'),
                     'stage_hint': stage_hint(p.get('title')),
                     'keyword_label': keyword_label(p.get('title'), p.get('body'))})
    rows.sort(key=lambda r: (r['token'], r['created'], r['id']))
    write_jsonl(out / 'candidates.jsonl', rows)
    per_token = {}
    for r in rows:
        per_token.setdefault(r['token'], [0, 0])[1 if r['control'] else 0] += 1
    update_manifest(out, screen={'at': now_iso(), 'since': args.since, 'until': args.until, 'proposals_loaded': len(props),
                                 'kept_closed_in_dates': len(kept), 'dropped': dropped, 'keyword_hits': len(hits),
                                 'keyword_misses': len(misses), 'controls': n_ctrl, 'control_seed': SEED,
                                 'min_votes': MIN_VOTES, 'open_spaces': OPEN_SPACES, 'routine_excluded': n_routine,
                                 'routine_title': ROUTINE_TITLE.pattern, 'value_title': VALUE_TITLE.pattern,
                                 'open_space_authors': {k: sorted(v) for k, v in core.items()},
                                 'keywords_any': KEYWORDS_ANY, 'keywords_title': KEYWORDS_TITLE,
                                 'per_token_hits_controls': per_token})
    print(json.dumps({'loaded': len(props), 'kept': len(kept), 'hits': len(hits), 'misses': len(misses),
                      'controls': n_ctrl, 'dropped': dropped}))
    return 0


# ------------------------------------------------------------------------------------------------ labeling

def label_packet(r):
    """What the labeler sees: no prices, no keyword hits, no control flag, no outcome — only what a reader of the
    proposal would see on the day it was published."""
    return {'id': r['id'], 'token': r['token'], 'space': r['space'], 'date': utc_iso(r['created'] * 1000)[:10],
            'title': r['title'], 'choices': r.get('choices'), 'text': r['body_head']}


def packets_md(packets, name):
    """The same packets as readable text: one section per proposal, the body as written."""
    L = ['# Labeling packets — %s (%d proposals). Label each against criteria.md.' % (name, len(packets)), '']
    for k, p in enumerate(packets):
        L += ['=' * 100, '[%d] id=%s  token=%s  space=%s  date=%s' % (k, p['id'], p['token'], p['space'], p['date']),
              'TITLE: %s' % (p['title'] or '').strip(), 'CHOICES: %s' % ' | '.join(str(c) for c in (p['choices'] or [])),
              'TEXT (first %d characters):' % BODY_LABEL, (p['text'] or '').strip(), '']
    return '\n'.join(L) + '\n'


def cmd_label_export(args):
    out = Path(args.out)
    rows = read_jsonl(out / 'candidates.jsonl')
    d = out / 'label_batches'
    d.mkdir(parents=True, exist_ok=True)
    # batches keep a token's proposals together and in time order, so a labeler can tell a re-vote from a first
    # appearance; a token never straddles two batches unless it alone exceeds the batch size
    batches, cur = [], []
    for tok in sorted({r['token'] for r in rows}):
        grp = [r for r in rows if r['token'] == tok]
        if cur and len(cur) + len(grp) > args.batch_size:
            batches.append(cur)
            cur = []
        while len(grp) > args.batch_size:
            batches.append(grp[:args.batch_size])
            grp = grp[args.batch_size:]
        cur += grp
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches):
        write_jsonl(d / ('batch_%02d.jsonl' % i), [label_packet(r) for r in b])
        (d / ('batch_%02d.md' % i)).write_text(packets_md([label_packet(r) for r in b], 'batch %02d' % i))
    rng = random.Random(SEED + 1)
    spot = rng.sample(rows, max(1, int(round(args.spot_frac * len(rows)))))
    rng.shuffle(spot)
    write_jsonl(d / 'spot_check.jsonl', [label_packet(r) for r in spot])
    half = (len(spot) + 1) // 2
    for part, rows_ in (('a', spot[:half]), ('b', spot[half:])):
        write_jsonl(d / ('spot_check_%s.jsonl' % part), [label_packet(r) for r in rows_])
        (d / ('spot_check_%s.md' % part)).write_text(packets_md([label_packet(r) for r in rows_],
                                                               'spot check %s (shuffled)' % part))
    update_manifest(out, label_export={'at': now_iso(), 'candidates': len(rows), 'batches': len(batches),
                                       'batch_sizes': [len(b) for b in batches], 'spot_check': len(spot),
                                       'spot_seed': SEED + 1, 'chars_shown': BODY_LABEL})
    print(json.dumps({'candidates': len(rows), 'batches': [len(b) for b in batches], 'spot_check': len(spot)}))
    return 0


def validate_labels(cands, labeled):
    """(rows by id, problems): every candidate labeled exactly once, with a known label, a boolean surprise and a
    confidence in [0, 1]."""
    problems, by_id = [], {}
    ids = {c['id'] for c in cands}
    for r in labeled:
        i = r.get('id')
        if i not in ids:
            problems.append('unknown id %s' % i)
            continue
        if i in by_id:
            problems.append('duplicate id %s' % i)
            continue
        if r.get('label') not in LABELS:
            problems.append('%s: label %r' % (i, r.get('label')))
        if not isinstance(r.get('surprise'), bool):
            problems.append('%s: surprise %r' % (i, r.get('surprise')))
        c = r.get('confidence')
        if not isinstance(c, (int, float)) or not 0 <= c <= 1:
            problems.append('%s: confidence %r' % (i, c))
        by_id[i] = r
    for i in ids - set(by_id):
        problems.append('missing %s' % i)
    return by_id, problems


def cmd_label_check(args):
    """Validate one labeler's output against its batch: every id once, valid fields. Prints OK or the problems."""
    d = Path(args.out) / 'label_batches'
    name = args.batch
    if name.startswith('spot_'):
        src, dst = d / ('spot_check_%s.jsonl' % name[5:]), d / ('spot_out_%s.jsonl' % name[5:])
    else:
        src, dst = d / ('batch_%s.jsonl' % name), d / ('out_%s.jsonl' % name)
    pk = read_jsonl(src)
    try:
        lab = read_jsonl(dst)
    except json.JSONDecodeError as e:
        print('not valid JSON lines: %s' % e)
        return 1
    _, problems = validate_labels(pk, lab)
    for r in lab:
        if r.get('binding') not in ('signal', 'binding', 'unknown'):
            problems.append('%s: binding %r' % (r.get('id'), r.get('binding')))
        if not (r.get('reason') or '').strip():
            problems.append('%s: no reason' % r.get('id'))
    if problems:
        print('\n'.join(problems[:40]))
        print('%d problems in %s' % (len(problems), dst.name))
        return 1
    counts = {k: sum(1 for r in lab if r['label'] == k) for k in LABELS}
    print('OK %s: %d packets labeled %s' % (dst.name, len(lab), counts))
    return 0


def cmd_label_freeze(args):
    out = Path(args.out)
    man = read_json(out / 'manifest.json', {}) or {}
    if man.get('labels_frozen') and not args.force:
        print('labels already frozen at %s (sha256 %s); --force to re-freeze' % (
            man['labels_frozen']['at'], man['labels_frozen']['sha256'][:12]))
        return 1
    cands = read_jsonl(out / 'candidates.jsonl')
    labeled = []
    for fn in sorted((out / 'label_batches').glob('out_*.jsonl')):
        for r in read_jsonl(fn):
            r['labeler_batch'] = fn.stem
            labeled.append(r)
    by_id, problems = validate_labels(cands, labeled)
    if problems:
        print('\n'.join(problems[:50]))
        print('%d problems; nothing frozen' % len(problems))
        return 1
    rows = []
    for c in cands:
        r = by_id[c['id']]
        rows.append({'id': c['id'], 'space': c['space'], 'token': c['token'], 'created_utc': utc_iso(c['created'] * 1000),
                     'label': r['label'], 'surprise': r['surprise'], 'confidence': float(r['confidence']),
                     'binding': r.get('binding') or 'unknown', 'reason': (r.get('reason') or '')[:300],
                     'labeler_batch': r['labeler_batch'], 'control': c['control'], 'keyword_label': c['keyword_label']})
    rows.sort(key=lambda r: (r['created_utc'], r['id']))
    write_jsonl(out / 'labels.jsonl', rows)
    ev = sorted(r['created_utc'] for r in rows if r['label'] != 'NEUTRAL')
    med = ev[len(ev) // 2] if ev else None
    cutoff = (med[:7] + '-01T00:00:00+00:00') if med else None
    counts = {}
    for r in rows:
        counts[r['label']] = counts.get(r['label'], 0) + 1
    man = update_manifest(out, labels_frozen={
        'at': now_iso(), 'sha256': sha256_file(out / 'labels.jsonl'), 'n': len(rows), 'counts': counts,
        'criteria_sha256': sha256_file(out / 'criteria.md') if (out / 'criteria.md').exists() else None,
        'cutoff': cutoff, 'cutoff_rule': 'first day of the month holding the median created date of VALUE_UP/VALUE_DOWN '
                                         'labels, fixed at the freeze, before any price path'})
    print(json.dumps(man['labels_frozen'], indent=1))
    return 0


def cohen_kappa(a, b, cats=LABELS):
    n = len(a)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((sum(1 for x in a if x == c) / n) * (sum(1 for y in b if y == c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else None


def cmd_label_agree(args):
    """Agreement of the blind spot-check re-label with the frozen labels, and of the keyword-only classifier with both."""
    out = Path(args.out)
    frozen = {r['id']: r for r in read_jsonl(out / 'labels.jsonl')}
    spot = {r['id']: r for part in ('a', 'b') for r in read_jsonl(out / 'label_batches' / ('spot_out_%s.jsonl' % part))}
    ids = [i for i in spot if i in frozen]
    a = [frozen[i]['label'] for i in ids]
    b = [spot[i]['label'] for i in ids]
    conf = {}
    for x, y in zip(a, b):
        conf.setdefault(x, {}).setdefault(y, 0)
        conf[x][y] += 1
    disagreements = [{'id': i, 'token': frozen[i]['token'], 'frozen': frozen[i]['label'], 'spot': spot[i]['label'],
                      'frozen_reason': frozen[i]['reason'], 'spot_reason': spot[i].get('reason')}
                     for i in ids if frozen[i]['label'] != spot[i]['label']]
    allr = list(frozen.values())
    kw = [r['keyword_label'] for r in allr]
    llm = [r['label'] for r in allr]
    kconf = {}
    for x, y in zip(llm, kw):
        kconf.setdefault(x, {}).setdefault(y, 0)
        kconf[x][y] += 1
    ctrl = [r for r in allr if r['control']]
    res = {'at': now_iso(), 'spot_n': len(ids),
           'agreement': (sum(1 for x, y in zip(a, b) if x == y) / len(ids)) if ids else None,
           'kappa': cohen_kappa(a, b), 'confusion_frozen_by_spot': conf,
           'surprise_agreement': (sum(1 for i in ids if frozen[i]['surprise'] == spot[i].get('surprise')) / len(ids))
           if ids else None,
           'disagreements': disagreements,
           'keyword_vs_llm': {'n': len(allr), 'agreement': sum(1 for x, y in zip(llm, kw) if x == y) / len(allr),
                              'kappa': cohen_kappa(llm, kw), 'confusion_llm_by_keyword': kconf},
           'controls': {'n': len(ctrl), 'llm_labels': {k: sum(1 for r in ctrl if r['label'] == k) for k in LABELS}},
           'screen_hits': {'n': len(allr) - len(ctrl),
                           'llm_labels': {k: sum(1 for r in allr if not r['control'] and r['label'] == k) for k in LABELS}}}
    write_json(out / 'label_agreement.json', res)
    print(json.dumps({k: v for k, v in res.items() if k != 'disagreements'}, indent=1))
    return 0




# ------------------------------------------------------------------------------------------------ prices (Binance)

def resolve_symbols(exchange_info, tokens):
    """{token: [symbol, multiplier, status]} for each token's USDT-margined perpetual (TRADING preferred over a
    delisted SETTLING contract; thousand-unit contracts such as 1000FLOKIUSDT are found too)."""
    perps = {x['symbol']: x.get('status') for x in exchange_info.get('symbols') or []
             if x.get('contractType') == 'PERPETUAL' and x.get('quoteAsset') == 'USDT'}
    out = {}
    for t in tokens:
        best = None
        for pre, mult in (('', 1), ('1000', 1000), ('1000000', 1_000_000), ('1M', 1_000_000)):
            sym = pre + t + 'USDT'
            if sym in perps and (best is None or (perps[sym] == 'TRADING' and best[2] != 'TRADING')):
                best = [sym, mult, perps[sym]]
        if best:
            out[t] = best
    return out


def bn_klines(http, sym, start_ms, end_ms, interval='4h', limit=1000):
    """[[open_ms, open, high, low, close, quote_volume], ...] from the first bar at or after start_ms."""
    rows, s = [], start_ms
    while s < end_ms:
        r = http.request(BN_FAPI + '/fapi/v1/klines', {'symbol': sym, 'interval': interval, 'startTime': s,
                                                       'endTime': end_ms, 'limit': limit})
        if not isinstance(r, list) or not r:
            break
        rows += [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[7])] for k in r]
        if len(r) < limit:
            break
        s = int(r[-1][0]) + 1
    return rows


def bn_funding(http, sym, start_ms, end_ms):
    """[[funding_time_ms, rate], ...]; a positive rate is paid by longs to shorts."""
    rows, s = [], start_ms
    while s < end_ms:
        r = http.request(BN_FAPI + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': end_ms,
                                                            'limit': 1000})
        if not isinstance(r, list) or not r:
            break
        rows += [[int(x['fundingTime']), float(x['fundingRate'])] for x in r]
        if len(r) < 1000:
            break
        s = int(r[-1][0] if isinstance(r[-1], list) else r[-1]['fundingTime']) + 1
    return rows


def cmd_prices(args):
    out = Path(args.out)
    raw = out / 'raw' / 'binance'
    http_k = Http(interval=args.interval)
    http_f = Http(interval=max(0.7, args.interval))      # fundingRate shares 500 requests / 5 min / IP
    t0 = time.time()
    xi = http_k.request(BN_FAPI + '/fapi/v1/exchangeInfo')
    write_json(raw / 'exchangeInfo_perps.json', [x for x in xi.get('symbols', []) if x.get('contractType') == 'PERPETUAL'])
    tokens = sorted(set(SPACES.values()))
    sym = resolve_symbols(xi, tokens + ['BTC'])
    s_ms = int(dt.datetime.fromisoformat(args.since).replace(tzinfo=UTC).timestamp() * 1000)
    e_ms = int(time.time() * 1000)
    got, failed = {}, {}
    order = ['BTC'] + (tokens[::-1] if args.reverse else tokens)
    for t in order:
        if t not in sym:
            failed[t] = 'no USDT perpetual on Binance'
            continue
        s = sym[t][0]
        kp, fp = raw / 'klines_4h' / (s + '.json.gz'), raw / 'funding' / (s + '.json.gz')
        try:
            if not kp.exists() or args.force:
                write_gz(kp, bn_klines(http_k, s, s_ms, e_ms))
            if not fp.exists() or args.force:
                write_gz(fp, bn_funding(http_f, s, s_ms, e_ms))
        except RuntimeError as e:
            failed[t] = str(e)[:160]
            continue
        k, f = read_gz(kp), read_gz(fp)
        sp = traded_span(k)
        got[t] = {'symbol': s, 'multiplier': sym[t][1], 'status': sym[t][2], 'bars': len(k), 'funding': len(f),
                  'zero_volume_bars': sum(1 for r in k if r[5] <= 0),
                  'first_bar': utc_iso(sp[0] - BAR_MS) if sp else None, 'last_bar': utc_iso(sp[1] - BAR_MS) if sp else None}
        print('%-7s %-16s %-8s bars %6d  funding %5d  %s .. %s' % (t, s, sym[t][2], len(k), len(f),
                                                                    got[t]['first_bar'] and got[t]['first_bar'][:10],
                                                                    got[t]['last_bar'] and got[t]['last_bar'][:10]),
              flush=True)
    update_manifest(out, prices={'at': now_iso(), 'source': BN_FAPI + ' /fapi/v1/klines (4h) and /fapi/v1/fundingRate',
                                 'since': args.since, 'tokens': got, 'failed': failed,
                                 'seconds': round(time.time() - t0, 1),
                                 'http': {'klines': http_k.stats(), 'funding': http_f.stats()}})
    print(json.dumps({'tokens': len(got), 'failed': failed}))
    return 0


def book_impact_bps(levels, mid, usd):
    """Average distance from mid, in bp, of filling `usd` against `levels` ([[px, qty], ...] best first); None if the
    side is too thin to fill it."""
    left, cost_q, filled = usd, 0.0, 0.0
    for px, q in levels:
        px, q = float(px), float(q)
        take = min(left, px * q)
        filled += take
        cost_q += take / px
        left -= take
        if left <= 1e-9:
            break
    if left > 1e-6 or cost_q <= 0:
        return None
    vwap = filled / cost_q
    return abs(vwap / mid - 1.0) * 1e4


def depth_within(levels, mid, bps):
    lim = bps / 1e4
    return sum(float(p) * float(q) for p, q in levels if abs(float(p) / mid - 1.0) <= lim)


def book_summary(book, sizes=(25_000, 50_000, 100_000, 250_000)):
    bids, asks = book.get('bids') or [], book.get('asks') or []
    if not bids or not asks:
        return None
    mid = (float(bids[0][0]) + float(asks[0][0])) / 2
    res = {'mid': mid, 'half_spread_bps': (float(asks[0][0]) - float(bids[0][0])) / 2 / mid * 1e4}
    for b in (25, 50, 100):
        res['bid_depth_%dbp' % b] = depth_within(bids, mid, b)
        res['ask_depth_%dbp' % b] = depth_within(asks, mid, b)
    for usd in sizes:
        buy, sell = book_impact_bps(asks, mid, usd), book_impact_bps(bids, mid, usd)
        res['impact_bps_%dk' % (usd // 1000)] = None if buy is None or sell is None else (buy + sell) / 2
    return res


def cmd_books(args):
    """Live Binance books (500 levels a side), 24h volume and open interest for every token still trading."""
    out = Path(args.out)
    man = read_json(out / 'manifest.json', {})
    toks = (man.get('prices') or {}).get('tokens') or {}
    http = Http(interval=args.interval)
    tick = {x['symbol']: x for x in http.request(BN_FAPI + '/fapi/v1/ticker/24hr')}
    res = {}
    for t, m in sorted(toks.items()):
        if m['status'] != 'TRADING':
            continue
        s = m['symbol']
        d = http.request(BN_FAPI + '/fapi/v1/depth', {'symbol': s, 'limit': 500})
        oi = http.request(BN_FAPI + '/fapi/v1/openInterest', {'symbol': s})
        summ = book_summary(d) if isinstance(d, dict) else None
        if summ is None:
            continue
        summ['quote_volume_24h'] = float((tick.get(s) or {}).get('quoteVolume') or 0)
        summ['open_interest_usd'] = float(oi.get('openInterest') or 0) * summ['mid'] if isinstance(oi, dict) else None
        summ['symbol'] = s
        res[t] = summ
    write_json(out / 'raw' / 'books.json', {'at': now_iso(), 'source': BN_FAPI + '/fapi/v1/depth?limit=500',
                                            'books': res})
    update_manifest(out, books={'at': now_iso(), 'tokens': len(res), 'http': http.stats()})
    print(json.dumps({'books': len(res)}))
    return 0


# ------------------------------------------------------------------------------------------------ series

class Series:
    """4h closes keyed by bar close time (open + 4h) and funding by its time, with the two lookups a study needs:
    `before(t)` — the last close at or before t (what was known at t), and `after(t)` — the first close at or after t
    (the price a decision taken at t can trade at)."""

    def __init__(self, klines, funding=(), max_gap_ms=2 * BAR_MS):
        # Binance keeps serving a delisted contract's klines at its settlement price with zero volume (BALUSDT stopped
        # trading on 2025-04-14 and still had flat bars on 2026-10-10): a bar nobody traded is not a price.
        k = sorted((r for r in klines if len(r) < 6 or r[5] > 0), key=lambda r: r[0])
        self.t = [int(r[0]) + BAR_MS for r in k]
        self.c = [float(r[4]) for r in k]
        f = sorted(funding, key=lambda r: r[0])
        self.ft = [int(r[0]) for r in f]
        self.fcum = [0.0]
        for r in f:
            self.fcum.append(self.fcum[-1] + float(r[1]))
        self.max_gap = max_gap_ms

    def before(self, t):
        i = bisect.bisect_right(self.t, t) - 1
        if i < 0 or t - self.t[i] > self.max_gap:
            return None
        return self.t[i], self.c[i]

    def after(self, t):
        i = bisect.bisect_left(self.t, t)
        if i >= len(self.t) or self.t[i] - t > self.max_gap:
            return None
        return self.t[i], self.c[i]

    def funding(self, t0, t1):
        """Sum of funding rates with time in (t0, t1]: what a long paid (positive) or received (negative)."""
        i0 = bisect.bisect_right(self.ft, t0)
        i1 = bisect.bisect_right(self.ft, t1)
        return self.fcum[i1] - self.fcum[i0]


def load_series(out, man=None):
    man = man or read_json(Path(out) / 'manifest.json', {})
    toks = (man.get('prices') or {}).get('tokens') or {}
    raw = Path(out) / 'raw' / 'binance'
    res = {}
    for t, m in toks.items():
        kp, fp = raw / 'klines_4h' / (m['symbol'] + '.json.gz'), raw / 'funding' / (m['symbol'] + '.json.gz')
        if kp.exists():
            res[t] = Series(read_gz(kp), read_gz(fp) if fp.exists() else [])
    return res


# ------------------------------------------------------------------------------------------------ events

NEG_CHOICE = re.compile(r"^\s*(no\b|nay\b|against|reject|disagree|oppose|do not\b|don'?t\b|do nothing|nothing\b|"
                        r"no action|keep\b|maintain\b|remain\b|status quo|no change|none\b|n/a|not\b|deny|veto)", re.I)
ABSTAIN = re.compile(r'abstain', re.I)


def outcome(choices, scores, scores_total=None, quorum=None):
    """{'result': passed|failed|unclear, 'margin', 'top'}: passed when the leading non-abstain choice is not a
    no / against / status-quo option and any quorum was met; margin = (leader - runner-up) / non-abstain votes."""
    if not choices or not scores or len(choices) != len(scores):
        return {'result': 'unclear', 'margin': None, 'top': None}
    pairs = [(float(s or 0), c) for c, s in zip(choices, scores) if not ABSTAIN.search(str(c or ''))]
    tot = sum(s for s, _ in pairs)
    if not pairs or tot <= 0:
        return {'result': 'unclear', 'margin': None, 'top': None}
    pairs.sort(key=lambda x: -x[0])
    margin = (pairs[0][0] - (pairs[1][0] if len(pairs) > 1 else 0.0)) / tot
    top = str(pairs[0][1])
    if quorum and scores_total is not None and float(scores_total) < float(quorum):
        return {'result': 'failed', 'margin': margin, 'top': top, 'quorum_missed': True}
    if len(pairs) > 1 and pairs[0][0] == pairs[1][0]:
        return {'result': 'unclear', 'margin': 0.0, 'top': top}
    return {'result': 'failed' if NEG_CHOICE.search(top) else 'passed', 'margin': margin, 'top': top}


def build_events(cands, labels, label_key='label'):
    """One row per labeled candidate with its Snapshot times in ms and its outcome."""
    lab = {r['id']: r for r in labels}
    ev = []
    for c in cands:
        r = lab.get(c['id'])
        if r is None:
            continue
        o = outcome(c.get('choices'), c.get('scores'), c.get('scores_total'), c.get('quorum'))
        # Snapshot records a start up to 40 hours before the proposal's creation time on 804 of 2,522 candidates (the
        # form's "now" precedes the IPFS pin); a start before publication would let 'start + 1 day' trade on a
        # proposal nobody could see, so the start anchor is never earlier than publication.
        C_ms = int(c['created']) * 1000
        ev.append({'id': c['id'], 'token': c['token'], 'space': c['space'], 'title': c['title'],
                   'C': C_ms, 'S': max(int(c['start']) * 1000, C_ms), 'E': int(c['end']) * 1000,
                   'label': r[label_key] if label_key in r else c.get(label_key),
                   'surprise': r.get('surprise'), 'confidence': r.get('confidence'), 'binding': r.get('binding'),
                   'control': c.get('control'), 'outcome': o['result'], 'margin': o['margin'], 'votes': c.get('votes')})
    ev.sort(key=lambda e: (e['C'], e['id']))
    return ev


def dedupe_events(events):
    """Keep the first proposal per (token, label, UTC day of publication): a DAO that posts three versions of one
    buyback on the same day is one event, not three."""
    seen, out = set(), []
    for e in sorted(events, key=lambda e: (e['C'], e['id'])):
        k = (e['token'], e['label'], e['C'] // DAY_MS)
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out


def anchor(e, a, off):
    return e[a] + off


AR_WINDOWS = {                       # measurement windows: (anchor, offset) -> (anchor, offset), prices known at each end
    'pre7': (('C', -7 * DAY_MS), ('C', 0)),
    'created+1d': (('C', 0), ('C', DAY_MS)),
    'vote': (('S', 0), ('E', 0)),
    'end+1d': (('E', 0), ('E', DAY_MS)),
    'end+3d': (('E', 0), ('E', 3 * DAY_MS)),
    'end+7d': (('E', 0), ('E', 7 * DAY_MS)),
    'created..end+7d': (('C', 0), ('E', 7 * DAY_MS)),
}
TRADE_WINDOWS = {                    # trades: decision time -> exit time, executed at the first 4h close at or after each
    'start+1d>end': (('S', DAY_MS), ('E', 0)),
    'start+1d>end+1d': (('S', DAY_MS), ('E', DAY_MS)),
    'start+1d>end+3d': (('S', DAY_MS), ('E', 3 * DAY_MS)),
    'start+1d>end+7d': (('S', DAY_MS), ('E', 7 * DAY_MS)),
    'end+1h>end+1d': (('E', HOUR_MS), ('E', DAY_MS)),
    'end+1h>end+3d': (('E', HOUR_MS), ('E', 3 * DAY_MS)),
    'end+1h>end+7d': (('E', HOUR_MS), ('E', 7 * DAY_MS)),
}


def window_ar(e, w, series, btc, min_others=5):
    """Log return of the token over window `w` of event `e`, less BTC's and less the equal-weight mean of every other
    universe token priced at both ends. Prices are the last close at or before each end (no look-ahead)."""
    (a0, o0), (a1, o1) = w
    t0, t1 = anchor(e, a0, o0), anchor(e, a1, o1)
    if t1 <= t0:
        return None
    s = series.get(e['token'])
    if s is None:
        return None
    p0, p1, b0, b1 = s.before(t0), s.before(t1), btc.before(t0), btc.before(t1)
    if None in (p0, p1, b0, b1) or p1[0] <= p0[0]:
        return None
    r = math.log(p1[1] / p0[1])
    rb = math.log(b1[1] / b0[1])
    others = []
    for tok, o in series.items():
        if tok in (e['token'], 'BTC'):
            continue
        q0, q1 = o.before(t0), o.before(t1)
        if q0 and q1 and q1[0] > q0[0]:
            others.append(math.log(q1[1] / q0[1]))
    ew = statistics.fmean(others) if len(others) >= min_others else None
    return {'r': r, 'r_btc': rb, 'ar_btc': r - rb, 'r_ew': ew, 'ar_ew': (r - ew) if ew is not None else None,
            'n_basket': len(others), 't0': t0, 't1': t1}


def trade_pnl(e, w, direction, series, btc, cost_rt):
    """Long (direction +1) or short (-1) the token perp against the opposite BTC perp leg of the same notional, decided
    at the window's first time and executed at the first 4h close at or after it; closed the same way. Simple returns
    (what a constant-notional pair earns), funding over (entry, exit] with Binance's sign (positive: longs pay), and
    `cost_rt` for both legs' round trips."""
    (a0, o0), (a1, o1) = w
    td, tx = anchor(e, a0, o0), anchor(e, a1, o1)
    s = series.get(e['token'])
    if s is None or tx <= td:
        return None
    en, ex, ben, bex = s.after(td), s.after(tx), btc.after(td), btc.after(tx)
    if None in (en, ex, ben, bex) or ex[0] <= en[0]:
        return None
    r_tok = ex[1] / en[1] - 1.0
    r_btc = bex[1] / ben[1] - 1.0
    f_tok = s.funding(en[0], ex[0])
    f_btc = btc.funding(ben[0], bex[0])
    gross = direction * (r_tok - r_btc)
    funding = -direction * f_tok + direction * f_btc
    days = (ex[0] - en[0]) / DAY_MS
    pnl = gross + funding - cost_rt
    return {'entry_t': en[0], 'exit_t': ex[0], 'days': days, 'r_tok': r_tok, 'r_btc': r_btc, 'gross': gross,
            'funding': funding, 'cost': cost_rt, 'pnl': pnl, 'excess_ssr': pnl - SSR * days / 365.0}


def placebo_shifts(event_id, k=2, lo=15, hi=30):
    """k deterministic day shifts per event, half before and half after, each 15-30 days."""
    rng = random.Random(int(hashlib.sha256(event_id.encode()).hexdigest()[:12], 16))
    return [(-1 if i % 2 == 0 else 1) * rng.uniform(lo, hi) for i in range(k)]


def shifted(e, days):
    d = int(days * DAY_MS)
    return dict(e, C=e['C'] + d, S=e['S'] + d, E=e['E'] + d, placebo_shift_days=days)


def placebo_ok(p, token_event_times, guard_ms=7 * DAY_MS, tail_ms=7 * DAY_MS):
    """A placebo window [C - 7d, E + 7d] must not contain the publication of any labeled event of the same token."""
    lo, hi = p['C'] - guard_ms, p['E'] + tail_ms
    i = bisect.bisect_left(token_event_times, lo)
    return not (i < len(token_event_times) and token_event_times[i] <= hi)


# ------------------------------------------------------------------------------------------------ statistics

def tstat(x):
    x = [v for v in x if v is not None]
    if len(x) < 3:
        return None
    sd = statistics.stdev(x)
    return (statistics.fmean(x) / (sd / math.sqrt(len(x)))) if sd > 0 else None


def welch_t(x, y):
    if len(x) < 3 or len(y) < 3:
        return None
    vx, vy = statistics.variance(x) / len(x), statistics.variance(y) / len(y)
    if vx + vy <= 0:
        return None
    return (statistics.fmean(x) - statistics.fmean(y)) / math.sqrt(vx + vy)


def pvalue(t):
    return None if t is None else 2.0 * (1.0 - statistics.NormalDist().cdf(abs(t)))


def week_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000, UTC).isocalendar()
    return '%d-W%02d' % (d[0], d[1])


def cluster_means(pairs, unit='week'):
    """Mean of the values sharing a UTC day or ISO week, one per cluster, in time order."""
    d = {}
    for T, v in pairs:
        k = (T // DAY_MS) if unit == 'day' else week_of(T)
        d.setdefault(k, []).append(v)
    return [statistics.fmean(v) for _, v in sorted(d.items())]


def describe(pairs):
    """pairs = [(cluster time ms, value)]: n, mean, median, plain t, t by event day and by event week, hit rate."""
    x = [v for _, v in pairs if v is not None]
    pairs = [(T, v) for T, v in pairs if v is not None]
    if not x:
        return {'n': 0}
    xs = sorted(x)
    k = int(0.05 * len(xs))
    return {'n': len(x), 'mean': statistics.fmean(x), 'median': statistics.median(x),
            'trim5': statistics.fmean(xs[k:len(xs) - k]) if len(xs) >= 20 else None, 't': tstat(x),
            't_day': tstat(cluster_means(pairs, 'day')), 't_week': tstat(cluster_means(pairs, 'week')),
            'weeks': len(set(week_of(T) for T, _ in pairs)), 'hit': sum(1 for v in x if v > 0) / len(x)}


# ------------------------------------------------------------------------------------------------ analysis

def iso_ms(s):
    d = dt.datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=UTC)
    return int(d.timestamp() * 1000)


def pair_costs(books, tokens, usd, fallback_q=0.75):
    """{token: round-trip cost of the pair as a fraction of one leg's notional} at `usd` a leg: taker fees on four
    fills, the token's average impact at `usd` from its live book (twice), and BTC's half spread (twice). Tokens with
    no live book (delisted) or a book too thin to fill `usd` get the `fallback_q` quantile of the priced tokens."""
    key = 'impact_bps_%dk' % (usd // 1000)
    imp = {t: (b or {}).get(key) for t, b in books.items()}
    priced = sorted(v for v in imp.values() if v is not None)
    fb = priced[min(len(priced) - 1, int(fallback_q * len(priced)))] if priced else 30.0
    res = {}
    for t in tokens:
        i = imp.get(t)
        res[t] = (4 * TAKER_BPS + 2 * (i if i is not None else fb) + 2 * BTC_HALF_SPREAD_BPS) / 1e4
    return res, fb


def direction_of(label):
    return 1 if label == 'VALUE_UP' else -1


SIDES = {'up_long': ('VALUE_UP',), 'down_short': ('VALUE_DOWN',), 'both': ('VALUE_UP', 'VALUE_DOWN')}
FILTERS = ('all', 'passed')


def run_variants(events, series, btc, costs, cut_ms, min_events, costs_alt=None):
    """Every (trade window, side, outcome filter) with its in-sample and out-of-sample P&L, the placebo's, and the
    excess. Outcome 'passed' is known only at the vote's end, so it is tradable only for entries after the end."""
    times = {}
    for e in events:
        times.setdefault(e['token'], []).append(e['C'])
    for v in times.values():
        v.sort()
    variants = []
    for wname, w in TRADE_WINDOWS.items():
        for side, labs in SIDES.items():
            for filt in FILTERS:
                tradable = not (filt == 'passed' and w[0][0] != 'E')
                sel = [e for e in events if e['label'] in labs and (filt == 'all' or e['outcome'] == 'passed')]
                rows, prow = [], []
                for e in sel:
                    d = direction_of(e['label'])
                    tr = trade_pnl(e, w, d, series, btc, costs.get(e['token'], 0.003))
                    if tr:
                        rows.append((e, tr))
                    for sh in placebo_shifts(e['id']):
                        p = shifted(e, sh)
                        if not placebo_ok(p, times.get(e['token'], [])):
                            continue
                        ptr = trade_pnl(p, w, d, series, btc, costs.get(e['token'], 0.003))
                        if ptr:
                            prow.append((p, ptr))
                ins = [(e['C'], tr['pnl']) for e, tr in rows if e['C'] < cut_ms]
                oos = [(e['C'], tr['pnl']) for e, tr in rows if e['C'] >= cut_ms]
                p_in = [tr['pnl'] for p, tr in prow if p['C'] < cut_ms]
                p_out = [tr['pnl'] for p, tr in prow if p['C'] >= cut_ms]
                vi, vo = [v for _, v in ins], [v for _, v in oos]

                def comp(rs):
                    if not rs:
                        return None
                    return {k: statistics.fmean(tr[k] for _, tr in rs) for k in
                            ('gross', 'funding', 'cost', 'pnl', 'excess_ssr', 'days')}
                variants.append({
                    'window': wname, 'side': side, 'filter': filt, 'tradable': tradable,
                    'n_in': len(vi), 'n_out': len(vo), 'in': describe(ins), 'out': describe(oos),
                    'placebo_n_in': len(p_in), 'placebo_n_out': len(p_out),
                    'placebo_mean_in': statistics.fmean(p_in) if p_in else None,
                    'placebo_mean_out': statistics.fmean(p_out) if p_out else None,
                    'excess_in': (statistics.fmean(vi) - statistics.fmean(p_in)) if vi and p_in else None,
                    'excess_out': (statistics.fmean(vo) - statistics.fmean(p_out)) if vo and p_out else None,
                    'excess_t_in': welch_t(vi, p_in), 'excess_t_out': welch_t(vo, p_out),
                    'components_in': comp([(e, tr) for e, tr in rows if e['C'] < cut_ms]),
                    'components_out': comp([(e, tr) for e, tr in rows if e['C'] >= cut_ms]),
                    'excess_ssr_out': statistics.fmean(tr['excess_ssr'] for e, tr in rows if e['C'] >= cut_ms)
                    if vo else None,
                    'by_half_year': by_half(rows, prow),
                    'trades_out': [{'id': e['id'], 'token': e['token'], 'label': e['label'], 'title': e['title'][:90],
                                    'entry': utc_iso(tr['entry_t'])[:16], 'pnl': tr['pnl'], 'cost': tr['cost'],
                                    'days': tr['days']}
                                   for e, tr in rows if e['C'] >= cut_ms],
                    # the same trades at the alternative size: only the cost changes
                    'mean_out_alt_size': statistics.fmean(tr['pnl'] + tr['cost'] - costs_alt.get(e['token'], tr['cost'])
                                                          for e, tr in rows if e['C'] >= cut_ms)
                    if (vo and costs_alt) else None,
                })
    elig = [v for v in variants if v['tradable'] and v['n_in'] >= min_events and v['excess_t_in'] is not None]
    chosen = max(elig, key=lambda v: v['excess_t_in']) if elig else None
    trad = [v for v in variants if v['tradable']]
    rej_in, adj_in = B.bh([pvalue(v['excess_t_in']) for v in trad], q=0.10)
    rej_out, adj_out = B.bh([pvalue(v['excess_t_out']) for v in trad], q=0.10)
    for v, ri, ai, ro, ao in zip(trad, rej_in, adj_in, rej_out, adj_out):
        v['bh_in'], v['bh_adj_p_in'], v['bh_out'], v['bh_adj_p_out'] = ri, ai, ro, ao
    sel = None
    if chosen:
        oos = [t['pnl'] for t in chosen['trades_out']]
        sel = {'window': chosen['window'], 'side': chosen['side'], 'filter': chosen['filter'],
               'n_tradable_variants': len(trad), 'eligible': len(elig),
               'deflated_sharpe_out': B.deflated_sharpe(oos, len(trad)) if len(oos) >= 3 else None}
    return variants, sel


def by_half(rows, prow):
    q = {}
    for e, tr in rows:
        q.setdefault(half_of(e['C']), {'pnl': [], 'placebo': []})['pnl'].append(tr['pnl'])
    for p, tr in prow:
        q.setdefault(half_of(p['C']), {'pnl': [], 'placebo': []})['placebo'].append(tr['pnl'])
    out = {}
    for k in sorted(q):
        a, b = q[k]['pnl'], q[k]['placebo']
        out[k] = {'n': len(a), 'mean': statistics.fmean(a) if a else None,
                  'placebo_mean': statistics.fmean(b) if b else None,
                  'excess': (statistics.fmean(a) - statistics.fmean(b)) if (a and b) else None}
    return out


def half_of(ms):
    d = dt.datetime.fromtimestamp(ms / 1000, UTC)
    return '%dH%d' % (d.year, 1 if d.month <= 6 else 2)


def ar_table(groups, series, btc, cut_ms):
    """{label: {window: {benchmark: {'all','in','out'}}}} of abnormal log returns, clustered by event week."""
    res = {}
    for lab, evs in groups.items():
        res[lab] = {}
        for wname, w in AR_WINDOWS.items():
            rows = [(e, window_ar(e, w, series, btc)) for e in evs]
            rows = [(e, a) for e, a in rows if a]
            res[lab][wname] = {}
            for bench in ('ar_btc', 'ar_ew'):
                pr = [(e['C'], a[bench]) for e, a in rows if a[bench] is not None]
                res[lab][wname][bench] = {'all': describe(pr), 'in': describe([x for x in pr if x[0] < cut_ms]),
                                          'out': describe([x for x in pr if x[0] >= cut_ms])}
    return res


def ar_bh(ar, q=0.10):
    """Benjamini-Hochberg over the value labels x measurement windows (vs the basket, event-week t), separately for the
    full sample, the in-sample and the out-of-sample halves: which abnormal returns survive the number of looks."""
    res = {}
    for part in ('all', 'in', 'out'):
        keys, pv = [], []
        for lab in ('VALUE_UP', 'VALUE_DOWN'):
            for wname in AR_WINDOWS:
                keys.append('%s %s' % (lab, wname))
                pv.append(pvalue(ar[lab][wname]['ar_ew'][part].get('t_week')))
        rej, adj = B.bh(pv, q=q)
        res[part] = {'tests': len(keys), 'survivors': [k for k, r in zip(keys, rej) if r],
                     'adjusted_p': dict(zip(keys, adj))}
    return res


def placebo_ar(events, series, btc, cut_ms, wname='created..end+7d'):
    times = {}
    for e in events:
        times.setdefault(e['token'], []).append(e['C'])
    for v in times.values():
        v.sort()
    res = {}
    for lab in ('VALUE_UP', 'VALUE_DOWN'):
        pr = []
        for e in events:
            if e['label'] != lab:
                continue
            for sh in placebo_shifts(e['id']):
                p = shifted(e, sh)
                if placebo_ok(p, times.get(e['token'], [])):
                    a = window_ar(p, AR_WINDOWS[wname], series, btc)
                    if a and a['ar_ew'] is not None:
                        pr.append((p['C'], a['ar_ew']))
        res[lab] = {'all': describe(pr), 'in': describe([x for x in pr if x[0] < cut_ms]),
                    'out': describe([x for x in pr if x[0] >= cut_ms])}
    return res


def conditional(events, series, btc, wname='created..end+7d', bench='ar_ew', cut_ms=None):
    """Abnormal return of value events split by what the labeler and the tally say: surprise, outcome, decisiveness
    (final margin), confidence, binding, and whether the keyword screen found it."""
    rows = []
    for e in events:
        a = window_ar(e, AR_WINDOWS[wname], series, btc)
        if a and a[bench] is not None:
            rows.append((e, a[bench]))
    res = {}
    for lab in ('VALUE_UP', 'VALUE_DOWN'):
        sub = [(e, v) for e, v in rows if e['label'] == lab]
        splits = {
            'surprise': lambda e: 'first appearance' if e['surprise'] else 'continuation',
            'outcome': lambda e: e['outcome'],
            'decisive': lambda e: ('margin>=0.8' if (e['margin'] or 0) >= 0.8 else 'margin<0.8')
            if e['outcome'] == 'passed' else 'not passed',
            'confidence': lambda e: 'conf>=0.8' if (e['confidence'] or 0) >= 0.8 else 'conf<0.8',
            'binding': lambda e: e['binding'] or 'unknown',
            'found_by': lambda e: 'control sample' if e['control'] else 'keyword screen',
        }
        res[lab] = {}
        for name, f in splits.items():
            g = {}
            for e, v in sub:
                g.setdefault(f(e), []).append((e['C'], v))
            res[lab][name] = {k: dict(describe(v), **({} if cut_ms is None else {
                'in': describe([x for x in v if x[0] < cut_ms]), 'out': describe([x for x in v if x[0] >= cut_ms])}))
                for k, v in sorted(g.items())}
    return res


def by_year(groups, series, btc, wnames=('created..end+7d', 'end+7d')):
    """Mean and median abnormal return vs the basket per calendar year of publication: is an effect one regime?"""
    res = {}
    for lab, evs in groups.items():
        res[lab] = {}
        for wname in wnames:
            d = {}
            for e in evs:
                a = window_ar(e, AR_WINDOWS[wname], series, btc)
                if a and a['ar_ew'] is not None:
                    d.setdefault(utc_iso(e['C'])[:4], []).append((e['C'], a['ar_ew']))
            res[lab][wname] = {y: dict(describe(v), median_ar=statistics.median([x for _, x in v]))
                               for y, v in sorted(d.items())}
    return res


def anecdotes(events, series, btc, k=15, wname='created..end+7d'):
    rows = []
    for e in events:
        a = window_ar(e, AR_WINDOWS[wname], series, btc)
        if a and a['ar_ew'] is not None:
            rows.append({'token': e['token'], 'label': e['label'], 'title': e['title'][:110],
                         'created': utc_iso(e['C'])[:10], 'end': utc_iso(e['E'])[:10], 'outcome': e['outcome'],
                         'surprise': e['surprise'], 'ar_ew': a['ar_ew'], 'ar_btc': a['ar_btc'], 'r': a['r']})
    rows.sort(key=lambda r: -abs(r['ar_ew']))
    return rows[:k]


def capacity(books, tokens):
    """Live depth and impact over the tokens a variant traded (each token counted once)."""
    b = [books[t] for t in sorted(set(tokens)) if t in books]
    if not b:
        return None
    med = lambda k: statistics.median([x[k] for x in b if x.get(k) is not None]) if any(
        x.get(k) is not None for x in b) else None
    def side_min(x, bps):
        v = [x.get('bid_depth_%dbp' % bps), x.get('ask_depth_%dbp' % bps)]
        return min(v) if None not in v else None

    def med_min(bps):
        v = [side_min(x, bps) for x in b if side_min(x, bps) is not None]
        return statistics.median(v) if v else None
    return {'tokens_with_live_book': len(b), 'tokens_traded': len(set(tokens)),
            'median_depth_50bp_min_side': med_min(50), 'median_depth_25bp_min_side': med_min(25),
            'median_impact_bps_25k': med('impact_bps_25k'), 'median_impact_bps_50k': med('impact_bps_50k'),
            'median_impact_bps_100k': med('impact_bps_100k'), 'median_impact_bps_250k': med('impact_bps_250k'),
            'median_quote_volume_24h': med('quote_volume_24h'), 'median_open_interest_usd': med('open_interest_usd')}


def cmd_analyze(args):
    out = Path(args.out)
    man = read_json(out / 'manifest.json', {})
    fz = man.get('labels_frozen')
    if not fz:
        raise SystemExit('labels are not frozen: run label-freeze first')
    if sha256_file(out / 'labels.jsonl') != fz['sha256']:
        raise SystemExit('labels.jsonl changed since it was frozen at %s' % fz['at'])
    started = now_iso()
    cut = args.cutoff or fz['cutoff']
    cut_ms = iso_ms(cut)
    cands = read_jsonl(out / 'candidates.jsonl')
    labels = read_jsonl(out / 'labels.jsonl')
    series = load_series(out, man)
    btc = series['BTC']
    books = (read_json(out / 'raw' / 'books.json', {}) or {}).get('books', {})
    costs, fb = pair_costs(books, sorted(series), args.size)
    costs_alt, fb_alt = pair_costs(books, sorted(series), args.alt_size)
    res = {'generated': now_iso(), 'analysis_started_at': started, 'labels_frozen_at': fz['at'],
           'labels_sha256': fz['sha256'], 'cutoff': cut, 'cutoff_from_freeze': args.cutoff is None,
           'trade_size_usd': args.size, 'cost_fallback_impact_bps': fb, 'ssr': SSR, 'taker_bps': TAKER_BPS,
           'alt_size_usd': args.alt_size, 'cost_fallback_impact_bps_alt': fb_alt,
           'pair_round_trip_bps': {t: c * 1e4 for t, c in costs.items()}, 'by_labeler': {}}
    for key, name in (('label', 'llm'), ('keyword_label', 'keyword')):
        evs = build_events(cands, labels, key)
        value = dedupe_events([e for e in evs if e['label'] in ('VALUE_UP', 'VALUE_DOWN')])
        neutral = dedupe_events([e for e in evs if e['label'] == 'NEUTRAL'])
        priced = [e for e in value if e['token'] in series and series[e['token']].before(e['C']) is not None]
        groups = {'VALUE_UP': [e for e in value if e['label'] == 'VALUE_UP'],
                  'VALUE_DOWN': [e for e in value if e['label'] == 'VALUE_DOWN'], 'NEUTRAL': neutral}
        variants, chosen = run_variants(value, series, btc, costs, cut_ms, args.min_events, costs_alt)
        R = {'events_labeled': len(evs), 'value_events_deduped': len(value), 'value_events_priced': len(priced),
             'priced_by_label': {l: sum(1 for e in priced if e['label'] == l) for l in ('VALUE_UP', 'VALUE_DOWN')},
             'priced_before_cutoff': sum(1 for e in priced if e['C'] < cut_ms),
             'priced_after_cutoff': sum(1 for e in priced if e['C'] >= cut_ms),
             'tokens_priced': sorted({e['token'] for e in priced}),
             'ar': ar_table(groups, series, btc, cut_ms), 'placebo_ar': placebo_ar(value, series, btc, cut_ms),
             'conditional': conditional(value, series, btc, cut_ms=cut_ms), 'by_year': by_year(groups, series, btc),
             'variants': variants, 'chosen': chosen,
             'anecdotes': anecdotes(value, series, btc)}
        R['ar_bh'] = ar_bh(R['ar'])
        if chosen:
            v = next(x for x in variants if (x['window'], x['side'], x['filter']) ==
                     (chosen['window'], chosen['side'], chosen['filter']))
            R['chosen_capacity'] = capacity(books, [t['token'] for t in v['trades_out']])
        for x in variants:                       # the per-trade list is kept for the chosen variant only (file size)
            if not chosen or (x['window'], x['side'], x['filter']) != (chosen['window'], chosen['side'], chosen['filter']):
                x.pop('trades_out', None)
        res['by_labeler'][name] = R
        if name == 'llm':
            audit = []
            for e in value:
                row = {k: e[k] for k in ('id', 'token', 'label', 'title', 'outcome', 'margin', 'surprise', 'confidence',
                                         'binding', 'control')}
                row.update({'created': utc_iso(e['C']), 'start': utc_iso(e['S']), 'end': utc_iso(e['E'])})
                for wname, w in AR_WINDOWS.items():
                    a = window_ar(e, w, series, btc)
                    row['ar_ew_' + wname] = a and a['ar_ew']
                    row['ar_btc_' + wname] = a and a['ar_btc']
                audit.append(row)
            write_jsonl(out / 'events_priced.jsonl', audit)
        c = chosen and next(x for x in variants if (x['window'], x['side'], x['filter']) ==
                            (chosen['window'], chosen['side'], chosen['filter']))
        print(name, 'value events', len(value), 'priced', len(priced), 'chosen',
              c and (c['window'], c['side'], c['filter'], c['n_in'], round(c['in'].get('mean') or 0, 4),
                     round(c['excess_t_in'] or 0, 2), c['n_out'], round(c['out'].get('mean') or 0, 4),
                     c['excess_t_out'] and round(c['excess_t_out'], 2)), flush=True)
    write_json(out / 'analysis.json', res)
    update_manifest(out, analysis={'started_at': started, 'finished_at': now_iso(), 'cutoff': cut})
    return 0


# ------------------------------------------------------------------------------------------------ render

def pct(x, d=2):
    return '—' if x is None else '%+.*f%%' % (d, 100 * x)


def f2(x):
    return '—' if x is None else '%.2f' % x


def cmd_render(args):
    out = Path(args.out)
    A = read_json(out / 'analysis.json')
    man = read_json(out / 'manifest.json', {})
    L = ['# Governance events — tables', '',
         'Generated %s. Labels frozen %s (sha256 %s…); analysis started %s; cutoff %s; pair round trip at $%dk a leg.' % (
             A['generated'], A['labels_frozen_at'], A['labels_sha256'][:12], A['analysis_started_at'], A['cutoff'],
             A['trade_size_usd'] // 1000), '']
    for name in ('llm', 'keyword'):
        R = A['by_labeler'].get(name)
        if not R:
            continue
        L += ['## Labels from the %s' % ('LLM reading (criteria.md)' if name == 'llm' else 'keyword screen alone'), '',
              'Value events after same-day dedupe: %d (priced %d: %s); %d before the cutoff, %d after; %d tokens.' % (
                  R['value_events_deduped'], R['value_events_priced'], R['priced_by_label'],
                  R['priced_before_cutoff'], R['priced_after_cutoff'], len(R['tokens_priced'])), '',
              '### Abnormal log return vs the equal-weight basket (vs BTC in brackets), t by event week', '',
              '| label | window | n | mean | t week | hit | in-sample mean (t wk) | out-of-sample mean (t wk) |',
              '|---|---|---:|---:|---:|---:|---:|---:|']
        for lab in ('VALUE_UP', 'VALUE_DOWN', 'NEUTRAL'):
            for wname in AR_WINDOWS:
                x = R['ar'][lab][wname]
                a, b = x['ar_ew'], x['ar_btc']
                L.append('| %s | %s | %d | %s (%s) | %s | %s | %s (%s) | %s (%s) |' % (
                    lab, wname, a['all'].get('n', 0), pct(a['all'].get('mean')), pct(b['all'].get('mean')),
                    f2(a['all'].get('t_week')), '—' if a['all'].get('hit') is None else '%.0f%%' % (100 * a['all']['hit']),
                    pct(a['in'].get('mean')), f2(a['in'].get('t_week')), pct(a['out'].get('mean')),
                    f2(a['out'].get('t_week'))))
        if R.get('ar_bh'):
            L += ['', 'Benjamini-Hochberg (q = 0.10) over the 14 value-label x window cells, event-week t: full sample %s; '
                      'in sample %s; out of sample %s.' % tuple(', '.join(R['ar_bh'][k]['survivors']) or 'none'
                                                            for k in ('all', 'in', 'out'))]
        pa = R['placebo_ar']
        L += ['', 'Placebo (same token, created..end+7d shifted 15-30 days, away from other value events): ' + '; '.join(
            '%s %s (n %d, t wk %s)' % (lab, pct(pa[lab]['all'].get('mean')), pa[lab]['all'].get('n', 0),
                                       f2(pa[lab]['all'].get('t_week'))) for lab in pa), '',
              '### Trades (pair vs BTC, after funding and costs; excess = over the placebo)', '',
              '| window | side | filter | n in | mean in | placebo in | excess t in | n out | mean out | placebo out | excess t out | t wk out | hit out | over SSR out | BH in | BH out |',
              '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|']
        for v in R['variants']:
            o = v['out']
            L.append('| %s | %s | %s%s | %d | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                v['window'], v['side'], v['filter'], '' if v['tradable'] else ' (look-ahead)', v['n_in'],
                pct(v['in'].get('mean')), pct(v['placebo_mean_in']), f2(v['excess_t_in']), v['n_out'],
                pct(o.get('mean')), pct(v['placebo_mean_out']), f2(v['excess_t_out']), f2(o.get('t_week')),
                '—' if o.get('hit') is None else '%.0f%%' % (100 * o['hit']), pct(v['excess_ssr_out']),
                'yes' if v.get('bh_in') else '', 'yes' if v.get('bh_out') else ''))
        c = R.get('chosen')
        if c:
            L += ['', 'Chosen on events before the cutoff (highest excess-over-placebo t among %d tradable variants, %d '
                      'with enough events): **%s, %s, %s**; deflated Sharpe out of sample %s.' % (
                          c['n_tradable_variants'], c['eligible'], c['window'], c['side'], c['filter'],
                          f2(c['deflated_sharpe_out']))]
        cap = R.get('chosen_capacity')
        if cap:
            L += ['', 'Live books of the tokens the chosen variant traded: median depth within 50bp (thinner side) $%.0fk, '
                      'within 25bp $%.0fk; median impact %s bp at $50k, %s bp at $100k; median 24h volume $%.1fM.' % (
                          (cap['median_depth_50bp_min_side'] or 0) / 1e3, (cap['median_depth_25bp_min_side'] or 0) / 1e3,
                          f2(cap['median_impact_bps_50k']), f2(cap['median_impact_bps_100k']),
                          (cap['median_quote_volume_24h'] or 0) / 1e6)]
        L += ['', '### Conditional (created..end+7d, vs the basket; descriptive, chosen after the split, not tested)', '',
              '| label | split | group | n | mean | t week | hit | in-sample n, mean (t wk) | out-of-sample n, mean (t wk) |',
              '|---|---|---|---:|---:|---:|---:|---:|---:|']
        for lab, d in R['conditional'].items():
            for split, g in d.items():
                for k, x in g.items():
                    xi, xo = x.get('in') or {}, x.get('out') or {}
                    L.append('| %s | %s | %s | %d | %s | %s | %s | %d, %s (%s) | %d, %s (%s) |' % (
                        lab, split, k, x.get('n', 0), pct(x.get('mean')), f2(x.get('t_week')),
                        '—' if x.get('hit') is None else '%.0f%%' % (100 * x['hit']), xi.get('n', 0), pct(xi.get('mean')),
                        f2(xi.get('t_week')), xo.get('n', 0), pct(xo.get('mean')), f2(xo.get('t_week'))))
        if R.get('by_year'):
            L += ['', '### By year of publication (vs the basket)', '', '| label | window | year | n | mean | median | t week |',
                  '|---|---|---|---:|---:|---:|---:|']
            for lab in ('VALUE_UP', 'VALUE_DOWN', 'NEUTRAL'):
                for wname, d in R['by_year'].get(lab, {}).items():
                    for y, x in d.items():
                        L.append('| %s | %s | %s | %d | %s | %s | %s |' % (lab, wname, y, x.get('n', 0), pct(x.get('mean')),
                                                                     pct(x.get('median_ar')), f2(x.get('t_week'))))
        L += ['', '### Largest moves (created..end+7d, vs the basket)', '',
              '| token | label | created | end | outcome | first? | AR vs basket | AR vs BTC | title |',
              '|---|---|---|---|---|---|---:|---:|---|']
        for a in R['anecdotes']:
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                a['token'], a['label'], a['created'], a['end'], a['outcome'], 'yes' if a['surprise'] else 'no',
                pct(a['ar_ew'], 1), pct(a['ar_btc'], 1), a['title'].replace('|', '/')))
        L.append('')
    ag = read_json(out / 'label_agreement.json')
    if ag:
        L += ['## Labeling', '', 'Blind spot check: %d proposals, agreement %.0f%%, Cohen kappa %s; surprise flag agreement %s. '
              'Keyword-only classifier vs the LLM on all %d candidates: agreement %.0f%%, kappa %s.' % (
                  ag['spot_n'], 100 * (ag['agreement'] or 0), f2(ag['kappa']),
                  '—' if ag.get('surprise_agreement') is None else '%.0f%%' % (100 * ag['surprise_agreement']),
                  ag['keyword_vs_llm']['n'], 100 * ag['keyword_vs_llm']['agreement'], f2(ag['keyword_vs_llm']['kappa'])),
              '', 'LLM labels of the random control sample (proposals the screen missed): %s; of the screen hits: %s.' % (
                  ag['controls']['llm_labels'], ag['screen_hits']['llm_labels']), '']
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:40]))
    return 0


# ------------------------------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect', help='every proposal of every mapped Snapshot space'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True); c.add_argument('--interval', type=float, default=1.1)
    c.add_argument('--force', action='store_true')
    s = sub.add_parser('screen', help='keyword screen + random control sample -> candidates.jsonl')
    s.set_defaults(fn=cmd_screen)
    s.add_argument('--out', required=True); s.add_argument('--since', default='2021-01-01')
    s.add_argument('--until', default='2026-10-01'); s.add_argument('--controls', type=int, default=200)
    e = sub.add_parser('label-export', help='LLM packets (title + first 1,500 chars, no prices) and the spot sample')
    e.set_defaults(fn=cmd_label_export)
    e.add_argument('--out', required=True); e.add_argument('--batch-size', type=int, default=120)
    e.add_argument('--spot-frac', type=float, default=0.10)
    f = sub.add_parser('label-freeze', help='validate the labels, write labels.jsonl, stamp time + hash + cutoff')
    f.set_defaults(fn=cmd_label_freeze)
    f.add_argument('--out', required=True); f.add_argument('--force', action='store_true')
    k = sub.add_parser('label-check', help="validate one labeler's output against its batch")
    k.set_defaults(fn=cmd_label_check)
    k.add_argument('--out', required=True); k.add_argument('--batch', required=True, help="'07', 'spot_a' or 'spot_b'")
    g = sub.add_parser('label-agree', help='blind spot-check agreement and keyword-vs-LLM agreement')
    g.set_defaults(fn=cmd_label_agree); g.add_argument('--out', required=True)
    q = sub.add_parser('prices', help='Binance USDⓈ-M 4h klines and funding per token (cached)')
    q.set_defaults(fn=cmd_prices)
    q.add_argument('--out', required=True); q.add_argument('--since', default='2020-09-01')
    q.add_argument('--interval', type=float, default=0.35); q.add_argument('--force', action='store_true')
    q.add_argument('--reverse', action='store_true', help='walk the tokens from the end (a second downloader)')
    b = sub.add_parser('books', help='live Binance books, 24h volume and open interest for capacity')
    b.set_defaults(fn=cmd_books)
    b.add_argument('--out', required=True); b.add_argument('--interval', type=float, default=0.4)
    a = sub.add_parser('analyze', help='event study and trade test; refuses to run on unfrozen labels')
    a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True); a.add_argument('--cutoff', default=None,
                                                          help='override the cutoff fixed at the freeze (reported)')
    a.add_argument('--size', type=int, default=25_000, help='USD a leg for the cost model (median live impact at '
                   '$100k was 68bp one way on 2026-10-10, so $25k is the primary size)')
    a.add_argument('--alt-size', type=int, default=100_000, help='a second size, reported as a cost sensitivity')
    a.add_argument('--min-events', type=int, default=15)
    r = sub.add_parser('render', help='tables.md from analysis.json'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
