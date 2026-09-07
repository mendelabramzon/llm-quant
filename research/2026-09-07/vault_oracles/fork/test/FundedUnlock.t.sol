// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

interface IERC20View {
    function approve(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}

interface IVault {
    function asset() external view returns (address);
    function deposit(uint256,address) external returns (uint256);
    function redeem(uint256,address,address) external returns (uint256);
    function previewRedeem(uint256) external view returns (uint256);
    function balanceOf(address) external view returns (uint256);
    function fullProfitUnlockDate() external view returns (uint256);
}

interface ICurvePool {
    function coins(uint256) external view returns (address);
    function exchange(int128,int128,uint256,uint256) external returns (uint256);
}

/// Fixed historical state; only the test investor is funded. No donations,
/// keeper reports, protocol storage edits, or future rewards are manufactured.
/// Time warp is a no-other-transactions counterfactual, not a yield forecast.
contract FundedUnlockTest is Test {
    IVault constant SUSG = IVault(0xF17D6f98A5C6EAA99d149079984119e0A4EF6900);
    IVault constant YVUSD = IVault(0x696d02Db93291651ED510704c9b286841d506987);
    IVault constant YVCRVUSD = IVault(0xBF319dDC2Edc1Eb6FDf9910E39b37Be221C8805F);

    function setUp() public view {
        require(block.number == 25920527, "wrong evidence block");
        require(block.timestamp == 1788724439, "wrong evidence timestamp");
    }

    function runPosition(IVault vault, uint256 principal) internal {
        address token = vault.asset();
        deal(token, address(this), principal);
        IERC20View(token).approve(address(vault), principal);
        uint256 gasStart = gasleft();
        uint256 shares = vault.deposit(principal, address(this));
        uint256 depositGas = gasStart - gasleft();
        uint256 instantQuote = vault.previewRedeem(shares);
        assertLe(instantQuote, principal, "no instant windfall");
        uint256 duration = vault.fullProfitUnlockDate() + 1 - block.timestamp;
        vm.warp(block.timestamp + duration);
        uint256 quote = vault.previewRedeem(shares);
        gasStart = gasleft();
        uint256 returned = vault.redeem(shares, address(this), address(this));
        uint256 redeemGas = gasStart - gasleft();
        assertEq(IERC20View(token).balanceOf(address(this)), returned);
        assertGt(returned, principal);
        emit log_named_address("vault", address(vault));
        emit log_named_uint("principal_raw", principal);
        emit log_named_uint("hold_seconds", duration);
        emit log_named_uint("ending_preview_raw", quote);
        emit log_named_uint("redeemed_raw", returned);
        emit log_named_uint("profit_raw", returned-principal);
        emit log_named_uint("capital_cost_5pct_raw", principal*5*duration/100/365 days);
        emit log_named_uint("deposit_call_gas_warm", depositGas);
        emit log_named_uint("redeem_call_gas_warm", redeemGas);
    }

    function testSUSG10k() public { runPosition(SUSG, 10_000e18); }
    function testSUSG100k() public { runPosition(SUSG, 100_000e18); }
    function testYVUSD100k() public { runPosition(YVUSD, 100_000e6); }
    function testYVUSD1m() public { runPosition(YVUSD, 1_000_000e6); }
    function testYVUSD1300k() public { runPosition(YVUSD, 1_300_000e6); }
    function testYVCRVUSD100k() public { runPosition(YVCRVUSD, 100_000e18); }

    function usdcLoop(uint256 principal) internal {
        ICurvePool pool = ICurvePool(address(bytes20(hex"97ba10115da528c113462ede9c20d7adc806d93f")));
        address usdc = pool.coins(0);
        address usg = pool.coins(1);
        assertEq(usg, SUSG.asset());
        deal(usdc, address(this), principal);
        IERC20View(usdc).approve(address(pool), principal);
        // Zero min-out is used solely to measure actual fork output. It is
        // unsuitable for a live transaction. There is no broadcast script.
        uint256 received = pool.exchange(0,1,principal,0);
        IERC20View(usg).approve(address(SUSG), received);
        uint256 shares = SUSG.deposit(received,address(this));
        uint256 duration = SUSG.fullProfitUnlockDate()+1-block.timestamp;
        vm.warp(block.timestamp+duration);
        uint256 redeemed = SUSG.redeem(shares,address(this),address(this));
        IERC20View(usg).approve(address(pool),redeemed);
        uint256 ending = pool.exchange(1,0,redeemed,0);
        assertEq(IERC20View(usdc).balanceOf(address(this)),ending);
        uint256 cost = principal*5*duration/100/365 days;
        assertLt(int256(ending)-int256(principal)-int256(cost),0);
        emit log_named_uint("USDC_principal_raw",principal);
        emit log_named_uint("USG_bought_raw",received);
        emit log_named_uint("USG_redeemed_raw",redeemed);
        emit log_named_uint("USDC_ending_raw",ending);
        emit log_named_int("USDC_profit_before_capital_gas_raw",int256(ending)-int256(principal));
        emit log_named_uint("capital_cost_5pct_raw",cost);
    }

    function testSUSGUSDCFullLoop10k() public { usdcLoop(10_000e6); }
    function testSUSGUSDCFullLoop100k() public { usdcLoop(100_000e6); }
}
