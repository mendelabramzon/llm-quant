#!/usr/bin/env python3
"""Seed `research/strategies.jsonl` with every strategy this repo has actually proposed, at its honest status.

Written once, kept in the tree so the book's starting state is reviewable as a diff rather than appearing from
nowhere. Each entry records where its numbers came from and, where the number was measured in a dated session and
never re-measured, says so — a strategy whose last quote is from Sunday is stale, not live, and the book's job is to
make that impossible to miss.

    uv run python scripts/seed_strategies.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import strategies as S

SEED = [
 {
  'id': 'susde-cooldown-redemption',
  'name': 'sUSDe cooldown redemption market-making',
  'kind': 'redemption',
  'status': 'fork-proven',
  'thesis': 'Buy a redeemable claim below the value the protocol pays on redemption and realise convergence through '
            'the protocol’s own cooldown. A bot cannot hold a position for a day, so this is the one edge on an '
            'efficient chain that is structurally not an MEV race.',
  'mechanism': 'Ethena’s sUSDe unstakes at NAV after a 1-day cooldown (cooldownDuration 86400). Any forced seller who '
               'will not wait a day must cross the Curve book, and the discount they pay is the fee for the waiting. '
               'The edge exists exactly because it cannot be flashed: atomic redeemability and a standing dislocation '
               'are mutually exclusive.',
  'legs': ['buy sUSDe on Curve', 'cooldownShares', 'wait 1 day', 'unstake to USDe', 'sell USDe on Curve'],
  'capacity_usd': 600000,
  'capital_days': 1.0,
  'evidence': {'findings': [], 'verify': [],
               'notes': 'research/2026-09-06/strategy/redemption_liquidity.md',
               'fork_proof': 'CooldownArb.sol + Redemption.t.sol, anvil fork at block 25918242'},
  'risks': ['USDe peg over the 1-day hold (hedge with a short)',
            'Ethena governance can lengthen cooldownDuration back to 7 days',
            'exit depth is one Curve pool; a second seller in the same day competes with you for it'],
  'kill_criteria': ['cooldownDuration() != 86400',
                    'Curve USDe/USDT (0x5B03CcCA) depth below $250k, which puts the exit below the entry size',
                    'no observed sUSDe ask below NAV − 10bps in 30 days of windows'],
  'recheck_hours': 168,
  'quotes': [{'at': '2026-09-06T13:00:00+00:00', 'window': 'research/2026-09-06/strategy', 'source': 'fork test',
              'present': True, 'net_apr': None, 'usd': None,
              'note': 'at the natural ask the round trip is −2.7bps: no trade. Under a manufactured 250k→1.5M sUSDe '
                      'sell the contract nets +4 to +263bps over one day on $118k. This is a standing bid, not a '
                      'continuous yield, and it is quoted as such.'}],
 },
 {
  'id': 'usdg-captive-flow-lp',
  'name': 'Concentrated LP to USDG captive conversion flow',
  'kind': 'liquidity',
  'status': 'fork-proven',
  'thesis': 'Provide the marginal liquidity to a taker who is paid to keep transacting, in the venue that taker '
            'underpays. Non-toxic $1↔$1 flow in a thin ultra-low-fee pool pays a fee yield far above the deep pool '
            'carrying the same risk.',
  'mechanism': 'Relay’s USDG solver rebalances inventory across chains and tops up through two thin Uniswap v4 '
               'USDC/USDG pools at 0.65–0.75bp. A dollar-for-dollar conversion carries no price information, so the '
               'flow is not adversely selected; the yield gap against the $20M Curve pool is pure underprovisioning.',
  'legs': ['mint a concentrated USDC/USDG v4 position at the active tick', 'collect fees', 'rebalance on drift'],
  'capacity_usd': 150000,
  'capital_days': 365,
  'evidence': {'findings': [], 'verify': [],
               'notes': 'research/2026-09-07/captive_flow_lp/findings.md',
               'fork_proof': 'v4 fork test minting the position in the real pool over one day of observed flow'},
  'risks': ['the desk is a cross-chain solver, not a rebate farmer: its pool use is a marginal top-up and can reroute '
            'to direct Paxos mint/redeem, which it already does in parallel at larger size',
            'APR dilutes fast — this is a $10k–$500k edge and nothing more',
            'v4 hook and pool-manager contract risk on a new venue'],
  'kill_criteria': ['deployed TVL in either pool above $5M, which takes the marginal APR under the Curve pool’s 3.8%',
                    'Relay depository throughput on Ethereum down 50% week over week',
                    'the desk’s share of pool volume below 25%, meaning the flow is no longer captive'],
  'recheck_hours': 72,
  'quotes': [{'at': '2026-09-06T20:19:00+00:00', 'window': 'research/2026-09-07/captive_flow_lp', 'source': 'scanner',
              'present': True, 'net_apr': 0.158, 'usd': None,
              'note': 'marginal-LP APR at +$50k into the 0.75bp pool: 15.8%; the 0.65bp pool 13.9%; the $20M Curve '
                      'pool paying 3.8% for the same risk'}],
 },
 {
  'id': 'pt-susds-fixed-vs-ssr',
  'name': 'PT-sUSDS fixed rate against the Sky savings rate',
  'kind': 'carry',
  'status': 'proposed',
  'thesis': 'The same USDS credit pays 137bps more fixed for 80 days than it pays floating, which is a term premium '
            'rather than a mispricing — but a term premium on an 80-day horizon is a trade.',
  'mechanism': 'Pendle principal tokens redeem 1:1 at maturity. PT-sUSDS-26NOV2026 implies 4.97% against a Sky '
               'savings rate of 3.60% on the identical underlying. The buyer is paid to accept that Sky governance '
               'cannot raise the rate inside the window.',
  'legs': ['buy PT-sUSDS on Pendle in clips', 'hold to maturity', 'redeem PT → sUSDS → USDS'],
  'capacity_usd': 1000000,
  'capital_days': 80,
  'evidence': {'findings': [], 'verify': [], 'notes': 'research/2026-09-06/opportunities/findings.md'},
  'risks': ['Pendle contract risk stacked on USDS risk',
            'the $3.5M pool means a $1M order eats a real part of the 137bps in impact',
            'exit before maturity is a sale back into the same pool'],
  'kill_criteria': ['Sky ssr above the PT implied APY',
                    'PT-sUSDS pool depth below $1M',
                    'implied minus floating below 50bps, which no longer pays for the lock-up'],
  'recheck_hours': 72,
  'quotes': [{'at': '2026-09-06T13:23:35+00:00', 'window': 'research/2026-09-06/opportunities', 'source': 'scanner',
              'present': True, 'net_apr': 0.0137, 'usd': None,
              'note': '4.97% fixed against 3.60% floating: +$2,913 per $1M over the 80 days, before Pendle fees'}],
 },
 {
  'id': 'morpho-usdt-borrow-vs-aave',
  'name': 'Borrow USDT on Morpho rather than Aave',
  'kind': 'spread',
  'status': 'proposed',
  'thesis': 'The cheapest dollar to borrow is not on the venue with the deepest book. A borrower already paying Aave '
            'is leaving roughly 90bps on the table whenever Spark’s allocator has just refilled the Morpho vault.',
  'mechanism': 'Spark’s liquidity layer moves USDT between its own products on a schedule. Each allocation into the '
               'Blue Chip USDT vault drops Morpho’s USDT borrow rate below Aave’s for as long as the utilisation '
               'stays down, and the borrower who is watching gets the whole gap.',
  'legs': ['supply wstETH or WBTC collateral on Morpho', 'borrow USDT', 'repay the Aave position'],
  'capacity_usd': 24000000,
  'capital_days': 365,
  'evidence': {'findings': [], 'verify': [], 'notes': 'research/2026-09-06/opportunities/findings.md'},
  'risks': ['Morpho markets are isolated: the rate moves with one vault’s allocation, not a market-wide curve',
            'the gap closes as borrowers arrive, and the allocation that opened it can be withdrawn',
            'refinancing costs gas twice and pays the spread on the way in'],
  'kill_criteria': ['Morpho USDT/wstETH utilisation above 95%, where the IRM steepens past Aave',
                    'borrow-rate gap against Aave below 25bps, which no longer pays for two refinancing legs'],
  'recheck_hours': 24,
  'quotes': [{'at': '2026-09-06T13:48:59+00:00', 'window': 'research/2026-09-06/opportunities', 'source': 'scanner',
              'present': True, 'net_apr': 0.0091, 'usd': None,
              'note': '3.35% on Morpho against 4.26% on Aave for a $10M borrow: about $90k a year'}],
 },
 {
  'id': 'compound-usdc-supply-spread',
  'name': 'Supply USDC to Compound v3 rather than Aave or SparkLend',
  'kind': 'spread',
  'status': 'monitored',
  'thesis': 'The same asset pays materially more on one venue than another for long enough to be worth moving, and '
            'the gap is a utilisation artefact rather than a credit judgement.',
  'mechanism': 'Compound v3’s USDC Comet runs at 90%+ utilisation against Aave’s 93% on a far larger book, and its '
               'kinked IRM pays the supplier the difference. The gap persists because supply is slow to move between '
               'venues, not because anyone is being compensated for extra risk.',
  'legs': ['supply USDC to Compound v3 Comet'],
  'capacity_usd': 120000000,
  'capital_days': 365,
  'evidence': {'findings': ['13b69d88bf8d'], 'verify': ['rate-gap-widest'],
               'notes': 'detectors/rate_dispersion.py; re-priced automatically every window'},
  'risks': ['Compound v3 is a single-collateral-base design: a base-asset shortfall is not isolated',
            'the rate dilutes as you supply — the detector reports the size that halves the gap',
            'a de-spiked read still assumes the window is representative of the next day'],
  'kill_criteria': ['gap below 50bps on window medians for three consecutive windows',
                    'Compound USDC utilisation below 70%, where the kink no longer pays'],
  'recheck_hours': 24,
  'quotes': [],
 },
 {
  'id': 'sky-ssr-vs-aave-usds',
  'name': 'Hold USDS in Sky savings rather than lending it on Aave',
  'kind': 'spread',
  'status': 'monitored',
  'thesis': 'The issuer pays more for its own dollar than the lending market does, at a size no lending market can '
            'absorb, and the rate does not dilute with size.',
  'mechanism': 'Sky sets the savings rate by governance and takes unlimited deposits at it, while Aave’s USDS reserve '
               'is small and barely utilised. The gap is not an arbitrage — it is the lending market failing to bid '
               'for a deposit the issuer already bids for.',
  'legs': ['deposit USDS into the Sky savings rate'],
  'capacity_usd': 1000000000,
  'capital_days': 365,
  'evidence': {'findings': ['0e76997b6c9e'], 'verify': [],
               'notes': 'detectors/rate_dispersion.py; Sky emits no ReserveDataUpdated, so the read is spot and '
                        'cannot be de-spiked — the detector says so on every hit'},
  'risks': ['Sky governance sets the rate and can cut it at any vote',
            'the read is a single head call, not a window median: no de-spiking is possible for this venue',
            'this is a savings product, not a trade; it is in the book as the floor every other dollar idea must beat'],
  'kill_criteria': ['ssr below the Aave USDS supply rate', 'gap below 100bps'],
  'recheck_hours': 24,
  'quotes': [],
 },
 {
  'id': 'jit-liquidity-mainnet',
  'name': 'Run just-in-time liquidity on mainnet v3/v4 pools',
  'kind': 'harvest',
  'status': 'retired',
  'thesis': 'Mint a concentrated position around a large swap and burn it after, collecting the fee without carrying '
            'inventory. Retired on economics, not on mechanism: the mechanism works and pays nothing.',
  'mechanism': 'The whole mainnet JIT field took $235 of fees across 144 episodes in five hours against $146k of pool '
               'fees — under 0.2%. Priced as a race with ten operators, the entire field nets about $6k a year, and '
               'that is an upper bound because it charges the median base fee rather than the bid a winner pays.',
  'legs': ['mint a concentrated position ahead of a swap', 'burn it after'],
  'capacity_usd': 0,
  'capital_days': 0,
  'evidence': {'findings': [], 'verify': [], 'notes': 'detectors/jit_liquidity.py'},
  'risks': [],
  'kill_criteria': ['already retired; revisit if the JIT share of pool fees exceeds 5% in any window'],
  'recheck_hours': 168,
  'quotes': [{'at': '2026-09-07T07:39:11+00:00', 'window': 'research/2026-09-07/live_5h', 'source': 'detector',
              'present': True, 'net_apr': 0.0, 'usd': 6134,
              'note': '$6,134 a year for the whole field at a 10% win rate, $1.63 of fee per episode'}],
 },
 {
  'id': 'stacyvault-reward-harvest',
  'name': 'Flash-farm the StacyVault reward lump',
  'kind': 'harvest',
  'status': 'retired',
  'thesis': 'A CORE-fork vault hands each accumulated reward lump to whoever is staked at that instant, and '
            '`depositFor` never sets `lastDepositBlock`, so a flash depositor takes it in one transaction.',
  'mechanism': 'Verified in source and asserted by `verify.py`’s `stacy-deposit-for` check, so the bug is real and '
               'still live. The STACY/WETH pair is thin, so the lump is worth $7.42 a run — a flat reward, not bps on '
               'the $175M of flash liquidity the run moves, which is why it looked large before it was priced.',
  'legs': ['flash-borrow from Morpho', 'mint v2 LP', 'depositFor into the vault', 'withdraw', 'unwind', 'repay'],
  'capacity_usd': 0,
  'capital_days': 0,
  'evidence': {'findings': [], 'verify': ['stacy-deposit-for'],
               'notes': 'research/2026-09-07/stacy_farm/findings.md',
               'fork_proof': 'StacyFarmer replication on a mainnet fork'},
  'risks': [],
  'kill_criteria': ['already retired; revisit only if the STACY/WETH pair holds more than $2M'],
  'recheck_hours': 168,
  'quotes': [{'at': '2026-09-07T07:39:11+00:00', 'window': 'research/2026-09-07/live_5h', 'source': 'economics',
              'present': True, 'net_apr': None, 'usd': 7.42,
              'note': '$7.42 per run against a gas cost that is a rounding error, but a flat reward that does not '
                      'scale with the flash size'}],
 },
]


def main():
    book = S.load()
    added, kept = [], []
    for s in SEED:
        if s['id'] in book:
            kept.append(s['id'])
            continue
        book[s['id']] = s
        added.append(s['id'])
    S.save(book)
    print(json.dumps({'added': added, 'already_present': kept, 'book_size': len(book)}, indent=1))


if __name__ == '__main__':
    main()
