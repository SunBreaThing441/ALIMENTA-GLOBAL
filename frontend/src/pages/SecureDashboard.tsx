/**
 * ALIMENTA GLOBAL — Protected User Telemetry & Operations Dashboard
 * Protected by <RouteGuard> and managed via AuthContext
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { RouteGuard } from '../router/RouteGuard';

export const SecureDashboardContent: React.FC = () => {
  const { session, logout, timeRemainingSeconds } = useAuth();
  const [apiKeyRevoked, setApiKeyRevoked] = useState(false);

  const formatSeconds = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const s = secs % 60;
    return `${mins}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Top Banner with Session Telemetry */}
      <div className="p-6 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-3xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-bold">
              Authenticated Session Active
            </span>
          </div>
          <h1 className="text-2xl font-black text-white">
            Welcome, {session?.username}
          </h1>
          <div className="text-xs text-slate-400 font-mono mt-0.5">
            Role Tier: <strong className="text-emerald-400 uppercase">{session?.role.replace('_', ' ')}</strong> &middot; Node: {session?.organization || 'Independent Observer'}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-slate-950 border border-slate-800 px-4 py-2 rounded-xl text-right">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Token Expiry In</div>
            <div className="text-lg font-mono font-black text-amber-400">
              {formatSeconds(timeRemainingSeconds)}
            </div>
          </div>
          <button
            onClick={() => logout('User requested session termination')}
            className="px-4 py-2.5 rounded-xl bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 font-bold text-xs uppercase tracking-wider transition shadow-sm"
          >
            Terminate Session
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="text-xs text-slate-400 font-semibold mb-1">Audited Products</div>
          <div className="text-3xl font-black font-mono text-cyan-400">142</div>
          <div className="text-[11px] text-slate-500 mt-1">Verified on public commons</div>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="text-xs text-slate-400 font-semibold mb-1">Queue Verifications</div>
          <div className="text-3xl font-black font-mono text-emerald-400">8</div>
          <div className="text-[11px] text-slate-500 mt-1">Awaiting community peer-review</div>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="text-xs text-slate-400 font-semibold mb-1">Impact Score</div>
          <div className="text-3xl font-black font-mono text-amber-400">98.4%</div>
          <div className="text-[11px] text-slate-500 mt-1">Data veracity index</div>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl">
          <div className="text-xs text-slate-400 font-semibold mb-1">Security Clearance</div>
          <div className="text-xl font-black font-mono text-white mt-1 uppercase">Tier 3</div>
          <div className="text-[11px] text-emerald-400 mt-1 font-mono">OWASP Verified</div>
        </div>
      </div>

      {/* Cryptographic API Key Section */}
      <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-3xl">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-base font-bold text-white">Sovereign API Access Token</h3>
            <p className="text-xs text-slate-400">
              For academic pipelines, field mobile applications, and IoT inventory devices querying the local REST API hub.
            </p>
          </div>
          {!apiKeyRevoked && (
            <button
              onClick={() => setApiKeyRevoked(true)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold font-mono transition"
            >
              Rotate Key
            </button>
          )}
        </div>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl font-mono text-xs flex justify-between items-center text-slate-300">
          <span className="truncate mr-4">
            {apiKeyRevoked ? 'Key revoked. Generating new cryptographic pair...' : `${session?.token.substring(0, 32)}••••••••••••••••`}
          </span>
          <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
            {apiKeyRevoked ? 'Revoked' : 'Active (Bearer)'}
          </span>
        </div>
      </div>
    </div>
  );
};

export const SecureDashboardPage: React.FC = () => (
  <RouteGuard>
    <SecureDashboardContent />
  </RouteGuard>
);
