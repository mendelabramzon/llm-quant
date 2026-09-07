#!/usr/bin/env python3
"""The address-label registry: what an address *is*, where that claim came from, and how much of a window it covers.

Why this exists. `live_scan` used to tag addresses from behaviour and model memory. Two mislabels moved headline numbers
by an order of magnitude in one window: the CoW settlement contract read as a CEX (leverage-to-exchange $5.3M -> $25.7M),
and an RLUSD treasury read as a CEX (net exchange flow -$0.9M -> -$101.6M). Both were caught by hand. Nothing would have
caught the third one.

The fix is provenance, not more labels. Every entry carries a `source`, and sources form a tier:

    known-canonical        an address this file hardcodes, with the reason written next to it
    etherscan-verified     verified contract name fetched from Etherscan V2
    blockscout-verified    verified contract name fetched from Blockscout
    model-memory           from the model's memory of well-known wallets; plausible, never independently checked
    behaviour-<date>       inferred from behaviour in one window; the weakest claim

`live_scan` can then compute exchange flow at a chosen minimum tier and report the spread between "verified only" and
"including memory" instead of hiding the assumption inside a number.

The audit is the part that earns its keep. A centralized-exchange hot wallet is an externally-owned account. So any
address tagged `exchange` that resolves to a *verified contract with a name* is a contradiction, and that is exactly the
shape of both bugs above. `labels.py audit` re-runs that check over the whole registry on demand.

    uv run python scripts/labels.py coverage --out research/2026-09-07/live_5h   what fraction of window USD is labelled
    uv run python scripts/labels.py resolve  --out research/2026-09-07/live_5h   fetch names for the top unlabelled
    uv run python scripts/labels.py audit                                        contradictions + unverified exchange tags
    uv run python scripts/labels.py adopt-memory                                 move live_scan's MEMORY_LABELS in, with provenance
    uv run python scripts/labels.py add 0x... --label "..." --kind venue --source known-canonical
    uv run python scripts/labels.py list [--kind exchange] [--source model-memory]
"""
import argparse
import collections
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
REGISTRY = ROOT / 'scripts' / 'address_labels.json'
UA = 'llm-quant research'

# `kind` decides how flow through the address is counted. Only the first two are exchange flow.
KINDS = ['exchange', 'exchange_deposit', 'protocol', 'venue', 'vault', 'bridge', 'issuer', 'treasury', 'token', 'mev_bot', 'eoa']
EXCHANGE_KINDS = {'exchange', 'exchange_deposit'}
# Provenance tiers, strongest first. `min_tier` in `load()` cuts the registry at a confidence level.
TIERS = ['known-canonical', 'etherscan-verified', 'blockscout-verified', 'model-memory', 'behaviour']


def tier_of(source):
    """Map a free-form source string onto a tier. `behaviour-2026-09-07-unverified` -> `behaviour`."""
    s = (source or '').lower()
    for t in TIERS:
        if s.startswith(t):
            return t
    return 'behaviour'


def tier_rank(source):
    return TIERS.index(tier_of(source))


# Addresses whose identity is not in doubt, with the reason kept next to the entry. These are the anchor of the registry:
# every one of them was previously either absent or inferred, and several were being counted as exchange flow.
CANONICAL = {
    # settlement and intent venues — funds rest here mid-trade, they are not an exchange balance
    '0x9008d19f58aabd9ed0d60971565aa8510560ab41': ('CoW Protocol settlement (GPv2Settlement)', 'venue'),
    '0xc92e8bdf79f0507f65a392b0ab4667716bfe0110': ('CoW Protocol vault relayer', 'venue'),
    '0x00000000009e50a7ddb7a7b0e2ee6604fd120e49': ('UniswapX reactor (Dutch v2)', 'venue'),
    '0x000000000022d473030f116ddee9f6b43ac78ba3': ('Permit2', 'protocol'),
    '0x4337084d9e255ff0702461cf8895ce9e3b5ff108': ('ERC-4337 EntryPoint v0.8', 'protocol'),
    '0x0000000071727de22e5e9d8baf0edac6f37da032': ('ERC-4337 EntryPoint v0.7', 'protocol'),
    # routers — pass-through, never a destination
    '0x1111111254eeb25477b68fb85ed929f73a960582': ('1inch AggregationRouterV5', 'venue'),
    '0x111111125421ca6dc452d289314280a0f8842a65': ('1inch AggregationRouterV6', 'venue'),
    '0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad': ('Uniswap Universal Router', 'venue'),
    '0x66a9893cc07d91d95644aedd05d03f95e1dba8af': ('Uniswap Universal Router v2', 'venue'),
    '0x7a250d5630b4cf539739df2c5dacb4c659f2488d': ('Uniswap v2 Router 02', 'venue'),
    '0xe592427a0aece92de3edee1f18e0157c05861564': ('Uniswap v3 SwapRouter', 'venue'),
    '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45': ('Uniswap v3 SwapRouter02', 'venue'),
    '0xdef1c0ded9bec7f1a1670819833240f027b25eff': ('0x Exchange Proxy', 'venue'),
    '0x6131b5fae19ea4f9d964eac0408e4408b66337b5': ('KyberSwap MetaAggregationRouterV2', 'venue'),
    # core protocol
    '0x000000000004444c5dc75cb358380d2e3de08a90': ('Uniswap v4 PoolManager', 'protocol'),
    '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2': ('Aave v3 Pool', 'protocol'),
    '0xc13e21b648a5ee794902342038ff3adab66be987': ('SparkLend Pool', 'protocol'),
    '0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb': ('Morpho Blue', 'protocol'),
    '0xba12222222228d8ba445958a75a0704d566bf2c8': ('Balancer v2 Vault', 'protocol'),
    '0xc3d688b66703497daa19211eedff47f25384cdc3': ('Compound v3 USDC (Comet)', 'protocol'),
    '0x3afdc9bca9213a35503b077a6072f3d0d5ab0840': ('Compound v3 USDT (Comet)', 'protocol'),
    '0xa17581a9e3356d9a858b789d68b4d866e593ae94': ('Compound v3 WETH (Comet)', 'protocol'),
    '0xae7ab96520de3a18e5e111b5eaab095312d7fe84': ('Lido stETH', 'token'),
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': ('Wrapped Ether (WETH9)', 'token'),
    '0x889edc2edab5f40e902b864ad4d7ade8e412f9b1': ('Lido withdrawal queue', 'protocol'),
    # bridges and messaging — a bridge inbox is not an exchange deposit
    '0xbd3fa81b58ba92a82136038b25adec7066af3155': ('Circle CCTP TokenMessenger v1', 'bridge'),
    '0x28b5a0e9c621a5badaa536219b3a228c8168cf5d': ('Circle CCTP TokenMessenger v2', 'bridge'),
    '0x0a992d191deec32afe36203ad87d7d289a738f81': ('Circle CCTP MessageTransmitter v1', 'bridge'),
    '0x6c96de32cea08842dcc4058c14d3aaad7fa41dee': ('LayerZero OFT adapter (USDT0)', 'bridge'),
    '0x147bde4f997f0d4c7544ed0c55eacf1e5e6bf9c4': ('LayerZero OFT adapter (USDG)', 'bridge'),
    '0x8484ef722627bf18ca5ae6bcf031c23e6e922b30': ('Polygon PoS ERC20 bridge', 'bridge'),
    '0xa0c68c638235ee32657e8f720a23cec1bfc77c77': ('Polygon PoS RootChainManager', 'bridge'),
    '0x8315177ab297ba92a06054ce80a67ed4dbd7ed3a': ('Arbitrum One bridge', 'bridge'),
    '0x99c9fc46f92e8a1c0dec1b1747d010903e884be1': ('Optimism gateway (L1StandardBridge)', 'bridge'),
    '0x3154cf16ccdb4c6d922629664174b904d80f2c35': ('Base L1StandardBridge', 'bridge'),
    '0xbd0d173eeb87d57a09521c24388a12789f33ba96': ('Robinhood Chain SequencerInbox', 'bridge'),
    # issuers / treasuries — a mint or treasury address moving size is issuance, not an exchange flow
    '0x5754284f345afc66a98fbb0a0afe71e0f007b949': ('Tether treasury', 'issuer'),
    '0x8292bb45bf1ee4d140127049757c2e0ff06317ed': ('RLUSD token (Ripple USD)', 'token'),
    # zero / burn
    '0x0000000000000000000000000000000000000000': ('zero address (mint/burn)', 'token'),
    '0x000000000000000000000000000000000000dead': ('burn address', 'token'),
}

# Proxy shells whose own name says nothing. The informative name is the implementation behind them, so `resolve_one`
# follows the proxy when it lands on one of these — otherwise the registry fills with rows that all read "ERC1967Proxy".
GENERIC_PROXIES = {'erc1967proxy', 'uupsproxy', 'transparentupgradeableproxy', 'adminupgradeabilityproxy',
                   'initializableimmutableadminupgradeabilityproxy', 'beaconproxy', 'gnosissafeproxy', 'safeproxy',
                   'proxy', 'upgradeableproxy', 'eip1967proxy', 'vyper_contract'}

# Contract-name -> kind heuristics for `resolve`, most specific first. A name is evidence, not proof, so a resolved entry
# records the name it matched and stays at the *-verified tier rather than becoming canonical. There is deliberately no
# name rule for `token`: names like "UsdsPsmWrapper" contain "usd" and a greedy token rule mislabelled them. A token is
# recognised only by the explorer reporting a token symbol for the address.
NAME_RULES = [
    (('settlement', 'gpv2', 'settler'), 'venue'),
    (('router', 'aggregat', 'swapper', 'exchangeproxy', 'reactor', 'filler', 'pair', 'curvepool', 'clipper'), 'venue'),
    (('bridge', 'inbox', 'outbox', 'messenger', 'transmitter', 'minter', 'oft', 'teleport', 'portal', 'gateway'), 'bridge'),
    (('vault', 'erc4626', 'strategy', 'masterchef', 'staking', 'stakedtoken', 'silo'), 'vault'),
    (('safe', 'gnosis', 'timelock', 'treasury', 'multisig', 'buffer', 'allocator'), 'treasury'),
    (('account', 'msca', 'wallet'), 'treasury'),   # a modular smart-contract account is a held balance, not a venue
    (('pool', 'comptroller', 'lend', 'comet', 'market', 'entrypoint', 'permit2', 'manager', 'factory', 'oracle',
      'psm', 'wrapper', 'converter', 'adapter', 'liquidity'), 'protocol'),
]


def infer_kind(name, token_symbol=None):
    """Name rules first, then the token-symbol fallback.

    Order matters: a Uniswap v2 pair and an ERC-4626 vault both expose an ERC-20 symbol, so a symbol-first rule files
    them as plain tokens and loses what they are. The name is the more specific evidence when it matches a rule.
    """
    n = (name or '').lower()
    for keys, kind in NAME_RULES:
        if any(k in n for k in keys):
            return kind
    return 'token' if token_symbol else None


# ----------------------------------------------------------------------------------------------------------------------
# Registry io
# ----------------------------------------------------------------------------------------------------------------------
def load_registry():
    d = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}
    d.setdefault('labels', {})
    return d


def save_registry(d):
    d['labels'] = dict(sorted(d['labels'].items()))
    REGISTRY.write_text(json.dumps(d, indent=1) + '\n')


def load(min_tier=None):
    """address -> entry, optionally cut at a minimum provenance tier ('known-canonical', 'model-memory', ...)."""
    labels = load_registry()['labels']
    if min_tier is None:
        return labels
    cut = TIERS.index(min_tier)
    return {a: v for a, v in labels.items() if tier_rank(v.get('source')) <= cut}


def put(reg, addr, label, kind, source, **extra):
    """Insert or upgrade an entry. A stronger source always wins; an equal source refreshes the label."""
    addr = addr.lower()
    old = reg['labels'].get(addr)
    if old and tier_rank(old.get('source')) < tier_rank(source):
        return False
    reg['labels'][addr] = dict({'label': label, 'kind': kind, 'source': source}, **extra)
    return True


# ----------------------------------------------------------------------------------------------------------------------
# Fetchers
# ----------------------------------------------------------------------------------------------------------------------
def http_json(url, timeout=20, retries=1):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode('utf-8', 'replace'))
        except Exception:
            if i == retries:
                return None
            time.sleep(1.0)
    return None


def blockscout_address(addr, host='eth.blockscout.com'):
    """{name, is_contract, is_verified, token_symbol, implementation} or None. Public Blockscout carries verified
    contract names but no exchange tags, so an EOA comes back nameless — which is itself the useful answer."""
    d = http_json('https://%s/api/v2/addresses/%s' % (host, addr))
    if not isinstance(d, dict):
        return None
    tok = d.get('token') or {}
    impl = (d.get('implementations') or [{}])[0]
    return {'name': d.get('name'), 'is_contract': bool(d.get('is_contract')), 'is_verified': bool(d.get('is_verified')),
            'token_symbol': tok.get('symbol'), 'proxy_type': d.get('proxy_type'),
            'implementation': impl.get('name'), 'implementation_address': impl.get('address_hash')}


def etherscan_name(addr, chainid=1):
    try:
        import etherscan
        s = etherscan.source(chainid, addr, follow_proxy=False)
        return s.get('name')
    except Exception:
        return None


def resolve_one(addr, use_etherscan=True):
    """Best available identity for one address, with the source that produced it.

    A proxy shell is followed to its implementation: "ERC1967Proxy" names nothing, while the implementation behind it
    ("SingleOwnerMSCA", "Sweeper") is the fact worth recording. The proxy name is kept alongside so the entry still says
    what the address literally is.
    """
    bs = blockscout_address(addr)
    if bs and bs.get('name'):
        name, extra = bs['name'], {}
        if name.lower() in GENERIC_PROXIES and bs.get('implementation'):
            name = bs['implementation']
            extra = {'via_proxy': bs['name'], 'implementation': bs.get('implementation_address')}
        return dict({'name': name, 'source': 'blockscout-verified', 'is_contract': True,
                     'token_symbol': bs.get('token_symbol')}, **extra)
    if use_etherscan and (ROOT / 'etherscan_key.txt').exists():
        n = etherscan_name(addr)
        if n:
            return {'name': n, 'source': 'etherscan-verified', 'is_contract': True, 'token_symbol': None}
    if bs is not None:
        return {'name': None, 'source': 'blockscout-verified', 'is_contract': bs['is_contract'],
                'token_symbol': bs.get('token_symbol')}
    return None


# ----------------------------------------------------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------------------------------------------------
def cmd_seed(args):
    """Write the canonical set into the registry. Idempotent; never downgrades an existing stronger entry."""
    reg = load_registry()
    n = 0
    for a, (label, kind) in CANONICAL.items():
        n += put(reg, a, label, kind, 'known-canonical')
    save_registry(reg)
    print(json.dumps({'canonical_written': n, 'registry_size': len(reg['labels'])}))


def cmd_adopt_memory(args):
    """Move `live_scan.MEMORY_LABELS` into the registry as `model-memory`, so the weakest claims are visible and cuttable.

    They stay `kind: exchange` — that is what memory asserts — but they now sit at a tier the exchange-flow computation
    can exclude, which is how the label uncertainty becomes a reported band instead of a hidden assumption.
    """
    import live_scan
    reg = load_registry()
    n = 0
    for a, label in live_scan.MEMORY_LABELS.items():
        kind = 'exchange_deposit' if 'deposit' in label.lower() else 'exchange'
        n += put(reg, a, label, kind, 'model-memory')
    save_registry(reg)
    print(json.dumps({'adopted': n, 'registry_size': len(reg['labels'])}))


def cmd_audit(args):
    """Contradictions and weak claims in the registry. This is the check that would have caught the CoW bug.

    A centralized-exchange *hot wallet* is an externally-owned account. So `kind: exchange` on an address that resolves
    to a verified contract is a hard contradiction, and its flow has been counted as exchange flow ever since. A
    `kind: exchange_deposit` on a contract is legitimate — deposit contracts are contracts — but a label naming a
    specific exchange still deserves review, so it is reported separately rather than as an error.
    """
    reg = load_registry()
    labels = dict(reg['labels'])
    if args.book:
        # The effective address book is what `live_scan` actually counts: the registry plus the behavioural and memory
        # tiers. Auditing only the file would miss exactly the tier where mislabels live.
        import live_scan
        for a, v in live_scan.load_address_book().items():
            labels.setdefault(a, v)
    ex = [(a, v) for a, v in labels.items() if v.get('kind') in EXCHANGE_KINDS]
    contradictions, review = [], []
    limit = args.limit or len(ex)
    checked = 0
    for i, (a, v) in enumerate(ex[:limit]):
        if v.get('source') == 'known-canonical' and not args.recheck:
            continue
        r = resolve_one(a, use_etherscan=not args.no_etherscan)
        time.sleep(args.sleep)
        checked += 1
        if r is None or not r.get('is_contract'):
            continue
        row = {'address': a, 'tagged': v['kind'], 'label': v['label'], 'source': v.get('source'),
               'resolves_to': r.get('name'), 'via': r.get('source')}
        # Severity is calibrated by how much the evidence actually proves. A *named, verified* contract behind an
        # `exchange` tag is a hard contradiction: GPv2Settlement is not a hot wallet. An unverified contract is only a
        # flag, because several exchanges genuinely run contract-based hot wallets, and treating that as an error would
        # produce noise that trains the reader to ignore the audit.
        if v['kind'] == 'exchange' and r.get('name'):
            contradictions.append(row)
        elif r.get('name') or v['kind'] == 'exchange':
            review.append(row)
        if (i + 1) % 20 == 0:
            print('  checked %d/%d' % (i + 1, len(ex)), file=sys.stderr)
    weak = [{'address': a, 'label': v['label'], 'kind': v['kind'], 'source': v.get('source')}
            for a, v in labels.items() if v.get('kind') in EXCHANGE_KINDS and tier_rank(v.get('source')) >= TIERS.index('model-memory')]
    by_tier = collections.Counter(tier_of(v.get('source')) for v in labels.values())
    by_kind = collections.Counter(v.get('kind') for v in labels.values())
    bad_kind = [a for a, v in labels.items() if v.get('kind') not in KINDS]
    report = {'registry_size': len(labels), 'by_tier': dict(by_tier), 'by_kind': dict(by_kind),
              'invalid_kind': bad_kind, 'contradictions': contradictions, 'identity_review': review,
              'unverified_exchange_tags': len(weak), 'exchange_tags': len(ex), 'checked': checked}
    (ROOT / 'scripts' / 'labels_audit.json').write_text(json.dumps(report, indent=1) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('contradictions', 'identity_review')}, indent=1))
    for title, rows in (('CONTRADICTIONS (tagged as a hot wallet but a contract)', contradictions),
                        ('IDENTITY REVIEW (deposit contract, named entity unproven)', review)):
        if rows:
            print('\n%s:' % title)
            for c in rows:
                print('  %s  %-34s %-16s -> %s' % (c['address'], c['label'][:34], c['tagged'], c['resolves_to']))
    print('\n%d of %d exchange tags rest on memory or behaviour alone.' % (len(weak), len(ex)))


def cmd_coverage(args):
    """How much of a window's USD flow moves through addresses the registry can name.

    Coverage is a diagnostic, not the goal: the number that matters is how much *unlabelled* value sits at the top of
    the list, because that is the queue of addresses whose mislabelling could still move a headline.
    """
    from window_raw import Window
    w = Window(args.out)
    labels = load_registry()['labels']
    seen = collections.Counter()
    flow = collections.defaultdict(lambda: {'in': 0.0, 'out': 0.0})
    total = labelled = 0.0
    n = 0
    for x in w.transfers(min_usd=args.min_usd):
        n += 1
        flow[x['to']]['in'] += x['usd']
        flow[x['from']]['out'] += x['usd']
        for side in ('from', 'to'):
            a = x[side]
            total += x['usd']
            if a in labels:
                labelled += x['usd']
            else:
                seen[a] += x['usd']
    top = [{'address': a, 'usd': round(u)} for a, u in seen.most_common(args.top)]
    # Behavioural contradiction: a deposit sink is defined by never sending. One that sends heavily in this window is
    # mislabelled, and its outflow has been counted as exchange *outflow* — the sign-flipping kind of error.
    sinks = []
    for a, v in labels.items():
        if v.get('kind') != 'exchange_deposit':
            continue
        f = flow.get(a)
        if f and f['out'] >= max(args.sink_min_usd, 0.25 * f['in']):
            sinks.append({'address': a, 'label': v['label'], 'source': v.get('source'),
                          'in_usd': round(f['in']), 'out_usd': round(f['out'])})
    sinks.sort(key=lambda r: -r['out_usd'])
    out = {'window': str(args.out), 'blocks': len(w.nums), 'legs': n, 'min_usd': args.min_usd,
           'endpoint_usd_total': round(total), 'endpoint_usd_labelled': round(labelled),
           'labelled_share': round(labelled / total, 4) if total else 0.0,
           'unlabelled_addresses': len(seen), 'sinks_that_send': sinks, 'top_unlabelled': top}
    p = Path(args.out) / 'label_coverage.json'
    p.write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k not in ('top_unlabelled', 'sinks_that_send')}, indent=1))
    if sinks:
        print('\nBEHAVIOURAL CONTRADICTION — tagged a deposit sink, but sends in this window:')
        for r in sinks:
            print('  %s  in $%-14s out $%-14s %s' % (r['address'], format(r['in_usd'], ','), format(r['out_usd'], ','), r['label']))
    print('\ntop unlabelled endpoints by USD touched (the work queue):')
    for r in top[:25]:
        print('  %s  $%s' % (r['address'], format(r['usd'], ',')))
    print('\nwrote %s' % p)


def cmd_resolve(args):
    """Fetch names for the top unlabelled addresses of a window and write the ones that resolve into the registry."""
    cov = Path(args.out) / 'label_coverage.json'
    if not cov.exists():
        print('run `coverage --out %s` first' % args.out)
        return
    top = json.loads(cov.read_text())['top_unlabelled'][:args.top]
    reg = load_registry()
    added, unresolved = [], []
    for i, r in enumerate(top):
        a = r['address']
        if a in reg['labels'] and not (args.refresh and tier_rank(reg['labels'][a].get('source')) >= TIERS.index('blockscout-verified')):
            continue
        res = resolve_one(a, use_etherscan=not args.no_etherscan)
        time.sleep(args.sleep)
        if res and res.get('name'):
            kind = infer_kind(res['name'], res.get('token_symbol')) or 'protocol'
            label = res['name'] + (' (via %s)' % res['via_proxy'] if res.get('via_proxy') else '')
            put(reg, a, label, kind, res['source'], usd_touched=round(r['usd']))
            added.append({'address': a, 'name': label, 'kind': kind, 'usd': r['usd']})
        else:
            unresolved.append({'address': a, 'usd': r['usd'], 'is_contract': bool(res and res.get('is_contract'))})
        if (i + 1) % 10 == 0:
            print('  %d/%d' % (i + 1, len(top)), file=sys.stderr)
    save_registry(reg)
    print(json.dumps({'resolved': len(added), 'unresolved': len(unresolved), 'registry_size': len(reg['labels'])}, indent=1))
    for r in added:
        print('  + %s  %-42s %-10s $%s' % (r['address'], r['name'][:42], r['kind'], format(r['usd'], ',')))
    print('\nunresolved (no verified name; EOA or unverified contract) — these stay unlabelled on purpose:')
    for r in unresolved[:15]:
        print('  ? %s  $%-14s %s' % (r['address'], format(r['usd'], ','), 'contract' if r['is_contract'] else 'EOA'))


def cmd_adopt_shapes(args):
    """Turn `solver_fingerprint` hits into registry entries: the detector finds the tail, this files it.

    The unlabelled tail is regenerated every window with different addresses in it, and none of the big ones carry a
    verified source, so `resolve` returns nothing for them and hand-labelling never catches up. What the window *can*
    prove is shape: an address that receives calldata, emits no logs, never originates a transaction, and returns every
    dollar inside the same transaction is a contract that holds nothing. That is enough to say what it is *not* — not an
    exchange, not a treasury — which is the claim that protects the headline numbers.

    So the entry written here is a shape claim at the weakest provenance tier, with the window and detector in its
    source, never an identity. `verify`'s label band then shows exactly how much these entries move, and a later
    verified name overwrites them because `put` lets a stronger tier win.

    Adopting changes the address book, which is what `analysis.json` records and `verify` gates on: every window
    analysed before this becomes stale and must be re-analysed. That is the intended cost, and it is why this is
    dry-run by default.
    """
    dj = Path(args.out) / 'detectors.json'
    if not dj.exists():
        print('no detectors.json in %s — run `live_scan detect` first' % args.out)
        return
    hits = [h for h in json.loads(dj.read_text()).get('hits', []) if h['detector'] == 'solver_fingerprint']
    reg = load_registry()
    src = 'behaviour-%s-fingerprint' % dt.date.today().isoformat()
    proposed, skipped = [], []
    for h in hits:
        e = h['evidence']
        a = e['address']
        # Only where the window proves code and proves it holds nothing. An `unknown` contract-ness or a `retains`
        # shape is exactly the case a shape claim cannot settle, and guessing there is the original bug.
        if e.get('is_contract') is not True or e['shape'] not in ('pass-through', 'cycles'):
            skipped.append({'address': a, 'why': 'is_contract=%s shape=%s' % (e.get('is_contract'), e['shape'])})
            continue
        if (e.get('gross_usd') or 0) < args.min_usd:
            skipped.append({'address': a, 'why': 'gross $%.0f below threshold' % (e.get('gross_usd') or 0)})
            continue
        kind = 'mev_bot' if e.get('vanity_zeros', 0) >= 4 else 'venue'
        label = ('%s (shape: %s, %d txs, %.0f%% flat, %d counterparties, $%.0fM gross)'
                 % ({'mev_bot': 'searcher bot', 'venue': 'router or solver'}[kind], e['shape'], e['txs'],
                    100 * e['pass_through_share'], e['counterparties'], (e['gross_usd'] or 0) / 1e6))
        old = reg['labels'].get(a)
        if old and tier_rank(old.get('source')) <= tier_rank(src):
            skipped.append({'address': a, 'why': 'already held at %s' % old.get('source')})
            continue
        proposed.append({'address': a, 'kind': kind, 'label': label})
    if args.apply:
        for r in proposed:
            put(reg, r['address'], r['label'], r['kind'], src)
        save_registry(reg)
    print(json.dumps({'window': str(args.out), 'source': src, 'applied': bool(args.apply),
                      'proposed': proposed, 'skipped': skipped, 'registry_size': len(reg['labels'])}, indent=1))
    if proposed and args.apply:
        print('\nThe address book changed. Re-run `live_scan analyze` on every window you still quote, or `verify` '
              'will (correctly) refuse to compare their numbers.')


def cmd_add(args):
    reg = load_registry()
    ok = put(reg, args.address, args.label, args.kind, args.source)
    save_registry(reg)
    print(json.dumps({'written': ok, 'address': args.address.lower(), 'registry_size': len(reg['labels'])}))


def cmd_list(args):
    labels = load_registry()['labels']
    rows = [(a, v) for a, v in labels.items()
            if (not args.kind or v.get('kind') == args.kind) and (not args.source or tier_of(v.get('source')) == args.source)]
    for a, v in sorted(rows, key=lambda kv: (tier_rank(kv[1].get('source')), kv[1].get('kind') or '')):
        print('%s  %-12s %-22s %s' % (a, v.get('kind'), v.get('source'), v.get('label')))
    print('\n%d of %d entries' % (len(rows), len(labels)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name, fn in (('seed', cmd_seed), ('adopt-memory', cmd_adopt_memory), ('audit', cmd_audit),
                     ('coverage', cmd_coverage), ('resolve', cmd_resolve), ('adopt-shapes', cmd_adopt_shapes),
                     ('add', cmd_add), ('list', cmd_list)):
        s = sub.add_parser(name, help=(fn.__doc__ or '').strip().split('\n')[0])
        s.set_defaults(fn=fn)
        if name in ('coverage', 'resolve', 'adopt-shapes'):
            s.add_argument('--out', required=True, help='window directory holding raw/ and analysis.json')
        if name == 'adopt-shapes':
            s.add_argument('--min-usd', type=float, default=100e6)
            s.add_argument('--apply', action='store_true', help='write the entries (default is a dry run)')
        if name == 'coverage':
            s.add_argument('--min-usd', type=float, default=1e5)
            s.add_argument('--top', type=int, default=120)
            s.add_argument('--sink-min-usd', type=float, default=1e6, help='outflow above which a "deposit sink" is contradicted')
        if name in ('resolve', 'audit'):
            s.add_argument('--top', type=int, default=40)
            s.add_argument('--sleep', type=float, default=0.25)
            s.add_argument('--no-etherscan', action='store_true')
        if name == 'resolve':
            s.add_argument('--refresh', action='store_true', help='re-resolve entries already held at a fetched tier (use after improving the rules)')
        if name == 'audit':
            s.add_argument('--limit', type=int, default=0, help='check at most N exchange-tagged entries (0 = all)')
            s.add_argument('--recheck', action='store_true', help='also re-fetch known-canonical entries')
            s.add_argument('--book', action='store_true', help='audit the effective address book (registry + behaviour + memory), not just the registry file')
        if name == 'add':
            s.add_argument('address')
            s.add_argument('--label', required=True)
            s.add_argument('--kind', required=True, choices=KINDS)
            s.add_argument('--source', default='known-canonical')
        if name == 'list':
            s.add_argument('--kind', choices=KINDS)
            s.add_argument('--source', choices=TIERS)
    a = p.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
