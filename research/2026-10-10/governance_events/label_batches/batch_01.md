# Labeling packets — batch 01 (125 proposals). Label each against criteria.md.

====================================================================================================
[0] id=QmUasF6yZRzQR7yzvjgTfrg7XREH3Do5EMqP4BBxJpqgu5  token=AAVE  space=aavedao.eth  date=2021-07-25
TITLE: Propose an AAVE x CURVE Alliance
CHOICES: I support this ! Ask Curve DAO | Buy some CRV but with stables | I disagree with this proposal 
TEXT (first 1500 characters):
Abstract:

Aave and Curve are two of the main DeFi protocols in constant evolution and growth with synergies between.
One way of increasing these synergies would be to give each protocol some voting power in the other governance.
A few weeks ago, i posted an ARC about a strategy using Curve to increase the revenues earned by Aave DAO. However, to benefit from the Curve system in the most efficient way, it requires to lock CRV.

Aave DAO is accumulating some CRV with the ecosystem collector, but not enough to boost the treasury from the ecosystem collector considering it’s now around 11.8M$ (or 753.3M$ including the ecosystem reserve). So how could the DAO get more CRV?

- Buy CRV using part of the funds from the ecosystem collector, but this would require approximately 850k$ to get the maximum boost on the Curve pools.

- Propose a token exchange between AAVE and CRV that increase the synergies created between both communities over the last year.

I would like to support the second option, especially because it would allow both communities to diversify their treasury without selling either Aave & Crv or spending additional stablecoins for this deal.

Treasury state:

AAVE:

Stablecoins: 1.3% of the DAO treasury worth 9.8M$
Ecosystem Reserve: 98.4% of the DAO treasury worth 741M$ in AAVE tokens
ETH/BTC & Governance tokens earned with the ecosystem collector including: 0.23% worth 2.05M$ (including CRV: 0.007% of the treasury worth 53K$)
CURVE:
Curve DAO also mostly hold $CRV w

====================================================================================================
[1] id=QmPyXyMKQPKnGmHj7Hgz6iujVCkgA3NUKPp3SgePy3EXVi  token=AAVE  space=aavedao.eth  date=2021-07-26
TITLE: Should AAVE Remove Flash Loan Fees?
CHOICES: Reduce Flash Loan Fees to Zero | Reduce Flash Loan Fees | Keep Flash Loan Fees
TEXT (first 1500 characters):
Rationale: AAVE's flash loan fees are not competitive with newer offerings on the market, and represent roughly 1% of protocol revenue. This revenue continues to steadily decline as more users switch to offerings like dYdX's free flashloans and Maker's new flash minting. AAVE governance should make a choice on whether to adapt to these changing conditions.

Proposal: Set flash loan fees to zero. This would essentially mean that the liquidity of AAVE would be available to all users with zero friction. The drawback is the loss of flash loan fees for depositors. Reducing flash loan fees is also an option, but there's no telling how long any new rate would stay competitive.

https://governance.aave.com/t/arc-reduce-flash-loan-fees-introduce-a-fee-for-1-tx-borrows-and-add-a-flash-loans-whitelist/3935

====================================================================================================
[2] id=QmdQiZvv5Z8GB4ScWqvLvtsJABZ78kqPHRb6SkGViGXeuq  token=AAVE  space=aavedao.eth  date=2021-07-27
TITLE: Dynamic Borrow/Deposit Rewards Split
CHOICES: Keep existing splits | Dynamic split for stablecoins | Dynamic split for all assets
TEXT (first 1500 characters):
Rationale: Since the implementation of liquidity mining rewards on April 26, deposit volume has outpaced borrow volume for stablecoins, leading to decreased utilization and deposit rates. 

Proposal: Modify the borrow/deposit rewards split for each asset to dynamically adjust based on the utilization rate. Each asset in AAVE has an optimal utilization rate (https://docs.aave.com/risk/liquidity-risk/borrow-interest-rate#interest-rate-model). By skewing the deposit/borrow rewards depending on the current utilization compared to optimal, it will incentivize AAVE users to push interest rates towards a stable equilibrium.

Given that the optimal utilization rate is set lower for non-stablecoins, this model can be applied to these assets as well.

A diagram of the proposed model is in the discussion below.

Discussion: https://governance.aave.com/t/arc-extend-aave-liquidity-mining-rewards/4852

====================================================================================================
[3] id=QmVbjarb9vTWYMQrEomSKD9PvZcnJv1btoN97PJeqRv7s7  token=AAVE  space=aavedao.eth  date=2021-07-27
TITLE: Safe Borrowing Rewards Program
CHOICES: In favor of program | Not in favor of program
TEXT (first 1500 characters):
Rationale: The liquidity mining program has resulted in a large increase in recursive borrowing. This activity is mostly non-productive to the protocol and takes up a large percentage of the rewards budget. This proposal is aimed to discourage unnecessary leverage and encourage users to be mindful of their liquidation risk.

Proposal: Allocate an amount of stkAAVE from the ecosystem reserve to incentivize AAVE users to maintain a high health factor. Distribute to users based on the following formula:

safeBorrowingRewards = userCollateral * rewardFactor where reward factor is a normal distribution centered at a health factor of 2

Discussion: https://governance.aave.com/t/arc-extend-aave-liquidity-mining-rewards/4852

====================================================================================================
[4] id=QmQvMC7CRx9o929LwacitsmDAuESs1asHJ6JwH914Bru2B  token=AAVE  space=aavedao.eth  date=2021-07-28
TITLE: Add FEI on AaveV2
CHOICES: Yes: Add FEI as collateral | No: Don't add FEI as collateral | More Discussions Needed
TEXT (first 1500 characters):
---
aip: <to be assigned>
title: Add FEI to Aave V2
status: Proposed
author: Joey Santoro (@joeysantoro), Brianna Montgomery (@bpm6867)
shortDescription: Create a new Aave V2 market for the FEI stablecoin
discussions: https://discord.gg/aDeErjS6Dt
created: 2021-06-16
updated: N/A
---

## Simple Summary

Fei Protocol issues a decentralized, scalable USD stablecoin called FEI. FEI aims to become a widely used decentralized stablecoin that reduces centralization risk throughout DeFi.

## Abstract

FEI is backed by protocol owned reserves used to provide liquidity and stabilize the peg. The Fei community is committed to using decentralized reserve assets and oracles to have FEI be as decentralized as possible. FEI is an ideal candidate to be included on Aave to provide more decentralized stablecoin alternatives.

## Motivation

Being the liquidity protocol, Aave understands the need for robust capital efficient liquidity in creating healthy markets. DAI and sUSD being the current available options for decentralized stablecoins is good but likely insufficient longer term. Having more options like FEI will improve liquidity and optionality for protocols which are committed to decentralization.

FEI brings with it substantial liquidity in the form of the $500m ETH-FEI pair on Uniswap V2. This can allow ETH leverage traders a capital efficient way to benefit from Aave liquidity and FEI liquidity. The yield paid by these traders will attract more FEI liquidity to Aave, benefiting both

====================================================================================================
[5] id=QmQjEhB3sn6buCuG2a16Uvn7oaE87VNyMEwwHB1NHUmEg6  token=AAVE  space=aavedao.eth  date=2021-08-15
TITLE: Should Aave Grants DAO approve a grant for developing an Aave mobile app?
CHOICES: Yes | No
TEXT (first 1500 characters):
2001DeFi team has submitted an Aave grants DAO application (not Aave treasury) to develop a mobile app interface for Aave Protocol. We would like to request an Aave DAO grant for $98k to design and develop a mobile application in React Native (iOS and Android). Please read the application here: https://governance.aave.com/t/proposal-building-a-mobile-app-for-aave/5298

Aave grants DAO committee supports this grant and would like to get a temperature check from the community.

We have been using Aave protocol and would love for Aave to have a decentralized app. Many mainstream users and crypto first-timers could enjoy using Aave on their phones. By developing a mobile app interface for Aave, we are hoping to accomplish followings:

- Onboarding new users to Aave protocol

- Ease of access to Aave protocol from mobile: checking healthfactor, reviewing proposals, voting, etc.

- User growth: more users interacting with protocol

- Increasing Aave TVL

We are a team of designers, developers, and product with backgrounds in DeFi UX design, video game design, contributor to graph protocol and IPFS, two times app featured on app store mobile engineer, and contributor to Aave and Yearn protocols.


The grant application is for Aave grants DAO and not for Aave treasury. Aave grants DAO committee has supported us and would like to get a temperature check from the community and have asked us to post the proposal on Aave Snapshot.

====================================================================================================
[6] id=QmeHAwW7XwUD3vqYLMRPF8MJiXkj2nnbRg1ae7mZ1SNQdm  token=AAVE  space=aavedao.eth  date=2021-08-18
TITLE: Should Aave Extend Liquidity Mining Rewards?
CHOICES: Yes  | No | Yes - Different distribution
TEXT (first 1500 characters):
Aave's liquidity mining program is ending in the next few days. 

We have seen several adjustments discussed in the forums including adding/removing new assets, allocating rewards based on health factors, additional vesting for stkAAVE rewards, and discouraging recursive borrowing. However, after discussing with several Aave community members and developers, these changes would require a heavy technical lift and potentially layer on a centralized distribution plan. 

We are open to these changes in the future but to avoid a disruption to the liquidity mining program, we propose the following program for the next 3 months: 

Asset	Daily stkAAVE Reward
DAI	        400.00
USDC	800.00
USDT	325.00
GUSD	5.00
sUSD	20.00
TUSD	10.00
PAX	5.00
RAI	       10.00
BAL	       10.00
YFI	       15.00
XSUSHI 15.00
LINK      25.00
UNI	       15.00
MKR       15.00
WBTC    150.00
ETH       180.00
Total      2,000.00		

This program would decrease the LM distribution by 9% while including more assets. The goal of this program is to create a more inclusive liquidity mining program with the option to further refine the distribution once live.

====================================================================================================
[7] id=QmSAvY8DQ7P16ZRDsUHyBWFmkrZFmfpGFhgoGuyStTZuUV  token=AAVE  space=aavedao.eth  date=2021-08-26
TITLE: Add FRAX to Aave V2
CHOICES: Yes: Add FRAX to Aave V2 | Do Nothing
TEXT (first 1500 characters):
---
aip: 29
title: Add FRAX to Aave V2
status: Proposed
author: Jason Huan (@jasonhuan_)
shortDescription: Create a new Aave V2 market for the FRAX stablecoin
discussions: https://governance.aave.com/t/proposal-add-support-for-frax/2621
created: 2021-08-25
---

## Simple Summary

Frax is the first algorithmic-stablecoin protocol, backed through on-chain collateral and algorithmically. Frax has two tokens, the FRAX stablecoin pegged at $1 and the FXS governance + seigniorage token, and aims to be a decentralized crypto-native unit of account with the upcoming Frax Price Index (FPI). FRAX has stayed at $1 for its entire existence, being the only non-traditional stablecoin to keep its peg perfectly in 8 months of release.

## Abstract

The FRAX stablecoin is partially backed with on-chain collateral and partially backed algorithmically, according to a collateral ratio (CR) parameter that the system adjusts according to market conditions. In Frax v2, the protocol is able to mint FRAX into lending markets using [Algorithmic Market Operations](https://docs.frax.finance/amo/overview) (AMOs), smart contracts which have the ability to print FRAX up to certain thresholds adjustable by governance.

## Motivation

As the value of Aave's TVL increases, borrow liquidity for stablecoins against volatile assets lent to Aave is one of the key benefits that is offered to lenders of the protocol. The flow of newly minted stablecoins to their decentralized lending market destination such as Aave

====================================================================================================
[8] id=QmYYBedL9aRFdC5DUgjN3QMoYxvJhAUBb2sEyhFuVQZbLG  token=AAVE  space=aavedao.eth  date=2021-09-10
TITLE: Launch Aave on Harmony
CHOICES: Yes | No
TEXT (first 1500 characters):
Harmony is proposing to deploy Aave v2 on the Harmony blockchain to expand lending to a growing community of users and provide incentives to bootstrap the launch of Aave to a new ecosystem. 

Paragraph Summary

Our goal is to accelerate Aave's expansion in the multi-chain world. Harmony is an open and fast blockchain that is fully Ethereum compatible with 2-second transaction finality and near-zero fees. 

Harmony invites the Aave community to support this launch by participating in the Aave contracts deployment, enabling the Aave v2 front-end for Harmony markets, and adding Harmony in its recently announced cross-chain governance module roadmap.  

Harmony will start by providing $5M USD in ONE tokens in incentives to bootstrap initial usage of Aave on Harmony. 

We specifically planned for a one year incentive campaign so that net new users have the opportunity to come into Aave and decentralized finance. We know that many protocols are giving out even higher incentives over a short period of time. We chose an attractive incentive over a longer period so that new users who may not be experienced power users can also benefit from the launch. 

In addition to token incentives, we will be investing heavily in co-marketing and educating users through tutorials, videos, and community-led support. 

Our overall goal is to use Harmony’s $300 million ecosystem fund for growing a deep base of 10,000 builders and 10 million users. 

Motivation

Aave is already planning to go multi-ch

====================================================================================================
[9] id=QmcgTovk982fcUTN17qtDyZ4oCoVGnKZJGuwMVtqspfphk  token=AAVE  space=aavedao.eth  date=2021-10-16
TITLE: Should Aave add the audited claimRewardsToSelf function to the liquidity mining incentives contract?
CHOICES: Yes | No
TEXT (first 1500 characters):
**Summary**
Aave incentive contracts currently only contain claiming functions in which the caller specifies the recipient to address, who will receive the claimed rewards. Unfortunately, this poses a security problem for abstractly-designed smart contract claimants that do not have fully-trusted originators of claiming txs. This is the case for Enzyme vaults.
By adding an additional claiming function to the incentive contract that uses msg.sender instead of to, the tx originator no longer needs to be trusted.
This simple addition - that can reuse the exact same claiming logic as the current claiming functions and will not require any changes to storage layout - will increase composability opportunities with Enzyme and similarly architected protocols.


**Background**
Enzyme is a decentralised asset management infrastructure built on Ethereum. It allows asset managers to build on-chain investment Vaults that utilise and allocate to the newest innovations in DeFi. Because all transactions occur on the Ethereum blockchain, compliance, accounting, and investor management services are rendered programatically and at a dramatically-reduced cost to their traditional finance counterparts.
Amongst other things, Enzyme Vaults can interact with AAVE by lending. We are currently also working on accommodating the borrowing functionality to enable leveraged strategies as part of our Sulu release this quarter.
In order to keep providing our users with superior asset management tools in De

====================================================================================================
[10] id=Qme8XusejN3LomNoxQcCsABPPJ1KmRgMFV3fj1eKRGzsGQ  token=AAVE  space=aavedao.eth  date=2021-10-18
TITLE: Add stETH on AaveV2
CHOICES: Yes: Add stETH as proposed | No: Do not add stETH
TEXT (first 1500 characters):
---
aip: <to be assigned>
title: Add stETH to Aave V2
status: ARC posted, pending snapshot vote
author: Jbeezy (@jbeezy1)
shortDescription: Create a new Aave V2 market for stETH
ARC discussion: https://governance.aave.com/t/arc-add-support-for-steth-lido/5793/6
created: 2021-10-18
updated: N/A
---

## Simple Summary

Lido allows users to earn staking rewards on the Ethereum beacon chain without locking Ether or maintaining staking infrastructure. This is done through the stETH token. stETH tokens represent a tokenized staking deposit and can be held, traded, or sold.

Full ARC and discussion can be viewed here: https://governance.aave.com/t/arc-add-support-for-steth-lido/5793

Proposed voting choices:
1. Yes: Add stETH as proposed (no borrowing)
2. No: Do not add stETH

## Abstract

There is strong interest in using stETH to earn additional yield without taking a lot of risk. This is evident through the growth of the stETH/ETH pool on Curve Finance, which has become the most liquid pool on Curve with a liquidity of $3.8 billion.

The addition of stETH on to Aave can work to attract a larger audience to both Aave and Lido. More ETH staked with Lido would subsequently benefit the decentralization and security of the Ethereum network, to the benefit of the community as a whole. stETH would likely bring new borrow demand to Aave as market participants look to borrow against their staked ETH or lend their stETH for a yield.

We want people who want to be responsibly long ETH (i.e.

====================================================================================================
[11] id=QmbeHotkg3SWSJSmdqau8scMAWrmHtYS1G6vwNF14v2d8k  token=AAVE  space=aavedao.eth  date=2021-10-21
TITLE: Should four (4) total risk parameters across three (3) Aave V2 assets be adjusted?
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
[Forum Discussion](https://governance.aave.com/t/arc-risk-parameter-updates-2021-10-21/5929)

## Simple Summary

A proposal to adjust four (4) total risk parameters across three (3) Aave V2 assets including LTV, Liquidation Threshold, and Liquidation Bonus.


## Abstract
This proposal is a batch update of three risk parameters to align with the the [Moderate risk level](https://snapshot.org/#/aave.eth/proposal/QmT9T4Rfnh1Z2HYmMPXvtFotMK2vSxiXK8dKStg2b6n4gi) chosen by the Aave community. These paramater updates are a continuation of Gauntlet's regular parameter recommendations, the latest being [AIP-42: Risk Parameter Updates 2021-10-14](https://app.aave.com/#/governance/42-Qmd8PTDdcq971N6QhLAKBdxN3sjdV5KJqqVw45CaRGRnej).


## Motivation

This set of parameter updates seeks to maintain the overall risk tolerance of the protocol while making risk trade-offs between specific assets. For more detail on Gauntlet's first two months of recommendations and their impact, please see our [Monthly Risk Report](https://governance.aave.com/t/market-risk-monthly-updates-and-review-october-2021/5887).


## Specification

No significant changes in volatility or liquidity were observed in most assets. However, we would note that the collateral usage of ZRX on Aave almost doubled, so that is an asset that we are monitoring during the upcoming period.


| Parameter | Current Value | Recommended Value |
| -------- | -------- | -------- |
| ENJ Liquidation Threshold    | 65%     | 70%     |
| DPI

====================================================================================================
[12] id=0x296cfaab6165c6a36d2afbd50fb28c349209cec4c2b6637352d6cf295eca7a85  token=AAVE  space=aavedao.eth  date=2021-11-16
TITLE: ARC - Aave V2 - Liquidity Mining Program (90 days at 30% reduced rate)
CHOICES: FOR Liquidity Mining | AGAINST Liquidity Mining
TEXT (first 1500 characters):
aip: TBA
title: Aave V2 - Liquidity Mining Program (90 days at 30% reduced rate)
status: Proposal
author: @MatthewGraham
created: 2021-10 25

# Simple Summary
Liquidity mining incentives were introduced to Aave V2on the 26th April 2021 via AIP-16 6 and then voted to continue on the 24th August 2021 via AIP-32 2 for an additional 90 days. AIP-32 incentives are due to expire 22nd November 2021.

This ARC presents the community with the opportunity to continue offering stkAAVE incentives for an additional 90 days from when AIP-32 2 finishes, up to including the 20th February 2021. The incentives will be distributed at a 30% reduced rate, commencing the tapering of incentives on the Aave V2 market.

Stable coin / low vol assets receive lending and borrowing incentives, split 1:2, in favour of borrowers over lenders. Aave V2’s revenue is derived from interest paid by borrowers and borrowing demand drives lending yield through higher liquidity utilisation. High vol assets receive lending incentives, skewed towards assets more recently listed and communities that have static relationships with Aave, like Balancer and Chainlink.

# Abstract
The intent is to recognise liquidity mining incentives played a large role in helping grow Aave V2 TVL, whilst being conscious that competitors continue to offer incentives APRs marginally exceeding what Aave is currently offering.

When incentives were reduced aggressively on the Polygon market, the daily revenue reduced significantly. There is a

====================================================================================================
[13] id=0xb9f2a37fbc61a6fc02276a86d14c69ff234287426bd6726980834487d1c37c95  token=AAVE  space=aavedao.eth  date=2022-02-01
TITLE: Deploy Aave V3 on Evmos
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Evmos proposes deploying Aave v3 on the Evmos blockchain to expand lending to the Evmos and greater Cosmos ecosystem. Evmos will be the port of entry to Cosmos for Ethereum users and vice-versa with the introduction of developer-focused incentives, interoperability across other Cosmos chains and interchain composability.

**Summary**

Evmos is an application-agnostic chain that will be interoperable with the Ethereum mainnet, EVM-compatible environments, and other BFT chains via IBC, making it easy for users and developers to interact seamlessly between chains. Rather than being competitive with Ethereum, Evmos aims to expand the functionality of the EVM to offer interoperability that enables new use cases. EVM bridges ([Nomad and Connext](https://evmos.blog/bridging-assets-to-evmos-with-nomad-and-connext-e8ec182145d5)) will integrate with Evmos shortly after mainnet launch to allow Ethereum and other EVM chains’ ERC-20 tokens to be available on Evmos and subsequently the entire Cosmos ecosystem via IBC.

Evmos was founded by Federico Kunze Küllmer and Akash Khosla. Federico has been a core contributor to a number of Cosmos projects including Tendermint, Cosmos SDK, Core IBC, Gravity Bridge (formerly Peggy) and Sommelier. He has been building in the blockchain space since 2017 when he was an exchange student at UC Berkeley, where he joined Blockchain at Berkeley. Akash had been working in the Cosmos ecosystem at Anchorage and as a Co-Founder of Blockchain at Berkeley, the blo

====================================================================================================
[14] id=0xf3b11b0e7bb488d054d8d61b8bfdad3a3919cbac8ce0173e39c9f69102d44338  token=AAVE  space=aavedao.eth  date=2022-02-03
TITLE: ARC - Continue Liquidity Mining Program on Aave V2 Ethereum market and Introduce Liquidity Mining on Aave ARC market
CHOICES: Directional - Yes | Directional - No
TEXT (first 1500 characters):
---
This is direction vote to continue with liquidity mining on Aave V2 Ethereum market and introduce liqudity mining on Aave ARC. The final proposal will reflect the discussion on the governance forum.

aip: TBA
title: ARC - Continue Liquidity Mining Program on Aave V2 Ethereum market and Initiate Liquidity Mining on Aave ARC market
status: Proposal
author: @MatthewGraham, @3SE_Holdings, @4lex.eth
created: 03.02.2022
Discussion: https://governance.aave.com/t/aave-v2-liquidity-mining-program-aave-v2-ethereum-market-and-aave-arc-market/7189

----

# Simple Summary

This ARC presents the community with the opportunity to continue offering stkAAVE incentives on Aave V2 Ethereum market for an additional 90 days from when [AIP-47](https://app.aave.com/#/governance/47-QmRTKqSJCMKysQonSHdxkawei78NmHe1aq6yAjDmWUPgqH) finishes at a further 30% reduced rate.

In addition to tapering incentives on the Aave V2 market, the ARC proposes introducing incentives on the Aave ARC market. 10% of the 30% reduction in incentives on the Aave V2 ethereum market are to be applied to incentivising AUM on the Aave ARC Ethereum market.

# Abstract

Liquidity mining incentives were introduced to Aave V2 on the 26th April 2021 via [AIP-16](https://app.aave.com/#/governance/11-Qmf1JeXiw8BDUoKJ89VmUJ8wy22D2udqL4HxprCG7DZ5zG), renewed by [AIP-32](https://app.aave.com/#/governance/28-QmWaac9UwQuiBtsGpm4oG6TwnVd86DWfqtVV8f11y5ZM5E) and then incentives were reduced by 30% with the implementation of [AIP-47](htt

====================================================================================================
[15] id=0xa460ff7c6b7531bd659c43d58a2cf6f4d23f08af010327350bc428583cc8942e  token=AAVE  space=aavedao.eth  date=2022-02-03
TITLE: ARC - Consolidate Aave V1, V2 & AMM Reserve Factors, Purchase CVX and Deploy to Earn Yield
CHOICES: Yes - Go in this direction | No - Do not go in this direction
TEXT (first 1500 characters):
---
This is direction vote to continue with proceed with the forum post. The final proposal will reflect the discussion on the governance forum.

title: ARC - Consolidate Aave V1, V2 & AMM Reserve Factors, Purchase CVX and Deploy to Earn Yield
author: Llama Community @MatthewGraham @Dydymoon 
created: 03/01/2022

https://governance.aave.com/t/arc-consolidate-aave-v1-v2-amm-reserve-factors-purchase-cvx-and-deploy-to-earn-yield/6797
---

# Simple Summary

The Aave V1, V2, and AMM market Reserve Factors (RF) on the Ethereum network hold a combined value of over [$28.27M](https://dune.xyz/llama/Aave-Treasury-Finances-by-Llama?Trailing%20Num%20Time-Series=60). The Llama Community proposes consolidating the RF into the V2 RF and deploying the capital with the intention of retaining TVL and earning additional yield. The yield generated comes with the added benefit of acquiring governance tokens of other DeFi protocols and increasing Aave’s metagovernance influence.

# Abstract

The Llama Community recommends implementing several yield generating strategies spanning Balancer, Curve, and Convex and subsequently participating in the respective communities' tokenomic constructs. Aave will earn yield in the form of swap fee income, aToken yield derived from Aave V2, and governance token incentives in the form of BAL, CRV, CVX, stkAAVE and LDO.

The first investment theme is deploying capital into the Balancer Boosted Pool and BTC Stable Pool to earn a vAPY of around 13.4% and 4.6% respec

====================================================================================================
[16] id=0x399300d33120f63cdda37068b46e5da8485dbeeb1100dab0367a223124798f5b  token=AAVE  space=aavedao.eth  date=2022-03-05
TITLE: ARC Add support for CVX
CHOICES: Yes - Do Add CVX | No - Do Not Add CVX
TEXT (first 1500 characters):
---

Title: ARC Add support for CVX 
Author: Llama Community members @MatthewGraham, @JeanBrasse and @Dydymoon with help from @zze 
Created: 15/02/2022

---

## References:

Project: https://www.convexfinance.com/
Whitepaper: https://raw.githubusercontent.com/Convex-Dev/design/main/papers/convex-whitepaper.pdf
Github: https://github.com/convex-eth
Documentation: https://docs.convexfinance.com/convexfinance/
App: https://www.convexfinance.com/stake
Audit: https://github.com/mixbytes/audits_public/tree/master/Convex%20Platform
Dune: [​​https://dune.xyz/Marcov/Convex-Finance](https://dune.xyz/Marcov/Convex-Finance)
CVX: https://etherscan.io/token/0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B
Chainlink: https://docs.chain.link/docs/ethereum-addresses/
Twitter: https://twitter.com/convexfinance
Telegram: https://t.me/convexEthChat
Discord: https://discord.com/invite/uAwvZfs9qU

## Summary

The Llama Community would like to ask for your support in listing CVX as a collateral asset. CVX is the governance token of the Convex Finance protocol.

## Motivation

CVX is not currently listed on major lending markets, including CVX on the platform would allow Aave to benefit from the first mover advantage. This has the potential to be a meaningful high vol asset revenue source. CRV is currently the fifth highest earn asset on the Aave V2 Market and has generated 190.33k aCRV tokens in revenue worth around $578.04k at the time of writing.

In addition to the lending and borrowing demand, the aC

====================================================================================================
[17] id=0x751b8fd1c77677643e419d327bdf749c29ccf0a0269e58ed2af0013843376051  token=AAVE  space=aavedao.eth  date=2022-03-28
TITLE: Add MAI to Aave V3 on Polygon, Fantom, and Avalanche
CHOICES: YES, add MAI to Aave V3 | NO, do not add MAI to Aave V3
TEXT (first 1500 characters):
Author: QiDao Protocol core team
Forum post: https://governance.aave.com/t/add-mai-on-aave-v3/7630

Proposal to add support for MAI (aka miMatic) on Aave V3 (On Polygon, Fantom, and Avalanche)

### Summary

MAI is the first and largest stablecoin project on Polygon and Fantom. It is an overcollateralized stablecoin that is non-custodial. All MAI is backed by collateral locked in user-managed vaults. MAI minting is available on 8 chains, and bridging to 18 chains.

All accepted collaterals are priced using Chainlink price feeds. MAI has stayed within its peg through several market downturns.

There’s around 250M MAI minted, with liquidity on all top DEXs in which MAI is present. A significant portion of liquidity for MAI is on Curve. MAI hosts the largest pool on Curve Polygon and the pool with most volume on Curve Fantom.

### Risk Parameters

* V3 Efficiency mode stablecoins: 97% LTV, 98% Liquidation threshold, 10% reserve factor
* V3 Isolation mode: 75% LTV, 80% liquidation threshold, 10% reserve factor, $50M initial debt ceiling per chain

### Specifications

1. What is the link between the author of the AIP and the Asset?

Core team at QiDao Protocol.

2. Provide a brief high-level overview of the project and the token

MAI is the first and largest stablecoin protocol on Polygon. It allows users to lock their tokens and use them as collateral to mint MAI at 0% interest.

MAI is an overcollateralized CDP stablecoin on Polygon, Avalanche, Fantom, Arbitrum, Harmony, Moonrive

====================================================================================================
[18] id=0x40871bfdae8e39b8ddfd7cc63b9138ca115dbd7ab84097dc953e74b8da042ef8  token=AAVE  space=aavedao.eth  date=2022-04-10
TITLE: ARC - Strategic Investment BAL Token
CHOICES: FOR | AGAINST
TEXT (first 1500 characters):
---

title: ARC - Strategic Investment BAL Token
status: WIP
author: Llama Community - @MatthewGraham
created: 21-03-2022

---

# Simple Summary

Acquire 200,000 BAL tokens via a combination of performing a BAL for AAVE token swap. The BAL tokens are to be complemented with ETH and deposited into the 80/20 BAL/ETH pool. The BPT token is deposited into the veBAL contract and locked for 1 year. The veBAL holding is then used to direct incentives to new aToken Boosted Pools, [1].

# Abstract

Perform a token swap with Balancer by exchanging AAVE from the Ecosystem Reserve for 200,000 BAL tokens. The exchange rate to be used is the 90-day moving average price when the votes pass on both sides. 

All 200,000 BAL tokens plus the aBAL tokens in the Reserve Factor (redeemed for BAL) are to be paired with sufficient ETH and deposited into the Balancer V2 BAL:ETH (80:20) pool. The veBAL holding will then participate in Balancer's revised tokenomics that commenced on the 28th March. 

Initially, the veBAL will be used to vote BAL rewards to pools which support aTokens that create TVL for Aave and/or AAVE liquidity pools.

# Motivation

Aave and Balance have a long history of working together. The AAVE : ETH (80/20) Balancer V1 pool BPT is accepted within the Aave Safe Module and the newly created Balancer Boosted Pools drive TVL to Aave markets, [2].

When the AAVE : ETH (80/20) Balancer V1 pool is moved to Balancer V2 and integrated into Aave’s Safety Module, the veBAL tokens can be us

====================================================================================================
[19] id=0xba25ccc6ec9c6638788e7337b892c37b52a843de4b8d7e273a0bb25b90947b81  token=AAVE  space=aavedao.eth  date=2022-04-27
TITLE: Aave Grants DAO Renewal Approval
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
We are looking to renew the program for the next two quarters by providing $6 million dollars in AAVE ($3 million per quarter). This is the third proposal for AGD. Aave Grants DAO is a community-led grants program, focused on growing a thriving ecosystem of contributors within Aave through funding ideas, projects and events that benefit the ecosystem. We aim to drive development on top of Aave and ensure a constant influx of talented builders to maintain Aave’s long term growth. We help build culture and community around the Aave ecosystem that in turn attracts the best contributors.

More details, including stats on AGD's grant distributions, can be found in our renewal post: https://governance.aave.com/t/aave-grants-dao-update-and-renewal/7842.

====================================================================================================
[20] id=QmVqWgpRmoEvvhvXZFepmAgYU5ZK9XpSs39MExEUpiJZw3  token=AAVE  space=aavedao.eth  date=2022-05-03
TITLE: ARC - Strategic Partnership with Balancer Part #2
CHOICES: FOR | AGAINST
TEXT (first 1500 characters):
---

title: ARC - Strategic Partnership with Balancer Part #2
status: Discussion
author: Llama Community - @MatthewGraham
created: 03-05-2022

---

# Simple Summary

Acquire 100,000 BAL tokens by deploying a Bonding Curve contract. The BAL tokens are to be held in the Reserve Factor until further details relating to Aura emerges and then the Aave community can determine if to deploy BAL to receive veBAL or auraBAL, [1].

# Abstract

Deploy a Bonding Curve to acquire an additional 100,000 BAL tokens on market at the chainlink oracle price +50 bps, for a cost $1,708,500 assuming a BAL price of $17. This is an additional purchase to the 200,000 BAL token swap being considered.

Aave will become one of eight token holders with 300,000 BAL tokens. All 100,000 BAL tokens are to be retained in the Reserve Factor until such time as further information on auraBAL emerges.

# Motivation

The original motivation for performing a token swap with Balancer can be found on the ARC - Strategic Investment BAL Token, [2].

With the additional 100,000 BAL acquisition, Aave would transition from just outside the Top 50 BAL holder to inside the Top 30 holders, [3]. If an additional 75,000 BAL was acquired, totalling 375,000 BAL, then Aave would become a Top 20 holder and this includes three community wallets, one Polygon bridge pool and the main BAL liquidity pool. So really it would be more like the Top 15 holders if another 75,000 BAL was acquired.

With 300,000 BAL tokens, Aave would have the

====================================================================================================
[21] id=0xdce03239f56932dfe5a074e20cefcdb0953ece31924814c83f7466910a5df602  token=AAVE  space=aavedao.eth  date=2022-05-04
TITLE: Add support for sAVAX (BENQI Liquid Staking AVAX Token) on AAVE v3
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
## References

Project: https://staking.benqi.fi/ 1

Document portal: https://docs.benqi.fi/

Ethereum addresses contracts: https://snowtrace.io/token/0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE

ChainLink Oracle: 0x2854Ca10a54800e15A2a25cFa52567166434Ff0a 1

Audit: https://162914606-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F-MViz_ikDZy4OemUj_VI%2Fuploads%2Fsjpc2u859ZnLjsedBuel%2FBenqi_LiquidStaking_Smart_Contract_Security_Audit_Report_Halborn_Final.pdf?alt=media&token=6b646d03-5123-42cd-b210-2238f8d0242b

Formal Verification: http://certora.com/wp-content/uploads/2022/04/benqiApril2022.md-Grip.pdf

Twitter: https://twitter.com/BenqiFinance

Telegram: https://t.me/BENQIFinance 1

## Summary

The community would like to ask for your support in listing sAVAX as a collateral asset. sAVAX is the Liquid Staking token from BENQI protocol.

## Motivation

sAVAX is a Liquid Staking token that allows a user to unlock liquidity while participating in securing the Avalanche network. As sAVAX constantly increases in value from network validation reward, listing sAVAX would allow users to unlock liquidity as a collateral for loans and in turn generate revenue to AAVE. Revenue in the form of sAVAX will always grow from the said network validation reward.

sAVAX is the largest Liquid Staking token on Avalanche and has over 3M sAVAX in circulation with deep liquidity in AMMs to support a healthy lending market ecosystem.

## Specifications

#### What is the link betw

====================================================================================================
[22] id=0x5c66ab47332df1fd14d2eca7632439115c6ebc0f956f498d74e9d6fb6348f1dd  token=AAVE  space=aavedao.eth  date=2022-05-05
TITLE: [ARC] Supply/borrow cap framework Fast track framework
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
To increase Aave protocol V3 efficiency and allow faster updates to caps on V3 markets this snapshot vote intends to implement a fast track framework for these caps.

Suggested fast-track process :

Step 1 - Governance thread for 24h
Step 2 - Snapshot with immediate vote open for 48h
Step 3 - Community multisig enforcement

Suggested scope & limitations of the fast-track process :
- Fast-track can only act on Supply & Borrow caps within a 30% to 100% modification range
- Fast-track requires an 80k AAVE quorum
- This process can only be applied to assets listed for at least 2 weeks.
- The process should take maximum 4 days. Meaning that in networks currently with Guardian, the Guardian should prepare the signing in advance, to assure execution not more than 24h after Snapshot closes positively.

This current proposal also would also upgrade the USDC supply cap on Aave Avalanche V3 market of +100% to a new total of 4B$ meaning that both adoption and execution of this framework would be the outcome of this proposal if YAE is leading at the end of the vote.

Community discussions related to the topic can be found on the link attached

====================================================================================================
[23] id=QmeTA4pmNiwX2CrurGwccLNiSGSDe2Ys46HErQXbo2R49E  token=AAVE  space=aavedao.eth  date=2022-05-07
TITLE: Should nine (9) total risk parameters across five (5) Aave V2 assets be updated?
CHOICES: YAE | ABSTAIN | NAY
TEXT (first 1500 characters):
## Simple Summary

A proposal to adjust nine (9) total risk parameters, including LTV, Liquidation Threshold, and Liquidation Bonus across five (5) Aave V2 assets. 

## Abstract
This proposal is a batch update of risk parameters to align with the [Moderate risk level](https://snapshot.org/#/aave.eth/proposal/QmT9T4Rfnh1Z2HYmMPXvtFotMK2vSxiXK8dKStg2b6n4gi) chosen by the Aave community. These parameter updates are a continuation of Gauntlet's regular parameter recommendations.


## Motivation


This set of parameter updates seeks to maintain the overall risk tolerance of the protocol while making risk trade-offs between specific assets.

Gauntlet's parameter recommendations are driven by an optimization function that balances 3 core metrics: insolvencies, liquidations, and borrow usage. Parameter recommendations seek to optimize for this objective function. Our agent-based simulations use a wide array of varied input data that changes on a daily basis (including but not limited to asset volatility, asset correlation, asset collateral usage, DEX / CEX liquidity, trading volume, expected market impact of trades, and liquidator behavior). Gauntlet's simulations tease out complex relationships between these inputs that cannot be simply expressed as heuristics. As such, the input metrics we show below can help understand why some of the param recs have been made but should not be taken as the only reason for recommendation. The individual collateral pages on the [Gauntlet Risk Dashb

====================================================================================================
[24] id=0xcce9760adea906176940ae5fd05bc007cc9252b524832065800635484cb5cb57  token=AAVE  space=aavedao.eth  date=2022-06-04
TITLE: ARC: Add GNO to Aave V2
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Proposal by Karpatkey DAO team

This is a proposal to add GNO, the Gnosisdao’s governance token, as collateral in the Aave v2 protocol.

Gnosisdao is a collective that uses GNO to transparently guide decisions on the development of Gnosis products. It has produced solutions which are widely adopted in our ecosystem, such as the Gnosis Safe multisignature wallet, Zodiac (DAO tooling consisting of Avatars, Modules, Modifiers, and Guards architecture), Gnosis Auction (a platform for conducting fair, transparent, and decentralized batch auctions) and Cowswap (which allows anyone to buy and sell tokens using gas-less orders that are settled peer-to-peer among its users or into any on-chain liquidity source while providing MEV protection), among others.

The GNO token allows its holders to be validators and boost their rewards on the Gnosis Chain network (formerly the xDai Chain). The Gnosis Chain provides stability and scalability. It is a stable EVM (Ethereum Virtual Machine) blockchain designed for fast and inexpensive transactions. The Gnosis Chain currently has a TVL of $290M, with 130k+ transactions a day, an average block time of 5 seconds, and holds over 6.1M wallets.
Useful Links

    Gnosis Chain: EVM 2
    Gnosisdao: Gnosis GnosisDAO 2
    Governance forum: GnosisDAO - Gnosis
    Gnosis Chain Information & Resources: https://gnosischain.world/
    Gnosis Blog: https://blog.gnosis.pm/
    Gnosis Docs: Gnosis Developer Portal Gnosis Protocol · Gnosis Protocol

Motivation

====================================================================================================
[25] id=0x669d6c67dfc4ca944f74c3e311060f844fc069065ab7099addd3daa298711bec  token=AAVE  space=aavedao.eth  date=2022-07-05
TITLE: ARC: Add support for LUSD (Liquity)
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Add LUSD as a borrowable asset on Aave

### References

* Project: https://liquity.org/
* Whitepaper: https://docsend.com/view/bwiczmy
* Twitter: https://twitter.com/liquityprotocol
* Codebase: https://github.com/liquity/dev
* Documentation: https://docs.liquity.org/
* App (list of front-ends): https://www.liquity.org/frontend
* Audit - Coinspect - March 21: https://www.coinspect.com/liquity-audit/
* Audit - TrailOfBits Security Assessment: https://github.com/trailofbits/publications/blob/master/reviews/Liquity.pdf
* Audit - TrailOfBits Liquity Protocol and Stability Pool Financial Report - March 21: https://github.com/trailofbits/publications/blob/master/reviews/LiquityProtocolandStabilityPoolFinalReport.pdf
* Audit - TrailOfBits Liquity Proxy Contracts Report - March 21: https://github.com/trailofbits/publications/blob/master/reviews/LiquityProxyContracts.pdf
* LUSD token contract: https://etherscan.io/token/0x5f98805A4E8be255a32880FDeC7F6728C6568bA0
* Discord: https://discord.gg/WQMEcgHBpc

### Paragraph Summary

LUSD is stablecoin minted directly by the protocol users by opening a Trove and depositing ETH as collateral. Loans are interest-free, with a 0.5% base initiation fee. All the contracts of the Liquity protocol are immutable, which makes LUSD the most trustless stablecoin currently available on the Ethereum mainnet.

LUSD is overcollateralized by ETH with two main mechanisms helping it keep its peg: first, LUSD can be redeemed for ETH at face value (i.e., 1 LUSD fo

====================================================================================================
[26] id=0xeefcd76e523391a14cfd0a79b531ea0a3faf0eb4a058e255fac13a2d224cc647  token=AAVE  space=aavedao.eth  date=2022-08-07
TITLE: [ARC] Aave V3 Fantom - Freeze reserves
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Simple Summary
This ARC proposes to freeze the Aave V3 Fantom market, allowing users to repay their debts and withdraw but blocking deposits and further borrowing on this market.
After the Harmony bridge event and the recent Nomad bridge exploit, the aave community should consider the risk/benefits of keeping an active Aave V3 market on fantom as this network is dependent of anyswap (multichain) bridge.

The Fantom Aave V3 market did not gain noticeable traction with a current market size of 9M$ and 2.4M$ of open borrowing position, this led to a market generating on average 300$ of fees daily for the protocol (~30$ of daily fees for the Aave treasury)

This market is not currently supported by the Aave Safety module and unless the Aave governance decides otherwise by specific vote, a failure of the main Bridge to Fantom will lead to users with assets worth 0.

This proposal calls for the Aave Guardian to freeze all reserves on the Aave V3 deployment on Fantom. This action would protect users by disabling the ability to deposit or borrow assets in the Aave V3 Market on Famtom, while still allowing repayment of debt, liquidations, withdrawals, and changes to the interest rates. Freezing the reserves will not interfere with any direct transfers to any of the aToken contracts.

Motivation
The unbalanced risk/reward of keeping of Aave V3 market on Fantom is the motivation of this ARC,

The risk of exposing users to potentially losing millions of $ due to causes exterior to intrin

====================================================================================================
[27] id=0x618c740ae12a64b570cbfac9688864ad427da49556b48f8eac04d796e1e67c7b  token=AAVE  space=aavedao.eth  date=2022-09-12
TITLE: [ARC] Add new KNC to Aave v2 and v3
CHOICES: YES | NAY | Abstain
TEXT (first 1500 characters):
## Summary
Full details at: https://governance.aave.com/t/arc-add-new-knc-to-aave-v2-and-v3/8236

Kyber Network is a multi-chain crypto trading and liquidity hub that connects liquidity from different sources to enable token trading at the best rates through its main user interface [KyberSwap.com](http://kyberswap.com). As a hybrid DEX aggregator + liquidity platform, it aims to offer the best rates for traders and the best returns for liquidity providers with concentrated liquidity.

Kyber Network launched on Ethereum in February 2018 and is a pioneer in the DeFi space, developing one of the earliest decentralized exchanges (DEX) with Vitalik Buterin as an advisor. The team has continued to innovate; spearheading the launch of WBTC (Wrapped Bitcoin) - the most popular ERC20 version of Bitcoin today, as well as developing amplified liquidity pools on KyberSwap that offers capital efficiency for any token pair. Kyber Network is also part of the pioneer batch of Alliance DAO/DeFi Alliance mentors.

This proposal aims to list the new version of the [Kyber Network Crystal (KNC) token](https://etherscan.io/token/0xdeFA4e8a7bcBA345F687a2f1456F5Edd9CE97202) for borrowing and lending and as a collateral asset on both Aave v2 and v3, after [delisting](https://governance.aave.com/t/arc-risk-parameter-updates-2022-03-31/7742) the old KNCL token (previously on Aave).

## Motivations

KyberSwap (Kyber Network’s main swap interface) is one of the oldest and most popular DEX aggregators wit

====================================================================================================
[28] id=bafkreidmj5twyypvk3se7nojlgw44zdcoz3d3szgddx2viug65grf42uce  token=AAVE  space=aavedao.eth  date=2022-11-01
TITLE: Staked ATokens, A New Aave Primitive Exploring Vote-Escrow Economies
CHOICES: Approve | Disapprove | Abstain
TEXT (first 1500 characters):
**Summary**

This proposal seeks community approval for the DAO to implement a new aToken primitive called “Staked aTokens” that would allow the Aave Protocol to participate in Vote-Escrowed economies. This new primitive would allow for the use of Liquidity Provider (“LP”) tokens from ve-based protocols, like Balancer or Curve, as collateral while participating in those protocols’ ecosystems. LP tokens are locked at their corresponding vaults (e.g., gauges) producing increased rewards that are distributed to suppliers to the Aave Protocol.

Under this proposal, users could use their LP positions as collateral while earning a variety of rewards with a maximized rate (also known as “boost” and referred to as increased rewards throughout this proposal). This brings a new wave of strategies like leveraged LP positions which can increase user rewards greater than the 2.5x limit and tap into the stability of listed stablecoins.

If approved, the Aave DAO Treasury could generate revenue from staking rewards. Further, this would also allow the Aave DAO Treasury to participate in the veToken economy and attract additional users.

The purpose of this Snapshot is to garner community approval on the above recommended implementation and to signal approval for Balancer Pool Token (“BPT”) assets being the first accepted LP positions.

**Conclusion**

Ultimately, this could have a wide array of benefits for the Aave DAO and users of the Aave Protocol. For example, the Aave DAO could gain a n

====================================================================================================
[29] id=0xf4a0e440e08d44f45aa691d038fd40cf3e3306247610c061e633ebd6eb63df04  token=AAVE  space=aavedao.eth  date=2022-11-18
TITLE: [ARC] LDO Emission_Admin for Polygon v3 Liquidity Pool
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARC] LDO Emission_Admin for Polygon v3 Liquidity Pool
Author: @llamaxyz @MatthewGraham
Dated: 2022-11-05

---

# Simple Summary

In preparation for distributing incentives on the Aave v3 Polygon Liquidity Pool, @llamaxyz proposes amending the `Emission_Admin` address to enable the distribution of LDO rewards.

# Abstract

In collaboration with Lido, Llama seeks to distribute LDO incentives to the stMATIC Reserve on Polygon Aave v3. In order to achieve this, the `EmissionManager` contract needs to assign an owner to the `Emission_Admin` permission allowing LDO rewards to be distributed, [1,2]. This can only be achieved via the governance process.

This proposal assigns the `Emission_Admin` permission to LDO rewards to the following address `0x87D93d9B2C672bf9c9642d853a8682546a5012B5`. This address is controlled by Lido.

# Motivation

The motivation of the proposal is to enable LDO rewards to be distributed on the Polygon v3 Liquidity Pool.

# Specification

The Lido Liquidity Mining Committee determines the emission rate and duration at which LDO rewards are offered. Standard practice is for the council to meet and determine the next 30 days of LDO rewards on a rolling basis. This means each month, the committee will determine if to extend the LDO rewards, or change the amount of LDO being offered across the Polygon v3 Liquidity Pool.

The `Emission_Admin` is not limited to a specified Reserve and is linked to the token being distributed across the Liquidity Pool

====================================================================================================
[30] id=0x58c20dae66638085b5e834cd66ef560a34a71cad88cb1866fb9a726a1fb1861a  token=AAVE  space=aavedao.eth  date=2022-11-18
TITLE: [ARC] SD Emission_Admin for Polygon v3 Liquidity Pool
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARC] SD Emission_Admin for Polygon v3 Liquidity Pool
Staus: Proposal
Author: @llamaxyz @MatthewGraham
Dated: 2022-11-14

---

# Simple Summary

@llamaxyz proposed assigning the SD `Emission_Admin` role on the Aave v3 Polygon Liquidity Pool to a Gnosis Safe controlled by the Stader Labs.

# Abstract

The Stader Labs team intends to distribute SD incentives to the MaticX Reserve on Polygon Aave v3.

In order to achieve this, the `EmissionManager` contract needs to assign an owner to the `Emission_Admin` permission allowing SD rewards to be distributed, [1,2]. This can only be achieved via the governance process.

This proposal assigns the `Emission_Admin` permission to SD rewards to the following address `matic:0x51358004cFe135E64453d7F6a0dC433CAba09A2a`.

# Motivation

The motivation of the proposal is to enable SD rewards to be distributed on the Polygon v3 Liquidity Pool.

Please do note a similar request was submitted enabling the distribution of LDO and stMATIC rewards by Lido and the Polygon Foundation respectively across the Polygon Aave v3 liquidity pool, [3,4].

# Specification

The Stader Labs team will determine the emission rate and duration SD rewards are offered. This will likely be influenced by the Aave DAO’s ability to adjust the wMATIC and MaticX risk parameters that enable users to generate a return from leverage the MaticX / wMATIC loop.

The `Emission_Admin` is not limited to a specified Reserve and is linked to the token being distributed acro

====================================================================================================
[31] id=0x0a319a2b17cc04b804e74f71fb54c3c8a7c21f8c8925b9da72d92028be634bb2  token=AAVE  space=aavedao.eth  date=2022-11-21
TITLE: [ARC] stMATIC & MaticX Emission_Admin for Polygon v3 Liquidity Pool
CHOICES: YAE | NAR | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARC] stMATIC & MaticX Emission_Admin for Polygon v3 Liquidity Pool
Author: @llamaxyz @MatthewGraham
Dated: 2022-11-11

---

# Simple Summary

@llamaxyz proposed assigning the stMATIC and MaticX `Emission_Admin` role on the Aave v3 Polygon Liquidity Pool to a Gnosis Safe controlled by the Polygon Foundation.

# Abstract

The Polygon Foundation team intends to distribute stMATIC and MaticX incentives to the wMATIC Reserve on Polygon Aave v3.

In order to achieve this, the `EmissionManager` contract needs to assign an owner to the `Emission_Admin` permission allowing stMATIC and MaticX rewards to be distributed, [1,2]. This can only be achieved via the governance process.

This proposal assigns the `Emission_Admin` permission to stMATIC and MaticX rewards to the following address `0x0c54a0BCCF5079478a144dBae1AFcb4FEdf7b263`.

# Motivation

The motivation of the proposal is to enable stMATIC and MaticX rewards to be distributed on the Polygon v3 Liquidity Pool.

Please do note a similar request was submitted enabling the Lido community to distribute LDO rewards across the Polygon Aave v3 liquidity pool, [3].

# Specification

The Polygon Foundation team will determine the emission rate and duration at which stMATIC and MaticX rewards are offered. This will likely be influenced by the Aave DAO’s ability to adjust the wMATIC, stMATIC and MaticX risk parameters that enable users to generate a return from leverage the stMATIC / wMATIC and MaticX/wMATIC loop.

The `Emissi

====================================================================================================
[32] id=0x3f4a96dcf93b2d9c7cbfa6c1b627f995ed420e57492b333843783434588f4370  token=AAVE  space=aavedao.eth  date=2022-11-24
TITLE: Risk Parameter Updates for Aave V3 AVAX 2022-11-23
CHOICES: YAE | ABSTAIN | NAY
TEXT (first 1500 characters):
## Summary
A proposal to make parameter changes on Aave V3 AVAX. 

## Motivation

We recommend the following borrow caps for the Aave V3 AVAX Market. Borrow caps help prevent against high-risk attack vectors while sacrificing little capital efficiency. Our simulation analyses show that these borrow caps for these assets reduce the likelihood of market manipulation while allowing for natural organic borrow demand. As these markets naturally grow, we can continue to reassess raising caps incrementally.  

- FRAX borrow_cap: 2,000,000
- MAI borrow_cap: 2,000,000
- LINK borrow_cap: 220,000

## Specification

Set borrow caps on FRAX, MAI, and LINK on Aave V3 AVAX.



## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

*By approving this proposal, you agree that any services provided by Gauntlet shall be governed by the terms of service available at gauntlet.network/tos. This message is for informational purposes only and does not constitute an offer to sell, a solicitation to buy, or a recommendation for any security, nor does it constitute an offer to provide investment advisory or other services by Gauntlet Networks Inc. No reference to any specific security constitutes a recommendation to buy, sell or hold that security or any other security. Nothing in this report shall be considered a solicitation or offer to buy or sell any security, future, option or other financial instrument or to offer or provide any investmen

====================================================================================================
[33] id=0x4fd357741900bfe62a863d1e3ec84fbf79bfebd5bdda3f66eee75b8845274b6d  token=AAVE  space=aavedao.eth  date=2022-11-24
TITLE: Activation of a ParaSwap fee claimer contract
CHOICES: Yes, approve | No, don't approve | Abstain
TEXT (first 1500 characters):
## Summary
We ask for approval from the Aave community to deploy a smart contract to automate fee collection from the Aave <> ParaSwap features (repay with/swap collateral) to the protocol.

## Context
A detailed explanation on the rationale and how the system will work can be found on the Aave governance forum [HERE](https://governance.aave.com/t/bgd-aave-paraswap-fee-claimer/10671)

====================================================================================================
[34] id=0x194b68a5319b074065e38fcb0bd96e8e8b6ce15870844593e79750605a609109  token=AAVE  space=aavedao.eth  date=2023-01-06
TITLE: Updated: Aave Grants DAO Renewal
CHOICES: YAE | NAY
TEXT (first 1500 characters):
# Summary
We are proposing to renew Aave Grants DAO for the next two quarters by providing $3.25 million dollars ($1.625 million per quarter). This is the fourth proposal from Aave Grants DAO. Aave Grants DAO is a community-led grants program, focused on growing a thriving ecosystem of contributors within Aave through funding ideas, projects and events that benefit the ecosystem. We aim to drive development on top of Aave and ensure a constant influx of talented builders to maintain Aave’s long term growth. We help build culture and community around the Aave ecosystem that in turn attracts the best contributors.

# Proposal 
More details, including the factors that influenced the proposal, success stories, stats on AGD's grant distributions, and more can be found in our renewal post: https://governance.aave.com/t/updated-proposal-aave-grants-dao-renewal/11289

====================================================================================================
[35] id=0x2cb10cfb57a79bb97c3aed1cc3e9847227fb0f6a843916921ae315b9d8ad11d3  token=AAVE  space=aavedao.eth  date=2023-01-17
TITLE: [ARFC] CRV Interest Rate Curve Upgrade
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] CRV Interest Rate Curve Upgrade
Author: @Llamaxyz @MatthewGraham @dydymoon @scottincrypto
Dated: 2023-01-11

---

# Simple Summary

@Llamaxyz presents a proposal to update the CRV interest rate parameters on the Aave Ethereum v2, Ethereum v3 (when deployed), Polygon v3, and Polygon v2 Liquidity Pools.

# Abstract

The CRV Supply Cap on the Polygon v3 deployment is currently at 100% with borrowing costs of 7.18% with a Utilization of 44.48% relative to a 45% Uoptimal value, [1]. This proposal intends to increase the CRV Supply Cap on Polygon v3 deployment, improve the capital efficiency of each liquidity pool, and increase the amount of revenue generated across the various CRV reserves.

Capital efficiency is improved by increasing the Uoptimal value. Revenue is increased by introducing a Base interest rate, doubling the interest rate at the Uoptimal point, and aligning the Reserve Factor to 20% across all pools. This is expected to generate more revenue for the DAO and significantly reduce the amount of free CRV in aggregate across the Reserves.

# Motivation

With the CRV Reserve on Polygon reaching its Supply Cap, this is an ideal time to implement an upgrade that addresses the Supply Cap and Interest Rate parameters. The current CRV Interest Rate reflects the original parameters implemented when the liquidity pools were deployed. The Interest Rate Parameters do not take into consideration the alternative use cases for CRV and consequently, Aave has misse

====================================================================================================
[36] id=0x0ddd9784d8ac59ffcabc8ce86d2993179e044eeb102df1644b5b58d04ff25e63  token=AAVE  space=aavedao.eth  date=2023-01-30
TITLE: [ARFC] Add wstETH to Optimism Aave v3
CHOICES: YAE (with emode) | YAE (without emode) | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add wstETH to Optimism Aave v3
Discussion: https://governance.aave.com/t/arc-add-wsteth-to-aave-v3-on-optimism/10932
short description: Add wstETH to Optimism Aave v3 deployment as collateral with borrowing enabled. Create an Ethereum eMode.
author: Llama - Defi_Consulting
dated: 2023-01-29

---

# Summary

This ARFC presents the community with the opportunity to add wstETH to the Optimism V3 Liquidity Pool.

# Abstract

Across the Aave Liquidity Pools, stETH is listed on Aave v2 Ethereum and wstETH is listed on Aave v3 Ethereum. This proposal seeks to list wstETH on the Optimism Liquidity Pool as Collateral with Borrowing enabled.  

The stETH/wETH rewards-maximising loop on Aave v2 is the main source of borrowing demand for wETH and the wETH reserve generates a material portion of Aave’s revenue, more than $281k in January 2023. By listing wstETH on Optimism users will be able to enter the same recursive strategy creating borrowing demand for wETH and revenue for Aave.
 
The risk parameters have been provided by Gauntlet and Llama, with this post using the parameters agreed between the two service providers.

# Motivation

The stETH reserve on Aave v2 is the largest reserve across all Aave deployments with $1.55B in deposits, exceeding USDC ($0.83B) and ETH ($1.42B). This is partially due to several communities having built products that deposit stETH and borrow ETH as part of a rewards-maximising strategy. 

Demand for borrowing wETH on Aave v2 Ethereum

====================================================================================================
[37] id=0xc28c45bf26a5ada3d891a5dbed7f76d1ff0444b9bc06d191a6ada99a658abe28  token=AAVE  space=aavedao.eth  date=2023-02-01
TITLE: [ARFC] LDO Emission_Admin for Ethereum, Arbitrum and Optimism v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] LDO Emission_Admin for Ethereum, Arbitrum and Optimism v3 Liquidity Pools
Author: @llamaxyz - DeFi_Consulting
Dated: 2023-01-26

---

# Summary

This proposal is to enable Lido to distribute LDO rewards across the Aave v3 Ethereum, Arbitrum and Optimism Liquidity Pools. The `Emission_Admin` role for LDO on each network is to be assigned to a wallet controlled by the Lido DAO.

# Abstract

Lido seeks to distribute LDO rewards across to the various Aave v3 deployments. To achieve this, the `EmissionManager` function assigns an owner to the `Emission_Admin` role for LDO on each respective Aave v3 deployment, [1,2].

The wallet with `Emission Admin` permission for LDO on each aave v3 deployment then controls the distribution of only LDO rewards across the respective Liquidity Pool.

# Motivation

Enable Lido DAO to distribute LDO rewards across the Ethereum, Arbitrum and Optimism v3 Liquidity Pools.

The Lido Liquidity Mining Committee (LMC) determines the emission rate and duration at which LDO rewards are offered.

Typically, the LMC meets and determines the next 30 days of LDO rewards on a rolling basis. This means each month, the committee will determine if to extend the LDO rewards, or change the amount of LDO being offered across the various Aave v3 Liquidity Pools.

# Specification

The `EmissionManager`, a governance controlled function, assigns the `Emission_Admin` role for a specified token, LDO.

The `Emission_Admin` role controls the distribution of

====================================================================================================
[38] id=0x56aaf192f5cad8277b0e7c82abad030c62bb8fcfe4f2640ce5b896ab04397c20  token=AAVE  space=aavedao.eth  date=2023-02-05
TITLE: [ARFC] CRV Interest Rate Curve Upgrade
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] CRV Interest Rate Curve Upgrade
Author: @Llamaxyz - DeFi_Consulting, @dydymoon and @scottincrypto
Dated: 2023-01-11
Revised Date: 2023-01-31

---

# Simple Summary

@Llamaxyz presents a proposal to update the CRV interest rate parameters on the Aave Ethereum v2, Ethereum v3 (when deployed), Polygon v3, and Polygon v2 Liquidity Pools.

# Abstract

The CRV SupplyCap on the Polygon v3 deployment is currently at 100% with borrowing costs of 24.66% with a Utilization of 47.76% relative to a 45% Uoptimal value, [1]. This proposal intends to increase the CRV SupplyCap on Polygon v3 deployment, improve the capital efficiency of each liquidity pool, and increase the amount of revenue generated across the various CRV reserves.

Capital efficiency is improved by increasing the Uoptimal value. Revenue is increased by introducing a Base interest rate, increasing the Slope1 and aligning the Reserve Factor to 20% across all pools. This is expected to generate more revenue for the DAO and significantly reduce the amount of free CRV in aggregate across the reserves.

# Motivation

With the CRV reserve on Polygon reaching its SupplyCap, this is an ideal time to implement an upgrade that addresses the SupplyCap and Interest Rate parameters. The current CRV Interest Rate reflects the original parameters implemented when the liquidity pools were deployed. The Interest Rate Parameters do not take into consideration the alternative use cases for CRV and consequently, Aave has mis

====================================================================================================
[39] id=0x402647b83c436aecbe2fe404870f08767b5509225cbe606913e50801f87f5db8  token=AAVE  space=aavedao.eth  date=2023-02-05
TITLE: [ARFC] Add wstETH to Arbitrum Aave v3
CHOICES: YAE - with Ethereum eMode | YAE - without Ethereum eMode | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add wstETH to Arbitrum Aave v3
Discussion: https://governance.aave.com/t/arc-add-support-for-wsteth-on-arbitrum-aave-v3/11387
short description: Add wstETH to Arbitrum Aave v3 deployment as collateral with borrowing enabled and the option to create an Ethereum eMode.
author: Llama - Defi_Consulting
dated: 2023-02-05

---

# Summary

This ARFC presents the community with the opportunity to add wstETH to the Arbitrum v3 Liquidity Pool.

# Abstract

Across the Aave Liquidity Pools, stETH is listed on Aave v2 Ethereum and wstETH is listed on Aave v3 Ethereum. This proposal seeks to list wstETH on the Arbitrum Liquidity Pool as Collateral with Borrowing enabled.  

The stETH/wETH rewards-maximising loop on Aave v2 is the main source of borrowing demand for wETH and the wETH reserve generates a material portion of Aave’s revenue, $279k in January 2023. By listing wstETH on Arbitrum users will be able to enter the same recursive strategy creating borrowing demand for wETH and revenue for Aave.
 
The risk parameters have been provided by Gauntlet and Chaos Labs, with this post using the more conservative of the two risk service providers.

# Motivation

The stETH reserve on Aave v2 is the largest reserve across all Aave deployments with $1.56B in deposits, exceeding USDC ($0.81B) and ETH ($1.39B). This is partially due to several communities having built products that deposit stETH and borrow ETH as part of a rewards-maximising strategy. 

Demand for borrowing wETH

====================================================================================================
[40] id=0xda3519f11e2308239d5f179b2579fe921b2a421eb752aba959779ee9ecea0d69  token=AAVE  space=aavedao.eth  date=2023-02-09
TITLE: [ARC] Add LUSD to Ethereum V3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARFC] Add LUSD to Ethereum V3 Market

Author: @marczeller - Aave-Chan Initiative

Dated: 2023-01-31

# Simple Summary
This proposal presents Aave with the opportunity to onboard LUSD to the Ethereum v3 Liquidity Pool.

# Abstract
LUSD is a decentralized stablecoin minted by the Liquity protocol. For more details about LUSD please refers to [Aave V2 ARC by @TokenBrice ARC: Add support for LUSD (Liquity) 3)

This ARC is a joint effort with @Llamaxyz to allow a selection of assets to be onboarded on V3 via the governance process. Both Llama & ACI will propose AIPs on onboard assets on V3…

# Motivation
Supporting stablecoin diversity is part of the Aave-Chan Initiative (ACI) delegate platform.

The ACI does not have any link nor is paid by Liquity or any entity to present this ARC.

The risk parameters provided within are the same as those provided by Gauntlet within the initial forum post 1 discussing which assets to onboard to v3 Ethereum.

The Interest rate Strategy curve is the same than for LUSD in V2. for now the ACI is supportive to onboard LUSD as it was on V2, when the V3 will be more mature, the ACI is supportive to work on AIP to allow usage of LUSD as a collateral.

By presenting each asset to be onboarded to v3 Ethereum individually, the community can focus on a specific asset, with individual Snapshots determining how to proceed. Finally, approved assets listings can be grouped for the on-chain AIP vote.

# Specification
Ticker: LUSD

Contract Address: http

====================================================================================================
[41] id=0xe394799e4d006c15e0cb13155701de495888b7e7dad8f917a6b5dd1c8106cea5  token=AAVE  space=aavedao.eth  date=2023-02-14
TITLE: [ARFC] Add BAL Ethereum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add BAL Ethereum v3
Author: @Llamaxyz - DeFi_Consultants & @solarcurve (Balancer DAO)
Dated: 2023-01-31

---

# Summary

This proposal presents Aave the opportunity to onboard BAL to the Ethereum v3 Liquidity Pool.

# Abstract

BAL is a strategic asset to Aave and any BAL earned from the pool could be used by Aave to bootstrap the adoption of GHO and/or the new aToken being developed by @AaveCompanies.

The risk parameters provided within are the same as those provided by Gauntlet within the [initial forum post](https://governance.aave.com/t/arc-aave-v3-ethereum-deployment-assets-and-configurations/10238/22) discussing which assets to onboard to v3 Ethereum.

By presenting each asset to be onboarded to v3 Ethereum individually, the community can focus on a specific asset, with individual Snapshots determining how to proceed. Finally, approved assets listings can be grouped for the on-chain AIP vote.

# Motivation

Listing BAL as a priority for Aave v3 reflects the strategic relationship between the two communities. Balancer and Aave completed a [200,000 BAL for AAVE token swap](https://app.aave.com/governance/proposal/87/) and Aave later purchased an additional [100,000 BAL via a swap contract](https://app.aave.com/governance/proposal/115/). With the launch of [GHO ](https://governance.aave.com/t/gho-development-update/10267)getting closer and the [new aToken](https://governance.aave.com/t/arc-staked-atokens-a-new-aave-primitive-exploring-vote-escrow-econom

====================================================================================================
[42] id=0xa0b5336692735fb4288537646aec5819cb4cbf01fc3a8a7cb06c9e62db708055  token=AAVE  space=aavedao.eth  date=2023-02-14
TITLE: [ARFC] Add CRV to Ethereum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add CRV to Ethereum v3
Author:@Llamaxyz - DeFi_Consulting (@MatthewGraham), @dydymoon
Dated: 2023-02-01

---

# Summary

This proposal presents Aave the opportunity to onboard CRV to the Ethereum v3 Liquidity Pool.

# Abstract

CRV is a strategic asset to Aave and any CRV earned from the pool could be used by Aave to create veCRV for the purpose of bootstrapping the adoption of GHO, the new staked aToken being developed by @AaveCompanies and in the long term, might help incentivize the Safety Module too.

The risk parameters provided within are the same as those provided by Gauntlet within the [initial forum post](https://governance.aave.com/t/arc-aave-v3-ethereum-deployment-assets-and-configurations/10238/22) discussing which assets to onboard to v3 Ethereum.

By presenting each asset to be onboarded to v3 Ethereum individually, the community can focus on a specific asset, with individual Snapshots determining how to proceed. Finally, approved assets listings can be grouped for the on-chain AIP vote.

# Motivation

Listing CRV on Aave v3 Ethereum compliments the community's recent on-market purchase of CRV to [repay the excessive debt](https://governance.aave.com/t/arfc-repay-excess-crv-debt-on-ethereum-v2/10955) created on v2 Ethereum. CRV is a material contributor to Aave’s revenue through the continual borrowing demand for CRV. Month on Month revenue has fallen significantly as a result of disabling borrowing on the Ethereum v2 deployment.

![|602x361](

====================================================================================================
[43] id=0x7fe7d372601aa2864cbe21071bd2fda10bf22aa8f66076db276818a2d6808bef  token=AAVE  space=aavedao.eth  date=2023-02-16
TITLE: [ARFC] Freeze BUSD on Aave V2
CHOICES: YAE (Freeze BUSD) | NAY | ABSTAIN
TEXT (first 1500 characters):
title: [ARFC] Freeze BUSD on Aave V2

Author: @marczeller - Aave Chan Initiative

Dated: 2023-02-13

Summary
Following the recent developments between Paxos (minter of BUSD) and the SEC,

Paxos will stop minting BUSD From the 21st of February 2023, and will only allow redemption for their underlying value by burning BUSD.

The circulating supply of BUSD will thus trend toward zero over time.

This ARFC presents the Aave governance with the opportunity to freeze BUSD reserve on the Aave V2 Ethereum market.

Abstract
This ARFC proposes to freeze the BUSD reserve on the Aave V2 Ethereum market.

Motivation
While BUSD is not an asset with borrowing power, and recent development does not present risks of excess debt, From the 21st of February 2023, the circulating supply of this asset will eventually go toward zero.

As there’s no real prospect of growth and the inability to mint new BUSD might hurt peg arbitrage opportunity and asset peg. It seems that the most reasonable path for Aave is to freeze this reserve and invite users to switch to another stablecoin among the diversity present in Aave.

As there’s no immediate risk for the protocol, the ACI doesn’t call for a fast-track process for this ARFC, and the standard governance process seems fit.

Specification
Ticker: BUSD (BUSD)

Contract Address: 0x4Fabb145d64652a948d72533023f6E7A623C7C53

Disclaimer
The Aave-Chan Initiative is not linked to nor paid by Binance/Paxos to publish this ARFC

Copyright
Copyright and related righ

====================================================================================================
[44] id=0x15a031fa5f848aac269214a7cda2fed314590ab0c935b6879e4bf7fb9d87cc2c  token=AAVE  space=aavedao.eth  date=2023-02-23
TITLE: ARC Spark Lend Profit Share Proposal
CHOICES: Entire profit share direct payme | Split between direct payment and | Reject | Abstain
TEXT (first 1500 characters):
The newly proposed Phoenix Labs, an R&D company building the Spark Protocol upon the foundations of the Aave v3 codebase to deploy Spark Lend, a liquidity protocol centered around DAI.

We propose a profit sharing of 10% of the gross profits (cost paid to DAI suppliers subtracted from the revenue generated by DAI borrows) from the DAI market in Spark Lend.

The profit share will take effect when the DAI market size reaches 100 million and will expire two years later.

- DAI market = portion of the pool with underlying asset ERC-20 DAI
- Profit = Gross Profit = Revenue - COGS
- Revenue (B) = revenue from borrows in the DAI market
- COGS (S) = Cost of Capital = amount paid to suppliers in the DAI market
- Profit share = 10%
- Minimum DAI borrows = 100 million DAI
- Duration = 2 years after reaching minimum DAI borrows

Profit share paid to Aave = 10% * (B - S)

We want to present two options for the Aave community to consider. The latter splits a minority of the profit share to purchase AAVE tokens to align both organizations further.

1. Entire profit share direct payment in DAI to the Aave Treasury at address `0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c`
2. Split between direct payment and purchase of AAVE
    1. 8% profit share direct payment to the Aave Treasury at address `0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c`
    2. 2% profit share used to purchase AAVE tokens held in the Spark Protocol Treasury

====================================================================================================
[45] id=0xff69be7580614ebc1a455591c1bd651d8f0af12070d277d7d8846beb3c7c964b  token=AAVE  space=aavedao.eth  date=2023-03-01
TITLE: [ARFC] Proposal for Deploying “Whitelabel” Aave V3 Market for RealT Tokens on GnosisChain
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
—
Title: [ARFC] Proposal for Deploying “Whitelabel” Aave V3 Market for RealT Tokens on GnosisChain

Author: @marczeller - Aave Chan Initiative

Date: 2023-02-15

—
Summary:
Realt is a Real Estate tokenization protocol that enables users to gain exposure to real estate properties that produce rent income directly paid on-chain. The RMM (RealT Market Maker) market based on Aave V2 has already reached ~10M$ in size since its launch.

This ARFC proposes deploying a “whitelabel” version of Aave V3 for RealT tokens on the Gnosis Chain network. By allowing friendly forks of Aave V3, Aave can increase its technology adoption and provide an alternative source of revenue and synergies for the DAO and third-party teams.

Motivation:
The quality of the Aave V3 codebase has made it a recognizable and trustworthy asset in the DeFi community as illustrated by spark protocol recent ARC 7.

Therefore, rather than “reinventing the wheel,” many projects are interested in deploying “friendly” forks of V3 that fit their own models.

Aave is currently “delegating” off-chain collaterals to third parties, such as the Centrifuge RWA market, but this might change mid-term with GHO and off-chain collateral facilitators.

At present, Aave is immature in this area, so allowing third parties to deploy these “friendly forks” or Aave whitelabel deployments can increase Aave technology adoption.

RealT proposes a 20% profit-sharing arrangement with the Aave DAO for this deployment. In this context, “profit”

====================================================================================================
[46] id=0x4bbd4dc6928b3d341381c5ba25cf9dfa41386229706832c627aef300963f5864  token=AAVE  space=aavedao.eth  date=2023-03-01
TITLE: Supply and Borrow Cap Updates - Aave V3 Avalanche
CHOICES: Conservative | Aggressive  | NAY | Abstain
TEXT (first 1500 characters):
## Simple Summary

A proposal to adjust: Twenty  (20) total  Supply and Borrow Caps across eleven (11) assets on Aave V3 Avalanche

## Motivation

The objective of this proposal is to recommend updated supply and borrow caps for:

1. **V3 Avalanche stablecoins that have excessive supply caps set and/or have no set borrow cap.** 
    1. The caps are intended to allow for substantial growth compared to the current supply while not set too excessively.
    2. The recommendations for the supply caps are set to up to 40% of the circulating supply for most assets and no more than 60%. You can find the exact number for each asset in the tables below. Borrow caps are set to ~65% of the supply cap.
2.  **Assets that have reached over 75% utilization of either cap.** 
    1. The recommendations provided in this proposal were derived using Chaos Labs’ [Updated Supply and Borrow Cap Methodology](https://governance.aave.com/t/chaos-labs-updated-supply-and-borrow-cap-methodology/11602). 
3. Assets with a supply cap that is >50% of the asset's total on-chain circulating supply.

![Screen Shot 2023-03-01 at 3.17.41 PM.png](ipfs://bafkreieihskcllnrajnnmjmo4ijx2x2c3trap2slx7evrgd2w5xz7sk7wi)
      

![Screen Shot 2023-03-01 at 3.12.18 PM.png](ipfs://bafkreid4nqtrnut37ukm2dsr5tbpgcvcgtssuoqbngpf35yfpruroxbh3u)

====================================================================================================
[47] id=0xf4aec3fbab5096752be96f0e5b522f37318c1902cf8b897b049b7a94d478de73  token=AAVE  space=aavedao.eth  date=2023-03-07
TITLE: [ARFC] Add MKR to Ethereum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Add MKR to Ethereum v3
Author: @Llamaxyz - DeFi_Consulting (@matthewgraham), ACI (@MarcZeller) and 3SE
Dated: 2023-02-18

---

# Summary

This proposal presents Aave the opportunity to onboard MKR to the Ethereum v3 Liquidity Pool.

# Abstract

MKR is the governance token of the Maker DAO ecosystem. MKR token holders govern the Maker Protocol, the smart contracts that power DAI. There is currently $12.71m of MKR deposited into Aave v2 on Ethereum. This proposal grants Aave the opportunity to list the governance token of the community supporting DAI which contributes $167m of TVL on the Ethereum v2 deployment.

This ARFC is a joint effort with ACI and 3SE to allow a selection of v2 listed assets to be onboarded on V3 via the governance process. Subject to a favourable Snapshot vote, Llama will submit an AIP for voting.

# Motivation

Maker DAO has over $7.45B in TVL and is ranked second on Defi Llama TVL rankings. The Maker Protocol is only deployed on the Ethereum network. The stable coin DAI, provides $167m of deposits into Aave v2 on Ethereum, with over $103m of this supply being borrowed by users.

The risk parameters provided here within are from Gauntlet’s original Aave v3 initial [assets listings and configurations](https://governance.aave.com/t/arc-aave-v3-ethereum-deployment-assets-and-configurations/10238/22) forum thread. These parameters are to be revised by Gauntlet and feedback will be incorporated before progressing to a Snapshot vote.

The in

====================================================================================================
[48] id=0x5f232a89e10d67df3aad2907e8dce3bec9708596929b3254055cf37499969b89  token=AAVE  space=aavedao.eth  date=2023-03-07
TITLE: [ARFC] Add SNX to Ethereum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Add SNX to Ethereum v3
Author: @Llamaxyz - DeFi_Consulting (@matthewgraham), ACI (@MarcZeller) and 3SE
Dated: 2023-02-18

---

# Summary

This proposal presents Aave the opportunity to onboard SNX to the Ethereum v3 Liquidity Pool.

# Abstract

Synthetix is financial primitive enabling the creation of synthetic assets, offering unique derivatives and exposure to real-world assets on the blockchain. SNX was originally listed on Aave v1 and included on Aave v2 when it was launched in late 2020.

Adding SNX to Aave v3 will enable users to migrate from v2 to v3, $10.5m, and enable Aave to continue generating SNX nominated revenue. SNX is not currently listed on either the USDC or ETH Compound v3 liquidity market.

This ARFC is a joint effort with ACI and 3SE to allow a selection of v2 listed assets to be onboarded on V3 via the governance process. Subject to a favourable Snapshot vote, Llama will submit an AIP for voting.

# Motivation

Synthetics has $435m of TVL and is [ranked 25](https://defillama.com/) on the Defi Llama dashboard. Aave has generated over $205,000 in revenue from users who borrow SNX on Aave v2. SNX is one of the few non stable coin tokens with significant borrowing demand.

The risk parameters provided here within are from Gauntlet’s original Aave v3 initial [assets listings and configurations](https://governance.aave.com/t/arc-aave-v3-ethereum-deployment-assets-and-configurations/10238/22) forum thread. These parameters are to be revised b

====================================================================================================
[49] id=0x51d67ef69e901b34f1d111f2cd5d582c59cffa8d70b7939023febd20f7613b88  token=AAVE  space=aavedao.eth  date=2023-03-07
TITLE: [ARFC] Add UNI to Ethereum v3
CHOICES: YEA | NAE | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Add UNI to Ethereum v3
Author: @Llamaxyz - DeFi_Consulting (@matthewgraham), ACI (@MarcZeller) and 3SE
Dated: 2023-02-18

---

# Summary

This proposal presents Aave the opportunity to onboard UNI to the Ethereum v3 Liquidity Pool.

# Abstract

The UNI token is the governance token of the Uniswap ecosystem and is a DeFi bluechip. UNI was one of the first governance tokens to be integrated into the Aave ecosystem when it was listed on v1 and was included on Aave v2 when it was launched in December 2020.

This ARFC is a joint effort with ACI and 3SE to allow a selection of v2 listed assets to be onboarded on V3 via the governance process. Subject to a favourable Snapshot vote, Llama will submit an AIP for voting.

# Motivation

Uniswap is a DEX with $4.18B in TVL, second only to Curve Finance with $5.06B, according to Defi Llama’s data. Uniswap is deployed on five networks. UNI provides Aave v2 with $15.86m of TVL. Something to note, it is possible with Aave v3 to delegate Aave’s UNI reserve holding governance influence to an address which can be used for voting on Uniswap proposals.

The risk parameters provided here within are from Gauntlet’s original Aave v3 initial [assets listings and configurations](https://governance.aave.com/t/arc-aave-v3-ethereum-deployment-assets-and-configurations/10238/22) forum thread. These parameters are to be revised by Gauntlet and feedback will be incorporated before progressing to a Snapshot vote.

The interest rate provide

====================================================================================================
[50] id=0xd8a400fc731b6e807f4d89aa1fa47225f0dfaaa8fc49ef04b46b11b98fbfa15f  token=AAVE  space=aavedao.eth  date=2023-03-07
TITLE: [ARFC] Grant OP Emission_Admin for Optimism v3 Liquidity Pool to Lido DAO
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Grant OP Emission_Admin for Optimism v3 Liquidity Pool to Lido DAO
author: @Llamaxyz , DeFi_Consulting (@MatthewGraham )
created: 2022-02-15

---

# Summary

This proposal is to enable Lido DAO to distribute OP rewards across the Aave v3 Optimism Liquidity Pool.

The `Emission_Admin` role for OP on Optimism is currently assigned to the Optimism team and is to be transferred to Lido DAO.

# Abstract

Lido seeks to distribute OP rewards across to the Aave v3 Optimism deployment. To achieve this, the `EmissionManager` function reassigns an owner to the `Emission_Admin` role for OP, [1,2].

The wallet with `Emission Admin` permission for OP then controls the distribution of OP and LDO rewards on the Optimism Liquidity Pool. This proposal will enable LDO and OP rewards to be distributed across the Optimism v3 deployment. 

# Motivation

Enable Lido DAO to distribute OP rewards across the Optimism v3 Liquidity Pools.

Lido DAO is about to receive a grant nominated in OP tokens that are to be used for bootstrapping the adoption of wstETH on the Optimism network. 

The Lido Liquidity Mining Committee (LMC) will be determining the emission rate and duration that OP rewards are offered on the Aave v3 deployment.

Typically, the LMC meets and determines the next 30 days rewards to be distributed on a rolling basis. This means each month, the committee will determine if to extend the OP rewards, or change the amount of OP being offered across the Aave v3 Liquidity Pool

====================================================================================================
[51] id=0x05182d6092e7a075b94ab937a6cd57968f36c6ac225196561a58b437e591065f  token=AAVE  space=aavedao.eth  date=2023-03-13
TITLE: [ARFC] Deploy BAL & aBAL from the Collector Contract
CHOICES: YAE - Locking veBAL | YAE - Staking auraBAL | NAE | ABSTAIN
TEXT (first 1500 characters):
---

[ARFC] Deploy BAL & aBAL from the Collector Contract
Author: @llamaxyz - DeFi_Consulting (@MatthewGraham) and @dydymoon
Created: 2023-02-05 (updated)

---

# Simple Summary

This proposal presents two options for deploying the approximately 100k BAL tokens being acquired by AIP 115 and the aBAL holding in the Ethereum Collector Contract, [1].

# Abstract

AIP 115 has been successfully implemented and Aave has acquired an additional 100k BAL on market. The total BAL and aBAL holding is now 308,978.30. With 200k BAL already committed to veBAL, this proposal will determine how to deploy the remaining 108,978.30 BAL with the overall objective of maximizing the growth potential of Aave, [4,16].

Aave Snapshot voters can choose between two options, each of which has varying degrees of complexity and represents different means of achieving similar goals over different time horizons.

Option 1) Locking veBAL.
Option 2) Staking auraBAL.

Option 1) is about locking B-80BAL-20WETH enabling Aave to participate in Balancer gauge and governance votes, and benefit from the Liquidity Provider (LP) boosting and protocol fees earnings.

Option 2) focuses on yield, forgoes governance influence (participating in votes) and presents a higher yield investment strategy that over time, will lead to more governance influence relative to Option 1).

A Snapshot will be posted enabling the community to choose between both options. Llama recommends voting for Option 1).

# Motivation

This BAL holdi

====================================================================================================
[52] id=0x1b816c12b6f547a1982198ffd0e36412390b05828b560c9edee4e8a6903c4882  token=AAVE  space=aavedao.eth  date=2023-03-14
TITLE: [ARFC] Migrate & Consolidate Polygon Treasury
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Migrate & Consolidate Polygon Treasury
author: @llamaxyz
created: 2023-03-11

---

# Summary

Llama proposes consolidating and migrating funds held in the Polygon v2 Collector Contract to the v3 Treasury.

# Abstract

The Polygon Aave v2 Collector Contract has accumulated holdings in several long tail assets over time. 

This proposal seeks to acheive the following:

* Transfer - Assets from v2 Collector Contract to v3 Treasury
* Consolidation - Swap GHST, JEUR, SUSHI, and DPI for USDT 

# Motivation

## Collector Contract

The image below shows an overview of the current Collector Contract holdings.

![](https://i.imgur.com/0LJCw1i.png)

Address: `matic:0x7734280A4337F37Fbf4651073Db7c28C80B339e9`

|Deployment|Ticker|Price|Quantity|USD Value|
|---|---|---|---|---|
|Aave V2|amUSDC|$1.00|3,700,350.15| $ 3,700,350.15 |
|Aave V2|amDAI|$1.00|3,350,246.64| $ 3,350,246.64 |
|Aave V2|amUSDT|$1.00|1,337,100.44| $ 1,337,100.44 |
|Aave V2|amWETH|$1,380.00|226.39| $ 312,418.20 |
|Aave V2|amWMATIC|$0.99|95,223.15| $ 94,270.92 |
|Aave V2|amBAL|$5.51|1,125.41| $ 6,201.01 |
|Aave V2|amGHST|$1.35|1,916.02| $ 2,586.63 |
|Aave V2|amCRV|$0.83|7,936.95| $ 6,587.67 |
|Aave V2|amWBTC|$19,750.00|0.03| $ 620.56 |
|Aave V2|amLINK|$6.07|31.72| $ 192.54 |
||||Total| $ 8,810,574.75 |

Address: `matic:0x7734280A4337F37Fbf4651073Db7c28C80B339e9`

## Treasury Contract

![](https://i.imgur.com/A3pLSSs.png)

|Deployment|Ticker|Price|Quantity|USD Value|
|---|---|---|---|---|
|Aave V3|aPolWMA

====================================================================================================
[53] id=0x22eb6c5cdaf3731d4d6e0f4bb179e4cf6fa87470e87323f373f0bb01baceb9af  token=AAVE  space=aavedao.eth  date=2023-03-24
TITLE: [TEMP CHECK] Aave Chan Initiative 6-Month Budget Proposal
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## **Introduction**

The Aave Chan Initiative (ACI) is a delegate platform dedicated to actively participating in Aave governance and contributing to the protocol's success. As the Aave ecosystem matures, it is essential to have diverse and independent delegate platforms to drive the protocol forward.

To continue our efforts and effectively serve the Aave community, we are seeking a 6-month budget allocation. This budget will support our ongoing initiatives and enable us to expand our team and resources for maximum impact.

## **ACI's current & future areas of focus**

1. **Governance and AIP Development**
    - Active participation in Aave governance discussions & votes
    - Developing and submitting snapshot votes & AIPs
    - Engaging with the community on forum discussions
    - Collaborating with other delegates and stakeholders
2. **Treasury Efficiency and Management**
    - Collaborate with DAO service contributors, such as Llama, to enhance Aave DAO treasury management.
    - Support initiatives and actively participate in efforts to improve treasury efficiency, led by Llama and other contributors.
    - Drive the adoption of strategic investments, diversification, and risk mitigation in treasury allocation.
    - Establish a cost-conscious culture and ensure responsible spending from the treasury for the benefit of the Aave protocol and its users.
3. **Protocol and Ecosystem Development**
    - Support the onboarding of new stablecoins, strategic assets, and LSDs

====================================================================================================
[54] id=0x0777eb4701023508c03825e2779e6189326ed9b3d1eb6e187d1f6e0f8d154605  token=AAVE  space=aavedao.eth  date=2023-03-25
TITLE: [ARFC - Temp check] “MVP” V3 deployment on ZkEVM mainnet
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
- --

title: [ARFC - Temp check] “MVP” V3 deployment on ZkEVM mainnet

Author: @marczeller - Aave Chan Initiative 

Dated: 2023-03-02

- --

# **Summary**

ZkEVM is an EVM-equivalent zk-rollup L2 developed by the Polygon team that is expected to be deployed on March 27th.

Aave V3 has been successfully deployed on the ZkEVM testnet for approximately 6 months (since October 2022). This testnet deployment was done for testing purposes by the @AaveCompanies team.

Since ZkEVM is EVM-equivalent, deploying Aave V3 would require minimal development work.

The Aave-Chan Initiative supports L2 diversity as part of its governance platform.

This minimal Aave V3 deployment, with strictly limited assets onboarding (”MVP V3”), can be an opportunity to establish a strategic Aave presence early in this new network while staying conservative in terms of risk.

This ARFC proposal should be considered as a "temperature check" that would allow development and risk service providers to conduct a deeper analysis of the zkEVM network.

# **Abstract**

This ARFC presents the Aave governance with an opportunity to “temp check” the deployment of a MVP version of Aave V3 on the ZkEVM L2.

# **Motivation**

The proposal to deploy Aave V3.0.1 on the ZkEVM L2 network, also known as "MVP V3," presents an opportunity for Aave Governance to establish a strategic presence on this new network early on. Aave has a history of pioneering in new frontiers, starting with the Polygon & Avalanche V2 deployment in

====================================================================================================
[55] id=0x953f0edc544fe50e68a0aa19d31542d15458bc3394478a31a294f748198fa906  token=AAVE  space=aavedao.eth  date=2023-03-26
TITLE: [ARFC] Add LDO to Ethereum Aave v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
shortDescription: Add LDO to Ethereum Aave v3 deployment as collateral, with borrowing enabled.
author: [Token Logic](https://twitter.com/Token_Logic) via [Llama](https://twitter.com/llama)
dated: 2023-03-26

# Summary

This ARFC presents the community with the opportunity to add LDO to the Ethereum V3 Liquidity Pool.

# Abstract

LDO would be the first Ethereum liquid staking protocol governance token to be listed on Aave. Aave would benefit from being the first major lending market to list LDO. Users will be able to express various trading views on LDO’s price outlook in the lead up to Shanghai.
 
The risk parameters have been provided by Gauntlet and Chaos Labs, with this post using the parameters agreed between the two service providers.

# Motivation

Lido is a suite of software protocols that facilitates liquid staking across multiple blockchains. The Lido DAO is a decentralised autonomous organisation. The LDO token is used to vote on the use of the DAO treasury associated with the protocols, research and development, and incentive programs.

The Lido DAO is an Aragon organization. The LDO token was created using an [Aragon Minime contract](https://aragon.org/dao). Since Aragon provides a full end-to-end framework to build DAOs, Lido DAO uses its standard tools.

LDO Token Ethereum Address: `0x5a98fcbea516cf06857215779fd812ca3bef1b32`

LDO is a Top 50 token by market cap, currently ranked [36th](https://www.coingecko.com/en/coins/lido-dao) by Coingecko. Lido Protocol i

====================================================================================================
[56] id=0x9d7296b06a66d6d6b4c9e85051477a4d62d066e3f56c248bcc85cbea00f7c7a4  token=AAVE  space=aavedao.eth  date=2023-03-26
TITLE: [TEMP CHECK] Add support for wstETH on Polygon v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
# Proposal: Add support for wstETH on Polygon v3

![](https://i.imgur.com/iMAkAXa.png)

## References

Project: https://lido.fi/
Whitepaper: https://github.com/lidofinance/lido-dao/blob/master/README.md
Github: https://github.com/lidofinance/polygon-contracts
Documentation: https://docs.lido.fi/
Audit: https://github.com/lidofinance/polygon-contracts/tree/main/audits/v2
wstETH: https://polygonscan.com/token/0x03b54a6e9a984069379fae1a4fc4dbae93b3bccd
Chainlink: https://polygonscan.com/address/0x10f964234cae09cB6a9854B56FF7D4F38Cda5E6a
Governance: https://research.lido.fi/
Twitter: https://twitter.com/LidoFinance
Discord: https://discord.com/invite/vgdPfhZ

# Summary

This ARFC presents the community with the opportunity to add wstETH to the Polygon v3 Liquidity Pool.

# Motivation

The stETH Reserve on Aave v2 is the largest Reserve across all Aave deployments with $1.52B in deposits, exceeding USDC ($0.99B) and ETH ($1.16B). On Aave v3, the most recent Aave deployment, wstETH provides $130M or 29% of markets TVL.

Several communities building on Aave utilize the wstETH/wETH rewards-maximizing strategy to generate rewards on various assets. By adding wstETH to the Polygon v3 market, users gain access to a third Liquid Staking Token (LST) source of rewards. 

The demand for wETH on Aave has increased as a result of listing stETH on Aave v2. This led to a material increase in Aave’s wETH nominated revenue stream. Listing wstETH across various Aave deployments, has enabled Aave t

====================================================================================================
[57] id=0xf92c5647c7f60a4a3db994b4953fc4408f5946cafdc0cebcd4c5924f40e04d36  token=AAVE  space=aavedao.eth  date=2023-03-26
TITLE: [ARFC] Deploy aCRV & CRV to veCRV
CHOICES: YAE - veCRV | YAE - st-yCRV | YAE - sdCRV | NAE | ABSTAIN
TEXT (first 1500 characters):
- - -

title: [ARFC] Deploy aCRV & CRV to veCRV
author: @llamaxyz - TokenLogic & @Dydymoon 
date: 2023.02.09

- - -

# Simple Summary

This proposal presents Aave with thr options for managing the CRV holding, with @Llamaxyz recommending to lock the CRV for veCRV via Curve Finance.

# Abstract

Aave currently holds approximately 696k CRV across Ethereum and Polygon networks. Llama has been looking at potential sources for CRV yield and governance influence. This proposal presents one high yield and one governance focused strategy for consideration:

Option 1) veCRV - Lowest risk, governance and direct control CRV emissions
Option 2) st-yCRV - High yield, no CRV emission influence and exit liquidity risk
Option 3 ) sdCRV - High yield, proportional CRV emission influence and exit liquidity risk

To vote NAE is to deposit CRV in Aave v3 on the network it was earned. This represents the “do nothing” approach.

A Snapshot vote presenting the three options will determine which options will be presented as an AIP. Each option has varying degrees of complexity to implement, with Option 1) being the most difficult in a decentralized way, but more closely aligned with Aave’s GHO and staked aToken direction.

# Motivation

Aave currently holds 696k of CRV across Ethereum and Polygon networks. 

To support Aave in choosing how best to manage the CRV holding, Llama presents three high-level strategies to choose between.

## Option 1) veCRV - Lowest risk, governance and direct control CRV

====================================================================================================
[58] id=0x4579b562a4ea07c52871f724a8baf156514a97384e9427156d04fb6f0ae91515  token=AAVE  space=aavedao.eth  date=2023-03-28
TITLE: [TEMP CHECK] Aave V3 deployment on BNB Chain
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
- --
**Title:** [TEMP CHECK] Aave V3 deployment on BNB Chain.

**Author:** @marczeller - Aave-Chan Initiative

**Date:** 2023-03-22
- --

## **Simple Summary**

This Temperature Check seeks community input on the possibility of deploying Aave V3 on the BNB Chain to expand Aave's presence and tap into BNB Chain's growing DeFi ecosystem and user base.

## **Background**

BNB Chain is a thriving blockchain with a strong DeFi ecosystem and a large user base. With a TVL of approximately $5 billion, BNB Chain is the third-largest chain by TVL. The chain has a diverse array of DeFi offerings, including prominent projects like PancakeSwap, Venus, and several others. Deploying Aave V3 on BNB Chain could provide opportunities for growth and collaboration between the Aave and BNB Chain communities.

## **Motivation**

Deploying Aave V3 on BNB Chain has the potential to benefit both Aave and BNB Chain ecosystems. Aave would gain access to BNB Chain's user base, DeFi ecosystem, and the potential for additional revenue. BNB Chain would benefit from having a flagship DeFi project like Aave on its platform, further diversifying DeFi options available to its users.

## **Specification**

This TEMP CHECK presents the Aave governance with the opportunity to deploy Aave V3 on the BNB Chain with a selection of suitable assets for collateral, including BNB, WBTC, BETH, WETH, USDC, and USDT. Suggested risk parameters for each asset are provided in the table below. The ACI invites risk service provi

====================================================================================================
[59] id=0xea8b9cc41076ba43c8a66dfd40ce539b3126af049639babce6c1fa3e62585b79  token=AAVE  space=aavedao.eth  date=2023-03-30
TITLE: [TEMP CHECK] - Aave DAO's $ARB Airdrop Allocation
CHOICES: Keep the $ARB | Do LM program | Sell the $ARB | Mixed option, discuss at [ARFC] | NAY | ABSTAIN
TEXT (first 1500 characters):
**Title:** [TEMP CHECK] - Aave DAO's $ARB Airdrop Allocation

**Author:** @marczeller - Aave-Chan Initiative

**Date:** 2023-03-22

## **Simple Summary**

This Temperature Check discusses the potential options for the Aave DAO's allocation of 2.7 million $ARB tokens received from the Arbitrum L2 airdrop. We propose four options for the community to consider and provide feedback on.

## **Background**

The Aave DAO is set to receive [an airdrop of ~2.7 million $ARB tokens](https://twitter.com/ArbitrumNewsDAO/status/1638212694712143872?s=20) from the Arbitrum L2. We are seeking community input on the best course of action for utilizing these tokens to benefit the Aave ecosystem.

## **Options for $ARB Token Allocation**

1. Keep the tokens and participate in Arbitrum governance as the Aave DAO: This option involves holding onto the $ARB tokens and using them to actively participate in Arbitrum governance, thereby contributing to the development and decision-making of the Arbitrum L2 ecosystem.
2. Use the tokens to fund a Liquidity Mining program to support the growth of Aave V3 Arbitrum Market: This option would allocate the $ARB tokens towards a Liquidity Mining program designed to incentivize users to participate in the Aave V3 Arbitrum Market, promoting growth and adoption of Aave on the Arbitrum L2.
3. Sell the tokens for stablecoins or ETH to support the Aave DAO treasury: This option involves converting the received $ARB tokens into stablecoins or ETH, which would bolster

====================================================================================================
[60] id=0xc3c8768fa4bbdc12eea40c6cdd0d3d9f61847142a37b17cafcab3fdac7ce32d2  token=AAVE  space=aavedao.eth  date=2023-04-11
TITLE: [ARFC] Align AAVE Risk Parameters on Aave V3 Ethereum Market with Aave V2
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
title: [ARFC] Align AAVE Risk Parameters on Aave V3 Ethereum Market with Aave V2
Author: @Marczeller - Aave-Chan Initiative
Date: 2023-04-05

## **Summary**
This Aave Request for Comments (ARFC) proposes the alignment of the AAVE risk parameters on the Aave V3 Ethereum market with those on Aave V2, as the current parameters on Aave V3 are less attractive for users considering migration. By matching the Aave V2 parameters, we aim to encourage migration and ensure a smoother transition for users. This proposal does not suggest any changes to Aave V3 caps or interest rate strategies.

### **Proposed Aave V3 Parameter Changes**
To make Aave V3 more attractive for migration and to match Aave V2 parameters, we propose the following changes:

1. Loan-to-Value (LTV): Increase the LTV from 60% to 66%.
2. Liquidation Threshold (LT): Increase the LT from 70% to 73%.
3. Liquidation Penalty (LP): Maintain the current LP of 7.5%, as it is already in alignment with Aave V2.

No changes to Aave V3 caps or interest rate strategies are proposed in this ARFC.

### **Recap Table**
| Parameter                | Current Aave V3 | Current Aave V2 | Proposed Aave V3 |
|--------------------------|-----------------|-----------------|------------------|
| Loan-to-Value (LTV)      | 60%             | 66%             | 66%              |
| Liquidation Threshold (LT)| 70%             | 73%             | 73%              |
| Liquidation Penalty (LP)  | 7.5%            | 7.5%            | 7.5%             |

====================================================================================================
[61] id=0x46cf72da892eb216edc1b7fe2f24f7491d8c37344b2b1f67632fa6950be034f7  token=AAVE  space=aavedao.eth  date=2023-04-11
TITLE: [TEMP CHECK] Aave V3 Deployment on zkSync Era Mainnet
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Aave V3 deployment on zkSync Era Mainnet

Author: @fig - Flipside Crypto

Date: 2023-03-26

---

## Simple Summary
This Temperature Check seeks community input for the opportunity to deploy Aave V3 on the zkSync Era Mainnet, expanding Aave’s presence and tapping into the growing zkEVM ecosystem.

## Background
zkSync is a zk rollup, a trustless protocol that uses cryptographic validity proofs to provide scalable and low-cost transactions on Ethereum. zkSync Era is made to look and feel like Ethereum, but with lower fees. Era empowers users with more security and embeds into the familiar infrastructure and ecosystem of EVM.

zkSync Era has launched with a diverse array of DeFi offerings, listed in its ecosystem documents – and others on the way. Deploying Aave V3 on zkSync Era could provide opportunities for growth and collaboration between the Aave and zkSync communities.

Era provides key EVM features, such as smart contract composability - leading to easier deployment of Aave V3 and requiring minimal development work.

## Motivation
The Aave community has previously voted to deploy the Aave V3 codebase on zkSync’s v2 Testnet, approved by this off-chain vote. With the release of Era Mainnet, it is possible to re-invest the work of developers, empowering Aave as a hub for mainnet activity and liquidity.

zkSync has the potential to benefit the Aave ecosystem by introducing new users into DeFi, and cementing Aave as the premier borrowing platform withi

====================================================================================================
[62] id=0xb5a684d8294e3978001eafd80a6096e3f9b8e925879f83e9ea67a03644877a50  token=AAVE  space=aavedao.eth  date=2023-04-24
TITLE: [TEMP CHECK] Gas Fee Rebate for On-Chain Votes
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## ***Summary***

The London Business School (LBS) Blockchain Society, in alliance with Flipside Governance (@fig), FranklinDAO (@PennBlockchain), the University of Michigan (@Michigan_Blockchain), and Columbia University (@BlockchainAtColumbia), proposes to institute a gas fee rebate mechanism for recognised delegates voting on-chain on Aave.

## ***Motivation***

Gas fees on Ethereum have been increasing recently. As shown by data from Dune Analytics, median gas prices sit at around 30 gwei, with intradaily spikes often far exceeding that level. The amount of gas fees required for voting on-chain has therefore risen proportionally, increasing the cost of on-chain governance for delegates (particularly in light of the heavier recent proposal load at Aave).

**![|537x363](https://lh5.googleusercontent.com/oDESh98-zthvbro3LnZuiQcCRWRRqMXRcC_HzQNnbdKmKLZ40BN5_Zes9fmVp2kg7tMLV7uAmJKMqHvl-IAH45Ycf17xD-XRzrphEo_oUpREx-AtZYZ6cg0IRjiRB7AjKMPVI9bfyfHxjtr2ybCclrE)**

To find out more about gas costs on Aave, refer to the following dashboards created by Flipside here:

* https://flipsidecrypto.xyz/janan/aave-delegates-rayk2E
* https://flipsidecrypto.xyz/alitaslimi/aave-delegates-gas-usage-9LderL
* https://flipsidecrypto.xyz/Ali3N/aave-delegates-gas-usage-136ks0
* https://flipsidecrypto.xyz/panda-gXSkiX/aave-gas-usage-on-votes-_zF8ba

LBS Blockchain Society, like other peer universities, is a not-for-profit, student-run organisation that depends on sponsorships and stipends to finance i

====================================================================================================
[63] id=0xb477feee6d506be940154bc84278654f2863044854f80fca825b236253a97778  token=AAVE  space=aavedao.eth  date=2023-05-01
TITLE: Aave Bug Bounty Program on Immunefi
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Introduction

This snapshot temp check asks the AaveDAO to approve a bug bounty program hosted on Immunefi. Immunefi proposes to engage with community contributors, the Aave Companies and BGD Labs, who would support the bug bounty program as technical experts in terms of receiving and evaluating bug reports as well as providing their view on what should and shouldn’t be covered under the program, pending DAO approval.


Motivation

Currently, the Aave Protocol boasts a TVL of over USD 5 billion. A key reason why the protocol has managed to amass such impressive liquidity is due to the DAOs security-focused culture. Users of the protocol feel safe when using Aave.

As the Protocol continues to develop thanks to impressive work done by DAO contributors, with some notable innovations being V3 and GHO, it continues to be incredibly important that as much care is taken to ensure that users feel safe when using the protocol.

One great way to further protect user funds is to enact an effective and standardized bug bounty program. A bug bounty program encourages security researchers to continuously look through our codebase and responsibly disclose any bugs that they find, especially as new types of vulnerabilities are being discovered. Additionally, it provides a last option for blackhat hackers who find a bug to disclose it instead of exploiting it and get rewarded with clean funds.


About Immunefi

Immunefi is the leading bug bounty and security services platform for Web3, featu

====================================================================================================
[64] id=0xe9ff93315d1ce1ee0fe746a3074b866566de096cf912d45350f35e4fe019f502  token=AAVE  space=aavedao.eth  date=2023-05-02
TITLE: [TEMP CHECK] Allocation of 300k OP Received by Aave Grants DAO
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [TEMP CHECK] Allocation of 300k OP Received by Aave Grants DAO

Author: @0xbilll  [Aave Grants DAO]

Created: 2023-04-19

---

###  **Simple Summary**

This proposal is for the community’s approval as to how Aave Grants DAO (AGD) should allocate the 300,000 OP tokens received as part of OP Stimpack phase 0. We are proposing allocating up to 100,000 OP as part of the current AGD proposal and keeping the remaining 200,000 OP in the AGD multisig for future seasons of AGD.

### **Background**

Last year, [we created a proposal and successfully received 300,000 OP tokens](https://gov.optimism.io/t/gf-phase-0-proposal-aave/1712?u=bill) as part of phase 0 of OP Stimpack. The tokens are to go towards funding projects to help grow Aave on Optimism. The original post in the Optimism forum states:

![Aave Grants.png](ipfs://bafkreiad63ih6ihr6tbkiplsr6fbvs3jmwjy4cdptah657fdbcnfga2jia)

AGD has funded multiple projects building on Optimism with funds received from Aave DAO. These include:

● Analytics from[ DappLooker](https://governance.aave.com/t/aave-v3-user-retention-dashboards-and-analytics/10946),[ Block Analitica](https://aave.blockanalitica.com/markets/) &[ Projection Finance](https://www.projection.finance/)

● Integrations with[ Mean Finance](https://mean.finance/create/10),[ Layer3](https://beta.layer3.xyz/communities/aave) &[ DeFunds](https://defunds.co/)

● Native apps like[ Pegasus Finance](https://twitter.com/0xPegasusFi),[ Lyra Finance](https://twitter.com/lyrafinan

====================================================================================================
[65] id=0x602046cab7a8a9abc178fbe2c4e869c55bcea35567235e3174e0409e9c39db7b  token=AAVE  space=aavedao.eth  date=2023-05-05
TITLE: [ARFC] E-Mode Specific Supply and Borrow Caps
CHOICES: Option 1: Add EM Specific Caps | Option 2: No EM Specific Caps | Abstain | Nay
TEXT (first 1500 characters):
## Simple Summary
Gauntlet's E-Mode methodology and forum discussion can be found [here](https://governance.aave.com/t/arfc-gauntlet-e-mode-methodology-aave-v3-liquid-staking-tokens/12700).

On Aave V3, E-mode requires multiple considerations, including mitigating tail risks to protocols, optimizing user experience, and allowing on-chain liquidity to remain robust. E-mode, in particular, unlocks capital efficiency with specific risk tradeoffs.

Please refer to Gauntlet's [forum post](https://governance.aave.com/t/arfc-gauntlet-e-mode-methodology-aave-v3-liquid-staking-tokens/12700) for discussion on factors such as short-term and long-term correlation, arbitraguer profitability, abnormal vs. normal price variances, and assumptions on the redemption mechanism.

This is a temperature check to see if the community would like to add E-Mode specific supply/borrow caps. Specifically, to include supply/borrow caps exclusive to a specific E-mode, different from the caps of the same assets in non-E-mode.

This functionality is not possible at the moment, but may be implemented on the protocol to enable more fine-tuned risk controls, if the community approves.

This proposal does not recommend any specific supply or borrow cap parameter changes. Rather, this proposal is only to align on the community's willingness to add the functionality of E-mode specific caps, and the community can then set parameter values later.

Specification:
- Option 1: Add E-Mode Specific Supply/Borrow Caps
-

====================================================================================================
[66] id=0x33cdbe42706aa449c2e7d55d6c1e81da4bf3f153bb5c1010df71e8ab296fe525  token=AAVE  space=aavedao.eth  date=2023-05-08
TITLE: [TEMP CHECK] Safety Module Update Part I - Migrate AAVE/wETH
CHOICES: YAE - 80/20 AAVE/wETH | YAE - 80/20 AAVE/wstETH | NAE - Rework Proposal | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Safety Module Update Part I - Migrate AAVE/wETH Balancer v1 Pool to Balancer v2
author: @Llamaxyz - @dydymoon & @TokenLogic
created: 2023-04-13

---

# Summary

The publication proposes creating a new AAVE liquidity pool on Balancer v2 and including the BPT in Aave’s Safety Module (SM).

# Abstract

The SM currently accepts two deposit tokens, AAVE and ABPT. The ABPT is a 80/20 AAVE/wETH Balancer v1 liquidity pool receipt token. Balancer v1 is now obsolete and the main AAVE liquidity pool requires migrating. This publication presents several pool options to consider when migration of the main decentralized exchange (DEX) AAVE liquidity pool and if the receipt token (ABPT) should be included in Aave’s SM.

Given Balancer DAO has adopted a veTokenomics model, if the new AAVE liquidity pool was to receive a gauge and incentives then this would represent an alternative yield source that does not incur any risk of shortfall. This is an important consideration when estimating the cost of renting users backstop liquidity within the SM.

This publication seeks to determine what liquidity pools should be created on Balancer v2 and if those ABPTs are to be included within Aave’s SM.

# Motivation

By depositing AAVE and ABPT into the SM, depositors receive stkAAVE and stkBPT respectively, along with yield nominated in AAVE. 550 AAVE are distributed daily to users who stake AAVE and another 550 AAVE is distributed daily to depositors who stake ABPT. In return fo

====================================================================================================
[67] id=0xcd09c811c9f5f58693656846f119dfd7561b10de6b5d91f860634b228cb7ee04  token=AAVE  space=aavedao.eth  date=2023-05-12
TITLE: [ARFC] Add LUSD Arbitrum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add LUSD Arbitrum v3
author: @Llama - @TokenLogic
created: 2023-04-23

---

# Summary

This publication presents the community with the opportunity to add LUSD to Aave Arbitrum v3. 

# Abstract

LUSD is decentralised stable coin backed by ETH that is minted on the non-custodial, immutable, and governance-free, Liquidity Protocol.

Adding LUSD to Arbitrum will promote stable coin diversity. All Liquidity Protocol contracts are immutable, which makes LUSD the most trustless stablecoin available.

This publication proposes listing LUSD with collateral disabled (LTV 0%) with borrowing enabled. 

# Motivation

LUSD is currently listed on the following Aave deployments:

* Ethereum v3
* Ethereum v2
* Optimism v3

This publication seeks to list LUSD on Aave v3 Arbitrum.

Past publications, [here](https://governance.aave.com/t/arc-add-lusd-to-ethereum-v3-market/11522) and [here](https://governance.aave.com/t/arc-add-support-for-lusd-liquity/8443) provide insight and context.

LUSD brings more stable coin diversity to the Aave Protocol and will further empower the support for decentralized stablecoins. The LUSD stable coin mechanism is relatively simple and is in line with the risk averse ethos of the Aave Community.

LUSD is overcollateralised by ETH with two main mechanisms helping it keep its peg: 

* LUSD can be redeemed for ETH at face value (i.e., 1 LUSD for $1 of ETH). 
* Minimal collateral ratio of 110%.
 
Both mechanisms respectively create a price floor an

====================================================================================================
[68] id=0xb4141f12f7ec8e037e6320912b5673fcc5909457d9f6201c018d5c15e5aa5083  token=AAVE  space=aavedao.eth  date=2023-05-14
TITLE: [ARFC] Consolidate Collector Contract & Secure Service Provider Runway
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Consolidate Collector Contract & Secure Service Provider Runway
author: @llama - @TokenLogic
created: 2023-05-13

---

# Summary

This publication proposes swapping many long tail assets for aUSDC to be used for Service Provider renumeration.

# Abstract

Aave DAO's service provider aUSDC burn rate exceeds the aUSDC revenue. Consequently, assets held in the Ethereum Collector Contract need to be periodically swapped to USDC and deposited in Aave v2.

This publication intends to swap several assets via Cowswap to USDC. The USDC is to be deposited in Aave v2 for aUSDC and then used to remunerate Service Providers via the various streaming contracts.

# Motivation

There is currently $1.7M aUSDC held in the Ethereum Collector contract.
 
![Screenshot 2023-05-14 at 14.58.27.png](ipfs://bafkreih2zwytnlor2pzedirxhxigqpxzmmv53npsavxnvebma4rspuqb4i)
    
There are a number of Service Providers requiring payment in aUSDC. The below summarises all of Aave's active Service Provider commitments.
 
![Screenshot 2023-05-14 at 14.57.38.png](ipfs://bafkreifmfxwvqzchg5awoz6kxioz67gvdklnmypsvoqfjruow4lupf3dv4)
    
Details of each Service Providers funding can be found [here](https://community.llama.xyz/aave/runway) by hovering the cursor over the respective Service Providers contract. Similar applies for the contract start and finish dates.

In order to provide sufficient funding, assets need to be converted to aUSDC. This publication proposes swapping assets to USDC and th

====================================================================================================
[69] id=0xd33381a83222b33afa8277f86fae5ee46d4e3455ba09dfc091f626e59ecc29ad  token=AAVE  space=aavedao.eth  date=2023-05-16
TITLE: [ARFC] Add ENS to Aave V3 Ethereum
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# Summary

This proposal presents Aave with the opportunity to onboard ENS to the Etheruem Aave V3 Market.

# Motivation

As part of the community efforts on the V2 to V3 migration, Chaos Labs proposed a [multi-phased plan](https://governance.aave.com/t/temp-check-ethereum-v2-to-v3-migration/12636) to promote V3 adoption. As per this plan, Chaos Labs proposes to list ENS on Aave V3 on Ethereum. ENS is currently listed on V2 Ethereum with borrow disabled.

As the proposed assets in the migration plan are traded with relatively low market cap and trading volume, we have taken a prudent approach in setting borrow caps to account for no more than 1% of the average daily trading volume. The supply cap was derived using our supply cap methodology with the V2 data (simulation results can be seen in the image below). Additionally, we have  adjusted the IR Slope1 to reflect the changes in interest rates over the past months and adjusted the liquidation bonus levels to the current liquidity levels in DEXs.

# Specification

Ticker: ENS

Contract Address: 0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72

| Parameter | ENS |
| --- | --- |
| Isolation Mode | Yes |
| Borrowable | Yes |
| Collateral Enabled | Yes |
| Supply Cap | 1M |
| Borrow Cap | 40,000 |
| Debt Ceiling | $3.9M |
| LTV | 39.00% |
| LT | 49.00% |
| Liquidation Bonus | 8.00% |
| Liquidation Protocol Fee | 10.00% |
| Variable Base | 0% |
| Variable Slope1 | 9.00% |
| Variable Slope2 | 300.00% |
| Uoptimal | 45.00% |
| Reserve Fac

====================================================================================================
[70] id=0x637d661f1c720aded816291dd01fb093ae8b1b38c322795fae5ceede876a8015  token=AAVE  space=aavedao.eth  date=2023-05-16
TITLE: [ARFC] Add 1INCH to Aave V3 Ethereum
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# Summary

This proposal presents Aave with the opportunity to onboard 1INCH to the Etheruem Aave V3 Market.

# Motivation

As part of the community efforts on the V2 to V3 migration, Chaos Labs proposed a [multi-phased plan](https://governance.aave.com/t/temp-check-ethereum-v2-to-v3-migration/12636) to promote V3 adoption. As per this plan, Chaos Labs proposes to list 1INCH on Aave V3 on Ethereum. 1INCH is currently listed on V2 Ethereum with borrow disabled.

As the proposed assets in the migration plan are traded with relatively low market cap and trading volume, we have taken a prudent approach in setting borrow caps to account for no more than 1% of the average daily trading volume. The supply cap was derived using our supply cap methodology with the V2 data (simulation results can be seen in the image below). Additionally, we have  adjusted the IR Slope1 to reflect the changes in interest rates over the past months and adjusted the liquidation bonus levels to the current liquidity levels in DEXs.


# Specification

Ticker: 1INCH

Contract Address: 0x111111111117dC0aa78b770fA6A738034120C302

| Parameter | 1INCH |
| --- | --- |
| Isolation Mode | Yes |
| Borrowable | Yes |
| Collateral Enabled | Yes |
| Supply Cap | 22M |
| Borrow Cap | 720,000 |
| Debt Ceiling | $4.5M |
| LTV | 57.00% |
| LT | 67.00% |
| Liquidation Bonus | 7.50% |
| Liquidation Protocol Fee | 10.00% |
| Variable Base | 0% |
| Variable Slope1 | 9.00% |
| Variable Slope2 | 300.00% |
| Uoptimal | 45.00% |

====================================================================================================
[71] id=0x058f8e69b69a27495ee9796fc6952326d94eb24fe0071050db166d5d5e1da242  token=AAVE  space=aavedao.eth  date=2023-05-17
TITLE: [TEMP CHECK] Add ARB to Arbitrum Aave v3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
**Title:** [TEMP CHECK] Add ARB to Arbitrum Aave v3
**Author:** @fig Flipside Crypto
**Created**: 04/27/203

---

This proposal is to add ARB to Aave v3 on Arbitrum. 

## References

Project - https://arbitrum.foundation/
Documentation - [Arbitrum Intro - Governance Docs](https://docs.arbitrum.foundation/gentle-intro-dao-governance) | [Arbitrum Intro - Developer Docs](https://developer.arbitrum.io/intro/) 
Github / source code - https://github.com/ArbitrumFoundation
Ethereum contracts - [Arbitrum | Arbiscan](https://arbiscan.io/token/0x912CE59144191C1204E64559FE8253a0e49E6548)
Chainlink Oracle [ARB Price Feed | 0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6 ](https://arbiscan.io/address/0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6)
Audit - [Trail Of Bits Report - 01/06/2023](https://github.com/ArbitrumFoundation/governance/blob/main/audits/trail_of_bits_governance_report_1_6_2023.pdf)
Twitter -https://twitter.com/arbitrum 
Blog - https://arbitrumfoundation.medium.com/

## Summary

This proposal is to add ARB to Aave v3 on Arbitrum. ARB is Arbitrum's governance token, an ERC-20 token native to the Arbitrum One chain.

## Motivation

Arbitrum represents a governance token in the Ethereum scaling ecosystem. It is widely distributed, initially across 625,000 wallet addresses - including to DAOs like Aave.

Adding support for ARB in Arbitrum v3 pools adds greater TVL and user experience to the increasingly popular Aave v3 Arbitrum market - and additional revenue opportunities for Aave.

====================================================================================================
[72] id=0xef4162088e6f35a70021d3a132f5a329ab7a660a4869ce8af6b9d20c646c6c92  token=AAVE  space=aavedao.eth  date=2023-05-19
TITLE: [ARC] Framework For Recognized Delegates
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARC] Framework For Recognized Delegates

Author: @fig - Flipside Crypto

Date: 05-04-2023

---

## Summary:

This proposal establishes a baseline set of guidelines and expectations for becoming a Recognized Delegate within Aave.

It aims to define the role, responsibilities, and characteristics of Aave’s recognized delegates to aid the DAO in addressing and sustainably growing this stakeholder base.

It is left intentionally sparse in some parts to provide a rich and diverse array of delegates from which AAVE [or equivalent] holders may select their chosen representative(s.)

## Abstract:

This proposal responds to the community's desire to outline what a recognized delegate looks like, to qualify for potential reimbursement in the current Gas Fee Rebate proposal.

It creates a framework for becoming or ending one’s role as a recognized delegate.

In addition, it delineates the distinction between a delegate and a recognized delegate.

## Motivation:

As Aave attracts more stakeholders, contributors, and delegates, it requires more active management and a clearer organization of the delegate base.

A typical interaction with Governance (roughly) looks something like this:

![91572a4486b9001bdd6927a25f55c5a4f23608bb.png](ipfs://bafkreied3ex3txkxbesko2cf4g3cgn7milsd6sx2l3pz663h25pnxffhnq)
   

This graphic illustrates a current dynamic within the DAO; delegates working on behalf of token holders, engaging with Governance or contributors themselves to vote and propose on

====================================================================================================
[73] id=0x00a60204ac48099bccff1b5801299486f73ef97fb4b51773e74a22a9e767930c  token=AAVE  space=aavedao.eth  date=2023-05-19
TITLE: [ARC] Delegate Code Of Conduct
CHOICES: Good Faith / Integrity | Best Interest | Due Care and Attention | Communication | Professional Knowledge | Conflicts of Interest | Availability | Security Optimization
TEXT (first 1500 characters):
Title: [ARC] Delegate Code Of Conduct

Author: @fig - Flipside Crypto

Date: 05-04-2023

---

## Summary:

This proposal looks to establish a Code of Conduct for new and existing recognized delegates within Aave’s governance and ecosystem.

It aims to codify and define the values and character upheld by individuals or organizations who embrace a delegate role, representing Aave and its stakeholders.

If implemented, it encourages more professionalism and accountability within the role.

## Abstract:

This proposal creates a baseline for all delegates to reference when participating in governance decision-making or discussions.

This post will serve as a reference and adherence to DAO-wide policies - as well as establish collective values within the Governance protocol.

Just as companies have guiding principles and values, DAOs should too.

This proposal will be submitted as a “ranked choice vote” to better outline and define the top values as identified by current stakeholders within Aave.

## Motivation:

A delegate is a unique role with teams approaching this responsibility in different ways.

As Aave introduces novel mechanisms such as Butter, Gas Fee Rebates, or other ongoing discussions about incentives - the community garners more delegate interest.

In order to protect the integrity and maturation of the DAO, it is important to establish and enforce an agreeable code of conduct for all delegates within Aave.

This proposal aims to codify nine values as identified by t

====================================================================================================
[74] id=0x8e60bbebf59a6911cd0d137aa06780aefc5b5b0cd0f8ccfa12427cf153f58b05  token=AAVE  space=aavedao.eth  date=2023-05-28
TITLE: [TEMP CHECK] Safety Module Upgrade Part II - Asset Diversity, SM Categories & Slashing Updates
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Safety Module Upgrade Part II - Asset Diversity, SM Categories & Slashing Updates
discussions: 
author: @Llamaxyz - @dydymoon & @TokenLogic
created: 2023-04-13

---

# Summary

This publication presents the community the opportunity to discuss Safety Module (SM) upgrades that enhance asset diversification, introduces risk tranching and potential growth synergies.

# Abstract

This publication presents the community with the opportunity to expand the assets accepted within the SM. Currently, the SM is overly concentrated in AAVE via direct AAVE staking and ABPT staking which is a Balancer v1 80/20 AAVE/wETH liquidity token.

This publication seeks to explore the community's appetite to diversify the SM asset base and vary the portion of users' funds which can be auctioned in the event of a shortfall. Currently, 30% of user deposits are at risk when depositing into the SM.

# Motivation

@bgdlabs is currently proposing to upgrade the [SM architecture](https://governance.aave.com/t/bgd-aave-safety-module-v1-5/12148) to support the launch of GHO, by enabling stkAAVE holders to access cheaper GHO borrowing rates. Further to this, Llama has kick started the conversation around migrating AAVE liquidity from Balancer v1 to v2 in this [forum post](https://governance.aave.com/t/temp-check-safety-module-update-part-i-migrate-aave-weth-balancer-v1-pool-to-balancer-v2/12748).

Several comments relating to the AAVE concentration and auction mechanism have been made

====================================================================================================
[75] id=0x601a534cd51391823c842e54dda5b9cc2c2be50fcb0655f8f59811e6cd2bdaa9  token=AAVE  space=aavedao.eth  date=2023-05-30
TITLE: [ARFC] Add fUSDC to Ethereum v3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
title: [ARFC] Add fUSDC to Ethereum v3
author: @marczeller - Aave-Chan Initiative
created: 2023-05-23
---

## Summary

This ARFC presents the community with the opportunity to add fUSDC to the Ethereum v3 Liquidity Pool.

## Abstract

fUSDC is a yield-bearing token representing USDC deposits in Flux, a fork of Compound V2. Adding fUSDC to Ethereum v3 would allow fUSDC holders to borrow stablecoins on Aave and leverage their fUSDC position, boosting the stablecoin utilization rate on Aave, while attracting new stablecoin deposits thanks to boosted supply rates.

## Motivation

fUSDC is a new financial primitive with arguably the best risk-adjusted yield available in DeFi. Adding support for fUSDC on Ethereum V3 in isolated mode would allow fUSDC holders to borrow stablecoins on Aave and leverage their fUSDC position, boosting the stablecoin utilization rate on Aave, while attracting new stablecoin deposits thanks to boosted supply rates.

## Specification

Ticker: fUSDC

Contract Address: `[0x465a5a630482f3abd6d3b84b39b29b07214d19e5](https://etherscan.io/address/0x465a5a630482f3abd6d3b84b39b29b07214d19e5)`

| Parameter | Value |
| --- | --- |
| Isolation Mode | Yes |
| Borrowable | No |
| Collateral Enabled | Yes |
| Supply Cap | 220M (~$4.45M) |
| Borrow Cap | N/A |
| Debt Ceiling | $1M |
| LTV | 77% |
| LT | 79% |
| Liquidation Bonus | 4.5% |
| Liquidation Protocol Fee | 20% |
| Variable Base | 0.00% |
| Variable Slope1 | 4.00% |
| Variable Slope2 | 60.00% |
| Uoptimal |

====================================================================================================
[76] id=0x036f9ce8b4a9fef0156ccf6b2a205d56d4f23b7ab9a485a16d7c8173cd85a316  token=AAVE  space=aavedao.eth  date=2023-06-01
TITLE: [ARFC] Add RPL to Ethereum v3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add RPL to Ethereum v3
author: @marczeller - Aave-Chan Initiative
created: 2023-05-20

---

# Summary

This ARFC presents the community with the opportunity to add RPL to the Ethereum v3 Liquidity Pool.

# Abstract

Rocket Pool is an Ethereum staking protocol. The protocol reduces ETH staking capital and hardware requirements to increase Ethereum’s decentralization and security. Rocket Pool lets customers stake trustlessly to a network of node operators to do this. Adding support for RPL on Ethereum V3 would allow RPL holders to obtain a passive yield on their holdings without the need to deploy mini-pools.
On their side, RPL borrowers would be able to participate in Rocket Pool staking without the need to invest in RPL.

# Motivation

RPL is the governance and utility token for RocketPool, a major decentralized liquid staking Token protocol. RocketPool has solidified itself as a Protocol which is actively contributing to Ethereum’s decentralization by making Operating a Node easy and accessible. By supporting RPL on Aave V3 Ethereum we would create an alternative for RPL holders who wish to earn yield on their asset.

# Specification

Ticker: RPL

Contract Address: [0xD33526068D116cE69F19A9ee46F0bd304F21A51f](https://etherscan.io/address/0xD33526068D116cE69F19A9ee46F0bd304F21A51f)`

|Parameter|Value|
| --- | --- |
|Isolation Mode|No|
|Borrowable|Yes|
|Collateral Enabled|No|
|Supply Cap (RPL)|105,000|
|Borrow Cap (RPL)|105,000|
|Debt Ceiling|N/A|
|LTV|N/A|

====================================================================================================
[77] id=0x308439517ffc8faa8709db0b4a1d131d2402ee8a3282cb79adf890de6135ec98  token=AAVE  space=aavedao.eth  date=2023-06-06
TITLE: [ARFC] Add ARB to Arbitrum Aave v3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
--
**Title:** [ARFC] Add ARB to Arbitrum Aave v3
**Author:** @fig - Flipside Crypto
**Created** : 2023-05-26

---
## Abstract

This proposal is the next step to add ARB to Aave v3 on Arbitrum.

## Summary

Following the successful [TEMP CHECK](https://snapshot.org/#/aave.eth/proposal/0x058f8e69b69a27495ee9796fc6952326d94eb24fe0071050db166d5d5e1da242) to add Aave v3 on Arbitrum, this  proposal progresses the asset listing to the next stage in the Governance cycle, incorporating parameters provided by Risk  Managers.

## Motivation

Adding support for ARB in Arbitrum v3 pools adds greater TVL and user experience to the increasingly popular Aave v3 Arbitrum market - and additional revenue opportunities for Aave.

By enabling borrowing, it allows users and institutions to take a unique position on this Governance token as the network matures and builds a decentralized community.

Furthermore, it more closely aligns the Aave community with Arbitrum and, by extension, Ethereum.

Additionally, it allows for creative uses of ARB received by the DAO to seed initial liquidity.

## Specifications

ARB may be listed with the following risk parameters:

|Parameter|Value|
| --- | --- |
|Isolation Mode|Yes|
|Borrowable|Yes|
|Collateral Enabled|Yes|
|Supply Cap (ARB)|20M|
|Borrow Cap (ARB)|16.5M|
|Debt Ceiling|$14M|
|LTV|50.00%|
|LT|60.00%|
|Liquidation Bonus|10.00%|
|Liquidation Protocol Fee|10.00%|
|Reserve Factor|20.00%|
|Variable Base|0.00%|
|Variable Slope1|7.00%|
|Variable Slope2|300.0

====================================================================================================
[78] id=0x7ac0e58020040e98d6f5793ccad9e29dfd69c4771ba12480f2f666c1da8fbc7c  token=AAVE  space=aavedao.eth  date=2023-06-07
TITLE: [ARFC] Add GUSD to Aave V3 Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
# Summary

This proposal presents Aave with the opportunity to onboard GUSD in isolation mode to the Ethereum Aave V3 Market.

# Motivation

As part of the community efforts on the V2 to V3 migration, Chaos Labs proposed a [multi-phased plan](https://governance.aave.com/t/temp-check-ethereum-v2-to-v3-migration/12636) to promote V3 adoption. As per this plan, Chaos Labs proposes to list GUSD on Aave V3 on Ethereum. GUSD is currently listed on V2 Ethereum as a non-collateral asset.

## Liquidity and Market Cap

When analyzing market cap and trading volumes of assets for listing, we look at data from the past 180 days. The average market cap of GUSD over the past 180 days was ~$527M, and the average daily trading volume was ~$1M (CeFi & DeFi). 

 
![image](ipfs://bafkreig3i5tpyiqm7khg4n6aydyq7vbyxstf5jjbxgkmzvqmenpr2kcig4)
    

## **Liquidation Threshold**

Analyzing GUSD price volatility over the past, we observed daily annualized volatility of 5.13% and 30-day annualized volatility of 2.38%. Considering this volatility and the history of GUSD on other networks, we recommend an initial LT of 75%.

 
![image](ipfs://bafkreid5fugl7ekjkzjhkqinwcacz6d3dtg4xet5lqjd3anfqus6yzyabu)
    

We recommend listing GUSD as borrowable, as we do not observe a significant risk to the protocol by allowing to borrow of GUSD, as long as it is bound by a well-defined cap.

## **Debt Ceiling**

Following [Chaos Labs’ Isolation Mode Methodology](https://governance.aave.com/t/chaos-labs-isolation-mod

====================================================================================================
[79] id=0x727fb5e26ebae03350d2485bf229cbe32f2e7cf7c26dfe82acb52b72b68894c1  token=AAVE  space=aavedao.eth  date=2023-06-07
TITLE: [ARFC] Add USDP to Aave V3 Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## Summary

This proposal presents Aave with the opportunity to onboard USDP in isolation mode to the Ethereum Aave V3 Market.

## Motivation

As part of the community efforts on the V2 to V3 migration, Chaos Labs proposed a [multi-phased plan](https://governance.aave.com/t/temp-check-ethereum-v2-to-v3-migration/12636) to promote V3 adoption. As per this plan, Chaos Labs proposes to list USDP on Aave V3 on Ethereum. USDP is currently listed on V2 Ethereum as a non-collateral asset.

### Liquidity and Market Cap

When analyzing market cap and trading volumes of assets for listing, we look at data from the past 180 days. The average market cap of USDP over the past 180 days was ~$883M, and the average daily trading volume was ~$8.7M (CeFi & DeFi). 

 
![image](ipfs://bafkreicffv66o5w2u2l6vdu6u2mfdobf4dgnla2k42osux3s7pycwyuj6m)
    

### **Liquidation Threshold**

Analyzing USDP price volatility over the past, we observed daily annualized volatility of 2.79% and 30-day annualized volatility of 1.63%. Considering this volatility and the history of USDP on other networks, we recommend an initial LT of 75%.

 
![image](ipfs://bafkreifydbyneeuh24uqgfmss6u3ppuyqevx6eyau44dpmgfurrtoj4h6a)
    

We recommend listing USDP as borrowable, as we do not observe a significant risk to the protocol by allowing to borrow of USDP, as long as it is bound by a well-defined cap.

### **Debt Ceiling**

Following [Chaos Labs’ Isolation Mode Methodology](https://governance.aave.com/t/chaos-labs-isolat

====================================================================================================
[80] id=0x0c9447367d5223863e829393a9e8937a54b2af85adef883542f063df4fb86db6  token=AAVE  space=aavedao.eth  date=2023-06-12
TITLE: [TEMP CHECK] Aave v3 MVP deployment on Scroll mainnet
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [TEMP CHECK] Aave v3 MVP deployment on Scroll mainnet

Author: Lea - Partnerships Lead at @Scroll_zkEVM

Date: 2023-05-30

----

### Simple Summary:

Proposal to deploy an Aave v3 MVP to Scroll mainnet with limited assets onboarding and conservative risk parameters in order to allow Aave to establish a strategic position in the Scroll ecosystem while limiting risk exposure.

### Background:

This Temp Check proposes the deployment of a Minimal Viable Product (MVP) version of Aave V3 on Scroll mainnet. Scroll mainnet will go live beginning of August this year and intends to onboard Aave V3 as one of the first DeFi dApps in the eocsystem. Scroll is an EVM-equivalent zk-rollup with the primary goal to provide scalability to Ethereum in the most robust and secure way. We guarantee this by being open source from day 1, a strong in-house security team paired with rigorous audits, third party provers upon our mainnet genesis block and a gradual decentralization of our sequencer network.

### Motivation:
Aave will be given a prominent role in the early Scroll ecosystem and will be able to establish a strategic presence early on. Aave will be in good company of 150+ projects going live shortly after mainnet launch and will be able to harness a vibrant new ecosystem that expands across the globe.

### Specification:
The proposal will detail the deployment of Aave V3 on Scroll mainnet with three collaterals (WETH, USDC, wstETH) and one borrowable asset (USDC). We consulted Gauntl

====================================================================================================
[81] id=0xf0a3ef553905b03d36e0982719cfe25e85d97f563c3ef401f25e8455960576f8  token=AAVE  space=aavedao.eth  date=2023-06-13
TITLE: [ARFC] Add FRAX to Ethereum Aave v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
- - - 
Title: [ARFC] Add FRAX to Ethereum Aave v3
Author: @oneski22 @TokenLogic
Created: 2023-05-10
- - - 

This proposal is to add FRAX to Aave v3 on Ethereum.

# References

**General**

Project - https://frax.finance/
Documentation - https://docs.frax.finance
Whitepaper: https://docs.frax.finance/overview
Github / source code - https://github.com/fraxfinance
Analytics: https://facts.frax.finance

Chainlink Oracle - [0x0809E3d38d1B4214958faf06D8b1B1a2b73f2ab8](https://etherscan.io/address/0xb9e1e3a9feff48998e45fa90847ed4d467e8bcfd)

**Audits**

11/2020 - [Certik](https://certik-public-assets.s3.amazonaws.com/REP-Frax-06-11-20.pdf)
07/2021 - [Trail of Bits](https://github.com/trailofbits/publications/blob/master/reviews/FraxFinance.pdf)
01/2022 - [Trail of Bits](https://github.com/trailofbits/publications/blob/master/reviews/FraxQ42021.pdf)

# Summary

FRAX is the inventor and first fractional stable coin that uses a hybrid of algorithmic and collateralized mechanisms to stay on price target. FRAX is currently the [#7 largest stablecoin by market cap](https://www.coingecko.com/en/categories/stablecoins) (1B) according to Coingecko. FRAX has also never lost peg a single time in its existence (defined as more than 1 cent price deviation on each side).

FRAX currently has the largest Curve pool on Ethereum mainnet with almost $900M in liquidity and is a Uniswap top 10 token. Additionally, FRAX has already been successfully lent out on Aave v2 on ETH mainnet for many months and

====================================================================================================
[82] id=0x68647b1a75da40cd7753ffd3dc81bc69ef2fda06502ea5710b89166223bbce5c  token=AAVE  space=aavedao.eth  date=2023-06-13
TITLE: [TEMP CHECK] Add GMX  to Arbitrum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
# References

Project: [https://gmx.io/#/](https://gmx.io/#/)
GitHub: [https://github.com/gmx-io](https://github.com/gmx-io)
Docs: [https://gmxio.gitbook.io/gmx/tokenomics](https://gmxio.gitbook.io/gmx/tokenomics)
Chainlink Oracle: [0xdb98056fecfff59d032ab628337a4887110df3db](https://arbiscan.io/address/0xdb98056fecfff59d032ab628337a4887110df3db)
Twitter: [https://twitter.com/GMX_IO?s=20](https://twitter.com/GMX_IO?s=20)
blog: [https://medium.com/@gmx.io](https://medium.com/@gmx.io)
Discord: [GMX](https://discord.com/invite/ymN38YefH9)

# Summary

This proposal presents Aave with the opportunity to onboard GMX to the Arbitrum v3 Liquidity Pool.

# Motivation

GMX is one of the largest DeFi’s offering derivatives and is currently one of the most popular DeFi’s. GMX is also one of the most heavily traded assets and the market demand is very high.
It has never been listed on Aave in the past, so it needs to be carefully considered.

# Specification

1. About the author of ARC

* LensProfile: [https://lensfrens.xyz/0xlide.lens](https://lensfrens.xyz/0xlide.lens)

2. Provide a brief high-level overview of the project and the token

* GMX is a decentralized spot and permanent exchange supporting low swap fees and zero price impact trading GMX is the market leader in Derivatives with $544 million TVL in two deployments and is #20 on Defi Llama’s TVL Dashboard It is ranked #20 on Defi Llama’s TVL Dashboard.

GMX, the platform’s utility and governance token, is ranked #68 above MKR on

====================================================================================================
[83] id=0x03798dc3d6382f0d461590059d554a4405eefd5c95e3de917515702fdfc9ecfb  token=AAVE  space=aavedao.eth  date=2023-06-13
TITLE: [ARFC] Add FRAX Arbitrum Aave v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add FRAX Arbitrum Aave v3 
discussions: https://governance.aave.com/t/arfc-add-frax-arbitrum-aave-v3/13222
shortDescription: Add FRAX Arbitrum Aave v3 
author: @Fig - Flipside & @TokenLogic
created: 05-06-2023

---

# References

Website: https://frax.finance/
Whitepaper: https://docs.frax.finance/overview
Documents: https://docs.frax.finance/
Analytics: https://facts.frax.finance/
Github: https://github.com/fraxfinance

Arbitrum Contract Address: [`Abritrum: 0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F`](https://arbiscan.io/token/0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F)

Oracle Address: [`Arbitrum: 0x0809E3d38d1B4214958faf06D8b1B1a2b73f2ab8`](https://arbiscan.io/token/0x17fc002b466eec40dae837fc4be5c67993ddbd6f)

**Audits**

* 11/2020: [Certik](https://certik-public-assets.s3.amazonaws.com/REP-Frax-06-11-20.pdf)
* 07/2021: [Trail of Bits](https://github.com/trailofbits/publications/blob/master/reviews/FraxFinance.pdf)
* 01/2022: [Trail of Bits](https://github.com/trailofbits/publications/blob/master/reviews/FraxQ42021.pdf)

# Summary

This publication presents the community an opportunity to add FRAX to the Arbitrum v3 Liquidity Pool.

# Motivation

FRAX can use its Lending AMO (similar to Maker’s DAI Direct Deposit Module) to mint protocol controlled FRAX to be lent out on Aave Protocol. Frax Finance has in the past done so in Aave v2 on Ethereum and has already stated on the Aave governance forum an interest in doing so on other deployments once FRAX is

====================================================================================================
[84] id=0xcf85642329d2f1f54ae8a55bf272e4fa6e231dee3759907f9c2a0d9447cee311  token=AAVE  space=aavedao.eth  date=2023-06-18
TITLE: [TEMP CHECK] GHO Liquidity Pools
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] GHO Liquidity Pools
discussions: https://governance.aave.com/t/temp-check-gho-liquidity-pools/13655
shortDescription: Initial liquidity pools supporting the GHO launch
author: @TokenLogic
created: 2023-06-13

---

# Summary

This publication presents the community with initial GHO liquidity strategy for discussion.

# Abstract

With GHO expected to launch in the near future, this publication presents the community with an initial liquidity strategy.

The strategy consists of primary and secondary liquidity pools, with the potential to included some pools in the Aave Safety Module (SM) at a later date. 

At a high level, the primary liquidity pools at launch are shown below:

1) GHO / bb-a-USD - ComposableStablePoolFactory
2) LST / GHO (80/20) - Weighted Pool Factory
3) GHO / LUSD - ComposableStablePoolFactory

With veBAL support from beyond Aave DAO expected, we believe concentrating effort across several pools will best serve the DAO launch strategy. A later proposal will detail pool sizes, yield estimates and how this could after the $1 peg.

# Introduction

When shaping the liquidity strategy for GHO, we assessed various options with three main considerations:

* Trading Pair
* Decentralised Exchange (pool type)
* Holistic Business Strategy

The largest trading pairs in Defi are ETH and USDC. For this reason we favour creating a USD stable coin liquidity pool and a LST / GHO liquidity pool.

* USD stable coin liquidity pool
* LST liquidity pool

De

====================================================================================================
[85] id=0x779d1c48092a41481bb1bca487d291a2b77af8a8db07d0cb08d795695b1d04e7  token=AAVE  space=aavedao.eth  date=2023-06-18
TITLE: [TEMP CHECK] Aave | Flipside Proposal
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
### TLDR:

* Flipside is requesting $125,000 / 6 months for a contributor role
* Flipside will address the following problems:
(1) Lack of coordination among contributors
(2) No education or path toward engaging more users & the governing base
(3) How to introduce and engage third-party organizations
(4) Data availability and open-source tooling
* We will deliver on four key verticals; operations, infrastructure, data, and governance

*[For the full introduction please see the forum post linked below.]*

### Current and Future Services
Investing in Flipside’s expertise provides builders and the community with the tools and focus needed to grow. These benefits take form in both current and future services:

***1. Aligning DAO Strategy, Vision, & Execution***

Flipside will deliver on Coordination by:

* Establish a multi-chain expansion strategy and deployment prioritization: allow for third parties to more closely align with Aave’s growth
* Poll, identify, & align strategic visions across the entire DAO (quarterly)
* Balance initiatives across growth, risk, and protocol development: 1)  First two weeks → Organize calls with delegate and contributor teams, polling their priorities and goals for Aave 2) Third week → Synthesize findings in a central document 3) Fourth week → Discuss with contributors together on a call, rank priorities via JokeDAO or off-chain polling, & present to the community for execution 4) Monthly, thereafter → Evaluate the accomplishments of this
* Minimi

====================================================================================================
[86] id=0x60960da6c27d781aaa1bd4350539ef54e3c5f39e8c58b2177ac94d6baec77307  token=AAVE  space=aavedao.eth  date=2023-06-28
TITLE: [TEMP CHECK] Allocating part of GHO Revenue to Safety Incentives
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
title: [TEMP CHECK] Allocating part of GHO Revenue to Safety Incentives
author: Marc Zeller, Aave-Chan Initiative (ACI)
date: 2023-06-07
---

## Abstract

This TEMP CHECK proposes the introduction of a dual reward system Safety Incentives, where a portion of GHO revenue is directed to the Aave Safety Incentives, enabling stakers (StkAAVE & StkBPT) to earn both AAVE and GHO tokens.

## Motivation

The motivation behind this TEMP CHECK is to enhance the sustainability of the Aave protocol by reducing its reliance on the Ecosystem Reserve of AAVE tokens for Safety Incentives. We propose a strategic shift towards harnessing protocol economic activity to generate "real yield" through the introduction of GHO as an additional Safety Incentive. 

By directing part of GHO revenue to the Safety Incentives, we aim to create a dual reward system, offering stakers both AAVE and GHO tokens. While the contribution of GHO to Safety Incentives may initially be a small fraction of the total incentives, it represents a significant step towards the protocol's maturity and sustainability. 

This proposal, suggests that the governance should adjust the distribution percentage quarterly, in response to market conditions.

As the Aave protocol already generates sustainable revenue that covers service provider costs, the introduction of GHO into the Safety Incentives mix is a viable and strategic move toward diversifying Safety Incentives and ensuring the long-term sustainability of the protocol.

====================================================================================================
[87] id=0xff11b348c1e8df41555d7579c7785942378bcf09ff1d9ca97af1d86b2b124beb  token=AAVE  space=aavedao.eth  date=2023-06-28
TITLE: [ARFC] Gas Rebate for Recognized Delegates
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
title: [ARFC] Gas Rebate for Recognized Delegates
author: @lbsblockchain, @MarcZeller Aave-Chan Initiative (ACI)
created: 2023-05-31
---

## Abstract

This ARFC introduces a mechanism for reimbursing gas fees to recognized delegates who vote on-chain on Aave.

## Motivation

As Ethereum gas fees continue to rise, the cost of on-chain governance for delegates has proportionally increased. This ARFC proposes a rebate system for these gas fees, aiming to incentivize active engagement and cultivate a more diverse voter base.

Rebating delegates for their participation offers several benefits:

- Encourages more active engagement from the delegate community by eliminating the disincentive to vote, leading to better decision-making for Aave.
- Fosters a more diverse voter base, including student organizations, by reducing the barrier to entry for voting. This creates a more open and collaborative delegate ecosystem, driving participation.
- Helps retain top delegates to foster the growth of the Aave ecosystem. Aave should remain competitive with its peers (e.g., Maker) to attract and retain the best delegate talent. The fundamental cost of being an excellent Aave delegate should not result in a net cost to the delegate due to ever-increasing gas costs.
- Can be achieved at a relatively low cost. We also propose measures to reduce the administrative burden for Aave.

## Specification

### Claiming Process

Every quarter, an ARFC will be proposed (with the current one being the f

====================================================================================================
[88] id=0xb112684943ef900f2918ccbc4de3bb3091869eaeb6b3c15cc26805c17cb6a9f6  token=AAVE  space=aavedao.eth  date=2023-07-04
TITLE: [ARFC] Add rETH Aave v3 Optimism
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add rETH Aave v3 Optimism
shortDescription: Add rETH to Aave v3 Optimism
author: @Llamaxyz - @TokenLogic
created: 2023-06-24

---

# Summary

Add rETH to Aave v3 Optimism as collateral and to the ETH correlated eMode.

# Abstract

rETH is currently listed on Aave v3 Ethereum and Arbtirum. This publication proposes adding rETH to Aave v3 Optimism network. 

ETH correlated asset make up over half of Aave's TVL on Optimism. By adding rETH and providing LST diversification, Aave presents itself as a neutral platform offering users the choice between various LSTs.

A Chainlink exchange rate oracle is now available and there is suitable liquidity across several DEX pools to support an rETH listing. 

# Motivation

rETH is listed on Aave v3 Ethereum and has over $58M of deposits. Rocket Pool is expanding its support for rETH across the L2 ecosystem and recently, a Chainlink oracle was published enabling rETH to be added to Aave Protocol. With the release of this oracle, this publication proposes adding rETH to Aave v3 on Optimism.

LST collateral types drive material borrowing revenue to Aave as users deposit the LST and borrow the corresponding network token. This is most evident on Ethereum where the LST-wETH-yield-maximising loop is the source of the vast majority of wETH borrowing demand.

An added benefit of offering a variety of LSTs is the respective communities may elect to compete for user acquisition via Aave through offering incentives. This is currentl

====================================================================================================
[89] id=0x1751d8de3c549ee99fbc9c1286d9575c482c3e639500dcc027455c8742d48bc9  token=AAVE  space=aavedao.eth  date=2023-07-04
TITLE: # [ARFC] Add GMX to Arbitrum v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Add GMX to Arbitrum Aave v3
discussions: 
shortDescription: Add GMX to Aave v3 on Arbitrum Network.
author: @0xlide, @Llamaxyz
created: 2023-06-20

---

# Summary

This publication presents the community an opportunity to add GMX to the Arbitrum Aave v3 Liquidity Pool.

# Motivation

GMX Protocol is the largest DEX offering derivatives and one of the most popular DeFi's today. GMX Token is also one of the highest traded assets on Arbiturm.

The GMX token is the utility, governance, and fee accrual token for the GMX protocol. The GMX value accrual mechanism is unique to the GMX protocol. GMX is a highly staked asset, with approximately 78% of circulating GMX staked earning an APR of [2.94%](https://app.gmx.io/#/earn). This staking yield may generate borrowing demand for GMX, noting the yield is volatile.

Adding the GMX token to Arbitrum Aave v3 support greater asset diversification. Users will be able to deposit GMX as collateral and borrow GMX leading to additional revenue opportunities for Aave.

This publication contains risk paramters provided by Chaos Labs and Gauntlet. The initial forum discussion can be found [here](https://governance.aave.com/t/temp-check-add-gmx-to-arbitrum-v3/12307/8). 

# Specification

The parameters shown below are supported by Gauntlet and Chaos Labs.

Ticker: GMX

Contract Address: [`0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a`](https://arbiscan.io/token/0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a)

Chainlink Oracle GMX/USD [`0

====================================================================================================
[90] id=0xb7f2a599086e7d0fdfde085f5760b15c9980ca0dfa05c4b3432e2ae9aecd5487  token=AAVE  space=aavedao.eth  date=2023-07-05
TITLE: [TEMP CHECK] Safety Module Upgrade Part IV - Incentives Management Upgrade
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Safety Module Upgrade Part IV - Incentives Management Upgrade
author: @Llamaxyz - @dydymoon & @TokenLogic
created: 2023-04-13

---

# Summary

This publication focuses on how incentives are distributed to reduce the overall AAVE spend and enhance the profitability of the Aave DAO.

# Abstract

The current SM incentives budget is 1100 AAVE/day. These rewards allow Aave to attract deposits, where up to 30% can be used to insure the protocol in case of shortfall event. At the moment, 100% of these incentives are spent in liquidity mining from the Ecosystem Reserve, which represents $89.3K daily or $32.6M yearly expense for the DAO.

This publication presents the community with an opportunity to reshape how AAVE incentives are distributed to significantly improve Aave’s economics and enhance the capital efficiency of the SM.

* Increased Backstop Value
* Decreased AAVE Spend
* Increased Yield for depositors
* Improved Profitability and Financial Sustainability

This publication focuses on how incentives are distributed to reduce the overall AAVE spend without exceeding the current AAVE budget & shares the estimated results from the strategy.

# Rationale

A quick recap of proposed from the current design so far:

* Part I - SstkABPT update proposal (Part I)
  * Support of the migration to a new BPT B-80-AAVE-20wstETH

* Part II - Categories implementation (Part II)
  * Single assets, volatile BPTs and stable BPTs.

* Part II- Slashing update (Part II)
  *

====================================================================================================
[91] id=0xe77196bd23ce671930811755d59ae9a285c9e00909b8857181bc327640c049e3  token=AAVE  space=aavedao.eth  date=2023-07-05
TITLE: [TEMP CHECK] Safety Module Upgrade Part V - veToken Holding
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Safety Module Upgrade Part V - veToken Holding Management Framework
author: @Llamaxyz - @dydymoon & @TokenLogic
created: 2023-04-13

---

# Summary

This directional publication presents an opportunity for the community to elect a voting committee and define a framework to manage the DAO’s strategic assets holdings.

# Abstract

This publication presents the community with the opportunity to introduce a voting framework & committee that will conduct votes on veToken and other strategic assets holdings on Aave DAO’s behalf. There are several types of votes in other communities which are high context and time sensitive that can not be automated.

Aave would benefit from optimizing these resources in the most efficient way (i.e: Avoid Curve & Balancer gauges votes weekly on the Aave snapshot and/or management by AIP), and this publication presents the community with an opportunity to establish a voting framework and electing a voting committee.

How the committee is to vote wouldl be determined by an overall global strategy that is agreed/voted upon, by Aave governance.

# Rationale:

As a reminder, veBAL positions offer the following benefits:

* Gauge-weight Power: Voting power which influences emissions on the gauges.

* Governance Power: Voting power in the DAO proposals

* veBoost: Holding veBAL earns a boost up to 2.5x on the liquidity provided.

* Protocol Fees: Part of the trading fees sold for bb-a-USD and claimable by lockers.

This proposal as

====================================================================================================
[92] id=0xf34db3fe2401c061e822177856e55c9df34d065610c29d1ebac1513c3c8eb9ee  token=AAVE  space=aavedao.eth  date=2023-07-10
TITLE: [ARFC] Set Metis Foundation Wallet as Emission Manager for METIS Token on Aave V3 Metis Pool
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
title: [ARFC] Set Metis Foundation Wallet as Emission Manager for METIS Token on Aave V3 Metis Pool
author: @MarcZeller - Aave Chan Initiative
date: 2023-07-05
---

## Summary

This ARFC proposes to set the Metis Foundation wallet as the emission manager for the METIS token on the Aave V3 Metis pool. This will enable the Metis Foundation to define and fund incentive programs for this Aave pool, promoting growth and expanding the user base of this new Aave V3 market.

## Motivation

The Metis Foundation has expressed a desire to actively contribute to the growth and development of the Aave V3 Metis pool. By setting their wallet as the emission manager for the METIS token, the Foundation will be able to directly fund incentive programs that can attract more users to the pool and stimulate activity. This aligns with the broader goals of the Aave community to foster active and engaged markets.

## Specification

The Metis Foundation wallet address is as follows:

Emission Admin Wallet (Metis Foundation): `0x97177cD80475f8b38945c1E77e12F0c9d50Ac84D`

The AIP call setEmissionAdmin() method in the emission_manager contract.

`EMISSION_MANAGER.setEmissionAdmin(METIS, EMISSION_ADMIN);`

This method will set the Metis Foundation wallet as the emission admin for the METIS token.

## Disclaimer

This proposal is powered by Skyward. The Aave Chan Initiative has not been paid by any third party for this proposal.

## Next Steps

1. If Snapshot outcome is YAE, escalate this proposal to

====================================================================================================
[93] id=0x4ec24a25d7d3af6c4d1a9782d791fd1fe2323527d3d8cb23b7c8c41f38d7e462  token=AAVE  space=aavedao.eth  date=2023-07-11
TITLE: [TEMP CHECK] Treasury Management - Introducing StrategicAssetManager
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Treasury Management - Introducing StrategicAssetManager 
author: @Llamaxyz - @TokenLogic, @dydymoon & Fermin
created: 2023-07-05

---

# Summary

The `StrategicAssetManager` is a dedicated contract for managing Aave DAO's strategic assets. At launch the `StrategicAssetManager` will manage the DAO's veBAL holding.

# Motivation

Aave DAO is soon to attain a veBAL holding. To maximise the upside for holding the strategic asset, the DAO needs a practical means of managing the asset.

The veBAL holding needs to be continually relocked to optimise goverance and rewards. Gauge votes are weekly and would require numerous AIPs to manage the veBAL effectively. Aave DAO also has an opportunity to participate in Balancer's governance on Snapshot votes via delegating governance rights.

The StrategicAssetManage will also hold the sdCRV position if approved by AIP. Yield generated from each strategic holding can be claimed, swapped and redeposited to compound into each strategy over time. The swaps have MEV protection and can be customised to have defined maximum amount of price impact.

Given the sheer volume and frequency of transactions to be performed, there exists a desire to minimum AIP votes. The StrategicAssetManager contains the ability for the `ShortExecutor` to assign an `AssetManager`. This role can be likened to a Treasury Committee (as suggested Part 4 of SM upgrade publications) and provides the DAO optionality to introduce a committee separte from

====================================================================================================
[94] id=0x60d44523a63e022fcca2f54aa3b84977e49fec0bdf15c9a298122422f6dd5902  token=AAVE  space=aavedao.eth  date=2023-07-12
TITLE: [ARFC] Aave V3 Deployment on BNB Chain
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARFC] Aave V3 Deployment on BNB Chain

Author: @marczeller - Aave-Chan Initiative

Date: 2023-04-04

## **Summary**:

This ARFC proposes the deployment of Aave V3 on the BNB Chain, expanding Aave's presence and tapping into the growing DeFi ecosystem and user base of BNB Chain.

## **Abstract**:

Upon approval by the Aave community, Aave V3 will be deployed on the BNB Chain with a selection of suitable assets for collateral, including BNB, WBTC, BETH, WETH, USDC, and USDT. This deployment aims to enhance the growth and collaboration between the Aave and BNB Chain communities, providing new opportunities for both ecosystems.

## **Motivation**:

Deploying Aave V3 on the BNB Chain presents potential benefits for both Aave and BNB Chain ecosystems. Aave would gain access to BNB Chain's user base, DeFi ecosystem, and potential additional revenue. In return, BNB Chain would benefit from having a flagship DeFi project like Aave on its platform, further diversifying DeFi options available to its users.

## **Specification**:

The ARFC suggests deploying Aave V3 on the BNB Chain with the following assets for collateral: CAKE, BNB, BTCB, WETH, USDC, and USDT. The table below provides the suggested risk parameters for each asset.

|Risk Parameter|CAKE|BNB|BTCB|WETH|USDC|USDT|
|---|---|---|---|---|---|---|
|Isolation Mode|YES|NO|NO|NO|NO|NO|
|Enable Borrow|NO|NO|YES|YES|YES|YES|
|Borrowable in Isolation|NO|NO|NO|NO|YES|YES|
|Enable Collateral|YES|YES|YES|YES|YES|YES|
|Emode Cate

====================================================================================================
[95] id=0x824b68306034ca6c86d45a2ad7911f45408be0466d6a60b95b67fd0aebc410f9  token=AAVE  space=aavedao.eth  date=2023-07-26
TITLE: [ARFC] GHO Liquidity Pools: Primary Pools Initial Strategy
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] GHO Liquidity Pools: Primary Pools Initial Strategy
author: @TokenLogic - @Dydymoon & @MatthewGraham 
created: 2023-07-20

---

# Summary

This publication presents the community with an initial repartition of the veBAL gauge weight power to different GHO primary liquidity pools

Additionally to the DAO voting power, several ecosystem members expressed interest in supporting GHO, pushing the estimated voting power up to ~ 7,7% of the veBAL voting supply.

# Motivation

Following on from a successful [Snapshot vote](https://snapshot.org/#/aave.eth/proposal/0xcf85642329d2f1f54ae8a55bf272e4fa6e231dee3759907f9c2a0d9447cee311) and [B-80BAL-20WETH acquisition](https://twitter.com/CoWSwap/status/1678498134195044361?s=20), the three primary Balancer liquidity pools have been defined and gauge proposals have been submitted with voting ongoing.

* [[BIP-357] Enable GHO/LUSD Gauge [Ethereum]](https://forum.balancer.fi/t/bip-357-enable-gho-lusd-gauge-ethereum/4963)
* [[BIP-358] Enable GHO/wstETH Gauge [Ethereum]](https://forum.balancer.fi/t/bip-358-enable-gho-wsteth-gauge-ethereum/4964)
* [[BIP-360] Enable GHO/bb-a-USD Gauge [Ethereum]](https://forum.balancer.fi/t/bip-360-enable-gho-bb-a-usd-gauge-ethereum/4965)

After discussion with other teams, two initial secondary pool gauges have been proposed. However, in line with the [TEMP CHECK](https://governance.aave.com/t/temp-check-gho-liquidity-pools/13655), the DAO’s veBAL holding should be used to support the three pri

====================================================================================================
[96] id=0xa8b018962096aa1fc22446a395d4298ebb6ca10094f35d072fbb02048e3b5eab  token=AAVE  space=aavedao.eth  date=2023-07-27
TITLE: [ARFC] Aave V3 Deployment on Base
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARFC] Aave V3 Deployment on Base

Author: @fig - Flipside Crypto

Date: 07-27-2023

---

## **Summary:**

This ARFC proposes the deployment of Aave V3 on the Base upon Mainnet launch, expanding Aave’s presence and tapping into the future growth, budding DeFi ecosystem, and unique users home to Base.

## **Abstract:**

When / if approved by the Aave community, Aave V3 will be deployed on Base Mainnet with a selection of assets for collateral, including wETH, wstETH, cbETH, and USDC. 

This deployment aims to expand Aave to a new ecosystem, capturing the growth and infrastructure allowed by Coinbase’s products and distribution -- providing new opportunities for both ecosystems.

## **Motivation:**

By enabling Base on Aave, it creates valuable (and differentiated) revenue opportunities for Aave, capturing the growth and interest of users who live on the Coinbase platform.

This allows Aave to leverage Coinbase integrations, fiat onramps, and access to 110mm+ users and $80B+ assets in the Coinbase ecosystem.

For Base, deploying Aave V3's codebase expands the on-chain experience by fostering a diversity of DeFi platforms and introducing trusted, flagship lending protocols.

## **Specification:**

The ARFC suggests deploying Aave V3 on Base with the following assets for collateral: wETH, wstETH, cbETH, and USDC. 

The table below illustrates the initial suggested risk parameters for each asset, a combination of reccomendations provided by @Gauntlet and @ChaosLabs.

|Risk

====================================================================================================
[97] id=0x0be8229173181fe0aaf5ed1883e53752546efb810e55610e7ac8b991155ab788  token=AAVE  space=aavedao.eth  date=2023-08-07
TITLE: [TEMP CHECK] Treasury Management - Avalanche v2 to v3 Migration
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Treasury Management - Avalanche v2 to v3 Migration
Author: @TokenLogic
Created: 2023-08-01

---

# Summary

This publication proposes redeeming all Aave DAO funds on Aave v2 Avalanche and depositing the underlying assets into Aave v3 Avalanche. 

# Motivation

Aave DAO currently holds around $4.58M on Avalanche v2. The publication supports redeeming the assets shown below from v2 Avalanche and deposit them in v3 Avalanche. 

![](https://hackmd.io/_uploads/S1JfO0Uo3.png)

The deposit rates on v3 are great than v2 and there is also wAVAX incentives being distributed across v3.

Upon assessing the utilisation of each applicable reserve on v3, there is sufficient Supply Cap capacity to support the migration of funds. Do note, the borrow rate on v2 will increase in response to migrating funds from v2.  

Transferring the DAOs funds from v2 to v3 can be performed via the migration tool developed by @bgdlabs. There are also smaller holdings, example: wAVAX, that can be deposited to earn yield. This proposal will result in ~8.3% of the TVL on v2 being migrated to v3. 

For reference, the Aave Avalanche v2 Treasury: [`0x5ba7fd868c40c16f7aDfAe6CF87121E13FC2F7a0`](https://snowtrace.io/address/0x5ba7fd868c40c16f7aDfAe6CF87121E13FC2F7a0)

# Specification

Perform the following:

* Transfer funds from v2 to v3 via migration tool
* Deposit passively held assets into v3 

# Disclaimer

TokenLogic receives no payment from Aave DAO or any external source for the creati

====================================================================================================
[98] id=0x7889339ebc62182cacccc69efbbf46902995eb4f35f6cf62724ba6aaad3933c7  token=AAVE  space=aavedao.eth  date=2023-08-21
TITLE: [TEMP CHECK] Aave Treasury Proposal for RWA Allocation
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
**Title:** Aave Treasury Proposal: Onboard with Centrifuge Prime to invest in RWA
**Author:** @Khan
**Date:** Aug 21, 2023



### **Summary**

This proposal requests that a portion of the Aave Treasury’s stablecoin holdings be allocated to a low-risk RWA investment through Centrifuge Prime.

This will allow Aave to earn yield on idle stablecoins, establish long-term RWA infrastructure for the protocol, and allow the Aave DAO to begin building internal familiarity and expertise in this market. The Aave Treasury will primarily benefit from an allocation into uncorrelated and differentiated collateral beyond crypto native assets.

The main results of this proposal:

1. Aave will onboard to Centrifuge Prime to establish the legal and technical infrastructure for the Aave treasury to invest in RWA
2. Aave Treasury to allocate to RWA, with an initial investment of 1M USDC into short-duration US treasuries, increasing to a target allocation of up to 20% of stablecoin holdings, and with the option to extend to other yields subject to Aave governance approval.

### **Motivation**

Aave has long been a contributor and supporter of RWA initiatives. Since the first announcement of GHO, the Aave community has consistently expressed its interest in expanding into this area. Treasury Management at Aave has historically been focused on strategic crypto assets, overlooking the returns and liquidity available in offchain markets. 

Today, with roughly 65% of the treasury in USDC (~15m USD), th

====================================================================================================
[99] id=0x659d9d54c19fb6b00e1b6061331d3d7d5d5ceab552c76e24dc1a6fe9a15d2c8d  token=AAVE  space=aavedao.eth  date=2023-08-22
TITLE: [TEMP CHECK] Aave V3 "MVP" Deployment on GnosisChain
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title : [TEMP CHECK] Aave V3 "MVP" Deployment on GnosisChain

Author : Marc Zeller @marczeller - Aave Chan Initiative

Date : 2023-08-16

---

## Summary

This TEMP CHECK proposes the deployment of an Aave V3 pool on GnosisChain. The assets considered for this deployment include wETH, wstETH, GNO, USDC, wxDAI, and EURe.

## Motivation

Aave & GnosisChain with the upcoming deployment of GnosisPay L2 payment system and GnosisCard product have strategic synergies opportunities. Allowing users to “deposit as collateral, borrow and spend with Gnosis” seamless and near-zero fees experience.

GnosisChain has been a historic actor in the ecosystem, with its roots tracing back to the POA network. 

This proposal builds upon the precedent of synergies between the Aave codebase and the gnosischain as illustrated by the friendly fork RMM Market with RealT, as seen [here](https://rmm.realtoken.network/).

This “MVP” deployment opens the gates for deeper synergies between the Gnosis & Aave ecosystems in the future.

## Specification

The proposed deployment on GnosisChain will include the following assets:

| Risk Parameter | wETH | wstETH | GNO | USDC | wxDAI | EURe |
| --- | --- | --- | --- | --- | --- | --- |
| Isolation Mode | NO | NO | YES | NO | NO | NO |
| Enable Borrow | YES | YES | NO | YES | YES | YES |
| Enable Collateral | YES | YES | YES | YES | YES | NO |
| Emode Category | N/A | N/A | N/A | N/A | N/A | N/A |
| Loan To Value | 80.5% | 69% | 25% | 77% | 77% | N/A |
| Liqui

====================================================================================================
[100] id=0xfe17ba406d90f8308794d14e8cad4f8d44c1f74e5589a5a106f9af17df916a59  token=AAVE  space=aavedao.eth  date=2023-08-28
TITLE: [ARFC] Treasury Management - Avalanche v2 to v3 Migration
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - Avalanche v2 to v3 Migration
author: @TokenLogic
created: 2023-08-28

---

# Summary

This publication proposes redeeming all Aave DAO funds on Aave v2 Avalanche and depositing the underlying assets into Aave v3 Avalanche. 

# Motivation

This publications progresses the [[TEMP CHECK] proposal](https://snapshot.org/#/aave.eth/proposal/0x0be8229173181fe0aaf5ed1883e53752546efb810e55610e7ac8b991155ab788) to migrate Aave DAO's funds from Avalanche v2 to v3.

Aave DAO currently holds around $4.58M on Avalanche v2. The publication supports redeeming the assets shown below from v2 Avalanche and deposit them in v3 Avalanche. 

 
![Screenshot 2023-08-28 at 09.23.18.png](ipfs://bafkreiggndqcywgealtinsz7yu3s6e7fmpkcla6r5r6fyqnsjd6jrxt6oi)
    

The deposit rates on v3 are great than v2 and there is also wAVAX incentives being distributed across v3.

If required, this proposal is to be implemented via multiple AIPs to ensure there is sufficient Supply Cap capacity to enable funds to be deposited into v3. 

Do note, the borrow rate on v2 will increase in response to migrating funds from v2.  

Transferring the DAOs funds from v2 to v3 can be performed via the migration tool developed by @bgdlabs. There are also smaller holdings, example: wAVAX, that can be deposited to earn yield. This proposal will result in ~8.3% of the TVL on v2 being migrated to v3. 

For reference, the Aave Avalanche v2 Treasury: [`0x5ba7fd868c40c16f7aDfAe6CF87121E13FC2F7a0`](

====================================================================================================
[101] id=0x3c133c1699da0cfd075b214483671bf83cdb24bcd391859dcd09d37e2d7e32ad  token=AAVE  space=aavedao.eth  date=2023-08-28
TITLE: [ARFC] Return OP to Aave Grants DAO Safe
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARFC] Return OP to Aave Grants DAO Safe

Date: 08-28-2023

Author: @corbpage

-----

### Description: 

Aave Grants DAO (AGD) was airdropped 300k OP from Optimism to allocate towards grants (OP proposal from May ‘22). While claiming these tokens, they were erroneously sent to the Aave Guardians Safe, instead of the AGD Safe. This proposal is to send the OP back to AGD from the Aave Guadians Safe.

Full context in forum post.👇

====================================================================================================
[102] id=0xeb88691a23f3b1f9dfb4d2fb575fa19e75050a67b80b23eff91c0d430a177bd1  token=AAVE  space=aavedao.eth  date=2023-09-03
TITLE: [ARFC] Treasury Management - Acquire AURA
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - Acquire AURA 
author: @TokenLogic & @MarcZeller (ACI)
created: 2023-08-29

---

# Summary

This publication proposes Aave DAO acquire 443,674 AURA from Olympus DAO for 420,159.28 units of DAI.

# Motivation

Over the next few months the veBAL and vlAURA being used to support GHO pools will reduce as voters shift there focus away from GHO. The initial commit from the Aura Finance team was 400,000 units of vlAURA for an initial 3 month duration.

This proposal seeks to replace the support from Aura Finance by acquiring 443,674 units of AURA from Olympus DAO. Olympus DAO is reducing there AURA exposure due to change in the Olympus DAO roadmap which is detailed [here](https://forum.olympusdao.finance/d/3756-towards-a-fully-autonomous-olympus) and [her](https://forum.olympusdao.finance/d/3967-tap29-aura-solicitation-to-bid).

Based upon the research presented in this [Update Balancer Ecosystem Holdings](https://governance.aave.com/t/temp-check-update-balancer-ecosystem-holdings/14682), which details impact AIP-42 by Aura Finance, the most efficient way for Aave DAO to bootstrap GHO is via vlAURA relative to veBAL. 

Olympus DAO seeks payment in DAI, at an exchange rate of 0.9470 DAI per unit of AURA. The amount of AURA is 443,674 with a total cost to Aave DAO of 420,159.28 units of DAI. Aave DAO currently holds [2.873M](https://etherscan.io/token/0x028171bca77440897b824ca71d1c56cac55b68a3?a=0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c) units

====================================================================================================
[103] id=0x53728c0416a9063bf833f90c3b3169fa4387e66549d5eb2b7ed2747bfe7c23fc  token=AAVE  space=aavedao.eth  date=2023-09-03
TITLE: [ARFC] Treasury Management - Replace AGD's DAI Allowance with GHO Allowance
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - Replace AGD's DAI Allowance with GHO Allowance
author: @TokenLogic & @0xlide + @0xbilll 
created: 2023-08-25

---

# Summary

To promote the adoption and usage of GHO, this publication proposes replacing Aave Grants DAO's (AGD) DAI allowance with a GHO allowance. 

# Motivation

The AGD has $377,938.79 unclaimed DAI remaining.

![](https://hackmd.io/_uploads/r1Ax40Qa3.png)

This publication proposes replacing AGD's existing DAI allowance with a new GHO allowance. This will enable AGD contributors and grant recipients to be rewarded with GHO, and any other asset held in the AGD's multisig. 

With GHO trading beneath $1, the Aave DAO can acquire GHO on market which will help support the peg and then use the GHO to provide funding to AGD. Distributing GHO  will promote the usage and adoption of GHO.

The Aave DAO is sending a strong signal of support for GHO by using it to reward contributors to the community. Over time, we hope all AGD and Service Provider expenses are settled in GHO.

This proposal will likely be implemented around the time the ARFC to increase [GHO's interest rate](https://governance.aave.com/t/arfc-increase-gho-borrow-rate/14612) is to be implemented and the issue flagged [here](https://governance.aave.com/t/temporarily-pausing-gho-integration-in-aave/14626) has been resolved. Both proposals are expected to help support the GHO peg.

# Specification

The following assets from the Treasury are to be swapped to GHO. 

*

====================================================================================================
[104] id=0xd41eebb9d9150f1d4ec106e8117809b78a4841641a18cd0ad47b5d31f6b6bf86  token=AAVE  space=aavedao.eth  date=2023-09-03
TITLE: [ARFC] Quarterly Gas Rebate Distribution - August 2023
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARFC] Quarterly Gas Rebate Distribution - August 2023
Author: Marc Zeller (@marczeller) - Aave Chan Initiative (ACI)
Date: 2023-09-04

---

## Summary:
This ARFC proposes the quarterly gas rebate distribution for recognized delegates. The distribution aims to reimburse the gas costs incurred by delegates during their participation in Aave governance.

## Motivation:
Recognized delegates play a crucial role in Aave governance by actively participating in proposal discussions, voting, and other governance activities. These activities often involve gas costs, especially when interacting with the Ethereum network. The Aave community established a quarterly gas rebate distribution to incentivize and support their continued participation.

## Specification:
The following table provides a breakdown of the total gas used by each recognized delegate and the corresponding ETH amount to be distributed:

| Name             | Total Gas Spent          |
|------------------|--------------------------|
| ACI              | 1.35      |
| HKTrust          | 0.07     |
| TokenLogic       | 0.50     |
| michigan         | 0.11     |
| LBS Blockchain   | 0.18     |
| Wintermute       | 0.15     |
| keyrock          | 0.14     |
| Stablelab        | 0.20     |
| **Total ETH** | **2.7 ETH** | 



### Notes:
1. @Alice forked and edited the flipside script to improve it & increase accuracy to track voting participation. here's the new script : https://dune.com/queries/2970451
2. The voting re

====================================================================================================
[105] id=0x456c2eb7f40ef7b0d132a111cbaeb023311c1b1bd5c8c78a6a81d4685116e309  token=AAVE  space=aavedao.eth  date=2023-09-07
TITLE: [TEMP CHECK] Update Balancer Ecosystem Holdings
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---------------------------------------------------------------------------------------------------
Title: [TEMP CHECK] Update Balancer Ecosystem Holdings

Author: @Dydymoon

Date: 2023-08-29

---------------------------------------------------------------------------------------------------
## Summary

Explain AIP-42 proposal & gauge the community thoughts to update the strategic assets from veBAL to an alternative solution increasing the emission power considering current metrics.

## Background

In March 2022, Llama proposed a strategic partnership with Balancer (Part I & Part II). The DAO used the BAL to buy B-80BAL-20WETH LP tokens, that would be locked for veBAL. This position was meant to be used for its emission power, enabling rewards redirection on AAVE & GHO gauges.

This estimated veBAL position & market metrics at the time were taken into account for the SM upgrade proposals (which includes migrating the current LPs to Balancer V2, implement new categories & slashing parameters, define the smBPT gauges, updates incentives management, create a strategic asset management framework, and further considerations.)

Considering that veBAL was likely to be needed before the SM upgrade implementation, Llama introduced the StrategicAssetsManager contract, creating a base framework to manage assets from Goverance or with a committee. The TEMP check vote ended mid July, and the contract was submitted to BGD for review after.

From Llama’s side, the code supporting veBAL posi

====================================================================================================
[106] id=0x294d7c2aa95222e444f5e971348538e43066c02f2ac0fcf159293cecc3ac5c7c  token=AAVE  space=aavedao.eth  date=2023-09-11
TITLE: [TEMP CHECK] Update Balancer Ecosystem Holdings
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
-----------------------------------------------------------------------------------------------
Title: [TEMP CHECK] Update Balancer Ecosystem Holdings

Author: @Dydymoon

Date: 2023-08-29

-----------------------------------------------------------------------------------------------
*Proposal resubmitted as the last vote didn't reached the quorum.*

# Summary
Explain AIP-42 proposal & gauge the community thoughts to update the strategic assets from veBAL to an alternative solution increasing the emission power considering current metrics.

# Background
In March 2022, Llama proposed a strategic partnership with Balancer (Part I & Part II). The DAO used the BAL to buy B-80BAL-20WETH LP tokens, that would be locked for veBAL. This position was meant to be used for its emission power, enabling rewards redirection on AAVE & GHO gauges.

This estimated veBAL position & market metrics at the time were taken into account for the SM upgrade proposals (which includes migrating the current LPs to Balancer V2, implement new categories & slashing parameters, define the smBPT gauges, updates incentives management, create a strategic asset management framework, and further considerations.)

Considering that veBAL was likely to be needed before the SM upgrade implementation, Llama introduced the StrategicAssetsManager contract, creating a base framework to manage assets from Goverance or with a committee. The TEMP check vote ended mid July, and the contract was submitted to BGD for review a

====================================================================================================
[107] id=0x71db494e4b49e7533c5ccaa566686b2d045b0761cb3296a2d77af4b500566eb0  token=AAVE  space=aavedao.eth  date=2023-09-12
TITLE: [ARFC] Aave Treasury Proposal for RWA Allocation
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
**Title:** Aave Treasury Proposal: Onboard with Centrifuge Prime to invest in RWA

**Author:** @Khan 

**Date:** Sep 12, 2023

---

### **Summary**

This proposal brings on Centrifuge as a service provider to the Aave DAO to setup a legal structure to support RWA investments, develop RWA specific management and governance processes, and allocate $1M of the Aave Treasury’s stablecoin holdings to a liquid US T-Bill fund on Centrifuge, as a proof of concept investment.

This is a first step towards a long term effort for Aave to develop and launch an RWA Facilitator that will back GHO with Real World Assets. With this proposal Aave can earn yield on idle stablecoins, establish long-term RWA infrastructure for the protocol, and allow the Aave DAO to begin building internal familiarity and expertise in the RWA industry.

The proposal minimizes upfront cost and completely recoups the initial investment within 6-12mo and starts earning yield for Aave within the first 3mo. It locks up no long term capital and leaves the DAO in full control over the treasury allocation.

The main results of this proposal:
1. Aave will onboard to Centrifuge Prime to establish the legal and technical infrastructure for the Aave protocol to invest in RWAs.
1. Through Prime, the Aave Treasury will allocate $1M of USDC to the Anemoy LTF, a short-duration US treasury bill pool on Centrifuge.

### **Motivation**

Aave has long been a contributor and supporter of RWA initiatives. Since the first announcement

====================================================================================================
[108] id=0x0c7fc4246c5795a9d9901c08a9a8279e7e6ed1069f2155fe48239c92e4e43193  token=AAVE  space=aavedao.eth  date=2023-09-13
TITLE: [ARFC] - Chaos Labs Risk Parameter Updates - Aave V3 Avalanche - 2023.09.06
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Simple Summary

A proposal to adjust five (5) total risk parameters, including Loan-to-Value, Liquidation Threshold and Liquidation Bonus across three (3) Aave V3 Avalanche assets.

## Motivation

Chaos Labs’ Parameter Recommendation Platform runs hundreds of thousands of agent-based off-chain and on-chain simulations to examine how different Aave V3 risk parameters configurations would behave under adverse market conditions - and find the optimal values to maximize protocol borrow usage while minimizing losses from liquidations and bad debt. 

Please find more information on the parameter recommendation methodology [here](https://community.chaoslabs.xyz/aave/recommendations/methodology).

You can also view the simulation results and breakdown for the different assets by clicking on them on this [page](https://community.chaoslabs.xyz/aave/risk/markets/Avalanche/recommendations).

The output of our simulations reveals an opportunity to optimize parameters for WAVAX, sAVAX and LINK.e on V3 Avalanche, resulting in improved capital efficiency of the system, with a negligible effect on the projected VaR (95th percentile of the protocol losses that will be accrued due to bad debt from under-collateralized accounts over 24 hours) and EVaR (Extreme VaR, the 99th percentile of the protocol losses that will be accrued due to bad debt from under-collateralized accounts over 24 hours)

**Simulating all changes jointly yields a projected borrow increase of ~$26K, with a negligible incr

====================================================================================================
[109] id=0xecd62eb5dca71e47e7e1d0e88f8e6127857c051bea190fe0eb665636b33caa62  token=AAVE  space=aavedao.eth  date=2023-09-17
TITLE: Title: [ARFC] Expansion of "Orbit" - A DAO Funded Delegate Platform Initiative
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

### Title: [ARFC] Expansion of "Orbit" - A DAO Funded Delegate Platform Initiative
### Author: Marc Zeller @marczeller - Aave Chan Initiative
### Date: 2023-09-07

---

## Summary:

This ARFC proposes the expansion of the ["Orbit" delegate platform initiative](https://governance.aave.com/t/introducing-orbit-a-delegate-platform-funding-initiative-by-aci/13241), transitioning it from being funded by the Aave-Chan Initiative (ACI) to being funded by the Aave DAO. The goal is to enhance the sustainability and independence of the program, ensuring continued support for active delegates in the Aave community.

## Motivation:

The pilot phase of Orbit, funded by ACI, has been a success in its first quarter. Recognizing its positive impact, there's a need to expand and generalize the program, ensuring its longevity and alignment with the broader Aave community goals.

## Specification:

The proposed funding for the Orbit initiative remains at $5,000 per month, with payments to be made in GHO stablecoin. Orbit operates on a quarterly basis, with eligibility criteria defined for each quarter.

For the upcoming quarter, the eligibility criteria will mirror that of the [[ARFC] Quarterly Gas Rebate Distribution - August 2023](https://governance.aave.com/t/arfc-quarterly-gas-rebate-distribution-august-2023/14680). In subsequent quarters, a threshold of voting power and diversity of delegation will be introduced to ensure the program's integrity and to prevent potential abuse. To fund

====================================================================================================
[110] id=0x8023477ae0364be4df4a24b5ef633bdd49121db0ceeacff6322872d557c7239b  token=AAVE  space=aavedao.eth  date=2023-09-17
TITLE: [TEMP CHECK] Treasury Management - Swap B-80BAL-20wETH to GHO
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Treasury Management - Swap B-80BAL-20wETH to GHO 
author: @TokenLogic
created: 2023-09-17

---

# Summary

This publication proposes swapping B-80BAL-20wETH for 420,000 GHO.

# Motivation

The Aave DAO is completed the purchase of 443,674 units of AURA from Olympus DAO with 420,159.28 units of DAI. This publication proposes replenishing the DAO's stable coin holdings by swapping B-80BAL-20wETH for 420,000 GHO. The net affect of the two proposals is to convert B-80BAL-20wETH to AURA.

Details on the DAI for AURA swap can be found [here](https://app.aave.com/governance/proposal/317/).

# Specification

This proposal will deploy use a version of the Aave Swap Contract and perform the following:

* Transfer B-80BAL-20wETH from Treasury to Aave Swap Contract
* Swap B-80BAL-20wETH to GHO 
* Transfer GHO to the Ethereum Treasury

# Disclaimer

TokenLogic receives no payment from Aave DAO or any external source for the creation of this proposal. TokenLogic is a delegate within the Aave ecosystem. TokenLogic seeks to become an Aave DAO Service Provider.

# Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

====================================================================================================
[111] id=0x556aa2b8439dba5929e613fb5515279d8396621e71fba058912434a60751fbd4  token=AAVE  space=aavedao.eth  date=2023-09-17
TITLE: [TEMP CHECK] Treasury Management - Create and Fund GHO Liquidity
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Treasury Management - Create and Fund GHO Liquidity Committee
Author: @TokenLogic
Dated: 2023-09-08

---

# Summary

This publication presents Aave DAO the opportunity to create and fund the GHO Liquidity Committee for an initial 3 month duration.

# Motivation

Over the coming weeks, we expect the voting base to reallocate gauge votes away from GHO liquidity pools. This is largely due to those voting for GHO pools incurring an opportunity cost by not participating in the bribe market.

If the Aave DAO was to lock all of its BPT for veBAL, the gauge vote is equivalent to 1.8% of veBAL. Even with some voters continuing to support GHO, a good portion of the 7.7% will move to other pools. There is also the impact of [AIP-42](https://governance.aave.com/t/temp-check-update-balancer-ecosystem-holdings/14682) for the DAO to consider. Voting support from external teams is expected to taper beyond what Aave DAO can replace with its own strategic assets. Furthermore, as the liquidity pools continue to grow additional gauge voting support is required to maintain the APR over time. Whilst the Aave Safety Module (SM) has the potential to be a more long term sustained solution, integrating BPTs that contain GHO, this requires time to develop and should not be rushed.

Meanwhile, the [GHO price](https://aave.tokenlogic.com.au/) is consistently trading between 96 cents and 99 cents. When the liquidity in the GHO/Aave Boosted Pool was withdrawn, the GHO peg improved.

====================================================================================================
[112] id=0x225c33775892d959715f85e0c3edb61966fe7e67b1dd474d0ee28fea533dc2c9  token=AAVE  space=aavedao.eth  date=2023-09-18
TITLE: [ARFC] Treasury Management - GHO Liquidity Strategy Update
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Treasury Management - GHO Liquidity Strategy Update
Author: @TokenLogic
Dated: 2023-09-08

---

# Summary

This publication details the revised liquidity strategy for GHO across Ethereum DeFi.

# Motivation

This publication outlines the GHO liquidity strategy with two main objectives:

* Improve GHO peg
* Promote diversified liquidity across multiple exchanges

It is widely accepted that the GHO peg requires improvement. This was especially evident when GHO traded at beneath 96 cents.

Furthermore, several liquidity pools have come about organically on Maverick, Uniswap and Curve. Similar to the Balancer pools, these pools are mostly GHO which is reflective of the GHO price relative to the stable coin being paired within each pool.

Do note, the existing Balancer pools are not being supported by Aave DAO. These pools are being supported by veBAL and vlAURA holders, mostly from contributors within each community.

The two initial pools being considered are GHO/USDT/USDC and GHO/LUSD until SM integration. This will be presented in a separate forum publication for future discussion. This publication will outline the Primary and Secondary Pools being proposed for GHO:

* Balancer GHO/USDC/USDT - Primary
* Balancer GHO/LUSD - Primary
* Maverick GHO/LUSD Static - Secondary
* Maverick GHO/LUSD Both - Secondary
* Uniswap (Bunni) GHO/USDC Wide - Secondary
* Uniswap (Bunni) GHO/USDC Narrow - Secondary
* Curve Finance GHO/crvUSD - Secondary

For the purpose of this p

====================================================================================================
[113] id=0xcf46924fb907fb35f15f0612fadc45dcee6f169a13dd27b2e172738b83a4871c  token=AAVE  space=aavedao.eth  date=2023-09-21
TITLE: [TEMP CHECK] Add KNC to Ethereum Aave V3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
This proposal seeks to add KNC (Kyber Network Crystal) to Aave v3 on Ethereum.

Authors: Maxax; Shane

Date: 12/09/2023

## References

* Project website: https://kyberswap.com/
* Documentation: https://docs.kyberswap.com/
* Github / source code: https://github.com/KyberNetwork
* Ethereum contracts: [0xdeFA4e8a7bcBA345F687a2f1456F5Edd9CE97202](https://etherscan.io/token/0xdeFA4e8a7bcBA345F687a2f1456F5Edd9CE97202)
* Chainlink Oracle - KNC/USD Price Feed :[ 0xf8ff43e991a81e6ec886a3d281a2c6cc19ae70fc](https://data.chain.link/ethereum/mainnet/crypto-usd/knc-usd)

Audits:

Because we are limited in the number of links, please find more information on our docs.

* KyberDAO & KNC audit by Hacken
* KyberSwap Elastic protocol audit by ChainSecurity
* KyberSwap Classic protocol audit by ChainSecurity

## Summary

KyberSwap (Kyber Network’s flagship product) is a multi-chain DEX aggregator + concentrated liquidity platform, which aims to offer superior rates for traders and capital efficient returns for liquidity providers.

Kyber launched on Ethereum in February 2018 and is a pioneer in the DeFi space, developing one of the earliest decentralized exchange protocols (DEX) with Vitalik Buterin as an advisor. The team spearheaded the launch of WBTC (Wrapped Bitcoin) - the most popular ERC20 version of Bitcoin today (and a collateral asset on Aave V2 & V3), as well as developing liquidity pools on KyberSwap that offers concentrated liquidity and capital efficiency for any token pair. Kyber

====================================================================================================
[114] id=0x8fd34012029bec536f779b7bf46813beb57f42705b24acaf239e42353ddf7b8c  token=AAVE  space=aavedao.eth  date=2023-09-22
TITLE: [ARFC] Aave V3 Deployment on zkEVM L2
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

**Title:** [ARFC] Aave V3 Deployment on zkEVM L2

**Author:** @marczeller - Aave-Chan Initiative

**Date:** 2023-09-22

---

## **Summary:**

Proposal for the deployment of Aave V3 on zkEVM L2, with limited assets onboarding ("MVP V3") to establish a strategic Aave presence early in this new network while staying conservative in terms of risk.

## **Abstract:**

This ARFC proposes the deployment of a Minimal Viable Product (MVP) version of Aave V3 on the zkEVM L2 network, an EVM-equivalent zk-rollup developed by the Polygon team.

## **Motivation:**

The deployment of Aave V3 on zkEVM L2 aims to establish a strategic presence on this new network early on, promoting L2 diversity and expanding Aave's reach in the DeFi space.

## **Specification:**

The proposal outlines the deployment of Aave V3.0.1 on zkEVM L2 with three collaterals (WETH, WMATIC & USDC) and one borrowable asset (USDC). Risk parameters are provided for community discussion and feedback from risk service providers.

## Recommended Initial Parameters

| Risk Parameter | WETH | USDC | WMATIC |
| --- | --- | --- | --- |
| Isolation Mode | NO | NO | NO |
| Enable Borrow | YES | YES | YES |
| Borrowable in Isolation | NO | YES | NO |
| Enable Collateral | YES | YES | YES |
| Loan To Value | 80% | 77% | 68% |
| Liquidation Threshold | 82.5% | 80% | 73% |
| Liquidation Bonus | 5% | 5% | 10% |
| Reserve Factor | 15% | 10% | 20% |
| Liquidation Protocol Fee | 10% | 10% | 10% |
| Borrow Cap | 280 | 1.26M | 375K |
|

====================================================================================================
[115] id=0xb094cdc806d407d0cf4ea00e595ae95b8c145f77b77cce165c463326cc757639  token=AAVE  space=aavedao.eth  date=2023-09-22
TITLE: [ARFC] Treasury Management - GHO Funding
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - GHO Funding
author: @TokenLogic
created: 2023-09-17

---

# Summary

This publication seeks to acquire GHO from secondary markets to support the Aave DAO's short-term funding needs.

# Motivation

The objective of this publication is to further transition Aave DAO's expenses towards being nominated in GHO. The below highlights some potential use cases for GHO:

* 870,000 over 6 months [Aave Grants Continuation Proposal](https://governance.aave.com/t/temp-check-aave-grants-continuation-proposal/14831)
    * Another 300,000 GHO if AAVE is replaced with GHO
* 75,000 GHO over 3 months [Expansion of “Orbit”](https://governance.aave.com/t/arfc-expansion-of-orbit-a-dao-funded-delegate-platform-initiative/14785)
* 406,000 GHO over 3 months [GHO Liquidity Committee](https://governance.aave.com/t/temp-check-treasury-management-create-and-fund-gho-liquidity-committee/14800)
* TBA Future ACI Funding Request (Renewal mid-October)

Although the GHO Liquidity Committee is funded via its own AIP, its inclusion here indicates the magnitude of the potential ongoing spend. The current ACI funding proposal is 250,000 aUSDT, which serves only as a budgetary estimate. Similarly, the 406,000 over the back 3 months of a 6-month lookahead is used as a budgetary estimate.

The spend identified above over the next 6 months is 1.676M GHO, or 1.976M GHO if AAVE is replaced with GHO within AGD proposal.

There is also the potential [420,000 GHO](https://governance.

====================================================================================================
[116] id=0xb62c93a8b3590dc46eed92b223da5fcbbf6b52f1f79a0c2fcd80bbc0afea59d8  token=AAVE  space=aavedao.eth  date=2023-09-23
TITLE: [ARFC] Aave V3 Deployment on GnosisChain
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] Aave V3 Deployment on GnosisChain
Author: Marc Zeller @marczeller - Aave Chan Initiative
Date: 2023-08-31
---

## **Summary**:

This ARFC proposes the deployment of Aave V3 on the GnosisChain. Following the positive feedback from the TEMP CHECK, the assets considered for this deployment include wETH, wstETH, GNO, USDC, wxDAI, and EURe.

## **Motivation**:

The GnosisChain, with its historical significance in the ecosystem and its roots in the POA network, presents a valuable opportunity for Aave. The friendly fork RMM Market with RealT on the GnosisChain has already showcased the potential synergies between Aave's codebase and GnosisChain. This ARFC seeks to further these synergies, providing mutual benefits for both ecosystems.

## **Specification**:

The ARFC suggests deploying Aave V3 on the GnosisChain with the following assets and risk parameters:

| Risk Parameter          | wETH  | wstETH | GNO | USDC | wxDAI | EURe |
|-------------------------|-------|--------|-----|------|-------|------|
| Isolation Mode          | NO    | NO     | YES | NO   | NO    | NO   |
| Borrowable in Isolation           | NO  | NO   | NO  | YES  | YES   | NO  |
| Stable Borrow         | NO    | NO     | NO | NO   | NO    | NO   |
| Enable Borrow           | YES   | YES    | NO  | YES  | YES   | YES  |
| Enable Collateral       | YES   | YES    | YES | YES  | YES   | NO   |
| Loan To Value           | 80.5% | 71%    | 31% | 77%  | 77%   | N/A  |
| Liquidation Threshold   | 83

====================================================================================================
[117] id=0x127be8af9854581fdb6565189a0cf351e5ef81d3b4a7ca1e9a059a1994eec6fe  token=AAVE  space=aavedao.eth  date=2023-09-25
TITLE: [TEMP CHECK] Updated Aave Grants Continuation Proposal
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
**Title:** [TEMP CHECK] Updated Aave Grants Continuation Proposal

**Author:** Bill & @0xmigi

**Date:** 09-25-2023

---

Thank you to everyone who participated in the TEMP CHECK: Continue Aave Grants Proposal. This is an updated proposal based on the feedback that was received. The main changes that has been made from the previous proposal are:

* The Events & Sponsorship budget and activities have been removed.
* Swapping the AAVE portion of funding with stables.
* Introducing a $20k max grant size.

# Summary

An opportunity to continue Aave Grants DAO (AGD) for 6 months by preserving the current AGD treasury holdings, providing $400,000 of new funding in ARB, and increasing AGD’s stablecoin allowance by $328,000.

This proposal will enable AGD to deliver and improve upon the top tier grants program the Aave ecosystem has had over the past 2+ years and continue being a gateway for new contributors to the ecosystem. AGD will fund $500,000 in developer grants per quarter, drive Aave’s culture and GHO adoption, and set the groundwork for the next chapter of the continued evolution of AGD.

# Overview

Throughout the previous proposal, AGD has:

* Awarded 50 new grants and made 15 payments to grantees based on milestone completion.

* Engaged builders and the community at five events, including four hackathons where AGD awarded a total of 19 Aave and GHO specific bounties and inspired 58 teams to hack with Aave and GHO.

* Proliferated the ghost by hosting 1 rAAVE to strengthe

====================================================================================================
[118] id=0x4fd764412e30cb038c7758ef739af089f1a59edfbbda7404751350833e3ad91e  token=AAVE  space=aavedao.eth  date=2023-09-25
TITLE: [ARFC] Aave V2 Markets Deprecation Plan
CHOICES: YAE | NAE | Abstain
TEXT (first 1500 characters):
## Summary

A proposal to gradually wind down the frozen markets on Aave V2 Ethereum via a series of LT reductions. This is a snapshot for a direct-to-AIP framework for V2 deprecation recommendations. For more details, see the full forum post [here]( https://governance.aave.com/t/arfc-aave-v2-markets-deprecation-plan/14870).


## Motivation

As part of Gauntlet’s and Chaos’ ongoing commitment to maintaining the highest standards of operation on Aave, we propose to gradually wind down the frozen Aave V2 Ethereum markets via a scheduled series of LT reductions.

This proposal represents the next step in continuous efforts to reduce risk in the V2 markets and encourage the transition to V3. It follows a series of previous proposals, including:

- [[ARFC] Chaos Labs - Incremental Reserve Factor Updates - Aave V2 Ethereum](https://governance.aave.com/t/arfc-chaos-labs-incremental-reserve-factor-updates-aave-v2-ethereum/13766)
- [[ARFC] Freeze CRV on V2](https://governance.aave.com/t/arfc-gauntlet-recommendation-on-freezing-crv-for-aave-v2-ethereum/14428)
- [[ARFC] Chaos Labs Risk Parameter Updates - Aave V2 Ethereum - 2023.6.23](https://governance.aave.com/t/arfc-chaos-labs-risk-parameter-updates-aave-v2-ethereum-2023-6-23/13789)
- [[ARFC] TUSD Offboarding Plan ](https://governance.aave.com/t/arfc-tusd-offboarding-plan/14008)
- [[ARFC] Set CRV LTV to Zero on V2](https://governance.aave.com/t/post-vyper-exploit-crv-market-update-and-recommendations/14214/4)
- [[ARFC] Chaos Labs Ris

====================================================================================================
[119] id=0x219cf8fbfa806b396728b7bf11e635ac4833ce92c9ea8e34f24a686e3cf0d132  token=AAVE  space=aavedao.eth  date=2023-09-26
TITLE: [ARFC] Treasury Manage - GHO Liquidity Committee
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Manage - GHO Liquidity Committee
Author: @TokenLogic
Dated: 2023-09-22

---

# Summary

This publication proposes creating and funding the GHO Liquidity Committee for an initial 3 month duration.

# Motivation

Following on from a success [TEMP CHECK](https://snapshot.org/#/aave.eth/proposal/0x556aa2b8439dba5929e613fb5515279d8396621e71fba058912434a60751fbd4), this publication progresses the creation of the GHO Liquidity Committee to the next step of the Aave governance process. 

Details relating to the committee are shown below:

* [Creation of Committee](https://governance.aave.com/t/temp-check-treasury-management-create-and-fund-gho-liquidity-committee/14800)
* [GHO Liquidity Strategy](https://governance.aave.com/t/arfc-treasury-management-gho-liquidity-strategy-update/14801)
* [Include Sommelier's Turbo GHO Vault](https://governance.aave.com/t/sommelier-turbogho-vault/14821) with further details [here](https://governance.aave.com/t/arfc-treasury-management-gho-liquidity-strategy-update/14801/12)

Update
*Further to the initial proposal GHO Liquidity Strategy, we are revising the Uniswap v3 strategy to include Sommelier's Turbo GHO Vault which actively manages liquidity in the GHO/USDC pool. This amendment will enable the LMC to allocate incentives to the Turbo GHO Vault without increasing the overall budget. The Sommelier team will be co-incentivising the Turbo GHO Vault.* 

# Specification

A Gnosis SAFE will be created and used to manage the

====================================================================================================
[120] id=0xb0124fb0206676ee743e8d6221b7b3c317cb26a657551f11cb5fa23544772a73  token=AAVE  space=aavedao.eth  date=2023-09-29
TITLE: [ARFC] Treasury Management - Amend Safety Module AAVE Emissions
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] Treasury Management - Amend Safety Module AAVE Emissions
Author: @MarcZeller - Aave Chan Initiative & @TokenLogic
Date: 2023-09-24
---

## Summary
This publication proposes reducing AAVE (Safety Incentives) distributions to the Safety Module (SM) by 30% and introducing a 90-day SM emission cycle.

## Motivation
The SM serves as the Aave Protocol’s self-protection smart contract. The Aave Protocol distributes 1,100 AAVE daily, split evenly across AAVE and B-80AAVE-20wETH deposits.

Future proposals shall discuss the composition and aim to improve the overall capital efficiency of the SM. However, this publication intends to reduce AAVE emissions in the immediate future, saving the DAO valuable AAVE emissions while the broader SM upgrade is being advanced. It is widely accepted within the community that Aave DAO is overpaying for AAVE and B-80BAL-20wETH deposits.

This publication proposes reducing AAVE emissions by ~30%. The revised AAVE emission is to be reduced from 1,100 AAVE/day to 770 AAVE/day. This represents a 330 AAVE/day reduction. The APR for stkAAVE holders is expected to reduce from 6.87% to 4.81%. Similarly, for the B-80BAL-20wETH deposits, yield is expected to fall from 14.35% to 10.05%.

Please note that the 80AAVE/20wETH Balancer v1 pool is to be migrated to Balancer v2 in the future. This will present the community with an opportunity to further revise the AAVE emissions. It may also occur at a time when the DAO has vlAURA and/or veBAL at its

====================================================================================================
[121] id=0x94735082d4ba33b53497efb025aa6dbf75a5e4ade71684fd675c03f0e416a294  token=AAVE  space=aavedao.eth  date=2023-09-30
TITLE: [ARFC] Treasury Management - Update Balancer Ecosystem Holdings
CHOICES: YAE (Option 1)  | YAE (Option 2) | YAE (Option 3) | NAY | ABSTAIN
TEXT (first 1500 characters):
--------------------------------------------------------------------------------------------

Title: [ARFC] Treasury Management - Update Balancer Ecosystem Holdings

Author: @Dydymoon

Date: 2023-09-26

--------------------------------------------------------------------------------------------

# Summary
Following the approval of this TEMP CHECK explaining AIP-42 potential impacts, this proposal will evaluate options to update holdings to maintain maximum emission power by acquiring AURA tokens to keep being exposed to the Balancer ecosystem while optimizing the voting power.

# Context

AIP-42 leads to a decorrelation of the incentives amounts generated on veBAL & vlAURA, as veBAL emission power is limited to BAL + base Aura rewards, while vlAURA receives additional AURA rewards allocated by the DAO treasury.

Looking at the vote incentives market a few weeks after the update went live, we can observe that the majority of cost paid per vote decreased on both layers. However, it’s common to still see projects overpaying so it might take more time for the full market to understand these changes.

For more context, some veBAL holders voted for the GHO gauges over the past two months without receiving bribes, enabling to generate ~ $300k of incentives on GHO gauges.

# Motivation

This proposal aims to propose several options to update the Balancer ecosystem holdings of the DAO by acquiring AURA to increase its maximum emission power.

*Current data (September 30th)*
AURA price

====================================================================================================
[122] id=0x5993430a914555d46947d2da6412b73549500f2246e93ca96576653cb1cbf6af  token=AAVE  space=aavedao.eth  date=2023-10-06
TITLE: [TEMP CHECK] Add FXS to Ethereum V3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Add FXS to Ethereum V3
Author: 0xlide
Date: 2023-09-21

---

## Summary
This TEMP CHECK presents the community with the opportunity to add FXS to the Ethereum v3 Liquidity Pool.

## Motivation
Frax Finance consists of a Stable-Protocol issuing Frax, FPI, FrxETH and Sub-Protocols such as Fraxlend, Fraxswap, Fraxferry, etc. Frax Shares Token ($FXS) is Frax Finance's Govenance Token & Utility Token.

Aave may facilitate diversification of GHO collateral by adding FXS. Also, FXS earned as revenue from the Aave V3 pool can be $veFXS as a new strategic asset to be used as a boost trap for GHO and/or new aToken adoption.

## Specifications
**What is the link between the author of the AIP and the Asset?**
0xLide have no link and are not compensated to present this TEMP CHECK proposal

**Provide a brief high-level overview of the project and the token.**
Frax Finance operates three stablecoins, $FRAX (USD peg), $FPI (US CPI peg) frxETH (LST and ETH peg), and sub-protocols Fraxlend (lending) Fraxswap (DEX) and Fraxferry (bridge). As of September 12, DeFiLlama's Protocol TVL Ranking is #17.

Frax Shares Token ($FXS) is Frax Finance's Govenance Token & Utility Token. There is a possibility of deflation. It also uses Curve's veCRV mechanism for its vesting and yield system, which can be used to specify the gauge and boost the yield.

**Explain the positioning of the token in the AAVE ecosystem. Why would it be a good borrow or collateral asset?**
FXS is suitable a

====================================================================================================
[123] id=0x89c3286743dc99b961d40d948c9507fe1005bc6fedf7e34ffb3d1265e0bc4bff  token=AAVE  space=aavedao.eth  date=2023-10-10
TITLE: [ARFC] TokenLogic Hohmann Transfer
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
title: [ARFC] TokenLogic Hohmann Transfer
author: @marczeller - Aave Chan Initiative
created: 2023-10-05
---

## Summary
This ARFC proposes the inclusion of TokenLogic in the "Orbit" delegate platform initiative for a period of 90 days, with a monthly compensation of 5k GHO and total budget of 15k GHO.

## Motivation
TokenLogic has been an active and valuable participant in the Aave ecosystem. While they were initially eligible and considered for the Orbit program, they opted to explore the possibility of becoming a service provider to the DAO. However, given their recent decision to re-organize internally and re-evaluate their proposed scope as a service provider, it's appropriate to reconsider their inclusion in the Orbit program.

## Specification

### TokenLogic Inclusion

- TokenLogic will be recognized as an official delegate within the Orbit program for a period of 90 days.
- They will receive a monthly compensation of 5k GHO, totaling 15k GHO over the three-month period.

### Funding and Emissions

TokenLogic's compensation will be in line with the Orbit program's guidelines, ensuring fairness and consistency with other delegates.

### Responsibilities and Conditions

- TokenLogic will actively participate in Aave governance, representing their delegators and contributing to the protocol's growth.
- If TokenLogic presents and successfully passes a proposal to become a service provider to the DAO, their Orbit funding stream will be terminated to prevent double comp

====================================================================================================
[124] id=0x33def6fd7bc3424fc47256ec0abdc3b75235d6f123dc1d15be7349066bc86319  token=AAVE  space=aavedao.eth  date=2023-10-10
TITLE: [ARFC] Transfer Assets From Polygon To Ethereum Treasury
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Transfer Assets From Polygon To Ethereum Treasury
author: @TokenLogic - @MatthewGraham
created: 2023-10-04

---

# Summary

This publication proposes transferring BAL, CRV, and USDC from the Polygon Treasury to the Ethereum Treasury.

# Motivation

Recently, the Aave DAO has created the [GHO Liquidity Committee](https://governance.aave.com/t/arfc-treasury-manage-gho-liquidity-committee/14914), completed an [AURA tokenswap with Olyympus](https://governance.aave.com/t/arfc-treasury-management-acquire-aura/14683), and is also considering a [tokenswap with Aura Finance](https://snapshot.org/#/aave.eth/proposal/0x94735082d4ba33b53497efb025aa6dbf75a5e4ade71684fd675c03f0e416a294). Each of these proposals has already utilized or is likely to utilize stable coins held in the Ethereum Treasury:

* 406,000 DAI - GHO Liquidity Committee
* 420,159.28 DAI - Olympus DAO token swap
* 600,000 USDC - Acquire AURA OTC with Aura Finance & AEF
* Total of 1,426,159.28 stable coins

This publication proposes transferring 1.5M DAI from Polygon to Ethereum to replenish the stable coin reserves.

Additionally, the Aave DAO's BAL and CRV holdings will also be transferred from Polygon to Ethereum. These assets can then be integrated into the DAO's broader strategy for managing these assets on Ethereum.

To implement this proposal, the newly released [Aave Polygon-Mainnet ERC20Bridge](https://governance.aave.com/t/update-on-aave-swapper-and-strategic-asset-manager-contracts/14522/3) by

