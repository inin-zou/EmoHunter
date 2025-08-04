# AuraVault MVP - Foundry Implementation

A minimalist multi-signature treasury vault contract built for Aura Foundation, implementing the `deposit → submit → sign (3 of N) → execute` workflow.

## 🚀 Quick Start

### Prerequisites
- [Foundry](https://book.getfoundry.sh/getting-started/installation)
- Node.js (for deployment scripts)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd contracts

# Install dependencies
forge install

# Build contracts
forge build

# Run tests
forge test -vv
```

## 📋 Contract Overview

### AuraVaultMVP.sol
The main vault contract implementing:
- Multi-signature governance (3 of N threshold)
- ERC-20 and native ETH support
- Proposal-based fund distribution
- Gas-efficient voting mechanism

### Key Features
- **Minimalist Design**: 158 lines, OpenZeppelin v5 dependencies
- **Security**: ReentrancyGuard, SafeERC20, CEI pattern
- **Flexibility**: Support for any ERC-20 token + native ETH
- **Transparency**: All actions emit events for easy tracking

## 🔧 Contract Interface

### Core Functions

#### For Owners (Multi-sig members)
```solidity
// Deposit ERC-20 tokens
function deposit(address token, uint256 amount) external onlyOwner

// Deposit native ETH
function depositNative() external payable onlyOwner

// Create a proposal
function submit(
    address token,
    address[] calldata targets,
    uint256[] calldata amounts,
    string calldata desc
) external onlyOwner returns (uint256 id)

// Sign a proposal
function sign(uint256 id) external onlyOwner
```

#### For Anyone
```solidity
// Execute an approved proposal
function execute(uint256 id) external nonReentrant

// View proposal details
function getProposalMeta(uint256 id) external view returns (...)
```

### Events
```solidity
event Deposit(address indexed from, address indexed token, uint256 amount)
event ProposalCreated(uint256 indexed id, address indexed proposer)
event Signed(uint256 indexed id, address indexed owner)
event Executed(uint256 indexed id)
```

## 🎯 Usage Examples

### 1. Deploy the Contract

#### Setup Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your private key and settings
nano .env
```

#### Deploy with Foundry Scripts

### Basic Workflow
```solidity
// 1. Deploy with 4 owners, threshold 3
address[] memory owners = [owner1, owner2, owner3, owner4];
AuraVaultMVP vault = new AuraVaultMVP(owners, 3);

// 2. Deposit funds
vault.deposit(USDC, 10000e6); // 10,000 USDC
vault.depositNative{value: 5 ether}(); // 5 ETH

// 3. Create proposal (only owners)
address[] memory targets = [user1, user2];
uint256[] memory amounts = [6000e6, 4000e6];
uint256 proposalId = vault.submit(USDC, targets, amounts, "April rewards");

// 4. Sign proposal (need 3 signatures)
vault.sign(proposalId); // owner1 signs
vault.sign(proposalId); // owner2 signs
vault.sign(proposalId); // owner3 signs

// 5. Execute (anyone can execute)
vault.execute(proposalId);
```

## 🧪 Testing

### Run All Tests
```bash
forge test -vv
```

### Coverage Report
```bash
forge coverage
```

### Specific Test Cases
- `test_CompleteWorkflowERC20()` - Full ERC-20 workflow
- `test_CompleteWorkflowNative()` - Full native ETH workflow
- `test_RevertWhenNonOwner()` - Permission checks
- `test_RevertExecuteWithoutEnoughVotes()` - Threshold validation

## 🔐 Security Considerations

- **Multi-sig protection**: Requires 3 of 4 signatures for execution
- **Reentrancy protection**: All external calls protected by ReentrancyGuard
- **ERC-20 safety**: SafeERC20 handles non-standard tokens
- **No admin functions**: Immutable design, no owner changes or pausing

## 📊 Gas Optimization

- Efficient storage usage with minimal state changes
- Batched transfers reduce per-transaction overhead
- Vote tracking uses simple boolean flags
- Estimated gas: ~600k for complete ERC-20 workflow

## 🔍 Verification

### Main Contract Verification
```bash
forge verify-contract --chain-id 1 <contract-address> src/AuraVaultMVP.sol:AuraVaultMVP
```

### Test Verification
The test suite includes:
- ✅ Constructor validation
- ✅ ERC-20 deposit/withdrawal
- ✅ Native ETH deposit/withdrawal
- ✅ Multi-signature workflow
- ✅ Edge case handling
- ✅ Access control
- ✅ Event emission

## Deployment

* Network Name: BSC Testnet
* RPC URL: https://data-seed-prebsc-1-s1.bnbchain.org:8545
* Chain ID: 97
* Symbol: tBNB
* Block Explorer: https://testnet.bscscan.com/

```bash
forge script script/DeployAuraVault.s.sol:DeployAuraVault \
    --rpc-url https://data-seed-prebsc-1-s1.bnbchain.org:8545 \
    --broadcast

forge verify-contract \
    --chain-id 97 \
    --constructor-args $(cast abi-encode "constructor(address[],uint256)" "[0x123...,0x456...,0x789...,0xabc...]" 3) \
    --etherscan-api-key $ETHERSCAN_API_KEY \
    --compiler-version 0.8.28 \
    YOUR_CONTRACT_ADDRESS \
    src/AuraVaultMVP.sol:AuraVaultMVP
```
## 🤝 Contributing

1. Install dependencies: `forge install`
2. Run tests: `forge test`
3. Format code: `forge fmt`
4. Check gas: `forge snapshot`
5. Submit PR with clear description

## 📄 License

MIT License - see LICENSE file for details