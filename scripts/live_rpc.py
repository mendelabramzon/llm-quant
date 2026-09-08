#!/usr/bin/env python3
"""Read-only JSON-RPC client for the live scan.

Rotates across every key in the local `infura_keys.txt` (round robin; a key that answers with a quota or rate error is
parked for a minute), sends batched requests with gzip on the wire, retries transient failures, and keeps an estimated
credit count. Keys are never written anywhere; error strings are redacted before they are stored or printed.
"""
import gzip
import json
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://mainnet.infura.io/v3/'
COST = {'eth_getBlockReceipts': 1000, 'eth_getLogs': 255, 'debug_traceTransaction': 1000, 'eth_chainId': 5}
QUOTA_CODES = (-32005, -32002, -32029)


class RPCError(Exception):
    pass


def hx(v):
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


def load_keys():
    keys = re.findall(r'"([^"\s]+)"', (ROOT / 'infura_keys.txt').read_text())
    if not keys:
        raise RPCError('No keys found in infura_keys.txt')
    return keys


class RPC:
    def __init__(self, log_path=None, max_credits=6_000_000, interval=.06, timeout=90, url=None):
        self.keys = load_keys()
        # Per-network endpoint. The local keys are enabled for many EVMs, and the cross-chain scan needs several
        # clients alive at once, so the host cannot be a module global that the last caller wins.
        self.url = url or URL
        self.parked = {}
        self.i = 0
        self.lock = threading.Lock()
        self.next_at = 0.
        self.credits = 0
        self.requests = 0
        self.errors = 0
        self.max_credits, self.interval, self.timeout = max_credits, interval, timeout
        self.log_path = Path(log_path) if log_path else None
        self.per_key = {k: 0 for k in self.keys}

    def clean(self, s):
        for k in self.keys:
            s = s.replace(k, '[KEY]')
        return re.sub(r'https?://\S+', '[URL]', s)[:400]

    def _pick(self):
        now = time.monotonic()
        for _ in range(len(self.keys)):
            k = self.keys[self.i % len(self.keys)]
            self.i += 1
            if self.parked.get(k, 0) <= now:
                return k
        soonest = min(self.parked.values())
        time.sleep(max(0., soonest - now))
        return self._pick()

    def _park(self, key, seconds=60):
        self.parked[key] = time.monotonic() + seconds

    def batch(self, calls, allow_errors=False):
        estimated = sum(COST.get(m, 80) for m, _ in calls)
        last_error = None
        for attempt in range(6):
            with self.lock:
                if self.credits + estimated > self.max_credits:
                    raise RPCError('credit ceiling reached')
                self.credits += estimated
                self.requests += 1
                key = self._pick()
                self.per_key[key] += estimated
                delay = max(0., self.next_at - time.monotonic())
                self.next_at = time.monotonic() + delay + self.interval
            if delay:
                time.sleep(delay)
            payload = [{'jsonrpc': '2.0', 'id': i, 'method': m, 'params': p} for i, (m, p) in enumerate(calls)]
            req = urllib.request.Request(self.url + key, data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json', 'Accept-Encoding': 'gzip'})
            transient, error, result = False, None, None
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read()
                    if resp.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                decoded = json.loads(body)
                if isinstance(decoded, dict):
                    err = decoded.get('error') or {}
                    error = self.clean(json.dumps(decoded))
                    transient = err.get('code') in QUOTA_CODES or 'rate' in str(err.get('message', '')).lower()
                else:
                    by_id = {x['id']: x for x in decoded if isinstance(x, dict) and 'id' in x and x['id'] is not None}
                    bare = [x for x in decoded if not (isinstance(x, dict) and x.get('id') is not None)]
                    quota_bare = any(isinstance(x, dict) and x.get('code') in QUOTA_CODES for x in bare)
                    if set(by_id) != set(range(len(calls))):
                        # Infura answers a throttled key with id-less error objects, sometimes mixed with real results.
                        # Keep the unambiguous results, park the key, and refill only the missing members elsewhere.
                        if quota_bare:
                            self._park(key, 120)
                        missing = [i for i in range(len(calls)) if i not in by_id or 'result' not in by_id[i] and 'error' not in by_id[i]]
                        if by_id and attempt < 5:
                            with self.lock:
                                self.errors += 1
                            filled = {}
                            for i in missing:
                                filled[i] = self.batch([calls[i]], allow_errors=True)[0]
                            merged = []
                            for i in range(len(calls)):
                                if i in filled:
                                    merged.append(filled[i])
                                else:
                                    r = by_id[i]
                                    if 'error' in r and not allow_errors:
                                        raise RPCError(self.clean(json.dumps(r['error'])))
                                    merged.append(r if 'error' in r else r.get('result'))
                            return merged
                        error, transient = ('throttled: ' + self.clean(json.dumps(bare[:1]))) if quota_bare else 'batch id mismatch', True
                    else:
                        result = [by_id[i] for i in range(len(calls))]
                        errs = [r['error'] for r in result if 'error' in r]
                        if errs:
                            error = self.clean(json.dumps(errs))
                            quota = [e for e in errs if e.get('code') in QUOTA_CODES and 'more than' not in str(e.get('message', ''))]
                            transient = bool(quota)
                            if not quota and allow_errors:
                                return [r if 'error' in r else r.get('result') for r in result]
                            if not quota and not allow_errors:
                                raise RPCError(error)
                            result = None
            except urllib.error.HTTPError as exc:
                error, transient = 'HTTP ' + str(exc.code), exc.code in (429, 500, 502, 503, 504)
            except RPCError:
                raise
            except Exception as exc:
                error, transient = type(exc).__name__ + ': ' + self.clean(str(exc)), True
            if result is not None:
                return [r.get('result') for r in result]
            last_error = error
            with self.lock:
                self.errors += 1
            if self.log_path:
                with self.lock, self.log_path.open('a') as f:
                    f.write(json.dumps({'t': time.time(), 'attempt': attempt, 'error': error, 'methods': sorted({m for m, _ in calls})}) + '\n')
            if transient:
                self._park(key, 120 if 'HTTP 429' in str(error) or '-32005' in str(error) or 'throttled' in str(error) else 15)
                time.sleep(min(8, .5 * 2 ** attempt))
                continue
            raise RPCError(str(error))
        raise RPCError('retry limit: ' + str(last_error))

    def call(self, method, params, allow_errors=False):
        return self.batch([(method, params)], allow_errors)[0]

    def eth_call(self, to, data, block='latest'):
        return self.call('eth_call', [{'to': to, 'data': data}, block])

    def eth_calls(self, items, block='latest'):
        """items: list of (to, data). Returns list of hex results or None per item (errors tolerated)."""
        out = []
        for i in range(0, len(items), 20):
            part = items[i:i + 20]
            res = self.batch([('eth_call', [{'to': to, 'data': data}, block]) for to, data in part], allow_errors=True)
            out.extend(None if (isinstance(r, dict) and 'error' in r) or r in (None, '0x') else r for r in res)
        return out

    def stats(self):
        return {'credits': self.credits, 'requests': self.requests, 'errors': self.errors, 'keys': len(self.keys)}


def word(data, i):
    """i-th 32-byte word of a hex data field as int."""
    s = data[2:] if data.startswith('0x') else data
    return int(s[i * 64:(i + 1) * 64] or '0', 16)


def sword(data, i, bits=256):
    v = word(data, i)
    return v - (1 << bits) if v >= (1 << (bits - 1)) else v


def topic_addr(t):
    return '0x' + t[-40:]


def topic_int(t, bits=256):
    v = int(t, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def enc_addr(a):
    return a[2:].lower().rjust(64, '0')


def enc_uint(v):
    return hex(v)[2:].rjust(64, '0')
