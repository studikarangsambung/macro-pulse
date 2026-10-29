"""
Futuristic, Minimalist HTML Dashboard Generator
Design principles:
- Minimalism & negative space (Foundry / Supima aesthetic)
- Bold visuals & subtle motion (Imagine Software futuristic dark-tech)
- AI-driven personalization (Interactive tabbed views: Macro, Sectors, Crypto, WhatsApp)
- Fast loading & 100% mobile responsive
- Innovative typography (Plus Jakarta Sans & JetBrains Mono)
"""

import json
import os

def render_html_report(payload, output_path="report_us_macro.html"):
    regime = payload["regime"]
    ews = payload["ews"]
    sectors = payload["sectors"]
    crypto = payload["crypto"]
    corrs = payload["correlations"]
    net_liq = payload["net_liquidity"]
    prices = payload["macro_prices"]
    whatsapp_text = payload["whatsapp_broadcast"]
    display_date = payload["display_date"]
    
    # Status badges helper
    def ews_badge(status):
        if status == "BAHAYA":
            return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>BAHAYA</span>'
        elif status == "WASPADA":
            return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>WASPADA</span>'
        else:
            return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>AMAN</span>'

    def chg_color(val):
        if val > 0:
            return "text-emerald-400"
        elif val < 0:
            return "text-rose-400"
        return "text-zinc-400"

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>MACRO PULSE · US Sectors & Crypto Intelligence</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    }},
                    colors: {{
                        vault: {{
                            950: '#06070A',
                            900: '#0A0C11',
                            850: '#10131B',
                            800: '#171B26',
                            700: '#262C3D',
                        }},
                        accent: {{
                            cyan: '#00F0FF',
                            purple: '#7928CA',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background-color: #06070A;
            color: #E2E8F0;
            letter-spacing: -0.01em;
        }}
        .glass-card {{
            background: linear-gradient(135deg, rgba(16, 19, 27, 0.75) 0%, rgba(10, 12, 17, 0.6) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .glass-card:hover {{
            border-color: rgba(0, 240, 255, 0.25);
            box-shadow: 0 10px 30px -10px rgba(0, 240, 255, 0.08);
            transform: translateY(-2px);
        }}
        .glow-cyan {{
            box-shadow: 0 0 25px -5px rgba(0, 240, 255, 0.3);
        }}
        .tab-btn.active {{
            background-color: #171B26;
            color: #00F0FF;
            border-color: rgba(0, 240, 255, 0.3);
        }}
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: #06070A;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #262C3D;
            border-radius: 9999px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #00F0FF;
        }}
    </style>
</head>
<body class="min-h-screen selection:bg-cyan-500/20 selection:text-cyan-300">

    <!-- Top Glow Element -->
    <div class="fixed top-0 left-1/2 -translate-x-1/2 w-[700px] h-[250px] bg-cyan-500/10 blur-[140px] pointer-events-none -z-10"></div>
    <div class="fixed top-40 right-10 w-[400px] h-[300px] bg-purple-600/10 blur-[130px] pointer-events-none -z-10"></div>

    <!-- Sticky Minimal Navigation Bar -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-vault-950/80 border-b border-white/[0.06] px-4 sm:px-8 py-3.5">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center font-black text-black text-sm tracking-wider">
                    MP
                </div>
                <div>
                    <h1 class="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                        MACRO PULSE <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-400">US & Crypto Engine v1.0</span>
                    </h1>
                    <p class="text-xs text-zinc-400 font-mono">{display_date}</p>
                </div>
            </div>

            <!-- Tab Switcher (Personalization Filter) -->
            <div class="flex items-center bg-vault-900/90 p-1 rounded-xl border border-white/10 text-xs font-medium">
                <button onclick="switchTab('tab-overview')" id="btn-tab-overview" class="tab-btn active px-3.5 py-1.5 rounded-lg border border-transparent transition-all">Overview</button>
                <button onclick="switchTab('tab-sectors')" id="btn-tab-sectors" class="tab-btn px-3.5 py-1.5 rounded-lg border border-transparent transition-all">US Sectors</button>
                <button onclick="switchTab('tab-crypto')" id="btn-tab-crypto" class="tab-btn px-3.5 py-1.5 rounded-lg border border-transparent transition-all">Crypto & Liquidity</button>
                <button onclick="switchTab('tab-whatsapp')" id="btn-tab-whatsapp" class="tab-btn px-3.5 py-1.5 rounded-lg border border-transparent transition-all flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>WhatsApp
                </button>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-10">

        <!-- HERO REGIME BANNER -->
        <section class="glass-card rounded-2xl p-6 sm:p-8 relative overflow-hidden">
            <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>
            
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div class="space-y-2">
                    <div class="flex items-center gap-2.5">
                        <span class="px-2.5 py-0.5 rounded text-[11px] font-mono tracking-wider uppercase font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                            CURRENT MACRO REGIME
                        </span>
                        <span class="text-xs font-mono text-zinc-400">Analog: {regime['analog']}</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
                        {regime['title']}
                    </h2>
                    <p class="text-sm text-zinc-300 max-w-3xl leading-relaxed">
                        {regime['summary']}
                    </p>
                </div>

                <!-- EWS Tally Scorecard -->
                <div class="flex items-center gap-3 shrink-0 bg-vault-900/80 p-3.5 rounded-xl border border-white/10">
                    <div class="text-center px-3 border-r border-white/10">
                        <div class="text-xl font-bold font-mono text-rose-400">{regime['score_bahaya']}</div>
                        <div class="text-[10px] text-zinc-400 uppercase tracking-wider">Bahaya</div>
                    </div>
                    <div class="text-center px-3 border-r border-white/10">
                        <div class="text-xl font-bold font-mono text-amber-400">{regime['score_waspada']}</div>
                        <div class="text-[10px] text-zinc-400 uppercase tracking-wider">Waspada</div>
                    </div>
                    <div class="text-center px-3">
                        <div class="text-xl font-bold font-mono text-emerald-400">{len(ews) - regime['score_bahaya'] - regime['score_waspada']}</div>
                        <div class="text-[10px] text-zinc-400 uppercase tracking-wider">Aman</div>
                    </div>
                </div>
            </div>

            <!-- Causality Chain Streamline -->
            <div class="mt-6 pt-6 border-t border-white/[0.06] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-mono">
                <div class="bg-vault-900/60 p-3.5 rounded-xl border border-white/5 space-y-1">
                    <div class="text-[10px] text-cyan-400 uppercase font-semibold">1 · Pemicu Makro</div>
                    <div class="text-zinc-200">US10Y ({prices.get('^TNX', {}).get('close', 0):.2f}%) & WTI (${prices.get('CL=F', {}).get('close', 0):.2f})</div>
                </div>
                <div class="bg-vault-900/60 p-3.5 rounded-xl border border-white/5 space-y-1">
                    <div class="text-[10px] text-amber-400 uppercase font-semibold">2 · Kondisi Moneter</div>
                    <div class="text-zinc-200">Suku bunga riil tinggi & Ekspektasi inflasi alot</div>
                </div>
                <div class="bg-vault-900/60 p-3.5 rounded-xl border border-white/5 space-y-1">
                    <div class="text-[10px] text-purple-400 uppercase font-semibold">3 · Transmisi Sektor</div>
                    <div class="text-zinc-200">Rotasi modal ke {', '.join(regime['favored_sectors'][:2])}</div>
                </div>
                <div class="bg-vault-900/60 p-3.5 rounded-xl border border-white/5 space-y-1">
                    <div class="text-[10px] text-emerald-400 uppercase font-semibold">4 · Sikap Crypto</div>
                    <div class="text-zinc-200">{regime['crypto_stance']}</div>
                </div>
            </div>
        </section>

        <!-- TAB 1: OVERVIEW -->
        <div id="tab-overview" class="tab-pane space-y-8">
            
            <!-- KEY ASSET METRIC TICKERS -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div class="glass-card rounded-xl p-4 space-y-1">
                    <div class="text-[11px] text-zinc-400 font-medium">Bitcoin (BTC)</div>
                    <div class="text-lg font-bold font-mono text-white">${prices.get('BTC-USD', {}).get('close', 0):,.0f}</div>
                    <div class="text-xs font-mono {chg_color(prices.get('BTC-USD', {}).get('change_1d_pct', 0))}">
                        {prices.get('BTC-USD', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="glass-card rounded-xl p-4 space-y-1">
                    <div class="text-[11px] text-zinc-400 font-medium">S&P 500 (SPY)</div>
                    <div class="text-lg font-bold font-mono text-white">${prices.get('SPY', {}).get('close', 0):.2f}</div>
                    <div class="text-xs font-mono {chg_color(prices.get('SPY', {}).get('change_1d_pct', 0))}">
                        {prices.get('SPY', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="glass-card rounded-xl p-4 space-y-1">
                    <div class="text-[11px] text-zinc-400 font-medium">US 10Y Yield</div>
                    <div class="text-lg font-bold font-mono text-white">{prices.get('^TNX', {}).get('close', 0):.3f}%</div>
                    <div class="text-xs font-mono text-zinc-400">Benchmark Rate</div>
                </div>
                <div class="glass-card rounded-xl p-4 space-y-1">
                    <div class="text-[11px] text-zinc-400 font-medium">US Dollar (DXY)</div>
                    <div class="text-lg font-bold font-mono text-white">{prices.get('DX-Y.NYB', {}).get('close', 0):.2f}</div>
                    <div class="text-xs font-mono {chg_color(prices.get('DX-Y.NYB', {}).get('change_1d_pct', 0))}">
                        {prices.get('DX-Y.NYB', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="glass-card rounded-xl p-4 space-y-1">
                    <div class="text-[11px] text-zinc-400 font-medium">WTI Crude Oil</div>
                    <div class="text-lg font-bold font-mono text-white">${prices.get('CL=F', {}).get('close', 0):.2f}</div>
                    <div class="text-xs font-mono {chg_color(prices.get('CL=F', {}).get('change_1d_pct', 0))}">
                        {prices.get('CL=F', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="glass-card rounded-xl p-4 space-y-1">
                    <div class="text-[11px] text-zinc-400 font-medium">Fed Net Liquidity</div>
                    <div class="text-lg font-bold font-mono text-cyan-400">${net_liq.get('net_liquidity_bil', 0):,.1f}B</div>
                    <div class="text-xs font-mono {chg_color(net_liq.get('change_4w_bil', 0))}">
                        {net_liq.get('change_4w_bil', 0):+.1f}B (4W)
                    </div>
                </div>
            </div>

            <!-- 2-COL GRID: EWS & CORRELATION MATRIX -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                <!-- Early Warning Signals -->
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                        <h3 class="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-cyan-400"></span>EARLY WARNING SIGNALS (EWS)
                        </h3>
                        <span class="text-xs font-mono text-zinc-400">8 Triggers Monitored</span>
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-vault-900/80 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div class="space-y-1">
                                <div class="text-xs font-semibold text-zinc-200">{item['name']}</div>
                                <div class="text-[11px] text-zinc-400">{item['context']}</div>
                            </div>
                            <div class="flex items-center gap-3 shrink-0 self-end sm:self-center">
                                <span class="font-mono text-xs font-bold text-white">{item['value']}</span>
                                {ews_badge(item['status'])}
                            </div>
                        </div>
                        ''' for item in ews])}
                    </div>
                </div>

                <!-- Cross-Asset Correlations -->
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                        <h3 class="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-indigo-400"></span>CROSS-ASSET CORRELATION MATRIX
                        </h3>
                        <span class="text-xs font-mono text-zinc-400">Rolling 30-Day Pearson r</span>
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-vault-900/80 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div class="space-y-1">
                                <div class="text-xs font-semibold text-zinc-200">{c['pair_name']}</div>
                                <div class="text-[11px] text-zinc-400">{c['notes']} (Expected: {c['expected_range']})</div>
                            </div>
                            <div class="flex items-center gap-3 shrink-0 self-end sm:self-center">
                                <span class="font-mono text-xs font-bold {chg_color(c['current_r'])}">{c['current_r']:+.2f}</span>
                                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase {'bg-rose-500/10 text-rose-400 border border-rose-500/20' if c['status'] == 'INVERT' else ('bg-amber-500/10 text-amber-400 border border-amber-500/20' if c['status'] == 'BREAK' else 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20')}">{c['status']}</span>
                            </div>
                        </div>
                        ''' for c in corrs])}
                    </div>
                </div>

            </div>

        </div>

        <!-- TAB 2: US 11 SECTORS DEEP-DIVE -->
        <div id="tab-sectors" class="tab-pane hidden space-y-6">
            <div class="glass-card rounded-2xl p-6 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.06]">
                    <div>
                        <h3 class="text-base font-bold text-white">S&P 500 Select Sector SPDR Tracker</h3>
                        <p class="text-xs text-zinc-400">Rotasi momentum dan keselarasan dengan rezim makro saat ini</p>
                    </div>
                    <div class="flex items-center gap-2 text-xs font-mono">
                        <span class="px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">OW = Overweight</span>
                        <span class="px-2 py-1 rounded bg-zinc-800 text-zinc-300 border border-white/10">N = Neutral</span>
                        <span class="px-2 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">UW = Underweight</span>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="text-[11px] font-mono text-zinc-400 uppercase tracking-wider border-b border-white/[0.06]">
                            <tr>
                                <th class="pb-3 font-semibold">Ticker & Sektor</th>
                                <th class="pb-3 font-semibold">Profil Karakter</th>
                                <th class="pb-3 font-semibold text-right">Harga</th>
                                <th class="pb-3 font-semibold text-right">1D %</th>
                                <th class="pb-3 font-semibold text-right">5D %</th>
                                <th class="pb-3 font-semibold text-right">20D %</th>
                                <th class="pb-3 font-semibold text-right">Momentum</th>
                                <th class="pb-3 font-semibold text-right">Rekomendasi</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-white/[0.04] font-mono">
                            {"".join([f'''
                            <tr class="hover:bg-white/[0.02] transition-colors">
                                <td class="py-3.5 font-bold text-white flex items-center gap-2">
                                    <span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-400 font-mono text-xs">{s['ticker']}</span>
                                    <span class="font-sans font-medium text-zinc-200">{s['name']}</span>
                                </td>
                                <td class="py-3.5 font-sans text-zinc-400">{s['profile']}</td>
                                <td class="py-3.5 text-right font-bold text-white">${s['close']:.2f}</td>
                                <td class="py-3.5 text-right {chg_color(s['chg_1d'])}">{s['chg_1d']:+.2f}%</td>
                                <td class="py-3.5 text-right {chg_color(s['chg_5d'])}">{s['chg_5d']:+.2f}%</td>
                                <td class="py-3.5 text-right {chg_color(s['chg_20d'])}">{s['chg_20d']:+.2f}%</td>
                                <td class="py-3.5 text-right font-bold text-white">{s['momentum_score']:+.2f}</td>
                                <td class="py-3.5 text-right">
                                    <span class="px-2 py-0.5 rounded text-[10px] font-bold {'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' if 'OVERWEIGHT' in s['recommendation'] else ('bg-rose-500/10 text-rose-400 border border-rose-500/20' if 'UNDERWEIGHT' in s['recommendation'] else 'bg-zinc-800 text-zinc-300 border border-white/10')}">
                                        {s['recommendation']}
                                    </span>
                                </td>
                            </tr>
                            ''' for s in sectors])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 3: CRYPTO & LIQUIDITY -->
        <div id="tab-crypto" class="tab-pane hidden space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {"".join([f'''
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="flex items-center justify-between">
                        <span class="px-2.5 py-1 rounded bg-white/5 border border-white/10 text-cyan-400 font-mono text-xs font-bold">{c['ticker']}</span>
                        <span class="text-xs text-zinc-400 font-mono">{c['category']}</span>
                    </div>
                    <div>
                        <div class="text-2xl font-extrabold font-mono text-white">${c['close']:,.2f}</div>
                        <div class="text-xs font-mono {chg_color(c['chg_1d'])} mt-1">{c['chg_1d']:+.2f}% (1D) · {c['chg_20d']:+.2f}% (20D)</div>
                    </div>
                    <div class="pt-4 border-t border-white/[0.06] text-xs text-zinc-400 space-y-1">
                        <div>Transmisi: Sangat sensitif terhadap Fed Net Liquidity & DXY.</div>
                    </div>
                </div>
                ''' for c in crypto])}

            </div>

            <!-- Fed Net Liquidity Card -->
            <div class="glass-card rounded-2xl p-6 space-y-4">
                <div class="flex items-center justify-between pb-4 border-b border-white/[0.06]">
                    <div>
                        <h3 class="text-base font-bold text-white">Fed Net Liquidity Engine</h3>
                        <p class="text-xs text-zinc-400">Total Assets (WALCL) − Treasury General Account (TGA) − Overnight Reverse Repo (RRP)</p>
                    </div>
                    <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
                        Historical Correlation with BTC: +0.82
                    </span>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
                    <div class="bg-vault-900/70 p-4 rounded-xl border border-white/5">
                        <div class="text-xs text-zinc-400">Fed Total Assets (WALCL)</div>
                        <div class="text-lg font-bold font-mono text-white mt-1">${net_liq.get('walcl', 0):,.0f}M</div>
                    </div>
                    <div class="bg-vault-900/70 p-4 rounded-xl border border-white/5">
                        <div class="text-xs text-zinc-400">Treasury TGA (WTREGEN)</div>
                        <div class="text-lg font-bold font-mono text-amber-400 mt-1">${net_liq.get('tga', 0):,.0f}M</div>
                    </div>
                    <div class="bg-vault-900/70 p-4 rounded-xl border border-white/5">
                        <div class="text-xs text-zinc-400">Reverse Repo (RRP)</div>
                        <div class="text-lg font-bold font-mono text-zinc-300 mt-1">${net_liq.get('rrp', 0):.3f}B</div>
                    </div>
                    <div class="bg-vault-900/70 p-4 rounded-xl border border-cyan-500/30">
                        <div class="text-xs text-cyan-400 font-semibold">Net Liquidity Result</div>
                        <div class="text-lg font-bold font-mono text-cyan-300 mt-1">${net_liq.get('net_liquidity_bil', 0):,.1f}B</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: WHATSAPP BROADCAST (READY TO COPY) -->
        <div id="tab-whatsapp" class="tab-pane hidden space-y-6">
            <div class="glass-card rounded-2xl p-6 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.06]">
                    <div>
                        <h3 class="text-base font-bold text-white flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            WhatsApp Macro & Sector Impact Broadcast
                        </h3>
                        <p class="text-xs text-zinc-400">Teks rantai kausalitas sentimen siap salin dan kirim langsung ke grup investor</p>
                    </div>
                    <button onclick="copyToClipboard()" id="copy-btn" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black text-xs font-bold font-mono flex items-center gap-2 transition-all">
                        📋 Copy to Clipboard
                    </button>
                </div>

                <div class="relative">
                    <textarea id="wa-text" readonly rows="22" class="w-full bg-vault-950/90 border border-white/10 rounded-xl p-4 font-mono text-xs text-zinc-200 leading-relaxed focus:outline-none focus:border-cyan-500/50 resize-y">{whatsapp_text}</textarea>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="max-w-7xl mx-auto px-4 sm:px-8 py-8 border-t border-white/[0.06] text-center text-xs text-zinc-500 font-mono">
        MACRO PULSE · Institutional-grade Pattern Recognition Engine for US Equities & Crypto. Point-in-time FRED & Market Ingestion.
    </footer>

    <!-- Interactive Script -->
    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            const target = document.getElementById(tabId);
            if (target) target.classList.remove('hidden');
            
            const btn = document.getElementById('btn-' + tabId);
            if (btn) btn.classList.add('active');
        }}

        function copyToClipboard() {{
            const copyText = document.getElementById("wa-text");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(copyText.value);
            
            const btn = document.getElementById("copy-btn");
            const originalText = btn.innerHTML;
            btn.innerHTML = "✅ Copied to Clipboard!";
            btn.classList.remove("bg-emerald-500", "text-black");
            btn.classList.add("bg-cyan-400", "text-black");
            
            setTimeout(() => {{
                btn.innerHTML = originalText;
                btn.classList.remove("bg-cyan-400");
                btn.classList.add("bg-emerald-500", "text-black");
            }}, 2500);
        }}
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Rendered institutional report to {output_path}")
    
    # Also write to index.html for instant root localhost:8080 viewing
    index_path = os.path.join(os.path.dirname(os.path.abspath(output_path)), "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return os.path.abspath(output_path)

if __name__ == "__main__":
    from data_fetcher import get_latest_snapshot
    from analytics_engine import evaluate_ews, classify_macro_regime, compute_correlation_matrix, compute_sector_scorecard, compute_crypto_scorecard, load_price_history
    from narrative_generator import generate_report_payload
    
    snapshot = get_latest_snapshot()
    price_df = load_price_history()
    ews = evaluate_ews(snapshot)
    regime = classify_macro_regime(snapshot, ews)
    corrs = compute_correlation_matrix(price_df)
    sectors = compute_sector_scorecard(snapshot, regime)
    crypto_data, eth_btc = compute_crypto_scorecard(snapshot)
    
    payload = generate_report_payload(snapshot, ews, regime, corrs, sectors, crypto_data, eth_btc)
    path = render_html_report(payload)
    print("HTML Generator verified:", path)
