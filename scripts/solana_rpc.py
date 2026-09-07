#!/usr/bin/env python3
"""Solana JSON-RPC client over the local GetBlock access tokens (getblock_keys.json, gitignored).

Round-robins every request over all tokens (EU host go.getblock.io and US host go.getblock.us), sends a browser-like
User-Agent (the US host answers 403 to python-urllib's default), retries transport failures (IncompleteRead is common
above ~10 concurrent block downloads; the cap observed from this machine is ~2.7 MB/s total whatever the concurrency),
parks a token for a while after HTTP 429/403, and falls back to the public mainnet-beta endpoint as a last resort.
Read-only. Tokens are never written to outputs; `stats()` reports per-endpoint request counts only.
"""
import gzip
import http.client
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = 'https://api.mainnet-beta.solana.com'
HEADERS = {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip', 'User-Agent': 'Mozilla/5.0 (Macintosh) llm-quant research (read-only)'}


class RpcError(Exception):
    """The node answered with a JSON-RPC error object (a result, not a transport failure)."""

    def __init__(self, err):
        super().__init__(json.dumps(err)[:300])
        self.err = err
        self.code = err.get('code') if isinstance(err, dict) else None


def load_endpoints(path=ROOT / 'getblock_keys.json'):
    keys = json.loads(Path(path).read_text())
    eps = ['https://go.getblock.io/%s/' % k for k in keys.get('eu', [])]
    eps += ['https://go.getblock.us/%s/' % k for k in keys.get('us', [])]
    return eps


class Client:
    def __init__(self, endpoints=None, public_fallback=True, park_seconds=30):
        self.endpoints = list(endpoints or load_endpoints())
        if not self.endpoints:
            raise RuntimeError('no GetBlock tokens found in getblock_keys.json')
        self.public_fallback = public_fallback
        self.park_seconds = park_seconds
        self.lock = threading.Lock()
        self.i = 0
        self.parked = {}          # endpoint -> unix time when usable again
        self.counts = {}          # endpoint index -> requests
        self.errors = []          # (utc, endpoint index, method, error) without tokens
        self.bytes = 0

    def _pick(self):
        with self.lock:
            now = time.time()
            for _ in range(len(self.endpoints)):
                ep = self.endpoints[self.i % len(self.endpoints)]
                idx = self.i % len(self.endpoints)
                self.i += 1
                if self.parked.get(ep, 0) <= now:
                    return idx, ep
            return None, None

    def _park(self, ep, seconds=None):
        with self.lock:
            self.parked[ep] = time.time() + (seconds or self.park_seconds)

    def call(self, method, params=None, timeout=120, retries=6):
        payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or []}).encode()
        last = None
        for attempt in range(retries):
            idx, ep = self._pick()
            if ep is None:
                if self.public_fallback:
                    idx, ep = 'public', PUBLIC
                else:
                    time.sleep(2)
                    continue
            req = urllib.request.Request(ep, data=payload, headers=HEADERS)
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                with self.lock:
                    self.counts[idx] = self.counts.get(idx, 0) + 1
                    self.bytes += len(body)
                d = json.loads(body)
                if 'error' in d:
                    err = d['error']
                    code = err.get('code') if isinstance(err, dict) else None
                    if code in (429, -32429) or 'rate' in str(err).lower():
                        self._park(ep)
                        last = 'rate limited'
                        continue
                    raise RpcError(err)
                return d['result']
            except RpcError:
                raise
            except urllib.error.HTTPError as e:
                last = 'HTTP %s' % e.code
                if e.code in (429, 403, 402):
                    self._park(ep, 60 if e.code != 429 else self.park_seconds)
                elif e.code >= 500:
                    self._park(ep, 5)
            except (http.client.IncompleteRead, http.client.RemoteDisconnected, ConnectionResetError, TimeoutError) as e:
                last = type(e).__name__
            except Exception as e:
                last = '%s: %s' % (type(e).__name__, str(e)[:120])
            with self.lock:
                self.errors.append((time.time(), idx, method, last))
            time.sleep(min(8, 0.5 * (attempt + 1)))
        raise RuntimeError('%s failed after %d attempts: %s' % (method, retries, last))

    def stats(self):
        return {'requests_by_endpoint': {str(k): v for k, v in sorted(self.counts.items(), key=lambda kv: str(kv[0]))},
                'requests': sum(self.counts.values()), 'transport_errors': len(self.errors), 'bytes_decoded': self.bytes}


_default = None


def rpc(method, params=None, **kw):
    global _default
    if _default is None:
        _default = Client()
    return _default.call(method, params, **kw)


if __name__ == '__main__':
    import sys
    c = Client()
    m = sys.argv[1] if len(sys.argv) > 1 else 'getSlot'
    p = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [{'commitment': 'finalized'}]
    print(json.dumps(c.call(m, p), indent=1)[:4000])
    print(c.stats())
