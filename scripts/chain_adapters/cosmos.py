#!/usr/bin/env python3
"""Cosmos-SDK zones over CometBFT RPC: transactions from block headers, transfer value from block results.

Counting. `/blockchain?minHeight=&maxHeight=` returns up to 20 block headers per call, each with its exact `num_txs`, so
the unit of sampling is a run of 20 consecutive blocks and one call reads one unit. When the whole window fits in the
call budget every run is read and the count is exact (`exact-blocks`). Otherwise a node that indexes transactions is
asked for the count over the height range in one `tx_search` call (`exact-index`; Noble's own RPC answers, the public
load balancers refuse ranges), and failing that runs are drawn from equal strata and the count carries the
successive-difference standard error (`sampled-blocks`). On 2026-10-09 the sampled 24-hour estimates sat within one
standard error of exact counts (Cosmos Hub 18,163 ± 421 vs 17,907; THORChain 209,944 ± 8,624 vs 206,465; Noble
2,532 ± 346 vs 2,750). `num_txs` counts every transaction the block included, successful or not; the failed share
comes from the block results.

Value. `/block_results?height=` for a sample of single heights gives every transaction's events, and the bank module
emits one `transfer` event (`sender`, `recipient`, `amount` as a coin list such as `123uosmo,45ibc/27..`) per send.
The headline table counts only *transaction-level* transfers of successful transactions, less the fee leg (the
recipient is the `fee_collector` module, whose address is derived on the spot from sha256("fee_collector") and the
chain's bech32 prefix rather than remembered), and it counts them *net per transaction*: the legs of one transaction
in one denom are netted account by account (`net_positive`), so a swap routed through three pools counts what the
trader paid and received, not every pool leg; the every-leg sum is kept as `gross_amount`. Block-level transfers — `finalize_block_events` on CometBFT 0.38,
`begin/end_block_events` before it — are kept in a separate table (`transfers.block_level`) with the staking and
inflation plumbing (fee_collector, distribution, mint, bonded/not-bonded pools, gov) removed, because on some zones
that is where the activity settles: THORChain executes swaps and outbounds in its end blocker, so its transaction-level
table sees deposits and sends but not the swaps themselves.

Identity. Denominations are named from the chain's own entry in the cosmos/chain-registry assetlist (symbol, decimal
exponent, CoinGecko id), then from an IBC denom trace read from the chain's REST endpoint when a voucher is not listed,
then from the registry's `denoms`; Injective's `peggy0x...` denoms are Ethereum ERC-20s and are priced as such.
Anything still unidentified is counted but not priced. Prices come from the shared DefiLlama feed.

Endpoints. Public CometBFT nodes prune aggressively (a Celestia node seen keeping 2.5 hours) and some refuse
`block_results` or range queries, so each endpoint's `earliest_block_height` is read from `/status` and a call goes to
the first endpoint that holds the height; the registry's endpoints come first, the fallbacks below after.
"""
import base64
import binascii
import concurrent.futures as cf
import datetime as dt
import hashlib
import math
import re
import time

from chain_adapters import (Http, HttpError, asset_rows, net_positive, register, sample_points, stratified_total,
                            window_dict)

RUN = 20                    # /blockchain returns at most 20 headers per call
EXACT_RUN_BUDGET = 800      # read every run (exact count) when the window needs at most this many calls (16k blocks:
                            # a 6-second chain's whole day, ~30 s at four workers)
TX_SEARCH_TIMEOUT = 15      # seconds; a node that indexes transactions can count a height range in one call
DEFAULT_RUN_SAMPLES = 300   # otherwise sample this many runs (6,000 blocks; Osmosis is bursty)
DEFAULT_VALUE_SAMPLES = 120  # single heights read through /block_results
MAX_TRACE_LOOKUPS = 15      # IBC denom traces resolved through REST per probe
CHAIN_REGISTRY = 'https://raw.githubusercontent.com/cosmos/chain-registry/master/%s/assetlist.json'

# Fallbacks verified 2026-10-09: rpc.cosmos.directory proxies every zone below (but answers 500 to block_results on
# Celestia); publicnode's Noble host is gone (404), its Celestia host keeps ~2.5 h; ninerealms no longer resolves.
FALLBACK_RPC = {
    'osmosis': ['https://osmosis-rpc.publicnode.com', 'https://rpc.cosmos.directory/osmosis'],
    'injective': ['https://injective-rpc.publicnode.com', 'https://rpc.cosmos.directory/injective'],
    'cosmoshub': ['https://cosmos-rpc.publicnode.com', 'https://rpc.cosmos.directory/cosmoshub'],
    'dydx': ['https://dydx-rpc.publicnode.com', 'https://rpc.cosmos.directory/dydx'],
    'celestia': ['https://rpc.celestia.pops.one', 'https://celestia.rpc.kjnodes.com', 'https://celestia-rpc.publicnode.com'],
    'noble': ['https://rpc.noble.xyz', 'https://noble-rpc.polkachu.com', 'https://rpc.lavenderfive.com:443/noble',
              'https://rpc.cosmos.directory/noble'],
    'thorchain': ['https://rpc.cosmos.directory/thorchain'],
}
FALLBACK_REST = {
    'osmosis': ['https://osmosis-rest.publicnode.com', 'https://rest.cosmos.directory/osmosis'],
    'injective': ['https://injective-rest.publicnode.com', 'https://rest.cosmos.directory/injective'],
    'cosmoshub': ['https://cosmos-rest.publicnode.com', 'https://rest.cosmos.directory/cosmoshub'],
    'dydx': ['https://dydx-rest.publicnode.com', 'https://rest.cosmos.directory/dydx'],
    'celestia': ['https://celestia-rest.publicnode.com', 'https://rest.cosmos.directory/celestia'],
    'noble': ['https://rest.cosmos.directory/noble'],
    'thorchain': ['https://rest.cosmos.directory/thorchain'],
}
# Module accounts whose transfers are protocol plumbing (fees, inflation, staking), not activity.
PLUMBING_MODULES = ('fee_collector', 'distribution', 'mint', 'bonded_tokens_pool', 'not_bonded_tokens_pool', 'gov')
# Base denominations an IBC trace can resolve to, beyond what the assetlists already name: (symbol, exponent, coingecko).
KNOWN_BASE = {
    'uusdc': ('USDC', 6, 'usd-coin'), 'uatom': ('ATOM', 6, 'cosmos'), 'uosmo': ('OSMO', 6, 'osmosis'),
    'utia': ('TIA', 6, 'celestia'), 'adydx': ('DYDX', 18, 'dydx-chain'), 'inj': ('INJ', 18, 'injective-protocol'),
    'untrn': ('NTRN', 6, 'neutron-3'), 'ustrd': ('STRD', 6, 'stride'), 'uakt': ('AKT', 6, 'akash-network'),
    'uaxl': ('AXL', 6, 'axelar'), 'ukava': ('KAVA', 6, 'kava'), 'uscrt': ('SCRT', 6, 'secret'),
    'ujuno': ('JUNO', 6, 'juno-network'), 'uluna': ('LUNA', 6, 'terra-luna-2'), 'ustars': ('STARS', 6, 'stargaze'),
    'weth-wei': ('ETH', 18, 'ethereum'), 'wbtc-satoshi': ('WBTC', 8, 'wrapped-bitcoin'), 'rune': ('RUNE', 8, 'thorchain'),
    'stuatom': ('stATOM', 6, 'stride-staked-atom'), 'stutia': ('stTIA', 6, 'stride-staked-tia'),
    'ubbn': ('BABY', 6, 'babylon'), 'uom': ('OM', 6, 'mantra-dao'), 'uusdt': ('USDT', 6, 'tether'),
    'dai-wei': ('DAI', 18, 'dai'), 'wbnb-wei': ('WBNB', 18, 'binancecoin'), 'wavax-wei': ('WAVAX', 18, 'avalanche-2'),
    'dot-planck': ('DOT', 10, 'polkadot'), 'uumee': ('UMEE', 6, 'umee'),
}
# Alloyed and synthetic assets trace to a non-Cosmos chain's own unit: (chain_name, base unit) -> CoinGecko id.
NATIVE_TRACE = {('bitcoin', 'sat'): 'bitcoin', ('ethereum', 'wei'): 'ethereum', ('xrpl', 'drop'): 'ripple',
                ('solana', 'lamport'): 'solana', ('dogecoin', 'koinu'): 'dogecoin', ('litecoin', 'litoshi'): 'litecoin',
                ('tron', 'sun'): 'tron', ('avalanche', 'wei'): 'avalanche-2', ('binancesmartchain', 'wei'): 'binancecoin'}
# THORChain names L1 assets as <CHAIN>-<SYMBOL>[-<contract>] (secured), <chain>/<symbol> (synth) or <chain>~<symbol>
# (trade), always with 8 decimals.
THOR_SYMBOL_CG = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'USDC': 'usd-coin', 'USDT': 'tether', 'BNB': 'binancecoin', 'AVAX': 'avalanche-2',
    'ATOM': 'cosmos', 'DOGE': 'dogecoin', 'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'XRP': 'ripple', 'SOL': 'solana',
    'TRX': 'tron', 'WBTC': 'wrapped-bitcoin', 'CBBTC': 'coinbase-wrapped-btc', 'DAI': 'dai', 'RUNE': 'thorchain',
    'TCY': 'tcy', 'RUJI': 'rujira',
}
CHAIN_NOTES = {
    'dydx': 'dYdX short-term orders are gossiped off-chain and only matched fills enter a block (one proposer '
            'operations transaction); the count is placements of long-term/conditional orders, cancels, transfers and '
            'that one operations transaction per block, not order flow. Fills settle in subaccount state and emit no '
            'bank transfer events, so transfer value is deposits, withdrawals and transfers only.',
    'thorchain': 'THORChain executes swaps, outbounds and liquidity actions in its end blocker: transaction-level '
                 'transfers are inbound deposits and sends; the swaps are in transfers.block_level.',
    'celestia': 'Most Celestia transactions are PayForBlobs from rollup sequencers; their value is the blob fee, not a '
                'transfer.',
    'injective': 'Injective order-book trades settle in the end blocker; transaction-level transfers are deposits, '
                 'sends and contract calls, and block-level settlement is in transfers.block_level.',
    'osmosis': 'Osmosis transaction-level transfers include every pool leg of a routed swap and ProtoRev back-runs.',
    'noble': 'Noble is the USDC issuer for IBC: most transfers are IBC receives/sends of uusdc.',
}

COIN_RE = re.compile(r'^(\d+)([a-zA-Z][a-zA-Z0-9/:._\-]{1,127})$')
_B64_RE = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')


# ---------------------------------------------------------------------------------------------- pure helpers

def parse_coins(s):
    """'123uosmo,45ibc/27AB..' -> [(123, 'uosmo'), (45, 'ibc/27AB..')]. Malformed members are dropped, not guessed."""
    out = []
    for part in (s or '').split(','):
        part = part.strip()
        if not part:
            continue
        m = COIN_RE.match(part)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


def _maybe_b64(s):
    """Decode a base64 attribute (CometBFT <= 0.34 encodes keys and values); leave plain text alone."""
    if not isinstance(s, str) or not s or len(s) % 4 or not _B64_RE.match(s):
        return s
    try:
        b = base64.b64decode(s, validate=True)
        t = b.decode('utf-8')
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return s
    return t if t.isprintable() else s


def event_attrs(ev):
    """[(key, value)] in order, base64-decoded when the node encodes them. A key is decoded only when its decoded form
    is a plausible attribute name, so a plain value that happens to be valid base64 ('test', 'amount') is not mangled."""
    out = []
    for a in ev.get('attributes') or []:
        k, v = a.get('key'), a.get('value')
        dk = _maybe_b64(k)
        if dk != k and re.match(r'^[a-z_][a-z0-9_.]*$', dk or ''):
            k, v = dk, _maybe_b64(v) if v is not None else v
        out.append((k, v))
    return out


def transfer_legs(ev):
    """(sender, recipient, [(amount, denom)]) per send in a `transfer` event.

    SDK >= 0.47 emits one send per event; older SDKs could append several sends' attributes to one event, so a new leg
    starts whenever an attribute repeats."""
    legs, cur = [], {}
    for k, v in event_attrs(ev):
        if k in ('recipient', 'sender', 'amount'):
            if k in cur:            # a repeated key opens the next send, whichever order the SDK wrote them in
                legs.append(cur)
                cur = {}
            cur[k] = v
    if cur:
        legs.append(cur)
    return [(l.get('sender'), l.get('recipient'), parse_coins(l.get('amount'))) for l in legs if l.get('amount')]


_BECH32 = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'


def _polymod(values):
    gen = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ v
        for i in range(5):
            chk ^= gen[i] if ((b >> i) & 1) else 0
    return chk


def bech32_encode(hrp, data):
    """BIP-173 bech32 of raw bytes (8-bit -> 5-bit regrouping, checksum)."""
    acc, bits, five = 0, 0, []
    for b in data:
        acc = (acc << 8) | b
        bits += 8
        while bits >= 5:
            bits -= 5
            five.append((acc >> bits) & 31)
    if bits:
        five.append((acc << (5 - bits)) & 31)
    hrp_exp = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]
    pm = _polymod(hrp_exp + five + [0] * 6) ^ 1
    chk = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + '1' + ''.join(_BECH32[d] for d in five + chk)


def module_address(hrp, name):
    """Cosmos SDK module account: the first 20 bytes of sha256(name), bech32 with the chain's prefix."""
    return bech32_encode(hrp, hashlib.sha256(name.encode()).digest()[:20])


def hrp_of(addr):
    return addr.rsplit('1', 1)[0] if isinstance(addr, str) and '1' in addr else None


def parse_time(s):
    """CometBFT RFC 3339 time with nanoseconds -> unix seconds (float)."""
    s = s.rstrip('Z')
    if '.' in s:
        head, frac = s.split('.', 1)
        frac = (frac + '000000')[:6]
        s = head + '.' + frac
    return dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp()


def thor_denom(denom):
    """THORChain asset denom -> (symbol, coingecko) or None: 'btc-btc', 'eth-usdc-0xa0b8..', 'eth/eth', 'btc~btc'."""
    d = denom.lower()
    if d in ('rune', 'tcy', 'x/ruji'):
        sym = d.split('/')[-1].upper()
        return sym, THOR_SYMBOL_CG.get(sym)
    m = re.match(r'^([a-z0-9]+)[-/~.]([a-z0-9]+)(?:-0x[0-9a-f]+)?$', d)
    if not m:
        return None
    sym = m.group(2).upper()
    return sym, THOR_SYMBOL_CG.get(sym)


# chain-registry chain names of EVM chains -> DefiLlama coins-API prefixes, for assets whose trace ends at an ERC-20
EVM_TRACE_PREFIX = {'ethereum': 'ethereum', 'arbitrum': 'arbitrum', 'base': 'base', 'polygon': 'polygon',
                    'avalanche': 'avax', 'binancesmartchain': 'bsc', 'optimism': 'optimism', 'fantom': 'fantom'}
STABLE_COINGECKO = {'usd-coin', 'tether', 'axlusdc', 'axelar-usdt', 'dai', 'usds', 'paypal-usd', 'first-digital-usd',
                    'ethena-usde', 'noble-dollar', 'agora-dollar', 'ripple-usd', 'global-dollar', 'usdt0'}


def trace_price_key(traces):
    """A price key from an assetlist entry's provenance: the last trace's counterparty, when it is an ERC-20 on an
    EVM chain the price feed covers, or a base denomination this module already knows."""
    for t in reversed(traces or []):
        cp = t.get('counterparty') or {}
        base, chain = cp.get('base_denom') or '', cp.get('chain_name') or ''
        if base.startswith('0x') and chain in EVM_TRACE_PREFIX:
            return '%s:%s' % (EVM_TRACE_PREFIX[chain], base.lower())
        if (chain, base.lower()) in NATIVE_TRACE:
            return 'coingecko:%s' % NATIVE_TRACE[(chain, base.lower())]
        if base in KNOWN_BASE:
            return 'coingecko:%s' % KNOWN_BASE[base][2]
    return None


def cosmos_class(symbol, price_key, default):
    """Asset class for IBC-decorated symbols ('USDC.n', 'axlUSDC', 'USDT.kv') that the shared table cannot read."""
    if price_key and price_key.startswith('coingecko:') and price_key.split(':', 1)[1] in STABLE_COINGECKO:
        return 'usd_stable'
    s = (symbol or '').strip()
    s = re.sub(r'^(axl|st\.|wh)', '', s, flags=re.I) if not s.lower().startswith('st') or s.lower().startswith('st.') else s
    s = re.sub(r'\.(n|inj|kv|axl|grv|eth|e|sol|wh|arb|base|pol|bsc|osmo|noble)$', '', s, flags=re.I)
    from chain_adapters import asset_class
    c = asset_class(s)
    return c if c != 'other' else default


def display_exponent(asset):
    """The decimal exponent of an assetlist entry's display unit (the largest exponent when display is not listed)."""
    units = asset.get('denom_units') or []
    disp = asset.get('display')
    for u in units:
        if u.get('denom') == disp or disp in (u.get('aliases') or []):
            return int(u.get('exponent') or 0)
    return max((int(u.get('exponent') or 0) for u in units), default=None)


# ---------------------------------------------------------------------------------------------- transport

class Comet:
    """CometBFT RPC over several endpoints, routing each call to an endpoint that still holds the height."""

    def __init__(self, urls, http, notes):
        self.http = http
        self.http_fast = Http(min_interval=http.min_interval, timeout=20, retries=1)
        self.eps = []
        self.notes = notes
        seen = set()
        for u in urls:
            u = u.rstrip('/')
            if u in seen:
                continue
            seen.add(u)
            try:
                st = http.get(u + '/status')['result']
                si = st['sync_info']
                self.eps.append({'url': u, 'network': st['node_info'].get('network'),
                                 'earliest': int(si.get('earliest_block_height') or 0),
                                 'earliest_time': si.get('earliest_block_time'),
                                 'latest': int(si['latest_block_height']), 'latest_time': parse_time(si['latest_block_time']),
                                 'parked': 0.0, 'no': set()})
            except Exception as e:
                notes.append('%s unavailable: %s' % (u.split('/')[2], str(e)[:80]))
        if not self.eps:
            raise RuntimeError('no CometBFT endpoint answered /status')
        nets = {}
        for e in self.eps:
            nets[e['network']] = nets.get(e['network'], 0) + 1
        self.network = max(nets, key=nets.get)
        for e in [e for e in self.eps if e['network'] != self.network]:
            notes.append('%s dropped: network %s' % (e['url'].split('/')[2], e['network']))
        self.eps = [e for e in self.eps if e['network'] == self.network]
        self.calls = 0

    @property
    def latest(self):
        return max(e['latest'] for e in self.eps)

    @property
    def earliest(self):
        """Lowest height any endpoint claims to hold (an earliest of 0 or 1 means unpruned)."""
        return min(max(1, e['earliest']) for e in self.eps)

    def get(self, path, params=None, height=None, rounds=3, fast=False):
        http = self.http_fast if fast else self.http
        last = None
        for _round in range(rounds):
            now = time.monotonic()
            for e in self.eps:
                if e['parked'] > now or path in e['no']:
                    continue
                if height is not None and e['earliest'] > 1 and height < e['earliest']:
                    continue
                try:
                    d = http.get(e['url'] + path, params)
                except HttpError as x:
                    last = x
                    if x.code == 429:
                        e['parked'] = time.monotonic() + 20
                    elif x.code in (404, 501):
                        e['no'].add(path)          # this node does not serve this route
                    elif x.code == 500 and height is not None:
                        pass                       # CometBFT answers a pruned height with HTTP 500; try the next node
                    else:
                        e['parked'] = time.monotonic() + 15
                    continue
                self.calls += 1
                if isinstance(d, dict) and 'result' in d:
                    return d['result']
                last = RuntimeError('%s: %s' % (path, str(d.get('error') if isinstance(d, dict) else d)[:160]))
                # a JSON-RPC error for one height (pruned between /status and now) is not a reason to park the node
            if _round + 1 < rounds:
                time.sleep(1.5 * (_round + 1))
        raise RuntimeError('%s h=%s failed on every endpoint: %s' % (path, height, str(last)[:160]))

    def tx_search_count(self, first, last):
        """(count, endpoint) from a node's transaction index over [first, last], or None. Public load balancers mostly
        refuse height ranges ("strict equality"); a chain's own RPC often answers in one call."""
        q = '"tx.height>=%d AND tx.height<=%d"' % (first, last)
        for e in self.eps:
            if e['earliest'] > 1 and first < e['earliest']:
                continue
            try:
                d = self.http_fast.get(e['url'] + '/tx_search', {'query': q, 'per_page': 1, 'page': 1},
                                       timeout=TX_SEARCH_TIMEOUT)
                n = int(((d or {}).get('result') or {}).get('total_count'))
                self.calls += 1
                return n, e['url'].replace('https://', '')
            except Exception:
                continue
        return None

    def serves(self, h):
        """Whether any endpoint returns the header at height h (one pass, no retries: used to find a pruning edge)."""
        try:
            self.get('/blockchain', {'minHeight': h, 'maxHeight': h}, height=h, rounds=1, fast=True)
            return True
        except RuntimeError:
            return False

    def header_time(self, h):
        r = self.get('/blockchain', {'minHeight': h, 'maxHeight': h}, height=h)
        return parse_time(r['block_metas'][0]['header']['time'])

    def first_height_at(self, ts, lo, hi):
        """First height in [lo, hi] whose header time >= ts, by a rate-seeded bracket and bisection."""
        t_hi = self.header_time(hi)
        if t_hi < ts:
            return hi + 1
        probe = max(lo, hi - 2000)
        t_probe = self.header_time(probe)
        spb = max((t_hi - t_probe) / max(1, hi - probe), 1e-3)
        guess = int(hi - (t_hi - ts) / spb)
        a, b = max(lo, guess - 3000), min(hi, guess + 3000)
        step = 6000
        while a > lo and self.header_time(a) >= ts:
            a, step = max(lo, a - step), step * 2
        step = 6000
        while b < hi and self.header_time(b) < ts:
            b, step = min(hi, b + step), step * 2
        if self.header_time(a) >= ts:
            return a
        while a + 1 < b:
            m = (a + b) // 2
            if self.header_time(m) >= ts:
                b = m
            else:
                a = m
        return b


# ---------------------------------------------------------------------------------------------- identity of denoms

class Denoms:
    """denom -> {'symbol', 'decimals', 'price_key'}, from the chain-registry assetlist, IBC traces and the registry."""

    def __init__(self, slug, cfg, http, rest_urls, cache_dir, notes, thor=False):
        self.info = {}
        self.notes = notes
        self.http = http
        self.rest_urls = rest_urls
        self.thor = thor
        self.traces = 0
        assets = self._assetlist(cfg.get('chain_registry') or slug, cache_dir)
        for a in assets:
            base = a.get('base')
            if not base:
                continue
            exp = display_exponent(a)
            key, src = None, 'chain-registry'
            if a.get('coingecko_id'):
                key = 'coingecko:%s' % a['coingecko_id']
            elif base.startswith('peggy0x'):
                key = 'ethereum:%s' % base[5:].lower()
            else:
                key = trace_price_key(a.get('traces'))
                if key:
                    src = 'chain-registry trace'
            self.info[base] = {'symbol': a.get('symbol'), 'decimals': exp, 'price_key': key, 'source': src}
        for d, v in (cfg.get('denoms') or {}).items():
            self.info.setdefault(d, {})
            self.info[d].update({'symbol': v.get('symbol'), 'decimals': v.get('decimals'),
                                 'price_key': 'coingecko:%s' % v['coingecko'] if v.get('coingecko') else None,
                                 'source': 'registry'})

    def _assetlist(self, name, cache_dir):
        path = (cache_dir / ('cosmos_assetlist_%s.json' % name)) if cache_dir else None
        try:
            if path and path.exists() and time.time() - path.stat().st_mtime < 7 * 86400:
                import json
                return json.loads(path.read_text()).get('assets') or []
            d = self.http.get(CHAIN_REGISTRY % name, timeout=60)
            if path:
                import json
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(d))
            return d.get('assets') or []
        except Exception as e:
            self.notes.append('chain-registry assetlist for %s unavailable: %s' % (name, str(e)[:80]))
            return []

    def resolve(self, denom):
        if denom in self.info:
            return self.info[denom]
        if self.thor:
            t = thor_denom(denom)
            if t:
                self.info[denom] = {'symbol': t[0], 'decimals': 8, 'source': 'thorchain-denom',
                                    'price_key': 'coingecko:%s' % t[1] if t[1] else None}
                return self.info[denom]
        if denom.startswith('peggy0x'):
            self.info[denom] = {'symbol': None, 'decimals': None, 'price_key': 'ethereum:%s' % denom[5:].lower(),
                                'source': 'peggy'}
            return self.info[denom]
        if denom.startswith('ibc/') and self.traces < MAX_TRACE_LOOKUPS and self.rest_urls:
            self.traces += 1
            base = self._trace(denom[4:])
            if base and base in self.info and self.info[base].get('price_key'):
                b = self.info[base]
                self.info[denom] = dict(b, source='ibc-trace:' + base)
                return self.info[denom]
            if base and base in KNOWN_BASE:
                sym, exp, cg = KNOWN_BASE[base]
                self.info[denom] = {'symbol': sym, 'decimals': exp, 'price_key': 'coingecko:%s' % cg,
                                    'source': 'ibc-trace:' + base}
                return self.info[denom]
            self.info[denom] = {'symbol': base, 'decimals': None, 'price_key': None, 'source': 'ibc-trace-unknown'}
            return self.info[denom]
        if denom in KNOWN_BASE:
            sym, exp, cg = KNOWN_BASE[denom]
            self.info[denom] = {'symbol': sym, 'decimals': exp, 'price_key': 'coingecko:%s' % cg, 'source': 'known-base'}
            return self.info[denom]
        return {'symbol': None, 'decimals': None, 'price_key': None, 'source': None}

    def _trace(self, h):
        for u in self.rest_urls:
            for route in ('/ibc/apps/transfer/v1/denom_traces/%s', '/ibc/apps/transfer/v1/denoms/%s'):
                try:
                    d = self.http.get(u.rstrip('/') + route % h, timeout=20)
                except Exception:
                    continue
                t = d.get('denom_trace') or d.get('denom') or {}
                base = t.get('base_denom') or t.get('base')
                if base:
                    return base
        return None


# ---------------------------------------------------------------------------------------------- the probe

def chain_key(cfg, network):
    slug = cfg.get('slug') or ''
    if slug in FALLBACK_RPC:
        return slug
    for k in FALLBACK_RPC:
        if (network or '').startswith(k) or (k == 'cosmoshub' and (network or '').startswith('cosmoshub')):
            return k
    return slug


def _add(bucket, denom, count, net, gross):
    e = bucket.setdefault(denom, [0, 0, 0])
    e[0] += count
    e[1] += net
    e[2] += gross


def _net_by_denom(legs):
    """[(sender, recipient, [(amount, denom)])] -> {denom: (legs, net, gross)} with net = net_positive per denom."""
    moves = {}
    for snd, rcv, coins in legs:
        for amt, denom in coins:
            moves.setdefault(denom, []).append((snd, rcv, amt))
    return {d: (len(mv), net_positive(mv), sum(a for _, _, a in mv)) for d, mv in moves.items()}


def reduce_results(res, fee_collector, plumbing):
    """One block's results -> tx counts and, per denom, [legs, net, gross] for tx-level and block-level transfers.

    Net is per transaction (`net_positive` over that transaction's legs of one denom), so a swap routed through three
    pools counts what the trader sent and received rather than every pool leg; gross keeps every leg. Block-level
    legs have no transaction to group by and are netted per block."""
    txr = res.get('txs_results') or []
    out = {'txs': len(txr), 'failed': 0, 'tx': {}, 'block': {}, 'fees': {}}
    for tr in txr:
        if int(tr.get('code') or 0) != 0:
            out['failed'] += 1
            continue
        legs, fee_legs = [], []
        for ev in tr.get('events') or []:
            if ev.get('type') != 'transfer':
                continue
            for leg in transfer_legs(ev):
                (fee_legs if (fee_collector and leg[1] == fee_collector) else legs).append(leg)
        for denom, (cnt, net, gross) in _net_by_denom(legs).items():
            _add(out['tx'], denom, cnt, net, gross)
        for denom, (cnt, net, gross) in _net_by_denom(fee_legs).items():
            _add(out['fees'], denom, cnt, gross, gross)
    blk = (res.get('finalize_block_events') or []) + (res.get('begin_block_events') or []) + (res.get('end_block_events') or [])
    legs = []
    for ev in blk:
        if ev.get('type') != 'transfer':
            continue
        legs += [l for l in transfer_legs(ev) if l[0] not in plumbing and l[1] not in plumbing]
    for denom, (cnt, net, gross) in _net_by_denom(legs).items():
        _add(out['block'], denom, cnt, net, gross)
    return out


def _table(units, field, denoms, ctx, N, native_symbol):
    n = len(units)
    per = {}
    for i, u in enumerate(units):
        for denom, (cnt, net, gross) in u[field].items():
            d = per.setdefault(denom, {'count': [0] * n, 'net': [0] * n, 'gross': [0] * n})
            d['count'][i] += cnt
            d['net'][i] += net
            d['gross'][i] += gross
    infos = {d: denoms.resolve(d) for d in per}
    keys = [i['price_key'] for i in infos.values() if i.get('price_key')]
    pr = ctx.prices.get(keys) if keys else {}
    meta, price_of, pa = {}, {}, {}
    for denom, d in per.items():
        inf = infos[denom]
        q = pr.get(inf.get('price_key')) if inf.get('price_key') else None
        dec = inf.get('decimals')
        if dec is None and q and q.get('decimals') is not None and inf.get('source') == 'peggy':
            dec = int(q['decimals'])
        sym = inf.get('symbol') or (q or {}).get('symbol')
        meta[denom] = {'symbol': sym, 'decimals': dec}
        price_of[denom] = q.get('price') if (q and dec is not None) else None
        pa[denom] = {'count': d['count'],
                     'amount': [x / 10 ** dec for x in d['net']] if dec is not None else [0.0] * n,
                     'gross': [x / 10 ** dec for x in d['gross']] if dec is not None else [0.0] * n}
    t = asset_rows(pa, n, N, meta, price_of, native_symbols=[native_symbol] if native_symbol else [])
    for r in t['assets'] + t['unpriced_top']:
        inf = infos[r['asset']]
        r['identity'] = inf.get('source')
        r['class'] = cosmos_class(r.get('symbol'), inf.get('price_key'), r['class'])
    by_class = {}
    for r in t['assets']:
        by_class[r['class']] = by_class.get(r['class'], 0.0) + (r['usd'] or 0.0)
    t['usd_by_class'] = by_class
    return t


def window_heights(c, start_ts, end_ts, latest, latest_time, notes):
    """(first, last, start_ts actually covered). Clips the start when no endpoint still holds it."""
    try:
        first = c.first_height_at(start_ts, 1, latest)
    except RuntimeError:
        lo, hi = 1, latest                       # invariant: hi is served by some endpoint
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if c.serves(mid):
                hi = mid
            else:
                lo = mid
        first = hi + 50                          # a margin above the pruning edge, which moves while we read
        t = c.header_time(first)
        notes.append('no endpoint holds the window start; covered from %s and scaled to the full window'
                     % window_dict(t, end_ts)['start_utc'])
        start_ts = t
    last = latest if end_ts >= latest_time else c.first_height_at(end_ts, first, latest) - 1
    return first, last, start_ts


@register('cosmos')
def probe(cfg, ctx):
    t0 = time.time()
    p = cfg.get('probe') or {}
    notes = []
    http = Http(min_interval=p.get('min_interval', 0.05), timeout=p.get('timeout', 40), retries=2)
    slug = cfg.get('slug') or ''
    urls = list(p.get('rpc') or []) + [u for u in FALLBACK_RPC.get(slug, []) if u not in (p.get('rpc') or [])]
    c = Comet(urls, http, notes)
    key = chain_key(cfg, c.network)
    latest = c.latest
    latest_time = c.header_time(latest)
    end_ts = min(ctx.end_ts, latest_time)
    first, last, start_ts = window_heights(c, ctx.start_ts, end_ts, latest, latest_time, notes)
    H = last - first + 1
    if H <= 0:
        raise RuntimeError('empty window: heights %d..%d' % (first, last))
    workers = int(p.get('workers', 4))
    scale = (end_ts - ctx.start_ts) / max(1.0, end_ts - start_ts)

    # ------------------------------------------------------------------ phase 1: transaction count from header runs
    U = int(math.ceil(H / RUN))
    indexed = c.tx_search_count(first, last) if U > EXACT_RUN_BUDGET else None
    budget = int(p.get('run_samples') or DEFAULT_RUN_SAMPLES)
    units = list(range(U)) if U <= EXACT_RUN_BUDGET else sample_points(0, U - 1, min(budget, U), seed=int(ctx.start_ts))

    def run_txs(u):
        a = first + u * RUN
        b = min(last, a + RUN - 1)
        try:
            r = c.get('/blockchain', {'minHeight': a, 'maxHeight': b}, height=a)
            metas = r.get('block_metas') or []
            if len(metas) != b - a + 1:
                return u, None, 'run %d..%d returned %d headers' % (a, b, len(metas))
            return u, [(int(m['header']['height']), int(m.get('num_txs') or 0)) for m in metas], None
        except Exception as e:
            return u, None, 'run %d: %s' % (a, str(e)[:100])

    errors = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        got = list(ex.map(run_txs, units))
    runs = [blocks for _, blocks, err in got if blocks is not None]
    errors += [err for _, blocks, err in got if err]
    vals = [sum(n for _, n in blocks) for blocks in runs]
    exact = len(vals) == U
    tx_count, tx_se = (float(sum(vals)), 0.0) if exact else stratified_total(vals, U)
    sampled_count, sampled_se = tx_count, tx_se
    if indexed is not None and not exact:
        tx_count, tx_se = float(indexed[0]), 0.0
    if scale > 1.0001 and tx_count is not None:
        tx_count, tx_se = tx_count * scale, (tx_se * scale if tx_se is not None else None)
    blocks_read = sum(len(b) for b in runs)
    nonempty = sorted(h for b in runs for h, n in b if n > 0)
    frac_ne = len(nonempty) / blocks_read if blocks_read else 0.0

    # ------------------------------------------------------------------ phase 2: transfer value from block results
    # Transaction-level transfers can only sit in blocks that carried transactions, so on a sparse chain (Noble: one
    # block in eleven) the value sample is drawn from the non-empty blocks phase 1 found and scaled to their (estimated)
    # number — a two-phase design whose standard error ignores the phase-1 error in that number. Block-level transfers
    # happen in every block and keep a uniform sample of heights.
    n_val = int(p.get('samples') or min(ctx.samples, DEFAULT_VALUE_SAMPLES))
    dense = frac_ne >= 0.9
    if dense or not nonempty:
        h_tx = sample_points(first, last, min(n_val, H), seed=int(ctx.start_ts) + 1)
        h_blk = h_tx
        N_tx = H
    else:
        idx = sample_points(0, len(nonempty) - 1, min(n_val, len(nonempty)), seed=int(ctx.start_ts) + 1)
        h_tx = [nonempty[i] for i in idx]
        h_blk = sample_points(first, last, min(max(20, n_val // 3), H), seed=int(ctx.start_ts) + 2)
        N_tx = frac_ne * H if not exact else float(len(nonempty))
    want = sorted(set(h_tx) | set(h_blk))

    def results(h):
        try:
            return h, c.get('/block_results', {'height': h}, height=h), None
        except Exception as e:
            return h, None, 'block_results %d: %s' % (h, str(e)[:100])

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        fetched = {h: (res, err) for h, res, err in ex.map(results, want)}
    errors += [err for res, err in fetched.values() if err]
    # the bech32 prefix comes from the first address any event names; module addresses are derived from it
    hrp = None
    for res, _ in fetched.values():
        for tr_ in (res or {}).get('txs_results') or []:
            for ev in tr_.get('events') or []:
                if ev.get('type') == 'transfer':
                    for snd, rcv, _c in transfer_legs(ev):
                        hrp = hrp_of(rcv) or hrp_of(snd)
                        if hrp:
                            break
                if hrp:
                    break
            if hrp:
                break
        if hrp:
            break
    fee_collector = module_address(hrp, 'fee_collector') if hrp else None
    plumbing = {module_address(hrp, m) for m in PLUMBING_MODULES} if hrp else set()
    reduced = {h: reduce_results(res, fee_collector, plumbing) for h, (res, err) in fetched.items() if res is not None}
    tx_units = [reduced[h] for h in h_tx if h in reduced]
    blk_units = [reduced[h] for h in h_blk if h in reduced]
    native_symbol = (cfg.get('native') or {}).get('symbol')
    rest = list(p.get('rest') or []) + FALLBACK_REST.get(key, [])
    denoms = Denoms(key, p, http, rest, (ctx.out / 'cache') if ctx.out else None, notes, thor=(key == 'thorchain'))
    tr = _table(tx_units, 'tx', denoms, ctx, N_tx, native_symbol)
    blk = _table(blk_units, 'block', denoms, ctx, H, native_symbol)
    fees = _table(tx_units, 'fees', denoms, ctx, N_tx, native_symbol)
    if scale > 1.0001:
        for t in (tr, blk, fees):
            for r in t['assets'] + t['unpriced_top']:
                for f in ('transfers', 'transfers_se', 'amount', 'usd', 'usd_se', 'gross_amount', 'gross_usd'):
                    if r.get(f) is not None:
                        r[f] = r[f] * scale
            t['priced_usd'] *= scale
            if t.get('gross_priced_usd') is not None:
                t['gross_priced_usd'] *= scale
            t['usd_by_class'] = {k: v * scale for k, v in t['usd_by_class'].items()}
    tr['method'] = ('sampled-blocks (transaction-level bank transfer events of successful transactions, fee legs '
                    'removed; amount = net per transaction and denom, gross_amount = every leg)'
                    + ('' if dense else '; two-phase: value read from non-empty blocks'))
    tr['block_level'] = {k: blk.get(k) for k in ('assets', 'unpriced_top', 'unpriced_assets', 'priced_usd',
                                                 'gross_priced_usd', 'usd_by_class')}
    tr['block_level']['method'] = ('sampled-blocks (finalize/begin/end-block transfer events, staking, inflation and fee '
                                   'plumbing removed; netted per block)')
    tr['fees'] = {'priced_usd': fees['priced_usd'], 'assets': fees['assets'][:5]}
    tr['module_addresses'] = {'fee_collector': fee_collector, 'prefix': hrp}

    n_txs = sum(u['txs'] for u in tx_units)
    n_fail = sum(u['failed'] for u in tx_units)
    secs = max(1, end_ts - ctx.start_ts)
    method = 'exact-blocks' if exact else ('exact-index' if indexed is not None else 'sampled-blocks')
    if scale > 1.0001:
        method += '-extrapolated'
    tx = {'count': tx_count, 'se': tx_se, 'method': method,
          'blocks': H, 'runs_read': len(vals), 'runs_total': U, 'run_length': RUN,
          'per_block': (tx_count / H / scale) if tx_count is not None else None,
          'tps': (tx_count / secs) if tx_count is not None else None,
          'nonempty_block_share': frac_ne,
          'index_count': ({'count': indexed[0], 'endpoint': indexed[1], 'sampled_estimate': sampled_count,
                           'sampled_se': sampled_se} if indexed is not None else None),
          'failed_share': (n_fail / n_txs) if n_txs else None,
          'note': 'every transaction included in a block (num_txs), successful or failed. ' + CHAIN_NOTES.get(key, '')}
    return {'tx': tx, 'transfers': tr, 'window': window_dict(ctx.start_ts, end_ts),
            'blocks': {'first': first, 'last': last, 'latest': latest, 'network': c.network,
                       'value_sampled_tx': len(tx_units), 'value_sampled_block': len(blk_units)},
            'endpoint': ', '.join(e['url'].replace('https://', '') for e in c.eps[:3]),
            'calls': c.calls, 'notes': notes, 'errors': errors[:20], 'error_count': len(errors),
            'seconds': round(time.time() - t0, 1)}
