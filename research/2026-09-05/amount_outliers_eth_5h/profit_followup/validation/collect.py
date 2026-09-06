"""Read-only historical evidence collection. Public RPC; no wallet or submissions.

Run with `uv run python .../validation/collect.py`. Successful responses are cached.
The first Infura probe and its unavailable methods are retained separately.
"""
import gzip
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
RAW = STUDY.parent / "eth_5h" / "raw"
URL = "https://eth.drpc.org"


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as f:
        return json.load(f)


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with (gzip.open(path, "wt") if path.suffix == ".gz" else path.open("w")) as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def rpc(method, params, path=None):
    if path and path.exists():
        return read(path)
    for attempt in range(4):
        req = urllib.request.Request(URL, data=json.dumps({"jsonrpc": "2.0", "id": 1,
            "method": method, "params": params}).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                raw = response.read()
            result = json.loads(raw)
        except urllib.error.HTTPError as exc:
            result = {"error": {"http_status": exc.code, "body": exc.read().decode(errors="replace")[:500]}}
        except Exception as exc:
            result = {"error": {"exception": type(exc).__name__}}
        log = {"provider": URL, "observed_at": datetime.now(timezone.utc).isoformat(),
               "method": method, "params": params, "attempt": attempt + 1,
               "elapsed_seconds": round(time.time()-started, 3), "error": result.get("error")}
        with (HERE / "public_rpc_requests.jsonl").open("a") as f:
            f.write(json.dumps(log) + "\n")
        time.sleep(.25)
        if "result" in result and result["result"] is not None:
            if path:
                save(path, result["result"])
            return result["result"]
        if attempt < 3:
            time.sleep(1 + attempt)
    raise RuntimeError(json.dumps(log))


def cached(method, params):
    key = hashlib.sha256(json.dumps([method, params], sort_keys=True).encode()).hexdigest()
    return rpc(method, params, HERE / "calls" / (key + ".json.gz"))


def main():
    es = read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]
    for e in es:
        b = rpc("eth_getBlockByNumber", [hex(e["block"]), False], HERE / "headers" / f'{e["block"]}.json.gz')
        assert b["hash"] == e["block_hash"]
        for h in e["hashes"]:
            receipt = rpc("eth_getTransactionReceipt", [h], HERE / "receipts" / (h + ".json.gz"))
            assert receipt["blockHash"] == b["hash"] and int(receipt["status"], 16) == 1
            rpc("debug_traceTransaction", [h, {"tracer": "callTracer", "timeout": "60s"}], HERE / "traces" / (h + ".json.gz"))
            rpc("debug_traceTransaction", [h, {"tracer": "prestateTracer", "tracerConfig": {"diffMode": True}, "timeout": "60s"}], HERE / "diffs" / (h + ".json.gz"))
        print("Collected", e["block"], flush=True)


if __name__ == "__main__":
    main()
