# sUSDe discount history, tables

Window 2026-03-13T20:23:59Z to 2026-09-10T12:13:11Z (blocks 24650913 to 25946913, 180.7 days). 30113 priced swaps (13209 sells, 16904 buys), $1,522,095,119 traded at NAV; 14961 dust swaps under $1,000 skipped; 15 prints beyond 100bp excluded ($549,882).
Round trip 2.7bp, capacity cap $600,000 per episode, gaps of up to 2 empty hours allowed inside an episode. sUSDe NAV 1.223562 at the start, 1.247396 at the end (181 daily samples).

## A. Raw discount to NAV (the other leg at its NAV or at par)

This is the number the `nav_discount` detector measures on a window. It includes USDe’s own price against the dollar.

Hours with at least one priced trade: 3902. Noise floor (median hourly p10-p90 spread): 1.78bp.

| series | p50 | p90 | p99 | p99.9 | max | min |
|---|---:|---:|---:|---:|---:|---:|
| volume-weighted discount, all trades | 2.8 | 9.3 | 17.3 | 23.0 | 32.5 | -18.9 |
| deepest sell of the hour | 4.5 | 10.9 | 23.9 | 34.4 | 43.1 | -20.8 |

Share of trading hours with a VW discount above the round trip 51%, at least 5bp 34%, 10bp 7%, 20bp 1%. Per trade: sells p50 5.0bp, p90 14.8bp, p99 24.7bp, max 43.1bp; buys p50 3.5bp.

Sells below NAV minus the round trip: 8758 trades, $560,852,619, 75% of sell volume.

| month | episodes | option value |
|---|---:|---:|
| 2026-03 | 44 | $4,316 |
| 2026-04 | 39 | $7,335 |
| 2026-05 | 29 | $2,424 |
| 2026-06 | 45 | $5,311 |
| 2026-07 | 11 | $3,371 |
| 2026-08 | 6 | $221 |
| 2026-09 | 19 | $2,538 |

Days with at least one qualifying hour: 106 of 181 (59%); median episode length 2 hours.

Episodes 193, hours inside episodes 1369, fillable sell volume $381,348,398 ($55,810,079 after the per-episode cap).
**Option value over the history $25,517, annualised $51,554 a year** with one $600,000 fill per episode; $76,724 a year if the position is refilled once a day inside a multi-day episode ($73,431,475 fillable). Trade-level upper bound (every sell below the round trip bought at its own price, uncapped, no competition): $912,733 a year.

### Ten deepest episodes

| start (UTC) | hours | trades | VW discount bp | deepest sell bp | sell volume | net bp | option value | min significance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-19T04:00:00Z | 80 | 2942 | 17.5 | 43.1 | $133,717,654 | 14.8 | $888 | 1.09 |
| 2026-04-01T15:00:00Z | 68 | 469 | 8.0 | 42.1 | $10,803,399 | 5.3 | $321 | 1.15 |
| 2026-04-18T21:00:00Z | 6 | 83 | 11.0 | 27.6 | $4,300,950 | 8.3 | $497 | 1.01 |
| 2026-05-01T14:00:00Z | 160 | 762 | 9.3 | 24.6 | $22,209,866 | 6.6 | $398 | 1.04 |
| 2026-07-02T01:00:00Z | 19 | 158 | 11.0 | 23.9 | $2,355,456 | 8.3 | $497 | 1.20 |
| 2026-06-26T09:00:00Z | 40 | 330 | 8.2 | 23.7 | $4,935,561 | 5.5 | $331 | 1.24 |
| 2026-07-01T05:00:00Z | 10 | 168 | 11.3 | 23.4 | $2,438,508 | 8.6 | $515 | 1.18 |
| 2026-03-22T12:00:00Z | 1 | 64 | 16.2 | 22.8 | $1,286,413 | 13.5 | $811 | 1.65 |
| 2026-05-31T20:00:00Z | 3 | 50 | 18.1 | 22.4 | $518,482 | 15.4 | $797 | 1.23 |
| 2026-03-22T02:00:00Z | 1 | 208 | 13.2 | 22.3 | $4,772,894 | 10.5 | $631 | 1.08 |

### Ten most valuable episodes

| start (UTC) | hours | VW discount bp | sell volume | capped | net bp | option value | daily-cap option value |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-19T04:00:00Z | 80 | 17.5 | $133,717,654 | $600,000 | 14.8 | $888 | $3,553 |
| 2026-03-22T12:00:00Z | 1 | 16.2 | $1,286,413 | $600,000 | 13.5 | $811 | $811 |
| 2026-05-31T20:00:00Z | 3 | 18.1 | $518,482 | $518,482 | 15.4 | $797 | $797 |
| 2026-04-22T13:00:00Z | 8 | 13.3 | $14,374,911 | $600,000 | 10.6 | $637 | $637 |
| 2026-03-22T02:00:00Z | 1 | 13.2 | $4,772,894 | $600,000 | 10.5 | $631 | $631 |
| 2026-04-22T22:00:00Z | 66 | 11.9 | $30,707,307 | $600,000 | 9.2 | $550 | $1,650 |
| 2026-07-06T18:00:00Z | 60 | 11.5 | $4,605,361 | $600,000 | 8.8 | $527 | $1,581 |
| 2026-09-05T05:00:00Z | 9 | 11.5 | $1,987,568 | $600,000 | 8.8 | $525 | $525 |
| 2026-07-01T05:00:00Z | 10 | 11.3 | $2,438,508 | $600,000 | 8.6 | $515 | $515 |
| 2026-07-02T01:00:00Z | 19 | 11.0 | $2,355,456 | $600,000 | 8.3 | $497 | $497 |

### Fifteen deepest sells

| when (UTC) | pool | sUSDe | notional at NAV | price | NAV | discount bp | tx |
|---|---|---:|---:|---:|---:|---:|---|
| 2026-04-20T01:36 | curve-sdai-susde | 285,306 | $350,327 | 1.22260 | 1.22790 | 43.1 | [0x8e1b13b0](https://etherscan.io/tx/0x8e1b13b0587006c0d134854acb8b61bfa338e2c9f15274c8f2f99bec6ef8075e) |
| 2026-04-02T22:00 | v4-susde-usdt | 81,546 | $99,965 | 1.22071 | 1.22587 | 42.1 | [0x3ad3b303](https://etherscan.io/tx/0x3ad3b303ee329187867bc97892257940061d44a8c96b01c121c1cbb1af1db554) |
| 2026-04-20T01:44 | curve-sdai-susde | 362,764 | $445,438 | 1.22273 | 1.22790 | 42.1 | [0x3f98e4a6](https://etherscan.io/tx/0x3f98e4a6539e11a3db4897788dc0fd66f6ea8be0968d0018b27351e9107c12d9) |
| 2026-04-20T02:17 | curve-sdai-susde | 30,815 | $37,838 | 1.22274 | 1.22790 | 42.1 | [0xfb789191](https://etherscan.io/tx/0xfb789191d89804dc8215046a5bfd7065ae35c8bff2cafa0a25e2c3893bbcfa80) |
| 2026-04-20T02:17 | curve-sdai-susde | 9,400 | $11,542 | 1.22292 | 1.22790 | 40.6 | [0x026b02b0](https://etherscan.io/tx/0x026b02b024b2d9af9fa0d486b89760b5f7c7455ea78ea056dd8f445d4be30f68) |
| 2026-04-20T02:14 | curve-sdai-susde | 42,146 | $51,752 | 1.22294 | 1.22790 | 40.4 | [0x8e3eb3cf](https://etherscan.io/tx/0x8e3eb3cf6b8cc2f470a40f4a993ae46a615be738b68789a0105df6aa981f26f1) |
| 2026-04-20T02:15 | curve-sdai-susde | 10,700 | $13,138 | 1.22301 | 1.22790 | 39.8 | [0x33c8fdbb](https://etherscan.io/tx/0x33c8fdbb22b461d811d0826703212ea4d705c0ca3764451e070d90969294bc78) |
| 2026-04-20T01:44 | curve-sdai-susde | 87,475 | $107,411 | 1.22311 | 1.22790 | 39.0 | [0xcaa38cea](https://etherscan.io/tx/0xcaa38ceae14a0607c93973042cf0218fa142cc8ac67f80bb32cb83ff71b8f0d5) |
| 2026-04-20T02:13 | curve-sdai-susde | 7,002 | $8,598 | 1.22315 | 1.22790 | 38.7 | [0x961e6a9d](https://etherscan.io/tx/0x961e6a9d4ee7b167268164a94f987ad59902e28591f0d4ef826caffa0d0cf04e) |
| 2026-04-20T02:11 | curve-sdai-susde | 37,403 | $45,928 | 1.22333 | 1.22790 | 37.2 | [0x03217287](https://etherscan.io/tx/0x032172873e41d22bcd433c93f6064cd072e2523320d9bd934f6802e335994e31) |
| 2026-04-20T01:39 | curve-sdai-susde | 104,774 | $128,652 | 1.22351 | 1.22790 | 35.7 | [0x18463bb4](https://etherscan.io/tx/0x18463bb45d34a2c1e06adecf7b85fec9402ee956a703f01727fe288c9fa607dd) |
| 2026-04-20T02:10 | curve-sdai-susde | 19,571 | $24,032 | 1.22355 | 1.22790 | 35.4 | [0x58c11198](https://etherscan.io/tx/0x58c111985a845a6a07142fe6b7cb9d8e94b8edb6e151df39d8f94a3526d6d944) |
| 2026-04-20T02:09 | curve-sdai-susde | 62,198 | $76,373 | 1.22358 | 1.22790 | 35.2 | [0xec99e889](https://etherscan.io/tx/0xec99e889a53b67ca1be44591a4506a8219f1a9b350a3cd59b087ba9289bf4ed9) |
| 2026-04-20T01:56 | curve-sdai-susde | 56,931 | $69,906 | 1.22360 | 1.22790 | 35.0 | [0x3c39edd7](https://etherscan.io/tx/0x3c39edd72d51cdfe1f44e09a5d51b68a0c67508d1467a435daa61135a2570ce0) |
| 2026-04-19T20:22 | v4-susde-usdt | 64,507 | $79,206 | 1.22363 | 1.22787 | 34.5 | [0x2a9122fa](https://etherscan.io/tx/0x2a9122fa59620b99de799c4d0b53921a048d23f17a62107160b4ec6c54476d19) |

## B. Discount net of the USDe basis (what a cooldown redemption that exits into a dollar captures)

Each swap’s discount less the same hour’s USDe price gap to par on Curve USDe/USDC (5194 swaps, $69,191,031 of USDe, 1737 hours, 11 prints beyond the bound excluded; hourly basis p50 3.3bp, p90 11.0bp, p99 19.1bp, max 81.1bp, min -41.9bp). 29505 swaps had a basis within 24h, 608 did not.

Hours with at least one priced trade: 3802. Noise floor (median hourly p10-p90 spread): 1.77bp.

| series | p50 | p90 | p99 | p99.9 | max | min |
|---|---:|---:|---:|---:|---:|---:|
| volume-weighted discount, all trades | -0.8 | 5.8 | 15.7 | 29.8 | 44.2 | -73.4 |
| deepest sell of the hour | 1.3 | 7.6 | 21.5 | 38.2 | 42.9 | -60.8 |

Share of trading hours with a VW discount above the round trip 26%, at least 5bp 13%, 10bp 2%, 20bp 0%. Per trade: sells p50 1.4bp, p90 11.4bp, p99 25.7bp, max 42.9bp; buys p50 0.5bp.

Sells below NAV minus the round trip: 5562 trades, $448,706,646, 61% of sell volume.

| month | episodes | option value |
|---|---:|---:|
| 2026-03 | 23 | $2,666 |
| 2026-04 | 76 | $13,489 |
| 2026-05 | 28 | $1,291 |
| 2026-06 | 2 | $179 |
| 2026-07 | 1 | $74 |
| 2026-08 | 6 | $213 |
| 2026-09 | 18 | $2,630 |

Days with at least one qualifying hour: 62 of 181 (34%); median episode length 2 hours.

Episodes 154, hours inside episodes 554, fillable sell volume $268,033,951 ($43,594,610 after the per-episode cap).
**Option value over the history $20,544, annualised $41,506 a year** with one $600,000 fill per episode; $44,632 a year if the position is refilled once a day inside a multi-day episode ($44,794,610 fillable). Trade-level upper bound (every sell below the round trip bought at its own price, uncapped, no competition): $634,888 a year.

### Ten deepest episodes

| start (UTC) | hours | trades | VW discount bp | deepest sell bp | sell volume | net bp | option value | min significance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-19T04:00:00Z | 27 | 1094 | 23.1 | 42.9 | $34,829,143 | 20.4 | $1,226 | 1.19 |
| 2026-04-20T08:00:00Z | 17 | 535 | 18.1 | 42.8 | $15,626,498 | 15.4 | $923 | 1.34 |
| 2026-04-02T21:00:00Z | 4 | 18 | 8.9 | 39.2 | $899,395 | 6.2 | $372 | 1.10 |
| 2026-04-21T11:00:00Z | 14 | 624 | 12.3 | 23.3 | $38,284,459 | 9.6 | $578 | 1.14 |
| 2026-03-22T12:00:00Z | 1 | 64 | 14.5 | 21.1 | $1,286,413 | 11.8 | $708 | 1.44 |
| 2026-04-21T02:00:00Z | 8 | 285 | 13.3 | 20.4 | $8,674,141 | 10.6 | $636 | 1.01 |
| 2026-04-12T23:00:00Z | 12 | 122 | 8.8 | 17.8 | $5,254,528 | 6.1 | $368 | 1.40 |
| 2026-09-05T05:00:00Z | 9 | 122 | 11.1 | 17.0 | $1,987,568 | 8.4 | $507 | 1.10 |
| 2026-04-18T19:00:00Z | 5 | 71 | 9.9 | 15.1 | $5,681,968 | 7.2 | $435 | 1.15 |
| 2026-04-11T08:00:00Z | 4 | 102 | 9.7 | 14.9 | $2,733,652 | 7.0 | $420 | 1.02 |

### Ten most valuable episodes

| start (UTC) | hours | VW discount bp | sell volume | capped | net bp | option value | daily-cap option value |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-19T04:00:00Z | 27 | 23.1 | $34,829,143 | $600,000 | 20.4 | $1,226 | $2,452 |
| 2026-04-20T08:00:00Z | 17 | 18.1 | $15,626,498 | $600,000 | 15.4 | $923 | $923 |
| 2026-03-22T12:00:00Z | 1 | 14.5 | $1,286,413 | $600,000 | 11.8 | $708 | $708 |
| 2026-04-21T02:00:00Z | 8 | 13.3 | $8,674,141 | $600,000 | 10.6 | $636 | $636 |
| 2026-04-21T11:00:00Z | 14 | 12.3 | $38,284,459 | $600,000 | 9.6 | $578 | $578 |
| 2026-09-05T05:00:00Z | 9 | 11.1 | $1,987,568 | $600,000 | 8.4 | $507 | $507 |
| 2026-04-14T09:00:00Z | 2 | 10.4 | $948,532 | $600,000 | 7.7 | $461 | $461 |
| 2026-09-05T02:00:00Z | 2 | 10.1 | $1,135,747 | $600,000 | 7.4 | $445 | $445 |
| 2026-04-18T19:00:00Z | 5 | 9.9 | $5,681,968 | $600,000 | 7.2 | $435 | $435 |
| 2026-04-11T08:00:00Z | 4 | 9.7 | $2,733,652 | $600,000 | 7.0 | $420 | $420 |

### Fifteen deepest sells

| when (UTC) | pool | sUSDe | notional at NAV | price | NAV | discount bp | tx |
|---|---|---:|---:|---:|---:|---:|---|
| 2026-04-20T01:36 | curve-sdai-susde | 285,306 | $350,327 | 1.22260 | 1.22790 | 42.9 | [0x8e1b13b0](https://etherscan.io/tx/0x8e1b13b0587006c0d134854acb8b61bfa338e2c9f15274c8f2f99bec6ef8075e) |
| 2026-04-20T09:29 | v4-susde-usdt | 63,195 | $77,600 | 1.22414 | 1.22794 | 42.8 | [0x6044ce7f](https://etherscan.io/tx/0x6044ce7f108b0faad72d84c28d74814f7e257b011b0db79f4537c0aceffba776) |
| 2026-04-20T01:44 | curve-sdai-susde | 362,764 | $445,438 | 1.22273 | 1.22790 | 41.9 | [0x3f98e4a6](https://etherscan.io/tx/0x3f98e4a6539e11a3db4897788dc0fd66f6ea8be0968d0018b27351e9107c12d9) |
| 2026-04-20T09:05 | v4-susde-usdt | 58,565 | $71,914 | 1.22446 | 1.22794 | 40.2 | [0x874239f3](https://etherscan.io/tx/0x874239f3236aabea3f67585173ba39b0f5ae0c93bc77890ccdbf77f397d02435) |
| 2026-04-02T22:00 | v4-susde-usdt | 81,546 | $99,965 | 1.22071 | 1.22587 | 39.2 | [0x3ad3b303](https://etherscan.io/tx/0x3ad3b303ee329187867bc97892257940061d44a8c96b01c121c1cbb1af1db554) |
| 2026-04-20T01:44 | curve-sdai-susde | 87,475 | $107,411 | 1.22311 | 1.22790 | 38.8 | [0xcaa38cea](https://etherscan.io/tx/0xcaa38ceae14a0607c93973042cf0218fa142cc8ac67f80bb32cb83ff71b8f0d5) |
| 2026-04-20T02:17 | curve-sdai-susde | 30,815 | $37,838 | 1.22274 | 1.22790 | 38.4 | [0xfb789191](https://etherscan.io/tx/0xfb789191d89804dc8215046a5bfd7065ae35c8bff2cafa0a25e2c3893bbcfa80) |
| 2026-04-20T02:17 | curve-sdai-susde | 9,400 | $11,542 | 1.22292 | 1.22790 | 36.9 | [0x026b02b0](https://etherscan.io/tx/0x026b02b024b2d9af9fa0d486b89760b5f7c7455ea78ea056dd8f445d4be30f68) |
| 2026-04-20T02:14 | curve-sdai-susde | 42,146 | $51,752 | 1.22294 | 1.22790 | 36.8 | [0x8e3eb3cf](https://etherscan.io/tx/0x8e3eb3cf6b8cc2f470a40f4a993ae46a615be738b68789a0105df6aa981f26f1) |
| 2026-04-20T02:15 | curve-sdai-susde | 10,700 | $13,138 | 1.22301 | 1.22790 | 36.2 | [0x33c8fdbb](https://etherscan.io/tx/0x33c8fdbb22b461d811d0826703212ea4d705c0ca3764451e070d90969294bc78) |
| 2026-04-19T23:18 | v4-susde-usdt | 31,000 | $38,064 | 1.22489 | 1.22789 | 36.2 | [0x98e332b5](https://etherscan.io/tx/0x98e332b5d5446744bbbb882af70c707cdffe7e8d42a5d54027385bffabd14720) |
| 2026-04-19T23:11 | v4-susde-usdt | 20,873 | $25,629 | 1.22490 | 1.22789 | 36.1 | [0xfff37043](https://etherscan.io/tx/0xfff37043021fe676a3c02cdac95912304d0cf82ac3bcea1a9ca893ec3e42f7f6) |
| 2026-04-19T23:26 | v4-susde-usdt | 24,000 | $29,469 | 1.22495 | 1.22789 | 35.7 | [0xe7618388](https://etherscan.io/tx/0xe7618388f495b64d7e27d9bf1fd541b819106aeb5d548c65669e97849b28bf0e) |
| 2026-04-20T01:39 | curve-sdai-susde | 104,774 | $128,652 | 1.22351 | 1.22790 | 35.5 | [0x18463bb4](https://etherscan.io/tx/0x18463bb45d34a2c1e06adecf7b85fec9402ee956a703f01727fe288c9fa607dd) |
| 2026-04-19T16:27 | v4-susde-usdt | 460,545 | $565,481 | 1.22528 | 1.22785 | 35.4 | [0xf2bdcdef](https://etherscan.io/tx/0xf2bdcdefee53b09ab13e7814b31b0f8b3b6aafacb7874c3cf0fb54efb33fe029) |

## C. Month by month

| month | swaps | sell volume | VW discount bp | VW sell discount bp | sell vol >= 5bp | >= 10bp | >= 20bp | USDe basis bp (VW) | VW discount net of basis bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-03 | 4168 | $87,548,030 | 3.5 | 4.7 | 51% | 9% | 1% | 4.0 | 0.7 |
| 2026-04 | 6921 | $297,851,274 | 12.1 | 13.2 | 90% | 67% | 13% | 0.3 | 9.8 |
| 2026-05 | 3471 | $105,643,638 | 3.9 | 4.8 | 38% | 14% | 2% | 9.0 | 2.0 |
| 2026-06 | 5595 | $95,877,408 | 4.9 | 6.0 | 56% | 14% | 1% | 12.8 | -4.2 |
| 2026-07 | 4172 | $75,217,425 | 2.5 | 3.8 | 49% | 20% | 2% | 4.4 | -1.8 |
| 2026-08 | 4081 | $57,554,856 | -1.8 | -0.6 | 10% | 1% | 0% | -1.4 | -1.6 |
| 2026-09 | 1705 | $25,355,248 | 4.9 | 6.2 | 62% | 10% | 0% | -5.0 | 4.2 |

## D. Kill criterion by 30-day slice

no sUSDe sell of at least $10000 at or below NAV - 10bp in a 30-day slice.

### Raw discount

Met in 1 of 7 slices.

| slice start | days | sells >= $10k | deepest sell >= $10k (bp) | when | sells >= $10k at NAV-10bp or deeper | any size | verdict |
|---|---:|---:|---:|---|---:|---:|---|
| 2026-03-13 | 30 | 1822 | 42.1 | 2026-04-02T22:00 | 218 ($18,215,440) | 299 | not met (keep) |
| 2026-04-12 | 30 | 2020 | 43.1 | 2026-04-20T01:36 | 1375 ($200,127,265) | 1807 | not met (keep) |
| 2026-05-12 | 30 | 1088 | 22.4 | 2026-05-31T20:12 | 75 ($6,070,944) | 88 | not met (keep) |
| 2026-06-11 | 30 | 1347 | 33.1 | 2026-06-25T05:02 | 290 ($19,451,150) | 379 | not met (keep) |
| 2026-07-11 | 30 | 679 | 24.0 | 2026-07-21T06:44 | 10 ($5,351,012) | 13 | not met (keep) |
| 2026-08-10 | 30 | 1153 | 17.4 | 2026-09-05T13:47 | 25 ($2,992,822) | 31 | not met (keep) |
| 2026-09-09 | 1* | 19 | 4.1 | 2026-09-10T10:46 | 0 ($0) | 0 | criterion met (kill) |

* partial slice

### Net of the USDe basis

Met in 1 of 7 slices.

| slice start | days | sells >= $10k | deepest sell >= $10k (bp) | when | sells >= $10k at NAV-10bp or deeper | any size | verdict |
|---|---:|---:|---:|---|---:|---:|---|
| 2026-03-13 | 30 | 1822 | 39.2 | 2026-04-02T22:00 | 97 ($9,434,658) | 143 | not met (keep) |
| 2026-04-12 | 30 | 2020 | 42.9 | 2026-04-20T01:36 | 1012 ($125,609,748) | 1301 | not met (keep) |
| 2026-05-12 | 30 | 1088 | 11.5 | 2026-05-31T20:12 | 6 ($1,477,154) | 6 | not met (keep) |
| 2026-06-11 | 30 | 1346 | 18.0 | 2026-06-25T05:02 | 14 ($1,746,650) | 15 | not met (keep) |
| 2026-07-11 | 30 | 661 | 17.6 | 2026-07-21T06:44 | 8 ($4,616,507) | 9 | not met (keep) |
| 2026-08-10 | 30 | 1091 | 17.0 | 2026-09-05T13:47 | 36 ($3,926,336) | 47 | not met (keep) |
| 2026-09-09 | 1* | 19 | 5.2 | 2026-09-10T00:53 | 0 ($0) | 0 | criterion met (kill) |

* partial slice

## E. By pool (raw)

| pool | swaps | volume | sell volume | VW discount bp | median bp | median sell bp | median buy bp | first | last |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| curve-sdai-susde | 3049 | $233,012,708 | $117,200,374 | 7.4 | 6.9 | 7.8 | 6.0 | 2026-03-14 | 2026-09-10 |
| curve-susde-frxusd | 1015 | $12,928,778 | $6,476,863 | 1.4 | 1.7 | 2.3 | 0.9 | 2026-08-06 | 2026-09-10 |
| v4-susde-usdt | 26049 | $1,276,153,633 | $621,370,641 | 6.6 | 4.0 | 4.8 | 3.4 | 2026-03-13 | 2026-09-10 |

## F. Prints excluded as venue liquidity failures (beyond 100bp)

| when (UTC) | pool | side | notional at NAV | price | NAV | discount bp | tx |
|---|---|---|---:|---:|---:|---:|---|
| 2026-03-15T11:00 | v4-susde-usdt | buy | $34,169 | 1.25477 | 1.22374 | -253.6 | [0x00e52f81](https://etherscan.io/tx/0x00e52f819a68e141c898bdf1ee5b9d3d3c31d26511a11472b82102ded6e5e267) |
| 2026-03-22T03:12 | v4-susde-usdt | sell | $107,202 | 0.93991 | 1.22450 | 2324.2 | [0x90548012](https://etherscan.io/tx/0x9054801226fc8a67e5e3d90d1a3dfa3b90e0442ad6c6168f7f9ec02e25c45469) |
| 2026-03-22T03:17 | v4-susde-usdt | sell | $46,969 | 0.85562 | 1.22450 | 3012.5 | [0x302558e4](https://etherscan.io/tx/0x302558e4cdbbcbcc9aa4a6c854455e8a0fb13e9703aee251b1cda46af9c9b610) |
| 2026-03-22T04:26 | v4-susde-usdt | buy | $9,420 | 1.29988 | 1.22451 | -615.5 | [0xc1dad8b8](https://etherscan.io/tx/0xc1dad8b89ce3310304c841e4bd20323a06a43b260763be33ff0db82d1f691d98) |
| 2026-03-22T04:35 | v4-susde-usdt | sell | $9,455 | 1.01260 | 1.22451 | 1730.5 | [0xe8bb1d81](https://etherscan.io/tx/0xe8bb1d81ea57861768debe52507a451a9503725ba1c70fc273c078b1c6a9c23d) |
| 2026-03-22T04:37 | v4-susde-usdt | buy | $46,752 | 1.30958 | 1.22451 | -694.7 | [0x3e2490dc](https://etherscan.io/tx/0x3e2490dc994691dcc3ad8edb2ec7aa160a1458d4281e2e9840b603b142baffbc) |
| 2026-04-08T07:47 | v4-susde-usdt | buy | $7,443 | 1.25136 | 1.22650 | -202.6 | [0x6b2faf85](https://etherscan.io/tx/0x6b2faf8516509614ba04cf3f30e8b13a508dbbde3d7f63a15ddc6343182eb231) |
| 2026-04-11T08:55 | v4-susde-usdt | sell | $80,284 | 1.21314 | 1.22686 | 111.8 | [0x88b83a80](https://etherscan.io/tx/0x88b83a806b56286eb5c497871be0611b8b0fd06d53849058ef7b3049ed13d9bb) |
| 2026-05-08T06:32 | v4-susde-usdt | buy | $66,800 | 1.24341 | 1.23053 | -104.7 | [0xfd14cf1b](https://etherscan.io/tx/0xfd14cf1b9cf1add153cce48b116539018bb33c0897eb39b31ca24b26058751e1) |
| 2026-05-11T13:10 | v4-susde-usdt | buy | $95,693 | 1.24447 | 1.23093 | -110.0 | [0xd433e89e](https://etherscan.io/tx/0xd433e89ecaa307958bd5a83611ad87c6c8fabbcf9bd4511e7277bdf3a36e599a) |
| 2026-05-13T08:53 | v4-susde-usdt | sell | $19,412 | 1.25701 | 1.23116 | -209.9 | [0xa438f37f](https://etherscan.io/tx/0xa438f37fab20a41b0a3d289f036c6d24e9104ca655ad8072828ce14ebc367161) |
| 2026-06-05T17:52 | v4-susde-usdt | buy | $9,801 | 1.25923 | 1.23421 | -202.7 | [0x80f2ae42](https://etherscan.io/tx/0x80f2ae42600ae17c9f913704bc559246f31d69b24bbae41073303981008ef184) |
| 2026-07-12T13:49 | v4-susde-usdt | buy | $6,264 | 1.27733 | 1.23893 | -309.9 | [0x1979d58f](https://etherscan.io/tx/0x1979d58f448fc8236849308fc6a75443690c5055261e9363c0e19ffecbc74710) |
| 2026-09-02T21:09 | v4-susde-usdt | buy | $8,013 | 1.30012 | 1.24622 | -432.5 | [0xa2457385](https://etherscan.io/tx/0xa24573850bcd0d203c88f695957ed652adf80b4e15f585268bf1b8efee92d41a) |
| 2026-09-06T23:15 | v4-susde-usdt | buy | $2,204 | 1.28453 | 1.24684 | -302.2 | [0x6358cad9](https://etherscan.io/tx/0x6358cad933eb0a07dd309e259eb4af60b2c2ee818fa808dbf0b90497d3a43b01) |

## Assumptions

- NAV is sampled once a day and interpolated linearly between samples; sUSDe NAV vests continuously and drifts 1-3bp a day, so the error is under 1bp.
- Swap timestamps are interpolated from one header a day; hourly buckets can be misassigned by a few minutes at their edges.
- The sDAI leg is valued at its own NAV in DAI and DAI at par; USDT, frxUSD and USDC are taken at par. A stablecoin trading off par moves the measured discount one for one.
- The raw discount includes USDe’s own price against the dollar. The strategy exits by selling USDe, so the series net of the hourly Curve USDe/USDC price is the capturable one; hours without a USDe/USDC trade inherit the last basis up to 24 hours back.
- Discounts are effective trade prices including the pool fee paid by that trader. A buyer stepping in after a seller pays the fee again; the 2.7bp round trip is meant to cover the buy leg and the USDe exit.
- Single prints more than 100bp from NAV are a venue running out of liquidity, not a market for sUSDe; they are listed and excluded from the series.
- Three sUSDe pools are read. Volume on other venues, over-the-counter flow and direct Ethena redemptions are not seen, so fillable volume is a lower bound on what was offered and an upper bound on what one bid could have taken from these pools.
- In an AMM the volume sold during an episode is what pushed the price down; a bid that absorbs it also lifts the price, so fillable volume is a generous capacity.
- Hours with fewer than 3 trades borrow the history-wide median hourly p10-p90 spread as their noise floor.
- Uniswap v4 deltas are taken from the Swap event; the saved live windows confirmed this pool settles those deltas as real transfers through the PoolManager.
