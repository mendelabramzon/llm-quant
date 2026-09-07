// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./FundedUnlock.t.sol";

interface IVetro is IVault {
    function requestRedeem(uint256,address) external returns (uint256,uint256);
    function claimWithdraw(uint256,address) external returns (uint256);
    function cooldownDuration() external view returns (uint256);
    function totalAssets() external view returns (uint256);
    function totalAssetsInCooldown() external view returns (uint256);
}

interface IYieldDistributorView {
    function pendingYield() external view returns (uint256);
}

interface IWithdrawalEscrow {
    function queueWithdrawal(uint256,uint256) external;
    function exitWindows(address) external view returns (uint128,uint128);
    function completeWithdraw() external;
}

contract AccountingExitTest is Test {
    function setUp() public view {
        require(block.number == 25920527, "wrong evidence block");
    }

    function testSVUSDGapBelongsToQueuedWithdrawals() public {
        IVetro v = IVetro(address(bytes20(hex"476310e34d2810f7d79c43a74e4d79405bd7a925")));
        IYieldDistributorView distributor = IYieldDistributorView(address(bytes20(hex"55745265ba172378cf45d224f09f0673cb470cef")));
        address asset = v.asset();
        assertEq(v.totalAssets(), IERC20View(asset).balanceOf(address(v)) + distributor.pendingYield() - v.totalAssetsInCooldown());
        uint256 principal = 10_000e18;
        deal(asset,address(this),principal);
        IERC20View(asset).approve(address(v),principal);
        uint256 shares = v.deposit(principal,address(this));
        vm.expectRevert(bytes4(keccak256("CooldownEnabled()")));
        v.redeem(shares,address(this),address(this));
        (uint256 requestId,uint256 lockedAssets) = v.requestRedeem(shares,address(this));
        assertLe(lockedAssets,principal);
        assertEq(IERC20View(asset).balanceOf(address(this)),0);
        uint256 duration = v.cooldownDuration();
        vm.warp(block.timestamp + duration);
        uint256 received = v.claimWithdraw(requestId,address(this));
        assertEq(received,lockedAssets);
        assertEq(IERC20View(asset).balanceOf(address(this)),received);
        emit log_named_uint("principal_raw",principal);
        emit log_named_uint("cooldown_seconds",duration);
        emit log_named_uint("received_raw",received);
    }

    function jrDolaPosition(uint256 principal) internal {
        IVault v = IVault(address(bytes20(hex"6f80a22a57c7f0257094ea8d426af3f747defbc7")));
        IWithdrawalEscrow escrow = IWithdrawalEscrow(address(bytes20(hex"8554d8a6bcc5b6d6eb7bea2189e6a8f8d24c7e45")));
        address asset = v.asset();
        deal(asset,address(this),principal);
        IERC20View(asset).approve(address(v),principal);
        uint256 shares = v.deposit(principal,address(this));
        vm.expectRevert(bytes("Only withdraw escrow"));
        v.redeem(shares,address(this),address(this));
        IERC20View(address(v)).approve(address(escrow),shares);
        escrow.queueWithdrawal(shares,type(uint256).max);
        (uint128 start,) = escrow.exitWindows(address(this));
        uint256 duration = start-block.timestamp;
        assertEq(IERC20View(asset).balanceOf(address(this)),0);
        vm.warp(start);
        escrow.completeWithdraw();
        uint256 received = IERC20View(asset).balanceOf(address(this));
        emit log_named_uint("sDOLA_principal_raw",principal);
        emit log_named_uint("queue_seconds",duration);
        emit log_named_uint("sDOLA_received_after_exit_fee_raw",received);
        emit log_named_int("sDOLA_profit_raw",int256(received)-int256(principal));
        emit log_named_uint("capital_cost_5pct_raw",principal*5*duration/100/365 days);
    }

    function testJrDOLA10kQueuedExit() public { jrDolaPosition(10_000e18); }
    function testJrDOLA100kQueuedExit() public { jrDolaPosition(100_000e18); }
}
