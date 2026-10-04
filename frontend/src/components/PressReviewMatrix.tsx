/**
 * ALIMENTA GLOBAL — Press Review Matrix Component
 * Consumes /api/v2/press and legacy press-review-merged.json datasets.
 * Displays investigative disclosures, broadcasts, and articles with type filters and pagination.
 */

import React, { useState } from 'react';
import { usePressReview } from '../hooks/useEcosystemData';

export const PressReviewMatrix: React.FC = () => {
  const [selectedType, setSelectedType] = useState<string>('all');
  const [search, setSearch] = useState<string>('');
  const [page, setPage] = useState<number>(0);

  const { data, loading, error, refetch } = usePressReview(selectedType, search, 10, page);

  const items = data?.results || [];
  const total = data?.total || 0;

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950 text-amber-400 border border-amber-800 text-xs font-bold tracking-widest uppercase mb-2">
            📰 Global Media & Investigative Disclosures
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            International Press Review & Broadcast Archive
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Global news stories, investigative documentaries, and radio podcasts reporting on food processing, additives, and public health using Open Food Facts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-amber-400">
            {total.toLocaleString()} Verified Press Reports
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-6">
        <div className="md:col-span-8">
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            placeholder="🔍 Search 340+ press mentions, journalists, or media outlets..."
            className="w-full bg-slate-900 border border-slate-800 focus:border-amber-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition"
          />
        </div>

        <div className="md:col-span-4 flex items-center gap-2 overflow-x-auto">
          {[
            { id: 'all', label: 'All' },
            { id: 'article', label: 'Articles' },
            { id: 'video', label: 'Video & TV' },
            { id: 'podcast', label: 'Podcasts' },
          ].map(m => (
            <button
              key={m.id}
              onClick={() => { setSelectedType(m.id); setPage(0); }}
              className={`px-3 py-2 rounded-xl text-xs font-bold capitalize transition-all ${
                selectedType === m.id
                  ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/80 rounded-2xl p-6 text-center mb-6">
          <div className="text-2xl mb-2">⚠️</div>
          <h4 className="text-rose-400 font-bold text-base mb-1">Failed to fetch press disclosures</h4>
          <p className="text-xs text-slate-400 mb-4">{error}</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-rose-600 text-white font-bold text-xs rounded-xl hover:bg-rose-500 transition"
          >
            Retry Request
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
              <div className="h-3 bg-slate-800 rounded w-2/3 mb-4"></div>
              <div className="h-3 bg-slate-800 rounded w-1/3"></div>
            </div>
          ))}
        </div>
      )}

      {/* Cards Grid */}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          {items.map(item => (
            <div
              key={item.id}
              className="bg-slate-900/60 border border-slate-800/80 hover:border-amber-500/40 transition-all rounded-2xl p-5 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800/60 uppercase">
                    {item.type || 'Press'}
                  </span>
                  <span className="text-xs font-mono text-slate-500">{item.date}</span>
                </div>
                <h4 className="font-bold text-base text-white group-hover:text-amber-400 transition-colors line-clamp-2 mb-2 leading-snug">
                  {item.title}
                </h4>
                <div className="text-xs text-slate-400 mb-3">
                  Published by <strong className="text-slate-200">{item.source}</strong>
                </div>
                {item.verbatim && (
                  <p className="text-xs text-slate-400/90 italic border-l-2 border-slate-700 pl-3 my-2 line-clamp-2">
                    &ldquo;{item.verbatim}&rdquo;
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs mt-3">
                <span className="text-slate-500 font-mono text-[11px]">{item.media_scope || 'Global Reach'}</span>
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-amber-400 hover:text-amber-300 font-bold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
                >
                  View Coverage &rarr;
                </a>
              </div>
            </div>
          ))}

          {items.length === 0 && (
            <div className="col-span-full py-16 text-center text-slate-500 font-mono text-sm">
              No press mentions match your search query.
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
          Showing {page * 10 + 1}–{Math.min((page + 1) * 10, total)} of {total}
        </span>

        <button
          disabled={(page + 1) * 10 >= total || loading}
          onClick={() => setPage(p => p + 1)}
          className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-slate-300 disabled:opacity-40 hover:bg-slate-800 transition"
        >
          Next Page &rarr;
        </button>
      </div>
    </section>
  );
};
