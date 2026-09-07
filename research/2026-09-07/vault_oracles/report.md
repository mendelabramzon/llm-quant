The strongest confirmed mechanism is joining a vault while previously recorded profits are still unlocking. It does not require winning transaction ordering, but the available surplus is small and falls as more capital enters. The scan did not establish an executable oracle arbitrage. The USDC-funded sUSG route failed after actual swaps; yvUSD retained a modest surplus in local fork simulations.

State: Ethereum block **25,920,527**, **2026-09-06 19:53:59 UTC**, hash `0xeaa29e14490fcb00d9e74c42ba80c445e2f68fc6a502db281bd11b78838d07c6`. Research directory uses the local September 7 date. Results describe this snapshot, not a live executable quote.

**What was scanned.** Discovery used 6,555,486 saved logs across 7,867 block files, from two noncontiguous datasets spanning blocks 25,904,413–25,918,420. These yielded 568 vault event emitters, 535 contracts matching core vault getters, and 529 with nonzero `totalAssets`. Matching getters does not establish full ERC-4626 compliance. Oracle inspection covered 228 active Morpho markets and 195 distinct oracle contracts. Discovery was reused from the earlier cutoff; contract state was refreshed at the later snapshot. Inactive contracts, other chains, vaults without these events, and lending protocols outside Morpho are not exhaustively covered. No aggregate dollar TVL is asserted: underlying tokens differ and vaults can hold other vaults.

**Full entry and exit tests.** Each row is an independent fork scenario. Only the investor's starting tokens were funded with a test cheatcode; no protocol profits, donations, keeper reports, privileged actions, or real transactions were manufactured. Time advanced without other transactions. Actual future deposits, strategy losses, reports, liquidity changes, fees and governance actions can change the outcome. A 5% simple annual capital cost is an illustrative assumption, not an observed financing offer. Token-denominated results below are not interchangeable with dollars.

| Position | Starting capital | Hold | Gain after deployed vault/exit fees | After assumed 5% capital cost, before gas |
|---|---:|---:|---:|---:|
| yvUSD | 100,000 USDC | 2.4597 days | 43.429529 USDC | 9.734546 USDC |
| yvUSD | 1,000,000 USDC | 2.4597 days | 396.277269 USDC | 59.327434 USDC |
| yvUSD | 1,300,000 USDC | 2.4597 days | 500.554344 USDC | 62.519559 USDC |
| sUSG, starting with USG | 100,000 USG | 3.8042 days | 98.713736 USG | 46.601705 USG |
| USDC → USG → sUSG → USG → USDC | 100,000 USDC | 3.8042 days | **−1.664748 USDC** | **−53.776778 USDC** |
| yvcrvUSD-2 | 100,000 crvUSD | 5.1135 days | 91.241251 crvUSD | 21.193052 crvUSD |
| jrDOLA, immediately queue withdrawal | 100,000 sDOLA | 4.4187 days | 108.247398 sDOLA | 47.716735 sDOLA |

All 11 tests passed; exact integer outputs and the smaller 10,000-token positions are in [fork-results.txt](fork-results.txt). Passing includes tests that demonstrate losses or blocked direct withdrawals. No live transactions were sent.

**yvUSD: a measurable but thin USDC opportunity.** Vault [`0x696d02db93291651ed510704c9b286841d506987`](https://etherscan.io/address/0x696d02db93291651ed510704c9b286841d506987) reported 9,285,137.438628 USDC of assets. Remaining self-held shares represented approximately 4,074.15 USDC of value scheduled to unlock. A new depositor shares in that release and also dilutes it. Immediate redemption previews did not show a windfall; holding through the remaining release produced the gains above, and the deployed redemption path returned USDC in the fork.

For total assets A, remaining self-held shares L, supply S and deposit C, define D=A×L/S. Ignoring integer rounding and assuming assets stay constant, the remaining gain is:

`G(C) = C × D / (A − D + C)`

Net opportunity surplus is `G(C) − C × annual_capital_cost × seconds/31,536,000 − gas − swap costs`. At 5% capital cost the model's optimum is approximately **1.312 million USDC**, for only **62.52 USDC before gas**. At 8%, the model selects no deposit. The 1.3 million USDC fork validates a nearby position; it does not validate all model sizes. Results at 3%, 5% and 8% are in [economics.json](economics.json).

Gas measurement inside the test is warm and excludes transaction overhead. As a separate sensitivity assumption, budgeting 1.2 million total gas at 1 gwei costs approximately $2.99 using the snapshot ETH/USD feed ($2,490.71925892). At 10 gwei that budget costs $29.89. This is not a live gas estimate or a guaranteed ceiling; conversion to USDC also assumes USDC=$1.

Most yvUSD assets were deployed, with just 0.006001 USDC idle at the vault itself. Its strategies can involve bridges, PT duration and leveraged lending; withdrawals can be delayed. Those exposures are material relative to a surplus of less than one basis point on capital. The mechanism merits monitoring for larger funded releases, but this snapshot does not justify treating it as a scalable low-risk trade. [Yearn's vault mechanics](https://docs.yearn.fi/developers/v3/vault_management), [yvUSD strategy and withdrawal design](https://docs.yearn.fi/getting-started/products/yvaults/yvusd).

**sUSG: works in USG, fails the tested USDC round trip.** Vault [`0xf17d6f98a5c6eaa99d149079984119e0a4ef6900`](https://etherscan.io/address/0xf17d6f98a5c6eaa99d149079984119e0a4ef6900) held 1,141,045.89 USG, all idle, with about 1,223.87 USG represented by remaining locked shares. The contract allowed deposit and later redemption to USG. The USDC pool was resolved from the official peg keeper's deployed `pool()` getter: [`0x97ba10115da528c113462ede9c20d7adc806d93f`](https://etherscan.io/address/0x97ba10115da528c113462ede9c20d7adc806d93f).

The complete 100,000 USDC loop bought 100,437.690462 USG, redeemed 100,536.801270 USG after the wait, and sold it for only 99,998.335252 USDC. The 10,000 USDC loop also lost before capital cost and gas. Both swaps ran sequentially on the same fork, preserving the investor's own pool impact. The result rejects this specific route at these sizes; other routes were not exhausted. Existing USG inventory could still earn the token-denominated carry, but its alternative use and price exposure matter. USG has no collateral redemption at par. Tangent's advertised zero-interest borrowing also gives up collateral rewards, so it is not free funding. [Official addresses](https://docs.tangent.finance/docs/faq/contracts), [sUSG mechanics](https://docs.tangent.finance/docs/usg/susg), [USG peg and borrowing design](https://docs.tangent.finance/docs/usg/overview_usg).

**Two apparent balance anomalies resolved.**

* sVUSD [`0x476310e34d2810f7d79c43a74e4d79405bd7a925`](https://etherscan.io/address/0x476310e34d2810f7d79c43a74e4d79405bd7a925): actual VUSD balance 66,369.288584 exceeded reported assets 65,679.424701. The exact reconciliation is `balance + pendingYield − totalAssetsInCooldown`: approximately `66,369.288584 + 26.937265 − 716.801148`. The excess belongs to queued claims. A funded 10,000 VUSD deposit could not redeem instantly; requesting redemption then waiting seven days returned principal minus one wei, with no extra yield during the queue. See [deployed implementation source](https://etherscan.io/address/0x91edc1f7b0ab6357a85b4d228a00ca68fd2b0661#code).
* jrDOLA [`0x6f80a22a57c7f0257094ea8d426af3f747defbc7`](https://etherscan.io/address/0x6f80a22a57c7f0257094ea8d426af3f747defbc7#code): the approximately 780.89 sDOLA gap is excluded weekly revenue. Revenue from one week streams during the next. Direct redemption requires the designated [withdrawal escrow](https://etherscan.io/address/0x8554d8a6bcc5b6d6eb7bea2189e6a8f8d24c7e45#code), whose deployed fee was 5 basis points. Queueing a new 100,000 sDOLA position required 381,779 seconds; a 10,000 sDOLA position required 131,298 seconds. Shares continue receiving rewards while queued, unlike sVUSD's fixed asset claims. This is first-loss insurance carry: an authorized slashing module can remove backing, including while a withdrawal is pending. Acquisition and conversion of sDOLA to USDC were not validated, so these are sDOLA results only. The DBR auction is a separate transaction-speed competition and is excluded from the proposed approach.

**Oracle findings.** I reconstructed 157 of 195 oracle prices exactly from deployed feed answers, conversion samples and scale factors, with zero arithmetic mismatches. The other 38 remain unresolved/custom; an ABI-looking getter can return a different type, including a bytes32 feed ID. Matching arithmetic is not evidence of accurate economic valuation. Across 23 vault/sample dependencies, conversions at 1×, 10× and 100× differed from exact scaling by no more than 100 raw asset units, consistent with rounding at those samples; this does not establish redeemability or resistance to manipulation.

* The mM1-USD/USD feed [`0xad316aa927c0970c2e8f0b903211d0bd19a10702`](https://etherscan.io/address/0xad316aa927c0970c2e8f0b903211d0bd19a10702) carried a positive timestamp **413.11 hours (17.21 days) old**, pricing collateral at 1.02351724 USDC. The affected market held stored supply of 8.530 million USDC and stored borrowing of 7.714 million USDC. This is a valuation/update-policy investigation lead. No independent current NAV, profitable market discount or executable redemption route was established. Midas describes standard redemptions as dependent on price updates and funds allocated by the strategy manager, so the feed price cannot simply be assumed to be cash available on demand. [Midas redemption terms](https://midas.app/mm1usd).
* Five other positive-timestamp feeds were older than 24 hours, mostly around 52–58 hours across the weekend. Age alone does not prove an erroneous NAV. Eleven feeds returned timestamp zero; those are classified separately, not as decades-old prices. Several explicitly describe exchange-rate adapters.
* Oracle [`0x6779b2f08611906fce70c70c596e05859701235d`](https://etherscan.io/address/0x6779b2f08611906fce70c70c596e05859701235d) had no external feed or vault dependencies and returned a constant value corresponding to 1 USDC per `ILLIQUID_PERPDEX_COLL`. The market had stored supply of 738,997.76 USDC and borrowing of 644,569.92 USDC. The collateral's issuance rights and off-chain backing were not established. A constant-price credit receipt is not by itself evidence of mispricing or public access to borrowed funds.

Morpho's reference feed library deliberately does not enforce staleness, relying on each feed's update guarantees. These checks therefore need feed-specific policies and executable exit prices before becoming trade candidates. [Morpho feed library](https://raw.githubusercontent.com/morpho-org/morpho-blue-oracles/main/src/morpho-chainlink/libraries/ChainlinkDataFeedLib.sol).

**Practical use.** Monitor recorded profit releases and compute the size-dependent surplus before committing capital. Require a successful funded entry/exit fork, an explicit funding or opportunity-cost rate, and actual conversion costs for the starting currency. This can run on confirmed blocks without priority-gas bidding: the edge comes from holding capital through an underallocated reward stream. It still faces competition through dilution. The present evidence favors watching yvUSD for larger releases, using sUSG only when USG inventory economics make sense, and treating junior insurance yield separately from ordinary vault carry. None of the oracle flags currently passes an executable-profit test.

Replay from the repository root:

```sh
python3 scripts/vault_oracle_scan.py --out research/2026-09-07/vault_oracles --offline
python3 scripts/vault_oracle_followup.py --out research/2026-09-07/vault_oracles --offline
python3 scripts/vault_oracle_economics.py --out research/2026-09-07/vault_oracles
cd research/2026-09-07/vault_oracles/fork
forge test --fork-url https://eth.drpc.org --fork-block-number 25920527 -vv
```

The fork uses the existing local `research/2026-09-06/non_mev/fork/lib/forge-std` dependency, Foundry 1.5.1 and Solidity 0.8.24. An archive RPC is required; the scanner's read-only RPC evidence is cached. Use a new output directory for fresh state: the current snapshot cache is intentionally immutable. [Raw evidence hashes](sha256.json), [oracle checks](oracle_checks.json), [accounting candidates](accounting_candidates.json), [validation](validation.json).
