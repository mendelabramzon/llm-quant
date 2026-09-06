// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

interface Token {
    function approve(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}
interface Pool {
    function supply(address, uint256, address, uint16) external;
    function withdraw(address, uint256, address) external returns (uint256);
}
interface Comet {
    function supply(address, uint256) external;
    function withdraw(address, uint256) external;
    function accrueAccount(address) external;
    function balanceOf(address) external view returns (uint256);
    function getUtilization() external view returns (uint256);
    function getSupplyRate(uint256) external view returns (uint64);
}
interface SavingsVault {
    function deposit(uint256, address) external returns (uint256);
    function redeem(uint256, address, address) external returns (uint256);
}

/// Hypothetical funded deposits on an unchanged historical fork. Not future profit.
/// Only the starting cash is assigned with deal(); all interest and withdrawals use
/// deployed protocol code. No flash loans, swaps, private order flow or builder calls.
contract PatientSupplyTest is Test {
    address constant ASSET = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    Pool constant AAVE = Pool(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
    Comet constant COMET = Comet(0xc3d688B66703497DAA19211EEdff47f25384cdc3);
    uint256 constant YEAR = 365 days;

    function setUp() public view {
        require(block.number == 25_918_293, "wrong evidence block");
    }

    function aaveIncome(uint256 amount) internal returns (uint256) {
        deal(ASSET, address(this), amount);
        Token(ASSET).approve(address(AAVE), amount);
        AAVE.supply(ASSET, amount, address(this), 0);
        vm.warp(block.timestamp + 1 days);
        AAVE.withdraw(ASSET, type(uint256).max, address(this));
        return Token(ASSET).balanceOf(address(this)) - amount;
    }

    function compoundIncome(uint256 amount, bool competingSupply)
        internal returns (uint256 income, uint256 entryRate, uint256 gasUnits)
    {
        deal(ASSET, address(this), amount);
        Token(ASSET).approve(address(COMET), amount);
        uint256 beforeGas = gasleft();
        COMET.supply(ASSET, amount);
        gasUnits = beforeGas - gasleft();
        entryRate = uint256(COMET.getSupplyRate(COMET.getUtilization())) * YEAR;
        if (competingSupply) {
            vm.warp(block.timestamp + 1 hours);
            address other = address(0xBEEF);
            deal(ASSET, other, 10_000_000e6);
            vm.startPrank(other);
            Token(ASSET).approve(address(COMET), 10_000_000e6);
            COMET.supply(ASSET, 10_000_000e6);
            vm.stopPrank();
            vm.warp(block.timestamp + 23 hours);
        } else {
            vm.warp(block.timestamp + 1 days);
        }
        beforeGas = gasleft();
        COMET.accrueAccount(address(this));
        uint256 balance = COMET.balanceOf(address(this));
        COMET.withdraw(ASSET, balance);
        gasUnits += beforeGas - gasleft();
        income = Token(ASSET).balanceOf(address(this)) - amount;
    }

    function compare(uint256 amount) internal returns (int256 incremental) {
        uint256 snapshot = vm.snapshotState();
        uint256 baseline = aaveIncome(amount);
        vm.revertToState(snapshot);
        (uint256 income, uint256 rate, uint256 gasUnits) = compoundIncome(amount, false);
        incremental = int256(income) - int256(baseline);
        emit log_named_decimal_uint("principal USDC", amount, 6);
        emit log_named_decimal_uint("Aave one-day interest USDC", baseline, 6);
        emit log_named_decimal_uint("Compound one-day interest USDC", income, 6);
        emit log_named_decimal_uint("Compound post-deposit APR fraction", rate, 18);
        emit log_named_decimal_int("incremental USDC before gas", incremental, 6);
        emit log_named_uint("internal supply+accrue+withdraw gas, excludes approval/tx overhead", gasUnits);
    }

    function test_100kPaysMoreOnStaticFork() public {
        assertGt(compare(100_000e6), 3e6);
    }

    function test_1mPaysMoreOnStaticFork() public {
        int256 increment = compare(1_000_000e6);
        assertGt(increment, 13e6);
        assertLt(increment, 15e6);
    }

    function test_10mDestroysRateAdvantage() public {
        assertLt(compare(10_000_000e6), 0);
    }

    function test_LaterSupplyCanReverseTheAdvantage() public {
        uint256 snapshot = vm.snapshotState();
        uint256 baseline = aaveIncome(1_000_000e6);
        vm.revertToState(snapshot);
        (uint256 income,,) = compoundIncome(1_000_000e6, true);
        emit log_named_decimal_uint("Compound interest after another 10m arrives at hour one", income, 6);
        emit log_named_decimal_uint("Aave unchanged-fork alternative", baseline, 6);
        assertLt(income, baseline);
    }

    function test_UsdsSavingsRedeemsSameUnderlying() public {
        address usds = 0xdC035D45d973E3EC169d2276DDab16f1e407384F;
        SavingsVault vault = SavingsVault(0xa3931d71877C0E7a3148CB7Eb4463524FEc27fbD);
        uint256 amount = 1_000_000e18;
        deal(usds, address(this), amount);
        Token(usds).approve(address(vault), amount);
        uint256 shares = vault.deposit(amount, address(this));
        vm.warp(block.timestamp + 1 days);
        uint256 received = vault.redeem(shares, address(this), address(this));
        assertEq(received, Token(usds).balanceOf(address(this)));
        assertGt(received, amount + 90e18);
        emit log_named_decimal_uint("USDS one-day savings interest, unchanged governance rate", received-amount, 18);
    }
}
