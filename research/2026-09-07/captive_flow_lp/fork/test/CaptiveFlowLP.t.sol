// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import {Test, console2} from "forge-std/Test.sol";
import {IPoolManager} from "v4-core/interfaces/IPoolManager.sol";
import {PoolModifyLiquidityTest} from "v4-core/test/PoolModifyLiquidityTest.sol";
import {PoolSwapTest} from "v4-core/test/PoolSwapTest.sol";
import {PoolKey} from "v4-core/types/PoolKey.sol";
import {PoolId, PoolIdLibrary} from "v4-core/types/PoolId.sol";
import {Currency} from "v4-core/types/Currency.sol";
import {IHooks} from "v4-core/interfaces/IHooks.sol";
import {ModifyLiquidityParams, SwapParams} from "v4-core/types/PoolOperation.sol";
import {StateLibrary} from "v4-core/libraries/StateLibrary.sol";

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
}

/// @notice Proves a small concentrated LP can mint into the REAL Uniswap v4 USDC/USDG pool on a
/// mainnet fork and collect fees from one day of the observed conversion flow, and that the yield
/// obeys the concentration law: fees are proportional to liquidity L, capital is L x band width, so
/// APR scales inversely with the band. A tight (incumbent-like) band reaches the scanner's ~15%; a
/// wide band is safer but earns proportionally less. A large one-way flow knocks a tight band out of
/// range and it stops earning. No broadcast; forge test only.
contract CaptiveFlowLP is Test {
    using StateLibrary for IPoolManager;
    using PoolIdLibrary for PoolKey;

    IPoolManager constant MANAGER = IPoolManager(0x000000000004444c5dc75cB358380D2e3dE08A90);
    address constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant USDG = 0xe343167631d89B6Ffc58B88d6b7fB0228795491D; // 6 decimals
    uint24 constant FEE = 75;      // 0.75 bp pool (0x7da1afe9...)
    int24 constant SPACING = 1;
    uint256 constant PIN_BLOCK = 25920655;
    uint256 constant DAILY_VOLUME = 5_849_096e6;   // captive_flow.json, this pool, 6 dp

    uint160 constant MIN_SQRT = 4295128739 + 1;
    uint160 constant MAX_SQRT = 1461446703485210103287273052203988822378723970342 - 1;

    PoolModifyLiquidityTest lpRouter;
    PoolSwapTest swapRouter;
    PoolKey key;

    receive() external payable {}   // the v4 test routers refund any leftover native value

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"), PIN_BLOCK);
        lpRouter = new PoolModifyLiquidityTest(MANAGER);
        swapRouter = new PoolSwapTest(MANAGER);
        key = PoolKey({
            currency0: Currency.wrap(USDC),
            currency1: Currency.wrap(USDG),
            fee: FEE,
            tickSpacing: SPACING,
            hooks: IHooks(address(0))
        });
        assertEq(
            PoolId.unwrap(key.toId()),
            0x7da1afe9de05528e6559b5845188b98d013843e630b20cd511b974a425267427,
            "poolId mismatch"
        );
        // deal() cannot locate balance slots for these proxied tokens; fund by impersonating a
        // holder of raw balances (the USDC/USDG Curve pool holds ~12M USDC and ~7.6M USDG).
        address whale = 0xc061caa073f3d95F80f8e5428d32D2d76F5e1622;
        vm.startPrank(whale);
        IERC20(USDC).transfer(address(this), 3_000_000e6);
        IERC20(USDG).transfer(address(this), 3_000_000e6);
        vm.stopPrank();
        IERC20(USDC).approve(address(lpRouter), type(uint256).max);
        IERC20(USDG).approve(address(lpRouter), type(uint256).max);
        IERC20(USDC).approve(address(swapRouter), type(uint256).max);
        IERC20(USDG).approve(address(swapRouter), type(uint256).max);
    }

    /// Mint L across [-half,+half] ticks at the peg, replay one day of alternating conversion clips,
    /// withdraw, and return (capital, feeProfit, aprBps). Same L => same fees; wider band => more
    /// capital => lower APR.
    function _runDay(int24 half, int128 L) internal returns (uint256 capital, int256 profit, uint256 aprBps) {
        (, int24 tick,,) = MANAGER.getSlot0(key.toId());
        int24 lo = ((tick - half) / SPACING) * SPACING;
        int24 hi = ((tick + half) / SPACING) * SPACING;

        uint256 u0 = IERC20(USDC).balanceOf(address(this));
        uint256 g0 = IERC20(USDG).balanceOf(address(this));
        lpRouter.modifyLiquidity(key, ModifyLiquidityParams(lo, hi, int256(L), bytes32(0)), "");
        capital = (u0 - IERC20(USDC).balanceOf(address(this))) + (g0 - IERC20(USDG).balanceOf(address(this)));
        require(capital > 0, "no capital used");

        // ~40 alternating clips summing to the day's volume; keeps price near peg.
        uint256 clip = DAILY_VOLUME / 40;
        for (uint256 i = 0; i < 40; i++) {
            bool buy = (i % 2 == 0);
            swapRouter.swap(
                key,
                SwapParams(buy, -int256(clip), buy ? MIN_SQRT : MAX_SQRT),
                PoolSwapTest.TestSettings(false, false),
                ""
            );
        }

        uint256 uA = IERC20(USDC).balanceOf(address(this));
        uint256 gA = IERC20(USDG).balanceOf(address(this));
        lpRouter.modifyLiquidity(key, ModifyLiquidityParams(lo, hi, -int256(L), bytes32(0)), "");
        uint256 back = (IERC20(USDC).balanceOf(address(this)) - uA) + (IERC20(USDG).balanceOf(address(this)) - gA);
        profit = int256(back) - int256(capital);
        aprBps = profit > 0 ? uint256(profit) * 365 * 10000 / capital : 0;
    }

    /// The concentration law, on the real pool: same L, two band widths.
    function test_concentrationLaw() public {
        int128 L = 1e14;
        (uint256 capTight, int256 pTight, uint256 aprTight) = _runDay(2, L);   // +-0.02%
        (uint256 capWide, int256 pWide, uint256 aprWide) = _runDay(10, L);     // +-0.10%
        console2.log("tight band  +-2 ticks: capital(6dp), profit(6dp), APR bps:");
        console2.log(capTight);
        console2.logInt(pTight);
        console2.log(aprTight);
        console2.log("wide band  +-10 ticks: capital(6dp), profit(6dp), APR bps:");
        console2.log(capWide);
        console2.logInt(pWide);
        console2.log(aprWide);

        assertGt(pTight, 0, "tight earned no fees");
        assertGt(pWide, 0, "wide earned no fees");
        // Same L earns ~the same fees; the tight band ties up ~1/5 the capital, so ~5x the APR.
        assertApproxEqRel(pTight, pWide, 0.25e18, "same-L fees should be close");
        assertGt(aprTight, aprWide * 3, "tight band should out-yield wide by the width ratio");
        // Tight, incumbent-like concentration reaches the scanner's double-digit band.
        assertGt(aprTight, 900, "tight APR below scanner band");
        assertLt(aprTight, 5000, "tight APR implausibly high");
    }

    /// A large one-directional flow pushes price out of a tight band: the LP is then fully converted
    /// to one asset and earns nothing more. The concentration failure mode, made explicit.
    function test_outOfRangeStopsEarning() public {
        (, int24 tick,,) = MANAGER.getSlot0(key.toId());
        int24 lo = ((tick - 3) / SPACING) * SPACING;
        int24 hi = ((tick + 3) / SPACING) * SPACING;
        lpRouter.modifyLiquidity(key, ModifyLiquidityParams(lo, hi, int256(1e14), bytes32(0)), "");
        swapRouter.swap(
            key,
            SwapParams(true, -int256(3_000_000e6), MIN_SQRT),
            PoolSwapTest.TestSettings(false, false),
            ""
        );
        (, int24 tickAfter,,) = MANAGER.getSlot0(key.toId());
        console2.log("tick before / after a large one-way flow:");
        console2.logInt(tick);
        console2.logInt(tickAfter);
        assertTrue(tickAfter <= lo || tickAfter >= hi, "expected out of range");
    }
}
