#!/usr/bin/env python3
"""Minimal dRPC client for tracing (debug_traceTransaction / debug_traceCall / prestateTracer) and archive reads.

Infura on the local keys returns 'method not found' for debug_* and errors for historical state; the public dRPC endpoint
https://eth.drpc.org answers both. This client is read-only, does no authentication, and saves nothing but what the caller asks.
"""
import gzip
import json
import time
import urllib.error
import urllib.request

ENDPOINTS = ['https://eth.drpc.org', 'https://ethereum-rpc.publicnode.com', 'https://eth.merkle.io', 'https://1rpc.io/eth']


class Revert(Exception):
    """The node executed the call and it reverted (or the method is unsupported there): a result, not a transport failure."""


def rpc(method, params, endpoints=ENDPOINTS, timeout=120, retries=3):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    last = None
    for attempt in range(retries):
        for ep in endpoints:
            req = urllib.request.Request(ep, data=payload, headers={'Content-Type': 'application/json', 'Accept-Encoding': 'gzip', 'User-Agent': 'llm-quant research'})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                d = json.loads(body)
                if 'error' in d:
                    err = d['error']
                    msg = str(err.get('message', '')).lower()
                    if err.get('code') in (3, -32000, -32015) or 'revert' in msg or 'execution' in msg or 'invalid opcode' in msg or 'out of gas' in msg:
                        raise Revert(json.dumps(err)[:300])
                    last = '%s: %s' % (ep, json.dumps(err)[:200])
                    continue
                return d['result']
            except Revert:
                raise
            except Exception as e:
                last = '%s: %s' % (ep, str(e)[:160])
                continue
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError('all endpoints failed: ' + str(last))


def trace_tx(txhash, tracer='callTracer', config=None):
    cfg = {'tracer': tracer}
    if config:
        cfg['tracerConfig'] = config
    return rpc('debug_traceTransaction', [txhash, cfg])


def trace_call(tx, block='latest', tracer='callTracer', config=None, state_overrides=None):
    cfg = {'tracer': tracer}
    if config:
        cfg['tracerConfig'] = config
    params = [tx, block, cfg]
    if state_overrides is not None:
        params.append(state_overrides)
    return rpc('debug_traceCall', params)


if __name__ == '__main__':
    import sys
    h = sys.argv[1]
    tracer = sys.argv[2] if len(sys.argv) > 2 else 'callTracer'
    cfg = {'diffMode': True} if tracer == 'prestateTracer' else {'withLog': True, 'onlyTopCall': False}
    out = trace_tx(h, tracer, cfg)
    print(json.dumps(out))
