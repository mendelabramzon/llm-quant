#!/usr/bin/env python3
"""Registry of transaction types: what happens qualitatively, how to recognise it quantitatively, how to investigate it.

Each entry is one type. `rule` is a deterministic predicate over a transaction context (see tx_types.Ctx); the first
matching entry in order wins, so specific mechanisms come before generic shapes. `method` names the known investigation
run by tx_types.classify for every occurrence. `origin` records which loop iteration and evidence produced the entry.
The LLM step adds or edits entries here after investigating the residue; the human reviews the diff.

Actor tags come from the window-wide profile of an address (tx_types.scan: addresses.json.gz). They are quantitative
proxies, not identities: 'hot_wallet' means an address that sent to many distinct destinations and received from many
sources over the window, which is what an exchange hot wallet does, but a payroll or a distribution bot can do it too.
"""
from decimal import Decimal


def actor_tags(p):
    """Tags of one address from its window-wide profile (None when the address touched no large transaction)."""
    if p is None:
        return set()
    tags = set()
    sent, to_d, in_d, out_d = p['sent'], p['to_distinct'], p['in_from_distinct'], p['out_to_distinct']
    if sent >= 100 and to_d >= 50:
        tags.add('hot_wallet')          # sends to many distinct destinations: withdrawal processing
    if in_d >= 50:
        tags.add('many_sources')        # receives from many distinct addresses: deposits or sweeps land here
    if sent >= 30 and to_d <= 3:
        tags.add('bot_sender')          # many transactions, one or two destinations: an automated caller
    if p['nonce_max'] is not None and p['nonce_max'] >= 50000:
        tags.add('very_high_nonce')
    if p['nonce_min'] is not None and p['nonce_min'] <= 1:
        tags.add('fresh')               # first or second transaction ever in the window
    if sent == 0:
        tags.add('never_sends')
    if p['pool_swaps'] > 0:
        tags.add('pool')
    if p['swaps_as_to'] >= 20:
        tags.add('router_like')         # called directly by many swapping transactions
    if Decimal(p['flash_lent_usd']) > 0:
        tags.add('flash_lender')
    if in_d <= 3 and out_d == 1 and sent >= 1 and all(abs(Decimal(v)) < Decimal(1000) for v in p['net'].values()) and any(Decimal(v) >= 10000 for v in p['gross'].values()):
        tags.add('pass_through')        # receives from few, forwards everything to one address: a deposit address being swept
    if p['as_to'] >= 20 and sent == 0:
        tags.add('contract_like')       # called by many, never sends: almost certainly code
    return tags


EXCHANGE = {'hot_wallet', 'many_sources'}
BRIDGE_OUT = {'OPTransactionDeposited', 'OPETHDepositInitiated', 'OPERC20DepositInitiated', 'OPETHBridgeInitiated', 'OPERC20BridgeInitiated',
              'ArbInboxMessageDelivered', 'ArbDepositInitiated', 'PolygonLockedEther', 'PolygonLockedERC20', 'ScrollQueueTransaction', 'ScrollDepositETH',
              'ScrollDepositERC20', 'LineaMessageSent', 'ZkSyncNewPriorityRequest', 'StarknetLogMessageToL2', 'CCTPDepositForBurn', 'CCTPv2DepositForBurn',
              'AcrossV3FundsDeposited', 'AcrossFundsDeposited', 'LZPacketSent', 'OFTSent', 'WormholeLogMessagePublished', 'HopTransferSent',
              'SynapseTokenDeposit', 'SocketBridge', 'LiFiTransferStarted'}
BRIDGE_IN = {'OPWithdrawalFinalized', 'OPETHBridgeFinalized', 'OPERC20BridgeFinalized', 'OPRelayedMessage', 'ArbOutBoxTransactionExecuted', 'PolygonExitedEther',
             'PolygonExitedERC20', 'CCTPMintAndWithdraw', 'CCTPv2MintAndWithdraw', 'OFTReceived', 'LZPacketDelivered', 'AcrossFilledV3Relay', 'AcrossFilledRelay'}
LIQ_ADD = {'V3Mint', 'V3IncreaseLiquidity', 'V2Mint', 'CurveAddLiquidity2', 'CurveAddLiquidity3', 'CurveAddLiquidityN'}
LIQ_REMOVE = {'V3Burn', 'V3DecreaseLiquidity', 'V3Collect', 'V3NFPMCollect', 'V2Burn', 'CurveRemoveLiquidity2', 'CurveRemoveLiquidity3', 'CurveRemoveLiquidityN',
              'CurveRemoveLiquidityOne', 'CurveRemoveLiquidityOneI'}
INTENT = {'CoWTrade', 'UniswapXFill', 'OneInchOrderFilled', 'ZeroExOtcOrderFilled', 'ZeroExRfqOrderFilled', 'ZeroExLimitOrderFilled'}
STABLES = {'USDT', 'USDC', 'DAI', 'USDS', 'USDe', 'PYUSD', 'USD1', 'RLUSD', 'FDUSD', 'TUSD', 'USDP', 'FRAX', 'frxUSD', 'USDtb', 'GHO', 'crvUSD', 'LUSD', 'USD0'}


def T(id, group, name, what, rule, rule_text, method, origin, quant_notes=''):
    return {'id': id, 'group': group, 'name': name, 'what': what, 'rule': rule, 'rule_text': rule_text, 'method': method, 'origin': origin,
            'quant_notes': quant_notes}


PILOT = 'pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC)'
SEED = 'seeded 2026-09-05 from event shapes, before the window run'

TYPES = [
    # ---- MEV and atomic strategies
    T('sandwich_attack', 'mev', 'sandwich-pattern candidate',
      'A bot places a swap in a pool immediately before a stranger\'s swap in the same direction and reverses it immediately after, in the same block, '
      'taking the price move the victim causes. The front and back legs are separate transactions from the same actor.',
      lambda c: any(s['role'] in ('front', 'back') for s in c.r.get('sw', [])),
      'same block, same pool: actor swaps direction d at index i, a stranger swaps d at index k, the actor swaps -d at index j > k (scan marks front/back)',
      'sandwich', SEED),
    T('sandwich_victim', 'mev', 'swap inside sandwich-pattern candidate',
      'A user swap that a sandwich bot bracketed in the same block; the user got a worse price than the pool showed before the block.',
      lambda c: any(s['role'] == 'victim' for s in c.r.get('sw', [])) and c.r['swaps'] >= 1,
      'swap in a pool between the front and back legs of a sandwich (scan marks victim)', 'swap', SEED),
    T('flash_loan_arbitrage', 'mev', 'flash-loan-funded swap strategy',
      'A bot borrows a large amount of one asset for the duration of one transaction, trades through several pools, repays the loan and keeps a small '
      'difference. The loan size says nothing about the economic size of the trade.',
      lambda c: c.flash > 0 and c.r['swaps'] >= 1,
      'a flash-loan pair (same asset lent and repaid between the same two parties inside the transaction) and at least one swap event',
      'flash_loan', PILOT + ' #3, #8'),
    T('flash_loan_other', 'mev', 'flash loan without a swap',
      'A flash loan used for something other than a pool trade: a collateral swap, a self-liquidation, a debt refinance, or a balance check.',
      lambda c: c.flash > 0, 'a flash-loan pair and no swap event', 'flash_loan', SEED),
    T('atomic_arbitrage', 'mev', 'positive observed-net multi-pool strategy',
      'A bot contract trades through two or more pools in one transaction and ends with more of one asset and no less of any other: a price '
      'difference between pools captured with the bot\'s own inventory.',
      lambda c: c.r['swaps'] >= 2 and len(c.r['pools']) >= 2 and c.flash == 0 and c.pnet and all(v >= 0 for v in c.pnet.values()) and any(v > 0 for v in c.pnet.values())
      and not c.r['fnet'],
      'two or more swap events across two or more pools, no flash loan, the principal contract nets >= 0 in every priced asset and > 0 in one, the EOA nets nothing',
      'arbitrage', SEED),
    # ---- stablecoin issuance and par conversions
    T('stablecoin_mint', 'stablecoin', 'stablecoin issuance',
      'The issuer creates new supply: tokens appear from the zero address, usually into the issuer\'s treasury, and reach the market in later transactions.',
      lambda c: any(s in STABLES and Decimal(a) >= c.thr for s, (a, b) in c.r['mb'].items()) and c.r['swaps'] == 0 and c.flash == 0,
      'a registry stablecoin transferred from the zero address for at least the threshold, no swap, no flash loan', 'mint_burn', PILOT + ' (USDS mint inside the PSM path)'),
    T('stablecoin_burn', 'stablecoin', 'stablecoin redemption',
      'Supply is destroyed: tokens go to the zero address, the issuer having received them from a redeeming customer earlier.',
      lambda c: any(s in STABLES and Decimal(b) >= c.thr for s, (a, b) in c.r['mb'].items()) and c.r['swaps'] == 0 and c.flash == 0,
      'a registry stablecoin transferred to the zero address for at least the threshold, no swap, no flash loan', 'mint_burn', SEED),
    T('psm_conversion', 'stablecoin', 'par conversion through a peg-stability module',
      'A user exchanges one dollar stablecoin for another at exactly 1:1 through a protocol reserve (Sky PSM: USDS or DAI against USDC), '
      'typically burning one and drawing the other from a pocket; fee zero or a few basis points.',
      lambda c: c.has('PSMBuyGem', 'PSMSellGem') or (c.has('DSNote') and 'USDC' in c.assets and ({'DAI', 'USDS'} & c.assets) and c.r['mb']),
      'BuyGem/SellGem event, or DSNote events with USDC and DAI/USDS legs and a mint or burn', 'psm', PILOT + ' #6'),
    T('wrapped_btc_mint_burn', 'stablecoin', 'wrapped BTC issuance or redemption',
      'A custodian or bridge mints or burns a BTC-backed token (WBTC, cbBTC, tBTC, LBTC) against bitcoin moved off-chain.',
      lambda c: any(s in ('WBTC', 'cbBTC', 'tBTC', 'LBTC') and (Decimal(a) >= c.thr or Decimal(b) >= c.thr) for s, (a, b) in c.r['mb'].items()) and c.r['swaps'] == 0,
      'a BTC wrapper minted from or burned to the zero address for at least the threshold, no swap', 'mint_burn', SEED),
    # ---- staking
    T('lido_stake', 'staking', 'ETH staked with Lido',
      'ETH is sent to the Lido pool and stETH is minted to the sender; from here the ETH is queued for validators.',
      lambda c: c.has('LidoSubmitted'), 'Submitted event', 'generic', SEED),
    T('lido_withdrawal', 'staking', 'Lido withdrawal request or claim',
      'A stETH holder asks to exit (stETH locked, a request NFT issued) or claims finalized ETH.',
      lambda c: c.has('LidoWithdrawalRequested', 'LidoWithdrawalClaimed'), 'WithdrawalRequested or WithdrawalClaimed event', 'generic', SEED),
    T('wsteth_wrap_unwrap', 'staking', 'stETH wrapped or unwrapped',
      'stETH is exchanged for wstETH (or back) at the current share rate; a wallet changes the form of its staked ETH, usually before a DeFi deposit.',
      lambda c: any(l['s'] == 'wstETH' and (l['f'] == c.ZERO or l['r'] == c.ZERO) for l in c.r['legs']) and 'stETH' in c.assets and c.r['swaps'] == 0,
      'wstETH minted or burned with a stETH leg and no swap', 'generic', SEED),
    T('beacon_deposit', 'staking', 'validator deposit',
      'ETH is deposited into the beacon deposit contract to activate or top up validators.',
      lambda c: c.has('BeaconDeposit'), 'DepositEvent from the deposit contract', 'generic', SEED),
    T('restaking_or_lst_other', 'staking', 'other liquid-staking or restaking operation',
      'Minting or burning of rETH, cbETH, weETH, or a deposit into EigenLayer or ether.fi.',
      lambda c: c.has('RocketTokensMinted', 'RocketTokensBurned', 'EigenDeposit', 'EtherFiDeposit') or
      any(l['s'] in ('rETH', 'cbETH', 'weETH') and (l['f'] == c.ZERO or l['r'] == c.ZERO) for l in c.r['legs']),
      'Rocket Pool, EigenLayer or ether.fi events, or an LST minted or burned', 'generic', SEED),
    # ---- bridges
    T('bridge_out', 'bridge', 'deposit into a bridge toward another chain',
      'Value is locked or burned on Ethereum and a message is sent so that it is released on another chain: an L2 deposit, a CCTP burn, a LayerZero packet.',
      lambda c: c.has(*BRIDGE_OUT), 'a bridge-deposit event family', 'bridge', SEED),
    T('bridge_in', 'bridge', 'bridge withdrawal finalized on Ethereum',
      'Value locked elsewhere is released on Ethereum: an L2 withdrawal finalized, a CCTP mint, an OFT receipt, a relayer fill.',
      lambda c: c.has(*BRIDGE_IN), 'a bridge-withdrawal event family', 'bridge', SEED),
    # ---- lending
    T('aave_v3_op', 'lending', 'Aave v3 supply, borrow, repay, withdraw or liquidation',
      'A user changes a lending position: supplies collateral (aToken minted), borrows (debt token minted), repays (debt burned), withdraws (aToken burned), '
      'or is liquidated (collateral seized by a liquidator who repays debt).',
      lambda c: c.has('AaveSupply', 'AaveBorrow', 'AaveRepay', 'AaveWithdraw', 'AaveLiquidation') and c.r['swaps'] == 0 and c.flash == 0,
      'an Aave pool event, no swap, no flash loan', 'lending', PILOT + ' #10'),
    T('morpho_op', 'lending', 'Morpho Blue market operation',
      'Supply, withdraw, borrow, repay, collateral movement or liquidation on a Morpho Blue market (or a MetaMorpho vault that routes to one).',
      lambda c: c.has('MorphoSupply', 'MorphoWithdraw', 'MorphoBorrow', 'MorphoRepay', 'MorphoSupplyCollateral', 'MorphoWithdrawCollateral', 'MorphoLiquidate')
      and c.r['swaps'] == 0 and c.flash == 0, 'a Morpho Blue market event, no swap, no flash loan', 'lending', SEED),
    T('compound_v3_op', 'lending', 'Compound v3 operation',
      'Supply or withdraw of base asset or collateral on a Comet market.',
      lambda c: c.has('CompoundV3Supply', 'CompoundV3Withdraw', 'CompoundV3SupplyCollateral', 'CompoundV3WithdrawCollateral') and c.r['swaps'] == 0 and c.flash == 0,
      'a Comet event, no swap, no flash loan', 'lending', SEED),
    T('spark_op', 'lending', 'Spark (Aave-fork) operation',
      'Supply on SparkLend, recognised by its five-argument Supply event.',
      lambda c: c.has('SparkSupply') and c.r['swaps'] == 0 and c.flash == 0, 'SparkSupply event, no swap, no flash loan', 'lending', SEED),
    # ---- DEX trades
    T('cow_settlement', 'dex', 'CoW Protocol batch settlement',
      'A solver settles one or more signed orders against pools or its own inventory in one transaction; users\' tokens move through the settlement contract.',
      lambda c: c.has('CoWTrade'), 'Trade event from the settlement contract', 'swap', SEED),
    T('intent_or_rfq_fill', 'dex', 'intent, limit-order or RFQ fill',
      'A filler or market maker executes a user\'s signed order (UniswapX, 1inch limit orders, 0x RFQ): the user gets a quoted amount, the filler sources it.',
      lambda c: c.has(*INTENT), 'UniswapX Fill, 1inch OrderFilled or 0x fill events', 'swap', SEED),
    T('dex_swap_user', 'dex', 'user swap through a router',
      'An externally owned account sells one asset and receives another in one transaction through a router or aggregator; the EOA\'s own balances change on both sides.',
      lambda c: c.r['swaps'] >= 1 and c.flash == 0 and c.two_sided(c.fnet) and not c.r['pool_to'],
      'swap event(s), no flash loan, the sending EOA nets negative in one asset and positive in another, destination is not the pool itself', 'swap', SEED),
    T('dex_swap_contract', 'dex', 'swap by a contract principal',
      'A contract (smart wallet, vault, bot, treasury) is the party whose balances change on both sides of a swap; the EOA only pays gas.',
      lambda c: c.r['swaps'] >= 1 and c.flash == 0 and c.two_sided(c.tnet) and not c.r['pool_to'],
      'swap event(s), no flash loan, the destination contract nets negative in one asset and positive in another', 'swap', SEED),
    T('dex_swap_direct_pool', 'dex', 'swap sent straight to the pool',
      'The transaction calls the pool contract itself rather than a router: a bot or an integrator that handles callbacks itself.',
      lambda c: c.r['swaps'] >= 1 and c.flash == 0 and c.r['pool_to'], 'the destination emits the swap event', 'swap', SEED),
    T('swap_other', 'dex', 'swap with an unclear principal',
      'Swap events are present but neither the EOA nor the destination ends two-sided: the beneficiary is a third address, or the priced legs are incomplete.',
      lambda c: c.r['swaps'] >= 1 and c.flash == 0, 'swap event(s) not matched by the rules above', 'swap', SEED),
    # ---- liquidity and vaults
    T('liquidity_add', 'liquidity', 'liquidity provided to a pool',
      'Tokens go into a pool and a position (NFT, LP token or Curve shares) comes back.',
      lambda c: c.has(*LIQ_ADD) and not c.has(*LIQ_REMOVE), 'a liquidity-add event family and no removal family', 'generic', SEED),
    T('liquidity_remove', 'liquidity', 'liquidity withdrawn from a pool',
      'A position is burned or decreased and the tokens plus fees return to the owner.',
      lambda c: c.has(*LIQ_REMOVE), 'a liquidity-remove event family', 'generic', SEED),
    T('liquidity_v4', 'liquidity', 'Uniswap v4 liquidity change',
      'ModifyLiquidity on the v4 pool manager.', lambda c: c.has('V4ModifyLiquidity'), 'ModifyLiquidity event', 'generic', SEED),
    T('balancer_liquidity', 'liquidity', 'Balancer pool join or exit',
      'PoolBalanceChanged on the Balancer vault.', lambda c: c.has('BalancerPoolBalanceChanged'), 'PoolBalanceChanged event', 'generic', SEED),
    T('vault_deposit', 'vault', 'deposit into an ERC-4626 vault',
      'Assets go into a vault and shares are minted to the depositor (yield vaults, sUSDe, sDAI, MetaMorpho).',
      lambda c: c.has('ERC4626Deposit', 'ERC4626DepositAlt') and c.r['swaps'] == 0, 'ERC-4626 Deposit event, no swap', 'generic', SEED),
    T('vault_withdraw', 'vault', 'withdrawal from an ERC-4626 vault',
      'Shares are burned and assets return to the owner.', lambda c: c.has('ERC4626Withdraw') and c.r['swaps'] == 0, 'ERC-4626 Withdraw event, no swap', 'generic', SEED),
    # ---- NFTs
    T('nft_trade', 'nft', 'NFT sale',
      'An ERC-721 or ERC-1155 changes hands against ETH or WETH through a marketplace.',
      lambda c: (c.has('SeaportOrderFulfilled', 'BlurOrdersMatched') or c.r['rc721'] >= 1) and c.r['priced'] >= 1 and c.r['swaps'] == 0,
      'marketplace event or ERC-721 transfer with a priced leg and no swap', 'generic', SEED),
    # ---- wallet infrastructure
    T('erc4337_bundle', 'wallet', 'account-abstraction bundle',
      'A bundler submits user operations to the EntryPoint; the value moves on behalf of smart accounts.',
      lambda c: c.has('UserOperation'), 'UserOperationEvent', 'generic', SEED),
    T('eip7702_delegated', 'wallet', 'call on an EIP-7702 delegated account',
      'A type-4 transaction sets or uses a delegation, or a relayer calls execute() on an EOA that carries a delegation designator; the account owner moves value without paying gas.',
      lambda c: c.r['ty'] == '0x4' or c.r['sel'] == '0xe9ae5c53', 'transaction type 0x4 or selector execute(bytes32,bytes) 0xe9ae5c53', 'generic', PILOT + ' #7'),
    T('safe_execution', 'wallet', 'multisig (Safe) execution',
      'Owners of a Safe execute a signed transaction from the Safe: a transfer, a contract call, a treasury operation.',
      lambda c: c.has('SafeExecutionSuccess', 'SafeModuleSuccess'), 'ExecutionSuccess or ExecutionFromModuleSuccess event', 'generic', SEED),
    T('contract_creation', 'wallet', 'contract creation carrying value',
      'A new contract is deployed and funded in the same transaction.', lambda c: c.r['to'] is None, 'no destination', 'generic', SEED),
    # ---- WETH
    T('weth_wrap', 'transfer', 'ETH wrapped into WETH',
      'A wallet converts ETH to its ERC-20 form, usually inventory management by a trading wallet before a pool or bridge operation.',
      lambda c: c.legs_only({'native', 'wrap'}) and c.r['lc'] == 1, 'the only legs are a top-level value and a WETH Deposit, one log', 'transfer', PILOT + ' #5'),
    T('weth_unwrap', 'transfer', 'WETH unwrapped into ETH',
      'The reverse conversion.', lambda c: c.legs_only({'unwrap'}) and c.r['lc'] == 1, 'the only leg is a WETH Withdrawal, one log', 'transfer', SEED),
    # ---- plain transfers, sub-typed by the window-wide profile of the parties
    T('exchange_internal_transfer', 'exchange_flow', 'transfer between two exchange-like wallets',
      'Both ends behave like exchange hot wallets over the window; the operator rebalances between its own addresses.',
      lambda c: c.plain and c.from_tags & EXCHANGE and c.cp_tags & EXCHANGE,
      'plain native or single-token transfer; sender and recipient both carry hot_wallet or many_sources tags', 'exchange', SEED),
    T('exchange_withdrawal', 'exchange_flow', 'withdrawal from an exchange-like hot wallet',
      'A hot wallet that sends to many destinations pays out to a customer address; the recipient is usually quiet.',
      lambda c: c.plain and 'hot_wallet' in c.from_tags,
      'plain transfer whose sender has the hot_wallet tag (>= 100 transactions to >= 50 distinct destinations in the window)', 'exchange', PILOT + ' #2, #9'),
    T('exchange_deposit', 'exchange_flow', 'deposit into an exchange-like wallet',
      'A customer or a deposit address sends to a wallet that receives from many sources over the window.',
      lambda c: c.plain and c.cp_tags & EXCHANGE,
      'plain transfer whose recipient has the hot_wallet or many_sources tag', 'exchange', PILOT + ' #11'),
    T('deposit_sweep', 'exchange_flow', 'sweep of a deposit address',
      'A pass-through address forwards what it received to a collector: exchange back-office consolidation.',
      lambda c: c.plain and ('pass_through' in c.from_tags or 'pass_through' in c.cp_tags),
      'plain transfer where either side is a pass-through address (few sources, one destination, net zero over the window)', 'exchange', SEED),
    T('batch_payout', 'transfer', 'one sender paying many recipients',
      'One transaction distributes an asset to five or more addresses: exchange batch withdrawals, payroll, airdrops, rewards.',
      lambda c: c.r['rcpt'] >= 5 and c.r['swaps'] == 0 and c.flash == 0 and c.pnet and all(v < 0 for v in c.pnet.values()),
      'five or more distinct recipients, no swap, the principal only pays out', 'generic', SEED),
    T('plain_transfer_eoa', 'transfer', 'plain transfer without a behavioural subtype',
      'A native or single-token transfer whose parties show no exchange-like, bot-like or pass-through behaviour over the window: OTC settlement, custody movement, '
      'a person moving funds. The largest class of unknown purpose; the profile of each side is the only evidence.',
      lambda c: c.plain, 'plain transfer with no actor tag matched above', 'transfer', SEED),
    T('erc20_transfer_from', 'transfer', 'token moved by an operator (transferFrom)',
      'A contract or operator moves a user\'s approved tokens: custody sweeps, subscription pulls, protocol deposits that do not emit their own event.',
      lambda c: c.r['sel'] == '0x23b872dd' and c.r['lc'] <= 2 and c.r['swaps'] == 0, 'selector transferFrom with at most two logs and no swap', 'transfer', SEED),
]


def by_id():
    return {t['id']: t for t in TYPES}


# Specific conversions precede generic mint/burn shapes. An internal PSM mint is not new external funding.
psm = next(t for t in TYPES if t['id'] == 'psm_conversion')
TYPES.remove(psm)
TYPES.insert(0, psm)
for entry in TYPES:
    if entry['id'] == 'aave_v3_op':
        entry['rule'] = lambda c: c.has_at('0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2', 'AaveSupply', 'AaveBorrow', 'AaveRepay', 'AaveWithdraw', 'AaveLiquidation') and c.r['swaps'] == 0 and c.flash == 0
        entry['rule_text'] += '; event emitter must be the documented Ethereum Core pool'
    elif entry['id'] == 'morpho_op':
        entry['rule'] = lambda c: c.has_at('0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb', 'MorphoSupply', 'MorphoWithdraw', 'MorphoBorrow', 'MorphoRepay', 'MorphoSupplyCollateral', 'MorphoWithdrawCollateral', 'MorphoLiquidate') and c.r['swaps'] == 0 and c.flash == 0
        entry['rule_text'] += '; event emitter must be the documented Ethereum Morpho Blue contract'
    elif entry['id'] == 'cow_settlement':
        entry['rule'] = lambda c: c.has_at('0x9008d19f58aabd9ed0d60971565aa8510560ab41', 'CoWTrade')
        entry['rule_text'] += '; event emitter must be the documented Ethereum settlement contract'
    elif entry['id'] == 'sandwich_attack':
        entry['what'] = 'The same sending address trades opposite directions around another sender in one pool and block. This is a sandwich candidate; coordinated ownership, profit and the counterfactual execution price remain unproved.'
    elif entry['id'] == 'sandwich_victim':
        entry['what'] = 'A swap lies inside the detected same-sender round trip. Price harm requires replay against the state without the surrounding trades.'
    elif entry['id'] == 'flash_loan_arbitrage':
        entry['what'] = 'An event-emitting lender sends tokens and receives at least the same amount back, while swaps occur. This establishes temporary funding plus trading; leverage adjustment or liquidation can have the same shape, so arbitrage profit is not assumed.'
        entry['rule_text'] += '; lender must also emit a flash-loan event'
    elif entry['id'] == 'exchange_internal_transfer':
        entry['what'] = 'Value moves between two high-connectivity addresses. Shared ownership or exchange identity cannot be established from these five-hour activity profiles.'
        entry['name'] = 'transfer between high-connectivity wallets'
    elif entry['id'] in ('exchange_withdrawal', 'exchange_deposit', 'deposit_sweep'):
        entry['what'] += ' Exchange identity and customer intent are hypotheses; distributions, treasury operations and other services can share this behaviour.'
    elif entry['id'] == 'nft_trade':
        entry['rule'] = lambda c: c.has('SeaportOrderFulfilled', 'BlurOrdersMatched') and c.r['priced'] >= 1 and c.r['swaps'] == 0
        entry['rule_text'] = 'marketplace event plus a priced leg and no swap; an NFT transfer alone does not establish a sale'
    elif entry['id'] == 'eip7702_delegated':
        entry['rule'] = lambda c: c.r['ty'] == '0x4'
        entry['rule_text'] = 'transaction type 0x4 (execution selector alone does not prove account delegation)'


LEARNED = 'five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05'
RELAY = '0x4cd00e387622c35bddb9b4c962c136462338bc31'
ASTER = '0x604dd02d620633ae427888d41bfd15e38483736e'
CCIP = '0x80226fc0ee2b096224eeac085bb9a8cba1146f7d'


def outgoing(c, address):
    return any(l['k'] == 'erc20' and l['f'] == address and l['r'] != address and int(l['raw']) > 0 for l in c.r['legs'])


def incoming(c, address):
    return any(l['r'] == address and l['f'] != address and int(l['raw']) > 0 for l in c.r['legs'])


def token_execution(c):
    return (c.r['sel'] in ('0xb61d27f6', '0x34fcd5be', '0x394b1de1') and c.r['legs'] and c.r['swaps'] == 0
            and set(c.r['fam']) <= {'ERC20_Transfer_shape', 'Approval'}
            and all(l['k'] == 'erc20' and l['f'] == c.r['to'] and l['r'] not in (c.ZERO, c.r['to']) for l in c.r['legs']))


NEW_TYPES = [
    T('dolomite_account_deposit', 'lending', 'Dolomite margin-account deposit',
      'USDC passes through a deposit proxy into DolomiteMargin, which credits a numbered account. The account balance is an internal signed principal record, so a second ERC-20 share transfer is not required. The two transfer legs are one deposit.',
      lambda c: any(a=='0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d' and t=='0x2bad8bc95088af2c247b30fa2b2e6a0886f88625e0945cd3051008e0e270198f' for a,t,_ in c.r['unk']) and incoming(c,'0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d'),
      'official DolomiteMargin Ethereum address, documented LogDeposit topic and incoming assets; decode account, market, deltaWei and newPar', 'dolomite', LEARNED),
    T('relay_settlement_withdrawal', 'settlement', 'Relay depository settlement withdrawal',
      'An allocator-authorized execute call releases escrowed tokens to a solver or nominated recipient. This is settlement inventory returning from the depository; it does not by itself prove a new user bridge withdrawal.',
      lambda c: c.has_at(RELAY, 'RelayCallExecuted') and outgoing(c, RELAY),
      'RelayCallExecuted emitted by the documented Ethereum depository plus a positive token outflow from that address', 'custody_flow', LEARNED),
    T('relay_deposit', 'settlement', 'deposit into Relay settlement escrow',
      'Tokens or native ETH enter the depository and an order identifier is recorded. A separate solver fill and settlement can happen later; destination execution is outside this Ethereum-only study.',
      lambda c: c.has_at(RELAY, 'RelayErc20Deposit', 'RelayNativeDeposit') and incoming(c, RELAY),
      'Relay deposit event from the documented Ethereum depository plus an incoming priced leg', 'custody_flow', LEARNED),
    T('aster_treasury_deposit', 'trading_custody', 'Aster trading-treasury deposit',
      'A user funds the documented trading treasury. A balance claim is created in the trading system; this transfer does not show a trade, a leverage change or a profit.',
      lambda c: c.has_at(ASTER, 'AsterDepositObserved') and incoming(c, ASTER),
      'observed deposit topic at the documented Ethereum Aster treasury plus incoming value', 'custody_flow', LEARNED),
    T('aster_treasury_withdrawal', 'trading_custody', 'Aster trading-treasury payout',
      'The treasury releases tokens to a beneficiary following a relayed instruction. Ethereum records the payout, not the preceding account PnL or trades.',
      lambda c: c.has_at(ASTER, 'AsterWithdrawalObserved') and outgoing(c, ASTER),
      'observed withdrawal topic at the documented Ethereum Aster treasury plus outgoing tokens', 'custody_flow', LEARNED),
    T('ccip_token_send', 'bridge', 'CCIP token-send request on Ethereum',
      'A sender locks tokens in a token pool and pays a separate message fee through the CCIP router. The emitted message proves initiation, not delivery on the other chain.',
      lambda c: c.r['to'] == CCIP and c.r['sel'] == '0x96f4e9f9' and c.has('CCIPMessageSentObserved') and any(l['k']=='erc20' and l['f']==c.r['from'] and int(l['raw'])>0 for l in c.r['legs']),
      'documented Ethereum CCIP router and ccipSend selector, message event, and a sender token outflow', 'custody_flow', LEARNED),
    T('contract_token_execution', 'wallet', 'contract-account token execution',
      'The fee-paying sender instructs an account contract to move its token inventory to one or several recipients. Separating caller, asset owner and beneficiary prevents counting the relayer as the payer. Exchange ownership is unresolved.',
      token_execution,
      'one of three observed execution selectors; only Transfer/Approval events; all priced legs are token outflows from the called account', 'custody_flow', LEARNED),
    T('operator_token_batch', 'wallet', 'operator-mediated token-transfer batch',
      'A helper moves tokens directly between third-party addresses. The transaction sender and helper can both have zero token net. The $20M example is a single USDT movement under a batch interface, not $20M owned by the gas payer.',
      lambda c: c.r['to']=='0xee39678386f5bfc68df2c65656ec8e23f60063b5' and c.r['sel']=='0xe4c705e9' and c.r['swaps']==0
      and bool(c.r['legs']) and all(l['k']=='erc20' and l['f'] not in (c.ZERO,c.r['to']) and l['r'] not in (c.ZERO,c.r['to']) for l in c.r['legs'])
      and any(a==c.r['to'] and t=='0xdf423376f9b0ab363b1b4d6f0b4cb6821921ec30f491555a97236a8a38ce095a' for a,t,_ in c.r['unk']),
      'observed helper address, four-array selector and completion topic, with direct non-mint token legs outside the helper', 'custody_flow', LEARNED),
    T('flash_funded_lending', 'lending', 'flash-funded lending-position adjustment',
      'Temporary borrowing enables a lending-position change. Read collateral and debt events separately from repayment of the temporary loan; a negative cash net may be newly supplied collateral, not a trading loss.',
      lambda c: c.flash > 0 and c.has('AaveSupply','AaveBorrow','AaveRepay','AaveWithdraw','MorphoSupply','MorphoBorrow','MorphoRepay','MorphoWithdraw'),
      'event-supported flash pair plus lending supply/borrow/repay/withdraw events', 'flash_lending', LEARNED),
    T('liquidity_with_swap', 'liquidity', 'liquidity management with an embedded swap',
      'One transaction combines a trade with a liquidity change. The swap can rebalance inventory used by the position; trading and liquidity legs must be investigated together.',
      lambda c: c.r['swaps']>0 and c.has(*(LIQ_ADD | LIQ_REMOVE | {'V4ModifyLiquidity'})),
      'swap events and mint/burn/collect/modify-liquidity events in the same transaction', 'generic', LEARNED),
    T('liquidity_collect_only', 'liquidity', 'collection of tokens owed to a liquidity position',
      'A pool or position manager pays tokens already owed. Without a positive liquidity burn in this transaction, this is not evidence of new liquidity removal; owed principal from an earlier burn and fees require position history to separate.',
      lambda c: c.has('V3Collect','V3NFPMCollect') and not c.has('V3Burn','V3DecreaseLiquidity') and c.r['swaps']==0,
      'Collect event with no Burn/DecreaseLiquidity and no swap in this transaction', 'generic', LEARNED),
]

# Audit corrections: protect business mechanisms from broad infrastructure and balance-shape matches.
for entry in TYPES:
    if entry['id'] == 'weth_wrap':
        entry['rule'] = lambda c: c.legs_only({'native','wrap'}) and any(l['k']=='wrap' for l in c.r['legs']) and c.r['lc']==1
        entry['rule_text'] = 'actual canonical WETH Deposit leg, optionally native input, and one log'
    elif entry['id'] == 'lido_stake':
        entry['rule'] = lambda c: c.has('LidoSubmitted') and c.r['swaps']==0 and c.flash==0
    elif entry['id'] == 'restaking_or_lst_other':
        prior = entry['rule']
        entry['rule'] = lambda c, prior=prior: prior(c) and c.r['swaps']==0 and c.flash==0

priority_ids = ['bridge_out','bridge_in','cow_settlement','intent_or_rfq_fill']
priority = [next(t for t in TYPES if t['id']==tid) for tid in priority_ids]
TYPES = NEW_TYPES + priority + [t for t in TYPES if t['id'] not in priority_ids]
