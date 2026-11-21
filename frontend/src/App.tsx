import React, { useState } from 'react';
import { CounterView } from './views/CounterView.tsx';
import { CustomerWitnessView } from './views/CustomerWitnessView.tsx';
import { PublicVerifyView } from './views/PublicVerifyView.tsx';
import { Shield, UserCheck, CheckCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'counter' | 'witness' | 'verify'>('counter');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="bg-slate-900 text-white border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gold-500 flex items-center justify-center font-bold text-slate-950 text-lg">
              G
            </div>
            <div>
              <span className="font-bold text-base tracking-tight">GOLD TRUST AI</span>
              <span className="text-[10px] block text-gold-400 font-mono tracking-widest uppercase">
                Dual-Ledger Trust Architecture
              </span>
            </div>
          </div>

          <nav className="flex items-center space-x-1 bg-slate-800 p-1 rounded-xl">
            <button
              onClick={() => setCurrentTab('counter')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                currentTab === 'counter'
                  ? 'bg-gold-500 text-slate-950 shadow'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>Counter Appraisal</span>
            </button>
            <button
              onClick={() => setCurrentTab('witness')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                currentTab === 'witness'
                  ? 'bg-gold-500 text-slate-950 shadow'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Customer Screen</span>
            </button>
            <button
              onClick={() => setCurrentTab('verify')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                currentTab === 'verify'
                  ? 'bg-gold-500 text-slate-950 shadow'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Public Verifier</span>
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 py-8 px-4">
        {currentTab === 'counter' && <CounterView />}
        {currentTab === 'witness' && <CustomerWitnessView />}
        {currentTab === 'verify' && <PublicVerifyView />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        Gold Trust AI · Built with RFC 8785 Canonical JSON · PostgreSQL Deferred Triggers · Zero Floating-Point Arithmetic
      </footer>
    </div>
  );
};
