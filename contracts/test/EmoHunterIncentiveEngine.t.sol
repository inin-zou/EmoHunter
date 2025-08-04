// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/EmoHunterIncentiveEngine.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockERC20 is ERC20 {
    constructor() ERC20("Test Token", "TEST") {
        _mint(msg.sender, 1000000 * 10**18);
    }
    
    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract EmoHunterIncentiveEngineTest is Test {
    EmoHunterIncentiveEngine public incentiveEngine;
    MockERC20 public rewardToken;
    
    address public owner;
    address public user1;
    address public user2;
    address public backend;
    address[] public governors;
    
    function setUp() public {
        owner = address(this);
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");
        backend = makeAddr("backend");
        
        // Setup governors
        governors.push(makeAddr("governor1"));
        governors.push(makeAddr("governor2"));
        governors.push(makeAddr("governor3"));
        governors.push(makeAddr("governor4"));
        
        // Deploy mock token
        rewardToken = new MockERC20();
        
        // Deploy incentive engine
        incentiveEngine = new EmoHunterIncentiveEngine(
            address(rewardToken),
            governors
        );
        
        // Authorize backend
        incentiveEngine.authorizeBackend(backend);
        
        // Fund the contract
        rewardToken.transfer(address(incentiveEngine), 100000 * 10**18);
        rewardToken.approve(address(incentiveEngine), type(uint256).max);
        incentiveEngine.depositToTreasury(100000 * 10**18);
    }
    
    function testStartSession() public {
        vm.prank(backend);
        uint256 sessionId = incentiveEngine.startSession(user1);
        
        assertEq(sessionId, 0);
        assertEq(incentiveEngine.userSessionCount(user1), 1);
        
        (uint256 startTime, uint256 endTime, uint256 engagementScore, , bool claimed) = 
            incentiveEngine.getUserSession(user1, sessionId);
        
        assertGt(startTime, 0);
        assertEq(endTime, 0);
        assertEq(engagementScore, 0);
        assertFalse(claimed);
    }
    
    function testRecordEmotion() public {
        vm.prank(backend);
        uint256 sessionId = incentiveEngine.startSession(user1);
        
        vm.prank(backend);
        incentiveEngine.recordEmotion(
            user1,
            sessionId,
            EmoHunterIncentiveEngine.EmotionType.HAPPY,
            5000 // 5 seconds
        );
        
        (uint256 count, uint256 duration) = incentiveEngine.getEmotionData(
            user1,
            sessionId,
            EmoHunterIncentiveEngine.EmotionType.HAPPY
        );
        
        assertEq(count, 1);
        assertEq(duration, 5000);
    }
    
    function testCompleteSessionWorkflow() public {
        // Start session
        vm.prank(backend);
        uint256 sessionId = incentiveEngine.startSession(user1);
        
        // Record multiple emotions
        vm.prank(backend);
        incentiveEngine.recordEmotion(
            user1,
            sessionId,
            EmoHunterIncentiveEngine.EmotionType.HAPPY,
            10000
        );
        
        vm.prank(backend);
        incentiveEngine.recordEmotion(
            user1,
            sessionId,
            EmoHunterIncentiveEngine.EmotionType.SURPRISED,
            5000
        );
        
        // Wait some time to simulate session duration
        vm.warp(block.timestamp + 600); // 10 minutes
        
        // End session
        vm.prank(backend);
        incentiveEngine.endSession(user1, sessionId);
        
        // Check session data
        (uint256 startTime, uint256 endTime, uint256 engagementScore, , bool claimed) = 
            incentiveEngine.getUserSession(user1, sessionId);
        
        assertGt(endTime, startTime);
        assertGt(engagementScore, 0);
        assertFalse(claimed);
        
        // Check pending reward
        uint256 pendingReward = incentiveEngine.calculatePendingReward(user1, sessionId);
        assertGt(pendingReward, 0);
    }
    
    function testClaimReward() public {
        // Complete a session
        vm.prank(backend);
        uint256 sessionId = incentiveEngine.startSession(user1);
        
        vm.prank(backend);
        incentiveEngine.recordEmotion(
            user1,
            sessionId,
            EmoHunterIncentiveEngine.EmotionType.HAPPY,
            15000
        );
        
        vm.warp(block.timestamp + 600);
        
        vm.prank(backend);
        incentiveEngine.endSession(user1, sessionId);
        
        // Get pending reward
        uint256 pendingReward = incentiveEngine.calculatePendingReward(user1, sessionId);
        uint256 initialBalance = rewardToken.balanceOf(user1);
        
        // Claim reward
        vm.prank(user1);
        incentiveEngine.claimReward(sessionId);
        
        // Check balances
        uint256 finalBalance = rewardToken.balanceOf(user1);
        assertEq(finalBalance - initialBalance, pendingReward);
        
        // Check that reward is marked as claimed
        (, , , , bool claimed) = incentiveEngine.getUserSession(user1, sessionId);
        assertTrue(claimed);
        
        // Check total user rewards
        assertEq(incentiveEngine.totalUserRewards(user1), pendingReward);
    }
    
    function testUnauthorizedBackendReverts() public {
        address unauthorizedBackend = makeAddr("unauthorized");
        
        vm.prank(unauthorizedBackend);
        vm.expectRevert("Not authorized backend");
        incentiveEngine.startSession(user1);
    }
    
    function testCannotClaimTwice() public {
        // Complete a session and claim once
        vm.prank(backend);
        uint256 sessionId = incentiveEngine.startSession(user1);
        
        vm.prank(backend);
        incentiveEngine.recordEmotion(
            user1,
            sessionId,
            EmoHunterIncentiveEngine.EmotionType.HAPPY,
            10000
        );
        
        vm.warp(block.timestamp + 300);
        
        vm.prank(backend);
        incentiveEngine.endSession(user1, sessionId);
        
        vm.prank(user1);
        incentiveEngine.claimReward(sessionId);
        
        // Try to claim again
        vm.prank(user1);
        vm.expectRevert("Reward already claimed");
        incentiveEngine.claimReward(sessionId);
    }
    
    function testGovernanceProposal() public {
        address governor1 = governors[0];
        address governor2 = governors[1];
        address governor3 = governors[2];
        
        // Create proposal
        vm.prank(governor1);
        uint256 proposalId = incentiveEngine.createGovernanceProposal(
            "Increase bronze base reward",
            20 * 10**18
        );
        
        assertEq(proposalId, 0);
        
        // Vote on proposal
        vm.prank(governor1);
        incentiveEngine.voteOnProposal(proposalId);
        
        vm.prank(governor2);
        incentiveEngine.voteOnProposal(proposalId);
        
        vm.prank(governor3);
        incentiveEngine.voteOnProposal(proposalId);
        
        // Check that proposal was executed (simplified check)
        (address proposer, string memory description, uint256 newBaseReward, uint256 voteCount, bool executed) = 
            incentiveEngine.proposals(proposalId);
        
        assertTrue(executed);
        assertEq(voteCount, 3);
    }
    
    function testMultipleEmotionTypes() public {
        vm.prank(backend);
        uint256 sessionId = incentiveEngine.startSession(user1);
        
        // Record all emotion types
        EmoHunterIncentiveEngine.EmotionType[7] memory emotions = [
            EmoHunterIncentiveEngine.EmotionType.HAPPY,
            EmoHunterIncentiveEngine.EmotionType.SAD,
            EmoHunterIncentiveEngine.EmotionType.ANGRY,
            EmoHunterIncentiveEngine.EmotionType.SURPRISED,
            EmoHunterIncentiveEngine.EmotionType.FEARFUL,
            EmoHunterIncentiveEngine.EmotionType.DISGUSTED,
            EmoHunterIncentiveEngine.EmotionType.NEUTRAL
        ];
        
        for (uint256 i = 0; i < emotions.length; i++) {
            vm.prank(backend);
            incentiveEngine.recordEmotion(user1, sessionId, emotions[i], 2000);
        }
        
        // Verify all emotions were recorded
        for (uint256 i = 0; i < emotions.length; i++) {
            (uint256 count, uint256 duration) = incentiveEngine.getEmotionData(user1, sessionId, emotions[i]);
            assertEq(count, 1);
            assertEq(duration, 2000);
        }
        
        vm.warp(block.timestamp + 1800); // 30 minutes for platinum tier
        
        vm.prank(backend);
        incentiveEngine.endSession(user1, sessionId);
        
        // Should get high reward due to emotion diversity and duration
        uint256 pendingReward = incentiveEngine.calculatePendingReward(user1, sessionId);
        assertGt(pendingReward, 50 * 10**18); // Should be significant reward
    }
}
