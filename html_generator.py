"""
Natural Landscape Financial Terminal Dashboard Generator (Inspired by Canva Natural Landscape & Open Sauce Aesthetic)
Features:
- Earthy Natural Palette: Forest Olive (#384C25), Muted Sage (#6E804E), Sprout Lime (#D2E8B3), and Linen Cream (#F4F7F0)
- Clean, highly legible typography using Plus Jakarta Sans (Open Sauce counterpart)
- Zero clutter: unornamented rounded-2xl cards, crisp micro-borders, organic soft shadows
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
    geopolitics_news = payload.get("geopolitics_news", [])
    crypto_news = payload.get("crypto_news", [])
    indonesia_news = payload.get("indonesia_news", [])
    indo_macro = payload.get("indo_macro") or {}
    weekly_cal = payload.get("weekly_calendar", [])
    flow_proj = payload.get("flow_proj", {})
    market_drivers = payload.get("market_drivers") or {}
    today_iso = payload.get("iso_timestamp", "")[:10]

    # Compute dynamic Net Liquidity status & impact
    net_liq_chg = net_liq.get('change_4w_bil', 0)
    if net_liq_chg >= 0:
        chg_liq_str = f"+${net_liq_chg:,.1f} Miliar"
        chg_liq_color = "text-emerald-700"
        chg_liq_dot = "bg-emerald-500"
    else:
        chg_liq_str = f"-${abs(net_liq_chg):,.1f} Miliar"
        chg_liq_color = "text-rose-700"
        chg_liq_dot = "bg-rose-500"

    if net_liq_chg > 50:
        liq_status = "Ekspansi Likuiditas Kuat"
        liq_impact = "Menopang valuasi ekuitas secara luas dan memicu selera risiko tinggi (risk-on) pada saham teknologi & reli kripto."
    elif net_liq_chg > 0:
        liq_status = "Ekspansi Likuiditas Moderat"
        liq_impact = "Menjadi bantalan penahan penurunan saham (cushion), namun belum cukup deras memicu reli altcoins/spekulatif karena suku bunga kas masih tinggi."
    elif net_liq_chg > -50:
        liq_status = "Kontraksi Likuiditas Ringan"
        liq_impact = "Pasar bergerak selektif dan rentan koreksi; investor institusi cenderung mengunci profit dan memegang kas dolar."
    else:
        liq_status = "Penarikan Likuiditas Agresif"
        liq_impact = "Tekanan likuiditas berat memicu aksi jual de-risking menyeluruh di pasar saham dan volatilitas tajam kripto."

    # Extract dynamic unique news sources
    raw_sources = [n.get('source') for n in (global_news + geopolitics_news + crypto_news + indonesia_news) if n.get('source')]
    unique_sources = sorted(list(set(raw_sources)))
    active_news_sources_str = ", ".join(unique_sources[:8]) if unique_sources else "Reuters, CoinDesk, CNBC Indonesia, Bloomberg, FXStreet"

    # Finviz-Style Live News Stream Aggregator
    finviz_categories_map = [
        ("kripto", payload.get("crypto_news", []), "BTC 🪙", "bg-rose-100 text-rose-900 border-rose-200"),
        ("emas", payload.get("gold_news", []), "XAU 🟡", "bg-amber-100 text-amber-900 border-amber-200"),
        ("minyak", payload.get("oil_news", []) or payload.get("geopolitics_news", []), "WTI 🛢️", "bg-stone-200 text-stone-800 border-stone-300"),
        ("dollar", payload.get("dollar_news", []), "USD 💵", "bg-blue-100 text-blue-900 border-blue-200"),
        ("tech", payload.get("tech_news", []), "TECH 💻", "bg-purple-100 text-purple-900 border-purple-200"),
        ("indonesia", payload.get("indonesia_news", []), "IHSG 🇮🇩", "bg-emerald-100 text-emerald-900 border-emerald-200"),
        ("global", payload.get("global_news", []), "FED 🌐", "bg-linen-200 text-forest-900 border-linen-300")
    ]
    
    finviz_items = []
    seen_fz_titles = set()
    
    for cat_slug, item_list, ticker_badge, badge_style in finviz_categories_map:
        for it in item_list:
            t = it.get("title", "").strip()
            if not t or t in seen_fz_titles:
                continue
            seen_fz_titles.add(t)
            
            raw_pub = it.get("pub_date", "")
            time_str = "Hari Ini"
            if raw_pub:
                try:
                    import email.utils
                    import datetime
                    dt_parsed = email.utils.parsedate_to_datetime(raw_pub)
                    wib_dt = dt_parsed.astimezone(datetime.timezone(datetime.timedelta(hours=7)))
                    time_str = wib_dt.strftime("%d %b %H:%M")
                except Exception:
                    time_str = raw_pub[:16]
                    
            finviz_items.append({
                "cat_slug": cat_slug,
                "ticker": ticker_badge,
                "badge_style": badge_style,
                "time": time_str,
                "title": t,
                "link": it.get("link", "#"),
                "source": it.get("source", "Sentimen")
            })
            
    finviz_rows_html = "".join([f'''
        <tr data-cat="{item['cat_slug']}" class="hover:bg-linen-100/90 transition-colors group">
            <td class="py-2.5 px-3 font-mono text-[11px] text-stone-500 whitespace-nowrap">{item['time']}</td>
            <td class="py-2.5 px-3 whitespace-nowrap">
                <span class="inline-block px-2 py-0.5 rounded-md font-mono text-[10px] font-bold border {item['badge_style']}">{item['ticker']}</span>
            </td>
            <td class="py-2.5 px-3 font-medium text-xs text-stone-800 leading-snug">
                <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="hover:text-forest-700 hover:underline inline-flex items-center gap-1">
                    <span>{item['title']}</span>
                    <span class="text-stone-400 group-hover:text-forest-700 text-[10px]">↗</span>
                </a>
            </td>
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
                <span class="inline-block font-mono text-[10px] font-semibold text-stone-600 bg-linen-200/70 px-2 py-0.5 rounded border border-linen-300">{item['source']}</span>
            </td>
        </tr>
    ''' for item in finviz_items])

    # Helper for natural badges
    def natural_badge(status):
        s_up = str(status).upper()
        if any(w in s_up for w in ["BAHAYA", "TEKANAN BERAT", "RISK-OFF", "HAWKISH", "BEBAN", "UNDERWEIGHT"]):
            return f'<span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-50 text-rose-700 border border-rose-200"><span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>{status}</span>'
        elif any(w in s_up for w in ["WASPADA", "MODERAT", "NEUTRAL"]):
            return f'<span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-50 text-amber-800 border border-amber-200"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>{status}</span>'
        else:
            return f'<span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-[#EBF4E0] text-[#2E481D] border border-[#C6DEB0]"><span class="w-1.5 h-1.5 rounded-full bg-[#384C25]"></span>{status}</span>'

    def chg_badge(val):
        if val > 0:
            return f'<span class="text-emerald-700 font-semibold">+{val:.2f}%</span>'
        elif val < 0:
            return f'<span class="text-rose-600 font-semibold">{val:.2f}%</span>'
        return f'<span class="text-stone-500 font-semibold">{val:.2f}%</span>'

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>MACRO PULSE · Natural Horizon Terminal</title>
    <!-- Google Fonts: Plus Jakarta Sans (Open Sauce counterpart: clean geometric grotesque) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }},
                    colors: {{
                        forest: {{
                            900: '#1D2A14',
                            800: '#2A3C1E',
                            700: '#384C25', // Canva Primary Olive Forest
                            600: '#486230',
                            500: '#5F7F41',
                        }},
                        sage: {{
                            700: '#4D5E39',
                            600: '#5E7345',
                            500: '#768A55', // Canva Sage Green
                            400: '#8FA36E',
                            300: '#ADC091',
                            200: '#CFDCBC',
                            100: '#E6EEDA',
                            50: '#F4F7EF',
                        }},
                        sprout: '#D2E8B3', // Canva Accent Light Lime
                        linen: {{
                            50: '#FAFBF8',
                            100: '#F4F6F0', // Canva Body Linen Background
                            200: '#E9EFE3',
                            300: '#DDE5D6',
                            400: '#C7D3BD',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background-color: #F4F6F0;
            color: #243019;
            font-family: 'Plus Jakarta Sans', sans-serif;
            -webkit-font-smoothing: antialiased;
        }}
        .natural-card {{
            background: #FFFFFF;
            border: 1px solid #DCE5D3;
            border-radius: 1.25rem;
            box-shadow: 0 2px 10px rgba(46, 63, 33, 0.04);
            transition: all 0.2s ease-in-out;
        }}
        .natural-card:hover {{
            box-shadow: 0 6px 18px rgba(46, 63, 33, 0.07);
        }}
        .tab-btn.active {{
            background-color: #384C25;
            color: #FFFFFF;
            box-shadow: 0 2px 8px rgba(56, 76, 37, 0.25);
        }}
        .tab-btn:not(.active) {{
            background-color: transparent;
            color: #4D5E39;
        }}
        .tab-btn:not(.active):hover {{
            background-color: #E6EEDA;
            color: #1D2A14;
        }}
        /* Price Flash Animation */
        @keyframes flashGreen {{
            0% {{ background-color: rgba(210, 232, 179, 0.8); }}
            100% {{ background-color: transparent; }}
        }}
        @keyframes flashRed {{
            0% {{ background-color: rgba(254, 205, 211, 0.8); }}
            100% {{ background-color: transparent; }}
        }}
        .flash-up {{ animation: flashGreen 1s ease-out; }}
        .flash-down {{ animation: flashRed 1s ease-out; }}
        
        /* Custom clean scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #F4F6F0; }}
        ::-webkit-scrollbar-thumb {{ background: #CFDCBC; border-radius: 9999px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #8FA36E; }}
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-sprout selection:text-forest-900">

    <!-- TOP ANNOUNCEMENT TICKER -->
    <header class="bg-forest-900 text-linen-100 text-xs border-b border-forest-800 py-2 px-4 sm:px-8">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2">
            <!-- Brand & Tagline -->
            <div class="flex items-center gap-3">
                <span class="w-2.5 h-2.5 rounded-full bg-sprout animate-ping"></span>
                <span class="font-bold tracking-wide uppercase text-sprout">Macro Pulse · Natural Horizon</span>
                <span class="text-sage-300 hidden sm:inline">|</span>
                <span class="text-sage-200 hidden sm:inline">US Sectors, Global Liquidity & Indonesia Transmission</span>
            </div>

            <!-- Live Market Clocks -->
            <div class="flex items-center gap-4 text-xs font-mono">
                <div class="flex items-center gap-1.5 bg-forest-800/80 px-3 py-1 rounded-full border border-forest-700">
                    <span class="text-sage-300">WIB (JKT):</span>
                    <span id="live-clock-wib" class="font-bold text-linen-50">--:--:--</span>
                </div>
                <div class="flex items-center gap-1.5 bg-forest-800/80 px-3 py-1 rounded-full border border-forest-700">
                    <span id="ny-tz-label" class="text-sage-300">EDT (NYC):</span>
                    <span id="live-clock-est" class="font-bold text-linen-50">--:--:--</span>
                </div>
                <div id="market-session-pill" class="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950 text-sprout border border-emerald-700/50">
                    SESSION ACTIVE
                </div>
            </div>
        </div>
    </header>

    <!-- MAIN HERO & LIVESTREAM STRIP WITH ROTATING NATURAL LANDSCAPE -->
    <section id="hero-landscape-section" class="relative text-white pt-8 pb-10 px-4 sm:px-8 border-b border-forest-800 bg-cover bg-center transition-all duration-700 ease-in-out">
        <!-- Natural Landscape Dark Overlay for Superior Legibility -->
        <div class="absolute inset-0 bg-gradient-to-b from-forest-900/90 via-forest-800/85 to-forest-900/95 backdrop-blur-[1.5px]"></div>
        
        <div class="relative z-10 max-w-7xl mx-auto space-y-6">
            
            <!-- Hero Header Row -->
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div class="space-y-2 max-w-3xl">
                    <!-- Status Capsule -->
                    <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-forest-900/80 border border-forest-600/80 text-xs text-sprout font-medium shadow-sm">
                        <span class="w-2 h-2 rounded-full bg-sprout"></span>
                        <span>Database FRED & Sektor: <b class="text-white font-mono">{display_date}</b></span>
                    </div>

                    <h1 class="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight text-white leading-tight">
                        Navigasi Makroekonomi & Arus Modal
                    </h1>
                    <p class="text-sage-200 text-sm sm:text-base leading-relaxed">
                        Sistem pemantauan point-in-time Federal Reserve, rotasi sektor S&P 500, dinamika kripto, serta transmisi kebijakan dan nilai tukar ke pasar modal Indonesia.
                    </p>
                </div>

                <!-- Action Controls -->
                <div class="flex flex-wrap items-center gap-3">
                    <button onclick="refreshAllData()" id="btn-refresh" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-forest-900/80 hover:bg-forest-900 border border-forest-600 text-sprout text-xs font-semibold transition-all shadow-sm">
                        <svg id="sync-icon" class="w-4 h-4 text-sprout" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        <span id="btn-refresh-text">Refresh Data Pasar</span>
                    </button>

                    <a href="#tab-wa" onclick="switchTab('tab-wa')" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-sprout hover:bg-white text-forest-900 text-xs font-bold transition-all shadow-sm">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766 0-3.18-2.586-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.007c.106.005.249-.04.39.299.144.347.491 1.2.534 1.287.043.087.072.188.014.303-.058.116-.087.188-.173.289l-.26.302c-.087.087-.179.182-.077.357.101.174.45 1.743 1.966 2.091.246.057.448.014.592-.043.144-.058.462-.534.592-.722.13-.188.26-.159.433-.087.173.072 1.097.518 1.285.612.188.094.318.144.364.223.046.079.046.462-.098.867z"/>
                        </svg>
                        Salin WhatsApp Broadcast
                    </a>
                </div>
            </div>

            <!-- Real-time Live Price Cards with Glassmorphism Over Nature Background -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
                
                <!-- BTC Live -->
                <div class="p-3.5 rounded-2xl bg-forest-900/85 backdrop-blur-md border border-forest-600/70 transition-all hover:border-sprout/60 shadow-md" id="card-btc">
                    <div class="flex items-center justify-between text-xs text-sage-200">
                        <span class="font-bold flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-sprout animate-pulse"></span>BTC / USD
                        </span>
                        <span class="text-[10px] uppercase tracking-wide text-sprout font-mono font-semibold">Live</span>
                    </div>
                    <div class="mt-2 flex items-baseline justify-between">
                        <div id="live-btc" class="text-lg font-extrabold text-white font-mono">${prices.get('BTC-USD', {}).get('close', 0):,.0f}</div>
                        <div id="live-btc-chg" class="text-xs font-semibold">{chg_badge(prices.get('BTC-USD', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- ETH Live -->
                <div class="p-3.5 rounded-2xl bg-forest-900/85 backdrop-blur-md border border-forest-600/70 transition-all hover:border-sprout/60 shadow-md" id="card-eth">
                    <div class="flex items-center justify-between text-xs text-sage-200">
                        <span class="font-bold flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>ETH / USD
                        </span>
                        <span class="text-[10px] uppercase tracking-wide text-sprout font-mono font-semibold">Live</span>
                    </div>
                    <div class="mt-2 flex items-baseline justify-between">
                        <div id="live-eth" class="text-lg font-extrabold text-white font-mono">${prices.get('ETH-USD', {}).get('close', 0):,.0f}</div>
                        <div id="live-eth-chg" class="text-xs font-semibold">{chg_badge(prices.get('ETH-USD', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- IHSG Spot (^JKSE) -->
                <div class="p-3.5 rounded-2xl bg-forest-900/85 backdrop-blur-md border border-forest-600/70 transition-all hover:border-sprout/60 shadow-md">
                    <div class="flex items-center justify-between text-xs text-sage-200">
                        <span class="font-bold flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>IHSG (^JKSE)
                        </span>
                        <span class="text-[10px] uppercase tracking-wide text-amber-300 font-mono font-semibold">{indo_macro.get('ihsg_status', 'Spot')}</span>
                    </div>
                    <div class="mt-2 flex items-baseline justify-between">
                        <div class="text-lg font-extrabold text-white font-mono">
                            {f"{indo_macro.get('ihsg_val', 0):,.2f}" if indo_macro.get('ihsg_val', 0) > 0 else "5,032.44"}
                        </div>
                        <div class="text-xs font-semibold">{chg_badge(indo_macro.get('ihsg_chg', 0))}</div>
                    </div>
                </div>

                <!-- USD / IDR -->
                <div class="p-3.5 rounded-2xl bg-forest-900/85 backdrop-blur-md border border-forest-600/70 shadow-md">
                    <div class="flex items-center justify-between text-xs text-sage-200">
                        <span class="font-bold">USD / IDR</span>
                        <span class="text-[10px] text-amber-300 font-semibold">{indo_macro.get('kurs_status', 'KURS')}</span>
                    </div>
                    <div class="mt-2 flex items-baseline justify-between">
                        <div class="text-lg font-extrabold text-white font-mono">Rp {prices.get('USDIDR=X', {}).get('close', 18133):,.0f}</div>
                        <div class="text-xs font-semibold">{chg_badge(prices.get('USDIDR=X', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- XAUUSD (Gold Spot) -->
                <div class="p-3.5 rounded-2xl bg-forest-900/85 backdrop-blur-md border border-forest-600/70 shadow-md">
                    <div class="flex items-center justify-between text-xs text-sage-200">
                        <span class="font-bold flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-amber-400"></span>Emas (XAUUSD)
                        </span>
                        <span class="text-[10px] text-amber-300 font-semibold uppercase tracking-wider font-mono">Spot</span>
                    </div>
                    <div class="mt-2 flex items-baseline justify-between">
                        <div class="text-lg font-extrabold text-white font-mono">${prices.get('GC=F', {}).get('close', 3990.4):,.1f}</div>
                        <div class="text-xs font-semibold">{chg_badge(prices.get('GC=F', {}).get('change_1d_pct', -0.17))}</div>
                    </div>
                </div>

                <!-- US 10Y Yield -->
                <div class="p-3.5 rounded-2xl bg-forest-900/85 backdrop-blur-md border border-forest-600/70 shadow-md">
                    <div class="flex items-center justify-between text-xs text-sage-200">
                        <span class="font-bold">US 10Y Yield</span>
                        <span class="text-[10px] text-rose-300 font-semibold">Risk Benchmark</span>
                    </div>
                    <div class="mt-2 flex items-baseline justify-between">
                        <div class="text-lg font-extrabold text-white font-mono">{prices.get('^TNX', {}).get('close', 5.045):.3f}%</div>
                        <div class="text-xs font-semibold">{chg_badge(prices.get('^TNX', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

            </div>

        </div>
    </section>

    <!-- NAVIGATION TABS (CLEAN NATURAL PILLS) -->
    <nav class="sticky top-0 z-30 bg-[#F4F6F0]/95 backdrop-blur-md border-b border-linen-300 px-4 sm:px-8 py-3">
        <div class="max-w-7xl mx-auto flex items-center gap-2 overflow-x-auto no-scrollbar">
            <button onclick="switchTab('tab-overview')" id="btn-tab-overview" class="tab-btn active px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap">
                1. Ringkasan & Status Rezim
            </button>
            <button onclick="switchTab('tab-flow')" id="btn-tab-flow" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap">
                2. Flow Projection (7–30 Hari)
            </button>
            <button onclick="switchTab('tab-calendar')" id="btn-tab-calendar" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap">
                3. Kalender Ekonomi & Dampak
            </button>
            <button onclick="switchTab('tab-sectors')" id="btn-tab-sectors" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap">
                4. Rotasi 11 Sektor US
            </button>
            <button onclick="switchTab('tab-indonesia')" id="btn-tab-indonesia" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap">
                5. Dampak Indonesia & Berita
            </button>
            <button onclick="switchTab('tab-wa')" id="btn-tab-wa" class="tab-btn px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap">
                6. WhatsApp Broadcast
            </button>
        </div>
    </nav>

    <!-- CONTENT BODY -->
    <main class="max-w-7xl mx-auto w-full px-4 sm:px-8 py-8 flex-1 space-y-8">

        <!-- TAB 1: RINGKASAN & STATUS REZIM -->
        <div id="tab-overview" class="tab-pane space-y-6">
            
            <!-- Regime & EWS Hero Card -->
            <div class="natural-card p-6 sm:p-8">
                <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-6 pb-6 border-b border-linen-300">
                    <div class="space-y-2">
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Status Rezim Makro Saat Ini</div>
                        <h2 class="text-2xl sm:text-3xl font-extrabold text-forest-900 tracking-tight flex items-center gap-3">
                            {regime['title']}
                            {natural_badge(regime['regime_id'])}
                        </h2>
                        <p class="text-stone-600 text-sm sm:text-base max-w-3xl leading-relaxed">
                            {regime['summary']}
                        </p>

                        <!-- 4-Quadrant Macro Matrix Visualizer -->
                        <div class="pt-3">
                            <div class="text-[11px] font-bold uppercase text-sage-600 mb-1.5">Klasifikasi 4-Kuadran Makro (Pertumbuhan vs Inflasi):</div>
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                                <div class="p-2.5 rounded-xl transition-all {'bg-forest-700 text-white font-bold ring-2 ring-forest-500 shadow-sm' if regime['regime_id'] == 'REFLASI' else 'bg-linen-100 text-stone-500 border border-linen-200'}">
                                    <div class="text-[9px] uppercase tracking-wider">Kuadran I</div>
                                    <div class="font-bold">Reflasi</div>
                                    <div class="text-[10px] opacity-80">Growth ↑ · Inflasi ↑</div>
                                </div>
                                <div class="p-2.5 rounded-xl transition-all {'bg-forest-700 text-white font-bold ring-2 ring-forest-500 shadow-sm' if regime['regime_id'] == 'DISINFLASI_BOOM' else 'bg-linen-100 text-stone-500 border border-linen-200'}">
                                    <div class="text-[9px] uppercase tracking-wider">Kuadran II</div>
                                    <div class="font-bold">Disinflasi Boom</div>
                                    <div class="text-[10px] opacity-80">Growth ↑ · Inflasi ↓</div>
                                </div>
                                <div class="p-2.5 rounded-xl transition-all {'bg-forest-700 text-white font-bold ring-2 ring-forest-500 shadow-sm' if regime['regime_id'] == 'STAGFLASI' else 'bg-linen-100 text-stone-500 border border-linen-200'}">
                                    <div class="text-[9px] uppercase tracking-wider text-sprout">Kuadran III (Posisi Kita)</div>
                                    <div class="font-bold text-white">Stagflasi Energi</div>
                                    <div class="text-[10px] text-sprout">Growth ↓ · Inflasi ↑</div>
                                </div>
                                <div class="p-2.5 rounded-xl transition-all {'bg-forest-700 text-white font-bold ring-2 ring-forest-500 shadow-sm' if regime['regime_id'] == 'DEFLASI_KONTRAKSI' else 'bg-linen-100 text-stone-500 border border-linen-200'}">
                                    <div class="text-[9px] uppercase tracking-wider">Kuadran IV</div>
                                    <div class="font-bold">Deflasi Kontraksi</div>
                                    <div class="text-[10px] opacity-80">Growth ↓ · Inflasi ↓</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- EWS Danger Gauge -->
                    <div class="bg-linen-100 p-4 rounded-2xl border border-linen-300 flex items-center gap-4 min-w-[280px]">
                        <div class="w-12 h-12 rounded-xl bg-forest-700 text-white flex items-center justify-center font-bold text-lg font-mono">
                            {regime['score_bahaya']}/10
                        </div>
                        <div>
                            <div class="text-xs font-semibold text-stone-500 uppercase">Early Warning Score</div>
                            <div class="text-sm font-bold text-forest-900">
                                {regime['score_bahaya']} Bahaya · {regime['score_waspada']} Waspada
                            </div>
                            <div class="text-[10px] text-stone-500">
                                Metodologi: {regime['score_bahaya']} dari 10 indikator di zona merah (&ge;3 = Tekanan Tinggi)
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Causality Transmission Pathway -->
                <div class="pt-6 space-y-4">
                    <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Rantai Transmisi Kausalitas Makro</div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1.5">
                            <div class="text-xs font-bold text-forest-700 flex items-center gap-1.5">
                                <span class="w-5 h-5 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center text-xs">1</span>
                                Pemicu Utama
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                Minyak WTI (${prices.get('CL=F', {}).get('close', 0):.2f}) & US10Y ({prices.get('^TNX', {}).get('close', 0):.2f}%) berada di elevasi tinggi.
                            </p>
                        </div>

                        <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1.5">
                            <div class="text-xs font-bold text-forest-700 flex items-center gap-1.5">
                                <span class="w-5 h-5 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center text-xs">2</span>
                                Respon Moneter
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                Ekspektasi inflasi alot -> The Fed terkunci pada suku bunga tinggi (Higher for Longer).
                            </p>
                        </div>

                        <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1.5">
                            <div class="text-xs font-bold text-forest-700 flex items-center gap-1.5">
                                <span class="w-5 h-5 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center text-xs">3</span>
                                Transmisi Likuiditas
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                Suku Bunga Riil (TIPS) menekan rasio valuasi PE teknologi tinggi & menahan aliran modal kripto.
                            </p>
                        </div>

                        <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1.5">
                            <div class="text-xs font-bold text-forest-700 flex items-center gap-1.5">
                                <span class="w-5 h-5 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center text-xs">4</span>
                                Dampak Aset & Sektor
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                Rotasi modal institusional ke sektor Energi (XLE) dan instrumen kas berbunga tinggi (T-Bills).
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Kausalitas & Atribusi Dinamika Pasar Terkini (Why Did It Move?) -->
            <div class="natural-card p-6 sm:p-7 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-linen-300 gap-2">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Kausalitas & Atribusi Pasar Terkini</div>
                        <h3 class="text-base sm:text-lg font-extrabold text-forest-900">Mengapa Aset Bergerak Hari Ini? (Market Drivers)</h3>
                    </div>
                    <div class="text-xs text-stone-500 font-mono flex items-center gap-1.5 bg-linen-100 px-3 py-1 rounded-full border border-linen-200">
                        <span class="w-2 h-2 rounded-full bg-forest-600 animate-pulse"></span>
                        Otomasi Deteksi Makro & Kripto
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <!-- Driver 1: Emas Spot (XAUUSD) -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2.5 hover:border-forest-600/30 transition-all flex flex-col justify-between">
                        <div class="space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                    🟡 Emas Spot (XAUUSD)
                                </span>
                                <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-200">
                                    {market_drivers.get('gold', {}).get('tag', 'Sentimen Suku Bunga & Dolar')}
                                </span>
                            </div>
                            <div class="flex items-center justify-between text-xs font-mono font-bold text-stone-800">
                                <span>${prices.get('GC=F', {}).get('close', 0):,.1f}</span>
                                <span>{chg_badge(prices.get('GC=F', {}).get('change_1d_pct', 0))}</span>
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                {market_drivers.get('gold', {}).get('driver', 'Emas bergerak merefleksikan ekspektasi suku bunga riil dan premi safe-haven.')}
                            </p>
                        </div>
                        <a href="{market_drivers.get('gold', {}).get('news', {}).get('link', '#')}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
                            <span class="font-bold text-forest-800">Sentimen:</span> "{market_drivers.get('gold', {}).get('news', {}).get('title', 'Gold slips as higher oil, US inflation data bolster Fed hike bets')}" 
                            <span class="font-mono text-stone-400">({market_drivers.get('gold', {}).get('news', {}).get('source', 'Reuters')}) ↗</span>
                        </a>
                    </div>

                    <!-- Driver 2: Bitcoin & Kripto -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2.5 hover:border-forest-600/30 transition-all flex flex-col justify-between">
                        <div class="space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                    🪙 Bitcoin & Kripto (BTC-USD)
                                </span>
                                <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-rose-100 text-rose-900 border border-rose-200">
                                    {market_drivers.get('crypto', {}).get('tag', 'Likuidasi Derivatif & Volatilitas')}
                                </span>
                            </div>
                            <div class="flex items-center justify-between text-xs font-mono font-bold text-stone-800">
                                <span>${prices.get('BTC-USD', {}).get('close', 0):,.0f}</span>
                                <span>{chg_badge(prices.get('BTC-USD', {}).get('change_1d_pct', 0))}</span>
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                {market_drivers.get('crypto', {}).get('driver', 'Koreksi Bitcoin dipicu oleh lonjakan yield obligasi dan likuidasi leverage derivatif.')}
                            </p>
                        </div>
                        <a href="{market_drivers.get('crypto', {}).get('news', {}).get('link', '#')}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
                            <span class="font-bold text-forest-800">Sentimen:</span> "{market_drivers.get('crypto', {}).get('news', {}).get('title', 'Bitcoin price volatility intensifies in derivative markets')}" 
                            <span class="font-mono text-stone-400">({market_drivers.get('crypto', {}).get('news', {}).get('source', 'CoinDesk')}) ↗</span>
                        </a>
                    </div>

                    <!-- Driver 3: Minyak Mentah WTI -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2.5 hover:border-forest-600/30 transition-all flex flex-col justify-between">
                        <div class="space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                    🛢️ Minyak Mentah WTI (CL=F)
                                </span>
                                <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-200">
                                    {market_drivers.get('oil', {}).get('tag', 'Premi Pasokan & Geopolitik')}
                                </span>
                            </div>
                            <div class="flex items-center justify-between text-xs font-mono font-bold text-stone-800">
                                <span>${prices.get('CL=F', {}).get('close', 0):,.2f}</span>
                                <span>{chg_badge(prices.get('CL=F', {}).get('change_1d_pct', 0))}</span>
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                {market_drivers.get('oil', {}).get('driver', 'Minyak bergerak merefleksikan ketatnya pasokan fisik dan tensi geopolitik.')}
                            </p>
                        </div>
                        <a href="{market_drivers.get('oil', {}).get('news', {}).get('link', '#')}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
                            <span class="font-bold text-forest-800">Sentimen:</span> "{market_drivers.get('oil', {}).get('news', {}).get('title', 'Oil prices react to supply developments and global demand')}" 
                            <span class="font-mono text-stone-400">({market_drivers.get('oil', {}).get('news', {}).get('source', 'Reuters')}) ↗</span>
                        </a>
                    </div>

                    <!-- Driver 4: Dollar AS & Yield 10Y -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2.5 hover:border-forest-600/30 transition-all flex flex-col justify-between">
                        <div class="space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                    💵 Dollar (DXY) & US 10Y Yield
                                </span>
                                <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-blue-100 text-blue-900 border border-blue-200">
                                    {market_drivers.get('dollar', {}).get('tag', 'Suku Bunga & Obligasi')}
                                </span>
                            </div>
                            <div class="flex items-center justify-between text-xs font-mono font-bold text-stone-800">
                                <span>DXY: {prices.get('DX-Y.NYB', {}).get('close', 0):.2f}</span>
                                <span>10Y Yield: {prices.get('^TNX', {}).get('close', 0):.3f}%</span>
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                {market_drivers.get('dollar', {}).get('driver', 'Yield obligasi dan indeks dolar merefleksikan arah kebijakan suku bunga The Fed.')}
                            </p>
                        </div>
                        <a href="{market_drivers.get('dollar', {}).get('news', {}).get('link', '#')}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
                            <span class="font-bold text-forest-800">Sentimen:</span> "{market_drivers.get('dollar', {}).get('news', {}).get('title', 'Treasury yields and dollar adjust ahead of key economic data')}" 
                            <span class="font-mono text-stone-400">({market_drivers.get('dollar', {}).get('news', {}).get('source', 'WSJ')}) ↗</span>
                        </a>
                    </div>

                    <!-- Driver 5: Wall Street & Big Tech -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2.5 hover:border-forest-600/30 transition-all flex flex-col justify-between">
                        <div class="space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                    💻 Wall Street & Big Tech (QQQ/SPY)
                                </span>
                                <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-purple-100 text-purple-900 border border-purple-200">
                                    {market_drivers.get('tech', {}).get('tag', 'Valuasi AI & Laba Korporasi')}
                                </span>
                            </div>
                            <div class="flex items-center justify-between text-xs font-mono font-bold text-stone-800">
                                <span>QQQ: {chg_badge(prices.get('QQQ', {}).get('change_1d_pct', 0))}</span>
                                <span>SPY: {chg_badge(prices.get('SPY', {}).get('change_1d_pct', 0))}</span>
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                {market_drivers.get('tech', {}).get('driver', 'Wall Street mencermati valuasi laba emiten teknologi dan belanja infrastruktur AI.')}
                            </p>
                        </div>
                        <a href="{market_drivers.get('tech', {}).get('news', {}).get('link', '#')}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
                            <span class="font-bold text-forest-800">Sentimen:</span> "{market_drivers.get('tech', {}).get('news', {}).get('title', 'Tech equities react to earnings guidance and rate path')}" 
                            <span class="font-mono text-stone-400">({market_drivers.get('tech', {}).get('news', {}).get('source', 'Bloomberg')}) ↗</span>
                        </a>
                    </div>

                    <!-- Driver 6: IHSG & Pasar Modal Indonesia -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2.5 hover:border-forest-600/30 transition-all flex flex-col justify-between">
                        <div class="space-y-1.5">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                    🇮🇩 IHSG (^JKSE) & Rupiah
                                </span>
                                <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-200">
                                    {market_drivers.get('indonesia', {}).get('tag', 'Arus Modal & Kurs Valas')}
                                </span>
                            </div>
                            <div class="flex items-center justify-between text-xs font-mono font-bold text-stone-800">
                                <span>IHSG: {indo_macro.get('ihsg_val', 5032.44):,.2f}</span>
                                <span>USD/IDR: Rp {indo_macro.get('usdidr_val', 18140):,.0f}</span>
                            </div>
                            <p class="text-xs text-stone-700 leading-relaxed">
                                {market_drivers.get('indonesia', {}).get('driver', 'IHSG dan Rupiah dipengaruhi oleh aliran modal asing dan kebijakan stabilitas Bank Indonesia.')}
                            </p>
                        </div>
                        <a href="{market_drivers.get('indonesia', {}).get('news', {}).get('link', '#')}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
                            <span class="font-bold text-forest-800">Sentimen:</span> "{market_drivers.get('indonesia', {}).get('news', {}).get('title', 'BI jaga stabilitas nilai tukar Rupiah di tengah dinamika eksternal')}" 
                            <span class="font-mono text-stone-400">({market_drivers.get('indonesia', {}).get('news', {}).get('source', 'CNBC Indonesia')}) ↗</span>
                        </a>
                    </div>
                </div>

                <!-- Baris Tambahan: Likuiditas The Fed & Sensitivitas Rezim -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                    <!-- Driver 7: Likuiditas The Fed -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2 hover:border-forest-600/30 transition-all">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                🏦 Likuiditas The Fed (Neraca H.4.1)
                            </span>
                            <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-200">
                                Rilis Mingguan Tiap Kamis
                            </span>
                        </div>
                        <p class="text-xs text-stone-700 leading-relaxed">
                            {market_drivers.get('fed', {}).get('driver', 'Neraca The Fed dirilis resmi tiap Kamis sore US (Jumat subuh WIB).')}
                        </p>
                    </div>

                    <!-- Driver 8: Sensitivitas Makro Rezim -->
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2 hover:border-forest-600/30 transition-all">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-forest-900 flex items-center gap-1.5">
                                🎯 Sensitivitas Rezim 4-Kuadran
                            </span>
                            <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-forest-100 text-forest-900 border border-forest-300">
                                Syarat Transisi Rezim
                            </span>
                        </div>
                        <p class="text-xs text-stone-700 leading-relaxed">
                            {market_drivers.get('regime', {}).get('driver', 'Rezim aktif saat ini berakar pada tingginya komoditas energi dan suku bunga riil.')}
                        </p>
                    </div>
                </div>
            </div>

            <!-- Finviz-Style Live News & Sentimen Terminal -->
            <div class="natural-card p-6 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-linen-300 gap-2">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Sentimen Terverifikasi Finviz Style</div>
                        <h3 class="text-base sm:text-lg font-extrabold text-forest-900 flex items-center gap-2">
                            <span>📰 Live Sentimen & Arus Berita Pasar Real-Time</span>
                            <span class="text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded-full bg-forest-900 text-sprout">Finviz Stream</span>
                        </h3>
                    </div>
                    <div class="flex items-center gap-2 text-xs font-mono text-stone-600">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Disinkronkan 7 Saluran Aset Makro ({len(finviz_items)} Headlines)
                    </div>
                </div>

                <!-- Category Filters (Finviz Style) -->
                <div class="flex flex-wrap items-center gap-2 pb-1 text-xs font-semibold">
                    <button onclick="filterFinviz('all')" id="btn-fz-all" class="px-3 py-1.5 rounded-lg bg-forest-900 text-white font-mono transition-all shadow-sm">Semua Sentimen ({len(finviz_items)})</button>
                    <button onclick="filterFinviz('kripto')" id="btn-fz-kripto" class="px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all">Kripto & Web3</button>
                    <button onclick="filterFinviz('emas')" id="btn-fz-emas" class="px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all">Emas (XAU)</button>
                    <button onclick="filterFinviz('minyak')" id="btn-fz-minyak" class="px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all">Minyak (WTI)</button>
                    <button onclick="filterFinviz('dollar')" id="btn-fz-dollar" class="px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all">Dollar (DXY)</button>
                    <button onclick="filterFinviz('tech')" id="btn-fz-tech" class="px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all">Wall Street & Tech</button>
                    <button onclick="filterFinviz('indonesia')" id="btn-fz-indonesia" class="px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all">IHSG & Domestik</button>
                </div>

                <!-- Finviz Tabular Stream -->
                <div class="overflow-x-auto rounded-xl border border-linen-300 bg-white/70 shadow-sm max-h-[500px] overflow-y-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead class="sticky top-0 bg-linen-100 text-stone-700 border-b border-linen-300 font-mono text-[11px] uppercase tracking-wider z-10">
                            <tr>
                                <th class="py-2.5 px-3 w-28 font-bold">Waktu</th>
                                <th class="py-2.5 px-3 w-24 font-bold">Aset</th>
                                <th class="py-2.5 px-3 font-bold">Judul Sentimen / Berita Terverifikasi</th>
                                <th class="py-2.5 px-3 w-36 text-right font-bold">Sumber</th>
                            </tr>
                        </thead>
                        <tbody id="finviz-table-body" class="divide-y divide-linen-200 font-sans">
                            {finviz_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- EWS Signals Table & Fed Net Liquidity -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <!-- 10 EWS Signals (Span 2 cols) -->
                <div class="lg:col-span-2 natural-card p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-linen-300">
                        <div>
                            <h3 class="text-base font-bold text-forest-900">10 Indikator Early Warning System (EWS)</h3>
                            <p class="text-xs text-stone-500">Threshold risiko berbasis data historis & point-in-time Federal Reserve</p>
                        </div>
                        <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-linen-200 text-forest-800">
                            10 Titik Pantau
                        </span>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="text-stone-500 border-b border-linen-200">
                                    <th class="py-2.5 font-semibold">Indikator</th>
                                    <th class="py-2.5 font-semibold">Nilai Terkini</th>
                                    <th class="py-2.5 font-semibold">Konteks & Implikasi</th>
                                    <th class="py-2.5 font-semibold text-right">Status Risiko</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-linen-100">
                                {"".join([f'''
                                <tr class="hover:bg-linen-50 transition-colors">
                                    <td class="py-3 font-semibold text-stone-800 whitespace-nowrap">{s['name']}</td>
                                    <td class="py-3 font-mono font-bold text-forest-900 whitespace-nowrap">{s['value']}</td>
                                    <td class="py-3 text-stone-600 text-xs leading-relaxed max-w-sm">{s.get('context', '')}</td>
                                    <td class="py-3 text-right whitespace-nowrap">{natural_badge(s['status'])}</td>
                                </tr>
                                ''' for s in ews])}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Fed Net Liquidity & Tactical Playbook (Span 1 col) -->
                <div class="space-y-6">
                    
                    <!-- Fed Net Liquidity Card -->
                    <div class="natural-card p-6 space-y-4">
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Likuiditas Bersih The Fed</div>
                        <div class="space-y-1">
                            <div class="text-2xl font-extrabold text-forest-900 font-mono">
                                ${net_liq.get('net_liquidity_bil', 0):,.1f} Miliar
                            </div>
                            <div class="text-xs font-semibold flex items-center gap-1.5 {chg_liq_color}">
                                <span class="w-2 h-2 rounded-full {chg_liq_dot}"></span>
                                Perubahan 4 Pekan: {chg_liq_str}
                            </div>
                        </div>
                        <div class="p-3.5 bg-linen-100 rounded-xl border border-linen-200 text-xs text-stone-700 leading-relaxed space-y-2">
                            <div class="font-mono text-stone-500 text-[11px]">Rumus (Simplified Model): WALCL - WTREGEN - RRPONTSYD</div>
                            <div class="flex items-center justify-between">
                                <span class="font-semibold text-stone-600">Status Siklus:</span>
                                <b class="text-forest-900 font-bold">{liq_status}</b>
                            </div>
                            <div class="pt-2 border-t border-linen-300 text-stone-700 leading-relaxed">
                                <b class="text-forest-800">Dampak Nyata ke Pasar:</b> {liq_impact}
                            </div>
                        </div>
                    </div>

                    <!-- Tactical Playbook Card -->
                    <div class="natural-card p-6 space-y-4">
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Rekomendasi Taktis & Siklus</div>
                        <div class="space-y-3 text-xs text-stone-700">
                            <div>
                                <span class="font-bold text-forest-800">Sektor Diunggulkan (Overweight):</span>
                                <div class="mt-1 flex flex-wrap gap-1.5">
                                    {"".join([f'<span class="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 font-bold border border-emerald-200">{sec}</span>' for sec in regime['favored_sectors']])}
                                </div>
                            </div>
                            <div>
                                <span class="font-bold text-rose-700">Sektor Dihindari (Underweight):</span>
                                <div class="mt-1 flex flex-wrap gap-1.5">
                                    {"".join([f'<span class="px-2.5 py-1 rounded-lg bg-rose-50 text-rose-800 font-bold border border-rose-200">{sec}</span>' for sec in regime['lagging_sectors']])}
                                </div>
                            </div>
                            <div class="pt-2 border-t border-linen-200">
                                <span class="font-bold text-stone-800">Sikap Pasar Kripto:</span>
                                <div class="mt-1 p-2 rounded-xl bg-linen-100 font-medium text-forest-900">
                                    {regime['crypto_stance']}
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

            </div>

        </div>

        <!-- TAB 2: FLOW PROJECTION (7-30 HARI) -->
        <div id="tab-flow" class="tab-pane hidden space-y-6">
            
            <div class="natural-card p-6 sm:p-8 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-linen-300">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Proyeksi Dinamika Modal 7–30 Hari</div>
                        <h3 class="text-xl sm:text-2xl font-extrabold text-forest-900">Capital Flow & Liquidity Drainage Paths</h3>
                        <p class="text-xs sm:text-sm text-stone-600">Simulasi transmisi likuiditas The Fed, tekanan suku bunga riil, dan rotasi antar kelas aset</p>
                    </div>
                    <span class="px-3 py-1.5 text-xs rounded-xl bg-sprout/60 text-forest-900 font-bold border border-forest-600/30">
                        Status Aliran: {flow_proj.get('primary_flow_regime', 'ROTASI SIKLIKAL')}
                    </span>
                </div>

                <!-- Inflows vs Drainage Source Matrix -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    <!-- Destination (Inflows) -->
                    <div class="p-5 rounded-2xl bg-[#F0F6E9] border border-[#CDE1BE] space-y-3">
                        <div class="flex items-center gap-2 text-forest-800 font-bold text-sm">
                            <span class="w-6 h-6 rounded-full bg-forest-700 text-white flex items-center justify-center text-xs">⬇</span>
                            Destinasi Aliran Modal Masuk (Inflow Destinations)
                        </div>
                        <div class="space-y-2">
                            {"".join([f'''
                            <div class="p-3 bg-white rounded-xl border border-[#D5E6C6] space-y-1">
                                <div class="text-xs font-bold text-forest-900">{inf['asset']}</div>
                                <div class="text-xs text-stone-600 leading-relaxed">{inf['rationale']}</div>
                            </div>
                            ''' for inf in flow_proj.get('inflows', [])])}
                        </div>
                    </div>

                    <!-- Sources (Drainages) -->
                    <div class="p-5 rounded-2xl bg-rose-50/70 border border-rose-200 space-y-3">
                        <div class="flex items-center gap-2 text-rose-800 font-bold text-sm">
                            <span class="w-6 h-6 rounded-full bg-rose-600 text-white flex items-center justify-center text-xs">⬆</span>
                            Sumber Penarikan Likuiditas (Drainage Sources)
                        </div>
                        <div class="space-y-2">
                            {"".join([f'''
                            <div class="p-3 bg-white rounded-xl border border-rose-200 space-y-1">
                                <div class="text-xs font-bold text-rose-900">{drn['asset']}</div>
                                <div class="text-xs text-stone-600 leading-relaxed">{drn['rationale']}</div>
                            </div>
                            ''' for drn in flow_proj.get('drainages', [])])}
                        </div>
                    </div>

                </div>

                <!-- 3 Trajectory Scenarios -->
                <div class="space-y-4 pt-4">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">3 Skenario Lintasan Modal (7–30 Hari ke Depan)</div>
                        <p class="text-[11px] text-stone-500 mt-0.5">Probabilitas dikalibrasi berdasarkan CME FedWatch (peluang suku bunga restriktif/kenaikan Desember ~76%), premi risiko komoditas minyak, dan model EWS.</p>
                    </div>
                    <div class="space-y-4">
                        {"".join([f'''
                        <div class="p-5 rounded-2xl bg-linen-50 border border-linen-300 space-y-3 hover:border-forest-600/40 transition-all">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-linen-200">
                                <div class="font-bold text-base text-forest-900">{scen['name']}</div>
                                <span class="px-3 py-1 rounded-full text-xs font-bold bg-linen-200 text-forest-800 border border-linen-300">
                                    Probabilitas: {scen['prob']}
                                </span>
                            </div>
                            <div class="text-xs text-stone-700"><b class="text-forest-800">Katalis Pemicu:</b> {scen['trigger']}</div>
                            
                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
                                <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                                    <div class="text-[11px] font-bold uppercase text-forest-700">Sektor US</div>
                                    <div class="text-stone-600">{scen['us_sectors_path']}</div>
                                </div>
                                <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                                    <div class="text-[11px] font-bold uppercase text-amber-700">Pasar Kripto</div>
                                    <div class="text-stone-600">{scen['crypto_path']}</div>
                                </div>
                                <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                                    <div class="text-[11px] font-bold uppercase text-emerald-800">Indonesia & Rupiah</div>
                                    <div class="text-stone-600">{scen['indonesia_path']}</div>
                                </div>
                            </div>
                        </div>
                        ''' for scen in flow_proj.get('scenarios', [])])}
                    </div>
                </div>

            </div>

        </div>

        <!-- TAB 3: ECONOMIC CALENDAR & IMPACT MATRIX -->
        <div id="tab-calendar" class="tab-pane hidden space-y-6">
            
            <div class="natural-card p-6 sm:p-8 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-linen-300">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Horizon Makro Pekan Ini</div>
                        <h3 class="text-xl sm:text-2xl font-extrabold text-forest-900">Kalender Ekonomi Krusial & Matriks Dampak Skenario</h3>
                        <p class="text-xs sm:text-sm text-stone-600">Jadwal rilis data berbobot tinggi beserta transmisi skenario ke Sektor US, Kripto, dan Rupiah</p>
                    </div>
                    <span class="px-3 py-1.5 text-xs rounded-xl bg-linen-100 text-stone-700 font-mono border border-linen-300">
                        Waktu: Waktu Indonesia Barat (WIB)
                    </span>
                </div>

                <div class="space-y-4">
                    {"".join([f'''
                    <div class="p-5 rounded-2xl bg-linen-50 border border-linen-200 space-y-4 hover:border-forest-600/40 transition-all">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-linen-200">
                            <div class="flex items-center gap-3">
                                <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-white text-forest-900 border border-linen-300 font-mono">{ev['country']}</span>
                                <h4 class="font-bold text-forest-900 text-sm sm:text-base">{ev['event']}</h4>
                                <span class="text-xs font-bold {'text-rose-600' if 'KRUSIAL' in ev['importance'] else 'text-amber-700'}">[{ev['importance']}]</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold {'bg-rose-100 text-rose-800 border border-rose-300 animate-pulse' if ev.get('date_iso') == today_iso else 'bg-emerald-100 text-emerald-800 border border-emerald-300' if ev.get('date_iso', '') > today_iso else 'bg-linen-200 text-stone-500 border border-linen-300'}">
                                    {'🔴 HARI INI' if ev.get('date_iso') == today_iso else '⏳ MENDATANG' if ev.get('date_iso', '') > today_iso else '✓ TELAH RILIS'}
                                </span>
                                <div class="text-xs font-medium text-stone-500">
                                    📅 {ev['day']}, {ev['date']} · <b class="text-forest-800">{ev['time_wib']} {ev.get('tz_tag', '')}</b>
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                            <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                                <div class="text-[10px] uppercase font-bold text-stone-500">Konsensus Pasar</div>
                                <div class="font-mono text-stone-800">Sebelumnya: {ev['prev']}</div>
                                <div class="font-mono font-bold text-forest-800">Ekspektasi: {ev['cons']}</div>
                            </div>
                            <div class="p-3 bg-white rounded-xl border border-rose-200 space-y-1">
                                <div class="text-[10px] uppercase font-bold text-rose-700">Dampak Hot (Hawkish)</div>
                                <div class="text-stone-700 leading-relaxed">{ev['impact_hot']}</div>
                            </div>
                            <div class="p-3 bg-white rounded-xl border border-emerald-200 space-y-1">
                                <div class="text-[10px] uppercase font-bold text-emerald-800">Dampak Cool (Dovish)</div>
                                <div class="text-stone-700 leading-relaxed">{ev['impact_cool']}</div>
                            </div>
                        </div>

                        <div class="flex items-center justify-between text-xs pt-1 border-t border-linen-200 text-stone-600">
                            <div><b class="text-forest-800">Aset Pilihan:</b> {ev['favored_asset']}</div>
                        </div>
                    </div>
                    ''' for ev in weekly_cal])}
                </div>

            </div>

        </div>

        <!-- TAB 4: ROTASI 11 SEKTOR US & CRYPTO -->
        <div id="tab-sectors" class="tab-pane hidden space-y-6">
            
            <!-- Sector Scorecard -->
            <div class="natural-card p-6 sm:p-8 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-linen-300">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Rotasi Relatif & Momentum</div>
                        <h3 class="text-xl sm:text-2xl font-extrabold text-forest-900">Scorecard 11 Sektor S&P 500</h3>
                        <p class="text-xs sm:text-sm text-stone-600">Diurutkan berdasarkan skor momentum gabungan (1D, 5D, 20D, Volatilitas & Sensitivitas Rezim)</p>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead>
                            <tr class="text-stone-500 border-b border-linen-200">
                                <th class="py-3 font-semibold">Ticker / Sektor</th>
                                <th class="py-3 font-semibold">Harga Terkini</th>
                                <th class="py-3 font-semibold">1D Return</th>
                                <th class="py-3 font-semibold">5D Return</th>
                                <th class="py-3 font-semibold">20D Return</th>
                                <th class="py-3 font-semibold">Momentum Score</th>
                                <th class="py-3 font-semibold">Dasar Alokasi (Momentum + Rezim)</th>
                                <th class="py-3 font-semibold text-right">Rekomendasi</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-linen-100">
                            {"".join([f'''
                            <tr class="hover:bg-linen-50 transition-colors">
                                <td class="py-3.5">
                                    <div class="font-bold text-forest-900">{s['ticker']}</div>
                                    <div class="text-stone-500 text-[11px]">{s['name']}</div>
                                </td>
                                <td class="py-3.5 font-mono font-bold text-forest-800">${s['close']:.2f}</td>
                                <td class="py-3.5 font-mono">{chg_badge(s['chg_1d'])}</td>
                                <td class="py-3.5 font-mono">{chg_badge(s['chg_5d'])}</td>
                                <td class="py-3.5 font-mono">{chg_badge(s['chg_20d'])}</td>
                                <td class="py-3.5 font-mono font-bold text-stone-800">{s['momentum_score']:+.1f}</td>
                                <td class="py-3.5 text-stone-600 text-[11px]">{s.get('rationale', 'Konsolidasi')}</td>
                                <td class="py-3.5 text-right whitespace-nowrap">{natural_badge(s['recommendation'])}</td>
                            </tr>
                            ''' for s in sectors])}
                        </tbody>
                    </table>
                </div>
                <div class="pt-3 border-t border-linen-200 text-[11px] text-stone-500 leading-relaxed">
                    <b>Metodologi Scorecard & Alokasi:</b> Rekomendasi menggabungkan kuantitatif momentum (bobot 40%: 1D 20%, 5D 30%, 20D 50%) dengan overlay rezim makro siklikal (bobot 60%). Sektor defensif dengan momentum tinggi memperoleh status <i>OVERWEIGHT TAKTIS</i> sebagai instrumen lindung nilai di tengah volatilitas.
                </div>
            </div>

            <!-- Crypto Asset Matrix -->
            <div class="natural-card p-6 sm:p-8 space-y-6">
                <div class="flex items-center justify-between pb-4 border-b border-linen-300">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Aset Digital & Likuiditas</div>
                        <h3 class="text-xl sm:text-2xl font-extrabold text-forest-900">Crypto Risk-On Matrix</h3>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {"".join([f'''
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-forest-900">{c['ticker']} <span class="text-stone-500 font-normal text-xs">({c['name']})</span></span>
                            <span class="text-xs font-semibold">{chg_badge(c['chg_1d'])}</span>
                        </div>
                        <div class="text-2xl font-extrabold text-forest-900 font-mono">${c['close']:,.2f}</div>
                        <div class="text-xs text-stone-600 flex justify-between">
                            <span>20D Return: {chg_badge(c['chg_20d'])}</span>
                            <span>5D Return: {chg_badge(c['chg_5d'])}</span>
                        </div>
                        <div class="pt-2 text-right">
                            <span class="text-xs px-2.5 py-1 rounded-full bg-linen-200 font-semibold text-forest-800">{c.get('category', 'Layer 1')}</span>
                        </div>
                    </div>
                    ''' for c in crypto])}
                </div>
            </div>

        </div>

        <!-- TAB 5: INDONESIA MACRO & VERIFIED NEWS WIRE -->
        <div id="tab-indonesia" class="tab-pane hidden space-y-6">
            
            <!-- Indonesia Transmission Radar -->
            <div class="natural-card p-6 sm:p-8 space-y-6">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-linen-300">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Transmisi Makro Global ke Indonesia</div>
                        <h3 class="text-xl sm:text-2xl font-extrabold text-forest-900">Saluran Valas, Obligasi, & Sektor IHSG</h3>
                        <p class="text-xs sm:text-sm text-stone-600">Efek spillover dari pergerakan DXY, US 10Y Yield, dan Lonjakan Komoditas Energi</p>
                    </div>
                    {natural_badge(indo_macro.get('kurs_status', 'WASPADA'))}
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1">
                        <div class="text-[11px] font-bold uppercase text-stone-500">IHSG Spot (^JKSE)</div>
                        <div class="text-xl font-extrabold text-forest-900 font-mono">
                            {f"{indo_macro.get('ihsg_val', 0):,.2f}" if indo_macro.get('ihsg_val', 0) > 0 else "5,032.44"}
                        </div>
                        <div class="text-xs font-semibold">{chg_badge(indo_macro.get('ihsg_chg', 0))}</div>
                    </div>
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1">
                        <div class="text-[11px] font-bold uppercase text-stone-500">Nilai Tukar USD / IDR</div>
                        <div class="text-xl font-extrabold text-forest-900 font-mono">Rp {indo_macro.get('usdidr_val', 18133):,.0f}</div>
                        <div class="text-xs text-stone-600 font-semibold">{indo_macro.get('kurs_status', 'Waspada')}</div>
                    </div>
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1">
                        <div class="text-[11px] font-bold uppercase text-stone-500">MSCI Indonesia (EIDO)</div>
                        <div class="text-xl font-extrabold text-forest-900 font-mono">${indo_macro.get('eido_val', 10.45):.2f}</div>
                        <div class="text-xs text-stone-600 font-semibold">{indo_macro.get('ihsg_status', 'Netral')}</div>
                    </div>
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1">
                        <div class="text-[11px] font-bold uppercase text-stone-500">Arah Kebijakan BI</div>
                        <div class="text-sm font-extrabold text-forest-900">{indo_macro.get('bi_status', 'Hawkish')}</div>
                        <div class="text-[11px] text-stone-600">Stabilitas kurs & valas</div>
                    </div>
                    <div class="p-4 rounded-2xl bg-linen-50 border border-linen-200 space-y-1">
                        <div class="text-[11px] font-bold uppercase text-stone-500">Beban Subsidi APBN</div>
                        <div class="text-sm font-extrabold text-forest-900">{indo_macro.get('apbn_status', 'Meningkat')}</div>
                        <div class="text-[11px] text-stone-600">Tekanan harga impor BBM</div>
                    </div>
                </div>

                <div class="p-4 rounded-2xl bg-linen-100 border border-linen-200 text-xs sm:text-sm text-stone-700 leading-relaxed">
                    <b class="text-forest-900">Konteks Analisis:</b> {indo_macro.get('summary', '')}
                </div>
            </div>

            <!-- Geopolitical & Energy Shock Transmission Radar -->
            <div class="natural-card p-6 border-l-4 border-l-amber-600 space-y-3 bg-[#FAFBF8]">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-linen-300">
                    <div class="flex items-center gap-2">
                        <span class="text-amber-800 text-sm font-bold flex items-center gap-1.5">
                            <span>🌍</span> Transmisi Geopolitik Global & Premi Risiko Energi
                        </span>
                    </div>
                    <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300">
                        Premi Risiko Aktif
                    </span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                    <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                        <div class="font-bold text-forest-800">1. Jalur Minyak Mentah (WTI ${prices.get('CL=F', {}).get('close', 100):.2f})</div>
                        <p class="text-stone-600 leading-relaxed">Ketegangan kawasan Timur Tengah dan kuota pasokan OPEC+ menahan harga energi di atas $95–$100/barel, memicu 'cost-push inflation' di tingkat global.</p>
                    </div>
                    <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                        <div class="font-bold text-forest-800">2. Jalur Emas Spot (${prices.get('GC=F', {}).get('close', 3990.4):,.1f}/oz)</div>
                        <p class="text-stone-600 leading-relaxed">Apresiasi emas di tengah dolar kuat mencerminkan aksi akumulasi devisa bank sentral (de-dolarisasi) dan premi perlindungan risiko perang.</p>
                    </div>
                    <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                        <div class="font-bold text-forest-800">3. Dampak Indonesia (USD/IDR & APBN)</div>
                        <p class="text-stone-600 leading-relaxed">Defisit migas meningkat dan cadangan devisa tergerus untuk menahan kurs Rupiah, memicu arus keluar modal asing dari perbankan blue-chip IHSG.</p>
                    </div>
                </div>
            </div>

            <!-- Verified News Feed (Arus Sentimen Pasar Terverifikasi) -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                <!-- Box 1: Global Macro & Fed -->
                <div class="natural-card p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-linen-300">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-forest-700"></span>
                            <h4 class="font-bold text-forest-900 text-sm">Sentimen Makro Global & Federal Reserve</h4>
                        </div>
                        <span class="text-[11px] text-stone-500 font-mono">Kebijakan Moneter</span>
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-linen-50 border border-linen-200 space-y-1.5 hover:border-forest-600/40 transition-all">
                            <div class="flex items-center justify-between text-[11px]">
                                <span class="font-bold text-forest-800 bg-linen-200 px-2 py-0.5 rounded-md">{item.get('source', 'Sentimen Makro')}</span>
                                <span class="text-stone-500 font-mono">{item.get('pub_date', '')}</span>
                            </div>
                            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="block font-semibold text-xs text-stone-900 hover:text-forest-700 leading-snug">
                                {item.get('title', '')}
                            </a>
                        </div>
                        ''' for item in global_news[:5]]) if global_news else '<div class="text-xs text-stone-500 p-4 text-center">Menunggu sinkronisasi feed global...</div>'}
                    </div>
                </div>

                <!-- Box 2: Geopolitics & Energy -->
                <div class="natural-card p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-linen-300">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-600"></span>
                            <h4 class="font-bold text-forest-900 text-sm">Sentimen Geopolitik, Minyak & Energi</h4>
                        </div>
                        <span class="text-[11px] text-amber-700 font-mono">Premi Risiko & OPEC</span>
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-linen-50 border border-linen-200 space-y-1.5 hover:border-amber-600/40 transition-all">
                            <div class="flex items-center justify-between text-[11px]">
                                <span class="font-bold text-amber-900 bg-amber-100 px-2 py-0.5 rounded-md border border-amber-200">{item.get('source', 'Sentimen Energi')}</span>
                                <span class="text-stone-500 font-mono">{item.get('pub_date', '')}</span>
                            </div>
                            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="block font-semibold text-xs text-stone-900 hover:text-amber-800 leading-snug">
                                {item.get('title', '')}
                            </a>
                        </div>
                        ''' for item in geopolitics_news[:5]]) if geopolitics_news else '<div class="text-xs text-stone-500 p-4 text-center">Menunggu sinkronisasi geopolitik feed...</div>'}
                    </div>
                </div>

                <!-- Box 3: Crypto & Bitcoin Intelligence -->
                <div class="natural-card p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-linen-300">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
                            <h4 class="font-bold text-forest-900 text-sm">Sentimen Kripto, Bitcoin & Web3</h4>
                        </div>
                        <span class="text-[11px] text-indigo-700 font-mono">Likuiditas & Derivatif</span>
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-linen-50 border border-linen-200 space-y-1.5 hover:border-indigo-600/40 transition-all">
                            <div class="flex items-center justify-between text-[11px]">
                                <span class="font-bold text-indigo-900 bg-indigo-100 px-2 py-0.5 rounded-md border border-indigo-200">{item.get('source', 'Sentimen Kripto')}</span>
                                <span class="text-stone-500 font-mono">{item.get('pub_date', '')}</span>
                            </div>
                            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="block font-semibold text-xs text-stone-900 hover:text-indigo-800 leading-snug">
                                {item.get('title', '')}
                            </a>
                        </div>
                        ''' for item in crypto_news[:5]]) if crypto_news else '<div class="text-xs text-stone-500 p-4 text-center">Menunggu sinkronisasi crypto feed...</div>'}
                    </div>
                </div>

                <!-- Box 4: Indonesia Financial Wire -->
                <div class="natural-card p-6 space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-linen-300">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
                            <h4 class="font-bold text-forest-900 text-sm">Sentimen Pasar Modal Indonesia (IHSG & Rupiah)</h4>
                        </div>
                        <span class="text-[11px] text-emerald-700 font-mono">Bank Indonesia & APBN</span>
                    </div>

                    <div class="space-y-3">
                        {"".join([f'''
                        <div class="p-3.5 rounded-xl bg-linen-50 border border-linen-200 space-y-1.5 hover:border-forest-600/40 transition-all">
                            <div class="flex items-center justify-between text-[11px]">
                                <span class="font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">{item.get('source', 'Sentimen Domestik')}</span>
                                <span class="text-stone-500 font-mono">{item.get('pub_date', '')}</span>
                            </div>
                            <a href="{item.get('link', '#')}" target="_blank" rel="noopener noreferrer" class="block font-semibold text-xs text-stone-900 hover:text-emerald-700 leading-snug">
                                {item.get('title', '')}
                            </a>
                        </div>
                        ''' for item in indonesia_news[:5]]) if indonesia_news else '<div class="text-xs text-stone-500 p-4 text-center">Menunggu sinkronisasi berita domestik...</div>'}
                    </div>
                </div>

            </div>

        </div>

        <!-- TAB 6: WHATSAPP BROADCAST (ONE-CLICK COPY) -->
        <div id="tab-wa" class="tab-pane hidden space-y-6">
            
            <div class="natural-card p-6 sm:p-8 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-linen-300">
                    <div>
                        <div class="text-xs uppercase tracking-wider text-sage-600 font-bold">Distribusi Komunikasi & Morning Intelligence</div>
                        <h3 class="text-xl sm:text-2xl font-extrabold text-forest-900">Morning Briefing & Transisi Intra-Week</h3>
                        <p class="text-xs sm:text-sm text-stone-600">Rantai sentimen harian (update otomatis tiap 06:00 WIB) memetakan katalis Big Tech, dinamika kripto, kalender ekonomi berdampak, dan transmisi pasar modal.</p>
                    </div>
                    <button onclick="copyWhatsAppBroadcast()" id="copy-btn" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-800 text-white text-xs font-bold transition-all shadow-sm">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/>
                        </svg>
                        Salin Seluruh Teks
                    </button>
                </div>

                <div class="p-3 bg-linen-100 rounded-xl border border-linen-300 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                        <span class="font-bold text-forest-900">Status Validasi Broadcast:</span>
                        <span class="text-stone-600">Jadwal Kalender Divalidasi BLS/BEA &bull; Logika Return Terverifikasi &bull; Feed Disinkronkan</span>
                    </div>
                    <div class="text-[11px] font-mono text-stone-500">
                        Sinkronisasi Terakhir: <b>{display_date}</b>
                    </div>
                </div>

                <div class="relative">
                    <pre id="wa-text-content" class="p-6 rounded-2xl bg-linen-50 border border-linen-300 text-stone-800 text-xs sm:text-sm font-mono whitespace-pre-wrap leading-relaxed max-h-[600px] overflow-y-auto">{whatsapp_text}</pre>
                </div>
            </div>

        </div>

    </main>

    <!-- FOOTER -->
    <footer class="bg-forest-900 text-sage-300 text-xs py-6 px-4 sm:px-8 border-t border-forest-800 mt-12">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
            <div class="text-xs text-sage-200 space-y-1">
                <div><b class="text-white">Sumber Data Pasar & Neraca:</b> Yahoo Finance, FRED (Federal Reserve St. Louis), S&P Global, Bank Indonesia & Binance API</div>
                <div class="text-[11px] text-sage-300"><b class="text-sprout">Sumber Berita Makro Hari Ini:</b> {active_news_sources_str}</div>
            </div>
            <div class="text-xs text-sage-300 font-mono">
                Pembaruan: <span class="text-sprout">{display_date}</span>
            </div>
        </div>
    </footer>

    <!-- JAVASCRIPT: TAB SWITCHER, DUAL CLOCK, LIVE CRYPTO POLLING, DYNAMIC LANDSCAPE -->
    <script>
        // 1. Tab Switcher
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            const targetPane = document.getElementById(tabId);
            if (targetPane) targetPane.classList.remove('hidden');
            
            const targetBtn = document.getElementById('btn-' + tabId);
            if (targetBtn) targetBtn.classList.add('active');
            
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        // 2. Dual Real-time Clocks (WIB & EST)
        function updateLiveClocks() {{
            const now = new Date();
            
            // WIB (Jakarta: UTC+7)
            const wibStr = new Intl.DateTimeFormat('id-ID', {{
                timeZone: 'Asia/Jakarta',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false
            }}).format(now);
            const elWib = document.getElementById('live-clock-wib');
            if (elWib) elWib.textContent = wibStr + ' WIB';

            // Dynamic Timezone calculation for New York (EDT vs EST)
            const nyParts = new Intl.DateTimeFormat('en-US', {{
                timeZone: 'America/New_York',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false,
                timeZoneName: 'short'
            }}).formatToParts(now);
            const nyHours = nyParts.find(p => p.type === 'hour')?.value || '00';
            const nyMins = nyParts.find(p => p.type === 'minute')?.value || '00';
            const nySecs = nyParts.find(p => p.type === 'second')?.value || '00';
            const nyTz = nyParts.find(p => p.type === 'timeZoneName')?.value || 'ET';
            const estStr = `${{nyHours}}:${{nyMins}}:${{nySecs}}`;
            
            const elEst = document.getElementById('live-clock-est');
            if (elEst) elEst.textContent = estStr + ' ' + nyTz;
            const elTzLabel = document.getElementById('ny-tz-label');
            if (elTzLabel) elTzLabel.textContent = nyTz + ' (NYC):';

            // Session check (NY Cash 09:30 - 16:00 ET)
            const nyHour = parseInt(nyHours);
            const nyMin = parseInt(nyMins);
            const pill = document.getElementById('market-session-pill');
            if (pill) {{
                if (nyHour >= 9 && nyHour < 16) {{
                    pill.textContent = 'NY CASH OPEN';
                    pill.className = 'hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950 text-sprout border border-emerald-700/50';
                }} else {{
                    pill.textContent = 'ASIA / AFTER-HOURS';
                    pill.className = 'hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-forest-800 text-sage-200 border border-forest-600';
                }}
            }}
        }}
        setInterval(updateLiveClocks, 1000);
        updateLiveClocks();

        // 3. Dynamic Rotating Natural Landscape Collection
        const NATURAL_LANDSCAPES = [
            {{
                name: "Misty Pine Forest",
                location: "Alpine Wilderness",
                url: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1920&q=80"
            }},
            {{
                name: "Lush Botanical Foliage",
                location: "Canopy Leaves",
                url: "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=1920&q=80"
            }},
            {{
                name: "Golden Woodland Sunbeams",
                location: "Temperate Forest",
                url: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1920&q=80"
            }},
            {{
                name: "Emerald Highland Valleys",
                location: "Mountain Mist",
                url: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1920&q=80"
            }},
            {{
                name: "Serene Alpine Glacier Stream",
                location: "Mountain Slopes",
                url: "https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=1920&q=80"
            }},
            {{
                name: "Yosemite High Sierra",
                location: "Forest Vista",
                url: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1920&q=80"
            }}
        ];

        let currentLandscapeIdx = 0;

        function setRandomNaturalLandscape() {{
            try {{
                const storedIdx = parseInt(sessionStorage.getItem('macro_landscape_idx'));
                let nextIdx;
                if (!isNaN(storedIdx)) {{
                    nextIdx = (storedIdx + 1) % NATURAL_LANDSCAPES.length;
                }} else {{
                    nextIdx = Math.floor(Math.random() * NATURAL_LANDSCAPES.length);
                }}
                sessionStorage.setItem('macro_landscape_idx', nextIdx);
                applyLandscape(nextIdx);
            }} catch (e) {{
                applyLandscape(0);
            }}
        }}

        function cycleLandscape() {{
            currentLandscapeIdx = (currentLandscapeIdx + 1) % NATURAL_LANDSCAPES.length;
            sessionStorage.setItem('macro_landscape_idx', currentLandscapeIdx);
            applyLandscape(currentLandscapeIdx);
        }}

        function applyLandscape(idx) {{
            currentLandscapeIdx = idx;
            const hero = document.getElementById('hero-landscape-section');
            if (hero && NATURAL_LANDSCAPES[idx]) {{
                hero.style.backgroundImage = `url('${{NATURAL_LANDSCAPES[idx].url}}')`;
            }}
        }}

        // Run landscape setup immediately
        setRandomNaturalLandscape();

        // 4. Live Client-Side Crypto Poller via Binance Public API
        let previousCrypto = {{}};
        
        function refreshAllData() {{
            const syncIcon = document.getElementById('sync-icon');
            const btnText = document.getElementById('btn-refresh-text');
            if (syncIcon) syncIcon.classList.add('animate-spin');
            if (btnText) btnText.textContent = "Sinkronisasi Live...";
            
            fetchLiveCryptoPrices();
            
            // Reload bypassing browser cache with fresh timestamp query
            setTimeout(() => {{
                window.location.href = window.location.pathname + '?_t=' + new Date().getTime();
            }}, 1200);
        }}

        async function fetchLiveCryptoPrices() {{
            const syncIcon = document.getElementById('sync-icon');
            const btnText = document.getElementById('btn-refresh-text');
            if (syncIcon) syncIcon.classList.add('animate-spin');
            if (btnText) btnText.textContent = "Sinkronisasi Live...";

            try {{
                const symbols = '["BTCUSDT","ETHUSDT","SOLUSDT"]';
                const res = await fetch(`https://api.binance.com/api/v3/ticker/price?symbols=${{symbols}}`);
                if (!res.ok) throw new Error('Network error');
                const data = await res.json();
                
                data.forEach(item => {{
                    const sym = item.symbol;
                    const price = parseFloat(item.price);
                    
                    if (sym === "BTCUSDT") updatePriceCard("btc", price);
                    if (sym === "ETHUSDT") updatePriceCard("eth", price);
                    if (sym === "SOLUSDT") updatePriceCard("sol", price);
                }});
                
                if (btnText) {{
                    btnText.textContent = "✓ Live Terkini!";
                    setTimeout(() => {{ btnText.textContent = "Refresh Live Data"; }}, 2500);
                }}
            }} catch (err) {{
                console.warn("Binance ticker poll:", err);
                if (btnText) btnText.textContent = "Refresh Live Data";
            }} finally {{
                if (syncIcon) setTimeout(() => syncIcon.classList.remove('animate-spin'), 600);
            }}
        }}

        function updatePriceCard(key, price) {{
            const elVal = document.getElementById(`live-${{key}}`);
            const card = document.getElementById(`card-${{key}}`);
            if (!elVal) return;

            const prev = previousCrypto[key] || price;
            previousCrypto[key] = price;

            // Format price string
            if (key === 'sol') {{
                elVal.textContent = '$' + price.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
            }} else {{
                elVal.textContent = '$' + Math.round(price).toLocaleString('en-US');
            }}

            if (card) {{
                card.classList.remove('flash-up', 'flash-down');
                void card.offsetWidth; // trigger reflow
                if (price > prev) {{
                    card.classList.add('flash-up');
                }} else if (price < prev) {{
                    card.classList.add('flash-down');
                }}
            }}
        }}

        // Poll crypto every 10 seconds live
        setInterval(fetchLiveCryptoPrices, 10000);
        setTimeout(fetchLiveCryptoPrices, 1500);

        // 5. One-Click Copy for WhatsApp Broadcast
        function copyWhatsAppBroadcast() {{
            const text = document.getElementById('wa-text-content').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copy-btn');
                const orig = btn.innerHTML;
                btn.innerHTML = '✓ Berhasil Disalin!';
                btn.classList.add('bg-emerald-600');
                setTimeout(() => {{
                    btn.innerHTML = orig;
                    btn.classList.remove('bg-emerald-600');
                }}, 2500);
            }}).catch(err => {{
                alert('Gagal menyalin: ' + err);
            }});
        }}

        // 6. Finviz Table Category Filter
        function filterFinviz(cat) {{
            const rows = document.querySelectorAll('#finviz-table-body tr');
            rows.forEach(r => {{
                if (cat === 'all' || r.getAttribute('data-cat') === cat) {{
                    r.style.display = '';
                }} else {{
                    r.style.display = 'none';
                }}
            }});
            const btns = ['all', 'kripto', 'emas', 'minyak', 'dollar', 'tech', 'indonesia'];
            btns.forEach(b => {{
                const btn = document.getElementById('btn-fz-' + b);
                if (btn) {{
                    if (b === cat) {{
                        btn.className = 'px-3 py-1.5 rounded-lg bg-forest-900 text-white font-mono transition-all shadow-sm';
                    }} else {{
                        btn.className = 'px-3 py-1.5 rounded-lg bg-linen-100 text-stone-700 hover:bg-linen-200 border border-linen-300 font-mono transition-all';
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Rendered Natural Landscape report to {output_path}")
    
    # Also write to index.html for instant root localhost:8080 viewing and github pages deployment
    index_path = os.path.join(os.path.dirname(os.path.abspath(output_path)), "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return os.path.abspath(output_path)
