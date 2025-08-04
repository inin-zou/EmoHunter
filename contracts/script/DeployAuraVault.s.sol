// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/AuraVaultMVP.sol";

contract DeployAuraVault is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        // 从环境变量读取owner地址
        address[] memory owners = new address[](4);
        owners[0] = vm.envAddress("OWNER_1");
        owners[1] = vm.envAddress("OWNER_2");
        owners[2] = vm.envAddress("OWNER_3");
        owners[3] = vm.envAddress("OWNER_4");
        
        vm.startBroadcast(deployerPrivateKey);
        AuraVaultMVP vault = new AuraVaultMVP(owners, 3);
        vm.stopBroadcast();
        
        console.log("Contract:", address(vault));
    }
}