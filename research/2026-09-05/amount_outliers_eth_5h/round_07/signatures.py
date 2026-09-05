#!/usr/bin/env python3
"""Extended event-signature table for the transaction-type loop.

Names are structural matches (the topic equals keccak of the signature string), not verified protocol identity.
The pilot decoder (analyze_onchain.SIGNATURES) stays the source for decoded fields; this table only adds family
names, grouped by the mechanism they usually mark. A family that never matches in a day's data costs nothing.
"""
from analyze_onchain import SIGNATURES as BASE, topic

EXTRA = {
    # flash loans
    'MorphoFlashLoan': 'FlashLoan(address,address,uint256)',
    'BalancerFlashLoan': 'FlashLoan(address,address,uint256,uint256)',
    'AaveFlashLoan': 'FlashLoan(address,address,address,uint256,uint8,uint256,uint16)',
    # lending
    'MorphoSupply': 'Supply(bytes32,address,address,uint256,uint256)',
    'MorphoWithdraw': 'Withdraw(bytes32,address,address,address,uint256,uint256)',
    'MorphoBorrow': 'Borrow(bytes32,address,address,address,uint256,uint256)',
    'MorphoRepay': 'Repay(bytes32,address,address,uint256,uint256)',
    'MorphoSupplyCollateral': 'SupplyCollateral(bytes32,address,address,uint256)',
    'MorphoWithdrawCollateral': 'WithdrawCollateral(bytes32,address,address,address,uint256)',
    'MorphoLiquidate': 'Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)',
    'MorphoAccrueInterest': 'AccrueInterest(bytes32,uint256,uint256,uint256)',
    'AaveWithdraw': 'Withdraw(address,address,address,uint256)',
    'AaveReserveDataUpdated': 'ReserveDataUpdated(address,uint256,uint256,uint256,uint256,uint256)',
    'CompoundV3Supply': 'Supply(address,address,uint256)',
    'CompoundV3Withdraw': 'Withdraw(address,address,uint256)',
    'CompoundV3SupplyCollateral': 'SupplyCollateral(address,address,address,uint256)',
    'CompoundV3WithdrawCollateral': 'WithdrawCollateral(address,address,address,uint256)',
    'SparkSupply': 'Supply(address,address,address,uint256,uint16)',
    # DEX
    'BalancerSwap': 'Swap(bytes32,address,address,uint256,uint256)',
    'BalancerPoolBalanceChanged': 'PoolBalanceChanged(bytes32,address,address[],int256[],uint256[])',
    'CurveTokenExchange': 'TokenExchange(address,int128,uint256,int128,uint256)',
    'CurveTokenExchangeU': 'TokenExchange(address,uint256,uint256,uint256,uint256)',
    'CurveTokenExchangeUnderlying': 'TokenExchangeUnderlying(address,int128,uint256,int128,uint256)',
    'CurveAddLiquidity2': 'AddLiquidity(address,uint256[2],uint256[2],uint256,uint256)',
    'CurveAddLiquidity3': 'AddLiquidity(address,uint256[3],uint256[3],uint256,uint256)',
    'CurveAddLiquidityN': 'AddLiquidity(address,uint256[],uint256[],uint256,uint256)',
    'CurveRemoveLiquidity2': 'RemoveLiquidity(address,uint256[2],uint256[2],uint256)',
    'CurveRemoveLiquidity3': 'RemoveLiquidity(address,uint256[3],uint256[3],uint256)',
    'CurveRemoveLiquidityN': 'RemoveLiquidity(address,uint256[],uint256[],uint256)',
    'CurveRemoveLiquidityOne': 'RemoveLiquidityOne(address,uint256,uint256,uint256)',
    'CurveRemoveLiquidityOneI': 'RemoveLiquidityOne(address,int128,uint256,uint256,uint256)',
    'CoWTrade': 'Trade(address,address,address,uint256,uint256,uint256,bytes)',
    'CoWSettlement': 'Settlement(address)',
    'CoWInteraction': 'Interaction(address,uint256,bytes4)',
    'OneInchOrderFilled': 'OrderFilled(bytes32,uint256)',
    'AggregatorSwapped': 'Swapped(address,address,address,address,uint256,uint256)',
    'UniswapXFill': 'Fill(bytes32,address,address,uint256)',
    'ZeroExTransformedERC20': 'TransformedERC20(address,address,address,uint256,uint256)',
    'ZeroExOtcOrderFilled': 'OtcOrderFilled(bytes32,address,address,address,address,uint128,uint128)',
    'ZeroExRfqOrderFilled': 'RfqOrderFilled(bytes32,address,address,address,address,uint128,uint128,bytes32)',
    'ZeroExLimitOrderFilled': 'LimitOrderFilled(bytes32,address,address,address,address,address,uint128,uint128,uint128,uint256,bytes32)',
    'V3IncreaseLiquidity': 'IncreaseLiquidity(uint256,uint128,uint256,uint256)',
    'V3DecreaseLiquidity': 'DecreaseLiquidity(uint256,uint128,uint256,uint256)',
    'V3NFPMCollect': 'Collect(uint256,address,uint256,uint256)',
    'V4Initialize': 'Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)',
    'V2PairCreated': 'PairCreated(address,address,address,uint256)',
    'V3PoolCreated': 'PoolCreated(address,address,uint24,int24,address)',
    'MaverickSwap': 'PoolSwap(address,address,(uint256,bool,bool,uint256,uint256,int32),uint256,uint256)',
    'FluidSwap': 'Swap(bool,uint256,uint256,address)',
    'DODOSwap': 'DODOSwap(address,address,uint256,uint256,address,address)',
    'BancorTokensTraded': 'TokensTraded(bytes32,address,address,uint256,uint256,uint256,uint256,uint256,address)',
    # staking and liquid staking
    'LidoSubmitted': 'Submitted(address,uint256,address)',
    'LidoTransferShares': 'TransferShares(address,address,uint256)',
    'LidoWithdrawalRequested': 'WithdrawalRequested(uint256,address,address,uint256,uint256)',
    'LidoWithdrawalClaimed': 'WithdrawalClaimed(uint256,address,address,uint256)',
    'LidoWithdrawalsFinalized': 'WithdrawalsFinalized(uint256,uint256,uint256,uint256,uint256)',
    'BeaconDeposit': 'DepositEvent(bytes,bytes,bytes,bytes,bytes)',
    'RocketTokensMinted': 'TokensMinted(address,uint256,uint256,uint256)',
    'RocketTokensBurned': 'TokensBurned(address,uint256,uint256,uint256)',
    'EigenDeposit': 'Deposit(address,address,address,uint256)',
    'EigenOperatorSharesIncreased': 'OperatorSharesIncreased(address,address,address,uint256)',
    'EtherFiDeposit': 'Deposit(address,uint256,uint8,address)',
    # stablecoin issuers
    'TetherIssue': 'Issue(uint256)',
    'TetherRedeem': 'Redeem(uint256)',
    'TetherDestroyedBlackFunds': 'DestroyedBlackFunds(address,uint256)',
    'TetherAddedBlackList': 'AddedBlackList(address)',
    'USDCMint': 'Mint(address,address,uint256)',
    'USDCBurn': 'Burn(address,uint256)',
    'USDCBlacklisted': 'Blacklisted(address)',
    'PSMBuyGem': 'BuyGem(address,uint256,uint256)',
    'PSMSellGem': 'SellGem(address,uint256,uint256)',
    'EthenaMint': 'Mint(string,address,address,address,uint256,uint256)',
    'EthenaRedeem': 'Redeem(string,address,address,address,uint256,uint256)',
    # smart accounts and multisig
    'SafeExecutionSuccess': 'ExecutionSuccess(bytes32,uint256)',
    'SafeExecutionFailure': 'ExecutionFailure(bytes32,uint256)',
    'SafeMultiSigTransaction': 'SafeMultiSigTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes,bytes)',
    'SafeModuleSuccess': 'ExecutionFromModuleSuccess(address)',
    'SafeReceived': 'SafeReceived(address,uint256)',
    'SafeSetup': 'SafeSetup(address,address[],uint256,address,address)',
    'ProxyCreation': 'ProxyCreation(address,address)',
    'EntryPointBeforeExecution': 'BeforeExecution()',
    'EntryPointAccountDeployed': 'AccountDeployed(bytes32,address,address,address)',
    'EntryPointDeposited': 'Deposited(address,uint256)',
    'ERC7821Executed': 'Executed(address,uint256,bytes)',
    # bridges and messaging
    'OPTransactionDeposited': 'TransactionDeposited(address,address,uint256,bytes)',
    'OPSentMessage': 'SentMessage(address,address,bytes,uint256,uint256)',
    'OPSentMessageExtension1': 'SentMessageExtension1(address,uint256)',
    'OPETHDepositInitiated': 'ETHDepositInitiated(address,address,uint256,bytes)',
    'OPERC20DepositInitiated': 'ERC20DepositInitiated(address,address,address,address,uint256,bytes)',
    'OPETHBridgeInitiated': 'ETHBridgeInitiated(address,address,uint256,bytes)',
    'OPERC20BridgeInitiated': 'ERC20BridgeInitiated(address,address,address,address,uint256,bytes)',
    'OPETHBridgeFinalized': 'ETHBridgeFinalized(address,address,uint256,bytes)',
    'OPERC20BridgeFinalized': 'ERC20BridgeFinalized(address,address,address,address,uint256,bytes)',
    'OPWithdrawalProven': 'WithdrawalProven(bytes32,address,address)',
    'OPWithdrawalFinalized': 'WithdrawalFinalized(bytes32,bool)',
    'OPRelayedMessage': 'RelayedMessage(bytes32)',
    'ArbInboxMessageDelivered': 'InboxMessageDelivered(uint256,bytes)',
    'ArbMessageDelivered': 'MessageDelivered(uint256,bytes32,address,uint8,address,bytes32,uint256,uint64)',
    'ArbDepositInitiated': 'DepositInitiated(address,address,address,uint256,uint256)',
    'ArbWithdrawalInitiated': 'WithdrawalInitiated(address,address,address,uint256,uint256,uint256)',
    'ArbOutBoxTransactionExecuted': 'OutBoxTransactionExecuted(address,address,uint256,uint256)',
    'ArbBridgeCallTriggered': 'BridgeCallTriggered(address,address,uint256,bytes)',
    'ArbSequencerBatchDelivered': 'SequencerBatchDelivered(uint256,bytes32,bytes32,bytes32,uint256,(uint64,uint64,uint64,uint64),uint8)',
    'PolygonLockedEther': 'LockedEther(address,address,uint256)',
    'PolygonLockedERC20': 'LockedERC20(address,address,address,uint256)',
    'PolygonExitedEther': 'ExitedEther(address,uint256)',
    'PolygonExitedERC20': 'ExitedERC20(address,address,uint256)',
    'PolygonStateSynced': 'StateSynced(uint256,address,bytes)',
    'PolygonNewHeaderBlock': 'NewHeaderBlock(address,uint256,uint256,uint256,uint256,bytes32)',
    'AcrossV3FundsDeposited': 'V3FundsDeposited(address,address,uint256,uint256,uint256,uint32,uint32,uint32,uint32,address,address,address,bytes)',
    'AcrossFundsDeposited': 'FundsDeposited(bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,uint32,bytes32,bytes32,bytes32,bytes)',
    'AcrossFilledV3Relay': 'FilledV3Relay(address,address,uint256,uint256,uint256,uint256,uint32,uint32,uint32,address,address,address,address,bytes,(address,bytes,uint256,uint8))',
    'AcrossFilledRelay': 'FilledRelay(bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,uint32,bytes32,bytes32,bytes32,bytes32,bytes,(bytes32,bytes,uint256,uint8))',
    'LZPacketSent': 'PacketSent(bytes,bytes,address)',
    'LZPacketDelivered': 'PacketDelivered((uint32,bytes32,uint64),address)',
    'OFTSent': 'OFTSent(bytes32,uint32,address,uint256,uint256)',
    'OFTReceived': 'OFTReceived(bytes32,uint32,address,uint256)',
    'CCTPDepositForBurn': 'DepositForBurn(uint64,address,uint256,address,bytes32,uint32,bytes32,bytes32)',
    'CCTPv2DepositForBurn': 'DepositForBurn(address,uint256,address,bytes32,uint32,bytes32,bytes32,uint256,uint32,bytes)',
    'CCTPMessageSent': 'MessageSent(bytes)',
    'CCTPMintAndWithdraw': 'MintAndWithdraw(address,uint256,address)',
    'CCTPv2MintAndWithdraw': 'MintAndWithdraw(address,uint256,address,uint256)',
    'WormholeLogMessagePublished': 'LogMessagePublished(address,uint64,uint32,bytes,uint8)',
    'LineaMessageSent': 'MessageSent(address,address,uint256,uint256,uint256,bytes,bytes32)',
    'ScrollQueueTransaction': 'QueueTransaction(address,address,uint256,uint64,uint256,bytes)',
    'ScrollSentMessage': 'SentMessage(address,address,uint256,uint256,uint256,bytes)',
    'ScrollDepositETH': 'DepositETH(address,address,uint256,bytes)',
    'ScrollDepositERC20': 'DepositERC20(address,address,address,address,uint256,bytes)',
    'ZkSyncNewPriorityRequest': 'NewPriorityRequest(uint256,bytes32,uint64,(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256[4],bytes,bytes,uint256[],bytes,bytes),bytes[])',
    'StarknetLogMessageToL2': 'LogMessageToL2(address,uint256,uint256,uint256[],uint256,uint256)',
    'HopTransferSent': 'TransferSentToL2(uint256,address,uint256,uint256,uint256,address,uint256)',
    'SynapseTokenDeposit': 'TokenDeposit(address,uint256,address,uint256)',
    'SocketBridge': 'SocketBridge(uint256,address,uint256,bytes32,address,address,bytes32)',
    'LiFiTransferStarted': 'LiFiTransferStarted((bytes32,string,string,address,address,address,address,uint256,uint256,bool,bool))',
    'LiFiGenericSwapCompleted': 'LiFiGenericSwapCompleted(bytes32,string,string,address,address,address,address,uint256,uint256)',
    # NFT markets
    'SeaportOrderFulfilled': 'OrderFulfilled(bytes32,address,address,address,(uint8,address,uint256,uint256)[],(uint8,address,uint256,uint256,address)[])',
    'BlurOrdersMatched': 'OrdersMatched(address,address,(address,uint8,address,address,uint256,uint256,address,uint256,uint256,uint256,(uint16,address)[],uint256,bytes),bytes32,(address,uint8,address,address,uint256,uint256,address,uint256,uint256,uint256,(uint16,address)[],uint256,bytes),bytes32)',
    # oracles and misc
    'ChainlinkAnswerUpdated': 'AnswerUpdated(int256,uint256,uint256)',
    'ChainlinkNewTransmission': 'NewTransmission(uint32,int192,address,int192[],bytes,bytes32)',
    'ChainlinkTransmitted': 'Transmitted(bytes32,uint32)',
    'OwnershipTransferred': 'OwnershipTransferred(address,address)',
    'Upgraded': 'Upgraded(address)',
    'Paused': 'Paused(address)',
    'Unpaused': 'Unpaused(address)',
    'ERC721ApprovalForAll': 'ApprovalForAll(address,address,bool)',
    'ERC20TransferWithData': 'Transfer(address,address,uint256,bytes)',
    'ERC777Sent': 'Sent(address,address,address,uint256,bytes,bytes)',
    'ERC777Minted': 'Minted(address,address,uint256,bytes,bytes)',
    'ERC777Burned': 'Burned(address,address,uint256,bytes,bytes)',
    'ENSNameRegistered': 'NameRegistered(string,bytes32,address,uint256,uint256,uint256)',
    'GnosisAuctionNewOrder': 'NewSellOrder(uint256,uint64,uint96,uint96)',
    'WithdrawalRequest': 'WithdrawalRequest(address,uint256)',
    'ClaimRewards': 'ClaimRewards(address,uint256)',
    'RewardPaid': 'RewardPaid(address,uint256)',
    'Staked': 'Staked(address,uint256)',
    'Withdrawn': 'Withdrawn(address,uint256)',
    'DepositAU': 'Deposit(address,uint256)',
    'WithdrawAU': 'Withdraw(address,uint256)',
    'DepositAAU': 'Deposit(address,address,uint256)',
    'WithdrawAAU': 'Withdraw(address,address,uint256)',
    'ERC4626DepositAlt': 'Deposit(address,address,uint256,uint256)',
    'TokenExchangeLog': 'Exchange(address,address,uint256,uint256)',
    'Claimed': 'Claimed(address,uint256)',
    'ClaimedIAU': 'Claimed(uint256,address,uint256)',
    'Distribution': 'Distribution(address,uint256)',
    'PermitTransfer': 'Permit(address,address,address,uint160,uint48,uint48)',
    'MetaMorphoUpdateLastTotalAssets': 'UpdateLastTotalAssets(uint256)',
    'AccrueInterest2': 'AccrueInterest(uint256,uint256)',
    'MorphoSetAuthorization': 'SetAuthorization(address,address,address,bool)',
    'PendleSwap': 'Swap(address,address,int256,int256,uint256,uint256)',
    'PendleMint': 'Mint(address,uint256,uint256,uint256)',
    'SparkPoolWithdraw': 'Withdraw(address,uint256,address,address)',
    'ReserveUsedAsCollateralEnabled': 'ReserveUsedAsCollateralEnabled(address,address)',
    'ReserveUsedAsCollateralDisabled': 'ReserveUsedAsCollateralDisabled(address,address)',
    'AaveMintedToTreasury': 'MintedToTreasury(address,uint256)',
    'AaveScaledMint': 'Mint(address,address,uint256,uint256,uint256)',
    'AaveScaledBurn': 'Burn(address,address,uint256,uint256,uint256)',
    'AaveBalanceTransfer': 'BalanceTransfer(address,address,uint256,uint256)',
    'LiquidationCallV2': 'LiquidationCall(address,address,address,uint256,uint256,address,bool)',
    'Sync3': 'Sync(uint256,uint256)',
    'Fees': 'Fees(address,uint256,uint256)',
    'ContractCreated': 'ContractCreated(address)',
    'Deployed': 'Deployed(address,address)',
    'SafeNonce': 'SafeSetup(address,address[],uint256,address,address)',
}

ALL = dict(BASE)
for k, v in EXTRA.items():
    ALL.setdefault(k, v)
TOPICS = {}
for name, signature in ALL.items():
    TOPICS.setdefault(topic(signature), name)
# Promoted from the five-hour packet investigation; unfamiliar emitters still need protocol identity checks.
TOPICS.update({
    topic('RelayErc20Deposit(address,address,uint256,bytes32)'): 'RelayErc20Deposit',
    topic('RelayNativeDeposit(address,uint256,bytes32)'): 'RelayNativeDeposit',
    topic('RelayCallExecuted(bytes32,(address,bytes,uint256,bool))'): 'RelayCallExecuted',
    '0x18081cde2fa64894914e1080b98cca17bb6d1acf633e57f6e26ebdb945ad830b': 'AsterDepositObserved',
    '0xfe7813e2866053d5c3938554e517b554fce6666a6561bed9eaa7419b29fa9b68': 'AsterWithdrawalObserved',
    '0x192442a2b2adb6a7948f097023cb6b57d29d3a7a5dd33e6666d33c39cc456f32': 'CCIPMessageSentObserved',
})

DSNOTE_TAIL = '0' * 56


def family(log):
    """Family name for any log: pilot decoder first, then the extended table, then DSNote, else 'unknown'."""
    ts = log.get('topics') or []
    if not ts:
        return 'anonymous'
    name = TOPICS.get(ts[0])
    if name:
        return name
    if ts[0].endswith(DSNOTE_TAIL) and len(ts) == 4:
        return 'DSNote'
    return 'unknown'


if __name__ == '__main__':
    import json, sys
    seen = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    hits = {t: n for t, n in TOPICS.items() if t in seen}
    print(json.dumps({'signatures': len(ALL), 'matched_observed': len(hits), 'unmatched_observed': len(seen) - len(hits)}))
    for t, n in sorted(hits.items(), key=lambda kv: -seen[kv[0]]):
        print(seen[t], n, t)
