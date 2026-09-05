"""Inspect a bounded public RPC result without disclosing the endpoint key."""
import json
from pathlib import Path
import urllib.request
from onchain_probe import RPC, ROOT

rpc = RPC(ROOT / 'research/2026-09-05/diagnostic', max_credits=5000)
result = rpc.call('base', 'eth_getBlockReceipts', ['0x' + format(50905673, 'x')], allow_errors=True)
print(json.dumps({'type': type(result).__name__, 'length': len(result) if isinstance(result, list) else None,
                  'error': result if isinstance(result, dict) else None}))
