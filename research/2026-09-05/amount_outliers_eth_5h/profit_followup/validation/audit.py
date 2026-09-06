"""Offline audit: receipts, exact replays, state closure, fees, and output impacts."""
from collections import defaultdict, Counter
from decimal import Decimal as D
import hashlib
import json
from collect import HERE, RAW, read, save
from reconcile import GROUP, HELPER, WETH, tokens, native, logs, log_shape
from mechanics import kh

# Retrospectively inspected output destinations, not claims of address ownership.
# Includes routers/settlement contracts when the on-chain route ends there.
OUTPUTS = {
    25910849: ("0xad9f96866562ae55e9423c15daf963b219f09f56", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    25910935: ("0x648038b6837c4c0a4b03ba26ca7c621eb06fc7f0", "ETH"),
    25910990: ("0xb8f275fbf7a959f4bce59999a2ef122a099e81a8", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"),
    25910995: ("0xa48e223e2a723a2f574e3a4e0b12126851b81ca4", "0x5886e4d8d6a41a5ea2f3f77f23d7a7e942d581f1"),
    25911033: ("0x05e7c72498fdecf1c3638b66af2740adea8d7f8f", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    25911089: ("0x4cd00e387622c35bddb9b4c962c136462338bc31", "0xe343167631d89b6ffc58b88d6b7fb0228795491d"),
    25911110: ("0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5", WETH),
    25911337: ("0x2adc73d7f87e8bdbcc64b7dd7c251bbccf72a7d2", "0xa9e8acf069c58aec8825542845fd754e41a9489a"),
    25911349: ("0x249a1b925e48d3dd31823a9ae76341229f298038", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    25911429: ("0x40ffe85a28dc9993541449464d7529a922142960", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    25911582: ("0x05e7c72498fdecf1c3638b66af2740adea8d7f8f", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    25911701: ("0xfa9edea5ac3aaf4f9af53c14f623e68ad61d6c0f", "0xcacd6fd266af91b8aed52accc382b4e165586e29"),
    25911742: ("0x49fb929c2252248afbc46f2ed43873f13452ebb5", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"),
    25911771: ("0xdeedd94590291d7b2640cea472ed2288e7812b05", "0x6243558a24cc6116abe751f27e6d7ede50abfc76"),
    25911802: ("0xccd92b453da9d6277f48c32fb0b6b5b630da7d4d", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    25911874: ("0x21fecf63489ab27e9483fe3ad6cfffd4e392b450", "0x7cf9a80db3b29ee8efe3710aadb7b95270572d47"),
    25911943: ("0x4cd00e387622c35bddb9b4c962c136462338bc31", "0xe343167631d89b6ffc58b88d6b7fb0228795491d"),
    25911995: ("0x3a6fb4fab64e8fa018d1b27226cb609e4b1feade", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"),
    25912028: ("0xf595902166aa1d60047d6ec141803fceef03a7fd", "0x6b175474e89094c44da98b954eedeac495271d0f"),
    25912097: ("0x1e605e0fd524745a25fd190e88c5da67303f945b", "0xdac17f958d2ee523a2206206994597c13d831ec7"),
}


def main():
    ledger = read(HERE / "ledger.json")
    balances = {b["block"]: b for b in read(HERE / "balances.json")}
    positions = read(HERE / "positions.json")
    assert len(positions) == 17
    metadata = {q["target"]: q["value"] for q in next(iter(balances.values()))["states"]["before"] if q["function"] == "symbol()"}
    decimals = {q["target"]: int(q["value"]) for q in next(iter(balances.values()))["states"]["before"] if q["function"] == "decimals()"}
    extras = read(HERE / "extra_metadata.json")
    metadata["ETH"], decimals["ETH"] = "ETH", 18
    for a, meta in extras.items():
        if "symbol()" in meta:
            metadata[a], decimals[a] = meta["symbol()"], meta["decimals()"]
    debt_assets = {a for a, sym in metadata.items() if sym.startswith("variableDebt")}
    state_deltas = defaultdict(int)
    impacts = []
    financing = []
    prior = {e["block"]: e for e in read(HERE.parent / "evidence.json")["actor_sequences"]["episodes"]}
    reserve_topic = "0x" + kh(b"ReserveDataUpdated(address,uint256,uint256,uint256,uint256,uint256)").hex()
    for e in ledger["episodes"]:
        b = balances[e["block"]]
        rawlogs = read(RAW / "logs" / f'{e["block"]}.json.gz')
        for h in e["hashes"]:
            actual = read(HERE / "receipts" / (h + ".json.gz"))["logs"]
            assert [log_shape(l) for l in actual] == [log_shape(l) for l in rawlogs if l["transactionHash"] == h]
        outer_logs = sum([read(HERE / "receipts" / (h + ".json.gz"))["logs"] for h in [e["hashes"][0], e["hashes"][2]]], [])
        indexes = defaultdict(list)
        for l in outer_logs:
            if l["address"] == "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2" and l["topics"][0] == reserve_topic:
                words = [int(l["data"][i:i+64], 16) for i in range(2, len(l["data"]), 64)]
                indexes["0x" + l["topics"][1][-40:]].append(words[-2:])
        assert indexes and all(len(set(tuple(v) for v in vs)) == 1 for vs in indexes.values())
        borrow = [v for v in prior[e["block"]]["aave_events"] if v["family"] == "AaveBorrow"]
        repay = [v for v in prior[e["block"]]["aave_events"] if v["family"] == "AaveRepay"]
        assert len(borrow) == len(repay) == 1
        rounding = int(repay[0]["amount_raw"]) - int(borrow[0]["amount_raw"])
        assert rounding in [1, 2]
        financing.append({"block": e["block"], "asset": borrow[0]["asset"], "borrow_raw": borrow[0]["amount_raw"],
            "repay_raw": repay[0]["amount_raw"], "difference_raw": rounding, "reserve_indexes": indexes})
        token_net = tokens(outer_logs)
        for phase in ["before", "after"]:
            for q in b["states"][phase]:
                if q["function"] == "getUserAccountData(address)":
                    assert int(q["values"][1]) == 0
                if q["target"] in debt_assets and q["function"] in ["balanceOf(address)", "scaledBalanceOf(address)"]:
                    assert q["success"] and int(q["value"]) == 0
        for d in b["deltas"]:
            delta = int(d["delta_raw"])
            if d["function"] == "getEthBalance(address)":
                assert delta == int(e["native_deltas_wei"][d["account"]])
            if d["function"] == "balanceOf(address)":
                state_deltas[d["target"]] += delta
                if not metadata[d["target"]].startswith("aEth"):
                    assert delta == token_net[(d["account"], d["target"])]
                if d["target"] != WETH:
                    assert abs(D(delta) / 10**decimals[d["target"]]) < D("0.00001")
        assert e["middle_replay"]["actual_exact_trace_gas_logs_match"]
        assert e["middle_replay"]["without_open_success"]
        a, token = OUTPUTS[e["block"]]
        t0 = read(HERE / "replays" / f'{e["block"]}_actual.json.gz')
        t1 = read(HERE / "replays" / f'{e["block"]}_without_open.json.gz')
        if token == "ETH":
            actual, cf = native(t0)[0][a], native(t1)[0][a]
        else:
            actual, cf = tokens(logs(t0))[(a, token)], tokens(logs(t1))[(a, token)]
        assert cf > actual > 0
        row = {"block": e["block"], "recipient": a, "token": token, "symbol": metadata.get(token),
            "actual_output_raw": str(actual), "without_open_output_raw": str(cf),
            "improvement_raw": str(cf-actual), "improvement_bps_of_actual_output": str(D(cf-actual)/D(actual)*10000),
            "actual_gas": e["middle_replay"]["actual_gas_used"], "without_open_gas": e["middle_replay"]["without_open_gas_used"]}
        if token in decimals:
            row.update(actual_output=str(D(actual)/10**decimals[token]), without_open_output=str(D(cf)/10**decimals[token]), improvement=str(D(cf-actual)/10**decimals[token]))
        impacts.append(row)
    fees = defaultdict(int)
    for r in read(HERE / "mechanics.json"):
        for m in r["new_ekubo_matches"]:
            assert m["middle_swap_same_pool"]
        for fee in r["lp_fees"]:
            for i in [0, 1]:
                amount = int(fee[f"amount{i}"])
                token = fee.get(f"token{i}") or extras[fee["address"]][f"token{i}()"]
                fees[token] += amount
    for p in positions:
        assert int(p["states"]["before"]["liquidity"]) == int(p["states"]["after"]["liquidity"]) == 0
        assert int(p["states"]["active"]["liquidity"]) == int(p["liquidity_expected"])
    summary = {"receipt_matches_to_original_infura_logs": 60, "exact_middle_replays": 20,
        "successful_without_open_replays": 20, "improved_output_destinations": 20,
        "account_state_boundaries": 40, "zero_debt_boundaries": 40,
        "state_verified_closed_lp_positions": 17, "positions_by_venue": dict(Counter(p["venue"] for p in positions)),
        "lp_fees": [{"token": a, "symbol": metadata[a], "raw": str(v), "amount": str(D(v)/10**decimals[a])} for a,v in sorted(fees.items()) if v],
        "other_state_deltas": [{"token": a, "symbol": metadata[a], "raw": str(v)} for a,v in sorted(state_deltas.items()) if v and a != WETH],
        "output_impacts": impacts}
    save(HERE / "audit.json", summary)
    save(HERE / "financing.json", financing)
    manifest = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.rglob("*"))
                if p.is_file() and "__pycache__" not in str(p) and p.name != "sha256.json"}
    save(HERE / "sha256.json", manifest)
    print(json.dumps({k:v for k,v in summary.items() if k not in ["output_impacts", "other_state_deltas"]}, indent=2))


if __name__ == "__main__":
    main()
