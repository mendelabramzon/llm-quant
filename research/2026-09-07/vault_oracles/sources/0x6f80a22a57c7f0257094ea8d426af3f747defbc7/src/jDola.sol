// SPDX-License-Identifier: MIT License
pragma solidity ^0.8.24;

import {ERC4626, ERC20} from "lib/solmate/src/tokens/ERC4626.sol";
import {SafeTransferLib} from "lib/solmate/src/utils/SafeTransferLib.sol";

interface IERC20 {
    function transfer(address, uint) external returns (bool);
    function transferFrom(address, address, uint) external returns (bool);
    function balanceOf(address) external view returns (uint);
}

interface IMintable {
    function mint(address to, uint amount) external;
}

/**
 * @title jDola
 * @dev Auto-compounding ERC4626 supplier for JunionDola utilizing xy=k auctions.
 * WARNING: This vault may both atomically increase and decrease in value and even go to 0. Be very careful with using it as collateral.
 */
contract JDola is ERC4626 {
   
    uint public constant MIN_SHARES = 1e18;
    uint public constant MAX_ASSETS = 1e32; // 100 trillion sDOLA
    uint public constant MAX_SHARES = 2 ** 128 - 1;
    uint public constant MIN_ASSETS = 1e18; 
    IMintable public immutable DBR;
    address public gov;
    address public operator;
    address public pendingGov;
    address public immutable withdrawEscrow;
    uint public lastUpdate;
    uint public maxYearlyRewardBudget;
    uint public yearlyRewardBudget; // starts at 0
    uint public dbrReserve;
    uint public dolaReserve; //sdola reserver
    //10000 = 1 sDOLA per DBR max. The initial params sets the max DBR price to 0.5 sDOLA
    uint public maxDolaDbrRatioBps = 5000;
    
    mapping (uint => uint) public weeklyRevenue;
    mapping (address => bool) public slashingModules;

    /**
     * @dev Constructor for jDola contract.
     * WARNING: MIN_SHARES will always be unwithdrawable from the vault. Deployer should deposit enough to mint MIN_SHARES to avoid causing user grief.
     * @param _gov Address of governance.
     * @param _operator Address of the operator.
     */
    constructor(
        address _gov,
        address _operator,
        address _withdrawEscrow,
        address _dbr,
        ERC20 _asset,
        string memory _name,
        string memory _symbol
    ) ERC4626(_asset, _name, _symbol) {
        DBR = IMintable(_dbr);
        gov = _gov;
        operator = _operator;
        withdrawEscrow = _withdrawEscrow;
    }

    modifier onlyGov() {
        require(msg.sender == gov, "ONLY GOV");
        _;
    }

    modifier onlyOperator() {
        require(msg.sender == operator || msg.sender == gov, "ONLY OPERATOR");
        _;
    }

    modifier onlySlashingModule() {
        require(slashingModules[msg.sender], "ONLY SLASHING MODULE");
        _;
    }

    modifier updateReserves {
        require(dolaReserve > 0 && dbrReserve > 0, "Not initialized");
        (dolaReserve, dbrReserve) = getReserves();
        lastUpdate = block.timestamp;
        _;
    }

    /** @dev Calculate the amount of accrued rewards since the last auction.
     * @return The amount of rewards claimable by the supplier.
     */
    function accruedRewards() public view returns(uint) {
        uint deltaT = block.timestamp - lastUpdate;
        uint rewardsAccrued = deltaT * yearlyRewardBudget / 365 days;
        return rewardsAccrued;
    }

    /**
     * @dev Hook that is called after tokens are deposited into the contract.
     */    
    function afterDeposit(uint256, uint256) internal override {
        require(totalSupply >= MIN_SHARES, "Shares below MIN_SHARES");
        require(totalSupply <= MAX_SHARES, "Shares above MAX_SHARES");
        require(totalAssets() >= MIN_ASSETS, "Assets below MIN_ASSETS");
    }

    /**
     * @dev Hook that is called before tokens are withdrawn from the contract.
     * @param assets The amount of assets to withdraw.
     * @param shares The amount of shares to withdraw
     */
    function beforeWithdraw(uint256 assets, uint256 shares) internal override {
        require(msg.sender == withdrawEscrow, "Only withdraw escrow");
        require(totalAssets() >= assets + MIN_ASSETS || assets == totalAssets(), "Assets below MIN_ASSETS");
        require(totalSupply - shares >= MIN_SHARES || shares == totalSupply, "Shares below MIN_SHARES");
    }

    /**
     * @dev Initializes the virtual reserves, the ratio between the two reserves will be the initial price and their product equals K
     * @param _dbrReserve Initial dbr reserve
     * @param _dolaReserve Initial sdola reserve
     */
    function initialize(uint _dbrReserve, uint _dolaReserve) external onlyGov {
        require(dbrReserve == 0, "dbr reserves already set");
        require(dolaReserve == 0, "dbr reserves already set");
        require(_dbrReserve > 0, "initial reserves cant be 0");
        require(_dolaReserve > 0, "initial reserves cant be 0");
        require(_dbrReserve * _dolaReserve < type(uint192).max, "K factor too high");
        dbrReserve = _dbrReserve;
        dolaReserve = _dolaReserve;
        lastUpdate = block.timestamp;
        emit Initialized(dbrReserve, dolaReserve);
    }

    /**
     * @dev Calculates the total assets controlled by the contract.
     * Weekly revenue is distributed linearly over the following week.
     * @return The total assets in the contract.
     */
    function totalAssets() public view override returns (uint) {
        uint week = block.timestamp / 7 days;
        uint timeElapsed = block.timestamp % 7 days;
        uint remainingLastRevenue = weeklyRevenue[week - 1] * (7 days - timeElapsed) / 7 days;
        uint actualAssets = asset.balanceOf(address(this)) - remainingLastRevenue - weeklyRevenue[week];
        return actualAssets < MAX_ASSETS ? actualAssets : MAX_ASSETS;
    }
    
    /**
     * @dev Calculate max deposit based off value of maxShares
     * @return maximum Dola available to deposit
     */
    function maxDeposit(address) public view override returns(uint) {
        uint assets = totalAssets();
        if(assets >= MAX_ASSETS) return 0;
        if(totalSupply >= MAX_SHARES) return 0;
        uint maxShares = MAX_SHARES - totalSupply;
        uint shareCeil;
        if(totalSupply == 0) shareCeil = MAX_SHARES;
        else shareCeil = assets * maxShares / totalSupply;
        uint assetCeil = MAX_ASSETS - assets;
        return shareCeil < assetCeil ? shareCeil : assetCeil;
    }

    /**
     * @dev Calculate max mint based off asset / share value
     * @return maximum jrDola shares that can be minted
     */
    function maxMint(address) public view override returns(uint) {
        uint assets = totalAssets();
        if(assets >= MAX_ASSETS) return 0;
        if(totalSupply >= MAX_SHARES) return 0;
        uint maxShares = MAX_SHARES - totalSupply;
        uint maxAssets = MAX_ASSETS - assets;
        uint assetCeil;
        if(totalSupply == 0) assetCeil = maxAssets;
        else assetCeil = maxAssets * totalSupply / assets;
        return assetCeil < maxShares ? assetCeil : maxShares;
    }

    /**
     * @dev Allows users to buy DBR with sDOLA.
     * WARNING: Never expose this directly to a UI as it is likely to cause a loss unless a transaction is executed immediately.
     * Instead use the jDolaHelper function or custom smart contract code.
     * @param exactDolaIn The exact amount of sDOLA to spend.
     * @param exactDbrOut The exact amount of DBR to receive.
     * @param to The address that will receive the DBR.
     */
    function buyDbr(uint exactDolaIn, uint exactDbrOut, address to) external updateReserves {
        require(to != address(0), "Zero address");
        uint K = dolaReserve * dbrReserve;
        dolaReserve += exactDolaIn;
        dbrReserve -= exactDbrOut;
        require(dolaReserve * dbrReserve >= K, "Invariant");
        //Prevent an edgecase where someone owning all possible shares of jrDola can mint as much DBR against Dola as they'd like
        require(dolaReserve * 10_000 / dbrReserve <= maxDolaDbrRatioBps, "Above max ratio");
        donate(exactDolaIn);
        DBR.mint(to, exactDbrOut);
        emit Buy(msg.sender, to, exactDolaIn, exactDbrOut);
    }

    /**
     * @dev Donatess sDOLA to weekly revenue emissions from msg.sender
     * @param amount Amount of sDOLA msg.sender will donate to the weekly revenue
     */
    function donate(uint amount) public {
        SafeTransferLib.safeTransferFrom(asset, msg.sender, address(this), amount);
        weeklyRevenue[block.timestamp / 7 days] += amount;
        emit Donate(msg.sender, amount);
    }

    /**
     * @dev Slashing module called by slashing modules to repay bad debt
     * @param amount Amount of DOLA needed to repay bad debt
     * @return `amount` of available DOLA
     */
    function slash(uint amount) external onlySlashingModule() returns(uint) {
        //Make sure slashed amount doesn't exceed a safe amount of assets to withdraw
        uint availableShares = totalAssets() - MIN_ASSETS;
        uint availableAssets = ERC4626(address(asset)).previewRedeem(availableShares);
        if(availableAssets <= amount)
            amount = availableAssets;
        require(amount > 0, "Zero slash");
        ERC4626(address(asset)).withdraw(amount, msg.sender, address(this));
        emit Slashing(msg.sender, amount);
        return amount;
    }
    
    /**
     * @dev Get updated sdola reserves and dbr reserves.
     * @return _dolaReserve The current sdola reserves
     * @return _dbrReserve The current dbr reserves
     */
    function getReserves() public view returns (uint _dolaReserve, uint _dbrReserve) {
        uint timeElapsed = block.timestamp - lastUpdate;
        if(timeElapsed > 0) {
            uint K = dolaReserve * dbrReserve;
            uint DbrsIn = timeElapsed * yearlyRewardBudget / 365 days;
            _dbrReserve = dbrReserve + DbrsIn;
            _dolaReserve = K / _dbrReserve;
            if(_dolaReserve == 0) _dolaReserve = 1;
        } else {
            _dolaReserve = dolaReserve;
            _dbrReserve = dbrReserve;
        }
    }
    
    /**
     * @dev Sets the dbr reserve while preserving the reserve ratio. Used for changing the depth of the pool.
     * @param _dbrReserve The new dbr reserve
     */
    function setDbrReserve(uint _dbrReserve) external onlyGov updateReserves {
        require(_dbrReserve > 0, "dbr reserve cant be 0");
        require(_dbrReserve <= type(uint112).max, "dbr reserves can't exceed 2**112");
        dolaReserve = dolaReserve * _dbrReserve / dbrReserve;
        require(dolaReserve <= type(uint112).max, "dola reserves can't exceed 2**112");
        require(dolaReserve > 0, "dola reserve cant be 0");
        dbrReserve = _dbrReserve;
        emit SetReserves(dbrReserve, dolaReserve);
    }

    /**
     * @dev Sets the sdola reserve while preserving the reserve ratio. Used for changing the depth of the pool.
     * @param _dolaReserve The new sdola reserve
     */
    function setDolaReserve(uint _dolaReserve) external onlyGov updateReserves {
        require(_dolaReserve > 0, "dola reserve cant be 0");
        require(_dolaReserve <= type(uint112).max, "dola reserves can't exceed 2**112");
        dbrReserve = dbrReserve * _dolaReserve / dolaReserve;
        require(dbrReserve <= type(uint112).max, "dbr reserves can't exceed 2**112");
        require(dbrReserve > 0, "dbr reserve cant be 0");
        dolaReserve = _dolaReserve;
        emit SetReserves(dbrReserve, dolaReserve);
    }

    /**
     * @dev Sets the maximum yearly reward budget.
     * @param _max The maximum yearly reward budget.
     */
    function setMaxYearlyRewardBudget(uint _max) external onlyGov updateReserves {
        maxYearlyRewardBudget = _max;
        if(yearlyRewardBudget > _max) {
            yearlyRewardBudget = _max;
            emit SetYearlyRewardBudget(_max);
        }
        emit SetMaxYearlyRewardBudget(_max);
    }

    /**
     * @dev Sets the max sDola/Dbr ratio
     * @param _maxDolaDbrRatioBps The max sDola/Dbr ratio in bps
     */
    function setMaxDolaDbrRatioBps(uint _maxDolaDbrRatioBps) external onlyOperator {
        maxDolaDbrRatioBps = _maxDolaDbrRatioBps;
        emit SetMaxDolaDbrRatioBps(_maxDolaDbrRatioBps);
    }

    /**
     * @dev Sets the yearly reward budget.
     * @param _yearlyRewardBudget The yearly reward budget.
     */
    function setYearlyRewardBudget(uint _yearlyRewardBudget) external onlyOperator updateReserves {
        require(_yearlyRewardBudget <= maxYearlyRewardBudget, "REWARD BUDGET ABOVE MAX");
        yearlyRewardBudget = _yearlyRewardBudget;
        emit SetYearlyRewardBudget(_yearlyRewardBudget);
    }
   
    /**
     * @dev Adds or removes a slashing module. Be careful as fraudulent slashing modules can steal all sDOLA
     * @param slashingModule slashingModule to be added or removed
     * @param isSlashingModule Set true for adding and false for removing
     */
    function setSlashingModule(address slashingModule, bool isSlashingModule) external onlyGov {
        slashingModules[slashingModule] = isSlashingModule;
        emit SetSlashingModule(slashingModule, isSlashingModule);
    }

    /**
     * @dev Sets a new operator
     */
    function setOperator(address _operator) external onlyGov {
        operator = _operator;
        emit NewOperator(_operator);
    }

    /**
     * @dev Sets a new pending governance address.
     * @param _gov The address of the new pending governance.
     */
    function setPendingGov(address _gov) external onlyGov {
        pendingGov = _gov;
        emit NewPendingGov(_gov);
    }

    /**
     * @dev Allows the pending governance to accept its role.
     */
    function acceptGov() external {
        require(msg.sender == pendingGov, "ONLY PENDINGGOV");
        gov = pendingGov;
        pendingGov = address(0);
        emit NewGov(gov);
    }

    /**
     * @dev Allows governance to sweep any ERC20 token from the contract.
     * @dev Excludes the ability to sweep DBR and sDOLA tokens.
     * @param token The address of the ERC20 token to sweep.
     * @param amount The amount of tokens to sweep.
     * @param to The recipient address of the swept tokens.
     */
    function sweep(address token, uint amount, address to) public onlyGov {
        require(address(DBR) != token, "Not authorized");
        require(address(asset) != token, "Not authorized");
        SafeTransferLib.safeTransfer(ERC20(token), to, amount);
        emit Sweep(token, to, amount);
    }

    event Buy(address indexed caller, address indexed to, uint exactDolaIn, uint exactDbrOut);
    event SetTargetK(uint newTargetK);
    event SetYearlyRewardBudget(uint);
    event SetMaxYearlyRewardBudget(uint);
    event Slashing(address indexed slashingModule, uint slashed);
    event SetSlashingModule(address indexed module, bool enabled);
    event Initialized(uint dbrReserve, uint dolaReserve);
    event SetReserves(uint newDbrReserve, uint newDolaReserve);
    event SetMaxDolaDbrRatioBps(uint newBps);
    event Sweep(address token, address to, uint amount);
    event Donate(address indexed donor, uint amount);
    event NewOperator(address);
    event NewPendingGov(address);
    event NewGov(address);
}
