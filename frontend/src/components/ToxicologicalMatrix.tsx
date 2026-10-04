/**
 * ALIMENTA GLOBAL — Toxicological & Chemical Additive Matrix
 * Replaces legacy static page: whats-in-my-shampoo.html (Open Beauty Facts)
 * Comprehensive chemical screening interface for cosmetics & personal hygiene products
 */

import React, { useState } from 'react';
import type { CosmeticComposition } from '../types';

export const SAMPLE_COSMETICS: CosmeticComposition[] = [
  {
    id: 'shampoo-commercial-volume',
    productName: 'Commercial Intense Volume Daily Shampoo',
    brand: 'Global Brand Corp',
    category: 'shampoo',
    chemicalAudit: {
      silicones: true,
      sulfates: true,
      endocrineDisruptors: true,
      microplastics: true,
      allergens: ['Linalool', 'Citronellol', 'Hexyl Cinnamal', 'Lilial (Banned in EU)'],
    },
    inciIngredients: [
      'Aqua', 'Sodium Laureth Sulfate (SLES)', 'Cocamidopropyl Betaine', 'Dimethicone (Silicone)',
      'Sodium Chloride', 'Parfum', 'Phenoxyethanol', 'Carbomer', 'Guar Hydroxypropyltrimonium Chloride'
    ],
    riskRating: 'caution'
  },
  {
    id: 'shampoo-organic-aloe',
    productName: 'Certified Bio Gentle Aloe Care Bar Shampoo',
    brand: 'EcoCommons Bio',
    category: 'shampoo',
    chemicalAudit: {
      silicones: false,
      sulfates: false,
      endocrineDisruptors: false,
      microplastics: false,
      allergens: ['Limonene (Natural extract)'],
    },
    inciIngredients: [
      'Sodium Cocoyl Isethionate', 'Hydrogenated Vegetable Oil', 'Aqua', 'Polyglyceryl-4 Laurate',
      'Glycerin', 'Aloe Barbadensis Leaf Juice Powder', 'Parfum'
    ],
    riskRating: 'optimal'
  },
  {
    id: 'toothpaste-whitening',
    productName: 'Enamel Optic White Mineral Toothpaste',
    brand: 'DentalPro Care',
    category: 'toothpaste',
    chemicalAudit: {
      silicones: false,
      sulfates: true,
      endocrineDisruptors: false,
      microplastics: true,
      allergens: ['Eugenol'],
    },
    inciIngredients: [
      'Sorbitol', 'Aqua', 'Hydrated Silica', 'Sodium Lauryl Sulfate (SLS)', 'Aroma',
      'Sodium Monofluorophosphate', 'Titanium Dioxide (E171)'
    ],
    riskRating: 'moderate'
  }
];

export const ToxicologicalMatrix: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<CosmeticComposition>(SAMPLE_COSMETICS[0]);

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950 text-purple-400 border border-purple-800 text-xs font-bold tracking-widest uppercase mb-2">
            🧴 Open Beauty Facts Chemical Audit
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            Toxicological & Endocrine Disruptor Screening Matrix
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Modernized chemical screening engine replacing "What’s in my Shampoo?" to audit silicones, harsh sulfates, and potential endocrine disruptors.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Sample Product Selectors */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Select Product Sample to Audit
          </div>
          {SAMPLE_COSMETICS.map(item => (
            <div
              key={item.id}
              onClick={() => setSelectedProduct(item)}
              className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                selectedProduct.id === item.id
                  ? 'bg-slate-900 border-purple-500 shadow-lg shadow-purple-500/10 ring-1 ring-purple-500/50'
                  : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900/80'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-sm text-white">{item.productName}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                  item.riskRating === 'optimal'
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    : 'bg-rose-950 text-rose-300 border border-rose-800'
                }`}>
                  {item.riskRating}
                </span>
              </div>
              <div className="text-xs text-slate-400 font-mono">{item.brand} • {item.category}</div>
            </div>
          ))}
        </div>

        {/* Right Column: Chemical Ingestion & INCI Breakdown */}
        <div className="lg:col-span-7 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h3 className="text-lg font-bold text-white">{selectedProduct.productName}</h3>
              <span className="text-xs text-slate-400 font-mono">{selectedProduct.brand}</span>
            </div>

            {/* Toxicological Indicators Array */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
              {[
                { label: 'Silicones', active: selectedProduct.chemicalAudit.silicones, desc: 'Non-biodegradable' },
                { label: 'Sulfates (SLS/SLES)', active: selectedProduct.chemicalAudit.sulfates, desc: 'Harsh surfactant' },
                { label: 'Endocrine Flags', active: selectedProduct.chemicalAudit.endocrineDisruptors, desc: 'Hormonal concerns' },
                { label: 'Microplastics', active: selectedProduct.chemicalAudit.microplastics, desc: 'Synthetic polymers' },
              ].map(indicator => (
                <div
                  key={indicator.label}
                  className={`p-3 rounded-xl border flex flex-col justify-between ${
                    indicator.active
                      ? 'bg-rose-950/40 border-rose-800 text-rose-200'
                      : 'bg-emerald-950/40 border-emerald-800 text-emerald-200'
                  }`}
                >
                  <div className="text-xs font-bold">{indicator.label}</div>
                  <div className="text-[10px] font-mono mt-1 opacity-80">
                    {indicator.active ? '⚠ DETECTED' : '✓ CLEAR'}
                  </div>
                </div>
              ))}
            </div>

            {/* Allergens Identified */}
            <div className="mb-4">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Allergenic Fragrances & Contact Dermatitis Triggers
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedProduct.chemicalAudit.allergens.map(allergen => (
                  <span
                    key={allergen}
                    className="text-xs font-mono px-2.5 py-1 rounded-lg bg-amber-950/60 border border-amber-800/80 text-amber-300"
                  >
                    ⚠ {allergen}
                  </span>
                ))}
              </div>
            </div>

            {/* Full INCI Ingredient Trace */}
            <div>
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                INCI Declared Ingredients ({selectedProduct.inciIngredients.length})
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs font-mono text-slate-400 leading-relaxed">
                {selectedProduct.inciIngredients.join(' • ')}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
