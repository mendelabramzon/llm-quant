# Bytecode packets — research/2026-09-08/live_10h

Built by `scripts/bytecode_lens.py`. Every line below is derived from the runtime bytecode, the window's raw
blocks, or Etherscan's verified source — nothing here is a guess. `?` after a selector means no signature is
known for it locally.

## 0x140022b7000081000001094700609300d2187dab  — score 99

- **shape**: no-dispatcher (bespoke / fallback-only), 21818 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas, top-calls
- **rank reasons**: selfdestruct (6 sites); extcodecopy (2 sites); origin_auth (4 sites); coinbase_pay (1 sites); transient_storage (6 sites); prevrandao (1 sites); storage_gated_revert (1 sites); create (1 sites); no-dispatcher: hand-written, no ABI to read; no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 414 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 414 calls, 21 senders, 0.102% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `selfdestruct` — can destroy itself / force-send its balance @440b,46d6,4862
  - `create` — deploys child contracts @4461
  - `extcodecopy` — copies another contract's code (clone factory or code check) @48b7,4aa4
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @004c,0ce3,0d23
  - `origin_auth` — authorises on tx.origin @003a,0063,006f
  - `coinbase_pay` — pays or reads the block builder (MEV) @3493
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @2b47,2b82
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @0015,0072
  - `balance_self` — reads its own ETH balance @0547,4256,433e
  - `static_only` — makes read-only calls @0197,01e2,401b
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @0341,0381,0441
  - `prevrandao` — reads PREVRANDAO (randomness / lottery) @4e2c
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @0041
  - `outbound_calls` — call sites in the code @
- **calls out**: 0x0dfe1681 token0(), 0x11da60b4 settle(), 0x80f0b44c clear(address,uint256), 0xa5841194 sync(address), 0xd21220a7 token1(), 0xefd1fc6a ?, 0xf135baaa exttload(bytes32)
- **hardcoded addresses**: 0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)], 0x140022b7000081000001094700609300d2187dab, 0xba12222222228d8ba445958a75a0704d566bf2c8 [Balancer v2 Vault], 0xfffd8963efd1fc6a506488495d951d5263988d25
- **opcodes**: STOP=7580, PUSH=3557, DUP=750, ADD=403, CALLDATALOAD=290, MSTORE=250, BYTE=226, SHR=208, CALLDATACOPY=195, SHL=183, SELFDESTRUCT=182, GAS=172, JUMPDEST=168, CALL=166

## 0xe08d97e151473a848c3d9ca3f323cb720472d015  — score 89

- **shape**: near-dispatcherless (1 selectors, 6818 bytes), 6818 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: selfdestruct (1 sites); origin_auth (1 sites); coinbase_pay (1 sites); transient_storage (6 sites); create (6 sites); blob (1 sites); near-dispatcherless: hand-written, no ABI to read; no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 284 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 284 calls, 1 senders, 0.077% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `selfdestruct` — can destroy itself / force-send its balance @1a8f
  - `create` — deploys child contracts @0332,04c5,0805
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @003f,01be,01e8
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @0a6f,0b8a,0c0c
  - `blob` — reads blob state @1a94
  - `origin_auth` — authorises on tx.origin @000d
  - `coinbase_pay` — pays or reads the block builder (MEV) @0a05
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @0508
  - `balance_self` — reads its own ETH balance @09f5,0a0e
  - `static_only` — makes read-only calls @027b,074e,0ce5
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **answers**: 0xcabcfc90 ?
- **calls out**: 0x2e1a7d4d withdraw(uint256), 0x70a08231 balanceOf(address)
- **hardcoded addresses**: 0xc0ffeebabe5d496b2dde509f9fa189c25cf29671, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)]
- **strings**: `ico!` | `iso!` | `icts!` | `isitss!` | `Wcico!_R_'` | `_Wcico!_R_'` | `jWciso!_R_'` | `xV[dicts!_R_'` | `[fisitss!_R_'` | `aWcico!_R_'` | `Wciso!_R_'` | `V[dicts!_R_'`
- **opcodes**: PUSH=1332, DUP=713, SWAP=452, ADD=320, POP=236, JUMPI=212, JUMPDEST=197, SHR=115, JUMP=115, SHL=86, SUB=82, MLOAD=81, GT=80, EQ=78

## 0x1b82a3d07fc1da1392110509cc47bb38678d7f59  — score 82

- **shape**: ordinary dispatcher (15 selectors), 21388 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: selfdestruct (1 sites); extcodecopy (1 sites); origin_auth (1 sites); coinbase_pay (1 sites); delegatecall (1 sites); transient_storage (1 sites); prevrandao (1 sites); storage_gated_revert (2 sites); no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 169 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 169 calls, 17 senders, 0.038% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `selfdestruct` — can destroy itself / force-send its balance @5073
  - `delegatecall` — executes another contract in its own storage @501c
  - `extcodecopy` — copies another contract's code (clone factory or code check) @5328
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @5322
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @1297,1361,15f7
  - `origin_auth` — authorises on tx.origin @05f8
  - `coinbase_pay` — pays or reads the block builder (MEV) @0fbe
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @05ca,05df,4f0c
  - `balance_self` — reads its own ETH balance @06eb,06f8,0f51
  - `static_only` — makes read-only calls @0631,0db6,0eb3
  - `prevrandao` — reads PREVRANDAO (randomness / lottery) @536b
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @05de,05f7
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **answers**: 0x0ab35bb0 ?, 0x10d1e85c uniswapV2Call(address,uint256,uint256,bytes), 0x20c5eff5 ?, 0x2e6940e9 ?, 0x31f57072 onMorphoFlashLoan(uint256,bytes), 0x3b9aca00 ?, 0x4b28ce3d ?, 0x599d0714 payCallback(uint256,address), 0x83197ef0 destroy(), 0x88b97778 ?, 0x91dd7346 unlockCallback(bytes), 0xb45a3c0e locked(uint256), 0xf2020020 ?, 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes), 0xfc4dd333 withdrawWETH(uint256)
- **calls out**: 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0240bc6b ?, 0x03a65ab6 withdraw(address,address,uint128), 0x0476982d ?, 0x07901001 ?, 0x0852cd8d ?, 0x08a960c1 ?, 0x0902f1ac getReserves(), 0x095ea7b3 approve(address,uint256), 0x0b0d9c09 take(address,address,uint256), 0x0b2583c8 originSwap(address,address,uint256,uint256,uint256), 0x0b477573 migrateFor(address,uint256), 0x0c11dedd pay(address), 0x0d0e30db ?, 0x0df791e5 ?, 0x0dfe1681 token0(), 0x0e03065f ?, 0x0ea598cb ?, 0x128acb08 swap(address,bool,int256,uint160,bytes), 0x12e103f1 completePayments(), 0x13346fd5 ?, 0x156e29f6 mint(address,uint256,uint256), 0x15afd409 settle(address,uint256), 0x18160ddd totalSupply(), 0x1a4ca37b ?, 0x1f18b371 swap(address,bool,int256,bytes), 0x20e8c565 deposit(address,address,uint256,uint256), 0x23b872dd transferFrom(address,address,uint256), 0x26599850 wrapTo(uint256,address), 0x2770a7eb ?, 0x2bfb780c swap((uint8,address,address,address,uint256,uint256,bytes)), 0x2e1a7d4d withdraw(uint256), 0x3ccfd60b withdraw(), 0x3e174aaf balanceOfInShares(address), 0x40c10f19 mint(address,uint256), 0x48c89491 unlock(bytes), 0x4b28ce3d ?, 0x4c5b2beb payoutFees(), 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0x59a87bc1 buy(uint256,uint256,address)
- **reverts with**: 0x03807f81 ?, 0x9b7cfcb7 InvalidTransferRecipient(), 0xdd85b49d InvalidDexType(uint8)
- **hardcoded addresses**: 0x8d8d5b393d7fabdd28bff2fa8912921641364fed, 0xaaabbc3c304ca824b641a2631a8c31c1a32890e6, 0xdb0e558e59cc03cf59c5c839bd91e7b055fc3ba4, 0xdfaaff44205a09df937c0816515d0fe9226e57c3, 0xf344beecd62579031e4a6ce2654140ba03cd4168, 0xfba0014d3a9dbe8a0cda6affd3da7b541a1ec32f, 0xddb9112d9f628aac2cc04a044ef76877f8f82d7c, 0xc87e4a6819d70aa8b3a0e9039076438b99dba874, 0xccfdc55f3219a9cb5cce713f05c45e5ea3e7b22e, 0xb106ada75585cd12026e8c49a8716b4094d55ecb, 0x9dd15b92a47dd4df58d31ada9e68388b7c0daede, 0xa8475224db16bb2aa33d3b27325f0fe7f81854a4, 0xa9721c9c85172ffeda5afbc8f23830b3482d9cf6, 0x9fe3d5c3cab35f57d1a246f13a9b3573640711ab, 0x8feaeea90d3a79c6cd3ea71d2fff2f9467fed7fa, 0x90a00d2500f975889c6a7083fc7ca99fb8909d99, 0x8e40395bfb1bac0657d72155c2f7ba1c5052146a, 0x3a28012f6572dd3bdb80842e885b6836d016d9c1, 0x5f444704bce3eb657768037bfb269b68730418a5, 0x7d4a81c93f04d7c6c82a89abeea2a3eacb265913, 0x8a29f8905b30dece481f312d3cbb39f29d3c9425, 0x6e50c4643dd48bdcee6435e98746c2050ac99887, 0x541a14efac81cb37adb57a5e75ed920edfeff596, 0x59144cff3e031b62e8c05fd5d1a7a1ad5cc777e5
- **strings**: `_RaOCV['@QbPro'`
- **opcodes**: PUSH=3520, DUP=2562, SWAP=2445, ADD=1079, JUMPDEST=764, POP=763, JUMPI=588, JUMP=570, MLOAD=489, MSTORE=480, SHR=286, ISZERO=265, EQ=193, SHL=121

## 0x009a8dbad7000f0000009b002d050058ca881b57  — score 77

- **shape**: no-dispatcher (bespoke / fallback-only), 13529 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas, top-calls
- **rank reasons**: extcodecopy (1 sites); origin_auth (3 sites); coinbase_pay (2 sites); transient_storage (6 sites); blob (1 sites); no-dispatcher: hand-written, no ABI to read; no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 427 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 427 calls, 2 senders, 0.045% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `extcodecopy` — copies another contract's code (clone factory or code check) @33d5
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @04d9,04dc,05c5
  - `blob` — reads blob state @33f0
  - `origin_auth` — authorises on tx.origin @0014,002b,0579
  - `coinbase_pay` — pays or reads the block builder (MEV) @07ca,0857
  - `number_gate` — branches on block.number @0583
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @0059,0074,008f
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @0042,0593,1d9a
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **calls out**: 0x022c0d9f swap(uint256,uint256,address,bytes), 0x02515961 ?, 0x0476982d ?, 0x080f44a9 ?, 0x092cc683 ?, 0x095ea7b3 approve(address,uint256), 0x0afede03 ?, 0x0b0d9c09 take(address,address,uint256), 0x0bb0c7ef ?, 0x108db744 withdrawQuoteTo(address,uint256), 0x11da60b4 settle(), 0x12e103f1 completePayments(), 0x13346fd5 ?, 0x15afd409 settle(address,uint256), 0x29610465 ?, 0x2e1a7d4d withdraw(uint256), 0x3ccfd60b withdraw(), 0x3cf36453 ?, 0x3eece7db swap(address,(uint256,bool,bool,int32),bytes), 0x43583be5 erc4626BufferWrapOrUnwrap((uint8,uint8,address,uint256,uint256)), 0x48c89491 unlock(bytes), 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0x55c4b02d ?, 0x5f179f64 depositQuoteTo(address,uint256), 0x7c1e845d ?, 0x7cdb53cb ?, 0x7fc9d4ad swapSingle((address,address,bytes32),bool,int256,uint256,address,bool,bytes,bytes), 0x7fffffff ?, 0x8201aa3f swapExactAmountIn(address,uint256,address,uint256,uint256), 0x8d7ef9bb buyGem(address,uint256), 0x8dae7333 sellBaseToken(uint256,uint256,bytes), 0x945bcec9 batchSwap(uint8,(bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256), 0x947cf92b withdrawBaseTo(address,uint256), 0x95991276 sellGem(address,uint256), 0xa9059cbb transfer(address,uint256), 0xaa06ce9b depositBaseTo(address,uint256), 0xae639329 sendTo(address,address,uint256), 0xbd6015b4 sellBase(address), 0xc51c9029 swap(address,uint256,bool,bool,uint256,bytes), 0xc6883ec5 swapMultiHop((bytes,int256,address,uint256,uint256,bytes))
- **hardcoded addresses**: 0x196c00c1b00000000000007c00739ad9faa3ee77, 0xba1333333333a1ba1108e8412f11850a5c319ba9, 0x6690384822aff0b65fe0c21a809f187f5c3fcdd8, 0xbbcb91440523216e2b87052a99f69c604a7b6e00, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)], 0xba12222222228d8ba445958a75a0704d566bf2c8 [Balancer v2 Vault], 0xeef417e1d5cc832e619ae18d2f140de2999dd4fb, 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 0xa1ea1ba18e88c381c724a75f23a130420c403f9a
- **opcodes**: PUSH=2709, DUP=1007, SHR=449, STOP=427, MSTORE=403, JUMPDEST=391, ADD=388, AND=331, JUMP=326, SWAP=288, CALLDATALOAD=247, JUMPI=198, SHL=154, POP=151

## 0x0de8bf93da2f7eecb3d9169422413a9bef4ef628  — score 75

- **shape**: ordinary dispatcher (10 selectors), 3768 bytes, solc 0.8.17, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: selfdestruct (2 sites); create2 (2 sites); origin_auth (3 sites); delegatecall (2 sites); storage_gated_revert (1 sites); one-off logic hash: not a known fork; 1.36% of window gas; 271 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 271 calls, 26 senders, 1.361% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `selfdestruct` — can destroy itself / force-send its balance @02ba,0451
  - `delegatecall` — executes another contract in its own storage @0280,0601
  - `create2` — deploys at a precomputed address (counterfactual / metamorphic) @03aa,08bf
  - `origin_auth` — authorises on tx.origin @02bd,0454,0802
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @02bc,0453,06be
  - `balance_self` — reads its own ETH balance @06ea
  - `static_only` — makes read-only calls @074c
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @06b4
  - `outbound_calls` — call sites in the code @
- **answers**: 0x59635f6f c(address,bytes), 0x725159a6 dKill(address,bytes), 0x81aafabb map(address,bytes), 0xb1ae2ed1 t(uint256,bytes,bytes), 0xb4f40c61 k(), 0xc2580804 f(uint256[],bytes,bytes), 0xc40493dc d(address,bytes), 0xd59fe5f4 cKill(address,bytes), 0xdf8de3e7 claimTokens(address), 0xf19c74b0 t_(uint256[],bytes,bytes)
- **calls out**: 0x70a08231 balanceOf(address), 0xa9059cbb transfer(address,uint256)
- **hardcoded addresses**: 0x0de8bf93da2f7eecb3d9169422413a9bef4ef628, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73
- **strings**: `UPPPPPPPPPV[3'`
- **opcodes**: PUSH=628, DUP=457, SWAP=292, POP=173, JUMPDEST=156, ADD=118, JUMP=97, MSTORE=74, JUMPI=72, MLOAD=56, SUB=49, REVERT=46, ISZERO=44, SHL=36

## 0x4884d28f048e66a537762334937e01a044cbdfac  — score 66

- **shape**: no-dispatcher (bespoke / fallback-only), 1594 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: eip7702-delegate
- **rank reasons**: origin_auth (1 sites); coinbase_pay (1 sites); transient_storage (6 sites); no-dispatcher: hand-written, no ABI to read; no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; EIP-7702 delegate: 22 authorizations, 21 submitters, 21 signing EOAs; unlabelled in the address book
- **window**: 0 calls, 0 senders, 0.000% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **EIP-7702**: 22 authorizations in this window, 21 gas-paying submitters, 21 distinct signing EOAs
- **facts**:
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @0008,0015,0019
  - `origin_auth` — authorises on tx.origin @000a
  - `coinbase_pay` — pays or reads the block builder (MEV) @037f
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @000b,0064
  - `balance_self` — reads its own ETH balance @007a,02fc,0326
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **strings**: `assert not eq` | `unknown compare type` | `balance check failed` | `R' '$Rlassert not eq'`
- **opcodes**: PUSH=332, SWAP=128, DUP=106, JUMPDEST=78, JUMP=58, JUMPI=42, ADD=37, MSTORE=37, POP=34, MLOAD=21, SHL=19, EQ=15, SHR=11, NOT=10

## 0x0000000000be226afde21672a5e4adc45692e69d  — score 65

- **shape**: no-dispatcher (bespoke / fallback-only), 1782 bytes, no metadata, unique logic
- **label**: searcher bot (shape: pass-through, 4 txs, 100% flat, 3 counterparties, $1279M gross)
- **selected because**: top-gas, top-calls
- **rank reasons**: create2 (2 sites); coinbase_pay (2 sites); transient_storage (6 sites); no-dispatcher: hand-written, no ABI to read; no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 0.21% of window gas; 419 calls and zero logs: emits nothing an event reader can see; proxy -> eip7702-delegation; labelled: searcher bot (shape: pass-through, 4 txs, 100% flat, 3 counterparties, $1279M gross)
- **window**: 419 calls, 16 senders, 0.211% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **proxy**: 0x06a1c212e1aca52430bb8aa5fa82c5d0b54a26fd (eip7702-delegation)
- **facts**:
  - `create2` — deploys at a precomputed address (counterfactual / metamorphic) @03d4,06e7
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @0013,0220,0248
  - `coinbase_pay` — pays or reads the block builder (MEV) @0499,04ba
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @005c,006e,009c
  - `balance_self` — reads its own ETH balance @04a6,04e2
  - `static_only` — makes read-only calls @043e,054f
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **calls out**: 0x2e1a7d4d withdraw(uint256), 0x70a08231 balanceOf(address), 0xa9059cbb transfer(address,uint256)
- **reverts with**: 0x30cd7471 NotOwner(), 0x5557f932 NP()
- **hardcoded addresses**: 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)]
- **opcodes**: PUSH=281, DUP=114, SWAP=82, JUMPDEST=53, POP=42, JUMPI=41, ADD=39, JUMP=30, EQ=27, CALLER=23, SHR=23, SHL=18, ISZERO=17, MUL=16

## 0xb276f62db0ce8ca2ca5bc522695be604521eac1c  — score 64

- **shape**: ordinary dispatcher (92 selectors), 21425 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas, top-logs
- **rank reasons**: callcode (1 sites); create2 (2 sites); extcodecopy (1 sites); delegatecall (1 sites); transient_storage (2 sites); prevrandao (1 sites); storage_gated_revert (4 sites); create (2 sites); blob (2 sites); no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 0.21% of window gas; unlabelled in the address book
- **window**: 357 calls, 47 senders, 0.212% of gas, 12.6229 ETH in, 2699 logs (19 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @52d3
  - `callcode` — deprecated CALLCODE @537f
  - `create` — deploys child contracts @3a73,5308
  - `create2` — deploys at a precomputed address (counterfactual / metamorphic) @52ae,52ec
  - `extcodecopy` — copies another contract's code (clone factory or code check) @52c0
  - `extcodesize` — checks whether a caller is a contract @0692,0ae7,0b4d
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @531a,5355
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @4e06
  - `blob` — reads blob state @5352,5382
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @056d,18b9,33a2
  - `number_gate` — branches on block.number @09b0,35ea
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @12df,1396,1bc3
  - `balance_self` — reads its own ETH balance @3a48
  - `static_only` — makes read-only calls @0615,070e,3220
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @52bc
  - `prevrandao` — reads PREVRANDAO (randomness / lottery) @537a
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @07b0,2b37,3feb
  - `outbound_calls` — call sites in the code @
- **answers**: 0x0793e5fd depositorReclaimBacking(uint256), 0x0986a5a1 claimTopSpot(uint256), 0x1b9bc525 treeRootWeight(), 0x1fe543e3 rawFulfillRandomWords(uint256,uint256[]), 0x20bd63ba acceptBidAsTokens(uint256,uint256), 0x249d39e9 BPS(), 0x24f74697 callbackGasLimit(), 0x25692962 requestOwnershipHandover(), 0x2b0b9641 ownerAcquisitionFeeBps(), 0x2c8bea33 activateListings(uint256), 0x2fa14f49 configureVrfRequest(bytes32,uint32), 0x34b1670f pendingAcquisitionCount(), 0x3531aed5 acquireBatch(uint256,uint256,uint256), 0x35390e96 acceptDepositorBid(uint256), 0x38dc89ef reservedListingCount(uint64), 0x38f5f005 acquisitionFee(), 0x39c33215 MAX_CALLBACK_GAS_LIMIT(), 0x39ea5e12 acquisitionRefundCredit(address), 0x3c61c7aa listNFT(address,uint256), 0x3d21f274 unsettledAcquisitionCount(), 0x3f23b0cb vrfCoordinatorAndSubId(), 0x40ef7ee1 selectionSlippageBps(), 0x41111a4a acquisitions(uint256), 0x4681a7c6 activeListingCount(), 0x49cfb710 keepNFT(uint256), 0x4a088a42 ownerSettlementFeeBps(), 0x4c5b2beb payoutFees(), 0x4c68b3b9 feeShareTotal(), 0x548b0de9 acquire(uint256,uint256), 0x54d1f13d cancelOwnershipHandover(), 0x59749e94 vrfService(), 0x59d973db acquisitionEscrowTotal(), 0x5b69ae6a retainedToProtocol(), 0x5b8d02d7 payoutAddress(), 0x5c584c88 feeCredit(address), 0x61e3c944 setUint(uint256,uint256), 0x6480ef05 acquisitionTokenSlice(uint256), 0x666cd313 collectionWhitelisted(address), 0x6a6e8c70 topThresholdBps(), 0x6e658d1a withdrawAcquisitionRefund(), 0x715018a6 renounceOwnership(), 0x783c3a09 acquisitionMeta(uint256), 0x7b9aa10f accruedOwnerFees(), 0x7d4b4a6f relistNFT(uint256), 0x7f3e2b9c acquire(uint256,uint256,uint256), 0x823e645a topListingShareBps(), 0x8600e5cb finalizeWindow(), 0x863975fa acquireBatch(uint256,uint256,uint256,uint256), 0x8ca14105 recoverStuckNFT(uint256), 0x8da5cb5b owner(), 0x96c82e57 totalWeight(), 0x97cedc76 setBool(uint256,bool), 0x987df4cd quoteAcquisitionPrice(), 0x9e790a76 requestIdAtSequence(uint64), 0x9eb60921 finalizeUnsettled(uint256), 0x9ec5a894 rewards(), 0xa2b93478 pendingFees(uint256), 0xa4e42912 reservedListingAt(uint64,uint256), 0xa66e8ae2 unfulfilledVrfCount(), 0xaaccf1ec nextListingId()
- **calls out**: 0x03280d35 ?, 0x0e4df0f3 onListingActivated(uint256,address,uint256), 0x0f253927 ?, 0x125fa267 vendorContracts(address,uint256), 0x17999f11 ?, 0x21421707 ?, 0x23b872dd transferFrom(address,address,uint256), 0x31a9108f ?, 0x389a75e1 ?, 0x41af6c87 pendingRequestExists(uint256), 0x487faeed ?, 0x4d8e1c2f ?, 0x64d38d69 ?, 0x688189d3 prepareRequests(uint256), 0x7e062a35 ?, 0xa81b8251 onListingRemoved(uint256), 0xc5fc9d43 registerAcquisition(uint256,address,uint256,uint256), 0xd969194b fwa(), 0xea502b3f processAcquisitions(uint256), 0xeb2e578b requestFee()
- **reverts with**: 0x03586681 AcquisitionsNotEnabled(), 0x0586b55f ErrorSellOfferAmountTooLowToCoverFundingFee(), 0x06b7c759 ?, 0x08c0b8b3 ?, 0x095c777f ListingNotAllocated(), 0x0b3b4ff1 ?, 0x0df21dc7 ?, 0x102f2f61 ?, 0x1a070b57 ?, 0x1acb3113 ?, 0x1d8730d1 ?, 0x2773d46f ?, 0x29dcff21 ?, 0x2c2f710d ?, 0x2d97066f NotPurchaser(), 0x2f579acf ?, 0x36f9dc41 OnlyVrfService(), 0x389a75e1 ?, 0x3cc50b45 NotDepositor(), 0x3cd01497 ?, 0x4a41747f ?, 0x4ae2ee69 ?, 0x4fdbe7f1 ?, 0x517172a1 ?
- **emits**: 0x155ad598d6… ListingWithdrawn(uint256,address,uint256), 0x3d3d959e38… RewardsConfigured(address,address), 0x48dc35af7b… EarningsWithdrawn(address,uint256), 0x4c4950b9ef… CollectionWhitelistSet(address,bool), 0x4ef8a301ec… UnfulfilledVrfReconciled(uint256), 0x63edc6f178… AcquisitionProcessed(uint256,uint64,uint8,address), 0x6aca4be863… AcquisitionRefundWithdrawn(address,uint256), 0x6f4528c508… UnsettledFinalized(uint256,address,address), 0xa92dbf0b2a… StuckNFTRecovered(uint256,address), 0xcbe199cf5a… FeesPaidOut(address,uint256), 0xdbf36a107d… OwnershipHandoverRequested(address), 0xf23e34f4aa… AcquisitionRequested(uint256,address,uint256,uint256), 0xfa7b8eab7d… OwnershipHandoverCanceled(address)
- **hardcoded addresses**: 0xa084c33fb7a467307452898b8d58165ebd2e5d9f
- **strings**: `aK'WaKta4`
- **opcodes**: PUSH=4313, DUP=1723, SWAP=1216, JUMPDEST=754, JUMPI=655, MSTORE=525, JUMP=477, SLOAD=379, ADD=367, SHL=319, POP=270, MLOAD=264, AND=250, SUB=236

## 0x00000000fd3a7b3fa5bcfa843c648714b11e089b  — score 63

- **shape**: ordinary dispatcher (8 selectors), 24060 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: extcodecopy (1 sites); coinbase_pay (1 sites); transient_storage (6 sites); no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 1.17% of window gas; 176 calls and zero logs: emits nothing an event reader can see; proxy -> eip7702-delegation; unlabelled in the address book
- **window**: 176 calls, 2 senders, 1.172% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **proxy**: 0xe49131e2e8e8aa02472ced78b0c5d9968b07e6fa (eip7702-delegation)
- **facts**:
  - `extcodecopy` — copies another contract's code (clone factory or code check) @5df8
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @00c7,0166,04c6
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @0353,0362,03fe
  - `coinbase_pay` — pays or reads the block builder (MEV) @0985
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @0016,00a3,00b5
  - `balance_self` — reads its own ETH balance @3839,3914,392a
  - `static_only` — makes read-only calls @3779,3a03,3ad5
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **answers**: 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x2c8958f6 algebraSwapCallback(int256,int256,bytes), 0x3a1c453c solidlyV3SwapCallback(int256,int256,bytes), 0x91dd7346 unlockCallback(bytes), 0xb134ef53 mauveSwapCallback(int256,int256,bytes), 0xe0154ff0 nineMMV3SwapCallback(int256,int256,bytes), 0xf40a74a8 ShibaswapV2SwapCallback(int256,int256,bytes), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes)
- **calls out**: 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0240bc6b ?, 0x02515961 ?, 0x0476982d ?, 0x0633bf1f ?, 0x095ea7b3 approve(address,uint256), 0x0b0d9c09 take(address,address,uint256), 0x0d0e30db ?, 0x0d343281 ?, 0x1e2eaeaf extsload(bytes32), 0x29610465 ?, 0x299ce14b ?, 0x2e1a7d4d withdraw(uint256), 0x3850c7bd slot0(), 0x39db0079 ?, 0x3cf36453 ?, 0x48c89491 unlock(bytes), 0x5d043b29 ?, 0x70a08231 balanceOf(address), 0x789add55 ?, 0xa9059cbb transfer(address,uint256), 0xf30dba93 ticks(int24)
- **hardcoded addresses**: 0x238a358808379702088667322f80ac48bad5e6c4, 0xdc035d45d973e3ec169d2276ddab16f1e407384f, 0x6b175474e89094c44da98b954eedeac495271d0f, 0x2260fac5e5542a773aa44fbcfedf7c193bc2c599, 0xdac17f958d2ee523a2206206994597c13d831ec7, 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48, 0xfffd8963efd1fc6a506488495d951d5263988d25
- **strings**: `a%UWPPV[_`
- **opcodes**: PUSH=4417, SWAP=2811, DUP=2251, JUMPDEST=1199, POP=1027, JUMP=919, ADD=694, JUMPI=689, MSTORE=336, ISZERO=286, SHL=273, EQ=232, MLOAD=232, SHR=171

## 0xbdb3ba9ffe392549e1f8658dd2630c141fdf47b6  — score 63

- **shape**: ordinary dispatcher (28 selectors), 11650 bytes, solc 0.8.28, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas, top-calls
- **rank reasons**: callcode (1 sites); extcodecopy (1 sites); coinbase_pay (2 sites); delegatecall (1 sites); transient_storage (6 sites); blob (1 sites); one-off logic hash: not a known fork; 0.61% of window gas; 1378 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 1378 calls, 24 senders, 0.610% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @1f0e
  - `callcode` — deprecated CALLCODE @2d7c
  - `extcodecopy` — copies another contract's code (clone factory or code check) @2d3e
  - `extcodesize` — checks whether a caller is a contract @029f,0673,08af
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @0717,0bcd,0c26
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @1f78
  - `blob` — reads blob state @2d67
  - `coinbase_pay` — pays or reads the block builder (MEV) @1b3e,1b59
  - `number_gate` — branches on block.number @0272,04a8,0537
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @056c,0a5d,0ae3
  - `balance_self` — reads its own ETH balance @1b2d,1b3d,2ab8
  - `static_only` — makes read-only calls @0611,063d,073d
  - `outbound_calls` — call sites in the code @
- **answers**: 0x15e2b6cd revokeRebalancerRole(address), 0x17f8f44d ?, 0x1f000000 ?, 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x2de6ca25 ?, 0x3ab1a494 setWithdrawAddress(address), 0x3c000000 ?, 0x53b03a83 revokeTraderRole(address), 0x5ca7ab59 ?, 0x62000000 ?, 0x6568a279 withdrawAll(address[]), 0x70000000 zCtfkP(), 0x800a35d9 ?, 0x824a811d ?, 0x853828b6 withdrawAll(), 0x8d690bab ?, 0x9410ae88 dexCallback(address,uint256), 0x94abab1d revokeMaintainerRole(address), 0x999895db ?, 0xa0000000 ?, 0xaaf10f42 getImplementation(), 0xb80042dc ?, 0xb9b4aacd ?, 0xc7137f5e ?, 0xd784d426 setImplementation(address), 0xe1477062 ?, 0xe98d8c3a grantRebalancerRole(address), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes)
- **calls out**: 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0240bc6b ?, 0x02515961 ?, 0x095ea7b3 approve(address,uint256), 0x0d0e30db ?, 0x2e1a7d4d withdraw(uint256), 0x2f85f1e7 ?, 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0x70a08231 balanceOf(address), 0x7464fc3d kLast(), 0x8201aa3f swapExactAmountIn(address,uint256,address,uint256,uint256), 0xa9059cbb transfer(address,uint256)
- **reverts with**: 0x022c0d9f swap(uint256,uint256,address,bytes)
- **hardcoded addresses**: 0xba12222222228d8ba445958a75a0704d566bf2c8 [Balancer v2 Vault], 0x5b43453fce04b92e190f391a83136bfbecedefd1, 0x00ff842be7e390605e7e3664ebfa0e432806500d, 0x52aa899454998be5b000ad077a46bbe360f4e497 [FluidLiquidityProxy], 0xfffd8963efd1fc6a506488495d951d5263988d25
- **strings**: `FluidT1DEX` | `iFluidT1DEX\` | `iFluidT1DEX\a` | `a);V[_iFluidT1DEX]'` | `iFluidT1DEX]V[`
- **opcodes**: PUSH=2351, DUP=825, SWAP=747, JUMPDEST=520, JUMP=419, JUMPI=282, MSTORE=268, ADD=262, SHL=173, ISZERO=152, MLOAD=132, SUB=105, AND=102, CALLDATALOAD=95

## 0x81463b0f960f247f704377661ec81c1fd65b5128  — score 63

- **shape**: no-dispatcher (bespoke / fallback-only), 20273 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: origin_auth (5 sites); coinbase_pay (1 sites); no-dispatcher: hand-written, no ABI to read; no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 350 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 350 calls, 4 senders, 0.084% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `origin_auth` — authorises on tx.origin @0015,0030,004b
  - `coinbase_pay` — pays or reads the block builder (MEV) @4f2d
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @0076,008b
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @009e,009f,0389
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **calls out**: 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0b0d9c09 take(address,address,uint256), 0x11da60b4 settle(), 0x128acb08 swap(address,bool,int256,uint160,bytes), 0x2e1a7d4d withdraw(uint256), 0x48c89491 unlock(bytes), 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0xa5841194 sync(address), 0xa9059cbb transfer(address,uint256), 0xd0e30db0 deposit(), 0xe5d7bde6 fillOrderTo((uint256,address,address,address,address,address,uint256,uint256,uint256,bytes),bytes,bytes,uint256,uint256,uint256,address), 0xf3cd914c swap((address,address,uint24,int24,address),(bool,int256,uint160),bytes), 0xf497df75 fillOrderArgs((uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256),bytes32,bytes32,uint256,uint256,bytes)
- **hardcoded addresses**: 0xe75ed6f453c602bd696ce27af11565edc9b46b0d, 0xfc9928f6590d853752824b0b403a6ae36785e535, 0x0bde59981fdeac219ce9e618d27f193438bff786, 0x7d344a2d90efb4544df07b5c510fee99b81915d4, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)], 0xfffd8963efd1fc6a506488495d951d5263988d25, 0xba12222222228d8ba445958a75a0704d566bf2c8 [Balancer v2 Vault], 0x1111111254eeb25477b68fb85ed929f73a960582 [1inch AggregationRouterV5], 0x111111125421ca6dc452d289314280a0f8842a65 [1inch AggregationRouterV6]
- **opcodes**: PUSH=4493, MSTORE=1144, DUP=1045, ADD=751, CALLDATALOAD=663, SHR=539, SWAP=230, BYTE=211, GAS=180, CALL=180, SHL=164, JUMPDEST=148, SUB=139, POP=124

## 0xa0df17b5ac76ababa36e1450e2cbcd18a620c845  — score 63

- **shape**: ordinary dispatcher (46 selectors), 11394 bytes, no metadata, unique logic
- **label**: _unlabelled_
- **selected because**: top-logs
- **rank reasons**: selfdestruct (1 sites); callcode (1 sites); create2 (3 sites); delegatecall (1 sites); transient_storage (6 sites); storage_gated_revert (1 sites); create (1 sites); blob (2 sites); no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; unlabelled in the address book
- **window**: 30 calls, 15 senders, 0.001% of gas, 0.0 ETH in, 1381 logs (6 topic0s)
- **facts**:
  - `selfdestruct` — can destroy itself / force-send its balance @2be6
  - `delegatecall` — executes another contract in its own storage @2bea
  - `callcode` — deprecated CALLCODE @2bc8
  - `create` — deploys child contracts @0cb5
  - `create2` — deploys at a precomputed address (counterfactual / metamorphic) @2c3b,2c3e,2c47
  - `extcodesize` — checks whether a caller is a contract @0473,0ddb,1811
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @03c9,06fe,1515
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @20b1,239b
  - `blob` — reads blob state @2beb,2c13
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @064f,0652,1017
  - `number_gate` — branches on block.number @0be8
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @1458,16a8,1e52
  - `balance_self` — reads its own ETH balance @0bee,0c8e
  - `static_only` — makes read-only calls @1311
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @12aa,1da0
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @2731
  - `outbound_calls` — call sites in the code @
- **answers**: 0x06fdde03 name(), 0x0741dc4d lastBuybackBlock(), 0x095ea7b3 approve(address,uint256), 0x12261ee7 permit2(), 0x16f0115b pool(), 0x18160ddd totalSupply(), 0x182148ef poolKey(), 0x224212cb routeBurnBps(), 0x23b872dd transferFrom(address,address,uint256), 0x25692962 requestOwnershipHandover(), 0x313ce567 decimals(), 0x3644e515 DOMAIN_SEPARATOR(), 0x3a308783 buybackSqrtPriceLimitX96(), 0x41f51da4 BUYBACK_DELAY_BLOCKS(), 0x42966c68 burn(uint256), 0x4437152a setPool(address), 0x54d1f13d cancelOwnershipHandover(), 0x5a01021d BUYBACK_INCREMENT(), 0x70a08231 balanceOf(address), 0x715018a6 renounceOwnership(), 0x791b98bc positionManager(), 0x7ecebe00 nonces(address), 0x7f5a7c7b hook(), 0x8091f3bf launched(), 0x87374239 routeDepositorBps(), 0x898c6150 routePurchaserBps(), 0x8c498e4c launching(), 0x8da5cb5b owner(), 0x8f0c86fa isDistributor(address), 0x91dd7346 unlockCallback(bytes), 0x95d89b41 symbol(), 0xa718e20d getTransferAllowance(), 0xa9059cbb transfer(address,uint256), 0xaf9e7239 increaseTransferAllowance(uint256), 0xbac0a7d6 CALLER_REWARD_BPS(), 0xbad51a7e setRouteSplit(uint256,uint256,uint256), 0xd505accf permit(address,address,uint256,uint256,uint8,bytes32,bytes32), 0xd59ba0df setDistributor(address,bool), 0xd947454d setBuybackSqrtPriceLimitX96(uint160), 0xdc4c90d3 poolManager(), 0xdd62ed3e allowance(address,address), 0xf04e283e completeOwnershipHandover(address), 0xf2fde38b transferOwnership(address), 0xf8ec6911 buyback(), 0xfd217053 launch(uint160,int24,int24), 0xfee81cf4 ownershipHandoverExpiresAt(address)
- **calls out**: 0x0476982d ?, 0x07cb8793 onTokenReceived(uint256,uint256), 0x0b0d9c09 take(address,address,uint256), 0x1592ca1b ?, 0x29610465 ?, 0x38377508 ?, 0x389a75e1 ?, 0x3cf36453 ?, 0x48c89491 unlock(bytes), 0x7f5e9f20 ?, 0x87517c45 approve(address,address,uint160,uint48), 0x87a211a2 ?, 0xa9059cbb transfer(address,uint256), 0xdd46508f modifyLiquidities(bytes,uint256), 0xf7020405 initializePool((address,address,uint24,int24,address),uint160)
- **reverts with**: 0x03faf4f9 ?, 0x13be252b InsufficientAllowance(), 0x18521d49 ?, 0x19f4db0f ?, 0x1a15a3cc PermitExpired(), 0x1b2c9ea5 ?, 0x1ee30da5 ?, 0x389a75e1 ?, 0x39d73813 DelayNotMet(), 0x3f68539a Permit2AllowanceIsFixedAtInfinity(), 0x45c3193d ?, 0x561ce9bb InvalidRange(), 0x570c1085 ?, 0x5a91834f OnlyHook(), 0x6f5e8818 NoHandoverRequest(), 0x7448fbae NewOwnerIsZeroAddress(), 0x7f5e9f20 ?, 0x82b42900 Unauthorized(), 0x87a211a2 ?, 0x8ff354d1 NoLpSupply(), 0x93dafdf1 SafeCastOverflow(), 0xab143c06 Reentrancy(), 0xb12d13eb ETHTransferFailed(), 0xbcd55b0f InvalidSplit()
- **emits**: 0x025f89b99c… PoolSet(address), 0xdbf36a107d… OwnershipHandoverRequested(address), 0xfa7b8eab7d… OwnershipHandoverCanceled(address)
- **hardcoded addresses**: 0x000000000022d473030f116ddee9f6b43ac78ba3 [Permit2], 0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e, 0xfffd8963efd1fc6a506488495d951d5163961682, 0x000000000004444c5dc75cb358380d2e3de08a90 [Uniswap v4 PoolManager], 0xfffd8963efd1fc6a506488495d951d5263988d26, 0x2c67eba8a50af0db5fba55f725247a75cbda6444
- **strings**: `a$OWPPPPP`
- **opcodes**: PUSH=2111, DUP=972, SWAP=588, JUMPDEST=386, JUMPI=314, MSTORE=294, ADD=230, JUMP=216, SHL=151, MLOAD=150, SUB=130, AND=121, POP=116, SHR=88

## 0x00000f91109c4d0007e90000d9facad5298a0cac  — score 62

- **shape**: no-dispatcher (bespoke / fallback-only), 1965 bytes, solc 0.8.26, unique logic
- **label**: searcher bot (shape: pass-through, 12 txs, 100% flat, 9 counterparties, $499M gross)
- **selected because**: top-gas
- **rank reasons**: origin_auth (1 sites); coinbase_pay (1 sites); delegatecall (1 sites); transient_storage (6 sites); no-dispatcher: hand-written, no ABI to read; one-off logic hash: not a known fork; 327 calls and zero logs: emits nothing an event reader can see; labelled: searcher bot (shape: pass-through, 12 txs, 100% flat, 9 counterparties, $499M gross)
- **window**: 327 calls, 6 senders, 0.118% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @0459
  - `extcodesize` — checks whether a caller is a contract @0245
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @0019,0023,0047
  - `origin_auth` — authorises on tx.origin @0010
  - `coinbase_pay` — pays or reads the block builder (MEV) @0307
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @000f
  - `balance_self` — reads its own ETH balance @027a,02f9,0311
  - `static_only` — makes read-only calls @018e,06cc
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **calls out**: 0x08c379a0 Error(string), 0x2e1a7d4d withdraw(uint256), 0x70a08231 balanceOf(address), 0xa9059cbb transfer(address,uint256), 0xd0e30db0 deposit(), 0xe0232b42 flashLoan(address,uint256,bytes)
- **hardcoded addresses**: 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)], 0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb [Morpho Blue]
- **strings**: `no profit`
- **opcodes**: DUP=282, PUSH=258, POP=108, ADD=106, SWAP=103, JUMPDEST=42, MLOAD=40, MSTORE=33, JUMPI=32, ISZERO=27, SUB=20, JUMP=19, GAS=16, DIV=14

## 0x4313c378cc91ea583c91387b9216e2c03096b27f  — score 58

- **shape**: ordinary dispatcher (28 selectors), 18326 bytes, solc 0.8.28, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas, top-logs, top-calls
- **rank reasons**: extcodecopy (1 sites); origin_auth (1 sites); delegatecall (6 sites); transient_storage (5 sites); storage_gated_revert (1 sites); one-off logic hash: not a known fork; 0.61% of window gas; 424 distinct senders; 103 ETH received directly; proxy -> eip1967.implementation; unlabelled in the address book
- **window**: 1319 calls, 424 senders, 0.611% of gas, 103.1398 ETH in, 2570 logs (2 topic0s)
- **proxy**: 0xb8f6534f3459d583ba30e7e7f9b16e7bda26c2a0 (eip1967.implementation)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @0d89,1084,1505
  - `extcodecopy` — copies another contract's code (clone factory or code check) @4712
  - `extcodesize` — checks whether a caller is a contract @0662,24f2,311c
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @4141,4664,4675
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @0ff1,2bf4
  - `origin_auth` — authorises on tx.origin @41d6
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @1c78,254c,275b
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @33a2,41ce
  - `balance_self` — reads its own ETH balance @065f,1452,1468
  - `static_only` — makes read-only calls @05be,0702,32ee
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @3004
  - `outbound_calls` — call sites in the code @
- **answers**: 0x180b0d7e feeDenominator(), 0x1861a3d8 swapV3ExactIn((address,address,address,address,uint24,address,uint256,uint256,uint256,uint160)), 0x1d5f45f5 factoryV3(), 0x236b7db2 pancakeFactoryV3(), 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x2c8958f6 algebraSwapCallback(int256,int256,bytes), 0x2dd327c5 swapV3MultiHopExactIn((address[],address[],bytes,address,uint256,uint256,uint256)), 0x3f4ba83a unpause(), 0x40e61bc3 swapMixedMultiHopExactIn((string[],bytes,address,address,bytes,address,address,address,uint256,uint256,uint256)), 0x58e3ce30 amountInCached(), 0x5b9e9006 swapV2ExactIn(address,address,uint256,uint256,address), 0x5c975abb paused(), 0x66a5a99e swapV2MultiHopExactIn(address,uint256,uint256,address[],address,uint256,address), 0x68e0d4e1 factoryV2(), 0x715018a6 renounceOwnership(), 0x8456cb59 pause(), 0x8da5cb5b owner(), 0x91dd7346 unlockCallback(bytes), 0x978bbdb9 feeRate(), 0xad5c4648 WETH(), 0xbfc60df9 feeExcludeList(address), 0xc415b95c feeCollector(), 0xd9caed12 withdraw(address,address,uint256), 0xe6cb474f swap((uint8,address,address,address,uint24,int24,address,bytes)[],address,uint256,uint256), 0xeffbec13 swap((uint8,address,address,address,uint24,int24,address,bytes)[],address,uint256,uint256,uint256), 0xf2fde38b transferOwnership(address), 0xf7013ef6 initialize(address,address,address,address,uint256), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes)
- **calls out**: 0x0d0e30db ?, 0x23b872dd transferFrom(address,address,uint256), 0x246326c3 ?, 0x2dcf4803 ?, 0x2e1a7d4d withdraw(uint256), 0x3352d4cf ?, 0x48c89491 unlock(bytes), 0x48eeb9a3 ?, 0x68ab79df ?, 0x70a08231 balanceOf(address), 0x92300e25 ?, 0xa9059cbb transfer(address,uint256), 0xb1d4ae39 ?, 0xc45a0155 factory()
- **reverts with**: 0x0a12f521 ?, 0x118cdaa7 OwnableUnauthorizedAccount(address), 0x1afcd79f ?, 0x1e4fbdf7 OwnableInvalidOwner(address), 0x37affdbf ?, 0x3ee5aeb5 ReentrancyGuardReentrantCall(), 0x48c89491 unlock(bytes), 0x5274afe7 SafeERC20FailedOperation(address), 0x8dfc202b ExpectedPause(), 0x9996b315 AddressEmptyCode(address), 0xd93c0665 EnforcedPause()
- **emits**: 0x5db9ee0a49… Unpaused(address), 0x62e78cea01… Paused(address), 0xc7f505b2f3… Initialized(uint64)
- **hardcoded addresses**: 0x1f98431c8ad98523631ae4a59f267346ea31f984, 0xfb8ed3485efa29a0e4bed93351dd51b59fc4b0f0, 0x129538ee65a692fa041e107921d716c31d186803, 0xbaceb8ec6b9355dfc0269c18bac9d6e2bdc29c4f, 0x968138d21b5c353a06ed0e4368320bc91fc0cc5c, 0xd8bd585d515f598f3ecd55418b10e7c96dbb08fd, 0x2dde2c8c0233876b42115d2bfe6cf76f48d1af39, 0x579f279a4d0ac1e239fabee4bc349e059b839e2c, 0x19ea70e105877975997ef1a82173eb512dc6d338, 0xd18dd117acfdad3d5599a6e70c4a737b6cf802ee, 0xf01f35a636eb55d631687c7e20bafe6177ab95d7, 0xd6b6f36ae706a578855bf078c9e258955b1205de, 0xafd78101ad9b4b8da4ca6b57472ed09b438b9fcf, 0x47866aac061db433aa471a2cdcd0d8ff8948fe2e, 0x0b0130911d747d54387f3d663c88d048912c72f8, 0x41ff9aa7e16b8b1a8a8dc4f0efacd93d02d071c9, 0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865, 0x07e610c722b66148d8c6b92967c99cd1ba8c7e61, 0x42ac1bef3f25c29bbe5e06ef5df3d00ead7cf20f
- **strings**: `unpaused already` | `paused already` | `BAD_ARGS` | `insufficient balance` | `ERR_EXCEEDED_SLIPPAGE:minReturn` | `toUint24_outOfBounds` | `insufficient funds` | `toAddress_outOfBounds` | `CallbackValidation: sender is no` | `ds-math-mul-overflow` | `PoolAddress: token0 > token1` | `Rounpaused already'` | `Rmpaused already'` | `RgBAD_ARGS'` | `a&UWV['@QbF` | `Rsinsufficient balance''` | `ERR_EXCEEDED_SLIPPAGE:minReturn 'D` | `RstoUint24_outOfBounds''` | `Rqinsufficient funds'p` | `a8IWPPPV['` | `RttoAddress_outOfBounds'X` | `CallbackValidation: sender is no'D` | `Rsds-math-mul-overflow''` | `R{PoolAddress: token0 > token1'`
- **opcodes**: PUSH=3581, DUP=1569, SWAP=1244, JUMPDEST=839, JUMP=705, ADD=596, MSTORE=404, JUMPI=391, MLOAD=342, SHL=246, POP=234, SUB=229, ISZERO=165, AND=159

## 0x0a252663dbcc0b073063d6420a40319e438cfa59  — score 58

- **shape**: ordinary dispatcher (48 selectors), 16000 bytes, solc 0.8.17, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: selfdestruct (1 sites); create2 (3 sites); coinbase_pay (1 sites); delegatecall (6 sites); prevrandao (1 sites); blockhash (1 sites); storage_gated_revert (4 sites); blob (2 sites); one-off logic hash: not a known fork; unlabelled in the address book
- **window**: 17 calls, 6 senders, 0.109% of gas, 0.0 ETH in, 32 logs (3 topic0s)
- **facts**:
  - `selfdestruct` — can destroy itself / force-send its balance @115e
  - `delegatecall` — executes another contract in its own storage @0ed0,15fb,1686
  - `create2` — deploys at a precomputed address (counterfactual / metamorphic) @23f7,3e54,3e57
  - `extcodesize` — checks whether a caller is a contract @0d03,14ad,1ec3
  - `blob` — reads blob state @3e03,3e04
  - `coinbase_pay` — pays or reads the block builder (MEV) @3dfb
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @213e,2f6a
  - `number_gate` — branches on block.number @098d,1190,183c
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @08e1,0950,14fb
  - `balance_self` — reads its own ETH balance @3e01
  - `static_only` — makes read-only calls @0ae7,0bda,1224
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @3e00
  - `prevrandao` — reads PREVRANDAO (randomness / lottery) @3dfe
  - `blockhash` — reads a block hash (randomness / proof) @3e5b
  - `storage_gated_revert` — reverts on a storage flag: pause, blocklist, or a trading switch @10e7,1108,155a
  - `outbound_calls` — call sites in the code @
- **answers**: 0x01bb4116 callClaimRank(uint256), 0x01ffc9a7 supportsInterface(bytes4), 0x044db8ba ROYALTY_BP(), 0x06fdde03 name(), 0x081812fc getApproved(uint256), 0x095ea7b3 approve(address,uint256), 0x152a902d ?, 0x19cba6b4 ownedTokens(), 0x23b872dd transferFrom(address,address,uint256), 0x2a55205a royaltyInfo(uint256,uint256), 0x41b169f3 POWER_GROUP_SIZE(), 0x41f43434 OPERATOR_FILTER_REGISTRY(), 0x42842e0e safeTransferFrom(address,address,uint256), 0x443aa533 mintInfo(uint256), 0x498a4c2d startBlockNumber(), 0x4d4b2be4 COMMON_CATEGORY_COUNTER(), 0x53b18de4 bulkClaimRankLimited(uint256,uint256,uint256), 0x543746b1 onTokenBurned(address,uint256), 0x55ee08ba SPECIAL_CATEGORIES_VMU_THRESHOLD(), 0x572b6c05 isTrustedForwarder(address), 0x5b5e139f ?, 0x5c41d2fe addForwarder(address), 0x6352211e ownerOf(uint256), 0x700107af LIMITED_CATEGORY_TIME_THRESHOLD(), 0x70a08231 balanceOf(address), 0x71141a58 xenCrypto(), 0x74a1dff2 specialClassesTokenLimits(uint256), 0x80ac58cd ?, 0x89776eb0 specialClassesCounters(uint256), 0x8da5cb5b owner(), 0x928dd2a7 powerDown(), 0x95d89b41 symbol(), 0x98bdf6f5 tokenIdCounter(), 0x9dc29fac burn(address,uint256), 0xa126ad1e BLACKOUT_TERM(), 0xa1a53fa1 vmuCount(uint256), 0xa22cb465 setApprovalForAll(address,bool), 0xb88d4fde safeTransferFrom(address,address,uint256,bytes), 0xba3ec741 AUTHORS(), 0xbd333033 xenBurned(uint256), 0xc87b56dd tokenURI(uint256), 0xd0d5f5b4 specialClassesBurnRates(uint256), 0xdf0030ef callClaimMintReward(address), 0xe3af6d0a genesisTs(), 0xe985e9c5 isApprovedForAll(address,address), 0xecef9201 bulkClaimRank(uint256,uint256), 0xee8743d7 isApex(uint256), 0xf5878b9b bulkClaimMintReward(uint256,address)
- **calls out**: 0x01ffc9a7 supportsInterface(bytes4), 0x125fb947 ?, 0x1b9345fd svgData(uint256,uint256,uint256,address,uint256), 0x1c560305 claimMintRewardAndShare(address,uint256), 0x1c9858dd ?, 0x30ba37b9 ?, 0x3185c44d ?, 0x346ba941 getTerm(uint256), 0x3b79c773 ?, 0x3c4a25e9 ?, 0x543746b1 onTokenBurned(address,uint256), 0x928dd2a7 powerDown(), 0x9ff054df claimRank(uint256), 0xdf0030ef callClaimMintReward(address), 0xe90cdc89 getRedeemed(uint256)
- **emits**: 0x17307eab39… ApprovalForAll(address,address,bool), 0x8c5be1e5eb… Approval(address,address,uint256)
- **hardcoded addresses**: 0x0000000000000000000000000000000000f8b9f0, 0x06450dee7fd2fb8e39061434babcfc05599a6fb8, 0xc73fc08c931efe3fce850c09278472e8a81c2e05, 0x0000000000000000000000000000000063ae7433, 0x0a252663dbcc0b073063d6420a40319e438cfa59, 0x3903b9cfa1680ed9663ecec7d3412305bebe326f, 0xc739d01beb34e380461bba9ef8ed1a44874382be, 0x1ac17ffb8456525bff46870bba7ed8772ba063a5, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73, 0x16115391950e88125b1b1959d85b0818dbdd5b9d
- **strings**: `XENFT: not enough burn amount` | `XENFT: not enough XEN balance` | `XENFT: not enough XEN balance ap` | `XENFT: illegal callback state` | `XENFT: illegal callback caller` | `XENFT: Forwarder is already set` | `ERC721: address zero is not a va` | `XENFT burn: not a supported cont` | `XENFT burn: illegal owner addres` | `XENFT burn: not an approved oper` | `XENFT burn: user is not tokenId` | `XENFT: Illegal address` | `XENFT: Error while claiming rewa` | `XENFT: Error while powering down` | `ERC721: approval to current owne` | `ERC721: approve caller is not to` | `ken owner nor approved for all` | `XENFT: only EOA allowed for this` | `category` | `XENFT: Error while claiming rank` | `ERC721: transfer from incorrect` | `ERC721: transfer to the zero add` | `ress` | `XENFT: transfer prohibited in bl`
- **opcodes**: PUSH=2886, DUP=1459, SWAP=802, JUMPDEST=538, ADD=491, MSTORE=458, JUMP=448, POP=387, SHL=242, JUMPI=229, MLOAD=212, SUB=175, AND=141, ISZERO=100

## 0x06cff7088619c7178f5e14f0b119458d08d2f5ef  — score 57

- **shape**: ordinary dispatcher (11 selectors), 22777 bytes, no metadata, unique logic
- **label**: router or solver (shape: pass-through, 42 txs, 100% flat, 1 counterparties, $2074M gross)
- **selected because**: top-gas, top-calls
- **rank reasons**: extcodecopy (1 sites); origin_auth (10 sites); coinbase_pay (5 sites); delegatecall (6 sites); transient_storage (2 sites); no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 588 calls and zero logs: emits nothing an event reader can see; labelled: router or solver (shape: pass-through, 42 txs, 100% flat, 1 counterparties, $2074M gross)
- **window**: 588 calls, 10 senders, 0.146% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @1f02,2bb7,2f37
  - `extcodecopy` — copies another contract's code (clone factory or code check) @57f5
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @008e,57ef
  - `origin_auth` — authorises on tx.origin @3677,3695,36b2
  - `coinbase_pay` — pays or reads the block builder (MEV) @2874,2b07,2e01
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @2ed5
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @2e1a
  - `balance_self` — reads its own ETH balance @0897,584a
  - `static_only` — makes read-only calls @2175,243b,29bc
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **answers**: 0x10d1e85c uniswapV2Call(address,uint256,uint256,bytes), 0x22222222 ?, 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x31f57072 onMorphoFlashLoan(uint256,bytes), 0x3a1c453c solidlyV3SwapCallback(int256,int256,bytes), 0x91dd7346 unlockCallback(bytes), 0x923b8a2a swapCallback(uint256,uint256,bytes), 0x99999999 ?, 0xa1dab4eb smardexSwapCallback(int256,int256,bytes), 0xf04f2707 receiveFlashLoan(address[],uint256[],uint256[],bytes), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes)
- **calls out**: 0x016ae6c7 ?, 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0240bc6b ?, 0x02515961 ?, 0x0476982d ?, 0x095ea7b3 approve(address,uint256), 0x0b0d9c09 take(address,address,uint256), 0x0b4c7e4d add_liquidity(uint256[2],uint256), 0x0b683721 ?, 0x0d0e30db ?, 0x0d2680e9 ?, 0x0f7c0849 ?, 0x1175980b ?, 0x1b0cd93b ?, 0x1f17a7a9 ?, 0x22770cc3 ?, 0x29610465 ?, 0x2967cf83 ?, 0x2e1a7d4d withdraw(uint256), 0x2e1c224f ?, 0x3850c7bd slot0(), 0x39f47693 unwrap(address,uint256), 0x3cf36453 ?, 0x4515cef3 add_liquidity(uint256[3],uint256), 0x48c89491 unlock(bytes), 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0x5320bf6b ?, 0x5f9bb63d ?, 0x65b2489b exchange_underlying(uint256,uint256,uint256,uint256), 0x67dfd4c9 leave(uint256), 0x701195a1 ?, 0x70a08231 balanceOf(address), 0x7156812d ?, 0x8201aa3f swapExactAmountIn(address,uint256,address,uint256,uint256), 0x95e3c50b tokenToEthSwapInput(uint256,uint256,uint256), 0x990966d5 unstake(address,uint256,bool,bool), 0xa9059cbb transfer(address,uint256), 0xb77d239b convertByPath(address[],uint256,uint256,address,address,uint256), 0xce7d6503 exchange(uint256,uint256,uint256,uint256,bool,address), 0xd3a4acd3 tradeBySourceAmount(address,address,uint256,uint256,uint256,address)
- **hardcoded addresses**: 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 0x0ab87046fbb341d058f17cbc4c1133f25a20a52f, 0x04906695d6d12cf5459975d7c3c03356e4ccd460, 0x64aa3364f17a4d01c6f1751fd97c2bd3d7e7f1d5, 0xfffd8963efd1fc6a506488495d951d5263988d25, 0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb [Morpho Blue], 0xd7e1236c08731c3632519dcd1a581bfe6876a3b2, 0x65fb9db5fc926eb22ac5ae86e74242e0df44718c, 0xb19c265d240326578eeb346189ebd96ae84949a9, 0xdf8adfe10d4a4d9f0fc4d3e377a6e8d5730eb40c, 0x5884b2faa9ad6f38010831e2290e515af17a7d47, 0x333c92538e7f47d17c79e5975d4e40e901427558, 0x9307514e06a07b149471ccfd690d0e3e6ace8df2, 0x1b1548763f8d5d6d3c37ad500f389b57e107bbff, 0x84e03f3b74b10c70db109cae6523c09a01552186, 0xf07b4d27cae6571857e51ab3fb209f5226de2d88
- **opcodes**: PUSH=5129, DUP=1941, SWAP=1788, POP=845, MSTORE=809, JUMPI=722, JUMPDEST=651, ADD=582, CALLDATALOAD=555, SHR=511, EQ=418, JUMP=414, MLOAD=321, ISZERO=217

## 0x7b32e9f7419836aa50fda10af4137400ae5c5f1b  — score 57

- **shape**: ordinary dispatcher (27 selectors), 23856 bytes, solc 0.8.28, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: extcodecopy (1 sites); origin_auth (3 sites); coinbase_pay (2 sites); delegatecall (4 sites); transient_storage (6 sites); prevrandao (1 sites); one-off logic hash: not a known fork; 351 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 351 calls, 17 senders, 0.086% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @1595,184b,1a62
  - `extcodecopy` — copies another contract's code (clone factory or code check) @5cec
  - `extcodesize` — checks whether a caller is a contract @0846,0b14,142c
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @1575,1a4f,3edc
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @09da,410f,413c
  - `origin_auth` — authorises on tx.origin @1a83,3a7a,52a8
  - `coinbase_pay` — pays or reads the block builder (MEV) @2658,5d27
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @21a6,2bc1
  - `balance_self` — reads its own ETH balance @2662,2753
  - `static_only` — makes read-only calls @0540,0620,0cc8
  - `prevrandao` — reads PREVRANDAO (randomness / lottery) @5d0f
  - `outbound_calls` — call sites in the code @
- **answers**: 0x0ab35bb0 ?, 0x10d1e85c uniswapV2Call(address,uint256,uint256,bytes), 0x20c31c75 ?, 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x2c8958f6 algebraSwapCallback(int256,int256,bytes), 0x2e6940e9 ?, 0x31f57072 onMorphoFlashLoan(uint256,bytes), 0x3a1c453c solidlyV3SwapCallback(int256,int256,bytes), 0x3b9aca00 ?, 0x4b28ce3d ?, 0x599d0714 payCallback(uint256,address), 0x6c813d29 croDefiSwapCall(address,uint256,uint256,bytes), 0x6dd2a554 ?, 0x81279c7e dmmSwapCall(address,uint256,uint256,bytes), 0x84645f79 swapsCall(address,uint256,uint256,bytes), 0x84800812 pancakeCall(address,uint256,uint256,bytes), 0x88b97778 ?, 0x91dd7346 unlockCallback(bytes), 0xa1dab4eb smardexSwapCallback(int256,int256,bytes), 0xb2ff9f26 swapV2Call(address,uint256,uint256,bytes), 0xb45a3c0e locked(uint256), 0xe6aac244 ?, 0xf40a74a8 ShibaswapV2SwapCallback(int256,int256,bytes), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes), 0xfa483e72 swapCallback(int256,int256,bytes), 0xfc4dd333 withdrawWETH(uint256), 0xfdb28658 ?
- **calls out**: 0x01d32d5b ?, 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0240bc6b ?, 0x02515961 ?, 0x038fff2d ?, 0x0476982d ?, 0x095ea7b3 approve(address,uint256), 0x0a28a477 previewWithdraw(uint256), 0x0b0d9c09 take(address,address,uint256), 0x0b683721 ?, 0x0c11dedd pay(address), 0x0d0e30db ?, 0x0dfe1681 token0(), 0x0f7c0849 ?, 0x12e103f1 completePayments(), 0x15afd409 settle(address,uint256), 0x1f18b371 swap(address,bool,int256,bytes), 0x1fb650cb ?, 0x23b872dd transferFrom(address,address,uint256), 0x29610465 ?, 0x2bfb780c swap((uint8,address,address,address,uint256,uint256,bytes)), 0x2d182be5 ?, 0x2e1a7d4d withdraw(uint256), 0x31b0b507 ?, 0x36cd3205 ?, 0x3ccfd60b withdraw(), 0x3cf36453 ?, 0x414bf389 exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160)), 0x48c89491 unlock(bytes), 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0x5320bf6b ?, 0x65b2489b exchange_underlying(uint256,uint256,uint256,uint256), 0x701195a1 ?, 0x70a08231 balanceOf(address), 0x7237e031 tokenToEthTransferInput(uint256,uint256,uint256,address), 0x794997aa unlock((address,uint256,uint256),(address,bytes),(uint256,uint256),bytes), 0x7c1e845d ?, 0x7cdb53cb ?, 0x8201aa3f swapExactAmountIn(address,uint256,address,uint256,uint256), 0x98d7e295 exitWithShares(uint256,address,address)
- **reverts with**: 0x41af4c7f ?, 0x7005668f TradeFailed(uint256), 0x71cd57f7 ?, 0xe5731c9d ?
- **hardcoded addresses**: 0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb [Morpho Blue], 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffca, 0xfffd8963efd1fc6a506488495d951d5263988d25, 0xfba0014d3a9dbe8a0cda6affd3da7b541a1ec32f, 0xdc035d45d973e3ec169d2276ddab16f1e407384f, 0x0ab87046fbb341d058f17cbc4c1133f25a20a52f, 0x64aa3364f17a4d01c6f1751fd97c2bd3d7e7f1d5, 0x1db1591540d7a6062be0837ca3c808add28844f6, 0xb63cac384247597756545b500253ff8e607a8020, 0xe592427a0aece92de3edee1f18e0157c05861564 [Uniswap v3 SwapRouter], 0xa3931d71877c0e7a3148cb7eb4463524fec27fbd [sUSDS (Savings USDS) — the token contract; symbol() and name() read on chain in this window], 0x8d8d5b393d7fabdd28bff2fa8912921641364fed, 0x3a28012f6572dd3bdb80842e885b6836d016d9c1, 0x18f96764c0785767e794f82e89b8b34f922dc8bf, 0x0afa3a877055f93c87381a7407db9c3d8c1bff47, 0x0165556a41a18c918dbe1bbfdbbd91a9ac3880c6, 0x0b4c5e9a101d28827330d74e67ae975b6eef96e5, 0x2988f8ed396a7541a03c7e78483fa987a172803d, 0x1bfd997d7d8cad60e8e9a3d1dfb078f676d5a95a, 0x363f5345d09f6d7e04c0be8233a65c0601b6d19c, 0x5f444704bce3eb657768037bfb269b68730418a5, 0x541a14efac81cb37adb57a5e75ed920edfeff596, 0x417025fdcf8d216855a062f4bb3fdc273a52a620
- **opcodes**: PUSH=4191, SWAP=2562, DUP=2554, JUMPDEST=1118, JUMP=890, POP=668, ADD=653, JUMPI=635, MSTORE=408, MLOAD=325, AND=313, ISZERO=238, SUB=233, SHL=213

## 0xd226997439ecfbeff8e110c8c78c8a7eefd19f89  — score 57

- **shape**: ordinary dispatcher (11 selectors), 23183 bytes, no metadata, unique logic
- **label**: router or solver (shape: pass-through, 37 txs, 100% flat, 1 counterparties, $1826M gross)
- **selected because**: top-gas
- **rank reasons**: extcodecopy (1 sites); origin_auth (20 sites); coinbase_pay (5 sites); delegatecall (6 sites); transient_storage (2 sites); no compiler metadata (hand-written Yul/assembly or stripped); one-off logic hash: not a known fork; 166 calls and zero logs: emits nothing an event reader can see; labelled: router or solver (shape: pass-through, 37 txs, 100% flat, 1 counterparties, $1826M gross)
- **window**: 166 calls, 12 senders, 0.061% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @1f02,2c35,2fb7
  - `extcodecopy` — copies another contract's code (clone factory or code check) @598b
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @008e,5985
  - `origin_auth` — authorises on tx.origin @36f7,3715,3732
  - `coinbase_pay` — pays or reads the block builder (MEV) @2874,2b45,2e81
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @2f55
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @2e9a
  - `balance_self` — reads its own ETH balance @0897,59e0
  - `static_only` — makes read-only calls @2175,243b,29bc
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **answers**: 0x10d1e85c uniswapV2Call(address,uint256,uint256,bytes), 0x22222222 ?, 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x31f57072 onMorphoFlashLoan(uint256,bytes), 0x3a1c453c solidlyV3SwapCallback(int256,int256,bytes), 0x91dd7346 unlockCallback(bytes), 0x923b8a2a swapCallback(uint256,uint256,bytes), 0x99999999 ?, 0xa1dab4eb smardexSwapCallback(int256,int256,bytes), 0xf04f2707 receiveFlashLoan(address[],uint256[],uint256[],bytes), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes)
- **calls out**: 0x016ae6c7 ?, 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0240bc6b ?, 0x02515961 ?, 0x0476982d ?, 0x095ea7b3 approve(address,uint256), 0x0b0d9c09 take(address,address,uint256), 0x0b4c7e4d add_liquidity(uint256[2],uint256), 0x0b683721 ?, 0x0d0e30db ?, 0x0d2680e9 ?, 0x0f7c0849 ?, 0x1175980b ?, 0x1b0cd93b ?, 0x1f17a7a9 ?, 0x22770cc3 ?, 0x29610465 ?, 0x2967cf83 ?, 0x2e1a7d4d withdraw(uint256), 0x2e1c224f ?, 0x3850c7bd slot0(), 0x39f47693 unwrap(address,uint256), 0x3cf36453 ?, 0x4515cef3 add_liquidity(uint256[3],uint256), 0x48c89491 unlock(bytes), 0x52bbbe29 swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256), 0x5320bf6b ?, 0x5f9bb63d ?, 0x65b2489b exchange_underlying(uint256,uint256,uint256,uint256), 0x67dfd4c9 leave(uint256), 0x701195a1 ?, 0x70a08231 balanceOf(address), 0x7156812d ?, 0x8201aa3f swapExactAmountIn(address,uint256,address,uint256,uint256), 0x95e3c50b tokenToEthSwapInput(uint256,uint256,uint256), 0x990966d5 unstake(address,uint256,bool,bool), 0xa9059cbb transfer(address,uint256), 0xb77d239b convertByPath(address[],uint256,uint256,address,address,uint256), 0xce7d6503 exchange(uint256,uint256,uint256,uint256,bool,address), 0xd3a4acd3 tradeBySourceAmount(address,address,uint256,uint256,uint256,address)
- **hardcoded addresses**: 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 0x0ab87046fbb341d058f17cbc4c1133f25a20a52f, 0x04906695d6d12cf5459975d7c3c03356e4ccd460, 0x64aa3364f17a4d01c6f1751fd97c2bd3d7e7f1d5, 0xfffd8963efd1fc6a506488495d951d5263988d25, 0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb [Morpho Blue], 0x480a15f9fdb1757d1db6cedc620772553f496637, 0xae0cc0d6e76c2b13451ab90cd13a5fa71a5c59ba, 0xe836ef5abbcde8c2a22c299f639cc9480aa52219, 0x970df0f4bd124df46b1dee31329f7444f9e66b68, 0x834d10cef4e5a75d3edddcbb1c5a94f8094e5713, 0xa57e3e178e41201b05b4e4aa6dde347fdcd5614e, 0x1c5bb001cf26ecb9e4af7fc0656d4fb452019790, 0x90a6e43c22005745c15df003b70292b53344dcf6, 0xe6618358787976f673187ca24da5f715a0496aa7, 0x8a3999c2a419d11635a5146035824a49c33ca211, 0xd7e1236c08731c3632519dcd1a581bfe6876a3b2, 0x65fb9db5fc926eb22ac5ae86e74242e0df44718c, 0xb19c265d240326578eeb346189ebd96ae84949a9, 0xdf8adfe10d4a4d9f0fc4d3e377a6e8d5730eb40c, 0x5884b2faa9ad6f38010831e2290e515af17a7d47, 0x333c92538e7f47d17c79e5975d4e40e901427558, 0x9307514e06a07b149471ccfd690d0e3e6ace8df2, 0x1b1548763f8d5d6d3c37ad500f389b57e107bbff
- **opcodes**: PUSH=5171, DUP=1959, SWAP=1802, POP=850, MSTORE=809, JUMPI=735, JUMPDEST=659, ADD=596, CALLDATALOAD=561, SHR=517, EQ=423, JUMP=420, MLOAD=321, ISZERO=218

## 0xce8b69d410e3241280ea8d0b1f71ba6840c4528b  — score 56

- **shape**: ordinary dispatcher (23 selectors), 24029 bytes, solc 0.8.26, unique logic
- **label**: _unlabelled_
- **selected because**: top-gas
- **rank reasons**: origin_auth (2 sites); coinbase_pay (3 sites); delegatecall (6 sites); transient_storage (6 sites); gasprice_gate (3 sites); one-off logic hash: not a known fork; 0.24% of window gas; 35 calls and zero logs: emits nothing an event reader can see; unlabelled in the address book
- **window**: 35 calls, 29 senders, 0.245% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **facts**:
  - `delegatecall` — executes another contract in its own storage @0833,094e,1cba
  - `extcodesize` — checks whether a caller is a contract @03a9,0a98,129d
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @020a,0212,03b1
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @077e,193d,1c7e
  - `origin_auth` — authorises on tx.origin @03a1,0a90
  - `coinbase_pay` — pays or reads the block builder (MEV) @1a7f,1a99,2e14
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @1b10,1c1f
  - `gasprice_gate` — branches on gas price (anti-frontrun or bribe sizing) @3b01,3bda,3d63
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @03a2,0a91,11e9
  - `balance_self` — reads its own ETH balance @056c,1a89,1fd7
  - `static_only` — makes read-only calls @0249,02d1,04de
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @1c32
  - `outbound_calls` — call sites in the code @
  - `stateless` — never writes storage: a router, a lens, or a pure library @
- **answers**: 0x10d1e85c uniswapV2Call(address,uint256,uint256,bytes), 0x2226ea1f ?, 0x23a69e75 pancakeV3SwapCallback(int256,int256,bytes), 0x25edf1c2 ?, 0x2c8958f6 algebraSwapCallback(int256,int256,bytes), 0x3a1c453c solidlyV3SwapCallback(int256,int256,bytes), 0x3b9aca00 ?, 0x599d0714 payCallback(uint256,address), 0x6c813d29 croDefiSwapCall(address,uint256,uint256,bytes), 0x6f5aeea3 ?, 0x84800812 pancakeCall(address,uint256,uint256,bytes), 0x8998d6ae unicSwapV2Call(address,uint256,uint256,bytes), 0x91dd7346 unlockCallback(bytes), 0x9410ae88 dexCallback(address,uint256), 0x9f3d4ab8 sushiswapV3SwapCallback(int256,int256,bytes), 0xa0bd0131 ?, 0xb45a3c0e locked(uint256), 0xb6a54548 dexCallback(address,uint256,bytes), 0xc18c82cc nineInchCallee(address,uint256,uint256,bytes), 0xce5937d7 ?, 0xe69da6c7 ?, 0xf04f2707 receiveFlashLoan(address[],uint256[],uint256[],bytes), 0xfa461e33 uniswapV3SwapCallback(int256,int256,bytes)
- **calls out**: 0x022c0d9f swap(uint256,uint256,address,bytes), 0x0bf45256 ?, 0x0dfe1681 token0(), 0x128acb08 swap(address,bool,int256,uint160,bytes), 0x2668dfaa swapIn(bool,uint256,uint256,address), 0x2e1a7d4d withdraw(uint256), 0x379c64dc ?, 0x442b26b9 ?, 0x48c89491 unlock(bytes), 0x5c38449e flashLoan(address,address[],uint256[],bytes), 0x6068a5a3 ?, 0x614c872e ?, 0x70a08231 balanceOf(address), 0x7768e0d2 ?, 0x7fc9d4ad swapSingle((address,address,bytes32),bool,int256,uint256,address,bool,bytes,bytes), 0x93967b77 ?, 0xa9059cbb transfer(address,uint256), 0xaf59a6a1 ?, 0xbe17c79c swapInWithCallback(bool,uint256,uint256,address), 0xd0e30db0 deposit(), 0xd21220a7 token1(), 0xf302b7c4 ?, 0xf83d08ba lock(), 0xf84c1c9a ?
- **hardcoded addresses**: 0x4d2b70c80d37c543fcdacba7bfcb3a8d52c89e54, 0xe0e0e08a6a4b9dc7bd67bcb7aade5cf48157d444, 0x8c3c081511f1cc2447f829220239bceecdc8bbae, 0xba12222222228d8ba445958a75a0704d566bf2c8 [Balancer v2 Vault], 0xfffd8963efd1fc6a506488495d951d5263988d25, 0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 [Wrapped Ether (WETH9)], 0xbbcb91440523216e2b87052a99f69c604a7b6e00, 0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97, 0xdadb0d80178819f2319190d340ce9a924f783711, 0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5, 0x396343362be2a4da1ce0c1c210945346fb82aa49, 0x1f9090aae28b8a3dceadf281b0f12828e676c326, 0xa28b0ac939fc6baaadc79a94f425345c60463417, 0xfb74767c1ce1aada0a0e114441173b57f8c1571b, 0x42966987a050f98b61d1c4606fc4b097888a0ae8, 0xbfb025eb30b857588df50c6c2bffa5c8633ca445
- **strings**: `do_swap ?` | `data` | `unkd` | `index out of range` | `n too small` | `aPyaPoaPep`
- **opcodes**: PUSH=3909, DUP=2128, SWAP=1899, JUMPDEST=1169, JUMP=974, ADD=734, POP=580, JUMPI=554, MLOAD=489, MSTORE=371, ISZERO=270, SUB=177, GT=120, AND=115

## 0x49ffbaea3e5e64ab888c942bf90f3d2f52d34bf8  — score 56

- **shape**: ordinary dispatcher (13 selectors), 20889 bytes, solc 0.8.27, unique logic
- **label**: _unlabelled_
- **selected because**: deployed-in-window
- **rank reasons**: create2 (1 sites); origin_auth (1 sites); delegatecall (6 sites); transient_storage (3 sites); gasprice_gate (1 sites); prevrandao (1 sites); blockhash (1 sites); one-off logic hash: not a known fork; deployed inside the window; unlabelled in the address book
- **window**: 0 calls, 0 senders, 0.000% of gas, 0.0 ETH in, 0 logs (0 topic0s)
- **deployed**: block 25928475 by 0x290757020f8f0935cafdcf701856728b0837ce91, tx 0xed976408d7eec9b7e7360b27252824fb7fd12be8a1e5f41c281b7c7f4858af79
- **facts**:
  - `delegatecall` — executes another contract in its own storage @07c5,0867,08e3
  - `create2` — deploys at a precomputed address (counterfactual / metamorphic) @516e
  - `extcodesize` — checks whether a caller is a contract @055b,0df4,1bb1
  - `transient_storage` — transient storage (EIP-1153): reentrancy locks, flash accounting @0d02,0d64,1158
  - `mcopy` — EIP-5656 memory copy (solc >= 0.8.25 / hand-written) @42d6,48bb,4bba
  - `origin_auth` — authorises on tx.origin @0e74
  - `timestamp_gate` — branches on block.timestamp (deadline or window) @0b03,0e31,0e3e
  - `number_gate` — branches on block.number @0d8e,0d9d
  - `gasprice_gate` — branches on gas price (anti-frontrun or bribe sizing) @0e62
  - `caller_pin` — compares msg.sender against a stored/hardcoded value @04a8,061a,0e73
  - `balance_self` — reads its own ETH balance @0c2a,0ed4,0f5b
  - `static_only` — makes read-only calls @28d6,29cf,2c59
  - `chainid` — reads chain id (EIP-712 domain or replay guard) @0db1,0dbb,0de3
  - `prevrandao` — reads PREVRANDAO (randomness / lottery) @0dc7
  - `blockhash` — reads a block hash (randomness / proof) @0da3
  - `outbound_calls` — call sites in the code @
- **answers**: 0x0f0c79d3 ?, 0x3b9aca00 ?, 0x3b9c85fd ?, 0x53c1b63e ?, 0x6386a850 ?, 0x7b4b3a33 ?, 0x7fe81d71 ?, 0x92acbbc6 ?, 0x952d6267 ?, 0x9ae74683 ?, 0xecc5320c ?, 0xf698da25 domainSeparator(), 0xfaf8a0ae ?
- **calls out**: 0x095ea7b3 approve(address,uint256), 0x0c2bf17b ?, 0x0df23dab ?, 0x23b872dd transferFrom(address,address,uint256), 0x31a9108f ?, 0x61599ce3 ?, 0x6eb1769f ?, 0x70a08231 balanceOf(address), 0x7619091f ?, 0x7e28a2ab ?, 0xa9059cbb transfer(address,uint256)
- **reverts with**: 0x081ceff3 ?, 0x1759616b ?, 0x185079b9 EmergencyMode(), 0x1ab7da6b DeadlineExpired(), 0x21421707 ?, 0x23b872dd transferFrom(address,address,uint256), 0x24856bc3 execute(bytes,bytes[]), 0x64c9d86f ?, 0x8cacdce1 ?, 0xd92e233d ZeroAddress()
- **emits**: 0x2d043ce009… SwapExecuted(address,uint256,uint256), 0x81f20f86f1… TransferFailed(address,address,uint256,uint256), 0x9b23ec14d4… AffiliateRewardPaid(address,uint256), 0xb9c1ea08b3… ?, 0xe7e15037b5… ReferralReward(address,uint256)
- **hardcoded addresses**: 0x73e2166be649736c07427b0b7ec5e54079d69558, 0xc2f15c8a6b2e7dac6cecfd08e401689c96f76473, 0x086967c62785a20de44879ebd5030b25788c0b69
- **strings**: `Reentrancy` | `RiReentrancy'` | `UPPV['@Qc1`
- **opcodes**: PUSH=4022, DUP=2455, SWAP=1441, ADD=951, JUMPDEST=834, POP=821, JUMP=574, MSTORE=475, MLOAD=413, JUMPI=407, SUB=321, ISZERO=278, SHL=233, AND=192
