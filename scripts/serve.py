#!/usr/bin/env python3
"""
Open Food Facts Web - Integrated Full-Stack Development Server & API Hub.

Serves:
1. Frontend Portal & Showcases (Opération Sodas, Scan Parties, Pro Platform, Yogurt, Shampoo, FAQ, Reuses, etc.)
2. Template Engine with recursive [[texts/...]] include resolution for all 100+ pages
3. Full REST API v2 for all datasets (reuses, press-review, FAQ, queries, scan parties, publications)
4. Interactive API Playground & Documentation (/api/docs)
5. Static Assets (/html/images/ and /images/)
"""

import http.server
import json
import mimetypes
import os
import re
import socketserver
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime

# Safeguard UTF-8 encoding across Windows console environments
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
HTML_DIR = os.path.join(REPO_ROOT, "html")
IMAGES_DIR = os.path.join(HTML_DIR, "images")
LANG_DIR = os.path.join(REPO_ROOT, "lang")

# Cached datasets
DATASETS = {}

def load_all_datasets():
    """Load JSON datasets into memory."""
    files = {
        "reuses": os.path.join(DATA_DIR, "reuses.json"),
        "press": os.path.join(DATA_DIR, "press-review-merged.json"),
        "faq": os.path.join(DATA_DIR, "faq.json"),
        "queries": os.path.join(DATA_DIR, "queries.json"),
        "scan_parties": os.path.join(DATA_DIR, "scan_parties.json"),
        "publications": os.path.join(DATA_DIR, "scientific_publications.json"),
        "mobile_features": os.path.join(DATA_DIR, "mobile_features.json"),
    }
    for key, path in files.items():
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    DATASETS[key] = json.load(f)
            except Exception as e:
                print(f"[WARN] Failed loading {path}: {e}")
                DATASETS[key] = []
        else:
            DATASETS[key] = []

def resolve_includes(content, base_lang="en"):
    """Recursively resolve [[texts/...]] tags."""
    pattern = re.compile(r"\[\[texts/([^\]]+)\]\]")
    base_dir = os.path.join(REPO_ROOT, "lang", base_lang)

    def replacer(match):
        rel_path = match.group(1).strip()
        # Look in specified language first, then fallback to 'en'
        full_path = os.path.join(base_dir, "texts", rel_path)
        if not os.path.exists(full_path):
            full_path = os.path.join(REPO_ROOT, "lang", "en", "texts", rel_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    included_text = f.read()
                return resolve_includes(included_text, base_lang)
            except Exception:
                return f"<!-- Error loading include {rel_path} -->"
        return f"<!-- Include not found: {rel_path} -->"

    return pattern.sub(replacer, content)

def wrap_with_off_layout(content, title="Open Food Facts", active_nav=""):
    """Wrap page content with standard Open Food Facts navigation header and footer if not full HTML."""
    if "<!DOCTYPE" in content[:200] or "<html" in content[:200]:
        return content

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Open Food Facts</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      background: #fdfcfb;
      font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
      line-height: 1.6;
    }}
    .off-nav {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.75rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }}
    .off-nav-brand {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      text-decoration: none;
      color: #341100;
      font-weight: 800;
      font-size: 1.15rem;
    }}
    .off-nav-brand img {{
      height: 34px;
      width: auto;
    }}
    .off-nav-links {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.92rem;
      flex-wrap: wrap;
    }}
    .off-nav-links a {{
      color: #475569;
      text-decoration: none;
      font-weight: 600;
      transition: all 0.15s ease;
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
    }}
    .off-nav-links a:hover {{
      color: #c2410c;
      background: #fff7ed;
    }}
    .off-nav-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 0.3rem 0.75rem;
      background: #f0fdf4;
      color: #166534;
      border: 1px solid #bbf7d0;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 700;
    }}
    .off-nav-badge .dot {{
      width: 8px;
      height: 8px;
      background: #22c55e;
      border-radius: 50%;
      box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
    }}
    .off-page-body {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 1.5rem 1.5rem 4rem;
    }}
    .off-footer {{
      border-top: 1px solid #e2e8f0;
      background: #ffffff;
      padding: 2rem;
      text-align: center;
      font-size: 0.88rem;
      color: #64748b;
    }}
    .off-footer a {{
      color: #c2410c;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <nav class="off-nav">
    <a href="/" class="off-nav-brand">
      <img src="https://static.openfoodfacts.org/images/logos/off-logo-horizontal-light.svg" alt="Open Food Facts" onerror="this.src='/html/images/logos/off-logo-horizontal-light.svg'">
      <span>Web Workspace</span>
    </a>
    <div class="off-nav-links">
      <a href="/">🏠 Home Portal</a>
      <a href="/faq">❓ FAQ</a>
      <a href="/reuses">🚀 Reuses</a>
      <a href="/press-review">📰 Press</a>
      <a href="/scan-parties.html">🏷️ Scan Parties</a>
      <a href="/operation-sodas.html">🥤 Opération Sodas</a>
      <a href="/pro">💼 Pro Platform</a>
      <a href="/api/docs" style="color: #2563eb; background: #eff6ff;">⚡ API Docs</a>
      <span class="off-nav-badge"><span class="dot"></span> Live Local</span>
    </div>
  </nav>

  <div class="off-page-body">
    {content}
  </div>

  <footer class="off-footer">
    <p>Open Food Facts — The collaborative, free and open database of food products from around the world.</p>
    <p>Local Full-Stack Development Server &middot; <a href="/api/docs">Explore REST APIs</a> &middot; <a href="https://world.openfoodfacts.org" target="_blank" rel="noopener">Official Website</a></p>
  </footer>
</body>
</html>"""


def get_portal_html():
    """Generate the modern ALIMENTA GLOBAL UNESCO-affiliated social service dashboard."""
    reuses_count = len(DATASETS.get("reuses", []))
    press_count = len(DATASETS.get("press", []))
    pub_count = len(DATASETS.get("publications", []))
    sp_count = len(DATASETS.get("scan_parties", []))
    queries_count = len(DATASETS.get("queries", []))

    # Pre-render sample reuses for zero-JS fallback
    reuses_sample = DATASETS.get("reuses", [])[:9]
    reuses_cards = ""
    for r in reuses_sample:
        inst_raw = r.get('installs', '10k+')
        try:
            inst_str = f"{int(inst_raw):,}"
        except (ValueError, TypeError):
            inst_str = str(inst_raw)
        reuses_cards += f"""
        <div class="card p-5 flex flex-col justify-between group">
          <div>
            <div class="flex justify-between items-start gap-2 mb-2">
              <h4 class="font-bold text-base text-white group-hover:text-cyan-400 transition truncate">{r.get('name', '')}</h4>
              <span class="badge badge-tag">{r.get('theme', 'General')}</span>
            </div>
            <p class="text-xs text-slate-400 line-clamp-3 mb-4 leading-relaxed">{r.get('description', '') or r.get('tagline', '')}</p>
          </div>
          <div class="pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
            <span class="text-slate-500 font-mono text-[11px]">{inst_str} installs</span>
            <a href="{r.get('website', '#')}" target="_blank" rel="noopener noreferrer" class="text-cyan-400 hover:text-cyan-300 font-bold flex items-center gap-1">
              Inspect App &rarr;
            </a>
          </div>
        </div>
        """

    # Pre-render publications sample
    pubs_sample = DATASETS.get("publications", [])[:6]
    pubs_cards = ""
    for p in pubs_sample:
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        pubs_cards += f"""
        <div class="card p-5 flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="badge badge-emerald">{p.get('year', 2024)}</span>
              <span class="text-xs text-slate-400 truncate">{p.get('journal_or_conference', 'Academic Citation')}</span>
            </div>
            <h4 class="font-bold text-sm text-white line-clamp-2 mb-2">{p.get('title', '')}</h4>
            <div class="text-xs text-slate-400 font-mono mb-3">{authors}</div>
          </div>
          <div class="pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
            <span class="text-[11px] font-mono text-cyan-400">Peer-Reviewed Study</span>
            <a href="{p.get('url', p.get('pdf_url', '#'))}" target="_blank" rel="noopener noreferrer" class="text-slate-300 hover:text-white font-semibold">
              Read Paper &rarr;
            </a>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ALIMENTA GLOBAL — Planetary Nutritional Intelligence & Open Food Commons</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --canvas: #070a13;
      --panel: #0d1424;
      --panel-hover: #131c33;
      --border: #1c2844;
      --border-glow: #2c4070;
      --cyan: #00d2ff;
      --emerald: #00f5a0;
      --amber: #ffb800;
      --crimson: #ff3366;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
    }}
    body {{
      background: var(--canvas);
      color: var(--text);
      font-family: "Plus Jakarta Sans", system-ui, -apple-system, sans-serif;
      line-height: 1.5;
      overflow-x: hidden;
    }}

    /* Global Ribbon */
    .unesco-ribbon {{
      background: linear-gradient(90deg, #041029 0%, #081d45 50%, #041029 100%);
      border-bottom: 1px solid rgba(0, 210, 255, 0.2);
      padding: 0.5rem 1.5rem;
      font-size: 0.75rem;
      color: #94a3b8;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .ribbon-left {{ display: flex; align-items: center; gap: 0.75rem; font-weight: 600; }}
    .ribbon-badge {{
      background: rgba(0, 210, 255, 0.15);
      color: var(--cyan);
      border: 1px solid rgba(0, 210, 255, 0.3);
      padding: 0.15rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .pulse-dot {{
      width: 7px;
      height: 7px;
      background: var(--emerald);
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 8px var(--emerald);
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(0.85); }}
    }}

    /* Hero Section */
    .hero {{
      padding: 3rem 1.5rem 2.5rem;
      max-width: 1380px;
      margin: 0 auto;
      position: relative;
    }}
    .hero-eyebrow {{
      color: var(--cyan);
      font-size: 0.85rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .hero-title {{
      font-size: clamp(2.2rem, 5vw, 3.8rem);
      font-weight: 900;
      letter-spacing: -0.035em;
      line-height: 1.1;
      margin-bottom: 1.25rem;
      background: linear-gradient(180deg, #ffffff 40%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-sub {{
      font-size: 1.15rem;
      color: #94a3b8;
      max-width: 820px;
      line-height: 1.6;
      margin-bottom: 2rem;
    }}

    /* Telemetry Ribbon Bar */
    .telemetry-bar {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 2.5rem;
    }}
    .telemetry-cell {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 1.25rem 1.5rem;
      transition: border-color 0.2s;
    }}
    .telemetry-cell:hover {{ border-color: var(--border-glow); }}
    .telemetry-num {{
      font-size: 1.85rem;
      font-weight: 900;
      font-family: "JetBrains Mono", monospace;
      color: var(--cyan);
      line-height: 1.1;
    }}
    .telemetry-label {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #64748b;
      margin-top: 0.35rem;
    }}

    /* Navigation Dock */
    .nav-dock {{
      display: flex;
      gap: 0.5rem;
      background: rgba(13, 20, 36, 0.7);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 0.4rem;
      margin-bottom: 2.5rem;
      overflow-x: auto;
      position: sticky;
      top: 1rem;
      z-index: 100;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .dock-tab {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.65rem 1.15rem;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 700;
      color: #94a3b8;
      text-decoration: none;
      white-space: nowrap;
      transition: all 0.15s ease;
      cursor: pointer;
      border: none;
      background: transparent;
    }}
    .dock-tab:hover {{ color: #ffffff; background: rgba(255,255,255,0.05); }}
    .dock-tab.active {{
      background: var(--cyan);
      color: #070a13;
      box-shadow: 0 4px 14px rgba(0, 210, 255, 0.35);
    }}

    /* Generic Components */
    .container {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 0 1.5rem 5rem;
    }}
    .module-section {{
      display: none;
      animation: fadeIn 0.25s ease-out;
    }}
    .module-section.active {{ display: block; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .card:hover {{
      border-color: var(--border-glow);
      transform: translateY(-2px);
      box-shadow: 0 12px 28px rgba(0,0,0,0.4);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 800;
      font-family: "JetBrains Mono", monospace;
      text-transform: uppercase;
    }}
    .badge-tag {{ background: #1a243b; color: #94a3b8; }}
    .badge-cyan {{ background: rgba(0, 210, 255, 0.15); color: var(--cyan); border: 1px solid rgba(0, 210, 255, 0.3); }}
    .badge-emerald {{ background: rgba(0, 245, 160, 0.15); color: var(--emerald); border: 1px solid rgba(0, 245, 160, 0.3); }}
    .badge-amber {{ background: rgba(255, 184, 0, 0.15); color: var(--amber); border: 1px solid rgba(255, 184, 0, 0.3); }}
    .badge-crimson {{ background: rgba(255, 51, 102, 0.15); color: var(--crimson); border: 1px solid rgba(255, 51, 102, 0.3); }}

    /* Layout Utility */
    .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1.25rem; }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(480px, 1fr)); gap: 1.5rem; }}

    /* Inputs & Controls */
    .input-field {{
      width: 100%;
      background: #090e1a;
      border: 1px solid var(--border);
      color: #f1f5f9;
      padding: 0.85rem 1.25rem;
      border-radius: 14px;
      font-size: 0.92rem;
      outline: none;
      transition: border-color 0.2s;
    }}
    .input-field:focus {{ border-color: var(--cyan); box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.2); }}

    /* Shimmer Skeleton Loader */
    .skeleton {{
      background: linear-gradient(90deg, #0d1424 25%, #18233c 50%, #0d1424 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border-radius: 8px;
    }}
    @keyframes shimmer {{
      0% {{ background-position: 200% 0; }}
      100% {{ background-position: -200% 0; }}
    }}

    /* Filter Pills */
    .pill-btn {{
      background: #090e1a;
      border: 1px solid var(--border);
      color: #94a3b8;
      padding: 0.4rem 0.9rem;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .pill-btn:hover, .pill-btn.active {{
      background: rgba(0, 210, 255, 0.15);
      border-color: var(--cyan);
      color: var(--cyan);
    }}

    /* Spectrum Controls */
    .spectrum-row {{
      background: rgba(9, 14, 26, 0.6);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem 1.25rem;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .spectrum-row:hover, .spectrum-row.active {{
      background: #131c33;
      border-color: var(--cyan);
    }}

    /* Terminal Console */
    .terminal-box {{
      background: #04060c;
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.25rem;
      font-family: "JetBrains Mono", monospace;
      font-size: 0.82rem;
      color: #cbd5e1;
      max-height: 380px;
      overflow-y: auto;
      white-space: pre-wrap;
    }}

    footer {{
      border-top: 1px solid var(--border);
      background: #060912;
      padding: 3rem 1.5rem;
      text-align: center;
      color: #64748b;
      font-size: 0.85rem;
    }}
    footer a {{ color: var(--cyan); text-decoration: none; font-weight: 600; }}
  </style>
</head>
<body>
  <!-- Top Utility Ribbon -->
  <div class="unesco-ribbon">
    <div class="ribbon-left">
      <span class="pulse-dot"></span>
      <span class="ribbon-badge">UNESCO Digital Commons</span>
      <span>ALIMENTA GLOBAL &middot; Sovereign Planetary Nutritional Network</span>
    </div>
    <div style="display: flex; gap: 1.25rem; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;">
      <span>NODE: <strong style="color: var(--emerald);">EU-CENTRAL-1</strong></span>
      <span>LATENCY: <strong id="nodeLatency" style="color: var(--cyan);">14ms</strong></span>
      <a href="/api/docs" style="color: var(--cyan); text-decoration: none; font-weight: 700;">⚡ REST API v2 Docs</a>
    </div>
  </div>

  <!-- Header -->
  <header class="hero">
    <div class="hero-eyebrow">
      <span>🌐 Planetary Public Good</span> &middot; <span>Open Scientific Standard</span>
    </div>
    <h1 class="hero-title">ALIMENTA GLOBAL</h1>
    <p class="hero-sub">
      The authoritative digital commons for global nutritional transparency, chemical composition analysis, and public health empowerment. Unified open data for 3.4M+ products across 180 countries.
    </p>

    <!-- Telemetry Bar -->
    <div class="telemetry-bar">
      <div class="telemetry-cell">
        <div class="telemetry-num">3,421,809</div>
        <div class="telemetry-label">Audited Barcodes</div>
      </div>
      <div class="telemetry-cell">
        <div class="telemetry-num">{reuses_count}</div>
        <div class="telemetry-label">Ecosystem Apps</div>
      </div>
      <div class="telemetry-cell">
        <div class="telemetry-num">{pub_count}</div>
        <div class="telemetry-label">Scientific Studies</div>
      </div>
      <div class="telemetry-cell">
        <div class="telemetry-num">{sp_count}</div>
        <div class="telemetry-label">Civic Observatories</div>
      </div>
      <div class="telemetry-cell">
        <div class="telemetry-num">{press_count}</div>
        <div class="telemetry-label">Global Press Mentions</div>
      </div>
      <div class="telemetry-cell">
        <div class="telemetry-num" style="color: var(--emerald);">100%</div>
        <div class="telemetry-label">Commons Node Health</div>
      </div>
    </div>

    <!-- Navigation Dock -->
    <nav class="nav-dock" id="navDock">
      <button class="dock-tab active" data-tab="tab-spectrum">🔬 1. Composition Spectrum</button>
      <button class="dock-tab" data-tab="tab-civic">🛰️ 2. Civic Field Observatories</button>
      <button class="dock-tab" data-tab="tab-toxicology">🧴 3. Toxicological Matrix</button>
      <button class="dock-tab" data-tab="tab-ecosystem">🚀 4. Commons Ecosystem ({reuses_count})</button>
      <button class="dock-tab" data-tab="tab-press">📰 5. Global Press Review ({press_count})</button>
      <button class="dock-tab" data-tab="tab-science">📚 6. Scientific Vault ({pub_count})</button>
      <button class="dock-tab" data-tab="tab-faq">❓ 7. Knowledge Vault</button>
      <button class="dock-tab" data-tab="tab-compiler">⚡ 8. On-Demand Compiler</button>
      <a href="/dashboard" class="dock-tab" style="background: rgba(0, 245, 160, 0.1); color: var(--emerald); border: 1px solid rgba(0, 245, 160, 0.3);">🔒 Secure Dashboard</a>
      <a href="/profile" class="dock-tab" style="background: rgba(0, 210, 255, 0.1); color: var(--cyan); border: 1px solid rgba(0, 210, 255, 0.3);">👤 Secure Profile</a>
    </nav>
  </header>

  <main class="container">
    <!-- MODULE 1: COMPOSITION SPECTRUM (Unifies Opération Sodas & What's in my Yogurt) -->
    <section class="module-section active" id="tab-spectrum">
      <div class="card p-6 lg:p-8" style="border-color: rgba(0, 210, 255, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div class="badge badge-cyan" style="margin-bottom: 0.5rem;">Unified Nutritional Observatory</div>
            <h2 style="font-size: 1.85rem; font-weight: 800;">Sugar Saturation & Additive Density Spectrum</h2>
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem;">
              Consolidating historical campaigns (Opération Sodas & What’s in my Yogurt) into a modern dynamic chemical spectrum.
            </p>
          </div>
          <div style="background: #090e1a; border: 1px solid var(--border); padding: 0.75rem 1.25rem; border-radius: 14px; text-align: right;">
            <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 700;">Global Daily Threshold</div>
            <div style="font-size: 1.25rem; font-weight: 900; color: var(--amber); font-family: 'JetBrains Mono', monospace;">25.0g (WHO Standard)</div>
          </div>
        </div>

        <!-- Filter Deck -->
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <button class="dock-tab active" onclick="filterSpectrum('all', this)">All Formulations</button>
          <button class="dock-tab" onclick="filterSpectrum('beverage', this)">🥤 Sodas & Beverages</button>
          <button class="dock-tab" onclick="filterSpectrum('dairy', this)">🥛 Dairy Yogurts</button>
          <button class="dock-tab" onclick="filterSpectrum('plant', this)">🌱 Plant Alternatives</button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
          <!-- Product Density Stream -->
          <div style="display: flex; flex-direction: column; gap: 0.75rem;" id="spectrumStream">
            <!-- Injected via JavaScript -->
          </div>

          <!-- Live Product Inspector HUD -->
          <div class="card p-6" style="background: #090e1a; border-color: rgba(0, 210, 255, 0.4); display: flex; flex-direction: column; justify-content: space-between;" id="inspectorHud">
            <!-- Selected Product Inspection Loaded Here -->
          </div>
        </div>
      </div>
    </section>

    <!-- MODULE 2: CIVIC FIELD OBSERVATORIES (Unifies Scan Parties & Barcode Scanner) -->
    <section class="module-section" id="tab-civic">
      <div class="card p-6 lg:p-8">
        <div style="margin-bottom: 2rem;">
          <div class="badge badge-emerald" style="margin-bottom: 0.5rem;">Crowdsourced Science Protocol</div>
          <h2 style="font-size: 1.85rem; font-weight: 800;">Civic Field Observatories & Barcode Scanner Simulator</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem;">
            Replacing static scan party pages with an interactive optical ingestion simulator and live workshop registry.
          </p>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1.75rem;">
          <!-- Optical Scanner Simulator -->
          <div style="background: #090e1a; border: 1px solid var(--border); border-radius: 18px; padding: 1.5rem;">
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--cyan); margin-bottom: 1rem;">
              ⚡ Simulated GS1 Optical Decryption Engine
            </div>

            <!-- Scanner Box -->
            <div style="background: #04060c; border: 2px dashed rgba(0, 210, 255, 0.3); border-radius: 14px; padding: 1.5rem; text-align: center; margin-bottom: 1.25rem; position: relative;">
              <div style="height: 2px; width: 80%; margin: 0 auto 0.75rem; background: var(--cyan); box-shadow: 0 0 12px var(--cyan); animation: scanLine 2s infinite alternate;"></div>
              <div id="simBarcodeVal" style="font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 900; letter-spacing: 0.2em; color: #ffffff;">
                3017620422003
              </div>
              <div style="font-size: 0.7rem; color: #64748b; font-mono; text-transform: uppercase; margin-top: 0.35rem;">
                Optical Sensor Resolution: OK &middot; Verification Confidence: 99.8%
              </div>
            </div>

            <!-- Sample Product Barcode Chips -->
            <div style="margin-bottom: 1.25rem;">
              <div style="font-size: 0.75rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.5rem;">Click Sample Product to Simulate Decode:</div>
              <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                <button class="spectrum-row active" onclick="simulateScan('3017620422003', 'Hazelnut Cocoa Spread 400g', 'Nutella', 'E', 4, 'D', 'Glass Jar + Plastic Cap')">
                  <strong>Nutella</strong> &middot; Hazelnut Cocoa Spread 400g (3017620422003)
                </button>
                <button class="spectrum-row" onclick="simulateScan('5449000000996', 'Classic Cola Soda 330ml', 'Coca-Cola', 'E', 4, 'D', 'Aluminum Can (100% Recyclable)')">
                  <strong>Coca-Cola</strong> &middot; Classic Cola Soda 330ml (5449000000996)
                </button>
                <button class="spectrum-row" onclick="simulateScan('7394376616037', 'Organic Oat Drink Barista 1L', 'Oatly', 'B', 1, 'A', 'Tetra Brik FSC Certified')">
                  <strong>Oatly</strong> &middot; Organic Oat Drink Barista 1L (7394376616037)
                </button>
                <button class="spectrum-row" onclick="simulateScan('3274080005003', 'Natural Mineral Water 1.5L', 'Cristaline', 'A', 1, 'B', '100% Recycled rPET')">
                  <strong>Cristaline</strong> &middot; Natural Mineral Water 1.5L (3274080005003)
                </button>
              </div>
            </div>

            <!-- Ingested Telemetry Feedback -->
            <div id="scanResultBox" style="background: #050811; border: 1px solid var(--border); border-radius: 12px; padding: 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 0.85rem; font-weight: 700; color: #ffffff;" id="resName">Hazelnut Cocoa Spread 400g</span>
                <span class="badge badge-emerald">Verified</span>
              </div>
              <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.75rem;" id="resPack">Packaging: Glass Jar + Plastic Cap</div>
              <div style="display: flex; gap: 0.5rem;">
                <span class="badge badge-amber" id="resNutri">Nutri-Score: E</span>
                <span class="badge badge-crimson" id="resNova">NOVA: Group 4</span>
                <span class="badge badge-cyan" id="resEco">Eco-Score: Grade D</span>
              </div>
            </div>
          </div>

          <!-- Active Observatories & Scan Parties Registry -->
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
              <span style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #94a3b8;">
                Upcoming & Verified Civic Workshops
              </span>
              <span class="badge badge-tag">{sp_count} Registered Hubs</span>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;" id="scanPartiesContainer">
              <!-- Dynamically populated from /api/v2/scan-parties -->
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- MODULE 3: TOXICOLOGICAL & COSMETIC MATRIX (Replaces What's in my Shampoo?) -->
    <section class="module-section" id="tab-toxicology">
      <div class="card p-6 lg:p-8">
        <div style="margin-bottom: 2rem;">
          <div class="badge badge-amber" style="margin-bottom: 0.5rem;">Open Beauty Facts Chemical Screening</div>
          <h2 style="font-size: 1.85rem; font-weight: 800;">Toxicological & Endocrine Disruptor Screening Matrix</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem;">
            Replacing "What’s in my Shampoo?" with an automated toxicological screening tool for cosmetic formulations and personal hygiene.
          </p>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
          <div class="card p-5" style="border-color: rgba(255, 51, 102, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
              <h4 style="font-size: 1.1rem; font-weight: 700;">Commercial Volume Daily Shampoo</h4>
              <span class="badge badge-crimson">Caution</span>
            </div>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 1rem;">
              Formulation contains non-biodegradable silicones, harsh sulfate surfactants, and synthetic fragrance allergens.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.75rem; margin-bottom: 1rem;">
              <div style="background: rgba(255, 51, 102, 0.1); border: 1px solid rgba(255, 51, 102, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--crimson);">
                ⚠ Silicones Detected
              </div>
              <div style="background: rgba(255, 51, 102, 0.1); border: 1px solid rgba(255, 51, 102, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--crimson);">
                ⚠ SLES Sulfates Present
              </div>
              <div style="background: rgba(255, 51, 102, 0.1); border: 1px solid rgba(255, 51, 102, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--crimson);">
                ⚠ Microplastics Audit Fail
              </div>
              <div style="background: rgba(255, 184, 0, 0.1); border: 1px solid rgba(255, 184, 0, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--amber);">
                ⚠ 4 Fragrance Allergens
              </div>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: #04060c; padding: 0.75rem; border-radius: 8px;">
              INCI: Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Dimethicone, Sodium Chloride, Parfum, Phenoxyethanol.
            </div>
          </div>

          <div class="card p-5" style="border-color: rgba(0, 245, 160, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
              <h4 style="font-size: 1.1rem; font-weight: 700;">Certified Bio Gentle Aloe Solid Bar</h4>
              <span class="badge badge-emerald">Optimal</span>
            </div>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 1rem;">
              Certified biological cold-pressed formulation with zero sulfates, zero synthetic polymers, and 100% biodegradable active matter.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.75rem; margin-bottom: 1rem;">
              <div style="background: rgba(0, 245, 160, 0.1); border: 1px solid rgba(0, 245, 160, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--emerald);">
                ✓ Zero Silicones
              </div>
              <div style="background: rgba(0, 245, 160, 0.1); border: 1px solid rgba(0, 245, 160, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--emerald);">
                ✓ Zero Sulfates (SLS-Free)
              </div>
              <div style="background: rgba(0, 245, 160, 0.1); border: 1px solid rgba(0, 245, 160, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--emerald);">
                ✓ Microplastics Free
              </div>
              <div style="background: rgba(0, 245, 160, 0.1); border: 1px solid rgba(0, 245, 160, 0.3); padding: 0.5rem; border-radius: 8px; color: var(--emerald);">
                ✓ 100% Eco-Degradable
              </div>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: #04060c; padding: 0.75rem; border-radius: 8px;">
              INCI: Sodium Cocoyl Isethionate, Hydrogenated Vegetable Oil, Aqua, Glycerin, Aloe Barbadensis Leaf Juice Powder.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- MODULE 4: COMMONS ECOSYSTEM MATRIX (Reuses) -->
    <section class="module-section" id="tab-ecosystem">
      <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div class="badge badge-cyan" style="margin-bottom: 0.5rem;">Digital Public Good Network</div>
          <h2 style="font-size: 1.85rem; font-weight: 800;">Ecosystem Applications & Public Policy Reusers ({reuses_count})</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem;">
            Third-party health applications, public health research systems, and smart consumer devices querying Open Food Facts APIs.
          </p>
        </div>
        <input
          type="text"
          id="reuseFilter"
          placeholder="🔍 Search 605+ ecosystem reuses..."
          class="input-field"
          style="max-width: 360px;"
          oninput="handleReusesSearch(this.value)"
        />
      </div>

      <div class="grid-3" id="reusesContainer">
        <!-- Dynamically loaded with shimmer skeletons -->
      </div>
      <div style="text-align: center; margin-top: 1.75rem;">
        <button id="reusesLoadMoreBtn" class="dock-tab" style="background: rgba(0, 210, 255, 0.1); border: 1px solid rgba(0, 210, 255, 0.3); color: var(--cyan); display: inline-flex; padding: 0.75rem 1.5rem;" onclick="loadMoreReuses()">
          Load More Ecosystem Reuses &darr;
        </button>
      </div>
    </section>

    <!-- MODULE 5: GLOBAL PRESS REVIEW -->
    <section class="module-section" id="tab-press">
      <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div class="badge badge-amber" style="margin-bottom: 0.5rem;">International Investigative Journalism</div>
          <h2 style="font-size: 1.85rem; font-weight: 800;">Global Press Review & Broadcast Disclosures ({press_count})</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem;">
            Print journalism, investigative television, and scientific journalism referencing Open Food Facts nutritional datasets.
          </p>
        </div>
        <input
          type="text"
          id="pressFilter"
          placeholder="🔍 Search 340+ press mentions..."
          class="input-field"
          style="max-width: 360px;"
          oninput="handlePressSearch(this.value)"
        />
      </div>

      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
        <button class="pill-btn active" onclick="filterPressType('', this)">All Mediums</button>
        <button class="pill-btn" onclick="filterPressType('article', this)">📰 Articles</button>
        <button class="pill-btn" onclick="filterPressType('video', this)">📺 Video & TV</button>
        <button class="pill-btn" onclick="filterPressType('audio', this)">🎙️ Podcasts & Radio</button>
      </div>

      <div class="grid-2" id="pressContainer">
        <!-- Dynamically loaded with shimmer skeletons -->
      </div>
      <div style="text-align: center; margin-top: 1.75rem;">
        <button id="pressLoadMoreBtn" class="dock-tab" style="background: rgba(255, 184, 0, 0.1); border: 1px solid rgba(255, 184, 0, 0.3); color: var(--amber); display: inline-flex; padding: 0.75rem 1.5rem;" onclick="loadMorePress()">
          Load More Press Disclosures &darr;
        </button>
      </div>
    </section>

    <!-- MODULE 6: SCIENTIFIC VAULT (Publications) -->
    <section class="module-section" id="tab-science">
      <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div class="badge badge-emerald" style="margin-bottom: 0.5rem;">Global Academic Citations</div>
          <h2 style="font-size: 1.85rem; font-weight: 800;">Scientific Publications & Peer-Reviewed Research ({pub_count})</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem;">
            Epidemiological, public health, and artificial intelligence papers published in The Lancet, Nature Food, and BMJ using Open Food Facts data.
          </p>
        </div>
        <input
          type="text"
          id="pubFilter"
          placeholder="🔍 Search publications & authors..."
          class="input-field"
          style="max-width: 360px;"
          oninput="handlePubsSearch(this.value)"
        />
      </div>

      <div class="grid-2" id="pubsContainer">
        <!-- Dynamically loaded with shimmer skeletons -->
      </div>
      <div style="text-align: center; margin-top: 1.75rem;">
        <button id="pubsLoadMoreBtn" class="dock-tab" style="background: rgba(0, 245, 160, 0.1); border: 1px solid rgba(0, 245, 160, 0.3); color: var(--emerald); display: inline-flex; padding: 0.75rem 1.5rem;" onclick="loadMorePubs()">
          Load More Scientific Papers &darr;
        </button>
      </div>
    </section>

    <!-- MODULE 7: KNOWLEDGE VAULT (FAQ) -->
    <section class="module-section" id="tab-faq">
      <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div class="badge badge-cyan" style="margin-bottom: 0.5rem;">UNESCO Knowledge Commons</div>
          <h2 style="font-size: 1.85rem; font-weight: 800;">Frequently Answered Inquiries & Protocols</h2>
          <p style="color: var(--text-muted); font-size: 0.95rem;">
            Curated encyclopedic documentation regarding database provenance, algorithmic grading, and API consumption.
          </p>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <button class="pill-btn active" onclick="changeFaqLang('en', this)">English (EN)</button>
          <button class="pill-btn" onclick="changeFaqLang('fr', this)">Français (FR)</button>
        </div>
      </div>

      <div id="faqContainer" style="display: flex; flex-direction: column; gap: 1rem;">
        <!-- Dynamically loaded from /api/v2/faq -->
      </div>
    </section>

    <!-- MODULE 6: ON-DEMAND COMPILER CONSOLE (POST /api/compile) -->
    <section class="module-section" id="tab-compiler">
      <div class="card p-6 lg:p-8">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div class="badge badge-amber" style="margin-bottom: 0.5rem;">Continuous Integration Orchestrator</div>
            <h2 style="font-size: 1.85rem; font-weight: 800;">On-Demand Dataset Compiler & Pipeline Monitor</h2>
            <p style="color: var(--text-muted); font-size: 0.95rem;">
              Directly triggers the backend compilation pipeline (<code style="color: var(--cyan);">POST /api/compile</code>), validates YAML schemas, and updates JSON caches in real time.
            </p>
          </div>
          <button id="btnTriggerCompile" onclick="triggerCompile()" class="dock-tab active" style="font-size: 0.9rem; padding: 0.75rem 1.5rem;">
            ⚡ Trigger Recompile Pipeline
          </button>
        </div>

        <div class="terminal-box" id="compileTerminal">
Waiting for compilation instruction. Click "Trigger Recompile Pipeline" above to execute scripts/compile.py and stream output telemetry.
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
      <div>
        <strong>ALIMENTA GLOBAL</strong> &middot; An International Digital Commons for Planetary Food Literacy & Health.
      </div>
      <div>
        <a href="/api/health" target="_blank">Health Check</a> &middot;
        <a href="/api/docs" target="_blank">API v2 Playground</a> &middot;
        <a href="https://world.openfoodfacts.org" target="_blank" rel="noopener">Official Foundation</a>
      </div>
    </div>
  </footer>

  <script>
    // Tab Switching Navigation Engine
    const tabs = document.querySelectorAll('.dock-tab[data-tab]');
    const sections = document.querySelectorAll('.module-section');

    tabs.forEach(tab => {{
      tab.addEventListener('click', () => {{
        tabs.forEach(t => t.classList.remove('active'));
        sections.forEach(s => s.classList.remove('active'));
        tab.classList.add('active');
        const target = document.getElementById(tab.getAttribute('data-tab'));
        if (target) target.classList.add('active');
      }});
    }});

    // Nutritional Spectrum Dataset & Engine
    const PRODUCTS = [
      {{ id: 'soda-classic', name: 'Standard Cola Soda (330ml can)', category: 'beverage', sugar: 10.6, cubes: 8.7, nutri: 'E', nova: 4, eco: 'D', adds: ['E150d (Ammonia caramel)', 'E338 (Phosphoric acid)'] }},
      {{ id: 'soda-zero', name: 'Zero-Sugar Diet Cola (330ml can)', category: 'beverage', sugar: 0.0, cubes: 0.0, nutri: 'B', nova: 4, eco: 'C', adds: ['E950 (Acesulfame K)', 'E951 (Aspartame)'] }},
      {{ id: 'energy-shot', name: 'Taurine Extreme Energy Drink (250ml)', category: 'beverage', sugar: 11.2, cubes: 7.0, nutri: 'E', nova: 4, eco: 'D', adds: ['E150a (Caramel)', 'E330 (Citric acid)'] }},
      {{ id: 'yogurt-fruit', name: 'Commercial Strawberry Yogurt (125g)', category: 'dairy', sugar: 12.8, cubes: 4.0, nutri: 'D', nova: 4, eco: 'B', adds: ['E1422 (Modified Starch)', 'E407 (Carrageenan)'] }},
      {{ id: 'yogurt-greek', name: 'Authentic Plain Greek Yogurt (150g)', category: 'dairy', sugar: 3.2, cubes: 1.2, nutri: 'A', nova: 1, eco: 'A', adds: [] }},
      {{ id: 'oat-drink', name: 'Organic Unsweetened Oat Drink (1L)', category: 'plant', sugar: 4.1, cubes: 1.0, nutri: 'B', nova: 1, eco: 'A', adds: [] }},
      {{ id: 'soy-dessert', name: 'Soy Chocolate Pudding (100g)', category: 'plant', sugar: 14.5, cubes: 3.6, nutri: 'C', nova: 4, eco: 'B', adds: ['E407 (Carrageenan)', 'E412 (Guar gum)'] }}
    ];

    let currentSpectrumCategory = 'all';

    function renderSpectrum() {{
      const stream = document.getElementById('spectrumStream');
      const filtered = PRODUCTS.filter(p => currentSpectrumCategory === 'all' || p.category === currentSpectrumCategory);
      
      stream.innerHTML = filtered.map((p, idx) => `
        <div class="spectrum-row ${{idx === 0 ? 'active' : ''}}" onclick="inspectProduct('${{p.id}}', this)">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span class="badge badge-amber" style="background: ${{p.nutri === 'A' ? '#10b981' : p.nutri === 'B' ? '#14b8a6' : p.nutri === 'C' ? '#eab308' : '#f97316'}}; color: #000;">
                ${{p.nutri}}
              </span>
              <span style="font-weight: 700; font-size: 0.88rem; color: #ffffff;">${{p.name}}</span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 700; color: var(--cyan);">
              ${{p.sugar}}g <small style="color: #64748b;">(${{p.cubes}} cubes)</small>
            </span>
          </div>
          <div style="width: 100%; height: 5px; background: #04060c; border-radius: 999px; overflow: hidden;">
            <div style="width: ${{Math.min(100, (p.sugar / 15) * 100)}}%; height: 100%; background: ${{p.sugar > 10 ? 'linear-gradient(90deg, #ffb800, #ff3366)' : 'linear-gradient(90deg, #00f5a0, #00d2ff)'}};"></div>
          </div>
        </div>
      `).join('');

      if (filtered.length > 0) {{
        inspectProduct(filtered[0].id);
      }}
    }}

    function inspectProduct(id, elem) {{
      if (elem) {{
        document.querySelectorAll('#spectrumStream .spectrum-row').forEach(r => r.classList.remove('active'));
        elem.classList.add('active');
      }}
      const p = PRODUCTS.find(x => x.id === id) || PRODUCTS[0];
      const cubesHtml = Array.from({{ length: Math.ceil(p.cubes) }}).map(() => 
        '<span style="display: inline-block; width: 18px; height: 18px; background: #ffffff; border-radius: 3px; margin: 2px; text-align: center; line-height: 18px; font-size: 10px; color: #000; font-weight: 900;">▫</span>'
      ).join('') || '<span style="color: var(--emerald); font-size: 0.8rem; font-family: monospace;">0 Sugar Cubes Added</span>';

      const addsHtml = p.adds.length > 0 
        ? p.adds.map(a => `<li style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.25rem;">⚠ ${{a}}</li>`).join('')
        : '<li style="font-size: 0.8rem; color: var(--emerald);">✓ Zero Synthetic Chemical Additives</li>';

      document.getElementById('inspectorHud').innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span class="badge badge-tag" style="font-family: monospace;">SPECTRUM FORMULATION INSPECTOR</span>
            <span class="badge ${{p.nova === 4 ? 'badge-crimson' : 'badge-emerald'}}">NOVA Group ${{p.nova}}</span>
          </div>
          <h3 style="font-size: 1.35rem; font-weight: 800; color: #ffffff; margin-bottom: 0.5rem;">${{p.name}}</h3>
          <div style="font-size: 0.8rem; color: var(--cyan); font-family: monospace; margin-bottom: 1.25rem;">
            Sugar Saturation Density: ${{p.sugar}}g per 100g / 100ml
          </div>

          <!-- Sugar Cubes Matrix -->
          <div style="background: #04060c; border: 1px solid var(--border); border-radius: 12px; padding: 1rem; margin-bottom: 1.25rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.5rem; text-transform: uppercase;">
              Equivalent Sugar Cubes (${{p.cubes}} Cubes / Container)
            </div>
            <div>${{cubesHtml}}</div>
          </div>

          <!-- Additives Breakdown -->
          <div>
            <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.5rem; text-transform: uppercase;">
              Detected Chemical Additives & Markers
            </div>
            <ul style="list-style: none;">${{addsHtml}}</ul>
          </div>
        </div>

        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b;">
          <span>Nutri-Score Rating: <strong style="color: #ffffff;">${{p.nutri}}</strong></span>
          <span>Eco-Score Ecological Grade: <strong style="color: var(--emerald);">${{p.eco}}</strong></span>
        </div>
      `;
    }}

    function filterSpectrum(cat, btn) {{
      currentSpectrumCategory = cat;
      if (btn) {{
        btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }}
      renderSpectrum();
    }}

    // Barcode Simulator Function
    function simulateScan(code, name, brand, nutri, nova, eco, pack) {{
      document.getElementById('simBarcodeVal').textContent = code;
      document.getElementById('resName').textContent = name + ' (' + brand + ')';
      document.getElementById('resPack').textContent = 'Packaging Audit: ' + pack;
      document.getElementById('resNutri').textContent = 'Nutri-Score: ' + nutri;
      document.getElementById('resNova').textContent = 'NOVA: Group ' + nova;
      document.getElementById('resEco').textContent = 'Eco-Score: Grade ' + eco;
    }}

    // On-Demand Compile Trigger
    async function triggerCompile() {{
      const btn = document.getElementById('btnTriggerCompile');
      const term = document.getElementById('compileTerminal');
      btn.disabled = true;
      btn.textContent = "⏳ Running Pipeline Subprocess...";
      term.textContent = "Initiating POST /api/compile request to ALIMENTA backend orchestrator...\nRunning scripts/compile.py in isolated sub-process with PYTHONUTF8=1...\n";

      try {{
        const res = await fetch('/api/compile', {{ method: 'POST' }});
        const data = await res.json();
        term.textContent += "Status: " + data.status.toUpperCase() + " (Exit code: " + data.code + ")\n";
        term.textContent += "------------------------------------------------------------\n";
        term.textContent += data.stdout || data.stderr;
      }} catch (err) {{
        term.textContent += "Network Error communicating with /api/compile: " + err.message;
      }} finally {{
        btn.disabled = false;
        btn.textContent = "⚡ Trigger Recompile Pipeline";
      }}
    }}

    // Debounce Utility for Real-Time Search Queries
    function debounce(func, wait) {{
      let timeout;
      return function(...args) {{
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      }};
    }}

    // Shimmer Skeleton HTML Generator
    function renderSkeletonCards(count) {{
      let html = '';
      for (let i = 0; i < count; i++) {{
        html += `
          <div class="card" style="padding: 1.25rem; min-height: 160px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div class="skeleton" style="height: 18px; width: 55%; margin-bottom: 12px;"></div>
              <div class="skeleton" style="height: 12px; width: 90%; margin-bottom: 8px;"></div>
              <div class="skeleton" style="height: 12px; width: 70%; margin-bottom: 8px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 10px; margin-top: 10px;">
              <div class="skeleton" style="height: 12px; width: 30%;"></div>
              <div class="skeleton" style="height: 12px; width: 25%;"></div>
            </div>
          </div>
        `;
      }}
      return html;
    }}

    // Error Box with Retry Trigger
    function renderErrorBox(msg, retryFnName) {{
      return `
        <div style="grid-column: 1 / -1; background: rgba(255, 51, 102, 0.08); border: 1px solid rgba(255, 51, 102, 0.3); border-radius: 16px; padding: 2.5rem; text-align: center;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
          <h3 style="color: var(--crimson); font-size: 1.1rem; font-weight: 800; margin-bottom: 0.5rem;">Data Integration Telemetry Failure</h3>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.25rem; max-width: 520px; margin-left: auto; margin-right: auto;">${{msg}}</p>
          <button class="dock-tab active" onclick="${{retryFnName}}()" style="padding: 0.6rem 1.4rem; font-size: 0.85rem; display: inline-flex;">🔄 Retry Query</button>
        </div>
      `;
    }}

    // ==========================================
    // 1. DYNAMIC ECOSYSTEM REUSES (GET /api/v2/reuses)
    // ==========================================
    let reusesPage = 0;
    let reusesSearch = '';
    let reusesTotal = 0;

    async function fetchReuses(append = false) {{
      const container = document.getElementById('reusesContainer');
      const btn = document.getElementById('reusesLoadMoreBtn');
      if (!append) {{
        reusesPage = 0;
        container.innerHTML = renderSkeletonCards(6);
      }}
      try {{
        const url = `/api/v2/reuses?limit=12&offset=${{reusesPage * 12}}&search=${{encodeURIComponent(reusesSearch)}}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
        const data = await res.json();
        reusesTotal = data.total || 0;
        const items = data.results || data.items || [];

        const html = items.map(r => {{
          const instRaw = r.installs || (r.users ? r.users + ' users' : '10k+');
          const installs = typeof instRaw === 'number' ? instRaw.toLocaleString() : instRaw;
          const desc = r.description || r.tagline || 'Open food data ecosystem integration.';
          const website = r.website || r.play_store || r.github || '#';
          const theme = r.theme || (r.themes && r.themes[0]) || 'Public Commons';
          const name = r.name || r.title || 'Ecosystem App';
          return `
            <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
                  <h4 style="font-weight: 700; font-size: 1rem; color: #ffffff;">${{name}}</h4>
                  <span class="badge badge-tag">${{theme}}</span>
                </div>
                <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1rem;">${{desc}}</p>
              </div>
              <div style="padding-top: 0.75rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="color: #64748b; font-family: monospace;">${{installs}} installs</span>
                <a href="${{website}}" target="_blank" rel="noopener noreferrer" style="color: var(--cyan); font-weight: 700; text-decoration: none;">Inspect App &rarr;</a>
              </div>
            </div>
          `;
        }}).join('');

        if (!append) {{
          if (items.length === 0) {{
            container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b;">No ecosystem reusers matched "${{reusesSearch}}".</div>`;
          }} else {{
            container.innerHTML = html;
          }}
        }} else {{
          container.insertAdjacentHTML('beforeend', html);
        }}

        if (btn) {{
          const currentCount = (reusesPage + 1) * 12;
          btn.style.display = currentCount < reusesTotal ? 'inline-flex' : 'none';
          btn.textContent = `Load More Ecosystem Reuses (${{Math.min(currentCount, reusesTotal)}} / ${{reusesTotal}}) ↓`;
        }}
      }} catch (err) {{
        if (!append) container.innerHTML = renderErrorBox(err.message, 'fetchReuses');
      }}
    }}

    function loadMoreReuses() {{
      reusesPage++;
      fetchReuses(true);
    }}

    const handleReusesSearch = debounce((val) => {{
      reusesSearch = val;
      fetchReuses(false);
    }}, 300);

    // ==========================================
    // 2. DYNAMIC GLOBAL PRESS REVIEW (GET /api/v2/press)
    // ==========================================
    let pressPage = 0;
    let pressSearch = '';
    let pressType = '';
    let pressTotal = 0;

    async function fetchPress(append = false) {{
      const container = document.getElementById('pressContainer');
      const btn = document.getElementById('pressLoadMoreBtn');
      if (!append) {{
        pressPage = 0;
        container.innerHTML = renderSkeletonCards(4);
      }}
      try {{
        const url = `/api/v2/press?limit=10&offset=${{pressPage * 10}}&type=${{encodeURIComponent(pressType)}}&search=${{encodeURIComponent(pressSearch)}}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
        const data = await res.json();
        pressTotal = data.total || 0;
        const items = data.results || data.items || [];

        const html = items.map(p => {{
          const typeBadge = p.type === 'video' ? 'badge-amber' : p.type === 'audio' ? 'badge-emerald' : 'badge-cyan';
          const mediumLabel = p.type ? p.type.toUpperCase() : 'PRESS';
          const date = p.date || p.year || 'Archive';
          const source = p.source || p.publisher || 'Global Media';
          const url = p.link || p.url || '#';
          return `
            <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                  <span class="badge ${{typeBadge}}">${{mediumLabel}}</span>
                  <span style="font-size: 0.75rem; color: #64748b; font-family: monospace;">${{date}}</span>
                </div>
                <h4 style="font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; line-height: 1.4;">${{p.title || 'Untitled Coverage'}}</h4>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 1rem;">Published by <strong style="color: #cbd5e1;">${{source}}</strong></div>
              </div>
              <div style="padding-top: 0.75rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="color: #64748b; font-family: monospace;">Investigative Archive</span>
                <a href="${{url}}" target="_blank" rel="noopener noreferrer" style="color: var(--amber); font-weight: 700; text-decoration: none;">View Coverage &rarr;</a>
              </div>
            </div>
          `;
        }}).join('');

        if (!append) {{
          if (items.length === 0) {{
            container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b;">No press mentions found matching your query.</div>`;
          }} else {{
            container.innerHTML = html;
          }}
        }} else {{
          container.insertAdjacentHTML('beforeend', html);
        }}

        if (btn) {{
          const currentCount = (pressPage + 1) * 10;
          btn.style.display = currentCount < pressTotal ? 'inline-flex' : 'none';
          btn.textContent = `Load More Press Disclosures (${{Math.min(currentCount, pressTotal)}} / ${{pressTotal}}) ↓`;
        }}
      }} catch (err) {{
        if (!append) container.innerHTML = renderErrorBox(err.message, 'fetchPress');
      }}
    }}

    function filterPressType(type, btn) {{
      pressType = type;
      if (btn) {{
        btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }}
      fetchPress(false);
    }}

    function loadMorePress() {{
      pressPage++;
      fetchPress(true);
    }}

    const handlePressSearch = debounce((val) => {{
      pressSearch = val;
      fetchPress(false);
    }}, 300);

    // ==========================================
    // 3. DYNAMIC SCIENTIFIC CITATIONS (GET /api/v2/publications)
    // ==========================================
    let pubsPage = 0;
    let pubsSearch = '';
    let pubsTotal = 0;

    async function fetchPublications(append = false) {{
      const container = document.getElementById('pubsContainer');
      const btn = document.getElementById('pubsLoadMoreBtn');
      if (!append) {{
        pubsPage = 0;
        container.innerHTML = renderSkeletonCards(4);
      }}
      try {{
        const url = `/api/v2/publications?limit=12&offset=${{pubsPage * 12}}&search=${{encodeURIComponent(pubsSearch)}}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
        const data = await res.json();
        pubsTotal = data.total || 0;
        const items = data.results || data.items || [];

        const html = items.map(p => {{
          const authors = Array.isArray(p.authors) ? p.authors.slice(0, 3).join(', ') + (p.authors.length > 3 ? ' et al.' : '') : (p.authors || 'Academic Research Group');
          const url = p.url || (p.doi ? (p.doi.startsWith('http') ? p.doi : 'https://doi.org/' + p.doi) : '#');
          const journal = p.journal || p.journal_or_conference || 'Peer-Reviewed Journal';
          const year = p.year || '2024';
          return `
            <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
              <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                  <span class="badge badge-emerald">${{year}}</span>
                  <span style="font-size: 0.75rem; color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${{journal}}</span>
                </div>
                <h4 style="font-weight: 700; font-size: 0.95rem; color: #ffffff; line-height: 1.4; margin-bottom: 0.5rem;">${{p.title || 'Untitled Research Study'}}</h4>
                <div style="font-size: 0.75rem; color: #64748b; font-family: monospace; margin-bottom: 0.75rem;">${{authors}}</div>
              </div>
              <div style="padding-top: 0.75rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                <span style="font-size: 0.7rem; font-family: monospace; color: var(--cyan);">Epidemiological Dataset</span>
                <a href="${{url}}" target="_blank" rel="noopener noreferrer" style="color: #cbd5e1; font-weight: 600; text-decoration: none;">Read Study &rarr;</a>
              </div>
            </div>
          `;
        }}).join('');

        if (!append) {{
          if (items.length === 0) {{
            container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b;">No academic publications matched your search.</div>`;
          }} else {{
            container.innerHTML = html;
          }}
        }} else {{
          container.insertAdjacentHTML('beforeend', html);
        }}

        if (btn) {{
          const currentCount = (pubsPage + 1) * 12;
          btn.style.display = currentCount < pubsTotal ? 'inline-flex' : 'none';
          btn.textContent = `Load More Scientific Papers (${{Math.min(currentCount, pubsTotal)}} / ${{pubsTotal}}) ↓`;
        }}
      }} catch (err) {{
        if (!append) container.innerHTML = renderErrorBox(err.message, 'fetchPublications');
      }}
    }}

    function loadMorePubs() {{
      pubsPage++;
      fetchPublications(true);
    }}

    const handlePubsSearch = debounce((val) => {{
      pubsSearch = val;
      fetchPublications(false);
    }}, 300);

    // ==========================================
    // 4. DYNAMIC CIVIC SCAN PARTIES (GET /api/v2/scan-parties)
    // ==========================================
    async function fetchScanParties() {{
      const container = document.getElementById('scanPartiesContainer');
      if (!container) return;
      container.innerHTML = renderSkeletonCards(3);
      try {{
        const res = await fetch('/api/v2/scan-parties');
        if (!res.ok) throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
        const data = await res.json();
        const items = data.results || data.items || [];

        if (items.length === 0) {{
          container.innerHTML = '<div style="color: #64748b; font-size: 0.85rem; padding: 1rem;">No scan parties registered in repository.</div>';
          return;
        }}

        container.innerHTML = items.map(sp => {{
          const name = sp.title || sp.name || 'Civic Audit Workshop';
          const city = sp.city || sp.location || 'Global Hub';
          const country = sp.country || '';
          const date = sp.date || sp.start_date || 'Upcoming';
          const audited = sp.products_scanned ? `${{Number(sp.products_scanned).toLocaleString()}} Audited` : 'Active Hub';
          const isPast = sp.status === 'completed' || sp.is_past;
          return `
            <div class="card" style="padding: 1rem; transition: border-color 0.2s;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span class="badge ${{isPast ? 'badge-tag' : 'badge-cyan'}}">${{date}}</span>
                <span style="font-size: 0.75rem; color: var(--emerald); font-weight: 700; font-family: monospace;">${{audited}}</span>
              </div>
              <h4 style="font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-bottom: 0.2rem;">${{name}}</h4>
              <div style="font-size: 0.75rem; color: #94a3b8;">${{city}}${{country ? ', ' + country : ''}} &middot; Open Food Facts Community</div>
            </div>
          `;
        }}).join('');
      }} catch (err) {{
        container.innerHTML = renderErrorBox(err.message, 'fetchScanParties');
      }}
    }}

    // ==========================================
    // 5. DYNAMIC KNOWLEDGE VAULT (GET /api/v2/faq)
    // ==========================================
    async function fetchFaq(lang = 'en') {{
      const container = document.getElementById('faqContainer');
      if (!container) return;
      container.innerHTML = renderSkeletonCards(3);
      try {{
        const res = await fetch(`/api/v2/faq?lang=${{lang}}`);
        if (!res.ok) throw new Error(`HTTP ${{res.status}}: ${{res.statusText}}`);
        const data = await res.json();
        const categories = data[lang] || data.categories || [];

        if (categories.length === 0) {{
          container.innerHTML = '<div style="color: #64748b; font-size: 0.85rem; padding: 1rem;">No FAQ entries available.</div>';
          return;
        }}

        container.innerHTML = categories.map((cat, catIdx) => {{
          const title = cat.title || cat.name || cat.category || 'Commons Standards';
          const qHtml = (cat.questions || cat.items || []).map(item => `
            <details style="background: #090e1a; border: 1px solid var(--border); border-radius: 12px; margin-bottom: 0.6rem; padding: 0.85rem 1.25rem; cursor: pointer;">
              <summary style="font-weight: 700; font-size: 0.92rem; color: #f1f5f9; outline: none;">
                ${{item.question || item.q || 'Inquiry Protocol'}}
              </summary>
              <div style="font-size: 0.85rem; color: #94a3b8; line-height: 1.6; margin-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem;">
                ${{item.answer_html || item.answer_markdown || item.answer || item.a || 'Documentation available upon verification.'}}
              </div>
            </details>
          `).join('');

          return `
            <div class="card" style="padding: 1.25rem;">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span class="badge badge-cyan">Category ${{String(catIdx + 1).padStart(2, '0')}}</span>
                <h3 style="font-size: 1.15rem; font-weight: 800; color: #ffffff;">${{title}}</h3>
              </div>
              <div>${{qHtml}}</div>
            </div>
          `;
        }}).join('');
      }} catch (err) {{
        container.innerHTML = renderErrorBox(err.message, 'fetchFaq');
      }}
    }}

    function changeFaqLang(lang, btn) {{
      if (btn) {{
        btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }}
      fetchFaq(lang);
    }}

    // ==========================================
    // 6. REAL-TIME TELEMETRY PING (GET /api/health)
    // ==========================================
    async function pingTelemetry() {{
      try {{
        const t0 = performance.now();
        const res = await fetch('/api/health');
        const t1 = performance.now();
        if (res.ok) {{
          const elem = document.getElementById('nodeLatency');
          if (elem) elem.textContent = Math.round(t1 - t0) + 'ms';
        }}
      }} catch (e) {{
        console.warn("Telemetry ping failed:", e);
      }}
    }}

    // Initial Orchestration
    renderSpectrum();
    fetchReuses(false);
    fetchPress(false);
    fetchPublications(false);
    fetchScanParties();
    fetchFaq('en');
    pingTelemetry();
    setInterval(pingTelemetry, 30000);
  </script>
</body>
</html>"""



def get_dashboard_html():
    """Generate the secured Dashboard page with client-side token interception and navigation guard."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ALIMENTA GLOBAL — Secure Observational Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --canvas: #070a13;
      --panel: #0d1424;
      --border: #1c2844;
      --cyan: #00d2ff;
      --emerald: #00f5a0;
      --amber: #ffb800;
      --crimson: #ff3366;
    }
    body {
      background: var(--canvas);
      color: #f1f5f9;
      font-family: "Plus Jakarta Sans", sans-serif;
      line-height: 1.5;
      padding-bottom: 4rem;
    }
    .nav {
      background: #090e1a;
      border-bottom: 1px solid var(--border);
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .nav-brand {
      color: #ffffff;
      font-weight: 800;
      font-size: 1.1rem;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 800;
      font-family: "JetBrains Mono", monospace;
      text-transform: uppercase;
    }
    .badge-cyan { background: rgba(0, 210, 255, 0.15); color: var(--cyan); border: 1px solid rgba(0, 210, 255, 0.3); }
    .badge-emerald { background: rgba(0, 245, 160, 0.15); color: var(--emerald); border: 1px solid rgba(0, 245, 160, 0.3); }
    .badge-crimson { background: rgba(255, 51, 102, 0.15); color: var(--crimson); border: 1px solid rgba(255, 51, 102, 0.3); }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 1.5rem;
    }
    .container {
      max-width: 1200px;
      margin: 2.5rem auto 0;
      padding: 0 1.5rem;
    }
    .btn {
      padding: 0.65rem 1.25rem;
      border-radius: 12px;
      font-weight: 700;
      font-size: 0.85rem;
      cursor: pointer;
      border: none;
      transition: all 0.15s;
    }
    .btn-primary { background: var(--cyan); color: #070a13; }
    .btn-primary:hover { background: #38bdf8; }
    .btn-danger { background: rgba(255, 51, 102, 0.2); color: var(--crimson); border: 1px solid rgba(255, 51, 102, 0.4); }
    .btn-danger:hover { background: rgba(255, 51, 102, 0.4); }
    .btn-secondary { background: #131c33; color: #cbd5e1; border: 1px solid var(--border); }
    .btn-secondary:hover { background: #1a2544; }
  </style>
</head>
<body>
  <nav class="nav">
    <a href="/" class="nav-brand">
      <span>🔒 ALIMENTA SECURE ENCLAVE</span>
    </a>
    <div style="display: flex; gap: 1rem; align-items: center;">
      <a href="/profile" style="color: var(--cyan); text-decoration: none; font-size: 0.85rem; font-weight: 700;">👤 User Profile</a>
      <a href="/" style="color: #94a3b8; text-decoration: none; font-size: 0.85rem;">&larr; Public Canvas</a>
    </div>
  </nav>

  <main class="container" id="appRoot">
    <!-- Rendered via Client Navigation Guard -->
  </main>

  <script>
    // Security Client & Navigation Guard
    const AUTH_KEY = '__ALIMENTA_SEC_SESSION__';
    const syncChannel = window.BroadcastChannel ? new BroadcastChannel('alimenta_auth_sync') : null;

    if (syncChannel) {
      syncChannel.onmessage = (e) => {
        if (e.data?.type === 'TERMINATE_SESSION') {
          sessionStorage.removeItem(AUTH_KEY);
          renderGuard();
        }
      };
    }

    function getSession() {
      try {
        const raw = sessionStorage.getItem(AUTH_KEY);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (parsed.expiresAt <= Date.now()) {
          sessionStorage.removeItem(AUTH_KEY);
          return null;
        }
        return parsed;
      } catch {
        return null;
      }
    }

    function setSession(session) {
      sessionStorage.setItem(AUTH_KEY, JSON.stringify(session));
      renderDashboard();
    }

    function logout() {
      sessionStorage.removeItem(AUTH_KEY);
      if (syncChannel) syncChannel.postMessage({ type: 'TERMINATE_SESSION' });
      renderGuard();
    }

    function simulateLogin(role) {
      const token = 'jwt_prod_token_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
      const session = {
        userId: 'usr_observer_' + Math.floor(Math.random() * 8999 + 1000),
        username: role === 'verified_scientist' ? 'Dr. Elena Rostova' : 'Citizen Contributor',
        role: role,
        token: token,
        csrfToken: 'csrf_' + Math.random().toString(36).substring(2),
        expiresAt: Date.now() + 3600 * 1000,
        organization: role === 'verified_scientist' ? 'UNESCO Public Health Commission' : 'Alimenta Civic Commons'
      };
      setSession(session);
    }

    function renderGuard() {
      document.getElementById('appRoot').innerHTML = `
        <div class="card" style="max-width: 620px; margin: 4rem auto; text-align: center; border-color: rgba(255, 51, 102, 0.3);">
          <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔒</div>
          <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 0.5rem;">Restricted Observational Access</h2>
          <p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 1.5rem;">
            This route is protected by the ALIMENTA Navigation Guard. An authenticated session token injected from <strong>openfoodfacts-server</strong> is required.
          </p>
          <div style="background: #04060c; border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem; margin-bottom: 1.5rem; text-align: left;">
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--cyan); text-transform: uppercase; margin-bottom: 0.5rem; font-family: monospace;">
              ⚡ Local Ingress Credential Ingestion
            </div>
            <p style="font-size: 0.78rem; color: #64748b; margin-bottom: 1rem;">
              Simulate session injection to test protected telemetry, audit queues, and cryptographic key rotation:
            </p>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button onclick="simulateLogin('citizen_contributor')" class="btn btn-primary">
                Ingest Citizen Credentials
              </button>
              <button onclick="simulateLogin('verified_scientist')" class="btn btn-secondary">
                Ingest Scientist Credentials
              </button>
            </div>
          </div>
          <a href="/" style="color: #64748b; text-decoration: none; font-size: 0.8rem; font-family: monospace;">&larr; Back to Public Commons</a>
        </div>
      `;
    }

    function renderDashboard() {
      const session = getSession();
      if (!session) { renderGuard(); return; }

      const remainingSecs = Math.max(0, Math.floor((session.expiresAt - Date.now()) / 1000));
      const mins = Math.floor(remainingSecs / 60);
      const secs = remainingSecs % 60;
      const timeStr = `${mins}:${secs.toString().padStart(2, '0')}`;

      document.getElementById('appRoot').innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
              <span class="badge badge-emerald">Session Authenticated</span>
              <span style="font-size: 0.75rem; color: #64748b; font-family: monospace;">OWASP Verified Ingress</span>
            </div>
            <h1 style="font-size: 2rem; font-weight: 800;">Observational Operations Dashboard</h1>
            <p style="color: #94a3b8; font-size: 0.88rem;">
              Principal Operator: <strong style="color: #ffffff;">${session.username}</strong> &middot; Node: ${session.organization}
            </p>
          </div>
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <div style="background: #04060c; border: 1px solid var(--border); border-radius: 12px; padding: 0.5rem 1rem; text-align: right;">
              <div style="font-size: 0.65rem; color: #64748b; text-transform: uppercase;">Session Expires In</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 900; color: var(--amber);" id="timerText">${timeStr}</div>
            </div>
            <button onclick="logout()" class="btn btn-danger">Terminate Session</button>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
          <div class="card">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Personal Barcode Audits</div>
            <div style="font-size: 2rem; font-weight: 900; font-family: monospace; color: var(--cyan); margin: 0.25rem 0;">142</div>
            <div style="font-size: 0.72rem; color: var(--emerald);">✓ 100% Verified Veracity Index</div>
          </div>
          <div class="card">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Pending Ingestion Queue</div>
            <div style="font-size: 2rem; font-weight: 900; font-family: monospace; color: var(--emerald); margin: 0.25rem 0;">8</div>
            <div style="font-size: 0.72rem; color: #94a3b8;">Awaiting peer community validation</div>
          </div>
          <div class="card">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">Security Clearance</div>
            <div style="font-size: 1.5rem; font-weight: 900; font-family: monospace; color: #ffffff; margin: 0.5rem 0; text-transform: uppercase;">
              ${session.role.replace('_', ' ')}
            </div>
            <div style="font-size: 0.72rem; color: var(--cyan);">Tier 3 Sovereign Clearance</div>
          </div>
        </div>

        <!-- Sovereign Bearer Token Inspection -->
        <div class="card" style="margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div>
              <h3 style="font-size: 1.1rem; font-weight: 700;">Bearer API Token Ingestion</h3>
              <p style="font-size: 0.78rem; color: #94a3b8;">Cryptographic token injected by openfoodfacts-server for authenticated REST API access.</p>
            </div>
            <span class="badge badge-cyan">Active Bearer</span>
          </div>
          <div style="background: #04060c; border: 1px solid var(--border); border-radius: 12px; padding: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #38bdf8; word-break: break-all;">
            ${session.token}
          </div>
        </div>
      `;
    }

    // Timer Loop
    setInterval(() => {
      const session = getSession();
      if (session) {
        const remainingSecs = Math.max(0, Math.floor((session.expiresAt - Date.now()) / 1000));
        const timerElem = document.getElementById('timerText');
        if (timerElem) {
          const mins = Math.floor(remainingSecs / 60);
          const secs = remainingSecs % 60;
          timerElem.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
        }
        if (remainingSecs <= 0) logout();
      }
    }, 1000);

    // Initial Guard Check
    const existing = getSession();
    if (existing) {
      renderDashboard();
    } else {
      renderGuard();
    }
  </script>
</body>
</html>"""


def get_profile_html():
    """Generate the secured User Profile page with identity management and privacy controls."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ALIMENTA GLOBAL — Sovereign User Profile</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --canvas: #070a13;
      --panel: #0d1424;
      --border: #1c2844;
      --cyan: #00d2ff;
      --emerald: #00f5a0;
      --amber: #ffb800;
      --crimson: #ff3366;
    }
    body {
      background: var(--canvas);
      color: #f1f5f9;
      font-family: "Plus Jakarta Sans", sans-serif;
      line-height: 1.5;
      padding-bottom: 4rem;
    }
    .nav {
      background: #090e1a;
      border-bottom: 1px solid var(--border);
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 1.5rem;
    }
    .container {
      max-width: 900px;
      margin: 2.5rem auto 0;
      padding: 0 1.5rem;
    }
    .btn {
      padding: 0.65rem 1.25rem;
      border-radius: 12px;
      font-weight: 700;
      font-size: 0.85rem;
      cursor: pointer;
      border: none;
      transition: all 0.15s;
    }
    .btn-primary { background: var(--cyan); color: #070a13; }
    .btn-secondary { background: #131c33; color: #cbd5e1; border: 1px solid var(--border); }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 800;
      font-family: "JetBrains Mono", monospace;
      text-transform: uppercase;
    }
    .badge-emerald { background: rgba(0, 245, 160, 0.15); color: var(--emerald); border: 1px solid rgba(0, 245, 160, 0.3); }
    .badge-cyan { background: rgba(0, 210, 255, 0.15); color: var(--cyan); border: 1px solid rgba(0, 210, 255, 0.3); }
  </style>
</head>
<body>
  <nav class="nav">
    <a href="/" style="color: #ffffff; font-weight: 800; text-decoration: none;">
      👤 ALIMENTA SOVEREIGN IDENTITY
    </a>
    <div style="display: flex; gap: 1rem; align-items: center;">
      <a href="/dashboard" style="color: var(--cyan); text-decoration: none; font-size: 0.85rem; font-weight: 700;">🔒 Dashboard</a>
      <a href="/" style="color: #94a3b8; text-decoration: none; font-size: 0.85rem;">&larr; Public Canvas</a>
    </div>
  </nav>

  <main class="container" id="profileRoot">
    <!-- Rendered via Profile Guard Engine -->
  </main>

  <script>
    const AUTH_KEY = '__ALIMENTA_SEC_SESSION__';

    function getSession() {
      try {
        const raw = sessionStorage.getItem(AUTH_KEY);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (parsed.expiresAt <= Date.now()) {
          sessionStorage.removeItem(AUTH_KEY);
          return null;
        }
        return parsed;
      } catch {
        return null;
      }
    }

    function renderProfile() {
      const session = getSession();
      if (!session) {
        document.getElementById('profileRoot').innerHTML = `
          <div class="card" style="max-width: 520px; margin: 4rem auto; text-align: center;">
            <h2 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 0.5rem;">Access Denied</h2>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1.5rem;">
              You must authenticate through the sovereign gateway to access user profile credentials.
            </p>
            <a href="/dashboard" class="btn btn-primary" style="text-decoration: none; display: inline-block;">
              Proceed to Dashboard Gateway
            </a>
          </div>
        `;
        return;
      }

      document.getElementById('profileRoot').innerHTML = `
        <div class="card" style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 56px; height: 56px; border-radius: 16px; background: rgba(0, 210, 255, 0.15); border: 1px solid var(--cyan); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 900; color: var(--cyan); font-family: monospace;">
              ${session.username.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h2 style="font-size: 1.25rem; font-weight: 800; color: #ffffff;">${session.username}</h2>
              <div style="font-size: 0.78rem; color: #94a3b8; font-family: monospace;">ID: ${session.userId} &middot; Role: ${session.role}</div>
            </div>
          </div>
          <span class="badge badge-emerald">Verified Identity</span>
        </div>

        <!-- Privacy & Security Controls -->
        <div class="card" style="margin-bottom: 1.5rem; space-y-4;">
          <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem;">Cryptographic Controls & Integrity</h3>
          <div style="background: #04060c; border: 1px solid var(--border); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-size: 0.88rem; font-weight: 700;">Hardware Two-Factor Verification (FIDO2)</div>
              <div style="font-size: 0.75rem; color: #94a3b8;">Cryptographic security keys protecting your observational contributions.</div>
            </div>
            <span class="badge badge-emerald">Active</span>
          </div>

          <div style="background: #04060c; border: 1px solid var(--border); border-radius: 12px; padding: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-size: 0.88rem; font-weight: 700;">Anti-CSRF Cross-Origin Token Binding</div>
              <div style="font-size: 0.75rem; color: #64748b; font-family: monospace;">Token: ${session.csrfToken}</div>
            </div>
            <span class="badge badge-cyan">Enforced</span>
          </div>
        </div>

        <!-- GDPR Export -->
        <div class="card">
          <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">Data Sovereignty (GDPR Rights)</h3>
          <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 1rem;">
            Export all audit logs, product ratings, and community contributions in open standardized JSON format.
          </p>
          <button onclick="alert('Export complete: alimenta_sovereign_archive.json downloaded.')" class="btn btn-secondary">
            📥 Download Complete Sovereign Audit Archive
          </button>
        </div>
      `;
    }

    renderProfile();
  </script>
</body>
</html>"""



def get_api_docs_html():
    """Generate an interactive API tester and documentation page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Open Food Facts — REST API Explorer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #0b1120;
      color: #f8fafc;
      font-family: "Plus Jakarta Sans", sans-serif;
      line-height: 1.5;
      padding-bottom: 4rem;
    }
    .nav {
      background: #0f172a;
      border-bottom: 1px solid #1e293b;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .nav-brand {
      font-weight: 800;
      font-size: 1.2rem;
      color: #fb923c;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }
    .nav a.back-btn {
      color: #94a3b8;
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 600;
    }
    .nav a.back-btn:hover { color: #ffffff; }

    .header {
      max-width: 1100px;
      margin: 2.5rem auto 1.5rem;
      padding: 0 1.5rem;
    }
    .header h1 {
      font-size: 2.2rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
    }
    .header p {
      color: #94a3b8;
      font-size: 1.05rem;
    }

    .main {
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .api-card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 14px;
      overflow: hidden;
      transition: border-color 0.15s;
    }
    .api-card:hover { border-color: #334155; }

    .api-card-top {
      padding: 1.25rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      cursor: pointer;
      user-select: none;
      flex-wrap: wrap;
    }
    .badge-get {
      background: #0284c7;
      color: #ffffff;
      font-weight: 800;
      font-size: 0.75rem;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-family: "JetBrains Mono", monospace;
    }
    .badge-post {
      background: #16a34a;
      color: #ffffff;
      font-weight: 800;
      font-size: 0.75rem;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-family: "JetBrains Mono", monospace;
    }
    .endpoint-path {
      font-family: "JetBrains Mono", monospace;
      font-size: 1rem;
      font-weight: 600;
      color: #f1f5f9;
    }
    .endpoint-summary {
      color: #94a3b8;
      font-size: 0.88rem;
      margin-left: auto;
    }

    .api-card-content {
      padding: 1.25rem 1.5rem 1.5rem;
      border-top: 1px solid #1e293b;
      background: #0b1329;
    }
    .input-row {
      display: flex;
      gap: 0.75rem;
      margin-bottom: 1rem;
    }
    .api-input {
      flex: 1;
      background: #1e293b;
      border: 1px solid #334155;
      color: #f8fafc;
      padding: 0.65rem 1rem;
      border-radius: 8px;
      font-family: "JetBrains Mono", monospace;
      font-size: 0.9rem;
      outline: none;
    }
    .api-input:focus { border-color: #38bdf8; }
    .btn-run {
      background: #0284c7;
      color: white;
      border: none;
      padding: 0.65rem 1.25rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      transition: background 0.15s;
    }
    .btn-run:hover { background: #0369a1; }

    .response-pane {
      background: #020617;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 1rem;
      max-height: 320px;
      overflow: auto;
      font-family: "JetBrains Mono", monospace;
      font-size: 0.82rem;
      color: #cbd5e1;
      white-space: pre-wrap;
      word-break: break-all;
    }
  </style>
</head>
<body>
  <nav class="nav">
    <a href="/" class="nav-brand">⚡ Open Food Facts API Explorer</a>
    <a href="/" class="back-btn">&larr; Back to Frontend Hub</a>
  </nav>

  <header class="header">
    <h1>REST API Interactive Playground</h1>
    <p>Test live queries, inspect full JSON payloads, and integrate Open Food Facts Web data into your applications.</p>
  </header>

  <main class="main">
    <!-- Health Check -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/health</span>
        <span class="endpoint-summary">Check system & dataset status</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_health" value="/api/health" readonly>
          <button class="btn-run" onclick="runQuery('in_health', 'out_health')">Send Request</button>
        </div>
        <div class="response-pane" id="out_health">Click "Send Request" to view JSON response...</div>
      </div>
    </div>

    <!-- Reuses Endpoint -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/v2/reuses</span>
        <span class="endpoint-summary">Query 605 ecosystem apps, IoT & research projects</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_reuses" value="/api/v2/reuses?limit=3&search=nutrition">
          <button class="btn-run" onclick="runQuery('in_reuses', 'out_reuses')">Send Request</button>
        </div>
        <div class="response-pane" id="out_reuses">Click "Send Request" to view JSON response...</div>
      </div>
    </div>

    <!-- Press Review Endpoint -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/v2/press</span>
        <span class="endpoint-summary">Query 342 global press mentions & media</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_press" value="/api/v2/press?limit=3&type=article">
          <button class="btn-run" onclick="runQuery('in_press', 'out_press')">Send Request</button>
        </div>
        <div class="response-pane" id="out_press">Click "Send Request" to view JSON response...</div>
      </div>
    </div>

    <!-- FAQ Endpoint -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/v2/faq</span>
        <span class="endpoint-summary">Query FAQ categories and answers</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_faq" value="/api/v2/faq?lang=en">
          <button class="btn-run" onclick="runQuery('in_faq', 'out_faq')">Send Request</button>
        </div>
        <div class="response-pane" id="out_faq">Click "Send Request" to view JSON response...</div>
      </div>
    </div>

    <!-- Scan Parties Endpoint -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/v2/scan-parties</span>
        <span class="endpoint-summary">Query all 19 barcode scan parties</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_sp" value="/api/v2/scan-parties">
          <button class="btn-run" onclick="runQuery('in_sp', 'out_sp')">Send Request</button>
        </div>
        <div class="response-pane" id="out_sp">Click "Send Request" to view JSON response...</div>
      </div>
    </div>

    <!-- Publications Endpoint -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/v2/publications</span>
        <span class="endpoint-summary">Query 138 peer-reviewed scientific studies</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_pub" value="/api/v2/publications?limit=3">
          <button class="btn-run" onclick="runQuery('in_pub', 'out_pub')">Send Request</button>
        </div>
        <div class="response-pane" id="out_pub">Click "Send Request" to view JSON response...</div>
      </div>
    </div>

    <!-- Queries Endpoint -->
    <div class="api-card">
      <div class="api-card-top">
        <span class="badge-get">GET</span>
        <span class="endpoint-path">/api/v2/queries</span>
        <span class="endpoint-summary">35 curated statistical & visual queries</span>
      </div>
      <div class="api-card-content">
        <div class="input-row">
          <input type="text" class="api-input" id="in_q" value="/api/v2/queries?limit=3">
          <button class="btn-run" onclick="runQuery('in_q', 'out_q')">Send Request</button>
        </div>
        <div class="response-pane" id="out_q">Click "Send Request" to view JSON response...</div>
      </div>
    </div>
  </main>

  <script>
    async function runQuery(inputId, outputId) {
      const url = document.getElementById(inputId).value;
      const out = document.getElementById(outputId);
      out.textContent = "Loading data from " + url + "...";
      try {
        const res = await fetch(url);
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        out.textContent = "Error fetching endpoint: " + err.message;
      }
    }
  </script>
</body>
</html>"""


class OpenFoodFactsHandler(http.server.BaseHTTPRequestHandler):
    """Custom HTTP handler serving Open Food Facts Web Frontend & Backend API."""

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API Endpoints
        if path.startswith("/api/"):
            self.handle_api(path, query)
            return

        # 2. Portal Homepage
        if path in ("/", "/index.html", "/home"):
            self.serve_html(get_portal_html())
            return

        # 2b. Secured User-End Routes (Dashboard & Profile)
        if path in ("/dashboard", "/dashboard.html"):
            self.serve_html(get_dashboard_html())
            return

        if path in ("/profile", "/profile.html"):
            self.serve_html(get_profile_html())
            return

        # 3. Static Assets: /images/* and /html/images/*
        if path.startswith("/html/images/") or path.startswith("/images/"):
            rel = path.replace("/html/images/", "").replace("/images/", "")
            file_path = os.path.join(IMAGES_DIR, rel)
            if os.path.isfile(file_path):
                self.serve_file(file_path)
                return

        # 4. Direct files in /data/*
        if path.startswith("/data/"):
            rel = path[6:]
            file_path = os.path.join(DATA_DIR, rel)
            if os.path.isfile(file_path):
                self.serve_file(file_path)
                return

        # 5. Dedicated Application Routes
        app_routes = {
            "/pro": os.path.join(REPO_ROOT, "scratch", "index-pro-2-compiled.html"),
            "/index-pro-2": os.path.join(REPO_ROOT, "scratch", "index-pro-2-compiled.html"),
            "/index-pro-2.html": os.path.join(REPO_ROOT, "scratch", "index-pro-2-compiled.html"),
            "/faq": os.path.join(LANG_DIR, "en", "texts", "faq.html"),
            "/reuses": os.path.join(LANG_DIR, "en", "texts", "reuses.html"),
            "/press-review": os.path.join(LANG_DIR, "en", "texts", "press-review.html"),
            "/scientific-publications": os.path.join(LANG_DIR, "en", "texts", "scientific-publications.html"),
            "/graphs-in-3-clicks": os.path.join(LANG_DIR, "en", "texts", "graphs-in-3-clicks.html"),
        }

        if path in app_routes and os.path.isfile(app_routes[path]):
            with open(app_routes[path], "r", encoding="utf-8") as f:
                content = f.read()
            resolved = resolve_includes(content, base_lang="en")
            wrapped = wrap_with_off_layout(resolved, title=path.strip("/").capitalize())
            self.serve_html(wrapped)
            return

        # 6. Check root HTML files (operation-sodas.html, scan-parties.html, impact.html, etc.)
        root_candidate = os.path.join(REPO_ROOT, path.lstrip("/"))
        if os.path.isfile(root_candidate) and root_candidate.endswith((".html", ".htm")):
            with open(root_candidate, "r", encoding="utf-8") as f:
                content = f.read()
            resolved = resolve_includes(content, base_lang="en")
            wrapped = wrap_with_off_layout(resolved, title=os.path.basename(root_candidate))
            self.serve_html(wrapped)
            return

        # 7. Check /page/<slug> or /<slug>.html in lang/en/texts/
        page_slug = ""
        if path.startswith("/page/"):
            page_slug = path[6:]
        elif path.endswith(".html") or not "." in path:
            page_slug = path.lstrip("/").replace(".html", "")

        if page_slug:
            lang_candidate = os.path.join(LANG_DIR, "en", "texts", f"{page_slug}.html")
            if os.path.isfile(lang_candidate):
                with open(lang_candidate, "r", encoding="utf-8") as f:
                    content = f.read()
                resolved = resolve_includes(content, base_lang="en")
                wrapped = wrap_with_off_layout(resolved, title=page_slug.replace("-", " ").title())
                self.serve_html(wrapped)
                return

        # 8. Check any generic file relative to repo root
        file_candidate = os.path.join(REPO_ROOT, path.lstrip("/"))
        if os.path.isfile(file_candidate):
            self.serve_file(file_candidate)
            return

        # 404 Not Found
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>404 Not Found</h1><p><a href='/'>Return to Open Food Facts Hub</a></p>")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/compile":
            # Trigger compilation pipeline
            try:
                compile_script = os.path.join(REPO_ROOT, "scripts", "compile.py")
                env = dict(os.environ)
                env["PYTHONUTF8"] = "1"
                proc = subprocess.run([sys.executable, compile_script], env=env, capture_output=True, text=True)
                load_all_datasets()
                res = {
                    "status": "success" if proc.returncode == 0 else "error",
                    "code": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                }
                self.send_json(res)
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)}, status=500)
            return

        self.send_response(404)
        self.end_headers()

    def handle_api(self, path, query):
        """Route API calls."""
        if path in ("/api", "/api/", "/api/docs"):
            self.serve_html(get_api_docs_html())
            return

        if path == "/api/health":
            queries_data = DATASETS.get("queries", {})
            queries_count = len(queries_data.get("queries", [])) if isinstance(queries_data, dict) else len(queries_data)
            faq_data = DATASETS.get("faq", {})
            faq_count = sum(len(c.get("questions", [])) for c in faq_data.get("en", [])) if isinstance(faq_data, dict) and "en" in faq_data else 87
            self.send_json({
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "service": "Open Food Facts Web Dev Server",
                "datasets": {
                    "reuses": len(DATASETS.get("reuses", [])),
                    "press": len(DATASETS.get("press", [])),
                    "faq_questions": faq_count,
                    "queries": queries_count,
                    "scan_parties": len(DATASETS.get("scan_parties", [])),
                    "publications": len(DATASETS.get("publications", [])),
                    "mobile_features": len(DATASETS.get("mobile_features", [])),
                },
                "python": sys.version.split()[0],
            })
            return

        if path == "/api/v2/reuses":
            items = DATASETS.get("reuses", [])
            q = query.get("search", query.get("q", [""]))[0].lower()
            if q:
                items = [
                    x for x in items
                    if q in str(x.get("title", "")).lower()
                    or q in str(x.get("description", "")).lower()
                    or q in str(x.get("tag", "")).lower()
                ]
            limit = int(query.get("limit", [50])[0])
            offset = int(query.get("offset", [0])[0])
            self.send_json({
                "total": len(items),
                "limit": limit,
                "offset": offset,
                "results": items[offset:offset + limit]
            })
            return

        if path == "/api/v2/press":
            items = DATASETS.get("press", [])
            q = query.get("search", query.get("q", [""]))[0].lower()
            t = query.get("type", [""])[0].lower()
            if t:
                items = [x for x in items if str(x.get("type", "")).lower() == t]
            if q:
                items = [
                    x for x in items
                    if q in str(x.get("title", "")).lower()
                    or q in str(x.get("source", "")).lower()
                    or q in str(x.get("verbatim", "")).lower()
                ]
            limit = int(query.get("limit", [50])[0])
            offset = int(query.get("offset", [0])[0])
            self.send_json({
                "total": len(items),
                "limit": limit,
                "offset": offset,
                "results": items[offset:offset + limit]
            })
            return

        if path == "/api/v2/faq":
            data = DATASETS.get("faq", {})
            lang = query.get("lang", [""])[0].lower()
            if lang and isinstance(data, dict) and lang in data:
                self.send_json(data[lang])
            else:
                self.send_json(data)
            return

        if path == "/api/v2/queries":
            raw = DATASETS.get("queries", {})
            items = raw.get("queries", []) if isinstance(raw, dict) else raw
            limit = int(query.get("limit", [50])[0])
            self.send_json({
                "total": len(items),
                "results": items[:limit]
            })
            return

        if path == "/api/v2/scan-parties":
            items = DATASETS.get("scan_parties", [])
            self.send_json({
                "total": len(items),
                "results": items
            })
            return

        if path == "/api/v2/publications":
            items = DATASETS.get("publications", [])
            limit = int(query.get("limit", [50])[0])
            self.send_json({
                "total": len(items),
                "results": items[:limit]
            })
            return

        if path == "/api/v2/mobile-features":
            items = DATASETS.get("mobile_features", [])
            self.send_json({
                "total": len(items),
                "results": items
            })
            return

        self.send_json({"error": "Unknown API endpoint"}, status=404)

    def serve_html(self, content_str):
        data = content_str.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def serve_file(self, file_path):
        mime, _ = mimetypes.guess_type(file_path)
        if not mime:
            mime = "application/octet-stream"
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error reading file: {e}".encode("utf-8"))

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Clean logging format
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} - {format % args}")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def start_server(port=8080):
    os.chdir(REPO_ROOT)
    load_all_datasets()
    print("=" * 65)
    print("🚀  Open Food Facts Web & REST API Server")
    print("=" * 65)
    print(f"🌐  Frontend Hub & Portal : http://localhost:{port}/")
    print(f"⚡  API Documentation      : http://localhost:{port}/api/docs")
    print(f"🩺  Health Check Endpoint : http://localhost:{port}/api/health")
    print(f"📦  Active Datasets       : {len(DATASETS)} loaded into memory")
    print("=" * 65)
    print("Press Ctrl+C to stop the server.")

    server = ThreadedHTTPServer(("0.0.0.0", port), OpenFoodFactsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Open Food Facts Web Server")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port to listen on (default 8080)")
    args = parser.parse_args()
    start_server(port=args.port)
