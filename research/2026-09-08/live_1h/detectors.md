# Detector sweep — research/2026-09-08/live_1h

Ran 1 detector(s); 3 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `fixed_vs_floating` | 3 | 0.64 | Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth |

### [notable] PT-SUSDS-26NOV2026 implies 4.89% fixed for 79 days against Sky savings rate at 3.60% — term premium

```json
{
 "market": "0x9c560ebaf78e596cbcc27411d633a74d628dd7dc",
 "pt": "0xdc169abe56461a2e0c034da431ac2a3ebf596094",
 "pt_symbol": "PT-SUSDS-26NOV2026",
 "implied_apy_pct": 4.891,
 "days_to_maturity": 78.771,
 "pt_to_asset": 0.9897477279853857,
 "underlying": "SUSDS",
 "comparison": "Sky savings rate",
 "floating_pct": 3.6,
 "gap_pp": 1.291,
 "classification": "term premium",
 "pt_depth_units": 758529,
 "pt_depth_usd": 750753,
 "oracle_ready": true,
 "why": "the same credit pays more fixed than floating for a fixed term, which is a view on the floating rate and nothing else"
}
```

Economics: net APR 0.64%, $338 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSD-10DEC2026 implies 10.98% fixed for 93 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x13285bcbc27f92b47b4edb99d744c07b48c977c0",
 "pt": "0xecfafdc7741323a945a163ed068b5a3c43483957",
 "pt_symbol": "PT-REUSD-10DEC2026",
 "implied_apy_pct": 10.982,
 "days_to_maturity": 92.771,
 "pt_to_asset": 0.9738648037957929,
 "underlying": "REUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 7.382,
 "classification": "credit spread",
 "pt_depth_units": 4048771,
 "pt_depth_usd": 3942956,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.42%, $53,468 per year, GO — clears gas, impact and competition at this size

### [info] PT-TRUSD-26NOV2026 implies 10.07% fixed for 79 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xfcf009cb3135da12a6eb1f73f3ee05392a7bc947",
 "pt": "0x7191878f1fe834b28f4d0cead0e4375b814c4abb",
 "pt_symbol": "PT-TRUSD-26NOV2026",
 "implied_apy_pct": 10.069,
 "days_to_maturity": 78.771,
 "pt_to_asset": 0.9795091830341319,
 "underlying": "TRUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 6.469,
 "classification": "credit spread",
 "pt_depth_units": 618223,
 "pt_depth_usd": 605555,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 4.16%, $6,303 per year, GO — clears gas, impact and competition at this size

