// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AuraVaultMVP.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockERC20 is ERC20 {
    constructor() ERC20("Mock", "MCK") {}
    
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract AuraVaultMVPTest is Test {
    AuraVaultMVP public vault;
    MockERC20 public token;
    
    address[] public owners;
    address public owner1 = address(0x1);
    address public owner2 = address(0x2);
    address public owner3 = address(0x3);
    address public owner4 = address(0x4);
    address public nonOwner = address(0x5);
    address public recipient1 = address(0x6);
    address public recipient2 = address(0x7);

    function setUp() public {
        owners.push(owner1);
        owners.push(owner2);
        owners.push(owner3);
        owners.push(owner4);
        
        vault = new AuraVaultMVP(owners, 3);
        token = new MockERC20();
    }

    function test_Constructor() public {
        assertEq(vault.THRESHOLD(), 3);
        assertEq(vault.owners(0), owner1);
        assertEq(vault.owners(1), owner2);
        assertEq(vault.owners(2), owner3);
        assertEq(vault.owners(3), owner4);
        assertTrue(vault.isOwner(owner1));
        assertTrue(vault.isOwner(owner2));
        assertTrue(vault.isOwner(owner3));
        assertTrue(vault.isOwner(owner4));
        assertFalse(vault.isOwner(nonOwner));
    }

    function test_DepositERC20() public {
        token.mint(owner1, 1000 * 10**18);
        
        vm.startPrank(owner1);
        token.approve(address(vault), 100 * 10**18);
        
        vm.expectEmit(true, true, true, true);
        emit AuraVaultMVP.Deposit(owner1, address(token), 100 * 10**18);
        
        vault.deposit(address(token), 100 * 10**18);
        
        assertEq(token.balanceOf(address(vault)), 100 * 10**18);
        vm.stopPrank();
    }

    function test_DepositNative() public {
        vm.deal(owner1, 10 ether);
        
        vm.startPrank(owner1);
        
        vm.expectEmit(true, true, true, true);
        emit AuraVaultMVP.Deposit(owner1, address(0), 5 ether);
        
        vault.depositNative{value: 5 ether}();
        
        assertEq(address(vault).balance, 5 ether);
        vm.stopPrank();
    }

    function test_CompleteWorkflowERC20() public {
        // Setup
        token.mint(owner1, 1000 * 10**18);
        token.mint(owner2, 1000 * 10**18);
        token.mint(owner3, 1000 * 10**18);
        
        // Deposit from owner1
        vm.startPrank(owner1);
        token.approve(address(vault), 100 * 10**18);
        vault.deposit(address(token), 100 * 10**18);
        vm.stopPrank();
        
        // Owner2 also deposits
        vm.startPrank(owner2);
        token.approve(address(vault), 200 * 10**18);
        vault.deposit(address(token), 200 * 10**18);
        vm.stopPrank();
        
        // Create proposal
        address[] memory targets = new address[](2);
        targets[0] = recipient1;
        targets[1] = recipient2;
        
        uint256[] memory amounts = new uint256[](2);
        amounts[0] = 50 * 10**18;
        amounts[1] = 100 * 10**18;
        
        vm.startPrank(owner1);
        uint256 proposalId = vault.submit(address(token), targets, amounts, "Test distribution");
        vm.stopPrank();
        
        // Check proposal
        (
            address proposer,
            address tokenAddress,
            address[] memory proposalTargets,
            uint256[] memory proposalAmounts,
            uint256 voteCount,
            bool executed,
            string memory description
        ) = vault.getProposalMeta(proposalId);
        
        assertEq(proposer, owner1);
        assertEq(tokenAddress, address(token));
        assertEq(proposalTargets.length, 2);
        assertEq(proposalAmounts[0], 50 * 10**18);
        assertEq(proposalAmounts[1], 100 * 10**18);
        assertEq(voteCount, 0);
        assertFalse(executed);
        assertEq(description, "Test distribution");
        
        // Sign proposal
        vm.startPrank(owner2);
        vm.expectEmit(true, true, true, true);
        emit AuraVaultMVP.Signed(proposalId, owner2);
        vault.sign(proposalId);
        vm.stopPrank();
        
        vm.startPrank(owner3);
        vm.expectEmit(true, true, true, true);
        emit AuraVaultMVP.Signed(proposalId, owner3);
        vault.sign(proposalId);
        vm.stopPrank();
        
        vm.startPrank(owner4);
        vm.expectEmit(true, true, true, true);
        emit AuraVaultMVP.Signed(proposalId, owner4);
        vault.sign(proposalId);
        vm.stopPrank();
        
        // Execute proposal
        uint256 recipient1BalanceBefore = token.balanceOf(recipient1);
        uint256 recipient2BalanceBefore = token.balanceOf(recipient2);
        
        vm.expectEmit(true, true, true, true);
        emit AuraVaultMVP.Executed(proposalId);
        vault.execute(proposalId);
        
        // Verify execution
        assertEq(token.balanceOf(recipient1), recipient1BalanceBefore + 50 * 10**18);
        assertEq(token.balanceOf(recipient2), recipient2BalanceBefore + 100 * 10**18);
        
        // Check proposal is executed
        (,,,,,bool executedAfter,) = vault.getProposalMeta(proposalId);
        assertTrue(executedAfter);
    }

    function test_CompleteWorkflowNative() public {
        // Deposit native tokens
        vm.deal(owner1, 10 ether);
        vm.startPrank(owner1);
        vault.depositNative{value: 5 ether}();
        vm.stopPrank();
        
        vm.deal(owner2, 10 ether);
        vm.startPrank(owner2);
        vault.depositNative{value: 3 ether}();
        vm.stopPrank();
        
        // Create proposal
        address[] memory targets = new address[](2);
        targets[0] = recipient1;
        targets[1] = recipient2;
        
        uint256[] memory amounts = new uint256[](2);
        amounts[0] = 2 ether;
        amounts[1] = 3 ether;
        
        vm.startPrank(owner1);
        uint256 proposalId = vault.submit(address(0), targets, amounts, "Native distribution");
        vm.stopPrank();
        
        // Sign proposal
        vm.startPrank(owner2);
        vault.sign(proposalId);
        vm.stopPrank();
        
        vm.startPrank(owner3);
        vault.sign(proposalId);
        vm.stopPrank();
        
        vm.startPrank(owner4);
        vault.sign(proposalId);
        vm.stopPrank();
        
        // Execute proposal
        uint256 recipient1BalanceBefore = recipient1.balance;
        uint256 recipient2BalanceBefore = recipient2.balance;
        
        vault.execute(proposalId);
        
        // Verify execution
        assertEq(recipient1.balance, recipient1BalanceBefore + 2 ether);
        assertEq(recipient2.balance, recipient2BalanceBefore + 3 ether);
    }

    function test_RevertWhenNonOwner() public {
        address[] memory targets = new address[](1);
        targets[0] = recipient1;
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 100;
        
        vm.startPrank(nonOwner);
        
        vm.expectRevert();
        vault.deposit(address(token), 100);
        
        vm.expectRevert();
        vault.depositNative{value: 1 ether}();
        
        vm.expectRevert();
        vault.submit(address(token), targets, amounts, "Test");
        
        vm.expectRevert();
        vault.sign(0);
        
        vm.stopPrank();
    }

    function test_RevertInvalidConstruction() public {
        address[] memory invalidOwners = new address[](2);
        invalidOwners[0] = owner1;
        invalidOwners[1] = owner2;
        
        vm.expectRevert("AuraVault: threshold must be 3");
        new AuraVaultMVP(invalidOwners, 2);
        
        vm.expectRevert("AuraVault: owners < threshold");
        new AuraVaultMVP(invalidOwners, 3);
    }

    function test_RevertDoubleSign() public {
        token.mint(owner1, 1000 * 10**18);
        
        vm.startPrank(owner1);
        token.approve(address(vault), 100 * 10**18);
        vault.deposit(address(token), 100 * 10**18);
        
        address[] memory targets = new address[](1);
        targets[0] = recipient1;
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 50 * 10**18;
        
        uint256 proposalId = vault.submit(address(token), targets, amounts, "Test");
        
        vault.sign(proposalId);
        vm.expectRevert("AuraVault: already signed");
        vault.sign(proposalId);
        vm.stopPrank();
    }

    function test_RevertExecuteWithoutEnoughVotes() public {
        token.mint(owner1, 1000 * 10**18);
        
        vm.startPrank(owner1);
        token.approve(address(vault), 100 * 10**18);
        vault.deposit(address(token), 100 * 10**18);
        
        address[] memory targets = new address[](1);
        targets[0] = recipient1;
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 50 * 10**18;
        
        uint256 proposalId = vault.submit(address(token), targets, amounts, "Test");
        vm.stopPrank();
        
        vm.expectRevert("AuraVault: insufficient votes");
        vault.execute(proposalId);
    }

    function test_RevertExecuteTwice() public {
        token.mint(owner1, 1000 * 10**18);
        
        vm.startPrank(owner1);
        token.approve(address(vault), 100 * 10**18);
        vault.deposit(address(token), 100 * 10**18);
        
        address[] memory targets = new address[](1);
        targets[0] = recipient1;
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 50 * 10**18;
        
        uint256 proposalId = vault.submit(address(token), targets, amounts, "Test");
        vm.stopPrank();
        
        // Get enough signatures
        vm.startPrank(owner2);
        vault.sign(proposalId);
        vm.stopPrank();
        
        vm.startPrank(owner3);
        vault.sign(proposalId);
        vm.stopPrank();
        
        vm.startPrank(owner4);
        vault.sign(proposalId);
        vm.stopPrank();
        
        // Execute first time
        vault.execute(proposalId);
        
        // Try to execute again
        vm.expectRevert("AuraVault: already executed");
        vault.execute(proposalId);
    }
}