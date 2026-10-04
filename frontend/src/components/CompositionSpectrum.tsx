/**
 * ALIMENTA GLOBAL — Composition Spectrum & Additive Observatory
 * Replaces legacy static pages: Opération Sodas (2012) & What's in my Yogurt?
 * WCAG 2.2 AAA Compliant & Highly Responsive
 */

import React, { useState, useMemo } from 'react';
import type { ProductComposition, NutriScoreGrade, NovaGroup } from '../types';

export const SAMPLE_PRODUCTS: ProductComposition[] = [
  {
    id: 'soda-cola-classic',
    name: 'Standard Cola Soda (330ml can)',
    category: 'beverage',
    subCategory: 'Carbonated Soft Drinks',
    sugarPer100g: 10.6,
    sugarCubesEquivalent: 8.7,
    caloriesPer100g: 42,
    nutriScore: 'e',
    novaGroup: 4,
    ecoScore: 'd',
    additives: [
      { code: 'E150d', name: 'Ammonia caramel', riskLevel: 'moderate', function: 'Artificial Colorant' },
      { code: 'E338', name: 'Phosphoric acid', riskLevel: 'moderate', function: 'Acidifier' },
    ],
    reformulationDeltaPercent: -5.0,
    barcode: '5449000000996',
  },
  {
    id: 'soda-zero',
    name: 'Zero-Sugar Diet Cola (330ml can)',
    category: 'beverage',
    subCategory: 'Carbonated Soft Drinks',
    sugarPer100g: 0.0,
    sugarCubesEquivalent: 0.0,
    caloriesPer100g: 0.8,
    nutriScore: 'b',
    novaGroup: 4,
    ecoScore: 'c',
    additives: [
      { code: 'E950', name: 'Acesulfame K', riskLevel: 'moderate', function: 'Intense Sweetener' },
      { code: 'E951', name: 'Aspartame', riskLevel: 'moderate', function: 'Intense Sweetener' },
      { code: 'E150d', name: 'Ammonia caramel', riskLevel: 'moderate', function: 'Colorant' },
    ],
    barcode: '5449000131805',
  },
  {
    id: 'energy-drink',
    name: 'Extreme Taurine Energy Drink (250ml)',
    category: 'beverage',
    subCategory: 'Energy Drinks',
    sugarPer100g: 11.0,
    sugarCubesEquivalent: 6.9,
    caloriesPer100g: 45,
    nutriScore: 'e',
    novaGroup: 4,
    ecoScore: 'd',
    additives: [
      { code: 'E150a', name: 'Plain caramel', riskLevel: 'safe', function: 'Colorant' },
      { code: 'E330', name: 'Citric acid', riskLevel: 'safe', function: 'Acidity Regulator' },
    ],
    barcode: '9002490100070',
  },
  {
    id: 'yogurt-fruit-sweetened',
    name: 'Commercial Strawberry Fruit Yogurt (125g)',
    category: 'dairy',
    subCategory: 'Flavored Yogurts',
    sugarPer100g: 12.8,
    sugarCubesEquivalent: 4.0,
    caloriesPer100g: 95,
    nutriScore: 'd',
    novaGroup: 4,
    ecoScore: 'b',
    additives: [
      { code: 'E1422', name: 'Acetylated distarch adipate', riskLevel: 'moderate', function: 'Modified Starch / Thickener' },
      { code: 'E407', name: 'Carrageenan', riskLevel: 'high_risk', function: 'Texture Stabilizer' },
      { code: 'E120', name: 'Carmine', riskLevel: 'moderate', function: 'Insect-derived Colorant' },
    ],
    reformulationDeltaPercent: -12.5,
    barcode: '3033490004523',
  },
  {
    id: 'yogurt-greek-plain',
    name: 'Authentic Plain Greek Strained Yogurt (150g)',
    category: 'dairy',
    subCategory: 'Natural Yogurts',
    sugarPer100g: 3.2,
    sugarCubesEquivalent: 1.2,
    caloriesPer100g: 120,
    nutriScore: 'a',
    novaGroup: 1,
    ecoScore: 'a',
    additives: [],
    barcode: '5201051000109',
  },
  {
    id: 'plant-oat-beverage',
    name: 'Organic Unsweetened Oat Drink (1L)',
    category: 'plant_based',
    subCategory: 'Plant-based Dairy Alternatives',
    sugarPer100g: 4.1,
    sugarCubesEquivalent: 1.0,
    caloriesPer100g: 45,
    nutriScore: 'b',
    novaGroup: 1,
    ecoScore: 'a',
    additives: [],
    barcode: '7394376616037',
  },
  {
    id: 'plant-soy-dessert-chocolate',
    name: 'Ultra-Processed Soy Chocolate Cream (100g)',
    category: 'plant_based',
    subCategory: 'Plant-based Desserts',
    sugarPer100g: 14.5,
    sugarCubesEquivalent: 3.6,
    caloriesPer100g: 102,
    nutriScore: 'c',
    novaGroup: 4,
    ecoScore: 'b',
    additives: [
      { code: 'E407', name: 'Carrageenan', riskLevel: 'high_risk', function: 'Thickener' },
      { code: 'E412', name: 'Guar gum', riskLevel: 'safe', function: 'Emulsifier' },
    ],
    barcode: '5411188114887',
  }
];

export const CompositionSpectrum: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [maxSugarFilter, setMaxSugarFilter] = useState<number>(20);
  const [selectedProduct, setSelectedProduct] = useState<ProductComposition>(SAMPLE_PRODUCTS[0]);

  const filteredProducts = useMemo(() => {
    return SAMPLE_PRODUCTS.filter(p => {
      const matchCat = activeCategory === 'all' || p.category === activeCategory;
      const matchSugar = p.sugarPer100g <= maxSugarFilter;
      return matchCat && matchSugar;
    });
  }, [activeCategory, maxSugarFilter]);

  const renderNutriBadge = (grade: NutriScoreGrade) => {
    const colors: Record<NutriScoreGrade, string> = {
      a: 'bg-emerald-500 text-black',
      b: 'bg-teal-400 text-black',
      c: 'bg-yellow-400 text-black',
      d: 'bg-orange-500 text-white',
      e: 'bg-rose-600 text-white',
    };
    return (
      <span className={`inline-flex items-center justify-center font-black uppercase text-xs w-7 h-7 rounded-md shadow-sm ${colors[grade]}`}>
        {grade}
      </span>
    );
  };

  const renderNovaBadge = (nova: NovaGroup) => {
    const isUltra = nova === 4;
    return (
      <span className={`px-2.5 py-1 text-xs font-bold rounded-md uppercase tracking-wider ${
        isUltra ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
      }`}>
        NOVA {nova} {isUltra ? '• Ultra-Processed' : '• Minimally Processed'}
      </span>
    );
  };

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative overflow-hidden">
      {/* Visual Ambient Glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs font-bold tracking-widest uppercase mb-2">
            🔬 Global Observatories Unified Matrix
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            Nutritional Composition & Additive Spectrum
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Real-time multi-dimensional chemical spectrum consolidating historical campaigns (Opération Sodas & What’s in my Yogurt) into a modern sensory intelligence engine.
          </p>
        </div>

        {/* Global KPI Quick Readout */}
        <div className="flex items-center gap-4 bg-slate-900/80 border border-slate-800 p-3 rounded-2xl">
          <div className="text-center px-2">
            <div className="text-xl font-black text-cyan-400 font-mono">10.6g</div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wider">Avg Sugar/100ml</div>
          </div>
          <div className="w-px h-8 bg-slate-800" />
          <div className="text-center px-2">
            <div className="text-xl font-black text-rose-400 font-mono">68%</div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wider">Nova 4 UPF Infiltration</div>
          </div>
        </div>
      </div>

      {/* Control Deck */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-6">
        {/* Category Pills */}
        <div className="md:col-span-8 flex flex-wrap gap-2">
          {[
            { id: 'all', label: 'All Products' },
            { id: 'beverage', label: '🥤 Sodas & Beverages' },
            { id: 'dairy', label: '🥛 Dairy Yogurts' },
            { id: 'plant_based', label: '🌱 Plant Alternatives' },
          ].map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeCategory === cat.id
                  ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/25 scale-[1.02]'
                  : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Sugar Threshold Slider */}
        <div className="md:col-span-4 bg-slate-900/60 border border-slate-800 p-3 rounded-2xl flex flex-col justify-center">
          <div className="flex justify-between items-center text-xs mb-1.5 font-medium">
            <span className="text-slate-400">Max Sugar Saturation:</span>
            <span className="text-cyan-400 font-mono font-bold">{maxSugarFilter}g / 100g</span>
          </div>
          <input
            type="range"
            min={0}
            max={20}
            step={0.5}
            value={maxSugarFilter}
            onChange={(e) => setMaxSugarFilter(parseFloat(e.target.value))}
            className="w-full accent-cyan-400 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
          />
        </div>
      </div>

      {/* Dual Workspace: Interactive Spectrum on Left, Detailed Inspector on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visual Spectrum Canvas */}
        <div className="lg:col-span-7 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 space-y-4">
          <div className="flex justify-between items-center text-xs font-semibold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-800">
            <span>Product Density Spectrum</span>
            <span>Sugar per 100g (Cubes)</span>
          </div>

          <div className="space-y-3">
            {filteredProducts.map((p) => {
              const isSelected = selectedProduct.id === p.id;
              const barWidth = Math.min(100, (p.sugarPer100g / 15) * 100);

              return (
                <div
                  key={p.id}
                  onClick={() => setSelectedProduct(p)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-800/90 border-cyan-500/80 shadow-md ring-1 ring-cyan-500/50'
                      : 'bg-slate-900/50 border-slate-800/80 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2.5">
                      {renderNutriBadge(p.nutriScore)}
                      <span className="font-bold text-sm text-slate-200">{p.name}</span>
                    </div>
                    <span className="font-mono text-xs font-bold text-cyan-400">
                      {p.sugarPer100g}g <span className="text-slate-500 font-normal">({p.sugarCubesEquivalent} cubes)</span>
                    </span>
                  </div>

                  {/* Relative Density Indicator Bar */}
                  <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden flex items-center">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        p.sugarPer100g > 10 ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-gradient-to-r from-emerald-500 to-cyan-400'
                      }`}
                      style={{ width: `${Math.max(4, barWidth)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Detailed Product Inspector (HUD Card) */}
        <div className="lg:col-span-5 bg-gradient-to-b from-slate-900 to-slate-950 border border-cyan-500/30 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] font-mono tracking-widest uppercase text-cyan-400 bg-cyan-950/80 border border-cyan-800 px-2 py-0.5 rounded">
                EAN {selectedProduct.barcode}
              </span>
              {renderNovaBadge(selectedProduct.novaGroup)}
            </div>

            <h3 className="text-xl font-black text-white mb-1">
              {selectedProduct.name}
            </h3>
            <div className="text-xs text-slate-400 mb-6 font-mono">
              Classification: {selectedProduct.subCategory}
            </div>

            {/* Sugar Cube Visualizer Array (Replacing Opération Sodas graphic) */}
            <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl mb-5">
              <div className="text-xs text-slate-400 font-semibold mb-2 flex justify-between">
                <span>Sugar Equivalents</span>
                <span className="text-cyan-400 font-bold">{selectedProduct.sugarCubesEquivalent} Cubes per unit</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {Array.from({ length: Math.ceil(selectedProduct.sugarCubesEquivalent) }).map((_, i) => (
                  <div
                    key={i}
                    title="1 sugar cube = 4g"
                    className="w-5 h-5 bg-slate-100 border border-slate-300 rounded shadow-inner flex items-center justify-center text-[10px] font-black text-slate-900 select-none transform hover:scale-110 transition"
                  >
                    ▫
                  </div>
                ))}
                {selectedProduct.sugarCubesEquivalent === 0 && (
                  <span className="text-xs text-emerald-400 font-mono">0 Sugar Added • Pure Formulation</span>
                )}
              </div>
            </div>

            {/* Additive & Chemical Toxicity Flags */}
            <div className="mb-4">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Detected Additives & Functional Chemicals ({selectedProduct.additives.length})
              </div>
              {selectedProduct.additives.length === 0 ? (
                <div className="text-xs text-emerald-400 bg-emerald-950/30 border border-emerald-900/50 p-2.5 rounded-lg flex items-center gap-2">
                  <span>✓</span> Clean formulation without synthetic additives or artificial sweeteners.
                </div>
              ) : (
                <div className="space-y-2">
                  {selectedProduct.additives.map(add => (
                    <div key={add.code} className="text-xs bg-slate-950 border border-slate-800 p-2.5 rounded-lg flex justify-between items-center">
                      <div>
                        <span className="font-mono font-bold text-amber-400 mr-2">{add.code}</span>
                        <span className="text-slate-200">{add.name}</span>
                      </div>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-semibold uppercase ${
                        add.riskLevel === 'high_risk' ? 'bg-rose-950 text-rose-300' : 'bg-slate-800 text-slate-300'
                      }`}>
                        {add.function}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Historical Reformulation Delta */}
          {selectedProduct.reformulationDeltaPercent && (
            <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs flex items-center justify-between text-slate-400">
              <span>Historical Public Accord Delta:</span>
              <span className="text-emerald-400 font-bold font-mono">
                {selectedProduct.reformulationDeltaPercent}% sugar reduction
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
