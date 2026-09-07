#!/usr/bin/env python3
"""Interchain joins across one day's per-chain windows (2026-09-07).

Reads only artifacts already produced by the per-chain pipelines plus the saved
raw windows; makes no network calls in the default mode. Every number the
findings quote is emitted here so it can be re-derived.

  uv run python scripts/interchain.py --date 2026-09-07              # all sections
  uv run python scripts/interchain.py --date 2026-09-07 --only relay
  uv run python scripts/interchain.py --date 2026-09-07 --live       # + head reads (needs network)

Sections
  fees     L1 base fee burned vs the L2's fee take, and the three urgency regimes
  relay    the Relay depository/solver footprint on Ethereum, Robinhood Chain, Solana
  usdg     USDG mint/burn per chain and the desk wallet that connects them
  stocks   tokenized-stock on-chain price vs reference, per chain
  yield    the dollar-yield ladder joined across chains
"""
import argparse, collections, gzip, json, os, sys, time

ETH_WINDOWS = ("live_5h", "live_midday")
RH = "robinhood_10h"
SOL = "solana_live"

USDG_ETH = "0xe343167631d89b6ffc58b88d6b7fb0228795491d"
USDC_ETH = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
USDG_RH = "0x5fc5360d0400a0fd4f2af552add042d716f1d168"
DESK = "0xf70da97812cb96acdf810712aa562db8dfa3dbef"
RELAY_DEPOSITORY = "0x4cd00e387622c35bddb9b4c962c136462338bc31"
RELAY_ROUTER = "0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f"
RELAY_APPROVAL = "0xccc88a9d1b4ed6b0eaba998850414b24f1c315be"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
V3SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
V4SWAP = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
ZERO = "0x" + "0" * 40
# Relay's Solana depository program and its vault / payout treasury, from the
# 2026-09-07 Solana window; program id confirmed against Relay's published
# depository deployment.
SOL_RELAY = {
    "program": "99vQwtBwYtrqqD9YSXbdum3KBdxPAVxYTaQ3cfnJSrN2",
    "vault": "7uTT8Xi5RWXzy7h9XL244GRgEycDYDhLjr3ZyNdXi8pZ",
    "treasury": "F7p3dFrjRTbtRp8FRF6qHLomXbKRBzpvBLjtQcfcgmNe",
    "router_payer": "AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51",
}
ERC20 = {
    USDC_ETH: ("USDC", 6), "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", 6),
    USDG_ETH: ("USDG", 6), "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": ("WETH", 18),
    "0x6c3ea9036406852006290770bedfcaba0e23a0e8": ("PYUSD", 6),
    "0x6b175474e89094c44da98b954eedeac495271d0f": ("DAI", 18),
    "0x4c9edd5852cd905f086c759e8383e09bff1e68b3": ("USDe", 18),
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c5d9": ("WBTC", 8),
}


def root(date):
    return os.path.join("research", date)


def jload(path):
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as fh:
        return json.load(fh)


def eth_blocks(date, win):
    d = os.path.join(root(date), win, "raw", "blocks")
    for fn in sorted(os.listdir(d)):
        try:
            yield jload(os.path.join(d, fn))
        except Exception:
            continue


def eth_logs(date, win):
    d = os.path.join(root(date), win, "raw", "logs")
    for fn in sorted(os.listdir(d)):
        try:
            yield from jload(os.path.join(d, fn))
        except Exception:
            continue


def rh_records(date, step=1):
    d = os.path.join(root(date), RH, "data")
    files = sorted(os.listdir(d))
    for fn in files[::step]:
        with gzip.open(os.path.join(d, fn), "rt") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def s256(h):
    v = int(h, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def words(hexdata):
    h = hexdata[2:]
    return [h[i * 64:(i + 1) * 64] for i in range(len(h) // 64)]


# --------------------------------------------------------------------------- fees
def sec_fees(date, eth_usd):
    out = {"ethereum": {}, "robinhood": {}, "solana": {}}
    burned = gas = txs = blocks = 0
    tips_ub = 0.0
    for win in ETH_WINDOWS:
        for b in eth_blocks(date, win):
            bf, gu = int(b["baseFeePerGas"], 16), int(b["gasUsed"], 16)
            burned += bf * gu
            gas += gu
            blocks += 1
            for tx in b["transactions"]:
                txs += 1
                gp = int(tx.get("gasPrice", "0x0"), 16)
                mp = tx.get("maxPriorityFeePerGas")
                tip = min(int(mp, 16), max(0, gp - bf)) if mp is not None else max(0, gp - bf)
                tips_ub += tip * int(tx.get("gas", "0x0"), 16)
    out["ethereum"] = {
        "blocks": blocks, "txs": txs, "gas_used": gas,
        "base_fee_burned_eth": round(burned / 1e18, 4),
        "base_fee_burned_usd": round(burned / 1e18 * eth_usd, 0),
        "avg_price_gwei": round(burned / 1e18 / (gas / 1e9), 4) if gas else None,
        # gas *limit* x tip: a strict upper bound, receipts are not collected
        "priority_fee_upper_bound_eth": round(tips_ub / 1e18, 2),
    }
    rh = jload(os.path.join(root(date), RH, "analysis.json"))
    fu = jload(os.path.join(root(date), RH, "followups.json"))
    w = rh["window"]
    out["robinhood"] = {
        "blocks": w["blocks"], "txs_user": w["txs_user"], "gas_used": int(w["gas_total_G"] * 1e9),
        "fees_eth": w["fees_eth"], "fees_usd": w["fees_usd"],
        "avg_price_gwei": round(w["fees_eth"] / (w["gas_total_G"]), 4),
        "l1_settlement_eth": fu["l1_cost"]["totals"].get("total_eth") if isinstance(fu["l1_cost"].get("totals"), dict) else None,
        "priority_bids": rh["gas_bidding"]["txs_ge_3x_basefee"],
        "priority_bids_charged": rh["gas_bidding"]["bids_charged_above_basefee"],
        "priority_extra_paid_eth": rh["gas_bidding"]["extra_paid_eth"],
        "daily_fee_accrual_eth": {r["date"]: r.get("network_accrual") for r in []} or None,
    }
    s = jload(os.path.join(root(date), SOL, "analysis.json"))["network"]
    out["solana"] = {
        "nonvote_txs": s["nonvote"], "failed": s["failed"], "failed_share": round(s["failed_share"], 4),
        "fees_sol": s["fees_sol"], "base_fees_sol": s["base_fees_sol"],
        "priority_fees_sol": s["priority_fees_sol"], "failed_fees_sol": s["failed_fees_sol"],
        "jito_tips_sol": s["jito_tips_sol"],
    }
    if out["ethereum"]["base_fee_burned_eth"]:
        out["ratio_l2_fees_over_l1_burn"] = round(
            out["robinhood"]["fees_eth"] / out["ethereum"]["base_fee_burned_eth"], 1)
    return out


# --------------------------------------------------------------------------- relay
def sec_relay(date, eth_usd, sol_usd):
    out = {}
    eth = {"token_in": collections.Counter(), "token_out": collections.Counter(),
           "n_in": collections.Counter(), "n_out": collections.Counter(),
           "depositors": set(), "recipients": set(), "native_eth": 0.0,
           "native_txs": 0, "native_senders": set()}
    for win in ETH_WINDOWS:
        for b in eth_blocks(date, win):
            for tx in b["transactions"]:
                if (tx.get("to") or "").lower() == RELAY_DEPOSITORY:
                    v = int(tx.get("value", "0x0"), 16)
                    if v:
                        eth["native_eth"] += v / 1e18
                        eth["native_txs"] += 1
                        eth["native_senders"].add(tx["from"].lower())
        for lg in eth_logs(date, win):
            t = lg.get("topics") or []
            if not t or t[0] != TRANSFER or len(t) < 3:
                continue
            frm, to = "0x" + t[1][-40:], "0x" + t[2][-40:]
            if RELAY_DEPOSITORY not in (frm, to):
                continue
            meta = ERC20.get(lg["address"].lower())
            if not meta:
                continue
            sym, dec = meta
            try:
                amt = int(lg["data"], 16) / 10 ** dec
            except Exception:
                continue
            if to == RELAY_DEPOSITORY:
                eth["token_in"][sym] += amt
                eth["n_in"][sym] += 1
                eth["depositors"].add(frm)
            else:
                eth["token_out"][sym] += amt
                eth["n_out"][sym] += 1
                eth["recipients"].add(to)
    usd = sum(v for k, v in eth["token_in"].items() if k not in ("WETH", "WBTC"))
    usd += eth["token_in"].get("WETH", 0) * eth_usd + eth["native_eth"] * eth_usd
    out["ethereum"] = {
        "depository": RELAY_DEPOSITORY,
        "token_in": {k: round(v, 2) for k, v in eth["token_in"].most_common()},
        "token_out": {k: round(v, 2) for k, v in eth["token_out"].most_common()},
        "deposit_txs": sum(eth["n_in"].values()) + eth["native_txs"],
        "native_eth_in": round(eth["native_eth"], 2),
        "distinct_token_depositors": len(eth["depositors"]),
        "distinct_native_depositors": len(eth["native_senders"]),
        "distinct_payout_recipients": len(eth["recipients"]),
        "payout_recipients": sorted(eth["recipients"]),
        "user_deposits_usd": round(usd, 0),
    }
    rh = jload(os.path.join(root(date), RH, "analysis.json"))
    ff = rh["focus_flows"]
    solvers = [r["from"] for r in rh["top_from"]
               if any("Relay" in (t[1] or "") for t in r.get("targets", []))]
    dep = ff["RelayDepository"].get("USDG", {})
    out["robinhood"] = {
        "depository_usdg_in": round(dep.get("in", 0), 2),
        "depository_usdg_out": round(dep.get("out", 0), 2),
        "deposit_txs": dep.get("n_in"), "withdrawals": dep.get("n_out"),
        "depositors": dep.get("counterparties"),
        "solver_wallets": len(solvers), "solvers": solvers,
        "solver_fee_share_pct": next((r["fee_share_pct"] for r in rh["top_to_by_fees"]
                                      if r["to"] == RELAY_APPROVAL), None),
        "approval_proxy_txs": next((r["txs"] for r in rh["top_to"]
                                    if r["to"] == RELAY_APPROVAL), None),
    }
    s = jload(os.path.join(root(date), SOL, "analysis.json"))
    out["solana"] = dict(SOL_RELAY)
    out["solana"]["note"] = ("today's Solana narrative describes this as an unlabelled custodial "
                             "deposit system; it is Relay's Solana depository")
    out["solana"]["window_hours"] = s["window"]["hours"]
    return out


# --------------------------------------------------------------------------- usdg
def sec_usdg(date, rh_step=1):
    out = {}
    for win in ETH_WINDOWS:
        mint = burn = 0.0
        mint_to = collections.Counter()
        burn_from = collections.Counter()
        desk_in = collections.Counter()
        desk_out = collections.Counter()
        for lg in eth_logs(date, win):
            t = lg.get("topics") or []
            if not t or t[0] != TRANSFER or len(t) < 3 or lg["address"].lower() != USDG_ETH:
                continue
            frm, to = "0x" + t[1][-40:], "0x" + t[2][-40:]
            try:
                amt = int(lg["data"], 16) / 1e6
            except Exception:
                continue
            if frm == ZERO:
                mint += amt
                mint_to[to] += amt
            if to == ZERO:
                burn += amt
                burn_from[frm] += amt
            if to == DESK:
                desk_in[frm] += amt
            if frm == DESK:
                desk_out[to] += amt
        out.setdefault("ethereum", {})[win] = {
            "mint": round(mint, 2), "burn": round(burn, 2), "net": round(mint - burn, 2),
            "mint_to": [(k, round(v, 2)) for k, v in mint_to.most_common(5)],
            "burn_from": [(k, round(v, 2)) for k, v in burn_from.most_common(5)],
            "desk_in": [(k, round(v, 2)) for k, v in desk_in.most_common(5)],
            "desk_out": [(k, round(v, 2)) for k, v in desk_out.most_common(5)],
            "desk_net": round(sum(desk_in.values()) - sum(desk_out.values()), 2),
        }
    mint = burn = 0.0
    mint_to = collections.Counter()
    burn_from = collections.Counter()
    desk_in = collections.Counter()
    desk_out = collections.Counter()
    for r in rh_records(date, rh_step):
        if r.get("t") != "l" or r.get("a") != USDG_RH:
            continue
        tp = r.get("tp") or []
        if not tp or tp[0] != TRANSFER or len(tp) < 3:
            continue
        frm, to = "0x" + tp[1][-40:], "0x" + tp[2][-40:]
        try:
            amt = int(r["d"], 16) / 1e6
        except Exception:
            continue
        if frm == ZERO:
            mint += amt
            mint_to[to] += amt
        if to == ZERO:
            burn += amt
            burn_from[frm] += amt
        if to == DESK:
            desk_in[frm] += amt
        if frm == DESK:
            desk_out[to] += amt
    out["robinhood"] = {
        "sample_step": rh_step,
        "mint": round(mint, 2), "burn": round(burn, 2), "net": round(mint - burn, 2),
        "mint_to": [(k, round(v, 2)) for k, v in mint_to.most_common(5)],
        "burn_from": [(k, round(v, 2)) for k, v in burn_from.most_common(5)],
        "desk_in": [(k, round(v, 2)) for k, v in desk_in.most_common(5)],
        "desk_out": [(k, round(v, 2)) for k, v in desk_out.most_common(5)],
        "desk_net": round(sum(desk_in.values()) - sum(desk_out.values()), 2),
    }
    s = jload(os.path.join(root(date), SOL, "analysis.json"))["issuance"]["by_mint"].get("USDG", {})
    out["solana"] = {"mint": s.get("mint"), "burn": s.get("burn"), "net": s.get("net")}
    return out


# --------------------------------------------------------------------------- stocks
def sec_stocks(date, step=18):
    """Re-derive every stock's on-chain price from its USDG pools, over the window.

    The per-chain scan records one first/last price per token merged with
    setdefault across passes, so a stale pass-1 price is never corrected. This
    reads every stock/USDG pool independently.
    """
    pools = jload(os.path.join(root(date), RH, "pools.json"))
    stocks = {e["address_hash"].lower(): (e.get("symbol"), float(e.get("exchange_rate") or 0) or None)
              for e in jload(os.path.join(root(date), RH, "stock_tokens.json"))}
    tgt = {}
    for k, v in pools.items():
        t0, t1 = (v.get("token0") or "").lower(), (v.get("token1") or "").lower()
        if t0 == USDG_RH and t1 in stocks:
            tgt[k.lower()] = (t1, False)
        elif t1 == USDG_RH and t0 in stocks:
            tgt[k.lower()] = (t0, True)
    agg = collections.defaultdict(lambda: collections.defaultdict(
        lambda: {"n": 0, "first": None, "last": None, "min": None, "max": None}))
    for r in rh_records(date, step):
        if r.get("t") != "l":
            continue
        tp = r.get("tp") or []
        if not tp:
            continue
        if tp[0] == V3SWAP:
            key = r.get("a", "").lower()
        elif tp[0] == V4SWAP and len(tp) >= 2:
            key = ("0x" + tp[1][2:]).lower()
        else:
            continue
        if key not in tgt:
            continue
        w = words(r["d"])
        if len(w) < 5:
            continue
        sq = int(w[2], 16)
        if not sq:
            continue
        tok, t0_is_stock = tgt[key]
        ratio = (sq / 2 ** 96) ** 2
        px = ratio * 1e12 if t0_is_stock else 1 / (ratio * 1e-12)
        a = agg[tok][key[:12]]
        a["n"] += 1
        a["first"] = a["first"] if a["first"] is not None else px
        a["last"] = px
        a["min"] = px if a["min"] is None else min(a["min"], px)
        a["max"] = px if a["max"] is None else max(a["max"], px)
    rows = []
    for tok, byp in agg.items():
        sym, ref = stocks[tok]
        n = sum(v["n"] for v in byp.values())
        deep = max(byp.items(), key=lambda kv: kv[1]["n"])
        lo = min(v["min"] for v in byp.values())
        hi = max(v["max"] for v in byp.values())
        rows.append({"symbol": sym, "reference": ref, "pools": len(byp), "swaps_sampled": n,
                     "deepest_pool": deep[0], "px_last_deepest": round(deep[1]["last"], 4),
                     "px_min": round(lo, 4), "px_max": round(hi, 4),
                     "dev_pct": round((deep[1]["last"] / ref - 1) * 100, 3) if ref else None})
    rows.sort(key=lambda r: -(abs(r["dev_pct"]) if r["dev_pct"] is not None else 0))
    return {"sample_step": step, "stock_usdg_pools": len(tgt), "rows": rows}


# --------------------------------------------------------------------------- yield
def sec_yield(date):
    out = {"rows": []}
    for win in ETH_WINDOWS:
        h = jload(os.path.join(root(date), win, "head_state.json"))
        for name, r in h["compound"].items():
            out["rows"].append({"chain": "ethereum", "at": h["utc"], "venue": name.replace("Compound v3 ", "Compound v3 "),
                                "asset": name.split()[-1], "supply_apr": round(r["supply_apr"] * 100, 2),
                                "borrow_apr": round(r["borrow_apr"] * 100, 2),
                                "util": round(r["utilisation"] * 100, 1), "size_usd": round(r["supplied"], 0)})
        for proto, res in h["lending"].items():
            for addr, r in res.items():
                if not isinstance(r, dict) or not r.get("supplied_usd"):
                    continue
                sym = r.get("sym")
                if sym not in ("USDC", "USDT", "USDS", "DAI", "PYUSD", "USDe", "GHO", "RLUSD"):
                    continue
                out["rows"].append({"chain": "ethereum", "at": h["utc"], "venue": proto, "asset": sym,
                                    "supply_apr": round(r["supply_apr"] * 100, 2),
                                    "borrow_apr": round(r["borrow_apr"] * 100, 2),
                                    "util": round((r.get("utilisation") or 0) * 100, 1),
                                    "size_usd": round(r["supplied_usd"], 0)})
        out["rows"].append({"chain": "ethereum", "at": h["utc"], "venue": "Sky SSR", "asset": "USDS",
                            "supply_apr": round(h["sky"]["ssr_apy"] * 100, 2), "borrow_apr": None,
                            "util": None, "size_usd": None})
    sh = jload(os.path.join(root(date), SOL, "head_state.json"))
    for e in sh["jupiter_lend"]:
        out["rows"].append({"chain": "solana", "at": sh["retrieved_utc"], "venue": "Jupiter Lend",
                            "asset": e["asset_symbol"], "supply_apr": round(e["total_rate_bps"] / 100, 2),
                            "borrow_apr": None, "util": None,
                            "size_usd": round(e["total_assets"] * e["asset_price"], 0)})
    for m in sh["kamino_markets"]:
        for r in m["reserves"]:
            if r["token"] in ("USDC", "USDT", "PYUSD", "USDG", "USDS", "USDe") and r["supplied_usd"] > 5e6:
                out["rows"].append({"chain": "solana", "at": sh["retrieved_utc"],
                                    "venue": "Kamino " + m["name"], "asset": r["token"],
                                    "supply_apr": round(r["supply_apy"] * 100, 2),
                                    "borrow_apr": round(r["borrow_apy"] * 100, 2),
                                    "util": round(r["util"] * 100, 1), "size_usd": round(r["supplied_usd"], 0)})
    for r in sh["save_main"]:
        if r.get("symbol") in ("USDC", "USDT") and r["supplied_usd"] > 5e6:
            out["rows"].append({"chain": "solana", "at": sh["retrieved_utc"], "venue": "Save main",
                                "asset": r["symbol"], "supply_apr": round(r["supply_apy"] * 100, 2),
                                "borrow_apr": round(r["borrow_apy"] * 100, 2),
                                "util": round(r["util"] * 100, 1), "size_usd": round(r["supplied_usd"], 0)})
    out["robinhood_gap"] = ("no rate read exists for Robinhood Chain; steakUSDG / spUSDG / ethenaUSDG "
                            "and Morpho Blue there are measured by flow only")
    out["rows"].sort(key=lambda r: -(r["supply_apr"] or 0))
    return out



# --------------------------------------------------------------------------- selfmatch
RH_TOP_POOLS = {"0x52e65b17fb6e5ba00ed806f37afcd2daa50271ca": "WETH/USDG v3 1bp",
                "0xd4eb21209c4d6093f80b5b84f5c45cc093ea14a3": "USDG/NVDA v3 5bp"}


def sec_selfmatch(date, step=24):
    """Port of the Solana wash test to Robinhood Chain, in the form the data allows.

    Solana's detector is intra-transaction (a second signer whose legs mirror the
    trader's). Orbit logs carry the calling contract, not the EOA, so this is the
    weaker same-block / same-caller / opposite-direction version: it bounds how
    much of a pool's volume is self-offsetting inside one block.
    """
    out = {"sample_step": step, "pools": []}
    pools = jload(os.path.join(root(date), RH, "pools.json"))
    # token0 decimals per pool: USDG is 6, WETH and the stock tokens are 18
    dec0 = {}
    for a in RH_TOP_POOLS:
        t0 = (pools.get(a, {}).get("token0") or "").lower()
        dec0[a] = 6 if t0 == USDG_RH else 18
    agg = collections.defaultdict(lambda: {"n": 0, "vol0": 0.0,
                                           "senders": collections.Counter(),
                                           "recipients": collections.Counter(),
                                           "byblock": collections.defaultdict(list)})
    for r in rh_records(date, step):
        if r.get("t") != "l":
            continue
        a = r.get("a", "").lower()
        if a not in RH_TOP_POOLS:
            continue
        tp = r.get("tp") or []
        if not tp or tp[0] != V3SWAP or len(tp) < 3:
            continue
        w = words(r["d"])
        if len(w) < 5:
            continue
        a0 = s256(w[0])
        snd, rcp = "0x" + tp[1][-40:], "0x" + tp[2][-40:]
        g = agg[a]
        g["n"] += 1
        g["vol0"] += abs(a0) / 10 ** dec0[a]
        g["senders"][snd] += 1
        g["recipients"][rcp] += 1
        g["byblock"][(r["n"], snd)].append(a0)
    for a, g in agg.items():
        opp = one = 0
        oppvol = 0.0
        for amts in g["byblock"].values():
            if len(amts) < 2:
                continue
            pos = [x for x in amts if x > 0]
            neg = [x for x in amts if x < 0]
            if pos and neg:
                opp += 1
                oppvol += min(sum(pos), -sum(neg)) / 10 ** dec0[a]
            else:
                one += 1
        out["pools"].append({
            "pool": a, "name": RH_TOP_POOLS[a], "swaps_sampled": g["n"],
            "distinct_calling_contracts": len(g["senders"]),
            "distinct_recipients": len(g["recipients"]),
            "top_callers": [(k[:10], v, round(100 * v / g["n"], 1)) for k, v in g["senders"].most_common(5)],
            "same_block_same_caller_opposite": opp, "same_block_same_caller_one_way": one,
            "token0_decimals": dec0[a],
            "offsetting_token0": round(oppvol, 3), "token0_volume": round(g["vol0"], 3),
            "self_match_share_pct": round(100 * oppvol / g["vol0"], 3) if g["vol0"] else None})
    s = jload(os.path.join(root(date), SOL, "analysis.json"))["dex"]
    out["solana_reference"] = {"priced_usd": s["total_priced_usd"],
                               "self_matched_usd": s["self_matched"]["total_usd"],
                               "self_matched_share_pct": round(100 * s["self_matched"]["total_usd"] / s["total_priced_usd"], 1)}
    return out


# --------------------------------------------------------------------------- live
RH_RPCS = ["https://rpc.mainnet.chain.robinhood.com", "https://robinhood.blockmachine.io",
           "https://robinhood-rpc.publicnode.com"]
RH_VAULTS = {"steakUSDG": "0xbeeff033f34c046626b8d0a041844c5d1a5409dd",
             "ethenaUSDG": "0xbeeff0fb1dc19344a87b8479dab60a2e16160737",
             "spUSDG": "0xde770c84fe66e063336b31737cfe9790f18c4087"}


def sec_live_rh_vaults(gap_s=420):
    """Robinhood Chain has no rate read in any per-chain artifact. Public RPCs
    there serve no archive state, so realise the rate forward instead: sample
    convertToAssets(1e24) twice and annualise. 1e24 shares keeps ~6 significant
    figures of share-price change over a few minutes."""
    import urllib.request
    ua = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
          "Content-Type": "application/json"}

    def rpc(method, params):
        p = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        for u in RH_RPCS:
            try:
                r = json.load(urllib.request.urlopen(
                    urllib.request.Request(u, json.dumps(p).encode(), ua), timeout=25))
                if r.get("result") not in (None, "0x"):
                    return r["result"]
            except Exception:
                pass
            time.sleep(0.25)
        return None

    def snap():
        blk = rpc("eth_blockNumber", [])
        b = rpc("eth_getBlockByNumber", [blk, False])
        s = {"block": int(blk, 16), "ts": int(b["timestamp"], 16), "v": {}}
        for k, a in RH_VAULTS.items():
            c = rpc("eth_call", [{"to": a, "data": "0x07a2d13a" + hex(10 ** 24)[2:].rjust(64, "0")}, "latest"])
            t = rpc("eth_call", [{"to": a, "data": "0x01e1d114"}, "latest"])
            s["v"][k] = {"conv1e24": int(c, 16) if c else None,
                         "totalAssets_usd": int(t, 16) / 1e6 if t else None}
        return s

    a = snap()
    time.sleep(gap_s)
    b = snap()
    dt = b["ts"] - a["ts"]
    rows = []
    for k in RH_VAULTS:
        x, y = a["v"][k]["conv1e24"], b["v"][k]["conv1e24"]
        if x and y and dt > 0:
            g = y / x - 1
            rows.append({"vault": k, "address": RH_VAULTS[k],
                         "total_assets_usd": b["v"][k]["totalAssets_usd"],
                         "window_s": dt, "growth": g,
                         "apr_pct": round(g * 31536000 / dt * 100, 3),
                         "apy_pct": round(((1 + g) ** (31536000 / dt) - 1) * 100, 3)})
    return {"chain": "robinhood", "method": "forward-realised share price, two samples",
            "sample_a": a, "sample_b": b, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-07")
    ap.add_argument("--out", default=None)
    ap.add_argument("--only", default=None, help="fees,relay,usdg,stocks,yield,selfmatch,live")
    ap.add_argument("--live-gap", type=int, default=420, help="seconds between the two Robinhood vault samples")
    ap.add_argument("--eth-usd", type=float, default=2490.0)
    ap.add_argument("--sol-usd", type=float, default=105.08)
    ap.add_argument("--rh-step", type=int, default=1, help="sample every Nth Robinhood chunk")
    ap.add_argument("--stock-step", type=int, default=18)
    a = ap.parse_args()
    out = a.out or os.path.join(root(a.date), "interchain")
    os.makedirs(out, exist_ok=True)
    want = set((a.only or "fees,relay,usdg,stocks,yield,selfmatch").split(","))
    res = {"date": a.date, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "price_basis": {"eth_usd": a.eth_usd, "sol_usd": a.sol_usd}}
    if "fees" in want:
        res["fees"] = sec_fees(a.date, a.eth_usd)
    if "relay" in want:
        res["relay"] = sec_relay(a.date, a.eth_usd, a.sol_usd)
    if "usdg" in want:
        res["usdg"] = sec_usdg(a.date, a.rh_step)
    if "stocks" in want:
        res["stocks"] = sec_stocks(a.date, a.stock_step)
    if "yield" in want:
        res["yield"] = sec_yield(a.date)
    if "selfmatch" in want:
        res["selfmatch"] = sec_selfmatch(a.date)
    if "live" in want:
        res["live_robinhood_vaults"] = sec_live_rh_vaults(a.live_gap)
    path = os.path.join(out, "interchain.json")
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1)
    print("wrote", path)
    for k in ("fees", "relay", "usdg"):
        if k in res:
            print("--", k, json.dumps(res[k])[:400])


if __name__ == "__main__":
    main()
