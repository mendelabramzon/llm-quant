# Queue bids off Ethereum and staked collateral: kHYPE passes both ways, nothing else does — 2026-10-10

The queue bid is the repo's only family that has survived twice: holders who will not wait for a redemption queue sell
the staking token at a discount, and a patient bidder buys and redeems. Off Ethereum the queues are longer and the
bidders fewer. Two questions:

- (a) do queue bids pay on staking tokens outside Ethereum;
- (b) does a staked token as the collateral of a same-venue short (staking yield + funding) beat the savings rate.

## The answer first

Two kHYPE trades pass; nothing else clears the bar.

- **kHYPE queue bid: proposed at $10M.** It made **$140,043 a year out of sample** (95% interval $17,327 to $356,703,
  t 1.44), and $373,849 at the capacity-rule size of $30M (interval $137,989 to $703,305, t 2.65).
  - This is from 3.55M swaps rebuilt from chain over 452 days.
  - The queue pays exactly what each request fixes: every one of 13,426 confirmations matched to the wei.
  - It is lumpy. About 70% of the out-of-sample value came from one episode, 19–28 September 2026.
- **kHYPE carry: proposed as an upgrade of `hl-hype-spot-perp-carry`, not a new row.** It holds the Hyperliquid HYPE
  short against kHYPE instead of spot HYPE.
  - Out of sample it made +4.48% a year over SSR (t 2.93), against +3.27% for spot HYPE in the same window.
  - That is +1.21pp, about $60k a year at the row's $5M.
- **Solana staking tokens are capped by a fee.** Every stake pool read (JitoSOL, JupSOL, bSOL, BNSOL) charges 10bp to
  withdraw, and the discount sits just under that. The JitoSOL bid makes $0.
- **sAVAX and stS are watch items** on bar-only evidence. **slisBNB and aprMON are no-go.**
- **SOL carries fail**: Binance with BNSOL is −0.36%; Hyperliquid with JitoSOL is +2.41% with an interval that includes
  zero and the last 365 days negative.

| asset / venue | mechanism | out of sample | capacity | payout reliability | verdict |
|---|---|---|---|---|---|
| kHYPE, HyperEVM | queue bid, 7–8.5-day queue | $140,043/yr at $10M (hurdle 20bp); $373,849 at $30M | $30M by the rule; flow is much thinner in 2026 | 13,426 of 13,426 confirmations exact, 0 cancelled | **proposed** |
| HYPE short + kHYPE spot (Hyperliquid + HyperLend) | carry | +4.48%/yr over SSR (interval +1.87% to +6.64%) | $5M, same as the existing row | kHYPE redeemable at the rate | **proposed, as an upgrade** |
| sAVAX | queue bid, 15+2 days | $42,343 at $3M (interval $1,755 to $94,834) | ~$3M | source code only | watch: $20,931 if only a quarter of volume is sales |
| stS | queue bid, 14 days | $17,090 at $1M (interval $2,101 to $35,797) | ~$1M | source code only | watch |
| slisBNB | queue bid, ~8 days | $2,112 at $3M | — | source code only | no-go |
| aprMON | queue bid, ~1 day, 10bp fee | $8,301 at $100k | $100k | source code only | no-go |
| JitoSOL | queue bid, ~1 epoch, 10bp fee | $0 | — | program-enforced | no-go |
| SOL short + BNSOL (Binance) | carry | −0.36% (t −0.62) | — | — | no-go |
| SOL short + JitoSOL (Hyperliquid, cash margin) | carry | +2.41% (t 2.43, interval −0.55% to +5.31%); last 365 days −0.37% | — | — | no-go |

## Which kHYPE number to trust

**The swap-level $140,043 at $10M, not the bar-based preview of $165k.**

- **The two price sources agree.**
  - On the same pool-hours, GeckoTerminal's bar and the swap VWAP rebuilt from chain differ by 0.06–0.67bp at the median
    per pool. Volumes match (ratio 1.00).
  - Over the same 212-day window with the same queue model, the bid comes out at $181,069 on bars and $189,719 on swaps
    at $10M, and $511,447 against $433,892 at $30M.
- **The gap to the preview comes from the window, not the prices.**
  - The swap-level run covers 452 days, so its hurdle is chosen on a first half that holds the September–December 2025
    stress.
  - That chosen hurdle (20bp) turned out to be the worst of seven out of sample. Every hurdle was still positive, from
    $140k to $224k at $10M.
- **Bars carry false prints.**
  - On 2026-09-05 at 13:00 UTC, GeckoTerminal showed kHYPE 778bp under its rate on $44M of volume. The swaps show
    5.6–7.3bp that hour on the pools that carried volume.
  - Bars also only assume the sale side (half the volume); the swaps measure it.

## Data and method

- **Screen.**
  - 33 staking tokens on 12 networks, counting only GeckoTerminal pools against the native coin.
  - The full treatment went to JitoSOL ($1.94M a day), kHYPE ($1.48M), slisBNB, stS, sAVAX and aprMON.
  - JupSOL, bSOL and mSOL share JitoSOL's fee cap. tsTON and vDOT have no rate history. Cosmos staking tokens are not on
    GeckoTerminal. The rest trade under $70k a day.
- **kHYPE.**
  - Swaps rebuilt from kHYPE/WHYPE transfers in and out of 9 pools, block 7.64M to 48.19M. In a test window this matched
    Project X's own swap events on 111 of 112 swaps.
  - Kinetiq's exchange rate read every ~3 hours (3,756 samples).
  - All 15,167 withdrawal requests and 13,663 confirmations decoded.
  - Valantis STEX ($326M of volume at 9.0bp) is Kinetiq's instant-unstake pool and holds no kHYPE to sell back. It is
    treated as a competing bidder, not a venue.
- **Other queue bids.** GeckoTerminal hourly bars (half the volume treated as sales, a quarter as a sensitivity), priced
  against archive reads of each token's exchange rate.
- **The bid.**
  - It reuses `queue_book.simulate_book` (the shared rule) and `backtest.choose_then_test`.
  - Each fill pays two pool fees and is capped at the median venue less one fee. It is also charged the staking yield
    given up over the queue and any redemption fee.
  - The kHYPE wait is the fastest confirmation seen within a day of each fill, never under 7 days; its median is 8.47
    days.
  - Sizes from $0.1M to $30M, hurdles 0–20bp. The hurdle is chosen on the first half (split 2026-02-26) and scored once
    on the second.
- **The carry.**
  - It reuses `term_carry.run_carry_block`. The staking token's daily rate growth and its daily mark against the native
    coin go in as the spot leg's extra return.
  - The existing HYPE row reproduces exactly: +4.30%, t 5.68.

## Results

**How the kHYPE queue paid.**

- 41.4M HYPE was requested and 41.1M paid. At the end 1,504 requests (337,096 HYPE) were unconfirmed, matching the
  contract's own queue total.
- A 10bp unstake fee applied to 10,791 requests; it was set to zero on 2026-04-08.
- The fastest confirmation was 7.00 days in every month since September 2025.
- During the 2025-09-24 depeg the queue still paid exactly, in 8.3–8.5 days.

**kHYPE's discount to its rate.**

- Hourly median 9.8bp, 90th percentile 30.1bp, 99th 64.1bp.
- It was at least 20bp in 23% of hours.
- The largest episodes:

| episode | discount | volume |
|---|---:|---:|
| 2025-09-23 to 09-30 | 103bp | $373M |
| 2025-10-10 to 10-21 | 55bp | $531M |
| November 2025 | 31bp | $458M |
| December 2025 | 29bp | $203M |
| 2026-09-19 to 09-28 | 47bp | $58M |
| 2026-05-18 to 06-08 | 17.5bp | $202M |

**Capacity.** Sales the bid could have bought at a profit came on 283 of 452 days: $1.8M on the median such day, $9.6M
at the 90th percentile.

**kHYPE variants at $10M:**

| variant | out of sample |
|---|---:|
| as quoted | $140,043 |
| capital borrowed as WHYPE on HyperLend (2.25%) instead of charging the staking yield | $156,977 |
| fixed 7-day wait | $141,087 |
| keeping the 2025-09-24 depeg prints that the 300bp filter drops | $139,981 |
| no venue-median cap (upper bound) | $185,553 |

**Locked capital.**

- Saved at `analysis.json` → `queue_bids.khype.locked_capital_daily_unbounded`: daily USD, 452 days, unbounded capital,
  20bp hurdle.
- Peak $194.0M on 2025-10-18. Capital was locked on 145 of 452 days; the 90th percentile is $12.4M and the 2026 mean is
  $0.85M.

**The other queue bids.**

- **JitoSOL.**
  - Hourly discount: median 7.4bp, 90th percentile 10.5bp.
  - Instant exits via Jupiter cost −7.0 to −7.3bp up to 1,000 JitoSOL, and −15.8bp at 50,000.
  - Even with unlimited capital the bid would have earned $2.3k a year.
- **slisBNB.** A steady 12.7bp discount, which is the 5bp pool fee paid twice plus about 2bp. In sample it made
  $113,743; out of sample it collapsed to $2,112.
- **sAVAX.** Rests on essentially one pool (Pharaoh) with no cross-venue check. A swap-level rebuild was impractical:
  the Avalanche public archive takes about 12 seconds a call.
- **stS.** Total volume was $9M over seven months.

**The kHYPE carry (part b).**

- No staking token can collateralise the short on HyperCore: Hyperliquid's portfolio margin accepts only USDC, USDT,
  HYPE and BTC. So kHYPE sits on HyperLend instead:
  - loan-to-value 59%, liquidation at 74%;
  - priced by an oracle that tracks Kinetiq's rate, not the market price, so the 12% depeg of September 2025 would not
    have triggered liquidation;
  - room for about 443k more kHYPE.
- The short's margin is USDT0 borrowed on HyperLend at a realised 10.40%. Over the window that cost 1.91% of notional,
  against 1.01% on Hyperliquid's own margin.
- Staking added 2.05% a year.
- Results:
  - Last 365 days: +5.35%, against +4.03% for spot HYPE. Last 90 days: +5.17%, against +4.16%.
  - Staking alone, without marking the kHYPE discount: +4.41% (t 4.22).
  - With cash margin instead of borrowed margin: +3.44%.

**Worker's independent checks.**

- kHYPE's rate: the rate fixed in 3,838 no-fee withdrawal requests matches Kinetiq's published rate (median 0.00bp;
  widest gaps −0.57 and +0.51bp).
- JitoSOL's rate: Jito's API sits 1.42bp below the on-chain stake pool, which is one epoch of accrual. Its yield over 365
  days was 5.60%, against 5.61% from DefiLlama.

## Late entry

| trade | kept 1 hour late | kept 1 day late |
|---|---:|---:|
| kHYPE at $10M | 76% | 31% |
| kHYPE at $30M | 87% | 51% |
| stS | 93% | 72% |
| sAVAX | 74% | 54% |
| carries (always-on) | 100% | 99.8% |

The kHYPE edge arrives in bursts. An hour late keeps most of it; a day late misses the start of each episode. A resting
order (research/2026-10-10/cow_fill_check, on Ethereum) is the way to be early without being fast.

## Risks and kill criteria

**kHYPE bid.** Stop on any of:

- the trailing 90-day value falls under $10k a year (it is $245,331 now);
- any confirmation pays less than its request, or the unstake fee is switched back on;
- the fastest confirmation runs over 10 days for a month;
- withdrawals are paused for more than a week.

Risks:

- The capital is HYPE. Hedge it with a short perp, which itself earns funding; that is the carry above.
- STEX and arbitrage bidders are not simulated, so the values are ceilings for one participant.
- Most of the value comes from stress episodes.

**kHYPE carry.** Stop on any of:

- the existing HYPE row's own kill criteria;
- USDT0 borrowing above 15% for a week;
- the kHYPE loan-to-value cut below 0.4;
- HyperLend switching kHYPE to a market-price oracle;
- a Kinetiq withdrawal pause.

Risks:

- In a crash, margin has to move from HyperCore gains to HyperLend before the loan is liquidated.
- kHYPE's discount is marked against the position until the queue pays.

## What failed and why

- **Solana staking tokens:** the 10bp withdrawal fee caps the discount.
- **slisBNB:** its discount equals two pool fees.
- **aprMON:** a 10bp fee, and flow too thin beyond $100k.
- **SOL carries:** funding is too low on Binance, and the excess faded in 2026 on Hyperliquid.
- **Drift:** its data API no longer resolves and its S3 history is empty.
- **Cosmos staking tokens, tsTON, vDOT:** no data.

## Errors found in the worker's own work

1. Three public HyperEVM RPCs (official, hypurrscan, stakely) ignore the block tag; caught by comparing against
   `latest`.
2. Sanctum's `sol-value` API is 230–250bp stale.
3. JitoSOL's discount looked like an edge until the pool's withdrawal fee was parsed.
4. GeckoTerminal's false 778bp hour on 2026-09-05.
5. STEX first counted as a venue the bid could buy from.
6. Pool 0xf905's fee read as 5.65bp; it is 1bp.
7. A typo in TON's native-coin id.
8. A test fixture with the wrong scale.
9. The episode round trip ignored the 10bp fee era until 2026-04-08.
10. The variant table first labelled $30M results as $10M.
11. The 300bp print filter drops the real 2025-09-24 depeg. Re-running at 1,000bp leaves the out-of-sample value
    unchanged.
12. Monad RPCs reject batched requests (403); only rpc2 accepts them.
13. An earlier handback quoted numbers from partial data. This note supersedes it.

## Next

1. Add kHYPE to the shared queue book (done for correlation, below; a joint simulation needs kHYPE's environment
   exported).
2. A swap-level rebuild for sAVAX before sizing it, through a faster Avalanche archive.
3. A live small cycle on Kinetiq (request, then confirm) to time the 8.5-day claim path.
4. Watch BTC staking tokens on Base and BSC as LBTC extensions.

## Coordinator's checks

- **The queue's facts, read on chain** with `eth_call` at the latest block on HyperEVM, without the worker's code:
  - StakingManager `withdrawalDelay()` = **604,800 s** (7 days);
  - `unstakeFeeRate()` = **0**;
  - StakingAccountant `kHYPEToHYPE(1e18)` = **1.02623**, about 2% a year since mid-2025, consistent with the measured
    2.0–2.3%.
- **kHYPE in the shared book.** Correlated the saved daily locked-capital series with each Ethereum bid's, at 2bp and
  unbounded capital, over 2025-07-15 → 2026-10-09 (452 days; `research/2026-10-10/queue_book/analysis.json →
  khype_overlap`):

  | kHYPE against | correlation | overlap |
  |---|---:|---:|
  | stETH | −0.04 | 28% |
  | weETH | +0.02 | 31% |
  | rsETH | −0.10 | 23% |
  | LBTC | +0.08 | 34% |
  | the three ETH bids summed | −0.03 | — |

  kHYPE's stress episodes are independent of the Ethereum ones: a third independent stream for the one-pool book.
  Its capital sits on HyperEVM, so it is a sub-pool unless capital moves or is borrowed (HyperLend WHYPE) between
  episodes.

Files: `scripts/queue_bids_alt.py`, `scripts/test_queue_bids_alt.py` (20 tests), `analysis.json`, `tables.md`,
`manifest.json`, `book_entries.json` (`kinetiq-khype-queue-bid`; `hl-hype-spot-perp-carry` with `upgrade_of`), `raw/`.
