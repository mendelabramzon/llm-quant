// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*
    Atomic, single-transaction, zero-own-capital flash-arbitrage of wstETH against its exact unwrap value.

    wstETH is the one asset that is BOTH atomically redeemable (unwrap -> stETH at an exact on-chain ratio, no queue)
    AND deeply, dislocatably traded (the Uniswap v3 wstETH/WETH pool). Everything else is one or the other:
    atomic-redeem vaults (sDAI, sUSDS) sit at NAV because atomic redemption keeps them there, and the vaults that
    dislocate (sUSDe, LRTs) have a cooldown/queue you cannot flash. So this is the clean atomic loop.

    One transaction, funded entirely by a free Balancer flash loan:
        flash WETH  ->  buy wstETH on Uniswap v3  ->  unwrap wstETH to stETH  ->  sell stETH for ETH on Curve
        ->  wrap ETH to WETH  ->  repay the flash loan  ->  keep the surplus.

    It is risk-free by construction: if the surplus is below `minProfit` the whole transaction reverts, so the worst
    case is the gas of a failed call. That makes it safe to fire speculatively whenever a detector sees wstETH trading
    below its unwrap value by more than the round-trip cost. There is no standing edge in calm markets (wstETH is ~0.5 bp
    rich right now); this fires on a dislocation.
*/

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
}
interface IWETH is IERC20 { function deposit() external payable; }
interface IWstETH { function unwrap(uint256 wstETHAmount) external returns (uint256); }
interface IV3Router {
    struct ExactInputSingleParams {
        address tokenIn; address tokenOut; uint24 fee; address recipient; uint256 deadline;
        uint256 amountIn; uint256 amountOutMinimum; uint160 sqrtPriceLimitX96;
    }
    function exactInputSingle(ExactInputSingleParams calldata) external payable returns (uint256);
}
interface ICurve { function exchange(int128 i, int128 j, uint256 dx, uint256 min_dy) external payable returns (uint256); }
interface IBalancerVault {
    function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external;
}

contract WstEthFlashArb {
    IWETH   constant WETH   = IWETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IWstETH constant WSTETH = IWstETH(0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0);
    IERC20  constant STETH  = IERC20(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84);
    IV3Router constant ROUTER = IV3Router(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    ICurve  constant CURVE  = ICurve(0xDC24316b9AE028F1497c275EB9192a3Ea0f67022); // [ETH(0), stETH(1)]
    IBalancerVault constant BAL = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    uint24  constant POOL_FEE = 100; // 0.01% wstETH/WETH

    address public immutable owner;
    uint256 private minProfit;

    event Arb(uint256 flashWeth, uint256 wstethBought, uint256 ethBack, uint256 profit);

    constructor(address o) { owner = o; }
    receive() external payable {}

    /// Borrow `flashWeth` WETH, run the loop, repay, and send the surplus to `owner`. Reverts unless surplus >= minProfit_.
    function run(uint256 flashWeth, uint256 minProfit_) external {
        require(msg.sender == owner, "not owner");
        minProfit = minProfit_;
        address[] memory tokens = new address[](1); tokens[0] = address(WETH);
        uint256[] memory amounts = new uint256[](1); amounts[0] = flashWeth;
        BAL.flashLoan(address(this), tokens, amounts, "");
    }

    function receiveFlashLoan(address[] memory, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory) external {
        require(msg.sender == address(BAL), "not balancer");
        uint256 flashWeth = amounts[0];

        // 1. WETH -> wstETH on Uniswap v3
        WETH.approve(address(ROUTER), flashWeth);
        uint256 wsteth = ROUTER.exactInputSingle(IV3Router.ExactInputSingleParams({
            tokenIn: address(WETH), tokenOut: address(WSTETH), fee: POOL_FEE, recipient: address(this),
            deadline: block.timestamp, amountIn: flashWeth, amountOutMinimum: 0, sqrtPriceLimitX96: 0
        }));

        // 2. unwrap wstETH -> stETH (exact on-chain ratio)
        WSTETH.unwrap(wsteth);
        uint256 steth = STETH.balanceOf(address(this));

        // 3. stETH -> ETH on Curve
        STETH.approve(address(CURVE), steth);
        uint256 ethBack = CURVE.exchange(1, 0, steth, 0);

        // 4. wrap ETH -> WETH
        WETH.deposit{value: address(this).balance}();

        // 5. repay and keep the surplus
        uint256 owed = flashWeth + feeAmounts[0];
        uint256 bal = WETH.balanceOf(address(this));
        require(bal >= owed + minProfit, "unprofitable");
        WETH.transfer(address(BAL), owed);
        uint256 profit = WETH.balanceOf(address(this));
        WETH.transfer(owner, profit);
        emit Arb(flashWeth, wsteth, ethBack, profit);
    }
}
