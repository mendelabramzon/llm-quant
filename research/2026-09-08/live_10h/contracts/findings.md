# Reading the window's contracts from their bytecode

Window: Ethereum blocks 25,928,453–25,931,445 (2,993 blocks, ten hours ending 2026-09-08 08:26 UTC), 675,675
transactions. Instrument: `scripts/bytecode_lens.py`. Everything below is derived from the runtime bytecode, the
window's own raw blocks, or a block-pinned archive read, and every number has a command beside it.

## The finding

**One operator spent 5.4% of Ethereum's gas in this window poisoning 16,258 wallets, and no event-based reader could
see it.**

`0x59aab1bd0d26290274398c07b55955c15425e16b` sent 2,258 transactions — roughly one per block, for the whole ten
hours. Each carries a batch of EIP-7702 authorizations and a single call to
`0x00fe78205f5f0e63b8ad2b2ae5337f538a610e04`. Inside those 2,258 transactions are **335,601 dust transfers** to
**16,258 addresses**. None of them is a transaction. None of the native ones emits a log. The whole campaign moves
**$2.29** of value and burns **$649** of gas.

The existing window report saw exactly one thing about this: an unlabelled address in tenth place on "most active
senders, 2,258 txs".

### What the three contracts are

The lens reads all three from bytecode alone, before asking Etherscan anything.

| address | what the bytes say |
|---|---|
| `0x00fe78…0e04` | 769 bytes, solc 0.8.34, **one** function `executeBatch((address,uint256,bytes)[])`, never writes storage. Reads slot 0, masks it to an address, compares it to `CALLER`, and reverts with custom error `WhoAreYou()` (`0x0bf9dbd1`) if it differs. Slot 0 reads `0x59aab1bd…e16b` — the operator. One embedded string: `Delegated call failed`. |
| `0xe6b97aa1…43ed` | 760 bytes, solc 0.8.34, the **delegate**: this is the code that runs *inside* each EOA. Same single function, same custom error, but the operator is **hardcoded** — `ORIGIN` masked to an address and compared against `PUSH32 0x…59aab1bd0d26290274398c07b55955c15425e16b` at pc `0x41`–`0x6c`. Authorises on `tx.origin`, so any account delegated to it is spendable by that one address and no other. |
| `0x59aab1bd…e16b` | the operator EOA. Nonce 704,475. Balance 11.12 ETH. |

`uv run --with pycryptodome python scripts/bytecode_lens.py one --address 0xe6b97aa1490c93c28a14d86c13c9dc9c950643ed --disasm 0x40:0x80`

The two contracts differ in exactly one way, and it is the interesting way: the hub's operator is **mutable** (slot 0,
compared against `CALLER`), the delegate's is **immutable** (a code constant, compared against `ORIGIN`). An account
that signs the delegation is handing its balance to a specific address that can never be changed without a new
delegation.

**Both are verified on Etherscan, and both are named `Poisoner`.** Asked for the source only after the bytecode had been
read, Etherscan returns two sources that match the disassembly line for line:

```solidity
// 0xe6b97aa1… — the delegate, solc 0.8.34, optimizer runs 1
contract Poisoner {
    /*  This contract is used by bad guys for the address poisoning scam to trick inattentive users into
        sending USDT/USDC to the wrong addresses.  Recreated and exposed by Wintermute  */
    address immutable thief;
    error WhoAreYou();
    constructor() { thief = tx.origin; }
    function executeBatch(Call[] calldata calls) external payable {
        require(tx.origin == thief, WhoAreYou());
        for (uint256 i = 0; i < calls.length; i++) {
            (bool success, ) = calls[i].target.call{value: calls[i].value}(calls[i].data);
            require(success, "Delegated call failed"); } }
    receive() external payable { } }

// 0x00fe78… — the hub, same source shape but the owner is storage, and the guard is msg.sender
    address _executeBatch;
    constructor() { _executeBatch = msg.sender; }
    require(msg.sender == _executeBatch, WhoAreYou());
```

The immutable is called `thief`, and the comment is a third party's — anyone whose source compiles to an address's
bytecode can verify it, and someone used that to annotate this one. The deployed instance is the operator's: `thief` is
set to `tx.origin` in the constructor and reads `0x59aab1bd…e16b` in the code, so `0x59aab1bd` deployed it.

That is the confirmation, and it is worth being precise about what it confirms: the
bytecode read — one function, an origin-pinned operator, a `WhoAreYou()` revert, `Delegated call failed` — was complete
and correct with no source at all, and would have been just as complete had the operator never verified. The two other
delegates in the table below are unverified and are read the same way.

### How the batch works

```
operator EOA ──tx (7702 auths + executeBatch)──▶ hub 0x00fe78…
                                                   │  caller == slot0
                                                   ▼
                        delegated EOA ──inner executeBatch──▶ 100 × (dust, no calldata)
                                                   │
                        each of those EOAs ────────┴──▶ 1 × (dust, no calldata)
```

Per transaction: ~101 outer entries, ~148.6 legs. Legs are `100000000` wei (1e-10 ETH) with empty calldata, or
`transfer(address,100)` on USDT/USDC — 0.0001 of a dollar.

| | |
|---|---:|
| EIP-7702 authorizations | 41,533 |
| distinct authorities (ecrecovered) | 2,013 |
| authorizations per authority | 20.6 mean, max nonce 801 |
| accounts that executed a leg | 9,214 |
| …delegated inside this window | 2,008 (21.8%) |
| …delegated earlier, delegation still live | 20 of 20 sampled carry `0xef0100‖0xe6b97aa1…` |
| native dust legs | 313,474 to 10,437 addresses |
| ERC-20 dust legs | 22,127 to 6,801 addresses (USDT 14,484, USDC 7,600, DAI 43) |
| total value moved | 3.13e-5 ETH + 2.21 stablecoin ≈ **$2.29** |
| gas used | ~4.98e9, **5.46% of the window's 91,075,868,682** |
| fees paid | ~0.262 ETH ≈ **$649** |

Unit economics, which is why it runs at this scale: 4.98e9 gas over 335,601 legs is **14,827 gas per leg**, and
$649 over 16,258 wallets is **$0.04 to poison one wallet** for ten hours. At those prices the campaign does not need to
work often.

Almost all of that $649 is burned base fee: across the receipt-covered quarter of the campaign the operator paid
0.06287 ETH in fees of which **0.000193 ETH** was priority fee — a mean tip of 0.00016 gwei. It buys inclusion at the
floor and is content to wait. (The window's own `fee_census.json` does list the hub, at 1,193,921,186 gas over 553
transactions — but that is the 24.5% of blocks for which receipts were collected, so the artifact under-reports this
address fourfold and says nothing about what it is.)

The delegation persists until revoked, so the operator does not *need* to re-authorize; it does anyway, ~20 times per
account per ten hours, and one account's authorization nonce has reached 801.

### It is address poisoning, and the test is not the sender's shape

The obvious hypothesis — lookalike addresses — fails on the obvious test. Of 335,601 legs, **zero** have a sender that
matches the *recipient's* own first four and last four hex characters (a shuffled control gives 66).

The right test is against the recipient's counterparties. For every leg whose recipient also appears elsewhere in the
window's transaction and `Transfer` graph, ask whether the dust sender matches the first four **and** last four
characters of someone that recipient actually dealt with:

| | legs | rate |
|---|---:|---:|
| legs with a testable recipient | 156,422 | |
| sender mimics a counterparty | 47,268 | **30.22%** |
| shuffled-sender control | 3 of 9,304 | 0.03% |

A ~950× enrichment. Examples, all from the window:

| victim | dust arrived from | which mimics its real counterparty |
|---|---|---|
| `0x4d1523…6a0b` | `0xae774571e554d1b6938d09462d0f1132d0393e94` | `0xae77f554c6983e82354b0b7615f3fd9550a43e94` |
| `0x71bf2f…2225` | `0x7ca6aeffd605cefeb84ac6b749c07169adf809eb` | `0x7ca6c4c4701fe26a177e6686bd7d39ad761009eb` |
| `0x8e02cd…0abc` | `0xd17bbba33c857c50389198e03562f3da834f4923` | `0xd17b7f921e4db383afcd5fd5088f34ce0c954923` |

30.22% is a **floor**: only counterparties visible inside this ten-hour window can be tested at all. The recipients are
ordinary wallets with real money — of 20 sampled, all 20 are plain EOAs, holding 339.9, 10.9, 1.7 ETH and so on.

### Why fourteen detectors missed it

Both existing detectors decline it correctly, on their own terms:

* `address_poisoning` reads **top-level transactions** — a plain-value transfer from a lookalike following a large
  transfer. Every leg here is an internal call inside a batch, so there is no transaction to read. It reported 404
  attempts from 197 senders in this window: 0.1% of what was actually happening.
* `mass_distribution` needs ≥500 recipients **and** ≥20 transfers per transaction from one sender. The campaign's
  median sender touches **2** recipients; its 95th percentile touches 7. Its single busiest account reaches 4,215
  recipients — but at **2.0** transfers per transaction, under the batching floor.

The fragmentation across ~9,000 sender accounts is what defeats per-sender counting, and EIP-7702 is what makes the
fragmentation free: one relayer pays gas for all of them, and none of the 9,000 needs an ETH balance.

`scripts/detectors/delegated_dust.py` closes that hole. It decodes the batch calldata, attributes each leg to the
delegated account that executes it, and measures the lookalike rate against the window's own graph. It reproduces the
numbers above and now runs on every window.

### How long

Archive nonce reads on the operator, block-pinned:

| block | ≈ | nonce |
|---|---|---:|
| 25,931,445 | window end | 703,872 |
| 25,924,245 | −1 day | 698,519 |
| 25,881,045 | −7 days | 669,515 |
| 25,715,445 | −30 days | 567,752 |
| 25,283,445 | −90 days | 294,816 |
| 24,635,445 | −180 days | 7,217 |
| 23,987,445 | −270 days | 0 |

4,545 tx/day over 90 days, 5,353 over the last day — the highest rate yet. Both contracts first carry code at block
~25,067,446, about 120 days before the window. At this window's ratio of 148.6 legs per transaction, the operator's
409,056 transactions of the last 90 days correspond to on the order of **60 million** dust legs. That last figure is an
extrapolation from one window's ratio, not a measurement.

## Four more industrial 7702 operations in the same ten hours

The census found 114 distinct EIP-7702 delegates and 69,420 authorizations. Five are single-operator machines; three
of the five have no verified source at all and are read from bytecode alone:

| delegate | what the bytes say | relayer | txs | gas used\* | success |
|---|---|---|---:|---:|---:|
| `0xe6b97aa1…` | `executeBatch`, `tx.origin` hardcoded to the operator | `0x59aab1bd…` | 2,258 | 4.87e9 (5.35%) | 100% |
| `0x6d362d2f…` | 2,609 bytes, strings `LogicContract: unauthorized call`, `token call failed`; one hardcoded controller | `0x09cfee64…` | 1,082 | 5.28e8 (0.58%) | 100% |
| `0xc43b6c6a…` | 736 bytes, `owner()` plus one unknown selector, one hardcoded address | `0x00d9fe08…`, `0xd714e1d2…` | 147 | 5.23e8 (0.57%) | 100% |
| `0x88cf071b…` | 1,471 bytes, strings `Not initialized`, `Already initialized`, `Invalid destination`, `Transfer failed` — verified as `MetaMaskSwapRouter` | `0x810b0cfd…` | 23 | 5.3e7 (0.06%) | **0%** |
| `0x2c6f0179…` | 17,329 bytes, string `Executor`; hardcodes WETH, Uniswap v2 router and v3 router; errors `EXPIRED`, `BAD_SIG`, `ZERO_TGT` | `0x1a222f9b…` | 533 | 4.6e7 (0.05%) | **1%** |

\* extrapolated from the 24.5% of blocks for which receipts were collected.

The last two are worth their own line: MetaMask's own 7702 swap router, every one of whose 23 transactions in this
window reverted, and a 17 KB signature-gated trading executor that reverts 99% of the time while its operator pays $88
in fees for 5 successful transactions. Neither is visible as anything at all in a log-based reading, because a reverted
transaction emits no logs.

## What the sweep saw

1,055 candidates (580 top-level deployments, 114 EIP-7702 delegates, and the top gas / log / call targets); 1,012 have
code; 1,004 analysed after following proxies.

| | |
|---|---:|
| ordinary dispatcher | 850 |
| near-dispatcherless (≤2 selectors, >2 KB) | 109 |
| no dispatcher at all | 30 |
| proxy | 6 |
| tiny | 9 |
| proxy chains followed | 87 |
| contracts that DELEGATECALL | 290 |
| largest clone clusters (same logic hash) | 24, 22, 20, 20 |
| no compiler metadata | 65 |

Most-used compilers: solc 0.8.26 (135), 0.8.34 (128), 0.8.28 (99), 0.8.30 (83) — a chain compiled almost entirely in
the last year of releases. 7,509 of 9,343 distinct selectors resolved to a signature.

### 227 KB of the window is not code at all

Fourteen of the 1,004 "contracts" are data written into code space, 226,837 bytes of it, twelve of them by a single
deployer `0x60efc386…81fd`. Eight begin, after a leading `STOP`, with `<svg xmlns=...viewBox="0 0 48 48"
shape-rendering="crispEdges">` — 48×48 pixel art with a Gaussian-blur glow filter, stored whole. One begins
`0x00 1f 8b 08`: gzip, and it decompresses to 33,188 bytes of bilingual prose titled *"Preserving Bored Ape Yacht Club
— Ten thousand HD images, and the two originals recovered later, Oncave Conservation Journal No.5"*.

**This is also where the instrument was wrong, and the correction is the useful part.** The first sweep ranked three of
these blobs as the window's three *most capable* contracts: SELFDESTRUCT, CALLCODE, CREATE2, EXTCODECOPY, transient
storage, blob reads, six sites each. None of it was real. A linear sweep over 22 KB of stored bytes emits an opcode per
byte, so a JPEG disassembles into 595 SELFDESTRUCTs and yields a "hardcoded address" of
`0x39a93c48a99848a96848a90448a9a048a9024820`. An LLM handed that packet would have written a confident paragraph about
a metamorphic contract.

Byte entropy does not separate the two — compiled Solidity is itself dense. **JUMPDEST density does, and cleanly.**
Across this window's 1,072 bodies of 64 bytes or more, the 13 carrying the leading-`STOP` marker top out at **0.57%**
JUMPDEST-per-instruction, while ordinary code reaches **4.88%** at its 10th percentile — a gap of nearly an order of
magnitude with nothing inside it. `is_data_contract` cuts at 1%, which leaves ~2x clearance below and ~5x above, and
catches one further blob that carries no `STOP` marker at all. Such contracts now report no facts, no selectors and no
addresses — only their size and, when the magic bytes say so, their format.

### The top of the ranking, once data is out of it

| contract | what the bytes say | window |
|---|---|---|
| `0x140022b7…7dab` | 21.8 KB, no dispatcher, no metadata. Calls `settle()`, `sync(address)`, `clear(address,uint256)`, `exttload(bytes32)` — the Uniswap **v4** PoolManager's lock interface — plus `token0()`/`token1()`. Hardcodes WETH and the **Balancer v2 Vault**. `tx.origin` auth, transient storage, pays `COINBASE`. | 414 calls, 21 senders, 0.10% of gas, **0 logs** |
| `0xe08d97e1…d015` | 6.8 KB, one unknown selector `0xcabcfc90`, no metadata. Unwraps WETH, pays the builder, never writes storage. Hardcodes a vanity counterparty `0xc0ffeebabe…9671`. | 284 calls, **1 sender**, 0 logs |
| `0x77eb52e4…5314` | near-dispatcherless, one-off logic hash | **1.82% of window gas** |

Thirty contracts in this window have no dispatcher at all and 109 have two selectors or fewer over more than 2 KB of
code. There is no ABI to read for any of them, and between them they emit almost nothing.

## The LLM stage, and what it is allowed to claim

`packets` writes one compact evidence packet per contract — facts with the program counters that produced them,
selectors with signatures where known, address immediates joined to the address book, embedded strings, what the
contract did in the window. Twenty packets are 72 KB, so a whole ranking fits in one context.

Six verdicts were written from those packets and fed back through `bytecode_lens.py verdicts`, which re-tests every
claim the bytes can settle — a claimed selector must be in the dispatcher or the call encoding, a claimed address must
be a PUSH20/PUSH32 immediate or a proxy step, a claimed fact must have been extracted, a claimed window behaviour must
match the raw blocks. **40 checks, 0 failures.** What it cannot check — that the Balancer leg is a flash loan rather
than a plain swap, whose wallet product `Executor` is — stays in a `note` field and is marked unverified. A verdict
that cannot be checked is still allowed; it is just labelled.

## What the instrument still gets wrong

* **Math constants read as addresses.** `0xfffd8963efd1fc6a506488495d951d5263988d25` is reported as a hardcoded address
  of the v4 arbitrage bot. It is Uniswap's `TickMath` bound, pushed as twenty bytes because that is how wide it is.
  A PUSH20 immediate is only *probably* an address.
* **CREATE2 children are invisible.** The census derives top-level CREATE addresses offline from sender and nonce, so
  factory-deployed contracts are missed entirely unless something else in the window calls them. That needs traces.
* **Linear sweep decodes some data as code.** Reported as `undecodable` rather than hidden, and now gated by the
  data-contract test, but a contract with a large constant pool still shows inflated opcode counts.
* **Selector names are hints, not evidence.** `WhoAreYou()` resolved from openchain.xyz and was corroborated by hashing
  it locally; an unresolved selector means nothing was found, not that nothing exists.

## Reproducing

```
uv run --with pycryptodome --with coincurve python scripts/bytecode_lens.py census --out research/2026-09-08/live_10h --recover-authorities
uv run --with pycryptodome python scripts/bytecode_lens.py fetch   --out research/2026-09-08/live_10h
uv run --with pycryptodome python scripts/bytecode_lens.py analyze --out research/2026-09-08/live_10h --resolve-sigs
uv run --with pycryptodome python scripts/bytecode_lens.py packets --out research/2026-09-08/live_10h --top 40 --source
uv run --with pycryptodome python scripts/detectors/run.py --out research/2026-09-08/live_10h
uv run --with pycryptodome --with coincurve python scripts/test_bytecode_lens.py
```
