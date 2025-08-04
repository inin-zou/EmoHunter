// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title EmoHunterIncentiveEngine
 * @dev Advanced incentive distribution system for EmoHunter platform
 * Features:
 * - Emotion-based reward calculation
 * - Multi-tier reward system
 * - Automated distribution based on engagement metrics
 * - Session-based tracking
 * - Multi-signature governance for fund management
 */
contract EmoHunterIncentiveEngine is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    // Emotion types supported by the system
    enum EmotionType {
        HAPPY,
        SAD,
        ANGRY,
        SURPRISED,
        FEARFUL,
        DISGUSTED,
        NEUTRAL
    }

    // Reward tier levels
    enum RewardTier {
        BRONZE,   // Basic engagement
        SILVER,   // Moderate engagement
        GOLD,     // High engagement
        PLATINUM  // Exceptional engagement
    }

    struct UserSession {
        address user;
        uint256 sessionId;
        uint256 startTime;
        uint256 endTime;
        uint256 totalEngagementScore;
        mapping(EmotionType => uint256) emotionCounts;
        mapping(EmotionType => uint256) emotionDurations;
        bool rewardClaimed;
        RewardTier tier;
    }

    struct RewardConfig {
        uint256 baseReward;           // Base reward amount
        uint256 emotionMultiplier;    // Multiplier for emotion diversity
        uint256 durationMultiplier;   // Multiplier for session duration
        uint256 tierMultiplier;       // Multiplier for reward tier
        bool active;
    }

    struct GovernanceProposal {
        address proposer;
        string description;
        uint256 newBaseReward;
        uint256 voteCount;
        bool executed;
        mapping(address => bool) voted;
    }

    // State variables
    mapping(address => mapping(uint256 => UserSession)) public userSessions;
    mapping(address => uint256) public userSessionCount;
    mapping(address => uint256) public totalUserRewards;
    mapping(RewardTier => RewardConfig) public rewardConfigs;
    
    // Governance
    address[] public governors;
    mapping(address => bool) public isGovernor;
    uint256 public constant GOVERNANCE_THRESHOLD = 3;
    uint256 public proposalCounter;
    mapping(uint256 => GovernanceProposal) public proposals;

    // Treasury
    IERC20 public rewardToken;
    uint256 public totalRewardsDistributed;
    uint256 public treasuryBalance;

    // Backend integration
    mapping(address => bool) public authorizedBackends;
    
    // Events
    event SessionStarted(address indexed user, uint256 indexed sessionId, uint256 timestamp);
    event SessionEnded(address indexed user, uint256 indexed sessionId, uint256 engagementScore);
    event EmotionRecorded(address indexed user, uint256 indexed sessionId, EmotionType emotion, uint256 duration);
    event RewardCalculated(address indexed user, uint256 indexed sessionId, uint256 amount, RewardTier tier);
    event RewardClaimed(address indexed user, uint256 indexed sessionId, uint256 amount);
    event GovernanceProposalCreated(uint256 indexed proposalId, address indexed proposer);
    event GovernanceVote(uint256 indexed proposalId, address indexed voter);
    event RewardConfigUpdated(RewardTier tier, uint256 baseReward);

    modifier onlyGovernor() {
        require(isGovernor[msg.sender], "Not a governor");
        _;
    }

    modifier onlyAuthorizedBackend() {
        require(authorizedBackends[msg.sender], "Not authorized backend");
        _;
    }

    constructor(
        address _rewardToken,
        address[] memory _governors
    ) Ownable(msg.sender) {
        require(_governors.length >= GOVERNANCE_THRESHOLD, "Insufficient governors");
        
        rewardToken = IERC20(_rewardToken);
        
        // Initialize governors
        for (uint256 i = 0; i < _governors.length; i++) {
            require(_governors[i] != address(0), "Invalid governor address");
            isGovernor[_governors[i]] = true;
            governors.push(_governors[i]);
        }

        // Initialize default reward configurations
        _initializeRewardConfigs();
    }

    function _initializeRewardConfigs() private {
        rewardConfigs[RewardTier.BRONZE] = RewardConfig({
            baseReward: 10e18,      // 10 tokens
            emotionMultiplier: 110,  // 1.1x
            durationMultiplier: 105, // 1.05x
            tierMultiplier: 100,     // 1.0x
            active: true
        });

        rewardConfigs[RewardTier.SILVER] = RewardConfig({
            baseReward: 25e18,      // 25 tokens
            emotionMultiplier: 125,  // 1.25x
            durationMultiplier: 115, // 1.15x
            tierMultiplier: 150,     // 1.5x
            active: true
        });

        rewardConfigs[RewardTier.GOLD] = RewardConfig({
            baseReward: 50e18,      // 50 tokens
            emotionMultiplier: 150,  // 1.5x
            durationMultiplier: 130, // 1.3x
            tierMultiplier: 200,     // 2.0x
            active: true
        });

        rewardConfigs[RewardTier.PLATINUM] = RewardConfig({
            baseReward: 100e18,     // 100 tokens
            emotionMultiplier: 200,  // 2.0x
            durationMultiplier: 150, // 1.5x
            tierMultiplier: 300,     // 3.0x
            active: true
        });
    }

    /**
     * @dev Start a new user session (called by authorized backend)
     */
    function startSession(address user) external onlyAuthorizedBackend returns (uint256 sessionId) {
        sessionId = userSessionCount[user]++;
        UserSession storage session = userSessions[user][sessionId];
        
        session.user = user;
        session.sessionId = sessionId;
        session.startTime = block.timestamp;
        session.totalEngagementScore = 0;
        session.rewardClaimed = false;

        emit SessionStarted(user, sessionId, block.timestamp);
    }

    /**
     * @dev Record emotion data during a session
     */
    function recordEmotion(
        address user,
        uint256 sessionId,
        EmotionType emotion,
        uint256 duration
    ) external onlyAuthorizedBackend {
        UserSession storage session = userSessions[user][sessionId];
        require(session.startTime > 0, "Session not found");
        require(session.endTime == 0, "Session already ended");

        session.emotionCounts[emotion]++;
        session.emotionDurations[emotion] += duration;
        
        // Update engagement score based on emotion and duration
        session.totalEngagementScore += _calculateEmotionScore(emotion, duration);

        emit EmotionRecorded(user, sessionId, emotion, duration);
    }

    /**
     * @dev End a user session and calculate rewards
     */
    function endSession(address user, uint256 sessionId) external onlyAuthorizedBackend {
        UserSession storage session = userSessions[user][sessionId];
        require(session.startTime > 0, "Session not found");
        require(session.endTime == 0, "Session already ended");

        session.endTime = block.timestamp;
        
        // Calculate reward tier and amount
        (RewardTier tier, uint256 rewardAmount) = _calculateReward(user, sessionId);
        session.tier = tier;

        emit SessionEnded(user, sessionId, session.totalEngagementScore);
        emit RewardCalculated(user, sessionId, rewardAmount, tier);
    }

    /**
     * @dev Claim rewards for a completed session
     */
    function claimReward(uint256 sessionId) external nonReentrant {
        UserSession storage session = userSessions[msg.sender][sessionId];
        require(session.endTime > 0, "Session not completed");
        require(!session.rewardClaimed, "Reward already claimed");

        (, uint256 rewardAmount) = _calculateReward(msg.sender, sessionId);
        require(rewardAmount > 0, "No reward available");
        require(rewardToken.balanceOf(address(this)) >= rewardAmount, "Insufficient treasury balance");

        session.rewardClaimed = true;
        totalUserRewards[msg.sender] += rewardAmount;
        totalRewardsDistributed += rewardAmount;

        rewardToken.safeTransfer(msg.sender, rewardAmount);

        emit RewardClaimed(msg.sender, sessionId, rewardAmount);
    }

    /**
     * @dev Calculate emotion-based engagement score
     */
    function _calculateEmotionScore(EmotionType emotion, uint256 duration) private pure returns (uint256) {
        uint256 baseScore = duration / 1000; // Base score per second
        
        // Different emotions have different engagement values
        if (emotion == EmotionType.HAPPY) return baseScore * 120 / 100;      // 1.2x
        if (emotion == EmotionType.SURPRISED) return baseScore * 150 / 100;  // 1.5x
        if (emotion == EmotionType.SAD) return baseScore * 110 / 100;        // 1.1x
        if (emotion == EmotionType.ANGRY) return baseScore * 130 / 100;      // 1.3x
        if (emotion == EmotionType.FEARFUL) return baseScore * 140 / 100;    // 1.4x
        if (emotion == EmotionType.DISGUSTED) return baseScore * 105 / 100;  // 1.05x
        
        return baseScore; // NEUTRAL
    }

    /**
     * @dev Calculate reward tier and amount based on session data
     */
    function _calculateReward(address user, uint256 sessionId) private view returns (RewardTier tier, uint256 amount) {
        UserSession storage session = userSessions[user][sessionId];
        
        uint256 sessionDuration = session.endTime - session.startTime;
        uint256 emotionDiversity = _calculateEmotionDiversity(user, sessionId);
        
        // Determine tier based on engagement score and session metrics
        if (session.totalEngagementScore >= 1000 && sessionDuration >= 1800) { // 30 minutes
            tier = RewardTier.PLATINUM;
        } else if (session.totalEngagementScore >= 500 && sessionDuration >= 900) { // 15 minutes
            tier = RewardTier.GOLD;
        } else if (session.totalEngagementScore >= 200 && sessionDuration >= 300) { // 5 minutes
            tier = RewardTier.SILVER;
        } else {
            tier = RewardTier.BRONZE;
        }

        // Calculate reward amount
        RewardConfig memory config = rewardConfigs[tier];
        if (!config.active) {
            return (tier, 0);
        }

        amount = config.baseReward;
        amount = amount * config.emotionMultiplier * emotionDiversity / 10000;
        amount = amount * config.durationMultiplier * sessionDuration / (300 * 100); // Normalize to 5 min baseline
        amount = amount * config.tierMultiplier / 100;
    }

    /**
     * @dev Calculate emotion diversity score (more diverse emotions = higher score)
     */
    function _calculateEmotionDiversity(address user, uint256 sessionId) private view returns (uint256) {
        UserSession storage session = userSessions[user][sessionId];
        uint256 diversityScore = 100; // Base score
        uint256 activeEmotions = 0;

        for (uint256 i = 0; i < 7; i++) {
            if (session.emotionCounts[EmotionType(i)] > 0) {
                activeEmotions++;
            }
        }

        // Bonus for emotion diversity (max 200% for all 7 emotions)
        diversityScore += (activeEmotions * 100) / 7;
        
        return diversityScore;
    }

    /**
     * @dev Authorize a backend service to interact with the contract
     */
    function authorizeBackend(address backend) external onlyOwner {
        authorizedBackends[backend] = true;
    }

    /**
     * @dev Revoke backend authorization
     */
    function revokeBackend(address backend) external onlyOwner {
        authorizedBackends[backend] = false;
    }

    /**
     * @dev Deposit tokens to treasury (only owner)
     */
    function depositToTreasury(uint256 amount) external onlyOwner {
        rewardToken.safeTransferFrom(msg.sender, address(this), amount);
        treasuryBalance += amount;
    }

    /**
     * @dev Create governance proposal to update reward configuration
     */
    function createGovernanceProposal(
        string calldata description,
        uint256 newBaseReward
    ) external onlyGovernor returns (uint256 proposalId) {
        proposalId = proposalCounter++;
        GovernanceProposal storage proposal = proposals[proposalId];
        
        proposal.proposer = msg.sender;
        proposal.description = description;
        proposal.newBaseReward = newBaseReward;
        proposal.voteCount = 0;
        proposal.executed = false;

        emit GovernanceProposalCreated(proposalId, msg.sender);
    }

    /**
     * @dev Vote on governance proposal
     */
    function voteOnProposal(uint256 proposalId) external onlyGovernor {
        GovernanceProposal storage proposal = proposals[proposalId];
        require(!proposal.executed, "Proposal already executed");
        require(!proposal.voted[msg.sender], "Already voted");

        proposal.voted[msg.sender] = true;
        proposal.voteCount++;

        emit GovernanceVote(proposalId, msg.sender);

        // Auto-execute if threshold reached
        if (proposal.voteCount >= GOVERNANCE_THRESHOLD) {
            _executeProposal(proposalId);
        }
    }

    /**
     * @dev Execute approved governance proposal
     */
    function _executeProposal(uint256 proposalId) private {
        GovernanceProposal storage proposal = proposals[proposalId];
        proposal.executed = true;

        // Update reward configuration (simplified - could be expanded)
        rewardConfigs[RewardTier.BRONZE].baseReward = proposal.newBaseReward;
        
        emit RewardConfigUpdated(RewardTier.BRONZE, proposal.newBaseReward);
    }

    // View functions
    function getUserSession(address user, uint256 sessionId) external view returns (
        uint256 startTime,
        uint256 endTime,
        uint256 totalEngagementScore,
        RewardTier tier,
        bool rewardClaimed
    ) {
        UserSession storage session = userSessions[user][sessionId];
        return (
            session.startTime,
            session.endTime,
            session.totalEngagementScore,
            session.tier,
            session.rewardClaimed
        );
    }

    function getEmotionData(address user, uint256 sessionId, EmotionType emotion) external view returns (
        uint256 count,
        uint256 duration
    ) {
        UserSession storage session = userSessions[user][sessionId];
        return (
            session.emotionCounts[emotion],
            session.emotionDurations[emotion]
        );
    }

    function calculatePendingReward(address user, uint256 sessionId) external view returns (uint256) {
        (, uint256 amount) = _calculateReward(user, sessionId);
        return amount;
    }
}
