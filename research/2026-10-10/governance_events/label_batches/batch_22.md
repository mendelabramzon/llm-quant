# Labeling packets — batch 22 (104 proposals). Label each against criteria.md.

====================================================================================================
[0] id=0x814c08dfbd4bacfc0265df159b344269912f7d8437b0194040f99654eb8b3b87  token=TREE  space=treehousefi.eth  date=2025-09-17
TITLE: Snapshot 2: Requesting TREE Budget for Community Incentives
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# TIP 2: Requesting TREE to Support Community Incentives  

## Summary  
This proposal seeks the release of **65,000 TREE** from the Community Rewards pool to fund three initiatives:  
- 25,000 TREE for an October community campaign  
- 25,000 TREE for emissions to the TREE/WETH Balancer LP gauge (10 weeks)  
- 15,000 TREE for emissions to the tAVAX/sAVAX Balancer LP gauge (8 weeks)  

The goal is to strengthen ecosystem awareness, deepen liquidity for TREE, and support early adoption of tAVAX.  

## Motivation  
The TREE tokenomics framework reserves a portion of TREE for *Community Rewards* to drive adoption, engagement, and ecosystem participation. TIP 2 activates this allocation to:  
- Expand Treehouse’s visibility through a coordinated campaign  
- Enhance TREE/WETH liquidity to improve trading efficiency  
- Incentivize adoption of tAVAX with LP rewards  

## Specification  
If approved, this proposal will:  
- Release **65,000 TREE** from the Community Rewards pool  
- Distribute funds as follows:  
  - 25,000 TREE → Campaign Payout Wallet (0x2f1AdA0F53AF3c91cA01f50818e5105029668F9B)  
  - 25,000 TREE → LP Incentives Wallet for Balancer gauge on Ethereum  
(0x6544A8a535C15eC75e7960Ced87Cf7bBE6fE86d9)
  - 15,000 TREE → LP Incentives Wallet for Balancer gauge on Avalanche  
(0x6544A8a535C15eC75e7960Ced87Cf7bBE6fE86d9)
- Transfers executed directly from the Community Rewards multisig to designated wallets  

## Voting Options  
- **For** – Approve the release of 65,000 T

====================================================================================================
[1] id=0xb075c81e73baf669c60c5f74ce704acbd3f12f2b723dfd7d8ac7032d1d184046  token=TREE  space=treehousefi.eth  date=2025-11-11
TITLE: Snapshot 4: Proposal for TREE Token Buybacks with Protocol Revenue
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary

This proposal seeks community approval to allocate **50% of all protocol fees generated from tETH MEY** toward recurring **open-market purchases of TREE**, the native governance token of the Treehouse ecosystem.

The objective is to **strengthen alignment** between **protocol adoption** and **long-term tokenholder value** by accumulating TREE in the DAO treasury.

If approved, all **repurchased tokens** will be held as **DAO reserves**, reducing effective circulating supply and reinforcing the protocol’s self-sustaining growth model.

**Token Details:**

-   **Token**: Treehouse (TREE)
    
-   **Network**: Ethereum (ERC-20)
    
-   **Address**: 0x77146784315ba81904d654466968e3a7c196d1f3
    
-   **Etherscan**: https://etherscan.io/token/0x77146784315ba81904d654466968e3a7c196d1f3
    

# Motivation

As Treehouse continues to expand its ecosystem of **tAssets** and **Decentralized Offered Rates (DOR)**, protocol revenue from **Market Efficiency Yield (MEY)** fees has become a recurring and scalable source of income.

Currently, the protocol charges a 20% fee on MEY generated across all tAssets, providing a **sustainable revenue stream** that grows proportionally with adoption.

Implementing a buyback mechanism allows the DAO to:

-   **Strengthen** the intrinsic link between **protocol success** and **tokenholder value**.
    
-   Establish a **deflationary mechanism** that reduces circulating supply over time.
    
-   Build a **strategic reserve of TREE** that ca

====================================================================================================
[2] id=0x898af59b849a5211c6bc15182d55f062f23224055aaa050714adc46b220332d6  token=TREE  space=treehousefi.eth  date=2025-12-01
TITLE: Snapshot 5: Establishing TREE–AVAX Concentrated Liquidity Pool on Avalanche
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
This proposal seeks community approval to establish a **TREE–AVAX Concentrated Liquidity Pool** on **Blackhole** within the **Avalanche** network, providing deep and efficient liquidity for TREE on Avalanche.

In addition, this proposal requests **20,000 TREE** from the ***Liquidity Provision*** portion of TREE’s token allocation to seed the initial liquidity for the pool.

# Motivation
Treehouse has expanded its tAsset product suite to Avalanche with **tAVAX**, but there is **currently no native liquidity venue for TREE on Avalanche**. This limits the ability of Avalanche users to acquire TREE directly or participate meaningfully in governance.

Establishing this pool will:
- **Enable** users on Avalanche to swap **TREE** directly with **AVAX** and vice-versa, increasing accessibility and liquidity depth.
- **Support** users who wish to participate in liquidity pools and earn TREE emissions, as introduced in [TIP 2](https://governance.treehouse.finance/t/tip-2-requesting-tree-budget-for-community-incentives/20).
- **Position** TREE more deeply within the Avalanche DeFi ecosystem, opening pathways for additional integrations across liquidity venues and partner protocols.

This initiative strengthens the connection between Avalanche users and the broader Treehouse ecosystem.

# Specification
**Pool Details**
- **Type**: Blackhole CL200 Pool
- **Pair**: TREE / AVAX
- **Chain**: Avalanche

**Seed Liquidity**
- **Amount Requested**: 20,000 TREE
- **Source**: *Liquidity

====================================================================================================
[3] id=0x3ecd1a8de7ef4c23885848d51792e190110466565cb2b7e57d338b3c092ebe72  token=TREE  space=treehousefi.eth  date=2026-01-08
TITLE: Snapshot 6: Mesh Bridging of Treehouse Assets
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Summary

This proposal seeks community approval to implement **mesh bridging** for all Treehouse assets, including **tETH, tAVAX, and TREE**, across the following networks:

- Ethereum
- Arbitrum
- Base
- Avalanche
- BNB

Mesh bridging enables direct asset transfers between any supported chain pair, removing the need to route through Ethereum. If approved, Treehouse will deploy this infrastructure using **Chainlink CCIP** to ensure secure, consistent, and transparent cross-chain transfers.

## Motivation

Treehouse’s fixed income ecosystem is expanding across multiple networks, with tETH, tAVAX, and TREE now deployed across Ethereum, Arbitrum, Avalanche, Base, and BNB.

Currently, bridging paths are limited, with Ethereum acting as the primary routing layer. For example, users can bridge tETH from Ethereum to Arbitrum or Base, but cannot bridge directly between Arbitrum and Base.

By adopting a mesh bridging architecture, Treehouse can:

- Enable direct bridging routes between any supported chain pairs, minimizing fees and improving routing efficiency
- Allow liquidity to flow more freely across networks, supporting tAsset integrations and TREE market depth
- Improve the user experience for multi-chain yield strategies and governance participation

This proposal supports Treehouse’s goal of building fixed income infrastructure that scales efficiently across ecosystems.

## Specification

If approved, this proposal will:

- Implement mesh bridging for the following Treehous

====================================================================================================
[4] id=0xd3a90d0ee34775c1112f7456ba5155dab4c0c82ab5e51db324e618d6212815f7  token=TREE  space=treehousefi.eth  date=2026-05-13
TITLE: TIP 9: Redirecting tETH Protocol Revenue Toward Ecosystem Growth
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Summary

This proposal seeks DAO approval to redirect the portion of protocol revenue currently allocated to TREE buybacks under [TIP 4](https://governance.treehouse.finance/t/tip-4-proposal-for-tree-token-buybacks-with-protocol-revenue/24) toward ecosystem growth, development, and strategic initiatives that strengthen Treehouse's long-term position.

If approved, the protocol fees generated from tETH Market Efficiency Yield (MEY) currently used for open-market TREE buybacks will instead be retained by the protocol for broader ecosystem deployment.

Buybacks funded under TIP 4 will be paused as a result of this reallocation, effective from the date this proposal passes on Snapshot. All TREE accumulated in the existing buyback wallet will remain intact as long-term DAO reserves.

## Motivation

Since TIP 4 passed, broader market conditions and the protocol's strategic priorities have continued to evolve. The DAO sees an opportunity to direct protocol revenue toward initiatives that may compound long-term value more efficiently than continuous open-market buybacks under current conditions.

Redirecting this share of revenue allows the DAO to:

-   **Preserve capital flexibility** to deploy revenue where it generates the most ecosystem leverage during the current market phase.
    
-   **Reinforce protocol-level growth** by channeling fees back into liquidity depth, integration support, as well as tAsset and Decentralized Offered Rates (DOR) adoption programs.
    
-   **Main

====================================================================================================
[5] id=0x275eeb63c31ad14467a18c5290961c89bf8658e7b979ebf26ef63ccd32c805da  token=TREE  space=treehousefi.eth  date=2026-06-27
TITLE: Snapshot 11: TREE Bridging to HyperEVM and tHYPE Liquidity Incentives
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Summary

This proposal seeks DAO approval for two related initiatives that support Treehouse's expansion to HyperEVM:

- Enable bridging of TREE to HyperEVM via Chainlink CCIP, alongside existing supported networks (Ethereum, Arbitrum, Base, Avalanche, and BNB)
- Allocate 50,000 TREE from the Community Rewards allocation to fund a 2-month TREE emissions program for tHYPE, distributed via Merkl

Together, these initiatives extend TREE's cross-chain reach to HyperEVM and support early adoption of tHYPE through targeted incentives.

## Motivation

**TREE Bridging to HyperEVM**

As Treehouse expands its tAsset ecosystem to HyperEVM, extending TREE's mesh bridging architecture to the network ensures consistency across all chains where Treehouse operates.

Enabling TREE bridging to HyperEVM via CCIP allows:

- HyperEVM users to access TREE for governance participation and ecosystem utility
- TREE to operate consistently across Treehouse-supported networks
- Treehouse to maintain alignment with the CCIP-based mesh bridging architecture established under [TIP 6](https://governance.treehouse.finance/t/tip-6-mesh-bridging-of-treehouse-assets/26/3)

**tHYPE Incentive Program**

tHYPE is a newly launched tAsset in Treehouse, and early liquidity depth is critical to its adoption curve.

A targeted TREE emissions program is intended to:

- Support early TVL growth for tHYPE
- Improve the competitiveness of tHYPE during its initial growth phase
- Increase visibility and adoption of Treeh

====================================================================================================
[6] id=0x3cfe8e581c090f1172c3dedeb5abf00a43c27e363ffc888438593102b854dc0f  token=TREE  space=treehousefi.eth  date=2026-08-02
TITLE: Snapshot 12: Supporting Ecosystem Growth Through Community Rewards
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary

This proposal seeks DAO approval to allocate **15,000,000 TREE** from the Community Rewards allocation to fund ecosystem growth initiatives over the next 12 months.

The budget is intended to support initiatives that **expand adoption of Treehouse's products and infrastructure**, including tAssets, Decentralized Offered Rates (DOR), and broader ecosystem growth opportunities.

# Motivation

As Treehouse continues expanding across multiple products, networks, and integrations, growth opportunities increasingly arise throughout the year. Establishing a dedicated ecosystem budget allows the protocol to respond to these opportunities more efficiently while remaining within the Community Rewards allocation approved by the DAO.

The budget is intended to support three primary areas:

1.  **tAsset adoption**  
    Fund incentive programs that grow TVL, liquidity depth and adoption across existing and future tAssets, including tETH, tAVAX, tHYPE and subsequent protocol deployments
    
2.  **DOR participation**  
    Support programs that increase participation in Treehouse's Decentralized Offered Rates through TREE delegation and ecosystem engagement, strengthening the adoption and credibility of DOR rates such as TESR, TELR, and TEBR
    
3.  **Ecosystem Growth**  
    Support strategic integrations, partnerships, campaigns, and other initiatives that strengthen the broader Treehouse ecosystem
    

The DAO retains authority to revise the budget, its permitted uses, or f

====================================================================================================
[7] id=0x1d2df6f40d6c22c1805e30362cb06ae446d07b243657dc6de69185c0f04906f3  token=TRU  space=truefigov.eth  date=2023-05-19
TITLE: Adjust stkTRU rewards before they run out
CHOICES: Yes, set rewards to 0 | No, keep at 125k TRU per day | Abstain
TEXT (first 1500 characters):
Summary

stkTRU rewards are set to run out in ~7 days. On-chain governance needs to decide between minting TRU needed to refill the distributor, or turning off stkTRU rewards.

Background

The current stkTRU rewards rate is 125,000 TRU/day.  At current, stakers are receiving ~33% ROI in return for staking.

Stakers have exposure to one loan – a tfUSDC loan to TrueTrading due July 24.
It is not expected that stakers will have exposure to additional new loans in the near future. stkTRU is needed to participate in TrueFi on-chain governance votes.

Next steps

We propose to disable TRU rewards / set it to 0 TRU / day, empty the distributor and send the remaining funds (currently ~1 mm TRU) to TrueFi DAO Treasury (Timelock).

Option 1: Yes, I support setting rewards to 0 and sending the remaining balance to the DAO treasury
Option 2: No, I support leaving rewards at 125k TRU per day
Option 3: Abstain

====================================================================================================
[8] id=0x36fd8860300b8ef0f73c209730741ab54b3dcc1571182937faf6889ec6bcb7c5  token=TRU  space=truefigov.eth  date=2023-05-25
TITLE: Send TRU to fulfill Sushi rewards for TRU-WETH LPs
CHOICES: Yes, I approve | No | Abstain
TEXT (first 1500 characters):
## Summary
If approved, this proposal will transfer 787,835 TRU from treasury funds to the Sushi TRU-WETH rewarder contract (0xc0482b9d1ff34f7cd98e3a0a4584298492acf550).

## Background
A total of 787,830 TRU rewards is due to Sushi the TRU-WETH rewarder as shown on https://rewarders.sushibackup.com/browse/1/8

To view TRU rewards due to each address, see the spreadsheet here:
https://docs.google.com/spreadsheets/d/1pVsPyy35i7Qq4irJcUBomgNHJ7zko0JwK1iEq90XS5g/edit?usp=sharing

TRU reward allocations to Sushi have ended, and this proposal aims to fulfill all TRU rewards due to previous LPs on Sushi. It would send 787,835 TRU (5 TRU more than the total shown on Sushi's UI) to ensure all TRU is covered.

====================================================================================================
[9] id=0xf6fa21dd7a6cdcae9e544e5b4eec47b2fda93f035e9e7a9e91a773133b850075  token=TRU  space=truefigov.eth  date=2023-07-05
TITLE: Send TRU to fulfill Sushi rewards for TRU-WETH LPs [second attempt]
CHOICES: Yes, I approve | No | Abstain
TEXT (first 1500 characters):
## Summary
This is the second attempt for this proposal. The [original proposal](https://snapshot.org/#/truefigov.eth/proposal/0x36fd8860300b8ef0f73c209730741ab54b3dcc1571182937faf6889ec6bcb7c5) did not meet quorum.

If approved, this proposal will transfer 787,835 TRU from treasury funds to the Sushi TRU-WETH rewarder contract (0xc0482b9d1ff34f7cd98e3a0a4584298492acf550).

## Background
A total of 787,830 TRU rewards is due to Sushi the TRU-WETH rewarder as shown on https://rewarders.sushibackup.com/browse/1/8

To view TRU rewards due to each address, see the spreadsheet here:
https://docs.google.com/spreadsheets/d/1pVsPyy35i7Qq4irJcUBomgNHJ7zko0JwK1iEq90XS5g/edit?usp=sharing

TRU reward allocations to Sushi have ended, and this proposal aims to fulfill all TRU rewards due to previous LPs on Sushi. It would send 787,835 TRU (5 TRU more than the total shown on Sushi's UI) to ensure all TRU is covered.

====================================================================================================
[10] id=0x54e399f0a1cf04d0b84a607ffed8e10330ce189448496f1996317055cc3d6296  token=TRU  space=truefigov.eth  date=2023-08-07
TITLE: Protocol Fee Change for tfBILL Integration
CHOICES: Yes, I approve | No | Abstain
TEXT (first 1500 characters):
Author: Adapt3r Digital

### Specification and Requirements:
Waive the protocol fee for tfBILL for the first 90 days and reduce protocol fee to 0.20% indefinitely.

### Summary:
This proposal seeks approval for a protocol fee holiday for the upcoming launch of the tfBILL product.

We believe hosting a scalable, liquid, low-risk strategy like tfBILL will benefit the liquidity and success of all current and future vaults on TrueFi, and given the magnitude of its strategic importance, we are seeking a reduction of the standard 0.50% protocol fee to 0.20% along with a 90 day fee holiday. This change will not affect existing products.

### Motivation:
Adapt3r Digital, a forward-thinking asset manager, is seeking to make the tfBILL product central to the TrueFi ecosystem. In the last six months, tokenized treasury bill products have become a highly competitive space.

====================================================================================================
[11] id=0x5cea6424b1aebb904a0259775fee15b4e038b6469194c97848f71d1fe855e061  token=UMA  space=uma.eth  date=2023-08-11
TITLE: Partnership Proposal: oStake
CHOICES: Yes | No
TEXT (first 1500 characters):
This proposal introduces oStake, a novel staking contract that dynamically optimizes staking rewards based on Key Performance Indicators (KPIs). Overcoming the limitations of traditional staking models and UMA’s KPI options, oStake continuously adjusts rewards according to set KPIs to create a more dynamic, engaging, and efficient system for incentive mechanisms while maintaining the UX simplicity of traditional staking contracts.

The on-chain vote will be to send the requested funding for the milestones to the Risk Labs foundation’s multi-sig, which will custody the total $UMA balance for this proposal and be responsible for confirming payouts at each milestone.

This proposal seeks a confirmation on the proposed roadmap and budgeting by the UMA Community, and delegating Risk Labs the decision making power over the completion of the milestones.

To ensure transparency and community participation, Inverter team will post an update to UMA community forum for every confirmed milestone.

Transfer 50,000 UMA to the Risk Labs Multi-sig:  0x8180D59b7175d4064bDFA8138A58e9baBFFdA44a

====================================================================================================
[12] id=0x882b8be47b5eb518ee03645d22ab68b46355d658ce99c519c872f9d6fb6a7de8  token=UMA  space=uma.eth  date=2023-08-17
TITLE: Partnership Proposal: oStake
CHOICES: Yes | No
TEXT (first 1500 characters):
This proposal introduces oStake, a novel staking contract that dynamically optimizes staking rewards based on Key Performance Indicators (KPIs). Overcoming the limitations of traditional staking models and UMA’s KPI options, oStake continuously adjusts rewards according to set KPIs to create a more dynamic, engaging, and efficient system for incentive mechanisms while maintaining the UX simplicity of traditional staking contracts.

The on-chain vote will be to send the requested funding for the milestones to the Risk Labs foundation’s multi-sig, which will custody the total $UMA balance for this proposal and be responsible for confirming payouts at each milestone.

This proposal seeks a confirmation on the proposed roadmap and budgeting by the UMA Community, and delegating Risk Labs the decision making power over the completion of the milestones.

To ensure transparency and community participation, Inverter team will post an update to UMA community forum for every confirmed milestone.

Transfer 50,000 UMA to the Risk Labs Multi-sig: 0x8180D59b7175d4064bDFA8138A58e9baBFFdA44a

====================================================================================================
[13] id=0x129e5dddc5ef34d70d03200c3b6d0a9423c0255d32678b75192bb8ad9690daf0  token=UMA  space=uma.eth  date=2024-03-07
TITLE: Request for Gas Rebate Program Refund
CHOICES: YES | NO
TEXT (first 1500 characters):
# Request for Gas Rebate Program Refund
## Summary
This proposal seeks approval from the UMA DAO to refund the [Risk Labs Foundation](https://risklabs.foundation/) for the expenses incurred through the [gas rebate program](https://medium.com/uma-project/voter-gas-fee-rebate-program-f9cce3391cb5). Over the past years, Risk Labs has supported the UMA protocol by providing gas rebates to incentivize community participation in voting. As the costs have accumulated, we now request a refund to ensure the continuation of this rebate program and the sustainability of the UMA ecosystem.
## Motivation
The gas rebate program has played a crucial role in increasing voter participation, encouraging community involvement, and maintaining the integrity of the UMA protocol. To date, Risk Labs has disbursed a total of 75,705.70 UMA tokens and 39.255 ETH in rebates. This was a cost of ~$576k USD at the time of the transaction. The costs associated with this program have risen significantly due to factors such as the rally in ETH, fluctuating gas prices, and increased community participation. To ensure this rebate program can continue, which aids in the adoption of the UMA protocol, we believe it is essential to seek reimbursement for these operational expenses.
## Refund Calculation Methodology
The proposal employs the following method for the refund calculation: Gas rebates paid in UMA will be refunded in UMA tokens. Gas rebates paid in ETH will be converted into UMA tokens based on the histo

====================================================================================================
[14] id=0xb6aa075fde3114a40a6a4a52e762d6d22e430c775fbca46be7f6768231f271c3  token=UMA  space=uma.eth  date=2025-02-13
TITLE: UMA Emissions Reduction
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
**Title:** UMA Emissions Reduction
**Authors:** Dylan O’Reilly, Lee Poettcker, Chase Coleman
**Status:** Proposed to Snapshot
--------------------------------------------------------------------------

### Summary

The UMA DAO should initiate a measured reduction in the current emissions rate to help optimize UMA’s token economics whilst maintaining a robust voting base to ensure protocol security and viability.

### Motivation & Rationale

The current emissions are providing UMA stakers with an APY exceeding 27% per annum.
This is quite high relative to rates you can earn in the market today (ETH: ~5%, Stables: ~15%). Details on our current emissions:

- Emissions Rate: 0.18 UMA per second (5,676,480 UMA per annum) (source: Etherscan)
- Circulating Supply: 84,605,309 UMA (source: CoinGecko)
- Current Inflation Rate: 6.7%
- Cumulative Stake: 21.6M UMA
- Current APY: ~26%
- 30 Day Average Voters (Dec 2024): 280
- 30 Day Average Voting Power (Dec 2024): 18.4M UMA
- Participation Rate (Dec 2024): 22% (Voting Power / Circulating Supply)

There are several reasons why we think the UMA DAO should reduce emissions:

**1. Potential Overpayment:** Our current emissions may be higher than necessary to maintain our current staking and voter base.
**2. Staker/ Voter Inelasticity:** We believe the voting base is relatively inelastic and will likely remain stable even with reduced rates. UMA voters will still earn handsome rewards for their participation in the voting process even if curre

====================================================================================================
[15] id=0xfd0f453660188b4ed6157be5c8844db7fbdedffd4550a3b94e50c22ade78b8f6  token=UMA  space=uma.eth  date=2025-02-25
TITLE: UMA Emissions Reduction - Roll 1
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
**Title:** UMA Emissions Reduction
**Authors:** Dylan O’Reilly, Lee Poettcker, Chase Coleman
**Status:** Proposed to Snapshot
-------------------------------------------------------------------------------

### Summary:
The UMA DAO should initiate a measured reduction in the current emissions rate to help optimize UMA’s token economics whilst maintaining a robust voting base to ensure protocol security and viability.

### Motivation & Rationale:
The current emissions are providing UMA stakers with an APY exceeding 27% per annum.
This is quite high relative to rates you can earn in the market today (ETH: ~5%, Stables: ~15%). Details on our current emissions:

- Emissions Rate: 0.18 UMA per second (5,676,480 UMA per annum) (source: Etherscan)
- Circulating Supply: 84,605,309 UMA (Source: CoinGecko)
- Current Inflation Rate: 6.7%
- Cumulative Stake: 21.6M UMA
- Current APY: ~26%
- 30 Day Average Voters (Dec 2024): 280
- 30 Day Average Voting Power (Dec 2024): 18.4M UMA
- Participation Rate (Dec 2024): 22% (Voting Power / Circulating Supply)

There are several reasons why we think the UMA DAO should reduce emissions:

**1. Potential Overpayment:** Our current emissions may be higher than necessary to maintain our current staking and voter base.
**2. Staker/ Voter Inelasticity:** We believe the voting base is relatively inelastic and will likely remain stable even with reduced rates. UMA voters will still earn handsome rewards for their participation in the voting process even if

====================================================================================================
[16] id=0xcf846712903525879719d6af6e94d416f68b5c536ed52a9997134cb537722f81  token=UMA  space=uma.eth  date=2025-03-28
TITLE: Gas Rebate Program Refund | Jan 2024 - Dec 2024
CHOICES: Yes | No
TEXT (first 1500 characters):
# Request for Gas Rebate Program Refund – 2024

# Summary
This proposal seeks approval from the UMA DAO to refund the [Risk Labs Foundation ](https://risklabs.foundation/) for expenses incurred through the gas rebate program during 2024. Following the successful approval of last year’s refund request, which covered the period from September 2020 to December 2023, Risk Labs has continued supporting the UMA protocol by covering gas costs to incentivize community participation in voting. To ensure the sustainability of this rebate program and the broader UMA ecosystem, we request reimbursement for the gas rebates distributed throughout 2024.

# Motivation
The gas rebate program has been instrumental in driving voter engagement, strengthening community involvement, and maintaining the security and integrity of the UMA protocol. Over the course of 2024, Risk Labs has disbursed a total of **184.235 ETH** in gas rebates. These expenses have been affected by fluctuations in gas prices, ETH market movements, and increased community participation.

Given the ongoing importance of this program and its demonstrated impact on governance participation, Risk Labs believes it is essential to continue seeking reimbursement for these operational expenses to ensure the long-term adoption and growth of the UMA ecosystem.

# Refund Calculation Methodology
The refund calculation follows the same methodology as the previously approved proposal:

- Gas rebates paid in **UMA** will be refunded in **U

====================================================================================================
[17] id=0xf7307fe889b65d99acdc9af34acbeeac0dedd5af41665c05c41e877e00333e48  token=UMA  space=uma.eth  date=2025-05-06
TITLE: UMA Emissions Reduction - Roll 2
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
Title: UMA Emissions Reduction
Authors: Dylan O’Reilly, Lee Poettcker, Chase Coleman
Status: Proposed to Snapshot
Discussion: [Forum 1](https://discourse.uma.xyz/t/uma-emissions-reduction/2140) | [Forum 2](https://discourse.uma.xyz/t/uma-emissions-reduction-2/2185) 
------------------

# Summary:

The UMA DAO should initiate a measured reduction in the current emissions rate to help optimize UMA’s token economics whilst maintaining a robust voting base to ensure protocol security and viability.

# Motivation & Rationale:
The current emissions are providing UMA stakers with an APY exceeding 27% per annum.
This is quite high relative to rates you can earn in the market today (ETH: ~5%, Stables: ~15%). Details on our current emissions:

- Emissions Rate: 0.18 UMA per second (5,676,480 UMA per annum) (source: Etherscan)
- Circulating Supply: 84,605,309 UMA (Source: CoinGecko)
- Current Inflation Rate: 6.7%
- Cumulative Stake: 21.6M UMA
- Current APY: ~26%
- 30 Day Average Voters (Dec 2024): 280
- 30 Day Average Voting Power (Dec 2024): 18.4M UMA
- Participation Rate (Dec 2024): 22% (Voting Power / Circulating Supply)

There are several reasons why we think the UMA DAO should reduce emissions:

1. Potential Overpayment: Our current emissions may be higher than necessary to maintain our current staking and voter base.
2. Staker/ Voter Inelasticity: We believe the voting base is relatively inelastic and will likely remain stable even with reduced rates. UMA voters will still earn ha

====================================================================================================
[18] id=0x5e036f2a5848ac5c3e1a966f526c3070c1d7b2963d2bc66b610c22dfe2df11d1  token=UMA  space=uma.eth  date=2026-09-04
TITLE: Request to refund 37,875 USDC.e burned by self-disputing 86 poisoned requests
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
**Community proposal**  
  
Title: Request to refund 37,875 USDC.e burned by self-disputing 86 poisoned requests.  
Author: dmitry_kuzmin.  
Status: Proposed to Snapshot

---

I run an automated proposer on Polygon, `0xa0b6210f5b522b97bbce9b8e617627105c0e3891`. On 10-11 August I proposed on 88 price requests that existed only to trap bonds. All 88 are disputed/settled now. I’m asking the DAO to return the **37,875 USDC.e** that gets burned to the treasury as a result.

**What happened**  
Someone copied live Polymarket markets in bulk. Between blocks 91786519 and 91812941 — about fifteen hours on 10-11 August — 7,605 duplicate requests went onto the oracle, one transaction each, each aimed at a different market. My bot proposed on 88 of them, which is 1.2% of the batch.

A question’s identity is the hash of its ancillary data, and Polymarket’s ancillary ends with the address that created it. Copy a real question, add one more address on the end, and the hash changes: the oracle sees a new question even though every word describing the market is identical. The extra address is `0d14e9a9bb646ff0b23f610dd3a50fc9f40cd336`, and it’s on all  
7,605 of them. Real Polymarket questions have one creator address at the end. These have two.

The 88 that reached me went in through Polymarket’s own adapter at `0x65070BE9…`, with zero reward and a challenge window of a billion seconds. That’s 31.7 years, so they’d have become settleable in April 2058. Real Polymarket sports requests that we

====================================================================================================
[19] id=Qme9MASbuzrX2W6o7e4CCKqQiLGS5yuBLmX8wkeM5awcio  token=UNI  space=uniswapgovernance.eth  date=2021-05-28
TITLE: Managing Systemic Risk in Uniswap's Community Treasury using KPI Options
CHOICES: Proceed to Consensus Check | Do Not Proceed
TEXT (first 1500 characters):
# Summary

## Problem

Uniswap's governance treasury will retain 43% of $UNI supply vested over 4 years, currently allocated 113 million in $UNI. Current value ~ ****$2.724 Billion USD. Max drawdown starting on May 3 2021, in 20 days $UNI lost 71% of it's value, a loss of ~ **$3.616 Billion USD.**
We need to manage this systemic risk and volatility for the long term success of the community treasury. 

## Solution

Partial divestment of Uniswap governance treasury by using UMA Synthetic KPI Options to create a win for the treasury, a win for the protocol and a win for the stakeholders. Long term goal would be to put together an actively managed portfolio for the treasury aka uniHOUSE.

TLDR: 

![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/be190280-346d-46c8-beac-5d2827c06bf8/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210528%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210528T202056Z&X-Amz-Expires=86400&X-Amz-Signature=cfc327266e06a5aabb9ad5174b4d9af87fedf6bfa6d811e30f023af337d92920&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22)

# Background

## Yam.Finance

[Yam.finance](http://yam.finance) has been leading the charge on treasury management for DAOs via our project DAO House: [https://yamfinance.medium.com/yam-finance-presents-dao-house-86625f9bae5a](https://yamfinance.medium.com/yam-finance-presents-dao-house-86625f9bae5a)

We've realized that there are significant system

====================================================================================================
[20] id=QmXDNKm4feLGUXCdtHjHZYrNTMsysEhP34nRYFSM3HhKVT  token=UNI  space=uniswapgovernance.eth  date=2021-06-14
TITLE: Temperature Check - Managing Systemic Risk in Uniswap’s Community Treasury using KPI Options
CHOICES: Pass Temperature Check | Do Not Pass
TEXT (first 1500 characters):
### Author: Feddas@Yam.Finance
### Forum Post: https://gov.uniswap.org/t/temperature-check-should-we-be-managing-systemic-risk-in-uniswaps-community-treasury-using-kpi-options/12624

# Summary

## Problem

Uniswap's governance treasury will retain 43% of $UNI supply vested over 4 years, currently allocated 113 million in $UNI. Current value ~ ****$2.724 Billion USD. Max drawdown starting on May 3 2021, in 20 days $UNI lost 71% of it's value, a loss of ~ **$3.616 Billion USD.**
We need to manage this systemic risk and volatility for the long term success of the community treasury. 

## Solution

Partial divestment of Uniswap governance treasury by using UMA Synthetic KPI Options to create a win for the treasury, a win for the protocol and a win for the stakeholders. Long term goal would be to put together an actively managed portfolio for the treasury aka uniHOUSE.

TVL Metric is only an example. There have been suggestions on using other metrics to measure the KPI for this option. It is currently an open issue which  we can delve into more after the temperature check.

### TLDR:

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/be190280-346d-46c8-beac-5d2827c06bf8/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/be190280-346d-46c8-beac-5d2827c06bf8/Untitled.png)

# Background

## Yam.Finance

[Yam.finance](http://yam.finance) has been leading the charge on treasury management for DAOs via our project DAO House: [https://yamfinance.medium.

====================================================================================================
[21] id=QmQbcxLpGENeDauCAsh3BXy9H9fiiK46JEfnLqG3s8iMbN  token=UNI  space=uniswapgovernance.eth  date=2021-06-22
TITLE: Temp Check: Larger Grant Construct // CEA + No Negative Net UNI
CHOICES: Yes | No
TEXT (first 1500 characters):
Uniswap should grant $25M to fund Flipside Community-Enabled Analytics via a sustainable yield-generating investment strategy that:
1. Produces analytics that drive user education and customer growth
2. Allocates UNI to participants through bounties, increasing liquidity
3. Uses Uniswap’s own yield mechanisms to enable a largely self-funded program

Forum Post >> https://gov.uniswap.org/t/temperature-check-larger-grant-program-construct-community-enabled-analytics-no-negative-net-uni/13044

====================================================================================================
[22] id=QmX6y6Koqc82o7TSSnmw793RbyJMUfrRStr1wsTvCy4Ynj  token=UNI  space=uniswapgovernance.eth  date=2021-07-10
TITLE: Temperature Check - Allocate 1.5M UNI to Go-Ethereum long-term Talent-Acquisition & Retention Grant (GETH-TARG)
CHOICES: Yes, allocate funding to Geth | No, do not fund Geth
TEXT (first 1500 characters):
Should the Uniswap DAO becomes the first of many Ethereum DAOs to allocate a portion of their treasury (1.5M UNI) towards Ethereum client development, which is crucial infrastructure to the Ethereum ecosystem and is developed solely from public goods funding from the ecosystem [while also complex and requires specialized talent to build on], in hopes that others follow suit in correctly allocating the necessary funds to incentivize the talent needed to build complex open-source infrastructure?

Full proposal: https://gov.uniswap.org/t/temperature-check-allocate-1-5m-uni-to-go-ethereum-long-term-talent-acquisition-retention-grant-geth-targ/13265

====================================================================================================
[23] id=QmTksCuBh2HLMKSXUE7yyCHGE9dCevac9oEWnkef8Junn2  token=UNI  space=uniswapgovernance.eth  date=2021-07-18
TITLE: Temperature Check - [Merge the Uniswap Grant Program into Uniswap DAO Governance]
CHOICES: Yes; Merge Grants and UNI DAO | No
TEXT (first 1500 characters):
View the proposal here:

https://gov.uniswap.org/t/temperature-check-merge-the-uniswap-grant-program-into-uniswap-dao-governance/13511

====================================================================================================
[24] id=QmVnsMXvSG84x3u2iYZ3nGWeXU4pRcfuKWwXnyjpD9j6To  token=UNI  space=uniswapgovernance.eth  date=2021-07-19
TITLE: Turning on the fee switch for V2
CHOICES: Yes, lets do it! | No
TEXT (first 1500 characters):
Should we turn the fee switch on for V2 and establish, "Buyback and Keep" model?

====================================================================================================
[25] id=QmRKpArENVfj7bUaXuEj2QUqZCB5ZJGc9VDmNvyfTKnAKf  token=UNI  space=uniswapgovernance.eth  date=2021-07-26
TITLE: Consensus Check - Create Uniswap Volume KPI Options to help divest Uniswap’s Community Treasury into Stablecoins
CHOICES: Approve | Deny
TEXT (first 1500 characters):
Please read the proposal on the forums: 

https://gov.uniswap.org/t/consensus-check-create-uniswap-volume-kpi-options-to-help-divest-uniswap-s-community-treasury-into-stablecoins/13533

Thank you. 

Feddas

====================================================================================================
[26] id=QmP3H8WGLiWTP2WumKyrq8yA1xz1XbwkT8brdGYePuAcES  token=UNI  space=uniswapgovernance.eth  date=2021-10-24
TITLE: Consensus Check - Add 1 Basis Point Fee Tier
CHOICES: Add 1bps fee tier (1 tick) | No change
TEXT (first 1500 characters):
# Consensus Check - Add 1 Basis Point Fee Tier 

## TLDR:
Uniswap should add a 1bps fee tier with 1 tick spacing. This change is straightforward from a technical perspective and would help Uniswap compete in stablecoin <> stablecoin pairs, where the majority of the market share is taken by Curve and DODO.

[Forum post](https://gov.uniswap.org/t/consensus-check-add-1-basis-point-fee-tier/14612?u=getty)

(the post exceeds Snapshot's 4800 character limit)

====================================================================================================
[27] id=0x1994d4598b81dbb511bc7068f65a12fdf0ddbf2b26f5b7313e087750c5f9c0b7  token=UNI  space=uniswapgovernance.eth  date=2021-12-15
TITLE: Temperature Check—Support izumi Finance as Uniswap V3 official partner of Liquidity Mining Platform
CHOICES: YES | NO
TEXT (first 1500 characters):
1. izumi Finance offered "Programmable Liquidity as a Service" on Uniswap V3, which has much higher capital efficiency than the traditional Liquidity Mining program. 
2. Uniswap Labs could partner with izumi Finance to cost-free provide Liquidity Mining program supports for any trading pair on Uniswap V3.

For More info, you could check Uniswap Governance Forum.

====================================================================================================
[28] id=0x4f42b3215c4028edd947dc69980a9b8ba837ffbe3d0caa60d999406d634c8e79  token=UNI  space=uniswapgovernance.eth  date=2022-01-18
TITLE: Temperature Check - Should Uniswap Provide Voltz with v3 Additional Use Grant?
CHOICES: Yes | No
TEXT (first 1500 characters):
Dear Uniswap Community,

The Voltz Labs team recently submitted a proposal to request for an “Additional Use Grant” from Uniswap governance. This would allow Voltz to use aspects of the Uniswap v3 code that is subject to the “Business Source License”.

Voltz is a new DeFi primitive, bringing interest rate swaps to DeFi in a manner that is up to 3000x more capital efficient than alternative models. Voltz, therefore, is not a competitor to Uniswap but instead is complementary; interest rate swaps are a core pillar of well-functioning financial systems - so as Voltz grows it should help DeFi grow, which in turn should have second order benefits to Uniswap.

That said, the Voltz Labs team recognise the significant R&D that went into v3 and as a result are offering Uniswap governance 1% of Voltz future tokens alongside a number of additional non-financial benefits. The full proposal, and discussion, can be found here: https://gov.uniswap.org/t/should-uniswap-provide-voltz-with-v3-additional-use-grant/15669?u=simonj

Following positive feedback, including the discussion with the Voltz Labs founders on the Uniswap discord community call last week, we are now initiating the Temperate Check with the Uniswap community.

We’re excited to see how the community votes. And excited about the opportunity to make this happen and set a precedent for DeFi!

====================================================================================================
[29] id=0xbfeb7f3c4a3f1d4979b59129f9a78ee217183b0656a480612d261233fb3f8c62  token=UNI  space=uniswapgovernance.eth  date=2022-02-06
TITLE: Consensus Check -  Should Uniswap Provide Voltz with v3 Additional Use Grant
CHOICES: Yes | No
TEXT (first 1500 characters):
Dear Uniswap Community,

A few weeks ago, Voltz submitted a proposal to request for an “Additional Use Grant” from the Uniswap Community. This would allow Voltz to use aspects of the v3 code that is subject to a “Business Source License”. Voltz recognises the significant R&D that went into v3 and as a result is offering Uniswap Governance 1% of Voltz future tokens, alongside a number of non-financial benefits. The full proposal is available here https://gov.uniswap.org/t/should-uniswap-provide-voltz-with-v3-additional-use-grant/15669?u=simonj

We were delighted and humbled by the response from the Uniswap Community to our Temperature Check vote, with >99% voting in favour of our proposal! The Temperature Check also met the 25k UNI Yes threshold required to pass.  https://snapshot.org/#/uniswap/proposal/0x4f42b3215c4028edd947dc69980a9b8ba837ffbe3d0caa60d999406d634c8e79 

We are now kicking off the Consensus Check - the 2nd of 3 votes, which requires 50k UNI Yes votes to pass - with the community. https://gov.uniswap.org/t/consensus-check-should-uniswap-provide-voltz-with-v3-additional-use-grant/16012?u=simonj

We’re excited to see how the community votes! And we’re excited to make this happen and set a precedent for DeFi! 


**Voltz TL;DR**

Voltz is a new DeFi primitive, bringing interest rate swaps to DeFi in a manner that is up to 3000x more capital efficient than alternative models. Voltz, therefore, is not a competitor to Uniswap but instead is complementary; interest rat

====================================================================================================
[30] id=0xe3d59b3439ac0519b02ff39606e0ad571cc9fa7a05b334b6f87df09b2c883879  token=UNI  space=uniswapgovernance.eth  date=2022-02-09
TITLE: Temperature Check - Deploy Uniswap V3 on Harmony through an Additional Use Grant to Hermes DeFi
CHOICES: Yes, grant the license. | No, do not grant the license.
TEXT (first 1500 characters):
Dear Uniswap community,

Since our initial proposal submission 9 days ago to bring Uniswap V3 technology to Harmony, we have seen an extremely positive response from both the Harmony and Uniswap communities. We have integrated community feedback and compiled a revised proposal and have posted it on the Uniswap governance forum: https://gov.uniswap.org/t/temperature-check-deploy-uniswap-v3-on-harmony-through-an-additional-use-grant-to-hermes-defi/16128

In summary, Hermes DeFi is requesting an Additional Use grant from Uniswap to deploy Uniswap V3 based smart contracts to power a new AMM/DEX on the Harmony blockchain.

In exchange for this permission, the Uniswap DAO will receive:
1. A 10% allocation of HERMES tokens
2. 25% of platform trading fees, returned as IRIS (decreasing 5% each year for the next 5 years)
3. 50% of platform trading fees for the IRIS/1UNI pair, which will have a dedicated farm for the foreseeable future.
4. 2% of IRIS supply (governance token of Hermes).
5. Lending and borrowing support for 1UNI upon the launch of our lending market.
6. The ability to bond 1UNI to earn HERMES as a mechanism of protocol-owned liquidity.

====================================================================================================
[31] id=Qmcs5pAv7eGBzqGn1G8LJGusME3t7bTCSfZjdyWmw88LaM  token=UNI  space=uniswapgovernance.eth  date=2022-02-13
TITLE: Funding the Fee Switch Activation
CHOICES: Yes | No
TEXT (first 1500 characters):
Should the UNI governance allocate 0.3 – 1 M UNI to fund an organization to oversee and manage the application of the fee switch mechanism on Uniswap V3 and V2 protocols?

====================================================================================================
[32] id=0x4fdc5d5c87669d3c99072541e1c775f8dee9b906241b2ce22203737b608c8e55  token=UNI  space=uniswapgovernance.eth  date=2022-03-10
TITLE: Should we deploy Uniswap V3 on Celo?
CHOICES: Yes | No
TEXT (first 1500 characters):
### Proposal Discussion Topic

This proposal is created on behalf of Blockchain at Michigan, and in partnership with the [Celo Foundation](https://celo.org/) and the [Celo Climate Collective](https://climatecollective.org/).
Deploy Uniswap V3 on Celo to Launch “Green Asset” Liquidity Pools and expand access to Uniswap to the 6B smartphone users around the world

### Description
We propose to authorize the deployment of the Uniswap protocol to Celo on behalf of the community.

Celo is a mobile-first, carbon-negative, EVM-compatible blockchain. Specifically, we propose launching Uniswap on the Celo platform to:

* Increase Uniswap’s influence through $10M in financial incentives to Uniswap users, as well as additional grant funding provided by the Celo Foundation to utilize Uniswap as a financial building block
* Bring Uniswap V3’s increased capital efficiency to the 6B smartphone users around the world
* Create green asset liquidity pools with natural capital backed assets such as tokenized carbon credits (e.g. MCO2 and TCO2) and future nature backed assets issued on Celo like land and forests
* Use Uniswap as a decentralized mechanism to rebalance the Celo Reserve with nature backed assets rather than relying on centralized exchanges
* Foster pathways for future green use cases on Uniswap

Overall, we believe the Uniswap community’s mission of creating a trustless and decentralized financial infrastructure accessible to anyone aligns with Celo’s vision of tackling climate cha

====================================================================================================
[33] id=QmWhemJom3RZdH91rBPmjvAFZEr9HdFRSFVNtAae6kgbyE  token=UNI  space=uniswapgovernance.eth  date=2022-03-18
TITLE: Temp Check - Should Uniswap add the 1bp fee tier to Polygon?
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary

To date, Uniswap has four deployments: Ethereum, Abritrum, Optimism, and Polygon. In addition to these deployments, there are proposals to deploy Uniswap on Harmony, Celo, and more chains expected soon. The protocol should continue to deploy to new markets, but as the protocol continues to grow, it is vital the protocol learns to manage each of the deployments. With each new chain, there is new infrastructure that needs to be adapted to so that UNI on Ethereum can govern all of these deployments.

GFX Labs has been researching the various deployments and has prepared the first Uniswap cross-chain proposal to demonstrate how mainnet UNI can manage deployments on other chains.

Polygon has a messaging mechanism between Ethereum and Polygon called the [Fx-Portal](https://docs.polygon.technology/docs/develop/l1-l2-communication/fx-portal/). The portal functions via three contracts: FxRoot, State Sender, & FxChild. Messages can be sent from Ethereum to Polygon by calling the sendMessageToChild(address, bytes) at the FxRoot contract on Ethereum, which calls the State Sender contract. The [validators](https://docs.polygon.technology/docs/validate/polygon-basics/who-is-validator/) monitor the State Sender contract and relay messages to the FxChild on Polygon. Upon successful relay to the FxChild, the message is executed on Polygon by the validators.

The owner of the Uniswap v3 contracts on Polygon is the [Ethereum Proxy contract](https://polygonscan.com/address/0x8a1b966

====================================================================================================
[34] id=QmZ2D27uouvVEHGuRvydwmwepgL2PEXbGzYAXqYr9bMwLo  token=UNI  space=uniswapgovernance.eth  date=2022-03-21
TITLE: Consensus Check - Should Uniswap add the 1bp fee tier to Polygon?
CHOICES: Yes | No
TEXT (first 1500 characters):
# Summary

To date, Uniswap has four deployments: Ethereum, Abritrum, Optimism, and Polygon. In addition to these deployments, there are proposals to deploy Uniswap on Harmony, Celo, and more chains expected soon. The protocol should continue to deploy to new markets, but as the protocol continues to grow, it is vital the protocol learns to manage each of the deployments. With each new chain, there is new infrastructure that needs to be adapted to so that UNI on Ethereum can govern all of these deployments.

GFX Labs has been researching the various deployments and has prepared the first Uniswap cross-chain proposal to demonstrate how mainnet UNI can manage deployments on other chains.

Polygon has a messaging mechanism between Ethereum and Polygon called the [Fx-Portal](https://docs.polygon.technology/docs/develop/l1-l2-communication/fx-portal/). The portal functions via three contracts: FxRoot, State Sender, & FxChild. Messages can be sent from Ethereum to Polygon by calling the sendMessageToChild(address, bytes) at the FxRoot contract on Ethereum, which calls the State Sender contract. The [validators](https://docs.polygon.technology/docs/validate/polygon-basics/who-is-validator/) monitor the State Sender contract and relay messages to the FxChild on Polygon. Upon successful relay to the FxChild, the message is executed on Polygon by the validators.

The owner of the Uniswap v3 contracts on Polygon is the [Ethereum Proxy contract](https://polygonscan.com/address/0x8a1b966a

====================================================================================================
[35] id=QmV8ZeseHEoAcGj51kGaC6gVF2BkL9BHACJDAaQ74uiaJi  token=UNI  space=uniswapgovernance.eth  date=2022-06-26
TITLE: [Consensus Check] - Enable 1bp Fee Tier on UniswapV3 Optimism(L2)
CHOICES: YES | NO
TEXT (first 1500 characters):
**Summary**:

Enable a 1bp, 1tick fee tier on optimism (L2).

The rationale and initial temperature check for this proposal can be found here: https://gov.uniswap.org/t/deploy-a-1bp-fee-tier-to-uniswapv3-on-optimism/16930

**Process**:

The complete process is described in Uniswap’s Governance Reference here 4 and can be summarized as:

• A proposal is posted in GovernorBravo on Mainnet (GovernorAlpha for Kovan)

• The proposal is voted, queued and executed via Timelock.

• When all the conditions are meet and is executed, Timelock contract, which is authorized to execute administrative actions on the protected contracts, will execute 
the requested actions in the proposal.

Since this proposal needs to be executed on a different network, in this case L2 Optimism, the executing action needs to be forwarded to the proper target. In order to do that, Timelock will send the transaction to OVM_L1CrossDomainMessenger (Optimism mechanism to forward transactions from L1 to L2).

The transaction will then be sent via Optimism contracts to Uniswap’s CrossChainAccount, that is the privileged contract that can execute administrative tasks on protected contracts on L2 Optimism, and CrossChainAccount will forward the transaction, if it has the right origin, to the target Contract, in this case to UniswapV3Factory.
The sequence of contract interactions is the following:

• GovernorBravo.propose(targets, values, signatures, calldatas, description)
    ◦ where targets are the address of the

====================================================================================================
[36] id=0x1bf2c3fb48e31f4e006ce6349967088fc726cbf1d1518eca60babfe44e9e2895  token=UNI  space=uniswapgovernance.eth  date=2022-07-12
TITLE: Should Uniswap provide Rage Trade with an additional use grant?
CHOICES: Yes | No
TEXT (first 1500 characters):
Authors: [Noodles](https://twitter.com/crypto_noodles) + [Crema](https://twitter.com/0xCrema) + [Vertex](https://twitter.com/0xVertex) 

Related Discussion: Our proposal is similar to [Voltz Additional Use Grant](https://gov.uniswap.org/t/should-uniswap-provide-voltz-with-v3-additional-use-grant/15669)

### What is Rage Trade?

[Rage Trade](https://rage.trade) is a new perpetual swap  protocol built using Uniswap v3. Many on-chain perpetuals currently use Uniswap v2 style vAMMs. However, traders and LPs benefit from v3’s concentrated liquidity so we opted to build on v3 to design the most capital efficient perp.

### Why do we need an additional use grant?

Our proposal is most similar to the proposal by Voltz Protocol. Unlike Voltz we have not forked UNI v3’s code but instead we have built on top of it. Think of Uniswap as our matching engine, and on top we have built a risk engine to enable leverage trading. We have wrapped the following on top of Uniswap’s core: leverage trading, leverage LPing, cross-margin, liquidations, and real time funding rates. 

### What changes have we made that require additional use?

We have built libraries to enable leverage trading, leverage LPing, and real-time funding rates. Each of the libraries below makes use of Uniswap’s BUSL protect code (that we require an additional grants use for):

- [SimulateSwap](https://github.com/RageTrade/core/blob/ea881f6204f1bf7f065bd9a4b11ee792592c7230/contracts/libraries/SimulateSwap.sol): This library is

====================================================================================================
[37] id=0x4dd49ee723a7e506c6c6c15c8eabc8a7057f3f0760e44ed2f475d42203c4e3e8  token=UNI  space=uniswapgovernance.eth  date=2022-07-19
TITLE: Temp Check: "Fee switch" activation for ETH/USDC & USDC/USDT
CHOICES: Yes | No
TEXT (first 1500 characters):
See governance forum for details: https://gov.uniswap.org/t/fee-switch-design-space-next-steps/17132

====================================================================================================
[38] id=0xe9f8e5dd7ec26f7c0e7dd9e19bb8d57497d27d4a74be01cd3cad159cf3901b7f  token=UNI  space=uniswapgovernance.eth  date=2022-08-04
TITLE: [Consensus Check] "Fee switch" Pilot for Three Pairs
CHOICES: Yes, implement pilot as outlined | No, make no changes
TEXT (first 1500 characters):
See governance forum for details: https://gov.uniswap.org/t/consensus-check-fee-switch-pilot/17384

====================================================================================================
[39] id=0x2f72d9f247d9ce143809bbb4af7f5b36aa50895e517cc32096b15b18b40e3191  token=UNI  space=uniswapgovernance.eth  date=2022-09-12
TITLE: Should we deploy Uniswap v3 on Aurora?
CHOICES: Yes | No
TEXT (first 1500 characters):
## Summary

This proposal is created on behalf of Blockchain at Michigan, and in partnership with [Proximity Labs](https://www.proximity.dev/). We propose to deploy Uniswap v3 on Aurora through an additional grant license and ask the Uniswap community to consider and discuss this proposal.

Uniswap will expand access to decentralized and permissionless trading of tokens on Aurora, and aligns with the community’s multichain vision to bring trustless liquidity to all chains and position itself as a de facto DeFi hub in the space.

Our proposal will include a $5m amount allocated for financial incentives to Uniswap users on Aurora and a commitment to actively engage with the Uniswap community to further support its growth through grant programs and funding for protocol-related development.

Proximity Labs will coordinate with the community and governance participants to distribute these funds and will support future developments and allocations to projects leveraging Uniswap and DeFi’s ecosystem participants on Aurora.

## About Aurora

[Aurora ](http://aurora.dev)is an EVM-compatible execution environment running on top of [NEAR](http://near.org), a proof-of-stake layer 1 chain, and takes advantage of its unique features, including sharding and developer gas fee remuneration. Our long-term vision is to provide a user-friendly platform for developers and users to build fast and highly-scalable decentralized applications offering seamless integrations with NEAR’s native chain as

====================================================================================================
[40] id=0xa4a21c808b28a61562c6b4ebf5b71c0cd37ee2d630bcbdf91ffaf5f683cc650f  token=UNI  space=uniswapgovernance.eth  date=2022-11-22
TITLE: [Temperature Check] Fix the Cross Chain Messaging Bridge on Arbitrum
CHOICES: Yes | No
TEXT (first 1500 characters):
## Background: 

On Ethereum, Uniswap Labs governance consists of a suite of smart contracts. However, in addition to its original deployment on Ethereum L1 mainnet, Uniswap contracts are also deployed on four additional domains - Polygon, Optimism, Celo, and Arbitrum. 

Uniswap deployments on these domains do not have native access to the on-chain governance system, nor the UNI tokens which grant voting power in this system on Ethereum mainnet; in order for the existing Uniswap governance system to execute proposals governing these deployments, there must be some method of passing governance decisions from Ethereum mainnet to other domains. 

Presently, this method has been implemented differently for each of the four chains. The system governing Optimism and Polygon follow similar design principles, and should be functional for passing proposals. 

***The system governing the Arbitrum deployment was mis-configured due to a mis-communication between developers, and will require more involved intervention to repair.***


## Problem:

Arbitrum was initially going to allow L1 addresses to pass calls directly to L2 with msg.sender preserved. After realizing security issues with this approach, Arbitrum team instead shifted their approach to use aliasing (this method transforms L1 addresses to be a different address when represented on an L2):

Uniswap Labs was not made aware of this change in approach before deploying on Arbitrum. The Uniswap Factory was deployed with the owner s

====================================================================================================
[41] id=0x31c3409c09f5561d6aff1e0adeee6c83a5e73768a5d5c3e01b2a48a3894eda54  token=UNI  space=uniswapgovernance.eth  date=2022-11-29
TITLE: [Consensus Check] Fix the Cross Chain Messaging Bridge on Arbitrum
CHOICES: Yes - Fix the bridge | No - Make no change
TEXT (first 1500 characters):
## Background:

On Ethereum, Uniswap Labs governance consists of a suite of smart contracts. However, in addition to its original deployment on Ethereum L1 mainnet, Uniswap contracts are also deployed on four additional domains - Polygon, Optimism, Celo, and Arbitrum.

Uniswap deployments on these domains do not have native access to the on-chain governance system, nor the UNI tokens which grant voting power in this system on Ethereum mainnet; in order for the existing Uniswap governance system to execute proposals governing these deployments, there must be some method of passing governance decisions from Ethereum mainnet to other domains.

Presently, this method has been implemented differently for each of the four chains. The system governing Optimism and Polygon follow similar design principles, and should be functional for passing proposals.

***The system governing the Arbitrum deployment was mis-configured due to a mis-communication between developers, and will require more involved intervention to repair.***

## Problem:

Arbitrum was initially going to allow L1 addresses to pass calls directly to L2 with msg.sender preserved. After realizing security issues with this approach, Arbitrum team instead shifted their approach to use aliasing (this method transforms L1 addresses to be a different address when represented on an L2):

Uniswap Labs was not made aware of this change in approach before deploying on Arbitrum. The Uniswap Factory was deployed with the owner set to

====================================================================================================
[42] id=0xa3c7247632d3a08e4e73a63867908d0cd4402f48fa673945f93e3197dee5450a  token=UNI  space=uniswapgovernance.eth  date=2023-01-17
TITLE: [Temperature Check] Should Uniswap v3 be deployed to BNB Chain? 🦄
CHOICES: Yes | No
TEXT (first 1500 characters):
This proposal will authorize [0xPlasma Labs](https://plasma.finance/) to deploy the Uniswap v3 protocol (Fee Tier: 1, 0.3, 0.05, 0.01) to the BNB PoS Chain on behalf of the community.

We believe this is the right moment for Uniswap to deploy on BNB PoS Chain, for many reasons (one of them is License expiration).

## Uniswap v3 current stats

Total Value Locked - **$3.65B**

Chain Breakdown
Ethereum - **$3.41B**
Polygon - **$101.93M**
Arbitrum - **$85.08M**
Optimism - **$47.04M**
Celo - **$1.26M**

> Potential TVL from BNB Chain: **1/2 * $2.36B (PancakeSwap) ~ $1.18B** 

## The Important reasons why Uniswap v3 should be deployed to BNB Chain as soon as possible

1. BNB Chain has a large and growing user base, providing a potential new market for Uniswap v3.
2. BNB Chain offers high transaction speeds and low fees, making it a suitable platform for Uniswap’s decentralized exchange services.
3. Deploying to BNB Chain could help Uniswap to tap into the growing popularity of DeFi in the Binance ecosystem.
4. BNB Chain offers unique features such as staking and cross-chain support that could enhance Uniswap v3’s functionality.
5. BNB Chain’s strong governance model and active community could provide valuable support and feedback for the development of Uniswap v3.
6. Binance, the company behind BNB Chain, has a strong track record of supporting and promoting high-quality projects, potentially providing valuable exposure for Uniswap v3.
7. Binance has a global presence and a strong

====================================================================================================
[43] id=0x15031b68121659b87a3f5e33c303cd517bcbc003d3f60fc82f1299620475bcab  token=UNI  space=uniswapgovernance.eth  date=2023-02-02
TITLE: [Temperature Check] Enable 1bp Fee Tier for UniswapV3 on Arbitrum
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**By GFX Labs & ConsenSys**
## Rationale:

This proposal seeks to deploy a 1bp fee tier for UniswapV3 on Arbitrum. This will allow users to trade with lower fees, making it more accessible and competitive with other decentralized exchanges. The optionality of a 1bp fee tier is useful for stable-to-stable swapping and can often be found among the top ten liquidity pools on each of Uniswap’s respective deployments. 

Since the launch of the 1bp fee tier on mainnet, [Polygon](https://gov.uniswap.org/t/polygon-1bp-fee-tier/16488), and [Optimism](https://gov.uniswap.org/t/deploy-a-1bp-fee-tier-to-uniswapv3-on-optimism/16930), the 1bp fee tier has directly led to growth in Uniswap’s DEX market share and directly competes with stablecoin DEX protocols. 

![](https://hackmd.io/_uploads/B1EjR5t3j.png)
[Source](https://dune.com/1a1/DEX-Market-Share-for-Stablecoins)
![](https://hackmd.io/_uploads/SJYsRqF2o.png)
[Source](https://dune.com/1a1/DEX-Market-Share-for-Stablecoins)
![](https://hackmd.io/_uploads/ByTsRqY3s.png)
[Source](https://dune.com/1a1/DEX-Market-Share-for-Stablecoins)

Benefits:
* Lower fee tiers increase competitiveness and incentivize more user activity.
* As liquidity is more concentrated, 1bp pools are more capital efficient, especially for stable-to-stable swaps.
* Lower fee tiers can also lead to increased volume and earnings for liquidity providers.
## Why Arbitrum:
Favorable outcomes from deploying the 1bp fee tier on all other existing Uniswap v3 deployments make

====================================================================================================
[44] id=0xbadf3b39b681c98ba8fb988d5b6c9454ebeb5aae88545a6a852d0734e9f7c957  token=UNI  space=uniswapgovernance.eth  date=2023-02-24
TITLE: Temperature Check: Create Accoutability Committee
CHOICES: Doo Wan Nam (StableLab) | Cam O'Donnell (Consensys) | Jun Sun (Penn Blockchain) | Kendra Leong (She256) | Rafael Solari (Tally) | Kydo (Stanford Blockchain)
TEXT (first 1500 characters):
By Other Internet & Accountability Working Group

## Overview
This is a vote to elect 5 Committee Members for the Partnerships & Accountability Committee, first term (March - August 2023). For background and rationale, please see the [temperature check](https://gov.uniswap.org/t/temperature-check-accountability-committee-proposal/20579).

Elections are conducted by approval voting. Approval voting allows you to select all the nominees you support for the role of Committee Member.

To vote, select each candidate you approve for the role of steward.

You can select as many or as few candidates to approve as you like.

At the conclusion of voting, the 5 candidates ranked highest will be the committee members confirmed for the final on-chain governance proposal.

- The vote will be considered valid if a minimum of 10m delegated UNI is reached, per the community governance process.
- The committee will not be approved if less than 10m in delegated UNI total votes in the proposal.

A list of nominees and qualifications is included below.

## Nominees
The following individuals were nominated by Other Internet and Uniswap Foundation, or nominated themselves during the RFC phase. Proposed committee members Kydo, Cam O’Donnell, and Doo Wan Nam were participants in the accountability working group that created this proposal.

-  **[Doo Wan Nam  / @Doo_Stablelab](https://gov.uniswap.org/u/doo_stablelab) (COO at StableLab)**
Experience: Professional delegate at StableLab across major DeFi

====================================================================================================
[45] id=0x0f8a85d90759acf3a6fdc018e20b991f3562847122a8142c4e166c71d0e755e3  token=UNI  space=uniswapgovernance.eth  date=2023-04-07
TITLE: [Temperature Check] Post-BSL cross-chain deployment process and creation of new uniswap.eth subdomain
CHOICES: Yes - create new subdomain | No - do not create new subdomain | Abstain
TEXT (first 1500 characters):
TL;DR
Uniswap v3’s BSL expired Saturday, April 1, 2023.
Post BSL-expiry, it will be beneficial to identify one official Uniswap v3 deployment per chain in order to provide safety & security for users, focused support to ecosystem participants, and clarity to Uniswap governance. This deployment would be recognized in future Uniswap governance actions, by the UF for hackathons, by the ecosystem for liquidity mining campaigns, etc. 
In the post below we recommend the following in order to determine and track official Uniswap v3 deployments: 

A governance process which mostly remains the same, with some updates to allow for the fact that deployments can now be recognized as official after they have been deployed. 
Creation of a new subdomain v3-deployments.uniswap.eth that will be used to track official deployments. 
The creation of the new v3-deployments.uniswap.eth subdomain requires a governance vote. We are kicking that off here with an RFC, and we will gather feedback on this proposal as a whole as we go through the governance process. 

As many of you know, the BSL is set to expire later this week on Saturday, April 1. Once it expires, it will be possible for any person or team to deploy the Uniswap v3 code for production or commercial use (more on the BSL here). We assume that there will be multiple deployments of Uniswap v3 across other chains. 

However, after the BSL expires, it will still be important for the Uniswap DAO to determine which deployment, of many potenti

====================================================================================================
[46] id=0xb471984c1daef6742be4d4983339af7ad140c3dfcfc883508fd975f5abe0e8c9  token=UNI  space=uniswapgovernance.eth  date=2023-05-25
TITLE: Making Protocol Fees Operational: Fee options for V3
CHOICES: 1/5 | 1/6 | 1/10 | No Fee
TEXT (first 1500 characters):
These three polls are related to GFX Labs' post, [Making Protocol Fees Operational](https://gov.uniswap.org/t/making-protocol-fees-operational/21198?u=gfxlabs).

Poll 1: Fee options for V3
Poll 2: Initial deployment chain
Poll 3: Asset to be held in the treasury

We invite all voters to express their opinions by voting on these three polls. Once the polls are closed, we'll use the polling data to propose a formal Temperate Check. 

## How do protocol fees work?
V3 sets fees on a pool-by-pool basis, with a fee of 0 as the default. The fee may be set to 0, 4, 5, 6, 7, 8, 9, or 10. This is interpreted as one over the specified number. For example, a 100bps fee tier pool with a parameter of 5 would be a 20% protocol share of the fee, and thus would be 20bps to the protocol and 80bps to LPs. Another example is a 30bps fee tier pool with a parameter of 10 would be a 10% protocol fee and thus would be 3bps to the protocol and 27bps to LPs.

Note that inserting a protocol fee does not increase the fees paid by users.

====================================================================================================
[47] id=0xa47a49305ab418cb2ceb9da1290cbe022671d5feeb5e2a344bfcd1edbe0720d6  token=UNI  space=uniswapgovernance.eth  date=2023-05-25
TITLE: Making Protocol Fees Operational: Initial deployment chain
CHOICES: Polygon | Optimism | Arbitrum
TEXT (first 1500 characters):
These three polls are related to GFX Labs' post, [Making Protocol Fees Operational](https://gov.uniswap.org/t/making-protocol-fees-operational/21198?u=gfxlabs).

Poll 1: Fee options for V3
Poll 2: Initial deployment chain
Poll 3: Asset to be held in the treasury

We invite all voters to express their opinions by voting on these three polls. Once the polls are closed, we'll use the polling data to propose a formal Temperature Check.

====================================================================================================
[48] id=0x4b362044000714197ab43d5f2155977976dcc7cf1cb28d945e1168ae7ac61f90  token=UNI  space=uniswapgovernance.eth  date=2023-05-25
TITLE: Making Protocol Fees Operational: Asset to be held in the treasury
CHOICES: DAI | USDC | ETH | UNI
TEXT (first 1500 characters):
These three polls are related to GFX Labs' post, [Making Protocol Fees Operational](https://gov.uniswap.org/t/making-protocol-fees-operational/21198?u=gfxlabs).

Poll 1: Fee options for V3
Poll 2: Initial deployment chain
Poll 3: Asset to be held in the treasury

We invite all voters to express their opinions by voting on these three polls. Once the polls are closed, we'll use the polling data to propose a formal Temperature Check. 

## Why do I need to pick an asset?
As fees accrue, the protocol should claim and sell the tokens to minimize the protocol’s long exposure to the assets it is earning. The community must pick an asset to purchase with the fees accrued.

====================================================================================================
[49] id=0x86ded24b11c4714e0f4f2b6e4ca489f60dc33e6f2f4ababa5575bf5ab973a005  token=UNI  space=uniswapgovernance.eth  date=2023-06-29
TITLE: ARB Distribution Proposal Poll
CHOICES: Create a UNI-ARB Working Group  | Enable upfront yield | MMA Infrastructure development | Combined Liquidity Incentives | None of the above
TEXT (first 1500 characters):
This poll serves as a Temperature Check for the four proposals listed below. They were produced as a result of an RFP published on 23 May 2023 which sought ideas from the Uniswap community for ways to allocate ARB granted to the DAO by the Arbitrum Foundation's airdrop.

You can vote for any, all, or none of these proposals. Your full voting power will be allocated to each proposal you select. As a concrete example, say you have 10 UNI delegated to you. If you vote for one proposal, that proposal will receive 10 UNI worth of votes. If you vote for all four proposals, they will all receive 10 UNI worth of votes. If you vote for no proposals, none of them will receive your 10 UNI worth of votes.

Each proposal that garners 10 million UNI worth of votes in this poll will proceed to an on-chain vote.

Proposals and links:

Create a UNI-ARB Working Group - 2,200,000 ARB requested
https://gov.uniswap.org/t/temp-check-create-a-uni-arb-working-group

Enabling upfront yield - 200,000 ARB requested
https://gov.uniswap.org/t/rfc-flashstake-enabling-upfront-yield-for-uniswap-liquidity-v2-v3

MMA Infrastructure Development - 250,000 ARB requested
https://gov.uniswap.org/t/rfc-li-fi-mma-infrastructure-development-for-uniswap

Combined Liquidity Incentives - Up to 2,000,000 ARB requested
https://gov.uniswap.org/t/temp-check-combined-liquidity-incentivization-proposal

One note - if it passes, the ARB requested by the liquidity incentives proposal will adjust to the lesser of 2,000,000 ARB a

====================================================================================================
[50] id=0x011e2297060cd82da866185392a54f506118cbece76c88c1e2a02fac4cd75893  token=UNI  space=uniswapgovernance.eth  date=2023-08-31
TITLE: [Temperature Check] Deploy Friendly Fork of Uniswap V3; ZERO Protocol on Polygon zkEVM
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
## Proposal summary
In light of the Uniswap DAO’s vote to deploy on the Polygon zkEVM (Tally | Uniswap Proposal 10), we propose a partnership between the Uniswap DAO and Zero Protocol. This collaboration centers on the concept of a “friendly fork.”

A friendly fork refers to the creation of a new version of an existing protocol that retains a cooperative and synergistic relationship with the original. Unlike contentious forks, which often lead to competitive divergence, a friendly fork seeks to align with the parent protocol.

In this context, the below proposal will outline how the partnership entails integrating Zero Protocol as a friendly fork of Uniswap on the Polygon zkEVM chain. Zero Protocol will utilize Uniswap’s established backend infrastructure as its foundational engine and be granted access to ecosystem funded tooling. To align interests, the DAO will benefit from the open R&D taking place and receive a 10% token allocation detailed below. This approach resonates with Uniswap V2’s historical challenges of dealing with competitive forks and this scenario into an opportunity.

# Overview of proposal
## Description:

We propose a visionary partnership between the Uniswap DAO and Zero Protocol, focusing on the integration of Zero Protocol as a friendly fork of Uniswap on the Polygon zkEVM chain. This collaboration draws inspiration from Uniswap V2’s history and aims to transform past challenges into future opportunities. By leveraging this partnership, Uniswap can ha

====================================================================================================
[51] id=0x4d8042e4e53715dc141be98b89aab659d5f7306c3d3ef789b0c807a029c23ca8  token=UNI  space=uniswapgovernance.eth  date=2023-10-09
TITLE: UADP Team Election
CHOICES: Abdullah Umar - @Michigan Blockc | jengajojo - @Jengajojo
TEXT (first 1500 characters):
## Overview
The UNI-ARB Working Group Zero (WG0) is launching the UNI-ARB Protocol Delegate Program (UADP) and is now initiating the election process for the available seat in the program.

Following the 2-week self-nomination period, we're excited to move forward to the election period where the Uniswap community can vote for their preferred nominees to fill the **1 available seat in the UADP**.

For background and rationale about UNI-ARB Delegate Program (UADP), please see the [on-chain proposal](https://vote.uniswapfoundation.org/proposals/47).

## Voting Details
* **Maximum Selection**: Voters can select 1 nominee.
* **Elections are conducted by approval voting**: Approval voting allows you to select all the nominees you support for the role of Committee Member.
* **Seat Allocation**: The nominee with the highest vote will qualify to join the UADP team.
* **Miminum threshold:** The vote will be considered valid if a minimum of 10m delegated UNI is reached, per the community governance process.

## Nominees
The following are all the nominees who have expressed interest in being part of the **UADP team**:

1) [Abdullah Umar - @Michigan Blockchain](https://gov.uniswap.org/t/nomination-and-election-process-for-the-uni-arb-grant-program-uagp-and-delegate-program-uadp/21950/2)
**Experience:** Lead governance at Michigan Blockchain, with experience as a delegate for various protocols, from DEXs and money markets, to L2s and stablecoins. Prior to governance, worked as a product a

====================================================================================================
[52] id=0xf551e90e767fccfac8593a3233b6e2f2e2a3a773e1e9f9abbb9a4d2678f101f8  token=UNI  space=uniswapgovernance.eth  date=2023-10-09
TITLE: UAGP Team Election
CHOICES: Marc - @Marc_Blockshard | Nneoma_StableLab - @Nneoma | King_Steve - @Steve | Zeb - @Zeb | JoJo - @_ JoJo (JonesDao) | Shreddy - @Shreddy | David - @Kouros | Arseny- @arseneeth (Daoism) | Ignacio Rodriguez - @ignacio-rsg | Sov - @Sov (Gitcoin) | azeem - @azeemk | ilia.eth - @ilia_0x (0xPlasma) | Honn - @honn24x | Lawrence - @omnianalytics | Srijith - @Srijith (Questbook)
TEXT (first 1500 characters):
## Overview
The UNI-ARB Working Group Zero (WG0) is launching the UNI-ARB Grant Program (UAGP) and is now initiating the election process for the available seats in the program.

Following the 2-week self-nomination period, we're excited to move forward to the election period where the Uniswap community can vote for their preferred nominees to fill the **3 available seats in the UAGP**.

For background and rationale about UNI-ARB Grant Program (UAGP), please see the [on-chain proposal](https://vote.uniswapfoundation.org/proposals/47).

## Voting Details
* **Elections are conducted by approval voting**: Approval voting allows you to select all the nominees you support for the role of Committee Member.
* **Seat Allocation**: The top 3 nominees with the highest votes will qualify to join the UAGP.
* **How to vote:** Select each candidate you approve for the role of committee member. You can select as many or as few candidates to approve as you like.
* **Miminum threshold:** The vote will be considered valid if a minimum of 10m delegated UNI is reached, per the community governance process.

## Nominees
The following are all the nominees who have expressed interest in being part of the **UAGP team**:

1) [Marc - @Marc_Blockshard](https://gov.uniswap.org/t/nomination-and-election-process-for-the-uni-arb-grant-program-uagp-and-delegate-program-uadp/21950/4) (Blockshard)
**Experience:** Currently member SSV DAO grants committee. Full-time dedication to the crypto industry since 2021

====================================================================================================
[53] id=0xcc41f669e5b4a92bc47b02d09847c1d4ba9ed4bd9c4dc0635190c974083482a6  token=UNI  space=uniswapgovernance.eth  date=2023-10-21
TITLE: Temperature Check - [Issue a Visa Card with Uniswap Logo ]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
![Screenshot 2023-10-21 at 09.43.32.png](ipfs://bafkreibwgf6qc2cse535mjngrqzpfd5gb524niaif7u7d5l2pjcfgfc4hy)
    

**Introduction**

Fiat24 is the first regulated and licensed Swiss bank that is exclusively built on a public blockchain (Arbitrum). Unlike any other traditional bank, we have completely abandoned servers, with all banking logics run by smart contracts, and our clients being identified via their Fiat24 NFT. You might imagine us as an additional fiat layer for DEXs, such as Uniswap. In fact, clients can not only top-up their Swiss bank accounts via international money transfer, but also by selling their crypto assets. All crypto tokens go through Uniswap and are converted to stabelcoins before arriving in our treasury, meaning that Uniswap is our liquidity provider.

We are directly connected with the Swiss National Bank, European Central Bank, and Visa Payment Network, and all real-world payment data, which is all booked on Arbitrum. Since we are a bank that is fully run by protocols, you can easily access your Swiss e-banking portal directly inside your non-custodial crypto wallet (such as MetaMask or Uniswap Wallet) by using this link http://www.fiat24.com

**Motivation & Benefits to Uniswap Community & Growth**

According to DeFi Llama the daily trading volume of Uniswap is more than 600M. That is a huge number, but compared to the daily trading volume of global Forex (7.5 trillion), it is still low. In fact, Uniswap will have much more potential if it could b

====================================================================================================
[54] id=0x73753f8ccab7747563b9c17a0bc746e6207991561278d7cadfaa1a7be12b081a  token=UNI  space=uniswapgovernance.eth  date=2023-11-17
TITLE: [Temperature Check]: Competition of Delegation of UNI to Active but Underrepresented Delegates
CHOICES: Wintermute Governance | Keyrock | StableLab | atiselsts.eth | PGov | 404 DAO | Karpatkey
TEXT (first 1500 characters):
*Summary*

The Temperature Check regarding “Delegation of UNI to Active but Underrepresented Delegates” has [passed](https://snapshot.org/#/uniswap/proposal/0x14aa7becb547ccb8fdcfc69054bda1557a90f1ebe3ac45569f049b5e29e98d76), and there was a 5-day period where delegates that met the application criteria posted their application to be considered for delegation.

There were 7 qualified delegates. This snapshot voting will be a voting weight poll where a delegate can distribute their voting power among qualified delegates.

Top 4 Delegates will get delegation till 2.5 M is achieved. The rest of UNI (out of 10 M) will be split among the rest proportional to their votes won.

Detailed example has been shared [here](https://gov.uniswap.org/t/temperature-check-delegation-of-uni-to-active-but-underrepresented-delegates/22238/21?u=doo_stablelab).

-----

*Qualified Delegates* (Order of when the application was posted)

***Wintermute Governance***

-Ever since launching our delegate profile in January, our mission has been to actively contribute to Uniswap’s governance efficiency and growth. We’ve maintained a 100% participation rate for on-chain votes (pass all participation requirements) since our delegate launch, deployed Uni V2 on Boba and Gnosis Chain, launched [WinterGov ](https://dune.com/wintermuteresearch/wintergov), and actively provided feedback to Uniswap proposals. We’d love to continue supporting the growth of Uniswap by contributing to governance efficiency, contributing

====================================================================================================
[55] id=0xad7e3612d11d56b21f0b2274e4ce825163bc1873d0e2ef809a3a98733df992a7  token=UNI  space=uniswapgovernance.eth  date=2024-03-01
TITLE: Activate Uniswap Protocol Governance
CHOICES: Yes, upgrade the factory owner | No, do not upgrade the owner | Abstain
TEXT (first 1500 characters):
This Snapshot poll is to gauge community sentiment to move forward with our proposal to Active Uniswap Protocol Governance. Specifically, we propose to upgrade the owner of the mainnet UniswapV3Factory contract from the Timelock to a deployment of V3FactoryOwner to enable the permissionless and programmatic collection of protocol fee revenue.

A full discussion of this proposal can be found at the link below; we recommend that delegates read that proposal and its accompanying materials before voting on this Snapshot.

====================================================================================================
[56] id=0x3d8d2f44677c19f49a5bbe4466e4b50068b1a704861801d95384c898b1cbde54  token=UNI  space=uniswapgovernance.eth  date=2024-03-03
TITLE: Uniswap V3 Fees: Factory Owner Amendment
CHOICES: Accept amendment | Reject amendment
TEXT (first 1500 characters):
**Authors**: MichiganBlockchain, @404DAO, @GFXlabs

**TL;DR**: Introduce an amendment to the Uniswap V3 Factory owner to allow the DAO to make future changes to the fee mechanism. This will prevent the DAO from being pigeonholed by a singular, immutable implementation, thereby enabling further experimentation and allowing the DAO to effectively respond to issues with the current setup.

[Full forum thread](https://gov.uniswap.org/t/uniswap-v3-fees-factory-owner-amendment/23187/1)

To not significantly slow down the current process proposed by the Foundation, this Snapshot poll will be used to collect opinions via a vote from the delegates. There will be two options, “Accept amendment” or “Reject amendment.” If the “Accept amendment” is able to demonstrate a significant majority, then we would expect the onchain proposal put forth by the Foundation to include the change. The poll will go up immediately and end on March 8th.

====================================================================================================
[57] id=0xd2d3a01ed6e4b0c080073d4510f545a51db224ff6e57babb9454640cc5e1ddfd  token=UNI  space=uniswapgovernance.eth  date=2024-03-26
TITLE: [Temp Check] Mobilizing the Uniswap Treasury
CHOICES:  Launch Working Group | Don't Launch Working Group | Abstain
TEXT (first 1500 characters):
Title: Mobilizing the Uniswap Treasury

Authors: @AbdullahUmar & @Doo
Summary:
The Uniswap DAO's treasury, containing assets worth nearly ~$6B, predominantly in $UNI tokens, faces challenges due to its single-asset composition and the lack of a plan for productive utilization. To address the treasury's volatility and underutilization, we propose forming the Uniswap Treasury Working Group (UTWG) to explore treasury management strategies aimed at achieving sustainability and growth for the DAO. This involves diversifying assets to stabilize the treasury and finding revenue-generating investments beyond the protocol's core operations. The UTWG will examine various treasury plans for Uniswap DAO based on 8 weeks of research and interviews with various entities and individuals familiar with treasury management and adjacent subject matters. A deliverable will correspondingly be released on the forum where we present at least two viable treasury management options for the DAO to begin pursuing. Both of these options will be presented as their individual RFC/RFP, ideally allowing various treasury managers to present their products and services to the DAO. The UTWG will help facilitate this process. 

The proposal's ultimate goal is to ensure the DAO's long-term financial health and support the sustenance of Uniswap. However, there is one caveat–before implementing any of the proposed strategies, in other words, before moving any $UNI to and from the treasury, we must have clarity aro

====================================================================================================
[58] id=0x7584aabd34944953f37008d4a6209e4efee8f1a066a5051fbba37910dae80b49  token=UNI  space=uniswapgovernance.eth  date=2024-04-15
TITLE: Uniswap Treasury Working Group (UTWG) Election
CHOICES: Franklin DAO | Solo Labs Corporation | Steakhouse Financial Limited | Nathan van der Heyden | GFX Labs | JoJo | 404 DAO | SpikeWatanabe.eth | karpatkey | Blockchain Education Network
TEXT (first 1500 characters):
Details regarding Uniswap Treasury Working Group (UTWG) Election and also its candidates can be found on the forum post: https://gov.uniswap.org/t/uniswap-treasury-working-group-utwg-application/23571

====================================================================================================
[59] id=0xfe8cb4e08138df2f0d136480e85edadf22679cca73b68f3f376d12f322dd2565  token=UNI  space=uniswapgovernance.eth  date=2024-05-08
TITLE: [Temp Check] Uniswap Delegate Reward -3 Months-Cycle 1
CHOICES: Yes, Proceed | Abstain | No, Do Not Proceed
TEXT (first 1500 characters):
Summary

This proposal outlines the Uniswap Delegate Reward Initiative, a compensation program designed to improve participation quality and dedication among Uniswap delegates. The initiative was developed by several members of the Uniswap Delegate Reward Working Group, which conducted extensive research and produced findings supporting the implementation of such a program.

Background

In late February 2024, StableLab proposed the Uniswap Delegate Reward Initiative 8. After the GovSwap event in Denver, further research to plan and implement the Delegate Reward Initiative was highlighted, leading to the formation of the Uniswap Delegate Reward Working Group, composed of 8 members from different organizations. After extensive research for more than a month, the Working Group produced several findings, which can be found here: https://gov.uniswap.org/t/findings-from-uniswap-delegate-reward-working-group/23702 7

The details of the findings were slightly different. However, this conclusion summarized the findings quite nicely:

“There was a general consensus across most categories that a compensation program for delegates could improve participation quality and dedication. However, the enthusiasm varied, with those deeply involved in governance showing the strongest support.”

The Uniswap Delegate Reward Working Group explored several frameworks for implementing rewards, including a Committee structure that allows several non-delegates to get rewarded for helping to contribute t

====================================================================================================
[60] id=0xcd74f6280e53cbdb3bda8349c3c6b833e613faf4677278e85a38cb06e5afb355  token=UNI  space=uniswapgovernance.eth  date=2024-08-14
TITLE: [Temp Check] Activate 2, 3, 4 bps fee tiers on Uniswap v3 on Base
CHOICES: Yes, activate additional tiers | No, do not activate the tiers
TEXT (first 1500 characters):
Just like the 1 bp fee tier originally proposed 3 years ago by Getty Hill, we propose to additionally add a 2, 3, 4 bps fee tier to Uniswap v3 on Base. 

You may question why we are proposing the creation of three new fee tiers when our analysis only focused on 4 bps. There are two reasons for this. For one, Aerodrome is able to adjust fees automatically on Base. We anticipate they may respond by lowering fees below 4 bps and want Uniswap Protocol to allow LPs to move without governance intervention if this happens. 

Second, we believe this analysis may be a single case study into a larger finding that the required fee for LPs on L2s may be lower than 5 bps. While Aerodrome highlights the success of a 4 bp fee tier, it’s unclear whether that’s the right market rate. It may be lower.

Lastly, we note that this change should not be blindly repeated on other chains. The community should do further research on the success or failures of this program before executing it on another chain.

====================================================================================================
[61] id=0x3c55a8685f64078d016a5a69cba3fccc3844692da97fdb3dbe6b31049b8f85ac  token=UNI  space=uniswapgovernance.eth  date=2024-08-19
TITLE: [REDO: Temp Check] Activate 2, 3, 4 bps fee tiers on Uniswap v3 on Base
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Note: While this snapshot originally passed, we misconfigured the time for 3 days instead of 5 days, which is the requirement according to https://gov.uniswap.org/t/community-governance-process-update-jan-2023/19976. We have fixed this mistake and are re-running the snapshot.

Original Text:
Just like the 1 bp fee tier originally proposed 3 years ago by Getty Hill, we propose to additionally add a 2, 3, 4 bps fee tier to Uniswap v3 on Base. 

You may question why we are proposing the creation of three new fee tiers when our analysis only focused on 4 bps. There are two reasons for this. For one, Aerodrome is able to adjust fees automatically on Base. We anticipate they may respond by lowering fees below 4 bps and want Uniswap Protocol to allow LPs to move without governance intervention if this happens. 

Second, we believe this analysis may be a single case study into a larger finding that the required fee for LPs on L2s may be lower than 5 bps. While Aerodrome highlights the success of a 4 bp fee tier, it’s unclear whether that’s the right market rate. It may be lower.

Lastly, we note that this change should not be blindly repeated on other chains. The community should do further research on the success or failures of this program before executing it on another chain.

====================================================================================================
[62] id=0xff05f8e61540a8ad3ca98b9a65a4b135d7834bdb0cf286a1346dcd6fcda85df0  token=UNI  space=uniswapgovernance.eth  date=2024-08-20
TITLE: [Temp Check] Uniswap Delegate Reward Initiative - Cycle 2
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Uniswap Delegate Reward Initiative - Cycle 2
Authors: @Doo_StableLab @PGov @AranaDigital

Summary
This proposal outlines the Uniswap Delegate Reward Initiative - Cycle 2, a compensation program designed to improve participation quality and dedication among Uniswap delegates following the conclusion of Cycle 1.

Background
In late February 2024, StableLab proposed the Uniswap Delegate Reward Initiative 9. After the GovSwap event in Denver, further research to plan and implement the Delegate Reward Initiative was highlighted, leading to the formation of the Uniswap Delegate Reward Working Group, composed of 8 members from different organizations. After extensive research for more than a month, the Working Group produced several findings, which can be found here: https://gov.uniswap.org/t/findings-from-uniswap-delegate-reward-working-group/23702 3

Incorporating these findings, the Uniswap Delegate Reward Initiative–Cycle 1 was proposed 2 and launched 1 in June 2024.

Success of Cycle 1
The 12 delegates that were selected under Cycle 1 maintained 100% voting participation rate for both offchain and onchain votes during this period. In addition, the Delegate Reward Initiative discussion attracted several new delegates.

New Delegate Name	Delegate Join Date
SEEDGov	May 2024
Curia	June 2024
Tané	June 2024
Bobbay	July 2024
Whetstone	July 2024

Learnings from Cycle 1
While Cycle 1 was simple and effective, there were several suggestions to have a tier system to incorporate different

====================================================================================================
[63] id=0xc95ebeb66aad587d768ed7ead88acacabbdd89bffb1bae8b15ce245a881ffab9  token=UNI  space=uniswapgovernance.eth  date=2024-10-16
TITLE: Uniswap Growth Program Trial
CHOICES: In Support | Not In Support | Abstain
TEXT (first 1500 characters):
### Full Forum Post: [Here](https://gov.uniswap.org/t/rfc-uniswap-growth-program-trial/24703/1)

#### Authors
AlphaGrowth and our sister company ReservoirDAO are DAO service providers primarily working in the realm of DeFi growth through grants, BD, growth-marketing, and DeFi Operations. Our marquee partner is Compound.Finance, where we run all things growth, business development and marketing for the DAO.

#### Co-authors for Uniswap Ecosystem Incentives Initiative section
Uniswap MetaGov Team: @PGov and @AranaDigital; The team first formed as the UADP to focus on Arbitrum’s governance and ecosystem. After applying and receiving 1M ARB in grants for the Uniswap DAO, it was deployed over 3 months and recently concluded. With this success, the UADP, now MetaGov team, is looking to deploy this framework across other chains. The team consists of long-time community members and delegates who have participated as contributors through multiple working groups and have worked across various committees and grant programs in Uniswap and across DeFi.

### How we got here
Over the last few market cycles, we cut our teeth in the world of grants, BD, go-to-market, tokenomics, and ecosystem growth. We’ve helped dozens of projects go multichain. Throughout this process, members of Compound DAO encouraged us to design and implement a comprehensive growth program to address stagnation in the protocol. As of today, we lead growth for Compound.Finance. 

[Here](https://www.comp.xyz/t/alphagrowth

====================================================================================================
[64] id=0x90fab9ab51bb8ca09bab7d76e7ccacaf7dad184e697c870c30957770211cc95d  token=UNI  space=uniswapgovernance.eth  date=2024-12-18
TITLE: Discretionary Budget from UAC for Co-Incentive Campaigns
CHOICES: Allow UAC Surplus Spending | Do Nothing | Abstain
TEXT (first 1500 characters):
#### Authors: @alphagrowth @PGov @AranaDigital

### Summary:
AlphaGrowth, stewards of the Uniswap Growth Program, proposes accelerating the execution of co-incentive campaigns. Leveraging some of the UAC’s surplus budget, we can capitalize on high-impact, time-sensitive opportunities without needing any additional funding from the DAO. While many of these opportunities are not yet able to be discussed publicly (pending negotiations), currently there is an opportunity with EtherFi to match $250k in incentives.

This EtherFi-sponsored campaign would deepen onchain liquidity of specific EtherFi assets (particularly weETH) on Uniswap. Our incentives would be matched 1-to-1 by EtherFi with ETHFI tokens, and additionally would be co-marketed by their protocol.

### Background:
Since the kickoff of the Uniswap Growth Program, we’ve activated numerous relationships with new chains and opportunities for the Uniswap protocol. Many of these opportunities are standard, and we will continue to help push these through governance, and co-incentivize deployments via the Onboarding Package. As we have quickly found, however, some of these opportunities require more of a tailor-made co-incentivization structure.

### Problem:
Uniswap’s governance process is designed to ensure transparency and thorough deliberation. However, with the current process, activating a co-incentive campaign requires an RFC, Snapshot, and on-chain proposal—a process that can take a minimum of 4 weeks. While this proce

====================================================================================================
[65] id=0x5527b3846cd05a64346a00461d2c763531f43e2b2f4f1c7d55e1ba7de60c4d4e  token=UNI  space=uniswapgovernance.eth  date=2024-12-20
TITLE: Incentive Package for Sonic (Formerly Fantom)
CHOICES: $250k Incentive Match | Do Not Match | Abstain
TEXT (first 1500 characters):
### Overview:

The deployment of Uniswap on Sonic has sucessfully be completed. This is a vote to gauge whether we should match $250k of incentives for Sonic's $500k committment. 

### [About](https://docs.soniclabs.com/):

Sonic is an EVM layer-1 blockchain platform focused on delivering exceptional performance, enabling developers to scale their applications without limits while ensuring smooth user experiences with benefits such as:

- Native Bridge from Ethereum - [Sonic Gateway](https://docs.soniclabs.com/sonic/sonic-gateway)
- 10,000 Transactions per Second
- Sub-Second Finality
- Fee Monetisation
- 100% EVM Compatible
- Solidity/Vyper Support

### Key Benefits of Sonic and synergy with Uniswap:

1. **Scalability and Speed**: Sonic boasts the ability to process 10,000 transactions per second (TPS) with sub-second transaction finality, ensuring fast and irreversible transactions. This makes it highly efficient for applications requiring high throughput and low latency.

2. **Availability of Key Infrastructure**: Sonic Labs has confirmed integration of key infrastructure partners such as Alchemy, Safe, Etherscan, Chainlink, Gelato, Biconomy, Dune, etc., making it extremely easy to onboard new builders.

3. **Cost Efficiency**: Operating on Sonic is cost-effective, with a 66% reduction in validator node costs and up to a 96% reduction in large-scale RPC node costs compared to previous solutions. This is coupled with advanced live-pruning capabilities that streamline node m

====================================================================================================
[66] id=0x0c7b3acc56ad1d276cd4c9338e2ef8ca9e15e8ab3e3a22d395fd34398bda40af  token=UNI  space=uniswapgovernance.eth  date=2025-02-19
TITLE: [Temp Check] Uniswap Delegate Reward Initiative - Cycle 3
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
#### Uniswap Delegate Reward Initiative - Cycle 3
Authors: @Doo_StableLab @PGov @AranaDigital @seedgov

## Summary

This proposal outlines the Uniswap Delegate Reward Initiative—Cycle 3, a compensation program designed to improve and sustain the participation quality and dedication among Uniswap delegates following the conclusion of Cycle 1 and 2.

## Background

In late February 2024, StableLab proposed the [Uniswap Delegate Reward Initiative](https://gov.uniswap.org/t/rfc-uniswap-delegate-reward/22909). After the GovSwap event in Denver, further research to plan and implement the Delegate Reward Initiative was highlighted, leading to the formation of the Uniswap Delegate Reward Working Group, composed of 8 members from different organizations. After extensive research for more than a month, the Working Group produced several findings, which can be found here: https://gov.uniswap.org/t/findings-from-uniswap-delegate-reward-working-group/23702

Incorporating these findings, the Uniswap Delegate Reward Initiative Cycle 1 was [proposed](https://gov.uniswap.org/t/temp-check-uniswap-delegate-reward-3-months-cycle-1/23837) and [launched](https://www.tally.xyz/gov/uniswap/proposal/64) in June 2024. Cycle 1 was successful in that the 12 delegates selected maintained 100% voting participation rate for votes during this period. In addition, several new delegates joined the protocol due to the presence of incentives.

With learnings from Cycle 1, including how to make a points system t

====================================================================================================
[67] id=0xe7fb39bd6f16b65d0847cdd6ab6ecef3a6c1e89bd523cf895f3d806c4bb4b1cf  token=UNI  space=uniswapgovernance.eth  date=2025-02-26
TITLE: [Temp Check] Unichain and Uniswap v4 Liquidity Incentives
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Proposal to Fund Unichain and v4 Liquidity Incentive Programs
Proposed by the Uniswap Foundation, with contributions from Gauntlet
[Feb 19 note: this proposal is being made alongside another to fund UF Grants + Operations, here, and outlines a strategy addressing questions in the comments below about builder support, demand creation to sustain liquidity, etc.]

TL;DR
The Uniswap community is entering 2025 with the momentum of three positive catalysts: a more collaborative regulatory environment, the launch of Uniswap v4, and the debut of Unichain. As we look to the months and years ahead, we see the potential for Uniswap Protocol and Unichain to cement themselves as foundational infrastructure for digital value transfer.

Achieving this vision will require more than just technological innovation; for the Protocol to become the world’s infrastructure for digital value transfer, we must take action. To that end, we propose funding liquidity campaigns, managed by our long-standing collaborators at Gauntlet, to kickstart sustainable growth for both Unichain and Uniswap v4.

Proposal: Fund two separate liquidity incentive programs to attract initial LPs, swappers, and developers to Uniswap v4 and Unichain. Through the use of Aera, Uniswap Governance would retain control of funds at all times, and be able to recall unused funds, if delegates made the call to do that. If the initial campaigns are successful, we would return to request subsequent funds, though we do not foresee campa

====================================================================================================
[68] id=0x6175261050aeccdd3d541cb4eb2b58c9fde747bfda509896586df5a62e1295d4  token=UNI  space=uniswapgovernance.eth  date=2025-03-12
TITLE: [Temp Check] Saga Uniswap v3 Liquidity Incentives
CHOICES: For $250k | Against | Abstain
TEXT (first 1500 characters):
## TLDR:
This proposal requests $250k in UNI from the DAO for six months to support five pools on Saga. 

Saga is: 
* Funding the Oku integration ($45k) and maintenance ($5k monthly) directly. 
* Allocating 2m $SAGA tokens monthly ($700k/month at current prices, $4.2m $SAGA over 6 months at current prices) from the Saga Foundation

### Saga:
Saga is launching its Liquidity Integration Layer (LIL), an innovative solution for liquidity fragmentation in horizontally scalable infrastructures. Uniswap V3 will serve as our canonical DEX. A meaningful, long-term partnership with Uniswap DAO will help cement Uniswap as a key player in the greenfield DeFi ecosystem in Saga.

Uniswap on Saga has already been optimistically canonicalized by the DAO in December 2024. The initial proposal and its associated contracts can be viewed [here](https://gov.uniswap.org/t/rfc-saga-l1-application-for-canonical-uniswap-v3-deployment/25008). Oku is presently serving as the only front-end for this deployment and will go live soon. The Saga team paid for the front-end integration and maintenance costs. 

Independently from the Uniswap proposal, working with the Uniswap Growth Program, Saga Foundation will contribute 2mm SAGA tokens per month (~$1.0mm USD per month as of Feb 27, 2024) to the Uniswap V3 pools to bootstrap Uniswap liquidity on Saga. This proposal of additional UNI incentives will deepen liquidity and attract diverse LPs to expand Uniswap’s reach into the Saga ecosystem.

This proposal is

====================================================================================================
[69] id=0x04af1fcb7538cf5458c5c17baa50fe410952d48e98d451a6ca5f7b94fea87ee8  token=UNI  space=uniswapgovernance.eth  date=2025-03-27
TITLE: [Temp Check] Treasury Delegation Round 2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Background

The DAO started the first treasury delegations as a program called [Delegation of UNI to Active but Underrepresented Delegates](https://gov.uniswap.org/t/governance-proposal-delegation-of-uni-to-active-but-underrepresented-delegates/22397) in December, 2023. According to [our analytics](https://gov.uniswap.org/t/treasury-delegation-round-2-ideas-thread/24667/13?u=tane) we shared in the original round 2 ideas thread, this program has been essential to keep the governance healthy and retain the active and capable delegates. At the same time, the originally promised time period has already passed, but the delegation has been kept as they didn't have their expirations. In addition, there have been discussions to consider how we proceed with the treasury delegation going forward. Through the process, we have decided to implement an important feature, expirations of the delegations to the Franchiser contract and create a robust system to keep the delegations enabled for the appropriate delegates.

# Proposal Summary

We propose allocating **up to 18 million UNI** of total amount as the treasury delegation, distributing into selected delegates.

We select delegates based on the objective criteria and metrics (the DIP criteria/scoring + VP cut-off) after the application phase. Each selected delegate receives 1M UNI delegation. Furthermore, the top delegates by scores are considered Tier 1 delegates and receive additional 1M UNI delegations.

Once we conclude the program

====================================================================================================
[70] id=0xad0e29aa7bc8e783c15b959b92b02b871af879b8f36372e80fc5ff5fc189ed8f  token=UNI  space=uniswapgovernance.eth  date=2025-04-10
TITLE: [TEMP CHECK] BoB Uniswap v3 Incentives Package
CHOICES: For $375k | Against | Abstain
TEXT (first 1500 characters):
This proposal is brought to the DAO by the Uniswap Growth Program in collaboration with BOB (Build on Bitcoin).

# Overview

BOB is a unique Hybrid Layer 2 that combines Bitcoin’s security with EVM smart contracts. By placing BTC at the heart of DeFi, BOB can unlock new use cases and trillions in liquidity. This makes BOB the ideal home for Bitcoin DeFi - the best and safest place to earn yield on Bitcoin. In October, 2024, BOB [became an official Uniswap V3 deployment](https://gov.uniswap.org/t/application-for-canonical-uniswap-v3-deployment-on-bob/24693). This proposal lorequests a Uniswap Onboarding Package for BOB Network.

* As of today 27 Mar 2025, BOB boasts over [$247M of TVL](https://defillama.com/chain/BOB) across all of its Dapps, with [$42.78M in Uniswap v3 pools](https://defillama.com/protocol/uniswap-v3), ranking 5th among all UniV3 deployment, before OP mainnet and BSC, nearly three times the TVL of Rootstock.
* As BOB has demonstrated its ability to effectively attract users and LPs across both the EVM and Bitcoin space, BOB is looking to further bolster the network's state by allocating incentives to Uniswap pools as the BOB TGE takes place. Our goal is to leverage Uni v3 via Oku as the canonical DEX on the chain.
* BOB will therefore commit $500K over the next 6 months, and BOB is requesting Uniswap to match 75% of that ask.
* BOB has made it a point to ensure Uniswap sustains its lead as the canonical DEX on the L2, unlike other networks that may prioritize

====================================================================================================
[71] id=0x46fef087a43555e156db287d370151a76e19e1e2cd7d36f442409987f93d4215  token=UNI  space=uniswapgovernance.eth  date=2025-04-24
TITLE: [Temp Check/Revised] Treasury Delegation Round 2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Author

Tané

# Note

This is the revised version of [the original Snapshot](https://snapshot.box/#/s:uniswapgovernance.eth/proposal/0x04af1fcb7538cf5458c5c17baa50fe410952d48e98d451a6ca5f7b94fea87ee8) with a few changes below:

- Setting a shorter period of the delegations with the promise of re-evaluating the program if and when a significant change to the delegation landscape, especially the Unistaker implementation
- Election Snapshot for selection of the “distinguished” delegates out of the qualified delegates
- Reducing the total amount of UNI for delegations to up to 15M

You can check the details and ratinoale of them in [our latest comment](https://gov.uniswap.org/t/rfc-treasury-delegation-round-2/25355/39?u=tane).

# Background

The DAO started the first treasury delegations as a program called "Delegation of UNI to Active but Underrepresented Delegates" in December, 2023. According to [our analytics](https://gov.uniswap.org/t/treasury-delegation-round-2-ideas-thread/24667/13?u=tane) we shared in the original round 2 ideas thread, this program has been essential to keep the governance healthy and retain the active and capable delegates. At the same time, the originally promised time period has already passed, but the delegation has been kept as they didn't have their expirations. In addition, there have been discussions to consider how we proceed with the treasury delegation going forward. Through the process, we have decided to implement an important feature, expi

====================================================================================================
[72] id=0x537a301c4c94c1ec0b972bab558e2e36b1fa1111f0cbc4d5a59b0465f505c9ab  token=UNI  space=uniswapgovernance.eth  date=2025-06-17
TITLE: Uniswap Unichain - USDS and sUSDS Co-Incentives Growth Management Plan
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
![175016851880796415 (1).jpg](ipfs://bafybeieugymnkvemsrglx5rtynso5f2n6s7iva526qnmys7einzjutqkxq)
Summary

Unichain is currently the main focus of Uniswap’s growth strategy, presenting a significant opportunity for collaborative growth. The launch of USDS and sUSDS opens doors for close collaboration among two of the premier DeFi protocols Uniswap and Sky Ecosystem.

Following the launch of USDS and sUSDS on Unichain, this proposal aims to boost growth on Unichain through a combination of partnerships and matched incentives, driven by aligned KPIs related to USDS and sUSDS growth on Unichain.

Motivation

Unichain is currently growing almost exclusively in Uniswap pools. Growth in other DeFi protocols on Unichain is growing but still behind. The introduction of USDS and sUSDS creates opportunities for enhanced collaboration among DeFi protocols.

sUSDS provides yield, which itself is paid for by the Sky ecosystem. For example, if Unichain sUSDS TVL grows to 100 million, and at the current 4.5% of sUSDS yield, that would cost Sky 4.5 million USD per year. sUSDS can be a crucial part of the growth of the Unichain DeFi ecosystem, as it allows a stable and scalable yield source. For example, just examining Euler, removing Euler’s extra incentive, the lending APY is 3.19% for USDC and 2.05% for USDT as of June 4th 2025. However, if Euler were to integrate sUSDS yield and also provide its own incentive on top of incentive from Unichain, it could make it much more competitive yield

====================================================================================================
[73] id=0xc689d74757ccf1de09c3b8656dcd2f0d678972c9715a318aa4e9b659a5ebaca1  token=UNI  space=uniswapgovernance.eth  date=2025-07-07
TITLE: [TEMP CHECK] - Etherlink Co-incentives Proposal
CHOICES: Approve $150k of Coincentives | Do Not Approve
TEXT (first 1500 characters):
## TL;DR:

**Etherlink**, an EVM-compatible Layer 2 blockchain secured by Tezos Smart Rollup technology, proposes a co-incentive program to bootstrap liquidity on Uniswap v3. The **Tezos Foundation commits $300K** to incentivize strategic pools and requests a **$150K co-incentive** from the Uniswap DAO. This initiative will drive long-term liquidity, support ecosystem growth, and position Uniswap as the default AMM for uncorrelated asset pairs on Etherlink.

## About Etherlink

Etherlink is an EVM-compatible, non-custodial Layer 2 blockchain powered by Tezos Smart Rollup technology. It enables seamless integration with existing Ethereum tools, including wallets and indexers, and facilitates asset transfers to and from other EVM-compatible chains.

Built upon the secure foundation of Tezos Layer 1, Etherlink delivers a fast, fair, and (nearly) free experience. Developed by the same core teams behind Tezos and fully supported by the Tezos Foundation, Etherlink offers a permissionless and censorship-resistant environment that empowers developers to actively build and participate in the next generation of decentralized applications.

Officially launched in early 2025, Etherlink has seen strong TVL growth \- rising from approximately $1.5 million to \~$45 million within a few months \- driven primarily by the Apple Farm incentive program. With the launch of Season 2 and the onboarding of new protocols, we expect this growth to continue, targeting a minimum of $100 million in TVL b

====================================================================================================
[74] id=0xea4a1505c96ce4ef5c1f88e6cc3ec89d63f3d88219aa97af97b8384d006a5f92  token=UNI  space=uniswapgovernance.eth  date=2025-08-13
TITLE: Uniswap Delegate Reward Initiative - Cycle 4
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Uniswap Delegate Reward Initiative - Cycle 4

Authors: @Doo_StableLab @PGov @AranaDigital @seedgov
![AD_4nXds4EPLs4TfuPYDacVihDk88smRJZ58HQ0P_yvIaHWm4VbLsJjjU7460oYFufJTRY8LV-R2GqSeshizBT1duYUdfMdsjNYglNg96LyQ73qHZwLL2SzlOE6fq7Yz67heGZmLqPcZYA.png](ipfs://bafkreier2adm2ha4yntm2au6c5obpjbothxfw3dldflb4vzbwxdukjqw2y)

Summary
This proposal outlines the Uniswap Delegate Reward Initiative—Cycle 4, a compensation program designed to improve and sustain the participation quality and dedication among Uniswap delegates following the conclusion of Cycle 1, 2, and 3.

*Due to character limit on snapshot, background has been removed. Please check on the forum for the background.*
...
The significant change for Cycle 3 is an introduction of Delegate owned UNI token to reflect on requests from several Uniswap DAO members during the Cycle 3 debate (the debate on this topic) for experimentation. For this cycle, the basis will be 1,000 UNI token (<$10k of August 2nd price). Delegates who hold 1,000 UNI or more would be able to get a small additional point on the application and will be the basis for getting 100% of the Uniswap Delegate reward once accepted. Details on how UNI ownership is determined is explained below in “Uniswap Delegate Reward Cycle 4 Metrics.” We believe experimenting with such can potentially address the question of delegates having more “skin in the game.”

...

Cycle 4 Proposal Details
Application Eligibility

There will be a week-long period for candidates to submit t

====================================================================================================
[75] id=0xf9f99fe0f9425c2b2e624185860bcc38ac00bda6abe330e9c123f5c5c29dfbac  token=UNI  space=uniswapgovernance.eth  date=2025-08-24
TITLE: Establish Uniswap Governance as “DUNI,” a Wyoming DUNA
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Summary
The Uniswap Foundation (“UF”) proposes that Uniswap Governance adopt a Wyoming-registered Decentralized Unincorporated Nonprofit Association (“DUNA”) as the legal structure for the Uniswap Governance Protocol. This new legal entity, called “DUNI”, will be purpose-built to preserve Uniswap’s decentralized governance structure while enabling engagement with the offchain world (e.g., entering into contracts, retaining service providers, and fulfilling any potential regulatory and tax responsibilities).

If adopted, DUNI will be a legal entity for Uniswap Governance that recognizes the binding validity of onchain Governance Proposals with the intention of providing certainty regarding its legal structure and intended liability protections for members of DUNI. Adopting DUNI does not, in any way, alter the Uniswap Protocol, the UNI token, or the core mechanics of onchain governance. Rather, it represents a significant step in equipping Uniswap Governance for the future.

Importantly, establishing Uniswap Governance as a DUNA would bolster critical limited liability protections for governance participants. This step is intended to protect governance participants from potential personal exposure to possible legal or tax liabilities stemming from the collective action taken by Uniswap Governance. This is a critical step in de-risking engagement in Uniswap Governance without compromising decentralization.

# Background & Motivation
In the [Uniswap Unleashed](https://gov.unisw

====================================================================================================
[76] id=0xfc6edc8b64e1fa8eef46d187557969b14ca24ac58b8b6d6b302ea27a2213849d  token=UNI  space=uniswapgovernance.eth  date=2025-09-01
TITLE: Launching Uniswap v3 on Ronin with co-incentives
CHOICES: Deploy $500k in UNI Incentives | Do not deploy incentives
TEXT (first 1500 characters):
## Overview

This proposal advocates for an official UniswapV3 deployment on Ronin along with a co-incentivization campaign to establish UniswapV3 as a primary DEX in the Ronin Ecosystem.

All contracts necessary for Uniswap v3 deployment will be managed under Uniswap’s governance control. To bootstrap liquidity, in combination with the migration of POL and chain-owned liquidity from the [Katana DEX](https://app.roninchain.com/swap) to Uniswap v3, Ronin proposes a $1M contribution in [RON](https://coinmarketcap.com/currencies/ronin/) tokens, matched by $500K in UNI tokens from the Uniswap DAO.

Historically, Ronin has prioritized Katana DEX as its primary trading venue but is now shifting its focus towards making Uniswap v3 its canonical DEX.

Further details on the Ronin chain and its refreshed 2026 roadmap can be found in the RFC:
[https://gov.uniswap.org/t/rfc-deploying-uniswap-v3-on-ronin-with-co-incentives/25810 ](https://gov.uniswap.org/t/rfc-deploying-uniswap-v3-on-ronin-with-co-incentives/25810)

---

## Key Mutual Benefits of Deployment

1. Ecosystem Expansion (Gaming x DeFi)
Bringing Uniswap v3 to Ronin strengthens the DeFi offering within the largest Web3 gaming ecosystem. Ronin is actively innovating on new game loops that plug directly into DeFi primitives to seamlessly onboard the millions of active gamers into DeFi.

2. High Demand and Engagement
With 700K+ Discord members, 2,500+ content creators, and 300K newsletter subscribers, Ronin’s hyper-engaged communit

====================================================================================================
[77] id=0x0d56ae30379b00f3862b3e13ef44ce628f3d19609984b8fcfcf90e48b35842e8  token=UNI  space=uniswapgovernance.eth  date=2025-09-02
TITLE: GLI — Treasury delegation Round 2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Background:

Beginning in June, the UAC internally recognized votable supply, which at the time stood at ~41M UNI (relative to the 40M UNI quorum), as a potentially imminent and systemic risk to the DAO. In response, and in efforts to protect the DAO, the UAC proactively began the first Governance Logistics Improvement research report and RFC. The report sought to identify the greatest issues Uniswap governance faces, with particular emphasis on votable supply as it pertains to quorum.

Notably, the report emphasized that “the DAO operates under an unspoken dependency: that nearly all of its top delegates will participate in every vote, without exception. Put plainly, the exit of even a single large voter could bring governance to a standstill. Further, the risk of delegate removal from the voter body is not hypothetical; we’ve already seen this dynamic unfold as several institutional actors have scaled back participation in response to regulatory pressures.”

Incidentally, during the initial weeks of research, that dependency risk became a material reality as changes in the token custody process led to A16Z’s removal of ~20M UNI from delegation. As it stands today, the consistently active votable supply stands at just 21M UNI. This is just 52.5% of the required 40M UNI quorum, or approximately a $209 million vote deficit. While the UAC strongly believes that, for now, critical proposals will pass through the direct support of large, less active voters, such as A16Z, broader

====================================================================================================
[78] id=0x1423731999c4ddd17568ac01b1b0f64f12c26138f0c3f9284dd688fa1d665989  token=UNI  space=uniswapgovernance.eth  date=2025-09-02
TITLE: GLI — Incentivized Delegation Vaults
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Background:

Beginning in June, the UAC internally recognized votable supply, which at the time stood at ~41M UNI (relative to the 40M UNI quorum), as a potentially imminent and systemic risk to the DAO. In response, and in efforts to protect the DAO, the UAC proactively began the first Governance Logistics Improvement research report and RFC. The report sought to identify the greatest issues Uniswap governance faces, with particular emphasis on votable supply as it pertains to quorum…

To address this mounting issue, the UAC invoked an open call for community-sourced solutions. This call resulted in five potential pathways, which were then aggregated and presented to the community. Of those five proposed solutions, two have emerged with majority support within the forum discussions: Treasury Delegations and Incentivized Delegation Vaults. (Governance Logistics Improvement)

This proposal addresses Incentivized Delegation Vaults.

UAC Next Steps:

UAC: 
With regards to IDVs, the UAC will serve under the DAO’s guidance as the program manager of the Incentivized Delegation Vault initiative, should it pass (detailed below).

Author: Event Horizon

Proposal Summary:
Incentivized Delegation Vaults: Multiple delegates recognized that it is not healthy for the governance ecosystem if the entirety of the votable supply is sustained by treasury delegations alone. As such, encouraging community delegations is essential. The most direct and intuitive approach is to incentivize participa

====================================================================================================
[79] id=0x9a52a7fc0213d077b11924e1d0949637bbc9b6f07cd0bebeff70b92da0cda4ff  token=UNI  space=uniswapgovernance.eth  date=2025-09-29
TITLE: Treasury Delegation Round 2 Elections
CHOICES: Proxy | cp0x | Curia | KPK | Event Horizon | SEEDGov | Tane | Arana Digital | Argonauts | Avantgarde | DAOplomats
TEXT (first 1500 characters):
This proposal ([Link Here](https://gov.uniswap.org/t/gli-treasury-delegation-round-2-applications/25832)) represents the second of two phases of the Treasury Delegation Round 2 application process, the election. The following nominees have been validated as eligible for inclusion during the first application phase.

**Voting Process:** The DAO will allocate voting power to each candidate as it sees fit. At the end of the voting period, all delegates will be ranked in order from the most to the least votes received. Sequentially from the top of the list to the bottom, each delegate will receive delegated voting power up to the point at which they individually hold 2.5M total VP. Then, the process repeats for the next delegate, and the next, until all VP has been allocated.

**Self-Voting Policy:** Because this election is not for a finite number of seats, and it is best to encourage broader distribution of votes, self-voting will not leverage the max-matching model seen during committee elections. Instead, each voter will be eligible to commit a maximum of 25% to himself or herself and distribute the remainder as they see fit. 

**Violation Policy:** If a delegate violates the self-voting policy, the portion of their voting power allocated to themself will be considered void. Any portion allocated toward other delegates will persist.

**Ranking and Distribution Calculations:** After election closure, all nominees will be ranked in order of most to least votes received, and the

====================================================================================================
[80] id=0x58d854c1f2468db6b67baab026cca1329c7bcaa5bf834146aa7563a5b45ad09f  token=UNI  space=uniswapgovernance.eth  date=2025-11-18
TITLE: UNIfication
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
![image (4).png](ipfs://bafybeicttadfmczxrupf7xsfcj5e5djhoajdezstgcklmvgsnvfwzeyn3m)

By voting “For” on this Snapshot, you are signaling support for the proposal summarized below and detailed in the [forum](https://gov.uniswap.org/t/unification-proposal/25881). 

## TL;DR

Uniswap Labs and the Uniswap Foundation have created a joint proposal that activates the protocol fee and aligns incentives across the Uniswap ecosystem.

We propose:

1. Turning on Uniswap protocol fees and using these fees to burn UNI  
2. Sending Unichain sequencer fees to this same UNI burn mechanism  
3. Building Protocol Fee Discount Auctions (PFDA) to increase LP returns and allow the protocol to internalize MEV  
4. Developing aggregator hooks, turning Uniswap v4 into an onchain aggregator that collects fees on external liquidity  
5. Burning 100 million UNI from the treasury, representing the approximate amount of UNI that would have been burned if fees were on from the beginning  
6. Focusing Labs on driving protocol development and growth, including turning off Labs’ interface, wallet, and API fees, and contractually committing to only pursue initiatives that align with DUNI interests  
7. Moving ecosystem teams from the Foundation to Labs, with a shared goal of protocol success, with growth and development funded from the treasury  
8. Migrating governance-owned Unisocks liquidity from Uniswap v1 on mainnet to v4 on Unichain and burning the LP position, locking in the supply curve forever

***L

====================================================================================================
[81] id=0x0242a914c60945d25873d2a98c6abd9f69cb889c6616e27f3c0ab759f9e8d783  token=UNI  space=uniswapgovernance.eth  date=2026-02-18
TITLE: [Temp Check] Protocol Fee Expansion: Eight More Chains and Remaining Mainnet V3 Pools
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# [Temp Check] Protocol Fee Expansion: Eight More Chains and Remaining Mainnet v3 Pools

_This is the first proposal to use the new governance process_ [_approved_](https://gov.uniswap.org/t/unification-proposal/25881#p-57882-protocol-fee-rollout-4) _in UNIfication. The new process only applies to fee parameter updates, where proposals can bypass the RFC stage and go directly to a five-day Snapshot followed by an onchain vote. This allows for faster updates to protocol fees, while retaining the security of onchain governance._

Since UNIfication went live in late December we have been monitoring protocol fees, which were rolled out gradually to ensure protocol health. This started with v2 and select v3 pools on Ethereum mainnet. This rollout has gone well, with market-adjusted TVL [up](https://defillama.com/protocol/uniswap?fees=false&events=false&denomination=ETH) on Ethereum mainnet since December. The burn system is working as expected, permissionlessly converting fees in [many different tokens](https://dune.com/queries/6711845) into UNI burns.

Now, we propose to:

-   Expand protocol fees on v2 and v3 to Arbitrum, Base, Celo, OP Mainnet, Soneium, X Layer, Worldchain, and Zora
    
-   Enable protocol fees on all v3 pools via a new tier-based [v3OpenFeeAdapter](https://github.com/Uniswap/protocol-fees/blob/main/src/feeAdapters/V3OpenFeeAdapter.sol) on mainnet and the above L2s
    

## **Implementation Details**

**Expand protocol fees to L2s and burn UNI on mainnet**  
T

====================================================================================================
[82] id=0xd41b2db93c0348e9061bf786dfcb610d8f35e8447f2e90b37b8f30a9b1a3091e  token=UNI  space=uniswapgovernance.eth  date=2026-05-03
TITLE: Return 12.5M Delegated Tokens to the Governance Timelock
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**Background and Motivation**
With DUNI unlocking greater governance participation from UNI token holders, this proposal undelegates 12.5M UNI currently deployed via the Franchiser, returning the tokens to the Governance Timelock.

These UNI were delegated from the treasury in 2022 and 2023 – 2.5M to the Uniswap Foundation and 10M to a group of active delegates – during periods of low governance participation. The delegations were intended to bootstrap an active delegate base when quorum was at risk and the number of delegates that could meet the proposal threshold was small.
Today, Uniswap’s governance environment looks very different. UNI holders have been actively delegating voting power, and since DUNI was established, passed proposals have averaged roughly 75 million votes in turnout, exceeding quorum by approximately 88%. There are now over 50 delegates with greater than 1M UNI of voting power.

Undelegating these tokens also resolves a potential incentive misalignment caused by the Franchiser mechanism itself. These delegates were selected by the community for their active participation in governance, but the Franchiser was not designed to ensure structural alignment between voting power and economic exposure. The potential for this misalignment should not persist indefinitely when the original reason for implementing it is no longer a concern.

====================================================================================================
[83] id=0x34954750c83fdbea3d428e387aa7948eecd66d2f76c35f5588c3f1fd1e1f5c4d  token=UNI  space=uniswapgovernance.eth  date=2026-05-16
TITLE: [Temp Check] Protocol Fee Expansion: Three More Chains
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal continues the protocol fee rollout, following proposals [#92](https://vote.uniswapfoundation.org/proposals/92), [#93](https://vote.uniswapfoundation.org/proposals/93), and [#94](https://vote.uniswapfoundation.org/proposals/94). It uses the expedited governance process [approved](https://gov.uniswap.org/t/unification-proposal/25881#p-57882-protocol-fee-rollout-4) in UNIfication, where fee parameter update proposals can bypass the RFC stage and go directly to a five-day Snapshot followed by an onchain vote.

Since protocol fees went live on Ethereum mainnet in late December, the rollout has extended to nine additional chains (Arbitrum, Base, OP Mainnet, Soneium, X Layer, Worldchain, and Zora). The burn system is working as designed, with fees accumulating in TokenJars across chains. From there, searchers claim them in exchange for burning UNI by bridging it back to mainnet and sending it to the burn address.

This proposal:

* Extends the infrastructure for collecting and burning protocol fees to BNB Chain and Polygon
* Enables v2 and v3 protocol fees on these chains
* Completes Celo's fee activation through a corrected cross-chain governance path, which was approved in a previous [proposal](https://vote.uniswapfoundation.org/proposals/94) but did not execute due to a configuration error

## Implementation Details

Fees on each chain will be routed to the TokenJar on that respective chain. UNI burned on these chains is bridged back to Ethereum mainnet and sent to

====================================================================================================
[84] id=0x3fda3c04fa106ad45173011ef4dfa5db2f14cd35c3c3a7a40f067a44cbadd5f4  token=UNI  space=uniswapgovernance.eth  date=2026-07-07
TITLE: [Temp Check] Activate v4 Protocol Fees
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Summary

This proposal continues the protocol fee rollout approved in UNIfication, following proposals [#93](https://vote.uniswapfoundation.org/proposals/93), [#94](https://vote.uniswapfoundation.org/proposals/94), [#95](https://vote.uniswapfoundation.org/proposals/95), and [#96](https://vote.uniswapfoundation.org/proposals/96). It uses the expedited governance process where fee parameter update proposals go directly to a five-day Snapshot followed by an onchain vote.

Protocol fees are now live across all v2 and v3 pools on 11 chains - Ethereum, Arbitrum, Base, Celo, OP Mainnet, Soneium, X Layer, Worldchain, Zora, BNB Chain, and Polygon. Last month, the protocol set a record burning [186,000 UNI in one day](https://x.com/UNIBurnBot/status/2063252718043459633).

Below we introduce a system for v4 protocol fees and propose to activate it on a subset of v4 pools on these same chains.

---

## Implementation Details

v4's hook architecture requires a different approach to fee activation than v2 or v3. v2 pools have a single LP fee tier and are charged a static fee. v3 has several LP fee tiers, each charged a static fee. Hooks mean v4 has potentially infinite distinct LP fee tiers, and a pool's fees can change dynamically from one block to the next. To manage this, we propose a V4 Fee Controller system where governance sets rules that let a dedicated contract compute the fee for any pool on demand, rather than setting a fee on each individual pool.

The system splits across tw

====================================================================================================
[85] id=0xc5fd6e916655b293c903b060906c994ff1ff1df348336b3b3e22ceecd2d13d7c  token=UNI  space=uniswapgovernance.eth  date=2026-07-11
TITLE: [Temp Check] Protocol Fee Expansion: Robinhood Chain
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
_This proposal is part of the protocol fee rollout, following proposals_ [_#93_](https://vote.uniswapfoundation.org/proposals/93)_,_ [_#94_](https://vote.uniswapfoundation.org/proposals/94)_,_ [_#95_](https://vote.uniswapfoundation.org/proposals/95)_, and_ [_#96_](https://vote.uniswapfoundation.org/proposals/96)_. It uses the expedited governance process_ [_approved_](https://gov.uniswap.org/t/unification-proposal/25881#p-57882-protocol-fee-rollout-4) _in UNIfication, where fee parameter update proposals can bypass the RFC stage and go directly to a five-day Snapshot followed by an onchain vote._

Since protocol fees went live on Ethereum mainnet in late December last year, the rollout has extended to ten additional chains: Arbitrum, Base, OP Mainnet, Worldchain, X Layer, Soneium, Zora, Celo, BNB Chain, and Polygon. The burn system is working as designed, with fees accumulating in TokenJars across chains. From there, searchers claim them in exchange for burning UNI by bridging it back to mainnet and sending it to the burn address.

Uniswap [launched on Robinhood Chain](https://blog.uniswap.org/robinhood-chain-is-live) at the chain's July 1, 2026 mainnet debut, with v2, v3, and v4 all live. As of July 10, the deployments have crossed [$1b of cumulative swap volume](https://x.com/DefiLlama/status/2075608063969485082?s=20). This proposal:

-   Extends the infrastructure for collecting and burning protocol fees to Robinhood Chain
    
-   Enables v2, v3, and v4 protocol fees on R

====================================================================================================
[86] id=0x5ae3426216321df66a67eb677874b725f80e51888ad2da72b382b21669c554ee  token=UNI  space=uniswapgovernance.eth  date=2026-07-21
TITLE: [Temp Check] - Four for V4
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
## Summary

GFX Labs/Oku Trade proposes deploying Uniswap V4 on four EVM-compatible networks: **Sei, Etherlink, Pharos, and 0G**. These deployments expand V4's footprint, generate protocol fees across new chains, and give hook developers new environments to build on. With Morpho deployed on these networks, the addition of V4 provides a playground for unique financial applications to be developed. V3 is deployed on all chains and acts as the main liquidity hub for the networks.

No treasury spend is requested — GFX Labs covers all costs.

---

## Background

Since 2022, GFX Labs has deployed Uniswap V3 to 30+ EVM chains through Oku Trade, funding and executing the majority of deployments independently. With Oku's V4 interface complete, we are positioned to continue this expansion.

This proposal covers four chains where the community, liquidity environment, or emerging technical primitives create meaningful opportunities for the Uniswap DAO.

---

## Upside for the DAO

The four networks in this proposal collectively represent a meaningful and growing source of protocol fee revenue for the DAO. Sei recorded $1.5B in DEX volume in Q1 2026 with TVL holding steadily above $50M. With limited competition outside of Sei's native DEX Saphyre, V4 is well positioned to carve out meaningful market share. Pharos adds further upside — with mainnet recently live and over $100M committed to RWAs on the network, V4 has a clear opportunity to become the primary trading protocol on a chain pur

====================================================================================================
[87] id=0xe1ac3254ff43d5d780fc6ae1f13a0c027c2ef138fadb316198d3ed814a154b7e  token=UNI  space=uniswapgovernance.eth  date=2026-09-18
TITLE: Protocol Fee Expansion: Arc
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
*This proposal is part of the protocol fee rollout, following proposals [#93](https://vote.uniswapfoundation.org/proposals/93), [#94](https://vote.uniswapfoundation.org/proposals/94), [#95](https://vote.uniswapfoundation.org/proposals/95), [#96](https://vote.uniswapfoundation.org/proposals/96), [#99](https://vote.uniswapfoundation.org/proposals/99), and [#100](https://vote.uniswapfoundation.org/proposals/100). It uses the expedited governance process [approved](https://gov.uniswap.org/t/unification-proposal/25881#p-57882-protocol-fee-rollout-4) in UNIfication, where fee parameter update proposals can bypass the RFC stage and go directly to a five-day Snapshot followed by an onchain vote.*

Since protocol fees went live on Ethereum mainnet in late December last year, the rollout has extended to eleven additional chains: Arbitrum, Base, OP Mainnet, Worldchain, X Layer, Soneium, Zora, Celo, BNB Chain, Polygon, and Robinhood Chain. The burn system is working as designed, with fees accumulating in TokenJars across chains. From there, searchers claim them in exchange for burning UNI by bridging it back to mainnet and sending it to the burn address.

Arc is a Layer 1 built by Circle for the world's financial markets, real-time money movement, and agentic economic activity, with [mainnet going live September 16, 2026](https://www.arc.io/blog/arc-mainnet-goes-live-on-september-16-2026). Uniswap was live on Arc from launch, with v2, v3, v4, and UniswapX all deployed.

This proposal:

*

====================================================================================================
[88] id=0x222d41ca946c553e592a0b96d9eee4828fb2d319b308c0ed638dfc89821bdfe6  token=W  space=wormholegovernance.eth  date=2025-06-10
TITLE: WIP-3: Establishment of a Grants Program
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**Abstract**
This proposal introduces a Grants Program governed by Wormhole Governance and its delegates. The program is intended to fund and support initiatives that meaningfully contribute to the growth and success of the Wormhole ecosystem. The program will have a budget of $250,000 USD, also denominated in $W. Delegates will be responsible for evaluating proposals and voting, while the Wormhole Foundation will handle administrative execution and fund disbursement. Since there is currently no onchain treasury, all disbursements will be handled manually by the Wormhole Foundation.

The entire proposal and its details can be viewed here: https://forum.wormhole.com/t/wip-3-establishment-of-a-grants-program/797

====================================================================================================
[89] id=0x74b097679b67a7d9b215ee8e67d224a5d52abf4008b5a617f523d9527ba55f54  token=WCT  space=walletconnect.eth  date=2025-07-29
TITLE: P3 - WCT Staking Redesign
CHOICES: Yes | No
TEXT (first 1500 characters):
## Abstract

Perpetual Stake with User-Triggered Unlocking & Discrete Duration Options

## Summary

We propose a redesign of the WCT staking mechanism to simplify usage, improve reward predictability, and provide greater flexibility to users. This includes the introduction of **Perpetual Staking Positions with User-Triggered Unlocking Periods**, a **set of discrete duration options for creating positions**, and **preserved support for the current decaying model** as an optional path.

**Current Implementation**

![image (4).jpg](ipfs://bafybeih4pzzzgh2c5v7fhuw3nshmcw6j45gzd7msyx3lcpv5o73pcbhkka)

*This chart visualizes the current staking mechanism, where two positions—Position A (12-month duration) and Position B (6-month duration)—are created simultaneously at T₀. Upon creation, both positions immediately enter their respective unstake periods. From that point forward, their stake weight begins to decrease gradually each week until it reaches zero, at which time the position becomes unlocked.*

*The unlock timing is determined solely by the duration set at creation: Position B unlocks at T₀ + 6 months, while Position A unlocks at T₀ + 12 months. As shown in the chart, Position B maintains a consistently lower stake weight than Position A throughout its lifecycle, reflecting the shorter commitment period.*

**Proposed Improvement**

![image(5).jpg](ipfs://bafybeiatz22tshgfbbueipocjsybo6cay5gq2vmlgbsqwrepedebdufcoe)

*The chart compares two staking positions initiated simulta

====================================================================================================
[90] id=0x3d6b84e2456d7e1248f83b6c60fbb37fbef9f04a0db0ae50cfc23e2cf530b1e5  token=WCT  space=walletconnect.eth  date=2026-03-10
TITLE: P5 - WalletConnect Pay Rewards Budget
CHOICES: For | Against
TEXT (first 1500 characters):
## Abstract

This proposal introduces a **WCT rewards budget for use and distribution of WalletConnect Pay** by allocating **50M WCT in 2026** to accelerate consumer usage, wallet adoption, and payment volume via WalletConnect Pay.

## Summary

This proposal establishes a **WalletConnect Pay Rewards Budget**, to incentivize both:

- **Consumers**, for making eligible retail purchases via WalletConnect Pay, and
- **Wallets**, for onboarding users and driving WalletConnect Pay usage through their wallet.

Rewards are **denominated and distributed in WCT tokens** and are designed to **align incentives across users, wallets, merchants, and the WCT ecosystem**.

WalletConnect Network will allocate **50M WCT in 2026** as a dedicated rewards budget for WalletConnect Pay to execute and evolve its rewards program. The program is expected to prioritize simplicity, predictability, and long-term sustainability, while allowing parameters such as rates and caps to evolve over time based on ecosystem feedback and performance evaluation.

## Background

WalletConnect Pay operates in a retail environment where adoption and scale depend on **user incentives**, **distribution**, and **developer participation**.

### Consumer Rewards

Traditional payment systems rely heavily on **cashback and consumer rewards** to drive usage, habit formation, and retention. These programs are typically funded through interchange, marketing budgets, or merchant subsidies and have become a standard growth lever a

====================================================================================================
[91] id=0x21cb61f1d9256335e656d2a63d8ac0ceddb1313ad490c95b713bbef9e313fda2  token=WLFI  space=worldlibertyfinancial.com  date=2025-09-11
TITLE: Proposal: Use 100% of WLFI Treasury Liquidity Fees for Buyback & Burn
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
**Summary**

This proposal directs all fees earned by WLFI’s protocol-owned liquidity (POL) to be used for buying WLFI on the open market and permanently burning it.

- Only fees from WLFI-controlled liquidity are included.
- Fees from community or third-party LPs are not affected.

**Why This Matters**

- **Direct supply reduction**: Every trade generates fees that will now remove WLFI from circulation.
- **Stronger holder alignment**: This program removes tokens from circulation held by participants not committed to WLFI’s long-term growth and direction, effectively increasing relative weight for committed long-term holders.
- **Alignment with growth**: More usage = more fees = more WLFI burned.
- **Transparency**: Burns are recorded on-chain and reported to the community.

**How It Works**

1. WLFI collects fees from its own liquidity positions on Ethereum, BSC, and Solana.
2. These fees are used to buy WLFI tokens back on the market.
3. Purchased tokens are then sent to a burn address, permanently reducing supply.

**Alternatives Considered**

- Keeping fees in the Treasury for operations.
- Splitting fees between Treasury and burn.

We believe the community preference is to maximize impact and burn 100% of WLFI POL fees.

**Voting Options**

- FOR: Use all WLFI Treasury POL fees for buyback & burn.
- AGAINST: Keep fees in the Treasury.
- ABSTAIN: No preference.

**Future Expansion**

If this proposal is passed, WLFI will treat it as the foundation of an ongoing buyback a

====================================================================================================
[92] id=0x4cb62c60be4f0664dc4394f4e2c42f748993b3c3c13d88cfb8ab165ffdedb508  token=WLFI  space=worldlibertyfinancial.com  date=2025-12-28
TITLE: Proposal: Utilize Unlocked $WLFI Treasury Holdings to Support the Growth of USD1
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
**Summary:**

This advisory proposal recommends World Liberty Financial begin to actively utilize a limited allocation of its unlocked treasury to support the growth of USD1. This will allow World Liberty Financial to enhance strategic partnerships and support the adoption and usage of USD1.

**Motivation:**

USD1 is among the world’s fastest growing stablecoins, hitting ~$3b in TVL in 6 months. This milestone has been achieved due to an upswell of community support across core stablecoin onchain use cases such as trading and a number of large partnerships. The team continues to arduously work to grow adoption and usage of USD1, working toward the core vision of democratizing finance and access to the dollar globally.

In order to support development and usage of USD1 in an increasingly competitive stablecoin landscape, World Liberty Financial intends to utilize a small percentage of unlocked $WLFI tokens to support USD1 use cases across select high profile CeFi & DeFi partnerships.

**Specification:**

World Liberty Financial plans to clearly identify all partners where $WLFI incentives are deployed on its website and in written online communications.

**Impact:**

USD1 is the first flagship product of the World Liberty Financial ecosystem. $WLFI remains the governance and coordination layer that unifies every current and future product we launch. The success of USD1 directly strengthens WLFI because USD1 adoption expands the overall footprint, utility, and economic activity

====================================================================================================
[93] id=0x79b572f1e64827a9d379684916ee2af602edc776b412556fe93304170d69c67a  token=WLFI  space=worldlibertyfinancial.com  date=2026-03-05
TITLE: Proposal: WLFI Governance Staking System
CHOICES: FOR | AGAINST | ABSTAIN
TEXT (first 1500 characters):
# Abstract

This proposal introduces the WLFI Governance Staking System. As governance tokens, WLFI are the consensus mechanism for WLF in determining the WLFI community’s views on the direction of the WLFI ecosystem. Active governance participation will enhance the technological operation, security and confidence in reflecting this consensus through the governance platform. The core objectives are to: (1) encourage active participation in WLFI governance, (ii) require staking as a prerequisite for governance voting for unlocked tokens, (2) reward participation in WLFI governance, (3) create a tiered node structure that incentivizes long-term ecosystem participants which have committed the most to governance through access to USD1, and (4) establishes a mechanism to prioritize partnership deal flow toward projects actively supporting WLFI governance and the WLFI ecosystem.

# Motivation

WLFI wishes to further incentivize more significant participation in governance, and to provide additional benefits for USD1 usage. In addition, in the recent USD1 expansion phase, market makers captured millions in arbitrage profits (~15 bps per minting/selling cycle), and WLFI additionally paid millions in subsidies to facilitate redemptions. This proposal redirects this value from a small number of intermediaries to long-term ecosystem participants, while simultaneously creating structural demand pressure on competing stablecoins.

# Specification

**1. Participation in Governance with Unl

====================================================================================================
[94] id=0x7389a30748bf921066fba2d63281e34718b141cef9f54fcb4ed5cd4566f94873  token=WLFI  space=worldlibertyfinancial.com  date=2026-04-29
TITLE: Proposal: Early Supporter & Founder/Team/Partner Token Unlock
CHOICES: YES | NO
TEXT (first 1500 characters):
**Tokens Subject to This Proposal**

-   Early supporter locked tokens: 17,043,666,558 WLFI (Reflects currently confirmed locked early supporter tokens, but may increase if holders with unclaimed prior allocations claim and enter the locked pool before this proposal takes effect)
    
-   Founder, team, advisor, and partner locked tokens will all be pushed to a longer vesting schedule: 45,238,585,647 WLFI
    
-   Total subject to this proposal: 62,282,252,205 WLFI
    

10% of founder, team, advisor and partner token allocation — 4,523,858,565 WLFI — is eligible to be permanently burned and removed from the total supply.

---

**Where We Are & Why This Matters Now**

When WLFI launched, WLFI made a bet that compliant, institutionally-ready DeFi was not only possible but inevitable. A lot has since happened in the WLFI ecosystem.

---

**Governance Participation History**

Since inception, WLFI has passed six governance proposals spanning protocol infrastructure, tokenomics, and ecosystem growth. Participation across those votes ranged from 2.7B to 11.1B WLFI:

-   Proposal to launch Aave V3 instance on Ethereum Mainnet — 8.0B WLFI
    
-   Proposal: Test Airdrop Functionality by distributing USD1 to all WLFI holders — 6.8B WLFI
    
-   Proposal: Make WLFI token tradable — 11.1B WLFI
    
-   Proposal: Use 100% of WLFI Treasury Liquidity Fees for Buyback & Burn — 4.4B WLFI
    
-   Proposal: Utilize Unlocked WLFI Treasury Holdings to Support USD1 Growth — 4.2B WLFI
    
-

====================================================================================================
[95] id=0x33496f16e246d02b0059a3a3448df68624e5f886a9c93bf2d01d91fe787ce470  token=WLFI  space=worldlibertyfinancial.com  date=2026-09-21
TITLE: Proposal: Launch $WLFI Governance Engagement Incentive Program
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
## Summary

The World Liberty Financial ecosystem has experienced significant growth, led by the rapid adoption of USD1 and the continued expansion of World Liberty Markets. USD1 has quickly grown into a major stablecoin with increasing adoption across centralized exchanges, DeFi protocols, institutional use cases, and multiple blockchain networks. At the same time, World Liberty Markets provided by Dolomite (“**WLFI Markets**”) has grown into a top-10 lending market and continues to experience strong growth in deposits, borrowing activity, and overall usage. This proposal seeks to build on that momentum by using governance staking incentives as a mechanism to deepen participation in WLFI governance.

This proposal recommends launching the $WLFI Governance Engagement Incentive Program (the “Program”) by October 1, 2026, introducing a governance participation incentive designed to encourage holders to remain actively aligned with governance and participation in the long-term direction of the World Liberty Financial ecosystem. The Program is structured as a promotional campaign using promotional allocations and participation recognition to encourage governance engagement and platform usage. This proposal, if approved, will supersede and replace the ecosystem proposal that was approved on March 12, 2026.

The initial staking rewards pool may be funded from various sources, including:

1.  Amounts from ecosystem sources, which may include fees received by WLF from World Liberty M

====================================================================================================
[96] id=0x3b3fe61f71b9b597f67c7b1b12e5c9bc171ad0a488e1f1b8cb0ad8416c5b3a84  token=XCN  space=chaingov.eth  date=2025-05-05
TITLE: Tiered Staking Rewards for Staking
CHOICES: Yes | No
TEXT (first 1500 characters):
Introduce a simplified multiplier-based staking system.

Example:
Month 1 - Current staking APR + 2%
Month 2 - Current staking APR + 4%
Month 3 - Current staking APR + 6%
And so on..
Longer staking duration = higher APR. 

This strengthens user commitment, reduces sell pressure, and supports XCN tokenomics.

Why Support This?
	•	Easy to understand, easy to implement.
	•	Encourages stronger hands.
	•	Reduces token circulation.

====================================================================================================
[97] id=0x837f5a9f0a34f7edb5e50acc0bad509d3805dff9124220d908248da511622b4c  token=XCN  space=chaingov.eth  date=2025-05-05
TITLE: Justin Sun to have a formal smart contract to ensure investor protection.
CHOICES: Yes | No
TEXT (first 1500 characters):
This proposal mandates the creation and deployment of an onchain smart contract to enforce the two-year lockup period for the 500 million XCN granted to Justin Sun and HTX in OIP-52. It also stipulates that these granted tokens will not be eligible for staking APR during the lockup period, as they were acquired via DAO allocation rather than market participation.

Rationale

OIP-52 allocated 500 million XCN to Justin Sun and HTX with the stated condition of a two-year lockup. As of now, no smart contract has been deployed to enforce this lockup, and there is no public guarantee that the tokens are non-transferable or non-stakable during the lockup period.

In the absence of an enforced smart contract, the DAO cannot verify that these tokens are secure, inactive, or excluded from staking rewards — which would create an unfair dynamic compared to users who purchased and locked tokens at market price.

This proposal reinforces the original agreement, preserves tokenomics fairness, and restores community trust by ensuring the lockup is technically enforced and economically neutral during its duration.

Specification

A smart contract will be deployed to hold the 500 million XCN with the following conditions:

Tokens will be non-transferable and non-stakable for a period of 730 days from the date of lockup execution.

Tokens may not accrue staking rewards (APR) during this time.

Contract code will enforce a strict unlock date and publish this date via a public method such as unlo

====================================================================================================
[98] id=0x95b9656f39c770c0306c4905a67187b0775a8b6cedd9f7d8a29975c33128dd8a  token=XCN  space=chaingov.eth  date=2025-05-17
TITLE: Enable Voter Incentives via Snapshot + Zealy Governance Quests
CHOICES: For | Against
TEXT (first 1500 characters):
To increase participation in Onyx DAO governance, this proposal introduces a system that rewards Snapshot voters through two participation paths:
	1.	Zealy Quests – For users who want to earn XP by completing governance-related tasks
	2.	Direct Snapshot Tracking – For users who vote but do not use Zealy

Either path will be eligible for the same core incentives such as:
• Onyx Points bonus in Season 2
• Early access to dApps and governance tools
• And more

Implementation Plan:
	•	Launch Zealy governance quests
	•	Begin tracking voter participation via Snapshot
	•	Distribute perks at the end of each season (e.g., pre-mainnet phase, Season 2)

Goal of This Proposal:

To increase meaningful participation in Onyx DAO governance by rewarding active voters and to build long-term DAO engagement ahead of mainnet.

====================================================================================================
[99] id=0x734acfc1c6657152bc47def46fcb7059b5ee543617c9038077922bdfd7d75f66  token=XCN  space=chaingov.eth  date=2025-06-10
TITLE: Reinstate Chain as Lead Developer for the DAO
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal seeks community approval to reinstate Chain as the lead developer for the DAO, effective immediately. Chain’s role will encompass development leadership, ISO compliance oversight, AMA engagement, and strategic coordination across all major DAO initiatives.

⸻

Background on Chain

Chain is a blockchain-based technology company founded in 2014 with a mission to enable a smarter and more connected economy. The company specializes in building cryptographic ledgers and cloud infrastructure that power transformative financial products and Web3 services.

Over the years, Chain has raised more than $40 million in funding from top-tier institutions such as Khosla Ventures, Pantera Capital, Capital One, Citigroup, Nasdaq, Fiserv, Orange, and Visa. Initially acquired by Stellar in 2018 to form Interstellar, Chain was re-acquired in 2020 to continue its independent mission of reshaping global financial infrastructure using blockchain technology.

Chain’s products and solutions have been trusted by companies across multiple industries—including payments, sports, retail, and banking—with work done with major brands and institutions such as Tiffany & Co., Citi, MUFG, State Street, and the Miami Heat.

⸻

Scope of Responsibilities

If approved, Chain will resume a leadership position in guiding the DAO’s technical and strategic development. This includes:

  •  Development Oversight: Chain will lead the design, execution, and maintenance of DAO infrastructure, ensuring secure,

====================================================================================================
[100] id=0x6bf863b88a7703a27897b64ac50e396983cd0476958dfbe9cc05b490d4309802  token=XCN  space=chaingov.eth  date=2025-06-14
TITLE: Diversify DAO Treasury
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal seeks community approval to diversify the DAO’s treasury by allocating a portion of its holdings into a basket of multiple cryptocurrencies.

If this proposal passes, follow-up polls will be conducted to determine which specific assets to include, along with allocation percentages and operational details (e.g. custody, conversion timing, and risk management strategies).

====================================================================================================
[101] id=0xed1a886234eb71e84bd6b33f1823e80c60ceaf5a724d1a8e0c37a9973f87c52f  token=XCN  space=chaingov.eth  date=2025-06-19
TITLE: Adjust XCN Emissions Rate
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal seeks community approval to lower staking rates by adjusting daily emissions to 2.5M XCN, with the goal of eliminating farming arbitrage via futures markets and promoting a healthier, more sustainable long-term ecosystem.

Current staking dynamics create opportunities for short-term arbitrage that distort the market and undermine the value of long-term participation. By reducing emissions to 2.5M per day, we aim to discourage exploitative strategies while preparing for the rollout of more robust locked staking mechanisms.

If approved, the DAO will implement the new emission rate as an interim measure to:

• Disincentivize yield farming arbitrage with derivatives
• Promote organic staking aligned with long-term growth
• Support market sustainability until locked staking is in place

This change is intended to align incentives with the project’s long-term vision and ensure fairer distribution of rewards among committed participants.

====================================================================================================
[102] id=0x688791a5a1e65ef8c31282bb16d075c74a23d0859d1005f454972159e39f2b2e  token=XCN  space=chaingov.eth  date=2025-08-13
TITLE: Reverse the previous emissions rate change implemented in OIP59
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
OIP reduced the emissions rate for staking with the intention of mitigating price pressures due to arbitrage between XCN futures and XCN staking rewards.

As of August 13, there is no evidence that price pressures have been alleviated.

In addition, the prior poll on this subject had a majority of votes (7 of 13) and voting power AGAINST the change, when excluding the DAO wallet.

A Vote FOR is to restore the emission rate on staking to what it was prior to OIP59

A Vote AGAINST is to leave the current emission rate as it is.

====================================================================================================
[103] id=0xdd9fca093f508bd18c9ef9447a5e31cc69c3a4dae40b2a084be7cc6f0a940751  token=XCN  space=chaingov.eth  date=2025-09-19
TITLE: Increase XCN Native Staking rate to 40%
CHOICES: For | Against
TEXT (first 1500 characters):
This poll represents a significant milestone for the Onyx community as we consider an adjustment to our native staking framework. By increasing the XCN Native Staking rate to 40%, we aim to strengthen protocol security while rewarding participants with higher yields.

This initiative directly benefits users who stake their ERC-20 XCN through the Onyx Protocol app (https://app.onyx.org/#/stake), aligning incentives to secure the network and further decentralize participation. A higher staking rate not only enhances protocol robustness but also demonstrates our collective commitment to long-term sustainability.

At the same time, the DAO will actively monitor for potential market abuse, including risks of futures arbitrage, to ensure that this adjustment maintains fairness and integrity across the ecosystem. By balancing increased rewards with vigilant oversight, we reinforce the trust and transparency that define the Onyx community.

Approving this proposal means embracing stronger network security, more attractive staking opportunities, and a governance process that adapts thoughtfully to evolving market dynamics. It is a declaration that our community is ready to secure Onyx’s future with confidence, resilience, and shared prosperity.

Your vote is not just about yields—it is about affirming Onyx’s values of decentralized stewardship and adaptive governance. Together, we can ensure that growth is both sustainable and community-driven.

Vote Options:

• For — Increase the XCN

