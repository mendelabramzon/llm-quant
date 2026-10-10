# Labeling packets — batch 21 (124 proposals). Label each against criteria.md.

====================================================================================================
[0] id=0xe6fef4aa9c8e9d162f694ab764b11c06918b9f199aafe43e0d85b12d8271011c  token=STG  space=stgdao.eth  date=2022-09-13
TITLE: SIP #16 - New Assets - DAI, FRAX, sUSD, LUSD
CHOICES: Add all 4 assets | Add DAI | Add FRAX | Add sUSD | Add LUSD | Do not add any
TEXT (first 1500 characters):
**[YOU CAN CHOOSE MORE THAN ONE OPTION ON THIS PROPOSAL]**

This proposal suggests Stargate should provide users a range of options for stablecoin bridging and greater asset diversity to bridge across the main different L1s and L2s. Fiat-collateralized / centralized stablecoins and algorithmic stablecoins present different use cases and have different risk characteristics. To provide greater diversification, FRAX, LUSD, sUSD, and DAI, should be added as new independent base assets to the Stargate Protocol, facilitating cross-chain transfers over Stargate.

The smart contract design and development required to support FRAX, LUSD, sUSD, and DAI transfers on Stargate should follow the below specifications:

- Initially, the following chains should be supported:
    - FRAX: Ethereum, Avalanche, Arbitrum and Optimism
    - LUSD: Ethereum and Optimism
    - sUSD: Ethereum and Optimism
    - DAI: Ethereum, Polygon and Optimism
- Only the liquidity pools on these chains will be connected to each other. More specifically, Stargate should not support cross-token transfers (i.e. FRAX <> USDC, sUSD <> USDT, etc) without further approval via governance.
- Emissions should be enabled and provided to incentive approximately $5M of TVL per asset should be targeted. Emissions should be set for two months then follow in line with current schedules for other stablepools.

Post launch, a range of transfer functionality to & from additional blockchains should be approved for new assets as demand

====================================================================================================
[1] id=0x9fd0e509ac0a27260328e49e4fe4cae5326b7e91c79699b4f306dfc3867749aa  token=STG  space=stgdao.eth  date=2022-11-11
TITLE: SIP#18 Staking Reward Distribution Plan
CHOICES: yes | no | abstain
TEXT (first 1500 characters):
**Background:**


In June 2022, STG holders determined that transaction fees should be accrued to STG holders who stake their STG. To further implement this governance decision, governance should establish: (i) a methodology to determine the timing of fee accrual, (ii) a methodology for calculating fee accruals for each chain-address, and (iii) a fee claim process.   
For details regarding fee apportioning, see the previous [proposal](https://snapshot.org/#/stgdao.eth/proposal/0x69c00cffab20a897469c4bdb04524dc6b31a167b3c0b11e5bea1269ae4ce9043).


(i) & (ii) Timing & Calculation Methodology of Fee Accrual:
veFee Calculation Constants
- feeStartDate (UNIX) = 1654947275
    - Timestamp of the initial veSTG [fee proposal approval](https://snapshot.org/#/stgdao.eth/proposal/0x69c00cffab20a897469c4bdb04524dc6b31a167b3c0b11e5bea1269ae4ce9043) on snapshot.
- veFee Interval (in seconds) = 3600
    - One hour
- Monthly UTC start & stop timetamps
    - Month start on first day of the month at UTC 00:00:00
    - Month stop on last day of the month at UTC 23:59:59

veFee Calculation Methodology

1. At each interval within the month, calculate veSTG balances for each address.
2. Over each hourly interval, calculate the fees accrued for veSTG stakers.
3. With this data you should have the following for each hourly interval:
    1. Individual veSTG balances at end of interval
    2. Total veSTG balance at end of interval
    3. veSTG fees accrued during interval
4. Calculate individual veSTG

====================================================================================================
[2] id=0x714977397be501e7f854293401370ab89d8c9261f533d7bb551d0c29ade5755f  token=STG  space=stgdao.eth  date=2022-11-25
TITLE: SIP#20 Continued Balance and Rebalancing
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
**Background:**

As mentioned in SIP#19 Stargate functions optimally when all pools and paths are balanced. A state of balance is when there is the ideal state of stables on each side of a path.

Stargate has historically relied on the protocol charging fees when a path is out of balance and rewarding users for restoring that balance. The most recent update to this methodology was in SIP#10 (https://snapshot.org/#/stgdao.eth/proposal/0x9cefef89f475daaf6bc9c83244209c9d82d62ecbf16175a4a3ae5a1d3e1ff56a). The methodology should be updated to allow the protocol to more effectively maintain balance.

By better maintaining balance, Stargate will need less liquidity deposited to function, and in the future less emissions will be needed to support liquidity as a result.

**Proposal:**

The protocol should change the conditions to receive eqReward from a minimum of 75% deficit in a pool to instead a minimum of 6 bps received in eqReward for a transfer. When this state is achieved, the protocol will instead lower all protocol fees to two (2) basis points. This cheaper flat fee will better incentivize partners to capture eqRewards and maintain balance within Stargate.

Stargate should also cap eqFee that accrues to eqReward at 50 basis points. Any eqFee that exceeds 50 basis points should accrue to protocol owned liquidity.

A public API will also be developed for anyone to identify rebalancing opportunities to help keep the protocol healthy while capturing rewards for doing so.

Path we

====================================================================================================
[3] id=0xdd13d9ecee26193e58fa8bdf00b0f84b6e715701aff5501fe753447f51c7fa2a  token=STG  space=stgdao.eth  date=2022-11-25
TITLE: SIP#21 Improved Depeg Protection
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
**Background**

In SIP#12 (https://snapshot.org/#/stgdao.eth/proposal/0xe366d625a736b8f66e5c3fa640c538d37ff503d019460e9267d6c3a54fe09f98) a depeg protection module was introduced. This module sets parameters for depeg where if the stablecoin value is $0.9800 or lower for 30 continuous minutes OR if the stablecoin value reaches $0.9500 it is considered depegged and transfers are stopped.

However, further protocol protection enhancements and guardrails are required to mitigate the risk of pool imbalances within Stargate Protocol arising from depeg scenarios. More specifically, under the current system, in the event of a slight stablecoin depeg (e.g., a depeg of greater than 10 basis points), Stargate Protocol can be arbitraged in a manner that creates greater pool imbalances, which in turn requires greater rebalancing effort (as demonstrated in SIP#19) (https://snapshot.org/#/stgdao.eth/proposal/0xa040cd10e6b648014373e84569218937f986ca1ab11210ceb39e65c88cd005a3). 

**Solution**

Stargate should implement a new depeg protection module. This module will rely on the Chainlink Oracle on BNB Chain to provide a verified price for every coin within Stargate that is connected to a different asset. There would be three unique states within this module:

- Normal State: The price is within 10 bps of peg ($0.999)
- Drift State: The price is between $0.999 and $0.985
- Depeg: The price is below $0.985

When the module is in the Normal State the protocol functions normally. When the module

====================================================================================================
[4] id=0x7839f919ddd2c226ef0f050ce9250b0f1f41c1d94bf0ab8fdc9205b151fe3a2a  token=STG  space=stgdao.eth  date=2022-11-27
TITLE: SIP#23 - Data Driven Emissions Modifications
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
**Background**

Stargate currently incentivizes a number of pools (USDC, USDT, ETH, DAI, SUSD, FRAX and LUSD), targeting a general TVL (total value locked) for each pool. Currently Stargate’s TVL in some pools is higher than needed to support current and projected transfer volumes and/or the protocol is emitting more emissions than needed resulting in APRs that are higher than the minimum required to incentivize the required TVL in those pools. By aligning emissions with pool utilization, the protocol can target an optimal TVL for each pool. This will allow for more efficient emissions to truly support protocol volumes with a goal towards overall reduction of emissions.

**Proposal**

Stargate should align emissions with pool utilization. This would allow the protocol to target an optimal and healthy TVL for each pool to facilitate the transfer of value and provide efficient liquidity. An overall emission reduction would also be targeted as protocol owned liquidity and protocol efficiency continues to improve.

**Success**

A successful implementation will ensure there is enough liquidity in each pool to support historical transfer volume. In tandem a community driven goal would be implemented to reduce overall emissions to continually aim for a state where protocol revenue is higher than emissions.

**Execution**

The protocol will periodically adjust emissions based on historical transfer volumes and calculated liquidity required to support them. The protocol will then eith

====================================================================================================
[5] id=0x00b8f2f79d105b9c2da9a346a24ff7c9f1295d4760e11e93709d4e5f0165c2ef  token=STG  space=stgdao.eth  date=2022-12-09
TITLE: Add LayerZero tokens (OFT tokens) to Stargate
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background:

Stargate should become a hub for LayerZero assets (OFT tokens). Stargate should enable OFT tokens as an option for users, allowing a wider variety of tokens able to be bridged through Stargate. This will result in users having a singular easy destination to move many tokens cross chain allowing the protocol to also capture more long tail token flow without the need for more STG emissions. 
Proposal
Stargate should add OFT tokens to the UI enabling more tokens to be transferred through Stargate.


Since OFT tokens rely on the LayerZero network for consensus, no new pools are required and no rewards are required to incentivize liquidity. We can see this in production with how the STG token moves through Stargate without the need for pools. 


A two basis point (2 bps) fee should be applied to any transactions as a convenience fee for providing an easy to use UI to move these tokens. This will generate additional revenue for the protocol. The 2 bps would be split proportionally between protocol fees, veSTG fees and partner fees based on the current ratios used within Stargate. 
Success
Success is when the Stargate Protocol is enabled to support more native OFT tokens, enabling it to drive more volume and offer users a singular place to move a larger variety of tokens cross chain while generating more revenue for Stargate. 
Execution
Once the smart contracts are completed and deployed, this will need to be implemented in the back end and into the front end. Lists wil

====================================================================================================
[6] id=0x85648cb05df3d2eb724e2806e00f3bb5b9a5d06440cde4cf241cc5eec4787c41  token=STG  space=stgdao.eth  date=2022-12-13
TITLE: Stargate Deployment On Metis
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
**Background**
Born out of the need for permissionless and open collaboration, Metis Andromeda is an EVM Equivalent Ethereum Layer 2. MetisDAO Foundation is building a hub for the entire Web3 economy in 3 stages: an Ethereum Layer 2 providing top notch scalability; built-in on-chain reputation through the Matrix Reputation Power System, providing countless capabilities previously just available for Web2 and traditional finance; and a Decentralized Autonomous Company (DAC) framework facilitating the transition of Web2 onto Web3, and enabling both blockchain and Web2 companies to build decentralized businesses on-chain. All the functionalities of real-world enterprises and all the security and decentralization of Ethereum.

**Proposal**
Stargate protocol was initially launched on 7 chains. The MetisDAO Foundation proposes for Stargate to launch on Metis now that there is the LayerZero endpoint on Metis mainnet. To start, the Foundation would like to request two pools:

-USDT (connected to Metis, Ethereum, BNB Chain, and Avalanche)
-APD for METIS between Ethereum, BNB Chain, and Metis.

To incentivize this launch and campaign, the MetisDAO Foundation proposes a 4 month grant distributed as:
-$100k worth of METIS per month, 4 month period 
-$40,000 of METIS for liquidity incentives ($13,333 of METIS/month per pool [Metis, Ethereum, BNB Chain]), $60,000 of METIS for inbound transfer volume rebates monthly 
          -Pools on launch: USDT between Metis, Ethereum, BNB Chain, and Av

====================================================================================================
[7] id=0x4218ee725798f5450583c29e20fa231c782b9f6880ef9170229235e9eb0442ef  token=STG  space=stgdao.eth  date=2023-01-21
TITLE: STG OTC Request Discussion
CHOICES: Complete The Transaction | Do Not Complete The Transaction
TEXT (first 1500 characters):
The Stargate Foundation has been approached by an individual representing he works with a family office that is looking to acquire $2,000,000 of STG at market price from the Stargate DAO. As this is the first time this has happened, the issue is being brought forward to the Stargate DAO. 

Should the Stargate DAO complete this transaction, selling $2,000,000 worth of STG (priced as a three day time weighted average price (Twap) of the STG price) for USDC. This USDC would then be used to purchase ETH that is locked into Stargate POL and supports Stargate liquidity on Ethereum. Assuming a target APY of 5%, this would reduce STG emissions by $100,000 per year and strengthen Stargate’s permanent liquidity. 

It is important to surface any proposals like this to the community to allow the Stargate DAO to make the determination around what to do with them and how to address the request.

Please note: although The Stargate Foundation brought this post to the forums, I am a community member posting it to Snapshot to move this issue forwards. I am not part of The Stargate Foundation.

====================================================================================================
[8] id=0x9301f156dd6aa17b2165fb3834e9523413884bc8158af166b0e25e33f990dab2  token=STG  space=stgdao.eth  date=2023-03-10
TITLE: Liquidity Reallocation from POL-LP to POL-Pools
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
By increasing Stargate POL, Stargate improves its functionality and reduces the need for emissions.  With POL growth, emissions or the need for them, is reduced and eventually eliminated as Stargate no longer needs to “rent” liquidity. For every $1 of added POL, the protocol currently reduces the need for $0.07-0.09 worth of STG emissions per year (7-9%). Of course, POL growth allows Stargate to be a reliable source of cross-chain liquidity for everyone.
At this stage, the Stargate LP is not the highest use of liquidity and has a higher effective value if deployed in POL.  Historically, the Stargate LP has earned an organic APR of less than 3-4%. This is significantly lower than the current 7-9% APR paid for rented liquidity within Stargate. Stargate can save significant emissions (Around 3x emissions saved versus a dollar earned from LP) with the LP stables in Stargate. Stargate is now able to save many hundreds of thousands of dollars in emissions on an annual basis when looking at the data available.

At the same time, the need for the DEX liquidity is not as great as it was at inception.  Thus a reallocation of POL from LP to Stargate pool should not materially impact STG trading.  The current on chain volumes are significantly less than centralized exchange (CEX) volumes, with a majority of the liquidity sitting unused on a daily basis. STG trades overwhelmingly more volume on centralized exchanges versus on-chain historically. 

When Stargate launched on Marc

====================================================================================================
[9] id=0xd0e742caae098261a030feaed2f10d1a36646bdf0ac8d4a128bfb241ca87d8f5  token=STG  space=stgdao.eth  date=2023-03-11
TITLE: Proposal To Unwind The Reissue Of STG
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Today, the Stargate Foundation published a twitter thread outlining the history of the Alameda launch auction token repurchase and current updates to the legal situation surrounding it (https://twitter.com/StargateFinance/status/1634318020473659392). 

Based on advisement from The Foundation, Stargate should cease its plans to reissue the STG token. 

Stargate should continue to use the original STG token within the protocol, and the tokens Alameda purchased should remain in the vesting contract where they currently sit at the request of the liquidators as noted in the thread posted. Stargate would undertake a large cost to reissue the token, along with material risk around its outcome. All of this, was to try to help the safety of the tokens in question. This is now being challenged with the liquidators clearly not wanting them moved.

As the legal process plays out, it is hopeful the tokens will be returned to LayerZero Labs and passed onto the Stargate DAO as proposed, but nothing at this time is certain. What Stargate should do is ensure that the protocol is protected. 

A fair number of exchanges have expressed support for the reissuance. The Foundation should work with those exchanges to resume support for the original STG token.

====================================================================================================
[10] id=0xb850477539d006f12feb53c1ef7d1ebc967cb5424a39dd6c6b2da3c57af05695  token=STG  space=stgdao.eth  date=2023-03-24
TITLE: Proposal to Approve Stargate Deployment to BASE, zkSync, Polygon zkEVM and ConsenSys zkEVM
CHOICES: yes | no | abstain
TEXT (first 1500 characters):
**Background**

Coinbase recently announced the launch of their L2, BASE (https://twitter.com/coinbase/status/1628760201254903809). In addition, Polygon zkEVM, ConsenSys zkEVM and zkSync are launching their blockchains at some point in the future. Stargate should launch on all four of these chains if technically feasible to help facilitate liquidity transfer between zkSync and the other eight chains Stargate currently supports.

**Proposal**

Stargate should launch on all of these chains as soon as possible, enabling bridging of stables (USDC and USDT) and ETH. This will allow Stargate to capture day one market share as well as establish itself as the de facto bridge in up-and-coming ecosystems. To support these pools, Stargate should emit STG to allow enough total value locked (TVL) within the pools to reach a level that is commensurate with the transfer volume observed per https://snapshot.org/#/stgdao.eth/proposal/0x7839f919ddd2c226ef0f050ce9250b0f1f41c1d94bf0ab8fdc9205b151fe3a2a.

**Execution**

Stargate will be deployed on BASE, Polygon zkEVM, ConsenSys zkEVM and zkSync shortly after the official mainnet launch of the chain and USDC, USDT and ETH pools should be enabled. STG emissions will be enabled on those pools when launched as well.

**Summary**

Stargate has the opportunity to become the bridging leader on multiple new blockchains that are launching in 2023. By being an early protocol to launch, Stargate can become the de facto third party bridge for  moving value

====================================================================================================
[11] id=0xd78c441994d140edde34131051113479651c593ab83badebc537a347ba86b705  token=STG  space=stgdao.eth  date=2023-04-03
TITLE: Make Velodrome the STG Hub on Optimism
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
Currently Stargate has protocol owned liquidity across each of the original seven chains it deployed on. These are Ethereum, Avalanche, Polygon, Fantom, BNB Chain, Optimism and Arbitrum. Each liquidity pair sits in a DEX, providing liquidity to trade STG and earning fees from trades.

Proposal
Velodrome is the leading DEX on Optimism and the top Ethereum Layer 2 DEX with over $300M TVL. It serves as the the primary liquidity hub for the quickly growing Optimism ecosystem, serving 2x - 3x as many protocols of comparable DEXs.

Velodrome works by directing VELO emissions to liquidity pools based on votes by veVELO (vote-escrow VELO) holders. Protocols can use veVELO or voter incentives (bribes) to attract votes and emissions for their liquidity pairs. In the last voting round, bribers received $3.5 in VELO for every $1 in bribes on average.

On top of the bribe multiplier, Velodrome incentives will match at least 25% of Stargate's bribes per the "Tour de OP" incentive program, if Stargate moves $1.5M of POL (protocol owned liquidity) to Velodrome and bribes STG-USDC pool. Combined, the bribe multiplier and bribe match can yield a 4X+ impact on liquidity incentives for STG-USDC.

The LP will still be used and routed through all aggregators, resulting in the same execution, but an APR higher than what Stargate is getting on the current Uniswap pools will be paid.

If this pair performs well, Stargate will additionally have the option to migrate additional POL to Optimi

====================================================================================================
[12] id=0x9b511ccf8bd097176255da63725877de9f80caeea8a28256ff50dfad10a3820d  token=STG  space=stgdao.eth  date=2023-04-14
TITLE: Create a Secure UniswapV3 Oracle for STG with Arrakis PALM
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
**Summary**
Deploy Arrakis PALM to create a secure Uniwap V3 oracle and get deep, concentrated liquidity on UniV3 STG.

**Introduction to Arrakis Finance and Arrakis PALM**
Arrakis Finance is Web3's trustless market-making infrastructure protocol that enables sophisticated algorithmic strategies on Uniswap V3.

Since launch, Arrakis has achieved:
- Around $1.7b in TVL at its peak (currently around $460m),  across Ethereum, Optimism and Polygon
- More than 25% of Uniswap V3s total TVL
- More than 80 projects have their liquidity managed via Arrakis vaults

**Arrakis PALM** - Protocol Automated Liquidity Management is a novel market making product sitting on top of UniV3.

In essence, PALM helps protocols bootstrap their base asset inventory (ETH, DAI, etc.) as well as attain deep and sustainable liquidity. The major advantages of using PALM include:
- Zero incentive: no LM incentive needed, liquidity bootstrapping is done solely via market making.
- No biased price impact: PALM conducts market making by setting up ranges 
 / limit orders, no swaps involved.
- Trustless: Stargate DAO retains the ownership of the liquidity and can withdraw at all times. PALM only autonomously manages the liquidity but can never remove it.
- Highly customizable: PALM can be adjusted for various asset types and purposes beyond just liquidity bootstrapping.

PALM has been deployed for a growing number (15) of protocols and is performing exactly as designed. To see a thread explaining these metrics

====================================================================================================
[13] id=0xf980d6deed62c3d77dd055963724b9d07ea0f383a2142703e5581c8e751b06ad  token=STG  space=stgdao.eth  date=2023-04-18
TITLE: Make Velodrome the STG Hub on Optimism
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
Currently Stargate has protocol owned liquidity across each of the original seven chains it deployed on. These are Ethereum, Avalanche, Polygon, Fantom, BNB Chain, Optimism and Arbitrum. Each liquidity pair sits in a DEX, providing liquidity to trade STG and earning fees from trades.

Proposal
Velodrome is the leading DEX on Optimism and the top Ethereum Layer 2 DEX with over $300M TVL. It serves as the the primary liquidity hub for the quickly growing Optimism ecosystem, serving 2x - 3x as many protocols of comparable DEXs.

Velodrome works by directing VELO emissions to liquidity pools based on votes by veVELO (vote-escrow VELO) holders. Protocols can use veVELO or voter incentives (bribes) to attract votes and emissions for their liquidity pairs. In the last voting round, bribers received $3.5 in VELO for every $1 in bribes on average.

On top of the bribe multiplier, Velodrome incentives will match at least 25% of Stargate's bribes per the "Tour de OP" incentive program, if Stargate moves $1.5M of POL (protocol owned liquidity) to Velodrome and bribes STG-USDC pool. Combined, the bribe multiplier and bribe match can yield a 4X+ impact on liquidity incentives for STG-USDC.

The LP will still be used and routed through all aggregators, resulting in the same execution, but an APR higher than what Stargate is getting on the current Uniswap pools will be paid.

If this pair performs well, Stargate will additionally have the option to migrate additional POL to Optimi

====================================================================================================
[14] id=0xda01dacad76bf6559fcd16cf947f23dd4ee3459e1d08aa6325b17a573733d039  token=STG  space=stgdao.eth  date=2023-04-25
TITLE: Stargate x Galxe: Optimism Ecosystem Growth Grant
CHOICES: Yes | No
TEXT (first 1500 characters):
Brief intro about Galxe:
Galxe is the leading platform for building Web3 communities. With over 65 million registered Galxe ID users, Galxe has propelled the growth of Optimism, Polygon, Arbitrum, and more than 2100 partners with reward-based loyalty programs.

Protocols can leverage Web3 credentials from Galxe’s credential data network to power marketplace growth, issue Soul Bound Tokens, increase community engagement, boost ecosystem growth, and generate brand awareness as a result.

Galxe is a team of growth experts that has powered the on-chain and off-chain growth of our 2100+ ecosystem partners. An organic community of over 65M+ Galxe ID users and 150K+ DAU make Galxe the go-to platform for growth and retention in Web3. In addition, Galxe has become the one and only discover-to-earn protocol for users with a variety of different ecosystems running growth and retention campaigns daily. At Galxe, we’ve integrated 15 different blockchains with NFT minting functionality that include non-evm chains such as Aptos and Solana. Stargate has a great opportunity to engage both the evm and non-evm users of Galxe to the Stargate ecosystem with the objective in mind of converting those users into long-term loyal users of Stargate. Galxe’s success has put us among the top dapps in the space. According to DappRadar, Galxe has consistently become a top 10 dapp based on unique active wallets over the course of a 30-day period.

Issue Statement:
Growth and marketing in Web3 are difficult

====================================================================================================
[15] id=0x6b703b90d3cd1f82f7c176fc2e566a2bb79e8eb6618a568b52a4f29cb2f8d57b  token=STG  space=stgdao.eth  date=2023-05-06
TITLE: Velodrome Strategy Update
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
Following implementation of Stargate's incentive program on Velodrome, TVL for the STG-USDC pair has grown over $7M and currently offers a 80%+ APR. Stargate has moved its $1.5M POL on Optimism to Velodrome to capture these VELO rewards as proposed. Given the strong initial results, we believe Stargate has the opportunity to make its incentive program more capital-efficient by reducing the weekly cadence of incentives and increasing the time period of the program.

Proposal
Stargate will reduce weekly bribes on Velodrome from $100k to $25K in STG, therefore expanding the length of the program from 4 additional weeks to 16 weeks. It will also move an additional $1M in POL to the pool to farm and lock more of the total emissions.
Extending the program from 4 to 16 weeks will give Stargate additional time to measure results of incentives on Velodrome, including VELO emissions, lock bonuses, and voting rewards.

If the STG-USDC pair on Velodrome continues to performs well, Stargate will additionally have the option to migrate additional POL to Optimism to add to Velodrome and receive additional VELO emissions. Stargate will be able to deploy the VELO rewards as bribes in following epochs and/or lock a portion as veVELO to significantly reduce the need for STG emissions while maintaining a robust liquidity layer on Optimism.

Execution
Stargate will use the remaining $400k in STG incentive program to bribe the STG-USDC pool at a rate of $25K per week for the next 16 wee

====================================================================================================
[16] id=0xe485f7c2bb4f7843d4ce353ae82f19dcf017e70e917bad28f70ff8b231b57deb  token=STG  space=stgdao.eth  date=2023-05-26
TITLE: Fantom Pool Windup
CHOICES: yes | no | abstain
TEXT (first 1500 characters):
**Background**

On May 24th Multichain announced that a “force majeure'' was impacting some parts of its service (Due to a technical error with Commonwealth previews the tweet will be available at the end of this thread). This creates a lack of clarity around what is happening with Multichain and the stability of anyUSDC, Fantom’s primary USDC asset.

At launch, Stargate included anyUSDC within its pools as anyUSDC was considered by the industry to be the “native” assets for Fantom. Currently, there are 11.4 million dollars worth of deposited LP into this pool, Fantom pools are currently effectively isolated from other Stargate pools.

**Proposal**

Stargate should disable the Fantom pools and pathways. 

The technical steps for accomplishing this are:

- Set STG emissions on the Fantom pools to 0
- Disconnect the Fantom pools from every other pool
- Remove and unwind anyUSDC POL via Multichain, Then deposit the POL into the Ethereum USDC pool.
- Whitelist existing LPs to enable redemption of their LP out to any other chain (Throughout the voting process any LP can remove their LP and unwind their anyUSDC balance manually over Multichain, and it’s probably advisable to do so.)

In light of the disclosure by Multichain of a force majeure event risk mitigating measures should be taken. Going forward, Stargate should consider expanding bridging options for bridging options to Fantom users  in other ways, including possibly via Hydra (https://commonwealth.im/stargatetoken/discuss

====================================================================================================
[17] id=0x04df8aafa123cf995b4ef28e0d28c4987ae09a41a4396235bd9c7368b05fdc80  token=STG  space=stgdao.eth  date=2023-05-28
TITLE: Update Stargate EqReward Design
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Stargate eqFees are generated based upon the following math:
  
![download.png](ipfs://bafkreiaesadod2pxj6fdm22dfa5jwubq3yi6ijp2kbdgrz5io26km7af2m)
    
    
In lay terms, when a user transfers funds on a healthy pathway within Stargate, only the core protocol fee is charged (6-10 bps). When a user transfers funds on an already depleted pathway in a way that makes the pathway less balanced, the user is charged an additional fee as described above. This fee is then set aside into a “sidepocket” (a pool of funds separated from all other funds) which can be used to reward users who swap in a direction that balances the protocol.

Based on Stargate’s design it’s not possible to know the full state of all chains at once. This problem led to the creation of the Delta Algorithm (https://www.dropbox.com/s/gf3606jedromp61/Delta-Solving.The.Bridging-Trilemma.pdf). This allows a surface where a user can add liquidity to a pool (reducing the deficit required to capture the eqReward by clearing the deficit) and then clear additional amounts of the deficit and receive a larger reward. As they do this, they can then remove the liquidity therefore bringing the protocol back to a state that is less balanced than ideal, but more balanced than prior to their actions. This was by design initially to make it such that providing liquidity doesn’t reward eqRewards.  However, as Stargate has evolved, this mechanism can now be used adversely, meaning that eqRewards are distributed in a less efficient

====================================================================================================
[18] id=0x5280241b4ccc9b7c5088e657a714d28fa89bd5305a1ff0abf0736438c446ae98  token=STG  space=stgdao.eth  date=2023-06-14
TITLE: Ammendment to SIP#20 - Continued Balance and Rebalancing
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
Per SIP#20, Stargate leverages POL to rebalance pools and ensure the optimal state of Stargate. This achieved the desired results as reflected monthly transparency reporting found here: https://commonwealth.im/stargatetoken/discussions/Foundation.  With aggressive flows of digital assets between layer 2 blockchains such as Arbitrum and Optimism and Ethereum, pool rebalancing remained beneficial and should be scaled.  Due to the 7 day bridge time back, in these scenarios, a larger base of POL is required to maintain the targeted balances. 

Proposal:
The POL capacity for rebalancing should be increased by USD 10m in stablecoins (to a total of USD 15m in stablecoins).  This should result in pool balances to be maintained at greater efficiency and allow additional flow of funds from L2 to L1 via Stargate. It is also expected that this would result in greater fees capture by Stargate and a larger share of balancing rewards toward POL growth.

Execution:
In administering rebalances, Stargate Foundation could employ an additional 10,000,000 in stablecoins. Transparency reports will continue to be produced for the DAO to evaluate the effectiveness of the rebalancing.  The DAO retains the right to cancel or terminate the capacity for rebalancing at all times.

Summary
The POL capacity for rebalancing should be increased by 10m in assets. By having a balanced system the protocol will be able to function with less TVL, warranting a future reduction of emissions and more reve

====================================================================================================
[19] id=0x108a9e597560c4f249cd8be23acd409059fcd17bb2290d69a550ac2232676e7d  token=STG  space=stgdao.eth  date=2023-06-14
TITLE: $ARB Token Allocation
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Issue Statement:
As part of the Arbitrum governance token airdrop, the Arbitrum Foundation reserved 1.13% of the ARB token supply for DAOs building applications on Arbitrum. Stargate was deemed to be eligible for an airdrop and received 1,674,013 $ARB token. As a DAO, STG holders are to determine the utilisation of the ARB airdrop. Discussion has ensued in our Community as to the utilisation of the ARB airdrop, which should culminate in formal discussion on the below proposal.

Based on the criteria set forth by the Arbitrum Foundation, the Stargate DAO should in general use the ARB assets for two objectives: 
1. To effectively distribute and decentralise the governance of Arbitrum by governance process (as was intended with these tokens).
2. To align with the Arbitrum ecosystem more generally and contribute to its success
 
Solution:
The DAO could accomplish these objectives by allocating the ARB tokens toward two key initiatives - partner integrations and liquidity mining. 70% for Liquidity Mining (1,171,083 $ARB) - boosts liquidity on Arbitrum, allowing more users to bridge into the ecosystem. This also reduces emissions of STG. These will be given out per the demand based incentives (https://snapshot.org/#/stgdao.eth/proposal/0x7839f919ddd2c226ef0f050ce9250b0f1f41c1d94bf0ab8fdc9205b151fe3a2a) until depleted. 
30% for Partner Integrations (502,930 $ARB) - encourages and supports builders within Arbitrum. 
 
Success:
Success of this proposal will result in the reduction of

====================================================================================================
[20] id=0xd6bb6427e285ae4e269ebb9f4d0396808d2de356c654c19877402da4e3e8c44a  token=STG  space=stgdao.eth  date=2023-08-10
TITLE: Beefy provides $OP incentives for STG liquidity.
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
Beefy is a multi-chain yield optimizer present on 21 different blockchains (8 of which are shared with Stargate). Currently offering more than 650 vaults that compound rewards generated by almost $250M TVL. Beefy has many strong traits, two of the most outstanding ones are a big focus on security, and great user experience.
Beefy is a recipient of a Grant from the Optimism Governance Fund. One of the purposes of the grant is to showcase Optimism protocols to our multichain user base.

Proposal
This proposal aims to allocate Beefy’s $OP tokens to boost the STG-USDC Velodrome autocompouding vault, with the goal of attracting more $STG liquidity and tokenholders on Optimism. We will introduce the boost along with some marketing and educational pieces, which will aim to increase awareness and understanding of Stargate’ s protocol and $STG token among Beefy users. As a result of the boost, the users will earn more $STG tokens, as the liquidity incentives from Velodrome are swapped into more $STG and redeposited, plus an extra APR in the form of $OP tokens for staking into the boost.

Beefy’s proposal is to allocate 12,500 $OP tokens to be distributed in the STG-USDC Vault. Beefy will also create the educational and marketing pieces about Stargate, and our development team will create and manage the contracts related to the boost. In return, we are asking for Stargate to stake $3M of STG-USDC as protocol-owned liquidity into the autocompounding Beefy vault, (and not into

====================================================================================================
[21] id=0xcfc335d45421a2d3b5f64d5ee19770ab103f539cedc240ba937691093b392bc4  token=STG  space=stgdao.eth  date=2023-08-10
TITLE: Make Aura and Balancer the STG Liquidity Hub on Arbitrum
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
-Background-
Currently, Stargate has protocol-owned liquidity in Arbitrum on a 50/50 STG/USDC.e Balancer Pool, with a TVL of more than $1.5M.The pool facilitates STG swaps and earns trading fees. However, the current pool's yield is not optimized because it only benefits from swap fees.

Stargate already has protocol-owned liquidity on mainnet within Aura Finance in a 50/50 STG/bb-a-USD pool.

-Proposal-
Aura Finance is a meta-governance protocol built on top of Balancer. Aura Finance has topped over $700M in TVL on mainnet and has a massive ecosystem of partners that encompasses everything from major lending markets like Aave, to cross-chain infrastructure providers like Stargate, to top LSD providers like Rocketpool and Swell. In total, Aura has obtained and maintained fruitful relationships with over 40 different protocols within DeFi. Based on its success on mainnet, Aura contributors believe in Balancer’s potential to be a first-choice for protocols considering to either seed or grow liquidity. 

Aura helps to amplify the effectiveness and growth of Balancer in addition to the protocols within the ecosystem. Aura’s voting incentive markets are one of the most diverse in DeFi, with over 20-30 active participants on any given round. Moreover, Aura has maintained a solid track record in the accumulation of governance influence for veBAL, which has helped to keep markets lively.

We propose the POL migration from the 50/50 STG/USDC.e pool to an 50/50 STG/Boosted Aave V3 USD

====================================================================================================
[22] id=0xe8e92474bbd4ad0aa011cf69ad1873a9e30ab9c431f717e9d859a78fdd799a3a  token=STG  space=stgdao.eth  date=2023-08-23
TITLE: Renewed Liquidity Incentivization Mandate
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
--Background--
On May 6, 2022, Stargate DAO voted to leverage its STG holdings to incentivize liquidity. This strategy involves paying out STG to veCRV holders, CVX holders, and Redacted Cartel (https://snapshot.org/#/stgdao.eth/proposal/0x456c84b723da125d1a4e7b53630b280228c5f2139c40f5dbc56fd3ace5b332ef).

On May 23, 2022, Stargate DAO voted to stake its STG/USDC LP on Convex to earn rewards (https://snapshot.org/#/stgdao.eth/proposal/0x48b26abbc97d94910503e65f02dbbc13f60a07265e49c2986405778978a9559d). The rewards are locked to further amplify the rewards earned, producing a compounding effect.

Through this mechanism, Stargate accumulates rewards in the form of CRV and CVX. Ideally, for every $1 of STG paid, Stargate earns greater than $1 in rewards.

Since then, several other proposals have passed that have diversified Stargate’s LP position into Yearn, StakeDAO, Aura Finance, BeethovenX, and most recently Velodrome. Rewards earned from these protocols are being staked and compounded in a similar fashion to Curve/Convex. As a result, Stargate is now accumulating additional assets such as yCRV, SDT, AURA, VELO, etc.

Over one year has passed since the initial governance vote and the DAO should reevaluate the effectiveness of this strategy.

The ultimate goal of liquidity incentivization is to generate additional POL for the DAO. Ideally, for every $1 of liquidity incentivization Stargate should earn greater than $1 in rewards. At the time of incentivization this is often the

====================================================================================================
[23] id=0x3ab405d7d396f0b3bf04b966dd12b06ad5e81d3cf583eda8b890f2d744a98693  token=STG  space=stgdao.eth  date=2023-09-04
TITLE: Lower TheAptosBridge Block Confirmations and Add Fees
CHOICES: yes | no | abstain
TEXT (first 1500 characters):
**Background**

Per a community vote (https://snapshot.org/#/stgdao.eth/proposal/0x73917ac1c09063a4776aea60176817f3aa3ee96b3a54f93ba9e9dddfc1add2ee) Stargate has taken ownership of TheAptosBridge. Stargate now runs the largest bridge to and from Aptos, allowing users to safely and securely bridge assets. Currently TheAptos bridge relies on LayerZero default finality to the chain as defined by LayerZero documentation (https://layerzero.gitbook.io/docs/technical-reference/mainnet/default-config) and a waiting period of approximately three days when bridging from Aptos back to another chain. TheAptosBridge is currently free to use in all directions for users and applications.

**Proposal**

Stargate should lower the block confirmations required to bridge from Aptos to 260 blocks (roughly 1 minute) and add a small fee of 7 basis points when returning from Aptos to other chains.

Other bridges that service Aptos have significantly faster transfer times from Aptos than Stargate. This reduces TheAptosBridge’s competitiveness in market and could lead to lower overall use. Reducing the block confirmations would allow Stargate to better align TheAptosBridge with the market. Protected by PreCrime (https://medium.com/layerzero-official/introducing-pre-crime-49bef4a581d5) this will have no security implications but create a better user experience for end users that use the bridge and applications that build on top of it.

Stargate should add a 7 basis point fee (0.07%) to TheAptosBridge o

====================================================================================================
[24] id=0x2eff53c9e9f0bf19a98345d1d32103ec0ec859d81978eecacb38db16be33b94b  token=STG  space=stgdao.eth  date=2023-09-04
TITLE: Stargate Foundation 12-month Budget Proposal
CHOICES: yes | no | abstain
TEXT (first 1500 characters):
**Issue Statement**

Stargate Finance has grown exponentially in 2023 hitting major protocol milestones, including over $3.4B in monthly transaction volume and over $2M in monthly protocol fees generated.

While Stargate is a decentralized protocol supported by the DAO.  The Stargate Foundation executes certain operations upon the will of the DAO. This support necessitates a budgeting and administration of expenses. With the protocol growing significantly in terms of community, use, partnerships and development, the Foundation should have a budget to support the DAO. The level of support needed has grown such that the Foundation requires dedicated resource allocation, as will be detailed below.

**Proposal**

This proposal is for a 12-month budget (September 2023 - August 2024) based on an estimation of costs required by the Foundation to continue supporting the DAO in the following functional areas:

***Dedicated Support***

* Foundation requires a small team of people dedicated to operating within the Foundation and executing upon the will of the DAO. This includes functions such as, but not limited to, the following;
    - BD and Partnerships - e.g. supporting protocols that build of top of Stargate, liaising with chains that get approved for Stargate deployments
    - Community and Marketing - e.g. coordinating launch announcements to Stargate’s >650,000 person audience, planning/coordinating community calls
    - Strategy and Analytics - e.g. analysing Stargate’s progres

====================================================================================================
[25] id=0xafce718ac2c5b42caa1c4a2f355f37bab804600b8f2a897840606df146db3da0  token=STG  space=stgdao.eth  date=2023-09-28
TITLE: Proposal for Stargate Deployment on Mantle
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
-Background-
Mantle Network is an optimistic Ethereum layer-2 (L2) solution with an EVM-compatible execution environment. Mantle is DAO-governed and employs a modular approach to execution, consensus, settlement, and data availability. Mantle Network Mainnet Alpha was launched on July 17, 2023. Mantle Network has worked with the LayerZero team and endpoints have been deployed. As a next step, we aim to provide users with the ability to bridge assets to and from Mantle Network through Stargate.

-Proposal-

Deploy the following pools and pathways
-ETH: Mantle, Ethereum, Arbitrum, Optimism, Base
-USDC: Mantle, Ethereum, Avalanche, Arbitrum, Optimism, Polygon, Base
-USDT: Mantle, Ethereum, BNB Chain, Avalanche, Arbitrum, Polygon

-User Incentives and Application Support-

To be discussed between the Stargate Foundation and the Mantle Core Contributor Team (authorized by BIP-19) and Mantle Economics Committee (as authorized under MIP-25).

-Pool incentives to be provided by Stargate. STG should be emitted commensurate with SIP #23.
-Liquidity pool support from Mantle Treasury up to 10M USDx and 5K ETH (see recent Economics committee proposal: https://forum.mantle.xyz/t/ec-proposal-treasury-assets-in-support-of-applications/7943)
-Other MNT support is provided to the Stargate Foundation at a 1 MNT to 2 STG ratio according to STG token emissions. The exact calculation method to be discussed between the Mantle Core Contributor Team and Stargate Foundation, settled and reviewed on a

====================================================================================================
[26] id=0x2e079e8ead1d586cb3fd95e60d14e5ffba29ab7ff377a07d91037ee138989e4a  token=STG  space=stgdao.eth  date=2023-11-06
TITLE: Phase out BUSD on Stargate
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background
Feb 2023 / Paxos (BUSD minter) has been ordered by US regulators to stop issuing BUSD. https://www.theverge.com/2023/2/13/23597539/crypto-paxos-order-sec-binance-usd-stablecoin

Paxos has agreed to comply - and since Apr 2023, it has stopped minting BUSD. BUSD can only be redeemed by burning, meaning circulating supply of BUSD will trend towards zero over time. With no growth in sight and reducing utility over time, Stargate should reduce and ultimately close its BUSD pools, and reduce its exposure to zero. Binance has also confirmed to cease BUSD support by Feb 2024. Stargate should act on this sooner than later.

Proposal
This proposal is to
-Shut down BNB BUSD pool and associated pathways
-Swap all BUSD multisig holdings into another highly liquid, USD-pegged stablecoin

Execution
This proposal can be implemented immediately with minimal technical resources. 

Upon proposal passing
-Set BNB Chain BUSD pool into withdrawal only mode on Stargate UI
-Notify community of intent to wind down pool and encourage LP withdrawal before Oct 30th
-Stargate Protocol Funds (held in Multisig): Swap all BUSD on BNB Chain into another highly liquid USD-pegged stablecoin
-PancakeSwap LP: Exit current position, swap all BUSD into another highly liquid USD-pegged stablecoin, and re-enter with STG-(USD-pegged stablecoin) pairing.

1 week after passing
-Set BNB Chain BUSD pool emissions, and associated pathway weights, to 0.
-Stargate should withdraw any BUSD POL, and swap for anothe

====================================================================================================
[27] id=0x57dfc29fe901e154f294e9e5fc6f7b26e58e4f9446d2d131168bb4531bd2a448  token=STG  space=stgdao.eth  date=2023-11-07
TITLE: Stargate Deployment On Meter
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
### Background 
Meter.io had been working with Layerzero team to enable Layerzero endpoint from Meter to multiple blockchains.  Today Layerzero is one of the top transaction generating applications on Meter mainnet.  In this proposal we are aiming to deploy Stargate on Meter mainnet to allow on/off major crypto assets from multiple blockchains to Meter and bring more activities to Stargate.

### About Meter.io
Meter is a high performance blockchain built on hybrid PoS/PoW and HotStuff consensus.  It is Ethereum compatible, highly decentralized (currently 337 consensus nodes, scalable to thousands) with unique features like MEV/front running resistant, instant finality and a PoW created flatcoin for payments and transaction fees.  Meter has a unique feature lists that is taylor made for decentralized financial applications:

1. Censorship resistant.  Meter’s highly decentralized consensus ensures the network is highly decentralized and robust.  Transactions will be processed smoothly even the network is under attacks.
2. High throughput and instant finality designed for trading.  Meter is not only capable of processing thousand of transaction per second but also each ensuring each transaction in the blockchain is finalized with no possibility of rollbacks.  
3. Fair transaction ordering.  Each year, blockchain users lost billions of dollars due to MEV and front running attacks when they use Ethereum, L2 and other blockchains.  Meter is the only blockchain that is built from gr

====================================================================================================
[28] id=0xa84cf96d0fca68f5c2e4e603d7faed9eb6f1fe0d54d86552545a035bb09a3736  token=STG  space=stgdao.eth  date=2023-11-28
TITLE: PancakeSwap veCAKE Proposa
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
-Summary-
To boost liquidity, reduce slippage, and increase volumes for STG-TOKEN pairs on PancakeSwap, PancakeSwap is requesting Stargate DAO to lock up the DAO’s existing holdings of ~82,000 CAKE as veCAKE for 4 years. This stash of veCAKE will be used to vote for STG-TOKEN gauges on PancakeSwap every 2 weeks, starting with the STG-USDC (0.25%) gauge on Ethereum PancakeSwap.

-Background-
PancakeSwap is launching a new veCAKE gauge system, similar to Curve’s veCRV and Balancer’s veBAL. Users can lock up CAKE for a maximum of 4 years, and then vote for gauges on PancakeSwap every 2 weeks. 
Based on the amount of vote each gauge receives, the respective liquidity pair (e.g. STG-USDC) will receive a pro-rata amount of CAKE emission. This CAKE emission is used to attract users to deepen liquidity for the specific pair, reducing slippage and encouraging higher trading volumes for that pair.
Stargate DAO currently has ~$5.8M of STG-USDC protocol-owned liquidity (POL) on Ethereum PancakeSwap. The POL has seen extremely effective utilization, with APRs currently at 17% based on CAKE incentives and liquidity provider fees.

By voting for this gauge (and other STG-TOKEN gauges in the future) with veCAKE regularly, the DAO can further deepen their liquidity on this highly effective trading venue. 

-Proposal-
a) Grant amount: PancakeSwap is requesting Stargate DAO to lock up 100% of the DAO’s existing CAKE holdings, of roughly ~82,000 CAKE at the time of posting, as veCAKE for 4 years

====================================================================================================
[29] id=0xa4558ffd23293318e9ab559202265a1bb3e26e9215effe3f3eea59f7c54fa166  token=STG  space=stgdao.eth  date=2023-11-28
TITLE: Yearn's Scale-Up Plan for Velodrome STG-USDC.e Incentives
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
-Background
Yearn Finance is a leading decentralized finance (DeFi) protocol offering automated yield-generation services to users. We strive to maximize returns by auto-compounding rewards into additional yield-generating opportunities. Our innovative vault factory allows anyone to deploy an auto-compounding vault specific to any Velodrome V2 liquidity pool. In the recent past, Yearn has been an active participant in the Optimism ecosystem, providing OP incentives to selected vaults.

-Proposal
To scale up and drive further activity in the Velodrome STG-USDC.e pool, the following plan is proposed: Stargate commits to depositing a minimum of $3M of protocol-owned liquidity (POL). For every $1M of total value locked (TVL) in the pool, Yearn commits to providing 500 OP tokens weekly. This incentive plan will be active for 26 weeks.

-Vault address: https://yearn.fi/vaults/10/0xf6B272134A193Df5b04332e73184E5b40b8EB810

-Execution
Once this proposal is approved, for every $1M of TVL in the Velodrome STG-USDC.e pool, Yearn will provide 500 OP tokens. OP boost will be calculated at the beginning of each week. Concurrently, Stargate will ensure that a minimum of $3M of their STG-USDC protocol-owned liquidity is deposited into the Yearn vault on Optimism. Yearn will also ensure the total yield (compounding + yvOP emission) is at least 15% superior to staking in the velodrome pool only, so long as Stargate keeps voting for that pool.

====================================================================================================
[30] id=0xf095ab5713a1a5052f264f6acda54690e921a276d8242c695c2394e9fe77ed85  token=STG  space=stgdao.eth  date=2024-01-17
TITLE: Stargate Partner with Toupee Tech on Base
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Toupee Tech Summary
An entirely new protocol on Base built with features from Solidly. Toupee is a coordinator of incentives within ecosystems built on the Solidly model. Protocols that stake LP tokens in Toupee earn extra rewards in oWIG emissions on top of the rewards earned from the underlying protocol.

No long-term token locking. Toupee operates with a 1-week epoch system, which is also the max token lock duration. Gone are the days of multi-year token locks.

4:1 bribing efficiency. Currently our partner protocols are getting $4 for every $1 they put in bribes, the best in the Base ecosystem. Toupee is also matching bribes for all new partner protocols dollar for dollar.

Liquidation-free loans borrowed against your voting position. Our native token WIG was launched on a bonding curve with a floor price of 1 ETH. Users have the ability to borrow ETH back against their vWIG (staked WIG). This means they have no risk of liquidation and can enjoy the benefits of a totally liquid position while earning profit on protocol fees and bribes.

The effectiveness of the voting flywheel is highlighted by Toupee’s quickly growing TVL which has reached almost $1.5M as of the time of this writing.

Proposal: We will airdrop you voting power to be used in our flywheel, and plug in Stargate pools which can receive bribes and emissions. For pools that you may want to incentivize, our bribing efficiency is currently 4:1 for every dollar put in.

Motivation

Protocols incentivizing on Toup

====================================================================================================
[31] id=0xac174c9bb4f7591f4ace0e8a084e28df7a0c4f9654274c08610f7ec262eed9e3  token=STG  space=stgdao.eth  date=2024-01-18
TITLE: Utilize unclaimed tokens on Velodrome to increase Stargate's weekly earnings and qualify for govNFT
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background

Stargate is in a unique position to extend its initial program on Velodrome at zero cost to the protocol by redeploying unclaimed liquidity rewards and veVELO voting rewards.
Deploying these rewards strategically can allow Stargate to generate up to ~$15K in profit per week, as well as receive a on-time Velodrome partner bonus of 10K OP tokens (~$40K at current valuation) vested over 1 year. Details below.

Proposal

Velodrome is the central trading and liquidity marketplace on Optimism. Velodrome distributes VELO emissions to liquidity pools weekly based on votes by veVELO (vote-escrow VELO) holders. Protocols can use veVELO vote power or voter incentives (bribes) to attract votes and emissions for their liquidity pairs.
Currently, protocols direct an average of $2-$3 in VELO emissions for every $1 of voter incentives, equivalent to a 1.1X-2.5X multiplier. Stargate is uniquely positioned to benefit from this incentive multiplier, as the protocol can capture a large share of VELO emissions through POL and rewards through veVELO votes.
Stargate has accumulated ~1.5M VELO in LP rewards and ~$60K in veVELO rewards (mainly STG, USDC, and OP) from its veVELO position, which Stargate can deploy to boost STG liquidity while continuing to accrue rewards at no additional cost, as follows:
Lock the VELO rewards to increase its Protocol Owned Votepower position to ~9M veVELO
Deposit the veVELO into Relay (Velodrome's automated voting system)
Deploy $6K in weekly incentives f

====================================================================================================
[32] id=0x80aea4dbb7406fa7a25858d241f708d39064404c2d5d65d50602b30dc01c2a15  token=STG  space=stgdao.eth  date=2024-02-17
TITLE: Grow POL on Optimism by leveraging Stargate's veVELO vote power on Velodrome
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background

This proposal aims to maximize the economic upside of Stargate's Protocol Owned Liquidity on Optimism leveraging Stargate’s veVELO position.
Deploying these assets strategically can allow Stargate to increase the yield on its POL, earn a one-time Velodrome partner bonus of 10K OP tokens (~$30K at current valuation) vested over 1 year, and grow its treasury on Optimism. Details below.

Proposal

Velodrome is the central trading and liquidity marketplace on Optimism. Velodrome distributes VELO emissions to liquidity pools weekly based on votes by veVELO (vote-escrow VELO) holders. Protocols can use veVELO vote power or voter incentives (bribes) to attract votes and emissions for their liquidity pairs. 
Voter incentives consistently attract $1.75 to $3 in VELO rewards to pools for every $1 deposited, offering a multiplier effect for protocols. Stargate is uniquely positioned to benefit from this multiplier, as it owns 80-90% of the STG-USDC liquidity on Velodrome, allowing it to capture 80-90% of the resulting VELO rewards. For every $1 in incentives, Stargate could capture $1.4 - $2.5 in rewards each week.
Stargate can also leverage Relay, Velodrome’s veVELO automation layer, to vote for STG-USDC perpetually, compound veVELO rewards, and direct VELO emissions to Stargate’s POL at zero cost to Stargate.
Stargate currently holds approximately 8M in veVELO, 1.6M VELO in LP rewards, and $5M in POL for STG/USDC on Velodrome pools, of which $3.2M is auto-compounding throu

====================================================================================================
[33] id=0x44b9630efed11ff179b69646989d1ef61f05a143164773021844b6aa06878c2a  token=STG  space=stgdao.eth  date=2024-03-19
TITLE: Use idle STG/USDC PoL on Fantom to Earn at Equalizer
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Summary:
Stargate DAO should Stake their currently idle STG/USDC PoL on Fantom into the Equalizer Gauge

By doing this, Stargate DAO starts earning EQUAL rewards for it.

No new Capital is required from treasury for this process.

Entirely self-funded via natural STG Trading Volume

Background:
The proposal highlights a strategic alignment with the upcoming Fantom Sonic Mainnet launch, suggesting that this move could enhance Stargate’s Protocol-owned Liquidity’s earning potential for Stargate DAO in anticipation of increased activity and the new Fantom chain’s increase in prominence.

Stargates current Protocol-owned Liquidity (PoL) for Fantom worth $2 Million is sitting idle on Spooky Exchange, where it has not been effectively utilized due to the absence of volume-driven incentives, no allocated token emissions, and zero added on-chain visibility.

Equalizer, which operates a system similar to Velodrome et. al. is well established on Fantom chain (running in its 2nd Year on the chain), proposes this strategy to better engage this liquidity for a mutually beneficial collaboration.

Target Platform:
The proposal recommends moving the PoL held on Fantom (Roughly $2M) to Equalizer, a modern, more dynamic and evolving DEX, to leverage the Starate DAO’s liquidity to earn $EQUAL emissions as reward for this LP, thanks to Equalize’s novel volume-driven fees incentivising Liquidity Provision.

Mechanism:
the STG liquidity will aim to capture a share of the weekly $EQUAL emissions by

====================================================================================================
[34] id=0xeb2e6a54d110db0cec12113aae61ac83e2d31fc60e14c8084d86d0cc710631d4  token=STG  space=stgdao.eth  date=2024-04-24
TITLE: Proposal to wind down support for the Fantom Ecosystem
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Background

On May 29th, the StargateDAO decided to wind-down support for the anyUDSC asset in the Fantom ecosystem, following the Force Majeure announced by Multichain. On July 15th, StargateDAO voted to support the new safehaven assets issued by LayerZero in the Fantom ecosystem.

Since July 2023, these assets have been supported within the Stargate protocol, averaging around $7M in incentivised TVL, and about $1-5M in 7-day volume for this pool.

On April 4th 2024, the Fantom Foundation announced that they are issuing a new version of a canonical stablecoin, called USDC.e, bridged from Ethereum.

Proposal

The Stargate Foundation is recommending that StargateDAO deprecates support for the lzUSDC pool on Fantom. This pool is currently not generating enough volume to recoup the costs spent on incentives. Further, the safehaven lzUSDC assets provided by LayerZero are likely to be deprecated in their use across Fantom’s DeFi ecosystem, and hence bridging volume will only decrease.

Additionally, removing this pool from the protocol will free up capital allocated on its pathways, increasing the thickness of other pathways within Stargate V1, reducing fees and increasing liquidity on these USDC pathways. This also means Stargate can handle more volume on these pathways.

The DAO should deprecate this pool ahead of Stargate V2 launch, and can revisit the idea of supporting the Fantom ecosystem once there has been meaningful adoption of any new native stablecoin. The asset will co

====================================================================================================
[35] id=0x331603498dd2beb9d9f8ff960a0d7d8fb902783b9ae15a6012086451e49acfb1  token=STG  space=stgdao.eth  date=2024-05-25
TITLE: Distribution of RFP
CHOICES: For | Against
TEXT (first 1500 characters):
Background:

This snapshot delineates the strategic framework for the imminent RFP within the Stargate DAO, a privileged recipient from the LayerZero foundation. After extensive review of the discussion revolving around this topic, a few proposals have emerged as contenders for consideration by the DAO.

There are 4 main factors that have been discussed: governance participation, LP, bridging, and partner protocols. All of these are accounted for within this proposals, and now the DAO should vote on if they deem it appropriate

The following are divided between the 90% left of RFP allocation after dev’s 10% cut.

Proposal

-38.5% to Bridgers, 5k minimum total volume, capped max 750k, linear

Reason: Exclusive users of the Stargate bridge, provides revenue for the protocol. Very important key players within the Stargate ecosystem. Should be allocated for their loyalty + promotion of our product.

-36.25% to veSTG voters contingent upon weight of all votes, ANY AMOUNT OF veSTG IS ELIGIBLE AS LONG AS IT REACHES CUMULATIVE MINIMUM OF 100 veSTG VOTE WEIGHT; EVEN IF YOU VOTE 10 veSTG 10 TIMES AS LONG AS IT REACHES 100 veSTG MINIMUM TOTAL (can vote with less than 100 veSTG, as long as it collectively makes up for 100 veSTG or more then you are eligible, see example), max 2m veSTG (CUMULATIVE; For example if you voted 4 times with 25 veSTG you are eligible/if you voted 5 times with 20 veSTG, or any other figure to cumulatively make up 100 veSTG in weight), linear

Reason: The decisio

====================================================================================================
[36] id=0xa5e2771ea596a620e68726563a79ddc5be80ba5de2d74007fd671e724a1b40a2  token=STG  space=stgdao.eth  date=2024-07-23
TITLE: Integrate with Sei Network
CHOICES: For | Against
TEXT (first 1500 characters):
Background
This governance proposal outlines the integration of Sei Network, a Layer 1 blockchain, with Stargate, a cross-chain and interconnectivity protocol powered by Layer Zero. Sei is a general purpose, open-source Layer 1 blockchain that aims to provide a unique scaling solution to grow the Ethereum Ecosystem alongside other ETH Layer 2 solutions. Sei launched V1 mainnet in August 2023 with full Cosmwasm interoperability and consistently performs at 400ms time-to-finality. Currently, Sei is preparing for V2 mainnet in H1, 2024 which will enable EVM compatibility on the blockchain and even faster performance speeds.

The objective of this proposal is to:
1. Improve user bridging experience on/off Sei for both Stargate and Sei users;
2. Enable Sei to be infrastructurally connected to and share liquidity with other LayerZero supported blockchains and;
3. Unlock interchain liquidity for both Stargate and Sei users via a Stargate Deployment on Sei Network

About Sei
Scheduled to be the first highly performant parallelized EVM in production, Sei’s consensus mechanism and client have undergone extensive battle-testing. With ruthless prioritization on speed and performance, Sei currently boasts the fastest time to finality of any decentralized network in the blockchain industry, achieving a speed of 390ms on its current V1 mainnet.

Sei V2 is on target to launch in H1 2024, which will further enhance the speed of Sei via a number of improvements, such as Optimistic Parallelizat

====================================================================================================
[37] id=0x45de70585d306879ea79de956ab5d136acd03b97d458ef03f09d61a05f1bf91f  token=STG  space=stgdao.eth  date=2024-12-07
TITLE: Stargate Deployment on Conflux
CHOICES: Yes | No
TEXT (first 1500 characters):
**Background**:

This governance proposal outlines the integration of Conflux Network’s eSpace with Stargate.

Conflux eSpace is a EVM-compatible chain with hybrid PoW/PoS consensus mechanism, ensuring a fast, secure, and scalable blockchain environment. Conflux operates without congestion, maintains low fees, and prioritizes network security.

The objective of this proposal is to:

1. Improve user bridging experience to and from Conflux eSpace for both Stargate and Conflux users
2. Enable Conflux to be infrastructurally connected to and share liquidity with other supported chains

**About Conflux eSpace:**

Conflux eSpace is an advanced EVM-compatible chain that delivers high performance, security, and affordability for decentralized applications, achieving lower gas fees and higher TPS than Ethereum. Its unique Tree-Graph consensus mechanism enhances scalability and cost-efficiency for developers and users alike.

Committed to bridging Web2 and Web3, Conflux collaborates with major companies, including China Telecom on a Blockchain SIM card, to onboard non-crypto users into Web3. As China’s leading regulatory-compliant public blockchain, Conflux offers strategic advantages for projects entering the Asian market, with partnerships across Shanghai, China Telecom, Little Red Book, McDonald’s China, and Oreo.

Our roadmap prioritizes privacy, scalability, efficiency, and interoperability, further supported by our new grant program focused on DeFi projects. With Layer 1 superior

====================================================================================================
[38] id=0x33fd697cab0db88aed884765acc848fc60d60349647f1cd078145f94c5ea42d0  token=STG  space=stgdao.eth  date=2025-01-29
TITLE: [Fast Track] HEP-1: Hydra Expansion Program
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal outlines an expansion initiative for Hydra. It is proposed for the DAO to allocate up to $10m in STG tokens to support key initiatives on Hydra chains. This allocation should last 12 months and any funds not used should rollover into the following year.

If approved, Berachain (Boyco) will be the first recipient of funds under this program.

Note: This proposal is intended to go through the fast-track process established in this proposal due to its time sensitive nature.

Context

Hydra extends Stargate via Bridging as a Service (BaaS). With Hydra, Stargate makes bridging USDC, USDT, WETH to non-native asset chains possible, enabling users to transfer Hydra-wrapped versions of USDC, USDT, and WETH to Hydra chains (and between Hydra chains).

The intention is for Stargate to enable chains to build day 1 USDC, WETH and USDT liquidity. In the event that Circle, or Tether respectively, wish to assume ownership over the stablecoin assets, Stargate’s Hydra has been built with the ability to hand over those contracts.

Importantly, whilst Hydra presents a multitude of benefits to chains and users, it also provides a unique opportunity for Stargate to reduce incentives by an order of magnitude. Once capital is locked in Stargate’s pools and Hydra assets are minted on the destination chain, the Stargate protocol now has protocol locked liquidity (PLL) and no longer needs to directly incentivise pools, which is a big unlock for the DAO.

Budget

Given the promise of Hydra

====================================================================================================
[39] id=0xc2d3ee54e28bedacdc23f39fa47f9ed61369a0b512d99fbac8fd0c3556f4b01a  token=STG  space=stgdao.eth  date=2025-02-06
TITLE: StargateDAO Treasury Consolidation Proposal
CHOICES: Approve | Don't Approve
TEXT (first 1500 characters):
–Background–

On Aug 26 2023, the Stargate DAO passed the renewed liquidity incentives mandate proposal, aiming to both reconsolidate non ETH, USDT and USDC assets as well as STG LP positions on various DEXs into ETH, USDT and USDC and deposit them in Stargate V2 pools. The Stargate DAO treasury also has an estimated $3.2m in ETH, USDT and USDC sitting idle in wallets across Stargate supported chains that the DAO could deploy into Stargate V2 pools.

–Purpose–

The purpose of this proposal is for the DAO to consolidate existing positions it holds. If this proposal is approved, this consolidated capital could be used in future to deploy onto HydraChains. The benefit here is that on top of earning on the LP positions, the capital creates Protocol Locked Liquidity, which is a two-fold benefit for the DAO.

–Proposal–

This proposal is made of four parts, as is outlined below.

Part 1:

The first aspect of the proposal as mentioned above is for the DAO to consolidate non ETH, USDT and USDC positions. These tokens will either be consolidated into ETH as per the liquidity incentives mandate proposal or redistributed as incentives for chains Stargate supports.

Chain	Asset	Amount
Ethereum	CRV	~$110k
Ethereum	FRAX	~$992k
Ethereum	BAL	~$96k
Ethereum	AURA	~$205k
Ethereum	METIS	~$15k
Fantom / Sonic	FTM / S	~$58k
Total value	~$1.48m	
Figure 1.

The table in figure 1 includes non USDT and USDC assets, which can be swapped for ETH, to be deposited into Stargate pools and increase POL, in t

====================================================================================================
[40] id=0x0b0b40c3617bf0849c85cfd5902a992e6c9029f551362c068b0aaa1fc2c3d744  token=STG  space=stgdao.eth  date=2025-02-16
TITLE: [Fast Track] Deploy USDC.e/HONEY Liquidity on BeraSwap
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Overview

This proposal outlines a recommendation for the DAO to allocate $5m USDC of Protocol Owned Liquidity (POL) into the USDC/HONEY LP on BeraSwap. The intention of this proposal is to further grow the DAOs Protocol Locked Liquidity (PLL), as Berachain is a HydraChain, whilst also enabling the DAO to earn yield in a reasonable way.

If the USDC/HONEY LP is deployed on Berachain, the capital is locked within Stargate’s pools and minted on Berachain. Doing so enables the DAO to earn yield on that locked liquidity and also accumulate BGT which can be of strategic importance to the DAO given the success of Bera.

BGT is the Berachain Governance Token primarily used for governance purposes like Proof of Liquidity (PoL) asset whitelisting and native dApp governance (BeraSwap, HoneySwap and etc.). By accumulating BGT, the DAO can select validators to “boost” and increase the validator’s reward emission. The incentives earned by the validator will then be returned to BGT holders such as the DAO. On top of this, holding BGT will allow the DAO to receive a share of Berachain core dApp fees as well. You can read more about $BGT here.

If the DAO in future decides to deploy STG liquidity onto Berachain, this BGT will play an important role in the success of that position. A future proposal should determine whether or not to deploy a liquidity pair on a selected DEX on Berachain.

Proposal

The DAO has expressed the strategic value and importance attached to growing the protocols PLL

====================================================================================================
[41] id=0x789acf4aadee717659030af1b286ffa15c26b0befc043f5f5ba169904f6a4de9  token=STG  space=stgdao.eth  date=2025-04-10
TITLE: Deploy STG liquidity on Kodiak Finance on Berachain mainnet & Make Kodiak the STG hub on Berachain
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Background:

Kodiak and Stargate have been in detailed discussions to strengthen our partnership and grow STG liquidity and volumes on Berachain, making Kodiak the STG hub on Berachain. Stargate DAO has demonstrated its commitment to the Berachain ecosystem by providing incentives to Boyco via HEP-1([[Fast Track] HEP-1: Hydra Expansion Program](https://stargate.discourse.group/t/fast-track-hep-1-hydra-expansion-program/201)) and the Stargate DAO has signalled interest to deploy capital on Berachain mainnet (https://snapshot.box/#/s:stgdao.eth/proposal/0x0b0b40c3617bf0849c85cfd5902a992e6c9029f551362c068b0aaa1fc2c3d744). This proposal seeks to deepen Stargate DAO’s commitment and presence to Berachain by establishing significant liquidity on Kodiak Finance.

Proposal:

Kodiak is the native liquidity platform for Berachain and serves as the leading decentralized exchange (DEX) by liquidity provider (LP) activity on Berachain, boasting $970m+ in total value locked (TVL) and just under $1b in lifetime trading volume. This deployment aims to position Kodiak as the primary STG hub on Berachain. Kodiak Finance proposes that Stargate DAO deploy a $5 million liquidity pool, structured as a 40:60 STG/HONEY Kodiak Island. Kodiak Islands are ERC20-wrapped Kodiak V3 positions specifically designed to “always in-range” for Berachain Proof of Liquidity. See docs for details: [Islands | Kodiak Finance](https://documentation.kodiak.finance/protocol/islands)

Stargate aims to have this pool whi

====================================================================================================
[42] id=0xd1dce9972df2b8f0cd40b4747c632d2441060355d6a5f48225a659b0d8d60fcc  token=STG  space=stgdao.eth  date=2025-04-12
TITLE: Fee Distribution Revamp
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**Introduction**

Stargate has accrued a significant amount of POL and will continue to do so. Furthermore, with the emergence of Hydra, there is no need for external liquidity, meaning emissions can be routed elsewhere. With over $130m in POL (at time of writing, 04.03.2025) and Hydra operating as intended, the amount being routed toward this POL accrual should be examined.

**Background**

Since its inception, Stargate has amassed nearly $70m (at time of writing, 04.03.2025) in non-STG tokens through POL accrual. The original intent was to eventually allow for Stargate to operate as a no-emission self-sustaining protocol without the need for external liquidity providers. Hydra’s advancements now render traditional liquidity provisions. Emissions toward said provisions are obsolete and can be routed elsewhere. Therefore, the rate of POL accrual, particularly given the significant capital already amassed, should be reevaluated, given this revenue could be to better benefit Stargate’s market position.

This is not to say POL is unnecessary entirely, and accrual should still occur, but at a different rate. The change in rate should go toward locked stakers instead, resulting in a higher APY, further promoting locks.

In regards to veSTG, initial targets of STG tokens locked have reached over double the expected amount (15m expected vs 36m at time of writing, 04.03.2025). However, the average stake duration is less than one year, which is less than half of the expected amount.

====================================================================================================
[43] id=0x1c43dc820b5999d807b2a69d44fbb0fe98b93827578a4769d8f18b35ee63e805  token=STG  space=stgdao.eth  date=2025-04-21
TITLE: Balanced earnings distribution: Increasing Value Accrual for STG Stakers
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Issue Statement

With the rollout of Stargate v2, the AIPM and Hydra’s demonstration of superior capital efficiency, the need to aggressively accumulate Protocol-Owned Liquidity (POL) at current levels has diminished. The Stargate DAO proposes adjusting the distribution of protocol earnings, increasing the share allocated to veSTG stakeholders to 50% of total earnings while retaining an equal 50% as POL.

The existing Vote-Escrowed Stargate Token (veSTG) mechanism cannot be upgraded. By increasing the distribution of protocol earnings, we aim to incentivize token holders to stake STG and participate in ecosystem governance. This shift aligns incentives with a dual mandate: fostering the protocol’s long-term growth while delivering reasonable returns to Stargate DAO stakeholders.

Allocating 50% of transfer fees and investment income to veSTG holders enhances the value proposition of the STG token for all holders. Simultaneously, retaining 50% as POL ensures sustainable operations and supports the Stargate Foundation, which relies on treasury STG sales to fund ongoing activities.

# Proposed Solution

The updated fee structure for Stargate is as follows:

**veSTG Holders:** 50% of the previous calendar month’s transfer fees and investment income, distributed by the 10th of the current month.
**POL:** 50% of earnings retained as Protocol-Owned Liquidity.

# Clause on Revenue Streams, Investment Returns, and Liquidation Process

All revenue streams, including realised returns

====================================================================================================
[44] id=0x651e4f676f4619107fcbcf97821f6b099500f4f62f2a425d6f4c8c7fbc5ba36d  token=STG  space=stgdao.eth  date=2025-05-08
TITLE: Building Stargate’s Flagship Cross-Chain Retail Superapp – A Glue x Stargate Partnership Proposal
CHOICES: For | Against
TEXT (first 1500 characters):
[please see the non-truncated version of this proposal is at the **[Discussion link](https://tinyurl.com/gluestg)** - Snapshot limits proposals to only 10k letters, so the below stops halfway through]

Stargate Finance has established itself as a leading cross-chain infrastructure protocol, with over $20 billion in lifetime bridge volume to date. The team recently launched Stargate V2, vastly reducing the cost of bridging for users, accelerating chain expansion, and optimizing capital efficiency for the protocol. However, while the STG token has shown some positive movement in response to this new product launch recently, it is evident that relying solely on infrastructure developments is not yet materially shifting long-term value for STG holders. Stargate’s core technology is critical plumbing for omnichain DeFi, but to unlock the next level of growth and token value, a new approach is needed: building a retail-facing application on top of this infrastructure.

We believe that a **retail-facing mobile app** built for Apple and Android devices will help bring new users onto the Stargate protocol. It will provide an easy way to capture the attention of users and highlight the STG token as the critical infrastructure token of crypto - **not dissimilar to how Nvidia is known as the hardware behind most of AI**.

This proposal is the result of extensive feedback gathered from members of the Stargate Foundation team and large ecosystem stakeholders, who recognize the strategic po

====================================================================================================
[45] id=0xb1121f1d909011f8e079d11eaf5b1252c6c86b0c343eb0ec5076598e6e02f2a5  token=STG  space=stgdao.eth  date=2025-07-26
TITLE: [Ratification] Stargate Deployment to Sonic
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal seeks to ratify a previous proposal that just missed quorum. 

The context for this proposal can be found here: https://stargate.discourse.group/t/ratification-governance-proposal/444

The original proposal is here: https://snapshot.box/#/s:stgdao.eth/proposal/0x85cf8edee24777c81f449c311b3f6df0a88aa5ecce31ddf4c429a0bff0a37573

====================================================================================================
[46] id=0xb00c8c8be9a35606a8ef7363fd7d1c8a1b5be91646e2b417e48e0c1384ff44ac  token=STG  space=stgdao.eth  date=2025-07-26
TITLE: [Ratification] Stargate Deployment on Abstract
CHOICES: For | Against
TEXT (first 1500 characters):
This proposal seeks to ratify a previous proposal that just missed quorum. 

The context for this proposal can be found here: https://stargate.discourse.group/t/ratification-governance-proposal/444

The original proposal is here: https://snapshot.box/#/s:stgdao.eth/proposal/0xc8922029030a23ba3dc03db661786012a47a6b9fa9a0e99b5603386a43a1a3a0

====================================================================================================
[47] id=0xcb6cf828878e7286a146543790de8e836320b1f651661855e7fe60f79d8ec328  token=STG  space=stgdao.eth  date=2025-07-28
TITLE: StargateDAO Capital Allocation to Intent Based Systems
CHOICES: For | Against
TEXT (first 1500 characters):
### Introduction

The Stargate protocol has emerged as the most successful bridge in DeFi, processing over $5.5B a month at peak during 2025. Its success is largely attributed to its liquidity pool-based architecture and Hydra, together ensuring efficient and seamless cross-chain asset transfers.

However, the market has also indicated demand for alternative bridge architectures that prioritise speed over decentralisation. These models typically rely on centralised liquidity providers, faster execution mechanisms, and other trade-offs that sacrifice some aspects of decentralisation for faster settlement.

One of the biggest challenges intent-based solutions face is the cost and speed of rebalancing liquidity. Many protocols struggle with efficiently moving liquidity across chains while maintaining competitive costs for users. Some solutions involve paying LPs to rebalance manually, utilising centralised exchanges like Binance, or relying on third-party market makers.

Stargate could hold a unique advantage in this system due to its ability to rebalance liquidity at low cost through Stargate V2 (where fees are simply accrued back to the DAO). This built-in mechanism significantly reduces operational costs of rebalancing, enhancing profitability and making it a competitive solution for cross-chain liquidity movement. By extending its liquidity pool-based architecture with an intents-based system, Stargate can offer both capital-efficient transfer of size and fast, near-instant

====================================================================================================
[48] id=0xf5516dd3c7c19d3182431ebac9af33abffdcba74a3440fdf851a96e58784d25c  token=STG  space=stgdao.eth  date=2025-08-16
TITLE: LayerZero Proposes Acquisition of Stargate (STG)
CHOICES: For | Against
TEXT (first 1500 characters):
3 full years after launching, Stargate is still the most used bridge in the industry today.

**It’s done $70B+ in volume.**

**It’s the home of every major OFT.**

**It has made bootstrapping liquidity to any new chain trivially easy with Hydra.**

*And yet there is still so much more it could do.*

We want to add a huge dose of fuel to the fire that Stargate has been burning – Which is why we are proposing an acquisition of the Stargate token.

**Final Proposal: LayerZero Proposes Acquisition of Stargate (STG)**

Following feedback from the community, the proposal has been updated to include a revenue-sharing period for veSTG holders and an extended voting period. 

The final proposal with updated terms can be found below:
- All circulating STG (including staked/voting STG) is swapped for ZRO at a ratio of 1 STG : 0.08634 ZRO.
- Stargate will become even more deeply ingrained in the LayerZero ecosystem, building a suite of consumer-facing offerings that may expand on its core in many new ways.
- veSTG holders (determined by a snapshot at time of initial proposal) will receive 50% of all top-line Stargate revenue for six months from the date of vote passing. The remaining 50% will be directed towards reducing the circulating supply of ZRO via a buyback program.
- After six months, all future excess revenue generated by Stargate will be directed towards reducing the circulating supply of ZRO via a buyback program.
- The dissolution of the Stargate DAO.

**Governance & Implemen

====================================================================================================
[49] id=0x8ebc109c8bcf1db0f9f53237d510dfada198b5a18f0edb7d0f6b7a0aa0598c5b  token=STRK  space=starknet.eth  date=2025-09-23
TITLE: What features are you missing on SN?
CHOICES: Reduce preconfirmations | Improve L1 finality | Reduce blocktime | Reduce costs by 2x | Add STRK burn mechanism | Add timeboost-like mechanism | Add transaction scheduling servi | Enable stateful validate | Add transient storage | Post-quantum signatures
TEXT (first 1500 characters):
This question is about which technical upgrades or protocol changes would most improve Starknet (SN).
 - Reduce preconfirmations from 500ms to <300ms – Faster transaction confirmations, improving UX for users and dApps.
 - Improve L1 finality from 6 hours to under 3 hours – Shorter time for transactions to be considered irreversible on Ethereum, lowering risk and improving usability.
 - Reduce blocktime from 6 seconds to <2 seconds (on average) – Speeds up transaction inclusion and makes the network feel more responsive.
 - Reduce costs by 2x – Lowers fees, making Starknet more attractive for smaller users and frequent activity.
 - Add STRK burn mechanism – Introduces token burning, potentially creating deflationary pressure on STRK and aligning incentives.
 - Add timeboost-like mechanism – Allows users to pay more for prioritized transaction ordering, useful for arbitrage or time-sensitive trades.
 - Add in-protocol transaction scheduling service – Lets users or apps schedule transactions in advance directly at the protocol level.
 - Enable zkLogin through stateful validate – Further improving user onboarding.
 - Add transient storage – Provides temporary storage in transactions, reducing costs and complexity for developers.
 - Add support for post-quantum signature schemes (e.g., Falcon) – Further future-proofs Starknet security against quantum computing threats.

====================================================================================================
[50] id=0x1f4637b105bed2c36371a22edf637c79825f451261b28368d6c999c81cc89815  token=STRK  space=starknet.eth  date=2026-03-30
TITLE: How do you participate in Starknet's staking mechanism?
CHOICES: Delegate STRK to validator | Run a validator node | Holding STRK, but not staking | I'm considering staking | None of the above
TEXT (first 1500 characters):
Starknet's roadmap is to become increasingly decentralized, with more validators, delegators, and community participants shaping the network. Help us understand where you stand today. Your answer will inform how we support different types of participants going forward.

1. I delegate my STRK to a validator
2. I run a validator node
3. I hold STRK but don't stake/delegate
4. I'm considering staking/delegating soon
5. None of the above (please leave a comment for the reason why)

====================================================================================================
[51] id=QmPwBGy98NARoEcUfuWPgzMdJdiaZub1gVic67DcSs6NZQ  token=SUSHI  space=sushigov.eth  date=2021-01-27
TITLE: SIMP#3 - Vesting
CHOICES: Option 1 | Option 1.1 | Option 2 | Option 1+2
TEXT (first 1500 characters):
Sushi Improvement or Modification to the Protocol SIMP Roadmap and Discussions #3

Sushi Vesting :
Almost three months ago, we’ve agreed[1] 13 to vest ⅔ of newly minted Sushi for 6 months. There was no clear implementation of the vesting and its release, and it ended up being more of a workaround controlled by the multi-sig.

We’re slowly coming closer to the 6-month mark, which means that we start figuring out the distribution and its details.

Option #1: Airdrop the vested Sushi at the 6-month mark and get rid of the vesting. The transaction costs would be subtracted from the total airdrop amount, spreading the costs evenly between the receivers. The total number of vested Sushi at the 6-month mark should be ~47,040,732.

Option #1.1: Airdrop the vested Sushi monthly beginning at the 6-month mark (end of March) and get rid of the vesting. This would increase transaction costs a bit but at the same time would decrease the sudden inflation.

The Sushi would be airdropped beginning with the smallest balances, ending with the highest ones.

Option #2: Similar approach to Balancer’s claims - use a smart contract that would allow claiming every week. This would cost us almost nothing, but the receivers would have to bear much higher gas costs, possibly preventing smaller farmers from claiming their Sushi.

Option #1+2: Airdrop vested balances under 1000 Sushi, get rid of the vesting, use the smart contract approach for bigger balances.

All of these options are broken down in the

====================================================================================================
[52] id=QmXjgif8mZNqkcJcM3gXAiNiTGZEVr5TJTZLKyZDm9kC9q  token=SUSHI  space=sushigov.eth  date=2021-03-09
TITLE: Increase vesting period to one year.
CHOICES: Yes | No
TEXT (first 1500 characters):
Just a proposal to consider increasing the vesting period to one year (:

====================================================================================================
[53] id=QmUrmCsmi2dSZ8ytyDSSHnyUQAqYF33YDPeUbUaYuQReg8  token=SUSHI  space=sushigov.eth  date=2021-03-30
TITLE: sushiHOUSE Treasury Management
CHOICES: sushiHOUSE+DPI 10m$ | sushiHOUSE+DPI 5m$ | sushiHouse 5m$ | DPI 5m$ | Refusal
TEXT (first 1500 characters):
In-depth : https://forum.sushiswapclassic.org/t/sushihouse-a-treasury-management-proposal/3106

Summary :

SushiHOUSE is a fully-customizable treasury management solution built by the Yam Finance team. This proposal would allow the Sushi DAO to migrate part of the sushi treasury into a diversified basket of ETH, BTC, stablecoin and other DeFi allocations as a Bear Market Protection Portfolio. sushiHOUSE will have an active portfolio manager to rebalance portfolio according to risk profiles.

For further divestment in addition to funds allocated to sushiHOUSE a purchase into the Defi Pulse Index (DPI) as a purely buy and hold strategy for the Sushi treasury.

sushiHOUSE Costs
Yam <> Sushi have been mutually supporting each other since their beginnings and we would be happy to support in building sushiHOUSE. We ask in return a 3%+ investment into $YAM token to be hodl’ed inside the sushiHOUSE. Yam Treasury and yamHOUSE currently hodl over $1.5 million in $SUSHI tokens.

Addendum - Purchase $2.5-5m DPI
Summary
Divest the treasury a further $2.5-5m into the Defi Pulse Index (DPI) 1 as a purely buy and hold strategy to diversify the Sushi treasury. This is a separate investment to SushiHOUSE but is being put forward in the same proposal.

Abstract
DPI is a basket of the top DeFi tokens built on Set Protocol V2 contracts. The methodology was designed and is managed by the team at DeFi Pulse aka Pulse inc. Tokens in the index are rebalanced based on relative market cap each month, f

====================================================================================================
[54] id=QmSB39Li1wiNBQuCN2fJkndkoeBomVbp4qY84m56BpDX6Y  token=SUSHI  space=sushigov.eth  date=2021-04-29
TITLE: Add SUSHI incentives on SushiSwap Polygon
CHOICES: Yes | No
TEXT (first 1500 characters):
Summary: To add SUSHI incentives on Polygon to expand SushiSwap's multi-chain mission. 

Introduction: Sushiswap was recently deployed on Polygon as part of the team’s multi-chain vision. Following that, Polygon ecosystem has seen tremendous growth and adoption with Ethereum L1 dapps like AAVE, Curve, mStable, PoolTogether and many more launching there. To better capitalize on this influx of demand, SushiSwap would benefit by launching SUSHI incentives there on certain pairs, in order to build deep liquidity on Polygon and in turn generating more fees for SUSHI holders. Also it would be in favour of Polygon to maybe match/add to the incentives provided by the SushiSwap team. 

Background: The Polygon ecosystem is a suite of Ethereum scaling solutions with Plasma and PoS chain live and running. SushiSwap is also deployed on the PoS chain but volumes and liquidity are minimal due to absence of any incentives (from both parties). Polygon has DEXes but depth of blue-chip pairs suffers, resulting in price slippage on a $100k transaction. SushiSwap, with its brand image and loyal following should capitalise on this gap. For eg. alloc points can be allocated for the top 5 pairs like ETH-wBTC, ETH-USDC, ETH-MATIC, ETH-DAI and wBTC-USDC. In addition to pairs which community proposes .

Motivation: The purpose of this partnership is to expedite SushiSwap’s multi-chain vision and create new opportunities for Liquidity providers to generate revenue. Going this route, I believe shouldn’t

====================================================================================================
[55] id=QmPuCGmPXv1UFqQPk9UF6WhRssHv5qMGKj5HU3wDqbugua  token=SUSHI  space=sushigov.eth  date=2021-05-06
TITLE: Incentives on Polygon & xDai
CHOICES: Incentivize with Treasury | Divert Emission | Negative Chef
TEXT (first 1500 characters):
Followup proposal to https://forum.sushi.com/t/proposal-add-sushi-incentives-on-polygon-market/3984 

Sushi team was able to lock in 15m$ in incentives from the Polygon foundation to bring more liquidity we need to decide how we will match it?

We have 2 solutions

Leverage some of the sleeping treasury (currently over 200m$)

Use the emissions directly by lowering the incentives of some pairs at the core team discretion.

We were also able to secure 1m$ in incentives from xDai which is another network where we are currently deployed fostering more liquidity and users on these various networks are key in establishing Sushi a go-to DEX on various locations with all the revenues accruing to xSushi holders.

Maki Opinion: This is only the first phase of incentives for cross-chain similarly to Bonsai it is WAY harder to bridge emission and for simplicity/fast execution we should just leverage the treasury this time until we have a proper technical solution in place and with the upcoming oSushi changes we will be able to direct theses emissions at will on various LP pairs - products of Sushi.

====================================================================================================
[56] id=QmXTSo2CoFqp8VNqb9Jy8zqgiiKZ9AAPnGwqA3sPaVkBzC  token=SUSHI  space=sushigov.eth  date=2021-08-12
TITLE: Sushi Samurai [GRANT]
CHOICES: Onboard Sushi Samurais | Nay
TEXT (first 1500 characters):
This proposal’s expectation is to release a maintenance grant. Full details and discussions thus far can be found at: 

https://forum.sushi.com/t/sushi-s-all-in-one-customer-support-and-engagement/4435 

With the increased usage of DEX’s, users are in need of support and troubleshooting. This proposal is designed to create a seamless multilingual customer service portal for Sushi users maintained by community members, aka “Sushi Samurai”. The primary goal is to give users the right customer support experience at every stage of their journey on Sushi. The supplementary goal is to educate the users about the platform at a low-level stage in addition to Gitbooks and give them a visual walkthrough of Sushi and partner ecosystems.

As of now, there are 6 dedicated Samurai who have been extremely helpful with thwarting scam attacks, and assisting users with issues revolving around their DeFi experiences. They 
can be found on the right-hand menu of Discord: 
Maka 
rsk
Porlix
n00bie
HHK
Pegbit

Main Focuses:

- Creating a Core Support team “Sushi Samurais”
- Implement a high-level customer knowledge base covering a wide range of topics on the Sushi ecosystem
- Segregate knowledge base and topics to span across three levels - Beginner, Intermediate, and Pro, allowing the customer flexibility on how they wish to engage with the support system
High-level focus on the visual aspect. Provide users with more visual guidance through the use of illustrations and video walkthroughs included

====================================================================================================
[57] id=QmaC15SjeAuAMbUnFp8GP5mk836K68nhsTXWFyWfjh1Rta  token=SUSHI  space=sushigov.eth  date=2021-08-12
TITLE: Shoyu Maintenance [GRANT]
CHOICES: We like the JPGs (Yes) | We don't like the JPGs (No) | Neutral
TEXT (first 1500 characters):
This proposal’s expectation is to release a maintenance grant. Full details and discussions thus far can be found at : 

https://forum.sushi.com/t/shoyu-sushis-nft-platform-dev-management-proposal/4548 

“I, LevX, proposed the idea of our NFT exchange, and thanks to our passionate community members, especially @FutureFund, @ayoki, Evan Keast, Zach Noble, and @OmakaseBar, it evolved into a concrete project that would meet the actual needs of NFT artists & collectors.

Now that contracts are complete, it’s time to develop the frontend, caching layer(subgraph), and infrastructure for artwork storage. Around the end of August, v0 will be released and we have gradual release plans for v1 and v2 for the next few months.

As the product manager & lead developer of Shoyu, I’ll guarantee the release of v0, further (v1 & v2) updates and maintenance in the next 1 year.”

Chef's recommendation: 
LevX is one of Sushi biggest contributor and has my total confidence in building Shoyu as highlighted in the proposal, welcome back!

====================================================================================================
[58] id=QmcwEVRfidkg5U8n3Z9CWgZfb63Fdy9Gy3BPX9z6xZL7nr  token=SUSHI  space=sushigov.eth  date=2021-10-19
TITLE: Community-Enabled Analytics [GRANT]
CHOICES: Fund CEA | Nay
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal on a grant. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/proposal-community-enabled-analytics-for-sushi/5516

Community-Enabled Analytics (CEA) is proposed as a solution to develop a community of nearly 500 individuals that attack analytic challenges in real time for Sushi. The program is designed to drive on-demand data needs - as well as customer acquisition, ecosystem growth and token circulation.

The forum post describes CEO as a free solution with a bounty program to incentivize and reward community members for learning about, analyzing, and publishing blockchain data.

The proposal requests a grant of 1M USD annually in $SUSHI to fund the CEA program for Sushi, which may be renewed on an annual basis.

→ 50% of this will be delivered to ecosystem community members as bounties ($41,667 per month)

→ The other 50% ($41,667 per month) is the subsidization of operational and infrastructure costs.

Year 1 Program Expectations:

Given previous programs, the expected results from a year of bounties would be as follows:

~ A community of 460 educated analysts to produce on-demand insights for Sushi

~ 27,000 $SUSHI retained in ecosystem

~ 350+ unique dashboards, queries, visualizations, & in-depth analyses, plus premium interactive solutions including a Trident concentrated liquidity calculator.

Sushi CEA Program Oversight:

Two components are proposed to provide effective check

====================================================================================================
[59] id=0x8315ab4c4ef39731bbae23c398efc7888732f08bb42e9c33ca7db5bca91764b1  token=SUSHI  space=sushigov.eth  date=2021-11-10
TITLE: Collateralize SUSHI Reactor on Tokemak
CHOICES: Collateralize Tokemak - $3.0M | Collateralize Tokemak - $1.5M | Nay
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal on whether to collateralize a SUSHI reactor on Tokemak with the goal of (i) supporting SUSHI liquidity and (ii) increasing liquidity in SushiSwap pools to increase trading fees for xSushi stakers.

Full details and discussions thus far can be found at: https://forum.sushi.com/t/collateralize-sushi-reactor-on-tokemak/5919

Implementing this proposal would involve a $1.5 or $3.0M Reactor Collateralization and Treasury Swap.

====================================================================================================
[60] id=0xb0a18a4179f8594dff36c5360c9a8f4e83fd36f86efe4a010d7ffa251f0367d1  token=SUSHI  space=sushigov.eth  date=2021-11-30
TITLE: Community-Enabled Analytics [GRANT]
CHOICES: Fund CEA | Don't Fund CEA
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal on a grant. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/updated-proposal-community-enabled-analytics-for-sushi/6127

A previous snapshot vote on this topic can be reviewed at: https://snapshot.org/#/sushigov.eth/proposal/QmcwEVRfidkg5U8n3Z9CWgZfb63Fdy9Gy3BPX9z6xZL7nr

Year 1 Program Expectations:

Given the pilot program data, the expected results from a year of bounties would be as follows:

~ Overhaul of Sushi website analytics page (multi-chain coverage)

~ Analytics on key Sushi product lines

~ 460 new active, engaged community members [acquisition]

~ 27,000 SUSHI retained in ecosystem [retention]

~ 350+ unique dashboards, queries, visualizations, & in-depth analyses, and premium interactive solutions.

Grant Request: $1M Annually

→ 50% of this will be delivered to ecosystem community members as bounties ($41,667 per month)

→ The other 50% ($41,667 per month) is Flipside’s Fee To Operate the Program

Oversight Committee: Purpose is to ensure that the grant proceeds are applied in a manner consistent with its design. The Committee will meet and take a vote annually to evaluate the continuation of the program.

The committee members will be:

- Tangle (Sushi)
- Mudit Gupta (Sushi)
- Pegbit (Sushi)
- Alex Woodard (Arca)
- Sushi Core team member to be named
- Flipside Crypto member to be named

====================================================================================================
[61] id=QmfW6KBcb7wSgKjGzcFSputWz2yjk1PTpgzvFDM7kMQcyu  token=SUSHI  space=sushigov.eth  date=2022-04-19
TITLE: Kanpai Part 1: SushiMaker Treasury Payout Ratio [Implementation]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/kanpai-bear-market-protection-with-treasury-revenue/4310

Synopsis:
Introduce a governance-controlled ‘payout ratio’ parameter (initially set to 95% or 90%). This will divert a portion of trading fees (100% - payout ratio) from xSUSHI stakers to the Treasury as revenue denominated in ETH. For example at a payout ratio of 95%, xSUSHI holders are paid out 95% of the 5bps. Introducing retained earnings will offer valuable bear market protection as well as allow SUSHI holders to govern a new cash flow, which could be used to reinvest in growth or generate non-operating income.

Implementation is short and sweet with just a couple of lines of code added to SushiMakerV2 so that a ‘payout ratio’ can be set and diverted to the treasury. Payout ratio will be adjustable, and can go under further governance votes to increase or decrease the percentage taken for the treasury.

This is a 2 part proposal, with 1st part being the vote on executing the Implementation and 2nd part being the vote on the initial ‘payout ratio’ set.

TL;DR
The Treasury’s current near 100% SUSHI allocation could prove to be risky in the event a prolonged bear market occurs, so the Treasury is in need of expanding its ongoing diversification efforts. By diverting a portion of the fees to the Treasury, this would give Sushi enough revenue every year to cover operational expe

====================================================================================================
[62] id=QmX6ZJtJN3KxjYiFHKDy1CK4vkUVTEeqq5Wy2PwArgj8bH  token=SUSHI  space=sushigov.eth  date=2022-04-19
TITLE: Kanpai Part 2: SushiMaker Treasury Payout Ratio [Implementation]
CHOICES: 90% | 95% | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/kanpai-bear-market-protection-with-treasury-revenue/4310

Synopsis:
Introduce a governance-controlled ‘payout ratio’ parameter (initially set to 95% or 90%). This will divert a portion of trading fees (100% - payout ratio) from xSUSHI stakers to the Treasury as revenue denominated in ETH. For example at a payout ratio of 95%, xSUSHI holders are paid out 95% of the 5bps. Introducing retained earnings will offer valuable bear market protection as well as allow SUSHI holders to govern a new cash flow, which could be used to reinvest in growth or generate non-operating income.

Implementation is short and sweet with just a couple of lines of code added to SushiMakerV2 so that a ‘payout ratio’ can be set and diverted to the treasury. Payout ratio will be adjustable, and can go under further governance votes to increase or decrease the percentage taken for the treasury.

This is a 2 part proposal, with 1st part being the vote on executing the Implementation and 2nd part being the vote on the initial ‘payout ratio’ set.

TL;DR
The Treasury’s current near 100% SUSHI allocation could prove to be risky in the event a prolonged bear market occurs, so the Treasury is in need of expanding its ongoing diversification efforts. By diverting a portion of the fees to the Treasury, this would give Sushi enough revenue every year to cover operational expe

====================================================================================================
[63] id=QmNqLbJf6x5HXSRy3FjcY5McpgGGnFho7GySmGZd8nXeKF  token=SUSHI  space=sushigov.eth  date=2022-04-26
TITLE: Kanpai Part 3: SushiMaker Treasury Payout Ratio [Implementation]
CHOICES: 100% ETH | 50-50 stables + ETH | 100% stables
TEXT (first 1500 characters):
This proposal's expectation is to produce an implementation. Full details and discussions thus far can be found at:
https://forum.sushi.com/t/kanpai-bear-market-protection-with-treasury-revenue/4310

Synopsis:
With successful passing of the Kanpai proposal, part 3 of the proposal will now decide the split between stables and ETH that will be diverted to the Treasury. Three options will be present: full ETH, full stables, and 50-50 ETH + stables.

TLDR:
Decision on the asset(s) that will be directed to the Treasury through Kanpai.

====================================================================================================
[64] id=QmNYBB9fxtygJhDE6kjtUfdvTkY34J37oSDCZqjuzocAAR  token=SUSHI  space=sushigov.eth  date=2022-06-06
TITLE: Gauntlet x Sushi Incentive Optimization [Renewal]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
Description:

This proposal's expectation is to produce an implementation. Full details and discussions can be found at: https://forum.sushi.com/t/gauntlet-x-sushi-incentive-optimization-renewal/10507

Synopsis:
This proposal is to renew Gauntlet’s engagement with Sushi on dynamic incentive optimization to drive efficiency and growth for the upcoming 12-month period.

The new engagement seeks to serve Sushi more holistically. The project scope will be expanded to include optimizing the overall incentive budget and expanding optimization efforts across additional chains beyond Ethereum mainnet. The target metric for the engagement is Protocol Utility, defined as revenue less incentives for pools optimized by Gauntlet. 

Gauntlet will provide the core team with a dashboard for visibility and post quarterly updates to the community.

Pricing for the engagement is a $500k service fee (denominated in $SUSHI) and a variable quarterly performance fee of 3.6% of Protocol Utility (denominated in $USDC or $SUSHI). 

Gauntlet payment address: https://etherscan.io/address/0xD20c9667bf0047F313228F9fE11F8b9F8Dc29bBa

TLDR: 
Renew Gauntlet's engagement with Sushi on incentive optimization for another year.

====================================================================================================
[65] id=QmTv4DARwft9sjaiBKpmqJj81YaBBGM5ejK995KrceJekH  token=SUSHI  space=sushigov.eth  date=2022-06-26
TITLE: KlimaDAO x Sushi Carbon Offset Integration [Signal]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/klimadao-x-sushi-swap-carbon-offset-integration/10678

Synopsis:

KlimaDAO’s goal is to embed the cost of carbon emissions into our economic system through the creation and governance of a carbon-backed currency, aligning incentives between investors, civil society, and organization. 

KlimaDAO also chose Sushi as the primary place for supplying liquidity for these carbon-based credits making Sushi a critical part of the on-chain carbon market. 

Liquidity was the first step in revolutionizing the current Voluntary Carbon Market. Since then, KlimaDAO has launched tooling that allows anyone to offset their carbon emissions, unlocking the ability for any individual or entity to play a part in the future of the carbon market.

Decentralized exchange (DEX) protocols are the most commonly used application in DeFi and amongst the largest consumers of gas on the blockchain. This makes DEXs a critical point of leverage for combatting carbon emissions on the blockchain.

With this, KlimaDAO is proposing the implementation/creation of an opt-in feature where user’s can elect to and automate the offsetting of their swaps directly through Sushi. Initial signal is to explore adding an optional toggle, like the “expert” mode toggle, that simply enables or disable carbon offsetting for swaps. KlimaDAO is offering to put in the research/development r

====================================================================================================
[66] id=QmTZTSq9LguJFcWnoZKqmANWiNBBrJCUEC3vVEQbseR4YN  token=SUSHI  space=sushigov.eth  date=2022-06-26
TITLE: Treasury MultiSig Member Rotation [Signal]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/treasury-multisig-member-rotation/10782

Synopsis:

The Sushi Treasury is backed by a 8 member Gnosis MultiSig. Original members of the multis were determined publicly nominated election / snapshot votes almost 2 years ago. Overtime, as members of the multisig took on other responsibilities some have been less available to sign than in the past. Due to this, this proposal is to signal if Sushi should look into replacing 3-4 members of the multisig with new signers that have the availability to sign transactions in a timely manner.

Member rotation will require an additional Implementation vote with more details on who will be joining the Treasury MultiSig and processes for the Treasury members going forward.

TLDR:

Signal to determine if Sushi should kick off the process of replacing 3-4 members of the Treasury multisig and implementation vote to follow to enact the changes to the multisig.

====================================================================================================
[67] id=QmWEfwveAg713g6GjPPEgzdh3cPPadB1zUGmhDuTtf82jg  token=SUSHI  space=sushigov.eth  date=2022-06-26
TITLE: SushiHouse Funds Redemption Pt1 [Implementation]
CHOICES: Yay (Redeem tokens) | Nay (Keep in SushiHouse) | Abstain
TEXT (first 1500 characters):
This proposal's expectation is to produce an implementation. Full details and discussions can be found at:

https://forum.sushi.com/t/sushihouse-funds-redemption/10783

Synopsis:

SushiHouse is a Set Token that was setup by Yam’s treasury management team to diversify into assets for bear market protection.

Due to the management team to manage these funds not being in place anymore, this proposal is to determine if Sushi Treasury should redeem the funds that currently makeup the SushiHouse tokens back to the Treasury.

This is a 2-part proposal, with part 1 being the implementation vote on the redemption of SushiHouse funds to the treasury. While part 2 will determine if the funds redeemed should be fully sold for stables or not.

Redemption vote is straightforward and just requires the Treasury multisig to breakdown SushiHouse tokens and redeem funds back to the Treasury.

Sell-off of funds will require Treasury to look into whether OTC or on-chain settlements are the better option for selling off assets, and will go with w/e approach results in smaller amount of slippage from the swaps. Likely being that OTC is the better option for selling out of these tokens.

TLDR:

Part1 -> Redeem SushiHouse assets back into the Treasury

====================================================================================================
[68] id=QmeoNQXWU7Uam1SYYLwT7pjnTbtU3qy81PEAcgdeHYkvuq  token=SUSHI  space=sushigov.eth  date=2022-06-26
TITLE: SushiHouse Funds Redemption Pt2 [Implementation]
CHOICES: Yay (Sell into Stables) | Nay (Keep as Is) | Abstain
TEXT (first 1500 characters):
This proposal's expectation is to produce an implementation. Full details and discussions can be found at:

https://forum.sushi.com/t/sushihouse-funds-redemption/10783

Synopsis:

SushiHouse is a Set Token that was setup by Yam’s treasury management team to diversify into assets for bear market protection.

Due to the management team to manage these funds not being in place anymore, this proposal is to determine if Sushi Treasury should redeem the funds that currently makeup the SushiHouse tokens back to the Treasury.

This is a 2-part proposal, with part 1 being the implementation vote on the redemption of SushiHouse funds to the treasury. While part 2 will determine if the funds redeemed should be fully sold for stables or not.

Redemption vote is straightforward and just requires the Treasury multisig to breakdown SushiHouse tokens and redeem funds back to the Treasury.

Sell-off of funds will require Treasury to look into whether OTC or on-chain settlements are the better option for selling off assets, and will go with w/e approach results in smaller amount of slippage from the swaps. Likely being that OTC is the better option for selling out of these tokens.

*Tokens and allocations for each are documented in the forum proposal.

TLDR:

Part2 -> Sell off SushiHouse funds redeemed for stables in the Treasury

====================================================================================================
[69] id=bafkreidu53p4m7usk3ewi3jr7hnxvni3ce7qlwmqhwwgcfaq7jq2o37aie  token=SUSHI  space=sushigov.eth  date=2022-10-28
TITLE: Sushi Treasury Multisig Update [Implementation]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/updated-treasury-multisig-signers/11156

Synopsis:

Over the past 2 years of Sushi, there have been various individuals on the multisig. Currently some of the users on the Multisig have become busy with other projects, or no longer have the bandwidth or interest to contribute.

Due to the need to have active signers for the Sushi Treasury, this proposal will determine if we should move forward on the implementation of rotating out members that no longer wish to be a part of the Multisig with a new cohort to oversee and manage the txs needed for the Sushi Treasury.

The following is the new list of signers to sit on the Sushi Treasury:

**Mable Jian** - Growing @Stepnofficial | Host of HODLong 后浪 podcast | Mentor @ @tangent_xyz | ex-@multicoincap | 
https://twitter.com/Mable_Jiang

**0xSami** - Founder of Redacted Carte. Currently on multisigs for several projects including Butterfly, New Order, Olympus, and Aura, and Esketit.
https://twitter.com/0xSami_

**Nick Rishwain** - Building and launching on-chain real estate protocol, operator in legal technology Web2 space. 
https://twitter.com/nickjrishwain

**ChopChop** - Core contributor @NFTX_, member of @dcv_capital
https://twitter.com/0xChop

**Maki** - Previous Head Chef at Sushi. Contributor at LayerZero, Stargate, and Aura. 
https://twitter.com/0xMaki

**Tom Lombardi** - Adjunct prof

====================================================================================================
[70] id=0xd817c716ff271f5141cfe112e1fd7b652f961b4c965852eb44d8ed1ec3a5d3b5  token=SUSHI  space=sushigov.eth  date=2022-12-12
TITLE: Increase Kanpai Treasury Payout Ratio to 100% [Signal]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:
https://forum.sushi.com/t/reinstated-increase-kanpai-treasury-allocation-to-100/11475

Synopsis:

With the introduction of Kanpai and a Treasury Payout Ratio, this proposal is a modification of the previously set payout ratio from 10% to 100% of the Sushi fees to the Treasury. Payout Ratio to the Treasury will stay in place for one year or until new tokenomics are implemented. Revenue to the treasury will be in the form of 50% ETH and 50% USDC, with projection of ~$6m being earned over the next year if this proposal were to pass.

Kanpai is a temporary solution to a long-term problem, and a new tokenomics proposal is on the horizon, which will help address the long-term value proposition of Sushi for it’s community and stakeholders. 

For governance, things will stay the same with xSUSHI still being used as governance voting, and depreciation of xSUSHI will not take place with the passing of this proposal.

Proposal is in the form of a Signal vote, and an implementation vote will follow using the usual Sushi Governance Process.

TLDR:

100% fee redirect to the Treasury for 1-year

====================================================================================================
[71] id=0xe8be4c19adbd6cdb1f95a0318ed0d037db4904b72e815569076cc9b6ba44d1ec  token=SUSHI  space=sushigov.eth  date=2022-12-19
TITLE: Sushi Vesting Merkle Tree Clawback [Signal]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/sushi-vesting-merkle-tree-clawback-temp-check/10008

Synopsis:

During the first 6 months of Sushi's liquidity mining a vest was put in place for 2/3rds of accrued Sushi rewards to be locked up and released after 6 months. With the full release of all vested SUSHI being October 12th, 2021 and thus being well over a year now since the SUSHI was unlocked this proposal will be used to signal the community's decision on clawing back the SUSHI still remaining in the contracts or to not.

Two merkle trees are in place with a collective amount of 8,246,689 SUSHI remaining in the contracts:

https://etherscan.io/address/0x1026cbed7b7e851426b959bc69dcc1bf5876512d

https://etherscan.io/address/0xcbe6b83e77cdc011cc18f6f0df8444e5783ed982

Clawback will go directly to the Treasury, and there will be a plan put forth to set a precedence for the time table and process for clawing back SUSHI in a Implementation proposal if the Signal proposal passes.

Thus further details of the clawback procedure will be worked out depending on the outcome of this proposal, and this is just a Signal to determine if we should go forward with planning this out for Q1 of next year 2023 or not.

TLDR:

To clawback vested SUSHI to the treasury or not

====================================================================================================
[72] id=0xf0353dcc69b766e96e2d1f65f76be2f13c03c1df7ed5ef483e9352e0da59a821  token=SUSHI  space=sushigov.eth  date=2023-01-16
TITLE: Sushi Vesting Merkle Tree Clawback [Implementation]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/sushi-vesting-merkle-tree-clawback-temp-check/10008

This proposal’s signal vote to advance this to an implementation vote can be found at:

https://snapshot.org/#/sushigov.eth/proposal/0xe8be4c19adbd6cdb1f95a0318ed0d037db4904b72e815569076cc9b6ba44d1ec

Synopsis:

Following the temp check in the forum post above, the proposed deadline duration for claiming remaining Sushi from the claw back will be 3 months.

If the proposal passes, then the start date for the final claim will be according to this snapshot end date - January 23rd 13:00 UTC

That results in a final claim date being set to - April 23rd 13:00 UTC

On this date, the two merkle trees will be frozen and an updated merkle root will be set so that clawed back SUSHI can be claimed directly by the Treasury.

TLDR:

3 month deadline to claim SUSHI w/ April 18th being the final day

Sushi clawed back will go to the Treasury

====================================================================================================
[73] id=0x64c5c6cdb74a1ebafe8e808ba69bd51ff70938b7db791ca8a05b37736541d147  token=SUSHI  space=sushigov.eth  date=2023-01-16
TITLE: Kanpai 2.0 [Implementation]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/t/reinstated-increase-kanpai-treasury-allocation-to-100/11475

Following snapshot is for this proposals signal to advance to this implementation vote: 

https://snapshot.org/#/sushigov.eth/proposal/0xd817c716ff271f5141cfe112e1fd7b652f961b4c965852eb44d8ed1ec3a5d3b5

Synopsis:

With the introduction of Kanpai and a Treasury Payout Ratio, this proposal is a modification of the previously set payout ratio from 10% to 100% of the Sushi fees to the Treasury. Payout Ratio to the Treasury will stay in place for one year or until new tokenomics are implemented. 

Premise of the proposal is roughly the same from the signal vote, but with clear guidelines set in place for the timeline of the enacted proposal. The proposal ensures that the 100% ratio of fees to the Treasury will only be in effect for a maximum of one year from when the signal vote passed on Dec 19th 2022. Thus, this means that a hard-stop will be in place for Dec 19th 2023 and the Kanpai payout ratio will revert back to 10% to Treasury and 100% to Sushi Bar. Also, implementation of new tokenomics will also be a cause for a hard stop on the fee re-direct and migrating to the new structure once it’s passed through governance/development and is ready to integrate.

Additionally, a governance dashboard will be developed to give full transparency & insights into the operations budget and

====================================================================================================
[74] id=0x8b91b6d70d8a31eb61b87f871cd4535a17faa9aa0023f15ac58c77b901a77a82  token=SUSHI  space=sushigov.eth  date=2023-11-15
TITLE: Deploy new tokenomics for Sushi [Signal]
CHOICES: Yay | Nay
TEXT (first 1500 characters):
This proposal expects to produce a community signal. Full details and discussions thus far can be found at: https://forum.sushi.com/t/rfc-deploy-new-tokenomics-for-sushi/12513/1

Synopsis:
Restructuring Sushi’s token model will help cement its role in the protocol’s ongoing success and contribute to its growth. Since its launch, Sushi has been at the forefront of tokenomics with initiatives like MasterChef and xSushi. We aim to present a token model that sets us on a sustainable growth path and long-term strategy. In January, we published an initial draft, which, thankfully, generated meaningful feedback from the Sushi and DeFi community, and we believe this final draft represents the best model curated from that feedback.

As Kanpai expires in December of this year and Sushi’s current distribution model quickly approaches full distribution, our new proposal outlines our vision for a revised Sushi token model crafted to ensure stability and sustained value for all stakeholders. The model builds on three pillars: protocol sustainability, token utility enhancement, and treasury diversification. We invite you to review the proposed changes showcased in our paper, which will synergize to support a resilient token economy.

Below is a brief overview of the new model’s mechanics and goals.

Challenges and Solutions
We’ve identified several challenges through thorough analysis.
Here’s a brief on what we’ve found and our proposed solutions:
We aim to improve rewards efficiency, reduc

====================================================================================================
[75] id=0x0fed35582abb7163a47ae5bc62d6f4185de60667db44adf65454c2d218559a60  token=SUSHI  space=sushigov.eth  date=2024-01-30
TITLE: Send Sushi From Merkel Distributor Contract to the Sushi Treasury Wallet
CHOICES: Yay | Nay
TEXT (first 1500 characters):
Summary:

The Ops team has yet to fulfill the requirements of the "Sushi Vesting Merkle Tree Clawback [Implementation]": https://snapshot.org/#/sushigov.eth/proposal/0xf0353dcc69b766e96e2d1f65f76be2f13c03c1df7ed5ef483e9352e0da59a821\

This snapshot formally requests that the Merkle Distribution Contract Sushi tokens be sent to the Sushi Treasury wallet immediately.

It is unclear as to why there has been a nine month delay in carrying out the will of the previous snapshot. The forum discussion pertaining to this [signal] can be found here: https://forum.sushi.com/t/signal-send-sushi-from-merkel-distributor-contract-to-sushi-treasury/12729

Implementation:
Upon a successful 'yay' vote the Sushi Ops team will return the Merkel Distributor Contract Sushi tokens to the Treasury wallet.

====================================================================================================
[76] id=0xb9d4a5edb70aad568b4a7b71d9fb2ee0e5ca366fcd5cf6b9200cdec6a5c4073d  token=SUSHI  space=sushigov.eth  date=2024-08-10
TITLE: Sushi High Kitchen Candidate - Hee-Sang Koo [Implementation]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
Sushi High Kitchen Appointment Vote

This proposal expects to produce an implementation.
The application forum post for Sushi High Kitchen elections can be found here:
https://forum.sushi.com/discussion/23761-apply-to-become-a-sushi-high-kitchen-member

Candidate Name: Kevin Michael Kozeny

https://forum.sushi.com/discussion/23761-apply-to-become-a-sushi-high-kitchen-member?comment=87411 

Motivation and Interest:

I’ve always been interested in SushiSwap because it stands out as an original DEX. Especially noteworthy is how SushiSwap was one of the first to distribute fee revenue to Sushi token holders, truly embodying the values of decentralization and democratization in the crypto space. This has made a significant contribution to the ecosystem. While many DAOs are becoming more like proprietary foundations, SushiSwap maintains its commitment to DAO values, which is why I’ve always wanted to be part of the Sushi ecosystem.

Additionally, I’ve come to understand firsthand how challenging it is to run a democratic and decentralized DAO. I’m the Vice-Champion of Bankless Korea DAO and also founded and currently run the Bankless Korea Investment DAO, a SubDAO. I believe that for a DAO to be truly decentralized and democratic, it must be closely integrated with the DeFi ecosystem, and its operational system must support this. By participating as a member of SushiSwap’s High Kitchen, which is a model of exemplary governance, I aim to apply SushiSwap’s values to the operation of

====================================================================================================
[77] id=0x29e0ef306104a2c1b135fb3070acf8ccb639af6649d2594e8dad1151567a8825  token=SUSHI  space=sushigov.eth  date=2024-08-10
TITLE: Sushi High Kitchen Candidate - Adarsh Bhatt [Implementation]
CHOICES: Yay | Nay | Abstain
TEXT (first 1500 characters):
Sushi High Kitchen Appointment Vote

This proposal expects to produce an implementation.
The application forum post for Sushi High Kitchen elections can be found here:
https://forum.sushi.com/discussion/23761-apply-to-become-a-sushi-high-kitchen-member

Candidate Name: Adarsh Bhatt 

https://forum.sushi.com/discussion/23761-apply-to-become-a-sushi-high-kitchen-member?comment=87133 

Motivation and Interest:

I am passionate about becoming a SushiSwap High Kitchen Member because I firmly believe in the transformative potential of decentralized finance broadly and admire SushiSwap’s innovative approach in the DeFi space specifically, as one of the first movers in the category. My journey as an early-stage investor in the web3 ecosystem I share much excitedment as to how decentralized protocols can revolutionize traditional financial systems.

SushiSwap was actually one of my first introductions into the DeFi space and pushed me to learn more. Over the years, I have closely collaborated with one of the Sushi Labs members, gaining deep insights into the vision and long-term goals of SushiSwap. This relationship has fueled my excitement about SushiSwap’s mission and upon learning about thHigh Kitchen, it was a no-brainer for me to apply and potentially become a direct contributor in its journey.

Joining the High Kitchen would be a meaningful opportunity for me to actively participate in shaping the future of SushiSwap and contribute to the broader DeFi movement. I am committed to

====================================================================================================
[78] id=0xa0030e41712ef24187dc56ef03ac37bfd8c7bb10b102571feace8ef4c2e37123  token=SUSHI  space=sushigov.eth  date=2024-12-06
TITLE: Treasury Diversification Proposal [Signal]
CHOICES: Yay | Nay
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

https://forum.sushi.com/discussion/25769-treasury-diversification-proposal

Synopsis:

As the Sushi DAO continues to evolve, it is crucial to ensure the sustainability and growth of our treasury. The DAO ultimately holds its treasury in SUSHI tokens, which exposes it to high volatility and potential liquidity challenges. This proposal outlines a strategy for diversifying the treasury assets to mitigate risks and enhance the protocol’s long-term stability.

Objectives:

1. Reduce Volatility: Minimize the impact of native token holdings on the treasury’s value.
2. Enhance Liquidity: Increase liquidity for operations and strategic assets.
3. Generate Yield: Explore staking, lending, or liquidity provision opportunities.

TLDR:

Full strategy of the treasury diversification proposal can be found in the forum post attached.

====================================================================================================
[79] id=0xdec0263f8991b3d8c2f6b94e1f89e81ee7f4a66a387b196d74196a6cef73b04f  token=SUSHI  space=sushigov.eth  date=2024-12-14
TITLE: Treasury Diversifications [Implementation]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/discussion/25954-Treasury%2520Diversification%2520%5BImplementation%5D

**Synopsis:**

This implementation proposal outlines a flexible approach for diversifying Sushi DAO’s treasury into stablecoins and blue-chip assets, such as WBTC and ETH/WETH. The diversification strategy aims to support Protocol Owned Liquidity (“POL”) initiatives, bolstering SushiSwap’s competitive positioning and ensuring sustainable value generation for SushiSwap, Sushi Labs, and token holders. Sushi Labs will receive and manage these diversified funds, aligning with the best interests of the SushiSwap protocol to achieve its POL, fee generation, and growth and operational continuity objectives by funding Sushi Labs’ infrastructure and personnel, product expansion, research, and development.

**Treasury Diversification Strategy:**

The following treasury diversification strategy proposal aims to enhance SushiSwap’s operational resilience and liquidity depth.

1) Asset Diversification:
* Diversification of Sushi DAO’s native token treasury holdings into stablecoins and blue-chip cryptocurrencies (e.g., WBTC and ETH/WETH);
* The exact composition and allocation will remain flexible and at the sole discretion of the Sushi Labs team to adapt to prevailing market conditions and opportunities.

2) Implementation Mechanism:
* Diversification will occur gradually, subje

====================================================================================================
[80] id=0x50ebd0803c290d08b566a6c18a9778f705312223a56ae6876b63874898f55bf0  token=SUSHI  space=sushigov.eth  date=2025-12-07
TITLE: Increase SUSHI Annual Emissions Rate (AER) for AMM Liquidity, Listings & Private Capital Deals [Signal]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

https://forum.sushi.com/discussion/1312021-increase-sushi-annual-emissions-rate-aer-for-amm-liquidity-listings-private-capital-deals-implementation

Synopsis:

This proposal seeks to raise the SUSHI Annual Emissions Rate (AER) from 1.5% to up to 5% of total annualized SUSHI supply, with emissions primarily focused on:

Deepening AMM liquidity on core networks
Incentivizing highquality token listings
Structuring private liquidity deals with aligned capital partners
Funding growth initiatives such as aggregator rebates and Blade POL
Sushi Labs generated over $10M in revenue in 2024, and our near-term goal is to scale Sushi to $20M in ARR. The most direct way to achieve this is to grow deep, sticky liquidity in core pools and scale protocol-owned liquidity (POL), particularly for Blade.

Blade has already been seeded with roughly $1M of initial POL and is averaging ~$2–5K per day in fee revenue. If we scale this model with targeted emissions and private-capital partnerships across more pools and networks, Sushi has a clear path to the $20M ARR target.

If Sushi reaches and sustains this ~$20M ARR level, we believe the protocol will be in a position to support substantially increased SUSHI token buybacks, funded from a growing treasury reserve of revenue and non-SUSHI assets. A key objective of this program is to build that reserve in a disciplined way, subject to

====================================================================================================
[81] id=0x9c4dd678c47020b2d308bb6876a9140f17f120c1b324727025703cb92186362e  token=SUSHI  space=sushigov.eth  date=2025-12-14
TITLE: Increase SUSHI Annual Emissions Rate (AER) for AMM Liquidity, Listings & Private Capital Deals [Implementation]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/discussion/1312021-increase-sushi-annual-emissions-rate-aer-for-amm-liquidity-listings-private-capital-deals-implementation

Synopsis:

This proposal seeks to raise the SUSHI Annual Emissions Rate (AER) from 1.5% to up to 5% of total annualized SUSHI supply, with emissions primarily focused on:

Deepening AMM liquidity on core networks
Incentivizing highquality token listings
Structuring private liquidity deals with aligned capital partners
Funding growth initiatives such as aggregator rebates and Blade POL
Sushi Labs generated over $10M in revenue in 2024, and our near-term goal is to scale Sushi to $20M in ARR. The most direct way to achieve this is to grow deep, sticky liquidity in core pools and scale protocol-owned liquidity (POL), particularly for Blade.

Blade has already been seeded with roughly $1M of initial POL and is averaging ~$2–5K per day in fee revenue. If we scale this model with targeted emissions and private-capital partnerships across more pools and networks, Sushi has a clear path to the $20M ARR target.

If Sushi reaches and sustains this ~$20M ARR level, we believe the protocol will be in a position to support substantially increased SUSHI token buybacks, funded from a growing treasury reserve of revenue and non-SUSHI assets. A key objective of this program is to build that reserve in a disciplined way, subject to

====================================================================================================
[82] id=0xa7f0caa483abaf35cabbf6b48104bec2797a03b941c3c9b746eed71e9bdeb109  token=SUSHI  space=sushigov.eth  date=2026-01-13
TITLE: MasterChef LP Migration to V3 + Protocol-Deployed Liquidity [Signal]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a community signal. Full details and discussions thus far can be found at:

https://forum.sushi.com/discussion/1312123-masterchef-lp-migration-to-v3-protocoldeployed-liquidity-rfc

# TL;DR
- Sushi currently has **tens of millions of dollars in LP tokens staked in legacy MasterChef & MiniChef contracts** across Ethereum, Arbitrum, Gnosis, and Polygon. (**~$56–57m** (approximate, fluctuates with prices).
- Much of this liquidity is **inactive and/or underutilized** but still locked in outdated emissions contracts and highly inefficient V2style pools.
- We propose to:
	1. **Catalog all staked LP by wallet → LP amount** using subgraphs and on-chain data.
	2. **Migrate LP tokens out of MasterChefs** via a new _Migrator_ contract into a designated V2 LP collector.
	3. **Open a public claim window (30–60 days)** where LPs can prove ownership and request withdrawal.
	4. **Aggregate remaining LP and programmatically redeploy the underlying into V3-style positions as protocol-deployed liquidity in conformance with governance-approved parameters**, while preserving a mechanism for users to **claim their share** later if they return.
- The Sushi core team expects this architecture, once fully deployed across the targeted pools and chains, to generate material protocol fee revenues.
- We intend for a **majority** of these protocol fees to be captured by the **Sushi Foundation** and **compounded back into protocol-deployed liquidity on core network

====================================================================================================
[83] id=0x26fad0eda6e06d759a6a9f69d96b6ced97e8115f5ccaa7d2f96e32f9b0cec578  token=SUSHI  space=sushigov.eth  date=2026-01-20
TITLE: MasterChef LP Migration to V3 + Protocol-Deployed Liquidity [Implementation]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

https://forum.sushi.com/discussion/1312123-masterchef-lp-migration-to-v3-protocoldeployed-liquidity-rfc

# TL;DR

- Sushi currently has **tens of millions of dollars in LP tokens staked in legacy MasterChef & MiniChef contracts** across Ethereum, Arbitrum, Gnosis, and Polygon. (**~$56–57m** (approximate, fluctuates with prices).
- Much of this liquidity is **inactive and/or underutilized** but still locked in outdated emissions contracts and highly inefficient V2style pools.
- We propose to:
	1. **Catalog all staked LP by wallet → LP amount** using subgraphs and on-chain data.
	2. **Migrate LP tokens out of MasterChefs** via a new _Migrator_ contract into a designated V2 LP collector.
	3. **Produce official block of migration snapshot** for each pools and it's LPs.
	4. **Open a public claim window (30–60 days)** where LPs can prove ownership and request withdrawal.
	5. **Aggregate remaining LP and programmatically redeploy the underlying into V3-style positions as protocol-deployed liquidity in conformance with governance-approved parameters**, while preserving a mechanism for users to **claim their share** later if they return.
- The Sushi core team expects this architecture, once fully deployed across the targeted pools and chains, to generate material protocol fee revenues.
- We intend for a **majority** of these protocol fees to be captured by the **Sushi F

====================================================================================================
[84] id=0xf41c3c6def5d9088c9fa8aa7aab6b3d1b148df2875ed0785270de65b0428c0e0  token=SUSHI  space=sushigov.eth  date=2026-08-18
TITLE: SUSHI Tokenomics Restructure: SUSHI Reserve, Revised xSUSHI Buybacks, and Protocol-Deployed Liquidity Deployment to Robinhood Chain [Signal]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce a **community signal**. Full details and discussions thus far can be found at:

[https://forum.sushi.com/discussion/1313076-sushi-tokenomics-restructure-sushi-reserve-revised-xsushi-buybacks-and-protocoldeployed-liquidity-deployment-to-robinhood-chain](https://forum.sushi.com/discussion/1313076-sushi-tokenomics-restructure-sushi-reserve-revised-xsushi-buybacks-and-protocoldeployed-liquidity-deployment-to-robinhood-chain)

# TL;DR

- Sushi’s current protocol fee model directs value primarily toward **xSUSHI buybacks**. This proposal would replace that structure with a more balanced framework supporting stakers, protocol reserves, and Sushi operations.
- We propose to:
  1. Allocate **1% of protocol fees**, plus **1% of all perpetuals fee revenue**, to **monthly xSUSHI buybacks**.
  2. Allocate **4% of protocol fees** to **weekly SUSHI purchases** for a new **SUSHI Reserve**, with purchased SUSHI held as protocol-controlled reserves.
  3. Direct **all remaining protocol fees, migration fees, and other protocol revenue to Sushi Ops** to fund development, incentives, partnerships, liquidity initiatives, security, and operations.
  4. Authorize the relocation of a portion of Sushi’s **protocol-deployed liquidity currently held on EVM networks** to **Robinhood Chain**, beginning with an **ETH–USDG V3 position**.
- Sushi’s initial target is approximately **$10–20 million of protocol-deployed TVL on Robinhood Chain**, with deployments execute

====================================================================================================
[85] id=0x2e6df9d02d40e05e9dede6ad50bac47a3e8e7cd3604f4caa63b3995eea7384b0  token=SUSHI  space=sushigov.eth  date=2026-08-27
TITLE: SUSHI Tokenomics Restructure: SUSHI Reserve, Revised xSUSHI Buybacks, and Protocol-Deployed Liquidity Deployment to Robinhood Chain [Implementation]
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This proposal’s expectation is to produce an implementation. Full details and discussions thus far can be found at:

[https://forum.sushi.com/discussion/1313076-sushi-tokenomics-restructure-sushi-reserve-revised-xsushi-buybacks-and-protocoldeployed-liquidity-deployment-to-robinhood-chain](https://forum.sushi.com/discussion/1313076-sushi-tokenomics-restructure-sushi-reserve-revised-xsushi-buybacks-and-protocoldeployed-liquidity-deployment-to-robinhood-chain)

# TL;DR

-   Sushi’s current protocol fee model directs value primarily toward **xSUSHI buybacks**. This proposal would replace that structure with a more balanced framework supporting stakers, protocol reserves, and Sushi operations.
    
-   We propose to:
    
    1.  Allocate **1% of protocol fees**, plus **1% of all perpetuals fee revenue**, to **monthly xSUSHI buybacks**.
        
    2.  Allocate **4% of protocol fees** to **weekly SUSHI purchases** for a new **SUSHI Reserve**, with purchased SUSHI held as protocol-controlled reserves.
        
    3.  Direct **all remaining protocol fees, migration fees, and other protocol revenue to Sushi Ops** to fund development, incentives, partnerships, liquidity initiatives, security, and operations.
        
    4.  Authorize the relocation of a portion of Sushi’s **protocol-deployed liquidity currently held on EVM networks** to **Robinhood Chain**, beginning with an **ETH–USDG V3 position**.
        
-   Sushi’s initial target is approximately **$10–20 million of protocol-

====================================================================================================
[86] id=0x0c162a69ab8046e5f08b5f276d3e0aa18d6c0d49e06d0eaab2e92564ac90a471  token=SYN  space=synapseprotocol.eth  date=2024-12-02
TITLE: [SIP - 40] - Reducing Yearly Emissions by 2.3 Million SYN (66% reduction)
CHOICES: For | Against
TEXT (first 1500 characters):
With the successful launch and adoption of SynapseRFQ, SynapseX, and SynapseCCTP, it's time to optimize Synapse DAO emission spend to more capital-efficient levels. SynapseRFQ already makes up 80% of bridge volume, which should reduce reliance on traditional liquidity based bridging. These newer bridge modules offer cheaper quotes without requiring SYN emissions, allowing us to significantly reduce emissions while maintaining service quality.

Proposed monthly emissions adjustments:

Major Reductions:
Arbitrum: 40,000 SYN (-69%)
BSC: 20,000 SYN (-61%)
Optimism: 8,000 SYN (-81%)
Base: 8,000 SYN (-79%)
Blast: 10,000 SYN (-70%)

Moderate Reductions:
Avalanche: 6,000 SYN (-50%)
Canto: 0 SYN (-100%, replace with POL)

Maintain Current:
Polygon: 20,000 SYN (positive ROI)
Metis: 15,000 SYN (subsidized)

Total New Monthly Emissions: 127,000 SYN ($63,500 at $0.50/SYN) Total Reduction: 66% in emissions, 66% in USD cost

More Details: https://forum.synapseprotocol.com/d/2084-synapse-emissions-reduction

====================================================================================================
[87] id=0x3e8a9ad0cd5c2fb7bab2a4a6b452524d66af253f82596d8ae2dc6bb30d4d61a6  token=SYN  space=synapseprotocol.eth  date=2024-12-10
TITLE: [SIP - 41] – Buyback 3.5 million USD worth of $SYN over 3 months
CHOICES: For | Against
TEXT (first 1500 characters):
Summary: 

The core objective of this proposal is to strengthen the protocol's economic foundation through strategic $SYN accumulation, preparing for upcoming staking mechanisms while maintaining robust treasury reserves. This proposal suggests the DAO implement an initial buyback program(BB-1) of $3.5M USD worth of $SYN over (at maximum) 3 months, starting from the time the proposal passes. 

Implementation: 

Consolidate 3.5 million USD worth of assets and claimed fees from all chains Synapse operates on. Uses the assets  to purchase $SYN from on-chain venues with deep aggregated $SYN liquidity such as DefiLlamaswap and Cowswap, taking no longer than 3 months, starting when the proposal passes. 

Reporting: 

Provide regular updates with on-chain receipts to all established governance channels, ensuring transparency.

--- 

Detailed Discussion: 

https://forum.synapseprotocol.com/d/2085-synapse-protocol-enhancement-treasury-optimization/9

====================================================================================================
[88] id=0xcef531ec731cd73c4edd8ed573bf37760c2981fdb339c916a5a3a165fd8ce73c  token=SYN  space=synapseprotocol.eth  date=2024-12-13
TITLE: [SIP - 42] Enhancement of SYN/ETH liquidity on L2s
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Summary: 

As Synapse Protocol enters its next phase of development it is crucial that we maintain deep SYN liquidity for protocol health and to provide token holders efficient on-chain avenues for trading the token. 

Implementation:

1. Incentivize a SYN/WETH pool on Optimism on Velodrome, with 50k $OP allocated for this
2. Decrease SYN min fees between L2s to increase composability.
3. Distribute incentives over a 3-month period to bootstrap initial liquidity

Considerations: 

Target $3-5M in TVL to ensure efficient price discovery and trading. After the 3 month period, emissions should be re-evaluated based on pool volume, total TVL. If the pool has not reached the TVL target, we should reassess the venue and incentive strategy, while if the TVL target is reached and/or available liquidity achieves effective pricing for swaps on optimism, the incentive program should be continued

---- 

Discussion Details: https://forum.synapseprotocol.com/d/2086-syneth-liquidity-enhancement-proposal

====================================================================================================
[89] id=0x274e0c14be2a62c2a293a0cade4560481ab8da183e66d250ed9c8cdd9bbd5b4e  token=SYN  space=synapseprotocol.eth  date=2025-01-29
TITLE: [SIP - 43] $SYN Token Upgrade to $CX
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
# Introduction
The motivation of this proposal is to upgrade the $SYN token to $CX. This will allow for a stronger, more unified protocol for all $SYN holders to benefit from Cortex Protocol. This unifies the focus, liquidity, and ownership among our community, users, and other stakeholders across one token, instead of two separate ones. We are therefore suggesting to upgrade $SYN and give the value of Cortex to $SYN holders.


# Proposal Implementation:
- Ratify the medium proposal from Cortex Labs approving the $CX allocation for $SYN holders. Users receive 5.5 $CX for every $SYN.
- Transfer ownership, IP and governance of Cortex Protocol from Labs to the new Cortex DAO for the benefit of $CX holders.
- Merge all existing $SYN utility into $CX resulting in a unified token. Resulting in a unified $CX token and DAO inheriting:
a) $CX as the native governance token for all Synapse and Cortex related contracts and protocol operations
b) A combined DAO with all assets
- Open a two way token migration portal between $CX and $SYN for the next three months. All major CEXs are in communication and expected to support the token upgrade by this deadline. After this deadline, there will be an additional 9 month grace period where $SYN will be able to migrate to $CX but not the other way around.
Afterwards, $SYN will have no utility.
- $CX Transferability and liquidity management:
a) Turn on $CX transferability
b) Migrate the majority of SYN/ETH protocol owned liquidity to a $CX/SOL poo

====================================================================================================
[90] id=0xa5e3ac51dffe1fd5099bff51dcbdb2c370df981d7b29092adc487abacd2e63b2  token=T  space=threshold.eth  date=2023-02-28
TITLE: Treasury Guild Committee Elections (3rd Epoch)
CHOICES: LakeLagoi | Vict0r | Will | JohnPackel | Sap | MrsNuBooty
TEXT (first 1500 characters):
The Treasury Guild Committee has 9 seats.
The top 5 nominees by vote weight will be appointed for a 12-month term upon expiration of this snapshot vote.
You may split your vote among candidates.

Rules for the elections are available here:
https://forum.threshold.network/t/tip-31-rules-for-guild-committee-elections-and-management/378

====================================================================================================
[91] id=0xf2590e88c6a651c8bd6635e244025c6d5f1feb5125bc77a63f2633536a7ec3c7  token=T  space=threshold.eth  date=2023-04-11
TITLE: TIP-047 Temp-Check: Liquidity Bootstrappening and Growth Part 2 - PCV
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Overview:

This is a multi-phased proposal intended to deploy a DAO-owned strategic plan to deepen tBTC liquidity and develop essential Threshold BTC-based Protocol Owned Liquidity.

It builds a DeFi revenue flywheel owned by the Threshold DAO and managed by the Threshold Treasury Guild (TTG) through four phases. This proposal was originally authored by Matt.

Important Note:

This version of TIP 47 is the result of multiple working sessions and iterations with the TTG. The Threshold DAO onchain proposal flow process requires a successful temp check snapshot before queing into Governor Bravo. The governance plan is to conduct the Threshold DAO temperature check to gauge the spirit of this proposal while the TTG conducts the final diligence and parameter determination required to execute the proposal.

If the temp check passes, this proposal will be amended to include final details before moving onto Governor Bravo vote if it successfully passes the temp check stage. To improve readability any such detail will be identified by a :pencil2:.

Milestones and Deadlines:

Threshold DAO Temperature Check
04/07/23
Amended proposal submitted to Threshold DAO
Week of 04/10/23
Governor Bravo proposal kick off
Week of 04/07/23
Dates for each bond phase are intentionally left open to provide execution flexibility for the TTG.
Who Is Involved?:

Threshold Token Holder DAO, Threshold Treasury Guild

Detailed Summary:

Phase I

The first phase is a test of the bonding mechanism, and our abil

====================================================================================================
[92] id=0x62a26aa03bdfce5a6908310c05227285053f3436950e72c1144fcc9edccc6966  token=T  space=threshold.eth  date=2023-05-01
TITLE: Threshold Treasury Guild 2Q23 Budget Proposal
CHOICES: Approve | Disapprove
TEXT (first 1500 characters):
Forum discussion: https://forum.threshold.network/t/gp-threshold-treasury-guild-2q23-budget-proposal/593

Text of proposal: 
Threshold Treasury Guild: 2Q23 Budget Request

Vote Type: Single choice voting (Yes/No)

Overview:

As part of TTG´s mission and scope and with its defined objectives the TTG is requesting discretionary funding of 50m T (~$1.6m) from the Threshold Treasury for Q2 2023.

This discretionary budget will be primarily used for:

Compensation for Threshold’s Guild and Council contributors
Execution of ongoing liquidity incentives
Execution of diversification efforts
Reimbursement to Bootstrapping node-operators per TIP-045
Payment for code audits
Other ongoing expenses and reimbursements supporting TTG’s mission
Milestones and Deadlines:

Budgeted funds are for 2Q 2023.

Proposed schedule:

Forum Discussion Started: April 25, 2023
Forum Discussion Concluded: April 28, 2023
Snapshot Vote Started: April 29, 2023
Snapshot Vote Concluded: May 2, 2023
Authors:

The Threshold Treasury Guild Committee (TTG) multisig consists of @JohnPackel , @Will , @ben , @Vict0r , @sap , @LakeLaogai , @Eastban. Two additional members are being added.

Threshold Treasury Guild OKRs

![image](ipfs://bafkreiauvbgruofoppvrepy5dca2zmu545dulcalf5uagmoozx4mq7vxuy)
    
Use of Proceeds

Funds will be managed under the TTG multi-sig and will be allocated towards the TTG goals listed above as well as any discretionary expenses that may fall outside of the initial scope. The funds will prima

====================================================================================================
[93] id=0x6072d21202727b5119166ba513c556146488fd620069c2ea0ef12ee1e24ce362  token=T  space=threshold.eth  date=2023-05-10
TITLE: TIP 51: Coverage Pool Allocation
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
TIP 51: Coverage Pool Allocation

Vote type:

Token Holder Governor Bravo Temp Check

Overview:

This is a proposal to provide more insurance to tBTC users in the form of allocating more Threshold DAO resources to the coverage of tBTC. Responsible risk management on behalf of the DAO is critical for tBTC users as the network continues to scale.

Currently, tBTC is backstopped by a single asset T-only coverage pool. Strong steps toward improving protocol risk management are achieved by the DAO committing more assets to this pool.

This proposal is an extension of TIP 43- Coverage Pool Migration. The intention is to strike a better initial balance between early tBTC coverage and the opportunity for the DAO to maximize yield by leveraging internal assets elsewhere across the DeFi ecosystem.

The proposal is not the end state for Threshold DAO tBTC risk management. The Threshold DAO can elect to expand tBTC coverage into multiple assets by deploying a new, fully incentivized multi asset coverage pool. This would allow for coverage outside of just T as a single asset which is beneficial for risk management. However, any expansion is out of scope of this proposal.

The full proposal is available on Threshold forums:

https://forum.threshold.network/t/tip-51-coverage-pool-allocation/610

====================================================================================================
[94] id=0x8b37f62aade328d1feffe899cd2c9484b8d550ba2e257a277ea8cbb0a8d01a6e  token=T  space=threshold.eth  date=2023-08-02
TITLE: TIP 55: Contractor role for POL Operations Coordinator
CHOICES: Approve | Disapprove
TEXT (first 1500 characters):
Vote Type
Token holder DAO Snapshot with a 7-day vote period.

DAO-elected Sponsors
@ben @JohnPackel @Sap @jakelynch

Timeline
 - 7 days for comment / discussion on this proposal
 - Token holder DAO Snapshot with a 7-day vote period

Definitions
Protocol Owned Liquidity (POL)
Assets owned and controlled by the DAO that are used to provide liquidity.

Purpose
This proposal is a request to the Threshold DAO to fund a POL Operations Coordinator role for the purpose of overseeing all operations for the DAO’s Protocol Owned Liquidity. This proposal recommends East as a candidate for the position.

Motivation
Threshold Treasury Guild has become an important working unit in the DAO. The guild was created and empowered by the DAO to work towards a strong, diversified and resilient treasury portfolio, to grow protocol owned liquidity, and to manage incentives for Threshold services and products…

Management of these activities requires heavy involvement of the guild’s committee members. The successful launch of tBTC, new exciting proposals, and the DAO’s expansion to L2s and other chains creates a persistent workload for the TTG. It is obvious that specialized roles with more time allocation are necessary. Roles such as Growth Lead (Incentives and Expansion) , POL Operations, Chairman (Meetings, Agenda, Moderation, Structure) and Finances (Accounting, Report, Payroll) are evident posts.

In practical terms this means that the TTG will continue to provide the strategy and oversight for

====================================================================================================
[95] id=0xb1b5d2902cc11e990c0c2d09351d979abb8c8d41ba987f38f54367f49229213e  token=T  space=threshold.eth  date=2023-08-09
TITLE: TIP 54: tBTC & T, better together (Part 1)
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
Please read before participating!

The governance process for TIP 54 is broken down into two separate cycles. 

Part 1 is the governance process for the second part of the proposal which includes deposit fees and rebates. This is a 3 day temp check snapshot. There are two actions resulting from this portion of the proposal: 

1) Lower the tBTC deposit fee to 0.1%

2) Transfer 13M T from the DAO to the threshold treasury multisig to manage a fee rebate program

The remainder of the proposal including details of the buy back and make program are still under DAO discussion and will be put to a separate governance cycle when appropriate. 

Full details for this proposal are available on the forum here -

https://forum.threshold.network/t/tip-54-tbtc-t-better-together/635

====================================================================================================
[96] id=0x0f361e70755c681183314355390999509c9d9859ad875b5cc3ab2def96de7690  token=T  space=threshold.eth  date=2023-08-24
TITLE: GP-031: Threshold Treasury Guild 2H23 Budget Proposal
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
Overview:

As part of TTG´s mission and scope and with its defined objectives the TTG is requesting discretionary funding of 152,422,368 T from the Threshold DAO Treasury for the five remaining months of 2H 2023 - August through December 2023.

This budget will be primarily used for:

Compensation for Threshold’s Guild and Council contributors
Execution of ongoing liquidity incentives
Execution of diversification efforts
Payment to Bootstrapping node-operators per TIP-045
Payment for development efforts and code audits
Other ongoing expenses and reimbursements supporting TTG’s mission

This is a temperature check snapshot and if passed this proposal will move onto a full threshold DAO governor bravo cycle.

The full proposal and including a more detailed budget breakdown is viewable on the governance forum here -

https://forum.threshold.network/t/gp-031-threshold-treasury-guild-2h23-budget-proposal/655

====================================================================================================
[97] id=0x4ddb002da7f2bf4e63ed906c273b2f47b65e1dfb7f845502e9ff645dfd2a8578  token=T  space=threshold.eth  date=2023-08-25
TITLE: Treasury Guild Committee Elections (4th Epoch)
CHOICES: Ben Longstaff | Eastban | Figue | Ramaruro
TEXT (first 1500 characters):
The Treasury Guild Committee has 9 seats.
The top 4 nominees by vote weight will be appointed for a 12-month term upon expiration of this snapshot vote.
You may split your vote among candidates.

Rules for the elections are available here:
https://forum.threshold.network/t/tip-31-rules-for-guild-committee-elections-and-management/378

====================================================================================================
[98] id=0x73a5b5c421e4c066b18ade29acbaee3a95a8c407778a2193feaef668b7b7a282  token=T  space=threshold.eth  date=2023-08-29
TITLE: TIP 57: Transfer Council POL to Treasury Guild Multisig
CHOICES: Approve | Disapprove | Abstain
TEXT (first 1500 characters):
**Vote Type**
Token holder DAO Snapshot with a 7-day vote period.

**DAO-elected Sponsors**
Sap, East, Will

**Timeline**
7 days for comment / discussion on this proposal.

Token holder DAO Snapshot with a 7-day vote period.

**Purpose**
This proposal is a request to the Threshold DAO to approve the transfer of Council-held Protocol Owned Liquidity (POL) to the Treasury Guild Committee’s Multisig.

**Motivation**
The DAO’s Protocol Owned Liquidity has continued to grow, thanks to the TTG’s various diversification efforts, including the continued success of TIP 46 and TIP 47, as well as revenues from incentives directed at existing POL allocations.

In addition, the recently ratified TIP 55 has increased the capacity of the DAO to manage and optimise POL, with the creation of a specific POL Operations role.

Given the importance of POL to the continued growth of the DAO Treasury, this proposal suggests transferring certain strategic POL to the Threshold Treasury Guild Mutisig.

The TTG members are better equipped to validate and queue the transactions required for POL allocation and maintenance, which reduces the risk of error and increases POL security. Most POL recommendations come from TTG and are executed by Council, which creates inefficiency due to signer fatigue and information transfer requirements.

Assets currently held by the Threshold Council can be viewed here: https://debank.com/profile/0x9f6e831c8f8939dc0c830c6e492e7cef4f9c2f5f 3

Assets currently held by the Tr

====================================================================================================
[99] id=0x5b03a6a2ca114845eed9b96591daccfdccbf3681eeeffbc1cbf45e9cb59e8af3  token=T  space=threshold.eth  date=2023-09-07
TITLE: TIP 54: tBTC & T, better together (Part 2)
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
TIP 54 is broken down into two governance cycles. The governance cycle for TIP 54 Part 1 was successful. This is a temp check snapshot for part 2. If passed, this proposal will move into the Token Holder DAO Governor Bravo instance.

This proposal will result in a Threshold Treasury Guild spend approval on the DAO's tBTC accrued from network fees for the following purpose.

Buyback and Make:

I propose that accrued tBTC fees be periodically single-side deposited into a T/tBTC pool, effectively buying back T with deposit amounts and timing determined at the discretion of the treasury guild. 

As tBTC fees grow, more and more T is bought back and locked in an DAO-owned LP position. These periodic buybacks will take T off the market, deepen T and tBTC liquidity, and further tie the successes of tBTC and T.

The pros and cons of this model, called “buyback and make”, are well covered by Joel Monegro at Placeholder 16.

Creating a deep T/tBTC pool doesn’t only create stronger liquidity for the pair… it also becomes another revenue stream for the DAO. The Curve T/ETH pool 2 is projected to earn 46% APR next epoch, while the Balancer T/WETH pool earns 9.7-15.75%.

Full details of TIP 54 Part 2 are on the governance forum here -

https://forum.threshold.network/t/tip-54-tbtc-t-better-together/635

====================================================================================================
[100] id=0xeba09624d033bba124dafdd6d762c96e6367436d7787f8f4eaa3127e7f7fac57  token=T  space=threshold.eth  date=2023-09-14
TITLE: GP-032: Move token mint operations to Threshold Foundation subsidiary
CHOICES: Approve | Disapprove
TEXT (first 1500 characters):
Vote Type
Token holder DAO Snapshot with a 5-day vote period.

DAO-elected Sponsors
@sap @JohnPackel @Will

Timeline
- 3 days for comment / discussion on this proposal (Forum)
- Token holder DAO Snapshot with a 5-day vote period

Background
Threshold DAO recently established a Cayman Islands Foundation Company, the Threshold Foundation, as authorized by the DAO in GP-025.

The purpose of the Threshold Foundation is to support Threshold DAO as a legal proxy, to sign legal agreements, and protect contributors from personal liability. It acts on behalf of Threshold DAO and its token holders.

The Threshold Foundation subsequently formed a subsidiary in the British Virgin Islands, Threshold BVI Ltd, wholly owner by the Threshold Foundation.

Since Threshold Foundation takes direction from token holders, this proposal seeks authorization to follow token minting best practices and house token mints in the BVI subsidiary.

Overall, the full functions to be housed in the new legal entities will be developed and likely evolve progressively.

This proposal is an attempt to move a basic function of the DAO, token minting, to the BVI subsidiary prior to the upcoming mint for staking rewards (see TIP-53).

Proposal
This proposal suggests to create a new multisig wallet for the BVI subsidiary, to house T token mints required by the stable yield model set out in TIP-003.

The new multisig will have the same signer set as the current Council multisig, with the addition of the Foundation Dire

====================================================================================================
[101] id=0x064390c13d1a8b6dc5a5e64b82e69a8dabecd01b7ee024fb709207606af692c6  token=T  space=threshold.eth  date=2023-09-27
TITLE: TIP-060 Solana Growth Partnership
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
This is a temp check. If passed the proposal will proceed to the Threshold DAO GB. 

Vote Type:
Token holder DAO Governor Bravo Proposal

DAO Elected Representative Sponsors:
Sap, Will

Overview:
tBTC has successfully launched on Solana, but with limited usage and in competition with existing efforts to bring native wBTC to Solana. There exists an opportunity now for a first mover advantage to establish tBTC as the new canonical BTC on Solana. To do that, the cold start problem for tBTC TVL and volume on Solana needs to be addressed immediately with new protocol integrations that increase the liquidity & utility of tBTC as collateral.

This is a proposal for the Threshold DAO to engage in a partnership with Mango & Dual DAO to deliver products supported by CKS Systems liquidity to bootstrap TVL for tBTC across the Solana DeFi ecosystem.

These protocols are better together and a more liquid BTC market on Solana via tBTC is collectively beneficial for T, MNGO, DUAL and even SOL. By making this benefit clear to the respective communities it’s possible to engage a positive feedback loop to grow tBTC. The proposed deal structure is designed with this in mind and includes treasury swaps in the form of on-chain call options to formalize the relationship of our mutual successes.

Full proposal available on the forums:

https://forum.threshold.network/t/tip-060-solana-growth-partnership/675

====================================================================================================
[102] id=0xc1447c0df207db94ef425be4bf28a3f51de597b0448c551d4b35d15f7f6de17c  token=T  space=threshold.eth  date=2023-10-24
TITLE: TIP061: Threshold x Flowdesk: T Liquidity and beyond
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
This is a snapshot temp check. If successful this proposal will move into a DAO Governor Bravo cycle before being successfully ratified by the DAO.

Please read: 

This temp check is for the following proposal with option 2 "Threshold to provide 75M T, Flowdesk to run a twap/vwap sell program to fund the other leg used for MM" and the option for the DAO monthly payment to occur with USDC. This partnership will occur with Threshold Treasury Guild oversight meaning any minor adjustments to strategies provided in the proposal can be approved by the Threshold Treasury Guild. 

Overview:

Flowdesk is the leading regulated digital assets Market Making as-a-Service infrastructure provider for token issuers, exchanges, and institutions. Our model offers token issuers a fully transparent and capital-efficient approach to managing liquidity on both centralized and decentralized exchanges. We enable our clients to directly manage their own capital, while giving them access to our OTC and execution services supported by our global trading desk.

Our Market-Making as-a-Service model has been designed to improve trust, control, and fairness. We trade with the token issuer’s capital and are compensated with a flat retainer fee, solving for misalignment of incentives. This has several advantages:

- Full control over the trading strategy
- Comprehensive set of data & analytics to facilitate reporting
- On-the-fly parameter adjustment
- Trade and custody assets with a regulated counterparty
-

====================================================================================================
[103] id=0x0b62119036a508fbd7bde48797ed80a7c3cac7abd8cae1e3c72d00e13b4fec39  token=T  space=threshold.eth  date=2023-11-13
TITLE: TIP-063: Drop support for legacy staking
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
This proposal intends to drop support for legacy staking connectors.

====================================================================================================
[104] id=0xff4d6f51b0bc27150002acebe3de15cbdec3b5a0df967fadd129d71ff71d0062  token=T  space=threshold.eth  date=2023-11-29
TITLE: TIP-065: tBTC Fee Holiday
CHOICES: YES | NO | ABSTAIN
TEXT (first 1500 characters):
Vote Type
Token holder DAO Snapshot with a 7-day vote period.

DAO-elected Sponsors
@sap, @JohnPackel, @Eastban

Timeline
5 days for comment / discussion on this proposal.
Token holder DAO Snapshot with a 7-day vote period.

Proposal
Reduce tBTC mint fee to 0%, and reduce redemption fee to 0% for 60 days.

After 60 days, mint and redemption fees will be reinstated at their current values of 0.1% mint and 0.2% redemption.

Background
This proposal suggests a temporary pause of the tBTC mint fee, and a reduction of the redemption fee, to eliminate friction for new users of tBTC and enable new utility and use cases.

tBTC is at a crucial inflection point in its growth trajectory. Liquidity and TVL have grown steadily since launch, but mainstream DeFi use cases, such as lending markets and derivative trading, are pending an increase in TVL and volume.

Rationale
Threshold DAO currently charges a 0.1% mint fee, and a 0.2% redemption fee, which imposes a cost to DeFi users that wish to mint tBTC, and a spread between the tBTC and BTC price for traders. This reduces the amount of capital that can flow into tBTC, as well as the likelihood of arbitrage opportunities for tBTC traders and bots.

A pause of the bridge fees will enable new tBTC to enter the system, and reduce tBTC and BTC spread. This allows users that want to earn BTC yield to do so without reducing their principal, as well as market makers to quote tighter spreads, and provide more liquidity with confidence.

A short te

====================================================================================================
[105] id=0x4e5cf4085c1a333585322f00056f3270251bccbb40c8bbc1081080077d73f4d2  token=T  space=threshold.eth  date=2024-02-12
TITLE: TIP-075: tBTC Bridge Fee Holiday - part 2
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):


====================================================================================================
[106] id=0x12e0821712ed0326625b37a37d680ae93e0c272d4c88ff406e8cedc4f1af4c5e  token=T  space=threshold.eth  date=2024-02-13
TITLE: GP-034 GP-033 Threshold Treasury Guild Nominations Election - Epoch 5, 2024
CHOICES: Vict0r | SAP | wuji | Will | John Packel | nico186
TEXT (first 1500 characters):
The Treasury Guild Committee has 9 seats.
The top 5 nominees by vote weight will be appointed for a 12-month term upon expiration of this snapshot vote.
You may split your vote among candidates.

Rules for the elections are available here:
https://forum.threshold.network/t/gp-034-gp-033-threshold-treasury-guild-nominations-election-epoch-5-2024/778

====================================================================================================
[107] id=0x2ef702effc3343035a67d179b0cc0c2f51669d7bed94d66d3dc4322c882a8bea  token=T  space=threshold.eth  date=2024-06-05
TITLE: TIP-077: Funding request for Staking Pool Contract Development
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
The Threshold DAO would like to enable all holders of T to be able to stake without the need for the 40K T minimum and skills to run a node.

To that end, this proposal is for 10K USD funding (denominated in T) to DELIGHT LABS to deliver a staking pool contract that operators can deploy to run a community pool.

Please see the forum proposal and discussion for more details.

About DELIGHT LABS:
- Technology-driven team, started from 6 developers
- Experienced team in blockchain core development, validator operation, and DApp development
- Successful operation of validators on over 20 networks including T nodes
- Started dApp development from Terraswap, which is the first DEX in Terra, and building more projects for now
- Participating in T beta staker program, more than general T node

====================================================================================================
[108] id=0x071fd1e9c07ef367bb6f447390c316930fade1c5b122dfa51e7f188c88698b10  token=T  space=threshold.eth  date=2024-06-26
TITLE: TIP79 - Use thUSD protocol for expenses
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
Tldr
Use thUSD protocol to mint thUSD against tBTC collateral to pay for some of the DAO’s monthly expenses.

Proposal
Convert $400k T into tBTC each month and add that tBTC as collateral to a vault on the thUSD protocol to mint $160k thUSD (with a safe 250% collateralization ratio). Use the minted thUSD to pay part of the DAO’s monthly expenses.

Benefits
Today the DAO pays expenses, including collaborator compensations, with T from the treasury. This is a pretty straightforward operation and each collaborator gets exposure to T. It also implies that the treasury gets depleted by ~$300k each month.

If instead, the DAO buys tBTC each month and borrows against it to pay expenses, the benefits would be:

- T gets dollar-cost averaged (DCA) into BTC: DCA is an investment strategy where an investor divides the total amount to be invested across periodic purchases of a target asset. This strategy aims to reduce the impact of volatility on the overall purchase, removes the pressure to make perfect timing decisions, as investments are made consistently regardless of market conditions and particularly in volatile markets can result in a lower average cost per share compared to lump-sum investing.
- Treasury gets diversified, an overall long-term goal of the treasury guild to build a more resilient treasury where capital is best preserved.
- Thresholds’ own thUSD protocol gets used by Threshold, a solid use case example and strong marketing message for the whole market.
- Getting pai

====================================================================================================
[109] id=0x766924ce1f1c9e620d9b389f232fd7c6fc6d42f406175cfe37975a9d15c82652  token=T  space=threshold.eth  date=2024-07-01
TITLE: TIP-082: TTG Betastaker reimbursement and tBTC Redemption Fees Mint and Transfer
CHOICES: Yes | No | Abstain
TEXT (first 1500 characters):
This proposal has 3 purposes:
1) Reimburse the Threshold Treasury Guild for T tokens delegated to Beta Stakers.
2) Mint ~10 tBTC from Bridge Redemption Fees and transfer to the Treasury Guild.
3) Act as retroactive confirmation of TIP-067 delegation.
See full proposal on Forum for details.

====================================================================================================
[110] id=0xffc84c30933947f32e8d50c8ce8707a24725066a8b120d1fde5f47359ba09f1f  token=T  space=threshold.eth  date=2024-08-13
TITLE: Treasury Guild Committee election (epoch 6)
CHOICES: East | Ramaruro | Figue | Bakhrom (kholbakh) | Wailoaloa
TEXT (first 1500 characters):
The Treasury Guild Committee has 9 seats.
The top 4 nominees by vote weight will be appointed for a 12-month term upon expiration of this snapshot vote.
You may split your vote among candidates.
Candidate nominations are on the Forum here: https://forum.threshold.network/t/gp-039-threshold-treasury-guild-nominations-election-epoch-6-2024/903?u=johnpackel

Rules for the elections are available here:
https://forum.threshold.network/t/tip-31-rules-for-guild-committee-elections-and-management/378

====================================================================================================
[111] id=0x6deb2f6f58e49c58c6009ef54a01ac52334e0aa4dd0677a73b653fb6485ee05b  token=T  space=threshold.eth  date=2024-09-03
TITLE: TIP-084 - Changing the tBTC reward calculation to daily eligibility
CHOICES: Approve | Decline | Abstain
TEXT (first 1500 characters):
https://forum.threshold.network/t/tip-084-changing-the-tbtc-reward-calculation-to-daily-eligibility/916

====================================================================================================
[112] id=0x702440c189ef78e906365748a78a233f347ef2c5b6774b6a01d4f9fdb2087955  token=T  space=threshold.eth  date=2024-12-13
TITLE: TIP-93 part 1: tBTC mint fee options
CHOICES: Keep tBTC mint fee at 0% | Set tBTC mint fee to 0.05% | Set tBTC mint fee to 0.1%
TEXT (first 1500 characters):
Following extensive deliberation by Threshold Treasury committee and then the community (see Forum discussion in link below), **this is the first of 4 snapshots** that cover the facets to be decided (mint fee, redeem fee, Treasury committee authorization, 30-day delay for fee changes), while avoiding inevitable "split votes" by trying to combine them.

First two votes are *weighted votes*, which allow voters to express support for more than one option and specify how much they support each of them (explanation here: https://docs.snapshot.box/user-guides/proposals/voting-types#weighted-voting).

====================================================================================================
[113] id=0xc7331a9d2b67602899d2176c0ba4ceaf31b256d7682c309244a24258d9c00b1c  token=T  space=threshold.eth  date=2024-12-13
TITLE: TIP-93 part 2: tBTC redeem fee options
CHOICES: Keep redeem fee at 0.2% | Reduce redeem fee to 0.15% | Increase redeem fee to 0.25%
TEXT (first 1500 characters):
Following extensive deliberation by Threshold Treasury committee and then the community (see Forum discussion in link below), **this is the **second** of 4 snapshots** that cover the facets to be decided (mint fee, redeem fee, Treasury committee authorization, 30-day delay for fee changes), while avoiding inevitable "split votes" by trying to combine them.

First two votes are *weighted votes*, which allow voters to express support for more than one option and specify how much they support each of them (explanation here: https://docs.snapshot.box/user-guides/proposals/voting-types#weighted-voting).

====================================================================================================
[114] id=0x6ccdf055ee0d781289ae1b74a0f58fa20336eeca169fa22beb2e55b7354f1645  token=T  space=threshold.eth  date=2024-12-13
TITLE: TIP-93 part 3: give Treasury committee discretion to adjust tBTC fees
CHOICES: Yes - grant committee discretion | No - | Abstain
TEXT (first 1500 characters):
Following extensive deliberation by Threshold Treasury committee and then the community (see Forum discussion in link below), **this is the 3rd of 4 snapshots** that cover the facets to be decided (mint fee, redeem fee, Treasury committee authorization, 30-day delay for fee changes), while avoiding inevitable "split votes" by trying to combine them.

Per Forum discussion, some tokenholders favor authorizing the elected Treasury committee discretion to adjust tBTC mint and/or redeem fees. The stated rationale in TIP-75 tBTC Bridge fee holiday part 2 was: "Moreover, in an effort to ensure a faster reaction time and greater flexibility in adapting to rapidly changing market conditions, we propose that the Treasury Guild be granted the authority for six (6) months to direct the Threshold Council to adjust fee parameters. By delegating this decision to the Treasury Guild Committee it will allow for a more agile and responsive adjustment of fees in line with market fluctuations." 

In order to provide a range of options should tokenholders vote here to approve some form of committee discretion, while avoiding malformed choices leading to split votes, **this vote addresses the basic question first.** If approved, another vote will follow after Forum alignment on options.

====================================================================================================
[115] id=0x192a94daff67da5401e1ebf461903c7cb94138fc352214468a7e532af37a9845  token=T  space=threshold.eth  date=2024-12-13
TITLE: TIP-93 part 4: mandatory 30-day delay on fee changes
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Following extensive deliberation by Threshold Treasury committee and then the community (see Forum discussion in link below), **this is the last of 4 snapshots** that cover the facets to be decided (mint fee, redeem fee, Treasury committee authorization, 30-day delay for fee changes), while avoiding inevitable "split votes" by trying to combine them.

The Treasury committee recommended a 30-day delayed implementation should TIP-93 be approved, stating: "We include a 30-day delayed implementation following Snapshot vote results, partly to give the market time to respond and as a consideration for those in favor of continuing the mint fee holiday..."

In this Forum comment, MrsNuBooty said, "I strongly recommend implementing a mandatory 30-day delay between any decision to adjust fees and their implementation. This gives the market adequate time to respond, ensures fairness to current users, and provides time to communicate changes effectively."
https://forum.threshold.network/t/tip-93-reinstate-tbtc-mint-fee-increase-redeem-fee/987/4?u=johnpackel

**Question: should we impose a mandatory 30-day delay to tBTC fee changes? **

To be clear, if approved this would apply to any fee changes tokenholders may approve in TIP-93 part 1 & part 2 snapshots, as well as future changes.

====================================================================================================
[116] id=0xd538fd95935ef436a5167fe8d39a91e384fc3147598472ae0ff838a5bfa10b34  token=T  space=threshold.eth  date=2025-01-10
TITLE: TIP-96: Mint 5% of T supply for TVL growth milestones
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Vote Type

Token Holder DAO Snapshot

DAO-elected Sponsors

@JohnPackel , @Eastban

Timeline

   - 7 days for comment / discussion on this proposal
   - Token holder DAO Snapshot with a 7-day vote period
   - If approved, 9 days for Governor Bravo vote (+ 4 days queue & timelock)

Who is Involved?

Threshold DAO, Threshold Treasury Committee, aligned liquidity provider(s)

Highlights

    Accelerate tBTC usage and TVL by engaging active trading firms
    Performance-based T token grants totaling up to 5% of current supply
    Delegation to Treasury Committee the agreement on and monitoring of performance milestones

Details

While centralized wrapped Bitcoin products continue to be released and some decentralized versions struggle or face delayed launches, tBTC is the oldest decentralized Bitcoin to DeFi bridge, approaching the 5-year mark of secure, trust-minimized activity – and increased utility to the community through adoption on major lending protocols like Aave, direct minting on Arbitrum (with Base and other L2s in development), stablecoin borrowing via ThresholdUSD and more.

tBTC has seen significant growth the last six months, particularly since August when many holders of WBTC expressed concern over its custody changes by dramatically increasing unmints. We are approaching 16,000 tBTC minted since January 2023, and more than 11,000 has been unminted.

The goal of this proposal is to accelerate that growth substantially by engaging one or more experienced trading f

====================================================================================================
[117] id=0xc80ddd25510430db366f866950f134a01b374794fc53bfd865ba39faa083a1b0  token=T  space=threshold.eth  date=2025-01-17
TITLE: TIP-098: The Future of Threshold
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**Introducing tLabs**
tLabs is a proposed labs company with the single purpose of developing and maintaining tBTC and Threshold Network. This proposal outlines the role of tLabs in the Threshold community, its relationship to the DAO, and the strategy to ensure the long-term growth and success of Threshold DAO.

This proposal is motivated by a clear need to address the core challenges facing Threshold and tBTC:

- Stalled tBTC product and technical development
- Growth coordination challenges and unclear market position
- Undercapitalization and runway
- Limited tokenomic model.

It is proposed that tLabs lead protocol, product, business development and marketing functions for tBTC.

High-level goals of tLabs include:

- Increased tBTC TVL and bridge velocity
- Upgraded tBTC core technology
- Developed tBTC product and usability.

To fund this endeavour, tLabs will conduct a fundraise on behalf of Threshold DAO, with the outcomes of an extended runway for Threshold DAO, funding for tLabs, and the further decentralization of Threshold Network by engaging aligned investors.

**The Future of Threshold**
Threshold Network operates the most secure, most decentralized Bitcoin bridge in the market, and tBTC has the potential to become the canonical BTC token. A recent surge of interest in Bitcoin makes now the time to secure Threshold’s position.

How do we do it?

Let’s start by understanding where we are now.

tBTC development has stalled because of competing priorities in the pre

====================================================================================================
[118] id=0xd334afe182b0aa6aee48c4df3668ad5fe68c2983ed3f914bf2477ab3d937ca82  token=T  space=threshold.eth  date=2025-02-05
TITLE: amended TIP-092: Make T Great Again, Part 1
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**Please note the 2 amendments to this TIP, as posted in comment on the TIP-92 Forum thread for feedback:**

1. No immediate change to TACo rewards. TIP-100 outlines a transition plan that is being actively developed, and tokens minted in TIP-94 are sufficient for “TACo stakers will continue to be compensated for their availability and service provision for at least six months”.
2. tBTC rewards will end February 15 as described in TIP-100. Upon passage of TIP-92, tBTC stakers may begin the unstake process, and the 45-day cooldown requirement is waived. Development work is underway to allow those who unstake to claim their T soon after Feb. 15, and we will post an update here confirming the date.

**Also note:**

- This [comment from MacLane](https://forum.threshold.network/t/tip-100-the-future-of-threshold-continued/1033/24?u=johnpackel) on TIP-100: “Given the imminent movement of TIP-92 to Snapshot, it’s important to clarify that that I view TIP-100 as the critical package for success, not an a la carte menu of options to selectively approve or reject (i.e. TIP-92 is a requirement for TIP-100). Please keep in mind that context while evaluating your decision.

- This TIP’s references to TIP-100, which among other things include this articulation of TACo rewards [in comment here](https://forum.threshold.network/t/tip-100-the-future-of-threshold-continued/1033/20?u=johnpackel): "TACo’s destination will be researched, designed and presented over the coming months. The utmost pri

====================================================================================================
[119] id=0x37e4917f506d716e00f74d7aa2252fbe0a028c3c3df9432bbc57c5c3a90f3c91  token=T  space=threshold.eth  date=2025-02-11
TITLE: TIP-100: The Future of Threshold, Continued
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
This TIP is a continuation of TIP-98 that expands on the role of tLabs and the expected DAO restructure. Given the meaningful updates and changes from the original TIP, it is re-introduced as TIP-100, rather than an amendment.

tBTC has an opportunity to become the canonical cross-chain liquidity hub for Bitcoin, with >10x today’s TVL and bridge velocity. Threshold can capture value with revamped tokenomics that couple the success of T with the success of tBTC. But achieving this goal requires the DAO to commit and compete: the path to success is narrow and requires immediate action.

Threshold currently lacks strategic focus and the internal structure necessary to successfully execute in an increasingly competitive market. To remedy this, tLabs will lead a DAO reorganization with a singular focus on scaling tBTC TVL and bridge velocity, while pivoting the network to profitability and cutting distractions that don’t directly contribute to winning.

**Threshold as a single app network for tBTC**
Threshold was originally envisioned as a multi-application threshold cryptography network. Unfortunately, this has introduced a significant amount of complexity, making internal alignment and external messaging around Threshold’s purpose extremely difficult.

To provide clarity of purpose and maximize the likelihood of success for both applications, TACo and tBTC will become separate networks **with the end of staking emissions (TIP-92) by February 15 **(with a small carveout for TACo)

====================================================================================================
[120] id=0x0c83560eb8275ae7b5dd645ef73f4824561b7c9699ead00ea11fe78e33f1f885  token=T  space=threshold.eth  date=2025-03-15
TITLE: TIP-103: Restructuring of Threshold DAO committees and roles
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
*[please see Forum post for the screenshots of the financials]*

DAO Elected Representative Sponsors: @JohnPackel @Eastban @Luna5 @Vict0r @MrsNuBooty

Key provisions
TIP-100 called for sunsetting existing committees and restructuring DAO roles to reflect Threshold Labs taking over tBTC development & growth per TIP-098
This TIP is the recommendation of the DAO restructuring workgroup based on evaluation of responsibilities remaining with the DAO
The treasury, security and oversight committee called for in TIP-100, combining the responsibilities of the Treasury Committee and Council, will be the “Threshold Committee”
The Threshold Committee will consist of 6 part-time paid seats and 3 volunteer seats, retaining the 5-of-9 threshold for multisig security
5 part-time contributor roles remain (hours reduced from current): treasury operations, tech support, communications/engagement/education, project management, incentives/reporting
Total cost for Committee and part-time roles will be $602k annually, a reduction of ~$1.1 million from current payroll
Streamlining operations and reducing cost substantially will minimize the treasury selling T tokens, allowing the DAO to be a net purchaser of T by implementing “buyback and make”
Treasury assets plus 30% of projected revenue can cover ~23 months of our obligations paid in stablecoins, with $10.6M in T remaining to cover ~$1.6M annual protocol & incentives cost
A detailed plan with timing is outlined, reflecting the need to transition

====================================================================================================
[121] id=0x6d15c307e70d1810ed0ae164ed90764d4b9787907d438b03be688667f9b7b73d  token=T  space=threshold.eth  date=2025-05-21
TITLE: TIP-104: Threshold Labs Year-1 Budget & Milestones
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
**Vote type:** Token holder DAO snapshot, single-choice voting (yes/no/abstain)

**DAO-elected representative sponsors:** @JohnPackel @Eastban

**Timeline:** 7-day discussion period followed by 7-day Snapshot vote

**tl/dr**

- Following tokenholder approval to create Threshold Labs per TIP-98 and TIP-100, tLabs submits a year-1 budget request for $2,850,000
- This number reflects at-cost projections with zero profit margin added
- Proposed milestones by which to measure tLabs success include doubling revenue to 50 tBTC and increasing TVL by 60%, to 7,500 BTC
- tLabs has commenced operations based on $250k fronted by the former Treasury committee, which will be deducted from the total
- The former Treasury committee created an expense payment plan based on estimated tLabs budget; Threshold Committee will update it to reflect the actual

**Purpose**

The stated purpose of creating tLabs was outlined in TIP-100 as addressing core challenges facing Threshold and tBTC: 1) growth coordination challenges and unclear market position, 2) stalled tBTC product and technical development and 3) limited tokenomic model.

Threshold became “default alive” (the protocol and network can operate sustainably and profitably) thanks to significant cost reductions from eliminating emissions (modified TIP-92), discontinuing investment in thUSD and putting it in maintenance mode (TIP-102) and reducing by $1.1million/year the cost of Threshold DAO committees and roles via restructuring in anticipatio

====================================================================================================
[122] id=0x5cd4a83c53c69752c3a64261def974fcda9a5f409056d27710186cc0ebb9649d  token=T  space=threshold.eth  date=2025-09-13
TITLE: TIP-106: Experimenting with a tBTC fee rebate for locking T tokens
CHOICES: For | Against | Abstain
TEXT (first 1500 characters):
Vote Type: Token holder DAO snapshot, single-choice voting (yes/no/abstain)

DAO-elected sponsor: John Packel

Timeline: 7-day discussion period followed by 7-day Snapshot vote

Purpose

Threshold Labs proposes to test the market appetite for an automated, instant bridge-fee rebate based on locking T tokens. We expect that DAO discussion and tLabs delivery of an initial feature will provide valuable learnings for development of mechanisms and tokenomics that more closely tie T value to tBTC success, encourage long-term staking and alignment with tBTC strategy, and improve the tBTC / BTC price peg.

Hypothesis

The introduction of a locked T–based rebate on bridge fees will open new trading opportunities for professional market makers by enabling tBTC / BTC arbitrage with enhanced capital efficiency. By requiring users to lock T in a contract as a prerequisite for rebates, this mechanism will increase demand for T and encourage arbitrageurs to lock significant T positions. In turn, the rebate of bridge fees will reduce tBTC’s persistent ~20+ bps discount to BTC (attributable to the current 20 bps redemption fee) by facilitating more frequent, fee-free redemptions.

Proposed feature: bridge fee rebate for locking T tokens

In the pull request proposed here, users receive an instant rebate on their bridge fees by locking T tokens in a contract. The more you lock, the more your bridge fees are reduced.

Details:

For every 100,000 T an address locks for 30 days, the system enable

====================================================================================================
[123] id=0x55ab722ebbc514df1fa82ecd91fea7d990ad33f75624fb475bf0d363ec64f7ee  token=T  space=threshold.eth  date=2026-02-19
TITLE: TIP-109: Reintroduce a tBTC Mint Fee
CHOICES: For | Against
TEXT (first 1500 characters):
Vote type: Token holder DAO on-chain 7-day vote period

DAO-elected Sponsors: Threshold Committee

tl;dr

This proposal reintroduces a 20 basis point (0.20%) mint fee for tBTC. The redemption fee will remain unchanged, as defined under TIP-075.

The proposal restores a sustainable fee structure now that the mint fee holiday has served its purpose, while maintaining clarity and predictability for users and integrators.

Background
Threshold DAO has adjusted tBTC bridge fees through multiple governance decisions in response to the protocol’s stage of development:

- tBTC v2 initially launched with a 20 bps mint fee and a 20 bps redemption fee.
- TIP-054 reduced mint fee to 10 bps; redemption fee remained unchanged.
- TIP-065 reduced both the mint and redemption fees to 0% with the explicit goal of accelerating adoption, increasing total value locked, and supporting integration across DeFi ecosystems.
- TIP-075 partially concluded the fee holiday by reintroducing the 20 bps redemption fee while maintaining a 0% mint fee.
- TIP-093 rejected proposed fee increases and introduced a mandatory 30-day delay on future tBTC fee changes.

Overall the fee holiday has achieved its intended objectives, contributing to increased tBTC usage, broader integrations and improved liquidity conditions. Importantly, the introduction of fee waivers for fee stakers has strengthened the tBTC price peg and eliminated the relatively persistent price discount attributable to the 20bps redemption fee. Sinc

