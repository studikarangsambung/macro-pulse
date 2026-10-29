"""
Retro Classic Financial Terminal Dashboard Generator (Bloomberg 1980s / Vintage Teletype Aesthetic)
Features:
- Vintage Amber Phosphor on Dark CRT Slate theme
- Live client-side real-time price streamer (Binance API for Crypto, live market clock WIB & EST)
- Flow Projection & Weekly Economic Calendar with Scenario Impacts
- US 11 Sectors Ledger, Crypto Liquidity, Indonesia Wire, and WhatsApp Dispatch
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
    global_news = payload.get("global_news", [])
    indonesia_news = payload.get("indonesia_news", [])
    indo_macro = payload.get("indo_macro") or {}
    weekly_cal = payload.get("weekly_calendar", [])
    flow_proj = payload.get("flow_proj", {})

    # Helper for retro badges
    def retro_badge(status):
        if any(w in status for w in ["BAHAYA", "TEKANAN BERAT", "RISK-OFF", "HAWKISH", "BEBAN"]):
            return f'<span class="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-bold bg-amber-500/20 text-rose-400 border border-rose-500/40">[! {status} !]</span>'
        elif any(w in status for w in ["WASPADA", "MODERAT"]):
            return f'<span class="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">[* {status} *]</span>'
        else:
            return f'<span class="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">[+ {status} +]</span>'

    def chg_color(val):
        if val > 0:
            return "text-amber-400 font-bold"
        elif val < 0:
            return "text-rose-400 font-bold"
        return "text-zinc-400"

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MACRO PULSE · RETRO FINANCIAL TERMINAL</title>
    <!-- Vintage & Monospace Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=VT323&display=swap" rel="stylesheet">
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        mono: ['IBM Plex Mono', 'monospace'],
                        typewriter: ['Courier Prime', 'monospace'],
                        headline: ['Playfair Display', 'serif'],
                        crt: ['VT323', 'monospace'],
                    }},
                    colors: {{
                        amber: {{
                            400: '#FBBF24',
                            500: '#F59E0B',
                            600: '#D97706',
                        }},
                        terminal: {{
                            950: '#08080A',
                            900: '#0E0F12',
                            850: '#15161B',
                            800: '#1D1F26',
                            700: '#2A2D37',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background-color: #08080A;
            color: #D1D5DB;
            letter-spacing: -0.01em;
            background-image: 
                radial-gradient(rgba(245, 158, 11, 0.03) 1px, transparent 0),
                linear-gradient(rgba(14, 15, 18, 0.8) 1px, transparent 0);
            background-size: 24px 24px, 100% 4px;
        }}
        .retro-card {{
            background-color: #0E0F12;
            border: 1px solid rgba(245, 158, 11, 0.25);
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.7), inset 0 0 12px rgba(245, 158, 11, 0.02);
            transition: all 0.2s ease;
        }}
        .retro-card:hover {{
            border-color: rgba(245, 158, 11, 0.45);
            box-shadow: 0 6px 24px -2px rgba(245, 158, 11, 0.08);
        }}
        .retro-double-border {{
            border: 3px double rgba(245, 158, 11, 0.35);
        }}
        .tab-btn.active {{
            background-color: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border-color: #F59E0B;
        }}
        .amber-glow {{
            text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
        }}
        .ticker-flash-up {{
            animation: flashUp 1s ease;
        }}
        .ticker-flash-down {{
            animation: flashDown 1s ease;
        }}
        @keyframes flashUp {{
            0% {{ background-color: rgba(16, 185, 129, 0.3); }}
            100% {{ background-color: transparent; }}
        }}
        @keyframes flashDown {{
            0% {{ background-color: rgba(244, 63, 94, 0.3); }}
            100% {{ background-color: transparent; }}
        }}
        /* Retro Teletype Marquee */
        .marquee-container {{
            overflow: hidden;
            white-space: nowrap;
        }}
        .marquee-content {{
            display: inline-block;
            animation: marquee 35s linear infinite;
        }}
        @keyframes marquee {{
            0% {{ transform: translate3d(0, 0, 0); }}
            100% {{ transform: translate3d(-50%, 0, 0); }}
        }}
    </style>
</head>
<body class="min-h-screen selection:bg-amber-500/20 selection:text-amber-300 font-mono">

    <!-- TOP TELETYPE TICKER TAPE -->
    <div class="border-b border-amber-500/30 bg-terminal-900 py-1.5 px-4 text-[11px] font-mono text-amber-400 flex items-center justify-between">
        <div class="flex items-center gap-2 shrink-0 pr-4 border-r border-amber-500/30 font-bold uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>WIRE TICKER [LIVE]</span>
        </div>
        <div class="marquee-container w-full overflow-hidden">
            <div class="marquee-content flex gap-8 items-center text-xs">
                <span>BTC/USD: <b class="text-white" id="live-tape-btc">${prices.get('BTC-USD', {}).get('close', 0):,.0f}</b> <span class="{chg_color(prices.get('BTC-USD', {}).get('change_1d_pct', 0))}">{prices.get('BTC-USD', {}).get('change_1d_pct', 0):+.2f}%</span></span>
                <span>GOLD (XAUUSD): <b class="text-white">${prices.get('GC=F', {}).get('close', 0):,.1f}</b></span>
                <span>USD/IDR: <b class="text-white">Rp {prices.get('USDIDR=X', {}).get('close', 0):,.0f}</b></span>
                <span>S&P 500: <b class="text-white">${prices.get('SPY', {}).get('close', 0):.2f}</b></span>
                <span>US10Y: <b class="text-white">{prices.get('^TNX', {}).get('close', 0):.3f}%</b></span>
                <span>DXY: <b class="text-white">{prices.get('DX-Y.NYB', {}).get('close', 0):.2f}</b></span>
                <span>WTI OIL: <b class="text-white">${prices.get('CL=F', {}).get('close', 0):.2f}</b></span>
                <span>ETH/USD: <b class="text-white" id="live-tape-eth">${prices.get('ETH-USD', {}).get('close', 0):,.0f}</b></span>
                <span>SOL/USD: <b class="text-white" id="live-tape-sol">${prices.get('SOL-USD', {}).get('close', 0):,.2f}</b></span>
                <span>FED NET LIQ: <b class="text-amber-300">${net_liq.get('net_liquidity_bil', 0):,.1f}B</b></span>
                <!-- Repeat for smooth loop -->
                <span>BTC/USD: <b class="text-white">${prices.get('BTC-USD', {}).get('close', 0):,.0f}</b></span>
                <span>GOLD: <b class="text-white">${prices.get('GC=F', {}).get('close', 0):,.1f}</b></span>
                <span>USD/IDR: <b class="text-white">Rp {prices.get('USDIDR=X', {}).get('close', 0):,.0f}</b></span>
            </div>
        </div>
        <div class="shrink-0 pl-4 border-l border-amber-500/30 text-[10px] text-zinc-400 hidden sm:block">
            <span id="market-status-badge">[NYSE: OPEN]</span>
        </div>
    </div>

    <!-- RETRO CLASSIC HEADER MASTHEAD -->
    <header class="border-b-2 border-double border-amber-500/40 bg-terminal-950 px-4 sm:px-8 py-5">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
            
            <div class="space-y-1 text-center md:text-left">
                <div class="flex items-center justify-center md:justify-start gap-2 text-[10px] uppercase font-mono tracking-widest text-amber-500">
                    <span>★ THE MACRO TELETYPE DISPATCH ★</span>
                    <span>·</span>
                    <span>VOL. XXVI · NO. 301</span>
                </div>
                <h1 class="text-2xl sm:text-3xl font-headline font-extrabold tracking-tight text-amber-400 amber-glow">
                    MACRO PULSE FINANCIAL TERMINAL
                </h1>
                <p class="text-xs text-zinc-400 font-typewriter">
                    Global Liquidity Surveillance · US Equities · Crypto Assets · Indonesian Sovereign Spillover
                </p>
            </div>

            <!-- DUAL LIVE CLOCKS -->
            <div class="flex items-center gap-4 bg-terminal-900 border border-amber-500/30 p-2.5 rounded-none text-xs">
                <div class="text-right px-2 border-r border-amber-500/20">
                    <div class="text-[10px] text-zinc-400 uppercase">Jakarta (WIB)</div>
                    <div class="font-bold text-amber-400" id="clock-wib">--:--:-- WIB</div>
                </div>
                <div class="text-left px-2">
                    <div class="text-[10px] text-zinc-400 uppercase">New York (EST)</div>
                    <div class="font-bold text-zinc-200" id="clock-est">--:--:-- EST</div>
                </div>
            </div>

        </div>

        <!-- RETRO NAVIGATION MENU -->
        <div class="max-w-7xl mx-auto mt-4 pt-3 border-t border-amber-500/20 flex flex-wrap items-center justify-center md:justify-start gap-2 text-xs">
            <button onclick="switchTab('tab-overview')" id="btn-tab-overview" class="tab-btn active px-3.5 py-1.5 border border-amber-500/30 font-bold uppercase tracking-wider transition-all">
                [1] Main Ledger
            </button>
            <button onclick="switchTab('tab-flow')" id="btn-tab-flow" class="tab-btn px-3.5 py-1.5 border border-amber-500/30 font-bold uppercase tracking-wider transition-all">
                [2] Flow Projection
            </button>
            <button onclick="switchTab('tab-calendar')" id="btn-tab-calendar" class="tab-btn px-3.5 py-1.5 border border-amber-500/30 font-bold uppercase tracking-wider transition-all">
                [3] Economic Calendar
            </button>
            <button onclick="switchTab('tab-sectors')" id="btn-tab-sectors" class="tab-btn px-3.5 py-1.5 border border-amber-500/30 font-bold uppercase tracking-wider transition-all">
                [4] US 11 Sectors
            </button>
            <button onclick="switchTab('tab-indonesia')" id="btn-tab-indonesia" class="tab-btn px-3.5 py-1.5 border border-amber-500/30 font-bold uppercase tracking-wider transition-all">
                [5] Indonesia & News Wire
            </button>
            <button onclick="switchTab('tab-whatsapp')" id="btn-tab-whatsapp" class="tab-btn px-3.5 py-1.5 border border-amber-500/30 font-bold uppercase tracking-wider transition-all text-emerald-400">
                [6] WhatsApp Dispatch
            </button>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-10">

        <!-- RETRO MEMORANDUM BANNER -->
        <section class="retro-card retro-double-border p-6 relative">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-4 border-b border-amber-500/20">
                <div class="space-y-1">
                    <div class="text-[10px] uppercase tracking-widest text-amber-500 font-bold flex items-center gap-2">
                        <span>[OFFICIAL MEMORANDUM · DESK COPY]</span>
                        <span>·</span>
                        <span class="text-zinc-400">{display_date}</span>
                    </div>
                    <h2 class="text-xl sm:text-2xl font-bold uppercase text-white font-headline">
                        REGIME: {regime['title']}
                    </h2>
                    <p class="text-xs text-zinc-300 max-w-3xl leading-relaxed font-typewriter">
                        {regime['summary']}
                    </p>
                </div>

                <!-- EWS VINTAGE TALLY GAUGE -->
                <div class="flex items-center gap-2 shrink-0 bg-terminal-950 p-3 border border-amber-500/40 font-mono text-center">
                    <div class="px-3 border-r border-amber-500/20">
                        <div class="text-xl font-bold text-rose-500">{regime['score_bahaya']}</div>
                        <div class="text-[9px] uppercase text-zinc-400 tracking-wider">Bahaya</div>
                    </div>
                    <div class="px-3 border-r border-amber-500/20">
                        <div class="text-xl font-bold text-amber-400">{regime['score_waspada']}</div>
                        <div class="text-[9px] uppercase text-zinc-400 tracking-wider">Waspada</div>
                    </div>
                    <div class="px-3">
                        <div class="text-xl font-bold text-emerald-400">{len(ews) - regime['score_bahaya'] - regime['score_waspada']}</div>
                        <div class="text-[9px] uppercase text-zinc-400 tracking-wider">Aman</div>
                    </div>
                </div>
            </div>

            <!-- 4-STEP RETRO TRANSMISSION WIRE -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 text-xs font-typewriter">
                <div class="p-3 bg-terminal-950 border border-amber-500/20 space-y-1">
                    <div class="text-[9px] text-amber-400 font-bold uppercase">[STEP 1 · PRIMARY CATALYST]</div>
                    <div class="text-zinc-200">US10Y ({prices.get('^TNX', {}).get('close', 0):.2f}%) & WTI (${prices.get('CL=F', {}).get('close', 0):.2f})</div>
                </div>
                <div class="p-3 bg-terminal-950 border border-amber-500/20 space-y-1">
                    <div class="text-[9px] text-amber-400 font-bold uppercase">[STEP 2 · CENTRAL BANK]</div>
                    <div class="text-zinc-200">Real Yields Elevated -> Rate Cuts Delayed</div>
                </div>
                <div class="p-3 bg-terminal-950 border border-amber-500/20 space-y-1">
                    <div class="text-[9px] text-amber-400 font-bold uppercase">[STEP 3 · SECTOR ROTATION]</div>
                    <div class="text-zinc-200">Capital rotates to {', '.join(regime['favored_sectors'][:2])}</div>
                </div>
                <div class="p-3 bg-terminal-950 border border-amber-500/20 space-y-1">
                    <div class="text-[9px] text-amber-400 font-bold uppercase">[STEP 4 · INDONESIA IMPACT]</div>
                    <div class="text-zinc-200">USD/IDR Rp {prices.get('USDIDR=X', {}).get('close', 0):,.0f} [{indo_macro.get('kurs_status', 'WASPADA')}]</div>
                </div>
            </div>
        </section>

        <!-- TAB 1: MAIN LEDGER (OVERVIEW) -->
        <div id="tab-overview" class="tab-pane space-y-8">
            
            <!-- 8 RETRO LEDGER TICKERS (LIVE AUTO-UPDATING) -->
            <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
                <div class="retro-card p-3 space-y-1" id="card-btc">
                    <div class="text-[10px] text-amber-400 uppercase">BITCOIN (BTC)</div>
                    <div class="text-base font-bold text-white font-mono" id="val-btc">${prices.get('BTC-USD', {}).get('close', 0):,.0f}</div>
                    <div class="text-[10px] {chg_color(prices.get('BTC-USD', {}).get('change_1d_pct', 0))}">
                        {prices.get('BTC-USD', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="retro-card p-3 space-y-1 border-amber-500/50 bg-amber-500/[0.04]">
                    <div class="text-[10px] text-amber-300 uppercase">EMAS (XAUUSD)</div>
                    <div class="text-base font-bold text-amber-200 font-mono">${prices.get('GC=F', {}).get('close', 0):,.1f}</div>
                    <div class="text-[10px] {chg_color(prices.get('GC=F', {}).get('change_1d_pct', 0))}">
                        {prices.get('GC=F', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="retro-card p-3 space-y-1 border-amber-500/50 bg-amber-500/[0.04]">
                    <div class="text-[10px] text-amber-300 uppercase">USD / IDR</div>
                    <div class="text-base font-bold text-amber-200 font-mono">Rp {prices.get('USDIDR=X', {}).get('close', 0):,.0f}</div>
                    <div class="text-[10px] {chg_color(prices.get('USDIDR=X', {}).get('change_1d_pct', 0))}">
                        {prices.get('USDIDR=X', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="retro-card p-3 space-y-1">
                    <div class="text-[10px] text-zinc-400 uppercase">S&P 500 (SPY)</div>
                    <div class="text-base font-bold text-white font-mono">${prices.get('SPY', {}).get('close', 0):.2f}</div>
                    <div class="text-[10px] {chg_color(prices.get('SPY', {}).get('change_1d_pct', 0))}">
                        {prices.get('SPY', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="retro-card p-3 space-y-1">
                    <div class="text-[10px] text-zinc-400 uppercase">US 10Y YIELD</div>
                    <div class="text-base font-bold text-white font-mono">{prices.get('^TNX', {}).get('close', 0):.3f}%</div>
                    <div class="text-[10px] text-zinc-400">Benchmark</div>
                </div>
                <div class="retro-card p-3 space-y-1">
                    <div class="text-[10px] text-zinc-400 uppercase">DOLLAR (DXY)</div>
                    <div class="text-base font-bold text-white font-mono">{prices.get('DX-Y.NYB', {}).get('close', 0):.2f}</div>
                    <div class="text-[10px] {chg_color(prices.get('DX-Y.NYB', {}).get('change_1d_pct', 0))}">
                        {prices.get('DX-Y.NYB', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="retro-card p-3 space-y-1">
                    <div class="text-[10px] text-zinc-400 uppercase">WTI CRUDE</div>
                    <div class="text-base font-bold text-white font-mono">${prices.get('CL=F', {}).get('close', 0):.2f}</div>
                    <div class="text-[10px] {chg_color(prices.get('CL=F', {}).get('change_1d_pct', 0))}">
                        {prices.get('CL=F', {}).get('change_1d_pct', 0):+.2f}% (1D)
                    </div>
                </div>
                <div class="retro-card p-3 space-y-1">
                    <div class="text-[10px] text-amber-400 uppercase">FED NET LIQ</div>
                    <div class="text-base font-bold text-amber-300 font-mono">${net_liq.get('net_liquidity_bil', 0):,.1f}B</div>
                    <div class="text-[10px] {chg_color(net_liq.get('change_4w_bil', 0))}">
                        {net_liq.get('change_4w_bil', 0):+.1f}B 4W
                    </div>
                </div>
            </div>

            <!-- DUAL RETRO LEDGER: EWS & CORRELATION -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                <!-- Early Warning Signals -->
                <div class="retro-card p-5 space-y-3">
                    <div class="flex items-center justify-between pb-2.5 border-b border-amber-500/20">
                        <h3 class="text-xs font-bold uppercase text-amber-400 tracking-wider">
                            ► EARLY WARNING SIGNALS (EWS)
                        </h3>
                        <span class="text-[10px] text-zinc-400 font-mono">10 GAUGES MONITORED</span>
                    </div>

                    <div class="space-y-2">
                        {"".join([f'''
                        <div class="p-2.5 bg-terminal-950 border border-amber-500/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <div class="space-y-0.5">
                                <div class="text-xs font-semibold text-zinc-200">{item['name']}</div>
                                <div class="text-[10px] text-zinc-400 font-typewriter">{item['context']}</div>
                            </div>
                            <div class="flex items-center gap-2.5 shrink-0 self-end sm:self-center font-mono">
                                <span class="text-xs font-bold text-white">{item['value']}</span>
                                {retro_badge(item['status'])}
                            </div>
                        </div>
                        ''' for item in ews])}
                    </div>
                </div>

                <!-- Cross-Asset Correlation Ledger -->
                <div class="retro-card p-5 space-y-3">
                    <div class="flex items-center justify-between pb-2.5 border-b border-amber-500/20">
                        <h3 class="text-xs font-bold uppercase text-amber-400 tracking-wider">
                            ► CROSS-ASSET CORRELATION MATRIX
                        </h3>
                        <span class="text-[10px] text-zinc-400 font-mono">ROLLING 30-DAY PEARSON R</span>
                    </div>

                    <div class="space-y-2">
                        {"".join([f'''
                        <div class="p-2.5 bg-terminal-950 border border-amber-500/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <div class="space-y-0.5">
                                <div class="text-xs font-semibold text-zinc-200">{c['pair_name']}</div>
                                <div class="text-[10px] text-zinc-400 font-typewriter">{c['notes']} (Norm: {c['expected_range']})</div>
                            </div>
                            <div class="flex items-center gap-2.5 shrink-0 self-end sm:self-center font-mono">
                                <span class="text-xs font-bold {chg_color(c['current_r'])}">{c['current_r']:+.2f}</span>
                                <span class="px-1.5 py-0.5 text-[9px] font-bold uppercase border {'border-rose-500 text-rose-400' if c['status'] == 'INVERT' else ('border-amber-500 text-amber-400' if c['status'] == 'BREAK' else 'border-emerald-500 text-emerald-400')}">[{c['status']}]</span>
                            </div>
                        </div>
                        ''' for c in corrs])}
                    </div>
                </div>

            </div>

        </div>

        <!-- TAB 2: FLOW PROJECTION (CAPITAL PATHS) -->
        <div id="tab-flow" class="tab-pane hidden space-y-6">
            <div class="retro-card p-6 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-amber-500 font-bold">[FORWARD LIQUIDITY VECTOR]</div>
                        <h3 class="text-lg font-headline font-bold text-white">Macro Capital Flow & Liquidity Projection</h3>
                        <p class="text-xs text-zinc-400 font-typewriter">Pemetaan jalur perpindahan likuiditas modal lintas aset 7 hingga 30 hari ke depan</p>
                    </div>
                    <span class="px-3 py-1 text-xs border border-amber-500/40 text-amber-400 font-mono">
                        Regime: {flow_proj.get('primary_flow_regime', 'ROTASI SIKLIKAL')}
                    </span>
                </div>

                <!-- 2-COL PIPELINE: INFLOWS VS DRAINAGE -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    <div class="p-4 bg-terminal-950 border border-emerald-500/30 space-y-3">
                        <div class="text-xs font-bold uppercase text-emerald-400 flex items-center gap-2 border-b border-emerald-500/20 pb-2">
                            <span>▲ TUJUAN ARUS MODAL MASUK (CAPITAL INFLOWS)</span>
                        </div>
                        <div class="space-y-2">
                            {"".join([f'''
                            <div class="p-3 bg-terminal-900 border border-emerald-500/10 space-y-1">
                                <div class="font-bold text-xs text-white">{inf['asset']}</div>
                                <div class="text-[11px] text-zinc-400 font-typewriter">{inf['rationale']}</div>
                            </div>
                            ''' for inf in flow_proj.get('inflows', [])])}
                        </div>
                    </div>

                    <div class="p-4 bg-terminal-950 border border-rose-500/30 space-y-3">
                        <div class="text-xs font-bold uppercase text-rose-400 flex items-center gap-2 border-b border-rose-500/20 pb-2">
                            <span>▼ SUMBER PENARIKAN LIKUIDITAS (CAPITAL DRAINAGE)</span>
                        </div>
                        <div class="space-y-2">
                            {"".join([f'''
                            <div class="p-3 bg-terminal-900 border border-rose-500/10 space-y-1">
                                <div class="font-bold text-xs text-white">{dr['asset']}</div>
                                <div class="text-[11px] text-zinc-400 font-typewriter">{dr['rationale']}</div>
                            </div>
                            ''' for dr in flow_proj.get('drainages', [])])}
                        </div>
                    </div>

                </div>

                <!-- 3-SCENARIO PROJECTION CARDS -->
                <div class="space-y-3 pt-4 border-t border-amber-500/20">
                    <div class="text-xs font-bold uppercase text-amber-400 tracking-wider">
                        ► 3 JALUR PROYEKSI TRAJEKTORI (7–30 HARI KE DEPAN):
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-4 bg-terminal-950 border border-amber-500/20 space-y-2.5">
                            <div class="flex items-center justify-between pb-2 border-b border-white/[0.06]">
                                <div class="font-bold text-sm text-amber-300">{scen['name']}</div>
                                <div class="px-2 py-0.5 text-xs font-bold border border-amber-500/40 text-amber-400">Probabilitas: {scen['prob']}</div>
                            </div>
                            <div class="text-[11px] text-zinc-300 font-typewriter"><b class="text-amber-400">Pemicu Kunci:</b> {scen['trigger']}</div>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px] font-typewriter pt-1">
                                <div class="p-2.5 bg-terminal-900 border border-white/5 space-y-1">
                                    <div class="text-[9px] uppercase font-bold text-cyan-400">Sektor US</div>
                                    <div class="text-zinc-300">{scen['us_sectors_path']}</div>
                                </div>
                                <div class="p-2.5 bg-terminal-900 border border-white/5 space-y-1">
                                    <div class="text-[9px] uppercase font-bold text-amber-400">Pasar Crypto</div>
                                    <div class="text-zinc-300">{scen['crypto_path']}</div>
                                </div>
                                <div class="p-2.5 bg-terminal-900 border border-white/5 space-y-1">
                                    <div class="text-[9px] uppercase font-bold text-emerald-400">Indonesia & Rupiah</div>
                                    <div class="text-zinc-300">{scen['indonesia_path']}</div>
                                </div>
                            </div>
                        </div>
                        ''' for scen in flow_proj.get('scenarios', [])])}
                    </div>
                </div>

            </div>
        </div>

        <!-- TAB 3: ECONOMIC CALENDAR (PEKAN INI & DAMPAK) -->
        <div id="tab-calendar" class="tab-pane hidden space-y-6">
            <div class="retro-card p-6 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-amber-500 font-bold">[ONE-WEEK MACRO HORIZON]</div>
                        <h3 class="text-lg font-headline font-bold text-white">Kalender Ekonomi Krusial Pekan Ini & Dampak Skenario</h3>
                        <p class="text-xs text-zinc-400 font-typewriter">Jadwal rilis data makro berbobot tinggi beserta transmisi skenario ke Sektor US, Crypto, & Rupiah</p>
                    </div>
                    <span class="px-3 py-1 text-xs border border-amber-500/40 text-amber-400 font-mono">
                        Timezone: Waktu Indonesia Barat (WIB)
                    </span>
                </div>

                <div class="space-y-4">
                    {"".join([f'''
                    <div class="p-4 bg-terminal-950 border border-amber-500/20 space-y-3 hover:border-amber-500/40 transition-all">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-white/[0.06]">
                            <div class="flex items-center gap-3">
                                <span class="px-2 py-0.5 text-xs font-bold border border-amber-500/40 text-amber-400 bg-amber-500/10 font-mono">{ev['country']}</span>
                                <span class="font-bold text-white text-sm">{ev['event']}</span>
                                <span class="text-[10px] font-mono font-semibold {'text-rose-400' if 'KRUSIAL' in ev['importance'] else 'text-amber-400'}">[{ev['importance']}]</span>
                            </div>
                            <div class="text-xs font-mono text-zinc-400">
                                📅 {ev['day']}, {ev['date']} · <b class="text-amber-300">{ev['time_wib']}</b>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-typewriter">
                            <div class="p-2.5 bg-terminal-900 border border-white/5 space-y-1">
                                <div class="text-[9px] uppercase font-bold text-zinc-400">Konsensus Pasar</div>
                                <div class="text-zinc-200">Sebelumnya: <b>{ev['prev']}</b> | Konsensus: <b class="text-amber-400">{ev['cons']}</b></div>
                            </div>
                            <div class="p-2.5 bg-terminal-900 border border-rose-500/20 space-y-1">
                                <div class="text-[9px] uppercase font-bold text-rose-400">Skenario Hot (> Konsensus)</div>
                                <div class="text-zinc-300 leading-relaxed text-[11px]">{ev['impact_hot']}</div>
                            </div>
                            <div class="p-2.5 bg-terminal-900 border border-emerald-500/20 space-y-1">
                                <div class="text-[9px] uppercase font-bold text-emerald-400">Skenario Cool (< Konsensus)</div>
                                <div class="text-zinc-300 leading-relaxed text-[11px]">{ev['impact_cool']}</div>
                            </div>
                        </div>

                        <div class="text-[11px] text-amber-300 font-mono pt-1 flex items-center gap-2">
                            <span class="text-zinc-400">Aset Prioritas Respon:</span>
                            <span class="border border-amber-500/30 px-2 py-0.5 bg-amber-500/5">{ev['favored_asset']}</span>
                        </div>
                    </div>
                    ''' for ev in weekly_cal])}
                </div>
            </div>
        </div>

        <!-- TAB 4: US 11 SECTORS LEDGER -->
        <div id="tab-sectors" class="tab-pane hidden space-y-6">
            <div class="retro-card p-6 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-amber-500 font-bold">[S&P 500 SELECT SECTOR SPDR]</div>
                        <h3 class="text-lg font-headline font-bold text-white">S&P 500 11 Sectors Momentum & Tactical Ledger</h3>
                        <p class="text-xs text-zinc-400 font-typewriter">Skor momentum berkala dan bobot alokasi taktis berbasis keselarasan siklus makro</p>
                    </div>
                    <div class="flex items-center gap-2 text-[10px] font-mono">
                        <span class="px-2 py-1 border border-emerald-500 text-emerald-400">[OW] OVERWEIGHT</span>
                        <span class="px-2 py-1 border border-zinc-600 text-zinc-400">[N] NEUTRAL</span>
                        <span class="px-2 py-1 border border-rose-500 text-rose-400">[UW] UNDERWEIGHT</span>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-mono">
                        <thead class="text-[10px] text-amber-400 uppercase tracking-wider border-b border-amber-500/30 bg-terminal-950">
                            <tr>
                                <th class="p-3 font-semibold">Ticker & Sektor</th>
                                <th class="p-3 font-semibold">Profil Karakter</th>
                                <th class="p-3 font-semibold text-right">Harga</th>
                                <th class="p-3 font-semibold text-right">1D %</th>
                                <th class="p-3 font-semibold text-right">5D %</th>
                                <th class="p-3 font-semibold text-right">20D %</th>
                                <th class="p-3 font-semibold text-right">Momentum</th>
                                <th class="p-3 font-semibold text-right">Rekomendasi</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-amber-500/10">
                            {"".join([f'''
                            <tr class="hover:bg-amber-500/[0.03] transition-colors">
                                <td class="p-3 font-bold text-white flex items-center gap-2">
                                    <span class="px-1.5 py-0.5 border border-amber-500/40 text-amber-400 text-xs font-bold">{s['ticker']}</span>
                                    <span class="text-zinc-200">{s['name']}</span>
                                </td>
                                <td class="p-3 text-zinc-400 font-typewriter text-[11px]">{s['profile']}</td>
                                <td class="p-3 text-right font-bold text-white">${s['close']:.2f}</td>
                                <td class="p-3 text-right {chg_color(s['chg_1d'])}">{s['chg_1d']:+.2f}%</td>
                                <td class="p-3 text-right {chg_color(s['chg_5d'])}">{s['chg_5d']:+.2f}%</td>
                                <td class="p-3 text-right {chg_color(s['chg_20d'])}">{s['chg_20d']:+.2f}%</td>
                                <td class="p-3 text-right font-bold text-white">{s['momentum_score']:+.2f}</td>
                                <td class="p-3 text-right">
                                    <span class="px-2 py-0.5 text-[10px] font-bold border {'border-emerald-500 text-emerald-400' if 'OVERWEIGHT' in s['recommendation'] else ('border-rose-500 text-rose-400' if 'UNDERWEIGHT' in s['recommendation'] else 'border-zinc-600 text-zinc-400')}">
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

        <!-- TAB 5: INDONESIA & NEWS WIRE -->
        <div id="tab-indonesia" class="tab-pane hidden space-y-8">
            
            <!-- Indonesia Macro Spillover Hero -->
            <div class="retro-card p-6 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-amber-500 font-bold">[DOMESTIC SOVEREIGN RADAR]</div>
                        <h3 class="text-lg font-headline font-bold text-white">Transmisi Makro Global ke Pasar Finansial Indonesia</h3>
                        <p class="text-xs text-zinc-400 font-typewriter">Saluran transmisi yield obligasi AS, Dolar DXY, dan Minyak terhadap ekonomi domestik</p>
                    </div>
                    <span class="px-3 py-1 text-xs border border-amber-500/40 text-amber-400 font-mono">
                        USD/IDR: Rp {prices.get('USDIDR=X', {}).get('close', 0):,.0f}
                    </span>
                </div>

                <!-- 4 Pillars Grid for Indonesia -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-terminal-950 p-4 border border-amber-500/20 space-y-2">
                        <div class="text-[10px] text-zinc-400 uppercase font-bold">Tekanan Nilai Tukar Rupiah</div>
                        <div class="font-mono text-sm font-bold text-white">USD/IDR Rp {prices.get('USDIDR=X', {}).get('close', 0):,.0f}</div>
                        <div>{retro_badge(indo_macro.get('kurs_status', 'WASPADA'))}</div>
                        <p class="text-[11px] text-zinc-400 font-typewriter">{indo_macro.get('kurs_desc', '')}</p>
                    </div>

                    <div class="bg-terminal-950 p-4 border border-amber-500/20 space-y-2">
                        <div class="text-[10px] text-zinc-400 uppercase font-bold">Sikap Bank Indonesia (BI-Rate)</div>
                        <div class="font-mono text-sm font-bold text-amber-400">Triple Intervention</div>
                        <div>{retro_badge(indo_macro.get('bi_status', 'HAWKISH'))}</div>
                        <p class="text-[11px] text-zinc-400 font-typewriter">{indo_macro.get('bi_desc', '')}</p>
                    </div>

                    <div class="bg-terminal-950 p-4 border border-amber-500/20 space-y-2">
                        <div class="text-[10px] text-zinc-400 uppercase font-bold">Beban Subsidi APBN (Energi)</div>
                        <div class="font-mono text-sm font-bold text-white">WTI ${prices.get('CL=F', {}).get('close', 0):.2f}/bbl</div>
                        <div>{retro_badge(indo_macro.get('apbn_status', 'BEBAN MENINGKAT'))}</div>
                        <p class="text-[11px] text-zinc-400 font-typewriter">{indo_macro.get('apbn_desc', '')}</p>
                    </div>

                    <div class="bg-terminal-950 p-4 border border-amber-500/20 space-y-2">
                        <div class="text-[10px] text-zinc-400 uppercase font-bold">Spillover IHSG (EIDO ETF)</div>
                        <div class="font-mono text-sm font-bold text-white">EIDO ${prices.get('EIDO', {}).get('close', 10.45):.2f}</div>
                        <div>{retro_badge(indo_macro.get('ihsg_status', 'RISK-OFF'))}</div>
                        <p class="text-[11px] text-zinc-400 font-typewriter">{indo_macro.get('ihsg_desc', '')}</p>
                    </div>
                </div>

                <div class="p-4 bg-terminal-950 border border-amber-500/20 space-y-1">
                    <div class="text-[10px] font-bold text-amber-400 uppercase tracking-wider">[SINTESIS TRANSMISI DOMESTIK]:</div>
                    <p class="text-xs text-zinc-300 font-typewriter leading-relaxed">{indo_macro.get('summary', '')}</p>
                </div>
            </div>

            <!-- 2-COL REAL VERIFIED NEWS WIRE -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                <!-- Global Macro Wire -->
                <div class="retro-card p-5 space-y-4">
                    <div class="flex items-center justify-between pb-2.5 border-b border-amber-500/20">
                        <h4 class="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                            <span>► GLOBAL MACRO TELETYPE WIRE (48 JAM)</span>
                        </h4>
                        <span class="text-[10px] text-zinc-400 font-mono">VERIFIED DISPATCH</span>
                    </div>

                    <div class="space-y-2.5">
                        {"".join([f'''
                        <div class="p-3 bg-terminal-950 border border-amber-500/10 space-y-1.5 hover:border-amber-500/40 transition-all">
                            <div class="flex items-center justify-between gap-2">
                                <span class="px-1.5 py-0.5 text-[9px] font-bold border border-amber-500/40 text-amber-400 font-mono">{n.get('source', 'Media')}</span>
                                <span class="text-[10px] text-zinc-500 font-mono">{n.get('pub_date', '')[:16]}</span>
                            </div>
                            <div class="text-xs font-semibold text-zinc-200 leading-snug">{n.get('title', '')}</div>
                            <div class="pt-1">
                                <a href="{n.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="text-[10px] font-mono text-amber-400 hover:underline">
                                    [BUKA SUMBER RESMI ↗]
                                </a>
                            </div>
                        </div>
                        ''' for n in global_news]) if global_news else '<div class="text-xs text-zinc-500 py-4">Belum ada transmisi kawat berita.</div>'}
                    </div>
                </div>

                <!-- Indonesia Financial Wire -->
                <div class="retro-card p-5 space-y-4">
                    <div class="flex items-center justify-between pb-2.5 border-b border-amber-500/20">
                        <h4 class="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                            <span>► INDONESIA FINANCIAL & MARKET WIRE</span>
                        </h4>
                        <span class="text-[10px] text-zinc-400 font-mono">IHSG, BI & RUPIAH</span>
                    </div>

                    <div class="space-y-2.5">
                        {"".join([f'''
                        <div class="p-3 bg-terminal-950 border border-emerald-500/10 space-y-1.5 hover:border-emerald-500/40 transition-all">
                            <div class="flex items-center justify-between gap-2">
                                <span class="px-1.5 py-0.5 text-[9px] font-bold border border-emerald-500/40 text-emerald-400 font-mono">{n.get('source', 'Media')}</span>
                                <span class="text-[10px] text-zinc-500 font-mono">{n.get('pub_date', '')[:16]}</span>
                            </div>
                            <div class="text-xs font-semibold text-zinc-200 leading-snug">{n.get('title', '')}</div>
                            <div class="pt-1">
                                <a href="{n.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="text-[10px] font-mono text-emerald-400 hover:underline">
                                    [BACA ARTIKEL ASLI ↗]
                                </a>
                            </div>
                        </div>
                        ''' for n in indonesia_news]) if indonesia_news else '<div class="text-xs text-zinc-500 py-4">Belum ada transmisi berita domestik.</div>'}
                    </div>
                </div>

            </div>

        </div>

        <!-- TAB 6: WHATSAPP DISPATCH -->
        <div id="tab-whatsapp" class="tab-pane hidden space-y-6">
            <div class="retro-card p-6 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-emerald-400 font-bold">[TELEGRAM & WHATSAPP WIRE]</div>
                        <h3 class="text-lg font-headline font-bold text-white">Investment Committee WhatsApp Dispatch</h3>
                        <p class="text-xs text-zinc-400 font-typewriter">Rantai kausalitas dan ringkasan kalender mingguan siap salin ke grup investor</p>
                    </div>
                    <button onclick="copyToClipboard()" id="copy-btn" class="px-4 py-2 border border-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs font-bold font-mono transition-all">
                        📋 COPY DISPATCH TO CLIPBOARD
                    </button>
                </div>

                <div class="relative">
                    <textarea id="wa-text" readonly rows="28" class="w-full bg-terminal-950 border border-amber-500/30 p-4 font-mono text-xs text-amber-200/90 leading-relaxed focus:outline-none focus:border-amber-400 resize-y">{whatsapp_text}</textarea>
                </div>
            </div>
        </div>

    </main>

    <!-- RETRO FOOTER -->
    <footer class="max-w-7xl mx-auto px-4 sm:px-8 py-8 border-t border-amber-500/30 text-center text-[10px] text-zinc-500 font-mono">
        ★ MACRO PULSE FINANCIAL TERMINAL · POINT-IN-TIME SURVEILLANCE ENGINE · NEW YORK · JAKARTA · LONDON ★
    </footer>

    <!-- INTERACTIVE SCRIPTS: TABS, LIVE CLOCK & REAL-TIME WEBSOCKET/API POLLING -->
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
            btn.innerHTML = "✅ DISPATCH COPIED!";
            btn.classList.add("bg-emerald-500", "text-black");
            
            setTimeout(() => {{
                btn.innerHTML = originalText;
                btn.classList.remove("bg-emerald-500", "text-black");
            }}, 2500);
        }}

        // DUAL LIVE CLOCK ENGINE (WIB & EST)
        function updateClocks() {{
            const now = new Date();
            
            // WIB (UTC+7)
            const wibString = now.toLocaleTimeString('en-GB', {{ timeZone: 'Asia/Jakarta' }});
            const clockWib = document.getElementById('clock-wib');
            if (clockWib) clockWib.innerText = wibString + ' WIB';

            // EST (America/New_York)
            const estString = now.toLocaleTimeString('en-US', {{ timeZone: 'America/New_York', hour12: false }});
            const clockEst = document.getElementById('clock-est');
            if (clockEst) clockEst.innerText = estString + ' EST';

            // Market status check (NYSE 09:30 - 16:00 EST on weekdays)
            const estHour = parseInt(estString.split(':')[0], 10);
            const estMin = parseInt(estString.split(':')[1], 10);
            const estDay = now.getDay();
            const isOpen = (estDay >= 1 && estDay <= 5) && (estHour > 9 || (estHour === 9 && estMin >= 30)) && (estHour < 16);
            
            const badge = document.getElementById('market-status-badge');
            if (badge) {{
                badge.innerText = isOpen ? '[NYSE: OPEN 🟢]' : '[NYSE: CLOSED 🔴]';
                badge.className = isOpen ? 'text-emerald-400 font-bold' : 'text-zinc-500';
            }}
        }}
        setInterval(updateClocks, 1000);
        updateClocks();

        // REAL-TIME CLIENT-SIDE PRICE STREAMER (BINANCE PUBLIC API)
        let lastPrices = {{ btc: 0, eth: 0, sol: 0 }};

        async function fetchLiveCryptoPrices() {{
            try {{
                const res = await fetch('https://api.binance.com/api/v3/ticker/price?symbols=["BTCUSDT","ETHUSDT","SOLUSDT"]');
                if (res.ok) {{
                    const data = await res.json();
                    data.forEach(item => {{
                        const price = parseFloat(item.price);
                        if (item.symbol === 'BTCUSDT') {{
                            const el = document.getElementById('val-btc');
                            const tape = document.getElementById('live-tape-btc');
                            const card = document.getElementById('card-btc');
                            if (el) el.innerText = '$' + price.toLocaleString('en-US', {{ maximumFractionDigits: 0 }});
                            if (tape) tape.innerText = '$' + price.toLocaleString('en-US', {{ maximumFractionDigits: 0 }});
                            if (lastPrices.btc > 0 && card) {{
                                card.classList.remove('ticker-flash-up', 'ticker-flash-down');
                                void card.offsetWidth; // trigger reflow
                                card.classList.add(price >= lastPrices.btc ? 'ticker-flash-up' : 'ticker-flash-down');
                            }}
                            lastPrices.btc = price;
                        }} else if (item.symbol === 'ETHUSDT') {{
                            const tape = document.getElementById('live-tape-eth');
                            if (tape) tape.innerText = '$' + price.toLocaleString('en-US', {{ maximumFractionDigits: 0 }});
                            lastPrices.eth = price;
                        }} else if (item.symbol === 'SOLUSDT') {{
                            const tape = document.getElementById('live-tape-sol');
                            if (tape) tape.innerText = '$' + price.toFixed(2);
                            lastPrices.sol = price;
                        }}
                    }});
                }}
            }} catch (e) {{
                // Fallback silently if offline or blocked
            }}
        }}

        // Poll live price every 10 seconds for real-time live trading desk feel!
        setInterval(fetchLiveCryptoPrices, 10000);
        fetchLiveCryptoPrices();
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Rendered Retro Classic report to {output_path}")
    
    # Also write to index.html for instant root localhost:8080 viewing and github pages deployment
    index_path = os.path.join(os.path.dirname(os.path.abspath(output_path)), "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return os.path.abspath(output_path)

if __name__ == "__main__":
    from data_fetcher import get_latest_snapshot
    from analytics_engine import evaluate_ews, classify_macro_regime, compute_correlation_matrix, compute_sector_scorecard, compute_crypto_scorecard, load_price_history, analyze_indonesia_macro_sentiment
    from calendar_engine import get_weekly_economic_calendar, compute_macro_flow_projections
    from narrative_generator import generate_report_payload
    
    snapshot = get_latest_snapshot()
    price_df = load_price_history()
    ews = evaluate_ews(snapshot)
    regime = classify_macro_regime(snapshot, ews)
    corrs = compute_correlation_matrix(price_df)
    sectors = compute_sector_scorecard(snapshot, regime)
    crypto_data, eth_btc = compute_crypto_scorecard(snapshot)
    indo_macro = analyze_indonesia_macro_sentiment(snapshot, ews, regime)
    
    weekly_cal = get_weekly_economic_calendar()
    flow_proj = compute_macro_flow_projections(snapshot, regime, ews)
    
    payload = generate_report_payload(snapshot, ews, regime, corrs, sectors, crypto_data, eth_btc, indo_macro, weekly_cal, flow_proj)
    path = render_html_report(payload)
    print("HTML Generator verified:", path)
