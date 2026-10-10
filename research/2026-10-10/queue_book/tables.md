# Queue bids on one capital pool — tables

Window 2024-09-26T12:53:11Z → 2026-10-09T20:06:47Z (744 days); hurdle chosen on the first half, tested once on the second.

## Each asset alone (out of sample, $ a year)

| asset | $1M | $3M | $5M | $10M | $15M | $20M | $30M | $50M |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| etherfi_ev | $22,573 | $62,882 | $102,497 | $194,238 | $266,454 | $324,264 | $431,076 | $603,250 |
| kelp | $22,803 | $44,120 | $50,894 | $50,894 | $50,894 | $50,894 | $50,894 | $50,894 |
| lbtc_cb | $20,477 | $54,486 | $83,340 | $111,136 | $115,702 | $115,702 | $115,702 | $115,702 |
| lido | $12,616 | $43,689 | $70,798 | $129,884 | $195,839 | $262,150 | $401,697 | $646,903 |

Separate books at the book sizes: $33,000,000 of capital, $479,378 a year out of sample.

## One pool

| set | pool | chosen | out of sample | t | 95% interval | by asset |
|---|---:|---|---:|---:|---|---|
| all4 | $1M | h=10 | $36,605 | 7.92 | $28,162 – $45,493 | etherfi_ev $5,879, kelp $11,386, lbtc_cb $18,134, lido $1,205 |
| all4 | $3M | h=3 | $115,438 | 9.66 | $92,411 – $140,018 | etherfi_ev $33,856, kelp $23,612, lbtc_cb $41,838, lido $16,133 |
| all4 | $5M | h=3 | $192,197 | 8.75 | $150,059 – $237,914 | etherfi_ev $65,499, kelp $30,121, lbtc_cb $66,049, lido $30,529 |
| all4 | $10M | h=2 | $326,286 | 9.31 | $255,637 – $399,645 | etherfi_ev $132,524, kelp $31,158, lbtc_cb $89,246, lido $73,358 |
| all4 | $15M | h=1 | $409,889 | 9.31 | $321,307 – $503,564 | etherfi_ev $158,553, kelp $28,343, lbtc_cb $97,308, lido $125,684 |
| all4 | $20M | h=1 | $508,553 | 8.81 | $395,497 – $630,672 | etherfi_ev $203,907, kelp $31,757, lbtc_cb $100,432, lido $172,458 |
| all4 | $30M | h=1 | $678,884 | 7.98 | $510,035 – $860,876 | etherfi_ev $282,936, kelp $36,550, lbtc_cb $103,383, lido $256,015 |
| all4 | $50M | h=1 | $987,373 | 6.75 | $700,316 – $1,294,724 | etherfi_ev $382,884, kelp $38,612, lbtc_cb $106,320, lido $459,558 |
| eth3 | $1M | h=3 | $34,043 | 7.79 | $25,767 – $43,292 | etherfi_ev $14,046, kelp $11,999, lido $7,999 |
| eth3 | $3M | h=3 | $95,643 | 7.97 | $72,442 – $120,564 | etherfi_ev $45,415, kelp $27,509, lido $22,719 |
| eth3 | $5M | h=3 | $150,307 | 7.21 | $110,707 – $193,465 | etherfi_ev $80,813, kelp $30,532, lido $38,961 |
| eth3 | $10M | h=1 | $233,960 | 7.63 | $174,509 – $297,687 | etherfi_ev $114,844, kelp $27,301, lido $91,816 |
| eth3 | $15M | h=1 | $337,677 | 7.31 | $246,729 – $434,865 | etherfi_ev $170,402, kelp $28,522, lido $138,753 |
| eth3 | $20M | h=1 | $428,717 | 6.97 | $307,146 – $558,641 | etherfi_ev $210,536, kelp $32,376, lido $185,805 |
| eth3 | $30M | h=1 | $596,712 | 6.56 | $417,484 – $787,962 | etherfi_ev $287,676, kelp $36,671, lido $272,365 |
| eth3 | $50M | h=1 | $897,665 | 5.90 | $607,034 – $1,221,107 | etherfi_ev $387,524, kelp $38,191, lido $471,950 |

## How often the dislocations coincide (unbounded capital, hurdle 2 bp)

- Peak capital each asset would lock: etherfi_ev $185,130,752, kelp $8,824,087, lbtc_cb $28,767,771, lido $833,236,305
- Sum of the peaks $1,055,958,914; peak of the sum $915,173,646 (ETH three: $913,809,299); 99th percentile of the sum $828,904,159; 90th $505,495,856.
- Busiest day 2025-08-30T00:00:00Z; days with any capital locked: 729.

| pair | correlation of daily locked capital | days both locked | days either | overlap |
|---|---:|---:|---:|---:|
| etherfi_ev|kelp | 0.26 | 285 | 662 | 43% |
| etherfi_ev|lbtc_cb | -0.06 | 352 | 678 | 52% |
| etherfi_ev|lido | 0.70 | 347 | 555 | 63% |
| kelp|lbtc_cb | 0.04 | 365 | 600 | 61% |
| kelp|lido | 0.38 | 223 | 614 | 36% |
| lbtc_cb|lido | -0.04 | 283 | 637 | 44% |
