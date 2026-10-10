# One proposition, two venues: Kalshi against Polymarket — 2026-10-09

**Verdict: no strategy at real size.** Across 3,226 matched market pairs (6,508 priced structures), two back-to-back
reads of both venues' books at 20:55 and 21:23 UTC found 59 and 57 structures that lock a profit after both taker fees.
Walking every book, all of them together were worth **$30.16 and $26.05** on $8.6k and $7.3k of capital. The 90-day hourly
history shows more. Gaps that clear fees and the savings rate were common in July and August, concentrated in the deep
political markets. They have roughly halved since, and the hurdle the protocol chose on the first half earned **3.0% a
year on peak capital out of sample**, below the 3.80% Sky savings rate. `book_entries.json` is empty. What the study does
find is a measurable **venue tilt**: Kalshi prices Republicans richer than Polymarket. That is the one thing worth
watching, and election night is where it would matter. Numbers are in `analysis.json`, tables in `tables.md`, and every
matched pair with both rules excerpts and the reason it was accepted is in `matches.json`.

## 1. What was matched, and how

The universe was read between 20:13 and 20:40 UTC. On Kalshi: 15,859 open events, of which 568 series were selected
(every game-winner series, every election and politics series naming a House, Senate, governor, control, president or
mayor race, and the macro releases), giving 2,770 events with markets. On Polymarket: 23,089 active events, read in
end-date windows because gamma refuses offsets past 2,000. Candidate generation is deterministic. Games are paired by
league tag, game date (exact preferred, ±1 day allowed) and team-name overlap. Everything else is paired by title-token
overlap with a year check, since Kalshi closes election events a year after the vote. That gave 3,944 candidate event
pairs, and acceptance kept **1,373 events / 3,215 market pairs**. Hand-mapped pairs (`manual_matches.json`) added 11 more
(five FOMC buckets and six CPI threshold/bucket equivalences), plus 24 three-leg CPI structures (`manual_buckets.json`).
A Polymarket bucket "x%" equals Kalshi "Above x−0.1%" and not "Above x%", so buying the bucket YES, Above-low NO and
Above-high YES pays exactly $1 in every state, and its complement pays $2.

The qualitative layer is `RULE_CLASSES` in the script, written after reading both venues' rules for each class. Every
accepted class is **near-identical**: the normal outcome resolves the same way on both venues, and they differ on a
stated edge case. Only the CPI pairs are identical.
- Football: a tie pays 50/50 on both venues. Postponement past 48h differs: Kalshi pays a "fair price", Polymarket
  waits for the game.
- Soccer: both venues settle on the result after 90 minutes plus stoppage. On a cancellation, Kalshi pays a fair price,
  while Polymarket resolves the team markets No and the draw Yes.
- Tennis: Kalshi needs "a ball has been played". Polymarket pays the player who "advances", so a walkover differs.
- Elections: Kalshi pays on the party of the person sworn in, decided early on a media consensus. Polymarket pays on
  the declared winner.
- FOMC: Polymarket reads the upper bound and rounds odd moves up to the next 25bp. Kalshi names the move and resolves
  "maintains" Yes if the meeting is cancelled.

Limitless was read (585 active markets) and left out. Its whole active universe has traded $0.57M lifetime, and 16 of its
markets have traded more than $10k, so it cannot carry size.

**The matcher was wrong four times before it was right**, and each fix is now a test or an explicit gate:
- The first books read priced **$85,165 of "arbitrage" on $1.18M**. All of it came from false matches. "Alaska Senate
  winner?" and "Delaware Senate winner?" had been paired with *which party wins the Senate*. Texas's state House had
  been paired with control of the US House. California's governor race had been paired with a Polymarket market on
  *Fresno County's* winner. The fix requires the office words and the place tokens of both titles to be equal
  (`place_tokens`). The rejected snapshot is kept in `raw/rejected/`.
- A women's volleyball match (LSU v Kentucky) had been paired with the football game between the same universities on
  the same weekend. The fix is `sport_consistent`.
- A Counter-Strike match winner had been paired with Polymarket's *Map 1* market in the same event. The fix uses only
  full-game moneyline markets.
- A Kalshi threshold ("Above 2.8%") is not a Polymarket bucket ("2.8%"). Those pairs were mapped by hand, including the
  three-leg structures.

## 2. The live books

| | 20:55 UTC | 21:23 UTC |
|---|---:|---:|
| structures with an ask on every leg | 6,407 | 6,392 |
| median gross gap at the touch (1 − cost of a $1 set) | −2.00¢ | −2.00¢ |
| share with a positive gross gap | 3.1% | 3.2% |
| positive after both taker fees, confirmed on a back-to-back read | 59 | 57 |
| profit at the touch, all of them | $16.35 | $13.47 |
| profit walking both books, all of them | $30.16 on $8,584 | $26.05 on $7,277 |
| median annualised return of those, net of SSR | −0.1% | −0.1% |

Fees decide it. Kalshi charges 0.07 × p(1−p) per contract and Polymarket 0.04–0.05 × p(1−p), so at an even price the two
legs cost about 2.75–3¢ per $1 set. The gross gap is negative for the median structure before any fee is paid.

The survivors are near-settled House races, where one leg costs 0.96–0.99, fees are tiny and the gap is under a cent. The
best was WA-05 at $4.59 on 984 sets, then LA-03 at $4.23.

The depth at the touch says where size could exist at all:
- deep: chamber control (median $28k across 8 structures) and the October FOMC buckets ($21k);
- thin: election races ($41 median, $489 at the 90th percentile) and soccer ($119).

## 3. The history (90 days, hourly, 115 pairs)

Each hour compares Kalshi's closing YES bid and ask with Polymarket's displayed price, plus that market's own half spread
read from the latest books (floor 0.5¢). Polymarket documents the displayed price as the midpoint, or the last trade when
the spread exceeds 10¢. Hours are dropped where Kalshi's book was wider than 5¢ (3,655 dropped). Two caveats bound how
far the series can be trusted:
- **An alignment bug was found and fixed.** Polymarket's hourly points land within a minute after the boundary, 99.5% of
  them. The first version stamped them an hour later than Kalshi's candle, which manufactured a 15¢ "gap" in the Fed
  October market on 2026-09-29 19:00 UTC, an hour with 298k contracts traded on Kalshi (`test_pm_crossvenue.Alignment`).
- **Checked against the 21:23 books, the proxy is right for the median pair and optimistic in the tail.** Across 104
  pairs, the median gap from the hourly proxy minus the executable net gap from the books was 0.00¢; the mean was +0.91¢,
  the 10th percentile −0.33¢ and the 90th +0.02¢. Three pairs were positive on each measure, and they were the same
  three.

| class | pairs | hours | net > 0 after fees | hours > 1¢ | episodes |
|---|---:|---:|---:|---:|---:|
| election races | 60 | 97,533 | 18.4% | 5,611 | 3,641 |
| House and Senate control | 4 | 8,455 | 30.6% | 729 | 98 |
| FOMC October | 5 | 5,717 | 6.1% | 159 | 115 |
| CPI September | 6 | 1,617 | 13.2% | 27 | 49 |
| sports (pre-game, short histories) | 40 | 6,325 | 0.7% | 22 | 27 |

Episodes last a median of 2 hours (90th percentile 13). The largest sports "episodes" (25–47¢ on college football games in
their first days of listing) are launch-period artefacts: new markets with no real price yet. They are excluded from
everything below.

**The gaps are closing.** Split at 2026-08-25, the share of positive hours fell from 26.2% to 11.9%, hours over 1¢ from
5,093 to 1,455, and the mean positive gap from 1.10¢ to 0.67¢.

**A monitor on the history.** It enters each episode once, at its first hour, for the size the latest books show at the
touch in that direction (capped at $25k), and holds to the expected resolution. Elections are taken as resolving a week
after Polymarket's close. Politics and macro only:

| hurdle (APR net of SSR) | episodes | booked gain | first half | second half | peak capital | on peak, first → second half |
|---:|---:|---:|---:|---:|---:|---:|
| 0% | 1,876 | $98,037 | $76,468 | $21,569 | $6.19M | 10.0% → 2.8% |
| 5% | 595 | $40,814 | $28,007 | $12,807 | $1.55M | 14.7% → 6.7% |
| 10% | 209 | $22,893 | $15,518 | $7,375 | $0.61M | 20.5% → 9.7% |
| 20% | 30 | $1,186 | $420 | $766 | $0.02M | — (too small to mean anything) |

Chosen on the first half by `backtest.choose_then_test` (four variants), the hurdle was 0%, at 10.4% a year in sample and
**3.0% out of sample**, under the savings rate. The 10% hurdle would have earned about 9.7% on $0.6M peak capital in the
second half. That is roughly $60k a year, but only on two generous assumptions: every historical episode fills at
today's touch size, and Polymarket's midpoint plus half a spread was executable. Weekly booked gains at the 5% hurdle went
from $12.1k in mid-July to $0.8k in the current week. That flow agrees with what the books show now: almost nothing.

## 4. The venue tilt

Kalshi's midpoint minus Polymarket's price, by month:
- "Republicans win the House": +2.39¢ (July), +2.77¢ (August), +1.62¢ (September), +1.02¢ (October), on a contract
  trading 10–19¢.
- "Republicans win the Senate": +0.25¢, +1.57¢, +2.37¢, +1.59¢.

Across the 27 Republican-coded race markets in the history, Kalshi was higher in 74% (mean +0.48¢). Across the 31
Democratic-coded ones it was higher in 45% (mean −0.18¢). The Kalshi crowd prices Republicans richer, and most of the
history's positive hours come from that.

Mostly the tilt is not an arbitrage. A 2¢ tilt on a contract that resolves three months out is about what two venues'
capital and resolution risk cost at the savings rate, and fees take another cent. It became a trade only when it widened
past fees plus the time value. That happened in July and August, and it has been narrowing since.

## 5. Who could run it

The segmentation is real but only partial:
- **Kalshi:** a US-regulated exchange. Since October 2025 it says it is open in about 140 countries, excluding 38
  jurisdictions including the UK, Canada, France and Singapore. Non-US users can trade only on the web.
- **Polymarket international:** blocks US persons, and has since its 2022 CFTC settlement. Polymarket US is a separate
  CFTC-regulated venue (QCX) with its own, thinner books. In April 2026 Polymarket asked the CFTC about lifting the
  block; no change had been reported as of the latest coverage found.

So a non-US resident eligible on both venues can hold both legs, and the trades available to them are the ones measured
here. A US person cannot hold the Polymarket leg. That, plus Kalshi's US-heavy user base (Similarweb data reported in 2026
put US visits near 80% of its traffic), is the likely reason the tilt exists at all. Sources:
- [Sportico on Kalshi's international access](https://www.sportico.com/business/sports-betting/2025/kalshi-international-countries-access-1234874388/)
- [Cointelegraph on the 140-country expansion](https://regional-front.cointelegraph.com/news/kalshi-300-million-raise-prediction-markets-140-countries)
- [Bloomberg Law on Polymarket's US request](https://news.bloomberglaw.com/esg/polymarket-seeks-cftc-blessing-to-bring-main-exchange-back-to-us)
- [River Markets, Polymarket vs Polymarket US](https://www.rivermarkets.com/insights/polymarket-vs-polymarket-us.html)

## 6. Kill criteria and what next

Nothing enters the book. These would reopen it:
- the hourly monitor at the 5% hurdle books more than $5k in a week, at touch sizes confirmed by a books read at entry;
- or a live read finds more than $1k of after-fee profit across the matched pairs.

Next:
- **Election night (2026-11-03/04)** and the **FOMC (2026-10-28)**: read both venues' books every minute for House and
  Senate control, the key races and the October buckets. Hourly data cannot see a gap that lives for minutes, and these
  are the windows where the tilt can blow out.
- **Sports in play** needs websocket books on both venues at sub-second resolution. Hourly pre-game history shows 0.7%
  positive hours and the live books show none, but in-play gaps would be fleeting and are not measured here.
- **Kalshi against Polymarket US**: the pair a US person can actually hold.
- **Maker on one venue, taker on the other**: Polymarket charges makers nothing and most Kalshi series charge only
  takers, so resting on the cheaper side removes one fee. It needs fill data this study does not have.
