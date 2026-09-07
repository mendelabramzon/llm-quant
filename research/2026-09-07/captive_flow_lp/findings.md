# Renting liquidity to a subsidized dollar

Ethereum mainnet, finalized block **25,920,655**, 6 September 2026 20:19 UTC. Block-pinned research
snapshot, not a live quote. Working position sizes are $10k–$500k because the edge is a small-capital,
capacity-limited one; the point is the *shape* of the return, not a promised number.

## The one-line thesis

A stablecoin whose issuer **rebates its reserve yield to ecosystem partners** manufactures durable DEX
conversion volume, because partners are *paid to transact it*. That volume routes to whichever venue is
cheapest per clip. Today that is two **ultra-low-fee Uniswap v4 pools** that are **thin because they are
new**. Thin liquidity + high, subsidized, stable-versus-stable (non-toxic) turnover is a fee yield far
above ordinary stablecoin LPing — capturable by a small, early, *active* concentrated LP, and by nobody
who needs size. It is not an arbitrage, not a reward you must be whitelisted for, and not an
ordering race. It is being the marginal liquidity to a captive taker, in the venue the taker underpays.

The subsidized dollar here is **USDG (Global Dollar / Paxos)**. The [Global Dollar
Network](https://globaldollar.com/network) returns **over 90% of USDG reserve yield to partners** —
exchanges, wallets, and *DeFi liquidity providers*. USDG pays a plain holder nothing directly, which is
exactly why a partner desk will pay a small premium and eat pool fees to keep converting into it: the
>4% reserve rebate dwarfs a few basis points of friction. Its DEX demand is inelastic and recurring.

## What the chain shows

Read on-chain at the pinned block, and replayed from 24h of saved logs
([`captive_flow.json`](captive_flow.json), [`tables.md`](tables.md), built by
[`scripts/captive_flow_lp.py`](../../../scripts/captive_flow_lp.py)):

| Venue | LP fee | Deployed TVL | 24h volume | Turnover | Fees/day | Marginal-LP APR (+$50k) |
|---|--:|--:|--:|--:|--:|--:|
| USDC/USDG v4 (0x7da1afe9…) | 0.75 bp | $964,545 | $5,849,096 | 6.1x/day | $439 | **15.8%** |
| USDC/USDG v4 (0xb90d1190…) | 0.65 bp | $1,042,852 | $6,386,810 | 6.1x/day | $415 | **13.9%** |
| USDC/USDG Curve (0xc061caa0…) | 1.00 bp | $20,028,824 | $20,799,839 | 1.0x/day | $2,080 | 3.8% |

The same flow reaches a deep $20M Curve pool and two ~$1M v4 pools. The Curve pool, 20x larger, pays its
LPs **3.8%**. The thin v4 pools pay a *marginal* concentrated LP **14–16%** for the same stable-pair
risk. The gap is pure underprovisioning: the v4 pools win the small clips on their sub-basis-point fee,
but almost nobody has shown up to provide their liquidity yet.

> **Follow-up (added by the [interchain study](../interchain/findings.md), same day).** The desk
> `0xf70da978…` is **Relay's USDG solver**, not a Global Dollar Network partner farming the reserve rebate: it
> takes 100% of the RelayDepository's payouts on both Ethereum and Robinhood Chain and is a Paxos
> mint-and-redeem counterparty on both. The taker analysis below stands — a $1↔$1 conversion still carries no
> price information — but two things change. The "flow durability" risk below prices a *future* reroute to
> direct mint/redeem; the desk is already doing that in parallel, at larger size than its pool activity, so the
> pool is its marginal top-up venue. And its USDG book is close to flat over the window (+$58k on Robinhood
> Chain, +$482k on Ethereum against tens of millions of turnover), so pool volume tracks gross cross-chain
> settlement churn. Monitor Relay depository throughput, not USDG issuance or a rebate programme.

**The flow is captive and non-toxic.** In the busier v4 pool one address,
[`0xf70da978…`](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) — the USDG
desk identified in the day study — is **62% of volume and is not an LP**. It routes USDC→USDG through a
dedicated router and pays the fee to the 24 addresses that do provide liquidity. There is no price
information in a $1↔$1 conversion, so this is not the adverse-selection ("LVR") flow that makes ETH/USDC
LPing a loser; it is a desk rebalancing inventory it is paid to hold.

## Capacity — the honest part

The APR is high *because* TVL is thin, so it dilutes as you add. That is the whole ballgame:

| Add size | v4 0.75bp APR | v4 0.65bp APR | $/day on that add |
|--:|--:|--:|--:|
| +$10k | 16.4% | 14.4% | ~$4.1 |
| +$50k | 15.8% | 13.9% | ~$20 |
| +$100k | 15.0% | 13.3% | ~$38 |
| +$500k | 10.9% | 9.8% | ~$140 |

Two people each adding $100k already halve the excess. Real capacity to earn **>15%** is a few hundred
thousand dollars total across both pools; beyond ~$1M you converge toward the Curve pool's 3.8%. This is
an *early-venue* edge that decays as LP capital arrives or as USDG migrates more volume to its own
mint/redeem rail. It is a real return on real capital held over time, not a one-transaction profit.

The APR in the table above is the *average-concentration* figure. As the fork shows, a passive wide band
earns less (~6%) and a tightly-managed one more (~30%+) for the same dollars; the table is the honest
midpoint an unsophisticated LP would see. For scale against this repo's prior best small-capital finding:
the Aave→Compound USDC allocator earned about **$3/day on $100k**. This earns roughly **$18/day passive
to $38+/day managed on $100k** — several times the yield per dollar, at comparable (stablecoin) risk but
with the extra work and risks below.

## Proof it can actually be done, and the concentration law

[`fork/test/CaptiveFlowLP.t.sol`](fork/test/CaptiveFlowLP.t.sol) forks mainnet at 25,920,655 and, against
the **real** Uniswap v4 PoolManager and the real USDC/USDG pool, mints a small position at the peg,
replays one day of the observed volume ($5.85M) as alternating conversion clips, then withdraws and
measures fees / capital, annualized. Running the same liquidity `L` at two band widths
([`fork_proof.txt`](fork_proof.txt)):

| Band | Capital deployed | Fees earned in one day | Annualized |
|---|--:|--:|--:|
| ±2 ticks (±0.02%) | $19,998 | $17.68 | **32.3%** |
| ±10 ticks (±0.10%) | $99,970 | $17.61 | **6.4%** |

The two positions earn **the same fees** because a v4 position's fee share depends on its liquidity `L`,
not its dollars; the tight band just ties up ~1/5 the capital, so ~5x the APR. That is the whole knob:
**fees ∝ L, capital ∝ L × band width, so APR ∝ 1 / band width.** The scanner's ~15% is the
average-concentration figure; a passive wide band earns ~6% with little management, and matching the
incumbents' ±1–2 tick concentration reaches ~30%+ but must be actively kept on the peg. A second test
drives a $3M one-directional flow and confirms a tight band goes **fully out of range** (tick −2 →
−887272) and stops earning — the failure mode that pays for the tight-band yield. Nothing was funded on
mainnet or broadcast.

## Risks (why the yield exists and is not free)

- **Concentration / out-of-range.** The active band is ~±0.01–0.10%. To earn the quoted APR you sit
  tight around the peg; a sustained one-directional move parks you 100% in one asset and pays nothing
  until you rebalance. This is the active work that keeps passive capital out.
- **Flow durability.** 44–62% of volume is one desk. If it reroutes to Paxos direct mint/redeem, to a
  CEX, or to the Curve pool, the APR collapses. The desk has run this daily across every observed
  window, but it is a program, not a law.
- **USDG depeg.** USDG is a fully-reserved, NYDFS-regulated Paxos token and has held par (it trades a
  ~1–3 bp *premium* to USDC here). It is a low but nonzero tail; a break parks the LP in the weak side.
- **v4 operational load.** Minting, monitoring and rebalancing a v4 position (PositionManager, Permit2)
  is real engineering, and gas on rebalances eats small positions.

## The screen generalizes

The reusable output is not "LP this pool"; it is a **filter**: for each stablecoin in a reward/distribution
program (USDG today; more Network-style dollars are launching), find the thinnest high-turnover pool its
subsidized flow routes through, confirm the dominant taker is a pure taker (not an LP) and the pair is
stable-vs-stable, then concentrated-LP it early and exit as the APR normalizes. `captive_flow_lp.py`
computes exactly the inputs that filter needs: deployed TVL from the tick distribution, realized turnover
and fees from the logs, the marginal-LP APR curve, and the taker-concentration / taker-is-LP checks.

## A thread this closes: apxUSD and Strata are risk, not discount

While scanning 535 ERC-4626 vaults ([`../../2026-09-06/vault_oracles`](../../2026-09-06/vault_oracles)) the
largest apparent "below-NAV" cluster was **apxUSD / apyUSD (Apyx)** — a $185.8M vault
([`0x38eeb52f…`](https://etherscan.io/address/0x38eeb52f0771140d10c4e9a9a72349a329fe8a6a)) whose share
redeems for 1.42 apxUSD — and **Strata's** tranched USDe/USDat (jrUSDat at NAV **0.486**, a junior tranche
that absorbed a 51% loss). The prior day study had flagged apxUSD ~2.8% below par with its identity
unresolved. Resolved: apxUSD is Apyx's synthetic dollar **backed by STRC preferred shares** (a
Bitcoin-treasury instrument); it **actually depegged to $0.90–0.93 in June 2026** when STRC fell, and
redemption is a slow, gated, off-chain liquidation of preferred stock. Its discount is STRC tail-risk plus
a redemption queue; Strata's junior discounts are first-loss risk. These are *priced risk*, not a
redemption arbitrage — correctly excluded. The one durable, non-speculative small-capital edge in this
snapshot is the captive-flow LP above.

## Reproduce

```sh
# Deterministic scanner (public archive RPC for state, saved logs for flow):
uv run --with pycryptodome python scripts/captive_flow_lp.py                 # pinned replay
uv run --with pycryptodome python scripts/captive_flow_lp.py --offline       # cache only
uv run --with pycryptodome python scripts/captive_flow_lp.py --out research/<date>/captive_flow_lp

# Fork proof (no broadcast). Needs an archive fork provider:
cd research/2026-09-07/captive_flow_lp/fork
forge install uniswap/v4-core --no-git
forge install foundry-rs/forge-std@v1.9.6 --no-git
ETH_RPC_URL=https://eth.drpc.org forge test -vv
```

Everything is read-only. No wallet or key is configured; the report gives the pool ids, the router the
desk uses, and the position parameters, and flags the missing funded key and live rebalancing as the
operator's decisions. Contracts are research code and would need an audit before real funds.
