"""Render compact episode tables from audited calculations; offline."""
from decimal import Decimal as D
from collect import HERE, read


def main():
    ledger = read(HERE / "ledger.json")["episodes"]
    impacts = {r["block"]: r for r in read(HERE / "audit.json")["output_impacts"]}
    positions = {r["block"]: r["venue"] for r in read(HERE / "positions.json")}
    lines = ["All 20 episodes are included below. Dollar values use the frozen study's hourly endpoint marks and are rounded for display; exact wei accounting is in [ledger.json](ledger.json). These are retained on-chain episode proceeds, before operating costs, failed attempts, later payments or rebates.\n",
        "| Block | Brief LP venue | Gross USD | Direct payment USD | Gas USD | Retained USD | Output improvement without opening, bps |",
        "|---|---|---:|---:|---:|---:|---:|"]
    for r in ledger:
        vals = [f'{D(r[k]):.2f}' for k in ["gross_usd_study_mark", "coinbase_usd_study_mark", "gas_usd_study_mark", "retained_usd_study_mark"]]
        lines.append(f'| [{r["block"]}](https://etherscan.io/block/{r["block"]}) | {positions.get(r["block"], "No matched position")} | ' + " | ".join(vals) + f' | {D(impacts[r["block"]]["improvement_bps_of_actual_output"]):.2f} |')
    totals = [f'{sum(D(r[k]) for r in ledger):.2f}' for k in ["gross_usd_study_mark", "coinbase_usd_study_mark", "gas_usd_study_mark", "retained_usd_study_mark"]]
    lines.append('| **Total** | **17 matched positions** | ' + ' | '.join(totals) + ' | — |')
    lines += ["\nOutput improvement is `(without-opening output − actual output) / actual output × 10,000`, at the explicitly identified recipient in [audit.json](audit.json). These include some settlement/route contracts. Different output assets are not summed together. Gas effects on the middle transaction are saved separately.\n",
        "| Block | Opening transaction | Middle order | Closing transaction |", "|---|---|---|---|"]
    for r in ledger:
        lines.append(f'| {r["block"]} | ' + ' | '.join(f'[{h[:12]}…](https://etherscan.io/tx/{h})' for h in r['hashes']) + ' |')
    (HERE / "episodes.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
