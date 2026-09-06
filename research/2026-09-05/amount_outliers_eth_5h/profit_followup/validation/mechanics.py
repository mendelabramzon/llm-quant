"""Decode historically verified Ekubo ABIs and measure LP fees in exact units."""
from collections import defaultdict
from eth_abi import decode as abi_decode, encode
from Crypto.Hash import keccak
from collect import HERE, read, save
from reconcile import HELPER, frames, hx, decode

EKUBO = ["0x00000000000014aa86c5d3c41765bb24e11bd701", "0xe0e0e08a6a4b9dc7bd67bcb7aade5cf48157d444"]


def typ(x):
    return "(" + ",".join(typ(v) for v in x["components"]) + ")" + x["type"][5:] if x["type"].startswith("tuple") else x["type"]


def kh(b):
    return keccak.new(digest_bits=256, data=b).digest()


def stringify(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, bytes):
        return "0x" + v.hex()
    if isinstance(v, (list, tuple)):
        return [stringify(x) for x in v]
    if isinstance(v, dict):
        return {k: stringify(x) for k, x in v.items()}
    if isinstance(v, int):
        return str(v)
    return v


def signed128(x):
    return x - 2**128 if x >= 2**127 else x


def packed_delta(data):
    x = hx(data)
    return signed128(x >> 128), signed128(x & (2**128-1))


def main():
    abis = {a: json_abi(a) for a in EKUBO}
    event_maps, function_maps = {}, {}
    for a, abi in abis.items():
        em, fm = {}, {}
        for item in abi:
            if item["type"] not in ["event", "function"]:
                continue
            sig = item["name"] + "(" + ",".join(typ(v) for v in item["inputs"]) + ")"
            (em if item["type"] == "event" else fm)["0x" + kh(sig.encode()).hex()[:(64 if item["type"] == "event" else 8)]] = item
        event_maps[a], function_maps[a] = em, fm
    es = read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]
    result = []
    for e in es:
        events, fees, swaps = [], [], set()
        adds, removes = {}, {}
        for leg, h in enumerate(e["hashes"]):
            receipt = read(HERE / "receipts" / (h + ".json.gz"))
            trace = read(HERE / "traces" / (h + ".json.gz"))
            for l in receipt["logs"]:
                a = l["address"]
                if a in EKUBO:
                    if l.get("topics") and l["topics"][0] in event_maps[a]:
                        spec = event_maps[a][l["topics"][0]]
                        assert not any(v["indexed"] for v in spec["inputs"])
                        vals = abi_decode([typ(v) for v in spec["inputs"]], bytes.fromhex(l["data"][2:]))
                        row = dict(zip([v["name"] for v in spec["inputs"]], vals))
                        events.append(dict(leg=leg, address=a, event=spec["name"], **row))
                        if spec["name"] == "PositionUpdated" and row["locker"] == HELPER:
                            if a == EKUBO[0]:
                                pos, liquidity = row["positionId"], row["liquidityDelta"]
                            else:
                                pos, bounds, liquidity = row["params"]
                                pos = (pos, *bounds)
                            key = (a, row["poolId"], pos)
                            if leg == 0 and liquidity > 0:
                                adds[key] = liquidity
                            elif leg == 2 and liquidity < 0:
                                removes[key] = liquidity
                        if spec["name"] == "PositionFeesCollected":
                            fees.append({"venue": "Ekubo", "address": a, "leg": leg,
                                "pool_id": row["poolId"], "amount0": row["amount0"], "amount1": row["amount1"]})
                    elif not l.get("topics") and leg == 1:
                        # Verified Core assembly emits packed swap data with log0:
                        # 20-byte locker, 32-byte poolId, then deltas/state.
                        data = bytes.fromhex(l["data"][2:])
                        if len(data) >= 52:
                            swaps.add((a, data[20:52]))
            for c in frames(trace):
                a, data = c.get("to"), c.get("input", "")
                if c["type"] != "CALL" or c["from"] != HELPER:
                    continue
                if a == "0x000000000004444c5dc75cb358380d2e3de08a90" and data.startswith("0x5a6bcfda"):
                    key, params, _ = abi_decode(["(address,address,uint24,int24,address)", "(int24,int24,int256,bytes32)", "bytes"], bytes.fromhex(data[10:]))
                    caller, accrued = abi_decode(["int256", "int256"], bytes.fromhex(c["output"][2:]))
                    f0, f1 = packed_delta(hex(accrued % 2**256))
                    if f0 or f1:
                        fees.append({"venue": "Uniswap v4", "address": a, "leg": leg,
                            "token0": key[0], "token1": key[1], "fee_pips": key[2],
                            "amount0": f0, "amount1": f1})
                elif a in EKUBO and data[:10] in function_maps[a]:
                    spec = function_maps[a][data[:10]]
                    if spec["name"] == "collectFees":
                        vals = abi_decode([typ(v) for v in spec["inputs"]], bytes.fromhex(data[10:]))
                        poolkey = vals[0]
                        poolid = kh(encode(["address", "address", "bytes32"], poolkey))
                        for f in fees:
                            if f["address"] == a and f["leg"] == leg and f["pool_id"] == poolid:
                                f.update(token0=poolkey[0], token1=poolkey[1])
            if leg == 2:
                # For v3, collect includes principal withdrawn by burn.
                burns = defaultdict(lambda: [0, 0])
                for l in receipt["logs"]:
                    v = decode(l)
                    if v["family"] == "V3Burn":
                        burns[l["address"]] = [int(v["amount0_raw"]), int(v["amount1_raw"])]
                    if v["family"] == "V3Collect":
                        principal = burns[l["address"]]
                        _, amount0, amount1 = abi_decode(["address", "uint128", "uint128"], bytes.fromhex(l["data"][2:]))
                        fees.append({"venue": "Uniswap v3", "address": l["address"], "leg": leg,
                            "amount0": amount0-principal[0], "amount1": amount1-principal[1]})
        matches = [{"address": k[0], "pool_id": k[1], "position": k[2], "liquidity": v,
                    "middle_swap_same_pool": k[:2] in swaps}
                   for k, v in adds.items() if removes.get(k) == -v]
        result.append({"block": e["block"], "known_uniswap_positions": e["matched_liquidity_positions"],
            "new_ekubo_matches": matches, "ekubo_events": events, "lp_fees": fees})
    save(HERE / "mechanics.json", stringify(result))
    for r in result:
        print(r["block"], len(r["known_uniswap_positions"]), len(r["new_ekubo_matches"]), stringify(r["lp_fees"]))


def json_abi(a):
    import json
    return json.loads(read(HERE / "sources" / (a + ".json.gz"))["result"][0]["ABI"])


if __name__ == "__main__":
    main()
