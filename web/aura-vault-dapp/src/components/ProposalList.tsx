import React from 'react';
import { useReadContract } from 'wagmi';
import { formatEther } from 'viem';
import { CONTRACT_ADDRESS } from '../config/contract';
import AuraVaultMVP from '../abi/AuraVaultMVP.json';

interface Proposal {
  proposer: string;
  token: string;
  targets: string[];
  amounts: bigint[];
  voteCount: bigint;
  executed: boolean;
  description: string;
}

interface ProposalListProps {
  maxProposals?: number;
}

export default function ProposalList({ maxProposals = 10 }: ProposalListProps) {
  const { data: proposalCounter } = useReadContract({
    address: CONTRACT_ADDRESS as `0x${string}`,
    abi: AuraVaultMVP,
    functionName: 'proposalCounter',
  });

  const proposalIds = Array.from(
    { length: Math.min(Number(proposalCounter || 0), maxProposals) },
    (_, i) => i
  ).reverse();

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Proposals</h3>
      
      {proposalIds.length === 0 ? (
        <p className="text-gray-500">No proposals yet</p>
      ) : (
        <div className="space-y-4">
          {proposalIds.map((id) => (
            <ProposalCard key={id} proposalId={id} />
          ))}
        </div>
      )}
    </div>
  );
}

function ProposalCard({ proposalId }: { proposalId: number }) {
  const { data: proposal } = useReadContract({
    address: CONTRACT_ADDRESS as `0x${string}`,
    abi: AuraVaultMVP,
    functionName: 'getProposalMeta',
    args: [BigInt(proposalId)],
  }) as { data: [string, string, string[], bigint[], bigint, boolean, string] | undefined };

  if (!proposal) return null;

  const [proposer, token, targets, amounts, voteCount, executed, description] = proposal;
  const totalAmount = amounts.reduce((sum: bigint, amount: bigint) => sum + amount, BigInt(0));

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-gray-900">
          Proposal #{proposalId}
        </h4>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          executed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {executed ? 'Executed' : 'Pending'}
        </span>
      </div>
      
      <p className="text-sm text-gray-600 mb-2">{description}</p>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="font-medium">Proposer:</span>
          <p className="text-gray-600 font-mono text-xs">
            {proposer.slice(0, 6)}...{proposer.slice(-4)}
          </p>
        </div>
        
        <div>
          <span className="font-medium">Votes:</span>
          <p className="text-gray-600">{voteCount.toString()} / 3</p>
        </div>
        
        <div>
          <span className="font-medium">Total Amount:</span>
          <p className="text-gray-600">{formatEther(totalAmount)} BNB</p>
        </div>
        
        <div>
          <span className="font-medium">Token:</span>
          <p className="text-gray-600 font-mono text-xs">
            {token === '0x0000000000000000000000000000000000000000' ? 'BNB' : 
             `${token.slice(0, 6)}...${token.slice(-4)}`}
          </p>
        </div>
      </div>
      
      {targets.length > 0 && (
        <div className="mt-3">
          <span className="font-medium text-sm">Targets:</span>
          <div className="text-xs text-gray-600 font-mono mt-1">
            {targets.map((target: string, index: number) => (
              <div key={index}>
                {target.slice(0, 6)}...{target.slice(-4)}: {formatEther(amounts[index])} BNB
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}