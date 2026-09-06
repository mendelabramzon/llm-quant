// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*
    Redemption-liquidity strategies: capture the discount at which a protocol's *redeemable* claim trades below the
    value the protocol itself pays on redemption. This is the non-MEV edge: the convergence clears through the
    protocol's redemption path (a cooldown or a queue), which a latency bot cannot race because it takes time.

    CooldownArb  — buys sUSDe (or any cooldown-gated ERC-4626-like vault) below NAV through Curve, enters the
                   protocol cooldown at full NAV, and after the cooldown redeems the underlying and sells it back.
                   The realized edge is (NAV locked at cooldown) - (price paid), minus two Curve legs and gas.

    FlashNavArb  — for vaults whose redemption is *atomic* (e.g. sDAI -> DAI): flash-borrow the asset from Balancer
                   (zero fee), buy the share below NAV, redeem it at NAV in the same transaction, repay, keep the rest.
                   Zero capital, risk-free by construction (reverts unless profit >= minProfit).

    Interfaces are intentionally minimal; addresses and routes are supplied by the caller so the contracts are not
    pinned to one venue. Owner-gated; funds only ever move to `owner`. No admin keys beyond ownership.
*/

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function transfer(address, uint256) external returns (bool);
    function transferFrom(address, address, uint256) external returns (bool);
    function approve(address, uint256) external returns (bool);
    function decimals() external view returns (uint8);
}

interface ICurve {
    function exchange(int128 i, int128 j, uint256 dx, uint256 min_dy) external returns (uint256);
    function coins(uint256) external view returns (address);
}

interface ICooldownVault {
    function cooldownShares(uint256 shares) external returns (uint256 assets);
    function unstake(address receiver) external;
    function convertToAssets(uint256 shares) external view returns (uint256);
    function cooldownDuration() external view returns (uint24);
    function balanceOf(address) external view returns (uint256);
}

interface IERC4626 {
    function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets);
    function previewRedeem(uint256 shares) external view returns (uint256);
    function asset() external view returns (address);
}

interface IBalancerVault {
    function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external;
}

// Tolerates non-standard ERC-20s (USDT returns no bool on transfer/approve).
library SafeT {
    function _call(address token, bytes memory data) private {
        (bool ok, bytes memory ret) = token.call(data);
        require(ok && (ret.length == 0 || abi.decode(ret, (bool))), "token op failed");
    }
    function approve(address t, address s, uint256 a) internal { _call(t, abi.encodeWithSelector(IERC20.approve.selector, s, a)); }
    function transfer(address t, address to, uint256 a) internal { _call(t, abi.encodeWithSelector(IERC20.transfer.selector, to, a)); }
    function transferFrom(address t, address f, address to, uint256 a) internal { _call(t, abi.encodeWithSelector(IERC20.transferFrom.selector, f, to, a)); }
}

// One Curve exchange leg. tokenIn/tokenOut are carried so the contract approves and reads balances without a registry.
struct Hop {
    address pool;
    int128 i;
    int128 j;
    address tokenIn;
    address tokenOut;
}

abstract contract Owned {
    address public owner;
    constructor(address o) { owner = o; }
    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }
    function rescue(address token, uint256 amount) external onlyOwner {
        SafeT.transfer(token, owner, amount);
    }
}

library Route {
    // Execute a Curve path starting from `amountIn` of path[0].tokenIn already held by address(this).
    // Returns the amount of path[last].tokenOut held afterwards.
    function run(Hop[] calldata path, uint256 amountIn) internal returns (uint256 out) {
        uint256 dx = amountIn;
        for (uint256 k = 0; k < path.length; k++) {
            Hop calldata h = path[k];
            SafeT.approve(h.tokenIn, h.pool, dx);
            out = ICurve(h.pool).exchange(h.i, h.j, dx, 0);
            dx = out;
        }
    }
}

contract CooldownArb is Owned {
    using Route for Hop[];
    ICooldownVault public immutable vault; // e.g. sUSDe

    event Entered(uint256 amountIn, uint256 shares, uint256 navLocked);
    event Exited(uint256 assetsUnstaked, uint256 amountOut);

    constructor(address o, address vault_) Owned(o) { vault = ICooldownVault(vault_); }

    /// Pull `amountIn` of buyPath[0].tokenIn from owner, buy vault shares along buyPath, and enter the cooldown at NAV.
    /// Reverts unless the NAV value locked is at least `minNavOut` (denominated in the vault's underlying).
    function enter(Hop[] calldata buyPath, uint256 amountIn, uint256 minNavOut)
        external onlyOwner returns (uint256 shares, uint256 navLocked)
    {
        require(buyPath.length > 0, "empty path");
        SafeT.transferFrom(buyPath[0].tokenIn, owner, address(this), amountIn);
        buyPath.run(amountIn);
        shares = vault.balanceOf(address(this));
        navLocked = vault.convertToAssets(shares);
        require(navLocked >= minNavOut, "nav<min");
        vault.cooldownShares(shares); // burns shares, escrows `navLocked` underlying in the silo, starts the timer
        emit Entered(amountIn, shares, navLocked);
    }

    /// After the cooldown, pull the underlying out of the silo and sell it along sellPath to the payout token.
    function exit(Hop[] calldata sellPath, uint256 minOut) external onlyOwner returns (uint256 amountOut) {
        vault.unstake(address(this)); // releases the escrowed underlying to this contract
        uint256 have = IERC20(sellPath[0].tokenIn).balanceOf(address(this));
        amountOut = sellPath.run(have);
        address payout = sellPath[sellPath.length - 1].tokenOut;
        require(amountOut >= minOut, "out<min");
        SafeT.transfer(payout, owner, IERC20(payout).balanceOf(address(this)));
        emit Exited(have, amountOut);
    }
}

contract FlashNavArb is Owned {
    using Route for Hop[];
    IBalancerVault public constant BAL = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

    struct Job { address vault; address asset; uint256 flashAmount; uint256 minProfit; Hop[] buyPath; }
    Job private job;

    event Profit(address vault, uint256 flashAmount, uint256 profit);

    constructor(address o) Owned(o) {}

    /// Flash-borrow `flashAmount` of the vault asset, buy shares below NAV along buyPath, redeem them at NAV,
    /// repay the flash loan, and send the surplus to owner. Reverts unless surplus >= minProfit.
    function run(address vault_, address asset, uint256 flashAmount, uint256 minProfit, Hop[] calldata buyPath)
        external onlyOwner
    {
        require(buyPath[buyPath.length - 1].tokenOut == vault_, "path must end in vault share");
        require(buyPath[0].tokenIn == asset, "path must start in asset");
        Job storage j = job;
        j.vault = vault_; j.asset = asset; j.flashAmount = flashAmount; j.minProfit = minProfit;
        delete j.buyPath;
        for (uint256 k = 0; k < buyPath.length; k++) j.buyPath.push(buyPath[k]);
        address[] memory tokens = new address[](1); tokens[0] = asset;
        uint256[] memory amounts = new uint256[](1); amounts[0] = flashAmount;
        BAL.flashLoan(address(this), tokens, amounts, "");
    }

    function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory)
        external
    {
        require(msg.sender == address(BAL), "not balancer");
        Job storage j = job;
        // buy shares with the flashed asset
        uint256 dx = amounts[0];
        Hop[] storage path = j.buyPath;
        for (uint256 k = 0; k < path.length; k++) {
            Hop storage h = path[k];
            SafeT.approve(h.tokenIn, h.pool, dx);
            dx = ICurve(h.pool).exchange(h.i, h.j, dx, 0);
        }
        // redeem shares at NAV -> asset
        uint256 shares = IERC20(j.vault).balanceOf(address(this));
        IERC4626(j.vault).redeem(shares, address(this), address(this));
        // repay flash loan
        uint256 owed = amounts[0] + feeAmounts[0];
        SafeT.transfer(tokens[0], address(BAL), owed);
        uint256 profit = IERC20(j.asset).balanceOf(address(this));
        require(profit >= j.minProfit, "profit<min");
        SafeT.transfer(j.asset, owner, profit);
        emit Profit(j.vault, amounts[0], profit);
    }
}
