# queue_live tables

## Implementation comparison (queue_book window 2024-09-26 to 2026-10-09, split 2025-10-03, $15M, out of sample)

| implementation | set | chosen | out of sample $/yr | t | 95% interval | in-sample positive | 1-day late kept |
|---|---|---|---:|---:|---|---|---:|
| taker, no delay (the backtest) | all4 | h=1 | $409,885 | 9.31 | $321,303 – $503,555 | yes | — |
| taker, no delay (the backtest) | eth3 | h=1 | $337,673 | 7.31 | $246,724 – $434,861 | yes | — |
| (a) taker checked hourly | all4 | h=1 | $392,430 | 8.14 | $297,542 – $493,309 | yes | 91% |
| (a) taker checked hourly | eth3 | h=0 | $313,402 | 6.35 | $218,826 – $417,766 | yes | 89% |
| (b) one fixed resting limit | all4 | L=15 | $191,626 | 3.84 | $101,425 – $302,107 | yes | 39% |
| (b) one fixed resting limit | eth3 | L=15 | $148,827 | 2.93 | $58,212 – $259,383 | yes | 37% |
| (c) daily re-quoted limit | all4 | requote | $210,512 | 8.01 | $157,454 – $263,332 | yes | n/a |
| (c) daily re-quoted limit | eth3 | requote | $168,566 | 6.26 | $117,022 – $223,323 | yes | n/a |
| (d) two-level ladder L / 2L | all4 | L=15|2L | $168,528 | 3.54 | $88,091 – $275,817 | yes | 45% |
| (d) two-level ladder L / 2L | eth3 | L=15|2L | $126,726 | 2.64 | $46,680 – $232,730 | yes | 43% |
| (e) hourly re-quoted limit (added) | all4 | hourly requote | $222,477 | 7.47 | $165,970 – $285,066 | yes | n/a |
| (e) hourly re-quoted limit (added) | eth3 | hourly requote | $182,929 | 5.96 | $124,108 – $249,625 | yes | n/a |
| (f) taker buying back at the next hour, later venue median | all4 | h=1 | $294,743 | 7.51 | $218,712 – $377,227 | yes | 72% |
| (f) taker buying back at the next hour, later venue median | eth3 | h=1 | $255,634 | 6.22 | $177,048 – $341,876 | yes | 76% |
| (f) taker buying back at the next hour, first later trade | all4 | h=2 | $317,253 | 7.03 | $229,382 – $413,223 | yes | 77% |
| (f) taker buying back at the next hour, first later trade | eth3 | h=1 | $289,059 | 6.14 | $200,932 – $388,869 | yes | 86% |
| (f) taker buying back at the next hour, study median, 6h carry | all4 | h=1 | $369,984 | 8.76 | $287,768 – $459,282 | yes | 90% |
| (f) taker buying back at the next hour, study median, 6h carry | eth3 | h=1 | $292,351 | 6.94 | $209,722 – $381,445 | yes | 87% |
| (g) taker buying back a day later, later venue median | all4 | h=1 | $213,113 | 5.70 | $145,226 – $293,586 | yes | 52% |
| (g) taker buying back a day later, later venue median | eth3 | h=1 | $185,810 | 4.83 | $115,341 – $267,379 | yes | 55% |
| (g) taker buying back a day later, first later trade | all4 | h=1 | $213,887 | 5.87 | $147,953 – $292,184 | yes | 52% |
| (g) taker buying back a day later, first later trade | eth3 | h=1 | $188,682 | 4.99 | $120,328 – $269,723 | yes | 56% |
| (g) taker buying back a day later, study median, 6h carry | all4 | h=1 | $249,268 | 6.79 | $181,699 – $331,593 | yes | 61% |
| (g) taker buying back a day later, study median, 6h carry | eth3 | h=1 | $195,658 | 5.19 | $126,785 – $275,064 | yes | 58% |

(b) out of sample by depth, all4: L=2 $132,750, L=5 $191,765, L=10 $206,585, L=15 $191,626, L=20 $140,080, L=30 $91,017, L=50 $69,923, L=75 $35,350

For (f) and (g) the last column is the share of the no-delay taker kept (queue_book's late-entry test kept all4 1d 91%, all4 1h 96%, eth3 1d 89%, eth3 1h 93% while still filling each sell at its own price).

### Does the discount persist? Sells that qualified in their own hour, still clearing 1bp at the later price

| asset | qualifying sells | next hour: venue median | next hour: first trade | next hour: missing | a day later: venue median | a day later: first trade | deep (>10bp) next hour / day, median |
|---|---:|---:|---:|---:|---:|---:|---:|
| lido | 138092 | 98% (98% of $) | 98% | 0% | 91% (88% of $) | 91% | 100% / 100% |
| etherfi_ev | 37899 | 91% (91% of $) | 92% | 3% | 82% (76% of $) | 83% | 98% / 97% |
| kelp | 1635 | 34% (34% of $) | 35% | 64% | 19% (21% of $) | 18% | 35% / 21% |
| lbtc_cb | 2814 | 53% (51% of $) | 53% | 46% | 32% (27% of $) | 32% | 56% / 33% |

**Book row should carry:** f_taker_next_hour. f_taker_next_hour|median: $294,743 a year out of sample on all four (t 7.51) and $255,634 on the ETH-only book (t 6.22); the best daily-signed implementation (c_daily_requote) falls below its 95% interval on both sets. The other later-price reading gives $317,253 / $289,059. Persistence makes it work: of the sells that qualified in their own hour, 98% of stETH/wstETH and 91% of weETH still cleared the hurdle at the next hour's venue median; rsETH and LBTC lose most sells to quiet venues (no later price), not to recovery.
