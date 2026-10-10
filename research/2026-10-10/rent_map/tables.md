# Rent map — tables (generated 2026-10-10T17:22:27Z; every number from analysis.json)

Fair rate: SSR 3.80% for dollars, ETH staking 2.37% for ETH, 0 for BTC and other coins. USD a year at the current run-rate (30 days unless stated).

## 1. The map (largest first)

| pool | size $/yr (band) | above fair $/yr (band) | accessible share | accessible $/yr | repo coverage |
|---|---:|---:|---:|---:|---:|
| Entertainment platforms: launchpads, trading apps, prediction markets | $6.65B ($3.12B to $6.65B) | $0.0M ($0.0M to $0.0M) | 0.00%-0.00% | $0.0M to $0.0M | 60% |
| DEX LP fees (supply side) | $4.36B ($2.49B to $4.36B) | $0.0M ($0.0M to $0.0M) | 0.00%-0.20% | $0.0M to $0.0M | 50% |
| Binance (top 100 by OI), Bybit and OKX (top 30 each) crypto perps | $2.24B ($2.24B to $2.43B) | $380.5M ($380.5M to $547.8M) | 0.00%-0.05% | $0.0M to $0.3M | 90% |
| Perp venue fees (DefiLlama Derivatives + perp front-ends) | $1.88B ($1.83B to $1.88B) | $49.4M ($24.7M to $49.4M) | 1.00%-5.00% | $0.2M to $2.5M | 30% |
| Lending and CDP interest paid by borrowers | $1.66B ($1.66B to $1.95B) | $310.6M ($247.3M to $413.2M) | 0.03%-0.10% | $0.1M to $0.4M | 90% |
| Hyperliquid main-dex crypto perps | $1.37B ($1.24B to $1.37B) | $850.0M ($709.7M to $850.0M) | 0.03%-0.15% | $0.2M to $1.3M | 80% |
| HIP-3 equity and index perps (+ Binance TradFi equity perps) | $552.4M ($356.0M to $552.4M) | $98.1M ($98.1M to $184.2M) | 0.04%-0.10% | $0.0M to $0.2M | 90% |
| Energy perps (oil, gas): funding is the roll | $431.9M ($297.7M to $431.9M) | $0.0M ($0.0M to $0.0M) | 0.00%-0.00% | $0.0M to $0.0M | 100% |
| Incentive budgets paid to depositors | $353.5M ($353.5M to $504.4M) | $353.5M ($353.5M to $504.4M) | 0.50%-2.00% | $1.8M to $10.1M | 30% |
| Gold, silver and other metal perps (all four venues) | $189.7M ($151.7M to $189.7M) | $112.8M ($90.7M to $112.8M) | 0.40%-1.20% | $0.4M to $1.4M | 20% |
| Manager and curator fees (the take, not the yield passed through) | $123.3M ($98.7M to $123.3M) | $0.0M ($0.0M to $0.0M) | 0.00%-0.00% | $0.0M to $0.0M | 0% |
| Points speculation: Pendle YT premium (implied - realised) on YT outstanding | $45.8M ($43.2M to $45.8M) | $43.2M ($43.2M to $45.8M) | 0.30%-1.00% | $0.1M to $0.5M | 90% |
| Queue impatience: LST/LRT and BTC-wrapper discounts x sell volume | $10.3M ($1.3M to $11.2M) | $7.6M ($0.8M to $9.8M) | 2.00%-10.00% | $0.0M to $1.0M | 90% |

Census total (rows that add without overlap; entertainment, manager fees and energy rolls excluded): size $12.67B, above fair $2.21B (band $1.95B to $2.72B), accessible $2.8M to $17.5M.

| pool | payer and motive | collector today | scarce resource | contestability | repo evidence |
|---|---|---|---|---|---|
| entertainment | memecoin launch and trading-app users, prediction-market bettors, gamers: entertainment | the platforms (pump.fun, trading bots, Polymarket, Kalshi) | the platform itself | not contestable by capital (owned); edges inside it are speed games | polymarket_history, pm_crossvenue: no-go (favourites, neg-risk, lags automated) |
| dex_lp | memecoin and retail swappers (PumpSwap, Meteora, Raydium, Uniswap v4 on Base) and, on major pairs, informed flow: entertainment and speed of access to new tokens; on majors the flow is mostly arbitrage, which takes LVR from LPs | LPs; on memecoin pools much of the liquidity is protocol-seeded and locked | inventory in a decaying token (memecoins), or the ability to beat LVR (on majors: none without speed) | high and racing at launch (JIT, sniping); on majors fees are below LVR for concentrated positions | jit-liquidity-mainnet retired; usdg-captive-flow-lp fork-proven (captive subsidized flow is the exception); listing_lifecycle: new tokens decay -25%/-33% at 30/60 days |
| funding_cex_crypto | leveraged longs on Binance, Bybit and OKX: leverage demand; funding sits near the 0.01%/8h formula rate | basis desks and Ethena's ~delta-neutral book (Ethena's fees ~$276M/yr include its funding), market makers | none beyond capital: BTC/ETH funding (4.1-5.0%) is within ~1pp of the savings rate | high: billions of basis capital arrive within days; altcoin excess lives in thin and new books | term_carry: DIY Ethena on Binance no-go; funding_arb: altcoin spreads in sub-$5k books; listing_lifecycle: delisting spread earned weeks before notices |
| perp_venue_fees | perp traders: taker and maker fees, HIP-3 deployer fees, front-end builder codes: leverage and venue convenience; front-ends charge for distribution (wallet perps: MetaMask, Phantom, Trust) | venue token holders (HYPE buybacks take 99% of HL fees), front-ends, and LP vaults (supply side) | a venue or a distribution channel; for LP vaults: tolerance for trader PnL and directional exposure | LP vaults are open to any depositor (pro-rata), venue fees are not | none on LP vaults (house_vaults, a sibling study, sizes trader-PnL transfers); usdg-captive-flow-lp is the DEX analogue |
| lending | borrowers: dollar loopers (sUSDe, PT and LST carry), market makers (Maple), CDP vaults (Sky): leverage on a carry; borrowing dollars against crypto without selling | suppliers (after the reserve factor) and protocols | none beyond dollars: supply rates sit at or near the savings rate | high: dollars arrive within hours; above-fair rents are the price of credit risk | multichain/strategy book: only 2 of 27 dollar reserves beat SSR (~$1M wide); cross-chain book $109k/yr; dollar PTs vs SSR died on defaults |
| funding_hl_crypto | leveraged longs on Hyperliquid (retail and on-chain natives; no KYC, high leverage, one wallet): leverage on a self-custodial venue; they pay ~9-10%/yr for BTC/ETH that cost ~4.4% on Binance | HL shorts: market makers and basis desks hedging on CEX (two-venue capital), HYPE spot holders, HLP | HL-native spot inventory as portfolio-margin collateral (PM cap 200 BTC a user; UBTC depth ~$2M within 25bp), or cheap capital on two venues | medium: the HL-Binance spread has persisted for years because two-venue capital costs about as much (funding_arb) | term_carry: HYPE spot-perp carry go (+4.30%/yr, $5M); BTC/ETH watch (t < 1 since 2025-11); funding_arb: HL vs Binance no-go at size |
| funding_hip3_equity | leveraged longs in HIP-3 equity and index perps (trade.xyz and others): 24/7 leveraged US-equity exposure without a broker; off-hours price discovery | HIP-3 shorts: market makers hedging at brokers in US hours | a broker account (cash-equity hedge) and tolerance for off-hours gap risk | medium: needs a broker plus HL margin; books are thin outside the top names | equity_offhours: thin go; tradfi_perps: Binance TradFi hedge no-go; book re-quoted $330k -> $54-73k/yr |
| funding_roll | holders of energy perps (oil, gas) whose oracles roll on the GSCI schedule: none: the funding pays each roll step (0.89-0.97 of it), a calendar price | the other side of the roll | - | priced | roll_carry: retired ($2.84M/yr line) |
| incentives | issuers and protocols buying deposits (Ethena loop programs, Sky, Spark, Usual, PayPal PYUSD, Ripple RLUSD, Robinhood USDG): marketing: growth of a stablecoin float or a market, paid from a fixed budget | depositors in rewarded vaults and markets, pro-rata; curators route flows | attention (campaigns change weekly), eligibility (KYC: "Robinhood users only"; looping required), tolerance for the issuer's credit | high in capital, low in attention: a fixed budget dilutes as deposits arrive, but each campaign must be found and read | stacyvault-reward-harvest retired; usdg-captive-flow-lp fork-proven ($150k); brainstorm 5.4 incentive-adjusted dollar yields is next (incentive_yields sibling) |
| funding_metals | leveraged longs in gold and silver perps (HL xyz, Binance, OKX, Bybit): 24/7 leveraged metal exposure from a crypto account (a broker barrier, like the equity carry) | unknown: no basis desk is visible; Binance TradFi perps have no interest floor (46% of XAU settlements zero) | a tokenized spot leg (PAXG/XAUT, 24/7, KYC to mint/redeem) and its depth; venue access (Binance TradFi perps non-US) | low-medium: the spot leg is on chain and liquid in size; the oracles follow spot (xyz GOLD/SILVER do not roll) | tradfi_perps: perp-perp metals pair (HL vs Binance) gold +2.9%, never traded; no test of perp vs tokenized spot |
| attention | passive depositors in curated vaults and yield aggregators: convenience: not choosing markets | curators and managers (performance fees) | reputation and distribution | slow (reputation) | none (not a trade) |
| points | YT buyers on Pendle (points and airdrop speculation, rate bets): points: a non-price payoff | PT holders (fixed-rate buyers, Morpho/Aave PT loopers) and Pendle LPs | duration and patience to hold a PT to maturity | medium: PT capacity is the market depth | pendle_history: PT-over-floating switch go ($216k/yr); points markets median implied - trailing 4.3% vs 1.8%; Boros no-go |
| queues | holders of queued claims (stETH, weETH, rsETH, LBTC, tBTC) who will not wait days for a redemption: impatience: immediate liquidity, mostly in stress weeks | DEX LPs, arbitrage bots, queue bidders | capital that can sit locked in a queue for days to weeks | medium: few bidders, capital lock is the barrier | dislocation_history + queue_bids_ext + queue_book: combined $15M book $409,889/yr out of sample; off-Ethereum screen (queue_bids_alt) running |

## 2. Ranking of under-contested pools (score = mid above fair x mid accessible share x (1 - coverage))

| rank | pool | above fair (mid) | accessible share (mid) | coverage | accessible $/yr (mid) | score $/yr |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Incentive budgets paid to depositors | $429.0M | 1.25% | 30% | $5.4M | $3.8M |
| 2 | Perp venue fees (DefiLlama Derivatives + perp front-ends) | $37.0M | 3.00% | 30% | $1.1M | $0.8M |
| 3 | Gold, silver and other metal perps (all four venues) | $101.7M | 0.80% | 20% | $0.8M | $0.7M |
| 4 | Hyperliquid main-dex crypto perps | $779.9M | 0.09% | 80% | $0.7M | $0.1M |
| 5 | Queue impatience: LST/LRT and BTC-wrapper discounts x sell volume | $5.3M | 6.00% | 90% | $0.3M | $0.0M |
| 6 | Points speculation: Pendle YT premium (implied - realised) on YT outstanding | $44.5M | 0.65% | 90% | $0.3M | $0.0M |
| 7 | Lending and CDP interest paid by borrowers | $330.2M | 0.07% | 90% | $0.2M | $0.0M |
| 8 | Binance (top 100 by OI), Bybit and OKX (top 30 each) crypto perps | $464.2M | 0.03% | 90% | $0.1M | $0.0M |
| 9 | HIP-3 equity and index perps (+ Binance TradFi equity perps) | $141.2M | 0.07% | 90% | $0.1M | $0.0M |
| 10 | Entertainment platforms: launchpads, trading apps, prediction markets | $0.0M | 0.00% | 60% | $0.0M | $0.0M |
| 11 | DEX LP fees (supply side) | $0.0M | 0.10% | 50% | $0.0M | $0.0M |
| 12 | Energy perps (oil, gas): funding is the roll | $0.0M | 0.00% | 100% | $0.0M | $0.0M |
| 13 | Manager and curator fees (the take, not the yield passed through) | $0.0M | 0.00% | 0% | $0.0M | $0.0M |

## 3. Perp funding by venue

| venue / slice | markets | OI | longs paid | shorts paid | net | above fair 30d (clipped) | above fair 90d | OI-weighted rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hl all | 336 | $15.69B | $1.82B | $434.2M | $1.38B | $785.5M ($1.02B) | $765.4M | 8.81% |
| hl crypto | 178 | $12.00B | $1.37B | $66.5M | $1.31B | $850.1M ($861.2M) | $787.0M | 10.88% |
| hl energy | 3 | $358.2M | $39.7M | $180.1M | $-140.4M | $-154.1M ($21.1M) | $-102.8M | -39.21% |
| hl equity | 127 | $2.14B | $328.8M | $174.6M | $154.2M | $72.9M ($115.8M) | $68.6M | 7.20% |
| hl fx | 3 | $54.8M | $2.2M | $2.5M | $-0.3M | $-2.4M ($1.2M) | $-2.1M | -0.55% |
| hl index | 14 | $630.0M | $27.2M | $8.0M | $19.2M | $-4.8M ($1.5M) | $-9.0M | 3.04% |
| hl metal | 6 | $499.1M | $42.5M | $1.5M | $41.0M | $22.0M ($22.0M) | $21.9M | 8.21% |
| hl rates | 5 | $9.3M | $3.0M | $0.9M | $2.1M | $1.8M ($2.2M) | $1.7M | 22.67% |
| hl dex io | 9 | $65.2M | $11.8M | $0.3M | $11.5M | $9.0M ($9.1M) | $2.0M | 17.65% |
| hl dex main | 178 | $12.03B | $1.37B | $66.4M | $1.31B | $851.6M ($862.7M) | $788.2M | 10.88% |
| hl dex mkts | 5 | $10.9M | $1.2M | $0.7M | $0.5M | $0.1M ($0.2M) | $-0.1M | 4.38% |
| hl dex para | 30 | $17.6M | $11.1M | $4.7M | $6.5M | $5.8M ($7.7M) | $5.3M | 36.59% |
| hl dex xyz | 114 | $3.57B | $417.0M | $362.1M | $54.9M | $-80.9M ($145.2M) | $-30.0M | 1.54% |
| binance all | 100 | $28.05B | $1.73B | $484.0M | $1.25B | $150.8M ($482.1M) | $355.9M | 4.46% |
| binance crypto | 71 | $24.22B | $1.43B | $173.2M | $1.25B | $293.7M ($344.2M) | $461.0M | 5.17% |
| binance metal | 4 | $998.6M | $83.1M | $0.2M | $82.9M | $49.3M ($49.3M) | $27.4M | 8.30% |
| binance tradfi_commodity | 3 | $470.0M | $29.1M | $232.5M | $-203.4M | $-222.2M ($21.7M) | $-173.0M | -43.28% |
| binance tradfi_equity | 21 | $2.05B | $136.4M | $48.5M | $87.9M | $13.0M ($49.8M) | $-16.3M | 4.29% |
| binance tradfi_kr_equity | 1 | $314.7M | $60.0M | $29.5M | $30.5M | $17.1M ($17.1M) | $56.9M | 9.69% |
| bybit all | 30 | $9.99B | $509.4M | $84.3M | $425.1M | $45.5M ($74.4M) | $45.5M | 4.26% |
| bybit crypto | 27 | $9.69B | $477.2M | $82.5M | $394.6M | $26.3M ($55.1M) | $26.3M | 4.07% |
| bybit metal | 3 | $295.6M | $32.3M | $1.8M | $30.5M | $19.3M ($19.3M) | $19.3M | 10.32% |
| okx all | 30 | $6.59B | $368.4M | $35.1M | $333.3M | $82.8M ($94.2M) | $82.8M | 5.06% |
| okx crypto | 28 | $6.34B | $336.6M | $35.1M | $301.5M | $60.6M ($72.0M) | $60.6M | 4.76% |
| okx metal | 2 | $252.8M | $31.8M | $0.0M | $31.8M | $22.2M ($22.2M) | $22.2M | 12.57% |

bybit: 903 perps, OI $12.60B, history for the top 30 (79% of OI); crypto tail x1.27 gives longs paid $604.6M, above fair $33.3M.

okx: 500 perps, OI $7.77B, history for the top 30 (85% of OI); crypto tail x1.19 gives longs paid $398.9M, above fair $71.8M.

Hyperliquid: top markets by |above fair| (30d)

| market | class | OI | rate now | 7d | 30d | 90d | hours at 0.00125%/h (30d) | above fair 30d |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ETH | crypto | $2.84B | -2.27% | 9.14% | 9.77% | 9.34% | 77.64% | $169.9M |
| BTC | crypto | $3.14B | 0.25% | 9.56% | 9.07% | 8.73% | 64.31% | $165.6M |
| xyz:BRENTOIL | energy | $200.5M | 57.75% | -93.39% | -54.79% | -34.23% | 0.00% | $-117.5M |
| HYPE | crypto | $1.70B | 10.95% | 8.31% | 9.11% | 9.96% | 73.33% | $90.3M |
| NEAR | crypto | $410.1M | 10.95% | 13.77% | 17.92% | 15.47% | 70.00% | $57.9M |
| xyz:CL | energy | $136.6M | 13.60% | -29.92% | -38.41% | -22.79% | 0.00% | $-57.6M |
| ZEC | crypto | $568.4M | 10.95% | 13.41% | 12.24% | 13.72% | 80.83% | $48.0M |
| xyz:SKHX | equity | $271.9M | -105.02% | 4.44% | 13.26% | 21.64% | 0.00% | $25.7M |
| SOL | crypto | $629.5M | 10.95% | 7.39% | 7.65% | 6.91% | 57.78% | $24.2M |
| PUMP | crypto | $226.5M | 10.95% | 11.07% | 14.26% | 14.69% | 71.67% | $23.7M |
| xyz:NATGAS | energy | $21.1M | 5.47% | 283.40% | 103.85% | 50.24% | 0.00% | $21.1M |
| XRP | crypto | $280.3M | 5.53% | 10.28% | 11.25% | 9.11% | 76.28% | $20.9M |
| xyz:SKHY | equity | $140.8M | -91.42% | -1.99% | -8.07% | -6.24% | 0.00% | $-16.7M |
| LIT | crypto | $178.6M | 10.95% | 10.34% | 12.92% | 11.68% | 80.97% | $16.3M |
| XMR | crypto | $68.0M | 10.95% | 24.10% | 26.57% | 34.02% | 61.94% | $15.5M |

## 4. Metal perps (oracles follow spot)

| venue | market | OI | 30d | 90d | net $/yr | above fair $/yr |
|---|---|---:|---:|---:|---:|---:|
| binance | XAUUSDT | $608.8M | 10.00% | 6.56% | $54.4M | $34.1M |
| hl | xyz:GOLD | $299.7M | 7.95% | 7.76% | $23.8M | $12.4M |
| binance | XAGUSDT | $243.8M | 8.14% | 7.11% | $18.4M | $10.0M |
| okx | XAU-USDT-SWAP | $215.6M | 12.85% | 12.85% | $27.7M | $19.5M |
| hl | xyz:SILVER | $158.5M | 8.10% | 8.30% | $12.8M | $6.8M |
| bybit | XAUTUSDT | $141.5M | 6.29% | 6.29% | $8.9M | $3.5M |
| bybit | XAUUSDT | $111.9M | 14.71% | 14.71% | $16.5M | $12.2M |
| binance | PAXGUSDT | $95.6M | 8.11% | 5.34% | $7.2M | $3.9M |
| binance | XAUTUSDT | $50.3M | 6.89% | 5.87% | $2.9M | $1.3M |
| bybit | XAGUSDT | $42.2M | 12.23% | 12.23% | $5.2M | $3.6M |
| okx | XAG-USDT-SWAP | $37.2M | 10.95% | 10.95% | $4.1M | $2.7M |
| hl | PAXG | $23.7M | 10.19% | 8.88% | $2.4M | $1.5M |
| hl | xyz:COPPER | $10.7M | 8.37% | 11.29% | $0.9M | $0.5M |
| hl | xyz:PLATINUM | $3.5M | 9.47% | 7.60% | $0.3M | $0.2M |
| hl | xyz:PALLADIUM | $3.1M | 22.37% | 28.47% | $0.7M | $0.6M |
| all | 15 markets | $2.05B | 9.10% | | $186.2M | $112.8M |

## 5. Perp-venue fees and LP vaults

Fees $1.88B/yr (trailing 365 days $1.83B), revenue $1.32B, supply side $465.8M.

| venue | fees | revenue | supply side | source |
|---|---:|---:|---:|---|
| Hyperliquid Perps | $1.05B | $859.5M | $194.2M | reported |
| Jupiter Perpetual Exchange | $102.1M | $25.5M | $76.6M | reported |
| tradeXYZ | $72.2M | $23.9M | $48.3M | reported |
| Aster Perps | $65.3M | - | - | missing |
| GMX Solana | $53.4M | $13.4M | $40.1M | reported |
| Pacifica Perps | $45.9M | $45.5M | $0.4M | reported |
| edgeX V2 | $45.9M | $33.2M | $12.7M | reported |
| Lighter Perps | $43.1M | $32.9M | $10.2M | reported |
| AZverse Perps | $36.2M | $35.0M | $1.2M | reported |
| Antarctic | $32.7M | $13.1M | $19.6M | reported |
| Lighter Robinhood Perps | $25.8M | $23.5M | $2.2M | reported |
| Nado Perps | $21.0M | $10.6M | $10.4M | reported |

| LP vault | fee income | TVL | fee APR | above SSR | used |
|---|---:|---:|---:|---:|---|
| Jupiter Perpetual Exchange | $76.6M | $772.9M | 9.91% | $47.2M | yes |
| GMX Solana | $40.1M | $27.8M | 143.95% | $39.0M | fee APR over 100%: TVL or fees mis-measured |
| Antarctic | $19.6M | $8.8M | 223.56% | $19.3M | TVL under $20M |
| Nado Perps | $10.4M | - | - | - | no TVL |
| Lighter Perps | $10.2M | - | - | - | no TVL |
| GMX V2 Perps | $9.0M | $211.1M | 4.24% | $0.9M | yes |
| Hyperliquid HLP | $6.7M | $180.8M | 3.69% | $-0.2M | yes |
| Veranta | $6.1M | $11.3M | 53.84% | $5.7M | TVL under $20M |
| Gains Network | $2.4M | $8.5M | 28.05% | $2.1M | TVL under $20M |
| Apex Omni | $2.4M | $31.1M | 7.61% | $1.2M | yes |
| Lighter Robinhood Perps | $2.2M | $111.6M | 1.98% | $-2.0M | yes |
| Sudo Perps | $2.2M | $0.9M | 249.78% | $2.2M | TVL under $20M |
| Ostium | $1.5M | $4.3M | 33.90% | $1.3M | TVL under $20M |
| Arcus Perps | $1.3M | $50.9M | 2.54% | $-0.6M | yes |

HLP (vaultDetails): account value $180.9M, last-month PnL $0.6M, $7.4M a year (4.03% APR).

## 6. Incentive budgets

Headline $353.5M/yr on $9.67B of rewarded TVL (3.66% mean reward APR); stable $246.3M, volatile $107.2M. Excluded: pass-through $46.2M, outlier-flagged $2.17B, over 300% APR $0.8M. Merkl live campaigns: $267.0M/yr (851 opportunities). Union with Merkl $468.4M.

| by chain | $/yr |
|---|---:|
| Ethereum | $200.2M |
| Base | $60.9M |
| Robinhood Chain | $35.8M |
| Tron | $17.6M |
| Monad | $10.2M |
| Sui | $4.3M |
| OP Mainnet | $3.9M |
| Avalanche | $3.3M |
| Solana | $3.2M |
| Tempo | $2.3M |

| by project | $/yr |
|---|---:|
| morpho-blue | $126.3M |
| sky-lending | $53.8M |
| usual-usd0 | $30.1M |
| sparklend | $24.7M |
| aerodrome-v1 | $24.5M |
| curve-dex | $20.1M |
| justlend-v1 | $17.6M |
| aave-v3 | $11.1M |
| dolomite | $5.6M |
| velodrome-v2 | $3.3M |
| aave-v4 | $2.6M |
| aerodrome-slipstream | $2.6M |

| Merkl protocol | Merkl $/yr | DefiLlama $/yr |
|---|---:|---:|
| morpho | $139.3M | $126.3M |
| aave | $83.1M | $13.7M |
| dolomite | $8.1M | $5.6M |
| euler | $5.0M | $1.1M |
| ? | $4.2M | $0.0M |
| 1inch | $4.1M | $0.0M |
| uniswap | $3.2M | $0.2M |
| curvance | $2.2M | $0.3M |
| upshift | $1.6M | $0.0M |
| accountable | $1.3M | $1.2M |

| largest Merkl campaigns | action | TVL | APR | budget $/yr |
|---|---|---:|---:|---:|
| Lend USDe on Aave (looping required) (aave, Plasma) | LEND | $588.3M | 4.75% | $26.4M |
| Deposit USDe as collateral on USDe/USDC 91.5% (morpho, Base) | LEND | $394.0M | 4.75% | $18.7M |
| [Robinhood Users Only] Supply to Steakhouse USDG V2 vault on Morpho (morpho, Robinhood Chain) | LEND | $529.6M | 3.41% | $18.0M |
| Supply to Sentora RLUSD Main V2 vault on Morpho on Ethereum (morpho, Ethereum) | LEND | $458.1M | 3.79% | $17.4M |
| Deposit USDe as collateral on USDe/USDG 91.5% (morpho, Robinhood Chain) | LEND | $358.6M | 4.75% | $17.0M |
| Supply to Paypal USD Main V2 vault on Morpho on Ethereum (morpho, Ethereum) | LEND | $414.1M | 3.60% | $14.9M |
| Lend USDe on Aave (looping required) (aave, Ethereum) | LEND | $323.8M | 4.75% | $14.6M |
| Supply to Steakhouse High Yield USDC Edition V2 vault on Morpho from C (morpho, Base) | LEND | $461.8M | 2.69% | $12.1M |
| Lend USDT0 on Aave (aave, Plasma) | LEND | $779.8M | 1.07% | $8.4M |
| Supply USDC on USDe/USDC 91.5% (morpho, Base) | LEND | $390.9M | 2.00% | $7.8M |

## 7. DEX LP fees and LVR

Fees $5.19B/yr, supply side $4.36B (trailing 365 days at the same share $2.49B), protocol revenue $825.9M.

| DEX | fees | supply side | trailing 365d fees |
|---|---:|---:|---:|
| PumpSwap | $1.43B | $1.24B | $706.8M |
| Uniswap V4 | $1.10B | $1.10B | $428.9M |
| Meteora DLMM | $623.6M | $559.7M | $252.8M |
| Uniswap V3 | $572.1M | $433.0M | $482.2M |
| Raydium AMM | $359.4M | $303.9M | $144.7M |
| PancakeSwap AMM V3 | $142.4M | $96.4M | $141.1M |
| Orca DEX | $125.0M | $108.8M | $69.7M |
| Aerodrome Slipstream | $118.7M | $40.7M | $105.9M |
| Fables | $61.6M | $61.6M | $5.4M |
| Meteora DAMM V2 | $61.4M | $49.6M | $163.4M |
| Uniswap V2 | $60.2M | $60.2M | $54.2M |
| PancakeSwap AMM | $48.5M | $32.9M | $62.4M |

LVR on the 40 largest volatile major-pair pools (TVL $1.05B): fees $91.9M/yr; LVR $28.9M (full range) to $92.9M (4x range); LPs keep 68.59% to -1.13% of fees. Volatility (90 days): AVAX/USD 78%, BNB/USD 35%, BTC/ETH 26%, BTC/USD 38%, ETH/USD 53%, HYPE/USD 55%, SOL/USD 56%.

| pair | TVL | fees $/yr | LVR full range $/yr |
|---|---:|---:|---:|
| ETH/USD | $628.4M | $65.0M | $21.9M |
| BTC/ETH | $213.4M | $11.0M | $1.8M |
| BTC/USD | $136.0M | $4.3M | $2.5M |
| SOL/USD | $53.6M | $9.7M | $2.1M |
| HYPE/USD | $14.0M | $1.9M | $0.5M |

## 8. Lending

DefiLlama Lending + CDP: fees $1.66B/yr (trailing 365 days $1.95B), supply side $1.35B, revenue $316.2M.

| source | class | borrowed | interest $/yr | mean APR | above fair (clipped) |
|---|---|---:|---:|---:|---:|
| aave | btc | $96.4M | $0.4M | 0.42% | $0.4M |
| aave | eth | $4.90B | $93.8M | 1.92% | $0.0M |
| aave | other | $83.7M | $2.1M | 2.55% | $2.1M |
| aave | stable | $7.15B | $332.1M | 4.64% | $61.1M |
| morpho | btc | $9.4M | $0.2M | 2.59% | $0.2M |
| morpho | eth | $176.0M | $4.0M | 2.25% | $0.7M |
| morpho | other | $65.8M | $1.8M | 2.80% | $1.8M |
| morpho | stable | $5.42B | $258.3M | 4.77% | $62.9M |

## 9. Queues

| asset | unit | wait (median days) | window | sell $/yr | gross rent $/yr | above fair $/yr | last 13 weeks gross |
|---|---|---:|---:|---:|---:|---:|---:|
| etherfi | ETH | 1.00 | 210d | $1.59B | $1.8M | $1.6M | $0.1M |
| frax | USD | 0.00 | 210d | $50.0M | $-0.0M | $0.0M | $0.0M |
| kelp | ETH | 12.04 | 210d | $36.0M | $0.1M | $0.0M | $0.1M |
| lido | ETH | 1.00 | 210d | $3.79B | $5.2M | $4.6M | $0.7M |
| maple_usdc | USD | 0.00 | 210d | $67.9M | $0.0M | $0.0M | $0.0M |
| maple_usdt | USD | 0.00 | 210d | $13.4M | $0.0M | $0.0M | $0.0M |
| renzo | ETH | 14.00 | 210d | $23.3M | $0.0M | $0.0M | $0.0M |
| rocketpool | ETH | 0.00 | 210d | $194.1M | $0.3M | $0.3M | $0.4M |
| sky | USD | 0.00 | 210d | $3.41B | $-0.1M | $0.0M | $-0.1M |
| susde | USD | 1.00 | 210d | $1.37B | $0.5M | $0.2M | $-0.0M |
| usde | USD | 0.00 | 210d | $3.15B | $1.0M | $0.7M | $-0.1M |
| lbtc | BTC | 9.00 | 743d | $482.4M | $0.4M | $0.4M | - |
| tbtc | BTC | 0.20 | 743d | $1.32B | $0.9M | $0.8M | - |
| oeth | ETH | 0.01 | 743d | $69.6M | $0.0M | $0.0M | - |

Combined queue book (queue_book): $0.4M/yr out of sample at $15M; unbounded capital would have locked $915.2M at the peak (2025-08-30T00:00:00Z); 1h-late entry keeps 95.74%. Off-Ethereum LSTs: $5.0M a day of native-pair volume (gross band $0.5M to $2.3M).

## 10. Points: Pendle YT premium

85 markets, YT outstanding $985.8M, premium $43.2M/yr net (4.38% on notional), $45.8M positive-only; with trailing 7d realised $43.9M.

| market | expiry | YT notional | implied | realised 30d | premium $/yr | points |
|---|---|---:|---:|---:|---:|---|
| reUSD | 2026-12-10 | $232.9M | 11.86% | 7.04% | $11.2M | False |
| USDai | 2026-10-15 | $58.1M | 12.86% | 0.00% | $7.5M | None |
| STRCx | 2026-11-26 | $33.9M | 24.56% | 12.05% | $4.2M | True |
| USD3 | 2026-12-17 | $46.0M | 15.13% | 6.70% | $3.9M | False |
| sUSDai | 2026-10-15 | $54.9M | 13.35% | 7.28% | $3.3M | None |
| USDat | 2027-01-14 | $52.6M | 9.03% | 3.00% | $3.2M | True |
| apxUSD | 2026-11-05 | $16.9M | 13.86% | 0.00% | $2.3M | True |
| USDat | 2027-01-14 | $27.0M | 8.41% | 3.00% | $1.5M | True |
| apyUSD | 2026-11-05 | $54.1M | 16.16% | 13.64% | $1.4M | True |
| sUSDat | 2027-01-14 | $5.6M | 13.97% | 36.42% | $-1.3M | True |
| sUSDS | 2026-11-26 | $86.1M | 5.01% | 3.60% | $1.2M | False |
| SIERRA | 2026-10-22 | $25.2M | 9.74% | 5.20% | $1.1M | True |

## 11. For scale only

| pool | fees $/yr | trailing 365d |
|---|---:|---:|
| scale_stable | $9.32B | $8.72B |
| scale_staking | $2.54B | $2.11B |
| scale_chain | $1.43B | $1.28B |
| scale_rwa | $878.4M | $679.3M |
| scale_mev | $366.7M | $457.6M |
| entertainment | $6.65B | $3.12B |

Stablecoin supply $312.01B; Ethena: USDe $4.78B, fees $276.3M/yr (6.07% of the longs-paid funding on the four venues, $4.55B).

## 12. Checks

- Hyperliquid funding, two paths over 2026-09-08T11:33:30Z to 2026-10-09T19:00:00Z (31.3 days, 178 main-dex coins): realised (OI interpolated across four snapshots x every settled hour) $1.18B/yr vs current OI x the same hours $1.30B/yr, ratio 0.902.
- Hyperliquid OI: venue $12.03B vs DefiLlama $7.71B on the main dex (ratio 0.64); tradeXYZ $3.57B vs $3.58B (ratio 1.001).
- Aave: own API (borrowed x APR now) $428.4M/yr vs DefiLlama aave-v3 fees (30 days) $450.9M/yr, ratio 1.053; Ethereum $329.2M vs $364.2M, ratio 1.106.
- Incentives: Merkl own API $267.0M/yr vs DefiLlama headline $353.5M/yr (Morpho $139.3M vs $126.3M; Aave $83.1M vs $13.7M).
- Hyperliquid fees: DefiLlama $2.4M a day (7-day mean) on the venue's own $3.01B of 24h volume = 8.0 bp (expected 2-12 bp).

## 13. Double-count guards

- dex_supply_side_excludes_voters_and_protocol: true
- duplicate_slugs: []
- ethena_not_in_total: true
- funding_not_in_defillama_fees: "order-book funding is peer to peer and absent from venue fees; GMX/Jupiter borrow fees are in fees and not in funding"
- incentives_exclude_outliers_yr: 2170107134.837563
- incentives_exclude_pass_through_yr: 46177459.76331792
- merkl_used_as_check_only: true
- one_pool_per_protocol: true
- pendle_only_in_points: true
- protocols_by_pool: {"None": 236, "attention": 168, "collector": 13, "dex_lp": 544, "entertainment": 326, "lending": 162, "perp_vaults": 248, "points": 2, "scale_chain": 169, "scale_mev": 9, "scale_rwa": 46, "scale_stable": 7, "scale_staking": 126}
- queue_above_fair_net_of_pool_fee: true
- roll_markets_excluded_from_rent_yr: 39699595.102146864

## 14. API gaps

- yields.llama.fi/poolsBorrow (borrow totals and rates per pool): HTTP 402, paid plan; borrow-side split taken from the Aave and Morpho APIs instead
- api.llama.fi/overview/derivatives (perp volume): HTTP 402, paid; the HL fee check uses the venue's own 24h volume
- dailyBribesRevenue: the free overview returns no protocols and the Aerodrome/Velodrome summaries carry no chart; ve(3,3) bribes unsized
- DefiLlama open interest for 'Hyperliquid Perps' reads 0.64 of the venue's own contexts on the main dex (1.00 on tradeXYZ); the venue's numbers are used
- liquidation penalties: no free per-protocol series; unsized (and a racing pool, excluded from the strategy space)
- Ethena hedge composition (which venues hold its shorts): not read; Ethena enters only as the collector of its DefiLlama fees
- Hyperliquid open-interest history: not served by the API; four stored snapshots (09-08, 09-10, 10-09, 10-10) interpolate path B
- Pendle YT supply: active markets of the 2026-10-10 00:02 list only; markets listed later are missing
- perp venues beyond HL, Binance, Bybit and OKX (Bitget, Gate, MEXC, Deribit, Aster, Lighter, edgeX): funding unsized
- tokenized gold supply (PAXG, XAUT): not in DefiLlama TVL or stablecoins; the spot leg depth is untested
