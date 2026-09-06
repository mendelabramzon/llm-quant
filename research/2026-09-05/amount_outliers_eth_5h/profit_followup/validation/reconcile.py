"""Offline exact-unit accounting and falsification checks over saved RPC data."""
from collections import Counter, defaultdict
from decimal import Decimal as D
import csv
import bisect
import json
import statistics
import sys
from collect import HERE, STUDY, RAW, read, save

sys.path.insert(0, str(STUDY / "replay"))
from analyze_onchain import decode

ACTOR = "0x654fae4aa229d104cabead47e56703f58b174be4"
OUTER = "0x000000000035b5e5ad9019092c665357240f594e"
HELPER = "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a"
GROUP = {ACTOR, OUTER, HELPER}
WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def hx(n):
    return int(n, 16) if isinstance(n, str) else n


def frames(t):
    # A parent's revert rolls back all descendants too.
    if t.get("error"):
        return
    yield t
    for c in t.get("calls", []):
        yield from frames(c)


def logs(t):
    return sorted([l for c in frames(t) for l in c.get("logs", [])], key=lambda l: hx(l["index"]))


def log_shape(l):
    return (l["address"].lower(), tuple(l["topics"]), l["data"])


def strip_logs(t):
    return {k: [strip_logs(c) for c in v] if k == "calls" else v for k, v in t.items() if k != "logs"}


def tokens(ll):
    nets = defaultdict(int)
    for l in ll:
        if len(l.get("topics", [])) == 3 and l["topics"][0] == TRANSFER and len(l["data"]) == 66:
            s, r = ("0x" + topic[-40:] for topic in l["topics"][1:])
            n = hx(l["data"])
            nets[(s, l["address"])] -= n
            nets[(r, l["address"])] += n
    return nets


def native(t):
    nets = defaultdict(int)
    transfers = []
    for c in frames(t):
        n = hx(c.get("value", "0x0"))
        if n and c["type"] in ("CALL", "CREATE", "CREATE2", "SELFDESTRUCT"):
            nets[c["from"]] -= n
            nets[c["to"]] += n
            transfers.append({"from": c["from"], "to": c["to"], "wei": str(n), "type": c["type"]})
    return nets, transfers


def balance_diff(d, a):
    pre = d.get("pre", {}).get(a, {})
    post = d.get("post", {}).get(a, {})
    if "balance" not in post:
        return 0  # Unchanged field omitted in geth diff mode (no controlled account deletion).
    return hx(post["balance"]) - hx(pre.get("balance", "0x0"))


def main():
    episodes = read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]
    marks = sorted((v["timestamp"], D(v["usd"])) for v in read(STUDY / "prices.json")["hourly"]["ETH"])
    out = []
    for e in episodes:
        b = read(HERE / "headers" / f'{e["block"]}.json.gz')
        ll, native_nets, payments, gas, checks = [], defaultdict(int), [], 0, []
        for h in [e["hashes"][0], e["hashes"][2]]:
            r = read(HERE / "receipts" / (h + ".json.gz"))
            t = read(HERE / "traces" / (h + ".json.gz"))
            d = read(HERE / "diffs" / (h + ".json.gz"))
            assert r["blockHash"] == e["block_hash"] == b["hash"]
            assert hx(r["status"]) == 1 and not t.get("error")
            assert hx(r["gasUsed"]) == hx(t["gasUsed"])
            assert hx(r["effectiveGasPrice"]) == hx(b["baseFeePerGas"])
            fee = hx(r["gasUsed"]) * hx(r["effectiveGasPrice"])
            gas += fee
            nn, pp = native(t)
            for a in GROUP:
                actual = balance_diff(d, a)
                expected = nn[a] - (fee if a == ACTOR else 0)
                assert actual == expected, (h, a, actual, expected)
                native_nets[a] += actual
            payments += pp
            ll += r["logs"]
            checks.append(h)
        tn = tokens(ll)
        wt = sum(v for (a, token), v in tn.items() if a in GROUP and token == WETH)
        outer_wt = tn[(OUTER, WETH)]
        assert D(outer_wt) / D(10**18) == D(e["outer_contract_weth_cash_change"])
        bribes = sum(int(p["wei"]) for p in payments if p["from"] in GROUP and p["to"] == b["miner"])
        assert len(payments) == 1 and int(payments[0]["wei"]) == bribes
        net = wt + sum(native_nets.values())
        assert net == wt - bribes - gas
        # Reuse the frozen study's NEXT hourly endpoint mark, solely for display.
        mark = marks[min(bisect.bisect_left([t for t, _ in marks], hx(b["timestamp"])), len(marks)-1)][1]
        row = {"block": e["block"], "hashes": e["hashes"], "indices": e["indices"],
               "coinbase": b["miner"], "gross_weth_wei": str(wt), "outer_weth_wei": str(outer_wt),
               "helper_weth_wei": str(wt - outer_wt), "coinbase_payment_wei": str(bribes),
               "gas_wei": str(gas), "retained_eth_wei": str(net),
               "eth_usd_study_mark": str(mark),
               "gross_usd_study_mark": str(D(wt) / D(10**18) * mark),
               "coinbase_usd_study_mark": str(D(bribes) / D(10**18) * mark),
               "gas_usd_study_mark": str(D(gas) / D(10**18) * mark),
               "retained_usd_study_mark": str(D(net) / D(10**18) * mark),
               "native_deltas_wei": {a: str(v) for a, v in native_nets.items()},
               "other_token_deltas_raw": [{"account": a, "token": token, "delta": str(v)}
                    for (a, token), v in sorted(tn.items()) if a in GROUP and token != WETH and v],
               "gas_and_native_state_checks_passed": checks}
        rp = HERE / "replays" / f'{e["block"]}_actual.json.gz'
        if rp.exists():
            actual = read(rp)
            recorded = read(HERE / "traces" / (e["hashes"][1] + ".json.gz"))
            receipt = read(HERE / "receipts" / (e["hashes"][1] + ".json.gz"))
            # Exact gas and ordered receipt-log match are mandatory, not just success.
            assert hx(actual["gasUsed"]) == hx(receipt["gasUsed"])
            assert [log_shape(l) for l in logs(actual)] == [log_shape(l) for l in receipt["logs"]]
            assert strip_logs(actual) == recorded
            cf = read(HERE / "replays" / f'{e["block"]}_without_open.json.gz')
            at, ct = tokens(logs(actual)), tokens(logs(cf))
            impacts = [{"account": a, "token": token, "actual_raw": str(at.get((a, token), 0)),
                        "without_open_raw": str(ct.get((a, token), 0)),
                        "without_open_minus_actual_raw": str(ct.get((a, token), 0)-at.get((a, token), 0))}
                       for a, token in sorted(set(at) | set(ct)) if at.get((a, token), 0) != ct.get((a, token), 0)]
            row["middle_replay"] = {"actual_exact_trace_gas_logs_match": True,
                "without_open_success": not bool(cf.get("error")), "without_open_error": cf.get("error"),
                "actual_gas_used": hx(actual["gasUsed"]), "without_open_gas_used": hx(cf["gasUsed"]),
                "changed_token_cashflows": impacts}
            cm = read(HERE / "replays" / f'{e["block"]}_close_without_middle.json.gz')
            row["close_without_middle"] = {"success": not bool(cm.get("error")), "error": cm.get("error")}
            if not cm.get("error"):
                opening_logs = read(HERE / "receipts" / (e["hashes"][0] + ".json.gz"))["logs"]
                cmn = tokens(opening_logs + logs(cm))
                row["close_without_middle"]["gross_weth_wei"] = str(sum(v for (a, tok), v in cmn.items() if a in GROUP and tok == WETH))
        out.append(row)
    sums = {k: str(sum(int(r[k]) for r in out)) for k in ["gross_weth_wei", "coinbase_payment_wei", "gas_wei", "retained_eth_wei"]}
    sums.update(episodes=len(out), positive_episodes=sum(int(r["retained_eth_wei"]) > 0 for r in out),
        median_retained_eth=str(D(statistics.median(int(r["retained_eth_wei"]) for r in out)) / D(10**18)),
        retained_usd_study_marks=str(sum(D(r["retained_usd_study_mark"]) for r in out)))
    save(HERE / "ledger.json", {"accounting_group": sorted(GROUP), "summary": sums, "episodes": out})
    with (HERE / "ledger.csv").open("w") as f:
        cols = ["block", "gross_weth_wei", "coinbase_payment_wei", "gas_wei", "retained_eth_wei", "retained_usd_study_mark"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print(json.dumps(sums, indent=2))
    print("All nonzero other-token changes are preserved in ledger.json.")


if __name__ == "__main__":
    main()
