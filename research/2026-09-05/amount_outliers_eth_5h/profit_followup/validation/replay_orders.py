"""Replay the original order at its actual prestate and before the opening leg.

txIndex selects the state immediately BEFORE that transaction. Each actual-state
replay is checked against its mined receipt and saved transaction trace offline.
No state, calldata, sender, value, gas limit, fees, route, or block overrides.
"""
from collect import HERE, RAW, read, rpc


def call_args(t):
    args = {k: t[k] for k in ["from", "to", "gas", "value", "accessList",
                              "maxFeePerGas", "maxPriorityFeePerGas"] if k in t}
    if "maxFeePerGas" not in args:
        args["gasPrice"] = t["gasPrice"]
    args["data"] = t["input"]
    if t.get("authorizationList"):
        args["authorizationList"] = t["authorizationList"]
    return args


def main():
    episodes = read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]
    for e in episodes:
        b = read(RAW / "blocks" / f'{e["block"]}.json.gz')
        middle = b["transactions"][e["indices"][1]]
        close = b["transactions"][e["indices"][2]]
        for label, t, idx in [("actual", middle, e["indices"][1]),
                              ("without_open", middle, e["indices"][0]),
                              ("close_without_middle", close, e["indices"][1])]:
            rpc("debug_traceCall", [call_args(t), b["hash"], {
                "tracer": "callTracer", "tracerConfig": {"withLog": True},
                "txIndex": hex(idx), "timeout": "60s"}],
                HERE / "replays" / f'{e["block"]}_{label}.json.gz')
        print("Replayed", e["block"], flush=True)


if __name__ == "__main__":
    main()
