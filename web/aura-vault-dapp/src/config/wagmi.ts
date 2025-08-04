import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { bscTestnet } from 'wagmi/chains';
import { QueryClient } from '@tanstack/react-query';

export const config = getDefaultConfig({
  appName: 'Aura Vault DApp',
  projectId: 'aura-vault-dapp',
  chains: [bscTestnet],
  ssr: false,
});

export const queryClient = new QueryClient();