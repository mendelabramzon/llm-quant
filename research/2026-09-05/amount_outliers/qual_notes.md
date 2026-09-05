# Qualitative notes for the amount-outlier packets

Written by the LLM after reading `packets.json`, `prices.json`, `stats.json`, `context.json`, per-transaction `show` output, and `cycling_check.json`. Each entry is keyed by transaction hash. Exact figures are copied from packet facts, decoded events and stats; anything derived (sums, ratios, differences, multiples) is approximate and marked as such. Contract identities that rest on model memory rather than an onchain check are listed under `unverified`.

## synthesis
A $10,000 threshold selects very different populations on the five chains: 82 of 2,742 Ethereum user transactions, 661 of 8,147 on Base, 292 of 1,569 on Optimism, 17 of 1,512 on Arbitrum and 8 of 9,056 on Polygon. Prices pinned at the sample end were $2,457.97 for ETH (2.5 basis points under the in-sample swap median, approx), $79,706 for BTC, $0.0944 for POL, $0.132 for ARB and $0.101 for OP, so the largest token-denominated transfers on the L2s are modest in dollars: 2.04 million ARB is $270k (#28) and 198,010 POL is $18.7k (#38).

Emission farming by per-block liquidity cycling. On Base and Optimism the population above the threshold is mostly a handful of bots that mint a 1 percent concentrated-liquidity position at the end of a block, stake it in the pool's gauge, and burn it at the start of the next block. Base: helper 0x9eef…eb79 cycles 1,024,025 USDC plus 356.6 WETH in the Aerodrome USDC/WETH pool 57 times in 60 blocks (#12, #13) and nets −$1,313 USDC on $116.7M through; helper 0x2192…20db, driven by three rotating EOAs, cycles $660k USDC plus 230 WETH in the same pool and $211k in the cbBTC/USDC pool (#19, #20), netting −$23,813 USDC on $83.4M and 0.00 cbBTC on $21.1M. Optimism: three systems work the Velodrome USDC/WETH pool 0x4789…ba25, the pool the pilot memo had already selected: 0xc26a…37e9 with a $248k position (#29, #30, #33), 0xf1b4…7c76 through four EOAs paying out to two treasury addresses (#31), and 0x343c…320f through three EOAs moving exactly 30,000 USDC plus 10.54 WETH twice in every one of the 60 blocks; all three net $0.00 on $6.1M, $3.5M and $7.2M through. Withdrawals land at block index 2 to 7 and re-deposits near the end, at index 17 to 167. The reason is timing: gauge rewards accrue by elapsed time, and time only passes between blocks, so a position staked across the boundary and absent during the block collects the emissions while never being available to a swapper. `cycling_check.json` tests this on the 30-minute pool histories the pilot saved: in the Optimism pool 1,948 cycler mints and 1,948 burns occur in 891 of 900 blocks, burns at a median index of 3 and mints at 25, and only 3 of 40 swaps (16 percent of token0 volume) executed while any cycler liquidity was present; in the Base USDC/WETH pool, 763 mints and 765 burns, indices 7 and 152, and 4 of 183 swaps (0.7 percent of volume); in the cbBTC/USDC pool 3 of 38 swaps. When present, cyclers were about 34 to 37 percent of in-range liquidity. At least 454 of Base's 661 and 251 of Optimism's 292 large transactions belong to these operators (approx, from the repeated-pattern census). Two consequences for research: pool liquidity read at a block boundary, which is what a pinned `eth_call` returns, overstates executable depth by an order of magnitude in these pools, and gauge emissions here pay for liquidity that no trade can use.

Ethereum is stablecoin and exchange flow. USDT is the asset of the largest position in 33 of 82 transactions and $9.5M of their sum; the biggest movements are a 4,000,000 USDT Aave V3 repayment (#10), a 3,000,000 USDT deposit into a hot wallet that also took in $84k of LINK while sending 20 transactions (#11), 999,985 USDT from a wallet on its second transaction (#4), and 786,000 USDS converted to USDC at par through the Sky PSM in seven legs (#6). Every large native transfer is exchange plumbing: withdrawals from wallets with nonces 793,355 (#2) and 15,190,919 (#9), and a 57.28 ETH wrap by a nonce-747,930 wallet (#5). The one control that is not plumbing is a contract that bought $144k of UNI net while selling WETH, WBTC, AAVE and USDC, at index 0 with a zero tip (#1).

Gross volume is a flash-loan detector and nothing else. Two Morpho flash loans of 9,826 WETH ($24.2M, #3) and 1,000 WETH ($2.5M, #8) backed trades whose legs were $49 to $222 and about $41 of profit; the lender's WETH nets 0.00 on $53.2M through. The position-change metric scored both near zero, which is right, and routed swaps inflate gross by 7 to 16 times (#6, #34, #42). Gross volume should be reported net of same-asset borrow-and-repay pairs.

Arbitrum and Polygon populations are small and made of plain transfers into consolidation or hot-wallet addresses: 0xb38e…891d received 2.04M ARB and nets +$359k ARB while sending 26 transactions (#28); 0xe780…e245 nets +$122k USDT and +$20.5k POL from several senders (#38, #41); 0x1347…74ec collects USDC and POL from three wallets (#37, #39); two EOAs empty 20.6 and 15.3 ETH into one address in one block (#21, #22); and a 209-byte forwarder at the same address on both chains, 0xee7a…4055, receives USDC on Arbitrum (+$73.8k net, #27) and on Polygon (+$24.7k, #40). Two of the 42 packets have an EIP-7702 delegated account on the large end of a stablecoin transfer (#7, #25). The Polymarket control (#35) shows the exchange's collateral vault paying USDC.e into ConditionalTokens as fills are settled by splitting positions; over the window the vault nets −$83.8k and ConditionalTokens +$54.7k, a net-opening reading.

Unpriced tokens carry a data-quality finding. The most transferred unpriced tokens on Ethereum are '꒤SDT' (107 transfers), a second 'USDT' at a different address (53) and '꒤SDC' (52); on Arbitrum 'ÚSDС' with a Cyrillic letter (170) and 'E.ꓔ.H?' (28). These are address-poisoning transfers, and a symbol-keyed price table would have valued them as dollars; the address-keyed registry ignored them. On Optimism three 'www.toks.mom' tokens account for 7,097 of 9,197 ERC-20 transfer logs, which is why only 18 percent of Optimism's transfer legs were priced. On Base 'WHUF' and 'LJT' have 1,003 and 1,002 transfers each, the count signature of an airdrop script.

Hypotheses for the quant step, each falsifiable on a longer sample. (1) Ghost liquidity: in Slipstream pools with cyclers, the share of swap volume executed against cycler liquidity stays under 10 percent, the cyclers earn emissions in proportion to liquidity and swap fees near zero, and any depth feature computed from block-end state overstates executable depth by the cyclers' share; the 30-minute check already agrees, and the pool histories can be extended. (2) Exchange flow: hot wallets identified by nonce, destination count and flat tip show net stablecoin inflow that is dominated by a few transfers at two minutes; over hours the sign of net inflow is the tradable quantity, to be tested against subsequent price. (3) Flash-loan volume: gross transfer volume with and without Morpho and Balancer borrow-repay pairs differs mainly on thin V4 pools such as the ELA pools, so an activity feature must exclude it or it measures bot configuration. (4) Poisoning transfers have dust amounts and recipients that received a real transfer of the imitated token minutes earlier; that overlap is a cheap wallet-risk feature.

## feedback
1. Window-level netting per (address, asset) was added to stats and packets during this pass and was what separated cycling from flow; extend it to sender clusters by grouping rotating EOAs on their destination contract and payout address (0x2192…20db has three senders, 0x343c…320f three, 0xf1b4…7c76 four).
2. Deduplicate selection by destination contract and sender cluster rather than by (selector, asset, rounded amount): one Optimism operator took three ranked slots (#29, #30, #33) while 0x343c…320f (120 transactions) got none and the Base multi-pool manager (61 transactions) two.
3. Detect EIP-7702 delegation designators: code of 23 bytes beginning 0xef0100; report the delegate address and count delegated accounts among counterparties (#7, #25).
4. Match counterparties across chains: 0xee7a…4055 holds code on Arbitrum and Polygon; cbBTC shares its address on Ethereum and Base by design.
5. Register the signatures recognised this pass so the next iteration decodes them: Morpho FlashLoan 0xc76f1b4f…; Sky DSNote-style topics (the selector padded to 32 bytes) from the Vat, DaiJoin and UsdsJoin; LitePSM BuyGem 0x085d06ec…; Slipstream gauge Deposit, Withdraw and ClaimRewards 0xf8e1a15a…, 0x40d0efd1…, 0x3067048b…, 0x26f6a048…; position-manager events 0x1c8ab8c7…, 0x1f89f963…, 0x8903a5b5…; the aggregator record events 0x77243948… and 0x7970b074… that accompany selector 0x0c307f76 on Ethereum, Base and Polygon; Bancor-style TokensTraded 0x5c02c2bb…; the Arbitrum payout receipt 0x6f7c6475…; the CTF v2 exchange event 0x55bb3cad…; Polygon's native LogTransfer 0xe6497e3e… from the 0x…1010 system contract.
6. Add a hot-wallet feature: nonce, distinct destinations in the window, tip variance, and window net by asset; candidates here are 0xdfd5…963d, 0x6872…f7de, 0x28c6…1d60, 0x07ae…0e67, 0x0d07…92fe, 0xb38e…891d and 0xe780…e245.
7. Price more assets: AERO and VELO (the cyclers' reward), cbXRP, EURC (needs a EUR feed), LGNS, pUSD; where no feed exists derive a price from in-sample V2 and V3 swaps against WETH or a stablecoin, which the swap decoder already exposes.
8. Add a confusable-symbol check for unpriced tokens (Unicode normalisation against registry symbols) with dust-amount and recipient-overlap statistics.
9. Report gross volume net of same-asset borrow-repay pairs inside a transaction and a separate `flash_loan_usd` fact.
10. Next bounded queries: a trace of #3 to learn whether the 9,826 WETH balance is used for anything; code and `rewardRate` lookups on the gauges 0xf33a…96b5 and 0xa751…2712 to price the emission capture per cycle; code lookups for the PSM wrapper 0x6a00…1068 and 0x006d…b000; the pUSD contract 0xc011…2dfb and vault 0xc417…9db1, touched by 1,867 transactions in two minutes.

## ethereum 0x6854a8e079bb83aa2d3c855478539eec7ce3dbb44607245d3ab80eba30012bd6
mechanism: contract buys 14,327 UNI with 36.85 WETH in the Uniswap V3 UNI/WETH pool at index 0, one of five large UNI purchases by the same contract in the window
confidence: medium
unverified: 0x1d42…8d801 as the Uniswap V3 UNI/WETH 0.3 percent pool and the role of the buying contract (a settlement or market-making contract) are model memory.
The 20,805-byte contract 0x51c7…2a7f, called by an EOA with nonce 71,276 and no priority fee, takes 14,327.33 UNI ($90,205 at the feed) from pool 0x1d42… and pays 36.849539 WETH ($90,575), a fill about 0.4 percent above the feed (approx). Index 0 of a 453-transaction block with a zero tip means private order flow or a builder placement. Over the window the same contract bought +$144,097 of UNI net and sold −$105,225 of WETH, plus WBTC, AAVE, USDC and USDT; 22 transactions touched it, five above the threshold. One actor rotating several assets into UNI, not a retail trade: a market maker rebalancing inventory or a settlement contract filling a large UNI order piecewise.

## ethereum 0xcee708511d08852f7c5489ad09793644921e67db31e9586b63ff3123e9a99487
mechanism: exchange-style hot wallet withdrawing 41.2 ETH to an EOA that forwards part of it within the window
confidence: medium
unverified: which exchange; the label rests on nonce and behaviour.
A legacy transaction of 41.199656 ETH ($101,268) from an EOA with nonce 793,355 to an EOA. The sender made 10 transactions in the window to 8 destinations, two above the threshold, and nets −$99,909 ETH plus small USDT and USDC legs: a withdrawal hot wallet. The recipient nets +$92,768 ETH on $109,767 through, so it sent about 7 ETH onward within the two minutes (approx). Tip 0.08 gwei, no urgency.

## ethereum 0x5b6b354951c145149d346fae74c33d3377aa17ff3ccc584024457c9236aaffd7
mechanism: Morpho flash loan of 9,826 WETH ($24.2M) backing a micro-arbitrage across Bancor-style, Uniswap V3, V4 and V2 pools for UNI and BNT
confidence: high
unverified: 0xbbbb…ffcb as Morpho Blue and topic 0xc76f1b4f… as its FlashLoan event; 0xde1b…83e4 and 0xeef4…d4fb as Bancor v3 contracts; 0x1f57…ff1c as BNT are model memory. Why the loan is 100,000 times the trade size is not explained by the receipt.
The bot contract 0xd226…9f89 (sender nonce 41,453, selector 0x99999999, 1,862 bytes of packed route data, zero tip) receives 9,826.171218 WETH from 0xbbbb… at log 325 and returns exactly the same amount at log 369; its WETH nets 0.00 on $48.3M through. In between it unwraps 0.03 and 0.02 WETH, trades 230.16 BNT and 11.68 UNI through the Bancor-style contracts, sells 11.68, 7.79 and 7.78 UNI in V3 pool 0xfaa3… for 0.0300, 0.0200 and 0.0200 WETH, buys 7.78 UNI for 49.16 USDT in a V4 pool and 7.78 UNI for 0.02 WETH in V2 pool 0x9d40…, and takes the 49.16 USDT out of the V3 WETH/USDT pool. Every leg is between $49 and $222; the largest single position change is −$222 of WETH at pool 0xfaa3…. Morpho charges nothing for the loan, so either the route encoder always borrows a fixed maximum or the balance is used to move a Bancor trading-liquidity checkpoint; a trace would show which. Gross volume is the only metric that finds this transaction, and it says nothing about economic size.

## ethereum 0x07ee2cd4a8b935d56d7f422fd9ad02557e87468889c2f90c029c83868e748b82
mechanism: 999,985 USDT sent from a wallet on its second transaction to an untouched EOA
confidence: medium
unverified: whether either side is an exchange or custodian.
A legacy transaction (nonce 1) moving 999,985.003115 USDT ($1,000,029) to 0x5f8e…, which has no other activity in the window; the sender has one transaction. The odd cents suggest a full-balance sweep after a fee rather than a round transfer. Fresh wallet, single hop, one million: the shape of an exchange withdrawal into a new custody address or one leg of an OTC settlement. Tip 0.04 gwei.

## ethereum 0x6b0a5908e135ce92133765b553b39346a9c1360763c56a9cd3a13eadfe4845e1
mechanism: high-nonce wallet wrapping 57.28 ETH into WETH
confidence: high
unverified: operator identity.
deposit() on WETH with 57.281915 ETH ($140,797) from an EOA with nonce 747,930, three transactions in the window of which one failed, tip 0.00001 gwei. The wallet's window net is −$140,799 ETH and +$140,797 WETH: an inventory conversion by an automated trader that needs ERC-20 ETH for pools or a bridge. No transfer of the WETH follows in the window.

## ethereum 0x1db694feffa59e7101e99e3e37d233220ef9b727a948875e1af44a21756976a1
mechanism: 786,000 USDS converted to 786,000 USDC at par through the Sky PSM path: USDS burned, DAI minted, USDC drawn from the LitePSM pocket, zero fee
confidence: high
unverified: 0x6a00…1068 as the USDS PSM wrapper, 0x006d…b000 as its entry router, 0xa188…f98c as the DaiUsds converter, 0x35d1…492b as the Vat, 0x9759…1a28 as DaiJoin, 0x3c0f…7feb as UsdsJoin, 0xf6e7…3042 as the LitePSM and 0x3730…7341 as its USDC pocket are model memory; the selector-padded DSNote topics and the BuyGem-shaped event with fee 0 match that memory.
The EOA (nonce 1,521, tip 0.0057 gwei) sends 786,000 USDS to 0x006d…, which passes it to 0xa188…; 786,000 USDS is burned to the zero address, 786,000 DAI is minted from the zero address to 0xa188… and forwarded to 0xf6e7…; the pocket 0x3730… then sends 786,000 USDC to 0x6a00…, which delivers it to the EOA. The sender ends −786,000 USDS and +786,000 USDC ($785,889 at the USDC feed) for a fee of 0.000016 ETH; the PSM event carries fee 0. Gross volume is 7 times the economic size because the same 786,000 crosses seven legs. This is the largest non-USDT stablecoin operation on Ethereum in the window: an exit from the Sky system into USDC at par, and a reminder that a zero-fee PSM makes USDS-to-USDC a free trade at size.

## ethereum 0x719ec3131efad55ef2d8835e95554eeee8bf670ed0f5a05b37d83b4673f926e4
mechanism: sponsored ERC-7821 batch execution on an EIP-7702 delegated account sending 17,700 USDC
confidence: high
unverified: the relayer's identity and the delegate implementation behind the 23-byte code.
The transaction sender 0x77bd…5900 (nonce 46,195, tip 0.00013 gwei) calls execute(bytes32,bytes) on 0x240c…d2ff, whose code is 23 bytes, the size of an EIP-7702 delegation designator. The mode word ending in 7821 0001 marks an ERC-7821 batch with signed opData, and the single call is USDC.transfer(0x0344…, 17,700.082168). A delegated EOA moved $17,698 without paying gas, through a relayer; the counterparty is an EOA with one touch. In receipts the economic actor is the `to` address, not the sender, and the largest-position logic attributed the flow to the right party.

## ethereum 0x3a9fdfc182bdb7a6f1ba6925666ed1d80f193b698c117a9296d5987ea648c53e
mechanism: 1,000 WETH Morpho flash loan for a two-pool ELA arbitrage worth about 0.017 ETH
confidence: high
unverified: Morpho identity as in #3; ELA as the second currency of the two V4 pools is carried over from the gas notes and is model memory; the V4 Swap sign convention (deltas from the swapper's side) is from memory.
Index 1 of block 25,910,251, zero tip. 0xbbbb… lends 1,000 WETH at log 5 and receives 1,000 WETH back at log 9. Between them, two V4 swaps: in pool 0xe5be… the bot pays 0.014531 of currency0 and receives 166.77 of currency1; in pool 0x76a0… it pays the same 166.77 and receives 0.031098 of currency0. The difference of about 0.0166 ETH, roughly $41 (approx), is wrapped as 0.016567 WETH and unwrapped again; the fee was 0.000066 ETH. Pool 0xe5be… is the ELA pool the gas-outlier fleet arbitraged (gas notes #4), so at least two independent bots, 0x99e6…3b80 here and 0xce8b…528b there, work the same thin V4 pools. The bot's WETH nets 0.00 on $4.9M through: a $2.5M loan for $41, because the loan size is a constant, not a need.

## ethereum 0x03c508303a341ca53ee7905d48d63f1ee0eaf3f2238a5b2e9e6cc5ebbc2d4ad7
mechanism: exchange hot wallet with nonce 15.19 million withdrawing 69.8 ETH
confidence: medium
unverified: 0xdfd5…963d as a Binance hot wallet is model memory.
69.804916 ETH ($171,578) to an EOA at a flat 1.0 gwei tip; the sender's nonce is 15,190,919, it made 11 transactions in the window to 6 destinations with the next one at index 29 of the same block, and its window net is −$171,979 ETH. Fixed tip, sequential nonces, many destinations: a withdrawal queue. The recipient has no other activity. The largest native transfer on any chain in the window is routine exchange plumbing.

## ethereum 0x61d078ac534d6dcd296d556248f1a54d58ba1d1f6aaac94c7a8654d71a78015e
mechanism: 4,000,000 USDT repayment of an Aave V3 variable-rate borrow
confidence: high
unverified: 0x8787…4fa4e2 as the Aave V3 Pool and 0x2387…086a as aEthUSDT are model memory; the debt token's symbol variableDebtEthUSDT is self-reported on chain.
repay(asset=USDT, amount 4,000,000.0001) from an EOA with nonce 64 at a 0.15 gwei tip. 3,999,988.825595 units of the variable debt token are burned to the zero address and 4,000,000.0001 USDT move to the aToken contract; an AaveRepay-shaped event closes the sequence. The 11.17 USDT gap between the two figures is interest-index rounding, not a fee (approx). Fee $0.08 for a $4M deleveraging. A low-nonce EOA carrying a $4M USDT borrow is a treasury or fund. The aToken contract's window net is +$4,093,180 USDT, so about 93k more USDT was repaid or supplied in the same two minutes (approx).

## ethereum 0xdf8ec771f632686012e3d717c0b3b294fa63356e5afb126c301c2fd9e988bebf
mechanism: 3,000,000 USDT deposit into an exchange hot wallet
confidence: medium
unverified: 0x28c6…1d60 as a Binance hot wallet is model memory; the behaviour is from the packet and stats.
A plain transfer of 3,000,000.0021 USDT ($3,000,132) from an EOA with nonce 886 at a 0.2 gwei tip. The recipient is the busiest large-value address on Ethereum in the window: touched by 35 transactions, six above the threshold, sender of 20; its window net is +$3,077,894 USDT, +$83,938 LINK and −$4,580 ETH. Deposits in, withdrawals out, one address: an exchange hot wallet. The extra 0.0021 USDT looks like a dust marker or fee remainder (approx).

## base 0xdd9809d45d3ceadc036f1ab21380dc899eea3e2229e271eca65bea04542359e2
mechanism: per-block emission farming: a 1 percent USDC/WETH position of 1,024,025 USDC plus 356.6 WETH minted at the end of the block and staked, to be burned at the start of the next
confidence: high
unverified: pool 0xb2cc…dc59 as an Aerodrome Slipstream USDC/WETH pool (a clone of 0xec8e…5342, by memory the Slipstream pool implementation), 0x8279…5b72 as the Slipstream position manager, 0xf33a…96b5 as its gauge and AERO as the reward token are model memory; the event shapes match.
Helper 0x9eef…eb79 (1,383 bytes), called by 0x3565…9dc9 (nonce 360,898; 114 transactions in the window, all to this helper), sends 356.618774 WETH ($876,559) and 1,024,024.776358 USDC ($1,023,881) into the pool and mints liquidity 7,676,991,415,352,672,456 in ticks [−198300, −198200], about 2,451 to 2,476 USDC per WETH (approx), a 1 percent band around the price; the position NFT is deposited in the gauge. The mint lands at index 167 of 172, the last user transaction of the block; its twin #13 burns it at index 6 of the next block, and the pair repeats 57 times in 60 blocks. Over the window the helper nets −$1,313 USDC and +$6 WETH on $116.7M and $99.9M through. Gauge rewards accrue by elapsed time and time passes only between blocks, so a position staked across the boundary and absent during the block collects emissions without ever quoting a price to a swapper. `cycling_check.json` over this pool's 30-minute history: 763 cycler mints and 765 burns, burns at median index 7 and mints at 152, and only 4 of 183 swaps (0.7 percent of token0 volume) executed while cycler liquidity was in the pool, when it was 36 percent of in-range liquidity.

## base 0x38b025b2b832211856bc40afaffb410dfa55e493ac2cdba54c6b575d4b4ff960
mechanism: the burn half of #12 at index 6 of the next block, with 0.433 AERO claimed
confidence: high
unverified: as #12.
Same sender, next nonce, tip 0.006 gwei (paid to be early; the mint pays none). A zero-liquidity burn and a collect return 356.618774 WETH and 1,024,024.776358 USDC to the helper, NFT 76,432,899 comes back from the gauge, and the gauge pays 0.433445 AERO (unpriced). The re-mint follows at index 131 of the same block. Per two-second cycle the operator collects a fraction of an AERO on a $1.9M position for about $0.02 of fees (approx); pricing AERO would give the emission yield per cycle.

## base 0xbf1e2087a8738e5f34d53938eb704cbd639cbdfb59902c38de75ca919e97eee2
mechanism: high-nonce wallet wrapping 13.17 ETH and spending the WETH within the window
confidence: high
unverified: operator.
A legacy transaction from nonce 2,561,330: deposit() of 13.173191 ETH ($32,379) into WETH. The wallet made 5 transactions in the window, one failed, two above the threshold, and its WETH nets −$1 on $64,760 through: wrapped and spent within the two minutes. A market-making or bridge wallet converting inventory.

## base 0x9c1d00e8b2ae862065e647648625e2812786608a5b66a5664d09dd62cbff9cdf
mechanism: a user opens a WETH/cbXRP concentrated position through a zap contract with 14.1 ETH and 9,869 cbXRP
confidence: medium
unverified: pool 0xb90f…03d6 as a Slipstream pool (clone of 0xc770…8985) and 0xe1f8…cd9a as a position manager are model memory; cbXRP is the token's self-reported symbol and is unpriced.
14.103572 ETH ($34,666) arrives with 9,868.61 cbXRP at contract 0xf8ce…c07f, which wraps the ETH, moves 14.089468 WETH and the cbXRP into pool 0xb90f…, mints liquidity in ticks [−201700, −201600] (a 1 percent band) and returns position NFT 5,555,556 plus WETH dust. Sender nonce 58,226, one transaction in the window. About $69k of capital (approx; the packet counts only the WETH leg). One deposit that stays: the shape the cyclers imitate but not the behaviour.

## base 0x0e890ae0c61cbb57eb6f46c51b3b64e5850b30fee1843bc2221fdddbc990442d
mechanism: multi-pool position manager collecting 11 positions across eight Aerodrome pools in one transaction, $1.9M gross
confidence: medium
unverified: the manager's identity; the destination is the one the pilot memo's Finding 2 flagged for 14 burns and 14 collects, and by memory it is a professional liquidity-management vault.
0x1d58…479c (nonce 3,695,371; 11 transactions in the window) calls 0x6104…d14b (130 bytes, a proxy) with selector 0xb2e8b356 and 11 ids; 22 zero-liquidity burns and 22 collects follow and the manager receives 8.834273 cbBTC ($704,148), 260.845675 WETH ($641,151) and 535,754.57 USDC ($535,679) from pools including cbBTC/USDC 0x4e96…, WETH pools 0x3fe0… and 0x42d4… and five others, plus AERO, TOWNS, ALIGN, VVV and METAc (unpriced). 187 logs, 4.59M gas, fee $0.07. Its twin #17 redeploys. Over the window the manager nets −$243,548 cbBTC, −$85,172 WETH and −$33,684 USDC on $32.7M, $15.7M and $11.4M through: unlike the cyclers it does not net to zero, it added about $360k to pools in two minutes (approx), and it does not cycle every block (31 collects and 30 mints in 52 blocks from nine sender EOAs).

## base 0xee264c1feafe98a5ec3083954f09952eafa3fe47f5e66f7afcbd56c235cac4d2
mechanism: the redeploy half of #16: 13 positions minted across 13 pools, $1.5M gross
confidence: medium
unverified: as #16.
0x3f31…4139 (nonce 2,814,829; 12 transactions in the window) calls the same manager with selector 0x0d390afd and 13 ids. The manager sends 313.285335 WETH ($770,046), 6.145273 cbBTC ($489,817) and 279,465.48 USDC ($279,426) into 13 pools and receives 13 position NFTs; 13 mints, 13 burns, 13 collects, 157 logs, 6.38M gas. The largest legs go back where #16 took them from: 137.28 WETH into 0x42d4… (which paid out 152.55) and 3.234758 cbBTC into 0x4e96… (which paid out 3.234758): positions closed in one transaction and reopened with adjusted amounts in the next, rebalancing, with EURC, QUID, wtCOIN, ALIGN and VVV legs unpriced.

## base 0xf9c42a859f61e42ee092fc69461f4f023ef3512f75a1331e21702e3186c9bf9c
mechanism: exchange hot wallet withdrawing 20 ETH
confidence: medium
unverified: 0x0d07…92fe as a Gate.io hot wallet is model memory.
19.99998 ETH ($49,159) to an EOA with no other activity; sender nonce 1,609,860, four transactions in the window to three destinations, tip 0.01 gwei. The amount is 20 ETH less 0.00002 (approx), a fee remainder. Base's largest native transfer and its only packet that is not liquidity management.

## base 0x48627df7953c53400eac59dc3532886168a7d97956a51d1440e917927a10eea1
mechanism: second cycling operator burning a $1.2M USDC/WETH position at index 29, one of 120 transactions from one EOA
confidence: high
unverified: as #12.
Helper 0x2192…20db (609 bytes) called by 0x4506…2e22 (nonce 2,087,920; 121 transactions in the window, 120 above the threshold, one destination). Zero burn and collect return 230.036446 WETH ($565,423) and 660,183.57 USDC ($660,091) from pool 0xb2cc…, NFT 76,277,043 comes back from the gauge, and 0.279526 AERO is claimed; the re-mint follows at index 163 of the same block. Over the window the helper nets −$23,813 USDC and −$15,930 WETH on $83.4M each, and 0.00 cbBTC on $21.1M: the same operator runs the cbBTC/USDC pool (#20) and a WETH pool through two more sender EOAs, 0xfbff…3fd6 and 0xff57…41fb, 116 transactions each. The two helpers account for at least 454 of Base's 661 large transactions (approx, from the eight repeated patterns).

## base 0x7dfab7528beef88b1cd8dc53c0c35e3b8506dd15ddfa8d61a95a8045eff4bf8d
mechanism: the same operator minting a $211k cbBTC/USDC position as the last transaction of the block
confidence: high
unverified: as #12; cbBTC is valued at the BTC feed.
0xfbff…3fd6 (nonce 293,552; 116 transactions) mints 29,941.49 USDC ($29,937) and 2.276068 cbBTC ($181,417) into pool 0x4e96…e778 in ticks [−66900, −66800] at index 132 of 133. The pool's own window net, +$254,933 cbBTC and +$47,374 USDC, is the manager of #16 and #17 adding inventory, not the cycler. `cycling_check.json` for this pool: 640 cycler mints and 639 burns, burns at median index 24 and mints at 150, 3 of 38 swaps (20 percent of token0 volume) met cycler liquidity.

## arbitrum 0x86d9cf169d5c660e41f2c88e61649f13e36f4faa46536452ee492b5b09416076
mechanism: 20.57 ETH consolidated into an address that receives a second transfer two positions later
confidence: medium
unverified: whether 0x5635…8c3c is an exchange deposit address.
20.568371 ETH ($50,556) from an EOA with nonce 2,175 to 0x5635…, at index 2 of 6; #22 sends 15.329218 ETH from a different EOA to the same address at index 4 of the same block. Two wallets emptying into one address in one block is one operator sweeping, or two users of one deposit address at the same second; the first is likelier. The recipient nets +$88,235 ETH and does nothing else. Fees round to $0.00 at 0.02 gwei.

## arbitrum 0xc12ef6654712e53872f1b297fdde329fc1a0e8ce05579d4f337e4e25014fcaf4
mechanism: second leg of the consolidation in #21
confidence: medium
unverified: as #21.
15.329218 ETH ($37,679) from a different EOA (nonce 1,517) to the same recipient, two positions later in the same block.

## arbitrum 0x7998897e4a6823ea23962ffec7ec092944e04df40370b0f8321e02583fc7c055
mechanism: 117,786 ARB sent to an EOA that appears in four transactions
confidence: medium
unverified: whether the recipient is an exchange deposit address.
A legacy transfer from a nonce-57 EOA. At $0.132 per ARB the transfer is $15,591: a six-figure token count and a mid-size dollar amount. The recipient is touched by four transactions in the window and nets +$15,591 ARB.

## arbitrum 0x742fb6b55e7b2bafed1d2544ee72e411140423905a52f16e59647deea9886d46
mechanism: automated distribution of 38,663 USDC to 51 vault clones, each acknowledging with an event keyed by a 16-byte id
confidence: medium
unverified: the application; the recipients are EIP-1167 clones of 0x8db6…c8b7 per the code lookups, and the 16-byte ids in calldata and events look like off-chain account identifiers.
The operator EOA 0x6c3d…e7b2 (nonce 868,298; five transactions in the window) calls distributor 0x6df2…47ba (7,066 bytes) with 4,868 bytes of ids and amounts. 38,663.11 USDC is pulled from 0x74bb…f2cd (an EOA that funds it; window net −$39,693 USDC) and split into 51 transfers from $10.75 to $28,138 (to 0x2668…, a clone), each answered by an event from the recipient carrying the same id and amount. 102 logs, 3.38M gas, fee $0.17. Payroll, affiliate or PnL settlement into per-user vaults of one application. The distributor's window net is 0.00 on $87,159 through, so a second batch ran in the same two minutes.

## arbitrum 0x4b3b5eb9efd3d683892c1213ae09fee6b117a2dff6655feadf972b69bb1205e6
mechanism: 200,000 USDT sent to an EIP-7702 delegated account
confidence: high
unverified: who controls the delegated account and its delegate implementation.
A plain transfer of 200,000 USDT (self-reported symbol USD₮0 on Arbitrum) from a nonce-406 EOA to 0xeb0c…187a, whose code is 23 bytes, the size of a delegation designator. Fee $0.00. The recipient is touched by two transactions. With #7 on Ethereum, two of the 42 packets have a 7702 account on the large end of a stablecoin transfer.

## arbitrum 0xeb9ec1785cea72c442a4aef948aca5ccefbb5606fbef9d6b5c0f25a03efd0495
mechanism: 12,693 USDC EOA-to-EOA transfer from a nonce-3 wallet
confidence: high
unverified: nothing further to verify.
A single transfer, fee $0.00, both sides otherwise idle in the window. The control drawn from Arbitrum's population is the ordinary case.

## arbitrum 0x8f56222667941e41843d418769ea155545204cc559c13d76929dc710f6fd74b1
mechanism: 75,000 USDC into a 209-byte deposit forwarder that exists at the same address on Polygon
confidence: medium
unverified: the forwarder's owner; that 209 bytes matches minimal deposit-forwarder contracts used by exchanges is model memory.
A legacy transfer (sender nonce 8,035) to 0xee7a…4055, a 209-byte contract touched by 10 transactions in the window with a window net of +$73,778 USDC on $94,912 through. The same address holds 209 bytes of code on Polygon, where it received 23,591.60 USDC in #40 and nets +$24,670. One deployer, one CREATE2 salt, several chains: a custodian's or exchange's deposit address that sweeps periodically (about $21k left the Arbitrum copy within the window, approx).

## arbitrum 0x5b8bb73ee21405ba5ae1f5ca723e76e89e0e89021950a5b671b83cd40d582cbf
mechanism: 2,039,593 ARB deposited into a hot wallet that sent 26 transactions in the window
confidence: medium
unverified: which exchange; the label rests on behaviour.
A legacy transfer from a nonce-951 EOA worth $269,979 at the feed. The recipient 0xb38e…891d is touched by 50 transactions and sent 26; its window net is +$359,454 ARB, +$5,891 USDT and −$2,576 ETH, so it received another 0.7 million ARB from someone else in the same two minutes (approx) while paying out ETH. Deposits of the chain's governance token into an exchange, at $0.13 per token.

## optimism 0x3e2e0790a841d6c181cd76b5227b3adee954db0a283e5526befdb4ad61f32c7f
mechanism: per-block emission farming on the Velodrome USDC/WETH pool: 133,133 USDC plus 46.78 WETH minted at index 17 of 22 and staked
confidence: high
unverified: pool 0x4789…ba25 as a Velodrome Slipstream pool (clone of 0xc28a…d288), 0x416b…6f29 as the position manager, 0xa751…2712 as the gauge and VELO as the reward token are model memory; the pool is the one the pilot memo selected for its 30-minute history.
Helper 0xc26a…37e9 (5,881 bytes) called by 0xa83a…faf9 (nonce 3,395,532; 46 transactions in the window, all above the threshold, one destination) sends 133,133.357941 USDC ($133,115) and 46.783494 WETH ($114,992) into the pool, mints liquidity 1,002,250,754,316,857,559 in ticks [198200, 198300], about 2,449 to 2,473 USDC per WETH (approx), receives NFT 45,467,482 and stakes it. Fee $0.00 at 0.0000014 gwei. The helper's window net is −0.00 USDC and −0.00 WETH on $6.09M and $5.29M through; #30 burns the position at index 2 of the next block. `cycling_check.json` for this pool over 30 minutes: 1,948 cycler mints and 1,948 burns across 891 of 900 blocks, burns at median index 3 and mints at 25; 3 of 40 swaps (16 percent of token0 volume) executed while cycler liquidity was present, when it was 34 percent of in-range liquidity; the median in-range liquidity reported by swaps with cyclers present is about 16 times the median without (approx).

## optimism 0x6e2698795438641a491b65649f851308a24a9975c5bc7f26ea4b04ba3a9e4148
mechanism: the burn half of #29 at index 2 of the next block, with 1.17 VELO claimed
confidence: high
unverified: as #29.
Same sender, next nonce, index 2 of 25, tip 0.0015 gwei (paid to be early). A zero burn and a collect return 133,133.357941 USDC and 46.783494 WETH to the helper, the NFT comes back from the gauge, and 1.173034 VELO (unpriced) arrives. 526,518 gas, fee $0.00. At about a tenth of a dollar per OP-ecosystem token the reward per cycle is small; the operator's edge is reward per unit of liquidity while, as the check shows, the liquidity is almost never at risk.

## optimism 0xabad0ca120a8092822548fce2206cc5dbf035af57795153b83d4ee69c97ef54b
mechanism: second cycling operator paying its withdrawal directly to a treasury EOA, one of 120 transactions from one sender
confidence: high
unverified: as #29.
Helper 0xf1b4…7c76 (24,413 bytes) called by 0x32f5…764e (nonce 2,522,482; 120 transactions in the window, all above the threshold, its next one at index 27 of the same block). The collect sends 20,775.57 USDC ($20,773) and 7.300603 WETH ($17,945) from the pool straight to the EOA 0x9e3e…946e, and 0.49 VELO to the helper. Four sender EOAs (120, 40, 40 and 40 transactions) work this helper and its sibling 0x343c…320f, which moves exactly 30,000 USDC and 10.54 WETH twice in every block of the window, paying out to 0x9e3e… and 0x7a05…8d5b. The helper's window net is 0.00 on $3.46M through; the treasury 0x9e3e… nets −$11,551 USDC and −$10,730 WETH, so the operator added about $22k to its cycling stake during the window (approx). Position sizes of $11.8k, $20.8k, $32.3k and $40.9k appear in the census, all in the same tick band.

## optimism 0x68d4dc5b1ad326ab6464f726fa02079a9122a4f7a456e2949514f62aa8f354a8
mechanism: a liquidity deposit that stays: 38,991 USDC plus 14.07 WETH minted into the same pool and staked, with 4,071 OP claimed
confidence: medium
unverified: as #29; 0x5e6a…37b9 as a personal position-manager contract is inferred from its single caller.
0x9dbc…79c8 (seven transactions in the window) calls 0x5e6a… (5,797 bytes), which approves, transfers 38,990.927452 USDC ($38,985) and 14.070250 WETH ($34,584) into the pool, mints liquidity 297,191,618,962,531,091 in the same [198200, 198300] band, receives NFT 45,467,595 and stakes it. Its window net is −$38,970 USDC, −$34,431 WETH and +$4,072 OP: capital went in and stayed, and OP rewards came out. The control shows what the cyclers are not. The pool's own window net, +$50,050 USDC and +$46,497 WETH, is roughly this deposit plus fees (approx).

## optimism 0x0266cc61146a08c6b0016e4211d6b223282f45ae47e76893838abbc8df6a8d77
mechanism: #29 again 47 blocks later with 129,645 USDC: the operator's USDC stake fell by 3,489 over the window
confidence: high
unverified: as #29.
Same helper and sender (nonce 3,395,568, 36 nonces on), same tick band, the same 46.783494 WETH, but 129,644.591909 USDC instead of 133,133.357941. The 3,488.77 USDC difference (approx) with the WETH unchanged is what left the position between the two mints: re-staked fees would raise it, so this is rebalancing or the operator skimming USDC. The census counts the two amounts as separate patterns because they round differently, which is how one operator came to hold three ranked slots.

## polygon 0x3ce3501eba4ee3cf15f2116e2905775dc86ec501170ed8d9ace91cef80a2b57e
mechanism: aggregator sale of 6,800 USDT for 6,790 DAI split across a V4 pool, the Balancer vault and two V3 pools
confidence: medium
unverified: 0x3c48…d41c as an aggregator router is inferred from the same selector 0x0c307f76 and the same record-event topics seen on Ethereum (gas notes #5) and Base; 0xba12…f2c8 as the Balancer V2 Vault and 0x6736…5cd6 as a V4 pool manager are model memory.
The EOA (nonce 110) sells 6,799.95 USDT: 6,800.72 USDC comes out of a V4 pool (fee 10, tick −2), passes through the Balancer vault into 6,797.36 USDC.e, and USDC.e buys DAI in two V3 pools (401.72 and 6,395.64); the EOA receives 6,790.11 DAI and the router keeps 6.797 DAI, about 0.1 percent (approx). Gross volume $67,983 for a $6,800 trade: 16 legs, a 10 times inflation. Tip 350 gwei, $0.08. A user rotating one stablecoin into another at about 0.14 percent all-in (approx); #42 is the same router with 8,823 USDT-to-DAI from another user a minute later.

## polygon 0x82a3031ad2c5e53b0e50da767b246a174cdacaf87fb0c1b10b850096b84bfba7
mechanism: Polymarket CTF Exchange fill settled by the collateral vault sending 12,859 USDC.e into ConditionalTokens to split a full set of outcome tokens
confidence: medium
unverified: pUSD as an exchange collateral wrapper and 0xc417…9db1 as its reserve vault are inferred from the flows; 0xe111…996b is Polymarket's documented CTF Exchange and 0x4d97…6045 its ConditionalTokens; 0xada1…0087 as the position splitter is inferred.
A relayer-style sender (nonce 142,350; 8,964 bytes of calldata) matches one taker against 14 maker orders (14 OrderFilled-shaped events, one OrdersMatched). pUSD moves from the makers to the exchange in 17 transfers, and the vault 0xc417… sends 12,858.97 USDC.e through 0xada1… into ConditionalTokens, which mints outcome positions (14 ERC-1155 transfers). The vault is touched by 1,867 transactions in the window, about a fifth of Polygon's user transactions (approx), and nets −$83,771 USDC.e on $272,636 through while ConditionalTokens nets +$54,711: collateral is entering open positions faster than it is redeemed, a net-opening reading for the two minutes. pUSD, the most transferred token on Polygon with 11,321 transfers, is unpriced here; parity would be the natural assumption to test.

## polygon 0x0fa6a3b0d7e8d035024557572fe6fa063632ee438bdeaa015d1530317cb42ec3
mechanism: 10,145 DAI buys 8,467 LGNS on a QuickSwap V2 pool from a nonce-5 wallet
confidence: high
unverified: 0xa5e0…78ff as the QuickSwap router is model memory; LGNS is the token's self-reported symbol and the token the gas notes' 155-position unstake consolidated.
swapExactTokensForTokensSupportingFeeOnTransferTokens moves 10,145 DAI ($10,143) into pool 0x882d…, and 8,467.376126 LGNS (nine decimals) come out, about 1.198 DAI per LGNS (approx). The pool is touched by 417 transactions in the window and LGNS has 7,749 transfers, the second most on Polygon: a heavily traded token that an operator was unstaking and consolidating in 155 positions in the same window (gas notes #38). A fresh wallet buying $10k of it while a large holder consolidates is worth watching, not a signal by itself. Tip 355 gwei, $0.01.

## polygon 0xb00eb59718c7246cac40e256f37801a720a24de96e2a4700fea9af294264d86a
mechanism: 34,890 USDC into an address that also received 124,707 POL in #39
confidence: medium
unverified: whether 0x1347…74ec is an exchange deposit address.
A plain transfer from a nonce-23 EOA at a 60 gwei tip. The recipient is an EOA touched by four transactions that nets +$34,885 USDC, +$11,777 POL and +$1,011 USDT within the window from three different senders: one destination collecting several assets from several wallets is a deposit address.

## polygon 0x48f8502d6f5ea6fef2bcbf5ba0d3796ad3ceb66118b2c14c2124484e2d591a20
mechanism: 198,010 POL into a hot-wallet-like EOA that also received 89,980 USDT
confidence: medium
unverified: the recipient's operator.
Polygon's largest native transfer: 198,009.593575 POL, worth $18,699 at $0.0944. The recipient 0xe780…e245 is touched by 65 transactions in the window, sent six, and nets +$121,798 USDT and +$20,523 POL: many deposits in and occasional payouts out, the hot-wallet profile. The system contract 0x…1010 emits its native LogTransfer (topic 0xe6497e3e…) beside the fee log; the decoder should register it as Polygon's native transfer record.

## polygon 0x06c9c9f6e421c9186b46d703e882d826d632756fa77ccfb043261e93ab02fde9
mechanism: 124,707 POL into the deposit address of #37
confidence: medium
unverified: as #37.
From a nonce-6,068 EOA at a 60 gwei tip, the same tip as #37 one block earlier from a different sender, so either the deposit address's users share a wallet preset or both transactions belong to one operator. $11,777 at the feed.

## polygon 0x2b214f60d1ef3d16918e8340dd5ea9b767f315b4e28e4365a9e16f360a72000a
mechanism: 23,592 USDC into the cross-chain deposit forwarder seen on Arbitrum (#27)
confidence: medium
unverified: as #27.
A plain transfer from a nonce-4,031 EOA to 0xee7a…4055, the 209-byte contract that also exists on Arbitrum; on Polygon it is touched by eight transactions and nets +$24,670 USDC on $24,779 through. Same block and the same 75.45 gwei tip as #41, three positions apart, from different senders: a shared wallet fee preset, most likely.

## polygon 0x4723c1d868db4e782593975257a9edc805230c4ff77bd3d5ea91e579140f689c
mechanism: 89,980 USDT into the hot-wallet-like EOA of #38
confidence: medium
unverified: as #38.
The largest position change on Polygon: 89,980 USDT (self-reported symbol USDT0) from a nonce-10 EOA to 0xe780…e245, which nets +$121,798 USDT over the window from several senders. A round number less 20 (approx): a fee remainder or an exact post-fee deposit. Tip 75 gwei, $0.00.

## polygon 0x255541ebd2ad7a590616eff30b68d09974c224d8d305c07bd0049adaea7f1812
mechanism: the same aggregator as #34: 8,823 USDT into 8,810 DAI in four slices across five pools
confidence: medium
unverified: as #34.
A nonce-3 EOA sells 8,822.93 USDT in four slices (99.70, 1,822.82, 4,099.13 and 2,801.28) through a V4 pool, pool 0x5520…, V3 pool 0x3108… and the V4 pool again, consolidates 8,623.59 USDC, converts through the Balancer vault to 8,619.23 USDC.e, and buys 8,809.63 DAI; 27 transfer legs, 48 logs, $88,007 gross for an $8.8k trade. The rotation cost about 13.3 USDT, roughly 0.15 percent (approx), plus 1.18 POL of gas. Two users on the same router within a minute, both selling USDT for DAI below par: the DAI side of Polygon's stable pools was bid during the window.
