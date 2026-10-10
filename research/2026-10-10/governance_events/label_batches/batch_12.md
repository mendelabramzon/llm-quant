# Labeling packets — batch 12 (97 proposals). Label each against criteria.md.

====================================================================================================
[0] id=0x3fdb38cc13abdfccf9978a27b74de7a47d52663c952bc6d8c4b8881442610fa3  token=LDO  space=lido-snapshot.eth  date=2022-10-07
TITLE: Proposal to return back 11 ETH that were sent by BloXroute's builder to Lido Execution Layer Rewards Vault
CHOICES: For | Against
TEXT (first 1500 characters):
## **Overview**

Over the course of the day on 09/27 the BloXroute ethical relay was receiving and returning bad blocks to validators from one of our block builders running an experimental build strategy that resulted in missed slots.

This builder was improperly committing transactions and caused improperly formatted blocks. Because the relay was not simulating blocks from known builders these blocks were getting sent to validators causing them to miss slots due to proposing blocks with improper receipts or log blooms. A total of 15 slots were missed due to this issue.

BloXroute’s relay was not simulating blocks from internal builders and was instead relying on these builders to submit valid blocks.

This was resolved:

- The experimental builder was taken offline and ensured that it was no longer submitting blocks to any of our relays.
- All of the validators who missed slot’s were paid for the bids they received from the bloXroute relay.
- On 09/30 all of the relays now simulate all block submissions regardless of source.

While transferring funds to bloXroute’s builder to pay for the missed slots the builder considered the transfer of 11 ETH as an MEV tip for the validator and paid that 11 ETH to the Lido Execution Layer Rewards Vault on slots [4791729](https://beaconcha.in/slot/4791729) and [4792026](https://beaconcha.in/slot/4792026).

## Proposal

This proposal is to return back 11 ETH that were sent to the Lido Execution Layer Rewards Vault.

If the proposal is suppo

====================================================================================================
[1] id=0x5844beba37131b3621c5c96621603db7cb7e2771d1c690dc6869ebd117e12abb  token=LDO  space=lido-snapshot.eth  date=2022-10-17
TITLE: Lido on Solana - Proposed Protocol Upgrade to v2
CHOICES: For | Against
TEXT (first 1500 characters):
# Summary

This proposal seeks approval from Lido DAO members to upgrade the smart contract to v2 in order to ensure a healthy validator economy and create a sustainable, high-performance validator set for Solana.

If this snapshot vote passes, the proposed smart-contract changes will be deployed to the mainnet. 

# Suggested changes in smart-contract

While the ideas that lie behind these changes were well described in [research forum proposal](https://research.lido.fi/t/lido-on-solana-protocol-upgrade-proposal/2959), we want to list again the key changes: 

- The transition from fully dedicated nodes with 100% fee to public ones with a variable fee;
- Increase the maximum number of validators to 6,700;

We also would like to set the variable fee for the validators in the set. Ideas behind that are described on the [research forum](https://research.lido.fi/t/lido-on-solana-maximum-validator-commission-proposal/2979). 

- Set the maximum commission for the validator to 5% to be eligible to receive a delegation from Lido on Solana.

# Changes in the rewards distribution model

As an expected result of the changes above, the staking rewards distribution model will slightly change. 

- In the current version of the smart contract, all the rewards are distributed simultaneously and precisely between node operators (5%), the DAO treasury (4%), the developer (1%), and the stakers (90%).
- After the suggested changes are made, the 5% (max, could be less than that) goes to the node o

====================================================================================================
[2] id=0x9d39cc7ed918e89cff5a597ff1e0bce0974f5721283dcac6ccc8274bde703d1f  token=LDO  space=lido-snapshot.eth  date=2022-10-17
TITLE: Proposal to return back 11 ETH that were sent by BloXroute's builder to Lido Execution Layer Rewards Vault (restart)
CHOICES: For | Against
TEXT (first 1500 characters):
## Overview
Over the course of the day on 09/27 the BloXroute ethical relay was receiving and returning bad blocks to validators from one of our block builders running an experimental build strategy that resulted in missed slots.

This builder was improperly committing transactions and caused improperly formatted blocks. Because the relay was not simulating blocks from known builders these blocks were getting sent to validators causing them to miss slots due to proposing blocks with improper receipts or log blooms. A total of 15 slots were missed due to this issue.

BloXroute’s relay was not simulating blocks from internal builders and was instead relying on these builders to submit valid blocks.

This was resolved:

* The experimental builder was taken offline and ensured that it was no longer submitting blocks to any of our relays.
* All of the validators who missed slot’s were paid for the bids they received from the bloXroute relay.
* On 09/30 all of the relays now simulate all block submissions regardless of source.
While transferring funds to bloXroute’s builder to pay for the missed slots the builder considered the transfer of 11 ETH as an MEV tip for the validator and paid that 11 ETH to the Lido Execution Layer Rewards Vault on slots [4791729](https://beaconcha.in/slot/4791729) and [4792026](https://beaconcha.in/slot/4792026).

Proposal
This proposal is to return back 11 ETH that were sent to the Lido Execution Layer Rewards Vault.

If the proposal is supported, then

====================================================================================================
[3] id=0x57c8e1017c79eacbe4dc56b9b0077f445d8bb8e49ec7dced4f6c3b3e63029eb1  token=LDO  space=lido-snapshot.eth  date=2022-10-17
TITLE: [RCC-3] October 1, 2022 - October 31, 2022 Budget Request
CHOICES: For | Against
TEXT (first 1500 characters):
The final standalone period for RCC funding, following on from [Q2 2022](https://research.lido.fi/t/rcc-2-july-1-2022-september-30-2022-budget-request/2729), has begun on October 1, 2022 and will end on October 31, 2022. We are preparing the grounds for a final funding proposal as a followup to [this post](https://research.lido.fi/t/lido-dao-core-contributors-provisional-budget/2556) that will run the DAO as a whole starting on November 1, 2022. We will publish more details over the coming days.

Lido will be moving to a continuous funding model starting on November 1, 2022, which has created a 1 month gap for operations financed out of RCC. The following request will bridge the gap for operating expenses for the month of October (many expenses are due at the end of the month). A total of 50k LDO will be requested to cover September overdue LDO compensation and October LDO compensation. 

This budget, on a monthly basis, is substantially larger than previous RCC asks for a few key reasons:
1. Deployment of marketing expenses in a busy month
2. Transfer of Audits and Bug Bounties from LEGO to RCC
3. Deployment of GCP and Github Funding
4. Contingency funding for operating expenses (not immediately drawn)

Details on the following link: [https://research.lido.fi/t/rcc-3-october-1-2022-october-31-2022-budget-request/3055](https://research.lido.fi/t/rcc-3-october-1-2022-october-31-2022-budget-request/3055)

## Proposal Actions

- **DAI 732,710** will be supplied to the RCC multis

====================================================================================================
[4] id=0xb2732ebb88f93b0c0cf649dfe6cc7e7549b36523781b9171c57e9ae68e441567  token=LDO  space=lido-snapshot.eth  date=2022-12-05
TITLE: Improving the incentive structure for the Lido on Polygon team
CHOICES: For | Against
TEXT (first 1500 characters):
We propose to increase by 500,000 LDO the number of incentives for the [Shard Labs](https://shardlabs.io) team who makes Lido on Polygon to **1,500,000 LDO total** to reflect that Polygon importance had risen relatively since the [first proposal](https://research.lido.fi/t/lido-for-polygon-proposal-by-shard-labs/816) and that the deal was different from our baseline for other networks as well.

### Hence, we advocate for the increase with the following changes:

1. Move the first threshold to 1% instead of 2.5%
2. Update steps of market share
3. Increase the number of incentives in the first steps
4. Change vesting conditions

### The proposed new incentive structure in detail:

- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 1% of the staked MATIC supply
- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 2% of the staked MATIC supply
- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 3% of the staked MATIC supply
- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 4% of the staked MATIC supply
- 100,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 5% of the staked MATIC supply
- 100,000 LDO tokens issued with vesting with 2-year vesting when Lido for Polygon manages to capture 6% of the staked MATIC supply
- 100,000 LDO tokens issued with vesting with 2-year vesting when Lido for Polygon manages to capture 8%

====================================================================================================
[5] id=0x7f19fed19b66df88b45d64c22f9905fbf716839a5052fb79b10ee2ef1241645d  token=LDO  space=lido-snapshot.eth  date=2022-12-13
TITLE: Referral Program for Ethereum - Final Reform
CHOICES: YAY | NAY
TEXT (first 1500 characters):
## Background

The bear market and recent market events has shown the importance of increasing the adoption of defi and more decentralized infrastructure. With increased centralized competition, speed of execution is of the utmost importance for the whole industry. To date, Lido DAO’s referral program has exceeded expectations. However, the current model is unsustainable. With protocol sustainability in mind, referral rewards need to be reduced to a manageable level.

A longer-term revenue share model is outside the scope of this proposal.

The initial focus will be on Ethereum.

## Proposal

We are submitting the following proposal:

1. Implement a new referral model for stETH structured as per referrer:
    - 2.5 DAI per ETH referred up to $100m worth of ETH
    - 3.5 DAI per ETH referred up to $250m worth of ETH
    - 4.5 DAI per ETH referred up to $500m worth of ETH
    - 5.0 DAI per ETH referred up to $1.0bn worth of ETH
    - 5.5 DAI per ETH referred up to $5.0bn worth of ETH
2. The new model starts at 0 and is cumulative during the term of the program for participants.
3. Limit the initial reward pool to a maximum of 1,000,000 DAI.
Depending on success and market dynamics, refreshing the pool in 1M DAI
increments will be voted on and discussed. Updates will be provided in
this thread.
4. Begin winding down the program before withdrawal operations are enabled on Ethereum.
    1. Optional transition to successor program after withdrawals are enabled

### Operations

Oper

====================================================================================================
[6] id=0x7ac2431dc0eddcad4a02ba220a19f451ab6b064a0eaef961ed386dc573722a7f  token=LDO  space=lido-snapshot.eth  date=2022-12-16
TITLE: Lido on Ethereum Block Proposer Rewards Policy 2.0 and Relay Maintenance Committee
CHOICES: For | Against
TEXT (first 1500 characters):
Following the [draft policy updates extensively discussed on the forums](https://research.lido.fi/t/discussion-draft-lido-on-ethereum-block-proposer-rewards-policy-2-0/3132/13), a proposed [v2.0 of the Block Proposer Rewards Policy](https://lido.mypinata.cloud/ipfs/QmaLLjLE2iecf59kTQSVC1rHVPjjQwGDTCouR8A871BNRY) has been uploaded to IPFS.

**If you think Lido DAO should update the existing policy and enact the updated version, vote For. If you are against this proposal, vote Against.**

**Below is a summary of changes to the policy included in the v2.0 proposal:**

- Set expectation of full-scale rollout of “PBS lite” via MEV Boost for all Node Operators going forward
- Define responsibilities of Node Operators in the case of Relay misbehavior, failure, or otherwise unexpected or non-performant functionality (e.g. what happens if relays provide bad bids, bad blocks, don’t unblind timely, etc).
- Define the responsibilities of Relay Operators towards the Lido Protocol and Node Operators

**Additionally, by voting For, the below is also ratified:**

- Propose to empower the [Relay Maintenance Committee](https://research.lido.fi/t/lido-on-ethereum-identify-and-constitute-relay-maintenance-committee/3386) to facilitate the maintenance of the Lido vetted relay lists.
    - The Relay Maintenance committee will be a 5/7 Gnosis Safe multisig and have the address [https://gnosis-safe.io/app/eth:0x98be4a407Bff0c125e25fBE9Eb1165504349c37d](https://gnosis-safe.io/app/eth:0x98be4a407Bff0c

====================================================================================================
[7] id=0x3436b98afacec300ec2c0f79bb8dfd16685ececeeb7a45a18754d43b710179e8  token=LDO  space=lido-snapshot.eth  date=2023-01-11
TITLE: Improving the incentive structure for the Lido on Polygon team (restart)
CHOICES: For | Against
TEXT (first 1500 characters):
This is a restart of [the proposal that did not reach a quorum](https://snapshot.org/#/lido-snapshot.eth/proposal/0xb2732ebb88f93b0c0cf649dfe6cc7e7549b36523781b9171c57e9ae68e441567). We provided [more explanation and got positive feedback on the Research forum](https://research.lido.fi/t/improving-the-incentive-structure-for-the-lido-on-polygon-team/3240/11). Please read the content of the proposal and vote.

We propose to increase by 500,000 LDO the number of incentives for the [Shard Labs](https://shardlabs.io) team who makes Lido on Polygon to **1,500,000 LDO total** to reflect that Polygon importance had risen relatively since the [first proposal](https://research.lido.fi/t/lido-for-polygon-proposal-by-shard-labs/816) and that the deal was different from our baseline for other networks as well.

### Hence, we advocate for the increase with the following changes:

1. Move the first threshold to 1% instead of 2.5%
2. Update steps of market share
3. Increase the number of incentives in the first steps
4. Change vesting conditions

### The proposed new incentive structure in detail:

- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 1% of the staked MATIC supply
- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 2% of the staked MATIC supply
- 150,000 LDO tokens issued with no vesting when Lido for Polygon manages to capture 3% of the staked MATIC supply
- 150,000 LDO tokens issued with no vesting when Lido

====================================================================================================
[8] id=0xc00b48275e268f26b6cebf82322f281a44acaf679f6381dd612e278174671daf  token=LDO  space=lido-snapshot.eth  date=2023-02-09
TITLE: Request to authorise a 22M LDO ceiling for a four year contributor Token Reward Plan (TRP)
CHOICES: For | Against
TEXT (first 1500 characters):
### Summary

This proposal incorporates updates to the [prior discussion](https://research.lido.fi/t/lidodao-token-rewards-plan-trp/3364). It requests approval for the authority to donate up to a maximum ceiling of 22M LDO to a grants association for use in a Token Reward Plan (TRP), a framework which will distribute voting LDO tokens spread over a period of up-to four years to DAO contributors. The proposal will enable a single universal arrangement for contributors to participate in DAO governance that is connected to their continuous contribution periods. It will also offboard the burden and risk of DAO commitments to the contributors to a single purpose grants association. The association will receive the donations over time and will make grants of LDO from the association into the hands of contributors according to the parameters of the TRP described below. Democratising governance participation by increasing the number of independent actors will enhance the resilience of the DAO’s treasury to resist governance attacks, improve routine quorum, and reward long-time contributors with LDO at the same time.


### Abstract

Approve the donation of up-to a maximum ceiling of 22M LDO to be transferred over a four year timeline to the grants association’s multisig. The signer’s of the multisig will be members of a not-for-profit grants association. The purpose of the association will be to own the multisig and to assure the integrity of a grants program described by the TRP. Thi

====================================================================================================
[9] id=0xac31f800288c68e32d1eb3cea7a525022faae3eb3bf805d1b3d248cda5375a13  token=LDO  space=lido-snapshot.eth  date=2023-04-20
TITLE: Proposal to approve Lido DAO Treasury Management Principles and authorize the formation of a Treasury Management Committee
CHOICES: For | Against
TEXT (first 1500 characters):
## Summary

This proposal is asking for the approval of a few key **Treasury Management Principles (Principles)**, and the creation of a **Treasury Management Committee (Committee)** to put forward **Treasury Management Strategies (Strategies)** constrained by the **Principles**, and **Treasury Management Actions (Actions)** to execute them using **On-chain tools**.

 
![image(1).png](ipfs://bafkreibfuwuo7jevntrqdh4l5nlurwwe7r7gs2xqeiew3ox54tpor27iku)
    

## Treasury Management Principles

1. **ETH is Lido DAO’s primary Unit of Account, interchangeable with stETH through deposits and withdrawals using Lido protocol.**
2. **Lido DAO’s treasury is the source of its resilience and future growth, and can fund initiatives that further the protocol’s decentralization and network security objectives**
    1.  The purpose of Lido DAO’s treasury is to support the integrity, growth and robustness of the Lido protocols
    2.  The treasury may also be used for funding many initiatives, including but not limited to, research, maintenance, development, education and advocacy that further the decentralization and network security objectives of the protocol
3. **Risk of loss to treasury funds should be minimized at every instance**
4. **All treasury ETH must be staked using Lido**
5. **Token holders have the ultimate say**
    1. Token holder decisions can amend and update the Principles, as well as override the Committee through separate on-chain votes

*(nb. 20,304 ETH at time of writin

====================================================================================================
[10] id=0xd460ea50072deb6bc428064a118dfd499714d4a7865552b4047eba3199663596  token=LDO  space=lido-snapshot.eth  date=2023-05-04
TITLE: Nominating reWARDS committee as a Lido DAO representative for airdrops
CHOICES: For | Against
TEXT (first 1500 characters):
The Arbitrum Foundation has announced that the Lido DAO is eligible for the ARB airdrop. According to the documentation of the airdrop ([$ARB airdrop eligibility and distribution specifications | Arbitrum DAO - Governance docs](https://docs.arbitrum.foundation/airdrop-eligibility-distribution#dao-airdrop-criteria-and-distribution)) Lido DAO is eligible to claim 772,621 ARB tokens. 

In response to this airdrop, [the Lido DAO reWARDS committee](https://research.lido.fi/t/proposal-to-form-rewards-committee/1447) puts forward the following proposal. This proposal covers operational and strategic topics related to claiming and making productive use of the potential ARB tokens or any other token airdrop to which Lido DAO may be entitled in the future. If passed, this proposal will enable the reWARDS committee to pursue the continued growth of staking and the wstETH DeFi ecosystem on Arbitrum One (and beyond).

The Arbitrum Foundation governance documentation shares that there are no specific conditions on the distribution of these tokens, but that the hope and intent is that each DAO will determine how to best participate in the governance and growth of the Arbitrum ecosystem using these tokens.

You may find more details about current State of wstETH on Arbitrum Network [in this forum post](https://research.lido.fi/t/arbitrum-arb-token-airdrop-acceptance/4393).

### **Proposal**

**This proposal has several elements:**

**A)** Acknowledging the offer of 772,621 ARB tokens from th

====================================================================================================
[11] id=0xdf57d5600ca8c0485a17de035afffe3b918e6059a6ba10bec71fb04f4041b41d  token=LDO  space=lido-snapshot.eth  date=2023-05-04
TITLE: [LIDO-v2] May 1, 2023 - December 31, 2023 | Lido Ongoing Grant Request
CHOICES: For | Against
TEXT (first 1500 characters):
# Summary

Request 24.5m DAI and 200k LDO in continuity funding from May through December 2023 to support the development and implementation of v2 and ongoing maintenance for the protocol. For simplicity this proposal will express itself in DAI to align with the denomination of most of these expenses.

- 20.5m DAI and 200k LDO to continue grant funding to outsource Lido V2 development and support to the 2 entities part of the wider Lido Contributors Group
    - ca. 30m DAI yearly run-rate with an expectation to land on a substantially lower run-rate after backing out audits and contingencies
- 4m DAI equivalent for liquidity and marketing incentives bringing the total max spend in all sales & marketing incentives to 14m for 2023, down from over 100m in 2022
- Switching liquidity incentivization from LDO to stETH (using EasyTrack factories in case of Lido DAO approval)
- Changes to TRP Program to protect the DAO from edge cases

# Proposal Actions

## Continuity Grant Funding for Lido v2

Continuity for ongoing projects being outsourced to Pool Maintenance Labs Ltd., Argo Technology Consulting Ltd. or serviced by RCC, to collect functions relating to protocol execution, sponsorships and development support for the DAO. These existing contributor channels can mitigate present business continuity risks while advancing decentralised protocol governance.

This proposal would ratify the below budget request that will officially engage the Lido Contributors Group for a further 8 mon

====================================================================================================
[12] id=0x211ebdacbfae9d3492ff9e096b6f7be8a58bd48cd9eb8fc57454575b68bd6fc1  token=LDO  space=lido-snapshot.eth  date=2023-05-04
TITLE: A decision on an outflow of 39.8 ETH from the Lido DAO treasury to aid in the Sushi recovery
CHOICES: No action | Send 39.8 ETH to sifuvision.eth
TEXT (first 1500 characters):
## Proposal

Should the `39.8 ETH` that flowed into the Lido DAO Treasury, as a result of an exploited vulnerability in [SushiSwap RouteProcessor2](https://twitter.com/MetaSleuth/status/1644940303466647553), be sent to [sifuvision.eth](https://etherscan.io/address/0x31d3243CfB54B34Fc9C73e1CB1137124bD6B13E1) (the affected party) as an expression of goodwill?

## Motivation

Untangling [the original post and discussion](https://research.lido.fi/t/sushi-routeprocessor2-post-exploit-request-for-comment/4383), two, largely orthogonal, decisions at hand may be derived:

1. A decision on an outflow of `39.8 ETH` from the Lido DAO treasury to help Sushi (this is the amount which came into the treasury as a result of the exploit).
2. A wider policy decision on whether or not the DAO should ever act as an arbiter between stakers, node operators, and third parties – and if so, how, and under what conditions.

The discussion under the original post has revolved almost entirely around the second decision – yet this has not been made clear within the discussion itself.

To minimize the risk of decisions, on both fronts, being made for the wrong reasons, it makes sense to move these two decisions into separate threads where they can be discussed individually.

## Key points

Concerns of the type that [Hasu](https://research.lido.fi/t/sushi-routeprocessor2-post-exploit-request-for-comment/4383/7) and [Misha](https://research.lido.fi/t/sushi-routeprocessor2-post-exploit-request-for-comment/43

====================================================================================================
[13] id=0xf9ea35a74376178f680b2d3d6c26174be1853a487fcec9cda6880a05198f33db  token=LDO  space=lido-snapshot.eth  date=2023-05-18
TITLE: A decision on an outflow of 39.8 ETH from the Lido DAO treasury to aid in the Sushi recovery (restart)
CHOICES: Send 39.8 ETH to sifuvision.eth | No action
TEXT (first 1500 characters):
### **TL;DR**

A second vote on whether the `39.8` ETH that flowed into the Lido DAO Treasury, as a result of an exploited vulnerability in [SushiSwap RouteProcessor2](https://twitter.com/MetaSleuth/status/1644940303466647553), should be sent to [sifuvision.eth](https://etherscan.io/address/0x31d3243CfB54B34Fc9C73e1CB1137124bD6B13E1) (the affected party) as an expression of goodwill?

The previous vote was split 67% / 33% in favour of sending the ETH, but quorum [was not reached](https://snapshot.org/#/lido-snapshot.eth/proposal/0x211ebdacbfae9d3492ff9e096b6f7be8a58bd48cd9eb8fc57454575b68bd6fc1). 

## Motivation

Untangling [the original post and discussion](https://research.lido.fi/t/sushi-routeprocessor2-post-exploit-request-for-comment/4383), two, largely orthogonal, decisions at hand may be derived:

1. A decision on an outflow of `39.8 ETH` from the Lido DAO treasury to help Sushi (this is the amount which came into the treasury as a result of the exploit).
2. A wider policy decision on whether or not the DAO should ever act as an arbiter between stakers, node operators, and third parties – and if so, how, and under what conditions.

The discussion under the original post has revolved almost entirely around the second decision – yet this has not been made clear within the discussion itself.

To minimize the risk of decisions, on both fronts, being made for the wrong reasons, it makes sense to move these two decisions into separate threads where they can be discussed indi

====================================================================================================
[14] id=0xbfecc75c45bca53d3c5786f099d46559ac597bc3fae802d5f599b60f10b4bd4a  token=LDO  space=lido-snapshot.eth  date=2023-05-25
TITLE: Nominate the Gas Supply Committee as a supervisor for gas expenditure
CHOICES: For | Against
TEXT (first 1500 characters):
### Proposal

The purpose of this proposal is to expand the role of the Gas Funder Committee (was created [here](https://research.lido.fi/t/proposal-to-fund-the-depositor-bot-in-ethereum/1881)) and to rebrand it into the **Gas Supply Committee**.

The new authority is to determine the eligibility of gas expense reimbursements arising in day-to-day operation of the protocols within an **annual budget capped at 1,000 stETH**.

If the proposal approved by the Lido DAO - stETH replenishment setup of the committee's multisig to be subsequently added into Easy Track factories registry during the next Aragon vote.

### The Committee Operations

A [multisig - 0x5181d5D56Af4f823b96FE05f062D7a09761a5a53](https://etherscan.io/address/0x5181d5D56Af4f823b96FE05f062D7a09761a5a53) will be used between the Lido treasury and compensation recipients, refills to be done via on-chain voting solution (i.e. [Easy Track](https://easytrack.lido.fi/) motions, [Aragon](https://vote.lido.fi/), etc) - continuous operation of the protocol is a priority, the first refill of 100 stETH to be offered via Easy Track motion or Aragon vote soon after this proposal acceptance. The first refill amount based on the current month gas spent (80+ ETH) and [an amount according to Lido on Polygon request](https://research.lido.fi/t/funding-for-lido-on-polygon-depositor-bot/4431).

The following will be the initial expenditures authorised for reimbursement with an opportunity to include new (or evict old) ones in the fu

====================================================================================================
[15] id=0x5e9ffb74b7f0e026a898301a65302345fb6dc2e09f724b9c9bec2f35902c1324  token=LDO  space=lido-snapshot.eth  date=2023-05-25
TITLE: Launchnodes - Impact Staking with Lido
CHOICES: For | Against
TEXT (first 1500 characters):
## TL;DR

Launchnodes has been at the forefront of Impact Staking for ETH since its launch in 2020, where staking rewards fund projects addressing global issues. Impact Stakers pledge a portion of their rewards, while receiving their initial staked capital back at an agreed time. Funded projects must provide clear metrics to demonstrate their efficacy, allowing Impact Stakers to monitor their impact. Effective projects receive ongoing funding, while ineffective projects are quickly remedied.

This grant proposal is to enable Lido on Ethereum stakers to pledge some or all of their staking rewards to projects that require ongoing funding. Projects are expected to include initiatives from UNICEF, GiveDirectly, Save The Children and other leading global organizations. It is anticipated that individuals and entities such as foundations and family offices will consider Impact Staking through Lido in the future.

The 3 initial causes to which Lido Impact Staking rewards are planned to be targeted are:

| Cause / Project | Project Delivery | KPIs / Outcome Tracked |
| --- | --- | --- |
| Net Zero Ethereum | Treedom | Carbon Offset (tonnes/CO2) vs Ethereum footprint |
| Internet Connectivity for Schools | UNICEF Giga | Number of schools connected to the Internet |
| Lifting People Out of Poverty | Give Directly | Number of people lifted out of poverty |

These 3 projects have huge global potential to improve lives, and to reduce the carbon footprint of the Ethereum network.

All aspec

====================================================================================================
[16] id=0x9279cd4addefdd9185d024f471f1a29561f61556ae209cdda5dffb1fd73b181e  token=LDO  space=lido-snapshot.eth  date=2023-06-22
TITLE: Tiered Rewards Share Program: A Sustainable Approach to stETH Growth
CHOICES: For | Against
TEXT (first 1500 characters):
# TL;DR

This proposal aims to introduce a rewards-share system to encourage market participants who may not prioritize or stake with the Lido protocol without rewards. To effectively manage the program and minimize risk, tiered rewards will be implemented as percentages of the generated rewards. This ensures that the incentives align with ETH being staked with Lido and maintain the protocol's sustainability.
It's also proposed to form the Committee which will control a multi-signature wallet with authority to whitelist, filter, and distribute stETH protocol rewards.

# Proposal

This proposal is for a tiered rewards-share program that offers a percentage of the DAO’s 5% share of staking rewards to participants who stake ETH using Lido. The program is designed to have limited rewards pools, gradual payouts, a fixed duration that the DAO shares with participants, and filtering for program abuse(details of abuse mentioned later).

The rewards-share program operates in three-phases:

1. **Onboarding**: This phase involves the initial application and evaluation process. Prospective participants need to meet the eligibility criteria outlined in the proposal below. The Rewards Share Committee will review and vote on applications, then add the accepted addresses to the program.
2. **Rewards-Share**: Once onboarded, participants are eligible for rewards-share. The Committee will monitor participants’ stETH contributions and calculate rewards based on positive activities, disqualifica

====================================================================================================
[17] id=0x2a990d0266910e14c21360e3902c64f2a68971b1a51aaaeb94978e1513effcfd  token=LDO  space=lido-snapshot.eth  date=2023-06-22
TITLE: LEGO grant to Launchnodes for Lido Impact Staking initiative
CHOICES: For | Against
TEXT (first 1500 characters):
Supervised by LEGO 

$300K DAI LEGO grant to Launchnodes for research and implementation of a solution for responsible staking initiative.

## TL;DR

Launchnodes pioneers Impact Staking for ETH, funding projects addressing global issues. Impact Stakers pledge rewards to projects with measurable impact. Effective projects receive ongoing funding, while ineffective ones are remedied swiftly.

Lido Impact Staking Smart Contract aims to enable ETH stakers to pledge rewards to ongoing projects. Beneficiaries include UNICEF, GiveDirectly, Treedom, and others. Impact Staking via Lido is expected to attract individuals, foundations, and family offices.

All aspects of the web3 infrastructure and implementation for Impact Staking with Lido are intended to be fully transparent and visible in public repos and on the Ethereum blockchain.

## Motivations

1. Strategically value of the proposal for Lido is that it can become a new distribution channel and a case study for stETH wrappers.
2. It provides a low-cost opportunity for the DAO to engage new contributors, which enhances decentralization and the growth of Lido on Ethereum.
3. The project's potential to attract interest and serve as a pilot for future initiatives is seen as a valuable positive communication opportunity for the broader ecosystem.
4. It showcases how Lido can be used as staking middleware to empower users in the web3 ecosystem and support real-world initiatives.
5. By linking staking rewards with real-world organizati

====================================================================================================
[18] id=0xf3ac657484444f0b54eba2c251135c47f875e3d1821496247d11bdd7fab0f291  token=LDO  space=lido-snapshot.eth  date=2023-10-26
TITLE: Staking Router Module Proposal: Simple DVT
CHOICES: 1a. Deploy Simple DVT | 1b. Do not deploy Simple DVT | 2a. Use Lido cover fund | 2b. Use 3rd party cover provider
TEXT (first 1500 characters):
Following a [discussion of the draft proposal on the Lido Research forum](https://research.lido.fi/t/staking-router-module-proposal-simple-dvt/5625) for the Simple DVT Module, the advancement of the proposed module is now up for Snapshot vote by the Lido DAO.

**The vote will consider two main components:**

**1. Should the Lido DAO add the Simple DVT module as described within the proposal?**
**2. Should potential module slashing penalties be covered by the DAO cover fund or explicitly purchased & scoped by third-party cover?**

The vote will cover these questions in a multiple choice format:
  1a. Deploy Simple DVT
  1b. Do not deploy Simple DVT
  2a. Use Lido cover fund
  2b. Use 3rd party cover provider

*Voters should first select between options 1a and 1b to determine if the module should be deployed on mainnet following a successful testnet. For voters that choose option 1a, they should also vote on whether to utilize the Lido cover fund (2a) or 3rd party cover provider (2b). Voters that choose option 1b can skip voting on options 2a and 2b. If option 2b is chosen, a subsequent vote will be held to determine the 3rd party cover provider.*

If option 1a passes with quorum, the risk mitigation option with the highest number of votes between 2a and 2b will be chosen as the path forward.

Below is a summary of the proposal and excerpts of certain sections from the Simple DVT policy for summary purposes. Voters are encouraged to read the proposal on the Lido Research forums

====================================================================================================
[19] id=0x1d38c11b27590ab5c69ca21c5d2545d53b7f5150dada7e05f89d500ede5becad  token=LDO  space=lido-snapshot.eth  date=2023-12-07
TITLE: Should the Lido DAO recognize the wstETH Bridge Endpoints on Mantle as canonical?
CHOICES: Recognize | Don’t recognize
TEXT (first 1500 characters):
**The proposal** is to recognize the wstETH token bridging endpoints for Mantle by the Lido DAO as canonical. If Snapshot passes, the Lido DAO will control the endpoints of wstETH token contract (including the token contract on Mantle itself) as a proxy admin. Lido DAO will only have the upgrade authority of the wstETH proxy contract, and will not be able to manage the native bridge itself.

The Mantle Core Contributor Team is submitting this proposal to the community for the deployment of wstETH on Mantle.

[Mantle Network](https://mantle.xyz/) is an optimistic Ethereum layer-2 (L2) solution with an EVM-compatible execution environment. Mantle is DAO-governed and employs a modular approach to execution, consensus, settlement, and data availability. In addition to a burgeoning ecosystem with 110+ dApps and counting, Mantle counts among its partners Game7, HyperPlay, EduDAO, Sozu Haus, and EigenLayer. The DAO-led community-driven Mantle possesses one of the largest on-chain treasuries — and the largest when discounting native tokens — including nearly 270K ETH/wstETH/WETH, priming it to be a major player in ETH LST and LSDFi.

### Motivation

Demand for Lido (w)stETH is significantly driven by its utility within major ecosystems, which are leveraging its composability in various DeFi protocols. Notably, wstETH’s overwhelming market share of staked ETH enhances its desirability. Additionally, wstETH’s versatility, being used for a range of DeFi applications including collateral

====================================================================================================
[20] id=0xa39815519107002997769f0b79a9e3957c3bf793166ab948fc6413ce5b3def55  token=LDO  space=lido-snapshot.eth  date=2023-12-07
TITLE: Lido Community Staking Module
CHOICES: Approve | No action
TEXT (first 1500 characters):
The Lido Community Staking team is seeking signal approval of the [Community Staking Module](https://hackmd.io/@lido/Byp775Ay6) (CSM) design from the Lido DAO. The module will allow permissionless entry to the Lido on Ethereum validator set with a bond requirement.

Lido on Ethereum currently has a curated set of node operators; at the current stage DAO has approved [Simple DVT module signal proposal](https://snapshot.org/#/lido-snapshot.eth/proposal/0xf3ac657484444f0b54eba2c251135c47f875e3d1821496247d11bdd7fab0f291), which is planned to launch in Q1 2024. And the next step towards decentralization is CSM!

In case of approval, the Community Staking team will carry out further research and development of the module proposed, and the mainnet release, along with all the parameters, would be proposed for the Lido DAO approval in the on-chain vote for the upgrade closer to the end of 2024.

## **High-level design**

High-level design is described in detail in the [Community staking landscape](https://hackmd.io/@lido/Byp775Ay6) and discussed on the [Lido research forum](https://research.lido.fi/t/community-staking-module/5917).

Key points of high-level design are:

1. Permissionless entry with bond
2. Only ETH (stETH) as a bond token
3. “Non-linear” bond scaling for Node Operators
4. First in, first out stake allocation queue
5. Performance oracle with performance threshold approach for solo staker friendly rewards distribution

Whereas the high-level design of the module is deve

====================================================================================================
[21] id=0x41a47f0735b7aca8c1e7f93fae86a82f5c3fac8796657d2e95e63b1aa6d09c52  token=LDO  space=lido-snapshot.eth  date=2023-12-07
TITLE: [EGG] st2024 v1 Lido Contributors Group request for grant funding to advance GOOSE goals
CHOICES: Provide funding | Decline
TEXT (first 1500 characters):
## tldr

- Continue grant approvals to the Lido Contributors Group to advance towards hasu’s [GOOSE](https://research.lido.fi/t/hasus-goose-submission-proposed-goals-for-lido-dao-to-consider/) Goals
- Development, audit and deployment of multiple Staking Router modules, Dual Governance, Layer 2 integrations and reviews and zkOracles
- Best-before date: 2024-06-30
- 22.5m DAI + 200k LDO in grant continuity for the Lido Contributor’s Group, with an additional 10% contingency
- 8.6m DAI in grant continuity for the Liquidity Observation Lab

## Basic Data

| Field | Description |
| --- | --- |
| Proposal Name | st2024 v1 |
| Which of the following GOOSE goals is your proposal advancing? | 1: Lido has effective and decentralized governance, 2: Lido attracts the best validator set in the market, 3: stETH is the most used token in the Ethereum ecosystem |
| Proposed scope of work | Engineering Coordination, stETH Core Protocol Engineering, Validator Set Engineering for the Staking Router, Alerting and Monitoring Tooling, Community Module, Governance Core Protocol Engineering, API & Components |
| Objectives | Significantly advance all three GOOSE goals by making meaningful progress towards researching and deploying new Staking Router modules, dual governance implementations |
| Total Budget Request | 34m DAI, 200k LDO |
| Best-before date | 2024-06-30 |

## st2024 v1

st2024 v1 is a 6mo grant request to advance all three of the GOOSE goals approved by the DAO earlier this year. All

====================================================================================================
[22] id=0x74eaaca973a0a2f3b661e344b64d953e6061eb35d119faf396f348a484c9948f  token=LDO  space=lido-snapshot.eth  date=2024-03-14
TITLE: InfStones Return to Active Status Proposal
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal is a followup to the previous vote (in December 2023) regarding InfStones resuming active participation in the Lido Node Operator set ([link to the vote](https://snapshot.org/#/lido-snapshot.eth/proposal/0xe432ccf3aba98301bcb9acc1befbf1725fbec1431340fbb1fdc0c0a8143ad188)), which ended with a lack of quorum for any option and generally leaning towards the operator re-activating but with some voters opining that additional time was required.

In the time since, InfStones have worked with a third party information security consultant (https://carbidesecure.com/) to perform penetration testing on their infra, specifically targeting the issues identified in the original infrastructure vulnerability disclosure. The executive summary of the pentest has been provided to the DAO (https://research.lido.fi/t/lido-on-ethereum-node-operator-infstones-platform-vulnerability-investigation-november-22-2023/6001/23), and the detailed report was provided to DAO contributors who requested access, as well as a SOC 2 Type I report. Follow-up questions were submitted by contributors and responses were received. Currently, contributors feel that there is no reason to believe that the relevant infrastructure vulnerabilities are still present, nor that any other known vulnerabilities have not been adequately remediated and/or resolved.

A summary of events follows below:

On Nov 22, Lido DAO contributors were made aware of two platform vulnerabilities in the validator infrastructure of

====================================================================================================
[23] id=0xd326ac1c7f4317b370e794a3e57d342f8c9dd8c4f517b2632f835a93585fb0f3  token=LDO  space=lido-snapshot.eth  date=2024-03-14
TITLE: Rewards-Share Program 2024
CHOICES: Adopt new proposed program | Retain current program
TEXT (first 1500 characters):
The Rewards Share Committee’s proposal is to adopt a new Rewards-Share Program that will replace the previous [Tiered Rewards Share program](https://research.lido.fi/t/tiered-rewards-share-program-a-sustainable-approach-to-steth-growth/4851) (approved by [Snapshot](https://snapshot.org/#/lido-snapshot.eth/proposal/0x9279cd4addefdd9185d024f471f1a29561f61556ae209cdda5dffb1fd73b181e) (end date June 29, 2023). 

As with the previous program, the new program helps spread awareness about liquid staking technology and liquid staking tokens like stETH, through sharing some of the middleware usage fees with selected applicants. However, the new program introduces number of changes, summarised below.

## **Summary of main changes**

- **Minimum Threshold:** The new program will focus on institutional applicants that meet a Minimum Threshold that requires participants to demonstrate that they have already driven at least 40,000 ETH in stake coming from users of the Lido Middleware - this should attract high quality participants.
- **No tiers:** Instead, the Rewards Share Percentage will be calculated by the Committee, up to a maximum of 50% of the DAO’s 5% share of staking rewards.
- **Quarterly payment of rewards-share**

For more details about the program please refer to [the forum post](https://research.lido.fi/t/rewards-share-program-2024/6812). Rewards Share committee details located [here](https://docs.lido.fi/multisigs/committees#22-rewards-share-committee-prev-referral-program-c

====================================================================================================
[24] id=0x3ea112ff9a98fb8f52f5b8ff636c4530657d9c4bff9827be80a7a27e2d119231  token=LDO  space=lido-snapshot.eth  date=2024-04-05
TITLE: Activate Lido Protocol Governance with Revenue Share Staking
CHOICES: Yes- add revenue share to $LDO | No - do not add revenue share
TEXT (first 1500 characters):
$LDO Revenue Share

a. Redirect 20-50% (toggle-able parameter based on governance) of future Lido DAO revenue from the protocol treasury to $LDO Stakers

b. Distribute Lido DAO revenue to $LDO stakers in $LDO tokens weekly through a buyback and distribute mechanism (exact mechanics will be determined separately)

i. This mechanism allows all $LDO holders (not just stakers) to benefit from the revenue generated by the protocol
ii. All stakers will ‘receive’ token as weekly emissions. All earned tokens will be vested for 3-months before distribution accruing compounded emissions.


The aforementioned is based on included link and subsequent conversation.

====================================================================================================
[25] id=0x2baf3275d15a8494ff94fef58d93bedd2fc28bfea8519f7e86474fc72dc25076  token=LDO  space=lido-snapshot.eth  date=2024-06-27
TITLE: [EGG] st2024 v2: Continuity Grant Funding to Achieve GOOSE Goals
CHOICES: Approve EGG request | Decline (grants discontinue)
TEXT (first 1500 characters):
## tldr

- Continue grant approvals to the Lido Contributors Group to advance towards Hasu’s [GOOSE](https://research.lido.fi/t/hasus-goose-submission-proposed-goals-for-lido-dao-to-consider/) and [reGOOSE](https://research.lido.fi/t/regoose-updated-goals-for-lido-in-the-light-of-mvi-and-restaking/) Goals
- Development, audit and deployment of multiple Staking Router modules, Dual Governance, Layer 2 integrations and reviews and zkOracles and integrations for stETH in restaking
- Best-before date: 2024-12-31
- 24.6m DAI (or USDC, USDT hereinafter) + 180k LDO in grant continuity for the Lido Contributor’s Group
- 7.1m DAI in grant continuity for the Liquidity Observation Lab
- 400k DAI for the [Community Lifeguard](https://research.lido.fi/t/egg-establishing-the-community-lifeguards-initiative-cli-sub-committee/) initiative

## Basic Data

| Field | Description |
| --- | --- |
| Proposal Name | st2024 v2 |
| Which of the following GOOSE goals is your proposal advancing? | 1: Lido has effective and decentralized governance, 2: Lido attracts  the best validator set in the market, 3: stETH is the most used token in the Ethereum ecosystem |
| Proposed scope of work | Engineering Coordination, stETH Core Protocol Engineering, Validator Set Engineering for the Staking Router, Alerting and Monitoring Tooling, Community Module, Governance Core Protocol Engineering, API & Components |
| Objectives | Significantly advance all three GOOSE goals by focusing on expanding the validator set

====================================================================================================
[26] id=0xdfb6a16a991379cd62222bb20792db7ce1dc0e2a0db17e8d7422717802f50145  token=LDO  space=lido-snapshot.eth  date=2024-06-27
TITLE: Proposal: The Decentralized Validator Vault
CHOICES: Implement the vault strategy | Do not implement
TEXT (first 1500 characters):
The below proposal follows the [discussion post created on June 20th 2024](https://research.lido.fi/t/discussion-the-decentralized-validator-vault/7729).

This proposal seeks DAO support for the implementation of a vault solution by the [Lido Alliance member Mellow](https://snapshot.org/#/lido-snapshot.eth/proposal/0x9cf59093a927afe5ebd860a46aaeb92e67ff980168d95dce4c0fe2d5d46d2e68) that would be used to serve as a focal point for user stakes and DVT incentives.

Voting for this proposal would mean that:

1. The Mellow team would be responsible for the implementation of a vault that accepts ETH and stakes it to the Lido protocol with the goal of driving net-new stakes to the Simple DVT Module;
2. 90% of potential future Obol contributions and SSV mainnet incentives (both calculated off-chain) will be allocated to the vault, with the remaining 10% allocated to the Node Operators in their corresponding SSV & Obol Simple DVT clusters. Any potential Mellow incentives would be directed to users of the vault;
3. Cross-team coordination will take place to facilitate staking to the Simple DVT Module. Relevant data will be provided in support of off-chain contribution and incentive programs. 

## Background

In light of the [recently updated ReGOOSE goals](https://research.lido.fi/t/regoose-updated-goals-for-lido-in-the-light-of-mvi-and-restaking/7462), [Simple DVT Expansion proposal](https://research.lido.fi/t/proposal-expanding-the-simple-dvt-module/7549), and as discussed in the [De

====================================================================================================
[27] id=0xffb4042d3bfceef33c66f78c092a76fa8e1db198559d93798cc9db3fb4d722e7  token=LDO  space=lido-snapshot.eth  date=2024-08-01
TITLE: LIP-25: Staking Router 2.0
CHOICES: Yay | Nay
TEXT (first 1500 characters):
The proposal for Lido Staking Router 2.0 (SR) upgrade includes improvements to both on- and off-chain parts of the following components:

- the Deposit Security Module (DSM)
- the Validator Exit Bus Oracle (VEBO)
- the Accounting Oracle (AO)
- and reward distribution mechanisms in curated-based staking router modules.

If the DAO approves it, the new SR upgrade will be included in the further on-chain vote to be applied to the Lido protocol. Off-chain parts needed to support on-chain changes will be deployed just before the on-chain vote.

## TL;DR

Lido ValSet stream contributors propose to improve the Staking Router in multiple ways: 
* automate key vetting and unvetting (the process of ensuring only safely depositable keys are under limit) and handling of cases such as incorrect signatures, duplicate keys, and deposits front-run within Deposit Security Module; 
* allow staking router modules to signal Validator Exit Bus Oracle to exit validators independently of withdrawal requests using a new boosted exit mode; 
* adjust validator exit prioritization to account for each module’s target share for Validator Exit Bus Oracle; 
* and scale reporting and decouple reward distribution for Accounting Oracle 3rd phase report.

It is proposed to change on-chain contracts and off-chain parts of the Staking Router.

## Motivation

1. In the current implementation of the curated Staking Router modules, key vetting (the process of validating keys before making them depositable) occurs t

====================================================================================================
[28] id=0xd0d7bfd68f2241524dbb14ae6fe0e8414b9fe3e0dcfc50641a8d28f0067d6693  token=LDO  space=lido-snapshot.eth  date=2024-10-03
TITLE: Lido Community Staking Module Mainnet Release Setup
CHOICES: Approve CSM mainnet release | Reject CSM mainnet release
TEXT (first 1500 characters):
Lido Community Staking contributors are seeking the support of the Lido DAO members regarding the upcoming Community Staking Module release on the Ethereum mainnet.

## **TL;DR**

[Community Staking Module](https://research.lido.fi/t/community-staking-module/5917) (CSM) is the first-ever permissionless staking module built for the Lido on Ethereum staking protocol. Initially announced and [approved](https://snapshot.org/#/lido-snapshot.eth/proposal/0xa39815519107002997769f0b79a9e3957c3bf793166ab948fc6413ce5b3def55) for development in November 2023, the module has already demonstrated outstanding results on the [Holesky testnet](https://docs.lido.fi/deployed-contracts/holesky#community-staking-module).

**This snapshot aims to get signal approval from the Lido DAO members regarding CSM parameters, their configuration for use in the mainnet release, and the granting of some CSM management permissions to the CSM committee.**

## **CSM design**

As outlined in the original [forum post](https://research.lido.fi/t/community-staking-module/5917) and [snapshot vote](https://snapshot.org/#/lido-snapshot.eth/proposal/0xa39815519107002997769f0b79a9e3957c3bf793166ab948fc6413ce5b3def55), the main design features of CSM are:
> 1. Permissionless entry with [bond](https://docs.lido.fi/staking-modules/csm/join-csm#bond)
> 2. Only ETH (stETH) as a bond token
> 3. “Non-linear” bond scaling for Node Operators
> 4. First in, first out stake allocation queue
> 5. Performance oracle with performanc

====================================================================================================
[29] id=0xeedef9fea3d782f192410768cabaf6974da40ef36e1d22c7f8fff5fd4cfc7a59  token=LDO  space=lido-snapshot.eth  date=2024-11-21
TITLE: GOOSE 2024 cycle: Lido DAO goals for 2025
CHOICES: Adopt Goals | No action
TEXT (first 1500 characters):
## **Summary**

During the 2024 [GOOSE](https://snapshot.org/#/lido-snapshot.eth/proposal/0x58bbc5d540e46081043ef29d4d1ee56b7df4dc1b0369aa78e0c15a2403549353) (Guided Open Objective Setting Exercise) proposal window, only one proposal for the upcoming 2025 year was submitted: [Hasu's GOOSE-2 Submission](https://research.lido.fi/t/hasus-goose-2-submission-a-product-line-approach-to-grow-lido-s-staking-ecosystem/8841). Consequently, the **GOOSE 2024 cycle** proposal is to adopt Hasu's proposed set of goals.

## **GOOSE Framework Overview**

[GOOSE](https://snapshot.org/#/lido-snapshot.eth/proposal/0x58bbc5d540e46081043ef29d4d1ee56b7df4dc1b0369aa78e0c15a2403549353) is the Lido DAO's framework for adopting and reviewing 3-year objectives and 1-year goals. The first GOOSE Submission was approved in [November 2023](https://snapshot.org/#/lido-snapshot.eth/proposal/0x0fa423280ce2bcc2596901d81322716ad440c7581658030a7d21784c2661d81c) and adjusted [in May 2024 (reGOOSE)](https://snapshot.org/#/lido-snapshot.eth/proposal/0x300523518b08f20c585751c0a720ef3ec53698d4e5062154d285b15cb062f96c). The ongoing [GOOSE 2024 cycle](https://research.lido.fi/t/hasus-goose-2-submission-a-product-line-approach-to-grow-lido-s-staking-ecosystem/8841) is proposed to confirm long-term objectives and focuses on new 1-year goals. Reevaluation occurs yearly, ensuring regular assessment and continuity.

## **Context and Motivation**

The context, key challenges, and motivations for selecting goals are detailed i

====================================================================================================
[30] id=0x7569e4487b7737fa8e98fe708843deb014a61d0dbfeeb6e57ad1f4dba5494598  token=LDO  space=lido-snapshot.eth  date=2024-12-16
TITLE: Lido Alliance Grant Proposal
CHOICES: For | Against
TEXT (first 1500 characters):
The [EGG] Lido Alliance Grant Funding proposal seeks to continue the activities of the Lido Alliance BORG through 2025, aligning with [GOOSE-2](https://research.lido.fi/t/hasus-goose-2-submission-a-product-line-approach-to-grow-lido-s-staking-ecosystem/8841)

## tldr

- Continue Alliance BORG activities through 2025 in line with [approved](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0xa478fa5518769096eda2b7403a1d4104ca47de3102e8a9abab8640ef1b50650c) guidelines

## Basic Data

| Field | Description |
| --- | --- |
| **Proposal Name** | Alliance BORG 2025 |
| **Which of the following GOOSE goals is your proposal advancing?** | [Lido Alliance BORG](https://lidoallianceb.org/) is a Cayman Foundation organized to endorse, amplify and stand behind builders driven by the same vision of decentralized validation, and a universally accessible, censorship-resistant Ethereum. Advancing mainly "Expand stETH’s Ecosystem with a Diverse Product Line" from [GOOSE-2](https://research.lido.fi/t/hasus-goose-2-submission-a-product-line-approach-to-grow-lido-s-staking-ecosystem/) |
| **Organization description** | Cayman Foundation founded after an affirmative [DAO vote](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0xa478fa5518769096eda2b7403a1d4104ca47de3102e8a9abab8640ef1b50650c), currently serviced, following Borg approval, by [Captain Nemo](https://research.lido.fi/u/nemo/summary) |
| **Proposed scope of work** | Scouting, research, due diligence calls, coordination with Lido co

====================================================================================================
[31] id=0x8736420fd3ebecc1aae603c3a49d6805899c38b142c92525169e5bfa95f53b26  token=LDO  space=lido-snapshot.eth  date=2024-12-16
TITLE: [EGG] Multi-EGG Continuity Grant Funding
CHOICES: For | Against
TEXT (first 1500 characters):
## tldr

- Continue grant approvals to the Lido Contributors Group to advance towards Hasu’s [GOOSE](https://research.lido.fi/t/hasus-goose-submission-proposed-goals-for-lido-dao-to-consider/), [reGOOSE](https://research.lido.fi/t/regoose-updated-goals-for-lido-in-the-light-of-mvi-and-restaking/) goals and preparation ahead of updates to deliver [GOOSE-2](https://research.lido.fi/t/hasus-goose-2-submission-a-product-line-approach-to-grow-lido-s-staking-ecosystem/)
- Development, audit and deployment of Dual Governance (finalizing DAO Governance strategic initiative), along with preparing and enabling the permissionless CSM entry (continuing focus on Validator Set strategic initiative)
- Maintain rollout and node operator onboarding for Simple DVT and CSM modules
1. 11.1m DAI (or USDC, USDT hereinafter) in grant continuity for the Lido Contributor’s Group (Best-before date: 2025-03-31)
2. 8.5m DAI in grant continuity for Ecosystem Growth through Liquidity Observation Lab (Best-before date: 2025-06-30)
3. 2m DAI in continuity for the [Bug Bounty](https://immunefi.com/bug-bounty/lido/information/) program (Best-before date: 2025-12-31) to be drawn down only in the event of payout events

## Basic Data

| Field | Description |
| --- | --- |
| **Proposal Name** | Multi-EGG Continuity Grant Funding |
| **Which of the following GOOSE goals is your proposal advancing?** | 1: Lido has effective and decentralized governance, 2: Lido attracts the best validator set in the market, 3: stE

====================================================================================================
[32] id=0xb58527a05581849b3890ff226fa30f2b5e19f7742fe8f4f94e6c953fe0055c0e  token=LDO  space=lido-snapshot.eth  date=2025-03-17
TITLE: [EGG] Lido Labs BORG Foundation Grant Funding Request (Apr-Dec 2025)
CHOICES: For | Against
TEXT (first 1500 characters):
## tldr

Seek grant approvals through 2025-12-31 to the [Lido Labs BORG Foundation](https://research.lido.fi/t/establishment-of-lido-labs-borg-foundation-as-a-lido-dao-adjacent-foundation/9344) to advance protocol research, development, and governance initiatives with a focus on Lido v3 implementation, as well as facilitating maintenance of the Lido on Ethereum protocol.

## Basic Data

| Field | Description |
| --- | --- |
| **Proposal Name** | Lido Labs BORG Foundation Grant Funding Request (Apr-Dec 2025) |
| **Which of the following GOOSE goals is your proposal advancing?** | [GOOSE-2 goals](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0xeedef9fea3d782f192410768cabaf6974da40ef36e1d22c7f8fff5fd4cfc7a59): #1 Lido DAO Has Effective and Decentralized Governance; #2 Lido protocol Attracts the Best Validator Set in the Market; #3 stETH is the most used token in the Ethereum ecosystem |
| **Proposed scope of work** | Protocol R&D, Lido v3 Implementation, Dual Governance Development, Security Research, and facilitating maintenance of the Lido protocol |
| **Objectives** | 1. Drive technical research and development for Lido v3 Staking Infrastructure for a diverse product line, 2. Strengthening DAO Governance Infrastructure and Decentralization, 3. Advance Decentralization of Ethereum, 4. Lead Protocol Research Initiatives |
| **Total Budget Request and Best Before Dates** | Budget request includes $34.88m through 2025-12-31. |

## Lido Labs BORG Foundation Grant Funding Req

====================================================================================================
[33] id=0x90e2f9926e37867d2ef319a8ef7a0257bb5695086b64b88b43b43f00959a0047  token=LDO  space=lido-snapshot.eth  date=2025-03-17
TITLE: [EGG] Lido Ecosystem BORG Foundation Grant Funding Request (Apr-Dec 2025)
CHOICES: For | Against
TEXT (first 1500 characters):
## tldr

Seek grant approvals through 2025-12-31 to the [Lido Ecosystem BORG Foundation](https://research.lido.fi/t/establishment-of-lido-ecosystem-borg-foundation-as-a-lido-dao-adjacent-foundation/9345) to advance stETH adoption, liquidity, and utility, as well as LOL’s grant request for H2 2025.

## **Basic Data**

| **Field** | **Description** |
| --- | --- |
| **Proposal Name** | Lido Ecosystem BORG Foundation Grant Funding Request (Apr-Dec 2025) |
| **Which of the following GOOSE goals is your proposal advancing?** | [GOOSE-2 goal](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0xeedef9fea3d782f192410768cabaf6974da40ef36e1d22c7f8fff5fd4cfc7a59) #3 stETH is the most used token in the Ethereum ecosystem |
| **Proposed scope of work** | Integrations and DeFi use-cases, Institutional adoption, Liquidity optimization, marketing, education and communications |
| **Objectives** | 1. 30%+ of stakers use Lido protocol to stake; 2. Institutions use Lido protocol to stake; 3. Build brand awareness of stETH and Lido protocol |
| **Total Budget Request and Best Before Dates** | Budget request includes $10.61M through 2025-12-31, Liquidity Observation Lab’s grant ($8.5M for H2 2025). |

## **Lido Ecosystem BORG Foundation Grant Funding Request**

|  | **2. Validator Set** | **3. stETH Adoption** | **4. Support** | **Grand Total** |
| --- | --- | --- | --- | --- |
| **G&A** | 0.99m | 0.81m | 1.88m | 3.68m |
| **R&D** |  |  | 1.00m | 1.00m |
| **S&M** | 0.15m | 5.78m |  | 5.93m |
|

====================================================================================================
[34] id=0xf752b2dbc9cf8693abf01b29938d7f7e0dd7e1ebe088583fd61da7641b870a36  token=LDO  space=lido-snapshot.eth  date=2025-03-26
TITLE: Re-endorsement of wstETH on Starknet
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Introduction

The Starknet Foundation is excited to introduce a proposal to re-endorse the wstETH bridge endpoints as canonical by the Lido DAO.

For context into the prior proposal that was passed, please view [here](https://research.lido.fi/t/wsteth-deployment-on-starknet/6335); and for further context into the asset’s offboarding, please view [here](https://research.lido.fi/t/nec-1-recognition-of-wsteth-bridge-endpoints-on-starknet-as-canonical/8956/5). For clarity, this issue occurred after the passing of the proposal and posed zero risk to holders.

Following the previous wstETH offboarding, the Starknet Foundation proceeded with an asset migration from wstETH(legacy) to the new wstETH following the recommended [guidline](https://docs.lido.fi/token-guides/wsteth-bridging-guide/).

That migration is now complete.

Upon the passing of this proposal, the governance roles for wstETH will be transferred to the Lido DAO.

# wstETH Metrics

The wstETH migration process began on 3 February through the [migration hub](https://wstethmigration.starknet.io/).

There is now ~3360 cumulative wstETH (new and old) on Starknet, with ~89% of all wstETH on Starknet being the new token. Migrations of legacy wstETH continue to take place.

These metrics can be verified in real-time: [new wstETH](https://starkscan.co/token/0x0057912720381af14b0e5c87aa4718ed5e527eab60b3801ebf702ab09139e38b) and [legacy wstETH](https://starkscan.co/token/0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c

====================================================================================================
[35] id=0x3ecd09e4c0f22d25c711ca5777c49c22d144385b85dd7f696ca6cc66cc0ca157  token=LDO  space=lido-snapshot.eth  date=2025-04-21
TITLE: Increasing LOL Easy Track Limits to align with Grant Requests
CHOICES: For | Against
TEXT (first 1500 characters):
### **TLDR**

The Lido Ecosystem BORG Foundation (the “**Foundation**”) proposes changing the Easy Track limits in relation to the [Liquidity Observation Lab multisig](https://docs.lido.fi/multisigs/committees#281-liquidity-observation-lab-committee-ethereum) to 6,000 stETH for every 6 months (instead of 2,100 for every 3 months) to reflect the Foundation’s funding needs. This change aims to align on-chain security constraints with operational needs.

### **Current status**

Under [existing Easy Track factories](https://docs.lido.fi/deployed-contracts/#easy-track-factories-for-token-transfers), funds from the Treasury can be transferred to the [Liquidity Observation Lab multisig](https://docs.lido.fi/multisigs/committees#281-liquidity-observation-lab-committee-ethereum) under a security limit of **2,100 stETH for every 3 months**.

By [Snapshot](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0x8736420fd3ebecc1aae603c3a49d6805899c38b142c92525169e5bfa95f53b26) ending 23 December 2024, DAO voters approved the Lido Ecosystem BORG Foundation’s funding request for the Liquidity Observation Lab of 8.5M for **H1 2025,** and by [Snapshot](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0x90e2f9926e37867d2ef319a8ef7a0257bb5695086b64b88b43b43f00959a0047) ending 24 March 2025, the Foundation was granted a total of $8.5M for the Liquidity Observation Lab from 2025-07-01 through 2025-12-31 (”**Grants**”).

With the existing 3-month limit of 2,100 stETH (roughly $3.4M at today’s pr

====================================================================================================
[36] id=0xcd1c1a051888efd495d97458ae9fa4fe5198616eb3d92a71d3352d9f25e79c4e  token=LDO  space=lido-snapshot.eth  date=2025-04-21
TITLE: CSM: stakeShareLimit and keyRemovalCharge parameters adjustment
CHOICES: For | Against
TEXT (first 1500 characters):
In the light of active development and [preparations](https://research.lido.fi/t/community-staking-module/5917/90) for Community Staking Module (CSM) v2 it is proposed to adjust several parameters for the current version of CSM, namely: increase `stakeShareLimit` from 2% to 3% upon reaching certain conditions and reduce `keyRemovalCharge` from 0.05 ETH to 0.02 ETH.

## 1. Increase `stakeShareLimit` to 3%

CSM has [reached](https://operators.lido.fi/module/3) its stake share limit of 2%. This means that new validators in CSM can be deposited to only if the total Lido protocol TVL increases or some of the current validators exit. This fact limits the future growth of the Lido on Ethereum Node Operator set. Currently, it is estimated that about 50 net-new Node Operators are in the CSM deposit queue.

**Proposal: If the below-stated conditions are met, increase the CSM stake share limit (`stakeShareLimit`) from the current 2% to 3%.**

To maintain consistency of the stake share limit parameters in the Staking Router, it is also proposed to set the `priorityExitShareThreshold` to 375 BP (3.75%) to maintain the [existing ratio](https://research.lido.fi/t/community-staking-module/5917/86).

**Conditions for further on-chain implementation:**

Proceeding with a change to the CSM stake share limit should take into account stake distribution across other Lido on Ethereum modules:

- SimpleDVT module should have all of the [depositable validators](https://operators.lido.fi/module/2) dep

====================================================================================================
[37] id=0xc67103e65d8bb4e088ddb89e0a7654fa56db5f0162f5870fca41c5dabd937f11  token=LDO  space=lido-snapshot.eth  date=2025-04-21
TITLE: Lido Alliance application: Twyne
CHOICES: For | Against
TEXT (first 1500 characters):
## **Summary**

[Twyne](https://x.com/twynexyz) is a credit delegation protocol built on top of existing lending markets. It enables lenders to delegate their unused borrowing capacity in exchange for yield, creating additional credit lines and unlocking new strategies on top of lending protocols. The proposal asks for the onboarding of the Twyne Protocol to Lido Alliance.

## **Envisioned Agreement or Terms**

### From Twyne
- Ethereum-alignment and commitment to decentralize validation
    - stETH gains wide adoption as a base token within Twyne, the growth of credit delegation will directly contribute to expanding stETH’s role as collateral across DeFi. This not only enhances capital efficiency but also strengthens Ethereum’s decentralization by supporting a more diverse set of node operators through increased stETH demand.
- Twyne expands the use cases for stETH in DeFi:
    - stETH holders can underwrite various cases and get liquidation incentives passively by absorbing liquidated positions using their idle borrowing capacity.
    - Enables higher-leverage staking strategies by providing access to additional credit lines via delegated borrowing power.
- Use-case for other Lido Alliance members
    - Credit delegation enables leverage to be extended to virtually any token. Within the Lido Alliance, this includes liquid restaking tokens (LRTs), yield strategies from other protocols, and governance tokens of member projects.
- Token and revenue allocation
    - 10% of the

====================================================================================================
[38] id=0xf7b718e7807f763ba826735781145dd06b79b0228b37b74a22dd5ac252e03c40  token=LDO  space=lido-snapshot.eth  date=2025-05-21
TITLE: Community Staking Module v2. Architecture and Fee Structure
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal outlines the architecture description and staking rewards allocation (fee structure) for the proposed major upgrade of the Lido [Community Staking Module](https://operatorportal.lido.fi/modules/community-staking-module) called CSM v2.

## Motivation

The [current version of CSM](https://blog.lido.fi/lido-community-staking-an-overview/) has been immensely successful in pushing the decentralization of Lido on Ethereum. It allows Node Operators to join the Lido on Ethereum protocol permissionlessly and receive Node Operator rewards without needing to put up the entire 32 ETH minimum of a validator. However, some limitations and challenges remain that need to be addressed to make CSM more robust, flexible, and competitive.

One of the main challenges is the need to support different types of Node Operators, such as permissionless operators, identified community stakers, professional Node Operators, etc to allow for an incentive separation between these groups. One of the main incentives that CSM offers to Node Operators is Node Operator rewards. Currently, CSM allocates 6% of the staking rewards (pro-rata based on the share of active validators operated by each Node Operator within the module)  to Node Operators. These conditions make the CSM reward structure way above the current permissionless staking solutions in terms of the bond required to rewards ratio and should be adjusted to fit the market.

## CSM v2 Architecture

CSM v2 is a major upgrade of the currentl

====================================================================================================
[39] id=0x8b6addc4be1a9ef4b2a1591be5ac4909aa82c868cd9b7871494b626539a99a8e  token=LDO  space=lido-snapshot.eth  date=2025-06-23
TITLE: Proposal for Updating Block Proposer Rewards Policy to Lido on Ethereum SNOP on Block Proposals v3
CHOICES: For | Against
TEXT (first 1500 characters):
### Summary

This proposal seeks the community’s support to update the currently in effect [Block Proposer Rewards Policy v2](https://lido.mypinata.cloud/ipfs/QmaLLjLE2iecf59kTQSVC1rHVPjjQwGDTCouR8A871BNRY) (approved by the [Snapshot](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0x7ac2431dc0eddcad4a02ba220a19f451ab6b064a0eaef961ed386dc573722a7f) vote) to the proposed [**Standard Node Operator Protocol (SNOP) on block proposals v3**](https://lido.mypinata.cloud/ipfs/bafybeicufs7hxrrtbkjtcoeal7oiculx4cns7nyyez7qkximfnnjnbfgay) ([diff-view](https://github.com/sssngth/documents-and-policies/compare/fbff4fed860aa79e3d6eec9d839d2e728434c080...220b0ce3ae9b42c042d18ee5fa6dd08524884b3e)).

### Context & Motivation

The current version of the Block Proposer Rewards Policy dates back to when Ethereum’s block proposal pipeline was less complex, Lido protocol was still monolithic, and out-of-protocol proposer-builder separation in the form of MEV-Boost had not yet been fully rolled out to the protocol.

Given the advancements since then — Pectra and Staking Router 2.0, the upcoming [Lido v3](https://research.lido.fi/t/lido-v3-whitepaper-rfc/10124) and [CSM v2](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0xf7b718e7807f763ba826735781145dd06b79b0228b37b74a22dd5ac252e03c40) upgrades, as well as features like Auxiliary Proposer Mechanisms (APMs) and Triggerable Withdrawals — this proposal aims to ensure the SNOP accurately reflects the current state and lays the groundwork for t

====================================================================================================
[40] id=0x4267fe277e52a3550e82286af96948a258392ddd303df6b479c4d8f4664acdd0  token=LDO  space=lido-snapshot.eth  date=2025-09-22
TITLE: NEST - Network Economic Support Tokenomics
CHOICES: Approve | Reject
TEXT (first 1500 characters):
## **Summary**

NEST is a modular mechanism that, when supplied with stETH, enables those stETH to be swapped for LDO via [STONKS](https://research.lido.fi/t/lido-stonks-treasury-swaps-via-optimistic-governance/) and routes the LDO back to the Lido DAO Treasury, effectively taking it out of circulation. The net effect it has is essentially to change the respective share over governance rights that holders enjoy, including over future ‘value distribution’ proposals.

This proposal requests approval of the concept of the NEST mechanism and further research and design, while final designs and actual use of NEST will be decided in a future proposal once it is ready.

![nest updated.png](ipfs://bafkreih2fxb2q422gqsk3ahpajc2m657czg6lfe3zu2d7okbn72kx6qxq4)

## **Introducing NEST**

NEST proposes a modular and future-proof system that allows triggering repurchases of LDO and can provide programmatic enforcement guarantees to token holders for the future. As written, it would require Aragon DAO votes for specific quantums of stETH to be deposited in NEST to activate. The idea is that a future, automated, module could ‘feed’ the NEST with stETH under any other parameters, including automated ones.

Any stETH available in NEST is subject to have 1 STONKS Cowswap order created for it at a minimum every 7,000 blocks, or approximately once a day. The maximum order size possible is configurable through an Aragon DAO vote and should aim to avoid slippage greater than 1% in a single transacti

====================================================================================================
[41] id=0xc87e56b48594d0a5560a959ac32252f86464966a5a9d6ea86ef189d842d9328a  token=LDO  space=lido-snapshot.eth  date=2025-10-31
TITLE: Lido Ecosystem Grants Organization (LEGO) — Framework Update 1 October 2025
CHOICES: For | Against (no changes)
TEXT (first 1500 characters):
## Summary

This proposal introduces several updates to the Lido Ecosystem Grants Organization (LEGO) framework, reflecting operational learnings and spending patterns over the past two years.

The changes aim to optimize fund allocation, simplify the budget structure, and refresh the LEGO Council composition.

If voted for, these changes will take effect on 1 October 2025, 00:00 UTC.

## Motivation

[LEGO](https://lido.fi/lego) has consistently supported ecosystem initiatives in research, development, and community growth. [LEGO Quarterly Reporting](https://lego.lido.fi/lego-quarterly-reporting) provides more details about the grants’ history.

Having reviewed LEGO’s activity and spending data, the LEGO Council identified several proposed adjustments to improve efficiency and ensure better budget accuracy.

## Proposed Changes

### 1. Adjust Quarterly Budget

- Before: $500,000 per quarter
- Going forward: $250,000 per quarter
- Applicability: effective for grants initiated after 1 October 2025, 00:00 UTC

**Rationale:** Historical spending data shows LEGO’s actual quarterly disbursements rarely exceeded $250k. Reducing the quarterly cap will align it better with observed spending trends while maintaining sufficient flexibility for grantmaking.

### 2. Budget Composition — USD-pegged Stablecoins Only

- Remove the LDO token allocation, maintaining the LEGO budget solely in USD-pegged stablecoins (e.g., USDC, USDT on Ethereum mainnet), subject to availability and compliance.

====================================================================================================
[42] id=0x4dd947f5e73377b074fd393148b377558179f22ea923d584dd3c718f3bab0687  token=LDO  space=lido-snapshot.eth  date=2025-11-24
TITLE: Conversion of Treasury Stablecoins into sUSDS or TMMFs
CHOICES: Approve | Reject
TEXT (first 1500 characters):
## **TL;DR**

This proposal requests the DAO’s approval to execute the TMC-6 strategy and handle the related operations to allow the DAO to generate returns on its stablecoin holdings.
## **Proposal details**

The [Treasury Management Committee](https://docs.lido.fi/multisigs/committees#25-treasury-management-committee) (”TMC”) has approved the [TMC-6 strategy](https://research.lido.fi/t/tmc-6-convert-dao-treasury-stablecoins-into-susds-and-update-config-on-easy-track-and-aragon-finance-accordingly/10868) to allow the DAO to generate returns on its stablecoin holdings (currently ~USD 30M in idle stablecoins). Under this strategy, stablecoin funds could be withdrawn from the DAO Treasury and subsequently converted into sUSDS or a tokenized USD money market fund of choice.

While the TMC is authorized to approve automated strategies that require further on-chain DAO confirmation and allow the DAO to object to execution, this particular strategy is not automated. This proposal seeks explicit DAO confirmation that the TMC and the Lido Labs Foundation and Lido Ecosystem Foundation (together the "Foundations") are authorized to execute the strategy and carry out the associated operational steps. This confirmation is limited to the specific strategy, parameters, and guardrails set out in TMC-6 and this proposal, and the TMC together with the Foundations will act solely as implementation agents within these predefined limits, without independent discretion to manage, reallocate, or o

====================================================================================================
[43] id=0x3a5d10fcd3fad6d5ccf05f5bd49244046600ad9cbed9a5e07845200b3ae97e09  token=LDO  space=lido-snapshot.eth  date=2025-11-24
TITLE: Curated Module Fee Changes
CHOICES: For | Against
TEXT (first 1500 characters):
## Tl;Dr

[This proposal](https://research.lido.fi/t/proposal-curated-module-fee-changes/10876) seeks to adjust the fee structure for Node Operators in the current Curated Module (CM or CMv1) of the protocol in light of two key factors: (1) proposed changes that will be brought by Staking Router v3 and Curated Module v2 (see “[Contributor Thoughts on the Future of Lido Core](https://research.lido.fi/t/contributor-thoughts-on-the-future-of-lido-core/10616)”), and (2) increasing competition in the Ethereum staking market. 

In the current staking market conditions (with some Node Operators offering to run validators for fees as low as 1-3% of staking rewards), there is a clear need for the protocol to remain attractive to participants while continuing to support ecosystem growth and decentralization initiatives.

As such, it is proposed to adopt the following interim fee structure for the CM for three categories of operators: 

- Standard Tier: baseline fee-share set to 3.50%
- Extra Effort Tier: baseline fee-share set to 4.00%
- Client-Team Tier: baseline fee-share set to 4.50%

The overall Lido protocol fee of 10% of staking rewards would remain unchanged.

## Background

As noted in the [Future of Lido Core proposal](https://research.lido.fi/t/contributor-thoughts-on-the-future-of-lido-core/10616), significant resources of the Lido DAO have been allocated to continuing to decentralize and harden the protocol with new features such as permissionless staking via the Community

====================================================================================================
[44] id=0xf263b730f1c64d637ec27227121d7c5bd2189bf456514bad8225e960cf34d7b0  token=LDO  space=lido-snapshot.eth  date=2025-12-11
TITLE: Ecosystem Grant gRequest (EGG): Executing GOOSE-3
CHOICES: Approve 2026 EGG | Reject 2026 EGG
TEXT (first 1500 characters):
## **TLDR**

This 2026 Ecosystem Grant gRequest (“EGG”) sets out the funding required to execute [GOOSE-3](https://research.lido.fi/t/lido-labs-goose-3-lido-s-next-chapter/10927) strategic plan for 2026 to support the Lido DAO (the “DAO”) in furthering the Lido protocol (“Lido” or “Protocol”).

## **Key Highlights**

- The 2026 Ecosystem Grant Request (EGG) is submitted to ensure protocol resilience, security, and continuity, and to support Lido DAO’s long-term treasury growth.
- The 2026 EGG is a consolidated submission from Lido Labs Foundation, Lido Ecosystem Foundation, and Lido Alliance BORG (collectively the “Foundations”), aligning their mandates and execution plans to maintain protocol operations and deliver the proposed [GOOSE-3](https://research.lido.fi/t/lido-labs-goose-3-lido-s-next-chapter/10927) goals:
    - Expand the Staking Ecosystem
    - Ensure Protocol Resilience: Lido Core Upgrade
    - Scale New DAO Revenue Streams: Lido Earn
    - Explore Vertical Expansion and Real-World Business Applications
- This request is structured into Core — for protocol maintenance, and Growth — for new strategic initiatives with low-variance and high-variance components.
- The Foundations request $60.0M in total:
    - $43.8M baseline amount ($26.9M – Core; $16.9M – Growth)
    - $16.2M discretionary amount cap under the Growth Part
- Projected baseline revenue amounts to $50.0M, with upside potential from Growth initiatives and allocation of discretionary expenses.
- Project

====================================================================================================
[45] id=0x8b8619f09213b868708b25cb2512023234e5e160cba5c291f4e9d944d2ccd3fa  token=LDO  space=lido-snapshot.eth  date=2026-01-19
TITLE: DVT & DVV Incentive Allocation Changes
CHOICES: For | Against
TEXT (first 1500 characters):
## Summary
This proposal introduces a variable incentive allocation model for Distributed Validator Technology (DVT) incentives accrued to the Lido protocol, split between Node Operators and the Mellow Distributed Validator Vault (DVV). The proposed new mechanism aims to better reflect the real costs of operating DVT‑based validators under current market conditions for Node Operators in the Curated Module (CM) and the Community Staking Module (CSM).

Instead of a fixed incentive split, Node Operator and Mellow DVV staker allocations would adjust dynamically based on the [SSV](https://ssv.network/) Network Fee and total incentives accrued. This is intended to support sustainable Node Operator economics and allocation to stakers:

- when DVT operating costs are high relative to incentives, the Node Operator share increases (up to 50%);
- when incentives increase or DVT costs decrease, the Node Operator share declines, and more incentives flow to stakers (up to 85%).

The SSV Network Fee and the SSV [Incentivized Mainnet Program](https://ssv.network/incentivized-mainnet) (IMP) will be viewed as a proxy for certain costs associated with running DVT validators. The proposed share split of the incentives is intended to be equally distributed for Node Operators utilizing either SSV or Obol DVT technology. No changes are proposed to the Simple DVT Module, as DVT provider fees for this module are currently expected to be covered via Node Operator validation rewards.

## Background

Th

====================================================================================================
[46] id=0xb4a35720b03f4c888c2fb41ab66ed324262d7a5b4696ffc3ee20bb35ebb0df6f  token=LDO  space=lido-snapshot.eth  date=2026-01-19
TITLE: Rewards Share Committee Reform
CHOICES: For | Against
TEXT (first 1500 characters):
### TL;DR

Reform and relaunch the Rewards Share Committee (”Committee”) as DAO-authorized operational committee to align with [GOOSE-3 goals](https://snapshot.org/#/s:lido-snapshot.eth/proposal/0x9504d26771291e011ff54c2e0d7665e79621aa0225c0d573697f1c4061401938). This proposal updates the Committee mandate and process, including adding support of the stVaults which were introduced with [Lido V3](https://snapshot.org/#/s:lido-snapshot.eth/proposal/0x01cd474645cc7c3ddf68314d475d421ef833499297f508fee5f7411fafff3954), as well as operational functions to help execute the changes approved to Curated Module processes, and updates Committee configuration.
The full updated version of the Rewards Share Program is available on the [Research Forum](https://research.lido.fi/t/rewards-share-program-committee-updates/11107/2).

### Background

- The DAO approved the creation of the Committee in 2022 to support targeted rewards for Ethereum stake growth.[[1]](https://research.lido.fi/t/setup-lido-referral-program-committee-and-use-easy-track-for-the-payouts-ethereum/1808)
- Over time, the program evolved in naming and process, while its core goal stayed the same: targeted initiatives that seek to grow the adoption of stETH by fostering high-quality and secure ecosystem development.
- Given the updated goals approved by the DAO via GOOSE-3 and the launch of Lido V3, the Rewards Share Committee should receive an update to its mandate, processes and configuration.

## Proposal

The Committee wi

====================================================================================================
[47] id=0xd32eab4ce41e2754d8a51fdf89bd9f4eb43ecbeb7b60d0e93ce84bc3e4d4c8a3  token=LDO  space=lido-snapshot.eth  date=2026-03-02
TITLE: Authorize $5M DAO Treasury Allocation to Lido Earn ETH and USD Vaults
CHOICES: For | Against
TEXT (first 1500 characters):
## TL;DR

This proposal requests a "skin-in-the-game" one-time $5M DAO Treasury allocation (requested in stETH equivalent) into the planned new [Lido Earn](https://research.lido.fi/t/lido-labs-goose-3-lido-s-next-chapter/10927#p-23526-h-2221-scale-new-dao-revenue-streams-lido-earn-10) vaults: **Lido Earn ETH Vault** and **Lido Earn USD Vault**. The purpose of this allocation is to:

- **Establish visible commitment** by having LDO token holders allocate a fixed portion of Treasury funds into the planned Lido Earn vaults alongside users under the same conditions, sharing the same upside and downside with transparent alignment.
- **Support Lido Earn growth** by reducing trust friction for new depositors and reinforcing transparency by making alignment and incident response posture verifiable on-chain, thereby increasing trust in Lido Earn vaults and enabling it to scale sustainably over time.

The proposal also introduces operational controls, including a first-loss mechanism that allows DAO-held vault shares to be burned (up to 100%) in severe, confirmed incident scenarios. This mechanism is intended to absorb losses in defined incident cases, thereby reducing the impact on other vault users.

The authorization is strictly limited to vault allocations and necessary execution costs. No funds may be used for incentives, marketing, grants, or operational expenses. This allocation is separate from the **[2026 Ecosystem Grant gRequest (EGG)](https://research.lido.fi/t/2026-ecosyste

====================================================================================================
[48] id=0x1d416954538fb9b82aae05daca1be29f7b20d5f9fac61bd2eb9da1f5901a3867  token=LDO  space=lido-snapshot.eth  date=2026-04-06
TITLE: Introduce an Identified DVT Cluster type in the Community Staking Module
CHOICES: For | Against
TEXT (first 1500 characters):
## TL;DR

This proposal introduces a new CSM Node Operator type — Identified DVT Cluster (IDVTC) — allowing groups of 4 Identified Community Stakers (ICS) to run validators collaboratively using DVT. The design combines the trust guarantees of ICS with the resilience of DVT, offering improved capital efficiency while maintaining strict eligibility requirements and DAO oversight. For full proposal details, please refer to the [Research Forum](https://research.lido.fi/t/community-staking-module/5917/188).

## Background and Motivation

While the Community Staking Module (CSM) [already supports permissionless DVT-based validator operation](https://docs.lido.fi/run-on-lido/csm/node-setup/DVT-setup/), it does not currently offer a capital-efficient path tailored to independent DVT clusters. At the same time, DVT adoption across the Lido protocol has continued to grow, and the [Identified Community Staker (ICS) operator type](https://research.lido.fi/t/community-staking-module/5917/141) has also seen strong demand from stakers willing to operate under more economically attractive conditions. The proposed IDVTC type builds on both developments by combining the resilience benefits of DVT with the trust assumptions of ICS, creating a more suitable framework for small independent operators running validators collaboratively.

## Proposal

This proposal introduces a new Node Operator type in the CSM: the Identified DVT Cluster (IDVTC), which will allow clusters of 4 verified, independen

====================================================================================================
[49] id=0x60cfe3531cd13ab84f5f6aaef7bcaab1747cbea4544dc7d18daaf642e36c9d39  token=LDO  space=lido-snapshot.eth  date=2026-04-06
TITLE: Redirect DVT & APM Incentives to Current Meta Treasury and LoL
CHOICES: Support | Reject
TEXT (first 1500 characters):
## Proposal Summary

This proposal aims to formalize the change in destination and utilization of post-Node Operator share of DVT incentives and APM incentives flows, and seeks DAO approval to:

- Redirect post-Node Operator share of DVT incentives flow arising from Obol and SSV Network providers (allocated under the recently [approved terms](https://snapshot.box/#/s:lido-snapshot.eth/proposal/0x8b8619f09213b868708b25cb2512023234e5e160cba5c291f4e9d944d2ccd3fa)) from the Decentralized Validator Vault to the Lido Earn Current Meta Treasury multisig to support Lido Earn ETH vault strategies.
- Route APM incentives flow to the [Liquidity Observation Lab](https://research.lido.fi/t/liquidity-observation-lab-lol-liquidity-strategy-and-application-to-curve-steth-eth-pool/5335) multisig to make them available to the [Growth Committee](https://research.lido.fi/t/rationalizing-liquidity-observation-lab-rewards-share-committee-growth-committee/10133) for agile deployment and continuous support of liquidity-focused strategies that contribute to the overall health of the stETH ecosystem.

## DVT Incentives

The Decentralized Validator Vault (DVV), implemented by Mellow, was launched in August 2024 as a coordination layer for user stake and Distributed Validator Technology (DVT) provider incentives. Among its primary goals was providing DVV stakers with access to Obol and SSV Network incentive programs they could not access directly.

Under the current setup, user deposits of ETH or WETH a

====================================================================================================
[50] id=0x1c929502f12c61a510c71965d7a7f82dcc76b5d812e2f52796f6bacd6f66e32b  token=LDO  space=lido-snapshot.eth  date=2026-04-06
TITLE: From LNOSG to CMC: Evolving Curated Staking Modules Governance
CHOICES: Support | Reject
TEXT (first 1500 characters):
## TL;DR

The proposal introduces the Curated Module Committee (CMC) as a dedicated body to handle the day-to-day operations of Lido’s Curated Modules in light of the upcoming [Curated Module v2](https://research.lido.fi/t/future-of-the-curated-module-cmv2-landscape/10929) (CMv2). The CMC is proposed to be granted governance authority over CMv2, oversight of CMv1 and Simple DVT Module (SDVTM), and the responsibilities currently performed by LNOSG (Lido Node Operator Sub-Governance Group), which will be deprecated. The CMC will operate via a multisig and handle routine operational tasks (e.g., penalties, parameter updates, registry management, and operator administration) within defined on-chain permissions. DAO oversight is preserved through Snapshot votes for high-impact decisions (such as Node Operator onboarding) and the Easy Track objection mechanism for routine actions.

## Background

The upcoming Curated Module v2 (CMv2) introduces new governance capabilities, enabling a shift toward a structured, committee-driven operational model with delegated on-chain permissions (see [CMv2 LIP](https://github.com/lidofinance/lido-improvement-proposals/blob/develop/LIPS/lip-33.md)). This enables more granular governance-based operational processes, resulting in a more advanced but operationally demanding model with recurring actions related to penalties, parameter updates, registry management, and operator administration.

The [Lido Node Operator Sub-Governance Group (LNOSG)](https

====================================================================================================
[51] id=0x43be9ee8ce820d444f706e9dd763a223ebabf37be27931cc056888e6c2e48814  token=LDO  space=lido-snapshot.eth  date=2026-04-06
TITLE: Authorize LDO Accumulation Program for up to 10,000 stETH
CHOICES: For | Against
TEXT (first 1500 characters):
## TL;DR

The proposal seeks to authorize the [Lido Growth Committee](https://research.lido.fi/t/rationalizing-liquidity-observation-lab-rewards-share-committee-growth-committee/10133) to execute a one-time LDO accumulation program using up to 10,000 stETH from the Lido DAO Treasury.

Execution will be facilitated by the Lido Ecosystem Foundation and carried out by the Growth Committee, with discretion over execution timing and venues within predefined constraints, provided current market conditions prevail. Execution will be conducted in 1,000 stETH batches obtained from the Treasury via Easy Track, with predefined price caps, ≤3% slippage limit, and full DAO oversight across tranches.

All acquired LDO tokens will be transferred to the Treasury, with detailed reports to be published on the Research Forum by the Growth Committee upon completion of each batch.

## Disclaimer

This proposal is not an addition, specification, or replacement for [Liquid Buybacks: NEST execution with LDO/wstETH liquidity](https://research.lido.fi/t/liquid-buybacks-nest-execution-with-ldo-wsteth-liquidity/10894) proposal. Unlike the proposed one-time initiative, which aims to capitalize on a recent market opportunity, NEST aims to establish a long-term automated solution to acquire LDO based on protocol performance and ETH price, and to improve on-chain liquidity.

This proposal is separate from the [2026 Ecosystem Grant gRequest (EGG)](https://research.lido.fi/t/2026-ecosystem-grant-grequest-egg-

====================================================================================================
[52] id=0x5629f9b201f32dbd5780f7e2e5601eed7504cdb7919b622a7ef039261d3c671a  token=LDO  space=lido-snapshot.eth  date=2026-04-30
TITLE: Authorize Lido EarnETH Loss Coverage Below 1% Threshold For The Kelp Incident
CHOICES: For | Against
TEXT (first 1500 characters):
## TL;DR

Lido Earn contributors request DAO authorization to use the [Lido Earn first-loss mechanism](https://snapshot.org/#/s:lido-snapshot.eth/proposal/0xd32eab4ce41e2754d8a51fdf89bd9f4eb43ecbeb7b60d0e93ce84bc3e4d4c8a3) to cover Kelp-related losses incurred by Lido EarnETH users, even if such losses are below the previously approved 1% threshold. This is a one-off, Kelp-specific exception intended to support Lido Earn's continuity and user confidence.

## Motivation

The April 2026 Kelp rsETH incident (LayerZero exploit) resulted in a material rsETH backing shortfall and triggered broader cross-protocol dislocation across DeFi. In response, a coordinated initiative — [DeFi United](https://defiunited.world) — has been established to cover the rsETH deficit. However, even in the case of full coverage, Lido EarnETH vault users remain exposed to residual losses arising from elevated borrowing costs in leveraged positions, estimated at approximately 400–600 ETH, depending on the time required for the Kelp protocol to resume normal operations.

Lido DAO previously approved a [first-loss mechanism for Lido Earn](https://snapshot.org/#/s:lido-snapshot.eth/proposal/0xd32eab4ce41e2754d8a51fdf89bd9f4eb43ecbeb7b60d0e93ce84bc3e4d4c8a3) with a 1% loss threshold, which may limit its applicability to Kelp-related losses. However, given the irregular nature of the Kelp incident and Lido DAO’s commitment to supporting Lido Earn users, covering residual losses even if they fall below the 1%

====================================================================================================
[53] id=0x022e901a6368573d18b150eecda563dd2ee17ad2aa6a0ef9772151cc7ba55187  token=LDO  space=lido-snapshot.eth  date=2026-05-11
TITLE: NEST: Automated LDO Buyback and Liquidity Provisioning
CHOICES: For | Against
TEXT (first 1500 characters):
## TL;DR

This proposal seeks DAO approval for the final design and implementation of **NEST** — a rule-based mechanism that creates an on-chain link between Lido protocol performance and LDO. If staking revenue exceeds an operating baseline, NEST can convert a bounded share of that surplus into LDO via CoW Swap. In the currently proposed Liquidity Provisioning (LP) mode, purchased LDO is paired with wstETH and deployed as DAO-owned liquidity in a Curve LDO/wstETH pool (LP tokens remain DAO-owned). NEST is automatic, permissionless, capped, and protected by emergency pause controls. The full NEST design is specified in [LIP-36](https://github.com/lidofinance/lido-improvement-proposals/blob/develop/LIPS/lip-36.md).

## Mechanism Design

NEST is a deterministic on-chain system that can permissionlessly convert a bounded share of protocol revenue into LDO via CoW Swap using [Stonks v2](https://github.com/lidofinance/lido-improvement-proposals/blob/develop/LIPS/lip-36.md#stonks-v2). Execution is permissionless: the NESTController contract funds orders from its stETH balance, with parameters computed on-chain based on current surplus and limits. In LP mode (proposed initial configuration), the surplus share is split equally between LDO purchases and corresponding wstETH pairing and deployed as LDO/wstETH DAO-owned liquidity in a Curve v2 NG pool. In Treasury mode, the full surplus share would instead be converted into LDO and transferred directly to the DAO Treasury. Switching mod

====================================================================================================
[54] id=0x517a6972a1b5ac20b4237b83a794f1ec4230ebe2cd35c293d6c03dafee40980f  token=LDO  space=lido-snapshot.eth  date=2026-09-21
TITLE: Proposal for Comprehensive Expense Optimization and NEST/stETH Buyback Parameter Restructuring
CHOICES: For | Against
TEXT (first 1500 characters):
I am putting forward a comprehensive proposal for community discussion and subsequent Snapshot voting. The goal is to aggressively optimize the DAO’s operational expenditures and realign our token support mechanisms with current market realities.

1. Independent Financial Audit
Proposal: Commission a full, external financial audit of all Lido DAO expenses and grant distributions for the 2025–2026 fiscal periods.Execution: Engage an independent, reputable Web3 auditing firm to identify inefficiencies, redundant outlays, and hidden costs.

2. Operational Downsizing (Lido Labs)
Proposal: Implement a 50% reduction in workforce across Lido Labs.

Rationale: In light of shifting market shares and intense competition in the institutional staking sector, our current burn rate is unsustainable. This restructuring will instantly lower our ongoing OpEx and safeguard the treasury.

3. NEST Buyback Framework Reform
The current NEST smart-contract parameters are overly restrictive. We propose modifying the revenue triggers to reflect the new economic baseline:

Lower Revenue Trigger: Reduce the annualized protocol revenue threshold required to activate buybacks from $40M to $30M.

Dynamic ETH Target: Lowering the baseline revenue trigger to $30M (combined with the OpEx cuts from Sections 1 and 2) will naturally depress the calculated ETH price activation floor well below the current $2,730 mark.

Aggressive Accumulation: Direct 100% of all protocol revenue generated above the new $30M thre

====================================================================================================
[55] id=0x415d54c2b9c85d9b4b631ab2f2b9a9aebfeaddb5cd116e0d0d742db0e51f7236  token=LISTA  space=listavote.eth  date=2024-08-16
TITLE: LIP-001:  Convert Protocol fees into LISTA Tokens for Distribution under Community Incentives
CHOICES: Yes | No
TEXT (first 1500 characters):
### Summary:
This proposal seeks to convert all existing community incentive rewards that come from **Protocol fees** into LISTA tokens, which will be bought on the open market and distributed to veLISTA holders. The conversion will streamline reward distribution and enhance liquidity within the Lista DAO ecosystem. 

This proposal targets the protocol fees that are accumulated on Lista DAO and it does **NOT** affect community incentives that are coming from LISTA emissions. 

### Abstract:
The proposal aims to centralize community incentives into LISTA tokens, ensuring transparency and efficiency in reward distribution. By consolidating rewards into a single token, Lista DAO intends to simplify governance and bolster the liquidity of LISTA tokens on the open market. 

Implementation will involve converting existing incentive mechanisms (slisBNB, WBETH, ETH and lisUSD) into LISTA tokens and distributing them to veLISTA holders. Users will only receive 1 form of reward, (LISTA), after this change.

### Motivation:
This proposal addresses the fragmentation and complexity of current reward systems within Lista DAO. The existing mechanism involves distributing various types of rewards each week, often in small amounts, making it inconvenient for veLISTA holders. By converting these incentives into LISTA tokens, we can unify the reward structure, offering greater clarity and predictability for stakeholders.

Additionally, centralizing rewards into LISTA tokens aims to enhance toke

====================================================================================================
[56] id=0x9df2802e57dda190db72ef1e83621669c3ff81d6d8086b8a906476d5a24fb37a  token=LISTA  space=listavote.eth  date=2024-12-03
TITLE: LIP 010 - Proposal to Supply 1 Million lisUSD to the Lista Market on Avalon Labs and Modify the Supply Cap of lisUSD and PSM Allocation
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal aims to strengthen the adoption of lisUSD by supplying 1 million lisUSD to the Lista Market on Avalon Labs. This initiative is designed to boost liquidity, enhance user engagement, and promote wider acceptance of lisUSD as a stable currency within the DeFi landscape. Additionally, the proposal suggests that the supply cap of lisUSD and lisUSD allocation to the PSM (Peg Stability Module) will no longer require proposals for future adjustments. This change will streamline operations, making it easier to stable lisUSD pegging, and involve more partners like Avalon Labs in the near future.

# Abstract
This proposal aims to:
1. Supply 1 million lisUSD to the Lista Market on Avalon Labs (DeFi), allowing Avalon users to borrow the supplied lisUSD.
2. Eliminate the requirement for formal proposals when making changes to the lisUSD supply cap and PSM lisUSD allocation, enabling stable pegging and efficient onboarding of additional ecosystem partners like Avalon Labs in the future.

# Motivation
The motivation behind this proposal is to support the growth of lisUSD and its ecosystem. By supplying 1 million lisUSD, we aim to increase liquidity in the Avalon Lista Market, benefiting both users and developers. Moreover, removing the requirement for proposal-based approvals regarding the supply cap of lisUSD and PSM lisUSD allocation will allow for a more agile response to market conditions and ecosystem needs, ensuring we can swiftly adapt as we transition towards

====================================================================================================
[57] id=0x63bb894fdc5da7ee58cf238b0af8398c7b4d9f5d6a0cc18f71c120050363649d  token=LISTA  space=listavote.eth  date=2024-12-13
TITLE: LIP 012 - Listing PumpBTC as a Collateral in the Innovation Zone
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal seeks to list PumpBTC as a collateral option within Lista DAO’s Innovation Zone. PumpBTC is a liquid staking token for the Babylon platform, enabling BTC holders to stake their assets while retaining liquidity. By listing PumpBTC, Lista DAO aims to expand collateral options, foster innovation, and attract Bitcoin users to the ecosystem.

# Abstract
This proposal aims to add PumpBTC as one of the collaterals to Lista DAO’s Innovation Zone. This integration will empower users to leverage their PumpBTC holdings for minting lisUSD while benefiting from increased liquidity and earning yields from Babylon.

## Reference
PumpBTC is a liquid staking solution designed for the Bitcoin ecosystem through the Babylon platform. It allows users to stake BTC and immediately receive PumpBTC, a 1:1 liquid representation of their staked BTC (WBTC/BTCB). 

Website: https://pumpbtc.xyz
Twitter: https://x.com/Pumpbtcxyz
Discord: https://discord.gg/pumpbtc
Docs: https://pumpbtc.gitbook.io/pumpbtc
Token ticker: $pumpBTC
Contract address: 0xf9C4FF105803A77eCB5DAE300871Ad76c2794fa4

# Motivation
The addition of PumpBTC as collateral aligns with Lista DAO’s mission of building a diverse and robust DeFi ecosystem. Listing PumpBTC will:
1. Broaden Collateral Options: Provide Bitcoin holders a unique way to access liquidity via lisUSD while retaining exposure to BTC.
2. Enhance DeFi Participation: Encourage adoption of both Babylon and Lista DAO’s platforms, bridging Bitcoin liquid

====================================================================================================
[58] id=0x124b6621252ced766836afcff5b8d93fa2c91d5188d8b6deaeb9367f194ad04f  token=LISTA  space=listavote.eth  date=2025-01-10
TITLE: LIP 013 — Proposal to Integrate mCAKE, mLISTA and mwBETH as Collaterals in the Innovation Zone
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary

This proposal seeks to add mCAKE, mLISTA, and mwBETH as collateral options in the Innovation Zone on Lista DAO. Given that these assets are integral to the Magpie ecosystem, this proposal intends to integrate them simultaneously.

mCAKE refers to "Magpie CAKE," a liquid version of veCAKE that enables users to earn rewards for their active participation on Cakepie. mLISTA is Listapie’s rendition of the LISTA token from Lista DAO, allowing LISTA holders to convert their tokens into mLISTA via Listapie to earn active participation rewards without any required lock-up period. mwBETH is Eigenpie's liquid restaking version of Binance's wBETH LST. These projects are core SubDAOs within Magpie's ecosystem.

By incorporating these collateral options into the Innovation Zone, Lista DAO aims to expand available collateral choices, foster innovation, and attract more on-chain users to the ecosystem.

# Abstract

This proposal aims to add mCAKE, mLISTA, and mwBETH as collateral options within Lista DAO’s Innovation Zone. These projects are integral SubDAOs within Magpie's ecosystem. 

This integration will enhance users’ capital efficiency by providing a broader array of assets for minting lisUSD, while benefiting from increased liquidity and yield generation capabilities.

## Reference

The Magpie DAO is a suite of protocols that transcends conventional platforms with the goal of enhancing participation and user opportunities across DeFi. Cakepie, Listapie and Eigenpie are key

====================================================================================================
[59] id=0x9ee7d583f642c9ef751180222515ef438b33871174e8ef864e51303fad73b207  token=LISTA  space=listavote.eth  date=2025-01-20
TITLE: LIP 015 - Governance Proposal: Enhanced Revenue Redistribution Plan
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal seeks to enhance Lista DAO’s revenue redistribution mechanism by allocating 40% of weekly revenue for permanent locking, and the remaining 60% will be mostly directed towards veLISTA holders, with a small portion going to operating expenses. The locked portion will be auto-locked and auto-compounded for 52 weeks perpetually, incentivizing long-term participation and supporting sustainable protocol growth. By permanently locking LISTA tokens, we are perpetually reducing the supply of LISTA through buy backs and reduction in emissions, hence increasing the price of LISTA tokens.

To ensure a smooth transition, the introduction of the 40% allocation for locking will not happen immediately. Instead, it will be implemented gradually, with no more than a 10% change in allocation per week. This gradual adjustment means the full implementation will take a minimum of 4 weeks.

## References
1. Current Revenue Redistribution Model:
a. In our previous proposal, we specified that more than 50% of our weekly revenue will go towards veLISTA holders.
2. Proposed Change:
a. 40% of the revenue will now be used to buy back LISTA, where it will be locked for 52 weeks perpetually through our auto-locking and auto-compounding features. 
b. For the remaining 60%, most of it will continue to be distributed to veLISTA holders, while the rest will be used for operational expenses.
c. Implementation of this change will be a gradual process, increasing no more than 10% weekly un

====================================================================================================
[60] id=0x8de005cbdcdc084942bfbff5a39577d1f88403dcea1e650d71b6a5a358c41888  token=LISTA  space=listavote.eth  date=2025-01-21
TITLE: LIP 016 - Governance Proposal: Enhanced Revenue Redistribution Plan #2
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal aims to enhance Lista DAO’s revenue redistribution mechanism by directing the 40% of LISTA tokens purchased through weekly revenue buybacks into a dedicated new contract address for permanent locking, replacing the latest proposal of using the veLISTA contract for this purpose.

By permanently removing these tokens from circulation, the proposal aims to create a deflationary effect that reduces the total supply of LISTA, enhances scarcity, and increases the long-term value of the token.

## References
1. Current Revenue Redistribution Model in Voting:
In the previous proposal which is currently up for vote, 40% of the revenue will be used to buy back LISTA, where it will be locked for 52 weeks perpetually through our auto-locking and auto-compounding features. 

2. Proposed Change:
Instead of locking LISTA into the veLISTA smart contract for 52 weeks perpetually through auto-lock and auto-compounding feature, LISTA will be locked in a new contract address (null address) where LISTA cannot be released into circulation. 

# Abstract
The proposed change introduces a deflationary strategy that complements Lista DAO’s tokenomics by permanently reducing the circulating supply of LISTA. This change builds on the prior redistribution plan, replacing perpetual locking with a new contract address that prevents LISTA from being released into circulation, achieving greater long-term price stability and value appreciation for LISTA holders. This proposal ensures th

====================================================================================================
[61] id=0xe19d0065f0c1154b3f90a817d30eaa3978304c8704ed9e1fc6c5d11c17600c69  token=LISTA  space=listavote.eth  date=2025-03-10
TITLE: LIP 017 - Governance Proposal: Adding USDF and asUSDF as Collateral in Innovation Zone
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal seeks to introduce USDF and asUSDF backed by Astherus as new collateral assets within Lista DAO’s Innovation Zone. By adding these assets, we aim to expand borrowing options and enhance capital efficiency within the ecosystem. The proposed borrow limits and collateralization requirements ensure risk mitigation while promoting accessibility for users.

## References
**1. What is USDF?**
USDF is a yield-bearing stablecoin issued by Astherus. Backed by crypto assets and corresponding short perpetual positions, USDF maintains delta neutral positions to generate staked USDF yields. USDT and USDF are fully convertible at a 1:1 ratio, with no minting fee. 

Oracle (Chainlink): 0xB97Ad0E74fa7d920791E90258A6E2085088b4320 

**2. What is asUSDF?**
asUSDF is the innovative yield-bearing token of stablecoin USDF. Stake USDF to mint asUSDF, which offers both security and high earning potential. 

Oracle (Binance): 0x82e549f75Da12C644B9095B1cA3333Cb388346e1

**3. About Astherus**
Astherus is a next-gen multi-asset liquidity hub dedicated to maximizing the utility and real yield of crypto assets. Astherus offers a powerful suite of yield-generating products under AstherusEarn and an innovative on-chain perpetual trading platform, AstherusEX.
Website: https://www.astherus.finance/
Twitter/X: https://x.com/AstherusHub
Telegram: https://t.me/AstherusHub
Discord: https://discord.com/invite/rJFFYGAGxG
Documentation: https://docs.astherus.com/

# Abstract
The addition of US

====================================================================================================
[62] id=0x81183e29eb0a8417da7bc3aae9669993f8a181dd8a661761861a2b5a50793d32  token=LISTA  space=listavote.eth  date=2025-03-28
TITLE: LIP 018 - Governance Proposal: veLISTA Incentivization & LP Emission Redistribution
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal introduces an update to the LISTA emission distribution model to the veLISTA holders. Other parts of emission (LPs & others) remain without changes. This proposal aims to enhance governance participation, strengthen ecosystem expansion, and grant veLISTA holders greater influence over emissions allocation. The proposed changes will modify the current LISTA emission pool by splitting it into two distinct parts:
1. **veLISTA Holder Rewards** – A portion will continue to be distributed directly to veLISTA holders, as in the current model. 
2. **Protocol-Bribed LP Incentives** – The remaining portion of LISTA emissions will be used by the protocol to bribe key LP pools directly. veLISTA holders who vote for these pools will receive the rest of the emissions, allowing the community to strategically direct liquidity incentives.

This new system ensures that veLISTA holders play a direct role in guiding LISTA emissions, while also driving liquidity growth in key ecosystem pools through bribes and incentives.

# Current Emission Model (Before Change)
Currently, veLISTA holders receive LISTA emissions through two sources:
	1.	LISTA emission pools
	2.	Protocol revenue used for LISTA buybacks - refer to LIP-016

While this rewards long-term holders, it does not encourage active participation in liquidity governance nor allow the protocol to strategically direct liquidity incentives.

# Proposed Changes: New Emission Model
The LISTA emission pool will now be split

====================================================================================================
[63] id=0x73a807cdea0aae56fec8f90ad6fed968703f10b0680d8e6fedd6f69df839fdb6  token=LISTA  space=listavote.eth  date=2025-08-01
TITLE: LIP 020 - Proposal to Integrate PancakeSwap LP Positions in Lista DAO’s Innovation Zone
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary
This proposal aims to enable lisUSD borrowing against PancakeSwap LP positions (V2, V3, Infinity, and StableSwap) as collateral in Lista DAO’s Collateral Debt Position Innovation Zone. The valuation of LP tokens will rely on a dedicated LP Oracle and LP Manager system with embedded circuit breakers to control volatility risk. Liquidation mechanisms will support LP redemption before the Dutch auction, ensuring smooth liquidation processes. Additionally, 50% of borrow interest and liquidation fees will be shared with PancakeSwap to foster partnership and ecosystem growth.
 
This proposal explores synergies leveraging both protocol’s latest infrastructure, which will significantly help both of the protocols bringing new ecosystem expansion, user adoption, and revenue opportunities. 
 
# About lisUSD
lisUSD is a decentralized, unbiased, collateral backed stablecoin soft-pegged to the US Dollar. Users who deposit assets as collateral within the Lista CDP module are eligible to borrow lisUSD based on the value of their collateral. lisUSD is generated, backed, and kept stable through collateral assets that are deposited into CeVault functioning as the Lista collateral vault.
 
##### lisUSD Key Technical Aspects
● Peg Stability Module (PSM): The Peg Stability Module (PSM) is a critical component designed to maintain the stability and usability of lisUSD by facilitating seamless conversions between centralized stablecoins (eg USDT or USD1) and lisUSD. 
● Algorithmic Market O

====================================================================================================
[64] id=0xdb92580e04ca8d688404a689a99579294715bd9ab858cc9b7ba637599720a6ff  token=LISTA  space=listavote.eth  date=2025-08-11
TITLE: LIP 021 - LISTA Deflationary Initiative: 20% Token Burn & Tokenomics Optimization
CHOICES: YES | NO
TEXT (first 1500 characters):
# Summary
This proposal aims to manage future token supply inflation, optimize the tokenomics structure, and reinforce the protocol’s long-term value commitment.

We propose to permanently burn 20% of LISTA’s maximum supply (200M LISTA), reducing the max supply from 1B to 800M, and replacing the fixed 40% permanent LISTA freeze allocation with a flexible distribution between veLISTA holders and DAO operational funding, while keeping the remaining 60% revenue allocation unchanged.

# Reference
### The current LISTA buy back and revenue distribution mechanism: 
Under LIP 016, effective from 2025-01-24, 40% of weekly protocol revenue has been allocated to buying back LISTA for permanent freezing. To date, this mechanism has bought back a total of 4.36 M LISTA, sent to the official Black Hole Address:  [BscScan link.](https://bscscan.com/token/0xfceb31a79f71ac9cbdcf853519c1b12d379edc46?a=0x000000000000000000000000000000000000dead)
### The proposed change:
Rather than gradually removing a small amount of LISTA each week, this proposal recommends a more impactful and strategic adjustment: executing a one-time burn of 200M LISTA (20% of the maximum supply) to deliver an immediate and substantial deflationary effect. In parallel, the fixed 40% weekly revenue allocation for permanent freezes would shift to a dynamic model, enabling flexible distribution between veLISTA rewards and DAO operational funding in line with evolving governance priorities and ecosystem needs.

# Abstract
This

====================================================================================================
[65] id=0x5ada27a430fdc9961a7e25ea9f30cd3713895076b274ad78988fbbe9e2d9b271  token=LISTA  space=listavote.eth  date=2025-11-12
TITLE: LIP 023 - Supplier Liquidation Profit Redistribution Proposal for the Re7 USD1 Vault
CHOICES: YES | NO
TEXT (first 1500 characters):
# Summary

Following [LIP 022](https://snapshot.org/#/s:listavote.eth/proposal/0xa74d8e9b81469ce77fd647c009f591d00644d0b312f63093f01f89eb2dadbbc6), a total of 481,801.15 USD1 in liquidation profit was automatically collected by Lista DAO’s wallet after executing a forced liquidation on the USDX/USD1 market, curated by Re7 Labs. While $3M was recovered immediately after liquidation, part of the Vault suppliers still experienced blocked withdrawals. To support these suppliers, Lista DAO proposes to return the liquidation profit to affected suppliers. Snapshots of Vault LP holdings will be taken immediately after the voting period concludes, and the Lista team will initiate the return process accordingly.

# Proposed Plan

The plan involves returning the 481,801.15 USD1 liquidation profit to affected Vault suppliers. The funds will be sent to a redeem contract and enable the Vault LP token holders to claim. A snapshot of the LP tokens will be taken immediately after the voting period, and only the addresses holding the LP tokens within the snapshot can claim upon redemption of the LP tokens.

# Voting

This proposal aims to return the 481,801.15 USD1 liquidation profit to help affected suppliers who aren’t able to withdraw.

YES: Return the 481,801.15 USD1 liquidation profit pro rata with position size. A snapshot of Vault LP holdings will be taken immediately after the voting period, addresses within the snapshot will be able to claim their share based on the portion of LP toke

====================================================================================================
[66] id=0x1a15347f6b452049212bdf51ff1a46c0a7edf7ca8efe1004b32c15c2965f0f3b  token=LISTA  space=listavote.eth  date=2026-03-30
TITLE: LIP 024 - Proposal for LISTA Tokenomics 2.0: Removing the veLISTA Model & Expanding LISTA Utility
CHOICES: YES | NO
TEXT (first 1500 characters):
# Summary
This proposal introduces LISTA Tokenomics 2.0 by removing the veLISTA mechanism. The key changes are:
- **Phase out veLISTA and LP pool voting,** while simplifying governance so that LISTA holders are eligible to vote on proposals.
- **Unlock all veLISTA,** without penalties, regardless of original lock duration.
- **Replace veLISTA revenue sharing with LISTA buybacks.** Fees previously allocated to veLISTA stakers will be redirected to fund future LISTA buybacks. A public dashboard will be set up to track all buyback activity.
- **Expand $LISTA token utility**, starting with the new product feature "Delayed liquidation" in Q2 2026.
# Motivation
The veLISTA model was originally designed to reward long-term commitment and align community incentives. In practice, it has introduced three core problems:
### 1. Most holders are excluded from benefits
To earn rewards, users must lock their LISTA for a fixed period in exchange for veLISTA. This has created a gap between the broader LISTA holder base and the small group of active veLISTA participants. Despite LISTA's circulating supply growing steadily, the amount locked in veLISTA has stayed flat. 
The community has made clear they want a system where all LISTA holders can benefit , not just those willing to lock.
### 2. Low participation due to complexity
Active participation in veLISTA and governance voting sits below 20%. The locking process, time commitment, and risk of being locked out of liquidity make the system mor

====================================================================================================
[67] id=0x35ed127d0b297b9d848de4ffc054951134c3afe6c458f80859fc4ffb1600066b  token=LRC  space=loopringdao.eth  date=2022-08-19
TITLE: Liquidity provider protocol fee distribution - September
CHOICES: 1INCH/ETH | AAVE/ETH | AC/ETH | AC/USDT | ADX/ETH | AMP/ETH | BAL/ETH | BAND/ETH | BCDT/ETH | BCP/ETH | BEL/ETH | BIT/USDC | BKT/USDT | BNT/ETH | BTC2XFLI/ETH | BTU/ETH | BZRX/ETH | CEL/ETH | COMP/ETH | CRV/ETH | DAI/USDT | DEFIL/ETH | DEP/ETH | DOUGH/ETH | DPI/ETH | DPR/ETH | ENJ/ETH | ENS/ETH | ENTRP/ETH | ETH/DAI | ETH/USDC | ETH/USDT | FARM/ETH | FIN/ETH | FLI/ETH | FLX/ETH | FUSE/ETH | GNO/ETH | GRG/ETH | GRID/ETH | GRT/ETH | HBTC/ETH | HBTC/USDT | HEX/ETH | ICHI/ETH | IDLE/ETH | IMX/USDC | INDEX/ETH | JRT/ETH | KEEP/ETH | KNC/ETH | KP3R/ETH | LINK/ETH | LRC/ETH | LRC/USDC | LRC/USDT | LRC/WBTC | MANA/USDC | MASK/LRC | MATIC/ETH | MCB/ETH | MKR/ETH | MOVD/ETH | NIOX/ETH | NMR/ETH | OBTC/ETH | OGN/ETH | OMG/ETH | OVR/ETH | PNK/ETH | PNT/ETH | RAI/ETH | REN/ETH | RENBTC/ETH | RENDOGE/ETH | REPT/ETH | RFOX/ETH | RGT/ETH | RICE/USDT | RPL/ETH | RSPT/USDC | SAND/USDC | SENT/USDC | SMARTCREDIT/ETH | SNT/ETH | SUSHI/ETH | SX/ETH | UNI/ETH | VETH/ETH | VSP/DAI | VSP/ETH | WBTC/DAI | WBTC/USDC | WBTC/USDT | WETH/ETH | WOO/USDT | YFI/ETH | YFII/ETH
TEXT (first 1500 characters):
LRC holders will decide which AMM pools are to be incentivized with protocol fees for the month of September.

Three pools will automatically be rewarded: LRC/ETH, LRC/USDC, and LRC/USDT.

This vote will determine which remaining pools will be included. Any pool that receives a minimum of 10% of the vote will be rewarded in the upcoming month’s fee distribution.

You will be able to vote with your LRC balances on Ethereum L1 as well as Loopring L2. For those who hold LRC on both layers, their balance is calculated as the sum of their Loopring + Ethereum LRC.

Protocol rewards will be disbursed with equal weight to each pool that is designated to receive them.

Fees generated by the protocol are distributed to Liquidity providers, the Loopring insurance fund, and the Loopring DAO. 
Fee Distribution:
- 80% towards LPs.
- 10% to the Loopring insurance fund.
- 10% to the Loopring DAO.

About Loopring DAO and Protocol Fees 
https://medium.loopring.io/introducing-dao-voting-46a210c373bc

====================================================================================================
[68] id=0xd99ac433eb95157817f583fbcedb90feaa102bf8237c8c06d150a01eb872acce  token=LRC  space=loopringdao.eth  date=2022-09-09
TITLE: What should the minimum liquidity value threshold be for AMM pools to be listed in the LP protocol fee vote?
CHOICES: $0 | $25,000 | $50,000
TEXT (first 1500 characters):
For context there were 98 AMM pools listed in the first protocol fee vote (https://vote.loopring.io/#/proposal/0x35ed127d0b297b9d848de4ffc054951134c3afe6c458f80859fc4ffb1600066b). Many felt that future proposals could be improved by reducing the number of options. In addition, establishing a minimum liquidity value may provide an incentive for less liquid AMM pools to acquire more liquidity in order to be listed in the quarterly protocol fee vote. 

Please note that protocol fee LP voting will take place quarterly, and any pool that receives a minimum of 10% of the vote will be rewarded for the quarterly fee distribution.

====================================================================================================
[69] id=0x146956c0061c5ae9e26aa1dda71324db4ad41640832f24345f8f3ae1d191c41a  token=LRC  space=loopringdao.eth  date=2022-09-15
TITLE: Should the quarterly token be automatically added to LP protocol fee distributions for its 1st quarter?
CHOICES: YES | NO
TEXT (first 1500 characters):
Each quarter LRC token holders will vote on a new token to be supported on Loopring (https://vote.loopring.io/#/proposal/0x080531cd46ca897ca97e7f8586ba96ef4fd9e02c2dbbd3b033b7a9c814dea5c3). In addition, an AMM pool will be created for each newly supported token. 

Since the winning token's corresponding AMM pool will have little to no liquidity to being with, should the quarterly token be automatically added to LP protocol fee distributions for its 1st quarter to help to help jump-start its liquidity.

Voting 'YES' will automatically add the quarterly voted token's corresponding AMM pool to LP protocol fee distribution for the 1st quarter after its addition.

====================================================================================================
[70] id=0x952d1e65d95569b7813e82a8914f57a3704fd8422c1e6f06a5e821593a41aca9  token=LRC  space=loopringdao.eth  date=2022-09-22
TITLE: Liquidity provider protocol fee distribution - Q4
CHOICES: BIT/USDC | DPI/ETH | ETH/DAI | ETH/USDC | ETH/USDT | IMX/USDC | LINK/ETH | LRC/WBTC | MANA/USDC | MASK/LRC | MATIC/ETH | RICE/USDT | SAND/USDC | VETH/ETH | WBTC/ETH | NONE
TEXT (first 1500 characters):
LRC holders and LRC LPs will decide which AMM pools are to be incentivized with protocol fees for the months of October, November, and December.

Four pools will automatically be rewarded: LRC/ETH, LRC/USDC, LRC/USDT, and rETH/ETH

This vote will determine which remaining pools will be included. Any pool that receives a minimum of 10% of the vote will be rewarded in the upcoming quarter's fee distribution.

Only pools with $50k in liquidity will be listed as voted in LIP #4
(https://vote.loopring.io/#/proposal/0xd99ac433eb95157817f583fbcedb90feaa102bf8237c8c06d150a01eb872acce).

Protocol rewards will be disbursed with equal weight to each pool that is designated to receive them.

====================================================================================================
[71] id=0xc45b905ae4cb2efdac8d8ff468a4ad2a7854ba0dab93960d0b6e838f59a0592d  token=LRC  space=loopringdao.eth  date=2022-11-29
TITLE: Should Loopring add Layer 2 LRC Staking to Loopring Earn?
CHOICES: YES | NO
TEXT (first 1500 characters):
---

A passing 'YES' vote will add Layer 2 LRC Staking into the development roadmap of the Loopring core team.

---

L2 LRC Staking pool will receive 45% of the protocol fee distributions going forward, once implemented. Distributions will take place once every quarter to ensure stakers remain staked for at least one full quarter in order to receive distributions.

Protocol fee distributions going forward (once staking is implemented) will be:

45% to LPs in qualifying AMM pools
45% to LRC stakers
10% to DAO pool

 IN ORDER FOR 'YES' VOTE TO PASS IT MUST ALSO PASS WITH:

 - 60% or higher of total votes for 'YES'
 - 10million or higher amount of LRC reflected in the total vote (quorum)

ANYTHING LOWER WILL RESULT IN A 'NO' VOTE PASSING

---

A passing 'NO' vote will mean protocol fee distribution remains the same and no new action is taken.

---

====================================================================================================
[72] id=0x40964acbf6df784a912bcde569eebf34bf451aa265869c5a3de67f4385c3f983  token=LRC  space=loopringdao.eth  date=2022-12-12
TITLE: Which token should be supported next on Loopring L2?
CHOICES: Ankr (ANKR) | Axie Infinity (AXS) | Lido DAO (LDO) | Quant (QNT)
TEXT (first 1500 characters):
LRC holders and LRC liquidity providers (LPs) will decide which token will be supported next on Loopring. In addition, an AMM pool will be created for this newly supported token. To further encourage the adoption of this new AMM pool, it will be incentivized with protocol fees for the months of January, February, and March 2022, as previously voted on in LIP #6 (https://vote.loopring.io/#/proposal/0x146956c0061c5ae9e26aa1dda71324db4ad41640832f24345f8f3ae1d191c41a).

====================================================================================================
[73] id=0x161c2ba84fb945de5ad5791cf64898e2d61272d51141e9da2cbcaacc65496f85  token=LRC  space=loopringdao.eth  date=2022-12-21
TITLE: LP protocol fee distribution - Q1 2023
CHOICES: BIT/USDC | DPI/ETH | ETH/DAI | ETH/USDC | ETH/USDT | IMX/USDC | LINK/ETH | MANA/USDC | MASK/LRC | RICE/USDT | SAND/USDC | VETH/ETH | WBTC/ETH | NONE
TEXT (first 1500 characters):
LRC holders and LRC LPs will decide which AMM pools are to be incentivized with protocol fees for the months of January, February, and March 2023.

Four pools will automatically be rewarded: LRC/ETH, LRC/USDC, LRC/USDT, and LDO/ETH

This vote will determine which remaining pools will be included. Any pool that receives a minimum of 10% of the vote will be rewarded in the upcoming quarter's fee distribution.

Only pools with $50k in liquidity will be listed as voted in LIP #4
(https://vote.loopring.io/#/proposal/0xd99ac433eb95157817f583fbcedb90feaa102bf8237c8c06d150a01eb872acce).

Protocol rewards will be distributed to the pools designated by the DAO. The distribution amongst the pools will be done in proportion to each pool’s total liquidity.

====================================================================================================
[74] id=0xbd20585ce42be201912b273c04922898eebf76cb88295836cbc2bc914db04dfa  token=LRC  space=loopringdao.eth  date=2023-03-16
TITLE: Which token should be supported next on Loopring L2?
CHOICES: Blur (BLUR) | Liquity (LQTY) | Metis (METIS) | Quant (QNT)
TEXT (first 1500 characters):
LRC holders and LRC liquidity providers (LPs) will decide which token will be supported next on Loopring. In addition, an AMM pool will be created for this newly supported token vs. ETH. To further encourage the adoption of this new AMM pool, it will be incentivized with protocol fees for the months of April, May, and June 2023.

====================================================================================================
[75] id=0x6d5305865570d659f50926b7c4108b66274c6a1cabe599349c1d96f30320859c  token=LRC  space=loopringdao.eth  date=2023-03-22
TITLE: LP protocol fee distribution - Q2 2023
CHOICES: BIT/USDC | DPI/ETH | ETH/DAI | ETH/USDC | ETH/USDT | IMX/USDC | LINK/ETH | LRC/WBTC | MANA/USDC | MASK/LRC | RETH/ETH | RICE/USDT | SAND/USDC | VETH/ETH | WBTC/ETH | WBTC/USDC | NONE
TEXT (first 1500 characters):
LRC holders and LRC LPs will decide which AMM pools are to be incentivized with protocol fees for the months of April, May, and June 2023.

Four pools will automatically be rewarded: LRC/ETH, LRC/USDC, LRC/USDT, and LQTY/ETH

This vote will determine which remaining pools will be included. Any pool that receives a minimum of 10% of the vote will be rewarded in the upcoming quarter's fee distribution.

Only pools with $50k in liquidity will be listed as voted in LIP #4
(https://vote.loopring.io/#/proposal/0xd99ac433eb95157817f583fbcedb90feaa102bf8237c8c06d150a01eb872acce).

Protocol rewards will be distributed to the pools designated by the DAO. The distribution amongst the pools will be done in proportion to each pool’s total liquidity.

====================================================================================================
[76] id=0xf7bb129aa9c4c15d84b9ceb195f357ac628e7501c7856f4be11846247191a1fe  token=LRC  space=loopringdao.eth  date=2023-06-16
TITLE: Which token should be supported next on Loopring L2?
CHOICES: Blur (BLUR) | Metis (METIS) | Quant (QNT) | Telos (TLOS)
TEXT (first 1500 characters):
LRC holders and LRC liquidity providers (LPs) will decide which token will be supported next on Loopring. In addition, an AMM pool will be created for this newly supported token vs. ETH. To further encourage the adoption of this new AMM pool, it will be incentivized with protocol fees for the months of July, August, and September 2023.

====================================================================================================
[77] id=0x38f366d48efb72ff6eab53bd0a07233439c14f315d191e87280f5ad5f096ee6f  token=LRC  space=loopringdao.eth  date=2023-06-21
TITLE: LP protocol fee distribution - Q3 2023
CHOICES: BIT/USDC | DPI/ETH | ETH/DAI | ETH/USDC | ETH/USDT | IMX/USDC | LINK/ETH | LRC/WBTC | MANA/USDC | MASK/LRC | NONE | RETH/ETH | RICE/USDT | SAND/USDC | WBTC/ETH
TEXT (first 1500 characters):
LRC holders and LRC LPs will decide which AMM pools are to be incentivized with protocol fees for the months of July, August, and September 2023.

Four pools will automatically be rewarded: LRC/ETH, LRC/USDC, LRC/USDT, and TLOS/ETH

This vote will determine which remaining pools will be included. Any pool that receives a minimum of 10% of the vote will be rewarded in the upcoming quarter's fee distribution.

Only pools with $50k in liquidity will be listed as voted in LIP #4
(https://vote.loopring.io/#/proposal/0xd99ac433eb95157817f583fbcedb90feaa102bf8237c8c06d150a01eb872acce).

Protocol rewards will be distributed to the pools designated by the DAO. The distribution amongst the pools will be done in proportion to each pool’s total liquidity.

====================================================================================================
[78] id=0x2c135f8fe60ea17cf22c607378939f6af6b024866e56784378ce895a66bd49c4  token=MAGIC  space=treasuregaming.eth  date=2023-03-14
TITLE: TIP-25: Re-Allocation of LP and Staking Rewards to Ecofund and Contributors
CHOICES: Approve TIP-25 | Reject TIP-25
TEXT (first 1500 characters):
# Summary
TIP-25 outlines a proposal for TreasureDAO (“Treasure”) to reallocate a portion of MAGIC originally assigned for LP and staking rewards to the Ecosystem Fund (“Ecofund”) and to be earmarked for new contributor allocations.

For more details, please see the [governance forum](https://gov.treasure.lol/discussion/10338-tip25-reallocation-of-lp-and-staking-rewards-to-ecofund-and-contributors).

# Voting Period
Voting commences now, ending Thursday, March 16, 2023 at 5:00 PM UTC ([see local time via timestamp: 1678986000](https://hammertime.cyou/?t=1678986000)).

# Voting Eligibility
- Only holders of MAGIC staked in the Harvesters or Governance Staking contract, and MAGIC-ETH SLP on Arbitrum can vote.
- gMAGIC will be calculated on a 1:1 basis across all options

👉 Stake to gain gMAGIC here: https://governance-staking.treasure.lol/

====================================================================================================
[79] id=0x7e7b480b7f50da01f276a5a717ba697a223d224c3ccc0352e7b1681e56b8a64a  token=MAGIC  space=treasuregaming.eth  date=2023-03-31
TITLE: MIP04 - List Realm ANIMA
CHOICES: List ANIMA | Abstrain for now
TEXT (first 1500 characters):
Realm is seeking to list ANIMA on MagicSwap, a community driven AMM for TreasureDAO projects. 

**Description**
Realm is a world-building and exploration game where players choose between two paths: Realmer and Adventurer. As a Realmer, manage your resources to become the most productive Realm in the ecosystem. As an Adventurer, explore the Realmverse as you discover your true origins.
 
**Token** 
ANIMA ($ANIMA) is currently used for:
• Levelling up characters (Time constrained)
• Ability to choose a new character Variant (Adventurer)
• Continuous usage(burn) to earn LootBoxes (Adventurers)
• Gamified staking to get portion of daily ANIMA emissions (Staker)

**Liquidity Strategy**
Realm plans to unlock trading restrictions on $ANIMA and allow its community to contribute and own the liquidity pools earning AMM fees. This will allow liquidity to grow in an organic manner that strengthens the correlation between the token’s value and in-game demand for the token. The team may decide to later provide liquidity.
We will be providing in-game incentives to offset any possible impermanent loss on the part of the provider. These incentives will mature as the risk for loss decreases.

**Additional details may be found in the commonwealth discussion thread.**

====================================================================================================
[80] id=0xc8a766cf5cae7f1db310ebb06aee471e77ad6622f3b32d1368ffa3895f486d32  token=MAGIC  space=treasuregaming.eth  date=2023-08-21
TITLE: TIP-29: MAGIC Reconciliation Mint and TIP-25 Token Schedule Assignment
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
TIP-29 outlines three proposals for TreasureDAO (“Treasure”): (i) mint tokens identified as being unminted from the genesis event and subsequent minting events following a reconciliation conducted by the council and r3gen Finance teams (financial ops partner selected to produce the DAO report as part of TIP-26 and [published here](https://commonwealth.im/treasure-dao/discussion/12731-treasure-dao-q2-financial-report) on August 15, 2023); (ii) reallocate the minting balance to the Ecosystem Fund (“Ecofund”); and (iii) assign a vesting schedule to the minted tokens as well as the tokens re-allocated from the Staking/LP fund in line with TIP-25. The reconciliation identified a total of 8,068,497 MAGIC remains unminted which was attributed to an overestimation of the original MAGIC Farm on Ethereum L1 which resulted in a current max total supply of ~339,645,510 instead of 347,714,007 as set forth in the original tokenomics framework.

For more details and the full proposal, please see the [governance forum](https://commonwealth.im/treasure-dao/discussion/12755-tip29-magic-reconciliation-mint-and-tip25-token-schedule-assignment).

# Voting Period
Voting commences now, ending Thursday, August 24, 2023 at 7:00 PM UTC ([see local time via timestamp: 1692903300](https://hammertime.cyou/?t= 1692903300)).

# Voting Eligibility
- Only holders of MAGIC staked in the Harvesters or the TreasureDAO Governance Staking contract, and MAGIC-ETH SLP on Arbitrum can vote.
- gMAGIC will b

====================================================================================================
[81] id=0x08bdb0457176991340dea5357ff310b29718db2c2cf572a56f0f7ecdf1bc0396  token=MAGIC  space=treasuregaming.eth  date=2023-12-11
TITLE: TIP-34: gMAGIC Expansion and Governance Staking Lockup Reduction
CHOICES: For | Against
TEXT (first 1500 characters):
# Summary
- Expand gMAGIC to account for additional sources of locked MAGIC, including: (i) [Magicswap](https://magicswap.lol/) through all pools with game partner ERC-20s; and (ii) decentralized finance and other exchanges such as [Beefy](https://app.beefy.com/vault/sushi-arb-magic-weth)’s mooSushiMAGIC-ETH vault and [Balancer](https://app.balancer.fi/#/arbitrum/pool/0xb3028ca124b80cfe6e9ca57b70ef2f0ccc41ebd40002000000000000000000ba)’s 50% MAGIC / 50% USDC weighted pool. 
- Reduce the governance staking contract’s staking lockup period from 14-days to **7-days**.

# Rationale
## Accounting for Magicswap 
With Magicswap serving as the native automated market maker (“AMM”) governed by the TreasureDAO community built specifically for its ecosystem of game tokens, all MAGIC added by the community to MAGIC denominated liquidity pools with listed ERC-20s should count towards governance power within TreasureDAO. Currently, the listed game tokens include $ANIMA (Realm), $ELM (Tales of Elleria), $GFLY (BattleFly), and $VEE (Zeeverse).

## Accounting for decentralized finance and other exchanges
Over time, MAGIC has seen increased adoption across the decentralized finance and exchange landscape with alternative liquidity sources being formed organically through the adoption and usage of new protocols by the Treasure and MAGIC community. Today, these protocols include Beefy’s mooSushiMAGIC-ETH vault and Balancer’s 50% MAGIC / 50% USDC weighted pool which was initially seeded by the fra

====================================================================================================
[82] id=0xc1da3eb8ced7102be6b8517477534403af5774646b5693d4ab534a873519ddb7  token=MAGIC  space=treasuregaming.eth  date=2023-12-30
TITLE: TIP-35: Updates to MAGIC LP Incentives: Conservation for Future Initiatives
CHOICES: For | Against
TEXT (first 1500 characters):
# Summary
Amend Sushi LP rewards downwards to reduce unnecessary inflation to MAGIC circulating supply, recoup MAGIC that was previously allocated to Arbitrum Nova and Hop via TIP-27, and preserve incentives to be used in future new user growth and market discovery initiatives as Treasure moves towards the Treasure Chain. 
# Rationale
## Healthy MAGIC Markets
In the past year MAGIC has enjoyed healthy volume and liquidity across a number of venues including major centralized exchanges such as Binance and Coinbase, as well as decentralized exchanges like Sushi. As of 7 December 2023, the Sushi LP pool holds approximately $11.2 mil MAGIC/ETH and has enough depth to support significant trading activities with acceptable slippage. A $100k buy or sale would move prices roughly only 1% to 1.5% at current liquidity depth. This allows us to lower LP incentives and conserve emissions for future use in line with [TIP-20(b)](https://gov.treasure.lol/discussion/8670-tip20b-amendment-to-magic-lp-incentives). 
## Conserving Emissions for Future Initiatives (eg. Treasure Chain)
With increased focus by the core contributing team on the Treasure Chain as one of the upcoming initiatives for the Treasure DAO ecosystem, it is imperative that liquidity and attention not be fragmented away from the current “homebase” of Treasure (Arbitrum One) and that we ease any potential migration to come. Moreover, emissions allocated to staking and liquidity incentives should be preserved in order to support

====================================================================================================
[83] id=0xd44ef5a7aa8e1f1fc7dbaeff668f401acf74170b37bd63e2b946590ba0aee6ce  token=MAGIC  space=treasuregaming.eth  date=2024-02-14
TITLE: TIP-36: Ecosystem Selection for the Treasure Chain
CHOICES: Optimism | zkSync | SKALE | Arbitrum | Do not build the Treasure Chain
TEXT (first 1500 characters):
# Summary
TIP-36 outlines a proposal for TreasureDAO (“Treasure”) to select the ecosystem to build the Treasure Chain. The Treasure Chain, secured by MAGIC, will serve as a settlement layer and enable the development of an end-to-end ecosystem for Treasure as a decentralized gaming network.

Despite the core contributors not running a public request for proposal (RFP) process, Treasure DAO received its first public ecosystem proposal on January 30, 2024 beginning with Optimism and later followed by zkSync and SKALE in order. The core contributor team published a [litepaper](https://go.treasure.lol/litepaper) on February 5, 2024 outlining their vision for the Treasure Chain and highlighted Arbitrum as its ecosystem recommendation.

**Ecosystem Proposals** (in order of publishing):
- [Optimism](https://forum.treasure.lol/discussion/15048-treasure-on-the-superchain)
- [zkSync](https://forum.treasure.lol/discussion/15058-zksync-and-treasure-dao-crafting-a-future-in-decentralized-gaming)
- [SKALE](https://forum.treasure.lol/discussion/15178-skale-network-treasure-dao-scaling-blockchain-gaming-for-mass-adoption)
- Arbitrum*

This proposal will only select the ecosystem to build the Treasure Chain. A separate proposal will follow at a later date to ratify chain specifications.

**Note: No public proposal was published by the Arbitrum Foundation, but Arbitrum as a recommendation was embedded within the Treasure Infinity Chains litepaper published by the core contributing team.*

# Ra

====================================================================================================
[84] id=0x3f7e2eda3d4334fbe5933c3fbe3dcde5fb652fa9b027a82d490e75e165620b60  token=MAGIC  space=treasuregaming.eth  date=2024-03-05
TITLE: MIP-07: Reduce Swap Fees on Magicswap
CHOICES: Reduce Swap Fee to 0.5% from 3% | No Change to Swap Fee (3%)
TEXT (first 1500 characters):
# Summary
Magicswap, a decentralized exchange (DEX) developed by TreasureDAO (“Treasure”), currently imposes swap fees that are substantially higher than its competitors. This proposal aims to address this issue by reducing swap fees on Magicswap.

*This proposal was submitted by long-standing Treasure community member "The Smolinator".*

# Rationale
- **Competitive Positioning:** By reducing swap fees, Magicswap can enhance its competitiveness in the decentralized exchange market. Lower fees could attract more users and liquidity to the platform, thereby increasing trading volume and overall ecosystem activity.
- **User Experience Improvement:** High swap fees can deter users, especially those trading smaller amounts, from utilizing Magicswap. Lowering fees would improve the user experience and make the platform more accessible to a broader range of traders, including retail investors.
- **Liquidity Incentive:** Reduced fees can incentivize liquidity providers to stake their assets on Magicswap, leading to deeper liquidity pools. Deeper liquidity enhances price stability and reduces slippage, benefiting all traders on the platform.
- **Community Satisfaction:** Addressing the community’s concerns about high swap fees demonstrates TreasureDAO’s responsiveness to user feedback and commitment to creating a user-centric decentralized ecosystem. This can foster greater trust and loyalty among community members.
- **Long-Term Sustainability:** While high fees may generate short-te

====================================================================================================
[85] id=0xb680eed05ef084b379bc10270ed2f42262fe37aae703e164e4547d9ff137ad5b  token=MAGIC  space=treasuregaming.eth  date=2024-08-06
TITLE: TIP-42: Reallocating Bridgeworld Emissions to Treasure Chain EigenLayer Staking and Transition to Bridgeworld v2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary

Reallocate Bridgeworld emissions to support Treasure mainnet staking through EigenLayer and EigenDA.
- Reallocate Bridgeworld emissions towards Treasure Chain DA emissions totalling 1.55mil MAGIC per year, with 3 mil MAGIC retained for Bridgeworld v2 (out of approximately 10 mil remaining emissions) and the excess going to the DAO treasury for future infrastructure emissions.
- Scrap the yearly halving schedule and institute terminal inflation beginning in Y8 (in four years).
- Sunset TIP-08 emissions.
- Tentatively cease Bridgeworld v1 operations on ~~August 24~~ **August 26**
- Update gMAGIC calculation to account for the future Treasure L2.

This proposal will briefly describe the planned system for Bridgeworld NFTs and the next iteration of Bridgeworld. However, for the purposes of governance clarity, this TIP strictly concerns the emissions policy regarding MAGIC. This proposal is not a referendum on Bridgeworld v2.

## Changelog (as of Aug 6 as of 12:12am ET)

The following parameters have changed from the original proposal to Snapshot (edited to be reflected in the proposal and summarized below):

- Moved the target date to tentatively cease Bridgeworld v1 operations and take the snapshot of Bridgeworld assets to be **Monday, August 26** instead of on Saturday, August 24. This change will allow the team to be online and active during the week and able to provide support. 

  - The date remains tentative and a final date will be announced closer in the coming

====================================================================================================
[86] id=0xb647ca49f710550a19c9519ce3a05965091b06e849863073e4fd9bbf83fb14ea  token=MAGIC  space=treasuregaming.eth  date=2024-08-21
TITLE: TIP-42(b): Confirming Bridgeworld Emissions Reallocation and Snapshot Date
CHOICES: Approve (1) | Approve (2) | Abstain | Reject
TEXT (first 1500 characters):
# Summary
Amend TIP-42 to confirm the Bridgeworld (BW) emission reallocation and snapshot date by either:
1. Halting MAGIC emissions through Harvesters and taking the BW snapshot on Monday August 26; or;
2. Reallocating 200,000 MAGIC per month back to BW Harvesters and maintain MAGIC emissions as a stop gap measure with a flexible end and snapshot date coinciding with the launch of EigenDA chain staking on Treasure mainnet.

In either case, all other parameters of the original TIP-42 will not be impacted and will continue to take place on Monday, August 26. For the avoidance of doubt:
- Reallocate Bridgeworld emissions towards Treasure Chain DA emissions totalling 1.55mil MAGIC per year, with 3 mil MAGIC (less any MAGIC reallocated if (2) is selected) retained for Bridgeworld v2 (out of approximately 10 mil remaining emissions) and the excess going to the DAO treasury for future infrastructure emissions.
- Close BW v1 gameplay loops (Questing, Crafting, Corruption, Corruption Crypts)
- Scrap the yearly halving schedule and institute terminal inflation beginning in Y8 (in four years).
- Sunset TIP-08.
- Maintain the transition plan to BW v2 (Conversion Points and Seekers).
- Update gMAGIC calculation for governance voting power.

# Read Full Proposal
👉 [See the proposal on the TreasureDAO governance forum](https://forum.treasure.lol/discussion/24564-tip42b-confirming-bridgeworld-emissions-reallocation-and-snapshot-date)

# Voting Eligibility
The following holders of MAGIC can

====================================================================================================
[87] id=0x2ff602825a007f159972880251b20d8a412371aae0dea57356b90d9b57989d56  token=MAGIC  space=treasuregaming.eth  date=2024-09-17
TITLE: TIP-43: Chain Migration Incentives
CHOICES: Approve | Reject | Abstain
TEXT (first 1500 characters):
# Summary
- Migrate 80% of TreasureDAO’s DAO-owned MAGIC/ETH liquidity on Arbitrum One to the Treasure L2 mainnet (100%) upon its launch.
- Migrate the other 20% of DAO-owned MAGIC/ETH liquidity from Arbitrum One to L1 Ethereum at the time of proposal passage.
- Institute new LP rewards to encourage migration of MAGIC and partner token liquidity from Arbitrum One on Sushi and Magicswap to Treasure L2.

# Read Full Proposal
- [Read the full proposal for TIP-43: Chain Migration Incentives
here](https://forum.treasure.lol/discussion/24826-tip43-chain-migration-incentives)

# Voting Eligibility
The following holders of MAGIC can vote:
- (A) Stakers in the TreasureDAO [Governance Staking contract](https://governance-staking.treasure.lol/), and Sushi (MAGIC-ETH SLP) on Arbitrum One.
- (B) Holders of all listed Magicswap LP tokens and stakers in Beefy’s mooSushiMAGIC-ETH vault or Balancer’s 50% MAGIC / 50% USDC weighted pool.

gMAGIC will be calculated on a 1:1 basis in (A) and 0.5 ratio in (B) (50% of MAGIC amount)

====================================================================================================
[88] id=0x291c3c0689e3d31e2d1e8629edb998333e5998f26bc8c03a17bc129fb1ed48c6  token=MAGIC  space=treasuregaming.eth  date=2024-12-03
TITLE: TIP-46: Fast Track Bridging and MAGIC Collateral Mint
CHOICES: Approve | Reject | Abstain
TEXT (first 1500 characters):
# Summary
In order to enable a seamless bridging experience to move MAGIC from Arbitrum One (`arb1`) to Treasure chain’s mainnet (`treasure`), TIP-46 proposes the following actions:
- Deploy a Hyperlane Warp Route and supporting smart contracts to power direct, real-time (Fast Track) collateral-based bridging of MAGIC between `arb1` and `treasure` (”MAGIC Fast Track”).
  - [Optional] Dynamically monitor incoming bridge requests for automated collateral top-up on `treasure`.
- Extend functionality of the MAGIC token on Ethereum (eth) to support minting and eventual burning of additional (bridge collateral) supply.
- Mint additional MAGIC supply for use solely as bridge collateral to facilitate mint-to-burn within a closed-loop for migration purposes. The proposed method is zero-sum and does not result in additional MAGIC circulating supply.
- Continue ongoing design and future rollout leveraging Chainlink CCIP for a long-term cross-chain MAGIC interop strategy.
- Approve the council-managed operation to migrate MAGIC held in the DAO’s various multisigs as well as the MAGIC-ETH protocol-owned liquidity (”PoL”) (ratified in [TIP-43](https://forum.treasure.lol/discussion/24826-tip43-chain-migration-incentives)) through the canonical Arbitrum bridge and/or MAGIC Fast Track Bridge.
  - For the PoL portion, 80% will be bridged through the MAGIC Fast Track Bridge when available with the remaining 20% bridged through the canonical Arbitrum imminently as approved in TIP-43

# Read Full

====================================================================================================
[89] id=0x2b84df98a825067bc9f3a857be0347da7a89f579e47e4b31b4265b0724d950e2  token=MAGIC  space=treasuregaming.eth  date=2025-04-13
TITLE: TIP-48: Reallocate Undistributed Atlas Mine Rewards
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Summary
This proposal will end the reward claim for the Atlas Mine, which opened in 2021 to distribute MAGIC as part of the project’s fair launch.

Rationale
The unclaimed MAGIC in the Atlas Mine has sat dormantly for years and was originally allocated to bootstrap the community around the Bridgeworld project. It has been many years since that time. Individuals who have not claimed their MAGIC likely forgot that they participated in this bootstrapping event years ago and are clearly disengaged from the Treasure project.

These farmers will remember that they participated in the Atlas Mine only after MAGIC starts outperforming the market and regaining attention, creating sell pressure from disengaged speculators who add no value to the Bridgeworld project.

In recent years, most airdrops and token farms included explicit conditions for rewards becoming unclaimable after a set period of time. The DAO should step in and legislate this cut-off that should have been included initially.

Reallocating rewards to Bridgeworld development, specifically the Canopy game, is in the best interests of today’s community.

Claimable MAGIC will be removed from the rewards contract 14 days after the passage of this proposal. 14 days is an adequate time frame. Farmers have had multiple years to claim their MAGIC but failed to do so. Moreover, the governance process itself takes time, creating additional buffer time to withdraw.

Implementation
MAGIC will be removed from the Atlas Mine rewards co

====================================================================================================
[90] id=0x733799d525cec0794f157cbace52851b28809706eb87d51472dac8584949d791  token=MAGIC  space=treasuregaming.eth  date=2025-04-22
TITLE: TIP-52: Temporary Authority for PoL Management and Chain Wind-Down
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Summary
In light of the critical financial situation outlined by lead contributor John Patten, this proposal seeks authority for the core contributor team to act swiftly regarding key assets and infrastructure to ensure the DAO’s survival and facilitate the necessary strategic pivot. Specifically, this TIP proposes to:
- Grant the core contributor team unilateral authority, effective immediately upon passing and expiring at the end of Q2 2025 (June 30, 2025), to manage the primary MAGIC-ETH Protocol-Owned Liquidity (PoL) pool.
- Grant the core contributor team unilateral authority, within the same timeframe (until June 30, 2025), to initiate and execute the wind-down and shutdown of the Treasure Chain infrastructure currently operating on the ZKsync network.
- Authorize the team to take necessary actions related to the above, including migrating liquidity, bridging assets, decommissioning services, and communicating the process, without requiring separate, subsequent governance votes for each specific action within this scope.

Rationale
The recent communication from John Patten has laid bare the serious financial challenges facing TreasureDAO. With a significantly reduced runway (estimated to last until December 2025, potentially February 2026 in an optimistic scenario) and a high historical burn rate, immediate and drastic measures are required for survival.
1. Need for Agility and Cost Reduction: The previous operational model, including the game publishing stack and the T

====================================================================================================
[91] id=0x35c92fffcc5275c0c712aa6d5274c06583194411e6078b1f481ddd33e792aa13  token=MAGIC  space=treasuregaming.eth  date=2025-07-14
TITLE: TIP-55: Amend Linear Unlock of Ecosystem Fund
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
SUMMARY
This proposal voids the linear unlock of the ecosystem fund and authorizes the core contributors to divest these tokens at market-neutral rates defined by TIP-17. Moreover, the circulating supply will be updated when diversification occurs. This proposal does not authorize the minting of additional tokens.

RATIONALE
The Treasure team’s current stablecoin runway is until August 2026. This proposal does not reflect an immediate need for continued operations. We have recovered from our early 2025 setbacks with strength and are preparing for the long-term again. This proposal is meant as a housekeeping proposal to discard the linear unlock of the ecosystem fund that was created in 2021.

The original emissions schedule was created almost four years ago when MAGIC’s market cap was much smaller. We have learned many lessons during this time, especially the volatility of the MAGIC price. The linear unlock was put there to reassure the community that the contributors would not be divesting large amounts through a DEX in the early months of the project, but it makes little sense to keep this guard-rail when the token is almost entirely emitted and with major CEX listings that enable market-neutral diversification.

Note: the current market maker proposals (TIP-17) establish the rate of diversification through Flowdesk. Treasure has used this program for years and successfully converted into stablecoins at a market neutral rate. On a day like today for example, where volumes w

====================================================================================================
[92] id=0x65b71a9f12e3e61887864ed936288f243fafc0c07e307d2ec2c3cfab4dbf4aa6  token=MAGIC  space=treasuregaming.eth  date=2025-07-28
TITLE: TIP-56: TIP-55 Re-Vote
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# SUMMARY
This proposal voids the linear unlock of the ecosystem fund and authorizes the core contributors to divest these tokens at market-neutral rates defined by TIP-17. Under the previous tokenomics the ecofund was unlocked linearly each month. This was estimated to be fully released to Treasure by December 2027. This proposal removes that unlock and makes the tokens available to the core contributors immediately from the date of this proposal passing. This proposal does not authorize the minting of additional tokens. **After this event, the circulating supply will increase from 311,795,218 to 337,855,447. Circulating supply will increase by 26,924,099 (8%) immediately.**


# RATIONALE
The Treasure team’s current stablecoin runway is until August 2026. This proposal does not reflect an immediate need for diversification for continued operations. We have recovered from our early 2025 setbacks with strength and are preparing for the long-term again. This proposal is to enable the DAO to be well prepared and funded going into the next few years, removing the linear unlock of the ecosystem fund that was created in 2021 when Treasure was a different organization. Our pivot and new goals require us to be flexible and will provide us the tools to strive in the coming years.

The original emissions schedule was created almost four years ago when MAGIC’s market cap was much smaller. We have learned many lessons during this time, especially the volatility of the MAGIC price. The li

====================================================================================================
[93] id=0x449d53b5971d5f4bf9f951215145ea7a72aa9a6e51679ff73d94432b539c866d  token=MAGIC  space=treasuregaming.eth  date=2025-08-27
TITLE: TIP-58: Vote to Sunset Canopy Development
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
This proposal implements the following:
1. Discontinuing the Bridgeworld project and Canopy 2.0 game
2. Legions holders would receive an airdrop of their original NFTs onto ArbitrumOne (details TBD)
3. MAGIC emissions currently allocated to Bridgeworld would be redirected to a marketing fund focused on engaging AI influencers and thought leaders to promote Treasure

# [Read Full Proposal and Rationale](https://forum.treasure.lol/t/tip-58-vote-to-sunset-canopy-development/206)

Voting Eligibility
The following holders of MAGIC can vote:
- (A) Stakers in the TreasureDAO [Governance Staking contract](https://governance-staking.treasure.lol/) on Arbitrum One.

gMAGIC will be calculated on a 1:1 basis in (A)

====================================================================================================
[94] id=0xfff62327c660d2fb00aa2c64898214e73e91410dbcb8a7e41be511f0b7f6a700  token=MAGIC  space=treasuregaming.eth  date=2026-02-01
TITLE: TIP-61: Autonomous Flywheel
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
Treasure has launched an initiative that has been several months in production called the Autonomous Flywheel. The Flywheel is a series of protocols spanning DeFi, Social, and Consumer powered by autonomous AI. This proposal establishes the fee policy for these dapps.
During current market conditions, revenue across Flywheel dapps will be converted into MAGIC and burnt with two exceptions: (1) burns will not occur if liquid runway for the DAO is below 18 months in USDC or highly-liquid assets like ETH, (2) the burn will not include the monthly opex costs for the DAO. These conditions ensure operational sustainability for the DAO.
With a solid liquid runway, the focus should currently shift to boosting the value of the treasury through a programmatic buy-and-burn strategy. In a future proposal, token holders can decide to use earned fees to buy back MAGIC for a vested ecosystem fund if the price of MAGIC has recovered to a level where additional burns would be wasteful in an opportunity cost sense.

# Proposal
This proposal authorizes Treasure contributors to engage in the following actions with accumulated fees:

- AI Frens Solana: this version of the platform will allow users to create 3D virtual characters through image uploads and text descriptions. Each character will have its own stream and chat interactivity immediately after launch. These AI Frens coins launch onto Pump.Fun, with TreasureDAO claiming the creator fees for each coin. Accumulated SOL will be con

====================================================================================================
[95] id=0x0d3c425df399250b1d4e9bee16e6725187ac0abccb2c04f8d929036e7f0ac60a  token=MAGIC  space=treasuregaming.eth  date=2026-02-17
TITLE: TIP-61: Autonomous Flywheel
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
Treasure has launched an initiative that has been several months in production called the Autonomous Flywheel. The Flywheel is a series of protocols spanning DeFi, Social, and Consumer powered by autonomous AI. This proposal establishes the fee policy for these dapps.
During current market conditions, revenue across Flywheel dapps will be converted into MAGIC and burnt with two exceptions: (1) burns will not occur if liquid runway for the DAO is below 18 months in USDC or highly-liquid assets like ETH, (2) the burn will not include the monthly opex costs for the DAO. These conditions ensure operational sustainability for the DAO.
With a solid liquid runway, the focus should currently shift to boosting the value of the treasury through a programmatic buy-and-burn strategy. In a future proposal, token holders can decide to use earned fees to buy back MAGIC for a vested ecosystem fund if the price of MAGIC has recovered to a level where additional burns would be wasteful in an opportunity cost sense.

# Proposal
This proposal authorizes Treasure contributors to engage in the following actions with accumulated fees:

- AI Frens Solana: this version of the platform will allow users to create 3D virtual characters through image uploads and text descriptions. Each character will have its own stream and chat interactivity immediately after launch. These AI Frens coins launch onto Pump.Fun, with TreasureDAO claiming the creator fees for each coin. Accumulated SOL will be con

====================================================================================================
[96] id=0xda4d79297e9af12964d4389c12e6688ada797b8726dfd103baa506743e6d46dd  token=MAGIC  space=treasuregaming.eth  date=2026-02-27
TITLE: TIP-61: Autonomous Flywheel
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
Treasure has launched an initiative that has been several months in production called the Autonomous Flywheel. The Flywheel is a series of protocols spanning DeFi, Social, and Consumer powered by autonomous AI. This proposal establishes the fee policy for these dapps.
During current market conditions, revenue across Flywheel dapps will be converted into MAGIC and burnt with two exceptions: (1) burns will not occur if liquid runway for the DAO is below 18 months in USDC or highly-liquid assets like ETH, (2) the burn will not include the monthly opex costs for the DAO. These conditions ensure operational sustainability for the DAO.
With a solid liquid runway, the focus should currently shift to boosting the value of the treasury through a programmatic buy-and-burn strategy. In a future proposal, token holders can decide to use earned fees to buy back MAGIC for a vested ecosystem fund if the price of MAGIC has recovered to a level where additional burns would be wasteful in an opportunity cost sense.

# Proposal
This proposal authorizes Treasure contributors to engage in the following actions with accumulated fees:
- Summon (summon.wtf): An updated version of AI Frens on Base that allows character creators to launch autonomous OpenClaw versions of their agents after $100K trading volume is passed. Summon collects protocol fees on each trade
- AI Frens Solana: this version of the platform allows users to create 3D virtual characters through image uploads and text descri

