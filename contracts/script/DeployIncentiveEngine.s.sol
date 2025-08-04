// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/EmoHunterIncentiveEngine.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Mock ERC20 token for testing
contract MockRewardToken is ERC20 {
    constructor() ERC20("EmoHunter Reward Token", "EHRT") {
        _mint(msg.sender, 1000000 * 10**18); // 1M tokens
    }
    
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract DeployIncentiveEngine is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy mock reward token (for testing)
        MockRewardToken rewardToken = new MockRewardToken();
        console.log("MockRewardToken deployed at:", address(rewardToken));
        
        // Set up governors (replace with actual addresses)
        address[] memory governors = new address[](4);
        governors[0] = deployer; // Deployer as first governor
        governors[1] = vm.envAddress("GOVERNOR_1"); // Add more governors from env
        governors[2] = vm.envAddress("GOVERNOR_2");
        governors[3] = vm.envAddress("GOVERNOR_3");
        
        // Deploy incentive engine
        EmoHunterIncentiveEngine incentiveEngine = new EmoHunterIncentiveEngine(
            address(rewardToken),
            governors
        );
        
        console.log("EmoHunterIncentiveEngine deployed at:", address(incentiveEngine));
        
        // Authorize the backend service
        address backendService = vm.envAddress("BACKEND_SERVICE_ADDRESS");
        incentiveEngine.authorizeBackend(backendService);
        console.log("Backend service authorized:", backendService);
        
        // Transfer some tokens to the incentive engine for rewards
        uint256 initialTreasuryAmount = 100000 * 10**18; // 100k tokens
        rewardToken.transfer(address(incentiveEngine), initialTreasuryAmount);
        
        // Approve the incentive engine to spend tokens for treasury deposits
        rewardToken.approve(address(incentiveEngine), type(uint256).max);
        incentiveEngine.depositToTreasury(initialTreasuryAmount);
        
        console.log("Initial treasury funded with:", initialTreasuryAmount / 10**18, "tokens");
        
        vm.stopBroadcast();
        
        // Save deployment info to file
        string memory deploymentInfo = string(abi.encodePacked(
            "{\n",
            '  "rewardToken": "', vm.toString(address(rewardToken)), '",\n',
            '  "incentiveEngine": "', vm.toString(address(incentiveEngine)), '",\n',
            '  "deployer": "', vm.toString(deployer), '",\n',
            '  "backendService": "', vm.toString(backendService), '",\n',
            '  "initialTreasuryAmount": "', vm.toString(initialTreasuryAmount), '"\n',
            "}"
        ));
        
        vm.writeFile("./deployment-info.json", deploymentInfo);
        console.log("Deployment info saved to deployment-info.json");
    }
}
