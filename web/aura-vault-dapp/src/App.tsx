import React from 'react';
import { WagmiProvider } from 'wagmi';
import { RainbowKitProvider, ConnectButton } from '@rainbow-me/rainbowkit';
import '@rainbow-me/rainbowkit/styles.css';
import { config, queryClient } from './config/wagmi';
import { QueryClientProvider } from '@tanstack/react-query';
import VaultDashboard from './components/VaultDashboard';

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
            <header className="bg-white shadow-sm border-b">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center py-4">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Aura Vault</h1>
                    <p className="text-sm text-gray-600">Multi-signature vault on BSC Testnet</p>
                  </div>
                  <ConnectButton />
                </div>
              </div>
            </header>
            <main>
              <VaultDashboard />
            </main>
          </div>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default App;
