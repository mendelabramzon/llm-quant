#!/usr/bin/env python3
"""Read-only client for the Hyperliquid info API, with the pacing its rate limiter actually wants.

One class because every collector and follow-up in the perp study talks to the same endpoint. The info API is
weight-limited per IP rather than request-limited, and a 429 there is silent about which of your last hundred calls
tripped it, so the client paces deliberately, backs off on 429 and 5xx, and keeps a request/error count that the
manifests record. Nothing is authenticated; nothing is written by this module.
"""
import gzip
import json
import threading
import time
import urllib.error
import urllib.request

INFO_URL = 'https://api.hyperliquid.xyz/info'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'


class APIError(Exception):
    pass


class Info:
    def __init__(self, url=INFO_URL, interval=0.09, timeout=45, retries=5):
        self.url, self.interval, self.timeout, self.retries = url, interval, timeout, retries
        self.lock = threading.Lock()
        self.next_at = 0.0
        self.requests = 0
        self.errors = 0
        self.throttled = 0

    def post(self, body):
        last = None
        for attempt in range(self.retries + 1):
            with self.lock:
                delay = max(0.0, self.next_at - time.monotonic())
                self.next_at = time.monotonic() + delay + self.interval
                self.requests += 1
            if delay:
                time.sleep(delay)
            req = urllib.request.Request(
                self.url, data=json.dumps(body).encode(),
                headers={'Content-Type': 'application/json', 'Accept-Encoding': 'gzip', 'User-Agent': UA})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    raw = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        raw = gzip.decompress(raw)
                return json.loads(raw)
            except urllib.error.HTTPError as e:
                last = 'HTTP %d' % e.code
                with self.lock:
                    self.errors += 1
                    if e.code == 429:
                        self.throttled += 1
                        # The limiter is per-IP and shared across threads, so widen the global spacing rather than
                        # only sleeping this one: otherwise the other workers walk straight back into the wall.
                        self.next_at = max(self.next_at, time.monotonic() + 2.0)
                if e.code not in (429, 500, 502, 503, 504):
                    raise APIError(last)
            except Exception as e:
                last = type(e).__name__ + ': ' + str(e)[:160]
                with self.lock:
                    self.errors += 1
            time.sleep(min(8.0, 0.4 * 2 ** attempt))
        raise APIError('retry limit: %s' % last)

    def stats(self):
        return {'requests': self.requests, 'errors': self.errors, 'throttled': self.throttled}


# ---------------------------------------------------------------------------------------------- typed calls

def perp_dexes(api):
    return api.post({'type': 'perpDexs'})


def meta_and_ctxs(api, dex=''):
    return api.post({'type': 'metaAndAssetCtxs', 'dex': dex})


def l2_book(api, coin):
    return api.post({'type': 'l2Book', 'coin': coin})


def candles(api, coin, interval, start_ms, end_ms):
    return api.post({'type': 'candleSnapshot',
                     'req': {'coin': coin, 'interval': interval, 'startTime': start_ms, 'endTime': end_ms}})


def funding_history(api, coin, start_ms, end_ms=None):
    b = {'type': 'fundingHistory', 'coin': coin, 'startTime': start_ms}
    if end_ms:
        b['endTime'] = end_ms
    return api.post(b)


def predicted_fundings(api):
    return api.post({'type': 'predictedFundings'})


def all_mids(api, dex=''):
    return api.post({'type': 'allMids', 'dex': dex})
