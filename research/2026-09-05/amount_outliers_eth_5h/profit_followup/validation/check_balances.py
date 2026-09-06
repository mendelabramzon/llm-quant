"""Historical view calls before opening and immediately after closing.

Multicall executes balanceOf/scaledBalanceOf/getUserAccountData at exact txIndex.
This complements the event ledger with state checks of underlying cash and claims.
Dependencies: eth-abi, pycryptodome (already used in this research environment).
"""
from eth_abi import encode, decode
from Crypto.Hash import keccak
from collect import HERE, RAW, read, rpc, save
from reconcile import ACTOR, OUTER, HELPER, GROUP, WETH, tokens, hx

MULTICALL = "0xca11bde05977b3631167028862be2a173976ca11"
AAVE = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"


def sel(signature):
    return keccak.new(digest_bits=256, data=signature.encode()).digest()[:4]


def main():
    es = read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]
    all_tokens = set()
    for e in es:
        for h in [e["hashes"][0], e["hashes"][2]]:
            all_tokens.update(tok for (a, tok) in tokens(read(HERE / "receipts" / (h + ".json.gz"))["logs"]) if a in GROUP)
    # Every token moved into/out of a controlled account, including zero-net debt.
    queries = []
    for tok in sorted(all_tokens):
        for a in sorted(GROUP):
            queries.append({"target": tok, "function": "balanceOf(address)", "account": a})
        queries.append({"target": tok, "function": "scaledBalanceOf(address)", "account": HELPER})
        for f in ["decimals()", "symbol()"]:
            queries.append({"target": tok, "function": f})
    for a in sorted(GROUP):
        queries.append({"target": AAVE, "function": "getUserAccountData(address)", "account": a})
        queries.append({"target": MULTICALL, "function": "getEthBalance(address)", "account": a})
    calls = [(q["target"], sel(q["function"]) + (encode(["address"], [q["account"]]) if "account" in q else b"")) for q in queries]
    data = "0x" + (sel("tryAggregate(bool,(address,bytes)[])") + encode(["bool", "(address,bytes)[]"], [False, calls])).hex()
    output = []
    for e in es:
        b = read(RAW / "blocks" / f'{e["block"]}.json.gz')
        states = {}
        for label, idx in [("before", e["indices"][0]), ("after", e["indices"][2]+1)]:
            assert idx < len(b["transactions"])
            r = rpc("debug_traceCall", [{"to": MULTICALL, "data": data, "gas": hex(10000000)}, b["hash"],
                {"tracer": "callTracer", "txIndex": hex(idx), "timeout": "60s"}],
                HERE / "balance_calls" / f'{e["block"]}_{label}.json.gz')
            assert not r.get("error"), (e["block"], label, r.get("error"))
            results = decode(["(bool,bytes)[]"], bytes.fromhex(r["output"][2:]))[0]
            assert len(results) == len(queries)
            vals = []
            for q, (success, v) in zip(queries, results):
                item = dict(q, success=success, output="0x" + v.hex())
                if success:
                    if q["function"] == "getUserAccountData(address)":
                        item["values"] = [str(x) for x in decode(["uint256"]*6, v)]
                    elif q["function"] == "symbol()":
                        try:
                            item["value"] = decode(["string"], v)[0]
                        except Exception:
                            item["value"] = v.rstrip(b"\x00").decode(errors="replace")
                    else:
                        item["value"] = str(int.from_bytes(v, "big"))
                else:
                    assert q["function"] == "scaledBalanceOf(address)", item
                vals.append(item)
            states[label] = vals
        deltas = []
        for pre, post in zip(states["before"], states["after"]):
            if pre["success"] and pre["function"] in ["balanceOf(address)", "scaledBalanceOf(address)", "getEthBalance(address)"]:
                deltas.append({k: pre[k] for k in ["target", "function", "account"]} | {
                    "before_raw": pre["value"], "after_raw": post["value"], "delta_raw": str(int(post["value"])-int(pre["value"]))})
        output.append({"block": e["block"], "before_tx_index": e["indices"][0],
            "after_tx_index": e["indices"][2]+1, "states": states, "deltas": deltas})
        save(HERE / "balances.json", output)
        print("Balances", e["block"], flush=True)


if __name__ == "__main__":
    main()
