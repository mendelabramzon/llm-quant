// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Test.sol";
import "../src/StacyFarmer.sol";

interface IStacyView {
    function stacy() external view returns (address);
    function poolInfo(uint256) external view returns (address token, uint256 allocPoint, uint256 accStacyPerShare, bool withdrawable);
    function totalAllocPoint() external view returns (uint256);
    function rewardsLock() external view returns (address);
}
interface ITok {
    function balanceOf(address) external view returns (uint256);
    function getCherryPopAmount() external view returns (uint256);
    function tokenUniswapPair() external view returns (address);
}

contract FarmTest is Test {
    address constant VAULT = 0x223Bc79156CBb0a6D175Ea6130Cb382D01868DF8;
    address constant BAL   = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
    address constant WETH  = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant USDC  = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant WBTC  = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;
    address constant CHADS = 0x69692D3345010a207b759a7D1af6fc7F38b35c5E;
    address constant EMTRG = 0xBd2949F67DcdC549c6Ebe98696449Fa79D988A9F;

    StacyFarmer farmer;
    address stacy;
    address me = address(0xBEEF);

    function setUp() public {
        stacy = IStacyView(VAULT).stacy();
        vm.prank(me);
        farmer = new StacyFarmer(VAULT, BAL);
    }

    function _fundGate() internal {
        // cherryPop caller must hold >= 10,000 CHADS or >= 1,000 eMTRG. Try to give the farmer eMTRG.
        deal(EMTRG, address(farmer), 2000e18);
        if (ITok(EMTRG).balanceOf(address(farmer)) < 1000e18) {
            deal(CHADS, address(farmer), 20000e18);
        }
        require(ITok(EMTRG).balanceOf(address(farmer)) >= 1000e18 || ITok(CHADS).balanceOf(address(farmer)) >= 10000e18, "gate not funded");
    }

    function test_farm_pools_3_and_4() public {
        _fundGate();
        // dust buffer to absorb LP mint/burn rounding
        deal(USDC, address(farmer), 100e6);
        deal(WETH, address(farmer), 1e18);
        deal(WBTC, address(farmer), 1e8);

        // let ~20 minutes accrue since the last cherryPop so getCherryPopAmount is meaningful
        vm.warp(block.timestamp + 1200);

        uint256 popBefore = ITok(stacy).getCherryPopAmount();
        emit log_named_decimal_uint("cherryPop available (STACY)", popBefore, 18);
        uint256 tA = IStacyView(VAULT).totalAllocPoint();
        (, uint256 ap3,,) = IStacyView(VAULT).poolInfo(3);
        (, uint256 ap4,,) = IStacyView(VAULT).poolInfo(4);
        emit log_named_uint("alloc pid3", ap3);
        emit log_named_uint("alloc pid4", ap4);
        emit log_named_uint("totalAllocPoint", tA);

        uint256 sBefore = ITok(stacy).balanceOf(address(farmer));
        uint256 uBefore = ITok(USDC).balanceOf(address(farmer));
        uint256 wBefore = ITok(WETH).balanceOf(address(farmer));
        uint256 bBefore = ITok(WBTC).balanceOf(address(farmer));
        uint256 lockBefore = ITok(stacy).balanceOf(IStacyView(VAULT).rewardsLock());

        uint256[] memory pids = new uint256[](2);
        pids[0] = 3; pids[1] = 4;
        vm.prank(me);
        farmer.farm(pids, 1000, 1e12);

        uint256 sAfter = ITok(stacy).balanceOf(address(farmer));
        emit log_named_decimal_uint("STACY liquid gained by farmer", sAfter - sBefore, 18);
        emit log_named_decimal_int("USDC net (dust)", int256(ITok(USDC).balanceOf(address(farmer))) - int256(uBefore), 6);
        emit log_named_decimal_int("WETH net (dust)", int256(ITok(WETH).balanceOf(address(farmer))) - int256(wBefore), 18);
        emit log_named_decimal_int("WBTC net (dust)", int256(ITok(WBTC).balanceOf(address(farmer))) - int256(bBefore), 8);
        emit log_named_decimal_uint("rewardsLock STACY delta (all pools' 75% lock)", ITok(stacy).balanceOf(IStacyView(VAULT).rewardsLock()) - lockBefore, 18);

        // theoretical liquid capture from pools 3+4: bounty(1% of pop) + 25% * 95% * (ap3+ap4)/tA * 99% * pop
        uint256 poolShare = popBefore * (ap3 + ap4) / tA;              // pools 3+4 share of the pop
        uint256 toVault = poolShare * 99 / 100;                         // 99% goes to vault (1% is caller bounty)
        uint256 liquidTheory = (toVault * 95 / 100) * 25 / 100 + popBefore / 100;
        emit log_named_decimal_uint("theory liquid (STACY)", liquidTheory, 18);

        assertGt(sAfter, sBefore, "farmer should have gained STACY");
    }
}
