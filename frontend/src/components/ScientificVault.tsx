/**
 * ALIMENTA GLOBAL — Scientific Publications Vault Component
 * Consumes /api/v2/publications and publications.json datasets.
 * Displays peer-reviewed studies, epidemiological research, and DOI citations.
 */

import React, { useState } from 'react';
import { usePublications } from '../hooks/useEcosystemData';

export const ScientificVault: React.FC = () => {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);

  const { data, loading, error, refetch } = usePublications(search, 12, page);

  const items = data?.results || [];
  const total = data?.total || 0;

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold tracking-widest uppercase mb-2">
            📚 Global Academic Citations & Research
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            Scientific Publications & Peer-Reviewed Studies
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            138 peer-reviewed research papers from The Lancet, Nature Food, British Medical Journal (BMJ), and Inserm utilizing Open Food Facts for nutritional epidemiology.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400">
            {total.toLocaleString()} Academic Publications
          </span>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          placeholder="🔍 Search publications by title, author (e.g., Hercberg, Touvier), journal, or DOI..."
          className="w-full bg-slate-900 border border-slate-800 focus:border-emerald-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition"
        />
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/80 rounded-2xl p-6 text-center mb-6">
          <div className="text-2xl mb-2">⚠️</div>
          <h4 className="text-rose-400 font-bold text-base mb-1">Failed to fetch scientific publications</h4>
          <p className="text-xs text-slate-400 mb-4">{error}</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-rose-600 text-white font-bold text-xs rounded-xl hover:bg-rose-500 transition"
          >
            Retry Query
          </button>
        </div>
      )}

      {/* Loading Skeletons */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 animate-pulse">
              <div className="h-4 bg-slate-800 rounded w-1/4 mb-3"></div>
              <div className="h-5 bg-slate-800 rounded w-4/5 mb-3"></div>
              <div className="h-3 bg-slate-800 rounded w-1/2 mb-4"></div>
              <div className="h-3 bg-slate-800 rounded w-1/3"></div>
            </div>
          ))}
        </div>
      )}

      {/* Cards Grid */}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          {items.map(item => {
            const authorsStr = Array.isArray(item.authors)
              ? item.authors.slice(0, 3).join(', ') + (item.authors.length > 3 ? ' et al.' : '')
              : item.authors || 'Academic Research Consortium';

            const linkUrl = item.url || (item.doi ? (item.doi.startsWith('http') ? item.doi : `https://doi.org/${item.doi}`) : '#');

            return (
              <div
                key={item.id}
                className="bg-slate-900/60 border border-slate-800/80 hover:border-emerald-500/40 transition-all rounded-2xl p-5 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                      {item.year || 2024}
                    </span>
                    <span className="text-xs text-slate-400 font-medium truncate max-w-[280px]">
                      {item.journal || 'Peer-Reviewed Study'}
                    </span>
                  </div>

                  <h4 className="font-bold text-base text-white group-hover:text-emerald-400 transition-colors line-clamp-2 mb-2 leading-snug">
                    {item.title}
                  </h4>

                  <div className="text-xs text-slate-400 font-mono mb-3 line-clamp-1">
                    {authorsStr}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs mt-3">
                  <span className="text-slate-500 font-mono text-[11px]">
                    {item.doi ? `DOI: ${item.doi.substring(0, 16)}...` : 'Academic Citation'}
                  </span>
                  <a
                    href={linkUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-400 hover:text-emerald-300 font-bold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
                  >
                    Read Paper &rarr;
                  </a>
                </div>
              </div>
            );
          })}

          {items.length === 0 && (
            <div className="col-span-full py-16 text-center text-slate-500 font-mono text-sm">
              No scientific papers match your search parameters.
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-800">
        <button
          disabled={page === 0 || loading}
          onClick={() => setPage(p => Math.max(0, p - 1))}
          className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition"
        >
          &larr; Previous Page
        </button>

        <span className="text-xs font-mono text-slate-400">
          Showing {page * 12 + 1}–{Math.min((page + 1) * 12, total)} of {total}
        </span>

        <button
          disabled={(page + 1) * 12 >= total || loading}
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition"
        >
          Next Page &rarr;
        </button>
      </div>
    </section>
  );
};
