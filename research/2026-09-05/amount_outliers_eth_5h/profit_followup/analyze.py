"""Offline follow-up for profit hypotheses; leaves the frozen study unchanged.

Run from any directory with Python and the study's existing pycryptodome dependency.
Outputs descriptive evidence, never a realized-PnL estimate. No RPC requests.
"""
from collections import Counter, defaultdict
from decimal import Decimal as D
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RAW = STUDY.parent / "eth_5h" / "raw"
sys.path.insert(0, str(STUDY / "replay"))
from analyze_onchain import decode, address
from signatures import family

ACTOR = "0x654fae4aa229d104cabead47e56703f58b174be4"
AAVE = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as f:
        return json.load(f)


def load_rows(path):
    with gzip.open(path, "rt") as f:
        for line in f:
            yield json.loads(line)


def total(rows, key="pc"):
    return sum((D(r[key]) for r in rows), D(0))


def position_key(emitter, event):
    return (emitter, event.get("pool_id"), event["owner"],
            event["tick_lower"], event["tick_upper"], event.get("salt"))


rows = list(load_rows(STUDY / "txs_big.jsonl.gz"))
types = read(STUDY / "types_by_hash.json.gz")
matches = read(STUDY / "all_matches_by_hash.json.gz")
by_hash = {r["h"]: r for r in rows}
evidence = {"scope": "Saved five-hour Ethereum window only; retrospective marks; no realized PnL",
            "inputs_sha256": {}, "primary_types": {}, "overlaps": {}}
for name in ["txs_big.jsonl.gz", "types_by_hash.json.gz", "all_matches_by_hash.json.gz"]:
    evidence["inputs_sha256"][name] = hashlib.sha256((STUDY / name).read_bytes()).hexdigest()
for name in sorted(set(types.values())):
    rr = [r for r in rows if types[r["h"]] == name]
    operators = defaultdict(list)
    for r in rr:
        operators[(r["from"], r["to"])].append(r)
    evidence["primary_types"][name] = {
        "count": len(rr), "sum_largest_change_usd": total(rr),
        "top_sender_destination_pairs": [
            {"sender": pair[0], "destination": pair[1], "count": len(group),
             "sum_largest_change_usd": total(group)}
            for pair, group in sorted(operators.items(), key=lambda x: -total(x[1]))[:3]]}
for name in ["sandwich_attack", "sandwich_victim", "liquidity_with_swap", "flash_loan_arbitrage"]:
    rr = [r for r in rows if name in matches[r["h"]]]
    evidence["overlaps"][name] = {"count": len(rr), "primary_labels": Counter(types[r["h"]] for r in rr)}

actor_rows = [r for r in rows if r["from"] == ACTOR]
blocks = defaultdict(list)
for r in actor_rows:
    blocks[r["b"]].append(r)
episodes = []
for block_number, rr in sorted(blocks.items()):
    rr.sort(key=lambda r: r["i"])
    assert len(rr) == 2 and rr[1]["i"] - rr[0]["i"] == 2
    block = read(RAW / "blocks" / f"{block_number}.json.gz")
    logs = read(RAW / "logs" / f"{block_number}.json.gz")
    middle = block["transactions"][rr[0]["i"] + 1]
    deposits, removals, middle_pools, lending = {}, {}, set(), []
    for log in logs:
        index = int(log["transactionIndex"], 16)
        if not rr[0]["i"] <= index <= rr[1]["i"]:
            continue
        event = decode(log)
        if event["family"] in ["V3Mint", "V3Burn", "V4ModifyLiquidity"]:
            key = position_key(log["address"], event)
            target = deposits if index == rr[0]["i"] else removals if index == rr[1]["i"] else None
            if target is not None:
                target[key] = target.get(key, 0) + int(event["liquidity_delta"])
        if index == rr[0]["i"] + 1 and event["family"] in ["V3Swap", "V4Swap"]:
            middle_pools.add((log["address"], event.get("pool_id")))
        fam = family(log)
        if log["address"].lower() == AAVE and fam in ["AaveSupply", "AaveBorrow", "AaveRepay", "AaveWithdraw"]:
            words = [int(log["data"][i:i+64], 16) for i in range(2, len(log["data"]), 64)]
            lending.append({"index": index, "family": fam,
                            "asset": address(log["topics"][1]),
                            "account": address(log["topics"][2]),
                            "amount_raw": str(words[1] if fam in ["AaveSupply", "AaveBorrow"] else words[0])})
    matched = [{"position": key, "liquidity_raw": str(value),
                "intervening_swap_same_pool": key[:2] in middle_pools}
               for key, value in deposits.items() if value > 0 and removals.get(key) == -value]
    raw_cash = sum(int(n[3]) for r in rr for n in r["net"] if n[0] == r["to"] and n[2] == "WETH")
    start_weth = -sum(D(n[3]) for n in rr[0]["net"] if n[0] == rr[0]["to"] and n[2] == "WETH") / D(10**18)
    mark = -D(rr[0]["tnet"]["WETH"]) / start_weth
    gas_limit_cost_eth = sum(D(r["gl"]) * D(r["eff"]) / D(10**18) for r in rr)
    episodes.append({"block": block_number, "block_hash": block["hash"],
                     "hashes": [rr[0]["h"], middle["hash"], rr[1]["h"]],
                     "indices": [rr[0]["i"], rr[0]["i"] + 1, rr[1]["i"]],
                     "primary_labels": [types[r["h"]] for r in rr],
                     "middle_selected": middle["hash"] in by_hash,
                     "middle_destination": middle["to"],
                     "start_weth": start_weth,
                     "outer_contract_weth_cash_change": D(raw_cash) / D(10**18),
                     "outer_contract_cash_usd_at_study_marks": sum(D(r["tnet"]["WETH"]) for r in rr),
                     "gas_limit_cost_usd_upper_bound": gas_limit_cost_eth * mark,
                     "matched_liquidity_positions": matched,
                     "aave_events": lending})

middle_hashes = {e["hashes"][1] for e in episodes}
all_actor_count = 0
all_actor_other = []
for row in load_rows(STUDY / "txs_all.jsonl.gz"):
    if row["from"] == ACTOR:
        all_actor_count += 1
        if row["h"] not in by_hash:
            all_actor_other.append({k: row.get(k) for k in ["h", "b", "i", "sel", "pc", "fam", "tnet"]})
    if row["h"] in middle_hashes:
        for episode in episodes:
            if episode["hashes"][1] == row["h"]:
                episode["middle_largest_change_usd"] = row["pc"]
                episode["middle_events"] = row["fam"]
                episode["middle_assets"] = row["assets"]
                break
evidence["actor_sequences"] = {
    "sender": ACTOR, "outer_contract": actor_rows[0]["to"],
    "all_window_sender_transactions": all_actor_count, "unselected_sender_transactions": all_actor_other,
    "selected_transactions": len(actor_rows), "primary_labels": Counter(types[r["h"]] for r in actor_rows),
    "sum_largest_changes_usd": total(actor_rows),
    "episodes": episodes,
    "summary": {
        "count": len(episodes), "middle_unselected": sum(not e["middle_selected"] for e in episodes),
        "matched_liquidity_episodes": sum(bool(e["matched_liquidity_positions"]) for e in episodes),
        "matched_liquidity_with_middle_swap": sum(any(p["intervening_swap_same_pool"] for p in e["matched_liquidity_positions"]) for e in episodes),
        "cash_weth": sum(e["outer_contract_weth_cash_change"] for e in episodes),
        "cash_usd": sum(e["outer_contract_cash_usd_at_study_marks"] for e in episodes),
        "median_episode_cash_usd": statistics.median(e["outer_contract_cash_usd_at_study_marks"] for e in episodes),
        "gas_limit_cost_usd_upper_bound": sum(e["gas_limit_cost_usd_upper_bound"] for e in episodes),
        "zero_priority_fee_transactions": sum(r["tip"] == 0 for r in actor_rows)}}
flash = [r for r in rows if D(r["flash_usd"]) > 0]
evidence["flash_screen"] = {"transactions": len(flash), "below_position_threshold": sum(D(r["pc"]) < 10000 for r in flash),
                            "zero_priority_fee": sum(r["tip"] == 0 for r in flash),
                            "with_unpriced_assets": sum(bool(r["unp"]) for r in flash),
                            "with_unknown_events": sum(bool(r["unk"]) for r in flash),
                            "with_weth_withdrawal": sum("WETHWithdrawal" in r["fam"] for r in flash)}
out = HERE / "evidence.json"
out.write_text(json.dumps(evidence, indent=2, default=str) + "\n")
print(json.dumps({"evidence": str(out), "actor_summary": evidence["actor_sequences"]["summary"],
                  "all_actor_transactions": all_actor_count, "flash_screen": evidence["flash_screen"]}, indent=2, default=str))
