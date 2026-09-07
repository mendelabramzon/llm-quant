// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Test.sol";

interface IVault {
    function poolLength() external view returns (uint256);
    function poolInfo(uint256) external view returns (address token, uint256 allocPoint, uint256 accStacyPerShare, bool withdrawable);
    function totalAllocPoint() external view returns (uint256);
    function stacy() external view returns (address);
    function rewardsLock() external view returns (address);
    function PERCENT_LOCK_BONUS_REWARD() external view returns (uint256);
}
interface IPair {
    function getReserves() external view returns (uint112, uint112, uint32);
    function token0() external view returns (address);
    function token1() external view returns (address);
    function totalSupply() external view returns (uint256);
    function balanceOf(address) external view returns (uint256);
}
interface IStacy {
    function tokenUniswapPair() external view returns (address);
    function lastPopTime() external view returns (uint256);
    function getCherryPopAmount() external view returns (uint256);
    function feeDistributor() external view returns (address);
    function balanceOf(address) external view returns (uint256);
    function cherryPopBurnPct() external view returns (uint256);
    function cherryPopBurnCallerRewardPct() external view returns (uint256);
}
interface IERC20m { function symbol() external view returns (string memory); function balanceOf(address) external view returns (uint256); }

contract Discover is Test {
    address constant VAULT = 0x223Bc79156CBb0a6D175Ea6130Cb382D01868DF8;
    address constant BAL   = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
    address constant WETH  = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant USDC  = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant WBTC  = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;

    function _sym(address t) internal view returns (string memory) {
        try IERC20m(t).symbol() returns (string memory s) { return s; } catch { return "?"; }
    }

    function test_discover() public {
        IVault v = IVault(VAULT);
        uint256 n = v.poolLength();
        emit log_named_uint("poolLength", n);
        emit log_named_uint("totalAllocPoint", v.totalAllocPoint());
        emit log_named_address("stacy", v.stacy());
        emit log_named_address("rewardsLock", v.rewardsLock());
        emit log_named_uint("PERCENT_LOCK", v.PERCENT_LOCK_BONUS_REWARD());
        for (uint256 i = 0; i < n; i++) {
            (address tok, uint256 ap, , bool wd) = v.poolInfo(i);
            uint256 staked = IPair(tok).balanceOf(VAULT);
            emit log_named_uint("--- pid", i);
            emit log_named_address("  token", tok);
            emit log_named_string("  token.symbol", _sym(tok));
            emit log_named_uint("  allocPoint", ap);
            emit log_named_string("  withdrawable", wd ? "true" : "false");
            emit log_named_uint("  staked(LP bal of vault)", staked);
            try IPair(tok).getReserves() returns (uint112 r0, uint112 r1, uint32) {
                emit log_named_string("  t0", _sym(IPair(tok).token0()));
                emit log_named_string("  t1", _sym(IPair(tok).token1()));
                emit log_named_uint("  reserve0", r0);
                emit log_named_uint("  reserve1", r1);
                emit log_named_uint("  totalSupply", IPair(tok).totalSupply());
            } catch { emit log_string("  (not a UniV2 pair)"); }
        }
        IStacy s = IStacy(v.stacy());
        emit log_named_address("stacy.pair", s.tokenUniswapPair());
        emit log_named_address("stacy.feeDistributor", s.feeDistributor());
        emit log_named_uint("stacy.lastPopTime", s.lastPopTime());
        emit log_named_uint("block.timestamp", block.timestamp);
        emit log_named_uint("cherryPopAmount(now)", s.getCherryPopAmount());
        emit log_named_uint("STACY in stacy-pair", s.balanceOf(s.tokenUniswapPair()));
        emit log_named_uint("Balancer WETH", IERC20m(WETH).balanceOf(BAL));
        emit log_named_uint("Balancer USDC", IERC20m(USDC).balanceOf(BAL));
        emit log_named_uint("Balancer WBTC", IERC20m(WBTC).balanceOf(BAL));
    }
}
