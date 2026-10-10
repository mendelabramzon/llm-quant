# Kalshi against Polymarket — tables

Generated 2026-10-09T21:30:11.089587+00:00 from `analysis.json`.

## Matching

Kalshi events with markets read: 2770; Polymarket active events: 23089; candidate event pairs: 3944; accepted market pairs: 3226 across 1378 Kalshi events.

| class | market pairs |
|---|---:|
| soccer | 1398 |
| election_party | 944 |
| football | 322 |
| esports | 172 |
| tennis | 164 |
| basketball_hockey | 126 |
| other_sport | 33 |
| baseball | 32 |
| combat | 20 |
| cpi_release | 6 |
| fomc | 5 |
| chamber_control | 4 |

Rejected at acceptance: mapping not one-to-one 61; non-sports pair left to manual review 185; weak label overlap 224; not every Kalshi market mapped 74; no candidate for the same office and place 56; no candidate of the same sport 152

## Snapshot 2026-10-09T20:55:31.882110+00:00

| | |
|---|---:|
| structures priced (two directions per pair, two per bucket) | 6508 |
| with an ask on every leg | 6407 |
| median gross gap at the touch (1 − cost per $1 set) | -2.00¢ |
| 95th percentile gross gap | 0.00¢ |
| share with a positive gross gap | 3.1% |
| positive after fees on a back-to-back read of both books | 59 |
| contracts at the touch, all of them | 4,802 |
| profit at the touch, all of them | $16.35 |
| profit walking both books, all of them | $30.16 on $8,584.46 of capital |
| median annualised return net of SSR, walked | -0.1% |

| class | structures | gross > 0 | median gross | confirmed > 0 | walked profit | capital |
|---|---:|---:|---:|---:|---:|---:|
| soccer | 2782 | 6 | -2.00¢ | 0 | — | — |
| election_party | 1879 | 163 | -2.00¢ | 57 | $29.94 | $8,528.34 |
| football | 627 | 1 | -3.00¢ | 0 | — | — |
| esports | 322 | 13 | -14.50¢ | 1 | $0.21 | $38.53 |
| tennis | 320 | 5 | -2.00¢ | 0 | — | — |
| basketball_hockey | 248 | 0 | -8.50¢ | 0 | — | — |
| baseball | 64 | 1 | -5.00¢ | 0 | — | — |
| other_sport | 58 | 0 | -42.50¢ | 0 | — | — |
| cpi_release | 52 | 6 | -1.25¢ | 1 | $0.01 | $17.59 |
| combat | 40 | 1 | -1.00¢ | 0 | — | — |
| chamber_control | 8 | 2 | -0.55¢ | 0 | — | — |
| fomc | 7 | 0 | -1.00¢ | 0 | — | — |

## Snapshot 2026-10-09T21:23:28.781418+00:00

| | |
|---|---:|
| structures priced (two directions per pair, two per bucket) | 6508 |
| with an ask on every leg | 6392 |
| median gross gap at the touch (1 − cost per $1 set) | -2.00¢ |
| 95th percentile gross gap | 0.00¢ |
| share with a positive gross gap | 3.2% |
| positive after fees on a back-to-back read of both books | 57 |
| contracts at the touch, all of them | 3,998 |
| profit at the touch, all of them | $13.47 |
| profit walking both books, all of them | $26.05 on $7,276.64 of capital |
| median annualised return net of SSR, walked | -0.1% |

| class | structures | gross > 0 | median gross | confirmed > 0 | walked profit | capital |
|---|---:|---:|---:|---:|---:|---:|
| soccer | 2772 | 8 | -2.00¢ | 0 | — | — |
| election_party | 1878 | 163 | -2.00¢ | 54 | $24.2 | $7,058.03 |
| football | 627 | 2 | -3.00¢ | 0 | — | — |
| esports | 320 | 8 | -13.00¢ | 2 | $1.84 | $201.02 |
| tennis | 318 | 6 | -2.00¢ | 0 | — | — |
| basketball_hockey | 248 | 0 | -9.00¢ | 0 | — | — |
| baseball | 64 | 1 | -5.50¢ | 0 | — | — |
| other_sport | 58 | 4 | -42.00¢ | 0 | — | — |
| cpi_release | 52 | 7 | -1.60¢ | 1 | $0.01 | $17.59 |
| combat | 40 | 1 | -1.00¢ | 0 | — | — |
| chamber_control | 8 | 2 | -0.55¢ | 0 | — | — |
| fomc | 7 | 0 | -1.00¢ | 0 | — | — |

## History (115 pairs, 90 days, Polymarket half spread assumed 0.5¢)

| class | pairs | hours with both venues | hours net > 0 | share | upper bound (no half spread) | hours > 1¢ | episodes |
|---|---:|---:|---:|---:|---:|---:|---:|
| election_party | 60 | 97533 | 17969 | 18.42% | 30.54% | 5611 | 3641 |
| chamber_control | 4 | 8455 | 2584 | 30.56% | 45.85% | 729 | 98 |
| fomc | 5 | 5717 | 346 | 6.05% | 24.54% | 159 | 115 |
| football | 19 | 4022 | 22 | 0.55% | 8.45% | 12 | 13 |
| soccer | 8 | 1879 | 15 | 0.80% | 2.13% | 2 | 6 |
| cpi_release | 6 | 1617 | 214 | 13.23% | 43.54% | 27 | 49 |
| basketball_hockey | 3 | 288 | 7 | 2.43% | 10.42% | 6 | 6 |
| tennis | 8 | 108 | 2 | 1.85% | 1.85% | 2 | 2 |
| baseball | 2 | 28 | 0 | 0.00% | 64.29% | 0 | 0 |

Episodes: 3930; median 2.0 h, p90 13 h, 149 lasting a day or more.

Stability (split at 2026-08-25T21:30:00+00:00): first half 48463 hours, 12694 positive, 5093 over 1¢; second half 71184 hours, 8465 positive, 1455 over 1¢.

| ticker | class | start | hours | peak net |
|---|---|---|---:|---:|
| KXNCAAFGAME-26OCT10STANND-STAN | football | 2026-09-29T01:00 | 3 | 46.61¢ |
| KXNCAAFGAME-26OCT10BALLNW-BALL | football | 2026-09-28T23:00 | 1 | 46.61¢ |
| KXNCAAFGAME-26OCT10BALLNW-BALL | football | 2026-09-29T01:00 | 3 | 46.61¢ |
| KXNCAAFGAME-26OCT10UCLAORE-UCLA | football | 2026-09-29T00:00 | 3 | 23.47¢ |
| KXNCAAFGAME-26OCT10BALLNW-BALL | football | 2026-10-01T08:00 | 1 | 21.32¢ |
| KXNCAAFGAME-26OCT10UCLAORE-UCLA | football | 2026-09-29T18:00 | 1 | 17.57¢ |
| GOVPARTYNV-26-R | election_party | 2026-09-13T09:00 | 2 | 17.37¢ |
| KXITFMATCH-26OCT09ANDSAL-SAL | tennis | 2026-10-09T21:00 | 1 | 15.68¢ |
| KXLIGAPORTUGALGAME-26OCT09BRASPO-SPO | soccer | 2026-10-09T20:00 | 2 | 15.43¢ |
| KXITFMATCH-26OCT09ANDSAL-AND | tennis | 2026-10-09T21:00 | 1 | 14.17¢ |
| HOUSEPA1-26-D | election_party | 2026-09-12T20:00 | 1 | 9.81¢ |
| HOUSEPA1-26-D | election_party | 2026-09-04T19:00 | 2 | 8.79¢ |
| GOVPARTYNV-26-R | election_party | 2026-09-13T00:00 | 2 | 8.78¢ |
| HOUSETX15-26-D | election_party | 2026-07-17T21:00 | 115 | 8.29¢ |
| HOUSEMT1-26-D | election_party | 2026-08-07T07:00 | 1 | 6.84¢ |

## A monitor on the history (one fill per episode at the latest touch size, clip $25,000.0)

| hurdle (APR net of SSR) | episodes | booked gain | first half | second half | peak capital | average capital | on peak | on average |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0% | 1876 | $98,036.92 | $76,467.51 | $21,569.41 | $6,191,538.98 | $3,573,566.71 | 6.4% | 11.1% |
| 5% | 595 | $40,814.14 | $28,006.9 | $12,807.24 | $1,546,638.92 | $851,914.52 | 10.7% | 19.4% |
| 10% | 209 | $22,893.24 | $15,518.02 | $7,375.22 | $614,279.67 | $385,125.74 | 15.1% | 24.1% |
| 20% | 30 | $1,185.87 | $420.26 | $765.61 | $17,796.1 | $8,682.81 | 29.0% | 59.3% |

Hurdle chosen on the first half of days: 0.00 (of 4); annualised on peak capital 10.4% in sample, 3.0% out of sample (rank 1 of 4 out of sample).

Proxy check against the books read at 2026-10-09T21:23: 104 pairs, hourly proxy minus executable net gap median +0.00¢, mean +0.91¢, p10 -0.33¢, p90 +0.02¢; positive on the proxy 3, in the books 3, both 3.

## Venue tilt: Kalshi midpoint minus Polymarket price

| market | 2026-07 | 2026-08 | 2026-09 | 2026-10 |
|---|---:|---:|---:|---:|
| CONTROLH-2026-R | +2.39¢ | +2.77¢ | +1.62¢ | +1.02¢ |
| CONTROLS-2026-R | +0.25¢ | +1.57¢ | +2.37¢ | +1.59¢ |

R-coded race markets: 27, mean +0.48¢, Kalshi higher in 74%.

D-coded race markets: 31, mean -0.18¢, Kalshi higher in 45%.
