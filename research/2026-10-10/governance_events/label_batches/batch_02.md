# Labeling packets — batch 02 (125 proposals). Label each against criteria.md.

====================================================================================================
[0] id=0xd1136b4db12346a95870f5a52ce02ef1bd4fb83cbbbf56c709aa14ae2d38659b  token=AAVE  space=aavedao.eth  date=2023-10-11
TITLE: [ARFC] Enhancing Aave DAO's Liquidity Incentive Strategy on Balancer
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Enhancing Aave DAO's Liquidity Incentive Strategy on Balancer
Author: @Karpatkey
Date: 2023-10-06

---

# Summary
This publication proposes Aave DAO to:
- Mint auraBAL using existing B-80BAL-20WETH holdings and stake it on Aura Finance's Classic Staking Pool;
- Buy 400,000 USDC worth of AURA OTM; and
- Swap $200,000 worth of AAVE for AURA and 200,000 USDC for AURA in an OTC deal with AURA DAO.

# Background
[AIP-42](https://forum.aura.finance/t/aip-42-maximizing-value-of-aura-lp-incentives-bootstrapping-l2s/544) resulted in a significant reduction in baseline AURA minted per BPT, while distributing additional AURA from the DAO treasury pro-rata to pool LPs based on their vlAURA gauge weight. This has effectively led to a decorrelation between veBAL's and vlAURA's emission power, with the latter becoming a more efficient liquidity incentive asset.

@Dydymoon pro-actively addressed this change by laying out a thoughtful analysis and proposing [two options](https://governance.aave.com/t/arfc-treasury-management-update-balancer-ecosystem-holdings/14955/1#h-1-convert-to-remaining-bpt-to-aura-7) for updating Aave DAO's Balancer ecosystem holdings.

We've expressed our [concerns](https://governance.aave.com/t/arfc-treasury-management-update-balancer-ecosystem-holdings/14955/11#option-1-convert-to-remaining-bpt-to-aura-1) around both options, primarily because:

- Balancer is historically deeply rooted in the mechanics of the Aave protocol and is a strategic partne

====================================================================================================
[1] id=0xd8a8bdf3692666195895efbe0e885887c73b614273d6f0bd584c68afa9c11600  token=AAVE  space=aavedao.eth  date=2023-10-16
TITLE: [ARFC] Add FXS to Ethereum V3
CHOICES: YAE (LTV: 35%; LT: 45%) Gauntlet | YAE (LTV: 50%; LT: 60%) ChaosLab | NAY | ABSTAIN
TEXT (first 1500 characters):
title: [ARFC] Add FXS to Ethereum V3
author: @0xlide + Alice Rozengarden @Alice - Aave-chan initiative
created: 2023-10-13

---

## Summary

This publication presents the community an opportunity to add FXS to the Ethereum Aave v3 Liquidity Pool.

## Motivation

Frax Finance is a DeFi protocol that offers a stable protocol for issuing FRAX/FPI/frxETH and subprotocols such as Fraxlend, Fraxswap, and Fraxferry. The Frax Shares Token ($FXS) serves a dual role as both a governance token and a utility token.

The addition of FXS to Aave V3 represents the introduction of a new asset, encouraging the transition from Aave V2 to V3 and diversifying collateral assets for GHO. Furthermore, Aave DAO can utilize FXS obtained from the pool to kickstart the adoption of GHO and/or new aTokens.

## Specification

The parameters shown below are supported by @Gauntlet and @Chaoslabs with diverging opinions on the LT and LTV

Ticker: FXS
Contract Adress:[0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0 ](https://etherscan.io/token/0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0#code)
Chainlink Oracle: [0x6Ebc52C8C1089be9eB3945C4350B68B8E4C2233f](https://etherscan.io/address/0x6ebc52c8c1089be9eb3945c4350b68b8e4c2233f)

| Parameter | Recommendation (Gauntlet) | Recommendation (ChaosLabs) |
| --- | --- | --- |
| Isolation Mode | YES | YES |
| Borrowable | YES | YES |
| Collateral Enabled | YES | YES |
| Supply Cap (FXS) | 800,000 | 800,000 |
| Borrow Cap (FXS) | 500,000 | 500,000 |
| Debt Ceiling | $4M | $4M

====================================================================================================
[2] id=0x80493cdca3b1893e198802cd245e6e3c00f5fcd0b37c09aa41765b17419a71fe  token=AAVE  space=aavedao.eth  date=2023-10-19
TITLE: [ARFC] Treasury Management - Add to rETH Holding
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - Add to rETH Holding
author: @TokenLogic - @MatthewGraham & @DefiJesus + ACI - @MarcZeller 
created: 2023-10-14

---

# Summary

This publication proposes acquiring rETH with ETH held in the DAO's Ethereum Treasury.

# Abstract

This publication proposes converting a portion of the wETH, awETH and wEthWETH held in the Treasury to rETH.

A balance of 100 aEthWETH will remain in the Treasury to facilitate on going DAO expenses such as the [Quarterly Gas Rebate](https://governance.aave.com/t/arfc-quarterly-gas-rebate-distribution-august-2023/14680) and any other future expense that arise.

# Motivation

At the time of writing the Aave DAO has the following assets in the Ethereum Treasury:

|Asset|Qty| Value ($)|
| --- | --- | --- |
|wETH| 14.56 |22,543.32|
|awETH|530.39|820,829.60|
|aEthWETH|510.45 | 789,962.05|

The following assets are available to be claimed from the Paraswap Legacy Fees and Fee Claimer contract:

|Asset|Qty| Value ($)|
| --- | --- | --- |
|wETH| 4.53 |7,011.99|
|wETH| 10.8 |16,717.32|

This publication proposes converting all wETH, awETH and all but 100 aEthWETH to rETH. The 100 aEthWETH is to remain to support on going DAO funding. 

The table below shows the yield differential between the various assets:

|Asset|Yield (%)| 
| --- | --- | 
|wETH| 0.00|
|awETH|1.26|
|aEthWETH|1.97 |
|rETH|3.07|

Based upon current market conditions, the additional yield generated by converting the assets as outlined to rETH is $23,266.

====================================================================================================
[3] id=0x461571b38365b12ebe39b80d4d9663daa9c7e574cd4bf190ec6fb48dec96371f  token=AAVE  space=aavedao.eth  date=2023-10-30
TITLE: [ARFC] Treasury Management - Tooling Upgrade
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - Tooling Upgrade
author: @TokenLogic - @MatthewGraham, @defiJesus & @efecarranza
created: 2023-10-23

---

# Summary

The publication suggests that the Aave DAO contracts @TokenLogic to develop various smart contracts aimed at assisting in the management of the DAO's Treasury.

# Motivation

At present, the Aave DAO has a mechanism for bridging funds between Polygon and Ethereum using the [Aave Polygon-Mainnet ERC20Bridge](https://github.com/bgd-labs/aave-helpers/tree/master/src/bridges) via the shortExecutor. This contract was created by @efecarranza during their tenure at [Llama](https://governance.aave.com/t/update-on-aave-swapper-and-strategic-asset-manager-contracts/14522/3).

To ensure the Aave DAO's financial stability and the ability to transfer assets across different networks through the shortExecutor, it is crucial to establish equivalent contracts for other networks. One such scenario involves moving USDC from Avalanche to Ethereum, effectively extending the DAO's stable coin runway.

This publication recommends the development of the following tooling contracts:

1) Avalanche to Ethereum
2) Optimism to Ethereum
3) Arbitrum to Ethereum

Upon the creation of these contracts, they will become public goods within the Aave ecosystem. This means that anyone will have the capability to draft a payload for transferring the DAO's funds between various networks with minimal effort.

Once the Avalanche to Ethereum bridge contract is c

====================================================================================================
[4] id=0x9a5c5e73452caf1d57a85a482c085bc03ac4fd3e67c20bdbe18f3ea9b113bb21  token=AAVE  space=aavedao.eth  date=2023-11-07
TITLE: [ARFC] Treasury Management - vlAURA
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - vlAURA
author: @TokenLogic - @MatthewGraham, @defiJesus & @efecarranza
created: 2023-11-03

---

# Summary

This publication proposes locking the AURA holding in vlAURA via the Strategic Asset Manager and delegating managing the position to the GHO Liquidity Committee.

# Motivation

The Aave DAO holds a substantial amount of AURA, and the GHO Liquidity Committee (GLC) is actively executing this [proposal](https://governance.aave.com/t/arfc-enhancing-aave-daos-liquidity-incentive-strategy-on-balancer/15061) by swapping 400,000 USDC worth of AURA on the market.

The next step in implementing the strategy is for the DAO to lock the AURA holdings. This publication proposes sending the AURA to the [Strategic Asset Manager](https://etherscan.io/address/0x6235d8071dbee0a20e7d6ebb214f65d913c7ac1b#code) (SAM) contract. From here, the full amount of AURA should be locked using [Function 9](https://etherscan.io/address/0x6235d8071dbee0a20e7d6ebb214f65d913c7ac1b#writeProxyContract) for vlAURA. The voting rights are to be delegated to the [GLC](https://app.safe.global/balances?safe=eth:0x205e795336610f5131Be52F09218AF19f0f3eC60) using [Function 5](https://etherscan.io/address/0x6235d8071dbee0a20e7d6ebb214f65d913c7ac1b#writeProxyContract).

The Guardian role on the SAM contract is already configured to the GLC SAFE address. This can be verified using the Read as Proxy [Function 10](https://etherscan.io/address/0x6235d8071dbee0a20e7d6ebb214f65d913c7

====================================================================================================
[5] id=0x66d766a8584ae23e137ca142902f68a6ba4fddf2874fa52815288b72ac9e84ce  token=AAVE  space=aavedao.eth  date=2023-11-07
TITLE: [ARFC] TokenLogic - Retrospective Funding Proposal
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] TokenLogic - Retrospective Funding Proposal
author: @TokenLogic - @MatthewGraham 
created: 2023-11-03

---

# Summary

This publication propose a retrospective payment that recognises @TokenLogic contributions to the Aave DAO over the last 6 months.

# Motivation

In light of the [Request For Proposal (RFP) issued by StableLabs](https://governance.aave.com/t/temp-check-aave-financial-management-working-group/15193), it is an opportune moment to outline the specific tasks that TokenLogic will accomplish before the Aave DAO selects a preferred financial service provider. This publication catalogs TokenLogic's past and ongoing involvements with the Aave DAO, acknowledging the team's valuable contributions while also establishing a path for a seamless transition in alignment with the outcome of the Request For Proposal process.

The lists below encompass most of our contributions thus far, excluding efforts on projects that didn't materialize. Additionally, we have outlined a limited scope of forthcoming work that we intend to undertake as part of this funding proposal.

## 15 Submitted AIPs

* [AIP-354 - Transfer Assets From Polygon to Ethereum Treasury](http://app-aave-com.ipns.localhost:48084/governance/proposal/?proposalId=354)
* [AIP-353 - Reserve Update October](http://app-aave-com.ipns.localhost:48084/governance/proposal/?proposalId=353)
* [AIP-347 - GHO Funding](http://app-aave-com.ipns.localhost:48084/governance/proposal/347/)
* [AIP-343 - Fund GHO Liq

====================================================================================================
[6] id=0x8e6b724f0ae90daaacbde615280e311c0648786bda934ca47bace2ce84a00c21  token=AAVE  space=aavedao.eth  date=2023-11-13
TITLE: [ARFC] Treasury Management - auraBAL
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - auraBAL
author: @TokenLogic - @MatthewGraham, @defiJesus & @efecarranza
created: 2023-11-08

---

# Summary

This publication proposes creating a permissioned and upgradeable contract to manage the auraBAL holding.

# Motivation

Currently, the auraBAL resides in the GHO Liquidity Committee (GLC) SAFE. The Aave DAO has placed trust in the signers of this SAFE who have custody of the funds. 

This publication proposes that TokenLogic create a permissioned contract, similar to the Strategic Asset Contract (SAM) to manage this position. The shortExecutor will be in absolute control of the funds and can grant/revoke the Guardian role to enable a SAFE to interact with the auraBAL contract.

During the initial deployment of the auraBAL contract, the Guardian role will be assigned to the GLC. The specification section below details the functions to be included on the auraBAL contract. 

# Specification

The below specification defines at a high level the functionality that the shortExecutor can assign to the Guardian role:

1) Mint auraBAL using B-80BAL-20wETH
2) Stake auraBAL to earn yield;
    2.1) Compounder, or 
    2.2) Classic auraBAL
3) Claim rewards
4) Transfer rewards to either Treasury or SAM (vlAURA) or GLC (bribes)
5) (Optionally) Swap BAL rewards for B-80BAL-20wETH to mint for more auraBAL

In addition to the above, the Ethereum Executor can also perform the following functionality:

1) Assign the Guardian role 
2) Revoke the Gua

====================================================================================================
[7] id=0xff6853c25774ad63a7ce2a92f0a4393112dad2941cf93e392ed8a10d7eac6664  token=AAVE  space=aavedao.eth  date=2023-11-27
TITLE: [ARFC] Upgrade Safety Module with StkGHO
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
**Title:** [ARFC] Upgrade Safety Module with StkGHO

**Author:** Marc Zeller - ACI (Aave Chan Initiative)

**Date:** 2023-11-21

---

## Summary
This ARFC introduces an enhancement to the Safety Module by integrating a GHO Safety Module. This new category aims to mitigate risks using GHO’s stablecoin attributes for potential shortfall events within its ecosystem. It also reduces the Safety incentives for StkAAVE and StkBPT.

## Motivation

[AIP-366 was adopted by governance](https://app.aave.com/governance/proposal/366/) to reduce the safety incentives of StkAAVE and StkBPT, but an implementation bug made the AIP execution impossible. After discussion with DAO service providers, it was decided to bundle the re-run of 366 with the creation of the GHO safety module and the StkGHO asset.

The GHO Safety Module will fortify the Aave Protocol's resilience by adding a stablecoin asset, which is inherently less volatile than AAVE. This strategic move diversifies the Safety Module's capacity to absorb shocks from various risk vectors in case of shortfall events.

The GHO Safety Module will target a liquidity pool of 9M GHO with an APR range of 12-15%, achievable with a daily emission of 35 AAVE/day over a 90-day period. The module will have a slashing rate set at 100%, meaning the entirety of the deposits could be utilized in a shortfall event, with socialized coverage among StkGHO holders. The cooldown period is adjusted to 10 days, which is suitable for a stablecoin.

## Specificat

====================================================================================================
[8] id=0xc999644bf64e4f62722d327416520b6f8cf8d7ceecbb69e7c52e2ebe1f4c3d63  token=AAVE  space=aavedao.eth  date=2023-12-02
TITLE: [ARFC] Treasury Management - Deploy AURA to vlAURA
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - Deploy AURA to vlAURA
author: @karpatkey_TokenLogic - @MatthewGraham, @Sisyphos & @efecarranza 
created: 2023-11-26

---

# Summary

This publication proposes transferring the AURA holding from the Ethereum Treasury to the GHO Liquidity Committee (GLC) SAFE. 

# Motivation

The Aave DAO holds [845,090.43 vlAURA](https://etherscan.io/token/0xc0c293ce456ff0ed870add98a0828dd4d2903dbf?a=0x205e795336610f5131Be52F09218AF19f0f3eC60) on the GLC SAFE and also [443,674 AURA](https://etherscan.io/token/0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF?a=0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c) in the Treasury. This publication proposes transferring the AURA from the Treasury to GLC SAFE and consolidating the vlAURA holding. The GLC is to lock the AURA for vlAURA.

The Aave DAO is expected to receive 413,849.57 units of vlAURA upon locking 443,674 AURA. 

The Aave DAO will benefit by earning yield, 3.10% APR in [auraBAl](https://app.aura.finance/#/1/lock) from holding vlAURA. In addition, the GLC has delegated the vlAURA to Paladin to earn additional yield. It is our understanding this is temporary strategy until Balancer liquidity pools feature as part of the overal GHO liquidity strategy. 

At the time of writing, delegating vlAURA to Paladin is generating approximately 0.0135 USD per week per vlAURA. This is roughly $11k per week and an annualise yield >65%. The yield offered by Paladin from vlAURA delegation is nominated in USDC. This is on par wi

====================================================================================================
[9] id=0x0341f4050ed20182c2c344fb370d958f8f77f7035c4783408dd0f962b7d39544  token=AAVE  space=aavedao.eth  date=2023-12-06
TITLE: [TEMP CHECK] AAVE Treasury Proposal for RWA Allocation with Maple Finance
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] AAVE Treasury Proposal for RWA Allocation with Maple Finance 

Author: @Maple_Direct

Created: 2023-11-20

---

# Summary

Maple Finance would like to propose that Aave’s Treasury allocates stablecoins into Maple Finance’s cash management pool to earn the risk-free rate on-chain, further diversifying their existing and future RWA holdings.

The main results of this proposal will be:

1. Aave will onboard with Maple Finance to enable the treasury to allocate to RWA strategies on the platform.
2. Aave Treasury to allocate to Maple’s Cash Management pool, with an initial investment of 1M USDC, with the goal to increase this allocation over the course of time.
3. As the Aave community gains comfort in the Maple platform, the treasury will explore investment opportunities into other Maple RWA pools, pending approval from Aave’s governance.

# Motivation

Shifting away from an exclusive focus on crypto assets, Aave is now exploring off-chain markets, particularly Real World Assets (RWA). This strategic move holds the promise of diversified treasury management, achieved through a thoughtful percentage allocation of Aave’s current USDC balance. This forward-thinking approach positions Aave to leverage RWA collateral for long-term growth, whether by enhancing liquidity, diversifying revenue streams, or capitalizing on earnings from dormant stablecoin assets.

Maple Direct is excited to introduce the Cash Management Pool (MPLcashUSDC) to the Aave community. Sin

====================================================================================================
[10] id=0x6e57ed54cf803652ab4839ff7b7f7de08ba086fbe99163547c6188a3ee55e209  token=AAVE  space=aavedao.eth  date=2023-12-10
TITLE: [ARFC] TokenLogic & karpatkey Service Provider Partnership
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
![Screenshot 2023-12-10 at 15.18.05.png](ipfs://bafybeibxdcjv3b4p4w5wyjkby74ynhsyobto67smsj2krhnfnaiuexya7e)

---

Title: [ARFC] TokenLogic & karpatkey Service Provider Partnership
Discussions: https://governance.aave.com/t/temp-check-financial-services-proposal-karpatkey-tokenlogic/15633
Author: @TokenLogic @karpatkey
Created: 2023-12-05

---

# Summary

This ARFC is to onboard TokenLogic & karpatkey to provide financial services to the Aave DAO for an initial period of 180 days, with a combined budget of 400k GHO.

# Motivation

## Overview

TokenLogic & karpatkey are responsible for delivering the following services to the Aave DAO: 

* Treasury Management;
* Strategic Assets' Liquidity; and
* Safety Module.

This funding will be used to support the TokenLogic and karpatkey teams to deliver the scope as outlined in the [TEMP CHECK](https://governance.aave.com/t/temp-check-financial-services-proposal-karpatkey-tokenlogic/15633).

## What to Expect

This proposal outlines a collaborative framework between TokenLogic and karpatkey to manage the Aave DAO’s treasury. Both parties will work in unison to ensure any future proposals within the agreed scope are jointly developed and endorsed.

### Treasury Management

#### Develop the Architecture for Managing Aave's Assets

We aim to define a robust architecture for asset management. This architecture will enable non-custodial asset management, incorporating role-based access controls preapproved by the community that will enable

====================================================================================================
[11] id=0x0e496f9cb98fb887e9c0e1b4669607a2b99a0675b23ad152c7aedbe28f8dc08d  token=AAVE  space=aavedao.eth  date=2023-12-18
TITLE: [ARFC] Chaos Labs Risk Parameter Updates - WBTC.e on V2 and V3 Avalanche
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# Summary

A proposal to adjust risk parameters for WBTC.e on Avalanche deployments, to limit further exposure and promote user migration to BTC.b:

- V2
    - Freeze asset
    - Reduce Liquidation Threshold and LTV
- V3
    - Freeze asset
    - Reduce Liquidation Threshold and LTV

# Motivation

As the Avalanche network is transitioning away from WBTC.e, we are observing an ongoing decrease in WBTC.e liquidity on-chain, with approximately 30% of the liquidity diminishing over the past few months. At this time, the total circulating supply on Avalanche is 1,731 WBTC.e. A  considerable portion, nearly 67%, of the circulating supply is concentrated on Aave Avalanche V2 and V3, with ~496 and ~664 tokens, respectively. 

Given the persistence of this trend, we suggest reducing exposure on Aave and proactively modifying risk parameters for the asset. This strategy aims to:

1.  Avert a potential scenario where there is inadequate liquidity to facilitate liquidations in Aave deployments.
2. Motivate new and existing users on Aave to transition to BTC.b, which has a stronger liquidity profile on Avalanche.

### Limit New Supply

Freeze the WBTC.e reserves on V2 and V3 Avalanche.

### Reduce Capital Efficiency

Additionally, as a precautionary measure and to further reduce exposure to the asset, we recommend reducing LTs and LTV, without impacting current holders:

- V3 - reduce LT to 70 % and LTV to 0.
- V2 - reduce LT to 70% and LTV to 0.
  - at this time, this will lead to 6 accou

====================================================================================================
[12] id=0x774c3ae45347e9778988143c59c56bf994661470c9103d69b30955652bb21f16  token=AAVE  space=aavedao.eth  date=2024-01-07
TITLE: [ARFC] Updated Aave Grants Continuation Proposal
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---

Title: [ARFC] Updated Aave Grants Continuation Proposal 
Author: @0xmigi & Bill
Created: 2023-11-14

---

# Summary

An opportunity to continue Aave Grants DAO (AGD) for 6 months by preserving the current AGD treasury holdings and increasing AGD’s GHO allowance by $328,000.

This proposal will enable AGD to deliver and improve upon the top tier grants program the Aave ecosystem has had over the past 2+ years and continue being a gateway for new contributors to the ecosystem. AGD will fund $500,000 in developer grants per quarter, drive Aave’s culture and GHO adoption, and set the groundwork for the next chapter of the continued evolution of AGD.

Figures and calculations based on asset prices have been updated from the TEMP CHECK to reflect the current market conditions.

# Motivation

Throughout the previous proposal, AGD has:

Awarded 50 new grants and made 15 payments to grantees based on milestone completion.

Engaged builders and the community at five events, including four hackathons where AGD awarded a total of 19 Aave and GHO specific bounties and inspired 58 teams to hack with Aave and GHO.

Proliferated the ghost by hosting 1 rAAVE to strengthen Aave’s culture, bring the community together, and cultivate an ecosystem with the best contributors.

Exercised prudence with the treasury by decreasing the average grant size awarded by 52.8% and maintaining average reviewer compensation at ~22% of the monthly maximum budget.

This proposal outlines renewing AGD for th

====================================================================================================
[13] id=0xb39537e468eef8c212c67a539cdc6d802cd857f186a4f66aefd44faaadd6ba19  token=AAVE  space=aavedao.eth  date=2024-01-15
TITLE: [ARFC] Treasury Management - GSM Funding & RWA Strategy Preparations
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Treasury Management - GSM Funding & RWA Strategy Preparations
author: @karpatkey_TokenLogic - @MatthewGraham, @Sisyphos & @efecarranza 
created: 2024-01-09

---

# Summary

In preparation for launching the GHO Stability Module (GSM) and the $1M RWA strategy with Centirfuge, this publication seeks to make available the necessary amount of USDC and USDT on Ethereum v3. 

# Motivation

The GSM is in the late stages of audit and is expected to be available for deployment in the near future. The Centrifuge proposal is currently mid way through the review process. The current stable coin holdings on Ethereum are insufficient to support the GSM, RWA strategy and Service Provider (SP) commitments. Additional funds are needed on Ethereum to support the GSM. 

The [largest GSM funding requested](https://governance.aave.com/t/gho-stability-module-update/14442/10) consisted of the following:

* 3.5M USDC
* 3.5M USDT 

The RWA Strategy is valued at [1M](https://governance.aave.com/t/arfc-aave-treasury-rwa-allocation/14790) of USDC funding.

The expected aEthUSDC and aEthUSDT Reserve Holding, post Aave Funding Part B being implemented, is as shown below:

* 2.93M aEthUSDC (0.72M current holding plus 2.21M Aave Funding Part B)
* 0.71M aEthUSDT (0.71M current holding)

It is clear from comparing the numbers above, there is a need to add to the aEthUSDC and aEthUSDT holdings in order to fullfill the GSM and RWA Strategy commitments.

Tapping into the aUSDT and aUSDC holding

====================================================================================================
[14] id=0x6fc11878e04e6bd26def1077115f67294c7a4cb0b91d4c4eacfa4e036791cfef  token=AAVE  space=aavedao.eth  date=2024-01-20
TITLE: [ARFC] Introducing "Frontier" - Staking as a Service for the Aave DAO
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

**Title:** [ARFC] Introducing "Frontier" - Staking as a Service for the Aave DAO

**Author:** Marc Zeller - ACI (Aave Chan Initiative)

**Date:** 2024-01-15

---

## Summary

The Aave Chan Initiative (ACI) introduces "Frontier," a 'Staking as a Service' product for the Aave DAO. This service aims to further decentralize the protocol's staking exposure and actively participate in network security. ACI will operate staking nodes and run validator nodes on behalf of the DAO, enhancing the DAO's passive income and promoting a diversified staking strategy.

## Motivation

Transitioning from simply acquiring Liquid Staking Tokens (LSTs) like stETH and rETH to actively running validator nodes, "Frontier" represents a significant step towards greater involvement in Ethereum's network decentralization and security. 

For this trial experiment, we propose to run 32 Stader minipools of 4 ETH.

This proactive approach will allow the Aave DAO to host community members in our minipools, providing them with staking exposure through ETHx.

## Specification

To initiate "Frontier," we propose the creation of a 2/3 multisig controlled by:

- Aci.eth
- Tokenlogic
- Karpatkey

This multisig will be funded with 128 wETH, enabling ACI to set up 32 validator minipools on behalf of the Aave DAO.

**Benefits:**

- **Enhanced diversity**: The Aave DAO has been a pioneer in LST diversity, staking as a service can allow the DAO to increase this diversity with new ecosystems and assets that are not

====================================================================================================
[15] id=0x59a31a5b09929d09cba2b069f65eeb4db534cc842771b69c7f38f5a905771c74  token=AAVE  space=aavedao.eth  date=2024-01-23
TITLE: [ARFC] Gauntlet USDC.e Supply and Borrow Cap Recommendation on Optimism Aave v3
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Summary

A proposal to make parameter changes on Aave Optimism V3. For more details, see the full forum post [here]( https://governance.aave.com/t/arfc-gauntlet-usdc-e-supply-and-borrow-cap-recommendation-on-optimism-aave-v3/16308 ).


## Motivation

Gauntlet recommends increasing supply and borrow caps for the following assets that have utilization rate of above 75%. The recommendations are made to improve capital efficiency - Gauntlet has not received any guidance from Circle on OP about removing support to USDC.e. Note that the supply and borrow caps for USDC.e on Optimism were reduced in [AIP-409](https://app.aave.com/governance/proposal/?proposalId=409) to onboard native USDC across Aave markets, however, we recommend the following specification from a capital efficiency & risk perspective.



## Specification

|Asset   |   Chain | Current Supply Cap|New Supply Cap |Current Borrow Cap |New Borrow Cap |
|:--------|-------------|-------------|-------------|-------------|-------------:|
|USDC.e    |      Optimism v3| 18,000,000  | 30,000,000|15,500,000|28,000,000 | 

**Disclaimer: Gauntlet reserves the right to not move forward with any parameter changes recommended in Snapshot polls, if market conditions change meaningfully.**

*By approving this proposal, you agree that any services provided by Gauntlet shall be governed by the terms of service available at gauntlet.network/tos.*

====================================================================================================
[16] id=0xdba99e9c8da24424447d7c7b70eff93ad5b6055714b5f34cf9859c923fb3a38a  token=AAVE  space=aavedao.eth  date=2024-01-25
TITLE: [ARFC] Add sFRAX on Ethereum V3
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
Title: [ARFC] Add sFRAX on Ethereum V3

Author: @0xlide, @SaucyBlock and ACI (Aave Chan Initiative)

Date: 2024-01-18

# Summary
This publication presents the community an opportunity to add sFRAX to the Ethereum Aave V3 Liquidity Pool.

# Motivation
Staked FRAX (sFRAX) is an ERC-4626 staking vault that distributes a portion of the Frax Protocol yield. sFRAX APY attempts to roughly track the interest on reserve balances (IORB) rate of the United States Federal Reserve.

Integrating sFRAX as collateral asset in the Aave V3 Ethereum Pool has the potential to create new demand for borrowable assets on Aave V3, such as stablecoins and FXS.

# Specification

Ticker: sFRAX
Contract Adress: 0xA663B02CF0a4b149d2aD41910CB81e23e1c41c32
Chainlink Oracle: 0xB9E1E3A9feFf48998E45Fa90847ed4D467E8BcfD


| Parameter               | Recommendation |
|-------------------------|----------------|
| Isolation Mode          | NO             |
| Borrowable in Isolation | NO             |
| Stable Borrow           | NO             |
| Enable Borrow           | NO             |
| Enable Collateral       | YES            |
| Loan To Value           | 70.00%         |
| Liquidation Threshold   | 75.00%         |
| Liquidation Bonus       | 6.00%          |
| Reserve Factor          | 20.00%         |
| Liquidation Protocol Fee| 20.00%         |
| Supply Cap(sFRAX)       | 10.00M         |
| Borrow Cap(sFRAX)       | N/A            |
| Uoptimal                | N/A            |
| Base

====================================================================================================
[17] id=0xf48feeb0d02ad70425f7d1095c5c433f87ea3f3e0178e9c905ec8bfcf137f3b4  token=AAVE  space=aavedao.eth  date=2024-02-05
TITLE: [TEMP CHECK] Merit - A New Aave-Alignment User Reward System
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

**Title:** [TEMP CHECK] Merit - A New Aave-Alignment User Reward System

**Author:** Marc Zeller - Aave-Chan Initiative

**Date:** 2024-01-30

---

## Summary

Introducing "Merit," an Aave-alignment user reward system, designed as a merkle-tree-based periodic airdrop to incentivize Aave-aligned behaviors and enhance the competitiveness of the Aave protocol.

## Motivation

In an increasingly competitive DeFi landscape, Aave seeks to innovate its protocol efficiency and appeal. "Merit" aims to distinguish Aave with a rewarding system that emphasizes actions beneficial to the DAO, countering competitors' use of points or non-transferable tokens. while increasing DAO revenue and wanted behaviour.

## Specification

"Merit" is a booster-based reward system with specific actions that earn points over time. These points determine the weekly distribution of StkAAVE and GHO rewards. The precise calculations are kept private to prevent gaming of the system. Merit does not provide any benefits to Sybil's actions.

### Rewarded Actions

Actions that align with Aave's strategic objectives will be rewarded:

| Action |
| --- |
| Deposit LST, Borrow wETH |
| Deposit LSTs, Borrow wETH using emode |
| Deposit sDAI, Borrow GHO |
| Deposit USDC/USDT, Borrow GHO |
| Deposit AAVE, Borrow GHO |

### Merit boosters

Merit boosters enhance these rewards for specific behaviors:

| Behavior | Multiplier description |
| --- | --- |
| Staker | Bonus for staking AAVE, StkBPT, StkGHO |
| Active in G

====================================================================================================
[18] id=0xf30c35c586e283bae81fe1c22bd4b3cfc7f6da37bde19ac9e633414f28dc9e74  token=AAVE  space=aavedao.eth  date=2024-02-05
TITLE: [ARFC] Set Liquidity Observation Labs as Emission manager for wstETH on V3 markets
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Set "Lido Liquidity Observation Labs as Emission manager for wstETH on V3 markets
Author: Aave Chan Initiative (ACI)
Dated: 2024-01-31
---

## Summary
This ARFC proposes to set the Lido "Lido Liquidity Observation Labs wallet as the emission manager for the wstETH token on Ethereum, Base, Arbitrum, Optimism, Polygon and Gnosis Aave V3 markets. This will enable the Lido "Lido Liquidity Observation Labs to define and fund incentive programs for all wstETH markets, promoting growth and expanding the user base of Aave.

## Motivation
The Lido "Lido Liquidity Observation Labs has expressed a desire to actively contribute to the growth and development of the Aave V3. By setting their wallet as the emission manager for the wstETH token, the Foundation will be able to directly fund incentive programs that can attract more users to the pool and stimulate activity. This aligns with the broader goals of the Aave community to foster active and engaged markets.

## Specification
The Lido "Lido Liquidity Observation Labs wallet address will be provided in a later stage.

The AIP call setEmissionAdmin() method in the emission_manager contract.

EMISSION_MANAGER.setEmissionAdmin(wstETH, EMISSION_ADMIN);

This method will set the Lido "Lido Liquidity Observation Labs wallet as the emission admin for the wstETH token on Ethereum, Base, Arbitrum, Optimism, Polygon and Gnosis V3 markets.

## Disclaimer
This proposal is powered by Skyward. The Aave Chan Initiative has not been p

====================================================================================================
[19] id=0x4db0fe8cb6c21abd34e4d38836db72ed7f1b06c91386ec9e637df8786a289d0d  token=AAVE  space=aavedao.eth  date=2024-02-12
TITLE: [ARFC] Set Aave Chan Initiative as Emission Manager for fdUSD on BNB Chain Aave V3
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Set Aave Chan Initiative as Emission Manager for fdUSD on BNB Chain Aave V3
Author: Aave Chan Initiative (ACI)
Dated: 2024-02-06

---

# **Summary**

This ARFC proposes to set the Aave Chan Initiative (ACI) wallet as the emission manager for the fdUSD token on BNB Chain Aave V3 markets. This will enable the ACI to enact incentive programs funded by BNB Chain ecosystem partners for all fdUSD markets, promoting growth and expanding the user base of Aave on the BNB Chain.

# Motivation

The Aave Chan Initiative has been in discussion with various parties that have a desire to actively contribute to the growth and development of the Aave V3 on the BNB Chain. In order to facilitate emissions by various stakeholders, ACI proposes becoming the emissions manager for fdUSD on BNB Chain. Emission incentives will be sent to ACI multisig and distributed as agreed on with partners. By setting the multisig as the emission manager for the fdUSD token, the ACI will be able to directly manage incentive programs that can attract more users to the pool and stimulate activity. This aligns with the broader goals of the Aave community to foster active and engaged markets on the BNB Chain.

# Specification

The ACI multisig address bnb:0xac140648435d03f784879cd789130F22Ef588Fcd will be set as Emissions manager.

The call to the setEmissionAdmin() method in the emission_manager contract will be as follows:

`EMISSION_MANAGER.setEmissionAdmin(fdUSD, 0xac140648435d03f784879cd789130F2

====================================================================================================
[20] id=0x412b38c7a0cf1840b102e28ea7ef0373e3ab4b9544873e8cc1544972b777d9a1  token=AAVE  space=aavedao.eth  date=2024-02-12
TITLE: [ARFC] Orbit Program Renewal
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Orbit Program Renewal
Author: Marc Zeller - Aave Chan Initiative (ACI)
Dated: 2024-02-05
---

## Summary

Proposing the renewal of the Orbit program for recognized delegates. Compensating them with GHO and ETH reimbursement of Gas costs associated with their governance activity.

## Motivation

With the transition to Governance V3, a significant feature introduced is gasless voting via Gelato integration on the [DAO-run governance app](https://vote.onaave.com), making it easier for delegates to participate without the burden of gas costs.

This innovation prompts the proposal to discontinue the general gas rebate program, However, recognizing the continued necessity for proposal creation and payload deployment activities, the proposal suggests maintaining targeted gas rebates for these specific actions. These tasks are now streamlined under the ACI's Dolce Vita product, offering a focused and efficient mechanism to manage and reimburse the gas expenditures associated with governance contributions.

To accurately track and reimburse gas expenditures, the proposal leverages [open-source scripts](https://github.com/JosepBove/aave-gov-gas) initially developed by Josep Bove, now part of the ACI team. These scripts have been [adapted for compatibility with Governance V3](https://github.com/AaveChan/aave-gov3-gas/tree/master), ensuring transparency and accountability in monitoring gas costs incurred by delegates during their governance activities.

Moreover, the pr

====================================================================================================
[21] id=0x4518ee2130b2299fdf0827aa6a97b8211b3273f5b07b6f13b8141e5b9ad89e5f  token=AAVE  space=aavedao.eth  date=2024-02-14
TITLE: [ARFC] Set ARB Emission Admin to Gauntlet
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Set ARB Emission Admin to Gauntlet
author: @karpatkey_TokenLogic & @Gauntlet
created: 2024-02-05

---


# Simple Summary

This proposal enables Gauntlet to distribute ARB rewards across Aave v3 on Arbitrum. 

# Motivation

Gauntlet has been engaged by the Arbitrum Foundation to support the migration from bridged USDC.e to native USDC on the network. As part of this project, Gauntlet seeks to distribute ARB rewards across Aave v3 on Arbitrum to encourage migration from USDC.e to USDC.

There is currently 15.59M units of USDC.e deposited on Arbitrum v3 that Gauntlet & the Arbitrum Foundation intend to attract to USDC with the use of ARB rewards.

# Specification

The `EmissionManager`, a governance controlled function, assigns the `Emission_Admin` role for a specified token, ARB on the Arbitrum network. 

The `Emission_Admin` role controls the distribution of the specified token, ARB, across the specified Aave v3 deployment.

The `Emission_Admin` can distribute ARB anywhere across the Aave v3 Arbitrum Liquidity Pool.

# Implementation

Set `Emission_Admin` permission for ARB to the following Gauntlet address: 

**Aave v3 Arbitrum**
Address Reward (ARB): `0x912CE59144191C1204E64559FE8253a0e49E6548`
EMISSION_ADMIN: `0xE79C65a313a1f4Ca5D1d15414E0c515056dA90b4`

The AIP call setEmissionAdmin() method in the emission_manager contract.

EMISSION_MANAGER.setEmissionAdmin(ARB,EMISSION_ADMIN);

# Disclosure

TokenLogic and karpatkey receive no payment for this proposa

====================================================================================================
[22] id=0xe0579b1efa1f26237104632f4ccddac0158866a18061b27a634634fa9d31e250  token=AAVE  space=aavedao.eth  date=2024-02-14
TITLE: [ARFC] Set osETH & SWISE Emission Admin to StakeWise
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Set osETH & SWISE Emission Admin to StakeWise
author: @karpatkey_TokenLogic & @ACI
created: 2024-02-09

---

# Simple Summary

This proposal enables StakeWise to distribute osETH and/or SWISE rewards across Aave v3 on Ethereum. 

# Motivation

With osETH being added to Aave v3 Ethereum in the near future, this publication enables StakeWise to emit osETH and/or SWISE rewards across Aave v3 on Ethereum.

StakeWise intends to use the rewards to support the continued growth and adoption of osETH.

# Specification

The `EmissionManager`, a governance controlled function, assigns the `Emission_Admin` role for a specified token, osETH and SWISE on the Ethereum network. 

The `Emission_Admin` role controls the distribution of the specified token, osETH and SWISE , across the specified Aave v3 deployment.

The `Emission_Admin` can distribute osETH and SWISE anywhere across the Aave v3 Ethereum Liquidity Pool.

# Implementation

Set `Emission_Admin` permission for osETH and SWISE to the following StakeWise Liquidity Committee Master SAFE address: 

**Aave v3 Ethereum**
Address Reward (SWISE): `0x48C3399719B582dD63eB5AADf12A40B4C3f52FA2`
Address Reward (osETH): `0xf1C9acDc66974dFB6dEcB12aA385b9cD01190E38`
EMISSION_ADMIN: `0x189Cb93839AD52b5e955ddA254Ed7212ae1B1f61`

The AIP call setEmissionAdmin() method in the emission_manager contract.

EMISSION_MANAGER.setEmissionAdmin(SWISE,EMISSION_ADMIN);
EMISSION_MANAGER.setEmissionAdmin(osETH,EMISSION_ADMIN);

# Disclosure

To

====================================================================================================
[23] id=0x66040ad4d46ba756365fbe5c2ed5957d17a3e70db5a00ec532fdc725251d2327  token=AAVE  space=aavedao.eth  date=2024-02-19
TITLE: [ARFC] Set OP Emission Admin
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Set OP Emission Admin 
Author: @karpatkey_TokenLogic, @ACI & @ChaosLabs
Dated: 2024-02-14
---

## Summary

This proposal enables a SAFE with signers from @karpatkey_TokenLogic, @ACI and @ChaosLabs to distribute USDC rewards across Aave v3 on Optimism.

## Motivation
Chaos Labs has been engaged by the Optimism Foundation to support the migration from bridged USDC.e to native USDC on the network.

As part of this project, a SAFE is to be created that will receive OP tokens on behalf of the Aave DAO. From this SAFE the OP rewards are to be distributed on Aave v3 Optimism.

The SAFE will be 3 of 3 and contains a nested SAFE that is 1 of 2.

@karpatkey_TokenLogic - @Sisyphos and @MatthewGraham
@ACI - @MarcZeller
@ChaosLabs - @OriN
There is currently 15.48M units of USDC.e deposited on Optimism v3 that Chaos Labs & the Optimism Foundation intend to attract to USDC with the use of OP rewards.

## Specification

The EmissionManager, a governance controlled function, assigns the Emission_Admin role for a specified token, OP on the Optimism network.

The Emission_Admin role controls the distribution of the specified token, OP, across the specified Aave v3 deployment.

The Emission_Admin can distribute OP anywhere across the Aave v3 Optimism Liquidity Pool.

## Implementation

Set Emission_Admin permission for OP to the following SAFE address:

Aave v3 Optimism
Address Reward (OP): 0x4200000000000000000000000000000000000042
EMISSION_ADMIN: TBA

The AIP call setEmission

====================================================================================================
[24] id=0x0d83730d546d74d463f045697e9ea6b1708b5c833a40e09e4f87f1804177f5a6  token=AAVE  space=aavedao.eth  date=2024-02-19
TITLE: [ARFC] Set ETHx and SD Emission Admin to Stader Labs
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Set ETHx and SD Emission Admin to Stader Labs 
Author: @karpatkey_TokenLogic & @ACI
Dated: 2024-02-11
---

## Summary

This proposal enables Stader Labs to distribute ETHx and/or SD rewards across Aave v3 on Ethereum.

## Motivation
With ETHx being added to Aave v3 Ethereum in the near future, this publication enables Stader Labs to emit ETHx and/or SD rewards across Aave v3 on Ethereum.

Stader Labs intends to use the rewards to support the continued growth and adoption of ETHx.

## Specification

The EmissionManager, a governance controlled function, assigns the Emission_Admin role for a specified token, ETHx and SD on the Ethereum network.

The Emission_Admin role controls the distribution of the specified token, ETHx and SD, across the specified Aave v3 deployment.

The Emission_Admin can distribute ETHx and SD anywhere across the Aave v3 Ethereum Liquidity Pool.

## Implementation

Set Emission_Admin permission for ETHx and SD to the following Stader Labs SAFE address:

Aave v3 Ethereum
Address Reward (SD): 0x30D20208d987713f46DFD34EF128Bb16C404D10f
Address Reward (ETHx): 0xA35b1B31Ce002FBF2058D22F30f95D405200A15b
EMISSION_ADMIN: 0xbDa6C9cd7eD043CB739ca2C748dAbd1fCA397132

The AIP call setEmissionAdmin() method in the emission_manager contract.

EMISSION_MANAGER.setEmissionAdmin(SD,EMISSION_ADMIN);
EMISSION_MANAGER.setEmissionAdmin(ETHx,EMISSION_ADMIN);

## Next Steps
1. Gather community feedback on this ARFC.
2. If consensus is achieved, move this prop

====================================================================================================
[25] id=0x0f73500d0f65c72482d352080ea9aa0aa92264eb059b8f646cf6f0e86556bc3d  token=AAVE  space=aavedao.eth  date=2024-02-20
TITLE: [ARFC] Amend Safety Module Emissions
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

**Title**: [ARFC] Amend Safety Module Emissions
**Author**: @karpatkey_TokenLogic
**Created**: 2024-02-15

---

# Summary

This publication proposes amending daily AAVE emissions across the three Safety Module (SM) categories to support GHO stability.

# Motivation

With the introduction of [stkGHO](htpps://app.aave.com/governance/v3/proposal/?proposalId=7), GHO went through a positive price action and recovered the 1:1 peg. 

Since then, however, the price of GHO has been drifting. There is an additional risk of GHO being redeemed from the SM and sold in the market. There are currently around [5.2M GHO cooling off](https://dune.com/xmc2/aave-safety-module) from the stkGHO module.

To support the GHO peg and to pave the way for future GHO supply expansion, this publication proposes increasing the daily AAVE emission going to stkGHO holders. 

This publication also proposes to offset this increase in AAVE emissions by reducing the emissions directed to stkAAVE and stkBPT holders. The overall amount of AAVE per day is to remain unchanged. 

# Specification

This proposal will implement the following changes to the AAVE emissions across the three SM categories: 

| Asset | Current AAVE/Day | Proposed AAVE/Day |
| --- | --- | --- |
| stkAAVE | 385 | 360 |
| stkGHO | 50 | 100 |
| stkBPT (AAVE/wstETH) | 385 | 360 |

# Next Steps

1) Gather feedback from the community and risk service providers.
2) If consensus is reached on this ARFC, escalate this proposal to the Snapshot sta

====================================================================================================
[26] id=0xc80da83fadfe4f8a4c56e1643895cb7e9b1af1d9dcd374f1b41ded5c95b42f68  token=AAVE  space=aavedao.eth  date=2024-02-21
TITLE: [ARFC] Merit - A New Aave-Alignment User Reward System
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Merit - A New Aave-Alignment User Reward System
Author: Marc Zeller - Aave Chan Initiative
Dated: 2024-02-16
---

## Summary
"Merit" proposes a merkle-tree-based periodic airdrop system, designed to reward Aave-aligned user behaviors and enhance protocol competitiveness, with a defined budget for the initial 90-day period.

## Motivation
Addressing the competitive DeFi landscape, "Merit" seeks to elevate Aave's appeal and efficiency through a rewarding mechanism that prioritizes DAO-beneficial actions, distinguishing Aave from competitors employing artificial incentive methods.

## Specification

The "Merit" system employs a booster-based model to reward specific user actions with points, dictating the weekly StkAAVE and GHO distribution. The system incorporates merit boosters and diluters to adjust user rewards based on their alignment with Aave's objectives. The initiative starts with a budget of 2.1M$ in wETH and 2.9M$ in GHO, totaling 5M$ for a 90-day duration, focusing on direct Aave protocol engagement and promoting diversified staking strategies.

### Rewarded Actions

Actions that align with Aave's strategic objectives will be rewarded:

| Action |
| --- |
| Borrow wETH |
| Borrow GHO |

### Merit boosters

Merit boosters enhance these rewards for specific behaviors:

| Behavior | Multiplier description |
| --- | --- |
| Second-degree user of aligned protocol | booster for users coming from aligned protocols that favor Aave over other protocols. |
|

====================================================================================================
[27] id=0xd7421a74db14aecb20a12c2e8c107d6718131e47b4c92cf8490fd6771b01c5b1  token=AAVE  space=aavedao.eth  date=2024-02-29
TITLE: [TEMP CHECK] Add rsETH to Aave V3 Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Add rsETH to Aave V3 Ethereum 
Author: Kelp DAO & ACI (Aave Chan Initiative)
Date: 2024-02-20

---

### **Summary**

[Kelp DAO](https://www.kelpdao.xyz/) is seeking community support for adding its Liquid Restaking Token, rsETH, to Aave V3 on Ethereum. In addition, rsETH depositors into Aave will accumulate additional [Kelp miles](https://www.kelpdao.xyz/dashboard/) and EigenLayer points.

### **Motivation**

**KelpDAO** (https://www.kelpdao.xyz/restake/) is one of the largest liquid restaking protocol built on top of the Eigen Layer. Restakers on Kelp get access to multiple benefits like restaking rewards, staking rewards and DeFi yields.

**Latest stats**:

- USD 470 Mn+ (~168k Eth) TVL
- 18K restakers onboarded
- Accepts ETHx, stETH and sfrxETH and Native ETH as collateral
- Live across mainnet and L2s such as Arbitrum and Polygon zkEVM

KelpDAO has undergone multiple security audits by top tier audit firms including Sigma Prime, Code4rena. More about KelpDAO’s security here: [Kelp DAO Audit reports](https://kelp.gitbook.io/kelp/audits).

The motivation for this proposal is to introduce a new asset class LRT (Liquid restaking tokens) to Aave and add to the diversity of LST/ LRT category.

**Restaking Innovation**

KelpDAO’s innovation in the restaking ecosystem has been focused on bringing about the following benefits to users and services-

- Restakers
    - Liqudity for restaked assets (stETH, ETHx, sfrxETH and Native ETH)
    - Access to additio

====================================================================================================
[28] id=0x4445ba1e54505430930112eeed3a6ac61a0b4102f853cf01fe1a58202399a8ee  token=AAVE  space=aavedao.eth  date=2024-02-29
TITLE: [TEMP CHECK] GHO Cross-Chain Strategy Launch with CCIP
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## Summary
This Snapshot aims to officially capture the community's agreement on adopting Chainlink Cross Chain Interoperability Protocol (CCIP) to initiate the GHO cross-chain strategy. The details of the rollout plan and the configuration of risk parameters remain subjects for future governance discussions.

## Motivation
The current limitation of GHO, which is primarily accessible only via minting on the Ethereum mainnet or through secondary markets, represents a significant constraint in its potential reach and utility across DeFi. We believe the future of GHO is to become a multichain asset where users can interact across various networks using GHO. Moving cross-chain increases the accessibility and liquidity of GHO for a larger spectrum of users.

The current moment is ideal for GHO to venture into new frontiers, and to facilitate this, it is essential to employ a solution that empowers users and stimulates growth. CCIP stands out for its high-speed and cost-effective token bridging, extensible compatibility to both EVM and non-EVM networks, ease of integration, and robust risk mechanisms. Aave Labs suggests implementing a canonical, unified cross-chain strategy for GHO using Chainlink's CCIP.

## Specification
Aave Labs proposes using Chainlink [CCIP infrastructure](https://docs.chain.link/ccip) to move GHO across blockchain networks. This will allow the seamless transfer of the GHO token between source and destination networks. CCIP transfers tokens by locking/burning

====================================================================================================
[29] id=0x166051b26be60fa3a64d7815b848b9b670a284b3da01c2d440c7815c400d7950  token=AAVE  space=aavedao.eth  date=2024-03-04
TITLE: [ARFC] Add gmBTC on Arbitrum V3
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
**Title:** [ARFC] Add gmBTC on Arbitrum V3 
**Author:** 0xlide - SaucyBlock
**Date:** 2024-02-05

---
## Summary
This publication presents the community an opportunity to add gmBTC on the Arbitrum Aave v3 Liquidity Pool.

## Motivation
GMX Protocol is the largest DEX offering derivatives and one of the most popular DeFi’s today. The introduction of several new features and integration with Chainlink Data Stream in GMX V2 has significantly reduced the risks of front-running and price manipulation compared to GMX V1. gmBTC is a BTC-USD's Liquidity Token on the GMX V2 and earn fees from leverage trading, borrowing fees and swaps. 

Integrating gmBTC as collateral asset in the Aave V3 Arbitrum Pool has the potential to create new demand for borrowable assets on Aave V3.

## Specification 
Ticker: gmBTC
Contract Adress: [0x47c031236e19d024b42f8AE6780E44A573170703](https://arbiscan.io/token/0x47c031236e19d024b42f8AE6780E44A573170703)
Chainlink Oracle: [0x395D5c5D552Df670dc4B2B1cef0c4EABfFba492f](https://arbiscan.io/address/0x395d5c5d552df670dc4b2b1cef0c4eabffba492f)

The parameters shown below are supported by @Chaos Labs
| Parameter | gmETH | gmBTC |
| --- | --- | --- |
| Isolation Mode | No | No |
| Borrowable | No | No |
| Collateral Enabled | Yes | Yes |
| Supply Cap | 3,500,000 gmETH | 4,300,000 gmBTC |
| Borrow Cap | N/A | N/A |
| LTV | 60% | 55% |
| LT | 65% | 60% |
| Liquidation Bonus | 12.00% | 12.00% |
| Liquidation Protocol Fee | 10.00% | 10.00% |
| Reserve Factor |

====================================================================================================
[30] id=0xb70490f6b0623631686d34f4ca99a7d45394ad29fdd504df3cd6e68790b22b9c  token=AAVE  space=aavedao.eth  date=2024-03-07
TITLE: [ARFC] Set Liquidity Observation Labs as Emission manager for wstETH on Scroll
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
**Title:** [ARFC] Set Liquidity Observation Labs as Emission manager for wstETH on Scroll
**Author:** @ACI (Aave Chan Initiative)
**Date:** 2024-03-02

---

## **Summary**

This ARFC proposes to set Liquidity Observation Labs wallet as the emission manager for the wstETH token on Scroll. This will enable Liquidity Observation Labs to define and fund incentive programs for all wstETH markets, including Scroll, promoting growth and expanding the user base of Aave.

## Motivation

Governance have already approved setting Liquidity Observation Labs as Emission manager for wstETH on the current Aave V3 Markets. 

But since Scroll market is live, the current ARFC is set to establish Liquidity Observation Labs as Emission manager for wstETH, aligning with the desire to actively contribute to the growth and development of the Aave V3. 

By setting their wallet as the emission manager for the wstETH token, the Foundation will be able to directly fund incentive programs that can attract more users to the pool and stimulate activity. This aligns with the broader goals of the Aave community to foster active and engaged markets.

## Specification

The Liquidity Observation Labs wallet address is:

Emission Admin Wallet (Liquidity Observation Labs): [0xC18F11735C6a1941431cCC5BcF13AF0a052A5022](https://app.safe.global/home?safe=eth:0xC18F11735C6a1941431cCC5BcF13AF0a052A5022)

The AIP call setEmissionAdmin() method in the emission_manager contract.

`EMISSION_MANAGER.setEmissionAdmin(wst

====================================================================================================
[31] id=0x81e98d2c31cdd5df48a49230db86248d388fd17a94cb8266ffff3aad30753fd1  token=AAVE  space=aavedao.eth  date=2024-03-08
TITLE: [ARFC-Addendum] Introduce "Hold StkGHO" Reward Action
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## **Title:** [ARFC-Addendum] Introduce "Hold StkGHO" Reward Action

## **Authors:** @ACI (Aave Chan Initiative)

## **Date:** 2024-03-08

---

## Simple Summary

This ARFC-Addendum proposes introducing a new rewarded action, "Hold StkGHO," within the Merit program. It also involves removing the StkGHO component from the "Staker" boost and approving the delayed start of GHO distribution.

## Motivation

To expand the Merit reward system scope and address concerns about long-term AAVE rewards for StkGHO holders, we propose introducing a new rewarded action: "Hold StkGHO." This change allows for a smooth transition to a safety module that is eventually 100% rewarded in GHO.

While there is an overlap between "Borrow GHO" and "Hold StkGHO" rewarded users, this outcome is considered acceptable. The introduction of a new rewarded action for "Hold StkGHO" allows us to address concerns about rewarding users for non-enforcable actions due to the GHO borrow cap reached. "Holding StkGHO is an incentive to liquidity sink GHO and secondary market demand.

## Specification

### Proposed Changes:

1. Introduce a new rewarded action, "Hold StkGHO."
2. Remove the StkGHO component from the "Staker" boost to avoid circular logic.
3. Approve the delayed start of GHO distribution within the Merit program.
4. Prioritize StkGHO holders' rewarded actions over having GHO debt in the Merit distribution as long as the GHO borrow cap remains below 50M.

## Next Steps

1. If this proposal reaches consen

====================================================================================================
[32] id=0xc0b723e76fa6682a58983695b7a015c3a5b928c89c2f400375c6a971ef1aba99  token=AAVE  space=aavedao.eth  date=2024-03-10
TITLE: [ARFC] Add gmETH on Arbitrum V3
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---

Title: [ARFC] Add gmETH on Arbitrum V3
Discussions: [[TEMP CHECK] Add gmETH on Arbitrum V3](https://governance.aave.com/t/temp-check-add-gmbtc-on-arbitrum-v3/16392?u=saucyblock)
Author: @0xlide - @SaucyBlock 
Date: 2024-02-05

---

## Summary
This publication presents the community an opportunity to add gmETH on the Arbitrum Aave v3 Liquidity Pool.

## Motivation
GMX Protocol is the largest DEX offering derivatives and one of the most popular DeFi’s today. The introduction of several new features and integration with Chainlink Data Stream in GMX V2 has significantly reduced the risks of front-running and price manipulation compared to GMX V1. gmETH is a ETH-USD's Liquidity Token on the GMX V2 and earn fees from leverage trading, borrowing fees and swaps. 

Integrating gmETH as collateral asset in the Aave V3 Arbitrum Pool has the potential to create new demand for borrowable assets on Aave V3.

## Specification 
Ticker: gmBTC
Contract Adress: [0x70d95587d40A2caf56bd97485aB3Eec10Bee6336](https://arbiscan.io/token/0x70d95587d40A2caf56bd97485aB3Eec10Bee6336)
Chainlink Oracle: [0xfb3264d1129824933a52374c2c1696f4470d041e](https://arbiscan.io/address/0xfb3264d1129824933a52374c2c1696f4470d041e)

The parameters shown below are supported by [@ChaosLabs](https://governance.aave.com/t/arfc-add-gmbtc-on-arbitrum-v3/16767/3?u=saucyblock)
|Parameter|Recommendation|
| --- | --- |
|Isolation Mode|NO|
|E-Mode|NO|
|Enable Borrow|Disabled |
|Stable Borrow|Disabled |
|Borrowable in Isolatio

====================================================================================================
[33] id=0xac80b6d5488c4949e30013d8ed88189ed48b64cb47580bee46921b28e3899bb7  token=AAVE  space=aavedao.eth  date=2024-03-11
TITLE: [ARFC] Set Aave Chan Initiative as Emission Manager for PYUSD on Aave V3 Ethereum Market
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
**Title:** [ARFC] Set Aave Chan Initiative as Emission Manager for PYUSD on Aave V3 Ethereum Market 
**Author:** @ACI (Aave Chan Initiative)
**Date:** 2024-03-04

---

## **Summary**

This ARFC proposes to set the Aave Chan Initiative (ACI) wallet as the emission manager for the PYUSD token on Aave V3 Ethereum Market. This will enable the ACI to enact incentive programs funded by ecosystem partners for all PYUSD markets, promoting growth and expanding the user base of Aave. 

## Motivation

The Aave Chan Initiative (ACI) has been in discussion with various parties that have a desire to actively contribute to the growth and development of the Aave V3 on the Ethereum Network. 

Recently, governance approved the [addition of PYUSD to Aave V3 Ethereum Market](https://governance.aave.com/t/arfc-add-pyusd-to-aave-v3-ethereum-market/16218). As a result, onboarding PYUSD into Aave has:

- Built synergies between Aave and PYUSD.
- Offered Aave users an additional stablecoin option.
- Strengthened the relationship between the PYUSD & the GHO stablecoin.

In order to facilitate emissions by various stakeholders, ACI proposes becoming the emissions manager for PYUSD on Aave V3 Ethereum Market. Emission incentives will be sent to ACI multisig and distributed as agreed on with partners. By setting the multisig as the emission manager for the PYUSD token, the ACI will be able to directly manage incentive programs that can attract more users to the pool and stimulate activity. This align

====================================================================================================
[34] id=0x226be983f6e70fd1fbf004c2757dbc575b767c918c9a964d3a6a1b026c8806af  token=AAVE  space=aavedao.eth  date=2024-03-11
TITLE: [ARFC] Set Aave Chan Initiative as Emission Manager for sUSD on Aave V3 Optimism
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
**Title:** [ARFC] Set Aave Chan Initiative as Emission Manager for sUSD on Aave V3 Optimism 
**Author:** @ACI (Aave Chan Initiative)
**Date:** 2024-03-06

---

# **Summary**

This ARFC proposes to set the Aave Chan Initiative (ACI) wallet as the emission manager for the sUSD token on Optimism Aave V3 market. This will enable the ACI to enact incentive programs funded by SNX ecosystem partners for all sUSD markets, promoting growth and expanding the user base of Aave on Optimism.

# Motivation

The Aave Chan Initiative has been in discussion with various parties that have a desire to actively contribute to the growth and development of Aave V3 on Optimism. In order to facilitate emissions by various stakeholders, ACI proposes becoming the emissions manager for sUSD on Optimism. Emission incentives will be sent to ACI multisig and distributed as agreed on with partners. 

By setting the multisig as the emission manager for the sUSD token, the ACI will be able to directly manage incentive programs that can attract more users to the protocol and stimulate activity. This aligns with the broader goals of the Aave community to foster active and engaged markets on Optimism.

# Specification

The ACI multisig address OP:0xac140648435d03f784879cd789130F22Ef588Fcd will be set as Emissions manager.

The call to the setEmissionAdmin() method in the emission_manager contract will be as follows:

`EMISSION_MANAGER.setEmissionAdmin(sUSD, 0xac140648435d03f784879cd789130F22Ef588Fcd);`

Thi

====================================================================================================
[35] id=0x484145c111c232e1ea7b71222b542d7aa9445fee65e1cacd1ef79c0edae86345  token=AAVE  space=aavedao.eth  date=2024-03-13
TITLE: [ARFC] Emission Manager Framework Update
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
**Title:** [ARFC] Emission Manager Framework Update 
**Author:** @ACI (Aave Chan Initiative)
**Date:** 2024-03-08

---
## Motivation

In the current market dynamic, with incentives programs becoming increasingly popular among protocols looking to collaborate, the existing framework for adding new emission managers to Aave pool reserves is considered unnecessary complex and lengthy. Given the general consensus in favor of incentives programs, it is challenging to consider a proposal that would fail to gain community support.

The current onboarding process involves:

| Step | Duration | Description |
| --- | --- | --- |
| Publish ARFC on forum | 5 days | Seek feedback from the community |
| Snapshot vote | 4 days | Gather consensus and obtain a YAE outcome |
| AIP publication | 5 days | Reach consensus and implement the new role |

Assuming perfect sync and seamless governance, this minimum two-week timeframe is deemed inefficient. To address these challenges, we propose updating the framework to incorporate emission admins into the "Direct-to-AIP" framework.

## Specification

### Proposed Changes:

1. Incorporate emission admins into the "Direct-to-AIP" framework, enabling direct escalation of proposals to the AIP stage following publication on the forum.
2. Pre-authorize the inclusion of an emission admin as part of either an ad-hoc steward or current risk steward role to facilitate a more efficient and streamlined onboarding process.

## Next Steps

1. Community feedba

====================================================================================================
[36] id=0xb7226dd6441b67225924082215f7a512bfd98252897ee43a879084e07ab53607  token=AAVE  space=aavedao.eth  date=2024-04-01
TITLE: [ARFC] aAMPL interim distribution
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
&nbsp;

## Simple summary

Proposal for the approval of an interim distribution of 300’000 stable-coins from the Aave Collector to allow partial withdrawals by aAMPL suppliers to Aave v2 Ethereum, consequence of the problem detected end 2023.

Additionally, this proposal will include technical updates on the AMPL reserve to better settle accounting for this distribution.

&nbsp;

## Motivation

On December 2023, a problem was detected on the AMPL custom reserve on Aave v2 Ethereum, causing an unexpected inflation of AMPL-related balances and supply, not following the intended design by the Ampleforth team.

While further analysis is performed for the most reasonable strategy on giving withdrawal liquidity for aAMPL supplies, an interim distribution of 300’000 USD value is proposed as lower threshold, to allow aAMPL suppliers to proceed partially with their withdrawals.

Also, as follow-up of previous AIPs, this proposal will include extra steps of not create problems accounting wise.

Important to read the full context on https://governance.aave.com/t/ampl-problem-on-aave-v2-ethereum/15886.

&nbsp;

## Specification

The specific technical details will be defined at AIP stage once this ARFC will be approved, but high-level the payload will contain the following:

- Activation of a USDC/USDT distribution on AaveMerkleDistributor contract used in the past for the Rescue Mission of assets that users mistakenly sent to Aave contracts. The claims of each account will be defined as

====================================================================================================
[37] id=0x6ad248c0f37e7abf9432f35316910ea274579a908bfb0957233828e1fc722d98  token=AAVE  space=aavedao.eth  date=2024-04-18
TITLE: [ARFC] "Merit is Forever" Reward System Program Extension
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] "Merit is Forever" Reward System Program Extension
Date: 2024-04-11
Author: Marc Zeller - Aave-Chan Initiative
---

## Summary:

Following the success of Merit's first two rounds, this ARFC proposes the long-term adoption of the Merit reward system for the DAO and allocating a 5m$/quarter budget for the next 12 months.

## Motivation:

Merit was designed to address two main objectives:

1. Counteract the negative impact of Morpho optimizer on Aave DAO revenue by attracting Ethereum back from Morpho. Merit Round 1 resulted in approximately 165k ETH leaving Morpho and growing Aave's market share. The Morpho product is now imbalanced (limited to a 52k ETH capacity), ensuring it will not offer additional yield on top of Aave, thus achieving its primary goal.
2. Support the GHO stablecoin peg, fostering supply growth and revenue expansion while maintaining a stablecoin base for the safety module:

   - StkGho supply increased by 45%.
   - GHO supply grew by 40%.
   - The GHO borrow rate was increased to 13.8%.
   - GHO peg remained within target rate 97% of the time.
   - GHO protocol revenue grew significantly, reaching approximately 6.5m$/year.

Merit Round 2 involved 1367 eligible users, with Staker & Strakoor being the largest booster (over 100 users), indicating a strong user trust in the Aave protocol and willingness to participate in the Safety module for yield and discounted GHO borrowings.

Building on these positive outcomes from the first two Merit rou

====================================================================================================
[38] id=0x372ea60168390ca30be8890ae18ba3c1bb171428ad613a3c8c1a568721c1d65d  token=AAVE  space=aavedao.eth  date=2024-04-24
TITLE: [ARFC] aAMPL Second Distribution
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
&nbsp;

## Simple summary
A proposal for a follow-up distribution of 758’000 stable-coins from the Aave Collector to allow full withdrawals by aAMPL suppliers to Aave v2 Ethereum, consequence of the problem detected at the end of 2023.

&nbsp;

## Motivation
In December 2023, a problem was detected on the AMPL custom reserve on Aave v2 Ethereum, causing an unexpected inflation of AMPL-related balances and supply, not following the intended design by the Ampleforth team.

After further analysis and remediation strategy, the Aave governance approved and executed a proposal on April 17th to provide approximately 300’000 USDC for aAMPL holders to claim. This was designed as an initial and interim distribution, with the sole objective of providing liquidity for users affected as soon as possible. Meanwhile, the service providers of the Aave DAO and the Ampleforth team completed further analysis for a final distribution proposal; this one.

&nbsp;

## Specification
To fully understand the problem at hand and the rationale of this distribution, we recommend mandatorily reading its specification on https://governance.aave.com/t/ampl-problem-on-aave-v2-ethereum/15886/155, to make an informed decision.

&nbsp;

In summary, this proposal recommends making claimable 758’000 stablecoins from the Aave Ethereum Collector, in addition to the already distributed 300’000 USDC, making a total of approximately $1,057,677.

Some key points output of the analysis are:

- Decisions when doing the a

====================================================================================================
[39] id=0xf01d857c392a5d3efcd69725cdee5a5d8e94e5cbe952791d24ff26a26f2b83fa  token=AAVE  space=aavedao.eth  date=2024-04-25
TITLE: [ARFC] Updating weETH Risk Parameters
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] Updating weETH Risk Parameters 
Date: 2024-04-18
Author: MarcZeller - ACI
---

## Summary:

This proposal aims to update the risk parameters and interest rate strategy of the weETH asset on the Ethereum pool to boost Aave DAO revenue and encourage collateral adoption.

## Motivation

The successful onboarding of EtherFI into Aave has demonstrated significant demand for weETH usage as both collateral and a borrowing asset, with both initial supply caps reached in minutes and second cap increases filled under similar conditions. To accommodate this demand and facilitate protocol growth, this proposal suggests increasing the supply cap of weETH on the Ethereum pool and the borrow cap at 35% of the new supply cap amount. This proposal also aims at changing the interestRate Strategy to place the optimal ratio at 35% of liquidity.

Expanding borrow capacity will result in a higher collateral yield, which in turn creates a positive flywheel effect on supply and demand. By maintaining the borrow cap at an optimal ratio (35%) of the supply cap, we can balance risk, available liquidity, and LP yield effectively.

We also propose to increase weETH RF to 45% to contribute to Aave DAO revenue.

## Specification

| Chain     | Asset        | Current Supply Cap  | Recommended New Supply Cap | Current Borrow Cap   | Recommended New Borrow Cap |
| ---       | ---          | ---                 | ---                         | ---                 | ---

====================================================================================================
[40] id=0xe75e505a693c177342a2c4bc62241b19fc04af508c3e11b76da5d46bdc597a45  token=AAVE  space=aavedao.eth  date=2024-04-28
TITLE: [TEMP CHECK] Add AERO to Base V3
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Add AERO to Base V3
Author: 0xlide - SaucyBlock
Date: 2024-04-20

---

## Summary
This publication presents the community an opportunity to add AERO on the Base Aave v3 Liquidity Pool.

## Motivation
Aerodrome Finance is the largest decentralized exchange on Base that inherits Verodrome. AERO is ERC-20 utility token and can be used as the voting powers for the amount of emission rewards the pool receives each epoch by vote-escrow their tokens and receive a $veAERO

The Addition of AERO to Base V3 is diversifying listed assets and improve user experience. Furthermore, AERO earned from Pool can be used to boost GHO and/or aToken adoption and liquidity on Base as a strategic asset.

## Specification 
Ticker: AERO
Contract Adress: [0x940181a94A35A4569E4529A3CDfB74e38FD98631](https://basescan.org/address/0x940181a94A35A4569E4529A3CDfB74e38FD98631)
Chainlink Oracle: [0x4EC5970fC728C5f65ba413992CD5fF6FD70fcfF0](https://basescan.org/address/0x4EC5970fC728C5f65ba413992CD5fF6FD70fcfF0)

Proposed risk parameters will be shared at the potential ARFC stage of this proposal.

## Reference
Project: [https://aerodrome.finance/](https://aerodrome.finance/)
GitHub:[https://github.com/aerodrome-finance](https://github.com/aerodrome-finance)
Docs: [https://aerodrome.finance/docs](https://aerodrome.finance/docs)
Audit*¹: [https://velodrome.finance/security](https://velodrome.finance/security)
Twitter: [https://twitter.com/aerodromefi](https://twitter.com/aerodromefi)

*¹

====================================================================================================
[41] id=0x59c7ea88a42b78351abb1e945aa67f9b0b5bf20502b70a6292c691ec2ddb8093  token=AAVE  space=aavedao.eth  date=2024-05-06
TITLE: [ARFC] Safety Module stkGHO - Rewards Adjustment
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Safety Module stkGHO - Rewards Adjustment
Author: @karpatkey_TokenLogic
Created: 2024-04-29

---

# Summary

This publication proposes replacing the AAVE emissions to stkGHO holders within the Safetey Module (SM) with GHO.

# Motivation

The stkGHO category within the SM currently holds 21.43M units of GHO and receives 100 AAVE/day. This is equivalent to 36,500 units of AAVE emissions per year worth an estimated $3,394,500 at an AAVE price of $93.00/unit. The current annualised accrued GHO revenue, with 50M units of supply and Borrow Rate of [12.26%](https://dune.com/queries/3206348/5447167) is 6.13M. The Aave DAO's GHO revenue is sufficient to replace the AAVE emissions to stkGHO holders and meaningfully contribute to offsetting other DAO expenses like [Merit](https://governance.aave.com/t/arfc-merit-is-forever-reward-system-program-extension/17336). 

With a bullish GHO revenue outlook, migrating stkGHO holders' rewards from AAVE to GHO is a positive step forward for Aave DAO. As a direct result of this proposed change, the AAVE Emissions runway is extended by 13.89%. After a successful migration of stkGHO rewards to GHO, other Safety Modules can be evaluated for similar adjustments. In particular, stkBPT would make a good candidate once GHO supply is large enough to cover the corresponding $AAVE emissions.


Given the recent price action in the AAVE price and the resulting lower yield on the stkGHO category, this publication propose a 20% yield on curren

====================================================================================================
[42] id=0x1f74c77f10c5f5d005e066c9454fc318073edb0699040d950dc9a90de0a74bdf  token=AAVE  space=aavedao.eth  date=2024-05-07
TITLE: [TEMP CHECK] Add rsETH to Aave V3 Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Add rsETH to Aave V3 Ethereum 
Author: Kelp DAO & ACI (Aave Chan Initiative)
Date: 2024-05-07

---

### **Summary**

[Kelp DAO](https://www.kelpdao.xyz/) is seeking community support for adding its Liquid Restaking Token, rsETH, to Aave V3 on Ethereum. In addition, rsETH depositors into Aave will accumulate additional [Kelp miles](https://www.kelpdao.xyz/dashboard/) and EigenLayer points.

### **Motivation**

**KelpDAO** (https://www.kelpdao.xyz/restake/) is one of the largest liquid restaking protocol built on top of the Eigen Layer. Restakers on Kelp get access to multiple benefits like restaking rewards, staking rewards and DeFi yields.

**Latest stats**:

- USD 470 Mn+ (~168k Eth) TVL
- 18K restakers onboarded
- Accepts ETHx, stETH and sfrxETH and Native ETH as collateral
- Live across mainnet and L2s such as Arbitrum and Polygon zkEVM

KelpDAO has undergone multiple security audits by top tier audit firms including Sigma Prime, Code4rena. More about KelpDAO’s security here: [Kelp DAO Audit reports](https://kelp.gitbook.io/kelp/audits).

The motivation for this proposal is to introduce a new asset class LRT (Liquid restaking tokens) to Aave and add to the diversity of LST/ LRT category.

**Restaking Innovation**

KelpDAO’s innovation in the restaking ecosystem has been focused on bringing about the following benefits to users and services-

- Restakers
    - Liqudity for restaked assets (stETH, ETHx, sfrxETH and Native ETH)
    - Access to additio

====================================================================================================
[43] id=0x300e594559b42518cf9cad713d1cf7d0cfc1c75f080c8e39c45b846f08205e3e  token=AAVE  space=aavedao.eth  date=2024-05-08
TITLE: [TEMP CHECK] Add AERO to Base V3 *Reproposal
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Add AERO to Base V3
Author: 0xlide - SaucyBlock
Date: 2024-04-20

---

## Summary
This publication presents the community an opportunity to add AERO on the Base Aave v3 Liquidity Pool.

## Motivation
Aerodrome Finance is the largest decentralized exchange on Base that inherits Verodrome. AERO is ERC-20 utility token and can be used as the voting powers for the amount of emission rewards the pool receives each epoch by vote-escrow their tokens and receive a $veAERO

The Addition of AERO to Base V3 is diversifying listed assets and improve user experience. Furthermore, AERO earned from Pool can be used to boost GHO and/or aToken adoption and liquidity on Base as a strategic asset.

## Specification 
Ticker: AERO
Contract Adress: [0x940181a94A35A4569E4529A3CDfB74e38FD98631](https://basescan.org/address/0x940181a94A35A4569E4529A3CDfB74e38FD98631)
Chainlink Oracle: [0x4EC5970fC728C5f65ba413992CD5fF6FD70fcfF0](https://basescan.org/address/0x4EC5970fC728C5f65ba413992CD5fF6FD70fcfF0)

Proposed risk parameters will be shared at the potential ARFC stage of this proposal.

## Reference
Project: [https://aerodrome.finance/](https://aerodrome.finance/)
GitHub:[https://github.com/aerodrome-finance](https://github.com/aerodrome-finance)
Docs: [https://aerodrome.finance/docs](https://aerodrome.finance/docs)
Audit*¹: [https://velodrome.finance/security](https://velodrome.finance/security)
Twitter: [https://twitter.com/aerodromefi](https://twitter.com/aerodromefi)

*¹

====================================================================================================
[44] id=0x4fe039367614b6dcdb0dfc15a306b0928fb9d3eee8e076e7f9a432a16a218449  token=AAVE  space=aavedao.eth  date=2024-05-10
TITLE: [ARFC] Fund USDC & USDT GSM
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Fund USDC & USDT GSM 
author: @karpatkey_TokenLogic & @ACI
created: 2024-05-02

---

# Summary

This publication proposes funding the USDC and USDT GHO Stability Modules (GSM).

# Motivation

With significant improvement in the GHO price as a result of the ongoing merit program, the GHO Stewards would like to propose funding both the USDC and USDT GSMs. 

Funding the GSM is expected to help mitigate the potential impact of funds being withdrawn from the stkGHO Safety Module (SM) category by providing continuous support for the GHO peg and protect the DEX liquidity spread across several pools.

The below table shows the larger holding sizes currently in cool down. Although some users will be eligible to withdraw GHO before the GSM is funded, the GSM is intended to be funded before some of the later holdings exit cool down. 

| SM Category | Size | Cool Down Date |
| :---:       | :---:| :---:          |
| stkGHO      | 1.4M |  06/05/2024    |
| stkGHO      | 3.0M |  08/05/2024    |
| stkGHO      | 0.9M |  10/05/2024    |
| stkGHO      | 2.4M |  19/05/2024    |

Source: [Dune Dashboard](https://dune.com/queries/2816986/4697667)

With the introduction of the Merit rewards expected to be included in the Aave Protocol frontend very soon and AAVE emissions flowing to depositors, we expect several of these addresses will recommit to holding GHO within the SM. 

# Specification

Two Allowances are to be created enabling the Aave Liquidity Committee (ALC) to draw 1M

====================================================================================================
[45] id=0x645981c18f5dc61c07324a39d57bcb873ebd8fb9e4a435280cac57cb07a8090b  token=AAVE  space=aavedao.eth  date=2024-05-14
TITLE: [ARFC] Aave V3 Deployment on Celo
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] Aave V3 Deployment on Celo
Date: 2024-05-09
Author: @pennblockchain, @Isha - Isha Varshney (Celo Foundation)
---

## Summary:

This ARFC proposes the deployment of Aave on Celo to expand Aave real-world lending and green asset collateral to users around the world, with the provision of rewards to bootstrap liquidity.

## Abstract:

Upon approval by the Aave community, Aave will be deployed on Celo with a selection of suitable assets for collateral, including CELO, USDC, USDT, cUSD and cEUR. This deployment aims to enhance the growth and collaboration between the Aave and Celo communities, providing new opportunities for both ecosystems. This deployment will be incentivized by the tune of $3M over 3 years (with option to extend) by Celo Foundation directly or through ecosystem partners.

## Motivation:

Deploying Aave on Celo presents potential benefits for both Aave and Celo ecosystems. The Celo ecosystem offers a unique value proposition featuring real-world usage and ReFi. As Aave will be given a prominent role on Celo, this deployment offers Aave differentiated expansion and revenue opportunities. For more details on Celo’s real-world usage and key features, please refer to the [temp check](https://governance.aave.com/t/temp-check-aave-v3-deployment-on-celo/14385).

1. A deployment on Celo expands AAVE’s utility and user base to a unique population of Celo’s mobile-first community which has [grown significantly 2](https://app.artemis.xyz/project/celo) ove

====================================================================================================
[46] id=0x2a6ffbcff41a5ef98b7542f99b207af9c1e79e61f859d0a62f3bf52d3280877a  token=AAVE  space=aavedao.eth  date=2024-05-15
TITLE: [ARFC] GHO Cross-Chain Launch
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] GHO Cross-Chain Launch
Author: Aave Labs
Date: 2024-05-15
---

# **Summary**

This snapshot proposes initiating the cross-chain strategy for the GHO stablecoin, the native asset of the Aave Protocol, beginning with the initial expansion to the Arbitrum network. This expansion will utilize Chainlink Cross-Chain Interoperability Protocol (CCIP). After extensive discussions concerning the cross-chain token model, the bridge, and potential networks, we are presenting this vote which gives final snapshot approval on the whole strategy, based on previous discussions and risk parameters provided by Chaos Labs.

# **Motivation**

The current accessibility of GHO, primarily through minting on the Ethereum mainnet or via secondary markets, significantly limits its potential reach and utility within the DeFi landscape. Transitioning to a cross-chain model will enhance GHO’s accessibility and liquidity, appealing to a broader userbase. Additionally, integrating with alternative chains could greatly improve the overall user experience by offering faster transactions and reduced costs, thus making GHO a more attractive financial tool. This shift also presents new opportunities within the ecosystem of each network, allowing access to a wide array of integrations with other protocols and tools, further enriching GHO’s utility and appeal.

# **Specification**

Below are the main actions to address, and the AIP will provide full implementation and details. For a detailed over

====================================================================================================
[47] id=0x1f0f0a63eeb34f9fc6a176527253495e43cefc28714734dbee79d9f33e943a67  token=AAVE  space=aavedao.eth  date=2024-05-19
TITLE: [TEMP CHECK] Safety Module - Create GHO/USDC E-CLP Category
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Safety Module - Create GHO/USDC E-CLP Category
author: @karpatkey_TokenLogic
created: 2024-05-13

---

# Summary

This publication proposes creating a new Safety Module (SM) category for the GHO/USDC E-CLP by Gyroscope built on Balancer v2.

# Motivation

Similarly to Staked ABPT, the ability to stake GHO liquidity pool tokens improves the value proposition of the SM by providing the dual service of deep GHO liquidity and protection in the case of protocol shortfall events. Additionally, Liquidity Providers (LPs) can also benefit from earning trading fees.

The Gyroscope protocol developed a concentrated liquidity AMM called Elliptic Liquidity Pools (E-CLPs) that sits on top of Balancer. This technology achieves liquidity efficiency by providing assymetric liquidity to a specific price range based on parameters like amplification, price boundaries and peak location. More information about E-CLPs can be found [here](https://docs.gyro.finance/gyroscope-protocol/concentrated-liquidity-pools/e-clps).

With GHO trading close to $1.00 and the [GHO Stability Module](https://governance.aave.com/t/arfc-fund-usdc-usdt-gsm/17566) to be funded, now is an ideal time to add a GHO LP to the SM. By adding the GHO-USDC E-CLP, it is expected to significantly improve market depth as well as USDC liquidity with the SM. Unlike other pool types on Balancer, the E-CLP requires dual asset deposits upon entering the LP.

The Aave Liquidity Committee (ALC) developed expertise

====================================================================================================
[48] id=0x4a10e2a8ca95024d7cf0791aa82ed262c816ff0ee78bc2f3ab3487e70d731361  token=AAVE  space=aavedao.eth  date=2024-05-19
TITLE: [ARFC] Orbit Program Renewal May 2024
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] Orbit Program Renewal May 2024 
Date: 2024-05-13
Author: Marc Zeller - Aave Chan Initiative (ACI)
---

## Summary

Proposing the renewal of the Orbit program for recognized delegates, compensating them with GHO and ETH reimbursement of Gas costs associated with their governance activity.

## Motivation

Orbit recognizes the added value of the Delegates in the decentralization & diversity of the Aave DAO. This compensation allows them to focus on aave and keep their contribution efforts to our governance. The ACI proposes the extension of Orbit for a new quarter.

With the transition to Governance V3, a significant feature introduced is gasless voting via Gelato integration on the [DAO-run governance app](https://vote.onaave.com), making it easier for delegates to participate without the burden of gas costs. This innovation prompts the proposal to discontinue the general gas rebate program. However, recognizing the continued necessity for proposal creation and payload deployment activities, we propose maintaining targeted gas rebates for these specific actions.

## Specification

* **Period Coverage:** Blocks 19162697 (5th Feb 2024) to Block 19860031 (May 13th 2024)
* **Eligible Platforms:**
	+ EzR3al
	+ Stable Labs
	+ Saucy Block
	+ Areta
* **Gas Rebate:** Since this period is entirely covered by Governance V3, the Orbit program does not reimburse delegate vote gas as their vote is now subsidized by Gelato. We will continue to reimburse Service Providers for

====================================================================================================
[49] id=0x9e2e3bd26866212d0cbd8e7cefcfa21eec9522202fd25b02456b8ff59371db08  token=AAVE  space=aavedao.eth  date=2024-05-20
TITLE: [ARFC] Onboard tBTC to Aave v3 on Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [ARFC] Onboard tBTC to Aave v3 on Ethereum
Date: 2024-05-13
Author: Aave Chan Initiative (ACI)
---

## Summary

The proposal aims to onboard Threshold Network’s tBTC, to the Aave v3 protocol on Ethereum. tBTC is backed one-to-one with Bitcoin.

## Motivation/Background:

tBTC is Threshold’s decentralized and permissionless bridge to bring BTC to the Ethereum network. tBTC has been designed to allow Bitcoin holders to participate in Ethereum’s Decentralized Finance (DeFi) applications. Users wishing to utilize their Bitcoin on Ethereum can use the tBTC decentralized bridge to deposit their Bitcoin into the system and get a minted tBTC token in their Ethereum wallet.

Having recently acquired a Chainlink oracle, tBTC enables Aave users to have access to the only wrapped Bitcoin, which can be permissionlessly minted and redeemed, where the BTC that backs it is not held by a central intermediary, but is instead held by a decentralized network of nodes using threshold cryptography. This implies a fully decentralized and permissionless lending and borrowing experience for BTC (i.e. bridge native BTC to tBTC and borrow via Aave).

tBTC was created by a decentralized effort of contributors at the Threshold Network DAO, and extensively utilizes the Threshold Network’s threshold cryptography to create a secure BTC asset. tBTC is a product launched on Threshold Network, on which many other decentralized applications are being built.

Threshold Network DAO was born out of the

====================================================================================================
[50] id=0x418eb093009f59a000c223f2455dc551983ec2a09f26e92f41be3640cce8f39c  token=AAVE  space=aavedao.eth  date=2024-05-21
TITLE: [ARFC Addendum] Increase Supply and Borrow Caps for weETH
CHOICES: YAE (Aggresive) | YAE (Conservative) | NAY | ABSTAIN
TEXT (first 1500 characters):
Title: [ARFC Addendum] Increase Supply and Borrow Caps for weETH

Date: 2024-05-21

Author: @ACI 

---

# **Summary**

This proposal asks for governance approval to raise the supply caps for weETH to accommodate growing demand. The goal is to balance risk with profitability, ensuring sustainable growth and optimized revenue.

# **Motivation**

weETH has been consistently hitting its current supply cap, reflecting substantial market demand. Increasing the cap will provide more liquidity for users, leading to higher borrow volumes and enhanced protocol revenue.

However, some voices from the community raised concerns about the speed of growth of weETH in the aave ecosystem and would like a slowed-down approach to allow the Etherfi & LRTs ecosystem to gain maturity.

# **Specification**

We propose governance to greenlight the Risk Stewards to raise caps according to market conditions and risk tolerance up to newly defined ceilings, with an aggressive or conservative approach.

1. Aggressive Approach: Increase weETH caps up to 1M weETH
2. Conservative Approach: Increase weETH caps up to 500K weETH

The implementation of new caps will be done via Risk Steward.

# Disclaimer

The ACI is not presenting this ARFC on behalf of any third party and is not compensated for creating this ARFC.

# Next Steps

1. If consensus is reached on this [ARFC Addendum], escalate this proposal to the Snapshot stage with 4 options: YAE (Aggressive Option,) YAE (Conservative Option),  Abstain, or NAY
2

====================================================================================================
[51] id=0x4df68c8364adbc1b538e4aebd7875783f5b489d9656a7b171255338526c21e3e  token=AAVE  space=aavedao.eth  date=2024-05-28
TITLE: [TEMP CHECK] Deploy Aave V3 on Mode
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [TEMP CHECK] Deploy Aave V3 on Mode 
Author: ACI (Aave Chan Initiative)
Date: 2024-05-23

---

### **Summary**

Mode is a state-of-the-art, modular L2 blockchain that builds on the Ethereum network via deployment on the OP Superchain. 

Deploying Aave on Mode involves setting up a new instance of the Aave protocol on the Mode L2 blockchain, which is positioned to be the DeFi hub of the OP Superchain. This proposal aims to leverage Mode's modular infrastructure tailored for DeFi applications, offering potential enhancements in scalability and interoperability within the ecosystem.

## **Motivation/Background**

Mode intends to be the DeFi hub of the Superchain, offering a best-in-class yield experience by attracting cutting edge and innovative DeFi protocols to weave into and build atop of a solid foundation of trusted blue chip favorites, Velodrome, Balancer en route, and (hopefully soon-to-be) Aave.

Mode stands apart in its approach to DeFi and liquidity architecture by working closely with stalwart protocols and teams to push integrations and intra-chain operability. By keeping an extremely active presence in the telegram channels and engaging in transformative open dialogue, Mode harnesses the collective wisdom of its builders to design an L2 every DeFi user would be proud to call home. Mode currently has baked-in incentives to help bootstrap early protocols via an ongoing metric based DevDrop which is redistributed to users, as well as Sequencer Fee Sharing,

====================================================================================================
[52] id=0xefde834f679751ec44f3f48eac6c48e74a95f4d421a8b96b8156332b9d3c8d3d  token=AAVE  space=aavedao.eth  date=2024-05-30
TITLE: [ARFC] Safety Module - Create GHO/USDC E-CLP Category
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Safety Module - Create GHO/USDC E-CLP Category
author: @karpatkey_TokenLogic
created: 2024-05-25

---

# Summary

This publication proposes creating a new Safety Module (SM) category for the GHO/USDC E-CLP by Gyroscope built on Balancer v2.

# Motivation

With the initial [TEMP CHECK](https://snapshot.org/#/aave.eth/proposal/0x1f0f0a63eeb34f9fc6a176527253495e43cefc28714734dbee79d9f33e943a67) vote passing, this publication progresses the proposal to add the GHO/USDC E-CLP to the Aave SM to ARFC stage of the governance process.

With GHO trading close to $1.00 and the [GHO Stability Module](https://governance.aave.com/t/arfc-fund-usdc-usdt-gsm/17566) to be funded, now is an ideal time to add a GHO LP to the SM. By adding the GHO-USDC E-CLP, it is expected to significantly improve market depth as well as USDC liquidity with the SM.

The GHO/USDC E-CLP pool requires dual asset deposits when Liquidity Providers enter the pool and when GHO is trading at $1.000, the pool is mostly USDC (75%). The pool's liquidity distribution is optimised for swap volume with Peak liquidity at 0.9995 reflecting that GHO is more likely to trade just beneath $1.000 than over. The upper and lower liquidity range was set to optimise the efficiency of the liquidity whilst still providing some USDC depth to the lower bound. The below provides a graphic representation of the liquidity profile and composition of the pool for GHO priced in USDC. 

![Screenshot 2024-05-23 at 18.45.52](https

====================================================================================================
[53] id=0xed2fd3dfee1f29f04b6cda4a5c4629fcca32a5c961b1b3e2a49ba6842367ce31  token=AAVE  space=aavedao.eth  date=2024-06-02
TITLE: [ARFC] Adjusting Interest Rate Curve for weETH on Arbitrum and Base
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## [ARFC] Adjusting Interest Rate Curve for weETH on Arbitrum and Base

## Author: ACI ( Aave Chan Initiative)

## Date: 2024-05-27

---

## **Summary**

The current proposal suggests adjusting the Interest Rate Curve for weETH on Arbitrum and Base networks to align with the mainnet, so Risk Parameters will be the same for weETH on Mainnet, Arbitrum, and Base networks.

The aim is to optimize the utilization rates and improve both lending and borrowing for users.

## **Motivation**

By adjusting the Interest Rate Curve, we aim to encourage more borrowing and lending activity, optimize the utilization rates, and enhance liquidity on Arbitrum and Base networks.

1. **Base Rate Increase:** Increasing the base rate provides a more attractive return for lenders, encouraging more weETH deposits.
2. **Slope 1 Adjustment:** Adjusting the Stable Rate Slope offers slightly higher interest for moderate utilization, making borrowing more attractive.
3. **Slope 2 Adjustment:** Reducing Stable Rate Slope 2 prevents excessively high borrowing costs at higher utilization rates, thus avoiding sharp declines in borrowing activities.
4. **Utilization Rate Optimal:** Raising the optimal utilization rate aims to better match the network's current usage patterns, ensuring a smoother transition between interest rate slopes and maintaining liquidity.
5. **Reserve Factor:** weETH borrowers and  LP are less sensible to interest rates due to external incentives, to Optimize the DAO revenue the reserve

====================================================================================================
[54] id=0x364de11d3a298f2c76721a8926cb32823cc29d0a95eadecbc0a98c628a38194b  token=AAVE  space=aavedao.eth  date=2024-06-11
TITLE: [ARFC] Set ACI as Emission Manager for Liquidity Mining Programs
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Set ACI as Emission Manager for Liquidity Mining Programs 
Author: ACI (Aave Chan Initiative)
Date: 2024-06-06

---

# **Summary**

The current ARFC proposes to appoint the Aave Chan Initiative (ACI) as the Emission Manager for liquidity mining programs across Aave markets. This will enable ACI to manage incentive programs funded by different partners, with the purpose of stimulating market activity and growth.

# **Motivation**

Liquidity mining programs are essential for attracting liquidity providers by offering rewards for their participation. Effective management of these programs is crucial for the sustained growth of the Aave Ecosystem. Therefore, ACI, with its extensive experience and strategic partnerships, is well-positioned to manage these emissions effectively.

A recent example is the [Long Term Incentive Program (LTIPP)](https://forum.arbitrum.foundation/t/aave-ltipp-application-final/21741) from Arbitrum DAO, where Aave DAO will receive 750,000 ARB tokens, illustrating the benefits of coordinated emission management.

# **Specification**

1. Appointment of ACI as Emission Manager for Liquidity Mining Programs
    1. ACI will be authorized to manage Emission Programs for Liquidity Mining across Aave Markets.
    2. ACI’s multisig address will be the one receiving and distributing emissions on behalf of the DAO.
2. Appointment of ACI as coordinator with ecosystem partners, to define and implement emission strategies, managing the distribution o

====================================================================================================
[55] id=0xb74537a0528f484e9cc76d8c7931eedef7b6290e7d2dc725b2c98e623a214f95  token=AAVE  space=aavedao.eth  date=2024-06-17
TITLE: [ARFC] Deployment of Aave on zkSync
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

Title: [ARFC] Deployment of Aave on zkSync
Author: ACI (Aave Chan Initiative)
Date: 2024-06-10

---

# **Summary**

The current ARFC proposes deploying Aave V3 on zkSync to leverage the scalability and cost-efficiency of zk-Rollups. By integrating with zkSync, Aave can offer users faster and cheaper transactions while maintaining the security and decentralization of the Ethereum mainnet. This ARFC seeks governance approval for the deployment of an Aave V3 instance on the zkSync Era L2.

## Motivation

zkSync is a Layer 2 scaling solution for Ethereum that utilizes zk-Rollups to batch multiple transactions off-chain and submit a single proof to the Ethereum mainnet. This approach significantly enhances transaction throughput and reduces gas fees. Deposit and borrowing activities can greatly benefit from the reduced transaction costs and increased throughput offered by zkSync.

### Benefits of deploying to zkSync

1. **Reduce Gas Fees:** By leveraging zkSync’s efficient transaction processing, users will incur significantly lower gas fees.
2. **Scalability:** zkSync’s high throughput will allow Aave to scale effectively, accommodating more users and transactions without compromising performance.
3. **New Frontier & Opportunities:** This deployment will offer the Aave DAO a new frontier for growth to explore and a new avenue path for GHO, our stablecoin.
4. **Interoperability:** Due to zkSync infrastructure, an Aave V3 deployment in the zkSync Era can benefit other Aave fam

====================================================================================================
[56] id=0x7ce767deb2b99cb7c95854df13857192e344d891e092f46e4fed748e74186edb  token=AAVE  space=aavedao.eth  date=2024-06-17
TITLE: [TEMP CHECK] Deploy a Lido Aave v3 Instance
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

### Title: [TEMP CHECK] Deploy a Lido Aave v3 Instance 
### Author: ACI (Aave Chan Initiative)
###  Date: 2024-06-10

---

### **Summary**
This proposal suggests supporting the launch of Lido Alliance and deploying an Aave v3 instance focused on the Lido ecosystem.

## **Motivation**

Aave and Lido have historically seen symbiotic growth, with stETH being one of the premier collaterals on Aave and leveraged staking being one of the most profitable use cases for both Aave DAO and Lido users.

Lido is in the process of launching the Lido Alliance, which will reward novel use cases of staked ETH and support further growth of the Lido ecosystem. This TEMP CHECK proposal suggests that Aave support Lido Alliance efforts by deploying a new Aave V3 ETH market for Lido. This Aave v3 instance will be designed and tuned to support stETH leverage loopers. The deployment will only include wstETH and wETH assets with E-Mode enabled.

Lido has committed incentive programs and ecosystem support for this instance in order to bootstrap liquidity and promote additional programs within the Lido Alliance.

They are invited to detail these incentives during the TEMP CHECK or ARFC stages of this proposals

## Specification

The Lido Alliance’s Aave v3 instance will implement the following:

- The borrow cap of wETH will be set to 90% of supplied wETH, with updates tightly controlled by the risk steward. This will ensure that stETH/wETH loops are consistently profitable and can't go into negati

====================================================================================================
[57] id=0x0aced3a8dc2f9fbe3b3f811222ab94fc3721abfe347408f2991f7bc8c5d4df69  token=AAVE  space=aavedao.eth  date=2024-06-19
TITLE: [ARFC] Aave Liquidity Committee Funding Phase III
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Aave Liquidity Committee Funding Phase III  
author: @karpatkey_TokenLogic  
created: 2024-06-11

---

# Summary

This publication proposes funding the Aave Liquidity Committee (ALC) with 600k GHO to continue supporting GHO's liquidity and DeFi integrations over the next three months on Ethereum.

The ALC will be funded by 375,000 ARB on Arbitrum from the LTIPP submission by the @ACI.

# Motivation

As GHO continues to grow on Ethereum, there is an increasing need for deeper liquidity to facilitate greater swap sizes with minimal price impact. Providing a great UX for larger swaps is a prerequisite for enabling more sophisticated and larger DeFi users to transition into GHO.

As GHO expands to other networks, like Arbitrum with others to follow, the ALC aims to develop a liquidity strategy and drive efforts that create utility to support the adoption of GHO on each new deployment.

## Ethereum

### Phase II Update

Over the last three months, the Aave Liquidity Committee has actively supported GHO liquidity across various DEXes and coordinated several key initiatives, leading to improved swap conditions.

Some of the notable achievements are mentioned below:

* GHO trading at peg
* Deeper on-chain DEX liquidity (Increase from 13M to over 32M)
* Borrow Cap increased from 32M to 85M 
* Improved peg resilience
* Both USDC and USDT GSMs are funded
* Cowswap & Paraswap have integrated various GHO liquidity pool types
* Cowswap has integrated both USDC and USDT G

====================================================================================================
[58] id=0xe87a1b1599f705027acdc6794348c04faf1cffb0020b73253fbae0656e199093  token=AAVE  space=aavedao.eth  date=2024-07-01
TITLE: [TEMP CHECK] Onboard dlcBTC to Aave v3 on Ethereum and Arbitrum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

### [TEMP CHECK] Onboard dlcBTC to Aave v3 on Ethereum and Arbitrum 
### Author: Aki Balogh & ACI (Aave Chan Initiative)
###  Date: 2024-06-24

---

### **Simple Summary:**

Proposal to onboard dlcBTC to Aave v3 on the Ethereum and Arbitrum pools.

### **Motivation/Background:**

dlcBTC is a decentralized wrapped Bitcoin on Ethereum, enabling Bitcoin holders to participate in DeFi protocols while retaining full ownership of their assets. It leverages Discreet Log Contracts (DLCs) for secure cross-chain transactions, ensuring trustless and decentralized asset management. dlcBTC is minted by a decentralized set of merchants who lock BTC with themselves (a process we call "self-wrapping"), ensuring self-custody and reducing central points of failure.

Unlike other bridges, dlcBTC merchants "self-wrap" Bitcoin, meaning funds are never sent to an external address, reducing the risk of theft or loss. dlcBTC has a Chainlink proof of reserve feed. See [https://data.chain.link/feeds/arbitrum/mainnet/dlcbtc-por](https://data.chain.link/feeds/arbitrum/mainnet/dlcbtc-por).

**Benefits of listing that token:**

Listing dlcBTC will enable Bitcoin holders to use their assets as collateral within Aave, increasing liquidity and user engagement on the platform. It will attract a broader user base from the Bitcoin community and enhance the diversity of collateral options within Aave. Additionally, it supports DeFi platforms such as Nektar and Swaap, which can generate staking yield using d

====================================================================================================
[59] id=0x9403b7f704ade0d6510591e4846fd85c84b19d134c0814511af914751ecfad5d  token=AAVE  space=aavedao.eth  date=2024-07-02
TITLE: [ARFC]  Deploy a Lido Aave v3 Instance
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## [ARFC]  Deploy a Lido Aave v3 Instance

## Author:  ACI (Aave Chan Initiative)

## Date: 2024-06-24

---

## **Summary**

This proposal suggests joining the Lido Alliance as the Aave DAO and deploying an Aave v3 instance focused on the Lido ecosystem.

## **Motivation**

Aave and Lido have historically seen symbiotic growth, with stETH being one of the premier collaterals on Aave and leveraged staking being one of the most profitable use cases for both Aave DAO and Lido users.

Lido is in the process of launching the Lido Alliance, which will reward novel use cases of staked ETH and support further growth of the Lido ecosystem. This ARFC proposal suggests that Aave supports Lido Alliance efforts by deploying a new Aave V3 ETH market for Lido. This Aave v3 instance will be designed and tuned to support stETH leverage loopers. The deployment will only include wstETH and wETH assets with E-Mode enabled.

Lido has committed incentive programs and ecosystem support for this instance in order to bootstrap liquidity and promote additional programs within the Lido Alliance.

This market will be bootstrapped with wETH from the Ahab program to attract wETH liquidity.

wETH suppliers will also be proposed to be eligible to a dedicated Merit Boost

Incentives from Lido will be detailed ahead of the AIP deployment. 

## Specification

The Lido Alliance’s Aave v3 instance implements the following:

- The borrow cap of wETH will be set to 90% of supplied wETH, with updates tightly contro

====================================================================================================
[60] id=0x19ab2b93680a98f0d5fe4fe8c84c0848a41afc1603454ef2ede6b642db0e0295  token=AAVE  space=aavedao.eth  date=2024-07-03
TITLE: [ARFC-Addendum] Update Boosters for Merit Round 6
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## [ARFC-Addendum] Update Boosters for Merit Round 6

## Author:  ACI (Aave Chan Initiative)

## Date: 2024-07-03

---

## **Summary**

We propose updating Merit parameters and rewarded actions to increase program efficiency and to reflect latest narratives to continue to boost Aave DAO and Merit for Round 6.

### Motivation

The Aave protocol maintained and developed its market share in DeFi in a highly competitive landscape thanks to the Merit program. Latest rounds of Merit have been a success.

Merit aims to maximize efficiency while being conscious of the budget weight of this program, therefore it needs to be updated and adapted when narratives change and new strategies can be applied for future rounds.

wETH supply is key for growth, as it is the biggest revenue source for Aave DAO. wETH is essential for the Aave DAO due to its role in enhancing liquidity, providing collateral, facilitating integrations, and driving user adoption, significantly increasing Aave's revenue through interest income, fees from liquidations, and increased platform usage.

With [**[ARFC] Deploy a Lido Aave v3 Instance**](https://governance.aave.com/t/arfc-deploy-a-lido-aave-v3-instance/18047) being at Snapshot stage, deploying an Aave v3 instance focused on the Lido ecosystem, aiming to support leveraged staking of stETH and wETH, benefiting both Aave and Lido users, it makes sense to align with Merit.

Finally, with **[GHO being launched on Arbitrum](https://avara.xyz/blog/gho-stablecoin-now-

====================================================================================================
[61] id=0x5d4e3fba58f76f516afd0855a687027270b74163911116f14a4f5c01c34a9bd9  token=AAVE  space=aavedao.eth  date=2024-07-08
TITLE: [TEMP CHECK] Aave Events & Sponsorship Grant 2024
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [TEMP CHECK] Aave Events & Sponsorship Grant 2024
Author: Aave Labs
Date: 2024-07-08
---
## Summary
Aave Labs is pleased to announce an event grant proposal. This proposal includes participation in key ecosystem initiatives at EthCC and Devcon among other events.

## Goals
To reinforce Aave Protocol’s unique and positive culture, share technical knowledge, and attract new community members. These initiatives are aimed at helping to continue the expansion of the DeFi ecosystem by showcasing Aave Protocol’s core values.

## Background
Aave Protocol has consistently been at the forefront of DeFi innovation with pioneering features. With a strong emphasis on security, usability, and composability, Aave has amassed a vibrant and engaged community of developers, users, contributors, and stakeholders.

Although the Aave Protocol has emerged as a leader within DeFi, the sector at large is still in its nascent stages, and Aave should work hard to retain its spot as a leader. For the events proposal from the DAO for 2024, Aave Labs wants to concentrate on proposing fewer but higher-quality events to maximize impact. 

## Overview
Aave Labs is requesting a grant for 650,000 GHO for events for the remainder of 2024 for EthCC Brussels (45%) and Devcon Bangkok (55%):
1. **Hackathons & Bounties:** We want to encourage developers to build on Aave Protocol, as well as GHO. These hackathons not only provide a platform for the Aave community to connect with talented developers in bot

====================================================================================================
[62] id=0xc44ec840f8f7f6ca3ef2f2a4289882c4cdc1a8b3e6e9ad6b811a640097a8016a  token=AAVE  space=aavedao.eth  date=2024-07-21
TITLE: [ARFC] TokenLogic + karpatkey Financial Service Providers - Phase II
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
# [ARFC] TokenLogic + karpatkey Financial Service Providers - Phase II

---

Title: [ARFC] TokenLogic + karpatkey - Phase II
Author: TokenLogic karpatkey
Created: 2024-07-16

---

![TL + kpk 2](https://hackmd.io/_uploads/Bkwva6C80.jpg)

# Summary

This publication proposes the continuation of the collaboration with karpatkey and TokenLogic for an additional 6 months, with a proposed budget of 500k GHO. The proposed contributions extend over the three themes detailed below: Treasury Management, GHO adoption and the Aave Stack.

# Motivation

The TokenLogic and karpatkey partnership has created significant value for the Aave DAO across all three focus areas detailed [here](https://governance.aave.com/t/phase-i-summary-karpatkey-tokenlogic/17962). GHO's peg, liquidity, and growth prospects have each improved dramatically over the last 6 months. The DAO's finances are more transparent than ever before and the DAO is firmly positioned for growth.

Building on the success of Phase I, we seek to extend our collaboration with the Aave Community for another 6 months. Phase II of our engagement is to focus on enabling GHO and Aave to grow market share through prudent financial management and contributing to numerous growth initiatives. Our three primary focus areas are summarized below:

* Treasury Management
* GHO Adoption
* Aave Stack


## What to Expect

### Treasury Management

**Asset Management** 

The Aave DAO receives revenue in the form of revenue-generating aTokens for each d

====================================================================================================
[63] id=0xc131152a6521f32bde908f2b602518fbff79b1c601d2ffd11ed463e36bc1655e  token=AAVE  space=aavedao.eth  date=2024-07-21
TITLE: [ARFC] Deploy USDC and USDT GSM On Arbitrum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Deploy USDC and USDT GSM On Arbitrum
author: @karpatkey_TokenLogic
created: 2024-06-30

---

# Summary

This publication proposes deploying a USDC and USDT GHO Stability Module (GSM) on the Arbitrum network. The two GSMs are to be maintained by the GHO Stewards.

# Motivation

The GSM provides stability to the GHO peg by enabling assets to be exchanged within a defined price band. Deploying a GSM on the Arbitrum network enables swaps to be filled without unnecessarily creating an arbitrage opportunity between networks. 

With the LTIPP ARB grant coinciding with GHO being launched on Arbtirum, the Aave DAO can stimulate demand for GHO whilst also restricting the Bridge Facilitator mint cap to encourage users to mint GHO via the GSMs. User will also be able to swap USDC and USDT for GHO via aggregators that have integrated the GSM. This will lead to USDC and USDT being deposited into the GSM.

With a healthy balance of USDC and USDT in each respective GSM, the Bridge Facilitator cap can be raised more aggressively and a GHO Bucket Cap with Facilitor role can be introduced to Aave v3 on Arbitrum. 

# Specification


The below outline the proposed changes to be included in the governance proposal submission.

## Ethereum

### Arbitrum Focused Facilitator

| Parameter  |     Value      | 
|    ---     |     :---:      |
| Mint Cap   |     +2M Units  | 

### CCIP Bucket Capacity Adjustment

| Parameter  |      Value      | 
|    ---     |      :---:      |
| Mint

====================================================================================================
[64] id=0x7f4941aff652cf2a41f47bc58220a952e4894fdc16e27a975045faa9c458da19  token=AAVE  space=aavedao.eth  date=2024-07-30
TITLE: [TEMP CHECK] AAVEnomics update
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---
### [TEMP CHECK] AAVEnomics update
### Author: ACI
###  Date: 2024-07-25
---
### Simple Summary:

This proposal seeks governance feedback and consensus on leveraging the Safety Module Umbrella update to create a clear path and roadmap related to the protocol "fee switch", defined as updated "AAVEnomics".

## Motivation

### Before we start

This proposal leverages the https://governance.aave.com/t/bgd-aave-safety-module-umbrella/18366 proposal, it is strongly advised to read it before diving into the current proposal.
The current proposal has been peer-reviewed by Aave service providers and active Aave DAO community representatives & delegates.

### Introduction

The Aave protocol is the clear market leader in the liquidity vertical and is focused on expanding in both the stablecoin and bridging verticals. The protocol's TVL and net profit growth have largely outpaced market conditions thanks to the coordinated efforts of service providers appointed by DAO governance.
The Aave protocol is also the clear leader on every network Aave has deployed to, and when given a choice, DeFi users leverage Aave over alternatives.
This has allowed the Aave DAO not only to "cover its own bills" but also has built [a large treasury of ETH and stablecoins](https://aave.tokenlogic.xyz/treasury).

 
![treasury.jpeg](ipfs://bafkreihrskqratcejxrmldlzopv4lj42esks3cgel2kugnd3ijzlt4leui)
    

Additionally, during the past couple of quarters, the DAO explored revenue sharing with the Merit progra

====================================================================================================
[65] id=0x15cbc6b6c5b4ef76a1fb8cf8747460bf327c459fa01b69907fab0119457939a8  token=AAVE  space=aavedao.eth  date=2024-08-05
TITLE: [ARFC] Merit Base Incentives and Superfest Matching
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## **[ARFC] Merit Base Incentives and Superfest Matching**

## **Author: ACI**

## **Date: 2024-07-29**

## **Summary**

This ARFC seeks to plan and implement an incentive program on Base with the goal of increasing Aave's market share and matching additional incentives from Optimism foundation. The program will involve the following key actions:

1. Inclusion of Base in Merit boosters for round 7
2. Incentives matching, up to 150k OP, (at max $2 per OP) paid in GHO

These will be in service of the eventual launch of GHO on Base and Umbrella coverage of aUSD and awETH for Aave v3 Base.

## **Motivation**

The primary motivation behind this proposal is to strengthen Aave's position on Base by leveraging incentive programs that can attract more users and liquidity. 

The addition of Superfest incentives and weETH has been a success and push Aave v3 to the largest lending protocol on Base. To continue momentum, this proposal will allocate Merit program incentives as well as additional incentives given by Optimism Foundation. These include incentives from Superfest and Optimism’s Retro Grants Round 4.

Base will be a good network to continue expansion of GHO and the upcoming Umbrella coverage program. By deploying GHO and providing umbrella coverage for key assets, as well as including Base in the Merit program, Aave can capitalize on the growth potential of the Base ecosystem. Additionally, offering matching incentives will help align with Superfest and further drive user engage

====================================================================================================
[66] id=0x9c35c8b1ba5de301650f839c586fc34f6f8908c7a213d9e2a8f3d1d5581db049  token=AAVE  space=aavedao.eth  date=2024-08-06
TITLE: [ARFC-Addendum] Update GHO Dynamics and StkGHO Fast Exit Mechanism
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## [ARFC-Addendum] Update GHO Dynamics and StkGHO Fast Exit Mechanism
## Author: ACI (Aave Chan Initiative)
## Date: 2024-08-05
---
### Simple Summary
We propose to whitelist dedicated service providers GHO to manage "FastPass" and remove the cooldown diluter for the Safety Module.

### Motivation

Following the previously proposed ["FastPass"](https://governance.aave.com/t/temp-check-introducing-fastpass-a-safety-module-update/17376) concept, we've refined our approach to enhance GHO ecosystem efficiency. As GHO has demonstrated stability, maturity, and resilience during its first volatility black swan event, it's time to optimize its staking liquidity. This proposal aims to enhance the efficiency of the StkGHO cooldown by creating a "fast exit mechanism".

This Simple "FastPass" implementation, whitelist dedicated service providers ( @karpatkey_TokenLogic & @ACI) to implement up to 2.5M "buy walls" via Cowswap limit orders at 0.99 GHO per stkGHO to allow StkGHO holders to leave the GHO safety module with a small fee.

FastPass mainteners GHO will be considered as StkGHO in the context of merit and eligible for rewards, to reduce their opportunity costs and incentives their service for the GHO stakers.

As limit orders are filled by the market the service providers are responsible to call cooldown and replenish their fastPass liquidity overtime.

### Specification

1. Whitelist Service Providers for StkGHO Buy Walls:
  * Implement a whitelist service provider addresses mobil

====================================================================================================
[67] id=0xe83b67dfdddd469c298ce6133f4fdb84c9796c671c023b88617d5a25b5933c7f  token=AAVE  space=aavedao.eth  date=2024-08-12
TITLE: [ARFC] Add rsETH to Aave V3 Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
## [ARFC]  Add rsETH to Aave V3 Ethereum

## Author: ACI (Aave Chan Initiative)

## Date: 2024-08-12
---

> ARFC has been updated with Risk Parameters provided by both Risk Service Providers after having reservations with exchange rate oracles. 2024-08-12

### **Summary**

[Kelp DAO](https://www.kelpdao.xyz/) is seeking community support for adding its Liquid Restaking Token, rsETH, to Aave V3 on Ethereum. In addition, rsETH depositors into Aave will accumulate additional [Kelp miles](https://www.kelpdao.xyz/dashboard/) and EigenLayer points.

### **Motivation**

**KelpDAO** (https://www.kelpdao.xyz/restake/) is one of the largest liquid restaking protocol built on top of the Eigen Layer. Restakers on Kelp get access to multiple benefits like restaking rewards, staking rewards and DeFi yields.

**Latest stats**:

- USD 800 Mn+ (~270k Eth) TVL
- 20K+ restakers onboarded
- Accepts ETHx, stETH, sfrxETH, and Native ETH as collateral
- Live across mainnet and L2s such as Arbitrum and Polygon zkEVM

KelpDAO has undergone multiple security audits by top tier audit firms including Sigma Prime, Code4rena. More about KelpDAO’s security here: [Kelp DAO Audit reports](https://kelp.gitbook.io/kelp/audits).

The motivation for this proposal is to introduce a new asset class LRT (Liquid restaking tokens) to Aave and add to the diversity of LST/ LRT category.

**Restaking Innovation**

KelpDAO’s innovation in the restaking ecosystem has been focused on bringing about the following benefits t

====================================================================================================
[68] id=0x2930599cae3cec0a16bd0aef13524347e0c5e85cff7dd66ae9b2bed90fc5d1fe  token=AAVE  space=aavedao.eth  date=2024-08-12
TITLE: [ARFC] Increase WETH Optimal Ratio to 90% on all Aave markets
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
### [ARFC]  Increase WETH Optimal Ratio to 90% on all Aave markets

### **Author: ACI**

### **Date: 2024-08-06**

---

# **Summary**

The current proposal seeks to increase the WETH Optimal Ratio across all Aave markets where it is below 90%. This adjustment aims to enhance capital efficiency and ensure a more effective utilization of liquidity within the Aave protocol.

# **Motivation**

Currently, the optimal usage ratios vary across different Aave instances, reflecting a balance between liquidity utilization and risk management. By increasing the optimal usage ratio for WETH to 90%, higher returns for liquidity providers and improved borrowing conditions for users can be achieved.

# **Specification**

The existing optimal usage ratios for WETH across different markets are as shown in the image below and can also be checked in the Aave dashboard [here](https://dash.onaave.com/). 

 
![weth optimal ratio.jpeg](ipfs://bafkreiherodz64aqwm3oosc5dpymmhplzabnxwkc6sssa46lkrlgxwzhuu)
    


This proposal will increase WETH Optimal Usage Ratio to 90% on the following markets which are currently at 80%, in order to unify them all:

Gnosis V3

Polygon V3

Metis V3

Base V3

Avalanche V3

Scroll V3

# Disclaimer

ACI is not presenting this ARFC on behalf of any third party and is not compensated for creating this ARFC.

# Next Steps

1. If consensus is reached on this [ARFC], escalate this proposal to the Snapshot stage.
2. If the ARFC snapshot outcome is YAE, publish an AIP vote for

====================================================================================================
[69] id=0x4acd11c6100a6b85a553e21359f3720fa5cd4783a76c77857436ace134f88c05  token=AAVE  space=aavedao.eth  date=2024-08-19
TITLE: [ARFC] Deploy an Etherfi/Stablecoin Aave v3 Instance
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
### [ARFC] Deploy an Etherfi/Stablecoin Aave v3 Instance

### **Author: ACI**

### **Date: 2024-07-29**

---

> Risk Parameters have been updated after Risk Service Providers feedback - 2024-08-01
> ARFC has been updated to add pyUSD and FRAX as non-collateral assets - 2024-08-07
> Risk Params updated with pyUSD and FRAX - 2024-08-14
> Due to some technical difficulties with GHO facilitator implementation at this stage, references to GHO and GHO facilitators have been removed. - 2024-08-19

## Summary

This proposal suggests deploying an Aave v3 instance focused on providing liquidity for weETH holders to borrow stablecoins.

## Motivation

The demand for borrowing wETH on Aave using weETH as collateral is extremely high, with caps being filled within minutes each week.

While this $2B growth is welcomed and responsible for ~$12.5M yearly revenue (at current ETH prices) for the DAO, it has created some frustration for significant users looking to borrow stablecoins using their weETH as collateral.

With this asset being constantly at cap, users are wary of leveraging Aave for this use case as they have legitimate concerns about their ability to add more collateral/debt to (de)leverage following market conditions.

To provide weETH holders with more suitable options, we propose creating a dedicated weETH/stablecoin Aave v3 Instance.

This market also lays the groundwork for future integrations & synergies with EtherFi’s Cash product.

## Specification

> *Risk Parameters have

====================================================================================================
[70] id=0x1ea388307b70d30c040f63e8a09d49276c5c8c9ef2fd809809f253654e5f5f06  token=AAVE  space=aavedao.eth  date=2024-09-02
TITLE: [ARFC] Chaos Labs Risk Parameter Updates - Decrease Supply and Borrow Caps on Aave V3 - 08.28.2024
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# Summary

Decrease supply and borrow caps for underutilized stablecoins on Aave V3.

# Motivation

As part of our ongoing strategy to optimize risk management on Aave, this proposal aims to address the low utilization of certain stablecoins by significantly reducing their supply cap and borrow cap values.

We recommend reducing the caps for various stablecoins that have consistently shown low supply and borrow demand over an extended period. All targeted stablecoins have demonstrated an average supply and borrow cap utilization below 15% for the last month. By keeping tighter caps relative to current demand, we aim to protect the protocol from potential risks associated with abnormal or unexpected events. These risks include significant stablecoin depegging and major hacks, which could result in an unexpected surge of risk in the protocol.

Should demand for these stablecoins increase, we can adjust the caps accordingly based on our established supply and borrow cap methodology.

This approach seeks to enhance the protocol's resilience and stability in fluctuating market conditions, protecting the interests of Aave users and stakeholders.

### Notable Low Utilization Stablecoins (crvUSD, LUSD)

There is currently low demand and utilization for crvUSD and LUSD across multiple Aave markets, highlighting a need for reassessment of borrow caps to match the reduced activity:

- crvUSD on Ethereum has a current supply utilization of only 0.85%, which saw spikes up to only 4% in th

====================================================================================================
[71] id=0x82c9a9bb833d869f4b17f405bb0e7b3f8db07c8a3649b948ab8937e7669a0a0c  token=AAVE  space=aavedao.eth  date=2024-09-04
TITLE: [TEMP CHECK] Superlend Profit Share Proposal, Deploying a Friendly Fork of Aave V3 on Etherlink (Stage 2 EVM Rollup) and Arbitrum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
### Title: [TEMP CHECK] Superlend Profit Share Proposal, Deploying a Friendly Fork of Aave V3 on Etherlink (Stage 2 EVM Rollup) and Arbitrum

### Author: @berndoostrum

### Date: 2024-08-28

---

### **Summary**

Superlend is building a lending and borrowing aggregator platform that allows users to manage their positions across multiple chains and protocols, always accessing the best APRs for lending and the lowest rates for borrowing. The Superlend project was Initially conceived during the Etherlink Accelerator in Singapore 2 as a lending and borrowing platform on Etherlink 3.

Our goals include launching our own dedicated money markets using the Aave V3 codebase on Etherlink and Arbitrum, while also integrating Aave V3 markets already deployed by the Aave DAO across the EVM ecosystem, such as on Ethereum, Base, and Polygon, into our aggregator. For the Arbitrum deployment, we are planning to deploy an instance of Aave V3 that will exclusively support ETH and ETH-correlated assets (such as LRTs and LSTs), similar to Aave’s Lido instance on Ethereum. These deployments and integrations will enable users to seamlessly manage their positions within the robust and secure Aave framework, while also allowing Superlend to offer innovative cross-chain liquidity management features. Additional details for the Arbitrum proposal will be provided in the future as we finalize the risk parameters and asset selection. Leveraging Aave’s well-audited and secure infrastructure allows us to ac

====================================================================================================
[72] id=0xea325542397fce607755f6c14be407f60a71a81f3a23c6b3a67e298b9dd8c091  token=AAVE  space=aavedao.eth  date=2024-09-04
TITLE: [ARFC] Orbit Program Renewal - Q3 2024
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
### [ARFC] Orbit Program Renewal - Q3 2024

### **Author: ACI**

### **Date: 2024-08-30**

---


## Summary
Proposing the renewal of the Orbit program for recognized delegates, compensating them with GHO and ETH reimbursement of Gas costs , associated with their governance activity during part of Q3 2024 ( From 2024-05-13 to 2024-08-30).

## Motivation
Orbit recognizes the added value of the Delegates in the decentralization & diversity of the Aave DAO. This compensation allows them to focus on aave and keep their contribution efforts to our governance. The ACI proposes the extension of Orbit for a new quarter, Q3 2024, from 2024-05-13 to 2024-08-30.

**Gas Rebate**:

Initially meant to reimburse gas cost associated with governance voting, the gas rebate has been entirely focused on service provider gas reimbursement since the launch of Aave governance V3, we propose to segregate these payments after this proposal to keep focus and consistency in the Orbit program.

Gas reimbursements from service providers activity are proposed to be managed by Aave Finance service providers in their monthly treasury management update.

## Specification

**Period Coverage: Blocks 19860032 (May 13th 2024) to Block 20639896 (August 30th 2024)**

Eligible Platforms:
EzR3al
StableNode
Saucy Block
Areta

Gas Rebate: Last service provider gas rebate using orbit:
ACI : 2.91 ETH
Catapulta: 0.67 ETH
TokenLogic: 0.72 ETH
Budget: 60000 GHO and 4.3 ETH

## Relevant Links

[Script output](https://aavecha

====================================================================================================
[73] id=0x53f266aa1a322fb3b9299e4a7286be00a24ad73ac25fd93e5b089ba924726acc  token=AAVE  space=aavedao.eth  date=2024-09-04
TITLE: [TEMP CHECK] BUIDL GSM
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---
Title: [TEMP CHECK] BUIDL GSM
Author: @aavelabs
Date: 2024-09-04
---

## Summary
This Temp Check proposes to build and deploy GHO Stability Module (GSM) to support reserve allocation and management features enabling third party integrations, specifically supporting integration into the BlackRock BUIDL 90 infrastructure.

## Motivation
The primary purpose of GHO Stability Module (GSM) is to ensure the stability of GHO in scenarios of increasing or decreasing demand, effectively providing 1:1 convertibility between GHO and the other asset within the specific GSM. In the case of GHO:USDC, this can result in a surplus of USDC that in current deployed implementation remains idle.

Aave Labs proposes to build a new instance of GSM that supports external integrations and related control mechanisms, specifically supporting BlackRock’s BUIDL. With this implementation GSM can be more capital efficient while maintaining the high standards of backing as USDC is backing the GHO.

BUIDL 25 is deployed on the Ethereum network, providing onchain access to traditional financial assets managed by BlackRock Financial Management Inc., with BNY Mellon as custodian, Securitize as transfer agent, and PricewaterhouseCoopers LLP as the appointed fund auditor. BUIDL offers a novel approach to the digital asset space by combining the reliability of traditional financial mechanisms with the efficiency and transparency of blockchain technology.

BlackRock has partnered with Coinbase, Anchorage, Fireb

====================================================================================================
[74] id=0x1d9e4f068704377a7fd4d5089ae6be9d243141f742def95c7a4c0e95770040e4  token=AAVE  space=aavedao.eth  date=2024-09-23
TITLE: [ARFC] Superlend Profit Share Proposal, Deploying a Friendly Fork of Aave V3 on Etherlink (Stage 2 EVM Rollup) and Arbitrum
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
## Author: ACI

## Date: 13/09/2024

# Summary

[Superlend](https://www.superlend.xyz/) is building a lending and borrowing aggregator platform that allows users to manage their positions across multiple chains and protocols, always accessing the best APRs for lending and the lowest rates for borrowing. The Superlend project was Initially conceived during the [Etherlink Accelerator in Singapore](https://medium.com/etherlink/the-future-of-defi-insights-from-dca-in-singapore-d543477cdbe6) as a lending and borrowing platform on [Etherlink](https://www.etherlink.com/).

Superlend's goals include launching their own dedicated money markets using the Aave V3 codebase on Etherlink and Arbitrum, while also integrating Aave V3 markets already deployed by the Aave DAO across the EVM ecosystem, such as on Ethereum, Base, and Polygon, into their aggregator. For the Arbitrum deployment, they are planning to deploy an instance of Aave V3 that will exclusively support ETH and ETH-correlated assets (such as LRTs and LSTs), similar to Aave's Lido instance on Ethereum. These deployments and integrations will enable users to seamlessly manage their positions within the robust and secure Aave framework, while also allowing Superlend to offer innovative cross-chain liquidity management features. Additional details for the Arbitrum proposal will be provided in the future as they finalize the risk parameters and asset selection. Leveraging Aave's well-audited and secure infrastructure allows them t

====================================================================================================
[75] id=0x15f4abf4403c413fb01d2f42b6401327e34fa997d01e1946093d2c6015f6c5b1  token=AAVE  space=aavedao.eth  date=2024-09-23
TITLE: [TEMP CHECK] USTB/BUIDL GSM
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
**Author:** Superstate Inc. – @fig  
**Date:** 09-12-2024

## Summary

This Temp Check proposes expanding the BUIDL GHO Stability Module (GSM) to incorporate Superstate's USTB. The proposal recommends a 50:50 split between BUIDL and USTB to help increase GHO's stability with diverse reserves and maximized yield.

## Motivation

This proposal aims to introduce an additional industry-leading tokenized U.S. Treasury Bill product to support the stability and efficiency of GHO while maximizing protocol revenue. Superstate recommends expanding the proposed BUIDL GSM instance to include USTB to diversify GHO's reserves, RWA yield sources, and foster a resilient and scalable GSM. Adding USTB to this instance will enhance the GSM's capital efficiency, while also maximizing transparency, liquidity, and yield.

USTB offers competitive benefits for the Aave ecosystem, bolstering GHO's stability and generating surplus revenue for Aave. Currently, management fees are waived (0.00%) while USTB is under $200M AUM. Once this is surpassed, the management fee is 0.15% for any client balance up to $25M. Aave will benefit from a 67% discount on management fees (0.05%) for any assets above $25M. Furthermore, USTB provides transparent daily Net Asset Value via a Chainlink oracle with a separate Proof of Reserves Chainlink oracle coming soon. USTB's website publishes holdings weekly with daily NAV, AUM, and yield available for anyone to see. You can visit https://superstate.co/ustb.

USTB is deploye

====================================================================================================
[76] id=0x72ebea577b94b545aa2d4dfd4b896e4144c92da0d9068f92e906be3edd043bdd  token=AAVE  space=aavedao.eth  date=2024-09-24
TITLE: [TEMP CHECK] Add support for Wrapped OETH (wOETH) to Aave v3
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
Author: Peter from the Origin Protocol core team
Date: 2024-09-18

### 1. Simple Summary

This is a proposal for adding supply/borrow support for wOETH on:

- Aave v3 Main Ethereum Instance

If the onboarding of OETH to Aave is successful, Origin hopes to discuss an additional onboarding of wOETH to:

- Aave v3 Lido Instance
- Aave v3 EtherFi Instance

### 2. Motivation/Background

[Origin Ether](https://oeth.com/)(OETH) was launched in May 2023 and is an ERC20 that generates yield while sitting in your wallet. Similar to stETH, OETH yield is paid out daily and automatically (sometimes multiple times per day) through a positive rebase in the form of additional OETH, proportional to the amount of OETH held.

Until a [proposal](https://snapshot.org/#/ousdgov.eth/proposal/0x76f64251d37310c5d241ec84a892751c7a34874faff7af848db193141ea24a6f) earlier this year, OETH was an LST aggregator that earned yield by tapping into blue-chip protocols while being collateralized by other LSTs. Over the weeks following, the ability to deploy OETH collateral to other projects was removed and LST collateral was divested back to ETH, as OETH transitioned into a full-fledged LST with an extremely tight peg (1:1 redemptions to ETH thru Origin's [ARM](https://www.originprotocol.com/arm-announcement)) and high yields thanks to DVT direct staking through SSV/P2p.

We've noticed many LSTs trade below their peg due to DEX fees and slippage, and to reflect the time value of money. LSTs that consistently tr

====================================================================================================
[77] id=0xb800d3ab766305fd57389101bc475f0220a8bd47699b0f850eec115f31ca22ee  token=AAVE  space=aavedao.eth  date=2024-10-03
TITLE: [TEMP CHECK] Deploy aUSDC GSM on Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Deploy aUSDC GSM on Ethereum
author: @karpatkey_TokenLogic
created: 2024-09-27

---

# Summary

This TEMP CHECK proposes creating a more capital efficient aToken GHO Stability Modules (GSM) to replace the USDC GSM on Ethereum.

# Motivation

Whilst the primary focus of the GSM is to ensure price stability during periods of price fluctuation. The current instance of the GSMs issue GHO into circulating supply and offer no additional revenue beyond the fee for interacting with the GSM. To date, both GSMs have generated a combined 21.9K USD in fees. 
  
![image](ipfs://bafkreidxpse554hufcrksjc2you63l3abqnublk4h4cyg6inwdsquvomdy)
    
With only 16M of combined USDC and USDT in the GSMs, the opportunity cost of holding aTokens in the GSM to date is 138.5k for the Aave DAO. However, during more recent times when GHO has been trading above peg and both GSMs have reached there Exposure Caps, the daily opportunity cost in lost yield is ~1.6k, which is equivalent to ~575k when annualised.

![image](ipfs://bafkreifay4gngo2u65tapm7brryjh22qrrt7smxbitkqlj6sjl7ezxrnma)
    
The proposed GSMs will enable funds held within the GSM to earn yield and for this yield to go the DAO's treasury. Due to the enhanced capital efficiency, the USDC Exposure and GHO Bucket Capacity of the GSM can be sized based upon the lesser of the following:

* Preferred amount of USDC exposure; or,
* Available exit liquidity in the USDC reserve.

Either of the above options, compares favourabl

====================================================================================================
[78] id=0x3c8116f97f990bf61fe63c636c1ae85630ad355e26881285aa4fefaebd8c9c0d  token=AAVE  space=aavedao.eth  date=2024-10-10
TITLE: [ARFC] Renew LlamaRisk as Risk Service Provider
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
## **Author: LlamaRisk**

## **Date: 2024-10-02**

---

## Summary

We'll keep this short. When we [initially applied](https://governance.aave.com/t/temp-check-onboard-llamarisk-as-aave-risk-service-provider) to serve Aave as a risk service provider, our primary goal was to deliver complementary and collaborative work alongside @ChaosLabs, focusing on qualitative analysis, ad hoc research, and legal/regulatory advisory.

Five months later, we are confident that we have fulfilled this commitment, a sentiment that numerous delegates and service providers have echoed. Our work has made a significant impact on safely integrating newly onboarded assets, and we have fostered a great relationship with @ChaosLabs, holding regular meetings, aligning internally, and driving informed decisions. We place high importance on furthering the common mission of all Aave service providers to promote sustainable growth of the protocol, and to that end we have engaged in collaborations and taken steps to join task forces with numerous ecosystem teams.

Although most of our work is publicly available through [monthly community updates](https://governance.aave.com/t/llamarisk-monthly-community-update/), we have made several positive contributions behind the scenes. These include advocating for bug bounty programs, improved access controls, and increased transparency for end users. A good example of such activity is our work behind the scenes on WBTC to ensure sensible and compliant steps in its cus

====================================================================================================
[79] id=0x03dc21e0423c60082dc23317af6ebaf997610cbc2cbb0f5a385653bd99a524fe  token=AAVE  space=aavedao.eth  date=2024-10-14
TITLE: [ARFC] Launch GHO on Base & set ACI as Emissions Manager for rewards
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: ACI

## Date: 2024-10-07

----------
> ARFC has been updated with latest Risk Parameters provided by Risk Service Providers. 2024-10-11

---

# **Summary**

This proposal aims to launch GHO on Base & set ACI as Emissions Manager for GHO and aGHO potential rewards and incentives.

# **Motivation**

With a dedicated portion of GHO supply moving to the Arbitrum network and the generous grant from the Arbitrum DAO as part of the LTIPP, Aave DAO successfully bootstrapped GHO liquidity both within the Aave protocol and throughout the Arbitrum ecosystem.

Building on this success, it is now time to expand GHO to other networks. However, the lessons learned from the Arbitrum launch highlight the importance of coordinated efforts in several key areas:

- Implementing the necessary smart contracts and infrastructure to support GHO on the  network
- Establishing appropriate risk parameters and collateral requirements specific to the Base ecosystem
- Integrating GHO with existing DeFi protocols and applications on Base to foster immediate utility
- Collaborating with the community to ensure a smooth launch and widespread adoption

These factors underscore the significant effort required from all service providers to create a successful launch. This ARFC vote seeks community approval to proceed with the launch of GHO on Base.

# **Specification**

The ACI invites all service providers to provide input on their scopes within this proposal. 

The proposed launch of GHO on Base wi

====================================================================================================
[80] id=0x2aed7eb8b03cb3f961cbf790bf2e2e1e449f841a4ad8bdbcdd223bb6ac69e719  token=AAVE  space=aavedao.eth  date=2024-10-14
TITLE: [ARFC] Launch GHO on Avalanche & set ACI as Emissions Manager for rewards
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: ACI

## Date: 2024-10-07

----------
> ARFC has been updated with latest Risk Parameters provided by Risk Service Providers. 2024-10-11

---


# **Summary**

This proposal aims to launch GHO on Avalanche and set ACI as Emissions Manager for GHO and aGHO potential rewards and incentives.

# **Motivation**

With a dedicated portion of GHO supply moving to the Arbitrum network and the generous grant from the Arbitrum DAO as part of the LTIPP, Aave DAO successfully bootstrapped GHO liquidity both within the Aave protocol and throughout the Arbitrum ecosystem.

Building on this success, it is now time to expand GHO to other networks. However, the lessons learned from the Arbitrum launch highlight the importance of coordinated efforts in several key areas:

- Implementing the necessary smart contracts and infrastructure to support GHO on the  network
- Establishing appropriate risk parameters and collateral requirements specific to the Avalanche ecosystem
- Integrating GHO with existing DeFi protocols and applications on Avalanche to foster immediate utility
- Collaborating with the community to ensure a smooth launch and widespread adoption

These factors underscore the significant effort required from all service providers to create a successful launch. This ARFC vote seeks community approval to proceed with the launch of GHO on Avalanche.

# **Specification**

The ACI invites all service providers to provide input on their scopes within this proposal. 

The proposed l

====================================================================================================
[81] id=0x9bc3f3d8e38d70f55887f2f2498e1b39f59467489158923488aceab73cd4f144  token=AAVE  space=aavedao.eth  date=2024-10-14
TITLE: [ARFC] Remove Frax from Isolation Mode on Aave v3 Mainnet
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: ACI

## Date: 2024-10-07

----------
> ARFC has been updated with latest Risk Parameters provided by Risk Service Providers. 2024-10-14
---
## **Summary**

This is an ARFC to remove FRAX from isolation mode, and set LTV to 0%. This is a reboot with minor changes of a [previous ARFC](https://governance.aave.com/t/arfc-remove-frax-from-isolation-mode-and-onboard-sfrax-to-aave-v3-mainnet/18506) which passed Snapshot but has not yet been implemented.

## **Motivation**

FRAX and Aave DAO have found more synergies over the last months. The FRAX team has responded with major updates to security on sfrxETH in response to BGD Labs feedback. FRAX has also initated governance proposals to add GHO to Frax Lend. There are ongoing conversations to have a FRAX AMO included into Aave v3. sFRAX was [previously accepted](https://governance.aave.com/t/arfc-add-sfrax-on-ethereum-v3/16303) for onboarding in a previous [ARFC vote](https://snapshot.org/#/aave.eth/proposal/0xdba99e9c8da24424447d7c7b70eff93ad5b6055714b5f34cf9859c923fb3a38a) before the introduction of CAPO feeds. 

This proposal suggests removing FRAX from isolation mode to facilitate further AMO deployments. 

Furthermore, this proposal sets LTV to 0% as there is no use-case for FRAX to act as collateral.

## Specification

- FRAX will be removed from Isolation Mode on Aave v3 instances.
- FRAX will receive same parameters as DAI, a Reserve Factor as other stables, and LTV of 0%.


 Parameter | Recommendation |
| --- | --

====================================================================================================
[82] id=0xf18b0bd1a2864436cc424e48c331783b8ea65eba0b72c77016c5719fab8074d4  token=AAVE  space=aavedao.eth  date=2024-10-17
TITLE: [TEMP CHECK] World Liberty Financial Aave v3 Instance on Ethereum Mainnet Proposal
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: WorldLibertyFi

## Date: 2024-10-08

----------

## Summary
This proposal suggests deploying a World Liberty Financial Aave v3 instance focused on:

1. Providing stablecoin liquidity for ETH and WBTC
2. Growing the Aave protocol user base

This proposal is subject to both AaveDAO governance approval and World Liberty Financial community approval.

## Motivation and Value Proposition for Aave Protocol and DAO

World Liberty Financial ("WLF") is a nascent DeFi protocol that will use Aave v3 to provide liquidity for Ethereum, Wrapped Bitcoin, stablecoins, and potentially other digital assets, as determined by WLF governance. WLF intends to:

* Promote DeFi to a wider audience through its marketing efforts
* Introduce a new class of users to over-collateralized borrowing and lending
* Onboard new users into DeFi by providing seamless user experiences for supplying and borrowing against digital assets

### Benefits for Aave

* Bring a significant number of new users and new liquidity to Aave
* Build brand loyalty and recognition among first-time DeFi users
* Help maintain Aave's position as a market leader in digital asset borrowing and supply

### Proposal Details

1. Initially, WLF's Aave v3 instance will allow USDC, USDT, ETH, and WBTC deposits
2. Users can deposit these assets as collateral and borrow the same assets
3. WLF will utilize the same reserve factor system as the main Aave instance
4. AaveDAO will receive:

  * 20% of the protocol fees generated by the WL

====================================================================================================
[83] id=0xc16cfd8f6da91d8e16de9722c5ed4f0b81d038a3e3f676a1d96327e22fb1ecd9  token=AAVE  space=aavedao.eth  date=2024-10-25
TITLE: [ARFC] Launch aUSDC GSM on Ethereum
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Launch aUSDC GSM on Ethereum
author: @karpatkey_TokenLogic
created: 2024-10-18

---

# Summary

This publication proposes deploying a new aUSDC GHO Stability Module (GSM) and migrating USDC from the existing GSM on Ethereum.

# Motivation

After a successful [TEMP CHECK](https://snapshot.org/#/aave.eth/proposal/0xb800d3ab766305fd57389101bc475f0220a8bd47699b0f850eec115f31ca22ee), the existing USDC GSM is to be replaced with an aUSDC GSM. Migrating to an aUSDC GSM is expected to improve the overall investment prospects of GHO by introducing a new aToken revenue stream for the DAO. 

![Screenshot 2024-10-15 at 19.56.00](https://hackmd.io/_uploads/H1H0cN3J1g.png)

With 8M of USDC from the existing GSM deposited into Aave v3, it would represent less than 10% of the available liquidity in the USDC Reserve. With sufficient growth upside remaining for the aUSDC GSM on Ethereum, the DAO can increase the amount of USDC backing GHO. In addition, separate instances of non USDC aToken GSMs can be deployed to diversify GHO's collateral across other reserves on Aave.

![Screenshot 2024-10-15 at 19.22.47](https://hackmd.io/_uploads/ByubX43kkx.png)

The existing GSM implementation has USDC exposure capacity set at 8M units. When combined with another 8M of USDT, this represents over 10% of GHO's supply not generating any revenue for the DAO. The GHO Stewards elected to not pursue increasing the Exposure Capacity of USDC and USDT to encourage new GHO entering circulating sup

====================================================================================================
[84] id=0xcd73f17361c7757cd94ec758b4d9f160b7cecefa7f4cb23b0b4ee49b5eb1b8b2  token=AAVE  space=aavedao.eth  date=2024-10-29
TITLE: [ARFC] PYUSD Reserve Configuration Update & Incentive Campaign
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] PYUSD Reserve Configuration Update & Incentive Campaign
author: @karpatkey_TokenLogic
created: 2024-10-23

---

# Summary

This publication proposes amendments to the PYUSD Reserve in preparation for an upcoming incentive campaign.

Additionally, a co-incentive campaign is to be implemented to improve the PYUSD and GHO liquidity.

# Motivation

Trident Digital with support from PayPal, presents the Aave DAO with an opportunity to promote the adoption of PYUSD on Aave Protocol and PYUSD/GHO liquidity on Balancer for an initial 6 month period.

Eligible Aave Protocol users are expected to receive up to 4.00% APR in Liquidity Mining (LM) rewards made available by Trident Digital on behalf of PayPal.

The incentive program seeks to increase PYUSD deposits into Aave Protocol, targeting total deposits of 75M units. After achieving 75M units of aEthPYUSD circulating supply, the rewards budget is to be distributed pro-rata. 

To prevent undesired rewards farming, an eligibility requirement is to be applied to discourage undesired behaviour. 

Rewards are to be distributed as aEthPYUSD on a monthly basis via a merkle contract administered by the ACI team.

## PYUSD Rewards

PYUSD rewards are to be distributed at a fixed rate of 4.00% to eligible user on Aave v3 on Ethereum up to a threshold of 75M aEthPYUSD. After this threshold is achieved, rewards are to be distributed pro-rata to eligible users. 

Eligible users can expect to earn the following rewards:

* Deposi

====================================================================================================
[85] id=0x353c9f870389ffd8576097355bc3d3ccf90cb290e311cf0b5556cce68f0a7684  token=AAVE  space=aavedao.eth  date=2024-11-04
TITLE: [TEMP CHECK] Deploy GHO Facilitator
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [TEMP CHECK] Deploy GHO Facilitator
author: @karpatkey_TokenLogic
created: 2024-10-29

---

# Summary

This publication proposes creating a Facilitator entity on Ethereum to support GHO's expansion across several decentralised applications on various networks.

This proposal also includes the first integration, a 5M GHO deposit into Aave v3 on Arbitrum. Future proposals shall outline how and where GHO shall be deployed. 

# Motivation

GHO was successfully launched on Arbitrum July 2nd 2024 with only the CCIP Bridge Facilitator on Arbitrum. Since then, growth has stalled with around 3% of GHO's supply located on Arbitrum.

This publication proposes creating a new Facilitator entity on Ethereum for the purpose of onboarding newly minted GHO to various applications on Ethereum, Arbitrum, Base, Avalanche and other networks as GHO expands. 

Using Aave v3 on Arbitrum as an example, the below provides a high level overview of the flow:

* GHO is Minted on Ethereum;
* Transferred to Arbitrum via the CCIP bridge; and,
* GHO is deposited into Aave v3 on Arbitrum.

The facilitator will enable Aave DAO to onboard new GHO demand vectors while segregating risk from the existing Ethereum facilitator.

The new facilitator role will have independent minting and bucket capacity constraints specific to supporting each proposed integration.

Collateralization of minted GHO will depend on the different use-cases and takes place on the respective dApp when users bring GHO into the ci

====================================================================================================
[86] id=0x77d0f79418b1c9ea3560154f4650372470a9e3da12c3a5ca3ca3d565f1112c5a  token=AAVE  space=aavedao.eth  date=2024-11-06
TITLE: [ARFC] Framework for Instances and Friendly Forks
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Author: ACI

## Date: 2024-11-01

---

## **Motivation**

Table 1 shows a large variation in terms of historical friendly fork proposals. We propose that terms for friendly forks are formalised to ensure fair and transparent treatment of teams wishing to make use of licensed Aave instances in the future.

**Table 1** - Licensed instances and benefits to Aave

| **Partner** | **Profit share for Aave** | **Token supply to Aave** |
| --- | --- | --- |
| WLFi | 20% | 7% |
| Spark | 10% | None |
| Superlend | 15% of quarterly revenues over $200k | Unconfirmed amount of tokens airdropped to stkAAVE holders |
| Zerolend | 10% for first year | 1% to stkAAVE holders |
| RealT | 20% | None |
| Reental | 20% | None |

It should be noted in the above that two particularly strategic outliers are present in WLFi and Spark. Spark represented a significant revenue opportunity for Aave DAO, with $2m per year projected revenue at the time of proposal. This could go some way to explaining the profit share being at the lower bound of previous forks. With WLFi, the terms are at the higher end of the range, although it should be noted that this is not an entirely separate fork of Aave and will make use of Aave liquidity, and tokens will in part be distributed as rewards to users.

Two other outliers representing not as good value for Aave DAO are the Zerolend, and Superlend forks. It should be noted that the Zerolend proposal was rejected by governance for being too low a profit share. With Zer

====================================================================================================
[87] id=0xa8b329bbbbc4471e68590e55216b82c2eaffafbe378be8e1ba4c2f431120fc39  token=AAVE  space=aavedao.eth  date=2024-11-25
TITLE: [TEMP CHECK] Aave x Metis: Strategic Alignment Initiative
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: @ACI
## Date: 2024-11-19

---

### Summary

We propose a strategic partnership between Metis and Aave to create a mutually beneficial, long-term collaboration that will drive competitive advantage and enhance user experience.

### Objectives

1. Establish Metis as a preferred chain for Aave users
2. Create a sustainable funding model for Aave markets on Metis
3. Leverage Aave service providers' expertise for optimal token allocation
4. Support key Aave initiatives, including GHO proliferation

### Implementation Strategy

### Perpetual Funding Stream

We propose delegating the remaining Metis tokens reserved for Aave emissions to an Aave sequencer. This approach offers several advantages:

- Sustainable Incentives: Creates an indefinite drip of emissions, ensuring long-term user retention
- TVL Stability: Prevents potential TVL decrease after grant depletion
- User Retention: Maintains competitive yields, discouraging users from migrating to other chains

### Collaboration with Aave Service Providers

By partnering with expert service providers such as BGD, ACI, Chaos, and Llama Risk, we can:

- Optimize token allocation and emission management
- Align with Aave's strategic objectives
- Develop tailored solutions for the Metis ecosystem

### GHO Integration

With CCIP enabled on Metis, we are well-positioned to support GHO proliferation:

- Develop Metis-specific use cases for GHO
- Contribute to GHO's adoption and utility within the broader DeFi ecosystem
- Expand

====================================================================================================
[88] id=0x8fdee3ec7a301f9fba2e4c048227257070645d636b09a7afb369ee9c002ad764  token=AAVE  space=aavedao.eth  date=2024-12-06
TITLE: [TEMP CHECK] Onboard & Enable LBTC/WBTC liquid E-Mode on Aave v3 Core Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: @ACI
## Date: 2024-11-28

---


# **Summary**

This proposal aims to onboard and enable LBTC/WBTC (Lombard) liquid E-Mode for the Main Instance. By implementing this change, we seek to enhance capital efficiency for borrowers using LBTC/WBTC as collateral.

# **Motivation**

The motivation behind this proposal stems from several key factors:

- High Utilization: LBTC/WBTC has demonstrated significant usage as collateral for borrowing stablecoins on other platforms.
- Capital Efficiency: Enabling liquid E-Mode for LBTC/WBTC will allow borrowers to substantially improve their capital efficiency when using this asset as collateral.
- Controlled Growth: Liquid E-Mode provides a mechanism for more precise control over the growth and borrow demand in relation to the overall stablecoin liquidity within Aave v3 on Core Instance.

By implementing this proposal, we aim to optimize the use of LBTC/WBTC within the Aave ecosystem, attracting more liquidity for the protocol and increasing revenues.

# **Specification**

This proposal will add LBTC/WBTC liquid E-Mode. Risk Parameters will be provided by Risk Service Providers and ARFC will be updated accordingly when ARFC is posted if it passes this TEMP CHECK.

## Useful links

[**BGD. Aave v3.2: Liquid Emodes**](https://governance.aave.com/t/bgd-aave-v3-2-liquid-emodes/19037) 

[**ARFC Snapshot**](https://snapshot.org/#/aave.eth/proposal/0x68ce69b5e71df1d77c2ad814a5d41162a40be54473576ff590d0b1bb5afde4a7)

[**Github**](https://g

====================================================================================================
[89] id=0xe6740e5aec256ccf1dfbf538591f6b1631927f8d950b17067fe6912b74158332  token=AAVE  space=aavedao.eth  date=2024-12-08
TITLE: [ARFC] Aave Liquidity Committee Funding Phase V
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] Aave Liquidity Committee Funding Phase V
author: @karpatkey_TokenLogic
created: 2024-12-03

---

# Summary

This publication presents the Aave Liquidity Committee (ALC) Phase V request. 

# Phase IV Update

Buoyant market conditions in November drove strong demand for stablecoin debt that resulted in the composition of DEX liquidity pools being increasingly concentrated in GHO, and outflows from the the GSMs. Three small Borrow Rate increases were implemented with minimal effect and ultimately GHO's peg began showing signs of stress from November 12th up until the 1st December.

From late October to early November, GHO's debt continued to expand leading to a noticeable shift in the composition of the Balancer 3pool liquidity pool in favour of GHO. A few days later, the GSMs started experiencing outflows resulting in GHO being burnt and USDC plus USDT reserves being distributing.

Note: The composition of the Balancer 3pool started shifting on October 28th, prior to the GSM experiencing outflows on the 3rd November and eight days before the Curve NP Pool's composition began favouring GHO. This is due to the high amp in the 3pool and the current the fees configuration on the GSMs. 

![Screenshot 2024-12-01 at 13.29.01](https://hackmd.io/_uploads/HJehNJcQkg.png)
Source: https://aave.tokenlogic.xyz/liquidity-pools

Between the 4th to 10th November, ~16M units of GHO were burned and all but small amount of the 8M units of USDC and 8M units of USDT remain in the

====================================================================================================
[90] id=0x78c3bbbeb6ed3d33f66d5ee7049f4d79bbd4744869f83ee091a5d3390f9964f7  token=AAVE  space=aavedao.eth  date=2024-12-16
TITLE: [ARFC] World Liberty Financial Aave v3 Instance on Ethereum Mainnet Proposal
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Date: 2024-11-06

## Author: WLFI

## Summary

This proposal suggests deploying a World Liberty Financial Aave v3 instance focused on:

1. Providing stablecoin liquidity for ETH and WBTC
2. Growing the Aave protocol user base

This proposal is subject to both AaveDAO governance approval and World Liberty Financial community approval.

## Motivation and Value Proposition for Aave Protocol and DAO

World Liberty Financial (“WLF”) is a nascent DeFi protocol that will use Aave v3 to provide liquidity for Ethereum, Wrapped Bitcoin, stablecoins, and potentially other digital assets, as determined by WLF governance. WLF intends to:

* Promote DeFi to a wider audience through its marketing efforts
* Introduce a new class of users to over-collateralized borrowing and lending
* Onboard new users into DeFi by providing seamless user experiences for supplying and borrowing against digital assets

### Benefits for Aave

* Bring a significant number of new users and new liquidity to Aave
* Build brand loyalty and recognition among first-time DeFi users
* Help maintain Aave’s position as a market leader in digital asset borrowing and supply

### Proposal Details

1. Initially, WLF’s Aave v3 instance will allow USDC, USDT, ETH, and WBTC deposits
2. Users can deposit these assets as collateral and borrow the same assets
3. WLF will utilize the same reserve factor system as the main Aave instance
4. AaveDAO will receive:

* 20% of the protocol fees generated by the WLF Aave v3 instance
* Ap

====================================================================================================
[91] id=0xd1fdca5d69b03ed57848180d62a812ab1a1ff72f85d671c417b5ff8fb2bd0a7c  token=AAVE  space=aavedao.eth  date=2024-12-18
TITLE: [ARFC] TokenLogic Financial Services Provider
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
![IMG_4368](https://hackmd.io/_uploads/rkHeXxqNkg.png)

# Summary

TokenLogic proposes to renew our engagement with the Aave DAO  for 1 year from the 15th December 2024 when our current stream ends.

TokenLogic is to provide the following services to the DAO. 

- Treasury and Runway Management;
- Analytics and Performance Metrics;
- GHO's growth across DeFi and CeFi; and,
- Support Aave protocol parameter optimisation.

# Motivation

## What to Expect

### Treasury and Runway Management

**Asset Management & Financial Security**

A central area of focus for the Finance Services Provider is to ensure that the DAO’s expenses and strategic initiatives are funded efficiently and without delay. Through the Steward role, or the standard governance process when required, TokenLogic will prioritize maintaining the DAO’s financial stability by ensuring a runway that exceeds six months of its burn rate while optimizing capital efficiency.

Key components of this objective include:

* Bridging Aave funds across networks;
* Providing AAVE & GHO Protocol-Owned-Liquidity (POL);
* Allocating assets for capital efficiency, integrating yield bearing assets to the treasury;
* Migrating funds from Aave v2 to Aave v3, and between Aave v3 markets;
* Swapping assets to align expenses with holdings.

### Analytics and Performance metrics

TokenLogic is establishing itself as the definitive hub for all Aave Protocol and GHO-related data via the [Aave Portal](https://aave.tokenlogic.xyz/). This initi

====================================================================================================
[92] id=0x61f027ea797763c9e01736693570141a27a0a5d4517a6b63d0fd84474e8be995  token=AAVE  space=aavedao.eth  date=2024-12-19
TITLE: [ARFC] Enable LBTC/WBTC liquid E-Mode on Aave v3 Core Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC] Enable LBTC/WBTC liquid E-Mode on Aave v3 Core Instance

## Author: ACI ( Aave Chan Initiative)

## Date: 2024-12-10

> ARFC has been updated 2024-12-19 with latest Risk Parameters provided by Risk Service Providers.

---

# **Summary**

This proposal aims to enable LBTC/WBTC liquid E-Mode for the Main Instance. By implementing this change, we seek to enhance capital efficiency for borrowers using LBTC/WBTC as collateral.

[TEMP CHECK](https://governance.aave.com/t/temp-check-onboard-enable-lbtc-wbtc-liquid-e-mode-on-aave-v3-core-instance/19968/7) and [TEMP CHECK Snapshot](https://snapshot.box/#/s:aave.eth/proposal/0x8fdee3ec7a301f9fba2e4c048227257070645d636b09a7afb369ee9c002ad764) have passed recently.

# **Motivation**

The motivation behind this proposal stems from several key factors:

- High Utilization: LBTC/WBTC has demonstrated significant usage as collateral for borrowing stablecoins on other platforms.
- Capital Efficiency: Enabling liquid E-Mode for LBTC/WBTC will allow borrowers to substantially improve their capital efficiency when using this asset as collateral.
- Controlled Growth: Liquid E-Mode provides a mechanism for more precise control over the growth and borrow demand in relation to the overall stablecoin liquidity within Aave v3 on Core Instance.

By implementing this proposal, we aim to optimize the use of LBTC/WBTC within the Aave ecosystem, attracting more liquidity for the protocol and increasing revenues.

# **Specification**

This proposa

====================================================================================================
[93] id=0x564a45f0a2855799d9be329942fa1f5e849058ff4b950f4027ec4666f4b61d9c  token=AAVE  space=aavedao.eth  date=2024-12-19
TITLE: [ARFC] Enable eBTC/WBTC liquid E-Mode on Aave v3 Core Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC] Enable eBTC/WBTC liquid E-Mode on Aave v3 Core Instance

## Author: ACI ( Aave Chan Initiative)

## Date: 2024-12-10

> ARFC updated 2024-12-19 with latest Risk Parameters provided by Risk Service Providers.

---

# **Summary**

This proposal aims to enable eBTC/WBTC (Etherfi) liquid E-Mode for the Core Instance. By implementing this change, we seek to enhance capital efficiency for borrowers using eBTC/WBTC as collateral.

Both [TEMP CHECK](https://governance.aave.com/t/temp-check-onboard-enable-ebtc-wbtc-liquid-e-mode-on-aave-v3-core-instance/19969) and [TEMP CHECK Snapshot](https://snapshot.box/#/s:aave.eth/proposal/0x60c360b61812b9ae96b2f785f9fca7a5461ab45e295f55a695638aef18d96d50) have passed recently.

# **Motivation**

The motivation behind this proposal stems from several key factors:

- High Utilization: eBTC/WBTC has demonstrated significant usage as collateral for borrowing stablecoins on the platform.
- Capital Efficiency: Enabling liquid E-Mode for eBTC/WBTC will allow borrowers to substantially improve their capital efficiency when using this asset as collateral.
- Controlled Growth: Liquid E-Mode provides a mechanism for more precise control over the growth and borrow demand in relation to the overall stablecoin liquidity within Aave v3 on Core Instance.
- Enhanced Borrowing Capacity: This change will enable users to borrow larger amounts of other stablecoins against their eBTC/WBTC collateral, potentially increasing platform utilization and revenue.

====================================================================================================
[94] id=0x2e93ddd01ba5ec415b0962907b7c65def947d1ed94f1e5b402c5578560b1dddb  token=AAVE  space=aavedao.eth  date=2024-12-24
TITLE: [ARFC] Aave v3 Gnosis Instance Updates
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
> Proposal edited to include Risk Providers feedback

## [ARFC] Aave v3 Gnosis Instance Updates

## Author: [@ACI](https://governance.aave.com/u/aci)

## Date: 2024-12-20

---

## Summary

This ARFC proposes several updates to the Aave v3 Gnosis instance to improve capital efficiency and add new use cases on the network. The key changes include removing GNO from isolation mode, adjusting the reserve factor for EURe, onboarding osGNO, making sDAI borrowable, and creating new relevant E-modes.

## Motivation

GNO has demonstrated strong stability and market presence on Gnosis Chain, making isolation mode unnecessarily restrictive and hindering network growth. Removing GNO from isolation mode will facilitate further expansion of the network.

The reduction in the EURe reserve factor aligns with the asset's performance and incentivizes increased lending activity.

The introduction of osGNO adds utility for GNO holders within the protocol and enables looping strategies using osGNO as collateral to borrow GNO. Leveraged staking use cases have been a key growth driver for Aave DAO, and enabling this on Gnosis Chain is expected to gain similar traction.

Making sDAI borrowable and introducing new E-modes will enhance capital efficiency and foster synergies between stable assets. The unique combination of EUR and USD borrowing opportunities is a distinct advantage for Gnosis Chain.

sDAI, as an asset with intrinsic yield, primarily serves as collateral. It is unsuitable to apply an in

====================================================================================================
[95] id=0x539ad30f3d3d531702bb7619fc0a9a44dc2da6a8e022eff7ffdc678032e0a8b9  token=AAVE  space=aavedao.eth  date=2024-12-30
TITLE: [ARFC] Add rlUSD to Core Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Title: [ARFC] Add rlUSD to Core Instance
## Author: Tokenlogic & ACI (Aave Chan Initiative)
## Date: 2024-12-16

> ARFC has been updated with latest Risk Parameters 2024-12-23

---

# Summary

This publication proposes onboardin Ripple's rlUSD stablecoin to the Core instance of Aave v3 on Ethereum.

# Motivation

rlUSD has received [NYDFS approval](https://x.com/bgarlinghouse/status/1866571228464460215) and is anticipated to launch in the near future. Whilst the date is unknown and subject to speculation, this proposals prepares the Aave Protocol to support the listing.

With rlUSD now [transferrable](https://etherscan.io/token/0x8292Bb45bf1Ee4d140127049757C2E0fF06317eD) and circulating supply at 52.9M (15th December 2024), this ARFC proposes onboarding rlUSD with conservative risk parameters pending a Chainlink Oracle.

# Specification

Ticker: rlUSD

Contract address on mainnet: `0x8292Bb45bf1Ee4d140127049757C2E0fF06317eD`

Chainlink oracle: `soon`

Project: https://ripple.com/

GitHub: https://github.com/fbtc-xyz/fbtc-contract

Docs: https://docs.ripple.com/stablecoin/developer-resources/rlusd-on-ethereum

Twitter: https://x.com/Ripple

Initial Risk Parameters are shared, being aware that those can be subject to changes per Risk Service Providers feedback, and ARFC would be updated accordingly.

| **Parameter** | **Value (Ethereum)** |
| --- | --- |
| Isolation Mode | No |
| Borrowable | Yes |
| Collateral Enabled | No |
| Supply Cap | - |
| Borrow Cap | - |
| Debt Ceil

====================================================================================================
[96] id=0x713989ad71340840fa1f52d6b19c00f001a967070c7a506696034f68774a1986  token=AAVE  space=aavedao.eth  date=2025-01-22
TITLE: [TEMP CHECK] Joint Incentive Program With Polygon
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## Author: Polygon Community Treasury Board

## Date: 2024-01-16

---

**Summary**

The Polygon Community Treasury Board proposes a strategic initiative to restore relationships and strengthen ties between the Polygon and Aave communities, and drive new growth of Aave on Polygon PoS. The following proposal introduces a $3M joint liquidity incentive program that seeks to enhance liquidity and adoption of Aave on the Polygon PoS chain, and re-align our respective communities. This proposal is being put forth by the Polygon CTB, which is external from Polygon Labs and acts on behalf of the Polygon community and ecosystem.

**Motivation**

**Long History of Success of Aave on Polygon PoS**

There is no debate that Aave’s deployment on Polygon in early 2021 is what kickstarted the multichain revolution, and since then, the collaboration between our two ecosystems has yielded tremendous results. With Polygon’s high throughput and low transaction costs complementing Aave’s robust lending and borrowing infrastructure, we have witnessed exponential growth of Aave TVL on Polygon:

* Aave v2 on Polygon PoS reached $3.5Bn+ TVL at its peak.
* Aave v3 on Polygon PoS reached $450M+ TVL at its peak ($335M TVL as of 1/14/24).
* Polygon and Aave, together with so many other protocols and community members, were able to contribute to the first successful high-scalability ecosystem on Ethereum. This was a proof of concept that led to many of the amazing innovations happening across the current,

====================================================================================================
[97] id=0xa2d0c8f06e8fae4ba961407f77732c0b6f870e00a349f826a032d20e291e48f6  token=AAVE  space=aavedao.eth  date=2025-01-23
TITLE: [ARFC] Add EURC to BASE Aave V3
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## **[ARFC] Add EURC to BASE Aave V3**

## Author: ACI (Aave Chan Initiative)

## Date: 2025-01-17

> ARFC updated with Parameters 2025-01-23

### **Simple** **Summary:**

The current ARFC proposes to add EURC on Base V3. EURC is Circle’s EUR-backed stablecoin, enhancing liquidity and expanding the platform’s appeal to European users. Original proposal was [**[TEMP CHECK] Add EURC to BASE Aave V3**](https://governance.aave.com/t/temp-check-add-eurc-to-base-aave-v3/20423) but has been reformatted to be governance compliant. It has also passed [TEMP CHECK Snapshot](https://snapshot.org/#/s:aave.eth/proposal/0x4ead0ee7c538878f1584b20f12ee99e62fb7e08517042b9820836cd9fe7375c7) .

### **Motivation/Background:**

EURC is a fully backed stablecoin pegged to the Euro, issued by Circle, the same entity behind USDC. It is a reliable and transparent Euro-denominated asset gaining adoption across DeFi protocols.

- **Utility and Role:** EURC facilitates Euro-based transactions in DeFi, allowing for a stable store of value and an efficient medium of exchange within the ecosystem.
- **Backers:** Circle is a trusted issuer with a track record of regulatory compliance, providing confidence in EURC’s stability.
- **Performance:** EURC has demonstrated consistent performance and adoption within the broader DeFi space such as Morpho (3M), Alien(4M) and Aerodome (3M).
- **Euro Liquidity:** EURC will offer Aave users access to Euro-denominated liquidity, appealing to the European market.
- **Broad

====================================================================================================
[98] id=0x8d41750cae27326ac50a84a25846747baeb99c57d371c536ec9219ff662f7497  token=AAVE  space=aavedao.eth  date=2025-01-31
TITLE: [ARFC] Deploy Aave v3 on Sonic
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC] Deploy Aave v3 on Sonic

## Author: ACI

## Date: 2025-01-07
-----

>Risk Parameters have been provided by Service Providers and this section has been updated 2025-01-30

## Simple Summary:

This ARFC seeks the community’s input on the deployment of Aave V3 on Sonic Mainnet.

## Background:

Sonic is a new Layer 1 EVM blockchain offering 10,000 TPS and fee monetization for app builders. It is the newest blockchain from the creators of Fantom which reached a peak TVL of circa $14.5 billion in 2021. 

## Motivation

Aave has deployed on multiple promising new L1 and L2 EVM networks and is often one of the largest protocols on these networks. Given the impressive history of the team building Sonic, and the innovations it promises, it represents a strong candidate for deployment of Aave V3. In addition, the fee monetization for apps has potential to be an additional income source for Aave.

## Proof of Liquidity (POL) and Deposit Commitments:

The Sonic Foundation will provide the following, upon its deployment is confirmed:

- 15M USD Funding from Sonic
- 800k USD stablecoins from Aave
- Up to 50M $S tokens Supply
- 20M of USDC Supply


## Specification:

Risk Parameters have been provided by Service Providers and this section has been updated 2025-01-30

| Parameter |  |  |  |
| --- | --- | --- | --- |
| Asset | WETH | wS | USDC.e |
| Isolation Mode | No | No | No |
| Enable Borrow | Yes | Yes | Yes |
| Enable Collateral | Yes | Yes | Yes |
| Loan To Value | 80% | 35%

====================================================================================================
[99] id=0x1d8d0d25f3b705bf207a130308658d15256e2cebc58d123e4ad9e7e3a177ac11  token=AAVE  space=aavedao.eth  date=2025-02-02
TITLE: [ARFC] Supply and Borrow Cap Risk Oracle Activation
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary

Building on the recent integration of [Aave Generalized Risk Stewards (AGRS)](https://governance.aave.com/t/arfc-aave-generalized-risk-stewards-agrs-activation/19178), this proposal introduces an automated Risk Oracle framework to enhance the efficiency of Supply and Borrow cap updates within the Aave Protocol. The framework is built around two core components: (1) algorithmic, simulation-based assessments continuously conducted to evaluate cap exposure across all markets, and (2) predefined cap utilization thresholds that trigger simulations to determine whether cap adjustments are necessary. Operating under stricter constraints than those currently permitted at the Risk Steward contract level, this system introduces no additional permissions while significantly improving the observability and responsiveness of risk management. The initial deployment is planned for Arbitrum to start, to be expanded to other chains in the future.

# Motivation

### Current Cap Update Process

The current implementation of the Risk Steward contract allows for the manual, periodic updating of Supply and Borrow caps, generally performed in response to market demand. Such an implementation allows for the risk/reward of respective asset exposure to be quantified and assessed in a much quicker fashion as opposed to the traditional governance mechanisms in place. This creates the ability to perform cap increases every three days by up to a 100% relative change, alongside functionality to

====================================================================================================
[100] id=0x048f19fef1f17cd88f962935fb21dd09f8a420c9ead9b7e165640a39c74e466f  token=AAVE  space=aavedao.eth  date=2025-02-09
TITLE: [ARFC] Deploy stataUSDC GSM on Base
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
---

title: [ARFC] Deploy stataUSDC GSM on Base
author: @TokenLogic
created: 2025-02-05

---

# Summary

This publication proposes deploying a stataUSDC GHO Stability Module (GSM) on Base supported by a facilitator on Ethereum.

# Motivation

This proposal recommends deploying a GSM on Base to enhance GHO's price stability during market fluctuations and facilitate new circulating supply issuance.

Introducing a GSM shortly after launch will help mitigate volatility caused by thin secondary market liquidity while providing users with an alternative way to acquire GHO. Given the various yield opportunities for GHO on Base, limited supply could push GHO above $1.00, as seen during its launch on Arbitrum.

Deploying a stataUSDC GSM would allow users to exchange USDC for GHO, with USDC deposited into Aave Protocol. Each unit of GHO transferred to a user increases the circulating supply, helping to balance market demand.

The chart below compares USDC deposit rates across Aave v3 instances on Ethereum Core, Arbitrum, and Base. Notably, the USDC deposit APY on Base closely aligns with that of Ethereum Core.

![Screenshot 2025-02-05 at 16.41.37](https://hackmd.io/_uploads/rJ8A4MbFkg.png)

All GHO issued by the GSM is backed 1:1, ensuring GHO is always over-collateralised.

The Aave DAO will receive the following revenue streams from the aUSDC GSM:

* Swap Fees;
* Surplus aToken Yield; and,
* Any incentives distributed to USDC deposit on Aave v3.

The aToken yield acts as a proxy for

====================================================================================================
[101] id=0xe7251459edae302517bc471776d82069afb13441b058c9fc989e0c878f13c873  token=AAVE  space=aavedao.eth  date=2025-02-09
TITLE: [ARFC] Prime Instance - Restore ETH LTV
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
title: [ARFC] Prime Instance - Restore ETH LTV 
author: @TokenLogic
created: 2024-02-04

---

# Summary

This publication proposes restoring ETH's LTV to 82% on the Prime instance of Aave v3.

# Motivation

With the introduction of liquidity mining rewards for ETH deposits on Prime, some users exploited wETH/wETH leverage to farm rewards. In response, ETH’s LTV was set to 0, preventing new ETH collateral positions while preserving existing ones.

Transitioning from direct liquidity mining emissions to a periodic Merkl distribution ensures that users leveraging wETH/wETH can be disqualified from rewards. By introducing qualification criteria, incentives are directed toward users who engage with the protocol as intended.

While details of the future liquidity mining program are yet to be announced, this proposal focuses on re-enabling ETH collateral positions by restoring the LTV to 82%—its original level at Prime’s launch.

# Specification

The LTV for ETH on Prime is to be amended as outlined below:

| **Parameter**             |  **Current** | **Proposed** |
| --------------------- | -------- | -------- |
| LTV                   |  0.00%   |  82.00%  |

The ETH Correlated eMode category is to be amended as outlined below:

| **Parameter**             |  **Value** | **Value** |
| --------------------- | -------- | -------- |
| Asset                          |  wETH   | wstETH  |
| Collateral                   |  Yes -> **No**  |  Yes |
| Borrowable                |  Yes   |

====================================================================================================
[102] id=0x1c0f3a4966a2af2fa39439d078ab8359a316b9a0d799c4abb046530624206abd  token=AAVE  space=aavedao.eth  date=2025-02-10
TITLE: [ARFC] Proposal to Allocate AGD treasury to Aave DAO
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC] Proposal to Allocate AGD treasury to Aave DAO

## **Author:** ACI

## **Date:** 2025-02-03

## **Summary**

This is a proposal to allocate Aave Grants DAO (AGD) treasury to Aave DAO, since Aave Grants DAO is winding down. 

## **Motivation**

Following the latest update by 0xbill on AGD journey, and next steps ([Reflecting on AGD’s Journey and Next Steps](https://governance.aave.com/t/reflecting-on-agd-s-journey-and-next-steps/20792) )which is the result of [Update from Aave Grants: Winding Down AGD 1.0 and What’s Next](https://governance.aave.com/t/update-from-aave-grants-winding-down-agd-1-0-and-what-s-next/18707),  where operations were announced to be wounded down and team disbanded, in August 2024, Aave Grants DAO still controls a treasury of mixed assets, that we believe should be disbursed back to Aave DAO, that will decide its utility and destination.

## AGD Treasury

| **Asset** | **# of Tokens Held in Treasury or Allowance** |
| --- | --- |
| DAI | 478.61 |
| GHO | 321,768.10 |
| USDC | 6,738.05 |
| USDT | 7,281.89 |
| SAFE | 5,243.26 |
| AAVE | 2,275.81 |
| OP | 259,221.75 |

## Specification

Send AGD treasury to Aave DAO collectors:

Aave V3 Ethereum Collector : 0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c 

Aave V3 Optimism Collector: 

0xB2289E329D2F85F1eD31Adbb30eA345278F21bcf

Aave V3 Gnosis Collector:

0xB5b64c7E00374e766272f8B442Cd261412D4b118

## **Useful Links**

[**ARC: Aave Community Grants Program**](https://governance.aave.com/t/arc-aave-comm

====================================================================================================
[103] id=0x75caa290c8eefe042d8d3959da08c0f6ebbd6a98e45bbbb9a991531f26bd9899  token=AAVE  space=aavedao.eth  date=2025-02-17
TITLE: [ARFC] Add sUSDE to Aave V3 Base Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
### **[ARFC] Add sUSDE to Aave V3 Base Instance**

### Author: sreno

### Date: 2025-02-03

> ARFC edited by ACI under Skywards. Also Risk Parameters added after Risk Service Providers feedback 2025-02-17

---

## Summary
*--EDITED: removed USDE--*
This publication presents the community an opportunity to expand sUSDE integration on the AAVE platform by adding sUSDE collateral option to Base.

sUSDE is an innovative stable-coin derivative producing real yield through perpetual arbitrage and ETH backing yield. 
## Motivation

- Expanding sUSDE integration into Base would allow any size L2 participant to access sUSDE yields while avoiding the expensive gas fees incurred from ETH main-net.
-Adding sUSDE to Base V3 market would allow Base sUSDE to be used productively through lending. This would facilitate the same 'Borrow USDC/USDT then stake/swap for sUSDE' arbitrage which happens within the ETH V3 main market, but on Base.

Ethena lacks strong foundations on Base L2 for their native yieldbearing stable-coin, sUSDE. The addition of sUSDE to Base V3 AAVE market would facilitate this expansion to the untapped L2 market for Ethena.

Base has seen expansion in its TVL now surpassing Arbitrum by ~15%. Base chain is a small but significant part of total Defi TVL (all chains) of 3%.
Source: https://defillama.com/chains

Updated price feeds for USDE and sUSDE could mean one or both will not have to be added to Base V3 in an isolated market.

## Specification

Ticker: USDE and sUSDE
USD

====================================================================================================
[104] id=0xab1d9c42264c89e1b8f0d807c9ff971f8c3f9f5cc0323072d9e970c110d1e39b  token=AAVE  space=aavedao.eth  date=2025-02-27
TITLE: [TEMP CHECK] Deploy Aave v3 on megaETH
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# [TEMP CHECK] Deploy Aave v3 on megaETH

## Author: ACI

## Date: 2025-02-21

## **Simple Summary**

This TEMP CHECK proposes the deployment of an Aave V3 pool on megaETH.

## Motivation

MegaETH is an EVM-compatible blockchain that aims to bring Web2-level real-time performance to the crypto world for the first time. Their goal is to push the performance to hardware limits, bridging the gap between blockchains and traditional cloud computing servers.

MegaETH plans to offer several distinguishing features, including high transaction throughput, abundant compute capacity, and millisecond-level response times even under heavy load. 

The network offers a performant location to the deploy the Aave protocol, and the megaETH team are planning to support Aave’s launch on the network. 

## Specification

Risk Parameters will be provided by Risk Service Providers during the ARFC stage and ARFC will be updated accordingly.

## Useful Links

- megaETH
    - Website: https://www.megaeth.com/
    - Whitepaper: https://www.megaeth.com/research

## **Disclaimer**

The current proposal is powered by Skywards. ACI is not directly affiliated with megaETH and did not receive compensation related to this proposal.

## **Next Steps**

1. Publish a TEMP CHECK in order to get initial feedback from Community and Service Providers.
2. Escalate proposal to TEMP CHECK Snapshot.
3. If TEMP CHECK Snapshot pass, publish an ARFC to continue gathering community and Service Providers feedback.
4. If the A

====================================================================================================
[105] id=0xfa1d8b2ffe47ad26862175a113c18a98d6e3ff258b3001f365c5e3a62d5ed53a  token=AAVE  space=aavedao.eth  date=2025-03-10
TITLE: [TEMP CHECK] Add USR to Aave v3 Core Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# [TEMP CHECK] Add USR to Aave v3 Core Instance

---

title: [TEMP CHECK] Add USR to Aave v3 Core Instance
author: @ACI & @TokenLogic
created: 2025-03-03

---

# Summary

The proposal aims to onboard [Resolv](https://resolv.xyz/)'s USR, to Aave v3 protocol Core Market on Ethereum.

# Motivation

### Introduction

Resolv is a decentralized protocol designed to maintain and manage USR a over-collateralised USD stablecoin backed by a delta-neutral ETH denominated strategy, alongside the Resolv Liquidity Pool (RLP), which acts as a liquid insurance reserve ensuring USR remains overcollateralized.

Resolv has been one of the latest growing stablecoins from last few months with TVL surging from 37M in December to now over 675M at the moment and with a USR circulating supply of 570M.

Resolv is currently running an ongoing points campaign, with Season 1 set to conclude between the end of Q1 and Season 2 set to begin during Q2. As part of this campaign, wstUSR holders earn 5 points per wstUSR held daily.

### Mint / Redeem

USR is minted using USDT or USDC at a 1:1 ratio, with minting fees currently set to zero but subject to future adjustments. Users can stake USR to receive wstUSR, which is the wrapped version of stUSR, to earn rebasing staking rewards. USR can also be redeemed back into USDC or USDT, with redemptions currently processed without fees.

The redemption process, though infrequent, averages approximately 1 hour and 50 minutes per transaction, with a maximum stated dura

====================================================================================================
[106] id=0x9de39ac8c12d86853779584dbfdbd9c8ef679d6f530a7c0d5c66c358b6ec772c  token=AAVE  space=aavedao.eth  date=2025-03-10
TITLE: [TEMP CHECK] Add stS to Aave v3 Sonic Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# [TEMP CHECK] Add stS to Aave v3 Sonic Instance

---

title: [TEMP CHECK] Add stS to Aave v3 Sonic Instance
author: @ACI
created: 2025-02-28

---

# Summary

The proposal aims to onboard [Beets](https://beets.fi/)'s stS, to Aave v3 Sonic instance.

# Motivation

Launched in December 2024, Beets Staked Sonic (stS) is an ERC-20 Liquid Staked Token offering seamless exposure to Sonic network staking rewards via validator delegation, while remaining fully liquid in users’ wallets.

Similar to wstETH, stS passively accrues value—each time delegation rewards are added to the staking pool, the stS-to-S exchange rate increases automatically, with no action needed from holders. The underlying S delegation enhances Sonic’s decentralization across a [diverse set of validators](https://dune.com/queries/4534324/7569460) and strengthens the network’s economic security.

Previously known as sFTMx, the leading LST on Fantom Opera, stS quickly established itself as the kingmaker LST in the Sonic ecosystem, capturing over [12% of all staked S liquidity and 76% of S LST liquidity](https://www.defiwars.xyz/wars/sonic). Demand for leverage looping strategies using stS has been steadily rising, with over $160 million already deployed across other lending markets. Despite this strong demand for leveraged positions, stS has maintained a solid peg, currently trading at [99.72%](https://www.defiwars.xyz/wars/sonic).

Users can easily convert their S into stS via the [Beets minting UI](https://beets.f

====================================================================================================
[107] id=0x27b21aa2cd21d5e94eb9b9e0232fe875ad45719588ada4b059f67a8834d7408e  token=AAVE  space=aavedao.eth  date=2025-03-11
TITLE: [ARFC] Enhancements in Aave v3 Gnosis Chain Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
> 2025-03-10: This post was edited to reflect @LlamaRisk and @ChaosLabs parameters recommendations. When they differ, the most conservative one was selected.

# Summary

This publication proposes changes in the Gnosis Chain instance to improve the capital efficiency of USDC.e and sDAI assets by promoting changes on its parametrisation.

# Motivation

The Gnosis Chain’s DeFi landscape has evolved considerably since these assets were first introduced. With a vibrant ecosystem now in place, it’s time to enhance capital efficiency, reduce capital fragmentation, and create useful debt vs no risk looping within the Aave GC instance to attract more capital and increase utilisation.

**USDC to USDC.e Transition:**

Gnosis Chain is committed to making USDC.e (the version that aligns with Circle’s standards) the defacto version of this stablecoin within its ecosystem, by accelerating the transition from USDC and making it the major market within Aave’s GC instance (replacing xDAI). To incentivise this migration and accommodate increased capital inflows, we propose the following adjustments for USDC.e:

* Supply and Borrowing Cap Increase: Enacted via the Risk Steward.
* Emode Creation: Establish an Emode pairing between USDC.e and sDAI, similar to the existing sDAI/EURe Emode.

Those changes will incentivise looping strategies with USDC.e similar to those with EURe/xDAI.

To further promote the transition to USDC.e, we propose reducing the LTV factor for USDC. This measure will prevent

====================================================================================================
[108] id=0x2b9f5615f406bf4d726c62e9a2b0eba25bbb3b0f50c3ad73ca78b7367492705d  token=AAVE  space=aavedao.eth  date=2025-03-13
TITLE: [ARFC-ADDENDUM] Aave DAO & Chainlink Smart Value Recapture (SVR)
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC-ADDENDUM] Aave DAO & Chainlink Smart Value Recapture (SVR)

## Author: ACI

## Date: 2025-03-12

---

## Summary

The current proposal pretends to formalize a six-month collaboration agreement between Aave DAO and Chainlink regarding the potential integration of Chainlink’s Smart Value Recapture (or SVR) system. 

## Motivation

The DAO is currently discussing the activation of Chainlink’s SVR system in Phase 1, (as its currently being discussed at [ARFC Snapshot stage](https://snapshot.box/#/s:aave.eth/proposal/0xe260268c607f20c85d1f93323f2f58b05f202916e0d3dbf55a8c335ed9be92da/discussion))

If proposal passes, SVR is expected to enhance Aave’s value recapture in liquidation scenarios, potentially generating significant additional revenue. 

Therefore it makes sense to formalize an agreement that would include a revenue sharing model and exclusivity to align incentives and ensure focused development on the Aave ecosystem.

This proposal is an addendum of [**[ARFC] Aave <> Chainlink SVR v1. Phase 1 activation**](https://governance.aave.com/t/arfc-aave-chainlink-svr-v1-phase-1-activation/21247).

## Specification

**Revenue Sharing Mechanism**

- The revenue split initially proposed will be set to:
    - **65% to Aave**
    - **35% to Chainlink**
- This distribution will be in effect for six months from the date of activation of the first SVR in Aave pools.
- Chainlink will send the proceeds of SVR directly to the Aave Ethereum Collector on https://etherscan.io/address

====================================================================================================
[109] id=0xf0591fe8e54900da9929fe25c466c2b4a0fac6e8f7a3a000087797363847fb65  token=AAVE  space=aavedao.eth  date=2025-03-14
TITLE: [ARFC] Aavenomics implementation: Part one
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
---

**Title**: [ARFC] Aavenomics implementation: Part one

**Author**: @marczeller - ACI 

**Date**: 2025-03-04

---

## Summary

This proposal seeks governance approval for the first part of the implementation of updated Aavenomics, updating AAVE tokenomics, protocol excess revenue redistribution, deprecating LEND, and updating AAVE secondary liquidity protocol management.

## Motivation

### Before we start

This proposal is the natural continuation of the [[TEMP CHECK] Aavenomics update](https://governance.aave.com/t/temp-check-aavenomics-update/18379) presented in July 2024 and [approved by governance](https://snapshot.box/#/s:aave.eth/proposal/0x7f4941aff652cf2a41f47bc58220a952e4894fdc16e27a975045faa9c458da19) in August 2024; it is suggested that readers of the current proposals familiarize themselves with the TEMP CHECK for better context. The current proposal is focused on implementing Aavenomics and is meant to be more concise than the TEMP CHECK for improved readability.

### Introduction

The Aavenomics update TEMP CHECK was approved around six months ago, since then, the Aave protocol reinforced it’s leadership in the Defi vertical and became the #1 Defi protocol in general.
Aave's market share has increased every quarter for the past two years, and GHO crossed $200m supply with healthy revenue despite harsher market conditions at the end of Q1 2025.

Every triggering milestone for implementation has been met, and Aave successfully upgraded to Aave 3.3 recently, t

====================================================================================================
[110] id=0xac45d4c364ce0306b0c487ae83215ebc1b1ebb406704ec36b9bba7aab428cdea  token=AAVE  space=aavedao.eth  date=2025-03-21
TITLE: [ARFC] Launch GHO on Sonic & set ACI as Emissions Manager for Rewards
CHOICES: YAE | NAE | ABSTAIN
TEXT (first 1500 characters):
# [ARFC] Launch GHO on Sonic & set ACI as Emissions Manager for Rewards

---

title: [ARFC] Launch GHO on Sonic
author: @ACI & @TokenLogic
created: 2025-03-05

---

# Summary

This proposal aims to launch GHO on Sonic & set ACI as Emissions Manager for GHO and aGHO.

# Motivation

GHO has gone multichain with its expansion to the Arbitrum and Base networks. As Aave continues its growth across new ecosystems, it presents a strategic opportunity to extend GHO’s reach alongside it. Sonic’s DeFi sector is currently thriving, and with Aave set to launch on Sonic in the coming weeks, deploying GHO there would be a natural next step.

Sonic’s current growth is largely driven by the anticipation of its [upcoming airdrop](https://docs.soniclabs.com/funding/sonic-airdrop), scheduled for June. Users earn points while protocols accumulate gems based on their activity within the ecosystem.

A key part of the early GHO growth strategy on Sonic will be securing liquidity in an Aave Boosted StableSurge Pool on Beethoven, a friendly fork of Balancer v3. This integration enables idle liquidity to be automatically redeployed into Aave to maximize capital efficiency. Additionally, as part of Aave’s collaboration with Balancer, these pools will receive further support, with Beethoven allocating a portion of their “gems” rewards to incentivize GHO liquidity.

Just as with the Base deployment, a well-coordinated strategy is crucial for GHO’s expansion to Sonic. A successful launch will require clos

====================================================================================================
[111] id=0x22621f3f49e99270faf063d41bc894862052f053c020991a85b973fe2d50bbdf  token=AAVE  space=aavedao.eth  date=2025-03-27
TITLE: [TEMP CHECK] Aave Decentralized Acqui-Hire Framework
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
**Title**: Aave Permissionless Acqui-Hire Framework.
**Author**: DAO Merger.
**Date**: 2025-03-17

**Summary**: In a Darwinian world with (too) many tokens, there should be a way to conduct "acqui-hire" mergers, where the best-performing project (**Aave**) attracts talent. Hence we need a permissionless acqui-hire framework.

**Motivation**: 
- Incentivize Proven Value : Teams earn AAVE tokens only after demonstrating measurable contributions to Aave’s ecosystem. Meanwhile, they have to give up their hard-earned treasury and their inflated market caps dreams.

- Aave Token Holder Benefit : The acqui-hired team’s treasury is repurposed to purchase AAVE tokens and reward their community with it, aligning incentives with Aave DAO.

- Permissionless Efficiency : Minimize overhead using governance and pre-existing framework while maintaining Aave’s decentralized ethos.

**Specification**: 

No change are required to the code.

1. Criteria for entry

The framework relies on a single vote after eligibility is confirmed.

Eligibility :
- Team must prove control of a token with at least $50K in liquidity in AAVE tokens.
- Team submits wallet addresses and a treasury address holding their funds.
- Team makes a proposal outling the earn out terms and objectives

2. Execution :

Provided vote is positive :
- Converts the treasury (e.g., ETH, stablecoins, or their native token) into AAVE via a DEX (e.g., Uniswap).
- Distributes the resulting AAVE tokens to the team’s existing holders prop

====================================================================================================
[112] id=0x54efdfaaccf429320071c7e56dd8f14759f2027c8f1c1fb4ef0596374c7558d8  token=AAVE  space=aavedao.eth  date=2025-04-01
TITLE: [ARFC] Add AAVE token to Aave V3 Base Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
> Risk Parameters have been updated by Risk Service Providers and ARFC has been updated accordingly 2025-04-01
---

## Summary

This publication presents the community an opportunity to expand AAVE governance token integration on the AAVE platform by adding AAVE collateral option to Base.

AAVE token has wide integrations into all other major AAVE instances including ETH Mainnet, Arbitrum, Optimism, Polygon, and Avalanche. Adding AAVE to the Base instance is the next logical step in AAVE token integration within the AAVE lending platform. 

## Motivation

* AAVE token is a versatile governance token which is already accepted collateral on all major AAVE instances.

-The Base Market is growing in TVL, the addition of collateral options already found on other AAVE instances will increase Base Market growth. 
-There is deep liquidity on Base chain for the AAVE token already. Price impact of just **0.77%** for $1m ETH/AAVE trades using jumper.exchange on Base.
-Aerodrome (Base DEX) has $10m TVL in WETH/AAVE concentrated liquidity.
![34039cc1bf8502f76660a4128e8162cb.png](ipfs://bafkreiclmjg4tyndj5gnyr522mkqdxxtaicqtmcntn4vtlnfhghjo3f45i)

![eaadd7e857120a1d552e4270081c9d3f.png](ipfs://bafkreic4fhcydkhxqeeppoq4ahujw3l2dcri7hxfiqq2wfj4rezbi4aixq)

Base has seen expansion in its TVL now surpassing Arbitrum by ~15%. Base chain is a small but significant part of total Defi TVL (all chains) of 3%.
Source: https://defillama.com/chains

## Specification

Ticker: AAVE
AAVE L2 (Base) contra

====================================================================================================
[113] id=0xb49491fa374865c309723a992da4d2b1f24e96f310b8842a01cf6215a48e5c6d  token=AAVE  space=aavedao.eth  date=2025-04-08
TITLE: [ARFC] Add stS to Aave v3 Sonic Instance
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
# [ARFC] Add stS to Aave v3 Sonic Instance

---

title: [ARFC] Add stS to Aave v3 Sonic Instance
author: @ACI
created: 2025-03-15

> ARFC updated with Risk Parameters 2025-03-25

---

# Summary

The proposal aims to onboard [Beets](https://beets.fi/)'s stS, to Aave v3 Sonic instance.

# Motivation

Launched in December 2024, Beets Staked Sonic (stS) is an ERC-20 Liquid Staked Token offering seamless exposure to Sonic network staking rewards via validator delegation, while remaining fully liquid in users’ wallets.

Similar to wstETH, stS passively accrues value—each time delegation rewards are added to the staking pool, the stS-to-S exchange rate increases automatically, with no action needed from holders. The underlying S delegation enhances Sonic’s decentralization across a [diverse set of validators](https://dune.com/queries/4534324/7569460) and strengthens the network’s economic security.

Previously known as sFTMx, the leading LST on Fantom Opera, stS quickly established itself as the kingmaker LST in the Sonic ecosystem, capturing over [12% of all staked S liquidity and 76% of S LST liquidity](https://www.defiwars.xyz/wars/sonic). Demand for leverage looping strategies using stS has been steadily rising, with over $160 million already deployed across other lending markets. Despite this strong demand for leveraged positions, stS has maintained a solid peg, currently trading at [99.72%](https://www.defiwars.xyz/wars/sonic).

Users can easily convert their S into stS via th

====================================================================================================
[114] id=0x8dbeee9b489266cfefb8cb3c75fb0791d364975eed48cee951ff04fd17ee57c1  token=AAVE  space=aavedao.eth  date=2025-04-08
TITLE: [ARFC] stkABPT - Emissions Update
CHOICES: YAE | NAY | ABSTAIN
TEXT (first 1500 characters):
---

title: [ARFC] stkABPT - Emissions Update
author: @TokenLogic
created: 2025-04-03

---

# Summary

This publication proposes reducing AAVE emissions to the stkABPT Safety Module category.

# Motivation

During 2025, AAVE liquidity is expected to transition away from stkABPT to a more diversified liquidity base.

The below outlines an overview of what to expect during 2025:

* Reduction stkABPT emissions, eventually to 0;
* Support AAVE liquidity across several networks;
* Improved liquidity distribution amongst LPs; and,
* Introduce Aave DAO liquidity provisions.

Thanks to a coordinated effort between Service Providers, AAVE token holders and Aerodrome, there is now AAVE liquidity on the Base network. The liquidity on Aerodrome was key to supporting the onboarding of AAVE to Aave Protocol on Base.

This publication focuses on implementing the first significant AAVE emission reduction to stkABPT holders.

![Screenshot 2025-04-03 at 21.55.51](https://hackmd.io/_uploads/SJ8k8uhaJg.png)
Source: https://aave.tokenlogic.xyz/stkbpt

## stkABPT Category Performance

### Yield 

The chart below shows the value of the Balancer Protocol Token (BPT) staked in the stkABPT category of the Safety Module (SM) and the historical yield received by Liquidity Providers (LP) over the last 30 days. 

![Screenshot 2025-04-03 at 21.57.57](https://hackmd.io/_uploads/S1PwL_3pkx.png)
Source: https://aave.tokenlogic.xyz/stkbpt

The chart above shows the resulting yield from Swap Fees, wstETH and AA

====================================================================================================
[115] id=0x9130a7cf9857fb6e822bc8d7fc632059b6046edfc8c6c8361c6640374a6a66d3  token=AAVE  space=aavedao.eth  date=2025-04-15
TITLE: [TEMP CHECK] Horizon’s RWA Instance
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
---
Title: [TEMP CHECK] Horizon’s RWA Instance
Author: @aavelabs
Date: 2025-04-15
---

![|904x509](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcJZD9736ZnwQouGOlS_t7pWTnuizTAU1acChstolyJoa6gyo5gvE795dO4-8a4i7dSTzwHjdDaTsn9CFbQiYXFX_i6-TtcxafzgXGIf-Glrvw9D5rX1Zrrd6R4a71rGKhseWQXUQ?key=rGRH6EIjJd6Q7YqlNKaFjz3H)

# Summary

Horizon, an Aave Labs tokenization initiative, creates RWA products tailored to institutions, where regulatory compliance requires some centralization for permissionless DeFi integrations.

This Temp Check proposes a friendly fork for Horizon to create a white label instance of the Aave Protocol, enabling the Aave DAO to capture new revenue from the Horizon RWA instance, one that is currently uncaptured.

# Motivation

Aave Labs is launching an initiative that works in the RWA space, providing support for existing tokenized assets in the market and tokenizing assets such as Money Market Funds, Credit, Equities and Real Estate. Eligible users can subscribe and redeem these assets onchain. This initiative is also meant to facilitate the flow of value into Aave Protocol through collateralization of these tokenized assets.

Currently, the Aave DAO has limited revenue from RWAs, yet the RWA market is growing substantially with more institutions interested in pursuing RWAs. To accelerate this revenue stream, Aave Labs proposes a white label Aave Protocol instance for centralized and permissioned Horizon assets.

# How Does the Horizon RWA Instance Work?

The Ho

====================================================================================================
[116] id=0xc69410600084e9d3d27e6569dddda08fc053182bcf402e3e612fc97cab783f24  token=AAVE  space=aavedao.eth  date=2025-05-02
TITLE: [ARFC] Horizon’s RWA Instance
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
---
Title: [ARFC] Horizon’s RWA Instance
Author: @aavelabs
Date: 2025-05-02
---
![|904x509](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfELiFrFpANwK0eXsIN03O-UD6POPqZTmhcc4Xnu92XD46JpyE9hV_gPRx-iTNBFEKQhBo-qQ7_1bJUTeHq7bVesim_StgmqRt_FW1-BzNZwgSskIqPFKI2Dzz-2L6ftZEI2l73nA?key=Iax17Vr8fPnoXh0YRYRMDFVF)
# Summary
Horizon, an Aave Labs tokenization initiative, creates RWA products tailored to institutions, where regulatory compliance requires some centralization for permissionless DeFi integrations.
This ARFC proposes a friendly fork for Horizon to create a white label instance of the Aave Protocol, enabling the Aave DAO to capture new revenue from the Horizon RWA instance, one that is currently uncaptured.
# Motivation
Aave Labs is launching an initiative that works in the RWA space, providing support for existing tokenized assets in the market and tokenizing assets such as Money Market Funds, Credit, Equities and Real Estate. Eligible users can subscribe and redeem these assets onchain. This initiative is also meant to facilitate the flow of value into Aave Protocol through collateralization of these tokenized assets.
Currently, the Aave DAO has limited revenue from RWAs, yet the RWA market is growing substantially with more institutions interested in pursuing RWAs. To accelerate this revenue stream, Aave Labs proposes a white label Aave Protocol instance for centralized and permissioned Horizon assets.
# How Does the Horizon RWA Instance Work?
The Horizon RWA instance co

====================================================================================================
[117] id=0x4dfc398fabb63305900572dff38b2ff8e104b0710077f6b7e48049de173d186b  token=AAVE  space=aavedao.eth  date=2025-05-19
TITLE: [ARFC] Base Incentive Campaign Funding
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
---

title: [ARFC] Base Incentive Campaign Funding 
author: @TokenLogic
created: 2025-05-06

---

# Summary

This publication proposes launching a targeted incentive campaign to accelerate Aave's adoption and growing market share on the Base network. 

# Motivation

During April variable Debt on Base has increased strongly on Aave Protocol from 337.9M to 377.9M, an 11.83% increase, meanwhile user deposits increased by only 3.92%. The growing demand for liquidity creates a competitive environment for both attracting user deposits and providing attractive funding rates.

The chart below highlights the improvement in demand for liquidity on the Base instance of Aave v3. The recent uptick in debt during April was only bettered by Avalanche and Ethereum v3 instances. Whilst Base continues to grow, Aave's positioning can be improved by capturing a large portion of the debt expansion in the coming months.

![Screenshot 2025-05-03 at 00.05.54](https://hackmd.io/_uploads/S1-1gRzxgx.png)

With the use of incentives to create an improved deposit yield and lower cost of capital for borrowers, the resulting demand is expected to attract new liquidity deposits and new users seeking access to lower borrowing costs. Improving the value proposition for the end user is expected to strengthen Aave's positioning within the Base ecosystem. 

### Incentives Allocation

With the use of targeted incentives and enhanced capital efficiency, the expected returns are strengthen by only rewarding Aave al

====================================================================================================
[118] id=0xd2a01c01d23804bb3d06a04e9f08e68e8bf70eb6dc2bfb6ad6feb9c0427ad903  token=AAVE  space=aavedao.eth  date=2025-05-20
TITLE: [ARFC] Supply and Borrow Cap Risk Oracle Constraint Specification
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC] Supply and Borrow Cap Risk Oracle Constraint Specification 
## Author: Chaos Labs
## Date: 2025-05-15

## Summary

The deployment of [Supply and Borrow Cap Risk Oracles](https://governance.aave.com/t/arfc-supply-and-borrow-cap-risk-oracle-activation/20834) across Avalanche, Base, and Arbitrum has proven to be highly robust and operationally efficient, collectively underwriting over $3.5 billion in total deposits and performing 140 collective updates since its launch a few months ago. This successful rollout has affirmed the framework’s ability to manage cap adjustments dynamically while strictly adhering to defined constraints. As the system scales across more markets, it becomes increasingly important to establish clear, standardized criteria for where automation is appropriate, ensuring continued protocol safety, effective governance, and consistent application of risk controls.

This addendum outlines a refined framework to standardize which asset types are eligible for automated cap adjustments under the Risk Oracle system. While the core automation mechanism is designed to enhance the scalability, efficiency, and responsiveness of cap management across Aave markets, not all assets exhibit risk profiles or maturity levels that make them suitable for autonomous updates.

To that end, this proposal introduces specific exclusion criteria that ensure automation is applied conservatively and only where appropriate. These constraints are rooted in protocol maturity, l

====================================================================================================
[119] id=0xbe792a1db33cd7803e23810553e5a6a728c3ac15827ad2652aa6de1858fa5596  token=AAVE  space=aavedao.eth  date=2025-05-23
TITLE: [ARFC] Aave Umbrella activation
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Simply summary
Proposal for the Aave governance to approve to initial activation of the Aave Umbrella system, focusing on Aave v3 Core Ethereum before expanding to other pools and networks.

---
---

# Motivation
Aave Umbrella is a replacement for the Aave Safety Module acting as a decentralised staking & coverage by slashing mechanism for potential losses in Aave pools.
With Umbrella, instead of staking AAVE, ABPT (Balancer AAVE/wstETH LP), users will use Aave aTokens (aUSDC, aUSDT, etc) of each pool while keeping GHO, given these are the most efficient assets for coverage.

---
---

# Specification
For full context it is highly recommended that voters visit and read the associated Aave governance forum post, but in summary, the proposal will do the following:
- Activating all Umbrella core and peripheral systems to start staking of assets to cover the biggest Aave v3 pool: v3 Core Ethereum.
- Do some changes on the legacy Safety Module instances, to start a progressive deprecation of it.

---

## Umbrella side

- The initial assets on Umbrella (v3 Core Ethereum) and their configurations will be the following.

| Staked asset | Covered asset | Target Liquidity * | Max emission (rewards at target liquidity) | Umbrella APY range (up until excess liquidity) ** | Total APY (Aave + Umbrella)*** | Cooldown/unstake window | Deficit offset |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aUSDC (wrapped) | USDC | 66’000’000 USDC | 2’330’000 aUSDC/year | 1.76%-7.06% | 6.8%-12.5

====================================================================================================
[120] id=0xa390fb9061fd689a5d93519a7a9dae23d76b4010b3eea6aaedc70ea7aaed9310  token=AAVE  space=aavedao.eth  date=2025-06-19
TITLE: [ARFC] GHO CEX Earn Incentive Program
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
---

title: [ARFC] GHO CEX Earn Incentive Program
author: @TokenLogic
created: 2025-06-05

---

## Summary

To maximize the impact of GHO’s upcoming listings on Bybit, Bitget, and other centralized exchanges (CEXs), this publication proposes engaging a market maker to provide spot liquidity and allocating funds to a CEX Earn program to drive broader adoption of GHO.

## Motivation

Listing GHO on centralized exchanges serves as a strategic lever to broaden its adoption by tapping into a wider and more diverse user base. It opens a powerful new distribution channel, allowing the Aave DAO to strengthen GHO’s market presence and accelerate its global reach.

- **Expanded Audience**: Access to retail and institutional users who primarily operate on CEXs and are less familiar with decentralized and on-chain stablecoins.  
- **New Utility**: Enables GHO to be used as collateral in perpetual contracts and other financial products not currently available within DeFi.  
- **Enhanced Liquidity and Visibility**: CEX listings improve global accessibility and strengthen GHO’s brand recognition through higher trading volumes and broader market exposure.

While several stablecoins are already entrenched on centralized platforms, GHO's success will hinge on delivering a compelling value proposition that differentiates it from more established alternatives. By leveraging the Aave Protocol as a native yield engine, GHO can replicate the successful strategies of stablecoins like USDtb and USDe,

====================================================================================================
[121] id=0x65e12ce7784f12fbed9731d4cdbc826a8a5d4804439dc6d55d6e31c0b069a048  token=AAVE  space=aavedao.eth  date=2025-06-25
TITLE: [ARFC] stS Loop Incentive Program
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
Title: [ARFC] stS Loop Incentive Program 
author: @TokenLogic  
created: 2025-06-16 


## Summary

This ARFC proposes the launch of a 3-month stS loop incentive program on Aave. The goal is to deepen stS liquidity on Aave, align incentives with Beets, and ensure Aave remains the exclusive lending market for stS.


## Motivation

Beets has committed to Aave as the exclusive home for stS liquidity and will not incentivize or market any external stS lending market. This commitment aligns with the broader “Just Use Aave” strategy and presents a strong opportunity to consolidate stS liquidity on Aave v3.

To support this integration and unlock meaningful TVL, this ARFC outlines a clear path forward to bootstrap stS<>wS loop participation via:
- Cashback incentives based on stS collector revenue.
- Clarity around exclusivity boundaries regarding Beets’ Boosted Pools.


### Incentive Program Structure

**Phase 1: 3 months**
- 100% of stS collector revenue will be recycled to users participating in the stS<>wS loop.
- A fixed budget of **40,000 wS** will be allocated for cashback distribution, **for the first month**.
- The budget will be managed via the dedicated **MASiv SAFE**, funded directly by the Aave Collector upon approval.

**Phase 2: Months 4 to 6**
- 50% of Aave's stS collector revenue will be recycled to users continuing to engage with the loop.
- Rewards will be distributed on a weekly basis, proportional to looped positions and verified through on-chain criteria.

## Ex

====================================================================================================
[122] id=0x844e6490591165e166fe511c1c527798369a21394fd93812d299cc320ec91dd5  token=AAVE  space=aavedao.eth  date=2025-07-16
TITLE: [ARFC] Safety Module Emission Update
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
---

title: [ARFC] Safety Module Emission Update
author: @TokenLogic
created: 2025-07-10

---

# Summary

This publication outlines the next incremental reduction in AAVE emissions being distributed to stkAAVE and stkABPT holders.

# Motivation

## stkAAVE  

On the 5th June 2025, the Umbrella upgrade went live and the AAVE emissions for stkAAVE reduced by 45 AAVE/day from 360 to 315 AAVE/day. The chart below show the stkAAVE yield reducing from 4.58% to 4.0% as [intended](https://governance.aave.com/t/arfc-aave-umbrella-activation/21521/27) when the Slashing risk was reduced from 30% to 20%. 
 
![Screenshot 2025-07-07 at 18.58.18](https://hackmd.io/_uploads/SkIaqtKSel.png)

The current stkAAVE yield is 3.95% and represents 19.33% of Total AAVE supply with 22,675 unique users, up from 20,023 on the 5th June 2025. Since early April AAVE deposits in stkAAVE have been gradually increasing and only 3.82% of stkAAVE in cooldown, indicating stkAAVE has achieved an equilibrium with only minor flows in and out of the contract. 

![Screenshot 2025-07-07 at 13.12.48](https://hackmd.io/_uploads/ByIajmtSlg.png)

Over the last 30 days, an additional 43,664 AAVE has been deposited into stkAAVE, with 26,595 deposited on the 7th June, two days after the Umbrella upgrade went live.

![Screenshot 2025-07-07 at 19.07.50](https://hackmd.io/_uploads/H17ZpYtBll.png)

Given the strong support for stkAAVE over the 30 day period since Umbrella went live, exceeding our expectations, this publication p

====================================================================================================
[123] id=0x4185135ca5693f3a7022372dc989ee432c1ca792cde020275f3dfb472a90d6f1  token=AAVE  space=aavedao.eth  date=2025-07-17
TITLE: [ARFC] Deploy a Whitelabel Aave V3 Instance on Ink
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
## [ARFC] Deploy a Whitelabel Aave V3 Instance on Ink

## Author: Ink Foundation & ACI

## Date: 2025-06-19

### **Summary**

This proposal aims to deploy a whitelabel version of Aave V3 for the Ink Foundation. By granting a license to deploy a centralized version of the Aave codebase, Aave can expand its technology adoption while creating new revenue streams through partnerships with innovative platforms.

### **Motivation**

The Ink Foundation seeks to leverage Aave's battle-tested infrastructure to create a native lending platform. This partnership represents an opportunity for Aave to expand its influence in the institutional lending space while maintaining its commitment to technological excellence.

### Specification

Key aspects of this deployment include:

- **Centralized Governance:** The instance will initially be centrally governed by the Ink Foundation without a governance token
- **Service Provider Support:** Aave DAO service providers (including ACI, Chaos Labs, and others) will maintain and contribute to the deployment for the initial 6-month period, after which Ink Foundation will need to establish a commercial arrangement for continued support
- **Revenue Sharing:** The Aave DAO will receive a share of all revenue generated by the platform. This should be greater than or equal to the equivalent of a Reserve Factor of 5% based on borrow volume in all pools.
- **Insurance Disclaimer:** This instance will not be covered by the DAO-operated Umbrella.
- **Branding

====================================================================================================
[124] id=0xd0d6ae015476ab371ea10e68ce270af05f45ec4ebcb105a8d573f606277956e1  token=AAVE  space=aavedao.eth  date=2025-07-29
TITLE: [ARFC] Claiming AAVE Rewards for the Sablier Legacy v1.1 Contract
CHOICES: YAE | NAY | Abstain
TEXT (first 1500 characters):
**Title:** [ARFC] Claiming AAVE Rewards for the Sablier Legacy v1.1 Contract
**Author:** Sablier Labs powered by @ACI Skywards
**Date:** 2025-05-05

---

### Summary

This ARFC proposes the transfer of **895.8057 AAVE** (~$160K) in staking rewards from the Aave Safety Module to **[sablier.eth](https://etherscan.io/address/0x5cE95bff1297dADBDcF9929a10Bd02BDfab0DCC6)**, due to the inability of Sablier’s Legacy v1.1 contract to claim them through standard mechanisms.

### Motivation

Sablier Legacy v1.1 is a non-upgradeable smart contract that lacks an ERC-20 recovery or sweeping function. Over time, the contract has accrued staking rewards from participation in the Aave Safety Module. However, due to its immutable design and lack of reward-claiming logic, these tokens are currently inaccessible.

To prevent permanent loss of funds, this proposal seeks governance approval to manually transfer the AAVE rewards to the Sablier treasury ([sablier.eth](https://etherscan.io/address/0x5cE95bff1297dADBDcF9929a10Bd02BDfab0DCC6)), ensuring recovery of assets legitimately earned.

**Supporting context:**

* The contract is publicly documented in [Sablier’s official documentation](https://www.docs.sablier.com/guides/legacy/deployments).
* Source code is verified on [Etherscan](https://etherscan.io/address/0xCD18eAa163733Da39c232722cBC4E8940b1D8888) and open-source on Github.

### Specification

This proposal calls **`claimRewardsOnBehalf()`** on [0xCD18eAa163733Da39c232722cBC4E8940b1D8888](

