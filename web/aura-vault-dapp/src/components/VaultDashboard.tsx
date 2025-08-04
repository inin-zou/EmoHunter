import React, { useState } from 'react';
import { useAccount, useReadContract, useWriteContract } from 'wagmi';
import { parseEther } from 'viem';
import { CONTRACT_ADDRESS } from '../config/contract';
import AuraVaultMVP from '../abi/AuraVaultMVP.json';

export default function VaultDashboard() {
  const { address, isConnected } = useAccount();
  const { writeContract } = useWriteContract();
  
  const [tokenAddress, setTokenAddress] = useState('');
  const [amount, setAmount] = useState('');
  const [proposalId, setProposalId] = useState('');
  const [submitTargets, setSubmitTargets] = useState('');
  const [submitAmounts, setSubmitAmounts] = useState('');
  const [submitDescription, setSubmitDescription] = useState('');

  const { data: isOwner } = useReadContract({
    address: CONTRACT_ADDRESS as `0x${string}`,
    abi: AuraVaultMVP,
    functionName: 'isOwner',
    args: address ? [address as `0x${string}`] : undefined,
  }) as { data: boolean | undefined };

  const { data: proposalCounter } = useReadContract({
    address: CONTRACT_ADDRESS as `0x${string}`,
    abi: AuraVaultMVP,
    functionName: 'proposalCounter',
  }) as { data: bigint | undefined };

  const handleDeposit = async () => {
    if (!tokenAddress || !amount) return;
    
    try {
      await writeContract({
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: AuraVaultMVP,
        functionName: 'deposit',
        args: [tokenAddress as `0x${string}`, parseEther(amount)],
      });
    } catch (error) {
      console.error('Deposit failed:', error);
    }
  };

  const handleDepositNative = async () => {
    if (!amount) return;
    
    try {
      await writeContract({
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: AuraVaultMVP,
        functionName: 'depositNative',
        value: parseEther(amount),
      });
    } catch (error) {
      console.error('Native deposit failed:', error);
    }
  };

  const handleSubmitProposal = async () => {
    const targets = submitTargets.split(',').map(t => t.trim());
    const amounts = submitAmounts.split(',').map(a => parseEther(a.trim()));
    
    try {
      await writeContract({
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: AuraVaultMVP,
        functionName: 'submit',
        args: [
          tokenAddress as `0x${string}`,
          targets,
          amounts,
          submitDescription,
        ],
      });
    } catch (error) {
      console.error('Submit proposal failed:', error);
    }
  };

  const handleSign = async () => {
    if (!proposalId) return;
    
    try {
      await writeContract({
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: AuraVaultMVP,
        functionName: 'sign',
        args: [BigInt(proposalId)],
      });
    } catch (error) {
      console.error('Sign failed:', error);
    }
  };

  const handleExecute = async () => {
    if (!proposalId) return;
    
    try {
      await writeContract({
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: AuraVaultMVP,
        functionName: 'execute',
        args: [BigInt(proposalId)],
      });
    } catch (error) {
      console.error('Execute failed:', error);
    }
  };

  if (!isConnected) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Connect Your Wallet
          </h2>
          <p className="text-lg text-gray-600">
            Please connect your wallet to interact with the Aura Vault
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Stats */}
        <div className="lg:col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Connected Address</h3>
              <p className="mt-1 text-sm text-gray-900 font-mono">
                {address?.slice(0, 6)}...{address?.slice(-4)}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Is Owner</h3>
              <p className="mt-1 text-lg font-semibold">
                {isOwner ? '✅ Yes' : '❌ No'}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Total Proposals</h3>
              <p className="mt-1 text-lg font-semibold">
                {proposalCounter?.toString() ?? '0'}
              </p>
            </div>
          </div>
        </div>

        {/* Deposit Section */}
        {isOwner && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Deposit Funds</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Token Address (0x0 for BNB)
                </label>
                <input
                  type="text"
                  value={tokenAddress}
                  onChange={(e) => setTokenAddress(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  placeholder="0x..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Amount
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  placeholder="0.0"
                />
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={handleDeposit}
                  className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
                >
                  Deposit Token
                </button>
                <button
                  onClick={handleDepositNative}
                  className="flex-1 bg-pink-600 text-white py-2 px-4 rounded-md hover:bg-pink-700"
                >
                  Deposit BNB
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Proposal Section */}
        {isOwner && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Submit Proposal</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Token Address
                </label>
                <input
                  type="text"
                  value={tokenAddress}
                  onChange={(e) => setTokenAddress(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  placeholder="0x..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Target Addresses (comma-separated)
                </label>
                <input
                  type="text"
                  value={submitTargets}
                  onChange={(e) => setSubmitTargets(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  placeholder="0x...,0x...,0x..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Amounts (comma-separated)
                </label>
                <input
                  type="text"
                  value={submitAmounts}
                  onChange={(e) => setSubmitAmounts(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  placeholder="0.1,0.2,0.3"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <input
                  type="text"
                  value={submitDescription}
                  onChange={(e) => setSubmitDescription(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  placeholder="Proposal description"
                />
              </div>
              
              <button
                onClick={handleSubmitProposal}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
              >
                Submit Proposal
              </button>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Proposal ID
              </label>
              <input
                type="number"
                value={proposalId}
                onChange={(e) => setProposalId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                placeholder="0"
              />
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={handleSign}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
              >
                Sign
              </button>
              <button
                onClick={handleExecute}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
              >
                Execute
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}