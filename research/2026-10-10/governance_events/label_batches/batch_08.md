# Labeling packets — batch 08 (123 proposals). Label each against criteria.md.

====================================================================================================
[0] id=0x065351bbfa19f5b4b3b8cb2d732a9809adeee6e424c9ede6815854a0dab9caeb  token=BAL  space=balancer.eth  date=2025-01-29
TITLE: [BIP-772] Enable Boosted GHO/PYUSD on Balancer v3
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1715

>## Summary
>
>This publication proposes creating a new gauge for the Boosted GHO/PYUSD Pool on Ethereum.
>
>This pool is to be considered “core pool”, meaning the protocol fees earned by these pool would be used to bribe for votes on it.

>## Motivation
>
>With both Buffer Pools adequately funded, this publication proposes enabling the gauge. 
>
>Balancer v3 - Boosted GHO / PYUSD
>
>Each asset is deployed into Aave v3 to earn yield.
>
>* GHO into Aave Prime
>* PYUSD into Aave Core
>
>The PYUSD deposits into the Core instance of Aave v3 will benefit from the ongoing liquidity mining program with [4.00% yield](https://governance.aave.com/t/arfc-pyusd-reserve-configuration-update-incentive-campaign/19573) being provided until a target of 75M in deposits is achieved. 
>
>Details relating to GHO and PYUSD specifically are well documented in [previous gauge submissions](https://forum.balancer.fi/t/bip-736-enable-gho-pyusd-e-clp-gauge-ethereum/6202). 

>## Specification
>
>Enable Gauge
>
>The Balancer Maxi LM Multisig `0xc38c5f97B34E175FFd35407fc91a937300E33860` will interact with the GaugeAdderv4 at `0x5DbAd78818D4c8958EfF2d5b95b28385A22113Cd` and call the `addGauge` function with the following arguments based on the table above:
>
>Pool address: `0x64B84023CfE8397dF83C67eACCC2C03ecDA4aeE5`
>Gauge(address): `0x6C0a4550C575C917435F228D36939125A437a98b`
>Rate Providers: `0x851b73c4BFd5275D47FFf082F9e8B4997d

====================================================================================================
[1] id=0x273c976bf56e8e83963c023bc501f3f99e3298831a88f7f6c90d7baf5cdb56d2  token=BAL  space=balancer.eth  date=2025-02-26
TITLE: [BIP-788] Grant Maxi Multisig set_reward_distributor permissions
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1797

Summary & Motivation

A crucial part of the Maxi operations is configuring reward distributions for injector and partner contracts on to pool gauges. Over time the Maxis have moved their primary method of ownership of injector contracts to the omni-chain multisig. To reduce the quantity and fragmentation of batched transactions, separate reviews, and to have a uniform process on all networks we propose granting permission to call `set_reward_distributor` via to the omni-chain multisig. This will allow reconfiguration of gauge rewards from an old distributor to a new one seamless along with the rest of the injector configuration process.

On Ethereum, the DAO multisig `0x10A19e7eE7d7F8a52822f6817de8ea18204F2e4f` will call `grantRole(bytes32,address)` on the authorizer `0xA331D84eC860Bf466b4CdCcFb4aC09a1B43F3aE6` with the following arguments:

* role: `0xd0090a09f425bba74e6c801fba7c6d15b44147ab0bd319e40076ce07e95168b6` ([ref](https://github.com/balancer/balancer-deployments/blob/346f78f1df91b7c910adda8a8e258861b8d452d4/action-ids/mainnet/action-ids.json#L727))
* account: `0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e` ([ref](https://github.com/BalancerMaxis/bal_addresses/blob/78e701eeca6d376b43a80684b5cfec50df0a971a/extras/multisigs.json#L11C19-L11C61))

It will perform the same action on all other chains where the omnichain multisig is deployed and does not have these permissions yet: Arbitrum, Avalanche, Ba

====================================================================================================
[2] id=0xf79cc1f749ae50f709e55860b9b7a8663e88b10c0eebfc5afbf072c34022480e  token=BAL  space=balancer.eth  date=2025-02-26
TITLE: [BIP-790] Grant Maxis Role for Balancer Contract Registry
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1798

### Summary and Motivation 

Balancer has created a new registry contract called the Balancer Contract Registry in which we will add v3 contracts to.  This proposal seeks to grant the role for functions related to this contract to the Balancer maxis.  

### Technical Specification

The DAO Multisig on Ethereum, Base, and Gnosis will call the `Authorizer` ’s `grantRoles` function with the respective action id’s for the following functions to the omni multisig.


#### Mainnet
omni multisig: `0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e`

`"addOrUpdateBalancerContractAlias(string,address)"`: `"0xc50be693f82453d6b7fbfabf52ae750e168eb530ce663aec7b2fe1c96cfdf381"`
        `"deprecateBalancerContract(address)"`: `"0xda5605d0e7c70ae825d1d2e45f0656490960542c725946cd5532909f723501b4"`
        `"deregisterBalancerContract(string)"`: `"0x534d9f0ca09366b50105b12a7492e9429c8621cf57c845195e7c6874fa413d03"`
        `"registerBalancerContract(uint8,string,address)"`: `"0xf539cbe9be426b500591a2dd63970d37952d95006d1039f35e731b4b52b33e73"`

#### Base
omni multisig: `0x9ff471F9f98F42E5151C7855fD1b5aa906b1AF7e`

`"addOrUpdateBalancerContractAlias(string,address)"`: `"0x0918fe18bf5dd7146d6ef70b2bc468e01847a23ebc248c46f0f3e860e760b95a"`
        `"deprecateBalancerContract(address)"`: `"0x4f36a3d4a5722964e73c1331cfbe74b0ce2717c92b0cb39e4e1bb402a34ce490"`
        `"deregisterBalancerContract(string)"`: `"0xff6339cb1834d4fd03de1

====================================================================================================
[3] id=0x313f35c623fd1651fffdd10db8cdb3e4180489eaa5c1c735ca6664fb57d1f381  token=BAL  space=balancer.eth  date=2025-03-05
TITLE: [BIP-792] Grant setTokenCacheRateDuration Permissions to Omni-Multisig for Balancer V2 Pools on Gnosis
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
PR With Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1809

### Summary and Motivation 
Due to the interest in chainlink oracles being utilized in StableSwap and StableSurge [pools](https://balancer.fi/pools?protocolVersion=3&poolHookTags=HOOKS_STABLESURGE&skip=0&orderBy=volume24h&orderDirection=desc) (see wETH/USDC pairs) on Balancer V3, there is a need to set the tokenCacheRateDuration lower on legacy Balancer V2 pools which utilize price oracles for further testing. The pools which utilize these types of rate providers are strictly on Gnosis Chain, in particular this [sDAI/EURe](https://balancer.fi/pools/gnosis/v2/0xdd439304a77f54b1f7854751ac1169b279591ef7000000000000000000000064) pool, as the rest are on V3 and have no cache rate duration setting. 

The setting currently is 10800 seconds, and for a Forex pair this is far too infrequently. The goal is to set this lower and for the heartbeat frqeuency of the underlying oracle itself to also be improved. This will permit pool creators and liquidity providers to continue testing theories around swap fees and improve capital efficiency of these pool types without the need to continuous migrations. 

Technical Speficifation:

Due to the request being only for a single pool on Balancer V2 the permissions will only be granted for Gnosis Chain, due to Balancer V3 no longer having this cache rate constraint.

The DAO Multisig on Gnosis Chain `0x2a5AEcE0bb9EfFD7608213AE1745873385515c18` will interact with the `Authorize

====================================================================================================
[4] id=0x6809b963e2bd2d5c0f2bf4756105d140587e5bc8b8088dc632fe252617d5f1d5  token=BAL  space=balancer.eth  date=2025-03-12
TITLE: [BIP-794] Enable Composable Stable Pool Pause functionality to Hypernative
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1732

**HYPERNATIVE – Balancer V2 Protocol**

Version: 1.0

Updated: 20 January 2025

### Summary

We propose to be given the authority to pause composable stable pools for Balancer v2, by installing a safe module to the Emergency SubDAO multi-sig to allow for quick threat mitigation and securing of funds in case of a security incident with Balancer.

### Motivation

Given that composable stable pools on Balancer hold a significant amount of TVL, it is crucial to improve security measures. One of these measures is the possibility to pause a specific pool type. Upon pausing, it is not possible to trade in a pool but proportional withdrawals are still possible. By installing a safe module managed by Hypernative’s real-time monitoring platform will enhance the resiliency and security of the protocol and augment the team’s security operations while minimizing the risk of hacks and exploits, loss of funds and prevent catastrophic loss to create long-term sustainable growth.

### Specification

The Balancer Emergency subDAO Safe on each network will install a safe Module to enable Hypernative to pause pools. A Module is a smart contract that executes a predefined set of instructions on behalf of the Safe address, pre-approved by the Safe signers, and capable of executing these instructions automatically. In this case, the instruction is to call the pause method for each Balancer pool. The module is attached via

====================================================================================================
[5] id=0xb7dc73580560446a20adc7bf79bce1d52a1ab32aee6154fce0441eea51307eb0  token=BAL  space=balancer.eth  date=2025-03-13
TITLE: [BIP-797] Wire Up V3 Protocol Fee Processing Permissions
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# TL;DR

Balancer's new v3 vault has its own mechanism of collecting fees. Helper contracts (`ProtocolFeeSweeper` and `CowSwapFeeBurner`) have been deployed and tested and are ready to start processing fees on all active chains. An offchain bot determines when and how to process exactly via an EOA. All these components require the necessary permissions in order to fulfill their role. A test run of this system was performed on Sepolia (see References below).

# Technical Specifications

The protocol fee processing infrastructure on Balancer v3 consists of several smart contracts:

## Protocol Fee Collector

This is the Balancer ‘native’ smart contract that actually withdraws the fees from the Balancer v3 vault, and is also where third parties would withdraw their fees.

## Protocol Fee Sweeper

This smart contract has [recently been deployed](https://github.com/balancer/balancer-deployments/pull/195), and sweeps specific tokens from the collector to then process for the DAO. In order to be able to do so, it needs the permission to call `ProtocolFeeCollector.withdrawProtocolFeesForToken(address,address,address)`.

The fee recipient of this sweeper is currently set to the Maxis’ omni-chain multisig. The fee recipient is automatically granted all other permissions needed to manage the sweeper (set target token, add/remove burners). However, eventually the actual sweeping will be performed automatically by an offchain bot, controlling the EOA `0x74E283B985EA76c55C8B48d6bD1067a4181

====================================================================================================
[6] id=0x776379fdfd30e1f79142ab330bca684a74e84bf875fe5467fe004387553a5d74  token=BAL  space=balancer.eth  date=2025-03-19
TITLE: [BIP-798] Balancer Foundation allocation for Marketing
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
## Intro

Following the recent [withdrawal of funding proposals for marketing](https://forum.balancer.fi/t/bip-xxx-marketing-team-selection-for-january-june-2025-withdrawn/6296) service providers, the Balancer community has engaged in productive discussions regarding the optimal structure and strategy for promoting the protocol. The Foundation has actively participated in these conversations, gathering feedback from a diverse range of stakeholders and marketing professionals. 

This proposal outlines a revised approach to Balancer's marketing efforts, shifting away from direct DAO funding of individual initiatives and towards a more strategic, Foundation-led model. This transition aims to prioritize long-term brand building while simultaneously driving measurable results aligned with community objectives.

**Problem Statement**

The previous marketing funding model, while well-intentioned, presented challenges in achieving consistent, impactful results. Direct DAO funding of previous providers lacked a cohesive strategy and often struggled to balance long-term brand development with immediate, measurable outcomes. The recent funding proposal withdrawals, with failure on reaching soft-consensus before vote, highlighted the need for a more structured and accountable approach.

**Proposed Solution: A Foundation-Managed Marketing Fund**

This proposal requests the allocation of $99,000 USD to the Balancer Foundation multisig. These funds will be earmarked for salaries/contractors

====================================================================================================
[7] id=0x25dc8b275484866182ee83076f48d16a5f7dbc5d99b862a86266d9a4cdd0bb6e  token=BAL  space=balancer.eth  date=2025-03-19
TITLE: [BIP-803] Grant v3 ECLP disable Permissions to the Emergency DAO Multisigs
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1834

### Motivation 
With the imminent launch of ECLPs on Balancer v3 on Mainnet, Arbitrum, Base and Gnosis chain, the emergency subDAO needs permissions to disable the factories in the case of a potential malfunction. It is therefore proposed that the emergency subDAO wallets on these chains are granted following roles by the authorizer:

#### Emergency DAO

`GyroECLPPoolFactory.disable`

| Network | Emergency Safe | Action ID |
| :---- | :---- | :---- |
| Mainnet | 0xA29F61256e948F3FB707b4b3B138C5cCb9EF9888 | 0x2d6f2043f87de4e7d3300eb8d3235d0a0015939b896057526473bb03cb53af84 |
| Arbitrum | 0xf404C5a0c02397f0908A3524fc5eb84e68Bbe60D | 0x95095549d7b771b285d8bc313117157a9c18db08596228d492e3fbc7c5dc751b |
| Base | 0x183C55A0dc7A7Da0f3581997e764D85Fd9E9f63a | 0x9a2847fdb9a96a453c9e5f3eda469d4f53b4e5616cbf9c20f6c820d30a30e40c |
| Gnosis | 0xd6110A7756080a4e3BCF4e7EBBCA8E8aDFBC9962 | 0x43951d61361ec89c52166ef54cf1f4d74ead1426b610bb3fd62aeea215ce8faa |

The action IDs can be verified by going to each chain and checking 20250124-v3-gyro-eclp, disable(), e.g. [here](https://github.com/balancer/balancer-deployments/blob/33e050a42ddd7d17a7a2594c63348c3da42ea45e/action-ids/mainnet/action-ids.json#L1773)

## Technical Specifications

The DAO multisig on each network will interact with the Authorizer by calling `grantRole`, with `role` as the corresponding action ID mentioned in the table above and `account` as the Em

====================================================================================================
[8] id=0xa174606ee924b6ccfcf6be9862f02ac8105541bd86df98ee0f44525c429f4b69  token=BAL  space=balancer.eth  date=2025-03-20
TITLE: [BIP-804] Protocol Fee Controller Migration
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
# Payloads

https://github.com/BalancerMaxis/multisig-ops/pull/1837

# Overview

The `ProtocolFeeController` deployed with the Vault was found to have a couple shortcomings. First, it lacked events exposing the initial protocol fees (e.g., there was no record that a pool was protocol fee exempt), making it effectively impossible to track protocol fees off-chain.

This prompted a migration (the fee controller is upgradeable in the Vault): but when we started writing the migration, it quickly became apparent that there was a lot of pool-specific state relating to fees that was only set on pool registration (or by pool creators). There was no way to copy this state to a new controller, and therefore no way to migrate it.

To solve this problem, we created V2 of the `ProtocolFeeController` with not only the events that originally motivated the upgrade, but also refactored the contract storage, added new getters, and most importantly, added a new `migratePools` function to copy the previously inaccessible state during migrations.

# Migration Mechanics

The general pattern for migrations is to first create and deploy the new version of the contract we’re upgrading, then deploy a migration helper contract to perform the actual migration. This migration helper is deployed with the addresses of the old and new contracts, and must be granted “admin” privileges by governance (i.e., so that the contract can grant itself any specific permissions it requires).

There is usually a permissi

====================================================================================================
[9] id=0x2636e7a6e91a30fa584560371f733b80d8f11973e97c9bb27409210bc5db9854  token=BAL  space=balancer.eth  date=2025-03-20
TITLE: [BIP-805] Balancer Registry Initialization
CHOICES: Yes, let's do it | No, this is not the way | Abstain
TEXT (first 1500 characters):
### PR with Payload
https://github.com/BalancerMaxis/multisig-ops/pull/1840

The `BalancerContractRegistry` was [recently deployed](https://github.com/balancer/balancer-deployments/pull/173) to all networks, followed by the [initializer contract](https://github.com/balancer/balancer-deployments/pull/207).

# Balancer Contract Registry Overview

The purpose of the contract is to maintain a registry of official Balancer Factories, Routers, Hooks, and valid ERC4626 tokens, for two main purposes.

**On-chain use case**

The first is to support the many instances where we need to know that a contract is "trusted" (i.e., is safe and behaves in the required manner). For instance, some hooks depend critically on the identity of the `msg.sender`, which must be passed down through the Router. Since Routers are permissionless, a malicious one could spoof the sender and "fool" the hook. The hook must therefore "trust" the Router.
 
It is also important for the front-end to know when a particular wrapped token should be used with buffers. Not all "ERC4626" wrapped tokens are fully conforming, and buffer operations with non-conforming tokens may fail in various unexpected ways. It is not enough to simply check whether a buffer exists (e.g., by calling `getBufferAsset`), since best practice is for the pool creator to initialize buffers for all such tokens regardless. They are permissionless, and could otherwise be initialized by anyone in unexpected ways.

This registry could be used to kee

====================================================================================================
[10] id=0x88c9e42ecd42f10766deb3eb2cb2d013d32b9f4073ad55856ce552ad7510d0c2  token=BIO  space=bioxyz.eth  date=2025-05-25
TITLE: BIOPSY-22 🧪 Postponing Unlock of Core Team's 1-Year Cliff Token Allocation
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TL;DR

- Bio Core Team tokens are on a **6‑year vesting schedule** with a **1‑year cliff** set for **28 May 2025**.
- To align token unlocks with actual value creation while the Bio Launchpad is still rolling out, the entire **1‑year** cliff tranche will **unlock linearly over six months—from 14 Nov 2025 to 14 May 2026—instead of unlocking all at once on May 28 2025**.
- Core Team tokens that were set to start vesting continuously from May 28 2025 onward will be vesting and unlocking continuously from May 28 2025 onward under the original timetable.

### Context

Team tokens account for 21.2% (**703,84M BIO) of the 3.32 B total supply**. They follow a **6‑year vesting curve** with a cliff at the end of year 1. Under the original timetable:

- **Start:** May 28 2024
- **Cliff:** May 28 2025 → 1/6 unlock (≈117.3M BIO)
- **Linear vesting:** The remaining 5/6 unlocks linearly over the next 5 years (≈117.3M BIO per year)

# Proposal

Postpone the single‑day unlock of 117.3M BIO+ tokens for the team to:

- Reduce circulating supply during the **six‑month window** while the Bio Launchpad is still being built out and revenue‑generating functionality is coming online, minimizing volatility before that value catalyst materializes.
- Align unlocks with clear product milestones, to not erode the "skin‑in‑the‑game" signal that long‑term supporters expect from core contributors.
- Reduce short‑term volatility that may distract community from shipping, adoption, and ecosystem growth.

Rel

====================================================================================================
[11] id=0xce3a2ed81ebaf68843da8d8c33f5072609010a0279553554785f4d40e81d625f  token=BIO  space=bioxyz.eth  date=2025-08-05
TITLE: BIOPSY-24: Bio Protocol V2 Upgrade – Launchpad, BioXP & Staking
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# **TL; DR**

- **Launchpad V2:** Low-cap sales for BioAgents, BioDAOs, and IP-Tokens.
- **BioXP System:** Earn points via staking, governance, and social engagement. Points determine access to new token launches.
- **Staking BIO & Ecosystem Tokens:** Stake BIO and ecosystem tokens (BioAgents, BioDAOs, and IP-Tokens) to earn BioXP.


## **Background & Motivation**
The first version of the launchpad focused on large, one-time fundraising events. While that approach helped bootstrap initial projects, it often resulted in unrealistic valuations, misaligned incentives, and low long-term community engagement.

Motivated by these insights, Bio Protocol V2 introduces:

- **Smaller, Ongoing Funding:** Funding shifts from large, one-off sales to smaller, incremental raises that grow with community traction and scientific progress.
- **Stronger Community Ties:** Sale allocations require BioXP, aligning token distribution with active ecosystem contribution.
- **Automation with Agentic AI:** Integrate AI-driven agents (BioAgents) to lower overhead and create automated research loops.
- **Long-Term Alignment:** Encourage holding and participating through rewards (points, staking yields, governance power) and disincentivize short-term flipping.

In summary, Bio Protocol V2 aims to increase velocity and sustainability: enabling rapid launches of experimental projects with minimal initial capital, while providing tools for those projects to continuously fund themselves through market activit

====================================================================================================
[12] id=0x0ab4a228b0ec7c614538ac7ff2209082703fb45c2f30f77ac79c3f1816312e4e  token=BIO  space=bioxyz.eth  date=2025-08-21
TITLE: BIOPSY-26: Establish AUBRAI Operational Setup, Multisig & Tokenomics
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## **TL;DR**

* Approve the launch of **Aubrai** through the **BIO Launchpad** as the first agent token to utilize Bio Protocol's new launch infrastructure.

* Designate **Aubrai** as a **pilot implementation** of **Molecule Protocol V2** for DeSci IP→RWA workflows, establishing the framework for future scientific IP tokenization.

* Support the creation of a **Swiss Association (Verein)** to execute DAO decisions off-chain, following the proven governance model established by VitaDAO.

* Establish a **4/6 multisig** with representatives from VitaDAO, BIO, Molecule, Aubrai, and an Aubrai guardian to ensure decentralized operational control.

* Ratify **$AUBRAI tokenomics**: 2,000,000 total supply with allocations & vesting as detailed below. No treasury spend requested; this is an **operational ratification** enabling launch.

---

## **Motivation**

Aubrai aims to operationalize an AI-forward DeSci project that aligns with BIO’s ecosystem and VitaDAO’s longevity mission. To move from concept to execution, we need:

1. A legally capable executor for DAO votes,  
2. Governance-aligned treasury controls, and  
3. A clear token distribution/vesting plan that aligns incentives across stakeholders.

**Why [Molecule Protocol V2](https://www.molecule.to/blog/molecule-protocol-v2-bridging-the-future-of-decentralized-science-into-rwas) now?** V2 provides a bridge from tokenized scientific/IP participation to **institution-grade RWAs**, enhancing compliance and institutional appeal whi

====================================================================================================
[13] id=0x1dd81f0c0915170dfd83f1f38c22a81714fc462d86768740e2ff5f799e56b6ca  token=BIO  space=bioxyz.eth  date=2025-08-27
TITLE: BIOPSY-29 Fund $20,000 for Wolfram Institute Research on Incentive Alignment in DeSci DAOs
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Proposal: Funding Wolfram Institute Research on DeSci DAO Incentive Alignment

---

## **TL;DR**

Deploy **$20,000 worth of $RSC** from the BIO treasury to fund the Wolfram Institute research study: [*“How can DeSci DAOs better align incentives for funding basic science research?”*](https://www.researchhub.com/fund/4300/a-new-kind-of-science-organization).  

The study explores governance and economic mechanisms to improve incentive alignment in decentralized science organizations. It strengthens BIO’s position as a thought leader in DeSci governance, generates open models applicable across BioDAOs, and forges collaboration with Wolfram Institute researchers—renowned for their work in computational frameworks for complex systems.

---

## **Scientific Relevance**

- The Wolfram Institute brings unique expertise in **computational social science, mechanism design, and complexity modeling**.  
- Their formal methods can test incentive structures under simulation before deployment.  
- The study builds on *“A New Kind of Science Organization”*, which highlights the need for new funding architectures that combine open science values with sustainable economic engines.

---

## **BIO Protocol Synergy**

- Strengthens BIO’s governance infrastructure and sets a precedent for robust DAO-level incentive design.  
- Outputs (models, simulations, proposed incentive structures) can be integrated into **tokenomics experiments** across BIO and partner DAOs (*VitaDAO, PsyDAO, CerebrumDAO*)

====================================================================================================
[14] id=0x73d7a19aeb4f25c801958acfe07ff4ae346f8fe12a9394e45726cc7b8445930a  token=BIO  space=bioxyz.eth  date=2025-09-15
TITLE: BIOPSY-Proposal: Analysis And Closing of bio/acc Season 1
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## TLDR
- bio/acc Season 1 ran for six months from July 18, 2024 until Jan 13, 2025.
- A total of 132.8M BIO were allocated to the bio/acc reserve for ecosystem builder incentives over all seasons.
- Key goals: Utilize BIO token rewards to accelerate the growth of our BioDAOs, as well as their research and products, while establishing standardized performance milestones and metrics for BioDAOs, as governed by BIO holders.
- 33M BIO incentives have been unlocked in Season 1 and will distributed to BioDAO treasuries .
- VitaDAO, Cerebrum DAO, PsyDAO and Quantum Biology DAO unlocked BIO rewards
- After the end of Season 1, there remain 99.8M BIO in the bio/acc cell that can be distributed over next seasons of bio/acc incentives

### Background: the bio/acc incentive program
The bio/acc rewards as ratified in BIOPSY-5 are designed as a strategic program to accelerate the growth of BioDAOs within the BIO Protocol ecosystem through clear milestones, standardized metrics, and financial incentives.

One primary objective of the program was to strengthen incentive alignment between BioDAOs and the BIO ecosystem by fostering collaboration and shared ownership.

The program emphasizes the importance of sustainable BioDAO and IP-token economies as a core driver of the ecosystem’s progression. The program allocated 4% of the total BIO supply (132,800,000 BIO) toward rewards, to be distributed based on key performance milestones, such as IP-Tokens and launching revenue-generating products.

====================================================================================================
[15] id=0x19ce2403540aeab6c31f334fc23f7584999668105e443d18dfba4dba27e9be89  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on USDT Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* USDT pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the USDT pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[16] id=0x10357f9119ff960ac5e9318d6f39fc4b30f98ac3c50ab99b395c272a7211fd71  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on ETH Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* ETH pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

====================================================================================================
[17] id=0xcca31422e4b6d1989f5b2ff48f4396b02844fec869cdd761eebffa34779f3bb6  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on MATIC Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* MATIC pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the MATIC pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[18] id=0x4568065b4089453cf4cd5a3ab63542471888b23db2ea9ff2d4cc9c21c0d4b24b  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on MKR Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* MKR pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the MKR pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[19] id=0x07b07814cc96bb85ec9b5131d8f630d163d69f2902f2f48a36a131949ef0c308  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on wNXM Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* wNXM pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the wNXM pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[20] id=0xee5779f43bc2e4cb5977df2b7c0ac4374f366db6973ead027d85e76800a27705  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on QNT Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* QNT pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the QNT pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[21] id=0xf42373e70da7cc366a3db41f8665b5f5d04ab57238c04edea732118b7f0d0a73  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on UNI Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* UNI pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the UNI pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[22] id=0xe41bc200d779ba3fcd1257cab21c40cabbd90655ac88aec2080031a11b96c1b3  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on ENJ Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* ENJ pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the ENJ pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[23] id=0xf938d9bffe03f6052fd8ea36cc91835212402eff45033e4eec7a99a28e10f7ca  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on WBTC Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* WBTC pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the WBTC pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[24] id=0xb6dad2d2eb8c474022380b967b776965480376d642fbddd0335a23ce8176a57c  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on BAT Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* BAT pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the BAT pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[25] id=0x20e0a144c0886d93da021ba5224e0660e3d563a1382af7f309f0188334cf68f8  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on ANKR Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* ANKR pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the ANKR pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[26] id=0x14ceb7bdd5be764996c5c7ebd3204d29c287f4259dc106de320814535cd8ac65  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on RPL Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* RPL pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the RPL pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[27] id=0x75454a2d8bbeb70d2c14fc09782eac871d55faed1efafd5555f10479b3f28e0a  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal to set funding limit to 0 on USDC Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/proposal-to-start-sunsetting-bancor-v3/4279

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* USDC pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the USDC pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[28] id=0x58f9525f9059b3d718da0fd56952309fb7a2bdcd01068ae08e54a3af3534f3f2  token=BNT  space=bancornetwork.eth  date=2023-08-20
TITLE: Proposal: Burn the Vortex Bancor 3 Captured BNT
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Bancorians should decide what to do with the BNT amount we captured from the Bancor 3 vortex.
This amount currently sits at exactly 1,041,563.82 and can be found via this [link](https://etherscan.io/readContract?m=normal&a=0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB&v=0xe2a2773a1aa412f10b9f338334f2d62b25dcd1f7#readCollapse9) ( Select value 9).

I am proposing to burn the total available captured BNT in the contract above in its entirety. As it stands, this BNT doesn’t reflect in the official numbers for circulating supply on Etherscan. That’s why we need to officially burn it to make this transparent for the community. 

How will this burning will be managed? That I will leave to the devs, the only thing that’s important is that it happens safely and is reflected in the BNT contract.

# For

Burn the entire captured BNT amount in the pendingNetworkFeeAmount

# Against

Do nothing

====================================================================================================
[29] id=0x96165a10c4db1ed79cb0b538cc889caf290ed3793b541c6da102461192dccec7  token=BNT  space=bancornetwork.eth  date=2023-10-01
TITLE: Proposal for the Bancor v2.1 vortex to use 100% of fees to burn BNT
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/bancorians-for-a-stronger-bnt/4434

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* The Bancor v2.1 vortex to use 100% of fees to burn BNT
* The Bancor v2.1 vortex will not burn vBNT any longer

**Summary**

The reduction in BNT supply is the most important number for all Bancor v2.1 and Bancor 3 LPs. This affects the pool deficits as burned BNT is bought from the markets first. It is important for any outsiders that is looking at BNT to know that it is deflationary.

How will the Bancor v2.1 vortex be made to burn BNT? That I will leave to the devs, the only thing that’s important is that it happens a safe manner.

# For

The Bancor v2.1 vortex to use 100% of fees to burn BNT

# Against

Do nothing.

====================================================================================================
[30] id=0x74917631a57cfbd39b06f25473941a993cdf1e57f2873bfe46a9f62bfee5e8f4  token=BNT  space=bancornetwork.eth  date=2023-10-08
TITLE: Proposal for Bancor 3 to use 100% of fees for BNT market buy back and burn
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

https://gov.bancor.network/t/bancorians-for-a-stronger-bnt/4434

and Bancorians should read that post to have an understanding about this proposal

TL;DR

100% of fees in Bancor 3 to be used for BNT market buy

Summary

Bancorians and LPs staked in Bancor 3 get small yield benefit from 10% of fees accumulating in their LP tokens. Instead of 90% of fees in Bancor 3 to be used for buying BNT from the market this proposal will move this to 100%. 

Why? ALL BNT holders are treated the same and benefit equally no matter where you are stake. Token LPs in Bancor 3 do not care about the negligible 10% fees that they are receiving and would prefer for their positions to be in surplus. This proposal seeks to further help with deficit reduction efforts.

How will 100% of fees in Bancor 3 to be used for BNT market buy? That I will leave to the devs, the only thing that’s important is that it happens safe manner.

For
100% of fees in Bancor 3 to be used for BNT market buy

Against
Do nothing.

====================================================================================================
[31] id=0x588313a4a6c950277427bc42347182952bd5b48befb61222eec6913d51128e41  token=BNT  space=bancornetwork.eth  date=2023-10-15
TITLE: Proposal to automatically burn the Vortex Bancor 3 Captured BNT
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Bancorians have previously created proposals to burn the collected BNT by the Bancor 3 vortex

https://gov.bancor.network/t/proposal-burn-the-vortex-bancor-3-captured-bnt/4415

https://gov.bancor.network/t/burning-the-vortex-v3-captured-bnt/4243

https://gov.bancor.network/t/proposal-focused-discussion-on-burning-bnt-collected-by-the-bancor-vortex-in-the-v3-vault-when-it-reaches-1m/4087

this process is creating unneeded work for the DAO.  

TL;DR

With this proposal, I want the Bancor DAO to automatically grant forever the ability for the bancor 3 collected BNT to be burned every time it reaches 1m in its entirety.

Summary

Bancorians should decide what to do with the BNT amount we captured from the Bancor 3 vortex.
This amount currently sits close to 500k and can be found via this [link ](https://etherscan.io/readContract?m=normal&a=0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB&v=0xe2a2773a1aa412f10b9f338334f2d62b25dcd1f7#readCollapse9) ( Select value 9).

I am proposing for this BNT to be burn every time the total available captured BNT in the contract reaches 1m BNT going forward. As it stands, this BNT doesn’t reflect in the official numbers for circulating supply on Etherscan. That’s why we need to officially burn it to make this transparent for the community.

How will this burning will be managed? That I will leave to the devs, the only thing that’s important is that it happens safely everytime it reaches 1m and is reflected in the BNT contract.

# For

Grant the abilit

====================================================================================================
[32] id=0xcc6ee5a27775560b838d9a7bdb123f5bd0b2b921cd51602f6634fcc7213d5d60  token=BNT  space=bancornetwork.eth  date=2023-10-15
TITLE: Proposal to set funding limit to 0 on vBNT Bancor 3 pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal is split from the discussion that has happened in this thread

[Bancorians for a stronger BNT - Community Chatroom (DISCUSSION) - Bancor Governance Forum](https://gov.bancor.network/t/bancorians-for-a-stronger-bnt/4434)

and Bancorians should read that post to have an understanding about this proposal

**TL;DR**

* vBNT pool on Bancor v3 might have a surplus in the future
* This proposal is looking to set the funding limit to 0 if it goes into surplus in the future

**Summary**

This is fairly simple and straight forward. Setting the funding limit to 0 on a Bancor 3 pool means that it no longer trades as there is no BNT liquidity allocated to it. Any BNT liquidity currently allocated to the pool is burned.

# For

Set the funding limit to 0 on the vBNT pool if it is currently in surplus. Otherwise, if at any point in the future of this proposal passing the pool goes into surplus then the funding limit can be set to 0.

# Against

Do nothing.

====================================================================================================
[33] id=0xd02f2b527cd0876cf272a727d99752e84d21810a929e85d4ee842b6bf24e50e0  token=BNT  space=bancornetwork.eth  date=2023-11-05
TITLE: Protocol Owned ETH Spending Proposition [32 ETH Weekly Method]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Protocol owned ETH to be used to continue the strategy of buying and burning BNT

Summary:

Bancor 3 token surpluses were converted to ETH. The contract now has about 1800 ETH which Bancorians must decide how to utilize

https://etherscan.io/tokenholdings?a=0xD06146D292F9651C1D7cf54A3162791DFc2bEf46

Historically the Bancor DAO has opted to buy and burn BNT as part of its approach to fix the deficit. Buying and burning BNT affects all LPs EQUALLY and does not pick any favorites or provide any preferential treatment to anyone. This method benefits BNT holders and TKN holders the same and has led to over 50+ pools being closed since the discussion regarding sunsetting Bancor 3. 

How will this be accomplished?

This proposal proposes a method similar to the approach that was recently used for converting protocol owned tokens to ETH with some modifications to prevent front running.

If it passes, the first initial BNT buy order to be put on chain will happen on November 13, 2023.

Buying of BNT should happen in tranches to prevent front running and be spread out over time using the following schedule every week:

Year 2023:

Week 46 Monday 13 November: 32 ETH to be used for buying BNT

Week 47 Monday 20 November: 32 ETH to be used for buying BNT

Week 48 Monday 27 November: 32 ETH to be used for buying BNT

Week 49 Monday 4 December: 32 ETH to be used for buying BNT

Week 50 Monday 11 December: 32 ETH to be used for buying BNT

Week 51 Monday 18 December: 32 ETH to be used for b

====================================================================================================
[34] id=0xbf21276c0a61590a1a76dd9aed326dca4277b4909493de1768ddcff924e2783f  token=BNT  space=bancornetwork.eth  date=2023-12-27
TITLE: Proposal to expand Custom Taker Fee on Stable to Stable Trades
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## TL;DR

A previous proposal was brought up to the Bancor DAO that set a 0.001% fee on stable to stable trades for certain trading pairs.

This proposal is looking to expand that list with other possible combinations of those five (USDC, USDT, DAI, FRAX, LUSD) tokens.

## Overview:

The default taker fee on Carbon is .2% which means that anyone taking an order from the protocol has to pay this amount. A previous proposal:

https://gov.bancor.network/t/custom-taker-fee-on-stable-to-stable-trades/4370

was brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon more competitive with stable to stable swaps that are normally lower across all DEXs.

This list currently encompasses the following trading pairs:

* USDC/USDT
* USDC/DAI
* USDC/FRAX
* USDC/LUSD
* USDT/DAI

But left out other possible combinations between these five tokens:

* USDT/FRAX
* USDT/LUSD
* DAI/FRAX
* DAI/LUSD
* FRAX/LUSD

This proposal is seeking to expand the custom taker fee to these other stable pairs.

**FOR**: Update the taker fee to .001% on the following trading pairs USDT/FRAX, USDT/LUSD, DAI/FRAX, DAI/LUSD, FRAX/LUSD

**AGAINST**: Take no Action

====================================================================================================
[35] id=0x82b918fd7d51809102bb0c3620ce22959e49b5ccdf29228da42360e48edadd46  token=BNT  space=bancornetwork.eth  date=2024-03-21
TITLE: Carbon Vortex 2.0 - Dutch Auction
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TL;DR

* The Carbon Vortex has been part of CarbonDefi since launch
  * Link to proposal: [Proposing Carbon](https://gov.bancor.network/t/proposing-carbon-final/4242)
  * Link to docs: [CarbonVortex](https://docs.carbondefi.xyz/developer-guides/carbonvortex)
  * Link to most recent update: [FastLane](https://gov.bancor.network/t/proposal-carbon-vortex/4331)
* The current version is limited to only being able to sell tokens that have a B3 pool.
* As noted here ([FastLane](https://gov.bancor.network/t/proposal-carbon-vortex/4331)) “If this proposal passes, we should expect a second version that will also know how to handle tokens that do not have liquidity on Bancor 3.”
* This proposal is to allow the Vortex to function without reliance on B3.
* As you can see, there are many tokens which are held by the vortex but the mechanism to sell them does not yet exist: https://etherscan.io/address/0xba7d1581db6248dc9177466a328bf457703c8f84
  * NOTE: This is designed in a generic fashion so that it can also be used by anyone licensing the Carbon source code.

# Background

The design for Vortex 2.0 is very similar to the POL contract ([link](https://gov.bancor.network/t/update-to-pol-migration-and-conversion-to-eth/4438)) ([link](https://gov.bancor.network/t/proposal-to-use-pol-to-reduce-b3-deficits/4502)). The goal is to take fees earned and convert them to BNT via ETH and send that BNT to the token contract.

# Description:

Parameters:

* Define target token: **ETH**
* Define final

====================================================================================================
[36] id=0x440fc48262a68897bd421d2fb729dae49dfa2fc6ca102a9c781a7f8584c66374  token=BNT  space=bancornetwork.eth  date=2024-05-01
TITLE: Proposal to Deploy CarbonDefi on the Upcoming SEI V2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TLDR

* SEI V2 is expected to be released in Q2, 2024
* SEI V2 is EVM compatible
* This proposal suggest to deploy on the SEI V2 network once it is live
* As with every deployment of CarbonDefi, the Arb Fast Lane framework will be deployed as well.
* Fees will be used in the same way they are in the Ethereum deployment.

# Summary

* SEI V2 is expected live shortly: https://v2.docs.sei.io/
* SEI has expressed interest in having Bancor deploy CarbonDefi.
  * SEI has offered a milestone based grant to the Bancor Foundation
  * SEI will work to ensure there is deep liquidity on CarbonDefi.
* As with every deployment of CarbonDefi, the Arb Fast Lane framework will be deployed as well.
* Fees generated by the deployment will be used exactly the same as fees generated by the Ethereum Deployment
  * Upon launch, fees will be held in the vortex until a bridging solution is decided upon in a future proposal and then can be sent to the CarbonDefi Vortex on Mainnet.
* This proposal suggests setting the taker fee at 40 basis points
  * This is a parameter that can be adjusted by the DAO.
  * There are two main reasons this proposal suggests 40BP.
    * As seen on licensed deployments, the fees can be a bit higher in a low gas environment
    * A 40 BP fee would enable licensees to also deploy on SEI without creating a race to the bottom.
* Upon deployment, this proposal does not suggest any custom fee for stable to stable trades. While the author of this proposal would like to have som

====================================================================================================
[37] id=0x21a4cacd86b4d09ae99508445207b74df8054e62cd44fb35f5bbfe9ecfd97e2d  token=BNT  space=bancornetwork.eth  date=2024-05-09
TITLE: Proposal: Arb Fast Lane Vault Vortex
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TL;DR

* The Arb Fast Lane has since become a very important part of the Bancor Ecosystem.
* There are two components to this system
  * Arb Fast Lane Smart Contract - where the bots feeds relevant info
  * Arb Fast Lane Bot - Off-chain logic that anyone can run
    * So far there are 78 callers of this decentralized system.
  * Data can be seen at the links below:
    * https://dune.com/bancor/bancor-fastlane-arbitrage-bot
* The Arb Fast Lane is deployed alongside all Carbon deployments
* A recent proposal has outlined a method for the Carbon Vortex on Ethereum to sell its tokens: https://vote.bancor.network/#/proposal/0x82b918fd7d51809102bb0c3620ce22959e49b5ccdf29228da42360e48edadd46
* I propose to deploy such a vortex on every chain where the Arb Fast Lane Bot system is active. This will allow these vaults to consolidate holdings into a single token **in preparation for sending it back to the Carbon Vortex on Ethereum mainnet.**
* No changes are proposed to the Ethereum Vortex as [this](https://vote.bancor.network/#/proposal/0x82b918fd7d51809102bb0c3620ce22959e49b5ccdf29228da42360e48edadd46) remains valid.

# Arb Fast Lane Vaults Not on Ethereum

BASE

https://basescan.org/address/0xd2b2d272c30d9a0ff3dbafe848da7e2f194f697f#tokentxns

FANTOM

https://ftmscan.com/address/0x4e017822e77e34842b71b8a24b09e6e490faca13#tokentxns

MANTLE

https://explorer.mantle.xyz/address/0x45d2e25C04F43A06f6C3e21e4f39B860D05a7aC8

As Carbon and licensed deployments expand to more chains, so wi

====================================================================================================
[38] id=0x1338c605aa0873326885340afb06adba41a3df7fbfee945d87cdc2f91836e5fb  token=BNT  space=bancornetwork.eth  date=2024-06-07
TITLE: Proposal: Expand Custom Taker Fee on Stable to Stable Trades on Sei v2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## TL;DR

Previous proposal have been brought up to the Bancor DAO that set a 0.001% (1/10th of a basis point) fee on stable to stable trades for certain trading pairs.

This proposal is looking to expand on these previous proposals by setting a lower fee on the USDC-USDT trading pair on the Carbon DeFi deployment on Sei v2.

## Overview:

The default taker fee on Carbon DeFi for Ethereum is 0.2% and 0.4% on the Sei v2 deployment. This means that anyone taking an order from the protocol has to pay this amount. Previous proposals:

https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades/4540
https://gov.bancor.network/t/custom-taker-fee-on-stable-to-stable-trades/4370

have been brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across all DEXs (e.g. On uniswap v3, stable to stable trading pairs are typically set to 1 basis point).

This proposal is seeking to expand the custom taker fee to the USDT-USDC trading pair on Sei v2. Specifically, these two tokens:

https://seitrace.com/token/0x3894085Ef7Ff0f0aeDf52E2A2704928d1Ec074F1?chain=pacific-1

https://seitrace.com/token/0xB75D0B03c06A926e488e2659DF1A861F860bD3d1?chain=pacific-1

Why these two tokens? This USDC is minted on noble (https://www.circle.com/en/multi-chain-usdc/noble) which is an app chain on Cosmos that is specifically built f

====================================================================================================
[39] id=0xa187a5d0a85a2b341683148e10cb9196d90fd3bbbc4f79eb1fd3a655efed80cc  token=BNT  space=bancornetwork.eth  date=2024-07-22
TITLE: Proposal to Deploy CarbonDeFi on CELO
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TLDR

* CELO is an EVM Blockchain
* CELO plans to become an [Ethereum L2](https://forum.celo.org/t/clabs-proposes-migrating-celo-to-an-ethereum-l2-leveraging-the-op-stack/7902)
* As with every deployment of CarbonDeFi, the Arb Fast Lane framework will be deployed as well.
* Fees will be used in the same way they are in the Ethereum and SEI deployments.

# Summary

* CELO is a Mobile-first, EVM compatible and Carbon negative blockchain.
* We have already seen CarbonDeFi’s performance on inexpensive fast chains is impressive.
* The [Credit Collective](https://www.credit-collective.com/) is very interested in this CarbonDeFi deployment
  * The Credit Collective will work to ensure there is deep liquidity on CarbonDeFi
* As with every deployment of CarbonDeFi, the Arb Fast Lane framework will be deployed as well.
* Fees generated by the deployment will be used exactly the same as fees generated by the Ethereum Deployment
  * Upon launch, fees will be held in the vortex until a bridging solution is decided upon in a future proposal and then can be sent to the CarbonDeFi Vortex on Mainnet.
* This proposal suggests setting the taker fee at 20 basis points
  * This is a parameter that can be adjusted by the DAO.
  * 20 BPs is being proposed as many of the [tokens expected](https://forum.celo.org/t/credit-collective-update/8336) are likely to be less volatile than on the SEI deployment:
* Upon deployment, this proposal does not suggest any custom fee for stable to stable trades. Whi

====================================================================================================
[40] id=0x59391c0165c4533f90d379c92445f0da09d81b2c6e4ef02e1ea7dd3463168fff  token=BNT  space=bancornetwork.eth  date=2024-11-28
TITLE: Proposal to Deploy CarbonDeFi on the Upcoming COTI V2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TLDR

* COTI V2 is an EVM-compatible L2 expected to go live shortly.
* COTI V2 provides a developer-friendly ecosystem that provides the fastest and lightest solution for privacy on a public blockchain in a way that provides scalable access to Ethereum.
* As with every deployment of CarbonDeFi, the Arb Fast Lane framework will be deployed as well.
* Fees will be used in the same way they are in the Ethereum, SEI and CELO deployments.

# Summary

* # [COTI Explained: How Garbled Circuits Enhance Web3 Privacy](https://www.youtube.com/watch?v=AvEBZp4Uv_Y)

* We have already seen CarbonDeFi’s performance on inexpensive fast chains is impressive.
* COTI is very interested in this CarbonDeFi deployment and will work to ensure there is deep liquidity on CarbonDeFi.
* As with every deployment of CarbonDeFi, the Arb Fast Lane framework will be deployed as well.
* Fees generated by the deployment will be used exactly the same as fees generated by the Ethereum, SEI and CELO deployments.
* This proposal suggests setting the taker fee at 20 basis points
  * This is a parameter that can be adjusted by the DAO.
* Upon deployment, this proposal does not suggest any custom fee for stable to stable trades. While the author of this proposal would like to have something similar to what was done on mainnet ([link](https://vote.bancor.network/#/proposal/0xcafe6326cfc8003ed379b1a77c50644825e334476b4db21feb60bf4ef65287fb)), it might make more sense to see which stables people are interested in usi

====================================================================================================
[41] id=0x195455187098fe90aa31940ee838795ce5a3a34a30c90c21bb63f6d5e840172b  token=BNT  space=bancornetwork.eth  date=2024-12-20
TITLE: Proposal: Remove Bancor 3 Fee Discount From ArbFastLane
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TLDR

* The Arb Fast Lane Protocol was created in early 2023 following this proposal: https://vote.bancor.network/#/proposal/0x81a10363baa0af61879e9b67142d17a8c23157c7a2a6259e36eb72192f6ab791
* Since then, the protocol has been a massive success: https://dune.com/bancor/arbfastlane-ecosystem
* The Arb Fast Lane has a few purposes
  * Help ensure Carbon DeFi’s users have their strategies filled when in the money
  * Use gains to bring pools to a state of surplus
  * It provides a large number of additional benefits to blockchains such as making markets more efficient, filling blocks, sending transactions to the wider DeFi ecosystem on that chain - but this is beyond the scope of this proposal as none of this will change.
* From the start, it was recognized that the Bancor 3 fee discount could potentially be taken advantage of, though it was uncertain whether the benefits would justify the effort required to do so.
* In recent weeks,likely due to market movements, multiple attempts, some successful, to take advantage of the discount while avoiding the protocol receiving its due portion of the arbitrage.
* Instead of engaging in a time consuming and expensive game of cat and mouse, this proposal suggests simply removing the fee discount.
* This would make the Arb Fast Lane on mainnet function exactly like it does on CELO, SEI and all other chains where it is active.

# Will the Bot Support Bancor3?

* If you want to arb vs Bancor 3 - You will need to update the bot to ensure i

====================================================================================================
[42] id=0x4473088a86c02eba328bce080fbf9180f641ee1b59918bdc86898a56969d8e1e  token=BNT  space=bancornetwork.eth  date=2025-04-14
TITLE: Proposal: Expand Custom Taker Fee on Stable to Stable Trades On Sei v2 - USDT0
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
## TL;DR:

A previous proposal was brought up to the Bancor DAO that set a 0.001% (1/10th of a basis point) fee on stable to stable trades for certain trading pair(s) on Sei v2.

This proposal is looking to expand that list with the new to be launched USDT0 and possible combinations of USDT0 with other popular stablecoins (USDC, KAVA-USDT).

## Overview:

The default taker fee on Carbon DeFi Sei v2 deployment is 0.4% which means that anyone taking an order from the protocol has to pay this amount. A previous proposal:

https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades-on-sei-v2/4630

was brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across all DEXs.

This list currently encompasses the following trading pairs:

USDC / KAVA-USDT

This proposal is seeking to expand the custom taker fee to these other stable pairs.

USDC / USDT0

USDT0 / KAVA-USDT

What is Kava USDT?

On Sei Mainnet, a bridged form of USDT exists, which has been bridged from Kava via IBC.

What is USDT0?

USDT0 is the official standard for USDT on Sei Mainnet. It's backed 1:1 by locked assets on Ethereum and ensures seamless interoperability across blockchain networks via the LayerZero protocol.

What are some differences?

![diffs.png](ipfs://bafkreiaxxs2bwpmw64gbw6fgqkp6vwfntk6c53alnyse4ii47yadjpqnay)

What are t

====================================================================================================
[43] id=0x09ad60732d17c275c6d6e7b40522e5a0f9f9ef368be861364fb645be246d54b2  token=BNT  space=bancornetwork.eth  date=2025-06-19
TITLE: Proposal to Deploy CarbonDeFi on TAC
CHOICES: FOR | AGAINST | ASBTAIN
TEXT (first 1500 characters):
# TLDR

* TAC is a purpose-built blockchain for EVM dApps to access TON and Telegram Ecosystem’s 1B+ users base.
* As with every deployment of CarbonDeFi, the Arb Fast Lane framework will be deployed as well.
* Fees will be used in the same way they are in the Ethereum, SEI, CELO and COTI deployments.

# Summary

* For a quick overview or TAC click [here](https://tac.build/)
* We have already seen CarbonDeFi’s performance on inexpensive fast chains is impressive.
* TAC is very interested in this CarbonDeFi deployment and will work to ensure there is deep liquidity on CarbonDeFi.
* As with every deployment of CarbonDeFi, the Arb Fast Lane framework will be deployed as well.
* Fees generated by the deployment will be used exactly the same as fees generated by the Ethereum, SEI, CELO and COTI deployments.
* This proposal suggests setting the taker fee at 20 basis points
  * This is a parameter that can be adjusted by the DAO.
* Upon deployment, this proposal does not suggest any custom fee for stable to stable trades. While the author of this proposal would like to have something similar to what was done on mainnet ([link](https://vote.bancor.network/#/proposal/0xcafe6326cfc8003ed379b1a77c50644825e334476b4db21feb60bf4ef65287fb)), it might make more sense to see which stables people are interested in using and then creating the special fee tier.

# FOR

Deploy on TAC with a taker fee of 20 BP

# AGAINST

Take no action

====================================================================================================
[44] id=0x9b4cc6553e1b12fae152520a4e079b7e002f3e94aea10ce10b181bef5cbaa5e9  token=BNT  space=bancornetwork.eth  date=2025-08-07
TITLE: Proposal: Expand Custom Taker Fee on Stable to Stable Trades On Sei v2 - Native USDC
CHOICES: ABSTAIN | FOR | AGAINST
TEXT (first 1500 characters):
TL;DR:

A previous proposal was brought up to the Bancor DAO that set a 0.001% (1/10th of a basis point) fee on stable to stable trades for certain trading pair(s) on Sei v2.

This proposal is looking to expand that list with the newly launched Native USDC and possible combinations of Native USDC with other popular stablecoins (USDC.n, kavaUSDT, and USDT0).

Overview:

The default taker fee on Carbon DeFi Sei v2 deployment is 0.4% which means that anyone taking an order from the protocol has to pay this amount. A previous proposal:

was brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across all DEXs.

This list currently encompasses the following trading pairs:

USDC.n / kavaUSDT

USDC.n / USDT0

USDT0 / kavaUSDT

This proposal is seeking to expand the custom taker fee to these other stable pairs.

Native USDC / USDC.n

Native USDC / USDT0

Native USDC / KavaUSDT

What is Kava USDT?

On Sei Mainnet, a bridged form of USDT exists, which has been bridged from Kava via IBC.

What is USDT0?

USDT0 is the official standard for USDT on Sei Mainnet. It’s backed 1:1 by locked assets on Ethereum and ensures seamless interoperability across blockchain networks via the LayerZero protocol.

What is Native USDC?

The official form of USDC on Sei Mainnet issued by Circle, backed 100% by highly liquid cash and cash-equivalent assets

====================================================================================================
[45] id=0xd186764d72ae80f308178baf229eee036217359cd07d5496947ebf46555b936c  token=BNT  space=bancornetwork.eth  date=2025-09-26
TITLE: Proposal: Expand Custom Taker Fee on Stable to Stable Trades on Celo
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
TL;DR

Previous proposal have been brought up to the Bancor DAO that set a 0.001% (1/10th of a basis point) fee on stable to stable trades for certain trading pairs.

This proposal is looking to expand on these previous proposals by setting a lower fee on the following:

USDT-USDCcUSD-USDTcUSD-USDCUSDGLO-USDTUSDGLO-USDCUSDGLO-cUSD

trading pairs on the Carbon DeFi deployment on Celo.

Overview:

The default taker fee on Carbon DeFi for CELO is 0.2%. This means that anyone taking an order from the protocol has to pay this amount. Previous proposals:

have been brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across all DEXs (e.g. On Uniswap v3/v4, stable to stable trading pairs are typically set to 1 basis point).

This proposal is seeking to expand the custom taker fee to the following six trading pairs on CELO. Specifically, these trading pairs:

USDT-USDCcUSD-USDTcUSD-USDCUSDGLO-USDTUSDGLO-USDCUSDGLO-cUSD

that have the following CAs:

USDT (https://celoscan.io/address/0x48065fbBE25f71C9282ddf5e1cD6D6A887483D5e)

USDC (https://celoscan.io/address/0xcebA9300f2b948710d2653dD7B07f33A8B32118C)

cUSD (https://celoscan.io/address/0x765de816845861e75a25fca122bb6898b8b1282a)

USDGLO (https://celoscan.io/address/0x4f604735c1cf31399c6e711d5962b2b3e0225ad3)

Why these tokens?

USDT: This is the official tether USDT on CELO.

USD

====================================================================================================
[46] id=0xc2c265b0a6d29b8f56482aacf48681eaeee2978f23ac94eab21d5ff938c9c4ae  token=BNT  space=bancornetwork.eth  date=2025-10-02
TITLE: Proposal: Expand Custom Taker Fee on Stable to Stable Trades On Sei v2 - Synnax USD
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
Previous proposals have been brought up to the Bancor DAO that set a lower fee on stable to stable trades for certain trading pair(s) on Sei v2.

This proposal is looking to expand that list and include SyUSD with a 1 bps taker fee. syUSD is the native stablecoin for the SEI Network, built to make capital useful. It’s overcollateralized, fast, and designed to move — not sit idle.

Overview:

The default taker fee on Carbon DeFi Sei v2 deployment is 0.4% which means that anyone taking an order from the protocol has to pay this amount. Previous proposals:

https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades-on-sei-v2/4630
https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades-on-sei-v2-usdt0/4895
https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades-on-sei-v2-native-usdc/4942

have been brought up to the Bancor DAO to lower this fee on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across other DEXs.

This list currently encompasses the following trading pairs:

USDC.n / kavaUSDT

USDC.n / USDT0

USDT0 / kavaUSDT

Native USDC / USDC.n

Native USDC / USDT0

Native USDC / KavaUSDT

This proposal is seeking to expand the custom taker fee to these other stable pairs.

syUSD / Native USDC

What is Synnax?

Synnax is a modular stablecoin protocol built to unify fragmented yield ac

====================================================================================================
[47] id=0x2c643633ec2f351c4ec970bbdfc4e2fe4bbb02930ef632653b25d23645c70544  token=BNT  space=bancornetwork.eth  date=2026-05-09
TITLE: Proposal: Custom Taker Fee on Stable to Stable Trades On TAC - USDT, USN, sUSN
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
### TL;DR:

Previous proposals have been brought up to the Bancor DAO that set a 0.001% (1/10th of a basis point) fee on stable to stable trades for certain trading pairs.

This proposal is looking to expand on these previous proposals by setting a lower fee on the following:

USDT/USN

USDT/sUSN

USN/sUSN

trading pairs on the Carbon DeFi deployment on TAC.

### Overview:

The default taker fee on Carbon DeFi TAC deployment is 0.2% which means that anyone taking an order from the protocol has to pay this amount. Previous proposals:

[https://gov.bancor.network/t/custom-taker-fee-on-stable-to-stable-trades/4370](https://gov.bancor.network/t/custom-taker-fee-on-stable-to-stable-trades/4370)

<https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades/4540>

have been brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across all DEXs.

This proposal is seeking to expand the custom taker fee to these other stable pairs.

USDT/USN

USDT/sUSN

USN/sUSN

What is USDT?

On TAC, a bridged form of USDT exists. This is considered the canonical form of USDT.

What is USN?

US Noon, or USN, is Noon's stablecoin. It maintains a 1:1 peg to the US Dollar. USN is deployed on Ethereum, ZKSync, Sophon, TAC & Starknet.

What is sUSN?

USN can be staked via the Noon dApp. Staking USN gives users access to a stak

====================================================================================================
[48] id=0x23b6e71d2a5bcb4384685510cf010c483c50b30b0fbf2b58f221de9e9db9951d  token=BNT  space=bancornetwork.eth  date=2026-06-05
TITLE: Proposal: Custom Taker Fee on Stable to Stable Trades On Ethereum - USDS, USDe, PYUSD, USDG, RLUSD, GHO
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
### **TL;DR:**

Previous proposals have been brought up to the Bancor DAO that set a 0.001% (1/10th of a basis point) fee on stable to stable trades for certain trading pairs.

This proposal is looking to expand on these previous proposals by setting a lower fee on the following:

USDS/USDT
USDS/USDC
USDS/DAI

USDe/USDT
USDe/USDC
USDe/USDS

PYUSD/USDT
PYUSD/USDC
PYUSD/USDS

USDG/USDT
USDG/USDC
USDG/USDS

RLUSD/USDT
RLUSD/USDC
RLUSD/USDS

GHO/USDT
GHO/USDC
GHO/USDS

trading pairs on the Carbon DeFi deployment on Ethereum.

### **Overview:**

The default taker fee on Carbon DeFi Ethereum deployment is 0.2% which means that anyone taking an order from the protocol has to pay this amount. Previous proposals:

[https://gov.bancor.network/t/custom-taker-fee-on-stable-to-stable-trades/4370](https://gov.bancor.network/t/custom-taker-fee-on-stable-to-stable-trades/4370)

[https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades/4540](https://gov.bancor.network/t/proposal-expand-custom-taker-fee-on-stable-to-stable-trades/4540)

have been brought up to the Bancor DAO to lower this fee to 0.001% on stable to stable trades for certain trading pairs in order to make Carbon DeFi more competitive with stable to stable swaps that are normally lower across all DEXs.

This proposal is seeking to expand the custom taker fee to these other stable pairs.

USDS/USDT
USDS/USDC
USDS/DAI

USDe/USDT
USDe/USDC
USDe/USDS

PYUSD/USDT
PYUSD/USDC
PYUSD/USDS

USDG/USDT
USDG/U

====================================================================================================
[49] id=0x40dea915d16630d3e0fa310880719207a789bfb8f913fe2f01e62bc361a5c478  token=CAKE  space=cakevote.eth  date=2023-11-16
TITLE: Proposal to Adjust Voting Power Requirements to Reduce Spam
CHOICES: ✅ Yes, reduce spam and increase voting power! | ❌ No, don't reduce spam and increase voting power!
TEXT (first 1500 characters):
#### Proposal to Adjust Voting Power Requirements to Reduce Spam

PancakeSwap’s community involvement and user voices have always been an integral part of decision making and guiding the future of the protocol. It is important to ensure that the most productive suggestions and proposals from active contributors are heard and executed upon. Recently, there has been an uptick in spam proposals, which dilutes the community and the Kitchen’s ability to respond to and integrate with the strongest recommendations.

This vote is to increase the required voting power needed to create a proposal. The amount of CAKE required will remain modest and does not greatly affect the ability of contributors from making their voices heard – but will help to prevent spam proposals that do not relate to the future of PancakeSwap and make it easier for admins and the Kitchen to review serious community suggestions. If any community member cannot reach this voting power threshold, they are always welcome to share feedback and suggestions through PCS Ambassadors and Chefs in the **[Telegram Group](https://t.me/PancakeSwap/2791670)**.


#### Overview of Current Proposal Creation Requirements

**There are currently two types of proposals supported:**

1️⃣ Core - proposals posted by the PancakeSwap team. These are used to align the recommendations of the Kitchen and the community.

2️⃣ Community - proposals posted by the PancakeSwap community. These are used to propose ideas and show the community's poi

====================================================================================================
[50] id=0xb337dce860f1173b6e17336be7476f1ea6f2c11a2efdeb842ab350b49662234f  token=CAKE  space=cakevote.eth  date=2023-11-16
TITLE: Proposal for CAKE Rewards on Range Protocol’s Vaults
CHOICES: ✅ We want CAKE Rewards on Range Protocol’s Vaults! | ❌ We don’t want CAKE Rewards on Range Protocol’s Vaults!
TEXT (first 1500 characters):
#### PancakeSwap Welcomes Range Protocol’s Integration to Position Manager on BNB & ETH Chain!

Dear CAKE holders, we’re excited to announce a new position manager integration with Range Protocol on BNB Chain & Ethereum.


Range Protocol is a liquidity management protocol that helps users manage their assets, optimize their earnings, and reduce the effort needed for managing positions. 


Depending on their preferences, users can deposit their tokens into Range Protocol’s vaults with three different strategies. Range Protocol’s smart contracts will then manage the liquidity positions on PancakeSwap’s v3 AMM based on the strategy selected to earn CAKE and LP rewards.

Range Protocol’s three strategies are: 
- **Pegged:** creates LP positions in a very narrow range around the current price
- **Active Strategy** creates LP positions in a narrow range around the current price
- **Passive Strategy**  creates LP positions in a wide range around the current price
Learn more about them [**here**](https://range-protocol.gitbook.io/range-protocol/amm-vaults/strategy-details).

#### Range Protocol’s Vaults & Liquidity Pools:

Deposit tokens into Range Protocol’s Vaults to earn additional CAKE rewards on top of LP rewards.


CAKE rewards will be distributed with the following criteria:
- **Distribution duration:** 14 days
- **Total tokens:** 2250 CAKE 
- **Start time:** Approx. 1200 UTC on 17 Nov 2023
- **Finish time:** Approx. 1200 UTC on 1 Dec 2023

The incentives will be distributed i

====================================================================================================
[51] id=0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c  token=CAKE  space=cakevote.eth  date=2023-11-21
TITLE: Proposal to Launch veCAKE
CHOICES: ✅ Yes, we want to launch veCAKE! | ❌ No, we don't want to launch veCAKE!
TEXT (first 1500 characters):
#### Proposal to Launch veCAKE Gauges System

![](https://i.imgur.com/8kO0mY8.jpg)

#### Vote-Escrowed CAKE Overview

Over the next few days, the Kitchen is proposing to introduce **veCAKE**. This update is designed to empower CAKE holders with increased governance influence, boost liquidity across our pools, and supercharge rewards for CAKE stakers.

As announced in our [**Q4 Roadmap**](https://docs.pancakeswap.finance/readme/roadmap), PancakeSwap will be shortly launching vote-escrowed CAKE (veCAKE) and voting gauges. Voting gauges allow for veCAKE holders to vote on where future CAKE farm emissions will be directed.

Launching voting gauges will allow existing CAKE holders, stakers and protocols to begin accumulating veCAKE.

**At a high level, veCAKE holders will be able to:**

1️⃣ **Direct Gauge Emissions** - veCAKE holders will be able to directly impact how CAKE emissions are distributed within each pool, rewarding specific liquidity pools and projects. Rewards and gauge weights are determined through voting power, which will be determined by veCAKE balance.

2️⃣ **Enable 3rd Party Protocols through Delegation** - external protocols, such as veCAKE managers and bribe markets, will compete to earn a share of veCAKE voting rights in order to direct CAKE rewards and receive voting incentives for doing so. veCAKE holders can opt to delegate their CAKE to automate their voting and potentially earn boosted rewards. However, direct participation is highly encouraged!
 
Voting

====================================================================================================
[52] id=0x7c0d0661dd646c6b5b812edc44d6d886335bc3856cfdb9e3048b1a09b5cb6ce0  token=CAKE  space=cakevote.eth  date=2023-11-24
TITLE: Proposal for CAKE Rewards on Bril Finance’s Vaults
CHOICES: ✅ We want CAKE Rewards on Bril Finance’s Vaults! | ❌ We don’t want CAKE Rewards on Bril Finance’s Vaults!
TEXT (first 1500 characters):
#### PancakeSwap Welcomes Bril Finance’s Integration to Position Manager on BNB Chain!

Dear CAKE holders, we’re excited to announce an extension for CAKE rewards on Bril’s vaults. 


Bril Finance offers a DeFi integration that helps users manage their assets, optimize their earnings, and reduce the effort needed for managing positions. 

Users can deposit single-sided assets into Bril's vaults which are managed by Bril's smart contracts. These smart contracts will allocate the assets into PancakeSwap's v3 AMMs with a range of automated liquidity strategies to earn CAKE yield for users.

The CAKE rewards on Bril’s vaults have been adjusted to ensure **CAKE is distributed in a sustainable and beneficial manner for CAKE holders.**

#### Bril Finance’s Vaults & Liquidity Pools:

Deposit single-sided assets to earn additional CAKE rewards on top of LP rewards. (Please note that the deposit token is the **first token** in the pair).

For example, for the **USDT**-WBNB (0.05%) pair, users will deposit USDT ONLY, and the SC will execute strategies to utilize the deposited USDT for the USDT-WBNB (0.05%) LP.


Vaults with an additional 1000 CAKE rewards:
- **WBNB**-CAKE (0.25%)
- **USDT**-CAKE (0.25%) 
- **BTCB**-CAKE (0.25%)

Vaults with an additional 400 CAKE rewards:
- **USDT**-WBNB (0.05%)
- **BTCB**-USDT (0.05%)
- **ETH**-CAKE (0.25%)
- (**NEW**) **USDC**-ETH (0.05%)

CAKE rewards will be distributed with the following criteria:
- **Distribution duration:** 28 days
- **Total toke

====================================================================================================
[53] id=0xeb163a0ee97e5c0029b070a98911e64340d1c1d49b65d652363cc8a81caa1ad1  token=CAKE  space=cakevote.eth  date=2023-11-30
TITLE: Proposal for CAKE Rewards on Range Protocol’s Vaults
CHOICES: ✅ We want CAKE Rewards on Range Protocol’s Vaults! | ❌ We don’t want CAKE Rewards on Range Protocol’s Vaults!
TEXT (first 1500 characters):
#### PancakeSwap Welcomes Range Protocol’s Integration to Position Manager on BNB Chain & Ethereum!

Dear CAKE holders, we’re excited to announce an extension of CAKE rewards for Range Protocol on BNB Chain & Ethereum.


Range Protocol is a liquidity management protocol that helps users manage their assets, optimize their earnings, and reduce the effort needed for managing positions. 


Depending on their preferences, users can deposit their tokens into Range Protocol’s vaults with three different strategies. Range Protocol’s smart contracts will then manage the liquidity positions on PancakeSwap’s v3 AMM based on the strategy selected to earn CAKE and LP rewards.

Range Protocol’s three strategies are: 
- **Pegged:** creates LP positions in a very narrow range around the current price
- **Active Strategy** creates LP positions in a narrow range around the current price
- **Passive Strategy**  creates LP positions in a wide range around the current price
Learn more about them [**here**](https://range-protocol.gitbook.io/range-protocol/amm-vaults/strategy-details).

#### Range Protocol’s Vaults & Liquidity Pools:

Deposit tokens into Range Protocol’s Vaults to earn additional CAKE rewards on top of LP rewards.


CAKE rewards will be distributed with the following criteria:
- **Distribution duration:** 14 days
- **Total tokens:** 1300 CAKE 
- **Start time:** Approx. 1200 UTC on 1 Dec 2023
- **Finish time:** Approx. 1200 UTC on 15 Dec 2023

The incentives will be distributed in

====================================================================================================
[54] id=0x467bc39ce202e48db6ffa01083437907ef12be32af18eed88bd3bd08ac9586c0  token=CAKE  space=cakevote.eth  date=2023-12-06
TITLE: Proposal for CAKE Rewards on DefiEdge’s Vaults
CHOICES: ✅ We want CAKE Rewards on DefiEdge’s Vaults! | ❌ We don’t want CAKE Rewards on DefiEdge’s Vaults!
TEXT (first 1500 characters):
#### PancakeSwap Welcomes DefiEdge’s Integration to Position Manager on BNB Chain, Arbitrum, zkSync, Polygon zkEVM & Base!

Dear CAKE holders, we’re excited to announce a new position manager integration with DefiEdge on BNB Chain, Arbitrum, zkSync, Polygon zkEVM & Base!


DefiEdge is a liquidity management protocol that helps users manage their assets, optimize their earnings, and reduce the effort needed for managing positions. 


Users can deposit their tokens into DefiEdge’s vaults with a single unified strategy. DefiEdge’s smart contracts will adjust the LP based on market volatility and trends, aiming to maintain a balanced 50-50 position across various ranges, enabling users to earn both CAKE and LP rewards.

#### DefiEdge’s Vaults & Liquidity Pools:

Deposit tokens into DefiEdge’s Vaults to earn additional CAKE rewards on top of LP rewards.


CAKE rewards will be distributed with the following criteria:
- **Distribution duration:** 14 days
- **Total tokens:** 1435 CAKE  and 600 MATIC 
- **Start time:** Approx. 1200 UTC on 7 Dec 2023
- **Finish time:** Approx. 1200 UTC on 21 Dec 2023

The CAKE incentives will be distributed in the following vaults:
- **USDT-WBNB 0.05% (BNB Chain)** - 410 CAKE
- **WBNB-CAKE 0.25% (BNB Chain)** - 410 CAKE
- **USDC-ETH 0.05% (zkSync)** - 205 CAKE
- **ARB-ETH 0.05% (Arbitrum)** - 205 CAKE
- **USDC-USDbC 0.05% (Base)** - 205 CAKE

The MATIC incentives will be distributed in the following vaults:
- **USDC-ETH 0.05% (zkEVM)** - 600 MATIC

The

====================================================================================================
[55] id=0xbfd1988eb0b48a966fbc809f3713258d1743c3ab61876cc9012e625116a93a1e  token=CAKE  space=cakevote.eth  date=2023-12-12
TITLE: Proposal to migrate vCAKE to veCAKE
CHOICES: ✅ Yes, migrate vCAKE to veCAKE! | ❌ No, do not migrate vCAKE to veCAKE!
TEXT (first 1500 characters):
#### Proposal to migrate vCAKE to veCAKE

We propose to migrate PancakeSwap’s voting rights from vCAKE to veCAKE. If this proposal passes, veCAKE will become the measurement of a user’s voting power in PancakeSwap’s governance system.

#### Background of veCAKE

veCAKE was a culmination of many major PancakeSwap milestones - CAKE becoming deflationary, establishing a wide multichain reach, and launching our V3 concentrated liquidity pools. These three factors had to be in place in order for veCAKE to be feasible and effective. 

Now, we look towards the veCAKE system to further CAKE locking and deflation, onboard the liquidity of new projects in our multichain deployments, all while leveraging our highly capital efficient V3 pools.

Additionally, via this proposal, veCAKE holders will be able to participate in PancakeSwap’s governance system, ranging from protocol adjustments to gauge approvals.

#### veCAKE’s Governance Rights

This is the scope of governance topics that veCAKE holders can vote on: 

1. [Core] High-level CAKE emission adjustments (allocating CAKE to Core Pools and other high-level categories)
2. [Core] Protocol adjustments (product changes, fee changes)
3. [Core] Multichain warchest spending
4. Regular gauges voting (every 2 weeks)

Similar to the vCAKE system now, we propose that Core topics must be voted on by veCAKE holders, but can only be proposed by the PancakeSwap Core Team. 

#### Gauges System

Our veCAKE / gauges system works in 14-day epochs and l

====================================================================================================
[56] id=0x1b9abebac478e44b11bd93071c4332d79ebf13d24842f5416c630c165fb575e7  token=CAKE  space=cakevote.eth  date=2023-12-15
TITLE: Proposal for CAKE allocation to Position Managers
CHOICES: ✅ Yes, allocate CAKE rewards for Position Managers! | ❌ No, do not allocate CAKE rewards for Position Managers!
TEXT (first 1500 characters):
#### Proposal for CAKE allocation to Position Managers

![](https://i.imgur.com/Zr9BtII.jpg)


Over the past few months, the Kitchen has launched various Position Manager vaults across our various deployments on BNB Chain, Ethereum, Arbitrum, Base and zkSync Era. 

These Position Managers have performed well, driving ~$250M in trading volume, and increasing TVL by ~$6M. 

Importantly, these position managers have also enabled users to provide concentrated liquidity in a simplified manner.

With these benefits, the kitchen feels that the value proposition of the Position Manager is strong, and will continue to expand on new vaults and new chains for this Product.

#### CAKE Allocation Details 

CAKE incentives for previous Position Manager vaults have been implemented individually through PancakeSwap’s governance process. 

In order to streamline the onboarding process for Position Managers on PancakeSwap, the Kitchen is requesting the allocation of **20,000 CAKE**. 

The tokens will be allocated among various Position Manager vaults over the next few weeks. 

This distribution will be carried out in a way that will maximize the TVL, Volume, and ultimately the CAKE Burn generated from incentivized vaults.

The Kitchen will share regular updates on the performance of these Position Manager’s vaults on our brand spanking new [** forum**](https://forum.pancakeswap.finance/). 

The CAKE tokens will not come from increased emissions, but rather will be taken from our ‘Multichain Wa

====================================================================================================
[57] id=0x42d83e1b454716dc1aba80560a5df7961e352808fd61107a6e716537584e3f3b  token=CAKE  space=cakevote.eth  date=2023-12-18
TITLE: Proposal for Adding CAKE Allocation to Bootstrap opBNB Liquidity
CHOICES: ✅ Yes, launch opBNB farms! | ❌ No, don't launch opBNB farms!
TEXT (first 1500 characters):
#### Proposal for Adding CAKE Allocation to Bootstrap opBNB Liquidity

PancakeSwap is proud to be expanding to opBNB and join BNB Chain’s leading Layer 2. This expansion will continue our path towards creating the smoothest and most user-friendly DeFi journey for everyone.

When expanding to new chains, it is important to begin with a **bang** and sustain that momentum. To do so, we require the help of our community, and also **juicy APRs**. For clarity, the Kitchen **will not be increasing emissions** to enable these farms, and will instead by drawing from the “Multichain Warchest” allocation:

 
![](https://imgur.com/W94mOao.png)

The initial set of farms are listed below:

- **BNB/USDT** (0.05% fee tier): 100 CAKE per day

While we will endeavor to highlight new farm requests prior to launch, for reasons for competitiveness and confidentiality, we request for flexibility in distributing farm emissions to potential high-impact pairs. For clarity, these farm emissions will again be drawn from the Multichain Warchest, and will not be drawn from increased emissions. 

We will continue to publish confirmation proposals (Aptos example [**here**](https://pancakeswap.finance/voting/proposal/0x959b9da76401a7a3fb73e417b69ef51859383bd523d887350ae9f69148fc26a8)) once chain deployments have reached a steady-state and ensure that the community is satisfied with our deployments.

# Timeline

1️⃣ This Proposal is submitted (18 December 2023)

2️⃣ PancakeSwap deploys new farms on opBNB (if

====================================================================================================
[58] id=0x0aebf3093bc6f4564ab84047fdf9c12f47cd3f308cc06f9942e15ca28f660e9a  token=CAKE  space=cakevote.eth  date=2023-12-22
TITLE: Proposal to Launch veCAKE on zkSync
CHOICES: ✅ Yes, we want to launch veCAKE on zkSync! | ❌ No, we don't want to launch veCAKE on zkSync!
TEXT (first 1500 characters):
![](https://i.imgur.com/4dp8fhR.jpg) 

#### Proposal to Launch veCAKE Gauges System on zkSync

As mentioned in our initial [**veCAKE proposal**](https://pancakeswap.finance/voting/proposal/0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c), we are launching veCAKE in phases, and are excited to share the next deployment - zkSync!

#### Recap: Vote-Escrowed CAKE Overview

As a quick summary, here’s quick recap of veCAKE, with the following utilities:

1️⃣ **Direct Gauge Emissions** - veCAKE holders will be able to directly impact how CAKE emissions are distributed within each pool, rewarding specific liquidity pools and projects. Rewards and gauge weights are determined through voting power, which will be determined by veCAKE balance.

2️⃣ **Enable 3rd Party Protocols through Delegation** - external protocols, such as veCAKE managers and bribe markets, will compete to earn a share of veCAKE voting rights in order to direct CAKE rewards and receive voting incentives for doing so. veCAKE holders can opt to delegate their CAKE to automate their voting and potentially earn boosted rewards. However, direct participation is highly encouraged!
 
#### Inclusion of zkSync in veCAKE Gauges System

Currently, the total rewards available for farm emissions on BNB Chain, Ethereum, and Arbitrum is **~0.99 CAKE/block**.  

With the inclusion of zkSync, the current **Trading Allocation** emission of 0.0131 CAKE per block directed towards zkSync Farms will be added to veCAKE e

====================================================================================================
[59] id=0x3e014aab40f6551da9f76da0e62e44e9ece55c4997f220057bf3e42dc8307c2f  token=CAKE  space=cakevote.eth  date=2023-12-28
TITLE: Proposal to Reduce CAKE Token Total Supply
CHOICES: ✅ Yes, we want to lower CAKE’s token supply! | ❌ No, we don't want to lower CAKE’s token supply!
TEXT (first 1500 characters):
#### Proposal to Reduce CAKE Token Total Supply

Over the past year, PancakeSwap has significantly revamped its tokenomics, emissions, and growth strategy. Starting from improving [**CAKE Tokenomics v2.5**](https://pancakeswap.finance/voting/proposal/0x707643dd2c2b941c7274f26a0362922198912e8549050ae9f2d1d9d71ada04bb) to most recently launching the [**veCAKE Gauges System**](https://pancakeswap.finance/voting/proposal/0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c), CAKE is in a position to pursue further growth across all deployments.

Now that CAKE has achieved consistent deflation for several months and is focusing on accelerating our journey to ultrasound CAKE, this proposal aims to reduce the CAKE token’s total supply to a **maximum cap of 450M CAKE**. 

With a current **total supply of 388M CAKE**, the Kitchen believes this new and lower cap will be sufficient to gain market share across all chains and sustain the veCAKE model.

![](https://imgur.com/kGk5kri.png)


#### Proposal Rationale:
There are several strong reasons to implement this adjustment:
- **Certainty for the community on future CAKE token supply**: 

When PancakeSwap launched in 2021, to ensure that there were sufficient incentives to bootstrap the ecosystem, there was significant token inflation. After almost 3 years in development, we now have more accurate estimations of incentives required to achieve our growth targets.

- **Accelerate the journey to ultrasound CAKE**: 

Total suppl

====================================================================================================
[60] id=0x9c54bc5c0861dc3131459c9e434a63a146200ef7fa17ac5348373bb1e03a2cee  token=CAKE  space=cakevote.eth  date=2023-12-29
TITLE: Proposal for Cakepie ($CKP) cIFO to be Hosted on PancakeSwap
CHOICES: ✅ Yes, let’s host the $CKP cIFO! | ❌ No, do not host the $CKP cIFO!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/15/64/ld8PgTdm_o.png)

# tl;dr

- Cakepie is a veCAKE Manager that boosts rewards for CAKE stakers and PancakeSwap’s liquidity providers
- PancakeSquad NFT holders and point holders **(≥ 1100 points)** are eligible for the Private Sale with 10% allocation, while the remaining 90% will be open to a Public Sale
- Flat participation fee of 1% for the Public Sale, 0% Participation Fee for the Private Sale

# Proposal and cIFO Timeline

- To allow the community to learn more about the project, we have published the cIFO proposal details on the PancakeSwap Forum on 29 Dec 2023, 1530 UTC, but voting will only start 24 hours later, on 30 Dec 2023, 1530 UTC
- Between publication and the start of voting, please comment under the [**Forum Topic**](https://forum.pancakeswap.finance/t/cakepie-cifo-discussion-thread/220) if you have any questions
- If the proposal is successful, there will be an AMA on 3 Jan 2024, 1200 UTC for the community to learn more from the team

# What is Cakepie?

Cakepie is a SubDAO created by Magpie to enhance the long-term sustainability of PancakeSwap. 

As a yield and veTokenomics service provider, Cakepie's core mechanism involves locking CAKE tokens as veCAKE. This process enables Cakepie to secure enhanced yields and amplified governance power within PancakeSwap, creating opportunities for DeFi users while simultaneously reducing the circulating supply of CAKE.

# What is CKP?

CKP is the primary token issued by Cakepie whic

====================================================================================================
[61] id=0xcbbd4b19bae851cb123f668bfacd2479e26848ea47714526bd5ca6dd8c001736  token=CAKE  space=cakevote.eth  date=2024-01-04
TITLE: Proposal to Launch veCAKE on Polygon zkEVM
CHOICES: ✅ Yes, we want to launch veCAKE on Polygon zkEVM! | ❌ No, we don't want to launch veCAKE on Polygon zkEVM!
TEXT (first 1500 characters):
#### Proposal to Launch veCAKE Gauges System on Polygon zkEVM

![](https://i.imgur.com/wBjmw8E.jpg)

As mentioned in our initial [**veCAKE proposal**](https://pancakeswap.finance/voting/proposal/0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c), we are launching veCAKE in phases, and are excited to share the next deployment - Polygon zkEVM!

#### Recap: Vote-Escrowed CAKE Overview

Here’s a quick recap of veCAKE’s utility:

1️⃣ **Direct Gauge Emissions** - veCAKE holders can directly impact how CAKE emissions are distributed within each pool, rewarding specific liquidity pools and projects. Rewards and gauge weights are determined through voting power, which will be determined by veCAKE balance.

2️⃣ **Enable 3rd Party Protocols through Delegation** - external protocols, such as veCAKE Managers, will compete to earn a share of veCAKE voting rights in order to direct CAKE emissions. veCAKE holders can opt to delegate their CAKE to potentially earn boosted rewards. However, direct participation is highly encouraged!
 
#### Inclusion of Polygon zkEVM in veCAKE Gauges System

Currently, the total rewards available for farm emissions on BNB Chain, Ethereum, Arbitrum, and zkSync Era is **~28,416 CAKE/day**.  

With the inclusion of Polygon zkEVM, the current **Trading Allocation** emission of ~125 CAKE/day directed towards Polygon zkEVM Farms will be added to veCAKE emissions. 

As voted for previously, the Kitchen will retain a **40% voting share** of total veCAK

====================================================================================================
[62] id=0x9e3ad540dbb9f751a78b25e97d0044a7de9e43fc45aa146403d4f23a0506ae23  token=CAKE  space=cakevote.eth  date=2024-01-16
TITLE: Proposal to Launch veCAKE on Linea
CHOICES: ✅ Yes, we want to launch veCAKE on Linea! | ❌ No, we don't want to launch veCAKE on Linea!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/24/4a/d5uKk8oF_o.jpg)

#### Proposal to Launch veCAKE Gauges System on Linea

As mentioned in our initial [**veCAKE proposal**](https://pancakeswap.finance/voting/proposal/0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c), we are launching veCAKE in phases, and are excited to share the next deployment - Linea!

#### Recap: Vote-Escrowed CAKE Overview

Here’s a quick recap of veCAKE’s utility:

1️⃣ **Direct Gauge Emissions** - veCAKE holders can directly impact how CAKE emissions are distributed within each pool, rewarding specific liquidity pools and projects. Rewards and gauge weights are determined through voting power, which will be determined by veCAKE balance.

2️⃣ **Enable 3rd Party Protocols through Delegation** - external protocols, such as veCAKE Managers, will compete to earn a share of veCAKE voting rights in order to direct CAKE emissions. veCAKE holders can opt to delegate their CAKE to potentially earn boosted rewards. However, direct participation is highly encouraged!
 
#### Inclusion of Linea in the veCAKE Gauges System

With the inclusion of Linea, the current **Trading Allocation** emission of ~125 CAKE/day directed towards Linea Farms will be added to veCAKE emissions. 

As voted for previously, the Kitchen will retain a **40% voting share** of total veCAKE votes currently allocated to the gauges system to vote for core pairs, such as USDC-ETH on Linea. This is to maintain the liquidity depth and volumes of

====================================================================================================
[63] id=0x12883dbf2fb692cd616a9ee5a9e90c8f87f8f11636278d3a7978074b339de1e0  token=CAKE  space=cakevote.eth  date=2024-01-29
TITLE: Proposal for Kitchen-Discretionary CAKE Emissions
CHOICES: ✅ Yes, we want to capture more TVL and volume! | ❌ No, we don't want Kitchen-discretionary CAKE emissions!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/ce/b7/KND9A2jE_o.png)

#### Proposal for Kitchen-Discretionary CAKE Emissions

After receiving feedback from the [**community**](https://forum.pancakeswap.finance/t/en-suggestions-for-quick-farm-launch/278), the Kitchen proposes to earmark up to **1%** of all CAKE emissions going to veCAKE gauges as Kitchen-discretionary emissions. 

This will allow the Kitchen to flexibly set up Farms for trending token pairs and capture crucial TVL and volume for PancakeSwap, thereby increasing CAKE burn for the community.
#### Rationale

With the launch of our veCAKE system, Farms are adjusted every 14 days based on the veCAKE vote allocation in the previous epoch. This makes it difficult for the Kitchen to launch ad-hoc Farms in a timely manner to capture TVL and volume for trending projects.

We have done this in the past with a high level of success. Examples include Binance Launchpool projects, tokens with trending narratives (e.g. BRC-20 and memecoins), etc. Some of these pairs were able to capture millions of volumes on their first few days of launch. 

The CAKE burned from the trading volume generated by such pairs usually heavily outweigh the CAKE emissions distributed to the Farms. This not only helps with CAKE’s deflationary momentum, but also increases PancakeSwap’s competitiveness as a premier trading venue.

#### Discretionary CAKE Emission Details

Currently, there is ~0.996 CAKE/block channeled towards veCAKE gauges. We propose to earmark up to

====================================================================================================
[64] id=0x8eff088ca5d8c07a1a0be979533b6aa36dd098edb62714f948c06cf561817432  token=CAKE  space=cakevote.eth  date=2024-02-06
TITLE: Proposal for Kitchen-Discretionary CAKE Emissions
CHOICES: ✅ Yes, we want to capture more TVL and volume! | ❌ No, we don't want Kitchen-discretionary CAKE emissions!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/ce/b7/KND9A2jE_o.png)

#### Proposal for Kitchen-Discretionary CAKE Emissions

After receiving feedback from the [**community**](https://forum.pancakeswap.finance/t/en-suggestions-for-quick-farm-launch/278), the Kitchen proposes to earmark up to **0.67%** of all CAKE emissions going to veCAKE gauges as Kitchen-discretionary emissions. 

This will allow the Kitchen to flexibly set up ad-hoc Farms for trending token pairs and capture crucial TVL and volume for PancakeSwap, thereby increasing CAKE burn for the community.
#### Rationale

With the launch of our veCAKE system, Farms are adjusted every 14 days based on the veCAKE vote allocation in the previous epoch. This makes it difficult for the Kitchen to launch ad-hoc Farms in a timely manner for trending projects, even if we were to use our Kitchen admin votes.

We also propose launching ad-hoc Farms this way instead of redirecting emissions from our ‘Multichain Warchest’ as the latter is a tedious operational process, will further increase CAKE supply, and takes ~3-4 days to fully take effect due to our smart contract design.

We have launched ad-hoc Farms in the past successfully. Examples include Binance Launchpool projects, tokens with trending narratives (e.g. BRC-20 and memecoins), etc. Some of these pairs were able to capture millions of trading volumes on their first few days of launch. 

The CAKE burned from the trading volume generated by such pairs usually heavily outweigh the CAKE em

====================================================================================================
[65] id=0x30f2e5d8b5460f6377dc4bf46dc10da5236bd04666edd0d5c4545a6d3431a101  token=CAKE  space=cakevote.eth  date=2024-02-07
TITLE: Proposal to Launch veCAKE on Base
CHOICES: ✅ Yes, we want to launch veCAKE on Base! | ❌ No, we don't want to launch veCAKE on Base!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/6d/94/LpChdp6q_o.jpg)

#### Proposal to Launch veCAKE Gauges System on Base

As mentioned in our initial [**veCAKE proposal**](https://pancakeswap.finance/voting/proposal/0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c), and because the Base folks dared us to, we are excited to share the next veCAKE deployment - Base!

#### Recap: Vote-Escrowed CAKE Overview

Here’s a quick recap of veCAKE’s utility:

1️⃣ **Direct Gauge Emissions** - veCAKE holders can directly impact how CAKE emissions are distributed within each pool, rewarding specific liquidity pools and projects. Rewards and gauge weights are determined through voting power, which will be determined by veCAKE balance.

2️⃣ **Enable 3rd Party Protocols through Delegation** - external protocols, such as veCAKE Managers, will compete to earn a share of veCAKE voting rights in order to direct CAKE emissions. veCAKE holders can opt to delegate their CAKE to potentially earn boosted rewards. However, direct participation is highly encouraged!
 
#### Inclusion of Base in the veCAKE Gauges System

With the inclusion of Base, the current **Trading Allocation** emission of ~378 CAKE/day directed towards Base Farms will be added to veCAKE emissions. 

As voted for previously, the Kitchen will retain a **40% voting share** of total veCAKE votes currently allocated to the gauges system to vote for core pairs, such as USDC-ETH on Base. This is to maintain the liquidity depth and volume

====================================================================================================
[66] id=0x57121617ce82be6faab483b2e83fa626593f51c4e9c71670be36bfaa6cd96bf1  token=CAKE  space=cakevote.eth  date=2024-04-04
TITLE: Proposal to Launch veCAKE on opBNB
CHOICES: ✅ Yes, we want to launch veCAKE on opBNB! | ❌ No, we don't want to launch veCAKE on opBNB!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/38/bf/YPaC9O4g_o.jpg)

#### Proposal to Launch veCAKE Gauges System on opBNB

As mentioned in our initial [**veCAKE proposal**](https://pancakeswap.finance/voting/proposal/0x9602c8f56d01f239b88ecf914ee263cc9cdd75b8d10ae4d9536fc27b2680849c), we are excited to share the next veCAKE deployment - opBNB!

#### Recap: Vote-Escrowed CAKE Overview

Here’s a quick recap of veCAKE’s utility:

1️⃣ **Direct Gauge Emissions** - veCAKE holders can directly impact how CAKE emissions are distributed within each pool, rewarding specific liquidity pools and projects. Rewards and gauge weights are determined through voting power, which will be determined by veCAKE balance.

2️⃣ **Enable 3rd Party Protocols through Delegation** - external protocols, such as veCAKE Managers, will compete to earn a share of veCAKE voting rights in order to direct CAKE emissions. Users who staked CAKE in the old Cake Pool can opt to delegate their CAKE to potentially earn boosted rewards. However, direct participation is highly encouraged!
 
#### Inclusion of opBNB in the veCAKE Gauges System

With the inclusion of opBNB, the current **Trading Allocation** emission of ~100 CAKE/day directed towards opBNB Farms will be added to veCAKE emissions. 

As voted for previously, the Kitchen will retain a **40% voting share** of total veCAKE votes currently allocated to the gauges system to vote for core pairs, such as USDT-BNB on opBNB. This is to maintain the liquidity depth and volumes of t

====================================================================================================
[67] id=0xbf8ac28356bd7ad863c7a1bf9fb66901b44430f274986a4e8793639f8214a747  token=CAKE  space=cakevote.eth  date=2024-04-08
TITLE: Proposal to recognize Mancake as an affiliate DEX on Mantle Network
CHOICES: ✅ Yes, we want to recognize Mancake as an affiliate DEX! | ❌ No, we don’t want to recognize Mancake as an affiliate DEX!
TEXT (first 1500 characters):
#### Proposal to recognize Mancake as an affiliate DEX

![](https://images2.imgbox.com/30/eb/VvGQPbIQ_o.jpeg)

Please refer to the following [**governance discussion**](https://forum.pancakeswap.finance/t/discussion-on-pancakeswap-affiliates-a-multichain-expansion-strategy/395) on the affiliate DEX proposal first raised by the Kitchen in late February and the Mancake team’s [**post**](https://forum.pancakeswap.finance/t/discussion-for-proposal-to-official-launch-mancake-as-a-pcs-affiliate-on-mantle-network/511/15) on our governance forum for details of the deployment.

Based on the above proposal from the Mancake team, the Kitchen proposes to recognize Mancake as an affiliate DEX on Mantle Network.

#### Rationale for recognition

This will allow PancakeSwap to grow on the Mantle blockchain network via a 3rd party affiliate team with strong execution capabilities to grow PancakeSwap’s influence and volume in a multichain world.

#### Summary terms

The Mancake team will require the following from the Kitchen and PancakeSwap
* Co-marketing support;
* Tech support as required, such as the full set of PCS-developed products without reliance on external partners (i.e. swap, liquidity, farm, upcoming PCSv4, staking, trading reward, Syrup pools, lottery, NFT, info, IFO) with tech support to help get Mancake up and running;
* At a future time, if Mancake also acts as a filler when PCSX is established, PancakeSwap will integrate such DEX into PCSX and preferentially execute trades vi

====================================================================================================
[68] id=0x41feef37054b6c090a2629d6eb2ed39f426f169b725cb565903e6b3ba1771bcc  token=CAKE  space=cakevote.eth  date=2024-04-16
TITLE: Proposal to Direct CAKE Emissions to Locker Protocols
CHOICES: ✅ Yes, we want to improve incentive efficiency and redirect CAKE! | ❌ No, we don’t want to improve incentive efficiency and redirect CAKE!
TEXT (first 1500 characters):
#### Proposal to Direct CAKE Emissions to Locker Protocols
![](https://i.imgur.com/B8wbReP.jpg)

In order to help bootstrap the veCAKE ecosystem and improve CAKE incentive efficiency, The Kitchen is proposing to redirect a portion of current CAKE emissions to participate in the veCAKE locker ecosystem (i.e., provide CAKE as bribes for strategic pools).

**Note:** no increase in overall CAKE emissions will occur under this proposal. Strategic pools include high volume and revenue driving pools such as: BNB-USDT, USDT-USDC, BTC-USDT, BNB-ETH, ETH-USDT, among others.

#### Summary: Redirection of CAKE Emissions to Bribes

The Kitchen is proposing to make the following modifications to current CAKE emissions:
* Reduce current emissions going to farming pools by 500 CAKE per day (from ~29,184 to ~28,684 CAKE per day).
* Allocate this 500 CAKE per day to participate in locker protocol bribes
* If this is successful in directing greater emissions to high volume pools to grow liquidity, then the Kitchen may request a larger amount in the future. The Kitchen will track these efforts to determine success based on pool volumes, TVL, and capital efficiency.
* This will not impact the deflationary status of CAKE as no emissions have been added or removed, only redirected.

How bribes will be allocated:
* The Kitchen will allocate bribes on a per epoch basis (i.e., every 14 days).
* The bribes will be distributed between any locker protocol built on veCAKE, including Cakepie, StakeDAO, and

====================================================================================================
[69] id=0xd58db3d317a410ef53fb850a834c9316644dac49e65999f9eee76537ec53e32b  token=CAKE  space=cakevote.eth  date=2024-05-27
TITLE: Proposal for Lista DAO ($LISTA) IFO to be Hosted on PancakeSwap
CHOICES: ✅ Yes, let’s host the $LISTA IFO! | ❌ No, do not host the $LISTA IFO!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/bd/fd/wceVKFfZ_o.png)

# tl;dr

- Lista DAO is a liquid staking and decentralized stablecoin protocol
- Users can liquid stake their BNB to receive slisBNB, and borrow lisUSD against accepted collateral assets
- PancakeSquad NFT holders and point holders **(≥ 1500 points)** are eligible for the Private Sale with 10% allocation, while the remaining 90% will be open to a Public Sale
- 0% participation fee for both the Public Sale and Private Sale

# IFO and Vote Proposal Timeline

- IFO Proposal Posted: 27 May 2024, 1200 UTC
- Voting Starts: 28 May 2024, 1200 UTC
- Voting Ends: 31 May 2024, 1200 UTC
- IFO Sale: June 2024
Between publication and the start of voting, please comment under the [**Forum Topic**](<insert forum link>) if you have any questions, or would like to join the discussions. 


The IFO Sale will happen in June 2024 – for compliance with other stakeholders involved in the LISTA IFO launch, we will communicate the timeline when the information can be made public.  

# A Note for Future IFOs:

Previously, IFO Vote Proposals were published to ensure we could seek the community’s decision on allocating precious CAKE towards the initial farms. 

Moving forward, as we will be using CAKE from our [**Kitchen-discretionary CAKE emissions**](https://pancakeswap.finance/voting/proposal/0x8eff088ca5d8c07a1a0be979533b6aa36dd098edb62714f948c06cf561817432) and Kitchen admin votes for these initial farms, we will be transitioning the IFO Vote P

====================================================================================================
[70] id=0x910b732e87993804b27bb93f9635d424f36fe760d0431865e02a7ccb96513bba  token=CAKE  space=cakevote.eth  date=2024-05-27
TITLE: (UPDATED) Proposal for Lista DAO ($LISTA) IFO to be Hosted on PancakeSwap
CHOICES: ✅ Yes, let’s host the $LISTA IFO! | ❌ No, do not host the $LISTA IFO!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/2b/45/MuffV1py_o.png)

# tl;dr

- Lista DAO is a liquid staking and decentralized stablecoin protocol
- Users can liquid stake their BNB to receive slisBNB, and borrow lisUSD against accepted collateral assets
- PancakeSquad NFT holders and point holders **(≥ 1500 points)** are eligible for the Private Sale with 10% allocation, while the remaining 90% will be open to a Public Sale
- 0% participation fee for both the Public Sale and Private Sale

# IFO and Vote Proposal Timeline

- IFO Proposal Posted: 27 May 2024, 1200 UTC
- Voting Starts: 28 May 2024, 1200 UTC
- Voting Ends: 31 May 2024, 1200 UTC
- IFO Sale: June 2024
Between publication and the start of voting, please comment under the [**Forum Topic**](https://forum.pancakeswap.finance/t/lista-dao-ifo-discussion-thread/595) if you have any questions, or would like to join the discussions. 


The IFO Sale will happen in June 2024 – for compliance with other stakeholders involved in the LISTA IFO launch, we will communicate the timeline when the information can be made public.  

# A Note for Future IFOs:

Previously, IFO Vote Proposals were published to ensure we could seek the community’s decision on allocating precious CAKE towards the initial farms. 

Moving forward, as we will be using CAKE from our [**Kitchen-discretionary CAKE emissions**](https://pancakeswap.finance/voting/proposal/0x8eff088ca5d8c07a1a0be979533b6aa36dd098edb62714f948c06cf561817432) and Kitchen admin votes for these in

====================================================================================================
[71] id=0xaffca49c859c6012ad7c969fe7afd1caa8d3386636ab8ccb12a5b5e5ae922e6a  token=CAKE  space=cakevote.eth  date=2024-10-01
TITLE: Proposal to Redirect Emissions for Ecosystem Growth
CHOICES: ✅ Yes, we want to utilize emissions more efficiently and redirect CAKE! | ❌ No, we don’t want to utilize emissions more efficiently and redirect CAKE!
TEXT (first 1500 characters):
![](https://images2.imgbox.com/1a/70/vjGlPBHY_o.png)

To enhance activity and growth across our upcoming products in the PancakeSwap Roadmap, the Kitchen proposes to redirect emissions from our Farms to a new allocation - Ecosystem Growth. Ecosystem Growth is proposed to replace the existing Multichain Warchest allocation.

**Why This Matters:**

Currently, we are emitting approximately 28,684 CAKE to Farms per day. By reallocating a portion of these emissions, we enhance our capacity to fund other products and initiatives, such as PancakeSwap v4 and other essential parts of our roadmap. Reclassifying Multichain Warchest as Ecosystem Growth will allow us to support initiatives beyond just chain expansions, which are important for our long-term growth.

#### Summary of Proposed Changes

**1. Emission Reduction:**
* Reduce current emissions to Farms by approximately 3,000 CAKE per day (a ~10% reduction), lowering the daily emission from 28,684 CAKE to 25,684 CAKE.
* This reduction will be implemented in two phases of 1,500 CAKE per day each to minimize the impact on APRs across pools and chains. If the proposal is approved, these changes will occur at the end of the upcoming veCAKE epochs, at the Kitchen's discretion.

**2. Ecosystem Growth Allocation:**
* The 3,000 CAKE per day will be redirected, to a new category called **Ecosystem Growth**. This allocation will accumulate over time, serving as a warchest to support various products and initiatives, such as PancakeSwap v4,

====================================================================================================
[72] id=0x3fb72659b13423d9b477a08ccea5528cc5490d5b3114108371eba2ae367ba04f  token=CAKE  space=cakevote.eth  date=2024-11-12
TITLE: Proposal to Relabel Multichain Warchest as Ecosystem Growth
CHOICES: ✅ Yes, we want to future-proof P | ❌ No, we don’t want to future-pr
TEXT (first 1500 characters):
![](https://images2.imgbox.com/7e/fe/0f1Yo3WM_o.png)

#### TLDR
We propose to relabel the current Multichain Warchest allocation as Ecosystem Growth to expand its scope. This allows us to provide incentives for PancakeSwap’s upcoming products and initiatives like PancakeSwap v4, for which we propose to establish a $250,000 Hooks Grant Program and a 0.05 CAKE per block emission program.

**Why This Matters:**

* The current Multichain Warchest, which receives ~0.2 CAKE per block, is solely meant to support PancakeSwap’s efforts in expanding to new chains. 
* While we will continue to do so, there are planned products in the pipeline like PancakeSwap v4 that do not belong to this category, but would still require incentives to kick-start adoption.
* By relabelling it as Ecosystem Growth, incentivizing PancakeSwap v4 becomes possible as it can contribute meaningfully to the protocol’s growth.

#### Summary of Proposed Changes

* **Relabel the current Multichain Warchest allocation as Ecosystem Growth**, allowing the use of its accrued funds and ongoing emissions to grow PancakeSwap’s ecosystem. This includes but is not limited to new products and initiatives like PancakeSwap v4 and expansion to new chains.
* Just like with the Multichain Warchest, **to allow the Kitchen to have flexibility in the implementation and use of funds** within the Ecosystem Growth allocation. We will provide regular reports for the use of funds as detailed below.

#### Transparency and Accountability

====================================================================================================
[73] id=0x79ef496c9737e48d9677a6e291ff2a549dee6729c9996398e453af8ecbf0ceb3  token=CAKE  space=cakevote.eth  date=2025-04-15
TITLE: CAKE Tokenomics Proposal 3.0: True Ownership, Simplified Governance and Sustainable Growth
CHOICES: ✅ Yes, I support this proposal f | ❌ No, I do not support this prop
TEXT (first 1500 characters):
![](https://images2.imgbox.com/35/4d/0uAPK6Ia_o.png)
# Key Highlights of the Tokenomics Proposal:
* **Deflationary Goal:** We aim for a ~4% annual deflation rate and target a ~20% reduction in the CAKE supply by 2030.
* **Retirement of the veCAKE and Gauges Voting System:** The veCAKE and Gauges Voting system will be phased out for a more straightforward and efficient emissions model.
* **Retirement of CAKE Staking:** All staked CAKE will be unlocked immediately, giving users full access to their CAKE without penalties, regardless of the original staking period.
* **Retirement of Revenue Sharing:** Fees previously allocated to revenue sharing through staking from the 0.01% and 0.05% v3 pools will be redirected to the CAKE burn.
* **Reducing Emissions:** Total CAKE emissions per day will be cut from ~40,000 CAKE to 22,500 CAKE, helping to reduce the supply and support deflation.

This proposal aims to streamline the PancakeSwap ecosystem by optimizing CAKE efficiency, enhancing flexibility, and optimizing returns for liquidity providers, all while supporting sustainable growth.
## Proposal to Reinvent PancakeSwap's CAKE Tokenomics
**PancakeSwap must work towards the best interest of CAKE holders and this proposal offers a path forward.**
## When the veCAKE and Gauges Voting system launched, the goals were simple:
* Lock CAKE for the long-term to drive additional benefits to CAKE lockers through bribe revenue
* Bribe revenue is generated by protocols wishing to incentivize liqu

====================================================================================================
[74] id=0xc988547f7b6c435764c840623685b0c2d13ebcc91d1672d39c51b6d14207f9a5  token=CAKE  space=cakevote.eth  date=2026-01-16
TITLE: Proposal to Reduce CAKE Token Max Supply
CHOICES: ✅ Yes, we want to lower CAKE’s max supply | ❌ No, we don't want to lower CAKE’s max supply
TEXT (first 1500 characters):
![](https://images2.imgbox.com/ee/98/OUFXSG3O_o.png)

In April 2025, we passed the [**CAKE Tokenomics Proposal 3.0**](https://pancakeswap.finance/voting/proposal/0x79ef496c9737e48d9677a6e291ff2a549dee6729c9996398e453af8ecbf0ceb3), which retired the veCAKE model and reduced CAKE emissions from ~40,000 to ~22,250 per day. 

Because of this change, we attained a [**net burn of ~8.19%**](https://x.com/PancakeSwap/status/2007044333661507905) of CAKE’s token supply in 2025, reducing it from 380M at the start of the year to ~350M now, maintaining CAKE’s deflationary streak since Sep 2023, with no signs of stopping soon.

Given this, the Kitchen would like to propose reducing CAKE’s max supply from 450M to **400M CAKE**. We believe this is sufficient to sustain all future protocol growth.

While this still leaves ~50M CAKE between the current total supply (~350M) and the new max supply (400M), this is a buffer that we don’t foresee ourselves needing to use, though if extenuating circumstances require, we may still tap on. 

That said, we have been steadily growing our Ecosystem Growth Fund, which currently has accumulated ~3.5M CAKE tokens. This can and will be used for the protocol’s growth needs before any additional emission is even considered. Hence, it is unlikely that the protocol will ever revert to an inflationary state.

#### Adjustment Details:
With the above in mind, we propose the following adjustments to the CAKE max supply:
- **Current Max Supply:** 450,000,000 CAKE
-

====================================================================================================
[75] id=0x05c6b47bcfb5133621c3c1082433713a6cc773255b42fed7f10721fc1d53add3  token=CAKE  space=cakevote.eth  date=2026-02-25
TITLE: Proposal to Retain Stablecoin Fees From Stablecoin Pools
CHOICES: For, please proceed. | Against, do not proceed.
TEXT (first 1500 characters):
![](https://images2.imgbox.com/a5/29/a1cuiZr8_o.png)
### **Background**
Under PancakeSwap’s current revenue flow, protocol fees generated from trading activities across the platform are partially accrued to the Treasury as protocol revenue. Today, all Treasury-bound fees, regardless of their source, are first converted into CAKE.
When the protocol needs to cover operating expenses such as Chefs’ salaries or external service provider fees (typically denominated in USD), the Treasury must then sell CAKE back into stablecoins to meet these obligations.
This workflow introduces two key inefficiencies:
*   **CAKE price volatility** exposes the Treasury to unnecessary market risk when converting assets to meet predictable USD-denominated expenses.
*   **Lack of stablecoin reserves** limits the protocol’s ability to discretionally buy back CAKE during favorable market conditions.
### **Problem Statement**
Converting all protocol revenue into CAKE and later selling a portion back into stablecoins creates:
*   Operational friction
*   Exposure to short-term price volatility
*   Reduced flexibility in Treasury management
This is especially inefficient for fees that are already generated in stablecoins, as it introduces an unnecessary round-trip conversion (stable -> CAKE -> stable).
### **Proposal Overview**
The Kitchen proposes that all Treasury-bound protocol fees arising from major stablecoin pools on PancakeSwap be retained in stablecoins, instead of being converted into CAKE. 
T

====================================================================================================
[76] id=0x7a55c37b49aba6035e24a27dbabb95c83388f7338520e8b78cc07f66702c9451  token=CAKE  space=cakevote.eth  date=2026-06-18
TITLE: Proposal to Redirect Side Product Fee Streams for Treasury Optimization
CHOICES: For, please proceed. | Against, do not proceed.
TEXT (first 1500 characters):
![](https://www.image2url.com/r2/default/images/1781600699737-cd157927-c1be-4ded-a988-f3189b991ee3.jpeg)

## TL;DR

The Kitchen proposes redirecting the fees from PancakeSwap's side products — defined as products other than AMM v2, v3, and Infinity — to the PancakeSwap Treasury, empowering the Kitchen to put them to work for the protocol. If passed, this enables the Kitchen to apply this reallocation to side products within the defined scope.

**To be clear about the scale: side product fees currently represent less than 2% of total protocol fees.**

This is not a change to our deflationary model in any material way. The core burn engine powered by AMM trading fees remains completely unchanged. This is an optimization of where minor streams are allocated: redirecting them from a burn program where they barely register, to Treasury where they can be actively deployed for the long-term benefit of the protocol.

### The Numbers: What This Actually Represents

Protocol fee breakdown (on average, weekly basis):

![Protocol fee breakdown: Swap (AMM v2, v3, Infinity) 98-99% unchanged; Side Products 1-2% to Treasury](https://www.image2url.com/r2/default/images/1781600743340-5aa234df-acca-472c-bb5a-2bd32a150169.png)

For the purposes of this proposal, side products refer to all PancakeSwap products outside of AMM v2, AMM v3, and Infinity. The deflationary engine is powered by spot trading fees across AMM v2, v3, and Infinity; fees from other products together represent less than two p

====================================================================================================
[77] id=0xaf732fcca772bcd33e7a319419008f9d661df61f81c87d0ed3ee973f66003902  token=CGPT  space=chaingptai.eth  date=2025-02-12
TITLE: DAO Proposal: Introduction of New Staking Pools on ChainGPT Pad (14-days & 30-days)
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Introduction:

We proposes the addition of two new staking pools on the ChainGPT Pad platform aimed at providing more accessible and flexible options for our community members and newcomers. These pools will offer shorter staking durations with lower multipliers compared to the longer-term options, allowing users to participate with less commitment while still benefiting from multipliers that encourage staking. The pools will have 0% APY, meaning there will be no immediate token rewards, but instead, users will earn staking multipliers tied to their participation.

## Proposal:

We propose adding the following two new staking pools to ChainGPT Pad:

#### 30-Day Staking Pool
- APY: 0%
- ChainGPT Pad Multiplier: 0.90x
- Duration: 30 days
* Note: 50% of the staking points will reflect on DegenPad

#### 14-Day Staking Pool
- APY: 0%
- Multiplier: 0.45x
- Duration: 14 days
* Note: 50% of the staking points will reflect on DegenPad

### Rationale:
1. Increased Accessibility: These pools provide additional opportunities for users who may not want to commit to longer durations. Newcomers, smaller holders, or those looking for flexibility will find these pools more accessible.
2. Lower Commitment Option: By offering shorter staking durations, we cater to those who want to experience staking without locking up their tokens for extended periods.
3. Maintaining Ecosystem Health: While these pools offer lower multipliers than longer-term pools, they still provide an incentive to stake

====================================================================================================
[78] id=0x52050fcb80efbd02f63e164a5bcbf771d1ed0dd5ff1e960cd10a4713f0feaaa7  token=CGPT  space=chaingptai.eth  date=2025-06-29
TITLE: 🗳️ DAO Proposal: Implement Dynamic FCFS Allocation System on ChainGPT Pad
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Proposal Summary
This proposal suggests replacing the current fixed FCFS (First-Come, First-Served) system with a dynamic, performance-based model. The proposed change will make FCFS more inclusive, by dynamically adjusting users’ allocation based on guaranteed round performance and increasing it over time until the pool sells out. By making this update, also users might actually get higher allocations than they do now (115%) in cases where the pool doesn't sell out (it keeps doubling) and in cases where the pool is slower and has a lot allocation left for FCFS.
---
### Current FCFS Model
- Only users who registered for the pool and qualified are eligible for FCFS. (stays the same)
- Each eligible user receives a fixed 115% additional allocation during the FCFS phase. (we propose to change the fixed FCFS allocation into dynamic FCFS allocation).
---
### The Problem
- For highly anticipated IDOs (e.g., hyped launches, giveaways, or exclusive drops), demand during FCFS is overwhelming.
- As a result, usually only 10–50 users typically manage to buy during FCFS, leaving many participants frustrated and excluded.
---
### The Challenge
- As a launchpad, our goal is to sell out every pool, and fast.
- Reducing FCFS allocation to slow things down would work against that goal.
- Too low of an allocation in FCFS might reduce the excitement from the community and make the participation in FCFS not worth it. 
---
## Proposed Solution: Dynamic FCFS Formula

### We propose a dynamic FC

====================================================================================================
[79] id=0xb63d344342b75da94b7b96254178b86704e5273c65c96d9f84e328c71a0a0750  token=CGPT  space=chaingptai.eth  date=2025-09-28
TITLE: DAO Proposal: Add Subscription Token Sales Format on ChainGPT Pad
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# ChainGPT Pad DAO Proposal: Add Subscription Token Sales Format

### TL;DR
- Add a new Subscription sale format in addition to our current pool types.
- Standard IDOs stay staker‑only with guaranteed allocations (no change).
- In Subscription pools, any KYC’d user can participate, but $CGPT stakers still get an advantage vs non-stakers in the form of a boost. The more they stake the higher the boost.
- Unused USDC in case of over-subscription is refunded to participants.
- Staker boost will range between 1.01x-1.04x for Bronze, 1.10x-1.40x for Silver, 1.25x-2x for Gold, 2x-5x for Diamond. Exact multiplier is to be determined but will be within those ranges. 
----------
## Why add this?
- **More Tier‑1 projects.** Oversub pools drive big “$X committed (×Y)” optics and bring stronger launch partners. This type of marketing generates hype. 
- **More users.** Letting non‑stakers join Subscription pools grows KYC and future demand.
- **Stronger $CGPT utility.** Stakers in all tiers get a visible multiplier that increases their share.
- **Better flywheel.** Bigger crowds → bigger raises → stronger brand → more Tier‑1s → repeat.
----------
## What’s NOT changing
- Standard IDOs remain staker‑only with guaranteed allocations.
- Buzz Campaigns, Launchdrops, Giveaways, Incubation Sales all continue as‑is.
----------
## How Subscription Sales work
1. **KYC + USDC on the sale chain.**
2. **When the window opens, deposit = registration** (one step; no GAP; no FCFS).
3. **Allocation is pr

====================================================================================================
[80] id=0xb84d08d844ddc5e296e3304569a13c64245aa5db509ada0d71d044b0e5efc8b3  token=COMP  space=comp-vote.eth  date=2024-04-11
TITLE: Swap Community ETHW
CHOICES: Swap to ETH | Swap to USDC | Do not Swap
TEXT (first 1500 characters):
In December, the compound community multisig received 186.6k ETHW through a white-hat hack. We've been looking for methods to hand it over to the DAO since the receiving the ETHW; however, since there is limited DEX liquidity and bridging abilities, this has been difficult. Recently, AlphaGrowth has agreed to facilitate the OTC transaction via wintermute.

This proposal seeks guidance from the community on moving forwards with swapping and transferring the ETHW. Given community support, we will swap to either USDC or ETH and pay out a 10% white-hat bounty to Arr00. The remaining 90% of funds will be sent to the Compound DAO multisig.

If the sum of the swap votes is higher than the do not swap votes, we will follow the swap selection with the most votes.

====================================================================================================
[81] id=0x8a022d6b7e3db97c9a0711a64fd4768ed4440ed2503aaa9c253edb4d87a6e56a  token=COMP  space=comp-vote.eth  date=2025-03-25
TITLE: A Growth-Earmarked Treasury Strategy for Compound
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
# Updates since V1
Based on feedback, a number of changes have been made to the proposal since first draft:
**Lowered COMP amount**
* Ask lowered from $5m to $1.5m as a first pilot.
**Focusing Exclusively on the COMP Covered Call Strategy**
* Citing Gauntlet’s concern over working ETH capital, we have removed the ETH strategy and are focusing exclusively on the COMP strategy. 
**Deploy Converted Stablecoins to Support Compound’s Liquidity**
* Using external lending markets may generate higher yields, but the most value-aligned way to deploy stablecoin proceeds is within Compound’s own lending markets to support liquidity supply and foster borrowing activity on COMP.
**Using Yield-Bearing cUSDC for Strategic Buybacks**
* Stablecoin proceeds from the options strategy will be used to buyback COMP price at key levels through cash-secured puts using Compound-deposited, yield-generating cUDSC, as deemed appropriate pending market conditions.
* If a COMP conversion (despite keeping probability reasonably low) occurs from the options strategy, we deposit the USDC into Compound and use the yield-bearing cUSDC as collateral to write put options—earning yield on yield while converting USDC back into COMP at favorable prices—eliminating any potential strategic overlap related to USDC accumulation. 
* To optimize execution, we will use technical market signals to help identify and trigger buyback opportunities systematically, see below for further elaboration.
* The bought-back COMP can t

====================================================================================================
[82] id=0x439e04e2fb564644673a84b082cebfb8c46b0ad149230cd2973c5d074dcd3bdb  token=COMP  space=comp-vote.eth  date=2025-06-18
TITLE: Authorizing the CGWG to Facilitate RFPs
CHOICES: Give CGWG authority to run RFPs | Do NOT give authority | Abstain
TEXT (first 1500 characters):
## Authorizing the CGWG to Facilitate RFPs

Authors: Compound Governance Working Group (CGWG)

## Background

In recent months, members of the Compound DAO have increasingly requested a structured Request for Proposal (RFP) process for evaluating competing initiatives. The Compound Governance WG (CGWG) has stepped in to facilitate several such RFPs on an ad-hoc basis. For example, when multiple teams proposed divergent designs for a Staked COMP mechanism, we helped launch a coordinated RFP to avoid disjointed efforts and conflicting votes for the future vote. Similarly, we organized RFPs to source the best Oracle Extractable Value solution and to evaluate options for a Voting Service Provider. These RFPs allow the DAO to compare proposals side-by-side in one framework instead of handling separate proposals in isolation.

These efforts have been in response to community needs, and we will continue to help facilitate the governance process and discussion for the DAO. Since the authority and process to run governance RFPs have not been formally defined or approved yet by the DAO, the purpose of this vote is to formalize the CGWG’s role in facilitating RFPs via a community-driven process.

## The Need for a Formal RFP Framework

When multiple teams or vendors propose services with overlapping scopes, it can be challenging for delegates to make informed choices if proposals are presented at different times or with varying formats. Without a unified process, the DAO risks fragmente

====================================================================================================
[83] id=0x1d596409a8d530f17c8c7dd9d963873d02fb06cd43612cb987935666fa4bc045  token=COMP  space=comp-vote.eth  date=2025-07-04
TITLE: Voting Service Provider RFP
CHOICES: Aragon Enterprise | Tally Enterprise | Tally Selfserve -Free/Status Quo | Lighthouse Labs | Snapshot Labs
TEXT (first 1500 characters):
**Title:** Compound DAO Voting Service Provider (VSP) Selection

Please go to the respective forum post to see a more in depth breakdown of the process and options.

## Details on the Snapshot Options

### Aragon ([read full proposal here](https://www.comp.xyz/t/request-for-proposal-rfp-compound-dao-voting-service-provider-vsp/6845/15))

#### **Aragon Enterprise**
In order for Compound to effectively transition from its current governance voting interface, and attain a branded UI, the most seamless manner to conduct this shift would be to subscribe to Aragon’s Enterprise tier, even though some of Aragon's stack can be adopted in a self-serve manner.
   
This tier costs $5,000/month for 12 months, totaling $60,000, streamed over the duration of the year-long contract.

The Enterprise tier allows Compound to deploy a fully customized, branded governance frontend integrated with Aragon OSx, their modular DAO operating system. This includes plugin support for advanced governance mechanics such as optimistic governance, permissioned parameter adjustments, and diverse decision-making flows. The Compound-specific frontend would offer a tailored user experience, mirroring the DAO’s current structure, enabling proposal creation, voting, and tracking.

In addition to the UI layer, Aragon commits to maintaining 99.9% frontend uptime and guarantees a 24-hour response time for critical issues that affect the DAO’s governance operations. The team also offers a detailed offboarding pathway

====================================================================================================
[84] id=0xc6199e1868681bdd32b508fb059c1520101080b4a6d1b2b3234b2619e3647849  token=COMP  space=comp-vote.eth  date=2026-08-18
TITLE: Treasury Management Program USDC Allocation
CHOICES: Support as Proposed | Suggest Changes | Abstain
TEXT (first 1500 characters):
### Treasury Management Program USDC Allocation

The Treasury Management Committee (TMC) has concluded its manager selection process and is now seeking a sentiment check from delegates via this Snapshot vote. These proposed allocations are relegated to the DAO’s USDC and are intended for allocation across a Primary Allocation Sleeve (onchain-heavy) and an RWA Sleeve. 

The RWA Sleeve puts $4M of the DAO's USDC into two tokenized positions held directly in the DAO's escrow: $1M in USTB and $3M in CUSHY.
* [Full RWA Sleeve Recommendation Memorandum accessible here.](https://www.comp.xyz/t/treasury-management-program-rwa-sleeve-allocation/8001)

The Primary Allocation Sleeve places up to ~$12M with Steakhouse Financial as curator of a dedicated, single-chain noncustodial vault on Ethereum, with flexibility around allocation amount depending on accessible capital and revenue. The DAO holds the position and retains guardian rights, the fee is 0.5% of NAV with no performance fee and no lockup, and the mandate is terminable on 30 days' notice. The book is entirely onchain, holds no tokenized RWAs at launch, and runs an indicative 35/45/15/5 split across prime repo, high-yield repo, term, and turbo strategies. 
* [Full Primary Manager Recommendation Memorandum accessible here.](https://www.comp.xyz/t/treasury-management-program-primary-allocation/8020)

Both memos set out how each manager and position was selected, what the vaults can and cannot do, how each sleeve earns its return,

====================================================================================================
[85] id=0xace71f6d52247f26fc776734fa735d85ff44674eba9f2c25af217c43c390c582  token=COW  space=cow.eth  date=2024-11-29
TITLE: CIP-55: Slashing of the GlueX Protocol solver and the CoW DAO bonding pool
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 55
title: Slashing of the GlueX Protocol solver and the CoW DAO bonding pool
author: Chris (c3rnst), Haris Angelidakis
status: active
created: 2024-11-22
```

# Simple summary

This CIP proposes the slashing of the CoW DAO bonding pool, which has vouched for the GlueX solver, as GlueX was involved in an incident on November 7, 2024 that resulted in a financial loss of $76,783 (equivalent) for the settlement contract.

No user funds were at risk, and no user allowances needed or need to be revoked. The GlueX solver has already refunded the bonding pool, and is operational again. The slashing is a procedural step to transfer the funds from CoW DAO’s bonding pool to CoW DAO's withdraw Safe (i.e., the safe where all balances accumulated in the settlement contract are withdrawn to).

# Background

The incident occurred due to a vulnerability in the GlueX solver’s deployment. Specifically, an allowance set on a flawed smart contract enabled malicious actors to drain funds from CoW DAO’s settlement contract. It is essential to clarify that the settlement contract never stores user funds; it only temporarily holds (a) Network (gas) fees and (b) Protocol fees collected by solvers.

These funds are regularly withdrawn (recently changed to daily withdrawals) and used for solver payouts and fee distribution.

# Incident Summary

1. Deployment of Vulnerable Contract: GlueX deployed a new settlement handler contract to execute winning solutions and set allowances for several token

====================================================================================================
[86] id=0x46d4fea1492207cf400fcb7a01141a7d4c730791d658cc77236941fc9eb7dccb  token=COW  space=cow.eth  date=2024-12-10
TITLE: CIP-57: Solver rewards on all chains
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 57
title: Solver rewards on all chains
author: Haris Angelidakis, Andrea Canidio, Felix Henneke, Bram van den Berg
status: active
created:  2024-11-11
```

# Simple Summary

CoW Protocol is currently operating on Ethereum mainnet, Gnosis Chain and Arbitrum One, and with its state-of-the-art solver competition, users on these chains are provided with a great quality of service. A key driving force behind the evolution of the solver competition has been the solver rewards program that is currently live on mainnet, with the latest specifications described in CIP-36, CIP-38 and CIP-44.

Since the program has worked very well on mainnet, we propose to extend it to the rest of the chains the protocol is operating, namely Gnosis Chain and Arbitrum. This would allow existing solvers to further improve on each of these chains, and moreover, it would incentivize new solvers that are potentially specialized in certain chains and do not necessarily (want to) participate in the mainnet competition to join any non-mainnet competition without having to worry that there are no rewards allocated for them. Ultimately, the protocol will benefit as this would establish very strong competition on a per chain basis.

Specifically, we propose to use the same rewards mechanism that has already worked very well on mainnet, with the only adaptation being the caps, that will become chain-dependent, and will always be denominated in the native currency of each chain.

Moreover, and given that b

====================================================================================================
[87] id=0x511329756e1c208f45a5008f63fdede8309de4bac7a3072aa5ad7d852fa0041e  token=COW  space=cow.eth  date=2024-12-18
TITLE: CIP-59: Funding for Marketing & Business Development Services - Service Agreement
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 59
title: Funding for Marketing & Business Development Services - Service Agreement
author: chim9
status: active
created: 2024-12-11
```

# Simple Summary

This is a truncated version due to snapshot character limitations. Please refer to the forum post for the full version of the CIP.

This CoW Improvement Proposal (“CIP”) requests the DAO to approve the allocation of funds to secure comprehensive business development and marketing services for CoW DAO, delivered by Defou S.A., an external Service Provider (the “Service Provider”) for the execution of the Services under the terms of the Service Agreement hereunder (the “Agreement”). The compensation will cover the Service Provider’s labor and expenses on a per-use basis for the period from 1 January 2025 to 31 December 2025 (the “Term”).

The Service Provider will be responsible for market analysis, brand positioning, campaign creation and execution, and developing an ecosystem of partnerships. This will boost CoW DAO’s brands and products visibility, customer engagement, and long-term growth in the decentralized finance ecosystem.

# Motivation

To achieve the vision of a decentralized future where digital assets are traded fairly, efficiently, and reliably, CoW DAO requires a strategic approach to business development and marketing. By partnering with an expert Service Provider, this CIP ensures that CoW DAO will leverage tailored strategies aligned with the DAO’s values to expand brand awareness, strengthen partn

====================================================================================================
[88] id=0xbafee087f3a1d5757e44a72fa76e8624ce212623153816a936a8888741485ef5  token=COW  space=cow.eth  date=2025-01-22
TITLE: CIP-61: price-improvement-share, Revenue-share and Fees on CoW Protocol
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
Authors: Core team
Created: 2025-01-10
```
*This is a truncated version. Please refer to the Forum post for the full version incl. "Results over the testing period"*

### Simple Summary
This CIP proposes to implement a specific method going forward, with the finalization of the revenue model experimentation. The main objective is to continue with price-improvement-sharing as the primary revenue model, while retaining the option to introduce new (price-improvement-share/fee) strategies for testing. If successfully passed, this proposal will take effect starting 1 February 2025.

Additionally, the CIP introduces options for partners to apply fees on trades attributed to their user flow, alongside a revenue-sharing model for CoW DAO. Assuming this proposal is accepted, at any time, CoW DAO can amend these revenue models (price-improvement-sharing, revenue-sharing, and fee structures) through a new proposal.

### Motivation
This proposal aligns with the conclusion of the mandate set by CIP-34 “Testing Fee Models for CoW Protocol”, along with its extension via CIP-49.

CoW DAO aims to ensure financial self-sustainability for CoW Protocol, removing reliance on external funding for growth and development. While fees and price-improvement-sharing generate revenue, profitability occurs only when revenue exceeds expenses (e.g., development costs, ecosystem grants, solver rewards).

In 2024, CoW Protocol generated approximately $6M USD through price-improvement-sharing, revenue-shar

====================================================================================================
[89] id=0xdf9c7d3c8964de744c6bf99a89f60833e8904953bbe3e1c6856eb59939f82a2f  token=COW  space=cow.eth  date=2025-01-29
TITLE: CIP-62: Core Treasury team mandate and funding
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
### Simple Summary

This CIP proposes to consolidate several existing mandates of the Core Treasury team, originally established by [CIP-19 (karpatkey Proposal to Create a Core Treasury Team)](https://snapshot.box/#/s:cow.eth/proposal/0xc4e9c0a28f12b28aedfc8c3802522a9ac9dd1c7d5045dca94abf555ca2d8cd31) and to request an allocation of 80 million COW tokens to empower the team and karpatkey to pursue additional liquidity provisioning, economic opportunities for the treasury tokens, and funding opportunities for the development and execution of CoW DAO product roadmap over the next 4 years (2025-2028).

The goal of this CIP is to strategically allocate COW in connection with long-term partners. The Core Treasury team will enact its best judgement on re-allocating COW between different initiatives in order to maximise the funds generated for CoW DAO’s products.

At the time of writing, we are requesting 80 million COW tokens from the [DAO’s currently owned COW tokens](https://app.safe.global/balances?safe=eth:0xcA771eda0c70aA7d053aB1B25004559B918FE662).

### Motivation

CoW DAO’s products have been revolutionising DeFi and protecting users from MEV since 2022, when the project spun out from GnosisDAO. Since then, CoW Swap & CoW Protocol have facilitated more than $70.8 billion in trading volume, more than $187 billion of value has been protected by MEV Blocker and more than $27 million of volume has been supercharged by CoW AMM’s features.

CoW Swap currently stands as the #1 UI f

====================================================================================================
[90] id=0x93b57204df8a33567da01a935686121d69d1443ef2189da45cfb011efc17fcae  token=COW  space=cow.eth  date=2025-01-30
TITLE: CIP-63: Renewing the CoW Grants Program
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 63
title: Renewing the CoW Grants Program
author: @Chim9, @Kubesqrt, @middleway.eth, @notsoformal, @mfw78, @c3rnst, @Master_CoW
status: Active
created: 2025-01-21
```

## Simple Summary

With the passing of this CIP, the mandate for Grants DAO continues for the period of 1st February 2025 through and including 31st January 2026.

For this period, the proposal requests an additional 383,000 xDAI from the Treasury held funds. With this additional funding, the available funds at the discretion of the Grant Committee to give out for funds in 2025 is 600,000 xDAI and 1,465,260 COW for Grant activities and 4,990,000 COW for volume grants.

The use of grants in the CoW ecosystem is a critical driver for fostering innovation and growth. Grants not only incentivize builders to develop on top of CoW but also encourage the creation of impactful products that align with the ecosystem’s goals. Since the inception of the Grants DAO, the initiative has successfully onboarded several impactful projects that have significantly advanced the CoW ecosystem, contributing positively to its expansion and overall utility.

# Motivation

The CoW Grants Program has funded numerous impactful projects contributing to the CoW ecosystem. For a full list and details on their contributions, please refer to the forum [post](https://forum.cow.fi/t/cip-draft-renewing-the-cow-grants-program/2771).

# Grant program financial position

![financial.png](ipfs://bafkreibpep3htrulwaeijzdnrnw3fqqk2uafx2rlvvce

====================================================================================================
[91] id=0x7bdf94cd8688a9baed7df2599ede5aaca6d931353d2765bb71519d97e478db80  token=COW  space=cow.eth  date=2025-03-07
TITLE: CIP-64: Incorporation of a legal structure for CoW DAO
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This CIP is shortened due to character limits. Full version pinned to IPFS, CID: bafkreiepdqfd7hblxbw6undnqon7onhvsj2ow7as5ws5fey7ucshxxsi4m 

### Summary
This proposal establishes a 4-entity legal structure for CoW DAO by incorporating a Cayman Islands Foundation and 3 BVI companies: CoW Core, CoW Hosting and CoW Business. 
With the successful passing of this CIP, the Service Providers will receive the mandate and community instructions for the incorporation of the below legal structure, on behalf of CoW DAO, with the mandates and split of activities set out below. 

## Legal Structure

### CoW DAO (unwrapped)
  * Governance + Delegation: CoW DAO sets strategic direction and approves mandates that are transmitted to the affiliated entities. The governance systems and settings, and Delegation Program remain unincorporated.
  * Settlement Contract & Tokenomics: CoW DAO’s settlement contract and tokenomics framework remain out of the scope of the legal structure.
  * CoW DAO’s MultiSig: CoW DAO remains exclusive owner of the COW token supply. The signer structure remains unaltered and unwrapped.

CHANGES
* Governance will remain in place, unaltered
* Through the incorporation documents, CoW DAO (unwrapped) will remain the ultimate decision maker of the legal structure - including the authority to direct, modify, or dissolve affiliated entities
* CoW DAO grants power to “Delegated Committees” that in turn will be mandated by the legal entities to perform the functions and assign

====================================================================================================
[92] id=0xf9ecb08c4738f04c4525373d6b78085d16635f86adacd1b8ea77b2c176c99d32  token=COW  space=cow.eth  date=2025-05-08
TITLE: CIP-67: Switching to the Fair Combinatorial Auction
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 67
title: Switching to the Fair Combinatorial Auction
author: Haris Angelidakis, Andrea Canidio, Felix Henneke, Bram van den Berg
status: Active
created: 2025-04-17
```
# Simple Summary
We propose to change CoW Protocol’s auction mechanism from the current batch auction to the fair combinatorial auction (described in [this research paper](https://arxiv.org/abs/2408.12225) and [forum post](https://forum.cow.fi/t/research-beyond-batch-auctions/2543)). The goal is to increase the protocol throughput and provide stronger fairness guarantees to traders. Changing the auction mechanism also requires changing the calculations of solvers’ rewards and penalties (see [here](https://forum.cow.fi/t/combinatorial-auctions-from-theory-to-practice-via-some-more-theory-about-rewards/2877) for an in-depth discussion). At the same time, like the batch auction, the fair combinatorial auction can guarantee uniform directional clearing prices (as defined in [CIP-38](https://forum.cow.fi/t/cip-38-solver-computed-fees-rank-by-surplus/2061)): if two traders trade the same tokens in the same direction in the same auction, they will receive the same price.

# Motivation
By allowing trades to be executed together, batch auctions deliver additional efficiencies and price improvement relative to alternatives such as Dutch auctions. However, batch auctions also have limitations that are becoming more and more evident as CoW Protocol grows. By forcing a single winner per auction, a batch auction ma

====================================================================================================
[93] id=0x041d03e803edf12a8e4429b1955987759a5b81a5fccbddb155128ae3e4f49027  token=COW  space=cow.eth  date=2025-06-11
TITLE: CIP-68: Distributing COW rewards on mainnet for all chains
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 68
title: Distributing COW rewards on mainnet for all chains 
author: @harisang , @notsoformal and Core Team
status: Active
created: 2025-06-03
```

# Simple summary

With [CIP-57](https://snapshot.box/#/s:cow.eth/proposal/0x46d4fea1492207cf400fcb7a01141a7d4c730791d658cc77236941fc9eb7dccb), CoW DAO has decided that COW rewards must be distributed as part of the rewards mechanism of the solver competition in each chain the protocol operates. As the protocol is aiming to expand on more chains, technical issues might arise around the bridging of the COW token to the respective chain.

To resolve this, we propose that COW rewards, awarded to solvers in any of the chains the protocol is active, will be distributed only on mainnet. This will allow both the DAO and the solvers to manage COW inventory more easily and uniformly.

Regarding protocol fees, which are intended to be paid back in COW, [CIP-38](https://snapshot.box/#/s:cow.eth/proposal/0xfb81daea9be89f4f1c251d53fd9d1481129b97c6f38caaddc42af7f3ce5a52ec) provides the flexibility to solvers to pay back the protocol in COW or in ETH. If the protocol fee is collected in ETH, or more precisely, the native currency of the chain, we propose that this amount is bridged to mainnet and converted into COW on mainnet.

# Motivation

The rewards mechanism with its COW rewards has proved instrumental in helping the protocol establish a very strong competition among solvers. As the DAO aims to activate the same rewards mechanism i

====================================================================================================
[94] id=0x0c70c8cd92accee872b52614b4fa10e3e3214f45c5b6857f7e88e910607a3c1d  token=COW  space=cow.eth  date=2025-11-06
TITLE: CIP-74:Align Solver Rewards with Protocol Revenue and introduce a volume based fee
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Simple Summary
CoW Protocol’s current second-price auction uses a fixed reward cap, which suppresses solver rewards on high-value batches and lets rewards exceed protocol fees on low-fee batches (especially on L2s). This CIP replaces the fixed cap with a dynamic cap tied to protocol fees generated by the winning solution, and introduces a very small unconditional volume fee of 2 bps (0.02%).

The goal of this CIP is to change the reward mechanism in a way that aligns incentives of solvers and the protocol to ensure economic viability even under adversarial or long tail order flow conditions.

# Motivation
CoW Protocol currently uses a second-price auction mechanism for solver rewards, with a fixed reward cap. The winning solver’s reward is determined by the difference between their solution’s score and the next-best solution’s score (the “second-price”), and this reward is capped at an upper bound (for example, ~0.012 ETH on mainnet).

Since surplus and protocol fees tend to follow a fat-tailed distribution (few trades contribute most of the value) we observe cases in which the protocol profits significantly from fees (price improvement or surplus fees) while the upside of solvers that provided a very good solution are capped at a fairly low amount. On the other hand, we also observe a lot of batches (especially on L2s) in which the protocol doesn’t earn sufficient protocol fee to cover the solver rewards.

The goal of this CIP is to align incentives between the protocol an

====================================================================================================
[95] id=0x64f3649a6eeab2ac1326d704c3ddaf04f0229a3d4605708deff04f4cba7ccd46  token=COW  space=cow.eth  date=2025-11-19
TITLE: CIP-75: Partner Incentive Alignment - Partner Fee, Partner Price Improvement Share and Increased Cap on Partner’s Maximum Aggregate Revenue Share.
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
title: CIP-75: Partner Incentive Alignment - Partner Fee, Partner Price Improvement Share and increased cap on Partner’s maximum aggregate revenue share.
author: @Kowrigan
status: Active
created: 2025-11-11
```

## Simple Summary

This CIP aims at amending [CIP-61](https://snapshot.box/#/s:cow.eth/proposal/0xbafee087f3a1d5757e44a72fa76e8624ce212623153816a936a8888741485ef5) by (i) introducing a Partner Share of the Price Improvement on attributed orders, (ii) allowing partners to combine the Partner Fee and the Partner Share of the Price Improvement, (iii) raising the cap of the Partner maximum aggregate revenue share from its current 1% to 5%. Other provisions of CIP-61 remain unchanged, and (iv) increase the default revenue share on volume based partner fees for the benefit of the partners from 50/50 to 25/75.

## Motivation

This amendment aligns incentives by granting integrators a direct, capped share of the Price Improvement mirroring the DAO Price Improvement Share and greater flexibility to monetise their flows by increasing the Partner’s maximum aggregate revenue share and explicitly allowing them to combine their share of Price Improvement and the app-level volume based Partner Fee.

While the philosophy of protecting users by implementing a cap above which the partner is prevented from exploiting users by charging a 100% volume fee remains a guiding principle, this CIP is driven by recent discussions with potential integrators, which indicate that there is a str

====================================================================================================
[96] id=0xffc1affd1b4a75cc917b9880768b7eb23bd07e77677cc8ac60bbfcf2bd919335  token=COW  space=cow.eth  date=2025-12-15
TITLE: CIP-80: CoW DAO Grants 2026 Renewal
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 80
title: CoW DAO Grants 2026 Renewal
author: @Sov, @mfw78, @Chim9, @middleway.eth, @notsoformal, @Master_CoW
status: Active
created: 2025-11-26
```
---

## Simple Summary

The 2026 CoW DAO Grants Program renewal builds on the foundation established in [CIP-63](https://forum.cow.fi/t/cip-63-renewing-the-cow-grants-program/2771) while refining focus toward strategic growth. Rather than repeating governance documentation from the previous proposal, this renewal demonstrates how the program has evolved from establishing processes to executing on priorities.

**Previous Renewal Reference:** [CIP-63: Renewing the CoW Grants Program](https://forum.cow.fi/t/cip-63-renewing-the-cow-grants-program/2771)

---

## Overview

The 2026 renewal reflects an evolution of the CoW Grants Program. Governance frameworks, operational safeguards, and termination procedures established under CIP-63 remain fully in effect. This proposal focuses on execution, capital efficiency, and strategic alignment with protocol priorities identified through sustained collaboration with the core team.

---

## Budget Evolution

CIP-63 allocated **600,000 xDAI** and **1,465,260 COW** for general grants, along with **4,990,000 COW** reserved for volume incentives.

For 2026, the budget request is grounded in the actual Q4 2025 deployment rate rather than projected growth. Any unused 2025 funds roll forward transparently.

As of today, the Grants Safe holds:

* **271,319 xDAI**
* **6,680,618 COW**

Confirmed

====================================================================================================
[97] id=0xe84793f122f1c9faa2bb9194faf71567ffd236df616bd60c300eead541f25304  token=COW  space=cow.eth  date=2026-01-08
TITLE: CIP-82: CoW DAO Grants 2026 Renewal
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP: 82
title: CoW DAO Grants 2026 Renewal
author: @Sov, @mfw78, @Chim9, @middleway.eth, @notsoformal, @Master_CoW
status: Active
created: 2025-11-26
```
---

## Simple Summary

This proposal was previously voted on as CIP-80 ([link to original proposal](https://snapshot.box/#/s:cow.eth/proposal/0xffc1affd1b4a75cc917b9880768b7eb23bd07e77677cc8ac60bbfcf2bd919335)). We believe it did not reach quorum due to low voter participation, likely impacted by the timing of the vote just before the holidays. Despite this, the proposal did not receive any significant opposition or suggestions for modification. As a result, we are bringing this proposal back for another voting round.

The 2026 CoW DAO Grants Program renewal builds on the foundation established in [CIP-63](https://forum.cow.fi/t/cip-63-renewing-the-cow-grants-program/2771) while refining focus toward strategic growth. Rather than repeating governance documentation from the previous proposal, this renewal demonstrates how the program has evolved from establishing processes to executing on priorities.

**Previous Renewal Reference:** [CIP-63: Renewing the CoW Grants Program](https://forum.cow.fi/t/cip-63-renewing-the-cow-grants-program/2771)

---

## Overview

The 2026 renewal reflects an evolution of the CoW Grants Program. Governance frameworks, operational safeguards, and termination procedures established under CIP-63 remain fully in effect. This proposal focuses on execution, capital efficiency, and strategic alignme

====================================================================================================
[98] id=0x52407329d3861f0e263eacc3ad98f0b1c29b3cd5513c26846f9aad11005f8e8b  token=COW  space=cow.eth  date=2026-01-26
TITLE: CIP-83: Renewing Team Grant Allocation with Performance-Linked Milestones
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Simple Summary

This proposal asks COW DAO to:

* Replenish the CoW Team Grant Allocation with a base of 5% of the total COW supply (50,000,000 COW) via a four-year linear streaming allocation from the DAO treasury.
* Establish a Performance-Based Incentive Tier of up to an additional 10% of total COW supply (100,000,000 COW), unlocked in four equal tranches (2.5% each) upon reaching specific protocol revenue milestones using either USD or ETH-denominated revenue targets
* Implement a Valuation Cap on performance rewards, ensuring each milestone reward is capped at a maximum value of $25,000,000 USD to protect the DAO in high-growth "bull market" scenarios.

If all milestones are reached, the incentive capacity equals 15% total (150,000,000 COW); if growth stalls, the program remains limited to 5% (50,000,000 COW).

## Motivation

CoW DAO’s initial team allocation (15% at TGE) has been highly effective, growing the team from 22 to 46 members. However, as initial 4-year grants vest by February 2026, the available pool is nearly exhausted (~2.5% remaining).

While the previous CIP-76 was rejected due to concerns over dilution and a lack of market-linked incentives, this revised proposal creates a direct link between contributor rewards and protocol success. By shifting a significant portion of the requested allocation to KPI-based triggers, we align the team’s upside with the DAO’s revenue growth, while the dollar-value cap addresses concerns regarding excessive payouts duri

====================================================================================================
[99] id=0xb488c343df3ba5f3857a4c7a920a74e18c13a2cdce99d27af34216803da6abff  token=COW  space=cow.eth  date=2026-03-30
TITLE: CIP-85:  Performance and Consistency Rewards
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
```
CIP-Number: 85
title: Performance and Consistency Rewards
author: @felixhenneke, @harisang
status: active
created: 2026-02-26
```

# Simple Summary

This CIP adapts the rewards mechanism to encourage solvers to provide a consistent service. This is realized by fixing the budget for rewards to a fixed percent of protocol revenue, where one part of this budget is spent on rewards in their current form, while the remaining part is distributed based on metrics related to consistent participation. The CIP also gives a mandate to the core team to experiment with different metrics for distributing rewards for consistency.

# Motivation

The current reward mechanism, akin to a second-price auction, which we will refer to as performance rewards, is designed to encourage solvers to innovate on providing better prices to users. One thing performance rewards do not sufficiently encourage is providing a consistent service or broad coverage of token pairs and small volume buckets. For example, settling a trade with small volume is minimally (or no longer) profitable, as [CIP-74](https://snapshot.box/#/s:cow.eth/proposal/0x0c70c8cd92accee872b52614b4fa10e3e3214f45c5b6857f7e88e910607a3c1d) effectively removed cross-auction subsidies for orders which are difficult to monetize. This can result in solvers focusing on large orders and specializing on a niche. Coming second in the competition is also not tied to any reward, which shows that robustness through participation is not encouraged.

====================================================================================================
[100] id=0x0b4b1fd167f5423008cfdefedfd3249c99e7e41ebb0bc9ec47fef9ee47788493  token=COW  space=cow.eth  date=2026-04-30
TITLE: CIP-86: Discretionary grants program for victims of the cow.fi domain hijacking
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**SIMPLE SUMMARY**

This CIP proposes the creation of a discretionary grants program to provide support to victims of the cow.fi domain hijacking of April 14, 2026. It also specifies criteria for submitting and verifying claims, as well as a timeline for opening and closing the discretionary grants program.

**MOTIVATION**

As documented in the [CoW.fi Domain Hijack Post-Mortem](https://x.com/CoWSwap/status/2044924940886163780), the domain registrar (Gandi SAS) used by CoW Swap’s DNS holder (AWS Route 53) was exploited on April 14, 2026, in a social engineering attack that gave hackers control of the cow.fi domain for approximately 4.5 hours. During this time, hackers were able to serve a “phishing” website that tricked cow.fi visitors into signing malicious transactions that drained tokens from their wallets. The core team estimates that approximately 1.2M USDC worth of user funds were taken from users as a result of this incident.

Despite the fact that CoW Swap was not hacked and was in no way responsible for the security failures that led to the success of the attack on its domain registrar, we take our relationship with our users seriously, and we recognize that these relationships are built on trust. Therefore, we believe it is right and proper to do what we can to assist CoW Swap users that lost funds during the aforementioned incident.

**SPECIFICATION**

To help users recover their funds, the core team is asking for a mandate from the DAO to pursue, where necessary,

====================================================================================================
[101] id=QmbLJyafmXeToA3zGJYJ8D2VeMFvb2DTZxfVnqjGXVmQju  token=CRV  space=curve.eth  date=2021-08-01
TITLE: Propose an AAVE x CURVE Alliance
CHOICES: I support the Aave x Curve swap  | I don't support the swap
TEXT (first 1500 characters):
**Summary**: 

Aave and Curve are two of the main DeFi protocols in constant evolution and growth with synergies between. One way of increasing these synergies would be to give each protocol some voting power in the other governance.

A few weeks ago, an Aave proposal was posted about a Curve strategy to increase the revenues earned by Aave DAO. However, to benefit from the Curve system in the most efficient way, it requires to lock CRV.

**Abstract**:
 
Aave DAO is accumulating some CRV with the ecosystem collector, but not enough to boost the treasury from the ecosystem collector considering it’s now around 12.9M$ (or 851.2M$ including the ecosystem reserve). So how could Aave DAO get more CRV?

* Buy CRV using part of the funds from the ecosystem collector, but this would require approximately 1M$ to get the maximum boost on the Curve pools.
* Propose a token exchange between AAVE and CRV that increase the synergies created between both communities over the last year.

**Motivation**:

I would like to support the second option, especially because it would allow both communities to diversify their treasury without selling either Aave & Crv or spending additional stablecoins for this deal.

**Treasury state:**

CURVE:

Curve DAO mostly hold $CRV with 123.9M tokens worth 216M$.  There is probably other addresses with stablecoins & other tokens, but I couldn’t find it.

AAVE:

* Stablecoins: 1.22% of the DAO treasury worth 10.35M$
* Ecosystem Reserve: 98.48% of the DAO treasur

====================================================================================================
[102] id=QmVc2zGmoyD8kKtvLHjxUQNu8m2am3pvzEURV4GRcjjpEq  token=CRV  space=curve.eth  date=2021-09-19
TITLE: Launch Curve on Harmony
CHOICES: Yes | No
TEXT (first 1500 characters):
Summary:

Harmony is proposing to work with the Curve to deploy Curve on the Harmony blockchain. This will expand stablecoin swap to its community of users and provide incentives to bootstrap the launch of Curve to a new ecosystem.

Abstract:

Our proposal is to support Curve as it continues to expand in the coming multi-chain world. Harmony is an open and fast blockchain that is fully Ethereum compatible with 2-second transaction finality and near-zero fees.

Harmony invites the Curve community to support this launch. Harmony will provide $2 million in incentives in ONE tokens to bootstrap initial usage of Curve on Harmony. We also propose the Curve community to contribute CRV tokens to add incentives to the launch.

In addition to token incentives, we will be investing heavily in co-marketing and educating users through tutorials, videos, and community-led support.

Harmony is a sharded proof-of-stake blockchain. It has processed more than 93 million transactions on mainnet 4 and it is fully EVM and Ethereum tooling compatible. Our secure bridges offer cross-chain asset transfers with Ethereum and Binance Smart Chain.

Motivation:

Curve is ready to go multi-chain and we want to help bring it to the Harmony ecosystem, which is growing with the launch of Sushi on Harmony and other DeFi projects.

A unique feature of Harmony is our bridges to Ethereum and Binance Smart Chain which are bringing in stablecoins and pegged assets from both ecosystems, i.e. ethBUSD-bscBUSD. This c

====================================================================================================
[103] id=0x2fa58b3fb9a28b628c46e8f9376353ec588f61726fadf9a5c56ef8db067215e6  token=CRV  space=curve.eth  date=2021-11-17
TITLE: 2024 $CRV Price Prediction 2024 $CRV价格预测
CHOICES: 能 YES | 不能 NO
TEXT (first 1500 characters):
$CRV 2024年价格能够超过100美元吗？
Can $CRV price pass $100 in 2024?

====================================================================================================
[104] id=0x342ae8487532442d903bbec0cdbe978005957b3ae667dcac878d38a9cf0295d9  token=CRV  space=curve.eth  date=2021-11-20
TITLE: Curve是否应该增加流动资金池？除了已经增加的Compound、USDT、Y、Pax、Ren、BUSD、sUSD、hbrc、sbtc和3pool。
CHOICES: 是 | 否
TEXT (first 1500 characters):


====================================================================================================
[105] id=0x15fae2fb5f07ef6b94db2496a5a26ba8cd331a0460365b15a648eac2726c1d11  token=CRV  space=curve.eth  date=2021-11-20
TITLE: Should Curve burn some CRVs?
CHOICES: Yes | Yes | Yes | No
TEXT (first 1500 characters):
Curve should burn harf of total volume.

====================================================================================================
[106] id=0xad25c0c52f407ba512d965db98f76e2514f4892fdb6325b88cc421dd39f04446  token=CRV  space=curve.eth  date=2021-11-23
TITLE: Should Curve DAO start buying up YFI
CHOICES: yes | no
TEXT (first 1500 characters):
Should the DAO start buying up YFI tokens in anticipation of the YFI tokenomics restructure?

====================================================================================================
[107] id=0xf039dc06a2506a6d70d531e9ea46ff5188d92d90f1f4c0145e0e75e8997a3591  token=CRV  space=curve.eth  date=2021-12-01
TITLE: Do you think Curve should adjust its total supply of tokens?
CHOICES: YES | NO
TEXT (first 1500 characters):


====================================================================================================
[108] id=0x5ba2a218857b24f31e265342d163fe995259b48aaac4457cfdab6798f2301c6b  token=CRV  space=curve.eth  date=2021-12-09
TITLE: CRV占你的仓位比例有多少？
CHOICES: >80% | 50%-80% | 30%-50% | 10%-30% | <10%
TEXT (first 1500 characters):


====================================================================================================
[109] id=0x7e50caa67544f4d0d0a4e6a0254d1a493cba879940b24eeaf5d45a0807a241d2  token=CRV  space=curve.eth  date=2021-12-10
TITLE: test
CHOICES: hi | test | test
TEXT (first 1500 characters):
test
## test

====================================================================================================
[110] id=0x4e54b479e0fd9f12202fd1f7b316ba73805a8f5654573c4625f5929c72edef6f  token=CRV  space=curve.eth  date=2021-12-22
TITLE: Grant funding for mutual growth in GameFi and Metaverse
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
For whom it may concern,

I am writing here regarding a marketing offer proposal. I am Marin and I am the content writer for GameFi Corner and have partnered up with a good friend of mine who has experience in marketing and e-commerce.

GameFi Corner is a newsletter exclusively aimed at blockchain gaming and metaverse. We handpick the most up to date information and create content that is suitable and engaging to read.

Our goal is to make GameFi a better place by making it accessible and educate everyone who is interested to make more informed decisions. We also want to collaborate with sponsors who believe in our development and positive future outcomes for everyone including the community, sponsors who partner up with us and GameFi Corner itself.

We see success when partnerships can truly benefit from one another like an interconnected chain. One provides with the sponsor, funding and in return we will contribute all our specific GameFi knowledge through extensive research and investment in paid advertisements so we can create traffic for both Curve Finance and GameFi Corner.

We will measure our success by analysing on how many users have clicked on your link / banner we will include in our texts. The more subscribers we can bring thanks to your potential funding, the more successful we will both become. Of course we are open to hear also other proposals on how we can benefit together.

We have just started writing for 1 month and collected more than 150 organic subscrib

====================================================================================================
[111] id=0x9eac55a31962e3fb452c926f410efc30e84c010bb98728d93264e3f676dccbf0  token=CTSI  space=cartesi.eth  date=2023-04-11
TITLE: New grant: Developing a decentralized painting canvas on Cartesi Rollups
CHOICES: Yes, fund this. | No, do not fund this.
TEXT (first 1500 characters):
This grant proposal is in response to Cartesi's own RFP. The vote is whether to fund this team to complete the project.

See the full proposal here:
https://governance.cartesi.io/t/in-response-to-rfp-for-developing-a-decentralized-painting-canvas-on-cartesi-rollups/80

====================================================================================================
[112] id=0xd2a6316dfccb081f70e781c752430912ccb2a596fbb4a133e5caf1086a69359f  token=CTSI  space=cartesi.eth  date=2023-06-07
TITLE: CGP Grant proposal- Tooling: Drand for Cartesi
CHOICES: Yes, fund this proposal. | No, do not fund this proposal.
TEXT (first 1500 characters):
Cartesi PRNG

This project is a component of a larger set of tools for generating random numbers on Cartesi’s convenience layer.

Find the full proposal here: https://governance.cartesi.io/t/tooling-drand-for-cartesi/127/1

====================================================================================================
[113] id=0xcd1159b7a49540b4402e97a0bce1099955dd314b8e116a3f0918828c689008c0  token=CTSI  space=cartesi.eth  date=2023-07-14
TITLE: CGP grant proposal: Cartenix: Run Nix inside Cartesi
CHOICES: Yes, fund this project | No, do not fund this project
TEXT (first 1500 characters):
Cartenix: a Proof of concept allowing you to run Nix inside the Cartesi virtual machine leveraging its determinism to accomplish complete reproducibility.

See the full proposal here: https://governance.cartesi.io/t/cartenix-run-nix-inside-cartesi/150

====================================================================================================
[114] id=0xb7c899de187fbfc686b5baaa5715b5a36030bfc3b1b0bb75e9c4fdcece2a79c7  token=CTSI  space=cartesi.eth  date=2023-10-07
TITLE: CGP Grant Proposal: DCA.Monster
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
DCA.Monster - Modular DeFi 2.0  Components for Cartesi

The DCA.Monster project originated from ETH Global Paris 2023. The project is a novel AMM leveraging ERC20 streams for granular, efficient on-chain DCA. Combining Uniswap V2's power with Token Streaming, we're enabling "Infinite Granularity DCA" and a more dynamic DCA experience. Making advanced on-chain DCA. See the full proposal here, https://governance.cartesi.io/t/dca-monster-modular-defi-2-0-components-for-cartesi/210

====================================================================================================
[115] id=0x4b0124294693e661cb062b3816eba255af12fceefbb8ae988441bf27e53d7510  token=CTSI  space=cartesi.eth  date=2023-10-17
TITLE: CGP Grant Proposal: AI License Plate Violations Detector
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
The proposed project aims to build an on-chain-verifiable image recognition system using AI algorithms, which can be run on the Cartesi Virtual Machine and whose results can be stored in the blockchain. See the full proposal here, https://governance.cartesi.io/t/ai-powered-system-for-detecting-license-plate-violations-on-vehicles/206

====================================================================================================
[116] id=0xd53ba1bcc0a61ba090a6646aad8e04fce372fa157b5e7dd853cfd95181460512  token=CTSI  space=cartesi.eth  date=2024-04-09
TITLE: CGP Grant Proposal: Fastlane
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
Fastlane is a fully on-chain, infinitely expanding game built on Cartesi, where players navigate a dynamic road with hidden obstacles and compete for ownership, powered by novel cryptography and play-to-earn incentives.

See the full proposal here, https://app.charmverse.io/cartesi-grants-program/fastlane-32931751989216007

====================================================================================================
[117] id=0x1ed99f4b67ba07721fcaf148c0e0b3bea83696f9c452c566d31f3cf8fff22523  token=CTSI  space=cartesi.eth  date=2024-04-29
TITLE: CGP Grant Proposal: Chain IDE for Cartesi
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
The project proposes to build ChainIDE for Cartesi, which will be a multichain, cloud-powered, zero-setup, full-stack application development platform designed specifically for Cartesi. It will feature rich GUI-based tooling, simplifying the development process by offering a user-friendly interface that allows developers to configure, build, test, deploy, and interact with applications for Cartesi.

See the full proposal here, https://app.charmverse.io/cartesi-grants-program/cloud-based-full-stack-application-development-platform-for-cartesi-5845854705258293

====================================================================================================
[118] id=0x6d99a88c1af995d693d9cbd2cde8175c02a51ff137108dfcf75fe58ec275ef54  token=CTSI  space=cartesi.eth  date=2024-04-29
TITLE: CGP Grant Proposal: Boardgame.io-Inspired Library for Cartesi
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
The RFP proposal proposes the development of a new game library, inspired by the proven Boardgame.io architecture, with a unique focus on seamless integration with Cartesi technology. This library aims to empower game developers to create turn-based board games for the web, where game results are securely validated on the blockchain for transparency and trust.

See the full proposal here, https://app.charmverse.io/cartesi-grants-program/boardgame-io-inspired-library-for-cartesi-9638894566119671

====================================================================================================
[119] id=0xc0849e19bd1a9a090dfd85849fa0a8556a185ee899123b7a0e9230237fdc7c13  token=CTSI  space=cartesi.eth  date=2024-05-27
TITLE: CGP Grant Proposal: DCA.Monster
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
The project's second grant is developing an innovative suite of technologies for the DCA Monster project. This includes a mechanism for Layer 1-2 Rebasing Yields, a system for creating and managing auto-liquidatable synthetic tokens, and a fully permissionless authority contract.

See the full proposal here, https://app.charmverse.io/cartesi-grants-program/dca-monster-7992275308181851

====================================================================================================
[120] id=0x7198414107cb7beb5ca9091e033bdba951691f9686ccc74428a3e39fb592403d  token=CTSI  space=cartesi.eth  date=2024-08-01
TITLE: CGP Grant Proposal: World Tycoon
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
World Tycoon is a fully on-chain city building game built on Cartesi, where players develop and construct cities using in-game funds, powered by novel cryptography and play-to-earn incentives.
See the full proposal here, https://app.charmverse.io/cartesi-grants-program/world-tycoon-8918385381156733

====================================================================================================
[121] id=0x2f276024a4573c367be2a3297fc8d9dcfe2846e1d419455c37eae3d3ec44dc76  token=CTSI  space=cartesi.eth  date=2024-11-02
TITLE: Proposal: Cartesi Grants Program Intents and Wave 2 renewal
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Please refer to the [full proposal text on the Cartesi governance forum](https://governance.cartesi.io/t/proposal-cartesi-grants-program-intents-and-wave-2-renewal/436). 

#### This proposal seeks to introduce CGP Intents and renew the grants program for 6 months with Wave 2 as an iteration of Wave 1, with an allocation budget of $500,000 in CTSI.

Proposers: Pedro Argento, João Garcia, Hellenstans.eth

# Summary:

* The Grants Council proposes renewing the Cartesi Grants Program (CGP) for Wave 2, building on the foundation of [Wave 1.](https://governance.cartesi.io/t/cartesi-grants-program-cgp-wave-1/361)
* Based on the learnings from Wave 1, the Grants Council proposes shifting to a more proactive and forward-looking approach to grant funding with the introduction of Intents.
* Intents are medium-term goals or objectives that guide the strategic direction which the community should focus on. Think of an Intent as a North Star for CGP.
* Wave 2 will run for 6 months, during which proposals will be accepted on a rolling basis. After the 6-month period, the Intents will be reviewed and possibly updated to ensure they continue to align with the ecosystem's evolving priorities.
* The Grants Council has drafted five key Intents for Wave 2 to enhance alignment, focus and success across the ecosystem.
* All community efforts and projects supported in Wave 2 must align with our Intents.
* Proposals will follow a structured submission process, including community feedback and evaluat

====================================================================================================
[122] id=0xb9fd642f87ae7b6fb040faf2809c9842dc0b9efe3953806eb2aa1a0d50e42e22  token=CTSI  space=cartesi.eth  date=2025-04-16
TITLE: CGP Grant Proposal: Cartesi–Chainlink Library
CHOICES: Yes, fund this proposal | No, do not fund this proposal
TEXT (first 1500 characters):
The Cartesi-Chainlink Library aims to seamlessly integrate Chainlink’s automation services with the Cartesi ecosystem, empowering developers to easily implement advanced automation features within Cartesi dApps.

See the full proposal here, https://app.charmverse.io/cartesi-grants-program/cartesi-chainlink-library-02907080443062071

