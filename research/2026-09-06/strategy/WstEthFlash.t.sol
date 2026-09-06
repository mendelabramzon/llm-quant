// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/WstEthFlashArb.sol";

interface IV3Pool { function token0() external view returns (address); function slot0() external view returns (uint160 sqrtPriceX96, int24, uint16, uint16, uint16, uint8, bool); }
interface IWst { function getStETHByWstETH(uint256) external view returns (uint256); }
interface ICurveT { function get_dy(int128,int128,uint256) external view returns (uint256); }
interface IRouterT {
    struct P { address tokenIn; address tokenOut; uint24 fee; address recipient; uint256 deadline; uint256 amountIn; uint256 amountOutMinimum; uint160 sqrtPriceLimitX96; }
    function exactInputSingle(P calldata) external payable returns (uint256);
}

contract WstEthFlashTest is Test {
    address constant WETH   = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant WSTETH = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0;
    address constant ROUTER = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
    address owner = address(0xA11CE);

    function _dumpWsteth(uint256 amt) internal {
        // A large wstETH sell into the v3 pool pushes wstETH below its unwrap value (a realistic LST-derisk flow).
        address seller = address(0xBEEF);
        deal(WSTETH, seller, amt);
        vm.startPrank(seller);
        IERC20(WSTETH).approve(ROUTER, amt);
        IRouterT(ROUTER).exactInputSingle(IRouterT.P({
            tokenIn: WSTETH, tokenOut: WETH, fee: 100, recipient: seller, deadline: block.timestamp,
            amountIn: amt, amountOutMinimum: 0, sqrtPriceLimitX96: 0
        }));
        vm.stopPrank();
    }

    function test_NaturalMarket_noEdge() public {
        WstEthFlashArb arb = new WstEthFlashArb(owner);
        vm.prank(owner);
        // reverts because wstETH is ~0.5 bp rich right now: no atomic edge in a calm market
        vm.expectRevert();
        arb.run(200e18, 1); // require >=1 wei profit
        assertEq(IERC20(WETH).balanceOf(owner), 0); // zero own capital, nothing lost
    }

    function test_Dislocation_capturedInOneTx() public {
        WstEthFlashArb arb = new WstEthFlashArb(owner);
        assertEq(IERC20(WETH).balanceOf(owner), 0); // owner starts with ZERO capital

        _dumpWsteth(500e18); // a ~$1.25M wstETH sell opens a ~1bp dislocation in the deep pool

        uint256 flash = 200e18; // borrowed from Balancer (holds ~1,135 WETH); owner posts nothing
        vm.prank(owner);
        arb.run(flash, 0);

        uint256 profit = IERC20(WETH).balanceOf(owner);
        emit log_named_decimal_uint("flash-borrowed WETH", flash, 18);
        emit log_named_decimal_uint("owner WETH profit (own capital = 0)", profit, 18);
        emit log_named_decimal_uint("profit in USD (ETH=2500)", profit * 2500, 18);
        assertGt(profit, 0);
    }

    address constant POOL  = 0x109830a1AAaD605BbF02a9dFA7B0B92EC2FB7dAa;
    address constant CURVE = 0xDC24316b9AE028F1497c275EB9192a3Ea0f67022;

    // wstETH ask (WETH per wstETH) from the pool mid vs its exact unwrap value in WETH -> the dislocation the arb sees.
    function _dislocationBps() internal view returns (int256) {
        (uint160 sp,,,,,,) = IV3Pool(POOL).slot0();
        uint256 mid = FullMath.mulDiv(uint256(sp) * uint256(sp), 1e18, 1 << 192); // WETH per wstETH, 1e18
        uint256 unwrap = IWst(WSTETH).getStETHByWstETH(1e18);
        uint256 stEth  = ICurveT(CURVE).get_dy(1, 0, 1e18);       // 1 stETH -> ETH
        uint256 unwrapVal = unwrap * stEth / 1e18;                 // wstETH -> ETH atomic value
        return (int256(unwrapVal) - int256(mid)) * 10000 / int256(mid); // >0 = wstETH cheap = arb edge
    }

    // Honest sensitivity: profit is bounded by the dislocation depth someone else's sell creates and the arb size.
    function test_DislocationSweep() public {
        uint256 flash = 200e18; // ~$0.5M borrowed, sized to the pool
        uint256[5] memory dumps = [uint256(300e18), 400e18, 500e18, 600e18, 700e18];
        emit log_string("wstETH dumped | wstETH dislocation bps | WETH profit | profit bps on flash");
        bool any;
        for (uint256 k = 0; k < dumps.length; k++) {
            uint256 id = vm.snapshotState();
            _dumpWsteth(dumps[k]);
            int256 disc = _dislocationBps();
            WstEthFlashArb arb = new WstEthFlashArb(owner);
            vm.prank(owner);
            try arb.run(flash, 0) {
                uint256 p = IERC20(WETH).balanceOf(owner);
                emit log_named_decimal_uint("dumped wstETH", dumps[k], 18);
                emit log_named_int("  wstETH dislocation (bps)", disc);
                emit log_named_decimal_uint("  WETH profit", p, 18);
                emit log_named_int("  profit on flash (bps)", int256(p) * 10000 / int256(flash));
                if (p > 0) any = true;
            } catch {
                emit log_named_decimal_uint("dumped wstETH (arb reverted, no edge)", dumps[k], 18);
                emit log_named_int("  wstETH dislocation (bps)", disc);
            }
            vm.revertToState(id);
        }
        assertTrue(any);
    }
}

// Minimal 512-bit mulDiv for the price math.
library FullMath {
    function mulDiv(uint256 a, uint256 b, uint256 d) internal pure returns (uint256) {
        unchecked {
            uint256 mm = mulmod(a, b, type(uint256).max);
            uint256 lo = a * b;
            uint256 hi = mm - lo - (mm < lo ? 1 : 0);
            if (hi == 0) return lo / d;
            require(d > hi);
            uint256 r = mulmod(a, b, d);
            lo = lo - r; hi = hi - (r > lo ? 1 : 0);
            uint256 pow2 = d & (~d + 1);
            d /= pow2; lo /= pow2;
            lo += hi * ((~pow2 + 1) / pow2 + 1);
            uint256 inv = (3 * d) ^ 2;
            inv *= 2 - d * inv; inv *= 2 - d * inv; inv *= 2 - d * inv;
            inv *= 2 - d * inv; inv *= 2 - d * inv; inv *= 2 - d * inv;
            return lo * inv;
        }
    }
}
