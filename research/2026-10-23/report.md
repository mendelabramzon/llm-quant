# The last two hours: 2026-10-23, 13:09 to 15:09 UTC

Window: Friday 23 October 2026, from 13:09 to 15:09 UTC. It covers the US cash open at 13:30 UTC. The question is the
repo's standing one: does anything here pay a patient trader who is not racing for speed or block position? Every
candidate below gets the late-entry test, and an executable price and capacity where one could be measured.

**Sources.** Each source has its own folder here, with the raw data gitignored.

| folder | what it holds |
|---|---|
| `eth_2h/` | Ethereum mainnet: 599 blocks, 167,653 transactions, 502,741 logs |
| `multi_2h/` | nine EVM chains |
| `perps_2h/` | Hyperliquid: 547 markets on 11 perp DEXes |
| `cex_2h/` | Binance and Bybit USDT perps: the top 200 by volume, from the new `scripts/cex_window.py` |

The news is from web search.

## Answer

**Nothing new enters the book.** The window was a quiet, risk-off US open. The one structure that looked like a rent
was alt perps whose shorts pay longs 100–1,100% a year. It fails the history test:

- Out of sample, a late-entered long collects +15% of funding per trade but loses 11% on price.
- The median trade loses 3.2%, and HAC t is 0.96.
- 0 of 32 variants survive BH.
- The mean is about five short squeezes a year.

The other leads fail too:

| lead | why it fails |
|---|---|
| Compound USDC at 5.49% (169bp over SSR) | about $1M wide |
| cross-chain dollar book | $19k a year |
| Hyperliquid funding carries | the window prints run 2–5× their 30-day means |
| USDC/USDT basis at +11bp | mean-reverts in history, but nets about 4bp a trade on about 5 trades a year, and the live episode (since Oct 13) is losing |
| wstETH at −63bp | our own feed bug, now fixed |

Two findings are worth carrying forward:

- **The failure is useful.** "Negative funding is a rent for the long" joins "positive floor funding is a rent for the
  short" (Oct 11) as a no-go. In both, the payers' motive is right about direction often enough to cover the funding.
- **Hyperliquid single-name pre-IPO perps (UNITREE) pay longs 150–400% a year** because they are the only short venue.
  That is the same structure, so on this evidence it should fail too. It is untested on Hyperliquid's own history.

## What happened

**Macro and market.** The two hours were a quiet, slightly risk-off drift. Nothing moved crypto as a whole:

- **BTC** fell from about 81.7k to 81.5k (−0.17%, a 1.2% range). It is down about 35% from the October 2025 high. On
  the day it lost 2.8%, below $82k.
- **ETH** traded between 2,378 and 2,414 and closed near 2,400.
- **Altcoins:** the median top-200 perp moved −0.01%.
- **ETF flows:** US spot BTC ETFs had $635M of outflows on Oct 22, after three days of inflows. ETH ETFs lost $110.6M.
  Grayscale's Zcash ETF took in money for a third straight day ($14.2M).
- **Liquidations:** about $431M of longs over the day.
- **Macro:** a tech sell-off took the Dow lower at the US open. Brent and WTI hit five-month highs after the attack on
  Saudi energy facilities and reports of US–Israel plans to strike Iran after the midterms. The Fed meets next week.
- **Ethereum:** core developers postponed Glamsterdam's Hoodi testnet activation.

**The two hours were the US open, on chain as much as on the exchanges.**

- **CEX volume:** Binance perp volume ran at 2.1–2.3× its trailing 24-hour rate on BTC, ETH, SOL and HYPE. The tokenized
  US stock perps ran at 4–6×: TQQQ, AAPL, TSLA, MU, CRCL, PLTR, HOOD and SNXX, with TQQQ open interest up 25%.
- **Ethereum fees:** the base fee went from 0.12 to 0.30 gwei at 13:30, and blocks were 51% full.
- **Builders:** Titan built 311 of 599 blocks.
- **Blobs:** Base posted 1,904 and Robinhood Chain 1,041, so Robinhood Chain is still the second-largest poster.
- **EIP-7702:** 1.3% of transactions were type 0x4.

**Movers.**

- **Up:** IRYS (+7% in the window, +121% on the day, $123M traded), DOS (+8%, volume 4.7× normal), BIRB (+9%) and JCT
  (+13%).
- **Down:** AGT (−16%, a 26% range), BE (−7%, volume 3.6×) and AERO (−5%, volume 4.5×).
- None of these left a dislocation that a late entry could collect. They were price moves, not mispricings.

**Lending and dollars on Ethereum.** This was a calm window: no liquidation over $20, and no new nightly blackout.

- **Aave v3 USDC** is at 94.2% utilisation, supplying 4.07% and borrowing at 4.50–5.00% inside the window. USDT
  supplies 3.32%.
- **SSR** is 3.80%, and sUSDe vesting implies 5.01%.
- **Compound v3** supplies 5.49% on USDC and 5.22% on USDT. That pays 169bp over SSR, but the pool sits at 90.7%
  utilisation, just above its 90% kink. The kink is very steep: about $0.9M of new supply takes the rate to 4.84%, and
  about $3M takes it to 3.24%, below SSR. **It is a $1M-wide edge, as the Sept 8 strategy book found for every dollar
  reserve that beats SSR.**
- **Cross-chain dollars:** across 9 chains the dollar-switch book fills at $1.7M for **$19k a year**. Avalanche USDC pays
  7.85%, but only $3.2M of it can be withdrawn, and the rate collapses past the kink. CCTP flow does not follow yield
  (rank correlation 0.05).
- **Morpho flash loans:** about $128M of USDC was flash-borrowed eight times through 0xd1c6…c7eb, and $790M of cbBTC once.
  These are atomic loops: latency business, not ours.
- **Exchange inflows:** tagged exchange wallets took in a net $58.7M of USDC and $31.7M of ETH (Binance 14: $126.5M in).
  This matches the risk-off tape but is not a tradable signal on its own.
- **Implied prices:** every stablecoin and LST traded within 3bp of NAV or par. The exceptions are USDT and crvUSD
  (−12bp), covered below. The scan first printed **wstETH at −63bp. That was our bug, not a market.** See "Correction".

**Hyperliquid (547 markets, $1.5B traded in the window, $15.7B open interest).**

- **Window funding is not the funding you earn.** The scan's "funding carries" table quotes instantaneous APRs:
  - xyz:GOLD shorts paid 26%, but the 30-day mean is 6.7%.
  - ZRO 36%, but 15.9% over 30 days.
  - xyz:BE 54%, but 11.0% over 30 days.
  - The gold carry is already a forward test (`gold-carry-watch`), and its kill line is 5.8%.
- **UNITREE pays longs.** It is the pre-IPO perp that now tracks the Shanghai listing.
  - xyz:UNITREE funding is −154% a year over 7 days and −250% over the last day. On para:UNITREE it is −313% and −420%.
  - Over the same week the price rose 53%, so shorts paid and lost on price. The funding is the cost of being the only
    short venue for a STAR-market stock.
  - Collecting it means an unhedged long, which is not a carry. It is the same structure as the Binance names below.
- **WLFI** pays −46% on Hyperliquid against +11% on Binance. Its 30-day mean on Hyperliquid is +4.9%, so the gap is one
  day old. The HL-vs-CEX funding arbitrage was already a no-go on 2026-10-09.

**Binance and Bybit funding: the one thing in the window that looked like a rent.**

- Several alt perps settle deeply negative every 4 hours, for days. Shorts pay longs:

  | perp | funding per 4h on Binance | for how long |
  |---|---|---|
  | BTWUSDT | −20 to −176bp | five days |
  | BIRBUSDT | −50 to −199bp | |
  | ALTUSDT | −27 to −99bp | since Oct 22 |
  | GTCUSDT | −10 to −71bp | |
  | ARKUSDT | −22bp (Bybit −131bp) | |

- At −50bp per 4h, a long collects about 1,100% a year.
- The payers are presumably holders who cannot borrow spot to hedge: airdrop, unlock or locked positions.
- The question is whether price drift eats the funding. That is testable from the funding and kline history the Oct 11
  alt-floor study already holds, delisted perps included. It is below.

## Candidates tested

**1. Long the perp after extreme negative funding: no-go.** Full study in
[`neg_funding_long/findings.md`](neg_funding_long/findings.md), from `scripts/neg_funding_long.py`. It covers 866
Binance perps, including 124 delisted, from 2024-10 to 2026-10-22, split at 2025-10-06, with 32 pre-registered
variants, lag-1 entry and taker costs.

- **The chosen rule:** trailing 3-day funding ≤ −100bp per 8h, ≥ $5M a day of volume, hold until funding normalises.
- **Out of sample, 153 trades:**

  | mean net | median | hit rate | HAC t | mean without the best 5 trades |
  |---:|---:|---:|---:|---:|
  | +4.0% | −3.2% | 46% | 0.96 | −3.3% |

- **Funding vs price:** funding is +15.4% and price −11.2%. Funding scales with the signal, and so does the drift:
  below −200bp per 8h, 7-day funding is +17% and the median price −14%.
- **Variants:** Bybit as the venue gives the same answer (t 1.12).
- **The Binance–Bybit gap hedge:** all 18 variants lose out of sample, and the hedge breaks in crashes (HUSDT, June
  2026).
- **The current names:** a long from Oct 18 is +76% on BIRB (price, not funding), −21% on BTW and −8% on ALT. That is
  the lottery shape the history shows.
- **The coordinator's recomputation from `trades.json.gz` matches.**

**2. USDC/USDT basis mean reversion: real but too small.**

- **Where it stands:** Binance USDCUSDT is +10–11bp. On chain, USDT clears at −12.7bp against USDC on $30M of swaps.
- **History:** since 2023 the mean premium is −0.3bp. In 2026 it is +4.2bp, and the 2026 range is −6 to +19bp.
- **Reversion:** after a ≥ 10bp close, the premium falls by 8bp over 7 days 92% of the time. Those are overlapping
  days, though.
- **As discrete trades** (enter at the next day's close, exit at ≤ 2bp or after 45 days, 1bp a side, and the USDT-vs-USDC
  lending carry of −0.75pp a year charged): 18 trades in 3.8 years, mean +4.4bp, 12 winners.
- **Recent trades lose:** 2026-06 lost 6.2bp over 45 days, and the open Oct 13 episode is −6.8bp so far.
- **Size:** about $50M a trade would make roughly $100k a year at an insignificant t, short a USDT-depeg tail.
- **Verdict:** not a book row. A watch-list candidate if the 2026 USDC premium regime ends.

**3. Lending and cross-chain dollars: about $1M wide, again.**

- Compound v3 USDC pays 5.49% at 90.7% utilisation, just above a kink that drops the supply rate from 4.84% to 3.24%
  between 90.5% and 90.0%. About $0.9M takes it to 4.8%.
- The nine-chain dollar-switch book fills at $1.7M for $19k a year.

**4. Hyperliquid funding: instantaneous is not earned.**

| market | window APR | 30-day mean |
|---|---:|---:|
| xyz:GOLD | 26% | 6.7% |
| xyz:BE | 54% | 11.0% |
| ZRO | 36% | 15.9% |

- WLFI's −46% is one day old: its 30-day mean on Hyperliquid is +4.9%.
- The gold carry is already a 90-day forward test, so nothing new here.
- **UNITREE (xyz −154% a year over 7 days, para −313%) is untested.** Test #1 predicts a no-go: shorts paid and also
  lost 53% on price this week. If a test is wanted, it is the same `neg_funding_long.py` rule on Hyperliquid history.
  `candleSnapshot` serves 5,000 bars, enough for the 2.5 months since the August listing.

## Correction: the wstETH "discount" was a feed mismatch

- `live_scan.py` priced wstETH's NAV as `stEthPerToken × STETH/USD`.
- The Chainlink STETH/USD feed has a 1% deviation threshold. It last updated at 14:53 UTC at $2,411, while ETH/USD read
  $2,395.86. That made wstETH look 63bp cheap.
- In ETH, the swaps cleared at 1.2469 against a NAV of 1.2470, so there was no discount.
- NAV is now `stEthPerToken × ETH`: Lido redeems stETH 1:1 for ETH, which is what the queue-bid trade earns. The
  re-rendered table shows −0.6bp.
- The LST queue-bid row in the book reads NAV in ETH and is unaffected.

## Housekeeping

- `.gitignore` is now a whitelist for `research/`. Only reports (`*.md`, figures, `strategy_book.txt`) and study code
  (`*.py`, our own `*.sol`, foundry configs) are tracked.
- Raw windows, ledgers (`*.jsonl`, `*.json`), logs, downloaded contract sources, forge builds, `selector_cache.json`
  and `labels_audit.json` are all untracked.
- 11,276 files left the index: `git rm --cached`, not committed, local copies kept. 504 tracked files remain.
- The history still holds the old data (`.git` is 2.3 GB). Shrinking it would need a history rewrite, which has not been
  done.
- **The forward tests had not run since Oct 11.** This session ran `forward_daily.py` once (1,593s), and every step
succeeded:

| test | status |
|---|---|
| JLP | day 13 of 60 |
| gold carry | day 12 of 90 |
| money-market rotation | 0 of 6 holds |
| DAT | 0 of 4 |
| collateral watcher | 85 events across the 12-day gap |

**The queue book (the book's largest row, $294,743 a year) returned `kill: criterion 4`.**

- c1–c3 pass. The trailing-90-day value is $326,888 a year as an hourly taker and $240,122 as a daily re-quote.
- c4 fired on proxy evidence: 3 of 289 CoW orders placed by *other* owners rested through hours in which the venue
  median, less one pool fee, cleared their limits.
  - Two are stETH bids with a 0bp limit (at NAV) that rested for 799h and 1,335h while the market sat 1–2bp under NAV.
  - One is a wstETH bid that missed a single hour by about 0.3bp, then filled 13 hours later.
- The book's own orders have never been posted; it is paper-only. So this is a reading of criterion 4's proxy, not an
  observed failure of our implementation.
- Still, it is the first kill signal on the book's biggest row. **It needs a human decision:** retire the row, or
  re-specify c4 with a minimum clearance margin above solver gas.
- The book was not changed.

## Sources (news)

- [Bitcoin price falls below $82K as spot ETFs see $635M in outflows (crypto.news)](https://crypto.news/why-is-bitcoin-price-down-today-etf-outflows/)
- [Crypto Price Today: Bitcoin at $81,668 as $635M ETF outflows drag ETH and XRP (Crypto Times)](https://www.cryptotimes.io/2026/10/23/crypto-price-today-bitcoin-price-falls-to-81668-as-635m-etf-outflows-drag-ethereum-xrp/)
- [Bitcoin price $81,568 after $431m liquidations (CryptoTicker)](https://cryptoticker.io/en/bitcoin-price-long-liquidations-nasdaq-23-october-2026/)
- [Stock Market Today, Oct. 23, 2026: Dow tumbles following tech sell-off (TheStreet)](https://thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-23-2026)
- [Crypto News October 23: Market turns red (CoinGabbar)](https://www.coingabbar.com/en/crypto-news-today-october-23-bitcoin-81k-eth-dacity-coin-price)
- [XRP and Zcash absorb millions as $635M flows out of Bitcoin (Bitbase)](https://www.bitbase.com/news/xrp-and-zcash-absorb-millions-amid-635-million-bitcoin-flush-main-crypto-news-this-morning)
- [DefiLlama hacks database](https://defillama.com/hacks)
- [Unitree IPO vs Hyperliquid pre-market perp (CoinDesk, Aug 2026)](https://www.coindesk.com/markets/2026/08/19/robot-maker-unitree-s-ipo-surges-600-outpacing-crypto-traders-premarket-bets)
