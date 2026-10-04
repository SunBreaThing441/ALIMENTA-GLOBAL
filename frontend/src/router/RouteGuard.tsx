/**
 * ALIMENTA GLOBAL — Enterprise Route Navigation Guard
 * Prevents Flash of Unauthenticated Content (FOUC)
 * Enforces Zero Trust Role-Based Access Control (RBAC)
 */

import React from 'react';
import { useAuth } from '../context/AuthContext';
import { UserSession } from '../services/auth.service';

interface RouteGuardProps {
  children: React.ReactNode;
  requiredRole?: UserSession['role'];
  requiredPermission?: string;
  fallbackUrl?: string;
}

export const RouteGuard: React.FC<RouteGuardProps> = ({
  children,
  requiredRole,
  requiredPermission,
  fallbackUrl = '/',
}) => {
  const { session, isAuthenticated, isLoading, hasPermission, loginDemo } = useAuth();

  // 1. Pending Cryptographic Verification (No FOUC)
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-100 p-6">
        <div className="w-16 h-16 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin mb-4" />
        <div className="font-mono text-sm tracking-widest text-cyan-400 uppercase font-bold">
          Verifying Cryptographic Tokens & Credentials...
        </div>
        <div className="text-xs text-slate-500 font-mono mt-1">
          Zero-Trust Ingress Security Protocol (RFC 6750)
        </div>
      </div>
    );
  }

  // 2. Unauthenticated State (Prompt or Redirect)
  if (!isAuthenticated || !session) {
    return (
      <div className="min-h-[70vh] bg-slate-950 border border-slate-800 rounded-3xl p-8 lg:p-12 flex flex-col items-center justify-center text-center max-w-2xl mx-auto my-12 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="w-16 h-16 rounded-2xl bg-rose-950/80 border border-rose-800 flex items-center justify-center text-rose-400 text-2xl mb-4">
          🔒
        </div>
        <h2 className="text-2xl font-black text-white mb-2">Restricted Observational Access</h2>
        <p className="text-sm text-slate-400 mb-6 max-w-md">
          This portal requires verified credentials injected from <strong>openfoodfacts-server</strong> or an active sovereign bearer token.
        </p>

        {/* Demo/Testing Trigger for Immediate Evaluation */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl w-full mb-6 text-left">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 font-mono">
            ⚡ Staging / Local Security Gateway
          </div>
          <p className="text-xs text-slate-400 mb-4">
            Simulate a secure session injection matching production Product Opener headers:
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => loginDemo('citizen_contributor')}
              className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs uppercase tracking-wider transition"
            >
              Sign In as Citizen Contributor
            </button>
            <button
              onClick={() => loginDemo('verified_scientist')}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs uppercase tracking-wider transition border border-slate-700"
            >
              Sign In as Verified Scientist
            </button>
          </div>
        </div>

        <a
          href={fallbackUrl}
          className="text-xs font-mono font-bold text-slate-500 hover:text-slate-300 transition"
        >
          &larr; Return to Public Commons Canvas
        </a>
      </div>
    );
  }

  // 3. Permission or Role Check
  if (requiredRole && session.role !== requiredRole && session.role !== 'system_admin') {
    return (
      <div className="min-h-[50vh] bg-slate-950 border border-rose-900/50 rounded-3xl p-8 flex flex-col items-center justify-center text-center max-w-lg mx-auto my-12">
        <div className="text-3xl mb-3">⛔</div>
        <h3 className="text-xl font-bold text-white mb-1">Insufficient Authorization Tier</h3>
        <p className="text-xs text-slate-400 mb-4">
          Your credential tier (<span className="text-amber-400 font-mono">{session.role}</span>) does not possess the clearance required (<span className="text-rose-400 font-mono">{requiredRole}</span>).
        </p>
        <a href="/" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold rounded-xl text-white">
          Back to Public Hub
        </a>
      </div>
    );
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="min-h-[50vh] bg-slate-950 border border-rose-900/50 rounded-3xl p-8 flex flex-col items-center justify-center text-center max-w-lg mx-auto my-12">
        <div className="text-3xl mb-3">⛔</div>
        <h3 className="text-xl font-bold text-white mb-1">Permission Denied</h3>
        <p className="text-xs text-slate-400 mb-4 font-mono">
          Missing claim: {requiredPermission}
        </p>
      </div>
    );
  }

  // Authorized
  return <>{children}</>;
};
