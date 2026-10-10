#!/usr/bin/env python3
"""Chain probes: how many transactions a chain carried in a window, and how much of each asset moved through it.

Why a family of adapters. "Transactions" and "volume" mean different things on an EVM rollup, on Solana, on a UTXO
chain and on a Cosmos zone, and the cheapest honest way to count them differs too. Some chains publish a cumulative
transaction counter (Sui checkpoints, Aptos ledger versions, Solana `getTransactionCount`), so a count over any window is
exact for two reads. Most do not, so the count is estimated from a stratified sample of blocks, and the estimate carries
its standard error. Every adapter returns the same shape and says which of the two it did:

    {"tx":        {"count": N, "se": s, "method": "exact-counter" | "exact-blocks" | "sampled-blocks", ...},
     "transfers": {"method": ..., "assets": [{"asset", "symbol", "class", "transfers", "amount", "usd", "usd_se", ...}]},
     "window": {...}, "endpoint": ..., "errors": [...]}

Transfer value is *net per transaction*: within one transaction, each account's net change in an asset is summed over
the accounts that gained (`net_positive`). A plain transfer counts once, a router hop that receives and forwards counts
nothing, a flash loan counts its fee, and a swap counts both legs. That is what balance-delta chains (Solana, Sui,
Hedera) report natively, so it is the one definition every family can meet, and it is the one that survives sampling:
the first EVM sweep summed raw `Transfer` logs instead, and one Base block of flash-loan loops scaled to "$666B a day"
of WETH. The raw sum is still kept as `gross_usd` where an adapter has it. Neither is economic volume — that comes from
DefiLlama's DEX adapters in `chain_census.py`. Prices come from one feed (DefiLlama's coins API) keyed by chain and
contract, so a token that only *calls itself* USDT is not priced as one.

Sampling. A window of N blocks is split into n equal strata and one block is read from each, at an offset seeded by the
window so a re-run reads the same blocks. The total is N times the sample mean and its standard error comes from the
successive-difference estimator, which is the standard one for a systematic sample. Transfer value is heavy-tailed — one
$80M block can carry a day — so each asset also reports the share of its sampled value that came from its single largest
block (`top_block_share`); above one half the estimate is one transfer scaled up, and the detectors treat it as such.
"""
import gzip
import hashlib
import http.client
import importlib
import json
import math
import random
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) llm-quant research (read-only)'

FAMILIES = {}
HISTORY = {}     # family -> history(cfg, ctx, day_starts, samples) -> [{day, count, se, method, ...}], where cheaper than per-day probes


def register(family):
    def deco(fn):
        FAMILIES[family] = fn
        return fn
    return deco


def register_history(family):
    def deco(fn):
        HISTORY[family] = fn
        return fn
    return deco


def load_all():
    """Import every adapter module so each registers its family."""
    for p in sorted(Path(__file__).resolve().parent.glob('*.py')):
        if p.stem != '__init__' and not p.stem.startswith('_'):
            importlib.import_module('chain_adapters.' + p.stem)
    return FAMILIES


# ---------------------------------------------------------------------------------------------- transport

class HttpError(Exception):
    def __init__(self, code, body=''):
        super().__init__('HTTP %s %s' % (code, str(body)[:160]))
        self.code = code
        self.body = body


class RpcError(Exception):
    """The endpoint answered with a JSON-RPC error object: a result, not a transport failure."""

    def __init__(self, err):
        super().__init__(json.dumps(err)[:300] if not isinstance(err, str) else err[:300])
        self.err = err
        self.code = err.get('code') if isinstance(err, dict) else None


def redact(s, secrets=()):
    s = str(s)
    for k in secrets:
        if k:
            s = s.replace(k, '[KEY]')
    return s


class Http:
    """JSON over HTTP with a browser User-Agent, gzip, retries with backoff, and a minimum spacing per host.

    The spacing is the whole rate-limit policy: public explorers answer 429 to bursts long before they answer it to a
    steady request rate, and a probe that is slow but finishes is worth more than one that is fast and half empty.
    """

    def __init__(self, min_interval=0.0, timeout=45, retries=4, secrets=()):
        self.min_interval = min_interval
        self.timeout = timeout
        self.retries = retries
        self.secrets = tuple(secrets)
        self.lock = threading.Lock()
        self.next_at = {}
        self.requests = 0
        self.bytes = 0
        self.errors = []
        self.host_interval = {}

    def _wait(self, host):
        gap = self.host_interval.get(host, self.min_interval)
        if gap <= 0:
            return
        with self.lock:
            now = time.monotonic()
            at = max(now, self.next_at.get(host, 0.0))
            self.next_at[host] = at + gap
        if at > now:
            time.sleep(at - now)

    def request(self, url, body=None, headers=None, timeout=None):
        host = urllib.parse.urlsplit(url).netloc
        h = {'User-Agent': UA, 'Accept': 'application/json', 'Accept-Encoding': 'gzip'}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h['Content-Type'] = 'application/json'
        h.update(headers or {})
        last = None
        for attempt in range(self.retries):
            self._wait(host)
            req = urllib.request.Request(url, data=data, headers=h)
            try:
                with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                    raw = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        raw = gzip.decompress(raw)
                with self.lock:
                    self.requests += 1
                    self.bytes += len(raw)
                return json.loads(raw)
            except urllib.error.HTTPError as e:
                try:
                    body = e.read()
                    if body[:2] == b'\x1f\x8b':
                        body = gzip.decompress(body)
                    txt = body[:400].decode('utf-8', 'replace')
                except Exception:
                    txt = ''
                last = HttpError(e.code, redact(txt, self.secrets))
                if e.code in (429, 500, 502, 503, 504, 520, 522, 524):
                    time.sleep(min(20, 1.5 * 2 ** attempt))
                    continue
                raise last
            except (http.client.IncompleteRead, http.client.RemoteDisconnected, ConnectionResetError, TimeoutError,
                    urllib.error.URLError, json.JSONDecodeError) as e:
                last = e
                time.sleep(min(10, 0.8 * 2 ** attempt))
        with self.lock:
            self.errors.append(redact('%s: %s' % (host, last), self.secrets)[:240])
        if isinstance(last, HttpError):
            raise last
        raise HttpError('transport', redact(str(last), self.secrets))

    def get(self, url, params=None, **kw):
        if params:
            url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        return self.request(url, **kw)

    def post(self, url, body, **kw):
        return self.request(url, body=body, **kw)

    def stats(self):
        return {'requests': self.requests, 'bytes': self.bytes, 'errors': len(self.errors)}


class JsonRpc:
    """JSON-RPC over an ordered list of endpoints.

    Endpoints are tried in order and one that fails at the transport level is parked for a minute, so a dead public
    node costs one timeout rather than one per call. Batching is detected per endpoint: several public nodes answer a
    batch with an error object or a 403, and those are then driven one call at a time.
    """

    def __init__(self, urls, http=None, batch_size=20, label=None, secrets=()):
        self.urls = [u for u in urls if u]
        if not self.urls:
            raise ValueError('no endpoints')
        self.http = http or Http()
        self.batch_size = batch_size
        self.label = label
        self.secrets = tuple(secrets)
        self.parked = {}
        self.no_batch = set()
        self.lock = threading.Lock()
        self.calls = 0

    def endpoint(self):
        now = time.monotonic()
        for u in self.urls:
            if self.parked.get(u, 0) <= now:
                return u
        return min(self.urls, key=lambda u: self.parked.get(u, 0))

    def _park(self, u, seconds=60):
        with self.lock:
            self.parked[u] = time.monotonic() + seconds

    def public_name(self, u=None):
        return redact(u or self.endpoint(), self.secrets)

    def call(self, method, params=None):
        last = None
        for _ in range(max(2, len(self.urls) + 1)):
            u = self.endpoint()
            try:
                d = self.http.post(u, {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params if params is not None else []})
            except HttpError as e:
                last = e
                self._park(u, 30 if e.code == 429 else 90)
                continue
            with self.lock:
                self.calls += 1
            if isinstance(d, dict) and 'error' in d and d['error']:
                err = d['error']
                msg = str(err.get('message', '') if isinstance(err, dict) else err).lower()
                if 'rate' in msg or 'limit exceeded' in msg or 'too many' in msg or (isinstance(err, dict) and err.get('code') in (-32005, 429, -32429)):
                    last = RpcError(err)
                    self._park(u, 20)
                    continue
                raise RpcError(err)
            if not isinstance(d, dict) or 'result' not in d:
                last = RpcError({'message': 'malformed response', 'body': str(d)[:200]})
                self._park(u, 30)
                continue
            return d['result']
        raise last or RpcError('all endpoints failed')

    def batch(self, calls, allow_errors=True):
        """Results in input order; with allow_errors, a failed member is {'error': ...} rather than an exception."""
        out = []
        for i in range(0, len(calls), self.batch_size):
            out += self._batch(calls[i:i + self.batch_size], allow_errors)
        return out

    def _batch(self, part, allow_errors):
        u = self.endpoint()
        if u not in self.no_batch and len(part) > 1:
            payload = [{'jsonrpc': '2.0', 'id': i, 'method': m, 'params': p} for i, (m, p) in enumerate(part)]
            try:
                d = self.http.post(u, payload)
                if isinstance(d, list):
                    by = {x.get('id'): x for x in d if isinstance(x, dict)}
                    if all(i in by for i in range(len(part))):
                        with self.lock:
                            self.calls += len(part)
                        res = []
                        for i in range(len(part)):
                            x = by[i]
                            if x.get('error'):
                                if not allow_errors:
                                    raise RpcError(x['error'])
                                res.append({'error': x['error']})
                            else:
                                res.append(x.get('result'))
                        # a batch can come back as one error per member when the node rate-limits batches
                        if not (allow_errors and all(isinstance(r, dict) and 'error' in r for r in res)):
                            return res
                self.no_batch.add(u)
            except HttpError as e:
                if e.code == 429:
                    self._park(u, 20)
                else:
                    self.no_batch.add(u)
        res = []
        for m, p in part:
            try:
                res.append(self.call(m, p))
            except (RpcError, HttpError) as e:
                if not allow_errors:
                    raise
                res.append({'error': getattr(e, 'err', None) or str(e)})
        return res


def is_err(x):
    return isinstance(x, dict) and 'error' in x and len(x) == 1


# ---------------------------------------------------------------------------------------------- sampling

def sample_points(first, last, n, seed=0):
    """n stratified points over the integer range [first, last]: equal strata, one point per stratum.

    The offset inside each stratum is drawn from a generator seeded by `seed` (the window start), so the same window is
    always read at the same blocks and two runs of the probe are comparable block for block.
    """
    span = last - first + 1
    if span <= 0:
        return []
    if span <= n:
        return list(range(first, last + 1))
    rng = random.Random(seed)
    width = span / n
    pts = []
    for h in range(n):
        lo = first + int(math.floor(h * width))
        hi = first + int(math.floor((h + 1) * width)) - 1
        pts.append(rng.randint(lo, max(lo, hi)))
    return pts


def stratified_total(values, N):
    """(total, standard error) over N units from one sampled unit per equal stratum, in stratum order.

    Successive-difference variance (Wolter): v(mean) = (1 - n/N) / n * sum((y[i+1]-y[i])^2) / (2(n-1)). With every unit
    read (n == N) the total is exact and the error is zero.
    """
    n = len(values)
    if n == 0:
        return None, None
    mean = sum(values) / n
    total = N * mean
    if n >= N:
        return float(sum(values)), 0.0
    if n < 2:
        return total, None
    ssd = sum((values[i + 1] - values[i]) ** 2 for i in range(n - 1))
    v = (1.0 - n / N) / n * ssd / (2.0 * (n - 1))
    return total, N * math.sqrt(max(v, 0.0))


def top_share(values):
    s = sum(v for v in values if v > 0)
    return (max(values) / s) if s > 0 else None


# ---------------------------------------------------------------------------------------------- pricing

USD_STABLES = {
    'USDT', 'USDC', 'USDC.E', 'USDCE', 'USDBC', 'USDT0', 'USD₮0', 'USD₮', 'DAI', 'USDS', 'USDE', 'SUSDE', 'FDUSD', 'PYUSD',
    'RLUSD', 'USDG', 'USDTB', 'FRAX', 'FRXUSD', 'LUSD', 'BOLD', 'CRVUSD', 'GHO', 'TUSD', 'USDP', 'USD1', 'USDD', 'BUSD',
    'USDB', 'USDA', 'AUSD', 'DOLA', 'MIM', 'USDX', 'USDH', 'USDHL', 'USDXL', 'USDM', 'MUSD', 'USDF', 'USDL', 'USDY', 'XUSD',
    'USD0', 'SRUSD', 'RUSD', 'DEUSD', 'EUSD', 'CUSD', 'USDZ', 'USDN', 'BUIDL', 'USTB', 'USDO', 'USDAF', 'HOLLAR', 'USDTZ',
    'DJED', 'IUSD', 'USDCX', 'USDSUI', 'OUSD', 'PATHUSD', 'USDC.E', 'AUSD', 'PUSD', 'USDM', 'USDT0',
}
EUR_STABLES = {'EURC', 'EURE', 'EURS', 'AGEUR', 'EURA', 'EURCV', 'EURR', 'EUROC', 'VEUR'}
BTC_LIKE = {'BTC', 'WBTC', 'CBBTC', 'BTCB', 'TBTC', 'LBTC', 'SOLVBTC', 'UBTC', 'KBTC', 'FBTC', 'EBTC', 'PUMPBTC', 'UNIBTC',
            'BTC.B', 'XBTC', 'ZBTC', 'SBTC', 'ENZOBTC', 'UNIBTC', 'BTCN', 'IBTC', 'OBTC', 'STBTC', 'XSOLVBTC', 'BBTC',
            'STRKBTC', 'CIRBTC', 'TZBTC'}
ETH_LIKE = {'ETH', 'WETH', 'STETH', 'WSTETH', 'RETH', 'CBETH', 'WEETH', 'EZETH', 'RSETH', 'METH', 'OETH', 'SFRXETH',
            'FRXETH', 'ETHX', 'OSETH', 'SWETH', 'PUFETH', 'WRSETH', 'WEETHS', 'SUPEROETHB', 'ETH+', 'MSETH'}


def asset_class(symbol, native_symbols=()):
    s = (symbol or '').upper().strip()
    if s in USD_STABLES:
        return 'usd_stable'
    if s in EUR_STABLES:
        return 'eur_stable'
    if s in BTC_LIKE:
        return 'btc'
    if s in ETH_LIKE:
        return 'eth'
    if s in {x.upper() for x in native_symbols} or (s.startswith('W') and s[1:] in {x.upper() for x in native_symbols}):
        return 'native'
    return 'other'


class Prices:
    """DefiLlama coins API, batched and memoised: keys are 'coingecko:<id>' or '<llama chain key>:<address>'.

    A price is kept only with confidence >= MIN_CONFIDENCE: the feed assigns low confidence to prices it read from thin
    pools, which is exactly where a spam token with a fake USD value would come from.
    """
    URL = 'https://coins.llama.fi/prices/current/'
    MIN_CONFIDENCE = 0.8

    def __init__(self, http=None, cache=None):
        self.http = http or Http(min_interval=0.25)
        self.cache = {}
        self.cache_path = Path(cache) if cache else None
        self.lock = threading.Lock()
        if self.cache_path and self.cache_path.exists():
            try:
                self.cache = json.loads(self.cache_path.read_text())
            except Exception:
                self.cache = {}

    def get(self, keys):
        want = [k for k in dict.fromkeys(keys) if k and k not in self.cache]
        for i in range(0, len(want), 60):
            part = want[i:i + 60]
            url = self.URL + ','.join(urllib.parse.quote(k, safe=':') for k in part) + '?searchWidth=6h'
            try:
                d = self.http.get(url)
            except HttpError:
                d = {}
            coins = (d or {}).get('coins') or {}
            with self.lock:
                for k in part:
                    c = coins.get(k)
                    if c is None:
                        # keys are case-sensitive on base58 chains but not on EVM ones; the feed answers in its own case
                        c = next((v for kk, v in coins.items() if kk.lower() == k.lower()), None)
                    self.cache[k] = c if (c and (c.get('confidence') or 0) >= self.MIN_CONFIDENCE) else None
        if self.cache_path:
            with self.lock:
                self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                self.cache_path.write_text(json.dumps(self.cache, sort_keys=True))
        return {k: self.cache.get(k) for k in keys}

    def one(self, key):
        return self.get([key]).get(key)


# ---------------------------------------------------------------------------------------------- result helpers

def utc(ts):
    import datetime as dt
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec='seconds')


def window_dict(start_ts, end_ts):
    return {'start_ts': int(start_ts), 'end_ts': int(end_ts), 'start_utc': utc(start_ts), 'end_utc': utc(end_ts),
            'hours': round((end_ts - start_ts) / 3600.0, 4)}


def net_positive(moves):
    """Net transfer value of one transaction for one asset: the sum of every account's positive net change.

    moves: iterable of (from, to, amount). A transfer A->B of X counts X; a router that receives X and forwards X nets
    to zero and counts nothing; a flash loan that lends X and is repaid X plus a fee counts the fee. This is the quantity
    a balance-delta chain (Solana's pre/post token balances, Sui's balance changes, Hedera's transfer lists) reports
    natively, so measuring EVM logs the same way makes the chains comparable — and it is what stops one block of
    flash-loan loops from being scaled into hundreds of billions of "volume".
    """
    net = {}
    for frm, to, v in moves:
        if frm == to:
            continue
        net[frm] = net.get(frm, 0) - v
        net[to] = net.get(to, 0) + v
    return sum(x for x in net.values() if x > 0)


def asset_rows(per_asset, n_units, N_units, meta, price_of, native_symbols=(), min_usd=0.0):
    """Turn per-sampled-unit sums into estimated totals.

    per_asset: {asset_id: {'count': [per unit], 'amount': [per unit, already in token units], 'gross': [optional,
    per unit]}}, lists aligned with the sampled units (zeros where the asset did not appear). `amount` is the headline
    and should be *net per transaction* (see `net_positive`) where the chain exposes transfers rather than balance
    deltas; `gross` (every transfer, every hop) is kept beside it when the adapter has it. meta: {asset_id: {'symbol',
    'decimals'}}. price_of: {asset_id: price-or-None}.
    """
    rows, unpriced = [], []
    gross_total = 0.0
    for a, d in per_asset.items():
        cnt = d['count'] + [0] * (n_units - len(d['count']))
        amt = d['amount'] + [0.0] * (n_units - len(d['amount']))
        transfers, transfers_se = stratified_total(cnt, N_units)
        amount, amount_se = stratified_total(amt, N_units)
        m = meta.get(a) or {}
        p = price_of.get(a)
        sym = m.get('symbol')
        row = {'asset': a, 'symbol': sym, 'class': asset_class(sym, native_symbols),
               'transfers': round(transfers or 0), 'transfers_se': round(transfers_se) if transfers_se is not None else None,
               'amount': amount, 'price': p,
               'usd': (amount * p) if (p is not None and amount is not None) else None,
               'usd_se': (amount_se * p) if (p is not None and amount_se is not None) else None,
               'top_block_share': top_share(amt), 'units_seen': sum(1 for x in cnt if x)}
        if d.get('gross') is not None:
            gr = d['gross'] + [0.0] * (n_units - len(d['gross']))
            g, _ = stratified_total(gr, N_units)
            row['gross_amount'] = g
            row['gross_usd'] = (g * p) if (p is not None and g is not None) else None
            gross_total += row['gross_usd'] or 0.0
        (rows if p is not None else unpriced).append(row)
    rows.sort(key=lambda r: -(r['usd'] or 0))
    unpriced.sort(key=lambda r: -(r['transfers'] or 0))
    priced_total = sum(r['usd'] or 0 for r in rows)
    by_class = {}
    for r in rows:
        by_class[r['class']] = by_class.get(r['class'], 0.0) + (r['usd'] or 0.0)
    out = {'assets': [r for r in rows if (r['usd'] or 0) >= min_usd],
           'unpriced_top': unpriced[:25], 'unpriced_assets': len(unpriced),
           'unpriced_transfers': sum(r['transfers'] for r in unpriced),
           'priced_usd': priced_total, 'usd_by_class': by_class}
    if any(d.get('gross') is not None for d in per_asset.values()):
        out['gross_priced_usd'] = gross_total
    return out


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def b58check(payload):
    """Base58Check (double-SHA256 checksum), as Tron addresses use."""
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    raw = payload + chk
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(raw, 'big')
    out = ''
    while n:
        n, r = divmod(n, 58)
        out = alphabet[r] + out
    pad = len(raw) - len(raw.lstrip(b'\x00'))
    return '1' * pad + out


HEX_RE = re.compile(r'^0x[0-9a-fA-F]*$')
