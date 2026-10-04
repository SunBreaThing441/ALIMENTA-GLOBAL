/**
 * ALIMENTA GLOBAL — Civic Field Observatories & Barcode Telemetry Hub
 * Replaces legacy static page: scan-parties.html
 * Features interactive in-browser barcode scanner simulator & real-time telemetry
 */

import React, { useState } from 'react';
import type { ScanPartyWorkshop } from '../types';

export const SAMPLE_WORKSHOPS: ScanPartyWorkshop[] = [
  {
    id: 'lyon-melting-coop-2024',
    title: 'La Melting Coop Citizen Scan Party',
    type: 'upcoming',
    status: 'upcoming',
    date: '16 November 2024',
    location: 'Lyon, France',
    city: 'Lyon',
    country: 'France',
    venue: 'La Melting Coop Store',
    organizer: 'Open Food Facts Rhone-Alpes',
    scanned_products_count: 850,
    attendees_count: 24,
  },
  {
    id: 'paris-academy-scan',
    title: 'UNESCO Youth Food Literacy Workshop',
    type: 'upcoming',
    status: 'upcoming',
    date: '05 December 2024',
    location: 'Paris, France',
    city: 'Paris',
    country: 'France',
    venue: 'Cité des Sciences et de l’Industrie',
    organizer: 'Alimenta Paris Node',
    scanned_products_count: 1200,
    attendees_count: 45,
  },
  {
    id: 'berlin-bio-hack',
    title: 'Berlin Sustainable Packaging Audit Party',
    type: 'past',
    status: 'completed',
    date: '12 September 2024',
    location: 'Berlin, Germany',
    city: 'Berlin',
    country: 'Germany',
    venue: 'Betahaus Kreuzberg',
    organizer: 'Open Food Facts Deutschland e.V.',
    scanned_products_count: 2430,
    attendees_count: 62,
  },
  {
    id: 'madrid-eco-scan',
    title: 'Madrid Supermercado Colectivo Scanathon',
    type: 'past',
    status: 'completed',
    date: '28 June 2024',
    location: 'Madrid, Spain',
    city: 'Madrid',
    country: 'Spain',
    venue: 'La Osa Supermercado',
    organizer: 'Open Food Facts España',
    scanned_products_count: 1890,
    attendees_count: 38,
  }
];

export const TEST_BARCODES = [
  { barcode: '3017620422003', name: 'Hazelnut Cocoa Spread 400g', brand: 'Nutella', nutri: 'E', nova: 4, eco: 'D', packaging: 'Glass Jar + Plastic Lid' },
  { barcode: '5449000000996', name: 'Classic Cola Soda 330ml', brand: 'Coca-Cola', nutri: 'E', nova: 4, eco: 'D', packaging: 'Aluminum Can (100% Recyclable)' },
  { barcode: '7394376616037', name: 'Organic Oat Drink Barista 1L', brand: 'Oatly', nutri: 'B', nova: 1, eco: 'A', packaging: 'Tetra Brik FSC Certified' },
  { barcode: '3033490004523', name: 'Strawberry Dairy Yogurt 4x125g', brand: 'Danone', nutri: 'D', nova: 4, eco: 'B', packaging: 'Polystyrene Plastic Pot' },
  { barcode: '3274080005003', name: 'Natural Mineral Water 1.5L', brand: 'Cristaline', nutri: 'A', nova: 1, eco: 'B', packaging: '100% Recycled rPET' }
];

export const CivicObservatoryHub: React.FC = () => {
  const [activeBarcode, setActiveBarcode] = useState<string>(TEST_BARCODES[0].barcode);
  const [ingestionStatus, setIngestionStatus] = useState<'idle' | 'scanning' | 'verified'>('verified');
  const [inspectedProduct, setInspectedProduct] = useState(TEST_BARCODES[0]);

  const handleSimulateScan = (item: typeof TEST_BARCODES[0]) => {
    setActiveBarcode(item.barcode);
    setIngestionStatus('scanning');
    setTimeout(() => {
      setInspectedProduct(item);
      setIngestionStatus('verified');
    }, 400);
  };

  return (
    <section className="bg-slate-950 border border-slate-800/80 rounded-3xl p-6 lg:p-8 text-slate-100 shadow-2xl relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold tracking-widest uppercase mb-2">
            🛰️ Citizen Science & Telemetry Hub
          </div>
          <h2 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
            Civic Field Observatories & Barcode Scanner Simulator
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Empowering local communities and schools to crowdsource, audit, and verify the global food supply chain through collective scanning workshops.
          </p>
        </div>

        <button className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs uppercase tracking-wider hover:opacity-90 transition shadow-lg shadow-emerald-500/20">
          + Register Local Workshop
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Barcode Scanner & Real-Time Ingestion Simulator */}
        <div className="lg:col-span-6 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Live Barcode & OCR Optical Simulator
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                ingestionStatus === 'verified' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-amber-950 text-amber-300 animate-pulse'
              }`}>
                {ingestionStatus === 'verified' ? '● Commited to Commons' : '○ Analyzing Barcode...'}
              </span>
            </div>

            {/* Virtual Barcode Scanner Interface */}
            <div className="bg-slate-950 border-2 border-dashed border-slate-700/80 rounded-xl p-5 mb-5 text-center relative overflow-hidden group">
              <div className="absolute inset-0 bg-cyan-500/5 pointer-events-none" />
              <div className="w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse mb-3" />
              <div className="font-mono text-2xl tracking-[0.25em] font-black text-white select-all">
                {activeBarcode}
              </div>
              <div className="text-[11px] text-slate-500 mt-1 font-mono uppercase">
                GS1 EAN-13 Optical Sensor Feed
              </div>
            </div>

            {/* Quick Test Payloads */}
            <div className="mb-6">
              <div className="text-xs font-semibold text-slate-400 mb-2">
                Click a sample supermarket product to simulate live optical decoding:
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {TEST_BARCODES.map(item => (
                  <button
                    key={item.barcode}
                    onClick={() => handleSimulateScan(item)}
                    className={`text-left p-2.5 rounded-lg border text-xs transition-all ${
                      activeBarcode === item.barcode
                        ? 'bg-slate-800 border-cyan-400 text-white'
                        : 'bg-slate-950 border-slate-800/80 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="font-bold truncate">{item.name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{item.brand} • {item.barcode}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Telemetry Output HUD */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Identified Formulation:</span>
                <span className="text-white font-bold">{inspectedProduct.name}</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Packaging Ecological Audit:</span>
                <span className="text-teal-400 font-medium">{inspectedProduct.packaging}</span>
              </div>
              <div className="flex items-center gap-3 pt-2 border-t border-slate-800/80">
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] text-slate-500 uppercase">Nutri:</span>
                  <span className="font-black text-xs px-2 py-0.5 rounded bg-orange-500 text-white font-mono">
                    {inspectedProduct.nutri}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] text-slate-500 uppercase">NOVA:</span>
                  <span className="font-black text-xs px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono">
                    Group {inspectedProduct.nova}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] text-slate-500 uppercase">Eco:</span>
                  <span className="font-black text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                    Grade {inspectedProduct.eco}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Upcoming & Past Community Scan Parties */}
        <div className="lg:col-span-6 space-y-4">
          <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
            <span>Global Citizen Scan Workshops</span>
            <span>19 Verified Hubs</span>
          </div>

          <div className="space-y-3">
            {SAMPLE_WORKSHOPS.map(ws => (
              <div
                key={ws.id}
                className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 hover:border-slate-700 transition flex items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      ws.type === 'upcoming'
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {ws.date}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">{ws.location}</span>
                  </div>
                  <h4 className="font-bold text-sm text-white">{ws.title}</h4>
                  <div className="text-xs text-slate-500 mt-0.5">
                    Organized by: {ws.organizer}
                  </div>
                </div>

                <div className="text-right flex-shrink-0">
                  <div className="text-sm font-mono font-bold text-emerald-400">
                    {ws.scanned_products_count}
                  </div>
                  <div className="text-[10px] text-slate-500 uppercase">Barcodes Audited</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
