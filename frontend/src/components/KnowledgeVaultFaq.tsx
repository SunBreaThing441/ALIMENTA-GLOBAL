/**
 * ALIMENTA GLOBAL — Knowledge Vault FAQ Component
 * Consumes /api/v2/faq?lang=en and data/faq.json.
 * Provides interactive accordion navigation, multilingual switching, and search.
 */

import React, { useState } from 'react';
import { useFaq } from '../hooks/useEcosystemData';

export const KnowledgeVaultFaq: React.FC = () => {
  const [lang, setLang] = useState<'en' | 'fr'>('en');
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const { data: categories, loading, error, refetch } = useFaq(lang);

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs font-bold tracking-widest uppercase mb-2">
            ❓ UNESCO Knowledge Commons
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            Frequently Answered Inquiries & Protocols
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Curated encyclopedic documentation regarding database provenance, algorithmic grading (Nutri-Score, NOVA, Eco-Score), and open data licensing.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setLang('en')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              lang === 'en'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            English (EN)
          </button>
          <button
            onClick={() => setLang('fr')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              lang === 'fr'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            Français (FR)
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/80 rounded-2xl p-6 text-center mb-6">
          <div className="text-2xl mb-2">⚠️</div>
          <h4 className="text-rose-400 font-bold text-base mb-1">Failed to load Knowledge Base</h4>
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
        <div className="space-y-4 mb-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 animate-pulse">
              <div className="h-5 bg-slate-800 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-slate-800 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-slate-800 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}

      {/* Categories & Q&A Accordion */}
      {!loading && !error && (
        <div className="space-y-4">
          {categories.map((cat, catIdx) => (
            <div
              key={cat.id || catIdx}
              className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 transition-all"
            >
              <div
                onClick={() => setActiveCategory(activeCategory === cat.id ? null : cat.id)}
                className="flex items-center justify-between cursor-pointer group"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                    Category {String(catIdx + 1).padStart(2, '0')}
                  </span>
                  <h3 className="text-base font-bold text-white group-hover:text-cyan-400 transition-colors">
                    {cat.title}
                  </h3>
                </div>
                <span className="text-slate-400 font-bold text-sm">
                  {activeCategory === cat.id ? '−' : '+'}
                </span>
              </div>

              {/* Collapsible Questions */}
              {activeCategory === cat.id && (
                <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-3">
                  {cat.questions.map((q, qIdx) => (
                    <details
                      key={q.id || qIdx}
                      className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs group"
                    >
                      <summary className="font-bold text-slate-200 cursor-pointer hover:text-cyan-400 outline-none select-none">
                        {q.question}
                      </summary>
                      <div
                        className="mt-3 text-slate-400 leading-relaxed border-t border-slate-900 pt-3 prose prose-invert max-w-none text-xs"
                        dangerouslySetInnerHTML={{ __html: q.answer_html }}
                      />
                    </details>
                  ))}
                </div>
              )}
            </div>
          ))}

          {categories.length === 0 && (
            <div className="py-16 text-center text-slate-500 font-mono text-sm">
              No knowledge base categories available for this language.
            </div>
          )}
        </div>
      )}
    </section>
  );
};
