"""Check matched LP positions at pre-open, pre-middle, and post-close state."""
from eth_abi import encode, decode
from collect import HERE, rpc, read, save
from check_balances import sel
from mechanics import kh, EKUBO
from reconcile import HELPER, hx


def word(n):
    return (n % 2**256).to_bytes(32, "big")


def main():
    es = {e["block"]: e for e in read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]}
    out = []
    for m in read(HERE / "mechanics.json"):
        e = es[int(m["block"])]
        queries = []
        for pos in m["known_uniswap_positions"]:
            address, pool, owner, lower, upper, salt = pos["position"]
            pk = bytes.fromhex(owner[2:]) + int(lower).to_bytes(3, "big", signed=True) + int(upper).to_bytes(3, "big", signed=True)
            if pool:
                pid = kh(pk + word(int(salt, 16)))
                poolbase = int.from_bytes(kh(bytes.fromhex(pool[2:]) + word(6)), "big")
                slot = kh(pid + word(poolbase + 6))
                data = sel("extsload(bytes32)") + slot
                venue = "Uniswap v4"
            else:
                data = sel("positions(bytes32)") + kh(pk)
                slot = None
                venue = "Uniswap v3"
            queries.append({"address": address, "data": "0x" + data.hex(), "venue": venue,
                "liquidity_expected": pos["liquidity_raw"], "slot": "0x"+slot.hex() if slot else None})
        for pos in m["new_ekubo_matches"]:
            a, pool = pos["address"], bytes.fromhex(pos["pool_id"][2:])
            if a == EKUBO[0]:
                pid = bytes.fromhex(pos["position"][2:])
                slot = kh(kh(pid + pool + encode(["address"], [HELPER])) + word(1))
            else:
                salt, lower, upper = pos["position"]
                pid = kh(kh(bytes.fromhex(salt[2:]) + encode(["address"], [HELPER])) + kh(encode(["int32", "int32"], [int(lower), int(upper)])))
                slot = kh(pid + kh(pool + word(4)))
            data = sel("sload()") + slot
            queries.append({"address": a, "data": "0x"+data.hex(), "slot": "0x"+slot.hex(),
                "venue": "Ekubo v3" if a == EKUBO[0] else "Ekubo v2", "liquidity_expected": pos["liquidity"]})
        assert len(queries) <= 1  # Cache names are per episode/phase.
        for q in queries:
            vals = {}
            for label, idx in [("before", e["indices"][0]), ("active", e["indices"][1]), ("after", e["indices"][2]+1)]:
                r = rpc("debug_traceCall", [{"to": q["address"], "data": q["data"], "gas": hex(1000000)}, e["block_hash"],
                    {"tracer": "callTracer", "txIndex": hex(idx)}],
                    HERE / "position_calls" / f'{e["block"]}_{label}.json.gz')
                assert not r.get("error")
                if q["venue"] == "Uniswap v3":
                    res = decode(["uint128", "uint256", "uint256", "uint128", "uint128"], bytes.fromhex(r["output"][2:]))
                    vals[label] = {"liquidity": str(res[0]), "tokens_owed0": str(res[3]), "tokens_owed1": str(res[4])}
                else:
                    n = hx(r["output"])
                    liquidity = n >> 128 if q["venue"] == "Ekubo v3" else n & (2**128-1)
                    vals[label] = {"liquidity": str(liquidity), "word": r["output"]}
            assert int(vals["before"]["liquidity"]) == 0
            assert int(vals["active"]["liquidity"]) == int(q["liquidity_expected"])
            assert int(vals["after"]["liquidity"]) == 0
            if q["venue"] == "Uniswap v3":
                assert all(int(vals[phase][k]) == 0 for phase in ["before", "after"] for k in ["tokens_owed0", "tokens_owed1"])
            out.append({"block": e["block"], **q, "states": vals})
            save(HERE / "positions.json", out)
            print("Position closed", e["block"], q["venue"], flush=True)


if __name__ == "__main__":
    main()
