/**
 * ALIMENTA GLOBAL — Continuous Integration & On-Demand Dataset Compiler
 * Triggers POST /api/compile to run scripts/compile.py in isolated subprocess
 * Displays live terminal logs, schema validation statuses, and dataset metrics.
 */

import React, { useState } from 'react';

export const OnDemandCompiler: React.FC = () => {
  const [running, setRunning] = useState<boolean>(false);
  const [logs, setLogs] = useState<string>(
    'Waiting for compilation instruction. Click "Trigger Recompile Pipeline" above to execute scripts/compile.py and stream output telemetry.'
  );
  const [lastStatus, setLastStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleTriggerCompile = async () => {
    setRunning(true);
    setLastStatus('idle');
    setLogs(
      'Initiating POST /api/compile request to ALIMENTA backend orchestrator...\n' +
      'Executing scripts/compile.py in isolated sub-process with PYTHONUTF8=1...\n' +
      'Re-validating YAML entities against JSON schemas...\n'
    );

    try {
      const res = await fetch('/api/compile', { method: 'POST' });
      const data = await res.json();

      setLogs(prev =>
        prev +
        `Status: ${data.status?.toUpperCase()} (Exit code: ${data.code})\n` +
        '------------------------------------------------------------\n' +
        (data.stdout || data.stderr || 'No stdout/stderr emitted.')
      );
      setLastStatus(data.code === 0 ? 'success' : 'error');
    } catch (err: any) {
      setLogs(prev => prev + `\nNetwork Error communicating with /api/compile: ${err.message}`);
      setLastStatus('error');
    } finally {
      setRunning(false);
    }
  };

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950 text-amber-400 border border-amber-800 text-xs font-bold tracking-widest uppercase mb-2">
            ⚡ Continuous Integration Orchestrator
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            On-Demand Dataset Compiler & Pipeline Monitor
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Directly invokes the backend compilation pipeline (<code className="text-cyan-400 font-mono">POST /api/compile</code>), validates YAML schemas, and updates JSON caches in real time.
          </p>
        </div>

        <button
          onClick={handleTriggerCompile}
          disabled={running}
          className="px-5 py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm disabled:opacity-50 transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20"
        >
          {running ? '⏳ Running Pipeline Subprocess...' : '⚡ Trigger Recompile Pipeline'}
        </button>
      </div>

      {/* Terminal View */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 font-mono text-xs text-slate-300">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3 text-[11px] text-slate-500">
          <span>TERMINAL STDOUT / STDERR STREAM</span>
          <span className={lastStatus === 'success' ? 'text-emerald-400' : lastStatus === 'error' ? 'text-rose-400' : 'text-slate-500'}>
            STATUS: {lastStatus.toUpperCase()}
          </span>
        </div>
        <pre className="whitespace-pre-wrap max-h-80 overflow-y-auto leading-relaxed font-mono">
          {logs}
        </pre>
      </div>
    </section>
  );
};
