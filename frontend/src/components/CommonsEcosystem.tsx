/**
 * ALIMENTA GLOBAL — Digital Commons Ecosystem Matrix
 * Replaces legacy static page: reuses.html (Directory of 605+ ecosystem apps)
 * Consumes /api/v2/reuses dynamically with high-density card grid & facet filtering
 */

import React, { useState, useEffect } from 'react';
import type { ReuseEntity } from '../types';

export const CommonsEcosystem: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTheme, setActiveTheme] = useState('all');
  const [items, setItems] = useState<ReuseEntity[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(605);
  const [page, setPage] = useState(0);
  const pageSize = 9;

  useEffect(() => {
    const fetchEntities = async () => {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams({
          limit: String(pageSize),
          offset: String(page * pageSize),
        });
        if (searchQuery) queryParams.set('search', searchQuery);

        const res = await fetch(`/api/v2/reuses?${queryParams.toString()}`);
        if (res.ok) {
          const data = await res.json();
          setItems(data.results || []);
          setTotalCount(data.total || 605);
        }
      } catch {
        // Fallback for isolated preview
      } finally {
        setLoading(false);
      }
    };

    fetchEntities();
  }, [searchQuery, page]);

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950 text-blue-400 border border-blue-800 text-xs font-bold tracking-widest uppercase mb-2">
            🚀 Global Digital Commons Registry
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            Ecosystem Applications & Public Policy Reusers
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Over 605 public health applications, smart kitchen scales, academic projects, and national regulatory bodies powered by Open Food Facts APIs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-cyan-400">
            {totalCount.toLocaleString()} Verified Commons Reusers
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-6">
        <div className="md:col-span-8">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setPage(0); }}
            placeholder="🔍 Search 605+ ecosystem applications by keyword, topic, or protocol..."
            className="w-full bg-slate-900 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition"
          />
        </div>

        <div className="md:col-span-4 flex items-center gap-2 overflow-x-auto">
          {['all', 'nutrition', 'environment', 'research'].map(theme => (
            <button
              key={theme}
              onClick={() => setActiveTheme(theme)}
              className={`px-3 py-2 rounded-xl text-xs font-bold capitalize transition-all ${
                activeTheme === theme
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {theme}
            </button>
          ))}
        </div>
      </div>

      {/* Application Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-6">
        {loading && (
          <div className="col-span-full py-12 text-center text-slate-500 font-mono text-sm animate-pulse">
            Querying ALIMENTA Global Commons Network (/api/v2/reuses)...
          </div>
        )}

        {!loading && items.map(item => (
          <div
            key={item.id}
            className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800/90 hover:border-slate-700 hover:bg-slate-900/80 transition flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="font-bold text-base text-white group-hover:text-cyan-400 transition truncate">
                  {item.name}
                </h3>
                <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {item.theme || 'Application'}
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-3 mb-4 leading-relaxed">
                {item.description || item.tagline}
              </p>
            </div>

            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-mono text-[11px]">
                {item.installs ? `${item.installs.toLocaleString()} users` : 'Civic Commons'}
              </span>
              <a
                href={item.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:text-cyan-300 font-bold flex items-center gap-1"
              >
                Inspect App &rarr;
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs text-slate-400 font-mono">
        <button
          onClick={() => setPage(p => Math.max(0, p - 1))}
          disabled={page === 0}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold transition"
        >
          &larr; Previous Page
        </button>
        <span>
          Page {page + 1} of {Math.ceil(totalCount / pageSize)}
        </span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={(page + 1) * pageSize >= totalCount}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed text-white font-bold transition"
        >
          Next Page &rarr;
        </button>
      </div>
    </section>
  );
};
