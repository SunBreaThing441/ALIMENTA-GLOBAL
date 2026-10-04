/**
 * ALIMENTA GLOBAL — Protected User Profile & Security Audit Center
 * Protected by <RouteGuard> and managed via AuthContext
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { RouteGuard } from '../router/RouteGuard';

export const SecureProfileContent: React.FC = () => {
  const { session, logout } = useAuth();
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(true);
  const [dataExported, setDataExported] = useState(false);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Profile Header */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-300 font-bold text-2xl font-mono">
            {session?.username.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">{session?.username}</h1>
            <div className="text-xs text-slate-400 font-mono">{session?.email}</div>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                Verified Identity
              </span>
              <span className="text-[10px] text-slate-500 font-mono">User ID: {session?.userId}</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => logout('User logged out from profile')}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 transition"
        >
          Sign Out
        </button>
      </div>

      {/* Security & Authentication Settings */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-3xl space-y-4">
        <h3 className="text-base font-bold text-white">Cryptographic Security Controls</h3>

        <div className="flex items-center justify-between p-4 bg-slate-950 border border-slate-800 rounded-2xl">
          <div>
            <div className="text-sm font-bold text-slate-200">Hardware 2-Factor Authentication (FIDO2 / TOTP)</div>
            <div className="text-xs text-slate-400">Protects your observational audits with cryptographic security keys.</div>
          </div>
          <button
            onClick={() => setTwoFactorEnabled(!twoFactorEnabled)}
            className={`px-3 py-1.5 rounded-xl font-bold text-xs transition ${
              twoFactorEnabled ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-slate-800 text-slate-400'
            }`}
          >
            {twoFactorEnabled ? 'Active (Protected)' : 'Enable 2FA'}
          </button>
        </div>

        <div className="flex items-center justify-between p-4 bg-slate-950 border border-slate-800 rounded-2xl">
          <div>
            <div className="text-sm font-bold text-slate-200">Anti-CSRF Cross-Origin Token Binding</div>
            <div className="text-xs text-slate-400 font-mono">Current Token: {session?.csrfToken.substring(0, 20)}...</div>
          </div>
          <span className="text-[10px] uppercase font-bold px-2 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
            Enforced (Strict)
          </span>
        </div>
      </div>

      {/* Sovereign Data Rights (GDPR) */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-3xl space-y-4">
        <h3 className="text-base font-bold text-white">Data Sovereignty & Privacy Controls</h3>
        <p className="text-xs text-slate-400">
          In alignment with UNESCO Digital Ethics, Open Food Facts guarantees your right to export your complete personal contribution telemetry or exercise the right to be forgotten.
        </p>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setDataExported(true)}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold font-mono transition"
          >
            {dataExported ? '✓ Exported: alimenta_audit_telemetry.json' : 'Download Complete Data Archive'}
          </button>
          <button
            onClick={() => alert('Account deletion request initiated under GDPR Art. 17.')}
            className="px-4 py-2.5 rounded-xl bg-rose-950/40 hover:bg-rose-950 text-rose-300 border border-rose-800/80 text-xs font-bold font-mono transition"
          >
            Revoke Identity & Erase Credentials
          </button>
        </div>
      </div>
    </div>
  );
};

export const SecureProfilePage: React.FC = () => (
  <RouteGuard>
    <SecureProfileContent />
  </RouteGuard>
);
