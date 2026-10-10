# Labeling packets — batch 07 (125 proposals). Label each against criteria.md.

====================================================================================================
[0] id=0xcb86b4c23e556ab048e3636f45d2b9d65e84f7a2a0971d9a34b9570e5a209f51  token=BAL  space=balancer.eth  date=2023-03-29
TITLE: [BIP-223] Enable USDC-TNGBL 20-80 Gauge with a 2% Emission Cap [Polygon]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[Payload PR](https://github.com/BalancerMaxis/multisig-ops/pull/122)


**Summary:**

Enable gauge on the TNGBL-USDC 80-20 pool

**References/Useful links:**

• [Website](https://www.tangible.store)

• [Documentation](https://docs.tangible.store/)

• [Github Page](https://github.com/TangibleTNFT)

• [Communities](https://discord.com/invite/zC4WpKhcj2)

• [Twitter](https://twitter.com/tangibleDAO)

**Protocol Description:**

Tangible is an RWA tokenization protocol, that already has several gauges for the protocol's stablecoin USDR.

**Motivation:**

Tangible's governance token TNGBL is a core part of the protocol, with all marketplace fees accruing to the token. In addition to having a claim on 10% of USDR seigniorage.

We have been building up protocol owned liquidity in the 80-20 TNGBL-USDC pool on Polygon and believe now it would be beneficial to add additional incentives via a gauge. This will be the main home for TNGBL liquidity on-chain.

**Specifications:**

1. Governance: TNGBL token holders can lock their TNGBL tokens and receive veNFTs that represent their locked tokens. These NFTs will grant holders governance rights. (Full governance launching soon)
2. Oracles: N/A
3. Audits: [Audits - Tangible](https://docs.tangible.store/real-usd/audits)
4. Centralization vectors: Governance upcoming.
5. Market History: Tangible has been tokenizing RWAs for over 18 months and the TNGBL token has been live for almost 12.
6. Value: Adoption and usage of Balancer's novel 80-20 pool

====================================================================================================
[1] id=0x8215d47c8e5505d32e8a9bbf93bf887f9767b901a4248cb2873679d45ce7a421  token=BAL  space=balancer.eth  date=2023-03-29
TITLE: [BIP-225] Amendment to [BIP-146] Incentivize 8020 BPT Staking (ve8020)
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
**Authors: Aura Contributors, Balancer Contributors**

**Background**

[BIP-146](https://snapshot.org/#/balancer.eth/proposal/0x3708b9fcb085bccc6ebb9e9708c6e45528a85b22483da9bbdcc0b606103429fb) was introduced to incentivize adoption of the 80/20 model across DeFI.  The proposal was approved earlier this year.  As noted by Solarcurve, some specifications within BIP-146 were purposefully left as soft requirements to allow for future flexibility.  This current proposal, based on extensive feedback from Balancer and Aura Contributors, seeks to finalize those provisions, so that projects adopting the 80/20 model have a working framework to follow during their grant application process.

**Specifications**

A. BIP-146 suggested the following milestones for grant qualification:

- 25k BAL
    - TVL exceeds value of 25k BAL by 30x
    - TVL exceeds $4.125M
    - Lifetime total revenue earned exceeds $45.8k
- 50K BAL
    - TVL exceeds value of 50k BAL by 30x
    - TVL exceeds $8.25M
    - Lifetime total revenue earned exceeds $275k

This proposal increases requirements in BAL terms to make them closer to the revenue added to the system.  At a market price of $7.00 USD, this amendment revises the first two milestones to the following, with no changes to the latter two milestones in BIP-146:

- 25k BAL
    - TVL exceeds value of 50K BAL by 25x
    - TVL exceeds $8.75M
    - Lifetime total revenue earned exceeds $280K
- 50K BAL
    - TVL exceeds value of 50K BAL by 60x
    - TVL exceeds

====================================================================================================
[2] id=0x0f431ff3cf1319c5b87fe09c6f9a08aa323dbd043d23841019c77a9818a10644  token=BAL  space=balancer.eth  date=2023-03-30
TITLE: [BIP-226] Enable SILO/ETH 80/20 Gauge w/ 2% emissions cap [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way
TEXT (first 1500 characters):
[Combined  2023 Week 14 Payload PR](https://github.com/BalancerMaxis/multisig-ops/pull/122)

**Summary**

This is a proposal to add a gauge for SILO/ETH 80:20 Pool that will serve as the base layer for Silo Finance’s veSILO governance module.

* Silo Finance has a large amount of POL in Balancer, earning incentives that are recycled through voting incentives for AURA and BAL holders to further bolster the pool liquidity. Silo Finance continues to increase its voting incentives over time as protocol revenue increases and is committed to support the Balancer ecosystem long-term.

* Silo Finance is a longtime partner of the Balancer DAO.

* Silo Finance core contributors have allocated roughly $1.4M~ of personal liquidity to the SILO/ETH 80:20 pool to help expand the governance base of SiloDAO.

**References/Useful Links:**

* Silo Website: https://www.silo.finance/
* Dev Docs: https://devdocs.silo.finance/protocol-architecture/protocol-overview
* Silopedia: https://silopedia.silo.finance/
* Twitter: https://twitter.com/SiloFinance
* Forum: https://gov.silo.finance/
* Snapshot: https://snapshot.org/#/silofinance.eth
* Tally: https://www.tally.xyz/gov/silo/proposals
* 80/20 SILO ETH Pool: https://app.balancer.fi/#/ethereum/pool/0x9cc64ee4cb672bc04c54b00a37e1ed75b2cc19dd0002000000000000000004c1
* 50/50 SILO ETH Pool: https://app.balancer.fi/#/ethereum/pool/0x48607651416a943bf5ac71c41be1420538e78f87000200000000000000000327

* Silo Token Address: https://etherscan.io/token/0x6f80310

====================================================================================================
[3] id=0x73556f30ec8f66fe90491e88d691a7c1104a0ff296b02b9c2151b5a6cfcd57fd  token=BAL  space=balancer.eth  date=2023-03-30
TITLE: [BIP-227] Upsize BAL allocation in Ribbon Finance Treasury Vault
CHOICES: Yes, let's do it | No, this is not the way
TEXT (first 1500 characters):
[PR with payload](https://github.com/BalancerMaxis/multisig-ops/pull/122)

*If approved, this vote would send 200k BAL to a new Ribbon Vault - effectively doubling our allocation towards call writing strategies.*

## Summary
In July 2022 Balancer passed [BIP-24](https://forum.balancer.fi/t/bip-24-allocate-bal-to-a-ribbon-finance-vault/3209/7) which allocates 200K BAL (~$1.3M) to a Ribbon BAL Covered Call treasury vault. The call-writing strategy has significantly outperformed buy-and-hold since inception, earning **221,885.41 USDC** for the Balancer subDAO [treasury](https://etherscan.io/address/0x10a19e7ee7d7f8a52822f6817de8ea18204f2e4f).

Currently, **4.16%** (200K / 4.8M BAL) of the treasury BAL is allocated to the Ribbon vault. We propose to **increase** the allocation of BAL to the vault.
## Motivation
The original rationale for BIP-24 still stands today:
1.  We are still in the midst of a significant bear market both for the price of BAL and for DeFi assets overall. This thesis was validated since BIP-24 8 months ago: BAL has remained range-bound between ~$4.5 - ~$7.8 from July to March (fig. 1).
2.  The DAO wanted to explore ways to bolster stablecoin reserves – indeed the strategy has shown results, earning 221K USDC on $1.3M worth of BAL.

**![](upload://v1E89zbqchEGyfyAfkdFP8Nm5eF.png)**
*Figure 1*


We think it is prudent to increase the allocation **at this time** for the following reasons:
1.  Implied volatility has been picking up recently, thus, selling calls i

====================================================================================================
[4] id=0x398ccb38479bb41ec79a8b2c08e2a5a660aced12aabe4356355966c66603c358  token=BAL  space=balancer.eth  date=2023-04-05
TITLE: [BIP-229] Fund Balancer Grants for Q2 2023
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# Balancer Grants DAO Service Provider Proposal Q2 2023

## Overview

This proposal is to continue Balancer Grants within the Balancer DAO, as an independent community-owned grants program for the Balancer ecosystem as a Service Provider (SP). The program aims to accelerate the development of the BAL ecosystem while optimizing contributor rewards in the Balancer ecosystem. Grants are an alternative pathway for projects aimed at funding smaller, short term or one off projects up to $100k USD that don’t fit the Foundation Service Provider funding model.

The current Balancer Grants team has been working together under the previous [snapshot proposal](https://snapshot.org/#/balancer.eth/proposal/0x8e20d769b9674fbea2f749844525bdddb8afcd874ab8b3aafb17c91a46cf7bca) passed on Jan 9, 2023. To date, the grants program has successfully delivered 7 waves of funding and mentoring, expanding the Balancer ecosystem by encouraging building to increase TVL and bring more quality teams into the Balancer ecosystem. This proposal is to continue the operation of the grants program as per [BIP-76](https://forum.balancer.fi/t/bip-144-fund-balancer-grants-q1-2023/4203/7) and [BIP-144](https://forum.balancer.fi/t/bip-144-fund-balancer-grants-q1-2023/4203).

Only significant changes to the previous proposal are:

1. Co-lead positions changing to Burns as a single lead due to Zen Dragon’s external commitments. Zen Dragon’s contributions as a co-lead have been invaluable to the grants program’s success

====================================================================================================
[5] id=0xcc65b6c599b11446da7074768b99a3a1dcc246705a090f6747f56c0719846a48  token=BAL  space=balancer.eth  date=2023-04-05
TITLE: [BIP-230] Fund the Balancer Maxis for Q2 2023
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/128)

### Introduction

There are some significant changes compared to the last funding proposal and I welcome community feedback as always.

After discussions with other leaders in the ecosystem in the wake of [BIP-149](https://forum.balancer.fi/t/bip-149-funding-proposal-for-silverlight-labs-revised/4241)’s failure to pass it was decided that Maxis should step into the role of project management. This is in addition to Maxis assuming the role of partnerships & business development in Q4. Despite having significantly more responsibilities, we are not raising net compensation, but we are re-assessing how each Maxi is compensated. Please see the following table for monthly salary specifics.



Some Maxis have opted to take some or all of their compensation in liquid BAL for various reasons. While my salary is increasing to reflect the increased importance of Maxis in the ecosystem I will continue to lock 100% and max re-lock my previous salaries. This is to ensure I have skin in the game and remain highly motivated to ensure Maxis execute at a high level in all of our areas of operation. I’ll point out that net USD compensation is decreasing by nearly 3% while net BAL compensation is decreasing 20% to reflect a higher BAL price compared to last quarter.

Additionally, we are requesting an allocation of 1500 BAL to be used for 3rd party dev bounties. This will be led by Tritium as we look to expand the develop

====================================================================================================
[6] id=0xaeaa64d5caccd822bce192ea7463d6ade32883922753cc99382ee63934c27988  token=BAL  space=balancer.eth  date=2023-04-05
TITLE: [BIP-231] Enable USDC-TNGBL 20-80 Gauge with a 2% Emission Cap [Polygon] [second vote]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/128)


**Summary:**

Enable gauge on the TNGBL-USDC 80-20 pool

**References/Useful links:**

• [Website](https://www.tangible.store)

• [Documentation](https://docs.tangible.store/)

• [Github Page](https://github.com/TangibleTNFT)

• [Communities](https://discord.com/invite/zC4WpKhcj2)

• [Twitter](https://twitter.com/tangibleDAO)

**Protocol Description:**

Tangible is an RWA tokenization protocol, that already has several gauges for the protocol's stablecoin USDR.

**Motivation:**

Tangible's governance token TNGBL is a core part of the protocol, with all marketplace fees accruing to the token. In addition to having a claim on 10% of USDR seigniorage.

We have been building up protocol owned liquidity in the 80-20 TNGBL-USDC pool on Polygon and believe now it would be beneficial to add additional incentives via a gauge. This will be the main home for TNGBL liquidity on-chain.

**Specifications:**

1. Governance: TNGBL token holders can lock their TNGBL tokens and receive veNFTs that represent their locked tokens. These NFTs will grant holders governance rights. (Full governance launching soon)
2. Oracles: N/A
3. Audits: [Audits - Tangible](https://docs.tangible.store/real-usd/audits)
4. Centralization vectors: Governance upcoming.
5. Market History: Tangible has been tokenizing RWAs for over 18 months and the TNGBL token has been live for almost 12.
6. Value: Adoption and usage of Balancer's novel 80-20

====================================================================================================
[7] id=0x80f4a0f101ddcfe1b7098f0652a194aa741cc43c0dfccccd714e977cdc8f1150  token=BAL  space=balancer.eth  date=2023-04-05
TITLE: [BIP-235] Enable TEMPLE/DAI 50/50 Gauge with 10% emissions cap [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/128)


> SUMMARY:

This proposal aims to add a new veBAL gauge for a new TEMPLE/DAI 50/50 weighted pool on Ethereum.

> PROTOCOL DESCRIPTION:

TEMPLE is a Treasury value backed token. We chose Balancer to deploy our AMO-styled price defense contract (RAMOS) which paired TEMPLE token to approximately $9mm USD worth of stables initially held in the Balancer USD (bb-a-USD) liquidity pool. The RAMOS contract protected TEMPLE token price from falling below the Treasury stable value backing each token.

**References/Useful links:**

Website: templedao.link

Github Page: github.com/TempleDAO/TempleDAO

Communities: discord.gg/templedao / Twitter: @templedao


> MOTIVATION:

In February of 2023, Balancer Team uncovered a reentrancy vulnerability for the boosted pools and stopped collecting protocol fees for bb-a-USD. Instead of redeploying a fixed bb-a-USD pool using AAVE v2, Balancer Team chose to push for a new boosted pool (bb-e-USD) that deposited stables into Euler. 

At the same time, Temple Protocol was asked by the Balancer Team to switch our token pairing to Euler USD. Wanting to be a good ecosystem partner, we switched TEMPLE to pair against the new bb-e-USD which was subsequently affected in the Euler attack. Since trading was paused in the Euler USD pool, we have been unable to resume TEMPLE trading on Balancer nor reactivate RAMOS.

This proposal aims to add a veBAL gauge for the new TEMPLE/DAI 50/50 we

====================================================================================================
[8] id=0x495c40b72c0bc24173c4ebdfb7ac3986bd3978fcae20bb8b3e3b3d8130b426b4  token=BAL  space=balancer.eth  date=2023-04-05
TITLE: [BIP-237] Enable USH - ETH 50/50 Gauge with 10% emission cap  [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/128)

**Summary:**

Proposal to add gauge support for the newly created unshETH 50/50 USH/ETH pool on Ethereum mainnet.

unshETH’s governance token, USH, has launched on both BNB and Ethereum mainnet. The initial liquidity mining program will end on April 5th. The unshETH team plans to conduct the next liquidity mining program on Balancer, and to expand the collaboration between unshETH and Balancer even further in the future. Moreover, unshETH is integrated with an ecosystem partner, Stargate, that will enable scaling of its liquidity.


**References/Useful links:**

Website - [https://unshETH.xyz/](https://unsheth.xyz/)

Documentation - [https://docs.unshETH.xyz/](https://docs.unsheth.xyz/)

Github Page - [https://github.com/unshETH](https://github.com/UnshETH)

Communities - https://discord.com/invite/5tZXASh5P3

**Other useful links?**

Twitter - [https://twitter.com/unshETH_xyz](https://twitter.com/unsheth_xyz)

Blog - https://mirror.xyz/0x749Dc728A68265e74754Ad8e6cc2649BD42a8f8a


**Protocol Description:**

unshETH is a decentralized, on-chain movement for improving validator decentralization. The Matrix prevents monopolies from growing so large that they stifle innovation and endanger the cryptocurrency economy by morphing into a central point of failure via the creation and enforcement of anti-competitive policies and practices.

Within Ethereum’s DeFi ecosystem, user activities are governed not by l

====================================================================================================
[9] id=0x054fef4115b9a25291bf4addc8ba0d4510504038e15200204cbc6aaef5d30da3  token=BAL  space=balancer.eth  date=2023-04-06
TITLE: [BIP-241] Aave v3 Migration
CHOICES: Yes, let's do it | No, this is not the way
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/128

## Motivation
> With the Aave v3 linear pool wrappers ready for deployment in the ecosystem various Boosted Aave v3 pools and pairings have started to crop up in the governance forum. In order to streamline the process of transitioning from the old Aave v2 pool and pairings I on behalf of the Maxis am proposing we close the loop by voting to kill the relevant gauges this week thereby permitting 3 more weeks of emissions on the pool gauges listed below. This will give LPs enough time to migrate their positions and new pools to bootstrap themselves in the BIP-19 cycles. As an adder, a new STG/bb-a-USD gauge will be activated with the execution of this proposal, along with the old one added to the kill list. The STG/bb-a-USD pool will be killed but the same information applies as in [BIP-105.](https://forum.balancer.fi/t/bip-105-enable-stg-bb-a-usd-gauge-ethereum/3905) 

We will be coordinating with the various bribe marketplaces to ensure all future voting incentives only go towards the new gauges. The old pools listed below will no longer have core pool status. All of the migrated pools will be restored as “core pools” under BIP-19.

## Pools being migrated:
Original deployment -> New pool address

[bb-a-USD](https://app.balancer.fi/#/ethereum/pool/0xa13a9247ea42d743238089903570127dda72fe4400000000000000000000035d) -> [bb-a-USD](https://app.balancer.fi/#/ethereum/pool/0xFEBB0BBF162E64FB9D0DFE186E517D84C395F016000000000000

====================================================================================================
[10] id=0x44a12d4123c0b534d7e9f84bf50f0e1582cb335ab13577ae7d5e7fb6ae55ee17  token=BAL  space=balancer.eth  date=2023-04-13
TITLE: [BIP-250] Enable jAURA - ETH 80/20 Gauge w/10% emissions cap[Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/137

## Summary

This is a proposal to enable a Balancer gauge for the 80% jAURA - 20% ETH pool on Ethereum Mainnet. jAURA is an auto-compounding wrapper token of the low-cost, partner-focused, vlAURA token.

As Aura launches on the Arbitrum Network, we will be using this pool to foster a familiar model that allows for ease of use and high adoption rate of both Balancer and Aura on Arbitrum. In a similar way, we plan on building upon the Balancer and Aura ecosystems through MetaVaults and other future integrations.

This strategy was co-developed alongside Redacted Cartel's Hidden Hand, with mentorship from Aura and Balancer. Special thank you’s to: Lamentations, Json, Sami, Solarcurve and Maha for helping us through ideation and finding equity with the Aura, Balancer, and Redacted communities.

jAURA provides, what we think, is a community service through its super efficient gas and retention structure as well as rebating back to the AURA team to help fund their ecosystem. Every single user who utilizes jAURA supports the AURA team.

## Protocol Description

Jones DAO is a **yield strategy, and liquidity protocol** with vaults that enable 1-click access to DeFi tools. These strategies unlock liquidity and capital efficiency through yield-bearing tokens.

Previously, Jones was focused solely on bringing users interested in Decentralized Options a simple, auto-pilot solution. The protocol has now expanded our focus, and explor

====================================================================================================
[11] id=0x438cb8ec286228bb46435efc9e74a3c4e66040eb39e61f4ec7ee7511ff25b8b0  token=BAL  space=balancer.eth  date=2023-04-13
TITLE: [BIP-252] Timeless 50k BAL Grant Application [ve8020 Program]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[PR with multisig payload](https://github.com/BalancerMaxis/multisig-ops/pull/137)

```
Author(s): @mcfly
Status: BIP
Date Applied: 2023-03-01
Date Updated: 2023-03-13
Date Ratified: yyyy-mm-dd
Vote Start Date: yyyy-mm-dd
Vote End Date: yyyy-mm-dd
BAL grant amount: 50k BAL
```

## Summary
This grant application requests 50k BAL to be awarded to Timeless as a participant in Balancer's program outlined in [BIP-146](https://forum.balancer.fi/t/bip-146-incentivize-8020-bpt-staking-ve8020/4210), which aims to support all systems involving the staking/locking of 8020 BPT. This proposal follows a [successful vote](https://snapshot.org/#/balancer.eth/proposal/0x4c5ffd14f56d2c641a09e752e45b6421323f494d74919212745a65fd1d14d7d0) to enable veLIT gauge on Balancer.


## Why we qualify

- Current ve8020 BPT TVL: $8,548,533
- 90 days fees: $315,129
- Project is [live on Mainnet](https://twitter.com/Timeless_Fi/status/1538997539529142273) since June 2022.
- BAL incentives will go to ve8020 lockers only, as defined in the [BIP-200](https://snapshot.org/#/balancer.eth/proposal/0x4c5ffd14f56d2c641a09e752e45b6421323f494d74919212745a65fd1d14d7d0)
- Project treasury will supply 20% of ETH so that no BAL is sold when locked. cf Timeless snapshot vote [approval](https://snapshot.org/#/timelessfi.eth/proposal/0x0d136b1f8fc363d83bcf591b5e0cfc2c4316e74e280321050f3270af84ab9322).
- TVL exceeds value of 25k BAL by 30x
- Lifetime total revenue earned exceeds ⅓ the value of 25k BAL

More details about Time

====================================================================================================
[12] id=0x0736c3f040d2539c7273f0ca4631c57220e5ca4a3ccc6fca0f77bba6c819852f  token=BAL  space=balancer.eth  date=2023-05-03
TITLE: [BIP-282] Return undesignated BAL tokens from OpCo to the DAO Treasury
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Authors: @Danko8383, @Xeonus and @Tristan345 

## TL;DR

* OpCo currently holds BAL tokens that were previously designated to fulfill vesting obligations with multiple contributors with the frontend team;
* These [BAL tokens are for use under direction of the DAO](https://forum.balancer.fi/t/bip-1-operating-framework-for-balancer-dao/3237/17) and, while governance has approved the transfer of these BAL to OpCo under [[BIP-55]](https://forum.balancer.fi/t/bip-55-funding-proposal-for-the-balancer-opco/3609), we believe that it reflects stronger governance for the tokens to reside in the DAO treasury until further governance vote;
* This proposal requests a vote to return 95,568.88 of undesignated BAL tokens to the Treasury

## Context:

As our ecosystem grows and evolves, it is essential that we take a proactive approach to safeguarding our funds and using them in alignment with our shared objectives in the most effective way possible.

Under [BIP-55], the Balancer OpCo was funded and received 116,678.08 BAL tokens to fulfill grants to its staff. These tokens were intended to serve as compensation for current and future team members, with a 4-year vesting period and a 1-year cliff.

In its first year, OpCo implemented cost-saving measures and did not fully exhaust its budget. Moreover, we believe that it would be preferable for the Treasury to hold custody of these assets until they are required to fulfill the vesting contracts, as per OpCo's frontend team budget requests durin

====================================================================================================
[13] id=0xe9fa0968d93ab117d6ef28d139d19e5d9d728c0ed4c9581e2f7eb8c381e5ff45  token=BAL  space=balancer.eth  date=2023-05-03
TITLE: [BIP-283] Change veBAL USD fee component to the new bb-a-usd that uses Aave V3
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## TL;DR

This proposal changes the USD portion of fees paid out to veBAL lockers from the old version of bb-a-usd  that uses Aave v2 and is in recovery mode to a new pool using Aave v3 and a updated version of the ComposableStableSwap pool.  

The choice of [bb-a-usd V3(0xfebb0bbf162e64fb9d0dfe186e517d84c395f016)](https://app.balancer.fi/#/ethereum/pool/0xfebb0bbf162e64fb9d0dfe186e517d84c395f016000000000000000000000502) as the new fee token was made by the community here: https://forum.balancer.fi/t/rfc-change-vebal-usd-yield-component/4692#looking-for-input-8.  

The change be implemented 3 weeks after the passing of this BIP (May 31st).   Lockers will notice the starting on the Wednesday following the first Fee Processing round after this date (June 14th)

## Note to integrators

This change may require integrators building on top of veBAL, or derivatives of it to make changes. We are trying to reach out to all integrators and inform them of this change, and will ensure that no changes to fee tokens paid out to claim will occur before June 1st.   Please drop a comment here if you have concerns or would like to talk to us about handling this change.


## Background and Context

### Fee Handling at Balancer

veBAL lockers are entitled to 65% of the protocol fees collected by the Balancer Protocol.

For pools designated as [Core Pools](https://forum.balancer.fi/t/bip-19-incentivize-core-pools-l2-usage/3329) these fees are paid out in the form of USDC incentives placed on Hidd

====================================================================================================
[14] id=0xb64a06bbf7a42bb6329a4da81f8dbff48c7f6071becf28b8f9c245a515ef5b7a  token=BAL  space=balancer.eth  date=2023-05-10
TITLE: [BIP-287] Enable UZD/bb-a-USD gauge w/2% emissions cap[Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[PR with multisig payload](https://github.com/BalancerMaxis/multisig-ops/pull/178)
https://github.com/BalancerMaxis/multisig-ops/pull/178

Gauge Proposal Template:

**Summary:**
> This proposal is to add a veBAL gauge for the new UZD/**bb-a-USD** stable pool on Ethereum.
Pool deployed here: 
https://etherscan.io/address/0xeC3626fEe40EF95e7C0CBb1D495C8B67B34D3983
2% capped gauge deployed here: https://etherscan.io/address/0x21cf9324d5b1ac739b7e6922b69500f1eedb52e0

**References/Useful links:**

> •Website: [https://www.zunami.io ](https://www.zunami.io/)
• Twitter: [https://twitter.com/ZunamiProtocol ](https://twitter.com/ZunamiProtocol)
• Documentation: [Introduction - Zunami Protocol Docs ](https://zunamilab.gitbook.io/product-docs/)
• Github Page: [GitHub - ZunamiProtocol/ZunamiProtocol ](https://github.com/ZunamiLab/ZunamiProtocol)
• Communities: [Zunami Protocol](https://discord.com/invite/BnC6kTWkUe)
• Defillama: [Zunami Protocol: TVL and Stats - DefiLlama ](https://defillama.com/protocol/zunami-protocol)
• Snapshot: [Snapshot ](https://snapshot.org/#/zunamidao.eth)

**Protocol Description:**

> Zunami Protocol is a DAO that aims to maximize returns on stablecoins while addressing issues faced by traditional yield farming protocols. The protocol aims to streamline interactions with decentralized finance, making it more cost-efficient and profitable through differentiated fund management strategies. Zunami's main product is the UZD stablecoin, which is designed as a rebas

====================================================================================================
[15] id=0xb7cd04a67e59ba75c1062a1abcc4cae432ecdd6297fdd7ce6abf33e38ec46034  token=BAL  space=balancer.eth  date=2023-05-10
TITLE: [BIP-290] Designate ALCX/ETH 80/20 as a Core Pool (with 10% emissions cap)
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
[Payload with PR](https://github.com/BalancerMaxis/multisig-ops/pull/179)
https://github.com/BalancerMaxis/multisig-ops/pull/179

**Summary:**
> Following the feedback received on the [pre-proposal for a ve8020 grant](https://forum.balancer.fi/t/pre-proposal-vealcx-application-for-ve8020-and-community-grant/4596) for veALCX, including the suggestion that Alchemix consider pursuing designating the 80/20 ALCX/ETH pool as a core Balancer pool, Alchemix has decided that it would like to proceed with pursuing a core Balancer pool designation. Instead of applying for a ve8020 grant and using that voting power for the pool, the core pool designation would mean that the fees earned by the Balancer protocol (excluding the Balancer DAO cut) are used to directly bribe the pool.

>At the same time, this BIP increases the emissions cap of the pool from the current 2% to 10%. The migration of liquidity and incentives from Sushiswap to Balancer is still ongoing but already the pool is almost at the existing emissions cap.

**References/Useful links:**

> Link to:
•[ Website](https://alchemix.fi/)
•[ Documentation](https://alchemix-finance.gitbook.io/user-docs/)
•[ Github](https://github.com/alchemix-finance)
•[ Discord](https://discord.com/invite/alchemix)
•[ Twitter](https://twitter.com/AlchemixFi)
• Other useful links:[ https://alchemix-stats.com](https://alchemix-stats.com)

**Protocol Description:**

> Alchemix is a future-yield-backed synthetic asset protocol that gives users advances

====================================================================================================
[16] id=0x13ff21be0ff540c9bd65b14265e1623cbe6eca8b41d9bb7e9c32fc3931ccb7ea  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-294] Authorize Mimic Smart Vault on Arbitrum
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/194

### Motivation

After BIP-115 passed late last year work began to create Mimic smart vaults that automatically collect protocol fees, sell for USDC, then bridge it back to Ethereum if necessary. The Maxis have recently conducted several tests in collaboration with Mimic, the most recent of which occurred a few days ago. Half of Arbitrum's protocol fees were successfully handled in this test - you can review the [history](https://app.mimic.fi/smart-vaults/arbitrum:0x94Dd9C6152a2A0BBcB52d3297b723A6F01D5F9f7/action-history/) of the Arbitrum smart vault if interested in the details.

Both the Maxis and Mimic have high confidence the Arbitrum smart vault is working as expected and ready to take over the handling of protocol fees on the network. We'll begin running tests on other networks in preparation for authorizing those smart vaults in the near future. In case an issue arises the role for allowing the smart vault to call `withdrawCollectedFees` on the `ProtocolFeeWithdrawer` can be revoked with a future BIP.

### Risks
Assigning  access to the fee collector gives the contracts assigned access to sweep all fees from the collector.  In the very worst case, the fee collector could stop functioning correctly/start leaking funds.  

Manual work is required in the process every 2 weeks to process veBAL fees and core pool bribes.   In the event that there was a significant leak of value from the fee collector,  It could take up

====================================================================================================
[17] id=0xd991e9f3c6edd148bd37c600d7ada3d28db1758e3cfd703c02d290f502906f05  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-295] Fee Discount for CowSwap Solvers
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/195

### Motivation

Balancer contributors have recently been exploring ways to increase non-toxic flow through the protocol. One opportunity which has presented itself is to leverage our close partnership with CowSwap to implement a fee discount when solvers route trades through Balancer liquidity. This would be done by granting the role for calling `setSwapFeePercentage` to the `GPv2Settlement` contract - then solvers would pass in interactions which lower the fee on the pool, execute the swap, then return the fee to the previous value. The swap fee could be lowered in this manner by around 50-75% to enable a significant increase in “good flow” to Balancer pools.

Most of Balancer’s protocol fees are generated from yield rather than swaps. There is a chance this proposal leads to more swap fees but even if it does not, one of the most important goals for the Balancer ecosystem is to grow our DEX volume market share. This is likely one of the best chances we have to move the needle on that on Ethereum.

### Risks

The Maxis will retain the ability to call `setSwapFeePercentage` on all pool factories so if something unexpected happens and fees are dramatically lowered or raised globally by accident it can be fixed very quickly by the Maxis. Governance can also revoke this role at any time in the future through a future BIP.

### Specification

If approved, the DAO Multisig `eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will

====================================================================================================
[18] id=0xbaf65c1626b1e66ea13d26920aa21d8b75f40dc149ff2cbd6972a6c22205a91a  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-297] Enable tBTC/WBTC [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/197

**Summary:**
> Proposal to add gauge support for 50/50 tBTC/WBTC pool on Arbitrum.
<br>Link to pool: [0x542F16DA0efB162D20bF4358EfA095B70A100f9E](https://app.balancer.fi/#/arbitrum/pool/0x542f16da0efb162d20bf4358efa095b70a100f9e000000000000000000000436)
Link to gauge: [0xc4b6cc9A444337b1Cb8cBbDD9de4d983f609C391](https://etherscan.io/address/0xc4b6cc9A444337b1Cb8cBbDD9de4d983f609C391#code)


**References/Useful links:**

> Link to:
    • [Website](https://threshold.network)
    • [Documentation](https://docs.threshold.network/)
    • [Github Page](https://github.com/keep-network/tbtc-v2)    
    • [Communities](https://forum.threshold.network/)
• [Discord](https://discord.com/invite/Threshold)
• [Twitter](https://twitter.com/tBTC_project)


**Protocol Description:**

> tBTC is a decentralized wrapped Bitcoin, that is 1:1 backed by mainnet BTC. 
<br>Unlike other wrapped Bitcoins, the BTC that backs tBTC is not held by a central intermediary, but is instead held by a decentralized network of nodes using threshold cryptography. tBTC is trust minimised and redeemable for mainnet BTC without a centralized custodian. 
<br>tBTC is built with Threshold Network’s decentralized infrastructure, and Ethereum.


**Motivation:**

> This proposal aims to add a veBAL gauge for the Balancer tBTC/WBTC pool on Arbitrum.<br>
Threshold DAO has recently launched a [L2 growth campaign with Wormhole](https://www.coindesk.com/tech/2023/05/11/thre

====================================================================================================
[19] id=0x68c90da5e374c2136935aaaad1c319df67ec4b78e77294d11c2055cab740a004  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-298] Enable tBTC/ETH [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/198

**Summary:**
> Proposal to add gauge support for 50/50 tBTC/ETH pool on Arbitrum.
<br>Link to pool: [0xc9f52540976385A84BF416903e1Ca3983c539E34](https://app.balancer.fi/#/arbitrum/pool/0xc9f52540976385a84bf416903e1ca3983c539e34000200000000000000000434)
Link to gauge: [0xa8D974288Fe44ACC329D7d7a179707D27Ec4dd1c](https://etherscan.io/address/0xa8D974288Fe44ACC329D7d7a179707D27Ec4dd1c)


**References/Useful links:**

> Link to:
    • [Website](https://threshold.network)
    • [Documentation](https://docs.threshold.network/)
    • [Github Page](https://github.com/keep-network/tbtc-v2)    
    • [Communities](https://forum.threshold.network/)
• [Discord](https://discord.com/invite/Threshold)
• [Twitter](https://twitter.com/tBTC_project)


**Protocol Description:**

> tBTC is a decentralized wrapped Bitcoin, that is 1:1 backed by mainnet BTC. 
<br>Unlike other wrapped Bitcoins, the BTC that backs tBTC is not held by a central intermediary, but is instead held by a decentralized network of nodes using threshold cryptography. tBTC is trust minimised and redeemable for mainnet BTC without a centralized custodian. 
<br>tBTC is built with Threshold Network’s decentralized infrastructure, and Ethereum.


**Motivation:**

> This proposal aims to add a veBAL gauge for the Balancer tBTC/ETH pool on Arbitrum.<br>
Threshold DAO has recently launched a [L2 growth campaign with Wormhole](https://www.coindesk.com/tech/2023/05/11/threshold-n

====================================================================================================
[20] id=0xcf116e440ae71ea05502c10930efb90e294af63b1d9333924ef905314f5f7004  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-299] Permissioned arbitrage to recover remaining funds in bb-e-usd
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## Payload
https://github.com/BalancerMaxis/multisig-ops/pull/190

## TL;DR
- Inverse Finance has around bb-e-usd representing around  $300,000 of the  around $320,000  in liquid value still held in bb-e-usd and rightfully owned by remaining bb-e-usd holders.  The inverse bb-e-usd is  in a contract that will not allow them to withdraw using methods so far provided. 
- bb-e-usd and other linear pools will unpause on June 8th as the grace period on the pause window comes to an end.  This will  allow arbitrageurs to drain remaining value from the pool.
- This BIP is a actions a plan to unpause the pools early, and run the arbitrage.
   - Once the exact amount recovered is known, another BIP will be brought forward to proportionally distribute the recovered funds to remaining bb-e-usd holders as of the block of the Arbitrage.
- After this point, bb-e-usd burns will render a value of almost 0 and will in no case be worth the gas.
- Special thanks to TempleDAO for providing the eDAI and eUSDC required to run this process.


## Background/Context

As initially described in [this RFC](https://forum.balancer.fi/t/rfc-bb-e-usd-permissioned-arbitrage-to-rescue-non-withdrawn-funds/4744).   There is still a significant amount of value left in bb-e-usd, a vast majority of which belongs to Inverse Finance.  

Since the time of the RFC posted above,  The Balancer Maxis have spent time working with TempleDAO, Euler, and Inverse to ensure that all required conditions are met on-chain to run th

====================================================================================================
[21] id=0x55a627c4efda395fc03c1ba908b01c0832d897e9248c619293ecdf7835cec469  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-301] Return undesignated BAL tokens from (Orb) to the DAO Treasury
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
TL;DR

* OpCo currently holds BAL tokens that were previously designated to fulfill vesting obligations with multiple contributors with Orb team (including previous BLabs employees and future agreements);
* These [BAL tokens are for use under direction of the DAO ](https://forum.balancer.fi/t/bip-1-operating-framework-for-balancer-dao/3237/17) and, while governance has approved the transfer of these BAL under [BIP-38](https://forum.balancer.fi/t/bip-38-request-for-bal-allocation-to-orb-collective/3545), we believe that it reflects stronger governance for the tokens to reside in the DAO treasury until further governance vote;
* This proposal requests a vote to return 153,915 of undesignated BAL tokens to the Treasury

## Context:

As our ecosystem grows and evolves, it is essential that we take a proactive approach to safeguarding our funds and using them in alignment with our shared objectives in the most effective way possible.

Under [BIP-38](https://forum.balancer.fi/t/bip-38-request-for-bal-allocation-to-orb-collective/3545), Orb Collective was funded 398,527 BAL tokens to fulfill grants to its staff. These tokens were intended to serve as compensation for "current and future team members", with a 4-year vesting period and a 1-year cliff. These funds are currently being held at OpCo's wallet, acting as an agent of the DAO.

In its first year, Orb implemented cost-saving measures and staff reduction, not fully exhausting its budget. According to this [BAL Inventory breakdo

====================================================================================================
[22] id=0x1aa212139d722754263a6f64806f9b6bc9019f8a6adfd33765c411432ee67eab  token=BAL  space=balancer.eth  date=2023-05-18
TITLE: [BIP-302] Enable 80ARCH20wETH Gauge w/ 2% emissions cap [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
https://github.com/BalancerMaxis/multisig-ops/pull/199

**Summary:**
This proposal aims at enabling BAL emissions into 80ARCH20WETH to incentivize liquidity and scale the ARCH token in an efficient way.

**References/Useful links:**
    • [Website](https://archimedesfi.com/)
    • [Documentation](https://docs.archimedesfi.com/)
    • [Github Page](https://github.com/thisisarchimedes/Archimedes_Finance)
    • [Twitter](https://twitter.com/ArchimedesFi)

**Protocol Description:**
Archimedes Finance is a novel lending and borrowing marketplace. It is designed to a) attract capital by offering top of market native and sustainable real yield to lenders, b) allow borrowers to create leveraged positions of up to x10 on yield-bearing strategies, and c) enable partner protocols to attract sustainable long-lasting capital.

The project is currently starting its Governance process and the 80ARCH20WETH Balancer Pool [https://app.balancer.fi/#/ethereum/pool/0xdf2c03c12442c7a0895455a48569b889079ca52a000200000000000000000538] is a critical piece of this process as the best option to deepen liquidity of ARCH, the project’s governance and utility token.

The Archimedes Core team is currently focusing on developing its V2, which will include:
1. New yield strategies besides LP and Leverage
2. Liquidity solution for leverage partners
3. Additional utility for ARCH
4. Potentially new chains, such as Arbitrum

**Motivation:**
Archimedes needs a liquidity pool with it's governance token to support

====================================================================================================
[23] id=0xfed6a4bb00b05c8b21db43bf12e459369d86a3371e964374575564e50fce355b  token=BAL  space=balancer.eth  date=2023-05-24
TITLE: [BIP-303] Grant Polygon zkEVM Permissions
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## [Payload PR - BIP-303](https://github.com/BalancerMaxis/multisig-ops/pull/201)

## Background
The goal of this BIP is to grant all necessary permissions on Polygon zkEVM for the network to be fully functional and up to par with Balancer's other networks. This is accomplished through four parts:

303 (zkevm.json) grants all necessary permissions for Balancer's infrastructure to operate
303A sets protocol fee on swaps and yield to 50%
303B enables the child chain gauges to operate
303C enables the authorizer wrapper
## English Specification

The transaction details were generated by [this script](https://github.com/BalancerMaxis/multisig-ops/blob/main/action-scripts/gen_add_permissions_payload.py) with inputs and outputs in [this directory](https://github.com/BalancerMaxis/multisig-ops/tree/staging/BIPs/BIP-303)

The following files can be found both linked below and in the payload PR linked above:


| Filename                                                                                                                             | Description of Contents                                                                                                              |
|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| [inputs.json](https://github.com/Balanc

====================================================================================================
[24] id=0x323af07cd370c70033320bb544ce9394965d28f991ef67c672e781c1e1d5b18b  token=BAL  space=balancer.eth  date=2023-05-24
TITLE: [BIP-304] Enable DFX/ETH Gauge with 2% emissions cap [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### [PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/207)

Gauge Proposal Template:

**Summary:**
> DFX Finance's proposal to add a gauge for the DFX/ETH 50/50 on Arbitrum

**References/Useful links:**

> Link to:
    • Website: [Main Website](https://dfx.finance/), [dApp](https://app.dfx.finance/)
    • Documentation: [Gitbook](https://docs.dfx.finance/), [Medium](https://medium.com/@dfxfinance)
    • Github Page: [Github](https://github.com/dfx-finance)
    • Communities: [Discord](https://discord.dfx.finance/)

**Protocol Description:**

> DFX Finance is a decentralized foreign exchange (FX) protocol that facilitates the seamless exchange of fiat-backed stablecoins denominated in a growing number of currencies. Using a hyper-efficient AMM, optimized for low volatility trading, DFX provides FX swaps with rates that will beat any bank, money changer, or FX platform. DFX Pools currently have over $40M in TVL. DFX is the governance token of DFX Finance which allows users to vote on protocol changes and initiatives of the DAO, and also allows users to receive boosted emissions on deposits within the DFX ecosystem.

**Price History DFX:**

>Price History for DFX can be found on [Coingecko](https://www.coingecko.com/en/coins/dfx-finance)

**Motivation:**

> The DFX/ETH 50/50 needs incentivization to migrate meaningful amounts of liquidity over to the Balancer ecosystem on Arbitrum, and to bring higher trading volumes to Balancer. As well, DFX Finance is commit

====================================================================================================
[25] id=0xd24e07b8444ee2b67ef4a44cfe5775aa53ed634d5d17661f27d73eba6eecdf26  token=BAL  space=balancer.eth  date=2023-05-31
TITLE: [BIP-314] - Funding Proposal For Beethoven X DAO - Marketing
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payloads
https://github.com/BalancerMaxis/multisig-ops/pull/225

**Service Provider Name:** Beethoven X DAO - Marketing

**Core Contributor(s):** JediRasta, Naly, Jeff, Vee, Skly, Tom, Josey, Ardordo

**Pledge to abide by the DAO's [Code of Conduct](https://www.notion.so/balancergrants/Code-of-Conduct-fef15e2ed1f5453f8bd56f338c70bb88) (or link to your own):** Yes

**Pledge to abide by the [Accountability Guidelines](https://www.notion.so/balancergrants/Accountability-Guidelines-229d93372403415688f8d3dc4cb964b1):** Yes

**Introduction & Domains of Operation:**

After a three-month trial contract facilitated by Balancer Labs, the Balancer community [passed](https://snapshot.org/#/balancer.eth/proposal/0x686cfe15ffd35178814276eaff348b791bfd8fd1684e2731f222e9881df61279) [BIP-254](https://forum.balancer.fi/t/bip-254-funding-proposal-for-beethoven-x-dao/4652) to fund Beethoven X DAO as an official Service Provider from May 1, 2023 - July 31, 2023.

Shortly after the ratification of BIP-254, Orb Co. [relinquished its responsibilities of all marketing-related work](https://forum.balancer.fi/t/orb-collective-april-2023-high-level-updates/4735) and has since [released all marketing personnel](https://forum.balancer.fi/t/orb-collective-updated-q2-budget-forecast-5-12-23/4775). These actions created a void wherein a critical service essential for the Balancer ecosystem ceased to exist almost overnight.

In order to ensure a smooth transition and mitigate any harm to the Balan

====================================================================================================
[26] id=0x080aff473f1c6c096e96897830e82a4569b5865f22329cfcef586b3889759076  token=BAL  space=balancer.eth  date=2023-06-07
TITLE: [BIP-317 Enable baoETH/ETH gauge w/2% emissions cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### [PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/250)

> This proposal aims to approve the creation of a gauge with a 2% cap for baoETH/ETH Composable stable pool.
> Bao intends to continue to build on their locked BAL position as well as incentivize voters to vote for the pool, and seed liquidity in the pool
> The baoETH/ETH Balancer pool will act as a base pool for Bao ETH liquidity gauges and will have incentivised liquidity on the Bao platform beginning BAO/baoETH-ETH and bETH/baoETH-ETH

**References/Useful links:**

> Link to:
>
>
>
> * Website: [https://app.bao.finance/ ](https://app.bao.finance/)
> * Documentation: [Bao Finance - Bao Finance Docs ](https://info.bao.finance/docs/)
> * Github Page• [Bao.Finance · GitHub](https://github.com/baofinance)
> * Communities• [Bao Finance](https://discord.com/invite/BW3P62vJXT), https://twitter.com/BaoCommunity

**Protocol Description:**

> Bao Finance is a community-run protocol creating synthetic assets and markets for any data. Our synths, baoUSD and baoETH, are backed by debt positions created in our vaults, and stable assets via its PSM.
>
>
>
> BaoETH is minted by whitelisted contracts, which currently are “the fed” and “the ballast”. The Bao multisig has control over which contracts are whitelisted. Changes are approved via governance.
>
>
>
> The fed mints baoETH into our vaults, ready to be borrowed against highly liquid collaterals. Controlling the borrowable supply also affects the variable lo

====================================================================================================
[27] id=0x20df1e5e328764e55926a17d407555b73da28b60ade8fb6feea34186ab920c0a  token=BAL  space=balancer.eth  date=2023-06-07
TITLE: [BIP-318] Grant Avalanche Permissions
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## [Payload PR - BIP-318](https://github.com/BalancerMaxis/multisig-ops/pull/246)

## Background
The goal of this BIP is to grant all necessary permissions and perform various "start up" actions to bring Avalanche up to par with Balancer's other networks ahead of our upcoming launch.

BIP-318 grants all base permissions for the network to operate
BIP-318A sets the protocol fee on swaps and yield to 50%
BIP-318B adds the child chain gauge factory to the pseudo minter to allow the L2 gauges to emit BAL
BIP-318C enables the authorizer wrapper
BIP-318D adds the avalanche root gauge factory to the gauge adder v4

Note, there will be upcoming governance to enable layer zero boosts on Avalanche and zkEVM.
## English Specification

The transaction details were generated by [this script](https://github.com/BalancerMaxis/multisig-ops/blob/main/action-scripts/gen_add_permissions_payload.py) with inputs and outputs in [this directory](https://github.com/BalancerMaxis/multisig-ops/tree/staging/BIPs/2023-W23/BIP-318)

The following files can be found both linked below and in the payload PR linked above:

| Filename                                                                                                                             | Description of Contents                                                                                                              |
|-----------------------------------------------------------------------------------------------------------------------

====================================================================================================
[28] id=0xbf403ada1645b0918252deb6fd37949ddd5594b4ced505e78b7d930e1163f18a  token=BAL  space=balancer.eth  date=2023-06-08
TITLE: [BIP-322] Allocate Balancer’s 3M ARB
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Motivation 

As part of the Arbitrum token launch [Balancer DAO was allocated ~3M ARB tokens ](https://docs.google.com/spreadsheets/d/e/2PACX-1vSSAzkIIJqw4WGKCF9gXFUkQojTt6weQTExZYmp3YRIR2TUjir9N8nh8xg7gQ2wuPA8mJKL2neL--to/pubhtml). While spending some to accelerate our growth certainly makes sense I believe it’s prudent to retain the majority as a long term bet on Arbitrum’s future. Balancer has seen promising early signs of momentum on Arbitrum like the launch of wstETH, rETH, Aave v3 boosted pools, and the adoption of ve8020 by two Arbitrum native projects (y2k and Radiant). Future catalysts like Aura going multichain, bridging over more rate providers like cbETH, and gyroscope's ECLP put us in a strong position to potentially become the top DEX on Arbitrum.

**I suggest allocating 1M ARB towards direct LP incentives as this is the most direct growth mechanism in my view.**

The USD amount of bribes placed has fallen significantly in line with the decline in BAL & AURA prices. If we use ARB to bribe I believe we’ll only accelerate the reduction in 3rd party bribing activity as we push the ROI closer to 1:1. I’d argue this leads to no gain at all for voters and would be a waste of 1M ARB.

Directly emitting ARB on the pools seems to be a better option as that increases the amount of emissions up for grabs, thus pushing the ROI for bribers up rather than down. Of course this program is limited to incentivizing Arbitrum pools so it is fair to say only the ROI for Arbitrum

====================================================================================================
[29] id=0xa0bfc9d0f19a420ced9bffd69c93acb1b3b8fea6f6b9590574ca0b48cbca4cd0  token=BAL  space=balancer.eth  date=2023-06-14
TITLE: [BIP-323] Authorize Mimic Smart Vaults on Optimism & Polygon
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### [PR with Payloads](https://github.com/BalancerMaxis/multisig-ops/pull/255)

### Motivation

After BIP-115 passed late last year work began to create Mimic smart vaults that automatically collect protocol fees, sell for USDC, then bridge it back to Ethereum if necessary. The Maxis have recently conducted several tests in collaboration with Mimic and the Arbitrum smart vault is already fully operational after [BIP-294](https://forum.balancer.fi/t/bip-294-authorize-mimic-smart-vault-on-arbitrum/4779). 

Tests have been completed in the Polygon and Optimism smart vaults. Both the Maxis and Mimic have high confidence all is working as expected. In case an issue arises the role for allowing the smart vault to call `withdrawCollectedFees` on the `ProtocolFeeWithdrawer` can be revoked with a future BIP.

### Risks

Assigning access to the fee collector gives the contracts assigned access to sweep all fees from the collector. In the very worst case, the fee collector could stop functioning correctly/start leaking funds.

Manual work is required in the process every 2 weeks to process veBAL fees and core pool bribes. In the event that there was a significant leak of value from the fee collector, It could take up to 2 weeks to notice, and then up to an additional week to enact governance to revoke rights to the fee collector.

As a result, there is some risk that up to 3 weeks of protocol fees could be lost. 

Here is a link to [Mimics audits](https://docs.mimic.fi/miscellaneous/sec

====================================================================================================
[30] id=0x67d6569aaa12e00a76622d1ce7f4d14e141b41d49b15cc13c9ba6f1bd3a3764a  token=BAL  space=balancer.eth  date=2023-06-14
TITLE: [BIP-332] Reallocate wstETH/wETH Protocol Fees
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
---

title: [BIP-XX] Reallocate wstETH/wETH Protocol Fees
author: @Llamaxyz - TokenLogic
created: 2023-06-06

---

# Summary

This publication presents the Balancer community an opportunity to bootstrap the wstETH/bb-a-wETH pool by redirecting protocol fees used for bribes from wstETH/wETH to wstETH/bb-a-wETH pool.

# Abstract

This publication proposes reallocating the bribe portion of Protocol Fees from the wstETH/wETH pool to the wstETH/bb-a-wETH pool. If the pool was fully migrated, the yield from the Aave wETH Linear Pool (bb-a-wETH) will provide the following benefits:

* Additional yield for Liquidity Providers (approx. 1.2%)
* Boost the Hidden Hand bribe flywheel (approx. 50%)
* Generate additional revenue for Balancer DAO ($0.26M)

Assuming 95% of the 32,060 wETH are deposited into Aave v3 earning 2.41%, Balancer DAO is expected to earn an additional $0.26M in additional annual revenue.

# Motivation

The wstETH/wETH pool is a "core pool" under BIP-19 with 50% of the pool generating yield. This means 32.5% of yield generated by this pool is then used for bribing votes on Hidden Hand. 

This publication proposes redirecting the bribe portion of the protocol fees towards the wstETH/bb-a-wETH pool. The wstETH/bb-a-wETH pool replaces the wETH with bb-a-wETH and generates additional yield and revenue for Liquidity Providers (LP) and Balancer DAO respectively. 

If 95% of the 32,060 wETH in the wstETH/wETH pool was deposited into Aave v3 via bb-a-wETH to earn [2.41%](https

====================================================================================================
[31] id=0x345e0618bd258a0f79ae05afe8097533f7a0142f250aced1146c123698e8a9dc  token=BAL  space=balancer.eth  date=2023-06-14
TITLE: [BIP-334] Fee Discount for 1inch Labs Solver
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### [PR with Payloads](https://github.com/BalancerMaxis/multisig-ops/pull/263)

### Motivation

Balancer contributors have recently been exploring ways to increase non-toxic flow through the protocol. In the wake of BIP-295’s approval discussions have been in progress with 1inch to bring this discount to 1inch Fusion. This would be done by granting the role for calling `setSwapFeePercentage` to the 1inch Labs settlement contract - then they would pass in interactions which lower the fee on the pool, execute the swap, then return the fee to the previous value. The swap fee could be lowered in this manner by up to 80% to enable a significant increase in “good flow” to Balancer pools.

Since Fusion is also available on L2’s we can extend this discount to Arbitrum and Polygon as well.

Most of Balancer’s protocol fees are generated from yield rather than swaps. There is a chance this proposal leads to more swap fees but even if it does not, one of the most important goals for the Balancer ecosystem is to grow our DEX volume market share. This is likely one of the best chances we have to move the needle on that.

### Risks

The Maxis will retain the ability to call `setSwapFeePercentage` on all pool factories so if something unexpected happens and fees are dramatically lowered or raised globally by accident it can be fixed very quickly by the Maxis. Governance can also revoke this role at any time in the future through a future BIP.

### Specification

#### Ethereum
If approved, t

====================================================================================================
[32] id=0xedeefde67a4dbf9ee51c50dbfc5feb156bd53d103bf08962dfc07d81887c8325  token=BAL  space=balancer.eth  date=2023-06-22
TITLE: [BIP-336] Enable uniETH/wETH Gauge [Ethereum] w/ 2% emissions cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### [PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/286)

**Summary**

Proposal to add gauge support for uniETH-wETH composable stable pool with a 2% emissions cap.

uniETH is an institutional friendly liquid staking token that represents ETH staked in Bedrock plus all future rewards from staking. There is more than USD3.7mil ETH staked at the time of writing.

**Protocol Description**

Bedrock's native tokenized version of staked Ether is known as uniETH.

uniETH represents the staked ETH in Bedrock plus all future staking rewards. uniETH is non-rebasing, i.e. does not grow in quantity over time but grows in value instead. In other words, 1 uniETH will be worth more than 1 ETH as time goes on, and its value will continue to increase as more time passes. uniETH’s non-rebasing model allows users to hold uniETH on centralized exchanges and use it in decentralized financial applications seamlessly.

Launched by RockX, Bedrock is a non-custodial solution that satisfies the requirements of institutions seeking a basis for large-scale liquid staking. By bringing new levels of transparency and security to liquid staking, Bedrock allows institutions to unlock liquidity safely by adhering to regulations while leveraging a true crypto-native solution.

References/Useful links

[[uniETH DApp](https://bedrock.rockx.com/unieth/stake)]
[[Learn more about uniETH](https://bedrock.rockx.com/unieth)]
[[uniETH audit report](https://github.com/RockX-SG/stake/blob/main/PeckSh

====================================================================================================
[33] id=0xc59ebe5c9ba238dfae21f048b6bb1ed7ecee8d52bdd5c5b92b787d61eed1980d  token=BAL  space=balancer.eth  date=2023-06-22
TITLE: [BIP-342] Reallocate wstETH/wETH Protocol Fees [second vote]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
---

title: [BIP-XX] Reallocate wstETH/wETH Protocol Fees
author: @Llamaxyz - TokenLogic
created: 2023-06-06

---

# Summary

This publication presents the Balancer community an opportunity to bootstrap the wstETH/bb-a-wETH pool by redirecting protocol fees used for bribes from wstETH/wETH to wstETH/bb-a-wETH pool.

# Abstract

This publication proposes reallocating the bribe portion of Protocol Fees from the wstETH/wETH pool to the wstETH/bb-a-wETH pool. If the pool was fully migrated, the yield from the Aave wETH Linear Pool (bb-a-wETH) will provide the following benefits:

* Additional yield for Liquidity Providers (approx. 1.2%)
* Boost the Hidden Hand bribe flywheel (approx. 50%)
* Generate additional revenue for Balancer DAO ($0.26M)

Assuming 95% of the 32,060 wETH are deposited into Aave v3 earning 2.41%, Balancer DAO is expected to earn an additional $0.26M in additional annual revenue.

# Motivation

The wstETH/wETH pool is a "core pool" under BIP-19 with 50% of the pool generating yield. This means 32.5% of yield generated by this pool is then used for bribing votes on Hidden Hand. 

This publication proposes redirecting the bribe portion of the protocol fees towards the wstETH/bb-a-wETH pool. The wstETH/bb-a-wETH pool replaces the wETH with bb-a-wETH and generates additional yield and revenue for Liquidity Providers (LP) and Balancer DAO respectively. 

If 95% of the 32,060 wETH in the wstETH/wETH pool was deposited into Aave v3 via bb-a-wETH to earn [2.41%](https

====================================================================================================
[34] id=0x635181c301e6608ab9ff5bdfc86ca8aad6857a984f4905a7fae649153370a622  token=BAL  space=balancer.eth  date=2023-07-05
TITLE: [BIP-350] Balancer Grants DAO Service Provider Proposal Q3 2023
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### [PR with Payload](https://github.com/BalancerMaxis/multisig-ops/pull/333)

## Overview

This proposal is to continue Balancer Grants within the Balancer DAO, as an independent community-owned grants program for the Balancer ecosystem as a Service Provider (SP). The program aims to accelerate the development of the BAL ecosystem while optimizing contributor rewards in the Balancer ecosystem. Grants are an alternative pathway for projects aimed at funding smaller, short term or one off projects up to $100k USD that don’t fit the Foundation Service Provider funding model.

The current Balancer Grants team has been working together under the previous [snapshot proposal](https://snapshot.org/#/balancer.eth/proposal/0x398ccb38479bb41ec79a8b2c08e2a5a660aced12aabe4356355966c66603c358) passed on Apr 10, 2023. To date, the grants program has successfully delivered 8 waves of funding and mentoring, expanding the Balancer ecosystem by encouraging building to bring more quality teams into the Balancer ecosystem, increase TVL and build useful tooling for developers, LPs and ecosystem projects. This proposal is to continue the operation of the grants program as per [BIP-229](https://forum.balancer.fi/t/bip-229-fund-balancer-grants-for-q2-2023/4563).

Changes to the previous proposal are:

1. Increase lead (Burns) comp by $1k USDC due to removal of Baller coordinape circle. Note this represents a net reduction of total compensation. Being the most significant compensation we think it is

====================================================================================================
[35] id=0x42c6aa9444292fb9d9ee3f0045e851781e5fafd794f388e7422bf1ab2803c4d6  token=BAL  space=balancer.eth  date=2023-07-12
TITLE: [BIP-353] Grant Permissions for Composable Stable Pool Factory v5
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## [Payload PR - BIP-353](https://github.com/BalancerMaxis/multisig-ops/pull/358)

## Background
The [v5 Composable Stable Pool Factory](https://github.com/balancer/balancer-deployments/tree/master/tasks/20230711-composable-stable-pool-v5)  were deployed to fix issue reported by a whitehat and requiring many CSPv4 pools to be put in recovery mode.  A full disclosure about the issue will be posted by Balancer Labs once they have wrapped up the ImmuniFi process(paid out). Some initial "wire-up" of permissions is required to bring them into standard function.  This BIP lays out these changes and requests permission to apply them.

## English Specification

The transaction details were generated by [this script](https://github.com/BalancerMaxis/multisig-ops/blob/main/action-scripts/gen_add_permissions_payload.py) with inputs and outputs in [this directory](https://github.com/BalancerMaxis/multisig-ops/tree/staging/BIPs/2023-W28/BIP-353)

The following files can be found both linked below and in the payload PR linked above:

| Filename                                                                                                                             | Description of Contents                                                                                                              |
|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------

====================================================================================================
[36] id=0xaed8caaffc512f6acdaf473993a4faabcbfee0bf35ef6cdc07a98724b61101d9  token=BAL  space=balancer.eth  date=2023-07-12
TITLE: [BIP-362] Restructure the Joint Balancer / Beethoven X Deployment on Optimism
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Authors: Beethoven X contributors (composers and music directors)

This proposal presents an opportunity to position Balancer and Aura as the leading forces of technology on Optimism. It aims to seize the upcoming launch of Aura to leverage cross-chain Balancer boosts, restructures the network's liquidity, and propel Balancer, Beethoven X, and Aura toward increased market dominance. This proposal seeks to do so by proposing a modified protocol fee structure and core pool framework, similar to other successful Balancer deployments.

**Background and Motivation**

Optimism's bedrock upgrade has transformed the Superchain thesis into reality. With the impending Base Launch and the continuous development of the OP stack, we believe Optimism is poised to attract greater attention and liquidity. With the launch of Aura, these developments present an opportunity to cement the joint Balancer and Beethoven X deployment as a core technology and liquidity host on the network.

Since the approval of the Beethoven X friendly fork of Balancer in November 2021, the partnership between the two protocols has flourished into a truly unique relationship. Nowhere else in DeFi has a fork become an essential SP of the original protocol. For the last year, we have recognized we are stronger when we work together, pushing the boundaries of what we can achieve and building a better ecosystem along the way. If we look back, the joint Optimism deployment was the pivotal milestone in the expanding relat

====================================================================================================
[37] id=0x2dd7639d8bfafde08e8e5820c9c6f12b914b235853e079f9093f42731975cd7d  token=BAL  space=balancer.eth  date=2023-07-13
TITLE: [BIP-365] Migrate Affected Composable Stable Pools Wave 1
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
**PR with Payload:**
https://github.com/BalancerMaxis/multisig-ops/pull/374

#### Summary:
This proposal will migrate several gauges affected by the fee collection issue mentioned [here](https://twitter.com/Balancer/status/1672635756005957633). The gauges encompassed in this proposal will be migrated to new Composabel Stable Pools (version 5) and kill the gauges of the earlier versions that are exposed to the fee collection problem mentioned. These pools are critical to Balancer's core liquidity and is why they will be migrated in this first wave. An additional wave will follow next week for additional. These pools were all core pools in their prior version, and will be so in their new implementation. The new gauges will be added upon this proposal passing (ASAP) and the gauges to be killed will be killed the week of July 31st for the new pool incentives to fully be established by the BIP-19 flywheel.

#### Motivation:

By migrating to these new pools Balancer LP's are in a safe position while protocol fees can still be collected by the DAO. While no funds are at risk in the current state, the migration will once again enable the core pool cycle and protocol fee collection.
#### Gauge migration table

|Pool Name|Network|Root Gauge to be Killed|New Pool Address|New Root Gauge Address|
|---|---|---|---|---|
|wstETH-rETH-sfrxETH-BPT|1|0xA2a9Ebd6f4dEA4802083F2C8D08066A4e695e64B|0x42ED016F826165C2E5976FE5BC3DF540C5AD0AF7|0x0021e01B9fAb840567a8291b864fF783894EabC6|
|bb-a-USD|1|0x00

====================================================================================================
[38] id=0x6f106532ad9c5dc1b702d3e36e0066fc0f3732ae4080a64201ab2cef66b6e024  token=BAL  space=balancer.eth  date=2023-07-19
TITLE: [BIP-366] Migrate Affected Composable Stable Pools Wave 2
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payloads
https://github.com/BalancerMaxis/multisig-ops/pull/379

#### Summary:

This proposal will migrate the remaining gauges affected by the fee collection issue mentioned [here](https://twitter.com/Balancer/status/1672635756005957633). The gauges encompassed in this proposal will be migrated to new Composable Stable Pools (version 5) and kill the gauges of the earlier versions that are exposed to the fee collection problem mentioned. These pools are crucial to Balancer’s core and supplemental liquidity and is why they will be migrated in this second wave. These pools were all core pools in their prior version, and will be so in their new implementation. The new gauges will be added upon this proposal passing (ASAP) and the gauges to be killed will be killed the week of August 7th for the new pool incentives to fully be established by the BIP-19 flywheel. Any emissions caps which were in place are respected by this proposal.

#### Motivation:

By migrating to these new pools Balancer LP’s are in a safe position while protocol fees can still be collected by the DAO. While no funds are at risk in the current state, the migration will once again enable the core pool cycle and protocol fee collection.

#### Gauge migration table

|Pool Name|Network|Root Gauge to be Killed|New Pool Address|New Root Gauge Address|
|---|---|---|---|---|
|bb-i-USD|1|0x33BcAa8A390e6DcF2f18AE5fDd9e38fD248219eB|0x9b692f571b256140a39a34676bffa30634c586e1|0xE35f0152f0d49fE8E386E5c42B656321f

====================================================================================================
[39] id=0x627c89289a3f29b4de9fa3479657a0a884590d6d705460fca5ca77de88409491  token=BAL  space=balancer.eth  date=2023-07-19
TITLE: [BIP-368] Allocate Incentives towards Avalanche Launch
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
#### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/381

### Introduction

Balancer contributors are working towards a likely Avalanche launch at the end of July or early August in accordance with [BIP-206](https://forum.balancer.fi/t/bip-206-deploy-balancer-to-avalanche/4449). The purpose of this RFC is to explore the possibility of Balancer allocating funds from the treasury towards incentives in the post launch period. My initial recommendation is to **allocate 100k USDC from the Treasury towards 12 weeks of incentives, to be matched 1:1 on a USD basis by Ava Labs.** Balancer Maxis and Ava Labs might decide to make changes to the allocation during the program based on conversations with partners. This is an RFC so everything is up for discussion.

### Why Incentivize Avalanche

Avalanche already has an established ecosystem with Aave v3 as the top protocol by TVL and several LST’s (sAVAX by BenQi, ankrAVAX, yyAVAX by Yield Yak, ggAVAX by GoGoPool), with sAVAX having nearly $100M TVL. This is a significant benefit because these are strong yield sources we can tap into. With optimized stable pools and enough starting incentives we can establish Balancer as the main LST and USDT<>USDC trading venue. Longer term our primary goals will be to source ve8020 integrations and encourage the growth of additional LST integrations - projects like Pendle and Raft plus Aave v3 listings for example.

BenQi, Ankr, Yield Yak, and GoGo Pool have all signaled their interes

====================================================================================================
[40] id=0x84c1b49554403f57a0dc602b7e13a654fc0a4fa175957b0f01a8bfb35cb7d6de  token=BAL  space=balancer.eth  date=2023-07-19
TITLE: [BIP-369] Grant CSPv5 Swap Fee Permissions to Cowswap & 1inch Labs Solver
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payloads
https://github.com/BalancerMaxis/multisig-ops/pull/382

### Motivation 

To continue the experiment started in BIP-295 and BIP-334 this will grant the role for calling `setSwapFeePercentage` on the recently released composable stable pool factory v5 to the GPv2 Settlement contract (cowswap) and the 1inch Labs Solver.

### Specification

#### Ethereum
If approved, the DAO Multisig `eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will interact with the Authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` and call `grantRole` twice with the following arguments:

Role: `0x42bc3b76ebdb675c6f7836b464d27c7517e14b05dc08bb944a4837563fc805ca`

Account: `0xad3b67bca8935cb510c8d18bd45f0b94f54a968f`

Which corresponds to the address for 1inch Labs’ Fusion resolver.

Role: `0x42bc3b76ebdb675c6f7836b464d27c7517e14b05dc08bb944a4837563fc805ca`

Account: `0x9008D19f58AAbD9eD0D60971565AA8510560ab41`

Which corresponds to the address for Cowswap’s `GPv2Settlement` contract 


#### Polygon
If approved, the DAO Multisig `matic:0xeE071f4B516F69a1603dA393CdE8e76C40E5Be85` will interact with the Authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` and call `grantRole` with the following arguments:

Role: `0x8e9ee99533bd178c1573e352145db0eeb33e8722b92d1d6fbc1de799b41f180c`

Account: `0xad3b67bca8935cb510c8d18bd45f0b94f54a968f`

Which corresponds to the address for 1inch Labs’ Fusion resolver.

#### Arbitrum

If approved, the DAO Multisig `arb1:0xaF23DC5983230E9eEAf93280e312e

====================================================================================================
[41] id=0x2f01469c72830d1e2b54075ab8219c9e8d806e3e0b5215ac7a3264344a83163f  token=BAL  space=balancer.eth  date=2023-07-19
TITLE: [BIP-370] Reallocate bb-a-USD Protocol Fees to GHO/bb-a-USD Fees
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
---

title: [BIP-XXX] Reallocate bb-a-USD Protocol Fees to GHO/bb-a-USD Fees
author: @TokenLogic
created: 2023-07-11

---

# Summary

This publication presents the Balancer community an opportunity to bootstrap the GHO/bb-a-USD pool by redirecting protocol fees used for bribes from bb-a-USD to GHO/bb-a-USD pool.

# Abstract

This publication proposes reallocating the bribe portion of Protocol Fees from the bb-a-USD pool to the GHO/bb-a-USD pool. The goal is for Balancer to become the home for GHO by granting GHO the best possible start and hosting the deepest liquidity pools. 

# Motivation

The bb-a-USD pool is a "core pool" under BIP-19 with 100% of the pool generating yield. This means 32.5% of yield generated by this pool is then used for bribing votes on Hidden Hand. 

This publication proposes redirecting the bribe portion of the protocol fees towards the GHO/bb-a-USD pool.

# Specification

The bribe portion of the ProtocolFee from bb-a-USD is to be redirected to bribes for GHO/bb-a-USD.

Pools:

* [bb-a-USD](https://app.balancer.fi/#/ethereum/pool/0xfebb0bbf162e64fb9d0dfe186e517d84c395f016000000000000000000000502)
* [GHO/bb-a-USD]() - Soon

# Disclosure

This proposal is the sole work of Matthew Graham and Dydymoon from TokenLogic. This proposal has been funded via the Butter Delegation Campaign.

Details on TokenLogics delegation platform can be found [here](https://governance.aave.com/t/tokenlogic-delegate-platform/12516).

# Copyright

Copyright and related rights

====================================================================================================
[42] id=0xc2d6cdccb791c50cb7099892c1b7e42dd613e95372fcc1c961fa1c704bf5f956  token=BAL  space=balancer.eth  date=2023-07-19
TITLE: [BIP-371] Adjust Protocol Fee Split
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Motivation

With the Year 2 funding season behind us there is an opportunity to re-assess the protocol fee split. Based on the[ impact analysis](https://forum.balancer.fi/t/year-2-sp-funding-impact-analysis/4921) conducted recently it’s relatively safe to say Balancer DAO will face a very low probability of a funding shortfall at least through the end of Year 3. I believe it is prudent to consider adjusting the fee split to provide additional tailwinds to the growth of key protocol metrics. In the future if circumstances change we can always pivot again.

As a reminder the fee split was decided to be 75% veBAL passive fees, 25% to the treasury when veBAL originally launched. [BIP-19](https://forum.balancer.fi/t/bip-19-incentivize-core-pools-l2-usage/3329) then introduced the idea of using fees to place voting incentives on “core pools”. The split then became: L1 core pools + L2’s: 75% voting incentives, 25% treasury. L1 non-core pools: 75% veBAL passive fees, 25% to the treasury.

[BIP-161](https://forum.balancer.fi/t/bip-161-close-year-2-funding-gap/4289) adjusted the split again, changing the 75% voting incentives/passive veBAL to 65% and increasing the treasury allocation to 35%.

There’s three core issues I want to address by proposing a new fee split:

* Voting incentives market is at capacity and partners often reduce their participation to reflect that
* veBAL wrappers do not benefit from the core pool mechanic. If Balancer sees most emissions on L2’s later this ye

====================================================================================================
[43] id=0x122d4d635e4e20d418ca0c489abb5f79f72ca71771852876a70dd181a675331e  token=BAL  space=balancer.eth  date=2023-07-26
TITLE: [BIP-377] Enable yBAL / 80-20BAL-wETH [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/394

**Summary:**
> Add gauge for the 80-BAL-20-WETH / yBAL composible stableswap pool to gauge controller
> Pool: `0x616D4D131F1147aC3B3C3CC752BAB8613395B2bB`
> Gauge: `0x5E23599eBE87A5A140f295C2fC6aAedb10955497`

**References/Useful links:**

> Link to:
    • [yearn.fi](https://yearn.finance)
    • Documentation
    • [Github](https://github.com/yearn)
    • [Discord](https://discord.com/invite/yearn)

**Protocol Description:**

> Yearn's yBAL is Yearn’s liquid veBAL wrapper product. The yBAL system features the same mechanics as Yearn's yCRV, but adapted to work within the Balancer ecosystem.
> 
> Users can mint yBAL tokens by locking their 80-20 BAL-WETH tokens to Yearn's whitelisted voter (note: This action is irreversible).
> 
> Upon minting yBAL, users can stake their yBAL into st-yBAL to passively earn yield. This yield comes from all incentives earned to Yearn's voter (e.g. bribes and protocol fees), and is automatically compounded back into yBAL increase each st-yBAL user's position.


**Motivation:**

> Incentivization to this pool will help drive liquidity for users who may wish to swap into or out of their yBAL position. We expect yBAL to increase the total locked tokens in veBAL and help users earn passive yield.

**Specifications:**

1. **Governance:** yBAL is designed to be a maximally trustless system with governance powers reserved to veYFI users. Some actions are available to the multisi

====================================================================================================
[44] id=0xa7bf76ad82a67170dce1fd90d3b9fcff8413c60b44c8e2f94c071cd764a4b50a  token=BAL  space=balancer.eth  date=2023-07-26
TITLE: [BIP-386] Allocate Base Incentives
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/403

### Motivation

Per Coinbase's recent public communications the official public launch of Base is likely to be in early August. Balancer contributors are actively working to ensure Balancer is available from day 1 which was authorized with the passing of [BIP-263](https://forum.balancer.fi/t/bip-263-deploy-balancer-to-base/4663). I request an initial allocation of 50,000 USDC from the treasury to be used towards Base launch incentives. This would be used over a period of no less than one month post launch. Another proposal will be put forward at that time if circumstances warrant additional funding. 

It's difficult to present any hard numbers because the network is not live yet and we don't know what will be available on launch day. The reasons I think funding incentives pre-launch is a good idea are the following:

* Balancer would be one of a small number of dapps with active incentives on launch day

* We'll start strong which is likely to bring interest from other Base projects

* Gives us the ability to match partner incentives for a period of time 

How quickly these funds are spent will depend on what opportunities present themselves and what activity the network is seeing post launch. 

The Balancer Maxis will be responsible for allocating these funds.

### Specification

If approved, the DAO Multisig `eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will transfer 50,000 USDC to the Maxi LM Mu

====================================================================================================
[45] id=0x060bc90eb8853153787da60aaf7a1891237e9cf9cb9a8df9928ce63f1efd0a2c  token=BAL  space=balancer.eth  date=2023-07-27
TITLE: BIP-388: Wire up Base Chain in preparation for launch
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## Payload PR - BIP-388
https://github.com/BalancerMaxis/multisig-ops/pull/405

## Background
Contracts are deployed, and everything is looking good for Balancers launch on Base Chain.   This BIP includes a number of final steps that must be taken to get everything working.

Along with the typical wireup of permissions, the Gauge Factory and Authorizer Wrapper are also being configured, and a 50% protocol fee is being set. 
## English Specification

The transaction details  for `base.json` were generated by [this script](https://github.com/BalancerMaxis/multisig-ops/blob/main/action-scripts/gen_add_permissions_payload.py) with inputs and outputs in [this directory](https://github.com/BalancerMaxis/multisig-ops/tree/staging/BIPs/BIP-388)

The following files can be found both linked below and in the payload PR linked above:

| Filename                                                                                                                                      | Description of Contents                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| [inputs.json](https://github.com/BalancerMaxis/multisig-ops/blob/staging/BIPs/2023-W30/BIP-388/inputs.json)

====================================================================================================
[46] id=0x014a8fc38f551e683cd799748153692f553aa806513446c9b252ccfcd4b402e6  token=BAL  space=balancer.eth  date=2023-08-02
TITLE: [BIP-393] Fund Beethoven X DAO - Technical for Aug - Dec
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/430

**Service Provider Name:** Beethoven X DAO

 **Core Contributor(s):** franz, groninge, daniel

**Pledge to abide by the DAO's [Code of Conduct](https://www.notion.so/balancergrants/Code-of-Conduct-fef15e2ed1f5453f8bd56f338c70bb88) (or link to your own):**  Yes

**Pledge to abide by the [Accountability Guidelines](https://www.notion.so/balancergrants/Accountability-Guidelines-229d93372403415688f8d3dc4cb964b1):** Yes

**Introduction & Domains of Operation:**

With the passing of [BIP-254](https://forum.balancer.fi/t/bip-254-funding-proposal-for-beethoven-x-dao/4652), the Beethoven X DAO became a Balancer Service Provider for the period of May 1, 2023 - July 31, 2023. This proposal seeks to extend the technical services and advisory component of the original proposal for an additional 5 month period (August 1, 2023 - December 31, 2023). As outlined in [BIP-314](https://forum.balancer.fi/t/bip-314-funding-proposal-for-beethoven-x-dao-marketing/4810), the marketing component of [BIP-254](https://forum.balancer.fi/t/bip-254-funding-proposal-for-beethoven-x-dao/4652) will appear as a separate proposal moving forward. 

The following sections present a summary of where we spent our time and energy over the last 10 weeks. As we continue to find the best way to bring value to the Balancer ecosystem, we welcome community feedback.

**API**

The new [Balancer API](https://api-v3.balancer.fi/) is production ready,

====================================================================================================
[47] id=0xc43178bf98c91380899c23ccbe63a37d3a1b487ce35edc54c1fadfd25001d21d  token=BAL  space=balancer.eth  date=2023-08-03
TITLE: [BIP-395] Delegate AAVE/stkAAVE to TokenLogic
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/432

---

title: [BIP-XXX] Delegate AAVE/stkAAVE to TokenLogic
author: TokenLogic
created: 2023-07-31

---

# Summary

This publication supports redirecting the AAVE and/or stkAAVE proposal and voting rights from Llama to TokenLogic. 

TokenLogic is a [recognised delegate](https://governance.aave.com/t/tokenlogic-delegate-platform/12516) within the Aave Community founded my Matthew Graham.

# Abstract

The main contributors to the Balancer ecosystem from Llama community was Matthew Graham and dydydmoon. The earlier is now 100% focused on building [TokenLogic](https://twitter.com/Matthew_Graham_/status/1682045389552365570?s=20) and dydymoon is transitioning from Llama to TokenLogic.

This publication advocates for redirecting Balancer's AAVE and/or stkAAVE, proposal and voting rights, from Llama to TokenLogic.

# Motivation

The below contains a list for recent proposals by TokenLogic.

* [[BIP-370] Reallocate bb-a-USD Protocol Fees to GHO/bb-a-USD Fees](https://forum.balancer.fi/t/bip-370-reallocate-bb-a-usd-protocol-fees-to-gho-bb-a-usd-fees/4969)
* [[BIP-361] Enable GHO/MAI Gauge [Ethereum]](https://forum.balancer.fi/t/bip-361-enable-gho-mai-gauge-ethereum/4970)
* [[BIP-360] Enable GHO/bb-a-USD Gauge [Ethereum]](https://forum.balancer.fi/t/bip-360-enable-gho-bb-a-usd-gauge-ethereum/4965)
* [[BIP-358] Enable GHO/wstETH Gauge [Ethereum] ](https://forum.balancer.fi/t/bip-358-enable-gho-wsteth-gauge-ethereum

====================================================================================================
[48] id=0x35013991f313a4c9ec7e50862b4f61d69ee4544eefe435ed37366818ff83ea19  token=BAL  space=balancer.eth  date=2023-08-09
TITLE: [BIP-396] Enable jCHF-VCHF Gauge w/ 2% emissions cap [Polygon]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/458

# Summary:

Enable a Balancer gauge for the Polygon jCHF - VCHF stable pool, coined 2chf (VCHF).

VCHF and jCHF are both Swiss Franc stablecoins. VCHF is backed by Swiss Francs and issued by VNX, and jCHF is backed by crypto and is issued by the Jarvis Network.

# References/Useful links:

## Jarvis Network:

Link to:

* Website:[ https://jarvis.network/](https://jarvis.network/)
* Documentation:[ https://learn.jarvis.network](https://learn.jarvis.network/)
* Code:[ jarvis-network / apps / Mono-repo / Synthereum · GitLab](https://gitlab.com/jarvis-network/apps/exchange/mono-repo)
* Social:[ https://twitter.com/Jarvis_Network](https://twitter.com/Jarvis_Network)
* Audits:[ Add SynthereumV6 audit report (f50be59f) · Commits · jarvis-network / apps / Mono-repo / Synthereum · GitLab](https://gitlab.com/jarvis-network/apps/exchange/mono-repo/-/commit/f50be59fbe43304302c51d90c24aaa97d1320b73)

## VNX:

Link to:

* Websites:[ https://vnx.li/](https://vnx.li/)
* Code:[ https://gitlab.com/vnx/ethereum-contracts](https://gitlab.com/vnx/ethereum-contracts)
* Social:[ https://twitter.com/vnx_platform](https://twitter.com/vnx_platform)
* Audits:[ https://vnx.li/transparency/](https://vnx.li/transparency/)

# Protocol Description:

## Jarvis Network

Jarvis Network is an ecosystem of protocols and applications to bring decentralized finance to real use cases. Its first protocol, Synthereum, allows borrowing and exch

====================================================================================================
[49] id=0x819da7fc945aa2a5a9cd47d06d6e9e47b0941d128de3a2ca04c69fc22304fc00  token=BAL  space=balancer.eth  date=2023-08-09
TITLE: [BIP-397] Authorize Mimic Smart Vault on Gnosis Chain
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/459

### Motivation

Gnosis Chain has grown enough that we can now start processing earned protocol fees. There's currently ~$13k accumulated in the fee collector. You can review [BIP-294](https://forum.balancer.fi/t/bip-294-authorize-mimic-smart-vault-on-arbitrum/4779) which authorized Mimic on Arbitrum for more information on the particulars. 

### Specification

The DAO Multisig on Gnosis `gno:0x2a5AEcE0bb9EfFD7608213AE1745873385515c18` will interact with the Authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` and call grantRole with the following arguments:

role: `0xf6c9a5b5acca77f76aed5abd6f810c52c3ff5f4a8a40ee9e1bc09f85795e73da`

which corresponds to the role for calling withdrawCollectedFees on the ProtocolFeeWithdrawer on Gnosis, verifiable [here](https://github.com/balancer/balancer-deployments/blob/master/action-ids/gnosis/action-ids.json#L58C64-L58C130).

account: 0x94Dd9C6152a2A0BBcB52d3297b723A6F01D5F9f7

which is the contract address for the Mimic smart vault on Gnosis.

====================================================================================================
[50] id=0x38168c355733a481b6385b876308ce7adc526daca6f0fa996cfeab374572deff  token=BAL  space=balancer.eth  date=2023-08-23
TITLE: [BIP-407] Enable LCNY/LUSD/ETH Gauge [Ethereum] with 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/482

Gauge Proposal Template:

**Summary:**
Enable a Balancer gauge for LCNY-LUSD-WETH pool on Ethereum.
LCNY is the immutable and decentralized CNY pegged stable on Ethereum. 
Link to pool: [0x8ed9e70bfa17a1e2c4f8e561c8d0c2d1acc092fa](https://etherscan.io/address/0x8ed9e70bfa17a1e2c4f8e561c8d0c2d1acc092fa)
Link to gauge: [0x2efCc89a1D534a8ee0e8dD469fa05cb20ccF5C19](https://etherscan.io/address/0x2efCc89a1D534a8ee0e8dD469fa05cb20ccF5C19)

**References/Useful links:**

Link to:
    • [Website](https://alternity.finance) 
    • [Documentation](https://docs.alternity.finance)
    • [Github Page](https://github.com/0xAlternity)    
    • [Twitter](https://twitter.com/0xAlternity)

**Protocol Description:**

Alternity is a decentralized protocol built on the Ethereum blockchain, inspired by the design of the Liquity Protocol. 

The protocol provide users with a stablecoin that is pegged to the Chinese Yuan, achieved by utilizing Ether as the required collateral. Loans are paid out in LCNY (a CNY pegged stablecoin) and need to maintain a minimum collateral ratio of 110%.

Alternity aims to cater to users who value diversification and seek alternatives to USD-pegged stablecoins.

As a protocol, Alternity is non-custodial, immutable, and governance-free.

**Motivation:**

Alternity Protocol is addressing the growing demand for a stable, decentralized, and Yuan-pegged financial instrument in the DeFi ecosystem. As

====================================================================================================
[51] id=0xeb1a639b7aa92ee03204c5521d7e69c8b180a55a696a88ca45aa24001c7a2ffd  token=BAL  space=balancer.eth  date=2023-08-23
TITLE: [BIP-408] Change Passive Fee Distribution
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Motivation

Currently passive protocol fees are paid in bbaUSD to veBAL holders. With the recent issue bbaUSD has been deprecated with no firm timeline on when it will reappear. Thus it is prudent to begin paying passive fees in USDC.

### Specification
No particular on chain execution is required. Maxis will make necessary changes in our operational procedures. USDC will be paid starting August 31st.

====================================================================================================
[52] id=0x0f2948f53a82df8aa543b352290cea414bb75c2b59193505e282614df690bd06  token=BAL  space=balancer.eth  date=2023-09-06
TITLE: [BIP-420] Refund Voting Incentives for Pools Shut Down Due to Bug Report
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/496

**Authors: Json**

**Background**

The bug disclosure made by Balancer [last week](https://twitter.com/Balancer/status/1694014645378724280) resulted in many pools being “killed” (i.e. no longer eligible to receive BAL rewards), this event coincided with the end of an Aura [voting round](https://gaugevotes.aura.finance/#/proposal/0x31a728854c1e6f16589d974515a14f88750d8990a926d54e6d9db43cb8d3955f). This proposal seeks to make whole projects who placed voting incentives or votes on affected pools, to a sum of $19.6k in USDC.

This event resulted in roughly $84k worth of voting incentives/votes being placed on affected pools, which would no longer be able to be honored by Aura/Balancer. Fortunately, Balancer contributors were able to swiftly create replacement pools/gauges with non-boosted pools to provide projects an alternative place for their votes to be cast. 

**Specifications**

Of the ~$84k affected votes, the final proposed refund amount stands at $19.6k, based on the value of provided incentives at the time and thanks to many projects opting to reallocate. This proposal is to refund the following amounts in USDC to the affected projects:

| Project | Gauge | Value | Refund address | Transaction |
| --- | --- | --- | --- | --- |
| Stader | ComposableStable ETHx/bb-a-WETH | $8700 | 0x68258012DA3B933a81617FD08c9382a60B87cA98 | https://etherscan.io/tx/0x2aaa5e2aea3c632e0049bf00509876f02586b44d849814a

====================================================================================================
[53] id=0x6459a7430d378236892af46e14afbecb56f51a81cd8e48b92e8a5774a919d7d6  token=BAL  space=balancer.eth  date=2023-09-07
TITLE: [BIP-424] Add Initial Avalanche & Base Gauges
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR with Payloads:
https://github.com/BalancerMaxis/multisig-ops/pull/500

#### Summary

Balancer has recently launched on the Avalanche and Base networks. Thus far both networks are teaming with new potential and it is likely through the streaming of BAL rewards higher TVL, volumes, and revenue can be tapped into. For each network the child ([AVAX](https://snowtrace.io/address/0xf23b4db826dba14c0e857029dff076b1c0264843#writeContract) , [Base](https://basescan.org/address/0xb1a4FE1C6d25a0DDAb47431A92A723dd71d9021f#writeContract)) and root gauge ([AVAX](https://etherscan.io/address/0x22625eEDd92c81a219A83e1dc48f88d54786B017#writeContract), [Base](https://etherscan.io/address/0x8e3B64b3737097F283E965869e3503AA20F31E4D#writeContract)) factories have been deployed earlier this week. The purpose of this proposal is to kickstart gauge emissions on the new chains. The gauges will all be uncapped, aside from those containing GOLD, and will be considered core pools in order to organically grow the network due to their high depth token and yield bearing natures. 

In order to add avalanche gauges to the controller, first the new gauge factory must be set for the type Avalanche.

For Base, the gaugeType must be added, and the gauge factory must be set for the new type. Furthermore, the child chain gauge factory must be added to the Base pseudo minter. 

**Motivation:**

Gauges being active on Avalanche and Base will allow Balancer to bootstrap liquidity and get the players on the network

====================================================================================================
[54] id=0x5bcccb1a57d7609154d18624ff3af1d0fba7ef925498afe6686e716c2b1c8400  token=BAL  space=balancer.eth  date=2023-09-13
TITLE: [BIP-426] Enable ALTR-WETH Gauge [Ethereum] with 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/504

**Summary:**
Enable a Balancer gauge for ALTR-WETH pool on Ethereum.
ALTR is the token issued by the Alternity Protocol. It captures the fee revenue that is generated by the system.
Link to pool: [0x47e1cf97a0586367349a14306a65f54ba0b8f1b6](https://etherscan.io/address/0x47e1cf97a0586367349a14306a65f54ba0b8f1b6)
Link to gauge: [0xeE707Ae5500DD9072aC0daB1170DD16d9AddD68F](https://etherscan.io/address/0xeE707Ae5500DD9072aC0daB1170DD16d9AddD68F)

**References/Useful links:**

Link to:
    • [Website](https://alternity.finance) 
    • [Documentation](https://docs.alternity.finance)
    • [Github Page](https://github.com/0xAlternity)    
    • [Twitter](https://twitter.com/0xAlternity)

**Protocol Description:**

Alternity is a decentralized protocol built on the Ethereum blockchain, inspired by the design of the Liquity Protocol. 

The protocol provide users with a stablecoin that is pegged to the Chinese Yuan, achieved by utilizing Ether as the required collateral. Loans are paid out in LCNY (a CNY pegged stablecoin) and need to maintain a minimum collateral ratio of 110%.

Alternity aims to cater to users who value diversification and seek alternatives to USD-pegged stablecoins.

As a protocol, Alternity is non-custodial, immutable, and governance-free.

**Motivation:**

Alternity Protocol is addressing the growing demand for a stable, decentralized, and Yuan-pegged financial instrument in the DeFi ecos

====================================================================================================
[55] id=0xb016d1a5dee45793c984dbc379d3e09a0395eae13a785cddfc074b51e74cf5e4  token=BAL  space=balancer.eth  date=2023-09-13
TITLE: [BIP-429] Adjust Arbitrum Airdrop Co-incentives Program(BIP-322) Distribution
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Motivation

Recently Balancer and Aura contributors have collaborated to submit a grant proposal for additional ARB.  Further, the Ballers are working on a Proposal for the [Arbitrum Short Term Incentives Program](https://snapshot.org/#/arbitrumfoundation.eth/proposal/0x5e0057920df9a278918e4de4ee1e6de7e2415d2af985e40a6c7a1a4b47a4ce01) .  Additionally, automating manual work in calculating incentive flows is a high priority for the Maxis in Q3, and the current program requires manual work and is schedule to run past the end of the quarter. 

As part of our work on grants and automation, a new [automated calculation system](https://github.com/BalancerMaxis/data_automation/blob/main/notebooks/arb_distribution.ipynb) for how the ARB would be distributed has been built.  This BIP proposes to change the current distribution of incentives to align with the program and automation proposed in the grant. 
   

## Details  about the newly developed Automation
The current program matches Bribes for Arbitrum pools with Bribes.   The new program is based on veBAL voting and + some situational boosts.

The new program distributes based on the following rules:

- 10,000 $ARB is emitted towards the USDC/USDC.E/DAI/USDT (core USD liquidity)
- Vote weight for all $ARB gauges is considered
- Boosts are applied to provide more ARB to pools seen to have added benefit to the ecosystem, and caps are in place to prevent too much gaming of the system.
    - Rules can be found here: [here](https://

====================================================================================================
[56] id=0x507e8b2e1b684887dcb9ac4d15c38caa5ec76eb908b9d441ce2c1f35ba35b070  token=BAL  space=balancer.eth  date=2023-10-12
TITLE: [BIP-448] Delegate DAO Grant ARB to LM Multisig
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Payload with PR
https://github.com/BalancerMaxis/multisig-ops/pull/542

### Summary

The Balancer DAO Multisig and Balancer LM Multisig should delegate their ARB balances to the LM Multisig. This will permit the Balancer Maxis to vote in the ARB ecosystem on behalf of the DAO. The goal is to strengthen ties with all parties in the Arbitrum ecosystem, and drive governance in a positive way for the Arbitrum ecosystem.

### Motivation

Balancer is doubling down on the Arbitrum ecosystem in many ways, one of the most obvious being the application for a grant from the [Arbitrum Short Term Incentives Program](https://forum.arbitrum.foundation/t/balancer-final-stip-round-1/16689). To further align with the ecosystem the Balancer DAO should become and active participant in Arbitrum governance and support future votes made that affect the network we have so much stake in. This will strengthen ties with Arbitrum, as well as any partners which are acting in a responsible way on the network. Balancer as a blue chip brings nuance to all governance forums it participates in, and this one makes sense to be in our scope. 

### Specifications

Part 1: The DAO Multisig on Arbitrum `0xaF23DC5983230E9eEAf93280e312e57539D098D0` will interact with the ARB token contract `0x912CE59144191C1204E64559FE8253a0e49E6548` by writing the `delegate` function passing the address `0xc38c5f97B34E175FFd35407fc91a937300E33860`. This will delegate the total ARB Balancer to the LM Multisig. 

[Part 1 Simulation](h

====================================================================================================
[57] id=0x8eb143cdf1608513078270f6c0302e30faa2155cce748e74678bde2ef4091f46  token=BAL  space=balancer.eth  date=2023-10-12
TITLE: [BIP-450] Fund Balancer Grants Q4 2023
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/546

## TL;DR

Continue grants SP with existing 12 grantees but with a reduced funding request for new grantees and committee members. Focus on:

* Funding for new grantees and buffer for existing grantee payments - 35k BAL
* Move to research focus and slow down for a revamp of grants program for 2024
  * Performance review of past grantees and assessment of current approval criteria
  * Mapping grants to Balancers latest roadmap
  * Define Grants Program plan for 2024 including a re-look at hackathons and IRL events.
* Committee Lead reduce by $1.5k to $7k USDC/month
* New committee member tiers due to current market conditions and grants slow-down:
  * Tier 1 Contributor - $600 USD paid in BAL - contribute to weekly grants meeting, grantee support and on-going assessments
  * Tier 2 Contributor - $1,200 USD paid in BAL - As per Tier 1 plus follow up calls for grant applications, mentor at least 1 grantee.
  * Tier 3 Contributor - $1,800 USD paid in BAL as per Tier 1 plus mentor 2-4 low assistance grantees or 1-2 high assistance grantees
  * Tier 4 Contributor - $3,000 USD paid in BAL - as per Tier 1 plus mentor 5+ low assistance grantees or 3+ high assistance grantees.
* Cancel final Fjord tranche ($66.6k USD in BAL) due to change in ownership and use to fund new grants.

With the cancellation of Fjord’s final tranche payment and a significant fall in BAL price, funding is requested to top up the treasur

====================================================================================================
[58] id=0x97856a0a66781666509f8e2d3dfa05aceabc543526e7fa546321f36f44030c03  token=BAL  space=balancer.eth  date=2023-10-19
TITLE: [BIP-457] Core Pool Incentive Program Automation
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## TL;DR:

* Automation for core pool incentives. See code  [here](https://github.com/BalancerMaxis/protocol_fee_allocator/blob/main/fee_allocator/notebooks/pool_fees_and_accounting.ipynb) and results from last round [here](https://docs.google.com/spreadsheets/d/16axBQBVNdPssQyjcIyb_4m4vOb5rKISIlrVMk7A2qjs/edit#gid=53204006).
* Reduction of threshold to receive voting incentives for an epoch from $5000 in accumulated fees to <$1000.
* Equal handling of incentive disbursements for Mainnet and L2s
  * Core Pool incentives always flow to the pools that generated the fee, no handling by TVL.
 * Mainnet pays 50% of protocol fees to core pools independent of the pool fee  source which results in a 20% increased fee flow to core pool voters

## Motivation

[The Core Pools program](https://forum.balancer.fi/t/bip-19-incentivize-core-pools-l2-usage/3329) was first initiated in July 2022. The original proposal underwent many iterations, making it less and less reproducible. As more chains have been added, the current system has too many moving parts and manual touch-points to maintain well. This BIP seeks to consolidate learnings and the current state of the incentive program, while simultaneously introducing a new automated system for handling fee redirection.

## History and Context

The Core Pools program fundamentally specifies that certain pools would have the portion of protocol fees due to veBAL holders being redirected as vote incentives. By incentivizing voters for voting on s

====================================================================================================
[59] id=0xc30fa0feac40a3df71d91e44af01215342ce2b2b7da35a95c763111b45053e6a  token=BAL  space=balancer.eth  date=2023-10-19
TITLE: [BIP-458] Enable 50GOLD/25USDC/25wstETH & 25GOLD/25BAL/25AURA/25wstETH [ARBITRUM]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/571

**Summary:**

After a successful launch on Base. The GoldenBoys are expanding to Arbitrum and getting ready to launch some products on mainnet. As many of the rules around caps have been created pertaining to me. I wanted to personally propose a suggestion that I think will be a general improvement for both Balancer and the Golden Boys.

First, to mirror the implementation on Base, which has created necessary USDC/ETH and BAL liquidity on Base, we request the following 2 gauges on Arbitrum:

[50GOLD/25USDC/25wstETH](https://app.balancer.fi/#/arbitrum/pool/0x2e8ea681fd59c9dc5f32b29de31f782724ef4dcb0001000000000000000004bc) - 6% cap

[25GOLD/25BAL/25AURA/25wstETH] (https://app.balancer.fi/#/arbitrum/pool/0x49b2de7d214070893c038299a57bac5acb8b8a340001000000000000000004be) - 2% cap

As pools containing $GOLD are already receiving 12% of veBAL, and the tokens market cap does not warrant unlimited pools as per the gauge framework. I suggest the following compromises be made, which should increase the overall health of Balancer emissions.

* Reduce cap on [50GOLD/25USDC/25ETH](https://app.balancer.fi/#/base/pool/0x433f09ca08623e48bac7128b7105de678e37d988000100000000000000000047) pool to 5%
* I suggest that the 10% cap for Arbitrum Airdrop incentives be shared between the 2 pools.
  * 8% cap on the 50/25/25 pool
  * 2% cap on the 25/25/25/25 pool

Further as a show of good faith:

* I will reduce voting on te

====================================================================================================
[60] id=0x3383c0a164ee6b80b27c37ce000fd8696dfb41199cb60c45691b0f4ecfcd63b7  token=BAL  space=balancer.eth  date=2023-11-01
TITLE: [BIP-467] Enable tBTC/WETH & tBTC/USDbC [Base]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/599

## Summary:

Proposal to add gauge support for 50/50 tBTC/WETH and 50/50 tBTC/USDbC pool on Base.

## References/Useful links:

Link to:

* Website: https://threshold.network
* Explorer: https://tbtcscan.com
* Documentation: https://docs.threshold.network/
* Github Page: https://github.com/keep-network/tbtc-v2
* Forum: https://forum.threshold.network/
* Discord: https://discord.com/invite/Threshold
* Twitter: https://twitter.com/tBTC_project

## Protocol Description:

tBTC is a decentralized wrapped Bitcoin, that is 1:1 backed by mainnet BTC.

Unlike other wrapped Bitcoins, the BTC that backs tBTC is not held by a central intermediary, but is instead held by a decentralized network of nodes using threshold cryptography.

tBTC is trust minimised and redeemable for mainnet BTC without a centralized custodian.

## Motivation:

This proposal aims to add a veBAL gauge for the 50/50 tBTC/WETH pool and 50/50 tBTC/USDbC pool on Base.

Threshold DAO seeks to build deep liquidity on Base, and Balancer is an ideal venue to build upon. These pools are key strategic pools, central to the long term growth strategy of Threshold DAO.

The DAO has budgeted T token bribes to incentivise this pool.

## Specifications:

### 1 Governance:

tBTC operates on Threshold DAO’s decentralized threshold encryption protocol. Threshold DAO is governed by the network’s work token, T. T token holders govern the DAO via proposals rais

====================================================================================================
[61] id=0x530857a34be237a1a5fa8d1356618bbf8e1e4345fec4392729153e37bd76d8e4  token=BAL  space=balancer.eth  date=2023-11-01
TITLE: [BIP-469] Enable BEETS/rETH gauge w/ 2% emission cap [Optimism]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/601


**Summary:**
> This is a proposal to enable BAL gauge for BEETS 80 / rETH 20 pool on optimism with 2% emission cap

**References/Useful links:**

> Link to:
    • Website https://op.beets.fi
    • Documentation https://docs.beets.fi/
    • Github Page https://github.com/beethovenxfi  
    • Twitter https://twitter.com/beethoven_x

**Protocol Description:**

> Beethoven X is a friendly fork of Balancer originated from Fantom back in 2021, and has been an essential part of the Balancer. It has been co-operating the Balancer deployment on optimism since 2022. $BEETS is the governance token of Beethoven X; on optimism, the token is bridged by Layerzero as a OFT. 

**Motivation:**

> This is to establish $BEETS liquidity on optimism. $BEETS token (the old multichain bridged version) has been used to incentivize liquidity through direct emission and voting incentives on optimism. The $BEETS token has recently been migrated to the Layerzero bridged version due to the multichain incidence (see [governance vote](https://snapshot.org/#/beets.eth/proposal/0xa3454614baec1abe0905d0abe6d1f08b53cae73879000dfcc8bd7c872419910c)). Hence, moving on the layerzero bridged version will be used. The pool will facilitate trading and holding of $BEETS on optimism. 

**Specifications:**
 
1. **Governance:** The BEETS governance is through maBEETS on fantom. 

2. **Oracles:** No

3. **Audits:** BeethovenX is a friendly fork of

====================================================================================================
[62] id=0x8e1e78461b9ba5681eb98f5d68fba19eaf3f63cf2f860492efc172e279f26559  token=BAL  space=balancer.eth  date=2023-11-08
TITLE: [BIP-474] Activate BAL Emissions for Mainnet GBPT:USDC “FX Pool” with 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/611

# **Summary**

PoundToken’s mission is to be the fully regulated GBP stablecoin of choice that allows for a true 24/7 real-time settlement and we are excited to have the opportunity to have the Balancer community be a part of this journey.

PoundToken is the first regulated issuer of a fully cash collateralized stable token called GBPT that comes with independent Proof of Reserves out of the gate. Every GBPT token is fully FIAT backed by 1 GBP in our bank account.

Our vision is to enable both retail consumers and financial institutions to leverage the power of GBP within the DeFi space and beyond. We are looking to Balancer as a great entry point into the arena and are excited to be offering exclusive incentives for those looking to help PoundToken in this initial distribution phase.

PoundToken is planning to set up a GBPT:USDC FX Pool that will enable liquidity providers to earn BAL Emissions as well as a starting 2% yield on all GBPT that is provisioned into the pool.

# **References/Useful links**

Links:

* Website
  * https://poundtoken.io/
* Twitter (X)
  * https://twitter.com/Poundtoken
* Token
  * https://etherscan.io/token/0x86b4dbe5d203e634a12364c0e428fa242a3fba98
* Audits
  * https://resources.poundtoken.io/tech-audits/
* Attestations
  * https://resources.poundtoken.io/reports/attestations/
* Proof Of Reserve
  * https://data.chain.link/ethereum/mainnet/reserves/gbpt-por
* CEX
  * https:

====================================================================================================
[63] id=0x338d29d51ffba3b3cfe4c3ff5ed509f00d6a1a037fd150fae588ce8f924cab03  token=BAL  space=balancer.eth  date=2023-11-08
TITLE: [BIP-477] Enable PSP/OP 80/20 Gauge with 2% emission cap [Optimism]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/614

**Summary:**
> Enable PSP/OP 80/20 A Night at the OPara Gauge on Optimism, with 2% BAL emission cap. 

**References/Useful links:**

> Link to:
    • Website https://www.paraswap.io/
    • Documentation https://www.paraswap.io/docs
    • Github Page    https://github.com/paraswap

**Protocol Description:**

> Paraswap is a DeFi aggregator that unites the liquidity of decentralized exchanges and lending protocols into one comprehensive and secure interface and APIs. The $PSP token is the governance token of Paraswap DAO. 

**Motivation:**

> This pool has been the main liquidity of PSP on optimism and recently the Paraswap governance has passed [the proposal](https://snapshot.org/#/paraswap-dao.eth/proposal/0x7c720fc7f9a239115cfe92261074e896266d113a0d0f245808fb690337e4df4e) to further bootstrap PSP liquidity using Aura and Balancer / Beethoven X on Optimism. The BAL gauge would be crucial for this. 

**Specifications:**
 
1. **Governance:** Paraswap governance is through PSP holders. 
 
3. **Audits:**  see [audits](https://www.paraswap.io/#home-audits)

4. **Centralization vectors:** No. 

5. **Market History:** The PSP/OP pool has been established on optimism for more than 7 months. 
 
6. **Value:** The pool is the primary liquidity of PSP on optimism and the BAL gauge would help further bootstrap the liquidity. 

Pool: https://op.beets.fi/pool/0x0244b0025264dc5f5c113d472d579c9c994a59ce000200000000000

====================================================================================================
[64] id=0x342ced517c06e7316f8a4876dc0d21d830d1347c0e0f25b0eb84353ee4372c9a  token=BAL  space=balancer.eth  date=2023-11-08
TITLE: [BIP-479] Enable psdnOCEAN/OCEAN 80/20 Gauge [Ethereum] with a 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/616

**Summary:**
H2O Data has been a staunch supporter of psdnOCEAN/OCEAN LP ($950K TVL) on Balancer from the outset. psdnOCEAN serves as a liquid staking token for veOCEAN. Much like veOCEAN, it accumulates rewards, but stands apart as it can be converted back into OCEAN via the LP at any moment, highlighting the criticality of pool liquidity. The pool's liquidity was spurred by OCEAN rewards courtesy of H2O Data. However, with the introduction of the Gauge, BAL/AURA emissions will now further fuel the incentive for liquidity provision, amplifying the pool's attractiveness.

**References/Useful links:**

> Link to:
•  Website: https://www.h2odata.xyz/
• Documentation: https://docs.h2odata.xyz/protocol-overview/welcome-to-h2o
• Github Page: https://github.com/h2odata
• Communities: 
Twitter: https://twitter.com/H2O_data; 

**Protocol Description:**

> H2O protocol is a protocol related to the emerging Data and AI economy (DataFi). Originating as a fork of RAI by Reflexer, H2O Data emerged in 2022 as a non-pegged stable asset backed by OCEAN. It has since transitioned towards crafting liquid staking derivatives aimed at governing non-liquid Data Infrastructure Tokens. The first token that was launched is psdnOCEAN which is a liquid staking derivative of veOCEAN.  
Upon locking veOCEAN, users can garner rewards from both Active and Passive Data Farming. Unlike psdnOCEAN, veOCEAN is not a transferable asset.

====================================================================================================
[65] id=0xd0715e1aaffc6a443dfeb618cd441bbebaaf755ee30fb7b98fc4be2541193515  token=BAL  space=balancer.eth  date=2023-11-08
TITLE: [BIP-481] Claim and Lock Balancer DAO Aura allocation into vlAura
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Payload with PR:
https://github.com/BalancerMaxis/multisig-ops/pull/618
**Summary**:

Back when Aura launched, a portion of the supply was allocated to the Balancer DAO.  That vested Aura exists in the following vesting contract: https://etherscan.io/address/0xfd72170339ac6d7bdda09d1eaca346b21a30d422#code
We are proposing to lock the 1.4m aura that has been vested. 

**Motivation**:

At the time of writing, 1.4m Aura has vested with 600k Aura left unvested. We are proposing to lock this into vlAura to begin earning rewards and eventually start allocating vote weight towards revenue generating or strategically important pools that lack a proper means of bootstrapping without ecosystem stakeholders voting philanthropically.  A proposal for how the DAO will deal with allocating this vlAura voting power will be presented in the coming weeks, but we think it is prudent to initiate the locking now. 

**Specification**: 

The DAO multisig on mainnet 0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f will call the claim() function on the AuraVestedEscrow at 0xfd72170339ac6d7bdda09d1eaca346b21a30d422 with the parameter _lock set to true.

====================================================================================================
[66] id=0x09871371baf920fcbc112e6f625dc7a6c44bb83f7e8bfac56cb56f4ef48922c2  token=BAL  space=balancer.eth  date=2023-11-15
TITLE: [BIP-482] Enable Savvy Tricrypto (svUSD-svETH-svBTC) Pool Gauge [Arbitrum] with 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/626

**Summary:**

Balancer has been actively seeking yield-bearing liquidity for some time. The emergence of new DeFi primitives, like svUSD, svETH, and svBTC, are helping bridge more liquidity to Arbitrum than ever.

As Arbitrum liquidity continues to rise, a compelling opportunity arises for Savvy to replicate the achievements of Balancer's Mainnet pools on Arbitrum. This TriCrypto pool benefits Balancer by bringing a new yield-bearing DeFi primitive that benefits Savvy by opening an additional market for svTokns, and helps the ecosystem by providing a new way to earn yield.

**References/Useful links:**

**Balancer Gauges**

root: https://etherscan.io/address/0xa1dDe34d48868F9E0901592f2A97e20F76004059

child: https://arbiscan.io/address/0x6817149cb753BF529565B4D023d7507eD2ff4Bc0

**Link to:** 
• Website[ https://savvydefi.io/](https://savvydefi.io/)

• Documentation[ https://docs.savvydefi.io/savvy-defi-faq/introduction-to-savvy-defi](https://docs.savvydefi.io/savvy-defi-faq/introduction-to-savvy-defi)

• Github Page[ https://github.com/savvy-finance](https://github.com/savvy-finance) 

• Other useful links?[ https://twitter.com/SavvyDefi](https://twitter.com/SavvyDefi)

**Protocol Description:**

Savvy is a novel platform offering non-liquidating, self-repaying, and interest-free borrowing solutions. With Savvy's cutting-edge synthetics, you can access up to 50% of your collateral's value. Whether you

====================================================================================================
[67] id=0x63ee2b81647ca896eb27e2ffa8464f8af98fa6d7939472026ac7a57d9a241862  token=BAL  space=balancer.eth  date=2023-11-15
TITLE: [BIP-483] Enable crvUSD/sDAI gauge with 2% emission cap on Gnosis Chain
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/627

**Summary:**

This is a proposal to enable a Balancer gauge for the crvUSD/sDAI pool on Gnosis Chain a with 2% emission cap.

**References/Useful links:**

> Link to:
    • https://curve.fi/
    • https://resources.curve.fi/
    • https://github.com/curvefi    
    • Audits: https://classic.curve.fi/audits                                               
                  https://github.com/curvefi/security-incident-reports/tree/main/audits

**Protocol Description:**

Curve is a multichain AMM exchange that specializes in low slippage stablecoin swaps and concentrated liquidity provision. Curve distinguishes itself as the primary liquidity hub for some of the most exciting DeFi innovations, including stablecoins, Liquid Staking Tokens, and Real World Assets. More recently, it has launched its own stablecoin, crvUSD, creating new opportunities for DeFi integrations on both mainnet, and crosschain.

**Motivation:**  

crvUSD is an overcollaterized stablecoin backed by a diverse set of collateral, including sfrxETH, wstETH, WBTC, WETH, and tBTC. The stablecoin was deployed in March 2023 and has reached a market cap of >$100m since inception. Its primary innovations are the LLAMMA AMM which gradually liquidates positions, and a dynamic monetary policy that adjusts interest rates based on market dynamics. Supporting the growth of crvUSD on Balancer will help Balancer become a hub for the adoption of decentra

====================================================================================================
[68] id=0x34a640cded6d8ebbab1677ad0286a32a7d2896eaffac904cd8579d5e153dccc2  token=BAL  space=balancer.eth  date=2023-11-15
TITLE: [BIP-484] Enable 50WETH-50TAG Gauge [Base] with a 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/628

**Summary:**

> Enable 50WETH-50TAG Gauge [Base] with a 2% emission cap

**References/Useful links:**

>     • Website: https://tag.tech/
>     • X: https://twitter.com/tagdottech
>     • Medium/Documentation: https://medium.com/@tag.tech

**Protocol Description:**

> TagTech is a new initiative by SoFi on the Base platform, designed to empower creators to manage their communities and shape their future. The team behind TagTech combines experienced SoFi users with experts in business and blockchain technology, aiming to improve upon the existing SoFi ecosystem.
> 
> 
> TagTech stands out by offering practical solutions to common problems:
> 
> 
> - Scalability: We built a dynamic bonding curve system that lets creators split their social tokens, called Tags. TagSplits create new bonding curves with double the Tags in circulation and half the Tag price, giving creators the power to scale their communities.
> 
> 
> - Creator freedom: Creators are the heartbeat of any SoFi platform, and they deserve more freedom and control. That’s why at TagTech we champion self-custody, so creators own their private keys and assets. This also empowers us to easily build features like TagTransfer and token reward systems to reward creators for their contributions.
> 
> 
> - Sniping bots: To combat sniping bots while also giving creators more freedom of choice, we added a launch feature that gives creators complete contr

====================================================================================================
[69] id=0x897aba7b7f3a68867595fea782931da3aae10fc15c62d8ace8cbd8e923ac07c4  token=BAL  space=balancer.eth  date=2023-11-15
TITLE: [BIP-488] Authorize Mimic Smart Vaults on Mainnet, Avalanche, and Base
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/631

### Motivation

The core purpose of the proposal is to take the manual labor of handling protocol fees out of the hands of the Balancer Maxis and automate the process to make the DAO as streamlined and sustainable as possible. Protocol fees are accruing on all networks at a healthy rate and Mimic is at the point where they are capable of managing this process in an automated way. One can review [BIP-294](https://forum.balancer.fi/t/bip-294-authorize-mimic-smart-vault-on-arbitrum/4779) which authorized Mimic on Arbitrum for more information on the particulars, as well as [BIP-115](https://forum.balancer.fi/t/bip-115-balancer-smart-vaults-fee-collector/3966) for the original development plan. This proposal will authorize Mimic vaults on Mainnet, Avalanche, and Base to execute the same automation. These vaults are using Mimic v3, as opposed to v2 like the prior instances. Addresses can be confirmed [here](https://www.notion.so/mimic-fi/Balancer-Fee-Collector-v3-Test-Base-Avalanche-and-Mainnet-instructions-89bda03acb7b4cf09b2bb2794eb0fa31?pvs=4#89b9190d21c240409f6eabca86c8778c). 

### Specification

#### Mainnet

The DAO Multisig on Ethereum `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will interact with the Authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` and call grantRole with the following arguments:

role: `0x826ac7ce861f2a54e071e6c724653757fdd1259804eb1ca7f040aa1cd09923fe`

which corresponds

====================================================================================================
[70] id=0xa04a9b7fc0b37a54943ab48ebbf906aca5c3acfb1fd05e1b08118fe637deed5c  token=BAL  space=balancer.eth  date=2023-11-22
TITLE: [BIP-490] Enable 80OETH-20WETH Gauge [Ethereum] with a 2% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/642

 **Summary:**

We propose the introduction of a gauge for the OETH/WETH pool on Ethereum. This initiative aims to foster greater liquidity and facilitate smoother transactions for users. By enabling this gauge, we anticipate enhancing the yield-generating opportunities for both the Balancer community and Origin Ether users. Origin has already brought over 8,443 rETH and ETH to the Balancer ecosystem and this gauge will encourage Origin to bring more.

**References/Useful links:**



• Website: https://oeth.com
• Documentation: https://docs.oeth.com
• Github: [https://github.com/originprotocol](https://github.com/originprotocol)

• Communities:
* Twitter: [https://twitter.com/OriginProtocol](https://twitter.com/OriginProtocol)
* Medium: [https://blog.originprotocol.com/](https://blog.originprotocol.com/)
* Defillama: [https://defillama.com/protocol/origin-ether](https://defillama.com/protocol/origin-ether)

**Protocol Description:**

[Origin Ether](https://www.oeth.com/) was launched in May 2023 and is an ERC20 LST aggregator that generates yield while sitting in your wallet by tapping into blue-chip protocols. OETH is backed 1:1 by ETH, WETH, stETH, rETH, and frxETH at all times; holders can go in and out of OETH as they please. Similar to stETH, OETH yield is automatically distributed at least once a day through a positive rebase in the form of additional OETH, proportional to the amount of OETH held

====================================================================================================
[71] id=0x141051b2fe6f18e322539c0e54b2fb0d9872b6096f2c3fd71fa3bf27e5c7b8f8  token=BAL  space=balancer.eth  date=2023-11-23
TITLE: [BIP-492] Enable weETH/WETH Gauge [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/645

**Summary:**
The [ether.fi](https://www.ether.fi/) team proposes a Balancer Boosted Gauge for a weETH-WETH pool on Ethereum mainnet, with a 10% emissions cap.

**References/Useful links:**

    • Website - https://www.ether.fi/
    • Documentation - https://etherfi.gitbook.io/etherfi/ether.fi-whitepaper
    • Github Page - https://github.com/etherfi-protocol
    • Discord - https://discord.com/invite/zqGzcuQWvD
    • Twitter - https://twitter.com/ether_fi

**Protocol Description:**

Ether.fi is a decentralized, non-custodial liquid staking protocol built on Ethereum, allowing users to stake their ETH and participate in the DeFi ecosystem without losing liquidity. The protocols eETH is a liquid restaking token (weETH is the non-rebasing equivalent), serving as a representation of ETH staked on the Beacon Chain, which rebases daily to reflect the associated staking rewards. Users can deposit ETH into the liquidity pool to mint eETH, hold eETH to accrue rewards, and use eETH within DeFi or swap it back to ETH at any time via the liquidity pool. The protocol currently employs a permissioned validator set, however this will transition to permisionless based on the protocol roadmap.

ETH staked through the ether.fi protocol liquidity pool accrues normal Ethereum staking rewards, and will also be natively restaked with EigenLayer. Currently when users wish to restake their LST’s they lock their tokens, which

====================================================================================================
[72] id=0x7ff95888348cd78c99b28b1da88de6dceb73c9ac924a6ba85fb7508bfc781e29  token=BAL  space=balancer.eth  date=2023-11-30
TITLE: [BIP-496] Enable osETH/ETH Gauge [Ethereum] with 10% emission cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/668

## Summary

Proposal to add gauge support for the new [osETH/ETH Composable Stable](https://app.balancer.fi/#/1/pool/0xdacf5fa19b1f720111609043ac67a9818262850c000000000000000000000635) with a 10% gauge cap.

## References/Useful links
• [Website
](https://stakewise.io) • [Documentation
](https://docs-v3.stakewise.io/) • [Github Page
](https://github.com/stakewise/v3-core) •  [Twitter](https://twitter.com/stakewise_io) - ~10K followers
• [What is osETH?](https://stakewise.medium.com/what-is-oseth-a-deep-dive-into-the-overcollateralized-staked-ether-token-of-stakewise-v3-part-1-37d14e28282a)

## Protocol Description

StakeWise was the first non-custodial liquid staking solution on Ethereum, launched in early 2021, with a little over 100k ETH currently staked. After over a year of development and testing, the V3 upgrade is now live on Mainnet. StakeWise V3 is the (Gnosis) Safe of ETH staking, a free public good that aims to fully democratize the staking ecosystem and greatly improve the decentralisation of staked capital. Any entity can offer trustless, non-custodial staking-as-a-service via an open marketplace that gives stakers the ability to delegate to their preferred operators/staking solutions. For more details about StakeWise V3, please refer to the [StakeWise V3 Announcement](https://stakewise.medium.com/stakewise-v3-announcement-9e4fe73abdf2).

StakeWise V3 features a liquid staking token, osETH

====================================================================================================
[73] id=0xb7fa9e686e059802b4396e7b3751866fcaf563af143ca70fee35fc71db2c73f6  token=BAL  space=balancer.eth  date=2023-12-06
TITLE: [BIP-502] Enable DFX/ETH Gauge with 2% emissions cap and deprecate old gauge [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/674

**Summary:**

DFX Finance’s proposal to (1) add a gauge for the DFX(L2)/ETH 50/50 on Arbitrum (2) deprecate the gauge for the DFX/ETH 50/50 on Arbitrum

References/Useful links:

Link to:
Website: [Main Website](https://dfx.finance/), [dApp](https://app.dfx.finance/)

• Documentation: [Gitbook](https://docs.dfx.finance/), [Medium](https://medium.com/@dfxfinance)

• Github Page: [Github](https://github.com/dfx-finance)

**Protocol Description:**

DFX Finance is a decentralized foreign exchange (FX) protocol that facilitates the seamless exchange of fiat-backed stablecoins denominated in a growing number of currencies. Using a hyper-efficient AMM, optimized for low volatility trading, DFX provides FX swaps with rates that will beat any bank, money changer, or FX platform. DFX is the governance token of DFX Finance which allows users to vote on protocol changes and initiatives of the DAO, and also allows users to receive boosted emissions on deposits within the DFX ecosystem.

**Price History DFX:**

Price History for DFX can be found on [Coingecko](https://www.coingecko.com/en/coins/dfx-finance)

**Motivation:**

The DFX token on L2s such as Arbitrum and Polygon is migrating from a bridged token to a Chainlink CCIP token. As well, DFX Finance is committed to continue to engage in the Hiddenhand Finance ecosystem in a meaningful way to further deepen DFX liquidity onchain.

**Specifications:**

1. Govern

====================================================================================================
[74] id=0x24d7a10765966e955fba88fc218f8684539456e67c7500099014e053614eda85  token=BAL  space=balancer.eth  date=2023-12-13
TITLE: [BIP-505] Enable 40DFX-20USDC-40TEL Gauge with 2% emissions cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/681

**Summary:**
DFX Finance’s proposal to add a gauge for the 40DFX-20USDC-40TEL - Polygon

**References/Useful links:**
Link to:
Website: [Main Website](https://dfx.finance/), [dApp](https://app.dfx.finance/)

• Documentation: [Gitbook](https://docs.dfx.finance/), [Medium](https://medium.com/@dfxfinance)

• Github Page: [Github](https://github.com/dfx-finance)

**Protocol Description:**

DFX Finance is a decentralized foreign exchange (FX) protocol that facilitates the seamless exchange of fiat-backed stablecoins denominated in a growing number of currencies. Using a hyper-efficient AMM, optimized for low volatility trading, DFX provides FX swaps with rates that will beat any bank, money changer, or FX platform. DFX is the governance token of DFX Finance which allows users to vote on protocol changes and initiatives of the DAO, and also allows users to receive boosted emissions on deposits within the DFX ecosystem.

**Price History DFX:**

Price History for DFX can be found on [Coingecko](https://www.coingecko.com/en/coins/dfx-finance)

**Motivation:**

The DFX token on L2s such as Arbitrum and Polygon is migrating from a bridged token to a Chainlink CCIP token. As well, DFX Finance is committed to continue to engage in the Hiddenhand Finance ecosystem in a meaningful way to further deepen DFX liquidity onchain.

**Specifications:**

1. Governance: DFX tokens serve as the governance token for the DFX Fi

====================================================================================================
[75] id=0x57283b9c67f71da710641bb6bb880666dc82dba70fb8e29b3f462f72ba1f0e6e  token=BAL  space=balancer.eth  date=2023-12-14
TITLE: [BIP-508] Utilize locked Aura to Support Ecosystem Growth
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/686

# Summary

The purpose of Balancer’s locked vlAura should be to augment our successful revenue driving pools while also giving us the flexibility to target particular narrative strategies so that we are able to compete with protocols that have a centralized emissions direction framework.  

Balancer DAO currently has 1,423,058.93 vlAura as a result of BIP-481 https://forum.balancer.fi/t/bip-481-claim-and-lock-balancer-dao-aura-allocation-into-vlaura/5319
This represents about 5.74% of vlAura voting weight and represents 2-3% of total veBAL votes.  

I propose we utilize this voting power to forward the strategic initiatives of the Balancer DAO according to the following framework.

**40% Revenue Producing Pools**
**40% Facilitating Core Liquidity**
**20% Discretionary Business Development**

### Revenue Producing Pools (40%)


40% of the vlAura will be used to vote for sustainable revenue producing pools.  We define a sustainable revenue producing pool as a pool with predictable revenue production that does not depend on volatility to earn protocol revenue. This would be inclusive of major LST stableswap pools with fee on yield (Lido stETH, rocketpool rETH, frax sfrxETH) and pools with >=50% composition of major interest bearing stablecoin pools (sDAI, sFRAX).  

The allocation strategy will be simple, first we will designate a list of pools to be considered as “core revenue producing pools” which ali

====================================================================================================
[76] id=0x09bda466bf467e7423d0c575c6d932db759a50dcdec6dbd5e86134479db1722b  token=BAL  space=balancer.eth  date=2023-12-21
TITLE: [BIP-510] Enable sDAI and sFRAX Gauge [Ethereum & Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/693

**Summary:**
> Balancer's core focus has been yield bearing liquidity for quite some time. As of recent [sDAI](https://app.spark.fi/sdai/) and [sFRAX](https://app.frax.finance/sfrax/stake) have become popular yield bearing stablecoins in the greater defi ecosystem. This proposal is meant to enable four gauges encompassing these tokens on Ethereum and Arbitrum in stable and weighted pools. The pool will sufficiently capture which captures the yield of these tokens and creates routing for the 3 primary stablecoins and wstETH to be swapped against. The pools all will be core for Balancer.

**References/Useful links:**

> Link to:
    • [Maker Webiste](https://makerdao.com/en/)
    • [Documentation](https://docs.makerdao.com/)
    • [Github Page](https://github.com/makerdao/developerguides/blob/master/dai/dsr-manager-docs/dsr-manager-docs.md)    
    • [Communities](https://forum.makerdao.com/)
> Link to: 
    • [Frax Webiste](https://app.frax.finance/)
    • [Documentation](https://docs.frax.finance/frax-v3/sfrax)
    • [Github Page](https://github.com/FraxFinance/frax-solidity/blob/master/src/types/constants.ts)    
    • [Communities](https://gov.frax.finance/)


**Protocol Description:**

> sDAI is part of the Maker ecosystem and utilizes the Dai Savings Rate to incentivize users to stake their DAI here https://app.spark.fi/sdai/ . 
>
>sFRAX is from the new Frax v3 ecosystem and can be utilized [here]

====================================================================================================
[77] id=0xf5e1d90f47596bbe84657b78780c3ac8fceac6d7da8e1720926e1168c2ad7fad  token=BAL  space=balancer.eth  date=2023-12-21
TITLE: [BIP-513] Seed BAL Liquidity on Avalanche
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/696

# Introduction

Earlier this year, governance has approved to [deploy Balancer on Avalanche](https://snapshot.org/#/balancer.eth/proposal/0xfac459b1f0ce7eec8965814a062a3eac195b5988990ae7a6a59e4022304837c3)

After a bootstrapping phase where [an initial set of gauges was added](https://snapshot.org/#/balancer.eth/proposal/0x6459a7430d378236892af46e14afbecb56f51a81cd8e48b92e8a5774a919d7d6) the deployment is now at a much more mature state with approximately $7mln in TVL and $400k in daily trading volume. Furthermore, BAL emissions are flowing to major AVAX LST pools that are also part of our core pool framework. However, currently, no deep liquidity exists for BAL to trade with on Avalanche.

# Motivation

Given the lack of BAL liquidity on Avalanche, we propose to seed $100k in BAL/WAVAX liquidity in a 80:20 [pool](https://app.balancer.fi/#/avalanche/pool/0xa39d8651689c8b6e5a9e0aa4362629aef2c58f55000200000000000000000038) on Avalanche so that protocol participants can trade against a core pair. This liquidity will be provisioned from the DAO treasury on mainnet. Funds will be bridged to Avalanche and deposited to a newly created BAL:WAVAX 80:20 pool.

At the time of the writing of this proposal, approximately $5k worth of BAL is emitted every day on Avalanche gauges. Therefore, a base liquidity of at least $100k is sufficient to provide a solid trading pair without too much slippage.This core liquidity

====================================================================================================
[78] id=0x71093cb5f1ed8359856757cc04c08f6905ea2b0bf7c7d78780745d27977a1102  token=BAL  space=balancer.eth  date=2023-12-21
TITLE: [BIP-514] Fund Balancer Maxis Q1-2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/697

## Introduction

 
![BIP-514.png](ipfs://bafkreid33cuhfiqmn7wlhpbarprz3ge736wizqnwf4lllitlrxb5zzfeii)
    

> Maxis queue up to embark on the v3 journey

The Balancer Maxis are thrilled to announce our pivotal role in the upcoming development of Balancer v3. Recognized as key contributors and the vital link between partners and the protocol, our dedication to the DAO is unwavering. As we embark on another quarter, our commitment is not just to continue, but to evolve – to redefine our engagement and amplify our positive impact on the DAO in 2024.

The third quarter marked a significant transition for the Maxis. Following the departure of our strategic visionary, Solarcurve, we embraced change and innovation. Tritium rose to the occasion, leading critical initiatives like the [core pool incentive automation](https://forum.balancer.fi/t/bip-457-core-pool-incentive-program-automation/5254), as well as securing and executing on the Arbitrum STIP, demonstrating our adaptability and resilience.

Our evolution goes beyond roles and responsibilities. The Maxis are transforming from a collective of passionate enthusiasts to a team of full-time, professional experts. The new full-time addition consists of @Xeonus who will spearhead our strategic direction.

Our mindful approach to funding allocation ensures an efficient use of resources – balancing USDC and BAL demands with maximum effectiveness. Our focus is no

====================================================================================================
[79] id=0xeeb9ffcd96ff3ba890bbcc8f6b2bb60b0a3135a67eccee5ffc3f2f3b2db49552  token=BAL  space=balancer.eth  date=2023-12-21
TITLE: [BIP-517] Fund Balancer Grants for Q1 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/700

# Balancer Grants DAO Service Provider Proposal Q1 2024

## TL;DR

With V3 due for launch in early 2024, the grants program will return to full funding targeting new integrations with Balancer’s new and improved tech. This quarter’s focus will be to find, fund and launch projects with Balancer V3 ahead of its launch in Q2 and help boost wide adoption.

The grants committee has completed a historic assessment of the grants awarded since its inception in August 2021. This proposal is created on the basis of the findings and recommendations of [this report](https://forum.balancer.fi/t/balancer-grants-program-all-time-recap/5458).

* Funding duration 3 months from Jan 1st to March 31st, 2024.
* Funding for new grantees - 50k BAL
* Separate budget for “Moonshot projects” (research topics, novel projects that are interesting but use case is unknown. Described more below ) - 15k BAL
* Funding categories identified in Program Recap
* Attract more projects to build on V3
* Reinstate Committee Lead to $8k USDC/month and allowance for 1 of each committee comp tier.
* End long running grants (RealEstate Exchange, GammaSwap and Yearn) recovering funds for future projects

With the recovery of funds from stale grants and an increase in BAL price, no BAL is required for funding period. Funding is requested to top up the grants treasury to:

1. 64,671 BAL available for new grantees, 50k general, 15k moonshot *(no add

====================================================================================================
[80] id=0xe562d95ca7c9e4c4ea9f433eff4ae4c0ea0840f0036198edb98249c3bf9bd054  token=BAL  space=balancer.eth  date=2023-12-21
TITLE: [BIP-522] Arbitrum LGP and STIP Adjustments
CHOICES: Yes, let's do it  | No, this is not the way | Abstain
TEXT (first 1500 characters):
Code being implemented: 
https://github.com/BalancerMaxis/STIP_automation

## Background

Balancer was awarded 1.2 million Arbitrum as part of the Arbitrum Short Term Incentives Program (STIP) to be paid out between November 11th and January 16th. The [program](https://forum.arbitrum.foundation/t/balancer-final-stip-round-1/16689?u=tritium) is being paid out in [biweekly chunks of 205,814.8 $ARB](https://forum.arbitrum.foundation/t/balancer-stip-program-updates-2/20078) based on [boost modified veBAL voting.](https://github.com/BalancerMaxis/data_automation/blob/main/data/arbitrumBoostRules.md)

After a number of weeks of the program in operation, this BIP seeks to make a few modifications to the program in order to increase it’s effectiveness, and enable our current major strategic focus of supporting interest bearing liquidity.

## Proposed Changes

### Dynamic Boost

When looking at the pools receiving veBAL there is a clear differentiation. Some pools are growing based on $ARB yields, generating decent volume and or fees and are examples of what we hope to see with STIP. Others seem to be more yield farming plays, with basic ERC-20 tokens that don’t generate much volume, engage with advanced balancer tech, or generate fees through our core pools program.

The STIP was designed to allow everyone an opportunity, but we want to leave space for real innovation and not have access to STIP rewards be made over-competitive by yield farming profit maxis.

The Dynamic Boost is the

====================================================================================================
[81] id=0x35bd58c3d039dc32995c53c745128703101e502b60c52482b8600e061a9cd8cf  token=BAL  space=balancer.eth  date=2023-12-27
TITLE: [BIP-523] Enable LUMIN/rETH Gauge with 2% emissions cap [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/714

## Summary:

Lumin Finance proposal to add a gauge for the LUMIN/rETH 80/20 pool on Arbitrum.

## References/Useful links:

Link to:

• Website: [Lumin Finance](https://lumin.finance)

• Documentation: [Docs](https://docs.lumin.finance), [Medium](https://medium.com/@lumin.finance)

• Github Page: [Github](https://github.com/bull-haus/lumin-contracts) (private until release, private access granted on request)

## Protocol Description:

Lumin Finance is a decentralized peer-to-peer fixed rate lending and borrowing protocol. Launching on the Arbitrum Blockchain, powered by the $LUMIN token. Unlike most DeFi lending protocols, the lender, borrower and staker in the protocol are rewarded for their participation, in a way that will (eventually) be administered by a DAO.

Lumin Finance offers some unique aspects with our platform, including fee sharing, buyback-and-distribute (BBD) and buyback-and-burn (BBB). These mechanisms create a powerful circulation flow and a deflationary supply for the LUMIN token.

## Motivation:

Balancer 80/20 pools are a very capital-efficient way to scale liquidity, while incentives are helpful to bootstrap liquidity. Lumin Finance sees the Balancer 80/20 pool as a perfect fit for the LUMIN token, and as the goal is to turn the pool LP token into the Protocol’s governance/staking token, Lumin Finance's objective with the pool incentivization is to reward LUMIN token holders that

====================================================================================================
[82] id=0x69cefa84f3e221d9f85581e3994840f288571de74bd61d3dca2a2c1730e0fd57  token=BAL  space=balancer.eth  date=2024-01-11
TITLE: [BIP-529] Enable sFRAX-sfrxETH gauge [Optimism]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/737

**Summary:**

> We request adding sFRAX/sfrxETH weighted pool on optimism to BAL gauge as an uncapped core pool 

**References/Useful links:**

> Link to
> • [Website](https://frax.finance/)
> • [Documentation](https://docs.frax.finance/)
> • [Github Page](https://github.com/FraxFinance/frax-solidity)

**Protocol Description:**

> sFRAX is a staked interest bearing version of FRAX stable coin and  sfrxETH is a staked interest bearing version of FRAX's staked ETH (frxETH). 

**Motivation:**

> As a joint effort with FRAX and Beethoven X, we aim to increase liquidity of FRAX, sFRAX, frxETH, sfrxETH, to make Balancer a liquidity hub for frax assets on optimism. The BAL gauge and core pool status will facilitate the process.

**Specifications:**

1. **Governance:** FRAX governance process can be seen [here](https://docs.frax.finance/smart-contracts/governance) and their snapshot [here](https://snapshot.org/#/frax.eth).
2. **Oracles:** Rate provider contract for [sfrxETH](https://optimistic.etherscan.io/address/0xf752dd899F87a91370C1C8ac1488Aef6be687505) and for [sFRAX](https://optimistic.etherscan.io/address/0xDe3B7eC86B67B05D312ac8FD935B6F59836F2c41).
3. **Audits:** See [here](https://docs.frax.finance/other/audits)
4. **Centralization vectors:** see [here](https://docs.frax.finance/frax-ether/overview).
5. **Market History:** See [here](https://docs.frax.finance/frax-ether/frxeth-and-sfrxeth)
6. **Value

====================================================================================================
[83] id=0x76050706905cc4860ab56dd118695a9dd78255c23284b4074966b56cbc1c19dd  token=BAL  space=balancer.eth  date=2024-01-17
TITLE: [BIP-537] Replace GGP Incentives On Avax
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/754

**Summary & Motivation:**

The direct incentive infrastructure for Balancer pools is managed by the Balancer Maxis to facilitate rewards provided by partners as opposed by BAL from the gauge system. This is done via reward injectors which take a recipient list schedule that takes mainly the gauge address, amount of rewards per week, and number of weeks. Once an injection is executed; it adds the number of rewards per week to a gauge contract to be streamed to stakers.

During the most recent adjustment to the injection schedule for the [ggAVAX/wAVAX pool](https://app.balancer.fi/#/avalanche/pool/0xc13546b97b9b1b15372368dc06529d7191081f5b00000000000000000000001d), the GoGoPool team requested to stream 4000 GGP over 4 weeks, at 1000 GGP per week. The transaction (can be seen [here](https://snowtrace.io/tx/0x6b1cf6ebcd19bca140c10a32d8e02d50957f6aae5b76ad1a080fdf621e8318dc?chainId=43114)) executed by the team was incorrectly configured and sent the full amount of 4000 GGP to the injector over a 1 week period which resulted in an undesired outcome for reward distribution.. To compensate the GGP team for this misconfiguration, we propose to supply the difference in incentives of 3000 GGP equivalent in BAL from the treasury at the time of execution.

This proposal requests Balancer DAO to provide 6545 BAL to be swapped to GGP and be distributed over the next 3 weeks as direct incentives to the ggAVAX/WAVAX g

====================================================================================================
[84] id=0x272057a8a147b98a8f796a5552274316798a6483026b3778157f93ddc59d723c  token=BAL  space=balancer.eth  date=2024-02-29
TITLE: [BIP-552] Authorize Mimic Smart Vaults V3 on Arbitrum, Polygon and Gnosis
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payloads
https://github.com/BalancerMaxis/multisig-ops/pull/820

## Motivation

The Balancer Maxis have worked closely together with Mimic to streamline and automate protocol fee processing on all Balancer deployments. In an initial phase, Mimic used their smart vault v2 architecture to process fees. In a second phase, we migrated Mainnet, Avalanche and Base fee processing to their smart vault v3 architecture as ratified in [[BIP-488]](https://snapshot.org/#/balancer.eth/proposal/0x897aba7b7f3a68867595fea782931da3aae10fc15c62d8ace8cbd8e923ac07c4). One can review[ [BIP-294]](https://forum.balancer.fi/t/bip-294-authorize-mimic-smart-vault-on-arbitrum/4779) which authorized Mimic on Arbitrum for more information on the particulars of v2, as well as [[BIP-115]](https://forum.balancer.fi/t/bip-115-balancer-smart-vaults-fee-collector/3966) for the original development plan.

Given the success of the fee processing automation program, we propose to further authorize the Mimic smart vault v3 on Arbitrum, Polygon and Gnosis. Permissions of the currently in use smart vault v2 will be revoked once smart vault v3 fee processing is fully operational.

## Specification

### Arbitrum

The DAO Multisig on Arbitrum `0xaF23DC5983230E9eEAf93280e312e57539D098D0` will interact with the Authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` and call grantRole with the following arguments:

role: `0x93b1b7dba9fb074b573d5edb3c983e0490a00925f709289485f0c75988e100cf`

which corresponds to

====================================================================================================
[85] id=0x6b7042ca6b93fea257320f21fc4934ac27544dc4d07738761561c95db3bdeb8a  token=BAL  space=balancer.eth  date=2024-03-07
TITLE: [BIP-558] Increase BD vlAURA Allocation
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# Summary

The BD Service Provider (BDSP) is seeking approval to raise the percentage of vlAURA allocated for strategic initiatives from 20% [[BIP-508]](https://forum.balancer.fi/t/bip-508-utilize-locked-aura-to-support-ecosystem-growth/5419) to 100%.

Balancer DAO currently has 1.7m vlAura as a result of [BIP-551](https://forum.balancer.fi/t/bip-551-claim-and-relock-balancer-daos-aura-vlaura/5588).

This represents about 5.77% of vlAura voting weight and represents 2-3% of total veBAL votes.

# Motivation

The BDSP was established in January 2024 under [BIP-525](https://forum.balancer.fi/t/bip-525-business-development-funding-proposal-q1-2024-and-retroactive-q4-2023-funding/5481/4). Since then, significant effort has taken place to onboard new partners, bootstrap new pools, and explore new growth opportunities for Balancer. See the BD SP January Update [here](https://forum.balancer.fi/t/business-development-sp-january-2024-update/5583) for an update as of mid February.

With the pipeline continuing to grow and the market heating up, it’s clear the 20% of vlAURA eligible for BD use is getting spread too thin to be impactful for these new partners and pool types. Further, unforeseen use cases for vlAURA, such as the recent rETH migration, eats into the BD allocation hampering the dry powder Balancer can use for partners.

Considering the present market conditions, the influx of new partnerships, interest from additional chains seeking Balancer deployments, demand from existing

====================================================================================================
[86] id=0x603b2b2b1983506936d5263c42a5e7a520d5d1a32f728a584ae4b2098056eacf  token=BAL  space=balancer.eth  date=2024-03-14
TITLE: [BIP-559] Enable ezETH / wstETH [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/840

**Summary:**
Renzo Protocol proposes a Balancer Gauge for a ezETH-wstETH pool on Arbitrum, with uncapped emissions. This will serve as a 100% yield bearing pair.

**References/Useful links:**

* Website: https://www.renzoprotocol.com
* Documentation: https://docs.renzoprotocol.com
* Github: [Renzo-Protocol · GitHub](https://github.com/renzo-protocol)
* Discord: [Discord](https://discord.com/invite/renzo)
* Twitter: https://twitter.com/RenzoProtocol
* $ezETH Token (Arbitrum): [ezETH (Renzo Restaked ETH) Token Tracker | Arbiscan](https://arbiscan.io/token/0x2416092f143378750bb29b79ed961ab195cceea5)
* Dune Dashboards: https://dune.com/maybeYonas/renzo-protocol

**Protocol Description:**

[$ezETH] is a Liquid Restaking token and Strategy Manager for EigenLayer

Renzo is the interface to the EigenLayer ecosystem securing Actively Validated Services (AVSs), offering a higher yield than ETH staking.

Renzo introduces the Balancer Gauge for the Renzo [ezETH/wstETH 50/50 pool]. ezETH, Renzo’s liquid restaking token (LRT), captures rewards, ensures liquidity, and simplifies reward management with AVSs. This approach ensures a user-friendly DeFi experience where participants deposit ETH into the liquidity pool, mint ezETH, accumulate rewards, and seamlessly engage in other DeFi activities. Renzo is on a trajectory toward a permissionless validator set, emphasizing composability in DeFi.

**Motivation:**

Renzo i

====================================================================================================
[87] id=0xef5059ed81c831d20c75ccd591a728a270444d685bd1ee6b3429bb9d7de7775f  token=BAL  space=balancer.eth  date=2024-03-20
TITLE: [BIP-561] Enable Gauge for genETH/wstETH [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/844

**Summary:**
> This is a proposal on behalf of GenesisLRT to enable a gauge for genETH/wstETH on Ethereum. genETH is Genesis' Restaked Token, obtained through GenesisLRT’s restaking mechanism and platform.
GenesisLRT offers a revolutionary process called 'Restaking' that supercharges users’
ETH by enabling them to stake their ETH on not just one, but multiple networks at once,
thereby maximizing their rewards.

**References/Useful links:**

> Link to:
    • Website: https://www.genesislrt.com/
    • Documentation: https://docs.genesislrt.com/
    • Github Page: https://github.com/genesislrt/contracts
    • Communities: https://twitter.com/Genesis_LRT, Discord: https://discord.com/invite/DCTWmhgBXr

**Protocol Description:**

> GenesisLRT offers a revolutionary process called 'Restaking' that supercharges users’
ETH by enabling them to stake their ETH on not just one, but multiple networks at once,
thereby maximizing their rewards. It applies a novel concept called “EigenLayer” to
empower users to restake their assets, whether it’s pure ETH or liquid staking tokens
(LSTs) from their existing stake. This not only earns them extra profits but also bolsters
the security of the network. Additionally, Genesis allows users to unlock the restaked
liquidity with the liquid restaked token genETH.

>With Genesis, users will have the possibility to have a customizable restaking
experience by being able to choose

====================================================================================================
[88] id=0x16efb32f66f58ce4ae5987f82ee28eb357f7c3720069167db862d2b622d7afa0  token=BAL  space=balancer.eth  date=2024-03-20
TITLE: [BIP-566] Year Three Funding Proposal for the Balancer Foundation
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# Summary

This proposal is for the funding of the Balancer Foundation for year three.

As a recap, the Foundation provides the DAO with an additional mechanism for executing work in a decentralized environment, and supports resilience across the Balancer Ecosystem.

The Balancer Foundation is a traditional legal entity that is directed by the DAO. It helps create a sustainable environment where many groups of people can participate. It allows the DAO to operate at a larger scale and engage with service providers who require formal contracts, and is able to take certain actions that a DAO is unable to perform on its own behalf.

The Foundation and its operating subsidiary (Balancer OpCo Limited) act as facilitators of the Balancer Ecosystem. This governance structure, at the direction of the DAO, can leverage other teams to execute work that can further the adoption of the Balancer Protocol – for example, the front-end team or other technology providers.

In short, the Balancer Foundation acts as an agent for the DAO and part of the DAO’s governance within the structure of the traditional business world.

The Balancer Foundation operates within a formal environment (The Foundation Companies Act) in the Cayman Islands and thus brings protection and certainty that comes with formal organizations.

# Specification - Foundation expenses and reserves

The budget identified for the Foundation is line-item specific and includes very few estimates. The Foundation has, however, assist

====================================================================================================
[89] id=0x4c9889961c9fc2871c19f49a274894c9c7cb9ed2eb8e630cd2f83124a7cdce8f  token=BAL  space=balancer.eth  date=2024-03-20
TITLE: [BIP-567] OpCo Admin & Ops supplementary budget for Q2 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# Service Provider / Organisation Name & Overview:

Balancer OpCo Limited (or the “Balancer OpCo”) is a wholly owned operating subsidiary of the Balancer Foundation. It is an integral element of the Balancer Foundation corporate structure supporting the Balancer DAO. It serves three primary functions: (1) Administrative and Operational; (2) housing Ecosystem and Protocol infrastructure; and (3) Product Development.

The OpCo budget is approved until the end of June 2024 under [[BIP-349]](https://forum.balancer.fi/t/bip-349-funding-proposal-for-the-balancer-opco-administrative-and-operational-for-year-2-fy23-q3-through-fy24-q2/4923). This proposal deals with changes to the Administrative and Operational (Admin & Ops) element of the OpCo, that goes hand and hand with the Foundation, seeking additional budget allocation to shift personnel currently being funded in [the Maxis](https://forum.balancer.fi/t/bip-514-fund-balancer-maxis-q1-2024/5420) and services previously budgeted under the [Product](https://forum.balancer.fi/t/bip351-funding-proposal-for-the-balancer-opco-product-team-fy23-q3-through-fy24-q1/4927) team.

The changes introduced this quarter present cost-savings opportunities to the ecosystem as a whole, reducing the Treasury’s burn rate. For full reference, please refer to these funding proposals from this round:

* [Foundation](https://forum.balancer.fi/t/bip-xxx-year-three-funding-proposal-for-the-balancer-foundation/5627)
* [Maxis](https://forum.balancer.fi/t/bip

====================================================================================================
[90] id=0x349cf3039e47a6eabcb9bf6b09e943c05d37d8acb7e0940304be9c7d5dac01d6  token=BAL  space=balancer.eth  date=2024-03-27
TITLE: [BIP-573] Fund Balancer Grants for Q2 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/870

## TL;DR

With V3 development ongoing, the grants program requests full funding to target new V3 integrations. This quarter’s focus will be to find, fund and launch projects with Balancer V3 to help boost wide adoption.

There are no major changes to the program and the committee will continue to focus on funding in line with the findings in the [historical assessment report](https://forum.balancer.fi/t/balancer-grants-program-all-time-recap/5458). Main points:

* Funding duration 3 months from April 1st to June 30th, 2024.
* Funding for new grantees - 75k BAL
* Funding categories identified in 2023 Q4 Program Recap
* Attract more projects to build on V3 and port over pools from V2
* Run V3 bounty program (details to come closer to V3 launch)

With the recovery of funds from stale grants and an increase in BAL price, a small amount of funding is requested to top up the treasury (currently 68,190 BAL uncommitted) to

1. 75,000 BAL for new grantees (6,809 BAL top up)
2. 38,400 USDC for committee/support (29,400 USDC top up)

As always, we welcome comments and recommendations from the community on how to better develop the Balancer grants program.

______________________________________________________________________

Service Provider Name: Balancer Grants

Leader(s): Burns, with committee members John Grant, Mike B, Steve0xp and Zen Dragon.

Pledge to abide by the DAO’s Code of Conduct 1 (or link to yo

====================================================================================================
[91] id=0xa1f76b92cd658aafbaa6a7ca4218bca564df75a6ff200536b376ffc3e83c3d0c  token=BAL  space=balancer.eth  date=2024-03-27
TITLE: [BIP-577] Enable pufETH/wstETH [Ethereum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/872

**Summary:**

> Puffer Finance is a unique solution introduced in the heart of the liquid restaking craze the has been sweeping the Defi ecosystem. The purpose of this gauge is give pufETH holders a place to keep their liquidity and not be susceptible to rate arbitrage over time, while earning yield on wstETH and via Balancer's core pool infrastructure
>
>
>
> This gauge is uncapped, and would enter as a “core pool” under [BIP-19](https://forum.balancer.fi/t/bip-19-incentivize-core-pools-l2-usage/3329).

**References/Useful links:**

> *pufETH*
>
>
>
> * [Website ](https://www.puffer.fi/)
> * [Documentation](https://docs.puffer.fi/)
> * [Github Page](https://github.com/PufferFinance)
> * [Twitter](https://twitter.com/puffer_finance)


**Protocol Description:**

> Puffer is a native liquid restaking protocol (nLRP) designed to optimize the potential of restaking, built on Eigenlayer. It offers a comprehensive framework for stakeholders, including Stakers and Node Operators (NoOps), to engage in decentralized validation while enhancing rewards and safeguarding Ethereum's ethos.

The protocol's design encompasses various components:

1. Protocol Features:
  * Permissionless operation allows anyone to become a validator on Puffer, promoting accessibility.
  * Native Restaking introduces the first liquid restaking protocol on Eigenlayer.
  * Ethos Alignment ensures the protocol's self-capping mechanism to

====================================================================================================
[92] id=0xe04f0c88c95f24c1cac5a816f4d702fdbeb2316c1a05bddd307298008b4aceb8  token=BAL  space=balancer.eth  date=2024-04-04
TITLE: [BIP-584] Enable PRF/WETH (80/20) Gauges with 2% emission cap (Arbitrum)
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/888

**Summary:**
This proposal suggests activating a Balancer gauge for the PRF/WETH (80/20) pool on Arbitrum.

**Protocol Description:**

Parifi is a novel perpetual protocol that introduces an innovative pricing mechanism for perpetual contracts. It leverages liquidity curves and on-chain oracles to dynamically adjust prices based on current market conditions. By using advanced mathematical models like parabolic and sigmoid functions, it offers more predictable and stable pricing and fees, considering factors such as liquidity and active trading positions.  

**Motivation:**

Parifi Finance aims to boost liquidity within its Balancer pool. Recent observations indicate that insufficient liquidity has led to price volatility for Parifi. Implementing a gauge and incentives through Hidden Hand could encourage greater liquidity within the Parifi Balancer pool. Parifi DAO initially provided liquidity for the pool and retains a share of the current liquidity. By introducing a gauge and incentives, Parifi DAO could also accumulate BAL tokens through gauge emissions. 

**Specifications:**
 
1. **Governance:**                                                                                                                        Parifi currently operates with a multi-signature wallet [GnosisSafe | Address](https://arbiscan.io/address/0x009ed9DF75B3426F8F082c02548fE9a03F6cCE75). The protocol is planning to decentral

====================================================================================================
[93] id=0x635babdb06710653d04fd84b67cb4c4440c957a88e0a66b7d1785c150af1a27c  token=BAL  space=balancer.eth  date=2024-04-18
TITLE: [BIP-590] Jellyverse Friendly Fork Proposal
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# Dear Ballers!

The Balancer Team and Jellyverse community have met in recent weeks to explore an exciting opportunity! JellySwap, the decentralized exchange within Jellyverse, wishes to become a friendly fork of Balancer on Sei V2!

## Jellyverse at a glance

*[Want to try out Jellyverse yourself? Check out: [app.jellyverse.org](http://app.jellyverse.org) (under construction)]*

Jellyverse addresses the limitations of many DeFi protocols by providing users with the opportunity to gain exposure not only to highly volatile cryptocurrency assets but also to both **synthetic** and **non-synthetic** real-world assets (RWA).

**Jellyverse** consists of multiple protocols and aims to become one of the biggest DeFi-Hubs, optimized for RWAs integration & highly flexible usage of liquidity. The platform's decentralized exchange (JellySwap), built on the well established Balancer protocol leverages Balancers **highly flexible** pool architectures to facilitate the creation of comprehensive **portfolio pools**.

Synthetic assets are crafted using the **jAsset** protocol, enabling users to easily mint tokens representing stocks, commodities, and more. Non-synthetic RWAs classified as commodities are offered through partnerships and are backed by tangible assets.

Consequently, users have access to a broader spectrum of assets, moving beyond the typically volatile cryptocurrency markets to enhance their DeFi experience.

Jellyverse operates on a permissionless basis, welcoming contributi

====================================================================================================
[94] id=0xdd19c8071cdcc3ee4a9e5ca8d11a4c4f8d4036b37cc58728fa2fc907f0f3fc3e  token=BAL  space=balancer.eth  date=2024-04-18
TITLE: [BIP-591] Generating USDC revenue for the treasury via BAL covered call lending on MYSO
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/904


**TL;DR**
We propose utilizing idle treasury-owned BAL to engage in covered call lending using [MYSO Finance](https://www.myso.finance/): this would allow Balancer to generate significant stablecoin revenue, diversify part of its treasury and earn cash upfront without having to wait until loan expiry. In contrast to simply selling tokens, there's no immediate market impact. All loan execution happens through MYSO smart contracts and is trustless and fully transparent with full on-chain traceability.

**Proposal author - MYSO Finance**
MYSO is a decentralized peer-to-peer lending protocol that specializes in custom loans that allow users to borrow and lend with any ERC20 token. In addition, the protocol can support a wide range of different on-chain structured product strategies like synthetic token buybacks and covered calls. MYSO has recently facilitated several on-chain covered call strategies for treasuries/users, including one with [Telos treasury](https://medium.com/mysofinance/myso-x-telos-treasury-covered-call-strategy-launch-59f3a993dca7) and [Evmos community treasury](https://commonwealth.im/evmos/discussion/14699-generate-usdc-revenue-by-lending-part-of-evmos-treasury-through-covered-calls).

The protocol currently holds a [TVL of ~$2.2m](https://defillama.com/protocol/myso/) and is currently live on Ethereum, Arbitrum, Mantle, Evmos, Telos, Linea and Neon EVM. The protocol originated from

====================================================================================================
[95] id=0xd13ba8f3cff914b5d99bc610ec0dfa6290a30eceddd3be2e0e518d75138e9b13  token=BAL  space=balancer.eth  date=2024-05-15
TITLE: [BIP-607] Update FTM Multisig to Claim vested BEETS
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Payload with PR
https://github.com/BalancerMaxis/multisig-ops/pull/916

Overview

Originally when BeethovenX was approved as a friendly fork 10 million BEETS was set aside for the DAO to unlock via a vest. This can be seen here in the original vote. https://vote.balancer.fi/#/proposal/0x95db8e797145ad590b467f8dbecb23404c25c2a7090aa8a8d65428ad9f7373fc to receive 4% of the total supply, 250M tokens, which can be confirmed in BEETS [tokenomics](https://docs.beets.fi/beets/tokenomics). The purpose of this proposal is to update the fantom wallet responsible for this vesting contract with the maxis as signers. The maxis will then claim the fully vested balance of BEETS, and transfer it to the DAO Multisig on Optimism. This is to make the bridging process streamlined. For the time being this will consolidate the multisigs utilized by the DAO as fantom is a relatively inactive network. There is no plan to utilize the BEETS tokens in any way for the time being, but an additional proposal can be made to do so at a later time.

The current DAO Multisig on Fantom will not be utilized after these actions unless absolutely necessary after this proposal. The likelihood of it's use is incredibly low due to the networks activity, and Balancer's influence in the Fantom ecosystem.

Specifications

The DAO Multisig ftm: `0xFe2022da08d17ac8388F5bEFE4F71456255105A4` will call `addOwnerWithThreshold` on itself six times, with the `threshold` equal to `6` and the following new `owner` addresses:

`0

====================================================================================================
[96] id=0xaa71cbfadc894d5ddb14a21b2ee38821a9c9b56ef1211f854d68eeccbaaa931b  token=BAL  space=balancer.eth  date=2024-05-23
TITLE: [BIP-611] Delegate BalancerDAO ARB to karpatkey
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Payload with PR
https://github.com/BalancerMaxis/multisig-ops/pull/982

title: [BIP-611] Delegate BalancerDAO ARB to karpatkey
author: karpatkey
created: 2024-05-15

## Summary

This proposal aims to delegate the [2M](https://arbiscan.io/address/0xaf23dc5983230e9eeaf93280e312e57539d098d0) ARB voting power held in the Balancer DAO treasury to karpatkey's delegation multisig. This voting power will be actively used by karpatkey in the Arbitrum governance process.

## Abstract

Since the passing of [[BIP-103]](https://snapshot.org/#/balancer.eth/proposal/0xddc174b931a0d2e5e32276a3d0d7110367797dd24248f078d0f7876d0987c92f), karpatkey has been serving as the treasury manager for Balancer DAO, a role that involves active governance interaction. In this capacity, karpatkey has engaged in governance across various protocols and chains. The Balancer DAO has recognised our expertise and commitment, selecting us through the [BIP-452](https://snapshot.org/#/balancer.eth/proposal/0x3a8d63ce6dbebf9b559fcd1acb367ce0c1625b805bde893b62c5a2ba2e827cbc) to be your delegate on Aave. Since December 2023, karpatkey has also been an active delegate in the Arbitrum DAO, contributing to the launch of their Arbitrum delegation [platform](https://forum.arbitrum.foundation/t/karpatkey-delegate-communication-thread/20085).

As delegates in Arbitrum, we have [provided research](https://forum.arbitrum.foundation/t/arbitrum-treasury-and-sustainability-research/20630) to the Treasury and Sustainability working

====================================================================================================
[97] id=0x34f21bba6d0dac30d29d3e92ffb46bd45aec6127901e07ce59d0900ed49a4b94  token=BAL  space=balancer.eth  date=2024-05-30
TITLE: [BIP-613] Wire up permissions and initial configuration for Mode and Fraxtal chains
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## Payload PR - BIP-613
https://github.com/BalancerMaxis/multisig-ops/pull/997

## Background
This BIP is to add permissions to the Balancer Multisigs as described in the payload PR linked above in order to enable the protocol to operate on [Fraxtal](https://forum.balancer.fi/t/bip-608-deploy-balancer-on-fraxtal/5746) and [Mode](https://forum.balancer.fi/t/bip-589-enable-balancer-deployment-into-mode/5681).

It is similar to other permissions BIPs such as [BIP-388](https://forum.balancer.fi/t/bip-388-wire-up-base-chain-in-preparation-for-launch/5026) for Base and [BIP-318](https://forum.balancer.fi/t/bip-318-grant-avalanche-permissions/4846) for AVAX.

## Specifications

This BIP includes a number of payload files that perform various functions required to get a chain up and running.  The payloads can be found with reports in the PR linked above, and are described in the tables below.

The transaction details for `00fraxtal.json` and `00mode.json` were generated by [this script](https://github.com/BalancerMaxis/multisig-ops/blob/main/action-scripts/gen_add_permissions_payload.py) with inputs and outputs in [this directory](https://github.com/BalancerMaxis/multisig-ops/tree/staging/BIPs/BIP-613).  These files were amended with transactions to set protocol fee percentages to 50% after generation. 

The following files can be found both linked below and in the payload PR linked above:

| Filename

====================================================================================================
[98] id=0x95c829194d909e045988bcf3481d8b2706b8dc2c0486da087736e58ec8585108  token=BAL  space=balancer.eth  date=2024-05-30
TITLE: [BIP-617] Request for BAL to reward UI beta testers
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1002

# Beta UI Test Rewards

## TL;DR
- OpCo is ready to begin beta testing a new and improved Balancer UI. We’re calling this Project Zen.
- We would also like to take the opportunity to invite old friends, community leaders, and partners to be part of the process of bringing the next iteration of Balancer to life/market.
- This BIP requests 1000 BAL to reward Beta Testers in a closed beta through [Coordinape](https://coordinape.com/).
- The Beta test will consist of under 250 users, selected by various SPs and partners.

## Background

The current V2 Balancer UI has served the Protocol and its users well for over 3 years, however, as Balancer has expanded cross-chain, its approach to segregated chain handling has made it feel dated and creates difficulties in understanding the entire protocol. Further, support for the upcoming release of Balancer V3 required a total refactor of transaction flows, and the ability to handle pools on 2 different sets of contracts.

OpCo has been working over the last year to get this new UI ready and now we are looking to collect and implement user feedback before the official launch. 

The last few months at Balancer have been somewhat inward-focused.  We have been hyper-focussed on v3 and so our community engagement has been lacking. Therefore, we would love to invite our old friends to come back, help us bring some new DeFi tooling to market, and help us create a tribe

====================================================================================================
[99] id=0xbd9c09b49e3ad7661903f21d14cdfd06deab8fba92677423cbf050634d8634f2  token=BAL  space=balancer.eth  date=2024-06-19
TITLE: [BIP-630] Fund Balancer Maxis for Q3 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1069

## Introduction

![ethMaxi.jpg](ipfs://bafybeicvsvxykkf7mhrbht4idfm5c2zs2u376rrjhe725lf4iidcsu64oy)

The Maxis have firmly established themselves as the on-chain operators for the Balancer DAO. By evolving into a DevOps powerhouse with a strong focus on automation, we are strategically positioned to meet the challenges of Balancer's ambitious expansion plans.

As Balancer gears up for a transformative phase, with innovative products slated for release in Q3 and Q4 2024, the Maxis are ready to lead the charge. Exciting developments on the horizon include the groundbreaking CoWAMM technology and the highly anticipated v3 installment of Balancer tech. Our team is dedicated to ensuring a seamless integration experience for partners and uninterrupted operations of the protocol.

To achieve this, we will lay a robust foundation for all on-chain operations needed for these new products while maintaining and optimizing the current infrastructure with utmost efficiency.

## Initiatives

Organizing initiatives into work packages has significantly enhanced our ability to focus on specific operational domains with clear deliverables. Moving forward, we will concentrate our efforts on two key work packages that promise high-value outcomes for the DAO.

### Initiative 1: On-Chain DevOps Hub

**Co-Leads: Xeonus & Tritium**

**Team: gosuto, Zekraken, Zen Dragon (and freelancers)**

#### Summary

With our increased d

====================================================================================================
[100] id=0x465fdb18596c6aa5088f3651296cd066d418d99f6c1132184188c1f84f0a559b  token=BAL  space=balancer.eth  date=2024-06-19
TITLE: [BIP-633] Fund Balancer Grants Q3 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1072

# Balancer Grants DAO Service Provider Proposal Q3 2024

## TL;DR

** Updated with revised compensation.**

With V3 set for imminent public code release, the grants program requests funding to target new V3 integrations, create a hook bounty program and partner with ecosystems to build more on Balancer with the new and improved DX. This quarter’s focus will be to find and fund projects launching on Balancer V3 to help boost wide adoption.

With this launch pending and a long history of performance, the committee requests funding for 3 months to continue to focus on funding in line with the findings in the [historical assessment report](https://forum.balancer.fi/t/balancer-grants-program-all-time-recap/5458). 

Main points:

* Funding duration 3 months from July 1st to September 30th, 2024.
* Funding for new grantees - 75k BAL
* Grants lead compensation reduced by $3k, committee members to contribute pro bono
* Funding categories identified in 2023 Q4 Program Recap
* Attract more projects to build on V3 and port over pools from V2
* Run V3 hook bounty program
* Partner with supported chains for co-funding and more visibility

With unspent BAL in the treasury and the recovery of funds from stale grants, funding is requested to top up the treasury (currently 41,473 BAL uncommitted) to:

1. 75,000 BAL for new grantees (**33,527 BAL top up**)
2. 15,000 USDC for committee/support (**6,900 USDC top up**)

A

====================================================================================================
[101] id=0xcb7e2ff7c8dd1a8273a7a2ec6297710d4e42238d2b2557cc18d82a0736815896  token=BAL  space=balancer.eth  date=2024-06-19
TITLE: [BIP-635] Business Development SP Proposal for Q3 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1074

### Background

The establishment of the Business Development Service Provider (BDSP) took place in Q1 2024 under [BIP-525](https://forum.balancer.fi/t/bip-525-business-development-funding-proposal-q1-2024-and-retroactive-q4-2023-funding/5481)  with the intent of forming a dedicated working group focused on business development and growth-oriented activities.

During Q2, the primary goals for the BDSP focused on growing the Balancer ecosystem and creating new partnerships. Please find updates from [April](https://forum.balancer.fi/t/business-development-sp-april-2024-update/5734) and [May](https://forum.balancer.fi/t/balancer-business-development-service-provider-may-update/5784/2) in the links attached.

### Key Objectives for Q3-2024

Lead Contributor: lipman

* Execute the launch of Mode and Fraxtal
  * Build liquidity on new chains
  * Implement, monitor, and adjust incentive strategies on new chains
  * Establish a comprehensive partnership network and ecosystem on the new chains, encompassing liquidity providers and networks, yield-bearing assets, lending protocols, etc.
  * Complete governance requirements for various activities (e.g Frax for PoL deploying on Balancer)
* Enhance presence on existing chains
  * Develop, coordinate, and execute growth initiatives on Layer 2 solutions for existing chains, focusing on Arbitrum, Optimism, and Base networks.
* Expand the yield-bearing thesis initiat

====================================================================================================
[102] id=0x29e28cd092b63175ba81bba3ef367589ab5338aac6df467a4b13f3dd4426f628  token=BAL  space=balancer.eth  date=2024-06-27
TITLE: [BIP-649] Enable TXAU:USDC; TXAG:USDC; TXAU:TXAG:WETH Gauges with 2% emissions cap [Polygon]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR with Payload:
https://github.com/BalancerMaxis/multisig-ops/pull/1112
RWA toolkit for Gold and Silver on Balancer.

**Summary:**

Aurus provides the tech infrastructure for Web3 businesses to secure their protocols, treasuries, products and token economics with stable, real-world value, in the form of tokenized Gold and Silver. 

Our vision is to become “The Value Layer of Web3” - innovating with RWA’s in Defi, Gaming and Digital Collectibles.

Aurus takes a decentralized approach, as we only partner with trusted precious metal providers. The Aurus Foundation performs KYC / KYB / AML - to ensure that only verified actors can provide the highest quality metals to the Aurus ecosystem. These metals are verified, audited and stored with top tier 3rd party custodians, in locations like: London, Zurich, Madrid.

The below pools are intended to be the primary source of liquidity for the Aurus ecosystem and subsequent RWA Alliance partners, driving the majority of traded volume to Balancer.

**References/Useful links:**

Pools: 

TXAU:USDC
**https://app.balancer.fi/#/polygon/pool/0x98f9220f128eed5e853cd3d23a2c33e1f98f8311000200000000000000000e55**

TXAG:USDC
**https://app.balancer.fi/#/polygon/pool/0x31ac27805b0665695071b640bf2abfbe0736c02e000200000000000000000e56**

TXAU:TXAG:WETH
**https://app.balancer.fi/#/polygon/pool/0x418681127fb0c4fb5ee01202fbe4ab8c8f4eb84a000100000000000000000e59**

TXAU:USDC Polygon Root Gauge: **https://etherscan.io/address/0x5787A5bADC53663F3f039C5fcA68

====================================================================================================
[103] id=0x5869cec1214f344fed63864a14aa56c1663f4469a34e4f7b94eaa5e1bd4ecd8a  token=BAL  space=balancer.eth  date=2024-07-03
TITLE: [BIP-653] Build a paylod for Paladin’s bribe to liquidity mining
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1107

**Tldr:**

Build a payload to enable Inverse and Threshold to take advantage of Paladin’s latest feature, bribe to liquidity mining, for their veBAL gauges.

**Context:**

Paladin quests provide DAOs with the ability to failover incentives intended to buy veBAL votes to direct incentives in cases where the target ROI is not reached through buying votes. As part of this process a number of gauges listed below were set up by the Balancer Maxis to allow Paladin’s questboard contract to distribute direct rewards in the required tokens. This work has revolved around work with Inverse Finance and Threshold who are customers of Paladin.
Paladin has upgraded to a new version of the questboard, and a new contract needs to take over the ability to distribute tokens. The quest contract does not have the capability to renounce its distributorship. This BIP therefore requests that the DAO multisig execute a transaction to move distributorship on the below mentioned gauges to the new Paladin quest contract.

**Rationale:**

Inverse Finance and Threshold are incentivizing liquidity provision across various pools, including DOLA/USDC, PYUSD/DOLA and sDOLA/DOLA for Inverse and 80/20 tBTC, base-tBTC+wETH, Arbi 50tBTC-50WETH, arbi-WBTC+tBTC and 2BTC for Threshold through veBAL voting incentives. Recently, the effectiveness of these voting incentives has turned net negative in free markets due to the correlation between

====================================================================================================
[104] id=0xc2a441f36eddac49a1ca2ed865a017cdf3f2068090db4d1b390a96667b5620ca  token=BAL  space=balancer.eth  date=2024-08-07
TITLE: [BIP-667] Roles V2 Migration & New Treasury Permissions
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1154

# Abstract

This proposal aims to roll out an updated version of the Zodiac Roles Modifier module. The new version improves usability and transparency of treasury management operations. Upon approval, the Roles Modifier v2 module will be activated.

Furthermore, this proposal requests authorization from the DAO to revise the permissions policy. A notable change includes enabling swapping actions on CoW Swap while the other permissions primarily focus on eliminating obsolete actions and protocols, and refining parameters within the existing permissions.


# Roles v2 Migration


## Motivation

The Zodiac Roles Modifier facilitates karpatkey’s proxy management of the treasury by ensuring that only pre-approved transactions, defined by the permissions policy voted on by the DAO, can be executed. In collaboration with karpatkey, the Gnosis Guild team has significantly upgraded the Zodiac Roles Modifier module and the Zodiac Roles app. These enhancements have resulted in a more powerful and robust on-chain permissions infrastructure with the following improvements:



* **Introduction of Allowances**: Implementation of spending limits within permissions.
* **Enhanced Call Data Scoping Toolset**: This toolset considerably broadens the range of functions that can have permissions set, increasing flexibility.
* **Advanced Logical Conditions**: Allows for the creation of complex permissions structures to accom

====================================================================================================
[105] id=0x662a637bc008e251513487926ed28e5c40f65747a9da2d26c37573f16eebb5d8  token=BAL  space=balancer.eth  date=2024-08-07
TITLE: [BIP-670] Update the Optimism Fees + LM Multisig to include Beethoven X signers
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1224

**Motivation:**

Based on the partnership between Balancer and Beethoven X, the joint deployment on Optimism is managed by Beethoven X. Up to now, there was no formal agreement that grants Beethoven X the power to distribute liquidity mining incentives on behalf of Balancer. This BIP grants permission to Beethoven X to distribute incentives, such as grants, on the Optimism chain and therefore adding Beethoven X Contributors to the Balancer Optimism Fees + LM multisig. This grants Beethoven X the power to enact the responsibility to operate the Optimism deployment.

This proposal aims to update the multisig to a 3/6 multisig with 3 signers from Beethoven X and 3 signers from Balancer.

**Specification:**

Update the Optimism Fees + LM Multisig 0x09Df1626110803C7b3b07085Ef1E053494155089 to require three out of six confirmation with the following signers:

Zendragon: 0x7c2eA10D3e5922ba3bBBafa39Dc0677353D2AF17

Xeonus: 0x7019Be4E4eB74cA5F61224FeAf687d2b43998516

Tritium: 0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F

Franz: 0x89c7D6ABA9Cd18D8A93571E583EEAc58Da75acE6

Ardo: 0x693f30c37D5a0Db9258C636E93Ccf011ACd8c90c

Netrim: 0xa01Bfd7F1Be1ccF81A02CF7D722c30bDCc029718

====================================================================================================
[106] id=0xb07ab604b5d172c4576e184164ed4b9132ebfeeb7f1fadc4972fced16d44455c  token=BAL  space=balancer.eth  date=2024-08-07
TITLE: [BIP-675] Enable Several E-CLPs [Arbitrum]
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR with Payload:
https://github.com/BalancerMaxis/multisig-ops/pull/1229

> # Summary
> 
> * **This is a proposal to enable five uncapped Balancer gauges for the following Arbitrum pools:**
>   *  sUSDe/GYD
>   * rETH/wstETH
>   * aGHO/GYD
>   * wUSDM/aUSDC
>   * sFRAX/aFRAX
> * **Every one of the pools is an Elliptic Concentrated Liquidity Pool (E-CLP)**. E-CLPs are custom pools from Gyroscope built on top of Balancer’s pool architecture. They enable trading along the curve of an ellipse. This pool type is ideally suited for stablecoins and liquid staking tokens; is typically more capital efficient and could thus generate significant trading volume.
> * **GYD is an all-weather stablecoin that provides one-stop access to stablecoin risk control.** GYD is fully backed by a set of assets with fundamental innovations in risk control built in at the protocol level to automate diversification and redundancy.
> * **Each pool shall be a ‘Core’ pool.** The fee split is as follows: 50% of all collected fees will go to liquidity providers, while the remaining 50% will go towards Balancer. At pool inception, no fees will go towards Gyroscope. As a Core pool it will be eligible for fee recycling.

> # References/Useful links
> 
> * [Slidedeck on E-CLPs](https://docs.google.com/presentation/d/16Qt-8PaLJ_1FkaNnI4rocEYUDrG1ktW3u4R6yeSwY68/edit#slide=id.g208e5b00ffd_0_95)
> * [Documentation of E-CLPs](https://docs.gyro.finance/gyroscope-protocol/concentrated-liquidity-pools/e-clps#descriptio

====================================================================================================
[107] id=0x3b09eeb26d102d4b30da56094f4bb9ab772242ccfab52b9eb03ca82eec32c343  token=BAL  space=balancer.eth  date=2024-08-29
TITLE: [BIP-685] Grant LM Multisig permission to set_reward_distributor
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR With Payload:
https://github.com/BalancerMaxis/multisig-ops/pull/1294

**Summary**

Grant the LM multisig permission to set the reward token distributor for any reward token on the gauge contracts

**Motivation**

The Gauge contract that is in use by Balancer allows for several additional reward tokens to be added on top of BAL. Each of these reward tokens as a so-called “distributor” assigned which has certain powers:

* Top up the gauge contract with more of the reward token.
* Restart a new epoch for the reward token before the current one is stopped.
* Set the distributor of the reward token to a different wallet address

In addition to the distributor, the DAO multisig is also allowed to change the distributor of any reward token on a gauge, which is used as a backup solution. This is useful if a new reward token was initialized with a wrong distributor address or when the current distributor is not responsive.

If the DAO multisig needs to act on this, it will always require a governance vote which makes the process transparent but also cumbersome. Changing the distributor of a reward token in a gauge is an operational decision and should therefore not require a governance vote but should nevertheless be handled carefully.

This proposal aims to grant the LM Multisig on each chain the power to change the distributor of any reward token on gauges, the same power that the DAO multisig currently has. This helps streamline the operations for reward tokens. The LM multisi

====================================================================================================
[108] id=0xefe9ad3188fc15943894b2935f9fab2469a18bee7b224952785912721d948114  token=BAL  space=balancer.eth  date=2024-09-11
TITLE: [BIP-693] Aegis Finance - Strategic Partnership Proposal
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
1. Summation

Aegis Finance proposes an agreement to collaborate with Balancer within a strategic partnership in exchange for 1% supply of Aegis’ utility token SHIELD to be allocated at the discretion of Balancer DAO.

2. What is Aegis?

Aegis is an upcoming Collateralized Debt Position (CDP) platform launching native to Frax Finance’s Fraxtal Layer 2. The project is fully supported by Frax with the relationship being strong enough to the point Sam Kazemian himself is an official advisor. The platform at its core is operated under a formal licensing agreement with Liquity with their upcoming V2 backend. Upon launch, the team will continue to build upon the concept to build a highly liquid, cross chain lending solution with competitive borrow rates and collateral requirements.

The CDP Market will allow users to borrow against Wrapped Ether, Select Stablecoins and FRAX native assets with multi collateral enabled vaults at a minimum collateral ratio of 110% (90.9% Loan To Value (LTV)). Multi collateral vaults enable users to supply multiple assets within a singular debt position. Within this, users only need to supply sufficient reserves to meet a 100% collateral ratio of external assets in some circumstances. This can occur if users choose to allocate part of their collateral position in SHIELD. Other innovative features will include one click looping leverage for positions, and a platform yield boosting direct incentives layer.

The ecosystem will consist of two tokens, the f

====================================================================================================
[109] id=0x866d1a8a02edd75b7c0cf882bdae6ad072c2a70d837df46471d52c5840c893ac  token=BAL  space=balancer.eth  date=2024-09-18
TITLE: [BIP-694] Fund Balancer Maxis for Q4 2024 to Q1 2025
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Payload with PR
https://github.com/BalancerMaxis/multisig-ops/pull/1354

# Introduction

Over the last 6 months, the Maxis have transformed into a professional on-chain DevOps team, ensuring smooth operations of Balancer technology across chains as well as providing white-glove service to partners in the ecosystem. Our key success metrics are showcased by fast response times to partner requests and successful execution of many initiatives like supporting the launch of CoWAMM, the related incentive program, or the design and execution of token grants. Furthermore, we are constantly improving our technology stack with the ultimate goal of achieving self-service autonomy for most operations.

Given the Maxis are an integral part of Balancer technology and partner management, we aim to switch to bi-annual funding starting in Q4 2024. This provides us with more funding stability and also guarantees that resources for the upcoming Balancer v3 launch will be adequately allocated.

# Initiatives

As with previous funding proposals, we want to make the most impact to Balancer DAO by working on key initiatives with clearly measurable objectives.

As context, you can refer to our last quarters performance reports to evaluate our progress in relation to initiatives executed in Q3 2024 ([July](https://forum.balancer.fi/t/balancer-maxis-monthly-update-for-july-2024/5907), [August](https://forum.balancer.fi/t/balancer-maxis-monthly-update-for-august-2024/5979), reports)

## Initiative 1: Sc

====================================================================================================
[110] id=0x34c9af709dcd8289b13e36efee96613705a6d608891714a90b4b413b08330e7a  token=BAL  space=balancer.eth  date=2024-09-18
TITLE: [BIP-696] Transfer GNO to karpatkey’s Treasury Safe & Authorise Staking on Stakewise v3
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# PR with Payload: 
https://github.com/BalancerMaxis/multisig-ops/pull/1291

# Abstract

This proposal seeks the BalancerDAO to take the following actions:



1. Have the [Balancer’s DAO main Safe](https://app.safe.global/home?safe=eth:0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f) claim the locked GNO in the [GNO locking contract](https://etherscan.io/address/0x4f8ad938eba0cd19155a835f617317a6e788c868).
2. Bridge the GNO from mainnet to Gnosis Chain (GC) using the Gnosis Bridge.
3. Set as destination address karpatkey’s managed Safe, whose [Gnosis Chain version](https://app.safe.global/settings/setup?safe=gno:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89) has just been launched.
4. Grant permission to karpatkey to stake GNO on [Stakewise v3](https://x.com/stakewise_io/status/1816458408041574446).


# Motivation

Following a successful[ Snapshot vote](https://snapshot.org/#/balancer.eth/proposal/0x8d4969e56fa8eb13abc7a3404b3d42fe6b4afa1c7f29111bd012314f093a2fd2) in January 2022, the BalancerDAO and the GnosisDAO conducted a token swap, resulting in 9,051 GNO being added to the DAO’s treasury. These tokens, claimed by the DAO in 2023, have been idle for a year since the locking period expired on February 15th, 2023. Now that Stakewise v3 has launched on Gnosis Chain and offers GNO staking possibilities, it’s a good opportunity to put those idle assets to work.

We propose making them available to karpatkey for yield-generating strategies, specifically staking on the [Genesis Vault](

====================================================================================================
[111] id=0xafca9352e403cf6ddb5a1f99f2ba2f364f5facf7c60ce93415aae1516576f55c  token=BAL  space=balancer.eth  date=2024-09-25
TITLE: [BIP-705] Fund Balancer Grants Q4 2024
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1378

## TL;DR

With V3 in final audits and due for release in Q4 2024, the grants program requests funding to target new V3 integrations, hook building and reformulating our Grants program. With less projects being approved, the structure of the grants program will be changed to allow for decreased overhead, while keeping a funding route open for valuable projects without the DAO having to sift through these applications.

While other SPs move to 6 month requests, the grants program will use this 3 month period to reshape the program for 2025 as an effective vehicle for assisting Balancer develop and meet its roadmap. We have been seeing a decreasing quality of applications and our biggest successes have come from projects with high internal buy-in (Scaffold Balancer, hooks etc), so this quarter we will experiment in tying the grants program more closely to Balancer Labs and the DAO. This is in an effort to enhance ecosystem and community engagement, align more closely with protocol goals and increase meaningful RFPs.

Main points:

* Attract more projects to build on V3 - fund v3 hook building, integrations and custom pools
* Complete retrospective report on grants program to reformulate it. With recommendations and a new proposal structure for 2025.
* Funding duration 3 months from Oct 1st to Dec 31st, 2024.
* Funding for new grantees - 50k BAL (match awarded grants in Q3 + 25% buffer)
* Funding max to $50k

====================================================================================================
[112] id=0x896b41473f5f7f8673f9c6d15f3ed9fcdee8815b4f525accf54856e761c6c0e6  token=BAL  space=balancer.eth  date=2024-10-02
TITLE: [BIP-709] Mode Allocation Mandate
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Background:

[BIP-589](https://forum.balancer.fi/t/bip-589-enable-balancer-deployment-into-mode/5681) signaled that the DAO would like the Balancer protocol deployed on Mode. As a result, a deal was struck between Balancer OpCo and the Mode Foundation for an incentives budget. It was decided not to launch veBAL on Mode due to the lack of capacity in incentive markets, and no clear parties interested in buying into veBAL or vlAURA. Instead it was mutually decided that it would be better to leave some space to try something new.

After speaking with the Mode team and realizing they were considering alternative incentive strategies other than their initial direct incentives and points-based programs, we collectively came to a realization that Mode governance itself could be an 80/20, where voters directed the chain-wide incentives budget between DAOs. This quickly became a workstream where a number of contributors from organizations including Balancer, Mode, Aragon, Hiddenhand, and Aerodrome all came together to ponder what such a meta-game could look like.

Mode Season 3 (veMODE) is about ready to go. This will be a multi-month experiment in VE tokenomics. An experiment that Balancer Contributors have helped architect, and one in which Balancer DAO will compete for incentives, TVL and relevance. It also presents a unique opportunity and case study for how Balancer can be an integral part of a chain-wide incentive and liquidity strategy.

Note that up until now, Balancer has

====================================================================================================
[113] id=0x3d8aff67780637416728bc6428ce2d5e2340d4dc474aa816941e98afd06ef271  token=BAL  space=balancer.eth  date=2024-10-02
TITLE: [BIP-711] Expand Hidden Hand Refund Flexibility
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Background:

Per [BIP-19](https://forum.balancer.fi/t/bip-19-incentivize-core-pools-l2-usage/3329) Hidden Hand has been providing Balancer DAO an incentives recycling discount of 3%. Hidden Hand’s typical fee placed on voting incentives is 4%, however as Balancer’s core pool incentive structure enshrined Hidden Hand to a degree, their team agreed to returning 3% to the [liquidity mining multisig](https://app.safe.global/balances?safe=eth:0xc38c5f97B34E175FFd35407fc91a937300E33860) `0xc38c5f97B34E175FFd35407fc91a937300E33860`. Over time, since these incentives would have technically gone to veBAL holders, the Maxis have been re-injecting the 3% discount as vote incentives for the bootstrapping of liquidity pools when necessary. While not since inception, the Maxis have been tracking the inflow and outflow of these funds from Hidden Hand in this [repository](https://github.com/BalancerMaxis/multisig-ops/tree/2113b142f183bb2d5f7a00b1f8005a9129b67ef5/MaxiOps/brib_rebate_handling).

### Summary:

The intention of this proposal is to give permission to the Balancer Maxis to have increased flexibility using the Hidden Hand rebate it receives to benefit the DAO in a plethora of ways. This would include using the tokens received for veBAL incentives, vlAura incentives, direct incentives, and potentially acquiring BAL in the case the DAO ever chooses to build any sort of token position in the governance ecosystem. The primary intention is to place varying voting incentives and dire

====================================================================================================
[114] id=0x33a8878f7747e4804b18e9363ba3f1bbc7d2a8b9a79e34ab1be5157e5d542c83  token=BAL  space=balancer.eth  date=2024-10-10
TITLE: [BIP-714] Allocate 250,000 USDT to sGYD
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# PR with payload
https://github.com/BalancerMaxis/multisig-ops/pull/1386


# Summary

This proposal seeks approval from the BalancerDAO to allocate 250,000 USDT, currently sitting idle in the [DAO’s main multisig wallet](https://app.safe.global/home?safe=eth:0x10a19e7ee7d7f8a52822f6817de8ea18204f2e4f) following the termination of the Fjord fee share agreement, to the [karpatkey-managed SAFE](https://app.safe.global/home?safe=eth:0x0EFcCBb9E2C09Ea29551879bd9Da32362b32fc89). These funds will be used to acquire the GYD stablecoin, issued by @FTL_labs, the creators of [Gyroscope](https://gyro.finance/). Once acquired, the GYD will be staked to convert into sGYD, unlocking yield-generating opportunities for the DAO's treasury. For more in-depth information, please refer to the original [post](https://forum.balancer.fi/t/bip-xxx-allocate-treasury-funds-of-the-balancer-dao-to-sgyd/5897/1) submitted by @FTL_Labs.

By approving this proposal, the BalancerDAO will tap into a new yield-bearing strategy for its treasury, enhancing capital efficiency and diversifying stablecoin holdings. Moreover, this move will strengthen Balancer's support for a key ecosystem partner, Gyroscope. Gyroscope pools (E-CLPs) have [demonstrated strong performance](https://dune.com/gyro_finance/gyroscope), contributing 8.81% ofBalancer’s volume with only 4.54% of its total TVL.


# Motivation

While the rationale behind this proposal is covered extensively in FTL Labs’ original [post](https://forum.balancer.f

====================================================================================================
[115] id=0x7a451385e49e341dce818927bf36aa35dfc6e42dabe328cb34e873c84fa452e4  token=BAL  space=balancer.eth  date=2024-11-28
TITLE: [BIP-734] Balancer V3 Launch and Protocol Enhancements
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
Contributors: @Marcus and @mendesfabio (BLabs); @danielmk , @naly (Beethoven-X); @ZenDragon ,@Mike_B , @Tritium and @Xeonus (Maxis)

# Summary

The launch of Balancer v3 presents the DAO with an opportunity to optimize its fee model and core operational framework, positioning it to dominate the yield-bearing market and enhance long-term revenue generation and redistribution for LPs, veBAL holders, and the DAO.

Upon approval, this BIP will implement the following changes:

**Balancer v3**

* **Initial Launch:** Mainnet and Gnosis chain  
* **Launch Strategy:** Primary focus on boosted pools technology without base pairing provisioning (e.g. Aave boosted waUSDC:waUSDT instead of standard USDC:USDT)  
* **Timeline:**   
  * Tentative launch end of Q4 2024  
  * Activation of veBAL gauges and core pools in Q1 2025  
  * Expansion to more chains thereafter  
* **Simplified Fee Model:**  
  * Universal fees: 10% on yield, 50% on swaps (enforced via vault[^1])  
  * Core pools require 50% yield-bearing tokens and a minimum $100k TVL[^2]  
  * Non-core pools fee split: 82.5% to veBAL holders, 17.5% to DAO  
  * Core pools fee split: 70% as voting incentives, 12.5% to veBAL, 17.5% to DAO

**Balancer v2**

* Maintaining current fee structure: 50% on yield, 50% on swaps  
* Core pool framework \[2\] adjustments:  
  * Discontinuing non-core pool fee redirect to core pools (as introduced per \[[BIP-457](https://forum.balancer.fi/t/bip-457-core-pool-incentive-program-automation/5254)\])[

====================================================================================================
[116] id=0x2fb5430efb587a4c7895d8b3f6712201592e98c4b2495585c0434578b074f1fa  token=BAL  space=balancer.eth  date=2024-11-28
TITLE: [BIP-735] Enable lpETH/wETH Gauge [Ethereum] with a 2% cap
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1523

**Summary:**

> We propose enabling a Balancer gauge for the lpETH-WETH Stableswap pool on Ethereum Mainnet. This pool will serve as the primary liquidity venue for lpETH, Loop’s yield-bearing ETH derivative.

**References/Useful links:**

> Link to:
> 
> - Website: https://loopfi.xyz
> - Documentation: https://docs.loopfi.xyz
> - Github Page: https://github.com/orgs/LoopFi
> 
> - Token Pair: lpETH / wETH
> - Gauge Address: 0xb7bb16b58b04fe4f8d270430ce57d2a4753993de
> - Pool Address: 0xdcb5ed405a9b11250def047ae8016008fae7d69b
> - Deployment Chain: Ethereum Mainnet
> - Relative Weight Cap: 2%

**Protocol Description:**

> Loop Finance is a specialized lending protocol designed to optimize leverage strategies for DEX LP tokens, with an initial focus on Pendle LP tokens. A key protocol innovation is  lpETH, a yield-bearing ETH receipt token that captures revenue from Loop's lending activities and is collateralized by a diversified index of LRTs. 

When users deposit ETH into Loop, they receive lpETH which can be:
> 
> 1. Staked to earn lending yields
> 2. Locked in dLP (Loop's governance token based on Balancers ve80/20 model) 
> 3. Provided as liquidity in AMM pools
> 
> The lpETH token is designed to always be backed 1:1 with ETH, while growing the Net Asset Value (NAV) through various protocol mechanisms including:
> 
> - Compounding revenue distribution from lending activities
> - Arbitrage opportun

====================================================================================================
[117] id=0xcf81e92a18e3cab3733c493bc5b1056807d229e4c92e4bcfbf3b1542976e9d81  token=BAL  space=balancer.eth  date=2024-11-28
TITLE: [BIP-737] Authorize Mimic Smart Vaults for Fee Processing on Balancer v2 for Polygon zkEVM
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1522

# Motivation

The Maxis have collaborated with Mimic to perform fee processing on Balancer v2 on all deployments except Polygon zkEVM. Processing on that chain was put on hold because of technical limitations which now have cleared up. Therefore, we want to authorize Mimic smart vaults to collect and process fees on that chain for Balancer v2.

The authorization process is the same as for other chains as seen in [[BIP-552]](https://forum.balancer.fi/t/bip-552-authorize-mimic-smart-vaults-v3-on-arbitrum-polygon-and-gnosis/5589).

# Technical Specification

The DAO Multisig on Polygon zkEVM `0x2f237e7643a3bF6Ef265dd6FCBcd26a7Cc38dbAa` will interact with the [Auhtorizer](https://github.com/balancer/balancer-deployments/blob/d81a658c95e0ed3c3724d90dafb40869c9550523/addresses/zkevm.json#L6C21-L6C63) at `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` and call grantRole with the following arguments:

role: `0xcd3768eb08cdc2de2d040f74fb351ccbef01df1d042fa8033e12f224ecc27c4d`

which corresponds to withdrawCollectedFees on protocol-fee-withdrawer, verifiable [here](https://github.com/balancer/balancer-deployments/blob/d280e55dbe0fe4a2570912567fc7ccbf3dbbe1d7/action-ids/zkevm/action-ids.json#L44C64-L44C130)

account: `0x9e5d6427d2cdadc68870197b099c2df535ec3c97`

corresponding to the mimic smart vault - identical on all chains.

Mimic verified the vault based on [these docs](https://mimic-fi.notion.site/Balancer-Fee

====================================================================================================
[118] id=0x95685a92236759db6c682af9b354d457a4e3266d9192f770da320af2aabd58be  token=BAL  space=balancer.eth  date=2024-12-05
TITLE: [BIP-741] Grant V3 Permissions to Maxis and Emergency DAO Multisigs
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
As per [BIP-734](https://forum.balancer.fi/t/bip-734-balancer-v3-launch-and-protocol-enhancements/6168), Balancer V3 contracts have successfully been deployed to Ethereum and Gnosis! In order to both (1) call emergency functions (2) manage pool settings, it is proposed that the following existing multisigs are granted the following roles by the authorizer:

## Emergency DAO

- `VaultAdmin.pauseVault`
- `VaultAdmin.unpauseVault`
- `VaultAdmin.pausePool`
- `VaultAdmin.unpausePool`
- `VaultAdmin.pauseVaultBuffers`
- `VaultAdmin.unpauseVaultBuffers`
- `VaultAdmin.enableRecoveryMode`
- `VaultAdmin.disableRecoveryMode`
- `VaultAdmin.enableQuery`
- `VaultAdmin.disableQuery`
- `VaultAdmin.disableQueryPermanently`
- `StablePoolFactory.disable`
- `WeightedPoolFactory.disable`

## Maxis

- `VaultAdmin.setStaticSwapFeePercentage`
- `StablePool.startAmplificationParameterUpdate`
- `StablePool.stopAmplificationParameterUpdate`
- `ProtocolFeeController.setGlobalProtocolSwapFeePercentage`
- `ProtocolFeeController.setGlobalProtocolYieldFeePercentage`
- `ProtocolFeeController.setProtocolSwapFeePercentage`
- `ProtocolFeeController.setProtocolYieldFeePercentage`
- `ProtocolFeeController.withdrawProtocolFees`
- `ProtocolFeeController.withdrawProtocolFeesForToken`

# Payload

The required payload can be found [on our GitHub repo](https://github.com/BalancerMaxis/multisig-ops/pull/1535) and can be summarised as follows:
```
+-----------------------+---------------------+----------------------------

====================================================================================================
[119] id=0x34f51ca0effb420ce01ee2cbfa10e4a930b4e6e8fd3b99b096ee21e0389f7fb9  token=BAL  space=balancer.eth  date=2024-12-19
TITLE: [BIP-749] Grant `add_reward` Permissions to Maxis’ Omnichain Multisig
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1612

# Motivation

The action of whitelisting a custom reward token on a gauge is permissioned. Doing it through the DAO multisig for every partner/gauge/token is not feasible, hence [BIP-387](https://forum.balancer.fi/t/bip-387-give-balancer-maxis-ability-to-add-3rd-party-rewards-to-mainnet-gauges/5018) requested permission for calling `add_reward` through the authorizer from the Maxis’ multisig.

The Maxis are however in the process of migrating their multisig to the so-called omnichain multisig, a multisig that has the same address on all chains. Over time it will replace the old one. In a lot of cases it already has replaced it; this permission is one of the last things that keeps the Maxis from moving over fully.

# Specification

On Ethereum, the DAO multisig `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will call `grantRole(bytes32,address)` on the authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` with the following arguments:

* role: `0x3bf29175652a3f0fac5abb715d0b7fe2e7b597e2e2eff555dac6b21a20a7c83e` ([ref](https://github.com/balancer/balancer-deployments/blob/master/action-ids/mainnet/action-ids.json#L714C41-L714C107))
* account: `0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e` ([ref](https://github.com/BalancerMaxis/bal_addresses/blob/78e701eeca6d376b43a80684b5cfec50df0a971a/extras/multisigs.json#L11C19-L11C61))

It will perform the same action on all other chains where the omnichain multisig i

====================================================================================================
[120] id=0xe2f45695282181886f128e3120372efa143743e5b600ce5419a2f0e0bfc6c315  token=BAL  space=balancer.eth  date=2025-01-16
TITLE: [BIP-757] Migrate BEETS Allocation to Sonic
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR With Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1664

#### Summary and Motivation:

Given the deployment of BeethovenX on Sonic and the migration of their maBEETs tokenomic model onto the chain, it makes sense for Balancer to bridge its BEETS balance from Fantom to Sonic. This proposal does not intend to allocate any BEETS into the 8020 pool required for maBEETS governance participation, but this does reduce the overhead in doing so and minimize any risk of not being able to bridge BEETS at a later date. Since [BIP-607](https://forum.balancer.fi/t/bip-607-update-ftm-multisig-to-claim-vested-beets/5717) will be executed on shortly by the DAO multisig, the BEETS balancer of 10M tokens will be in the Maxi Omni-chain multisig which, if this proposal passes, will facilitate the bridging of BEETS to Sonic and the transfer of the bridged BEETS to the newly deployed DAO Multisig on Sonic.

#### Technical specifications:

For reference the Sonic Maxi Omni-chain multisig and DAO Multisig addresses can be confirmed in the bal_addresses repo [here](https://github.com/BalancerMaxis/bal_addresses/blob/a3080be58e203f37ea31bcdec5aa30410526a059/extras/multisigs.json#L106).

The pre-requisite for this transaction is the execution of the claim and transfer of BEETS on Fantom by the DAO Multisig to the Omni-Chain Multisig outlined in BIP-607.

The Maxi Omni-Chain Multisig `0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e` will interact with the BEETS token ftm:`0xf24bcf4d1e507740041

====================================================================================================
[121] id=0xb4525d95c2696da4802905fee739ff1dfdd459962e63be01679d6ce1a65e9b84  token=BAL  space=balancer.eth  date=2025-01-16
TITLE: [BIP-763] Enable Boosted GHO 3pool on Balancer v3
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR with payload
https://github.com/BalancerMaxis/multisig-ops/pull/1678

## Summary

In preparations for migrating GHO liquidity from Balancer v2 to v3, @TokenLogic proposes enabling the new Boosted 3pool gauge on Ethereum.

This pool is to be considered “core pool” under BIP-19, meaning the protocol fees earned by these pool would be used to bribe for votes on it.

Within this proposal legacy gauges not being used on Balancer v2 are to be sunset.

## Motivation

With several GHO liquidity pools on Balancer v2, this publication begins the process by proposing to enable a new Boosted 3pool gauge and migrating liquidity from our largest liquidity pool across to Balancer v3.

The [Boosted 3pool](https://balancer.fi/pools/ethereum/v3/0x85B2b559bC2D21104C4DEFdd6EFcA8A20343361D) is to deploy each asset into Aave v3 to earn yield.

- GHO into Aave Prime
- USDC into Aave Core
- USDT into Aave Core

For information specific to each of the constituents mentioned above, please refer to the following Balancer v2 forum post.

* [GHO/USDC/USDT Gauge Proposal](https://forum.balancer.fi/t/bip-411-enable-gho-usdt-usdc-gauge-ethereum/5135)

You can find detailed information about all these assets in the [rate provider registry]( https://github.com/balancer/code-review/blob/main/rate-providers/registry.json), which serves as a comprehensive source for all relevant details required for the review.

We will also, use this opportunity to sunset a few under-utilised gauges across Arbitrum and Ether

====================================================================================================
[122] id=0xe24b86882703abcc6d97e5b8e472ce57c79ecbb9d26ef5e048753bb6593ef252  token=BAL  space=balancer.eth  date=2025-01-22
TITLE: [BIP-765] Boosted Pool Lending Market Incentive Handling
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### Summary and Motivation

Balancer v3 has brought forward multiple opportunities for the underlying assets in Balancer pools to be rehypothecated into lending markets for increased LP yields. For example the [Aave-Lido wstETH - wETH pool](https://balancer.fi/pools/ethereum/v3/0xc4ce391d82d164c166df9c8336ddf84206b2f812), which receives external incentives on the [wETH lending market](https://app.aave.com/?marketName=proto_lido_v3). Due to these external rewards not accruing directly to LPs, but to the Balancer v3 vault; I, along with the Balancer Maxis, are proposing to manage these rewards by claiming them and distributing them via bi-weekly merkl campaigns to LPs. In this sense LP rewards accrue for the exact time they are deposited in the pool and are distributed to be claimed 2 weeks later. As opposed to streaming rewards to the pool with a time delay. The issue with repurposing these rewards as direct or vote incentives is the time delay would mean newer LPs can join and dilute the rewards of those which have been in the pool prior.

This proposal will act as a standard for all external lending market incentives to be passed through the Balancer vault. The flow will be claimed by the omni-chain multisig using the same tracking, merkl schedule, and execution process to get rewards to respective LPs unless a change is proposed to Balancer governance at a later date.

Tokenlogic, from Aave will put forward a proposal for the Balancer Maxis Omni-chain multisig to have abili

====================================================================================================
[123] id=0x3b8dd76c89c2ef6fb5cc9e506fbb546a4c3741617c715d327d5aa859b44d554d  token=BAL  space=balancer.eth  date=2025-01-29
TITLE: [BIP-766] Grant V3 Permissions to Maxis and Emergency DAO Multisigs on Arbitrum One and Base
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1696

This is a repetition of [BIP-741](https://forum.balancer.fi/t/bip-741-grant-v3-permissions-to-maxis-and-emergency-dao-multisigs/6220), where the DAO granted both (1) call emergency functions (2) manage pool settings permissions to the emergency DAO and Maxis multisigs respectively. Except now these same permissions are granted on the Arbitrum One and Base chains, following successful deployment there ([BIP-760](https://forum.balancer.fi/t/bip-760-deploy-balancer-v3-on-base/6290), [BIP-761](https://forum.balancer.fi/t/bip-761-deployment-of-balancer-v3-on-arbitrum-one/6294)).

## Emergency DAO

* `VaultAdmin.pauseVault`
* `VaultAdmin.unpauseVault`
* `VaultAdmin.pausePool`
* `VaultAdmin.unpausePool`
* `VaultAdmin.pauseVaultBuffers`
* `VaultAdmin.unpauseVaultBuffers`
* `VaultAdmin.enableRecoveryMode`
* `VaultAdmin.disableRecoveryMode`
* `VaultAdmin.enableQuery`
* `VaultAdmin.disableQuery`
* `VaultAdmin.disableQueryPermanently`
* `StablePoolFactory.disable`
* `WeightedPoolFactory.disable`

## Maxis

* `VaultAdmin.setStaticSwapFeePercentage`
* `StablePool.startAmplificationParameterUpdate`
* `StablePool.stopAmplificationParameterUpdate`
* `ProtocolFeeController.setGlobalProtocolSwapFeePercentage`
* `ProtocolFeeController.setGlobalProtocolYieldFeePercentage`
* `ProtocolFeeController.setProtocolSwapFeePercentage`
* `ProtocolFeeController.setProtocolYieldFeePercentage`
* `ProtocolFeeController.withdrawProtoco

====================================================================================================
[124] id=0x175bdfe14bcb17cca9dc6772a4c7c1255f6204a83550ef7885fdf9cba855c91b  token=BAL  space=balancer.eth  date=2025-01-29
TITLE: [BIP-767] Relock Balancer DAOs AURA - Q1 2025
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1703

## Summary

The Balancer DAO has locked its vested AURA into vlAURA across multiple BIPs throughout 2024. The fourth lock of 2.00m AURA will expire and can be relocked after Feb 6th and before the unlock date of Feb 13th, 2025:

![Bildschirmfoto 2025-01-27 um 11.00.39.png](ipfs://bafkreiaxrpzohea46d4irgsa3jzgjdbekurv7y4gmfv4tpx3qpv3u5airi)

The DAO therefore wishes to relock its current position in the classical way by executing a “manual” relock via the DAO multi-sig—similar to [BIP-720](https://forum.balancer.fi/t/bip-720-manual-relock-of-balancer-daos-vlaura/6092) sixteen weeks ago.

### Postponing of Unlock and relock on new Multi-sig

An automatic relock Safe module was developed and voted in with [[BIP-715]](https://forum.balancer.fi/t/bip-715-enable-automatic-aura-relocking/6077). However, it was concluded by various DAO members that installing a Safe module on the DAO multi-sig might raise serious safety concerns.

To circumvent this, we aim to unlock and transfer the vlAURA at some point. However, given the current market situation and focus on a successful v3 launch and gauge bootstrapping, we can’t afford any unlock period as it would mean that the DAO would miss out on a 2 week emission cycle. Therefore, this action will be postponed until further notice.

## Specification

The Balancer DAO Multisig `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will interact with the vlAURA contract at `0x

