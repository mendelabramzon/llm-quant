// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";

interface IERC20 { function balanceOf(address) external view returns (uint256); function approve(address,uint256) external returns (bool); }
interface IBPool {
    function swapExactAmountIn(address tokenIn, uint256 tokenAmountIn, address tokenOut, uint256 minAmountOut, uint256 maxPrice) external returns (uint256 tokenAmountOut, uint256 spotAfter);
    function joinswapExternAmountIn(address tokenIn, uint256 tokenAmountIn, uint256 minPoolAmountOut) external returns (uint256 poolAmountOut);
    function exitswapPoolAmountIn(address tokenOut, uint256 poolAmountIn, uint256 minAmountOut) external returns (uint256 tokenAmountOut);
    function getBalance(address) external view returns (uint256);
    function getSwapFee() external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

// Does the tiny Balancer v1 pool 0x69d460e0 (DAI/USDC/WETH/REQ, 100 BPT, 0.15% fee) leak on a round trip?
contract BalV1LeakTest is Test {
    address constant POOL = 0x69d460e01070A7BA1bc363885bC8F4F0daa19Bf5;
    address constant DAI  = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    address constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant REQ  = 0x8f8221aFbB33998d8584A2B05749bA73c37a938a;
    uint256 constant MAX = type(uint256).max;

    function setUp() public {
        deal(DAI, address(this), 5_000e18);
        deal(REQ, address(this), 5_000_000e18);
        IERC20(DAI).approve(POOL, MAX);
        IERC20(REQ).approve(POOL, MAX);
        IERC20(USDC).approve(POOL, MAX);
    }

    function test_state() public {
        emit log_named_decimal_uint("pool DAI",  IBPool(POOL).getBalance(DAI), 18);
        emit log_named_decimal_uint("pool USDC", IBPool(POOL).getBalance(USDC), 6);
        emit log_named_decimal_uint("pool REQ",  IBPool(POOL).getBalance(REQ), 18);
        emit log_named_decimal_uint("swap fee",  IBPool(POOL).getSwapFee(), 18);
        emit log_named_decimal_uint("BPT supply", IBPool(POOL).totalSupply(), 18);
    }

    // A: single-asset join then immediate exit (same token). Fee is charged on the swapped portion.
    function test_JoinExit_roundtrip() public {
        uint256 before = IERC20(DAI).balanceOf(address(this));
        uint256 bpt = IBPool(POOL).joinswapExternAmountIn(DAI, 50e18, 0);
        uint256 out = IBPool(POOL).exitswapPoolAmountIn(DAI, bpt, 0);
        int256 net = int256(IERC20(DAI).balanceOf(address(this))) - int256(before);
        emit log_named_decimal_uint("join 50 DAI -> BPT", bpt, 18);
        emit log_named_decimal_uint("exit BPT -> DAI", out, 18);
        emit log_named_int("net DAI (wei)", net);
    }

    // B: swap round trip DAI -> REQ -> DAI (pays fee twice).
    function test_Swap_roundtrip() public {
        uint256 before = IERC20(DAI).balanceOf(address(this));
        (uint256 req,)  = IBPool(POOL).swapExactAmountIn(DAI, 20e18, REQ, 0, MAX);
        (uint256 back,) = IBPool(POOL).swapExactAmountIn(REQ, req, DAI, 0, MAX);
        int256 net = int256(IERC20(DAI).balanceOf(address(this))) - int256(before);
        emit log_named_decimal_uint("DAI->REQ", req, 18);
        emit log_named_decimal_uint("REQ->DAI back", back, 18);
        emit log_named_int("net DAI (wei)", net);
    }

    // C: the bot's shape — a geometric ladder of many tiny swaps, then measure the net across the group.
    function test_Ladder() public {
        uint256 beforeDai = IERC20(DAI).balanceOf(address(this));
        uint256 beforeUsdc = IERC20(USDC).balanceOf(address(this));
        uint256 amt = 1e15; // 0.001 DAI
        for (uint256 k = 0; k < 40; k++) {
            // DAI -> USDC then USDC -> DAI, growing 1.5x each step (bot's pattern)
            try IBPool(POOL).swapExactAmountIn(DAI, amt, USDC, 0, MAX) returns (uint256 usdc, uint256) {
                IBPool(POOL).swapExactAmountIn(USDC, usdc, DAI, 0, MAX);
            } catch { break; }
            amt = amt * 3 / 2;
        }
        int256 netDai = int256(IERC20(DAI).balanceOf(address(this))) - int256(beforeDai);
        int256 netUsdc = int256(IERC20(USDC).balanceOf(address(this))) - int256(beforeUsdc);
        emit log_named_int("ladder net DAI (wei)", netDai);
        emit log_named_int("ladder net USDC (6dp)", netUsdc);
    }

    // D: tiny-amount rounding — swap the smallest unit repeatedly and check output rounding.
    function test_TinyRounding() public {
        for (uint256 amt = 1; amt <= 1000; amt *= 10) {
            (uint256 out,) = IBPool(POOL).swapExactAmountIn(DAI, amt, USDC, 0, MAX);
            emit log_named_uint("DAI wei in", amt);
            emit log_named_uint("  USDC out (6dp units)", out);
        }
    }
}
