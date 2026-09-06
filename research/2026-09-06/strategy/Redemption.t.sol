// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/RedemptionArb.sol";

/*
    Fork proof of the redemption-liquidity thesis (run against a mainnet fork):
      forge test --fork-url <rpc> --fork-block-number <head> -vv

    T1 primitives : an atomic ERC-4626 (sDAI) redeems at its NAV; a Balancer flash loan is free.
    T2 natural ask: buy sUSDe at today's market ask, cool down 1 day, redeem USDe at NAV, sell back — the round
                    trip is ~flat (markets are efficient today: there is no standing discount to capture).
    T3 stressed   : a large holder dumps sUSDe into the deepest pool (a realistic derisk event), opening a discount;
                    the same contract buys below NAV, waits out the 1-day cooldown, and redeems at NAV for a
                    measured profit. This is the non-MEV edge — the convergence takes a day, so no bot can race it.
*/

interface ICurveRead { function coins(uint256) external view returns (address); function get_dy(int128,int128,uint256) external view returns (uint256); }

contract RedemptionTest is Test {
    address constant USDC  = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant USDE  = 0x4c9EDD5852cd905f086C759E8383e09bff1E68B3;
    address constant SUSDE = 0x9D39A5DE30e57443BfF2A8307A4256c8797A3497;
    address constant DAI   = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    address constant SDAI  = 0x83F20F44975D03b1b09e64809B757c47f942BEeA;

    address constant P_SDAI_SUSDE = 0x167478921b907422F8E88B43C4Af2B8BEa278d3A; // [sDAI, sUSDe], ~$5.4M
    address constant USDT         = 0xdAC17F958D2ee523a2206206994597C13D831ec7;
    address constant P_USDE_USDT  = 0x5B03CcCAb7BA3010fA5CAd23746cbf0794938e96; // [USDT, USDe], deepest USDe DEX pool (~$0.6M)
    address owner = address(0xA11CE);

    function _buy() internal pure returns (Hop[] memory p) {   // sDAI -> sUSDe
        p = new Hop[](1);
        p[0] = Hop({pool: P_SDAI_SUSDE, i: 0, j: 1, tokenIn: SDAI, tokenOut: SUSDE});
    }
    function _sell() internal pure returns (Hop[] memory p) {  // USDe -> USDT (deepest USDe pool)
        p = new Hop[](1);
        p[0] = Hop({pool: P_USDE_USDT, i: 1, j: 0, tokenIn: USDE, tokenOut: USDT});
    }
    function _usdOfSdai(uint256 sdai) internal view returns (uint256) { // USD value of an sDAI amount (18dp) in 6dp
        return IERC4626(SDAI).previewRedeem(sdai) / 1e12; // sDAI->DAI(≈$1), scale 18->6
    }

    // ---------- T1: primitives ----------
    function test_AtomicRedeemAtNav_and_FreeFlash() public {
        uint256 shares = 1_000_000e18;
        deal(SDAI, address(this), shares);
        uint256 nav = IERC4626(SDAI).previewRedeem(shares);
        uint256 before = IERC20(DAI).balanceOf(address(this));
        IERC4626(SDAI).redeem(shares, address(this), address(this));
        uint256 got = IERC20(DAI).balanceOf(address(this)) - before;
        emit log_named_decimal_uint("sDAI redeemed (shares)", shares, 18);
        emit log_named_decimal_uint("DAI paid at NAV", got, 18);
        assertApproxEqRel(got, nav, 1e12);
        assertGt(got, shares);

        FlashProbe probe = new FlashProbe();
        uint256 fee = probe.borrow(DAI, 100_000e18); // Balancer holds ~112k DAI; larger size uses Maker/Morpho (also free)
        emit log_named_decimal_uint("Balancer flash fee on 100k DAI", fee, 18);
        assertEq(fee, 0);
    }

    // ---------- lifecycle helper ----------
    function _lifecycle(uint256 sdaiIn) internal returns (int256 pnlUsd, uint256 costUsd, uint256 navLockedUsd) {
        CooldownArb strat = new CooldownArb(owner, SUSDE);
        deal(SDAI, owner, sdaiIn);
        costUsd = _usdOfSdai(sdaiIn);
        vm.startPrank(owner);
        IERC20(SDAI).approve(address(strat), sdaiIn);
        (uint256 shares, uint256 navLocked) = strat.enter(_buy(), sdaiIn, 0);
        vm.stopPrank();
        navLockedUsd = navLocked / 1e12; // USDe(18dp,≈$1) -> 6dp
        emit log_named_decimal_uint("sDAI spent (USD)", costUsd, 6);
        emit log_named_decimal_uint("sUSDe bought", shares, 18);
        emit log_named_decimal_uint("USDe NAV locked (USD)", navLockedUsd, 6);

        vm.warp(block.timestamp + 1 days + 1);
        vm.roll(block.number + 1);

        uint256 b4 = IERC20(USDT).balanceOf(owner);
        vm.prank(owner);
        strat.exit(_sell(), 0);
        uint256 usdcOut = IERC20(USDT).balanceOf(owner) - b4;
        emit log_named_decimal_uint("USDT realized after 1 day (via $0.6M USDe pool)", usdcOut, 6);
        pnlUsd = int256(usdcOut) - int256(costUsd);
    }

    function test_Cooldown_NaturalAsk() public {
        (int256 pnl, uint256 cost, uint256 nav) = _lifecycle(200_000e18);
        emit log_named_int("PnL vs cost (USD 6dp) at natural ask", pnl);
        emit log_named_int("entry discount captured (bps)", (int256(nav) - int256(cost)) * 10000 / int256(cost));
        // documentary: no standing discount today, so ~flat/slightly negative after fees
    }

    function _dump(uint256 amt) internal {
        address seller = address(0xBEEF);
        deal(SUSDE, seller, amt);
        vm.startPrank(seller);
        IERC20(SUSDE).approve(P_SDAI_SUSDE, amt);
        ICurve(P_SDAI_SUSDE).exchange(1, 0, amt, 0); // sell sUSDe -> sDAI, push sUSDe below NAV
        vm.stopPrank();
    }

    // Sensitivity: how large a derisk sell into the $5.4M pool is needed before the 1-day redemption trade
    // (fixed $118k buy) clears the entry discount AND the thin USDe exit, and what it nets. Honest about capacity.
    function test_Cooldown_StressSweep() public {
        uint256 buy = 100_000e18; // ~$118k
        uint256[5] memory dumps = [uint256(250_000e18), 500_000e18, 750_000e18, 1_000_000e18, 1_500_000e18];
        bool anyProfit;
        emit log_string("dump sUSDe | entry disc bps | USDe exit slip bps | net PnL USD | return %");
        for (uint256 k = 0; k < dumps.length; k++) {
            uint256 id = vm.snapshotState();
            _dump(dumps[k]);
            (int256 pnl, uint256 cost, uint256 navUsd, uint256 realized) = _lifecycleR(buy);
            int256 discBps = (int256(navUsd) - int256(cost)) * 10000 / int256(cost);
            int256 slipBps = (int256(navUsd) - int256(realized)) * 10000 / int256(navUsd);
            emit log_named_decimal_uint("dump sUSDe", dumps[k], 18);
            emit log_named_int("  entry discount (bps)", discBps);
            emit log_named_int("  USDe exit slippage (bps)", slipBps);
            emit log_named_int("  net PnL (USD 6dp)", pnl);
            emit log_named_int("  return on $ deployed (bps)", pnl * 10000 / int256(cost));
            if (pnl > 0) anyProfit = true;
            vm.revertToState(id);
        }
        assertTrue(anyProfit); // the contract nets a profit once the derisk sell is large enough
    }

    function _lifecycleR(uint256 sdaiIn) internal returns (int256 pnlUsd, uint256 costUsd, uint256 navLockedUsd, uint256 realized) {
        CooldownArb strat = new CooldownArb(owner, SUSDE);
        deal(SDAI, owner, sdaiIn);
        costUsd = _usdOfSdai(sdaiIn);
        vm.startPrank(owner);
        IERC20(SDAI).approve(address(strat), sdaiIn);
        (, uint256 navLocked) = strat.enter(_buy(), sdaiIn, 0);
        vm.stopPrank();
        navLockedUsd = navLocked / 1e12;
        vm.warp(block.timestamp + 1 days + 1);
        vm.roll(block.number + 1);
        uint256 b4 = IERC20(USDT).balanceOf(owner);
        vm.prank(owner);
        strat.exit(_sell(), 0);
        realized = IERC20(USDT).balanceOf(owner) - b4;
        pnlUsd = int256(realized) - int256(costUsd);
    }
}

contract FlashProbe {
    IBalancerVault constant BAL = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    uint256 public lastFee;
    function borrow(address token, uint256 amount) external returns (uint256) {
        address[] memory t = new address[](1); t[0] = token;
        uint256[] memory a = new uint256[](1); a[0] = amount;
        BAL.flashLoan(address(this), t, a, "");
        return lastFee;
    }
    function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory fees, bytes memory) external {
        lastFee = fees[0];
        IERC20(tokens[0]).transfer(msg.sender, amounts[0] + fees[0]);
    }
}
