// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract AuraVaultMVP is ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct Proposal {
        address proposer;
        address token;
        address[] targets;
        uint256[] amounts;
        uint256 voteCount;
        bool executed;
        string description;
        mapping(address => bool) signed;
    }

    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public immutable THRESHOLD;
    uint256 public proposalCounter;
    mapping(uint256 => Proposal) private _proposals;

    event Deposit(address indexed from, address indexed token, uint256 amount);
    event ProposalCreated(uint256 indexed id, address indexed proposer);
    event Signed(uint256 indexed id, address indexed owner);
    event Executed(uint256 indexed id);

    modifier onlyOwner() {
        require(isOwner[msg.sender], "AuraVault: not owner");
        _;
    }

    constructor(address[] memory _owners, uint256 _threshold) {
        require(_threshold == 3, "AuraVault: threshold must be 3");
        require(_owners.length >= _threshold, "AuraVault: owners < threshold");
        
        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0), "AuraVault: zero address");
            require(!isOwner[owner], "AuraVault: duplicate owner");
            isOwner[owner] = true;
            owners.push(owner);
        }
        
        THRESHOLD = _threshold;
    }

    function deposit(address token, uint256 amount) external onlyOwner {
        require(amount > 0, "AuraVault: zero amount");
        
        if (token == address(0)) {
            revert("AuraVault: use depositNative for ETH");
        }
        
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        emit Deposit(msg.sender, token, amount);
    }

    function depositNative() external payable onlyOwner {
        require(msg.value > 0, "AuraVault: zero amount");
        emit Deposit(msg.sender, address(0), msg.value);
    }

    function submit(
        address token,
        address[] calldata targets,
        uint256[] calldata amounts,
        string calldata desc
    ) external onlyOwner returns (uint256 id) {
        require(targets.length == amounts.length, "AuraVault: length mismatch");
        require(targets.length > 0, "AuraVault: empty targets");
        
        uint256 totalAmount = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            totalAmount += amounts[i];
        }
        require(totalAmount > 0, "AuraVault: zero total");

        id = proposalCounter++;
        Proposal storage proposal = _proposals[id];
        proposal.proposer = msg.sender;
        proposal.token = token;
        proposal.targets = targets;
        proposal.amounts = amounts;
        proposal.description = desc;

        emit ProposalCreated(id, msg.sender);
    }

    function sign(uint256 id) external onlyOwner {
        Proposal storage proposal = _proposals[id];
        require(proposal.proposer != address(0), "AuraVault: nonexistent proposal");
        require(!proposal.executed, "AuraVault: already executed");
        require(!proposal.signed[msg.sender], "AuraVault: already signed");

        proposal.signed[msg.sender] = true;
        proposal.voteCount++;

        emit Signed(id, msg.sender);
    }

    function execute(uint256 id) external nonReentrant {
        Proposal storage proposal = _proposals[id];
        require(proposal.proposer != address(0), "AuraVault: nonexistent proposal");
        require(!proposal.executed, "AuraVault: already executed");
        require(proposal.voteCount >= THRESHOLD, "AuraVault: insufficient votes");

        proposal.executed = true;

        if (proposal.token == address(0)) {
            for (uint256 i = 0; i < proposal.targets.length; i++) {
                (bool success, ) = proposal.targets[i].call{value: proposal.amounts[i]}("");
                require(success, "AuraVault: ETH transfer failed");
            }
        } else {
            for (uint256 i = 0; i < proposal.targets.length; i++) {
                IERC20(proposal.token).safeTransfer(proposal.targets[i], proposal.amounts[i]);
            }
        }

        emit Executed(id);
    }

    function getProposalMeta(uint256 id)
        external
        view
        returns (
            address proposer,
            address token,
            address[] memory targets,
            uint256[] memory amounts,
            uint256 voteCount,
            bool executed,
            string memory description
        )
    {
        Proposal storage proposal = _proposals[id];
        require(proposal.proposer != address(0), "AuraVault: nonexistent proposal");
        
        return (
            proposal.proposer,
            proposal.token,
            proposal.targets,
            proposal.amounts,
            proposal.voteCount,
            proposal.executed,
            proposal.description
        );
    }

    receive() external payable {
        // Allow direct ETH transfers
    }
}