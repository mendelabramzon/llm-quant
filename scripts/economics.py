#!/usr/bin/env python3
"""One honest scorer for every opportunity the loop finds: capacity, gas, capital, competition, decay.

The problem. Each opportunity so far was priced by hand — the redemption arb, the captive-flow LP, the reward-timing
harvest, the rate dispersion. Hand-priced numbers are not comparable, and the failure mode is always the same shape:
something looks mechanically alive, and only a separate arithmetic step reveals it clears $6 a run against $4 of gas.
The StacyVault farm was exactly that, and it took a manual pass to notice.

So every opportunity reports through `score()`, which answers three questions in a fixed way:

  * **What does one run net?** Gross edge at the traded size, minus price impact on every leg, minus gas, minus fees.
  * **Where does it break even?** The size below which gas eats the edge, and the size above which impact does.
  * **What does it annualise to, honestly?** Net per run times a realistic run count, over the capital that must sit
    idle to run it, haircut by the share of runs a competitor takes first and by decay as the edge is worn down.

The output is a `Verdict` with a single `go` flag and the reason it failed, because the useful answer is usually "no".

Price impact. A leg is described by its depth, not by a magic slippage number: `impact_bps(size)` defaults to a constant
product curve, where trading `s` against reserve `R` costs roughly `s/R` in price. Passing a measured curve overrides it.

    from economics import Leg, Opportunity, score
    opp = Opportunity(
        name='sUSDe cooldown redemption arb',
        edge_bps=35,                       # gross edge on notional, before costs
        legs=[Leg('buy sUSDe on Curve', depth_usd=6e5), Leg('redeem at NAV', depth_usd=None)],
        gas_units=450_000, capital_locked_usd=1e6, capital_days=7,
        runs_per_day=1, competitors=2, decay_per_run=0.05)
    print(score(opp, size_usd=250_000, gas_gwei=0.06, eth_usd=2490).table())
"""
import argparse
import dataclasses
import json
import math
from typing import Callable, List, Optional

SECONDS_PER_YEAR = 31_536_000
DAYS_PER_YEAR = 365.0


@dataclasses.dataclass
class Leg:
    """One trade or action in the strategy, described by the depth behind it.

    `depth_usd` is the liquidity the leg trades against — a pool reserve, a redemption queue, a market's available
    borrow. `None` means the leg does not move a price (a redemption at oracle NAV, a fixed-rate deposit), so it costs
    nothing in impact but may still cap size through `capacity_usd`.
    """
    name: str
    depth_usd: Optional[float] = None
    capacity_usd: Optional[float] = None
    fee_bps: float = 0.0
    amplification: float = 1.0            # 1 = constant product; a Curve-style stable pool is far flatter near par
    impact_curve: Optional[Callable[[float], float]] = None

    def impact_bps(self, size_usd):
        """Price impact in basis points for trading `size_usd` through this leg.

        The default is the constant-product result: swapping `s` into a pool of depth `R` moves the effective price by
        about `s / R` when `s << R`, which is `10_000 * s / R` bps. A leg with a measured curve overrides it.
        """
        if self.impact_curve is not None:
            return float(self.impact_curve(size_usd))
        if not self.depth_usd:
            return 0.0
        # Amplification models a stable pool as constant product with `A` times the depth, which is what a StableSwap
        # invariant behaves like near par. It is an approximation and it stops being one once the trade pushes the pool
        # far off balance, so treat a result above a few hundred bps on an amplified leg as out of the model's range.
        r = size_usd / (self.depth_usd * max(self.amplification, 1e-9))
        # exact constant-product execution cost against a reserve R: 1 - 1/(1+r) = r/(1+r)
        return 10_000 * r / (1.0 + r)

    def cost_bps(self, size_usd):
        return self.impact_bps(size_usd) + self.fee_bps


@dataclasses.dataclass
class Opportunity:
    """A strategy expressed in the terms that decide whether it is worth doing."""
    name: str
    edge_bps: float = 0.0                 # gross edge on notional per run, before any cost
    edge_usd: float = 0.0                 # gross edge as a flat amount per run (a reward harvest, a fixed rebate)
    legs: List[Leg] = dataclasses.field(default_factory=list)
    gas_units: int = 0                    # total gas for one run, all transactions
    fixed_cost_usd: float = 0.0           # anything not gas: bridge fee, relayer tip, protocol flat fee
    capital_locked_usd: Optional[float] = None   # capital that must sit idle; defaults to the traded size
    capital_days: float = 0.0             # how long it is locked per run (a cooldown, a bridge delay)
    runs_per_day: float = 1.0
    race: bool = False                    # True when losing an attempt still costs gas (MEV-style contention)
    competitors: int = 0                  # other actors racing for the same edge
    win_rate: Optional[float] = None      # override the 1/(1+competitors) default
    decay_per_run: float = 0.0            # fraction of the edge consumed by your own runs
    notes: str = ''

    def capacity_usd(self):
        """The largest size the thinnest binding leg allows."""
        caps = [l.capacity_usd for l in self.legs if l.capacity_usd]
        return min(caps) if caps else None


@dataclasses.dataclass
class Verdict:
    opportunity: str
    size_usd: float
    gross_usd: float
    impact_usd: float
    gas_usd: float
    fixed_usd: float
    net_per_run_usd: float
    net_bps: float
    break_even_size_usd: Optional[float]
    optimal_size_usd: Optional[float]
    max_net_per_run_usd: Optional[float]
    capacity_usd: Optional[float]
    capital_usd: float
    win_rate: float
    size_matters: bool
    effective_runs_per_year: float
    annual_net_usd: float
    net_apr: float
    go: bool
    reason: str

    def as_dict(self):
        return dataclasses.asdict(self)

    def table(self):
        rows = [
            ('size traded', usd(self.size_usd)),
            ('gross edge', usd(self.gross_usd)),
            ('price impact + fees', usd(-self.impact_usd)),
            ('gas', usd(-self.gas_usd)),
            ('other fixed cost', usd(-self.fixed_usd)),
            ('net per run', '%s  (%.1f bps)' % (usd(self.net_per_run_usd), self.net_bps)),
            ('break-even size', usd(self.break_even_size_usd) if self.break_even_size_usd else 'never profitable'),
            ('best size', usd(self.optimal_size_usd) if self.size_matters else 'flat in size'),
            ('net at best size', usd(self.max_net_per_run_usd) if self.size_matters else 'n/a'),
            ('capacity cap', usd(self.capacity_usd) if self.capacity_usd else 'unbounded by leg capacity'),
            ('capital locked', usd(self.capital_usd)),
            ('win rate', '%.0f%%' % (100 * self.win_rate)),
            ('effective runs/year', '%.2f' % self.effective_runs_per_year if self.effective_runs_per_year < 10
             else format(round(self.effective_runs_per_year), ',')),
            ('net per year', usd(self.annual_net_usd)),
            ('net APR on locked capital', '%.2f%%' % (100 * self.net_apr)),
            ('verdict', ('GO — ' if self.go else 'NO — ') + self.reason),
        ]
        w = max(len(r[0]) for r in rows)
        return '\n'.join('%-*s  %s' % (w, k, v) for k, v in rows)


def usd(v):
    if v is None:
        return 'n/a'
    a = abs(v)
    sign = '-' if v < 0 else ''
    if a >= 1e9:
        return '%s$%.2fB' % (sign, a / 1e9)
    if a >= 1e6:
        return '%s$%.2fM' % (sign, a / 1e6)
    if a >= 1e3:
        return '%s$%.1fk' % (sign, a / 1e3)
    return '%s$%.2f' % (sign, a)


def gas_cost_usd(gas_units, gas_gwei, eth_usd):
    return gas_units * gas_gwei * 1e-9 * eth_usd


def net_at(opp, size_usd, gas_gwei, eth_usd, edge_bps=None):
    """Net USD for one run at a given size. The core arithmetic everything else searches over.

    Two edge shapes add: `edge_bps` scales with the size traded (a spread, a fee yield), `edge_usd` does not (a reward
    harvest, a fixed rebate). A harvest expressed as bps-on-notional silently rescales with size and reports a farm that
    nets $7 a run as if it netted hundreds.
    """
    edge = opp.edge_bps if edge_bps is None else edge_bps
    gross = size_usd * edge / 1e4 + opp.edge_usd
    impact = sum(size_usd * l.cost_bps(size_usd) / 1e4 for l in opp.legs)
    gas = gas_cost_usd(opp.gas_units, gas_gwei, eth_usd)
    return gross - impact - gas - opp.fixed_cost_usd, gross, impact, gas


def break_even_size(opp, gas_gwei, eth_usd, hi=None):
    """Smallest size whose edge covers gas and fixed cost. None when no size does.

    Net is not monotonic in size: impact grows superlinearly, so a large enough trade is unprofitable even when a small
    one clears. The search therefore runs between $1 and the *optimum*, not the capacity — bisecting up to capacity
    reports "never profitable" for any strategy whose top size is impact-bound, which is most of them.
    """
    hi = hi if hi is not None else optimal_size(opp, gas_gwei, eth_usd)[0]
    lo = 1.0
    if net_at(opp, hi, gas_gwei, eth_usd)[0] <= 0:
        return None
    if net_at(opp, lo, gas_gwei, eth_usd)[0] > 0:
        return lo
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if net_at(opp, mid, gas_gwei, eth_usd)[0] > 0:
            hi = mid
        else:
            lo = mid
        if hi / lo < 1.0001:
            break
    return hi


def size_matters(opp):
    """False when net does not depend on size: a flat reward with no leg that moves a price."""
    return bool(opp.edge_bps) or any(l.depth_usd or l.impact_curve for l in opp.legs)


def optimal_size(opp, gas_gwei, eth_usd):
    """Size maximising net per run. Impact grows superlinearly, so the optimum is interior when legs have depth."""
    cap = opp.capacity_usd() or 1e9
    if not size_matters(opp):
        return cap, net_at(opp, cap, gas_gwei, eth_usd)[0]
    lo, hi = 1.0, cap
    for _ in range(200):
        a = lo + (hi - lo) / 3
        b = hi - (hi - lo) / 3
        if net_at(opp, a, gas_gwei, eth_usd)[0] < net_at(opp, b, gas_gwei, eth_usd)[0]:
            lo = a
        else:
            hi = b
    best = (lo + hi) / 2
    return best, net_at(opp, best, gas_gwei, eth_usd)[0]


def score(opp, size_usd=None, gas_gwei=1.0, eth_usd=2500.0, min_net_usd=50.0, min_apr=0.0):
    """Price one opportunity end to end and return a go/no-go with the reason.

    The go test is deliberately strict about the two ways an edge dies quietly. A run that nets less than `min_net_usd`
    is dust regardless of its APR, because the APR is computed on capital that is not really at risk for a meaningful
    amount. And an edge whose break-even size exceeds its capacity cannot be traded at any size at all.
    """
    best_size, best_net = optimal_size(opp, gas_gwei, eth_usd)
    size = size_usd if size_usd is not None else best_size
    cap = opp.capacity_usd()
    if cap:
        size = min(size, cap)
    net, gross, impact, gas = net_at(opp, size, gas_gwei, eth_usd)
    be = break_even_size(opp, gas_gwei, eth_usd)

    win = opp.win_rate if opp.win_rate is not None else 1.0 / (1 + max(0, opp.competitors))
    attempts = opp.runs_per_day * DAYS_PER_YEAR
    # Competition enters through the *gross*, not the run count, and it enters differently for the two shapes an
    # opportunity can take. In a race you attempt every time and win a fraction, so you pay gas on the losses too —
    # that asymmetry is what kills marginal MEV. In a held position (an LP range, a supply spread) competitors dilute
    # your share of the same fees while you incur no failed attempts.
    wins = attempts * win
    # Decay: each of *your* runs consumes `decay_per_run` of the edge, so a year of runs is a geometric series rather
    # than a straight multiple. This separates a repeatable spread from a one-shot dislocation dressed as a yield.
    if opp.decay_per_run > 0 and wins > 0:
        d = 1 - opp.decay_per_run
        wins = min(wins, (1 - d ** wins) / (1 - d) if d < 1 else wins)
    capital = opp.capital_locked_usd if opp.capital_locked_usd is not None else size
    # Capital locked for a cooldown or a bridge delay cannot be redeployed, which caps runs whatever the venue allows.
    if opp.capital_days > 0:
        cap_runs = DAYS_PER_YEAR / opp.capital_days
        wins = min(wins, cap_runs)
        attempts = min(attempts, cap_runs / win if win else cap_runs)
    per_win = gross - impact - opp.fixed_cost_usd
    annual = wins * per_win - (attempts if opp.race else wins) * gas
    apr = annual / capital if capital else 0.0
    runs_eff = wins

    go, reason = True, 'clears gas, impact and competition at this size'
    if net <= 0:
        go, reason = False, 'negative net per run at this size'
    elif be is None:
        go, reason = False, 'no size covers gas and fixed cost'
    elif cap and be and be > cap:
        go, reason = False, 'break-even size $%s exceeds capacity $%s' % (format(round(be), ','), format(round(cap), ','))
    elif net < min_net_usd:
        go, reason = False, 'dust: %s per run is below the $%s floor' % (usd(net), format(round(min_net_usd), ','))
    elif apr < min_apr:
        go, reason = False, 'net APR %.2f%% below the %.2f%% floor' % (100 * apr, 100 * min_apr)

    return Verdict(opportunity=opp.name, size_usd=size, gross_usd=gross, impact_usd=impact, gas_usd=gas,
                   fixed_usd=opp.fixed_cost_usd, net_per_run_usd=net, net_bps=1e4 * net / size if size else 0.0,
                   annual_net_usd=annual,
                   break_even_size_usd=be, optimal_size_usd=best_size, max_net_per_run_usd=best_net,
                   capacity_usd=cap, capital_usd=capital, win_rate=win, size_matters=size_matters(opp),
                   effective_runs_per_year=runs_eff,
                   net_apr=apr, go=go, reason=reason)


def rank(opps, **kw):
    """Score a list of opportunities and return them worst-reason-last, best net APR first."""
    vs = [score(o, **kw) for o in opps]
    vs.sort(key=lambda v: (not v.go, -v.net_apr))
    return vs


def rank_table(verdicts):
    head = '%-38s %11s %11s %12s %9s %5s  %s' % ('opportunity', 'best size', 'net/run', 'net/year', 'net APR', 'go', 'reason')
    lines = [head, '-' * len(head)]
    for v in verdicts:
        lines.append('%-38s %11s %11s %12s %8.2f%% %5s  %s' % (
            v.opportunity[:38], usd(v.optimal_size_usd) if v.size_matters else 'flat',
            usd(v.net_per_run_usd), usd(v.annual_net_usd), 100 * v.net_apr,
            'GO' if v.go else 'no', v.reason[:40]))
    return '\n'.join(lines)


# ----------------------------------------------------------------------------------------------------------------------
# The opportunities this project has actually found, priced through the same harness so they are comparable.
# ----------------------------------------------------------------------------------------------------------------------
def known_opportunities():
    return [
        # 2026-09-07: the flash-loan reward-timing harvest on StacyVault. Mechanically live all session; the point of
        # the harness is that it prices out on gas without anyone having to notice by hand.
        Opportunity(name='StacyVault reward-timing harvest', edge_usd=7.6, gas_units=1_200_000,
                    legs=[Leg('flash borrow, deposit, harvest, exit', depth_usd=None)],
                    capital_locked_usd=1_000.0, runs_per_day=24, race=True, competitors=1, decay_per_run=0.0,
                    notes='the edge is the pending reward itself, ~$7.6 a run, so it is flat in size; a flash loan '
                          'supplies the notional, leaving only gas and a small buffer as capital'),
        # 2026-09-06: buy sUSDe below NAV and redeem through the one-day cooldown. Capacity is the DEX exit, not the vault.
        Opportunity(name='sUSDe cooldown redemption arb', edge_bps=35, gas_units=450_000,
                    legs=[Leg('buy sUSDe on Curve', depth_usd=6e5, fee_bps=1.0, capacity_usd=6e5, amplification=100),
                          Leg('redeem at NAV after cooldown', depth_usd=None)],
                    capital_days=7, runs_per_day=1, competitors=3, decay_per_run=0.10,
                    notes='proven on a mainnet fork with CooldownArb; the binding constraint is the $0.6M USDe DEX '
                          'exit, so impact, not the vault, is what caps it'),
        # 2026-09-06: lend into the Compound/Aave USDC spread. No trade, so no impact; the cost is the rate converging.
        Opportunity(name='Compound-vs-Aave USDC supply spread', edge_bps=333, gas_units=300_000,
                    legs=[Leg('supply USDC to Compound v3', depth_usd=None, capacity_usd=2e7)],
                    capital_days=365, runs_per_day=1 / 365, competitors=0, decay_per_run=0.0,
                    notes='3.33pp supply-rate gap (6.91% vs 3.58%) held through the 2026-09-07 midday window; the '
                          'edge is quoted annually, so one run per year and the APR is the edge itself'),
        # 2026-09-07: rent concentrated liquidity to subsidised captive flow in a thin v4 pool.
        Opportunity(name='captive-flow LP (thin v4 pool)', edge_bps=1500, gas_units=600_000,
                    legs=[Leg('provide concentrated liquidity', depth_usd=None, capacity_usd=2.5e5)],
                    capital_days=365, runs_per_day=1 / 365, competitors=2, decay_per_run=0.0,
                    notes='14-16% APR observed on a small-cap USDG pool; two other LPs in the same range dilute the '
                          'fee share to a third, which is the whole difference between a headline and a return'),
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--gas-gwei', type=float, default=0.06, help='base fee to price gas at (mainnet has been ~0.05)')
    p.add_argument('--eth-usd', type=float, default=2490.0)
    p.add_argument('--min-net-usd', type=float, default=50.0, help='below this a run is dust regardless of APR')
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    vs = rank(known_opportunities(), gas_gwei=a.gas_gwei, eth_usd=a.eth_usd, min_net_usd=a.min_net_usd)
    if a.json:
        print(json.dumps([v.as_dict() for v in vs], indent=1))
        return
    print(rank_table(vs))
    print()
    for v in vs:
        print('== %s ==' % v.opportunity)
        print(v.table())
        print()


if __name__ == '__main__':
    main()
